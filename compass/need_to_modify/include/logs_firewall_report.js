$( document ).ready(function() {

	/*渲染面板*/

	message_manager.render();

	add_panel.render();
	add_panel.hide(); //初始化，将添加面板隐藏

	/*将面板之间关联*/
	add_panel.set_ass_message_manager( message_manager );

	$("#inputDate").datepicker({
		dateFormat: "yy-mm-dd",
		yearSuffix: '年',
		monthNames: ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
		dayNamesMin: ['日','一','二','三','四','五','六'],
		onClose: function(selectedDate) {
		}
	});

    var sending_data = {
        ACTION: "load_data"
    };
    function ondatareceived(data) {
        console.log(data);
        var eths = data.eths;
        var str = '<option value="">任意</option>';
        for (var i = 0; i < eths.length; i++) {
            str = str + '<option value="' + eths[i] + '">' + eths[i] + '</option>';
        }; 
        $("#iface").html(str);
    }
    do_request( sending_data, ondatareceived, function(){
        message_manager.show_popup_error_mesg("数据错误！");
    })
});

/*定义全局变量*/
var ass_url = "/cgi-bin/logs_firewall_report.cgi";

var message_box_config = {
	url: ass_url,
	check_in_id: "mesg_box",
	panel_name: "mesg_box",
}

var add_panel_config = {
	url: ass_url,
	check_in_id: "add_panel",
	panel_name: "add_panel",
	rule_title: "报表条件设置",
	button_adding_text:"设置",
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
				style: "left:29%",
				id: "install",
                value: "设置",
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
    	title: "选择日期",
    	sub_items: [
    		{
    			enable: true,
    			type: "text",
    			style: "width:138px;",
    			id: "inputDate",
    			name: "DATE",
    			value: "",
    			readonly: "readonly",
    			functions: {

    			},
    			class: "calendar"
    		}
    	]
    }, {
        title: "排序",
        sub_items: [
            {
                enable: true,
                type: "label",
                name: "order_label_1",
                value: "按"
            }, {
                enable: true,
                type: "select",
                id: "type",
                name: "type",
                style: "width:125px;line-height:20px",
                options:
                [
                    {
                        text: "源IP前十五",
                        value: "SRC"
                    },
                    {
                        text: "目的IP前十五",
                        value: "DST"
                    }
                ]
            }, {
                enable: true,
                type: "label",
                name: "order_label_2",
                value: "排序"
            }
        ]
    }, {
        title: "选择接口",
        sub_items: [
            {
                enable: true,
                type: "select",
                id: "iface",
                name: "iface",
                style: "width:147px;line-height:20px",
                options:
                [
                    {
                        text: "任意",
                        value: " "
                    },
                    {
                        text: "eth1",
                        value: "eth1"
                    },
                    {
                        text: "eth2",
                        value: "eth2"
                    },
                    {
                        text: "br0",
                        value: "br0"
                    },
                    {
                        text: "br1",
                        value: "br1"
                    }
                ]
            }
        ]
    }, {
        title: "报表标题",
        sub_items: [
            {
                enable: true,
                type: "text",
                style: "width:143px;",
                id: "report_title",
                name: "report_title",
                value: "",
                functions: {

                },
            }
        ]
    }]
};

var add_panel = new RuleAddPanel( add_panel_config );
var message_manager = new MessageManager( message_box_config );

/*定义各项函数*/

//在list_panel里面点击查询时间，触发事件search
function install_for_report() {
	add_panel.show();
}

//在add_panel里面点击查询时间，触发事件searchTime
function searchTime() {

    $("#add_panel_body_form_id_for_add_panel").submit();
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

