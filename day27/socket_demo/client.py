import socket

# 1. 创建 TCP Socket（AF_INET 表示 IPv4，SOCK_STREAM 表示 TCP）
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. 连接服务器
client_socket.connect(("127.0.0.1", 8888))
print("成功连接到服务器！")

try:
    while True:
        msg = input("请输入要发送的消息 (输入 q 退出): ")
        if msg.lower() == "q":
            break

        # 发送字节数据
        client_socket.send(msg.encode("utf-8"))

        # 读取服务端的回复
        response = client_socket.recv(1024)
        print(response.decode("utf-8"))
except ConnectionRefusedError as e:
    print(f"客户端连接失败：{e}")
finally:
    # 3. 关闭连接
    client_socket.close()
    print("已断开连接。")
