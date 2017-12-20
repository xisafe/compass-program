$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    //tip_panel = new RuleAddPanel( tip_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    /* 渲染面板 */
    add_panel.render();
    //tip_panel.render();
    list_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    
    add_panel.hide();
    //tip_panel.hide();
    
    list_panel.update_info(true);
    show_state_SMScat();
    check_sender._main(object);
});
var check_sender = new ChinArk_forms();
var object = {
   'form_name':'SMS_SETTING_FORM',
   'option':{
        'receiver_test':{
            'type':'text',
            'required':'1',
            'check':'other',
            'other_reg':'!/^\$/',
            'ass_check':function(eve){
                var phone_num = $("#receiver_test").val();
                var re =  /^1\d{10}$/;
                var msg = "";
                if(!(re.test(phone_num))){
                    msg = "请填写正确的手机号码";
                }
                return msg;
            }
        }
    }
};


var list_panel;
var add_panel;
var tip_panel;
var message_box_config = {
    url: "/cgi-bin/idps_sms_alarm.cgi",
    check_in_id: "panel_sms_message",
    panel_name: "my_message_box"
}
var message_manager;
var is_can_sending = true;
var add_panel_config = {
    url: "/cgi-bin/idps_sms_alarm.cgi",
    check_in_id: "panel_sms_add",
    panel_name: "add_panel",
    rule_title: "短信告警设置",
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    is_modal: true,
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "收信人手机号码*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "tel_reciever",
                    name: "tel_reciever",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'other',
                        other_reg: '!/^\$/',
                        ass_check: function( check ) {
                            var msg = "";
                            var tel = $("#tel_reciever").val();
                            var reg = /^1\d{10}$/;
                            if(!reg.test(tel)){
                                msg = "请输入正确的手机号码";
                            }
                            return msg;
                        }
                    }
                }
            ]
        },
        {
            title: "说明",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "description",
                    name: "description",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 0,
                        check: 'note|',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "启用",
            sub_items: [
                {
                    enable: true,
                    type: "checkbox",
                    id: "enable",
                    name: "enable",
                    checked: true,
                    value: ""
                }
            ]
        }
    ]
};

var tip_panel_config = {
    url: "/cgi-bin/idps_sms_alarm.cgi",
    check_in_id: "panel_sms_tip",
    panel_name: "tip_panel",
    is_rule_title_icon: false,
    rule_title: "发送短信测试",
    footer_buttons: {
        add_btn: false,
        cancel_btn: false,
        import_btn: false,
        sub_items: [
            {
                enable: true,
                type: "button",
                value: "发送",
                functions: {
                    onclick: "sending_test();"
                }
            }
        ]
    },
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    is_modal: true,
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "短信猫状态",
            sub_items: [
                {
                    enable: true,
                    type: "label",
                    id: "state_smscat",
                    name: "state_smscat",
                    value: ""
                }
            ]
        },
        {
            title: "收件人号码*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "receiver_test",
                    name: "receiver_test",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'other',
                        other_reg: '!/^\$/',
                        ass_check: function( check ) {
                            var msg = "";
                            var tel = $("#receiver_test").val();
                            var reg = /^1\d{10}$/;
                            if(!reg.test(tel)){
                                msg = "请输入正确的手机号码";
                            }
                            return msg;
                        }
                    }
                }
            ]
        }
    ]
};

var list_panel_render = {
    'enable': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "禁用";
            if(data_item.enable == "on"){
                result_render = "启用";
            }
            return '<span>' + result_render + '</span>';
        }
    }
    
};


var list_panel_config = {
    url: "/cgi-bin/idps_sms_alarm.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_sms_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "td_class": "align-center",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": false,
            "type": "radio",
            "name": "radio",
            "td_class": "",
            "width": "5%"
        }, {
            "enable": true,
            "type": "text",
            "title": "收信人手机号码",
            "name": "tel_reciever",
            "width": "30%"
        }, {
            "enable": true,
            "type": "text",
            "title": "说明",
            "name": "description",
            "width": "50%"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "td_class":"align-center",
            "width": "10%"
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "新建",
            functions: {
                onclick: "add_rule(this);"
            }
        },
        {
            enable: false,
            type: "image_button",
            button_text: "发送测试短信",
            functions: {
                onclick: "show_tip('this');"
            }
        },
        {
            "enable": true,             // ==可选==，如果为不填或者为false,就不显示
            type: "image_button",
            "id": "enable_selected",    // ==可选==，按钮的ID
            "name": "enable_selected",  // ==可选==，按钮的名字
            "button_icon": "on.png",    // ==可选==，操作按钮的图标，如果没有设置，就没有图标
            "button_text": "启用选中",  // **必填**，操作按钮的文字，这个必须设置,建议在五个字以内
            "functions": {              // ==可选==，回调函数，没有的话就只是一个按钮，什么也不做
                onclick: "enable_selected_items(this)"
            }
        }, {
            "enable": true,
            type: "image_button",
            "id": "disable_selected",
            "name": "disable_selected",
            "button_icon": "off.png",
            "button_text": "禁用选中",
            "functions": {
                onclick: "disable_selected_items(this)"
            }
        }, {
            "enable": true,
            type: "image_button",
            "id": "delete_selected",
            "name": "delete_selected",
            "button_icon": "delete.png",
            "button_text": "删除选中",
            "functions": {
                onclick: "delete_selected_items(this)"
            }
        }
    ],
    bottom_widgets: [               /* ===可选=== */
        {
            "enable": false,
            "id": "export_selected",
            "name": "export_selected",
            "button_icon": "download.png",
            "button_text": "导出选中",
            "functions": {
                onclick: "export_selected_items(this)"
            }
        }, {
            "enable": false,
            "id": "delete_all_logs",
            "name": "delete_all_logs",
            "button_icon": "delete.png",
            "button_text": "清空日志",
            "functions": {
                onclick: "delete_all_logs(this)"
            }
        }
    ],
    is_default_search: false
    
}

function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }
    if(checked_items_id.length == 0){
        alert("请勾选联动配置项！");
        return;
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
    if(checked_items_id.length == 0){
        alert("请勾选联动配置项！");
        return;
    }

    var ids = checked_items_id.join( "&" );

    list_panel.disable_item( ids );
}

function delete_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_panel.delete_item( ids );
}

function extend_search_function( element ) {
    list_panel.update_info( true );
}

//显示添加面板
function add_rule( element ) {
    add_panel.show();
}
function show_tip( element ) {
    show_state_SMScat();
    tip_panel.show();
}
//发送短信测试函数
function sending_test(){
    var receiver_test = $("#receiver_test").val();
    var sending_data = {
        ACTION: "sending_sms",
        receiver_test: receiver_test
    };
    function ondatareceived(data) {
        //tip_panel.hide();
        var sending_state = data.state_sending.replace("\n","");
        if(sending_state == "yes"){
            message_manager.show_popup_note_mesg("短信已发送，请到收信人手机上查看是否发送成功。");
        }else{
            var error_mesg = "";
            if(sending_state != "" && sending_state != null){
                error_mesg = (sending_state.split(","))[1];
            }
            message_manager.show_popup_error_mesg("信息发送失败。"+error_mesg);
        }
        
    }
    list_panel.request_for_json(sending_data, ondatareceived);
    /* if(is_can_sending){
        list_panel.request_for_json(sending_data, ondatareceived);
    }else{
        alert("短信猫工作状态不正常！");
    } */
}
//显示短信猫工作状态
function show_state_SMScat(){
    var sending_data = {
        ACTION: "check_state_SMScat"
    };
    function ondatareceived(data) {
        var state_SMScat = data.state_cat;
        state_SMScat = state_SMScat.replace("\n","");
        if(state_SMScat == ""){
            state_SMScat = "工作异常";
        }
        if(state_SMScat == "工作正常"){
            //is_can_sending = false;
            $("#state_smscat").html("<span style='color:black'>"+state_SMScat+"</span>");
        }else{
            $("#state_smscat").html("<span style='color:red'>"+state_SMScat+"</span>");
        }
        
    }
    list_panel.request_for_json(sending_data, ondatareceived);
}