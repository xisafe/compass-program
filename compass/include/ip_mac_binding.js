// JavaScript Document
//显示添加的栏
$(document).ready(function(){
	$('#add-div-header_ip').click(function(){
            if($('#add-div-content_ip').css('display')=='none')
			{
				$('#add-div-content_ip').slideDown('1000');
				$('#add-div-header_ip img').attr("src","/images/del.png");
			}else{
				$('#add-div-content_ip').slideUp('1000');
				$('#add-div-header_ip img').attr("src","/images/add.png")
			}
        });
	$('#add-div-header_ip1').click(function(){
            if($('#add-div-content_ip1').css('display')=='none')
			{
				$('#add-div-content_ip1').slideDown('1000');
				$('#add-div-header_ip1 img').attr("src","/images/del.png");
			}else{
				$('#add-div-content_ip1').slideUp('1000');
				$('#add-div-header_ip1 img').attr("src","/images/add.png")
			}
        });
		
});
var status = 0;
function add_method(method){
	var status = method;
	if(status == "unknown"){
		$("#manual_id").css("display", "none");
		var method_value=$("#method_select").val();
		if(method_value == "scan_ip"){
			$("#scan_select").css("display", "none");
			$("#in_ip").css("display", "inline");
			$("#note_message").css("display", "inline");
		}
		else{
			$("#in_ip").css("display", "none");
			$("#note_message").css("display", "none");
			$("#scan_select").css("display", "inline");
		}
		$("#fuzhu").val(method_value);
	}
	if(status == "manual"){
		$("#manual_id").css("display", "block");
		if($('#add-div-content').css('display')=='none'){
			$('#add-div-content').slideDown('1000');
			$('#add-div-header img').attr("src","/images/del.png");
		}
	}
}

function goto_scan(scan_method,iface,hunhe){
	if(check._submit_check(object2,check) > 0){
		return;
	}
	var iface = iface;  //端口扫描时获取端口
	var scan_method = scan_method;
	var hunhe = hunhe;
	if(iface == 0 ){
		var iface = $("#scan_select").val();  
		var scan_method = $("#fuzhu").val();
	}
	var zone,duankou;
	if((scan_method == "searched") && (hunhe == 0)){
		zone = "<option  value='br0'>LAN区域</option><option  value='br1'>DMZ区域</option>";
		duankou = "未定义";
	}
	if((scan_method == "scan_ip") && (hunhe == 0)){
		iface = $("#in_ip").val();
		if(!iface){
			alert("输入不能为空!");
			return 0;
		}
		else if(!range_ip(iface)){
			alert("请输入正确的IP地址段!");
			return 0;
		}
		zone = "<option  value='br0'>LAN区域</option><option  value='br1'>DMZ区域</option>";
		duankou = "未定义";
	}
	else if(iface == "br0" || hunhe == "br0"){
		duankou = "LAN区域";
		hunhe = "br0";
		zone = "<option  value='br0'>LAN区域</option>";
	}
	else if(iface == "br1" || hunhe == "br1"){
		duankou= "DMZ区域";
		hunhe = "br1";
		zone = "<option  value='br1'>DMZ区域</option>";
	}
	if(scan_method == "no"){
		alert("选择IP/MAC扫描后将进行扫描！");
	}
	else{
		$("<div id='infoDiv'></div><div id='cover'></div>").appendTo("body");
		$("#infoDiv").empty();
		var viewport_width = $(window).width();
		var viewport_height = $(window).height();
		var Bwidth=$(document).width();
		var Bheight=$(document).height();
		var width=0.6*Bwidth;
		var height=0.6*Bheight;
		var left = Math.round((viewport_width - width) / 2);
		var top = 100;
		$("#cover").css({display:'block',top:'0px',left:0,width:Bwidth,height:Bheight});
		$("#infoDiv").css({display:'block',left:left,top:top,width:width});
		var startMess = "正在扫描,如果扫描范围较大将会花费较长时间,请稍等...";
		var endMess = "扫描完成!";
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
		
        $('#notification-overlay').show().fadeTo(500, 0.66, 
            function() {
               $('#notification-view').show().fadeTo(500, 1);
               $('#notification-container').show();
            });
		$.get('/cgi-bin/scan_ajax.cgi',{'iface':iface,'hunhe':hunhe,'method':scan_method},function(data){
		$('#notification-view').find('.content').html(endMess);
		$('#notification-view').fadeTo(500, 1, function() {
            $('#notification-container').hide()
            $('#notification-overlay').fadeTo(500, 0.66, function() {
                $('#notification-overlay').hide();
                });
        });	
		var names = new Array();
		var values = new Array();
		var strings=data.split("===");
		var len = strings.length;
		var str="";
		var i=0;
		str += "<div><table class='list-legend' width='100%' cellpadding='0' cellspacing='0'><tr><td  class='boldbase'>按IP/MAC : </td><td class='boldbase'><input type='text' id='searches' /></td><td  class='boldbase'><input  class='net_button' type='button' value='查找' onclick=\""+"fuzhu_scan('"+hunhe+"')\" /></td></tr></table></div><div style='padding:5px;margin-top:5px;max-height:450px;overflow:auto;'><table class='ruleslist' width='100%' cellpadding='0' cellspacing='0'><tr><td class='boldbase'><input type='checkbox' id='select_0' onclick='change_value("+i+")'/>全选</td><td  class='boldbase'>IP</td><td class='boldbase'>MAC</td></tr>";
		var color="";
		for(i = 1; i<len; i++){
			var elem = strings[i].split(",");
			var selid="select_"+i;
			if(i%2){color='env';}
			else{color='odd';}
			str +="<tr class='"+color+"'><td><input class='allbox' type='checkbox' id='"+selid+"' onclick='change_value("+i+")'/></td><td>"+elem[0]+"</td><td>"+elem[1]+"</td></tr>";
		}
		if(i == 1){
			str += "<tr class='env'><td colspan='4' ><div style='text-align:center'><img src='/images/pop_warn_min.png' />没有符合条件的扫描结果,请检查扫描条件或搜索条件.</div></td></tr>";
		}
		str +="</table></div><div  style='padding:5px;'><table class='ruleslist' cellpadding='0' cellspacing='0'><tr><td class='boldbase'>绑定到:<select style='width:100px;' id='to_iface' onchange='change_iface()' >"+zone+"</select><input type='button' class='net_button' value='添加' onclick='save_add();' /><input type='button' class='net_button' value='取消' onclick='hide();' /></td></tr></table></div>";
		$(str).appendTo("#infoDiv");
		var heights = $("#infoDiv").height();
		var Bheight=$(window).height();
		heights = parseInt(heights);
		var final_top = (Bheight - heights) / 2;
		$("#infoDiv").css({display:'block',top:final_top});
		$("html").css({overflow:'visible'});
		});
	}
}
function hide(){	
	$("#infoDiv").css({display:'none'});
	$("#cover").css({display:'none'});	
}

function fuzhu_scan(hunhe){
	var hunhe = hunhe;
	var searches = $("#searches").val();
	goto_scan("searched",searches,hunhe);
}

function change_value(value){
	var enable = value;
	var yes_no;
	var iface = $("#to_iface").val();
	var is_on = $("#select_" + value).attr("checked");
	if (enable == 0){
		if(is_on){
			$(".allbox").attr( "checked", true );
		}
		else{
			$(".allbox").attr( "checked", false );
		}
	}
	if(is_on == true || is_on == "checked"){
		yes_no = "on";
	}
	else{
		yes_no = "off";
	}
	$.get('/cgi-bin/scan_ajax.cgi',{enabled:enable,yes_no:yes_no,iface:iface},function(data){
		//alert(data);
	});
}
function change_iface(){
	var num = $("#to_iface").val();
	$.get('/cgi-bin/scan_ajax.cgi',{changeiface:num},function(data){
		//alert(data);
	});
}
function save_add(){
	$.get('/cgi-bin/scan_ajax.cgi',{save:'binding'},function(data){
		var urlvalue=$("#urlvalue").val();
		window.location.href=window.location.href;
	});
}
function validip(str){   
    var ip =   /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}$/;   
    var flag = ip.test(str);
	var ip_0 = /\.0$/;
	if(ip_0.test(str)){
		flag = false;
	}
	return flag;
}
//检测IP合法性的函数end


//检测网段合法性的函数start
function formatIP(ip){
	return (ip+256).toString(2).substring(1); //格式化输出(补零)
}
function validsegment(str){  
	var test = new Array(); 
	test = str.split("/");
	var leng = test.length;
	var ip = test[0];
	var mask = test[1];
	var ip_reg =   /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}$/;
	if (mask < 1 || mask >32 || leng < 2){
		return false;
	}
	else if(!ip_reg.test(ip)){
		return false;
	}
	else{
		var total_str = "";
		var temp = new Array(); 
		temp = ip.split(".");
		for (i = 0;i < 4;i ++){
			temp[i] = parseInt(temp[i]);
			temp[i] = formatIP(temp[i]);
			total_str += temp[i];
		}
		var segment = total_str.substring(mask);
		var all_zero = /^0+$/;
		return all_zero.test(segment);
	}
}
function range_ip(str){
	var temp = str.split("-");
	if(temp.length!=2){
		 return false;
	}
	var startip = temp[0];
	var endip = temp[1];
    var start = startip.split(".");
	var end = endip.split(".");
	var flag = this.compareIP(startip,endip);
	if(this.validip(startip) && flag == -1){
		return this.validip(endip);
	}
	else{
		return false;
	}
}

function compareIP(ipBegin,ipEnd){
	var temp1 = ipBegin.split(".");  
    var temp2 = ipEnd.split(".");     
    for (var i = 0; i < 4; i++)  {  
       temp1[i] = parseInt(temp1[i]);
	   temp2[i] = parseInt(temp2[i]);
	   if (temp1[i]>temp2[i])  {  return 1;  }  
	   else if (temp1[i]<temp2[i]){return -1;}  
   }  
   return 0; 
}