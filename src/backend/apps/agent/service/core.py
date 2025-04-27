from django.conf import settings
import os
import json

from ..deepseek import Agent

from .clients import deepseek_client, zhipu_client, redis_client

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
        self.media_text = '''你是一个专业的影视查询助手。根据用户输入，返回匹配的影视结果：
            
            **规则：**
            1. 如果用户查询的是模糊需求（如类型、推荐、多个选项）：
            - 返回50个以内影视作品的字符串列表，格式如：["影片1", "影片2", "影片3"]
            2. 如果用户提供了明确特征（如片名、导演、主演、年份等）使其能确定是某部影片而无其他结果：
            - 返回唯一最匹配的影片也为数组，数组有唯一元素，格式如：["影片名"]
            3. 无结果时返回空列表：[]

            **示例：**
            用户输入："科幻电影推荐" → ["星际穿越", "盗梦空间", "银翼杀手2049"]
            用户输入："诺兰导演的电影" → ["盗梦空间", "星际穿越", "信条"]
            用户输入："汤姆·汉克斯主演的太空电影" → ["阿波罗13号"]
            用户输入："2023年王家卫的电视剧" → ["繁花"]
            用户输入："不存在的电影" → []

            **注意：**
            - 不要额外解释，直接返回结果
            - 优先匹配用户明确指定的特征（如片名、人名、年份）
            '''
        self.agent_media = Agent(
            name='Movie Search Agent',
            instructions=self.media_text,
            functions=[]
        )
        
        with open('./apps/agent/config/media_library.json', 'r', encoding='utf-8') as f:
            self.medias = json.load(f)

    def _chat(self, message:str):
        response = deepseek_client.run(agent=self.agent_talk, messages=[{"role": "user", "content": message}], context_variables={})
        return response.messages[0]['content']

    def _media(self, message:str):
        response = deepseek_client.run(agent=self.agent_media, messages=[{"role": "user", "content": message}], context_variables={})
        return response.messages[0]['content']

    def _image(self, img_path, text):
        response = zhipu_client.chat(img_path=img_path,text=self.media_text+'\n用户输入：'+text)
        return response

    def _load_medias_info(self, medias):
        medias_info = [
            media for media in self.medias
            if media["name"] in medias
        ]
        return medias_info
    
    def media_search(self, message:str):
        medias = self._media(message=message)
        medias_info = self._load_medias_info(medias)
        redis_client.publish(medias_info)
        return medias, medias_info

    def voice_media_search(self, message:str, steps:list[str]):
        chat_info = ''
        medias = []
        medias_info = []
        for step in steps:
            print(step)
            if step == 'media':
                medias, medias_info = self.media_search(message=message)
            elif step == 'talk':
                chat_info = self._chat(message=message + str(medias))
        return chat_info, medias, medias_info

    def image_analyze(self, img_path, text):
        medias = self._image(img_path=img_path, text=text)
        medias_info = self._load_medias_info(medias)
        redis_client.publish(medias_info)
        return medias, medias_info

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