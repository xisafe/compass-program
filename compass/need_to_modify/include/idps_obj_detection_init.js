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
    check_running();
    list_panel.update_info(true);
});
var message_box_config = {
    url: "/cgi-bin/idps_obj_detection.cgi",
    check_in_id: "panel_obj_msg",
    panel_name: "my_message_box"
}
var message_manager;
var list_panel;
var add_panel;
var add_panel_config = {
    url: "/cgi-bin/idps_obj_detection.cgi",
    check_in_id: "panel_obj_add",
    panel_name: "add_panel",
    rule_title: "内网检测对象",
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            /* $(".ctl_added_div").remove();
            var root = $("#addr_add")[0].parentNode.parentNode.parentNode;
            var objs = data_item.addr.split("&");
            for(var i = 0;i < objs.length;i++){
                var div = document.createElement("div");
                div.className = "ctl_added_div";
                div.innerHTML = "<input name='addr_added' type='text' style='margin-left:10px;margin-top:5px' value="+objs[i]+" class='add-panel-form-text' /><input type='button' class='net_button' style='width:50px' value='删除' onclick='delete_addr(this);'/>";
                root.insertBefore(div,$("#addr_add")[0].parentNode.parentNode);
            } */
            
            var objs = data_item.addr.split("&");
            var str_objs = objs.join("\n");
            $("#addr_add").val(str_objs);
        }
    },
    is_modal: true,
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "名称*",
        sub_items: [{
            enable: true,
            type: "text",
            id: "name",
            name: "name",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 1,
                check: 'name|',
                ass_check: function( check ) {

                }
            }
        }]
    },{
        title: "说明",
        sub_items: [{
            enable: true,
            type: "text",
            id: "description",
            name: "description",
            style:"width:300px;",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 0,
                check: 'note|',
                ass_check: function( check ) {

                }
            }
        }]
    },
    /* {
        "title": "地址*",
        sub_items:[
            {
                enable:true,
                type:"items_group",
                "sub_items":[
                    {
                        "enable": true,
                        "type": "text",
                        //"readonly": true,
                        "id": "addr_add",
                        "name": "addr_add",
                        value: "",
                        check: {
                            type: "text",
                            required: 0,
                            check: 'ip|ip_mask|',
                            ass_check: function( check ) {
                        
                            }
                        }
                    },
                    {
                        "enable": true,
                        "type": "button",
                        "id": "btn_add_addr",
                        "name": "btn_add_addr",
                        "style": "width:50px;margin-left:5px;",
                        cls: "net_button",
                        "value":"增加",
                        "functions":{
                            onclick: "add_addr(this);"
                        }
                    }
                ]
            }
        ]
    },  */
    {
        title: "地址*",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "addr_add",
            name: "addr_add",
            value: "",
            functions: {
            },
            check: {
                type: "textarea",
                required: 1,
                check:'other',
                other_reg:'!/^\$/',
                ass_check: function( check ) {
                    var temp = $("#addr_add").val().split("\n");
                    var mesg = "";
                    for(var i=0;i<(temp.length);i++){
                        if(i > 0){
                            if(temp[i-1] == temp[temp.length-1]){
                                mesg = "IP地址重复";
                            }
                        }
                        if(!check.validsegment(temp[i]) && !check.validip(temp[i]) && !(temp[i] == "0.0.0.0/0") && !(temp[i] == "0.0.0.0/1")){
                            mesg = "请输入正确的地址";
                        }
                    }
                    return mesg;
                }
            }
        }]
    }]
};

var list_panel_render = {
    'addr': {
        render: function( default_rendered_text, data_item ) {
            var temp_arr = default_rendered_text.split("&");
            var result_render = temp_arr.join(", ");
            return result_render;
        }
    }
    
};


var list_panel_config = {
    url: "/cgi-bin/idps_obj_detection.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_obj_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [{
        "enable": true,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",        //元素的class
        "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
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
        "title": "名称",        //一般text类型需要title,不然列表没有标题
        "name": "name",
        "width": "20%"
    }, {
        "enable": true,
        "type": "text",
        "title": "说明",
        "name": "description",
        "width": "30%"
    }, {
        "enable": true,
        "type": "text",
        "title": "地址",
        "name": "addr",
        "width": "30%"
    }, {
        "enable": true,
        "type": "action",
        "title": "活动/动作",
        "name": "action",
        "width": "15%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        button_icon: "add16x16.png",
        button_text: "新建",
        functions: {
            onclick: "add_rule(this);"
        }
    },{
        "enable": true,
        "type": "image_button",
        "id": "delete_selected",
        "name": "delete_selected",
        "button_icon": "delete.png",
        "button_text": "删除选中",
        "functions": {
            onclick: "delete_selected_items(this)"
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

//切换添加面板形式
function changeAddPanel(e){
    if(e.value == "tcp" || e.value == "udp"){
        $(".tr_crl_sport").show();
        $(".tr_crl_dport").show();
        $(".tr_crl_type").hide();
        $(".tr_crl_code").hide();
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
//动态添加地址
function add_addr(e){
    var root = e.parentNode.parentNode.parentNode;
    var addr_add = $("#addr_add").val();
    var div = document.createElement("div");
    div.className = "ctl_added_div";
    div.innerHTML = "<input name='addr_added' type='text' style='margin-left:10px;margin-top:5px;' value='"+addr_add+"' class='add-panel-form-text' /><input type='button' style='width:50px;' class='net_button' value='删除' onclick='delete_addr(this);'/>";
    if(addr_add == "" || addr_add == null){
        message_manager.show_popup_error_mesg("添加地址内容不能为空！");
    }else{
        root.insertBefore(div,e.parentNode.parentNode);
    }
    $("#addr_add").val("");
}
function delete_addr(e){
    var root = e.parentNode.parentNode;
    root.removeChild(e.parentNode)
}
//显示添加面板
function add_rule( element ) {
    $(".ctl_added_div").remove();
    add_panel.show();
}