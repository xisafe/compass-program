/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/idps_sub_console_config.cgi",
    add_title: "添加子控制台",
    update_title: "更新子控制台",
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
    if(data_item.sub_console_connected == "CONNECTED") {
        data_item.sub_console_connected_render = "<font color='green'>已连接</font>";
    } else if (data_item.sub_console_connected == "DISCONNECT") {
        data_item.sub_console_connected_render = "<font color='red'>未连接</font>";
    }

    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function create_other_opt_image_button(data_item_id, data_item) {
    var actions = "";
    /*CONFIGURATION VARIABLES - BEGIN*/

    /*CONFIGURATION VARIABLES - END*/
    return actions;
}

/*Global Vsariable*/
var check = new ChinArk_forms();

var object = {
   'form_name':'TEMPLATE_FORM',
   'option':{
        'sub_console_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
        },
        'sub_console_ip':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        }
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");