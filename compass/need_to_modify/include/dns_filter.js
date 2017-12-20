var message_box_config = {
    url: "/cgi-bin/dns_filter.cgi",
    check_in_id: "mesg_box_id",
    panel_name: "message_box"
}

var object_dns = {
   'form_name':'DNS_FILTER_FORM',
   'option':{
        'CLIENT_BYPASS':{
            'type':'textarea',
            'required':'0',
            'check':'ip|mac|ip_mask',
            'ass_check':function(eve){
                
            }
        },
        'SERVER_BYPASS':{
            'type':'textarea',
            'required':'0',
            'check':'ip|ip_mask',
            'ass_check':function(eve){
                
            }
        }
    }
}

var check = new ChinArk_forms();
var message_manager = new MessageManager( message_box_config );
var check_interval = 500;  // 原来写的5000是5秒啊,即5秒才检测一次,而因为脚本启动时间并不长,一般两秒就完成了,所以你的检测频率要变高,变成0.5秒检测一次
var mesg_text = "";


$( document ).ready(function() {
    message_manager.render();
    // message_manager.show_error_mesg( "xixi" );  测试成功
    check._main(object_dns);
    $("#whitelist_id").click(function(){
        if( $("#whitelist_id").attr("checked") ) {
            $("#last_tr_id").show();
        }else{
            $("#last_tr_id").hide();
        }
    });
    $("#save_button_id").click(function(){
        save_data();
    });
    $("#last_tr_id").hide();
    init_load_data();

});


/*function timing_check_running() {
    var sending_data = {
        ACTION: "check_running"
    }
    function ondatareceived( response ) {
        if ( response.running == 1 ) {
            window.setTimeout( timing_check_running, check_interval );
        } else {
            endmsg("规则应用成功");
            // endmsg("接收邮件过滤开启成功");
        }
    }
    request_for_json( sending_data, ondatareceived );
}*/



function save_data(){
    /*var sending_data = {   这里存在严重的问题是你只会传送出去ACTION字段，而form表单里所有的元素都没有被发送出去！
        ACTION: "save_data"  因为你为了自己实现Ajax方式已经把form的onsubmit设置为了‘return false；’了
    }*/
    var sending_data = $("#form_id_for_dns_filter_panel").serialize();
    sending_data += "&ACTION=save_data";
    function onreceived(response){
        if(response.status == 0){
            message_manager.show_note_mesg(response.mesg);
            // init_load_data();
            if ( response['reload'] == 1 ) {
                message_manager.show_apply_mesg("规则已改变，需要重新应用以使规则生效");
            }
        }else{
            message_manager.show_error_mesg(response.mesg);
            $("#form_id_for_dns_filter_panel").reset();
        }
    }

    if ( check._submit_check( object_dns, check ) < 1 ) {
        request_for_json( sending_data, onreceived );
    } else {
        message_manager.show_popup_error_mesg("请正确填写表单");
    }
}


function init_load_data(){
    var sending_data = {
        ACTION: "load_data"
    }
    function onreceived(response){
        if ( response['reload'] == 1 ) {
            message_manager.show_apply_mesg("规则已改变，需要重新应用以使规则生效");
        }
        var detail_data = response.detail_data;
        var dns_enabled = detail_data['DNS_ENABLED'];
        var whitelist   = detail_data['WHITELIST'];
        
        var client_bypass = detail_data['CLIENT_BYPASS'];
        var server_bypass = detail_data['SERVER_BYPASS'];
        if(dns_enabled == 'on'){
            $("#dns_enabled_id").attr("checked",true);
        }else{
            $("#dns_enabled_id").attr("checked",false);
        }

        if(whitelist == 'on') {
            $("#whitelist_id").attr("checked",true);
            $("#last_tr_id").show();
        }else{
            $("#whitelist_id").attr("checked",false);
            // $("#last_tr_id").hide();
        }
        $("div.whitelist_textarea textarea:eq(0)").val(client_bypass);
        $("div.whitelist_textarea textarea:eq(1)").val(server_bypass);
    }
    request_for_json( sending_data, onreceived );
}

function request_for_json( sending_data, ondatareceived ) {
    var url = "/cgi-bin/dns_filter.cgi";
    $.ajax({
        type: 'POST',
        url: url,
        data: sending_data,
        dataType: 'json',
        success: ondatareceived
    });
}