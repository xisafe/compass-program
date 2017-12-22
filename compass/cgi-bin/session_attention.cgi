#!/usr/bin/perl

use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $conf_file_break;    #规则所存放的文件
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $cmd_restart;
my $FILE_CONTROL;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/sessionmanager/control';             #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/lib".$custom_dir;                #规则所存放的文件夹
    $conf_file          = $conf_dir.'/sessionfile';              #规则所存放的文件
    $conf_file_break    = '/var/efw/sessionmanager/block/config';#规则所存放的文件
    $cmd = "sudo /usr/local/bin/countconn2.py -L ";
    $cmd_restart = "sudo /usr/local/bin/session_block.py";
    $need_reload_tag    = $conf_dir.'/need_reload_break';
    $FILE_CONTROL = "/var/lib/sessionmanager/control/sessionfile";

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/session_attention_init.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#

    &make_file();#检查要存放规则的文件夹和文件是否存在
}

sub do_action() {
    my $action = $par{'ACTION'};
    if( !$action ) {
        $action = $query{'ACTION'};
    }

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==下载数据==#
        &load_data();
    } 
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ($action eq 'save_data') {
        &save_data();
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
    &display_test_div();
    &closepage();
}

sub display_test_div() {
    printf<<EOF
    <div id="mesg_box_attention" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_block_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_account" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub convertip2ipmask($){
	my $ip = shift;
	if ( &validip($ip)){
		chomp($ip);
		return $ip.'/32';
	}
	return $ip
}

sub load_data(){
    my %ret_data;
    my $PROTO = $par{'style_protocol'};
    my $s_ip_or_mask = &convertip2ipmask($par{'s_ip_or_mask'});
    my $flag_law = 0;
    if(!$s_ip_or_mask){
        $s_ip_or_mask = "0.0.0.0";
    }elsif(!(&validipormask($s_ip_or_mask))){
        $flag_law++;
    }
    my $d_ip_or_mask = &convertip2ipmask($par{'d_ip_or_mask'});
    if(!$d_ip_or_mask){
        $d_ip_or_mask = "0.0.0.0";
    }elsif(!(&validipormask($d_ip_or_mask))){
        $flag_law++;
    }
    my $d_port_range = $par{'d_port_range'};

    if(!$d_port_range){
        $d_port_range = "0";
    }elsif(!(&validport($d_port_range)) && !(&validportrange($d_port_range)) && !($d_port_range =~ m/\d\-\d/)){
        $flag_law++;
    }
    my @content_array;
    my ( $status, $error_mesg, $total_num );

    if($flag_law){ #非0
        @content_array = ();
    }else{ #0
        system($cmd."-p ".$PROTO." -s ".$s_ip_or_mask." -d ".$d_ip_or_mask." -r ".$d_port_range." -f ".$FILE_CONTROL);
        ( $status, $error_mesg, $total_num ) = &get_test_content( \@content_array );
        if($? != 0){
            $error_mesg .= ",命令执行失败$?";
        }
    }
    #system("sudo /usr/local/bin/countconn -L -p tcp -s 0.0.0.0 -d 0.0.0.0 -r 0 -f /var/log/sessionmanager/control/sessionfile");
    
    $total_num = @content_array;
    my @panel_header = &config_list_panel_header();
    my $reload = 0;
    if(-e $need_reload_tag){
        $reload = 1;
    }

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'reload'} = $reload;
    %ret_data->{'error_mesg'} = $error_mesg;
    # %ret_data->{'page_size'} = $PAGE_SIZE;
    %ret_data->{'panel_header'} = \@panel_header;

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}


sub delete_data() {
    my ( $status, $mesg ) = &delete_one_record( $conf_file, $par{'id'});

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'msg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_test_content($) {
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
    my @temp = split(" ", $line_content);
    $config{'protocol'}   = $temp[0];
    $config{'s_ip'}   = $temp[1];
    $config{'s_port'}   = $temp[2];
    $config{'d_ip'}   = $temp[3];
    $config{'d_port'}   = $temp[4];
    #$config{'state'}   = $temp[5];
    $config{'live_time'}   = $temp[5];
    if($config{'s_ip'} eq '0.0.0.0'){
        $config{'valid'} = 0;
    }

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'protocol'} );
    push( @record_items, $hash_ref->{'s_ip'} );
    push( @record_items, $hash_ref->{'s_port'} );
    push( @record_items, $hash_ref->{'d_ip'} );
    push( @record_items, $hash_ref->{'d_port'} );
    #push( @record_items, $hash_ref->{'state'} );
    push( @record_items, $hash_ref->{'live_time'} );
    return join " ", @record_items;
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

sub config_list_panel_header() {
    #====第三步，配置表头=============#
    my %functions = (
        "onclick" => "toggle_check(this);",
    );
    my %hash = (
        "enable"    => 0,           #用户控制表头是否显示
        "type"      => "checkbox",  #type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title"     => "",          #不同类型的，title需要的情况不同，一般text类型需要title
        "name"      => "checkbox",  #用户装载数据之用
        "id"        => "",          #元素的id号
        "class"     => "",          #元素的class
        "td_class"  => "",          #这一列td的class，主要用于控制列和列内元素
        "width"     => "5%",        #所有表头加起来应该等于100%,以精确控制你想要的宽度
        # "functions" => \%functions, #一般只有checkbox才会有这个字段
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "协议", 
        "name"      => "protocol",
        "class"     => "",
        "td_class"  => "align-center",
        "width"     => "8%",
    );
    push( @panel_header, \%hash );
    
    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "源IP", 
        "name"      => "s_ip",
        "class"     => "",
        "td_class"  => "align-center",
        "width"     => "18%",
    );
    push( @panel_header, \%hash );
    
    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "源端口", 
        "name"      => "s_port",
        "class"     => "",
        "td_class"  => "align-center",
        "width"     => "10%",
    );
    push( @panel_header, \%hash );
    
    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "目的IP", 
        "name"      => "d_ip",
        "class"     => "",
        "td_class"  => "align-center",
        "width"     => "17%",
    );
    push( @panel_header, \%hash );
    
    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "目的端口", 
        "name"      => "d_port",
        "class"     => "",
        "td_class"  => "align-center",
        "width"     => "17%",
    );
    push( @panel_header, \%hash );
    
    # my %hash = (
        # "enable"    => 1,
        # "type"      => "text",
        # "title"     => "状态", 
        # "name"      => "state",
        # "class"     => "",
        # "width"     => "14%",
    # );
    # push( @panel_header, \%hash );
    
    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "存活时间", 
        "name"      => "live_time",
        "class"     => "",
        "td_class"  => "align-center",
        "width"     => "8%",
    );
    push( @panel_header, \%hash );
    
    my %hash = (
        "enable"    => 1,
        "type"      => "action",
        "title"     => "操作",        #一般action列都是这个标题
        "name"      => "action",
        "class"     => "",
        "td_class"  => "align-center",
        "width"     => "8%",
    );
    push( @panel_header, \%hash );

    return @panel_header;
}
#添加临时阻断
sub save_data() {
    my $reload = 0;
    my $record = &get_config_record_breck( \%par );
    my $item_id = $par{'id'};

    my ( $status, $mesg ) = ( -1, "未保存" );
    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $conf_file_break, $record );
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file_break, $item_id, $record );
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "添加成功";
    }

    &send_status( $status, $reload, $mesg );
}

sub get_config_record_breck($) {
    my $hash_ref = shift;
    my @record_items = ();
    my $protocol = $hash_ref->{'protocol'};
    push( @record_items, $protocol );
    push( @record_items, $hash_ref->{'source'} );
    if($protocol eq 'tcp' || $protocol eq 'udp' || $protocol eq 'all'){
        push( @record_items, $hash_ref->{'s_port'} );
    }else{
        push( @record_items, $hash_ref->{'type'} );
    }
    push( @record_items, $hash_ref->{'dest'} );
    if($protocol eq 'tcp' || $protocol eq 'udp' || $protocol eq 'all'){
        push( @record_items, $hash_ref->{'d_port'} );
    }else{
        push( @record_items, $hash_ref->{'code'} );
    }
    push( @record_items, $hash_ref->{'left_time'} );
    push( @record_items, "0" );
    return join ",", @record_items;
}
sub apply_data() {
    system($cmd_restart);
    &clear_need_reload_tag();
    &send_status( 0, 0, "应用成功" );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
