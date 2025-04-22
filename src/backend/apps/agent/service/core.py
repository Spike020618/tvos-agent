import json

from ..client import Client, Agent, Response, Result

from .deepseek import deepseek_client

class Service():
    def __init__(self) -> None:
        self.name = 'service'
        self.agent_talk = Agent(
            name='Talk Agent',
            instructions='''你是一个功能强大的对话助手。
            
            你的回复内容将被直接语音播报，所以请回答纯文本内容，并且需要语言丰富流畅，不超过100个字
            
            **注意：**
            - 若用户输入最后跟了一个数组，那代表影视检索推荐agent工作并呈现结果。请结合用户前文输入和该结果进行回答
            ''', functions=[])
        self.agent_search = Agent(
            name='Movie Search Agent',
            instructions='''你是一个专业的影视查询助手。根据用户输入，返回最匹配的影视结果：
            
            **规则：**
            1. 如果用户查询的是模糊需求（如类型、推荐、多个选项）：
            - 返回3-5个影视作品的字符串列表，格式如：["影片1", "影片2", "影片3"]
            2. 如果用户提供了明确特征（如片名、导演、主演、年份等）使其能确定是某部影片而无其他结果：
            - 返回唯一最匹配的影片名称字符串，格式如："影片名"
            3. 无结果时返回空列表：[]

            **示例：**
            用户输入："科幻电影推荐" → ["星际穿越", "盗梦空间", "银翼杀手2049"]
            用户输入："诺兰导演的电影" → ["盗梦空间", "星际穿越", "信条"]
            用户输入："汤姆·汉克斯主演的太空电影" → ["阿波罗13号"]
            用户输入："2023年王家卫的电视剧" → []"繁花"]
            用户输入："不存在的电影" → []

            **注意：**
            - 不要额外解释，直接返回结果
            - 优先匹配用户明确指定的特征（如片名、人名、年份）
            ''',
            functions=[]
        )

        with open('./apps/agent/config/movie_library.json', 'r', encoding='utf-8') as f:
            self.movies = json.load(f)

    def chat(self, message:str):
        response = deepseek_client.run(agent=self.agent_talk, messages=[{"role": "user", "content": message}], context_variables={})
        return response.messages[0]['content']

    def search(self, message:str):
        response = deepseek_client.run(agent=self.agent_search, messages=[{"role": "user", "content": message}], context_variables={})
        return response.messages[0]['content']

    def run(self, message:str, steps:list[str]):
        user_platform = ['爱奇艺', 'B站']
        chat_info = ''
        movies = []
        for step in steps:
            print(step)
            if step == 'search':
                movies = self.search(message=message)
            elif step == 'talk':
                chat_info = self.chat(message=message + str(movies))
        movies_info = [
            movie for movie in self.movies
            if movie["title"] in movies
        ]
        return chat_info, movies, movies_info