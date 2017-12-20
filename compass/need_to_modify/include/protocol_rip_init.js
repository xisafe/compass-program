$(document).ready(function(){
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
    load_usable_interface();
    change_checkModel();
    /* 绑定时间输入*/
    //ESONCalendar.bind("time_start");
    //ESONCalendar.bind("time_end");
});

var useable_interfaces = [];

var message_box_config = {
    url: "/cgi-bin/protocol_rip.cgi",
    check_in_id: "mesg_box_rip",
    panel_name: "my_message_box"
}
var message_manager = new MessageManager( message_box_config );
var add_panel_config = {
    url: "/cgi-bin/protocol_rip.cgi",
    check_in_id: "panel_rip_add",
    panel_name: "add_panel",
    rule_title: "接口配置",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            //先加载数据
            change_version();
        },
        after_load_data: function( add_obj,data_item ) {
            //先加载数据
            change_version();
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "选择接口",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "interface",
                    name: "interface",
                    value: ""
                }
            ]
        }, {
            title: "版本",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "version",
                    name: "version",
                    options: [
                        {
                            text: "默认",
                            value: "1 2"
                        },
                        {
                            text: "RIPV1",
                            value: "1"
                        },
                        {
                            text: "RIPV2",
                            value: "2"
                        }
                    ],
                    value: "",
                    functions: {
                        onchange: "change_version()",
                        onkeyup: "change_version()"
                    }
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
                    value: "",
					check: {
						type:'text',
						required:'0',
						check:'other|',
						other_reg: '/.*/',
						ass_check:function( check ){
                    
						}	
					}
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
                        check: 'num|',
                        ass_check: function( check ) {
                            var val = $("#character").val();
                            if(val > 255){
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
        }
    ]
};
var add_panel = new RuleAddPanel( add_panel_config );

var list_panel_render = {
    'protocol': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "RIP";
            return '<span>' + result_render + '</span>';
        }
    },
    'version': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text == "1 2"){
                result_render = "默认";
            }else if(default_rendered_text == "1"){
                result_render = "RIPV1";
            }else if(default_rendered_text == "2"){
                result_render = "RIPV2";
            }
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
    }
};


var list_panel_config = {
    url: "/cgi-bin/protocol_rip.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_rip_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持接口关键字查询",
        title: ""
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
            "td_class": "align-center"
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
            "width": "18%"
        }, {
            "enable": true,
            "type": "text",
            "title": "接口",
            "name": "interface",
            "width": "18%"
        }, {
            "enable": true,
            "type": "text",
            "title": "版本",
            "name": "version",
            "width": "18%"
        }, {
            "enable": true,
            "type": "text",
            "title": "验证模式",
            "name": "check_model",
            "width": "26%"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "10%",
            "td_class": "align-center"
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "新建接口配置",
            // style:"padding:3px 4px",
            functions: {
                onclick: "add_rule(this);"
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
var list_panel = new PagingHolder( list_panel_config );

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
    $("#username").attr("value","");
    $("#pwd").attr("value","");
    add_panel.show();
    change_checkModel();
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
            $("#interface").append("<option onclick='change_checkModel();' value='"+useable_interfaces[i]+"'>"+useable_interfaces[i]+"</option>");
        }
    }
    do_request(sending_data, ondatareceived);
}
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/protocol_rip.cgi',
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
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
    var height = $("#modal_border_box_add_panel").height();
    $("#TransparentBorder_add_panel").css('height',height);
}
function change_version(){
    var version = $("#version").val();
    if(version == "1"){
        $(".tr_crl_checkModel").hide();
        $(".tr_crl_check").hide();
        $(".tr_crl_character").hide();
    }else{
        $(".tr_crl_checkModel").show();
        change_checkModel();
    }
    var height = $("#modal_border_box_add_panel").height();
    $("#TransparentBorder_add_panel").css('height',height);
}
//启用禁用调用函数
function change_switch(){
    var enabled = "";
    if($("#enableRIP").is(":checked")){
        enabled = "on";
    }else{
        enabled = "off";
    }
    var sending_data = {
        ACTION: "switch",
        ENABLED: enabled
    };

    function ondatareceived(data) {
        //list_panel.update_info(true);
        list_panel.show_apply_mesg();
    }

    do_request(sending_data, ondatareceived);
}