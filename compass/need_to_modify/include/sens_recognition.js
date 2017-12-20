$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    
    list_panel.render();
    message_manager.render();
    add_panel.render();
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
    url: "/cgi-bin/sens_recognition.cgi",
    check_in_id: "mesg_box_url",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/sens_recognition.cgi",
    check_in_id: "panel_url_add",
    panel_name: "add_panel",
    rule_title: "敏感信息定义",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            console.log(data_item);
        },
        after_load_data: function( add_obj,data_item ) {
            
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,

    items_list: [
            {
                title: "名称*",
                sub_items: [
                    {
                        enable: true,
                        type: "text",
                        tip: "（最多10个字符）",
                        id: "name",
                        name: "name",
                        check: {
                            type: "text",
                            required: 1,
                            // nameLength:$("#name").val().length,
                            check:'specify_name|',
                            ass_check:function(eve){
                                var name = $("#name").val();
                                if(name.length > 10){
                                    return "最多输入10个字符！";
                                }
                            }
                        }
                    }
                ]
            }, {
                title: "说明*",
                sub_items: [
                    {
                        enable: true,
                        type: "text",
                        tip: "（最多30个字符）",
                        id: "description",
                        name: "description",
                        check: {
                            type: "text",
                            required: 1,
                            check:'note|',
                            other_reg:'!/^\$/',
                            ass_check:function(eve){
                                var content = $("#description").val();
                                if(content.length > 30){
                                    return "最多输入30个字符！";
                                }
                            }
                        }
                    }
                ]
            }, {
                title: "敏感信息定义*",
                sub_items: [
                    {
                        enable: true,
                        type: "textarea",
                        tip: "（每行一个,不必输入括号）",
                        id: "rules",
                        name: "rules",
                        check: {
                            type: "textarea",
                            required: 1,
                            check:'regexp|',
                            ass_check:function(eve){
                                // var action = eve._getCURElementsByName("ACTION","input","CLASS_FORM")[0].value;
                                    var msg = '';
                                    var rule_data = $("#rules").val();
                                        rule_data = rule_data.replace(/\'/g, '"');
                                    var temp_length = rule_data.split('\n');
                                    for (var i = 0; i < temp_length.length; i++) {
                                        if(temp_length[i].length > 200){
                                            msg = '每行字符限定200以内';
                                            return msg;
                                        }
                                    };
                                    var sending_data = {
                                        ACTION: 'check_rule',
                                        rule_data: rule_data
                                    };
                                    $.ajax({
                                        type: "post",
                                        url: '/cgi-bin/sens_recognition.cgi',
                                        async: false,
                                        data: sending_data,
                                        success: function(data){
                                            console.log(JSON.parse(data) );
                                            if(JSON.parse(data).error_rule){
                                                var temp_rule = JSON.parse(data).error_rule.split(';');
                                                var temp_status = JSON.parse(data).error_status.split(';');
                                                for (var i = 0; i < temp_rule.length; i++) {
                                                    if(i == 0){
                                                        msg = temp_status[i];
                                                    }
                                                    else{
                                                        msg = msg + '第'+temp_rule[i]+'条' +':'+ temp_status[i] + ';';
                                                    }
                                                };
                                            }
                                        }
                                    });
                                    return msg;
                            }
                        }
                    }
                ]
            }
        ]
};

var list_panel_render = {
    'checkbox': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if( data_item.type == "0" ){
                result_render = "";
            }else{
                result_render = default_rendered_text;
            }
            return result_render;
        }
    },
    'type': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if( default_rendered_text == "0" ){
                result_render = "内置";
            }else{
                result_render = "用户自定义";
            }
            return result_render;
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
            
            if(data_item.type == "0"){
                var edit_button = {
                enable: true,
                id: "edit_item",
                name: "edit_item",
                button_icon: "edit_disabled.png",
                class:"action-image"
                }
                var delete_button = {
                    enable: true,
                    id: "delete_item",
                    name: "delete_item",
                    button_icon: "delete_disabled.png",
                    class:"action-image"
                }
            
            }else{
                var edit_button = {
                enable: true,
                id: "edit_item",
                name: "edit_item",
                button_icon: "edit.png",
                value: data_item.id,
                    functions: {
                        onclick: "list_panel.edit_item(this.value);"
                    },
                     class:"action-image"
                }
                var delete_button = {
                    enable: true,
                    id: "delete_item",
                    name: "delete_item",
                    button_icon: "delete.png",
                    value: data_item.id,
                    functions: {
                        onclick: "list_panel.delete_item(this.value);"
                    },
                     class:"action-image"
                }
            }
            var render_edit_button = PagingHolder.create_action_buttons( [edit_button] );
            var render_delete_button = PagingHolder.create_action_buttons( [delete_button] );
            var action_buttons = render_edit_button+render_delete_button;
            return action_buttons;
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/sens_recognition.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_url_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持名称、说明关键字查询",
        title: ""
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
            "width": "2%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": true,
            "title":"序号",
            "type": "text",
            "name": "index",
            "width": "3%"
        }, {
            "enable": true,
            "type": "text",
            "title": "名称",
            "name": "name",
            "width": "20%"
        },{
            "enable": true,
            "type": "text",
            "title": "说明",
            "name": "description",
            "width": "60%"
        },{
            "enable": true,
            "type": "text",
            "title": "类型",
            "name": "type",
            "width": "8%",
            "td_class":"align-center"
        },  {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "7%",
            "td_class":"align-center",
             "class":"action-image"

        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "新建",
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
    event_handler:{
        after_load_data: function( add_obj,data_item ) {
            // console.log(data_item);
        }
    },
    is_default_search: true          /* ===可选===，默认是true，控制默认的搜索条件 */
}


function delete_selected_items(e) {
    var ids = "";
    if(e.id == "delete_selected"){
        var checked_items = list_panel.get_checked_items();
        if( checked_items < 1){
            message_manager.show_popup_note_mesg("请先选中策略项");
            return;
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


function add_rule( element ) {
    add_panel.show();
}