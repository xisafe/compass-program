$( document ).ready(function() {

    /* 渲染面板 */
    message_manager.render();
    list_panel.render();
	list_panel_expendRender();
	classfication_panel();
	edit_panel.render();
	edit_panel.hide();



    /* 设置面板关联 */
    // add_panel.set_ass_list_panel( list_panel );
    // list_panel.set_ass_add_panel( add_panel );

    edit_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );

});

var ass_url = "/cgi-bin/application_feature_rec_library.cgi";
var appgroup_show = null;//确定当前所选择的应用组

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box"          /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

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
                    "value": data_item.id,
                    "functions": {
                        onclick: "edit_data(" + data_item.appid + ");"
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
    page_size: 20, 
	check_in_id: "table_list",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，以区别不同面板 */
    render: list_panel_render,
    default_search_config: {
        input_tip: "支持应用名称关键字查询",
        title: ""
    },
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
                                            一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                            第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                 */
        td_class: "align-center",                /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
        class: "",         /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                             当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                             在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                 */
        width: "5%",            /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                             以精确控制你想要的宽度
                                 */
        functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            // onclick: "alert(this.value);"
        }
    }, {
        enable: true,
        type: "text",
        title: "应用名称",
        name: "name",
        width: "45%"
    }, {
        enable: false,
        type: "text",
        title: "描述",
        name: "description",
        width: "60%"
    }, {
		enable: true,
		type: "text",
		title: "规则启用状态",
		name: "appStatus",
		width: "40%"
	}, {
        enable: true,
        type: "action",
		title: "操作",
        name: "action",
        td_class:"align-center",
        width: "10%"
    }],
    top_widgets: [{                     /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */
        enable: true,                   /* =*可选*=，如果为不填或者为false,就不创建 */
        type: "image_button",           /* =*可选*=，目前支持类型有text,password,file,select,checkbox,radio,textarea,
                                                    label,button和image_button,最常用的是image_button，并且目前考虑得
                                                    比较多其他组件比较弱，但能勉强使用，如果其他需求很强，需要进一步
                                                    扩展
                                         */
        button_icon: "on.png",    /* ==可选==，image_button的图标，如果没有设置，就没有图标，image_button独有字段 */
        button_text: "启用",        /* **必填**，image_button的文字，这个必须设置,建议在五个字以内，image_button独有字段 */
        functions: {                    /* ==可选==，回调函数，没有的话就只是一个按钮，什么也不做 */
            onclick: "enable_selected_items();"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "off.png",
        button_text: "禁用",
        functions: {
            onclick: "disable_selected_items();"
        }
    }],
	extend_search: [{
        "enable": true,         // ==可选==，如果为不填或者为false,就不显示
        "type": "select",         // ==可选==，默认为text类型
        "id": "condition",     // ==可选==，控件ID
        "name": "condition",   // **必填**，控件的名字
        "title": "筛选：",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        "options": [
		{
            "value":"all",
            "text":"所有"
        },	
		{
            "value":"on",
            "text":"启用"
        },
        {   "value":"off",
            "text":"禁用"
		}],
		functions: {
			onchange: "appgroup_click();"
		}
	}]
    
};

//编辑规则配置面板
var edit_panel_render = {
   /*'protocol': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "RIP";
            return '<span>' + result_render + '</span>';
        },
    },*/ 
    enable: {
        render: function(a,b) {
            var msg = ""
            if(a == "1") {
                msg = "启用";
            }else {
                msg = "禁用";
            }
            return msg;
        }
    }
    
};

var edit_panel_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "edit_panel",         // ***必填***，确定面板挂载在哪里 
    page_size: 10,                  //===可选===，定义页大小，默认是15 
    panel_name: "edit_panel",       // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "识别规则",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    render: edit_panel_render,      //===可选===，渲染每列数据 
    panel_header: [                 // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",           //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "class": "",                //元素的class
            "td_class": "align-center",             //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "20%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
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
            "title": "规则名称",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "50%"
        }, {
            "enable": true,
            "type": "text",
            "title": "状态",
            "name": "enable",
            "width": "30%"
        }
    ],    
	top_widgets: [{                     /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */
        enable: true,                   /* =*可选*=，如果为不填或者为false,就不创建 */
        type: "image_button",           /* =*可选*=，目前支持类型有text,password,file,select,checkbox,radio,textarea,
                                                    label,button和image_button,最常用的是image_button，并且目前考虑得
                                                    比较多其他组件比较弱，但能勉强使用，如果其他需求很强，需要进一步
                                                    扩展
                                         */
        button_icon: "on.png",    /* ==可选==，image_button的图标，如果没有设置，就没有图标，image_button独有字段 */
        button_text: "启用",        /* **必填**，image_button的文字，这个必须设置,建议在五个字以内，image_button独有字段 */
        functions: {                    /* ==可选==，回调函数，没有的话就只是一个按钮，什么也不做 */
            onclick: "on_rule();"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "off.png",
        button_text: "禁用",
        functions: {
            onclick: "off_rule();"
        }
    }],
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
                button_text: "保存",
                functions: {
                    onclick: "save_rule();"
                }
            }, {
                enable: true,
                type: "image_button",
                class: "",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "edit_panel.hide();"
                }
            }
        ]
    }
}



var list_panel = new PagingHolder( list_panel_config );
var edit_panel = new PagingHolder( edit_panel_config );
var message_manager = new MessageManager( message_box_config );

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

//生成应用分类列表
function classfication_panel() {
	classfication_data();
}

//获得应用分类列表数据
function classfication_data() {

	var sending_data = {
        ACTION: "load_classfication",

		    };
	function ondatareceived(data) {
		$("#cont_title b:nth-child(1)").text(data.total_number);
		$("#cont_title b:nth-child(2)").text(data.total_number_rule);
		classfication_gettree(data);
	}
	do_request(sending_data,ondatareceived);

}

//生成应用分类列表树
function classfication_gettree(data) {
	var detaildata = data.detail_data;
	var length = detaildata.length;
	for( var i=1; i<length; i++ ){ 	
		var li = '<li class="application_group" onclick="change_appgroup(this);">' + detaildata[i].name +'( '+ detaildata[i].number +' )<span style="display:none">' + detaildata[i].appgroupId + '</span></li>';
		$("#cont_menu_ul").append(li);
	}
	
}

//根据用户点选的应用组改变样式
function change_appgroup(e) {
	$(appgroup_show).attr("class","application_group");
	appgroup_show = e;
	$(appgroup_show).attr("class","application_group_change");
    var value = "具体应用（" +$(appgroup_show).text().split("(")[0] + "）";
    $("#cur_app").text(value);
	appgroup_click();
}

//点击应用组按钮显示具体的应用
function appgroup_click() {
	
	var id = $(appgroup_show).find("span").text();
	var selectVal = $("#condition").val();
	var search = $("#search_key_for_list_panel").val();
	var sending_data = {

        ACTION: "load_application",
		appgroupid: id,
		selectVal: selectVal,
		search: search
	};
	function ondatareceived(data) {
		list_panel.detail_data = data.detail_data;
		list_panel.status = data.status;
		list_panel.error_mesg = data.error_mesg;
		list_panel.total_num = data.total_num;
		list_panel.page_size = 20;
		list_panel.search = data.search;
		list_panel.update_info();
		for_title();

		
	}
	do_request(sending_data,ondatareceived);
}

//获得编辑页面数据并加载 
function edit_data(e) {
	var sending_data = {

        ACTION: "load_rule",
		appid: e
	};
	function ondatareceived(data) {
		console.log(data);
		edit_panel.detail_data = data.detail_data;
		edit_panel.status = data.status;
		edit_panel.error_mesg = data.error_mesg;
		edit_panel.reload = data.reload;
		edit_panel.total_num = data.total_num;
        if(data.page_size && data.page_size > 10) {
            edit_panel.refresh_list_panel(data);    
        }else {
            data.page_size = 10;
            edit_panel.refresh_list_panel(data);
        }
		edit_panel.update_info();
		edit_panel.show();
		
	}
	do_request(sending_data,ondatareceived);
}

//编辑页面启用功能
function on_rule() {
	var checked_items = edit_panel.get_checked_items();
	var str = "";
	var length = checked_items.length;
	if(!checked_items[0]) {
		message_manager.show_popup_error_mesg("请选择需要启用的规则");
	}else{
    	for(var i = 0; i < length; i++) {
    		checked_items[i].enable = "1";
    		edit_panel.update_info();
    	}
   
	}
}

//编辑页面禁用功能
function off_rule() {
	var checked_items = edit_panel.get_checked_items();
	var str = "";
	var length = checked_items.length;
	if(!checked_items[0]) {
		message_manager.show_popup_error_mesg("请选择需要禁用的规则");
	}else{
		for(var i = 0; i < length; i++) {
			checked_items[i].enable = "0";
			edit_panel.update_info();
		}
		
	}
}

//编辑页面保存按钮触发事件
function save_rule() {
	var data = new Object();
	data.detaildata = edit_panel.detail_data;
	var jsonData = JSON.stringify(data);
	

	var sending_data = {
		
		ACTION: "edit_rule",
		jsonData: jsonData 	
	};
	function ondatareceived(data) {
		
		edit_panel.hide();
        appgroup_click();
		
	}
	do_request(sending_data,ondatareceived);
	
}

//列表导航栏启用按钮
function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    if ( checked_items.length < 1){
    message_manager.show_popup_note_mesg("请选择一项需要启用的策略！");
    }else{
        var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].rowNumber );
        }
    
        var ids = checked_items_id.join( "&" );
		
    
        list_panel.enable_item( ids );
		appgroup_click();
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
            checked_items_id.push( checked_items[i].rowNumber );
        }

        var ids = checked_items_id.join( "&" );
        
        list_panel.disable_item( ids );
		appgroup_click();
    }
}
//list_panel的额外渲染
function list_panel_expendRender() {
	$("#search_button_for_list_panel").unbind("click");
	$("#search_button_for_list_panel").click(function() {
		appgroup_click();
	});

}
//为TITLE赋值
function for_title() {
	var $tds = $(".rule-list #rule_listb_for_list_panel  td:nth-child(3)");
	for(var i=0; i < $tds.length; i++) {
		$tds.eq(i).attr("title",$tds.eq(i).text());
	}
}





