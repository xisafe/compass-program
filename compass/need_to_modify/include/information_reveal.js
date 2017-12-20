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
    // single_select();

	!function() {
		$("ip_group_value,#user_group_value,#single_time_value,#circle_time_value").attr("disabled",true);
		$(".ctr_inpt").css("width","50px");
		$("input[name='url_type']").bind('click', function(){
			$("input[name='url_type']").not(this).attr("checked", false);
		});	
		$("#protocolType").css("display", "none");
	}();
});
var list_panel;
var add_panel;
var analysis_panel;
var message_box_config = {
    url: "/cgi-bin/information_reveal.cgi",
    check_in_id: "mesg_box_tmp",
    panel_name: "my_message_box",
}
var message_manager;


var add_panel_config = {
    url: "/cgi-bin/information_reveal.cgi",
    check_in_id: "panel_tmp_add",
    panel_name: "add_panel",
    rule_title: "敏感信息",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {
          
          // 动作按钮也必须选择一样
          var action_length = $("input[name='action_permission']:checked").length;
          if( action_length == 0 ){
               message_manager.show_popup_note_mesg( "至少选择一个动作" );
              return false;
          }
		  

        },
        before_load_data: function( add_obj,data_item ) {
           console.log(data_item);
           read_data();
		   if(data_item.protocolType) {
			$("#protocolType").css("display", "inline-block");
		  }else {
			$("#protocolType").css("display", "none");
		  }
		},
        after_load_data: function( add_obj,data_item ) {
        
		
        },
        after_cancel_edit: function( add_obj ) {
        }
        
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list:[
        {
            title: "名称:",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "name",
                    name: "name",
                    value: "",
                    style: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'name|',
                        // other_reg:'^$',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "描述:",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    style: "", 
                    id: "description",
                    name: "description",
                    functions: {
                    
                    },
                      check: {
                        type:'text',
                        required:'1',
                        check:"note",
                        ass_check:function( check ){
                            
                        }
                    }

                }
            ]
        },
        {
            title: "IP组:",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    multiple: false,
                    style: "",
                    id: "ip_group_value",
                    name: "ip_group_value",
                    functions: {
                    
                    },
                    check: {
                        type:'select-one',
                        required:'1',
                        ass_check:function( check ){
                            
                        }
                    }

                }
            ]
        },
        {
            title: "敏感信息:",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    multiple: true,
                    style: "",
                    tip:"按住Ctrl键即可多选", 
                    id: "sens_info_type",
                    name: "sens_info_type",
                    functions: {
                    
                    },
                    check: {
                        type:'select-multiple',
                        required:'1',
                        ass_check:function( check ){
                            
                        }
                    }

                }
            ]
        },
        {
            title: "协议:",
            sub_items: [
                {
                    enable: true,
                    type: "select",
                    style: "", 
                    id: "protocol",
                    name: "protocol",
                    options:
                    [
                            {
                                text:"http",
                                value:"http"
                            },
                            {
                                text:"smtp",
                                value:"smtp"
                            },
                            {
                                text:"pop3",
                                value:"pop3"
                            }
                    ],
                    functions: {
						"onchange": "selectChange()"
                    },
                    check: {
                        type:'select-one',
                        required:'1',
                        ass_check:function( check ){
                            
                        }
                    }

                },{
					enable: true,
					type: "items_group",
					id: "protocolType",
					sub_items:[
						{
							enable: true,
							type: "radio",
							name: "protocolType",
							id: "tex",
							value: "tex",
							label: "邮件正文"
						},
						{
							enable: true,
							type: "radio",
							name: "protocolType",
							id: "sys",
							value: "sys",
							label: "邮件主题"
						},{
							enable: true,
							type: "radio",
							name: "protocolType",
							id: "sen",
							value: "sen",
							label: "发件人"
						},{
							enable: true,
							type: "radio",
							name: "protocolType",
							id: "rec",
							value: "rec",
							label: "收件人"
						}
					]
				}
            ]
        },
         {
            title: "阈值:",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    style: "", 
                    id: "gate",
                    name: "gate",
                    functions: {
                    
                    },
                      check: {
                        type:'text',
                        required:'1',
                        check:"int",
                        ass_check:function( check ){
                            
                        }
                    }

                }
            ]   
        },
        {
            title:"动作",
            sub_items:[{
                enable:true,
                type:"items_group",
                sub_items:[
                    {
                        enable:true,
                        label:"允许",
						checked: "checked",
                        type:"radio",
                        id:"permit",
                        name:"action_permission",
                        value:"0",
                    },
                    {
                        enable:true,
                        label:"拒绝",
                        type:"radio",
                        id:"forbid",
                        name:"action_permission",
                        value:"1",
                    }
                ]
            }]
        },
        {
            title:"启用",
            sub_items:[{
                enable:true,
                type:"checkbox",
                name:"enabled_status",
                id:"enabled_status",
                value:"on"
            }]
        }]
};

var list_panel_render = {
    // 'ip_or_user_value':{
    //     render: function( default_text,data_item){
    //         var rendered_text = default_text.split("|")[1];
    //         return rendered_text;

    //     }
    // },
    'action_permission':{
         render: function(default_text,data_item){
            var rendered_text = default_text;
            if( rendered_text == "0"){
                rendered_text = "允许";
            }
            else{
                rendered_text = "禁止";
            }
            return rendered_text;
        }
    },
    'enabled_status':{
         render: function(default_text,data_item){
            var rendered_text = default_text;
            if( rendered_text == "on"){
                rendered_text = "启用";
            }
            else{
                rendered_text = "未启用";
            }
            return rendered_text;
        }
    },
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
                    "class": "",
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
                    "class": "",
                }
            ];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/information_reveal.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_tmp_list",         /* ***必填***，确定面板挂载在哪里 */
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
            "class": "",                //元素的class
            "td_class": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "2%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": true,
            "type": "text",
            "title": "序号",        //一般text类型需要title,不然列表没有标题
            "name": "index",
            "width": "3%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "text",
            "title": "名称",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "27%"
        },
        {
            "enable": true,
            "type": "text",
            "title": "源IP",
            "name": "ip_group_value",
            "width": "15%"
        }, 
        {
            "enable": true,
            "type": "text",
            "title": "敏感信息类型",
            "name": "sens_info_type",
            "width": "25%"
        },
        {
            "enable": true,
            "type": "text",
            "title": "协议",
            "name": "protocol",
            "width": "5%"
        },
        {
            "enable": true,
            "type": "text",
            "title": "阈值",
            "name": "gate",
            "width": "3%",
            "td_class":"align-center"
        },
        {
            "enable": true,
            "type": "text",
            "title": "动作",
            "name": "action_permission",
            "width": "5%",
            "td_class":"align-center"
        },
        {
            "enable": true,
            "type": "text",
            "title": "状态",
            "name": "enabled_status",
            "width": "5%",
            "td_class":"align-center"
        },
        {
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
        },
        {
            "enable": true,
            type: "image_button",
            "id": "delete_selected",
            "name": "delete_selected",
            "class": "",
            "button_icon": "on.png",
            "button_text": "启用选中",
            "functions": {
                onclick: "enable_selected_items()"
            } 
        },
        {
            "enable": true,
            type: "image_button",
            "id": "delete_selected",
            "name": "delete_selected",
            "class": "",
            "button_icon": "off.png",
            "button_text": "禁用选中",
            "functions": {
                onclick: "disable_selected_items()"
            }
        }
    ],
    is_default_search: true,          /* ===可选===，默认是true，控制默认的搜索条件 */
    event_handler: {
        before_load_data: function( list_obj ) {
            
        },
        after_load_data: function ( list_obj, response ) {
          console.log(response);  
        },
    },
    
}
//选择用户组还是ip组
function single_select(element){
    if( element == "ip_group"  ){
        $("#ip_group_value").removeAttr("disabled");
        $("#user_group_value").val("");
        $("#user_group_value").attr("disabled",true);
    }
    else if(element == "user_group") {
        $("#user_group_value").removeAttr("disabled");
        $("#ip_group_value").val("");
        $("#ip_group_value").attr("disabled",true);
    }
    else if(element == "single_plan"){
       $("#single_time_value").removeAttr("disabled");
       $("#circle_time_value").val("");
       $("#circle_time_value").attr("disabled",true);
    }
    else{
        $("#circle_time_value").removeAttr("disabled");
        $("#single_time_value").val("");
        $("#single_time_value").attr("disabled",true);
    } 
}

function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    if ( checked_items.length < 1){
        message_manager.show_popup_note_mesg("至少选择一项！");
    }else{
         var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].id );
        }

        var ids = checked_items_id.join( "&" );
    
        list_panel.enable_item( ids );
    }
   
}

function disable_selected_items() {

    var checked_items = list_panel.get_checked_items();
    if ( checked_items.length < 1){
        message_manager.show_popup_note_mesg("至少选择一项！");
    }else{
        var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].id );
        }

        var ids = checked_items_id.join( "&" );

        list_panel.disable_item( ids );
    }
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

function read_data(){
// 获取数据
    var sending_data = {
        ACTION: "read_data"
    }

    function ondatareceived( data ) {
        console.log(data);
        var ipgroups_option_str = '<option value="" disabled selected>请选择源ip组</option>';
        var sens_info_type_option_str = '<option value="" disabled selected>请选择敏感信息类型</option>';
        for(var i = 0; i < data.ipgroups_data.length; i++ ){
            ipgroups_option_str += '<option value="'+data.ipgroups_data[i] +'">'+data.ipgroups_data[i]+'</option>';    
        }
        for(var i = 0; i < data.sens_info_type.length; i++ ){
            sens_info_type_option_str += '<option value="'+data.sens_info_type[i]+'">'+data.sens_info_type[i]+'</option>';    
        }
        
        $("#ip_group_value").html('');
        $("#sens_info_type").html('');
        
        $("#ip_group_value").append(ipgroups_option_str);
        $("#sens_info_type").append(sens_info_type_option_str);
       
    }

    list_panel.request_for_json( sending_data, ondatareceived );
}

function add_rule( element ) {
    
    read_data();
	$("#protocolType").css("display", "none");
    add_panel.show();
}

//初始化小时和分钟的选项值
function select_options(val){
    var options = [];
    for(var i = 0; i<val; i++){
       var  option ={};
        i = i + "";
        if(i.length<2){
        i = "0"+i;
        }
        else{
        }
        option.value = i;
        option.text = i;
        options.push(option);
    }
    return options;
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
//检测协议选项变动来决定是否弹出过滤类型选项
function selectChange() {
	if($("#protocol")[0].selectedIndex == 2 || $("#protocol")[0].selectedIndex == 1) {
		$("#protocolType").css("display", "inline-block");
		$("#tex").prop("checked", true);
	}else {
		$("input[name='protocolType']").prop("checked", false);
		$("#protocolType").css("display", "none");
		
	}
}