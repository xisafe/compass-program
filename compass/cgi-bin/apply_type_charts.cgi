#!/usr/bin/perl
#author: pujiao
#createDate: 2016/8/05

use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#

my $need_reload_tag;       #规则改变时需要重新应用的标识
my $page_title;            #页面标题
my $extraheader;           #存放用户自定义JS
my %par;                   #存放post方法传过来的数据的哈希
my %query;                 #存放通过get方法传过来的数据的哈希
my %settings;              #存放该页面配置的哈希
my %list_panel_config;     #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $read_json_file;
my $ip_json_file;
my $file_dir;
          #ip数据对应的json数据文件
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
    # &load_data_for_ip();
}

sub init_data(){
    $file_dir              = '/usr/local/bin';
    $read_json_file           = $file_dir.'/flowmeter_main.py';

    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/apply_type_charts.css" />
                    <script language="javascript" src="/include/echarts-all.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/change_date.js"></script>
                    <script language="JavaScript" src="/include/apply_type_charts.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#

    # &make_file();#检查要存放规则的文件夹和文件是否存在
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $panel_name = $par{'panel_name'};
    if( !$action ) {
        $action = $query{'ACTION'};
    }

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==下载数据==#
        &load_data();
    } 
   
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_flow_enable();
    &display_list_div();
    &display_nodata();
    &closepage();
}

sub display_list_div() {
    printf<<EOF
    <div id="panel_flow_list_for_apply" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_member_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub display_flow_enable(){
  
    printf <<EOF
    <div id="mesg_box_flow" style="width: 96%;margin: 20px auto;"></div>
EOF
;
    &openbox('96%', 'left', '流量统计图');
    printf <<EOF
    <form name='FLOW_ENABLE_FORM' method='post' action='$ENV{SCRIPT_NAME}'>
        <div class="map_title" id="map_title">
            <label>统计条件：</label>
            时间<span class="map_time" id="s_time"></span> |
            筛选类型<span class="ip_or_user" id="user_type"></span> |
            应用类型<span class="type" id="app_type"></span>
        </div>
        <div class="map_condition">
            <span>
                <label>统计方式</label>
                <select id="statistical_method" onchange="chang_statistical_method();">
                    <option value="0">应用类型</option>
                    <option value="1">IP</option>
                    <option value="2">用户</option>
                </select>
            </span>
            <span>
                <label>显示:</label>
                <select id="top_num" onchange="chang_top_method();">
                    <option value="3">Top 3</option><option value="5" selected>Top 5</option><option value="10">Top 10</option>
                </select>
            </span>
            <span id="is_refresh_wrap">
                <label>是否实时刷新:</label>
                <select id="is_refresh" onchange="change_refresh();">
                    <option value="refresh_yes" selected>刷新</option><option value="refresh_no" >不刷新</option>
                </select>
            </span>

        </div>
        <div id="apply_flow_chart" style=""></div>

    </form>
EOF
;
    &closebox();
}


#列表无数据展示的面板
sub display_nodata(){
    printf <<EOF
    <div id="no_data_box" style="width: 96%;margin: 20px auto;">
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr class="table-footer"> 
            <td>
                <span style="color:red;">暂时无信息展示</span>
            </td>
        </tr>
    </table>
    </div>
EOF
;
}

sub load_data() {

    my %ret_data;
    my $content;
    my $rankby ='--rankby '.$par{'rankby'};
    my $top ='--top '.$par{'top'};
    #my $isurl  ='--isurl '.$par{'isurl'};
    my $isurl  ='--isurl 0';
    my $islive ='--islive '.$par{'islive'};
    my $ldate  = ($par{'islive'} == 1) ? 0 : '--ldate '.$par{'ldate'};
    my $hdate  = ($par{'islive'} == 1) ? 0 : '--hdate '.$par{'hdate'};
    my $ttag   ='--ttag '.$par{'ttag'};
   
    my $avalue ='--avalue '.$par{'avalue'};
   
    # my $uvalue ='--uvalue '.$par{'uvalue'};
   my $tvalue = '';
    my $uvalue = '';
    my $ruser = '';
    my $istrend= '--istrend '.$par{'istrend'};
    if($par{'tvalue'}){
        $tvalue = '--tvalue '.$par{'tvalue'};
    }
    if($par{'uvalue'}){
        $uvalue = '--uvalue '.$par{'uvalue'};
    }
    if($par{'ruser'}){
        $ruser = '--ruser '.$par{'ruser'};
    }
    my ($status,$error_mesg, $total_num ) =(1,"暂时无信息展示",0);
    my $json_str    ="$read_json_file $ldate  $hdate  $isurl $avalue  $uvalue  $rankby $top $ttag  $ruser $tvalue $istrend $islive";
    
    my $ip_json_str =`sudo $read_json_file $ldate  $hdate  $isurl $avalue  $uvalue  $rankby $top $ttag $ruser $tvalue $istrend $islive`;
    &debug_info($ip_json_str."\n");
    &debug_info($json_str."\n");
    
    my $ip_json = $json->decode( $ip_json_str );  

    %ret_data->{'detail_data'} = $ip_json;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $ip_json;
    # %ret_data->{'json_str'} = $json_str;;
 
    my $ret = $json->encode(\%ret_data);

    print $ret;

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

