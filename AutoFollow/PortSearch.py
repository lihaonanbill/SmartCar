# writer: lihaonan_Bill
# date:  2022/3/10 21:48
import serial.tools.list_ports

port_list = list(serial.tools.list_ports.comports())


def getPort():
    return [str(port_list[0])[0:12], str(port_list[1])[0:12]]
