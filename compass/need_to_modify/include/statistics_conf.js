/*
 * 描述: 类型统计页面
 *
 * 作者: pujiao
 * 公司: Capsheaf
 * 历史：
 *       2016.08.08  pujiao创建
 */
$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    message_manager = new MessageManager( message_box_config );
   
    /* 渲染面板 */
    add_panel.render();
   

    message_manager.render();
    /* 设置面板关联 */
    add_panel.set_ass_message_manager( message_manager );
    read_data();   
});
var message_manager;
var add_panel;
var message_box_config = {
    url: "/cgi-bin/statistics_conf.cgi",
    check_in_id: "mesg_box_tmp",
    panel_name: "my_message_box",
};
var add_panel_config = {
    url: "/cgi-bin/statistics_conf.cgi",
    check_in_id: "panel_flow_list",
    panel_name: "add_panel",
    rule_title: "统计配置",
    is_modal: false,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    footer_buttons: {              
        add: false,
        cancel: false,
        import: false,
        sub_items: [               
            {
                enable: true,
                type: "button",
                value: "保存",
                functions: {       
                    onclick: "save_data()"
                }
            }
        ]
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {


        },
        after_save_data:function( add_obj,data_item ) {
       
        },
        before_load_data: function( add_obj,data_item ) {
        
        },
        after_load_data: function( add_obj,data_item ) {
           
          
        },
        after_cancel_edit: function( add_obj ) {
            
        }

        
    },
    is_panel_stretchable: false,
    is_panel_closable: false,
    items_list: [
       
        {
            title: "是否启用:",
            sub_items: [
                {       
                        enable:true,
                        id:"enable_yes",
                        name:"enable",
                        label:"是",
                        type:"radio",
                        // checked:true,
                        value:"1",
                        functions:{
                             // onclick: "enable_function(this.value);"
                        }
                }, 
                {       
                        enable:true,
                        id:"enable_no",
                        name:"enable",
                        label:"否",
                        type:"radio",
                        value:"0",
                        functions:{
                             // onclick: "enable_function(this.value);"
                        },
                }
           
              
            ]
        },
        // {
        //     title:"待检测设备:",
        //     enable:false,
        //     class:"device",
        //     sub_items:[{
        //         enable: false,
        //         type:"select",
        //         id:"device",
        //         name:"device",
        //         check:{

        //         }
        //     }]
        // },
        {
            title: "IP地址*:",
            sub_items: [
                {
                    enable: true,
                    type: "textarea",
                    style: "", 
                    id:"ip",
                    tip:"待检测流量的IP/网段，总IP数不能超过131070，超过部分将自动忽略，如192.168.1.0/24 或192.168.11.5",
                    name: "ip",
                    value:"",
                    functions:{
                        "onclick": ""
                    },
                    check: {
                        type:'textarea',
                        required:'1',
                        check:"ip|ip_addr_segment",
                        ass_check:function( check ){
                            var ip = $('#ip').val()
                            var ip_arr = ip.split('\n')
                            var msg = ip_arr.length > 131070 ? "总IP数不能超过131070":''
                            var mask = 0
                            for(var i = 0;i<ip_arr.length;i++){
                                var ip_mask = ip_arr[i].split('\/')
                                if (ip_mask[1]<16) {
                                    mask++
                                    if (mask>2) {
                                        msg ="掩码低于16的网段不能超过2个"
                                        break
                                    }
                                }
                            }
                            return msg
                        }
                    }
                }
                
            ]
        }
    ]
};
// function enable_function(val){
//     if(val == 1){
//         $(".device").show();
//     }else{
//         $(".device").hide();
//     }
// }
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/statistics_conf.cgi",
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
function read_data(){
    // 获取数据

    var sending_data = {
        ACTION: "read_data"
    }

    function ondatareceived( data ) {
        
        $("#ip").val(data.data_content.join("\n"));
        if(data.enable == 1){
            $("#enable_yes").attr("checked",true);
            // $(".device").show();
        }
        else{
            $("#enable_no").attr("checked",true);
            // $(".device").hide();
        }

        // var str = "<option value='请选择' selected disabled>请选择</option>";
        // var selected = data.label.trim().split(",");
        // selected.shift();
        
        // for(var j = 0; j < selected.length ; j++){
        //         for(var i = 0;i < data.device.length; i++){
        //             if( selected[j].toLowerCase() == data.device[i].iface ){
        //                 data.device[i].selected = true;
        //             }            
        //     }
        // }

        // for(var i = 0;i < data.device.length; i++){
        //     var flag = '';
        //     if(data.device[i].selected)
        //         flag = ' selected '
        //     str += "<option value='"+data.device[i].iface+"' "+flag+">"+data.device[i].iface+ "&nbsp;&nbsp;&nbsp;&nbsp;" + data.device[i].mac+"</option>";  
        // }
        // $("#device").html("");
        // $("#device").append(str);
    }

   do_request( sending_data, ondatareceived );
}

function save_data(){
    var data = $("#ip").val().trim().replace(/\n/g,"&");
    var enable = $("input[name='enable']:checked").val();
    // var device = $("#device").val();
    if(data.length == 0){
        message_manager.show_popup_error_mesg("输入IP地址！");
    }
    else{
       var sending_data = {
        ACTION: "save_data",
        data: data,
        enable:enable
        // device:device
    }

    function ondatareceived( data ) {
       
        if(data.status == 1){
            message_manager.show_note_mesg("保存成功");
        }
        else{   
            message_manager.show_popup_error_mesg("保存失败");
        }
        window.location=('/cgi-bin/statistics_conf.cgi');
    }

    do_request( sending_data, ondatareceived ); 
    }
    
}




