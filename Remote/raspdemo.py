# writer: lihaonan_Bill
# date:  2022/1/18 22:23
from socket import *
import ast

# 主机地址为空字符串，表示绑定本机所有网络接口ip地址
IP = '120.25.163.59'
# 绑定端口号
PORT = 7000
# 定义一次从socket缓冲区最多读入512个字节数据
BUFLEN = 512 * 2

# 实例化一个socket对象
# 参数 AF_INET 表示该socket网络层使用IP协议
# 参数 SOCK_STREAM 表示该socket传输层使用tcp协议
dataSocket = socket(AF_INET, SOCK_STREAM)

# socket绑定地址和端口
dataSocket.connect((IP, PORT))
print('成功连接服务器')
# -------- Main Program Loop -----------
# steering_gear_local_control.setup()
# steering_gear_local_control.init_car()
while True:

    recved = dataSocket.recv(BUFLEN)
    # 读取的字节数据是bytes类型，需要解码为字符串
    Info = recved.decode()  # 字符串类型
    if Info == "e":
        break
    print(Info)
    dataSocket.send(f'服务端接收到了信'.encode())
dataSocket.close()