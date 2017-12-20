$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    add_panel.render();
    list_panel.render();
	list_panel_expendRender();
	load_select();
    message_manager.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    add_panel.hide();
	list_panel.update_info(true);
    $("#search_key_for_list_panel").css("font-size","5px");
    $("#search_key_for_list_panel").attr("placeholder","支持规则名称查询");

	
    
});
var ass_url = "/cgi-bin/web_features.cgi";
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/web_features.cgi",
    check_in_id: "mesg_box_url",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/web_features.cgi",
    check_in_id: "panel_url_add",
    panel_name: "add_panel",
    rule_title: "URL分类库",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
            
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "名称*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    tip: "（最多10个字符）",
                    id: "name",
                    name: "name",
                    check: {
                        type: "text",
                        required: 1,
                        check:'name|',
                        ass_check:function(eve){
                            var name = $("#name").val();
                            if(name.length > 20){
                                return "最多输入10个字符！";
                            }
                        }
                    }
                }
            ]
        }, {
            title: "说明*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    tip: "（最多30个字符）",
                    id: "description",
                    name: "description",
                    check: {
                        type: "text",
                        required: 1,
                        check:'other',
                        other_reg:'!/^\$/',
                        ass_check:function(eve){
                            var content = $("#description").val();
                            if(content.length > 30){
                                return "最多输入30个字符！";
                            }
                        }
                    }
                }
            ]
        }, {
            title: "URL地址*",
            sub_items: [
                {
                    enable: true,
                    type: "textarea",
                    tip: "（每行一个）",
                    id: "urls",
                    name: "urls",
                    check: {
                        type: "textarea",
                        required: 1,
                        check:'domain|'
                    }
                }
            ]
        }
    ]
};

var list_panel_render = {
   

    'action': {
        render: function( default_rendered_text, data_item ) {
            
            var enable = data_item.enable;
			var status = data_item.status;
            var toggle_class, button_text, button_icon, onclick, statusIcon, statusOnclick, statusText;
            
            if( enable == "off"){
                button_icon = "off.png";
				button_text = "启用";
                onclick = "change_status('on','','"+data_item.index+"')";
            }
            else{
                button_icon = "on.png";
				button_text = "禁用";
                onclick = "change_status('off','','"+data_item.index+"')";
            }
			if( status == "drop") {
				statusIcon = "drop.png";
				statusText = "检测";
				statusOnclick = "change_status('','alert','"+data_item.index+"')";
			}
			else {
				statusIcon = "alert.png";
				statusText = "阻断";
				statusOnclick = "change_status('','drop','"+data_item.index+"')";
			}
            var toggle_enable_button = {
                enable: true,
                button_icon: button_icon,
                value: data_item.index,
				button_text: button_text,
                functions: { 
                    onclick: onclick,
                },
                class:"action-image"
            };
			var toggle_status_button = {
				enable: true,
				button_icon: statusIcon,
				value: data_item.index,
				button_text: statusText,
				functions: { 
                    onclick: statusOnclick,
                },
                class:"action-image"
			};
			
            

            // var render_edit_button = PagingHolder.create_action_buttons( [edit_button] );
            var toggle_enable_button = PagingHolder.create_action_buttons( [toggle_enable_button,toggle_status_button] );
            var action_buttons = toggle_enable_button;
            return action_buttons;
        }
    }

};

var list_panel_config = {
    url: "/cgi-bin/web_features.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_url_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_default_search: true,
	is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
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
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            },
            "td_class":"align-center"
        }, {
            "enable": true,
            "title":"规则ID号",
            "type": "text",
            "name": "index",
            "td_class":"align-center",
            "width": "10%"
        }, {
            "enable": true,
            "type": "text",
            "title": "规则名称",
            "name": "name",
            "width": "56%"
        },{
            "enable": true,
            "type": "text",
            "title": "类型",
            "name": "type",
            "td_class":"align-center",
            "width": "12%"
        },{
            "enable": true,
            "type": "text",
            "title": "危险等级",
            "name": "level",
            "width": "7%",
            "td_class":"align-center"
        },  {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "10%",
            "td_class":"align-center"
        }
    ],
    top_widgets: [                  /* ===可选=== */

        {
            enable: true,
            type: "image_button",
            id: "enable_selected",
            name: "enable_selected",
            class: "",
            button_icon: "on.png",
            button_text: "启用",
            functions: {
                onclick: "change_status('on','','');"
            }
        }, {
            enable: true,
            type: "image_button",
            id: "disable_selected",
            name: "disable_selected",
            class: "",
            button_icon: "off.png",
            button_text: "禁用",
            functions: {
                onclick: "change_status('off','','');"
            }
        },{
            enable: true,
            type: "image_button",
            id: "alert_selected",
            name: "alert_selected",
            class: "",
            button_icon: "alert.png",
            button_text: "检测",
            functions: {
                onclick: "change_status('','alert','');"
            }
        },{
            enable: true,
            type: "image_button",
            id: "drop_selected",
            name: "drop_selected",
            class: "",
            button_icon: "drop.png",
            button_text: "阻断",
            functions: {
                onclick: "change_status('','drop','');"
            }
        },{
            enable: true,
            type: "image_button",
            id: "alertAll",
            button_text: "全部检测",
            functions: {
                onclick: "change_status('','alert','ALL');"
            }
        },{
            enable: true,
            type: "image_button",
            id: "dropAll",
            button_text: "全部阻断",
            functions: {
                onclick: "change_status('','drop','ALL');"
            }
        },
        {
            enable: true,
            type: "image_button",
            id: "onAll",
            button_text: "全部启用",
            functions: {
                onclick: "change_status('on','','ALL');"
            }
        },
        {
            enable: true,
            type: "image_button",
            id: "offAll",
            button_text: "全部禁用",
            functions: {
                onclick: "change_status('off','','ALL');"
            }
        }
    ],
    extend_search: [                /* ===可选===，定义额外的搜索筛选条件，位置在面板右上角，控件类似top_widgets中控件 */
        {
            enable: true,               /* ==可选==，如果为不填或者为false,就不显示*/
            type: "select",             /* ==可选==，默认为text类型 */
            id: "select_rule",  /* ==可选==，控件ID */
            name: "select_rule",/* **必填**，控件的名字 */
            title: "筛选",          /* **必填**，输入控件前面的提示信息，没有会导致用户迷糊 */
            class: "",                  /* ==可选==，控件本身样式的类名，会覆盖默认类的属性 */
            multiple: false,            /* ==可选==，select组件特有 */
            functions: {
                onchange: "$(search_button_for_list_panel).click();",
            }
        } 
    ],
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
	}
}

function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_panel.enable_item( ids );
}

function disable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_panel.disable_item( ids );
}

function delete_selected_items(e) {
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

function extend_search_function( element ) {
    list_panel.update_info( true );
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
        async: false,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//获取list_panel数据
function load_listdata() {

	var sending_data = {
        ACTION: "load_listdata"
		
    };
	function ondatareceived(data) {
		
		list_panel.detail_data = data.detail_data;
		list_panel.status = data.status;
		list_panel.error_mesg = data.error_mesg;
		list_panel.page_size = 20;
		list_panel.total_num = data.total_num;
		list_panel.update_info();
		load_select();
		

	}
	do_request( sending_data,ondatareceived );

}

//读取list_panel top部分的select标签数据
function load_select() {

    var sending_data = {
        ACTION: "load_select"
    }

    function ondatareceived( data ) {
        str = '<option value="0" selected>所有</option>';
        for(var i = 0; i < data.rules_data.length; i++ ){
			str += '<option value="'+data.rules_data[i].id +'">'+data.rules_data[i].name+'</option>';    
        }
        $("#select_rule").html('');
        $("#select_rule").append(str);

    }

    do_request( sending_data, ondatareceived );

}
//启用禁用
function change_status(e1,e2,e3) {

	var check_items = list_panel.get_checked_items();
	var length = check_items.length;
	var str = "";
	if(e3 == ""){
		if(check_items.length == 0) {
    		alert("请选择需要操作的规则");
    		return;
		}
		for (var i = 0; i < length-1; i++ ) {
			str += check_items[i].index + "&";
		}
		str += check_items[length-1].index;
	}else if(e3 == "ALL") {
		var allData = list_panel.detail_data;
        var allIndex = new Array();
        for(var i = 0; i < allData.length; i++) {
            allIndex.push(allData[i].index);
        }
        str = allIndex.join("&");
	}else {
        str = e3;
    }
	
	var sending_data = {
        ACTION: "change_enable",
		enable_action: e1,
		action: e2,
		ruleIds: str
		
    };
	function ondatareceived(data) {
        message_manager.show_note_mesg(data.mesg);
        if (data.reload == 1) {
            message_manager.show_apply_mesg('规则已改变，需要重新应用以使规则生效');            
        }
		list_panel.update_info(true);
		for_title();

		

	}
	do_request( sending_data,ondatareceived );
	
}
//为TITLE赋值
function for_title() {
	var $tds = $(".rule-list #rule_listb_for_list_panel  td:nth-child(3)");
	for(var i=0; i < $tds.length; i++) {
		$tds.eq(i).attr("title",$tds.eq(i).text());
	}
}
//list_panel额外渲染函数
function list_panel_expendRender() {
	$("#first_page_icon_for_list_panel").click(function(){for_title();});
	$("#last_page_icon_for_list_panel").click(function(){for_title();});
	$("#next_page_icon_for_list_panel").click(function(){for_title();});
	$("#end_page_icon_for_list_panel").click(function(){for_title();});
	$("#refresh_icon_for_list_panel").click(function(){for_title();});
	$("current_page_for_list_panel").keydown(function(){for_title();});
}