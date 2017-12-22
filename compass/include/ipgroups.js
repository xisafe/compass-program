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
    
    $(".ctr_inpt").css("width","50px");
});
var list_panel;
var add_panel;
var analysis_panel;
var message_box_config = {
    url: "/cgi-bin/ipgroups.cgi",
    check_in_id: "mesg_box_tmp",
    panel_name: "my_message_box",
}
var message_manager;


var add_panel_config = {
    url: "/cgi-bin/ipgroups.cgi",
    check_in_id: "panel_tmp_add",
    panel_name: "add_panel",
    rule_title: "IP组设置",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {
           console.log(data_item);

        },
        before_load_data: function( add_obj,data_item ) {
            // console.log("加载前");
        },
        after_load_data: function( add_obj,data_item ) {
           // console.log("加载后");
        },
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "IP名称*",
            sub_items: [
                {
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
                        check:'name',
                        //other_reg:'!/^\$/',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "IP组描述",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    style: "",
                    id: "description",
                    name: "description",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 0,
                        check:'note',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "IP地址",
            sub_items: [
                {
                    enable: true,
                    type:"textarea",
                    style: "width: 198px",
                    tip:"每行一个",
                    id: "ip",
                    name: "ip",
                    value: "",
                    functions:{
                      
                    },
                    check: {
                        type: "textarea",
                        required: '1',
                        check:'ip|ip_range|ip_addr_segment|',
                        ass_check: function( check ) {

                        }
                    }  
                }
            ]
        }
        
    ]
};

var list_panel_render = {

    'action': {
        render: function( default_rendered_text, data_item ) {
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
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "value": data_item.id,
                    "functions": {
                        onclick: "check_delete_rule(this.value);"
                    },
                    "class": "action-image",
                }
            ];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/ipgroups.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_tmp_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持名称、IP、描述关键字查询",
        title: ""
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "class": "",                //元素的class
            "td_class": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": true,
            "type": "text",
            "title": "名称",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "10%",
            "class": "align-left"
        },{
            "enable": true,
            "type": "text",
            "title": "IP范围",        //一般text类型需要title,不然列表没有标题
            "name":  "ip",
            "width": "35%"
        },
        {
            "enable": true,
            "type": "text",
            "title": "描述",
            "class":"",
            "name": "description",
            "width": "40%"
        }, {
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
        },
        {
            "enable": true,
            type: "image_button",
            "id": "delete_selected",
            "name": "delete_selected",
            "class": "",
            "button_icon": "delete.png",
            "button_text": "删除选中",
            "functions": {
                onclick: "check_delete_selected_items()"
            }
        }
    ],
    bottom_widgets: [               /* ===可选=== */
        {
            "enable": false,
            "id": "export_selected",
            "name": "export_selected",
            "class": "",
            "button_icon": "download.png",
            "button_text": "导出选中",
            "functions": {
                onclick: "export_selected_items(this)"
            }
        }, {
            "enable": false,
            "id": "delete_all_logs",
            "name": "delete_all_logs",
            "class": "",
            "button_icon": "delete.png",
            "button_text": "清空日志",
            "functions": {
                onclick: "delete_all_logs(this)"
            }
        }
    ],
    is_default_search: true,          /* ===可选===，默认是true，控制默认的搜索条件 */
    
}

// function enable_selected_items() {
//     var checked_items = list_panel.get_checked_items();
//     var checked_items_id = new Array();
//     for( var i = 0; i < checked_items.length; i++ ) {
//         checked_items_id.push( checked_items[i].id );
//     }

//     var ids = checked_items_id.join( "&" );

//     list_panel.enable_item( ids );
// }

// function disable_selected_items() {
//     var checked_items = list_panel.get_checked_items();
//     var checked_items_id = new Array();
//     for( var i = 0; i < checked_items.length; i++ ) {
//         checked_items_id.push( checked_items[i].id );
//     }

//     var ids = checked_items_id.join( "&" );

//     list_panel.disable_item( ids );
// }

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

function add_rule( element ) {
    add_panel.show();
}






//删除规则函数，包含规则引用检查
function check_delete_rule(item_id){
    //var length_used_rule = [];
    var data_item = list_panel.get_item(item_id);
    //length_used_rule = data_item.rules_for_policy.split("&");
    if( data_item.rules_for_policy != "" ){
        list_panel.operate_item( data_item.id, 'delete_data',
        '策略模板正在被使用。删除该策略模板，也将删除使用该策略模板的规则', true );
    }else{
        list_panel.delete_item(data_item.id);
    }
}
//删除选中规则，包含规则引用检查
function check_delete_selected_items(){
    var checked_items = list_panel.get_checked_items();
    if(checked_items.length < 1){
        message_manager.show_popup_note_mesg("请先选中策略项");
        return;
    }
    var checked_items_id = new Array();
    var ids = "";
    var is_used = "no";
    var used_policy = new Array();
    for(var i=0;i<checked_items.length;i++){
        checked_items_id.push(checked_items[i].id);
        if(checked_items[i].rules_for_policy != ""){
            is_used = "yes";
            used_policy.push(checked_items[i].name);
        }
    }
    ids = checked_items_id.join("&");
    if(is_used == "yes"){
        list_panel.operate_item( ids, 'delete_data',used_policy.join("、")+
        '策略模板正在被使用。删除该策略模板，也将删除使用该策略模板的规则', true );
    }else{
        list_panel.delete_item(ids);
    }
}