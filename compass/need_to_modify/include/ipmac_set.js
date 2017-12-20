/*
 * 描述: 【IP/MAC绑定设置页面】
 * 作者: 
 * 历史：2015-1-5  xinzhiwei创建
 */


var message_box_config = {
    url: "/cgi-bin/ipmac_set.cgi",
    check_in_id: "message_box_config",
    panel_name: "message_box"
}

var toggle_switch_panel_config = {
    url: "/cgi-bin/ipmac_set.cgi",
    check_in_id: "toggle_switch_panel_config",
    panel_name: "toggle_switch_panel",
    rule_title_adding_icon: "applications-blue.png",
    rule_title_adding_prefix: "",   // 把前缀文字置为空！
    rule_title: "开启/关闭IP/MAC绑定功能",
    is_panel_closable: false,
    is_panel_stretchable: false,
    is_modal: false,   // 模态框如果设置为true的话那么这个面板初始时就是弹出来的！
    items_list: [{
        title: "IP/MAC绑定功能",
        sub_items: [{
            enable: true,
            type: "radio",
            id: "toggle_switch_on",
            name: "toggle_switch",
            label: "开启",
            functions: {
                // onclick: "toggle_switch_on();", 函数执行失败原因就是函数名toggle_switch_on();和id属性值"toggle_switch_on"重名了！
                onclick: "handle_toggle_switch_on();"    // 解决办法就是给函数换个别的名字就好了
            }
        }, {
            enable: true,
            type: "radio",
            id: "toggle_switch_off",
            name: "toggle_switch",
            label: "关闭",
            functions: {
                // onclick: "toggle_switch_off();",
                onclick: "handle_toggle_switch_off();"
            }
        }]
    },{
        title: "是否跨三层",
        // id: "CROSS_LEVEL_TR",
        sub_items: [{
            enable: true,
            type: "radio",
            id: "cross_level_on",
            name: "cross_level",
            label: "是",
            functions:{
                onclick: "handle_cross_on();"
            }
        }, {
            enable: true,
            type: "radio",
            id: "cross_level_off",
            name: "cross_level",
            label: "否",
            functions:{
                onclick: "handle_cross_off();"
            }
        }]
    }]
};


var snmp_add_panel_config = {
    url: "/cgi-bin/ipmac_set.cgi",
    check_in_id: "snmp_add_panel_config",
    panel_name: "snmp_add_panel",
    rule_title_adding_icon: "applications-blue.png",
    rule_title_adding_prefix: "",   // 把前缀文字置为空！
    rule_title: "SNMP配置",
    is_panel_closable: true,
    is_panel_stretchable: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "m"
    },
    event_handler: {
        before_cancel_edit:function(add_obj){
        },
        after_cancel_edit:function(add_obj){
        },
        before_save_data:function( add_obj, sending_data ){
        },
        after_save_data:function( add_obj, received_data ){
            update_snmp_data();
        }
    },
    items_list: [{
        title: "访问SNMP服务超时时间",
        sub_items: [{
            enable: true,
            type: "select",
            id  : "timeout_limit",
            name: "timeout_limit",
            tip: "秒",
            style: "width:90px;",
            options:[]
        }]
    },{
        title: "访问SNMP服务时间间隔",
        sub_items: [{
            enable: true,
            type: "select",
            id  : "time_interval",
            name: "time_interval",
            tip: "秒",
            style: "width:90px;",
            options:[]
        }]
    },{
        title: "SNMP协议版本",
        sub_items: [{
            enable: true,
            type: "select",
            id  : "version",
            name: "version",
            style: "width:90px;",
            options:[{
                value: "V2",
                text: "V2"
            }]
        }]
    }]
};

var switchboard_add_panel_config = {
    url: "/cgi-bin/ipmac_set.cgi",
    check_in_id: "switchboard_add_panel_config",
    panel_name: "switchboard_add_panel",
    rule_title: "交换机",   // '添加交换机'
    is_panel_closable: true,
    is_panel_stretchable: false,
    border_transparent: true,
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
    },
    items_list: [{
        title: "IP地址",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "ip_address",
            name: "ip_address",
            check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                type:'text',        /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required:'1',       /* **必填**，1表示必填，0表示字段可为空 */
                check:'ip|',      /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                ass_check:function( check ){

                }
            }
        }]
    }, {
        title: "SNMP团体字",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "read_community",
            name: "read_community"
        }]
    }, {
        title: "启用",
        sub_items: [{
            enable: true,
            type: "checkbox",
            // id  : "switchboard_enabled",
            // name: "switchboard_enabled",
            name: "enable"
        }]
    }]
};

var switchboard_list_panel_config = {
    url: "/cgi-bin/ipmac_set.cgi",
    check_in_id: "switchboard_list_panel_config",
    panel_name: "switchboard_list_panel",
    page_size: 3,    // 只让它显示5行
    // render: switchboard_list_panel_actions_render,
    event_handler: {
        before_load_data: function( add_obj, data_item ) {
        },
        after_load_data: function ( add_obj, data_item ) {
            // $(".edit_item_for_switchboard_list_panel").remove(); 可惜还是不好使，说明此时列表的编辑动作按钮还不存在！
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
        title: "交换机IP地址",
        name: "ip_address",
        width: "40%"
    }, {
        enable: true,
        type: "text",
        title: "SNMP团体字",
        name: "read_community",
        width: "40%"
    }, {
        enable: true,
        type: "action",
        title: "活动/动作",
        name: "action",
        "td_class":"align-center",
        width: "15%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        button_icon: "applications-blue.png",
        button_text: "配置SNMP",
        style: "width:100px;height:30px;",
        functions: {
            onclick: "show_snmp_panel();"
        }
    }, {
        enable: true,
        type: "image_button",  // 要加type属性，不然按钮上显示不出文字
        button_icon: "add16x16.png",
        button_text: "添加交换机",
        style: "width:100px;height:30px;",
        functions: {
            onclick: "show_switchboard_add_panel();"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "delete.png",
        button_text: "删除选中",
        style: "width:100px;height:30px;",
        functions: {
            onclick: "delete_selected_sb_items(this);"
        }
    }]
};

var ipmac_add_panel_config = {
    url: "/cgi-bin/ipmac_set.cgi",
    check_in_id: "ipmac_add_panel_config",
    panel_name: "ipmac_add_panel",
    rule_title: "IP/MAC绑定",
    is_panel_closable: true,
    is_panel_stretchable: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_cancel_edit:function(add_obj){
        },
        after_cancel_edit:function(add_obj){
            $("#IP_ADDR").attr("disabled",false);
            $("#MAC_ADDR").attr("disabled",false);
        },
        before_load_data: function( add_obj, data_item ) {
        },
        after_load_data: function ( add_obj, data_item ) {
            $("#IP_ADDR").attr("disabled",true);
            $("#MAC_ADDR").attr("disabled",true);
        },
        before_save_data:function( add_obj, sending_data ){
            /*for(var item in sending_data){
                str += item+":"+sending_data[item];
            }*/  // 经过测试证明sending_data是string类型的！
            
            /*if(sending_data.id != ""){
                sending_data['IPMAC_SOURCE'] = "报文学习";  因为sending_data不是对象类型所以失败
            }*/
            // sending_data = sending_data + "&IPMAC_SOURCE=报文学习";   测试也失败，原因是此接口其实没有成功提供sending_data的引用权限出来！
        },
        after_save_data:function( add_obj, received_data ){
            $("#IP_ADDR").attr("disabled",false);
            $("#MAC_ADDR").attr("disabled",false);
        }
    },
    items_list: [{
        title: "IP地址*",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "IP_ADDR",
            name: "IP_ADDR",
			check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                type:'text',        /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required:'1',       /* **必填**，1表示必填，0表示字段可为空 */
                check:'ip|',      /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                ass_check:function( check ){
                    /*
                     * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
                     *
                     * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
                     *
                     * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
                     */
                }
            }
        }]
    },{
        title: "MAC地址*",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "MAC_ADDR",
            name: "MAC_ADDR",
			check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                type:'text',        /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required:'1',       /* **必填**，1表示必填，0表示字段可为空 */
                check:'mac|',      /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                ass_check:function( check ){
                    /*
                     * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
                     *
                     * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
                     *
                     * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
                     */
                }
            }
        }]
    },{
        title: "启用",
        sub_items: [{
            enable: true,
            type: "checkbox",
            // id  : "ipmac_enabled",
            // name: "ipmac_enabled",
            name: "enable"
        }]
    },{
        title: "备注",
        sub_items: [{
            enable: true,
            type: "text",
            id  : "ipmac_note",
            name: "ipmac_note",
			check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                type:'text',        /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required:'0',       /* **必填**，1表示必填，0表示字段可为空 */
                check:'note|',      /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                ass_check:function( check ){
                    /*
                     * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
                     *
                     * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
                     *
                     * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
                     */
                }
            }
        } /*,{
            enable: true,
            type: "text",
            name: "IPMAC_SOURCE",   // 技巧：来源字段在编辑的时候要传递到add-panel里以防止编辑时该字段被覆盖为空值
            item_style: "display: none;"
            //但是黑客可以轻易的扫描出这个hidden域并且修改来源字段的值，所以这个处理是很不安全的，
            //最保险的做法是在后台保存的时候来源字段不接受页面提交的值而仍然保存为旧值就OK了
        }*/]
    }]
};

var ipmac_batch_import_panel_config = {
    url: "/cgi-bin/ipmac_set.cgi",
    check_in_id: "ipmac_batch_import_panel_config",
    panel_name: "ipmac_batch_import_panel",
    rule_title_adding_icon: "upload.png",
    rule_title_adding_prefix: "导入",
    rule_title: "IP/MAC文件",
    is_modal: true,
    modal_config: {
        modal_box_size: "m"
    },
    event_handler: {
        before_save_data: function(add_obj, sending_data){
            // 这个接口没反应说明你点导入的时候发送的动作请求已经不是默认的save_data而很有可能是import_data，
        },
        after_save_data: function(add_obj, received_data){
        }
    },
    is_panel_closable: true,
    is_panel_stretchable: false,
    // footer_buttons: {
    //     add_btn: false,
    //     cancel_btn: true,
    //     import_btn: true   // 因为这个接口仅仅实现了发送import-data请求给后台，而没有提供onreceived接口，所以你要重写自己的实现
        /*if ( footer_buttons.import !== undefined && footer_buttons.import ) {
            panel_footer += '<input type="button" id="' + import_button_id + '" class="' + panel_control.form_button_class + '" value="' + button_import_text + '"/>';
            panel_footer += '<input type="hidden" name="ACTION"  value="import_data"/>';
            panel_footer += '<input type="hidden" name="panel_name"  value="' + panel_config.panel_name + '"/>';
        }*/
    // },
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add: false,
        cancel: false,
        import: false,
        sub_items: [                /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            {
                enable: true,
                type: "submit",
                value: "确认",
                style:"vertical-align: top;background-image: url(../images/button.jpg);background-repeat: repeat-x;border-top: 0px;border-left: 1px solid #b3e2f4;border-bottom: 1px solid #b3e2f4;border-right: 1px solid #b3e2f4;",
                id:"upload_ipmac",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "add_ip_mac_file();"
                }
            },{
                enable: true,
                type: "button",
                value: "取消",
                functions: {        /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                    onclick: "ipmac_batch_import_panel.hide();"
                }
            },
            {
                enable:true,
                type:"hidden",
                name:"ACTION",
                value:"import_data"
            }
        ]
    },
    items_list: [{
        title: "IP/MAC文件",
        sub_items: [{
            enable: true,
            type: "file",
            style:"height:24px",
            name: "upload_file",
            check: {
                type: "file",
                required: 1
            }
        }, {
            enable: true,
            
                type: "label",
                value: "下载文件模板",
                id:"download_file",
                style:"color:blue;text-decoration:underline;",
                style:"    color: blue;text-decoration: underline;"
            // href: "/cgi-bin/ipmac_set.cgi?ACTION=export_template_file",
            // link_icon: "download.png",
            // link_text: "下载文件模板"
        }]
    }]
};

var ipmac_list_panel_config = {
    url: "/cgi-bin/ipmac_set.cgi",
    check_in_id: "ipmac_list_panel_config",
    panel_name: "ipmac_list_panel",
    page_size: 9,   // 手动设置只让它显示5行
    // render: ipmac_list_panel_actions_render,
    event_handler: {
        before_load_data: function( add_obj, data_item ) {
        },
        after_load_data: function ( add_obj, data_item ) {
            // $(".edit_item_for_ipmac_list_panel").remove();  可惜还是不好使，说明此时列表的编辑动作按钮还不存在！
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
        name: "IP_ADDR",
        width: "30%"
    }, {
        enable: true,
        type: "text",
        title: "MAC地址",
        name: "MAC_ADDR",
        width: "30%"
    }, {
        enable: true,
        type: "text",
        title: "来源",
        name: "IPMAC_SOURCE",
        width: "15%"
    }, {
        enable: true,
        type: "text",
        title: "备注",
        name: "ipmac_note",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "活动/动作",
        name: "action",
        "td_class":"align-center",
        width: "10%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",  // 要加type属性，不然按钮上显示不出文字
        button_icon: "add16x16.png",
        button_text: "手动添加",
        style: "width:100px;height:30px;",
        functions: {
            onclick: "show_ipmac_add_panel();"
        }
    },{
        enable: true,
        type: "image_button",  // 要加type属性，不然按钮上显示不出文字
        button_icon: "../images/stock_up-16.png",
        button_text: "IP/MAC文件导入",
        style: "width:125px;height:30px;",
        functions: {
            onclick: "show_ipmac_batch_import_panel();"
        }
    },{
        enable: true,
        type: "link_button",
        id: "export_selected_rules",
        href: "/cgi-bin/ipmac_set.cgi?ACTION=export_data&panel_name=ipmac_list_panel",
        button_icon: "../images/download.png",
        button_text: "IP/MAC文件导出",
        functions: {
        }
    },{
        enable: true,
        type: "image_button",
        button_icon: "delete.png",
        button_text: "删除选中",
        style: "width:100px;height:30px;",
        functions: {
            onclick: "delete_selected_ipmac_items(this);"
        }
    }]
};

var message_manager = new MessageManager( message_box_config );
var toggle_switch_panel = new RuleAddPanel( toggle_switch_panel_config );
var snmp_add_panel = new RuleAddPanel( snmp_add_panel_config );

var switchboard_add_panel  = new RuleAddPanel( switchboard_add_panel_config );
var switchboard_list_panel = new PagingHolder( switchboard_list_panel_config );

var ipmac_add_panel  = new RuleAddPanel( ipmac_add_panel_config );
var ipmac_list_panel = new PagingHolder( ipmac_list_panel_config );
var ipmac_batch_import_panel = new RuleAddPanel( ipmac_batch_import_panel_config );
var CROSS_STATUS = "";

function do_ajax( sending_data, onreceived ) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/ipmac_set.cgi",
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            ipmac_list_panel.show_error_mesg("返回数据格式有误,请检查");
        },
        success: onreceived
    });
}
$( document ).ready(function() {

    /* 渲染面板 */
    message_manager.render();
    if( status == -1 ){
        message_manager.show_popup_error_mesg( mesg );
    }else{
        if(mesg != ""){
            message_manager.show_popup_note_mesg( mesg );
        }
    }
    toggle_switch_panel.render();
    snmp_add_panel.render();
    init_snmp_options();

    switchboard_add_panel.render();
    switchboard_list_panel.render();
    ipmac_add_panel.render();
    ipmac_list_panel.render();
    ipmac_batch_import_panel.render();

    snmp_add_panel.hide();  //让它隐藏起来！
    ipmac_add_panel.hide();
    switchboard_add_panel.hide();
    ipmac_batch_import_panel.hide();

    /* 设置面板关联 */
    switchboard_add_panel.set_ass_list_panel( switchboard_list_panel );
    switchboard_list_panel.set_ass_add_panel( switchboard_add_panel );
    switchboard_add_panel.set_ass_message_manager( message_manager );
    switchboard_list_panel.set_ass_message_manager( message_manager );

    ipmac_add_panel.set_ass_list_panel( ipmac_list_panel );
    ipmac_list_panel.set_ass_add_panel( ipmac_add_panel );
    ipmac_add_panel.set_ass_message_manager( message_manager );
    ipmac_list_panel.set_ass_message_manager( message_manager );
    $(".search:eq(0)").remove();
    $(".add-panel-footer:eq(0)").remove();
    $(".add-panel-close-button").hide();

    $("#search_key_for_ipmac_list_panel").attr("placeholder","仅支持以IP地址查询...");
    $("#list_panel_id_for_ipmac_list_panel a>button").css({"width":"125px","height":"30px"});
    $("<span style='float:left;'>&nbsp;&nbsp;注：重复的IP/MAC条目上传时会被过滤掉</span>").insertBefore("#add_panel_import_button_id_for_ipmac_batch_import_panel");

    hide_all_divs();  // 初始默认要隐藏起来
    switchboard_list_panel.hide();  //默认把交换机配置列表隐藏起来！但问题是最终还是显示了出来！
    // 原因就是在后台'BIND'的值为'enable'的情况下在load_init_data()中执行了show_all_divs();里面执行了switchboard_list_panel.slideUp();导致其在隐藏了之后又显示了出来！
    load_init_data();
    // switchboard_list_panel.hide();    放在这里还会导致一个严重错误就是当cross值为on时你应该显示，但你这句却一概隐藏了！！// 放在load_init_data();的后面就可以了
    update_snmp_data();

    switchboard_list_panel.update_info( true );
    ipmac_list_panel.update_info( true );

});

function handle_toggle_switch_on(){
    var sending_data = {
       ACTION: "IP_MAC_START"
    }
    function onreceived(response){
        show_all_divs();
        if( CROSS_STATUS == "off" ){
            switchboard_list_panel.hide();
        }
        if ( response.status == 0 ) {
            message_manager.show_note_mesg( response.mesg );
            $("#toggle_switch_on").attr("disabled",true);     // 这点很重要，你从后台收到开启成功时就要把‘开启’radio设置为不可选择，防止用户已经开启了过后再点击开启！！
            $("#toggle_switch_off").attr("disabled",false);   // 不要忘记把‘关闭’重新恢复为可选！！
        } else {
            message_manager.show_error_mesg( response.mesg );
        }
    }
    do_ajax( sending_data, onreceived );
}

function handle_toggle_switch_off(){
    var sending_data = {
       ACTION: "IP_MAC_CLOSE"
    }
    function onreceived(response){
        hide_all_divs();
        /*if( CROSS_STATUS == "on" ){
            switchboard_list_panel.show();  // 
        }*/
        if ( response.status == 0 ) {
            message_manager.show_note_mesg( response.mesg );
            $("#toggle_switch_off").attr("disabled",true);
            $("#toggle_switch_on").attr("disabled",false);   // 不要忘记把‘开启’重新恢复为可选！！
        } else {
            message_manager.show_error_mesg( response.mesg );
        }
    }
    do_ajax( sending_data, onreceived );
}

function handle_cross_on(){
    switchboard_list_panel.show();
    var sending_data = "ACTION=CROSS_ON";
    function onreceived(response){
        CROSS_STATUS = "on";   // 这里必须手动把CROSS_STATUS的值改成on，因为后台的值刚刚已被改成了on，
        // 而前台设置的全局变量CROSS_STATUS的值必须要与后台的值时刻保持一致！
    }
    do_ajax( sending_data, onreceived );
}

function handle_cross_off(){
    switchboard_list_panel.hide();
    var sending_data = "ACTION=CROSS_OFF";
    function onreceived(response){
        CROSS_STATUS = "off";   // see above
    }
    do_ajax( sending_data, onreceived );
}

function init_snmp_options(){
    var options = "";
    for(var i=3; i<=9; i++){
        // if(i == 5){  selected="selected";  }
        options += '<option value="' + i + '">' + i + '</option>';
    }
    $( "#timeout_limit" ).empty();
    $( "#timeout_limit" ).append( options );

    options = "";
    for( i=10; i<=40; ){
        // if(i == 30){  selected="selected";  }
        options += '<option value="' + i + '">' + i + '</option>';
        i = i + 5;
    }
    $( "#time_interval" ).empty();
    $( "#time_interval" ).append( options );
}

function show_all_divs(){
    // $("#snmp_add_panel_config").slideDown("slow");    原因在这里，就是执行这句导致snmp面板显示了而非隐藏！
    $("#CROSS_LEVEL_TR").show();
    // $("#switchboard_list_panel_config").slideDown("fast"); // 原因就是这里也对switchboard_list_panel进行了操作，与handle_cross_off()函数里的hide()操作造成了冲突导致sb_list_panel隐藏失败
    // 不要用slideDown方法(因为这样做发现在其后面执行hide()结果就是失败的！)，把slideDown方法改为show()方法就可以了
    $("#switchboard_list_panel_config").show();
    $("#ipmac_list_panel_config").slideDown("fast");
}
function hide_all_divs(){
    $("#CROSS_LEVEL_TR").hide();
    // $("#switchboard_list_panel_config").slideUp("fast");
    // 不要用slideUp方法,改为hide()方法就可以了
    $("#switchboard_list_panel_config").hide();
    $("#ipmac_list_panel_config").slideUp("fast");
}

function load_init_data(){
    function onreceived(response){
        var status = response.status;
        var cross = response.cross;
        CROSS_STATUS = cross;
        if(status == "on"){
            $("#toggle_switch_on").attr("checked", true);
            $("#toggle_switch_on").attr("disabled", true);
            show_all_divs();
            if( cross == "off" ){ switchboard_list_panel.hide(); }
        }else{
            $("#toggle_switch_off").attr("checked", true);
            $("#toggle_switch_off").attr("disabled", true);
        }
        if(cross == "on"){
            $("#cross_level_on").attr("checked", true);
            switchboard_list_panel.show();
        }else{
            $("#cross_level_off").attr("checked", true);
        }
    }
    do_ajax( { ACTION: "load_init_data" }, onreceived );
}
function update_snmp_data(){
    function onreceived_func(response){
        var data_item = response.snmp_hash;
        var timeout = data_item['SNMP_TIMEOUT'];//data_item.SNMP_TIMEOUT;
        var interval = data_item['SNMP_INTERVAL'];
        var version = data_item['VERSION'];
        // alert("timeout="+timeout+"interval="+interval);
        $("#timeout_limit").val( timeout );
        $("#time_interval").val( interval );
        $("#version").val( version );
    }
    do_ajax( { ACTION: "load_snmp_data" }, onreceived_func );
}
function delete_selected_sb_items(element){
    var checked_items = switchboard_list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }
    var ids = checked_items_id.join( "&" );
    if( ids == ""){
        switchboard_list_panel.show_error_mesg( "未检测到删除项" );
        return;
    }
    switchboard_list_panel.delete_item( ids );
}

function delete_selected_ipmac_items(element){
    var checked_items = ipmac_list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }
    var ids = checked_items_id.join( "&" );
    if( ids == ""){
        ipmac_list_panel.show_error_mesg( "未检测到删除项" );
        return;
    }
    ipmac_list_panel.delete_item( ids );
}

function show_snmp_panel() {
    snmp_add_panel.show();
}
function show_switchboard_add_panel() {
    switchboard_add_panel.show();
}
function show_ipmac_add_panel() {
    ipmac_add_panel.show();
}
function show_ipmac_batch_import_panel(){
    ipmac_batch_import_panel.show();
    $("#download_file").on('click', function(event) {
      window.open('/cgi-bin/ipmac_set.cgi?ACTION=export_template_file');  
        
    }).hover(function() {
        window.document.body.style.cursor='pointer';
    }, function() {
        window.document.body.style.cursor='default';
    });;
}

function add_ip_mac_file(){
    $("#add_panel_body_form_id_for_ipmac_batch_import_panel").submit();

    ipmac_batch_import_panel.hide();
}
