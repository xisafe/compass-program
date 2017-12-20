/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var strategy_file_paging_holder = {
    url: "/cgi-bin/idps_strategy_file_config.cgi",
    add_title: "添加规则",
    update_title: "更新规则",
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

/*Global Vsariable*/
var new_check = new ChinArk_forms();

var ips_object = {
   'form_name':'ELIMINATE_FORM',
   'option':{
        'eliminate_ips':{
            'type':'textarea',
            'required':'0',
            'check':'ip|ip_mask',
            'ass_check': function( eve ) {

            }
        }
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");

function new_edit_config_data( data_item ) {
    /*CONFIGURATION VARIABLES - BEGIN*/
    data_item.eliminate_ips = data_item.eliminate_ips.replace( /&/g, "\n")
    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function new_config_display_data( data_item ) {
    /*CONFIGURATION VARIABLES - BEGIN*/
    data_item.classtype = data_item.classtype_cn;
    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function new_create_other_opt_image_button( data_item_id, data_item ) {
    var actions = "";
    /*CONFIGURATION VARIABLES - BEGIN*/
    actions = '<input type="image" class="action-image" src="../images/respond.png" title="修改响应方式" value="' + data_item_id + '" onclick="edit_rule_respond_type(this,\'rule\', \'' + data_item.respond_type + '\');"/>';
    /*CONFIGURATION VARIABLES - END*/
    return actions;
}

function new_do_other_when_edit_item( data_item ) {
    /*DO SOMETHING WHEN EDIT - BEGIN*/
    show_eliminate_edit_box();
    /*DO SOMETHING WHEN EDIT - END*/
}

function new_do_other_when_reset_edit_box() {
    /*DO SOMETHING WHEN RESET - BEGIN*/
    hide_eliminate_edit_box();
    /*DO SOMETHING WHEN RESET - END*/
}

function edit_rule_respond_type( element, type, respond_type ) {
    new_select_edit_item_line( element );
    set_selected_respond_type( respond_type );
    show_respond_type_choices();
    set_respond_type_flag( type );
}

function change_rule_respond_type() {
    var set_filename = document.getElementById("load_set_filename").value;
    var line = strategy_file_paging_holder.selected_line;
    new_reset_selected_line();//重置选中的行以免出现提示
    hide_respond_type_choices();
    new_opt_item_respond_type( "edit_respond_type", set_filename, line );
}

function new_opt_item_respond_type( opt, set_filename, line ){
    var respond_type = get_selected_respond_type();
    var sending_data = {
        ACTION: opt,
        respond_type: respond_type,
        set_filename: set_filename
    };

    if( line < 0 ) {
        /*没有单独编辑任何行，就编辑选中的行*/
        var detail_data = strategy_file_paging_holder.data_content.detail_data;
        var items_length = detail_data.length;
        for(var i = 0; i < items_length; i++) {
            if(detail_data[i].checked) {
                sending_data[detail_data[i].line] = detail_data[i].line;
            }
        }
    } else {
        sending_data[line] = line;
    }
    /*Do request*/
    new_do_action(sending_data);
}

function new_edit_respond_type_selected_items() {
    var selected_num = new_get_selected_items_count();
    if(selected_num > 0) {
        set_selected_respond_type( new_get_first_selected_respond_type() );
        show_respond_type_choices();
        set_respond_type_flag( 'rule' );
    } else {
        show_warn_mesg("未选择任何项目,操作失败");
    }
}

function new_get_first_selected_respond_type() {
    var respond_type = "";
    var detail_data = strategy_file_paging_holder.data_content.detail_data;
    var items_length = detail_data.length;
    for(var i = 0; i < items_length; i++) {
        if(detail_data[i].checked) {
            respond_type = detail_data[i].respond_type;
            break;
        }
    }
    return respond_type;
}

function new_get_selected_items_count() {
    var detail_data = strategy_file_paging_holder.data_content.detail_data;
    var items_length = detail_data.length;
    var selected_num = 0;
    for(var i = 0; i < items_length; i++) {
        if(detail_data[i].checked) {
            selected_num++;
        }
    }
    return selected_num;
}

function show_strategy_items_list() {
    $("#strategy_items_list_back").show();
    $("#strategy_items_list").show();
}

function hide_strategy_items_list() {
    $("#strategy_items_list_back").hide();
    $("#strategy_items_list").hide();
    deselect_edit_item_line();
}

function show_eliminate_edit_box() {
    $("#eliminate_edit_box_back").show();
    $("#eliminate_edit_box").show();
}

function hide_eliminate_edit_box() {
    $("#eliminate_edit_box_back").hide();
    $("#eliminate_edit_box").hide();
}