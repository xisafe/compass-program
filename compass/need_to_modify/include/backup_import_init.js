$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    add_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    
    add_panel.set_ass_message_manager( message_manager );
    
    add_panel.hide();
    change_import_type();
    init_qquploader();
    change_server_type();
});
var add_panel;
var message_box_config = {
    url: "/cgi-bin/backup_import.cgi",
    check_in_id: "mesg_box_import",
    panel_name: "my_message_backup"
}
var message_manager;
var add_panel_config = {
    url: "/cgi-bin/backup_import.cgi",
    check_in_id: "panel_select_file",
    panel_name: "select_panel",
    rule_title: "",
    rule_title_adding_prefix:"",
    is_rule_title_icon: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
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
        sub_items: [{
            enable: true,
            type: "button",
            value: "导入",
            functions: {
                onclick: "import_remote();"
            }
        }]
    },
    items_list: [{
        title: "选择导入文件:",
        sub_items: [{
            enable: true,
            type: "select",
            style: "height:150px;width:820px;",
            id: "usable_member",
            name: "usable_member",
            multiple: true,
            options:[]
        }]
    }]
};


function add_rule( element ) {
    $("#username").attr("value","");
    $("#password_remote").attr("value","");
    add_panel.show();
}
//启用被禁用的用户
function enable_forbidded_item(e){
    var data = e.value.split("&");
    var id = data[0];
    var userstate = data[1];
    var sending_data = {
        ACTION: 'enable_forbidded_item',
        id: id,
        userstate: userstate
    };
    function ondatareceived(data) {
        list_panel.update_info(true);
    }
    do_request(sending_data, ondatareceived);
}
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/backup_import.cgi",
        data: sending_data,
        async: false,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//动态添加文件
function add_file(){
    $("#usable_member").find("option:selected").each(function(){
        $(this).remove();
        $("#member").append("<option selected value="+$(this).val()+">"+$(this).text()+"</option>");
    });
}
//删除节点
function delete_item(){
    $("#member").find("option:selected").each(function(){
        $(this).remove();
        $("#usable_member").append("<option value="+$(this).val()+">"+$(this).text()+"</option>");
    });
}
//选择导入方式
function change_import_type(){
    var type = $("input[name='import_type']:checked").val();
    if(type == "remote"){
        $("#tr_local").hide();
        $("#tr_remote").show();
    }else{
        $("#tr_local").show();
        $("#tr_remote").hide();
    }
}
//加载上传文件控件
function init_qquploader(){
    var uploader = new qq.FileUploader({
            element: document.getElementById('file-uploader'),
            allowedExtensions: ['dat'], 
            action:'/cgi-bin/backup_import_new_post.cgi',
            debug:true,
            onSubmit: function(id, fileName){},
            onProgress: function(id, fileName, loaded, total){},
            onComplete: function(id, fileName, responseJSON){
                $(".qq-upload-list").hide();
                var tmp = fileName.split(".");
                var item_id = tmp[0];
                $("#file-uploader").append('<div class="ctr_file" style="margin-top:10px;" id="'+item_id+'"><span>'+fileName+'</span><input style="margin-left:20px" src="/images/delete.png" title="删除" type="image" value="'+fileName+'" onclick="delete_file(this)"/></div>');
            },
            onCancel: function(id, fileName){},
            showMessage: function(message){ alert(message); }
        });
}
//导入控制函数
function do_import(){
    var type = $("input[name='import_type']:checked").val();
	var note = $("#note").val();
	if(/[~!@#$%^&*()<>]/.test(note)) {
		message_manager.show_popup_error_mesg("注释信息包含非法字符!!!");
		return false;
	}
    if(type == "remote"){
        add_panel.show();
        load_useable_filelist();
    }else{
        import_local();
    }
}
//加载可导入文件列表
function load_useable_filelist(){
    var remoteType = $("input[name='REMOTE_TYPE']:checked").val();
    var remote_addr;
    var userName;
    var password;
    if(remoteType == "ftp"){
        remote_addr = $("#SERVER_ADDR_FTP").val();
        userName = $("#USER_NAME_FTP").val();
        password = $("#PWD_FTP").val();
    }else{
        remote_addr = $("#SERVER_ADDR_CAPSHEAF").val();
        userName = $("#USER_NAME_CAPSHEAF").val();
        password = $("#PWD_CAPSHEAF").val();
    }
    
    var note = $("#note").val();
    
    var sending_data = {
        ACTION: 'load_useable_filelist',
        remoteType: remoteType,
        remoteAddr: remote_addr,
        userName: userName,
        password: password,
        note: note
    };
    function ondatareceived(data) {
        var file_names = [];
        file_names = data.split(",");
        $("#usable_member").empty();
        for(var i=0;i<file_names.length;i++){
            $("#usable_member").append("<option value="+file_names[i]+">"+file_names[i]+"</option>");
        }
    }
    do_request(sending_data, ondatareceived);
}
//删除文件
function delete_file(e){
    var fileName = e.value;
    var sending_data = {
        ACTION: 'delete_file',
        fileName: fileName
    };
    function ondatareceived(data) {
        var tmp = data.split(".");
        var id = "#"+tmp[0];
        $(id).remove();
    }
    do_request(sending_data, ondatareceived);
}
//远程导入
function import_remote(){
    add_panel.hide();
    var temp = $("#usable_member").val();
    var note = $("#note").val();
    var selected_files = temp.join(" ");
    var sending_data = {
        ACTION: 'import_remote',
        fileNames: selected_files,
        note: note
    };
    function ondatareceived(data) {
        if(data == "5"){
            message_manager.show_popup_note_mesg("当前备份数已达到系统最大限制，如需备份，请先删除部分备份文件");
        }else{
            message_manager.show_popup_note_mesg("远程导入成功");
        }
        $("#note").attr("value","");
    }
    do_request(sending_data, ondatareceived);
}
//本地导入
function import_local(){
    var note = $("#note").val();
    var sending_data = {
        ACTION: 'import_local',
        note: note
    };
    function ondatareceived(data) {
        $(".ctr_file").remove();
        if(data == "0"){
            message_manager.show_popup_note_mesg("本地导入成功");
        }else if(data == "1"){
            message_manager.show_popup_error_mesg("请先选择导入文件");
        }else if(data == "3"){
            message_manager.show_popup_error_mesg("上传的文件不正确");
        }else if(data == "4"){
            message_manager.show_popup_error_mesg("上传的部分文件不正确");
        }else if(data == "5"){
            message_manager.show_popup_error_mesg("当前备份数已达到系统最大限制，如需备份，请先删除部分备份文件");
        }
        $("#note").attr("value","");
    }
    do_request(sending_data, ondatareceived);
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