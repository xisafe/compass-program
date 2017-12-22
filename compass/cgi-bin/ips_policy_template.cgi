#!/usr/bin/perl
#==============================================================================#
#
# 描述: 入侵防御策略模板页面
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.11.21 WangLin创建
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
my $need_reload_tag;    #规则改变时需要重新应用的标识
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
}

sub init_data(){
    $custom_dir         = '/idps_console/rules/policy_template';
    $conf_dir           = "${swroot}".$custom_dir;
    $conf_file          = $conf_dir.'/config';
    # $need_reload_tag    = $conf_dir.'/policy_template_need_reload';

    #============扩展的CSS和JS文件-BEGIN========================================================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/ips_policy_template.js"></script>';
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
    if ( $action eq 'save_data' ) {
        &save_data();
    }
    elsif ( $action eq 'load_data' ) {
        &load_data();
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
    else {
        &show_page();
    }
}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &display();
    &closepage();
}

sub display() {
    printf<<EOF
    <div id="template_mesg_box" style="width: 96%;margin: 20px auto;"></div>
    <div id="template_add_panel" style="width: 96%;margin: 20px auto;"></div>
    <div id="list_template_panel" style="width: 96%;margin: 20px auto;"></div>
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

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'template_name'} );
    push( @record_items, $hash_ref->{'template_note'} );
    push( @record_items, $hash_ref->{'modified_time'} );
    push( @record_items, $hash_ref->{'apply_scope'} );
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

sub get_compare_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'template_name'} );
    push( @record_items, $hash_ref->{'template_note'} );
    push( @record_items, $hash_ref->{'apply_scope'} );
    push( @record_items, $hash_ref->{'respond_type'} );
    push( @record_items, $hash_ref->{'merge_type'} );
    push( @record_items, $hash_ref->{'merge_interval'} );
    push( @record_items, $hash_ref->{'max_merge_count'} );
    push( @record_items, $hash_ref->{'exception_type'} );
    push( @record_items, $hash_ref->{'exception_ips'} );
    return join ",", @record_items;
}

sub prepare_note($) {
    my $note = shift;
    $note =~ s/\n/ /g;
    $note =~ s/\r//g;
    $note =~ s/,/，/g;
    return $note;
}

sub save_data_handler() {
    my ( $status, $mesg ) = ( -1, "未开始检测各项的合法性" );

    #===第一步，检查名称是否重名===#
    my $name_exist_line_num = "";
    ( $status, $mesg, $name_exist_line_num ) = &where_is_field( $conf_file, ",", 0, $par{'template_name'} );
    
    if ( $name_exist_line_num ne "" ) {
        #===如果检测到已存在，则允许是编辑的情况，并且只能是原来的行===#
        if ( $par{'id'} ne "" && $par{'id'} eq $name_exist_line_num ) {
            #===允许通过===#
        } else {
            $status = -1;
            $mesg = "名称已存在";
            return ( $status, $mesg );
        }
    }
   
    #===第二步，检查说明字符串长度 0-128个字符,并处理空行和非法字符===#
    # $par{'template_note'} = &prepare_note( $par{'template_note'} );
    # my $notes_len = split( "", $par{'template_note'} );
    # if ( $notes_len > 128 ) {
    #     $status = -1;
    #     $mesg = "说明信息0-128个字符";
    #     return ( $status, $mesg );
    # }

    #===第三步，检查应用范围是否为空===#
    $par{'apply_scope'}     =~ s/\|/&/g;
    if ( $par{'apply_scope'} eq "" ) {
        $status = -1;
        $mesg = "至少选择一个应用类别";
        return ( $status, $mesg );
    }

    #===获取当前时间===#
    my $time_stamp = time();
    my $day = &get_time_by_formatday( $time_stamp, "-" );
    my $sec = &get_time_by_formatdaytime( $time_stamp, ":" );
    $par{'modified_time'} = "$day $sec";

    $par{'respond_type'}    =~ s/\|/&/g;
    $par{'exception_ips'}   =~ s/\n/&/g;
    $par{'exception_ips'}   =~ s/\r//g;
    $par{'exception_ips'}   =~ s/(^s+|s+$)//g;

    #===对ip地址进行去重===#
    my @exception_ips = split( "&", $par{'exception_ips'} );

    # @exception_ips = &trim_redundancy( \@exception_ips );

    $par{'exception_ips'} = join( "&", @exception_ips );
   
    #===根据选择的配置项，将响应的其他项置空====#
    if ( !($par{'apply_scope'} =~ m/RESPOND/) ) {
                #===如果设置了响应方式===#
        $par{'respond_type'} = "";
    } else {
        if ( $par{'respond_type'} eq "" ) {
            $status = -1;
            $mesg = "至少选择一种响应方式";
            return ( $status, $mesg );
        }
    }
    if ( !($par{'apply_scope'} =~ m/MERGE/) ) {
        #===如果设置了合并方式===#
        $par{'merge_type'} = "";
        $par{'merge_interval'} = "";
        $par{'max_merge_count'} = "";
    }
    if ( !($par{'apply_scope'} =~ m/EXCLUDE/) ) {
        #===如果设置了排除方式===#
        $par{'exception_type'} = "";
        $par{'exception_ips'} = "";
    }

    if ( $par{'merge_type'} eq "none" ) {
        $par{'merge_interval'} = "";
        $par{'max_merge_count'} = "";
    }

    if ( $par{'exception_type'} eq "none" ) {
        $par{'exception_ips'} = "";
    }
    

    #===如果当前是编辑状态，检测传上来的字段与现有字段是否一致，一致就不在进行更改===#
    if ( $par{'id'} ne "" ) {
        my $exist_record = &get_one_record( $conf_file, $par{'id'} );
        my %exist_record_hash = &get_config_hash( $exist_record );
        my $compare_record_old = &get_compare_record( \%exist_record_hash );
        my $compare_record_new = &get_compare_record( \%par );
        if ( $compare_record_old eq $compare_record_new ) {
            $status = -1;
            $mesg = "配置未改变";
        } else {
            $status = 0;
            $mesg = "检测合格";
        }
    } else {
        $status = 0;
        $mesg = "检测合格";
    }
    return ( $status, $mesg );
}

sub save_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未保存" );
    ( $status, $mesg ) = save_data_handler();
     # &send_status( $status, $reload, $mesg );
    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};

    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $conf_file, $record );
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
    }

    if( $status == 0 ) {
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
}

sub load_data(){
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'reload'} = 0;

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

        if ( $search ne "" ) {
            my $template_name = lc $hash{'template_name'};
            my $template_note = lc $hash{'template_note'};
            if ( !($template_name =~ m/$search/) && !($template_note =~ m/$search/) ) {
                #===对名字，说明，创建时间进行搜索===#
                $total_num--;
                next;
            }
        }

        $hash{'id'} = $id;
        &load_data_handler( \%hash );
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg, $total_num );
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

sub load_data_handler($) {
    my $hash_ref = shift;
    #===根据选择的配置项，将响应的其他项置空====#
    if ( !($hash_ref->{'apply_scope'} =~ m/RESPOND/) ) {
                #===如果设置了响应方式===#
        $hash_ref->{'respond_type'} = "";
    }
    if ( !($hash_ref->{'apply_scope'} =~ m/MERGE/) ) {
        #===如果设置了合并方式===#
        $hash_ref->{'merge_type'} = "";
        $hash_ref->{'merge_interval'} = "";
        $hash_ref->{'max_merge_count'} = "";
    }
    if ( !($hash_ref->{'apply_scope'} =~ m/EXCLUDE/) ) {
        #===如果设置了排除方式===#
        $hash_ref->{'exception_type'} = "";
        $hash_ref->{'exception_ips'} = "";
    }

    if ( $hash_ref->{'merge_type'} eq "none" ) {
        $hash_ref->{'merge_interval'} = "";
        $hash_ref->{'max_merge_count'} = "";
    }

    if ( $hash_ref->{'exception_type'} eq "none" ) {
        $hash_ref->{'exception_ips'} = "";
    }

    $hash_ref->{'apply_scope'}      =~ s/&/\|/g;
    $hash_ref->{'respond_type'}     =~ s/&/\|/g;
    $hash_ref->{'exception_ips'}    =~ s/&/\n/g;
}

sub delete_data() {
    my $reload = 0;
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'} );

    if( $status == 0 ) {
        $mesg = "删除成功"
    } else {
        $mesg = "删除失败";
    }

     &send_status( $status, $reload, $mesg );
}

sub toggle_enable($) {
    my $enable = shift;
    my $operation = "启用";
    if ( $enable ne "on" ) {
        $operation = "禁用";
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
        &create_need_reload_tag();
    }

    &send_status( $status, $reload, $mesg );
    return;
}

sub apply_data() {
    &clear_need_reload_tag();
    &send_status( 0, 0, "应用成功" );
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
    # system( "touch $need_reload_tag" );
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