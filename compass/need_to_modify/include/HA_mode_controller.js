/**author:刘炬隆（liujulong）
date:2015/05/06
**/
var paging_holder = {
    url: "/cgi-bin/HA_mode.cgi"
};
var message_box_config = {
    url: paging_holder.url,
    check_in_id: "panel_mesg",
    panel_name: "my_message_box"
}
var checked_items_group = [];
var message_manager;
var backgroup_list_panel;
var backgroup_panel_render = {
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
var backgroup_list_panel_config = {
    url: paging_holder.url,
    check_in_id: "panel_backgroup",
    panel_name: "backgroup_panel",
    page_size: 15,
    panel_title: "配置备份组",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: true,
    is_modal: true,
    render: backgroup_panel_render,
    modal_config: {
        modal_box_size: "m",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            
        }
    },
    panel_header: [
        {
            enable: true,
            type: "checkbox",
            name: "checkbox",
            width: "5%"
        }, {
            enable: true,
            type: "text",
            title: "备份组名称",
            name: "name",
            width: "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "备份组虚拟IP",
            "name": "virtual_ip",
            "width": "30%"
        }, {
            "enable": true,
            "type": "text",
            "title": "备份组所在接口",
            "name": "interface_backupgroup",
            "width": "15%"
        }, {
            "enable": true,
            "type": "text",
            "title": "监听接口",
            "name": "interface_listenner",
            "width": "20%"
        }
    ],
    bottom_extend_widgets: {
        cls: "align-center",
        sub_items: [
            {
                enable: true,
                type: "image_button",
                id: "btn_confirm",
                style: "margin-top: 5px;margin-bottom: 5px;",
                button_text: "确定",
                functions: {
                    onclick: "save_backgroup(this);"
                }
            }, {
                enable: true,
                type: "image_button",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "backgroup_list_panel.hide();"
                }
            }
        ]
    }
};
var check = new ChinArk_forms();
var object = {
   'form_name':'HAMODE_FILTER_FORM',
   'option':{
        'HEART_IP':{
            'type':'text',
            'required':'1',
            'check':'ip|',
            'ass_check':function(eve){
                
            }
        },
        'HEARTPEER_IP':{
            'type':'text',
            'required':'1',
            'check':'ip|',
            'ass_check':function(eve){
                
            }
        },
        'MANAGEIP':{
            'type':'text',
            'required':'1',
            'check':'ip|',
            'ass_check':function(eve){
                
            }
        },
        'HA_ID':{
            'type':'text',
            'required':'1',
            'check':'num|',
            'ass_check':function(eve){
                var mesg = "";
                var ha_id = $("#HA_ID").val();
                if(ha_id > 255){
                    mesg = "应填1-255之间的整数";
                }
                return mesg;
            }
        },
        'HA_PRIORITY':{
            'type':'text',
            'required':'1',
            'check':'num|',
            'ass_check':function(eve){
                var mesg = "";
                var ha_priority = $("#HA_PRIORITY").val();
                if(ha_priority > 255){
                    mesg = "应填1-255之间的整数";
                }
                return mesg;
            }
        },
        'HA1_ID':{
            'type':'text',
            'required':'1',
            'check':'num|',
            'ass_check':function(eve){
                var mesg = "";
                var ha1_id = $("#HA1_ID").val();
                if(ha1_id > 255){
                    mesg = "应填1-255之间的整数";
                }
                return mesg;
            }
        },
        'HA1_PRIORITY':{
            'type':'text',
            'required':'1',
            'check':'num|',
            'ass_check':function(eve){
                var mesg = "";
                var ha1_priority = $("#HA1_PRIORITY").val();
                if(ha1_priority > 255){
                    mesg = "应填1-255之间的整数";
                }
                return mesg;
            }
        },
        'HA2_ID':{
            'type':'text',
            'required':'1',
            'check':'num|',
            'ass_check':function(eve){
                var mesg = "";
                var ha2_id = $("#HA2_ID").val();
                if(ha2_id > 255){
                    mesg = "应填1-255之间的整数";
                }
                return mesg;
            }
        },
        'HA2_PRIORITY':{
            'type':'text',
            'required':'1',
            'check':'num|',
            'ass_check':function(eve){
                var mesg = "";
                var ha2_priority = $("#HA2_PRIORITY").val();
                if(ha2_priority > 255){
                    mesg = "应填1-255之间的整数";
                }
                return mesg;
            }
        }
    }
}

$(document).ready(function(){
    backgroup_list_panel = new PagingHolder( backgroup_list_panel_config );
    message_manager = new MessageManager( message_box_config );
    backgroup_list_panel.render();
    message_manager.render();
    backgroup_list_panel.set_ass_message_manager( message_manager );
    
    backgroup_list_panel.hide();
    backgroup_list_panel.update_info(true);
    
    check._main(object);
    
    enable_controll();
    $("#ENABLED").on('click', function() {
         enable_controll();
    });
    change_show_mode();
});
function enable_controll(){

    if ($("#ENABLED").attr('checked')) {
        $('#ENABLED').parent().parent().siblings().not('.table-footer').show().each(function() {
            $(this).children('td').eq(1).find('input,select').removeAttr('disabled');
            $("#HA1_ID,#HA2_ID").removeAttr('disabled');
        });
    }else{
        $('#ENABLED').parent().parent().siblings().not('.table-footer').hide().each(function() {
            $(this).children('td').eq(1).find('input,select').attr('disabled', 'disabled');            
            $("#HA1_ID,#HA2_ID").attr('disabled', 'disabled');
        });
    }
    $('.ctr_aa').hide();
}
//控制显示模式
function change_show_mode(){
    var ha_mode = $('input:radio[name="HA_MODE"]:checked').val();
    if(ha_mode == "AA"){
        $(".ctr_as").hide();
        $(".ctr_aa").show();
    }else{
        $(".ctr_as").show();
        $(".ctr_aa").hide();
    }
}
//显示备份组配置面板
function show_backgroup_panel(e,str_checked_items){
    backgroup_list_panel.show();
    $("#btn_confirm").val(e.id);
    for(var j=0;j<checked_items_group.length;j++){
        backgroup_list_panel.set_check(checked_items_group[j],false);
    }
    if(str_checked_items == "" || str_checked_items == null || e.innerHTML == "请选择备份组"){
        checked_items_group = [];
    }else{
        checked_items_group = str_checked_items.split("&");
    }
    for(var i=0;i<checked_items_group.length;i++){
        backgroup_list_panel.set_check(checked_items_group[i],true);
    }
    backgroup_list_panel.update_info();
}
//保存备份组配置
function save_backgroup(e){
    var checked_items = backgroup_list_panel.get_checked_items();
    var checked_items_name = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_name.push( checked_items[i].name );
    }
    var names = checked_items_name.join( "&" );
    var show_names = "请选择备份组"; 
    if(checked_items_name.length > 0){
        show_names = "已选备份组:"+checked_items_name.join( "," );
    }
    if(e.value == "btn_bac"){
        $("#BACKGROUP").val(names);
        $("#btn_bac").html(show_names);
    }else if(e.value == "btn_h1bac"){
        $("#BACKGROUP1").val(names);
        $("#btn_h1bac").html(show_names);
    }else{
        $("#BACKGROUP2").val(names);
        $("#btn_h2bac").html(show_names);
    }
    backgroup_list_panel.hide();
}