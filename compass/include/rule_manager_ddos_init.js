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
    load_policy_templates();
    $(".add-panel-form-item").css("marginTop","0px");
    $(".add-panel-form-item").css("marginBottom","0px");
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/rule_manager_ddos.cgi",
    check_in_id: "mesg_box_rule",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/rule_manager_ddos.cgi",
    check_in_id: "panel_rule_add",
    panel_name: "add_panel",
    rule_title: "规则",
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,sending_data ) {
            var addr_host = $("#addr_host").val();
            var addr_from = $("#addr_from").val();
            var addr_to = $("#addr_to").val();
            var addr_ipnet = $("#addr_ipnet").val();
            var type_addr = $("input[name='type_addr']:checked").val();
            var addr_ddos = "";
            var tip = "IP子网";
            if(type_addr == "HOST"){
                addr_ddos = addr_host;
                tip = '主机IP';
            }else if(type_addr == "IPNET"){
                addr_ddos = addr_ipnet;
                tip = 'IP范围';
            }
            if((type_addr == "HOST" || type_addr == "IPNET") && addr_ddos == ""){
                message_manager.show_popup_error_mesg("防护地址中"+tip+"不能为空！");
                return false;
            }else if(type_addr == "IPRANGE"){
                if(addr_from == "" || addr_to == ""){
                    message_manager.show_popup_error_mesg("防护地址中"+tip+"不能为空！");
                    return false;
                }
            }
            
        },
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
            /* if(data_item.type_addr == "HOST"){
                $("#rad_host").attr("checked","checked");
                $("#addr_host").val(data_item.addr1);
            }else if(data_item.type_addr == "IPRANGE"){
                $("#rad_iprange").attr("checked","checked");
                $("#addr_from").val(data_item.addr1);
                $("#addr_to").val(data_item.addr2);
            }else if(data_item.type_addr == "IPNET"){
                $("#rad_ipnet").attr("checked","checked");
                $("#addr_ipnet").val(data_item.addr1);
                $("#mask").val(data_item.addr2);
            } */
            disable_input();
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "名称*",
        sub_items: [{
            enable: true,
            type: "text",
            id: "name",
            name: "name",
            // maxlength: "20",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check:'name',
                ass_check: function( check ) {
                    // var name = $("#name").val();
                    // if(name.length > 20){
                    //     return "规则名称不得多于20个字符！";
                    // }
                }
            }
        }]
    },
    {
        title: "说明",
        sub_items: [{
            enable: true,
            type: "text",
            id: "description",
            name: "description",
            // maxlength: "50",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 0,
                check:'note',
                //other_reg:'!/^\$/',
                ass_check: function( check ) {
                    var description = $("#description").val();
                    if(description.length > 50){
                        return msg="规则名称不得多于50个字符！";
                    }
                }
            }
        }]
    }, {
        title: "防护地址*",
        sub_items: [{
            enable:true,
            type:"items_group",
            item_style:"width:100%;",
            sub_items:[{
                enable: true,
                type: "radio",
                id: "rad_host",
                name: "type_addr",
                value: "HOST",
                checked: true,
                functions: {
                    onclick: "disable_input();"
                }
            }, {
                enable: true,
                type: "text",
                id: "addr_host",
                name: "addr_host",
                value: "",
                label: "主机IP",
                functions: {
                },
                check: {
                    type: "text",
                    required: 1,
                    check:'ip',
                    ass_check: function( check ) {
                    }
                }
            }]
        }, {
            enable:true,
            type:"items_group",
            item_style:"width:100%;",
            sub_items:[{
                enable: true,
                type: "radio",
                id: "rad_iprange",
                name: "type_addr",
                value: "IPRANGE",
                functions: {
                    onclick: "disable_input();"
                }
            }, {
                enable: true,
                type: "text",
                id: "addr_from",
                name: "addr_from",
                value: "",
                label: "IP范围",
                functions: {
                },
                check: {
                    type: "text",
                    required: 1,
                    check:'ip|',
                    ass_check: function( check ) {

                    }
                }
            }, {
                enable: true,
                type: "text",
                id: "addr_to",
                name: "addr_to",
                value: "",
                label: "-",
                functions: {
                },
                check: {
                    type: "text",
                    required: 1,
                    check: 'other',
                    other_reg: '!/^\$/',
                    ass_check: function( check ) {
                        var mesg = "";
                        var ip_from = $("#addr_from").val();
                        var ip_to = $("#addr_to").val();
                        if(!check.validip(ip_to)){
                            mesg = "此项应填ip地址！";
                            return mesg;
                        }
                        var temp1 = ip_from.split(".");
                        var temp2 = ip_to.split(".");
                        for(var i=0;i<4;i++){
                            if((temp1[i] - temp2[i]) > 0){
                                mesg = "该ip地址应大于前一个ip地址！";
                                return mesg;
                            }else if((temp2[i] - temp1[i]) > 0){
                                mesg = "";
                                return mesg;
                            }
                        }
                        return mesg;
                    }
                }
            }]
        }, {
            enable:true,
            type:"items_group",
            item_style:"width:100%;",
            sub_items:[ {
                enable: true,
                type: "radio",
                id: "rad_ipnet",
                name: "type_addr",
                value: "IPNET",
                functions: {
                    onclick: "disable_input();"
                }
            }, {
                enable: true,
                type: "text",
                id: "addr_ipnet",
                name: "addr_ipnet",
                value: "",
                label: "IP子网",
                check: {
                    type: "text",
                    required: 1,
                    check: 'other',
                    other_reg: '!/^\$/',
                    ass_check: function( check ) {
                        var mesg = "";
                        var pre = $("#addr_ipnet").val();
                        var ip_net = pre+"/"+$("#mask").val();
                        if(!check.validsegment(ip_net)){
                            mesg = "请输入正确的子网地址";
                        }
                        if(pre.split("/").length > 1){
                            mesg = "请输入正确的子网地址";
                        }
                        return mesg;
                    }
                }
            }, {
                enable: true,
                type: "select",
                id: "mask",
                name: "mask",
                label: "/",
                options: [{
                    text: "1",
                    value: "1"
                }, {
                    text: "2",
                    value: "2"
                }, {
                    text: "3",
                    value: "3"
                }, {
                    text: "4",
                    value: "4"
                }, {
                    text: "5",
                    value: "5"
                }, {
                    text: "6",
                    value: "6"
                }, {
                    text: "7",
                    value: "7"
                }, {
                    text: "8",
                    value: "8"
                }, {
                    text: "9",
                    value: "9"
                }, {
                    text: "10",
                    value: "10"
                }, {
                    text: "11",
                    value: "11"
                }, {
                    text: "12",
                    value: "12"
                }, {
                    text: "13",
                    value: "13"
                }, {
                    text: "14",
                    value: "14"
                }, {
                    text: "15",
                    value: "15"
                }, {
                    text: "16",
                    value: "16"
                }, {
                    text: "17",
                    value: "17"
                }, {
                    text: "18",
                    value: "18"
                }, {
                    text: "19",
                    value: "19"
                }, {
                    text: "20",
                    value: "20"
                }, {
                    text: "21",
                    value: "21"
                }, {
                    text: "22",
                    value: "22"
                }, {
                    text: "23",
                    value: "23"
                }, {
                    text: "24",
                    value: "24",
                    selected: "true"
                }, {
                    text: "25",
                    value: "25"
                }, {
                    text: "26",
                    value: "26"
                }, {
                    text: "27",
                    value: "27"
                }, {
                    text: "28",
                    value: "28"
                }, {
                    text: "29",
                    value: "29"
                }, {
                    text: "30",
                    value: "30"
                }]
            }]
        }]
    }, {
        title: "源区域",
        sub_items: [{
            enable: true,
            type: "select",
            id: "section_source",
            name: "section_source",
            options: [{
                text: "WAN区",
                value: "WAN"
            }, {
                text: "LAN区",
                value: "LAN"
            }, {
                text: "DMZ区",
                value: "DMZ"
            }]
        }]
    }, {
        title: "防护策略模板",
        sub_items: [{
            enable: true,
            type: "select",
            id: "policy_template",
            name: "policy_template",
            options: []
        }]
    }, {
        title: "检测攻击后操作",
        sub_items: [{
            enable: true,
            type: "checkbox",
            label: "记录日志",
            id: "log",
            name: "log",
            value: "",
            checked: true
        }, {
            enable: true,
            type: "checkbox",
            label: "阻断",
            id: "break",
            name: "break",
            value: "",
            checked: true
        }]
    }, {
        title: "启用",
        sub_items: [{
            enable: true,
            type: "checkbox",
            label: "启用",
            id: "enable",
            name: "enable",
            checked: true,
            value: ""
        }]
    }]
};

var list_panel_render = {
    /* 'enable': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.enable == "on"){
                result_render = "启用";
            }else{
                result_render = "禁用";
            }
            return '<span>' + result_render + '</span>';
        }
    } */
};


var list_panel_config = {
    url: "/cgi-bin/rule_manager_ddos.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_rule_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持名称、说明关键字查询",
        title: ""
    },
    panel_header: [{
        "enable": true,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //用户装载数据之用
        "td_class": "align-center",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
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
        "title": "名称",        //一般text类型需要title,不然列表没有标题
        "name": "name",
        "width": "27%"
    }, {
        "enable": true,
        "type": "text",
        "title": "说明",
        "name": "description",
        "width": "27%"
    }, {
        "enable": true,
        "type": "text",
        "title": "防护策略模板",
        "name": "policy_template",
        "width": "27%"
    }, /* {
        "enable": true,
        "type": "text",
        "title": "启用/禁用",
        "name": "enable",
        "width": "20%"
    },  */{
        "enable": true,
        "type": "action",
        "title": "活动/动作",
        "td_class": "align-center",
        "name": "action",
        "width": "10%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        button_icon: "add16x16.png",
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
        type: "image_button",
        "id": "delete_selected",
        "name": "delete_selected",
        "button_icon": "delete.png",
        "button_text": "删除选中",
        "functions": {
            onclick: "delete_selected_items(this)"
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
    is_default_search: true
    
}

function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    if(checked_items.length < 1){
        message_manager.show_popup_note_mesg("请先选中规则项");
        return;
    }
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }
    var ids = checked_items_id.join( "&" );

    list_panel.enable_item( ids );
}

function disable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    if(checked_items.length < 1){
        message_manager.show_popup_note_mesg("请先选中规则项");
        return;
    }
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
        if(checked_items.length < 1){
            message_manager.show_popup_note_mesg("请先选中规则项");
            return;
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

function add_rule( element ) {
    add_panel.show();
    disable_input();
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/rule_manager_ddos.cgi",
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            alert("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//加载策略模板数据
function load_policy_templates(){
    var sending_data = {
        ACTION: 'load_policy_templates'
    };
    function ondatareceived(data) {
        var policy_templates = data.policy_templates;
        for(var i = 0;i < policy_templates.length; i++){
            $("#policy_template").append("<option value='"+policy_templates[i]+"'>"+policy_templates[i]+"</option>");
        }
    }
    do_request(sending_data, ondatareceived);
}
//禁用其他非选中输入框
function disable_input(){
    var val_addrType = $("input[name='type_addr']:checked").val();
    if(val_addrType == "HOST"){
        $("#addr_host").removeAttr("disabled");
        $("#addr_from").attr("disabled","disabled");
        $("#addr_to").attr("disabled","disabled");
        $("#addr_ipnet").attr("disabled","disabled");
        $("#mask").attr("disabled","disabled");
    }else if(val_addrType == "IPRANGE"){
        $("#addr_host").attr("disabled","disabled");
        $("#addr_from").removeAttr("disabled");
        $("#addr_to").removeAttr("disabled");
        $("#addr_ipnet").attr("disabled","disabled");
        $("#mask").attr("disabled","disabled");
    }else{
        $("#addr_host").attr("disabled","disabled");
        $("#addr_from").attr("disabled","disabled");
        $("#addr_to").attr("disabled","disabled");
        $("#addr_ipnet").removeAttr("disabled");
        $("#mask").removeAttr("disabled");
    }
}