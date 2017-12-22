#!/usr/bin/perl
#==============================================================================#
#
# 描述: 上行链路页面
#
# 作者: 辛志薇
# 公司: capsheaf
# 历史:
#   2015-1-27 创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $uplink_config_file_path;
my $uplinks_dir;
my $need_reload_file;
my $smart_routing_config_file;

my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my $CUR_PAGE = "xxxx" ;  #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post请求传过来的变量
    &getcgihash(\%par);
    #获取get请求传过来的变量
    &get_query_hash(\%query);    # 这个好像是被写入了list_panel_opt.pl文件里,确实是在那个头文件里面啊
    #初始化变量值
    &init_data();
    &make_file();
    #做出响应
    &do_action();
}
sub init_data(){
    $uplink_config_file_path = '/var/efw/outboundlb/uplink_config';
    $uplinks_dir = "/var/efw/uplinks";
    $need_reload_file = "/var/efw/outboundlb/needreload";   # 这个其实就是智能路由对应的启动应用文件，
    $smart_routing_config_file = "/var/efw/outboundlb/config";
    # 当上行链路发生更新后，智能路由页面应该弹出‘应用’提示框
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/outboundlb_uplink_setting.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#
}

sub make_file(){
    if(! -e $uplink_config_file_path){
        system("touch $uplink_config_file_path");
    }
}
sub do_action() {
    my $action = $par{'ACTION'};           # 这个是post方法发送过来的 ACTION 参数值
    my $query_action = $query{'ACTION'};   # 这个是get方法发送过来的 ACTION 参数值
    my $panel_name = $par{'panel_name'};

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ( $action eq 'save_data' ) {
        &save_data();
        $log_oper = 'edit';
    }
    elsif ( $action eq 'load_data' ) {
        &load_data();
    }
    elsif( $action eq 'load_uplinks_list' ){
        &load_uplinks_list();
    }
    elsif( $action eq 'is_need_reload' ){
        &init_show_apply_box();
    }
    elsif( $action eq 'apply' ){
        &apply_data();
        $log_oper = 'apply';
    }
    elsif( $action eq 'apply_data' ){
        &apply_data();
        $log_oper = 'apply';
    }
    elsif( $action eq 'enable_data'){
        &toggle_enable("on");
    }
    elsif( $action eq 'disable_data'){
        &toggle_enable("off");
    }
    elsif( $action eq 'delete_data'){
        &delete_data();
    }
    else {
        &show_page();
    }
}
sub init_show_apply_box(){
    my %response;

    if(-e $need_reload_file ) {
        %response->{'need_reload'} = 1;
        %response->{'mesg'} = "路由规则已改变，请应用该规则以使改变生效";
    }else{
        %response->{'need_reload'} = 0;
    }
    my $ret = $json->encode(\%response);
    print $ret;
}

sub show_page() {
    &openpage(_('上行链路'), 1, $extraheader);
    # &openbigbox($errormessage, $warnmessage, $notemessage);
    # &closebigbox();
    &display_main_body();
    &closepage();
}

sub display_main_body() {
    printf<<EOF
    <div id="mesg_box_id" style="width: 96%;margin: 20px auto;"></div>
    <div id="uplink_add_panel_config" style="width: 96%;margin: 20px auto;"></div>
    <div id="uplink_list_panel_config" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}
sub create_need_reload_tag(){
    if(! -e $need_reload_file){
        system( "touch $need_reload_file" );
    }
}
sub clear_need_reload_tag() {
    if( -e $need_reload_file ){
        system( "rm $need_reload_file" );
    }
}
sub apply_data() {
    &clear_need_reload_tag();
    system("/usr/local/bin/restartoutboundlb");
    $status = $?>>8;

    if( $status != 0 ){
        &send_status(-1, 0, "应用失败");
    }else{
        &send_status(0, 0, "应用成功");
    }
}

sub toggle_enable($){
    my $enable_str = shift;   # enable_str的值其实就是字符串‘on’或者‘off’
    my @lines = ();
    my ( $status, $reload, $mesg ) = (-1, 0, "未操作");

    ( $status, $mesg ) = &read_config_lines( $uplink_config_file_path, \@lines );
    for ( my $i = 0; $i < @lines; $i++ ) {
        if( $par{'id'} eq "$i" ) {
            my @arr = split(/,/, $lines[$i]);
            $arr[0] = $enable_str;
            $lines[$i] = join ",", @arr;
        }
    }

    ( $status, $mesg ) = &write_config_lines( $uplink_config_file_path, \@lines );
    if( $status != 0 ){
        if( $enable_str eq "on" )     {  $mesg = "启用失败";  }
        elsif( $enable_str eq "off" ) {  $mesg = "禁用失败";  }
        &send_status( $status, 0, $mesg );
        return;
    }
    $reload = 1;
    &create_need_reload_tag();

    # if($enable_str eq "on")     {  $mesg = "启用成功";  }   成功的话就不要提示了！
    # elsif($enable_str eq "off") {  $mesg = "禁用成功";  }
    &send_status( $status, $reload, "" );

}

sub get_config_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'enable'}     = $temp[0];
    $config{'name'}        = $temp[1];
    $config{'true_name'}   = $temp[2];
    $config{'weight'}      = $temp[3];
    $config{'band_width'}  = $temp[4];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    if( !$hash_ref->{'enable'} ){
        push( @record_items, "off");
    }else{
        push( @record_items, "on");
    }
    # push( @record_items, $hash_ref->{'enable'} );
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'true_name'} );
    push( @record_items, $hash_ref->{'weight'} );
    push( @record_items, $hash_ref->{'band_width'} );

    return join ",", @record_items;
}
sub handle_before_save_data(){
    my $item_id = $par{'id'};
    my $name;
    my @temp;
    my @virtual_names;
    my $flag = 0;

    if( !$par{'name'} ){
        return(-1,"对不起,链路名不能为空");
    }
    if( !$par{'weight'} && $par{'weight'} !=0 ){
        return(-1,"对不起，权重为必填项");
    }
    elsif( $par{'weight'} !~ /^[1-9][0-9]*$/ ){
        return(-1, "对不起，权重应为数字类型");
    }else{
        if( $par{'weight'} < 1 || $par{'weight'} > 10 ){  return(-1, "对不起，权重值应在1-10之间(包含1和10)");  }
    }

    if( !$par{'true_name'} ){
        # return(-1,"对不起，实际链路不能为空");
        return(-1,"对不起，所有的链路都已被使用，故无法添加");
    }
    if( !$par{'band_width'} && $par{'band_width'} !=0 ){
        return(-1,"对不起，带宽值为必填项");
    }
    elsif( $par{'band_width'} !~ /^[1-9][0-9]*$/ ){
        return(-1, "对不起，带宽应为数字类型");
    }
    # if( $item_id eq '' ){   # 切记只有在添加时才进行查重处理，编辑时不能查重(出错啦：编辑的时候也要查重因为在编辑的时候人家是可以修改虚拟名的，改的虚拟名就有可能和已有的名字发生‘重名’)
        $name = $par{'name'};
        open( UPLINK_FH, "<$uplink_config_file_path" );
        while(<UPLINK_FH>){
            chomp($_);
            @temp = split(/,/, $_);
            push( @virtual_names, $temp[1] );      # $temp[1]为虚拟链路名
        }
        close(UPLINK_FH);
        # foreach(@virtual_names){
        #     if( $_ eq "$name" ){ $flag = 1; last; }
        # }
        my $cur_name;
        for(my $i=0; $i<@virtual_names; $i++){
            $cur_name = $virtual_names[$i];
            if( $cur_name eq "$name" && $item_id eq '') { $flag = 1; last; }
            elsif( $item_id ne '' && $item_id ne "$i" && $cur_name eq "$name"){ $flag = 1; last; }
        }
        if($flag == 1){  return(-1,"对不起此虚拟名称已被使用");  }
    # }
    return(0,"");
}

sub save_data() {
    my $reload = 0;
    my ( $status, $mesg ) = &handle_before_save_data();    # 调用预处理函数
    if( $status == -1 ){
        &send_status( $status, $reload, $mesg );
        return;
    }
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};

    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $uplink_config_file_path, $record );
        $log_oper = "add";
    } else {
        ( $status, $mesg ) = &update_one_record( $uplink_config_file_path, $item_id, $record );
        $log_oper = "edit";
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        # $mesg = "保存成功";
    }

    &send_status( $status, $reload, "" );
}
sub load_uplinks_list(){
    my %response;
    my $dir = $uplinks_dir;
    my @all_uplinks;
    my @used_uplinks;
    my %uplinks_hash;

    opendir DIR,$dir;
    foreach my $uplink (readdir DIR) {   # 从目录中读取所有的接口名，存放到bonds数组中
        if( $uplink eq "." || $uplink eq ".." ) { #因为凡是目录的内容都有两个隐藏的子目录，值就是'.'和'..'所以要过滤掉！
            next;
        }else {  # $uplink是目录类型
            push( @all_uplinks,$uplink );
            $uplinks_hash{ $uplink } = $uplink;
        }
    }

    open( UPLINK_FH, "<$uplink_config_file_path" );
    while(<UPLINK_FH>){
        chomp($_);
        @temp = split(/,/, $_);
        push( @used_uplinks, $temp[2] );      # $temp[2]为实际链路名
    }
    close(UPLINK_FH);

    my $used_uplinks = join(" ", @used_uplinks);
    my $uplink;
    foreach(@all_uplinks){
        $uplink = $_;
        if( $used_uplinks =~ /$uplink/){
            delete $uplinks_hash{ $uplink };
            next;
        }
    }
    # %response->{'uplinks_list'} = \@all_uplinks;
    %response->{'uplinks_list'} = \%uplinks_hash;
    my $ret = $json->encode(\%response);
    print $ret;
}

sub load_data(){
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub get_detail_data($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $uplink_config_file_path, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records( $uplink_config_file_path, $page_size, $current_page, \@lines );
    }

    for( my $i = 0; $i < @lines; $i++ ) {
        my $id = $from_num + $i;
        if( !$LOAD_ONE_PAGE ) {
            $id = $i;
        }
        my %hash = &get_config_hash( $lines[$i] );
        $hash{'id'} = $id;
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg, $total_num );
}

sub delete_data() {
    my $reload = 0;

    my $line_id = $par{'id'};
    # my @lines = &read_config_file( $uplink_config_file_path );
    my @lines = ();
    &read_config_lines( $uplink_config_file_path, \@lines );
    my $line_record = $lines[ $line_id ];
    my @tmp = split(/,/, $line_record);
    my $uplink_to_del = $tmp[2];

    open (FILE_HOLDER, "<$smart_routing_config_file");
    while( <FILE_HOLDER> ){
        my @arr = split(/,/,$_);
        my $uplinks = $arr[5];
        my @uplinks_arr = split(/&/, $uplinks);
        my $uplink;
        foreach(@uplinks_arr){
            $uplink = $_;
            if($uplink_to_del =~ /$uplink/){
                &send_status(-1, 0, "对不起，此行的链路正在被智能路由使用，无法删除");
                return;
            }
        }
    }
    close FILE_HOLDER;

    my ( $status, $mesg ) = &delete_several_records( $uplink_config_file_path, $par{'id'} );

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
    }
    &send_status( $status, $reload, "" );
     # &send_status( $status, $reload, "删除成功" );
}
sub send_status($$$) {
    my ($status, $reload, $mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'reload'} = $reload;
    # 最新：做这样一个修改，在启用`禁用`添加`删除`这些操作'成功'($status == 0)的时候就不发送mesg，在操作'失败'($status != 0)的时候发送mesg
    if( $status != 0 ){
        %hash->{'mesg'} = $mesg;
    }
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
    my $result = $json->encode(\%hash);
    print $result;
}

