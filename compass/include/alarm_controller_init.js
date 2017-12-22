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
    list_panel.hide();
    list_panel.update_info(true);
    $(".toolbar").css("text-align","center");
});
var is_checked = "";
var detail_data_auto_confirm = "";
var detail_data = "";
var confirm_id;
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/center.cgi",
    check_in_id: "mesg_box_alarm",
    panel_name: "my_message_alarm"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/center.cgi",
    check_in_id: "panel_detail",
    panel_name: "detail_panel",
    is_rule_title_icon: false,
    rule_title_adding_prefix: "",
    footer_buttons: {
        sub_items: [
            {
                enable: true,
                type: "button",
                id: "btn_confirm",
                name: "btn_confirm",
                value: "确认",
                functions: {
                    onclick: "do_confirm_detail();"
                }
            }
        ]
    },
    rule_title: "报警信息",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 20
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
            title: "报警主题",
            sub_items: [
                {
                    enable: true,
                    type: "label",
                    id: "theme_display",
                    name: "theme",
                    value: "",
                    functions: {
                    },
                    check: {
                        
                    }
                }
            ]
        },
        {
            title: "报警类型",
            sub_items: [
                {
                    enable: true,
                    type: "label",
                    id: "type_display",
                    name: "type",
                    value: "",
                    functions: {
                    },
                    check: {
                        
                    }
                }
            ]
        },
        {
            title: "报警时间",
            sub_items: [
                {
                    enable: true,
                    type: "label",
                    id: "time_display",
                    name: "time",
                    value: "",
                    functions: {
                    },
                    check: {
                        
                    }
                }
            ]
        },
        {
            title: "报警内容",
            sub_items: [
                {
                    enable: true,
                    type: "label",
                    id: "content_display",
                    name: "content",
                    value: "",
                    functions: {
                    },
                    check: {
                        
                    }
                }
            ]
        },
        {
            title: "自动确认相同事件",
            sub_items: [
                {
                    enable:true,
                    type:"items_group",
                    item_style:"width:100%",
                    sub_items:[
                        {
                            enable: true,
                            type: "checkbox",
                            item_style: "width:100%",
                            id: "enable_same",
                            name: "enable_same",
                            label: "启用自动确认相同事件",
                            value: "",
                            functions: {
                                onclick: "change_input_state(this);"
                            }
                        },
                        {
                            enable: true,
                            type: "text",
                            item_style: "width:100%",
                            id: "num_event",
                            name: "num_event",
                            label: "调整为基线事件，并配置基线事件（1-10000）为",
                            tip: "（条/小时）",
                            value: "",
                            check: {
                                type: "text",
                                required: 1,
                                check: 'num|',
                                ass_check: function( check ) {
                                    var val_event = $("#num_event").val();
                                    var mesg = "";
                                    if(val_event > 10000){
                                        mesg = "请填写1-10000之间的整数";
                                    }
                                    return mesg;
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
    ]
};

var list_panel_render = {
    'theme': {
        render: function( default_rendered_text, data_item ) {
            //var result_render = "";
            return '<span><a style="text-decoration:underline;" href="javascript:void(0)" onclick="show_detail_panel('+data_item.id+','+data_item.item_id+');">' + default_rendered_text + '</a></span>';
        }
    }
    
};


var list_panel_config = {
    url: "/cgi-bin/center.cgi",
    check_in_id: "panel_list",
    page_size: 20,
    panel_name: "list_panel",
    panel_title: "报警信息列表",
    is_panel_closable: true,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            detail_data_auto = data_item.detail_data_auto;
        }
    },
    is_load_all_data: false,
    render: list_panel_render,
    panel_header: [{
        "enable": true,
        "type": "checkbox",
        "title": "",
        "name": "checkbox",
        "column_cls": "rule-listbc",
        "width": "5%"
    }, {
        "enable": false,
        "type": "radio",
        "name": "radio",
        "column_cls": "rule-listbc",
        "width": "5%"
    }, {
        "enable": true,
        "type": "text",
        "title": "报警主题",        //一般text类型需要title,不然列表没有标题
        "name": "theme",
        "width": "40%"
    }, {
        "enable": false,
        "type": "text",
        "title": "报警类型",
        "name": "type",
        "width": "20%"
    }, {
        "enable": true,
        "type": "text",
        "title": "报警时间",
        "name": "time",
        "width": "30%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        id: "confirm_selected",
        name: "confirm_selected",
        value: "confirm_selected",
        button_icon: "",
        button_text: "确认选中",
        functions: {
            onclick: "do_confirm_selected(this);"
        }
    },
    {
        enable: true,
        type: "image_button",
        id: "confirm_all",
        name: "confirm_all",
        value: "confirm_all",
        button_icon: "",
        button_text: "确认全部",
        functions: {
            onclick: "do_confirm_selected(this)"
        }
    }],
    bottom_extend_widgets: {
        "cls": "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            button_text: "关闭",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "list_panel.hide();"
            }
        }]
    },
    extend_search: [{
        "enable": false,         // ==可选==，如果为不填或者为false,就不显示
        "type": "select",         // ==可选==，默认为text类型
        "id": "alarm_type",     // ==可选==，控件ID
        "name": "alarm_type",   // **必填**，控件的名字
        "title": "报警类型",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        "options": [
            {"value":"all","text":"所有事件"},
            {"value":"system","text":"系统事件"},
            {"value":"ips","text":"入侵防御事件"}
        ]
    },  {
        "enable": false,
        "type": "image_button",
        "id": "begin_search",
        "name": "begin_search",
        "button_text": "确定",
        "cls": "my_search_button",
        "functions": {
            onclick: "extend_search_function(this);"
        }
    }]
};

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
function do_request_alarm(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/center.cgi",
        data: sending_data,
        async: false,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//加载预警详细信息
function show_detail_panel(id,item_id){
    add_panel.show();
    confirm_id = id;
    detail_data = list_panel.detail_data[item_id];
    $("#theme_display").html(detail_data.theme);
    $("#type_display").html(detail_data.type);
    $("#time_display").html(detail_data.time);
    var content = detail_data.content.split("\|").join("</br>");
    $("#content_display").html(content);
    //自动确认相同事件设置
    var is_same = false;
    var num_event = "";
    detail_data_auto_confirm = "";
    for(var i=0;i<detail_data_auto.length;i++){
        if(detail_data_auto[i].alarm_theme == detail_data.theme){
            is_same = true;
            num_event = detail_data_auto[i].num_event;
            detail_data_auto_confirm = detail_data_auto[i];
        }
    }
    if(is_same){
        $("#enable_same").attr("checked","checked");
        $("#num_event").removeAttr("disabled");
        $("#num_event").val(num_event);
    }else{
        $("#enable_same").removeAttr("checked");
        $("#num_event").val("");
        $("#num_event").attr("disabled","disabled");
    }
}
//点击确定按钮的操作
function do_confirm_detail(){
    var sending_data;
    var id_auto = "";
    var item_auto = "";
    if($("#enable_same").is(":checked")){
        is_checked = "yes";
        if(detail_data_auto_confirm != ""){
            id_auto = detail_data_auto_confirm.id;
            item_auto = detail_data_auto_confirm.alarm_theme+","+$("#num_event").val();
        }else{
            id_auto = "new_id";
            item_auto = detail_data.theme+","+$("#num_event").val();
        }
        
        sending_data = {
            ACTION: 'do_confirm_detail',
            id_alarm: confirm_id,
            id_auto: id_auto,
            item_auto: item_auto,
            is_checked: is_checked
        };
    }else{
        is_checked = "no";
        if(detail_data_auto_confirm != ""){
            id_auto = detail_data_auto_confirm.id;
            item_auto = detail_data_auto_confirm.alarm_theme+","+$("#num_event").val();
        }
        sending_data = {
            ACTION: 'do_confirm_detail',
            id_alarm: confirm_id,
            id_auto: id_auto,
            item_auto: item_auto,
            is_checked: is_checked
        };
    }
    function ondatareceived(data) {
        list_panel.update_info(true);
    }
    var val_event = $("#num_event").val();
    if(is_checked == "yes" && (val_event < 1 || val_event > 10000)){
        message_manager.show_popup_error_mesg("请填写1-10000之间的整数再确认！");
    }else{
        do_request_alarm(sending_data, ondatareceived);
        add_panel.hide();
    }
}
//确认选中事件
function do_confirm_selected(e){
    var ids = "";
    if(e.value == "confirm_all"){
        ids = "ids_all";
    }else{
        var checked_items = list_panel.get_checked_items();
        var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].id );
        }
        ids = checked_items_id.join( "," );
    }
    var sending_data = {
        ACTION: 'do_confirm_selected',
        id: ids
    };
    function ondatareceived(data) {
        list_panel.update_info(true);
    }
    do_request_alarm(sending_data, ondatareceived);
}
//改变输入框状态
function change_input_state(e){
    if(e.checked){
        $("#num_event").removeAttr("disabled");
        is_checked = "yes";
    }else{
        $("#num_event").attr("disabled","disabled");
        is_checked = "no";
    }
}