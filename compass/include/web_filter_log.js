/*
 * 描述:web内容过滤日志记录页面js
 *
 * 作者: xinzhiwei 1002395703@qq.com
 * 历史：
 *       2015.5.11 Created by xinzhiwei
 */
var ass_url = "/cgi-bin/web_filter_log.cgi";

var message_box_config = {
    url: ass_url,
    check_in_id: "mesg_box_id",
    panel_name: "my_message_box"
}


var list_panel_config = {
    url: ass_url,
    check_in_id: "web_filter_log_panel",
    panel_name: "web_filter_log_panel",
    // is_default_search: false,
    default_search_config: {
        title:"日志关键字",
        input_tip:"仅支持英文查找"
    },
    event_handler: {
        before_load_data: function( list_obj ) {
            // list_panel.extend_sending_data['TEST_NAME'] = 'test';
            list_panel.extend_sending_data['DATE'] = $("#log_date_input_id").val();
        },
        after_load_data: function ( list_obj, response ) {
            /*var date = response['DATE'];
            $("#log_date_input_id").val(date);*/
            // 在每次load-data请求返回之后都设置的值会有个bug那就是在页面一开始初始化日志列表即
            // 也发送的是load-data请求，那么会把我的日期文本框里的值刷为空的了
        }
    },
    // render: list_panel_render,
    panel_header: [{
        enable: true,
        type: 'text',
        title: "时间",
        name: "LOG_TIME",
        column_cls: "align-center",
        width: "20%"
    }, {
        enable: true,
        type: 'text',
        title: "源IP",
        name: "SRC_IP",
        column_cls: "align-center",
        width: "20%"
    }, {
        enable: true,
        type: 'text',
        title: "URL",
        name: "FILTER_URL",
        column_cls: "align-center",
        width: "20%"
    }, {
        enable: true,
        type: 'text',
        title: "过滤类型",
        name: "FILTER_TYPE",
        column_cls: "align-center",
        width: "20%"
    }, {
        enable: true,
        type: 'text',
        title: "策略名称",
        name: "POLICY_NAME",
        column_cls: "align-center",
        width: "10%"
    }, {
        enable: true,
        // type: "action",
        type: 'text',
        title: "动作",
        name: "ACTION",
        column_cls: "align-center",
        width: "10%"
    }],
    top_widgets: [{
        enable: true,
        type: "link_button",
        id: "export_log_id",
        href: "/cgi-bin/web_filter_log.cgi?ACTION=export_data",  // ACTION=export_data&DATE=20150223
        button_icon: "download.png",
        button_text: "导出日志",
        functions: {
            onclick: "append_date_to_link_href();"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "delete.png",
        button_text: "删除日志",
        style: "width:100px;height:30px;",
        functions: {
            onclick: "handle_delete_log();"
        }
    }, {
        enable: true,
        type: "text",
        title: "跳转到",
        id: "log_date_input_id",
        name: "LOG_DATE_INPUT",
        style: "width:130px;height:25px;",
        check: {
            type:'text',
            required: 1,
            check: 'other',
            other_reg: /.*/,
            ass_check: function(){
                var val = $( "#log_date_input_id" ).val();
                if( val > 100 || val < 10 ) {
                    return "此项应填日期且符合yyyy-mm-dd格式";
                }
            }
        },
        functions: {
            onchange: "load_data();"
        }
    }, {
        enable: true,
        type: "image_button",
        button_text: "上一天",
        style: "width:40px;height:30px;",
        functions: {
            onclick: "load_one_day_before_log();"
        }
    }, {
        enable: true,
        type: "image_button",
        button_text: "下一天",
        style: "width:40px;height:30px;",
        functions: {
            onclick: "load_one_day_after_log();"
        }
    }]
};

var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );

$( document ).ready(function() {

    /* 渲染面板 */
    message_manager.render();
    list_panel.render();
    ESONCalendar.bind("log_date_input_id");

    $("#list_panel_id_for_web_filter_log_panel a>button").css({"width":"100px","height":"30px"});

    // list_panel.set_ass_message_manager( message_manager );

    init_date();
    list_panel.extend_sending_data['INIT_TAG'] = true;
    load_data();
    // list_panel.extend_sending_data = null;
    list_panel.extend_sending_data['INIT_TAG'] = false;
    $("#log_date_input_id").blur(function(){
        // alert('o');        // 可以修改的onselect方法里的实现，在里面调用load_data();
        window.setTimeout( load_data, 1000 );  // 等待1秒
        // load_data();
    });

});


function init_date(){
    var sending_data = {
        ACTION: "init_date"
    }
    function onreceived(data){
        var sys_date = data['SYS_DATE'];
        $("#log_date_input_id").val( sys_date );
    }
    do_request( sending_data, onreceived );
    // 下面的是直接在前台利用Date对象获得时间，但它获得的是客户端电脑的时间2015-5-13而不是防火墙系统的时间2015-5-12！
    /*var now = new Date();
    var y = now.getFullYear();
    var m = now.getMonth()+1;
    var d = now.getDate();
    var date = y+"-"+m+"-"+d;
    $("#log_date_input_id").val( date );*/
}


function load_data(){
    list_panel.update_info(true);
    /*var date = $("#log_date_input_id").val();
    var search = $("#search_button_for_web_filter_log_panel").val();
    list_panel.extend_sending_data['DATE'] = date;
    list_panel.extend_sending_data['search'] = search;*/
    // 记住在update_info(true);方法里已经帮你把search框里的值传递到后台了！
    /*var sending_data = {
        ACTION: "load_data",
        DATE: date,
        search: search
    }*/
}


function load_one_day_before_log(){
    var date = $("#log_date_input_id").val();
    var arr = date.split("-");
    var y = arr[0];  var m = arr[1]-1;  var d = arr[2];
    // var date_obj = new Date( Date.UTC(y,m,d,0,0,0) );
    var date_obj = new Date(y,m,d,0,0,0);

    var milliseconds = date_obj.getTime();
    milliseconds = milliseconds - 24*60*60*1000;
    // date_obj.setTime(milliseconds);  is also right..
    // date_obj.getFullYear();  date_obj.getMonth()+1;  date_obj.getDate();
    var new_obj = new Date(milliseconds);
    var y = new_obj.getFullYear();
    var m = new_obj.getMonth()+1;
    var d = new_obj.getDate();
    var new_date = y+"-"+m+"-"+d;
    $("#log_date_input_id").val(new_date);

    load_data();
}


function load_one_day_after_log(){
    var date = $("#log_date_input_id").val();
    var arr = date.split("-");
    var y = arr[0];  var m = arr[1]-1;  var d = arr[2];
    // var date_obj = new Date( Date.UTC(y,m,d,0,0,0) );
    var date_obj = new Date(y,m,d,0,0,0);

    var milliseconds = date_obj.getTime();
    milliseconds = milliseconds + 24*60*60*1000;

    var new_obj = new Date(milliseconds);
    var y = new_obj.getFullYear();
    var m = new_obj.getMonth()+1;
    var d = new_obj.getDate();
    var new_date = y+"-"+m+"-"+d;
    $("#log_date_input_id").val(new_date);

    load_data();
}

function handle_delete_log(){
    var date = $("#log_date_input_id").val();

    var sending_data = {
        ACTION: "delete_data",
        DATE: date
    }
    function onreceived(response){
        alert(response.mesg);
    }
    if( confirm("确定要删除"+date+"日的日志吗？") ){
        do_request( sending_data, onreceived );
    }
}

function append_date_to_link_href(){
    var href = $( "#export_log_id" ).attr("href");
    href += "&DATE=";
    href += $("#log_date_input_id").val();
    // alert(href);
    $( "#export_log_id" ).attr( "href", href );
    return true;
}

function get_input_date(){
    return $("#log_date_input_id").val();
}


function set_input_data(value){
    $("#log_date_input_id").val(value);
}


function do_request( sending_data, onreceived ) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/web_filter_log.cgi",
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            alert("返回数据格式有误,请检查");
        },
        success: onreceived
    });
}