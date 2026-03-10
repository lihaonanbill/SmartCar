# writer: lihaonan_Bill
# date:  2022/3/5 20:09
"""
this code can realize the FOLLOWING MODEL 3,which is 2 in the front and 2 in the back


readUWB->decode->analyse->carControl
"""
from ReadUWB import ReadUWB
from Decode import Decode
from Analyse import Analyse
import time

from CarControl import CarControl

"""
ReadUWB
judge the node automatically according to the hex code
"""

"""
Decode
"""

"""
Analyse
to calculate :
1. Attitude
2. Distance
3. Orientation
"""

"""
CarControl
interface to CarControl
"""

"""使电调处于可接收状态"""
CarControl.setForward(8)
CarControl.setTurn(7.8)
time.sleep(1)  # 这个必须加，不然电机还没初始化，不知道为什么
"""UWB串口初始化"""
ReadUWB.setup()

"""UWB串口开始读取数据"""
ReadUWB.start()
temp = []
while True:
    """
    ReadUWB有可能返回空列表
    """
    while True:

        data_str = ReadUWB.getData()
        if len(data_str) == 2:
            break

    """
    因为decode要做均值过滤，每10次循环才能返回有效值，
    所以要对temp做判断
    """
    Decode.decode(data_str[0])
    Decode.decode(data_str[1])
    temp = Decode.getData()
    if temp:
        try:
            print(int(temp[0] * 100) / 100, int(temp[1] * 100) / 100, int(temp[2] * 100) / 100,
                  int(temp[3] * 100) / 100)
            Analyse.cal(temp[0], temp[1], temp[2], temp[3])
            Attitude, Distance, Orientation, ChasingDis, ChasingAngle = Analyse.getData()
            # 减少有效位数
            Attitude = int(Attitude * 100) / 100
            Distance = int(Distance * 100) / 100
            Orientation = int(Orientation * 100) / 100
            ChasingDis = int(ChasingDis * 100) / 100
            ChasingAngle = int(ChasingAngle * 100) / 100
            print("Attitude, Distance, Orientation, ChasingDis, ChasingAngle:", Attitude, Distance, Orientation,
                  ChasingDis, ChasingAngle)
            temp = []
            """车辆控制"""
            CarControl.carMove(Attitude, Distance, Orientation, ChasingDis, ChasingAngle)
        except Exception as e:
            CarControl.setForward(8)
            print(e)
        finally:
            print("---------")
