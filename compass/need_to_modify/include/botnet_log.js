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

	add_panel.render();
	add_panel.hide();  //初始化，将添加面板隐藏

    importLog_panel.render();
    importLog_panel.hide();

	/*将面板之间关联*/
	add_panel.set_ass_message_manager( message_manager );
	list_panel.set_ass_add_panel( add_panel );
    importLog_panel.set_ass_message_manager( message_manager )


    list_panel.set_ass_message_manager( message_manager );

    list_panel.update_info( true );
    import_panel_extendrender();
    page_turn();
    (function() {
        var img = $('<img title="重置" src="/images/reconnect.png">');
        img.css({
            cursor: "pointer",
            position: "relative"
        });
        img.on("click", function() {
            clear_add_panel_text();
        })
        $("#add_panel_id_for_add_panel .add-panel-title").find("span").css('float','left');
        $("#add_panel_id_for_add_panel .add-panel-title").find("span").after(img);
    })();

    $(".ctr_inpt").css("width","50px");
    $("#start_date").datepicker({   
        dateFormat:"yy-mm-dd",
        // changeMonth: true,
        yearSuffix: '年', 
        monthNames: ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
        dayNamesMin: ['日','一','二','三','四','五','六'],
        onClose: function( selectedDate ) {
        $( "#end_date" ).datepicker( "option", "minDate", selectedDate );
        
      }
    });
    $("#end_date").datepicker({
            dateFormat:"yy-mm-dd",
            // changeMonth: true,
            // changeYear: true,
            yearSuffix: '年', 
            monthNames: ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
            dayNamesMin: ['日','一','二','三','四','五','六'],
            onClose: function( selectedDate ) {
            $( "#start_data" ).datepicker( "option", "maxDate", selectedDate );
            
      }
    });

});

/*
 * 第一步，定义全局变量
 */
 var start_date = '';
 var start_time_hour = '';
 var start_time_minute = '';
 var end_date = '';
 var end_time_hour = '';
 var end_time_minute = '';

var ass_url = "/cgi-bin/botnet_log.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

var importLog_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "importLog_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "importLog_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "导入日志",
    rule_title_adding_prefix: "",
    rule_title_adding_icon:"uploadtray.png",
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 1             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons:{
        add:false,
        sub_items:[
            {
                enable: true,
                type: "hidden",
                name: "ACTION",
                value: "importLog",

            },
            {
                enable: true,
                type: "hidden",
                name: "importLog_panel",
                value: "",

            },
            {
                enable: true,
                type: "submit",
                style: "",
                id: "submit_for_log",
                functions: {
                    onclick:"importLog();"
                },

            }
        ],
        cancel: true,
    },
    event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function( add_obj, data_item ) {

        },
        after_load_data: function( add_obj, data_item ) {

        },
        before_cancel_edit: function( add_obj ) {

        },
        after_cancel_edit: function( add_obj ) {

        },
        before_save_data: function( add_obj, sending_data ) {

        },
        after_save_data: function( add_obj, received_data ) {

        }
    },
    items_list: [ 
            {
            title: "选择日志文件",
            sub_items: [
                {
                    enable: true,
                    type: "file",
                    id:"upload_file",
                    name: "upload_file",
                    functions: {
                        onclick: ""
                    },
                    style:"width:300px;height:25px;border-radius:4px"
                }
                
            ]
        }]
};

var add_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "查询条件",         /* ==*可选*==，默认是"规则" */
    rule_title_adding_prefix: "",
    button_adding_text:"查询",
    rule_title_adding_icon:"searchlog.png",
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons:{
        
        sub_items:[
            {
                enable:true,
                type:"hidden",
                name:"ACTION",
                value:"search"
            },
            {
                enable: true,
                type: "button",
                style: "",
                id: "search",
                name: "search",
                value: "筛选",
                functions: {
                    onclick:"searchItem(this);"
                },

            },
        ],
        cancel: true,
    },
    event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function( add_obj, data_item ) {
            
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
        after_load_data: function( add_obj, data_item ) {
            /*
             * ===可选事件函数===，在数据项往添加面板加载后，数据“已”装载入面板时调用
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *         -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
        },
        before_cancel_edit: function( add_obj ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
             *    在做这些默认的操作之“前”调用此函数
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *
             * 返回：无
             */
        },
        after_cancel_edit: function( add_obj ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
             *    在做这些默认的操作之“后”调用此函数
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *
             * 返回：无
             */
        },
        before_save_data: function( add_obj, sending_data ) {
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
        after_save_data: function( add_obj, received_data ) {
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
            title: "开始时间",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    style: "",
                    id: "start_date",
                    name: "start_date",
                    value: "",
                    readonly:"readonly",
                    functions: {
                    
                    },
                    class:"calendar"

                },
                {
                    enable: true,
                    type:"select",
                    style: "width:50px;",
                    id: "start_time_hour",
                    name: "start_time_hour",
                    options: select_options(24)
                    
                  
                },
                {
                    enable: true,
                    label:":",
                    type:"select",
                    style: "width:50px;",
                    id: "start_time_minute",
                    name: "start_time_minute",
                    options: select_options(60)
                
                  
                }
                
            ]
        },
        {
            title: "结束时间",
            sub_items: [
                {
                    enable: true,
                    type:"text",
                    style: "",
                    id: "end_date",
                    name: "end_date",
                    readonly:"readonly",
                    value: "",
                    class:"calendar"
                  
                  
                },
                {
                    enable: true,
                    type:"select",
                    style: "width:50px;",
                    id: "end_time_hour",
                    name: "end_time_hour",
                    options: select_options(24)
                    
                  
                },
                {
                    enable: true,
                    label:":",
                    type:"select",
                    style: "width:50px;",
                    id: "end_time_minute",
                    name: "end_time_minute",
                    options: select_options(60)
                   
                  
                }
                
            ]
        }, {
        title: "源IP",
        sub_items: [{
            enable: true,
            type: "text",
            id: "sourceIP",
            name: "sourceIP",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 0,
                check: 'ip|',
                ass_check: function( check ) {

                }
            }
        }]
    },
     {
            title: "源用户",
            sub_items: [{
                enable: true,
                type: "text",
                id: "sourceUser",
                name: "sourceUser",
                value: "",
                functions: {},
                style:"width:235px",
                check: {
                    type: "text",
                    required: 0,
                    check: 'name',
                    ass_check: function(eve) {
                       
                    }
                }
            }]
        },
    {
        title: "目标IP",
        sub_items: [{
            enable: true,
            type: "text",
            id: "destinationIP",
            name: "destinationIP",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 0,
                check: 'ip|',
                ass_check: function( check ) {

                }
            }
        }]
    },
    {
            title: "目标用户",
            sub_items: [{
                enable: true,
                type: "text",
                id: "destinationUser",
                name: "destinationUser",
                value: "",
                functions: {},
                style:"width:235px",
                check: {
                    type: "text",
                    required: 0,
                    check: 'name',
                    ass_check: function(eve) {
                       
                    }
                }
            }]
        }
    ]
};

var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 20,
    is_default_search: false, 
    render:{
        'virus_name':{
            render:function(default_rendered_text, data_item){
                 return '<span  onclick="show_suggestion(\'' + data_item.virus_name+'\',\''+data_item.file_name+ '\')">' + default_rendered_text + '<img src="/images/suggestion.png" class="suggestion-img" alt="点击查看建议" title="点击查看建议"/></span>';
            }
        },
        'sip': {
            render: function(default_rendered_text, data_item) {
                var rendered_text = default_rendered_text;

                if (data_item.src_user == "") {
                    rendered_text = '<span class="sip">' + default_rendered_text + '</span>';
                } else {
                    rendered_text = '<span class="sip">' + default_rendered_text + '</span>: ' + "(" + data_item.src_user + ")";
                }

                return rendered_text;
            }
        },
        'dip': {
            render: function(default_rendered_text, data_item) {
                var rendered_text = default_rendered_text;
                if (data_item.dst_user == "") {
                    rendered_text = '<span class="dip">' + default_rendered_text + '</span>';
                } else {
                    rendered_text = '<span class="dip">' + default_rendered_text + '</span>: ' + "(" + data_item.dst_user + ")";
                }
                return rendered_text;
            }
        }
    },
    event_handler: {
        before_load_data: function( list_obj ) {
            list_obj.extend_sending_data.time = $("#log_date_input_id").val();
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 时，系统向服务器重新加载数据之前调用此函数
             *
             * 参数： -- list_obj      ==可选==，列表面板实例
             * 返回：无
             */
        },
        after_load_data: function ( list_obj, response ) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 后，并且服务器响应后调用此函数
             *
                                    
             * 参数： -- add_obj    ==可选==，添加面板实例，用户可以通过add_obj.show_
             *        -- response   ==可选==, 服务器响应的数据
             * 返回：无
             */
        },
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            enable: true,
            type: "text",
            title: "时间",
            name: "datetime",
            width: "15%",
            td_class:"align-center"
        }, 
        {
            enable: true,
            type: "text",
            title: "事件名称",
            name: "event_name",
            width: "12%"
        },
        // {
        //     enable: true,
        //     type: "text",
        //     title: "事件ID",
        //     name: "event_id",
        //     width: "12%"
        // }, 
        {
            enable: true,
            type: "text",
            title: "事件类别",
            name: "event_type",
            width: "15%",
            td_class:"align-center"
        }, {
            enable: true,
            type: "text",
            title: "源",
            name: "sip",
            width: "17%"
        }, {
            enable: true,
            type: "text",
            title: "目标",
            name: "dip",
            width: "17%"
        }, {
            enable: true,
            type: "text",
            title: "协议",
            name: "protocol",
            width: "12%",
            td_class:"align-center"
        }, {
            enable: true,
            type: "text",
            title: "动作",
            name: "actionView",
            width: "7%",
            td_class:"align-center"

        }, {
            enable: true,
            type: "text",
            title: "结果",
            name: "result",
            width: "7%",
            td_class:"align-center"
        }
    ],
    top_widgets: [                          /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */

        {
            enable: true,
            type: "image_button",
            button_icon: "searchlog.png",
            button_text: "查询条件",
            functions: {
                onclick: "search(this);"
            }
        },{
            enable: true,
            type: "image_button",
            button_icon: "../images/download.png",
            button_text: "导入日志",
            functions: {
                onclick: "show_importLog(this);"
            }
        },{
            enable: true,
            id: "export_log",
            name: "export_log",
            type: "image_button",
            button_icon: "../images/upload.png",
            button_text: "导出日志",
            functions: {
            
            }
        },{
            enable: true,
            id: "deleteLog",
            name: "deleteLog",
            type: "link_button",
            button_icon: "delete.png",
            button_text: "删除日志",
            functions: {
                onclick: "get_delete_args();warning_log_box(delete_Date);"
            }
        },{
            enable: true,
            id: "clearLog",
            name: "clearLog",
            type: "link_button",
            // href: "/cgi-bin/url_log.cgi?ACTION=clearLog",
            button_icon: "delete.png",
            button_text: "清空日志",
            functions: {
                onclick: "warning_log_box('clear');"
            }
        }
    
    ]
};
var add_panel = new RuleAddPanel( add_panel_config );
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );
var importLog_panel = new RuleAddPanel( importLog_panel_config );

function search( element ) {
    add_panel.show();

}
function show_importLog( element ) {
    importLog_panel.show();
}

function importLog() {
    
    var upload_file=$('#upload_file').val();
    var bin_reg = /.dat$/;
    if (upload_file=='') {
        alert('请选择文件');
    } 
    // else if(bin_reg.test(file_lib)==false){
    //     show_popup_alert_mesg('文件格式错误');
    // }
    else{
        importLog_panel.hide();
        // show_waiting_mesg("上传中...");
        add_panel_body_form_id_for_importLog_panel.submit();
    }
}

function searchItem(e) {
    // if($("img").hasClass("popup-error-tip")){
    //     message_manager.show_error_mesg("请正确输入查询条件");
    //     add_panel.hide();
    //     return false;
    // }
    if ($('#export_log')) {
        $("#start_time").attr('value',$('#start_date').val());
        $("#start_hour").attr('value',$('#start_time_hour').val());
        $("#start_min").attr('value',$('#start_time_minute').val());
        $("#end_time").attr('value',$('#end_date').val());
        $("#end_hour").attr('value',$('#end_time_hour').val());
        $("#end_min").attr('value',$('#end_time_minute').val());
        
    };
    start_date = $('#start_date').val();
    start_time_hour = $('#start_time_hour').val();
    start_time_minute = $('#start_time_minute').val();
    end_date = $('#end_date').val();
    end_time_hour = $('#end_time_hour').val();
    end_time_minute = $('#end_time_minute').val();

    update_log_data('1','false',e);

    // add_panel.hide();

}
//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: ass_url,
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
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




//检测选择时间是否非法
function checkTime(str) {
    var myDate = new Date();
    var chooseTime = arrInt( str.split("-") );
    var localTime = arrInt( myDate.toLocaleDateString().split("/") );
    var flag = false;
    if ( chooseTime[0] > localTime[0] ) {
        flag = true;
    }
    else if ( chooseTime[0] == localTime[0] ) {
        if ( chooseTime[1] > localTime[1] ) {
            flag = true;
        }else if ( chooseTime[1] == localTime[1] ) {
            if ( chooseTime[2] > localTime[2] ) {
                flag = true;
            }
        }
    }
    return flag;
    function arrInt(arr) {
        for(var i = 0; i < arr.length; i++) {
            arr[i] = parseInt(arr[i]);
        }
        return arr;
    }
}


function show_suggestion( v,f ) {
    var time = $("#log_date_input_id").val();
    var sending_data = {
        ACTION: 'query_suggestion',
        name: v,
        file:f,
        time:time
    }

    function ondatareceived(data) {
        message_manager.show_details_message( data.mesg , true);
    }

   do_request(sending_data, ondatareceived);

}

function import_panel_extendrender(argument) {

    $("#export_log").append('<input type="hidden" name="ACTION" value="down_log" style="width:0;height:0;">')
    .wrap('<form enctype="multipart/form-data" method="post" action="/cgi-bin/botnet_log.cgi" style="display:inline-block"></form>');
    $("#export_log").append('<input type="hidden" id="start_time" name="start_time" style="width:0;height:0;">');
    $("#export_log").append('<input type="hidden" id="start_hour" name="start_hour" style="width:0;height:0;">');
    $("#export_log").append('<input type="hidden" id="start_min" name="start_min" style="width:0;height:0;">');
    $("#export_log").append('<input type="hidden" id="end_time" name="end_time" style="width:0;height:0;">')
    $("#export_log").append('<input type="hidden" id="end_hour" name="end_hour" style="width:0;height:0;">');
    $("#export_log").append('<input type="hidden" id="end_min" name="end_min" style="width:0;height:0;">');
}

function show_the_tip_message(num) {
    var mesg = '';
    if(num == 0) {
        var sd = start_date;
        var ed = end_date;
        if(sd == '' && ed == ''){
            mesg = '确定删除全部日志吗？';
        }
        else{
            mesg = '确定删除您查询的日志吗？';
        }
    }
    if(num == 1){
        mesg = '确定清空全部日志吗？'
    }
    return mesg;

}
var delete_Date;
function get_delete_args() {
    if (start_date == '' && start_time_hour == '' && start_time_minute == '' && end_date == '' && end_time_hour == '' && end_time_minute == '') {
        delete_Date = '';
        return;
    } else {
        delete_Date = "date";
        return;
    }
}
function clear_add_panel_text() {
    $("#start_date").val('');
    $("#start_time_hour").val('00');
    $("#start_time_minute").val('00');

    $("#end_date").val('');
    $("#end_time_hour").val('00');
    $("#end_time_minute").val('00');

    $("#sourceIP").val('');
    $("#destinationIP").val('');
}

function deleteLog() {
    var mesg = confirm_pwd();
    if (mesg == "success"){
        var sending_data = {
            ACTION: "delete",
            start_time: start_date,
            start_hour: start_time_hour,
            start_min: start_time_minute,
            end_time: end_date,
            end_hour: end_time_hour,
            end_min: end_time_minute
        };
        function ondatareceived(data) {
            // warning_box(data.filestr);
            // console.log(data);
            // if(data.status == '0') {
            //     message_manager.show_note_mesg(data.mesg);
            // }
            // else {
            //     message_manager.show_error_mesg(data.mesg);
            // }
            delete(list_panel.is_log_search);
            list_panel.update_info( true );
        }
        do_request( sending_data,ondatareceived, function() {
            message_manager.show_popup_error_mesg("数据错误！");
        })
    }
}
function clearLog() {
    var mesg = confirm_pwd();
    if (mesg == "success"){
        var sending_data = {
            ACTION: "clearLog"
        };
        function ondatareceived(data) {
            // console.log(data);
            // if(data.status == '1') {
            //     message_manager.show_note_mesg(data.mesg);
            // }
            // else {
            //     message_manager.show_error_mesg(data.mesg);
            // }
            list_panel.update_info( true );

        }
        do_request( sending_data,ondatareceived, function() {
            message_manager.show_popup_error_mesg("数据错误！");
        })
    }
}