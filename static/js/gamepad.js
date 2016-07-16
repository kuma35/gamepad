'use strict';
// ref: http://qiita.com/gyabo/items/baae116e9e4c53ca17ab
//---------------------------------------------------------------------
//  ref:https://developer.mozilla.org/en-US/docs/Web/Guide/API/Gamepad
//---------------------------------------------------------------------

// JavaScript: The good parts
// P.50 4.14 カリー化 ( use P.5 Functin.prototype.method...)
Function.prototype.method = function(name, func) {
    'use strict';
    this.prototype[name] = func;
    return this;
}

Function.method('curry', function () {
    'use strict';
    let slice = Array.prototype.slice,
	args = slice.apply(arguments),
	that = this;
    return function () {
	'use strict';
	return that.apply(null, args.concat(slice.apply(arguments)));
    };
});

//////////
const DECIMAL_WIDTH = 1;	// 小数桁数
let TargetPad = {
    'index': -1,
    'id':'',
};
let AllowAjax = true;
const rAF = window.mozRequestAnimationFrame ||
      window.webkitRequestAnimationFrame ||
      window.requestAnimationFrame;
// map
let maps = [];

const construct_map = function(spec) {
    // spec = { pad }
    let that;

    let last_pad = {
	axes:[],
	buttons:[],
    };
    let connect_flag = true;
    let gamepadid;
    let sessionid;
    let data = {	// override construct_base_map
	turn: '0.0',
	beam: '0.0',
	arm: '0.0',
	backet: '0.0',
	backetturn: '0.0',
    };
    let ctrl_axes = [];
    let ctrl_buttons = [];

    // set params
    gamepadid = spec.pad && spec.pad.id || '';

    // that && inherit
    that = {};


    // private method
    const _normal = function(v) {
	'use strict';
	return v.toFixed(DECIMAL_WIDTH);
    };
    
    const _reverse = function(v) {
	'use strict';
	return (v * -1).toFixed(DECIMAL_WIDTH);
    };

    // public method
    const none = function(v) {
	'use strict';
	;
    };
    none.id = 'none';
    that.none = none;

    const turn_normal = function(v) {
	'use strict';
	data.turn = _normal(v);
    };
    turn_normal.id = 'turn_normal';
    that.turn_normal = turn_normal;
    
    const turn_reverse = function(v) {
	'use strict';
	data.turn = _reverse(v);
    };
    turn_reverse.id = 'turn_reverse';
    that.turn_reverse = turn_reverse;
    
    const turn_left = function(v) {
	'use strict';
	data.turn = _reverse(v);
    };
    turn_left.id = 'turn_left';
    that.turn_left = turn_left;
    
    const turn_right = function(v) {
	'use strict';
	data.turn = _normal(v);
    };
    turn_right.id = 'turn_right';
    that.turn_right = turn_right;
    
    const beam_normal = function(v) {
	'use strict';
	data.beam = _normal(v);
    };
    beam_normal.id = 'beam_normal';
    that.beam_normal = beam_normal;
    
    const beam_reverse = function(v) {
	'use strict';
	data.beam = _reverse(v);
    };
    beam_reverse.id = 'beam_reverse';
    that.beam_reverse =beam_reverse;
    
    const beam_down = function(v) {
	'use strict';
	data.beam = _reverse(v);
    };
    beam_down.id = 'beam_down';
    that.beam_down = beam_down;
    
    const beam_up = function(v) {
	'use strict';
	data.beam = _normal(v);
    };
    beam_up.id = 'beam_up';
    that.beam_up = beam_up;
    
    const arm_normal = function(v) {
	'use strict';
	data.arm = _normal(v);
    };
    arm_normal.id = 'arm_normal';
    that.arm_normal = arm_normal;
    
    const arm_reverse = function(v) {
	'use strict';
	data.arm = _reverse(v);
    };
    arm_reverse.id = 'arm_reverse';
    that.arm_reverse = arm_reverse;
    
    const arm_fold = function(v) {
	'use strict';
	data.arm = _reverse(v);
    };
    arm_fold.id = 'arm_fold';
    that.arm_fold = arm_fold;
    
    const arm_extend = function(v) {
	'use strict';
	data.arm = _normal(v);
    };
    arm_extend.id = 'arm_extend';
    that.arm_extend = arm_extend;
    
    const backet_normal = function(v) {
	'use strict';
	data.backet = _normal(v);
    }
    backet_normal.id = 'backet_normal'
    that.backet_normal = backet_normal;
    
    const backet_reverse = function(v) {
	'use strict';
	data.backet = _reverse(v);
    };
    backet_reverse.id = 'backet_reverse';
    that.backet_reverse = backet_reverse;
    
    const backet_down = function(v) {
	'use strict';
	data.backet = _reverse(v);
    };
    backet_down.id = 'backet_down';
    that.backet_down = backet_down;
    
    const backet_up = function(v) {
	'use strict';
	data.backet = _normal(v);
    };
    backet_up.id = 'backet_up';
    that.backet_up = backet_up;
    
    const backetturn_normal = function(v) {
	'use strict';
	data.backetturn = _normal(v);
    };
    backetturn_normal.id = 'backetturn_normal';
    that.backetturn_normal = backetturn_normal;
    
    const backetturn_reverse = function(v) {
	'use strict';
	data.backetturn = _reverse(v);
    };
    backetturn_reverse.id = 'backetturn_reverse';
    that.backetturn_reverse = backetturn_reverse;
    
    const backetturn_left = function(v) {
	'use strict';
	data.backetturn = _reverse(v);
    };
    backetturn_left.id = 'backetturn_left';
    that.backetturn_left = backetturn_left;
    
    const backetturn_right = function(v) {
	'use strict';
	data.backetturn = _normal(v);
    };
    backetturn_right.id = 'backetturn_right';
    that.backetturn_right = backetturn_right;

    const set_axis_label = function(index) {
	'use strict';
	let label = '';
	let key = ctrl_axes[index].id;
	let words = key.split('_');
	if (words[1] == 'normal' ||
	    words[1] == 'reverse') {
	    label = $('#select-axis-control #'+words[0]).text();
	    if (words[1] == 'reverse') {
		label += '(R';
	    }
	} else {
	    label = $('#select-axis-control #'+key).text();
	}
	$('#list-axes #'+index).next().text(label);
    };
    that.set_axis_label = set_axis_label;

    const default_control = function() {
	'use strict';
	if (spec.pad.axes.length > 0) {
	    ctrl_axes[0] = that.turn_normal;
	    set_axis_label(0);
	}
	if (spec.pad.axes.length > 1) {
	    ctrl_axes[1] = that.arm_normal;
	    set_axis_label(1);
	}
	if (spec.pad.axes.length > 2) {
	    ctrl_axes[2] = that.backet_normal;
	    set_axis_label(2);
	}
	if (spec.pad.axes.length > 3) {
	    ctrl_axes[3] = that.beam_normal;
	    set_axis_label(3);
	}
	if (spec.pad.axes.length > 4) {
	    ctrl_axes[4] = that.backetturn_normal;
	    set_axis_label(4);
	}
    };
    that.default_control = default_control;

    const set_connected = function(v) {
	'use strict';
	connect_flag = v;
	if (!v) {
	    expire_session();
	}
    };
    const get_connected = function() {
	'use strict';
	return connect_flag;
    };
    Object.defineProperty(that, "connected", {
	set: set_connected,
	get: get_connected, });

    const set_gamepadid = function(v) {
	'use strict';
	gamepadid = v;
    };
    const get_gamepadid = function() {
	'use strict';
	return gamepadid;
    };
    Object.defineProperty(that, "gamepad_id", {
	set: set_gamepadid,
	get: get_gamepadid, });

    const get_sessionid = function() {
	'use strict';
	return sessionid;
    };
    const set_sessionid = function(v) {
	'use strict';
	sessionid = v;
    };
    Object.defineProperty(that, "session_id", {
	set: set_sessionid,
	get: get_sessionid, });
    
    const set_ctrl_axes = function(i, func_name) {
	'use strict';
	if (func_name in that) {
	    if (ctrl_axes[i]) {
		delete ctrl_axes[i];
	    }
	    ctrl_axes[i] = that[func_name];
	} else {
	    console.log('maps['+i+'] not have ['+func_name+']');
	}
    };
    that.set_ctrl_axes = set_ctrl_axes;

    const set_ctrl_buttons = function(i, func_name) {
	'use strict';
	if (func_name in that) {
	    if (ctrl_buttons[i]) {
		delete ctrl_buttons[i];
	    }
	    ctrl_buttons[i] = that[func_name];
	} else {
	    console.log('maps['+i+'] not have ['+func_name+']');
	}
    };
    that.set_ctrl_buttons = set_ctrl_buttons;

    const ctrl_axis_id = function(i) {
	'use strict';
	let id = '';
	if (ctrl_axes[i]) {
	    id = ctrl_axes[i].id;
	}
	return id;
    };
    that.ctrl_axis_id = ctrl_axis_id;

    const ctrl_button_id = function(i) {
	'use strict';
	let id = ''
	if (ctrl_buttons[i]) {
	    id = ctrl_buttons[i].id;
	}
	return id;
    };
    that.ctrl_button_id = ctrl_button_id;

    const exec_axis = function(i) {
	'use strict';
	let flag = false;
	if (ctrl_axes[i]) {
	    let axis = spec.pad.axes[i];
	    if ((typeof last_pad.axes[i] == 'undefined') ||
		(last_pad.axes[i] != axis)) {
		ctrl_axes[i](axis);
		last_pad.axes[i] = axis;
		flag = true;
	    }
	}
	return flag;
    };
    that.exec_axis = exec_axis;

    const exec_axes = function() {
	'use strict';
	let is_change = false;
	for (let i=0;i < spec.pad.axes.length;i++ ) {
	    is_change |= exec_axis(i);
	}
	return is_change;
    }
    that.exec_axes = exec_axes

    const exec_button = function(i) {
	'use strict';
	let flag = false;
	if (ctrl_buttons[i]) {
	    let val = spec.pad.buttons[i];
	    if (typeof(val) == "object") {
		val = val.value;
	    }
	    if ((typeof last_pad.buttons[i] == 'undefined') ||
		(last_pad.buttons[i] != val)) {
		ctrl_buttons[i](val);
		last_pad.buttons[i] = val;
		flag = true;
	    }
	}
	return flag;
    };
    that.exec_button = exec_button;

    const exec_buttons = function() {
	'use strict';
	let is_change = false;
	for (let i=0;i < spec.pad.buttons.length;i++ ) {
	    is_change |= exec_button(i);
	}
	return is_change;
    }
    that.exec_buttons = exec_buttons;

    const exec = function() {
	'use strict';
	let is_change = false;
	is_change |= exec_axes();
	is_change |= exec_buttons();
	return is_change;
    }
    that.exec = exec;

    // ajax
    const expire_session = function() {
	'use strict';
	if (sessionid && AllowAjax) {
	    AllowAjax = false;
	    $.ajax({
		type:'get',
		url:'/gp/es',
		data : {
		    i : sessionid,
		},
		cache:false,
		timeout:1000,
	    }).done(function () {
		$('#com-status').text('セッション expire:done');
	    }).fail(function () {
		// 念の為に出すexpireリクエスト。
		// リクエストが失敗してもサーバ側で
		// 期限切れのセッションは適宜削除回収されるので特にエラーとはしない。
		$('#com-status').text('セッション expire:fail');
	    }).always(function () {
		sessionid = '';
		AllowAjax = true;
	    });
	}
    };
    that.expire_session = expire_session;

    const get_session_error = function (jqXHR, textStatus, errorThrown) {
	// get_session ajax error-handler
	'use strict';
	$('#com-status').text('セッション取得:error'+textStatus);
	AllowAjax = true;
    };

    const get_session = function() {
	'use strict';
	if (AllowAjax) {
	    AllowAjax = false;
	    $.ajax({
		type:'get',
		url:'/gp/gs',
		cache:false,
		timeout:1000,
		dataType:'text',
		error: get_session_error,
	    }).done(function (data) {
		$('#com-status').text('セッション取得:done');
		sessionid = data;
	    }).fail(function (data) {
		// 注意:sessionid取得失敗時はsend()は実行しない。
		$('#com-status').text('セッション取得:fail');
	    }).always(function () {
		AllowAjax = true;
		console.log(sessionid);
	    });
	}
    };
    that.get_session = get_session;
    
    const send_error = function(jqXHR, textStatus, errorThrown) {
	'use strict';
	$('#com-status').text('送信:error:'+textStatus);
	AllowAjax = true;
    };
    // send_error is private method no let to that.send_error
    
    const send =  function () {
	'use strict';
	// send data to server
	if (AllowAjax) {
	    AllowAjax = false;
	    $.ajax({
		type:'GET',
		url:'/gp/sd',
		cache:false,
		timeout:10000,
		data:{
		    't':data.turn,
		    'b':data.beam,
		    'a':data.arm,
		    'bk':data.backet,
		    'bt':data.backetturn,
		},
		//error:this.send_error,
	    }).done(function(data) {
		setTimeout(function() {
		    console.log(data);
		}, 1000);		
	    }).fail(function(data) {
		setTimeout(function() {
		    console.log(data);
		}, 1000);		
	    }).always(function() {
		AllowAjax = true;
	    });
	}
    };
    that.send = send;
   
    // set default control
    default_control();

    return that;
};

//event handlers
$(window).on('gamepadconnected gamepaddisconnected', list_gamepads);

$('#select-gamepad').on('click', '.list-group-item', function() {
    'use strict';
    TargetPad.index = this.id;
    TargetPad.id = $(this).text();
    $('#select-gamepad .list-group-item').each(function (i, e) {
	$(e).removeClass("active");
    });
    $(this).addClass("active");
    let pads = navigator.getGamepads ? navigator.getGamepads() :
	(navigator.webkitGetGamepads ? navigator.webkitGetGamepads : []);
    info_gamepad(pads[TargetPad.index]);
});

$('#axis-control-modal').on('show.bs.modal', function(e) {
    'use strict';
    let index = $(e.relatedTarget).data('index');
    let key = $(e.relatedTarget).data('key');
    $('#axis-control-modal .modal-content').attr('id', index);
    $('#axis-modal-label').text(key+' '+index);
    $('#select-axis-control .list-group-item').removeClass("active");
    $('#select-axis-normal-reverse .list-group-item').removeClass("active");
    let id = maps[TargetPad.index].ctrl_axis_id(index);
    if (id) {
	let term = id.split('_');
	if (term[0]) {
	    $('#select-axis-control #'+term[0]).addClass("active");
	} else {
	    $('#select-axis-control #none').addClass("active");
	}
	if (term[1]) {
	    $('#select-axis-normal-reverse #'+term[1]).addClass("active");
	} else {
	    $('#select-axis-normal-reverse #normal').addClass("active");
	}
    } else {
	$('#select-axis-control #none').addClass("active");
	$('#select-axis-normal-reverse #normal').addClass("active");
    }
});

$('#select-axis-control').on('click', '.list-group-item', function() {
    $('#select-axis-control .list-group-item').removeClass("active");
    $(this).addClass("active");
});

$('#select-axis-normal-reverse').on('click', '.list-group-item', function() {
    $('#select-axis-normal-reverse .list-group-item').removeClass("active");
    $(this).addClass("active");
});

$('#axis-control-modal-ok').on('click', function() {
    let index = $('#axis-control-modal .modal-content').attr('id');
    let active = $('#select-axis-control .active');
    let key = active.attr('id');
    let nr = $('#select-axis-normal-reverse .active').attr('id');
    if (key != 'none') {
	key += '_' + nr;
    }
    let nr_mark = '';
    if (nr == 'reverse') {
	nr_mark = '(R';
    }
    $('#list-axes #'+index).next().text(active.text()+nr_mark);
    maps[TargetPad.index].set_ctrl_axes(index, key);
    $('#axis-control-modal').modal('hide');
});

$('#button-control-modal').on('show.bs.modal', function(e) {
    'use strict';
    let index = $(e.relatedTarget).data('index');
    let key = $(e.relatedTarget).data('key');
    $('#button-control-modal .modal-content').attr('id', index);
    $('#button-modal-label').text(key+' '+index);
    $('#select-button-control .list-group-item').removeClass("active");
    let id = maps[TargetPad.index].ctrl_button_id(index);
    if(id) {
	$('#select-button-control #'+id).addClass("active");
    } else {
	$('#select-button-control #none').addClass("active");
    }
});

$('#select-button-control').on('click', '.list-group-item', function() {
    $('#select-button-control .list-group-item').removeClass("active");
    $(this).addClass("active");
});

$('#button-control-modal-ok').on('click', function() {
    let index = $('#button-control-modal .modal-content').attr('id');
    let active = $('#select-button-control .active');
    let key = active.attr('id');
    $('#list-buttons #'+index).next().text(active.text());
    maps[TargetPad.index].set_ctrl_buttons(index, key);
    $('#button-control-modal').modal('hide');
});


function list_gamepads() {
    'use strict';
    let pads = navigator.getGamepads ? navigator.getGamepads() :
	(navigator.webkitGetGamepads ? navigator.webkitGetGamepads : []);
    if (pads) {
	let id_list_html = '';
	for(let i=0; i<pads.length; i++){
	    if (pads[i] && pads[i].connected) {
		if (TargetPad.index == i &&
		    TargetPad.id == pads[i].id) {
		    id_list_html += '<a id="'+i+'" class="list-group-item active">'+pads[i].id+'</a>';
		} else {
		    id_list_html += '<a id="'+i+'" class="list-group-item">'+pads[i].id+'</a>';
		}
	    } else {
		id_list_html += '<a id="'+i+'" class="list-group-item disabled"></a>';
		if ( i == TargetPad.index) {
		    maps[TargetPad.index].connected = false;
		    TargetPad.index = -1;
		    TargetPad.id = '';
		    Map.gamepad_id = '';
		    info_gamepad(null);
		}
	    }
	}
	$("#select-gamepad").html(id_list_html);
    }
}

function info_gamepad(pad) {
    'use strict';
    let info_html = '';
    if (pad) {
	info_html += '<ul class="list-inline" id="list-axes">';
	for (let i=0;i<pad.axes.length;i++) {
	    info_html += '<li>';
	    info_html += '<span class="label label-primary gamepad-axis" data-toggle="modal" data-target="#axis-control-modal" data-index="'+i+'" data-key="axis">AXIS '+i+'</span>';
	    info_html += '<span class="label label-default gamepad-axis" id="'+i+'"  data-toggle="modal" data-target="#axis-control-modal" data-index="'+i+'" data-key="axis">'+pad.axes[i].toFixed(DECIMAL_WIDTH)+'</span>';
	    info_html += '<span class="label label-success gamepad-axis"  data-toggle="modal" data-target="#axis-control-modal" data-index="'+i+'" data-key="AXIS">(割付無)</span>';
	    info_html += '</li>';
	}
	info_html += '</ul>';
	
	info_html += '<ul class="list-inline" id="list-buttons">';
	for(let i=0;i<pad.buttons.length;i++) {
	    let val = pad.buttons[i];
	    let pressed = (val == 1.0);
	    if (typeof(val) == "object") {
		pressed = val.pressed;
		val = val.value;
	    }
	    info_html += '<li>';
	    info_html += '<span class="label label-primary gamepad-button" data-toggle="modal" data-target="#button-control-modal" data-index="'+i+'" data-key="button">BUTTON '+i+'</span>';
	    info_html += '<span class="label label-default gamepad-button" id="'+i+'" data-toggle="modal" data-target="#button-control-modal" data-index="'+i+'" data-key="button">'+val+'</span>';
	    info_html += '<span class="label label-success gamepad-button" data-toggle="modal" data-target="#button-control-modal" data-index="'+i+'" data-key="button">(割付無)</span>';
	    info_html += '</li>';
	    }
	info_html += '</ul>';
    }
    let last_info_html = $("#gamepad-info").html();
    if (info_html != last_info_html) {
	$("#gamepad-info").html(info_html);
    }
}

function update_gamepad(pad) {
    'use strict';
    if (pad) {
	for (let i=0;i<pad.axes.length;i++) {
	    let axis = $('#list-axes #'+i);
	    if (axis.length) {
		let axis_last = axis.text();
		let axis_now = pad.axes[i].toFixed(DECIMAL_WIDTH);
		if (axis_last != axis_now ) {
		    axis.text(axis_now);
		}
	    }
	}
	for(let i=0;i<pad.buttons.length;i++) {
	    let val = pad.buttons[i];
	    let pressed = (val == 1.0);
	    if (typeof(val) == "object") {
		pressed = val.pressed;
		val = val.value;
	    }
	    let buttons = $('#list-buttons #'+i);
	    if (buttons.length) {
		let buttons_last = buttons.text();
		if (buttons_last != val) {
		    buttons.text(val);
		}
	    }
	}
    }
}

function update_control_list(selector) {
    if (selector) {
	if (!selector.hasClass("active")) {
	    selector.addClass("active");
	}
	selector.siblings().removeClass("active");
    }
}

//Update loop
function scanGamepads() {
    'use strict';
    let pads = navigator.getGamepads ? navigator.getGamepads() :
	(navigator.webkitGetGamepads ? navigator.webkitGetGamepads : []);
    if (!pads) {
	$("#select-gamepad").html('');
	$("#gamepad-info").html('');
	rAF(scanGamepads);
	return;
    }

    if (TargetPad.index > -1) {
	let pad = pads[TargetPad.index];
	update_gamepad(pad);
	if (maps[TargetPad.index]) {
	    let map = maps[TargetPad.index];
	    if (map.connected) {
		if (map.exec()) {
		    if (map.session_id) {
			map.send();	// if need, send control data to server.
		    } else {
			console.log('no session id; no send');
		    }
		}
	    } else {
		console.log('map.gamepad_id['+map.gamepad_id+'], pad.id['+pad.id+']');
		if (map.gamepad_id != pad.id) {
		    map.expire_session();
		    delete maps[TargetPad.index];
		    maps[TargetPad.index] = construct_map({pad:pad});
		    map = maps[TargetPad.index];
		} else {
		    // gamepad_id == pad.id then reuse this.
		    map.connected = true;
		}
		map.get_session();
	    }
	} else {
	    maps[TargetPad.index] = construct_map({pad:pad});
	    maps[TargetPad.index].get_session();
	}
    } else {
	info_gamepad(null);
    }
    
    rAF(scanGamepads);
}

//Start
rAF(scanGamepads);
