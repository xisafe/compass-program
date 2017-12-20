//author:zhouyuan
//Date:2011-07-09
//function:用于connections.cgi页面的js控制

var draw_float = new Array();
var firsttime  = 1;
var num        = 100;
var start      = 1;//表示当前显示的页数，默认为第一页
var sub_start  = 1;//表示当前显示的页数，默认为第一页
var count      = "";
var language   = $("#gui_set").text();
var temp_sub   = new Array();
var new_array  = new Array();
var sort       = "";
var up_or_down = "";
var temp_id    = "";
var is_selected= 0;

//详细显示时的参数
var per_page   = 10;
var pages      = 0;
var temp_src   = "";

//js用到的界面上的文字
var text_protocol = "";
var text_request = "";
var text_response = "";
var text_src = "";
var text_dst = "";
var text_packet = "";
var text_flow = "";
var text_state = "";
var text_timeout = "";
var text_sure = "";
var text_fresh = "";
var text_return = "";
var text_null = "";
var text_no = "";

var language = $("#gui_set").text();
if(language == "en")
{
	text_protocol = "protocol";
	text_request = "request";
	text_response = "response";
	text_src = "source";
	text_dst = "destination";
	text_packet = "packet";
	text_flow = "flow";
	text_state = "state";
    text_time = "time";	
	text_timeout = "Current connection alerady timeout";
	text_sure = "sure";
	text_fresh = "refresh";
	text_return= "return";
	text_null = "current connections is timeout";
	text_no = "No search result";
}else{
	text_protocol = "协议";
	text_request = "会话发起端";
	text_response = "会话响应端";
	text_src = "源";
	text_dst = "目的";
	text_packet = "包量";
	text_flow = "流量";
	text_state = "状态";
	text_time = "剩余超时时间";	
	text_timeout = "当前连接已断开";
	text_sure = "确定";
	text_fresh = "刷新";
	text_return = "返回";
	text_null = "此连接已经过期";
	text_no = "没有找到相关搜索结果";
}


$(document).ready(function(){
		for(var i = 0;i<4;i++)
		{
			draw_float[i] = new Array();
			for(var j = 0;j<100;j++)
			{
				draw_float[i].push([j,0]);
			}
		}
		setInterval("get_data()",3000);
		setInterval("get_connect()",3000);
});



var id_array = ["total","tcp","udp","icmp","other"];

function get_data()
{
	//start++;
	//$("#main_table").css("display","table");
	$("#wait").css("display","none");
	$.get('/cgi-bin/connection_back.cgi', {}, function(data){
		var temp_arry = data.split("=");
		for(var i = 0;i<temp_arry.length;i++)
		{
			$("#"+id_array[i]).text(temp_arry[i]);
			var percent = 0;
			if(parseInt(temp_arry[0]) != 0)
			{
				percent = (parseInt(temp_arry[i])/parseInt(temp_arry[0]))*100;
				percent = percent.toFixed(1);
			}
			var str = draw_percent(percent);
			if(i>0)
			{	//关于比例图的相关设置
				$("#"+id_array[i]+"percent table").remove();
				$(str).appendTo("#"+id_array[i]+"percent");
				$("#"+id_array[i]+"percent").next().text(percent+"%");
				
				//关于流量图的相关设置
				draw_float[i-1].push([num,temp_arry[i]]);
				draw_float[i-1] = draw_float[i-1].slice(1,101);
				num++;
			}
		}
		
		var finaldis = new Array();
		var legends = ["TCP","UDP","ICMP","其他"];
		for(var m=0;m<4;m++)
		{
			finaldis[m] = {'label':legends[m],
				       'data':draw_float[m],
					   'color':m+5
		    	      };
		}
		var options = {
        'series': { shadowSize: 0 ,lines:{lineWidth: 1}}, // drawing is faster without shadows
        'yaxis': { min: 0},
        'xaxis': { show: false},
		'legend':{
					noColumns: 1,
					container:$(".rx-text")
				}
		};
		
		$.plot($("#connect_channels"),finaldis,options);	
		
	});
}

// 绘制百分比例图
function draw_percent(percent)
{           
	var background_img = "class='percent_low'";
	var no_percent = 100-parseInt(percent);
	var str = "<table class='percentage' cellpadding='0' cellspacing='0'><tr>";
	var null_td = 100-parseInt(percent);
	if(parseInt(percent) > 0)
	{
		
		str += "<td  class='used'   width='"+parseInt(percent)+"px'"+ background_img +"></td><td class='unused'  width='"+null_td+"px' ></td>";
	}else{
		str += "<td class='used'   width='0px'></td><td class='unused'  width='100px' ></td>";
	}
	str += "</tr></table>";
	return str;
}


window.onload=function(){
	get_connect();
	get_data();
}

function get_connect()
{
	
	$.get('/cgi-bin/connect_count.cgi', {start:start}, function(data){
		//alert(data);
		is_selected = 0;
		var temp = data.split("=");
		var str = "";
		
		if(temp[0]>= start && start > 0)
		{
			if(language == "en")
			{
				$("#count_pre").text("total:");
				$("#count").text(temp[0]);
				$("#count_las").text("pages");
				$("#pages").text("page "+start);
			}else{
				$("#count_pre").text("共");
				$("#count").text(temp[0]);
				$("#count_las").text("页");
				$("#pages").text("第"+start+"页");
			}
			for(var i= 1;i<temp.length-1;i++)
			{
				var temp_str = temp[i].split(",");
				str += "<tr class='new' ><td  class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"\",\"\",\"\",\"\")'>"+temp_str[0]+"</td><td  class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"\",\"\",\"\",\"\")'>"+temp_str[1]+"</td><td class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"tcp\",\"\",\"\",\"\")'>"+temp_str[2]+"</td><td   class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"udp\",\"\",\"\",\"\")'>"+temp_str[3]+"</td><td  class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"icmp\",\"\",\"\",\"\")'>"+temp_str[4]+"</td><td>"+temp_str[5]+"</td></tr>";
			}
			$(".new").remove();
			
			$(str).appendTo(".ruleslist");
			
		}
	});
}



/*点击下一页*/
function next_page()
{
	count = $("#count").text();
	if(start < count)
	{
		start++;
		get_connect();
	}
}

function last_page()
{
	start--;
	get_connect();
}

function first_page()
{
	start=1;
	get_connect();
}

function end_page()
{
	count = $("#count").text();
	if(start < count)
	{
		start = count;
		get_connect();
	}
}

function skip_page()
{
	count = $("#count").text();
	var error = "";
	var pages = document.getElementById("skip_page").value;
	var re = /^(\d+)$/;
	if(re.test(pages))
	{
		if(parseInt(RegExp.$1) <= count && parseInt(RegExp.$1) >0)
		{
			start = RegExp.$1;
			get_connect();
		}else{
			error = "所跳转页数不能超过总页数或为0";
		}
	}else{
			error = "所输入跳转页数格式不合法";
	}
	error_box(error);
}

function choice_by_ip()
{
	
	is_selected = 1;
	var ip = document.getElementById("choice_by_ip").value;
	var re = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
	var error = "";
	if(!re.test(ip))
	{
		if(language == "en")
		{
			error = "The valid Ip format";
		}else{
			error = "所输入的IP格式错误";
		}
	}else if(!((RegExp.$1>=0 && RegExp.$1<=255) && (RegExp.$2>=0 && RegExp.$2<=255)&&(RegExp.$3>=0 && RegExp.$3<=255) && ( RegExp.$4>=0 && RegExp.$4<=255))){
		if(language == "en")
		{
			error = "The ip should be 0-255";
		}else{
			error = "所输入的ip应在0-255之间";
		}
	}else{
		$.get('/cgi-bin/connection_search.cgi', {start:start,ip:ip}, function(data){
			//alert(data);
			//$("return_span").css("display","inline");
			var temp = data.split("=");
			
			var str = "";
			//alert("haha");
			if(temp[0]>= start && start > 0)
			{
				if(language == "en")
				{
					$("#count_pre").text("total:");
					$("#count").text(temp[0]);
					$("#count_las").text("pages");
					$("#pages").text("page "+start);
				}else{
					$("#count_pre").text("共");
					$("#count").text(temp[0]);
					$("#count_las").text("页");
					$("#pages").text("第"+start+"页");
				}
				
				for(var i= 1;i<temp.length-1;i++)
				{
					var temp_str = temp[i].split(",");
					str += "<tr class='new' ><td class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"\",\"\",\"\",\"\")' >"+temp_str[0]+"</td><td class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"\",\"\",\"\",\"\")'>"+temp_str[1]+"</td><td class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"tcp\",\"\",\"\",\"\")'>"+temp_str[2]+"</td><td class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"udp\",\"\",\"\",\"\")'>"+temp_str[3]+"</td><td class='show_cursor' onclick='get_detail(\""+temp_str[0]+"\",\"icmp\",\"\",\"\",\"\")'>"+temp_str[4]+"</td><td>"+temp_str[5]+"</td></tr>";
				}
				if(str == "")
				{
					str = "<tr><td colspan='6'></td></tr>";
				}
				$(".new").remove();
				$(str).appendTo(".ruleslist");
			}else{
				var str = "<tr><td colspan = '11'> "+text_no+"</td></tr>";
			}
		});
	}
	error_box(error);
}

function error_box(error)
{
	if(error != "")
	{
		$("#pop-divs").remove();
		$("#pop-error-divs").remove();
		var str = '<div id="pop-divs"></div><div id="pop-error-divs"><span><img src="/images/pop_error.png" />'+error+'</span><span id="cancel"><input type="button"  class="net_button"  value= \"'+text_sure+'\" onclick="hide()"></span></div>';
		//alert(str);
		$(str).appendTo("body");
	}
}


var pro        = "";
var state      = "";
var time       = "";
var res_src    = "";
var res_dst    = "";
var res_sport  = "";
var res_dport  = "";
var res_packets= "";
var res_flow   = "";
var res_bytes  = "";
var rsp_src    = "";
var rsp_dst    = "";
var rsp_sport  = "";
var rsp_dport  = "";
var rsp_packets= "";
var rsp_flow   = "";
	
var re  = /^([a-zA-Z]+) +\d+ +(\d+) +([a-zA-Z_]*)/;
var re1 = /src=(\d+\.\d+\.\d+\.\d+) +dst=(\d+\.\d+\.\d+\.\d+) +sport=(\d+) +dport=(\d+) +packets=(\d+) +bytes=(\d+) +(\[[a-zA-Z]+\])? +src=\d+\.\d+\.\d+\.\d+/;
var re11 = /src=(\d+\.\d+\.\d+\.\d+) +dst=(\d+\.\d+\.\d+\.\d+) +sport=(\d+) +dport=(\d+) +packets=(\d+) +bytes=(\d+) +src=\d+\.\d+\.\d+\.\d+/;
var re2 = /src=(\d+\.\d+\.\d+\.\d+) +dst=(\d+\.\d+\.\d+\.\d+) +sport=(\d+) +dport=(\d+) +packets=(\d+) +bytes=(\d+) +(\[[a-zA-Z]+\])? +mark=\d+/;
var re22 = /src=(\d+\.\d+\.\d+\.\d+) +dst=(\d+\.\d+\.\d+\.\d+) +sport=(\d+) +dport=(\d+) +packets=(\d+) +bytes=(\d+) +mark=\d+/;
		
//获取当前IP连接的详细信息
function get_detail(src_ip,type,sort,index,up_to_down)
{
	temp_src = src_ip;
	sub_start = 1;
	$.get('/cgi-bin/connection_detail.cgi', {src_ip:src_ip,type:type,sort:sort,index:index,up_to_down:up_to_down}, function(data){
		//alert(data);
		$("#pop-divs").remove();
		$("#pop-text-div").remove();
		/*udp      17 175 src=127.0.0.1 dst=127.0.0.1 sport=40201 dport=123 packets=9800 bytes=2077600 src=127.0.0.1 dst=127.0.0.1 sport=123 dport=40201 packets=9800 bytes=999600 [ASSURED] mark=0 secmark=0 use=3
		*/
		temp_sub = data.split("\n");
		if((temp_sub.length)%per_page == 0)
		{
			pages = (temp_sub.length)/per_page;
		}else{
			pages = Math.ceil((temp_sub.length)/per_page);
		}
		var str = "<div id='pop-divs'></div>";
		str += "<div id='pop-text-div'><div id='pop-text-div-header'><img  id='pop-text-img' src='/images/delete.png  ' onclick='hide()' /></div><table width='100%' class='detail_table'  cellpadding='0' cellspacing='0' border='0'>";
		str += "<tr class='env_thin_val'><td rowspan='2' width='5%'>"+text_protocol+"</td>";
		str += "<td colspan = '4' class='add-div-table' width='40%'>"+text_request+"</td>";
		str += "<td colspan = '4' class='add-div-table' width='40%'>"+text_response+"</td>";
		str += "<td rowspan='2'  width='10%'>"+text_state+"</td><td rowspan='2'  width='5%'>"+text_time+"</td></tr>";
		str+= "<tr class='env_thin_val'><td>"+text_src+"</td><td>"+text_dst+"</td><td class='show_cursor'   onclick='my_sort(\"src_packet\",\"5\")'>"+text_packet+"<img src='/images/down_to_up.png' id='src_packet' class='sort_img'  /></td><td class='show_cursor' onclick='my_sort(\"src_flow\",\"6\")' >"+text_flow+"<img src='/images/down_to_up.png' id='src_flow' class='sort_img' /></td><td>"+text_src+"</td><td>"+text_dst+"</td><td class='show_cursor'  onclick='my_sort(\"dst_packet\",\"11\")'>"+text_packet+"<img src='/images/down_to_up.png' id='dst_packet' class='sort_img'  /></td><td class='show_cursor'  onclick='my_sort(\"dst_flow\",\"12\")'>"+text_flow+"<img src='/images/down_to_up.png' id='dst_flow' class='sort_img'  /></td></tr>";
		str += update_detail();
		str += "</table></div>";
		//alert(str);
		$(str).appendTo("body");
		//alert(up_to_down);
		if(up_to_down == "up_to_down")
		{
			//alert("test1");
			$("#"+temp_id).attr("src","/images/up_to_down.png");
		}else if(up_to_down == "down_to_up"){
			//alert("test2");
			$("#"+temp_id).attr("src","/images/down_to_up.png");
		}
	});
}

function cut_connections()
{
	$.get('/cgi-bin/connection_cutoff.cgi', {}, function(data){
	//alert("haha");
	get_connect();
	});
}


function my_sort(id,index)
{
	temp_id = id;
	sub_start  = 1;
	if($("#"+id).attr("src")  == "/images/down_to_up.png")
	{
		up_or_down            = "up_to_down";	
	}else{
		up_or_down            = "down_to_up";
	}
	get_detail(temp_src,"","sort",index,up_or_down);
}


function hide()
{
	$("#pop-divs").remove();
	$("#pop-text-div").remove();
	$("#pop-error-divs").remove();
}


function update_detail()
{
		var sub_str = "";
		$(".sub_new").remove();
		$("#sub_pages").remove();
		var length = temp_sub.length;
		var end = "";
		if(sub_start*per_page < length)
		{
			end = sub_start*per_page;
		}else{
			end = length;
		}
		
		for(var i = (sub_start-1)*per_page;i<end;i++)
		{
			if(temp_sub[i] != "")
			{
				if(re.test(temp_sub[i]))
				{
					pro  = RegExp.$1;
					time = RegExp.$2;
					if(RegExp.$3 != "src")
					{
						state  = RegExp.$3;
					}
					if(pro == "icmp")
					{
						re1 = /src=(\d+\.\d+\.\d+\.\d+) +dst=(\d+\.\d+\.\d+\.\d+) +type=\d+ +code=\d+ +id=\d+ +packets=(\d+) +bytes=(\d+)+ +src=\d+\.\d+\.\d+\.\d+/;
						re2 = /src=(\d+\.\d+\.\d+\.\d+) +dst=(\d+\.\d+\.\d+\.\d+) +type=\d+ +code=\d+ +id=\d+ +packets=(\d+) +bytes=(\d+) +mark=\d+/;
						if(re1.test(temp_sub[i]))
						{
							res_src     = RegExp.$1;
							res_dst     = RegExp.$2;
							res_packets = RegExp.$3;
							res_flow    = RegExp.$4;
						}
						if(re2.test(temp_sub[i]))
						{
							
							rsp_src     = RegExp.$1;
							rsp_dst     = RegExp.$2;
							rsp_packets = RegExp.$3;
							rsp_flow    = RegExp.$4;
						}
					}else{
					var re1 = /src=(\d+\.\d+\.\d+\.\d+) +dst=(\d+\.\d+\.\d+\.\d+) +sport=(\d+) +dport=(\d+) +packets=(\d+) +bytes=(\d+) +(\[[a-zA-Z]+\])? +src=\d+\.\d+\.\d+\.\d+/;

var re2 = /src=(\d+\.\d+\.\d+\.\d+) +dst=(\d+\.\d+\.\d+\.\d+) +sport=(\d+) +dport=(\d+) +packets=(\d+) +bytes=(\d+) +(\[[a-zA-Z]+\])? +mark=\d+/;
						if(re1.test(temp_sub[i]))
						{
							res_src     = RegExp.$1+":"+RegExp.$3;
							res_dst     = RegExp.$2+":"+RegExp.$4;
							res_packets = RegExp.$5;
							res_flow    = RegExp.$6;
						}else if(re11.test(temp_sub[i]))
						{
							res_src     = RegExp.$1+":"+RegExp.$3;
							res_dst     = RegExp.$2+":"+RegExp.$4;
							res_packets = RegExp.$5;
							res_flow    = RegExp.$6;
						}
					if(re2.test(temp_sub[i]))
					{
						rsp_src     = RegExp.$1+":"+RegExp.$3;
						rsp_dst     = RegExp.$2+":"+RegExp.$4;
						rsp_packets = RegExp.$5;
						rsp_flow    = RegExp.$6;
					}else if(re22.test(temp_sub[i]))
					{
						rsp_src     = RegExp.$1+":"+RegExp.$3;
						rsp_dst     = RegExp.$2+":"+RegExp.$4;
						rsp_packets = RegExp.$5;
						rsp_flow    = RegExp.$6;
					}
				}
				
				}
		var line = pro+","+res_src+","+res_dst+","+res_packets+","+res_flow+","+rsp_src+","+rsp_dst+","+rsp_packets+","+rsp_flow+","+state+","+time;
		
		sub_str += "<tr  class='sub_new odd_thins' ><td>"+pro+"</td><td>"+res_src+"</td><td>"+res_dst+"</td><td>"+res_packets+"</td><td>"+deal_packet(res_flow)+"</td><td>"+rsp_src+"</td><td>"+rsp_dst+"</td><td>"+rsp_packets+"</td><td>"+deal_packet(rsp_flow)+"</td><td>"+state+"</td><td>"+time+"</td></tr>";
		
		}
	}
	sub_str += "<tr class='add-div-table' id='sub_pages' ><td colspan='4' border='0'></td><td  colspan='3' class=' page_button'  align='center' border='0' ><img   src='/images/first-page.gif'    onclick='sub_first_page()' /><img src='/images/last-page.gif'     onclick='sub_last_page()' /><span><b id='sub_count' class='hidden'>"+pages+"</b></span><span id='pages' style='margin-top:5px;'>"+sub_start+"/"+pages+"</span><img src='/images/next-page.gif'     onclick='sub_next_page()'  /><img src='/images/end-page.gif'      onclick='sub_end_page()'   /></td><td colspan='4' border='0'></td></tr>";
	return sub_str;
}

/*包、流量的单位转换*/
function deal_packet(num)
{
	var temp = "";
	if(parseInt(num)>1024*1024)
	{
		temp = (parseInt(num)/(1024*1024)).toFixed(2)+"MB";
	}else if(parseInt(num) >1024)
	{
		temp = (parseInt(num)/1024).toFixed(2)+"KB";
	}else{
		temp = parseInt(num)+"B";
	}
	return temp;
}


/*详细信息分页函数*/
/*点击下一页*/
function sub_next_page()
{
	var sub_count = $("#sub_count").text();
	if(sub_start < sub_count)
	{
		sub_start++;
		var str = update_detail();
		$(str).appendTo('.detail_table');
	}
}

function sub_last_page()
{
	if(sub_start >1)
	{	
		sub_start--;
		var str = update_detail();
		$(str).appendTo('.detail_table');
	}
}

function sub_first_page()
{
	sub_start=1;
	var str = update_detail();
	$(str).appendTo('.detail_table');
}

function sub_end_page()
{
	var count = $("#sub_count").text();
	if(sub_start < count)
	{
		sub_start = count;
		var str = update_detail();
		$(str).appendTo('.detail_table');
	}
}
