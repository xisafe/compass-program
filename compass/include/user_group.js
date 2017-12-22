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
	$("#groupid").attr("hidden",true);
    add_panel.hide();
	
	add_group_panel.render();
	add_group_panel.hide();
    list_panel.render();
	get_init_data_tree();//渲染左侧列表


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
var group_show = null;
var groupShowData = new Object();
var ass_url = "/cgi-bin/user_group.cgi";


var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

var add_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "用户",         /* ==*可选*==，默认是"规则" */
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
            title: "用户名",          /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
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
            title: "老化时间",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "outtime",
                    name: "outtime",
                    value: "",
                    functions: {
                    },
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
					type: "text",
					id: "groupid",
					name:"groupid"
				}
            ]
        }
    ]
};

//list_panel渲染函数
var list_panel_render = {
 
    'action': {
        render: function( default_rendered_text, data_item ) {

            action_buttons = [
                {
                    "enable": true,
                    "id": "edit_item",
                    "name": "edit_item",
                    "button_icon": "edit.png",
                    "button_text": "编辑",
                    "value": data_item.id,
                    "functions": {
                        onclick: "list_panel.edit_item("+data_item.id+");"
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
                        onclick: "delete_selected_items2(this);"
                    },
                    "class": "action-image",
                }

            ];
        
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
    
};

var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,
	panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
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
			 search_hide();
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
            name: "checkbox",       /* **必填**，作用于整列，控制整列要显示的数据项
                                                    ****当type为checkbox、radio、action之一时，name也必须对应为三项中的一项
                                                    如果要渲染每列数据，到“配置对象”（注释<1>）的render属性中去配置与当前name值
                                                一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                                第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                    */
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
            },
            "td_class":"align-center"
        }, {
            enable: true,
            type: "用户名",
            title: "名称",
            name: "name",
            width: "40%"
        }, {
            enable: true,
            type: "text",
            title: "老化时间",
            name: "outtime",
            width: "45%"
        }, {
            enable: true,
            type: "action",
            name: "action",
            width: "10%",
            "td_class":"align-center"
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

//添加用户组页面
var add_group_panel_config = {
	    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_group_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_group_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "用户组",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "m",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add: false,
        cancel: false,
        import: false,
        sub_items: [                /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            {
                enable: true,
                type: "button",
                value: "确认",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "add_group();"
                }
            },{
                enable: true,
                type: "button",
                value: "取消",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "add_group_panel.cancel_edit_box();"
                }
            }
        ]
    },
    items_list: [                   /* ***必填***，确定面板中有哪些规则，不填什么都没有 */
        {
            title: "用户组名称",          /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
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
                    name: "group_name",/* **必填**，字段的名字 */
                    id: "add_groupname",
					value: "",              /* ==可选==，字段默认值 */
                    functions: {            /* ==可选==，DOM标准事件都可生效 */
                    },
                    check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                        type: "text",       /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                        required: 1,        /* **必填**，1表示必填，0表示字段可为空 */
                        check: 'note|',     /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
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
            title: "用户组描述",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "add_groupdescription",
                    name: "description",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'note|',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        }
    ]
}


var add_panel = new RuleAddPanel( add_panel_config );
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );
var add_group_panel = new RuleAddPanel( add_group_panel_config );


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
function delete_selected_items2(e) {
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

function add_rule( element ) {
    if(group_show == null) {
		message_manager.show_popup_error_mesg("请选择一个用户组");
		return;
	}
	$("#groupid").val( groupShowData.groupid );
	add_panel.show();

}


	



//控制左侧列表的显示
function show_or_none(e) {
	var $list = $(e).parent("div").next("ul");
	if($list.css("display") == "none") 
	{	
		$list.slideDown();
		$(e).removeAttr("class");
		$(e).attr("class","downArrow");
	}else{
		$list.slideUp();
		$(e).removeAttr("class");
		$(e).attr("class","rightArrow");
	}

	
}

//根据按钮刷新右侧列表
function show_list(e) {
	var groupid = groupShowData.groupid;
	$("input#search_key_for_list_panel").val(groupid);
	$("button#search_button_for_list_panel").click();
	
	
 
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

//用户组添加事件
function add_group() {
	if( !add_group_panel.is_input_data_correct() ) {
		message_manager.show_popup_error_mesg("请正确填写各字段");
		return;
	}

	if( groupShowData.edit ) {
		edit_group();
	}else {
		var str1;
		if( group_show == null ) {
			str1 = 0;
		}else{
			str1 = groupShowData.groupid;
		}
		var str2 = $("#add_groupname").val();
		var str3 = $("#add_groupdescription").val();
		var sending_data = {
			ACTION: "add_group",
			groupid: str1, 
			name: str2,
			description: str3
			
		};
		function ondatareceived(data) {
			add_tree(data);
			add_group_panel.cancel_edit_box();		
		}
		do_request(sending_data,ondatareceived);
	}

}

//用户组删除事件
function delete_group() {

	var str1 = groupShowData.groupid;
	var sending_data = {
        ACTION: "delete_group",
		groupid: str1, 
		
    };
	function ondatareceived(data) {
		delete_tree();
		group_show = null;
		groupShowData = {};
	}
	do_request(sending_data,ondatareceived);

}

//用户组编辑事件
function edit_group() {

	var str1 = groupShowData.groupid;
	var str2 = $("#add_groupname").val();
	var str3 = $("#add_groupdescription").val();
	var sending_data = {
        ACTION: "edit_group",
		groupid: str1, 
		name: str2,
		description: str3
		
    };
	function ondatareceived(data) {
		edit_tree(data);
		update_groupShowData();
		add_group_panel.cancel_edit_box();		
	}
	do_request(sending_data,ondatareceived);

}


//改变用户当前选择的用户组样式
function choose_css(e) {
	$(group_show).css("background-color","#e6eff8");
	group_show = e;
	update_groupShowData();
	$(group_show).css("background-color","#8ebff2");
}

//获得用户当前选择的用户组数据
function update_groupShowData() {
	groupShowData.group_name = $(group_show).contents().filter(function() {
				return this.nodeType === 3;
			}).text(); 
	groupShowData.description = $(group_show).find("span:nth-child(4)").text();
	groupShowData.groupid = $(group_show).find("span:nth-child(3)").text();
	
}

//隐藏搜索栏
function search_hide() {
	$("#search_key_for_list_panel").hide();
	$("#search_button_for_list_panel").hide();
	
}

//新建用户时将groupid写到请求参数中
function add_groupid() {
	$("#groupid").val($(group_show).children("span").text()); 
}


//获取原始树形数据
function get_init_data_tree(){
    var sending_data = {
        ACTION: "get_tree"
    };

    function ondatareceived(data) {
		var direc = new Array();
		direc[0] = data;
		if( data == null ) {
			return;
		}
        set_tree(direc,document.getElementById("user_group"),1);
    }
    do_request(sending_data, ondatareceived);
}

/*
//递归处理树形数据
function contrust_tree_data(data){
    var children_nodes = [];
    for(var i=0; i< data.length; i++){
        var node = {
            id: data[i].admin_id,
            text: data[i].admin_name,
            //type: !(data[i].children_admin)?"file":"default",
            type: "default",
            asset_name: data[i].admin_name,
            description: data[i].admin_description,
            children: !(data[i].children_admin)?[]:contrust_tree_data(data[i].children_admin)
        };
        if(!data[i].children_admin && data[i].children_admin != null){
            children_nodes.push(node);
        }else{
            if(data[i].admin_level == 1){
                tree_nodes.push(node);
            }else{
                children_nodes.push(node);
            }
        }
    }
    return children_nodes;
}
*/

//生成树形列表
function set_tree(childrenlist,farthernode,level) {

	
	for(var i = 0; i < childrenlist.length; i++) {
		
		var childrenlist_in = new Array();
		childrenlist_in = childrenlist[i].children;
		
		var li = document.createElement("li");

		var para = document.createElement("div");
		para.setAttribute("style","cursor:pointer;");
		$(para).css("height","30px");
		$(para).css("line-height","30px");
		$(para).css("padding-left",level*15);
		para.setAttribute("onclick","choose_css(this);show_list(this);");
		
		var span = document.createElement("span");//存放ID
		span.setAttribute("style","display:none");
		var groupid = document.createTextNode(childrenlist[i].groupid);
		span.appendChild(groupid);
		
		var spanDescription = document.createElement("span");//存放描述
		spanDescription.setAttribute("hidden","hidden");
		var description = document.createTextNode(childrenlist[i].groupdescribe);
		spanDescription.appendChild(description);
		
		var log = document.createElement("div");//创建组名前的箭头
		if(childrenlist_in != null && childrenlist_in.length != 0){
			log.setAttribute("class","rightArrow");
			log.setAttribute("onclick","show_or_none(this);");
		}else{
			log.setAttribute("class","noArrow");
		}
		
		var img = document.createElement("img");
		img.setAttribute("src","../images/user_group.png");
		$(img).css( {"width":"12px","margin-right":"3px"} );


		
		
		var ul = document.createElement("ul");
		ul.setAttribute("style","display:none;");
		
		var text_node = document.createTextNode(childrenlist[i].groupname);
		

		
		para.appendChild(log);
		para.appendChild(img);
		para.appendChild(text_node);
		para.appendChild(span);
		para.appendChild(spanDescription);
		if(childrenlist_in != null) {
			set_tree(childrenlist_in,ul,level+1);
		};
		li.appendChild(para);
		li.appendChild(ul);
		farthernode.appendChild(li);

	}
	
}

//添加树形列表
function add_tree(data) {
	var li = document.createElement("li");
	
	var para = document.createElement("div");
	var level = ( parseInt($(group_show).css("padding-left"))/15 ) + 1;
	para.setAttribute("style","cursor:pointer;");
	$(para).css("height","30px");
	$(para).css("line-height","30px");
	$(para).css("padding-left",level*15);
	para.setAttribute("onclick","choose_css(this);show_list(this);");
		
	var span =document.createElement("span");//存放ID
	span.setAttribute("style","display:none");
	var groupid = document.createTextNode(data.groupid);
	span.appendChild(groupid);
	
	var spanDescription = document.createElement("span");//存放描述
	spanDescription.setAttribute("hidden","hidden");
	var description = document.createTextNode(data.description);
	spanDescription.appendChild(description);
		
	var log = document.createElement("div");
	log.setAttribute("class","noArrow");
	
	var img = document.createElement("img");
	img.setAttribute("src","../images/user_group.png");
	$(img).css("width","12px");
	$(img).css("margin-right","3px");

		
	var ul = document.createElement("ul");
	ul.setAttribute("style","display:none;");
		
	var text_node = document.createTextNode(data.name);
		
	
	para.appendChild(log);
	para.appendChild(img);
	para.appendChild(text_node);
	para.appendChild(span);
	para.appendChild(spanDescription);
	li.appendChild(para);
	li.appendChild(ul);

    if ($("#user_group li").length!=0) {
        $(group_show).next("ul").get(0).appendChild(li);
        if($(group_show).children("div").css("width") != "0px") {
            $(group_show).children("div").get(0).setAttribute("class","rightArrow");
            $(group_show).children("div").get(0).setAttribute("onclick","show_or_none(this);");
        };
    } else {
       document.getElementById('user_group').appendChild(li); 
    }
		


}

//删除树形列表
function delete_tree() {
	
	
	if($(group_show).parent('li').siblings('li').length == 0) {
		var temp = $(group_show).parent("li").parent("ul").prev("div").children("div").get(0);
		temp.setAttribute("class","noArrow");
		temp.setAttribute("onclick","");
	}
	$(group_show).parent('li').remove();
	



}

//编辑树形列表
function edit_tree(data) {
	$(group_show).contents().filter(function() {
				return this.nodeType === 3;
			})[0].data = data.name;
	$(group_show).find("span:nth-child(4)").text(data.description);

}



//用户组添加事件前奏
function add_group_rule() {
	if(group_show == null) {
		if( $("#user_group > li").length == 0 ) {
			
		}else {
			alert("请选择一个用户组");
			return;
		}
	}
	groupShowData.edit = 0;
	add_group_panel.show();
}

//用户组删除事件前奏
function delete_group_rule() {
	if(group_show == null){
		alert("请选择需要删除的用户组");
		return;
	}
	var str = $(group_show).contents().filter(function() {
				return this.nodeType === 3;
			}).text();
	if( confirm("确认删除" + str + "组吗？" ) ) {
		delete_group();
		}
}

//用户组编辑事件前奏
function edit_group_rule() {
	if(group_show == null) {
		alert("请选择需要编辑的用户组");
		return;
	}
	groupShowData.edit = 1;
	add_group_panel.load_data_into_add_panel(groupShowData);
	
}