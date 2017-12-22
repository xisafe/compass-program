/**author:����¡��liujulong��
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
                                        msg = "�����Ϊ�գ�";
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
            show_error_mesg("�������,���ֹ��ܿ��ܳ����쳣");
        },
        success: ondatareceived
    });
}


//����������û���Ϣ������ƺ���
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
//�����ʼ����Ժ���
function sending_test_mail(){
    var sending_data = {
        ACTION: "sending_test_mail",
    };
    function ondatareceived(data) {
        if(data == 0){
            alert("�ʼ����ͳɹ���");
        }else{
            alert("�ʼ�����ʧ�ܣ�");
        }
    }
    do_request(sending_data, ondatareceived);
}
//�л�������smtp�������˿�
function change_smtp_port(){
    if($("#ssl_start").is(":checked")){
        $("#sender_port_smtp").attr("value","465");
    }else{
        $("#sender_port_smtp").attr("value","25");
    }
}