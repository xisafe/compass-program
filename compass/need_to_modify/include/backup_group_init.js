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
});
var list_panel;
var add_panel;
var usable_interfaces = [];
var usable_interfaces_init = [];
var message_box_config = {
    url: "/cgi-bin/backup_group.cgi",
    check_in_id: "mesg_box_backup",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/backup_group.cgi",
    check_in_id: "panel_backup_add",
    panel_name: "add_panel",
    rule_title: "添加备份组",
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            
        },
        before_save_data: function( add_obj,sending_data ) {
            var count = $("#interface_listenner option").length;
            var tmp = [];
            for(var i=0;i<count;i++){
                //$("#interface_listenner").get(0).options[i].selected = true;
                tmp.push($("#interface_listenner").get(0).options[i].value);
            }
            
            sending_data = 'interface_listenner_save='+ tmp.join("|")+'&' + sending_data;
            return sending_data;
            // sending_data.interface_listenner_save = ;
        },
        after_load_data: function( add_obj,data_item ) {
            $("#interface_listenner").empty();
            var interfaces_listenner = data_item.interface_listenner.split("&");
            usable_interfaces = usable_interfaces_init.concat();
            for(var i=0;i<interfaces_listenner.length;i++){
                $("#interface_listenner").append("<option selected value="+interfaces_listenner[i]+">"+interfaces_listenner[i]+"</option>");
                for(var j=0;j<usable_interfaces.length;j++){
                    if(usable_interfaces[j] == interfaces_listenner[i]){
                        usable_interfaces.splice(j,1);
                    }
                }
            }
            $("#usable_member").empty();
            for(var k=0;k<usable_interfaces.length;k++){
                $("#usable_member").append("<option value="+usable_interfaces[k]+">"+usable_interfaces[k]+"</option>");
            }
            $("#virtual_ip").val(data_item.virtual_ip.replace("&","\n"));
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "备份组名称",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "name",
                    name: "name",
                    check: {
                        type: "text",
                        required: 1,
                        check:'name|'
                    }
                }
            ]
        }, {
            title: "备份组虚拟IP地址",
            sub_items: [
                {
                    enable: true,
                    type: "textarea",
                    id: "virtual_ip",
                    name: "virtual_ip",
                    check: {
                        type: "textarea",
                        required: 1,
                        check:'other',
                        other_reg:'!/^\$/',
                        ass_check:function(eve){
                            var mesg = "";
                            var vip = $("#virtual_ip").val();
                            var tmp = vip.split(/\//);
                            if(tmp.length != 2){
                                mesg = "请输入正确的IP/掩码格式";
                            }else{
                                if(!eve.validip(tmp[0]) || tmp[1]<1 || tmp[1]>32){
                                    mesg = "请输入正确的IP/掩码格式";
                                }else{
                                    mesg = "";
                                }
                            }
                            return mesg;
                        }
                    }
                }
            ]
        }, {
            title: "备份组所在接口",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    id: "interface_backupgroup",
                    name: "interface_backupgroup"
                }
            ]
        }, {
            "title": "监听接口",
            sub_items:[
                {
                    enable:true,
                    type:"items_group",
                    item_style:"width:36%",
                    "sub_items":[
                        {
                            "enable": true,
                            "type": "select",
                            "label": "未选接口",
                            style: "height:150px",
                            "id": "usable_member",
                            "name": "usable_member",
                            "multiple": true
                        }
                    ]
                }, {
                    enable:true,
                    type:"items_group",
                    item_style:"width:16%",
                    "sub_items":[
                        {
                            "enable": true,
                            "type": "button",
                            "id": "btn_right",
                            "name": "btn_right",
                            "value": ">>",
                            "style": "width:66px;min-width:66px;",
                            functions: {
                                onclick: "add_interface();"
                            }
                        }, {
                            "enable": true,
                            "type": "button",
                            "id": "btn_left",
                            "name": "btn_left",
                            "value": "<<",
                            "style": "width:66px;margin-top:20px;margin-bottom:30px;min-width:66px;",
                            functions: {
                                onclick: "delete_node();"
                            }
                        }, {
                            "enable": true,
                            "type": "label",
                            value: "",
                            item_style: "height:1px;width:200px"
                        }
                    ]
                }, {
                    enable:true,
                    type:"items_group",
                    item_style:"width:25%",
                    "sub_items":[
                        {
                            "enable": true,
                            "type": "select",
                            "label": "已选接口",
                            style: "height:150px",
                            "id": "interface_listenner",
                            "name": "interface_listenner",
                            "multiple": true
                        }
                    ]
                }
            ]
        }
    ]
};

var list_panel_render = {
    'virtual_ip': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text){
                result_render = default_rendered_text.replace(/&/g,",");
            }
            return result_render;
        }
    },
    'interface_listenner': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text){
                result_render = default_rendered_text.replace(/&/g,",");
            }
            return result_render;
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/backup_group.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_backup_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    event_handler: {
        before_load_data: function( list_obj ) {
            
        },
        after_load_data: function ( list_obj, response ) {
            
            $("#interface_backupgroup").empty();
            $("#interface_backupgroup").append("<option value='br0'>LAN口</option>");
            $("#interface_backupgroup").append("<option value='br1'>DMZ口</option>");
            for(var i=0;i<response.eths.length;i++){
                $("#interface_backupgroup").append("<option value="+response.eths[i]+">"+response.eths[i]+"</option>");
            }
            $("#usable_member").empty();
            for(var i=0;i<response.interfaces.length;i++){
                $("#usable_member").append("<option value="+response.interfaces[i]+">"+response.interfaces[i]+"</option>");
            }
            usable_interfaces = response.interfaces;
            usable_interfaces_init = response.interfaces.concat();
        }
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
            "width": "3%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            'td_class':"align-center",      //使表格文字居中
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
            "title": "备份组名称",
            "name": "name",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "备份组虚拟IP",
            'td_class':"align-center",
            "name": "virtual_ip",
            "width": "30%"
        },{
            "enable": true,
            "type": "text",
            "title": "备份组所在接口",
            "name": "interface_backupgroup",
            'td_class':"align-center",
            "width": "15%"
        },{
            "enable": true,
            "type": "text",
            "title": "监听接口",
            "name": "interface_listenner",
            "width": "20%"
        },{
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            'td_class':"align-center",
            "width": "10%"
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
            "enable": false,
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
    is_default_search: false          /* ===可选===，默认是true，控制默认的搜索条件 */
    
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
    $("#interface_listenner").empty();
    $("#usable_member").empty();
    for(var k=0;k<usable_interfaces_init.length;k++){
        $("#usable_member").append("<option value="+usable_interfaces_init[k]+">"+usable_interfaces_init[k]+"</option>");
    }
}
//删除节点
function delete_node(){
    $("#interface_listenner").find("option:selected").each(function(){
        $(this).remove();
        $("#usable_member").append("<option value="+$(this).val()+">"+$(this).text()+"</option>");
    });
    
    /* var count = $("#interface_listenner option").length;
    for(var i=0;i<count;i++){
        $("#interface_listenner").get(0).options[i].selected = true;
    } */
}
//动态添加地址
function add_interface(){
    $("#usable_member").find("option:selected").each(function(){
        $(this).remove();
        $("#interface_listenner").append("<option selected value="+$(this).val()+">"+$(this).text()+"</option>");
    });
}