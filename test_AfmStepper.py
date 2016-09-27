#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logging import getLogger, FileHandler, DEBUG, Formatter
from time import sleep
import unittest
import serial
import AfmStepper

log_file = 'log/test_AfmStepper.log'
signature ="Sep 27 2016 14:14:52"
com_port = '/dev/ttyACM0'
com_boud = 9600
com_timeout = 1
open_with_soft_reset = 6


class TestArduinoSerial(unittest.TestCase):
    """Waiting 2 sec by serial open. for arduino enable soft-reset."""
    def setUp(self):
        self.logger = getLogger(__name__)
        formatter = Formatter('%(asctime)s - '
                              '%(levelname)s - '
                              '%(filename)s:%(lineno)d - '
                              '%(funcName)s - '
                              '%(message)s')
        self.sh = FileHandler(log_file, delay=True)
        self.sh.setLevel(DEBUG)
        self.sh.setFormatter(formatter)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(self.sh)

    def tearDown(self):
        self.sh.close()
        self.logger.removeHandler(self.sh)

    def testReset(self):
        """IF disable soft-reset, this test alway FAIL."""
        ser = serial.Serial(com_port,
                            com_boud,
                            timeout=com_timeout)
        sleep(open_with_soft_reset)
        recv = list(ser.read(ser.in_waiting))
        buf = bytes(recv).decode('utf-8')
        self.assertEqual(buf, "O:S "+signature)
        ser.close()

    def NotestNoReset(self):
        """No implement DTR in Linux...?"""
        recv = []
        self.ser = serial.Serial()
        self.ser.port = com_port
        self.ser.baudrate = com_boud
        self.ser.timeout = com_timeout
        self.ser.dsrdtr = True
        self.ser.dtr = False
        self.ser.open()
        sleep(open_with_soft_reset)
        recv.extend(list(self.ser.read(self.ser.in_waiting)))
        buf = bytes(recv).decode('utf-8')
        self.assertEqual(buf, "O:S "+signature)
        self.ser.close()

class TestStepper(unittest.TestCase):
    def setUp(self):
        """ open serial port."""
        self.logger = getLogger(__name__)
        formatter = Formatter('%(asctime)s - '
                              '%(levelname)s - '
                              '%(filename)s:%(lineno)d - '
                              '%(funcName)s - '
                              '%(message)s')
        self.sh = FileHandler(log_file, delay=True)
        self.sh.setLevel(DEBUG)
        self.sh.setFormatter(formatter)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(self.sh)
        self.ser = serial.Serial()
        self.ser.port = com_port
        self.ser.baudrate = com_boud
        self.ser.timeout = com_timeout
        self.ser.open()
        sleep(open_with_soft_reset)
        self.ser.read(self.ser.in_waiting)

    def tearDown(self):
        """Deleting self.cmd and closing serial port."""
        self.ser.close()
        self.sh.close()
        self.logger.removeHandler(self.sh)

    def testSignature(self):
        """ Check signature on AfmStepper.ino.
        if FAIL, connect monitor then get 'O:S XXX mm YYYY HH:MM:SS'.
        Global variable signature update by 'XXX mm YYY HH:MM:SS'
        in this file and update in AfmStepper::AfmSignature() in
        AfmStepper.py."""
        afm = AfmStepper.AfmSignature(self.logger)
        afm.prepare()
        self.assertTrue(afm.execute(self.ser))
        buf = bytes(afm.recv).decode('utf-8')
        self.assertEqual(buf, signature)

    def testSweep(self):
        f = AfmStepper.AfmForward(self.logger)
        b = AfmStepper.AfmBackward(self.logger)
        f.prepare(50)
        b.prepare(50)
        f.execute(self.ser)
        sleep(30)
        b.execute(self.ser)

class TestStepperNoWait(unittest.TestCase):
    """IF enable soft-reset, follow tests alway FAIL."""
    def setUp(self):
        """ open serial port."""
        self.logger = getLogger(__name__)
        formatter = Formatter('%(asctime)s - '
                              '%(levelname)s - '
                              '%(filename)s:%(lineno)d - '
                              '%(funcName)s - '
                              '%(message)s')
        self.sh = FileHandler(log_file, delay=True)
        self.sh.setLevel(DEBUG)
        self.sh.setFormatter(formatter)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(self.sh)
        self.ser = serial.Serial()
        self.ser.port = com_port
        self.ser.baudrate = com_boud
        self.ser.timeout = com_timeout
        self.ser.open()
        self.ser.read(self.ser.in_waiting)

    def tearDown(self):
        """Deleting self.cmd and closing serial port."""
        self.ser.close()
        self.sh.close()
        self.logger.removeHandler(self.sh)

    def no_testSignature(self):
        afm = AfmStepper.AfmSignature(self.logger)
        afm.prepare()
        self.assertTrue(afm.execute(self.ser))
        buf = bytes(afm.recv).decode('utf-8')
        self.assertEqual(buf, signature)

    def no_testSweep(self):
        f = AfmStepper.AfmForward(self.logger)
        b = AfmStepper.AfmBackward(self.logger)
        f.prepare(50)
        b.prepare(50)
        f.execute(self.ser)
        sleep(10)
        b.execute(self.ser)

if __name__ == '__main__':
    unittest.main()
