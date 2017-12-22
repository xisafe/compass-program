#!/usr/bin/perl
#==============================================================================#
#
# 描述: 特征事件自定义
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.10.15 WangLin创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'file_relevant_time.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $lib_conf_file;      #规则库配置所存放的文件
my $sid_file;           #储存规则当前最大sid + 1 的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $protocol_file;      #协议定义的文件
my $event_cls_file;     #事件类别定义的文件
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
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
    #测试
    # &export_selected();
}

sub init_data(){
    $custom_dir         = '/idps_console/rules/custom_rules';
    $conf_dir           = "${swroot}".$custom_dir;
    $conf_file          = $conf_dir.'/config';
    $lib_conf_file      = "${swroot}/idps_console/rule_libraries/config";
    $sid_file           = $conf_dir.'/sid';
    $need_reload_tag    = "${swroot}/idps/need_reload_tag";
    $ips_running_flag   = "${swroot}/idps/engine/apping_flage";
    $restart_ips_service = "/usr/local/bin/restartips";
    $protocol_file      = '/etc/efw/idps_console/rules/protocol_info';
    $event_cls_file     = '/etc/efw/idps_console/rules/event_class';
    $event_level_file   = '/etc/efw/idps_console/rules/event_level';
    $respond_type_file  = '/etc/efw/idps_console/respond/respond_type';
    $create_eventrules  = 'sudo /usr/local/bin/idps_console/generate_eventrules.py 2>/tmp/generate_eventrules';
    $rectify_eventrules = 'sudo /usr/local/bin/idps_console/rectify_libsandcerules.py';
    $imported_filename  = "/tmp/user_import_events";
    $to_export_file     = "/tmp/export.events";
    $import_events      = "sudo /usr/local/bin/idps_console/export_import_events.py -i -f $imported_filename";
    $export_events      = "sudo /usr/local/bin/idps_console/export_import_events.py -e -s";

    #============扩展的CSS和JS文件-BEGIN========================================================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/waiting.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/ips_check_running.js"></script>
                    <script language="JavaScript" src="/include/ips_rule_custom.js"></script>';
    #============扩展的CSS和JS文件-BEGIN=======================================================#
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};

    if($action ne 'export_data' && $query_action ne 'export_data' && $query_action ne 'export_selected') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ( $action eq 'save_data' && $panel_name eq 'rule_custom_add'  ) {
        if ( $par{'id'} eq "" ) {
            #====新增记录====#
            &add_data();
        } else {
            &edit_data();
        }
    }
    elsif ( $action eq 'load_data' && $panel_name eq 'rule_custom_list' ) {
        &load_data();
    }
    elsif ( $action eq 'load_data'  && $panel_name eq 'rule_lib_list' ) {
        &load_rule_lib_list();
    }
    elsif ( $action eq 'load_init_data' ) {
        &load_init_data();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ( $action eq 'check_event_content' ) {
        &check_event_content();
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
    elsif($action eq 'import_data'){
        #==导入数据,可以导入特定几列的数据==#
        &import_data();
    } 
    else {
        if($query_action eq 'export_data') {
            #==导出数据,可以导出特定几列的数据==#
            &export_data();
        } elsif($query_action eq 'export_selected') {
            #==导出指定的项目===#
            &export_selected();
        } else {
            &show_page();
        }
    }
}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_main_body();
    &closebigbox();
    &closepage();
}

sub display_main_body() {
    printf<<EOF
    <div id="rule_custom_mesg_box"></div>
    <div id="rule_custom_add" class="container"></div>
    <div id="rule_custom_import" class="container"></div>
    <div id="rule_custom_list" class="container"></div>
    <div id="rule_lib_list" class="container"></div>
EOF
    ;
}

sub get_config_line_sid() {
    my $sid = -1;
    #===读取sid===#
    open( FILE, "<$sid_file" ) or return -1;
    my @temp = <FILE>;
    close( FILE );
    $sid = $temp[0];
    chomp $sid;
    #===写入新的sid===#
    open( FILE, ">$sid_file" ) or return -1;
    my $new_sid = $sid + 1;
    print FILE $new_sid;
    close( FILE );

    return $sid;
}

sub load_data_handler($) {
    my $hash_ref = shift;
    $hash_ref->{'respond_type'}     =~ s/&/\|/g;
    $hash_ref->{'protocol_port'}    =~ s/&/\n/g;
    $hash_ref->{'exception_ips'}    =~ s/&/\n/g;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'rule_name'} );
    push( @record_items, $hash_ref->{'rule_note'} );
    push( @record_items, $hash_ref->{'protocol'} );
    push( @record_items, $hash_ref->{'protocol_port'} );
    push( @record_items, $hash_ref->{'s_d_ip_reverse'} );
    push( @record_items, $hash_ref->{'event_class'} );
    push( @record_items, $hash_ref->{'event_level'} );
    push( @record_items, $hash_ref->{'event_content'} );
    push( @record_items, $hash_ref->{'rule_lib'} );
    push( @record_items, $hash_ref->{'respond_type'} );
    push( @record_items, $hash_ref->{'merge_type'} );
    push( @record_items, $hash_ref->{'merge_interval'} );
    push( @record_items, $hash_ref->{'max_merge_count'} );
    push( @record_items, $hash_ref->{'exception_type'} );
    push( @record_items, $hash_ref->{'exception_ips'} );
    for( my $i = 0; $i < 10; $i++ ) {
        push( @record_items, $hash_ref->{''} );
    }
    push( @record_items, $hash_ref->{'sid'} );
    return join ",", @record_items;
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
    $config{'rule_name'}        = $temp[0];
    $config{'rule_note'}        = $temp[1];
    $config{'protocol'}         = $temp[2];
    $config{'protocol_port'}    = $temp[3];
    $config{'s_d_ip_reverse'}   = $temp[4];
    $config{'event_class'}      = $temp[5];
    $config{'event_level'}      = $temp[6];
    $config{'event_content'}    = $temp[7];
    $config{'rule_lib'}         = $temp[8];
    $config{'respond_type'}     = $temp[9];
    $config{'merge_type'}       = $temp[10];
    $config{'merge_interval'}   = $temp[11];
    $config{'max_merge_count'}  = $temp[12];
    $config{'exception_type'}   = $temp[13];
    $config{'exception_ips'}    = $temp[14];
    $config{'sid'}              = $temp[25];

    if ( $config{'merge_type'} eq "" ) {
        $config{'merge_type'} = "none";
    }

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_lib_config_hash($) {
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
    $config{'name'}         = $temp[0];
    $config{'note'}         = $temp[1];
    $config{'type'}         = $temp[2];
    $config{'create_time'}  = $temp[3];
    $config{'filepath'}     = $temp[4];
    #============自定义字段组装-END===========================#
    if ( $config{'type'} eq 'system' ) {
        $config{'valid'} = 0;
    }
    return %config;
}

sub get_protocol_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'name'}                 = $temp[0];
    $config{'value'}                = $temp[1];
    $config{'protocol_type'}        = $temp[2];
    $config{'is_port_editable'}     = $temp[3];
    $config{'is_port_redirect'}     = $temp[4];
    $config{'default_ports'}        = $temp[5];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_protocol_defaultports_hash() {
    my @protocol_array;
    my ( $status, $mesg, $total_num ) = &read_config_lines( $protocol_file, \@protocol_array );

    my %config;
    for ( my $i = 0; $i < $total_num; $i++ ) {
        my %hash = &get_protocol_hash( $protocol_array[$i] );
        my $value = $hash{'value'};
        $config{ $value } = $hash{'default_ports'};
    }

    return %config;
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

sub get_event_level_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'text'}     = $temp[0];
    $config{'value'}    = $temp[1];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_respond_type_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'label'}     = $temp[0];
    $config{'value'}    = $temp[1];

    #============自定义字段组装-END===========================#
    return %config;
}

sub prepare_search($) {
    my $search = shift;

    $search =~ s/\^/\\\^/g;
    $search =~ s/\$/\\\$/g;
    $search =~ s/\./\\\./g;
    $search =~ s/\|/\\\|/g;
    $search =~ s/\(/\\\(/g;
    $search =~ s/\)/\\\)/g;
    $search =~ s/\[/\\\[/g;
    $search =~ s/\]/\\\]/g;
    $search = lc $search;

    return $search;
}

sub load_data(){
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_rule_lib_list() {
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_lib_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'page_size'} = $total_num;
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_init_data() {
    my %ret_data;

    my @protocol_array, @event_class, @event_level, @respond_type;
    my ( $status, $mesg, $total_num ) = &get_protocol_info( \@protocol_array );
    ( $status, $mesg, $total_num ) = &get_event_class( \@event_class );
    ( $status, $mesg, $total_num ) = &get_event_level( \@event_level );
    ( $status, $mesg, $total_num ) = &get_respond_type( \@respond_type );

    %ret_data->{'protocol_info'} = \@protocol_array;
    %ret_data->{'event_class'} = \@event_class;
    %ret_data->{'event_level'} = \@event_level;
    %ret_data->{'respond_type'} = \@respond_type;
    %ret_data->{'mesg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_detail_data($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;
    my $search = &prepare_search( $par{'search'} );

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records( $conf_file, $page_size, $current_page, \@lines );
    }

    my %sort_hash;
    for ( my $i = 0; $i < @lines; $i++ ) {
        my %hash = &get_config_hash( $lines[$i] );
        if ( !$hash{'valid'} ) {
            next;
        }
        $sort_hash{ $hash{'sid'} } = $i;
    }


    my $valid_total_num = 0;
    #====针对sid对数据进行排序====#
    for my $key ( sort keys %sort_hash ) {
        my $line_num = $sort_hash{ $key };
        my $id = $from_num + $line_num;
        if( !$LOAD_ONE_PAGE ) {
            $id = $line_num;
        }
        my %hash = &get_config_hash( $lines[$line_num] );
        if ( !$hash{'valid'} ) {
            $total_num--;
            next;
        }
        if ( $search ne "" ) {
            my $rule_name = lc $hash{'rule_name'};
            my $rule_note = lc $hash{'rule_note'};
            if ( !($rule_name =~ m/$search/) && !($rule_note =~ m/$search/) ) {
                #===对名字，说明进行搜索===#
                $total_num--;
                next;
            }
        }

        $hash{'id'} = $id;
        &load_data_handler( \%hash );
        push( @$content_array_ref, \%hash );
        $valid_total_num++;
    }

    return ( $status, $mesg, $valid_total_num );
}

sub get_lib_detail_data($) {
    my $content_array_ref = shift;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    ( $status, $mesg, $total_num ) = &read_config_lines( $lib_conf_file, \@lines);

    for( my $i = 0; $i < @lines; $i++ ) {
        my %hash = &get_lib_config_hash( $lines[$i] );
        if ( !$hash{'valid'} ) {
            $total_num--;
            next;
        }
        $hash{'id'} = $hash{'name'};
        &load_data_handler( \%hash );
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg, $total_num );
}

sub get_protocol_info($) {
    my $content_array_ref = shift;
    my @lines = ();
    my ( $status, $mesg, $total_num ) = &read_config_lines( $protocol_file, \@lines);
    if ( $status != 0 ) {
        return ( $status, $mesg );
    }

    for ( my $i = 0; $i < $total_num; $i++ ) {
        my %hash = &get_protocol_hash( $lines[$i] );
        $hash{'default_ports'} =~ s/&/\n/g;
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg );
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

sub get_event_level($) {
    my $content_array_ref = shift;
    my @lines = ();
    my ( $status, $mesg, $total_num ) = &read_config_lines( $event_level_file, \@lines);
    if ( $status != 0 ) {
        return ( $status, $mesg );
    }

    for ( my $i = 0; $i < $total_num; $i++ ) {
        my %hash = &get_event_level_hash( $lines[$i] );
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg );
}

sub get_respond_type($) {
    my $content_array_ref = shift;
    my @lines = ();
    my ( $status, $mesg, $total_num ) = &read_config_lines( $respond_type_file, \@lines);
    if ( $status != 0 ) {
        return ( $status, $mesg );
    }

    for ( my $i = 0; $i < $total_num; $i++ ) {
        my %hash = &get_respond_type_hash( $lines[$i] );
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg );
}

sub edit_data_handler() {
    my ( $status, $mesg ) = ( -1, "未开始检测各项的合法性" );

    #===第一步，检查名称是否重名===#
    my $name_exist_line_num = "";
    ( $status, $mesg, $name_exist_line_num ) = &where_is_field( $conf_file, ",", 0, $par{'rule_name'} );
    if ( $name_exist_line_num ne "" && $par{'id'} ne $name_exist_line_num ) {
        $status = -1;
        $mesg = "名称已存在";
        return ( $status, $mesg );
    }

    #===第二步，检查说明字符串长度 0-120个字符,并处理空行和非法字符===#
    # $par{'rule_note'} = &prepare_note( $par{'rule_note'} );
    # my $notes_len = split( "", $par{'rule_note'} );
    # if ( $notes_len > 120 ) {
    #     $status = -1;
    #     $mesg = "说明信息0-120个字符";
    #     return ( $status, $mesg );
    # }

    #===第三步，检测是否选择了系统支持的协议===#
    my %protocol_defaultports = &get_protocol_defaultports_hash();
    if ( exists $protocol_defaultports{ $par{'protocol'} } ) {
        if ( $protocol_defaultports{ $par{'protocol'} } ne '' ) {
            $par{'protocol_port'} = $protocol_defaultports{ $par{'protocol'} };
        } else {
            $par{'protocol_port'} =~ s/\n/&/g; #将换行符替换掉
            $par{'protocol_port'} =~ s/\r//g; #将换行符替换掉
        }
    } else {
        $status = -1;
        $mesg = "请选择系统支持的协议";
        return ( $status, $mesg );
    }

    #===第四步，检查响应方式是否为空===#
    $par{'respond_type'} =~ s/\|/&/g;
    if ( $par{'respond_type'} eq "" ) {
        $status = -1;
        $mesg = "至少选择一种响应方式";
        return ( $status, $mesg );
    }

    #===第五步，处理特征定义，===#
    $par{'event_content'} = &prepare_note( $par{'event_content'} );

    #===第六步，处理排除IP===#
    $par{'exception_ips'} =~ s/\n/&/g;
    $par{'exception_ips'} =~ s/\r//g;

    #===第七步，检测传上来的字段与现有字段是否一致，一致就不在进行更改===#
    my $exist_record = &get_one_record( $conf_file, $par{'id'} );
    my $new_record = &get_config_record( \%par );
    if ( $exist_record eq $new_record ) {
        $status = -1;
        $mesg = "配置未改变";
    } else {
        $status = 0;
        $mesg = "检测合格";
    }

    return ( $status, $mesg );
}

sub edit_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未保存" );
    my $item_id = $par{'id'};

    ( $status, $mesg ) = &edit_data_handler();
    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $record = &get_config_record( \%par );
    ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );

    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===生成规则===#
    system( "$create_eventrules" );
    $status = $?;
    if ( $status != 0 ) {
        $mesg = "生成自定义特征事件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===矫正===#
    my $rule_lib = $par{'rule_lib'};
    my $cmd = "$rectify_eventrules -l \"$rule_lib\" -s $par{'sid'} -a -f"; # 编辑时的矫正命令
    # if ( $par{'rule_lib'} ne "" ) {
        system( "$cmd" );
        $status = $?;
    # }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "编辑成功";
    } else {
        $mesg = "编辑失败";
    }

    &send_status( $status, $reload, $mesg );
}

sub add_data_handler() {
    my ( $status, $mesg ) = ( -1, "未开始检测各项的合法性" );

    #===第一步，检查名称是否重名===#
    my $name_exist_line_num = "";
    ( $status, $mesg, $name_exist_line_num ) = &where_is_field( $conf_file, ",", 0, $par{'rule_name'} );
    if ( $name_exist_line_num ne "" ) {
        $status = -1;
        $mesg = "名称已存在";
        return ( $status, $mesg );
    }

    #===第二步，检查说明字符串长度 0-120个字符,并处理空行和非法字符===#
    # $par{'rule_note'} = &prepare_note( $par{'rule_note'} );
    # my $notes_len = split( "", $par{'rule_note'} );
    # if ( $notes_len > 120 ) {
    #     $status = -1;
    #     $mesg = "说明信息0-120个字符";
    #     return ( $status, $mesg );
    # }

    #===第三步，检测是否选择了系统支持的协议===#
    my %protocol_defaultports = &get_protocol_defaultports_hash();
    if ( exists $protocol_defaultports{ $par{'protocol'} } ) {
        if ( $protocol_defaultports{ $par{'protocol'} } ne '' ) {
            $par{'protocol_port'}   = $protocol_defaultports{ $par{'protocol'} };
        } else {
            $par{'protocol_port'}   =~ s/\n/&/g; #将换行符替换掉
            $par{'protocol_port'}   =~ s/\r//g; #将换行符替换掉
        }
    } else {
        $status = -1;
        $mesg = "请选择系统支持的协议";
        return ( $status, $mesg );
    }

    #===第四步，检查响应方式是否为空===#
    $par{'respond_type'} =~ s/\|/&/g;
    if ( $par{'respond_type'} eq "" ) {
        $status = -1;
        $mesg = "至少选择一种响应方式";
        return ( $status, $mesg );
    }

    #===第五步，处理特征定义，===#
    $par{'event_content'} = &prepare_note( $par{'event_content'} );

    #===第六步，处理排除IP===#
    $par{'exception_ips'} =~ s/\n/&/g;
    $par{'exception_ips'} =~ s/\r//g;

    #===根据选择的配置项，将响应的其他项置空====#
    if ( $par{'merge_type'} eq "none" ) {
        $par{'merge_interval'} = "";
        $par{'max_merge_count'} = "";
    }

    if ( $par{'exception_type'} eq "none" ) {
        $par{'exception_ips'} = "";
    }

    $par{'respond_type'}    =~ s/\|/&/g;
    $par{'exception_ips'}   =~ s/\n/&/g;
    $par{'exception_ips'}   =~ s/\r/r/g;

    $status = 0;
    $mesg = "检测合格";
    return ( $status, $mesg );
}

sub add_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未添加" );

    ( $status, $mesg ) = &add_data_handler();

    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }

    #===获取特征事件的SID===#
    $par{'sid'} = &get_config_line_sid();
    if ( $par{'sid'} < 0 ) {
        $status = -1;
        $mesg = "获取特征事件SID失败";
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===向文件写入特征事件配置信息===#
    my $record = &get_config_record( \%par );
    ( $status, $mesg ) = &append_one_record( $conf_file, $record );
    if ( $status != 0 ) {
        $mesg = "向文件写入特征事件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===生成自定义特征事件===#
    system( "$create_eventrules" );
    $status = $?;
    if ( $status != 0 ) {
        $mesg = "生成自定义特征事件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===矫正特征事件库特征事件===#
    my $rule_lib = $par{'rule_lib'};
    my $cmd = "$rectify_eventrules -l '$rule_lib' -s $par{'sid'} -a"; #添加时的矫正命令
    if ( $rule_lib ne "" ) {
        system( "$cmd" );
        $status = $?;
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "添加成功";
    } else {
        $mesg = "添加失败";
    }

    &send_status( $status, $reload, $mesg );
}

sub prepare_note($) {
    my $note = shift;
    $note =~ s/\n/ /g;
    $note =~ s/\r//g;
    $note =~ s/,/，/g;
    return $note;
}

sub import_data_check() {
    my ( $status, $mesg ) = ( -1, "未导入" );
    my $cgi = new CGI; 
    my $upload_file = $cgi->param('rules_file');

    if ( $upload_file eq "" ) {
        $mesg = "未检测到上传文件";
        return ( $status, $mesg ); 
    }

    #===将数据写到tmp目录下===#
    my $count = 0;
    open( UPLOAD, ">$imported_filename" ) or return ( $status, "打开写文件失败" );
    binmode UPLOAD;
    while( <$upload_file> ) {
        $count++;
        print UPLOAD;
    }
    close UPLOAD;

    if ( !$count ) {
        $mesg = "上传文件内容为空";
        return ( $status, $mesg );
    }

    $status = 0;
    return ( $status, $mesg );
}

sub import_data(){
    my ( $status, $mesg ) = &import_data_check();
    if ( $status == 0 ) {
        system( "$import_events" );
        $status = $?;
        if ( $status != 0 ) {
            $errormessage = "事件导入系统失败";
        } else {
            &create_need_reload_tag();
            $notemessage = "导入成功";
        }
    } else {
        $errormessage = $mesg;
    }

    &show_page();
}

sub generate_selected_download_file() {
    #===第一步:根据上传的数据,筛选出要下载的规则文件===#
    my ( $status, $mesg ) = ( -1, "未生成导出文件" );
    if ( $query{'id'} eq "" ) {
        $mesg = "未选择导出项";
        return ( $status, $mesg );
    }
    $query{'id'} =~ s/\|/&/g;
    my $line_nums = $query{'id'};
    my @lines;
    ( $status, $mesg ) = &get_several_records( $conf_file, $line_nums, \@lines );
    if ( $status != 0 ) {
        return ( $status, $mesg );
    }
    my @rules_sid;
    my $length = @lines;
    for( my $i = 0; $i < @lines; $i++ ) {
        my %data = &get_config_hash( $lines[$i] );
        push( @rules_sid, $data{'sid'});
    }
    my $sids = join "&", @rules_sid;
    #===第二步:调用后台的命令,生成下载的文件===#
    my $export_file_cmd = $export_events." '$sids'";
    system( $export_file_cmd );
    $status = $?>>8;
    return ( $status, $mesg );
}

sub export_selected() {
    my ( $status, $mesg ) = &generate_selected_download_file();
    if( $status == 0 ){
        my $file_modified_time = &get_file_mtime_by_formatday( $to_export_file, "-" );
        my $export_filename = "export-".$file_modified_time.".events";

        open( DOWNLOADFILE, "<$to_export_file" ) or $status = -1;
        @fileholder = <DOWNLOADFILE>;
        close ( DOWNLOADFILE ); 

        if ( $status == 0 ) {
            print "Content-Type: application/x-download\n";  
            print "Content-Disposition: attachment;filename=$export_filename\n\n";
            print @fileholder;
            exit;
        } else {
            &showhttpheaders();
            $errormessage = "读取导出内容失败";
            &show_page();
        }
    }
    else{
        &showhttpheaders();
        $errormessage = $mesg;
        &show_page();
    }
}

sub delete_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未删除" );

    ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
    if ( $status != 0 ) {
        $mesg = "读取配置文件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    #===获取所有SID===#
    my @sids = ();
    my @lines_num = split( "&", $par{'id'} );
    for ( my $i = 0; $i < @lines_num; $i++ ) {
        my $line_num = $lines_num[$i];
        my %hash = &get_config_hash( $lines[$line_num] );
        push( @sids, $hash{'sid'} );
    }
    my $sid = join "&", @sids;
    #===删除符合条件的特征事件===#
    my $cmd = "$rectify_eventrules -s '$sid' -f";
    system( "$cmd" );
    $status = $?;
    if( $status != 0 ) {
        $mesg = "从规则库中移除规则失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'} );

    #===不管从特征库自定义文件中删除特征事件成功与否，都要重新生成规则===#
    system( "$create_eventrules" );

    if( $status == 0 && $? == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "删除成功";
    } else {
        $mesg = "删除失败";
    }

    &send_status( $status, $reload, $mesg );
}

sub toggle_enable($) {
    my $enable = shift;
    my @lines = ();
    my $reload = 0;

    my ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        $mesg = "操作失败";
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
        $mesg = "操作失败";
    } else {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "操作成功";
    }

    &send_status( $status, $reload, $mesg );
    return;
}

sub check_event_content {
    &send_status( 0, 0, "yes" );
}

sub apply_data() {
    system( "touch $ips_running_flag" );
    system( $restart_ips_service );
    my ( $status, $reload, $mesg ) = ( $?>>8, 0, "未开始应用" );
    if ( $status == 0 ) {
        &clear_need_reload_tag();
        $reload = 0;
        $mesg = "应用成功";
    } else {
        $reload = 1;
        $mesg = "应用失败";
    }
    &send_status( $status, $reload, $mesg );
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

    if( !-e $sid_file ) {
        system("touch $sid_file");
        system("echo 1005000000 > $sid_file");
    }
}
