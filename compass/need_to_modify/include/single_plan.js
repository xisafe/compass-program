$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    add_panel.render();
    list_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    
    add_panel.hide();
    
    list_panel.update_info(true);
    
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
var list_panel;
var add_panel;
var analysis_panel;
var message_box_config = {
    url: "/cgi-bin/single_plan.cgi",
    check_in_id: "mesg_box_tmp",
    panel_name: "my_message_box",
}
var message_manager;


var add_panel_config = {
    url: "/cgi-bin/single_plan.cgi",
    check_in_id: "panel_tmp_add",
    panel_name: "add_panel",
    rule_title: "单次时间计划",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {
           var s = $("#start_date").val();
           var e = $("#end_date").val();

           if(s == ""){
                message_manager.show_popup_mesg("请选择时间");
                return false;
           }else if(e == ""){
            message_manager.show_popup_mesg("请选择时间");
                return false;
           }else {
                s += " "+ $("#start_time_hour").val()+":" + $("#start_time_minute").val();
                e += " "+ $("#end_time_hour").val() +":"+ $("#end_time_minute").val();
                var begin = new Date(s).getTime();
                var end = new Date(e).getTime();
                if((begin - end )>0){
                    message_manager.show_popup_mesg("开始时间应该小于结束时间");
                    return false;
                }
                else if(begin == end){
                 message_manager.show_popup_mesg("请选择有效的单次时间计划");
                    return false;   
                }
           }

        },
        before_load_data: function( add_obj,data_item ) {
            var start_time = data_item.start_time;
            var start_date_val = start_time.split(" ");
            var start_date =start_date_val[0];
            var start_time_hour = start_date_val[1].split(":")[0];
            var start_time_minute = start_date_val[1].split(":")[1];

            var end_time = data_item.end_time;
            var end_date_var = end_time.split(" ");
            var end_date = end_date_var[0];
            var end_time_hour = end_date_var[1].split(":")[0];
            var end_time_minute =end_date_var[1].split(":")[1];

            $("#start_date").val(start_date);
            $("#start_time_hour").val(start_time_hour);
            $("#start_time_minute").val(start_time_minute);

            $("#end_date").val(end_date);
            $("#end_time_hour").val(end_time_hour);
            $("#end_time_minute").val(end_time_minute);

        },
        after_load_data: function( add_obj,data_item ) {
        },
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "名称*",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "name",
                    name: "name",
                    value: "",
                    style: "width: 235px",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'name|',
                        //other_reg:'!/^\$/',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "开始时间*",
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
            title: "结束时间*",
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
        }
        
    ]
};

var list_panel_render = {

    'action': {
        render: function( default_rendered_text, data_item ) {
        var action_buttons = [
                {
                    "enable": true,
                    "id": "edit_item",
                    "name": "edit_item",
                    "button_icon": "edit.png",
                    "button_text": "编辑",
                    "value": data_item.id,
                    "functions": {
                        onclick: "list_panel.edit_item(this.value);"
                    },
                    "class": "action-image",
                },
                {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "value": data_item.id,
                    "functions": {
                        onclick: "check_delete_rule(this.value);"
                    },
                    "class": "action-image",
                }
            ];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/single_plan.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_tmp_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持名称、时间关键字查询",
        title: ""
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            "enable": true,            //用户控制表头是否显示
            "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "class": "",                //元素的class
            "td_class": "rule-listbc",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": true,
            "type": "text",
            "title": "名称",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "15%"
        },{
            "enable": true,
            "type": "text",
            "title": "开始时间",        //一般text类型需要title,不然列表没有标题
            "name":  "start_time",
            "width": "35%",
        },
        {
            "enable": true,
            "type": "text",
            "title": "结束时间",
            "name": "end_time",
            "width": "35%",
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "10%",
            "td_class":"align-center",
        }
    ],
    top_widgets: [                  /* ===可选=== */
        {
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
            "class": "",
            "button_icon": "delete.png",
            "button_text": "删除选中",
            "functions": {
                onclick: "check_delete_selected_items()"
            }
        }
    ],
    is_default_search: true,          /* ===可选===，默认是true，控制默认的搜索条件 */
    
}




//小时取值范围
function hour_range(element){
    number_range(element, 0 ,24);
}
function number_range(element,low,high){
    var hour = $(element).val();
    var lastValue = $(element).attr("lastValue");

    if(!$(element).attr("lastValue")){
        $(element).attr("lastValue","00");
    }
    //不合法
    if(lastValue <low){
        $(element).attr("lastValue" ,low);
        $(element).val(low);
        return;
    }
    else if(lastValue >high){
        $(element).attr("lastValue" ,high);
        $(element).val(high);
        return;
    }
    if(hour < low||hour > high){
        // message_manager.show_popup_note_mesg("请输入合法的时间！");
        if(lastValue == 24){
            $(element).val('00');
        }else if (parseInt(lastValue) == 0) {
            $(element).val('24');  
        };
    }else if(hour < 10){//合法
        $(element).attr("lastValue","0"+hour);
        hour = hour + "";
        if(hour.length==1){
            $(element).val("0"+hour);   
        }
    }else{
        $(element).attr("lastValue",hour);
    }
    $(element).attr("lastValue",$(element).val());
    // console.log("lastValue:"+lastValue+"\tval:"+$(element).val());
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


//删除规则函数，包含规则引用检查
function check_delete_rule(item_id){
    //var length_used_rule = [];
    var data_item = list_panel.get_item(item_id);
    //length_used_rule = data_item.rules_for_policy.split("&");
    if( data_item.rules_for_policy != "" ){
        list_panel.operate_item( data_item.id, 'delete_data',
        '应用控制策略正在被使用，删除该应用控制策略，也将删除使用该应用控制策略的规则', true );
    }else{
        list_panel.delete_item(data_item.id);
    }
}
//删除选中规则，包含规则引用检查
function check_delete_selected_items(){
    var checked_items = list_panel.get_checked_items();
    if(checked_items.length < 1){
        message_manager.show_popup_note_mesg("请先选中策略项");
        return;
    }
    var checked_items_id = new Array();
    var ids = "";
    var is_used = "no";
    var used_policy = new Array();
    for(var i=0;i<checked_items.length;i++){
        checked_items_id.push(checked_items[i].id);
        if(checked_items[i].rules_for_policy != ""){
            is_used = "yes";
            used_policy.push(checked_items[i].name);
        }
    }
    ids = checked_items_id.join("&");
    if(is_used == "yes"){
        list_panel.operate_item( ids, 'delete_data',used_policy.join("、")+
        '策略模板正在被使用。删除该策略模板，也将删除使用该策略模板的规则', true );
    }else{
        list_panel.delete_item(ids);
    }
}