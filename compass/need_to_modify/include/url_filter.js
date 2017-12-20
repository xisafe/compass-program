$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    user_group_panel = new PagingHolder( user_group_panel_config);
    url_classify_panel = new PagingHolder(url_classify_panel_config);
    message_manager = new MessageManager( message_box_config );
    SrcIPGroup_panel = new PagingHolder(SrcIPGroup_config);
    DestIPGroup_panel = new PagingHolder(DestIPGroup_config);
    
    /* 渲染面板 */
    add_panel.render();
    list_panel.render();
    message_manager.render();
    user_group_panel.render();
    url_classify_panel.render();
    SrcIPGroup_panel.render();
    SrcIPGroup_panel.hide();
    DestIPGroup_panel.render();
    DestIPGroup_panel.hide();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    user_group_panel.set_ass_message_manager( message_manager );
    url_classify_panel.set_ass_message_manager( message_manager );
    add_panel.hide();
    user_group_panel.hide();
    url_classify_panel.hide();
    list_panel.update_info(true);
    // single_select();
    $("#search_key_for_list_panel").css("font-size","5px");
    $("#search_key_for_list_panel").attr("placeholder","支持名称,源IP,URL分类,URL类型查询");

    $("#ip_group_value,#SrcUserlist,#user_group_btn,#single_time_value,#circle_time_value").attr("disabled",true);
    $("#user_group_btn").removeClass("add-panel-form-button").addClass("add-panel-form-disabled-button");
    $(".ctr_inpt").css("width","50px");
    $("#list_panel_id_for_url_classify_panel .container-main-body").empty().append('<div id="urlTree"></div>');
    
});

var ass_url = "/cgi-bin/url_filter.cgi";

var edit_id = "";
var list_panel;
var add_panel;
var user_group_panel;
var message_manager;
var SrcIPGroup_panel;
var DestIPGroup_panel;
var userid = "";
var message_box_config = {
    url: "/cgi-bin/url_filter.cgi",
    check_in_id: "mesg_box_tmp",
    panel_name: "my_message_box",
}
var user_group_panel_config = {
    url: "/cgi-bin/url_filter.cgi",
    check_in_id: "panel_uesr_group",
    panel_name: "user_group_panel",
    page_size: 0,
    panel_title: "配置用户组",
    is_panel_stretchable:true,
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    is_first_load: true,
    // render: monitoring_object_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            if(edit_id == ""){ //添加
                if(list_obj.panel_config.is_first_load){
                    get_init_data_tree();
                    list_obj.panel_config.is_first_load = false;
                }else{
                    var $zone_tree_root = $($('#list_panel_id_for_user_group_panel').find('.toolbar')[0]);
                    if($zone_tree_root){
                        $zone_tree_root.jstree(zone_tree_config);
                        $zone_tree_root.jstree(true).deselect_all();//PT:clear all checked nodes
                        // $zone_tree_root.jstree("select_node",object_selected);//PT:check some nodes
                        $zone_tree_root.jstree("open_all");
                    }
                }
            }else{   //编辑
                get_init_data_tree(edit_id);
            }
            
        },
        after_load_data: function( list_obj,data_item ) {
           
        }
    },
    panel_header: [{
        enable: false,
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: false,
        type: "text",
        title: "用户组",
        name: "user_name"
    }],
    bottom_extend_widgets: {
        class: "add-panel-footer",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_checked_for_jstree(user_group_panel,'SrcUserlist','user')"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "user_group_panel.hide();"
            }
        }]
    } 
};

var url_classify_panel_config = {
    url: "/cgi-bin/url_filter.cgi",
    check_in_id: "panel_url_classify",
    panel_name: "url_classify_panel",
    page_size: 0,
    panel_title: "配置URL分类",
    is_panel_stretchable:true,
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    is_first_load: true,
    // render: monitoring_object_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
          
        },
        after_load_data: function( list_obj,data_item ) {
           
        }
    },
    panel_header: [{
        enable: false,
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: false,
        type: "text",
        title: "用户组",
        name: "user_name"
    }],
    bottom_extend_widgets: {
        class: "add-panel-footer",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_checked_jstree(url_classify_panel,'url_classify','urltype')"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "url_classify_panel.hide();"
            }
        }]
    }  
};


var add_panel_config = {
    url: "/cgi-bin/url_filter.cgi",
    check_in_id: "panel_tmp_add",
    panel_name: "add_panel",
    rule_title: "URL过滤",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {
         


          // 行为按钮也必须选择一样
           var action_length = $("input[name='url_type']:checked").length;
           if( action_length == 0 ){
                message_manager.show_popup_note_mesg( "至少选择一种类型！" );
               return false;
           }


          // 动作按钮也必须选择一样
          var action_length = $("input[name='action_permission']:checked").length;
          if( action_length == 0 ){
               message_manager.show_popup_note_mesg( "至少选择一个动作" );
              return false;
          }

          // 将edit_id置空
          edit_id = "";


        },
        before_load_data: function( add_obj,data_item ) {
            //console.log(data_item.url_type);
          
           // read_data();
        },
        after_load_data: function( add_obj,data_item ) {

            select_items(data_item.dest_ipgroup,'dest_ipgroup');
            select_items(data_item.ip_or_user,'ip_or_user');
            select_items(data_item.time_plan,'time_plan');
            select_items(data_item.service_or_app,'service_app');

            var ip_mac_text = $('#sour_netip_text,#sour_mac_text,#dest_ip_text');
            for (var i = 0; i < ip_mac_text.length; i++) {
                var text_val = $(ip_mac_text[i]).val();
                text_val = text_val.replace(/\s/g,'');
                text_val = text_val.replace(/\,|，/g,'\n');
                $(ip_mac_text[i]).val(text_val);
            }
            //   if(data_item.url_type=="ALL"){
            //     //$("#url_type_https").attr("checked",'true');
            //     $("input[id='url_type_https']:checked");
            // }

           
        },
        after_cancel_edit: function( add_obj ) {  
          // 将edit_id置空
          edit_id = "";
          $("#SrcIPGroup,#SrcIPGroup_btn,#SrcUserlist,#SrcUserlist_btn,#sour_netip_text,#sour_mac_text").hide();
          $("#DestIPGroup,#ipGroup,#dest_ip_text").hide();
          $("#ServiceName,#ServiceName_btn,#Appname,#Appid_btn").hide();
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
            title: "描述",
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
                        required:'0',
                        check:"note",
                        ass_check:function( check ){
                            
                        }
                    }

                }
            ]
        },
        {
        title: "源IP/组/用户",
        sub_items: [{
            enable: true,
            type: "items_group",
            style: " margin:-5px;",
            sub_items: [{
                enable: true,
                type: "select",
                id: "ip_or_user",
                name: "ip_or_user",
                value: "",
                style: "width:69px;   vertical-align: text-top;",
                functions: {
                    onchange: "select_items(this.value,this.id);"
                },
                options: [{
                        text: "任意",
                        id: "sour_any",
                        value: "sour_any",
                        functions: {}
                    }, {
                        text: "IP组",
                        id: "sour_ip",
                        value: "sour_ip",
                        functions: {}
                    }, {
                        id: "sour_user",
                        text: "用户",
                        value: "sour_user",
                        functions: {},
                    }, {
                        text: "网络/IP",
                        id: "sour_netip",
                        value: "sour_netip",
                        functions: {}
                    }

                ]
            }, {
                enable: true,
                id: "SrcIPGroup",
                name: "SrcIPGroup",
                type: "text",
                readonly: "readonly",
                style: "height:16px;width:117px;display:none;",
                check: {
                        type:'text',
                        required:'1',
                        check: 'other|',
                        other_reg: '/.*/',
                        ass_check:function( check ){
                            
                        }
                    }



            }, {
                enable: true,
                id: "SrcIPGroup_btn",
                name: "user_group_btn",
                type: "button",
                class: "set-button",
                value: "配置",
                functions: {
                    onclick: "show_config_panel(SrcIPGroup_panel,'SrcIPGroup')"
                },
                style: "width:40px;height:20px;border-radius:4px;display:none;"
            }, {
                enable: true,
                id: "SrcUserlist",
                name: "SrcUserlist",
                type: "text",
                readonly: "readonly",
                style: "height:16px;width:117px;display:none;",
                check: {
                        type:'text',
                        required:'1',
                        check: 'other|',
                        other_reg: '/.*/',
                        ass_check:function( check ){
                            
                        }
                    }


            }, {
                enable: true,
                id: "SrcUserlist_btn",
                name: "user_group_btn",
                type: "button",
                class: "set-button",
                value: "配置",
                functions: {
                    onclick: "load_jstree_panel(user_group_panel,'load_userlist','SrcUserlist','user')"
                },
                style: "width:40px;height:20px;border-radius:4px;display:none;"
            }, {
                enable: true,
                // label: "请填写IP(每行一个)",
                type: "textarea",
                // tip: "请填写IP(每行一个)",
                id: "sour_netip_text",
                name: "sour_netip_text",
                placeholder: "请填写IP(每行一个)",
                style: "width:119px;display:none;vertical-align: middle;",
                readonly: false,
                check: {
                    type: 'textarea',
                    required: '1',
                    check: 'ip|ip_addr_segment',
                    ass_check: function(check) {

                    }
                }
        
            }]


        }]
    },{
        title: "目标IP/组",
        enable:false,
        sub_items: [{
                enable: false,
                type: "items_group",
                style: " margin:-5px;",
                sub_items: [{
                    enable: false,
                    type: "select",
                    id: "dest_ipgroup",
                    name: "dest_ipgroup",
                    value: "",
                    style: "width:69px;   vertical-align: text-top;",
                    functions: {
                        onchange: "select_items(this.value,this.id);"
                    },
                    options: [{
                        text: "任意",
                        id: "dest_any",
                        value: "dest_any",
                        functions: {}
                    }, {
                        text: "IP组",
                        id: "dest_ip",
                        value: "dest_ip",
                        functions: {}
                    }, {
                        text: "网络/IP",
                        id: "dest_group",
                        value: "dest_group",
                        functions: {}
                    }]
                }, {
                    enable: false,
                    type: "text",
                    id: "DestIPGroup",
                    style: "width:117px;display:none;",
                    readonly: "readonly",
                    name: "DestIPGroup",

                }, {
                    enable: false,
                    type: "button",
                    value: "配置",
                    id: "ipGroup",
                    name: "ipGroup",
                    functions: {
                        onclick: "show_config_panel(DestIPGroup_panel,'DestIPGroup')"
                    },
                    style: "width:40px;height:20px;border-radius:4px;display:none;"

                }, {
                    enable: false,
                    // label: "请填写IP(每行一个)",
                    type: "textarea",
                    // tip: "请填写IP(每行一个)",
                    id: "dest_ip_text",
                    name: "dest_ip_text",
                    placeholder: "请填写IP(每行一个)",
                    style: "width:119px;display:none;vertical-align: middle;",
                    readonly: false,
                    check: {
                        type: 'textarea',
                        required: '0',
                        check: 'ip|ip_addr_segment',
                        ass_check: function(check) {

                        }
                    }
                }]
            }

        ]
    },{
            title: "URL分类*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    //multiple: true,
                    style: "",
                    id: "url_classify",
                    name: "url_classify",
                    readonly:"readonly",
                    functions: {
                    
                    },
                    check: {
                        type: 'text',
                        required: '1',
                        check: 'other|',
                        other_reg: '/.*/',
                        ass_check: function(check) {

                        }
                    }

                },
                 {
                        enable:true,
                        id:"url_classify_btn",
                        name:"url_classify_btn",
                        type:"button",
                        value:"配置",
                        functions:{
                            onclick:"load_jstree_panel_url(url_classify_panel,'read_data','url_classify','urltype')"
                        },
                        style:"width:40px;height:20px;border-radius:4px"
                    },
            ]
        },
        {
            title: "类型*",
            sub_items: [
               {
                            enable:true,
                            type:"checkbox",
                            id:"url_type_get",
                            name:"url_type",
                            label:"HTTP(GET)",
                            value:"GET",
                        },
                        {
                            enable:true,
                            id:"url_type_post",
                            name:"url_type",
                            label:"HTTP(POST)",
                            type:"checkbox", 
                            value:"POST",  
                      }, {
                            enable:true,
                            id:"url_type_https",
                            name:"url_type",
                            label:"HTTP+HTTPS",
                            type:"checkbox", 
                            value:"ALL", 
                            functions:{
                              onclick:"https_select();"
                        } 
                      }
                      ]
        },
      {
            title: "生效时间",
            enable:false,
            sub_items: [
                {
                    enable: false,
                    type: "items_group",
                    style: "height:30px;line-height:20px",
                    sub_items:[{
                        enable:false,
                        id:"effect_time_single",
                        name:"single_or_circle",
                        label:"单次时间计划",
                        type:"radio",
                        // checked:true,
                        value:"single_plan",
                        functions:{
                            onclick:"single_select(this.value);"
                        }

                    },
                    {
                        enable:false,
                        id:"single_time_value",
                        name:"single_time_value",
                        type:"select",
                        check:{
                            
                        }
                    }]

                },{
                   enable: false,
                    type: "items_group",
                    style: "height:30px;line-height:20px",
                    sub_items:[{
                        enable:false,
                        id:"effect_time_circle",
                        name:"single_or_circle",
                        label:"循环时间计划",
                        type:"radio",
                        value:"circle_plan",
                        functions:{
                            onclick:"single_select(this.value);"
                        }
                    },
                    {
                        enable:false,
                        id:"circle_time_value",
                        name:"circle_time_value",
                        type:"select",
                        check:{
                          
                        }
                    }] 
                }
            ]
        },
        {
            title:"动作*",
            sub_items:[{
                        enable:true,
                        label:"允许",
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
                    }]
        },
        {
            title:"日志",
            sub_items:[{
                enable:true,
                type:"checkbox",
                label:"记录",
                id:"is_record",
                name:"is_record",
                value:"0",
            }]
    },
    {
            title:"启用",
            sub_items:[{
                enable:true,
                type:"checkbox",
                name:"enable",
                id:"enable",
                value:"0"
            }]
    }]
};

var SrcIPGroup_render = {
    /*'protocol': {
         render: function( default_rendered_text, data_item ) {
             var result_render = "RIP";
             return '<span>' + result_render + '</span>';
         },
     },*/

};

var SrcIPGroup_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "SrcIPGroup_panel", // ***必填***，确定面板挂载在哪里 
    page_size: 10, //===可选===，定义页大小，默认是15 
    panel_name: "SrcIPGroup_panel", // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true, // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置源IP",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    render: SrcIPGroup_render, //===可选===，渲染每列数据 
    panel_header: [ // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": true, //用户控制表头是否显示
            "type": "checkbox", //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "", //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox", //用户装载数据之用
            "class": "", //元素的class
            "td_class": "align-center", //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%", //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": { //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": false,
            "type": "radio",
            "name": "radio",
            "td_class": "rule-listbc",
            "width": "5%"
        }, {
            "enable": true,
            "type": "name",
            "title": "源IP名称", //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "30%"
        }
    ],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            class: "",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_checked_for_list(SrcIPGroup_panel, 'SrcIPGroup')"
            }
        }, {
            enable: true,
            type: "image_button",
            class: "",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "SrcIPGroup_panel.hide();"
            }
        }]
    }
}

var DestIPGroup_render = {
    /*'protocol': {
         render: function( default_rendered_text, data_item ) {
             var result_render = "RIP";
             return '<span>' + result_render + '</span>';
         },
     },*/

};

var DestIPGroup_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "DestIPGroup_panel", // ***必填***，确定面板挂载在哪里 
    page_size: 10, //===可选===，定义页大小，默认是15 
    panel_name: "DestIPGroup_panel", // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true, // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置目标IP",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    render: DestIPGroup_render, //===可选===，渲染每列数据 
    panel_header: [ // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": true, //用户控制表头是否显示
            "type": "checkbox", //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "", //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox", //用户装载数据之用
            "class": "", //元素的class
            "td_class": "align-center", //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%", //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": { //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": false,
            "type": "radio",
            "name": "radio",
            "td_class": "rule-listbc",
            "width": "5%"
        }, {
            "enable": true,
            "type": "name",
            "title": "目标IP名称", //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "30%"
        }
    ],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            class: "",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_checked_for_list(DestIPGroup_panel, 'DestIPGroup')"
            }
        }, {
            enable: true,
            type: "image_button",
            class: "",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "DestIPGroup_panel.hide();"
            }
        }]
    }
}

var list_panel_render = {
    'url_type':{
        render: function(default_text,data_item){
            var rendered_text = default_text;
            // if( rendered_text != "GET" && rendered_text != "POST"){
            if( rendered_text == "GET|POST"){
                rendered_text = "GET&POST";
            }
            else if(rendered_text == "ALL"){
                rendered_text = "ALL";
            }
            return rendered_text;
        }
    },
    'target_ipgroups':{
        render: function(default_rendered_text, data_item) {
            // data_item.Dest_IP_Group = data_item.Dest_IP_Group.replace(/\,/g,', ');
            // data_item.Dest_IP_Group = data_item.Dest_IP_Group.replace(/\，/g,', ');
            if (data_item.dest_ipgroup == 'dest_any') {
                return '<font style="color:green;">'+data_item.target_ipgroups+'</font>';
            }else if(data_item.dest_ipgroup == 'dest_group'){
                return '<font style="color:green;">网络/IP: </font>'+data_item.target_ipgroups;
            }else{
                return '<font style="color:green;">IP: </font>'+data_item.target_ipgroups;
            }
        }
    },
        'IpOrUser':{
        render: function(default_rendered_text, data_item) {
            data_item.IpOrUser = data_item.IpOrUser.replace(/\,/g,', ');
            data_item.IpOrUser = data_item.IpOrUser.replace(/\，/g,', ');
            if (data_item.ip_or_user == 'sour_user') {
                return '<font style="color:green;">用户: </font>'+data_item.IpOrUser;
            }else if(data_item.ip_or_user == 'sour_mac'){
                return '<font style="color:green;">MAC: </font>'+data_item.IpOrUser;
            }else if(data_item.ip_or_user == 'sour_netip'){
                return '<font style="color:green;">网络/IP: </font>'+data_item.IpOrUser;
            }else if(data_item.ip_or_user == 'sour_ip'){
                return '<font style="color:green;">IP: </font>'+data_item.IpOrUser;
            }else if(data_item.ip_or_user == 'sour_any'){
                return '<font style="color:green;">'+data_item.IpOrUser+'</font>';
            }
        }
    },
    'is_record':{
        render: function(default_text,data_item){
            var rendered_text = default_text;
            if( rendered_text == "0"){
                rendered_text = "开启";
            }
            else{
                rendered_text = "未开启";
            }
            return rendered_text;
        }
    },
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
            if( rendered_text == "0"){
                rendered_text = "启用";
            }
            else{
                rendered_text = "未启用";
            }
            return rendered_text;
        }
    }
   
};


var list_panel_config = {
    url: "/cgi-bin/url_filter.cgi", /* ***必填***，控制数据在哪里加载 */
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
            "td_class": "align-center",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
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
            "width": "12%"
        },{
        enable: true,
        type: "text",
        title: "描述",
        name: "description",
        width: "15%"
        },{
            "enable": true,
            "type": "text",
            "title": "源IP/组/用户",
            "name": "IpOrUser",
            "width": "25%"
        },{
            "enable": false,
            "type": "text",
            "title": "目标IP",
            "name": "target_ipgroups",
            "width": "15%"
        },  
        {
            "enable": true,
            "type": "text",
            "title": "URL分类",
            "name": "url_classify",
            "width": "10%"
        },
        {
            "enable": true,
            "type": "text",
            "title": "类型",
            "name": "url_type",
            "width": "10%",
            "td_class":"align-center"
        },
        {
            "enable": false,
            "type": "text",
            "title": "生效时间",
            "name": "effect_time",
            "width": "10%",
            "td_class":"align-center"
        },
        {
            "enable": true,
            "type": "text",
            "title": "日志",
            "name": "is_record",
            "width": "5%",
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
        
        },
    },
    
}
function load_jstree_panel_url(panel,action,input_id,img){

    var sending_data = {
        ACTION: action
    };

    function ondatareceived(data) {
        data= data.url_classify_data;
        data.state={};
        data = change_jstree(input_id,data);
        jstreeRender(panel,data,img);
        panel.show();
    }
    do_request(sending_data, ondatareceived);
}
function change_jstree(input_id,data){
    var input_val = $('#'+input_id).val();
    if (input_val != '') {
        var input_arr = /\,/.test(input_val) ? input_val.split(',') : input_val.split('|');
        input_arr = input_arr.map(function(ele, index) {
            return ele.trim();
        });
        data.state = {opened : true} ;
        for (var i = 0; i < data.children.length; i++) {
            // for (var j = 0; j < data.children[i].children.length; j++) {
                var data_text = data.children[i].text.replace(/\n/,'');
                if ($.inArray(data_text,input_arr) != -1) {
                    data.children[i].state = { 'selected' : true} ;
                }
            // }
        }
    }
    return data;
}
//渲染JS树
function jstreeRender(panel,data,img,type) {
    var jstree_id = 'jstree_' + panel.panel_name ;
    if ($('#'+jstree_id)) {$('#'+jstree_id).remove()};
    var jstree_div = '<div id="'+jstree_id+'"></div>';
    var panel_id = panel.panel_id;
    $('#'+panel_id + ' .container-main-body').append(jstree_div).css('min-height', '200px').children('.rule-list').remove();
    data = Array.isArray(data) ? data : [data] ;
    var i_d_a = "../images/";
    icon = {'user':i_d_a+"login_user.png",'app':i_d_a+'application.png','urltype':i_d_a+'applications-blue.png'}[img] || i_d_a+img;
    var jstree_obj = {
        "plugins": [
            "checkbox","types", "wholerow"
        ],
        "core": {
            "themes": {
                "stripes": true
            },
            "data": data
        },
        "types":{},
        "checkbox": {
            "keep_selected_style": false
        },
    }
    type ? jstree_obj.types[type] = {'icon':icon} : jstree_obj.types[img] = {'icon':icon}
    $('#'+jstree_id).jstree(jstree_obj);
}

function write_checked_jstree(panel,input_id,type,id_id){
    var jstree_id = 'jstree_' + panel.panel_name ;
    var checked_nodes = $('#'+jstree_id).jstree().get_checked(true);
    var checked_str = '',checked_id_str = '',temp = 0;
    for (var i = 0; i < checked_nodes.length; i++) {
        if (checked_nodes[i].type == type) {
            var separator = temp == 0 ? '' : ', ';
            temp++ ;
            checked_str += separator ;
            checked_str += checked_nodes[i].text.replace(/\n/,'') ;
            if (id_id) {
                // var id_separator = i == 0 ? '':',';
                // checked_id_str += id_separator ;
                checked_id_str += separator;
                checked_id_str += checked_nodes[i].id ;
            }
        }
    }
    if (checked_str == '') {
        message_manager.show_popup_error_mesg("没有明确的选项！");
        return;
    }
    $('#'+input_id).val(checked_str).attr('title',checked_str);
    id_id ? $('#'+id_id).val(checked_id_str) : true;
    panel.hide();
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
    // read_data();
    add_panel.show();
    $("[name='url_type']").removeAttr("disabled");
    $("#ip_group_value,#SrcUserlist,#user_group_btn,#single_time_value,#circle_time_value").attr("disabled",true);
    $("#user_group_btn").removeClass("add-panel-form-button").addClass("add-panel-form-disabled-button");

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

//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/url_filter.cgi",
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

function select_items(val, id) {

    var select_obj = {
        'ip_or_user': {
            'sour_ip': '#SrcIPGroup,#SrcIPGroup_btn',
            'sour_user': '#SrcUserlist,#SrcUserlist_btn',
            'sour_netip': '#sour_netip_text',
            'sour_mac': '#sour_mac_text'
        },
        'dest_ipgroup': {
            'dest_ip': '#DestIPGroup,#ipGroup',
            'dest_group': '#dest_ip_text'
        },
        'service_app': {
            'service': '#ServiceName,#ServiceName_btn',
            'app': '#Appname,#Appid_btn'
        },
        'time_plan': {
            'single_plan': '#singletime',
            'circle_plan': '#looptime'
        }
    };
    select_and_show(val,id,select_obj)

}

//为所有配置按钮初始化样式
function set_button() {

    $(".set-button").addClass("add-panel-form-button").removeClass("add-panel-form-disabled-button");
}

function https_select(){

    if($("#url_type_https").is(":checked")){
        $('#url_type_get').attr("disabled",true);
        $('#url_type_post').attr("disabled",true);
    }
    else{
        $('#url_type_get').removeAttr("disabled");
        $('#url_type_post').removeAttr("disabled");
    }

}