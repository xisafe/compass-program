//初始化页面按钮效果
//2014.11.27 modified by Liu Julong，修改按钮显示效果
$(document).ready(function(){
    document.getElementById("stop").style.backgroundImage = '';
});
var handle;
function start() {
    var sending_data, ret_data;
    if(!check._submit_check(object,check)) {
        /*确认正确填写了表单*/
        sending_data = $("#NETWORK_DIAGNOSIS_FORM").serialize();
        sending_data = sending_data + "&ACTION=ping_start";
        ret_data = request(sending_data);
        if(is_success(ret_data.status)) {
            sending_data = {
                ACTION: "read_ping"
            }
            clear_result_display();
            set_button_status(1);
            update_result(sending_data);
        } else {
            show_error_mesg("服务器繁忙,请稍后重试");
        }
    }
}

function clear_result_display() {
    $("#diagnosis_result").html("");
}

function update_result(sending_data) {
    handle = setInterval(function() {
        $.ajax({
            url: "/cgi-bin/network_diagnosis_ping.cgi",
            type: 'POST',
            data: sending_data,
            dataType: 'json',
            cache: false,
            async: false,
            success: ondatareceived
        });
        
        function ondatareceived(retdata) {
            $("#diagnosis_result").html("");
            var start = 0;
            // if(retdata.data.length > 20) {
            //     /*只显示小于20条记录*/
            //     start = retdata.data.length - 20 -1;
            // }
            // 不限制显示条数 2015.02.09 by wanglin
            // start = 0;
            for (var i = start;i < retdata.data.length; i++) {
                $("#diagnosis_result").append(retdata.data[i] + "\r\n");
            }
            if (retdata.mesg == "end") {
                clearInterval(handle);
                set_button_status(0);//设置为初始状态
                return;
            }
        }

    }, 1000);
}

function stop_fetch_data() {
    clearInterval(handle);
    set_button_status(0);//设置为初始状态
    var sending_data = {
        ACTION: "ping_stop"
    };
    request(sending_data);
}

function request(sending_data) {
    var ret_data;
    $.ajax({
        type: "POST",
        cache: false,
        async: false,
        url: "/cgi-bin/network_diagnosis_ping.cgi",
        data: sending_data,
        dataType: "json",
        error: function(request) {
            show_error_mesg("连接错误,请重试");
        },
        success: function(data) {
            ret_data = data;
        }
    });
    return ret_data;
}

function set_button_status(status) {
    var begin = document.getElementById("begin");
    var stop = document.getElementById("stop");
    if(status == 0) {
        //初始状态
        begin.disabled = false;
        stop.disabled = true;
        stop.style.backgroundImage = '';
        begin.style.backgroundImage = 'url("/images/button.jpg")';
    } else {
        //运行状态
        begin.disabled = true;
        stop.disabled = false;
        //2014.11.27 modified by Liu Julong，修改按钮显示效果
        begin.style.backgroundImage = '';
        stop.style.backgroundImage = 'url("/images/button.jpg")';
    }
}


function exchange_tool(element) {
    if(element.value == "ping") {
        hide_traceroute_config();
        show_ping_config();
    } else {
        hide_ping_config();
        show_traceroute_config();
    }
}

function show_ping_config() {
    var ping_config = $(".ping_config_tr");
    for(var i = 0; i < ping_config.length; i++) {
        ping_config[i].style.display = "table-row";
    }
}

function hide_ping_config() {
    var ping_config = $(".ping_config_tr");
    for(var i = 0; i < ping_config.length; i++) {
        ping_config[i].style.display = "none";
    }

}

function show_traceroute_config() {
    var traceroute_config = $(".traceroute_config_tr");
    for(var i = 0; i < traceroute_config.length; i++) {
        traceroute_config[i].style.display = "table-row";
    }

}

function hide_traceroute_config() {
    var traceroute_config = $(".traceroute_config_tr");
    for(var i = 0; i < traceroute_config.length; i++) {
        traceroute_config[i].style.display = "none";
    }
}

function is_success(status) {
    if (status == "0") {
        return true;
    } else {
        return false;
    }
}

function show_error_mesg(mesg) {
    alert(mesg);
}