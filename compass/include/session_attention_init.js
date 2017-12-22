$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    paging_holder = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    add_panel.render();
    message_manager.render();
    paging_holder.render();
    add_panel.hide();
    
    add_panel.set_ass_message_manager( message_manager );
    paging_holder.set_ass_message_manager( message_manager );
    
    paging_holder.update_info(true);
    $('.userTipRight').hide();
});
var add_panel;
var message_box_config = {
    url: "/cgi-bin/session_attention.cgi",
    check_in_id: "mesg_box_attention",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/session_attention.cgi",
    check_in_id: "panel_block_add",
    panel_name: "add_panel",
    rule_title: "临时阻断",
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        after_save_data: function( add_obj,data_item ) {
            paging_holder.update_info(true);
        }
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
                "selected": true,
                "functions": {
                    onclick: "changeAddPanel(this);"
                }
            }, {
                "value": "tcp",
                "text": "TCP",
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
    }, {
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
        sub_items: [
            {
                enable: true,
                type: "text",
                id: "d_port",
                name: "d_port",
                value: "",
                tip: "（如:22,23-65,不填为任意）",
                functions: {
                },
                check: {
                    type: "text",
                    required: 1,
                    check: 'port|port_range|',
                    ass_check: function( check ) {

                    }
                }
            }
        ]
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
    'classification': {
        render: function( default_rendered_text, data_item ) {
            return '<span class="note">' + default_rendered_text + "--" + data_item.id + '</span>';
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
        var action_buttons = [
                {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "cut.png",
                    "button_text": "添加临时阻断",
                    "value": data_item.id,
                    "functions": {
                        //onclick: "goto_another_page();"
                        onclick: "show_add_panel(this.value);"
                    }
                }
            ];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/session_attention.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_account",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    //panel_title: "筛选连接",
    is_panel_closable: false,
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [{
        "enable": false,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //用户装载数据之用
        "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
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
        "title": "协议",        //一般text类型需要title,不然列表没有标题
        "name": "protocol",
        "width": "8%"
    }, {
        "enable": true,
        "type": "text",
        "title": "源IP",
        "name": "s_ip",
        "width": "14%"
    }, {
        "enable": true,
        "type": "text",
        "title": "源端口",
        "name": "s_port",
        "width": "14%"
    }, {
        "enable": true,
        "type": "text",
        "title": "目的IP",
        "name": "d_ip",
        "width": "14%"
    }, {
        "enable": true,
        "type": "text",
        "title": "目的端口",
        "name": "d_port",
        "width": "14%"
    }, /* {
        "enable": true,
        "type": "text",
        "title": "状态",
        "name": "state",
        "width": "14%"
    },  */{
        "enable": true,
        "type": "text",
        "title": "存活时间",
        "name": "live_time",
        "width": "14%"
    }, {
        "enable": true,
        "type": "action",
        "title": "活动/动作",
        "name": "action",
        "width": "8%"
    }],
    top_buttons: [{
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
    }],
    bottom_buttons: [{
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
    is_default_search: false,          /* ===可选===，默认是true，控制默认的搜索条件 */
    extend_search: [{
        "enable": true,         // ==可选==，如果为不填或者为false,就不显示
        "type": "select",         // ==可选==，默认为text类型
        "id": "style_protocol",     // ==可选==，控件ID
        "name": "style_protocol",   // **必填**，控件的名字
        "title": "协议",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        "options": [
            {"value":"all","text":"任意"},
            {"value":"tcp","text":"TCP"},
            {"value":"udp","text":"UDP"},
            {"value":"icmp","text":"ICMP"}
        ]
    }, {
        "enable": true,
        "type": "text",
        "id": "s_ip_or_mask",
        "name": "s_ip_or_mask",
        "title": "源IP/掩码",
         "check":{
            type: "text",
            required: 0,
            check: 'ip|ip_mask|',
            ass_check: function( check ) {
                
            }
        } 
    },{
        "enable": true,
        "type": "text",
        "id": "d_ip_or_mask",
        "name": "d_ip_or_mask",
        "title": "目的IP/掩码",
         "check":{
            type: "text",
            required: 0,
            check: 'ip|ip_mask|',
            ass_check: function( check ) {
                
            }
        } 
    },{
        "enable": true,
        "type": "text",
        "id": "d_port_range",
        "name": "d_port_range",
        "title": "目的端口范围",
         "check":{
            type: "text",
            required: 0,
            check: 'other',
            other_reg:'!/^\$/',
            ass_check: function( check ) {
                var d_port_range = $('#d_port_range').val().split(','),msg=''
                if($('#d_port_range').val()){
                    for (var i = 0; i < d_port_range.length; i++) {
                        if(!(/^\d+\-\d+$/.test(d_port_range[i])||/^\d+$/.test(d_port_range[i]))){
                            msg  = '格式错误'
                            return msg;
                        } else{
                            var arr = d_port_range[i].split('-')
                            if (arr[0]<0&&arr[1]<0&&arr[0]>65535&&arr[1]>65535) {
                                msg  = '端口范围不正确'
                                return msg;
                            }
                        }

                    }
                    
                }

            }
        } 
    },{
        "enable": true,
        "type": "image_button",
        "id": "begin_search",
        "name": "begin_search",
        // "button_icon": "search16x16.png",
        "button_text": "确定",
        cls: "my_search_button",
        "functions": {
            onclick: "extend_search_function(this);"
        }
    }],
    actions: {                      /* ===可选=== */
        // enable_button: function( data_item ) {
        //     alert("外部函数enable-" + data_item.id);
        // },
        // disable_button: function( data_item ) {
        //     alert("外部函数disable-" + data_item.id);
        // },
        // eidt_button: function( data_item ) {
        //     alert("外部函数eidt-" + data_item.id);
        // },
        // delete_button: function( data_item ) {
        //     alert("外部函数delete-" + data_item.id);
        // },
        edit_item: function( data_item, on_finished ) {
            /* 开始书写自己的代码 */
            alert("外部函数eidt-" + data_item.id);


            /* 处理完成后**必须**调用执行 */
            on_finished();
        }
    }
}

var paging_holder;

/* function test_test_test() {
    var checked_items = paging_holder.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var str = checked_items_id.join( " | " );

    // var selected_item = paging_holder.selected_item;
    alert( str );
} */
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
        setTimeout("load_data_linkage()",60000*5);
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

//页面跳转函数
function goto_another_page(){
    parent.window.document.getElementById('rightFrame').src='session_break.cgi';
}

function show_add_panel(data_item_id){
    add_panel.show();
    var data_item = paging_holder.detail_data[data_item_id];
    var ele = {"value":data_item.protocol};
    changeAddPanel(ele);
    $("#protocol").val(data_item.protocol);
    $("#source").val(data_item.s_ip);
    $("#s_port").val(data_item.s_port);
    $("#dest").val(data_item.d_ip);
    $("#d_port").val(data_item.d_port);
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