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
    /* 绑定时间输入*/
    //ESONCalendar.bind("time_start");
    //ESONCalendar.bind("time_end");
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/remote_dial_vpn.cgi",
    check_in_id: "mesg_box_vpn",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/remote_dial_vpn.cgi",
    check_in_id: "panel_vpn_add",
    panel_name: "add_panel",
    rule_title: "VPN远程拨号用户",
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "用户名称*",
            sub_items: [ {
                enable: true,
                type: "text",
                id: "username",
                name: "username",
                check: {
                    type: "text",
                    required: 1,
                    check:'other',
                    other_reg:'!/^\$/',
                    ass_check: function( check ) {
                        var uname = $("#username").val();
                        var reg = /^[0-9a-zA-Z-_]+$/ig;
                        if(!reg.test(uname)){
                            return "用户名应由数字、字母、减号、下划线组成";
                        }
                        if(uname.length < 1 || uname.length > 20){
                            return "用户名长度应在1-20之间";
                        }
                    }
                }
            } ]
        }, {
            title: "密码*",
            sub_items: [ {
                enable: true,
                type: "password",
                id: "pwd",
                name: "pwd",
                check: {
                    type: "password",
                    required: 1,
                    check:'other',
                    other_reg:'!/^\$/',
                    ass_check: function( check ) {
                        var pwd = $("#pwd").val();
                        var reg = /^[0-9a-zA-Z]+$/ig;
                        if(!reg.test(pwd)){
                            return "密码应由数字、字母组成";
                        }
                        if(pwd.length < 6 || pwd.length > 15){
                            return "密码长度应在6-15之间";
                        }
                    }
                }
            } ]
        }, {
            title: "重输密码*",
            sub_items: [ {
                enable: true,
                type: "password",
                id: "pwd2",
                name: "pwd2",
                check: {
                    type: "password",
                    required: 1,
                    check:'other',
                    other_reg:'!/^\$/',
                    ass_check: function( check ) {
                        var pwd2 = $("#pwd2").val();
                        var reg = /^[0-9a-zA-Z]+$/ig;
                        if(!reg.test(pwd2)){
                            return "重复密码应由数字、字母组成";
                        }
                        if(pwd2.length < 6 || pwd2.length > 15){
                            return "重复密码长度应在6-15之间";
                        }
                        var pwd1 = $("#pwd").val();
                        if(pwd2 != pwd1){
                            return "重复密码与密码不一样";
                        }
                    }
                }
            } ]
        }, {
            title: "备注",
            sub_items: [ {
                enable: true,
                type: "text",
                id: "note",
                name: "note",
                check: {
                    type: "text",
                    required: 0,
                    check: 'note|'
                }
            } ]
    } ]
};

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
    url: "/cgi-bin/remote_dial_vpn.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_vpn_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持用户名称、备注关键字查询",
        title: ""
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
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
            "title": "用户名称",        //一般text类型需要title,不然列表没有标题
            "name": "username",
            "width": "35%"
        }, {
            "enable": true,
            "type": "text",
            "title": "备注",
            "name": "note",
            "width": "50%"
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
            button_text: "添加拨号用户",
            functions: {
                onclick: "add_rule(this);"
            }
        }, {
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
    is_default_search: true          /* ===可选===，默认是true，控制默认的搜索条件 */
    
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