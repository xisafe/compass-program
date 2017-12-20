$(document).ready(function(){
    list_panel = new PagingHolder( list_panel_config );
    detail_panel = new PagingHolder( detail_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    list_panel.render();
    detail_panel.render();
    message_manager.render();
    
    detail_panel.hide();
    
    list_panel.set_ass_message_manager( message_manager );
    load_list_data();
    //list_panel.update_info(true);
});
var list_panel;
var detail_panel;
var is_loading_list_data_auto = true;
var message_box_config = {
    url: "/cgi-bin/ipranking.cgi",
    check_in_id: "mesg_box_iprank",
    panel_name: "my_message_box"
}
var message_manager;

var list_panel_render = {
    'app_type': {
        render: function( default_rendered_text, data_item ) {
            var result_render = data_item.app_type;
            return '<a style="text-decoration: underline;cursor:pointer;" onclick="show_detail_panel(this);" name='+data_item.ip_addr+'>' + result_render + '</a>';
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/ipranking.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_iprank_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    panel_title: "前100用户流量排名",
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    is_paging_tools: false,
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            if(data_item.nodata){
                //message_manager.show_popup_error_mesg(data_item.nodata);
                $("#no_data_box").show();
            }else{
                $("#no_data_box").hide();
            }
        }
    },
    panel_header: [{
        "enable": false,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //元素的class
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
        "type": "text",
        "title": "IP地址",        //一般text类型需要title,不然列表没有标题
        "name": "ip_addr",
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
    }, {
        "enable": true,
        "type": "text",
        "title": "流量构成",
        "name": "app_type",
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
        "id": "timetype",     // ==可选==，控件ID
        "name": "timetype",   // **必填**，控件的名字
        "title": "统计时间范围：",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        "options": [{
            "value":"rt",
            "text":"实时"
        }, {
            "value":"lasthour",
            "text":"最近一小时"
        }, {
            "value":"lastday",
            "text":"最近一天"
        }, {
            "value":"lastweek",
            "text":"最近一周"
        }]
    }, {
        "enable": true,         // ==可选==，如果为不填或者为false,就不显示
        "type": "select",         // ==可选==，默认为text类型
        "id": "unit",     // ==可选==，控件ID
        "name": "unit",   // **必填**，控件的名字
        "title": "单位：",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        "options": [{
            "value":"KB/s",
            "text":"KB/s"
        }, {
            "value":"KB",
            "text":"KB"
        }]
    }, {
        "enable": true,         // ==可选==，如果为不填或者为false,就不显示
        "type": "select",         // ==可选==，默认为text类型
        "id": "period",     // ==可选==，控件ID
        "name": "period",   // **必填**，控件的名字
        "title": "刷新间隔：",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
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
    }, {
        "enable": true,
        "type": "text",
        "id": "filterIP",
        "name": "filterIP",
        "title": "过滤IP："
        /* "check":{
            type: "text",
            required: 0,
            check: 'ip|ip_mask|',
            ass_check: function( check ) {
                
            }
        } */
    }, {
        "enable": true,
        "type": "image_button",
        "id": "begin_search",
        "name": "begin_search",
        "button_text": "确定",
        "cls": "my_search_button",
        "functions": {
            onclick: "load_list_data();"
        }
    }]
}

var detail_panel_render = {
    'name': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.name == "DNS"){
                result_render = "域名解析流量";
            }else if(data_item.name == "HTTP"){
                result_render = "web流量";
            }else if(data_item.name == "NETBIOS"){
                result_render = "netbios流量";
            }else if(data_item.name == "NTP"){
                result_render = "网络时间同步流量";
            }else if(data_item.name == "POP3"){
                result_render = "接收邮件流量";
            }else if(data_item.name == "SMTP"){
                result_render = "发送邮件流量";
            }else if(data_item.name == "SNMP"){
                result_render = "简单网络管理流量";
            }else if(data_item.name == "SSH"){
                result_render = "ssh流量";
            }else if(data_item.name == "TELNET"){
                result_render = "telnet流量";
            }else if(data_item.name == "FTP"){
                result_render = "ftp流量";
            }else if(data_item.name == "other"){
                result_render = "其他流量";
            }else if(data_item.name == "total"){
                result_render = "总流量";
            }
            return '<span>' + result_render + '</span>';
        }
    }
};
var detail_panel_config = {
    url: "/cgi-bin/ipranking.cgi",
    check_in_id: "panel_detail",
    panel_name: "detail_panel",
    page_size: 2,
    panel_title: "流量详情",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    render: detail_panel_render,
    modal_config: {
        modal_box_size: "m",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            
        }
    },
    panel_header: [{
        enable: false,
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "流量类型",
        name: "name",
        width: "18%"
    }, {
        enable: true,
        type: "text",
        title: "百分比",
        name: "ratio",
        width: "18%"
    }, {
        enable: true,
        type: "text",
        title: "上行流量",
        name: "upload",
        width: "18%"
    }, {
        enable: true,
        type: "text",
        title: "下行流量",
        name: "download",
        width: "18%"
    }, {
        enable: true,
        type: "text",
        title: "总流量",
        name: "sum",
        width: "18%"
    }],
    bottom_extend_widgets: {
        cls: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "detail_panel.hide();"
            }
        }, {
            enable: false,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "detail_panel.hide();"
            }
        }]
    }
};

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

//显示详细信息
function show_detail_panel(e){
    var ip_addr = e.name;
    var unit = $("#unit").val();
    var timetype = $("#timetype").val();
    detail_panel.extend_sending_data = {
        ip_addr: ip_addr,
        unit: unit,
        timetype: timetype
    };
    detail_panel.update_info(true);
    detail_panel.show();
    $(".list-panel-title").get(1).innerHTML = ip_addr+"流量详情";
}
//动态加载列表展示数据
function load_list_data(){
    var period = $("#period").val();
    list_panel.update_info(true);
    if(period > 0){
        window.setTimeout("load_list_data()",period*1000);
    }else{
        is_loading_list_data_auto = false;
    }
}