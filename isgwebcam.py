# -*- coding:utf-8 mode:Python -*-
from logging import getLogger, StreamHandler, DEBUG, Formatter
from pprint import pformat
import time
from datetime import datetime
from bottle import request, get, route, run, template, static_file, \
    debug, hook, default_app
from beaker.middleware import SessionMiddleware
import WaitQueue

debug(True)  # for debug

session_opts = {
    'session.data_dir': './session/data',
    'session.lock_dir': './session/lock',
    'session.type': 'file',
    'session.auto': True,
    'session.cookie_expires': True,
    'session.key': 'isg_session',
}


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


@route('/gp/gs')
def get_session():
    """gs is 'Get Session'; First access from web client. """
    session = request.environ.get('beaker.session')
    session.save()
    logger.debug('session.id=[{}]'.format(session.id))
    return '{}'.format(session.id)


@route('/gp/eq')
def entry_wait_queue():
    session = request.environ.get('beaker.session')
    session.save()
    wait_queue.entry(session.id, datetime.today())
    return 'OK'


@route('/gp/as')
def alive_sesion():
    """Checking alive session. client request per by 10sec.
    """
    session = request.environ.get('beaker.session')
    session['alive_time'] = datetime.today()
    session.save()
    return 'OK'


@get('/gp/sd')
def from_data():
    turn = request.query.t
    beam = request.query.b
    arm = request.query.a
    backet = request.query.bk
    backetturn = request.query.bt
    return 'Ok'


if __name__ == '__main__':
    logger = getLogger(__name__)
    formatter = Formatter('%(asctime)s - '
                          '%(levelname)s - '
                          '%(filename)s:%(lineno)d - '
                          '%(funcName)s - '
                          '%(message)s')
    sh = StreamHandler()
    sh.setLevel(DEBUG)
    sh.setFormatter(formatter)
    logger.setLevel(DEBUG)
    logger.addHandler(sh)

    wait_queue = WaitQueue()

    app = default_app()
    app = SessionMiddleware(app, session_opts)
    run(app=app,
        host='192.168.115.7',
        port=8080,
        reloader=True)  # for debug
