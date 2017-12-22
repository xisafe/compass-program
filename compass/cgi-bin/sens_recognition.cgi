#!/usr/bin/perl
#author: pujiao
#createDate: 2016/07/22
use Encode;
use List::Util qw(max);
require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file_rule;   #用户自定义规则库所存放的文件夹
my $conf_file;          #URL规则所存放的文件
# my $conf_file_rule_pid;#用于存储用户自定义规则库的主键文件
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
    $custom_dir           = '/security_objects/dataleak';                                   #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir             = "/var/efw".$custom_dir;                     #规则所存放的文件夹
    $conf_file            = $conf_dir.'/config';                     #存储URL规则库信息
    $conf_file_rule     = $conf_dir.'/rules';                        #保存用户自定义的URL规则库文件夹
    # $conf_file_rule_pid = $conf_dir.'/rule_pid';                     #保存用户自定义的规则库主键
    $need_reload_tag      = $conf_dir.'/add_list_need_reload_url';      #启用信息所存放的文件
    # $cmd                = "sudo /usr/local/bin/search_domain.py";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/sens_recognition.js"></script>';
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
    elsif ($action eq 'check_rule') {
        #==禁用规则==#
        &check_rule($par{'rule_data'});
        # print $par{'rule_data'};
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
    my $old_record;
    my $id_arr;
    my ($record,$path_item) = &get_config_record( \%par );
    my $item_id = $par{'id'};
    my $str_rules = $par{'rules'};
    # $str_rules =~ s/\(/（/g;
    # $str_rules =~ s/\)/）/g;    
    $str_rules =~ s/\r//g;
    # $str_rules =~ s/\n/,/g;
    my @arr_rules = split("\n",$str_rules);

    my @lines;
    &read_config_lines($conf_file,\@lines);
    

    my ( $status, $mesg ) = ( -1, "未保存" );
    foreach (@lines){
        push(@id_arr,(split(",",$_))[0]); 
    }
  
    if( $item_id eq '' ) {
         #添加
        #重复性判断
        foreach (@lines){
            if($par{'name'} eq (split(",",$_))[1]){
                ( $status, $mesg ) = ( -2, $par{'name'}."已占用" );
            }
        }
            #重复性检测成功
        if($status != -2){
             $maxid = (max( @id_arr ) >= 1000) ? max( @id_arr ) + 1 : 1001;
            ( $status, $mesg ) = &append_one_record( $conf_file, "$maxid,$record$maxid" );
           
        }

            #创建并写入自定义用户的规则库-----begin-------
            system("mkdir $conf_file_rule");
            system("touch $conf_file_rule/dataleak$maxid");

            my ( $status, $mesg ) = &write_config_lines( "$conf_file_rule/dataleak$maxid", \@arr_rules );

            #创建并写入自定义用户的规则库 -------end----------
       
    } else {

        if($status != -2){
            my @record_temp = split(",",$record);
            ( $status, $mesg, $old_record ) = &get_one_record_by_id( $conf_file,$item_id);
            $path_item = (split(",",$old_record))[4]; #获取配置文件中存放的路径
            $record_temp[3] = $path_item;

            my $record_str = join (",", @record_temp);
            ( $status, $mesg ) = &update_one_record_by_id( $conf_file, $item_id, "$item_id,$record_str");
            `> $path_item`;
            my ( $status, $mesg ) = &write_config_lines( $path_item, \@arr_rules );

        }
    }

    
    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }
    &send_status( $status, 1, $mesg);
}

sub check_rule($) {
    my $rule_data = shift;
    my @rule_array = split(/\n/,$par{'rule_data'},);
    my %ret_data;
    my $status = 1;
    my $error_rule = '';
    my $error_status = '';
    my $i = 0;
    foreach my $rule_check(@rule_array) {
        $i++;
        # $rule_check =~ s/\'/\"/g;
        # my $cmd = "sudo /usr/local/bin/check_pattern.py -p \'$rule_check\'";
        my $cmd = 'sudo /usr/local/bin/check_pattern.py'.' '.'-p'.' '.'\''.$rule_check.'\'';
        $status = `$cmd`;
        if($status =~/0/){
            # $error_rule = $error_rule.' '.$rule_check
        }
        else{
            $error_status = $error_status.';'.$status;
            $error_rule = $error_rule.';'.$i;
        }

    }
    %ret_data->{'error_status'} = $error_status;
    %ret_data->{'error_rule'} = $error_rule;

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my @lines_system = ();
    my $search_result;
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );#读取用户的URL规则库；
    
    my $record_num = @lines;
    my $search = $par{'search'};
    if($search){

        chomp($search);
        #===转换成小写，进行模糊查询==#
        $search = lc($search);
        
        for(my $i = 0; $i < $record_num; $i++){
            chomp(@lines[$i]);
           
            my %conf_data = &get_config_hash(@lines[$i]);
            if ($conf_data{'name'} !~ m/$search/ && $conf_data{'description'} !~ m/$search/) {
                next;
            }
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
    my @lines_content = ();
    my ( $status, $mesg) = &get_several_records_by_ids($conf_file, $par{'id'},\@lines_content);
    
    foreach(@lines_content){
        my %config = &get_config_hash( $_ );
        my $file_rule = $config{'path'};
        if(-e $file_rule){
            system("rm -rf $file_rule");
        }
    }
    
    ( $status, $mesg ) = &delete_several_records_by_id( $conf_file, $par{'id'});
    
    if($status == 0){
        $mesg = "删除成功";
    }

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;

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
    $config{'id'}   = $temp[0];
    $config{'name'}          = $temp[1];
    $config{'description'}   = $temp[2];
    $config{'type'}          = $temp[3];
    $config{'path'}          = $temp[4];
    
    if($temp[3] == "1"){
        my @lines_rules = ();
        my $path_rule = $temp[4];
        &read_config_lines($path_rule,\@lines_rules);
        $config{'rules'}   = join("\n",@lines_rules);
    }
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'description'} ); 
    push( @record_items, "1" );
    my $path_item = $conf_file_rule.'/'.'dataleak';

    push( @record_items, $path_item );
    my $record = join (",", @record_items);
    return ($record,$path_item);
}

sub toggle_enable($$) {
    my $item_id = shift;
    my $enable = shift;

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

    if(! -e $conf_dir."/rules"){
        system("mkdir -p $conf_dir/rules");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
    
}

sub apply_data() {
    my $result;
    system($cmd);
    `sudo /usr/local/bin/setwebdefend.py`;
    $result = $?;
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