from ..deepseek import DeepSeekClient
from ..zhipu import ZhiPuClient
from ..database import RedisClient

deepseek_client = DeepSeekClient(key='sk-d53a6d90486e462aa755d198e940ea9d', url='https://api.deepseek.com')

zhipu_client = ZhiPuClient('f1677ec1cb784f3fbda4b8767bcc3c1e.PaYoK8zqumX6QFtT')

redis_client = RedisClient()
