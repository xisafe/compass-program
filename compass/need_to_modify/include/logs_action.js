$( document ).ready(function() {

	/*渲染面板*/

	message_manager.render();
	list_panel.render();

	add_panel.render();
	add_panel.hide();  //初始化，将添加面板隐藏

    importLog_panel.render();
    importLog_panel.hide();


    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    importLog_panel.set_ass_message_manager( message_manager ) 



    list_panel.set_ass_message_manager( message_manager );

    list_panel.update_info( true );

    import_panel_extendrender();
    (function() {
        var img = $('<img title="重置" src="/images/reconnect.png">');
        img.css({
            cursor: "pointer",
            position: "relative"
        });
        img.on("click", function() {
            clear_add_panel_text();
        })
        $("#add_panel_id_for_add_panel .add-panel-title").find("span").css('float','left');
        $("#add_panel_id_for_add_panel .add-panel-title").find("span").after(img);
    })();
	$("#time_check").datepicker({
		dateFormat: "yy-mm-dd",
		yearSuffix: '年',
		monthNames: ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
		dayNamesMin: ['日','一','二','三','四','五','六'],
		onClose: function(selectedDate) {
		}
	});
});

/*定义全局变量*/
var ass_url = "/cgi-bin/logs_action.cgi";
var search_date = '';

var message_box_config = {
	url: ass_url,
	check_in_id: "mesg_box",
	panel_name: "mesg_box",
}

var importLog_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "importLog_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "importLog_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "导入日志",
    rule_title_adding_prefix: "",
    rule_title_adding_icon:"uploadtray.png",
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 1             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons:{
        add:false,
        sub_items:[
            {
                enable: true,
                type: "hidden",
                name: "ACTION",
                value: "importLog",

            },
            {
                enable: true,
                type: "hidden",
                name: "importLog_panel",
                value: "",

            },
            {
                enable: true,
                type: "submit",
                style: "",
                id: "submit_for_log",
                functions: {
                    onclick:"importLog();"
                },

            }
        ],
        cancel: true,
    },
    event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function( add_obj, data_item ) {

        },
        after_load_data: function( add_obj, data_item ) {

        },
        before_cancel_edit: function( add_obj ) {

        },
        after_cancel_edit: function( add_obj ) {

        },
        before_save_data: function( add_obj, sending_data ) {

        },
        after_save_data: function( add_obj, received_data ) {

        }
    },
    items_list: [ 
            {
            title: "选择日志文件",
            sub_items: [
                {
                    enable: true,
                    type: "file",
                    id:"upload_file",
                    name: "upload_file",
                    functions: {
                        onclick: ""
                    },
                    style:"width:300px;height:25px;border-radius:4px"
                }
                
            ]
        }]
};


var add_panel_config = {
	url: ass_url,
	check_in_id: "add_panel",
	panel_name: "add_panel",
	rule_title: "筛选条件",
	button_adding_text:"筛选",
	rule_title_adding_prefix: "",
	rule_title_adding_icon: "searchlog.png",
	is_panel_closable: true,
	is_panel_stretchable: false,
	is_modal: true,
	modal_config: {
		modal_box_size: "s",
		modal_level: 10
	},
	footer_buttons: {
		sub_items: [
			{
				enable: true,
				type: "button",
				style: "",
				id: "search",
				name: "search",
				value: "筛选",
				functions: {
					onclick: "searchTime();"
				},
			},
		],
		cancel: true,
	},
	event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function( add_obj, data_item ) {
            
        },
        after_load_data: function( add_obj, data_item ) {

        },
        before_cancel_edit: function( add_obj ) {

        },
        after_cancel_edit: function( add_obj ) {

        },
        before_save_data: function( add_obj, sending_data ) {

        },
        after_save_data: function( add_obj, received_data ) {

        }
    },
    items_list: [{
    	title: "查询日期",
    	sub_items: [
    		{
    			enable: true,
    			type: "text",
    			style: "width:190px;",
    			id: "time_check",
    			name: "time_check",
    			value: "",
    			readonly: "readonly",
    			functions: {

    			},
    			class: "calendar"
    		}
    	]
    }]
};

var list_panel_config = {
	url: ass_url,
	check_in_id: "list_panel",
	panel_name: "list_panel",

	page_size: 20,
	is_default_search: false,
	event_handler: {
        before_load_data: function( list_obj ) {

        },
        after_load_data: function ( list_obj, response ) {

        },
    },
    panel_header: [
    	{
    		enable: true,
    		type: "text",
    		title: "时间",
    		name: "datetime",
    		width: "30%"
    	}, {
    		enable: true,
    		type: "text",
    		title: "消息",
    		name: "messages",
    		width: "70%"
    	}
    ],
    top_widgets: [
        {
            enable: true,
            type: "image_button",
            button_icon: "searchlog.png",
            button_text: "查询条件",
            functions: {
                onclick: "search(this);"
            }
        },{
            enable: true,
            type: "image_button",
            button_icon: "../images/download.png",
            button_text: "导入日志",
            functions: {
                onclick: "show_importLog(this);"
            }
        },{
            enable: true,
            id: "export_log",
            name: "export_log",
            type: "image_button",
            button_icon: "../images/upload.png",
            button_text: "导出日志",
            functions: {
            
            }
        },{
            enable: true,
            id: "deleteLog",
            name: "deleteLog",
            type: "link_button",
            button_icon: "delete.png",
            button_text: "删除日志",
            functions: {
                onclick: "deleteLog();"
            }
        },{
            enable: true,
            id: "clearLog",
            name: "clearLog",
            type: "link_button",
            // href: "/cgi-bin/logs_firewall.cgi?ACTION=clearLog",
            button_icon: "delete.png",
            button_text: "清空日志",
            functions: {
                onclick: "clearLog();"
            }
        }
    ]

};
var add_panel = new RuleAddPanel( add_panel_config );
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );
var importLog_panel = new RuleAddPanel( importLog_panel_config );

//在list_panel里面点击查询时间，触发事件search
function search( element ) {

    
	add_panel.show();
}

function show_importLog( element ) {
    importLog_panel.show();
}

function importLog() {
    
    var upload_file=$('#upload_file').val();
    var bin_reg = /.dat$/;
    if (upload_file=='') {
        alert('请选择文件');
    } 
    // else if(bin_reg.test(file_lib)==false){
    //     show_popup_alert_mesg('文件格式错误');
    // }
    else{
        importLog_panel.hide();
        // show_waiting_mesg("上传中...");
        add_panel_body_form_id_for_importLog_panel.submit();
    }
}

function deleteLog() {
    var sending_data = {
        ACTION: "delete",
        searchTime: search_date
    };
    function ondatareceived(data) {
        warning_box(data.filestr,search_date);
    }
    do_request( sending_data,ondatareceived, function() {
        message_manager.show_popup_error_mesg("数据错误！");
    })
}
function clearLog() {
    var sending_data = {
        ACTION: "clearLog"
    };
    function ondatareceived(data) {
        var date = '所有';
        warning_box(data.filestr,date);
        // warning_box(data.filestr);
    }
    do_request( sending_data,ondatareceived, function() {
        message_manager.show_popup_error_mesg("数据错误！");
    })
}

//在add_panel里面点击查询时间，触发事件searchTime
function searchTime() {
    if ($('#export_log')) {
        $("#export_log").attr('value',$('#time_check').val());
        
    };
    search_date = $("#time_check").val();
    var searchTime = $("#time_check").val();
    var sending_data = {
        ACTION: "search_log",
        search: searchTime
    }
    function ondatareceived(data){

        // message_manager.show_popup_mesg("查询成功");
        list_panel.detail_data=data.detail_data;
        list_panel.total_num = data.total_num;
        list_panel.update_info();

    }
    
    do_request(sending_data, ondatareceived);

	add_panel.hide();
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

function import_panel_extendrender(argument) {

    $("#export_log").append('<input type="hidden" name="ACTION" value="download" style="width:0;height:0;">')
    .wrap('<form enctype="multipart/form-data" method="post" action="/cgi-bin/logs_action.cgi" style="display:inline-block"></form>');
}

function clear_add_panel_text() {
    $("#time_check").val('');

}

