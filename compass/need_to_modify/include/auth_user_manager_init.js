/*
 *
 *创建者：陈世松
 *谨慎删除注释，注释掉的内容可能为暂时屏蔽的功能！！！！！！！！！！！
 *2017.6.5
 *
 */


$(document).ready(function() {
    add_panel = new RuleAddPanel(add_panel_config);
    import_panel = new RuleAddPanel(import_panel_config);
    list_panel = new PagingHolder(list_panel_config);
    message_manager = new MessageManager(message_box_config);

    user_group_panel = new PagingHolder(user_group_panel_config);
    /* 渲染面板 */
    add_panel.render();
    import_panel.render();
    list_panel.render();
    user_group_panel.render();
    user_group_panel.hide();

    message_manager.render();
    init();

    $("#search_key_for_list_panel").attr("placeholder","输入用户名，老化时间，绑定信息关键字进行查询").width("295px");

    /* 设置面板关联 */
    add_panel.set_ass_list_panel(list_panel);
    import_panel.set_ass_list_panel(list_panel);
    list_panel.set_ass_add_panel(import_panel);
    list_panel.set_ass_add_panel(add_panel);

    add_panel.set_ass_message_manager(message_manager);
    import_panel.set_ass_message_manager(message_manager);
    list_panel.set_ass_message_manager(message_manager);
    import_panel.set_ass_message_manager(message_manager);

    add_panel.hide();
    import_panel.hide();
    list_panel.update_info(false);
    //得到树结构
    get_data_tree();
    //页面刷新时更新用户数据
    show_user_data();
    //创建页码所需的标签，由于树的加载是异步的，所以用settimeout将函数推至最后执行，否则树还没加载就无法创建标签
    // setTimeout('tree_append_num()',100);
    //刷新时更新用户数
    // setTimeout('show_user_num()',100);

    setTimeout('save_user_data()', 0);
    setTimeout('show_list_user()', 0);
    setTimeout('update_tree()', 0);

    import_panel_extendrender();



});


var list_panel;
var password_val;
var button_val = 0;
var add_panel;
var ass_url = "/cgi-bin/auth_user_manager.cgi";

var message_box_config = {
    url: ass_url,
    check_in_id: "mesg_box_user",
    panel_name: "my_message_user",
}
var message_manager;

var user_group_panel_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "user_group_panel", // ***必填***，确定面板挂载在哪里 
    page_size: 0, //===可选===，定义页大小，默认是15 
    panel_name: "user_group_panel", // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true, // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "分组列表",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 99
    },
    // render: Appid_render,      //===可选===，渲染每列数据 
    panel_header: [ // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": false, //用户控制表头是否显示
            "type": "checkbox", //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "", //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox", //用户装载数据之用
            "class": "", //元素的class
            "td_class": "", //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
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
            "enable": false,
            "type": "name",
            "title": "应用ID号", //一般text类型需要title,不然列表没有标题
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
                onclick: "move_to();"
            }
        }, {
            enable: true,
            type: "image_button",
            class: "",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "user_group_panel.hide();"
            }
        }]
    }
}

var add_panel_config = {
    url: ass_url,
    check_in_id: "panel_user_add",
    panel_name: "add_panel",
    rule_title: "认证用户",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 2
    },
    footer_buttons: { //需要向后台发送额外的sending_data，采用添加额外的隐藏按钮实现
        add: true,
        sub_items: [{
            enable: true,
            type: "hidden",
            name: "group_addr",
            value: "",

        }],
        cancel: true,
    },
    event_handler: {
        before_load_data: function(add_obj, data_item) {
            $("#pwd").attr('disabled', 'disabled');
            $("#pwd_again").attr('disabled', 'disabled');
        },
        after_load_data: function(add_obj, data_item) {
            $("#modify_passwd_button").val('更改密码');
            button_val = 0;
            password_val = $('#pwd').val();
            bindPass();
        },
        before_cancel_edit: function(add_obj) {

        },
        after_cancel_edit: function(add_obj) {
            elimPass();
        },
        before_save_data: function(add_obj, sending_data) {
            //提交用户前检查填写是否符合要求
            // return hintFill();

        },
        after_save_data: function(add_obj, received_data) {
            elimPass();
            //提交增加的用户之后，更新用户数量
            // show_user_num();
            var move_data = $("#cat_tree").jstree(true).get_selected()[0];
            var num = $('#' + move_data).find('small').eq(1);
            num.text(Number(num.text()) + 1);
            save_user_data();
            update_tree();
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        // {
        //     title: "用户策略",
        //     sub_items: [
        //         {
        //                 enable:true,
        //                 label:"有",
        //                 type:"radio",
        //                 id:"strategy_has",
        //                 checked: "checked",
        //                 name:"strategy",
        //                 style:"vertical-align: middle;margin-top: -7px;",
        //                 value:"1",
        //                 functions:{
        //                     onclick:"judgeStrategy(this.value);"
        //                 }
        //         },
        //         {
        //                 enable:true,
        //                 label:"无",
        //                 type:"radio",
        //                 id:"strategy_no",
        //                 name:"strategy",
        //                 style:"vertical-align: middle;margin-top: -7px;",
        //                 value:"0",
        //                 functions:{
        //                     onclick:"judgeStrategy(this.value);"
        //                 }
        //         }
        //     ]
        // },
        // {
        //     title: "名称",
        //     sub_items: [
        //         {
        //             enable: true,
        //             type: "text",
        //             tip: "（必填，1-20个字符）",
        //             id: "description",
        //             name: "description",
        //             value: "",
        //             functions: {
        //             },
        //             check: {
        //                 type: "text",
        //                 required: 1,
        //                 check:'other',
        //                 other_reg:'!/^\$/',
        //                 ass_check:function(eve){
        //                     var description = $("#description").val();
        //                     if(description.length < 1 || description.length > 20){
        //                         return "请输入1-20个字符！";
        //                     }
        //                 }
        //             }
        //         }
        //     ]
        // },
        {
            title: "用户名",
            sub_items: [{
                enable: true,
                type: "text",
                popup: ["{r{4-10}}个字符"],
                id: "uname",
                name: "uname",
                value: "",
                functions: {},
                check: {
                    type: "text",
                    required: 1,
                    check: 'name',
                    ass_check: function(eve) {
                        var name = $("#uname").val();
                        if (name.length < 3 || name.length > 10) {
                            return "请输入4-10个字符！";
                        }
                    }
                }
            }]
        },{
            title: "更改密码",
            style:"display:none",
            sub_items: [{
                enable: true,
                type: "button",
                popup: ["展开更改密码，收起不更改"],
                id: "change_pwd",
                name: "change_pwd",
                value: "展开",
                functions: {

                }
            }]
        }, {
            title: "密码",
            sub_items: [{
                enable: true,
                type: "password",
                popup: ["至少{r{6}}个字符","编辑时请{r{重新输入密码}}"],
                id: "pwd",
                name: "pwd",
                value: "",
                functions: {

                },
                check: {
                    type: "text",
                    required: 1,
                    check: 'other',
                    other_reg: '!/^\$/',
                    ass_check: function(eve) {
                        var pwd = $("#pwd").val();
                        if (pwd.length < 6) {
                            return "密码至少为6个字符！";
                        }
                    }
                }
            },{
                enable: true,
                type:"button",
                id:"modify_passwd_button",
                name:"modify_passwd_button",
                value:"更改密码",
                style: "width:40px;height:20px;border-radius:4px;display:none;",
                functions: {
                    onclick: "modify_passwd();"
                }
            },{
                enable: false,
                type: "password",
                popup: ["至少{r{6}}个字符","编辑时请{r{重新输入密码}}"],
                id: "pwd_mod",
                name: "pwd_mod",
                value: "",
                functions: {

                },
                check: {
                    type: "text",
                    required: 1,
                    check: 'other',
                    other_reg: '!/^\$/',
                    ass_check: function(eve) {
                        var pwd_mod = $("#pwd_mod").val();
                        if (pwd_mod.length < 6) {
                            return "密码至少为6个字符！";
                        }
                    }
                }
            }]
        }, {
            title: "确认密码",
            sub_items: [{
                enable: true,
                type: "password",
                popup: ["和密码{r{一致}}"],
                id: "pwd_again",
                name: "pwd_again",
                value: "",
                functions: {},
                check: {
                    type: "text",
                    required: 1,
                    check: 'other',
                    other_reg: '!/^\$/',
                    ass_check: function(eve) {
                        var pwd = $("#pwd").val();
                        var pwd_again = $("#pwd_again").val();
                        if (pwd != pwd_again) {
                            return "确认密码与密码不一致！";
                        }
                    }
                }
            }]
        }, {
            title: "用户老化时间",
            sub_items: [{
                enable: true,
                type: "text",
                id: "outtime",
                name: "outtime",
                popup: ["{r{30-60}}之间","单位：{g{分钟}}"],
                value: "",
                functions: {},
                check: {
                    type: "text",
                    required: 0,
                    check: 'num|',
                    ass_check: function(check) {
                        var val = $("#outtime").val();
                        if (val < 30 || val > 60) {
                            return "用户老化时间应在30-60之间";
                        }
                    }
                }
            }]
        }, {
            title: "IP/MAC绑定",
            sub_items: [{
                enable: true,
                type: "items_group",
                style: "height:30px;line-height:20px;margin:-2px;",
                sub_items: [{
                    enable: true,
                    id: "no-bind",
                    name: "bind_info",
                    label: "不绑定",
                    type: "radio",
                    checked: true,
                    value: "no_bind",
                    style: "vertical-align: middle;margin-top: -7px;",
                    functions: {
                        onclick: "radio_disabled (this);"
                    },
                }, {
                    enable: true,
                    id: "ip",
                    name: "bind_info",
                    label: "绑定IP",
                    type: "radio",
                    // checked:true,
                    value: "ip",
                    style: "vertical-align: middle;margin-top: -7px;",
                    functions: {
                        onclick: "radio_disabled (this);"
                    },
                }, {
                    enable: true,
                    id: "mac",
                    name: "bind_info",
                    label: "绑定MAC",
                    type: "radio",
                    // checked:true,
                    value: "mac",
                    style: "vertical-align: middle;margin-top: -7px;",
                    functions: {
                        onclick: "radio_disabled (this);"
                    },
                }, {
                    enable: true,
                    id: "ip-mac",
                    name: "bind_info",
                    label: "绑定IP和MAC",
                    type: "radio",
                    // checked:true,
                    value: "ipmac",
                    style: "vertical-align: middle;margin-top: -7px;",
                    functions: {
                        onclick: "radio_disabled (this);"
                    },
                }, ]
            }, {
                enable: true,
                type: "items_group",
                sub_items: [{
                    enable: true,
                    type: "textarea",
                    id: "binding-info-no",
                    name: "binding_info",
                    class: "binding_info",
                    popup: ["不绑定"],
                    value: "",
                    style: "width:280px;height:125px;",
                    disabled: "disabled",
                    functions: {},
                    check: {
                        type: "textarea",
                        required: 0,
                        check: 'note|',
                        ass_check: function(check) {

                        }
                    }
                }, {
                    enable: true,
                    type: "textarea",
                    id: "binding-info-ip",
                    name: "binding_info_ip",
                    class: "binding_info",
                    popup: ["绑定IP地址","{r{每行}}可以输入{r{一个IP地址}}"],
                    value: "",
                    style: "width:280px;height:125px;",
                    disabled: "disabled",
                    functions: {},
                    check: {
                        type: "textarea",
                        required: 1,
                        check: 'ip|',
                        ass_check: function() {

                        }
                    }
                }, {
                    enable: true,
                    type: "textarea",
                    id: "binding-info-mac",
                    name: "binding_info_mac",
                    class: "binding_info",
                    popup: ["绑定MAC地址","{r{每行}}可以输入{r{一个MAC地址}}"],
                    value: "",
                    style: "width:280px;height:125px;",
                    disabled: "disabled",
                    functions: {},
                    check: {
                        type: "textarea",
                        required: 1,
                        check: 'mac|',
                        ass_check: function() {

                        }
                    }
                }, {
                    enable: true,
                    type: "textarea",
                    id: "binding-info-ipmac",
                    name: "binding_info_ipmac",
                    class: "binding_info",
                    tip:"绑定IP/MAC地址",
                    popup: ["绑定IP/MAC地址","{r{每行}}可以输入{r{一个IP/MAC地址}}"],
                    value: "",
                    style: "width:280px;height:125px;",
                    disabled: "disabled",
                    functions: {},
                    check: {
                        type: "textarea",
                        required: 1,
                        check: 'other',
                        other_reg: '/^([1-9]|[1-9]\\d|1\\d{2}|2[0-1]\\d|22[0-3])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3}\\/([\\dA-Fa-f]{2}):([\\dA-Fa-f]{2}):([\\dA-Fa-f]{2}):([\\dA-Fa-f]{2}):([\\dA-Fa-f]{2}):([\\dA-Fa-f]{2})$/',
                        ass_check: function() {}
                    }
                }]
            }]
        }


    ]
};


/** 格式化输入字符串**/
//用法: "hello{0}".format('world')；返回'hello world'
String.prototype.format= function(){
	var args = arguments;
	return this.replace(/\{(\d+)\}/g,function(s,i){
        	return args[i];
	});
}
var userstate_css = {'online':'user-online', 'offline':'user-offline', 'forbid':'user-forbid'};
var userstate_text = {'online':'在线', 'offline':'离线', 'forbid':'被强制下线中'};

var list_panel_render = {
    'userstate': {
        render: function(default_rendered_text, data_item) {
            var key = "";
            if (default_rendered_text == "online") {
                key = "online";
            } else if (default_rendered_text == "offline") {
                key = "offline";
            } else {
                key = "forbid";
            }
	    return '<span class="{0}" title="{1}"></span>'.format(userstate_css[key], userstate_text[key])
        },
    },
    'bind_detail':{
        render: function(default_rendered_text, data_item) {
            default_rendered_text=default_rendered_text==''? '不绑定':default_rendered_text;
            return default_rendered_text; 
        }
    },
    'action': {
        render: function(default_rendered_text, data_item) {
            var action_buttons = [];
            if (data_item.userstate == "forbidden") {
                action_buttons = [{
                    "enable": true,
                    "id": "enable_item",
                    "name": "enable_item",
                    "button_icon": "user-recover.png",
                    "button_text": "恢复可登陆状态",
                    "value": data_item.id + "&" + data_item.userstate,
                    "functions": {
                        onclick: "enable_forbidded_item(this);"
                    },
                    "class": "action-image",
                }, {
                    "enable": true,
                    "id": "edit_item",
                    "name": "edit_item",
                    "button_icon": "edit.png",
                    "button_text": "编辑",
                    "value": data_item.id,
                    "functions": {
                        onclick: "edit_items('"+data_item.id+"','"+data_item.bind_detail+"','"+data_item.strategy+"','"+data_item.user_group+"');"
                    },
                    "class": "action-image",
                }, {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "value": data_item.id,
                    "functions": {
                        onclick: "delete_selected_items(this);"
                    },
                    "class": "action-image",
                }];
            } else {
                action_buttons = [{
                    "enable": true,
                    "id": "edit_item",
                    "name": "edit_item",
                    "button_icon": "edit.png",
                    "button_text": "编辑",
                    "value": data_item.id,
                    "functions": {
                        onclick: "edit_items('"+data_item.id+"','"+data_item.bind_detail+"','"+data_item.strategy+"','"+data_item.user_group+"');"
                    },
                    "class": "action-image",
                }, {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "value": data_item.id,
                    "functions": {
                        onclick: "delete_selected_items(this);"
                    },
                    "class": "action-image",
                }];
            }
            return PagingHolder.create_action_buttons(action_buttons);
        }
    }

};


var list_panel_config = {
    url: ass_url,
    /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_user_list",
    /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,
    /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",
    /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,
    /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,
    /* ===可选===，渲染每列数据 */
    panel_header: [ /* ***必填***，控制数据的加载以及表头显示 */ {
        "enable": true, //用户控制表头是否显示
        "type": "checkbox", //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "", //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox", //用户装载数据之用
        "class": "", //元素的class
        //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
        "width": "5%", //所有表头加起来应该等于100%,以精确控制你想要的宽度
        "functions": { //一般只有checkbox才会有这个字段
        },
        "td_class": "align-center"
    }, {
        "enable": false,
        "type": "text",
        "title": "用户策略",
        "name": "strategy",
        "width": "6%",
        "td_class": "align-center"
    }, {
        "enable": false,
        "type": "text",
        "title": "名称",
        "name": "description",
        "width": "15%"
    }, {
        "enable": false,
        "type": "radio",
        "name": "radio",
        "td_class": "rule-listbc",
        "width": "5%",
        "td_class": "align-center"
    }, {
        "enable": true,
        "type": "text",
        "title": "用户名", //一般text类型需要title,不然列表没有标题
        "name": "uname",
        "width": "15%"
    }, {
        "enable": true,
        "type": "text",
        "title": "老化时间",
        "name": "outtime",
        "width": "8%",
        "td_class": "align-center"
    }, {
        "enable": true,
        "type": "text",
        "title": "绑定信息",
        "name": "bind_detail",
        "width": "25%"
    }, {
        "enable": false,
        "type": "text",
        "title": "",
        "name": "ip_name1",
        "width": "0%"
    }, {
        "enable": false,
        "type": "text",
        "title": "绑定IP2",
        "name": "ip_name2",
        "width": "0%"
    }, {
        "enable": false,
        "type": "text",
        "title": "绑定IP3",
        "name": "ip_name3",
        "width": "0%"
    }, {
        "enable": false,
        "type": "text",
        "title": "IP/掩码",
        "name": "ip_mask",
        "width": "0%"
    }, {
        "enable": false,
        "type": "text",
        "title": "IP范围",
        "name": "ip_range",
        "width": "0%"
    }, {
        "enable": true,
        "type": "text",
        "title": "状态",
        "name": "userstate",
        "width": "8%",
        "td_class": "align-center"
    }, {
        "enable": true,
        "type": "action",
        "title": "操作",
        "name": "action",
        "width": "10%",
        "td_class": "align-center"
    }],
    top_widgets: [ /* ===可选=== */ {
        "enable": true,
        "type": "image_button",
        "button_icon": "add16x16.png",
        "button_text": "新建",
        "functions": {
            onclick: "add_rule(this);"
        }
    }, {
        "enable": true,
        "type": "image_button",
        "id": "delete_selected",
        "name": "delete_selected",
        "class": "",
        "button_icon": "delete.png",
        "button_text": "删除选中",
        "functions": {
            onclick: "delete_selected_items(this)"
        }
    }, {
        "enable": false,
        "type": "image_button",
        "id": "show_all_data",
        "name": "show_all_data",
        "class": "",
        "button_icon": "detail.png",
        "button_text": "显示所有用户",
        "functions": {
            onclick: "show_all_data()"
        }
    }, {
        "enable": true,
        "type": "image_button",
        "id": "move_user_group",
        "name": "move_user_group",
        "class": "",
        "button_icon": "stock_up-16.png",
        "button_text": "移动至分组",
        "functions": {
            onclick: "move_user_group('move')"
        }
    }, {
        "enable": true,
        "type": "image_button",
        "id": "import_user",
        "name": "import_user",
        "class": "",
        "button_icon": "download.png",
        "button_text": "导入用户",
        "functions": {
            onclick: "import_panel.show()"
        }
    }, {
        "enable": true,
        "type": "image_button",
        "id": "export_user",
        "name": "export_user",
        "class": "",
        "button_icon": "upload.png",
        "button_text": "导出用户",
        "functions": {
            onclick: "export_user()"
        }
    }],
    is_default_search: true,
    /* ===可选===，默认是true，控制默认的搜索条件 */

}
var import_panel_config = {
    url: ass_url,
    /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "import_panel",
    /* ***必填***，确定面板挂载在哪里 */
    panel_name: "import_panel",
    /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "导入用户",
    rule_title_adding_prefix: "",
    rule_title_adding_icon: "download.png",
    is_panel_closable: true,
    /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,
    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,
    /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: { /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",
        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 15 /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons: {
        add: false,

        sub_items: [{
            enable: true,
            type: "hidden",
            name: "ACTION",
            value: "import",

        },{
            enable: true,
            type: "submit",
            style: "",
            value: "导入",
            id: "update",
            functions: {
                onclick: "import_user();"
            },

        }],
        cancel: true,
    },
    event_handler: { /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function(add_obj, data_item) {

            /*
             * ===可选事件函数===，在数据项往添加面板加载时，数据还“未”装载入面板时调用，
             *    一般是点击编辑后数据项才会向添加面板加载
             *
             * 参数：-- add_obj   ==可选==，添加面板实例
             *        -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
        },
        after_load_data: function(add_obj, data_item) {
            /*
             * ===可选事件函数===，在数据项往添加面板加载后，数据“已”装载入面板时调用
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *         -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
        },
        before_cancel_edit: function(add_obj) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
             *    在做这些默认的操作之“前”调用此函数
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *
             * 返回：无
             */
        },
        after_cancel_edit: function(add_obj) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
             *    在做这些默认的操作之“后”调用此函数
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *
             * 返回：无
             */
        },
        before_save_data: function(add_obj, sending_data) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的添加按钮时，系统向服务器提交添加面板的所有数据，
             *    在做提交数据之“前”会调用此函数
             *
             * 参数： -- add_obj       ==可选==，添加面板实例
             *        -- sending_data  ==可选==, 要向服务器提交的数据，
             *           用户可以通过 sending_data.xxx = xxx 添加向服务器提交的数据
             * 返回：true/false
             *       -- 返回true，或者不返回数据，数据会如实提交
             *       -- 返回false，会阻止数据向服务器其提交
             */
        },
        after_save_data: function(add_obj, received_data) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的添加按钮时，系统向服务器提交添加面板的所有数据，
             *    在做提交数据之“后”并且服务器响应之“后”会调用此函数
             *
             * 参数： -- add_obj       ==可选==，添加面板实例，可以调用add_obj.show_error_mesg( mesg )
             *           或者add_obj.show_note_mesg( mesg )等函数反馈信息给用户
             *        -- received_data ==可选==, 服务器响应的数据，
             *           可以在后台配置要传递的数据，并在此处访问
             * 返回：无
             */
        }
    },
    items_list: [{
        title: "选择升级文件(.xls)*",
        sub_items: [{
                enable: true,
                type: "file",
                value: "选择",
                id: "file_lib",
                name: "file_lib",
                functions: {
                    onclick: ""
                },
                style: "width:300px;height:25px;border-radius:4px"
            }]
        },{
            title:"默认分组",
            sub_items:[{
                            enable:true,
                            id:"default_group",
                            name:"default_group",
                            type:"text",
                            // disabled: "disabled",
                            readonly:"readonly",
                            style:"height:16px;width:117px"

               
                        },
                        {
                            enable:true,
                            id:"default_group_btn",
                            name:"default_group_btn",
                            type:"button",
                            // disabled: "disabled",
                            class: "set-button",
                            value:"配置",
                            functions:{
                                onclick:"move_user_group('import');"
                            },
                            style:"width:40px;height:20px;border-radius:4px"
                        },{
                            enable:true,
                            id:"default_group_id",
                            name:"default_group_id",
                            type:"text",
                            style:"display:none"               
                        }]
        },{
            title:"对本地存在的用户",
            sub_items: [{
                enable: true,
                type: "select",
                id: "continue_or_skip",
                name: "continue_or_skip",
                value: "",
                style: "width:226px;   vertical-align: text-top;",
                functions: {
                    onchange: "select_items(this.value,this.id);"
                },
                options: [{
                        text: "继续导入，覆盖已存在的用户",
                        id: "continue_import",
                        value: "continue_import",
                        functions: {}
                    }, {
                        text: "跳过，不导入该用户",
                        id: "skip_import",
                        value: "skip_import",
                        functions: {}
                    }

                ]
            }]
        }]
};

function export_user(argument) {
    var sending_data = {
        ACTION: 'export'
    }

    function ondatareceived(data) {

    }
    do_request(export_user, ondatareceived);
}

function import_user(argument) {
    var file_lib=$('#file_lib').val();
    var bin_reg = /.xls$/;
    if (file_lib=='') {
        show_popup_alert_mesg('请选择文件');
    } else if(bin_reg.test(file_lib)==false){
        show_popup_alert_mesg('文件格式错误');
    }else{
        // update_detail();
        import_panel.hide();
        show_waiting_mesg("上传中...");
        $("#add_panel_body_form_id_for_import_panel").get(0).submit();


        // offline_update();
        
    }
}
//当textarea上方四个radio按钮切换时控制textarea是否可操作
function radio_disabled(e) {

    $('textarea').attr('disabled', 'disabled');
    if ($(e).val() == $('#no-bind').val()) {
        $('#binding-info-no').attr('disabled', 'disabled').parent().css('display', 'inline-block').siblings().css('display', 'none');

    } else if ($(e).val() == $('#ip').val()) {
        $('#binding-info-ip').removeAttr('disabled').parent().css('display', 'inline-block').siblings().css('display', 'none');

    } else if ($(e).val() == $('#mac').val()) {
        $('#binding-info-mac').removeAttr('disabled').parent().css('display', 'inline-block').siblings().css('display', 'none');

    } else if ($(e).val() == $('#ip-mac').val()) {
        $('#binding-info-ipmac').removeAttr('disabled').parent().css('display', 'inline-block').siblings().css('display', 'none');

    }

}

//发送额外的sending_data
function sending_data_extend(recent_group) {
    var user_group;
    if (recent_group) {
        user_group = recent_group;
    } else {
        user_group = list_panel_config.user_group_data;
    }
    list_panel.extend_sending_data = {
        group_addr: user_group
    }; //load_data时send_data发送当前树选中的项，后台返回当前选中的项的用户；

    add_panel_config.footer_buttons.sub_items[0].value = user_group;
    //打开add_panel时给form表单传递树当前选中的项，后台在保存数据时，知道数据存在哪一个组下
}
//编辑信息时，根据数据加载相对应的add_panel面板
function edit_items(id,info,radio,group) {
    $("#modify_passwd_button").css('display','block');
    $("input[name='group_addr']").val(group);
    //需要发送额外的sending_data
    sending_data_extend(group);
    //根据list_panel中绑定信息判定绑定信息中radio、textarea的状态
    var arr = info.split('=');
    if (arr[1]) {
        arr[1] = arr[1].replace(/ \| /g, '\n');
    } else {
        arr[1] = '';
    }

    list_panel.edit_item(id);


    $('textarea').attr('disabled', 'disabled');
    if (arr[0] == '') {
        $("#no-bind")[0].checked = true;
        $('#binding-info-no').attr('disabled', 'disabled').parent().css('display', 'inline-block').siblings().css('display', 'none');
    } else if (arr[0] == 'IP') {
        $("#ip")[0].checked = true;
        $('#binding-info-ip').removeAttr('disabled').val(arr[1]).parent().css('display', 'inline-block').siblings().css('display', 'none');
    } else if (arr[0] == 'MAC') {
        $("#mac")[0].checked = true;
        $('#binding-info-mac').removeAttr('disabled').val(arr[1]).parent().css('display', 'inline-block').siblings().css('display', 'none');
    } else if (arr[0] == 'IP/MAC') {
        $("#ip-mac")[0].checked = true;
        $('#binding-info-ipmac').removeAttr('disabled').val(arr[1]).parent().css('display', 'inline-block').siblings().css('display', 'none');
    }

    // 根据list_panel显示radio选中项
    // if (radio == '无') {
    //     radio=0;
    //     $('')
    //     $("#strategy_no")[0].checked = true;
    // } else {
    //     radio=1;
    //     $("#strategy_has")[0].checked = true;
    // }
    // 调用切换有无用户策略的radio按钮的函数
    // judgeStrategy(radio);
}


//在用户添加用户时，根据不同类别判断是否填写项目
function hintFill() {

    $('.userTipRight').css('display', 'none');
    var radio = $("input[name='bind_info']:checked").val();
    var strategyRadio = $("input[name='strategy']:checked").val();

    var bindIp = $("#binding-info-ip").val();
    var bindMac = $("#binding-info-mac").val();
    var bindIpmac = $("#binding-info-ipmac").val();

    var uname = $("#uname").val();
    var pwd = $("#pwd").val();
    var pwd_again = $("#pwd_again").val();

    if (strategyRadio == '1') {
        if (uname == '' || pwd == '' || pwd_again == '') {
            list_panel.show_error_mesg("如果有用户策略，需填写账户及密码");
            return false;
        }
    }

    if (radio == 'ip' && bindIp == '') {
        list_panel.show_error_mesg("请填写IP地址");
        return false;
    } else if (radio == 'mac' && bindMac == '') {
        list_panel.show_error_mesg("请填写MAC地址");
        return false;
    } else if (radio == 'ipmac' && bindIpmac == '') {
        list_panel.show_error_mesg("请填写IP/MAC地址");
        return false;
    }

}
//当有无用户策略切换时，决定用户名、密码的是否可填写
function judgeStrategy(radioVal) {
    var disabledArr = [$("#uname"), $("#pwd"), $("#pwd_again")];

    if (radioVal == '0') {

        $("#ip")[0].checked = true;
        $("#no-bind").parent().css('display', 'none');
        $('#binding-info-ip').removeAttr('disabled').parent().css('display', 'inline-block').siblings().css('display', 'none');

        for (var i = 0; i < disabledArr.length; i++) {
            disabledArr[i].attr('disabled', 'disabled');
            disabledArr[i].val('');
        }

    } else {
        $("#no-bind")[0].checked = true;
        $("#no-bind").parent().css('display', 'inline-block');
        $('#binding-info-no').attr('disabled', 'disabled').parent().css('display', 'inline-block').siblings().css('display', 'none');


        for (var i = 0; i < disabledArr.length; i++) {
            disabledArr[i].removeAttr('disabled');
            // disabledArr[i].val(disabledDetailArr[i]);

        }
    }
}
//渲染额外add_panel的面板样式
function renderStyle() {

    $(".binding_info").next().css({
        display: 'inline-block',
        width: '156px'
    });
    $(".binding_info").parent().css({
        position: 'absolute',
        left: '10px',
        top: '40px'
    }).parent().parent().parent().css('position', 'relative').parent().css('height', '190px');

    $("input[name='bind_info']").parent().parent().css({
        position: 'absolute',
        top: '5px'
    });

    $(".binding_info").parent('div:gt(0)').css('display', 'none');

    $("#add_panel_body_form_name_for_add_panelbinding_info_macCHINARK_ERROR_TIP").css({
        position: 'absolute',
        top: '0px',
        left: '290px'
    });
}

//删除用户
function delete_selected_items(e) {
    var checked_items = list_panel.get_checked_items();
    if (e.id == "delete_item") {
        delete_user();
    } else {
        if (checked_items == '') {
            alert('请在复选框中先选择您要删除的用户！');
        } else {
            delete_user();
        }
    }

    function delete_user() {
        var ids = "";
        if (e.id == "delete_selected") {

            var checked_items_id = new Array();
            for (var i = 0; i < checked_items.length; i++) {
                checked_items_id.push(checked_items[i].id);
            }
            ids = checked_items_id.join("&");
        } else {
            ids = e.value;
        }
        //需要发送额外的sending_data
        var recent_group;
        if (typeof(list_panel_config.select_node) == 'undefined' || list_panel_config.select_node == 1) {
            recent_group = "j1_18";
        } else if (list_panel_config.select_node == 3) {
            recent_group = list_panel_config.user_group_data_parent;
        }
        sending_data_extend(recent_group);
        list_panel.delete_item(ids);
        $("#rule_listb_for_list_panel").find('tr').each(function() {
            $(this).removeClass('tr_green');
        });

        //更新树中用户数
        show_user_num();
        save_user_data();
        update_tree();
    }

}

//增加用户
function add_rule(element) {
    var recent_group;
    if (typeof(list_panel_config.select_node) == 'undefined' || list_panel_config.select_node == 1) {
        recent_group = "j1_18";
    } else if (list_panel_config.select_node == 3) {
        recent_group = list_panel_config.user_group_data_parent;
    }
    // for(var key in user_tree_detail){
    //     if (list_panel_config.user_group_data == key) {

    //     }else{
    //         recent_group = "j1_18";
    //         break;
    //     }
    // }

    //需发送额外的sending_data
    sending_data_extend(recent_group);
    //渲染面板
    add_panel.render();
    //渲染额外样式
    renderStyle();
    //清空面板中内容
    add_panel_extend();
    add_panel.show();
}
//清空面板中内容，显示正确的面板项目
function add_panel_extend() {
    $("#uname").attr("value", "");
    $("#pwd").attr("value", "");
    $('textarea').attr('disabled', 'disabled');
    $('#no-bind')[0].checked = true;
    $('#binding-info-no').attr('disabled', 'disabled').parent().css('display', 'inline-block').siblings().css('display', 'none');

}

//启用被禁用的用户
function enable_forbidded_item(e) {
    var data = e.value.split("&");
    var id = data[0];
    var userstate = data[1];
    var sending_data = {
        ACTION: 'enable_forbidded_item',
        id: id,
        userstate: userstate
    };

    function ondatareceived(data) {
        list_panel.update_info(true);
    }
    do_request(sending_data, ondatareceived);
}
//当用户组管理树的选中项发生变化时，更新list_panel中数据
function show_user_data(data) {
    //jstree中change事件，当选中项发生变化时调用
    $('#cat_tree')
        .on('changed.jstree', function(e, data) {

            if (data.action == "select_node") {
                list_panel_config.user_group_data = data.node.id;
                list_panel_config.user_group_data_parent = data.node.parent;
                list_panel_config.select_node = data.node.parents.length;
                $("#rule_listb_for_list_panel").find('tr').each(function() {
                    $(this).removeClass('tr_green');
                });
                //当选中项改变时，检查是否选中的几级树，如果是多层树，在删除组时，需要知道子目录的id，一起删除，否则会产生漏删的情况
                //需要传入两个参数，前者为当前选中项id，后者为选中项子级目录的id[数组]
                // judge_ul(list_panel_config.user_group_data,data.node.children) ;
                //更新用户数
                if (list_panel_config.user_group_data == "j1_1") {
                    if (typeof(list_panel_config.all_detail_data) != 'undefined') {
                        list_panel.detail_data = list_panel_config.all_detail_data.detail_data;
                        list_panel.total_num = list_panel_config.all_detail_data.total_num;
                        list_panel.update_info();
                    }

                } else {

                    if (typeof(list_panel_config.user_detail) != 'undefined') {
                        for (var key in list_panel_config.user_detail) {
                            if (key == list_panel_config.user_group_data || key == $('#' + list_panel_config.user_group_data).parent().parent()[0].id) {
                                list_panel.detail_data = list_panel_config.user_detail[key];
                                list_panel.total_num = list_panel_config.user_detail[key].length;
                                list_panel.update_info();
                            }
                        }
                    }

                    if (list_panel_config.select_node == 3) {
                        $("#rule_listb_for_list_panel").find('tr').each(function() {
                            if ($(this).children('td').eq(1).text() != '') {
                                if ($(this).children('td').eq(1).text() == $("#" + list_panel_config.user_group_data)[0].textContent) {
                                    $(this).addClass('tr_green').siblings().removeClass('tr_green');
                                }
                            }
                        });
                    }
                }
            }
        }).on("open_node.jstree", function(e, data) {
            ///当树展开时，添加用户数的标签及更新用户数
            tree_append_num();
            show_user_num();

        })
        .on("select_node.jstree", function(e, data) { //点击事件
            //触发toggle_node 事件 就行了
            // $('#cat_tree').jstree("toggle_node", "#" + data.node.id /*.rslt.obj.attr("id")*/ );
            $('#cat_tree').children('ul').children('li').children('ul').children('li')
                .last().addClass('jstree-last').siblings().removeClass('jstree-last');
        })
    var to = false;
    $('#cat_tree_search').keyup(function() {
        if (to) {
            clearTimeout(to);
        }
        to = setTimeout(function() {
            var v = $('#cat_tree_search').val();
            $('#cat_tree').jstree(true).search(v);
        }, 250);
    });

}

//删除树及树中用户
function delete_user_data() {

    var sending_data = {
        ACTION: "delete_group_item",
        user_group_data: list_panel_config.user_group_data /*_children*/ //树选中项及子级目录的集合
    };

    function ondatareceived() {
        list_panel.detail_data = [];
        list_panel.total_num = 0;
        list_panel.update_info();
        save_user_data();
        update_tree();
        // list_panel.show_note_mesg('删除成功');
    }
    do_request(sending_data, ondatareceived);
}


//加载树结构
function get_data_tree() {

    var sending_data = {
        ACTION: "get_tree"
    };

    function ondatareceived(data) {
        if (data == -1) {
            data = {
                "id": "j1_1",
                "text": "/",
                "icon": true,
                "li_attr": {
                    "id": "j1_1"
                },
                "a_attr": {
                    "href": "#"
                },
                'state':{'opened':true},
                "data": "1",
                "children": [{
                    "id": "j1_18",
                    "text": "默认",
                    "icon": true,

                    "li_attr": {
                        "id": "j1_18"
                    },
                    "a_attr": {
                        "href": "#"
                    },
                    "data": null,
                    "children": []
                }]
            }
            var json = JSON.stringify(data);
            var sending_data = {
                ACTION: "update_tree",
                tree_json: json
            };

            function ondatareceived(data) {
                //添加用户数的标签
                tree_append_num();
                show_user_num();
                if (data.status == 'fail') {
                    alert('用户组更改失败');
                    get_data_tree();
                }
            }
            do_request(sending_data, ondatareceived);
        }

        data.state = {"opened":true};

        $("#cat_tree")
            /*.on('move_node.jstree', function(e,data){
                        console.log('a');
                        tree_append_num();
                        show_user_num();
                        update_tree();

                    })*/
            .jstree({
                core: {
                    check_callback: true,
                    data: data
                },
                plugins: ['contextmenu'/*, 'state'*/ /*,'dnd'*/ /*, "wholerow"*/ , 'search' /*,'cookies'*/ ],
                contextmenu: {
                    items: context_menu
                }
                // dnd:{ is_draggable: false }
            });


    }
    do_request(sending_data, ondatareceived);

}

//操作树的对象
function context_menu(node) {
    var tree = $('#cat_tree').jstree(true);

    var items = {
        "Create": {
            "separator_before": false,
            "separator_after": false,
            "label": "新建组",
            "action": function(obj) {

                var $node = tree.create_node(node);
                tree.edit($node);

            }
        },
        "Rename": {
            "separator_before": false,
            "separator_after": false,
            "label": "重命名",
            "action": function(obj) {

                tree.edit(node);

            }
        },
        "MoveUp": {
            "separator_before": true,
            "separator_after": false,
            "label": "上移菜单",
            "action": function(data) {
                // if ($('#'+node.id).hasClass('jstree-last')) {
                //     $('#'+node.id).removeClass('jstree-last')
                //     .prev().addClass('jstree-last');
                // }
                var b = $('#' + node.id).prev().attr('id');
                $('#' + node.id).insertBefore('#' + b);
                update_tree(node.id, b, 'up');
                $('#cat_tree').children('ul').children('li').children('ul').children('li')
                    .last().addClass('jstree-last').siblings().removeClass('jstree-last');
            }
        },
        "MoveDown": {
            "separator_before": false,
            "separator_after": false,
            "label": "下移菜单",
            "action": function(data) {
                // if ($('#'+node.id).next().hasClass('jstree-last')  ) {
                //    $('#'+node.id).addClass('jstree-last')
                //     .prev().removeClass('jstree-last'); 
                // }
                var b = $('#' + node.id).next().attr('id');
                $('#' + node.id).insertAfter('#' + b);
                update_tree(node.id, b, 'down');
                $('#cat_tree').children('ul').children('li').children('ul').children('li')
                    .last().addClass('jstree-last').siblings().removeClass('jstree-last');
            }
        },
        "Remove": {
            "separator_before": true,
            "separator_after": false,
            "label": "移除",
            "action": function(obj) {
                if (confirm('删除组将删除组中所有数据，确认删除？')) {
                    // if (node.data == '1') {
                    //     alert('此目录不能删除！');
                    // }else{

                    tree.delete_node(node);
                    //更新后台配置文件中树的结构
                    // update_tree();

                    delete_user_data();
                    // }

                }
            }
        }
    };
    //当右键弹出选项点击后调用
    $('ul.vakata-context').on('click', function() {
        event.preventDefault();
        //更新后台树结构的数据
        edit_tree();
    });

    var node_par_len = node.parents.length;
    // tree_node = node_par_len;
    // 

    if (node_par_len == 1) {
        items.Remove._disabled = true;
        items.MoveUp = null;
        items.MoveDown = null;
    } else if (node_par_len == 2) {

        items.Create = {
            "separator_before": false,
            "separator_after": false,
            "label": "新增用户",
            "action": function(obj) {

                add_rule();

            }
        };

    } else {
        items.Create = {
            "separator_before": true,
            "separator_after": false,
            "label": "编辑",
            "action": function(obj) {
                var aim_user = search_edit_user(node);

                edit_items(aim_user.id, aim_user.bind_detail, aim_user.strategy);

            }
        }
        items.Remove = {
                "separator_before": true,
                "separator_after": false,
                "label": "删除",
                "action": function(obj) {
                    var aim_user = search_edit_user(node);
                    var remove_user = {
                            value: aim_user.id,
                            id: "delete_item"
                        }
                    delete_selected_items(remove_user);
                }
            }
        items.Rename = null;
        items.MoveUp = null;
        items.MoveDown = null;
    }
    if (node.id == 'j1_18') {
        items.Remove._disabled = true;
        items.Rename._disabled = true;
    }
    return items;

}

function search_edit_user(node) {
    var all_user = list_panel_config.all_detail_data.detail_data;
    var aim_user;
    for (var i = 0; i < all_user.length; i++) {
        if (all_user[i].uname == node.text) {
            aim_user = all_user[i];
        }
    }
    return aim_user;
}
//由于重命名、增加项目和删除不同，他们要在input框blur事件后才调用更新后台树数据的函数
function edit_tree() {

    $("#cat_tree").find('input').on('blur', function() {
        event.preventDefault();
        update_tree();

    });

}
//更新后台配置文件中树的结构
function update_tree(node, move_node, derection) {

    var t_json = $('#cat_tree').jstree(true).get_json($("#j1_1"), {
        no_li_attr: true,
        no_a_attr: true,
        no_state: true
    });
    for (var i = 0; i < t_json.children.length; i++) {
        for (var j = 0; j < t_json.children[i].children.length; j++) {
            t_json.children[i].children[j].type = "user";
        }
    }
    if (node && move_node) {
        var sending_data = {
            ACTION: "up_down_tree",
            derection: derection,
            node: node
        };

        function ondatareceived(data) {
            if (data.status != '0') {
                message_manager.show_popup_error_mesg('移动失败！');
            }
        }
        do_request(sending_data, ondatareceived);
        return;
    }

    var json = JSON.stringify(t_json);
    console.log(t_json);
    var sending_data = {
        ACTION: "update_tree",
        tree_json: json
    };

    function ondatareceived(data) {
        //添加用户数的标签
        tree_append_num();
        show_user_num();
        if (data.status == 'fail') {
            alert('用户组更改失败');
            get_data_tree();
        }
    }
    do_request(sending_data, ondatareceived);
}
//显示所有用户
function show_all_data() {

    var sending_data = {
        ACTION: "load_data",
        current_page: $("#total_page_for_list_panel").text(),
        page_size: 20,
    };

    function ondatareceived(data) {
        list_panel.detail_data = data.detail_data;
        list_panel.total_num = data.total_num;
        list_panel.update_info();
    }
    do_request(sending_data, ondatareceived);
}
//移动用户所在组
function move_user_group(type) {
    var move_data = list_panel.get_checked_items();
    if (move_data == '' && type == 'move') {
        alert('请在复选框中先选择您要移动的用户！');
        return;
    } else {
        $("#list_panel_id_for_user_group_panel .container-main-body.container-main-body-s").css({
            height: "250px",
            background: "#e6eff8"
        }).empty().append('<div id="cat_tree_move" class="move_panel_style"></div>');
        //向移动用户面板中添加树结构
        get_data_tree_move();
        user_group_panel.show();

    }

}
//向移动用户面板中添加树结构
function get_data_tree_move() {

    var sending_data = {
        ACTION: "get_tree"
    };

    function ondatareceived(data) {
        for (var i = 0; i < data.children.length; i++) {
            data.children[i].children = null;
        }
        $("#cat_tree_move").jstree({
            core: {
                check_callback: true,
                data: data
            } 
        });

    }
    do_request(sending_data, ondatareceived);
}

//移动用户
function move_to() {
    var move_to_num = $("#cat_tree_move").jstree(true).get_selected();
    if (move_to_num[0] == 'j1_1') {
        alert('不能移动到根目录！');
        return;
    }
    if ($("#import_panel").css('display') != 'none') {
        $("#default_group").val($("#cat_tree_move #"+move_to_num[0]).text());
        $("#default_group_id").val(move_to_num[0]);
        user_group_panel.hide();
    }else{
        var move_data = list_panel.get_checked_items();
        var move_data_id_arr = new Array();
        for (var i = 0; i < move_data.length; i++) {
            move_data_id_arr.push(move_data[i].user_id);

        }
        move_data_id = move_data_id_arr.join(',');
        
        //传入要移动的用户、要移动到的组的id
        var sending_data = {
            ACTION: "move_to",
            move_data: move_data_id,
            move_to_num: move_to_num[0]

        };

        function ondatareceived() {
            user_group_panel.hide();
            //更新用户数
            show_user_num();
            //更新list_panel中用户
            var sending_data = {
                ACTION: "load_data",
                user_data_addr: list_panel_config.user_group_data,
                current_page: $("#total_page_for_list_panel").text(),
                page_size: 20,
            };

            function ondatareceived(data) {
                list_panel.detail_data = data.detail_data;
                list_panel.total_num = data.total_num;
                list_panel.update_info();
                save_user_data();
                update_tree();

            }
            do_request(sending_data, ondatareceived);
        }
        do_request(sending_data, ondatareceived);
    }
}
//动态创建元素
function tree_append_num() {
    var page_num = '<span><small>(</small><small>0</small><small>)</small></span>';

    $('#cat_tree').children('ul').children('li').children('ul').children('li').children('a').each(function() {
        if ($(this).next('span').length == '0') {
            $(this).after(page_num);
        }
    });
    $('#cat_tree').children('ul').children('li').children('a').each(function() {
        if ($(this).next('span').length == '0') {
            $(this).after(page_num);
        }
    });
}
//更新用户数
function show_user_num() {
    var all_id = $('#cat_tree').children('ul').children('li').children('ul').children('li');
    var all_id_arr = [];
    all_id.each(function() {
        all_id_arr.push($(this)[0].id);
    });
    var all_id_str = all_id_arr.join(',');
    if (typeof(list_panel_config.all_detail_data) != 'undefined') {
        for (var i = 0; i < all_id_arr.length; i++) {
            $('#cat_tree' + " #" + all_id_arr[i]).find('span').each(function() {
                for (var key in list_panel_config.user_detail) { //遍历后台传过来的json，对象
                    if (key == $(this).parent().attr('id')) {
                        $(this).children().eq(1).html(list_panel_config.user_detail[key].length);
                    }
                }
            });
        }
        var num = $('#j1_1').find('small').eq(1);
        num.text(Number(list_panel_config.all_detail_data.total_num));
    }

}

function save_user_data() {
    var sending_data = {
        ACTION: "load_data",
        // user_data_addr:list_panel_config.user_group_data,
        current_page: $("#total_page_for_list_panel").text(),
        page_size: 20,
        panel_name: 'list_panel',
        // paging_action:'none',
        search: $("#search_key_for_list_panel").val()
    };

    function ondatareceived(data) {
        var all_id = $('#cat_tree').children('ul').children('li').children('ul').children('li');
        var all_id_arr = [];
        all_id.each(function() {
            all_id_arr.push($(this)[0].id);
        });
        var detail = {};
        var tree_detail = {};
        for (var i = 0; i < all_id_arr.length; i++) {
            detail[all_id_arr[i]] = [];
            tree_detail[all_id_arr[i]] = [];

        }

        for (var i = 0; i < data.detail_data.length; i++) {
            for (var key in detail) {
                if (key == data.detail_data[i].user_group) {
                    detail[key].push(data.detail_data[i]);
                    tree_detail[key].push({
                        text: data.detail_data[i].uname,
                        icon: '../images/login_user.png',
                        children: [],
                        li_attr: {},
                        a_attr: {}
                    });
                }
            }
        }

        list_panel_config.user_detail = detail;
        // user_tree_detail = tree_detail;
        list_panel_config.all_detail_data = data;

        for (var key in tree_detail) {
            $('#' + key).children().remove();
            $('#cat_tree').jstree(true)._append_json_data($('#' + key), tree_detail[key]);
        }
        tree_append_num();
        for (var i = 0; i < all_id_arr.length; i++) {
            $('#cat_tree' + " #" + all_id_arr[i]).find('span').each(function() {
                for (var key in detail) { //遍历后台传过来的json，对象
                    if (key == $(this).parent().attr('id')) {
                        $(this).children().eq(1).html(detail[key].length);
                    }
                }

            });
        }
        var num = $('#j1_1').find('small').eq(1);
        num.text(Number(data.total_num));

    }
    do_request(sending_data, ondatareceived);
}

function show_list_user() {
    $("#cat_tree").find('a').each(function() {
        if ($(this).hasClass('jstree-clicked')) {
            var recent_group = $(this).parent().attr('id');
            if (recent_group == 'j1_1') {
                list_panel.detail_data = list_panel_config.all_detail_data.detail_data;
                list_panel.total_num = list_panel_config.all_detail_data.total_num;
                list_panel.update_info();
                return;
            }
            for (var key in list_panel_config.user_detail) {
                if (key == recent_group) {
                    list_panel.detail_data = list_panel_config.user_detail[key];
                    list_panel.total_num = list_panel_config.user_detail[key].length;
                    list_panel.update_info();
                }
            }
        }
    });
}
//为编辑面板的两个密码编辑框绑定事件,使用户不可以在原有密码上修改
function forEditPassword() {
    $("#pwd").val("");
    $("#pwd_again").val("");
    $("#pwd_again").unbind("keydown", forEditPasswordAgain);
}

function forEditPasswordAgain() {
    $("#pwd").val("");
    $("#pwd_again").val("");
    $().bind("keydown")
}

function bindPass() {
    $("#pwd").one("keydown", forEditPassword);
    $("#pwd_again").one("keydown", forEditPasswordAgain);
}

function elimPass() {
    $("#pwd").unbind("keydown", forEditPassword);
    $("#pwd_again").unbind("keydown", forEditPasswordAgain);
}
//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: ass_url,
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request) {
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

//创建action_button
function create_action_buttons(action_buttons) {
    var buttons = "";

    if (action_buttons === undefined) {
        return buttons; /*如果没有定义相应的对象，直接返回*/
    }

    for (var i = 0; i < action_buttons.length; i++) {
        var item = action_buttons[i];
        if (item.enable === undefined || !item.enable) {
            continue;
        }
        buttons += '<input type="image" ';
        if (item.id !== undefined && item.id) {
            buttons += 'id="' + item.id + '" ';
        }
        if (item.value !== undefined && item.value) {
            buttons += 'value="' + item.value + '" ';
        }
        if (item.name !== undefined && item.name) {
            buttons += 'name="' + item.name + '" ';
        }
        if (item.class !== undefined && item.class) {
            buttons += 'class="action-image ' + item.class + '" ';
        } else {
            buttons += 'class="action-image" ';
        }
        if (item.button_text !== undefined && item.button_text) {
            buttons += 'title="' + item.button_text + '" ';
        }
        if (item.button_icon !== undefined && item.button_icon) {
            buttons += 'src="../images/' + item.button_icon + '" ';
        }
        if (item.functions !== undefined && item.functions) {
            var functions = item.functions;
            for (var key in functions) {
                buttons += key + '="' + functions[key] + '" ';
            }
        }
        buttons += '/>';
    }

    return buttons;
}
function import_panel_extendrender(argument) {
    $("#add_panel_header_id_for_import_panel").append('<form enctype="multipart/form-data" method="post" action="/cgi-bin/auth_user_manager.cgi"></form>');
    $('#add_panel_header_id_for_import_panel form[enctype="multipart/form-data"]').append('<input type="submit" value="下载模板"><input type="hidden" name="ACTION" value="download">');

    $("#export_user").append('<input type="hidden" name="ACTION" value="export" style="width:0;height:0;">')
    .wrap('<form enctype="multipart/form-data" method="post" action="/cgi-bin/auth_user_manager.cgi" style="display:inline-block"></form>');
}


function init() {
    /*初始化消息框,以使图片加载*/
    show_waiting_mesg("准备中...");
    hide_waiting_mesg();
}

/*点击更改密码触发事件*/
function modify_passwd() {
    if (button_val == 0) {
        $("#pwd,#pwd_again").removeAttr('disabled').val('');
        $("#modify_passwd_button").val('恢复');
        button_val = 1;
        return;
    }
    if (button_val == 1) {
        $("#pwd,#pwd_again").attr('disabled','disabled').val(password_val);
        $("#modify_passwd_button").val('更改密码');
        button_val = 0;
        return;
    }

}
