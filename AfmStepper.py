#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Controlling PWM Servo by N328P
"""Afm is AdaFruit-Motorshield"""

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


class AfmStepperException(object):
    """ AfmStepper and sub class exception. """
    pass


class AfmStepper(object):
    """ Base class for conpatible Arduino uno with stepper.
    Object needs Pyserial objects. Serial.open(115200) in Arduino.
    If You get first receive text first "O:S", open() with Arduino
    soft-restart.
    Inputing lock about 2 seconds with soft-restart.
    Webcam4 disable soft-restart.
    If you want to disable, connect RESET pin and GND pin by 10μF
    capacity. (If you won to enable, remove this capacity.)
    """
    def __init__(self, logger=None):
        """Now self.recv_delay is 0.2 for 115200. If you changed baud
        rate, change self.recv_delay.(0.5 for 9600 :-)"""
        self.packet = []
        self.recv = []
        self.recv_delay = 0.5
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


class AfmForward(AfmStepper):
    def __init__(self, logger=None):
        super(AfmForward, self).__init__(logger)

    def prepare(self, count):
        self.packet = array.array('B', [ord('F'), count])
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf == "O:F"

class AfmBackward(AfmStepper):
    def __init__(self, logger=None):
        super(AfmBackward, self).__init__(logger)

    def prepare(self, count):
        self.packet = array.array('B', [ord('B'), count])
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        return buf == "O:B"

class AfmSignature(AfmStepper):
    """ get adruino sketch Stepper.ino signature.
    Compile __DATE__ and __TIME__ in Stepper.ino."""
    def __init__(self, logger=None):
        super(AfmSignature, self).__init__(logger)

    def prepare(self):
        self.packet = array.array('B', [ord('S')])
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        sleep(self.recv_delay)
        self.recv = ser.read(ser.in_waiting)
        buf = bytes(self.recv).decode('utf-8')
        self.logger.debug(buf)
        return buf == "Sep 27 2016 14:14:52"
