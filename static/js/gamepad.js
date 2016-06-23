// ref: http://qiita.com/gyabo/items/baae116e9e4c53ca17ab

//---------------------------------------------------------------------
//  ref:https://developer.mozilla.org/en-US/docs/Web/Guide/API/Gamepad
//---------------------------------------------------------------------

var StrSelectGamepad = '<p>PCにゲームパッド(ジョイスティック)を接続して下さい。アナログスティックを操作するかボタンを押すと認識します。</p>'
var StrGamepadInfo = '';
var TargetPad = -1;

var Map = {
    'axes' : [],
    'buttons' : [],
    'ctrls_old' : {
	turn: 0.0,
	beam: 0.0,
	backet: 0.0,
	turn_backet : 0.0
    },
    'ctrls' : {
	turn: 0.0,
	beam: 0.0,
	backet: 0.0,
	turn_backet : 0.0
    },
    
    'set_turn' : function(value) {
	this.ctrls.turn = value;
    },
    
    'set_beam' : function(value) {
	this.ctrls.beam = value;
    },
    
    'set_backet' : function(value) {
	this.ctrls.backet = value;
    },
    
    'set_trun_backet' : function(value) {
	this.ctrl.trun_backet = value;
    },
    
    'send' : function() {
	this.ctrls_old.turn = this.ctrls.turn;
	this.ctrls_old.beam = this.ctrls.beam;
	this.ctrls_old.backet = this.ctrls.backet;
	this.ctrls_old.turn_backete = this.ctrls.turn_backet;
    },
};

$('#select-gamepad').on('click', '.list-group-item', function(e) {
    TargetPad = this.id;
});
		   
//code here
function list_gamepad(pads) {
    var last_id_list_html = $("#select-gamepad").html();
    var id_list_html = StrSelectGamepad;
    id_list_html = '';
    for(var i=0; i<pads.length; i++){
	if (pads[i]) {
	    if (i == TargetPad) {
		id_list_html += '<li id="'+i+'" class="list-group-item active">';
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
    var info_html = StrGamepadInfo;
    if (pad) {
	info_html += '<ul class="list-inline">';
	for (i=0;i<pad.axes.length;i++) {
	    info_html += '<li>';
	    info_html += '<span class="label label-primary">AXIS '+i+'</span>';
	    info_html += '<span class="label label-default">'+pad.axes[i].toFixed(5)+'</span>';
	    info_html += '</li>';
	}
	info_html += '</ul>';
	
	info_html += '<ul class="list-inline">';
	for(i=0;i<pad.buttons.length;i++) {
	    var val = pad.buttons[i];
	    var pressed = (val == 1.0);
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
    var last_info_html = $("#gamepad-info").html();
    if (info_html != last_info_html) {
	$("#gamepad-info").html(info_html);
    }
}


//Create AnimationFrame
var rAF = window.mozRequestAnimationFrame ||
    window.webkitRequestAnimationFrame ||
    window.requestAnimationFrame;

//Update
function scanGamepads() {
    var pads = navigator.getGamepads ? navigator.getGamepads() :
        (navigator.webkitGetGamepads ? navigator.webkitGetGamepads : []);

    if (!pads) {
	$("#select-gamepad").html(StrSelectGamepad);
	$("#gamepad-info").html(StrGamepadInfo);
	rAF(scanGamepads);
	return;
    }

    list_gamepad(pads);
    info_gamepad(pads[TargetPad]);

    // attach function
    
    rAF(scanGamepads);
}

//Start
rAF(scanGamepads);
