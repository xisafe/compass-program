#!/usr/bin/perl
#==============================================================================#
#
# 描述: 历史日志查询页面
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.12.10 WangLin创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'logs_event_search.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my @template_configs;   #保存整个模板配置的引用
my $CUR_PAGE = "历史日志查询" ;  #当前页面名称，用于记录日志
my $log_oper;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
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
    #做出响应
    &do_action();
}

sub init_data(){
    $custom_dir         = '/ips';
    $conf_dir           = "${swroot}".$custom_dir;
    $conf_file          = $conf_dir.'/logtemplete';
    $history_conf_file  = $conf_dir.'/logs_history.conf';
    # $need_reload_tag    = $conf_dir.'/add_list_need_reload';
    $event_cls_file     = '/etc/efw/idps_console/rules/event_class';

    #============扩展的CSS和JS文件-BEGIN========================================================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/extjs/resources/css/ext-all.css">
                    <link rel="stylesheet" type="text/css" href="/include/logs_real_time_events.css" />
                    <link rel="stylesheet" type="text/css" href="/include/logs_history_events.css" />
                    <script type="text/javascript" src="/extjs/ext-debug.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/logs_history_events.js"></script>';
    #============扩展的CSS和JS文件-BEGIN=======================================================#

    &read_template_json();
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};

    if($action ne 'export_data' && $query_action ne 'export_data' && $query_action ne 'export_selected') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ( $action eq 'save_data' ) {
        &save_data();
    }
    elsif ( $action eq 'load_data' && $panel_name eq "list_query_template" ) {
        &load_data();
    }
    elsif ( $action eq 'load_data' && $panel_name ne "list_query_template" && $panel_name ne "logs_event_details" ) {
        &load_history_events_data();
    }
    elsif ( $action eq 'load_data' && $panel_name eq "logs_event_details" ) {
        &load_history_event_details();
    }
    elsif ( $action eq 'load_init_data' ) {
        &load_init_data();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ($action eq 'delete_data') {
        &delete_data();
    }
    elsif ($action eq 'enable_data') {
        &toggle_enable( "on" );
    }
    elsif ($action eq 'disable_data') {
        &toggle_enable( "off" );
    }
    elsif( $action eq 'query_suggestion' ) {
        &query_suggestion();
    }
    else {
        &show_page();
    }
}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &display_test_div();
    &closepage();
}

sub display_test_div() {
    printf<<EOF
    <div id="my_message_box"></div>
    <div id="add_query_template"></div>
    <div id="logs_event_details"></div>
    <div class="container">
        <div id="page_tabs_container" class="page_tabs_container">
            <div id="query_template_tab" class="page_tab page_tab_active">
                <span id="query_template_tab_text" class="page-tab-text">查询模板</span>
            </div>
        </div>
        <div id="page_content_container" class="page_content_container">
            <div id="list_query_template" class="list_check_in_dom"></div>
        </div>
    </div>
EOF
    ;
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
    $config{'name'}       = $temp[0];
    $config{'note'}       = $temp[1];
    $config{'enable'}     = $temp[2];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'note'} );
    push( @record_items, $hash_ref->{'enable'} );
    return join ",", @record_items;
}

sub get_detail_data($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records( $conf_file, $page_size, $current_page, \@lines );
    }

    for( my $i = 0; $i < @lines; $i++ ) {
        my $id = $from_num + $i;
        if( !$LOAD_ONE_PAGE ) {
            $id = $i;
        }
        my %hash = &get_config_hash( $lines[$i] );

        if ( !$hash{'valid'} ) {
            $total_num--;
            next;
        }

        $hash{'id'} = $id;
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg, $total_num );
}

sub get_event_class_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'cn_name'}  = $temp[0];
    $config{'en_name'}  = $temp[1];
    $config{'en_short'} = $temp[2];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_event_class($) {
    my $content_array_ref = shift;
    my @lines = ();
    my ( $status, $mesg, $total_num ) = &read_config_lines( $event_cls_file, \@lines);
    if ( $status != 0 ) {
        return ( $status, $mesg );
    }

    for ( my $i = 0; $i < $total_num; $i++ ) {
        my %hash = &get_event_class_hash( $lines[$i] );
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg );
}

sub save_data_handler($) {
    my $to_save_hash = shift;
    my ( $status, $mesg ) = ( -1, "未开始检测数据" );

    #===检测重名====#
    my $exit_conf_num = scalar( @template_configs );
    for ( my $i = 0; $i < $exit_conf_num; $i++ ) {
        if ( $template_configs[$i]->{'template_name'} eq $par{'template_name'} ) {
            if ( "$par{'id'}" ne "$i" ) {
                $mesg = "名称已存在";
                return ( $status, $mesg );
            }
        }
    }

    $to_save_hash->{"template_name"} = $par{"template_name"};
    $to_save_hash->{"template_note"} = $par{"template_note"};

    if ( $par{'template_name'} eq "" ) {
        $status = -1;
        $mesg = "请填写模板名称";
        return ( $status, $mesg );
    }

    #===时间范围字段===#
    my %time_range = (
        type => $par{"time_range_radio"},
        value => $par{'time_range_choice'}
    );
    if ( $par{'time_range_radio'} == 1 ) {
        if ( $par{'time_range_choice'} eq "lastday_N" || $par{'time_range_choice'} eq "lastweek_N" ||
             $par{'time_range_choice'} eq "lastmonth_N" ) {
            my $time_range_value = $par{'time_range_choice'};
            my $time_range_N = $par{'recent_n_value'};
            $time_range_value =~ s/N/$time_range_N/g;
            $time_range{'value'} = $time_range_value;
        }
    } elsif ( $par{'time_range_radio'} == 2 ) {
        if($par{'start_time'} =~/PM/){
            my @temp = split(":",$par{'start_time'});
            if ($temp[0] ne '12') {
                $temp[0] = int($temp[0]) + 12;
            }
        
            $par{'start_time'} = $temp[0].':'.$temp[1];
             $par{'start_time'} =~ s/( AM| PM)/\:00/g;
        }else{
            my @temp = split(":",$par{'start_time'});
            if ($temp[0] eq '12') {
                $temp[0] = '00';
            }elsif($temp[0] ne '11' && $temp[0] ne '10'){
                $temp[0] = '0'.$temp[0];
            }
            $par{'start_time'} = $temp[0].':'.$temp[1];
                $par{'start_time'} =~ s/( AM| PM)/\:00/g;
        }

        if($par{'end_time'} =~/PM/){
            my @temp = split(":",$par{'end_time'});
            if ($temp[0] ne '12') {
                $temp[0] = int($temp[0]) + 12;
            }
            $par{'end_time'} = $temp[0].':'.$temp[1];
             $par{'end_time'} =~ s/( AM| PM)/\:00/g;
        }else{
             my @temp = split(":",$par{'end_time'});
            if ($temp[0] eq '12') {
                $temp[0] = '00';
            }elsif($temp[0] ne '11' && $temp[0] ne '10'){
                $temp[0] = '0'.$temp[0];
            }
            $par{'end_time'} = $temp[0].':'.$temp[1];
            $par{'end_time'} =~ s/( AM| PM)/\:00/g;
        }
        
        my %time_value = (
            time_start  => "$par{'start_date'} $par{'start_time'}",
            time_end    => "$par{'end_date'} $par{'end_time'}",
        );
        $time_range{'value'} = \%time_value;
    } else {
        $time_range{'type'} = 1;
        $time{'value'} = "today";
    }
    $to_save_hash->{"time_range"} = \%time_range;

    #===事件类型字段===#
    $par{"event_class"} =~ s/\|/,/g;
    $to_save_hash->{"safe_type"} = $par{"event_class"};
    if ( $par{'event_class_radio'} eq "ignore" ) {
        $to_save_hash->{"safe_type"} = "all";
    }

    #===事件级别字段===#
    $par{"event_level"} =~ s/\|/,/g;
    $to_save_hash->{"priority"} = $par{"event_level"};
    if ( $par{'event_level_radio'} eq "ignore" ) {
        $to_save_hash->{"priority"} = "all";
    }

    #===IP地址字段===#
    my @ips;
    foreach my $key ( keys %par ) {
        if ( $key =~ m/ip_addr_(\d+)/ ) {
            #===找到一个IP地址===#
            my $ip_addr = $par{$key}, $serial = $1;
            my $source_ip_switch = "off", $destination_ip_switch = "off";
            if ( $par{"source_ip_$serial"} eq "$serial" ) {
                $source_ip_switch = "on";
            }
            if ( $par{"destination_ip_$serial"} eq "$serial" ) {
                $destination_ip_switch = "on";
            }
            push( @ips, "$ip_addr,$source_ip_switch,$destination_ip_switch" );
        }
    }
    $to_save_hash->{"ip"} = \@ips;
    if ( $par{'ip_addr_checkbox'} eq "ignore" ) {
        @ips = ();
    }

 #===用户===#
    my @user;
    foreach my $key ( keys %par ) {
        if ( $key =~ m/user_addr_(\d+)/ ) {
            #===找到一个用户===#
            my $user_addr = $par{$key}, $serial = $1;
            my $source_user_switch = "off", $destination_user_switch = "off";
            if ( $par{"source_user_$serial"} eq "$serial" ) {
                $source_user_switch = "on";
            }
            if ( $par{"destination_user_$serial"} eq "$serial" ) {
                $destination_user_switch = "on";
            }
            push( @user, "$user_addr,$source_user_switch,$destination_user_switch" );
        }
    }
    $to_save_hash->{"user"} = \@user;
    if ( $par{'user_addr_checkbox'} eq "ignore" ) {
        @user = ();
    }

    #===通信端口字段===#
    my @sport = split( ",", $par{"source_ports"} );
    my @dport = split( ",", $par{"destination_ports"} );
    my %port = (
        sport => \@sport,
        dport => \@dport,
    );
    $to_save_hash->{"port"} = \%port;
    if ( $par{'ignore_communication_port'} eq "ignore_communication_port" ) {
        @sport = ();
        @dport = ();
    }

    $status = 0;
    $mesg = "检测结束";
    return ( $status, $mesg );
}

sub save_data() {
    my %to_save_hash;
    my $success = "false";

    my ( $status, $reload, $mesg ) = ( -1, 0, "未保存" );
    ( $status, $mesg ) = &save_data_handler( \%to_save_hash );
    if ( $status != 0 ) {
        &send_status_x( $success, $status, $reload, $mesg );
        return;
    }

    if ( $par{'id'} eq "" ) {
        push( @template_configs, \%to_save_hash );
        $log_oper = "add";
    } else {
        @template_configs[$par{'id'}] = \%to_save_hash;
        $log_oper = "edit";
    }

    my $configs_str = $json->encode( \@template_configs );;

    my @configs = ( $configs_str );
    ( $status, $mesg ) = &write_config_lines( $conf_file, \@configs );
    if( $status != 0 ) {
        $mesg = "保存失败";
    } else {
        $success = "true";
        $mesg = "保存成功";
    }
    &send_status_x( $success, $status, $reload, $mesg );
}

sub load_data(){
    my %ret_data;
    my $total_num = scalar( @template_configs );

    for ( my $i = 0; $i < $total_num; $i++ ) {
        @template_configs[$i]->{"id"} = $i; # 初始化ID
    }

    $ret_data{'detail_data'} = \@template_configs;
    $ret_data{'total_num'} = $total_num;
    $ret_data{'reload'} = 0;

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub save_query_conf($) {
    my $dbh = shift;
    my $query_conf = shift;
    my $save_flag = 0;
    if ( $query_conf->{'PAGESIZE'} eq "" ) {
        $query_conf->{'PAGESIZE'} = $par{'page_size'};
        $save_flag++;
    }

    # if ( $query_conf->{'total_page'} eq "" || $query_conf->{'log_count'} eq "" ) {
    #     #===查询总记录数===#
    #     my ( $total_page, $log_count ) = &get_total_page_num( $dbh, $query_conf, $template_configs[$par{'template_id'}] );
    # }
}

sub load_history_events_data() {
    my %ret_data = (
        reload => 0,
    );
    my %query_conf = (
        PAGESIZE => $par{'page_size'},
    );
    my @content_array;
    &readhash( $history_conf_file, \%query_conf );

    my $dbh = connect_sql();
    &save_query_conf( $dbh, \%query_conf );
    my ( $total_page, $log_count ) = &get_total_page_num( $dbh, \%query_conf, $template_configs[$par{'template_id'}] );
    &query( $dbh, \%query_conf, $template_configs[$par{'template_id'}], $par{'current_page'}, $total_page, \@content_array );

    $ret_data{'detail_data'} = \@content_array;
    $ret_data{'total_num'} = $log_count;
    $ret_data{'reload'} = 0;

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub load_init_data() {
    my %ret_data;

    my @event_class;
    ( $status, $mesg, $total_num ) = &get_event_class( \@event_class );

    %ret_data->{'event_class'} = \@event_class;
    %ret_data->{'mesg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_history_event_details() {
    my %ret_data;

    my @content_array;
    my ( $status, $error_mesg, $total_num ) = &get_details_content( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_details_content() {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $dbh = connect_sql();
    &get_detail_by_eid( $dbh, $par{'eid'},$par{'sid'}, $content_array_ref);
    my $total_num = scalar ( @$content_array_ref );
    my $status = 0, $mesg = "加载成功";

    return ( $status, $error_mesg, $total_num );
}

sub delete_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未删除" );

    my %to_delete_ids = get_record_keys_hash( $par{'id'}, "&" );
    my @to_save_data;
    my $to_delete_num = 0;

    my $total_num = scalar( @template_configs );
    for( my $i = 0; $i < $total_num; $i++ ) {
        if ( $to_delete_ids{$i} ne "$i" ) {
            push( @to_save_data, $template_configs[$i] );
        } else {
            $to_delete_num++;
        }
    }

    if ( $to_delete_num == 0 ) {
        $status = -1;
        $mesg = "未检测到符合删除的数据";
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $configs_str = $json->encode( \@to_save_data );;
    my @configs = ( $configs_str );
    ( $status, $mesg ) = &write_config_lines( $conf_file, \@configs );
    if( $status != 0 ) {
        $mesg = "删除失败";
    } else {

        $mesg = "成功删除$to_delete_num个模板";
    }
    $log_oper = "del";
    &send_status( $status, $reload, $mesg );
}

sub toggle_enable($) {
    my $enable = shift;
    my $operation = "启用";
    $log_oper = 'enable';
    if ( $enable ne "on" ) {
        $operation = "禁用";
        $log_oper = 'disable';
    }
    my @lines = ();
    my $reload = 0;

    my ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        $mesg = "$operation失败";
        &send_status( $status, $reload, $mesg );
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
        $mesg = "$operation失败";
    } else {
        $mesg = "$operation成功";
        $reload = 1;
        &create_need_reload_tag();
    }

    &send_status( $status, $reload, $mesg );
    return;
}

sub apply_data() {
    &clear_need_reload_tag();
    $log_oper = "apply";
    &send_status( 0, 0, "应用成功" );
}

sub read_template_json() {
    my @lines;
    my ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines );
    if ( $status != 0 ) {
        return;
    }

    my $configs = join "", @lines;
    if ( $configs eq "" ) {
        return;
    }
    my $template_configs_ref = $json->decode( $configs );
    @template_configs = @$template_configs_ref;
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
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
}

sub send_status_x($$$$) {
    #==========状态解释=========================#
    # $success ext方式的表示成功与否的字段,true表示成功
    # $status: 0 表示成功，其他表示不成功
    # $reload: 1 表示重新应用，其他表示不应用
    # $mesg: 相关错误的消息
    #===========================================#
    my ( $success, $status, $reload, $mesg) = @_;
    my %hash;
    if ( $success eq "true" ) {
        %hash->{'success'} = 1;
    } else {
        %hash->{'failure'} = 1;
    }
    %hash->{'status'} = $status;
    %hash->{'reload'} = $reload;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
}

sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }

    if(! -e $history_conf_file){
        system("touch $history_conf_file");
    }
}
sub query_suggestion() {
    my %ret_data;
    my $sid = $par{'type'};
    my $virus_data = `sudo /usr/local/bin/get_sid_info.py -s $sid`;
    my $temp = $json->decode($virus_data);
    %ret_data->{'mesg'} = $temp;
    my $ret = $json->encode(\%ret_data);
    print $ret;
}