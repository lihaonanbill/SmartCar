# writer: lihaonan_Bill
# date:  2022/3/10 20:14

"""
同时从两个UWB读取数据
包含函数
setup():
read():在内部被装入线程池，不作为外部调用
start():
close():
getData():

缺点：没有进程结束机制，只能在命令行中敲入 ctrl C强行退出
"""

import threading

# import time
import serial
import PortSearch


class ReadUWB:
    """
    serial初始化设置
    """
    threads = []  # 线程池，用来同时从两个串口读取数据
    """此处需要加线程锁"""
    effectiveData0 = []  # 存储有效数据(str形式)
    effectiveData1 = []
    getDataNum = 0
    # lock = threading.Lock()
    """
    在Python基本数据类型中list、tuple、dict本身就是属于线程安全的，
    所以如果有多个线程对这3种容器做操作时，我们不必考虑线程安全问题。
    """
    bps = 921600
    port0, port1 = PortSearch.getPort()
    ser0 = serial.Serial(port0, bps, timeout=1, bytesize=8)  # 串口应该根据实际情况修改
    ser1 = serial.Serial(port1, bps, timeout=1, bytesize=8)
    flag0 = ser0.is_open
    flag1 = ser1.is_open

    @classmethod
    def setup(cls):
        if cls.flag0 and cls.flag1:
            print("port0 already open!")
            print("port1 already open!")
        else:
            cls.ser0.open()
            cls.ser1.open()

        """清除之前的数据，我们只需要当前的数据"""
        cls.ser0.flushInput()
        cls.ser1.flushInput()

    """
    UWB数据读取函数
    exception not written yet
    """

    @classmethod
    def read(cls, ser, effectiveData):
        # start = time.time()
        # count = 10000
        num = 0
        WrongNumber = 0
        print(ser.port, "starting...")
        while True:

            data_bytes = ser.read(159)
            data_str = data_bytes.hex()
            # print("get 159 bytes", count)
            # print(data_str, "\n")
            """
            采取偏移补救措施，最大化地利用数据
            """
            if data_str.startswith("5504"):

                effectiveData.append(data_str)
                num += 1
                # print(ser.port, "startswith\"5504\"", num)
            else:
                if data_str.count("5504") >= 1:
                    location = data_str.find("5504")
                    ser.read(location // 2)
                    # print("5504 exists at ", location, "\n")
                    WrongNumber += 1
            # count -= 1
        # finish = time.time()
        # print(ser.port, type(start - finish), finish - start, "\n", "有效数据:", num, "WrongNumber:", WrongNumber)

    """
    进行线程操作
    """

    @classmethod
    def start(cls):
        th0 = threading.Thread(target=cls.read, args=(cls.ser0, cls.effectiveData0,))
        th1 = threading.Thread(target=cls.read, args=(cls.ser1, cls.effectiveData1,))
        cls.threads.append(th0)
        cls.threads.append(th1)
        for tt in cls.threads:
            tt.start()

    """
    关闭串口
    """

    @classmethod
    def close(cls):
        for tt in cls.threads:
            tt.join()
        cls.ser0.close()
        cls.ser1.close()

    @classmethod
    def getData(cls):
        """
        先判断数据是否存在，因为UWB的数据读取不是可控的
        若存在：获取字符串并清除
        :return: 一个含有两个字符串的列表
        """
        if len(cls.effectiveData0) > 1 and len(cls.effectiveData1) > 1:
            temp = [cls.effectiveData0[cls.getDataNum], cls.effectiveData1[cls.getDataNum]]
            cls.effectiveData0.remove(cls.effectiveData0[0])
            cls.effectiveData1.remove(cls.effectiveData1[0])
            return temp
        else:
            return []
