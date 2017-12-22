#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/12/03
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $services_file;
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
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/doublenat';                         #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;               #规则所存放的文件夹
    $conf_file          = $conf_dir.'/config';                  #发件人信息所存放的文件
    $services_file      = $conf_dir.'/services';
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_nat';#启用信息所存放的文件
    $cmd                = "/usr/local/bin/setdoublenat";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/double_nat_init.js"></script>';
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
    elsif ($action eq 'load_data_services') {
        #==加载数据==#
        &load_data_services();
    }
    elsif ($action eq 'save_data' && $panel_name eq 'add_panel') {
        #==保存数据==#
        &save_data();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ($action eq 'delete_data') {
        #==删除数据==#
        &delete_data();
    }
    elsif ($action eq 'up_item') {
        #==上移规则==#
        &up_item();
    }
    elsif ($action eq 'down_item') {
        #==下移规则==#
        &down_item();
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
    &display_list_div();
    &closepage();
}

sub display_list_div() {
    printf<<EOF
    <div id="mesg_box_nat" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_nat_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_nat_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}


sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};
    
    my @lines;
    &read_config_lines($conf_file,\@lines);

    my ( $status, $mesg ) = ( -1, "未保存" );
    my @conflict_rules = ();
    if( $item_id eq '' ) {
        for (my $i=0;$i<@lines;$i++){
            if($par{'source'} eq (split(",",$lines[$i]))[0] && $par{'dest'} eq (split(",",$lines[$i]))[1] && $par{'protocol'} eq (split(",",$lines[$i]))[2] && $par{'dst_port'} eq (split(",",$lines[$i]))[3]){
                $status = -2;
                push(@conflict_rules,"规则".($i+1));
            }
        }
        if($status != -2){
            ( $status, $mesg ) = &append_one_record( $conf_file, $record );
            $mesg = "添加成功";
        }else{
            &append_one_record( $conf_file, $record );
            $status = 0;
            $mesg = "检测到当前规则与".join(",",@conflict_rules)."冲突";
        }
    } else {
        for (my $i=0;$i<@lines;$i++){
            if($i ne $item_id){
                if($par{'source'} eq (split(",",$lines[$i]))[0] && $par{'dest'} eq (split(",",$lines[$i]))[1] && $par{'protocol'} eq (split(",",$lines[$i]))[2] && $par{'dst_port'} eq (split(",",$lines[$i]))[3]){
                    $status = -2;
                    push(@conflict_rules,"规则".($i+1));
                }
            }
        }
        if($status != -2){
            ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
            $mesg = "修改成功";
        }else{
            &update_one_record( $conf_file, $item_id, $record );
            $status = 0;
            $mesg = "检测到当前规则与".join(",",@conflict_rules)."冲突";
        }
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
    }

    &send_status( $status, $reload, $mesg );
}
sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );
    
    my $record_num = @lines;
    my $sequence = 1;
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
            $conf_data{'sequence'} = $sequence;
            $sequence++;
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

    if($status eq '0'){
        $mesg = "删除成功";
    }
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
    my $sequence = 1;
    for ( my $i = $from_num; $i < $total_num; $i++ ) {
        my %config = &get_config_hash( $lines[$i] );
        if( $config{'valid'} ) {
            $config{'id'} = $i;
            $config{'sequence'} = $sequence;
            $sequence++;
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
    $config{'source'}   = $temp[0];
    $config{'dest'}   = $temp[1];
    $config{'protocol'}   = $temp[2];
    $config{'dst_port'}   = $temp[3];
    $config{'nat_type_r'}   = $temp[4];
    $config{'ip_r'}   = $temp[5];
    #$config{'port_r'}   = $temp[6];
    $config{'nat_type_d'}   = $temp[6];
    $config{'ip_d'}   = $temp[7];
    $config{'port_d'}   = $temp[8];
    $config{'enable'}   = $temp[9];
    $config{'log'}   = $temp[10];
    $config{'note'}   = $temp[11];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    my $source = $hash_ref->{'source'};
    $source =~ s/\n/&/g;
    $source =~ s/\r//g;
    push( @record_items, $source );
    my $dest = $hash_ref->{'dest'};
    $dest =~ s/\n/&/g;
    $dest =~ s/\r//g;
    push( @record_items, $dest );
    push( @record_items, $hash_ref->{'protocol'} );
    my $dst_port = $hash_ref->{'dst_port'};
    $dst_port =~ s/\n/&/g;
    $dst_port =~ s/\r//g;
    push( @record_items, $dst_port );
    push( @record_items, $hash_ref->{'nat_type_r'} );
    my $ip_r = $hash_ref->{'ip_r'};
    if($hash_ref->{'nat_type_r'} eq "ip"){
        $ip_r = $hash_ref->{'ip_r'};
    }elsif($hash_ref->{'nat_type_r'} eq "netmap"){
        $ip_r = $hash_ref->{'ipnet_r'};
    }else{
        $ip_r = "";
    }
    push( @record_items, $ip_r );
    #push( @record_items, $hash_ref->{'port_r'} );
    push( @record_items, $hash_ref->{'nat_type_d'} );
    my $ip_d = $hash_ref->{'ip_d'};
    if($hash_ref->{'nat_type_d'} eq 'ip'){
        $ip_d = $hash_ref->{'ip_d'};
    }elsif($hash_ref->{'nat_type_d'} eq 'lb'){
        $ip_d = $hash_ref->{'lb_d'};
    }elsif($hash_ref->{'nat_type_d'} eq 'netmap'){
        $ip_d = $hash_ref->{'ipnet_d'};
    }else{
        $ip_d = "";
    }
    push( @record_items, $ip_d );
    if($hash_ref->{'nat_type_d'} eq 'return'){
        push( @record_items, "" );
    }else{
        push( @record_items, $hash_ref->{'port_d'} );
    }
    if($hash_ref->{'enable'}){
        push( @record_items, $hash_ref->{'enable'} );
    }else{
        push( @record_items, "off" );
    }
    push( @record_items, 'off' );
    my $note = $hash_ref->{'note'};
    $note =~ s/,/，/g;
    push( @record_items, $note );
    return join (",", @record_items);
}

sub toggle_enable($$) {
    my $item_id = shift;
    my $enable = shift;
    my $reload = 1;
    
    my @lines;
    my @conflict_rules = ();
    &read_config_lines($conf_file,\@lines);

    my ( $status, $mesg, $line_content ) = &get_one_record( $conf_file, $item_id );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    my %config = &get_config_hash( $line_content );
    $config{'enable'} = $enable;
    $line_content = &get_config_record(\%config);

    ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $line_content );
    if( $status != 0 ) {
        $mesg = "操作失败";
    }elsif($enable eq 'on'){
        $mesg = "启用成功";
        for (my $i=0;$i<@lines;$i++){
            if($i ne $item_id){
                if($config{'source'} eq (split(",",$lines[$i]))[0] && $config{'dest'} eq (split(",",$lines[$i]))[1] && $config{'protocol'} eq (split(",",$lines[$i]))[2] && $config{'dst_port'} eq (split(",",$lines[$i]))[3]){
                    $status = 0;
                    push(@conflict_rules,"规则".($i+1));
                }
            }
        }
        my $length_conflict = @conflict_rules;
        if($length_conflict > 0){
            $mesg = "检测到当前规则与".join(",",@conflict_rules)."冲突";
        }
    }else{
        $mesg = "禁用成功";
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
#加载服务数据
sub load_data_services(){
    my %ret_data;
    #加载服务及端口数据
    my @lines_services = ();
    &read_config_lines($services_file,\@lines_services);
    my @data_services = ();
    foreach (@lines_services){
        my @data_item = split(",",$_);
        my %config_service;
        $config_service{'name'} = $data_item[0];
        $config_service{'port'} = $data_item[1];
        $config_service{'protocol'} = $data_item[2];
        push(@data_services,\%config_service);
    }
    %ret_data->{'data_services'} = \@data_services;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
#上移规则
sub up_item(){
    my ($status,$mesg) = &move_one_record($conf_file,$par{'item_id'},-1);
    my $reload = 0;
    &send_status($status,$reload,$mesg);
}
#下移规则
sub down_item(){
    my ($status,$mesg) = &move_one_record($conf_file,$par{'item_id'},1);
    my $reload = 0;
    &send_status($status,$reload,$mesg);
}