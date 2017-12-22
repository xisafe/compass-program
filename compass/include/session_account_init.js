$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    add_panel.render();
    message_manager.render();
    paging_holder.render();
    detail_paging_holder.render();
    
    add_panel.hide();
    detail_paging_holder.hide();
    
    add_panel.set_ass_message_manager( message_manager );
    paging_holder.set_ass_message_manager( message_manager );
    
    paging_holder.update_info(true);
    load_data_linkage();
        $('.userTipRight').hide();
});
var message_box_config = {
    url: "/cgi-bin/session_account.cgi",
    check_in_id: "message_box_account",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel;
var add_panel_config = {
    url: "/cgi-bin/session_account.cgi",
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
            enable: true,
            type: "select",
            name: "protocol",
            id: "protocol",
            functions: {
                onclick: "changeAddPanel(this);"
            },
            options: [{
                value: "all",
                text: "任意",
                "selected": true,
                functions: {
                    onclick: "changeAddPanel(this);"
                }
            }, {
                value: "tcp",
                text: "TCP",
                functions: {
                    onclick: "changeAddPanel(this);"
                }
            }, {
                value: "udp",
                text: "UDP",
                functions: {
                    onclick: "changeAddPanel(this);"
                }
            }, {
                value: "icmp",
                text: "ICMP",
                functions: {
                    onclick: "changeAddPanel(this);"
                }
            }],
            "multiple": false,
            check: {
                type:'select-one',
                required:'1',
                ass_check:function( check ){
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
        sub_items: [{
            enable: true,
            type: "text",
            id: "s_port",
            name: "s_port",
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
        title: "type",
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
                    var ip = $("#source").val();
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
            check: {
                type: "text",
                required: 0,
                check: 'num|',
                ass_check: function( check ) {
                    if($("#code").val() != "" || $("#code").val() != null){
                        if($("#type").val() == "" || $("#type").val() == null){
                            add_panel_config.items_list[3].sub_items[0].check.required = 1;
                            $("#add_panel_add_button_id_for_add_panel").attr("disabled",true);
                            alert("选填了code就一定要选填type!");
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
    'classification': {
        render: function( default_rendered_text, data_item ) {
            return '<span class="note">' + default_rendered_text + "--" + data_item.id + '</span>';
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
            var action_buttons = [{
                enable: true,
                id: "show_detail",
                name: "show_detail",
                button_icon: "detail.png",
                button_text: "查看详情",
                class:"action-image",
                value: data_item.ip_or_port,
                functions: {
                    onclick: "show_detail(this.value);"
                }
            }, {
                enable: true,
                id: "cut_session",
                name: "cut_session",
                button_icon: "cut.png",
                button_text: "阻断",
                class:"action-image",
                value: data_item.ip_or_port,
                functions: {
                    //onclick: "goto_another_page();"
                    onclick: "show_add_panel(this.value);"
                }
            }];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/session_account.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_account",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 8,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [{
        enable: false,            //用户控制表头是否显示
        type: "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        title: "",                //不同类型的，title需要的情况不同，一般text类型需要title
        name: "checkbox",         //用户装载数据之用
        column_cls: "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        width: "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
        functions: {              //一般只有checkbox才会有这个字段
        }
    }, {
        enable: false,
        type: "radio",
        name: "radio",
        column_cls: "rule-listbc",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "源IP地址",        //一般text类型需要title,不然列表没有标题
        name: "s_ip",
        width: "30%"
    }, {
        enable: true,
        type: "text",
        title: "会话总数",
        name: "session_num",
        width: "30%"
    }, {
        enable: true,
        type: "action",
        title: "活动/动作",
        "class": "align-center",
        name: "action",
        width: "30%"
    }],
    top_widgets: [{
        enable: false,             // ==可选==，如果为不填或者为false,就不显示
        id: "enable_selected",    // ==可选==，按钮的ID
        name: "enable_selected",  // ==可选==，按钮的名字
        button_icon: "on.png",    // ==可选==，操作按钮的图标，如果没有设置，就没有图标
        button_text: "启用选中",  // **必填**，操作按钮的文字，这个必须设置,建议在五个字以内
        functions: {              // ==可选==，回调函数，没有的话就只是一个按钮，什么也不做
            onclick: "test_test_test(this)"
        }
    }, {
        enable: false,
        id: "disable_selected",
        name: "disable_selected",
        button_icon: "off.png",
        button_text: "禁用选中",
        functions: {
            onclick: "disable_selected_items(this)"
        }
    }],
    bottom_buttons: [{
        enable: false,
        id: "export_selected",
        name: "export_selected",
        button_icon: "download.png",
        button_text: "导出选中",
        functions: {
            onclick: "export_selected_items(this)"
        }
    }, {
        enable: false,
        id: "delete_all_logs",
        name: "delete_all_logs",
        button_icon: "delete.png",
        button_text: "清空日志",
        functions: {
            onclick: "delete_all_logs(this)"
        }
    }],
    is_default_search: false,          /* ===可选===，默认是true，控制默认的搜索条件 */
    extend_search: [{
        enable: true,         // ==可选==，如果为不填或者为false,就不显示
        type: "select",         // ==可选==，默认为text类型
        id: "style_account",     // ==可选==，控件ID
        name: "style_account",   // **必填**，控件的名字
        title: "统计方式",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        options: [{
            value:"s_ip",
            text:"源IP统计"
        }, {
            value:"d_ip",
            text:"目的IP统计"
        }, {
            value:"s_port",
            text:"服务端口统计"
        }],
        functions: {
            onclick: "change_label_for_paramter(this);"
        }
    }, {
        enable: true,
        type: "text",
        id: "query_parameter",
        name: "query_parameter",
        title: "请输入IP/掩码",
        check: {
            type: 'text',
            required: '0',
            check: 'other',
            other_reg: '!/^\$/',
            ass_check:function(eve){
                var val_style = $( "#style_account" ).val();
                var param = eve._getCURElementsByName("query_parameter","input","list_panel_search_form_for_list_panel")[0].value;
                if( val_style == "s_port"  ) {
                    //param = eve.trim(param);
                    if(!eve.validport(param)){
                        return "请输入正确的端口";
                    }
                }else{
                    if(!eve.validip(param) && !eve.validsegment(param)){
                        return "请输入正确的IP地址或IP/掩码";
                    }
                }
            }
        }
    }, {
        enable: true,
        type: "image_button",
        id: "begin_search",
        name: "begin_search",
        // button_icon: "search16x16.png",
        button_text: "确定",
        "cls": "my_search_button",
        functions: {
            onclick: "extend_search_function(this);"
        }
    }]
};

//详细信息面板配置
var detail_list_panel_config = {
    url: "/cgi-bin/session_account.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_detail",         /* ***必填***，确定面板挂载在哪里 */
    panel_title: "详细情况",
    is_panel_closable: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    is_modal: true,
    panel_name: "detail_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_default_search: false,          /* ===可选===，默认是true，控制默认的搜索条件 */
    panel_header: [{
        enable: false,            //用户控制表头是否显示
        type: "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        title: "",                //不同类型的，title需要的情况不同，一般text类型需要title
        name: "checkbox",         //用户装载数据之用
        column_cls: "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        width: "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
        functions: {              //一般只有checkbox才会有这个字段
        }
    }, {
        enable: false,
        type: "radio",
        name: "radio",
        column_cls: "rule-listbc",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "协议",        //一般text类型需要title,不然列表没有标题
        name: "protocol",
        column_cls: "align-center",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "源IP",
        column_cls: "align-center",
        name: "s_session_sender",
        width: "15%"
    }, {
        enable: true,
        type: "text",
        title: "源端口",
        column_cls: "align-center",
        name: "d_session_sender",
        width: "15%"
    }, {
        enable: true,
        type: "text",
        title: "目的IP",
        column_cls: "align-center",
        name: "s_session_reciver",
        width: "15%"
    }, {
        enable: true,
        type: "text",
        title: "目的端口",
        column_cls: "align-center",
        name: "d_session_reciver",
        width: "15%"
    },/* {
        enable: true,
        type: "text",
        title: "状态",
        name: "state",
        width: "15%"
    },  */{
        enable: true,
        type: "text",
        title: "剩余时间",
        name: "left_time",
        column_cls: "align-center",
        width: "10%"
    }]
};

var paging_holder =  new PagingHolder( list_panel_config );
var detail_paging_holder = new PagingHolder( detail_list_panel_config );

//初始化实时连接状态
function load_data_linkage(){
    var sending_data = {
        ACTION: "load_data_linkage"
    };

    function ondatareceived(data) {
        var data_content = data;
        //var data_content = JSON.parse(data);
        //var data_content = eval("("+data+")");
        document.getElementById("total").innerHTML = data_content.total;
        document.getElementById("tcp").innerHTML = data_content.tcp;
        document.getElementById("udp").innerHTML = data_content.udp;
        document.getElementById("icmp").innerHTML = data_content.icmp;
        document.getElementById("other").innerHTML = data_content.other;
        setTimeout("load_data_linkage()",3000);
    }
    paging_holder.request_for_json(sending_data, ondatareceived);
}

function enable_selected_items() {
    var checked_items = paging_holder.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    paging_holder.enable_item( ids );
}

function disable_selected_items() {
    var checked_items = paging_holder.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    paging_holder.disable_item( ids );
}

function extend_search_function( element ) {
    setTimeout(function(){
        $('.userTipRight').fadeOut('slow')  
    },1000)
    paging_holder.update_info( true );
}

//显示详细信息面板
function show_detail(paramter){
    var count_type = $("#style_account").val();
    detail_paging_holder.extend_sending_data = {
        ACTION: "generate_data_detail",
        param: paramter,
        count_type: count_type
    };
    //detail_paging_holder.render();
    detail_paging_holder.show();
    detail_paging_holder.update_info( true );
    
    
}

//页面跳转函数
function goto_another_page(){
    parent.window.document.getElementById('rightFrame').src='session_break.cgi';
}

function show_add_panel(ip_or_port){
    add_panel.show();
    var ele = {value:"all"};
    changeAddPanel(ele);
    var count_type = $("#style_account").val();
    if(count_type == "s_ip"){
        $("#source").val(ip_or_port);
        $("#dest").val("0.0.0.0/0");
    }else if(count_type == "d_ip"){
        $("#dest").val(ip_or_port);
        $("#source").val("0.0.0.0/0");
    }
    $("#left_time").val("10");
    
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

function change_label_for_paramter(e){
    if(e.value == 's_port'){
        paging_holder.set_extend_search_item_title_by_id("query_parameter","请输入端口");
    }else{
        paging_holder.set_extend_search_item_title_by_id("query_parameter","请输入IP/掩码");
    }
    $("#query_parameter").val("");
}