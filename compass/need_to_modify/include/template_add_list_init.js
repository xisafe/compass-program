/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/template_add_list_new.cgi",
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
var check = new ChinArk_forms();

var object = {
   'form_name':'TEMPLATE_FORM',
   'option':{
        'name':{
            'type':'text',
            'required':'1',
            'check':'name|',
            'ass_check':function(eve){
                // var msg="";
                // var name = eve._getCURElementsByName("name","input","TEMPLATE_FORM")[0].value;
                // if (name == ""){
                //     msg = "请填写名字";
                // }
                // return msg;
            }
        },
        'field1':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
        'field2':{
            'type':'select-multiple',
            'required':'1',
            'ass_check':function(eve){
                // var msg="";
                // var field2 = eve._getCURElementsByName("field2","select","TEMPLATE_FORM")[0].value;
                // if (field2 == ""){
                //     msg = "必须选择一个";
                // }
                // return msg;
            }
        },
        'field4':{
            'type':'textarea',
            'required':'1',
            'check':'note|',
        },
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