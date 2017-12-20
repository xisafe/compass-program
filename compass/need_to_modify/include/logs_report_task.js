$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    
    /* 渲染面板 */
    add_panel.render();
    list_panel.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.hide();
    
    list_panel.update_info(true);
});
var list_panel;
var add_panel;
var add_panel_config = {
    url: "/cgi-bin/logs_report_task.cgi",
    check_in_id: "panel_notice_add",
    panel_name: "add_panel",
    rule_title: "报表",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
     
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "报表名称*",
        sub_items: [
            {
                enable: true,
                type: "text",
                id: "report_name",
                name: "report_name",
                value: "",
                functions: {
                },
                check: {
                    type: "text",
                    required: 1,
                    check:'note',
                    // other_reg:'!/^\$/',
                    ass_check:function(eve){
                        var msg="";
                        var viewsize = document.getElementsByName("report_name")[0].value;
                        if (viewsize.length > 40) {
                        msg = "请输入1-40字符";
                        }
                        return msg;
                    }
                }
            }
        ]
    },
    {
        title: "提交人*",
        sub_items: [
            {
                enable: true,
                type: "text",
                id: "submitter",
                name: "submitter",
                value: "",
                functions: {
                    
                },
                check: {
                    type: "text",
                    required: 1,
                    check:'note',
                    // other_reg:'/\w\W/',
                    ass_check:function(eve){
                        var msg="";
                        var viewsize = document.getElementsByName("submitter")[0].value;
                        if (viewsize.length > 40) {
                        msg = "请输入1-40字符";
                        }
                        return msg;
                    }
                }
            }
        ]
    },
    {
        title: "提交单位*",
        sub_items: [
            {
                enable: true,
                type: "text",
                id: "submit_institution",
                name: "submit_institution",
                value: "",
                functions: {
                    
                },
                check: {
                    type: "text",
                    required: 1,
                    check:'note',
                    // other_reg:'/\w\W/',
                    ass_check:function(eve){
                        var msg="";
                        var viewsize = document.getElementsByName("submit_institution")[0].value;
                        if (viewsize.length > 80) {
                        msg = "请输入1-80个字符";
                        }
                        return msg;
                    }
                }
            }
        ]
    },
    {
        title: "TopN*",
        sub_items: [
            {
                enable: true,
                type: "text",
                id: "topN",
                name: "topN",
                value: "",
                functions: {
                    
                },
                check: {
                    type: "text",
                    required: 1,
                    check:'num',
                    // other_reg:'/\w\W/',
                    ass_check:function(eve){
                        var msg="";
                        var viewsize = document.getElementsByName("topN")[0].value;
                        if (viewsize<5 || viewsize > 100) {
                            msg = "请输入5-100的整数";
                        }
                        return msg;
                    }
                }
            }
        ]
    },
    {
        title: "报表模板",
        id: "report_template",
        sub_items: [
            {
                enable: true,
                type: "checkbox",
                label: "按入侵类型统计",
                name: "report_template",
                value: "attack_type",
            },
            {
                enable: true,
                type: "checkbox",
                label: "按源地址统计",
                name: "report_template",
                value: "sourceip"
            },
            {
                enable: true,
                type: "checkbox",
                name: "report_template",
                label: "按目标统计",
                value: "dip"
            },
            {
                enable: true,
                type: "checkbox",
                name: "report_template",
                label: "事件级别",
                value: "danger_level"
            },
            {
                enable: true,
                type: "checkbox",
                label: "影响服务",
                name: "report_template",
                value: "affect_service"
            },
            {
                enable: true,
                type: "checkbox",
                name: "report_template",
                label: "响应方式",
                value: "action"
            }
        ]
    },
    {
        title: "时间周期",
        id: "time_period",
        sub_items: [
            {
                enable: true,
                type: "radio",
                name: "time_period",
                label: "今天",
                value: "today",
                checked: "checked"
            },
            {
                enable: true,
                type: "radio",
                name: "time_period",
                value: "lastweek",
                label: "最近一周"
            },
            {
                enable: true,
                type: "radio",
                name: "time_period",
                value: "lastmonth",
                label: "最近一个月"
            },
            {
                enable: true,
                type: "radio",
                name: "time_period",
                value: "lastthreemonths",
                label: "最近三个月"
            },
            {
                enable: true,
                type: "radio",
                name: "time_period",
                value: "lasthalfyear",
                label: "最近半年"
            },
            {
                enable: true,
                type: "radio",
                name: "time_period",
                value: "lastyear",
                label: "最近一年"
            }
        ]
    },
    {
        title: "生成格式",
        sub_items: [
            {
                enable: true,
                type: "checkbox",
                id: "produce_format",
                name: "produce_format",
                label: "EXCEL",
                checked: "checked",
                value: "xls",
                functions: {
                    
                },
                check: {
                    type: "text",
                    required: 1,
                    check:'note',
                    ass_check:function(eve){
            
                    }
                }
            }
        ]
    },
    ]
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
    }
    
};

var list_panel_config = {
    url: "/cgi-bin/logs_report_task.cgi", /* ***必填***，控制数据在哪里加载 */
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
    },{
        "enable": false,
        "type": "radio",
        "name": "radio",
        "column_cls": "rule-listbc",
        "width": "5%"
    },{
        "enable": true,
        "type": "text",
        "title": "报表名称*",        //一般text类型需要title,不然列表没有标题
        "name": "report_name",
        "width": "18%",
        "td_class":"align-center"
    },{
        "enable": true,
        "type": "text",
        "title": "提交人*",
        "name": "submitter",
        "width": "18%",
        "td_class":"align-center"
    },{
        "enable": true,
        "type": "text",
        "title": "提交单位*",
        "name": "submit_institution",
        "width": "18%",
        "td_class":"align-center"
    },{
        "enable": true,
        "type": "text",
        "title": "创建时间",
        "name": "create_time",
        "width": "18%",
        "td_class":"align-center"
    }, {
        "enable": true,
        "type": "action",
        "title": "活动/动作",
        "name": "action",
        "width": "18%",
        "td_class":"align-center"
    }],
    top_widgets: [{
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
        "button_icon": "delete.png",
        "button_text": "删除选中",
        "functions": {
            onclick: "delete_selected_items(this)"
        }
    }],
    is_default_search: true           /* ===可选===，默认是true，控制默认的搜索条件 */
    
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
function openWindow(str,title){
    OpenWindow=window.open("错误页面预览", "newwin", "height=500, width=1000,top=200, left= 310,toolbar=no ,scrollbars="+scroll+",menubar=no"); 
　　//写成一行 
　　OpenWindow.document.title = title + ' - 实时预览';

　　// OpenWindow.document.write('<h1 style="text-align: center;">'+title+'</h1>'); 
　　OpenWindow.document.write(str); 
　　// OpenWindow.document.write('<p style="padding: 0px 13%;">'+str+'</p>'); 

　　// OpenWindow.document.write("</BODY>") 
　　// OpenWindow.document.write("</HTML>") 
　　OpenWindow.document.close() 
}
