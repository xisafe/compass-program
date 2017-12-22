/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/idps_sub_engine_config.cgi",
    add_title: "添加引擎",
    update_title: "更新引擎",
    page_size: 15,
    total_page: 0,
    first_page: 1,
    current_page: 1,
    from_num: 0,
    to_num: 0,
    search: "",
    selected_line:-1,/*记录当前被编辑的行，-1表示没有编辑的行*/
    import_error_mesg: [],
    data_content:{
        total: 0,
        detail_data: [],
        display_cols: []
    }
};
/*CONFIGURATION VARIABLES - END*/

function edit_config_data(data_item) {
    /*CONFIGURATION VARIABLES - BEGIN*/

    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function config_display_data(data_item) {
    /*CONFIGURATION VARIABLES - BEGIN*/
    if(data_item.engine_connected == "CONNECTED" && data_item.engine_status == "UP") {
        data_item.engine_status_render = "<font color='green'>开启</font>";
    } else if (data_item.engine_connected == "CONNECTED" && data_item.engine_status == "DOWN"){
        data_item.engine_status_render = "<font color='red'>关闭</font>";
    } else {
        data_item.engine_status_render = "<font color='red'>未知</font>";
    }
    if(data_item.engine_connected == "CONNECTED") {
        data_item.engine_connected_render = "<font color='green'>已连接</font>";
    } else if (data_item.engine_connected == "DISCONNECT") {
        data_item.engine_connected_render = "<font color='red'>未连接</font>";
    }

    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function create_other_opt_image_button(data_item_id, data_item) {
    var actions = "";
    /*CONFIGURATION VARIABLES - BEGIN*/
    // var engine_status_on = "UP";
    // var engine_status_off = "DOWN";
    // if(data_item.engine_connected == "CONNECTED" && data_item.engine_status == engine_status_on) {
    //     actions += '<input type="image" class="action-image" src="../images/powered-on.png" title="关闭" value="' + data_item_id + '" onclick="power_down_item(this);"/>';
    // } else if ( data_item.engine_connected == "CONNECTED" && data_item.engine_status == engine_status_off ) {
    //     actions += '<input type="image" class="action-image" src="../images/powered-down.png" title="开启" value="' + data_item_id + '" onclick="power_on_item(this);"/>';
    // } else {
    //     actions += '<input type="image" class="action-image" src="../images/error_note.png" title="未连接" value="' + data_item_id + '"/>';
    // }
    /*CONFIGURATION VARIABLES - END*/
    return actions;
}

function get_data_item( id ) {
    var detail_data = paging_holder.data_content.detail_data;
    var data_item = "";
    for( var i = 0; i < detail_data.length; i++ ) {
        if ( detail_data[i].line == id ) {
            data_item = detail_data[i];
            break;
        }
    }
    return data_item;
}

/*Global Vsariable*/
var check = new ChinArk_forms();

var object = {
   'form_name':'TEMPLATE_FORM',
   'option':{
        'engine_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
        },
        'engine_addr':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        }
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");