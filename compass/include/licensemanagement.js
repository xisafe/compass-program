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
    // message_manager.render();
    // list_panel.render();
    add_panel.render();
    add_panel.hide();
	
    // init();

    // add_panel.set_ass_list_panel( list_panel );
    // list_panel.set_ass_add_panel( add_panel );

    // add_panel.set_ass_message_manager( message_manager );
    // list_panel.set_ass_message_manager( message_manager );

    modify_license();

    style_render();
    // list_panel.update_info( true );

});

var ass_url = "/cgi-bin/licensemanagement.cgi";

var add_panel_config = {
    url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "add_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title_adding_prefix: "",
    rule_title_adding_icon:"uploadtray.png",
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 1             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons:{
        add:false,
        sub_items:[
            {
                enable: true,
                type: "hidden",
                name: "ACTION",
                value: "upgrade",

            },
            {
                enable: true,
                type: "hidden",
                name: "lib_type",
                value: "",

            },
            {
                enable: true,
                type: "submit",
                style: "",
                id: "update",
                functions: {
                    onclick:"check_update();"
                },

            }
        ],
        cancel: true,
    },
    event_handler: {              
        before_load_data: function( add_obj, data_item ) {
            
        },
        after_load_data: function( add_obj, data_item ) {
      
        },
        before_cancel_edit: function( add_obj ) {
     
        },
        after_cancel_edit: function( add_obj ) {
     
        },
        before_save_data: function( add_obj, sending_data ) {
          
        },
        after_save_data: function( add_obj, received_data ) {
          
        }
    },
    items_list: [ 
            {
            title: "选择升级文件(.dat)",
            sub_items: [
                {
                    enable: true,
                    type: "file",
                    value: "选择",
                    id:"file_lib",
                    name: "file_lib",
                    functions: {
                        onclick: ""
                    },
                    style:"width:300px;height:25px;border-radius:4px"
                }
                
            ]
        }]
};

var add_panel = new RuleAddPanel(add_panel_config);

function modify_license() {
    $(".modify_num,.modify_lib").click(function() {
        $(this).each(function() {
            var panel_name;
            if ($(this).hasClass('modify_num')) {
                panel_name = $(this).parent().parent().parent().children().eq(0).text();
            }else{
                panel_name = $(this).parent().prev().prev().text();
            }
            var update_type = $(this).attr('libtype');
            add_panel_config.footer_buttons.sub_items[1].value = update_type;

            add_panel_config.rule_title='导入升级包-'+panel_name;

            add_panel.render();
            add_panel.show();
        });
    });

}


function update_item( text,type ) {

    add_panel.render();
    add_panel.show();
}

function style_render() {

    $('.active_status').each(function() {
        if ($(this).text()=='0') {
            $(this).text('未激活').addClass('red');
        } else if($(this).text()=='1'){
            $(this).text('已激活').addClass('green');
        }
    });

    $('.deadtime').each(function() {
        if ($(this).text()!='') {
            $(this).text('有效日期：'+$(this).text());
        } 
    });
}

function check_update() {

    var file_lib=$('#file_lib').val();
    var bin_reg = /.dat$/;
    if (file_lib=='') {
        show_popup_alert_mesg('请选择文件');
    } else if(bin_reg.test(file_lib)==false){
        show_popup_alert_mesg('文件格式错误');
    }else{

        $("#add_panel_body_form_id_for_add_panel").submit();

        add_panel.hide();

        offline_update();
        
    }
}

var object = {
   'form_name':'add_panel_body_form_name_for_add_panel',
   'option'   :{
        'file_lib':{
            'type':'file',
            'required':'1',
            'ass_check':function(){
            }
        }
    }
}

var check = new ChinArk_forms();

function offline_update() {
    if(check._submit_check(object,check)){
        //do nothing
    } else {
        show_waiting_mesg("上传中...");
    }
}