#!/usr/bin/perl
#author: pujiao
#createDate: 2016/07/11
use Encode;
use List::Util qw(max);
require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file_custom;   #用户自定义规则库所存放的文件夹
my $conf_file;          #URL规则所存放的文件
# my $conf_file_custom_pid;#用于存储用户自定义规则库的主键文件
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
#记录日志的变量
my $CUR_PAGE = "URL分类库" ;  #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir           = '/objects/urllist';                         #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir             = "/var/efw".$custom_dir;                     #规则所存放的文件夹
    $conf_file            = $conf_dir.'/urlconfig';                     #存储URL规则库信息
    $conf_file_custom     = $conf_dir.'/custom';                        #保存用户自定义的URL规则库文件夹
    # $conf_file_custom_pid = $conf_dir.'/custom_pid';                    #保存用户自定义的规则库主键
    $need_reload_tag      = $conf_dir.'/add_list_need_reload_url';      #启用信息所存放的文件
    $cmd                = "sudo /usr/local/bin/search_domain.py";
    $cmd_apply                = "sudo /usr/local/bin/seturlfilter.py";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/url_classify_lib.js"></script>';
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
    if($action ne "export_data"){
        &showhttpheaders();
    }
    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data' && $panel_name eq 'list_panel') {
        #==下载数据==#
        &load_data();
    } 
    elsif ($action eq 'save_data' && $panel_name eq 'add_panel') {
        #==保存数据==#
        &save_data();
    }
    elsif( $action eq 'search_domain'){
        #====查询域名====#
        &search_domain();
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
        if($action eq 'export_data') {
            #==导出数据==#
            &export_data();
        } else {
            #返回默认页面
            &show_page();
        }
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_list_div();
    &closepage();
}

sub display_list_div() {
    printf<<EOF
    <div id="mesg_box_url" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_url_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_url_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}


sub save_data() {
    my $reload = 0;
    my $maxid ;
    my @id_arr;
    my $old_record ;
    my ($record,$path_item) = &get_config_record( \%par );
    my $item_id = $par{'id'};
    my $str_urls = $par{'urls'};
    $str_urls =~ s/\r//g;
    $str_urls =~ s/\n/,/g;
    my @arr_urls = split(",",$str_urls);

    my @lines;
    &read_config_lines($conf_file,\@lines);
    

    my ( $status, $mesg ) = ( -1, "未保存" );

    foreach (@lines){
        push(@id_arr,(split(",",$_))[0]); 
    }
    if( $item_id eq '' ) {
        foreach (@lines){
           if($par{'name'} eq (split(",",$_))[1]){
                ( $status, $mesg ) = ( -2, $par{'name'}."已占用" );
            }
        }
        if($status != -2){
            $maxid = (max( @id_arr ) >= 100) ? max( @id_arr ) + 1 : 101;
            ( $status, $mesg ) = &append_one_record( $conf_file, "$maxid,$record$maxid" );
            $log_oper = "add";
            #创建并写入自定义用户的规则库-----begin-------
            system("mkdir $conf_file_custom");
            system("touch $conf_file_custom/custom$maxid");
            foreach(@arr_urls){
                system("echo $_ >> $conf_file_custom/custom$maxid");
            } 
            #创建并写入自定义用户的规则库 -------end----------
        }
    } else {
        if($status != -2){
            my @record_temp = split(",",$record);
           
            ( $status, $mesg, $old_record ) = &get_one_record_by_id( $conf_file,$item_id);

            $path_item = (split(",",$old_record))[4]; #获取配置文件中存放的路径
            $record_temp[3] = $path_item;

             $record_str = join (",", @record_temp);
            ( $status, $mesg ) = &update_one_record_by_id( $conf_file, $item_id, "$item_id,$record_str");
            $log_oper = "edit";
            system("cat /dev/null > $path_item");
            foreach(@arr_urls){
                system("echo $_ >> $path_item");
            }
        }
        $reload =1 ;
    }

    if( $status == 0 ) {
        $mesg = "保存成功";
        $reload = 1;
        &create_need_reload_tag();
    }
    &send_status( $status, $reload, $mesg );
}
sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my $search_result;
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );#读取用户的URL规则库；
    
    my $record_num = @lines;
    my $search = $par{'search'};
    if($search){
        $cmd_str = $cmd.' -f '.$search;
        $search_result =`$cmd_str`;
        if($search_result ne ""){
            my %conf_data =  &get_config_hash($search_result);
            push(@content_array,\%conf_data);
            $total_num = 1;
        }
        else{
           @content_array = ""; 
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
sub search_domain(){
    my %ret_data;
    my @content_array;
    my ( $status, $error_mesg );
    my $domain = $par{'data'};
    my $cmd_str = $cmd.' -f '.$domain;
    my $search_result =`$cmd_str`;
    if( $search_result != 0){
         my %conf_data =  &get_config_hash($search_result);
         push(@content_array,\%conf_data);
         $status = 0;
         $error_mesg = "查找成功";
    }
    else{
       @content_array = ();
       $status = 1;
       $error_mesg = "查找失败";
    }
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $search_result;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    my $ret = $json->encode(\%ret_data);
    print $ret; 

}

sub delete_data() {
    my @lines_content = ();
    my ( $status, $mesg) = &get_several_records_by_ids($conf_file, $par{'id'},\@lines_content);
    
    foreach(@lines_content){
        my %config = &get_config_hash( $_ );
        my $file_url = $config{'path'};
        if(-e $file_url){
            system("rm -rf $file_url");
        }

      
    }
    
     ( $status, $mesg ) = &delete_several_records_by_id( $conf_file, $par{'id'});
    
    if($status == 0){
        $mesg = "删除成功";
        $reload = 1;
        &create_need_reload_tag();
    }
    # my %ret_data;
    # %ret_data->{'status'} = $status;
    # %ret_data->{'mesg'} = $mesg;

    # my $ret = $json->utf8->encode(\%ret_data);
    # print $ret;
    $log_oper = 'del';
    &send_status( $status, $mesg);
}

sub get_content($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );

    my $from_num = ( $current_page - 1 ) * $page_size;
    my $to_num = $current_page * $page_size;

    my @lines = ();
    ( $status, $error_mesg ) = &read_config_lines( $conf_file, \@lines );

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
    for ( my $i = $from_num; $i < @lines; $i++ ) {
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
    $config{'id'}            = $temp[0];
    $config{'name'}          = $temp[1];
    $config{'description'}   = $temp[2];
    $config{'type'}          = $temp[3];
    $config{'path'}          = $temp[4];
    
    if($temp[3] eq 'custom'){
        my @lines_urls = ();
        my $path_url = $temp[4];
        &read_config_lines($path_url,\@lines_urls);
        $config{'urls'}   = join("\n",@lines_urls);
    }
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'description'} ); 
    push( @record_items, "custom" );

    my $path_item = $conf_file_custom.'/'.'custom';
    push( @record_items, $path_item );
    my $record = join (",", @record_items);
    return ($record,$path_item);
}

sub toggle_enable($$) {
    my $item_id = shift;
    my $enable = shift;
    my $operation = "启用";
    $log_oper = 'enable';
    if ( $enable ne "on" ) {
        $operation = "禁用";
        $log_oper = 'disable';
    }
    my ( $status, $mesg, $line_content ) = &get_one_record( $conf_file, $item_id );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, $mesg );
        return;
    }

    my %config = &get_config_hash( $line_content );
    $config{'enable'} = $enable;
    $line_content = &get_config_record(\%config);

    my ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $line_content );
    if( $status != 0 ) {
        $mesg = "操作失败";
    }

    &send_status( $status, $mesg );
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
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
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

    if(! -e $conf_dir."/custom"){
        system("mkdir -p $conf_dir/custom");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
    
}

sub apply_data() {
    my $result;
    system($cmd_apply);
    $result = $?;
    chomp($result);
    my $msg;
    if($result == 0){
        $msg = "应用成功";
    }else{
        $msg = "应用失败";
    }
    &clear_need_reload_tag();
    $log_oper = 'apply';
    &send_status( 0, 0, $msg );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
#下载数据
sub export_data() {
    my ( $status, $mesg,$file_name ) = &generate_download_file();
    if( $status == 0 ){
        open( DOWNLOADFILE, "<$file_name" ) or $status = -1;
        @fileholder = <DOWNLOADFILE>;
        close ( DOWNLOADFILE );
        if ( $status == 0 ) {
            print "Content-Type: application/x-download\n";  
            print "Content-Disposition: attachment;filename=$file_name\n\n";
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
sub generate_download_file() {
    #===第一步:根据上传的数据,筛选出要下载的规则文件===#
    my ( $status, $mesg, $record, $filename  ) = ( -1, "未生成导出文件", "", "" );
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
    #===第二步:组装需要下载的文件的全路径===#
    $filename = $data{'path'}.'/domains';
    return ( $status, $mesg, $filename );
}
