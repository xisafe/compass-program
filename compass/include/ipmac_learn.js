var layer_flag;
var message_box_config = {
    url: "/cgi-bin/ipmac_learn.cgi",
    check_in_id: "mesg_box_id"
    
}

var learn_method_panel_config = {
    url: "/cgi-bin/ipmac_learn.cgi",
    check_in_id: "learn_method_panel_config",
    panel_name: "learn_method_panel",
    rule_title_adding_icon: "applications-blue.png",
    rule_title_adding_prefix: "选择",
    rule_title: "学习方式",        //显示在页面上的就是 添加IP/MAC绑定了
    button_adding_text: "学习",
    is_panel_closable: true,
    is_panel_stretchable: false,    //原来一直是false 改成true就能拖动了
    is_modal: false,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_cancel_edit:function(add_obj){

        },
        after_cancel_edit:function(add_obj){
        },
        before_save_data:function( add_obj, sending_data ){
            RestartService("正在启动学习...");

            start_learning();
            return false;   // must禁止掉由框架add_panel.js默认实现的提交数据，id:null,LEARN_METHOD:by_switchboard,ACTION:save_data,panel_name:learn_method_panel
        },
        after_save_data:function( add_obj, received_data ){
            /*if ( response.running == 1 ) {
                window.setTimeout( timing_check_running, check_interval );
            }*/
        }
    },
    items_list: [{
        title: "学习方式",
        sub_items:[{    
            enable:true,
            type: "items_group",
            // name: "merge_way",
            id: "learn_method_id",
            sub_items: [{
                enable: true,
                type: "radio",
                id: "sb_method_id",
                name: "LEARN_METHOD",
                value: "by_switchboard",
                label: "从三层交换机学习",
                // checked:true,
                functions: {
                    onclick: "save_learn_method();"
                }
            }, {
                enable: true,
                type: "radio",
                id: "baowen_method_id",
                name: "LEARN_METHOD",
                value: "by_baowen",
                label: "从报文中学习",
                functions: {
                    onclick: "save_learn_method();"
                }
            }]      //sub_items结束
        }]
    }]
};

var learn_result_list_panel_config = {
    url: "/cgi-bin/ipmac_learn.cgi",
    check_in_id: "learn_result_list_panel_config",
    panel_name: "learn_result_list_panel",
    page_size: 10,    // 只让它显示10行
    event_handler: {
        before_load_data: function( add_obj, data_item ) {
        },
        after_load_data: function ( add_obj, data_item ) {
            layer_flag = data_item.layer_flag;
        },
        before_save_data: function ( add_obj, sending_data ) {
        },
        after_save_data: function ( add_obj, received_data ) {
        }
    },
    panel_header: [{
        enable: true,
        type: "checkbox",
        name: "checkbox",
        width: "5%"
    }, {
        enable: true,
        type: "text",
        title: "IP地址",
        name: "ip_addr",
        width: "35%"
    }, {
        enable: true,
        type: "text",
        title: "MAC地址",
        name: "mac_addr",
        width: "35%"
    }, {
        enable: true,
        type: "text",
        title: "来源",
         name: "source",
        width: "25%"
    }],
    top_widgets: [/*{
        enable: true,
        type: "image_button",
        button_icon: "search16x16.png",
        button_text: "查看学习结果",
        style: "width:100px;height:30px;",
        functions: {
            // onclick: "learn_result_list_panel.update_info(true);"  注：此句也完全正确
            onclick: "load_learn_results();"
        }
    },*/
    {
        enable: true,
        type: "image_button",
        id: "synchronize_button_id_for_learn_result_list_panel",
        // button_icon: "search16x16.png",
        button_text: "同步勾选数据到IP/MAC绑定列表",
        style: "width:250px;height:30px;",
        functions: {
            onclick: "synchronize_selected_items(this);"
        }
    }, {
        enable: true,
        type: "image_button",
        id: "synchronize_all_button_id_for_learn_result_list_panel",
        // button_icon: "search16x16.png",
        button_text: "一键同步所有数据到IP/MAC绑定列表",
        style: "width:250px;height:30px;",
        functions: {
            onclick: "synchronize_all_selected_items(this);"
        }
    }]
};

var choose_learn_method_panel  = new RuleAddPanel( learn_method_panel_config );
var learn_result_list_panel = new PagingHolder( learn_result_list_panel_config );
var message_manager = new MessageManager( message_box_config );
var check_interval = 500;

$( document ).ready(function() {
    choose_learn_method_panel.render();
    learn_result_list_panel.render();
    message_manager.render();

    learn_result_list_panel.set_ass_add_panel( choose_learn_method_panel );
    choose_learn_method_panel.set_ass_list_panel( learn_result_list_panel );

    learn_result_list_panel.set_ass_message_manager( message_manager );
    choose_learn_method_panel.set_ass_message_manager( message_manager );

    load_init_data();
    //learn_result_list_panel.update_info(true);

    $(".search").remove();
    $(".add-panel-close-button").remove();
    $("#add_panel_cancel_button_id_for_learn_method_panel").remove();
    
});

function save_learn_method(){
    var method = $("#baowen_method_id").attr("checked")?"two":"three";
    var sending_data = "ACTION=save_method&METHOD="+method;
    function onreceived(response){
        
    }
    send_ajax( sending_data, onreceived );
}

function load_init_data(){
    var sending_data = {
        ACTION: "load_init_data"
    };
    function onreceived(response){
        var status = response.status;   // status变量对应的其实是后台'LAYER'的值哦
        var bind = response.bind;
        if( bind == "on" ){
            $("#add_panel_add_button_id_for_learn_method_panel").css("color","black").attr("disabled", false);
            $("#synchronize_button_id_for_learn_result_list_panel,#synchronize_all_button_id_for_learn_result_list_panel").attr("disabled", false);

        }else{
            $("#add_panel_add_button_id_for_learn_method_panel").css("color","#808080").attr("disabled", true);
            $("#synchronize_button_id_for_learn_result_list_panel,#synchronize_all_button_id_for_learn_result_list_panel").attr("disabled", true);
        }
        if( status == "none" ){
            $("#sb_method_id").attr("checked", false);
            $("#baowen_method_id").attr("checked", false);
        }
        else if( status == "three" ){
            $("#sb_method_id").attr("checked", true);
        }
        else if( status == "two" ){
            $("#baowen_method_id").attr("checked", true);
        }

        if( response.running == 1 ) {
            RestartService("正在学习中...");
            window.setTimeout( timing_check_running, check_interval );
        }else{
            load_learn_results();  // 如果一开始后台并没有在学习中那么就要加载学习列表了
        }
    }
    send_ajax( sending_data, onreceived );
}



function synchronize_selected_items( element ) {   //这个按钮是顶部的那个‘删除选中’的处理函数
    var checked_items = learn_result_list_panel.get_checked_items();
    var checked_items_id = new Array();
    var detail_data_array = new Array();
    var data_str="";

    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
        // var data_item = checked_items[i];  这句话也是对的，因为data_item其实就是数组checked_items中下标为i的对象元素
        var data_item = learn_result_list_panel.get_item( checked_items[i].id );
        data_str += "on," + data_item['ip_addr'] +","+ data_item['mac_addr'] +","+ data_item['source']+","+"\n";
        // detail_data_array.push(data_item);
    }
    var ids = checked_items_id.join( '|' );  //千万不要用&来分隔，因为你不同属性之间就是用&分隔的，这样会导致歧义即id=6&7，那么7会被解析成下一个属性的属性名
    if( ids == ""){
        learn_result_list_panel.show_error_mesg( "未检测到选中项" );
        return;
    }
    var sending_data = {
        ACTION: "SYNCHRONIZE",
        id: ids,
        detail_data: data_str,
        layer_flag:layer_flag
    };
    function ondatareceived( data ) {
        message_manager.show_note_mesg(data.mesg);  // 显示‘同步成功或失败’的消息
        selected_all_items(learn_result_list_panel,false); //恢复页面之前的状态
    }
    send_ajax( sending_data, ondatareceived );
}
function selected_all_items(panel,is_checked){ /*is_checked 是否选中*/
    
    var data_items = panel.get_all_items();
   panel.detail_data = $.map(data_items,function(v,i){
        v.checked = is_checked;
        return v
    });
   $("#control_checkbox_for_"+panel.panel_name).attr("checked",is_checked);
   panel.load_data_into_main_body();
}

function synchronize_all_selected_items(){
   selected_all_items(learn_result_list_panel,true);
   synchronize_selected_items();
}
function send_ajax(sending_data, ondatareceived){
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/ipmac_learn.cgi",
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            learn_result_list_panel.show_error_mesg("返回数据格式有误,请检查");
        },
        success: ondatareceived
    });
}

function start_learning(){
    var url = "/cgi-bin/ipmac_learn.cgi";
    var sending_data = $( "#add_panel_body_form_id_for_learn_method_panel" ).serialize();   //表单中的数据有id属性和LEARN_METHOD属性
    sending_data = sending_data + "&ACTION=START_LEARNING";

    function ondatareceived( response ) {
        if ( response.running == 1 ) {
            window.setTimeout( timing_check_running, check_interval );
        } else {  // response.running == -1
            // endmsg("学习完毕");
            if ( response.status == 0 ) {
                learn_result_list_panel.show_note_mesg( response.mesg );
            } else {
                learn_result_list_panel.show_error_mesg( response.mesg );
            }
        }
    }
    send_ajax( sending_data, ondatareceived );
}


function timing_check_running() {
    var sending_data = {
        ACTION: "check_running"
    }
    function ondatareceived( response ) {
        if ( response.running == 1 ) {
            window.setTimeout( timing_check_running, check_interval );
        } else {
            endmsg("学习完毕");
            load_learn_results();
        }
    }
    send_ajax( sending_data, ondatareceived );
}


function load_learn_results(){
    var method = $("#baowen_method_id").attr("checked")?"by_baowen":"by_switchboard";
    learn_result_list_panel.extend_sending_data['LEARN_METHOD'] = method;
    learn_result_list_panel.update_info(true);   // 这个接口里发送的数据是ACTION=load_data
}

/*function load_learn_results(){
    var sending_data = $( "#add_panel_body_form_id_for_learn_method_panel" ).serialize();   //表单中的数据有id属性和LEARN_METHOD属性
    sending_data = sending_data + "&ACTION=VIEW_THE_RESULTS";
    function my_ondatareceived( data ) {
        // 第二步,更新paging_holder的数据
        // 第三步,更新页面主体的数据
        // 第四步,更新翻页工具的数据
        // 第五步,给页面上的控制按钮注册监听
    }
    send_ajax( sending_data, my_ondatareceived );
}*/


