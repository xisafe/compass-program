/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/idps_sec_event_config.cgi",
    add_title: "添加二次事件",
    update_title: "更新二次事件",
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
var check = new ChinArk_forms();

var object = {
   'form_name':'TEMPLATE_FORM',
   'option':{
        'name':{
            'type':'text',
            'required':'1',
            'check':'name|',
        },
        'summary':{
            'type':'textarea',
            'required':'0',
            'check':'note|',
        },
        'sid':{
            'type':'text',
            'required':'1',
            'check':'int|',
        },
        'src_ip_value':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
        'dst_ip_value':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
        'src_port_value':{
            'type':'text',
            'required':'1',
            'check':'port|',
        },
        'dst_port_value':{
            'type':'text',
            'required':'1',
            'check':'port|',
        },
        'min_count':{
            'type':'text',
            'required':'1',
            'check':'int|',
        },
        'interval':{
            'type':'text',
            'required':'1',
            'check':'int|',
        }
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
    actions += '<input type="image" class="action-image" src="../images/respond.png" title="修改响应方式" value="' + data_item_id + '" onclick="edit_respond_type(this, \'' + data_item.respond_type + '\');"/>';
    /*CONFIGURATION VARIABLES - END*/
    return actions;
}

function do_other_when_edit_item( data_item ) {
    /*DO SOMETHING WHEN EDIT - BEGIN*/
    var selects = document.getElementsByClassName("ref_extend");
    var spans   = document.getElementsByClassName("extend_text");
    for( var i = 0; i < selects.length; i++ ) {
        change_type( selects[i] );
    }
    var input_radios = $(".respond_type_choice_item");
    input_radios.each( function() {
        var input_radio_handle = this;
        if( data_item[$(input_radio_handle).attr("name")] == $(input_radio_handle).val() ) {
            $( input_radio_handle ).attr( "checked", true );
        }
    });
    var input_radios_level = $(".risk_level");
    input_radios_level.each( function() {
        var input_radio_handle = this;
        if( data_item[$(input_radio_handle).attr("name")] == $(input_radio_handle).val() ) {
            $( input_radio_handle ).attr( "checked", true );
        }
    });
    hide_port_tr( data_item.protocol );
    $("input[name=name]").attr( "disabled", true );
    /*DO SOMETHING WHEN EDIT - END*/
}

function do_other_when_reset_edit_box() {
    /*DO SOMETHING WHEN RESET - BEGIN*/
    var spans = document.getElementsByClassName("extend_text");
    for( var i = 0; i < spans.length; i++ ) {
        spans[i].style.display = "none";
    }
    show_port_tr();
    $("input[name=name]").attr( "disabled", false );
    /*DO SOMETHING WHEN RESET - END*/
}

function change_type( element ) {
    var input_name = element.name + "_value";
    var spans = document.getElementsByClassName("extend_text");
    for( var i = 0; i < spans.length; i++ ) {
        if( spans[i].children[0].name == input_name ) {
            if( element.value == "none" ) {
                spans[i].style.display = "none";
            } else {
                spans[i].style.display = "inline";
            }
        }
    }
}

function edit_respond_type( element, respond_type ) {
    select_edit_item_line( element );
    set_selected_respond_type( respond_type );
    show_respond_type_choices();
}

function change_respond_type() {
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
    sending_data[line] = line;
    /*Do request*/
    do_action(sending_data);
}

function set_selected_respond_type( respond_type_id ) {
    var respond_types = document.getElementsByClassName("respond_type_item");
    for( var i = 0; i < respond_types.length; i++ ) {
        if( respond_types[i].id == respond_type_id ) {
            /*选中了当前响应类型*/
            respond_types[i].checked = true;
            $('#label_for_'+respond_types[i].id).addClass("respond_type_selected");
        } else {
            respond_types[i].checked = false;
            $('#label_for_'+respond_types[i].id).removeClass("respond_type_selected");
        }
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

function show_respond_type_choices() {
    $("#respond_type_choices_back").show();
    $("#respond_type_choices").show();
}

function hide_respond_type_choices() {
    $("#respond_type_choices_back").hide();
    $("#respond_type_choices").hide();
    deselect_edit_item_line();
}

function show_port_tr() {
    $(".specify_port_tr").show();
}

function hide_port_tr( protocol ) {
    if( protocol == "icmp" ) {
        $(".specify_port_tr").hide();
    } else {
        $(".specify_port_tr").show();
    }
}