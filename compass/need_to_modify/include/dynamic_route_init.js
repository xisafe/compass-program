$(document).ready(function(){
    list_panel = new PagingHolder( list_panel_config );
    /* 渲染面板 */
    list_panel.render();

    
    list_panel.update_info(true);
    /* 绑定时间输入*/
    //ESONCalendar.bind("time_start");
    //ESONCalendar.bind("time_end");
});
var list_panel;

var list_panel_render = {
    'destip': {
        render: function( default_rendered_text, data_item ) {
            var result_render ="";
            if(default_rendered_text == "default"){
                result_render = "默认";
            }else{
                result_render = default_rendered_text;
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'via': {
        render: function( default_rendered_text, data_item ) {
            var result_render ="";
            if(default_rendered_text == "" || default_rendered_text == null){
                result_render = "0.0.0.0";
            }else{
                result_render = default_rendered_text;
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'metric': {
        render: function( default_rendered_text, data_item ) {
            var result_render ="";
            if(default_rendered_text == "" || default_rendered_text == null){
                result_render = "0";
            }else{
                result_render = default_rendered_text;
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'proto': {
        render: function( default_rendered_text, data_item ) {
            var result_render ="";
            if(default_rendered_text == "zebra"){
                result_render = "动态路由";
            }else{
                result_render = "直连";
            }
            return '<span>' + result_render + '</span>';
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/dynamic_route.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_dyroute_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
     panel_title: "路由信息",
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": false,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "column_cls": "rule-listbc",//这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": true,
            "type": "text",
            "title": "目的地址",        //一般text类型需要title,不然列表没有标题
            "name": "destip",
            "width": "16%"
        }, {
            "enable": true,
            "type": "text",
            "title": "网络掩码",
            "name": "mask",
            "width": "16%"
        }, {
            "enable": true,
            "type": "text",
            "title": "下一跳地址",
            "name": "via",
            "width": "16%"
        }, 
        {
            "enable": true,
            "type": "text",
            "title": "Metric值",
            "name": "metric",
            "td_class": "align-center",
            "width": "16%"
        }, 
        {
            "enable": true,
            "type": "text",
            "title": "路由类型",
            "name": "proto",
            "td_class": "align-center",
            "width": "16%"
        }, {
            "enable": true,
            "type": "text",
            "title": "接口",
            "name": "dev",
            "td_class": "align-center",
            "width": "16%"
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: false,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "添加拨号用户",
            functions: {
                onclick: "add_rule(this);"
            }
        },
        {
            "enable": false,
            type: "image_button",
            "id": "delete_selected",
            "name": "delete_selected",
            "button_icon": "delete.png",
            "button_text": "删除选中",
            "functions": {
                onclick: "delete_selected_items(this)"
            }
        }
    ],
    bottom_widgets: [               /* ===可选=== */
        {
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
        }
    ],
    is_default_search: false
    
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

function add_rule( element ) {
    $("#username").attr("value","");
    $("#pwd").attr("value","");
    add_panel.show();
}