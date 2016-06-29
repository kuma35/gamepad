'use strict';
// ref: http://qiita.com/gyabo/items/baae116e9e4c53ca17ab

//---------------------------------------------------------------------
//  ref:https://developer.mozilla.org/en-US/docs/Web/Guide/API/Gamepad
//---------------------------------------------------------------------

// JavaScript: The good parts
// (Polyfill)P.26 3.5 プロトタイプ 参照
// browser support: MDN Object.create()
// https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Object/create
//if (typeof Object.create != 'function') {
//    Object.create = function (o) {
//	'use strict';
//	let F = function () {};
//	F.prototype = o;
//	return new F();
//    }
//}

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

const StrSelectGamepad = '<p>PCにゲームパッド(ジョイスティック)を接続して下さい。アナログスティックを操作するかボタンを押すと認識します。</p>'
let StrGamepadInfo = '';
let TargetPad = -1;
let FocusPad = -1;
let ArrowAjax = true;
let Maps = [];

$('#select-gamepad').on('click', '.list-group-item', function(e) {
    TargetPad = this.id;
});

//$('.list-group-item').focusin( function(e) {FocusPad = this.id;})
//    .focusout( function(e) {FocusPad = -1;});

function create_maps(maps, pads) {
    'use strict';
    for (let i = 0; i < pads.length; i++) {
	maps[i] = Object.create(pads[i]);
	maps[i].session_id = '';	// get session id from server.
	maps[i].axes_func = new Array(pads[i].axes.length);
	maps[i].buttons_func = new Array(pads[i].buttons.length);
	maps[i].controls = {
	    turn: 0.0,
	    beam: 0.0,
	    arm: 0.0,
	    backet: 0.0,
	    turn_backet: 0.0,
	};
	maps[i].controls_old = {
	    turn: 0.0,
	    beam: 0.0,
	    arm: 0.0,
	    backet: 0.0,
	    turn_backet: 0.0,
	};
	maps[i].set_turn = function(value) {
	    'use strict';
	    this.controls.turn = value;
	};
	maps[i].set_beam = function(value) {
	    'use strict';
	    this.controls.beam = value;
	};
	maps[i].set_arm = function(value) {
	    'use strict';
	    this.controls.arm = value;
	};
	maps[i].set_backet = function(value) {
	    'use strict';
	    this.controls.backet = value;
	};
	maps[i].set_turn_backet = function(value) {
	    'use strict';
	    this.controls.turn_backet = value;
	};
	maps[i].send = function () {
	    'use strict';
	    if (this.controls_old.turn !== this.controlsturn ||
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
	};
    } // for
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
function list_gamepad(pads) {
    'use strict';
    let last_id_list_html = $("#select-gamepad").html();
    let id_list_html = StrSelectGamepad;
    id_list_html = '';
    for(let i=0; i<pads.length; i++){
	if (pads[i]) {
	    if (i == TargetPad) {
		id_list_html += '<li id="'+i+'" class="list-group-item active">';
//	    } else if (i == FocusPad) {
//		id_list_html += '<li id="'+i+'" class="list-group-item list-group-item-success">';
	    } else {
		id_list_html += '<li id="'+i+'" class="list-group-item">';
	    }
	    id_list_html += pads[i].id;
	    id_list_html += '</li>';
	}
    }
    if (id_list_html != last_id_list_html) {
	$("#select-gamepad").html(id_list_html);
    }
}

function info_gamepad(pad) {
    'use strict';
    let info_html = StrGamepadInfo;
    if (pad) {
	info_html += '<ul class="list-inline">';
	for (let i=0;i<pad.axes.length;i++) {
	    info_html += '<li>';
	    info_html += '<span class="label label-primary">AXIS '+i+'</span>';
	    info_html += '<span class="label label-default">'+pad.axes[i].toFixed(5)+'</span>';
	    info_html += '</li>';
	}
	info_html += '</ul>';
	
	info_html += '<ul class="list-inline">';
	for(let i=0;i<pad.buttons.length;i++) {
	    let val = pad.buttons[i];
	    let pressed = (val == 1.0);
	    if (typeof(val) == "object") {
		pressed = val.pressed;
		val = val.value;
	    }
	    info_html += '<li>';
	    info_html += '<span class="label label-primary">BUTTON '+i+'</span>';
	    info_html += '<span class="label label-default">'+val+'</span>';
	    info_html += '</li>';
	    }
	info_html += '</ul>';
    }
    let last_info_html = $("#gamepad-info").html();
    if (info_html != last_info_html) {
	$("#gamepad-info").html(info_html);
    }
}


//Create AnimationFrame
const rAF = window.mozRequestAnimationFrame ||
      window.webkitRequestAnimationFrame ||
      window.requestAnimationFrame;

//Update
function scanGamepads() {
    'use strict';
    let pads = navigator.getGamepads ? navigator.getGamepads() :
        (navigator.webkitGetGamepads ? navigator.webkitGetGamepads : []);

    if (!pads) {
	$("#select-gamepad").html(StrSelectGamepad);
	$("#gamepad-info").html(StrGamepadInfo);
	rAF(scanGamepads);
	return;
    }

    list_gamepad(pads);
    if (TargetPad > -1) {
	info_gamepad(pads[TargetPad]);
    }

    //if (!Maps) {
//	create_maps(Maps, pads);
//	// attach default function by gamepad-id or generic.
//    } else if (TargetPad >=0 ){
//	Maps && Maps[TargetPad].send();	// if need, send control data to server.
//    } else {
//    }
   
    rAF(scanGamepads);
}

//Start
rAF(scanGamepads);
