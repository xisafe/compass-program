// JavaScript Document
$(document).ready(function(){
	/*用于鼠标移向待解释的表单元素时，显示帮助层,鼠标移除，帮助层*/
		$(".add-div-type").hover(function() {
			$(this).find(".help_div").stop()
			.animate({left: "150", opacity:1}, "fast")
			.css("display","block")
		}, function() {
			$(this).find(".help_div").stop()
			.animate({left: "130", opacity:0}, "10")
			.css("display","none")
		});
});


/*author:zhouyuan
  date:2011-10-12
*/
window.onload=function(){
	var current_href=location.href;
	var temp= current_href.split("?"); 
	if(temp[1])
	{
		var temp2 = temp[1].split("&");
		if(temp2[0] == "ACTION=edit")
		{
			$("#add-div-content").css("display","block");
		
			if(temp2[1])
			{
				var id = temp2[1].split("=");
				if(id[1])
				{
					$(".ruleslist tr").eq(id[1]+1).addClass("selected"); 
				}
			}
		}

	}
	if($("span").hasClass("fielderror"))
	{
		$("#add-div-content").css("display","block");
	}
}


$(document).ready(function(){
	$.get('/cgi-bin/qos_snort_ajax.cgi',function(data){
		var page_name = $(".editoradd").text();
		var dev = /添加 QoS 设备/;
		var cla = /添加 QoS 类/;
		var rul = /添加 QoS 规则/;
		if (dev.test(page_name)){
			$("<input id='help_hidden' value='/manage/qos/devices' class='hidden_class' />").appendTo("body");
		}
		if (cla.test(page_name)){
			$("<input id='help_hidden' value='/manage/qos/classes' class='hidden_class' />").appendTo("body");
		}
		if (rul.test(page_name)){
			$("<input id='help_hidden' value='/manage/qos/rules' class='hidden_class' />").appendTo("body");
		}
		if(data){
			var pages = new Array();
			var devices = new Array();
			var classes = new Array();
			var rules = new Array();
			pages = data.split("---###");
			devices = pages[0].split("-###");
			classes = pages[1].split("-###");
			rules = pages[2].split("-###");
			if (dev.test(page_name)){
				$(".add-div-type").eq(0).addClass("need_help").append(devices[0]);
				$(".add-div-type").eq(1).addClass("need_help").append(devices[1]);
				$(".add-div-type").eq(2).addClass("need_help").append(devices[2]);
			}
			if (cla.test(page_name)){
				for (var i=0;i<5;i++){
					$(".add-div-type").eq(i).addClass("need_help").append(classes[i]);
				}
			}
			if (rul.test(page_name)){
				$(".add-div-type").eq(0).addClass("need_help").append(rules[0]);
				$(".add-div-type").eq(2).addClass("need_help").append(rules[1]);
				$(".add-div-type").eq(3).addClass("need_help").append(rules[2]);
				$(".add-div-type").eq(5).addClass("need_help").append(rules[3]);
				$(".add-div-type").eq(8).addClass("need_help").append(rules[4]);
			}
		}
	});
});
