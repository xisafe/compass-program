#!/usr/bin/perl
#==============================================================================#
#
# 描述: 添加面板使用示例页面
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

#=================初始化全局变量到init_data()中去初始化========================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $json = new JSON::XS;#处理json数据的变量，一般不变
my $page_title;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post请求传过来的变量
    &getcgihash(\%par);
    #获取get请求传过来的变量
    &get_query_hash(\%query);
    #初始化变量值
    &init_data();
    #检查要存放规则的文件夹和文件是否存在
    &make_file();
    #做出响应
    &do_action();
}

sub init_data(){
    $page_title = '添加面板测试页面';
    $custom_dir = '/template';                      #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir   = "${swroot}".$custom_dir;          #规则所存放的文件夹
    $conf_file  = $conf_dir.'/config';              #规则所存放的文件

    #============页面要使用添加面板必须引用的CSS和JS-BEGIN======================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的*extend.css/js脚本=====================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/info_panel.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/add_panel_extend.css" />
                    <script language="JavaScript" src="/include/add_panel_extend.js"></script>
                    <script language="JavaScript" src="/include/info_panel_extend.js"></script>';
    #============页面要使用添加面板必须引用的CSS和JS-END========================================#
}

sub do_action() {
    #==一般ACTION只会通过一种方式传过来，开发者需要自己判断从哪种方式传过来==#
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ( $action eq 'save_data' && $panel_name eq "add_panel_1" ) {
        &save_panel_1_data();
    } 
    elsif ( $action eq 'save_data' && $panel_name eq "add_panel_2" ) {
        &save_panel_2_data();
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
    <div id="display_panel" class="container"></div>
    <div id="add_panel_1" class="container"></div>
    <div id="add_panel_2" class="container"></div>
EOF
    ;
}

sub save_panel_1_data($) {
    my ( $status, $reload, $mesg ) = ( 0, 0, "面板1测试成功~~" );

    &send_status( $status, $reload, $mesg );
    return;
}

sub save_panel_2_data() {
    my ( $status, $reload, $mesg ) = ( 0, 0, "面板2测试成功~~" );

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

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}