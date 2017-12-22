#!/usr/bin/perl
#==============================================================================#
#
# 描述: 实时日志查询页面
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.10.13 WangLin创建
#
#==============================================================================#
use Encode;
use Data::Dumper;
require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'logs_event_search.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #配置所存放的文件
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $json = new JSON::XS;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir = '/ips';
    $conf_dir   = "${swroot}".$custom_dir;
    $conf_file  = $conf_dir.'/intimesearch.conf';

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/logs_real_time_events.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/logs_real_time_events.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);

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
    if ( $action eq 'load_data' && $panel_name eq 'logs_rt_events' ) {
        #==下载数据==#
        &load_data();
    }
    elsif ( $action eq 'load_data' && $panel_name eq 'logs_rt_details' ) {
        #==下载数据==#
        &load_details_data();
    }
    elsif ( $action eq 'load_page_size' ) {
        &load_page_size();
    }
    elsif( $action eq 'query_suggestion' ) {
        &query_suggestion();
    }
    else {
        #==如果用户什么都没提交，默认返回页面==#
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
    <div id="logs_rt_events" class="container"></div>
    <div id="logs_event_mesg_box" class="container"></div>
    <div id="logs_rt_details" class="container"></div>
EOF
    ;
}

sub save_parameter() {
    my %saved_data;

    &readhash( $conf_file, \%saved_data );

    if( $saved_data{'MAX_SHOW'} != $par{'page_size'} ) {
        $saved_data{'MAX_SHOW'} = $par{'page_size'};
        &writehash( $conf_file, \%saved_data );
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

sub load_page_size() {
    my %saved_data, %ret_data;

    &readhash( $conf_file, \%saved_data );

    if( $saved_data{'MAX_SHOW'} != 0 ) {
        %ret_data->{'page_size'} = $saved_data{'MAX_SHOW'};
    } else {
        %ret_data->{'page_size'} = 15;
        $saved_data{'MAX_SHOW'} = 15;
        &writehash( $conf_file, \%saved_data );
    }

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_data(){
    my %ret_data;

    &save_parameter();

    my @content_array;
    my $page_size = 15;
    my ( $status, $error_mesg, $total_num ) = &get_content( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'page_size'} = $total_num;

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub load_details_data() {
    my %ret_data;

    my @content_array;
    my ( $status, $error_mesg, $total_num ) = &get_details_content( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_content($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $dbh = connect_sql();
    &intime_query( $dbh, $page_size, $par{'event_level'}, $par{'search'}, $content_array_ref);
    my $total_num = scalar ( @$content_array_ref );
    my $status = 0, $mesg = "加载成功";

    return ( $status, $error_mesg, $total_num );
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

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}