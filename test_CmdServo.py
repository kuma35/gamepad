#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logging import getLogger, FileHandler, DEBUG, Formatter, shutdown
from time import sleep
import serial
import unittest
import CmdServo

com_port = '/dev/ttyFT485R'
com_boud = 115200
com_timeout = 1
log_file = 'log/test_CmdServo.log'


class TestExistServos(unittest.TestCase):
    """In WebCam4 now (20160911), have 2 command servos.
    servo id is 1 and 2.
    """
    def setUp(self):
        """ open serial port """
        self.ser = serial.Serial(com_port,
                                 com_boud,
                                 timeout=com_timeout)
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
        """Deleting self.cmd and closing serial port."""
        self.ser.close()
        self.sh.close()
        self.logger.removeHandler(self.sh)

    def test_exist_servos(self):
        """Servos return a \x07 if exists and ready. """
        self.cmd = CmdServo.CmdAck(self.logger)
        for id in [1, 2]:
            with self.subTest(id=id):
                self.cmd.prepare(id)
                self.assertTrue(self.cmd.execute(self.ser))
                self.assertTrue(len(self.cmd.recv) > 0)
                self.assertEqual(self.cmd.recv[0], 7)


class TestInfo(unittest.TestCase):

    def setUp(self):
        """Open serial port."""
        self.ser = serial.Serial(com_port,
                                 com_boud,
                                 timeout=com_timeout)
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
        """Cosing serial port."""
        self.ser.close()
        self.sh.close();
        self.logger.removeHandler(self.sh)

    def test_info_return_short_packet_header(self):
        for servo_id in [1, 2]:
            with self.subTest(servo_id=servo_id):
                cmd = CmdServo.CmdInfo(self.logger)
                cmd.prepare(servo_id=servo_id, section=3)
                self.assertTrue(cmd.execute(self.ser))
                cmd.info()
                self.assertEqual(cmd.mem['packet_header'], 'FDDF')
                self.assertEqual(cmd.mem['servo_id'], servo_id)

    def test_info_section_3(self):
        """Model Number (L,H):(50H, 40H)(RS405CB) for servo 1 and 2."""
        for servo_id in [1, 2]:
            with self.subTest(servo_id=servo_id):
                cmd = CmdServo.CmdInfo(self.logger)
                cmd.prepare(servo_id=servo_id, section=3)
                self.assertTrue(cmd.execute(self.ser))
                self.assertEqual(cmd.recv[0], 0xfd)
                self.assertEqual(cmd.recv[1], 0xdf)
                self.assertEqual(cmd.get_checksum(cmd.recv[:-1]),
                                 cmd.recv[-1])
                self.assertTrue(cmd.check_return_packet(cmd.recv))
                cmd.info()
                self.assertEqual(cmd.mem['Model_Number_L'], 0x50)
                self.assertEqual(cmd.mem['Model_Number_H'], 0x40)
                self.assertEqual(cmd.mem['Servo_ID'], servo_id)
                self.assertEqual(cmd.mem['Reverse'], 0)

    def test_info_section_5(self):
        for servo_id in [1, 2]:
            with self.subTest(servo_id=servo_id):
                cmd = CmdServo.CmdInfo(self.logger)
                cmd.prepare(servo_id=servo_id, section=5)
                self.assertTrue(cmd.execute(self.ser))
                self.assertEqual(cmd.recv[0], 0xfd)
                self.assertEqual(cmd.recv[1], 0xdf)
                self.assertEqual(cmd.get_checksum(cmd.recv[:-1]),
                                 cmd.recv[-1])
                self.assertTrue(cmd.check_return_packet(cmd.recv))
                cmd.info()
                self.assertEqual(cmd.mem['Max_Torque'], 0x64)
                self.assertEqual(cmd.mem['Torque_Enable'], 0)
                self.assertEqual(cmd.mem['Present_Speed'], 0)
                self.logger.debug('Present_Posion:{0}'
                                  .format(cmd.mem['Present_Posion']/10))

class TestMove(unittest.TestCase):

    def setUp(self):
        """Open serial port."""
        self.ser = serial.Serial(com_port,
                                 com_boud,
                                 timeout=com_timeout)
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
        """Cosing serial port."""
        self.ser.close()
        self.sh.close();
        self.logger.removeHandler(self.sh)

    def no_test_move_slow(self):
        """Testing be able to slow move.
        Result: Over 300(3.00sec), lacking torque, can not move start.
        和文：どのぐらい遅く動かせるかテスト。
        300(3.00sec)以上を指定すると動かなかった。遅く動かすためにサーボ
        モータへの出力を下げるのかな？
        また同時に動作途中に動作をキャンセルできるかどうかテスト→NG。
        Present_PosionをGoal_Posisonに代入すれば動作をキャンセルできるか
        と思ったが、Present_Posionの更新は動作終了時に行っているようだ。"""
        Sv = 2
        info = CmdServo.CmdInfo(self.logger)
        info.prepare(Sv,section=5)
        info.execute(self.ser)
        info.info()
        self.logger.debug('Present_Posion:{0}'
                          .format(info.mem['Present_Posion']/10))
        trq = CmdServo.CmdTorque(self.logger)
        trq.prepare(Sv, 'on')
        trq.execute(self.ser)
        cmd = CmdServo.CmdAngle(self.logger)
        cmd.prepare(Sv, 900, 300)
        cmd.execute(self.ser)
        sleep(2)
        cmd.prepare(Sv, 300, 300)
        cmd.execute(self.ser)
        sleep(10)
        trq.prepare(Sv, 'off')
        trq.execute(self.ser)

    def test_kamae(self):
        """Testing 'kamae' form.
        0. Initial pos Sv1:90deg, Sv2:-90deg(both torque off)
        1. torque off CmdServo2.
        2. torque on CmdServo1.
        3. move CmdServo1 to 300(30.0 degree), speed 300
        4. torque on CmdServo2.(Beam and Arm -60deg)
        5. move CmdServo1 to -30
        6. stay hold and you see mjpg-stremaer shapshot.
        """
        c = CmdServo.CmdAngle(self.logger)
        t = CmdServo.CmdTorque(self.logger)
        t.prepare(2, 'off')
        t.execute(self.ser)
        t.prepare(1, 'on')
        t.execute(self.ser)
        c.prepare(1, 300, 300)
        c.execute(self.ser)
        sleep(3)
        t.prepare(2, 'on')
        t.execute(self.ser)
        c.prepare(1, -300, 300)
        c.execute(self.ser)

    def test_kamae3(self):
        """Testing 'kamae' form.
        0. Initial pos Sv1:90deg, Sv2:-90deg(both torque off)
        1. torque off CmdServo2.
        2. torque on CmdServo1.
        3. move CmdServo1 to 300(30.0 degree), speed 300
        4. torque on CmdServo2.(Beam and Arm -60deg)
        5. move CmdServo1 to -30
        6. stay hold and you see mjpg-stremaer shapshot.
        """
        c = CmdServo.CmdAngle(self.logger)
        t = CmdServo.CmdTorque(self.logger)
        t.prepare(1, 'on')
        t.execute(self.ser)
        c.prepare(1, 0, 0)
        c.execute(self.ser)

    def test_beam(self):
        """Testing arm(CmdServo id 1)."""
        c = CmdServo.CmdAngle(self.logger)
        t = CmdServo.CmdTorque(self.logger)
        t.prepare(1, 'on')
        t.execute(self.ser)
        c.prepare(1, 300, 300)
        c.execute(self.ser)

    def test_arm(self):
        """Testing arm(CmdServo id 2)."""
        c = CmdServo.CmdAngle(self.logger)
        t = CmdServo.CmdTorque(self.logger)
        t.prepare(2, 'on')
        t.execute(self.ser)
        c.prepare(2, -300, 0)
        c.execute(self.ser)

    def test_naore(self):
        """Testing 'naore' form.
        """
        c = CmdServo.CmdAngle(self.logger)
        t = CmdServo.CmdTorque(self.logger)
        c.prepare(1, 900, 0)
        c.execute(self.ser)
        sleep(3)
        t.prepare(2, 'off')
        t.execute(self.ser)
        t.prepare(1, 'off')
        t.execute(self.ser)

    def test_datsuryoku(self):
        """Testing 'naore' form.
        """
        t = CmdServo.CmdTorque(self.logger)
        t.prepare(2, 'off')
        t.execute(self.ser)
        t.prepare(1, 'off')
        t.execute(self.ser)

if __name__ == '__main__':
    unittest.main()
