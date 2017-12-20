/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/firewall_linkage.cgi",
    add_title: "添加联动设备",
    update_title: "更新联动设备",
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
        'device_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
        },
        'device_ip':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
        'community_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
        },
        'user_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
        },
        'auth_pass':{
            'type':'password',
            'required':'1',
            'check':'note|',
            'ass_check':function(eve){
                var msg;
                var value = eve._getCURElementsByName("auth_pass","input","TEMPLATE_FORM")[0].value;
                if( value.length < 6 ){
                    msg = "密钥长度不能小于6位";
                }
                return msg;
            }
        },
        'encrypt_pass':{
            'type':'password',
            'required':'0',
            'check':'note|',
            'ass_check':function(eve){
                var msg;
                var value = eve._getCURElementsByName("encrypt_pass","input","TEMPLATE_FORM")[0].value;
                if( value.length < 6 ){
                    msg = "密钥长度不能小于6位";
                }
                return msg;
            }
        },
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");

function switch_version( value ) {
    if ( value == "V1" || value == "2C" ) {
        $(".community").show();
        $(".personal").hide();
    } else {
        $(".community").hide();
        $(".personal").show();
        var level_value = $("input[name='level']").val();
        switch_level( level_value );
    }
}

function switch_level( value ) {
    if ( value == "authPriv" ) {
        $(".auth_class").show();
        $(".encrypt_class").show();
    } else if ( value == "authNoPriv" ) {
        $(".auth_class").show();
        $(".encrypt_class").hide();
    } else {
        $(".auth_class").hide();
        $(".encrypt_class").hide();
    }
}

function do_other_when_edit_item( data_item ) {
    var input_radios = $('.input-radio');
    for(var i = 0; i < input_radios.length; i++) {
        if(data_item[input_radios[i].name] == input_radios[i].value) {
            input_radios[i].checked = true;
        }
    }
    if ( data_item.protocol_version =="V3" ) {
        switch_version( data_item.protocol_version );
        switch_level( data_item.level );
    } else {
        switch_version( data_item.protocol_version );
    }
}

function reset_form() {
    switch_version( "V1" );
}