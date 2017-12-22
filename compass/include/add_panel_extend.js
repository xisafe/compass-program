/*
 * 描述: 添加面板使用实例文件
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2014.09.18 WangLin创建
 */

$(document).ready(function(){
    /* 渲染面板 */
    rule_add_panel1.render();
    rule_add_panel2.render();
});

var ass_url = "/cgi-bin/add_panel.cgi";

var panel_config1 = {
    url: ass_url,                   /* ***必填***，控制数据向哪里提交 */
    check_in_id: "add_panel_1",     /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel_1",      /* ==*可选*==，默认名字my_add_panel，当一个页面存在多个添加面板，此字段必填，以区别不同面板，
                                                   当后台保存数据时，也要通过$panel_name来区分是哪个面板提交的数据 */
    is_panel_closable: false,       /* ===可选===，默认是false，控制面板是否可关闭，跟点击撤销按钮是一个效果 */
    rule_title_adding_icon: "upload.png",     /* ==*可选*==，默认是"add.png" */
    rule_title_editing_icon: "upload.png",    /* ==*可选*==，默认是"del.png" */
    rule_title_adding_prefix: "导入",
    rule_title: "文件",             /* ==*可选*==，默认是"规则" */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add : false,
        cancel : false,
        import : true
    },
    items_list: [{                  /* ***必填***，确定面板中有哪些规则，不填什么都没有，具体里面每项怎么配置，见下文panel_config2 */
        title: "选择文件",
        sub_items: [{
            enable: true,
            type: "file",
            id: "filename",
            name: "filename",
            value: ""
        }, {
            enable: true,
            type: "link",
            href: "showca.cgi?type=pem",
            link_icon: "download.png",
            link_text: "下载模板"
        }]
    }]
};

var panel_config2 = {
    url: ass_url,                   /* ***必填***，控制数据向哪里提交 */
    check_in_id: "add_panel_2",     /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel_2",      /* ==*可选*==，默认名字my_add_panel，当一个页面存在多个添加面板，此字段必填，以区别不同面板，
                                                   当后台保存数据时，也要通过$panel_name来区分是哪个面板提交的数据 */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭，跟点击撤销按钮是一个效果 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: false,                /* ===可选===，默认是false，控制面板是否模态显示 */
    is_panel_draggable : true,      /* ===可选===，默认是ture，控制面板是否可以拖拽 */ 
    border_transparent : true,      /* ===可选===，默认是ture，控制面板是否可以含边框 */ 
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "m",        /* ===可选===，默认是l,有l、m、s三种尺寸的模态框 */
        modal_level: 10             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    rule_title: "一条规则",         /* ==*可选*==，默认是"规则" */
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add : true,
        cancel : true,
        import : false,
        sub_items: [{               /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            enable: true,
            type: "button",
            value: "其他按钮",
            functions: {            /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                onclick: ""
            }
        }]
    },
    event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function( add_obj, data_item ) {
            /*
             * ===可选事件函数===，在数据项往添加面板加载时，数据还“未”装载入面板时调用，
             *    一般是点击编辑后数据项才会向添加面板加载
             *
             * 参数：-- add_obj   ==可选==，添加面板实例
             *        -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
        },
        after_load_data: function( add_obj, data_item ) {
            /*
             * ===可选事件函数===，在数据项往添加面板加载后，数据“已”装载入面板时调用
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *         -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
        },
        before_cancel_edit: function( add_obj ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
             *    在做这些默认的操作之“前”调用此函数
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *
             * 返回：无
             */
        },
        after_cancel_edit: function( add_obj ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
             *    在做这些默认的操作之“后”调用此函数
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *
             * 返回：无
             */
        },
        before_save_data: function( add_obj, sending_data ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的添加按钮时，系统向服务器提交添加面板的所有数据，
             *    在做提交数据之“前”会调用此函数
             *
             * 参数： -- add_obj       ==可选==，添加面板实例
             *        -- sending_data  ==可选==, 要向服务器提交的数据，
             *           用户可以通过 sending_data.xxx = xxx 添加向服务器提交的数据
             * 返回：true/false
             *       -- 返回true，或者不返回数据，数据会如实提交
             *       -- 返回false，会阻止数据向服务器其提交
             */
        },
        after_save_data: function( add_obj, received_data ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的添加按钮时，系统向服务器提交添加面板的所有数据，
             *    在做提交数据之“后”并且服务器响应之“后”会调用此函数
             *
             * 参数： -- add_obj       ==可选==，添加面板实例，可以调用add_obj.show_error_mesg( mesg )
             *           或者add_obj.show_note_mesg( mesg )等函数反馈信息给用户
             *        -- received_data ==可选==, 服务器响应的数据，
             *           可以在后台配置要传递的数据，并在此处访问
             * 返回：无
             */
        }
    },
    items_list: [{                  /* ***必填***，确定面板中有哪些规则，不填什么都没有 */
        title: "名称",              /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
        id: "name_tr",              /* ==可选==，整行的id */
        name: "",                   /* ==可选==，整行的name */
        cls: "",                    /* ==可选==，整行的class */
        functions: {                /* ==可选==，整行相应事件的回调函数，DOM标准事件都可生效 */
            /* onmouseover: "alert('hover on name line');", */
            // onclick: "alert('click on name line');"
        },
        sub_items:[{                /* **必填**，确定此行有哪些字段，不填什么都没有 */
            enable: true,           /* **必填**，如果为不填或者为false,就不创建 */
            label: "名称：",        /* ==可选==，字段前面的提示文字 */
            type: "text",           /* ==可选==，默认是text类型，支持text,password,button,file,select,checkbox,
                                                 radio,textarea,label,link,items_group
                                     */
            id: "name",             /* =*可选*=，字段的id，如果存在label字段，最好填写此字段 */
            name: "name",           /* **必填**，字段的名字 */

            cls: "",                /* ==可选==，输入框元素的class */
            item_id: "",            /* ==可选==，整个字段，包括前缀和后缀组件的id */
            item_cls: "",           /* ==可选==，整个字段，包括前缀和后缀组件的class */
            item_style: "",         /* ==可选==，整个字段的style */
            value: "test",          /* ==可选==，字段默认值 */
            label_id: "text_label",
            readonly: false,
            disabled: false,
            tip: "(输入4-20字符)",  /* ==可选==，字段输入提示 */
            functions: {            /* ==可选==，DOM标准事件都可生效 */
            },
            check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                type:'text',        /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required:'1',       /* **必填**，1表示必填，0表示字段可为空 */
                check:'name|',      /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
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
        }, {
            enable: true,
            label: "选择：",
            type: "select",
            id: "type",
            name: "type",
            tip: "请选择", 
            multiple: false,
            functions: {
                
            },
            options: [{             /* ==可选==,select组件特有的属性 */
                value: "s_ip",
                text: "按源IP统计"
            }, {
                value: "d_ip",
                text: "按目的IP统计",
                selected: true
            }, {
                value: "s_port",
                text: "按服务端口统计"
            }],
            check: {
                type:'select-one',
                required:'1',
                ass_check:function( check ){
                    
                }
            }
        }, {
            enable: true,
            label: "选择：",
            type: "select",
            tip: "请选择类型", 
            id: "type2",
            name: "type2",
            options: [{
                value: "s_ip",
                text: "按源IP统计"
            }, {
                value: "d_ip",
                text: "按目的IP统计",
                selected: true
            }, {
                value: "s_port",
                text: "按服务端口统计"
            }],
            multiple: true,
            functions: {
            },
            check: {
                type:'select-one',
                required:'1',
                ass_check:function( check ){
                    
                }
            }
        }]
    }, {
        title: "密码",
        sub_items:[{
            enable: true,
            label: "密码：",
            type: "password",
            id: "password",
            name: "password",
            tip: "请填写密码",
            disabled: true,
            value: "www12346",
            functions: {
                onclick: ""
            },
            check: {
                type:'password',
                required:'1',
                check:'other|',
                other_reg: '/.*/',
                ass_check:function( check ){
                    
                }
            }
        }]
    }, {
        title: "说明",
        sub_items:[{
            enable: true,
            label: "说明：",
            type: "textarea",
            tip: "请填写说明",
            id: "note",
            name: "note",
            value: "this is my note",
            readonly: false,
            check: {
                type:'textarea',
                required:'1',
                check:'other|',
                other_reg: '/.*/',
                ass_check:function( check ){
                    
                }
            }
        }]
    }, {
        title: "多选",
        sub_items:[{
            enable: true,
            label: "多选：",
            type: "items_group",
            tip: "请勾选",
            id:"checkboxs_group",
            cls: "",
            /* item_style: "width:40%;", */
            sub_items: [{
                enable: true,
                type: "checkbox",
                id: "sssssss",
                name: "checkboxs_group",
                value: "s_ip",
                label: "按源IP统计",
                checked: false,
                functions: {
                    onclick: ""
                }
            }, {
                enable: true,
                type: "checkbox",
                name: "checkboxs_group",
                value: "d_ip",
                label: "按目的IP统计",
                checked: true
            }, {
                enable: true,
                type: "checkbox",
                name: "checkboxs_group",
                value: "s_port",
                label: "按服务端口统计"
            }]
        }]
    }, {
        title: "单选",
        sub_items:[{
            enable: true,
            label: "单选：",
            type: "items_group",
            tip: "(选择其中之一吧)",
            id:"items_group_all_radios",
            sub_items: [{
                enable: true,
                type: "radio",
                id: "toggle1",
                name: "radios_group",
                value: "toggle1",
                label: "隐藏启用行",
                functions: {
                    onclick: "hide_or_show_tr(this);"
                }
            }, {
                enable: true,
                type: "radio",
                name: "radios_group",
                value: "toggle2",
                label: "显示启用行",
                checked: true,
                functions: {
                    onclick: "hide_or_show_tr(this);"
                }
            }]
        }]
    }, {
        title: "启用",
        cls: "enable_tr",
        sub_items: [{
            enable: true,
            type: "checkbox",
            id: "enable",
            name: "enable",
            /* value: "on", */
            text: "启用",
            checked: true
        }]
    }, {
        title: "集合组",
        sub_items: [{
            enable: true,
            type: "items_group",    /* 各种输入框的集合 */
            label: "左边的东东",
            item_style: "width:48%;",
            sub_items: [{
                enable: true,
                label: "点击启用左边边的输入框",
                type: "radio",
                tip: "(点击启用左边边的输入框)",
                name: "enable_one",
                value: "iam1",
                functions: {
                    onclick: "enable_left_or_right(this);"
                }
            }, {
                enable: true,
                label: "说明1",
                type: "text",
                name: "note1",
                disabled: true,
                cls: "i_am_belong_to_class_1",
                item_cls: "i_am_controled_by_1",
                tip: "(输入任意字符)",
                check: {
                    type: "text",
                    check: 'note|',
                    required: 0,
                    ass_check: function( check ) {
                    }
                }
            }, {
                enable: true,
                label: "说明2",
                type: "text",
                id: "note2",
                name: "note2",
                cls: "i_am_belong_to_class_1",
                disabled: true,
                item_cls: "i_am_controled_by_1",
                tip: "% (1-100的数字)",
                check: {
                    type: "text",
                    check: 'note|',
                    required: 0,
                    ass_check: function( check ) {
                        
                    }
                }
            }, {
                enable: true,
                type: "label",
                value: "",
                item_style: "height: 15px;width: 200px;"
            }]
        },{
            enable: true,
            type: "items_group",    /* 各种输入框的集合 */
            label: "右边的东东",
            item_style: "width:48%;",
            sub_items: [{
                enable: true,
                label: "启用右边的输入框",
                type: "radio",
                tip: "(点击启用右边的输入框)",
                name: "enable_one",
                value: "iam2",
                checked: true,
                functions: {
                    onclick: "enable_left_or_right(this);"
                }
            }, {
                enable: true,
                label: "名称1",
                type: "text",
                name: "name1",
                cls: "i_am_belong_to_class_2",
                item_cls: "i_am_controled_by_2",
                tip: "(输入4-20个字符哦~)",
                check: {
                    type: "text",
                    check: 'name|',
                    required: 0,
                    ass_check: function( check ) {
                        /* return "逗你玩呢,^_^，输入什么都不能通过的~~"; */
                    }
                }
            }, {
                enable: true,
                label: "数值1",
                type: "text",
                id: "number1",
                name: "number1",
                cls: "i_am_belong_to_class_2",
                item_cls: "i_am_controled_by_2",
                tip: "% (1-100的数字)",
                check: {
                    type: "text",
                    check: 'int|',
                    required: 0,
                    ass_check: function( check ) {
                        var value = $( "#number1" ).val();
                        if ( value > 100 || value < 1 ) {
                            return "请输入1-100的数字，没逗你玩哦";
                        }
                    }
                }
            }, {
                enable: true,
                label: "数值2",
                type: "text",
                id: "number2",
                name: "number2",
                cls: "i_am_belong_to_class_2",
                item_cls: "i_am_controled_by_2",
                tip: "% (10-100的数字)",
                check: {
                    type: "text",
                    check: 'int|',
                    required: 0,
                    ass_check: function( check ) {
                        var value = $( "#number2" ).val();
                        if ( value > 100 || value < 10 ) {
                            return "请输入10-100的数字^_^";
                        }
                    }
                }
            }]
        }, {
            enable: false,
            type: "select",
            name: "select1",
            options: [{
                value: 1,
                text: "选择1"
            }, {
                value: 2,
                text: "选择多多"
            }, {
                value: 3,
                text: "上一选择那是逗你玩的~"
            }]
        }]
    }]
};

var rule_add_panel1 = new RuleAddPanel( panel_config1 ),
    rule_add_panel2 = new RuleAddPanel( panel_config2 );

function enable_left_or_right( element ) {
    var value = element.value;
    if ( value == "iam1" ) {
        $( ".i_am_belong_to_class_2" ).attr( "disabled", true );
        $( ".i_am_belong_to_class_1" ).attr( "disabled", false );
    } else {
        $( ".i_am_belong_to_class_1" ).attr( "disabled", true );
        $( ".i_am_belong_to_class_2" ).attr( "disabled", false );
    }
}

function hide_or_show_tr( element ) {
    if( element.value == "toggle1" ) {
        $( ".enable_tr" ).hide();
    } else {
        $( ".enable_tr" ).show();
    }
}