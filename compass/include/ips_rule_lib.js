/*
 * 描述: 特征库管理
 *
 * 作者: WangLin，245105947@qq.com
 * 历史：
 *       2015.01.05 WangLin创建
 */
$( document ).ready(function() {
    load_init_data();
    /* 渲染面板 */
    message_manager.render();
    add_lib_panel.render();
    merge_lib_panel.render();
    copy_lib_panel.render();
    import_lib_panel.render();
    list_lib_panel.render();
    template_list_panel.render();

    add_lib_panel.hide();
    merge_lib_panel.hide();
    copy_lib_panel.hide();
    import_lib_panel.hide();
    template_list_panel.hide();

    /* 设置面板关联 */
    // add_lib_panel.set_ass_list_panel( list_lib_panel );
    // list_lib_panel.set_ass_add_panel( add_lib_panel );

    add_lib_panel.set_ass_message_manager( message_manager );
    merge_lib_panel.set_ass_message_manager( message_manager );
    copy_lib_panel.set_ass_message_manager( message_manager );
    import_lib_panel.set_ass_message_manager( message_manager );
    edit_event_panel.set_ass_message_manager( message_manager );
    list_lib_panel.set_ass_message_manager( message_manager );

    $("#TransparentBorder_template_list_panel").css("z-index",20000);
    $("#popup-mesg-border-box-cover-template_list_panel").css("z-index",19999);

    /* 加载数据 */
    check_running();
    list_lib_panel.update_info( true );
    template_list_panel.update_info( true );
    $( "#exception_ips_item" ).hide();
    $('#tool-1021').hide()
});

/*
 * 加载Ext所需文件
 */
Ext.require([
    'Ext.data.TreeStore',
    'Ext.tree.Panel',
    'Ext.form.ComboBox',
    'Ext.form.Panel',
    'Ext.window.Window'
]);

/*
 * 定义全局变量
 */
var panel_ass_url = "/cgi-bin/ips_rule_lib.cgi";

var message_manager_config = {
    url: panel_ass_url,
    check_in_id: "rule_libraries_mesg_box"
};

var add_lib_config = {
    url: panel_ass_url,
    check_in_id: "rule_libraries_add",
    panel_name: "rule_libraries_add",
    rule_title_adding_prefix: "新建",
    rule_title: "特征库",
    is_modal: true,
    modal_config: {
        modal_box_size: "m"
    },
    is_panel_closable: true,
    is_panel_stretchable: false,
    // is_rule_title_icon: false,
    event_handler: {
        after_save_data: function( add_obj, received_data ) {
            list_lib_panel.update_info( true );
            if ( add_lib_panel.is_operation_succeed( received_data ) ) {
                adding_lib_flag = 0; //添加成功后将添加状态重置为未添加状态
            }
        }
    },
    items_list: [{
        title: "名称 *",
        sub_items: [{
            enable: true,
            type: "text",
            name: "name",
            value: "",
            style: "height:22px;width:200px;",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check: 'name|',
                ass_check: function( check ) {

                }
            }
        }, {
            enable: true,
            type: "text",
            item_style: "display: none;",
            name: "type"
        }, {
            enable: true,
            type: "text",
            item_style: "display: none;",
            name: "create_time"
        }, {
            enable: true,
            type: "text",
            item_style: "display: none;",
            name: "filepath"
        }]
    }, {
        title: "说明",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "add_lib_note",
            name: "note",
            value: "",
            check: {
                type: "textarea",
                required: 0,
                check: 'note|',
                ass_check: function( check ) {
                    var msg=''
                    var note = $("#add_lib_note").val();
                    if ( note.length > 128 ) {
                        return msg="说明信息0-128个字符";
                    }
                }
            }
        }]
    }, {
        title: "选择特征事件 *",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "rules",
            name: "rules",
            value: "",
            readonly: true,
            functions: {
                onclick: "choose_events_when_adding_lib();"
            }
        }, {
            enable: true,
            type: "text",
            id: "rules_id",
            name: "rules_id",
            readonly: true,
            item_style: "display: none;"
        }]
    }]
};

var merge_lib_config = {
    url: panel_ass_url,
    check_in_id: "rule_libraries_merge",
    panel_name: "rule_libraries_merge",
    rule_title_adding_icon: "merge.png",
    rule_title_adding_prefix: "合并",
    rule_title: "特征库",
    is_modal: true,
    modal_config: {
        modal_box_size: "m"
    },
    is_panel_closable: true,
    is_panel_stretchable: false,
    event_handler: {
        after_save_data: function( add_obj, received_data ) {
            list_lib_panel.update_info( true );
        }
    },
    items_list: [{
        title: "名称 *",
        sub_items: [{
            enable: true,
            type: "text",
            name: "name",
            check: {
                type: "text",
                required: 1,
                check: "name|",
                ass_check: function() {

                }
            }
        }]
    }, {
        title: "说明",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "merge_lib_note",
            name: "note",
            check: {
                type: "textarea",
                required: 0,
                check: "note|",
                ass_check: function( check ) {
                    var msg=''
                    var note = $( "#merge_lib_note" ).val();
                    if ( note.length > 128 ) {
                        return msg="说明信息0-128个字符";
                    }
                }
            }
        }]
    }, {
        title: "已选择特征库 *",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "choosed_rule_libs",
            name: "choosed_rule_libs",
            readonly: true,
            functions: {
                onclick: ""
            },
            check: {
                type: "text",
                required: 0,
                check: "other|",
                other_reg: "/.*/"
            }
        }]
    }]
};

var copy_lib_config = {
    url: panel_ass_url,
    check_in_id: "rule_libraries_copy",
    panel_name: "rule_libraries_copy",
    rule_title_adding_icon: "copy.png",
    rule_title_adding_prefix: "衍生",
    rule_title: "特征库",
    is_modal: true,
    modal_config: {
        modal_box_size: "s"
    },
    is_panel_closable: true,
    is_panel_stretchable: false,
    event_handler: {
        after_save_data: function( add_obj, received_data ) {
            list_lib_panel.update_info( true );
        }
    },
    items_list: [{
        title: "名称 *",
        sub_items: [{
            enable: true,
            type: "text",
            name: "name",
            check: {
                type: "text",
                required: 1,
                check: "name|",
                ass_check: function() {

                }
            }
        }, {
            enable: true,
            type: "text",
            id: "to_copy_lib",
            name: "to_copy_lib",
            readonly: true,
            item_style: "display: none;"
        }]
    }, {
        title: "说明",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "breed_lib_note",
            name: "note"
            // check: {
            //     type: "textarea",
            //     required: 0,
            //     check: "note|",
            //     ass_check: function() {

            //     }
            // }
        }]
    }]
};

var import_lib_config = {
    url: panel_ass_url,
    check_in_id: "rule_libraries_import",
    panel_name: "rule_libraries_import",
    rule_title_adding_icon: "upload.png",
    rule_title_adding_prefix: "导入",
    rule_title: "特征库",
    is_modal: true,
    modal_config: {
        modal_box_size: "m"
    },
    is_panel_closable: true,
    is_panel_stretchable: false,
    footer_buttons: {
        add: false,
        cancel: true,
        import: true
    },
    items_list: [{
        title: "特征库文件",
        sub_items: [{
            enable: true,
            type: "file",
            name: "rule_lib_file",
            style:"height:24px",
            check: {
                type: "file",
                required: 1
            }
        }]
    }]
};

var edit_event_config = {
    url: panel_ass_url,
    check_in_id: "rule_lib_edit_event",
    panel_name: "rule_lib_edit_event",
    rule_title: "特征事件",
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 2000
    },
    is_panel_closable: true,
    is_panel_stretchable: false,
    event_handler: {
        after_load_data: function( add_obj, data_item ) {
            choose_merge_type( $(".merge_type_item:checked")[0] );
            choose_exception_type( document.getElementById("exception_type") );
            document.getElementById( "event_of_lib_name" ).value = edit_lib.name;
            document.getElementById( "event_of_lib_id" ).value = edit_lib.id;
        },
        after_save_data: function( add_obj, received_data ) {
            Ext.getCmp( "event_detail_tree_grid" ).getStore().load();
        },
        before_save_data: function ( add_obj, sending_data ) {
            var respond_type_item = $( ".respond_type_item:checked" );
            var respond_type_item_notid = $( ".respond_type_item:checked" ).not('input[id="log"]');
            if ( respond_type_item.length === 0 ) {
                message_manager.show_popup_error_mesg( "至少选择一种响应方式" );
                return false;
            }else if(respond_type_item_notid.length>1){
                message_manager.show_popup_error_mesg( "响应方式中允许、丢弃、RST阻断最多只能选择一个" );
                return false;
            }
            

        },
    },
    items_list: [{
        title: "事件名称",
        sub_items: [{
            enable: true,
            type: "text",
            id: "event_name",
            name: "event_name",
            readonly: true
        }, {
            enable: true,
            type: "text",
            id: "event_of_lib_name",
            name: "lib_name",
            readonly: true,
            item_style: "display: none;"
        }, {
            enable: true,
            type: "text",
            id: "event_of_lib_id",
            name: "lib_id",
            readonly: true,
            item_style: "display: none;"
        }]
    }, {
        title: "事件类型",
        sub_items: [{
            enable: true,
            type: "text",
            id: "event_type",
            name: "event_type",
            value: "特征事件",
            readonly: true
        }]
    },{
        title: "事件有效性",
        sub_items: [{
            enable: true,
            type: "checkbox",
            name: "event_enable"
        }]
    }, {
        title: "响应方式",
        sub_items: [{
            enable: true,
            type: "items_group",
            sub_items: []
        }]
    }, {
        title: "合并方式",
        sub_items: [{
            enable: true,
            type: "items_group",
            id: "merge_type",
            item_style: "width: 100%;",
            sub_items: [{
                enable: true,
                type: "radio",
                id: "merge_type_none",
                name: "merge_type",
                class: "merge_type_item",
                value: "none",
                label: "不合并",
                checked: true,
                functions: {
                    onclick: "choose_merge_type(this);"
                },
                check: {
                    type: "radio",
                    required: 0,
                    ass_check: function( check ) {
                        var value = $( ".merge_type_item" ).length;
                        if ( value == 0 ) {
                            return "必须选择一种合并方式";
                        }
                    }
                }
            }, {
                enable: true,
                type: "radio",
                id: "merge_type_s_ip",
                name: "merge_type",
                class: "merge_type_item",
                value: "mergeby_src",
                label: "按<源IP>合并",
                functions: {
                    onclick: "choose_merge_type(this);"
                }
            }, {
                enable: true,
                type: "radio",
                id: "merge_type_d_ip",
                name: "merge_type",
                class: "merge_type_item",
                value: "mergeby_dst",
                label: "按<目标IP>合并",
                functions: {
                    onclick: "choose_merge_type(this);"
                }
            }, {
                enable: true,
                type: "radio",
                id: "merge_type_both",
                name: "merge_type",
                class: "merge_type_item",
                value: "mergeby_ip",
                label: "按<源IP + 目标IP>合并",
                functions: {
                    onclick: "choose_merge_type(this);"
                }
            }]
        }, {
            enable: true,
            type: "items_group",
            item_id: "merge_config_item",
            item_label: "合并参数",
            item_style: "width: 100%;display: none;",
            sub_items: [{
                enable: true,
                type: "text",
                label: "合并周期:",
                id: "merge_interval",
                name: "merge_interval",
                tip: "(单位：秒，范围：1~120)",
                disabled: true,
                item_id: "merge_interval_item",
                check: {
                    type: "text",
                    required: 1,
                    check: "int",
                    ass_check: function( check ) {
                        var value = $( "#merge_interval" ).val();
                        var merge_type = $( ".merge_type_item:checked" ).val();
                        if ( merge_type == "none" ) {
                            return;
                        } else {
                            if ( value < 1 || value > 120 ) {
                                return "请填入1~120的数字"
                            }
                        }
                    }
                }
            }, {
                enable: true,
                type: "text",
                label: "最大合并次数:",
                id: "max_merge_count",
                name: "max_merge_count",
                disabled: true,
                item_id: "max_merge_count_item",
                check: {
                    type: "text",
                    required: 1,
                    check: "int|",
                    ass_check: function( check ) {
                        var value = $( "#max_merge_count" ).val();
                        var merge_type = $( ".merge_type_item:checked" ).val();
                        if ( merge_type == "none" ) {
                            return;
                        } else {
                            if ( value < 1 ) {
                                return "请填入大于1的数字"
                            }
                        }
                    }
                }
            }]
        }]
    }, {
        title: "排除IP",
        sub_items: [{
            enable: true,
            type: "items_group",
            item_style: "width: 40%;", 
            sub_items: [{
                enable: true,
                label: "排除方式：",
                label_style: "display:block;",
                type: "select",
                id: "exception_type",
                name: "exception_type",
                multiple: false,
                item_id: "exception_item",
                functions: {
                    onkeyup: "choose_exception_type(this);",
                    onchange: "choose_exception_type(this);"
                },
                options: [{
                    value: "none",
                    text: "不排除"
                }, {
                    value: "by_src",
                    text: "按源IP排除"
                }, {
                    value: "by_dst",
                    text: "按目标IP排除",
                    selected: true
                }],
                check: {
                    type: "select-one",
                    required: 1,
                    ass_check: function( check ){
                        
                    }
                }
            }, {
                enable: true,
                type: "label",
                value: "",
                item_style: "height: 28px;width: 200px;"
            }]
        }, {
            enable: true,
            type: "textarea",
            label: "排除IP地址：",
            label_style: "display:block;",
            id: "exception_ips",
            name: "exception_ips",
            value: "",
            tip: "(每行一个)",
            item_id: "exception_ips_item",
            item_style: "width: 50%;", 
            check: {
                type: "textarea",
                required: 1,
                check: 'ip|ip_range',
                ass_check: function( check ) {

                }
            }
        }]
    }]
}

var list_lib_panel_render = {
    'type': {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = "用户";

            if ( data_item.type == "system" ) {
                rendered_text = "系统";
            }

            return rendered_text;
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
            var view_all_button = {
                enable: true,
                id: "view_all",
                name: "view_all",
                button_icon: "view_details.png",
                button_text: "查看详情",
                value: data_item.id,
                class:"action-image",
                functions: {
                    onclick: "view_rule_lib(this);"
                }
            };
            var breed_button = {
                enable: true,
                id: "breed_rule_lib",
                name: "breed_rule_lib",
                button_icon: "copy.png",
                button_text: "衍生",
                class:"action-image",
                value: data_item.id,
                functions: {
                    onclick: "copy_rule_lib(this);"
                }
            }

            var edit_button = {
                enable: true,
                id: "edit_rule_lib",
                name: "edit_rule_lib",
                button_icon: "edit.png",
                class:"action-image",
                button_text: "编辑",
                value: data_item.id,
                functions: {
                    onclick: "edit_rule_lib(this);"
                }
            }
            var del_button = {
                enable: true,
                id: "del_rule_lib",
                name: "del_rule_lib",
                button_icon: "delete.png",
                class:"action-image",
                button_text: "删除",
                value: data_item.id,
                functions: {
                    onclick: "del_rule_lib(this);"
                }
            }

            var rendered_view_all = PagingHolder.create_action_buttons( [view_all_button] );
            var rendered_breed_button = PagingHolder.create_action_buttons( [breed_button] );
            var rendered_export_button = '<a href="' + panel_ass_url + '?ACTION=export_data&id=' + data_item.id + '">' +
                                            '<input type="image" class="action-image" title="导出" src="../images/download.png">' +
                                        '</a>';
            var rendered_edit_button = PagingHolder.create_action_buttons( [edit_button] );
            if ( data_item.type == "system" ) {
                del_button.disabled = true;
                del_button.button_icon = "delete_disabled.png";
            }
            var rendered_del_button = PagingHolder.create_action_buttons( [del_button] );

            var action_buttons = rendered_edit_button + rendered_breed_button + 
                                 rendered_export_button + rendered_del_button;
            if ( data_item.type == "system" ) {
                action_buttons = rendered_view_all + rendered_breed_button + rendered_export_button + rendered_del_button;
            }
            return action_buttons;
        }
    }
};

//为EXT面板的确定按钮添加更新事件
function ensure_extend () {
    $("#button-1020").on("click", function(){
        list_lib_panel.update_info(true);
    });
}
ensure_extend.flag = true;

var list_lib_config = {
    url: panel_ass_url,
    check_in_id: "rule_libraries_list",
    panel_name: "rule_libraries_list",
    render: list_lib_panel_render,
    page_size: 20,
    actions: {
        edit_item: function( data_item, on_finished ) {
            /* 开始书写自己的代码 */

            show_envents_grid_tree( data_item );
            /* 处理完成后**必须**调用执行 */
            if(ensure_extend.flag) {
                ensure_extend();
                ensure_extend.flag = false;
            }
            // on_finished();
        }
    },
    panel_header: [{
        enable: true,
        type: "checkbox",
        name: "checkbox",
        td_class:"align-center",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "类型",
        name: "type",
        td_class:"align-center",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "名称",
        name: "name",
        width: "20%"
    }, {
        enable: true,
        type: "text",
        title: "说明",
        name: "note",
        width: "45%"
    }, {
        enable: true,
        type: "text",
        title: "创建时间",
        name: "create_time",
        td_class:"align-center",
        width: "15%"
    }, {
        enable: true,
        type: "action",
        name: "action",
        td_class:"align-center",
        width: "10%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        button_icon: "add16x16.png",
        button_text: "新建特征库",
        functions: {
            onclick: "create_new_rule_lib(this);"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "merge.png",
        button_text: "合并特征库",
        functions: {
            onclick: "merge_rule_lib(this);"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "upload.png",
        button_text: "导入特征库",
        functions: {
            onclick: "import_rule_lib(this);"
        }
    },
    {
        enable: true,
        type: "image_button",
        button_icon: "delete.png",
        button_text: "删除选中",
        functions: {
            onclick: "delete_selected_items(this);"
        }
    }]
};

var list_template_config = {
    url: panel_ass_url,
    check_in_id: "template_list_panel",
    panel_name: "template_list_panel",
    panel_title: "请选择模板",
    page_size: 10,
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 20000
    },
    panel_header: [{
        enable: true,
        type: "radio",
        name: "radio",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "模板名称",
        name: "template_name",
        width: "30%"
    }, {
        enable: true,
        type: "text",
        title: "模板说明",
        name: "template_note",
        width: "60%"
    }],
    bottom_extend_widgets: {
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "apply_template_to_event_item( this );"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "cancel_choose_policy_template( this );"
            }
        }]
    }
};

var message_manager     = new MessageManager( message_manager_config );
var add_lib_panel       = new RuleAddPanel( add_lib_config );
var merge_lib_panel     = new RuleAddPanel( merge_lib_config );
var copy_lib_panel      = new RuleAddPanel( copy_lib_config );
var import_lib_panel    = new RuleAddPanel( import_lib_config );
var edit_event_panel    = new RuleAddPanel( edit_event_config );
var list_lib_panel      = new PagingHolder( list_lib_config );
var template_list_panel = new PagingHolder( list_template_config );

var adding_lib_flag = 0;        // 不为零表示正在新增一个特征库
var edit_lib = new Object();    // 当编辑一个特征库时，将被赋值为被编辑的特征库
var view_lib_flag = 0;          // 不为零表示正在查看一个特征库
var tool_button_border = "solid 1px #99BCE8";
var choosed_template_id = "";      // 记录当前选中的特征模板

function choose_events_when_adding_lib() {
    adding_lib_flag++; // 表征正在添加特征库,并且数字代表点开选择特征事件面板的次数
    show_event_tree_window();
}

function choose_events_when_editing_lib() {
    adding_lib_flag = 0;//表征正在编辑特征库
    show_event_tree_window();
}

function show_event_tree_window() {

    Ext.define('EventModel', {
        extend: 'Ext.data.Model',
        fields: [
           { name: 'id', type: 'string' },
           { name: 'name', type: 'string' },
           { name: 'text', type: 'string' },
           { name: 'expanded', type: 'boolean' },
           { name: 'leaf', type: 'boolean' },
           { name: 'checked', type: 'boolean', defaultValue: false },
        ],
        idProperty: 'eventmodel'
    });
    var event_tree_store = Ext.create('Ext.data.TreeStore', {
        model: 'EventModel',
        id: 'event_tree_store',
        proxy: {
            type: 'ajax',
            url: panel_ass_url,
            reader: {
                type: 'json'
            },
            actionMethods:{
                read: 'POST'
            }
        },
        listeners: {
            beforeload: function( store ){
                var params ={
                    ACTION: 'load_event_data',
                    type: "protcol",
                    search: "",
                    lib_name: ""
                };
                var data_type = Ext.getCmp( "event_type_select" );
                if ( data_type ) {
                    params.type = data_type.getValue();
                }
                var event_search = Ext.getCmp( "event_search" );
                if ( event_search ) {
                    params.search = event_search.getValue();
                }
                if ( !adding_lib_flag ) {
                    /* 正在编辑特征库 */
                    params.lib_name = edit_lib.name;
                } else {
                    /* 正在添加特征库 */
                    params.lib_name = "";
                }
                Ext.apply(store.proxy.extraParams, params);
            },
            load: {
                fn: function( store ) {
                    var responseData = store.getProxy().getReader().jsonData;
                    var label = Ext.getCmp( "total_info" );
                    if ( label ) {
                        label.setText( "共" + responseData.total + "条" );
                    }
                    Ext.getCmp('event_tree_panel').getRootNode().set( "checked", false );
                }
            }
        }
    });
    var event_tree_panel = Ext.getCmp('event_tree_panel');
    if(!event_tree_panel){
        event_tree_panel = Ext.create('Ext.tree.Panel', {
            id: 'event_tree_panel',
            closeAction: 'hide',
            width: 600,
            // width: document.body.clientWidth*0.37,
            height: 400,
            rootVisible: true,
            root: {
                text: '所有事件',
                id: '所有事件',
                name: '所有事件',
                leaf: false,
                expanded: true
            },
            store: event_tree_store,
            listeners: {
                checkchange:function( node, checked ){
                    node.eachChild( function ( child ) {
                        chd( child, checked );
                    });
                    //进行父级选中操作
                    parentnode( node ); 
                },
                itemdblclick: function( node, record ) {
                    var id = record.data.id;
                    var regx = /^\d+$/;
                    if ( id.match( regx ) ) {
                        view_event_detail( id );
                    }
                }
            }
        });
    }

    var event_type_store = Ext.create('Ext.data.Store', {
        fields: ['abbr', 'name'],
        data : [
            {"abbr":"protcol", "name":"按协议分类"},
            {"abbr":"eventtype", "name":"按事件类型分类"},
            {"abbr":"dangerlevel", "name":"按事件级别分类"}
        ]
    });
    var event_type_select = Ext.getCmp( 'event_type_select' );
    if ( !event_type_select ) {
        event_type_select = Ext.create('Ext.form.ComboBox', {
            width: 200,
            id: 'event_type_select',
            fieldLabel: '分组方式',
            labelAlign: "right",
            labelWidth: "70px",
            store: event_type_store,
            queryMode: 'local',
            displayField: 'name',
            valueField: 'abbr',
            value: "protcol",
            selectOnFocus: true,
            style: {
                float: "right"
            },
            listeners: {
                change: {
                    fn: function( me, newValue, oldValue ) {
                        var tree_store = me.up('window').down('treepanel').getStore();
                        tree_store.load();
                    }
                }
            }
        });
    };

    var event_tool_bar = Ext.getCmp( 'event_tool_bar' );
    if ( !event_tool_bar ) {
        event_tool_bar = Ext.create('Ext.toolbar.Toolbar', {
            id: "event_tool_bar",
            items: [{
                xtype: event_type_select
            },{
                xtype: "textfield",
                id: "event_search",
                name: "name",
                fieldLabel: '名称查询',
                fieldStyle: {
                    width: "150px"
                },
                labelAlign: "right",
                labelWidth: "60px",
                emptyText: "请输入名称关键字以查询...",
                width: 200,
                style: {
                    marginLeft: "5px"
                },
                allowBlank: true,
                enableKeyEvents: true,
                listeners: {
                    // change: {
                    //     fn: function( me ) {
                    //         me.up( "window" ).down( "treepanel" ).getStore().load();
                    //     }
                    // },
                    keyup: {
                        fn: function( me, event ) {
                            /*
                             * enter:13
                             */
                            // var event = event || window.event; //IE、FF下获取事件对象
                            var code = event.charCode || event.keyCode; //IE、FF下获取键盘码
                            if (code == 13){
                                ext_search(me);
                                // me.up("window").down("treepanel").getStore().load();
                            }
                        }
                    }
                }
            }, {
                xtype: "button",
                style: {
                    border: tool_button_border,
                    marginLeft: "5px",
                    marginRight: "5px"
                },
                icon: "/images/search16x16.png",
                text : "搜索",
                listeners: {
                    click: {
                        fn: function( me ) {
                            ext_search(me);
                            // me.up("window").down("treepanel").getStore().load();
                        }
                    }
                }
            }, {
                xtype: "label",
                id: "total_info",
                text: "共0条"
            }]
        });
    }

    var event_tree_window_title = "选择特征事件";
    if ( adding_lib_flag > 0 ) {
        
    }
    
    var event_tree_window = Ext.getCmp('event_tree_window');
    if(!event_tree_window){
        event_tree_window = Ext.create('Ext.window.Window', {
            title: '选择特征事件',
            id: 'event_tree_window',
            closeAction: 'hide',
            modal: true,
            // width: document.body.clientWidth*0.37,
            width: 600,
            height: 400,
            layout: 'fit',
            data: '',
            items: [
                { 
                    xtype: event_tree_panel
                }
            ],
            dockedItems: [{
                xtype: event_tool_bar,
                dock: 'top'
            }],
            buttons:[{
                text: '确定',
                handler: function( me ){
                    
                    var nodes = me.up('window').down('treepanel').getChecked();

                    var id_str = "", name_str = "";
                    var id_array = new Array();
                    var name_array = new Array();
                    for( var i = 0; i < nodes.length; i++ ){
                        var item = nodes[i];
                        if ( item.data.leaf ) {
                            name_array.push( item.data.name );
                            id_array.push( item.data.id );
                        }
                    }
                    id_str = id_array.join( "&" );
                    name_str = name_array.join( "\n" );

                    /* 判断是在添加还是编辑 */
                    if ( !adding_lib_flag ) {
                        //正在编辑
                        add_events_to_lib( id_str );
                    } else {
                        //正在添加
                        $( "#rules" ).val( name_str );
                        $( "#rules_id" ).val( id_str );
                    }

                    me.up('window').close();
                    Ext.getCmp( "event_detail_tree_grid" ).getStore().load();
                }
            },{
                text: '取消',
                class: "imaged-button",
                handler: function(me){
                    me.up('window').close();
                }
            }]
        })
    } else {
        if ( adding_lib_flag > 0 ) {
            /* 正在添加特征库 */
            if ( adding_lib_flag == 1 ) {
                Ext.getCmp( "event_type_select" ).setValue( "protcol" );
                Ext.getCmp( "event_search" ).setValue( "" );
                event_tree_window.down( "treepanel" ).getStore().load();
            } else {
                check_choosed_tree_item( event_tree_window.down( "treepanel" ).getRootNode( ), $( "#rules_id" ).val() );
            }
        } else {
            event_tree_window.down( "treepanel" ).getStore().load();
        }
    }
    event_tree_window.show();
}

function show_envents_grid_tree( data_item ) {
    edit_lib = data_item;
    Ext.define('EventDetailModel', {
        extend: 'Ext.data.Model',
        fields: [
           { name: 'id', type: 'string' },
           { name: 'name', type: 'string' },
           { name: 'text', type: 'string' },
           { name: 'enabled', type: 'string' },
           { name: 'dangerlevel', type: 'string' },
           { name: 'respond_type', type: 'string' },
           { name: 'merge_type', type: 'string' },
           { name: 'excepted_type', type: 'string' },
           { name: 'checked', type: 'boolean', defaultValue: false },
        ],
        idProperty: 'eventdetailmodel'
    });

    var event_detail_tree_store = Ext.create('Ext.data.TreeStore', {
        model: 'EventDetailModel',
        id: 'event_detail_tree_store',
        proxy: {
            type: 'ajax',
            url: panel_ass_url,
            reader: {
                type: 'json'
            },
            actionMethods:{
                read: 'POST'
            }
        },
        listeners: {
            beforeload: function( store ){
                var params ={
                    ACTION: 'load_event_grid_data',
                    type: "protcol",
                    search: "",
                    lib_name: edit_lib.name
                };
                var data_type = Ext.getCmp( "event_detail_type_select" );
                if ( data_type ) {
                    params.type = data_type.getValue();
                }
                var event_search = Ext.getCmp( "event_detail_search" );
                if ( event_search ) {
                    params.search = event_search.getValue();
                }
                Ext.apply(store.proxy.extraParams, params);
            },
            load: {
                fn: function( store ) {
                    var responseData = store.getProxy().getReader().jsonData;
                    var label = Ext.getCmp( "event_detail_total_info" );
                    if ( label ) {
                        label.setText( "共" + responseData.total + "条" );
                    }
                    Ext.getCmp('event_detail_tree_grid').getRootNode().set( "checked", false );
                }
            }
        }
    });

    var event_detail_tree_grid = Ext.getCmp('event_detail_tree_grid');
    if(!event_detail_tree_grid){
        event_detail_tree_grid = Ext.create('Ext.tree.Panel', {
            id: 'event_detail_tree_grid',
            closeAction: 'hide',
            width: document.body.clientWidth*0.8,
            // width: 800,
            height: 500,
            rootVisible: true,
            root: {
                text: '所有事件',
                id: '所有事件',
                name: '所有事件',
                leaf: false,
                expanded: true
            },
            store: event_detail_tree_store,
            stripeRows : true,
            columns: [{
                xtype: 'treecolumn',
                text: '名称',
                dataIndex: 'name',
                flex: 2,
                sortable: true
            }, {
                text: '启用',
                dataIndex: 'enabled',
                flex: 1,
                sortable: true,
                renderer: function( value ) {
                    if ( value == "启用" ) {
                        return '<font color="#41C85F">' + value + '</font>';
                    } else {
                        return '<font color="#EA1C0A">' + value + '</font>';
                    }
                }
            }, {
                text: '危险级别',
                dataIndex: 'dangerlevel',
                flex: 2,
                sortable: true
            }, {
                text: '响应方式',
                dataIndex: 'respond_type',
                flex: 2,
                sortable: true
            }, {
                text: '合并方式',
                dataIndex: 'merge_type',
                flex: 2,
                sortable: true
            }, {
                text: '排除方式',
                dataIndex: 'excepted_type',
                flex: 2,
                sortable: true
            }, {
                text: '活动/动作',
                dataIndex: 'id',
                flex: 2,
                align: 'center',
                iconCls: 'imagecursor',
                renderer: function( id ) {
                    var regx = /^\d+$/;
                    if ( !id.match( regx ) ) {
                        return "";
                    }

                    var disabled = false;
                    if ( edit_lib.type == "system" ) {
                        disabled = true;
                    }

                    var view_event_detail = {
                        enable: true,
                        id: "view_event_detail",
                        name: "view_event_detail",
                        button_icon: "view_details.png",
                        button_text: "查看详情",
                        value: id,
                        functions: {
                            onclick: "view_event_detail(this.value);"
                        }
                    };

                    var edit_button = {
                        enable: true,
                        id: "edit_event_item",
                        name: "edit_event_item",
                        button_icon: "edit.png",
                        button_text: "编辑",
                        value: id,
                        // disabled: disabled,
                        functions: {
                            onclick: "edit_event_item(this.value);"
                        }
                    };

                    var del_button = {
                        enable: true,
                        id: "delete_event_item",
                        name: "delete_event_item",
                        button_icon: "delete.png",
                        button_text: "删除",
                        value: id,
                        // disabled: disabled,
                        functions: {
                            onclick: "delete_event_item(this.value);"
                        }
                    };

                    var actions = [ view_event_detail, edit_button, del_button ];
                    if ( edit_lib.type == "system" ) {
                        edit_button.button_icon = "edit_disabled.png";
                        del_button.button_icon = "delete_disabled.png";
                    }
                    return PagingHolder.create_action_buttons( actions );
                }
            }],
            listeners: {
                checkchange:function( node, checked ){
                    node.eachChild( function ( child ) {
                        chd( child, checked );
                    });
                    //进行父级选中操作
                    parentnode( node ); 
                }
            }
        });
    }

    var event_detail_type_store = Ext.create('Ext.data.Store', {
        fields: ['abbr', 'name'],
        data : [
            {"abbr":"protcol", "name":"按协议分类"},
            {"abbr":"eventtype", "name":"按事件类型分类"},
            {"abbr":"dangerlevel", "name":"按事件级别分类"}
        ]
    });
    var event_detail_type_select = Ext.getCmp( 'event_detail_type_select' );
    if ( !event_detail_type_select ) {
        event_detail_type_select = Ext.create('Ext.form.ComboBox', {
            width: 200,
            id: 'event_detail_type_select',
            fieldLabel: '分组方式',
            labelAlign: "right",
            labelWidth: "70px",
            store: event_detail_type_store,
            queryMode: 'local',
            displayField: 'name',
            valueField: 'abbr',
            value: "protcol",
            selectOnFocus: true,
            style: {
                float: "right"
            },
            listeners: {
                change: {
                    fn: function( me, newValue, oldValue ) {
                        me.up('window').down('treepanel').getStore().load();
                    }
                }
            }
        });
    };
    var tool_button_style = {
            border: tool_button_border,
            marginLeft: "5px",
            marginRight: "5px"
        };
    var event_detail_tool_bar = Ext.getCmp( 'event_detail_tool_bar' );
    if ( !event_detail_tool_bar ) {
        event_detail_tool_bar = Ext.create('Ext.toolbar.Toolbar', {
            id: "event_detail_tool_bar",
            items: [{
                xtype: "button",
                id: "add_events_button",
                icon: "/images/add16x16.png",
                text: "新增事件",
                style: tool_button_style,
                handler: function( me ) {
                    if ( edit_lib.type == "system" ) {
                        message_manager.show_popup_error_mesg( "系统特征库可不编辑" );
                        return;
                    }
                    choose_events_when_editing_lib();
                }
            }, {
                xtype: "button",
                id: "apply_template_button",
                icon: "/images/applications-blue.png",
                text: "应用模板",
                style: tool_button_style,
                handler: function( me ) {
                    if ( edit_lib.type == "system" ) {
                        message_manager.show_popup_error_mesg( "系统特征库可不编辑" );
                        return;
                    }
                    var nodes = me.up('window').down('treepanel').getChecked();
                    var id_str = get_event_checked_ids( nodes );
                    if ( id_str != "" ) {
                        choose_policy_template();
                    } else {
                        edit_event_panel.show_error_mesg( "请选择特征事件" );
                    }
                }
            }, {
                xtype: "button",
                id: "enable_selected_button",
                icon: "/images/on.png",
                text: "启用选中",
                style: tool_button_style,
                handler: function( me ) {
                    if ( edit_lib.type == "system" ) {
                        message_manager.show_popup_error_mesg( "系统特征库可不编辑" );
                        return;
                    }
                    var nodes = me.up('window').down('treepanel').getChecked();
                    var id_str = get_event_checked_ids( nodes );
                    if ( id_str != "" ) {
                        enable_event_item( id_str );
                    } else {
                        edit_event_panel.show_error_mesg( "请选择特征事件" );
                    }
                }
            }, {
                xtype: "button",
                id: "disable_selected_button",
                icon: "/images/off.png",
                text: "禁用选中",
                style: tool_button_style,
                handler: function( me ) {
                    if ( edit_lib.type == "system" ) {
                        message_manager.show_popup_error_mesg( "系统特征库可不编辑" );
                        return;
                    }
                    var nodes = me.up('window').down('treepanel').getChecked();
                    var id_str = get_event_checked_ids( nodes );
                    if ( id_str != "" ) {
                        disable_event_item( id_str );
                    } else {
                        edit_event_panel.show_error_mesg( "请选择特征事件" );
                    }
                }
            }, {
                xtype: "button",
                id: "delete_selected_button",
                icon: "/images/delete.png",
                text: "删除选中",
                style: tool_button_style,
                handler: function( me ) {
                    if ( edit_lib.type == "system" ) {
                        message_manager.show_popup_error_mesg( "系统特征库可不编辑" );
                        return;
                    }
                    var nodes = me.up('window').down('treepanel').getChecked();
                    var id_str = get_event_checked_ids( nodes );
                    if ( id_str != "" ) {
                        delete_event_item( id_str );
                    } else {
                        edit_event_panel.show_error_mesg( "请选择特征事件" );
                    }
                }
            }, {
                xtype: event_detail_type_select
            }, {
                xtype: "textfield",
                id: "event_detail_search",
                name: "name",
                fieldLabel: '名称查询',
                fieldStyle: {
                    width: "150px"
                },
                labelAlign: "right",
                labelWidth: "70px",
                emptyText: "请输入名称关键字以查询...",
                width: 200,
                style: {
                    marginLeft: "5px"
                },
                allowBlank: true,
                enableKeyEvents: true,
                listeners: {
                    keyup: {
                        fn: function( me, event ) {
                            /*
                             * enter:13
                             */
                            // var event = event || window.event; //IE、FF下获取事件对象
                            var code = event.charCode || event.keyCode; //IE、FF下获取键盘码
                            if (code == 13){
                                ext_search(me);

                                // me.up("window").down("treepanel").getStore().load();
                            }
                        }
                    }
                }
            }, {
                xtype: "button",
                style: tool_button_style,
                icon: "/images/search16x16.png",
                text : "搜索",
                listeners: {
                    click: {
                        fn: function( button ) {
                            ext_search(button);

                            // var store = button.up("window").down("treepanel").getStore();
                            // store.load();
                        }
                    }
                }
            }, {
                xtype: "label",
                id: "event_detail_total_info",
                text: "共0条"
            }]
        });
    }

    var window_title = "编辑" + edit_lib.name + "特征库";
    if ( edit_lib.type == "system" ) {
        window_title = "查看" + edit_lib.name + "特征库详情";
    }
    
    var event_detail_window = Ext.getCmp('event_detail_window');
    if ( !event_detail_window ){
        event_detail_window = Ext.create('Ext.window.Window', {
            title: window_title,
            id: 'event_detail_window',
            closeAction: 'hide',
            modal: true,
            width: document.body.clientWidth*0.9,
            // width: 800,
            height: 500,
            layout: 'fit',
            data: '',
            items: [
                { 
                    xtype: event_detail_tree_grid
                }
            ],
            dockedItems: [{
                xtype: event_detail_tool_bar,
                dock: 'top'
            }],
            listeners: {
                hide: {
                    fn: function( me ) {
                        list_lib_panel.deselect_edit_item();
                        list_lib_panel.update_info();
                    }
                }
            },
            buttons:[
                {
                    text: '确定',
                    class: "imaged-button",
                    handler: function( me ){
                        list_lib_panel.deselect_edit_item();
                        list_lib_panel.update_info();
                        me.up('window').close();
                    }
                }
            ]
        })
    } else {
        event_detail_window.down( "textfield[id=event_detail_search]" ).setValue( "" );
        event_detail_window.down( "treepanel" ).getStore().load();
        event_detail_window.setTitle( window_title )
    }
    if ( edit_lib.type == "system" ) {
        event_detail_window.down( "button[id=add_events_button]" ).disable();
        event_detail_window.down( "button[id=apply_template_button]" ).disable();
        event_detail_window.down( "button[id=enable_selected_button]" ).disable();
        event_detail_window.down( "button[id=disable_selected_button]" ).disable();
        event_detail_window.down( "button[id=delete_selected_button]" ).disable();
    } else {
        event_detail_window.down( "button[id=add_events_button]" ).enable();
        event_detail_window.down( "button[id=apply_template_button]" ).enable();
        event_detail_window.down( "button[id=enable_selected_button]" ).enable();
        event_detail_window.down( "button[id=disable_selected_button]" ).enable();
        event_detail_window.down( "button[id=delete_selected_button]" ).enable();
    }
    event_detail_window.show();
    
}

function view_event_detail_info( data ) {
    var detail_panel = Ext.create('Ext.form.Panel',{
        bodyPadding: '5 15',
        layout: {
            type: 'table',
            columns: 1
        },
        defaultType: 'displayfield',
        items: [{
            fieldLabel: "事件名称",
            value: data.name
        }, {
            fieldLabel: "事件类型",
            value: data.type
        }, {
            fieldLabel: "事件描述",
            value: data.desc
        }, {
            fieldLabel: "事件类别",
            value: data.eventtype
        }, {
            fieldLabel: "协议类别",
            value: data.protcol
        }, {
            fieldLabel: "事件级别",
            value: data.dangerlevel
        }, {
            fieldLabel: "公开日期",
            value: data.undisclosed_date
        }, {
            fieldLabel: "发现日期",
            value: data.discovery_date
        }, {
            fieldLabel: "解决方法",
            value: data.solution
        }, {
            fieldLabel: "影响系统",
            value: data.effected_system
        }]
    });

    Ext.create('Ext.window.Window',{
        title: data.name+'的详情',
        width: 500,
        height: 400,
        modal: true,
        autoScroll: true,
        layout: 'anchor',
        closeAction: 'destroy',
        items:[{
            xtype: detail_panel
            
        }],
        buttons: [{
            text:"确定",
            padding: 5,
            handler: function(me){
                me.up('window').close();
            }
        }]
    }).show();
}

function get_event_checked_ids( nodes ) {
    var id_str = "";
    var id_array = new Array();

    var regx = /^\d+$/;
    for( var i = 0; i < nodes.length; i++ ){
        var item = nodes[i];
        var id = item.data.id;
        if ( id.match( regx ) ) {
            id_array.push( id );
        }
    }
    id_str = id_array.join( "&" );

    return id_str;
}

/* 再次选中之前已经选中的项目 */
function check_choosed_tree_item( root, ids ) {
    /* ids是&连接起来的id */
    var id_array = ids.split( "&" );

    var id_hash = new Object();
    for ( var i = 0; i < id_array.length; i++ ) {
        id_hash[id_array[i]] = id_array[i];
    }

    /* 遍历节点 */
    for ( i = 0; i < root.childNodes.length; i++ ) {
        var event_cls = root.childNodes[i];
        var checked_children = 0;
        for ( var j = 0; j < event_cls.childNodes.length; j++ ) {
            var event_node = event_cls.childNodes[j];
            if ( event_node.data.id in id_hash ) {
                // 此项被选中过
                event_node.set( "checked", true );
                checked_children++;
            } else {
                event_node.set( "checked", false );
            }
        }
        if ( checked_children == event_cls.childNodes.length ) {
            // 子节点全部被选中
            event_cls.set( "checked", true );
        } else {
            event_cls.set( "checked", false );
        }
    }

    return;
}

/* 遍历子结点 选中 与取消选中操作 */
function chd( node, check ) {
    node.set( 'checked', check );
    if( node.isNode ){
        node.eachChild( function (child) {
            chd( child, check );
        });
    }
}

/* 进行父级操作 */
function parentnode( node ) { 
    if ( node.parentNode != null ){
        if ( nodep( node.parentNode ) ) {
            node.parentNode.set( 'checked', true );
        } else {
            node.parentNode.set( 'checked', false );
        }       
        parentnode( node.parentNode );
    }
}

/* 向上遍历父结点 */
function nodep( node ) {
    var bnode = true;
    Ext.Array.each( node.childNodes,function(v) {
        if ( !v.data.checked ) {
            bnode = false;
            return;
        }
    });
    return bnode;
}

function delete_selected_items( element ) {
    var checked_items = list_lib_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_lib_panel.delete_item( ids );
}

function create_new_rule_lib( element ) {
    add_lib_panel.show();

}

function merge_rule_lib( element ) {
    var checked_items = list_lib_panel.get_checked_items();
    var checked_items_names = new Array();
    if ( checked_items.length == 0 ) {
        message_manager.show_error_mesg( "请选择要合并的特征库" );
    } else {
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_names.push( checked_items[i].name );
        }

        var names = checked_items_names.join( "\n" );

        $( "#choosed_rule_libs" ).val( names );

        merge_lib_panel.show();
        var height = $("#add_panel_id_for_rule_libraries_merge").height() + 16;
        document.getElementById("TransparentBorder_rule_libraries_merge").style.height = height + 'px';

    }
}

function add_choosed_rule_libs() {
    var checked_items = list_lib_panel.get_checked_items();
    var checked_items_names = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_names.push( checked_items[i].name );
    }

    var names = checked_items_names.join( "\n" );

    $( "#choosed_rule_libs" ).val( names );
}

function import_rule_lib( element ) {
    import_lib_panel.show();
    var height = $("#add_panel_id_for_rule_libraries_import").height() + 16;
    document.getElementById("TransparentBorder_rule_libraries_import").style.height = height + 'px';

}

function copy_rule_lib( element ) {
    var lib_config = list_lib_panel.get_item( element.value );
    $( "#to_copy_lib" ).val( element.value );
    $( "#breed_lib_note" ).val( "【" + lib_config.name + "】的衍生特征库" );
    copy_lib_panel.show();
}

function view_rule_lib( element ) {
    var lib = list_lib_panel.get_item( element.value );
    view_lib_flag++;
    show_envents_grid_tree( lib );
}

function edit_rule_lib( element ) {
    view_lib_flag = 0;
    list_lib_panel.edit_item( element.value );
    $('#tool-1021').hide();
}

function del_rule_lib( element ) {
    list_lib_panel.delete_item( element.value );
}

function view_event_detail( id ) {
    var sending_data = {
        ACTION: "load_event_detail_data",
        id: id
    }

    function ondatareceived( data ) {
        view_event_detail_info( data );
    }

    edit_event_panel.request_for_json( sending_data, ondatareceived );
}

function edit_event_item( id ) {
    if ( edit_lib.type == "system" ) {
        return; //不可编辑
    }

    var sending_data = {
        ACTION: "load_event_config",
        lib_name: edit_lib.name,
        id: id
    }

    function ondatareceived( data ) {
        edit_event_panel.edit_data( data.data );
        edit_event_panel.show();
        $("#TransparentBorder_rule_lib_edit_event").css("z-index",20000);
        $("#popup-mesg-border-box-cover-rule_lib_edit_event").css("z-index",19999);
    }

    edit_event_panel.request_for_json( sending_data, ondatareceived );
}

function add_events_to_lib( id ) {
    var sending_data = {
        ACTION: "add_events_to_lib",
        lib_name: edit_lib.name,
        id: id
    }

    function ondatareceived( data ) {
        if ( edit_event_panel.is_operation_succeed( data ) ) {
            edit_event_panel.show_note_mesg( data.mesg );
            // Ext.getCmp( "event_detail_tree_grid" ).getStore().load();
            // if ( edit_event_panel.is_need_reload(data) ) {
            //     edit_event_panel.show_apply_mesg();
            //}
        } else {
            edit_event_panel.show_error_mesg( data.mesg );
        }
    }

    edit_event_panel.request_for_json( sending_data, ondatareceived );
}

function apply_template_to_event_item( element ) {
    template_list_panel.hide();
    var id = get_event_checked_ids( Ext.getCmp("event_detail_tree_grid").getChecked() );
    var checked_template = template_list_panel.get_checked_items();
    var template_id = checked_template[0].id;
    operate_event_item( id, "apply_template_to_event_item", "应用模板", true, { template_id: template_id} );


}

function cancel_choose_policy_template( element ) {
    template_list_panel.hide();
    template_list_panel.set_check( choosed_template_id, false );
    template_list_panel.update_info();
    choosed_template_id = "";
}

function choose_policy_template() {
    if ( choosed_template_id != "" ) {
        template_list_panel.set_check( choosed_template_id, true );
    }

    template_list_panel.update_info();
    template_list_panel.show();
    $("#TransparentBorder_template_list_panel").css("z-index",20000);
    $("#popup-mesg-border-box-cover-template_list_panel").css("z-index",19999);
}

function enable_event_item( id ) {
    operate_event_item( id, "enable_event_item", "启用选中", false );
}

function disable_event_item( id ) {
    operate_event_item( id, "disable_event_item", "禁用选中", true );
}

function delete_event_item( id ) {
    if ( edit_lib.type == "system" ) {
        return; //不可删除
    }

    operate_event_item( id, "delete_event_item", "删除", true );
}

function operate_event_item( id, operation, operation_tip, inquiry, extend_par ) {
    var sending_data = {
        ACTION: operation,
        lib_name: edit_lib.name,
        lib_id: edit_lib.id,
        id: id
    }

    if ( extend_par !== undefined ) {
        for ( var key in extend_par ) {
            sending_data[key] = extend_par[key];
        }
    }

    function ondatareceived( data ) {
        if ( edit_event_panel.is_operation_succeed( data ) ) {
            edit_event_panel.show_note_mesg( data.mesg );
            Ext.getCmp( "event_detail_tree_grid" ).getStore().load();
            if ( edit_event_panel.is_need_reload(data) ) {
                edit_event_panel.show_apply_mesg();
            }
        } else {
            edit_event_panel.show_error_mesg( data.mesg );
        }
    }

    if( inquiry !== undefined && inquiry ) {
        if( confirm("确认" + operation_tip + "?") ) {
            edit_event_panel.request_for_json( sending_data, ondatareceived );
        }
    } else {
        edit_event_panel.request_for_json( sending_data, ondatareceived );
    }
}

function choose_merge_type( element ) {
    if( element.value == "none" ) {
        $( "#merge_interval" ).attr( "disabled", true );
        $( "#max_merge_count" ).attr( "disabled", true );
        $( "#merge_config_item" ).hide();
    } else {
        $( "#merge_interval" ).attr( "disabled", false );
        $( "#max_merge_count" ).attr( "disabled", false );
        $( "#merge_config_item" ).show();
    }
}

function choose_exception_type( element ) {
    if ( element.value == "by_dst" || element.value == "by_src" ) {
        $( "#exception_ips" ).attr( "disabled", false );
        $( "#exception_ips_item" ).show();
    } else {
        $( "#exception_ips" ).attr( "disabled", true );
        $( "#exception_ips_item" ).hide();
    }
}

function load_init_data() {
    var sending_data = {
        ACTION: "load_init_data"
    }

    function ondatareceived( data ) {
        init_respond_type( data.respond_type );
        edit_event_panel.render();
        edit_event_panel.hide();
    }

    edit_event_panel.request_for_json( sending_data, ondatareceived );
}

function init_respond_type( respond_type ) {
    var respond_type_checkboxs = new Array();

    for ( var i = 0; i < respond_type.length; i++ ) {
        var item = respond_type[i];
        var checkbox = {
            enable: true,
            type: "checkbox",
            id: item.value,
            name: "respond_type",
            class: "respond_type_item",
            value: item.value,
            label: item.label,
            // split: "&",
            // check: {
            //     type:"checkbox",
            //     required: 1,
            //     ass_check:function( check ){
            //         // var value = $( ".respond_type_item:checked" ).length;
            //         // if ( value == 0 ) {
            //         //     return "必须选择一种响应方式";
            //         // }
            //     }
            // }
        };

        respond_type_checkboxs.push( checkbox );
    }

    edit_event_config.items_list[3].sub_items[0].sub_items = respond_type_checkboxs;
}
var last_search_time =0;
function ext_search(me){
    $('#button-1012-btnInnerEl').attr('disabled', 'disabled');
        var timestamp=new Date().getTime();
        console.log(timestamp-last_search_time);
        if (last_search_time!= 0) {
            if (timestamp-last_search_time>1000) {
                me.up("window").down("treepanel").getStore().load();
                last_search_time= timestamp;
            }
            
        }else{
            me.up("window").down("treepanel").getStore().load();
            
            last_search_time= timestamp;
        }
    setTimeout(function(){
        
        $('#button-1012-btnInnerEl').removeAttr('disabled');
    },1000)
};
