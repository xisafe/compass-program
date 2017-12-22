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
    // add_panel.render();
    add_panel.hide();
	
    init();

    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );

    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );

    list_panel.update_info( true );

    log_detail_panel.render();
    log_detail_panel.hide();
    // log_detail_panel.update_info(true);
    show_error_update()
    $('.right-waiting').fadeOut();
    show_wait_update()
    
});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/sm_update_manager.cgi";
var log_detail_panel_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "log_detail_panel",         // ***必填***，确定面板挂载在哪里 
    page_size: 10,                  //===可选===，定义页大小，默认是15 
    panel_name: "log_detail_panel",       // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "升级日志",
    is_panel_closable: true,
    is_paging_tools: true,
    is_default_search: false,

    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 11
    },
    title_icon:"detail.png",
    panel_header: [                 // ***必填***，控制数据的加载以及表头显示 
         {
            "enable": true,
            "type": "text",
            "title": "时间",
            "name": "update_time",
            "width": "30%"
        }, {
            "enable": true,
            "type": "text",
            "title": "操作",        //一般text类型需要title,不然列表没有标题
            "name": "update_action",
            "width": "60%"
        }, {
            "enable": true,
            "type": "text",
            "title": "结果",
            "name": "update_res",
            "width": "10%"
        }
    ],
    // bottom_extend_widgets: {
    //     id: "",
    //     name: "",
    //     class: "align-center",
    //     sub_items: [
    //          {
    //             enable: true,
    //             type: "image_button",
    //             class: "",
    //             button_text: "取消",
    //             style: "margin-top: 5px;margin-bottom: 5px;",
    //             functions: {
    //                 onclick: "log_detail_panel.hide();"
    //             }
    //         }
    //     ]
    // }
}
var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

var list_panel_render = {

    'action': {
        render: function( default_rendered_text, data_item ) {
            var action_buttons = [
                {
                    enable: true,
                    id: "update_item_"+data_item.lib_type,
                    name: "update_item",
                    button_icon: "uploadtray.png",
                    button_text: "升级",
                    value: data_item.id,
                    functions: {
                        onclick: "update_item('"+data_item.function+"','"+data_item.lib_type+"');"
                    },
                    class: "action-image",
               },{
                    enable: true,
                    id: "show_update_log",
                    name: "show_update_log",
                    button_icon: "detail.png",
                    button_text: "显示升级日志",
                    value: data_item.id,
                    functions: {
                        onclick: "show_update_log('"+data_item.lib_type+"');"
                    },
                    class: "action-image", 
                }
            ];
            var update_arr = data_item.update_status.split('\:')
            switch(true){
                case update_arr[0] === 'COMPLETED':break
                case update_arr[0] === 'UPGRADING':
                    action_buttons[0].button_icon='uploadtray1.png'
                    action_buttons[0].disabled='disabled'
                    action_buttons[2] = {
                        enable: true,
                        id: "wait_update_"+data_item.lib_type,
                        name: "wait_update",
                        button_icon: "wait-small.gif",
                        // button_text: "有用户正在升级",
                        value: data_item.id,
                        functions: {
                            // onclick: "show_update_status('"+data_item.lib_type+"','"+data_item.deadtime+"');"
                        },
                        class: "action-image upspring",
                    } 
                    break
                case update_arr[0] === 'ERROR':
                    action_buttons[2] = {
                        enable: true,
                        id: "show_error_"+data_item.lib_type,
                        name: "show_error_info",
                        button_icon: "error_note.png",
                        // button_text: "显示错误信息",
                        value: data_item.id,
                        functions: {
                            // onclick: "message_manager.show_popup_error_mesg('"+update_arr[1]+"');"
                        },
                        class: "action-image upspring", 
                    }
                    break
                default:break
            }
            if (data_item.deadtime=='序列号无效') {
                    action_buttons[0].button_icon='uploadtray1.png';
                    action_buttons[0].disabled='disabled';
            }
        
            return PagingHolder.create_action_buttons( action_buttons );
        }
    },
    'version':{
        render:function(default_rendered_text,data_item){
            if(default_rendered_text == "暂无当前版本"){
                return '<font color="red">'+default_rendered_text+'</font>';
            }
            else{
               return default_rendered_text;
            }
        }
    },
    'deadtime':{
        render:function (default_rendered_text,data_item) {
            if(default_rendered_text == "序列号无效"){
                return '<font color="red">'+default_rendered_text+'</font>';
            }
            else{
               return default_rendered_text;
            }
        }
    }
};

var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
	page_size: 20,
	is_default_search: false,
    render: list_panel_render,
	event_handler: {
        before_load_data: function( list_obj ) {
          
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
            title: "序号",
            name: "index",
            td_class: "align-center",
            width: "5%"
        }, {
            enable: true,
            type: "text",
            title: "功能",
            name: "function",
            width: "20%"
        }, {
            enable: true,
            type: "text",
            title: "当前版本",
            name: "version",
            td_class: "align-center",
            width: "20%"
        }, {
            enable: true,
            type: "text",
            title: "升级有效期",
            name: "deadtime",
            td_class: "align-center",
            width: "20%"
        },{
            enable: true,
            type: "action",
            title: "操作",
            name: "action",
            width: "7%",
            td_class:"align-center"
        }
    ],
    top_widgets: [                          /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */
    ]
};

var add_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title_adding_prefix: "",
    rule_title_adding_icon:"uploadtray.png",
    cancel_refresh :true,
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
                value: "upgrade",

            },
            {
                enable: true,
                type: "hidden",
                name: "lib_type",
                value: "",

            },
            {
                enable: true,
                type: "submit",
                style: "",
                id: "update",
                functions: {
                    onclick:"check_update();"
                },

            }
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
            show_error_update()

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
    items_list: [ 
            {
            title: "选择升级文件(.dat)",
            sub_items: [
                {
                    enable: true,
                    type: "file",
                    value: "选择",
                    id:"file_lib",
                    name: "file_lib",
                    functions: {
                        onclick: ""
                    },
                    style:"width:300px;height:25px;border-radius:4px"
                }
                
            ]
        }]
};


var add_panel = new RuleAddPanel(add_panel_config);
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );
var log_detail_panel = new PagingHolder( log_detail_panel_config );
function update_item( text,type ) {
    
  
    add_panel_config.footer_buttons.sub_items[1].value = type;

    add_panel_config.rule_title='导入升级包-'+text;

    add_panel.render();
    add_panel.show();
}

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
function init() {
    /*初始化消息框,以使图片加载*/
    show_waiting_mesg("准备中...");
    hide_waiting_mesg();
}

function show_update_status(type,deadtime) {
    var sending_data ={
        ACTION:'update',
        detail:'updating',
        lib_type: type,
        temp:'direct_get'
    }
    function ondatareceived(data) {
        var data_mesg = data.mesg.split('\:')
        switch(true){
            case data_mesg[0] === 'COMPLETED':
                $('#wait_update_'+data.status+',#tip_'+data.status).hide()
                $('#update_item_'+data.status).show()
                if (deadtime != '序列号无效') {
                    $('#update_item_'+data.status).removeAttr('disabled').attr('src', '../images/uploadtray.png');
                }
                break
            case data_mesg[0] === 'ERROR':
                $('#show_error_info'+data.status).attr('src', '../images/error_note.png')
                break
            case data_mesg[0] === 'UPGRADING':
                $('#tip_'+data.status+' .tip-text').text(data_mesg[1])
                setTimeout(show_update_status(data.status),3000)
                break
            default:break
        }
        
    }
    do_request(sending_data,ondatareceived)
}
function show_wait_update(){
    var up_type=['app_lib','file_lib','url_lib','zombie_lib','virus_lib','web_lib','function']
    var content=''
    for (var i = 0; i < up_type.length; i++) {
        var ele = '#wait_update_'+up_type[i];
        if ($(ele).length) {
            list_panel.detail_data.forEach(function(item,index){
                if(item.lib_type === up_type[i]){
                    deadtime = item.deadtime
                }
            })
            var sending_data ={
                ACTION:'update',
                detail:'updating',
                lib_type: up_type[i],
                temp:'direct_get'
            }
            function ondatareceived(data) {

                var data_mesg = data.mesg.split('\:')
                switch(true){
                    case data_mesg[0] === 'COMPLETED':
                        $('#wait_update_'+data.status).hide()
                        // message_manager.show_popup_error_mesg('其他用户已完成升级')
                        if (deadtime != '序列号无效') {
                            $('#update_item_'+data.status).removeAttr('disabled').attr('src', '../images/uploadtray.png');
                        }
                        break
                    case data_mesg[0] === 'ERROR':
                        $('#show_error_info'+data.status).attr('src', '../images/error_note.png')
                        // message_manager.show_popup_error_mesg(data_mesg[1])
                        break
                    case data_mesg[0] === 'UPGRADING':
                        $('#update_item_'+data.status).hide();
                        if ($('#tip_'+data.status).length) {
                            $('#tip_'+data.status+' .tip-text').text(data_mesg[1])
                        }else{

                            tips.init('wait_update_'+data.status,{
                                id:'tip_'+data.status,
                                title:'升级进程',
                                trigger:'click',
                                drag:true,
                                close:true,
                                adjust:{
                                    width:'200px'
                                },
                                move:{
                                    top:50,
                                    left:20
                                },
                                color:'#C6E0FA',
                                content:data_mesg[1],
                                btn:{
                                    cancel:true
                                }
                            });
                        }
                        show_update_status(data.status)
                        break
                    default:break
                }
                
            }
            do_request(sending_data,ondatareceived)
        }
    }
}
function show_error_update(){
    var up_type=['app_lib','file_lib','url_lib','zombie_lib','virus_lib','web_lib','function']
    var content=''
    for (var i = 0; i < up_type.length; i++) {
        var ele = '#show_error_'+up_type[i];
        if ($(ele).length) {
            list_panel.detail_data.forEach(function(item,index){
                if(item.lib_type === up_type[i]){
                    content = item.update_status.split(':')[1]
                }
            })
            tips.init(ele,{
                id:'tip_'+up_type[i],
                trigger:'click',
                drag:true,
                // close:true,
                title:'上次升级错误原因',
                adjust:{
                    width:'200px'
                },
                move:{
                    top:50,
                    left:20
                },
                color:'#C6E0FA',
                content:content,
                btn:{
                    cancel:true,
                    custom:[{
                        text:'不再提示',
                        'data-ele':up_type[i],
                        fn:function(){
                            var error_type = $(this).attr('data-ele'),
                                error_btn = '#show_error_'+error_type
                            $(error_btn+',#tip_'+error_type).hide()
                            var sending_data = {
                                ACTION:'reset_status',
                                type:error_type
                            }
                            function ondatareceived(data){

                            }
                            do_request(sending_data,ondatareceived)
                        }
                    }]
                }
            });
        }
    }
}
// 升级过程
function update_detail(){
    add_panel.hide();
    
    var lib_type = $('input[name="lib_type"]').val();
    // form表单提交，升级进程开始
    var temp = '';
    // var sending_data ={
    //     ACTION:'update',
    //     detail:'updating',
    //     lib_type: lib_type,
    //     temp:temp
    // }
    // function ondatareceived(data) {
    //     temp = data.mesg
    //     update_mess = data.mesg.split('\:')
    //     show_waiting_mesg(update_mess[1]);
    //     if (update_mess[0] != 'COMPLETED' && update_mess[0] != 'ERROR') {
    //         do_request(sending_data,ondatareceived)
    //     }
    // }
    var sending ={
        ACTION:'update',
        detail:'updating',
        lib_type: lib_type,
        temp:'direct_get'
    }
    function ondata(data) {
        if (data.mesg.split('\:')[0] === 'UPGRADING') {
            message_manager.show_popup_error_mesg(data.mesg.split('\:')[1])
        }else{
            show_waiting_mesg("上传中...");
            $("#add_panel_body_form_id_for_add_panel").submit();
            // do_request(sending_data,ondatareceived)
        }
    }
    do_request(sending,ondata)
    // function ondatareceived_p(data) {
    //     if(data.mesg == 'updated'){
    //         do_request(sending_data_p,ondatareceived_p);            
    //     }else{
    //         if (data.mesg == 'preparing') {
    //             show_waiting_mesg("准备中...");

    //         }

    //         var sending_data_i ={
    //             ACTION:'update',
    //             detail:'preparing',
    //             lib_type: lib_type
    //         }
    //         function ondatareceived_i(data) {
    //             if (data.mesg == 'installing') {
    //                 show_waiting_mesg("升级中...");

    //             }
    //             var sending_data_e ={
    //                 ACTION:'update',
    //                 detail:'installing',
    //                 lib_type: lib_type
    //             }
    //             function ondatareceived_e(data) {
                    
    //             }

    //             if (data.mesg != 'complete') {
    //                 do_request(sending_data_e,ondatareceived_e);
    //             }
    //         }
    //         if (data.mesg != 'complete') {
    //             do_request(sending_data_i,ondatareceived_i);    
    //         }
    //     }
    // }
    // // 发送请求，捕捉升级进程开始
    // // 如果data.mesg为updated说明还在上传，需再次发送请求，如果为end说明升级结束不再发送请求，
    // // 如果为空，也说明升级结束，与end的区别为end捕捉到了结束的瞬间，而为空未捕捉到，
    // // 为空的话继续执行完后面的js代码刷新页面，end直接结束剩余js代码
    // do_request(sending_data_p,ondatareceived_p);
}
function check_update() {
    
    var file_lib=$('#file_lib').val();
    var bin_reg = /.dat$/;
    if (file_lib=='') {
        show_popup_alert_mesg('请选择文件');
    } else if(bin_reg.test(file_lib)==false){
        show_popup_alert_mesg('文件格式错误');
    }else{
        update_detail();
        // $("#add_panel_body_form_id_for_add_panel").submit();

        // add_panel.hide();

        // offline_update();
        
    }
}


var object = {
   'form_name':'RULES_UPDATE_ONLINE',
   'option':{
        'self_url':{
            'type':'text',
            'required':'1',
            'check':'url|',
            'ass_check':function(){
                
            }
        },
    }
}

var object2 = {
   'form_name':'add_panel_body_form_name_for_add_panel',
   'option'   :{
        'file_lib':{
            'type':'file',
            'required':'1',
            'ass_check':function(){
            }
        }
    }
}

var check = new ChinArk_forms();

function offline_update() {
    if(check._submit_check(object2,check)){
        //do nothing
    } else {
        show_waiting_mesg("上传中...");
    }
}

function show_update_log(type) {
    log_detail_panel.extend_sending_data ={
        type : type
    }
    log_detail_panel.update_info(true);
    log_detail_panel.show();
    // var sending_data ={
    //     ACTION :"show_update_log",
    //     type : type
    // }
    // function ondatareceived(data){
    //     if (data == null) {
    //         data = '暂无升级记录';
    //     }
    //     message_manager.show_popup_mesg(data);
    // }

    // do_request(sending_data, ondatareceived);
}
