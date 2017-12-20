$(document).ready(function(){
    lib_panel = new PagingHolder( lib_panel_config );
    obj_panel = new PagingHolder( obj_panel_config );
    
    /* 渲染面板 */
    lib_panel.render();
    obj_panel.render();
    
    lib_panel.hide();
    obj_panel.hide();
    
    lib_panel.update_info(true);
    obj_panel.update_info(true);
    // init_data();

    check._main(object);

    check_running();
    // check_engine();
});

//配置表单检测
var check = new ChinArk_forms();
var object = {
   'form_name':'ENGINE_CONFIG_FORM',
   'option':{
        'rule_lib':{
            'type':'text',
            'required':'1',
            'check':'other',
            'other_reg':'!/^\$/',
            'ass_check':function(eve){
                
            }
        },
        'net_obj':{
            'type':'text',
            'required':'1',
            'check':'other',
            'other_reg':'!/^\$/',
            'ass_check':function(eve){
                
            }
        }
    }
}

var lib_panel;
var obj_panel;
var cache_arr={};
var lib_panel_render = {
    /* 'protocol': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "RIP";
            return '<span>' + result_render + '</span>';
        }
    } */
};

var lib_panel_config = {
    url: "/cgi-bin/idps_engine_config.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_rule_lib",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 10,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "lib_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    panel_title: "选择特征库",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 10
    },
    render: lib_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [{
        "enable": true,            //用户控制表头是否显示
        "type": "radio",           //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "radio",         //用户装载数据之用
        "column_cls": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "10%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
        "functions": {              //一般只有checkbox才会有这个字段
        }
    }, {
        "enable": false,
        "type": "radio",
        "name": "radio",
        "column_cls": "rule-listbc",
        "width": "5%"
    }, {
        "enable": true,
        "type": "text",
        "title": "名称",        //一般text类型需要title,不然列表没有标题
        "name": "name",
        "width": "40%"
    }, {
        "enable": true,
        "type": "text",
        "title": "说明",
        "name": "description",
        "width": "50%"
    }],
    bottom_extend_widgets: {
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_lib_data();"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "lib_panel.hide();"
            }
        }]
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
                        
        },
        after_load_data: function( list_obj,data_item ) {
            cache_arr.rule_lib = data_item;
            // init_data();

        }
    }
}
//内网检测对象选择面板
var obj_panel_render = {
    /* 'protocol': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "RIP";
            return '<span>' + result_render + '</span>';
        }
    } */
};


var obj_panel_config = {
    url: "/cgi-bin/idps_engine_config.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_net_obj",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 10,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "obj_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    panel_title: "选择IP组",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 10
    },
    render: obj_panel_render,      /* ===可选===，渲染每列数据 */
    panel_header: [{
        "enable": true,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //用户装载数据之用
        "td_class": "align-center",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
        "functions": {              //一般只有checkbox才会有这个字段
        }
    }, {
        "enable": false,
        "type": "radio",
        "name": "radio",
        "column_cls": "rule-listbc",
        "width": "5%"
    }, {
        "enable": true,
        "type": "text",
        "title": "名称",        //一般text类型需要title,不然列表没有标题
        "name": "name",
        "width": "40%"
    }, {
        "enable": false,
        "type": "text",
        "title": "说明",
        "name": "description",
        "width": "50%"
    }],
    bottom_extend_widgets: {
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_obj_data();"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "obj_panel.hide();"
            }
        }]
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
                        
        },
        after_load_data: function( list_obj,data_item ) {
            cache_arr.net_obj = data_item;
            init_data();

        }
    },
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

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/idps_engine_config.cgi",
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            alert("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//初始化加载数据
function init_data(){
    var sending_data = {
        ACTION: 'init_data'
    };
    function ondatareceived(data) {
        console.log(data);
        $("#rule_lib").val(data.rule_lib);
        $("#net_obj").val(data.net_obj);
        if(data.enabled_engine == "on"){
            $("#enabled_engine").attr('checked',true);
        }
        if(data.enabled_log == "on"){
            $("#enabled_log").attr('checked',true);
        }
        if(data.rule_lib){
            grepIndexInListPanel(data.rule_lib,"name",cache_arr.rule_lib.detail_data,lib_panel);
        }if(data.net_obj){
            grepIndexInListPanel(data.net_obj,"name",cache_arr.net_obj.detail_data,obj_panel);
        }
    }
    do_request(sending_data, ondatareceived);
}
//查找listPanel指定关键字的行保持选中
function grepIndexInListPanel(name,key,detailData,panelName){
    for(var i = 0; i < detailData.length; i++){
        if(name == detailData[i][key]){
            panelName.set_check(i,"checked");
            panelName.update_info();
            break;
        }
    }
   
}
//将特征库数据写入配置输入框
function write_lib_data(){
    var checked_items = lib_panel.get_checked_items();
    $("#rule_lib").val(checked_items[0].name);
    lib_panel.hide();
}
//将内网检测对象数据写入配置输入框
function write_obj_data(){
    var checked_items = obj_panel.get_checked_items();
    var arr_obj = new Array();
    for(var i=0;i<checked_items.length;i++){
        arr_obj.push(checked_items[i].name);
    }
    var str_obj = arr_obj.join("&");
    $("#net_obj").val(str_obj);
    obj_panel.hide();
}
//检查启用引擎是否可用
// function check_engine(){
//     var sending_data = {
//         ACTION: 'judge_engine'
//     };
//     function ondatareceived(data) {
//         if(data.status == "1"){
//             $("#enabled_engine").attr("disabled",true);
//             $("#enabled_engine").attr("checked",false);
//             $("#label_tip").html("（IPS特征库未激活，该功能无法使用。请先激活！）");
//         }else if(data.status == "2"){
//             $("#enabled_engine").attr("disabled",true);
//             $("#enabled_engine").attr("checked",false);
//             $("#label_tip").html("（IPS特征库未激活，该功能无法使用。请先激活！）");
//         }
//     }
//     lib_panel.request_for_json( sending_data, ondatareceived );
// }
// 
// 
function obj_panel_show(panel,id){
        //修改部分
    // panel.update_info(true);
    var text_val = $('#'+id).val();
    if (text_val != '') {
        var text_arr = /\&/.test(text_val) ? text_val.split('&') : text_val.split('，');
        text_arr = text_arr.map(function(ele, index) {
            return ele.trim();
        });
        $('#'+panel.panel_body_id+' tr').each(function(index, el) {
        if ($.inArray($(this).children('td').eq(1).text(),text_arr) != -1) {
            $(this).children('td').eq(0).children('input').attr('checked',true);
            if ($(this).children('td').eq(1).text() == 'any') {
                $(this).siblings().each(function(index, el) {
                    $(this).children('td').eq(0).children('input').attr('disabled',true);  
                })
            }
            for (var i = 0; i < panel.detail_data.length; i++) {
                    panel.detail_data[index].checked = true;
                }
            } 
        });
    }
    panel.show();
}