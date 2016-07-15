# -*- coding:utf-8 mode:Python -*-
from bottle import request, get, route, run, template, static_file, debug, hook, default_app
from beaker.middleware import SessionMiddleware
debug(True) #for debug

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
    'session.cookie_expires': True,
}

@route('/')
def index() :
    return static_file(filename='index.html', root='./static')

@route('/css/<name>')
def get_css(name) :
    return static_file(filename=name, root='./static/css')

@route('/fonts/<name>')
def get_fonts(name) :
    return static_file(filename=name, root='./static/fonts')

@route('/js/<name>')
def get_js(name) :
    return static_file(filename=name, root='./static/js')

@route('/<name>')
def root_file(name) :
    return static_file(filename=name, root='./static')

@route('/hello/<name>')
def hello(name) :
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/gp/gs')
def get_session() :
    return 'dummy-session-id';

@get('/gp/sd')
def from_data() :
    turn = request.query.t;
    beam = request.query.b;
    arm = request.query.a;
    backet = request.query.bk;
    backetturn = request.query.bt;
    return 'Ok';

#app = beaker.middleware.SessionMiddleware(app(), session_opts)

if __name__ == '__main__':
    app = default_app()
    app = SessionMiddleware(app, session_opts)
    run(app=app, host='192.168.115.7', port=8080, reloader=True) #for debug
