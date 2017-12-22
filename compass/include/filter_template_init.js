$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    key_words_panel = new RuleAddPanel( key_words_panel_config );
    url_list_panel = new PagingHolder( url_list_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    add_panel.render();
    key_words_panel.render();
    url_list_panel.render();
    list_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    add_panel.hide();
    key_words_panel.hide();
    url_list_panel.hide();
    
    url_list_panel.update_info(true);
    list_panel.update_info(true);
    check._main(object);
    
    check_havp();
});
var list_panel;
var add_panel;
var key_words_panel;
var url_list_panel;

var key_values_url;
var checked_items_urllist = [];

var urllist_panel_render = {
    /* 'checkbox': {
        render: function( default_rendered_text, data_item ) {
            var result_render = default_rendered_text;
            for(var i=0;i<checked_items_urllist.length;i++){
                if(checked_items_urllist[i] == data_item.id){
                    result_render = "<input class='checkbox_item_for_backgroup_panel' value="+data_item.id+" checked type='checkbox'>";
                }
            }
            return result_render;
        }
    } */
};
var url_list_panel_config = {
    url: "/cgi-bin/filter_template.cgi",
    check_in_id: "panel_template_urllist",
    panel_name: "urllist_panel",
    page_size: 20,
    panel_title: "配置URL分类库",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: true,
    is_modal: true,
    render: urllist_panel_render,
    modal_config: {
        modal_box_size: "l",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            key_values_url = data_item.key_values_url;
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
            title: "类型",
            name: "type",
            width: "10%"
        }, {
            enable: true,
            type: "text",
            title: "名称",
            name: "name",
            width: "15%"
        }, {
            enable: true,
            type: "text",
            title: "说明",
            name: "description",
            width: "65%"
        } ],
    bottom_extend_widgets: {
        cls: "align-center",
        sub_items: [
            {
                enable: true,
                type: "image_button",
                style: "margin-top: 5px;margin-bottom: 5px;",
                button_text: "确定",
                functions: {
                    onclick: "save_urllist();"
                }
            }, {
                enable: true,
                type: "image_button",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "url_list_panel.hide();"
                }
            } ]
    }
};

var message_box_config = {
    url: "/cgi-bin/filter_template.cgi",
    check_in_id: "mesg_box_template",
    panel_name: "my_message_box"
}
var message_manager;
var key_words_panel_config = {
    url: "/cgi-bin/filter_template.cgi",
    check_in_id: "panel_template_keywords",
    panel_name: "keywords_panel",
    rule_title: "页面关键字",
    is_rule_title_icon: "",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 11
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {        },
        after_load_data: function( add_obj,data_item ) {        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "页面关键字",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    tip: "(以逗号隔开)",
                    id: "text_keywords",
                    name: "text_keywords"
                } ]
        } ],
    footer_buttons: {
        add_btn: false,
        cancel_btn: false,
        import_btn: false,
        sub_items: [                /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            {
                enable: true,
                type: "button",
                value: "确定",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "save_keywords();"
                }
            } ]
    }
};
var add_panel_config = {
    url: "/cgi-bin/filter_template.cgi",
    check_in_id: "panel_template_add",
    panel_name: "add_panel",
    rule_title: "过滤策略（最多8个）",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {        },
        after_load_data: function( add_obj,data_item ) {
            if(data_item.KEY_WORDS == ""){
                $("#key_words").html("配置");
            }else{
                $("#key_words").html(data_item.KEY_WORDS);
            }
            $("#KEY_WORDS").val(data_item.KEY_WORDS);
            $("#text_keywords").val(data_item.KEY_WORDS);
            $("#URLLIST").val(data_item.URLLIST);
            //check_havp();
            checked_items_urllist = data_item.URLLIST.split(";");
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "过滤策略名称*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "NAME",
                    name: "NAME",
                    check: {
                        type: "text",
                        required: 1,
                        check:'name|'
                    }
                } ]
        },
        /* {
            title: "启用杀毒扫描",
            sub_items: [
                {
                    enable: true,
                    type: "checkbox",
                    id: "HAVP",
                    name: "HAVP",
                    value: "on",
                    functions: {
                        //onclick: "check_havp(this);",
                    }
                }, {
                    enable: true,
                    type: "label",
                    id: "label_havp",
                    name: "label_havp",
                    value: "启用"
                } ]
        }, */
        {
            title: "页面关键字过滤",
            sub_items: [
                {
                    enable: true,
                    type: "label",
                    id: "KEY_WORDS_SHOW",
                    name: "KEY_WORDS_SHOW",
                    value: "<a style='text-decoration:underline;cursor:pointer;' id='key_words'>配置</a>",
                    functions: {
                        onclick: "add_keywords();"
                    }
                }, {
                    enable: true,
                    type: "text",
                    id: "KEY_WORDS",
                    name: "KEY_WORDS",
                    item_style: "display:none;"
                } ]
        }, {
            title: "配置URL分类库",
            sub_items: [
                {
                    enable: true,
                    type: "label",
                    id: "BTN_URLLIST",
                    name: "BTN_URLLIST",
                    value: "<a style='text-decoration:underline;cursor:pointer;' id='url_list'>配置</a>",
                    functions: {
                        onclick: "show_urllist_panel();"
                    }
                }, {
                    enable: true,
                    type: "text",
                    id: "URLLIST",
                    name: "URLLIST",
                    item_style: "display:none;"
                } ]
        }, {
            title: "黑白名单",
            sub_items: [
                {
                    enable: true,
                    type: "radio",
                    tip: "黑名单",
                    id: "BLACK",
                    name: "BLACK_WHITE",
                    checked: true,
                    value: "black"
                }, {
                    enable: true,
                    type: "radio",
                    tip: "白名单",
                    id: "WHITE",
                    name: "BLACK_WHITE",
                    value: "white"
                } ]
        } ]
};

var list_panel_render = {
    'checkbox': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.undeletable){
                result_render = "";
            }else{
                result_render = default_rendered_text;
            }
            return result_render;
        }
    },
    'HAVP': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text == "on" ){
                result_render = "启用";
            }else{
                result_render = "禁用";
            }
            return result_render;
        }
    },
    'BLACK_WHITE': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text == "black" ){
                result_render = "黑名单";
            }else{
                result_render = "白名单";
            }
            return result_render;
        }
    },
    'URLLIST': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var arr_urllist =[];
            if(default_rendered_text){
                arr_urllist = default_rendered_text.split(";");
            }
            var display_urllist = [];
            for(var i=0;i<arr_urllist.length;i++){
                var key = arr_urllist[i];
                display_urllist.push(key_values_url[key]);
            }
            result_render = display_urllist.join(";");
            return result_render;
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/filter_template.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_template_list",         /* ***必填***，确定面板挂载在哪里 */
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
            "cls": "",                //元素的class
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
            "title": "过滤策略名称",        //一般text类型需要title,不然列表没有标题
            "name": "NAME",
            "width": "16%"
        },/*  {
            "enable": true,
            "type": "text",
            "title": "启用杀毒",
            "name": "HAVP",
            "width": "16%"
        },  */{
            "enable": true,
            "type": "text",
            "title": "页面关键字",
            "name": "KEY_WORDS",
            "width": "28%"
        },{
            "enable": true,
            "type": "text",
            "title": "URL库",
            "name": "URLLIST",
            "width": "28%"
        },{
            "enable": true,
            "type": "text",
            "title": "黑白名单",
            "name": "BLACK_WHITE",
            "width": "8%"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "10%"
        } ],
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
            "cls": "",
            "button_icon": "delete.png",
            "button_text": "删除选中",
            "functions": {
                onclick: "delete_selected_items(this)"
            }
        } ],
    bottom_widgets: [               /* ===可选=== */
        {
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
        } ],
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
    $("#key_words").html("配置");
    $("#text_keywords").val("");
    checked_items_urllist = [];
    //check_havp();
}
//保存页面关键字
function save_keywords(){
    key_words_panel.hide();
    var key_words = $("#text_keywords").val();
    $("#KEY_WORDS").val(key_words);
    if(!key_words){
        key_words = "配置";
    }
    $("#key_words").html(key_words);
}
//保存urllist
function save_urllist(){
    var checked_items = url_list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( ";" );
    $("#URLLIST").val(ids);
    url_list_panel.hide();
}
var check = new ChinArk_forms();
var object = {
   'form_name':'HAVP_FORM',
   'option':{
        'whitelist_url':{
            'type':'textarea',
            'required':'0',
            'check':'url|',
            'ass_check':function(eve){
                
            }
        }
    }
}
//检查启用病毒是否可用
function check_havp(){
    var sending_data = {
        ACTION: 'judge_havp'
    };
    function ondatareceived(data) {
        if(data.status == "1"){
            $("#HAVP").attr("disabled",true);
            $("#HAVP").attr("checked",false);
            //$("#label_havp").val("未激活");
            $("#label_tip").html("（病毒库未激活，该功能无法使用。请先激活！）");
        }else if(data.status == "2"){
            //$("#HAVP").hide();
            $("#HAVP").attr("disabled",true);
            $("#HAVP").attr("checked",false);
            //$("#label_havp").val("已过期");
            $("#label_havp").html("（病毒库未激活，该功能无法使用。请先激活！）");
        }
    }
    /* if(e.checked){
        list_panel.request_for_json( sending_data, ondatareceived );
    } */
    list_panel.request_for_json( sending_data, ondatareceived );
}
function add_keywords(){
    key_words_panel.show();
}
function show_urllist_panel(){
    url_list_panel.show();
    url_list_panel.update_info(true);
    
    
    for(var i=0;i<checked_items_urllist.length;i++){
        url_list_panel.set_check(checked_items_urllist[i],true);
    }
    url_list_panel.update_info();
}