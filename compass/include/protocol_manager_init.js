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
    $("#description").attr("maxLength","128");
    $("#search_key_for_list_panel").css("width","250px");
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/protocol_manager.cgi",
    check_in_id: "mesg_box_pro",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/protocol_manager.cgi",
    check_in_id: "panel_pro_add",
    panel_name: "add_panel",
    rule_title: "协议管理",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
            
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "名称",
        sub_items: [{
            enable: true,
            type: "text",
            id: "name",
            name: "name",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check:'other',
                other_reg:'!/^\$/',
                ass_check: function( check ) {

                }
            }
        }]
    }, {
        title: "协议",
        sub_items: [{
            enable: true,
            type: "select",
            id: "protocol",
            name: "protocol",
            options: [{
                text: "TCP",
                value: "tcp"
            }, {
                text: "UDP",
                value: "udp"
            }]
        }]
    }, {
        title: "端口",
        sub_items: [{
            enable: true,
            type: "text",
            id: "port",
            name: "port",
            tip: "（1-65535）",
            value: "",
            check: {
                type: "text",
                required: 1,
                check: 'port|',
                ass_check: function( check ) {
                }
            }
        }]
    }, {
        title: "超时时间",
        sub_items: [{
            enable: true,
            type: "text",
            id: "outtime",
            name: "outtime",
            tip: "（1-65535分钟）",
            value: "",
            check: {
                type: "text",
                required: 1,
                check: 'num|',
                ass_check: function( check ) {
                    var val = $("#outtime").val();
                    if(val > 65535){
                        return "超时时间应在1-65535之间";
                    }
                }
            }
        }]
    }, {
        title: "描述",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "description",
            name: "description",
            value: "",
			check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                type:'textarea',        /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required:'0',       /* **必填**，1表示必填，0表示字段可为空 */
                check:'note|',      /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                ass_check:function( check ){
                    /*
                     * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
                     *
                     * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
                     *
                     * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
                     */

                }
            }
			
        }]
    }, {
        title: "启用",
        sub_items: [{
            enable: true,
            type: "checkbox",
            id: "enable",
            name: "enable",
            value: ""
        }]
    }]
};

// var list_panel_render = {
//      'protocol': {
//         render: function( default_rendered_text, data_item ) {
//             var result_render = "RIP";
//             return '<span>' + result_render + '</span>';
//         }
//     } 
// };
var list_panel_render = {
            'description':{
                render: function(default_rendered_text,data_item){
                    console.log(data_item.description);
                     var descr = data_item.description.trim();
                      return '<span>' + descr + '</span>';
                }
                    
            }            
}

var list_panel_config = {
    url: "/cgi-bin/protocol_manager.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_pro_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持名称、协议、端口、时间、描述查询",
        title: "",
        width:"200px"
    },
    panel_header: [{
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
        "title": "名称",        //一般text类型需要title,不然列表没有标题
        "name": "name",
        "width": "15%"
    }, {
        "enable": true,
        "type": "text",
        "title": "协议",
        "name": "protocol",
        "td_class": "align-center",
        "width": "15%"
    }, {
        "enable": true,
        "type": "text",
        "title": "端口",
        "name": "port",
        "td_class": "align-center",
        "width": "15%"
    }, {
        "enable": true,
        "type": "text",
        "title": "超时时间（分钟）",
        "name": "outtime",
        "td_class": "align-center",
        "width": "15%"
    },  {
        "enable": true,
        "type": "text",
        "title": "描述",
        "name": "description",
        "width": "20%"
    }, {
        "enable": true,
        "type": "action",
        "title": "活动/动作",
        "name": "action",
        "td_class": "align-center",
        "width": "10%"
    }],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "新建协议管理",
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
        if (checked_items.length === 0) {
            message_manager.show_popup_note_mesg('请选择要删除的规则')
            return
        }
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