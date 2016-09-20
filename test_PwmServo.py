#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logging import getLogger, FileHandler, DEBUG, Formatter
from time import sleep
import unittest
import serial
import PwmServo

signature ="Sep 21 2016 07:02:50"
com_port = '/dev/ttyN328P'
com_boud = 115200
com_timeout = 10
open_with_soft_reset = 2


class TestArduinoSerial(unittest.TestCase):
    """Waiting 2 sec by serial open. for arduino enable soft-reset."""
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

class TestServos(unittest.TestCase):
    """In WebCam4 now (20160911), have 2 command servos.
    servo id is 1 and 2.
    NO RESET ARDUINO
    """
    def setUp(self):
        """ open serial port."""
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

    def testDetach(self):
        for i in [0, 1]:
            with self.subTest(i=i):
                pwm = PwmServo.PwmDetach()
                pwm.prepare(i)
                self.assertTrue(pwm.execute(self.ser))
                buf = bytes(pwm.recv).decode('utf-8')
                self.assertEqual(buf, "O:D")

    def testSignature(self):
        """ Check signature on PwmServo.ino.
        if FAIL, connect monitor then get 'O:S XXX mm YYYY HH:MM:SS'.
        Global variable signature update by 'XXX mm YYY HH:MM:SS'
        in this file and update in PwmServo::PwmSignature() in
        PwmServo.py."""
        pwm = PwmServo.PwmSignature()
        pwm.prepare()
        self.assertTrue(pwm.execute(self.ser))
        buf = bytes(pwm.recv).decode('utf-8')
        self.assertEqual(buf, signature)

    def testInfo(self):
        pwm = PwmServo.PwmInfo()
        pwm.prepare()
        self.assertTrue(pwm.execute(self.ser))
        buf = bytes(pwm.recv).decode('utf-8')
        self.assertEqual(buf[:3], "O:I")
        self.assertEqual(buf,
                         "O:I\r\n"
                         "Sv,pin,min,max\r\n"
                         "0,9,800,2200\r\n"
                         "1,10,800,2200\r\n")

    def testRead(self):
        """Get addr 0 from N328P.
        N328P addr 0 is I2C address (01H, no use)."""
        pwm = PwmServo.PwmRead()
        pwm.prepare(0)
        self.assertTrue(pwm.execute(self.ser))
        buf = bytes(pwm.recv).decode('utf-8')
        self.assertEqual(buf[:3], "O:R")
        self.assertEqual(buf[3:], "1")

    def no_testWriteAndRead(self):
        """EEPROM write.
        If you want write to EEPROM, rename no_testWriteAndRead to
        testWriteAndRead. (python unittest only run name-first 'test'.)
        """
        EEPROM_SERVO_0 = 1
        EEPROM_MIN_L_OFFSET = 1
        EEPROM_MIN_H_OFFSET = 2
        EEPROM_MAX_L_OFFSET = 3
        EEPROM_MAX_H_OFFSET = 4
        EEPROM_SERVO_1 = 6
        pwm = PwmServo.PwmWrite()
        pwm.prepare(EEPROM_SERVO_0, 9)
        self.assertTrue(pwm.execute(self.ser))
        min = (800).to_bytes(2, 'little')
        max = (2200).to_bytes(2, 'little')
        pwm.prepare(EEPROM_SERVO_0 + EEPROM_MIN_L_OFFSET, min[0])
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        pwm.prepare(EEPROM_SERVO_0 + EEPROM_MIN_H_OFFSET, min[1])
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        pwm.prepare(EEPROM_SERVO_0 + EEPROM_MAX_L_OFFSET, max[0])
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        pwm.prepare(EEPROM_SERVO_0 + EEPROM_MAX_H_OFFSET, max[1])
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        pwm.prepare(EEPROM_SERVO_1, 10)
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        pwm.prepare(EEPROM_SERVO_1 + EEPROM_MIN_L_OFFSET, min[0])
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        pwm.prepare(EEPROM_SERVO_1 + EEPROM_MIN_H_OFFSET, min[1])
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        pwm.prepare(EEPROM_SERVO_1 + EEPROM_MAX_L_OFFSET, max[0])
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        pwm.prepare(EEPROM_SERVO_1 + EEPROM_MAX_H_OFFSET, max[1])
        self.assertTrue(pwm.execute(self.ser))

    def testPulse(self):
        a = PwmServo.PwmAttach()
        d = PwmServo.PwmDetach()
        pwm = PwmServo.PwmPulse()
        for sv in [0, 1]:
            with self.subTest(sv=sv):
                a.prepare(sv)
                self.assertTrue(a.execute(self.ser))
                pwm.prepare(sv, 800)
                self.assertTrue(pwm.execute(self.ser))
                sleep(2)
                pwm.prepare(sv, 2200)
                self.assertTrue(pwm.execute(self.ser))
                sleep(2)
                pwm.prepare(sv, 1500)
                self.assertTrue(pwm.execute(self.ser))
                sleep(2)
                d.prepare(sv)
                self.assertTrue(d.execute(self.ser))

class TestServosNoWait(unittest.TestCase):
    """IF enable soft-reset, follow tests alway FAIL."""
    def setUp(self):
        """ open serial port."""
        self.ser = serial.Serial()
        self.ser.port = com_port
        self.ser.baudrate = com_boud
        self.ser.timeout = com_timeout
        self.ser.open()
        self.ser.read(self.ser.in_waiting)

    def tearDown(self):
        """Deleting self.cmd and closing serial port."""
        self.ser.close()

    def testDetach(self):
        for i in [0, 1]:
            with self.subTest(i=i):
                pwm = PwmServo.PwmDetach()
                pwm.prepare(i)
                self.assertTrue(pwm.execute(self.ser))
                buf = bytes(pwm.recv).decode('utf-8')
                self.assertEqual(buf, "O:D")

    def testSignature(self):
        pwm = PwmServo.PwmSignature()
        pwm.prepare()
        self.assertTrue(pwm.execute(self.ser))
        buf = bytes(pwm.recv).decode('utf-8')
        self.assertEqual(buf, signature)

    def testInfo(self):
        pwm = PwmServo.PwmInfo()
        pwm.prepare()
        self.assertTrue(pwm.execute(self.ser))
        buf = bytes(pwm.recv).decode('utf-8')
        self.assertEqual(buf[:3], "O:I")
        self.assertEqual(buf,
                         "O:I\r\n"
                         "Sv,pin,min,max\r\n"
                         "0,9,800,2200\r\n"
                         "1,10,800,2200\r\n")

    def testAttach(self):
        pwm = PwmServo.PwmAttach()
        pwm.prepare(0)
        self.assertTrue(pwm.execute(self.ser))
        buf = bytes(pwm.recv).decode('utf-8')
        self.assertEqual(buf, "O:A")
        pwm.prepare(1)
        self.assertTrue(pwm.execute(self.ser))
        sleep(0.5)
        buf = bytes(pwm.recv).decode('utf-8')
        self.assertEqual(buf, "O:A")

    def testPulse(self):
        a = PwmServo.PwmAttach()
        d = PwmServo.PwmDetach()
        pwm = PwmServo.PwmPulse()
        for sv in [0, 1]:
            with self.subTest(sv=sv):
                a.prepare(sv)
                self.assertTrue(a.execute(self.ser))
                pwm.prepare(sv, 800)
                self.assertTrue(pwm.execute(self.ser))
                sleep(2)
                pwm.prepare(sv, 2200)
                self.assertTrue(pwm.execute(self.ser))
                sleep(2)
                pwm.prepare(sv, 1500)
                self.assertTrue(pwm.execute(self.ser))
                sleep(2)
                d.prepare(sv)
                self.assertTrue(d.execute(self.ser))

if __name__ == '__main__':
    unittest.main()
