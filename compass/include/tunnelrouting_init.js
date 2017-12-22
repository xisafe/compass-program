/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/tunnelrouting.cgi",
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

function edit_config_data(data_item) {
    data_item.routing_ip = data_item.routing_ip_1 + "+" + data_item.routing_ip_2;
    return data_item;
}

function config_display_data(data_item) {
    data_item.routing_ip = data_item.routing_ip_1;
    return data_item;
}

/*Global Vsariable*/
var check = new ChinArk_forms();

var object = {
   'form_name':'TEMPLATE_FORM',
   'option'   :{
        'dst_ip':{
            'type':'text',
            'required':'1',
            'check':'ip_mask|',
            'associated':'routing_ip',
            'ass_check':function(eve){
            }
        },
        'routing_ip':{
            'type':'select-one',
            'required':'1',
            'ass_check':function(eve){
                var msg="";
                var dev = eve._getCURElementsByName("routing_ip","select","TEMPLATE_FORM")[0].value;
                if (dev == ""){
                    msg = "必须选择一个路由网络";
                }
                return msg;
            }
        }
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");