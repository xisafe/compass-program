$(document).ready(function(){
    SrcUserlist_panel.render();
    message_manager.render();
    SrcUserlist_panel.hide();
    DesUserlist_panel.render();
    DesUserlist_panel.hide();
    Appid_panel.render();
    (function (){
        var img = $('<img title="重置" src="/images/reconnect.png">');
        img.css({
            cursor: "pointer",
            position: "relative",
            top: "3px",
            left: "10px"
        });
        img.on("click", function() {
            $("#for_appJstree-qosrule").jstree().deselect_all();
        })
        $("#list_panel_id_for_Appid_panel .list-panel-title").find("span").after(img);
    })();
    Appid_panel.hide();
    toggle_policy(document.getElementById("dst_dev"));
});
var dst_dev_options;
//用户组配置面板
var ass_url = '/cgi-bin/qosrules.cgi';
var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}
var SrcUserlist_config = {
    url: ass_url,
    check_in_id: "SrcUserlist_panel",
    panel_name: "SrcUserlist_panel",
    page_size: 0,
    panel_title: "配置用户组",
    is_panel_stretchable:true,
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    is_first_load: true,
    // render: monitoring_object_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
                
        },
        after_load_data: function( list_obj,data_item ) {
           
        }
    },
    panel_header: [{
        enable: false,
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: false,
        type: "text",
        title: "用户组",
        name: "user_name"
    }],
    bottom_extend_widgets: {
        class: "add-panel-footer",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_userlist('SrcUserlist','#for_jstree-qosrule',SrcUserlist_panel);"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "SrcUserlist_panel.hide();"
            }
        }]
    }
};
var SrcUserlist_panel = new PagingHolder(SrcUserlist_config);
var message_manager = new MessageManager( message_box_config );
var DesUserlist_config = {
    url: ass_url,
    check_in_id: "DesUserlist_panel",
    panel_name: "DesUserlist_panel",
    page_size: 0,
    panel_title: "配置用户组",
    is_panel_stretchable:true,
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    is_first_load: true,
    // render: monitoring_object_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
                
        },
        after_load_data: function( list_obj,data_item ) {
           
        }
    },
    panel_header: [{
        enable: false,
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: false,
        type: "text",
        title: "用户组",
        name: "user_name"
    }],
    bottom_extend_widgets: {
        class: "add-panel-footer",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_userlist('DesUserlist','#for_des_jstree-qosrule',DesUserlist_panel);"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "DesUserlist_panel.hide();"
            }
        }]
    }
};
var DesUserlist_panel = new PagingHolder(DesUserlist_config);
var Appid_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "Appid_panel",         // ***必填***，确定面板挂载在哪里 
    page_size: 10,                  //===可选===，定义页大小，默认是15 
    panel_name: "Appid_panel",       // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置应用",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    // render: Appid_render,      //===可选===，渲染每列数据 
    panel_header: [                 // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": false,            //用户控制表头是否显示
            "type": "checkbox",           //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "class": "",                //元素的class
            "td_class": "",             //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": false,
            "type": "radio",
            "name": "radio",
            "td_class": "rule-listbc",
            "width": "5%"
        }, {
            "enable": false,
            "type": "name",
            "title": "应用ID号",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "30%"
        }
    ],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [
            {
                enable: true,
                type: "image_button",
                class: "",
                style: "margin-top: 5px;margin-bottom: 5px;",
                button_text: "确定",
                functions: {
                    onclick: "write_app();"
                }
            }, {
                enable: true,
                type: "image_button",
                class: "",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "Appid_panel.hide();"
                }
            }
        ]
    }
}
var Appid_panel = new PagingHolder(Appid_config);
function toggle_policy(element) {
    var options = element.children;
    var br0_selected = 0;
    for(var i = 0; i < options.length; i++) {
        if(options[i].selected) {
            var policy_info = options[i].className.split(":");
            var policy = policy_info[0];//当前是什么策略
            var policy_count = policy_info[1];//当前策略已存在多少条
            if(policy == "br0" || policy == "br0share" || policy == "br0exclusive"){
                /*找到选择了属于br0接口的选项*/
                show_policy_div();
                if(policy == "br0share"){
                    choose_share_policy();
                    if(policy_count > 1) {
                        //不能改为独占策略
                        disable_exclusive_policy();
                    } else {
                        /*判断是不是编辑状态，不是的话也不能改为独占状态*/
                        var line = document.getElementById("edit_line").value;
                        if(line == "") {//添加状态
                            //不能改为独占策略
                            disable_exclusive_policy();
                        }
                    }
                } else {
                    enable__exclusive_policy();
                }
                br0_selected++;
                break;
            }
        }
    }
    if(!br0_selected) {
        hide_policy_div();//没有选择br0的接口，就隐藏带宽策略
    }
}

function change_policy(value) {
    if(value == "share"){
        hide_limit_content();
    }else if(value == "exclusive") {
        show_limit_content();
        exclusive_option_check(get_selected_option(document.getElementById("dst_dev").children));
    }else{
        show_error_mesg("选择出错，请刷新页面重试");
    }
}

function show_limit_content() {
    var limit_content = document.getElementById("limit_content");
    var limit = document.getElementById("limit");
    limit_content.style.display = "inline";
    limit.value = "";
}

function hide_limit_content() {
    var limit_content = document.getElementById("limit_content");
    var limit = document.getElementById("limit");
    limit_content.style.display = "none";
    limit.value = "";
}

function get_selected_option(options) {
    var selected_option;
    for(var i = 0; i < options.length; i++) {
        if(options[i].selected) {
            selected_option = options[i];
            break;
        }
    }
    return selected_option;
}

function exclusive_option_check(selected_option) {
    var policy_info = selected_option.className.split(":");
    var policy = policy_info[0];//当前是什么策略
    var policy_count = policy_info[1];//当前策略已存在多少条
    if(policy == "br0") {
        /*It's OK.Do nothing*/
    }else if(policy == "br0share") {
        if(policy_count > 1) {
            // show_error_mesg("[" + selected_option.text + "]已配置多条共享带宽策略,不能配置独占带宽策略");
            choose_share_policy();
            disable_exclusive_policy();
        }
    }else{
        /*Don't know what happen. Just do nothing*/
    }
}

function choose_share_policy() {
    document.getElementById("policy_share").checked = true;
    hide_limit_content();
}

function disable_exclusive_policy() {
    document.getElementById("policy_exclusive").disabled = true;
    var line = document.getElementById("edit_line").value;
    var alert_mesg = "";
    if(line == "") {//添加状态
        alert_mesg = "当前类已配置共享策略,不能再配置独占策略";
    } else {
        alert_mesg = "当前类已配置多条共享策略,不能修改为独占策略";
    }
    document.getElementById("conflict_tip").innerHTML = alert_mesg;
}

function enable__exclusive_policy() {
    document.getElementById("policy_exclusive").disabled = false;
    document.getElementById("conflict_tip").innerHTML = "";
}

function show_policy_div() {
    document.getElementById("policy_div").style.display = "block";
}

function hide_policy_div() {
    document.getElementById("policy_div").style.display = "none";
    choose_share_policy();
    enable__exclusive_policy();
}

function show_error_mesg(mesg) {
    alert(mesg);
}

function is_same_network( ip_str ) {
    var ips = ip_str.split( "\n" );
    var flag = true;
    for( var i = 0; i < ips.length; i++) {
        var ip_ranges = ips[i].split( "-" );
        if ( ip_ranges.length < 2 ) {
            continue;
        } else {
            var first_ips = ip_ranges[0].split( "." );
            var second_ips = ip_ranges[1].split( "." );
            if ( first_ips[0] == second_ips[0] && first_ips[1] == second_ips[1] && first_ips[2] == second_ips[2] ) {
                continue;
            } else {
                flag = false;
                break;
            }
        }
    }
    return flag;
}

var object = {
    'form_name':'RULE_FORM',
    'option'   :{
        'dscp_value':{
            'type':'text',
            'required':'1',
            'check':'int|',
        },
        'note':{
            'type':'text',
            'required':'0',
            'check':'note|',
        },
        'dst_dev':{
            'type':'select-one',
            'required':'1',
        },
        'tos':{
            'type':'select-one',
            'required':'1',
            'ass_check':function(eve){
                var msg;
                var value = eve._getCURElementsByName("tos","select","RULE_FORM")[0].value;
                if(value == "0"){
                    msg = "请选择一个tos标志流量";
                }
                return msg;
            }
        },
        'dscp_class':{
            'type':'select-one',
            'required':'1',
            'ass_check':function(eve){
                var msg;
                var value = eve._getCURElementsByName("dscp_class","select","RULE_FORM")[0].value;
                if(value == "请选择"){
                    msg = "请选择一个dscp标志流量";
                }
                return msg;
            }
        },
        'dscp_value':{
            'type':'text',
            'required':'1',
            'check':'int',
            'ass_check':function(eve){
                var msg;
                var value = eve._getCURElementsByName("dscp_value","input","RULE_FORM")[0].value;
                if(value > 63 || value < 0){
                    msg = "DSCP值的取值范围需位于0-63之间";
                }
                return msg;
            }
        },
        'src_ip':{
            'type':'textarea',
            'required':'0',
            'check':'ip|ip_mask|ip_range|',
        },
        'mac':{
            'type':'textarea',
            'required':'0',
            'check':'mac|',
        },
        'dst_ip':{
            'type':'textarea',
            'required':'0',
            'check':'ip|ip_mask|ip_range|',
            'ass_check':function(eve){
                var dst_ip = eve._getCURElementsByName("dst_ip","textarea","RULE_FORM")[0].value;
                var dst_ip_mask = dst_ip.split("/");
                var exclusive = document.getElementById("policy_exclusive").checked;
                if(exclusive) {
                    if(dst_ip == "") {
                        return "带宽独占情况下不能为空";//不起作用，只能到后台检测
                    }
                    if(dst_ip_mask.length > 1) {
                        return "带宽独占情况下不能填入IP/掩码形式地址";
                    }
                    if( !is_same_network( dst_ip ) ) {
                        return "带宽独占情况下不能填入跨网段地址";
                    }
                }
            }
        },
        'limit':{
            'type':'text',
            'required':'0',
            'check':'num|',
            'ass_check':function(eve){
                var msg="";
                var limit = eve._getCURElementsByName("limit","input","RULE_FORM")[0].value;
                if (limit != "" && limit < 1){
                    msg = "不能小于1";
                }
                return msg;
            }
        },
        'port':{
            'type':'textarea',
            'required':'0',
            'check':'port|port_range|',
        },
    }
}

//加载用户组
function load_userlist(panelName){
    panelName.show();
}

//获取应用配置面板数据
function load_app() {
    Appid_panel.show();
}
//将用户组配置内容写入文本框
function write_userlist(inputId,jstreeId,panelName) {
    var nodes = $(jstreeId).jstree().get_checked(true);
  
    var length = nodes.length;
    var array = new Array();
    var str = "";

    for(var i = 0; i < length; i++) {
        if ( nodes[i].type == "user" ) {
            array.push( nodes[i].text );
        }
    }
    if(array.length == 0) {
        message_manager.show_popup_error_mesg("没有明确的用户！");
        return;
    }
    
    for(var i = 0; i < array.length-1; i++) {
        str += array[i] + "，";
    }
    str += array[array.length-1];
    
    $("#"+inputId).val(str);
    $("#"+inputId+"Id").val(str.replace(/，/g,"&"));
    // writeFrame(document.getElementById("SrcUserlist"), array);
    panelName.hide();
    
}

//将应用配置内容写入文本框
function write_app() {
    

    var nodes = $("#for_appJstree-qosrule").jstree().get_checked(true);
    var appname = document.getElementById("Appname");
    var length = nodes.length;
    var array = new Array();
    var idArray = new Array();
    var str = "";
    var idStr = "";

    for(var i = 0; i < length; i++) {
        if ( nodes[i].type == "app" ) {
            array.push( nodes[i].text );
            idArray.push( nodes[i].id );
        }
    }
    if(array.length == 0) {
        message_manager.show_popup_error_mesg("请选择至少一项应用！");
        return;
    }
    
    for(var i = 0; i < array.length-1; i++) {
        str += array[i] + ",";
    }
    for(var i = 0; i < idArray.length-1; i++) {
        idStr += idArray[i] + ":";
    } 
    str += array[array.length-1];
    idStr += idArray[idArray.length-1];
    $(appname).val(str);
    $("#AppnameList").val(idStr);
    // writeFrame(appname, array);
    Appid_panel.hide();
    
}