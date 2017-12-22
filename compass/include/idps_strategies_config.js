/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/idps_strategies_config.cgi",
    add_title: "添加规则",
    update_title: "更新规则",
    page_size: 18,
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
var eidt_respond_type_flag = 0;//为1时表示编辑set,为2时表示编辑rule
var check = new ChinArk_forms();

var object = {
   'form_name':'TEMPLATE_FORM',
   'option':{
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");

function edit_config_data( data_item ) {
    /*CONFIGURATION VARIABLES - BEGIN*/

    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function config_display_data( data_item ) {
    /*CONFIGURATION VARIABLES - BEGIN*/

    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function create_other_opt_image_button( data_item_id, data_item ) {
    var actions = "";
    /*CONFIGURATION VARIABLES - BEGIN*/
    actions += '<input type="image" class="action-image" src="../images/respond.png" title="修改响应方式" value="' + data_item_id + '" onclick="edit_set_respond_type(this, \'set\', \'' + data_item.respond_type + '\');"/>';
    actions += '<input type="image" class="action-image" src="../images/edit.png" title="修改" value="' + data_item_id + '" onclick="edit_my_strategies(this, \'' + data_item.strategy_set_filename + '\');"/>';
    /*CONFIGURATION VARIABLES - END*/
    return actions;
}

function do_other_when_edit_item( data_item ) {
    /*DO SOMETHING WHEN EDIT - BEGIN*/

    /*DO SOMETHING WHEN EDIT - END*/
}

function do_other_when_reset_edit_box() {
    /*DO SOMETHING WHEN RESET - BEGIN*/

    /*DO SOMETHING WHEN RESET - END*/
}

function edit_my_strategies( element, set_filename ) {
    reset_search_key();
    set_set_filename( set_filename );
    select_edit_item_line( element );
    new_init();
    show_strategy_items_list();
}

function edit_set_respond_type( element, type, respond_type ) {
    select_edit_item_line( element );
    set_selected_respond_type( respond_type );
    show_respond_type_choices();
    set_respond_type_flag( type );
}

function change_respond_type() {
    if( respond_type_selected() ) {
        if( is_change_set_respond_type() ) {
            change_set_respond_type();
        } else if ( is_change_rule_respond_type() ) {
            change_rule_respond_type();
        }
    }
}

function change_set_respond_type() {
    var line = paging_holder.selected_line;
    reset_selected_line();//重置选中的行以免出现提示
    hide_respond_type_choices();
    opt_item_respond_type( "edit_respond_type", line );
}

function opt_item_respond_type(opt, line){
    var respond_type = get_selected_respond_type();
    var sending_data = {
        ACTION: opt,
        respond_type: respond_type
    };

    if( line < 0 ) {
        /*没有单独编辑任何行，就编辑选中的行*/
        var detail_data = paging_holder.data_content.detail_data;
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
    do_action(sending_data);
}

function edit_respond_type_selected_items() {
    var selected_num = get_selected_items_count();
    if(selected_num > 0) {
        set_selected_respond_type( get_first_selected_respond_type() );
        show_respond_type_choices();
        set_respond_type_flag( 'set' );
    } else {
        show_warn_mesg("未选择任何项目,操作失败");
    }
}

function get_first_selected_respond_type() {
    var respond_type = "";
    var detail_data = paging_holder.data_content.detail_data;
    var items_length = detail_data.length;
    for(var i = 0; i < items_length; i++) {
        if(detail_data[i].checked) {
            respond_type = detail_data[i].respond_type;
            break;
        }
    }
    return respond_type;
}

function get_selected_items_count() {
    var detail_data = paging_holder.data_content.detail_data;
    var items_length = detail_data.length;
    var selected_num = 0;
    for(var i = 0; i < items_length; i++) {
        if(detail_data[i].checked) {
            selected_num++;
        }
    }
    return selected_num;
}

function set_selected_respond_type( respond_type_id ) {
    var respond_types = document.getElementsByClassName("respond_type_item");
    var selected_num = 0;
    for( var i = 0; i < respond_types.length; i++ ) {
        if( respond_types[i].id == respond_type_id ) {
            /*选中了当前响应类型*/
            respond_types[i].checked = true;
            $('#label_for_'+respond_types[i].id).addClass("respond_type_selected");
            selected_num++;
        } else {
            respond_types[i].checked = false;
            $('#label_for_'+respond_types[i].id).removeClass("respond_type_selected");
        }
    }
    if( !selected_num ) {
        /*如果没有被选中的项，就默认选中默认项(日志记录)*/
        respond_types[i -1].checked = true;
        $('#label_for_alert').addClass("respond_type_selected");
    }
}

function get_selected_respond_type() {
    var ret_value = "";
    var respond_type_items = document.getElementsByClassName("respond_type_item");
    for( var i = 0; i < respond_type_items.length; i++ ) {
        if( respond_type_items[i].checked ) {
            ret_value = respond_type_items[i].value;
            break;
        }
    }
    return ret_value;
}

function select_respond_type() {
    var respond_types = document.getElementsByClassName("respond_type_item");
    for( var i = 0; i < respond_types.length; i++ ) {
        if( respond_types[i].checked ) {
            /*选中了当前响应类型*/
            $('#label_for_'+respond_types[i].id).addClass("respond_type_selected");
        } else {
            $('#label_for_'+respond_types[i].id).removeClass("respond_type_selected");
        }
    }
}

function respond_type_selected() {
    var ret_value = false;
    var respond_type_items = document.getElementsByClassName("respond_type_item");
    for( var i = 0; i < respond_type_items.length; i++ ) {
        if( respond_type_items[i].checked ) {
            ret_value = true;
            break;
        }
    }
    return ret_value;
}

function is_change_set_respond_type() {
    if( eidt_respond_type_flag == 1 ) {
        return true;
    } else {
        return false;
    }
}

function is_change_rule_respond_type() {
    if( eidt_respond_type_flag == 2 ) {
        return true;
    } else {
        return false;
    }
}

function reset_search_key() {
    document.getElementById("new-search-key").value = "";
}

function set_set_filename( set_filename ) {
    document.getElementById("load_set_filename").value = set_filename;
}

function set_respond_type_flag( type ) {
    if( type == "set" ) {
        eidt_respond_type_flag = 1;
    } else if ( type = "rule" ) {
        eidt_respond_type_flag = 2;
    } else {
        eidt_respond_type_flag = 0;
    }
}

function reset_respond_type_flag() {
    eidt_respond_type_flag = 0;
}

function show_respond_type_choices() {
    $("#respond_type_choices_back").show();
    $("#respond_type_choices").show();
}

function hide_respond_type_choices() {
    $("#respond_type_choices_back").hide();
    $("#respond_type_choices").hide();
    if( is_change_set_respond_type() ) {
        deselect_edit_item_line();
    } else if ( is_change_rule_respond_type() ) {
        new_deselect_edit_item_line();
    }
}