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
let ArrowAjax = true;
const rAF = window.mozRequestAnimationFrame ||
      window.webkitRequestAnimationFrame ||
      window.requestAnimationFrame;
let Map = {
    'gamepad_id': '',
    'session_id': '',	// get session id from server.
    'controls' : {
	turn: 0.0,
	beam: 0.0,
	arm: 0.0,
	backet: 0.0,
	turn_backet: 0.0,
    },
    'controls_old' : {
	turn: 0.0,
	beam: 0.0,
	arm: 0.0,
	backet: 0.0,
	turn_backet: 0.0,
    },
    'set_turn' : function(value) {
	'use strict';
	this.controls.turn = value;
    },
    'set_beam' : function(value) {
	'use strict';
	this.controls.beam = value;
    },
    'set_arm' : function(value) {
	'use strict';
	this.controls.arm = value;
    },
    'set_backet' : function(value) {
	'use strict';
	this.controls.backet = value;
    },
    'set_turn_backet' : function(value) {
	'use strict';
	this.controls.turn_backet = value;
    },
    'send' : function () {
	'use strict';
	if (this.controls_old.turn !== this.controls.turn ||
	    this.controls_old.beam !== this.controls.beam ||
	    this.controls_old.arm !== this.controls.arm ||
	    this.controls_old.backet !== this.controls.backet ||
	    this.controls_old.turn_backet !== this.controls.turn_backet) {
	    // send data to server
	    if (AllowAjax) {
		$.ajax().done().fail();
	    }
	    // update controls_old
	    this.controls_old.turn = this.controlsturn;
	    this.controls_old.beam = this.controls.beam;
	    this.controls_old.arm = this.controls.arm;
	    this.controls_old.backet = this.controls.backet;
	    this.controls_old.turn_backet = this.controls.turn_backet;
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
$('#gamepad-info').on('click', '.gamepad-axis', function() {
    $('#axis-control-modal').modal();
});
$('#gamepad-info').on('click', '.gamepad-button', function() {
    $('#button-control-modal').modal();
});


function create_map(map, pad) {
    'use strict';
    map.prototype = pad;
    map.gamepad_id = map.prototype.id;
    //map.gamepad_id = pad.id;
    map.axes_func = new Array(pad.axes.length);
    map.buttons_func = new Array(pad.buttons.length);
}

function default_generic_pad(map) {
    'use strict';
    if (map.axes.length > 4) {
	map.axes_func[0] = map.turn;
	map.axes_func[1] = map.beam;
	map.axes_func[2] = map.arm;
	map.axes_func[3] = map.backet;
    }
    if (map.axes.length > 5) {
	map.axes_func[4] = map.turn_backet;
    }
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
	    info_html += '<span class="label label-primary gamepad-axis">AXIS '+i+'</span>';
	    info_html += '<span class="label label-default gamepad-axis" id="'+i+'">'+pad.axes[i].toFixed(5)+'</span>';
	    info_html += '<span class="label label-success gamepad-axis gamepad-axis-ctrl">(割付無)</span>';
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
	    info_html += '<span class="label label-primary gamepad-button">BUTTON '+i+'</span>';
	    info_html += '<span class="label label-default gamepad-button" id="'+i+'">'+val+'</span>';
	    info_html += '<span class="label label-success gamepad-button gamepad-button-ctrl">(割付無)</span>';
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
	update_gamepad(pads[TargetPad.index]);
	if (Map.gamepad_id != '') {
	    Map && Map.send();	// if need, send control data to server.
	} else {
	    create_map(Map, pads[TargetPad.index]);
	    //console.log(Map);
	}
    } else {
	info_gamepad(null);
    }
    
    rAF(scanGamepads);
}

//Start
rAF(scanGamepads);
