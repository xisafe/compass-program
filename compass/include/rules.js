//author:zhouyuan
//Date:2011-10-20
//function:用于rules.cgi页面的js控制

$(document).ready(function(){
		var rule_set_tr = $("#rule_set").find("tr");//规则集行数
		var sub_rule_tr = $("#sub_rule").find("tr");//规则行数
		var search_tr = $("#search_table").find("tr");//搜索规则行数
		
		//判断规则集那一行被编辑
		var i = 0;
		var is_edit = 0;
		for(i =0;i<rule_set_tr.length;i++)
		{
			if(rule_set_tr.eq(i).hasClass("selected"))
			{
				is_edit = 1;
				break;
			}
		}
		if(is_edit)
		{
			document.getElementById("rule_set_div").scrollTop = i*26;
		}
		//######################
		
		//判断规则哪一行被编辑
		var j = 0;
		var is_click = 0;
		for(j =0;j<sub_rule_tr.length;j++)
		{
			if(sub_rule_tr.eq(j).hasClass("selected"))
			{
				is_click = 1;
				break;
			}
			
		}
		if(is_click)
		{
			document.getElementById("sub_rule_div").scrollTop = j*26;
		}
		//######################
		
		if(!is_edit)
		{
			var height_style = (document.documentElement.clientHeight||window.innerHeight)-130;
			if(rule_set_tr.length>15)
			{
				$('#rule_set_div').css("height",height_style+"px");
			}else{
				$('#rule_set_div').css("height","auto");
			}
		}else{
			var height_style = document.documentElement.clientHeight||window.innerHeight;
			var sub_tr = $("#sub_rule").find("tr");
			$('#rule_set_div').css("height","160px");
			if(sub_tr.length>11)
			{
				$('#sub_rule_div').css("height",(height_style-110)/2+"px");
			}
		}
		var div_arr = $("div");
		var no_result = $("table");
		
		var no_is_result = 0;
		var is_search = 0;
		for(var z =0;z<div_arr.length;z++)
		{
			if(div_arr.eq(z).hasClass("search_div"))
			{
				is_search = 1;
				break;
			}
		}
		
		if(is_click)
		{
			document.getElementById("sub_rule_div").scrollTop = j*26;
		}
		
		var h = 0;
		for(h =0;h<no_result.length;h++)
		{
			if(no_result.eq(h).hasClass("search_result"))
			{
				no_is_result = 1;
				break;
			}
		}
		
		if(is_search)
		{
			$('#rule_set_div').css("height","160px");
			var m = 0;
			var sear_is_edit = 0;
			for(m =0;m<search_tr.length;m++)
			{
				if(search_tr.eq(m).hasClass("selected"))
				{
					sear_is_edit = 1;
					break;
				}
			}
			if(sear_is_edit)
			{
				document.getElementById("search_div").scrollTop = m*26;
			}
		}
		
		
		if(no_is_result)
		{
			$('.search_div').css("height","30px");
		}
		if(search_tr.length>10)
		{
			var height_style = document.documentElement.clientHeight||window.innerHeight;
			$('.search_div').css("height",(height_style-110)/2+"px");
		}else{
			$('.search_div').css("height","auto");
		}
		var sub_temp_height = $('#sub_rule_div').css("height");
		var sear_temp_height = $('.search_div').css("height");
		if(!sub_temp_height && !sear_temp_height)
		{
			var height_style = (document.documentElement.clientHeight||window.innerHeight)-130;
			if(rule_set_tr.length>15)
			{
				$('#rule_set_div').css("height",height_style+"px");
			}else{
				$('#rule_set_div').css("height","auto");
			}
		}
		
		
});
function search_check(){
	var str=document.getElementById('search_text').value;
	var reg = /^[_0-9a-zA-Z\u4e00-\u9fa5][_0-9a-zA-Z\u4e00-\u9fa5]+$/;
	if((str.length < 2) || (str.length > 50)){
		alert("关键字长度不合法，请重新输入(长度为2-50)");
		return false;
	}
	else if(!reg.test(str)){
		alert("关键字包含非法字符，请重新输入");
		return false;
	}
	else{
		return ture;
	}

}
