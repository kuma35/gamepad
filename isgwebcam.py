# -*- coding:utf-8 mode:Python -*-
from logging import getLogger, FileHandler, DEBUG, Formatter
from pprint import pformat
import time
from datetime import datetime
from bottle import request, get, route, run, template, static_file, \
    debug, hook, default_app
from beaker.middleware import SessionMiddleware
import serial
import pprint
import WaitQueue
import CmdServo
import Amplifier

debug(True)  # for debug

session_opts = {
    'session.data_dir': './session/data',
    'session.lock_dir': './session/lock',
    'session.type': 'file',
    'session.auto': True,
    'session.cookie_expires': True,
    'session.key': 'isg_session',
}

cmd_servo_port = '/dev/ttyFT485R'
cmd_servo_boud = 115200
beam_servo = 1  # servo id
arm_servo = 2  # servo id


def move_cmd_servo(servo_id, step_angle):
    pp = pprint.PrettyPrinter(indent=4)
    if step_angle != 0:
        ser = serial.Serial(cmd_servo_port,
                            cmd_servo_boud,
                            timeout=1)
        cmd_ack = CmdServo.CmdAck(logger)
        cmd_ack.prepare(servo_id)
        cmd_ack.execute(ser)
        if len(cmd_ack.recv) == 0 or cmd_ack.recv[0] != bytes([7]):
            logger.warn('can not access servo id 1.')
            return ' Ok'
        cmd_info = CmdServo.CmdInfo(logger)
        cmd_info.prepare(servo_id, 5)
        cmd_info.execute(ser)
        cmd_info.info(pp)
        cmd_torque = CmdServo.CmdTorque(logger)
        cmd_torque.prepare(servo_id, 'on')
        cmd_torque.execute(ser)
        logger.debug('Present Posison:{0}'
                     .format(cmd_info.mem['Present_Posion']))
        new_angle = cmd_info.mem['Present_Posion'] + step_angle
        cmd_angle = CmdServo.CmdAngle(logger)
        cmd_angle.prepare(servo_id, new_angle, 10)
        cmd_angle.execute(ser)
        ser.close()


def torque_off_cmd_servos():
    ser = serial.Serial(cmd_servo_port,
                        cmd_servo_boud,
                        timeout=1)
    for servo_id in [1, 2]:
        cmd = CmdServo.CmdTorque(logger)
        cmd.prepare(servo_id, 'off')
        cmd.execute(ser)
        del cmd
    ser.close()

#  routing


@route('/doc/')
def get_devel_doc_index():
    return static_file(filename='index.html', root='./doc/ja/_build/html')


@route('/doc/<path:path>')
def get_delvel_doc(path):
    return static_file(filename=path, root='./doc/ja/_build/html')


@route('/')
def index():
    return static_file(filename='index.html', root='./static')


@route('/css/<name>')
def get_css(name):
    return static_file(filename=name, root='./static/css')


@route('/fonts/<name>')
def get_fonts(name):
    return static_file(filename=name, root='./static/fonts')


@route('/js/<name>')
def get_js(name):
    return static_file(filename=name, root='./static/js')


@route('/<name>')
def root_file(name):
    return static_file(filename=name, root='./static')


@route('/gp/as')
def alive_session():
    """Checking alive session.
    Need reequest from client per less than expire_span_time.
    In client, maybe use setInerval()
    Expire entry from wait_queue over expire_span_time.
    Entry session if not in wait_queue

    :return: queue entry index. 0 is active, index > 0 is waiting.
    """
    session = request.environ.get('beaker.session')
    session['alive_time'] = datetime.today()
    session.save()
    i = wait_queue.alive(session.id, datetime.today())
    if i == -1:
        wait_queue.entry(session.id, datetime.today())
        i = wait_queue.exist_session(session.id)
    return '{0}'.format(i)


@route('/gp/es')
def expire_session():
    """ Expire now session.
    If expired a session, re-get at alive_session quickly and
    re-entry to wait_queue(of cource, last entry).
    """
    session = request.environ.get('beaker.session')
    session.delete()
    return 'OK'


@get('/gp/sd')
def from_data():
    """Send control data from client.
    """
    pp = pprint.PrettyPrinter(indent=4)

    turn = request.query.t
    beam = float(request.query.b)
    arm = float(request.query.a)
    backet = request.query.bk
    backetturn = request.query.bt
    torque_off = float(request.query.to)

    if torque_off == 1.0:
        torque_off_cmd_servos()
        return 'OK'

    beam_amp = Amplifier.BeamAmplifier()
    beam_angle = beam_amp.get_angle(beam)
    # logger.debug('beam_angle={0}'.format(beam_angle))
    move_cmd_servo(beam_servo, beam_angle)

    arm_amp = Amplifier.ArmAmplifier()
    arm_angle = arm_amp.get_angle(arm)
    # logger.debug('arm_angle={0}'.format(arm_angle))
    move_cmd_servo(arm_servo, arm_angle)

    return 'OK'

if __name__ == '__main__':
    logger = getLogger(__name__)
    formatter = Formatter('%(asctime)s - '
                          '%(levelname)s - '
                          '%(filename)s:%(lineno)d - '
                          '%(funcName)s - '
                          '%(message)s')
    sh = FileHandler('webcam4.log')
    sh.setLevel(DEBUG)
    sh.setFormatter(formatter)
    logger.setLevel(DEBUG)
    logger.addHandler(sh)

    wait_queue = WaitQueue.WaitQueue()

    app = default_app()
    app = SessionMiddleware(app, session_opts)
    run(app=app,
        host='192.168.115.7',
        port=8080,
        reloader=True)  # for debug
