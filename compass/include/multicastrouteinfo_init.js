$(document).ready(function(){
    list_panel = new PagingHolder( list_panel_config );
    /* 渲染面板 */
    list_panel.render();

    
    update_data();
    /* 绑定时间输入*/
    //ESONCalendar.bind("time_start");
    //ESONCalendar.bind("time_end");
});
var list_panel;

var list_panel_render = {
    's_port': {
        render: function( default_rendered_text, data_item ) {
            var temp_arr = default_rendered_text.split("&");
            var result_render = temp_arr.join(" ")
            return '<span>' + result_render + '</span>';
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/multicastrouteinfo.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_multicastroute_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
     // panel_title: "组播路由信息",
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持关键字查询",
        title: ""
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": false,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": false,
            "type": "radio",
            "name": "radio",
            "column_cls": "rule-listbc",
            "width": "5%"
        }, {
            "enable": true,
            "type": "text",
            "title": "组播源",        //一般text类型需要title,不然列表没有标题
            "name": "s_multicast",
            "width": "24%"
        }, {
            "enable": true,
            "type": "text",
            "title": "组播地址",
            "name": "addr_multicast",
            "width": "24%"
        }, {
            "enable": true,
            "type": "text",
            "title": "入接口",
            "name": "input_interface",
            "width": "24%"
        }, 
        {
            "enable": true,
            "type": "text",
            "title": "出接口",
            "name": "output_interface",
            "width": "24%"
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
    is_default_search: true
    
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
    add_panel.show();
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/multicastrouteinfo.cgi',
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

//加载数据
function update_data(){
    var sending_data = {
        ACTION: "update_data"
    };

    function ondatareceived(data) {
        //if(data.state_static == "off" && data.state_dynamic == "off"){
        if(data.state_static !== undefined && data.state_static == "off"){
            
        }else{
            list_panel.update_info(true);
        }
        window.setTimeout("update_data()",5000);
    }

    do_request(sending_data, ondatareceived);
}