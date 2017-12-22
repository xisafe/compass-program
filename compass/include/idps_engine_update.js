$(document).ready(function(){
    init();
    check_uploaded();
});

function init() {
    /*初始化消息框,以使图片加载*/
    show_waiting_mesg("准备中...");
    hide_waiting_mesg();
}

function check_uploaded() {
    var sending_data = {
        updated_check: 'uploaded_check'
    }

    function ondatareceived(data){
        var data_content = data;
        if(data.is_opted == '0') {
            /*上次进行了上传文件操作*/
            if ( data.status == '1') {
                /*上传了,并已经解密过了*/
                show_engine_list();
            } else if ( data.status == '2') {
                /*上传了,没解密,不需要重传*/
                show_waiting_mesg("解密中...");
                do_decrytion();
            } else if ( data.status == '3' ) {
                /*上传了,没解密,需要重传*/
                /*不做什么,等着重传*/
            } else {
                //不知道做什么,就什么也不做
            }
        }
    }

    do_request(sending_data, ondatareceived);
}

function do_decrytion() {
    var sending_data = {
        updated_check: 'do_decryption'
    }

    function ondatareceived(data){
        var data_content = data;
        if(data.is_opted == '0') {
            /*解密操作开始*/
            window.setTimeout(function(){check_decryption();}, 500);//0.5秒后再检查解密情况
        } else {
            do_decrytion();
        }
    }

    do_request(sending_data, ondatareceived);
}

function check_decryption() {
    var sending_data = {
        updated_check: 'decryption_check'
    }

    function ondatareceived(data){
        var data_content = data;
        if(data.is_opted == '0') {
            /*解密完成*/
            hide_waiting_mesg();
            if(data.status == '0') {
                /*解密成功*/
                show_engine_list();
            } else {
                show_popup_alert_mesg(data.mesg);
            }
        } else {
            window.setTimeout(function(){check_decryption();}, 500);//0.5秒后再检查
        }
    }

    do_request(sending_data, ondatareceived);
}

function update_engines() {
    var checked_engines = document.getElementsByClassName("engines");
    var sending_data = {
        updated_check: 'update_engine'
    }

    var selected_count = 0;
    for( var i = 0; i < checked_engines.length; i++ ) {
        if( checked_engines[i].checked ) {
            sending_data[i] = i;
            selected_count++;
        }
    }

    function ondatareceived(data){
        var data_content = data;
        if(data.is_opted == '0') {
            check_update();
        } else {
            show_popup_alert_mesg(data.mesg);
        }
    }

    if( selected_count ) {
        /*已经开始下发*/
        hide_engine_list();
        show_waiting_mesg("下发中...");
        do_request(sending_data, ondatareceived);
    } else {
        show_popup_alert_mesg("未选择引擎,下发失败");
    }
}

function check_update() {
    var sending_data = {
        updated_check: 'updated_check'
    }

    function ondatareceived(data){
        var data_content = data;
        if(data.is_opted == '0') {
            /*下发完成*/
            hide_waiting_mesg();
            if(data.status == '0') {
                /*下发成功*/
                var mesgs = data.mesg.split("\n");
                show_popup_long_alert_mesg(mesgs);
            } else {
                show_popup_alert_mesg(data.mesg);
            }
        } else {
            window.setTimeout(function(){check_update();}, 500);//0.5秒后再检查
        }
    }

    do_request(sending_data, ondatareceived);
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/idps_engine_update.cgi',
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
   'form_name':'ENGINE_UPDATE_FORM',
   'option'   :{
        'IDPS_ENGINE_FILE':{
           'type':'file',
           'required':'1',
           'ass_check':function(){
            }
        },
    }
}

var check = new ChinArk_forms();
//check._get_form_obj_table("RULES_UPDATE_OFFLINE");


function import_engine_file() {
    if(check._submit_check(object,check)){
        //do nothing
    } else {
        show_waiting_mesg("上传中...");
    }
}

function show_uploading_mesg(){
    $("#popup-mesg-box-back").show();
    $("#popup-mesg-box-uploading").show();
}

function hide_uploading_mesg() {
    $("#popup-mesg-box-back").hide();
    $("#popup-mesg-box-uploading").hide();
}

function show_engine_list() {
    $("#popup-mesg-box-back").show();
    $("#engine_list").show();
}

function hide_engine_list() {
    $("#popup-mesg-box-back").hide();
    $("#engine_list").hide();
}

function toggle_check_all(element) {
    $(".engines").attr("checked", element.checked);
}