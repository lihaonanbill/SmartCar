# writer: lihaonan_Bill
# date:  2022/1/18 22:23
from socket import *

#  === TCP 客户端程序 client.py ===
# IP = input("请输入服务端ip:")
IP = '120.25.163.59'  # 阿里云服务器的公网地址
print("正在连接", IP)
SERVER_PORT = 7000
BUFLEN = 512

# 实例化一个socket对象，指明协议
# 参数 AF_INET 表示该socket网络层使用IP协议
# 参数 SOCK_STREAM 表示该socket传输层使用tcp协议
dataSocket = socket(AF_INET, SOCK_STREAM)

# 连接服务端socket
dataSocket.connect((IP, SERVER_PORT))
print('连接成功')

while True:
    data = input("input e if you want to exit")
    if data == "e":
        break
    dataSocket.send(data.encode())
    reced = dataSocket.recv(BUFLEN)
dataSocket.close()