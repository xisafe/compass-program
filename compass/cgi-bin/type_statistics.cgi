#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/12/03
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;            #要保存数据的目录名字
my $conf_dir;              #规则所存放的文件夹
my $conf_file;             #规则所存放的文件
my $settings_file;         #启用服务所存放的文件
my $settings_file_default; #默认启用服务所存放的文件
my $need_reload_tag;       #规则改变时需要重新应用的标识
my $page_title;            #页面标题
my $extraheader;           #存放用户自定义JS
my %par;                   #存放post方法传过来的数据的哈希
my %query;                 #存放通过get方法传过来的数据的哈希
my %settings;              #存放该页面配置的哈希
my %list_panel_config;     #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
# my $cmd;
# my $cmd_getRtinfo;
# my $cmd_getDetail;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $read_conf_dir; 
my $url_classify_file; 
my $apply_classify_file;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir            = '/flowMonit';                         #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir              = "/var/efw".$custom_dir;               #规则所存放的文件夹
    $conf_file             = $conf_dir.'/config';                  #流量信息所存放的文件
    $settings_file         = $conf_dir.'/settings';                #启用所存放的文件
    $settings_file_default = $conf_dir.'/default/settings';        #默认启用所存放的文件
    $need_reload_tag       = $conf_dir.'/add_list_need_global';    #表示需要重新应用的文件
    $read_conf_dir         ="/var/efw/objects";                    #读取数据的目录文件夹     
    $url_classify_file  =$read_conf_dir.'/urllist/urlconfig';      #读取url分类库文件
    $apply_classify_file = $read_conf_dir.'/application/app_group';
    # $cmd                   = "/usr/local/bin/restarttrafficstat";
    # $cmd_getRtinfo         = "sudo /usr/local/bin/getRtFlowinfo.py";
    # $cmd_getDetail         = "sudo /usr/local/bin/getDetailFlowinfo.py";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/jquery-ui.min.css" />
                    <script language="JavaScript" src="/include/jquery-1.12.1.min.js"></script>
                    <script language="JavaScript" src="/include/jquery-ui.js"></script>
                     <!--<script language="javascript" src="/include/echarts-plain.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>-->
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/change_date.js"></script>
                    <script language="JavaScript" src="/include/type_statistics.js"></script>';
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
    if ($action eq 'read_data' ) {
        #==下载数据==#
        &read_data();
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
    <div id="panel_flow_list" style="width: 96%;margin: 20px auto;"></div>
    <div id="mesg_box_tmp" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub read_data(){
    my %ret_data; 
    my @lines_url_classify;
    my @lines_url_classify_names; 
    my @lines_apply_classify;
    my @lines_apply_classify_names;
    my ( $status, $error_mesg)= &read_config_lines($url_classify_file,\@lines_url_classify);
    my ( $status, $error_mesg)= &read_config_lines($apply_classify_file,\@lines_apply_classify);
   
  
   # add all type --pengtian
   push( @lines_url_classify_names,'0,所有');
    foreach(@lines_url_classify){
        my $id = (split(",",$_))[0];
        my $name = (split(",",$_))[1];
        my $value = $id.','.$name;
        push( @lines_url_classify_names,$value);
    }
    foreach(@lines_apply_classify){
        my $id = (split(",",$_))[0];
        my $name = (split(",",$_))[1];
        my $value = $id.','.$name;
        push( @lines_apply_classify_names,$value);
    }
    %ret_data->{'url_classify_data'}= \@lines_url_classify_names;
    %ret_data->{'apply_classify_data'} =\@lines_apply_classify_names;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $error_mesg;
    my $ret = $json->encode(\%ret_data);
    print $ret; 

}

# sub send_status($$$) {
#     #==========状态解释=========================#
#     # => $status: 0 表示成功，其他表示不成功
#     # => $reload: 1 表示重新应用，其他表示不应用
#     # => $mesg: 相关错误的消息
#     #===========================================#
#     my ($status,$reload,$mesg) = @_;
#     my %hash;
#     %hash->{'status'} = $status;
#     %hash->{'reload'} = $reload;
#     %hash->{'mesg'} = $mesg;
#     my $result = $json->encode(\%hash);
#     print $result;
# }

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
    
    if(! -e $settings_file_default){
        system("touch $settings_file_default");
        system("echo ENABLED=on >> $settings_file_default");
    }
    
}
