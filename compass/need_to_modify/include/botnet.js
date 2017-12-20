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

$( document ).ready(function() {

    /* 渲染面板 */
    message_manager.render();
    list_panel.render();
    list_panel.set_ass_message_manager( message_manager );
    /* 设置面板关联 */
    list_panel.update_info( true );

	$("#search_key_for_list_panel").css("font-size","5px");
    $("#search_key_for_list_panel").attr("placeholder","支持规则名称查询");


});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/botnet.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box"          /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}
var list_panel_render = {
    action: {
        render: function(a, b) {
            var id     = b["event_id"],
                enable = b["state"],
                status = b["strategy"];
            var button_text, button_icon, onclick, statusIcon, statusOnclick, statusText;
            if( enable == "off"){
                button_icon = "off.png";
                button_text = "启用";
                onclick = function() {
                    change_status('on','',b.event_id);
                }
            }
            else{
                button_icon = "on.png";
                button_text = "禁用";
                onclick = function() {
                    change_status('off','',b.event_id);
                }
            }
            if( status == "drop") {
                statusIcon = "drop.png";
                statusText = "检测";
                statusOnclick = function() {
                    change_status('','alert',b.event_id);
                }
            }
            else {
                statusIcon = "alert.png";
                statusText = "阻断";
                statusOnclick = function() {
                    change_status('','drop',b.event_id);
                }
            }
            var toggle_enable_button = {
                enable: true,
                button_icon: button_icon,
                button_text: button_text,
                style: "margin-right: 15px;",
                onFunc: onclick
            };
            var toggle_status_button = {
                enable: true,
                button_icon: statusIcon,
                button_text: statusText,
                onFunc: statusOnclick

            };
            var toggle_enable_button = PagingHolder.create_action_buttons( [toggle_enable_button,toggle_status_button] );
            return toggle_enable_button;
        }
    }
}

var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 20,
    render: list_panel_render,
    seFlag: true,
    event_handler: {
        before_load_data: function( list_obj, sending_data ) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 时，系统向服务器重新加载数据之前调用此函数
             *
             * 参数： -- list_obj      ==可选==，列表面板实例
             * 返回：无
             */
        },
        after_load_data: function ( list_obj, response ) {
          
            if(list_panel_config.seFlag) {
                forSelect(response["type_list"]);
                list_panel_config.seFlag = false;
            }
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 后，并且服务器响应后调用此函数
             *
                                    
             * 参数： -- add_obj    ==可选==，添加面板实例，用户可以通过add_obj.show_
             *        -- response   ==可选==, 服务器响应的数据
             * 返回：无
             */
        }
    },
    panel_header: [{            /* ***必填***，控制数据的加载以及表头显示 */
        enable: true,           /* ==可选==，作用于整列，如果为不填或者为false，那么定义的这一列都不会显示 */
        type: "checkbox",       /* ==可选==，作用于整列，type目前有checkbox/text/radio/action，分别对应不同类型的表头，
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
        title: "",              /* =*可选*=，作用于标题头单元格，不同type，title需要的情况不同，
                                                一般type为text需要文字title，提示这一列数据表示什么意义，不填不显示标题
                                                当type为checkbox时，会默认渲染‘全选checkbox框’，填了title也将不起作用，
                                            当type为radio类型时，title变为‘请选择’，填了title也不起作用，当type为action时，
                                            默认标题是“活动/动作”，如果在action配置项填了title属性，会覆盖默认标题，示例见
                                            下文
                                 */
        name: "checkbox",       /* **必填**，作用于整列，控制整列要显示的数据项
                                                ****当type为checkbox、radio、action之一时，name也必须对应为三项中的一项
                                                如果要渲染每列数据，到“配置对象”（注释<1>）的render属性中去配置与当前name值
                                            一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                            第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                 */
        cls: "",                /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
        column_cls: "",         /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                             当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                             在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                 */
        width: "5%",            /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                             以精确控制你想要的宽度
                                 */
        functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            // onclick: "alert(this.value);"
        }
    }, {
        enable: true,
        type: "text",
        title: "规则ID号",
        name: "event_id",
        td_class: "align-center",
        width: "10%"
        
    }, {
        enable: true,
        type: "text",
        title: "规则名称",
        name: "name",
        width: "56%"
    }, {
        enable: true,
        type: "text",
        title: "类型",
        name: "family",
        width: "12%",
        td_class: "align-center"
    }, {
        enable: true,
        type: "text",
        title: "危险等级",
        name: "danger",
        width: "7%",
        td_class: "align-center"
    }, {
        enable: true,
        type: "action",
        title: "操作",
        name: "action",
        width: "10%",
        td_class: "align-center"
    }],
    top_widgets: [                   /* ===可选=== */

        {
            enable: true,
            type: "image_button",
            id: "enable_selected",
            name: "enable_selected",
            class: "",
            button_icon: "on.png",
            button_text: "启用",
            functions: {
                onclick: "change_status('on','','');"
            }
        }, {
            enable: true,
            type: "image_button",
            id: "disable_selected",
            name: "disable_selected",
            class: "",
            button_icon: "off.png",
            button_text: "禁用",
            functions: {
                onclick: "change_status('off','','');"
            }
        }, {
            enable: true,
            type: "image_button",
            id: "alert_selected",
            name: "alert_selected",
            class: "",
            button_icon: "alert.png",
            button_text: "检测",
            functions: {
                onclick: "change_status('','alert','');"
            }
        }, {
            enable: true,
            type: "image_button",
            id: "drop_selected",
            name: "drop_selected",
            class: "",
            button_icon: "drop.png",
            button_text: "阻断",
            functions: {
                onclick: "change_status('','drop','');"
            }
        },{
            enable: true,
            type: "image_button",
            id: "alertAll",
            button_text: "全部检测",
            functions: {
                onclick: "change_status('','alert','ALL');"
            }
        },{
            enable: true,
            type: "image_button",
            id: "dropAll",
            button_text: "全部阻断",
            functions: {
                onclick: "change_status('','drop','ALL');"
            }
        }
    ],
    extend_search: [                /* ===可选===，定义额外的搜索筛选条件，位置在面板右上角，控件类似top_widgets中控件 */
        {
            enable: true,               /* ==可选==，如果为不填或者为false,就不显示*/
            type: "select",             /* ==可选==，默认为text类型 */
            id: "select_type",  /* ==可选==，控件ID */
            name: "type",/* **必填**，控件的名字 */
            title: "筛选",          /* **必填**，输入控件前面的提示信息，没有会导致用户迷糊 */
            class: "",                  /* ==可选==，控件本身样式的类名，会覆盖默认类的属性 */
            multiple: false,            /* ==可选==，select组件特有 */
            functions: {
                onchange: "$('#search_button_for_list_panel').click();",
            }
        } 
    ]
};

var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );

//启用禁用
function change_status(e1,e2,e3) {

    var check_items = list_panel.get_checked_items();

    var length = check_items.length;
    var str = "";
    if(e3 == ""){
        if(check_items.length == 0) {
            alert("请选择需要操作的规则");
            return;
        }
        for (var i = 0; i < length-1; i++ ) {
            str += check_items[i].event_id + "&";
        }
        str += check_items[length-1].event_id;
    }else if(e3 == "ALL") {
        var allData = list_panel.detail_data;
        var allIndex = new Array();
        for(var i = 0; i < allData.length; i++) {
            allIndex.push(allData[i].event_id);
        }
        str = allIndex.join("&");
    }else {
        str = e3;
    }
    
    var sending_data = {
        ACTION: "change_enable",
        enable_action: e1,
        action: e2,
        ruleIds: str
        
    };
    function ondatareceived(data) {
        message_manager.show_note_mesg(data.mesg);
        if (data.reload == 1) {
            message_manager.show_apply_mesg('规则已改变，需要重新应用以使规则生效');            
        }
        list_panel.update_info(true);
        // for_title();
    }
    do_request( sending_data,ondatareceived );
    
}


// function select_change(str) {
//     var enable = "",
//         status = "";
//     if(str == "on" || str == "off") {
//         enable = str;
//     }else if(str == "alert" || str == "drop") {
//         status = str;
//     }
//     c();
//     function c() {
//         var obj = new Object();
//         var arr = list_panel.get_checked_items();
//         obj["id"] = new Array();
//         obj["enable"] = new Array();
//         obj["status"] = new Array();
//         for(var key in arr) {
//             var a  = arr[key];
//             var id = a["event_id"]; 
//             var e  = enable || a["state"];
//             var s  = status || a["strategy"];
//             obj["id"].push(id);
//             obj["enable"].push(e);
//             obj["status"].push(s);

//         }
//         change_status(obj["id"].join("&"), obj["enable"].join("&"), obj["status"].join("&"));
//     }
    
// }
// function change_status(id, enable, status) {
//     var sending_data = {
//         ACTION: "change_status",
//         id: id,
//         enable: enable,
//         status: status
//     };
//     ondatareceived = function(data) {
//         if(data["status"]) {
//             message_manager.show_popup_error_mesg("操作失败！")
//         }else {
//             list_panel.update_info(true);
//         }
//     }
//     do_request(sending_data, ondatareceived);
// }
//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: ass_url,
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
function forSelect(data) {
    var par$ = $("#select_type");
    par$.empty();
    par$.append('<option value="0">所有</option>');
    for(var i = 0; i < data.length; i++) {
        par$.append('<option value="'+ data[i]["id"] + '">' + data[i]["name"] + '</option>');
    }
}