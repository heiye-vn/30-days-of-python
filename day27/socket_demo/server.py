import socket

# 1. 创建 TCP Socket（AF_INET 表示 IPv4，SOCK_STREAM 表示 TCP）
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. 绑定 IP 和端口
server_socket.bind(("127.0.0.1", 8888))

# 3. 开始监听，最大排队连接数为 5
server_socket.listen(5)
print("服务器已启动，正在等待客户端连接...")

# 4. 阻塞等待客户端连接
# client_socket 是专门用来和该客户端通信的套接字，addr 是客户端的 IP 和端口
client_socket, addr = server_socket.accept()
print(f"连接成功！客户端地址：{addr}")

try:
    while True:
        # 5. 接收客户端发来的数据（最大接收 1024 字节）
        data = client_socket.recv(1024)
        if not data:
            break  # 客户端关闭了连接

        # 收到的是字节（bytes），需要解码成字符串
        msg = data.decode("utf-8")
        print(f"收到客户端消息：{msg}")

        # 回送数据（必须先编码成字节）
        client_socket.send(f"服务器已收到：{msg}".encode("utf-8"))
finally:
    # 6. 关闭连接
    client_socket.close()
    server_socket.close()
    print("服务已关闭。")
