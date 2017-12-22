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
    add_panel.render();
    add_panel.hide();
    list_panel.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    addPanelExtendRender();
    list_panel.set_ass_add_panel( add_panel );

    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );

    list_panel.update_info( true );

});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/virtual_twine.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

var add_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "虚拟网线",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "m",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
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
            var twine = new Object();
            twine.one = $("#twineOne").val();
            twine.two = $("#twineTwo").val();

            if(twine.one == '请选择网线接口') {
                return falseFun("请选择虚拟网线接口一!");
            }
            if(twine.two == '请选择网线接口') {
                return falseFun("请选择虚拟网线接口二!");
            }
            if(twine.one == twine.two) {
                return falseFun("请不要选择相同的虚拟网线接口!");
            }

            function falseFun(mesg) {
                list_panel.show_error_mesg(mesg);
                return false;
            }
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
    items_list: [                   /* ***必填***，确定面板中有哪些规则，不填什么都没有 */
        {
            title: "名称*",          /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
            id: "name_tr",          /* ==可选==，整行的id */
            name: "",               /* ==可选==，整行的name */
            class: "",              /* ==可选==，整行的class */
            functions: {            /* ==可选==，整行相应事件的回调函数，DOM标准事件都可生效 */
                // onmouseover: "alert('hover on name line');",
                // onclick: "alert('click on name line');",
            },
            sub_items: [            /* **必填**，确定此行有哪些字段，不填什么都没有 */
                {
                    enable: true,           /* **必填**，如果为不填或者为false,就不创建 */
                    type: "text",           /* ==可选==，默认是text类型，支持text,password,button,file,select,checkbox,
                                                         radio,textarea,label,items_group
                                             */
                    name: "name",           /* **必填**，字段的名字 */
                    value: "",              /* ==可选==，字段默认值 */
                    functions: {            /* ==可选==，DOM标准事件都可生效 */
                    },
                    check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                        type: "text",       /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                        required: 1,        /* **必填**，1表示必填，0表示字段可为空 */
                        check: 'name|',     /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
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
                }
            ]
        }, {
            title: "虚拟网线接口一*",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "twineOne",
                    name: "twineOne",
                    value: "",
                    functions: {
                    }
                }
            ]
        }, {
            title: "虚拟网线接口二*",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "twineTwo",
                    name: "twineTwo",
                    value: "",
                    functions: {
                    }
                }
            ]
        }, {
            title: "描述*",
            sub_items: [
                {
                    enable: true,
                    type: "textarea",
                    id: "description",
                    name: "description",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "textarea",
                        required: 1,
                        check: 'note|',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        }, {
            title: "启用",
            sub_items: [
                {
                    enable: true,
                    type: "checkbox",
                    id: "enable",
                    name: "enable",
                    text: "启用",
                    label: "启用",
                    checked: true

                }
            ]
        },
    ]
};

var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 20,
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
        },
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
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
            name: "checkbox",        /**必填**，作用于整列，控制整列要显示的数据项
                                                    ****当type为checkbox、radio、action之一时，name也必须对应为三项中的一项
                                                    如果要渲染每列数据，到“配置对象”（注释<1>）的render属性中去配置与当前name值
                                                一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                                第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                    
            class: "",              /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
            td_class: "",           /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                                 当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                                 在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                     */
            width: "5%",            /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                                 以精确控制你想要的宽度
                                     */
            functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
                // onclick: "alert(this.value);",
            }
        }, 
        {
            enable: true,
            type: "text",
            title: "名称",
            name: "name",
            width: "10%"
        }, 
        {
            enable: true,
            type: "text",
            title: "虚拟网线接口一",
            name: "twineOne",
            width: "15%"
        },
        {
            enable: true,
            type: "text",
            title: "虚拟网线接口二",
            name: "twineTwo",
            width: "15%"
        },
        {
            enable: true,
            type: "text",
            title: "描述",
            name: "description",
            width: "45%"
        },
        {
            enable: true,     
            type: "action",   
            title: "操作",
            name: "action",
            width: "10%"
        }
    ],
    top_widgets: [                          /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */
        {
            enable: true,                   /* =*可选*=，如果为不填或者为false,就不创建 */
            type: "image_button",           /* =*可选*=，目前支持类型有text,password,file,select,checkbox,radio,textarea,
                                                        label,button和image_button,最常用的是image_button，并且目前考虑得
                                                        比较多其他组件比较弱，但能勉强使用，如果其他需求很强，需要进一步
                                                        扩展
                                             */
            button_icon: "add16x16.png",    /* ==可选==，image_button的图标，如果没有设置，就没有图标，image_button独有字段 */
            button_text: "新建",        /* **必填**，image_button的文字，这个必须设置,建议在五个字以内，image_button独有字段 */
            functions: {                    /* ==可选==，回调函数，没有的话就只是一个按钮，什么也不做 */
                onclick: "add_rule(this);"
            }
        },
        {
            enable: true,
            type: "image_button",
            button_icon: "delete.png",
            button_text: "删除",
            functions: {
                onclick: "delete_selected_items(this);"
            }
        }
    ]
};


var add_panel = new RuleAddPanel( add_panel_config );
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );

function delete_selected_items( element ) {
    var checked_items = list_panel.get_checked_items();

    if ( checked_items.length == 0 ) {
        list_panel.show_error_mesg( "请选择要删除的规则" );
        return;
    }
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_panel.delete_item( ids );
}

function add_rule( element ) {
    add_panel.show();
}

//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: ass_url,
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

//获得虚拟网线接口数据
function getInterface() {
    var sending_data = {
        ACTION: "getInterface"
    };
    var ondatareceived = function(data) {
        addInterface('twineOne', data);
        addInterface('twineTwo', data);
    }
    do_request(sending_data, ondatareceived);

}

//将虚拟网线接口数据插入select
function addInterface(id, data) {
    data = eval(data.interface);
    var str = '<option selected="selected" hidden="hidden">请选择网线接口</option>';
    for(var i = 0; i < data.length; i++){
        str += '<option>' + data[i] + '</option>';
    }
    $('#' + id).append(str);
}
//add_panel额外渲染
function addPanelExtendRender() {
    getInterface();
}