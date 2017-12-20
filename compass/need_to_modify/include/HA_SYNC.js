// JavaScript Document

function goto_sync(sync_method){
	var method = sync_method;  

	var startMess;
	var endMess;

	$("<div id='infoDiv'></div><div id='cover'></div>").appendTo("body");
	$("#infoDiv").empty();

	var viewport_width = $(window).width();
	var viewport_height = $(window).height();
	var Bwidth=$(document).width();
	var Bheight=$(document).height();
	var width=0.6*Bwidth;
	var info_width=0.3*Bwidth;
	var height=0.6*Bheight;
	var left = Math.round((viewport_width - width) / 2);
	var info_left = Math.round((viewport_width - info_width) / 2);
	var top = 100;
	$("#cover").css({display:'block',top:'0px',left:0,width:Bwidth,height:Bheight});
	$("#infoDiv").css({display:'block',left:info_left,top:top,width:info_width});
	if (method == 0)
	{
		startMess = "正在同步到对端,该操作将会花费较长时间,请稍等...";
	    successMess = "同步到对端成功!";
		failMess = "同步到对端失败!";
	}
	else
	{
		startMess = "正在同步到本地,该操作将会花费较长时间,请稍等...";
	    successMess = "同步到本地成功!";
		failMess = "同步到本地失败!";
	}

	if($('#notification-view').find('.content').attr("class") != 'content')
	{
		var viewport_width = $(window).width();
		var viewport_height = $(window).height();
		var document_width = $(document).width();
		var document_height = $(document).width();
		$overlay = $('<div></div>').attr('id', 'notification-overlay')
					 .css('width', document_width + 'px')
					 .css('height', document_height + 'px')
					 .css('opacity','0.0')
		$container = $('<div></div>').attr('id', 'notification-container')
		var left = Math.round((viewport_width - 516) / 2);
		var top = Math.round((viewport_height - 86) / 2);
		/* Centering the container */
		$container.css('top', top).css('left', left)
		$content = $('<div></div>').addClass("content");
		/* Inserting the content view into the container */
		$container.append($content)
		enconsole.log($container);
		enconsole.log($content);
		/* Inserting the container view into the body */
		$('body').append($overlay)
		$('#notification-view').append($container);
	}
		
	$('#notification-view').find('.content').html(startMess);
	
	$('#notification-overlay').show().fadeTo(500, 0.66,function() {
		   $('#notification-view').show().fadeTo(500, 1);
		   $('#notification-container').show();
	});
	$.get('/cgi-bin/hasync_ajax.cgi',{'flag':method},function(data){
		var strings=data.split("===");
		var len = strings.length;
		var sync_str="";
		var info_str="";
		var sync_staus="";

		$('#notification-view').fadeTo(500, 1, function() {
			$('#notification-container').hide()
			$('#notification-overlay').fadeTo(500, 0.66, function() {
				$('#notification-overlay').hide();
			});
		});	


		if (strings[1] == "0")
		{
			sync_staus="<font color='red' size='4'>"+failMess+"</font>";
			sync_str ="<font color='red'>未同步</font>";
		}
		else
		{
			sync_staus="<font color='green' size='4'>"+successMess+"</font>";
			sync_str ="<font color='green'>已同步</font>";
		}
		document.getElementById("Sync_status").value = sync_str;
	
	    info_str = "<div  style = 'width:100%;height:30px;text-align:center'>"+sync_staus
		info_str += "</div>"
		info_str +="<div  style='padding:5px;text-align:center'><input type='button' style='text-align:center;height:26px;width:40px' value='确定' onclick='hide();' /></div>";
		
		$(info_str).appendTo("#infoDiv");
		var heights = $("#infoDiv").height();
		var Bheight=$(window).height();
		heights = parseInt(heights);
		var final_top = (Bheight - heights) / 2;
		$("#infoDiv").css({display:'block',top:final_top});
		$("html").css({overflow:'visible'});
	});
}
function hide(){	
	$("#infoDiv").css({display:'none'});
	$("#cover").css({display:'none'});	
}
