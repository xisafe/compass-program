/*Configurate those variables to control the pages*/
/*CONFIGURATION VARIABLES - BEGIN*/
var paging_holder = {
    url: "/cgi-bin/url_filter.cgi",
    add_title: "添加策略",
    update_title: "更新策略",
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
            'form_name':'TEMPLATE_FORM',//这里填写表单的名字
            'option'   :{
                'policy_name':{
                    'type':'text',
                    'required':'0',
                    'check':'name|',
                    'ass_check':function(eve){//这个eve对象是ChinArk_forms对象，如果需要用到其中的函数，可以填写，不一定用eve这个名字，可以用其他名字
                        var msg = "";
                        //此处添加你自己的代码,如果要返回错误消息，就填在msg中，如果没有错误，将msg置空就OK了
                        var name = eve._getCURElementsByName("policy_name","input","TEMPLATE_FORM")[0].value;
                        if(name.size>20){
                            msg = "策略名称最长为20个字符";
                        }
                        return msg;
                    }
                },
                'blacklist_user':{
                    'type':'textarea',
                    'required':'0',
                    'check':'other',
                    'other_reg':'!/^\$/',
                    'ass_check':function(eve){
                        var msg = "";
                        var add = eve._getCURElementsByName("blacklist_user","textarea","TEMPLATE_FORM")[0].value;
                        var test = add.split("\n");
                        for(var i=0;i<test.length;i++){
                            test[i] = eve.trim(test[i]);
                            if(!eve.validip(test[i]) && !eve.rangeip(test[i]) && !eve.validsegment(test[i])){
                                msg = "请输入正确的用户地址";
                                break;
                            }
                        }
                        return msg;
                    }
                },
                'blacklist_url':{
                    'type':'textarea',
                    'required':'1',
                    'check':'other',
                    'other_reg':'!/^\$/',
                    'ass_check':function(eve){
                        var msg = "";
                        var add = eve._getCURElementsByName("blacklist_url","textarea","TEMPLATE_FORM")[0].value;
                        var test = add.split("\n");
                        //var strRegex = /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i;
                        //var re=new RegExp(strRegex);
                        for(var i=0;i<test.length;i++){
                            test[i] = eve.trim(test[i]);
                            /* if(!eve.validurl(test[i])){
                                msg = "请输入正确的url地址";
                                break;
                            } */
                            /* var http = test[i].substr(0,4);
                            if(http == "http"){
                                msg = "输入的url不必带协议号";
                                break;
                            } */
                            if(test[i].length>128){
                                msg = "单个url的长度小于128字节";
                                break;
                            }
                        }
                        return msg;
                    }
                },
                'discription':{
                    'type':'text',
                    'required':'0',
                    'check':'other|',
                    'other_reg':'/\.*/',
                    'ass_check':function(eve){
                        var msg = "";
                        var name = eve._getCURElementsByName("policy_name","input","TEMPLATE_FORM")[0].value;
                        if(name.size>100){
                            msg = "策略描述最长为100个字符";
                        }
                        return msg;
                    }
                }
            }
        }

// check._get_form_obj_table("TEMPLATE_FORM");