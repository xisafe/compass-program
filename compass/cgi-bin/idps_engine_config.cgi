#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/12/25
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $conf_file_lib;      #规则所存放的文件
my $conf_file_obj;      #规则所存放的文件
my $default_conf_file;  #默认规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $ERROR = "";
my $WARING = "";
my $NOTE = "";
my $status_engine;
my $sourceip_file;
my $CUR_PAGE = "引擎配置" ;      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $sourceip_file      = '/var/efw/objects/ip_object/ip_group';#源IP配置文件路径
    $custom_dir         = '/idps/engine';                                   #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = $swroot.$custom_dir;                              #规则所存放的文件夹
    $conf_file          = $conf_dir.'/settings';                            #配置信息所存放的文件
    $conf_file_lib      = $swroot.'/idps_console/rule_libraries/config';    #配置信息所存放的文件
    $conf_file_obj      = $swroot.'/idps_console/detected_objects/config';  #配置信息所存放的文件
    $default_conf_file  = $conf_dir.'/default/settings';                    #配置信息所存放的文件
    $need_reload_tag    = $swroot.'/idps/need_reload_tag';                  #启用信息所存放的文件
    $ips_running_flag   = "${swroot}/idps/engine/apping_flage";
    $cmd                = "/usr/local/bin/restartips -f";
    # $cmd_judge_status   = "sudo /usr/local/bin/judge_virus_enable.py -m ipsrules";
    # $status_engine      = "off";
    $cmd_isActive       = "/usr/local/bin/ipsIsactive";
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/waiting.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/ips_check_running.js"></script>
                    <script language="JavaScript" src="/include/idps_engine_config_init.js"></script>';
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
    if ($action eq 'load_data' && $panel_name eq 'lib_panel') {
        #==下载数据==#
        &load_data_lib();
    } 
    elsif ($action eq 'load_data' && $panel_name eq 'obj_panel') {
        #==下载数据==#
        &load_settingdata($sourceip_file);
        # &load_data_obj();
    } 
    elsif ($action eq 'save_data') {
        #==保存数据==#
        &save_data();
       &write_log($CUR_PAGE,"edit",0,$rule_or_config);
    }
    elsif ($action eq 'init_data') {
        #==初始加载数据==#
        &load_init_data();
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
    if(-e $need_reload_tag && $par{'ACTION'} ne "apply" && !-f $ips_running_flag ){
        &applybox("规则已改变,需要重新应用以使规则生效");
    }
    &openbigbox($ERROR, $WARING, $NOTE);
    &openbox('96%', 'left', '引擎配置');
    &display_engine_config();
    &display_list_div();
    &closebox();
    &closebigbox();
    &closepage();
    if ( $par{'ACTION'} eq 'apply') {
        &apply_data();
        $log_oper = "apply";
        &write_log($CUR_PAGE,$log_oper,0,$rule_or_config);
    }
}

sub display_list_div() {
    printf<<EOF
    <div id="panel_rule_lib"></div>
    <div id="panel_net_obj"></div>
EOF
    ;
}
sub EnableIsOK(){
    my $result=`sudo $cmd_isActive`; #结果若是1，则启用功能；0禁用
    chomp($result);
    if($result eq '0'){
        return 1;
    }else{
        return 0;
    }
}
sub display_engine_config(){
    
    my $enable = $par{'enabled_engine'};
    my $goal ="";
    if($enable eq "on")
    {
        $goal="checked";
    }

    my $enableordis="";
    my $title="";
    my $dest=EnableIsOK();
    if($dest eq "0"){
        $enableordis="";
        $title="";
    }
    else{
        $goal="";
        $enableordis="disabled";
        $title="入侵防御功能模块未激活，暂无法启用";
    }

    printf <<EOF
    <form name='ENGINE_CONFIG_FORM' method='post' action='$ENV{SCRIPT_NAME}'>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr class ='odd'>
                <td class='add-div-type'>特征库<font style="margin-left:3px;vertical-align:middle;">*</font></td>
                <td>
                    <input id="rule_lib" readonly="true" name="rule_lib" style="height:20px;" type="text"/>
                    <input class="net_button" type="button" value="选择特征库" onclick="lib_panel.show();"/>
                </td>
            </tr>
            <tr class ='odd'>
                <td class='add-div-type'>IP组<font style="margin-left:3px;vertical-align:middle;">*</font></td>
                <td>
                    <input id="net_obj" readonly="true" name="net_obj" style="height:20px;" type="text"/>
                    <input class="net_button" type="button" value="选择IP组" onclick="obj_panel_show(obj_panel,'net_obj');"/>
                </td>
            </tr>
            <tr class ='odd'>
                <td class='add-div-type'>启用</td>
                <td>
                    <input type="checkbox" id="enabled_engine" name="enabled_engine" value="on" $enableordis $goal/>
                    <span>启用</span>
                    <span id="label_tip" style="color:red;"><font color="red"><strong>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp$title</font></strong></span>
                </td>
            </tr>
            <tr class ='odd'>
                <td class='add-div-type'>启用日志</td>
                <td>
                    <input type="checkbox" id="enabled_log" name="enabled_log" value="on"/>
                </td>
            </tr>
            <tr class="table-footer"> 
                <td colspan="2">
                    <input type="submit" class="net_button" name="save" value="保存"/>
                    <input type="hidden" name="ACTION" value="save_data"/>
                </td>
            </tr>
        </table>
    </form>
EOF
}

sub save_data() {
    my $reload = 0;

    my ( $status, $mesg ) = ( -1, "未保存" );
    my $rule_lib = $par{'rule_lib'};
    my $net_obj = $par{'net_obj'};
    my $enabled_engine;
    if($par{'enabled_engine'}){
        $enabled_engine = $par{'enabled_engine'};
    }else{
        $enabled_engine = "off";
    }
    my $enabled_log;
    if($par{'enabled_log'}){
        $enabled_log = $par{'enabled_log'};
    }else{
        $enabled_log = "off";
    }
    my $data_save = "GATEWAY,,".$rule_lib.",".$net_obj.",".$enabled_engine.",".$enabled_log.",,,,,";
    
    open (FILE, ">$conf_file");
    print FILE "$data_save\n";
    close(FILE);
    
    $status = 0;
    #system($cmd);

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    #&send_status( $status, $reload, $mesg );
    &show_page();
}
sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );
    
    my $record_num = @lines;
    my $search = $par{'search'};
    if($search){
        chomp($search);
        #===转换成小写，进行模糊查询==#
        $search = lc($search);
        for(my $i = 0; $i < $record_num; $i++){
            chomp(@lines[$i]);
            if($search ne ""){
                my $searched = 0;
                my $where = -1;
                my @data = split(",", @lines[$i]);
                foreach my $field (@data) {
                    #===转换成小写，进行模糊查询==#
                    my $new_field = lc($field);
                    $where = index($new_field, $search);
                    if($where >= 0) {
                        $searched++;
                    }
                }
                #如果没有一个字段包含所搜寻到子串,则不返回
                if(!$searched){
                    next;
                }
            }
            my %conf_data = &get_config_hash(@lines[$i]);
            if (! $conf_data{'valid'}) {
                next;
            }
            $conf_data{'id'} = $i;
            push(@content_array, \%conf_data);
            $total_num++;
        }
    }else{
        ( $status, $error_mesg, $total_num ) = &get_content( \@content_array );
    }

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    # %ret_data->{'page_size'} = $PAGE_SIZE;
    
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
    
}

sub apply_data() {
    printf <<EOF
    <script>
        RestartService("正在应用更改...");
    </script>
EOF
    ;
    system( "touch $ips_running_flag" );
    system($cmd);
    my $result = $?>>8;
    my $mesg = "应用成功";
    if($result != 0){
        $mesg = "应用失败";
    } else {
        &clear_need_reload_tag();
    }
    printf <<EOF
    <script>
        endmsg("$mesg")
    </script>
EOF
    ;
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
#加载特征库数据
sub load_data_lib(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file_lib, \@lines );
    
    my $record_num = @lines;
    $total_num = $record_num;
    
    for ( my $i = 0; $i < $record_num; $i++ ) {
        my %config;
        my @data_line = split(",",$lines[$i]);
        %config->{'name'} = $data_line[0];
        %config->{'description'} = $data_line[1];
        %config->{'id'} = $i;
        %config->{'valid'} = 1;
        push( @content_array, \%config );
    }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

#加载配置面板数据
sub load_settingdata() {
    my $file = shift;
    
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $file, \@lines );    
    my $record_num = @lines;
    $total_num = $record_num;
    
    for ( my $i = 0; $i < $record_num; $i++ ) {
        my %config;
        my @data_line = split(",",$lines[$i]);
        %config->{'name'} = $data_line[1];
        %config->{'id'} = $i;
        %config->{'valid'} = 1;
        push( @content_array, \%config );
    }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    

    my $ret = $json->encode(\%ret_data); 
    print $ret; 
}
#加载内网检测对象数据
sub load_data_obj(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file_obj, \@lines );
    
    my $record_num = @lines;
    $total_num = $record_num;
    
    for ( my $i = 0; $i < $record_num; $i++ ) {
        my %config;
        my @data_line = split(",",$lines[$i]);
        %config->{'name'} = $data_line[0];
        %config->{'description'} = $data_line[1];
        %config->{'id'} = $i;
        %config->{'valid'} = 1;
        push( @content_array, \%config );
    }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
#初始化加载数据
sub load_init_data(){
    my @lines = ();
    &read_config_lines($conf_file,\@lines);
    my @lines_lib = ();
    &read_config_lines($conf_file_lib,\@lines_lib);
    
   
    my @data_line = split(",",$lines[0]);
    
    my $rule_lib = $data_line[2];
    my $net_obj = $data_line[3];
    if(@lines_lib < 1){
        $rule_lib = "";
    }
    
    my %ret_data;
    %ret_data->{'rule_lib'}       = $rule_lib;
    %ret_data->{'net_obj'}        = $net_obj;
    %ret_data->{'enabled_engine'} = $data_line[4];
    %ret_data->{'enabled_log'}    = $data_line[5];
    

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

