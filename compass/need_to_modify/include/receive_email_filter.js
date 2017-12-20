var message_box_config = {
    url: "/cgi-bin/receive_email_filter.cgi",
    check_in_id: "mesg_box_id"
}

var object = {
   'form_name':'RECEIVE_FILTER_FORM',
   'option':{
        'BLACKLIST':{
            'type':'textarea',
            'required':'0',
            'check':'',
            'ass_check':function(eve){
                var value = $("div.checklist_textarea textarea:eq(0)").val();
                value = value.replace(/\r/,'');
                var items = value.split("\n");
                var item;
                for(var i=0;i<items.length;i++){
                    item = items[i];
                    if(/^[-_A-Za-z0-9\*]+@([_A-Za-z0-9]+\.)+[A-Za-z0-9]{2,3}$/.test(item) ){
                    }else{
                        return "对不起您输入的内容格式不正确";
                    }
                }
             }
        },
        'WHITELIST':{
            'type':'textarea',
            'required':'0',
            'check':'',
            'ass_check':function(eve){
                var value = $("div.checklist_textarea textarea:eq(1)").val();
                value = value.replace(/\r/,'');
                var items = value.split("\n");
                var item;
                for(var i=0;i<items.length;i++){
                    item = items[i];
                    if(/^[-_A-Za-z0-9\*]+@([_A-Za-z0-9]+\.)+[A-Za-z0-9]{2,3}$/.test(item) ){
                    }else{
                        return "对不起您输入的内容格式不正确";
                    }
                }
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
    check._main(object);
    $("#checklist_id").click(function(){
        if( $("#checklist_id").attr("checked") ) {
            $("#last_tr_id").show();
        }else{
            $("#last_tr_id").hide();
        }
    });
    $("#save_button_id").click(function(){
        save_data();
    });
    $("#apply_mesg_box_button_for_my_message_box").click(function(){
        RestartService("正在应用更改...");
        timing_check_running();
    });
    $("#last_tr_id").hide();
    init_load_data();

});


function timing_check_running() {
    var sending_data = {
        ACTION: "check_running"
    }
    function ondatareceived( response ) {
        if ( response.running == 1 ) {
            window.setTimeout( timing_check_running, check_interval );
        } else {
            endmsg("正在应用中...");
            // endmsg("接收邮件过滤开启成功");
        }
    }
    request_for_json( sending_data, ondatareceived );
}



function save_data(){
    /*var sending_data = {   这里存在严重的问题是你只会传送出去ACTION字段，而form表单里所有的元素都没有被发送出去！
        ACTION: "save_data"  因为你为了自己实现Ajax方式已经把form的onsubmit设置为了‘return false；’了
    }*/
    var sending_data = $("#form_id_for_receive_email_filter_panel").serialize();
    sending_data += "&ACTION=save_data";
    function onreceived(response){
        if( response.status == 0 ){
            message_manager.show_note_mesg(response.mesg);  // show_note_mesg..
            // init_load_data();   这个可以不写了，框架里已设置不会还原即清空表单里的数据
            if ( response['reload'] == 1 ) {
                message_manager.show_apply_mesg("规则已改变，需要重新应用以使规则生效");
            }
        }else{
            endmsg();
            message_manager.show_error_mesg(response.mesg);  // show_error_mesg..
            // alert(response.mesg);
        }
    }
    if ( check._submit_check( object, check ) < 1 ) {
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
        if( response.running == 1 ) {
            // 此处是把ready初始化里调用的check_running里面的'check_running'请求以及响应处理的代码融合到‘load-data’请求里
            // 这样就可以节省一次post请求哦
            RestartService("服务正在重启...");
            window.setTimeout( timing_check_running, check_interval );
        }
        if(response['reload'] == 1){
            message_manager.show_apply_mesg("规则已改变，需应用该规则以使改变生效");
        }
        var detail_data = response.detail_data;
        var pop_enabled = detail_data['POP_ENABLED'];
        var checkspam   = detail_data['CHECKSPAM'];

        var virus_enable = response.virus_enable;
        var checkvirus  = detail_data['CHECKVIRUS'];
        var checklist   = detail_data['CHECKLIST'];
        var blacklist = detail_data['BLACKLIST'];
        var whitelist = detail_data['WHITELIST'];
        if(pop_enabled == 'on'){
            $("#pop_enabled_id").attr("checked",true);
        }else{
            $("#pop_enabled_id").attr("checked",false);
        }

        if(checkspam == 1) {
            $("#checkspam_id").attr("checked",true);
        }else{
            $("#checkspam_id").attr("checked",false);
        }
        if(virus_enable == 0){
            $("#checkvirus_id").attr("disabled",false);
            if(checkvirus == 1) {
                $("#checkvirus_id").attr("checked",true);
            }else{
                $("#checkvirus_id").attr("checked",false);
            }
        }else{
            $("#checkvirus_id").attr("disabled",true);
            $("#checkvirus_id").attr("checked",false);
            $("#label_tip").html("（病毒库未激活，该功能无法使用。请先激活！）");
        }
        if(checklist == 1) {
            $("#checklist_id").attr("checked",true);
            $("#last_tr_id").show();
        }else{
            $("#checklist_id").attr("checked",false);
            // $("#last_tr_id").hide();
        }

        // $("#checklist_textarea textarea:eq(0)").val(blacklist);
        // $("#checklist_textarea textarea:eq(1)").val(whitelist);
        $("div.checklist_textarea textarea:eq(0)").val(blacklist);
        $("div.checklist_textarea textarea:eq(1)").val(whitelist);
    }
    request_for_json( sending_data, onreceived );
}

function request_for_json( sending_data, ondatareceived ) {
    var url = "/cgi-bin/receive_email_filter.cgi";
    $.ajax({
        type: 'POST',
        url: url,
        data: sending_data,
        dataType: 'json',
        success: ondatareceived
    });
}