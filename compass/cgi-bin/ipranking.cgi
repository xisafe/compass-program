#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/12/03
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
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
my $cmd_detail;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
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
    $need_reload_tag       = $conf_dir.'/add_list_need_ipranking'; #表示需要重新应用的文件
    $cmd                   = "sudo /usr/local/bin/getIPRankingFlowinfo.py";
    $cmd_detail            = "sudo /usr/local/bin/getDetailIPFlowinfo.py";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/ipranking_init.js"></script>';
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
    elsif ($action eq 'load_data' && $panel_name eq 'detail_panel') {
        #==加载详细数据==#
        &load_data_detail();
    }
    elsif ($action eq 'save_data') {
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
    &display_nodata();
    &closepage();
}

sub display_list_div() {
    printf<<EOF
    <div id="mesg_box_iprank" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_iprank_list" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_detail" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
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

sub save_data() {
    my $reload = 0;
   

    my ( $status, $mesg ) = ( -1, "未保存" );
    my $ENABLED;
    if($par{'enable'}){
        $ENABLED = $par{'enable'};
    }else{
        $ENABLED = 'off';
    }
    $settings{'ENABLED'} = $ENABLED;
    &writehash( $settings_file, \%settings );
    $status = 0;
    
    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
}
sub load_data(){
    my %ret_data;
    my $content_array;
    my $unit = $par{'unit'};
    my $timetype = $par{'timetype'};
    my $filterIP = "";
    if($par{'filterIP'}){
        $filterIP = $par{'filterIP'};
    }
    my ( $status, $error_mesg, $total_num ) = (1,"未读取",0);
    my $cmd_run = 'sudo /usr/local/bin/getIPRankingFlowinfo.py -u KB/s -t rt -f "" 2>/dev/null';
    my $str_json = "";
    if($par{'filterIP'} && !(&validipormask($filterIP))){
        $str_json = "no data";
    }else{
        $str_json = `$cmd -u $unit -t $timetype -f '$filterIP' 2>/dev/null`;
    }
    chomp($str_json);
    if($str_json eq "no data"){
        %ret_data->{'nodata'} = "暂时无信息展示";
        $content_array = $str_json;
    }else{
        $content_array = $json->decode( $str_json);
        $total_num = @$content_array;
        #$content_array = $str_json;
    }
    

    %ret_data->{'detail_data'} = $content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub load_data_detail(){
    my %ret_data;
    my $content_array;
    my $unit = $par{'unit'};
    my $timetype = $par{'timetype'};
    my $ip_addr = $par{'ip_addr'};
    my ( $status, $error_mesg, $total_num ) = (1,"未读取",0);
    my $str_json = `$cmd_detail -u $unit -t $timetype -a $ip_addr 2>/dev/null`;
    chomp($str_json);
    if($str_json eq 'no data'){
        %ret_data->{'nodata'} = "暂时无信息展示";
    }else{
        my $json_obj = $json->decode( $str_json);
        $content_array = $json_obj -> {'app_info'};
        $total_num = @$content_array;
        # $content_array = $str_json;
    }
    

    %ret_data->{'detail_data'} = $content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}


sub delete_data() {
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});

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
    $config{'name'}   = $temp[1];
    $config{'protocol'}   = $temp[2];
    $config{'port'}   = $temp[3];
    $config{'outtime'}   = $temp[4];
    $config{'description'}   = $temp[5];
    $config{'enable'}   = $temp[0];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    if($hash_ref->{'enable'}){
        push( @record_items, $hash_ref->{'enable'} );
    }else{
        push( @record_items, "off" );
    }
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'protocol'} );
    push( @record_items, $hash_ref->{'port'} );
    push( @record_items, $hash_ref->{'outtime'} );
    push( @record_items, $hash_ref->{'description'} );
    return join (",", @record_items);
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
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
    
}

sub apply_data() {
    my $result;
    system($cmd);
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