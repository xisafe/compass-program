$(document).ready(function(){
    init();
    check_update();
});

function init() {
    /*初始化消息框,以使图片加载*/
    show_waiting_mesg("准备中...");
    hide_waiting_mesg();
}

function check_update() {
    var sending_data = {
        updated_check: 'updated_check'
    }

    function ondatareceived(data){
        var data_content = data;
        if(data.is_updated == '1') {
            /*上次进行了升级操作*/
            show_waiting_mesg("升级中...");
            check_updated_result();
        }
    }
    
    do_request(sending_data, ondatareceived);
}

function check_updated_result() {
    var sending_data = {
        updated_check: 'check_updated_result'
    }

    function ondatareceived(data){
        var data_content = data;
        if(data.status == '0') {
            /*升级成功*/
            hide_waiting_mesg();
            show_popup_mesg("升级成功");
        } else {
            hide_waiting_mesg();
            show_popup_alert_mesg(data.mesg);
        }
    }
    
    // do_request(sending_data, ondatareceived);
    window.setTimeout(function() {do_request(sending_data, ondatareceived)}, 3500);
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/idps_console_update.cgi',
        data: sending_data,
        dataType: 'json',
        async: true,//异步方式
        error: function(request){
            show_popup_alert_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

var object = {
   'form_name':'RULES_UPDATE_ONLINE',
   'option':{
        'CONTROL_URL':{
           'type':'text',
           'required':'1',
           'check':'ip|domain|',
           'ass_check':function(){
            }
        },
    }
}
var object2 = {
   'form_name':'RULES_UPDATE_OFFLINE',
   'option'   :{
        'IDPS_CONSOLE_FILE':{
           'type':'file',
           'required':'1',
           'ass_check':function(){
            }
        },
    }
}

var check = new ChinArk_forms();
//check._get_form_obj_table("RULES_UPDATE_OFFLINE");


function toggle_update_server(element){
    if(element.value == "auto") {
        disable_url_input();
    } else {
        enable_url_input();
    }
}

function disable_url_input() {
    var url_input = document.getElementById("snort_rules_url");
    url_input.disabled = true;
    url_input.style.display = "none";
}

function enable_url_input() {
    var url_input = document.getElementById("snort_rules_url");
    url_input.disabled = false;
    url_input.style.display = "inline";
}

function toggle_update_schedule(element) {
    if(element.checked) {
        enable_update_schedule();
    } else {
        disable_update_schedule();
    }
}

function offline_update() {
    if(check._submit_check(object2,check)){
        //do nothing
    } else {
        show_waiting_mesg("上传中...")
    }
}

function disable_update_schedule() {
    $(".update_schedule_radio").attr("disabled", true);
    $(".update_schedule_label").addClass("disabled");
}

function enable_update_schedule() {
    $(".update_schedule_radio").attr("disabled", false);
    $(".update_schedule_label").removeClass("disabled");
}

function show_uploading_mesg(){
    $("#popup-mesg-box-back").show();
    $("#popup-mesg-box-uploading").show();
}

function hide_uploading_mesg() {
    $("#popup-mesg-box-back").hide();
    $("#popup-mesg-box-uploading").hide();
}
