#!/usr/bin/python
# -*- coding: UTF-8 -*-
#  === TCP 服务端程序 server.py ===
import time
from smbus import SMBus
from PCA9685 import PWM
import ast
from socket import *


class Gear:
    # Gear(传动装置)类，包含转向函数和前进函数
    @staticmethod
    def setTurn(duty):
        """
        -------------------------------------
        函数名称：setTurn()
        函数功能：通过输入参数调用pca9685控制转向
        输入参数：duty，Initial_Value  输出参数:
        编制人：常江东      编写日期：2021.02.04
        ------------------------------------
        """
        pwm.setDuty(0, duty)

    @staticmethod
    def setForwad(duty):
        """
        -------------------------------------
        函数名称：setForwad()
        函数功能：通过输入参数调用pca9685控制前进
        输入参数：duty       输出参数:
        编制人：             改进日期：2021.02.04
        ------------------------------------
        """
        pwm.setDuty(4, duty)


def setup():
    # 初始化函数
    global pwm

    # 舵机电机初始化
    fPWM = 50
    i2c_address = 0x40
    bus = SMBus(1)  # Raspberry Pi revision 2
    pwm = PWM(bus, i2c_address)

    # 将频率转换为脉冲时间 20ms周期 = 频率为50Hz
    pwm.setFreq(fPWM)

    Gear.setTurn(7.5)  # 舵机初始化
    Gear.setForwad(8)  # 电机初始化
    print('当前电机值', pwm.readDuty(4))
    print('当前舵机值', pwm.readDuty(0))
    time.sleep(1)  # 延时1秒
    print('初始化完毕')


# --------------------------------------


setup()

info_new = {}
feedback = {}
firstFlag = True
brakeFlag = True
start = 0
# ------------- 连接客户端 ---------------
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
# 接受第一个数据
recved = dataSocket.recv(BUFLEN)
# 读取的字节数据是bytes类型，需要解码为字符串
Info = recved.decode()  # 字符串类型
print(Info)

info_old = ast.literal_eval(Info)
dataSocket.send(f'服务端接收到了信'.encode())
while True:
    # 尝试读取对方发送的消息
    # BUFLEN 指定从接收缓冲里最多读取多少字节
    recved = dataSocket.recv(BUFLEN)

    # 如果返回空'e'，表示对方关闭了连接
    # 退出循环，结束消息收发
    if recved.decode("utf-8") == "e":
        Gear.setTurn(7.5)
        Gear.setForwad(8)
        dataSocket.close()
        break

    # 读取的字节数据是bytes类型，需要解码为字符串
    Info = recved.decode()  # 字符串类型
    info_new = ast.literal_eval(Info)
    # print(f'收到对方信息： {Info}')

    # 发送的数据类型必须是bytes，所以要编码
    dataSocket.send(f'服务端接收到了信'.encode())

    # ----------------- 舵机 电机赋值 ----------------------
    # Usually axis run in pairs, up/down for one, and left/right for one
    axes = info_new.get('NumberOfAxes')
    for j in range(2):
        axis = info_new.get('Value_Axis' + str(j))  # 获取当前第i个axis的值
        # 上一时刻的值大于0.001，且变化量大于0.001
        if True:
            if j == 0:  # 舵机
                axis = int(100 * axis) / 100  # 减少有效位数
                if axis > 0:
                    print('右转', 7.5 + 2.4 * axis)
                    Gear.setTurn(7.5 + 2.4 * axis)  # 舵机赋值
                elif axis < 0:
                    print('左转', 7.5 + 2.4 * axis)
                    Gear.setTurn(7.5 + 2.4 * axis)
            elif j == 1:  # 电机
                if axis > 0:
                    temp = 8 - 2 * axis
                    print('前进', temp)
                    Gear.setForwad(temp)  # 电机赋值
                elif axis < 0:
                    temp = 8 - 1.5 * axis
                    print('后退', temp)
                    Gear.setForwad(temp)
                else:
                    print('停止', 0)
                    Gear.setForwad(8)

    # # -------------------------------------------------------------------
    # # get the the value of buttons
    # buttons = info_new.get('NumberOfButtons')
    # for j in range(buttons):
    #     button = info_new.get('Value_Button' + str(j))     # 获取第i个button的值
    #     # 上一时刻的值大于0.001，且变化量大于0.001
    #     if info_old.get('Value_Button'+str(j)) and abs(button-info_old['Value_Button'+str(j)]) > 0.001:
    #         if j == 5:
    #             # 摇杆前
    #             print('摇杆向前')
    #         if j == 4:
    #             # 摇杆后
    #             print('摇杆向后')
    #         if j == 13:
    #             # 手刹
    #             if brakeFlag:
    #                 brakeFlag = not brakeFlag
    #                 print(brakeFlag)
    #             else:
    #                 brakeFlag = not brakeFlag
    #                 print(brakeFlag)

    info_old.clear()
    info_old = info_new
