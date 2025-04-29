from queue import Queue
import threading
from .clients import redis_client

clients = set()

def background_listener():
    """独立线程运行的消息监听"""
    for message in redis_client.pubsub.listen():
        if message['type'] == 'message':
            data = message['data']
            for q in list(clients):  # 广播给所有活跃客户端
                q.put(data)

# 启动后台线程（Django启动时执行）
threading.Thread(target=background_listener, daemon=True).start()

class SseView:
    def event_stream(self):
        q = Queue()
        clients.add(q)
        print('👥 新客户端连接')
        try:
            while True:
                data = q.get()
                yield f"data: {data.decode('utf-8')}\n\n"
        except GeneratorExit:
            print('❌ 客户端断开')
        finally:
            clients.remove(q)