/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/idps_strategy_custom.cgi",
    add_title: "添加策略项",
    update_title: "更新策略项",
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
    data_item.custom_set = data_item.custom_set_file;
    data_item.classtype = data_item.classtype_en;
    data_item.dst_port = data_item.dst_port.replace( /&/g, "\n" );
    if( data_item.protocol == "ip" ) {
        data_item.protocol = "any";
    }
    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function config_display_data(data_item) {
    /*CONFIGURATION VARIABLES - BEGIN*/
    data_item.custom_set = data_item.custom_set_name;
    data_item.classtype = data_item.classtype_cn;
    /*CONFIGURATION VARIABLES - END*/
    return data_item;
}

function create_other_opt_image_button(data_item_id, data_item) {
    var actions = "";
    /*CONFIGURATION VARIABLES - BEGIN*/

    /*CONFIGURATION VARIABLES - END*/
    return actions;
}

function do_other_when_edit_item( data_item ) {
    /*DO SOMETHING WHEN EDIT - BEGIN*/
    // document.getElementsByName("custom_set")[0].disabled = true;
    updateService('protocol', 'service_port', 'dst_port');
    document.getElementsByName("custom_set")[0].disabled = true;//不可更改
    /*DO SOMETHING WHEN EDIT - END*/
}

function do_other_when_reset_edit_box() {
    /*DO SOMETHING WHEN RESET - BEGIN*/
    // var input_texts = $('.input-text');
    // for(var i = 0; i < input_texts.length; i++){
    //     input_texts[i].value = "";
    // }
    document.getElementsByName("custom_set")[0].disabled = false;
    selectService('protocol', 'service_port', 'dst_port');
    /*DO SOMETHING WHEN RESET - END*/
}

function export_selected_items() {
    var selected_num = count_selected_items();
    if(selected_num > 0) {
        return true;
    } else {
        show_warn_mesg("未选择任何项目,操作失败");
        return false;
    }
}

function append_selected_items() {
    var selected_num = count_selected_items();
    if(selected_num > 0) {
        var sending_data = "";
        var detail_data = paging_holder.data_content.detail_data;
        var items_length = detail_data.length;
        for(var i = 0; i < items_length; i++) {
            if(detail_data[i].checked) {
                sending_data += "&" + detail_data[i].line;
            }
        }
        $("#export_selected_items").attr("value",sending_data);
        return true;
    } else {
        return false;//阻止点击链接下载文件
    }
}

function append_selected_items_to_link() {
    var selected_num = count_selected_items();
    if(selected_num > 0) {
        // var sending_data = "";
        // var detail_data = paging_holder.data_content.detail_data;
        // var items_length = detail_data.length;
        // for(var i = 0; i < items_length; i++) {
        //     if(detail_data[i].checked) {
        //         sending_data += "&" + detail_data[i].line + "=" + detail_data[i].line;
        //     }
        // }
        // var href = document.getElementById('export-all-link').href.split("?")[0];
        // href += "?ACTION=export_selected";
        // href += sending_data;
        // $("#export-all-link").attr("href",href);
        return true;
    } else {
        return false;
    }
}

function count_selected_items() {
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

/*Global Vsariable*/
var check = new ChinArk_forms();

var object = {
   'form_name':'TEMPLATE_FORM',
   'option':{
        'dst_port':{
            'type':'textarea',
            'required':'0',
            'check':'port|port_range',
        },
        'pattern':{
            'type':'textarea',
            'required':'0',
            'check':'note|',
            'ass_check': function( eve ) {
                var pattern = eve._getCURElementsByName('pattern', 'textarea', 'TEMPLATE_FORM')[0].value;
                var test_pattern = /\"/;
                if( test_pattern.test(pattern) ) {
                    return "输入含有非法字符";
                }
            }
        },
        'summary':{
            'type':'textarea',
            'required':'0',
            'check':'note|',
            'ass_check': function( eve ) {
                var summary = eve._getCURElementsByName('summary', 'textarea', 'TEMPLATE_FORM')[0].value;
                var test_pattern = /\"/;
                if( test_pattern.test(summary) ) {
                    return "输入含有非法字符";
                }
            }
        }
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");