/**author:刘炬隆（liujulong）
date:2014/10/23
**/

var check = new ChinArk_forms();
var object1 = {
   'form_name':'EMAIL_ALARM_FORM',
   'option':{
        'reciver_email':{
            'type':'text',
            'required':'1',
            'check':'mail|',
        },
        'sender_addr_smtp':{
            'type':'text',
            'required':'1',
            'check':'ip|domain',
        },
        'sender_port_smtp':{
            'type':'text',
            'required':'1',
            'check':'port|',
        },
        'sender_email':{
            'type':'textarea',
            'required':'1',
            'check':'mail|',
        },
    }
}

var object2 = {
   'form_name':'EMAIL_ALARM_FORM',
   'option':{
        'reciver_email':{
            'type':'text',
            'required':'1',
            'check':'mail|',
        },
        'sender_addr_smtp':{
            'type':'text',
            'required':'1',
            'check':'ip|domain',
        },
        'sender_port_smtp':{
            'type':'text',
            'required':'1',
            'check':'port|',
        },
        'sender_email':{
            'type':'textarea',
            'required':'1',
            'check':'mail|',
        },
        'account':{
            'type':'text',
            'required':'1',
            'check':'mail|',
        },
        'pwd':{
            'type':'text',
            'required':'1',
            'check':'',
            'ass_check':function(eve){
                                        var msg="";
                                        var viewsize = eve._getCURElementsByName("pwd","input","EMAIL_ALARM_FORM")[0].value;
                                        if (viewsize.length < 1) {
                                        msg = "此项不能为空！";
                                        }
                                        return msg;
                                     }
        },
    }
}
var paging_holder = {
    url: "/cgi-bin/idps_email_alarm.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    change_account_input();
    load_data();
});

function load_data(){
    var sending_data = {
        ACTION: "load_data",
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        paging_holder.detail_data = data_content.detail_data;
        document.getElementById("reciver_email").value = paging_holder.detail_data[0].MAILFROM;
        if(paging_holder.detail_data[1].MAILTO != "" && paging_holder.detail_data[1].MAILTO != null){
            document.getElementById("sender_email").value = paging_holder.detail_data[1].MAILTO.split(",").join("\n");
        }
        document.getElementById("sender_addr_smtp").value = paging_holder.detail_data[2].SMTPADDR;
        document.getElementById("sender_port_smtp").value = paging_holder.detail_data[3].SMTPPORT;
        if(paging_holder.detail_data[5].SMTP_ENABLED == "on"){
            document.getElementById("account").disabled = false;
            document.getElementById("pwd").disabled = false;
            document.getElementById("start").checked="checked";
            //check._main(object2);
        }else{
            document.getElementById("account").disabled=true;
            document.getElementById("pwd").disabled=true;
            //check._main(object1);
        }
        document.getElementById("account").value = paging_holder.detail_data[6].USER;
        document.getElementById("pwd").value = paging_holder.detail_data[7].PASS;
        if(paging_holder.detail_data[4].SMTPSSL == "on"){
            document.getElementById("ssl_start").checked = "checked";
        }
    }

    do_request(sending_data, ondatareceived);
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: paging_holder.url,
        data: sending_data,
        async: false,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}


//启用下面的用户信息输入控制函数
function change_account_input(){
    var cbk_start = document.getElementById("start");
    if(cbk_start.checked == true){
        document.getElementById("account").disabled = false;
        document.getElementById("pwd").disabled = false;
        check._main(object2);
    }else{
        document.getElementById("account").disabled = true;
        document.getElementById("pwd").disabled = true;
        check._main(object1);
    }
}
//发送邮件测试函数
function sending_test_mail(){
    var sending_data = {
        ACTION: "sending_test_mail",
    };
    function ondatareceived(data) {
        if(data == 0){
            alert("邮件发送成功！");
        }else{
            alert("邮件发送失败！");
        }
    }
    do_request(sending_data, ondatareceived);
}
//切换发件人smtp服务器端口
function change_smtp_port(){
    if($("#ssl_start").is(":checked")){
        $("#sender_port_smtp").attr("value","465");
    }else{
        $("#sender_port_smtp").attr("value","25");
    }
}