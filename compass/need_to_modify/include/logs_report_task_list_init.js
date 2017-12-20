/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/logs_report_task.cgi",
    add_title: "新建",
    update_title: "更新",
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

/*Global Vsariable*/
var check = new ChinArk_forms();

var object = {
   'form_name':'TEMPLATE_FORM',
   'option':{
        'report_name':{
            'type':'text',
            'required':'1',
            'check':'note',
            'ass_check':function(eve){
                var msg="";
                var viewsize = eve._getCURElementsByName("report_name","input","TEMPLATE_FORM")[0].value;
                if (viewsize.length > 20) {
                msg = "请输入1-20字符";
                }
                return msg;
            }
        },
        'submitter':{
            'type':'text',
            'required':'1',
            'check':'note',
            'ass_check':function(eve){
                var msg="";
                var viewsize = eve._getCURElementsByName("submitter","input","TEMPLATE_FORM")[0].value;
                if (viewsize.length > 20) {
                msg = "请输入1-20字符";
                }
                return msg;
            }
        },
        'submit_institution':{
            'type':'text',
            'required':'1',
            'check':'note',
            'ass_check':function(eve){
                var msg="";
                var viewsize = eve._getCURElementsByName("submit_institution","input","TEMPLATE_FORM")[0].value;
                if (viewsize.length > 40) {
                msg = "请输入1-40字符";
                }
                return msg;
            }
        }, 
        'topN':{
            'type':'text',
            'required':'1',
            'check':'num',
            'ass_check':function(eve){
                var msg="";
                var viewsize = eve._getCURElementsByName("topN","input","TEMPLATE_FORM")[0].value;
                if (viewsize<5 || viewsize > 100) {
                msg = "请输入5-100的整数";
                }
                return msg;
            }
        }
    }
}

// check._get_form_obj_table("TEMPLATE_FORM");