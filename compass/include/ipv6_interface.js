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
    list_panel.set_ass_add_panel( add_panel );

    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );

    list_panel.update_info( true );

});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/ipv6_interface.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

var add_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "IPv6地址",         /* ==*可选*==，默认是"规则" */
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
            title: "接口名称:",          /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
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
					name: "interface",
					id: "interface",
					readonly: "readonly"


       
                }
            ]
        }, {
            title: "ipv6地址",
            sub_items: [
                {
                    enable: true,
                    type: "textarea",
                    id: "addr",
                    name: "addr",
                    value: "",
					tip: "请输入ipv6地址,每行一个",
                    functions: {
                    },
                    check: {
                        type: "textarea",
                        required: 1,
                        check: 'ipv6_mask|',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        }
    ]
};

//list_panel渲染函数
var list_panel_render = {
 
    'action': {
        render: function( default_rendered_text, data_item ) {
        var action_buttons = [];
      
            action_buttons = [
                {
                    "enable": true,
                    "id": "edit_item",
                    "name": "edit_item",
                    "button_icon": "edit.png",
                    "button_text": "编辑",
					"style": "margin:0 auto", 
                    "value": data_item.id,
                    "functions": {
                        onclick: "list_panel.edit_item("+data_item.id+");"
                    },
                    "class": "",
                }
            ];
        
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
    
};

var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
	page_size:20,
	render: list_panel_render,
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
            enable: true,
            type: "text",
            title: "接口名称",
            name: "interface",
            width: "13%"
        }, {
            enable: true,
            type: "text",
            title: "IPv6地址",
            name: "addr_list",
            width: "67%"
        }, {
            enable: true,
            type: "action",
			title: "操作",
            name: "action",
            width: "20%"
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

//列表导航栏启用按钮
function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    if ( checked_items.length < 1){
    message_manager.show_popup_note_mesg("请选择一项需要启用的策略！");
    }else{
        var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].id );
        }
    
        var ids = checked_items_id.join( "&" );
    
        list_panel.enable_item( ids );
    }
}

//列表导航栏禁用按钮
function disable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    if ( checked_items.length < 1){
     message_manager.show_popup_note_mesg("请选择一项需要禁用的策略！");
    }else{
        var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].id );
        }

        var ids = checked_items_id.join( "&" );

        list_panel.disable_item( ids );
    }
}