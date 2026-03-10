# -*- coding:utf-8 -*-
# PCA9685.py
# ============================================================================
import time
import math


class PWM:
    # 保护成员，类对象和子类对象能够访问
    _mode_adr = 0x00
    _LED0_OFF_L = 0x08
    _LED0_OFF_H = 0x09
    _LED0_ON_L = 0x06
    _LED0_ON_H = 0x07
    _prescale_adr = 0xFE

    def __init__(self, bus, address=0x40):
        '''
        Creates an instance of the PWM chip at given i2c address.
        @param bus: the SMBus instance to access the i2c port (0 or 1).
        @param address: the address of the i2c chip (default: 0x40)
        '''
        self.bus = bus
        self.address = address
        self._writeByte(self._mode_adr, 0x00)

    def setFreq(self, freq):
        """
        设置PWM频率，将值存入设备。
        Sets the PWM frequency. The value is stored in the device.
        @param freq: the frequency in Hz (approx.)
        """
        # prescal寄存器设置周期
        # prescalValue = round(osc_clock/(4096*update_rate)-1)
        prescaleValue = 25000000.0  # 内部时钟25MHz
        prescaleValue /= 4096.0  # 12-bit
        prescaleValue /= float(freq)
        prescaleValue -= 1.0

        # math.floor向下取整
        prescale = math.floor(prescaleValue + 0.5)  # 四舍五入

        oldmode = self._readByte(self._mode_adr)
        if oldmode == None:
            return
        newmode = (oldmode & 0x7F) | 0x10  # 准备进入sleep，设置时钟前必须先进入sleep模式

        # 写1进入sleep模式后，时钟会关闭。此时可以修改时钟源寄存器EXTCLOCK和周期寄存器PRE_SCALE，修改这两个寄存器之前必须先进入sleep模式。
        self._writeByte(self._mode_adr, newmode)
        self._writeByte(self._prescale_adr, int(math.floor(prescale)))
        self._writeByte(self._mode_adr, oldmode)

        time.sleep(0.005)
        self._writeByte(self._mode_adr, oldmode | 0x80)

    def setDuty(self, channel, duty):
        '''
        Sets a single PWM channel. The value is stored in the device.
        @param channel: one of the channels 0..15
        @param duty: the duty cycle 0..100
        '''
        data = int(duty * 4096 / 100)  # 0..4096 (included)
        on = 0  # 每次周期00一开始就输出高电平
        self._writeByte(self._LED0_ON_L + 4 * channel, on & 0xFF)  # duty = 7，on & 0xFF = 0 将开始时间的低八位写入寄存器中
        self._writeByte(self._LED0_ON_H + 4 * channel, on >> 8)  # duty = 7，on & 0xFF = 0 将开始时间的高八位写入寄存器中
        self._writeByte(self._LED0_OFF_L + 4 * channel, data & 0xFF)  # duty = 7，data & 0xFF = 30 将关闭时间低八位写入寄存器中
        self._writeByte(self._LED0_OFF_H + 4 * channel, data >> 8)  # duty = 7，data >> 8 = 1，去掉所有下八位 将关闭时间的高八位写入寄存器中

    def readDuty(self, channel):
        """
        -------------------------------------
        函数名称：readDuty()
        函数功能：将寄存器中的值读出来并经过处理后得出占空比
        输入参数：channel    输出参数:Value_Duty
        编制人：周峰立        编制日期：2021.02.03
        ------------------------------------
        """
        Value_LEDx_ON_L = self._readByte(self._LED0_ON_L + 4 * channel) | 0  # 读取开始时间的低八位的值
        Value_LEDx_ON_H = self._readByte(self._LED0_ON_H + 4 * channel) << 8  # 读取开始时间的高八位的值
        Value_LEDx_OFF_L = self._readByte(self._LED0_OFF_L + 4 * channel) | 0  # 读取结束时间的低八位的值
        Value_LEDx_OFF_H = self._readByte(self._LED0_OFF_H + 4 * channel) << 8  # 读取结束时间的高八位的值
        Value_Data = Value_LEDx_OFF_H + Value_LEDx_OFF_L - Value_LEDx_ON_H - Value_LEDx_ON_L  # 用结束时间减去开始时间即可算出高电平持续的时间
        Value_Duty = Value_Data * 100 / 4096  # 算出占空比
        return Value_Duty  # 返回占空比

    def _writeByte(self, reg, value):
        try:
            self.bus.write_byte_data(self.address, reg, value)  # 将设备中的值写入寄存器中
        except Exception as e:
            print("Error while writing to I2C device")
            print(e)

    def _readByte(self, reg):
        try:
            result = self.bus.read_byte_data(self.address, reg)
            return result
        except Exception as e:
            print("Error while reading from I2C device")
            print(e)
            return None
