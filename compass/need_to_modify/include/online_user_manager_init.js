$(document).ready(function(){
    paging_holder = new PagingHolder( list_panel_config );
    paging_holder.render();
    paging_holder.update_info(true);
});

var list_panel_render = {
    'stay_online': {
        render: function( default_rendered_text, data_item ) {
            var str_timenow = getNowFormatDate();
            var str_timeold = data_item.time_online;
            var result_render = DiffLong(str_timenow,str_timeold);
            return '<span>' + result_render + '</span>';
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
        var action_buttons = [{
            "enable": true,
            "id": "delete_item",
            "name": "delete_item",
            "button_icon": "delete.png",
            "button_text": "强制下线(10分钟内禁止登陆)",
            "value": data_item.ip,
            "functions": {
                onclick: "offline_user(this.value);"
            },
            "class":"action-image"
        }];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/online_user_manager.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_online",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 15,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    panel_title: "在线用户管理",
    is_panel_closable: false,
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [{
        "enable": false,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",
        "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "5%"
    }, {
        "enable": false,
        "type": "radio",
        "name": "radio",
        "column_cls": "rule-listbc",
        "width": "5%"
    }, {
        "enable": true,
        "type": "text",
        "title": "序号",        //一般text类型需要title,不然列表没有标题
        "name": "sequence",
        "width": "5%",
        "td_class":"align-center"
    }, {
        "enable": true,
        "type": "text",
        "title": "用户名",
        "name": "username",
        "width": "15%"
    }, {
        "enable": true,
        "type": "text",
        "title": "登陆信息",
        "name": "ip",
        "width": "25%"
    }, {
        "enable": true,
        "type": "text",
        "title": "上线时间",
        "name": "time_online",
        "width": "20%"
    }, {
        "enable": true,
        "type": "text",
        "title": "在线时长",
        "name": "stay_online",
        "width": "15%"
    }, /* {
        "enable": true,
        "type": "text",
        "title": "状态",
        "name": "state",
        "width": "15%"
    },  */{
        "enable": true,
        "type": "action",
        "title": "操作",
        "name": "action",
        "width": "10%",
        "td_class":"align-center"
    }],
    top_buttons: [{
        "enable": false,             // ==可选==，如果为不填或者为false,就不显示
        "id": "enable_selected",    // ==可选==，按钮的ID
        "name": "enable_selected",  // ==可选==，按钮的名字
        "button_icon": "on.png",    // ==可选==，操作按钮的图标，如果没有设置，就没有图标
        "button_text": "启用选中",  // **必填**，操作按钮的文字，这个必须设置,建议在五个字以内
        "functions": {              // ==可选==，回调函数，没有的话就只是一个按钮，什么也不做
            onclick: "test_test_test(this)"
        }
    }, {
        "enable": false,
        "id": "disable_selected",
        "name": "disable_selected",
        "button_icon": "off.png",
        "button_text": "禁用选中",
        "functions": {
            onclick: "disable_selected_items(this)"
        }
    }],
    bottom_buttons: [{
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
    is_default_search: false,          /* ===可选===，默认是true，控制默认的搜索条件 */
    extend_search: [{
        "enable": true,         // ==可选==，如果为不填或者为false,就不显示
        "type": "select",         // ==可选==，默认为text类型
        "id": "condition",     // ==可选==，控件ID
        "name": "condition",   // **必填**，控件的名字
        "title": "查询条件",    // **必填**，输入控件前面的提示信息，没有会导致用户迷糊
        "options": [{
            "value":"username",
            "text":"用户名"
        },
        {   "value":"ip",
            "text":"IP"
        }]
    }, {
        "enable": true,
        "type": "text",
        "id": "username_or_ip",
        "name": "username_or_ip",
        "title": "",
        "check":{
            type: "text",
            required: 0,
            check:'other',
            other_reg:'!/^\$/',
            ass_check: function( check ) {
                var condition = $("#condition").val();
                var val_check = $("#username_or_ip").val();
                var mesg = "";
                if(condition == "ip"){
                    if(!check.validip(val_check) && val_check != ""){
                        mesg = "请输入IP地址";
                    }
                }
                return mesg;
            }
        }
    },{
        "enable": true,
        "type": "image_button",
        "id": "begin_search",
        "name": "begin_search",
        // "button_icon": "search16x16.png",
        "button_text": "查找",
        "cls": "my_search_button",
        "functions": {
            onclick: "extend_search_function(this);"
        }
    }]
}

var paging_holder;

function enable_selected_items() {
    var checked_items = paging_holder.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    paging_holder.enable_item( ids );
}

function disable_selected_items() {
    var checked_items = paging_holder.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    paging_holder.disable_item( ids );
}

function delete_selected_items(e) {
    var ids = "";
    if(e.id == "delete_selected"){
        var checked_items = paging_holder.get_checked_items();
        var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].id );
        }
        ids = checked_items_id.join( "&" );
    }else{
        ids = e.value;
    }
    
    paging_holder.delete_item( ids );
}

function extend_search_function( element ) {
    paging_holder.update_info( true );
}

function DiffLong(datestr1, datestr2) {

    var date1 = new Date(Date.parse(datestr1.replace(/-/g, "/")));
    var date2 = new Date(Date.parse(datestr2.replace(/-/g, "/")));
    var datetimeTemp;
    var isLater = true;

    if (date1.getTime() > date2.getTime()) {
        isLater = false;
        datetimeTemp = date1;
        date1 = date2;
        date2 = datetimeTemp;
    }

    var difference = date2.getTime() - date1.getTime();
    var thisdays = Math.floor(difference / (1000 * 60 * 60 * 24));

    difference = difference - thisdays * (1000 * 60 * 60 * 24);
    var thishours = Math.floor(difference / (1000 * 60 * 60));
    
    difference = difference - thishours * (1000 * 60 * 60);
    var thisminutes = Math.floor(difference / (1000 * 60));
    
    difference = difference - thisminutes * (1000 * 60);
    var thisseconds = Math.floor(difference / 1000);


    var strRet = thisdays + '天' + thishours + '小时' + thisminutes + '分' + thisseconds + '秒';

    return strRet;
}
function getNowFormatDate() {
 
    var date = new Date();
    var seperator1 = '-';
    var seperator2 = ':';
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    if (month >= 1 && month <= 9){
        month = '0' + month;
    }
    if (strDate >= 0 && strDate <= 9){
        strDate = '0' +strDate;
    }
    var currentdate = date.getFullYear() + seperator1 +month + seperator1 + strDate
            + ' ' +date.getHours() + seperator2 + date.getMinutes()
            +seperator2 + date.getSeconds();
    return currentdate;
} 
//强制用户下线
function offline_user(u){
    var sending_data = {
        ACTION: 'offline',
        username: u
    };
    function ondatareceived(data) {
        //var data_content = JSON.parse(data);
        paging_holder.update_info(true);
    }
    do_request(sending_data, ondatareceived);
}
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/online_user_manager.cgi",
        data: sending_data,
        async: false,
        error: function(request){
            alert("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
