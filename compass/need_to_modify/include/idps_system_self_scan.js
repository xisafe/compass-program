$(document).ready(function(){

});

var scan_manager = new ScanManager();

function begin_scan() {
    scan_manager.self_scan();
}

function abort_scan() {
    scan_manager.abort_scan();
}

function ScanManager() {
    this.steps = [
        {
            ACTION: 'i',
            rate_begin: 0,
            rate_ending: 11,
            icon_id: 'kernel_image_file',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: '内核镜像文件不完整'
        },{
            ACTION: 'g',
            rate_begin: 12,
            rate_ending: 22,
            icon_id: 'boot_record_file',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: '引导记录文件不完整'
        },{
            ACTION: 'w',
            rate_begin: 23,
            rate_ending: 33,
            icon_id: 'device_hardware',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: ''
        },{
            ACTION: 'a',
            rate_begin: 34,
            rate_ending: 44,
            icon_id: 'executable_file',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: '执行文件不完整'
        },{
            ACTION: 'c',
            rate_begin: 45,
            rate_ending: 55,
            icon_id: 'configuration_file',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: '配置文件不完整'
        },{
            ACTION: 'm',
            rate_begin: 56,
            rate_ending: 66,
            icon_id: 'system_memory',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: '内存存在泄漏'
        },{
            ACTION: 's',
            rate_begin: 67,
            rate_ending: 77,
            icon_id: 'available_space',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: '硬盘可用空间不足'
        },{
            ACTION: 'e',
            rate_begin: 78,
            rate_ending: 88,
            icon_id: 'engine_lib_file',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: '引擎库文件不完整'
        },{
            ACTION: 'r',
            rate_begin: 89,
            rate_ending: 100,
            icon_id: 'rule_lib_file',
            finish_flag: false,
            succeed_flag: false,
            error_mesg: '特征库文件不完整'
        }
    ];
    this.abort_flag = false;
    this.request_interval = 5000;
    this.update_rate_interval = 500;
}

ScanManager.prototype.self_scan = function() {
    this.init_steps();
    this.set_scanning_status();
    this.updating_rate(this.steps[0].rate_begin, 0 );
    this.do_action( 0 );
}


ScanManager.prototype.do_action = function( step ) {
    var self = this;
    /*如果现在用户已点击了停止*/
    if ( self.abort_flag ) {
        return;
    }
    var sending_data = {
        ACTION: self.steps[step].ACTION
    }
    function ondatareceived( data ){
        /*如果现在用户已点击了停止*/
        if ( self.abort_flag ) {
            self.set_step_failed( step, "未完成" );
            return;
        }
        if( self.is_finished( data.opt ) ) {
            self.set_step_finished( step );
            if ( self.is_success( data.status ) ) {
                self.set_step_succeeded( step );
            } else {
                self.set_step_failed( step, self.steps[step].error_mesg );
            }
            /*完成本步骤,如果本步骤不是最后一个步骤,就进入下一个步骤*/
            if ( step != ( self.steps.length - 1 ) ) {
                self.do_action( step + 1 );
            } else {
                self.set_finished_status();
            }
            return;
        } else {
            /*再询问后台是否完成*/
            window.setTimeout( function() {
                if ( !self.abort_flag ) {
                    self.do_action( step );
                }
            }, self.request_interval);
        }
    }
    self.set_step_begin( step );
    self.do_request(sending_data, ondatareceived);
    // window.setTimeout( function() {
    //     self.do_request(sending_data, ondatareceived);
    // }, self.request_interval);//testing
}

ScanManager.prototype.do_request = function( sending_data, ondatareceived ) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/idps_system_self_scan.cgi',
        data: sending_data,
        dataType: 'json',
        async: true,
        timeout: 10000,
        error: function(request){
            show_popup_alert_mesg("网络错误,部分功能可能出现异常");
        },
        complete : function(XMLHttpRequest,status){ //请求完成后最终执行参数
            if( status == 'timeout' ){
                show_popup_alert_mesg("请求超时");
            }
        },
        success: ondatareceived
    });
}

ScanManager.prototype.updating_rate = function( rate, step ) {
    var self = this;
    if ( rate > ( self.steps[step].rate_ending - 1 ) || self.steps[step].finish_flag || self.abort_flag || self.steps[ self.steps.length -1 ].finish_flag ) {
        /*如果所有的步骤都已完成*/
        if ( self.steps[ self.steps.length -1 ].finish_flag ) {
            rate = self.steps[ self.steps.length -1 ].rate_ending;
            self.set_progress( rate );
            return;
        }
        /*已完成本步骤,进入下一个步骤*/
        if ( self.steps[step].finish_flag ) {
            rate = self.steps[step].rate_ending;
            self.set_progress( rate );
            /*如果是最后一个步骤,就终止更新*/
            if ( step != ( self.steps.length - 1 ) ) {
                window.setTimeout( function() {
                    self.updating_rate( rate, step + 1 );
                }, self.update_rate_interval);
            }
            return;
        }
        /*已本步骤进度条已走完,但本步骤中的后台事情还没有做完*/
        if ( rate > ( self.steps[step].rate_ending - 1 ) ) {
            window.setTimeout( function() {
                self.updating_rate( rate, step );
            }, self.update_rate_interval);
            return;
        }
        if ( self.abort_flag )
        {
            return;//abort
        }
    } else {
        self.set_progress( rate );
        rate++;
        window.setTimeout( function() {
            self.updating_rate( rate, step );
        }, self.update_rate_interval);
        return;
    }
}

ScanManager.prototype.set_progress = function( rate ) {
    if ( rate < 0 || rate > 100 ) {
        rate = 0;
    }
    this.set_progress_ring( rate );
    this.set_progress_bar( rate );
}

ScanManager.prototype.set_progress_ring = function( rate ) {
    if ( rate == 100 ) {
        document.getElementById( "scanning-header-left-text" ).style.backgroundImage = "url(../images/waiting_over.png)";
    } else if ( rate == 0 ) {
        document.getElementById( "scanning-header-left-text" ).style.backgroundImage = "url(../images/waiting.gif)";
    }
    $( "#scanning-header-left-text" ).html( rate + "%" );
}

ScanManager.prototype.set_progress_bar =function( rate ) {
    var finished = rate + "%";
    var unfinished = 100 - rate;
    unfinished = unfinished + "%";
    document.getElementById("finished").style.width = finished;
}

ScanManager.prototype.init_steps = function() {
    for( var i = 0; i < this.steps.length; i++ ) {
        var icon_id = this.steps[i].icon_id;
        var icon = document.getElementById( icon_id );
        icon.src = "../images/indicator.gif";
        icon.style.display = "none";

        var error_text_id = icon_id + "_td";
        document.getElementById( error_text_id ).innerHTML = "";

        this.steps[i].finish_flag = false,
        this.steps[i].succeed_flag = false
    }
    this.abort_flag = false;
}

ScanManager.prototype.set_step_begin = function( step ) {
    var icon_id = this.steps[step].icon_id;
    var icon = document.getElementById( icon_id );
    icon.src = "../images/indicator.gif";
    icon.style.display = "inline";
}

ScanManager.prototype.set_step_finished = function( step ) {
    this.steps[step].finish_flag = true;
}

ScanManager.prototype.set_step_succeeded = function( step ) {
    this.steps[step].succeed_flag = true;
    var icon_id = this.steps[step].icon_id;
    document.getElementById( icon_id ).src = "../images/on.png";
}

ScanManager.prototype.set_step_failed = function( step, error_mesg ) {
    this.steps[step].succeed_flag = false;
    var icon_id = this.steps[step].icon_id;
    var error_text_id = icon_id + "_td";
    document.getElementById( icon_id ).src = "../images/off.png";
    document.getElementById( error_text_id ).innerHTML = error_mesg;
}

ScanManager.prototype.abort_scan = function() {
    this.abort_flag = true;
    this.set_abort_status();
}

ScanManager.prototype.set_abort_status = function() {
    document.getElementById( "scanning-header-left-text" ).style.backgroundImage = "url(../images/waiting_abort.png)";
    document.getElementById( "begin_self_scan" ).value = "重新开始";
    document.getElementById( "begin_self_scan" ).disabled = false;
    document.getElementById( "stop_self_scan" ).disabled = true;
}

ScanManager.prototype.set_finished_status = function() {
    document.getElementById( "scanning-header-left-text" ).style.backgroundImage = "url(../images/waiting_over.png)";
    document.getElementById( "begin_self_scan" ).value = "重新开始";
    document.getElementById( "begin_self_scan" ).disabled = false;
    document.getElementById( "stop_self_scan" ).disabled = true;
}

ScanManager.prototype.set_scanning_status = function() {
    document.getElementById( "scanning-header-left-text" ).style.backgroundImage = "url(../images/waiting.gif)";
    document.getElementById( "begin_self_scan" ).value = "自检中...";
    document.getElementById( "begin_self_scan" ).disabled = true;
    document.getElementById( "stop_self_scan" ).disabled = false;
}

ScanManager.prototype.is_finished = function( status ) {
    if ( status == '0' ) {
        return true;
    } else {
        return false;
    }
}

ScanManager.prototype.is_success = function( status ) {
    if ( status == '0' ) {
        return true;
    } else {
        return false;
    }
}