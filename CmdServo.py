#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Controlling FUTABA RS405CB
# Web service version.
from logging import getLogger, NullHandler, DEBUG
import pprint
import array
import time
# import locale
import serial
import argparse
import sys


def int_l_h(memory):
    return int.from_bytes(list(memory[0:2]),
                          'little',
                          signed=True)


class CmdServoException(object):
    """ CmdServo and sub class exception. """

    pass


class CmdServo(object):
    """ Base class for servo commands. """

    def __init__(self, logger=None):
        self.packet = []
        self.recv = []
        if logger is None:
            self.logger = getLogger(__name__)
            sh = NullHandler()
            sh.setLevel(DEBUG)
            self.logger.setLevel(DEBUG)
            self.logger.addHandler(sh)
        else:
            self.logger = logger

    def get_checksum(self, packet):
        """ calculate checksum byte from packet. """

        checksum = packet[2]
        for value in packet[3:]:
            checksum ^= value
        return checksum

    def check_return_packet(self, recv):
        """After CmdServo::execute(), check received return packet.
        True:received return-packet and checksum OK.
        False:can not received or checksum NG.
        """
        if len(recv) == 0:
            self.logger.debug('NG:zero')
            return False
        if self.recv[0] != 0xfd or self.recv[1] != 0xdf:
            self.logger.debug('NG:packet header')
            return False
        if self.get_checksum(self.recv[:-1]) != ord(self.recv[-1]):
            self.logger.debug('NG:checksum NG')
            return False
        return True

    def prepare(self):
        pass

    def execute(self):
        """Sending short-pakect to specified servo and
        receiving return-packet.
        True:Received return-packet and checksum OK.
        False:Can not received return-packet or checksum NG.
        Notice:alread returned FALSE in this base class.
        """
        if self.packet is None:
            raise CmdServoException('no prepare packet. '
                                    'coll prepare() before execute.')
        return False

    def info(self, pp):
        """ pretty print recieve packet. """
        pass


class CmdInfo(CmdServo):
    """ get servo infomation memory. """

    def __init__(self, logger=None):
        super(CmdInfo, self).__init__(logger)
        self.mem = {}

    def info_short_packet_header(self, recv):
        """ dict for short packet header. """
        self.mem['packet_header'] = '{bl:X}{bh:X}'.format(bl=recv[0],
                                                          bh=recv[1])
        self.mem['servo_id'] = recv[2]
        self.mem['flag_value'] = recv[3]
        flags = []
        if recv[3] & 0b10000000:
            flags.append('Temp limit error')
        if recv[3] & 0b00100000:
            flags.append('Temp warn')
        if recv[3] & 0b00001000:
            flags.append('Flash write error')
        if recv[3] & 0b00000001:
            flags.append('Received packet can not processing')
        self.mem['flags'] = flags
        self.mem['address'] = recv[4]
        self.mem['length'] = recv[5]
        self.mem['count'] = recv[6]

    def info_section_3(self, memory):
        """ memory No.00-29. """
        self.mem['Model_Number_L'] = memory[0]
        self.mem['Model_Number_H'] = memory[1]
        self.mem['Firmware_Version'] = memory[2]
        self.mem['Servo_ID'] = memory[4]
        self.mem['Reverse'] = memory[5]
        self.mem['Boud_Rate'] = memory[6]
        self.mem['Return_Delay'] = memory[7]
        self.mem['CW_Angle_Limit'] = int_l_h(memory[8:10])
        self.mem['CCW_Angle_Limit'] = int_l_h(memory[10:12])
        self.mem['Temperture_Limit'] = int_l_h(memory[14:16])
        self.mem['Damper'] = memory[20]
        self.mem['Torque_in_Silence'] = memory[22]
        self.mem['Warm_up_Time'] = memory[23]
        self.mem['CW_Compliance_Margin'] = memory[24]
        self.mem['CCW_Compliance_Margin'] = memory[25]
        self.mem['CW_Compliance_Slope'] = memory[26]
        self.mem['CCW_Compliance_Slope'] = memory[27]
        self.mem['Punch'] = int_l_h(memory[28:30])

    def info_section_5(self, memory):
        """ memory No.30-59.  offset 30"""
        self.mem['Goal_Position'] = int_l_h(memory[0:2])
        self.mem['Goal_Time'] = int_l_h(memory[2:4])
        self.mem['Max_Torque'] = memory[5]
        self.mem['Torque_Enable'] = memory[6]
        self.mem['Present_Posion'] = int_l_h(memory[12:14])
        self.mem['Present_Time'] = int_l_h(memory[14:16])
        self.mem['Present_Speed'] = int_l_h(memory[16:18])
        self.mem['Present_Current'] = int_l_h(memory[18:20])
        self.mem['Present_Temperture'] = int_l_h(memory[20:22])
        self.mem['Present_Volts'] = int_l_h(memory[22:24])

    def prepare(self, servo_id, section, addr=0, length=0):
        """
        section:
         3(0011b) request memory map No.00 to No.29
         5(0101b) request memory map No.30 to No.59
         7(0111b) request memory map No.20 to No.29
         9(1001b) request memory map No.42 to No.59
        11(1011b) request memory map No.30 to No.41
        13(1101b) request memory map No.60 to No.127
        15(1111b) request from specify addr and specify length...
        """
        self.section = section
        if section in [3, 5, 7, 9, 11, 13]:
            self.packet = array.array('B',
                                      [0xFA, 0xAF,
                                       servo_id,
                                       section,
                                       0xFF,
                                       0x00,
                                       0x00])
        elif section == 15:
            self.addr = addr
            self.length = length
            self.packet = array.array('B',
                                      [0xFA, 0xAF,
                                       servo_id,
                                       section,
                                       addr,
                                       length,
                                       0x00])
        else:
            raise CmdServoException("invalid section value")
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        ser.write(self.packet)
        self.recv.extend(list(ser.read(7)))
        self.recv.extend(list(ser.read(self.recv[5])))
        self.recv.append(ser.read())  # checksum
        return self.check_return_packet(self.recv)

    def info(self, pp):
        self.logger.debug('Returned packet:')
        sum = self.recv[2]
        for value in self.recv[3:-1]:
            sum ^= value
        self.logger.debug('calculate checksum:{0}'.format(sum))
        self.logger.debug('recv checksum:{0}'.format(self.recv[-1]))
        if sum == ord(self.recv[-1]):
            self.logger.debug('checksum OK')
        else:
            self.logger.debug('checksum NG')
        self.info_short_packet_header(self.recv)
        if self.section == 3:
            self.info_section_3(self.recv[7:-1])
        elif self.section == 5:
            self.info_section_5(self.recv[7:-1])
        else:
            self.logger.debug("Data:", end='')
            self.logger.debug(pp.pformat(self.recv[7:-1]))
        self.logger.debug('{0}:{1:#x}'.format('Checksum',
                                              ord(self.recv[-1])))


class CmdAck(CmdServo):
    """ ACK command. """

    def prepare(self, servo_id):
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x01,
                                   0xFF,
                                   0x00,
                                   0x00])
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdAck, self).execute()
        ser.write(self.packet)
        self.recv.append(ser.read())
        if len(self.recv) == 0:
            return False
        if self.recv[0] != bytes([7]):
            return False
        return True

    def info(self, pp):
        self.logger.debug('ACK(\\x07):', end='')
        self.logger.debug(pp.pformat(self.recv))


class CmdSetId(CmdServo):
    """ Set Servo ID. """

    def prepare(self, servo_id, new):
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x00,
                                   0x04,
                                   0x01,
                                   0x01,
                                   new])
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdSetId, self).execute()
        ser.write(self.packet)

    def info(self, pp):
        pass


class CmdFlash(CmdServo):
    """ Write to flash ROM. """

    def prepare(self, servo_id):
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x40,
                                   0xFF,
                                   0x00,
                                   0x00])
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdFlash, self).execute()
        ser.write(self.packet)
        time.sleep(1)

    def info(self, pp):
        pass


class CmdReboot(CmdServo):
    """ Reboot Servo. """

    def prepare(self, servo_id):
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x20,
                                   0xFF,
                                   0x00,
                                   0x00])
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdReboot, self).execute()
        ser.write(self.packet)
        time.sleep(3)

    def info(self, pp):
        pass


class CmdAngle(CmdServo):
    """ Goal Angle and Goal Time. Please Torque ON first!"""

    def prepare(self, servo_id, degree, speed):
        degree_packet = list(degree.to_bytes(2, 'little', signed=True))
        speed_packet = list(speed.to_bytes(2, 'little', signed=True))
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x00,
                                   0x1E,
                                   0x04,
                                   0x01])
        self.packet.extend(degree_packet)
        self.packet.extend(speed_packet)
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdAngle, self).execute()
        ser.write(self.packet)

    def info(self, pp):
        pass


class CmdMaxTorque(CmdServo):
    """ Set Max Torque. """

    def prepare(self, servo_id, rate):
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x00,
                                   0x23,
                                   0x01,
                                   0x01,
                                   rate])
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdMaxTorque, self).execute()
        ser.write(self.packet)

    def info(self, pp):
        pass


class CmdTorque(CmdServo):
    """ Torque on/off/brak """

    def prepare(self, servo_id, flag):
        if flag == 'on':
            value = 1
        elif flag == 'off':
            value = 0
        elif flag == 'break':
            value = 2
        else:
            raise CmdServoException('unknown torque flag. '
                                        'valid on/off/break.')
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x00,
                                   0x24,
                                   0x01,
                                   0x01,
                                   value])
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdTorque, self).execute()
        ser.write(self.packet)

    def info(self, pp):
        pass


class CmdCwLimit(CmdServo):
    """ Set CW Limit """

    def prepare(self, servo_id, degree):
        limit_packet = list(degree.to_bytes(2, 'little', signed=True))
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x00,
                                   0x08,
                                   0x02,
                                   0x01])
        self.packet.extend(limit_packet)
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdCwLimit, self).execute()
        ser.write(self.packet)

    def info(self, pp):
        pass


class CmdCcwLimit(CmdServo):
    """ Set CCW Limit """

    def prepare(self, servo_id, degree):
        limit_packet = list(degree.to_bytes(2, 'little', signed=True))
        self.packet = array.array('B',
                                  [0xFA, 0xAF,
                                   servo_id,
                                   0x00,
                                   0x0A,
                                   0x02,
                                   0x01])
        self.packet.extend(limit_packet)
        checksum = self.get_checksum(self.packet)
        self.packet.append(checksum)
        return self.packet

    def execute(self, ser):
        super(CmdCcwLimit, self).execute()
        ser.write(self.packet)

    def info(self, pp):
        pass


def main():
    parser = argparse.ArgumentParser(
        description='Manupirate FUTABA command servo RS405CB.')
    parser.add_argument(
        '--version', action='version', version='%(prog)s 0.0')
    parser.add_argument('-p', '--port',
                        dest='port',
                        default='/dev/ttyUSB0',
                        metavar='DEVICE')
    parser.add_argument('-b', '--baud',
                        dest='baud',
                        default=115200)
    parser.add_argument('-i', '--id',
                        dest='servo_id',
                        type=int,
                        help='servo ID.',
                        default=1)
    parser.add_argument('--ack',
                        action='store_true',
                        default=True,
                        help='Checking specified id\'s servo existance.')
    parser.add_argument('--dryrun',
                        action='store_true',
                        help='no port open, no execute.')
    subparsers = parser.add_subparsers(dest='subparser_name')
    subparser1 = subparsers.add_parser('ack',
                                       help='return ACK(\\x07)')
    subparser2 = subparsers.add_parser('info',
                                       help='read memory')
    subparser2.add_argument(
        '-s', '--section',
        dest='section',
        type=int,
        choices=[3, 5, 7, 9, 11, 13, 15],
        default=3,
        help='read memory 3:00-29, 5:30-59, 7:20-29, 9:42-59, '
        '11:30-41, 13:60-127, 15:specify addr and length')
    subparser2.add_argument('--addr',
                            type=int,
                            help='section is 15, use --addr .')
    subparser2.add_argument('--length',
                            type=int,
                            help='section is 15, use --length .')
    subparser3 = subparsers.add_parser(
        'setid',
        help='set new servo ID to Servo. NOTICE:NO UPDATE FLASH.')
    subparser3.add_argument('new',
                            type=int,
                            help='new servo ID.')
    subparser4 = subparsers.add_parser('flash',
                                       help='write to flash ROM.')
    subparser5 = subparsers.add_parser('reboot',
                                       help='Reboot Servo.')
    subparser6 = subparsers.add_parser('angle',
                                       help='set angle and speed.')
    subparser6.add_argument('--speed',
                            type=int,
                            default=0,
                            help='Goal Time. 0-0x3fff.')
    subparser6.add_argument('degree',
                            type=int,
                            help='Goal Angle. 90degree to set 900.')
    subparser7 = subparsers.add_parser('maxtorque',
                                       help='max torque')
    subparser7.add_argument('torque_rate',
                            type=int,
                            default=100,
                            choices=range(0, 101),
                            help='max torque % 0-100')
    subparser8 = subparsers.add_parser('torque',
                                       help='torque on/off/break.')
    subparser8.add_argument('torque_flag',
                            choices=['on', 'off', 'break'],
                            help='torque on/off/break')
    subparser9 = subparsers.add_parser('cwlimit',
                                       help='set CW Angle Limit.')
    subparser9.add_argument('degree',
                            type=int,
                            help='CW Angle Limit; 0 to 1500')
    subparser10 = subparsers.add_parser('ccwlimit',
                                        help='set CCW Angle Limit.')
    subparser10.add_argument('degree',
                             type=int,
                             help='CCW Angle Limit; 0 to -1500')

    args = parser.parse_args()

    if args.subparser_name == 'ack':
        cmd = CmdAck()
        cmd.prepare(args.servo_id)
    elif args.subparser_name == 'info':
        cmd = CmdInfo()
        cmd.prepare(args.servo_id, args.section, args.addr, args.length)
    elif args.subparser_name == 'setid':
        cmd = CmdSetId()
        cmd.prepare(args.servo_id, args.new)
    elif args.subparser_name == 'flash':
        cmd = CmdFlash()
        cmd.prepare(args.servo_id)
    elif args.subparser_name == 'reboot':
        cmd = CmdReboot()
        cmd.prepare(args.servo_id)
    elif args.subparser_name == 'angle':
        cmd = CmdAngle()
        cmd.prepare(args.servo_id, args.degree, args.speed)
    elif args.subparser_name == 'maxtorque':
        cmd = CmdMaxTorque()
        cmd.prepare(args.servo_id, args.torque_rate)
    elif args.subparser_name == 'torque':
        cmd = CmdTorque()
        cmd.prepare(args.servo_id, args.torque_flag)
    elif args.subparser_name == 'cwlimit':
        cmd = CmdCwLimit()
        cmd.prepare(args.servo_id, args.degree)
    elif args.subparser_name == 'ccwlimit':
        cmd = CmdCcwLimit()
        cmd.prepare(args.servo_id, args.degree)
    else:
        parser.exit(0, 'no specifiy command, nothing to do.\n')

    pp = pprint.PrettyPrinter(indent=4)
    if args.dryrun:
        print("====== DRY RUN. NOT EXECUTING =====")
        print("generate packet:", end='')
        pp.pprint(cmd.packet)
    else:
        ser = serial.Serial(args.port, args.baud, timeout=1)
        if args.ack and args.subparser_name != 'ack':
            cmd_ack = CmdAck()
            cmd_ack.prepare(args.servo_id)
            cmd_ack.execute(ser)
            if len(cmd_ack.recv) == 0 or cmd_ack.recv[0] != bytes([7]):
                print("NO EXIST Servo ID's Servo. please check servo ID.")
                sys.exit(1)
        cmd.execute(ser)
        cmd.info(pp)
        ser.close()


if __name__ == '__main__':
    main()
