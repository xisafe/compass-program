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
    load_services();
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/double_nat.cgi",
    check_in_id: "mesg_box_nat",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/double_nat.cgi",
    check_in_id: "panel_nat_add",
    panel_name: "add_panel",
    rule_title: "双向NAT规则",
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            init_service();
            init_source();
            init_dest();
        },
        after_load_data: function( add_obj,data_item ) {
            init_service();
            init_source();
            init_dest();
            if(data_item.nat_type_r == "ip"){
                $("#ip_r").val(data_item.ip_r);
            }else if(data_item.nat_type_r == "netmap"){
                $("#ipnet_r").val(data_item.ip_r);
            }
            if(data_item.nat_type_d == "ip"){
                $("#ip_d").val(data_item.ip_d);
            }else if(data_item.nat_type_d == "netmap"){
                $("#ipnet_d").val(data_item.ip_d);
            }else if(data_item.nat_type_d == "lb"){
                $("#lb_d").val(data_item.ip_d);
            }
            //恢复服务协议与端口数据
            if(data_item.protocol){
                $("#protocol").val(data_item.protocol);
            }
            //恢复源，目的
            $("#source").val(data_item.source.split("&").join("\n"));
            $("#dest").val(data_item.dest.split("&").join("\n"));
            if(data_item.dst_port){
                $("#dst_port").show();
                $("label[for = 'dst_port']").show();
                $("#dst_port").val(data_item.dst_port.split("&").join("\n"));
            }
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "源",
        sub_items: [
        {
            enable: true,
            type: "select",
            style: "width:100px;",
            id: "src_type",
            name: "src_type",
            item_style:"width:22%",
            label: "类型*",
            options: [
            {
                text: "网络/IP",
                value: "ip"
            }]
        },
        {
            enable: true,
            item_style:"width:78%",
            type: "textarea",
            id: "source",
            name: "source",
            value: "",
            label: "请输入网络/IP（每行一个）",
            label_style: "display:block;",
            functions: {
            },
            check: {
                type: "textarea",
                required: 1,
                check:'ip|ip_mask',
                ass_check: function( check ) {

                }
            }
        }]
    },
    {
        title: "目的",
        sub_items: [{
            enable: true,
            item_style:"width:22%",
            type: "select",
            style: "width:100px;",
            id: "dst_type",
            name: "dst_type",
            label: "类型*",
            options: [
            {
                text: "网络/IP",
                value: "ip"
            }]
        }, {
            enable: true,
            type: "textarea",
            item_style:"width:78%",
            id: "dest",
            name: "dest",
            value: "",
            label: "请输入网络/IP（每行一个）",
            label_style: "display:block;",
            check: {
                type: "textarea",
                required: 1,
                check:'ip|ip_mask',
                ass_check: function( check ) {

                }
            }
        }]
    }, {
        title: "服务/端口",
        sub_items: [{
            enable: true,
            type:"items_group",
            item_style:"width:22%;margin:0px;",
            style: "margin:0px;",
            "sub_items":[{
                enable: true,
                item_style:"width:100%",
                style: "width:100px;",
                type: "select",
                id: "server",
                name: "server",
                label: "服务*",
                options: [
                    {
                        text: "任意",
                        value: "any"
                    },
                    {
                        text: "用户自定义",
                        value: "defined_byuser"
                    }
                ],
                value: "",
                functions: {
                    onkeyup: "init_service()",
                    onchange: "init_service()"
                }
            },
            {
                enable: true,
                item_style:"width:100%",
                style: "width:100px;",
                type: "select",
                id: "protocol",
                name: "protocol",
                label: "协议*",
                options: [{
                    text: "任意",
                    value: " "
                },
                {
                    text: "TCP",
                    value: "tcp"
                },
                {
                    text: "UDP",
                    value: "udp"
                },
                {
                    text: "TCP+UDP",
                    value: "tcp&udp"
                },
                {
                    text: "ESP",
                    value: "esp"
                },
                {
                    text: "GRE",
                    value: "gre"
                },
                {
                    text: "ICMP",
                    value: "icmp"
                }]
            }]
        }, {
            enable: true,
            item_style:"width:32%",
            type: "textarea",
            id: "dst_port",
            name: "dst_port",
            value: "",
            label: "目的端口/范围（每行一个）",
            functions: {
            },
            check: {
                type: "textarea",
                required: 0,
                check:'port|port_range|',
                ass_check: function( check ) {

                }
            }
        }]
    },
    {
        title: "源转换为",
        sub_items: [{
            enable: true,
            style: "width:100px;",
            item_style:"width:100%",
            type: "select",
            id: "nat_type_r",
            name: "nat_type_r",
            label: "NAT类型*",
            label_style: "width:70px;display:inline-block;",
            options: [
                {
                    text: "IP",
                    value: "ip"
                },
                {
                    text: "网络映射",
                    value: "netmap"
                },
                {
                    text: "不用NAT",
                    value: "return"
                }
            ],
            value: "",
            functions: {
                onkeyup: "init_source()",
                onchange: "init_source()"
            }
        },
        {
            enable: true,
            item_id: "div_ip",
            item_style:"width:100%",
            type: "text",
            id: "ip_r",
            name: "ip_r",
            value: "",
            label: "IP地址*",
            label_style: "width:70px;display:inline-block;",
            tip: "（IP地址，如192.168.1.1）",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check:'ip|',
                ass_check: function( check ) {

                }
            }
        },
        {
            enable: true,
            item_style:"width:100%",
            type: "text",
            id: "ipnet_r",
            name: "ipnet_r",
            item_id: "div_ipnet",
            value: "",
            label: "IP子网*",
            label_style: "width:70px;display:inline-block;",
            tip: "（IP子网，如192.168.1.0/24）",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check:'ip_mask|',
                ass_check: function( check ) {

                }
            }
        }]
    }, {
        title: "目的地址转换为",
        sub_items: [{
            enable: true,
            style: "width:100px;",
            item_style:"width:100%",
            type: "select",
            id: "nat_type_d",
            name: "nat_type_d",
            label: "NAT类型*",
            label_style: "width:70px;display:inline-block;",
            options: [
                {
                    text: "IP",
                    value: "ip"
                },
                {
                    text: "流量均衡",
                    value: "lb"
                },
                {
                    text: "网络映射",
                    value: "netmap"
                },
                {
                    text: "不用NAT",
                    value: "return"
                }
            ],
            value: "",
            functions: {
                onkeyup: "init_dest()",
                onchange: "init_dest()"
            }
        }, {
            enable: true,
            item_id: "div_dip",
            item_style:"width:100%",
            type: "text",
            id: "ip_d",
            name: "ip_d",
            label_style: "width:70px;display:inline-block;",
            value: "",
            label: "IP地址*",
            tip: "（IP地址，如192.168.1.1）",
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
            item_id: "div_diprange",
            item_style:"width:100%",
            type: "text",
            id: "lb_d",
            name: "lb_d",
            label_style: "width:70px;display:inline-block;",
            value: "",
            label: "IP范围*",
            tip: "（IP范围，192.168.1.1-192.168.1.22）",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check:'ip_range|',
                ass_check: function( check ) {

                }
            }
        }, {
            enable: true,
            item_id: "div_dipnet",
            item_style:"width:100%",
            type: "text",
            id: "ipnet_d",
            name: "ipnet_d",
            label_style: "width:70px;display:inline-block;",
            value: "",
            label: "IP子网*",
            tip: "（IP子网，192.168.1.0/24）",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check:'ip_mask|',
                ass_check: function( check ) {

                }
            }
        }, {
            enable: true,
            item_id: "div_dport",
            item_style:"width:100%",
            type: "text",
            id: "port_d",
            name: "port_d",
            value: "",
            label: "端口/范围",
            tip: "例如80，80:88",
            label_style: "width:70px;display:inline-block;",
            check: {
                type: "text",
                required: 0,
                check:'port|port_range',
                ass_check: function( check ) {

                }
            }
        }]
    }, {
        title: "启用",
        sub_items: [{
            enable: true,
            type: "checkbox",
            id: "enable",
            name: "enable",
            value: ""
        }]
    }, {
        title: "注释",
        sub_items: [{
            enable: true,
            type: "text",
            id: "note",
            name: "note",
            value: ""
        }]
    }]
};

var list_panel_render = {
    'source': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var source = data_item.source.split("&").join(",");
            result_render = source;
            return '<span>' + result_render + '</span>';
        }
    },
    'dest': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var dest = data_item.dest.split("&").join(",");
            result_render = dest;
            return '<span>' + result_render + '</span>';
        }
    },
    'server': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var pro = data_item.protocol.split("&").join("+");
            if(pro == ""){
                result_render = "<任意>";
            }else{
                result_render = pro;
            }
            if(data_item.dst_port){
                result_render += "/"+data_item.dst_port;
            }
            if(result_render == "/"){
                result_render = "";
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'ip_d': {
        render: function( default_rendered_text, data_item ) {
            var result_render = default_rendered_text;
            if(data_item.port_d){
                result_render = default_rendered_text+"("+data_item.port_d+")";
            }
            return result_render;
        }
    },
    'note': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.note){
                result_render = default_rendered_text
            }
            return '<div style="word-break:break-all;">' + result_render + '</div>';
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
            //return default_rendered_text;
            var src_toggle = "";
            var item_text = "";
            if(data_item.enable == "on"){
                src_toggle = "on.png";
                item_text = "禁用";
            }else{
                src_toggle = "off.png";
                item_text = "启用";
            }
            var action_buttons = [{
                enable: true,
                id: "toggle",
                name: "toggle",
                button_icon: src_toggle,
                button_text: item_text,
                value: data_item.id,
                functions: {
                    onclick: "function_click('"+data_item.enable+"',this.value);"
                }
            }, {
                enable: true,
                id: "edit_item",
                name: "edit_item",
                button_icon: "edit.png",
                button_text: "编辑",
                value: data_item.id,
                functions: {
                    onclick: "list_panel.edit_item(this.value);"
                }
            }, {
                enable: true,
                id: "delete_item",
                name: "delete_item",
                button_icon: "delete.png",
                button_text: "删除",
                value: data_item.id,
                functions: {
                    onclick: "list_panel.delete_item(this.value);"
                }
            }];
            
            var btn_up = {
                enable: true,
                id: "up_item",
                name: "up_item",
                button_icon: "up.png",
                button_text: "上移",
                value: data_item.id,
                functions: {
                    onclick: "up_item(this.value);"
                }
            }
            var btn_down = {
                enable: true,
                id: "down_item",
                name: "down_item",
                button_icon: "down.png",
                button_text: "下移",
                value: data_item.id,
                functions: {
                    onclick: "down_item(this.value);"
                }
            }
            
            if(data_item.id == "0" && list_panel.total_num > 1){
                action_buttons.unshift(btn_down);
            }else if(data_item.id == (list_panel.total_num-1) && list_panel.total_num > 1){
                action_buttons.unshift(btn_up);
            }else if(list_panel.total_num > 2){
                action_buttons.unshift(btn_down);
                action_buttons.unshift(btn_up);
            }

            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/double_nat.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_nat_list",         /* ***必填***，确定面板挂载在哪里 */
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
            "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": true,
            "type": "text",
            "title": "序号",        //一般text类型需要title,不然列表没有标题
            "name": "sequence",
            "width": "4%"
        }, {
            "enable": true,
            "type": "text",
            "title": "源",        //一般text类型需要title,不然列表没有标题
            "name": "source",
            "width": "12%"
        }, {
            "enable": true,
            "type": "text",
            "title": "目标",
            "name": "dest",
            "width": "12%"
        }, {
            "enable": true,
            "type": "text",
            "title": "服务",
            "name": "server",
            "width": "12%"
        }, {
            "enable": true,
            "type": "text",
            "title": "源NAT到",
            "name": "ip_r",
            "width": "12%"
        }, {
            "enable": true,
            "type": "text",
            "title": "目的NAT到",
            "name": "ip_d",
            "width": "12%"
        }, {
            "enable": true,
            "type": "text",
            "title": "注释",
            "name": "note",
            "width": "14%"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "16%"
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
    init_service();
    init_source();
    init_dest();
}
//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/double_nat.cgi",
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//动态加载服务项
function load_services(){
    var sending_data = {
        ACTION: "load_data_services"
    };

    function ondatareceived(data) {
        var services = data.data_services;
        for(var i=0;i<services.length;i++){
            $("#server").append("<option value="+services[i].port+"/"+services[i].protocol+">"+services[i].name+"</option>");
        }
    }
    do_request(sending_data, ondatareceived);
}
//动态为服务适配端口和协议
function init_service(){
    var val = $("#server").val();
    if(val == "any"){
        $("#protocol").val("any");
        $("#dst_port").hide();
        $("label[for = 'dst_port']").hide();
    }else if(val == "defined_byuser"){
        $("#protocol").val("any");
        $("#dst_port").show();
        $("label[for = 'dst_port']").show();
        $("#dst_port").val("");
    }else{
        var data_item = val.split("/");
        $("#protocol").val(data_item[1]);
        $("#dst_port").show();
        $("label[for = 'dst_port']").show();
        $("#dst_port").val(data_item[0]);
    }
}
//动态切换源转换
function init_source(){
    var val = $("#nat_type_r").val();
    if(val == "netmap"){
        $("#div_ipnet").show();
        $("#div_ip").hide();
    }else if(val == "ip"){
        $("#div_ip").show();
        $("#div_ipnet").hide();
    }else{
        $("#div_ip").hide();
        $("#div_ipnet").hide();
    }
}
//动态切换目的转换
function init_dest(){
    var val = $("#nat_type_d").val();
    if(val == "ip"){
        $("#div_dport").show();
        $("#div_dip").show();
        $("#div_diprange").hide();
        $("#div_dipnet").hide();
    }else if(val == "lb"){
        $("#div_dport").show();
        $("#div_diprange").show();
        $("#div_dip").hide();
        $("#div_dipnet").hide();
    }else if(val == "netmap"){
        $("#div_dport").show();
        $("#div_dipnet").show();
        $("#div_dip").hide();
        $("#div_diprange").hide();
    }else{
        $("#div_dipnet").hide();
        $("#div_dip").hide();
        $("#div_diprange").hide();
        $("#div_dport").hide();
    }
}
function function_click(val,id){
    if(val == "on"){
        list_panel.disable_item(id);
    }else{
        list_panel.enable_item(id);
    }
}
function down_item(id){
    var sending_data = {
        ACTION: "down_item",
        item_id:id
    };

    function ondatareceived(data) {
        list_panel.update_info(true);
    }
    list_panel.request_for_json( sending_data, ondatareceived );
}
function up_item(id){
    var sending_data = {
        ACTION: "up_item",
        item_id:id
    };

    function ondatareceived(data) {
        list_panel.update_info(true);
    }
    list_panel.request_for_json( sending_data, ondatareceived );
}