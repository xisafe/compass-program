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
   
});
var list_panel;
var add_panel;
var analysis_panel;
var message_box_config = {
    url: "/cgi-bin/around_plan.cgi",
    check_in_id: "mesg_box_tmp",
    panel_name: "my_message_box",
};
var message_manager;


var add_panel_config = {
    url: "/cgi-bin/around_plan.cgi",
    check_in_id: "panel_tmp_add",
    panel_name: "add_panel",
    rule_title: "循环时间计划",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {
           var s = $("#start_time_hour").val() + $("#start_time_minute").val();
           var e = $("#end_time_hour").val() + $("#end_time_minute").val();
           if( s == e ){
            message_manager.show_popup_note_mesg("请选择有效的循环时间计划");
            return false;
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

            $('.start_date').removeAttr('checked');
            var start_date_arr=start_date.split("|");
            start_date_arr.forEach(function(v,i){

                $('.start_date[value='+v+']').attr("checked",true);
            })

            $('#start_time_hour').children('option').removeAttr('selected');
            $('#start_time_hour option[value='+start_time_hour+']').attr('selected','selected');
            $('#start_time_minute').children('option').removeAttr('selected');
            $('#start_time_minute option[value='+start_time_minute+']').attr('selected','selected');

            $('#end_date').children('option').removeAttr('selected');
            $('#end_date option[value='+end_date+']').attr('selected','selected');

            var end_date_arr=end_date.split("|");
            end_date_arr.forEach(function(v,i){
                $('#end_date option[value='+v+']').attr('selected','selected');
            })

            $('#end_time_hour').children('option').removeAttr('selected');
            $('#end_time_hour option[value='+end_time_hour+']').attr('selected','selected');
            $('#start_time_minute').children('option').removeAttr('selected');
            $('#end_time_minute option[value='+end_time_minute+']').attr('selected','selected');

        },
        after_load_data: function( add_obj,data_item ) {
           
        },
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
        {
            title: "名称",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "name",
                    name: "name",
                    value: "",
                    style: "width: 239px",
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
            title: "周期",
            sub_items: [
            {
                enable:true,
                label:"周一",
                type:"checkbox",
                class: "start_date",
                name: "start_date",
                value:"1"
            },{
                enable:true,
                label:"周二",
                type:"checkbox",
                class: "start_date",
                name: "start_date",
                value:"2"
            },{
                enable:true,
                label:"周三",
                type:"checkbox",
                class: "start_date",
                name: "start_date",
                value:"3"
            },{
                enable:true,
                label:"周四",
                type:"checkbox",
                class: "start_date",
                name: "start_date",
                value:"4"
            },{
                enable:true,
                label:"周五",
                type:"checkbox",
                class: "start_date",
                name: "start_date",
                value:"5"
            },{
                enable:true,
                label:"周六",
                type:"checkbox",
                class: "start_date",
                name: "start_date",
                value:"6"
            },{
                enable:true,
                label:"周日",
                type:"checkbox",
                class: "start_date",
                name: "start_date",
                value:"7"
            }
                // {
                //     enable: true,
                //     type: "checkbox",
                //     // multiple: "multiple",
                //     style: "width: 108px", 
                //     // tip:"可按ctrl进行多选",
                //     id: "start_date",
                //     name: "start_date",
                //     inputs: [
                //         {
                //             value: "1",
                //             text: "星期一"
                //         },
                //         {
                //             value: "2",
                //             text: "星期二",
                //         },
                //         {
                //             value: "3",
                //             text: "星期三"
                //         },
                //          {
                //             value: "4",
                //             text: "星期四"
                //         },
                //         {
                //             value: "5",
                //             text: "星期五"
                //         },
                //         {
                //             value: "6",
                //             text: "星期六"
                //         },
                //         {
                //             value:"7",
                //             text:"星期天"
                //         }
                //     ],
                //     functions: {
                    
                //     },
                //       check: {
                //         // type:'select-one',
                //         // type:"select",
                //         // required:'1',
                //         ass_check:function( check ){
                            
                //         }
                //     }

                // }
                // {
                //     enable:true,
                //     value:"可按ctrl进行多选",
                //     text:"可按ctrl进行多选",
                //     // id: "start_date",
                //     // name: "start_date"
                // }
            ]
        },
        {
            title: "时间*",
            sub_items: [
                {
                    enable: true,
                    type:"select",
                    style: "width:40px;",
                    id: "start_time_hour",
                    name: "start_time_hour",
                    options: select_options(24)
                   
                },
                 {
                    enable: true,
                    label:"时",
                    type:"select",
                    style: "width:40px;",
                    id: "start_time_minute",
                    name: "start_time_minute",
                    options: select_options(60)
                },
                 {
                    enable: true,
                    label:"到",
                    type:"select",
                    style: "width:40px;",
                    id: "end_time_hour",
                    name: "end_time_hour",
                    options: select_options(24),
                    
                },
                 {
                    enable: true,
                    label:"时",
                    type:"select",
                    style: "width:40px;",
                    id: "end_time_minute",
                    name: "end_time_minute",
                    options: select_options(60)
                    
                  
                }
               
            ]
        }
        
    ]
};

var list_panel_render = {
    'week':{
        render:function(default_rendered_text,data_item){
            // var week_var = data_item.week.split(" ")[0];
             var week_var_s = data_item.start_time.split(" ")[0];
             var week_s=week_var_s.split("|");
             for(var i=0;i<week_s.length;i++){
                switch(parseInt(week_s[i])){
                    case 1: 
                        week_s[i]= "周一 "; 
                        break;
                    
                    case 2: 
                        week_s[i]= "周二 "; 
                        break;
                    
                    case 3: 
                        week_s[i] = "周三 "; 
                        break;
                    case 4: 
                        week_s[i] = "周四 ";
                        break;  
                    case 5: 
                        week_s[i] = "周五 "; 
                    break;
                    case 6: 
                        week_s[i] = "周六 "; 
                    break;
                    case 7:
                        week_s[i] = "周日 ";
                          break;      
                }
             }
             return week_s.join(" ");
        }
    },
    'start_time':{
        render:function( default_rendered_text,data_item){
             // var week_var = data_item.start_time.split(" ")[0];
             var time_var = data_item.start_time.split(" ")[1];
             return time_var;
             // switch( parseInt(week_var) ){
             //    case 1: 
             //        return week_var = "星期一 "+time_var; 
                    
             //    case 2: 
             //        return week_var = "星期二 "+time_var; 
                    
             //    case 3: 
             //       return week_var = "星期三 "+time_var; 
                   
             //    case 4: 
             //        return week_var = "星期四 "+time_var;
                    
             //    case 5: 
             //        return week_var = "星期五 "+time_var; 
                    
             //    case 6: 
             //        return week_var = "星期六 "+time_var; 
                    
             //    default:
             //        return week_var = "星期日 "+time_var;
                                
             // }
        }
    },
    'end_time':{
        render:function( default_rendered_text,data_item){
             // var week_var = data_item.end_time.split(" ")[0];
             var time_var = data_item.end_time.split(" ")[1];
             return time_var;
             // switch( parseInt(week_var) ){
             //    case 1: 
             //        return week_var = "星期一 "+time_var; 
                    
             //    case 2: 
             //        return week_var = "星期二 "+time_var; 
                    
             //    case 3: 
             //       return week_var = "星期三 "+time_var; 
                   
             //    case 4: 
             //        return week_var = "星期四 "+time_var;
                    
             //    case 5: 
             //        return week_var = "星期五 "+time_var; 
                    
             //    case 6: 
             //        return week_var = "星期六 "+time_var; 
                    
             //    default:
             //        return week_var = "星期日 "+time_var;
                                
             // }
        }
    },
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
                    "class": "action-image"
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
                    "class": "action-image"
                }
            ];
            return PagingHolder.create_action_buttons( action_buttons );
        }
        }
    };


var list_panel_config = {
    url: "/cgi-bin/around_plan.cgi", /* ***必填***，控制数据在哪里加载 */
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
            "title": "周期",        //一般text类型需要title,不然列表没有标题
            "name":  "week",
            "width": "50%",
        },{
            "enable": true,
            "type": "text",
            "title": "开始时间",        //一般text类型需要title,不然列表没有标题
            "name":  "start_time",
            "width": "10%",
        },
        {
            "enable": true,
            "type": "text",
            "title": "结束时间",
            "name": "end_time",
            "width": "10%",
        }, {
            "enable": true,
            "type": "action",
            "title": "活动/动作",
            "name": "action",
            "width": "10%",
            "td_class":"align-center"
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
    event_handler: {
        before_load_data: function( list_obj ) {
            
        },
        after_load_data: function ( list_obj, response ) {
          
        },
    },
    
};

// function enable_selected_items() {
//     var selected_items = list_panel.get_selected_items();
//     var selected_items_id = new Array();
//     for( var i = 0; i < selected_items.length; i++ ) {
//         selected_items_id.push( selected_items[i].id );
//     }

//     var ids = selected_items_id.join( "&" );

//     list_panel.enable_item( ids );
// }

// function disable_selected_items() {
//     var selected_items = list_panel.get_selected_items();
//     var selected_items_id = new Array();
//     for( var i = 0; i < selected_items.length; i++ ) {
//         selected_items_id.push( selected_items[i].id );
//     }

//     var ids = selected_items_id.join( "&" );

//     list_panel.disable_item( ids );
// }

function delete_selected_items(e) {
    var ids = "";
    if(e.id == "delete_selected"){
        var selected_items = list_panel.get_selected_items();
        var selected_items_id = new Array();
        for( var i = 0; i < selected_items.length; i++ ) {
            selected_items_id.push( selected_items[i].id );
        }
        ids = selected_items_id.join( "&" );
    }else{
        ids = e.value;
    }
    
    list_panel.delete_item( ids );
}

function extend_search_function( element ) {
    list_panel.update_info( true );
}

function create_action_buttons( action_buttons ) {
    var buttons = "";

    if( action_buttons === undefined ) {
        return buttons;/*如果没有定义相应的对象，直接返回*/
    }

    for( var i = 0; i< action_buttons.length; i++ ) {
        var item = action_buttons[i];
        if( item.enable === undefined || !item.enable ){
            continue;
        }
        buttons += '<input type="image" ';
        if( item.id !== undefined && item.id ) {
            buttons += 'id="' + item.id + '" ';
        }
        if( item.value !== undefined && item.value ) {
            buttons += 'value="' + item.value + '" ';
        }
        if( item.name !== undefined && item.name ) {
            buttons += 'name="'+ item.name +'" ';
        }
        if( item.class !== undefined && item.class ) {
            buttons += 'class="action-image ' + item.class + '" ';
        } else {
            buttons += 'class="action-image" ';
        }
        if( item.button_text !==undefined && item.button_text ) {
            buttons += 'title="' + item.button_text + '" ';
        }
        if( item.button_icon !== undefined && item.button_icon ) {
            buttons += 'src="../images/' + item.button_icon +'" ';
        }
        if( item.functions !== undefined && item.functions ) {
            var functions = item.functions;
            for ( var key in functions ) {
                buttons += key +'="' + functions[key] + '" ';
            }
        }
        buttons += '/>';
    }

    return buttons;
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
    var selected_items = list_panel.get_selected_items();
    if(selected_items.length < 1){
        message_manager.show_popup_note_mesg("请先选中策略项");
        return;
    }
    var selected_items_id = new Array();
    var ids = "";
    var is_used = "no";
    var used_policy = new Array();
    for(var i=0;i<selected_items.length;i++){
        selected_items_id.push(selected_items[i].id);
        if(selected_items[i].rules_for_policy != ""){
            is_used = "yes";
            used_policy.push(selected_items[i].name);
        }
    }
    ids = selected_items_id.join("&");
    if(is_used == "yes"){
        list_panel.operate_item( ids, 'delete_data',used_policy.join("、")+
        '策略模板正在被使用。删除该策略模板，也将删除使用该策略模板的规则', true );
    }else{
        list_panel.delete_item(ids);
    }
}