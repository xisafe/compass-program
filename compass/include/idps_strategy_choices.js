/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var new_paging_holder = {
    url: "/cgi-bin/idps_strategy_choices.cgi",
    add_title: "添加规则",
    update_title: "更新规则",
    page_size: 10,
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

/*Global Vsariable*/
var new_check = new ChinArk_forms();

var new_object = {
   'form_name':'ELIMINATE_FORM',
   'option':{
        
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");

function new_edit_config_data( data_item ) {
    /*CONFIGURATION VARIABLES - BEGIN*/
    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function new_config_display_data( data_item ) {
    /*CONFIGURATION VARIABLES - BEGIN*/
    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function new_create_other_opt_image_button( data_item_id, data_item ) {
    var actions = "";
    /*CONFIGURATION VARIABLES - BEGIN*/
    /*CONFIGURATION VARIABLES - END*/
    return actions;
}

function new_do_other_when_edit_item( data_item ) {
    /*DO SOMETHING WHEN EDIT - BEGIN*/
    /*DO SOMETHING WHEN EDIT - END*/
}

function new_do_other_when_reset_edit_box() {
    /*DO SOMETHING WHEN RESET - BEGIN*/
    /*DO SOMETHING WHEN RESET - END*/
}

function show_strategy_choices_list() {
    $("#strategy_choices_list_back").show();
    $("#strategy_choices_list").show();
}

function hide_strategy_choices_list() {
    $("#strategy_choices_list_back").hide();
    $("#strategy_choices_list").hide();
}

function choose_strategy_item_id() {
    new_init();
    show_strategy_choices_list();

}

function choosed_strategy_item_id() {
    var choosed_item = get_choosed_strategy_item();//得到的是ID号
    if( choosed_item != "") {
        hide_strategy_choices_list();
        fill_choosed_item( choosed_item );
    }
}

function get_choosed_strategy_item() {
    var choosed_item = "";
    var strategy_items = document.getElementsByName("strategy_item");
    for( var i = 0; i < strategy_items.length; i++ ) {
        if( strategy_items[i].checked ) {
            choosed_item = strategy_items[i].value;
            break;
        }
    }
    return choosed_item;
}

function get_choosed_strategy_item_protocol( choosed_item ) {
    var detail_data = new_paging_holder.data_content.detail_data;
    var protocol = "";
    for( var i = 0; i < detail_data.length; i++ ) {
        if( detail_data[i].sid == choosed_item ) {
            protocol = detail_data[i].protocol;
            break;
        }
    }
    return protocol;
}

function fill_choosed_item( choosed_item ) {
    /*第一步，将sid号填入名为sid的input框*/
    document.getElementsByName("sid")[0].value = choosed_item;
    /*第二步，判断选中的规则的协议是否为icmp，做相应处理*/
    var choosed_item_protocol = get_choosed_strategy_item_protocol( choosed_item );
    hide_port_tr( choosed_item_protocol );
    document.getElementsByName("protocol")[0].value = choosed_item_protocol;
}