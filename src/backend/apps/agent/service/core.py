from django.conf import settings
import os
import json
import ast
from ..deepseek import Agent

from .clients import deepseek_client, zhipu_client, get_redis_client

import requests
from typing import Dict, Any
from ..deepseek import Result



class Service():
    def __init__(self) -> None:
        self.name = 'service'
        self.chat_history = []
        self.agent_talk = Agent(
            name='Talk Agent',
            instructions='''你是一个功能强大的对话助手。
            
            你的回复内容将被直接语音播报，所以请回答纯文本内容，并且需要语言丰富流畅，不超过100个字
            
            **注意：**
            - 若用户输入最后跟了一个数组，那代表影视检索推荐agent工作并呈现结果。请结合用户前文输入和该结果进行回答
            ''', functions=[])
        self.media_prompt = '''你是一个专业的影视查询助手。根据用户输入，返回匹配的影视结果：
            
            **规则：**
            - 根据call_mcp函数返回结果，格式如：["影片1", "影片2", "影片3"]，返回全部影片不要漏掉


            **示例：**
            用户输入："科幻电影推荐" → ["星际穿越", "盗梦空间", "银翼杀手2049"]
            用户输入："诺兰导演的电影" → ["盗梦空间", "星际穿越", "信条"]
            用户输入："汤姆·汉克斯主演的太空电影" → ["阿波罗13号"]
            用户输入："2023年王家卫的电视剧" → ["繁花"]
            用户输入："不存在的电影" → []

            **注意：**
            - 不要额外解释，直接返回结果
            - 优先匹配用户明确指定的特征（如片名、人名、年份）

            当用户查询带有特定信息的影视资源时：
            1. 调用 call_mcp 工具
            2. 参数初始化设置为：
            {"tool_name": "search_medias", "parameters": {"query": {}}}}
            针对用户输入的信息，提取影片名称信息，类型信息，导演信息，演员信息，开始年份信息，结束年份信息，国家信息，更新参数信息填写到query中，信息不全时，不用填写query里所有字段
            例如：{"tool_name": "search_medias", "parameters": {"query": {"name": "赌圣", "genre": "喜剧", "director": "张艺谋", "actor": "陈道明", "min_year": "2020", "max_year": "2023", "region": "中国"}}}}
            - 信息不全时，不用填写query里所有字段，例如：{"tool_name": "search_medias", "parameters": {"query": {"director": "张艺谋", "actor": "陈道明"}}}}
            - 年份说明：min_year和max_year是开始年份和结束年份，开始年份一定小于结束年份，且2010年之前则只填写max_year，2010年之后则填写min_year
            - 此外注意，单独提到人名时，将该字段同时填入actor和director字段中
            3. 从工具返回的结果中提取信息回答用户

            当用户询问最新热门影视问题时：
            1. 调用 call_mcp 工具
            2. 参数必须设置为：
            {"tool_name": "hot_medias", "parameters": {"query": "hot"}}}
            3. 从工具返回的结果中提取信息回答用户
            
"""
            '''
        self.agent_media = Agent(
            name='Movie Search Agent',
            instructions=self.media_prompt,
            functions=[call_mcp]
        )

        self.figure_prompt = '''你是一个专业的可输入图片的多模态影视查询助手。根据用户输入，返回匹配的影视元素信息，包括片名，导演，演员：
            **规则：**
            1. 最高优先级：如果用户输入图片含有严重违规内容，如色情（裸露、性暗示）、暴力（血腥、武器）、其他违法内容（毒品、恐怖主义等）：
            - 必须返回{"safe": false, "response": {}}
            2. 输入不违规：针对用户输入的图片，提取影视名称信息，导演信息或演员信息（只有两种情况）
            - 优先提取影视名称信息：{"safe": true, "response": {"name": "赌圣"}}
            - 提取不到影视名称，则提取导演信息或演员信息（识别到人名时，将该字段同时填入actor和director字段中）：{"safe": true, "response": {"director": "陈道明", "actor": "陈道明"}}
            3. 输入不违规：针对用户输入的文字，补充，类型信息，开始年份信息，结束年份信息，地区信息到response字段里：
            - {"safe": true, "response": {"director": "陈道明", "actor": "陈道明", "genre": "喜剧", "min_year": "2020", "max_year": "2023", "region": "中国"}}
            - 不用填充所有字段，文字信息包含就填写，没有就不用填写，例如文字为空：{"safe": true, "response": {"director": "陈道明", "actor": "陈道明"}}
            - 年份说明：min_year和max_year是开始年份和结束年份，开始年份一定小于结束年份，且2010年之前则只填写max_year，2010年之后则填写min_year
            4. 无法识别有效信息，反馈空：{"safe": true, "response": {}}

            **注意：**
            - 图片含有严重违规内容，如色情（裸露、性暗示）、暴力（血腥、武器）、其他违法内容（毒品、恐怖主义等）必须返回{"safe": false, "response": {}}
            - 匹配用户明确指定的特征（如片名、人名、年份）
            - 不要返回重复片名！
            注意：必须返回合法dict，不要额外解释！
            '''

        with open('./apps/agent/config/media_library.json', 'r', encoding='utf-8') as f:
            self.medias = json.load(f)

    def _chat(self, message:str):
        self.chat_history.append({"role": "user", "content": message})
        response = deepseek_client.run(agent=self.agent_talk, messages=self.chat_history)
        self.chat_history.append(response.messages[0])
        return response.messages[0]['content']

    def _media(self, message:str):
        response = deepseek_client.run(agent=self.agent_media, messages=[{"role": "user", "content": message}], context_variables={})
        '''# 假设 response.messages 是可迭代的消息容器
        for message in response.messages:
            print(message)  # 直接打印消息内容'''
        return response.messages[-1]['content']

    def _image(self, img_path, text):
        safe, query = zhipu_client.chat(img_path=img_path,text=self.figure_prompt+'用户输入：'+text)
        if safe:
            result = call_mcp(tool_name='search_medias', parameters={"query": ast.literal_eval(query)}).value
            return safe, json.loads(result)['data']['result']
        return safe, {}

    def _load_medias_info(self, medias):
        medias_info = [
            media for media in self.medias
            if media["name"] in medias
        ]
        return medias_info

    def media_search(self, message:str):
        medias = self._media(message=message)
        medias_info = self._load_medias_info(medias)
        redis_client = get_redis_client()
        redis_client.publish(medias_info)
        return medias, medias_info

    def voice_media_search(self, message:str, steps:list[str]):
        chat_info = ''
        medias = []
        medias_info = []
        for step in steps:
            print(step)
            if step == 'query':
                medias, medias_info = self.media_search(message=message)
            elif step == 'talk':
                chat_info = self._chat(message=message + str(medias))
        return chat_info, medias, medias_info

    def image_analyze(self, img_path, text):
        safe, medias = self._image(img_path=img_path, text=text)
        if not safe :
            return safe, medias, []
        medias_info = self._load_medias_info(medias)
        redis_client = get_redis_client()
        redis_client.publish(medias_info)
        return safe, medias, medias_info

    def get_media_path(self, media_id):
        file_name = ''
        for media in self.medias:
            if media.get('id') == media_id:
                file_name = media['file_name']
        video_path = os.path.join(settings.MEDIA_ROOT, '', file_name)
        print(video_path)
        if not os.path.exists(video_path):
            return ''
        return video_path


def call_mcp(
    tool_name: str,
    parameters: Dict[str, Any],
    context_variables: Dict[str, Any] = {}
) -> Result:
    print('MCP-----', tool_name, parameters, context_variables)
    """
    调用MCP服务器并将结果存入上下文变量
    
    参数:
        tool_name: MCP服务器的工具名称（如"search_movies"）
        parameters: 传递给MCP工具的参数（如{"query": "动作电影"}）
        context_variables: Swarm上下文变量（用于存储结果）
    """
    try:
        # 从上下文获取MCP服务器地址（也可硬编码）
        mcp_url = "http://127.0.0.1:9000/execute"
        
        # 构造请求体
        payload = {
            "tool_name": tool_name,
            "parameters": parameters
        }
        
        # 发送请求（使用stream=True启用流式响应）
        with requests.post(mcp_url, json=payload, stream=True) as response:
            response.raise_for_status()
            
            # 检查Content-Type是否为SSE格式
            content_type = response.headers.get('Content-Type', '')
            if 'text/event-stream' in content_type:
                # 处理流式SSE响应
                result = parse_sse_response(response)
            else:
                # 处理普通JSON响应
                result = response.json()
        #print(result)
        
        # 将结果存入上下文变量（使用工具名称作为键前缀）
        context_key = f"mcp_result_{tool_name}"
        context_variables[context_key] = result
        
        # 封装结果为Result对象（value需为字符串，agent可为None）
        return Result(
            value=json.dumps(result),
            context_variables={context_key: result}
        )
        
    except Exception as e:
        # 错误处理：存入错误信息到上下文
        error_msg = f"MCP调用失败: {str(e)}"
        context_variables[f"mcp_error_{tool_name}"] = error_msg
        return Result(
            value=error_msg,
            context_variables={f"mcp_error_{tool_name}": error_msg}
        )
    
def parse_sse_response(response) -> Dict[str, Any]:
    """解析SSE格式的流式响应，合并所有data段"""
    full_result = {"data": []}
    current_line = ""
    
    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
        if not chunk:
            continue
            
        # 处理分块数据
        current_line += chunk
        
        # 按行分割（SSE使用\n\n分隔消息）
        lines = current_line.split('\n')
        current_line = lines.pop()  # 最后一行可能不完整，保留到下一次处理
        
        for line in lines:
            line = line.strip()
            if line.startswith('data:'):
                data_str = line[5:].strip()
                if data_str:
                    try:
                        data = json.loads(data_str)
                        full_result["data"].append(data)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON in SSE: {data_str}")
    
    # 提取最终结果（根据MCP实际返回结构调整）
    if full_result["data"] and isinstance(full_result["data"][0], dict):
        # 假设最后一条data包含完整结果
        return full_result["data"][-1]
    return full_result