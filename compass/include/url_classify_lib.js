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
var message_box_config = {
    url: "/cgi-bin/url_classify_lib.cgi",
    check_in_id: "mesg_box_url",
    panel_name: "my_message_box",
    rule_title:"URL查询"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/url_classify_lib.cgi",
    check_in_id: "panel_url_add",
    panel_name: "add_panel",
    rule_title: "URL分类库",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
        },
        after_load_data: function( add_obj,data_item ) {
            
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "名称*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    popup: ["最多10个字符"],
                    id: "name",
                    name: "name",
                    check: {
                        type: "text",
                        required: 1,
                        check:'note|',
                        ass_check:function(eve){
                            var name = $("#name").val();
                            if(name.length > 10){
                                return "最多输入10个字符！";
                            }
                        }
                    }
                }
            ]
        }, {
            title: "说明",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    popup: ["最多30个字符"],
                    id: "description",
                    name: "description",
                    check: {
                        type: "text",
                        required: 0,
                        check:'other',
                        other_reg:'!/^\$/',
                        ass_check:function(eve){
                            var content = $("#description").val();
                            if(content.length > 30){
                                return "最多输入30个字符！";
                            }
                        }
                    }
                }
            ]
        }, {
            title: "URL地址*",
            sub_items: [
                {
                    enable: true,
                    type: "textarea",
                    popup: ["每行一个"],
                    id: "urls",
                    name: "urls",
                    check: {
                        type: "textarea",
                        required: 1,
                        check:'url|'
                    }
                }
            ]
        }
    ]
};

var list_panel_render = {
    'checkbox': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if( data_item.type == "system" ){
                result_render = "";
            }else{
                result_render = default_rendered_text;
            }
            return result_render;
        }
    },
    'type': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if( default_rendered_text == "system" ){
                result_render = "内置";
            }else{
                result_render = "用户自定义";
            }
            return result_render;
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
            
            if(data_item.type == "system"){
                var edit_button = {
                enable: true,
                id: "edit_item",
                name: "edit_item",
                button_icon: "edit_disabled.png",
                "class": "action-image",
                }
                var delete_button = {
                    enable: true,
                    id: "delete_item",
                    name: "delete_item",
                    button_icon: "delete_disabled.png",
                    "class": "action-image",
                }
            
            }else{
                var edit_button = {
                enable: true,
                id: "edit_item",
                name: "edit_item",
                button_icon: "edit.png",
                value: data_item.id,
                 "class": "action-image",
                    functions: {
                        onclick: "list_panel.edit_item(this.value);"
                    }
                }
                var delete_button = {
                    enable: true,
                    id: "delete_item",
                    name: "delete_item",
                    button_icon: "delete.png",
                    value: data_item.id,
                     "class": "action-image",
                    functions: {
                        onclick: "list_panel.delete_item(this.value);"
                    }
                }
            }
            var render_edit_button = PagingHolder.create_action_buttons( [edit_button] );
            var render_delete_button = PagingHolder.create_action_buttons( [delete_button] );
            var action_buttons = render_edit_button+render_delete_button;
            return action_buttons;
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/url_classify_lib.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_url_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
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
            "title":"序号",
            "type": "text",
            "name": "index",
            "width": "5%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "text",
            "title": "名称",
            "name": "name",
            "width": "20%"
        },{
            "enable": true,
            "type": "text",
            "title": "说明",
            "name": "description",
            "width": "55%"
        },{
            "enable": true,
            "type": "text",
            "title": "类型",
            "name": "type",
            "width": "5%",
            "td_class":"align-center"
        },  {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "10%",
            "td_class":"align-center"

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
    // default_search_config: {        /* ===可选===，只有当is_default_search为true时才生效 */
    //     input_tip: "输入域名以查询...",   /* ===可选===，控制搜索输入框内的提示，默认是“输入关键字以查询...” */
    //     title: "域名： ",                     /* ===可选===，控制搜索输入框左边的提示，默认无提示 */
    //     functions:{
    //        onchange:"list_panel.update_info(true);"
    //     },

    // },
    
       extend_search: [                /* ===可选===，定义额外的搜索筛选条件，位置在面板右上角，控件类似top_widgets中控件 */
       {
            enable: true,
            type: "text",
            input_tip: "输入域名以查询...",   /* ===可选===，控制搜索输入框内的提示，默认是“输入关键字以查询...” */
            id: "domain_name",
            name: "domain_name",
            title: "域名：",
            class:"width:200px"
            // check: {
            //     type:'text',
            //     required: 1,
            //     check: 'int|',
            //     ass_check: function(){
            //         var val = $( "#page_size" ).val();
            //         if( val > 100 || val < 10 ) {
            //             return "输入10-100之间的整数";
            //         }
            //     }
            // }
        }, {
            enable: true,
            type: "image_button",
            id: "begin_search",
            name: "begin_search",
            button_icon: "search16x16.png",
            button_text: "搜索",
            class: "my_search_button",
            functions: {
                onclick: "search_domain();"
            }
        }
    ],
    event_handler:{
        after_load_data: function( add_obj,data_item ) {
           

        }
    },
    is_default_search: false          /* ===可选===，默认是true，控制默认的搜索条件 */
}
function search_domain() {
    var domain_name = $('#domain_name').val();
	if(!/^[0-9a-zA-Z]+[0-9a-zA-Z\.-]*\.[a-zA-Z]{2,4}$/.test(domain_name)) {
		message_manager.show_popup_error_mesg("搜索格式错误！！！");
		return false;
	}
    // paging_holder.update_info( true );
    var sending_data = {
        ACTION:'search_domain',
        data: domain_name
    }
     function ondatareceived( data ) {
        var type = (data.detail_data.length != 0) ? "你所查询的URL类别为：["+data.detail_data[0].name +"]" : "无法查询该域名！";
        message_manager.show_details_message("查询结果 :"+type);
       
     }
     do_request( sending_data, ondatareceived );
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
        if(checked_items.length < 1){
            message_manager.show_popup_note_mesg("请先选中策略项");
            return;
        }
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

// function extend_search_function( element ) {
//     list_panel.update_info( true );
// }
function add_rule( element ) {
    add_panel.show();
}

//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/url_classify_lib.cgi",
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}