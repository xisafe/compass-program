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
    url: "/cgi-bin/ca_certificate.cgi",
    check_in_id: "mesg_box_notice",
    panel_name: "my_message_box"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/ca_certificate.cgi",
    check_in_id: "panel_notice_add",
    panel_name: "add_panel",
    rule_title: "导入证书",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add: false,
        cancel: false,
        import: false,
        sub_items: [                /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            {
                enable: true,
                type: "submit",
                value: "确认",
                style:"vertical-align: top;background-image: url(../images/button.jpg);background-repeat: repeat-x;border-top: 0px;border-left: 1px solid #b3e2f4;border-bottom: 1px solid #b3e2f4;border-right: 1px solid #b3e2f4;",
                id:"import_ca",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "add_CA_file();"
                }
            },{
                enable: true,
                type: "button",
                value: "取消",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "add_panel.hide();"
                }
            },
            {
                enable:true,
                type:"hidden",
                name:"ACTION",
                value:"import_data"
            }
        ]
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
            var text_val = $('#notice_content').val();
                text_val = text_val.replace(/\ \ \ /g,'\n');
                $('#notice_content').val(text_val);
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "选择升级文件*",
        sub_items: [{
            enable: true,
            type: "file",
            style:"height:24px",
            name: "file_lib",
            id: "file_lib",
            check: {
                type: "file",
                required: 1
            }
        }]
    }]
};

var list_panel_render = {
    'notice_content': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(default_rendered_text.length > 45 ){
                result_render = default_rendered_text.substr(0,45)+"...";
            }else{
                result_render = default_rendered_text;
            }
            result_render = result_render.replace(/\</g,'&lt;');
            result_render = result_render.replace(/\>/g,'&gt;');
            return '<code>' + result_render + '</code>';
        }
    },
    'action' : {
        render: function( default_rendered_text, data_item ){
            var button_text, button_icon, onclick;
            var action_buttons = [
                {
                    "enable": true,
                    "id": "edit_item",
                    "name": "edit_item",
                    "button_icon": "edit.png",
                    "button_text": "编辑",
                    "value": data_item.id,
                    "functions": {
                        onclick: "list_panel.edit_item(this.value);"
                    },
                    "class": "action-image",
                },
                {
                    "enable": true,
                    "id": "review_item",
                    "name": "review_item",
                    "button_icon": "view_details.png",
                    "button_text": "预览",
                    "value": data_item.id,
                    "functions": {
                        onclick: "open_page('','',this.value);"
                    },
                    "class": "action-image",
                },
                {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "value": data_item.id,
                    "functions": {
                        onclick: "list_panel.delete_item(this.value);"
                    },
                    "class": "action-image",
                }
            ];
            var temp = PagingHolder.create_action_buttons( action_buttons );
            return temp;
            // var btn$ = $(temp);
            // return btn$;
        }

    } 
};

function create_action_buttons( action_buttons ) {
    var buttons = "";

    if( action_buttons === undefined ) {
        return buttons;/*如果没有定义相应的对象，直接返回*/
    }

    for( var i = 0; i< action_buttons.length; i++ ) {
        var item = action_buttons[i];
        if( item.enable === undefined || !item.enable ){
            continue;
        }
        buttons += '<input type="image" ';
        if( item.id !== undefined && item.id ) {
            buttons += 'id="' + item.id + '" ';
        }
        if( item.value !== undefined && item.value ) {
            buttons += 'value="' + item.value + '" ';
        }
        if( item.name !== undefined && item.name ) {
            buttons += 'name="'+ item.name +'" ';
        }
        if( item.class !== undefined && item.class ) {
            buttons += 'class="action-image ' + item.class + '" ';
        } else {
            buttons += 'class="action-image" ';
        }
        if( item.button_text !==undefined && item.button_text ) {
            buttons += 'title="' + item.button_text + '" ';
        }
        if( item.button_icon !== undefined && item.button_icon ) {
            buttons += 'src="../images/' + item.button_icon +'" ';
        }
        if( item.functions !== undefined && item.functions ) {
            var functions = item.functions;
            for ( var key in functions ) {
                buttons += key +'="' + functions[key] + '" ';
            }
        }
        buttons += '/>';
    }

    return buttons;
}

var list_panel_config = {
    url: "/cgi-bin/ca_certificate.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_notice_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [{
        "enable": true,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //用户装载数据之用
        "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "3%",
        "td_class":"align-center"
    }, {
        "enable": false,
        "type": "radio",
        "name": "radio",
        "column_cls": "rule-listbc",
        "width": "3%"
    }, {
        "enable": true,
        "type": "text",
        "title": "ID",        //一般text类型需要title,不然列表没有标题
        "name": "idForCA",
        "width": "3%",
        "td_class":"align-center"
    },{
        "enable": true,
        "type": "text",
        "title": "证书名称",        //一般text类型需要title,不然列表没有标题
        "name": "nameForCA",
        "width": "6%",
        "td_class":"align-center"
    }, {
        "enable": true,
        "type": "text",
        "title": "颁发者",
        "name": "authorizer",
        "width": "29%",
    }, {
        "enable": true,
        "type": "text",
        "title": "主题",
        "name": "theme",
        "width": "30%",
    },{
        "enable": true,
        "type": "text",
        "title": "有效期起始时间",
        "name": "start_time",
        "width": "13%",
    }, {
        "enable": true,
        "type": "text",
        "title": "有效期起始时间",
        "name": "end_time",
        "width": "13%",
        "td_class":"align-center"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        button_icon: "../images/stock_up-16.png",
        button_text: "导入证书",
        functions: {
            onclick: "add_rule(this);"
        }
    },
    {
        "enable": true,
        type: "image_button",
        "id": "delete_selected",
        "name": "delete_selected",
        "button_icon": "delete.png",
        "button_text": "删除证书",
        "functions": {
            onclick: "delete_selected_items(this)"
        }
    }],
    bottom_widgets: [{
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
function open_page(str,title,id){
    if (id) {
        str = list_panel.detail_data[id].notice_content;
        title = list_panel.detail_data[id].notice_title;
    }
    OpenWindow=window.open("", "newwin", "height=500, width=1000,top=200, left= 310"); 
　　//写成一行 
// 　　OpenWindow.document.title = title + ' - 实时预览';
    OpenWindow.document.write("<TITLE>"+ title +"</TITLE>");
　　OpenWindow.document.write('<h1 style="text-align: center;">'+title+'</h1>'); 
// 　　OpenWindow.document.write(str); 
　　OpenWindow.document.write('<p style="padding: 0px 13%;">'+str+'</p>'); 

　　OpenWindow.document.write("</BODY>") ;
　　OpenWindow.document.write("</HTML>") ;
　　OpenWindow.document.close() ;
}
function reviewPage(){
    var notice_content = $("#notice_content").val();
    notice_content = notice_content.replace(/\n/g,'<br/>');
    var notice_title = $("#notice_title").val();

    open_page(notice_content,notice_title);
}

function add_CA_file(){
    $("#add_panel_body_form_id_for_add_panel").submit();

    add_panel.hide();
}