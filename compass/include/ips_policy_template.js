/*
 * 描述: 入侵防御策略模板页面
 *
 * 作者: WangLin，245105947@qq.com
 * 历史：
 *       2012.11.21 WangLin创建
 */

$( document ).ready(function() {
    load_init_data();
    /* 渲染面板 */
    message_manager.render();
    list_template_panel.render();

    /* 设置面板关联 */
    template_add_panel.set_ass_list_panel( list_template_panel );
    list_template_panel.set_ass_add_panel( template_add_panel );

    template_add_panel.set_ass_message_manager( message_manager );
    list_template_panel.set_ass_message_manager( message_manager );

    list_template_panel.update_info( true );

});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/ips_policy_template.cgi";

var message_box_config = {
    url: ass_url,
    check_in_id: "template_mesg_box",
    panel_name: "template_mesg_box"
}

var template_add_config = {
    url: ass_url,
    check_in_id: "template_add_panel",
    panel_name: "template_add_panel",
    rule_title: "策略模板",
    is_panel_closable: true,
    is_panel_stretchable: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        after_load_data: function ( add_obj, data_item ) {
            choose_exception_type( document.getElementById("exception_type") );
            // choose_merge_type( $( ".merge_type_item:checked" )[0] );  不需要调用
            toggle_respond_type_line( document.getElementById("apply_scope_of_respond") );
            toggle_merge_type_line( document.getElementById("apply_scope_of_merge") );
            toggle_exception_type_line( document.getElementById("apply_scope_of_exception") );
        },
        after_cancel_edit: function( add_obj ) {
            choose_exception_type( document.getElementById("exception_type") );
            choose_merge_type( $( ".merge_type_item:checked" )[0] );
            toggle_respond_type_line( document.getElementById("apply_scope_of_respond") );
            toggle_merge_type_line( document.getElementById("apply_scope_of_merge") );
            toggle_exception_type_line( document.getElementById("apply_scope_of_exception") );
        },
        before_save_data: function( add_obj, sending_data ) {
            var apply_scope_item_len = $( ".apply_scope_item:checked" ).length;
            if ( apply_scope_item_len == 0 ) {
                template_add_panel.show_error_mesg( "至少选择一个应用类别" );
                return false;
            }

            var apply_scope_of_respond = $( "#apply_scope_of_respond" ).attr( "checked" );
            if ( apply_scope_of_respond ) {
                var respond_type_item = $( ".respond_type_item:checked" );
                var respond_type_item_notid = $( ".respond_type_item:checked" ).not('input[id="log"]');
                if ( respond_type_item.length === 0 ) {
                    template_add_panel.show_error_mesg( "至少选择一种响应方式" );
                    return false;
                }else if(respond_type_item_notid.length>1){
                    template_add_panel.show_error_mesg( "响应方式中允许、丢弃、RST阻断最多只能选择一个" );
                    return false;
                }
            }
        }
    },
    items_list: [{
        title: "名称 *",
        sub_items: [{
            enable: true,
            type: "text",
            id: "template_name",
            name: "template_name",
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
        }]
    }, {
        title: "说明",
        sub_items: [{
            enable: true,
            type: "textarea",
            tip: "(0~128个字符)",
            id: "template_note",
            name: "template_note",
            value: "",
            functions: {
            },
            check: {
                type: "textarea",
                required: 0,
                check: 'note|',
                ass_check: function(check) {
                    var value = $("#template_note").val();
                    var length = value.length;
                    if( length > 128 ) {
                        return "请输入0~128个字符";
                    }
                }
            }
        }]
    }, {
        title: "应用范围 *",
        sub_items: [{
            enable: true,
            type: "items_group",
            sub_items: [{
                enable: true,
                type: "checkbox",
                id: "apply_scope_of_respond",
                name: "apply_scope",
                class: "apply_scope_item",
                label: "设置响应方式",
                value: "RESPOND",
                checked: true,
                functions: {
                    onclick: "toggle_respond_type_line(this);"
                }
            }, {
                enable: true,
                type: "checkbox",
                id: "apply_scope_of_merge",
                name: "apply_scope",
                class: "apply_scope_item",
                label: "设置合并方式",
                value: "MERGE",
                checked: true,
                functions: {
                    onclick: "toggle_merge_type_line(this);"
                }
            }, {
                enable: true,
                type: "checkbox",
                id: "apply_scope_of_exception",
                name: "apply_scope",
                class: "apply_scope_item",
                label: "设置排除IP",
                value: "EXCLUDE",
                checked: true,
                functions: {
                    onclick: "toggle_exception_type_line(this);"
                }
            }]
        }]
    }, {
        title: "响应方式*",
        id: "respond_type_line", //整行的id
        sub_items: [{
            enable: true,
            type: "items_group",
            sub_items: [
            ]
        }]
    }, {
        title: "合并方式",
        id: "merge_type_line", //整行的id
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
                class: "merge_type_item merge_type_config_item",
                value: "none",
                label: "不合并",
                checked: true,
                functions: {
                    onclick: "choose_merge_type(this);"
                }
            }, {
                enable: true,
                type: "radio",
                id: "merge_type_s_ip",
                name: "merge_type",
                class: "merge_type_item merge_type_config_item",
                value: "mergeby_src",
                label: "按<源IP>合并",
                functions: {
                    onclick: "choose_merge_type(this);"
                },
                check: {
                    type: "radio",
                    required: 1
                }
            }, {
                enable: true,
                type: "radio",
                id: "merge_type_d_ip",
                name: "merge_type",
                class: "merge_type_item merge_type_config_item",
                value: "mergeby_dst",
                label: "按<目标IP>合并",
                functions: {
                    onclick: "choose_merge_type(this);"
                },
                check: {
                    type: "radio",
                    required: 1
                }
            }, {
                enable: true,
                type: "radio",
                id: "merge_type_both",
                name: "merge_type",
                class: "merge_type_item merge_type_config_item",
                value: "mergeby_ip",
                label: "按<源IP + 目标IP>合并",
                functions: {
                    onclick: "choose_merge_type(this);"
                },
                check: {
                    type: "radio",
                    required: 1
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
                class: "merge_type_config_item",
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
                class: "merge_type_config_item",
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
        id: "exception_type_line", //整行的id
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
                class: "exception_type_item",
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
            class: "exception_type_item",
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

var list_template_config = {
    url: ass_url,
    check_in_id: "list_template_panel",
    panel_name: "list_template_panel",
    page_size:20,
    default_search_config: {                            /* ===可选===，只有当is_default_search为true时才生效 */
        input_tip: "输入名称、说明关键字以查询..."      /* ===可选===，控制搜索输入框内的提示，默认是“输入关键字以查询...” */
    },
    event_handler: {
        before_load_data: function( list_obj ) {
        },
        after_load_data: function ( list_obj, response ) {
        }
    },
    render: {
        template_note: {
            render: function( default_text, data_item ) {
                var rendered_text = default_text;
                if ( default_text.split( "" ).length > 60 ) {
                    rendered_text = '<span class="short-mesg" title="' + default_text + '">' + 
                                    default_text.substring( 0, 60 ) + '...</span>';
                }
                return rendered_text;
            }
        }
    },
    panel_header: [{
        enable: true,
        type: "checkbox",
        name: "checkbox",
        "td_class":"align-center",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "模板名称",
        name: "template_name",
        width: "20%"
    }, {
        enable: true,
        type: "text",
        title: "模板说明",
        name: "template_note",
        width: "50%"
    }, {
        enable: true,
        type: "text",
        title: "最后修改时间",
        name: "modified_time",
        "td_class":"align-center",
        width: "15%"
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
        button_text: "新建模板",
        functions: {
            onclick: "add_policy_template(this);"
        }
    },{
        enable: true,
        type: "image_button",
        button_icon: "delete.png",
        button_text: "删除选中",
        functions: {
            onclick: "delete_selected_items(this);"
        }
    }]
};

var template_add_panel = new RuleAddPanel( template_add_config );
var list_template_panel = new PagingHolder( list_template_config );
var message_manager = new MessageManager( message_box_config );

function delete_selected_items( element ) {
    var checked_items = list_template_panel.get_checked_items();

    if ( checked_items.length == 0 ) {
        list_template_panel.show_error_mesg( "请选择要删除的规则" );
        return;
    }
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_template_panel.delete_item( ids );
}

function add_policy_template( element ) {
    template_add_panel.show();
}


function load_init_data( sending_data, ondatareceived ) {
    var sending_data = {
        ACTION: "load_init_data"
    }

    function ondatareceived( data ) {
        init_respond_type( data.respond_type );
        template_add_panel.render();
        template_add_panel.hide();
    }

    $.ajax({
        type: 'POST',
        url: "/cgi-bin/ips_rule_lib.cgi",
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            alert( "加载初始化数据出错" );
        },
        success: ondatareceived
    });
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

    template_add_config.items_list[3].sub_items[0].sub_items = respond_type_checkboxs;
}

function toggle_respond_type_line( element ) {
    toggle_line( "#respond_type_line", ".respond_type_item", element.checked );
}

function toggle_merge_type_line( element ) {
    toggle_line( "#merge_type_line", ".merge_type_config_item", element.checked );
}

function toggle_exception_type_line( element ) {
    toggle_line( "#exception_type_line", ".exception_type_item", element.checked );
}

function toggle_line( id, items, show ) {
    if ( show ) {
        $( id ).show();
        $( items ).attr( "disabled", false );
    } else {
        $( id ).hide();
        $( items ).attr( "disabled", true );
    }
    var height = $("#modal_border_box_template_add_panel").height();
    $("#TransparentBorder_template_add_panel").css('height',height);
}

function choose_merge_type( element ) {
	// console.log(element);
    if( element.value == "none" ) {
        $( "#merge_interval" ).attr( "disabled", true );
        $( "#max_merge_count" ).attr( "disabled", true );
        $( "#merge_config_item" ).hide();
    } else {
        $( "#merge_interval" ).attr( "disabled", false );
        $( "#max_merge_count" ).attr( "disabled", false );
        $( "#merge_config_item" ).show();
    }
    var height = $("#modal_border_box_template_add_panel").height();
    $("#TransparentBorder_template_add_panel").css('height',height);
}

function choose_exception_type( element ) {
    if ( element.value == "by_dst" || element.value == "by_src" ) {
        $( "#exception_ips" ).attr( "disabled", false );
        $( "#exception_ips_item" ).show();
    } else {
        $( "#exception_ips" ).attr( "disabled", true );
        $( "#exception_ips_item" ).hide();
    }
    var height = $("#modal_border_box_template_add_panel").height();
    $("#TransparentBorder_template_add_panel").css('height',height);
}