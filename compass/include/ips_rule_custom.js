/*
 * 描述: 特征事件自定义
 *
 * 作者: WangLin，245105947@qq.com
 * 历史：
 *       2012.10.15 WangLin创建
 */

$( document ).ready(function() {
    load_init_data();
    /* 渲染面板 */
    message_manager.render();
    rule_import_panel.render();
    rule_list_panel.render();
    lib_list_panel.render();

    rule_import_panel.hide();
    lib_list_panel.hide();
    /* 设置面板关联 */
    rule_add_panel.set_ass_list_panel( rule_list_panel );
    rule_list_panel.set_ass_add_panel( rule_add_panel );
    rule_add_panel.set_ass_message_manager( message_manager );
    rule_import_panel.set_ass_message_manager( message_manager );
    rule_list_panel.set_ass_message_manager( message_manager );
    lib_list_panel.set_ass_message_manager( message_manager );
    /* 加载数据 */
    check_running();
    rule_list_panel.update_info( true );
    lib_list_panel.update_info( true );
    // $( "#exception_ips_item" ).hide();


});

/*
 * 定义全局变量
 */
var ass_url = "/cgi-bin/ips_rule_custom.cgi";

var global_config = new Object();

var message_box_config = {
    url: ass_url,
    check_in_id: "rule_custom_mesg_box"
}

var rule_add_config = {
    url: ass_url,
    check_in_id: "rule_custom_add",
    panel_name: "rule_custom_add",
    rule_title: "特征事件",
    is_panel_closable: true,
    is_panel_stretchable: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj, data_item ) {
            // data_item.exception_ips = data_item.exception_ips.replace( /&/g, "\n" );
            // data_item.protocol_port = data_item.protocol_port.replace( /&/g, "\n" );
        },
        after_load_data: function ( add_obj, data_item ) {
            choose_protocol( document.getElementById("protocol"), data_item.protocol_port );
            choose_exception_type( document.getElementById("exception_type") );
            choose_merge_type( $( ".merge_type_item:checked" )[0] );
        },
        before_cancel_edit: function( add_obj ) {

        },
        after_cancel_edit: function( add_obj ) {
            choose_protocol( document.getElementById("protocol") );
            choose_exception_type( document.getElementById("exception_type") );
            choose_merge_type( $( ".merge_type_item:checked" )[0] );
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
            var event_content = $( "#event_content" ).val();
            if (/[\u4e00-\u9fa5]/g.test(event_content)) {
                message_manager.show_popup_error_mesg( "特征定义中语法错误" );
                return false
            }
        },
        after_save_data: function ( add_obj, received_data ) {
            if ( add_obj.is_operation_succeed( received_data ) ) {
                lib_list_panel.update_info();
            }
        }
    },
    items_list: [{
        title: "名称",
        sub_items: [ {
            enable: true,
            type: "text",
            id: "rule_name",
            name: "rule_name",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check: 'name|',
                ass_check: function( check ) {

                }
            }
        },{
            enable: true,
            type: "text",
            name: "sid",
            item_style: "display: none;"
        }]
    }, {
        title: "说明",
        sub_items: [{
            enable: true,
            type: "textarea",
            tip: "(0~128个字符)",
            id: "rule_note",
            name: "rule_note",
            value: "",
            check: {
                type: "textarea",
                required: 0,
                check: 'note|',
                ass_check: function( check ) {
                    var msg = ''
                    var value = $("#rule_note").val();
                    if( value.length > 128 ) {
                        return msg="请输入0~128个字符";
                    }
                }
            }
        }]
    }, {
        title: "协议类别",
        sub_items: [{
            enable: true,
            type: "items_group",
            item_style: "width: 40%;", 
            sub_items: [{
                enable: true,
                label: "选择协议：",
                label_style: "display: block;",
                type: "select",
                id: "protocol",
                name: "protocol",
                multiple: false,
                item_id: "protocol_item",
                functions: {
                    onkeyup: "choose_protocol(this);",
                    onchange: "choose_protocol(this);"
                },
                options: [
                ],
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
            label: "端口/范围：",
            label_style: "display: block;",
            id: "protocol_port",
            name: "protocol_port",
            tip: "(每行一个)",
            item_id: "protocol_port_item",
            item_style: "width: 50%;", 
            check: {
                type: "textarea",
                required: 0,
                check: 'port|port_range',
                ass_check: function( check ) {

                }
            }
        }]
    }, {
        title: "源/目的IP反向",
        sub_items: [{
            enable: true,
            type: "select",
            id: "s_d_ip_reverse",
            name: "s_d_ip_reverse",
            options: [
                {
                    value: "no",
                    text: "否"
                }, {
                    value: "yes",
                    text: "是"
                }, {
                    value: "twoway",
                    text: "双向"
                }
            ],
            check: {
                type: "select-one",
                required: 1,
                ass_check: function( check ){
                    
                }
            }
        }]
    }, {
        title: "事件类别",
        sub_items: [{
            enable: true,
            type: "select",
            id: "event_class",
            name: "event_class",
            options: [
            ],
            check: {
                type: "select-one",
                required: 1,
                ass_check: function( check ){
                    
                }
            }
        }]
    }, {
        title: "事件级别",
        sub_items: [{
            enable: true,
            type: "select",
            id: "event_level",
            name: "event_level",
            options: [
            ],
            check: {
                type:"select-one",
                required:'1',
                ass_check:function( check ){
                    
                }
            }
        }]
    }, {
        title: "特征定义",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "event_content",
            name: "event_content"
        }, {
            enable: true,
            type: "button",
            id: "check_event_content",
            name: "check_event_content",
            value: "语法检测",
            functions: {
                onclick: "check_event_content_function();"
            }
        }]
    }, {
        title: "所属特征库",
        sub_items: [{
            enable: true,
            type: "text",
            id: "rule_lib",
            name: "rule_lib",
            readonly: true,
            functions: {
                onclick: "choose_rule_lib(this);"
            }
        }]
    }, {
        title: "响应方式*",
        sub_items: [{
            enable: true,
            type: "items_group",
            sub_items: [
            ]
        }]
    }, {
        title: "合并方式*",
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
            item_style: "width: 100%;display:none;",
            sub_items: [{
                enable: true,
                type: "text",
                label: "合并周期:",
                id: "merge_interval",
                name: "merge_interval",
                tip: "(单位：秒，范围：1~120)",
                disabled: true,
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
        title: "排除IP*",
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
                options: [
                    {
                        value: "none",
                        text: "不排除"
                    }, {
                        value: "by_src",
                        text: "按源IP排除",
                        selected: true
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
};

var import_panel_config = {
    url: ass_url,
    check_in_id: "rule_custom_import",
    panel_name: "rule_custom_import",
    rule_title_adding_prefix: "导入",
    rule_title: "自定义特征事件",
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
        title: "特征事件文件",
        sub_items: [
            {
                enable: true,
                type: "file",
                name: "rules_file",
                style:"height:24px",
                check: {
                    type: "file",
                    required: 1
                }
            }
        ]
    }]
};

var rule_list_render = {
    rule_note: {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = default_rendered_text;

            if ( default_rendered_text.split( "" ).length > 40 ) {
                rendered_text = '<span class="short-mesg" title="' + default_rendered_text + '">' + 
                                default_rendered_text.substring( 0, 40 ) + '...</span>';
            }

            return rendered_text;
        }
    },
    action: {
        render: function( default_rendered_text, data_item ) {
            var edit_button = {
                enable: true,
                id: "edit_rule",
                name: "edit_rule",
                button_icon: "edit.png",
                button_text: "编辑",
                value: data_item.id,
                functions: {
                    onclick: "edit_rule(this);"
                },
                class:"action-image"
            }
            var del_button = {
                enable: true,
                id: "del_rule",
                name: "del_rule",
                button_icon: "delete.png",
                button_text: "删除",
                value: data_item.id,
                functions: {
                    onclick: "del_rule(this);"
                },
                class:"action-image"
            }
            var actions = [ edit_button, del_button ];
            return PagingHolder.create_action_buttons( actions );
        }
    }
};

var rule_list_config = {
    url: ass_url,
    check_in_id: "rule_custom_list",
    panel_name: "rule_custom_list",
    render: rule_list_render,
    page_size:20,
    default_search_config: {                            /* ===可选===，只有当is_default_search为true时才生效 */
        input_tip: "输入名称、说明关键字以查询..."     /* ===可选===，控制搜索输入框内的提示，默认是“输入关键字以查询...” */
    },
    panel_header: [{
        enable: true,
        td_class:"align-center",
        type: "checkbox",
        name: "checkbox",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "名称",
        name: "rule_name",
        width: "20%"
    }, {
        enable: true,
        type: "text",
        title: "说明",
        name: "rule_note",
        width: "45%"
    }, {
        enable: true,
        type: "text",
        title: "所属策略集",
        name: "rule_lib",
        width: "20%"
    }, {
        enable: true,
        type: "action",
        name: "action",
        width: "10%",
        td_class:"align-center"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        button_icon: "add16x16.png",
        button_text: "新建特征事件",
        functions: {
            onclick: "add_rule(this);"
        }
    },
    {
        enable: true,
        type: "image_button",
        button_icon: "upload.png",
        button_text: "导入特征事件",
        functions: {
            onclick: "import_rules(this);"
        }
    },
    {
        enable: true,
        type: "link_button",
        id: "export_selected_rules",
        href: ass_url + "?ACTION=export_selected",
        button_icon: "download.png",
        button_text: "导出选中事件",
        functions: {
            onmouseover: "append_selected_items_to_link(this);"
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

var lib_list_config = {
    url: ass_url,
    check_in_id: "rule_lib_list",
    panel_name: "rule_lib_list",
    panel_title: "选择特征库",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 20,
        modal_box_position: "fixed"
    },
    panel_header: [{
        enable: true,
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "名称",
        name: "name",
        width: "30%"
    }, {
        enable: true,
        type: "text",
        title: "说明",
        name: "note",
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
                onclick: "choosed_rule_lib( this );"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "cancel_choose_rule_lib( this );"
            }
        }]
    }
};

var rule_add_panel = new RuleAddPanel( rule_add_config );
var rule_import_panel = new RuleAddPanel( import_panel_config );
var rule_list_panel = new PagingHolder( rule_list_config );
var lib_list_panel = new PagingHolder( lib_list_config );
var message_manager = new MessageManager( message_box_config );


/* 定义全局函数 */
function delete_selected_items( element ) {
    var checked_items = rule_list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    rule_list_panel.delete_item( ids );
}

function add_rule( element ) {
    rule_add_panel.show();
}

function edit_rule( element ) {
    rule_list_panel.edit_item( element.value );
}

function del_rule( element ) {
    var item_id = element.value;
    var data_item = rule_list_panel.get_item( item_id );
    var del_tip = "该特征事件属于多个特征库，若删除该特征事件，则也将从相应特征库中移除该特征事件，是否确定删除?";
    if ( data_item.rule_lib == "" ) {
        del_tip = "确认删除该特征事件?";
    }
    rule_list_panel.operate_item( item_id, "delete_data", del_tip, true );
}

function import_rules( element ) {
    rule_import_panel.show();
}

function append_selected_items_to_link() {
    var checked_items = rule_list_panel.get_checked_items();
    var checked_ids = new Array();
    var items_length = checked_items.length;
    var sending_data = "";
    for (var i = 0; i < items_length; i++) {
        var item = checked_items[i];
        checked_ids.push( item.id );
    }
    sending_data += "&id=" + checked_ids.join( "|" );
    var href = document.getElementById( 'export_selected_rules' ).href.split("?")[0];
    href += "?ACTION=export_selected";
    href += sending_data;
    $( "#export_selected_rules" ).attr( "href", href );
    return true;
}

function choose_protocol( element, ports ) {
    var protocol_info = global_config.loaded_data.protocol_info;
    var default_ports = "";
    var is_port_editable = "off";
    for ( var i = 0; i < protocol_info.length; i++ ) {
        var item = protocol_info[i];
        if( item.value == element.value ) {
            default_ports = item.default_ports;
            is_port_editable = item.is_port_editable;
            break;
        }
    }
    if ( default_ports != undefined && default_ports != null && default_ports != "" ) {
        $( "#protocol_port" ).val( default_ports );
    } else {
        if ( ports !== undefined ) {
            $( "#protocol_port" ).val( ports );
        } else {
            $( "#protocol_port" ).val( "" );
        }
    }
    if ( is_port_editable == "on" ) {
        // document.getElementById( "protocol_port" ).disabled = false;
        $( "#protocol_port_item" ).show();
    } else {
        // document.getElementById( "protocol_port" ).disabled = true;
        $( "#protocol_port_item" ).hide();
    }
}

function check_event_content_function() {
    var event_content = $( "#event_content" ).val();
    if (/[\u4e00-\u9fa5]/g.test(event_content)) {
        message_manager.show_popup_error_mesg( "语法错误" );
    }else{
        message_manager.show_popup_note_mesg( "语法正确" );
    }
    // var sending_data = {
    //     ACTION: "check_event_content",
    //     event_content: event_content
    // }

    // function ondatareceived( data ) {
    //     if ( data.mesg == "yes" ) {
    //         message_manager.show_popup_note_mesg( "语法正确" );
    //     } else {
    //         message_manager.show_popup_error_mesg( "语法错误" );
    //     }
    // }

    // rule_add_panel.request_for_json( sending_data, ondatareceived );
}

function choose_rule_lib( element ) {
    var choosed_lib = $( "#rule_lib" ).val();

    if ( choosed_lib != "" ) {
        var names = choosed_lib.split( "&" );
        for ( var i = 0; i < names.length; i++ ) {
            lib_list_panel.set_check( names[i], true );
        }
    }

    lib_list_panel.update_info();
    lib_list_panel.show();
}

function choosed_rule_lib( element ) {
    var checked_items = lib_list_panel.get_checked_items();
    var checked_items_name = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_name.push( checked_items[i].name );
    }

    var names = checked_items_name.join( "&" );

    $( "#rule_lib" ).val( names );
    lib_list_panel.hide();
    lib_list_panel.uncheck_current_page();
}

function cancel_choose_rule_lib( element ) {
    lib_list_panel.hide();
    lib_list_panel.uncheck_current_page();
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
        global_config.loaded_data = data;
        init_options( data );
        rule_add_panel.render();
        rule_add_panel.hide();
    }

    rule_add_panel.request_for_json( sending_data, ondatareceived );
}

function init_options( data ) {
    init_protocol_options( data.protocol_info );
    init_event_class_options( data.event_class );
    init_event_level_options( data.event_level );
    init_respond_type( data.respond_type );
}

function init_protocol_options( protocol_info ) {
    var options = new Array();

    for ( var i = 0; i < protocol_info.length; i++ ) {
        var item = protocol_info[i];
        var new_option_item = { value: item.value, text: item.name };
        if ( item.value == "tcp" ) {
            new_option_item.selected = true;
        }
        options.push( new_option_item );
    }

    rule_add_config.items_list[2].sub_items[0].sub_items[0].options = options;
}

function init_event_class_options( event_class ) {
    var options = new Array();

    for ( var i = 0; i < event_class.length; i++ ) {
        var item = event_class[i];
        var new_option_item = { value: item.en_short, text: item.cn_name };
        options.push( new_option_item );
    }

    rule_add_config.items_list[4].sub_items[0].options = options;
}

function init_event_level_options( event_level ) {
    var options = new Array();

    for ( var i = 0; i < event_level.length; i++ ) {
        var item = event_level[i];
        var new_option_item = { value: item.value, text: item.text };
        options.push( new_option_item );
    }

    rule_add_config.items_list[5].sub_items[0].options = options;
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
            label: item.label
        };

        respond_type_checkboxs.push( checkbox );
    }

    rule_add_config.items_list[8].sub_items[0].sub_items = respond_type_checkboxs;
}