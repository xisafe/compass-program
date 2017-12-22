/**author:����¡��liujulong��
date:2014/12/05
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'AUTH_SETTING_FORM',
   'option':{
        'IP_SELECTED':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                var mesg = "";
                var val_ip = $("#IP_SELECTED").val();
                if(val_ip == ""){
                    mesg = "����д��ȷ��IP��ַ";
                };
                var temp = val_ip.split("\n");
                var new_arry = temp.sort();
                for(var i=0;i<(temp.length);i++){
                    if(new_arry[i] == ""){
                        mesg = "����д��ȷ��IP��ַ";
                        break;
                    }
                    if(new_arry[i] == new_arry[i+1]){
                        mesg = "IP��ַ�ظ�";
                        break;
                    }
                    /* if(i > 0){
                        if(temp[i-1] == temp[temp.length-1]){
                            mesg = "IP��ַ�ظ�";
                            break;
                        }
                    } */
                }
                return mesg;
            }
        },
        'IP_SOURCE':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                var mesg = "";
                var val_ip = $("#IP_SOURCE").val();
                var temp = val_ip.split("\n");
                var new_arry = temp.sort();
                for(var i=0;i<(temp.length);i++){
                    if(new_arry[i] == ""){
                        mesg = "����д��ȷ��IP��ַ";
                        break;
                    }
                    if(new_arry[i] == new_arry[i+1]){
                        mesg = "IP��ַ�ظ�";
                        break;
                    }
                }
                return mesg;
            }
        },
        'Timeout':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var Timeout = eve._getCURElementsByName("Timeout","input","AUTH_SETTING_FORM")[0].value;
                if (Timeout < 30 || Timeout > 60 ){
                    msg = "����д30-60������";
                }
                return msg;
            }
        },
        'Forbid':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var Forbid = eve._getCURElementsByName("Forbid","input","AUTH_SETTING_FORM")[0].value;
                if (Forbid < 10 || Forbid > 60 ){
                    msg = "����д10-60������";
                }
                return msg;
            }
        }
    }
}
var object1 = {
   'form_name':'AUTH_SETTING_FORM',
   'option':{
        'IP_SELECTED':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                var mesg = "";
                var val_ip = $("#IP_SELECTED").val();
                var temp = val_ip.split("\n");
                var new_arry = temp.sort();
                for(var i=0;i<(temp.length);i++){
                    if(new_arry[i] == ""){
                        mesg = "����д��ȷ��IP��ַ";
                        break;
                    }
                    if(new_arry[i] == new_arry[i+1]){
                        mesg = "IP��ַ�ظ�";
                        break;
                    }
                }
                return mesg;
            }
        },
        'IP_SOURCE':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                var mesg = "";
                var val_ip = $("#IP_SOURCE").val();
                var temp = val_ip.split("\n");
                var new_arry = temp.sort();
                for(var i=0;i<(temp.length);i++){
                    if(new_arry[i] == ""){
                        mesg = "����д��ȷ��IP��ַ";
                        break;
                    }
                    if(new_arry[i] == new_arry[i+1]){
                        mesg = "IP��ַ�ظ�";
                        break;
                    }
                }
                return mesg;
            }
        },
        'Timeout':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var Timeout = eve._getCURElementsByName("Timeout","input","AUTH_SETTING_FORM")[0].value;
                if (Timeout < 30 || Timeout > 60 ){
                    msg = "����д30-60������";
                }
                return msg;
            }
        },
        'Forbid':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var Forbid = eve._getCURElementsByName("Forbid","input","AUTH_SETTING_FORM")[0].value;
                if (Forbid < 10 || Forbid > 60 ){
                    msg = "����д10-60������";
                }
                return msg;
            }
        },
        'RADIUS_server_ip':{
            'type':'text',
            'required':'1',
            'check':'ip|',
            'ass_check':function(eve){
                
            }
        },
        'RADIUS_SKEY':{
            'type':'password',
            'required':'1',
            'check':'other',
            'other_reg':'!/^\$/',
            'ass_check':function(eve){
                
            }
        },
        'RADIUS_port_auth':{
            'type':'text',
            'required':'1',
            'check':'port|',
            'ass_check':function(eve){
                
            }
        },
        'RADIUS.RADIUS_PPORT':{
            'type':'text',
            'required':'1',
            'check':'port|',
            'ass_check':function(eve){
                
            }
        },
        'RADIUS_timeout':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var timeout = $("#RADIUS_timeout").val();
                if (timeout < 5 || timeout > 20 ){
                    msg = "����д5-20������";
                }
                return msg;
            }
        },
        'RADIUS_time_resend':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var time_resend = $("#RADIUS_time_resend").val();
                if (time_resend < 3 || time_resend > 5 ){
                    msg = "����д3-5������";
                }
                return msg;
            }
        }
    }
}
var object2 = {
   'form_name':'AUTH_SETTING_FORM',
   'option':{
        'IP_SELECTED':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                var mesg = "";
                var val_ip = $("#IP_SELECTED").val();
                var temp = val_ip.split("\n");
                var new_arry = temp.sort();
                for(var i=0;i<(temp.length);i++){
                    if(new_arry[i] == ""){
                        mesg = "����д��ȷ��IP��ַ";
                        break;
                    }
                    if(new_arry[i] == new_arry[i+1]){
                        mesg = "IP��ַ�ظ�";
                        break;
                    }
                }
                return mesg;
            }
        },
        'IP_SOURCE':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                var mesg = "";
                var val_ip = $("#IP_SOURCE").val();
                var temp = val_ip.split("\n");
                var new_arry = temp.sort();
                for(var i=0;i<(temp.length);i++){
                    if(new_arry[i] == ""){
                        mesg = "����д��ȷ��IP��ַ";
                        break;
                    }
                    if(new_arry[i] == new_arry[i+1]){
                        mesg = "IP��ַ�ظ�";
                        break;
                    }
                }
                return mesg;
            }
        },
        'Timeout':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var Timeout = eve._getCURElementsByName("Timeout","input","AUTH_SETTING_FORM")[0].value;
                if (Timeout < 30 || Timeout > 60 ){
                    msg = "����д30-60������";
                }
                return msg;
            }
        },
        'Forbid':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var Forbid = eve._getCURElementsByName("Forbid","input","AUTH_SETTING_FORM")[0].value;
                if (Forbid < 10 || Forbid > 60 ){
                    msg = "����д10-60������";
                }
                return msg;
            }
        },
        'LDAP_server_ip':{
            'type':'text',
            'required':'1',
            'check':'ip|',
            'ass_check':function(eve){
                
            }
        },
        'LDAP_port':{
            'type':'text',
            'required':'1',
            'check':'port|',
            'ass_check':function(eve){
                
            }
        },
        'LDAP_BaseDN':{
            'type':'text',
            'required':'1',
            'check':'other',
            'other_reg':'!/^\$/',
            'ass_check':function(eve){
                
            }
        },
        'LDAP_managerDN':{
            'type':'text',
            'required':'1',
            'check':'other',
            'other_reg':'!/^\$/',
            'ass_check':function(eve){
                
            }
        },
        'LDAP_password_manager':{
            'type':'password',
            'required':'1',
            'check':'other',
            'other_reg':'!/^\$/',
            'ass_check':function(eve){
                
            }
        }
    }
}

$(document).ready(function(){
    check._main(object);
    $("#detail_radius").hide();
    $("#detail_ldap").hide();
    show_detail_method();
});
//��̬����һ��IP
function add_one_ip(){
    var ip_add = $("#IP_ADD").val();
    $("#IP_SELECTED").append("<option selected value="+ip_add+">"+ip_add+"</option>");
}
//��̬ɾ��һ��IP
function delete_selected_ip(){
    $("#IP_SELECTED").find("option:selected").each(function(){
        $(this).remove();
    });
}
//��ʾ��֤��������ϸ��Ϣ
function show_detail_method(){
    var methods = document.getElementsByName("method");
    for(var i = 0;i < methods.length;i++){
        if(methods[i].checked == true){
            if(methods[i].value == "LOCAL"){
                $("#detail_radius").hide();
                $("#detail_ldap").hide();
                check._main(object);
            }else if(methods[i].value == "RADIUS"){
                $("#detail_radius").show();
                $("#detail_ldap").hide();
                if($("#RADIUS_port_auth").val() == ""){
                    $("#RADIUS_server_ip").val("");
                    $("#RADIUS_SKEY").val("");
                }
                check._main(object1);
            }else if(methods[i].value == "LDAP"){
                $("#detail_radius").hide();
                $("#detail_ldap").show();
                check._main(object2);
            }
        }
    }
}
//�첽��������
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/auth_setting.cgi",
        //dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            alert("�������,���ֹ��ܿ��ܳ����쳣");
        },
        success: ondatareceived
    });
}
//��������
function testConn(){
    var method = $("input[name='method']:checked").val();
    var sending_data = "";
    if(method == "RADIUS"){
        sending_data = {
            ACTION: 'testconn',
            method: method,
            RADIUS_server_ip: $("#RADIUS_server_ip").val(),
            RADIUS_SKEY: $("#RADIUS_SKEY").val(),
            RADIUS_port_auth: $("#RADIUS_port_auth").val(),
            RADIUS_PPORT: $("#RADIUS_PPORT").val(),
            RADIUS_timeout: $("#RADIUS_timeout").val(),
            RADIUS_time_resend: $("#RADIUS_time_resend").val()
        };
    }else{
        sending_data = {
            ACTION: 'testconn',
            method: method,
            LDAP_server_version: $("#LDAP_server_version").val(),
            LDAP_server_ip: $("#LDAP_server_ip").val(),
            LDAP_port: $("#LDAP_port").val(),
            LDAP_BaseDN: $("#LDAP_BaseDN").val(),
            LDAP_managerDN: $("#LDAP_managerDN").val(),
            LDAP_password_manager: $("#LDAP_password_manager").val()
        };
    }
    function ondatareceived(data) {
        var state = data.replace("\n","");
        if(state == "0"){
            alert("���ӳɹ���");
        }else{
            alert("����ʧ�ܣ�");
        }
    }
    do_request(sending_data, ondatareceived);
}