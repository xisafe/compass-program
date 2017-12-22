#!/usr/bin/perl
#==============================================================================#
#
# 描述: 添加规则列表规则页面
#
# 作者: 刘婷 (LiuTing), 914855723@qq.com
# 公司: capsheaf
# 历史:
#   2015.4.15 LiuTing创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'file_relevant_time.pl';

#=================初始化全局变量到init_data()中去初始化========================#
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my %system_settings;
my $version_file;
my $update_time;
my $oldversion;
my $systemconfig;
my %system_settings;
my $save_update_online;
my $update_system_online;
my $downloadurl_oline;
my $save_servername ;
my $save_update_detail;
my $version;
my $MSG;                #存放系统提示信息
my $STATUS_FLAG;
my $running_tag_file_path;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post请求传过来的变量
    &getcgihash(\%par);
    #获取get请求传过来的变量
    &get_query_hash(\%query);
    #初始化变量值
    &init_data();
    &make_file();
    &do_action();
}

sub init_data(){
    $systemconfig          = "${swroot}/systemconfig/settings";
    $imported_file_dir     = "/tmp/FWUpdateIpsRules.bin";
    $imported_file_check   = "/usr/local/bin/DecryptIpsRules";
    $imported_file_update  = "/usr/local/bin/UpdateIpsRules";
    $save_update_online    = "/usr/local/bin/restartruleupdate";
    $update_system_online  = "/usr/local/bin/AutogetUpdateIpsrules";
    $config_file           = "/var/efw/update/ipsrules/settings";
    $version_file_check    = "/var/license/ipsrules/unactivetag";
    $version_file          = "/var/efw/update/ipsrules/release";
    $old_version_file      = "/var/efw/update/ipsrules/release.old";
    $save_update_detail    ="/usr/local/bin/restartruleupdate -m ipsrules";
    $running_tag_file_path = "/var/efw/update/ipsrules/";
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/fileuploader.css" />
                    <script language="JavaScript" src="/include/fileuploader.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script type="text/javascript" src="/include/waiting.js"></script>
                    <script type="text/javascript" src="/include/ipsrulesupdate_controller.js"></script>
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
    my $query_action = $query{'ACTION'};
    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($par{'save_update_detail'} ne "" ) {
        `echo haha >/tmp/haha`;
        &save_update_detail();
    }elsif ($par{'update_data_online'} !~ /^$/) {
        &update_data_online();
    }elsif($action eq 'update_data_offline'){
        &begin();
        &update_data_offline();
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
    &openpage($page_config{'病毒库升级'}, 1, $extraheader);
    &display_messagebox();
    &showoffline();
    # &showonline();
    &showinfo();
    &check_form();
    &show_message();
    &closepage();
}


sub show_version_info()
{
    my $name = "IPS 特 征 库";
    printf<<EOF
    <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;" >
    <thead>
        <tr class = "odd">
            <td class="add-div-type" width="20%" vlign="center" align="center">模 块 名 称</td>
            <td class="add-div-type" width="20%" vlign="center" align="center">当 前 版 本</td>
            <td class="add-div-type" width="20%" vlign="center" align="center">更 新 时 间</td>
            <td class="add-div-type" width="20%" vlign="center" align="center">历 史 版 本</td>
        </tr>
    </thead>

EOF
    ;
    if( !(-e $version_file_check ) ){
        open (VERSIONFILE, "$version_file");
        $version = <VERSIONFILE>;
        $update_time = &get_file_mtime_by_formatday( "$version_file",'-' );
        close(VERSIONFILE);
        open (OLDVERSIONFILE, "$old_version_file");
        $oldversion = <OLDVERSIONFILE>;
        close(OLDVERSIONFILE);
        if(!$oldversion){
            $oldversion = $version;
        }
    }else{
        $version = "未 激 活";
        $update_time = "未 激 活";
        $oldversion = "未 激 活";
    }
    printf <<EOF
    <tbody>
            <tr class = "odd">
            <td width="20%" vlign="center" align="center">$name</td>
            <td width="20%" vlign="center" align="center">$version</td>
            <td width="20%" vlign="center" align="center">$update_time</td>
            <td width="20%" vlign="center" align="center">$oldversion</td>
        </tr>
    </tbody>
    </table>
EOF
;
}

sub begin(){
    printf <<EOF
    <script>
      RestartService("IPS特征库正在升级，请耐心等待.....");
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
sub showonline(){
    &openmybox('100%', 'left', _('在线升级'));
    &display_online_body();
    &closebox();
}
sub showinfo(){
    &openmybox('100%', 'left', _('版本信息'));
    &show_version_info();
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
     <span class="containter-div-header"><span style="display:block;float:left;margin-top:3px;"><img src='/images/applications-blue.png' />$caption</span><span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;"></span></span>
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
        <form name="update_offline_form" method="post" ACTION="$ENV{'SCRIPT_NAME'}" enctype="multipart/form-data" onsubmit="check_upload_file();">
        <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
            <tbody><tr class="odd">
                <td width="20%" class='add-div-width' vlign='center' align='center' rowspan ='1'>IPS特征库升级：</td>
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
                <td width="78%""></td><td width="22%">请到<a onclick='jump("http://%s")' style='cursor:pointer' color='blue'>%s
                </a>下载最新升级包！</td></tr>
                </tr>
        </tbody></table>
        </form>
EOF
    ,$system_settings{'COMPANY_WEBSITE'}
    ,$system_settings{'COMPANY_WEBSITE'}
;
}
sub display_online_body(){
    my %slection,%settings;
    my $downloadurl, $update_schedule;
    if ( -f $config_file ) {
        &readhash( "$config_file", \%settings );
        $downloadurl = $settings{'DOWNLOADURL'};
        $update_schedule = $settings{'UPDATE_SCHEDULE'};
        if(!$update_schedule){
            $update_schedule = "off";
        }
    }
    my $default_checked = "";
    my $self_define_checked = "";
    my $customize_server = "";

    if($downloadurl eq "capsheaf"){
        $default_checked = "checked";
    }else{
        $self_define_checked = "checked";
        $customize_server = $downloadurl;
    }
    $slection{$update_schedule} = "checked";

    printf <<EOF
    <form name="UPDATE_ONLINE" method="post" ACTION="$ENV{'SCRIPT_NAME'}" enctype="multipart/form-data">
        <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
            <tbody><tr class="odd">
                <td width="20%" class="add-div-width" vlign="center" align="center" rowspan="1">升级服务器： </td>
                <td width="80%">
                    <div style="font-size:12px;margin-left:20px">
            <dl>
                <dd><input type="radio" name="downloadurl" value="capsheaf" $default_checked }/>默认服务器</dd>
                <dd><input type="radio" name="downloadurl" value="SELF_DEFINE" $self_define_checked />
                <input type="text" name="customize_server" value="$customize_server"/>(自定义服务器ip/域名)</dd>
            </dl>
                    </div>
                 </td>
            </tr>
                <tr class="odd">
                  <td width="20%" class="add-div-width" vlign="center" align="center" rowspan="1">升级周期： </td>
                  <td width="80%">
                    <div style="font-size:12px;margin-left:20px">
                        <input id="enable" value="off" type="radio" name="update_schedule" $slection{'off'}/><label for="enable">不启用</label>
                        <input id="daily" style="margin-left:5px;" value="daily" type="radio"  name="update_schedule" $slection{'daily'}/><label for="daily">每天</label>
                        <input id="weekly" style="margin-left:5px;" value="weekly" type="radio" name="update_schedule" $slection{'weekly'}/><label for="weekly">每周</label>
                        <input id="monthly" style="margin-left:5px;" value="monthly" type="radio"  name="update_schedule" $slection{'monthly'}/><label for="monthly">每月</label>
                        <!--<input id="yearly" value="yearly" type="radio" name="update_schedule" $slection{'yearly'}/><label for="yearly">每年</label>-->
            </tr>
            </tbody></table>
            <table  class="add-div-footer" width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
                <tr>
                <td align='center' >
                <input class='net_button' type='submit' name='save_update_detail' value='保 存' />&nbsp;&nbsp;&nbsp;&nbsp;
                <input class='net_button' type='submit' name='update_data_online' value='立即升级' /></td>
                </tr>
            </tbody></table>
        </form>
EOF
;
}

sub data_check_offline() {
    my ( $status, $msg ) = ( -1, "" );
    
    # my $cgi = new CGI; 
    # my $upload_file = $cgi->param('upload_file_lib');


    # #===将数据写到tmp目录下===#
    # my $count = 0;
    # open( UPLOAD, ">$imported_file_dir" ) or return ( $status, "打开写文件失败" );
    # binmode UPLOAD;
    # while( <$upload_file> ) {
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
        $msg = "获取升级包信息失败，请上传正确升级包。";
    } else {
        $msg = "检测失败";
    }

    return ($status,$msg);
}


sub update_data_offline(){
    ( $STATUS_FLAG, $MSG ) = &data_check_offline();
    if ( $STATUS_FLAG == 0 ) {
        system("$imported_file_update");
        $STATUS_FLAG = $?>>8;
        if ($STATUS_FLAG == 0 ){
            open (VERSIONFILE, "$version_file");
            my $version_str = <VERSIONFILE>;
            $version = (split(" ",$version_str))[1];
            close(VERSIONFILE);
            $MSG = "升级成功，系统相应模块在系统重启后生效，请重新启动系统!";
        }
        elsif ( $STATUS_FLAG == 1 ){
            $MSG = "该模块未激活或已过期，不能完成升级功能，请激活后再升级!";
        }
        elsif ( $STATUS_FLAG == 2 ){
            $MSG = "IPS特征库升级失败，请确认升级包并重新升级!";
        }else {
            $MSG = "升级失败！";
        }
    } 
}
sub data_check_online(){
    my ( $status, $msg ) = ( -1, "" );
    if( $par{'downloadurl'} eq 'capsheaf'){
        $status = 0;
    }

    if( $par{'downloadurl'} eq 'SELF_DEFINE'){
        if( !($par{'customize_server'}) ){
            $msg = "服务器名不能为空！";
            return ( $status, $msg );
        }

        if( validip($par{'customize_server'}) || validdomainname($par{'customize_server'})){
            $status = 0;
        }else{
            $msg = "您输入的必须是ip或domain类型";
        }
    }
    return ( $status, $msg );
}
sub update_data_online(){
    ( $STATUS_FLAG, $MSG ) = &data_check_online();
    if( $STATUS_FLAG == 0 ){
        system("$update_system_online");
        $STATUS_FLAG = $?>>8;
        if ($STATUS_FLAG == 0 ){
            $MSG = "升级成功，系统相应模块在系统重启后生效，请重新启动系统!";
        }elsif($STATUS_FLAG == 1){
            $MSG = "该模块未激活或已过期，不能完成升级功能，请激活后再升级!";
        }elsif($STATUS_FLAG == 2){
            $MSG = "IPS特征库升级失败，请确认升级包并重新升级!";
        }elsif($STATUS_FLAG == 4){
            $MSG = "下载IPS特征库升级包失败，请检查网络连接并重新升级!";
        }
    } 
}

sub save_update_detail(){
    ( $STATUS_FLAG, $MSG ) = &data_check_online();
    if( $STATUS_FLAG == 0 ){
        my %new_settings;
        if ( -f $config_file ) {
           &readhash( "$config_file", \%new_settings );
            if ($par{'downloadurl'} eq 'capsheaf'){
                $new_settings{'DOWNLOADURL'} = $par{'downloadurl'};
                $new_settings{'UPDATE_SCHEDULE'} = $par{'update_schedule'};
            }
            elsif ($par{'downloadurl'} eq 'SELF_DEFINE'){
                $new_settings{'DOWNLOADURL'} = $par{'customize_server'};
                $new_settings{'UPDATE_SCHEDULE'} = $par{'update_schedule'};
            }
            &writehash($config_file, \%new_settings);
            $MSG = "信息保存成功。";
             system("$save_update_detail");
        }else{
                $MSG = "信息保存失败！";
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