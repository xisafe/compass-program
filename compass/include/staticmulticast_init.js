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
    
    add_panel.hide();
    list_panel.update_info(true);
    load_usable_interface();
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/staticmulticast.cgi",
    check_in_id: "mesg_box_static",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/staticmulticast.cgi",
    check_in_id: "panel_static_add",
    panel_name: "add_panel",
    rule_title: "组播路由",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,sending_data ) {
            var count = $("#selected_interface option").length;
            var tmp = [];
            for(var i=0;i<count;i++){
                tmp.push($("#selected_interface option").get(i).value);
            }
            var tamp = tmp.join("|");
            return sending_data = sending_data + "&selected_interface_save=" + tamp;
        },
        before_load_data: function( add_obj,data_item ) {
            var selected_interfaces = data_item.output_multicast.split("&");
            var left_members = $.grep(useable_interfaces,function(val,key){
                for(var i=0;i<selected_interfaces.length;i++){
                    if(val == selected_interfaces[i]){
                        return false;
                        break;
                    }else if( i == (selected_interfaces.length-1) ){
                        return true;
                    }
                }
            });
            $("#usable_interface").empty();
            for(var j=0;j<left_members.length;j++){
                $("#usable_interface").append("<option value='"+left_members[j]+"'>"+left_members[j]+"</option>");
            }
            $("#selected_interface").empty();
            for(var k=0;k<selected_interfaces.length;k++){
                $("#selected_interface").append("<option selected value='"+selected_interfaces[k]+"'>"+selected_interfaces[k]+"</option>");
            }
        },
        after_load_data: function( add_obj,data_item ) {
            
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "组播源*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "s_multicast",
                    name: "s_multicast",
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
        }, {
            title: "组播地址*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "addr_multicast",
                    name: "addr_multicast",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'other',
                        other_reg: '!/^\$/',
                        ass_check: function( check ) {
                            var msg = "";
                            var val = $("#addr_multicast").val();
                            /* if(!check.validip(val)){
                                msg = val+"是非法的ip地址！";
                            } */
                            var tmp = val.split(".");
							if(/[^0-9|\.]/.test(val)){
								msg = val+"是非法的组播地址！";
							}
                            if(tmp[0] < 224 || tmp[0] > 239 || tmp[1] < 0 || tmp[1] > 255 || 
                            tmp[2] < 0 || tmp[2] > 255 || tmp[3] < 0 || tmp[3] > 255 || tmp.length != 4){
                                msg = val+"是非法的组播地址！";
                            }
                            return msg;
                        }
                    }
                }
            ]
        }, {
            title: "组播入接口*",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "input_multicast",
                    name: "input_multicast",
                    value: ""
                }
            ]
        }, {
            title: "组播出接口*",
            sub_items:[
                {
                    enable:true,
                    type:"items_group",
                    item_style:"width:44%;margin: 0px -4px;",
                    "sub_items":[
                        {
                            "enable": true,
                            "type": "select",
                            "label": "可用接口",
                            "style": "height:115px",
                            "id": "usable_interface",
                            "name": "usable_interface",
                            "multiple": true
                        }
                    ]
                }, {
                    enable:true,
                    type:"items_group",
                    item_style:"width:13%",
                    "sub_items":[
                        {
                            "enable": true,
                            "type": "button",
                            "id": "btn_right",
                            "name": "btn_right",
                            "value": ">>",
                            "style": "width:50px;",
                            functions: {
                                onclick: "add_interface();"
                            }
                        }, {
                            "enable": true,
                            "type": "button",
                            "id": "btn_left",
                            "name": "btn_left",
                            "value": "<<",
                            "style": "width:50px;margin-top:8px;margin-bottom:13px;",
                            functions: {
                                onclick: "delete_interface();"
                            }
                        }, {
                            "enable": true,
                            "type": "label",
                            "value": "",
                            "item_style": "height:0px;width:50px"
                        }
                    ]
                }, {
                    "enable":true,
                    "type":"items_group",
                    "item_style":"width:25%;margin: 0px -4px;",
                    "sub_items":[
                        {
                            "enable": true,
                            "type": "select",
                            "label": "已选接口",
                            "style": "height:115px",
                            "id": "selected_interface",
                            "name": "selected_interface",
                            "multiple": true,
                            "options": []
                        }
                    ]
                }
            ]
        }, {
            title: "启用",
            sub_items: [
                {
                    enable: true,
                    type: "checkbox",
                    id: "enable",
                    name: "enable",
                    label: "启用",
                    value: ""
                }
            ]
        }
    ]
};

var list_panel_render = {
    'output_multicast': {
        render: function( default_rendered_text, data_item ) {
            var outputs = default_rendered_text.split("&");
            var result_render = outputs.join(",");
            return '<span>' + result_render + '</span>';
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/staticmulticast.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_static_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持关键字查询",
        title: ""
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            },
            "td_class":"align-center"
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
            "width": "21%"
        }, {
            "enable": true,
            "type": "text",
            "title": "组播地址",
            "name": "addr_multicast",
            "width": "21%"
        }, {
            "enable": true,
            "type": "text",
            "title": "组播入接口",
            "name": "input_multicast",
            "width": "21%"
        }, {
            "enable": true,
            "type": "text",
            "title": "组播出接口",
            "name": "output_multicast",
            "width": "21%"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "10%",
            "td_class":"align-center"
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "新建组播路由",
            // style:"padding:3px 5px",
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
    $("#username").attr("value","");
    $("#pwd").attr("value","");
    add_panel.show();
}
//获取系统可用接口
function load_usable_interface(){
    var sending_data = {
        ACTION: "load_usable_interface"
    };
    function ondatareceived(data) {
        useable_interfaces = data.useable_interfaces;
        $("#input_multicast").empty();
        for(var i = 0;i < useable_interfaces.length;i++){
            $("#input_multicast").append("<option value='"+useable_interfaces[i]+"'>"+useable_interfaces[i]+"</option>");
        }
        $("#usable_interface").empty();
        for(var i = 0;i < useable_interfaces.length;i++){
            $("#usable_interface").append("<option value='"+useable_interfaces[i]+"'>"+useable_interfaces[i]+"</option>");
        }
    }
    do_request(sending_data, ondatareceived);
}
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/staticmulticast.cgi',
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
    if($("#enableStatic").is(":checked")){
        enabled = "on";
    }else{
        enabled = "off";
    }
    var sending_data = {
        ACTION: "switch",
        ENABLED: enabled
    };

    function ondatareceived(data) {
        list_panel.update_info(true);
    }

    do_request(sending_data, ondatareceived);
}
//动态添加接口
function add_interface(){
    $("#usable_interface").find("option:selected").each(function(){
        $(this).remove();
        $("#selected_interface").append("<option selected value="+$(this).val()+">"+$(this).text()+"</option>");
    });
}
//删除接口
function delete_interface(){
    $("#selected_interface").find("option:selected").each(function(){
        $(this).remove();
        $("#usable_interface").append("<option value="+$(this).val()+">"+$(this).text()+"</option>");
    });
}