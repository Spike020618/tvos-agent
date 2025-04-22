import socket

def get_ip():
    local_ip = '127.0.0.1'  # 默认回环地址
    # 创建一个 UDP 套接字（不真正发送数据）
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # 连接 Google DNS
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip