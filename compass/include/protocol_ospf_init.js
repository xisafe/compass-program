var useable_interfaces = [];
$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    add_panel_interface = new RuleAddPanel( add_panel_config_interface );
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    /* 渲染面板 */
    add_panel.render();
    add_panel_interface.render();
    list_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    add_panel_interface.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel_interface );
    
    add_panel.set_ass_message_manager( message_manager );
    add_panel_interface.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    add_panel.hide();
    add_panel_interface.hide();
    
    list_panel.update_info(true);
    load_usable_interface();
    change_checkModel();
    change_levelSetting();
});
var list_panel;
var add_panel;
var add_panel_interface;
var message_box_config = {
    url: "/cgi-bin/protocol_ospf.cgi",
    check_in_id: "mesg_box_ospf",
    panel_name: "my_message_ospf"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/protocol_ospf.cgi",
    check_in_id: "panel_ospf_add",
    panel_name: "add_panel_area",
    rule_title: "区域（请为区域添加接口，若该区域无接口，OSPF路由将不会生效！）",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            change_checkModel();
            flag = "on";
            change_levelSetting();
        },
        after_load_data: function( add_obj,data_item ) {
            change_checkModel();
            load_usable_interface();
        },
        after_save_data: function( add_obj,data_item ) {
            load_usable_interface();
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "区域ID号*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "sectionID_a",
                    name: "sectionID_a",
                    tip: "(0-4294967295)",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'int|',
                        ass_check: function( check ) {
                            var val = $("#sectionID_a").val();
                            if(val > 4294967295){
                                return "区域ID号应在0-4294967295之间";
                            }
                        }
                    }
                }
            ]
        }, {
            title: "区域类型",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "sectionType",
                    name: "sectionType",
                    options: [
                        {
                            text: "普通",
                            value: "common"
                        },
                        {
                            text: "STUB",
                            value: "stub"
                        },
                        {
                            text: "NSSA",
                            value: "nssa"
                        }
                    ]
                }
            ]
        }
    ]
};

var add_panel_config_interface = {
    url: "/cgi-bin/protocol_ospf.cgi",
    check_in_id: "panel_ospf_add_interface",
    panel_name: "add_panel_interface",
    rule_title: "接口",
    is_modal: true,
    border_transparent: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            load_usable_interface();
            $("#check_model").val(data_item.check_model);
            change_checkModel();
            $("#interface").append("<option value='"+data_item.interface+"'>"+data_item.interface+"</option>");
            $("#interface_old").val(data_item.interface);
            $("#sectionID_old").val(data_item.sectionID);
        },
        after_load_data: function(add_obj, data_item) {
            // console.log(data_item);
        },
        after_save_data: function( add_obj,data_item ) {
            load_usable_interface();
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "区域*",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "sectionID",
                    name: "sectionID",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "select-one",
                        required: 1,
                        check: 'name|',
                        ass_check: function( check ) {
                            if($("#sectionID").val() == "" || $("#sectionID").val() == null){
                                return "您还没有创建区域，请先创建区域！";
                            }
                        }
                    }
                }
            ]
        }, {
            title: "接口",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "interface",
                    name: "interface",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "select-one",
                        required: 1,
                        check: 'name|',
                        ass_check: function( check ) {
                            if($("#interface").val() == "" || $("#interface").val() == null){
                                return "系统接口已经用完！";
                            }
                        }
                    }
                }, {
                    enable: true,
                    type: "text",
                    item_style: "display:none;",
                    id: "interface_old",
                    name: "interface_old",
                    value: ""
                }, {
                    enable: true,
                    type: "text",
                    item_style: "display:none;",
                    id: "sectionID_old",
                    name: "sectionID_old",
                    value: ""
                }
            ]
        }, {
            title: "验证模式",
            class: "tr_crl_checkModel",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "check_model",
                    name: "check_model",
                    options: [
                        {
                            text: "不验证",
                            value: "noCheck"
                        },
                        {
                            text: "明文",
                            value: "laws"
                        },
                        {
                            text: "密文",
                            value: "ciphertext"
                        }
                    ],
                    value: "",
                    functions: {
                        onchange:  "change_checkModel()",
                        onkeyup: "change_checkModel()"
                    }
                }
            ]
        }, {
            title: "验证字",
            class: "tr_crl_check",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "text_check",
                    name: "text_check",
                    value: ""
                }
            ]
        }, {
            title: "标示符*",
            class: "tr_crl_character",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "character",
                    name: "character",
                    tip: "（1-255）",
                    value: "",
                    check: {
                        type: "text",
                        required: 1,
                        check: 'int|',
                        ass_check: function( check ) {
                            var val = $("#character").val();
                            if(val<1 || val > 255){
                                return "标示符应在1-255之间";
                            }
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
                    name: "enable",
                    value: ""
                }
            ]
        },
        //高级设置
        {
            title: "高级设置",
            style: "color:blue;",
            sub_items: [
                {
                    enable: true,
                    type: "button",
                    id: "highSetting",
                    name: "highSetting",
                    value: "点击展开",
                    style:'margin-left: auto;height: 20px;',
                    functions: {
                        onclick: "change_levelSetting()"
                    }
                }
            ]
        },
        {
            title: "hello间隔",
            class: "tr_crl_hello",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "hello",
                    name: "hello",
                    tip: "(5-65535)",
                    value: "10",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'int|',
                        ass_check: function( check ) {
                            var val = $("#hello").val();
                            if(val <5 || val > 65535){
                                return "hello间隔应在5-65535之间";
                            }
                        }
                    }
                }
            ]
        }, {
            title: "dead间隔",
            class: "tr_crl_dead",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "dead",
                    name: "dead",
                    tip: "(20-65535，默认值：40)",
                    value: "40",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'int|',
                        ass_check: function( check ) {
                            var val = $("#dead").val();
                            if(val <20 || val > 65535){
                                return "dead间隔应在20-65535之间";
                            }
                        }
                    }
                }
            ]
        }, {
            title: "优先级",
            class: "tr_crl_level",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "level",
                    name: "level",
                    tip: "(0-255，默认值：1)",
                    value: "1",
                    check: {
                        type: "text",
                        required: 1,
                        check:'int|',
                        ass_check: function( check ) {
                            var val = $("#dead").val();
                            if(val > 255){
                                return "优先级应在0-255之间";
                            }
                        }
                    }
                }
            ]
        }
    ]
};

var list_panel_render = {
    'protocol': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "OSPF";
            return '<span>' + result_render + '</span>';
        }
    },
    'check_model': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text == "" || default_rendered_text == null){
                result_render = "不验证";
            }else if(default_rendered_text == "laws"){
                result_render = "明文（验证字："+data_item.text_check+"）";
            }else if(default_rendered_text == "ciphertext"){
                result_render = "密文（验证字："+data_item.text_check+"，标示符："+data_item.character+"）";
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'sectionType': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text == "common"){
                result_render = "普通";
            }else if(default_rendered_text == "stub"){
                result_render = "STUB";
            }else if(default_rendered_text == "nssa"){
                result_render = "NSSA";
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
            var action_buttons = [];
            var src_enable;
            var text_enable;
            var function_enable;
            if(data_item.enable == 'on'){
                src_enable = 'on';
                text_enable = '禁用';
                function_enable = "disable_selected_items(this)";
            }else{
                src_enable = 'off';
                text_enable = '启用';
                function_enable = "enable_selected_items(this)";
            }
            if(data_item.id >= data_item.num_interface){
                action_buttons = [
                    {
                        "enable": true,
                        "id": "delete_item",
                        "name": "delete_item",
                        "button_icon": "delete.png",
                        "button_text": "删除",
                        "value": data_item.id,
                        "class": "action-image",
                        "functions": {
                            onclick: "delete_selected_items(this);"
                        }
                    }
                ];
            }else{
                action_buttons = [
                    {
                        "enable": true,
                        "id": "enable_item",
                        "name": "enable_item",
                        "button_icon": src_enable+".png",
                        "button_text": text_enable,
                        "value": data_item.id,
                        "class": "action-image",
                        "functions": {
                            onclick: function_enable
                        }
                    },
                    {
                        "enable": true,
                        "id": "edit_item",
                        "name": "edit_item",
                        "button_icon": "edit.png",
                        "button_text": "编辑",
                        "value": data_item.id,
                        "class": "action-image",
                        "functions": {
                            onclick: "list_panel.edit_item("+data_item.id+")"
                        }
                    },
                    {
                        "enable": true,
                        "id": "delete_item",
                        "name": "delete_item",
                        "button_icon": "delete.png",
                        "button_text": "删除",
                        "value": data_item.id,
                        "class": "action-image",
                        "functions": {
                            onclick: "delete_selected_items(this);"
                        }
                    }
                ];
            }
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/protocol_ospf.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_ospf_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    default_search_config: {
        input_tip: "支持区域ID、区域类型、接口查询",
        title: ""
    },
    event_handler: {
        before_load_data: function( list_abj,data ) {
            
        },
        after_load_data: function( list_obj,data ) {
            load_usable_interface();
        }
    },
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
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
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "区域ID",
            "name": "sectionID",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "区域类型",
            "name": "sectionType",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "接口",
            "name": "interface",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "验证模式",
            "name": "check_model",
            "width": "20%"
        }, {
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
            button_icon: "add16x16.png",
            button_text: "新建区域",
            functions: {
                onclick: "add_rule(this);"
            }
        }, {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "添加接口",
            functions: {
                onclick: "add_rule_interface(this);"
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
    is_default_search: true
    
}

function enable_selected_items(e) {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );
    if(ids == "" || ids == null){
        ids = e.value;
    }

    list_panel.enable_item( ids );
}

function disable_selected_items(e) {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );
    if(ids == "" || ids == null){
        ids = e.value;
    }

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

function add_rule_interface( element ) {
    add_panel_interface.show();
    change_checkModel();
    flag = "on";
    change_levelSetting();
}

//切换添加面板表单选项
function change_checkModel(){
    var checkModel = $("#check_model").val();
    if(checkModel == "noCheck"){
        $(".tr_crl_check").hide();
        $(".tr_crl_character").hide();
    }else if(checkModel == "laws"){
        $(".tr_crl_check").show();
        $(".tr_crl_character").hide();
    }else if(checkModel == "ciphertext"){
        $(".tr_crl_check").show();
        $(".tr_crl_character").show();
    }
    var temp = $("#add_panel_id_for_add_panel_interface").height();
    $("#TransparentBorder_add_panel_interface").height(temp);
}

var flag = "on";
function change_levelSetting(){
    if(flag == "on"){
        $(".tr_crl_hello").hide();
        $(".tr_crl_dead").hide();
        $(".tr_crl_level").hide();
        $("#highSetting").val('点击展开');
        flag = "off";
    }else{
        $(".tr_crl_hello").show();
        $(".tr_crl_dead").show();
        $(".tr_crl_level").show();
        $("#highSetting").val('点击收起');
        flag = "on";
    }
    var temp = $("#add_panel_id_for_add_panel_interface").height();
    $("#TransparentBorder_add_panel_interface").height(temp);
}

//获取系统可用接口
function load_usable_interface(){
    var sending_data = {
        ACTION: "load_usable_interface"
    };
    function ondatareceived(data) {
        useable_interfaces = data.useable_interfaces;
        $("#interface").empty();
        for(var i = 0;i < useable_interfaces.length;i++){
            $("#interface").append("<option value='"+useable_interfaces[i]+"'>"+useable_interfaces[i]+"</option>");
        }
        $("#sectionID").empty();
        for(var j = 0; j < data.sectionIDS.length;j++){
            $("#sectionID").append("<option value='"+data.sectionIDS[j]+"'>"+data.sectionIDS[j]+"</option>");
        }
    }
    do_request(sending_data, ondatareceived);
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/protocol_ospf.cgi',
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

//启用禁用调用函数
function change_switch(){
    var enabled = "";
    if($("#enableOSPF").is(":checked")){
        enabled = "on";
    }else{
        enabled = "off";
    }
    var sending_data = {
        ACTION: "switch",
        ENABLED: enabled
    };

    function ondatareceived(data) {
        list_panel.update_info(true);
    }

    do_request(sending_data, ondatareceived);
}