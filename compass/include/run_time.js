//author:zhouyuan
//Date:2011-07-09
//function:用于footer.cgi页面的js控制
var last_1_state = 4;
var last_2_state = 4;
var last_3_state = 4;

var last_1_status = 200;
var last_2_status = 200;
var last_3_status = 200;

var shut_up = 0;

var Cookie=new Object();
Cookie.setCookie=function(name,value,option){
	//用于存储赋值给document.cookie的cookie格式字符串
	var str=name+"="+escape(value); 
	if(option){
		//如果设置了过期时间
		if(option.expireDays){
			var date=new Date();
			var ms=option.expireDays*24*3600*1000;
			date.setTime(date.getTime()+ms);
			str+="; expires="+date.toGMTString();
		}
		if(option.path)str+="; path="+option.path;   //设置访问路径
		if(option.domain)str+="; domain"+option.domain; //设置访问主机
		if(option.secure)str+="; true";    //设置安全性
	}
	document.cookie=str;
}
Cookie.getCookie=function(name){
	var cookieArray=document.cookie.split("; "); //得到分割的cookie名值对
	var cookie=new Object();
	for(var i=0;i<cookieArray.length;i++){
		var arr=cookieArray[i].split("=");    //将名和值分开
		if(arr[0] == name)return unescape(arr[1]); //如果是指定的cookie，则返回它的值
	}
	return "";
}
Cookie.deleteCookie=function(name){
	var hosts = document.location.host;
	var temp = hosts.split(":");
	var ip = temp[0];
	this.setCookie(name,"",{expireDays:-1,path:"/",domain:ip}); //将过期时间设置为过去来删除一个cookie
}

var request = false;
   try {
     request = new XMLHttpRequest();
   } catch (trymicrosoft) {
     try {
       request = new ActiveXObject("Msxml2.XMLHTTP");
     } catch (othermicrosoft) {
       try {
         request = new ActiveXObject("Microsoft.XMLHTTP");
       } catch (failed) {
         request = false;
       }  
     }
   }
   
   
// $(document).ready(function(){
// 	setInterval(getCustomerInfo,3300);//时间设定为3300ms是确保10s的掉电重新认证和3.3s的不同用户登录合并
// 	setInterval(read_runtime,30000);//每隔30秒去读一遍系统运行事件
//     getCustomerInfo();
// });
window.parent.parent.document.onreadystatechange=function(){
	if (window.parent.parent.document.readyState == 'complete') {
		setInterval(getCustomerInfo,3300);//时间设定为3300ms是确保10s的掉电重新认证和3.3s的不同用户登录合并
		setInterval(read_runtime,30000);//每隔30秒去读一遍系统运行事件
    	getCustomerInfo();
	}
}



function getCustomerInfo() {
     var url = "/cgi-bin/main.cgi";
     request.open("GET", url, true);
     request.onreadystatechange = check_server_state;
     request.send(null);
	 if(document.all)//判断是否为IE浏览器
	 {
		if(last_1_state<4 && last_2_state<4 && last_3_state<4)//上三次的状态都没有完成，确认为服务器挂了
		{
			Cookie.deleteCookie("ee11cbb19052e40b07aac0ca060c23ee");
			parent.window.document.location.href = "https://"+document.location.host;
		}
	 }
	 else{
		if(last_1_status!= 200 && last_2_status!= 200 && last_3_status!= 200)//上三次的状态都没成功，确认为服务器挂了
		{
			Cookie.deleteCookie("ee11cbb19052e40b07aac0ca060c23ee");
			parent.window.document.location.href = "https://"+document.location.host;
		}
	 }
	 // 判断当前cookie和界面的用户是否统一，不统一则刷新非cookie用户的界面，使其统一
	 var obj = window.parent.document.getElementById('topFrame').contentDocument;
	if (obj == null) {return;}
	 var userDom = obj.getElementById('now_user');
	 var val;
	 if( userDom){
	 	val = userDom.innerHTML;
	 }else{
	 	//ie 和 ie8
	 	var temp = window.parent.document.frames['topFrame'].document.getElementById("now_user");
	 	if( temp){
	 		val = temp.value;
	 	}else{
	 		val = window.parent.window.document.getElementById("topFrame").contentWindow.now_user.innerHTML; //ie8;
	 	}
	 	
	 }
	 var sending_data={
	 	action:'get_user_status',
	 	val:val
	 }
	 function check_cookie_user(data) {
	 	if (data != '0') {
	 		parent.window.document.location.href = "https://"+document.location.host;
	 	}
	 }
	 do_ajax_request(sending_data,check_cookie_user);
}
   
   
function check_server_state() 
{
	last_1_state = last_2_state;
	last_2_state = last_3_state;
	last_3_state = request.readyState;
	
	if (request.readyState == 4)
	{
		if (request.status != 0) {
			last_1_status = last_2_status;
			last_2_status = last_3_status;
			last_3_status = request.status;
		}
	}
}
   
   
function read_runtime()
{

	var is_alert = 0;
	//ajax异步从footer_runtime.cgi获取系统运行时间
	var xmlhttp = $.get('/cgi-bin/footer_runtime.cgi', {}, function(data){
		// console.log(data);
		var time_arry = data.split("=");
		$("#day").text(time_arry[0]);//更新天
		$("#hour").text(time_arry[1]);//更新小时
		$("#min").text(time_arry[2]);//更新分钟
		$("#run_time").text(time_arry[3]);//更新系统当前时间
		$("#hostname").text(time_arry[4]);//更新主机名
		if(parseInt(time_arry[5])>=0 && !is_alert)//表示超时
		{
			is_alert = 1;
			Cookie.deleteCookie("ee11cbb19052e40b07aac0ca060c23ee");
			//显示超时退出登录信息
			parent.alert("登陆超时，请重新登录，如有疑问，请联系系统管理员。");
			parent.location.href = "https://"+parent.location.host;
		}
	});
}
//AJAX异步请求数据
function do_ajax_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/footer_runtime.cgi',
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request) {
            // parent.alert("网络错误,部分功能可能出现异常,请重新登录");
            console.log("网络错误,部分功能可能出现异常");
            // Cookie.deleteCookie("ee11cbb19052e40b07aac0ca060c23ee");
            // parent.location.href = "https://"+parent.location.host;
        },
        success: ondatareceived
    });
}