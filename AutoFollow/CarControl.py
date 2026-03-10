# writer: lihaonan_Bill
# date:  2022/3/14 18:53
# -----------包的导入-----------------
from smbus import SMBus
from PCA9685 import PWM
import time
from Analyse import Analyse


class CarControl:
    # ---------相关参数设定及初始化---------
    fPWM = 50
    i2c_address = 0x40
    channel = 1
    bus = SMBus(1)  # Raspberry Pi revision 2
    pwm = PWM(bus, i2c_address)  # 将频率转换为脉冲时间 20ms周期 = 频率为50Hz
    pwm.setFreq(fPWM)
    Divide = []  # 用于微分控制算法,第一项是历史值，第二项是实时值
    Integration = []  # 用于积分控制算法，下标越小历史越久远，也就是说最后一项是最新的数据

    @classmethod
    def setTurn(cls, duty):
        """
        -------------------------------------
        函数名称：setTurn()
        函数功能：通过输入参数调用pca9685控制转向
        输入参数：duty，Initial_Value  输出参数:
        编制人：周峰立      编写日期：2021.02.04
        ------------------------------------
        """
        cls.pwm.setDuty(0, duty)

    @classmethod
    def setForward(cls, duty):
        """
        -------------------------------------
        函数名称：setForward()
        函数功能：通过输入参数调用pca9685控制前进
        输入参数：duty       输出参数:
        编制人：周峰立            改进日期：2021.02.04
        ------------------------------------
        """
        cls.pwm.setDuty(4, duty)  # 通过pwm脉冲来改变小车的状态

    @classmethod
    def AdaptiveShift(cls, Distance):  # 自适应变速(pid)
        """
        function:adjust the velocity according to the distance
        :param Distance:
        :return:
        """

        """判断微分和积分能不能用"""
        if len(cls.Divide) < 2 or len(cls.Divide) < 2:  # 必须有两个及以上的有效数据
            return
        AmplificationFactor = 350
        DeltaPWM = 0.8
        PausePWM = 8
        Kp = 1 / AmplificationFactor
        # Ki = 1 / 750
        Ki = 0
        Kd = 1 / 10
        Pid = Kp * Distance + Ki * sum(cls.Integration) + Kd * (cls.Divide[1] - cls.Divide[0])
        if Pid > 1:  # 距离太大，最大速度
            CarControl.setForward(PausePWM + DeltaPWM)
        elif Pid < 0:
            CarControl.setForward(PausePWM)
        else:  # 距离适宜，自适应变速
            CarControl.setForward(Pid * DeltaPWM + PausePWM)

    @classmethod
    def AdaptiveTurn(cls, Attitude, flag):  # 控制姿态，仅在后车中心处于前车中垂线附近时使用
        """

        :param Attitude:
        :param flag: 三种模式
        1.转向角度与Attitude成正比
        2.
        3.

        :return:
        """
        if flag == 1:  # 自适应转弯
            if abs((-1) * (Attitude / 180)) * 6 < 2.5:
                CarControl.setTurn((-1) * (Attitude / 180) * 6 + 7.8)
            else:
                CarControl.setTurn((-1) * (Attitude / 180) * 2.5 + 7.8)
        elif flag == 2:  # 大角度转弯
            CarControl.setTurn((-1) * (Attitude / abs(Attitude)) * 2.5 + 7.8)
        else:
            if abs((-1) * (Attitude / 90)) * 8 < 2.5:
                CarControl.setTurn((-1) * (Attitude / 90) * 8 + 7.8)
            else:
                CarControl.setTurn((-1) * (Attitude / 90) * 2.5 + 7.8)

    @classmethod
    def carMove(cls, Attitude, Distance, Orientation, ChasingDis, ChasingAngle):
        MinDis = Analyse.L46
        if Attitude:
            pass
        if Orientation:
            pass
        if Distance <= MinDis:  # 在这种情况下可以保证ChasingDis>MinDis
            cls.setForward(8)
            cls.Divide.clear()
            cls.Integration.clear()
        else:
            # 对历史数据的增和删
            if len(cls.Divide) > 2:
                cls.Divide.remove(cls.Divide[0])
            cls.Divide.append(ChasingDis)
            if len(cls.Integration) > 0:
                cls.Integration.append(ChasingDis)
            # 油门
            cls.AdaptiveShift(ChasingDis)
            # 方向
            cls.AdaptiveTurn(ChasingAngle, 1)


if __name__ == "__main__":
    while True:
        order = input("input,there must be a blank!!!")
        start = time.time()
        if order[0] == "0":
            CarControl.setTurn(int(order[2:]))
        elif order[0] == "4":
            CarControl.setForward(int(order[2:]))
        else:
            pass
        finish = time.time()
        print("time:", finish - start)
