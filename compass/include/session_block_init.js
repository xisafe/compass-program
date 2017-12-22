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
    update_data_for_list();
    
    /* 绑定时间输入*/
    //ESONCalendar.bind("time_start");
    //ESONCalendar.bind("time_end");
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/session_break.cgi",
    check_in_id: "mesg_box_break",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/session_break.cgi",
    check_in_id: "panel_block_add",
    panel_name: "add_panel",
    rule_title: "临时阻断",
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    is_modal: true,
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "协议",
        sub_items: [{
            "enable": true,
            "type": "select",
            "name": "protocol",
            "id": "protocol",
            "functions": {
                onclick: "changeAddPanel(this);"
            },
            "options": [{
                "value": "all",
                "text": "任意",
                "functions": {
                    onclick: "changeAddPanel(this);"
                }
            }, {
                "value": "tcp",
                "text": "TCP",
                "selected": true,
                "functions": {
                    onclick: "changeAddPanel(this);"
                }
            }, {
                "value": "udp",
                "text": "UDP",
                "functions": {
                    onclick: "changeAddPanel(this);"
                }
            }, {
                "value": "icmp",
                "text": "ICMP",
                "functions": {
                    onclick: "changeAddPanel(this);"
                }
            }],
            "multiple": false,
            "check": {
                'type':'select-one',
                'required':'1',
                'ass_check':function( check ){
                    
                }
            }
        }]
    }, {
        title: "源IP/子网",
        sub_items: [{
            enable: true,
            type: "text",
            tip: "（0.0.0.0/0为任意）",
            id: "source",
            name: "source",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check:'other',
                other_reg:'!/^\$/',
                ass_check: function( check ) {
                    var mesg = "";
                    var ip = $("#source").val();
                    if(!check.validsegment(ip) && !check.validip(ip) && !(ip == "0.0.0.0/0")){
                        mesg = "请填写正确的IP或子网地址";
                    }
                    return mesg;
                }
            }
        }]
    }, {
        title: "源端口/范围",
        cls: "tr_crl_sport",
        sub_items: [
            {
                enable: true,
                type: "text",
                id: "s_port",
                name: "s_port",
                value: "",
                tip: "（如:22,23-65,不填为任意）",
                functions: {
                },
                check: {
                    type: "text",
                    required: 0,
                    check: 'port|port_range|',
                    ass_check: function( check ) {

                    }
                }
            }
        ]
    },
    {
        title: "Type",
        cls:"hidden tr_crl_type",
        sub_items: [{
            enable: true,
            type: "text",
            id: "type",
            name: "type",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 0,
                check: '',
                ass_check: function( check ) {
                    if($("#type").val() != "" || $("#type").val() != null){
                        $("#add_panel_add_button_id_for_add_panel").attr("disabled",false);
                    }
                }
            }
        }]
    }, {
        title: "目的IP/子网",
        sub_items: [{
            enable: true,
            type: "text",
            tip: "（0.0.0.0/0为任意）",
            id: "dest",
            name: "dest",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check:'other',
                other_reg:'!/^\$/',
                ass_check: function( check ) {
                    var mesg = "";
                    var ip = $("#dest").val();
                    if(!check.validsegment(ip) && !check.validip(ip) && !(ip == "0.0.0.0/0")){
                        mesg = "请填写正确的IP或子网地址";
                    }
                    return mesg;
                }
            }
        }]
    }, {
        title: "目的端口/范围",
        cls: "tr_crl_dport",
        sub_items: [{
            enable: true,
            type: "text",
            id: "d_port",
            name: "d_port",
            value: "",
            tip: "（如:22,23-65,不填为任意）",
            check: {
                type: "text",
                required: 0,
                check: 'port|port_range|',
                ass_check: function( check ) {

                }
            }
        }]
    }, {
        title: "Code",
        cls:"hidden tr_crl_code",
        sub_items: [{
            enable: true,
            type: "text",
            id: "code",
            name: "code",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 0,
                check: 'num|',
                ass_check: function( check ) {
                    if($("#code").val() != "" && $("#code").val() != null){
                        if($("#type").val() == "" || $("#type").val() == null){
                            add_panel_config.items_list[3].sub_items[0].check.required = 1;
                            $("#add_panel_add_button_id_for_add_panel").attr("disabled",true);
                            return "选填了code就一定要选填type!";
                        }
                    }else{
                        $("#add_panel_add_button_id_for_add_panel").attr("disabled",false);
                    }
                }
            }
        }]
    }, {
        title: "阻断时间",
        sub_items: [{
            enable: true,
            type: "text",
            id: "left_time",
            name: "left_time",
            value: "",
            tip: "（1-43200分钟）",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check: 'num|',
                ass_check: function( check ) {
                    var time = $("#left_time").val();
                    if(time > 43200){
                        return "不能大于43200";
                    }
                }
            }
        }]
    }]
};

var list_panel_render = {
    'protocol': {
        render: function( default_rendered_text, data_item ) {
            if(data_item.id > (data_item.config_num-1)){
                return '<span style="color:#AAAAAA">' + default_rendered_text + '</span>';
            }else{
                return '<span>' + default_rendered_text + '</span>';
            }
        }
    },
    'source': {
        render: function( default_rendered_text, data_item ) {
            if(data_item.id > (data_item.config_num-1)){
                return '<span style="color:#AAAAAA">' + default_rendered_text + '</span>';
            }else{
                return '<span>' + default_rendered_text + '</span>';
            }
        }
    },
    's_port': {
        render: function( default_rendered_text, data_item ) {
            var temp_arr = default_rendered_text.split("&");
            var result_render = temp_arr.join(" ")
            if(data_item.id > (data_item.config_num-1)){
                return '<span style="color:#AAAAAA">' + result_render + '</span>';
            }else{
                return '<span>' + result_render + '</span>';
            }
        }
    },
    'dest': {
        render: function( default_rendered_text, data_item ) {
            if(data_item.id > (data_item.config_num-1)){
                return '<span style="color:#AAAAAA">' + default_rendered_text + '</span>';
            }else{
                return '<span>' + default_rendered_text + '</span>';
            }
        }
    },
    'd_port': {
        render: function( default_rendered_text, data_item ) {
            var temp_arr = default_rendered_text.split("&");
            var result_render = temp_arr.join(" ")
            if(data_item.id > (data_item.config_num-1)){
                return '<span style="color:#AAAAAA">' + result_render + '</span>';
            }else{
                return '<span>' + result_render + '</span>';
            }
        }
    },
    'left_time': {
        render: function( default_rendered_text, data_item ) {
            if(data_item.id > (data_item.config_num-1)){
                return '<span style="color:#AAAAAA">' + default_rendered_text + '</span>';
            }else{
                return '<span>' + default_rendered_text + '</span>';
            }
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
        var action_buttons = [
                {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "value": data_item.id,
                    "functions": {
                        onclick: "delete_selected_items(this);"
                    }
                }
            ];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/session_break.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_block",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [{
        "enable": true,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //用户装载数据之用
        "td_class": "align-center",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "10%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
        "functions": {              //一般只有checkbox才会有这个字段
        }
    }, {
        "enable": false,
        "type": "radio",
        "name": "radio",
        "column_cls": "rule-listbc",
        "width": "5%"
    }, {
        "enable": true,
        "type": "text",
        "title": "协议",        //一般text类型需要title,不然列表没有标题
        "name": "protocol",
        "td_class": "align-center",
        "width": "10%"
    }, {
        "enable": true,
        "type": "text",
        "title": "源",
        "name": "source",
        "td_class": "align-center",
        "width": "16%"
    }, {
        "enable": true,
        "type": "text",
        "title": "源端口（Type）",
        "name": "s_port",
        "td_class": "align-center",
        "width": "16%"
    }, {
        "enable": true,
        "type": "text",
        "title": "目的",
        "name": "dest",
        "td_class": "align-center",
        "width": "16%"
    }, {
        "enable": true,
        "type": "text",
        "title": "目的端口（Code）",
        "name": "d_port",
        "td_class": "align-center",
        "width": "16%"
    }, {
        "enable": true,
        "type": "text",
        "title": "剩余时间（分钟）",
        "name": "left_time",
        "td_class": "align-center",
        "width": "11%"
    }, {
        "enable": true,
        "type": "action",
        "title": "活动/动作",
        "name": "action",
        "td_class": "align-center",
        "width": "8%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        button_icon: "add16x16.png",
        button_text: "添加规则",
        functions: {
            onclick: "add_rule(this);"
        }
    }, {
        "enable": false,             // ==可选==，如果为不填或者为false,就不显示
        "id": "enable_selected",    // ==可选==，按钮的ID
        "name": "enable_selected",  // ==可选==，按钮的名字
        "button_icon": "on.png",    // ==可选==，操作按钮的图标，如果没有设置，就没有图标
        "button_text": "启用选中",  // **必填**，操作按钮的文字，这个必须设置,建议在五个字以内
        "functions": {              // ==可选==，回调函数，没有的话就只是一个按钮，什么也不做
            onclick: "test_test_test(this)"
        }
    }, {
        "enable": false,
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
    }, {
        "enable": true,
        type: "image_button",
        "id": "delete_used",
        "name": "delete_used",
        "button_icon": "delete.png",
        "button_text": "删除过期规则",
        "functions": {
            onclick: "delete_used_items()"
        }
    }],
    bottom_widgets: [{
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
    }],
    is_default_search: false
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
        if (checked_items.length === 0) {
            message_manager.show_popup_note_mesg('请选择要删除的规则')
            return
        }
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

//切换添加面板形式
function changeAddPanel(e){
    if(e.value == "tcp" || e.value == "udp"){
        $(".tr_crl_sport").show();
        $(".tr_crl_dport").show();
        $(".tr_crl_type").hide();
        $(".tr_crl_code").hide();
        add_panel_config.items_list[2].sub_items[0].check.required = 0;
        add_panel_config.items_list[5].sub_items[0].check.required = 0;
    }else if(e.value == "icmp"){
        $(".tr_crl_sport").hide();
        $(".tr_crl_dport").hide();
        $(".tr_crl_type").show();
        $(".tr_crl_code").show();
    }else{
        $(".tr_crl_sport").hide();
        $(".tr_crl_dport").hide();
        $(".tr_crl_type").hide();
        $(".tr_crl_code").hide();
    }
}

function add_rule( element ) {
    add_panel.show();
}

//自动刷新数据，时间间隔每分钟刷新一次
function update_data_for_list(){
    list_panel.update_info(true);
    window.setTimeout("update_data_for_list()",60000);
}

//删除所有过时规则
function delete_used_items(){
    var sending_data = {
        ACTION: 'delete_used'
    };
    function ondatareceived(data) {
        message_manager.show_popup_note_mesg(data.mesg);
        list_panel.update_info(true);
    }
    list_panel.request_for_json( sending_data, ondatareceived );
}
