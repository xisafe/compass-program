/**author:刘炬隆（liujulong）
date:2014/04/17
**/

var check = new ChinArk_forms();
var object1 = {
   'form_name':'SWITCH_LINKAGE_FORM',
   'option':{
        'ip_addr_switch':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
        'port_switch':{
            'type':'text',
            'required':'1',
            'check':'port|',
        },
    }
}
var object2 = {
   'form_name':'SWITCH_LINKAGE_FORM',
   'option':{
        'ip_addr_switch':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
        'port_switch':{
            'type':'text',
            'required':'1',
            'check':'port|',
        },
        'account_switch':{
            'type':'text',
            'required':'1',
            'check':'name|',
        },
        'pwd_switch':{
            'type':'text',
            'required':'1',
            'check':'',
            'ass_check':function(eve){
                                        var msg="";
                                        var viewsize = eve._getCURElementsByName("pwd_switch","input","SWITCH_LINKAGE_FORM")[0].value;
                                        
                                        if (viewsize.length < 1) {
                                        msg = "此项不能为空！";
                                        }
                                        return msg;
                                     }
        },
    }
}
var paging_holder = {
    url: "/cgi-bin/idps_switch_linkage.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    check._main(object1);
    //$(".containter-div").css({"width":"47%","margin-left":"20px","float":"left"});
    load_type();
    load_data();
});

function load_type(){
    var sending_data = {
        ACTION: "load_type",
    };

    function ondatareceived(data) {
        var data_content = eval("("+data+")");
        document.getElementById("switches_type").options.add(new Option(data_content.switch_name_cn,data_content.switch_name_en));
        document.getElementById("linkage_way_switch").options.add(new Option(data_content.linkage_mode.mode_name_cn,data_content.linkage_mode.mode_name_en));
        
    }

    do_request(sending_data, ondatareceived);
}

function load_data(){
    var sending_data = {
        ACTION: "load_data",
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        paging_holder.detail_data = data_content.detail_data;
        document.getElementById("ip_addr_switch").value = paging_holder.detail_data[2].IPADDR;
        document.getElementById("port_switch").value = paging_holder.detail_data[3].PORT;
        if(paging_holder.detail_data[4].VERIFCATION == "on"){
            document.getElementById("start_switch").checked = "checked";
            //check._main(object2);
        }
        document.getElementById("account_switch").value = paging_holder.detail_data[5].USER;
        document.getElementById("pwd_switch").value = paging_holder.detail_data[6].PASS;
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
    var cbk_start = document.getElementById("start_switch");
    if(cbk_start.checked == true){
        document.getElementById("account_switch").disabled = false;
        document.getElementById("pwd_switch").disabled = false;
        check._main(object2);
    }else{
        document.getElementById("account_switch").disabled = true;
        document.getElementById("pwd_switch").disabled = true;
        check._main(object1);
    }
}