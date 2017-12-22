#!/usr/bin/perl
#author: LiuJulong
#createDate: 2015/01/28
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;            #要保存数据的目录名字
my $conf_dir;              #规则所存放的文件夹
my $localimport_dir;
my $import_dir;
my $conf_file;             #规则所存放的文件
my $settings_file;         #启用服务所存放的文件
my $settings_file_default; #默认启用服务所存放的文件
my $file_ftplist;
my $setting_file_import;
my $need_reload_tag;       #规则改变时需要重新应用的标识
my $page_title;            #页面标题
my $extraheader;           #存放用户自定义JS
my %par;                   #存放post方法传过来的数据的哈希
my %query;                 #存放通过get方法传过来的数据的哈希
my %settings;              #存放该页面配置的哈希
my %settings_import;
my %list_panel_config;     #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $cmd_getRtinfo;
my $cmd_import_remote;
my $cmd_import_local;
my $cmd_get_ftplist;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir            = '/flowMonit';                         #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir              = "/var/efw".$custom_dir;               #规则所存放的文件夹
    $localimport_dir       = "/tmp/localimport";
    $import_dir            = "/var/efw/backup/import";
    $conf_file             = $conf_dir.'/config';                  #流量信息所存放的文件
    $settings_file         = $conf_dir.'/settings';                #启用所存放的文件
    $settings_file_default = $conf_dir.'/default/settings';        #默认启用所存放的文件
    $file_ftplist          = '/tmp/backupftplist';
    $setting_file_import   = '/var/efw/backup/import/settings';
    $need_reload_tag       = $conf_dir.'/add_list_need_global';    #表示需要重新应用的文件
    $cmd                   = "sudo /usr/local/bin/restarttrafficstat";
    $cmd_getRtinfo         = "sudo /usr/local/bin/getRtFlowinfo.py";
    $cmd_import_remote     = "sudo /usr/local/bin/BackupFileRemote.py -i -f ";
    $cmd_import_local      = "sudo /usr/local/bin/LocalImportBackfile.py -m ";
    $cmd_get_ftplist       = "sudo /usr/local/bin/BackupFileRemote.py -g";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/fileuploader_import.js"></script>
                    <script language="JavaScript" src="/include/backup_import_init.js"></script>
                    <style type="text/css">
                    .mesg-box-l{
                        top:75%;
                    }
                    </style>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#

    &make_file();#检查要存放规则的文件夹和文件是否存在
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $panel_name = $par{'panel_name'};
    if( !$action ) {
        $action = $query{'ACTION'};
    }

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data' && $panel_name eq 'list_panel') {
        #==下载数据==#
        &load_data();
    } 
    elsif ($action eq 'load_useable_filelist') {
        #==加载数据==#
        &load_useable_filelist();
    }
    elsif ($action eq 'save_data_enable') {
        #==保存数据==#
        &save_data();
    }
    elsif ( $action eq 'delete_file') {
        &delete_file();
    }
    elsif ( $action eq 'import_remote') {
        &import_remote();
    }
    elsif ( $action eq 'import_local') {
        &import_local();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ($action eq 'delete_data') {
        #==删除数据==#
        &delete_data();
    }
    elsif ($action eq 'enable_data') {
        #==启用规则==#
        &toggle_enable( $par{'id'}, "on" );
    }
    elsif ($action eq 'disable_data') {
        #==禁用规则==#
        &toggle_enable( $par{'id'}, "off" );
    }
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_import_config();
    &closepage();
}


sub display_import_config(){
    if( -f $setting_file_import ) {
        &readhash( $setting_file_import, \%settings_import );
    }
    my $REMOTE_HOST_FTP;
    my $USERNAME_FTP;
    my $PASSWORD_FTP;
    my $REMOTE_HOST_CAPSHEAF;
    my $USERNAME_CAPSHEAF;
    my $PASSWORD_CAPSHEAF;
    if($settings_import{'REMOTE_TYPE'} eq 'ftp'){
        $REMOTE_HOST_FTP = $settings_import{'REMOTE_HOST'};
        $USERNAME_FTP = $settings_import{'USERNAME'};
        $PASSWORD_FTP = $settings_import{'PASSWORD'};
    }else{
        $REMOTE_HOST_CAPSHEAF = $settings_import{'REMOTE_HOST'};
        $USERNAME_CAPSHEAF = $settings_import{'USERNAME'};
        $PASSWORD_CAPSHEAF = $settings_import{'PASSWORD'};
    }
    printf <<EOF
    <div id="mesg_box_import" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_select_file" style="width: 96%;margin: 20px auto;"></div>
EOF
;
    &openbox('96%', 'left', '导入备份档案');
    printf <<EOF
    <!--<form name='IMPORT_FORM' method='post' action='$ENV{SCRIPT_NAME}'>-->
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr class ='odd'>
                <td class='add-div-type'>导入方式</td>
                <td>
                    <input type="radio" id="rad_local" name="import_type" value="local" checked onclick="change_import_type();"/>本地导入
                    <input style="margin-left:50px;" type="radio" id="rad_remote" name="import_type" value="remote" onclick="change_import_type();"/>远程导入
                </td>
            </tr>
            <tr class ='odd' id="tr_remote">
                <td class='add-div-type'>导入文件</td>
                <td>
                    <div style="margin-top:10px;"><input type="radio" name="REMOTE_TYPE" value="ftp" onclick="change_server_type();"/>FTP服务器</div>
                    <div id="content_ftp">
                      <div style="margin-top:5px;margin-left:20px;">服务器地址<input style="margin-left:10px;" type="text" id="SERVER_ADDR_FTP" value="$REMOTE_HOST_FTP"></div>
                      <div style="margin-top:5px;margin-left:45px;"><span>用户名</span><input style="margin-left:10px;" type="text" id="USER_NAME_FTP" value="$USERNAME_FTP"></div>
                      <div style="margin-top:5px;margin-left:45px;"><span>密&nbsp;&nbsp;&nbsp;码</span><input style="margin-left:10px;" type="password" id="PWD_FTP" value="$PASSWORD_FTP"></div>
                    </div>
                    <div style="margin-top:5px;"><input type="radio" name="REMOTE_TYPE" value="capsheaf" checked onclick="change_server_type();"/>顶点灾备机</div>
                    <div id="content_capsheaf">
                      <div style="margin-top:5px;margin-left:20px;">服务器地址<input type="text" style="margin-left:10px;" id="SERVER_ADDR_CAPSHEAF" value="$REMOTE_HOST_CAPSHEAF"></div>
                      <div style="margin-top:5px;margin-left:45px;"><span>用户名</span><input type="text" style="margin-left:10px;" id="USER_NAME_CAPSHEAF" value="$USERNAME_CAPSHEAF"></div>
                      <div style="margin-top:5px;margin-left:45px;"><span>密&nbsp;&nbsp;&nbsp;码</span><input style="margin-left:10px;" type="password" id="PWD_CAPSHEAF" value="$PASSWORD_CAPSHEAF"></div>
                    </div>
                </td>
            </tr>
            <tr class ='odd' id="tr_local">
                <td class='add-div-type'>导入文件</td>
                <td>
                    <div id="file-uploader"></div>
                    <div style="margin-top:10px;display:none;"><textarea id="local_file" name="local_file"></textarea></div>
                </td>
            </tr>
            <tr class ='odd'>
                <td class='add-div-type'>注释</td>
                <td>
                    <input type="text" id="note" name="note"/>
                </td>
            </tr>
            <tr class="table-footer"> 
                <td colspan="2">
                    <input type="button" class="net_button" name="save" value="确定" onclick="do_import()"/>
                    <!--<input type="hidden" name="ACTION" value="save_data"/>-->
                </td>
            </tr>
        </table>
    <!--</form>-->
EOF
;
    &closebox();
}

sub save_data() {
    my $reload = 0;
   

    my ( $status, $mesg ) = ( -1, "未保存" );
    my $ENABLED;
    if($par{'enabled'}){
        $ENABLED = $par{'enabled'};
    }else{
        $ENABLED = 'off';
    }
    $settings{'ENABLED'} = $ENABLED;
    &writehash( $settings_file, \%settings );
    $status = 0;
    
    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
}
sub load_data(){
    my %ret_data;
    my $content_array = ();
    my ( $status, $error_mesg, $total_num );
    my $unit = $par{'unit'};
    my $lines_str;
    
    &readhash( $settings_file_default, \%settings );
    if( -f $settings_file ) {
        &readhash( $settings_file, \%settings );
    }
    if($settings{'ENABLED'} eq 'on'){
        $lines_str = `$cmd_getRtinfo -u $unit 2>/dev/null`;
        chomp($lines_str);
        if($lines_str eq 'no_data'){
            $content_array = ();
            $total_num = 0;
            $status = 1;                   #无数据状态
            $error_mesg = '暂时无信息展示';
        }else{
            $content_array = $json->decode( $lines_str );
            $total_num = @$content_array;
            $status = 0;
        }
    }else{
        $content_array = ();
        $total_num = 0;
        $status = 1;                      #配置未启动状态
        $error_mesg = '流量统计功能未启动，无信息展示';
    }
    
    

    %ret_data->{'detail_data'} = $content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret;
}


sub delete_data() {
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_content($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );

    my $from_num = ( $current_page - 1 ) * $page_size;
    my $to_num = $current_page * $page_size;

    my @lines = ();
    my ( $status, $error_mesg ) = &read_config_lines( $conf_file, \@lines );

    my $total_num = @lines;
    if( $total_num < $to_num ) {
        $to_num = $total_num;
    }

    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        #==全部加载===#
        $from_num = 0;
        $to_num = $total_num;
    }
    for ( my $i = $from_num; $i < $total_num; $i++ ) {
        my %config = &get_config_hash( $lines[$i] );
        if( $config{'valid'} ) {
            $config{'id'} = $i;
            # if( $i % 5 == 0 ) {
            #     $config{'uneditable'} = 1;
            #     $config{'undeletable'} = 1;
            # }
            push( @$content_array_ref, \%config );
        }
    }
    return ( $status, $error_mesg, $total_num );
}

sub get_config_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    $config{'valid'} = 1;#默认是合法的行，如果有不合法的，将该字段置为0
    if ($line_content eq '') {
        $config{'valid'} = 0;
        return %config;
    }
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'name'}   = $temp[1];
    $config{'protocol'}   = $temp[2];
    $config{'port'}   = $temp[3];
    $config{'outtime'}   = $temp[4];
    $config{'description'}   = $temp[5];
    $config{'enable'}   = $temp[0];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    if($hash_ref->{'enable'}){
        push( @record_items, $hash_ref->{'enable'} );
    }else{
        push( @record_items, "off" );
    }
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'protocol'} );
    push( @record_items, $hash_ref->{'port'} );
    push( @record_items, $hash_ref->{'outtime'} );
    push( @record_items, $hash_ref->{'description'} );
    return join (",", @record_items);
}

sub toggle_enable($$) {
    my $item_id = shift;
    my $enable = shift;

    my ( $status, $mesg, $line_content ) = &get_one_record( $conf_file, $item_id );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, $mesg );
        return;
    }

    my %config = &get_config_hash( $line_content );
    $config{'enable'} = $enable;
    $line_content = &get_config_record(\%config);

    my ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $line_content );
    if( $status != 0 ) {
        $mesg = "操作失败";
    }

    &send_status( $status, $mesg );
    return;
}

sub send_status($$$) {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 1 表示重新应用，其他表示不应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status,$reload,$mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'reload'} = $reload;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}

sub getqueryhash($){
    my $query = shift;
    my $query_string = $ENV{'QUERY_STRING'};
    if ($query_string ne '') {
        my @key_values = split("&", $query_string);
        foreach my $key_value (@key_values) {
            my ($key, $value) = split("=", $key_value);
            $query->{$key} = $value;
            #===对获取的值进行一些处理===#
            $query->{$key} =~ s/\r//g;
            $query->{$key} =~ s/\n//g;
            chomp($query->{$key});
        }
    }
    return;
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
    
    if(! -e $setting_file_import){
        system("mkdir -p $import_dir");
        system("touch $setting_file_import");
    }
    
    if(! -e $settings_file_default){
        system("touch $settings_file_default");
        system("echo ENABLED=on >> $settings_file_default");
    }
    system("mkdir -p $localimport_dir");
}

sub apply_data() {
    my $result;
    system($cmd);
    $result = $?;
    chomp($result);
    my $msg;
    if($result == 0){
        $msg = "应用成功";
    }else{
        $msg = "应用失败";
    }
    &clear_need_reload_tag();
    &send_status( 0, 0, $msg );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
#加载图表数据
sub load_useable_filelist(){
    if( -f $setting_file_import ) {
        &readhash( $setting_file_import, \%settings_import );
    }
    $settings_import{'REMOTE_HOST'} = $par{'remoteAddr'};
    $settings_import{'USERNAME'} = $par{'userName'};
    $settings_import{'PASSWORD'} = $par{'password'};
    $settings_import{'REMOTE_TYPE'} = $par{'remoteType'};
    &writehash( $setting_file_import, \%settings_import);
    system("$cmd_get_ftplist");
    my @file_names = ();
    &read_config_lines( $file_ftplist, \@file_names );
    my $str_file_names = join(",",@file_names);
    print $str_file_names;
}
#用户自定义删除文件
sub delete_file(){
    my $fileName = $par{'fileName'};
    my $file = $localimport_dir.'/'.$fileName;
    `rm $file`;
    print $fileName;
}
#远程导入
sub import_remote(){
    my $fileNames = $par{'fileNames'};
    my $note = $par{'note'};
    my $result = 0;
    #my $cmd_run = "$cmd_import_remote'$fileNames' -m '$note'";
    system("$cmd_import_remote'$fileNames' -m '$note'");
    $result = $? >> 8;
    print $result;
}
#本地导入
sub import_local(){
    my $note = $par{"note"};
    my $rult = 0;
    my $filecount = `ls $localimport_dir | wc -w`;
    if($filecount == 0){
        $rult = 1;
    }else{
        system("$cmd_import_local'$note'");
        $rult = $? >>8;
    }
    
    print $rult;
}