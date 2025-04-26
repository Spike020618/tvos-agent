from queue import Queue
import threading
from .clients import redis_client

message_queue = Queue()

def background_listener():
    """独立线程运行的消息监听"""
    for message in redis_client.pubsub.listen():
        if message['type'] == 'message':
            message_queue.put(message['data'])

# 启动后台线程（Django启动时执行）
threading.Thread(target=background_listener, daemon=True).start()

class SseView:
    def event_stream(self):
        while True:
            data = message_queue.get()  # 阻塞直到新消息
            yield f"data: {data.decode('utf-8')}\n\n"