//author:zhouyuan
//Date:2011-06-01
//function:用于usermanagement.cgi页面的js控制
//modify:2011-07-20


var name_note_ch = "";//当系统语言设置为中文时，显示的警告信息
var name_note_en = "";//当系统语言设置为英文时，显示的警告信息
var psw_note_ch = "";//当系统语言设置为中文时，显示的警告信息
var psw_note_en = "";//当系统语言设置为英文时，显示的警告信息
var repsw_note_ch = "";//当系统语言设置为中文时，显示的警告信息
var repsw_note_en = "";//当系统语言设置为英文时，显示的警告信息
var mail_note_ch = "";//当系统语言设置为中文时，显示的警告信息
var mail_note_en = "";//当系统语言设置为英文时，显示的警告信息
var encrypt = new JSEncrypt();

function encryptFn(){
	if(!encrypt.pKey){ //如果没有加载公钥
		$.ajax({
		type:'POST',
		url:'/cgi-bin/getPublicKey.cgi',
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

$(document).ready(function(){


	$("#change_psw").click(function(){
		//document.getElementById("repswshow").style.display=document.all?"block":"table-row"; //2012.12.13 IE中会出现问题，使用下面的行更改 by wl
		document.getElementById("repswshow").style.display = "table-row";
		$("#psw").css("display","inline");
		$("#change_psw").css("display","none");
		$("#hidden").attr("value","change");
	});
	encryptFn();
});
function forPswMd5() {

	var error_length = check._submit_check(object,check);
	if(error_length>0) {
		return;
	}
	var loginForm = document.getElementById("forPswMd5");
	loginForm.psw.value = encrypt.encrypt(loginForm.psw.value);
	loginForm.re_psw.value = encrypt.encrypt(loginForm.re_psw.value);
	//loginForm.psw.value = $.md5(loginForm.psw.value);
	//loginForm.re_psw.value = $.md5(loginForm.re_psw.value);

}  




