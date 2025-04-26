import redis
import json

from django.conf import settings

class RedisClient:
    def __init__(self, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB):
        self.client = redis.StrictRedis(host=host,port=port,db=db)
        self.pubsub = self.client.pubsub()
        self.pubsub.subscribe('sse_channel')  # 订阅一个叫 'sse_channel' 的频道
        self.client.set('name', 'tvos')
    def publish(self, data):
        self.client.publish('sse_channel', json.dumps(data))