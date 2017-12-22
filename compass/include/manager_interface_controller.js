/**author:刘炬隆（liujulong）
date:2014/05/30
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'MANAGENMENT_MOUTH_FORM',
   'option':{
        'management_ip':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
    }
}
var paging_holder = {
    url: "/cgi-bin/interface_manager.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    check._main(object);
    //load_data();
    //init_data();
});

function load_data(){
    var sending_data = {
        ACTION: "load_data",
    };

    function ondatareceived(data) {
        //debugger;
        var data_content = JSON.parse(data);
        paging_holder.detail_data = data_content.detail_data;
        paging_holder.states_all = data_content.states;
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


function init_data(){
    var data = paging_holder.detail_data;
    document.getElementById("management_ip").value = data[1].IPADDR;
    document.getElementById("netmask").value = data[2].NETMASK;
    
    
}
