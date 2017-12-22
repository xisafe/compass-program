/**author:刘炬隆（liujulong）
date:2015/04/07
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'BASIC_WEBFILTER_FORM',
   'option':{
        'BYPASS_SOURCE':{
            'type':'textarea',
            'required':'0',
            'check':'ip|ip_mask|mac',
            'ass_check':function(eve){
                
            }
        },
        'BYPASS_DESTINATION':{
            'type':'textarea',
            'required':'0',
            'check':'ip|ip_mask|mac',
            'ass_check':function(eve){
                
            }
        }
    }
}
var paging_holder = {
    url: "/cgi-bin/basic_webfilter.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    check._main(object);
    change_show_lasttr();
    check_running();
});
//控制最后一列显示与否
function change_show_lasttr(){
    if($("#WHITELIST").attr("checked")){
        $(".ctr_last").show();
    }else{
        $(".ctr_last").hide();
    }
}

var check_interval = 5000;

function request_for_json( sending_data, ondatareceived ) {
    var url = "/cgi-bin/basic_webfilter.cgi";
    $.ajax({
        type: 'POST',
        url: url,
        async:false,
        data: sending_data,
        dataType: 'json',
        success: ondatareceived
    });
}

function check_running() {
    var sending_data = {
        ACTION: "check_running"
    }

    function ondatareceived( response ) {
        if ( response.running == 1 ) {
            RestartService("正在应用基本配置，请耐心等待.....");
            window.setTimeout( timing_check_running, check_interval );
        }
    }

    request_for_json( sending_data, ondatareceived );
}

function timing_check_running() {
    var sending_data = {
        ACTION: "check_running"
    }

    function ondatareceived( response ) {
        if ( response.running == 1 ) {
            window.setTimeout( timing_check_running, check_interval );
        }else {
            endmsg("配置应用成功");
        }
    }

    request_for_json( sending_data, ondatareceived );
}