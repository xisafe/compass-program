$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    // show_panel = new PagingHolder ( show_panel_config);
	detail_panel = new RuleAddPanel( detail_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    add_panel.render();
    list_panel.render();
	detail_panel.render();
    message_manager.render();


    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    add_panel.hide();
	detail_panel.hide();
    
    list_panel.update_info(true);
    
    $(".ctr_inpt").css("width","50px");
});

/*
 * 加载Ext所需文件
 */
// Ext.require([
//     'Ext.data.TreeStore',
//     'Ext.tree.Panel',
//     'Ext.form.ComboBox',
//     'Ext.form.Panel',
//     'Ext.window.Window'
// ]);

var list_panel;
var add_panel;
var detail_panel;
// var show_panel;
var message_box_config = {
    url: "/cgi-bin/file_type_group.cgi",
    check_in_id: "mesg_box_tmp",
    panel_name: "my_message_box",
}
var message_manager;

var add_panel_config = {
    url: "/cgi-bin/file_type_group.cgi",
    check_in_id: "panel_tmp_add",
    panel_name: "add_panel",
    rule_title: "文件类型组",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {
           

        },
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
           
        },
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "文件类型组名称*:",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "name",
                    name: "name",
                    value: "",
                    tip: "最多20个字符！",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'name',
                        //other_reg:'!/^\$/',
                        ass_check: function( check ) {
                            var val = $("#name").val();
                            if(val.length>20){
                                return "最多20个字符！"
                            }
                        }
                    }
                }
            ]
        },
        {
            title: "文件类型组描述",
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
                        check:'other|',
                        other_reg:'!/^\$/',
                        ass_check: function( check ) {
                            var val = $("#description").val();
                            if(val.length>40){
                                return "最多40个字符！"
                            }
                        }
                    }
                }
            ]
        },
        {
            title: "文件类型(后缀名):",
            sub_items: [
                {
                    enable: true,
                    // type:"textarea",
                    type:"select",

                    style: "",
                    id: "extentions",
                    name: "extentions",
                    value: "",
                    // tip: "每行一个",
                    check: {
                        type: "select-one",
                        required: '1',
                        check:'',
                        ass_check: function( check ) {

                        }
                    }  
                }
            ]
        }
        
    ]
};
// var show_panel_config = {
//     url: "/cgi-bin/file_type_group.cgi", 
//     check_in_id: "panel_tmp_list", 
//     panel_name: "list_panel",

// }
var list_panel_render = {
    'checkbox': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if( data_item.flag == "0" ){
                result_render = "";
            }else{
                result_render = default_rendered_text;
            }
            return result_render;
        }
    },
    'flag': {
        render:function( default_rendered_text, data_item) {
            var render_text = data_item.flag;
            if(render_text == "1"){
                render_text = "自定义";
            }
            else{
                render_text = "内置";
            }
            return render_text;
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
			if( data_item.flag == "0"){
				 var action_buttons = [
				   {
						"enable": true,
						"id": "edit_item",
						"name": "edit_item",
						"button_icon": "edit.png",
						"button_text": "查看详情",
						"value": data_item.id,
						"functions": {
							onclick: "onFun(this.value);"
						},
						 "class": "action-image",
					},
					{
						"enable": true,
						"id": "delete_item",
						"name": "delete_item",
						"button_icon": "delete_disabled.png",
						"button_text": "不能删除",
						 "class": "action-image",
					}
				];
		   }
		   else{
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
			}
			return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/file_type_group.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_tmp_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        // {
        //     "enable": true,            //用户控制表头是否显示
        //     "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        //     "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        //     "name": "checkbox",         //用户装载数据之用
        //     "class": "",                //元素的class
        //     "td_class": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
        //     "width": "2%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
        //     "functions": {              //一般只有checkbox才会有这个字段
        //     }
        // }, 
        {
            "enable": true,
            "type": "text",
            "title": "序号",        //一般text类型需要title,不然列表没有标题
            "name": "index",
            "width": "5%",
            "td_class":"align-center"
        },{
            "enable": true,
            "type": "text",
            "title": "名称",        //一般text类型需要title,不然列表没有标题
            "name":  "name",
            "width": "20%"
        },
        {
            "enable": true,
            "type": "text",
            "title": "描述",
            "name": "description",
            "width": "60%"
        },
        {
            "enable": true,
            "type": "text",
            "title": "类型",
            "name": "flag",
            "width": "5%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "10%",
            "td_class":"align-center"
        }
    ],
    // top_widgets: [                  /* ===可选=== */
        // {
            // enable: true,
            // type: "image_button",
            // button_icon: "add16x16.png",
            // button_text: "新建",
            // functions: {
                // onclick: "add_rule(this);"
            // }
        // },功能不可用 暂时屏蔽
        // {
            // "enable": true,
            // type: "image_button",
            // "id": "delete_selected",
            // "name": "delete_selected",
            // "class": "",
            // "button_icon": "delete.png",
            // "button_text": "删除选中",
            // "functions": {
                // onclick: "check_delete_selected_items()"
            // }
        // }
    // ],
    event_handler:{
         after_load_data: function( add_obj,data_item ) {
           
        },
    },
    is_default_search: false,          /* ===可选===，默认是true，控制默认的搜索条件 */
    
}

var detail_panel_config = {
    url: "/cgi-bin/file_type_group.cgi",
    check_in_id: "detail_panel",
    panel_name: "detail_panel",
    rule_title: "查看详情",
	rule_title_editing_prefix: "",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {

        },
        before_load_data: function( add_obj,data_item ) {
			data_item.extentions = data_item.extentions.toLocaleLowerCase();
            var data_arr = data_item.extentions.split('\n');
            var ipgroups_option_str = '<option selected>点击查看</option>';
            for(var i = 0; i < data_arr.length; i++ ){
                ipgroups_option_str += '<option value="'+data_arr[i] +'">'+data_arr[i]+'</option>';    
            }

            $("#extentions1").html('');
            $("#extentions1").append(ipgroups_option_str);
        },
        after_load_data: function( add_obj,data_item ) {
           
        },
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
	footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add_btn: false,
        cancel_btn: false,
        import_btn: false
    },
    items_list: [
        {
            title: "文件类型组名称*:",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "name",
                    name: "name",
					readonly: "readonly"
                }
            ]
        },
        {
            title: "文件类型组描述",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "description",
                    name: "description",
					readonly: "readonly"
                }
            ]
        },
        {
            title: "文件类型(后缀名):",
            sub_items: [
                {
                    enable: true,
                    type:"select",
                    id: "extentions1",
                    name: "extentions1",
					readonly: "readonly",
                }
            ]
        }
        
    ]
};

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

// function create_action_buttons( action_buttons ) {
//     var buttons = "";

//     if( action_buttons === undefined ) {
//         return buttons;/*如果没有定义相应的对象，直接返回*/
//     }

//     for( var i = 0; i< action_buttons.length; i++ ) {
//         var item = action_buttons[i];
//         if( item.enable === undefined || !item.enable ){
//             continue;
//         }
//         buttons += '<input type="image" ';
//         if( item.id !== undefined && item.id ) {
//             buttons += 'id="' + item.id + '" ';
//         }
//         if( item.value !== undefined && item.value ) {
//             buttons += 'value="' + item.value + '" ';
//         }
//         if( item.name !== undefined && item.name ) {
//             buttons += 'name="'+ item.name +'" ';
//         }
//         if( item.class !== undefined && item.class ) {
//             buttons += 'class="action-image ' + item.class + '" ';
//         } else {
//             buttons += 'class="action-image" ';
//         }
//         if( item.button_text !==undefined && item.button_text ) {
//             buttons += 'title="' + item.button_text + '" ';
//         }
//         if( item.button_icon !== undefined && item.button_icon ) {
//             buttons += 'src="../images/' + item.button_icon +'" ';
//         }
//         if( item.functions !== undefined && item.functions ) {
//             var functions = item.functions;
//             for ( var key in functions ) {
//                 buttons += key +'="' + functions[key] + '" ';
//             }
//         }
//         buttons += '/>';
//     }

//     return buttons;
// }

// function add_rule( element ) {
//     add_panel.show();
// }

function showDetailPage(id){
    list_panel.addDetail(id);    
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

//用于系统默认数据详情显示
var onFun = function(id) {
	detail_panel.edit_data(list_panel.detail_data[id-1]);
}