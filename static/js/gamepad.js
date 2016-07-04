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
let AllowAjax = false;
const rAF = window.mozRequestAnimationFrame ||
      window.webkitRequestAnimationFrame ||
      window.requestAnimationFrame;
let Map = {
    'gamepad_id': '',
    'session_id': '',	// get session id from server.
    'ctrl' : {
	'axis' : [],
	'btn' : [],
    },
    'data' : {
	turn: 0.0,
	beam: 0.0,
	arm: 0.0,
	backet: 0.0,
	backet_turn: 0.0,
    },
    'none' : function(direction, value) {
	'use strict';
	// nothing
    },
    'turn' : function(direction, value) {
	'use strict';
	this.data.turn = value * direction;
    },
    'beam' : function(direction, value) {
	'use strict';
	this.data.beam = value * direction;
    },
    'arm' : function(dirction, value) {
	'use strict';
	this.data.arm = value * direction;
    },
    'backet' : function(direction, value) {
	'use strict';
	this.data.backet = value * direction;
    },
    'backet_turn' : function(direction, value) {
	'use strict';
	this.data.backet_trun = value * direction;
    },
    // execute
    'send' : function () {
	'use strict';
	// send data to server
	if (AllowAjax) {
	    $.ajax().done().fail();
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
    if( Map.ctrl.axis[index]) {
	let term = Map.ctrl.axis[index].name.split('-');
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
    //$('#select-axis-control #'+Map.ctrl.axis[index].name).addClass("active");
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
    Map.ctrl.axis[index] = Map[key];
    $('#axis-control-modal').modal('hide');
});
$('#button-control-modal').on('show.bs.modal', function(e) {
    'use strict';
    let index = $(e.relatedTarget).data('index');
    let key = $(e.relatedTarget).data('key');
    $('#button-control-modal .modal-content').attr('id', index);
    $('#button-modal-label').text(key+' '+index);
    $('#select-button-control .list-group-item').removeClass("active");
    if( Map.ctrl.btn[index]) {
	if (Map.ctrl.btn[index].name) {
	    $('#select-button-control #'+Map.ctrl.btn[index].name).addClass("active");
	} else {
	    $('#select-button-control #none').addClass("active");
	}
    } else {
	$('#select-button-control #none').addClass("active");
    }
    //$('#select-axis-control #'+Map.ctrl.axis[index].name).addClass("active");
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
    Map.ctrl.btn[index] = Map[key];
    $('#button-control-modal').modal('hide');
});

function create_map(map, pad) {
    'use strict';
    map.prototype = pad;
    map.gamepad_id = map.prototype.id;

    // make controls functions
    // axis(axis-value) ; only one argument.
    // button() ; no argument. only call function.
    map.turn_normal = {
	'name' : 'turn-normal',
	'func' : map.turn.curry(1.0),
    };
    map.turn_reverse = {
	'name' :'turn-reverse',
	'func' : map.turn.curry(-1.0),
    };
    map.turn_left = {
	'name' : 'turn-left',
	'func' : map.turn.curry(1.0, -1.0),
    };
    map.turn_right = {
	'name' : 'turn-right',
	'func' : map.turn.curry(1.0, 1.0),
    };
    map.beam_normal = {
	'name' : 'beam-normal',
	'func' : map.beam.curry(1.0),
    };
    map.beam_reverse = {
	'name' : 'beam-reverse',
	'func' : map.beam.curry(-1.0),
    };
    map.beam_down = {
	'name' : 'beam-down',
	'func' : map.beam.curry(1.0, -1.0),
    };
    map.beam_up = {
	'name' : 'beam-up',
	'func' : map.beam.curry(1.0, 1.0),
    };
    map.arm_normal = {
	'name' : 'arm-normal',
	'func' : map.arm.curry(1.0),
    };
    map.arm_reverse = {
	'name' : 'arm-reverse',
	'func' : map.arm.curry(-1.0),
    };
    map.arm_fold = {
	'name' : 'arm-fold',
	'func' : map.arm.curry(1.0, -1.0),
    };
    map.arm_extend = {
	'name' : 'arm-extend',
	'func' : map.arm.curry(1.0, 1.0),
    };
    map.backet_normal = {
	'name' : 'backet-normal',
	'func' : map.backet.curry(1.0),
    };
    map.backet_reverse = {
	'name' : 'backet-reverse',
	'func' : map.backet.curry(-1.0),
    };
    map.backet_fold = {
	'name' : 'backet-fold',
	'func' : map.backet.curry(1.0, -1.0),
    };
    map.backet_extend = {
	'name' : 'backet-extend',
	'func' : map.backet.curry(1.0, 1.0),
    };
    map.backetturn_normal = {
	'name' : 'backetturn-normal',
	'func' : map.backet_turn.curry(1.0),
    };
    map.backetturn_reverse = {
	'name' : 'backetturn-reverse',
	'func' : map.backet_turn.curry(-1.0),
    };
    map.backetturn_left = {
	'name' : 'backetturn-left',
	'func' : map.backet_turn.curry(1.0, -1.0),
    };
    map.backetturn_right = {
	'name' : 'backetturn-right',
	'func' : map.backet_turn.curry(1.0, 1.0),
    };

}

function generic_mapping(map, pad) {
    // set default control
    if (pad.axes.length > 0) {
	map.ctrl.axis[0] = map.turn_normal;
	set_axis_label(0);
    }
    if (pad.axes.length > 1) {
	map.ctrl.axis[1] = map.arm_normal;
	set_axis_label(1);
    }
    if (pad.axes.length > 2) {
	map.ctrl.axis[2] = map.backet_normal;
	set_axis_label(2);
    }
    if (pad.axes.length > 3) {
	map.ctrl.axis[3] = map.beam_normal;
	set_axis_label(3);
    }
    if (pad.axes.length > 4) {
	map.ctrl.axis[4] = map.backetturn_normal;
	set_axis_label(4);
    }
}

function set_axis_label(index) {
    'use strict';
    let label = '';
    let key = Map.ctrl.axis[index].name;
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
	    info_html += '<span class="label label-default gamepad-axis" id="'+i+'"  data-toggle="modal" data-target="#axis-control-modal" data-index="'+i+'" data-key="axis">'+pad.axes[i].toFixed(5)+'</span>';
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
		let axis_now = pad.axes[i].toFixed(5);
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
	    for (let i=0;i < Map.ctrl.axis.length;i++ ) {
		if (Map.ctrl.axis && Map.ctrl.axis.func) {
		    Map.ctrl.axis.func(pad.axis[i]);
		}
	    }
	    for (let i=0;i < Map.ctrl.btn.length;i++) {
		if (Map.ctrl.btn && Map.ctrl.btn.func) {
		    let val = pad.buttons[i];
		    let pressed = (val == 1.0);
		    if (typeof(val) == "object") {
			pressed = val.pressed;
			val = val.value;
		    }
		    Map.ctrl.btn.func(val);
		}
	    }
	    Map && Map.send();	// if need, send control data to server.
	} else {
	    create_map(Map, pads[TargetPad.index]);
	    //console.log(Map);
	    generic_mapping(Map, pads[TargetPad.index]);
	}
    } else {
	info_gamepad(null);
    }
    
    rAF(scanGamepads);
}

//Start
rAF(scanGamepads);
