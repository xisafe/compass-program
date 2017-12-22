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
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/interface_level.cgi",
    check_in_id: "mesg_box_level",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/interface_level.cgi",
    check_in_id: "panel_level_add",
    panel_name: "add_panel",
    rule_title: "监听接口",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
            $("#interface").append("<option selected value="+data_item.interface+">"+data_item.interface+"</option>");
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "选择接口",
            sub_items: [ {
                enable: true,
                type: "select",
                id: "interface",
                name: "interface"
            } ]
        }, {
            title: "优先级",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "level",
                    name: "level",
                    tip: "（范围1-255）",
                    check: {
                        type: "text",
                        required: 1,
                        check:'num|',
                        ass_check:function(eve){
                            var level = $("#level").val();
                            if(level > 255){
                                return "请输入1-255的正整数！";
                            }
                        }
                    }
                } ]
        }, {
            title: "备注",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    // style: "width: 300px;",
                    id: "note",
                    name: "note",
                    check: {
                        type: "text",
                        required: 0,
                        check:'note|',
                        ass_check:function(eve){
                            // var mesg = "";
                            // var note = $("#note").val();
                            // if(note.length > 40){
                            //     mesg = "不能超过40个字符";
                            // }
                            // return mesg;
                        }
                    }
                }
            ]
        }
    ]
};

var list_panel_render = {
    'notice_content': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text.length > 45 ){
                result_render = default_rendered_text.substr(0,45)+"...";
            }else{
                result_render = default_rendered_text;
            }
            return '<span>' + result_render + '</span>';
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/interface_level.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_level_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    event_handler: {
        before_load_data: function( list_obj ) {
            
        },
        after_load_data: function ( list_obj, response ) {
            $("#interface").empty();
            for(var i=0;i<response.interfaces.length;i++){
                $("#interface").append("<option value="+response.interfaces[i]+">"+response.interfaces[i]+"</option>");
            }
        }
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "td_class": "align-center",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
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
            "title": "接口名称",
            "name": "interface",
            "width": "20%"
        }, {
            "enable": true,
            "type": "text",
            "title": "优先级",
            "name": "level",
            "td_class":"align-center",
            "width": "20%"
        },{
            "enable": true,
            "type": "text",
            "title": "备注",
            "name": "note",
            "width": "45%"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "td_class":"align-center",
            "width": "10%"
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            type: "image_button",
            //button_icon: "add16x16.png",
            button_icon: "",
            button_text: "设置接口优先级",
            functions: {
                onclick: "add_rule(this);"
            }
        }, {
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
    is_default_search: false          /* ===可选===，默认是true，控制默认的搜索条件 */
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