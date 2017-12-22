var message_box_config = {
    url: "/cgi-bin/outboundlb_uplink_setting.cgi",
    check_in_id: "mesg_box_id"
    
}

var uplink_add_panel_config = {
    url: "/cgi-bin/outboundlb_uplink_setting.cgi",
    check_in_id: "uplink_add_panel_config",
    panel_name: "uplink_add_panel",
    rule_title: "上行链路",
    is_panel_closable: true,
    is_panel_stretchable: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_cancel_edit:function(add_obj){
        },
        after_cancel_edit:function(add_obj){
        },
        before_load_data:function(){
        },
        after_load_data:function( add_obj, data_item ){
            load_uplinks_list();   // 这个也必须执行，因为会存在你切换从一行的编辑到另一行编辑时还是会存在‘上次状态保留’的问题。
            var true_name = data_item['true_name'];
            var option = '<option value="' + true_name + '">' + true_name + '</option>';
            // 解决一个大难题，如何准确判断出value值为true_name的那个option是否存在呢？必须用val()方法才能测出来
            if( $("#true_uplink_name_id option[value="+true_name+"]").val() == undefined ){   // 只有当列表原来不存在这个option时才需添加！
                $("#true_uplink_name_id").append(option);
            }
            // $("#true_uplink_name_id option:eq(0)").before(option);  // 这个存在累加问题，就是你连续几次点击‘编辑’时
            $("#true_uplink_name_id option[value="+true_name+"]").attr("selected","selected");
        },
        before_save_data:function( add_obj, sending_data ){
        },
        after_save_data:function( add_obj, received_data ){
            load_uplinks_list();
            init_show_apply_box();
        }
    },
    items_list: [
        {
            title: "链路名(虚拟链路名) *",
            sub_items:[
               {     enable:true,
                     type: "text",
                     name: "name",
                     id: "name",
                     check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                        type: "text",       /* **必填** */
                        required: 1,        /* **必填** */
                        check: 'name|',     /* **必填** */
                        ass_check: function( check ) {
                        }
                    }
               }
            ]
        },{
            title: "权重 *",
            sub_items:[
               {     enable: true,
                     type: "text",
                     name: "weight",
                     id: "weight",
                     tip: "(1-10)"
               }
            ]
        },{
            title: "启用 *",
            sub_items:[
               {     enable: true,
                     type: "checkbox",
                     name: "enable",
                     id: "enable",
                     checked: true
               }
            ]
        },{
            title: "实际链路 *",
            sub_items:[
               {     enable:true,
                     type: "select",
                     name: "true_name",
                     id: "true_uplink_name_id",
                     style:"width:200px;",
                     options: []
               }
            ]
        },{
            title: "带宽值设置 *",
            sub_items:[
               {     enable:true,
                     type: "text",
                     name: "band_width",
                     id: "band_width",
                     tip: "(单位：Mb/s)"
               }
            ]
        }
    ]
}
var my_list_panel_actions_render = {
    'action': {
        render: function( default_rendered_text, data_item ) {
            var enable = data_item.enable;
            var toggle_class, button_text, button_icon, onclick;
            
            if( enable == "off"){
                button_icon = "off.png";
                onclick = "enable_item(this);";
            }
            else{
                button_icon = "on.png";
                onclick = "disable_item(this);";
            }
            var toggle_enable_button = {
                enable: true,
                button_icon: button_icon,
                value: data_item.id,
                functions: { 
                    onclick: onclick
                },
                class:"action-image"
            };
            var edit_button = {
                enable: true,
                name: "edit_edit",
                button_icon: "edit.png",
                button_text: "编辑",
                value: data_item.id,
                functions: {
                    onclick: "handle_edit_operation(this);"
                },
                class:"action-image"
            };
            var del_button = {
                enable: true,
                name: "delete_delete",
                button_icon: "delete.png",
                button_text: "删除",
                value: data_item.id,
                functions: {
                    onclick: "handle_delete_operation(this);"
                },
                class:"action-image"
            };
            var action_buttons = [ toggle_enable_button, edit_button, del_button ];

            var rendered_text =  PagingHolder.create_action_buttons( action_buttons );
            return rendered_text;
        }
    }
}

var uplink_list_panel_config = {
    url: "/cgi-bin/outboundlb_uplink_setting.cgi",
    check_in_id: "uplink_list_panel_config",
    panel_name: "uplink_list_panel",
    page_size: 10,    // 只让它显示10行
    render: my_list_panel_actions_render,    // 先把渲染这个地方注释掉吧
    event_handler: {
        before_load_data: function( add_obj, data_item ) {
        },
        after_load_data: function ( add_obj, data_item ) {
        },
        before_save_data: function ( add_obj, sending_data ) {
        },
        after_save_data: function ( add_obj, received_data ) {
        }
    },
    panel_header: [
        {
            enable: true,
            type: "checkbox",
            name: "checkbox",
            width: "5%",
            td_class: "align-center"
        }, {
            enable: true,
            type: "text",
            title: "链路名称",
            name: "name",
            width: "20%"
        }, {
            enable: true,
            type: "text",
            title: "实际链路",
            name: "true_name",
            width: "20%"
        }, {
            enable: true,
            type: "text",
            title: "权重",
            name: "weight",
            width: "20%"
        }, {
            enable: true,
            type: "text",
            title: "最大带宽",
            name: "band_width",
            width: "20%"
        }, {
            enable: true,
            type: "action",
            title: "动作",
            name: "action",
            width: "10%",
            td_class: "align-center"

        }
    ],
    top_widgets: [
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "添加新链路",
            // style: "padding:3px 4px",
            functions: {
                onclick: "load_uplinks_list(); show_add_panel();  "
                // 最新更改：添加调用执行load_uplinks_list();
                // 目的是为解决上一时刻在‘编辑’中uplinks列表被新增了一个option但是下一次切换到‘添加’时uplinks列表里还保留有上次的那个option
            }
        }
    ]
}

var UPLINKS = null;
var uplink_add_panel  = new RuleAddPanel( uplink_add_panel_config );
var uplink_list_panel = new PagingHolder( uplink_list_panel_config );
var message_manager = new MessageManager( message_box_config );

$( document ).ready(function() {
    uplink_add_panel.render();
    uplink_list_panel.render();
    message_manager.render();

    uplink_add_panel.hide();

    uplink_list_panel.set_ass_add_panel( uplink_add_panel );
    uplink_add_panel.set_ass_list_panel( uplink_list_panel );

    uplink_list_panel.set_ass_message_manager( message_manager );
    uplink_add_panel.set_ass_message_manager( message_manager );

    uplink_list_panel.update_info(true);

    init_show_apply_box();
    load_uplinks_list();   // 新增，初始要从后台相应目录中加载最新的所有链路

    $(".search").remove();

});
function init_show_apply_box(){
    function onreceived(response){
        var is_need_reload = response['need_reload'];
        if( is_need_reload == 1 ){
            uplink_list_panel.show_apply_mesg(response['mesg']);
        }
    }
    send_request( { ACTION:"is_need_reload" }, onreceived );
}
function load_uplinks_list(){

    function ondatareceived( data ) {
        var options = "";
        UPLINKS = data['uplinks_list'];
        var uplinks = data['uplinks_list'];  // 切记uplinks是个哈希对象而非数组对象
        for(var item in uplinks){
            options += '<option value="' + item + '">' + item + '</option>';
        }
        $( "#true_uplink_name_id" ).empty();
        $( "#true_uplink_name_id" ).append( options );
    }

    send_request( { ACTION:"load_uplinks_list" }, ondatareceived );
}


function send_request(sending_data, ondatareceived){
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/outboundlb_uplink_setting.cgi",
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            uplink_list_panel.show_error_mesg("返回数据格式有误,请检查");
        },
        success: ondatareceived
    });
}

function enable_item(element){
    uplink_list_panel.operate_item( element.value, "enable_data", "确认启用？", false );

}
function disable_item(element){
    uplink_list_panel.operate_item( element.value, "disable_data", "确认禁用？", false );

}
function handle_edit_operation(element){
    uplink_list_panel.edit_item( element.value );

}
function handle_delete_operation(element){
    uplink_list_panel.delete_item( element.value );
    load_uplinks_list();
}

function show_add_panel(){
    // if( UPLINKS.length == 0 ){   // if( UPLINKS.size() == 0 )  if(UPLINKS == null)测试失败，因为它并不是‘不存在的’，而是一个‘空的’对象
    //     alert("对不起，所有的链路都已使用，故无法添加新链路");
    //     return;
    // }
    // if( UPLINKS.toString() == "") { alert("haha"); }
    uplink_add_panel.show();
}


