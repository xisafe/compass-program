#!/usr/bin/perl

use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $conf_file_used;     #规则所存放的文件
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
my $LINE_NUM_CONFIG = 0;
my $LINE_NUM_CONFIGUSED = 0;
my $json = new JSON::XS;

my $CUR_PAGE = "会话阻断" ;  #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/sessionmanager/block';                      #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;          #规则所存放的文件夹
    $conf_file          = $conf_dir.'/config';              #规则所存放的文件
    $conf_file_used     = $conf_dir.'/configused';              #规则所存放的文件
    $cmd = "sudo /usr/local/bin/session_block.py -f";
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_break';

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/session_block_init.js"></script>';
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
        #==删除数据==#
        &delete_data();
    }
    elsif ($action eq 'delete_used') {
        #==删除所有过期规则==#
        &delete_used();
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
    <div id="mesg_box_break" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_block_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_block" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};

    my ( $status, $mesg ) = ( -1, "未保存" );
    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $conf_file, $record );
        $log_oper = "add";
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
        $log_oper = "edit";
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "添加成功";
    }

    &send_status( $status, $reload, $mesg );
}

sub load_data(){
    my %ret_data;
    my $protocol = $par{'protocol'};
    my $s_ip_or_mask = $par{'s_ip_or_mask'};
    my $d_ip_or_mask = $par{'d_ip_or_mask'};
    my $d_port_range = $par{'d_port_range'};
    system("");
    
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
    $log_oper = 'del';
    my @ids = split("\&",$par{'id'});
    my @lines_config = ();
    &read_config_lines($conf_file,\@lines_config);
    my $len = @lines_config;
    my @ids_config = ();
    my @ids_configused = ();
    my ( $status, $mesg );
    my $str_used;
    if($len > 0){
        foreach(@ids){
            if($_ > ($len-1)){
                push(@ids_configused,($_-$len));
            }else{
                push(@ids_config,$_);
            }
        }
        my $ids_str_config = join("\&",@ids_config);
        my $ids_str_configused = join("\&",@ids_configused);
        $str_used = $ids_str_configused;
        ( $status, $mesg ) = &delete_several_records( $conf_file, $ids_str_config);
        &delete_several_records( $conf_file_used, $ids_str_configused);
    }else{
        ( $status, $mesg ) = &delete_several_records( $conf_file_used, $par{'id'});
    }
    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'msg'} = $mesg;
    %ret_data->{'str_used'} = $str_used;
    create_need_reload_tag();
    my $ret = $json->encode(\%ret_data);
    print $ret;
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_congfig);

}

sub get_content($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );

    my $from_num = ( $current_page - 1 ) * $page_size;
    my $to_num = $current_page * $page_size;

    my @lines = ();
    my ( $status, $error_mesg ) = &read_config_lines( $conf_file, \@lines );
    $LINE_NUM_CONFIG = @lines;
    my @lines_used = ();
    &read_config_lines( $conf_file_used, \@lines_used );
    push(@lines,@lines_used);

    my $total_num = @lines;
    my $used_num = @lines_used;
    $LINE_NUM_CONFIGUSED = $used_num;
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
            # if($i > ($total_num-($used_num+1))){
                # $config{'id'} = $i-($total_num-$used_num);
            # }else{
                # $config{'id'} = $i;
            # }
            $config{'id'} = $i;
            $config{'config_num'} = $LINE_NUM_CONFIG;
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
    $config{'protocol'}   = $temp[0];
    $config{'source'}   = $temp[1];
    $config{'s_port'}   = $temp[2];
    $config{'dest'}   = $temp[3];
    $config{'d_port'}   = $temp[4];
    $config{'left_time'}   = $temp[5];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
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

sub toggle_enable($) {
    my $enable = shift;
    my @lines = ();

    my ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, $mesg );
        return;
    }

    my %item_id_hash;
    my @item_ids = split( "&", $par{'id'} );
    foreach my $id ( @item_ids ) {
        $item_id_hash{$id} = $id;
    }

    my $len = scalar( @lines );

    for ( my $i = 0; $i < $len; $i++ ) {
        if( $item_id_hash{$i} eq "$i" ) {
            my %config = &get_config_hash( $lines[$i] );
            $config{'enable'} = $enable;
            $lines[$i] = &get_config_record(\%config);
        }
    }

    my ( $status, $mesg ) = &write_config_lines( $conf_file, \@lines );
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
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_congfig);

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
    $log_oper = 'apply';
    system($cmd);
    &clear_need_reload_tag();
    &send_status( 0, 0, "应用成功" );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
#删除所有过期规则
sub delete_used(){
    $log_oper = 'del';
    system("cat /dev/null > $conf_file_used");
    &send_status(0,0,"删除成功");

}
