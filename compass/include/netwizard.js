//author:zhouyuan
//Date:2011-09-26
//function:用于网络配置页面帮助信息框的显示

window.onload=function(){
	parent.parent.window.document.getElementById("bottomFrame").src="footer.cgi";
	$.get('/cgi-bin/netwizard_back.cgi', {}, function(data){	
		var temp = data.split("&&&&&&&&&&");
		$(".help_div_box").remove();
		if(temp[0] == "on")
		{
			$(temp[1]).appendTo("#tmpl1");
			$(temp[2]).appendTo("#tmpl2");
			$(temp[3]).appendTo("#tmpl3_green_ip");
			$(temp[4]).appendTo("#tmpl3_green_addip");
			$(temp[5]).appendTo("#tmpl3_green_eth");
			//$(temp[4]).append("#postfix");
			//$(temp[5]).append("#main_pop3");
			$(temp[6]).appendTo("#snort");
			$(temp[7]).appendTo("#main_state");
		}
	});
}

/*
	作者:周圆
	功能:显示帮助悬浮层信息
	修改时间：2011-09-23
*/
function show_help(id)
{
	$("#"+id).find(".help_div").stop()
	.animate({left: "150", opacity:1}, "fast")
	.css("display","block")
}

/*
	作者:周圆
	功能:隐藏帮助悬浮层信息
	修改时间：2011-09-23
*/
function hide_help(id)
{
	$("#"+id).find(".help_div").stop()
	.animate({left: "130", opacity:0}, "10")
	.css("display","none")
}