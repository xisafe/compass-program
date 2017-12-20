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
    add_panel_expendRender();
    add_panel.hide();

    list_panel.render();
    SrcIPGroup_panel.render();
    SrcIPGroup_panel.hide();
    DestIPGroup_panel.render();
    DestIPGroup_panel.hide();
    ServiceName_panel.render();

    ServiceName_panel.hide();

    Appid_panel.render();
    (function() {
        var img = $('<img title="重置" src="/images/reconnect.png">');
        img.css({
            cursor: "pointer",
            position: "relative",
            top: "3px",
            left: "10px"
        });
        img.on("click", function() {
            $("#for_appJstree").jstree().deselect_all();
        })
        
        $("#list_panel_id_for_Appid_panel .list-panel-title").find("span").after(img);
    })();
    Appid_panel.hide();
    SrcUserlist_panel.render();
    SrcUserlist_panel.hide();

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

    $("#search_key_for_list_panel").css("font-size","5px");
    $("#search_key_for_list_panel").attr("placeholder","支持名称,源IP,目标IP,服务/应用查询");
    select_app(this.val,this.id);
    
});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/appfilter.cgi";
var areaInfo;
var message_box_config = { /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,
    /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",
    /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",
    /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

var add_panel_config = {
    url: ass_url,
    /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",
    /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel",
    /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "应用控制策略",
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
            if (data_item.sour_port == 'port_tcp') {
                data_item.port_tcp_text = data_item.sour_port_text ;
            } else if (data_item.sour_port == 'port_udp') {
                data_item.port_udp_text = data_item.sour_port_text ;
            }else if (data_item.sour_port == 'port_tu') {
                data_item.port_tu_text = data_item.sour_port_text ;
            }
            /*
             * ===可选事件函数===，在数据项往添加面板加载时，数据还“未”装载入面板时调用，
             *    一般是点击编辑后数据项才会向添加面板加载
             *
             * 参数：-- add_obj   ==可选==，添加面板实例
             *       -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
        },
        after_load_data: function(add_obj, data_item) {
            var form_id = add_obj.panel_control.panel_body_form_id;
            $('#'+form_id+' input[readonly]').each(function(index, el) {
                $(this).attr('title', $(this).val());
            });
            /*
             * ===可选事件函数===，在数据项往添加面板加载后，数据“已”装载入面板时调用
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *         -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
            // var txt = $("#Appname").val();
            // var obj = txt.split(",")
            // var appname = document.getElementById("Appname");
            // writeFrame(appname,obj );
            
            select_items(data_item.dest_ipgroup,'dest_ipgroup');
            select_items(data_item.ip_or_user,'ip_or_user');
            select_items(data_item.time_plan,'time_plan');
            select_items(data_item.service_or_app,'service_app');
            select_items(data_item.sour_port,'sour_port');

            var ip_mac_text = $('#sour_netip_text,#sour_mac_text,#dest_ip_text,#port_tcp_text,#port_udp_text,#port_tu_text');
            for (var i = 0; i < ip_mac_text.length; i++) {
                var text_val = $(ip_mac_text[i]).val();
                text_val = text_val.replace(/\s/g,'').replace(/\，|,/g,'\n');
                $(ip_mac_text[i]).val(text_val);
            }
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
            $("#SrcIPGroup,#SrcIPGroup_btn,#SrcUserlist,#SrcUserlist_btn,#sour_netip_text,#sour_mac_text").hide();
            $("#DestIPGroup,#ipGroup,#dest_ip_text").hide();
            $("#ServiceName,#ServiceName_btn,#Appname,#Appid_btn").hide();
            $("#singletime,#looptime").hide();
            $("#port_tcp_text,#port_udp_text,#port_tu_text").hide();
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
            /* 返回：true/false
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
                    // console.log("aaa");
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
            id: "description",
            name: "description",
            value: "",
            functions: {},
            check: {
                type: "text",
                required: 0,
                check: 'note|',
                ass_check: function(check) {
                    // console.log("bbbb");
                }
            }
        }]
    }, {
        title: "源区域",
        sub_items: [{
            enable: true,
            type: "select",
            id: "s_area",
            name: "s_area",
            style:"width:104px;",
            // value: "",
            functions: {},
            //              check: {
            //                  type: "",
            //                  required: 1,
            //                  check: 'note|',
            //                  ass_check: function( check ) {
            // console.log("bbbb");
            //                  }
            //              }
        }]
    }, {
        title: "源端口",
        sub_items: [{
                enable: true,
                type: "items_group",
                style: " margin:-5px;",
                sub_items: [{
                    enable: true,
                    type: "select",
                    id: "sour_port",
                    name: "sour_port",
                    value: "",
                    style: "width:104px;   vertical-align: text-top;",
                    functions: {
                        onchange: "select_items(this.value,this.id);"
                    },
                    options: [{
                        text: "任意",
                        id: "port_any",
                        value: "port_any",
                        functions: {}
                    }, {
                        text: "ICMP",
                        id: "port_icmp",
                        value: "port_icmp",
                        functions: {}
                    }, {
                        text: "TCP",
                        id: "port_tcp",
                        value: "port_tcp",
                        functions: {}
                    }, {
                        text: "UDP",
                        id: "port_udp",
                        value: "port_udp",
                        functions: {}
                    }, {
                        text: "TCP+UDP",
                        id: "port_tu",
                        value: "port_tu",
                        functions: {}
                    }]
                }, {
                    enable: true,
                    type: "textarea",
                    id: "port_tcp_text",
                    name: "port_tcp_text",
                    placeholder: "请填写端口范围(每行一个)",
                    style: "width:208px;height:84px;display:none;vertical-align: middle;",
                    readonly: false,
                    check: {
                        type: 'textarea',
                        required: '1',
                        check: 'port|port_range|',
                        ass_check: function(check) {

                        }
                    }
                }, {
                    enable: true,
                    type: "textarea",
                    id: "port_udp_text",
                    name: "port_udp_text",
                    placeholder: "请填写端口范围(每行一个)",
                    style: "width:208px;height:84px;display:none;vertical-align: middle;",
                    readonly: false,
                    check: {
                        type: 'textarea',
                        required: '1',
                        check: 'port|port_range|',
                        ass_check: function(check) {

                        }
                    }
                }, {
                    enable: true,
                    type: "textarea",
                    id: "port_tu_text",
                    name: "port_tu_text",
                    placeholder: "请填写端口范围(每行一个)",
                    style: "width:208px;height:84px;display:none;vertical-align: middle;",
                    readonly: false,
                    check: {
                        type: 'textarea',
                        required: '1',
                        check: 'port|port_range|',
                        ass_check: function(check) {

                        }
                    }
                }]
            }

        ]
    },{
        title: "源IP/组/用户/MAC",
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
                    onclick: "load_jstree_panel(SrcUserlist_panel,'load_userlist','SrcUserlist','user');"
                },
                style: "width:40px;height:20px;border-radius:4px;display:none;margin:auto;"
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
        title: "目标区域",
        sub_items: [{
            enable: true,
            type: "select",
            id: "d_area",
            name: "d_area",
            style:"width:104px;",
            // value: "",
            functions: {},
            //              check: {
            //                  type: "text",
            //                  required: 0,
            //                  check: 'note|',
            //                  ass_check: function( check ) {
            // console.log("bbbb");
            //                  }
            //              }
        }]
    }, {
        title: "目标IP/组",
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
                    style: "width:40px;height:20px;border-radius:4px;display:none;margin:auto;"

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
        title: "服务/应用*",
        sub_items: [{
            enable: true,
            type: "items_group",
            style: "line-height:20px;margin:-5px;",
            sub_items: [{
                enable: true,
                id: "service_app",
                name: "service_or_app",
                type: "select",
                style: "width:104px;   vertical-align: text-top;",
                value: "",
                functions: {
                    onchange: "select_items (this.value,this.id);select_app(this.value,this.id);"
                },
                options: [{
                    text: "服务",
                    id: "service",
                    value: "service",
                    functions: {}
                }, {
                    text: "应用",
                    id: "app",
                    value: "app",
                    functions: {
                        // onchange: "select_app(this.value,this.id);"
                    }
                }]
            }, {
                enable: true,
                id: "ServiceName",
                name: "ServiceName",
                type: "text",
                // disabled: "disabled",
                readonly: "readonly",
                style: "height:16px;width:117px",
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
                id: "ServiceName_btn",
                name: "user_group_btn",
                type: "button",
                // disabled: "disabled",
                class: "set-button",
                value: "配置",
                functions: {
                    onclick: "show_config_panel(ServiceName_panel,'ServiceName');	servicePanelExtend();"
                },
                style: "width:40px;height:20px;border-radius:4px;margin:auto;"
            }, {
                enable: true,
                id: "Appname",
                name: "Appname",
                type: "text",
                // disabled: "disabled",
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
                id: "Appid_btn",
                name: "user_group_btn",
                type: "button",
                // disabled: "disabled",
                class: "set-button",
                value: "配置",
                functions: {
                    onclick: "load_jstree_panel(Appid_panel,'load_app','Appname','app');"
                },
                style: "width:40px;height:20px;border-radius:4px;display:none;margin:auto;"
            }, {
                enable: true,
                id: "Appid",
                name: "Appid",
                type: "text"
            }]
        }]
    }, {
        title: "时间计划",
        sub_items: [{
            enable: true,
            type: "items_group",
            style: "line-height:20px;margin:-5px;",
            sub_items: [{
                enable: true,
                id: "time_plan",
                name: "time_plan",
                type: "select",
                style: "width:104px;   vertical-align: text-top;",
                value: "",
                functions: {
                    onchange: "select_items (this.value,this.id);"
                },
                options: [{
                    text: "无",
                    id: "time_plan_no",
                    value: "time_plan_no",
                    functions: {}
                }, {
                    text: "单次时间计划",
                    id: "single_plan",
                    value: "single_plan",
                    functions: {}
                }, {
                    text: "循环时间计划",
                    id: "circle_plan",
                    value: "circle_plan",
                    functions: {}
                }]
            }, {
                enable: true,
                id: "singletime",
                name: "TimeName",
                style: "width:212px;display:none;",
                type: "select",
                disabled: "disabled",
                check: {
                    type:"select-one",
                    required:1,
                    check: 'other',
                    other_reg:'/\[\^\]/',
                    ass_check: function(check) {

                    }
                }
            }, {
                enable: true,
                id: "looptime",
                name: "TimeName",
                type: "select",
                style: "width:192px;display:none;",
                disabled: "disabled",
                check: {
                    type:"select-one",
                    required:1,
                    check: 'other',
                    other_reg:'/\[\^\]/',
                    ass_check: function(check) {

                    }
                }
            }]
        }]
    }, {
        title: "动作",
        sub_items: [{
                enable: true,
                label: "允许",
                type: "radio",
                id: "permit",
                name: "action_permission",
                checked: true,
                value: "0",
            }, {
                enable: true,
                label: "丢弃",
                type: "radio",
                id: "forbid",
                name: "action_permission",
                value: "1",
            }, {
                enable: false,
                label: "切断会话",
                type: "radio",
                id: "cut",
                name: "action_permission",
                value: "2",
            }
            // {
            // enable:true,
            // label:"拒绝",
            // type:"radio",
            // id:"refuse",
            // name:"action_permission",
            // value:"3",
            // }
        ]
    }, {
        title: "日志",
        sub_items: [{
            enable: true,
            type: "checkbox",
            label: "记录",
            id: "isLog",
            name: "isLog",
            // checked: true
        }]
    }, {
        title: "启用",
        sub_items: [{
            enable: true,
            type: "checkbox",
            label: "启用",
            id: "enable",
            name: "enable",
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
    'TimeName':{
        render: function(default_rendered_text, data_item) {
            if (data_item.SingleOrCircle == '') {
                return '<font style="color:green;">'+data_item.TimeName+'</font>';
            }else if(data_item.SingleOrCircle == 'single_plan'){
                return '<font style="color:green;">单次: </font>'+data_item.TimeName;
            }else{
                return '<font style="color:green;">循环: </font>'+data_item.TimeName;
            }
        }
    },
    'Dest_IP_Group':{
        render: function(default_rendered_text, data_item) {
            // data_item.Dest_IP_Group = data_item.Dest_IP_Group.replace(/\,/g,', ');
            // data_item.Dest_IP_Group = data_item.Dest_IP_Group.replace(/\，/g,', ');
            if (data_item.dest_ipgroup == 'dest_any') {
                return '<font style="color:green;">'+data_item.Dest_IP_Group+'</font>';
            }else if(data_item.dest_ipgroup == 'dest_group'){
                return '<font style="color:green;">网络/IP: </font>'+data_item.Dest_IP_Group;
            }else{
                return '<font style="color:green;">IP: </font>'+data_item.Dest_IP_Group;
            }
        }
    },
    'ServiceOrApp':{
        render: function(default_rendered_text, data_item) {
            // data_item.ServiceOrApp = data_item.ServiceOrApp.replace(/\,/g,', ');
            // data_item.ServiceOrApp = data_item.ServiceOrApp.replace(/\，/g,', ');
            if (data_item.service_or_app == 'app') {
                return '<font style="color:green;">应用: </font>'+data_item.ServiceOrApp;
            }else if(data_item.service_or_app == 'service'){
                return '<font style="color:green;">服务: </font>'+data_item.ServiceOrApp;
            }
        }
    },
    'IpOrUser':{
        render: function(default_rendered_text, data_item) {
            // data_item.IpOrUser = data_item.IpOrUser.replace(/\,/g,', ');
            // data_item.IpOrUser = data_item.IpOrUser.replace(/\，/g,', ');
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
    'sour_port_text':{
        render: function(default_rendered_text, data_item) {
            var port = data_item.sour_port.toUpperCase();
            port = port.replace(/PORT\_/,'');
            port == 'TU' ? port = 'TCP+UDP': port = port ;
            if (port == 'ANY') {
                return '<font style="color:green;">任意</font>';
            }else if(port == 'ICMP'){
                return '<font style="color:green;">ICMP</font>';
            }
            else{
                if (default_rendered_text == 'any') {
                    default_rendered_text = '';
                }else{
                    port = port+': ';
                }
                return '<font style="color:green;">'+port+'</font>'+default_rendered_text;
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
    event_handler: {
        before_load_data: function(list_obj) {
            // console.log(list_obj);
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 时，系统向服务器重新加载数据之前调用此函数
             *
             * 参数:  -- list_obj      ==可选==，列表面板实例
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
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "名称",
        name: "name",
        width: "7%"
    },{
        enable: true,
        type: "text",
        title: "描述",
        name: "description",
        width: "7%"
    },
    {
        enable: true,
        type: "text",
        title: "源区域",
        name: "s_area",
        width: "7%"
    },{
        enable: true,
        type: "text",
        title: "源端口",
        name: "sour_port_text",
        width: "7%" 
    }, {
        enable: true,
        type: "text",
        title: "源IP/组/用户/MAC",
        name: "IpOrUser",
        width: "12%"
    }, {
        enable: true,
        type: "text",
        title: "目标区域",
        name: "d_area",
        width: "8%"
    }, {
        enable: true,
        type: "text",
        title: "目标IP/组",
        name: "Dest_IP_Group",
        width: "7%"
    }, {
        enable: true,
        type: "text",
        title: "服务/应用",
        name: "ServiceOrApp",
        width: "8%"
    }, {
        enable: true,
        type: "text",
        title: "时间计划",
        name: "TimeName",
        width: "7%"
    }, {
        enable: true,
        type: "text",
        title: "日志",
        name: "isLog",
        td_class: "align-center",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "动作",
        name: "actionView",
        td_class: "align-center",
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
        button_text: "新增",
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
                onclick: "write_checked_for_list(DestIPGroup_panel,'DestIPGroup');"
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

//服务名称配置面板
var ServiceName_render = {
    /*'protocol': {
         render: function( default_rendered_text, data_item ) {
             var result_render = "RIP";
             return '<span>' + result_render + '</span>';
         },
     },*/

};

var ServiceName_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "ServiceName_panel", // ***必填***，确定面板挂载在哪里 
    page_size: 10, //===可选===，定义页大小，默认是15 
    panel_name: "ServiceName_panel", // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
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
    render: ServiceName_render, //===可选===，渲染每列数据 
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
                onclick: "write_checked_for_list(ServiceName_panel,'ServiceName');"
            }
        }, {
            enable: true,
            type: "image_button",
            class: "",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "ServiceName_panel.hide();"
            }
        }]
    }
}

//应用ID配置面板
var Appid_render = {
    /*'protocol': {
         render: function( default_rendered_text, data_item ) {
             var result_render = "RIP";
             return '<span>' + result_render + '</span>';
         },
     },*/

};

var Appid_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "Appid_panel", // ***必填***，确定面板挂载在哪里 
    page_size: 10, //===可选===，定义页大小，默认是15 
    panel_name: "Appid_panel", // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true, // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置应用",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    render: Appid_render, //===可选===，渲染每列数据 
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
                // onclick:"write_app()"
                onclick: "write_checked_for_jstree(Appid_panel,'Appname','app','Appid');"
            }
        }, {
            enable: true,
            type: "image_button",
            class: "",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "Appid_panel.hide();"
            }
        }]
    }
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

var add_panel = new RuleAddPanel(add_panel_config);
var list_panel = new PagingHolder(list_panel_config);
var message_manager = new MessageManager(message_box_config);
var SrcIPGroup_panel = new PagingHolder(SrcIPGroup_config);
var DestIPGroup_panel = new PagingHolder(DestIPGroup_config);
var ServiceName_panel = new PagingHolder(ServiceName_config);
var Appid_panel = new PagingHolder(Appid_config);
var SrcUserlist_panel = new PagingHolder(SrcUserlist_config);

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
    $("#ServiceName,#ServiceName_btn").show().removeAttr('disabled').parent().show();
    add_panel.show();
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
        },
        'sour_port': {
            'port_tcp' : '#port_tcp_text',
            'port_udp' : '#port_udp_text',
            'port_tu' : '#port_tu_text'
        }
    };

    select_and_show(val,id,select_obj);
    
}

//为所有配置按钮初始化样式
function set_button() {

    $(".set-button").addClass("add-panel-form-button").removeClass("add-panel-form-disabled-button");
}


//对服务面板做一些处理
function servicePanelExtend() {
    $("#control_checkbox_for_ServiceName_panel").prop("hidden", true);
    var any$ = $("#rule_listb_for_ServiceName_panel>tr:first-child>td:first-child>input");
    var detail = ServiceName_panel.detail_data;
    any$.on("click", function() {
        var flag = any$.prop("checked");
        $(".checkbox_item_for_ServiceName_panel").prop("checked", false);
        any$.prop("checked", flag);
        if (any$.prop("checked") == true) {
            $(".checkbox_item_for_ServiceName_panel").prop("disabled", true);
            any$.prop("disabled", false);
            for (var i = 1; i < detail.length; i++) {
                if (detail[i].checked != undefined) {
                    detail[i].checked = false;
                }
            }
        } else {
            $(".checkbox_item_for_ServiceName_panel").prop("disabled", false);
        }
    });
}



//获得生效时间数据
function getTimeData(e) {

    var sending_data = {
        ACTION: e + "_data"
    }

    function ondatareceived(data) {

        if (e == "singletime") {
            var time_str = '';
        } else {
            var time_str = '';
        }
        for (var i = 0; i < data.time_data.length; i++) {
            time_str += '<option value="' + data.time_data[i] + '">' + data.time_data[i] + '</option>';
        }
        $("#" + e).html('');
        $("#" + e).append(time_str);
    }

    do_request(sending_data, ondatareceived);
}

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
//将配置的内容写入文本框
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
    $("#" + textId).val(checked_str);
    id_id ? $('#'+id_id).val(checked_id_str) : true;
    panel.hide();
}

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
//add_panel额外的的渲染函数
function add_panel_expendRender() {
    set_button();
    getTimeData("singletime");
    getTimeData("looptime");
    getAreaData("area");

    // $("#add_panel_id_for_add_panel").parent().css("width","650px");
    $("#Appid").attr("type", "hidden");
    // $("#DestIPGroup").css({"margin-left":"99px","height":"16px"});

    //生成提示框
    // createFrame(document.getElementById("SrcIPGroup"));
    // createFrame(document.getElementById("SrcUserlist"));
    // createFrame(document.getElementById("DestIPGroup"));
    // createFrame(document.getElementById("ServiceName"));
    // createFrame(document.getElementById("Appname"));
    


}
// //生成提示框
// function createFrame(e) {
//     $(e).parent().addClass("textAreaDivParent");
//     $(e).after("<div class = 'textAreaDiv' hidden='hidden'><div class='divArrow'></div><ul class='divText'></ul></div>");
// }

// //绑定显示提示框类到input上
// function susFrame(e) {

//     $(e).addClass("displayPro");

// }
// //清除input上的显示提示框类
// function clearFrame(e) {

//     $(e).removeClass("displayPro");

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

//重置DISABLED状态
function resetDisabled() {
    $(".set-button").attr("disabled", "disabled").removeClass("add-panel-form-button").addClass("add-panel-form-disabled-button");
    $(".set-button").parent().prev().find("input[type='text']").attr("disabled", "disabled");
}

function select_app(val,id){
    // console.log(val);
     var service_or_app = val;
     if(service_or_app == "app"){
     var sending_data = {
        ACTION:  "select_app",
        service_or_app:val
    }
    function ondatareceived(data) {
        // console.log(data);
        if(data == 0){
            $("#Appname,#Appid_btn").hide();
             $("#service_app").parent().append("<span>&nbsp&nbsp&nbsp应用暂未启用</span>");
        }
        else{
            $("#Appname,#Appid_btn").show();
            $("#service_app").next("span").hide();
        }
        
    }

    do_request(sending_data, ondatareceived);
}
else{
    $("#service_app").next("span").hide();
}
}