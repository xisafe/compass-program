/*
 * 描述: 系统升级页面添加锁屏功能
 *
 * 作者: JuLong Liu
 * 公司: capsheaf
 * 历史：
 *       2015.05.20 JuLong Liu创建
 */

var check_interval = 5000;

function request_for_json( sending_data, ondatareceived ) {
    var url = "/cgi-bin/systemupdate.cgi";
    $.ajax({
        type: 'POST',
        url: url,
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
            RestartService("正在下载系统升级包，请耐心等待.....");
            window.setTimeout( timing_check_running, check_interval );
        }else if(response.running == 2){
            RestartService("系统正在升级，请耐心等待.....");
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
        } else if(response.running == 2){
            window.setTimeout( timing_check_running, check_interval );
        } else {
            endmsg("系统升级成功");
        }
    }

    request_for_json( sending_data, ondatareceived );
}

$( document ).ready(function(){
    check_running();
});