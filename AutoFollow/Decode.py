# writer: lihaonan_Bill
# date:  2022/3/11 20:42
"""
               front car
node0  -------------------------node1
-                                   -
-                                   -
-                                   -
-                                   -
-                                   -
-                                   -
-                                   -
node2  --------------------------node3
              rear car
e.g. L01,L13分别表示node0到node1的距离，node1到node3的距离，其他的距离表示类似
----------------------*
函数功能：在318长度的字符串中解析出我们需要的距离数据
数据单位：cm
"""

import threading


class Decode:
    lock = threading.Lock()
    """
    原始数据区：
    每个列表存放两个数据，一个是长度的累加和sum(cm), 另一个是累加次数，
    当累加次数到达5-10时，取平均值，数据取出并清零
    """
    L02_Origin = [0, 0]
    L12_Origin = [0, 0]
    L03_Origin = [0, 0]
    L13_Origin = [0, 0]

    """
    有效数据区：
    存放取均值过滤后的数据
    注意：该数据需要加线程所，因为除了本类相关线程在存放数据，还有Analyse类来访问数据
    """
    L02 = []
    L12 = []
    L03 = []
    L13 = []

    """
    函数功能：在318长度的字符串中解析出我们需要的距离数据
    """

    @classmethod
    def getData(cls):
        """
        若存在数据，则返回数据，然后清除
        :return: 返回由三个长度组成的列表
        """
        if len(cls.L02) > 1 and len(cls.L12) > 1 and len(cls.L03) > 1 and len(cls.L13) > 1:
            temp = [cls.L02[0], cls.L12[0], cls.L03[0], cls.L13[0]]
            cls.L02.remove(cls.L02[0])
            cls.L12.remove(cls.L12[0])
            cls.L03.remove(cls.L03[0])
            cls.L13.remove(cls.L13[0])
            return temp
        else:
            return []

    @classmethod
    def decode(cls, data_str: str):
        frequency = 1  # 设置均值过滤频率
        if data_str[11] == "3":
            """这里因为是同步的，所以判断其中一条边长的累加值即可"""
            if cls.L03_Origin[1] == frequency:
                """
                算出平均值后L03和L13的累加值的平均值
                移交给有效数据区
                然后清零
                """

                cls.L03.append(cls.L03_Origin[0] / frequency)
                cls.L13.append(cls.L13_Origin[0] / frequency)
                cls.L03_Origin[0] = 0
                cls.L03_Origin[1] = 0
                cls.L13_Origin[0] = 0
                cls.L13_Origin[1] = 0

            else:
                """
                将16进制数转为十进制后存入相原始区
                """
                temp03: str = data_str[246:248] + data_str[244:246] + data_str[242:244]
                cls.L03_Origin[0] += int(temp03, 16) / 10
                cls.L03_Origin[1] += 1
                temp13: str = data_str[272:274] + data_str[270:272] + data_str[268:270]
                cls.L13_Origin[0] += int(temp13, 16) / 10
                cls.L13_Origin[1] += 1
        elif data_str[11] == "2":
            """这里因为是同步的，所以判断其中一条边长的累加值即可"""
            if cls.L02_Origin[1] == frequency:
                """
                算出平均值后L02和L12的累加值的平均值
                移交给有效数据区
                然后清零
                """

                cls.L02.append(cls.L02_Origin[0] / frequency)
                cls.L12.append(cls.L12_Origin[0] / frequency)
                cls.L02_Origin[0] = 0
                cls.L02_Origin[1] = 0
                cls.L12_Origin[0] = 0
                cls.L12_Origin[1] = 0

            else:
                """
                将16进制数转为十进制后存入相原始区
                """
                temp02: str = data_str[272:274] + data_str[270:272] + data_str[268:270]
                cls.L02_Origin[0] += int(temp02, 16) / 10
                cls.L02_Origin[1] += 1
                temp12: str = data_str[298:300] + data_str[296:298] + data_str[294:296]
                cls.L12_Origin[0] += int(temp12, 16) / 10
                cls.L12_Origin[1] += 1
