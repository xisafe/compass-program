#!/usr/bin/perl

use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $page_title;         #页面标题
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $rule_to_update;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/eventwarn';                        #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;              #规则所存放的文件夹
    $conf_file          = $conf_dir.'/event-warn';              #规则所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload';
    $cmd = "/usr/local/bin/systemeventwarn.py";

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/event_setting_init.js"></script>';
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
        &load_data();
    }elsif ($action eq 'save_data' && $panel_name eq 'add_panel') {
        &save_data();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ($action eq 'delete_data') {
        #==下载数据==#
        &delete_data();
    }
    elsif ($action eq 'enable_data') {
        #==下载数据==#
        &toggle_enable( $par{'id'}, "on" );
    }
    elsif ($action eq 'disable_data') {
        #==下载数据==#
        &toggle_enable( $par{'id'}, "off" );
    }
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_div();
    &closepage();
}

sub display_div() {
    printf<<EOF
    <div id="mesg_box_event" class="container"></div>
    <div id="panel_event_add" class="container"></div>
    <div id="panel_event_list" class="container"></div>
EOF
    ;
}

sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};
    $rule_to_update = $par{'name'};

    my ( $status, $mesg ) = ( -1, "未保存" );
    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $conf_file, $record );
        if( $status == 0 ) {
            $reload = 1;
            $mesg = "添加成功";
        }
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
        if( $status == 0 ) {
            $reload = 1;
            # &create_need_reload_tag(); # systemeventwarn中这些配置是实时读取的。所以不需要应用 --2017/11/21,pengtian
            $mesg = "修改成功";
        }
    }

    &send_status( $status, $reload, $mesg );
}

sub load_data(){
    my %ret_data;
    
    my @content_array;
    my ( $status, $error_mesg, $total_num ) = &get_content( \@content_array );

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
    my @lines;
    my ( $status, $mesg );
    &read_config_lines( $conf_file, \@lines );
    my $line_delete = @lines[$par{'id'}];
    my @lines_delete = split("\&",$par{'id'});
    my $unremovable_node;
    if(@lines_delete > 1 ){
        foreach(@lines_delete){
            if((split(",",$lines[$_]))[3] == 0){
                &delete_several_records( $conf_file, $_);
            }else{
                $unremovable_node .= ',';
            }
        }
        if($unremovable_node){
            ( $status, $mesg ) = (-1,$unremovable_node."正在被使用，删除失败。");
        }
    }else{
        if((split(",",$line_delete))[3] == 0){
           ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});
        }else{
            ( $status, $mesg ) = (-1,"删除失败");
        }
    }
    
    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'msg'} = $mesg;

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
            $config{'undeletable'} = 1;
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
    $config{'event_description'}   = $temp[1];
    $config{'alarm_type'}   = $temp[3];
    $config{'enable'}   = $temp[2];
    $config{'val_max'}   = $temp[4];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @lines;
    &read_config_lines( $conf_file, \@lines );
    my @data_orignal_line = split(",",$lines[$hash_ref->{'id'}]);
    my @record_items = ();
    push( @record_items, $data_orignal_line[0] );
    push( @record_items, $data_orignal_line[1] );
    #push( @record_items, $hash_ref->{'event_description'} );
    if($hash_ref->{'enable'} eq "on"){
        push( @record_items, "on" );
    }else{
        push( @record_items, "off" );
    }
    my $alarm_type = "";
    my %hash;
    my $str_types = $hash_ref->{'alarm_type'};
    $str_types =~ s/\+/\|/g;
    my @arr_type = split(/\|/,$str_types);
    unshift(@arr_type,"log");
    @arr_type = grep { ++$hash{$_} < 2 } @arr_type;
    $alarm_type = join("+",@arr_type);
    
    push( @record_items, $alarm_type);
    
    if($hash_ref->{'val_max'}){
        push( @record_items, $hash_ref->{'val_max'});
    }else{
        push( @record_items, 0 );
    }
    
    return join ",", @record_items;
}

sub toggle_enable($$) {
    my $reload = 0;
    my $item_id = shift;
    my $enable = shift;
    my @lines = ();

    my ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, $mesg );
        return;
    }
    
    my %config = &get_config_hash( $lines[$item_id] );
    $config{'enable'} = $enable;
    $config{'id'} = $item_id;
    $record = &get_config_record(\%config);
    
    ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
    if( $status != 0 ) {
        $mesg = "操作失败";
    }
    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "操作成功";
    }
    &send_status( $status, $reload, $mesg );
    return;
}

sub send_status($$$) {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 1 表示重新应用，其他表示不应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $reload, $mesg) = @_;
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
    system($cmd.$rule_to_update);
    &clear_need_reload_tag();
    my $result = $?;
    my $msg = "应用失败"; 
    my $status = -1;
    if($result eq "0"){
        $msg = "应用成功";
        $status = 0;
    }
    &send_status( $status, 0, $msg );
}

sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
