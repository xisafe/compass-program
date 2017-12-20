//author:zhouyuan
//Date:2012-03-09
//function:用于hirel.cgi页面的js控制

$(document).ready(function(){
	
	$("#is_enabled").click(function(){
		if($(this).attr("value") == '1')
		{
			$(this).attr("value",0);
		}else{
			$(this).attr("value",1);
		}
	});
	
	var version =  CheckBrowser();
	/*
	if(version == 'firefox')
	{
		$("#vrrp").attr("rowspan","10");
		$("#sub_row2").attr("rowspan","5");
	}else{
		$("#vrrp").attr("rowspan","10");
		$("#sub_row2").attr("rowspan","5");
		$("#sub_row1").attr("rowspan","5");
	}
	*/
	$("#mode_select").change(function(){
		var test = $(this).attr("value");
		if(test == "AA")
		{
			if(version == 'firefox')
			{
				$(".ha2").css("display","table-row");
				$("#sub_row2").attr("rowspan","5");
				$("#sub_row1").attr("rowspan","5");
			}else{
				$(".ha2").css("display","block");
				$("#sub_row2").attr("rowspan","5");
				$("#sub_row1").attr("rowspan","5");
			}
			
			$("#vrrp").attr("rowspan","10");
			
			
			$(".mode1").css("display","none");
			$(".mode2").css("display","none");
		}else{
			$("#vrrp").attr("rowspan","5");
			$("#sub_row1").attr("rowspan","5");
			$(".ha2").css("display","none");
			if(version == 'firefox')
			{
				$(".mode1").css("display","table-cell");
			}else{
				$(".mode1").css("display","block");
			}
		}
	});
	check_mode();
	$("#V1_STATE").change(function(){
		check_mode();
	});
	$("#mode_select").change(function(){
		check_mode();
	});
	$("#V1_ID").change(function(){
		check_mode();
	});
	$("#V2_ID").change(function(){
		check_mode();
	});
	refresh();
	//setInterval("refresh()",3000);
});

function refresh()
{
	$.get('/cgi-bin/hirel_ajax.cgi', {}, function(data){
		
		var str ="";
		var temp = data.split("=");
		var reg = /pop_warn_min/;
		if(!reg.test(data)){
			for(var i = 0;i<temp.length-1;i++){
				var detail = temp[i].split("---");
				str += "<tr class='event_detail'><td>"+detail[0]+"</td><td>"+detail[1]+"</td></tr>";
			}
		}
		else{
			str = data;
		}
		$(".event_detail").remove();	
		$(str).appendTo(".ruleslist");
		
	});
}

function check_mode(){
	var mode = $("#mode_select").val();
	var role = $("#V1_STATE").val();
	var v1 = $("#V1_ID").val();
	var v2 = $("#V2_ID").val();
	if((mode == "AA") && (v1 > v2)){
		$("#saves").attr("colspan" ,3);
		$("#sync").css("display" ,"table-cell");
	}
	else if((mode == "AP") && (role == "MASTER")){
		$("#saves").attr("colspan" ,3);
		$("#sync").css("display" ,"table-cell");
	}
	else{
		$("#saves").attr("colspan" ,4);
		$("#sync").css("display" ,"none");
	}
}