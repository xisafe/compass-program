$(document).ready(function(){
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    list_panel.render();
    message_manager.render();
    
    
    list_panel.set_ass_message_manager( message_manager );
    //list_panel.update_info(true);
    load_list_data();
    load_chart_data();
});
var myChart;
var chart_data = [];
var chart_data_x = [];
var chart_data_y_upload = [];
var chart_data_y_download = [];
var chart_data_y_sum = [];
var is_loading_list_data_auto = true;
var appName = "";
var id_timeout = "";
var id_timeout_list = "";
var list_panel;
var message_box_config = {
    url: "/cgi-bin/global_flow.cgi",
    check_in_id: "mesg_box_flow",
    panel_name: "my_message_box"
}
var message_manager;

var list_panel_render = {
    'rad_check': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var val_rad = "";
            if(data_item.name == "总流量"){
                val_rad = "total";
            }else if(data_item.name == "域名解析流量"){
                val_rad = "DNS";
            }else if(data_item.name == "web流量"){
                val_rad = "HTTP";
            }else if(data_item.name == "netbios流量"){
                val_rad = "NETBIOS";
            }else if(data_item.name == "网络时间同步流量"){
                val_rad = "NTP";
            }else if(data_item.name == "接收邮件流量"){
                val_rad = "POP3";
            }else if(data_item.name == "发送邮件流量"){
                val_rad = "SMTP";
            }else if(data_item.name == "简单网络管理流量"){
                val_rad = "SNMP";
            }else if(data_item.name == "ssh流量"){
                val_rad = "SSH";
            }else if(data_item.name == "telnet流量"){
                val_rad = "TELNET";
            }else if(data_item.name == "ftp流量"){
                val_rad = "FTP";
            }else if(data_item.name == "其他流量"){
                val_rad = "other";
            }
            
            var checked = "";
            if(val_rad == appName){
                checked = "checked";
            }else if(val_rad == "total"){
                checked = "checked";
            }
            result_render = '<input type="radio" '+checked+' name="rad_appname" value="'+val_rad+'" onclick="load_chart_data();"/>';
            return result_render;
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/global_flow.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_flow_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 13,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    panel_title: "实时流量",
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    is_paging_tools: false,
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            if(data_item.status == '1'){
                //message_manager.show_popup_error_mesg(data_item.error_mesg);
                is_loading_list_data_auto = false;
                clearTimeout(id_timeout);
                $("#no_data_box").show();
                $("#chart_recent").html("<span style='color:red;font-size:18px;position:relative;top:150px;left:50%'>暂时无信息展示</span>");
            }else{
                $("#no_data_box").hide();
                is_loading_list_data_auto = true;
                load_chart_data();
                display_chart_detail();
                
            }
        }
    },
    panel_header: [{
        "enable": false,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //用户装载数据之用
        "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "5%"
    }, {
        "enable": false,
        "type": "radio",
        "name": "rad_flowType",
        "column_cls": "rule-listbc",
        "width": "5%"
    }, {
        "enable": true,
        "type": "radio",
        "title": "",        //一般text类型需要title,不然列表没有标题
        "name": "rad_check",
        "width": "5%"
    }, {
        "enable": true,
        "type": "text",
        "title": "流量类型",        //一般text类型需要title,不然列表没有标题
        "name": "name",
        "width": "18%"
    }, {
        "enable": true,
        "type": "text",
        "title": "百分比",
        "name": "ratio",
        "width": "18%"
    }, {
        "enable": true,
        "type": "text",
        "title": "上行流量",
        "name": "upload",
        "width": "18%"
    }, {
        "enable": true,
        "type": "text",
        "title": "下行流量",
        "name": "download",
        "width": "18%"
    }, {
        "enable": true,
        "type": "text",
        "title": "总流量",
        "name": "sum",
        "width": "18%"
    }],
    top_widgets: [{
        enable: false,
        type: "image_button",
        button_icon: "add16x16.png",
        button_text: "新建协议管理",
        functions: {
            onclick: "add_rule(this);"
        }
    }, {
        "enable": false,
        "type": "image_button",
        "id": "delete_selected",
        "name": "delete_selected",
        "button_icon": "delete.png",
        "button_text": "删除选中",
        "functions": {
            onclick: "delete_selected_items(this);"
        }
    }],
    bottom_widgets: [{
        "enable": false,
        "id": "export_selected",
        "name": "export_selected",
        "button_icon": "download.png",
        "button_text": "导出选中",
        "functions": {
            onclick: "export_selected_items(this)"
        }
    }, {
        "enable": false,
        "id": "delete_all_logs",
        "name": "delete_all_logs",
        "button_icon": "delete.png",
        "button_text": "清空日志",
        "functions": {
            onclick: "delete_all_logs(this)"
        }
    }],
    is_default_search: false,          /* ===可选===，默认是true，控制默认的搜索条件 */
    extend_search: [{
        "enable": true,         // ==可选==，如果为不填或者为false,就不显示
        "type": "select",         // ==可选==，默认为text类型
        "id": "unit",     // ==可选==，控件ID
        "name": "unit",   // **必填**，控件的名字
        "title": "单位",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        "options": [{
            "value":"KB/s",
            "text":"KB/s"
        },{
            "value":"KB",
            "text":"KB"
        }]
    }, 
    {
        "enable": true,         // ==可选==，如果为不填或者为false,就不显示
        "type": "select",         // ==可选==，默认为text类型
        "id": "period",     // ==可选==，控件ID
        "name": "period",   // **必填**，控件的名字
        "title": "刷新间隔",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        "options": [{
            "value":"10",
            "text":"10秒"
        }, {
            "value":"15",
            "text":"15秒"
        }, {
            "value":"30",
            "text":"30秒"
        }, {
            "value":"60",
            "text":"60秒"
        }, {
            "value":"0",
            "text":"不刷新"
        }]
    }, 
    {
        "enable": true,
        "type": "image_button",
        "id": "begin_search",
        "name": "begin_search",
        "button_text": "确定",
        "cls": "my_search_button",
        "functions": {
            onclick: "do_confirm_refresh();"
        }
    }]
}

function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_panel.enable_item( ids );
}

function disable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_panel.disable_item( ids );
}

function delete_selected_items(e) {
    var ids = "";
    if(e.id == "delete_selected"){
        var checked_items = list_panel.get_checked_items();
        var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].id );
        }
        ids = checked_items_id.join( "&" );
    }else{
        ids = e.value;
    }
    
    list_panel.delete_item( ids );
}

function extend_search_function( element ) {
    list_panel.update_info( true );
}

//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/global_flow.cgi",
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//保存启用配置
function save_data_enable(){
    var enabled = "";
    if($("#enabled").attr("checked")){
        enabled = $("#enabled").val();
    }else{
        enabled = "off";
    }
    var sending_data = {
        ACTION: "save_data_enable",
        enabled: enabled
    };

    function ondatareceived(data) {
        message_manager.show_popup_note_mesg(data.mesg);
        if(data.reload == "1"){
            message_manager.show_apply_mesg("规则已改变,需要重新应用以使规则生效");
            //parent.window.document.getElementById('rightFrame').src='global_flow.cgi';
            
            /* clearTimeout(id_timeout);
            clearTimeout(id_timeout_list);
            is_loading_list_data_auto = true;
            load_list_data();
            load_chart_data(); */
        }
    }
    do_request(sending_data, ondatareceived);
}
//加载图表数据
function load_chart_data(){
    appName = $("input[name='rad_appname']:checked").val();
    if(appName == "" || appName ==null){
        appName = "total";
    }
    var unit = $("#unit").val();
    var period = $("#period").val();
    var time = $("input[name='rad_time']:checked").val();
    var sending_data = {
        ACTION: "load_chart_data",
        unit: unit,
        time: time,
        appName: appName
    };

    function ondatareceived(data) {
        var data_content = data;
        //数据配置
        chart_data = data.detail_info;
        var type = data.type;
        var name = data.name;
        chart_data_x = [];
        chart_data_y_download = [];
        chart_data_y_upload = [];
        chart_data_y_sum = [];
        $("#chart_recent").html("");
        $("#title_detail").html(name);
        if(data_content.nodata){
            //message_manager.show_popup_error_mesg("暂时无信息展示");
            $("#chart_recent").html("<span style='color:red;font-size:18px;position:relative;top:150px;left:50%'>暂时无信息展示</span>");
        }else{
            for(var i=0;i<chart_data.length;i++){
                var download = "";
                var upload = "";
                var sum = "";
                download = (chart_data[i].download.split("K"))[0];
                upload = (chart_data[i].upload.split("K"))[0];
                sum = (chart_data[i].sum.split("K"))[0];
                /* if(type == "realtime"){
                    var arr_time = chart_data[i].time.split(":");
                    if(arr_time[1] == "00"){
                        chart_data_x.unshift(chart_data[i].time);
                        chart_data_y_download.unshift(download);
                        chart_data_y_upload.unshift(upload);
                        chart_data_y_sum.unshift(sum);
                    }
                }else{ */
                    chart_data_x.unshift(chart_data[i].time);
                    chart_data_y_download.unshift(download);
                    chart_data_y_upload.unshift(upload);
                    chart_data_y_sum.unshift(sum);
                //}
                
            }
            display_chart_detail();
        }
        
        
        if(is_loading_list_data_auto && type == "realtime"){
            id_timeout = setTimeout("load_chart_data()",period*1000);
        }else{
            clearTimeout(id_timeout);
        }
    }
    do_request(sending_data, ondatareceived);
}
//动态加载列表展示数据
function load_list_data(){
    var unit = $("#unit").val();
    var period = $("#period").val();
    list_panel.extend_sending_data = {
        unit: unit
    };
    list_panel.update_info(true);
    if(period > 0){
        id_timeout_list =  window.setTimeout("load_list_data()",period*1000);
    }else{
        is_loading_list_data_auto = false;
    }
}
//点击列表确定按钮执行的函数
function do_confirm_refresh(){
    var period = $("#period").val();
    if(is_loading_list_data_auto == false && period > 0){
        is_loading_list_data_auto = true;
        load_list_data();
    }
}
//展示统计图表详细信息
function display_chart_detail(){
    var type = $("input[name='rad_time']:checked").val();
    var unit = $("#unit").val();
    var time_unit = "";
    var data_legend = [];
    var series = [];
    var flow_type = $("input[name='rad_type']:checked").val();
    var interval = 0;
    if(type == "r"){
        $("#div_rad_type").css("display","none");
        $("#chart_recent").css("width","100%");
        interval = 11;
        time_unit = "(分:秒)";
        myChart = echarts.init(document.getElementById('chart_recent'));
        data_legend = ['总流量','上行流量','下行流量'];
        series = [{
            name:'总流量',
            type:'line',
            symbol:'none',
            data:chart_data_y_sum
        }, {
            name:'上行流量',
            type:'line',
            symbol:'none',
            data:chart_data_y_upload
        }, {
            name:'下行流量',
            type:'line',
            symbol:'none',
            data:chart_data_y_download
        }];
    }else{
        $("#div_rad_type").css("display","block");
        $("#chart_recent").css("width","90%");
        interval = 0;
        myChart = echarts.init(document.getElementById('chart_recent'));
        if(flow_type == "upload"){
            data_legend = ['上行流量'];
            series = [{
                name:'上行流量',
                type:'bar',
                symbol:'none',
                data:chart_data_y_upload
            }];
        }else if(flow_type == "download"){
            data_legend = ['下行流量'];
            series = [{
                name:'下行流量',
                type:'bar',
                symbol:'none',
                data:chart_data_y_download
            }];
        }else if(flow_type == "sum"){
            data_legend = ['总流量'];
            series = [{
                name:'总流量',
                type:'bar',
                symbol:'none',
                data:chart_data_y_sum
            }];
        }else{
            data_legend = ['上行流量','下行流量'];
            series = [{
                name:'上行流量',
                type:'bar',
                symbol:'none',
                data:chart_data_y_upload
            }, {
                name:'下行流量',
                type:'bar',
                symbol:'none',
                data:chart_data_y_download
            }];
        }
        if(type == "m"){
            interval = 1;
            time_unit = "(月-日)";
        }else{
            time_unit = "(时)";
        }
    }
    var option = {
        tooltip : {
            show:false,
            trigger: 'axis'
        },
        legend: {
            data:data_legend,
            orient:'horizontal',
            x:'center'
        },
        toolbox: {
            show : false,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        calculable : true,
        xAxis : [{
            name: '时间'+time_unit,
            type : 'category',
            axisTick: {
                show: false,
                interval : interval
            },
            axisLabel: {
                show: true,
                interval : interval
            },
            data: chart_data_x
        }],
        yAxis : [{
            name: '流量'+"("+unit+")",
            type : 'value',
            splitNumber: 5,
            precision: 2,
            splitArea : {show : true}
        }],
        series : series
    };
    //debugger;
    myChart.setOption(option,true);
}