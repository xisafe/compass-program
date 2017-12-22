//author:zhouyuan
//Date:2011-07-20
//function:用于index.cgi页面的js控制

$(document).ready(function(){

	var height_explorer = document.documentElement.clientHeight||window.innerHeight;
	var width_explorer = document.documentElement.clientWidth||window.innerWidth;
	$("#input_text_user").on("focus",userNameFocus);
	$("#input_text_user").on("blur",userNameBlur);

	var version = CheckBrowser();
	if(width_explorer > 1024)
	{
		$(".login_div").css("width","480px");
		
		if(version == "IE6_DOWN")
		{
			$(".login_div").css("margin-left",width_explorer-900+"px");
			//$(".main_div").css("padding-top","300px");//height_explorer*0.35+"px");
		}else{
			$(".login_div").css("margin-left",width_explorer-480+"px");
			//$(".main_div").css("padding-top","300px");//height_explorer*0.35+"px");
		}
	}else{
		$(".login_div").css("width","360px");
		if(version == "IE6_DOWN")
		{
			if(width_explorer > 800)
			{
				$(".login_div").css("margin-left",width_explorer-700+"px");
			}else{
				$(".login_div").css("margin-left",width_explorer-565+"px");
			}
			//$(".main_div").css("padding-top","300px");//height_explorer*0.35+"px");
		}else{
			$(".login_div").css("margin-left",width_explorer-360+"px");
			//$(".main_div").css("padding-top","300px");//height_explorer*0.35+"px");
		}
	}

	
	
	//判断当前浏览器是否启用了cookie
	if(navigator.cookieEnabled == false)
	{
		//alert(navigator.cookieEnabled);
		$("#error-cookie").remove();
		var str = '<div id="error-cookie"><span><img src="/images/pop_error.png" />当前浏览器cookie未开启，请开启后再登陆本系统</span></div>';
		$(str).appendTo("body");
	}else{
		$("#error-div-cookie").remove();
	}


	$("#error-div").fadeOut(10000);//错误提示层消失

	// //用于登陆框鼠标焦点获得时输入框的效果变化
	// 	$("#input_text_user").focus(function(){
	// 		 $(this).css("background-image","url(/images/user_on.gif)");
	// 		 $("#input_text_psw").css("background-image","url(/images/psw_off.gif)")
	// 	});
		
	// 	$("#input_text_psw").focus(function(){
	// 		 $(this).css("background-image","url(/images/psw_on.gif)");
	// 		 $("#input_text_user").css("background-image","url(/images/user_off.gif)");
	// 	});
	//---end---//

	//阻止浏览器存储密码
	if(isIE()) {

		if(versionFlag == "IE7" || versionFlag == "IE8" || versionFlag == "0") {

			$("#input_text_psw").on("focus", function() {
				$("#textOrPsw").html('<input id="input_text_psw" name="pswView" type="password" oncopy="return false;" onpaste="return false;" oncut="return false;">');
				$("#input_text_psw").focus();
			});	
		}else { 
			document.getElementById("input_text_psw").addEventListener("focus", function() {this.type = "password"; }); 
		}
			$("#input_text_psw").on("focus", textForPasswordIE);		
	}else {
		
		if(versionFlag == "Chrome") {
			document.getElementById("input_text_psw").addEventListener("focus", function() {this.type = "password"; });
		}else {
			$("#input_text_psw").on("keydown", forKeydown);
			$("#input_text_psw").on("input", textForPassword);
		}
	}
	$('#write_info').show();
	encryptFn();
});


window.onload=function(){
	check_explorer();
}

//判断浏览器版本
var versionFlag = ieVersion();
var encrypt = new JSEncrypt();

function encryptFn(){
	if(!encrypt.pKey){ //如果没有加载公钥
		$.ajax({
		type:'POST',
		url:'/index.cgi',
		async:true,
		data:{'ACTION':'getPublicKey'},
		success:function(data){
			encrypt.pKey = data;
			encrypt.setPublicKey(encrypt.pKey);
		},
		error:function(){
			alert('网络错误,管理员配置功能将无效！');
		}
	});
	}
}

function CheckBrowser()
{
  var app=navigator.appName;
  var verStr=navigator.appVersion;
  if (app.indexOf('Netscape') != -1) {
    //alert("阿里西西WEB开发友情提示：\n    你使用的是Netscape浏览器或火狐浏览器。");
	return "firefox";
  }
  else if (app.indexOf('Microsoft') != -1) {
    if (verStr.indexOf("MSIE 3.0")!=-1 || verStr.indexOf("MSIE 4.0") != -1 || verStr.indexOf("MSIE 5.0") != -1 || verStr.indexOf("MSIE 5.1") != -1 || verStr.indexOf("MSIE 6.0") != -1) {
	  return "IE6_DOWN";
    } else {return "IE6_UP";}
  }
}

//用于判断当前用户使用的浏览器版本，并给予响应提示
function check_explorer()
{
	var version = CheckBrowser();
	if(version == "IE6_DOWN")
	{
		$.get('/cgi-bin/login_note.cgi', {read:"read"}, function(data){
			if(data == "yes")
			{
				var str = "<div class='version_div' style='display:none;'><div>系统检测您当前使用的浏览器版本过低，为了不影响您正常使用本系统，建议您升级浏览器至IE7及其以上版本，或者使用firefox浏览器。<input id='if_choice' type='checkbox' />不再提醒  <input type='button' value='我知道了'     onclick='close_note()' class='net_button'  /></div></div>";
				$(str).appendTo("body");
				window.setTimeout(show,1000);
			}
		});
	}
}

function show()
{
	$(".version_div").slideDown("slow");
}

function close_note()
{
	//alert(document.getElementById('if_choice').checked);
	if(document.getElementById('if_choice').checked == true)
	{
		$.get('/cgi-bin/login_note.cgi', {write:"write"}, function(data){

		});
	}
	$(".version_div").slideUp("slow");
}
function userNameFocus() {
	$("#input_text_user_div").css("border","1px solid #3091f2");
	$("#input_text_user_div img").attr("src","../images/login_user.png");
}
function userNameBlur() {
	$("#input_text_user_div").css("border","1px solid #d6d6d6");
	$("#input_text_user_div img").attr("src","../images/login_user_gray.png");	
}

function forLoginMd5() {
	if($("#psw").val() == "") {
		$("#psw").val( $("#input_text_psw").val() );
	}
	if(versionFlag == "IE7" || versionFlag == "IE8" || versionFlag == "0") {
		$("#textOrPsw").html('<input id="input_text_psw" name="pswView" type="text" oncopy="return false;" onpaste="return false;" oncut="return false;">');
	}
	$("#input_text_psw").val("");
	var loginForm = document.getElementById("forLogin");
	if( /[~!@#$%^&*()]/.test(loginForm.psw.value) ) {
		alert("非法输入!!!");
		loginForm.psw.value = "";
		return false;
	}else {
		loginForm.psw.value = encrypt.encrypt(loginForm.psw.value);;
		// loginForm.psw.value = $.md5(loginForm.psw.value);
		return navigator.cookieEnabled;
	}
}

//监听keydown事件
var cursorStart = 0;
var cursorEnd = 0;
var inputFlag = true;
var selectFlag = true;
function forKeydown(){

		cursorStart = $("#input_text_psw")[0].selectionStart;
		cursorEnd = $("#input_text_psw")[0].selectionEnd;	
}

//text模拟password
function textForPassword() {
	var loginForm = document.getElementById("forLogin");
	var view = loginForm.pswView.value.split("");
	var post = loginForm.psw.value.split("");
	var start = $("#input_text_psw")[0].selectionStart;
	var length = Math.abs( cursorEnd - cursorStart );
	if(length == 0) {
		if(view.length < post.length){
			post.splice(start,1);
		}else {
			post.splice(start-1,0,view[start-1]);
		}
	}else {
		if(view.length < post.length){
			post.splice(start,length);
		}else {
			post.splice(start-1,length,view[start-1]);
		}
	}
	// if(view.length < post.length ) {
		// length = 0;
		// cha = view[start-1];
	// }else if(view.length > post.length){
		// length = 0;
		// cha = view[start-1];
	// }
	// post.splice(start,length,cha);
	var viewPsdValue = "";
	var psdValue = "";
	for(var i = 0; i < post.length; i++) {
		viewPsdValue += "*";
	}
	psdValue = post.join("");
	loginForm.pswView.value = viewPsdValue;
	loginForm.psw.value = psdValue;
	
	$("#input_text_psw")[0].selectionStart = start;
	$("#input_text_psw")[0].selectionEnd = start;

}

function textForPasswordIE() {
	if(versionFlag == "IE7" || versionFlag == "IE8" || versionFlag == "0") {
		console.log("IE8");
	    $("#textOrPsw").html('<input id="input_text_psw" name="pswView" type="password" oncopy="return false;" onpaste="return false;" oncut="return false;">');
	    $("#input_text_psw").focus();
	}else{ 
		console.log("IE8+");
		$("#input_text_psw")[0].type = "password"; 
	}
}


function ieVersion() {
 
	var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串  
	var isOpera = userAgent.indexOf("Opera") > -1; //判断是否Opera浏览器  
	var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera; //判断是否IE浏览器  
	var isEdge = userAgent.indexOf("Windows NT 6.1; Trident/7.0;") > -1 && !isIE; //判断是否IE的Edge浏览器  
	var isFF = userAgent.indexOf("Firefox") > -1; //判断是否Firefox浏览器  
	var isSafari = userAgent.indexOf("Safari") > -1 && userAgent.indexOf("Chrome") == -1; //判断是否Safari浏览器  
	var isChrome = userAgent.indexOf("Chrome") > -1 && userAgent.indexOf("Safari") > -1; //判断Chrome浏览器  
	
	if (isIE) {  
		var reIE = /MSIE\s([0-9]+)\.[0-9]+/;  
		reIE.test(userAgent);  
		var fIEVersion = parseFloat(RegExp["$1"]);  
		if(fIEVersion == 7)  
		{ return "IE7";}  
		else if(fIEVersion == 8)  
		{ return "IE8";}  
		else if(fIEVersion == 9)  
		{ return "IE9";}  
		else if(fIEVersion == 10)  
		{ return "IE10";}  
		else if(fIEVersion == 11)  
		{ return "IE11";}  
		else  
		{ return "0"}//IE版本过低  
	}//isIE end  
         
	if (isFF) {  return "FF";}  
	if (isOpera) {  return "Opera";}  
	if (isSafari) {  return "Safari";}  
	if (isChrome) { return "Chrome";}  
	if (isEdge) { return "Edge";}  
  
}

function isIE() { //ie?  
    if (!!window.ActiveXObject || "ActiveXObject" in window) {  
		return true; 
	}
    else {  
		return false; 
	}  
}  




//AJAX异步请求数据
// function do_request(sending_data, ondatareceived) {
	// $.ajax({
        // type: 'POST',
        // url: ass_url,
        // data: sending_data,
        // async: false,
        // error: function(request){
            // alert("网络错误,部分功能可能出现异常");
        // },
        // success: ondatareceived
    // });
// }



