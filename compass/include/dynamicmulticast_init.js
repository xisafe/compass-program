var useable_interfaces = [];
$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    add_panel.render();
    list_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    list_panel.update_info(true);
    add_panel.hide();
    load_usable_interface();
    /* 绑定时间输入*/
    //ESONCalendar.bind("time_start");
    //ESONCalendar.bind("time_end");
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/dynamicmulticast.cgi",
    check_in_id: "mesg_box_dynamic",
    panel_name: "my_message_box",
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/dynamicmulticast.cgi",
    check_in_id: "panel_dynamic_add",
    panel_name: "add_panel",
    rule_title: "接口配置",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
            
        },
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "RP汇合点",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "point_rp",
                    name: "point_rp",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'ip|',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "组播地址组",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "multicast_addrgroup",
                    name: "multicast_addrgroup",
                    value: "",
                    functions: {
                        
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'ip_mask|',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "模式",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "model",
                    name: "model",
                    options: [
                        {
                            text: "稀疏模式（PIM-SM）",
                            value: "PIM-SM",
                        }
                    ],
                    value: "",
                    functions: {
                        
                    },
                }
            ]
        },
        {
            title: "Cand-RP发送间隔",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "interval_CRP",
                    name: "interval_CRP",
                    value: "60",
                    tip: "s（默认：60）",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'num|',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "优先级",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "level",
                    name: "level",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'num|',
                        ass_check: function( check ) {
                            
                        }
                    }
                }
            ]
        },
        {
            title: "启用",
            sub_items: [
                {
                    enable: true,
                    type: "checkbox",
                    id: "enable",
                    name: "enable",
                    label: "启用",
                    value: "",
                    functions: {
                    },
                }
            ]
        },
        
    ]
};

var list_panel_render = {
    'version': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text == "1 2"){
                result_render = "默认";
            }else if(default_rendered_text == "1"){
                result_render = "RIPV1";
            }else if(default_rendered_text == "2"){
                result_render = "RIPV2";
            }
            return '<span>' + result_render + '</span>';
        },
    },
    
};


var list_panel_config = {
    url: "/cgi-bin/dynamicmulticast.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_dynamic_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    /* event_handler: {
        before_load_data: function( list_abj,data ) {
            if(list_abj.total_num < 15){
                list_panel_config.page_size = list_abj.total_num;
            }
        },
    }, */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
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
            "title": "RP汇合点",        //一般text类型需要title,不然列表没有标题
            "name": "point_rp",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "组播地址组",
            "name": "multicast_addrgroup",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "模式",
            "name": "model",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "Cand-RP发送间隔",
            "name": "interval_CRP",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "优先级",
            "name": "level",
            "width": "15%"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "15%"
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "新建组播路由",
            functions: {
                onclick: "add_rule(this);"
            }
        },
        {
            "enable": true,
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
    is_default_search: true,          /* ===可选===，默认是true，控制默认的搜索条件 */
    
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

//获取系统可用接口
function load_usable_interface(){
    var sending_data = {
        ACTION: "load_usable_interface",
    };
    function ondatareceived(data) {
        useable_interfaces = data.useable_interfaces;
        var closed_interface = data.opened_interface;
        var opened_interface = useable_interfaces;
        if(closed_interface.length > 0){
            opened_interface = $.grep(useable_interfaces,function(val,key){
                for(var i=0;i<closed_interface.length;i++){
                    if(val == closed_interface[i]){
                        return false;
                        break;
                    }else if( i == (closed_interface.length-1) ){
                        return true;
                    }
                }
            });
        }
        
        $("#left_select").empty();
        for(var i = 0;i < opened_interface.length;i++){
            $("#left_select").append("<option value='"+opened_interface[i]+"'>"+opened_interface[i]+"</option>");
        }
        $("#right_select").empty();
        for(var i = 0;i < closed_interface.length;i++){
            $("#right_select").append("<option value='"+closed_interface[i]+"'>"+closed_interface[i]+"</option>");
        }
    }
    do_request(sending_data, ondatareceived);
}
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/dynamicmulticast.cgi',
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//启用禁用调用函数
function change_switch(){
    var enabled = "";
    if($("#enableDYNAMIC").is(":checked")){
        enabled = "on";
    }else{
        enabled = "off";
    }
    var sending_data = {
        ACTION: "switch",
        ENABLED: enabled,
    };

    function ondatareceived(data) {
        list_panel.update_info(true);
    }

    do_request(sending_data, ondatareceived);
}
//动态添加接口
function add_interface(){
    $("#left_select").find("option:selected").each(function(){
        $(this).remove();
        $("#right_select").append("<option selected value="+$(this).val()+">"+$(this).text()+"</option>");
    });
}
//删除接口
function delete_interface(){
    $("#right_select").find("option:selected").each(function(){
        $(this).remove();
        $("#left_select").append("<option value="+$(this).val()+">"+$(this).text()+"</option>");
    });
}