/*
 * 描述: HTTP代理服务器页面添加锁屏功能
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2015.03.03 WangLin创建
 */

var check_interval = 5000;

function request_for_json( sending_data, ondatareceived ) {
    var url = "/cgi-bin/proxyconfig.cgi";
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
        ACTION: "check_running",
    }

    function ondatareceived( response ) {
        if ( response.running == 1 ) {
            RestartService("HTTP代理正在应用改变，需要一定时间，请等待.....");
            window.setTimeout( timing_check_running, check_interval )
        }
    }

    request_for_json( sending_data, ondatareceived );
}

function timing_check_running() {
    var sending_data = {
        ACTION: "check_running",
    }

    function ondatareceived( response ) {
        if ( response.running == 1 ) {
            window.setTimeout( timing_check_running, check_interval );
        } else {
            endmsg("HTTP代理设置成功");
        }
    }

    request_for_json( sending_data, ondatareceived );
}

function when_click_switch() {
    $('.service-switch .image img').click( function() {
        RestartService("HTTP代理正在应用改变，需要一定时间，请等待.....");
        window.setTimeout( timing_check_running, check_interval );
    })
}

$( document ).ready(function(){
    check_running();
    when_click_switch();
});