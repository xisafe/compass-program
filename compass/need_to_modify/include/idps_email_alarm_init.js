var check_sender = new ChinArk_forms();
var object1 = {
   'form_name':'SENDER_SETTING_FORM',
   'option':{
        'SENDER_EMAILADDRESS':{
            'type':'text',
            'required':'1',
            'check':'mail|'
        },
        'SMTPSERVER_ADDR':{
            'type':'text',
            'required':'1',
            'check':'ip|domain|'
        },
        'SMTPSERVER_PORT':{
            'type':'text',
            'required':'1',
            'check':'port|'
        },
        'TESTED_RECIVER_EMAILADDRESS':{
            'type':'text',
            'required':'0',
            'check':'mail|'
        }
    }
};

//启用身份认证时表单检测
var object2 = {
   'form_name':'SENDER_SETTING_FORM',
   'option':{
        'SENDER_EMAILADDRESS':{
            'type':'text',
            'required':'1',
            'check':'mail|'
        },
        'SMTPSERVER_ADDR':{
            'type':'text',
            'required':'1',
            'check':'ip|domain|'
        },
        'SMTPSERVER_PORT':{
            'type':'text',
            'required':'1',
            'check':'port|'
        },
        'TESTED_RECIVER_EMAILADDRESS':{
            'type':'text',
            'required':'0',
            'check':'mail|'
        },
        'USERNAME':{
            'type':'text',
            'required':'1',
            'check':'mail|'
        },
        'PASSWD':{
            'type':'text',
            'required':'1',
            'check':'',
            'ass_check':function(eve){
                var msg="";
                var viewsize = eve._getCURElementsByName("PWD","input","SENDER_SETTING_FORM")[0].value;
                if (viewsize.length < 1 || viewsize > 20) {
                    msg = "请输入1-20个字符";
                }
                return msg;
            }
        }
    }
};

function changeFormCheck(){
    if($("#AUTH").attr("checked")){
        $("#ACCOUNT").attr("disabled",false);
        $("#PWD").attr("disabled",false);
        check_sender._main(object2);
    }else{
        $("#ACCOUNT").attr("disabled","disabled");
        $("#PWD").attr("disabled","disabled");
        check_sender._main(object1);
    }
}

$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    /* 渲染面板 */
    add_panel.render();
    list_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    
    add_panel.hide();
    list_panel.update_info(true);
    
    check_sender._main(object1);
    changeFormCheck();
});

var message_box_config = {
    url: "/cgi-bin/idps_email_alarm.cgi",
    check_in_id: "panel_email_mesg",
    panel_name: "my_message_box"
}

var message_manager;
var list_panel;
var add_panel;
var add_panel_config = {
    url: "/cgi-bin/idps_email_alarm.cgi",
    check_in_id: "panel_email_add",
    panel_name: "add_panel",
    rule_title: "收件人",
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    is_modal: true,
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "收件人邮箱*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "reciever",
                    name: "reciever",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'mail|',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        }, {
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
        }, {
            title: "启用",
            sub_items: [
                {
                    enable: true,
                    type: "checkbox",
                    id: "enable",
                    label: "启用收件人",
                    name: "enable",
                    value: "",
                    functions: {
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
    url: "/cgi-bin/idps_email_alarm.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_email_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持收件人、说明关键字查询",
        title: ""
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "td_class": "align-center",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的td-class是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
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
            "title": "收件人",
            "name": "reciever",
            "width": "40%"
        }, {
            "enable": true,
            "type": "text",
            "title": "说明",
            "name": "description",
            "width": "40%"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "td_class":"align-center",
            "name": "action",
            "width": "10%"
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            button_icon: "add16x16.png",
            type: "image_button",
            button_text: "新建",
            functions: {
                onclick: "add_rule(this);"
            }
        }, {
            "enable": true,             // ==可选==，如果为不填或者为false,就不显示
            "id": "enable_selected",    // ==可选==，按钮的ID
            type: "image_button",
            "name": "enable_selected",  // ==可选==，按钮的名字
            "button_icon": "on.png",    // ==可选==，操作按钮的图标，如果没有设置，就没有图标
            "button_text": "启用选中",  // **必填**，操作按钮的文字，这个必须设置,建议在五个字以内
            "functions": {              // ==可选==，回调函数，没有的话就只是一个按钮，什么也不做
                onclick: "enable_selected_items(this)"
            }
        }, {
            "enable": true,
            "id": "disable_selected",
            type: "image_button",
            "name": "disable_selected",
            "button_icon": "off.png",
            "button_text": "禁用选中",
            "functions": {
                onclick: "disable_selected_items(this)"
            }
        }, {
            "enable": true,
            "id": "delete_selected",
            type: "image_button",
            "name": "delete_selected",
            "button_icon": "delete.png",
            "button_text": "删除选中",
            "functions": {
                onclick: "delete_selected_items(this)"
            }
        }
    ],
    bottom_buttons: [               /* ===可选=== */
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
    is_default_search: true           /* ===可选===，默认是true，控制默认的搜索条件 */
    
}

function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }
    if(checked_items_id.length == 0){
        alert("请勾选配置项！");
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

//邮件发送测试
function sending_mail_test(){
    var contents = $(".send");
    var data_sender = [];
    for(var i=0;i<contents.length;i++){
        if(contents[i].value == ""){
            alert("请先完善发件人信息后再测试");
            return;
        }
        data_sender.push(contents[i].value);
    }
    if($("#ENCODE_SSL").get(0).checked){
        data_sender.push($("#ENCODE_SSL").val());
    }else{
        data_sender.push("off");
    }
    if($("#AUTH").get(0).checked){
        data_sender.push($("#AUTH").val());
        var authes = $(".auth");
        for(var i=0;i<authes.length;i++){
            data_sender.push(authes[i].value);
            if(authes[i].value == ""){
                alert("请先完善发件人身份认证信息后再测试");
                return;
            }
        }
    }else{
        data_sender.push("off");
        data_sender.push("");
        data_sender.push("");
    }
    //验证邮箱格式是否正确
    var re = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
    if(!(re.test(data_sender[3]))){
        message_manager.show_popup_error_mesg("邮件接收地址格式不正确！");
        return;
    }
    var sending_data = {
        ACTION: "sending_mail_test",
        SENDER_EMAILADDRESS: data_sender[0],
        SMTPSERVER_ADDR: data_sender[1],
        SMTPSERVER_PORT: data_sender[2],
        TESTED_RECIVER_EMAILADDRESS: data_sender[3],
        ENABLED_SSL: data_sender[5],
        ENABLED_AUTH: data_sender[6],
        USERNAME: data_sender[7],
        PASSWD: data_sender[8]
    }

    function ondatareceived( data ) {
        var sending_state = data.sending_state.replace("\n","");
        if(sending_state == "yes"){
            message_manager.show_popup_note_mesg("邮件已发送，请到收件人邮箱查看是否发送成功。");
        }else{
            var error_mesg = "";
            if(sending_state != "" && sending_state != null){
                var temp = sending_state.split(",");
                error_mesg = temp[1];
            }
            message_manager.show_popup_error_mesg("邮件发送失败。"+error_mesg);
        }
    }
    list_panel.request_for_json( sending_data, ondatareceived );
}
//显示添加面板
function add_rule( element ) {
    add_panel.show();
}
