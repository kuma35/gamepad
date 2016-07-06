# -*- coding:utf-8 mode:Python -*-
from bottle import get, route, run, template, static_file, debug
debug(True) #for debug

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

run(host='192.168.115.7', port=8080, reloader=True) #for debug
