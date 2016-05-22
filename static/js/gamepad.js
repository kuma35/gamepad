// ref: http://qiita.com/gyabo/items/baae116e9e4c53ca17ab

//---------------------------------------------------------------------
//  ref:https://developer.mozilla.org/en-US/docs/Web/Guide/API/Gamepad
//---------------------------------------------------------------------

//Create AnimationFrame
var rAF = window.mozRequestAnimationFrame ||
    window.webkitRequestAnimationFrame ||
    window.requestAnimationFrame;

//Update
function scanGamepads() {
    var pads = navigator.getGamepads ? navigator.getGamepads() :
                   (navigator.webkitGetGamepads ? navigator.webkitGetGamepads : []);

    //gamepad id list
    var last_id_list_html = $("#select-gamepad").html();
    var id_list_html = '';

    if (pads[0]) {
	id_list_html += '<li class="list-group-item active">';
	id_list_html += pads[0].id;
	    id_list_html += '</li>';
    }
    for(var i=1; i<pads.length; i++){
	if (pads[i]) {
	    id_list_html += '<li class="list-group-item">';
	    id_list_html += pads[i].id;
	    id_list_html += '</li>';
	}
    }
    if (id_list_html != last_id_list_html) {
	$("#select-gamepad").html(id_list_html);
    }

    // id 0's info :-)
    var target = 0;
    if (pads[target]) {
	var info_html = '';
	info_html += '<ul class="list-inline">';
	for (i=0;i<pads[target].axes.length;i++) {
	    info_html += '<li>';
	    info_html += '<span class="label label-primary">AXIS '+i+'</span>';
	    info_html += '<span class="label label-default">'+pads[target].axes[i].toFixed(5)+'</span>';
	    info_html += '</li>';
	}
	info_html += '</ul>';

	info_html += '<ul class="list-inline">';
	for(i=0;i<pads[target].buttons.length;i++) {
	    var val = pads[target].buttons[i];
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
	var last_info_html = $("#gamepad-info").html();
	if (info_html != last_info_html) {
	    $("#gamepad-info").html(info_html);
	}
    }
    rAF(scanGamepads);
}

//Start
rAF(scanGamepads);
