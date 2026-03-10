# writer: lihaonan_Bill
# date:  2022/1/18 20:42

# writer: lihaonan_Bill
# date:  2022/1/18 15:18

import socket
import threading


# ------------------------------------
def c2r(SOCKETS):
    while True:
        data = SOCKETS[0].recv(1024)
        if not data:
            print("disconnected from client!")
            SOCKETS[1].send("e".encode("utf-8"))
            break
        SOCKETS[1].send(data)  # 由于只是中继作用不需要解码，直接转发
    SOCKETS[0].close()


def r2c(SOCKETS):
    while True:
        data = SOCKETS[1].recv(1024)
        # 此时client端一定已经断开
        if not data:
            print("disconnected from rasp!")
            break
        SOCKETS[0].send(data)
    SOCKETS[1].close()


# ----------------------------------------
# 1.创建socket(套接字)
# AF_INET:表示使用IPv4
# SOCK_STREAM:表示TCP协议
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.绑定
# 参数为一个元组，元组第一个元素为本机ip，第二个元素为端口号，一般使用8000以上端口(因为8000以下已经使用)，最大使用到65535
server.bind(("172.26.33.67", 7000))

# 3.监听，设置最多连接数
server.listen(50)

# 4.等待客户端的连接
# 这里总共只需要连接2个客户端

threads = []  # 存放线程
sockets = []  # 存放套接字 0存放客户端 1存放树莓派

print("正在等待连接")
# 客户端连接成功返回客户端的套接字和客户端的IP地址,这里会阻塞

# -------------------------------------------------rasp和client分别与客户端连接，先连client后连rasp

clientSocket, clientAddr = server.accept()
sockets.append(clientSocket)
print("client已连接，address:%s" % str(clientAddr))
th1 = threading.Thread(target=c2r, args=(sockets,))

clientSocket, clientAddr = server.accept()
sockets.append(clientSocket)
print("rasp已连接，address:%s" % str(clientAddr))
th2 = threading.Thread(target=r2c, args=(sockets,))

threads.append(th1)
threads.append(th2)

for tt in threads:
    tt.start()

for tt in threads:
    tt.join()
# -------------------------------------------------------
server.close()
