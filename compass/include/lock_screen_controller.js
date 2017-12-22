$(document).ready(function(){
    register_listeners();
    check_form._main(edit_pwd_object);
    window.setTimeout( lock_check, 1000); //过会儿去检测，不然有些东西没准备好
	if(document.getElementById("psdLength")) {
		psdLength = document.getElementById("psdLength").value;



    $(window).resize(function(){
        if ($("#eidt_passwd_bg").css("display") == 'block'){
            var cover_height = parseInt(document.getElementById('eidt_passwd_bg').offsetHeight);
            var cover_width = parseInt(document.getElementById('eidt_passwd_bg').offsetWidth);

            var border_height = parseInt(document.getElementById('eidt_passwd_bbb').offsetHeight);
            var border_width = parseInt(document.getElementById('eidt_passwd_bbb').offsetWidth);

            var temp_top = (cover_height - border_height)/2 - 78;
            var temp_left = (cover_width - border_width)/2;

            document.getElementById('eidt_passwd_bbb').style.top = temp_top + 'px';
            document.getElementById('eidt_passwd_bbb').style.marginTop = 0 + 'px';
            document.getElementById('eidt_passwd_bbb').style.left = temp_left + 'px';
            document.getElementById('eidt_passwd_bbb').style.marginLeft = 0 + 'px';
        }

    })


	}

    encryptFn();
});
var psdLength = 8;//默认密码长度
var edit_pwd_object = {
   'form_name':'EDIT_PASSWD_FORM',
   'option'   :{
        // 'primary_passwd':{
        //     'type':'text'
        //     'required':'1',
        //     'check':'other|',
        //     'other_reg':'!/^\$/',
        // },
        'new_passwd':{
            'type':'text',
            'is_transparent_border':'1',
            'required':'1',
            'check':'other|',
            'other_reg':'!/^\$/',
            'ass_check':function(eve){
                $.ajax({
                    type : "post",
                    url : '/cgi-bin/center.cgi',
                    async : false,
                    data : {'ACTION':'getPasswordLength'},
                    dataType:'text',
                    success : function(data){
                        psdLength = data;
                    }
                });
                var psw =eve._getCURElementsByName("new_passwd","input","EDIT_PASSWD_FORM")[0].value; 
                var msg = "";
                if(psw.length < parseInt(psdLength) ){
                    var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
                    var edit_passwd_height = mainframe.document.getElementById("eidt_passwd_body").offsetHeight;
                    mainframe.document.getElementById("eidt_passwd_bbb").style.height = edit_passwd_height + 'px';
                    msg = "密码长度不能小于" + psdLength + "位！";
                }else if(psw.length >50){
                    msg = "密码长度不能大于" + 50 + "位！";
                }
                else if( (/^\d+$/.test(psw)) || (!/\d/.test(psw)) ){
                    var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
                    var edit_passwd_height = mainframe.document.getElementById("eidt_passwd_body").offsetHeight;
                    mainframe.document.getElementById("eidt_passwd_bbb").style.height = edit_passwd_height + 'px';
                    msg="密码不能只有数字或者字母，必须包含数字及字母！";
                }
                return msg;
            }
        },
        'confirm_passwd':{
            'type':'text',
            'required':'1',
            'is_transparent_border':'1',
            'check':'other|',
            'other_reg':'!/^\$/',
            ass_check: function() {
                var new_passwd = $( "#new_passwd" ).val();
                var confirm_passwd = $( "#confirm_passwd" ).val();
                if ( new_passwd != confirm_passwd ) {
                    var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
                    var edit_passwd_height = mainframe.document.getElementById("eidt_passwd_body").offsetHeight;
                    mainframe.document.getElementById("eidt_passwd_bbb").style.height = edit_passwd_height + 'px';
                    return "两次密码不一致";
                }
           }
        },
    }
}
var check_form = new ChinArk_forms();
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
function register_listeners() {
    $( "#reset_edit_button" ).click( hide_edit_passwd );
}


function show_edit_passwd() {
    var bottomframe = window.parent.parent.document.getElementById("bottomFrame").contentWindow;
    var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
    var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;

    bottomframe.document.getElementById("div_lock_footer").style.display = "block";
    if(mainframe.document.getElementById("eidt_passwd_bbb").style.display == 'none'){
        topframe.document.getElementById("div_lock_top").style.display = "none";
    }
    else{
        topframe.document.getElementById("div_lock_top").style.display = "block";
    }
    mainframe.document.getElementById("eidt_passwd_bg").setAttribute('class','open-dialog__overlay');
    mainframe.document.getElementById("eidt_passwd_bbb").setAttribute('class','open--eidt_passwd_bbb');
    mainframe.document.getElementById("eidt_passwd_body").style.display = "block";
}

function hide_edit_passwd() {
    var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
    mainframe.document.getElementById("eidt_passwd_bg").setAttribute('class','dialog__overlay');

    setTimeout(function() {
        mainframe.document.getElementById("eidt_passwd_bg").style.display = 'none';
        mainframe.document.getElementById("eidt_passwd_body").style.display = "none";
    },700);

    var bottomframe = window.parent.parent.document.getElementById("bottomFrame").contentWindow;
    bottomframe.document.getElementById("div_lock_footer").style.display = "none";
    var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;
    topframe.document.getElementById("div_lock_top").style.display = "none";
}

function do_request(sending_data, ondatareceived) {
    var csrfpId = $( "input[name=csrfpId]" ).val();
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/lock_screen_check.cgi",
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            //alert("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived,
        beforeSend: function(request) {
            if ( csrfpId ) {
                request.setRequestHeader( "csrfpId", csrfpId );
            }
        }
    });
}

//锁屏与否判断函数
function lock_check(){
    var sending_data = {
        ACTION: "lock_check"
    };
    function ondatareceived(data) {
        if(data.status != 0){
            $( "#have_to_mesg" ).text( data.mesg );
            // document.getElementById( "reset_edit_button" ).disabled = true;
            // console.log('showing..')
            // console.log(data)
            show_edit_passwd();
            var cover_height = parseInt(document.getElementById('eidt_passwd_bg').offsetHeight);
            var cover_width = parseInt(document.getElementById('eidt_passwd_bg').offsetWidth);

            var border_height = parseInt(document.getElementById('eidt_passwd_bbb').offsetHeight);
            var border_width = parseInt(document.getElementById('eidt_passwd_bbb').offsetWidth);

            var temp_top = (cover_height - border_height)/2 - 78;
            var temp_left = (cover_width - border_width)/2;

            document.getElementById('eidt_passwd_bbb').style.top = temp_top + 'px';
            document.getElementById('eidt_passwd_bbb').style.marginTop = 0 + 'px';
            document.getElementById('eidt_passwd_bbb').style.left = temp_left + 'px';
            document.getElementById('eidt_passwd_bbb').style.marginLeft = 0 + 'px';
            
            var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
            var edit_passwd_height = mainframe.document.getElementById("eidt_passwd_body").offsetHeight;
            mainframe.document.getElementById("eidt_passwd_bbb").style.height = edit_passwd_height + 'px';

        }else{
            hide_edit_passwd();
        }
    }
    do_request(sending_data, ondatareceived);
}

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

function do_edit_passwd() {
    var check_result = check_form._submit_check( edit_pwd_object, check_form );
    if ( check_result ) {
        // 错误数大于0
    var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
    var edit_passwd_height = mainframe.document.getElementById("eidt_passwd_body").offsetHeight;
    mainframe.document.getElementById("eidt_passwd_bbb").style.height = edit_passwd_height + 'px';
        return;
    }

    var primary_passwd = $( "#primary_passwd" ).val();
	// var primary_passwd_md5 = $.md5( primary_passwd );
    var primary_passwd_ = encrypt.encrypt(primary_passwd);
    var new_passwd = $( "#new_passwd" ).val();
    // var new_passwd_md5 = $.md5( new_passwd );
	var new_passwd_ = encrypt.encrypt( new_passwd );
    var confirm_passwd = $( "#confirm_passwd" ).val()

    var sending_data = {
        ACTION: 'change_passwd',
        primary_passwd: primary_passwd_,
        new_passwd: new_passwd_,
    }

    function ondatareceived(data) {
        if(data.status == 0){
            hide_edit_passwd();
            Cookie.deleteCookie("ee11cbb19052e40b07aac0ca060c23ee");
            // //显示超时退出登录信息
            window.parent.alert("修改密码成功，请重新登录.");
            window.top.location.href = "https://"+window.parent.location.host;
        }else{
            window.parent.alert( data.mesg );
        }
    }
    do_request(sending_data, ondatareceived);
}
