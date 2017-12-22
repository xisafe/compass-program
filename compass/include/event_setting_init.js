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
    $(".tr_crl_max,.event-level-class").hide();
});
var list_panel;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/event_setting.cgi",
    check_in_id: "mesg_box_event",
    panel_name: "my_message_box"
}
//设置最大值形式的阀值
var int_maxFlag ={
    'AbnormalNetThroughPut':200,
    'AbnormalCountConn':512
};
//设置高中低形式的阀值
var set_level ={
    'IPSEvent':true,
}


var message_manager;
var add_panel_config = {
    url: "/cgi-bin/event_setting.cgi",
    check_in_id: "panel_event_add",
    panel_name: "add_panel",
    rule_title: "事件设置",
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            // console.log(data_item);
            $('#tipValMax').hide()
            var index = data_item.val_max.indexOf("|");
            if(data_item.val_max == 0){ /*不需要阀值*/
                $("#tipValMax").prop("hidden", true);
				$("#tipValMax").next().removeClass("add-panel-even-line").addClass("add-panel-odd-line");
                 $("#tipValMax .add-panel-subtitle").text("阀值");
            }else if(index > -1){ /*高，中，低*/
                if(set_level[data_item.event_description]){
                    $("#low").parent().parent().show();
                    $("#low,#middle,#high").removeAttr('disabled');
                    
                    var arr = data_item.val_max.split("|");
                    $("#high").attr("checked",!!parseInt(arr[0]));
                    $("#middle").attr("checked",!!parseInt(arr[1]));
                    $("#low").attr("checked",!!parseInt(arr[2]));
                    
                    $("#val_max,#val_max_other,#val_max_flowmeter").attr("disabled","disabled");
                    $("#val_max,#val_max_other,#val_max_flowmeter").parent().hide();
                    $("#tipValMax .add-panel-subtitle").text("事件");
                    $('#tipValMax').show()
                }
            }else{ /*大于200 或者 512*/
                if(int_maxFlag[data_item.event_description] === 200){ /*阀值大于200*/
                    $("#val_max_other").parent().show();
                    $("#val_max_other").removeAttr("disabled");
                    $("#val_max_other").val(data_item.val_max);
                    
                    $("#val_max,#val_max_flowmeter,#low,#middle,#high").attr("disabled","disabled");
                    $("#val_max,#val_max_flowmeter").parent().hide();
                    $("#low").parent().parent().hide();
                }else if(int_maxFlag[data_item.event_description] === 512){
                    $("#val_max_flowmeter").parent().show();
                    $("#val_max_flowmeter").removeAttr("disabled");
                    $("#val_max_flowmeter").val(data_item.val_max);

                    $("#val_max,#val_max_other,#low,#middle,#high").attr("disabled","disabled");
                    $("#val_max,#val_max_other").parent().hide();
                    
                    $("#low").parent().parent().hide();
                }else{
                    $("#val_max").parent().show();
                    $("#val_max").removeAttr("disabled");
                    $("#val_max_other,#val_max_flowmeter,#low,#middle,#high").attr("disabled","disabled");
                    $("#val_max_other,#val_max_flowmeter").parent().hide(); 
                    $("#low").parent().parent().hide();
                }
                $('#tipValMax').show()
                $("#tipValMax").prop("hidden", false);
				$("#tipValMax").next().removeClass("add-panel-odd-line").addClass("add-panel-even-line");
                 $("#tipValMax .add-panel-subtitle").text("阀值");
            }

        },
        after_load_data: function( add_obj,data_item ) {
            //编辑时将事件描述替换为中文
            if(data_item.event_description == "LogDiskFull"){
                $("#event_description").val("日志磁盘使用率过高");
            }else if(data_item.event_description == "DiskFull"){
                $("#event_description").val("磁盘使用率过高");
            }else if(data_item.event_description == "IPSEvent"){
                $("#event_description").val("IPS");
            }else if(data_item.event_description == "VirusEvent"){
                $("#event_description").val("病毒防御");
            }else if(data_item.event_description == "CpuusageFull"){
                $("#event_description").val("CPU利用率过高");
            }else if(data_item.event_description == "MEMusageFull"){
                $("#event_description").val("内存利用率过高");
            }else if(data_item.event_description == "TemperatureFull"){
                $("#event_description").val("CPU温度过高");
            }else if(data_item.event_description == "UplinkOff"){
                $("#event_description").val("上行线路接口断开");
            }else if(data_item.event_description == "LANOff"){
                $("#event_description").val("LAN区接口断开");
            }else if(data_item.event_description == "DMZOff"){
                $("#event_description").val("DMZ区接口断开");
            }else if(data_item.event_description == "UplinkFailure"){
                $("#event_description").val("上行线路失效");
            }else if(data_item.event_description == "AbnormalCountConn"){

                $("#event_description").val("连接数异常");
            }else if(data_item.event_description == "AbnormalNetThroughPut"){
                $("#event_description").val("流量异常");
            }else if(data_item.event_description == "AdminLoginFailure"){
                $("#event_description").val("管理员登录失败");
            }
        },
        before_save_data:function(add_obj, sending_data){
            // var temp,captrue,reg = /\S+&?(?:(high=\d+)?(&middle=\d+)?(&middle=\d+)?)&?\S+/;
            // sending_data.replace(reg,function(all,c){
            //     captrue += c;
            //     temp =  c.replace(/(&?[a-z]+=)/g,"|").replace("|","val_max=");
            // })
            // sending_data = sending_data.replace(captrue,temp);
            if(!$("#low,#middle,#high").attr("disabled")){
                var high = ($("#high").prop("checked")) ? 1:0 ;
                var middle = ($("#middle").prop("checked")) ? 1:0 ;
                var low = ($("#low").prop("checked")) ? 1:0 ;
                var temp_str = 'val_max=' +high + "|" +middle + "|" + low ;
                sending_data += "&"+ temp_str;
            }
            
    
            return sending_data.replace(/val_max_other|val_max_flowmeter/g,'val_max');
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "事件描述",
            cls: "tr_crl_description",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    disabled: true,
                    id: "event_description",
                    name: "event_description",
                    value: "",
                    check: {
                        type: "text",
                        required: 0,
                        check: 'note|'
                    }
                }
            ]
        },
        {
            title: "告警方式",
            sub_items: [
                {
                    enable: true,
                    type: "items_group",
                    name: "alarm_type",
                    sub_items: [
                        {
                            enable: true,
                            type: "checkbox",
                            label: "记录日志",
                            disabled: true,
                            split: "+",
                            id: "alarm_type",
                            name: "alarm_type",
                            checked: true,
                            value: "log",
                            functions: {
                                onclick: "return false;"
                            }
                        }, {
                            enable: true,
                            type: "checkbox",
                            label: "预警",
                            split: "+",
                            id: "alarm_type",
                            name: "alarm_type",
                            value: "voice"
                        }, {
                            enable: true,
                            type: "checkbox",
                            label: "邮件告警",
                            split: "+",
                            id: "alarm_type",
                            name: "alarm_type",
                            value: "mail"
                        }, {
                            enable: true,
                            type: "checkbox",
                            label: "短信告警",
                            split: "+",
                            id: "alarm_type",
                            name: "alarm_type",
                            value: "message"
                        }
                    ]
                }
            ]
        }, {
            title: "阀值",
            cls: "tr_crl_max",
			id: "tipValMax",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "val_max", /*日志磁盘，磁盘使用率 针对显示百分比*/
                    name: "val_max",
                    style: "width:30px",
                    tip: "（80-100,默认值：90）",
                    tip_id: "tip_val_max",
                    value: "",
                    check: {
                        type: "text",
                        required: 1,
                        check: 'int|',
                        ass_check: function( check ) {
                            // console.log(check);
                            var val = $("#val_max").val();
                            if(val < 80 || val > 100){
                                if(val == 0){
                                    return "";
                                }else{
                                    return "请设置80-100之间的数值";
                                }
                            }
                        }
                    }
                },
                {
                    enable: true,
                    type: "text",
                    id: "val_max_flowmeter", /*链接数异常 针对显示200以上的值*/
                    name: "val_max_flowmeter",
                    style: "width:100px",
                    tip:"(请设置大于200的整数)",
                    value: "",
                    check: {
                        type: "text",
                        required: 1,
                        check: 'int|',
                        ass_check: function( check ) {
                            // console.log(check);
                            var val = $("#val_max_flowmeter").val();
                            if(val < 200 ){
                                    return "请设置大于200的整数";
                                
                            }
                        }
                    }
                },{
                    enable: true,
                    type: "text",
                    id: "val_max_other",  /*关于流量异常*/
                    name: "val_max_other",
                    style: "width:100px",
                    tip:"KB/s (请设置大于等于512的整数)",
                    value: "",
                    check: {
                        type: "text",
                        required: 1,
                        check: 'int|',
                        ass_check: function( check ) {
                            // console.log(check);
                            var val = $("#val_max_other").val();
                            if(val < 512 ){
                                    return "请设置大于等于512的整数";
                                
                            }
                        }
                    }
                },{
                    enable: true,
                    type: "items_group",
                    name: "event_level", /*ips 针对选择高中低*/
                    cls:"event-level-class",
                    style:"margin:-5px;",
                    sub_items: [{
                            enable: true,
                            type: "checkbox",
                            label: "高",
                            tip:"",
                            split: "|",
                            id: "high",
                            value:1,
                           
                            
                        },{
                            enable: true,
                            type: "checkbox",
                            label: "中",
                            split: "|",
                            id: "middle",
                            value:1,
                           
                           
                        },{
                            enable: true,
                            type: "checkbox",
                            label: "低",
                            split: "|",
                            id: "low",
                            value:1,
                           
                        }]
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

var list_panel_render = {
    'event_description': {
        render: function( default_rendered_text, data_item ) {

            if(default_rendered_text == "LogDiskFull"){
                default_rendered_text = "日志磁盘使用率过高（阀值："+data_item.val_max+"%）";
            }else if(data_item.event_description == "DiskFull"){
                default_rendered_text = "磁盘使用率过高（阀值："+data_item.val_max+"%）"
            }else if(data_item.event_description == "IPSEvent"){
                var arr = data_item.val_max.split("|");
               default_rendered_text = "IPS";
            }else if(data_item.event_description == "VirusEvent"){
                default_rendered_text = "病毒防御";
            }else if(default_rendered_text == "CpuusageFull"){
                default_rendered_text = "CPU利用率过高（阀值："+data_item.val_max+"%）";
            }else if(default_rendered_text == "MEMusageFull"){
                default_rendered_text = "内存利用率过高（阀值："+data_item.val_max+"%）";
            }else if(default_rendered_text == "TemperatureFull"){
                default_rendered_text = "CPU温度过高（阀值："+data_item.val_max+"%）";
            }else if(default_rendered_text == "UplinkOff"){
                default_rendered_text = "上行线路接口断开";
            }
            else if(default_rendered_text == "LANOff"){
                default_rendered_text = "LAN区接口断开";
            }
            else if(default_rendered_text == "DMZOff"){
                default_rendered_text = "DMZ区接口断开";
            }
            else if(default_rendered_text == "UplinkFailure"){
                default_rendered_text = "上行线路失效";
            }else if(default_rendered_text == "AbnormalCountConn"){
                default_rendered_text = "连接数异常（阀值："+data_item.val_max+"）";
            }else if(default_rendered_text == "AbnormalNetThroughPut"){
                default_rendered_text = "流量异常（阀值："+data_item.val_max+"KB/s）";
            }else if(default_rendered_text == "AdminLoginFailure"){
                default_rendered_text = "管理员登录失败";
            }
            return '<span>' + default_rendered_text + '</span>';
        }
    },
    'alarm_type': {
        render: function( default_rendered_text, data_item ) {
            var temp_arr = default_rendered_text.split("+");
            //var result_arr = [];
            for(var i = 0;i < temp_arr.length;i++){
                if(temp_arr[i] == "log"){
                    temp_arr[i] = "记录日志";
                    //result_arr.push(temp_arr[i]);
                }else if(temp_arr[i] == "mail"){
                    temp_arr[i] = "邮件告警";
                    //result_arr.push(temp_arr[i]);
                }else if(temp_arr[i] == "voice"){
                    temp_arr[i] = "预警";
                    //result_arr.push(temp_arr[i]);
                }else if(temp_arr[i] == "message"){
                    temp_arr[i] = "短信告警";
                    //result_arr.push(temp_arr[i]);
                }
            }
            var result_render = temp_arr.join("+")
            return '<span>' + result_render + '</span>';
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/event_setting.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_event_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 11,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
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
            "title": "事件描述",        //一般text类型需要title,不然列表没有标题
            "name": "event_description",
            "width": "40%"
        }, {
            "enable": true,
            "type": "text",
            "title": "告警方式",
            "name": "alarm_type",
            "width": "40%"
        },{
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "td_class":"align-center",
            "width": "15%"
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
            enable: false,
            button_icon: "add16x16.png",
            button_text: "添加规则",
            functions: {
                onclick: "add_rule(this);"
            }
        },
        {
            "enable": false,
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
    is_default_search: false           /* ===可选===，默认是true，控制默认的搜索条件 */
    
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
}
