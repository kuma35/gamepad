#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial
import unittest
import pprint
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
        self.assertTrue(self.cmd.execute(self.ser))
        self.assertTrue(len(self.cmd.recv) > 0)
        self.assertEqual(self.cmd.recv[0], bytes([7]))

    def test_exist_servo_2(self):
        """Servo 2 return a charctor \x07 if exists and ready. """
        self.cmd.prepare(2)
        self.assertTrue(self.cmd.execute(self.ser))
        self.assertTrue(len(self.cmd.recv) > 0)
        self.assertEqual(self.cmd.recv[0], bytes([7]))


class TestInfo(unittest.TestCase):

    def setUp(self):
        """Open serial port."""
        self.pp = pprint.PrettyPrinter(indent=4)
        self.ser = serial.Serial(com_port,
                                 com_boud,
                                 timeout=com_timeout)

    def tearDown(self):
        """Cosing serial port."""
        self.ser.close()

    def test_info_return_short_packet_header(self):
        for servo_id in [1, 2]:
            with self.subTest(servo_id=servo_id):
                cmd = CmdServo.CmdInfo()
                cmd.prepare(servo_id=servo_id, section=3)
                self.assertTrue(cmd.execute(self.ser))
                cmd.info(self.pp)
                self.assertEqual(cmd.mem['packet_header'], 'FDDF')
                self.assertEqual(cmd.mem['servo_id'], servo_id)

    def test_info_section_3(self):
        """Model Number (L,H):(50H, 40H)(RS405CB) for servo 1 and 2."""
        for servo_id in [1, 2]:
            with self.subTest(servo_id=servo_id):
                cmd = CmdServo.CmdInfo()
                cmd.prepare(servo_id=servo_id, section=3)
                self.assertTrue(cmd.execute(self.ser))
                self.assertEqual(cmd.recv[0], 0xfd)
                self.assertEqual(cmd.recv[1], 0xdf)
                self.assertEqual(cmd.get_checksum(cmd.recv[:-1]),
                                 ord(cmd.recv[-1]))
                self.assertTrue(cmd.check_return_packet(cmd.recv))
                cmd.info(self.pp)
                self.assertEqual(cmd.mem['Model_Number_L'], 0x50)
                self.assertEqual(cmd.mem['Model_Number_H'], 0x40)
                self.assertEqual(cmd.mem['Servo_ID'], servo_id)
                self.assertEqual(cmd.mem['Reverse'], 0)

    def test_info_section_5(self):
        for servo_id in [1, 2]:
            with self.subTest(servo_id=servo_id):
                cmd = CmdServo.CmdInfo()
                cmd.prepare(servo_id=servo_id, section=5)
                self.assertTrue(cmd.execute(self.ser))
                self.assertEqual(cmd.recv[0], 0xfd)
                self.assertEqual(cmd.recv[1], 0xdf)
                self.assertEqual(cmd.get_checksum(cmd.recv[:-1]),
                                 ord(cmd.recv[-1]))
                self.assertTrue(cmd.check_return_packet(cmd.recv))
                cmd.info(self.pp)
                self.assertEqual(cmd.mem['Max_Torque'], 0x64)
                self.assertEqual(cmd.mem['Torque_Enable'], 0)
                self.assertEqual(cmd.mem['Present_Speed'], 0)

if __name__ == '__main__':
    unittest.main()
