#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial
import unittest
import CmdServo

com_port = '/dev/ttyFT485R'
com_boud = 115200
com_timeout = 1


class TestExistServos(unittest.TestCase):
    """In WebCam4 now (20160911), have 2 command servos.
    servo id is 1 and 2.
    """
    def setUp(self):
        """ open serial port """
        self.ser = serial.Serial(com_port,
                                 com_boud,
                                 timeout=com_timeout)
        self.cmd = CmdServo.CmdAck()

    def tearDown(self):
        """Deleting self.cmd and closing serial port."""
        del self.cmd
        self.ser.close()

    def test_exist_servo_1(self):
        """Servo 1 return a charctor \x07 if exists and ready. """
        self.cmd.prepare(1)
        self.cmd.execute(self.ser)
        self.assertTrue(len(self.cmd.recv) > 0)
        self.assertEqual(self.cmd.recv[0], bytes([7]))

    def test_exist_servo_2(self):
        """Servo 2 return a charctor \x07 if exists and ready. """
        self.cmd.prepare(2)
        self.cmd.execute(self.ser)
        self.assertTrue(len(self.cmd.recv) > 0)
        self.assertEqual(self.cmd.recv[0], bytes([7]))

if __name__ == '__main__':
    unittest.main()
