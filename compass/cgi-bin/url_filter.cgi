#!/usr/bin/perl
#author: pujiao
#createDate: 2016/7/08

use Encode;
use List::Util qw(max);
require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #策略模板所存放的文件
my $conf_file_rule;     #规则所存放的文件
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
my $cmd_init_tree;      #获取用户组初始化的值；
my $read_conf_dir; 
my $ip_groups_file; 
my $single_plan_file; 
my $circle_plan_file; 
my $url_classify_file;

my $CUR_PAGE = "URL过滤" ;  #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

#=========================全部变量定义end=======================================#

&main();
# &init_tree();
sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/urlfilter';                             #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;                   #url控制策略所存放的文件夹
    $conf_file          = $conf_dir.'/config';                      #存储Url控制策略
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_tmp';    #启用信息所存放的文件

    $sourceip_file      = '/var/efw/objects/ip_object/ip_group'; 
    $read_conf_dir      ="/var/efw/objects";                        #读取数据的目录文件夹     
    $ip_groups_file     =$read_conf_dir.'/ip_object/ip_group';      #读取ip组文件
    $single_plan_file   =$read_conf_dir.'/time_plan/single';         #读取单次时间计划文件
    $circle_plan_file   =$read_conf_dir.'/time_plan/around';         #读取循环时间计划文件
    $url_classify_file  =$read_conf_dir.'/urllist/urlconfig';        #读取url分类库文件
    $cmd                = "/usr/local/bin/seturlfilter.py";
    $cmd_init_tree      = "/usr/local/bin/getGroupUserTree.py";
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/jsTree.css" />
                    <script language="JavaScript" src="/include/jquery-1.12.1.min.js"></script>
                    <script language="JavaScript" src="/include/jstree.min.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/url_filter.js"></script>
                    <script language="JavaScript" src="/include/add_panel_include_config.js"></script>';
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
    elsif ( $action eq 'load_data' && $panel_name eq 'SrcIPGroup_panel') {
        &load_settingdata($sourceip_file);
    }    
    elsif ( $action eq 'load_data' && $panel_name eq 'DestIPGroup_panel') {
        &load_settingdata($sourceip_file);
    }
    elsif( $action eq 'load_userlist') {
        &init_tree();
    }
       
    elsif( $action eq 'get_init_data_tree' or $panel_name eq 'user_group_panel') {
        &init_tree();
    }
    elsif ($action eq 'read_data') {
        #==加载数据==#
        &read_data();
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
    elsif ($action eq 'enable_data') {
        #==启用规则==#
        &toggle_enable( $par{'id'}, "0" );
    }
    elsif ($action eq 'disable_data') {
        #==禁用规则==#
        &toggle_enable( $par{'id'}, "1" );
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
    <div id="mesg_box_tmp" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_tmp_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_uesr_group"  style="width:96%;margin:20px auto"></div>
    <div id="panel_url_classify"  style="width:96%;margin:20px auto"></div>
    <div id="panel_tmp_list" style="width: 96%;margin: 20px auto;"></div>
    <div id="SrcIPGroup_panel" class="container"></div>
    <div id="DestIPGroup_panel" class="container"></div>

EOF
    ;
}

sub read_data(){
    my %ret_data; 
    my @lines_ipgroups;
    my @lines_single_plan;
    my @lines_circle_plan;
    my @lines_url_classify;
    my @lines_ipgroups_names;
    my @lines_single_plan_names;
    my @lines_circle_plan_names;
    my @lines_url_classify_names;
    # my $str_json;
    # my $json_obj;
    # my $list_name = $par{'list_name'};

    my ( $status, $error_mesg)= &read_config_lines($ip_groups_file ,\@lines_ipgroups);
    my ( $status, $error_mesg)= &read_config_lines($single_plan_file ,\@lines_single_plan);
    my ( $status, $error_mesg)= &read_config_lines($circle_plan_file ,\@lines_circle_plan);
    my ( $status, $error_mesg)= &read_config_lines($url_classify_file,\@lines_url_classify);
   
    # if($list_name ne ""){
    #      $str_json = `sudo $cmd_init_tree $list_name`;
    #      $json_obj = $json->decode($str_json);
    # }
    foreach(@lines_ipgroups){
        push( @lines_ipgroups_names,(split(",",$_))[1]);
    }
    foreach(@lines_single_plan){
        push( @lines_single_plan_names,(split(",",$_))[1]);
    }
    foreach(@lines_circle_plan){
        push( @lines_circle_plan_names,(split(",",$_))[1]);
    }
    foreach(@lines_url_classify){
        my %temp->{'id'} = (split(",",$_))[0];
            %temp->{'text'} =  (split(",",$_))[1];
            %temp->{'type'} = 'urltype';
        push( @lines_url_classify_names,\%temp);
    }

    %ret_data->{'ipgroups_data'}    = \@lines_ipgroups_names;
    # %ret_data->{'user_group_data'}  = $json_obj;
    %ret_data->{'single_plan_data'} = \@lines_single_plan_names;
    %ret_data->{'circle_plan_data'} = \@lines_circle_plan_names;
    %ret_data->{'url_classify_data'}={};
    %ret_data->{'url_classify_data'}{'children'}= \@lines_url_classify_names;
    %ret_data->{'url_classify_data'}{'text'}= "所有";
    %ret_data->{'url_classify_data'}{'id'}= "rootid";
    %ret_data->{'url_classify_data'}{'type'}= "urltypes";
    %ret_data->{'url_classify_data'}{'children'}= \@lines_url_classify_names;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $error_mesg;
    my $ret = $json->encode(\%ret_data);
    print $ret; 

}
sub init_tree() {
    my $edit_id = $par{'edit_id'};
    my %ret_data;
    my $str_json;
    if($edit_id eq ""){
         $str_json = `sudo $cmd_init_tree`;
    }
    else{
        my $cmd_str = $cmd_init_tree.' -n '.$edit_id;
        $str_json = `sudo $cmd_str`;
    }
   
    print $str_json;
}
sub save_data() {
    my $max_id;
    my @id_arr;
    my $reload = 0;

    if( $par{'ip_or_user'} eq 'sour_ip' ) {
        $par{'SrcIPGroup'} = &datas_hander( $par{'SrcIPGroup'},'save' );
    }elsif($par{'ip_or_user'} eq 'sour_user' ) {
        $par{'SrcUserlist'} = &datas_hander( $par{'SrcUserlist'},'save' );
    }

    $par{'DestIPGroup'} = &datas_hander( $par{'DestIPGroup'},'save' );

    if( $par{'service_or_app'} eq 'service' ) {
        $par{'ServiceName'} = &datas_hander( $par{'ServiceName'},'save' );
        $par{'Appid'} = '';
    }else {
        $par{'Appid'} = &datas_hander( $par{'Appid'},'save' );
        $par{'ServiceName'} = '';
    }
    $par{'url_classify'} =~ s/\, /\|/g;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};

    
    my @lines;
    &read_config_lines($conf_file,\@lines);

    my ( $status, $mesg ) = ( -1, "未保存" );
    foreach(@lines){
        push(@id_arr,(split(",",$_))[0]);
    }

    if( $item_id eq '' ) {
        foreach (@lines){
            if($par{'name'} eq (split(",",$_))[1]){
                ( $status, $mesg ) = ( -2, $par{'name'}."已占用" );
            }
        }
        if($status != -2){
            if(@id_arr>0){
              $max_id = max(@id_arr)+1;  
            }
            else{
                $max_id = 0;
            }
            
            ( $status, $mesg ) = &append_one_record( $conf_file, "$max_id,$record" );
            $log_oper = "add";
            
        }
    } else {
        ( $status, $mesg ) = &update_one_record_by_id( $conf_file, $item_id, "$item_id,$record" );
        $log_oper = "edit";
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
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
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );
    
    my $record_num = @lines;
    my $search = &prepare_search($par{'search'});
    if($search){
        chomp($search);
        #===转换成小写，进行模糊查询==#
        $search = lc($search);
        for(my $i = 0; $i < $record_num; $i++){
            chomp(@lines[$i]);
            
            my %config = &get_config_hash(@lines[$i]);
            if( $config{'valid'} ) {
            $config{'index'} = $i+1;
            # $config{'id'} = $i;
            # if( $i % 5 == 0 ) {
            #     $config{'uneditable'} = 1;
            #     $config{'undeletable'} = 1;
            # }
                if( $config{'SrcUserlist'} eq '' ) {
                    if ($config{'sour_netip_text'} eq '') {
                        if ($config{'SrcIPGroup'} eq '') {
                            $config{'IpOrUser'} = '任意';   
                            $config{'ip_or_user'} = 'sour_any';
                        }else{
                            $config{'ip_or_user'} = 'sour_ip';
                            $config{'SrcIPGroup'} = &datas_hander( $config{'SrcIPGroup'},'load' );
                            $config{'IpOrUser'} = $config{'SrcIPGroup'};                    
                        }
                    }else{
                        $config{'ip_or_user'} = 'sour_netip';
                        $config{'sour_netip_text'} = &datas_hander( $config{'sour_netip_text'},'load' );
                        $config{'IpOrUser'} = $config{'sour_netip_text'};
                    }
                }else {
                $config{'ip_or_user'} = 'sour_user';
                $config{'SrcUserlist'} = &datas_hander( $config{'SrcUserlist'},'load' );
                $config{'IpOrUser'} = $config{'SrcUserlist'};
            }

            if ($config{'DestIPGroup'} eq '') {
                if ($config{'dest_ip_text'} eq '') {
                    $config{'target_ipgroups'} = '任意';
                    $config{'dest_ipgroup'} = 'dest_any';
                }else{
                    $config{'dest_ip_text'} = &datas_hander( $config{'dest_ip_text'},'load' );
                    $config{'target_ipgroups'} = $config{'dest_ip_text'};
                    $config{'dest_ipgroup'} = 'dest_group';
                }
            }else{
                $config{'DestIPGroup'} = &datas_hander( $config{'DestIPGroup'},'load' );
                $config{'target_ipgroups'} = $config{'DestIPGroup'};
                $config{'dest_ipgroup'} = 'dest_ip';
            }
            if($search ne ""){
                if (lc($config{'name'}) !~ m/$search/ &&
                 lc($config{'IpOrUser'}) !~ m/$search/ &&
                  lc($config{'url_classify'}) !~ m/$search/ &&
                   lc($config{'url_type'}) !~ m/$search/ 
                   # &&
                   #  $config{'is_record'} !~ m/$search/ &&
                   #   $config{'action_permission'} !~ m/$search/ 
                ) 
                {
                    next;
                }    
            }
        }
            if (! $config{'valid'}) {
                next;
            }
            $config{'id'} = $i;
            push(@content_array, \%config);
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
    my @lines = ();
    $log_oper = 'del';
    my $id_temp = $par{'id'};
    &read_config_lines($conf_file,\@lines);
    my @ids = split("\&",$par{'id'});
    my @ids_rule_del = ();
    foreach(@ids){
        my @data_line = split(",",$lines[$_]);
        my @sub_ids_rule = &get_ruleid_for_policy($data_line[0]);
        push(@ids_rule_del,@sub_ids_rule);
    }
    # &delete_several_records( $conf_file_rule,join("\&",@ids_rule_del) );
     $id_temp  =~ s/&/\\&/g;
     `sudo $cmd -n $id_temp`;
    my ( $status, $mesg ) = &delete_several_records_by_id( $conf_file, $par{'id'});
   
    
    if($status eq '0'){
        $mesg = '删除成功！';
    }

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;
    if(@ids_rule_del > 0){
        %ret_data->{'reload'} = 1;
        &create_need_reload_tag();
    }

    my $ret = $json->encode(\%ret_data);
	`sudo $cmd`;
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
    for ( my $i = $from_num; $i < $total_num; $i++ ) {
        my %config = &get_config_hash( $lines[$i] );
        if( $config{'valid'} ) {
            $config{'index'} = $i+1;
            # $config{'id'} = $i;
            # if( $i % 5 == 0 ) {
            #     $config{'uneditable'} = 1;
            #     $config{'undeletable'} = 1;
            # }
                if( $config{'SrcUserlist'} eq '' ) {
                    if ($config{'sour_netip_text'} eq '') {
                        if ($config{'SrcIPGroup'} eq '') {
                            $config{'IpOrUser'} = '任意';   
                            $config{'ip_or_user'} = 'sour_any';
                        }else{
                            $config{'ip_or_user'} = 'sour_ip';
                            $config{'SrcIPGroup'} = &datas_hander( $config{'SrcIPGroup'},'load' );
                            $config{'IpOrUser'} = $config{'SrcIPGroup'};                    
                        }
                    }else{
                        $config{'ip_or_user'} = 'sour_netip';
                        $config{'sour_netip_text'} = &datas_hander( $config{'sour_netip_text'},'load' );
                        $config{'IpOrUser'} = $config{'sour_netip_text'};
                    }
                }else {
                $config{'ip_or_user'} = 'sour_user';
                $config{'SrcUserlist'} = &datas_hander( $config{'SrcUserlist'},'load' );
                $config{'IpOrUser'} = $config{'SrcUserlist'};
            }

            if ($config{'DestIPGroup'} eq '') {
                if ($config{'dest_ip_text'} eq '') {
                    $config{'target_ipgroups'} = '任意';
                    $config{'dest_ipgroup'} = 'dest_any';
                }else{
                    $config{'dest_ip_text'} = &datas_hander( $config{'dest_ip_text'},'load' );
                    $config{'target_ipgroups'} = $config{'dest_ip_text'};
                    $config{'dest_ipgroup'} = 'dest_group';
                }
            }else{
                $config{'DestIPGroup'} = &datas_hander( $config{'DestIPGroup'},'load' );
                $config{'target_ipgroups'} = $config{'DestIPGroup'};
                $config{'dest_ipgroup'} = 'dest_ip';
            }
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
    $config{'id'}                = $temp[0];
    $config{'name'}              = $temp[1];
    $config{'description'}       = $temp[2];
    $config{'SrcIPGroup'}        = $temp[3];
    $config{'SrcUserlist'}       = $temp[4];
    $config{'sour_netip_text'}   = $temp[5];

    # if( ($temp[3]) eq "" ){
    #     $config{'ip_or_user'} = 'user_group';
    #     $config{'user_group_value'} = $temp[4];
    # }
    # else{
    #     $config{'ip_or_user'} = 'ip_group'; 
    #     $config{'ip_group_value'} = $temp[3];  
    # }
    # $config{'ip_or_user_value'}    = $temp[3].$temp[4];
    # $config{'target_ipgroups'} = $temp[5]; 
    $config{'url_classify'}      = $temp[6];
    $config{'url_type'}          = $temp[7];
    if ($config{'url_type'} eq 'HTTPS') {
        $config{"url_type"} = 'ALL';
    }
    #  if( $temp[9] eq "" ){
    #     $config{'single_or_circle'} = 'circle_plan';
    #     $config{'circle_time_value'} = $temp[10];
    # }
    # else{
    #     $config{'single_or_circle'} = 'single_plan'; 
    #     $config{'single_time_value'} = $temp[9];  
    # }
    # $config{'single_or_circle'} = $temp[9];
    # $config{'circle_time_value'} = $temp[10];
    # $config{'effect_time'} = $temp[9]. $temp[10];
    $config{'action_permission'} = $temp[10];
    $config{'is_record'}         = $temp[11];
    $config{'enable'}            = $temp[12];
    if ($config{'enable'} eq '0') {
        $config{"enable"} = 'on';
    }else {
        $config{'enable'} = 'off';
    }
  
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();

    
    push( @record_items, $hash_ref->{'name'} );
    my $description = $hash_ref->{'description'};
    $description =~ s/,/，/g;
    push( @record_items, $description );
    push( @record_items, $hash_ref->{'SrcIPGroup'} );
    my $user_group_value = $hash_ref->{'SrcUserlist'};
    $user_group_value =~ s/,/，/g;
    push( @record_items, $user_group_value);
    my $sour_netip_text = $hash_ref->{'sour_netip_text'};
    $sour_netip_text =~ s/\r\n/&/g;
    $sour_netip_text =~ s/&{2,}$//;
    push( @record_items, $sour_netip_text );
    push( @record_items, $hash_ref->{'url_classify'} );
    my $url_type = $hash_ref->{'url_type'};
    if( $url_type eq "HTTPS" ){
        $url_type = "ALL";
    }
    # push( @record_items, $hash_ref->{'url_type'} );
    push( @record_items, $url_type );
    push( @record_items, $hash_ref->{'single_time_value'} );
    push( @record_items, $hash_ref->{'circle_time_value'} );
    push( @record_items, $hash_ref->{'action_permission'} );
    my $is_record = $hash_ref->{'is_record'};
    if( $is_record eq "" ){
        $is_record = "1";
    }
    push( @record_items, $is_record );
    my $enabled_status = $hash_ref->{'enable'};
    if( $enabled_status eq "" ){
        $enabled_status = "1";
    }
    push( @record_items, $enabled_status );

    return join (",", @record_items);
}

sub toggle_enable($$) {
    my $item_ids = shift;
    my $enable = shift;
    my $reload = 0;
    my @lines;
  
    my ( $status, $mesg ) = &get_several_records_by_ids( $conf_file, $item_ids,\@lines );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status,$reload,$mesg );
        return;
    }
    my $len = @lines;
    my @item_ids = split("&",$item_ids);
    for(my $i=0; $i < $len; $i++){
         my @line_content = split(",",$lines[$i]);
         @line_content[@line_content-1] = $enable;
         my $record = join("," , @line_content);
         ( $status, $mesg ) = &update_one_record_by_id( $conf_file, @item_ids[$i], $record );
         
         if( $enable == "0" ) {
            $mesg = "启用成功";
            $log_oper = 'enable';
         }
         else{
            $mesg = "禁用成功";
            $log_oper = 'disable';
         }
    }
    `sudo $cmd`;
    if( $status != 0 ) {
        $mesg = "操作失败";
    }

    &send_status( $status,$reload,$mesg );
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
   
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_congfig);
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
    $log_oper = 'apply';
    
    $result = `sudo $cmd`;
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

#检查策略模板是否被规则占用，返回所有被占的规则名称
sub get_ruleid_for_policy($){
    my $policy_name = shift;
    my @lines_rule = ();
    my @rules = ();
    &read_config_lines($conf_file_rule,\@lines_rule);
    for(my $i=0;$i<@lines_rule;$i++){
        my @data_line = split(",",$lines_rule[$i]);
        if($data_line[6] eq $policy_name){
            push(@rules,$i);
        }
    }
    return @rules;
}

sub load_settingdata() {
    my $file = shift;
    
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $file, \@lines );    
    my $record_num = @lines;
    $total_num = $record_num;
    
    for ( my $i = 0; $i < $record_num; $i++ ) {
        my %config;
        my @data_line = split(",",$lines[$i]);
        %config->{'name'} = $data_line[1];
        %config->{'id'} = $i;
        %config->{'valid'} = 1;
        push( @content_array, \%config );
    }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    

    my $ret = $json->encode(\%ret_data); 
    print $ret; 
}

sub datas_hander() {
    my ($data,$act) = @_;
    if( $act eq 'save' ) {
        $data =~ s/, /&/g;
    }
    if($act eq 'load') {
        $data =~ s/&/, /g;
    }
    return $data;
    
}


