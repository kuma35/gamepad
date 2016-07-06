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

let TargetPad = {
    'index': -1,
    'id':'',
};
let AllowAjax = true;
const rAF = window.mozRequestAnimationFrame ||
      window.webkitRequestAnimationFrame ||
      window.requestAnimationFrame;
// map
let Map = {
    'gamepad_id': '',
    'session_id': '',	// get session id from server.
    'ctrl_axis' : [],
    'ctrl_btn' : [],
    'last_data': {
	'turn': 0.1,
	'beam': 0.1,
	'arm': 0.1,
	'backet': 0.1,
	'backetturn': 0.1,
    },
    'data' : {
	'turn': 0.0,
	'beam': 0.0,
	'arm': 0.0,
	'backet': 0.0,
	'backetturn': 0.0,
    },
    'none' : function(that, v) {
	'use strict';
	;// nothing
    },
    'turn_normal' : function(that, v) {
	'use strict';
	that.data.turn = v;
    },
    'turn_reverse' : function(that, v) {
	'use strict';
	that.data.turn = v * -1;
    },
    'turn_left' : function(that, v) {
	'use strict';
	that.data.turn = -1;
    },
    'turn_right' : function(that, v) {
	'use strict';
	that.data.turn = 1;
    },
    'beam_normal' : function(that, v) {
	'use strict';
	that.data.beam = v;
    },
    'beam_reverse' : function(that, v) {
	'use strict';
	that.data.beam = v * -1;
    },
    'beam_down' : function(that, v) {
	'use strict';
	that.data.beam = -1;
    },
    'beam_up' : function(that, v) {
	'use strict';
	that.data.beam = 1;
    },
    'arm_normal' : function(that, v) {
	'use strict';
	that.data.arm = v;
    },
    'arm_reverse' : function(that, v) {
	'use strict';
	that.data.arm = v * -1;
    },
    'arm_fold' : function(that, v) {
	'use strict';
	that.data.arm = -1;
    },
    'arm_extend' : function(that, v) {
	'use strict';
	that.data.arm = 1;
    },
    'backet_normal' : function(that, v) {
	'use strict';
	that.data.backet = v;
    },
    'backet_reverse' : function(that, v) {
	'use strict';
	that.data.backet = v * -1;
    },
    'backet_down' : function(that, v) {
	'use strict';
	that.data.backet = -1;
    },
    'backet_up' : function(that, v) {
	'use strict';
	that.data.backet = 1;
    },
    'backetturn_normal' : function(that, v) {
	'use strict';
	that.data.backetturn = v;
    },
    'backetturn_reverse' : function(that, v) {
	'use strict';
	that.data.backetturn = v * -1;
    },
    'backetturn_left' : function(that, v) {
	'use strict';
	that.data.backetturn = -1;
    },
    'backetturn_right' : function(that, v) {
	'use strict';
	that.data.backetturn = 1;
    },
    // ajax
    'send_error': function(jqXHR, textStatus, errorThrown) {
	$('#com-status').text('送信:error:'+textStatus);
	AllowAjax = true;
    },
    'is_change': function() {
	if (this.last_data.turn == this.data.turn &&
	    this.last_data.beam == this.data.beam &&
	    this.last_data.arm == this.data.arm &&
	    this.last_data.backet == this.data.backet &&
	    this.last_data.backetturn == this.data.backetturn) {
	    // no change
	    return false;
	} else {
	    // check data update
	    this.last_data.turn = this.data.turn;
	    this.last_data.beam = this.data.beam;
	    this.last_data.arm = this.data.arm;
	    this.last_data.backet = this.data.backet;
	    this.last_data.backetturn = this.data.backetturn;
	    return true;
	}
    },
    'send' : function () {
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
		    't':this.data.turn.toFixed(2),
		    'b':this.data.beam.toFixed(2),
		    'a':this.data.arm.toFixed(2),
		    'bk':this.data.backet.toFixed(2),
		    'bt':this.data.backetturn.toFixed(2),
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
    },
};

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
    if( Map.ctrl_axis[index]) {
	let term = Map.ctrl_axis[index].id.split('-');
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
    //$('#select-axis-control #'+Map.ctrl_axis[index].id).addClass("active");
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
    Map.ctrl_axis[index] = Map[key];
    $('#axis-control-modal').modal('hide');
});
$('#button-control-modal').on('show.bs.modal', function(e) {
    'use strict';
    let index = $(e.relatedTarget).data('index');
    let key = $(e.relatedTarget).data('key');
    $('#button-control-modal .modal-content').attr('id', index);
    $('#button-modal-label').text(key+' '+index);
    $('#select-button-control .list-group-item').removeClass("active");
    if( Map.ctrl_btn[index]) {
	if (Map.ctrl_btn[index].id) {
	    $('#select-button-control #'+Map.ctrl_btn[index].id).addClass("active");
	} else {
	    $('#select-button-control #none').addClass("active");
	}
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
    Map.ctrl_btn[index] = Map[key];
    $('#button-control-modal').modal('hide');
});

function create_map(map, pad) {
    'use strict';
    map.prototype = pad;
    map.gamepad_id = map.prototype.id;
    map.turn_normal.id = 'turn-normal';
    map.turn_reverse.id = 'turn-reverse';
    map.turn_left.id = 'turn-left';
    map.turn_right.id = 'turn-right';
    map.beam_normal.id = 'beam-normal';
    map.beam_reverse.id = 'beam-reverse';
    map.beam_up.id = 'beam-up';
    map.beam_down.id = 'beam-down';
    map.arm_normal.id = 'arm-normal';
    map.arm_reverse.id = 'arm-reverse';
    map.arm_fold = 'arm-fold';
    map.arm_extend = 'arm-extend';
    map.backet_normal.id = 'backet-normal';
    map.backet_reverse.id = 'backet-reverse';
    map.backet_up.id = 'backet-up';
    map.backet_down.id = 'backet-down';
    map.backetturn_normal.id = 'backetturn-normal';
    map.backetturn_reverse.id = 'backetturn-reverse';
    map.backetturn_left.id = 'backetturn-left';
    map.backetturn_right.id = 'backetturn-right';
}

function generic_mapping(map, pad) {
    // set default control
    if (pad.axes.length > 0) {
	map.ctrl_axis[0] = map.turn_normal;
	set_axis_label(0);
    }
    if (pad.axes.length > 1) {
	map.ctrl_axis[1] = map.arm_normal;
	set_axis_label(1);
    }
    if (pad.axes.length > 2) {
	map.ctrl_axis[2] = map.backet_normal;
	set_axis_label(2);
    }
    if (pad.axes.length > 3) {
	map.ctrl_axis[3] = map.beam_normal;
	set_axis_label(3);
    }
    if (pad.axes.length > 4) {
	map.ctrl_axis[4] = map.backetturn_normal;
	set_axis_label(4);
    }
}

function get_session_error(jqXHR, textStatus, errorThrown) {
    $('#com-status').text('セッション取得:error'+textStatus);
    AllowAjax = true;
}

function get_session() {
    if (AllowAjax) {
	AllowAjax = false;
	$.ajax({
	    type:'get',
	    url:'/gp/gs',
	    cache:false,
	    timeout:1000,
	    dataType:'text',
	    //error: get_session_error,
	}).done(function (data) {
	    $('#com-status').text('セッション取得:done');
	    Map.session_id = data;
	}).fail(function (data) {
	    $('#com-status').text('セッション取得:fail');
	}).always(function () {
	    AllowAjax = true;
	    console.log(Map.session_id);
	});
    }
}

function set_axis_label(index) {
    'use strict';
    let label = '';
    let key = Map.ctrl_axis[index].id;
    console.log(Map.ctrl_axis[index].id);
    let words = key.split('-');
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
}

//code here
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
	    info_html += '<span class="label label-default gamepad-axis" id="'+i+'"  data-toggle="modal" data-target="#axis-control-modal" data-index="'+i+'" data-key="axis">'+pad.axes[i].toFixed(2)+'</span>';
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
		let axis_now = pad.axes[i].toFixed(2);
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

//Create AnimationFrame

//Update
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
	if (Map.gamepad_id != '') {
	    for (let i=0;i < pad.axes.length;i++ ) {
		if (Map.ctrl_axis[i]) {
		    Map.ctrl_axis[i](Map, pad.axes[i]);
		}
	    }
	    for (let i=0;i < pad.buttons.length;i++) {
		if (Map.ctrl_btn[i]) {
		    let val = pad.buttons[i];
		    let pressed = (val == 1.0);
		    if (typeof(val) == "object") {
			pressed = val.pressed;
			val = val.value;
		    }
		    Map.ctrl_btn[i](Map, val);
		}
	    }
	    if (Map.is_change()) {
		console.log('data');
		console.log(Map.data);
		console.log('last_data');
		console.log(Map.last_data);
		Map && Map.send();	// if need, send control data to server.
	    }
	} else {
	    create_map(Map, pads[TargetPad.index]);
	    //console.log(Map);
	    generic_mapping(Map, pads[TargetPad.index]);
	    get_session();
	}
    } else {
	info_gamepad(null);
    }
    
    rAF(scanGamepads);
}

//Start
rAF(scanGamepads);
