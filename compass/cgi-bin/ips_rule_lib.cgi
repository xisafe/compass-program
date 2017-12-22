#!/usr/bin/perl
#==============================================================================#
#
# 描述: 特征库管理页面
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.08.21 WangLin创建
#
#==============================================================================#
use Encode;
use Digest::SHA qw(sha1_hex);

require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'file_relevant_time.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $extraheader;        #存放用户自定义JS
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
}

sub init_data(){
    $custom_dir = '/idps_console/rule_libraries';
    $conf_dir   = "${swroot}".$custom_dir;
    $conf_file  = $conf_dir.'/config';
    $template_conf_file = "${swroot}/idps_console/rules/policy_template/config";
    $conf_file_engine   = "${swroot}/idps/engine/settings";

    $to_export_file     = '/tmp/export.elib';
    $imported_filename  = '/tmp/user_import.elib';
    $respond_type_file  = '/etc/efw/idps_console/respond/respond_type';

    $add_rules          = 'sudo /usr/local/bin/idps_console/init_evnetconfig_ofrulelib.py';
    $merge_rule_lib     = 'sudo /usr/local/bin/idps_console/mergerulelib.py';
    $export_import_lib  = 'sudo /usr/local/bin/idps_console/export_import_eventlibrary.py';
    $export_rule_lib    = $export_import_lib.' -e -n';
    $import_rule_lib    = $export_import_lib.' -i -f '.$imported_filename;
    $rectify_eventrules = 'sudo /usr/local/bin/idps_console/rectify_libsandcerules.py';
    $add_events_to_lib_cmd = 'sudo /usr/local/bin/idps_console/init_evnetconfig_ofrulelib.py';

    $load_event_data_cmd        = 'sudo /usr/local/bin/idps_console/get_allevents_info.py';
    $load_event_grid_data_cmd   = 'sudo /usr/local/bin/idps_console/get_alleventinfo_of_rulelibrary.py -l';
    $load_event_detail_data_cmd = 'sudo /usr/local/bin/idps_console/get_event_detail.py -s';
    $load_event_config_cmd      = 'sudo /usr/local/bin/idps_console/get_eventconfig_of_rulelibrary.py';

    $need_reload_tag        = "${swroot}/idps/need_reload_tag";
    $ips_running_flag       = "${swroot}/idps/engine/apping_flage";
    $restart_ips_service    = "/usr/local/bin/restartips";
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/extjs/resources/css/ext-all.css">
                    <link rel="stylesheet" type="text/css" href="/include/ips_rule_lib.css" />
                    <script language="JavaScript" src="/include/waiting.js"></script>
                    <script type="text/javascript" src="/extjs/ext-debug.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/ips_check_running.js"></script>
                    <script language="JavaScript" src="/include/ips_rule_lib.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};

    if($action ne 'export_data' && $query_action ne 'export_data' && $query_action ne 'export_selected') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ( $action eq 'save_data' && $panel_name eq 'rule_libraries_add'  ) {
        &save_data();
    }
    elsif ( $action eq 'save_data' && $panel_name eq 'rule_libraries_merge'  ) {
        &merge_data();
    }
    elsif ( $action eq 'save_data' && $panel_name eq 'rule_libraries_copy'  ) {
        &copy_data();
    }
    elsif ( $action eq 'save_data' && $panel_name eq 'rule_lib_edit_event' ) {
        &edit_event_data();
    }
    elsif ( $action eq 'add_events_to_lib' ) {
        &add_events_to_lib();
    }
    elsif ( $action eq 'apply_template_to_event_item' ) {
        &apply_template_to_event_item();
    }
    elsif ( $action eq 'load_data' && $panel_name eq 'rule_libraries_list' ) {
        &load_data();
    }
    elsif ( $action eq 'load_data' && $panel_name eq 'template_list_panel' ) {
        &load_policy_template();
    }
    elsif ( $action eq 'load_init_data' ) {
        &load_init_data();
    }
    elsif ( $action eq 'load_event_detail_data' ) {
        &load_event_detail_data();
    }
    elsif ( $action eq 'load_event_config' ) {
        &load_event_config();
    }
    elsif ( $action eq 'import_data' && $panel_name eq 'rule_libraries_import' ) {
        &import_data();
    }
    elsif ( $action eq 'load_event_data' ) {
        &load_event_data();
    }
    elsif ( $action eq 'load_event_grid_data' ) {
        &load_event_grid_data();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ( $action eq 'delete_data') {
        &delete_data();
    }
    elsif ( $action eq 'delete_event_item' ) {
        &delete_event_item();
    }
    elsif ($action eq 'enable_data') {
        &toggle_enable( "on" );
    }
    elsif ($action eq 'enable_event_item') {
        &toggle_event_data( "on" );
    }
    elsif ($action eq 'disable_data') {
        &toggle_enable( "off" );
    }
    elsif ($action eq 'disable_event_item') {
        &toggle_event_data( "off" );
    }
    else {
        if($query_action eq 'export_data') {
            #==导出数据,可以导出特定几列的数据==#
            &export_data();
        } else {
            &show_page();
        }
    }
}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &closebigbox();
    &display();
    &closepage();
}

sub display() {
    printf<<EOF
    <div id="rule_libraries_mesg_box"></div>
    <div id="rule_libraries_add" class="container"></div>
    <div id="rule_libraries_merge" class="container"></div>
    <div id="rule_libraries_copy" class="container"></div>
    <div id="rule_libraries_import" class="container"></div>
    <div id="rule_lib_edit_event" class="container"></div>
    <div id="rule_libraries_list" class="container"></div>
    <div id="template_list_panel" class="container"></div>
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
    $config{'name'}         = $temp[0];
    $config{'note'}         = $temp[1];
    $config{'type'}         = $temp[2];
    $config{'create_time'}  = $temp[3];
    $config{'filepath'}     = $temp[4];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'note'} );
    push( @record_items, $hash_ref->{'type'} );
    push( @record_items, $hash_ref->{'create_time'} );
    push( @record_items, $hash_ref->{'filepath'} );
    return join ",", @record_items;
}

sub get_template_config_hash() {
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
    $config{'template_name'}    = $temp[0];
    $config{'template_note'}    = $temp[1];
    $config{'modified_time'}    = $temp[2];
    $config{'apply_scope'}      = $temp[3];
    $config{'respond_type'}     = $temp[4];
    $config{'merge_type'}       = $temp[5];
    $config{'merge_interval'}   = $temp[6];
    $config{'max_merge_count'}  = $temp[7];
    $config{'exception_type'}   = $temp[8];
    $config{'exception_ips'}    = $temp[9];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_lib_event_hash($) {
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
    $config{'sid'}              = $temp[0];
    $config{'id'}               = $temp[0];
    $config{'event_name'}       = $temp[1];
    $config{'event_type'}       = $temp[2];
    $config{'event_enable'}     = $temp[3];
    $config{'respond_type'}     = $temp[4];
    $config{'merge_type'}       = $temp[5];
    $config{'merge_interval'}   = $temp[6];
    $config{'max_merge_count'}  = $temp[7];
    $config{'exception_type'}   = $temp[8];
    $config{'exception_ips'}    = $temp[9];

    if ( $config{'merge_type'} eq "" ) {
        $config{'merge_type'} = "none";
    }

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_event_config_hash($) {
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
    $config{'id'}               = $temp[0];
    $config{'event_enable'}     = $temp[1];
    $config{'respond_type'}     = $temp[2];
    $config{'merge_type'}       = $temp[3];
    $config{'merge_interval'}   = $temp[4];
    $config{'max_merge_count'}  = $temp[5];
    $config{'exception_type'}   = $temp[6];
    $config{'exception_ips'}    = $temp[7];

    if ( $config{'merge_type'} eq "" ) {
        $config{'merge_type'} = "none";
    }

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_engine_config_hash($) {
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
    $config{'deploy'}           = $temp[0];
    $config{'interface'}        = $temp[1];
    $config{'rule_lib'}         = $temp[2];
    $config{'checking_obj'}     = $temp[3];
    $config{'enable_engine'}    = $temp[4];
    $config{'enable_log'}       = $temp[5];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_event_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'id'} );
    push( @record_items, $hash_ref->{'event_enable'} );
    push( @record_items, $hash_ref->{'respond_type'} );
    push( @record_items, $hash_ref->{'merge_type'} );
    push( @record_items, $hash_ref->{'merge_interval'} );
    push( @record_items, $hash_ref->{'max_merge_count'} );
    push( @record_items, $hash_ref->{'exception_type'} );
    push( @record_items, $hash_ref->{'exception_ips'} );
    for( my $i = 0; $i < 10; $i++ ) {
        push( @record_items, $hash_ref->{''} );
    }
    return join ",", @record_items;
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

sub get_rules_sid($) {
    my $lib_path = shift;
    my @content_lines, @sids;

    &read_config_lines( $lib_path, \@content_lines );
    foreach my $line ( @content_lines ) {
        my @temp = split( ",", $line );
        push( @sids, $temp[0] );
    }

    return join "&", @sids;
}

sub prepare_note($) {
    my $note = shift;
    $note =~ s/\n/ /g;
    $note =~ s/\r//g;
    $note =~ s/,/，/g;
    return $note;
}

sub save_data_handler($) {
    my $item_id = shift;
    my ( $status, $mesg, $name_exist_line_num ) = ( -1, "操作失败", "" );

    #===第一步，检查重名===#
    ( $status, $mesg, $name_exist_line_num ) = &where_is_field( $conf_file, ",", 0, $par{'name'} );
    if ( $name_exist_line_num ne "" ) {
        $status = -1;
        $mesg = "名称已存在";
        return ( $status, $mesg );
    }

    #===第二步，检查说明字符串长度 0-120个字符,并处理空行和非法字符===#
    # $par{'note'} = &prepare_note( $par{'note'} );
    # my $notes_len = split( "", $par{'note'} );
    # if ( $notes_len > 120 ) {
    #     $status = -1;
    #     $mesg = "说明信息0-120个字符";
    #     return ( $status, $mesg );
    # }

    if ( $par{'panel_name'} eq "rule_libraries_add" ) {
        #===添加特征库，检查是否选中特征事件====#
        if ( $par{'rules_id'} eq "" ) {
            $status = -1;
            $mesg = "请选择特征事件";
            return ( $status, $mesg );
        }
    }

    if ( $par{'panel_name'} eq "rule_libraries_merge" ) {
        #===合并特征库，检查是否选中特征库===#
        if ( $par{'choosed_rule_libs'} eq "" ) {
            $status = -1;
            $mesg = "请选择要合并的特征库";
            return ( $status, $mesg );
        }
    }
    

    #===新建,此处只存在新建，不存在修改特征库名称说明等操作===#
    my $filename = sha1_hex( $par{'name'} );
    my $filepath = $conf_dir."/".$filename.".info";
    system( "touch $filepath" );
    if( $? != 0 ) {
        $mesg = "创建文件失败";
        return ( $status, $mesg );
    }

    my $cday = &get_file_ctime_by_formatday( $filepath, "-" );
    my $cdaytime = &get_file_ctime_by_formatdaytime( $filepath, ":" );
    my $create_time = $cday." ".$cdaytime;

    $par{'type'} = "custom";
    $par{'filepath'} = $filepath;
    $par{'create_time'} = $create_time;

    $status = 0;
    $mesg = "创建成功";

    return ( $status, $mesg );
}

sub save_data() {
    my $reload = 0;
    my $item_id = $par{'id'};
    my ( $status, $mesg ) = ( -1, "未保存" );
    my $record;

    ( $status, $mesg ) = &save_data_handler( $item_id );
    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }

    $record = &get_config_record( \%par );
    ( $status, $mesg ) = &append_one_record( $conf_file, $record );

    my $lib_name = $par{'name'};
    my $rules_id = $par{'rules_id'};

    if ( $status == 0 ) {
        my $add_rules_cmd = $add_rules." -l $lib_name -s '$rules_id'";
        system( $add_rules_cmd );
        $status = $?>>8;
    } else {
        $mesg = "保存至文件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    if ( $status == 0 ) {
        my $rectify_rules_cmd = $rectify_eventrules." -l $lib_name -s '$rules_id' -a";
        system( $rectify_rules_cmd );
        $status = $?>>8;
    } else {
        $mesg = "保存事件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    if( $status == 0 ) {
        $mesg = "新建成功";
        $reload = 1;
        &create_need_reload_tag();
    } else {
        $mesg = "矫正事件失败";
    }

    &send_status( $status, $reload, $mesg );
}

sub add_events_to_lib() {
    my ( $status, $reload, $mesg, $lib_name, $sids ) = ( -1, 0, "未开始添加规则", $par{'lib_name'}, $par{'id'} );
    my $add_to_lib_cmd = "$add_events_to_lib_cmd -l $lib_name -s '$sids'";
    my $rectify_rules_cmd = "$rectify_eventrules -l $lib_name -s '$sids' -a";

    #===判断是否选择了特征事件，没选择返回错误消息===#
    if ( $sids eq "" ) {
        $mesg = "未选择特征事件，新增失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    #===添加===#
    system( $add_to_lib_cmd );
    $status = $?>>8;
    if ( $status != 0 ) {
        $mesg = "向特征库新增事件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    #===矫正===#
    system( $rectify_rules_cmd );
    $status = $?>>8;
    if ( $status != 0 ) {
        $mesg = "矫正特征库失败";
    } else {
        $mesg = "添加成功";
        $reload = 1;
        &create_need_reload_tag();
    }


    &send_status( $status, $reload, $mesg );

}

sub merge_data() {
    my $reload = 0;
    my $item_id = $par{'id'};
    my ( $status, $mesg ) = ( -1, "未保存" );
    my $record;

    ( $status, $mesg ) = &save_data_handler($item_id);
    if( $status == 0 ) {
        $record = &get_config_record( \%par );
        ( $status, $mesg ) = &append_one_record( $conf_file, $record );
    } else {
        &send_status( $status, $reload, $mesg );
        return;
    }

    if ( $status == 0 ) {
        $par{'choosed_rule_libs'} =~ s/\n/&/g;
        $par{'choosed_rule_libs'} =~ s/\r//g;
        my $choosed_rule_libs = $par{'choosed_rule_libs'};
        my $merge_rule_lib_cmd = $merge_rule_lib." -n $par{'name'} -m '$choosed_rule_libs'";
        system( $merge_rule_lib_cmd );
        $status = $?>>8;
    } else {
        $mesg = "保存事件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    if( $status == 0 ) {
        $mesg = "合并成功";
        $reload = 1;
        &create_need_reload_tag();
    } else {
        $mesg = "合并失败";
    }

    &send_status( $status, $reload, $mesg );
}

sub copy_data() {
    my $reload = 0;
    my $item_id = $par{'id'};
    my ( $status, $mesg ) = ( -1, "未保存" );
    my $record;

    ( $status, $mesg ) = &save_data_handler($item_id);
    if( $status == 0 ) {
        $record = &get_config_record( \%par );
        ( $status, $mesg ) = &append_one_record( $conf_file, $record );
    } else {
        &send_status( $status, $reload, $mesg );
        return;
    }

    if ( $status == 0 ) {
        my $to_copy_line = "";
        ( $status, $mesg, $to_copy_line ) = &get_one_record( $conf_file, $par{'to_copy_lib'} );
        my %to_copy_hash = &get_config_hash( $to_copy_line );
        
        # 第一步，拷贝内容
        my @to_copy_content, $total_num;
        ( $status, $mesg, $total_num ) = &read_config_lines( $to_copy_hash{'filepath'}, \@to_copy_content );
        if ( $total_num > 0 ) {
            # 有内容就写到衍生文件中去
            ( $status, $mesg ) = &write_config_lines( $par{'filepath'}, \@to_copy_content );

            # 第二步，提取所有内容的ID,调用矫正命令
            my $sids = &get_rules_sid( $to_copy_hash{'filepath'} );
            my $rectify_rules_cmd = $rectify_eventrules." -l $par{'name'} -s '$sids' -a";
            system( $rectify_rules_cmd );
            $status = $?>>8;
        }

    } else {
        $mesg = "保存事件失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    if( $status == 0 ) {
        $mesg = "衍生成功";
        $reload = 1;
        &create_need_reload_tag();
    } else {
        $mesg = "衍生库失败";
    }

    &send_status( $status, $reload, $mesg );
}

sub get_rule_lib_path() {
    my ( $status, $mesg, $lib_record, $lib_path, $total_num ) = ( -1, 0, "未开始读取数据", "", "", 0 );

    ( $status, $mesg, $lib_record ) = &get_one_record( $conf_file, $par{'lib_id'} );
    if( $status != 0 ) {
        $mesg = "读取特征库信息失败";
        return ( $status, $mesg, $lib_path );
    }

    my %lib_hash = &get_config_hash( $lib_record );
    if ( !$lib_hash{'valid'} ) {
        $status = -1;
        $mesg = "读取的特征库信息不合法";
    } else {
        $lib_path = $lib_hash{'filepath'};
    }

    return ( $status, $mesg, $lib_path );
}

sub edit_event_data() {
    my ( $status, $reload, $mesg, $config_path, $total_num ) = ( -1, 0, "未开始读取数据", "", 0 );
    #===第一步，找到事件所在的特征库信息文件的路径===#
    ( $status, $mesg, $config_path ) = &get_rule_lib_path();
    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===第二步，读取特征库信息详细文件中的信息===#
    my @event_records = ();
    ( $status, $mesg, $total_num ) = &read_config_lines( $config_path, \@event_records );
    if ( $status != 0 ) {
        $mesg = "读取特征事件原有配置信息失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    #===第三步，找到特征库信息详细文件中关于该特征事件的记录并更新===#
    my $updated_flag = 0;
    for ( my $i = 0; $i < $total_num; $i++ ) {
        my %hash = &get_event_config_hash( $event_records[$i] );
        #===找到了要更新的项===#
        if ( $hash{'id'} eq $par{'id'} ) {
            ( $status, $mesg ) = &save_event_data_handler();
            if ( $status != 0 ) {
                &send_status( $status, $reload, $mesg );
                return;
            }
            my $record = &get_event_config_record( \%par );
            ( $status, $mesg ) = &update_one_record( $config_path, $i, $record );
            $updated_flag = 1;
            last;
        }
    }

    if ( $updated_flag ) {
        if ( $status == 0 ) {
            $reload = 1;
            &create_need_reload_tag();
            $mesg = "更新配置成功";
        } else {
            $mesg = "更新配置失败"
        }
    } else {
        $status = -1;
        $mesg = "未找到符合条件的特征事件";
    }

    &send_status( $status, $reload, $mesg );
}

sub save_event_data_handler() {
    my ( $status, $mesg ) = ( -1, "未开始检测数据合法性" );

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
    $par{'exception_ips'}   =~ s/\r//g;

    $status = 0;
    $mesg = "预处理成功";
    return ( $status, $mesg );
}

sub apply_template_to_event_item() {
    my ( $status, $reload, $mesg, $config_path, $template_record, $total_num ) = ( -1, 0, "未开始读取数据", "", "", 0 );
    #===第一步，获取模板中的信息====#
    ( $status, $mesg, $template_record ) = &get_one_record( $template_conf_file, $par{'template_id'} );
    if( $status != 0 ) {
        $mesg = "读取模板信息失败";
        &send_status( $status, $mesg, $lib_path );
        return;
    }

    my %T_hash = &get_template_config_hash( $template_record );
    if ( !$T_hash{'valid'} ) {
        $status = -1;
        $mesg = "读取的模板信息不合法";
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===第二步，找到事件所在的特征库信息文件的路径===#
    ( $status, $mesg, $config_path ) = &get_rule_lib_path();
    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===第三步，读取特征库信息详细文件中的信息===#
    my @event_records = ();
    ( $status, $mesg, $total_num ) = &read_config_lines( $config_path, \@event_records );
    if ( $status != 0 ) {
        $mesg = "读取特征事件原有配置信息失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $updated_flag = 0;
    my %toggle_ids = &get_record_keys_hash( $par{'id'}, "&" );
    for ( my $i = 0; $i < $total_num; $i++ ) {
        my %hash = &get_event_config_hash( $event_records[$i] );
        #===找到了要更新的项===#
        if ( $toggle_ids{$hash{'id'}} eq $hash{'id'} ) {
            $updated_flag = 1;
            #===将当前找到的项的对应字段更新为模板中的字段===#
            if ( $T_hash{'apply_scope'} =~ m/RESPOND/ ) {
                #===如果设置了响应方式===#
                $hash{'respond_type'} = $T_hash{'respond_type'};
            }
            if ( $T_hash{'apply_scope'} =~ m/MERGE/ ) {
                #===如果设置了合并方式===#
                $hash{'merge_type'} = $T_hash{'merge_type'};
                $hash{'merge_interval'} = $T_hash{'merge_interval'};
                $hash{'max_merge_count'} = $T_hash{'max_merge_count'};
            }
            if ( $T_hash{'apply_scope'} =~ m/EXCLUDE/ ) {
                #===如果设置了排除方式===#
                $hash{'exception_type'} = $T_hash{'exception_type'};
                $hash{'exception_ips'} = $T_hash{'exception_ips'};
            }
            my $record = &get_event_config_record( \%hash );
            $event_records[$i] = $record;
        }
    }

    if ( $updated_flag ) {
        ( $status, $mesg ) = &write_config_lines( $config_path, \@event_records );
        if ( $status == 0 ) {
            $reload = 1;
            &create_need_reload_tag();
            $mesg = "应用模板成功";
        } else {
            $mesg = "应用模板失败";
        }
    } else {
        $status = -1;
        $mesg = "未找到符合条件的特征事件";
    }

    &send_status( $status, $reload, $mesg );
}

sub delete_event_item() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未删除数据" );
    my $lib_name = $par{'lib_name'};
    my $sids = $par{'id'};
    my $to_delete_cmd = "$rectify_eventrules -l $lib_name -s '$sids' -r";
    system( $to_delete_cmd );
    $status = $?>>8;
    if( $status != 0 ) {
        $mesg = "删除失败";
    } else {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "删除成功";
    }
    &send_status( $status, $reload, $mesg );
}

sub toggle_event_data($) {
    my $enable = shift;
    my $operation = "启用";
    if ( $enable ne "on" ) {
        $operation = "禁用";
    }
    my ( $status, $reload, $mesg, $config_path, $total_num ) = ( -1, 0, "未开始读取数据", "", 0 );
    #===第一步，找到事件所在的特征库信息文件的路径===#
    ( $status, $mesg, $config_path ) = &get_rule_lib_path();
    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }
    #===第二步，读取特征库信息详细文件中的信息===#
    my @event_records = ();
    ( $status, $mesg, $total_num ) = &read_config_lines( $config_path, \@event_records );
    if ( $status != 0 ) {
        $mesg = "读取特征事件原有配置信息失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $updated_flag = 0;
    my %toggle_ids = &get_record_keys_hash( $par{'id'}, "&" );
    for ( my $i = 0; $i < $total_num; $i++ ) {
        my %hash = &get_event_config_hash( $event_records[$i] );
        #===找到了要更新的项===#
        if ( $toggle_ids{$hash{'id'}} eq $hash{'id'} ) {
            $updated_flag = 1;
            $hash{'event_enable'} = $enable;
            my $record = &get_event_config_record( \%hash );
            $event_records[$i] = $record;
        }
    }

    if ( $updated_flag ) {
        ( $status, $mesg ) = &write_config_lines( $config_path, \@event_records );
        if ( $status == 0 ) {
            $reload = 1;
            &create_need_reload_tag();
            $mesg = "$operation成功";
        } else {
            $mesg = "$operation失败";
        }
    } else {
        $status = -1;
        $mesg = "未找到符合条件的特征事件";
    }

    &send_status( $status, $reload, $mesg );
}

sub generate_download_file() {
    #===第一步:根据上传的数据,筛选出要下载的规则文件===#
    my ( $status, $mesg, $record  ) = ( -1, "未生成导出文件", "" );
    if ( $query{'id'} eq "" ) {
        $mesg = "未选中导出项";
        return ( $status, $mesg );
    }
    ( $status, $mesg, $record ) = &get_one_record( $conf_file, $query{'id'} );
    if ( $status != 0 ) {
        $mesg = "未检测到可导出项";
        return ( $status, $mesg );
    }
    my %data = &get_config_hash( $record );
    #===第二步:调用后台的命令,生成下载的文件===#
    my $export_file_cmd = $export_rule_lib." $data{'name'}";
    system( $export_file_cmd );
    $status = $?>>8;
    if( $status != 0 ) {
        $mesg = "执行导出命令失败";
    }
    return ( $status, $mesg );
}

sub export_data() {
    my ( $status, $mesg ) = &generate_download_file();
    if( $status == 0 ){
        my $file_modified_time = &get_file_mtime_by_formatday( $to_export_file, "-" );
        my $export_filename = "export-".$file_modified_time.".elib";

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

sub import_data_check() {
    my ( $status, $mesg ) = ( -1, "未导入" );
    my $cgi = new CGI; 
    my $upload_file = $cgi->param('rule_lib_file');

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
        system( "$import_rule_lib" );
        $status = $?;
        if ( $status != 0 ) {
            $errormessage = "特征库导入系统失败";
        } else {
            &create_need_reload_tag();
            $notemessage = "导入成功";
        }
    } else {
        $errormessage = $mesg;
    }

    &show_page();
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
    %ret_data->{'reload'} = 0;
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_policy_template() {
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_template_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'page_size'} = $total_num;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_event_data()  {
    my %ret_data, @content_array;
    my $lib_name = $par{'lib_name'};
    my $get_data_cmd = $load_event_data_cmd;

    #===判断是否是加载全部，还是排除某一特征库之外的特征事件====#
    if ( $lib_name eq "" ) {
        #====加载全部====#
        $get_data_cmd .= " -a";
    } else {
        $get_data_cmd .= " -e $lib_name -a";
    }

    my $data_str = `$get_data_cmd`;
    my $search = &prepare_search( $par{'search'} );

    my $data_hash = $json->decode( $data_str );

    my $my_type_events = $data_hash->{$par{'type'}};
    my $total_num = 0;

    while( my ($event_class, $event_value) = each %$my_type_events ) {
        my @sub_events;
        my $init_num = $total_num;
        foreach my $event ( @$event_value ) {
            my %hash = (
                id   => $event->{'id'},
                name => $event->{'name'},
                text => $event->{'name'},
                leaf => "true",
            );
            if ( $search ne "" ) {
                my $name = lc $hash{'name'};
                if ( $name =~ m/$search/ ) {
                    push( @sub_events, \%hash );
                    $total_num++;
                }
            } else {
                push( @sub_events, \%hash );
                $total_num++;
            }
        }

        if ( $init_num == $total_num ) {
            #===说明没有增加记录===#
            next;
        }

        my %hash = (
            id      => $event_class,
            name    => $event_class,
            text    => $event_class,
            leaf    => "false",
            # expanded => "true",
            expanded => "false",
            children => \@sub_events,
        );
        push( @content_array, \%hash );
    }

    %ret_data->{'total'} = $total_num;
    %ret_data->{'children'} = \@content_array;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_event_grid_data() {
    my %ret_data, @content_array;
    my $get_data_cmd = "$load_event_grid_data_cmd $par{'lib_name'}";
    my $data_str = `$get_data_cmd`;
    my $search = &prepare_search( $par{'search'} );
    `echo "$get_data_cmd" >/tmp/get_data_cmd`;

    my $data_hash = $json->decode( $data_str );

    my $my_type_events = $data_hash->{$par{'type'}};
    my $total_num = 0;

    while( my ($event_class, $event_value) = each %$my_type_events ) {
        my @sub_events;
        my $init_num = $total_num;
        foreach my $event ( @$event_value ) {
            $event->{leaf} = "true";
            $event->{text} = $event->{'name'};
            if ( $search ne "" ) {
                my $name = lc( $event->{'name'} );
                if ( $name =~ m/$search/ ) {
                    push( @sub_events, $event );
                    $total_num++;
                }
            } else {
                push( @sub_events, $event );
                $total_num++;
            }
        }
        
        if ( $init_num == $total_num ) {
            #===说明没有增加记录===#
            next;
        }

        my %hash = (
            id      => $event_class,
            name    => $event_class,
            text    => $event_class,
            leaf    => "false",
            # expanded => "true",
            expanded => "false",
            children => \@sub_events,
        );
        push( @content_array, \%hash );
    }

    %ret_data->{'total'} = $total_num;
    %ret_data->{'children'} = \@content_array;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_init_data() {
    my @respond_type;

    ( $status, $mesg, $total_num ) = &get_respond_type( \@respond_type );

    %ret_data->{'respond_type'} = \@respond_type;
    %ret_data->{'mesg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_event_detail_data() {
    my $get_data_cmd = "$load_event_detail_data_cmd $par{'id'} 2>/dev/null";

    my $ret_data = `$get_data_cmd`;
    if ($? != 0 ) {
        print "error";
    }

    print $ret_data;
}

sub load_event_config() {
    my $get_data_cmd = "$load_event_config_cmd -l $par{'lib_name'} -s $par{'id'} 2>/dev/null";
    my $ret = "";

    my $record = `$get_data_cmd`;
    if ( $? != 0 ) {
        $ret_data{'status'} = $?>>8;
        $ret_data{'mesg'} = "执行命令失败";
        my $ret = $json->encode(\%ret_data);
        print $ret;
        return;
    }
    my %hash = &get_lib_event_hash( $record );
    if ( !$hash{'valid'} ) {
        $ret_data{'status'} = -1;
        $ret_data{'mesg'} = "获取数据不合法";
        my $ret = $json->encode(\%ret_data);
        print $ret;
        return;
    }

    $ret_data{'status'} = 0;
    $ret_data{'mesg'} = "获取数成功";
    $ret_data{'data'} = \%hash;

    &load_event_config_handler( \%hash );

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_event_config_handler($) {
    my $hash_ref = shift;
    $hash_ref->{'respond_type'}     =~ s/&/\|/g;
    $hash_ref->{'protocol_port'}    =~ s/&/\n/g;
    $hash_ref->{'exception_ips'}    =~ s/&/\n/g;
}

sub get_template_detail_data($) {
    my $content_array_ref = shift;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    ( $status, $mesg, $total_num ) = &read_config_lines( $template_conf_file, \@lines);

    for( my $i = 0; $i < @lines; $i++ ) {
        my %hash = &get_template_config_hash( $lines[$i] );
        if ( !$hash{'valid'} ) {
            $total_num--;
            next;
        }
        $hash{'id'} = $i;
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg, $total_num );
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

    for( my $i = 0; $i < @lines; $i++ ) {
        my $id = $from_num + $i;
        if( !$LOAD_ONE_PAGE ) {
            $id = $i;
        }
        my %hash = &get_config_hash( $lines[$i] );
        if (! $hash{'valid'}) {
            $total_num--;
            next;
        }
        if ( $search ne "" ) {
            my $name = lc $hash{'name'};
            my $note = lc $hash{'note'};
            if ( !($name =~ m/$search/) && !($note =~ m/$search/) 
                && !($hash{'create_time'} =~ m/$search/)) {
                #===对名字，说明，创建时间进行搜索===#
                $total_num--;
                next;
            }
        }
        $hash{'id'} = $id;
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg, $total_num );
}

sub delete_data() {
    my $reload = 0;
    my $item_ids = $par{'id'};
    my @lines, @to_delete_record_ids, @to_delete_files;
    my %ids_hash = &get_record_keys_hash( $item_ids, "&" );

    my ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }

    my ( $used_lib_count, $used_mesg ) = ( 0, "" );
    my @engine_lines;
    &read_config_lines($conf_file_engine,\@engine_lines);
    my %engine_config = &get_engine_config_hash( $engine_lines[0] );

    for ( my $i = 0; $i < @lines; $i++ ) {
        if( $ids_hash{$i} eq "$i" ) {
            my %hash = &get_config_hash( $lines[$i] );
            if ( $hash{'name'} eq $engine_config{'rule_lib'} ) {
                $used_lib_count++;
                $used_mesg = "$hash{'name'}正在使用中,删除失败";
                next;
            }
            if( $hash{'type'} eq 'custom' ) {
                #===提取文件中的sid，用户矫正===#
                my $sids = &get_rules_sid( $hash{'filepath'} );
                my $rectify_rules_cmd = "$rectify_eventrules -l $hash{'name'} -s '$sids' -r";
                if ( $sids ne "" ) {
                    #===不矫正===#
                    system( $rectify_rules_cmd );
                    if ( $? != 0 ) {
                        next;
                    }
                }
                
                #===矫正成功，再删除===#
                push( @to_delete_record_ids, $i );
                push( @to_delete_files, $hash{'filepath'} );
            }
        }
    }

    if ( @to_delete_record_ids == 0 ) {
        $status = -1;
        $mesg = "未检测到可删除项";
        if ( $used_lib_count > 0 ) {
            $mesg = $used_mesg;
        }
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $to_delete_files_str = join " ", @to_delete_files;
    my $to_delete_cmd = "rm ".$to_delete_files_str;

    system( $to_delete_cmd );
    $status = $?>>8;
    if ( $status != 0 ) {
        $mesg = "删除文件失败";
        if ( $used_lib_count > 0 ) {
            $mesg = $used_mesg;
        }
        &send_status( $status, $reload, $mesg );
        return;
    }

    ( $status, $mesg ) = &delete_several_records( $conf_file, join "&", @to_delete_record_ids );

    my $delete_count = @to_delete_record_ids;
    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "成功删除$delete_count个特征库";
        if ( $used_lib_count > 0 ) {
            $mesg .= "，$used_mesg";
        }
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
        $mesg = "";
        $reload = 1;
        &create_need_reload_tag();
    }

    &send_status( $status, $reload, $mesg );
    return;
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
}
