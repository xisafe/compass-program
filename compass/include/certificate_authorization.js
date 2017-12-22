/*
 * 描述: 【IP/MAC绑定设置页面】
 * 作者: 
 * 历史：2017-9-1  ChenSisi创建
 */
 $( document ).ready(function() {

    /* 渲染面板 */
    message_manager.render();
    toggle_CA_panel.render();
    CA_list_panel.render();
    create_CA_add_panel.render();
    create_CA_add_panel.hide();

    CA_import_panel.render();
	CA_import_panel.hide();

    CA_list_panel.update_info( true );

    toggle_CA_panel.set_ass_message_manager( message_manager );
    
    $("#add_panel_add_button_id_for_create_CA_add_panel").bind("click",function(){
    	$("#create_CA_add_panel_config").slideUp("fast");
    	create_button = 0;
    })
    var wrap_input = '<form enctype="multipart/form-data" method="post" action="/cgi-bin/certificate_authorization.cgi" class="download_icon"></form>';
    $('input[name="import_item"]').wrap(wrap_input);
    $(".download_icon").append('<input type="hidden" name="ACTION" value="ca_download" style="width:0;height:0;">');
});
var create_button = 0;

var message_box_config = {
    url: "/cgi-bin/certificate_authorization.cgi",
    check_in_id: "message_box_config",
    panel_name: "message_box"
}

var toggle_CA_panel_config = {
    url: "/cgi-bin/certificate_authorization.cgi",
    check_in_id: "toggle_CA_panel_config",
    rule_title_adding_prefix: "",
    panel_name: "toggle_CA_panel",
    rule_title_adding_icon: "applications-blue.png",
    rule_title_adding_prefix: "",   // 把前缀文字置为空！
    rule_title: "生成/查看/重置CA证书",
    is_panel_closable: false,
    is_panel_stretchable: false,
    is_modal: false,   // 模态框如果设置为true的话那么这个面板初始时就是弹出来的！
    footer_buttons: {
    	add: false,
    	cancel: false
    },
    items_list: [{
        title: "生成/查看/重置CA证书",
        sub_items: [{
            enable: true,
            type: "button",
            class: "set-button",
            id: "Create_CA",
            name: "Create_CA",
            value: "生成CA证书",
            functions: {
            	onclick: "show_create_CA_panel();"
                // onclick: "handle_toggle_switch_on();"
            }
        }, {
            enable: true,
            type: "button",
            id: "Check_CA",
            name: "Check_CA",
            class: "set-button",
            value: "查看CA证书",
            functions: {
                // onclick: "toggle_switch_off();",
                onclick: "check_CA_file();"
            }
        }, {
        	enable: true,
            type: "button",
            id: "Reset_CA",
            name: "Reset_CA",
            class: "set-button",
            value: "重置CA证书",
            functions: {
                // onclick: "toggle_switch_off();",
                onclick: "reset_CA_file();"
            }
        }]
    }]
};


var create_CA_add_panel_config = {
    url: "/cgi-bin/certificate_authorization.cgi",
    check_in_id: "create_CA_add_panel_config",
    panel_name: "create_CA_add_panel",
    rule_title_adding_icon: "applications-blue.png",
    rule_title_adding_prefix: "",   // 把前缀文字置为空！
    rule_title: "生成CA证书",
    is_panel_closable: true,
    is_panel_stretchable: false,
    is_modal: false,
    modal_config: {
        modal_box_size: "m"
    },
    event_handler: {
        before_cancel_edit:function(add_obj){
        },
        after_cancel_edit:function(add_obj){
        },
        before_save_data:function( add_obj, sending_data ){
        	$("#create_CA_add_panel_config").slideUp("fast");
    		create_button = 0;
        },
        after_save_data:function( add_obj, received_data ){
        }
    },
    items_list: [{
        title: "名称",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "name",
            name: "name",
            style: "",
            functions: {

            },
            check: {
    	        type: "text",
                required: 1,
                check:'name|',
                // other_reg:'//',
                ass_check: function( check ) {
    
                }
            }
        }]
    },{
        title: "国家",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "country",
            name: "country",
            style: "",
            functions: {

            },
            check: {
            	type: "text",
            	required: 0,
            	check: 'note|',
            	ass_check: function( check ){

            	}
            }
        }]
    }, {
        title: "省份",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "province",
            name: "province",
            style: "",
            functions: {

            },
            check: {
            	type: "text",
            	required: 0,
            	check: 'note|',
            	ass_check: function( check ){

            	}
            }
        }]
    }, {
        title: "城市",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "city",
            name: "city",
            style: "",
            functions: {

            },
            check: {
            	type: "text",
            	required: 0,
            	check: 'note|',
            	ass_check: function( check ){

            	}
            }
        }]
    }, {
        title: "组织",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "organization",
            name: "organization",
            style: "",
            functions: {

            },
            check: {
            	type: "text",
            	required: 0,
            	check: 'note|',
            	ass_check: function( check ){

            	}
            }
        }]
    }, {
        title: "部门",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "department",
            name: "department",
            style: "",
            functions: {

            },
            check: {
            	type: "text",
            	required: 0,
            	check: 'note|',
            	ass_check: function( check ){

            	}
            }
        }]
    }, {
        title: "邮件",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "email",
            name: "email",
            style: "",
            functions: {

            },
            check: {
            	type: "text",
            	required: 0,
            	check: 'note|',
            	ass_check: function( check ){

            	}
            }
        }]
    }]
};

var CA_import_panel_config = {
    url: "/cgi-bin/certificate_authorization.cgi",
    check_in_id: "CA_import_panel_config",
    panel_name: "CA_import_panel",
    rule_title_adding_icon: "upload.png",
    rule_title_adding_prefix: "导入证书请求",
    is_modal: true,
    modal_config: {
        modal_box_size: "m"
    },
    event_handler: {
        before_save_data: function(add_obj, sending_data){
            // 这个接口没反应说明你点导入的时候发送的动作请求已经不是默认的save_data而很有可能是import_data，
        },
        after_save_data: function(add_obj, received_data){
        }
    },
    is_panel_closable: true,
    is_panel_stretchable: false,
    // footer_buttons: {
    //     add_btn: false,
    //     cancel_btn: true,
    //     import_btn: true   // 因为这个接口仅仅实现了发送import-data请求给后台，而没有提供onreceived接口，所以你要重写自己的实现
        /*if ( footer_buttons.import !== undefined && footer_buttons.import ) {
            panel_footer += '<input type="button" id="' + import_button_id + '" class="' + panel_control.form_button_class + '" value="' + button_import_text + '"/>';
            panel_footer += '<input type="hidden" name="ACTION"  value="import_data"/>';
            panel_footer += '<input type="hidden" name="panel_name"  value="' + panel_config.panel_name + '"/>';
        }*/
    // },
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add: false,
        cancel: false,
        import: false,
        sub_items: [                /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            {
                enable: true,
                type: "submit",
                value: "确认",
                style:"vertical-align: top;background-image: url(../images/button.jpg);background-repeat: repeat-x;border-top: 0px;border-left: 1px solid #b3e2f4;border-bottom: 1px solid #b3e2f4;border-right: 1px solid #b3e2f4;",
                id:"import_CA",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "add_CA_file();"
                }
            },{
                enable: true,
                type: "button",
                value: "取消",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "CA_import_panel.hide();"
                }
            },
            {
                enable:true,
                type:"hidden",
                name:"ACTION",
                value:"import_data"
            }
        ]
    },
    items_list: [{
        title: "导入请求文件",
        sub_items: [{
            enable: true,
            type: "file",
            style:"height:24px",
            name: "file_lib",
            id: "file_lib",
            check: {
                type: "file",
                required: 1
            }
        }]
    }
     // {
    	// title: "证书类型",
    	// sub_items:[{
    	// 	enable: true,
    	// 	type: "checkbox",
    	// 	id: "sign_CA",
    	// 	name: "sign_CA",
    	// 	label: "签名证书",
    	// 	value: "sig",
    	// }, {
    	// 	enable: true,
    	// 	type: "checkbox",
    	// 	id: "encrypt_CA",
    	// 	name: "encrypt_CA",
    	// 	label: "加密证书",
    	// 	value: "enc",
    	// }]
    ]
};
var list_panel_render = {

    'action': {
        render: function( default_rendered_text, data_item ) {
            var action_buttons = [
                {
                    enable: true,
                    id: "import_item",
                    name: "import_item",
                    button_icon: "uploadtray.png",
                    button_text: "导出",
                    style:"margin-left:-47px;margin-bottom:-23px;",
                    value: data_item.CA_ID,
                    functions: {
                        // onclick: "download_data(this.value);"
                    },
                    class: "action-image",
                },{
                    enable: true,
                    id: "show_update_log",
                    name: "show_update_log",
                    button_icon: "info.png",
                    button_text: "查看信息",
                    value: data_item.CA_ID,
                    functions: {
                        onclick: "check_info(this.value);"
                    },
                    class: "action-image", 
                }
            ];
        
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};
var CA_list_panel_config = {
    url: "/cgi-bin/certificate_authorization.cgi",
    check_in_id: "CA_list_panel_config",
    panel_name: "CA_list_panel",
    page_size: 15,   // 手动设置只让它显示5行
    is_default_search: false,
    render: list_panel_render,
    event_handler: {
        before_load_data: function( add_obj, data_item ) {

        },
        after_load_data: function ( add_obj, data_item ) {
        },
        before_save_data: function ( add_obj, sending_data ) {
        },
        after_save_data: function ( add_obj, received_data ) {
        }
    },
    panel_header: [{
        enable: true,
        type: "text",
        title: "证书ID",
        name: "CA_ID",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "证书名称",
        name: "CA_Name",
        width: "16%"
    },{
        enable: true,
        type: "text",
        title: "证书类型",
        name: "CA_Type",
        width: "6%"
    },{
        enable: true,
        type: "text",
        title: "证书格式",
        name: "CA_Form",
        width: "6%"
    },{
        enable: true,
        type: "text",
        title: "证书主题",
        name: "CA_Item",
        width: "24%"
    }, {
        enable: true,
        type: "text",
        title: "起始时间",
        name: "state_Date",
        width: "17%"
    },  {
        enable: true,
        type: "text",
        title: "到期时间",
        name: "end_Date",
        width: "17%"
    },{
        enable: true,
        type: "action",
        title: "操作",
        name: "action",
        td_class:"align-center",
        width: "9%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",  // 要加type属性，不然按钮上显示不出文字
        button_icon: "../images/stock_up-16.png",
        button_text: "导入证书请求",
        style: "width:125px;height:30px;",
        functions: {
            onclick: "show_CA_import_panel();"
        }
    }]
};



var message_manager = new MessageManager( message_box_config );
var toggle_CA_panel = new RuleAddPanel( toggle_CA_panel_config );
var create_CA_add_panel = new RuleAddPanel( create_CA_add_panel_config );

var CA_list_panel = new PagingHolder( CA_list_panel_config );
var CA_import_panel = new RuleAddPanel( CA_import_panel_config );

function do_ajax( sending_data, onreceived ) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/certificate_authorization.cgi",
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            ipmac_list_panel.show_error_mesg("返回数据格式有误,请检查");
        },
        success: onreceived
    });
}

function show_create_CA_panel() {
	if (create_button == 0) {
		$("#create_CA_add_panel_config").slideDown("fast");
		create_button = 1;
	}
	else {
		$("#create_CA_add_panel_config").slideUp("fast");
		create_button = 0;	
	}
}


function show_CA_import_panel(){
    CA_import_panel.show();
}

function add_CA_file(){
    $("#add_panel_body_form_id_for_CA_import_panel").get(0).submit();

    CA_import_panel.hide();
}

function check_CA_file() {
	var sending_data = {
		ACTION: "check_ca"
	};
	function ondatareceived(data) {
		console.log(data.detail_data.replace(/\r/g,'\n'));

		var detail_data = data.detail_data
        var line = data.detail_data.split('\n');
        var code = "";
        code = line[0]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;'+line[1]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
               +line[2]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+line[3]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;'
               +line[4]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+line[5]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
               +line[6]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+line[7]
               +'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+line[8];

		message_manager.show_details_message(code,true);
        $("#details_message_box_text_for_message_box").css('text-align','left');
        $(".popup-short-mesg-text-area").css('width','500px');
        $(".popup-short-mesg-buttons").css('width','500px');
	}
	do_request( sending_data,ondatareceived, function(){
		message_manager.show_popup_error_mesg("未知错误");
	})
}

function reset_CA_file() {
	var sending_data = {
		ACTION: "reset_ca"
	};
	function ondatareceived(data) {
		console.log(data);
		message_manager.show_note_mesg(data.mesg);
	}
	do_request( sending_data,ondatareceived, function(){
		message_manager.show_popup_error_mesg("未知错误");
	})
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/certificate_authorization.cgi",
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

function check_info(data) {
    var id = data;
    var sending_data = {
        ACTION: "check_ca_one",
        id: id
    };
    function ondatareceived(data) {
        console.log(data);
        var detail_data = data.detail_data
        var line = data.detail_data.split('\n');
        var code = "";
        code = line[0]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;'+line[1]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
               +line[2]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+line[3]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;'
               +line[4]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+line[5]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
               +line[6]+'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+line[7]
               +'<br>'+'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+line[8];

        message_manager.show_details_message(code,true);
        $("#details_message_box_text_for_message_box").css('text-align','left');
        $(".popup-short-mesg-text-area").css('width','500px');
        $(".popup-short-mesg-buttons").css('width','500px');
    }
    do_request( sending_data,ondatareceived, function(){
        message_manager.show_popup_error_mesg("未知错误");
    })

}