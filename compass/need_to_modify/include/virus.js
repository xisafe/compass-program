/*
 * 描述: 测试添加模板和列表模板类
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2014.09.23 WangLin创建
 */

/*
 * 注释<1>：此文档的“配置对象”指new PagingHolder时传入的对象
 */

$( document ).ready(function() {	
    /* 渲染面板 */
     message_manager.render();
     lib_panel.render();
     lib_panel.hide();   
   
    (function() {
        //控制应用面板是否显示
        var control = parseInt( $("#apply-control").val() );
        if(control) {
            message_manager.show_apply_mesg();
        }

        //为form表单绑定检测方法
        var object = {
            "form_name": "virus-form",
            option: {
                'depth_min': {
                    'type': 'text',
                    'required': '1',
                    'check': 'int|',
                    'ass_check': function(eve){ 
                     
                      var min = $("#depth_min").val();  
                      if( min == "") {
                             return "该项不能为空";
                         }
                      if(min>102400){
                             return "该项不能超过102400KB";
                         }  
                      if(min<0){
                         return "该项不能为负数";
                      }                   
                    }
                },
                'depth_max': {
                    'type': 'text',
                    'required': '1',
                    'check': 'num|',
                    'ass_check': function(eve){  

                      var min = $("#depth_min").val();
                      var max = $("#depth_max").val();  
                      if( max == "") {
                             return "该项不能为空";
                         }  
                      if(max>102400){
                         return "该项不能超过102400KB";
                      }
                      if(min>max){
                         return "该项输入不合法，请重新输入";
                      }                      
                    }
                },
                'filetypes':{
                  'type':'text',
                  'required':'1',
                  'check': 'other|',
                  'other_reg':'/\[\^\]/',
                  'ass_check': function(eve){
                      var text = $("#setvirus-filetype").val();
                      if(!text){
                        $("div#virus-formfiletypesCHINARK_ERROR_TIP").remove();
                      }
                  }
                },
                'clamav_action': {
                    /*'type': 'select-one',
                    'required': '1',
                    'check': 'other|',*/
                    //'other_reg': '/.*/'
                },
                'proto': {
                    'type': 'checkbox',
                    'required': '1',
                    'check': 'check|',
                    'other_reg': '/.*/',
                     'ass_check': function(eve){

                         var number=$("input[name='proto']:checked");  
                         if(number.length==0){  
                            return "请至少选择一个" ;  
                        }
                     }
                }

            }
        }
        var check = new ChinArk_forms();
        check._main(object);
     })();
   var text = $("#setvirus-filetype").val();
                      if(text==""){
                        
                      }else{
                        $("div#virus-formfiletypesCHINARK_ERROR_TIP").remove();
                      }
    // init_tree();
});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/virus.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}


var lib_panel_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "panel_rule_lib",         // ***必填***，确定面板挂载在哪里 
    page_size: 0,                  //===可选===，定义页大小，默认是15 
    panel_name: "lib_panel",       // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置文件类型",
    is_panel_stretchable:false,
    is_panel_closable: true,
    is_paging_tools: false,
    is_first_load: true,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 20
    },
    title_icon:"add.png",
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
     
        },
        after_load_data: function( list_obj,data_item ) {
            
        }
    },
    panel_header: [],
    bottom_extend_widgets: {
        class: "add-panel-footer",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_checked_for_jstree(lib_panel,'setvirus-filetype','file');"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "lib_panel.hide();"
            }
        }]
    }

};

var lib_panel = new PagingHolder( lib_panel_config );
var message_manager = new MessageManager( message_box_config );

function show_lib_panel(){
    var sending_data = {
        ACTION: 'read_data'
    };

    function ondatareceived(data) {

        change_jstree_data('setvirus-filetype',data.file_type_data.children);      
        jstree_render(lib_panel,data.file_type_data,'file');       
        lib_panel.show();

    }
    do_request(sending_data, ondatareceived);
}