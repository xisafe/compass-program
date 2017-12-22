/*
 * 描述: 测试添加模板和列表模板类
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2014.09.23 WangLin创建
 */

/*
 * 注释<1>：此文档的“配置对象”指new PagingHolder时传入的对象
 */

$(document).ready(function() {

    /* 渲染面板 */
    message_manager.render();

    add_panel.render();
    add_panel.hide();
    addPanelExtendRender();
    add_panel_expendRender();
    SrcIPGroup_panel.render();
    SrcIPGroup_panel.hide();

    DestIPGroup_panel.render();
    DestIPGroup_panel.hide();

    service_panel.render();
    service_panel.hide();

    SrcUserlist_panel.render();
    SrcUserlist_panel.hide();

    list_panel.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel(list_panel);
    list_panel.set_ass_add_panel(add_panel);

    add_panel.set_ass_message_manager(message_manager);
    list_panel.set_ass_message_manager(message_manager);

    do_request({
        ACTION: "area_data",
        param: '-s'
    }, function(data) {
        areaInfo = data;
        list_panel.update_info(true);
    })
});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/connection_control.cgi";
var areaInfo;
var message_box_config = { /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,
    /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",
    /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",
    /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}
//用户组配置面板
var SrcUserlist_config = {
    url: ass_url,
    check_in_id: "SrcUserlist_panel",
    panel_name: "SrcUserlist_panel",
    page_size: 0,
    panel_title: "配置用户组",
    is_panel_stretchable: true,
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    is_first_load: true,
    // render: monitoring_object_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    event_handler: {
        before_load_data: function(list_obj, data_item) {

        },
        after_load_data: function(list_obj, data_item) {

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
                onclick: "write_checked_for_jstree(SrcUserlist_panel,'SrcUserlist','user');"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "SrcUserlist_panel.hide();"
            }
        }]
    }
};
//目标IP配置面板
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
                onclick: "write_checked_for_list(DestIPGroup_panel,'DestIPGroup','Appid');"
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
//源IP配置面板
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
                onclick: "write_checked_for_list(SrcIPGroup_panel,'SrcIPGroup');"
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
var add_panel_config = {
    url: ass_url,
    /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",
    /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel",
    /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "连接控制策略",
    /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,
    /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,
    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,
    /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: { /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "m",
        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10,
        /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
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
            var form_id = add_obj.panel_control.panel_body_form_id;
            $('#'+form_id+' input[readonly]').each(function(index, el) {
                $(this).attr('title', $(this).val());
            });

            
            if (data_item.act == "丢弃") {
                $("input[type='radio'][name='act'][value='1']").prop("checked", true);
            } else if (data_item.act == "切断") {
                $("input[type='radio'][name='act'][value='2']").prop("checked", true);
            }
            select_items(data_item.dest_ipgroup,'dest_ipgroup');
            select_items(data_item.ip_or_user,'ip_or_user');
            // select_items(data_item.time_plan,'time_plan');
            // select_items(data_item.service_or_app,'service_app');

            var ip_mac_text = $('#sour_netip_text,#sour_mac_text,#dest_ip_text');
            for (var i = 0; i < ip_mac_text.length; i++) {
                var text_val = $(ip_mac_text[i]).val();
                text_val = text_val.replace(/\s/g,'').replace(/\，|,/g,'\n');
                $(ip_mac_text[i]).val(text_val);
            }
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
            $("#sour_mac_text,#SrcIPGroup,#SrcIPGroup_btn,#SrcUserlist,#SrcUserlist_btn,#sour_netip_text,#sour_mac_text,#DestIPGroup,#ipGroup,#dest_ip_text").hide();
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
    items_list: [ /* ***必填***，确定面板中有哪些规则，不填什么都没有 */ {
        title: "名称*",
        /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
        id: "name_tr",
        /* ==可选==，整行的id */
        name: "",
        /* ==可选==，整行的name */
        class: "",
        /* ==可选==，整行的class */
        functions: { /* ==可选==，整行相应事件的回调函数，DOM标准事件都可生效 */
            // onmouseover: "alert('hover on name line');",
            // onclick: "alert('click on name line');",
        },
        sub_items: [ /* **必填**，确定此行有哪些字段，不填什么都没有 */ {
            enable: true,
            /* **必填**，如果为不填或者为false,就不创建 */
            type: "text",
            /* ==可选==，默认是text类型，支持text,password,button,file,select,checkbox,
                                                          radio,textarea,label,items_group
                                              */
            name: "name",
            /* **必填**，字段的名字 */
            value: "",
            /* ==可选==，字段默认值 */
            functions: { /* ==可选==，DOM标准事件都可生效 */ },
            check: { /* ==可选==，如果要对字段进行检查，填写此字段 */
                type: "text",
                /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required: 1,
                /* **必填**，1表示必填，0表示字段可为空 */
                check: 'name|',
                /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                ass_check: function(check) {
                    /*
                     * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
                     *
                     * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
                     *
                     * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
                     */
                }
            }
        }]
    }, {
        title: "描述",
        sub_items: [{
            enable: true,
            type: "text",
            id: "note",
            name: "description",
            value: "",
            functions: {},
            check: {
                type: "text",
                required: 0,
                check: 'note|',
                ass_check: function(check) {

                }
            }
        }]
    }, {
        title: "源区域*",
        sub_items: [{
            enable: true,
            type: "select",
            id: "s_area",
            name: "s_area",
            style:"width:104px",
            // value: "",
            functions: {},
            //              check: {
            //                  type: "",
            //                  required: 1,
            //                  check: 'note|',
            //                  ass_check: function( check ) {
            //                  }
            //              }
        }]
    }, {
        title: "源IP/组/用户/MAC*",
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
                style: "width:104px;   vertical-align: text-top;",
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
                    }, {
                        text: "MAC",
                        id: "sour_mac",
                        value: "sour_mac",
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
                        type: 'text',
                        required: '1',
                        check: 'other',
                        other_reg:'/\[\^\]/',
                        ass_check: function(check) {

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
                    onclick: "show_config_panel(SrcIPGroup_panel,'SrcIPGroup');"
                },
                style: "width:40px;height:20px;border-radius:4px;display:none;margin:auto;"
            }, {
                enable: true,
                id: "SrcUserlist",
                name: "SrcUserlist",
                type: "text",
                readonly: "readonly",
                style: "height:16px;width:117px;display:none;",
                check: {
                        type: 'text',
                        required: '1',
                        check: 'other',
                        other_reg:'/\[\^\]/',
                        ass_check: function(check) {

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
                    onclick: "load_jstree_panel(SrcUserlist_panel,'load_userList','SrcUserlist','user');"
                },
                style: "width:40px;height:20px;border-radius:4px;display:none;margin:auto"
            }, {
                enable: true,
                // label: "请填写IP(每行一个)",
                type: "textarea",
                // tip: "请填写IP(每行一个)",
                id: "sour_netip_text",
                name: "sour_netip_text",
                placeholder: "请填写IP(每行一个)",
                style: "width:208px;height:84px;display:none;vertical-align: middle;",
                readonly: false,
                check: {
                    type: 'textarea',
                    required: '1',
                    check: 'ip|ip_addr_segment',
                    ass_check: function(check) {

                    }
                }
            }, {
                enable: true,
                type: "textarea",
                // tip: "请填写端口(每行一个)",
                id: "sour_mac_text",
                name: "sour_mac_text",
                placeholder: "请填写MAC(每行一个)",
                style: "width:208px;height:84px;display:none;vertical-align: middle;",
                readonly: false,
                check: {
                    type: 'textarea',
                    required: '1',
                    check: 'mac|',
                    ass_check: function(check) {

                    }
                }
            }]


        }]
    }, {
        title: "目标区域*",
        sub_items: [{
            enable: true,
            type: "select",
            id: "d_area",
            name: "d_area",
            style:'width:104px',
            // value: "",
            functions: {},
            //              check: {
            //                  type: "text",
            //                  required: 0,
            //                  check: 'note|',
            //                  ass_check: function( check ) {
            //                  }
            //              }
        }]
    }, {
        title: "目标IP/组*",
        sub_items: [{
                enable: true,
                type: "items_group",
                style: " margin:-5px;",
                sub_items: [{
                    enable: true,
                    type: "select",
                    id: "dest_ipgroup",
                    name: "dest_ipgroup",
                    value: "",
                    style: "width:104px;   vertical-align: text-top;",
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
                    enable: true,
                    type: "text",
                    id: "DestIPGroup",
                    style: "width:117px;display:none;",
                    readonly: "readonly",
                    name: "DestIPGroup",
                    check: {
                        type: 'text',
                        required: '1',
                        check: 'other',
                        other_reg:'/\[\^\]/',
                        ass_check: function(check) {

                        }
                    }

                }, {
                    enable: true,
                    type: "button",
                    value: "配置",
                    id: "ipGroup",
                    name: "ipGroup",
                    functions: {
                        onclick: "show_config_panel(DestIPGroup_panel,'DestIPGroup');"
                    },
                    style: "width:40px;height:20px;border-radius:4px;display:none;margin:auto"

                }, {
                    enable: true,
                    // label: "请填写IP(每行一个)",
                    type: "textarea",
                    // tip: "请填写IP(每行一个)",
                    id: "dest_ip_text",
                    name: "dest_ip_text",
                    placeholder: "请填写IP(每行一个)",
                    style: "width:208px;height:84px;display:none;vertical-align: middle;",
                    readonly: false,
                    check: {
                        type: 'textarea',
                        required: '1',
                        check: 'ip|ip_addr_segment',
                        ass_check: function(check) {

                        }
                    }
                }]
            }

        ]
    }, {
        title: "服务*",
        sub_items: [{
            enable: true,
            type: "text",
            readonly: "readonly",
            name: "destServiceNames",
            id: "destServiceNames",
            style: "width:106px",
            check: {
                        type: 'text',
                        required: '1',
                        check: 'other',
                        other_reg:'/\[\^\]/',
                        ass_check: function(check) {

                        }
                    }

        }, {
            enable: true,
            type: "text",
            name: "destServiceIds",
            id: "destServiceIds"
            
        }, {
            enable: true,
            type: "button",
            value: "配置",
            style:'margin:auto; height: 20px; border-radius: 4px;',
            functions: {
                onclick: "show_config_panel(service_panel,'destServiceNames');servicePanelExtend();"
            }
        }]
    }, {
        title: "每IP最大并发连接数*",
        sub_items: [{
            enable: true,
            type: "text",
            id: "note",
            name: "maxConn",
            value: "",
            functions: {},
            check: { /* ==可选==，如果要对字段进行检查，填写此字段 */
                type: "text",
                /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required: 1,
                /* **必填**，1表示必填，0表示字段可为空 */
                check: 'int|',
                /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                ass_check: function(eve) {
                    var maxConn = eve._getCURElementsByName("maxConn","input","add_panel_body_form_name_for_add_panel")[0].value;
                    if (maxConn >4294967295) {
                        msg = "最大并发连接数不能大于4294967295"
                    }
                     return msg;
                    /*
                     * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
                     *
                     * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
                     *
                     * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
                     */
                }
            }
        }]
    }, {
        title: "动作",
        sub_items: [{
            enable: true,
            type: "radio",
            label: "丢弃",
            name: "act",
            value: "1",
            checked: true
        }, {
            enable: true,
            type: "radio",
            label: "切断",
            name: "act",
            value: "2"
        }]
    }, {
        title: "日志",
        sub_items: [{
            enable: true,
            type: "checkbox",
            name: "isLog",
            value: "1",
            label: "记录",
            // checked: true

        }]
    }, {
        title: "启用",
        sub_items: [{
            enable: true,
            type: "checkbox",
            id: "enable",
            name: "enable",
            label: "启用",
            checked: true
        }]
    }]
};
var list_panel_render = {
    's_area': {
        render: function(default_rendered_text, data_item) {
            var rendered_text = "";
            if (typeof(areaInfo[default_rendered_text]) == 'undefined') {
                rendered_text = '<font style="color:red">该区域已失效</font>';
            }else{
                rendered_text = areaInfo[default_rendered_text];
            }
            return rendered_text;


        }
    },
    'd_area': {
        render: function(default_rendered_text, data_item) {
            var rendered_text = "";
            if (typeof(areaInfo[default_rendered_text]) == 'undefined') {
                rendered_text = '<font style="color:red">该区域已失效</font>';
            }else{
                rendered_text = areaInfo[default_rendered_text];
            }
            return rendered_text;


        }
    },
    'Dest_IP_Group':{
        render: function(default_rendered_text, data_item) {
            if (data_item.dest_ipgroup == 'dest_any') {
                return '<font style="color:green;">'+data_item.Dest_IP_Group+'</font>';
            }else if(data_item.dest_ipgroup == 'dest_group'){
                return '<font style="color:green;">网络/IP：</font>'+data_item.Dest_IP_Group;
            }else{
                return '<font style="color:green;">IP：</font>'+data_item.Dest_IP_Group;
            }
        }
    },
    'IpOrUser':{
        render: function(default_rendered_text, data_item) {
            if (data_item.ip_or_user == 'sour_user') {
                return '<font style="color:green;">用户：</font>'+data_item.IpOrUser;
            }else if(data_item.ip_or_user == 'sour_mac'){
                return '<font style="color:green;">MAC：</font>'+data_item.IpOrUser;
            }else if(data_item.ip_or_user == 'sour_netip'){
                return '<font style="color:green;">网络/IP：</font>'+data_item.IpOrUser;
            }else if(data_item.ip_or_user == 'sour_ip'){
                return '<font style="color:green;">IP：</font>'+data_item.IpOrUser;
            }else if(data_item.ip_or_user == 'sour_any'){
                return '<font style="color:green;">'+data_item.IpOrUser+'</font>';
            }
        }
    },
    'isLog':{
        render: function(default_rendered_text, data_item) {
            if (data_item.isLog == 'on') {
                return '记录';
            }else {
                return '不记录';
            }
        }
    }

}
var list_panel_config = {
    url: ass_url,
    /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",
    /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",
    /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                以区别不同面板 */
    page_size: 20,
    render: list_panel_render,
    default_search_config: {
        input_tip: "支持名称关键字查询",
        title: ""
    },
    event_handler: {
        before_load_data: function(list_obj) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 时，系统向服务器重新加载数据之前调用此函数
             *
             * 参数： -- list_obj      ==可选==，列表面板实例
             * 返回：无
             */
        },
        after_load_data: function(list_obj, response) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 后，并且服务器响应后调用此函数
             *
                                    
             * 参数： -- add_obj    ==可选==，添加面板实例，用户可以通过add_obj.show_
             *        -- response   ==可选==, 服务器响应的数据
             * 返回：无
             */
        },
    },
    panel_header: [ /* ***必填***，控制数据的加载以及表头显示 */ {
        enable: true,
        /* ==可选==，作用于整列，如果为不填或者为false，那么定义的这一列都不会显示 */
        type: "checkbox",
        /* ==可选==，作用于整列，type目前有checkbox/text/radio/action，分别对应不同类型的表头，
                                                 默认是text类型，表示显示加载的数据，如果是checkbox，表示整列都显示checkbox框，
                                                 如果是radio，表示整列都显示radio按钮，如果是action，表示这一列是操作列，可以自
                                                 行定义要显示哪些操作按钮，也可以使用默认渲染的操作按钮，见“配置对象”（注释<1>）
                                                 的render属性中的action属性
                                                     type为checkbox类型和radio类型在一个列表面板中一般不能一起使用，到目前为止，
                                                 也没有遇到这种需求，并且一起使用会有BUG。
                                                     type为action的列，默认会渲染启用/禁用按钮（如果本行数据中包含enable字段的
                                                 话会渲染）、编辑、删除，并且点击这三种类型按钮会有默认动作，点击启用/禁用按钮
                                                 会自动向服务器发起启用/禁用相关规则的请求，具体能否启用/禁用相关规则，还要靠后
                                                 台 的相关处理是否起作用；点击编辑时，会向添加面板加载数据并将添加面板切换为编
                                                 辑状态（前提是“列表面板”设置了关联的“添加面板”具体使用方法见add_list_demo.js中
                                                 set_ass_add_panel）；点击删除按钮时，会向服务器发起删除相关规则的请求，具体能
                                                 否删除相关规则，也要靠后台处理结果
                                      */
        title: "",
        /* =*可选*=，作用于标题头单元格，不同type，title需要的情况不同，
                                              一般type为text需要文字title，提示这一列数据表示什么意义，不填不显示标题
                                              当type为checkbox时，会默认渲染‘全选checkbox框’，填了title也将不起作用，
                                          当type为radio类型时，title变为‘请选择’，填了title也不起作用，当type为action时，
                                          默认标题是“活动/动作”，如果在action配置项填了title属性，会覆盖默认标题，示例见
                                          下文
                               */
        name: "checkbox",
        /* **必填**，作用于整列，控制整列要显示的数据项
                                                     ****当type为checkbox、radio、action之一时，name也必须对应为三项中的一项
                                                     如果要渲染每列数据，到“配置对象”（注释<1>）的render属性中去配置与当前name值
                                                 一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                                 第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                     */
        class: "",
        /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
        td_class: "align-center",
        /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                              当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                              在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                  */
        width: "5%",
        /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                             以精确控制你想要的宽度
                                 */
        functions: { /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            // onclick: "alert(this.value);",
        }
    }, {
        enable: true,
        type: "text",
        title: "序号",
        name: "idView",
        td_class: "align-center",
        width: "3%"
    }, {
        enable: true,
        type: "text",
        title: "名称",
        name: "name",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "描述",
        name: "description",
        width: "12%"
    },
    {
        enable: true,
        type: "text",
        title: "源区域",
        name: "s_area",
        width: "10%"
    },
    {
        enable: true,
        type: "text",
        title: "源IP/组/用户/MAC",
        name: "IpOrUser",
        width: "11%"
    }, {
        enable: true,
        type: "text",
        title: "目标区域",
        name: "d_area",
        width: "11%"
    }, {
        enable: true,
        type: "text",
        title: "目标IP/组",
        name: "Dest_IP_Group",
        width: "11%"
    }, {
        enable: true,
        type: "text",
        title: "服务",
        name: "destServiceNames",
        width: "7%"
    }, {
        enable: true,
        type: "text",
        title: "最大连接数",
        name: "maxConn",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "日志",
        td_class: "align-center",
        name: "isLogView",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "动作",
        td_class: "align-center",
        name: "act",
        width: "5%"
    }, {
        enable: true,
        type: "action",
        name: "action",
        td_class: "align-center",
        width: "7%"
    },{
        enable: true,
        type: "move",
        name: "move",
        td_class: "align-center",
        width: "8%" 
    }],
    top_widgets: [ /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */ {
        enable: true,
        /* =*可选*=，如果为不填或者为false,就不创建 */
        type: "image_button",
        /* =*可选*=，目前支持类型有text,password,file,select,checkbox,radio,textarea,
                                                     label,button和image_button,最常用的是image_button，并且目前考虑得
                                                     比较多其他组件比较弱，但能勉强使用，如果其他需求很强，需要进一步
                                                     扩展
                                          */
        button_icon: "add16x16.png",
        /* ==可选==，image_button的图标，如果没有设置，就没有图标，image_button独有字段 */
        button_text: "新建",
        /* **必填**，image_button的文字，这个必须设置,建议在五个字以内，image_button独有字段 */
        functions: { /* ==可选==，回调函数，没有的话就只是一个按钮，什么也不做 */
            onclick: "add_rule(this);"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "delete.png",
        button_text: "删除",
        functions: {
            onclick: "delete_selected_items(this);"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "on.png",
        button_text: "启用",
        functions: {
            onclick: "enable_selected_items();"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "off.png",
        button_text: "禁用",
        functions: {
            onclick: "disable_selected_items();"
        }
    }]
};

//服务配置面板
var service_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "service_panel", // ***必填***，确定面板挂载在哪里 
    page_size: 10, //===可选===，定义页大小，默认是15 
    panel_name: "service_panel", // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true, // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置服务",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    panel_header: [ // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": true, //用户控制表头是否显示
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
            "enable": true,
            "type": "text",
            "title": "服务名称", //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "60%"
        }, {
            "enable": true,
            "type": "text",
            "title": "服务类型", //一般text类型需要title,不然列表没有标题
            "name": "type",
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
                onclick: "write_checked_for_list(service_panel,'destServiceNames','destServiceIds','idReal');"
            }
        }, {
            enable: true,
            type: "image_button",
            class: "",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "service_panel.hide();"
            }
        }]
    }
}

var add_panel = new RuleAddPanel(add_panel_config);
var list_panel = new PagingHolder(list_panel_config);

var SrcUserlist_panel = new PagingHolder(SrcUserlist_config);
var service_panel = new PagingHolder(service_config);
var message_manager = new MessageManager(message_box_config);
var SrcIPGroup_panel = new PagingHolder(SrcIPGroup_config);
var DestIPGroup_panel = new PagingHolder(DestIPGroup_config);

function delete_selected_items(element) {
    var checked_items = list_panel.get_checked_items();

    if (checked_items.length == 0) {
        list_panel.show_error_mesg("请选择要删除的规则");
        return;
    }
    var checked_items_id = new Array();
    for (var i = 0; i < checked_items.length; i++) {
        checked_items_id.push(checked_items[i].id);
    }

    var ids = checked_items_id.join("&");

    list_panel.delete_item(ids);
}

function add_rule(element) {
    add_panel.show();
}

//add_panel额外渲染函数
function addPanelExtendRender() {
    $("#src").find("input[type='text']").attr("disabled", "disavled");
    $("#src").find("input[type='button']").attr("disabled", "disabled").removeClass("add-panel-form-button").addClass("add-panel-form-disabled-button");
    $("#destServiceIds").attr("hidden", "hidden");
    $("#destServiceIds").parent().css("margin", 0);
}
//

//改变IP组/用户组disabled状态
function changeDisabled(e) {
    var my$ = $(e).parent().parent();
    var other$ = my$.parent().siblings().children();
    my$.children().children("input").removeAttr("disabled");
    my$.find("input[type='button']").removeClass("add-panel-form-disabled-button").addClass("add-panel-form-button");
    other$.children().children("input[type='text']").attr("disabled", "disabled");
    other$.children().children("input[type='button']").attr("disabled", "disabled").removeClass("add-panel-form-button").addClass("add-panel-form-disabled-button");
    other$.children().children("input[type='text']").val("");
}

//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: ass_url,
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request) {
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}


// //获取用户组配置面板数据
// function load_userList () {

//     var sending_data = {
//         ACTION: "load_userList"

//     };

//     function ondatareceived(data) {

//         jstree_render(data);
//         SrcUserlist_panel.show();


//     }
//     do_request(sending_data, ondatareceived, function() {
//         message_manager.show_popup_error_mesg("暂无用户组数据！");
//     });

// }


// //请求服务数据
// function load_service() {
//     service_panel.update_info(true);
//     service_panel.show();
// }

// //将IP组内容写入input框
// function write_ipGroup(str) {

//     var panel, textId;
//     var panel = ipGroup_panel;
//     if (str == "src") {
//         textId = "srcIpGroup";
//     } else {
//         textId = "destIpGroup";
//     }
//     write_data(panel, textId);
// }

// //将用户组数据写入input框
// function write_userlist () {

//     var nodes = $("#for_jstree").jstree().get_checked(true);
//     var length = nodes.length;
//     var array = new Array();
//     var str = "";

//     for (var i = 0; i < length; i++) {
//         if (nodes[i].type == "user") {
//             array.push(nodes[i].text);
//         }
//     }
//     if (array.length == 0) {
//         message_manager.show_popup_error_mesg("没有明确的用户！");
//         return;
//     }
//     for (var i = 0; i < array.length - 1; i++) {
//         str += array[i] + ",";
//     }
//     str += array[array.length - 1];

//     $("#SrcUserlist").val(str);
//     //writeFrame(document.getElementById("SrcUserlist"), array);
//     SrcUserlist_panel.hide();
// }

// //将服务数据写入input框
// function write_service() {

//     var panel = service_panel;
//     var checked_items = panel.get_checked_items();
//     var str = "";
//     var ids = "";
//     //var array = new Array();
//     var length = checked_items.length;
//     if (!checked_items[0].name) {
//         alert("请选择至少一种服务");
//     } else {
//         for (var i = 0; i < length - 1; i++) {
//             str += checked_items[i].name + ",";
//             ids += checked_items[i].idReal + ",";
//             //array.push(checked_items[i].name);
//         }
//         str += checked_items[length - 1].name;
//         ids += checked_items[length - 1].idReal;
//         //array.push(checked_items[length-1].name);
//         $("#destServiceNames").val(str);
//         $("#destServiceIds").val(ids);
//         //writeFrame(document.getElementById(textId), array);
//         panel.hide();
//     }
// }

// //将配置数据写入文本框
// function write_data(panel, textId) {

//     var checked_items = panel.get_checked_items();
//     var str = "";
//     //var array = new Array();
//     var length = checked_items.length;
//     if (!checked_items[0].name) {
//         alert("请选择至少一个IP组");
//     } else {
//         for (var i = 0; i < length - 1; i++) {
//             str += checked_items[i].name + ",";
//             //array.push(checked_items[i].name);
//         }
//         str += checked_items[length - 1].name;
//         //array.push(checked_items[length-1].name);
//         $("#" + textId).val(str);
//         //writeFrame(document.getElementById(textId), array);
//         panel.hide();
//     }
// }
// //渲染用户组JS树
// function jstree_render(data) {
//     if ($("#for_jstree")) {
//         $("#for_jstree").remove();
//     }
//     var div = document.createElement("div");
//     div.setAttribute("id", "for_jstree");
//     var $div = $(div);
//     $("#list_panel_id_for_SrcUserlist_panel .container-main-body").append($div);
//     $("#list_panel_id_for_SrcUserlist_panel .container-main-body").css("min-height", "200px");
//     $("#list_panel_id_for_SrcUserlist_panel .container-main-body .rule-list").remove();
//     $('#for_jstree').jstree({
//         "plugins": [
//             "checkbox",
//             "state", "types", "wholerow"
//         ],
//         "core": {
//             "themes": {
//                 "stripes": true
//             },
//             "data": data

//         },
//         "types": {
//             "user": {
//                 "icon": "../images/user.png",
//             }
//         },
//         "checkbox": {
//             "keep_selected_style": false
//         },

//     });
// }

//列表导航栏启用按钮
function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    if (checked_items.length < 1) {
        message_manager.show_popup_note_mesg("请选择一项需要启用的策略！");
    } else {
        var checked_items_id = new Array();
        for (var i = 0; i < checked_items.length; i++) {
            checked_items_id.push(checked_items[i].id);
        }

        var ids = checked_items_id.join("&");

        list_panel.enable_item(ids);
    }
}

//列表导航栏禁用按钮
function disable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    if (checked_items.length < 1) {
        message_manager.show_popup_note_mesg("请选择一项需要禁用的策略！");
    } else {
        var checked_items_id = new Array();
        for (var i = 0; i < checked_items.length; i++) {
            checked_items_id.push(checked_items[i].id);
        }

        var ids = checked_items_id.join("&");

        list_panel.disable_item(ids);
    }
}

//对服务面板做一些处理
function servicePanelExtend() {
    $("#control_checkbox_for_service_panel").prop("hidden", true);
    var any$ = $("#rule_listb_for_service_panel>tr:first-child>td:first-child>input");
    var detail = service_panel.detail_data;
    any$.on("click", function() {
        var flag = any$.prop("checked");
        $(".checkbox_item_for_service_panel").prop("checked", false);
        any$.prop("checked", flag);
        if (any$.prop("checked") == true) {
            $(".checkbox_item_for_service_panel").prop("disabled", true);
            any$.prop("disabled", false);
            for (var i = 1; i < detail.length; i++) {
                if (detail[i].checked != undefined) {
                    detail[i].checked = false;
                }
            }
        } else {
            $(".checkbox_item_for_service_panel").prop("disabled", false);
        }
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
        }
    };
    select_and_show(val,id,select_obj);
}

//配置按钮弹出配置模版事件
function add_configure_rule(e) {
    e.update_info(true);
    e.show();
}
function write_checked_for_list(panel, textId,id_id) {
    var checked_items = panel.get_checked_items();
    var checked_str = "",checked_id_str='';
    if (checked_items.length == 0) {
        message_manager.show_popup_error_mesg('请至少选择其中一项！');
        return;
    } else {
        for (var i = 0; i < checked_items.length; i++) {
            var separator = i == 0 ? '' : ', ';
            checked_str += separator ;
            checked_str += checked_items[i].name ;
            if (id_id) {
                checked_id_str += separator ;
                checked_id_str += checked_items[i].id ;
            }
        }
    }
    $("#" + textId).val(checked_str).attr('title',checked_str);
    id_id ? $('#'+id_id).val(checked_id_str) : true;
    panel.hide();
}
// //将配置的内容写入文本框
// function write_lib_data(panel, textId) {
//     var checked_items = panel.get_checked_items();
//     var dataText = new Object();
//     dataText.SrcIPGroup = "请选择至少一组源IP组！";
//     dataText.DestIPGroup = "请选择至少一组目标IP组！";
//     dataText.ServiceName = "请选择至少一种服务";
//     var str = "";
//     var array = new Array();
//     var length = checked_items.length;
//     if (checked_items.length == 0) {
//         message_manager.show_popup_error_mesg(dataText[textId]);
//         return;
//     } else {
//         for (var i = 0; i < length - 1; i++) {
//             str += checked_items[i].name + "，";
//             array.push(checked_items[i].name);
//         }
//         str += checked_items[length - 1].name;
//         array.push(checked_items[length - 1].name);
//         $("#" + textId).val(str);
//         writeFrame(document.getElementById(textId), array);
//         panel.hide();
//     }
// }

// //将input内容写进提示框
// function writeFrame(e, array) {

//     if (array.length < 4) {
//         clearFrame(e);
//         return;
//     }
//     var ul$ = $(e).next().children("ul");
//     ul$.html("");
//     for (var i = 0; i < array.length && i < 15; i++) {
//         ul$.append("<li>" + array[i] + "</li>");
//     }
//     if (array.length > 15) {
//         ul$.append("<li>...</li>");
//     }
//     susFrame(e);
// }
// //清除input上的显示提示框类
// function clearFrame(e) {

//     $(e).removeClass("displayPro");

// }

// //绑定显示提示框类到input上
// function susFrame(e) {

//     $(e).addClass("displayPro");

// }
//add_panel额外的的渲染函数
function add_panel_expendRender() {
    // getTimeData("singletime");
    // getTimeData("looptime");
    getAreaData("area");

    // $("#add_panel_id_for_add_panel").parent().css("width","650px");
    // $("#Appid").attr("type", "hidden");
    // $("#DestIPGroup").css({"margin-left":"99px","height":"16px"});

    //生成提示框
    // createFrame(document.getElementById("SrcIPGroup"));
    // createFrame(document.getElementById("SrcUserlist"));
    // createFrame(document.getElementById("DestIPGroup"));
    // createFrame(document.getElementById("ServiceName"));
    // createFrame(document.getElementById("Appname"));



}

//生成提示框
// function createFrame(e) {
//     $(e).parent().addClass("textAreaDivParent");
//     $(e).after("<div class = 'textAreaDiv' hidden='hidden'><div class='divArrow'></div><ul class='divText'></ul></div>");
// }
function getAreaData(e) {
    var sending_data = {
        ACTION: e + "_data"
    }

    function ondatareceived(data) {
        var area_str = "";
        for (var i = 0; i < data.length; i++) {
            area_str += '<option value="' + data[i].value + '">' + data[i].text + '</option>'
        }
        $("#s_area,#d_area").html('');
        $("#s_area,#d_area").append(area_str);

    }

    do_request(sending_data, ondatareceived);
}
