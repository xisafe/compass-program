#!/usr/bin/perl
#==============================================================================#
#
# 描述: 添加规则列表规则页面
#
# 作者: 刘婷 (LiuTing), 914855723@qq.com
# 公司: capsheaf
# 历史:
#   2015.4.15 LiuTing创建
#   2015.05.27 JuLong Liu 修改
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'file_relevant_time.pl';


#=================初始化全局变量到init_data()中去初始化========================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my %system_settings;    #存放页面选择器的哈希
my $version_file_path;  #存放版本信息文件的路径
my $update_time;        #存放系统的更新时间
my $systemconfig;       #存放系统配置文件
my $update_system_online;#存放在线升级的文件
my $MSG;                #存放系统提示信息
my $STATUS_FLAG;
my $running_tag_file_path;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post请求传过来的变量
    &getcgihash(\%par);
    #初始化变量值
    &init_data();
    &make_file();
    &do_action();
    #&show_page();

}

sub init_data(){
    $need_reload_tag        = $conf_dir.'/add_list_need_reload';
    $systemconfig           = "${swroot}/systemconfig/settings";
    $imported_file_dir      = "/tmp/FWUpdateSystem.bin";
    $imported_file_check    = "/usr/local/bin/DecryptSystem";
    $imported_file_update   = "/usr/local/bin/UpdateSystem";
    $update_system_online   = "/usr/local/bin/AutogetUpdateSystem";
    $config_file            = "/var/efw/update/system/settings";
    $version_file_path      = "/etc/release";
    $running_tag_file_path  = "/var/efw/update/system/";
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/fileuploader.css" />
                    <script language="JavaScript" src="/include/fileuploader.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script type="text/javascript" src="/include/waiting.js"></script>
                    <script type="text/javascript" src="/include/systemupdate_controller.js"></script>
                    <script type="text/javascript">
                        function jump(des){
                            window.open(des);
                        }
                    </script>';
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-END==============================#
}

sub do_action() {
    #==一般ACTION只会通过一种方式传过来，开发者需要自己判断从哪种方式传过来==#
    my $action = $par{'ACTION'};
    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ( $action eq 'update_data_offline' ) {
        &begin();
        &update_data_offline();
        &ends();
    }
    elsif ( $action eq 'update_data_online' ) {
        &begin();
        &update_data_online();
        &ends();
    }
    #检测后台是否在升级
    elsif ( $action eq 'check_running' ) {
        &check_running();
    }
    
    if($action ne 'check_running'){
        &show_page();
    }
}

sub show_page() {
    #&showhttpheaders();
    &openpage($page_config{'系统升级'}, 1, $extraheader);
    &display_messagebox();
    &showoffline();
    # &showonline();#2016-09-19:去除在线升级功能
    &showinfo();
    &check_form();
    &show_message();
    &closepage();
}

sub show_version()
{
    $version = "";
    $updatetime = "";
    if (-e $version_file_path){
        open (VERSIONFILE, "$version_file_path");
        my $version_str = <VERSIONFILE>;
        $version = (split(" ",$version_str))[1];
        #$version = substr($version,1);
        $updatetime = &get_file_mtime_by_formatday( "$version_file_path",'-' );
        close(VERSIONFILE);
        }else{
            $version = "未检测到版本信息";
            $updatetime = "未检测到更新时间";
        }
        printf <<EOF  
        <table class = "ruleslist" style="width:100%;">
            <tr>
                <td class="add-div-type" width="20%" align = "center">当 前 版 本：</td>
                <td>$version</td>
            </tr>
            <tr>
                <td class="add-div-type" align = "center">更 新 时 间：</td>
                <td>$updatetime</td>
            </tr>
        </table>

EOF
;
}

sub begin(){
    printf <<EOF
    <script>
      RestartService("系统正在升级，请耐心等待.....");
    </script>
EOF
;
}
sub ends(){
    printf <<EOF
    <script>
      endmsg("");
    </script>
EOF
;
}


sub showoffline(){
    &openmybox('100%', 'left', _('离线升级'));
    &display_offline_body();
    &closebox();
}
# sub showonline(){
#     &openmybox('100%', 'left', _('在线升级'));
#     &display_online_body();
#     &closebox();
# }
sub showinfo(){
    &openmybox('100%', 'left', _('版本状态'));
    &show_version();
    &closebox();
}

sub openmybox
{
    $width = $_[0];
    $align = $_[1];
    $caption = $_[2];
    $id = $_[3];
    
    if($id ne '') {
        $id = "id=\"$id\"";
    }
    else {
        $id="";
    }
    
    
    printf <<EOF
<div class="containter-div">
EOF
    ;
    if ($caption) {
        printf <<EOF
         <span class="containter-div-header"><span style="display:block;float:left;margin-top:3px;">
         <img src='/images/applications-blue.png' />$caption</span>
         <span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;">
         </span></span>
EOF
;
    }
    else {
        printf <<EOF
        <span class="containter-div-header"><img src='/images/applications-blue.png' />&nbsp;</span>
EOF
;
    }
    printf <<EOF
    <div class="containter-div-content">
EOF
;
}


sub display_messagebox() {
    printf<<EOF
    <div id="mesg_box" class="container"></div>
EOF
    ;
}

sub show_message(){
        printf<<EOF
        <script>
        \$( document ).ready(function(){
                message_box.render();
                var uploader = new qq.FileUploader({
                    element: document.getElementById('file-uploader'),
                    allowedExtensions: ['bin'], 
                    action:'/cgi-bin/systemupdate_post.cgi',
                    debug:true,
                    onSubmit: function(id, fileName){},
                    onProgress: function(id, fileName, loaded, total){},
                    onComplete: function(id, fileName, responseJSON){
                        //\$(".qq-upload-list").hide();
                        //var tmp = fileName.split(".");
                        //var item_id = tmp[0];
                        //\$("#file-uploader").append('<div class="ctr_file" style="margin-top:10px;" id="'+item_id+'"><span>'+fileName+'</span><input style="margin-left:20px" src="/images/delete.png" title="删除" type="image" value="'+fileName+'" onclick="delete_file(this)"/></div>');
                    },
                    onCancel: function(id, fileName){},
                    showMessage: function(message){ alert(message); }
                });
EOF
;
    if($STATUS_FLAG == 0 ){
        if($MSG ne ''){
        printf<<EOF
        message_box.show_popup_mesg("$MSG");
EOF
;
        } 
    }
    if($STATUS_FLAG != 0 ){
        if($MSG ne ''){
        printf<<EOF
        message_box.show_popup_error_mesg("$MSG");
EOF
;
        }
    } 
        printf<<EOF
        });
        var message_box_config = {
            url: "/cgi-bin/message_manager.cgi",
            check_in_id: "mesg_box",
            panel_name: "mesg_box"
        }

        var message_box = new MessageManager( message_box_config );
        </script>
EOF
;
}


sub display_offline_body() {
    if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    printf <<EOF
        <form name ="update_offline_form" method="post" ACTION="$ENV{'SCRIPT_NAME'}" enctype="multipart/form-data" onsubmit="check_upload_file();">
        <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;"
            <tbody><tr class="odd">
                <td width="20%" class='add-div-width' vlign='center' align='center' rowspan ='1'>系统升级：</td>
                <td width = "80%">
                    <div style="font-size:12px;margin-left:20px">
                        <!--<input type="file" id="upload_file_lib" name="upload_file_lib" />-->
                        <div id="file-uploader" style="float:left;"></div>
                        <input type="submit" style="margin-top:25px;" class="net_button" value="立即升级">
                        <input type="hidden" name="ACTION" value="update_data_offline"/>
                    </div>
                </td>
            </tr>
            </tbody></table>
            <table  class="add-div-footer" width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
                <tbody>
                    <tr>
                    <td width="60%""></td><td width="40%" style='text-align: right;'>请到 <a onclick='jump("http://%s")' style='cursor:pointer' color='blue'>%s
                    </a>下载最新升级包！</td></tr>
                    </tr>
                </tbody>
            </table>
        </form>
EOF
    ,$system_settings{'COMPANY_WEBSITE'}
    ,$system_settings{'COMPANY_WEBSITE'}
;
}



sub import_data_check() {
    my ($status,$msg) = (-1,"");
    
    # my $cgi = new CGI; 
    # my $upload_file = $cgi->param('upload_file_lib');

    # #===将数据写到tmp目录下===#
    # my $count = 0;
    # open( UPLOAD, ">$imported_file_dir" ) or return ( $status, "打开写文件失败" );
    # binmode UPLOAD;
    # while( <$upload_file> ) {
        # $count++;
        # print UPLOAD;
    # }
    # close UPLOAD;

    system( "$imported_file_check" );
    $status = $?>>8;
    if ( $status == 0 ) {
        $msg = "";
    }
    elsif ( $status == 1 ) {
        $msg = "该模块未激活或已过期，不能完成升级功能，请激活后再升级!";
    }
    elsif($status == 2 ){
        $msg = "未检测到升级包，请重新上传升级包!";
    }
    elsif($status == 3 ){
        $msg = "获取升级包信息失败，请上传正确升级包!";
    } else {
        $msg = "检测失败";
    }

    return ($status,$msg);
}

sub update_data_offline() {
    ( $STATUS_FLAG, $MSG ) = &import_data_check();
    if ( $STATUS_FLAG == 0 ) {
        system("$imported_file_update");
        $STATUS_FLAG = $?>>8;
        if ($STATUS_FLAG == 0 ){
            open (VERSIONFILE, "$version_file_path");
            my $version_str = <VERSIONFILE>;
            $version = (split(" ",$version_str))[1];
            close(VERSIONFILE);
            $MSG = "升级成功，系统相应模块在系统重启后生效，请重新启动系统!";
        }
        elsif ( $STATUS_FLAG == 1 ){
            $MSG = "该模块未激活或已过期，不能完成升级功能，请激活后再升级!";
        }
        elsif ( $STATUS_FLAG == 2 ){
            $MSG = "检测到系统当前版本高于升级文件中的版本，如需升级请下载最新升级包!";
        }
        elsif ( $STATUS_FLAG == 3 ){
            $MSG = "系统升级失败，请确认升级包并重新升级!";
        } else {
            $MSG = "系统升级失败！";
        } 
    }
}

sub display_online_body(){
    my %slection,%settings;
    my $servername;
    if ( -f $config_file ) {
        &readhash( $config_file, \%settings );
        # $slection{$settings{'UPDATE_SCHEDULE'}} = "checked";
        # $slection{$settings{'DOWNLOADURL'}} = "checked";
        $servername = $settings{'DOWNLOADURL'};
    }
    # open (CONFIGFILE, "$config_file");
    # my $servername = <CONFIGFILE>;
    # $servername = substr($servername,12);
    # close(CONFIGFILE);

    $slection{'capsheaf'} = "checked";
    $slection{'customize_server'} = "";
    my $customize_server = "";

    if ( $par{'save_update_detail'} ne "" ) {
        $servername = $par{"downloadurl"}
    }

    if($servername ne "capsheaf" ){
        $slection{'capsheaf'} = "";
        $slection{'customize_server'} = "checked";
        $customize_server = $servername;
    }
    printf <<EOF
    <form name="UPDATE_ONLINE" method="post" ACTION="$ENV{'SCRIPT_NAME'}" enctype="multipart/form-data">
        <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
            <tbody><tr class="odd">
                <td width="20%" class="add-div-width" vlign="center" align="center" rowspan="1">升级服务器： </td>
                <td width="80%">
                    <div style="font-size:12px;margin-left:20px">
            <dl>
                <dd><input type="radio" name="downloadurl" value="capsheaf" $slection{'capsheaf'} }/>默认服务器</dd>
                <dd><input type="radio" name="downloadurl" value="SELF_DEFINE" $slection{'customize_server'}/>
                <input type="text" name="customize_server" value="$customize_server"/>(自定义服务器ip/域名)</dd>
            </dl>
                    </div>
                 </td>
            </tr>
            </tbody></table>
            <table  class="add-div-footer" width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
                <tbody>
                <tr><td align='center'><input type="submit" class="net_button" value="立即升级"></td>
                        <input type="hidden" name="ACTION" value="update_data_online"/>
            </tbody></table>
        </form>
EOF
;
}

sub check_values(){
    my ($status,$msg) = (-1,'');
    if( $par{'downloadurl'} eq 'capsheaf'){
        $status = 0;
    }

    if( $par{'downloadurl'} eq 'SELF_DEFINE'){
        if(!($par{'customize_server'})){
             $msg = "服务器名不能为空！";
             return ( $status, $msg );
         }
        if( validip($par{'customize_server'}) == 1 || validdomainname($par{'customize_server'}) == 1 ){
            $status = 0;
        }else{
            $msg = "您输入的必须是ip或domain类型";
        }
    }
    return ( $status, $msg );
}

sub update_data_online(){
    ( $STATUS_FLAG, $MSG ) = &check_values();
    if( $STATUS_FLAG == 0 ){
        my %new_settings;
        if ( -f $config_file ) {
            &readhash( $config_file, \%new_settings );
            if ($par{'downloadurl'} eq 'capsheaf'){
                $new_settings{'DOWNLOADURL'} = $par{'downloadurl'};
            }
            elsif ($par{'downloadurl'} eq 'SELF_DEFINE'){
                $new_settings{'DOWNLOADURL'} = $par{'customize_server'};
            }
            &writehash($config_file, \%new_settings);
        }
        system("$update_system_online");
        $STATUS_FLAG = $?>>8;
        if ($STATUS_FLAG == 0 ){
            $MSG = "升级成功，系统相应模块在系统重启后生效，请重新启动系统!";
        }elsif($STATUS_FLAG == 1){
            $MSG = "升级失败，请确认升级包并重新升级!";
        }elsif($STATUS_FLAG == 2){
            $MSG = "检测到系统当前版本高于升级文件中的版本，如需升级请下载最新升级包!";
        }elsif($STATUS_FLAG == 3){
            $MSG = "该模块未激活或已过期，不能完成升级功能，请激活后再升级!";
        }elsif($STATUS_FLAG == 4){
            $MSG = "下载升级包失败，请检查网络连接并重新升级!";
        }
    }
}


sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}
sub check_form(){

    printf <<EOF
    <script>
    var object = {
       'form_name':'update_offline_form',
       'option'   :{
            'upload_file_lib':{
                'type':'file',
                'required':'1',
                'check':'other|',
                'ass_check': function(){
                    var filename = \$( "#upload_file_lib" ).val();
                    var regx = /bin\$/;
                    if ( !filename.match( regx ) ) {
                        return "文件后缀名不正确";
                    }
               }
            }
        }
    };
    var check = new ChinArk_forms();
    //check._get_form_obj_table("update_offline_form");
    //check._main(object);
    function check_upload_file() {
        var error_count = check._submit_check( object, check );
        if ( error_count > 0 ) {
            return;
        }
        RestartService("正在上传...");
    }
    </script>
EOF
    ;
}

#检测后台是否在升级
sub check_running(){
    my %ret_data;
    if ( -e $running_tag_file_path.'downloading' ) {
        %ret_data->{'running'} = 1;
    }elsif(-e $running_tag_file_path.'updating'){
        %ret_data->{'running'} = 2;
    }else {
        %ret_data->{'running'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret;
    exit;
}