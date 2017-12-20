/**author:刘炬隆（liujulong）
date:2014/04/17
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'TEMPLATE_FORM',
   'option':{
        'ip_addr':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
        'user_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
        },
        'snmp_group_character':{
            'type':'text',
            'required':'1',
            'check':'',
            'ass_check':function(eve){
                                        var msg="";
                                        var viewsize = eve._getCURElementsByName("snmp_group_character","input","TEMPLATE_FORM")[0].value;
                                        if (viewsize.length < 1) {
                                        msg = "此项不能为空！";
                                        }
                                        return msg;
                                     }
        },
        'password':{
            'type':'text',
            'required':'1',
            'check':'',
            'ass_check':function(eve){
                                        var msg="";
                                        var viewsize = eve._getCURElementsByName("password","input","TEMPLATE_FORM")[0].value;
                                        if (viewsize.length < 8) {
                                        msg = "请输入超过8位的密码";
                                        }
                                        if (viewsize.length < 1) {
                                        msg = "此项不能为空！";
                                        }
                                        return msg;
                                     }
        },
        'encry_key':{
            'type':'text',
            'required':'1',
            'check':'',
            'ass_check':function(eve){
                                        var msg="";
                                        var viewsize = eve._getCURElementsByName("encry_key","input","TEMPLATE_FORM")[0].value;
                                        if (viewsize.length < 8) {
                                        msg = "请输入超过8位的密钥";
                                        }
                                        if (viewsize.length < 1) {
                                        msg = "此项不能为空！";
                                        }
                                        return msg;
                                     }
        },
    }
}
var paging_holder = {
    url: "/cgi-bin/idps_fw_linkage_setting.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    check._main(object);
    //$(".containter-div").css({"width":"47%","margin-left":"20px","float":"left"});
    load_type();
    load_data();
    //init_data();
});

function load_type(){
    var sending_data = {
        ACTION: "load_type",
    };

    function ondatareceived(data) {
        
        var data_content = eval("("+data+")");
        document.getElementById("firewall_type").options.add(new Option(data_content.fw_name_cn,data_content.fw_name_en));
        document.getElementById("linkage_way").options.add(new Option(data_content.linkage_mode.mode_name_cn,data_content.linkage_mode.mode_name_en));
       
    }

    do_request(sending_data, ondatareceived);
}

function load_data(){
    var sending_data = {
        ACTION: "load_data",
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        if(data_content.detail_data.length == 0){
            change_form();
        }
        paging_holder.detail_data = data_content.detail_data;
        paging_holder.states_all = data_content.states;
        document.getElementById("ip_addr").value = paging_holder.detail_data[2].IPADDR;
        var protocols = document.getElementsByName("snmp_protocol");
        for(var i=0;i<protocols.length;i++){
            if(protocols[i].value == paging_holder.detail_data[3].PROT){
                protocols[i].checked="checked";
                if(protocols[i].value != "V3"){
                    change_form();
                }
            }
        }
        document.getElementById("group").value = paging_holder.detail_data[4].SNMP_COMMUNITY_STRING;
        //debugger;
        document.getElementById("uname").value = paging_holder.detail_data[5].USER;
        var levels = document.getElementsByName("auth_level");
        for(var i=0;i<levels.length;i++){
            if(levels[i].value == paging_holder.detail_data[6].LEVEL){
                levels[i].checked="checked";
                if(levels[i].value == "authPriv"){
                    change_form_auth_encry();
                    //debugger;
                    document.getElementById("pwd").value = paging_holder.detail_data[7].PASS;
                    document.getElementById("auth_method").value = paging_holder.detail_data[8].AUTHEN;
                    document.getElementById("key").value = paging_holder.detail_data[9].PASS_ENCRY;
                    document.getElementById("encry_method").value = paging_holder.detail_data[10].ENCRYT;
                }else if(levels[i].value == "authNoPriv"){
                    change_form_auth_unencry();
                    document.getElementById("pwd").value = paging_holder.detail_data[7].PASS;
                    document.getElementById("auth_method").value = paging_holder.detail_data[8].AUTHEN;
                }else if(levels[i].value == "noAuthNoPriv"){
                    change_form_nolevel();
                }
            }
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

function change_form(){
    document.getElementById("tr_uname").style.display="none";
    document.getElementById("tr_level").style.display="none";
    document.getElementById("tr_pwd").style.display="none";
    document.getElementById("tr_auth").style.display="none";
    document.getElementById("tr_encry_key").style.display="none";
    document.getElementById("tr_encry_method").style.display="none";
}
function change_form_another(){
    document.getElementById("tr_uname").style.display="";
    document.getElementById("tr_level").style.display="";
    document.getElementById("tr_pwd").style.display="";
    document.getElementById("tr_auth").style.display="";
    document.getElementById("tr_encry_key").style.display="";
    document.getElementById("tr_encry_method").style.display="";
}

function change_form_auth_encry(){
    document.getElementById("tr_uname").style.display="";
    document.getElementById("tr_level").style.display="";
    document.getElementById("tr_pwd").style.display="";
    document.getElementById("tr_auth").style.display="";
    document.getElementById("tr_encry_key").style.display="";
    document.getElementById("tr_encry_method").style.display="";
}

function change_form_auth_unencry(){
    document.getElementById("tr_pwd").style.display="";
    document.getElementById("tr_auth").style.display="";
    document.getElementById("tr_encry_key").style.display="none";
    document.getElementById("tr_encry_method").style.display="none";
}
function change_form_nolevel(){
    document.getElementById("tr_pwd").style.display="none";
    document.getElementById("tr_auth").style.display="none";
    document.getElementById("tr_encry_key").style.display="none";
    document.getElementById("tr_encry_method").style.display="none";
}