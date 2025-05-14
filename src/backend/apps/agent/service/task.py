import os
import ahocorasick
from pathlib import Path
from typing import List, Literal
import re
import json

from ..deepseek import Agent
from .clients import deepseek_client

class Task():
    def __init__(self) -> None:
        self.name = 'task'
        self.textSensitiveFilter = TextSensitiveFilter('./apps/agent/config/tencent-sensitive-words/sensitive_words_lines.txt')
        self.planner = TaskPlanner()

class TextSensitiveFilter:
    def __init__(self, word_file=None):
        """
        初始化敏感词过滤器
        :param word_file: 词库文件路径，默认使用同目录下的config/sensitive_words.json
        """
        self.automaton = ahocorasick.Automaton()
        self.word_file = word_file or Path(__file__).parent / 'config' / 'sensitive_words.json'
        self._load_words()

    def _load_words(self):
        """加载txt格式敏感词库（每行一个词）"""
        if not os.path.exists(self.word_file):
            raise FileNotFoundError(f"敏感词库文件不存在: {self.word_file}")

        with open(self.word_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()  # 去除首尾空白字符
                if word and not word.startswith('#'):  # 忽略空行和注释行
                    self.automaton.add_word(word, word)

        self.automaton.make_automaton()
        print(f"已加载敏感词数量: {len(self.automaton)}")

    def contains_sensitive(self, text: str) -> bool:
        """
        检查是否包含敏感词
        :param text: 待检测文本
        :return: True-包含敏感词, False-不包含
        """
        return any(True for _ in self.automaton.iter(text))

    def get_sensitive_words(self, text):
        """获取详细敏感词（当check返回False时可调用）"""
        return {word for _, (word, _) in self.automaton.iter(text)}

class TaskPlanner:
    def __init__(self):
        # 本地规则引擎
        self.local_keywords = re.compile(
            r'电影|电视剧|影视|推荐|看过|片荒|导演|演员|主演|^有什么好看的|^剧荒|的(电影|电视剧)',
            re.IGNORECASE
        )

        # 降级用Agent拆解器
        self.agent_task_planner = Agent(
            name="TaskPlanner",
            instructions="""根据用户输入决定执行步骤，严格按以下规则输出数组：
            
            **规则：**
            1. 当输入内容包含影视领域时：
               ["media", "talk"]
            2. 其他情况：
               ["talk"]

            **关键词示例：**
            - 电影/电视剧/动漫/剧集
            - 推荐/找/查/看过
            - 导演/演员/主演/片名
            
            **输出要求：**
            - 数组只能包含注册模块（talk/media）""",
            functions=[]
        )

    def plan(self, message: str) -> list[Literal["media", "talk"]]:
        """混合拆解流程"""
        # 第一步：本地快速判断
        local_decision = self._local_judge(message)

        if local_decision is not None:
            return local_decision  # 本地能确定结果

        # 第二步：降级到Agent拆解
        return self._agent_judge(message)

    def _local_judge(self, text: str) -> list[str] | None:
        """本地规则判断（返回None表示不确定）"""
        text_lower = text.lower()

        # 明确需要搜索的情况
        if any(kw in text_lower for kw in ["电影", "电视剧", "推荐", "导演", "演员"]):
            return ["talk", "media"]

        return None  # 本地无法确定

    def _agent_judge(self, message: str) -> list[str]:
        """Agent降级判断"""
        response = deepseek_client.run(agent=self.agent_task_planner, messages=[{"role": "user", "content": message}], context_variables={})
        print(response.messages[0]['content'], type(response.messages[0]['content']))
        steps = json.loads(response.messages[0]['content'])
        return steps