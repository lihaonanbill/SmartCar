# writer: lihaonan_Bill
# date:  2022/3/14 19:03
"""
通过给定的数据利用几何关系计算出偏移角和偏移距离
               front car
node0  ------------m4------------node1
-                  m6                 -
-                  -                 -
-                  -                 -
-                  -                 -
-                  -                 -
-                  -                 -
-                  -                 -
node2  -------------m5-------------node3
              rear car
e.g. L01,L13分别表示node0到node1的距离，node1到node3的距离，其他的距离表示类似
角度表示形如Angle_204, Angle_205
计算姿态角和偏移距离和引导方向的详细算法见UWB编队解决方案
"""
import math


class Analyse:
    L01 = 95
    L23 = 95
    L46 = 95
    data = []

    @classmethod
    def cal(cls, L02, L12, L03, L13):
        """L13留作备用"""
        if L13:
            pass
        """Attitude"""
        Angle_201 = math.acos((L02 ** 2 + cls.L01 ** 2 - L12 ** 2) / (2 * L02 * cls.L01))
        Angle_023 = math.acos((L02 ** 2 + cls.L23 ** 2 - L03 ** 2) / (2 * L02 * cls.L23))
        Attitude = math.pi - (2 * math.pi - Angle_023 - Angle_201)
        """Distance"""
        L05 = (L02 ** 2 + (cls.L23 / 2) ** 2 - 2 * L02 * (cls.L23 / 2) * math.cos(Angle_023)) ** 0.5
        Angle_205 = math.acos((L02 ** 2 + L05 ** 2 - (cls.L23 / 2) ** 2) / (2 * L02 * L05))
        Angle_504 = Angle_201 - Angle_205
        L45 = (L05 ** 2 + (cls.L01 / 2) ** 2 - 2 * L05 * (cls.L01 / 2) * math.cos(Angle_504)) ** 0.5
        """Orientation"""
        Angle_045 = math.acos(((0.5 * cls.L01) ** 2 + L45 ** 2 - L05 ** 2) / (2 * (0.5 * cls.L01) * L45))

        if abs(Angle_045 - math.pi / 2) < 0.01:  # 在正后方时三角形456不存在
            L56 = L45 - cls.L46
            DeltaAngle = Attitude
        else:
            """ChasingDis"""
            Angle_546 = abs(math.pi / 2 - Angle_045)
            L56 = (L45 ** 2 + cls.L46 ** 2 - 2 * L45 * cls.L46 * math.cos(Angle_546)) ** 0.5
            """ChasingAngle"""
            Angle_max = math.pi - math.acos((L56 ** 2 + cls.L46 ** 2 - L45 ** 2) / (2 * L56 * cls.L46))
            DeltaAngle = (Attitude - (abs(math.pi / 2 - Angle_045) / (math.pi / 2 - Angle_045)) * Angle_max)
        """把数据存入data"""
        cls.data.append(Attitude / math.pi * 180)  # 把角度从弧度制转为角度制
        cls.data.append(L45)
        cls.data.append(Angle_045 / math.pi * 180)  # 把角度从弧度制转为角度制
        cls.data.append(L56)
        cls.data.append(DeltaAngle / math.pi * 180)  # 把角度从弧度制转为角度制

    @classmethod
    def getData(cls):
        """
        拿出数据之后清除原来数据
        Attitude:[-180,180]
        当Attitude>0, L01和L23在左边相交
        当Attitude<0, L01和L23在右边相交
        Distance:[0,+Infinite]
        Orientation:[0,180]
        [0,90]:后车在前车左后方
        [90,180]:后车在前车右后方
        ChasingDis
        ChasingAngle:[-180,180]


        不需要担心原来不存在数据，因为执行完cal()之后一定有数据，也就是说不存在线程安全的问题
        """
        temp = cls.data[0:5]
        for i in range(len(temp)):
            cls.data.remove(cls.data[0])
        return temp


if __name__ == "__main__":
    Analyse.cal(167.2, 157.4, 230.9, 179.9)
    print(Analyse.getData())
