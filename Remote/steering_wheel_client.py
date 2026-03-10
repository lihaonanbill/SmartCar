#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pygame
from socket import *
import threading

flag = True


def out():
    global flag
    data = input("input 'e' whenever you want to quit\n")
    if data == "e":
        flag = False


th = threading.Thread(target=out)

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

pygame.init()
done = False
info = {}  # 方向盘数据
firstFlag = True
brakeFlag = True
# -------- Main Program Loop -----------
# steering_gear_local_control.setup()
# steering_gear_local_control.init_car()
th.start()
while ~done:
    if not flag:
        break
    # EVENT PROCESSING STEP
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            print('Joystick button pressed.')
        if event.type == pygame.JOYBUTTONUP:
            print('Joystick button released.')

    # 获取joysticks数目
    joystick_count = pygame.joystick.get_count()
    info['NumberOfsticks'] = joystick_count  # NumberOfJoysticks 加入字典
    joystick = pygame.joystick.Joystick(0)  # 实例化Joystick类,传入id为0
    joystick.init()  # 对象初始化

    # 从操作系统中获取控制器/操纵杆的名称
    name = joystick.get_name()
    info['Joystick name'] = name

    # -------------------------------------------------------------------------------
    # Usually axis run in pairs, up/down for one, and left/right for one
    axes = joystick.get_numaxes()  # 获取axis的数目 并加入字典
    info['NumberOfAxes'] = axes
    for j in range(2):
        value_axis = joystick.get_axis(j)  # 获取当前第j个axis的值
        # # if abs(value_axis) and abs(value_axis-info['Value_Axis'+str(j)]) > 0.001:
        # if abs(value_axis) > 0.01:
        #     # 上一时刻的值大于0.001，且变化量大于0.001
        #     if j == 0:      # 舵机
        #         print('舵机转向')
        #     elif j == 1:
        #         print('电机赋值')
        # print('Value_Axis {} value: {:>6.3f}'.format(j, value_axis))  # 格式输出
        info['Value_Axis' + str(j)] = value_axis  # 将第i个axis的当前值加入字典

    # -------------------------------------------------------------------------------
    # get the the value of buttons
    buttons = joystick.get_numbuttons()  # 获取button的数目 并加入字典
    info['NumberOfButtons'] = buttons
    for j in range(buttons):
        value_button = joystick.get_button(j)  # 获取第i个button的值
        # if info.get('Value_Button'+str(j)) and abs(value_button-info['Value_Button'+str(j)]) > 0.001:
        #     # 上一时刻的值大于0.001，且变化量大于0.001
        #     if j == 5:
        #         # 摇杆前
        #         print('摇杆向前')
        #     if j == 4:
        #         # 摇杆后
        #         print('摇杆向后')
        #     if j == 13:
        #         # 手刹
        #         if brakeFlag:
        #             brakeFlag = not brakeFlag
        #             print(brakeFlag)
        #         else:
        #             brakeFlag = not brakeFlag
        #             print(brakeFlag)
        #
        # # print('Button {:>2} value: {}'.format(j, value_button))   # 格式输出当前button值
        info['Value_Button' + str(j)] = value_button
    tosend = str(info)
    dataSocket.send(tosend.encode())
    reced = dataSocket.recv(BUFLEN)
    print('舵机 Value_Axis0', info['Value_Axis0'])
    print('电机 Value_Axis1', info['Value_Axis1'])
    print('开关 Value_Button', info['Value_Button7'])
dataSocket.close()
pygame.quit()
