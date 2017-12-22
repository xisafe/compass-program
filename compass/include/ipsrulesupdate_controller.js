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
    var url = "/cgi-bin/ipsrulesupdate.cgi";
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
            RestartService("正在下载IPS特征库升级包，请耐心等待.....");
            window.setTimeout( timing_check_running, check_interval );
        }else if(response.running == 2){
            RestartService("IPS特征库正在升级，请耐心等待.....");
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
            endmsg("IPS特征库升级成功");
        }
    }

    request_for_json( sending_data, ondatareceived );
}

$( document ).ready(function(){
    check_running();
    var uploader = new qq.FileUploader({
        element: document.getElementById('file-uploader'),
        allowedExtensions: ['dat'], 
        action:'/cgi-bin/ipsrulesupdate_post.cgi',
        debug:true,
        onSubmit: function(id, fileName){},
        onProgress: function(id, fileName, loaded, total){},
        onComplete: function(id, fileName, responseJSON){},
        onCancel: function(id, fileName){},
        showMessage: function(message){ alert(message); }
    });
});