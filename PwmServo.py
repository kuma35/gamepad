#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Controlling PWM Servo by N328P
from logging import getLogger, NullHandler, DEBUG
import array
from time import sleep
# import locale
import serial
import argparse
import sys


def int_l_h(memory):
    return int.from_bytes(list(memory[0:2]),
                          'little',
                          signed=True)


class PwmServoException(object):
    """ PwmServo and sub class exception. """
    pass


class PwmServo(object):
    """ Base class for N328P(5V) with pwm-servos. PwmServo object needs
    Pyserial objects. Serial.open(115200) in Arduino.
    If You get first receive text first "O:S", open() with Arduino
    soft-restart.
    Inputing lock about 2 seconds with soft-restart.
    Webcam4 disable soft-restart.
    If you want to disable, connect RESET pin and GND pin by 10μF
    capacity. (If you won to enable, remove this capacity.)
    和文：PWMサーボを2基(id: 0, 1)繋げたN328P(5V)(Arudino nano互換機)に
    アップロードしたPwmServo.inoと連携するクラスのベースクラスです。
    利用するには他にPyserialオブジェクトが必要です。Arduino側では
    Serial.begin(115200)としてますので、それに合わせてpyserial
    オブジェクトをオープンしてください。
    シリアルをオープンした時に3秒待って(Time.sleep(3))、"O:S"が返された
    時はオープン時にArduinoのsoft-resetが有効です。これはUSB接続時のデフ
    ォルトです。Linux,Mac以外ではdtr=Falseでsoft-resetを無効にできるそう
    なので設定してみてください(未確認)。現在(2016/09/20)Webcam4で使って
    いるホストはLinuxなので、ハードウェアを付加して対応しています。回路
    としてはRESETとGNDを10μFのコンデンサで繋ぐだけです。再び
    soft-resetを有効にするとき(スケッチをUSBでアップロードしたいとき)は
    コンデンサを取り除くだけです。Webcam4では利便性の為これに
    トグルスイッチを追加して簡単に切り替えられるようにしています。
    """
    def __init__(self, logger=None):
        """Now self.recv_delay is 0.2 for 115200. If you changed baud
        rate, change self.recv_delay.(0.5 for 9600 :-)"""
        self.packet = []
        self.recv = []
        self.recv_delay = 0.2
        if logger is None:
            self.logger = getLogger(__name__)
            sh = NullHandler()
            sh.setLevel(DEBUG)
            self.logger.setLevel(DEBUG)
            self.logger.addHandler(sh)
        else:
            self.logger = logger

    def prepare(self):
        """Making packet(self.packet)."""
        pass

    def execute(self):
        """Sending short-pakect to specified servo and
        receiving return-packet(self.recv).
        Notice:alway returned FALSE in this base class.
        """
        if self.packet is None:
            raise PwmServoException('no prepare packet. '
                                    'coll prepare() before execute.')
        return False


class PwmAttach(PwmServo):
    """Attaching arduino Servo object to arudino digital pin."""
    def __init__(self, logger=None):
        super(PwmAttach, self).__init__(logger)

    def prepare(self, servo_id):
        """Specify servo_id. 1 or 2.
        Assigning digital pin number is read from arduino EEPROM.
        """
        self.packet = array.array('B', [ord('A'), servo_id])
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf == "O:A"

class PwmDetach(PwmServo):
    """Detach digital pin from arduino Servo object."""
    def __init__(self, logger=None):
        super(PwmDetach, self).__init__(logger)

    def prepare(self, servo_id):
        """Specify servo_id. 1 or 2."""
        self.packet = array.array('B', [ord('D'), servo_id])
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf == "O:D"
    
class PwmPulse(PwmServo):
    """Sending writeMicroseconds().
    GWS Servo accept 800 to 2200.
    http://www.gws.com.tw/english/product/servo/sat%20form.htm
    Check over max. and under min. both values read from Arduino EEPROM.
    You change EEPROM if you want to change max, min, and assign pin.
    Changing EEPROM, use PwmServo::PwmWrite() and PwmRead().
    See also PwmServo.ino.
    """
    def __init__(self, logger=None):
        super(PwmPulse, self).__init__(logger)

    def prepare(self, servo_id, pulse):
        """Specify servo_id. 1 or 2."""
        b = pulse.to_bytes(2, 'little')
        self.packet = array.array('B', [ord('P'),
                                        servo_id,
                                        b[0],
                                        b[1],])
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf == "O:P"

class PwmInfo(PwmServo):
    """Get info from Arduino."""
    def __init__(self, logger=None):
        super(PwmInfo, self).__init__(logger)

    def prepare(self):
        self.packet = array.array('B', [ord('I')])
        return self.packet

    def execute(self, ser):
        """Receiving message is a little long, self.recv_delay * 2"""
        ser.write(self.packet)
        sleep(self.recv_delay*2)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf[:3] == "O:I"


class PwmRead(PwmServo):
    """Read EEPROM."""
    def __init__(self, logger=None):
        super(PwmRead, self).__init__(logger)

    def prepare(self, addr):
        """Addr is 1 byte, value is 1 byte."""
        self.packet = array.array('B', [ord('R'),
                                        addr])
        return self.packet

    def execute(self, ser):
        """ buf[3:] is returned byte info 99H."""
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf[:3] == "O:R"

class PwmSignature(PwmServo):
    """ get adruino sketch PwmServo.ino signature.
    Compile __DATE__ and __TIME__ in PwmServo.ino."""
    def __init__(self, logger=None):
        super(PwmSignature, self).__init__(logger)

    def prepare(self):
        self.packet = array.array('B', [ord('S')])
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf == "Sep 21 2016 07:02:50"

class PwmWrite(PwmServo):
    """Write EEPROM."""
    def __init__(self, logger=None):
        super(PwmWrite, self).__init__(logger)

    def prepare(self, addr, value):
        """Addr is 1 byte, value is 1 byte."""
        self.packet = array.array('B', [ord('W'),
                                        addr,
                                        value])
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf == "O:W"
