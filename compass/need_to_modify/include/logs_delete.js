// JavaScript Document

$(document).ready(function() {
	encryptFn();
});
 var successMesg='';
var encrypt = new JSEncrypt();

function encryptFn() {
	if (!encrypt.pKey) { //如果没有加载公钥
		$.ajax({
			type: 'POST',
			url: '/cgi-bin/getPublicKey.cgi',
			async: true,
			data: {
				'ACTION': 'getPublicKey'
			},
			success: function(data) {
				encrypt.pKey = data;
				encrypt.setPublicKey(encrypt.pKey);
			},
			error: function() {
				alert('网络错误,管理员配置功能将无效！');
			}
		});
	}
}

function warning_box(path, date) {
	var path = path;
	var date = date;
	if (date == '') {
		date = '今天';
	}
	$("<div id='infoDiv'></div><div id='cover'></div>").appendTo("body");
	$("#infoDiv").empty();
	var viewport_width = $(window).width();
	var viewport_height = $(window).height();
	var Bwidth = $(document).width();
	var Bheight = $(document).height();
	var width = 0.6 * Bwidth;
	var height = 0.6 * Bheight;
	var left = Math.round((viewport_width - width) / 2);
	var top = 100;
	$("#cover").css({
		display: 'block',
		top: '0px',
		left: 0,
		width: Bwidth,
		height: Bheight
	});
	$("#infoDiv").css({
		display: 'block',
		left: left,
		top: top,
		width: width
	});
	var startMess = "<table style='margin-left:18px;'><tr><td style='text-align:left'>将删除" + date + "的日志</td><tr><td style='text-align:left;width: 49%;'>请输入当前管理员账户密码：</td><td style='text-align:left'><input id='admin_passwd' type='password' onkeyup='PwKeyUp(event)' style='width: 70%;'/></td></tr></table><input id='path' type='hidden' value=" + path + "/>";
	var endMess = "扫描完成!";
	if ($('#notification-view').find('.content').attr("class") != 'content') {
		var viewport_width = $(window).width();
		var viewport_height = $(window).height();
		var document_width = $(document).width();
		var document_height = $(document).width();
		$overlay = $('<div></div>').attr('id', 'notification-overlay')
			.css('width', document_width + 'px')
			.css('height', document_height + 'px')
			.css('opacity', '0.0');
		$container = $('<div></div>').attr('id', 'notification-container_elvis')
			.css('width', '30%')
			.css('min-height', '80px')
			.css('position', 'fixed')
			.css('z-index', '4001')
			.css('display', 'none')
			.css('text-align', 'center')
			.css('padding', '10px')
			.css('background-color', '#fff')
			.css('border', '3px solid #fcb214');
		var left = Math.round((viewport_width) / 4) + 165;
		var top = Math.round((viewport_height - 80) / 2) - 80;
		/* Centering the container */
		$container.css('top', top).css('left', left)
		$content = $('<div></div>').addClass("content1");
		/* Inserting the content view into the container */
		$container.append($content)
		enconsole.log($container);
		enconsole.log($content);
		/* Inserting the container view into the body */
		$('body').append($overlay)
		$('#notification-view').append($container);
	}
	startMess = "<br />" + "<span style='font-size:13px' ><b>" + startMess + "</n></span>";
	startMess += '<br /><br /><input class="net_button" type="submit" name="save" value="确认" onclick="delete_log()"><input class="net_button" type="submit" name="save" value="取消" onclick="hide()">';
	$('#notification-view').find('.content1').html(startMess);

	$('#notification-overlay').show().fadeTo(500, 0.66,
		function() {
			$('#notification-view').show().fadeTo(500, 1);
			$('#notification-container_elvis').show();
		});
}


function warning_log_box(date) {
	var date = date;
	if (date == ''|| date==undefined) {
		date = '所有';
	} else if(date=='clear'){
		date = '清空';
	}else{
		date = '面板显示';
	}
	$("<div id='infoDiv'></div><div id='cover'></div>").appendTo("body");
	$("#infoDiv").empty();
	var viewport_width = $(window).width();
	var viewport_height = $(window).height();
	var Bwidth = $(document).width();
	var Bheight = $(document).height();
	var width = 0.6 * Bwidth;
	var height = 0.6 * Bheight;
	var left = Math.round((viewport_width - width) / 2);
	var top = 100;
	$("#cover").css({
		display: 'block',
		top: '0px',
		left: 0,
		width: Bwidth,
		height: Bheight
	});
	$("#infoDiv").css({
		display: 'block',
		left: left,
		top: top,
		width: width
	});
	if(date=='清空'){
		var startMess = "<table style='margin-left:18px;'><tr><td style='text-align:left'>将" + date + "日志</td><tr><td style='text-align:left;width: 49%;'>请输入当前管理员账户密码：</td><td style='text-align:left'><input id='admin_passwd' type='password' onkeyup='ClearKeyUp(event)' style='width: 70%;'/></td></tr></table>";
		startMess = "<br />" + "<span style='font-size:13px' ><b>" + startMess + "</n></span>";
		startMess += '<br /><br /><input class="net_button" type="submit" name="save" value="确认" onclick="clearLog()"><input class="net_button" type="submit" name="save" value="取消" onclick="hide()">';
	
	}else{
		var startMess = "<table style='margin-left:18px;'><tr><td style='text-align:left'>将删除" + date + "的日志</td><tr><td style='text-align:left;width: 49%;'>请输入当前管理员账户密码：</td><td style='text-align:left'><input id='admin_passwd' type='password' onkeyup='DeleteKeyUp(event)' style='width: 70%;'/></td></tr></table>";	
		startMess = "<br />" + "<span style='font-size:13px' ><b>" + startMess + "</n></span>";
		startMess += '<br /><br /><input class="net_button" type="submit" name="save" value="确认" onclick="deleteLog()"><input class="net_button" type="submit" name="save" value="取消" onclick="hide()">';
	
	}
	var endMess = "扫描完成!";
	if ($('#notification-view').find('.content').attr("class") != 'content') {
		var viewport_width = $(window).width();
		var viewport_height = $(window).height();
		var document_width = $(document).width();
		var document_height = $(document).width();
		$overlay = $('<div></div>').attr('id', 'notification-overlay')
			.css('width', document_width + 'px')
			.css('height', document_height + 'px')
			.css('opacity', '0.0');
		$container = $('<div></div>').attr('id', 'notification-container_elvis')
			.css('width', '30%')
			.css('min-height', '80px')
			.css('position', 'fixed')
			.css('z-index', '4001')
			.css('display', 'none')
			.css('text-align', 'center')
			.css('padding', '10px')
			.css('background-color', '#fff')
			.css('border', '3px solid #fcb214');
		var left = Math.round((viewport_width) / 4) + 165;
		var top = Math.round((viewport_height - 80) / 2) - 80;
		/* Centering the container */
		$container.css('top', top).css('left', left)
		$content = $('<div></div>').addClass("content1");
		/* Inserting the content view into the container */
		$container.append($content)
		enconsole.log($container);
		enconsole.log($content);
		/* Inserting the container view into the body */
		$('body').append($overlay)
		$('#notification-view').append($container);
	}
	$('#notification-view').find('.content1').html(startMess);

	$('#notification-overlay').show().fadeTo(500, 0.66,
		function() {
			$('#notification-view').show().fadeTo(500, 1);
			$('#notification-container_elvis').show();
		});
}



function hide() {
	$('#notification-view').fadeTo(0, 1, function() {
		$('#notification-container_elvis').hide()
		$('#notification-overlay').fadeTo(0, 0.66, function() {
			$('#notification-overlay').hide();
		});
	});
}

function PwKeyUp(event) {
	var thevent = event || window.event;
	if (thevent.keyCode == 13) {
		//解决firefox连续坦框问题
		document.getElementById('admin_passwd').blur();
		delete_log();
	}
}

function delete_log(path, obj) {
	// var name = $("#admin_name").val();
	hide();
	var passwd = $("#admin_passwd").val();
	var msg = '';
	// passwd = $.md5( passwd );

	var path = $("#path").val();
	var len = path.length - 1;
	path = path.substring(0, len);
	if (!name || !passwd) {
		msg = "用户名及密码不能为空";
		message_manager.show_error_mesg(msg);
		// alert("用户名及密码不能为空");
	} else {
		passwd = encrypt.encrypt(passwd);
		$.get('/cgi-bin/logs_delete_ajax.cgi', {
			pass: passwd,
			path: path
		}, function(data) {
			if (data == "success") {
				msg = "操作执行成功!";
				// alert(msg);
				message_manager.show_warn_mesg(msg);
				// window.location.href = window.location.href;
				list_panel.update_info(true); 
			} else {
				msg = "认证失败，请重新输入配置管理员账户!";
				message_manager.show_error_mesg(msg);
				// alert("认证失败，请重新输入配置管理员账户!"+data);
			}
		});
	}
}

function DeleteKeyUp(event) {
	var thevent = event || window.event;
	if (thevent.keyCode == 13) {
		//解决firefox连续坦框问题
		document.getElementById('admin_passwd').blur();
		deleteLog();
	}

}
function ClearKeyUp(event) {
	var thevent = event || window.event;
	if (thevent.keyCode == 13) {
		//解决firefox连续坦框问题
		document.getElementById('admin_passwd').blur();
		clearLog();
	}

}

function confirm_pwd() {
	hide();
	var passwd = $("#admin_passwd").val();
	var msg = '';
	var checkData
	if (!passwd) {
		msg = "用户名及密码不能为空";
		message_manager.show_error_mesg(msg);
	} else {
		passwd = encrypt.encrypt(passwd);
		$.ajax({
			type: 'GET',
			url: '/cgi-bin/logs_delete_ajax2.cgi',
			//dataType: "json",
			data: {
				pass: passwd
			},
			async: false,
			error: function(request) {
				msg = "认证失败，请重新输入配置管理员账户!";
				message_manager.show_error_mesg(msg);
				message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
			},
			success: function(data) {
				checkData = data
					// if (data == "success") {
				// 	successMesg = "success";
				// }
				if (data == "success") {
				msg = "操作执行成功!";
				message_manager.show_warn_mesg(msg);
				// window.location.href = window.location.href;
				//list_panel.update_info(true);
			} else {
				msg = "认证失败，请重新输入配置管理员账户!";
				message_manager.show_error_mesg(msg);
			}
			},
		});
	 
	}
	return checkData
}

