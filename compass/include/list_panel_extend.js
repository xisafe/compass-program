/*
 * 描述: 可翻页的列表面板使用示例
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2014.08.01 WangLin创建
 */

/*
 * 注释<1>：此文档的“配置对象”指new PagingHolder时传入的对象
 */

$(document).ready(function(){
    paging_holder.render();
    paging_holder.update_info( true );
});

var list_panel_render = {
    'checkbox': {
        listeners: {    /* ===可选===，向checkbox增加类似click的外接监听 */
            click: function( element, data_item, list_obj ) {
                if ( element.checked ) {
                    alert( data_item.id + "chcked!" );
                } else {
                    alert( data_item.id + "unchcked!" );
                }
            }
        }
    },
    'radio': {      /* ===可选===，向radio增加类似click的外接监听 */
        listeners: {
            click: function( element, data_item, event, list_obj ) {
                if ( element.checked ) {
                    alert( data_item.id + "chcked!" );
                } else {
                    alert( data_item.id + "unchcked!" );
                }
            }
        }
    },
    'classification': {
        render: function( default_rendered_text, data_item ) {
            return '<span class="note">' + default_rendered_text + "--" + data_item.id + '</span>';
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
            return default_rendered_text;
            var action_buttons = [{
                enable: true,
                id: "delete_all_logs",
                name: "delete_all_logs",
                cls: "",
                button_icon: "search16x16.png",
                button_text: "查看详情",
                value: data_item.id,
                functions: {
                    onclick: "alert(this.value);"
                }
            }];

            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/list_panel.cgi", /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_main_body",  /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 15,                  /* ===可选===，控制数据项默认加载多少条，默认是15，此处可以在加载数据过程中更改，
                                                   更改方法是从服务器加载数据到浏览器时，传一个page_size字段到浏览器 */
    panel_title: "列表面板",        /* ===可选===，面板的标题 */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_modal: false,                /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次时创建，并且在is_modal为true时才生效 */
        modal_box_size: "l",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
        modal_box_position: "fixed" /* ===可选===，position属性值，目前未使用，未调试成功，建议不使用此字段 */
    },
    is_default_search: true,        /* ===可选===，默认是true，控制搜索框是否展示，
                                                    注意：这里的搜索条件会在用户每次加载数据前提交到服务器，搜索的实现，
                                                要在服务端根据提交上来的条件自行实现，这里并不会提供默认的搜索功能
                                     */
    default_search_config: {        /* ===可选===，只有当is_default_search为true时才生效 */
        input_tip: "输入某字段关键字以查询...",   /* ===可选===，控制搜索输入框内的提示，默认是“输入关键字以查询...” */
        title: "某字段关键字"                     /* ===可选===，控制搜索输入框左边的提示，默认无提示 */
    },
    is_paging_tools: true,          /* ===可选===，默认是true，控制是否需要翻页工具 */
    is_load_all_data: true,         /* ===可选===，默认是true
                                                    目前存在两种情况的数据加载，第一种是从服务器加载全部可显示数据，然后在本地
                                                翻页操作时不再向服务器请求数据；第二种情况是数据太多，没法全部加载在本地，因此
                                                需要一页一页地去服务器请求数据。如果是第二种情况，那么这里要设置成false，每次
                                                翻页时重新向服务器请求数据。
                                                    在第一种情况中，页面的勾选操作是可以记忆的，比如勾选了部分数据，然后翻页，在
                                                翻页回来，是可以保持勾选状态的，但是第二种情况中，勾选功能不能记忆
                                                 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    check_obj: null,                /* ===可选===，当有数据需要检查才刷新时提交此对象 */
    event_handler: {
        before_load_data: function( list_obj ) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 时，系统向服务器重新加载数据之前调用此函数
             *
             * 参数： -- list_obj      ==可选==，列表面板实例
             * 返回：无
             */
        },
        after_load_data: function ( list_obj, response ) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 后，并且服务器响应后调用此函数
             *
                                    
             * 参数： -- add_obj    ==可选==，添加面板实例，用户可以通过add_obj.show_
             *        -- response   ==可选==, 服务器响应的数据
             * 返回：无
             */
        }
    },
    panel_header: [{            /* ***必填***，控制数据的加载以及表头显示 */
        enable: true,           /* ==可选==，作用于整列，如果为不填或者为false，那么定义的这一列都不会显示 */
        type: "checkbox",       /* ==可选==，作用于整列，type目前有checkbox/text/radio/action，分别对应不同类型的表头，
                                            默认是text类型，表示显示加载的数据，如果是checkbox，表示整列都显示checkbox框，
                                            如果是radio，表示整列都显示radio按钮，如果是action，表示这一列是操作列，可以自
                                            行定义要显示哪些操作按钮，也可以使用默认渲染的操作按钮，见“配置对象”（注释<1>）
                                            的render属性中的action属性
                                                type为checkbox类型和radio类型在一个列表面板中一般不能一起使用，到目前为止，
                                            也没有遇到这种需求，并且一起使用会有BUG。
                                                type为action的列，默认会渲染启用/禁用按钮（如果本行数据中包含enable字段的
                                            话会渲染）、编辑、删除，并且点击这三种类型按钮会有默认动作，点击启用/禁用按钮
                                            会自动向服务器发起启用/禁用相关规则的请求，具体能否启用/禁用相关规则，还要靠后
                                            台 的相关处理是否起作用；点击编辑时，会向添加面板加载数据并将添加面板切换为编
                                            辑状态（前提是“列表面板”设置了关联的“添加面板”具体使用方法见add_list_demo.js中
                                            set_ass_add_panel）；点击删除按钮时，会向服务器发起删除相关规则的请求，具体能
                                            否删除相关规则，也要靠后台处理结果
                                 */
        title: "",              /* =*可选*=，作用于标题头单元格，不同type，title需要的情况不同，
                                                一般type为text需要文字title，提示这一列数据表示什么意义，不填不显示标题
                                                当type为checkbox时，会默认渲染‘全选checkbox框’，填了title也将不起作用，
                                            当type为radio类型时，title变为‘请选择’，填了title也不起作用，当type为action时，
                                            默认标题是“活动/动作”，如果在action配置项填了title属性，会覆盖默认标题，示例见
                                            下文
                                 */
        name: "checkbox",       /* **必填**，作用于整列，控制整列要显示的数据项
                                                ****当type为checkbox、radio、action之一时，name也必须对应为三项中的一项
                                                如果要渲染每列数据，到“配置对象”（注释<1>）的render属性中去配置与当前name值
                                            一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见本文档第20行，再比
                                            如要渲染下文中classification列，见本文档的42行。
                                 */
        cls: "",                /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
        td_class: "",         /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                             当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                             在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                 */
        width: "5%",            /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                             以精确控制你想要的宽度
                                 */
        functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            onclick: "alert(this.value);"
        }
    }, {
        enable: false,
        type: "radio",
        title: "填啥都是‘请选择’",
        name: "radio",
        column_cls: "",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "发生时间",
        name: "time_start",
        width: "15%"
    }, {
        enable: true,
        type: "text",
        title: "入侵信息",
        width: "30%",           /* 这里宽度不起决定性作用 */
        children: [{            /* 支持两层标题套用 */
            type: "text",
            title: "入侵描述",
            name: "msg",
            width: "15%"        /* 最终决定宽度的是子节点 */
        }, {
            type: "text",
            title: "入侵类型",
            name: "classification",
            column_cls: "align-center",
            width: "15%"        /* 最终决定宽度的是子节点 */
        }]
    }, {
        enable: true,
        type: "text",
        title: "危险级别",
        name: "priority",
        column_cls: "align-center",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "源",
        name: "sip",
        width: "15%"
    }, {
        enable: true,
        type: "text",
        title: "目标",
        name: "dip",
        width: "15%"
    }, {
        enable: true,
        type: "action",
        title: "操作",
        name: "action",
        width: "10%"
    }],
    top_widgets: [{                     /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */
        enable: false,                  /* =*可选*=，如果为不填或者为false,就不创建 */
        type: "image_button",           /* =*可选*=，目前支持类型有text,password,file,select,checkbox,radio,textarea,
                                                    label,button,link_button和image_button,最常用的是image_button，
                                                    并且目前考虑得比较多其他组件比较弱，但能勉强使用，如果其他需求很强，
                                                    需要进一步扩展
                                         */
        id: "new_list",                 /* ==可选==，控件的id */
        name: "new_list",               /* ==可选==，控件的name */
        label: "按钮要闹哪样",          /* ==可选==，控件的标签，只有为checkbox、和radio才生效 */
        cls: "",                        /* ==可选==，按钮的样式，多个类以空格隔开 */
        button_icon: "add16x16.png",    /* ==可选==，image_button的图标，如果没有设置，就没有图标，image_button独有字段 */
        button_text: "新列表",          /* **必填**，image_button的文字，这个必须设置,建议在五个字以内，image_button独有字段 */
        functions: {                    /* ==可选==，回调函数，没有的话就只是一个按钮，什么也不做 */
        }
    }, {
        enable: false,
        type: "image_button",
        id: "enable_selected",
        name: "enable_selected",
        cls: "",
        button_icon: "on.png",
        button_text: "启用选中",
        functions: {
            onclick: "enable_selected_items(this)"
        }
    }, {
        enable: false,
        type: "image_button",
        id: "disable_selected",
        name: "disable_selected",
        cls: "",
        button_icon: "off.png",
        button_text: "禁用选中",
        functions: {
            onclick: "disable_selected_items(this)"
        }
    }, {
        enable: true,
        type: "checkbox",
        id: "stop_refresh",
        name: "stop_refresh",
        cls: "",
        label: "停止刷新"
    }, {
        enable: true,
        type: "select",
        title: "测试选择框",
        id: "select_test",
        name: "select_test",
        options: [{
            value: "test1",
            text: "test1"
        }]
    }],
    bottom_widgets: [{                  /* ===可选===，在面板左下角位置的控件组，创建方式类似top_widgets */
        enable: true,
        type: "link_button",
        id: "export_selected",
        name: "export_selected",
        href: "showca.cgi?type=pem",
        button_icon: "download.png",
        button_text: "导出选中",
        functions: {
            onclick: "export_selected_items(this)"
        }
    }, {
        enable: true,
        type: "image_button",
        id: "delete_all_logs",
        name: "delete_all_logs",
        cls: "",
        button_icon: "delete.png",
        button_text: "清空日志",
        functions: {
            onclick: "delete_all_logs(this)"
        }
    }],
    extend_search: [{               /* ===可选===，定义额外的搜索筛选条件，位置在面板右上角，控件类似top_widgets中控件 */
        enable: true,               /* ==可选==，如果为不填或者为false,就不显示*/
        type: "select",             /* ==可选==，默认为text类型 */
        id: "statistical_pattern",  /* ==可选==，控件ID */
        name: "statistical_pattern",/* **必填**，控件的名字 */
        title: "统计方式",          /* **必填**，输入控件前面的提示信息，没有会导致用户迷糊 */
        cls: "",                    /* ==可选==，控件本身样式的类名，会覆盖默认类的属性 */
        multiple: false,            /* ==可选==，select组件特有 */
        functions: {
            onchange: "alert(this.value);"
        },
        options: [{                 /* ==可选==，select组件特有 */
            id: "s_ip",
            name: "s_ip",
            cls: "test_class",
            value: "s_ip",
            text: "按源IP统计"
        }, {
            value: "d_ip",
            text: "按目的IP统计"
        }, {
            value: "s_port",
            text: "按服务端口统计"
        }],
        check: {                    /* ==可选==，如果定义了检测项，在查询之前要检查通过才能查询 */
            type: 'select-one',
            required: 1,
            ass_check: function( check ){
                
            }
        }
    }, {
        enable: true,
        type: "text",
        id: "page_size",
        name: "page_size",
        title: "显示条数",
        cls: "",
        value: 15,
        check: {
            type:'text',
            required: 1,
            check: 'int|',
            ass_check: function(){
                var val = $( "#page_size" ).val();
                if( val > 100 || val < 10 ) {
                    return "输入10-100之间的整数";
                }
            }
        }
    }, {
        enable: true,
        type: "image_button",
        id: "begin_search",
        name: "begin_search",
        button_icon: "search16x16.png",
        button_text: "搜索",
        cls: "my_search_button",
        functions: {
            onclick: "extend_search_function_extend_extend(this);"
        }
    }],
    actions: {                      /* ===可选===，如果想在点击默认渲染的按钮外接自己的函数时可以使用这里的接口，
                                        根据经验来看，这里的接口使用得很少，因为可以用render方案替代 */
        enable_button: function( data_item ) {
            alert("外部函数enable-" + data_item.id);
        },
        disable_button: function( data_item ) {
            alert("外部函数disable-" + data_item.id);
        },
        eidt_button: function( data_item ) {
            alert("外部函数eidt-" + data_item.id);
        },
        delete_button: function( data_item ) {
            alert("外部函数delete-" + data_item.id);
        },
        edit_item: function( data_item, on_finished ) {
            /* 开始书写自己的代码 */
            alert("外部函数eidt-正在编辑" + paging_holder.selected_item);
        }
    },
    bottom_extend_widgets: {        /* ===可选===，定义放在底部的按钮 */
        id: "",
        name: "",
        cls: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            cls: "",
            button_text: "确定",
            functions: {
                onclick: "show_mesg_when_ok();"
            }
        }, {
            enable: true,
            type: "image_button",
            cls: "",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: ""
            }
        }]
    }
};

var paging_holder = new PagingHolder( list_panel_config );

function enable_selected_items() {
    var checked_items = paging_holder.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    paging_holder.enable_item( ids );
}

function disable_selected_items() {
    var checked_items = paging_holder.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    paging_holder.disable_item( ids );
}

function extend_search_function_extend_extend( element ) {
    paging_holder.update_info( true );
    paging_holder.set_extend_search_item_title_by_id( "PAGESIZE", "当前显示条数" );
}

function show_mesg_when_ok( element ) {
    var checked_items = paging_holder.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );
    var mesg = "选择了" + ids;
    if ( ids == "" ) {
        mesg = "你啥都没选确定想干啥!?";
    }

    paging_holder.show_note_mesg( mesg );
}