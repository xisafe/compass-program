$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    add_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    
    add_panel.set_ass_message_manager( message_manager );
    
    add_panel.hide();
    change_server();
    change_server_type();
});
var add_panel;
var message_box_config = {
    url: "/cgi-bin/backup_newcreat.cgi",
    check_in_id: "mesg_box_backup",
    panel_name: "my_message_backup"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/backup_newcreat.cgi",
    check_in_id: "panel_backup_remote",
    panel_name: "remote_panel",
    rule_title: "远程FTP导出",
    rule_title_adding_prefix:"",
    is_rule_title_icon: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    event_handler: {
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
            
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    footer_buttons: {
        sub_items: [
            {
                enable: true,
                type: "button",
                value: "确定",
                functions: {
                    onclick: "export_remote();"
                }
            }
        ]
    },
    items_list: [
        {
            title: "远程服务器IP地址:",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "remote_addr_export",
                    name: "remote_addr_export",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'ip|',
                        ass_check:function(eve){
                            
                        }
                    }
                }
            ]
        },
        {
            title: "用户名:",
            sub_items: [
                {
                    enable: true,
                    type: "text",
                    id: "username_export",
                    name: "username_export",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check: 'name|',
                        ass_check: function( check ) {
                            
                        }
                    }
                }
            ]
        },
        {
            title: "密码:",
            sub_items: [
                {
                    enable: true,
                    type: "password",
                    id: "password_export",
                    name: "password_export",
                    value: "",
                    functions: {
                    },
                    check: {
                        type: "password",
                        required: 0,
                        check:'other',
                        other_reg:'!/^\$/',
                        ass_check:function(eve){
                            var pwd = $("#password_export").val();
                            if(pwd.length < 1 || pwd.length > 20){
                                return "请输入1-20个字符！";
                            }
                        }
                    }
                }
            ]
        }
    ]
};


function add_rule( element ) {
    $("#username").attr("value","");
    $("#password_remote").attr("value","");
    add_panel.show();
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/backup_newcreat.cgi",
        data: sending_data,
        async: false,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//选择多项
function select_all(){
    if($("#cbk_checkall").attr("checked")){
        $("input[name='cbk_checkone']").each(function() {
            $(this).attr("checked", true);
        }); 
    }else{
        $("input[name='cbk_checkone']").each(function() {
            $(this).attr("checked", false);
        });
    }
    
}
//获取所有选择项
function get_selected_items(){
    var file_names = [];
    $("input[name='cbk_checkone']").each(function() {
        if($(this).attr("checked")){
            file_names.push(this.value);
        }
    });
    return file_names;
}
//本地导出
function export_local(){
    var str_filenames = "";
    var file_names = get_selected_items();
    str_filenames = file_names.join(" ");
    var sending_data = {
        ACTION: 'export_local',
        file_names: str_filenames
    };
    function ondatareceived(data) {
        
    }
    if(file_names.length < 1){
        message_manager.show_popup_note_mesg("请先选择备份项");
    }else{
        do_request(sending_data, ondatareceived);
    }
}
function append_selected_items_to_link() {
    var str_filenames = "";
    var file_names = get_selected_items();
    str_filenames = file_names.join(" ");
    var selected_num = file_names.length;
    if(selected_num > 0) {
        var sending_data = "";
        sending_data += "&file_names="+str_filenames;
        var href = document.getElementById('export-all-link').href.split("?")[0];
        href += "?ACTION=export_local";
        href += sending_data;
        $("#export-all-link").attr("href",href);
        return true;
    } else {
        return false;
    }
}
function exportFile(){
    // e.preventDefault()
    var fileNames = get_selected_items().join(' ')
    if (fileNames) {
        $("input[name='file_names']").val(fileNames)
        // var sending_data={
        //     ACTION:'export_local',
        //     file_names:fileNames
        // }
        // function ondatareceived(data) {
            
        // }
        // do_request(sending_data, ondatareceived);
    }/*else{
        e.preventDefault()
        message_manager.show_popup_note_mesg("请先选择备份项")
    }*/
}
//远程导出
function export_remote(){
    var str_filenames = "";
    var file_names = get_selected_items();
    str_filenames = file_names.join(" ");
    var remote_addr_export = $("#remote_addr_export").val();
    var username_export = $("#username_export").val();
    var password_export = $("#password_export").val();
    var sending_data = {
        ACTION: 'export_remote',
        remote_addr_export: remote_addr_export,
        username_export: username_export,
        password_export: password_export,
        file_names: str_filenames
    };
    function ondatareceived(data) {
        message_manager.show_popup_note_mesg(data);
    }
    if(file_names.length < 1){
        message_manager.show_popup_note_mesg("请先选择备份项");
    }
    else{
        if ( add_panel.is_input_data_correct() ) {
            add_panel.hide();
            do_request(sending_data, ondatareceived);
        } else {
            message_manager.show_popup_error_mesg("请正确填写表单");
        }
    }
}
//改变远程服务器的展示状态
function change_server(){
    if($("#REMOTE_ENABLE").attr("checked")){
        $("#remote_server").show();
    }else{
        $("#remote_server").hide();
    }
}
//改变远程服务器方式
function change_server_type(){
    var type = $("input[name='REMOTE_TYPE']:checked").val();
    if(type == "ftp"){
        $("#content_ftp").show();
        $("#content_capsheaf").hide();
    }else{
        $("#content_ftp").hide();
        $("#content_capsheaf").show();
    }
}