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
#=========================全部变量定义end=======================================#

&main();
sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/dataleak';                             #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;                   #url控制策略所存放的文件夹
    $conf_file          = $conf_dir.'/config';                      #存储Url控制策略
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_tmp';    #启用信息所存放的文件

    $read_conf_dir      ="/var/efw/objects";                        #读取数据的目录文件夹     
    $ip_groups_file     =$read_conf_dir.'/ip_object/ip_group';      #读取ip组文件
    $sens_info_file     ='/var/efw/security_objects/dataleak/config';        #读取敏感信息识别库文件
    $cmd                ='/usr/local/bin/setdataleak.py';
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/information_reveal.js"></script>';
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
        &toggle_enable( $par{'id'}, "on" );
    }
    elsif ($action eq 'disable_data') {
        #==禁用规则==#
        &toggle_enable( $par{'id'}, "off" );
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
    <div id="panel_tmp_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub read_data(){
    my %ret_data; 
    my @lines_ipgroups;
    my @lines_sens_info;
    my @lines_ipgroups_names;
    my @lines_sens_info_names;
    my ( $status, $error_mesg)= &read_config_lines($ip_groups_file ,\@lines_ipgroups);
    my ( $status, $error_mesg)= &read_config_lines($sens_info_file,\@lines_sens_info);
    foreach(@lines_ipgroups){
        
        push( @lines_ipgroups_names,(split(",",$_))[1]);
    }
    foreach(@lines_sens_info){
        
        push( @lines_sens_info_names,(split(",",$_))[1]);
    }

    %ret_data->{'ipgroups_data'}    = \@lines_ipgroups_names;
    %ret_data->{'sens_info_type'}= \@lines_sens_info_names;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $error_mesg;
    my $ret = $json->encode(\%ret_data);
    print $ret; 

}
sub save_data() {
    my $max_id;
    my @id_arr;
    my $reload = 0;
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
        }
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, "$item_id,$record" );
    }
   
    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
}
sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );
    
    my $record_num = @lines;
    my $search = $par{'search'};
    if($search){
        chomp($search);
        #===转换成小写，进行模糊查询==#
        $search = lc($search);
        for(my $i = 0; $i < $record_num; $i++){
            chomp(@lines[$i]);
            if($search ne ""){
                my $searched = 0;
                my $where = -1;
                my @data = split(",", @lines[$i]);
                foreach my $field (@data) {
                    #===转换成小写，进行模糊查询==#
                    my $new_field = lc($field);
                    $where = index($new_field, $search);
                    if($where >= 0) {
                        $searched++;
                    }
                }
                #如果没有一个字段包含所搜寻到子串,则不返回
                if(!$searched){
                    next;
                }
            }
            my %conf_data = &get_config_hash(@lines[$i]);
            if (! $conf_data{'valid'}) {
                next;
            }
            $conf_data{'id'} = $i;
            push(@content_array, \%conf_data);
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
    &read_config_lines($conf_file,\@lines);
    my @ids = split("\&",$par{'id'});
    my @ids_rule_del = ();
    foreach(@ids){
        my @data_line = split(",",$lines[$_]);
        my @sub_ids_rule = &get_ruleid_for_policy($data_line[0]);
        push(@ids_rule_del,@sub_ids_rule);
    }
    # &delete_several_records( $conf_file_rule,join("\&",@ids_rule_del) );
    my ( $status, $mesg ) = &delete_several_records_by_id( $conf_file, $par{'id'});
     `sudo $cmd`;
    
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
    $config{'id'}                = $temp[0];
    $config{'name'}              = $temp[1];
    $config{'description'}       = $temp[2];
    $config{'ip_group_value'}    = $temp[3];
    $config{'sens_info_type'}    = $temp[4];
    $config{'protocol'}          = $temp[5];
    $config{'gate'} 		     = $temp[6];
    $config{'action_permission'} = $temp[7];  
    $config{'enabled_status'}    = $temp[8];
	if($temp[9]){
		$config{'protocolType'}  = $temp[9];
	}else {
		$config{'protocolType'}  = "";
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
    push( @record_items, $hash_ref->{'ip_group_value'} );
    push( @record_items, $hash_ref->{'sens_info_type'} );
    push( @record_items, $hash_ref->{'protocol'} );
    push( @record_items, $hash_ref->{'gate'} );
    push( @record_items, $hash_ref->{'action_permission'} );
   
    my $enabled_status = $hash_ref->{'enabled_status'};
    if( $enabled_status eq "" ){
        $enabled_status = "off";
    }
    push( @record_items, $enabled_status );
    push( @record_items, $hash_ref->{'protocolType'} );

    return join (",", @record_items);
}

sub toggle_enable($$) {
    my $item_ids = shift;
    my $enable = shift;
    my $reload = 0;
    my @lines;
  
    my ( $status, $mesg ) = &get_several_records( $conf_file, $item_ids,\@lines );
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
         ( $status, $mesg ) = &update_one_record( $conf_file, @item_ids[$i], $record );
         `sudo $cmd`;
         if( $enable eq "on" ) {
            $mesg = "启用成功";
         }
         else{
            $mesg = "禁用成功";
         }
    }

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
    system( "rm  $need_reload_tag" );
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

