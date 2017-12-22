//author:zhouyuan
//Date:2011-07-09
//function:用于footer.cgi页面的js控制


var time = 3500;
var is_IE = check_explorer()
var color = "";
function check_explorer()
{
	var app=navigator.appName;
	if (app.indexOf('Netscape') != -1) 
	{
		return 0;
	}else{
		return 1;
	}
}


$(document).ready(function(){
	window.setInterval("read_update()",time);
});



function odd_over(id)
{
	//color = $("#"+id).css("background-color");
	//$("#"+id).css("background-color","#fcfd9b");
	//var font_color = $("#"+id).css("color");
	$("#"+id).css("CURSOR","pointer");
	$("#"+id).css("font-size","14px");
	//$("#"+id).find("td").css("border-top","2px solid font_color");
}

function odd_out(id)
{
	//$("#"+id).css("background-color",color);
	$("#"+id).css("font-size","11px");
	//$("#"+id).css("height","20px");
}



function show_detail(eth)
{
	$.get('/cgi-bin/netstatus_detail.cgi', {eth:eth}, function(data){
		$("#pop-divs").remove();
		$("#pop-text-div").remove();
		var str = "<div id='pop-divs'></div>";
		str += "<div   id='pop-text-div'><div id='pop-text-div-header'><img  id='pop-text-img' src='/images/delete.png  ' onclick='hide()' /></div><table width='100%' class='detail_table'  cellpadding='0' cellspacing='0' border='0'>";
		str += data;
		str += "</table></div>";
		$(str).appendTo("body");
	});
}




function read_update()
{
	var all_tr = $(".ruleslist tr");
	var speed_in_new = new Array;
	var speed_out_new = new Array;
	for(var i =1;i<all_tr.length-1;i++)
	{
		speed_in_new.push(all_tr.eq(i).find("td").eq(2).attr("name"));
	    speed_out_new.push(all_tr.eq(i).find("td").eq(3).attr("name"));
	}
	$.get('/cgi-bin/netstatus_update.cgi', {}, function(data){
		$(".ruleslist").remove();
		$(".down_tr").remove();
		$(data).appendTo(".right-content");
		var all_tr = $(".ruleslist tr");
		var speed_in_old = new Array;
		var speed_out_old = new Array;
		for(var i =1;i<all_tr.length-1;i++)
		{
			speed_in_old.push(all_tr.eq(i).find("td").eq(2).attr("name"));
			speed_out_old.push(all_tr.eq(i).find("td").eq(3).attr("name"));
		}

		
		for(var i =0;i<speed_in_old.length;i++)
		{
			speed_in_new[i] = speed_in_new[i].replace(/ /,"");
			speed_in_old[i] = speed_in_old[i].replace(/ /,"");
			speed_out_new[i] = speed_out_new[i].replace(/ /,"");
			speed_out_old[i] = speed_out_old[i].replace(/ /,"");
			
			var ins =parseInt(speed_in_old[i])-parseInt(speed_in_new[i]);
			ins = parseInt((ins/time)*100)/100;
			ins = check_speed(ins);
			$(".speed_in").eq(i).text(ins);
			
			var out = parseInt(speed_out_old[i])-parseInt(speed_out_new[i]);
			out= parseInt((out/time)*100)/100;
			out = check_speed(out);
			$(".speed_out").eq(i).text(out);
		}
	});
}

function hide()
{
	$("#pop-divs").remove();
	$("#pop-text-div").remove();
}

function check_speed(rx)
{
	var rxkb = rx;
	rxunit = "KB/s";
	if (rx >= 1000) {
		rx = rx / 1000;
		rxunit = "MB/s";
	}
	if (rx >= 1000) {
		rx = rx / 1000;
		rxunit = "GB/s";
	}
	return rx+rxunit;
}
