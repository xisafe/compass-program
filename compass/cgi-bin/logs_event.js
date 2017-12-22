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
  // list_panel_extendRender();
    
    add_panel.render();
    add_panel.hide();

    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel ); 



    list_panel.set_ass_message_manager( message_manager );

    list_panel.update_info( true );

  $(".ctr_inpt").css("width","50px");
    $("#search_date").datepicker({   
        dateFormat:"yy-mm-dd",
        // changeMonth: true,
        yearSuffix: '年', 
        monthNames: ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
        dayNamesMin: ['日','一','二','三','四','五','六'],
        onClose: function( selectedDate ) {
        $( "#end_date" ).datepicker( "option", "minDate", selectedDate );
        
      }
    });
    

});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/logs_event.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

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
                value: "查询",
                functions: {
                    onclick:"searchItem();"
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
            title: "查询时间",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    style: "",
                    id: "search_date",
                    name: "search_date",
                    value: "",
                    readonly:"readonly",
                    functions: {
                    
                    },
                    class:"calendar"

                },
                {
                  enable:"true",
                  type:"text",
                  id:"note",
                  name:"note",
                  functions:{}
                }
            ]
        }]
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
            width: "20%"
        }, {
            enable: true,
            type: "text",
            title: "消息",
            name: "messages",
            width: "70%"
        }, {
            enable: true,
            type: "text",
            title: "结果",
            name: "result",
            width: "10%",
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
        }
  
    ]
};
var add_panel = new RuleAddPanel( add_panel_config );
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );

function search( element ) {
    add_panel.show();

}

function searchItem() {
    var sending_data = {
        ACTION:"search",
        search:$("#search_date").val(),
        note:$('#note').val()
    };

    function ondatareceived(data){

        // message_manager.show_popup_mesg("查询成功");
        list_panel.detail_data=data.detail_data;
        list_panel.total_num = data.total_num;
        list_panel.update_info();

    }
    
    do_request(sending_data, ondatareceived);

    add_panel.hide();

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