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
    list_panel.render();
	list_panel_extendRender();



    list_panel.set_ass_message_manager( message_manager );

    list_panel.update_info( true );
	(function() {
		if($("#log-mesg-note").val() != ""){
			message_manager.show_popup_error_mesg("导入成功！");
		}else if($("#log-mesg-error").val() != ""){
			message_manager.show_popup_error_mesg($("#log-mesg-error").val());
		}
	})();

});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/reveal_log.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}



var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
	page_size: 20,
	default_search_config: {        /* ===可选===，只有当is_default_search为true时才生效 */
	input_tip: "仅支持英文查找",   /* ===可选===，控制搜索输入框内的提示，默认是“输入关键字以查询...” */
	title: "日志关键词"                     /* ===可选===，控制搜索输入框左边的提示，默认无提示 */
	},
	event_handler: {
        before_load_data: function( list_obj ) {
            list_obj.extend_sending_data.time = $("#log_date_input_id").val();
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 时，系统向服务器重新加载数据之前调用此函数
             *
             * 参数： -- list_obj      ==可选==，列表面板实例
             * 返回：无
             */
        },
        after_load_data: function ( list_obj, response ) {
            console.log( response );
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
            title: "时间",
            name: "datetime",
            width: "10%"
        }, {
            enable: true,
            type: "text",
            title: "事件名称",
            name: "name",
            width: "10%"
        }, {
            enable: true,
            type: "text",
            title: "源IP",
            name: "sip",
            width: "10%"
        }, {
            enable: true,
            type: "text",
            title: "目的IP",
            name: "dip",
            width: "10%"
        }, {
            enable: true,
            type: "text",
            title: "动作",
            name: "actionView",
            width: "10%"
        }, {
			enable: true,
			type: "text",
			title: "结果",
			name: "result",
			width: "10%"
		}
    ],
    top_widgets: [                          /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */

        // {
            // enable: true,
            // type: "image_button",
            // button_icon: "delete.png",
            // button_text: "删除日志",
            // functions: {
                // onclick: "deleteLog();"
            // }
        // },
		{
            enable: true,
            type: "image_button",
            button_icon: "down.png",
            button_text: "导出日志",
            functions: {
                onclick: "downLog();"
            }
        },
		{
			enable: true,
			type: "text",
			title: "时间",
			id: "log_date_input_id",
			name: "LOG_DATE_INPUT",
			style: "width:130px;height:25px;",
			functions: {
		
			}
		}
    ]
};

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
//扩展list_panel
function list_panel_extendRender() {
	var date = document.getElementById("log_date_input_id");
    var myDate = new Date();
    date.setAttribute("type","date");
    var str = myDate.toLocaleDateString();
    var strs = str.split("/");
    strs[1] = strs[1].length == 1?"0"+strs[1]:strs[1];
    strs[2] = strs[2].length == 1?"0"+strs[2]:strs[2];
    date.setAttribute("value",strs.join("-"));
    $(date).on("change",function() {
        if ( checkTime( $(date).val() ) ) {
            list_panel.show_error_mesg("非法的时间!");
            $(date).val( list_panel.logTime );
            return;
        }else {
            list_panel.logTime = $(date).val();
        }
        list_panel.update_info( true );
    });

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

//删除日志
function deleteLog() {
    var time = $("#log_date_input_id").val();     
    var sending_data = {
        ACTION: "delete_data",
        panel_name: "list_panel",
        time: time
    }
    var ondatareceived = function(data) {
        if(data.status == 0){
            list_panel.update_info(true);
        }
        message_manager.show_popup_error_mesg(data.mesg);
    }
    do_request(sending_data, ondatareceived);
}
//检测选择时间是否非法
function checkTime(str) {
    var myDate = new Date();
    var chooseTime = arrInt( str.split("-") );
    var localTime = arrInt( myDate.toLocaleDateString().split("/") );
    var flag = false;
	console.log(chooseTime, localTime);
    if ( chooseTime[0] > localTime[0] ) {
        flag = true;
    }
    else if ( chooseTime[0] == localTime[0] ) {
        if ( chooseTime[1] > localTime[1] ) {
            flag = true;
        }else if ( chooseTime[1] == localTime[1] ) {
            if ( chooseTime[2] > localTime[2] ) {
                flag = true;
            }
        }
    }
    console.log(flag);
    return flag;
    function arrInt(arr) {
        for(var i = 0; i < arr.length; i++) {
            arr[i] = parseInt(arr[i]);
        }
        return arr;
    }
}
//导出日志
function downLog() {
	var time = $("#log_date_input_id").val();     
    var sending_data = {
        ACTION: "down_log",
        panel_name: "list_panel",
        time: time
    }
    var ondatareceived = function(data) {
        if(data.status){
            message_manager.show_popup_error_mesg(data.mesg);
        }else {
			window.location.href = "https://"+window.location.host+data.path;
		}
        
    }
    do_request(sending_data, ondatareceived);
}