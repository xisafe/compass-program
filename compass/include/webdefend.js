/*
 * 描述: 测试添加模板和列表模板类
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2014.09.23 WangLin创建
 */

/*
 * 注释<1>：此文档的“配置对象”指new PagingHolder时传入的对象
 */

$( document ).ready(function() {


	
    /* 渲染面板 */
    message_manager.render();
    // lib_panel.render();
    // lib_panel.hide();
    // lib_panel.update_info(true);

    // csrf_list_panel.render();
    // csrf_list_panel.hide();
    // csrf_list_panel.update_info(true);

    // csrf_add_panel.render();
    // csrf_add_panel.hide();

    csrf_add_panel.set_ass_list_panel( csrf_list_panel );
    csrf_list_panel.set_ass_add_panel( csrf_add_panel );

    // mgxx_list_panel.render();
    // mgxx_list_panel.hide();
    // mgxx_list_panel.update_info(true);

    // mgxx_add_panel.render();
    // mgxx_add_panel.hide();
    // mgxx_add_extend_render();
    // mgxx_add_panel.update_info(true);

    // brute_panel.render();
    // brute_panel.hide();

    // hideSite_panel.render();
    // hideSite_panel.hide();

    // brute_panel_show();

    var panel;
    var domain;
    var connect_type;
    // var mgxx_info;

    // mgxx_list_extend_render();
    // csrf_extend_render();
    
     (function() {
        //控制应用面板是否显示
        var control = parseInt( $("#apply-control").val() );
        if(control) {
            message_manager.show_apply_mesg();
        }
        
        //为form表单绑定检测方法
        var object = {
            "form_name": "webdefend-form",
            option: {
                'name': {
                    'type': 'text',
                    'required': '1',
                    'check': 'name|',
                    'ass_check': function(eve){                        
                    }
                },
                'description': {
                    'type': 'textarea',
                    'required': '0',
                    'check': 'note|',
                    'ass_check': function(eve){                       
                    }
                },
                'ipGroup': {
                    'type': 'select-one',
                    'required': '1',
                    'check': 'other|',
                    'other_reg': '/.*/'
                },
                'webRule': {
                    'type': 'textarea',
                    'required': '0',
                    'check': 'other|',
                    'other_reg': '/.*/'
                },
                'ipPort': {
                    'type': 'textarea',
                    'required': '1',
                    'check': 'port|',
                    ass_check:function( check ) {
                         var str = $("#webdefend-ipport").val();
                         if( str == "") {
                             return "该项不能为空";
                         }
                         var strs = new Array();
                         strs = str.split("\n");
                         for( var i=0; i<strs.length-1; i++) {
                             if (strs[i] == "") {
                                 return "请不要输入空的端口号";
                             }
                         }
                         if( !judgePort(strs) ) {
                             return "请不要输入重复的端口号";
                         } 
                     }
                }
            }
        }
        var check = new ChinArk_forms();
        check._main(object);
     })();
});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/webdefend.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}
var csrf_add_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "csrf_add_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "csrf_add_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "规则页面",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 12            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
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
    items_list: [{              /* ***必填***，确定面板中有哪些规则，不填什么都没有 */
        title: "需要防护的页面(Target)",          /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
        id: "name_tr",          /* ==可选==，整行的id */
        name: "",               /* ==可选==，整行的name */
        cls: "",                /* ==可选==，整行的class */
        functions: {            /* ==可选==，整行相应事件的回调函数，DOM标准事件都可生效 */
            // onmouseover: "alert('hover on name line');",
            // onclick: "alert('click on name line');",
        },
        sub_items: [{           /* **必填**，确定此行有哪些字段，不填什么都没有 */
            enable: true,       /* **必填**，如果为不填或者为false,就不创建 */
            type: "text",       /* ==可选==，默认是text类型，支持text,password,button,file,select,checkbox,
                                             radio,textarea,label,items_group
                                 */
            name: "need_target",       /* **必填**，字段的名字 */
            value: "",          /* ==可选==，字段默认值 */
            tip:'需以/字符开头',
            functions: {        /* ==可选==，DOM标准事件都可生效 */
            },
            check: {            /* ==可选==，如果要对字段进行检查，填写此字段 */
                type: "text",   /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required: 1,    /* **必填**，1表示必填，0表示字段可为空 */
                check: 'other|', /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                other_reg:'/^\\/[a-zA-Z0-9\\_\\-\\.\\/\\\\]+$/',
                ass_check: function( check ) {
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
        title: "允许访问的来源页面(Rerfer)",
        sub_items: [{
            enable: true,
            type: "text",
            id: "note",
            name: "allow_rerfer",
            value: "",
            tip:'需以/字符开头',
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check: 'other|',
                other_reg:'/^\\/[a-zA-Z0-9\\_\\-\\.\\/\\\\]+$/',
                ass_check: function( check ) {

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
            text: "启用",
            checked: true
        }]
    }]
};
var csrf_list_panel_render = {
    'action': {
        render: function( default_rendered_text, data_item ) {
            var enable = data_item.enable;
            var toggle_class, button_text, button_icon, onclick;

            if( enable == "off"){
                button_icon = "off.png";
                button_text = "启用";
                onclick = "change_status('on','"+data_item.id+"')";
            }
            else{
                button_icon = "on.png";
                button_text = "禁用";
                onclick = "change_status('off','"+data_item.id+"')";
            }

            var action_buttons = [
                {
                    enable: true,
                    button_icon: button_icon,
                    value: data_item.index,
                    button_text: button_text,
                    functions: { 
                        onclick: onclick,
                    },
                    class:"action-image"
                },
                {
                    "enable": true,
                    "id": "edit_item",
                    "name": "edit_item",
                    "button_icon": "edit.png",
                    "button_text": "编辑",
                    "value": data_item.id,
                    "functions": {
                        onclick: "edit_rule(this.value);"
                    },
                    "class": "action-image",
                },
                {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "value": data_item.id,
                    "functions": {
                        onclick: "delete_rule(this.value);"
                    },
                    "class": "action-image",
                }
            ];

            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};
var hideSite_panel_config = {
   
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "panel_site_hide",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "hideSite_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "站点隐藏-报头设置",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    event_handler:{
         before_load_data: function( add_obj,data_item ) {
            //$("#head").empty();
            /*$("#head").append("<option value='br0'>Server</option>");
            $("#head").append("<option value='br1'>X-Powered-By</option>");*/
        },
        before_save_data: function( add_obj,sending_data ) {

        },
         after_load_data: function( add_obj,data_item ) {
            /*
             * ===可选事件函数===，在数据项往添加面板加载后，数据“已”装载入面板时调用
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *         -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
           
            
         }
    },
    footer_buttons:{
        sub_items:[
        {
            enable:true,
            type:"button",
            style:"",
            id:"save",
            value:"完成",
            functions:{
                onclick:"save_complete();"
            },
        },
        {
            enable:true,
            type:"button",
            style:"",
            id:"cancel",
            value:"取消",
            functions:{
                onclick:"hideSite_panel.hide();"
            },
        }
        ],
       /* cancel:true,*/
     },
 
   items_list: [
        {
          title: "",
          sub_items: [ 
            {
                enable: true,
                type: "select",
                style:"width:130px",
                id: "head",
                name: "head",
               
            },
            {
                
                enable: true,
                type: "text",
                style:"width:130px",
                id: "headertxt",
                name: "headertxt",
                check: {
                    type: "text",
                    required: 1,
                    check: 'note|',
                    ass_check: function( check ) {

                    }
                }
                
            },
            {
                enable: true,
                type: "button",
                style:"min-width:50px;",
                id: "add",
                name: "add",
                value:"添加",
                functions:{
                onclick:"addHead();"
            },
                check: {
                    
                }
            },
            {
                enable: true,
                type: "button",
                style:"min-width:50px;",
                id: "httpcancel",
                name: "httpcancel",
                value:"移除",
                functions:{
                onclick:"deleteHead();"
            },
                check: {
                    
                }   
            }

            ]},

        { 
            title: "",
            sub_items: [ {
                enable: true,
                type: "select",
                style:"height:150px;width:454px;",
                "multiple": true,
                id: "head_content",
                name: "head_content",
                value:"",
               /* readonly:"readonly",*/
                check: {
                    
                }   
            }]},
            {
                title: "",
                sub_items: [ {
                    enable:true,
                    label:"替换HTTP出错页面",
                    type:"checkbox",
                    id:"replace_page",
                    // checked: "checked",
                    name:"replace_page",
                    style:"vertical-align: middle;margin-top: -7px;",
                    // value:"1",
                    functions:{
                        // onclick:"judgeStrategy(this.value);"
                    }
                }]
                
            }
        ]
};

var csrf_list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "csrf_list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "csrf_list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 8,
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "新增CSRF防护页面",
    is_panel_closable: true,
    is_paging_tools: true,
    is_default_search: false,
    is_modal: true,
    render: csrf_list_panel_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    title_icon:"add.png",
    event_handler: {
        before_load_data: function( list_obj ) {

        },
        after_load_data: function ( list_obj, response ) {

        }
    },
    panel_header: [ {        /* ***必填***，控制数据的加载以及表头显示 */
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
                                            一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                            第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                 */
        cls: "",                /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
        column_cls: "",         /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                             当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                             在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                 */
        width: "8%",            /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                             以精确控制你想要的宽度
                                 */
        functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            // onclick: "alert(this.value);"
        }
    },
    {
        enable: true,
        type: "text",
        title: "需要防护的页面(Target)",
        name: "need_target",
        width: "40%"
    }, {
        enable: true,
        type: "text",
        title: "允许访问的来源页面(Rerfer)",
        name: "allow_rerfer",
        width: "40%"
    }, {
        enable: true,
        type: "action",
        name: "action",
        width: "20%",
        td_class:"align-center"
    }],
    top_widgets: [{                     /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */
        enable: true,                   /* =*可选*=，如果为不填或者为false,就不创建 */
        type: "image_button",           /* =*可选*=，目前支持类型有text,password,file,select,checkbox,radio,textarea,
                                                    label,button和image_button,最常用的是image_button，并且目前考虑得
                                                    比较多其他组件比较弱，但能勉强使用，如果其他需求很强，需要进一步
                                                    扩展
                                         */
        button_icon: "add16x16.png",    /* ==可选==，image_button的图标，如果没有设置，就没有图标，image_button独有字段 */
        button_text: "新建规则",        /* **必填**，image_button的文字，这个必须设置,建议在五个字以内，image_button独有字段 */
        functions: {                    /* ==可选==，回调函数，没有的话就只是一个按钮，什么也不做 */
            onclick: "add_rule(this);"
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
    },
    {
        "enable": true,
        type: "image_button",
        "id": "delete_selected",
        "name": "delete_selected",
        "class": "",
        "button_icon": "on.png",
        "button_text": "启用选中",
        "functions": {
            onclick: "change_status('on','')"
        } 
    },
    {
        "enable": true,
        type: "image_button",
        "id": "delete_selected",
        "name": "delete_selected",
        "class": "",
        "button_icon": "off.png",
        "button_text": "禁用选中",
        "functions": {
            onclick: "change_status('off','')"
        }
    }],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        // style:"background:#A4C2E4",
        sub_items: [
            {
                enable: true,
                type: "image_button",
                class: "",
                style: "margin-top: 5px;margin-bottom: 5px;",
                button_text: "确定",
                functions: {
                    onclick: "save_domain();"
                }
            }, {
                enable: true,
                type: "image_button",
                class: "",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "csrf_list_panel_hide()"
                }
            }
        ]
    }
};

var mgxx_add_panel_render = {
    'mgxx_reg': {
        render: function( default_rendered_text, data_item ) {
            default_rendered_text = default_rendered_text.replace(/\&lt;br\/&gt;/g , '<br/>')
            return default_rendered_text
        }
    },
}

var mgxx_add_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "mgxx_add_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mgxx_add_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 50,
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "防护的敏感信息",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    render_to_text:false,
    render:mgxx_add_panel_render,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 12
    },
    title_icon:"add.png",
    event_handler: {
        before_load_data: function( list_obj ) {

        },
        after_load_data: function ( list_obj, response ) {
            var null_td = $("#list_panel_id_for_mgxx_add_panel").find('.container-main-body table tbody').find('tr');
            null_td.each(function(index, el) {
                if (index > (response.total_num-1)) {
                    $(this).remove();
                }
            });
        }    
            
    },
    panel_header: [ {        /* ***必填***，控制数据的加载以及表头显示 */
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
                                            一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                            第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                 */
        cls: "",                /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
        column_cls: "",         /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                             当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                             在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                 */
        width: "8%",            /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                             以精确控制你想要的宽度
                                 */
        functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            // onclick: "alert(this.value);"
        }
    },
    {
        enable: true,
        type: "text",
        title: "序号",
        name: "index",
        width: "10%",
        td_class:"align-center"
    }, {
        enable: true,
        type: "text",
        title: "敏感信息名称",
        name: "mgxx_name",
        width: "20%"
    },{
        enable: true,
        type: "text",
        title: "类别",
        name: "type",
        width: "15%",
    }, {
        enable: true,
        type: "text",
        title: "正则表达式",
        name: "mgxx_reg",
        width: "35%"
    }],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        // style:"background:#A4C2E4",
        sub_items: [
            {
                enable: true,
                type: "image_button",
                class: "",
                style: "margin-top: 5px;margin-bottom: 5px;",
                button_text: "确定",
                functions: {
                    onclick: "save_mgxx();"
                }
            }, {
                enable: true,
                type: "image_button",
                class: "",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "mgxx_add_panel.hide();"
                }
            },
            {
                enable: true,
                type: "hidden",
                class:"edit_id",
                value:'',
                style:'display:none;',
                functions: {
                    onclick: ";"
                }
            }
        ]
    }
};
var mgxx_list_panel_render = {
    'action': {
        render: function( default_rendered_text, data_item ) {
            // var item = JSON.stringify(data_item);
            var action_buttons = [
                {
                    "enable": true,
                    "id": "edit_item",
                    "name": "edit_item",
                    "button_icon": "edit.png",
                    "button_text": "编辑",
                    "value": data_item.id,
                    // "functions": {
                    //     onclick: "edit_rule("+data_item+");"
                    // },
                    "class": "action-image",
                },
                {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "value": data_item.id,
                    "functions": {
                        onclick: "delete_rule(this.value);"
                    },
                    "class": "action-image",
                }
            ];
            var temp = PagingHolder.create_action_buttons( action_buttons );
            var btn$ = $(temp);
           $(btn$[0]).on('click', function() {
                event.preventDefault();
                // mgxx_info = data_item.mgxx_info;
               edit_rule(data_item);
           });
            return btn$;
        }
    }
};
var mgxx_list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "mgxx_list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mgxx_list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 8,
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "防护的敏感信息",
    is_panel_closable: true,
    is_paging_tools: true,
    is_default_search: false,
    render: mgxx_list_panel_render,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    title_icon:"add.png",
    event_handler: {
        before_load_data: function( list_obj ) {

        },
        after_load_data: function ( list_obj, response ) {
            if (response.total_num != 0) {
                connect_type = response.detail_data[0].connect_type;
            }else{
                connect_type = 'no_type';
            }
            // console.log(response.detail_data[0].connect_type);
            // console.log(response);
        }
    },
    panel_header: [ {        /* ***必填***，控制数据的加载以及表头显示 */
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
                                            一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                            第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                 */
        cls: "",                /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
        column_cls: "",         /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                             当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                             在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                 */
        width: "8%",            /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                             以精确控制你想要的宽度
                                 */
        functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            // onclick: "alert(this.value);"
        }
    },
    {
        enable: true,
        type: "text",
        title: "敏感信息组合策略",
        name: "mgxx_comb_stra",
        width: "24%"
    }, {
        enable: true,
        type: "text",
        title: "描述",
        name: "description",
        width: "24%"
    },{
        enable: true,
        type: "text",
        title: "最低命中次数",
        name: "min_num",
        width: "24%"
    }, {
        enable: true,
        type: "action",
        name: "action",
        width: "20%",
        td_class:"align-center"
    }],
    top_widgets: [{                     /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */
        enable: true,                   /* =*可选*=，如果为不填或者为false,就不创建 */
        type: "image_button",           /* =*可选*=，目前支持类型有text,password,file,select,checkbox,radio,textarea,
                                                    label,button和image_button,最常用的是image_button，并且目前考虑得
                                                    比较多其他组件比较弱，但能勉强使用，如果其他需求很强，需要进一步
                                                    扩展
                                         */
        button_icon: "add16x16.png",    /* ==可选==，image_button的图标，如果没有设置，就没有图标，image_button独有字段 */
        button_text: "新建规则",        /* **必填**，image_button的文字，这个必须设置,建议在五个字以内，image_button独有字段 */
        functions: {                    /* ==可选==，回调函数，没有的话就只是一个按钮，什么也不做 */
            onclick: "add_rule(this);"
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
    }],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        // style:"background:#A4C2E4",
        sub_items: [
            {
                enable: true,
                type: "image_button",
                class: "",
                style: "margin-top: 5px;margin-bottom: 5px;",
                button_text: "确定",
                functions: {
                    onclick: "change_connect_type();"
                }
            }, {
                enable: true,
                type: "image_button",
                class: "",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "mgxx_list_panel.hide();"
                }
            }
        ]
    }
};

var brute_panel_config = {
   
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "panel_brute",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "brute_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "口令暴力破解防护",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    event_handler:{
         before_load_data: function( add_obj,data_item ) {
            
        },
        before_save_data: function( add_obj,sending_data ) {

        },
         after_load_data: function( add_obj,data_item ) {
           
         }
    },
    footer_buttons:{
        sub_items:[
        {
            enable:true,
            type:"button",
            style:"",
            id:"save",
            value:"完成",
            functions:{
                onclick:"save_brute_complete();"
            },
        },
        {
            enable:true,
            type:"button",
            style:"",
            id:"cancel",
            value:"取消",
            functions:{
                onclick:"brute_panel.hide();"
            },
        }
        ],
       /* cancel:true,*/
     },
 
   items_list: [
        {
          title: "WEB登陆页面",
          sub_items: [ 
            {
                enable: false,
                type: "label",
                style:"background-color:#e4e8eb",
                value:"WEB登陆页面",
            },
            {
                enable: true,
                type: "textarea",
                value:"",
                style:"height:100px;",
                id: "loginpage",
                name: "loginpage",
                tip: '需以"/"字开头（如/login.html）',
                check: {
                  type: "textarea",
                  required: 1,
                  check: 'other|',
                  other_reg:'/^\\/[a-zA-Z0-9\\_\\-\\.\\/\\\\]+$/' 
                }
            }
            ]},

        { 
            title: "爆破次数",
            sub_items: [ 
             {
                enable: false,
                type: "label",
                style:"background-color:#e4e8eb",
                value:"爆破次数",
            },
             {
                enable: true,
                type: "text",
                style:"width:99px;",
                id: "brute_number",
                name: "brute_number",
                value:"",
               /* readonly:"readonly",*/
                check: {
                    type: "text",
                    required: 1,
                    check: 'num|',
                 
                }   
            },
            {
                enable: true,
                type: "select",
                style:"width:89px;",
                id: "rate",
                name: "rate",
                options:
                [
                    {
                        text: "次/分钟",
                        value: "min"
                    },
                    {
                        text: "次/小时",
                        value: "hour"
                    },
                ]

            }
            ]}
        ]
};

var lib_panel_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "panel_rule_lib",         // ***必填***，确定面板挂载在哪里 
    page_size: 10,                  //===可选===，定义页大小，默认是15 
    panel_name: "lib_panel",       // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置WEB防护规则",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    title_icon:"add.png",
    panel_header: [                 // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",           //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "class": "",                //元素的class
            "td_class": "",             //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": false,
            "type": "radio",
            "name": "radio",
            "td_class": "rule-listbc",
            "width": "5%"
        }, {
            "enable": true,
            "type": "text",
            "title": "WEB规则名称",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "30%"
        }, {
            "enable": true,
            "type": "text",
            "title": "描述",
            "name": "description",
            "width": "60%"
        }
    ],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [
            {
                enable: true,
                type: "image_button",
                class: "",
                style: "margin-top: 5px;margin-bottom: 5px;",
                button_text: "确定",
                functions: {
                    onclick: "write_lib_data();"
                }
            }, {
                enable: true,
                type: "image_button",
                class: "",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "lib_panel.hide();"
                }
            }
        ]
    }
}

var lib_panel = new PagingHolder( lib_panel_config );

var csrf_list_panel = new PagingHolder( csrf_list_panel_config );
var csrf_add_panel = new RuleAddPanel( csrf_add_panel_config );

var mgxx_list_panel = new PagingHolder( mgxx_list_panel_config );
var mgxx_add_panel = new PagingHolder( mgxx_add_panel_config );
var hideSite_panel = new RuleAddPanel( hideSite_panel_config );
var brute_panel = new RuleAddPanel( brute_panel_config );

var message_manager = new MessageManager( message_box_config );

//将特征库数据写入配置输入框
function write_lib_data(){
    var checked_items = lib_panel.get_checked_items();
	var str = "";
	var length = checked_items.length;
	if(!checked_items[0]) {
		$("#webdefend-webrule").val("");
	}else{
    	for(var i = 0; i < length-1; i++) {
    		str += checked_items[i].name + "\n";
    	}
    	str += checked_items[length-1].name;
        $("#webdefend-webrule").html(str);
        $("#webdefend-webrule").val(str);
	}
    lib_panel.hide();
}
//判定端口号是否重复
function judgePort (e) {
	var array = e;
	array.sort(function(a,b){
		return a - b;
	});
	for ( var i = 0; i < array.length; i++ ) {
		if( array[i] == array[i+1] ) {

			return false;
			}
	}
	return true;
}

function delete_selected_items( element ) {

    var checked_items = panel.get_checked_items();

    if ( checked_items.length == 0 ) {
        panel.show_error_mesg( "请选择要删除的规则" );
        return;
    }
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    panel.delete_item( ids );
}

function panel_show(ele) {
    var eleData = $(ele).attr('data');
    if (eleData == 'csdf') {
        panel = csrf_list_panel;
        if ($('#csrf_list_panel').html() == '') {
            csrf_list_panel.render();
            csrf_list_panel.update_info(true);
            csrf_add_panel.render();
            csrf_add_panel.hide();
            csrf_extend_render();
            var sending_data = {
                ACTION: 'load_domain',
            };
            function ondatareceived(data) {
                $("#csdf_domain_name").val(data.domain);
                domain = data.domain;
            }
            do_request(sending_data, ondatareceived);
        }
        
    }else if (eleData == 'mgxx'){
        panel = mgxx_list_panel;
        if ($('#mgxx_list_panel').html() == '') {
            panel.render();
            panel.update_info(true);
            mgxx_list_extend_render();
        }
    }else if (eleData == 'brute'){
        panel = brute_panel;  
        if ($('#panel_brute').html() == '') {
            panel.render();  
            brute_panel_show();
        }
    }else if(eleData == 'hideSite'){
        panel = hideSite_panel;
        if ($('#panel_site_hide').html() == '') {
            panel.render();
            brute_panel_show();
        }   
    }else if(eleData == 'lib'){
        panel = lib_panel;
        
        if ($('#panel_rule_lib').html() == '') {
            panel.render();
            panel.update_info(true);
        }

        $("#list_panel_id_for_lib_panel").children(".toolbar").eq(2).css("background","#D5E2F2")
        .siblings('.toolbar').remove();
        
        var webdefend_select = $("#webdefend-webrule").html();
        var webdefend_select_arr = webdefend_select.split('\n');
        $("#rule_listb_for_lib_panel tr").each(function() {
            for (var i = 0; i < webdefend_select_arr.length; i++) {
                if ($(this).children('td').eq(1).html() == webdefend_select_arr[i] ) {
                    $(this).children('td').eq(0).children('input')[0].checked = true;
                    for (var i = 0; i < lib_panel.detail_data.length; i++) {
                        lib_panel.detail_data[$(this).index()].checked = true;
                    }
                }
            }
            
        });
    }

    panel.show();
}

function add_rule(ele) {
    if (panel == csrf_list_panel) {
        csrf_add_panel.show();
    }else if(panel == mgxx_list_panel){

        mgxx_add_panel.render();
        mgxx_add_extend_render();

        mgxx_add_panel.update_info(true);
        mgxx_add_panel.show();
        $(".widgets-item .edit_id").val('');
        $(".widgets-item .edit_id").attr('data', '');
    }
}

function create_action_buttons( action_buttons ) {
    var buttons = "";

    if( action_buttons === undefined ) {
        return buttons;/*如果没有定义相应的对象，直接返回*/
    }

    for( var i = 0; i< action_buttons.length; i++ ) {
        var item = action_buttons[i];
        if( item.enable === undefined || !item.enable ){
            continue;
        }
        buttons += '<input type="image" ';
        if( item.id !== undefined && item.id ) {
            buttons += 'id="' + item.id + '" ';
        }
        if( item.value !== undefined && item.value ) {
            buttons += 'value="' + item.value + '" ';
        }
        if( item.name !== undefined && item.name ) {
            buttons += 'name="'+ item.name +'" ';
        }
        if( item.class !== undefined && item.class ) {
            buttons += 'class="action-image ' + item.class + '" ';
        } else {
            buttons += 'class="action-image" ';
        }
        if( item.button_text !==undefined && item.button_text ) {
            buttons += 'title="' + item.button_text + '" ';
        }
        if( item.button_icon !== undefined && item.button_icon ) {
            buttons += 'src="../images/' + item.button_icon +'" ';
        }
        if( item.functions !== undefined && item.functions ) {
            var functions = item.functions;
            for ( var key in functions ) {
                buttons += key +'="' + functions[key] + '" ';
            }
        }
        buttons += '/>';
    }

    return buttons;
}

function change_status(status,id){
    if (id != '') {
        if (status == 'on') {
            panel.enable_item( id );
        }else{
            panel.disable_item( id );
        }
    }else{
        var checked_items = panel.get_checked_items();
        if ( checked_items.length < 1){
            message_manager.show_popup_note_mesg("至少选择一项！");
        }else{
            var checked_items_id = new Array();
            for( var i = 0; i < checked_items.length; i++ ) {
                checked_items_id.push( checked_items[i].id );
            }
        
            var ids = checked_items_id.join( "&" );
            
            if (status == 'on') {
                panel.enable_item( ids );
            }else{
                panel.disable_item( ids );
            }
        }
        
    }
}

function edit_rule(item){
    if (panel == csrf_list_panel) {
        edit_id = item;
        panel.edit_item(item);
    }else if (panel == mgxx_list_panel) {
        mgxx_add_panel_config.bottom_extend_widgets.sub_items[2].value = item.id;
        mgxx_add_panel.render();
        

        mgxx_add_panel.update_info(true);
        mgxx_add_panel.show();
        mgxx_add_extend_render();
        $(".widgets-item .edit_id").attr('data', 'edit');
        $("#mgxx_add_panel_form_name").val(item.mgxx_comb_stra);
        $("#mgxx_add_panel_form_description").val(item.description);
        $("#mgxx_add_panel_form_num").val(item.min_num);
        var mgxx_info = item.mgxx_info.split('&');
        for (var i = 0; i < mgxx_info.length; i++) {
            for (var j = 0; j < mgxx_add_panel.detail_data.length; j++) {
                if (mgxx_add_panel.detail_data[j].storage_id == mgxx_info[i]) {
                    $("#rule_listb_for_mgxx_add_panel tr").eq(j).children('td').eq(0).children('input')[0].checked = true;
                }
                
            }
            
        }
        // $("#rule_listb_for_mgxx_add_panel tr").each(function() {
        //     for (var i = 0; i < mgxx_info.length; i++) {
        //         if (mgxx_info[i] == $(this).index()) {
        //             $(this).children('td').eq(0).children('input')[0].checked = true;
        //         } 
        //     }
        // });
    }
    
}

//删除规则函数，包含规则引用检查
function delete_rule(item_id){

    var data_item = panel.get_item(item_id);
    panel.delete_item(data_item.id);
}

function save_domain() {
    var csdf_domain_name_val = $("#csdf_domain_name").val();
    var domain_reg = /^([\S]+\.[\S]+)+$/;
    if (csdf_domain_name_val == '') {
        message_manager.show_popup_error_mesg('您还没填写域名！');
    }else{
        if (csdf_domain_name_val != domain) {
            if (domain_reg.test(csdf_domain_name_val)) {
                domain = csdf_domain_name_val;
                var sending_data = {
                    ACTION: 'sava_domain_brute',
                    domain: csdf_domain_name_val,
                    panel_name:'csrf_list_panel'
                };
                function ondatareceived(data) {
                    if (data.status == '0') {
                       
                        panel.hide();
                    }else{
                        panel.show_error_mesg(data.mesg);
                    }
                }
                do_request(sending_data, ondatareceived);
            }else{

                message_manager.show_popup_error_mesg('域名格式错误');
            }
        }else{
            panel.hide();
        }
        
    }
    
}
function change_connect_type() {
    var mgxx_select = $("#mgxx_select").find("option:selected").val();
    // if (mgxx_select != connect_type) {
        var sending_data = {
            ACTION: 'change_connect_type',
            mgxx_select:mgxx_select
        };
        function ondatareceived(data) {
            if (data.status == '0') {
               
                panel.hide();
            }else{
                panel.show_error_mesg(data.mesg);
            }
        }
        do_request(sending_data, ondatareceived);
    // }
    // else{
    //     panel.hide();
    // }
}
function save_mgxx() {
    var mgxx_name = $("#mgxx_add_panel_form_name").val();
    var mgxx_description = $("#mgxx_add_panel_form_description").val();
    var mgxx_num = $("#mgxx_add_panel_form_num").val();
    var mgxx_checked_id = [];
    $("#rule_listb_for_mgxx_add_panel tr").each(function() {
        if ($(this).children('td').eq(0).children('input')[0].checked) {
            mgxx_checked_id.push(mgxx_add_panel.detail_data[$(this).index()].storage_id);
        }
    });
    // var mgxx_checked = mgxx_add_panel.get_checked_items();
    // var mgxx_checked_id = [];
    // for (var i = 0; i < mgxx_checked.length; i++) {
    //     mgxx_checked_id[i] = mgxx_checked[i].id;
    // }
    var mgxx_checked_id_json = mgxx_checked_id.join('&');

    var mgxx_select = $("#mgxx_select").find("option:selected").val();
    if (connect_type != 'no_type') {
        mgxx_select = connect_type;
    }
    var edit_id = $(".edit_id").val();
    var edit_id_data = $(".edit_id").attr('data');
    if ($('#mgxx_add_panel_form').find('.userTipError').length >0) {
        message_manager.show_popup_error_mesg('填写有误，请检查后重新提交！')
        return
    }

    if (mgxx_name != '' && mgxx_num != '' && mgxx_checked_id != '') {
        if (!/^[1-9]\d*$/.test(Number(mgxx_num))) {
            message_manager.show_popup_error_mesg('最低命中次数必须是大于零的整数！');

        }else{
            var sending_data = {
                ACTION: 'save_data',
                mgxx_name:mgxx_name,
                mgxx_description: mgxx_description,
                mgxx_num:mgxx_num,
                panel_name:'mgxx_list_panel',
                mgxx_checked:mgxx_checked_id_json,
                mgxx_select:mgxx_select,
            };
            if (edit_id_data != '') {
                sending_data.id = edit_id;
            }
            function ondatareceived(data) {
                if (data.status == '0') {
                    // mgxx_list_panel.show_note_mesg('保存成功');
                    mgxx_add_panel.hide();

                    mgxx_list_panel.update_info(true);
                }else{
                    mgxx_list_panel.show_error_mesg(data.mesg);
                }
            }
            do_request(sending_data, ondatareceived);
        }
        
    }else{

        message_manager.show_popup_error_mesg('名称，敏感信息，最低命中次数不能为空！');
    }
}
//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: ass_url,
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

function mgxx_list_extend_render() {
    var mgxx_add_info = '<div class="csrf-panel" style="padding: 6px 14px;"><span>命中次数统计方式：</span><select name="mgxx_select" id="mgxx_select">'
    if (mgxx_list_panel.detail_data.length && mgxx_list_panel.detail_data[0].connect_type === 'conn') {
        mgxx_add_info +='<option value="conn">以连接统计</option><option value="ip">以IP统计</option>'
    }else{
        mgxx_add_info += '<option value="ip">以IP统计</option><option value="conn">以连接统计</option>'
    }
    $("#list_panel_id_for_mgxx_list_panel .toolbar .opt-tools")
    .before(mgxx_add_info+'</select></div>');
   
}
function mgxx_add_extend_render() {
 
    $("#list_panel_id_for_mgxx_add_panel").find('.container-main-body')
    .before('<p class="mgxx_add_panel_title"><span>选择要组合的敏感信息：</span><span class="title_tips">（可选多条，必须同时满足勾选内容）</span></p>')
    
    $("#list_panel_id_for_mgxx_add_panel").find('.container-main-body')
        .after('<form action="" id="mgxx_add_panel_form" name="mgxx_add_panel_form"></form>')
    $("#mgxx_add_panel_form").append('<ul><li><span>名称 *&nbsp&nbsp</span><input type="text" id="mgxx_add_panel_form_name" name="mgxx_add_panel_form_name"></li><li><span>描述</span><input type="text" id="mgxx_add_panel_form_description" name="mgxx_add_panel_form_description"></li><li><span>最低命中次数 *</span><input type="text" id="mgxx_add_panel_form_num" name="mgxx_add_panel_form_num"></li></ul>')

    var check = new ChinArk_forms();
    var object = {
        'form_name':'mgxx_add_panel_form',
        'option':{
            'mgxx_add_panel_form_name':{
               'type':'text',
               'required':'1',
               'check':'name|'
            },
            'mgxx_add_panel_form_description':{
               'type':'text',
               'required':'0',
               'check':'note|'
            },
            'mgxx_add_panel_form_num':{
               'type':'text',
               'required':'1',
               'check':'num|'
            }
        }
    }
    check._main(object);
}
function csrf_extend_render() {
    $("#list_panel_id_for_csrf_list_panel .toolbar .opt-tools")
    .before('<div class="csrf-panel" style="padding: 6px 14px;"><span>域名：</span><input type="text" value="" id="csdf_domain_name" name="csdf_domain_name"></div>');  
}
/*存储口令防护配置面板*/
function save_brute_complete(){

    if (!panel.is_input_data_correct()) {
        message_manager.show_popup_error_mesg("请填写正确格式！");
        return false;
    }
    var loginpage = $("#loginpage").val().replace(/\n/g,"&");
    var brute_number = $("#brute_number").val();
    var rate = $("#rate").val();
    var sending_data = {
      ACTION: 'sava_domain_brute',
      loginpage: loginpage,
      brute_number: brute_number,
      rate: rate,
      panel_name:'brute_panel'
    }

    function ondatareceived(data) {
      // console.log('aaa');
      if (data.status != 0) {
        message_manager.show_error_mesg(data.mesg);
      }
    }
    do_request(sending_data, ondatareceived);
    brute_panel.hide();
}

/*读取口令配置文件数据*/
function brute_panel_show (){

    var sending_data = {
      ACTION: "load_brute_data",
      panel_name: "brute_panel"
    }

    function ondatareceived(data) {
        if (panel == brute_panel) {
            $("#loginpage").val(data.loginpage);
            var temp = $("#loginpage").val().replace(/\&/g,"\n");
            $("#loginpage").val(temp);
            $("#brute_number").val(data.brute_number);
            $("#rate").val(data.rate);
        }else{
            $("#head").empty();
            for(var i=0;i<data.headers.length;i++){
            $("#head").append("<option value="+data.headers[i]+">"+data.headers[i]+"</option>");
            };

            $("#head_content").empty();
            for(var i=0;i<data.http_content.length;i++){
            var http_string= new Array();
            http_string = data.http_content[i].split(",");
            $("#head_content").append("<option value="+http_string[0]+">"+http_string[0]+"  :   "+http_string[1]+"</option>");
            };

            if (data.replace_page == '1') {
                $('#replace_page')[0].checked = true;
            } else{
                $('#replace_page')[0].checked = false;
            }
        }
     
    }
    do_request(sending_data, ondatareceived);
}

function addHead(){
    
 
    var current_head = $("#head").find("option:selected").text();
    var current_desc = $("#headertxt").val();
    var current_string = current_head + "  :   " + current_desc;
    $("#head_content option").each(function(){  //遍历所有option     
          var txt = $(this).text();   //获取option值 
          if(txt==current_string){
               message_manager.show_popup_error_mesg("重复输入，请再次输入！");  //添加到数组中
               $(this).remove();  
          }
      });

    if ($("#popup_img_for_headertxt").attr('src') === '../images/error_note.png') {
        message_manager.show_popup_error_mesg('报头设置有误！')
    }else{
        $("#head").find("option:selected").each(function(){
            var desc = $("#headertxt").val();
            $("#head_content").append("<option selected value="+$(this).val()+">"+$(this).text()+"  :   "+desc+"</option>");
        });
    }

    // $("#head_content").find("option:selected").each(function(){

    // })


}
function deleteHead(){
    $("#head_content").find("option:selected").each(function(){
        $(this).remove();      
    });
}

function save_complete(){

    var array = new Array();
    $("#head_content option").each(function(){  //遍历所有option     
          var txt = $(this).text();   //获取option值 
          if(txt!=''){
               var arr_txt = txt.split(':');
               arr_txt[0] = $.trim(arr_txt[0]);
               arr_txt[1] = $.trim(arr_txt[1]);
               txt = arr_txt.join(':');
               array.push(txt);  //添加到数组中
          }
      });
    var content = array.join("&");
   
    var sending_data = {
            ACTION: 'save_complete',
            content: content,
            panel_name:'hideSite_panel',
            replace_page:$('#replace_page').is(':checked').toString()
        };
        function ondatareceived(data) {
           if (data.status != 0) {
                message_manager.show_popup_error_mesg(data.mesg);
           }
           panel.hide();
        }
        do_request(sending_data, ondatareceived);
}
function csrf_list_panel_hide() {
    $("#csdf_domain_name").val(domain)
    csrf_list_panel.hide();
}