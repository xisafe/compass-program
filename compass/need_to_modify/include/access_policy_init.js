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
    init_dest();
    init_source();
    //init_auth();
    init_access_policy();
    init_limit_time();
    
    list_panel.update_info(true);
});
var list_panel;
var add_panel;

var arr_filter_templates = [];

var message_box_config = {
    url: "/cgi-bin/access_policy.cgi",
    check_in_id: "mesg_box_policy",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/access_policy.cgi",
    check_in_id: "panel_policy_add",
    panel_name: "add_panel",
    rule_title: "访问策略",
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,sending_data ) {
            /* if($("input[name='browser']:checked").length < 1){
                message_manager.show_popup_error_mesg("请至少选择一种浏览器");
                return false;
            } */
            if($("#enable_time_limit").is(":checked")){
                if($("input[name='live_days']:checked").length < 1){
                    message_manager.show_popup_error_mesg("请选择活跃天数");
                    return false;
                }
                var arr_live_days = [];
                $("input[name='live_days']:checked").each(function(){
                    arr_live_days.push(this.value);
                });
                sending_data.live_days_save = arr_live_days.join("|");
            }
        },
        before_load_data: function( add_obj,data_item ) {
            init_data_limit_time();
        },
        after_load_data: function( add_obj,data_item ) {
            init_dest();
            init_source();
            //init_auth();
            init_access_policy();
            //初始化文件类型
            if(data_item.file_type){
                var ftypes = data_item.file_type.split("&");
                for(var i=0;i<ftypes.length;i++){
                    var id = "#"+ftypes[i].replace(/\./,"");
                    $(id).attr("checked",true);
                }
            }
            init_limit_time();
            //init_data_limit_time();
            //var alive_days = data_item.live_days.split("");
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "策略名称*",
        sub_items: [{
            enable: true,
            type: "text",
            id: "policy_name",
            name: "policy_name",
            maxlength: "20",
            check: {
                type: "text",
                required: 1,
                check:'name|'
            }
        }]
    }, {
        title: "源*",
        sub_items: [{
            enable: true,
            style: "width:100px;",
            item_style:"width:25%",
            type: "select",
            id: "type_r",
            name: "type_r",
            label: "源类型*",
            label_style: "width:70px;display:inline-block;",
            options: [{
                text: "<任意>",
                value: "any"
            }, {
                text: "区域",
                value: "zone"
            }, {
                text: "网络/IP",
                value: "ip"
            }, {
                text: "MAC",
                value: "mac"
            }],
            functions: {
                onkeyup: "init_source()",
                onchange: "init_source()"
            }
        }, {
            enable: true,
            item_id: "div_any",
            item_style:"width:60%",
            type: "label",
            id: "any_r",
            name: "any_r",
            value: "规则将匹配所有源"
        }, {
            enable: true,
            item_id: "div_zone",
            item_style: "width:60%;display:inline-block;",
            type: "select",
            id: "source_zone",
            name: "source_zone",
            label: "选择源区域*",
            label_style: "width:100px;display:inline-block;",
            check: {
                type: "select-one",
                required: 1
            },
            multiple: true
        }, {
            enable: true,
            item_id: "div_ip",
            item_style:"width:60%;;display:inline-block;",
            type: "textarea",
            id: "ip_r",
            name: "ip_r",
            label: "插入源的 网络/IP*",
            label_style: "width:120px;display:inline-block;",
            check: {
                type: "textarea",
                required: 1,
                check:'ip|ip_mask|'
            }
        }, {
            enable: true,
            item_id: "div_mac",
            item_style:"width:60%;display:inline-block;",
            type: "textarea",
            id: "mac_r",
            name: "mac_r",
            label: "插入源的 MAC地址*",
            label_style: "width:120px;display:inline-block;",
            check: {
                type: "textarea",
                required: 1,
                check:'mac|'
            }
        }]
    }, {
        title: "目标*",
        sub_items: [{
            enable: true,
            style: "width:100px;",
            item_style:"width:25%",
            type: "select",
            id: "type_d",
            name: "type_d",
            label: "源类型*",
            label_style: "width:70px;display:inline-block;",
            options: [{
                text: "<任意>",
                value: "any"
            }, {
                text: "区域",
                value: "zone"
            }, {
                text: "网络/IP",
                value: "ip"
            }, {
                text: "域",
                value: "domain"
            }],
            functions: {
                onkeyup: "init_dest()",
                onchange: "init_dest()"
            }
        }, {
            enable: true,
            item_id: "div_any_d",
            item_style:"width:60%",
            type: "label",
            id: "any_r",
            name: "any_r",
            value: "规则将匹配任何目标"
        }, {
            enable: true,
            item_id: "div_zone_d",
            item_style:"width:60%;display: inline-block;",
            type: "select",
            id: "dest_zone",
            name: "dest_zone",
            label: "选择目标区域*",
            label_style: "width:100px;display:inline-block;",
            check: {
                type: "select-one",
                required: 1
            },
            multiple: true
        }, {
            enable: true,
            item_id: "div_ip_d",
            item_style:"width:60%;display: inline-block;",
            type: "textarea",
            id: "ip_d",
            name: "ip_d",
            label: "插入目的 网络/IP*",
            label_style: "width:120px;display:inline-block;",
            check: {
                type: "textarea",
                required: 1,
                check:'ip|ip_mask|'
            }
        }, {
            enable: true,
            item_id: "div_domain_d",
            item_style:"width:60%;display:inline-block;",
            type: "textarea",
            id: "domain_d",
            name: "domain_d",
            label: "插入域*",
            label_style: "width:120px;display:inline-block;",
            check: {
                type: "textarea",
                required: 1,
                check:'domain|'
            }
        }]
    },
    /* {
        title: "身份认证",
        sub_items: [{
            enable: true,
            style: "width:100px;",
            item_style:"width:30%",
            type: "select",
            id: "auth_type",
            name: "auth_type",
            label: "身份认证",
            label_style: "width:70px;display:inline-block;",
            tip: "",
            options: [{
                    text: "禁用",
                    value: "none"
                }, {
                    text: "基于用户的",
                    value: "user"
                }, {
                    text: "基于组的",
                    value: "group"
                },
            ],
            value: "",
            functions: {
                onkeyup: "init_auth();",
                onchange: "init_auth();"
            }
        }, {
            enable: true,
            item_id: "div_user",
            item_style:"width:60%;display: inline-block;",
            type: "select",
            id: "user",
            name: "user",
            value: "",
            label: "允许的用户",
            label_style: "width:100px;display:inline-block;",
            options: [
                
            ],
            functions: {
            },
            check: {
                type: "select-one",
                required: 0,
                ass_check: function( check ) {

                }
            },
            multiple: true
        }, {
            enable: true,
            item_id: "div_group",
            item_style:"width:60%;display: inline-block;",
            type: "select",
            id: "group",
            name: "group",
            value: "",
            label: "允许的组",
            label_style: "width:100px;display:inline-block;",
            options: [
            ],
            functions: {
            },
            check: {
                type: "select-one",
                required: 0,
                ass_check: function( check ) {

                }
            },
            multiple: true
        }]
    }, */
    {
        title: "时间限制",
        sub_items: [{
            enable: true,
            item_style:"width:10%",
            type: "checkbox",
            id: "enable_time_limit",
            name: "enable_time_limit",
            label: "启用",
            functions: {
                onclick: "init_limit_time();"
            }
        }, {
            enable: true,
            label: "活跃天数：",
            type: "items_group",
            item_id: "div_live_days",
            item_style: "width:40%;", 
            sub_items: [{
                enable: true,
                type: "checkbox",
                name: "live_days",
                value: "M",
                label: "周一"
            }, {
                enable: true,
                type: "checkbox",
                name: "live_days",
                value: "T",
                label: "周二"
            }, {
                enable: true,
                type: "checkbox",
                name: "live_days",
                value: "W",
                label: "周三"
            }, {
                enable: true,
                type: "checkbox",
                name: "live_days",
                value: "H",
                label: "周四"
            }, {
                enable: true,
                type: "checkbox",
                name: "live_days",
                value: "F",
                label: "周五"
            }, {
                enable: true,
                type: "checkbox",
                name: "live_days",
                value: "A",
                label: "周六"
            }, {
                enable: true,
                type: "checkbox",
                name: "live_days",
                value: "S",
                label: "周日"
            }]
        }, {
            enable: true,
            label: "不能跨天输入,时间格式如00:01",
            type: "items_group",
            id:"time",
            item_id: "div_time",
            item_style: "width:30%;",
            sub_items: [{
                enable: true,
                type: "select",
                style: "width:50px;",
                name: "start_hour",
                id: "start_hour",
                label:"起始时间:",
                tip: ":",
                check: {
                    type: "select-one",
                    required: 1,
                    check:'other',
                    other_reg:'!/^\$/'
                }
            }, {
                enable: true,
                type: "select",
                style: "width:50px;",
                name: "start_min",
                id: "start_min",
                check: {
                    type: "select-one",
                    required: 1,
                    check:'other',
                    other_reg:'!/^\$/'
                }
            }, {
                enable: true,
                type: "select",
                style: "width:50px;",
                name: "end_hour",
                id: "end_hour",
                label:"结束时间:",
                tip: ":",
                check: {
                    type: "select-one",
                    required: 1,
                    check:'other',
                    other_reg:'!/^\$/',
                    ass_check: function( check ) {
                        var mesg = "";
                        var start_hour = $("#start_hour").val();
                        var end_hour = $("#end_hour").val();
                        if(start_hour > end_hour){
                            mesg = "结束时间应大于起始时间";
                        }
                        return mesg;
                    }
                }
            }, {
                enable: true,
                type: "select",
                style: "width:50px;",
                name: "end_min",
                id: "end_min",
                check: {
                    type: "select-one",
                    required: 1,
                    check:'other',
                    other_reg:'!/^\$/',
                    ass_check: function( check ) {
                        var mesg = "";
                        var start_hour = $("#start_hour").val();
                        var end_hour = $("#end_hour").val();
                        var start_min = $("#start_min").val();
                        var end_min = $("#end_min").val();
                        if(start_hour == end_hour){
                            if(start_min >= end_min){
                                mesg = "结束时间应大于起始时间";
                            }
                        }
                        return mesg;
                    }
                }
            }]
        }]
    },
    /* {
        title: "使用浏览器",
        sub_items: [{
            enable: true,
            label: "",
            type: "items_group",
            tip: "",
            id:"browser",
            cls: "",
            item_style: "width:100%;", 
            sub_items: [{
                enable: true,
                type: "checkbox",
                name: "browser",
                value: "MSIE",
                label: "Internet Explorer",
                checked: false,
                functions: {
                    onclick: ""
                }
            }, {
                enable: true,
                type: "checkbox",
                name: "browser",
                value: "FIREFOX",
                label: "Firefox",
                checked: false,
                functions: {
                    onclick: ""
                }
            }, {
                enable: true,
                type: "checkbox",
                name: "browser",
                value: "NETSCAPE",
                label: "Netscape",
                checked: false,
                functions: {
                    onclick: ""
                }
            }, {
                enable: true,
                type: "checkbox",
                name: "browser",
                value: "OPERA",
                label: "Opera",
                checked: false,
                functions: {
                    onclick: ""
                }
            }, {
                enable: true,
                type: "checkbox",
                name: "browser",
                value: "SAFARI",
                label: "safari",
                checked: false,
                functions: {
                    onclick: ""
                }
            }, {
                enable: true,
                type: "checkbox",
                name: "browser",
                value: "GOOGLE",
                label: "google Toobar",
                checked: false,
                functions: {
                    onclick: ""
                }
            }]
        }]
    }, */
    {
        title: "访问策略",
        sub_items: [{
            enable: true,
            style: "width:100px;",
            item_style:"width:30%",
            type: "select",
            id: "access_policy",
            name: "access_policy",
            options: [{
                text: "过滤模板",
                value: "allow"
            }, {
                text: "文件类型过滤",
                value: "deny"
            }],
            functions: {
                onkeyup: "init_access_policy();",
                onchange: "init_access_policy();"
            }
        }, {
            enable: true,
            item_id: "div_allow",
            item_style:"width:50%",
            type: "select",
            id: "filter_template",
            name: "filter_template",
            options: [
                /* {
                    text: "不做任何检测",
                    value: "none",
                },
                {
                    text: "只检测病毒",
                    value: "havp",
                } */
            ],
            functions: {
                onkeyup: "",
                onchange: ""
            }
        }, {
            enable: true,
            type: "label",
            item_id: "div_deny",
            id: "btn_deny",
            name: "btn_deny",
            value: "<a style='text-decoration:underline;cursor:pointer;' id='setting_deny'>设置</a>",
            functions: {
                onclick: "show_panel_ftype();"
            }
        }, {
            enable: true,
            type: "text",
            style: "display:none;",
            id: "file_type",
            name: "file_type"
        }]
    }, {
        title: "启用策略",
        sub_items: [{
            enable: true,
            type: "checkbox",
            label: "启用",
            id: "enable",
            name: "enable",
            checked: true
        }]
    }, {
        title: "位置",
        sub_items: [{
            enable: true,
            type: "select",
            id: "position",
            name: "position",
            functions: {
                onkeyup: "",
                onchange: ""
            }
        }]
    }]
};

var list_panel_render = {
    'start_time': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var live_days = data_item.live_days.split("|");
            var live_days_display = [];
            for(var i=0;i<live_days.length;i++){
                var item = "";
                if(live_days[i] == "M"){
                    item = "周一";
                }else if(live_days[i] == "T"){
                    item = "周二";
                }else if(live_days[i] == "W"){
                    item = "周三";
                }else if(live_days[i] == "H"){
                    item = "周四";
                }else if(live_days[i] == "F"){
                    item = "周五";
                }else if(live_days[i] == "A"){
                    item = "周六";
                }else if(live_days[i] == "S"){
                    item = "周日";
                }
                live_days_display.push(item);
            }
            result_render = live_days_display.join(",");
            if(data_item.start_hour){
                result_render += data_item.start_hour+":"+data_item.start_min+"--"+
                                data_item.end_hour+":"+data_item.end_min;
            }else{
                result_render = "总是";
            }
            return result_render;
        }
    },
    'auth_type': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text == "none"){
                result_render = "无";
            }else if(default_rendered_text == "user"){
                result_render = "基于用户";
            }else{
                result_render = "基于组";
            }
            return result_render;
        }
    },
    'filter_template': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.access_policy == "deny"){
                result_render = "文件类型过滤";
            }else{
                if(default_rendered_text == "havp"){
                    result_render = "只检测病毒";
                }else if(default_rendered_text == "none"){
                    result_render = "不做任何检测";
                }else if(default_rendered_text == "content1"){
                    result_render = "默认策略";
                }else{
                    //result_render = default_rendered_text;
                    for(var i=0;i<arr_filter_templates.length;i++){
                        if(default_rendered_text == arr_filter_templates[i].VALUE){
                            result_render = arr_filter_templates[i].NAME;
                            break;
                        }
                    }
                }
            }
            return result_render;
        }
    },
    'source': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if( data_item.type_r == "any"){
                result_render = "任意";
            }else{
                if(default_rendered_text == "ORANGE"){
                    result_render = "DMZ区";
                }else if(default_rendered_text == "GREEN"){
                    result_render = "LAN区";
                }else if(default_rendered_text == "BLUE"){
                    result_render = "WAN区";
                }else{
                    result_render = default_rendered_text;
                }
            }
            return result_render;
        }
    },
    'dest': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if( data_item.type_d == "any"){
                result_render = "任意";
            }else{
                if(default_rendered_text == "ORANGE"){
                    result_render = "DMZ区";
                }else if(default_rendered_text == "GREEN"){
                    result_render = "LAN区";
                }else if(default_rendered_text == "BLUE"){
                    result_render = "WAN区";
                }else{
                    result_render = default_rendered_text;
                }
            }
            return result_render;
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/access_policy.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_policy_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    event_handler: {
        before_load_data: function( list_obj ) {
            
        },
        after_load_data: function ( list_obj, response ) {
            $("#source_zone").empty();
            $("#dest_zone").empty();
            $("#position").empty();
            $("#user").empty();
            $("#group").empty();
            
            arr_filter_templates = response.filter_templates;
            
            for(var i=0;i<response.useable_zones.length;i++){
                $("#source_zone").append("<option value="+response.useable_zones[i].value+">"+response.useable_zones[i].display+"</option>");
                $("#dest_zone").append("<option value="+response.useable_zones[i].value+">"+response.useable_zones[i].display+"</option>");
            }
            var lines = response.detail_data;
            $("#position").append("<option value='0'>首位置</option>");
            if(lines.length > 0){
                for(var j=1;j<lines.length;j++){
                    $("#position").append("<option value="+lines[j].id+">位置"+lines[j].id+"</option>");
                }
                $("#position").append("<option value='last' selected>末位置</option>");
            }
            //加载用户和组的数据
            for(var n=0;n<response.users.length;n++){
                $("#user").append("<option value="+response.users[n]+">"+response.users[n]+"</option>");
            }
            for(var m=0;m<response.groups.length;m++){
                $("#group").append("<option value="+response.groups[m]+">"+response.groups[m]+"</option>");
            }
            //加载过滤模板
            $("#filter_template").empty();
            $("#filter_template").append("<option value='none'>不做任何检测</option>");
            if(response.is_active_havp == "yes"){
                $("#filter_template").append("<option value='havp'>只检测病毒</option>");
            }
            $("#filter_template").append("<option value='content1'>默认策略</option>");
            for(var k=0;k<response.filter_templates.length;k++){
                $("#filter_template").append("<option value="+response.filter_templates[k].VALUE+">"+response.filter_templates[k].NAME+"</option>");
            }
        }
    },
    panel_header: [{                /* ***必填***，控制数据的加载以及表头显示 */
        "enable": true,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //用户装载数据之用
        "cls": "",                  //元素的class
        "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "3%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
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
        "title": "策略名称",        //一般text类型需要title,不然列表没有标题
        "name": "policy_name",
        "width": "14%"
    }, {
        "enable": true,
        "type": "text",
        "title": "源",
        "name": "source",
        "width": "21%"
    }, {
        "enable": true,
        "type": "text",
        "title": "目标",
        "name": "dest",
        "width": "21%"
    },/* {
        "enable": true,
        "type": "text",
        "title": "认证方式",
        "name": "auth_type",
        "width": "12%"
    }, */{
        "enable": true,
        "type": "text",
        "title": "开启时间",
        "name": "start_time",
        "width": "14%"
    },/* {
        "enable": true,
        "type": "text",
        "title": "浏览器",
        "name": "browser",
        "width": "14%"
    }, */{
        "enable": true,
        "type": "text",
        "title": "访问策略",
        "name": "filter_template",
        "width": "14%"
    }, {
        "enable": true,
        "type": "action",
        "title": "活动/动作",
        "name": "action",
        "width": "10%"
    }],
    top_widgets: [{                 /* ===可选=== */
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
        "cls": "",
        "button_icon": "delete.png",
        "button_text": "删除选中",
        "functions": {
            onclick: "delete_selected_items(this)"
        }
    }],
    bottom_widgets: [{               /* ===可选=== */
        "enable": false,
        "id": "export_selected",
        "name": "export_selected",
        "cls": "",
        "button_icon": "download.png",
        "button_text": "导出选中",
        "functions": {
            onclick: "export_selected_items(this)"
        }
    }, {
        "enable": false,
        "id": "delete_all_logs",
        "name": "delete_all_logs",
        "cls": "",
        "button_icon": "delete.png",
        "button_text": "清空日志",
        "functions": {
            onclick: "delete_all_logs(this)"
        }
    }],
    is_default_search: true          /* ===可选===，默认是true，控制默认的搜索条件 */
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
    init_dest();
    init_source();
    init_access_policy();
    init_limit_time();
    init_data_limit_time();
}
//按源类型切换展示区
function init_source(){
    var type_r = $("#type_r").val();
    if(type_r == "any"){
        $("#div_any").show();
        $("#div_zone").hide();
        $("#div_ip").hide();
        $("#div_mac").hide();
    }else if(type_r == "zone"){
        $("#div_any").hide();
        $("#div_zone").show();
        $("#div_ip").hide();
        $("#div_mac").hide();
    }else if(type_r == "ip"){
        $("#div_any").hide();
        $("#div_zone").hide();
        $("#div_ip").show();
        $("#div_mac").hide();
    }else{
        $("#div_any").hide();
        $("#div_zone").hide();
        $("#div_ip").hide();
        $("#div_mac").show();
    }
}
function init_dest(){
    var type_d = $("#type_d").val();
    if(type_d == "any"){
        $("#div_any_d").show();
        $("#div_zone_d").hide();
        $("#div_ip_d").hide();
        $("#div_domain_d").hide();
    }else if(type_d == "zone"){
        $("#div_any_d").hide();
        $("#div_zone_d").show();
        $("#div_ip_d").hide();
        $("#div_domain_d").hide();
    }else if(type_d == "ip"){
        $("#div_any_d").hide();
        $("#div_zone_d").hide();
        $("#div_ip_d").show();
        $("#div_domain_d").hide();
    }else{
        $("#div_any_d").hide();
        $("#div_zone_d").hide();
        $("#div_ip_d").hide();
        $("#div_domain_d").show();
    }
}
//切换访问策略
function init_access_policy(){
    var access_policy = $("#access_policy").val();
    if(access_policy == "allow"){
        $("#div_allow").show();
        $("#div_deny").hide();
    }else{
        $("#div_allow").hide();
        $("#div_deny").show();
    }
}
//切换身份认证
function init_auth(){
    var auth = $("#auth_type").val();
    if(auth == "user"){
        $("#div_user").show();
        $("#div_group").hide();
    }else if(auth == "group"){
        $("#div_user").hide();
        $("#div_group").show();
    }else{
        $("#div_user").hide();
        $("#div_group").hide();
    }
}
//初始换时间限制
function init_limit_time(){
    if($("#enable_time_limit").is(":checked")){
        $("#div_live_days").show();
        $("#div_time").show();
    }else{
        $("#div_live_days").hide();
        $("#div_time").hide();
    }
}
//显示文件显示列表
function show_panel_ftype(){
    $("#cover_filetype_list").show();
    $("#panel_filetype_list").show();
}
//关闭文件类型显示列表
function close_panel_ftype(){
    $("#panel_filetype_list").hide();
    $("#cover_filetype_list").hide();
}
//树形操作
function toogle(e){
    var html_pre = e.innerHTML;
    if(document.getElementById(e.title).style.display == "none"){
        document.getElementById(e.title).style.display = "block";
        html_pre =  html_pre.replace("+","-");
    }else{
        document.getElementById(e.title).style.display = "none";
        html_pre =  html_pre.replace("-","+");
    }
    e.innerHTML = html_pre;
}
//选择文件类型
function select_ftype_all(e){
    if(e.checked){
        $("."+e.value).attr("checked",true);
    }else{
        $("."+e.value).removeAttr("checked");
    }
}
//保存所选文件类型
function save_ftype(){
    var checked_items_id = new Array();
    $(".ctr_ftype:checked").each(function(){
        checked_items_id.push(this.value);
    });

    var ids = checked_items_id.join( "&" );
    $("#file_type").val(ids);
    close_panel_ftype();
}
//初始化起始时间数据
function init_data_limit_time(){
    $("#start_hour").empty();
    $("#end_hour").empty();
    $("#start_min").empty();
    $("#end_min").empty();
    for(var i=0;i<24;i++){
        if(i<10){
            var hour = "0"+i;
            $("#start_hour").append("<option value="+hour+">"+hour+"</option>");
            $("#end_hour").append("<option value="+hour+">"+hour+"</option>");
        }else{
            $("#start_hour").append("<option value="+i+">"+i+"</option>");
            $("#end_hour").append("<option value="+i+">"+i+"</option>");
        }
    }
    for(var i=0;i<60;i++){
        if(i<10){
            var min = "0"+i;
            $("#start_min").append("<option value="+min+">"+min+"</option>");
            $("#end_min").append("<option value="+min+">"+min+"</option>");
        }else{
            $("#start_min").append("<option value="+i+">"+i+"</option>");
            $("#end_min").append("<option value="+i+">"+i+"</option>");
        }
    }
}