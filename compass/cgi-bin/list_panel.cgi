#!/usr/bin/perl
#==============================================================================#
#
# 描述: 列表规则页面
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.09.23 WangLin创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $page_title = '';
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $page_title = '列表面板调试';
    $custom_dir = '/template';                      #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir   = "${swroot}".$custom_dir;          #规则所存放的文件夹
    $conf_file  = $conf_dir.'/config';              #规则所存放的文件

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/list_panel_extend.css" />
                    <script language="JavaScript" src="/include/list_panel_extend.js"></script>
                    <script type="text/javascript" src="/include/ESONCalendar.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &get_query_hash(\%query);
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
    elsif ($action eq 'delete_data') {
        #==下载数据==#
        &delete_data();
    }
    elsif ($action eq 'enable_data') {
        #==下载数据==#
        &toggle_enable( "on" );
    }
    elsif ($action eq 'disable_data') {
        #==下载数据==#
        &toggle_enable( "off" );
    }
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_main_body();
    &closepage();
}

sub display_main_body() {
    printf<<EOF
    <div id="list_main_body" class="container"></div>
EOF
    ;
}

sub load_data(){
    my %ret_data;

    my @content_array;
    my ( $status, $error_mesg, $total_num ) = &get_detail_content( \@content_array );
    my @panel_header = &config_list_panel_header();

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub delete_data() {
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'item_id'});

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'msg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_detail_content($) {
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
    $config{'time_start'}       = $temp[0];
    $config{'sip'}              = $temp[1];
    $config{'dip'}              = $temp[2];
    $config{'msg'}              = $temp[3];
    $config{'classification'}   = $temp[4];
    $config{'priority'}         = $temp[3];
    $config{'enable'}           = $temp[6];
    $config{'time_end'}           = $temp[7];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'time_start'} );
    push( @record_items, $hash_ref->{'msg'} );
    push( @record_items, $hash_ref->{'classification'} );
    push( @record_items, $hash_ref->{'priority'} );
    push( @record_items, $hash_ref->{'sip'} );
    push( @record_items, $hash_ref->{'dip'} );
    push( @record_items, $hash_ref->{'enable'} );
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
    my @item_ids = split( "&", $par{'item_id'} );
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

sub send_status($$) {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}