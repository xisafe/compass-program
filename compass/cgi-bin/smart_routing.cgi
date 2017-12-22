#!/usr/bin/perl
#==============================================================================#
#
# 描述: 智能路由页面
#
# 作者: 辛志薇
# 公司: capsheaf
# 历史:
#   2014.12.1 创建
#
#==============================================================================#
use Encode;
use Digest::SHA qw(sha1_hex);

require '/var/efw/header.pl';
require 'list_panel_opt.pl';    #

my $base_dir;
my $settings_file_path; # settings文件路径
my $config_file_path;   # config  文件路径
my $isp_dir;
my $uplinks_dir;
my $uplink_config_file_path;
my $isp_config_file_path;
my $isp_default_config_file;
my $extraheader;        #
my %par;                #
my %query;              #
my $LOAD_ONE_PAGE = 0;  #
my $json = new JSON::XS;#
my $need_reload_file;

my %uplinks_hash = ();
my %reverse_hash = ();
#记录日志的变量
# my $CUR_PAGE = "智能路由" ;      #当前页面名称，用于记录日志
# my $log_oper ;                   #当前操作，用于记录日志，
#                                  # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
# my $rule_or_congfig = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

&main();

sub main() {
    &getcgihash(\%par);
    &get_query_hash(\%query);    # 
    &init_data();
    &make_file();
    &do_action();
}

sub init_data(){
    $base_dir = '/var/efw/outboundlb';
    $settings_file_path   = $base_dir . '/settings';
    $config_file_path  = $base_dir . '/config';
    $isp_dir = "/var/efw/outboundlb/isp";
    $isp_config_file_path = "/var/efw/outboundlb/isp/config";
    $isp_default_config_file = "/var/efw/outboundlb/isp/default/config";
    $uplinks_dir = "/var/efw/uplinks";
    $uplink_config_file_path = $base_dir . '/uplink_config';
    $need_reload_file = "/var/efw/outboundlb/needreload";
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/smart_routing.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/smart_routing.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#
}

sub create_need_reload_file() {
    if(! -e $need_reload_file){
        system( "touch $need_reload_file" );
    }
}

sub clear_need_reload_file() {
    if( -e $need_reload_file ){
        system( "rm $need_reload_file" );
    }
}
sub apply_data() {
    &clear_need_reload_file();
    system("/usr/local/bin/restartoutboundlb");
    $status = $?>>8;
    if( $status != 0 ) {            $mesg = "应用失败";        }else{  $mesg = "应用成功"; }
    # $log_oper = 'apply';
    &send_status( $status, 0, $mesg );
}

sub make_file(){

    if(! -e $base_dir){
        system("mkdir -p $base_dir");
    }
    if(! -e $isp_dir){
        system("mkdir -p $isp_dir");
    }
    if(! -e $settings_file_path){
        system("touch $settings_file_path");
        system("echo ENABLED=off >> $settings_file_path");
    }
    if(! -e $config_file_path){
        system("touch $config_file_path");
    }
    if(! -e $isp_config_file_path){
        system("touch $isp_config_file_path");
    }
}

sub do_action() {
    my $action = $par{'ACTION'};           # 
    my $query_action = $query{'ACTION'};   # 
    my $panel_name = $par{'panel_name'};

    &showhttpheaders();
    if ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ( $action eq 'save_data' ) {
        &save_data();
    }
    elsif ( $action eq 'load_data' ) {
        &load_data();
    }
    elsif ($action eq 'enable_data') {
        &toggle_enable( "on" );
    }
    elsif ($action eq 'disable_data') {
        &toggle_enable( "off" );
    }
    elsif ( $action eq 'load_other_data' ) {
        &load_other_data();
    }
    elsif ( $action eq 'MOVE_UP') {
        &handle_move_action();
    }
    elsif ( $action eq 'MOVE_DOWN') {
        &handle_move_action();
    }
    elsif ($action eq 'delete_data') {
        &delete_data();
    }
    else {
        &show_page();
    }
}
sub toggle_enable($) {
    my $enable_str = shift;   # 
    my $enable = shift;
    my $operation = "启用";
    $log_oper = 'enable';
    if ( $enable ne "on" ) {
        $operation = "禁用";
        $log_oper = 'disable';
    }
    my @lines = ();
    my ( $status, $reload, $mesg ) = (-1, 0, "未操作");

    ( $status, $mesg ) = &read_config_lines( $config_file_path, \@lines );
    for ( my $i = 0; $i < @lines; $i++ ) {
        if( $par{'id'} eq "$i" ) {
            my @arr = split(/,/, $lines[$i]);
            $arr[0] = $enable_str;
            $lines[$i] = join ",", @arr;
        }
    }

    ( $status, $mesg ) = &write_config_lines( $config_file_path, \@lines );
    if( $status != 0 ){
        if($enable_str eq "on")     {  $mesg = "启用失败";  }
        elsif($enable_str eq "off") {  $mesg = "禁用失败";  }
        &send_status( $status, 0, $mesg );
        return;
    }
    if( $status == 0 ){
        $reload = 1;
        &create_need_reload_file();
    }
    
    &send_status( $status, $reload, "" );

}
sub handle_move_action(){    # 
    my $type = $par{'ACTION'};
    my $cur_line_id = $par{'LINE_ID'};
    my $max_line_num = $par{'MAX_LINE_NUM'};
    my $last_line = $max_line_num-1;      # 
    my $last_last_line = $max_line_num-2; # 
    my $new_line_id;
    my ( $status, $reload, $mesg ) = (-1, 0, "");

    if( $type eq "MOVE_UP" )        { $mesg = "未上移";   $new_line_id = $cur_line_id-1; }
    elsif( $type eq "MOVE_DOWN" )   { $mesg = "未下移";   $new_line_id = $cur_line_id+1; }
    else{ $mesg = "参数字符串不能被识别"; &send_status( $status, $reload, $mesg ); return; }

    if( $cur_line_id == 0 && $type eq "MOVE_UP"){
        $mesg = "第一行的规则不可上移！";    &send_status( $status, $reload, $mesg ); return;
    }elsif( $cur_line_id eq "$last_line" && $type eq "MOVE_UP"){
        $mesg = "默认路由不可上移！";        &send_status( $status, $reload, $mesg ); return;
    }
    if( $cur_line_id eq "$last_last_line" && $type eq "MOVE_DOWN"){
        $mesg = "最后一行的规则不可下移！";  &send_status( $status, $reload, $mesg ); return;
    }elsif( $cur_line_id eq "$last_line" && $type eq "MOVE_DOWN"){
        $mesg = "默认路由不可下移！";        &send_status( $status, $reload, $mesg ); return;
    }

    ( $status, $mesg, $line_content_1 ) = &get_one_record($config_file_path,$cur_line_id);   # i
    ( $status, $mesg, $line_content_2 ) = &get_one_record($config_file_path,$new_line_id);   # i-1

    ( $status, $mesg ) = &update_one_record( $config_file_path, $new_line_id, $line_content_1 );  #把第i行的内容放到第i-1行上去
    if( $status != 0 ) { $mesg = "更新第"+$new_line_id+"行失败"; &send_status( $status, $reload, $mesg ); return; }

    ( $status, $mesg ) = &update_one_record( $config_file_path, $cur_line_id, $line_content_2 );   #把第i-1行的内容放到第i行上去
    if( $status != 0 ) { $mesg = "更新第"+$cur_line_id+"行失败"; &send_status( $status, $reload, $mesg ); return; }
    
    # $status = 0;
    if( $type eq "MOVE_UP" )        { $mesg = "上移操作已成功"; }
    elsif( $type eq "MOVE_DOWN" )   { $mesg = "下移操作已成功"; }
    if( $status == 0 ){  $reload = 1;  &create_need_reload_file();  }
    
    &send_status( $status, $reload, $mesg );
}

sub load_other_data(){
    my %response;
    my @lines=();
    my ( $status, $mesg ) = &read_config_lines( $isp_config_file_path, \@lines);
    if($status != 0){
        $mesg = "读取ISP配置文件内容失败";
        &send_status( $status, 0, $mesg );
        return;
    }
    my @name_array;
    for(my $i=0; $i<@lines; $i++){
        chomp( $lines[$i] );
        my @temp = split(/,/, $lines[$i]);
        push(@name_array, $temp[0]);
    }
    # my @default_isp = ("中国电信","中国联通","中国教育网","中国移动","中国铁通","中国网通");
    # my @default_isp = ();
    @lines = ();
    &read_config_lines( $isp_default_config_file, \@lines);
    foreach( @lines ){
        my @arr = split(/,/, $_);
        push( @name_array, $arr[0] );
    }
    # push( @name_array, @default_isp );

    my @addr_nodes, @addr_groups;
    push( @addr_nodes, "test_node1");     push( @addr_nodes, "test_node2");
    push( @addr_groups, "test_group1");   push( @addr_groups, "test_group2");

    open( UPLINK_FH, "<$uplink_config_file_path" );
    while(<UPLINK_FH>){
        @temp = split(/,/, $_);
        if( $temp[0] eq "on" ){   # 只有当第1个字段为on时，该行的链路才是有效可以选的！
            # $temp[2]为实际链路名
            $uplinks_hash{ $temp[2] } = $temp[1];  # $temp[1]为虚拟链路名，此句即建立从实际链路名到虚拟链路名的映射
        }
    }
    close(UPLINK_FH);

    %response->{'isp_name_list'} = \@name_array;    # 
    %response->{'addr_nodes'}    = \@addr_nodes;
    %response->{'addr_groups'}   = \@addr_groups;
    %response->{'uplinks_hash'}  = \%uplinks_hash;

    if(-e $need_reload_file ) {
        %response->{'need_reload'} = 1;
        %response->{'mesg'} = "路由规则已改变，请应用该规则以使改变生效";    # 
    }else{
        %response->{'need_reload'} = 0;
    }
    my $ret = $json->encode(\%response);
    print $ret;

}

sub load_data(){
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'MAX_LINE_NUM'} = $total_num;   # 
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub get_detail_data($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;
    my %default_routing_hash;
    my $search = $par{'search'};
    my $search_id;
    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );

    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $config_file_path, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records( $config_file_path, $page_size, $current_page, \@lines );
    }
    if ( $search ne "" ) {
        if( !$LOAD_ONE_PAGE ){
            $search_id = 0;
        }else{ $search_id = $from_num; }

    }

    for( my $i = 0; $i < @lines; $i++ ) {
        my $id = $from_num + $i;
        if( !$LOAD_ONE_PAGE ) {  #
            $id = $i;
        }

        my %hash = &get_config_hash( $lines[$i] );
        $hash{'id'} = $id;   # 

        if ( $search ne "" ) {             #

            if ( !( $hash{'routing_name'}      =~ m/$search/ ) &&
                 !( $hash{'links'}        =~ m/$search/ ) 
                  ) {
                    $total_num--;
                    next;
            }else{

                $hash{'search_id'} = $search_id;
                $search_id++;
                push( @$content_array_ref, \%hash );
            }
        }else {
            if ( $id == 0 )         { $hash{'IS_FIRST_LINE'} = 1; }    # 
            else                    { $hash{'IS_FIRST_LINE'} = 0; }
            if ( $id == @lines-1 )  { $hash{'IS_LAST_LINE'}  = 1; }    # 
            else                    { $hash{'IS_LAST_LINE'}  = 0; }
            push( @$content_array_ref, \%hash );

        }
        
    }
    # 加载最后一行默认路由
    $default_routing_hash{'IS_DEFAULT_ROUTING'} = "true";
    $default_routing_hash{'enabled'} = "默认路由";
    $default_routing_hash{'routing_name'} = "默认路由";
    $default_routing_hash{'routing_src'} = "全部";
    $default_routing_hash{'routing_dst'} = "全部";
    $default_routing_hash{'protocal'} = "默认路由";
    $default_routing_hash{'links'} = "全部";
    $default_routing_hash{'time'} = "全部";
    $default_routing_hash{'scheduler'} = "";
    push( @$content_array_ref, \%default_routing_hash);
    $total_num = $total_num+1;      # 
    # 加载默认路由结束
    $search_id=0;
    return ( $status, $mesg, $total_num );

}
sub handle_before_save_data(){
    my ( $status, $mesg ) = ( -1, "" );
    if( $par{'id'} eq ""){ # 
        if( $par{'routing_name'} eq "" ){
            $mesg = "对不起，名称不能为空！";
            return($status, $mesg);
        }

        &read_config_lines( $config_file_path, \@file_lines );
        foreach my $line( @file_lines ) {
            my @temp = split( /,/, $line );
            if( $par{'routing_name'} eq "$temp[1]") {   # 
                $mesg="对不起，此名称已经存在!";
                return($status, $mesg);
            }
        }
        if( !$par{'SELECTED_UPLINKS'} ){
            $mesg = "对不起，上行链路不能为空！请至少选择一个";
            return($status, $mesg);
        }
    }

    if( $par{'scheduler'} eq 'none' ){
        # 将要保存的行(来自编辑或添加)没有使用调度策略，即值为none，那么直接通过，添加成功
    }else{
        @file_lines = ();
        &read_config_lines( $config_file_path, \@file_lines );
        my $i = 0;  my $k;
        foreach my $line( @file_lines ) {
            my @temp = split( /,/, $line );
            my $scheduler = $temp[7];
            if( $scheduler eq "") {
                $i++;  next;
            }else{
                my @to_saved_uplinks = split(/&/, $par{'SELECTED_UPLINKS'} );
                my @saved_uplinks = split(/&/, $temp[5] );

                foreach my $uplink( @to_saved_uplinks ){
                    foreach my $up( @saved_uplinks ){
                        if( $uplink eq $up ){
                            if( $par{'id'} ne "" && $par{'id'} eq "$i" ){
                                next;
                            }
                            open( UPLINK_FH, "<$uplink_config_file_path" );
                            while(<UPLINK_FH>){
                                @temp = split(/,/, $_);
                                if( $uplink eq $temp[2] ){  $k = $temp[1];  }
                                # $uplinks_hash{ $temp[2] } = $temp[1];
                            }
                            close(UPLINK_FH);
                            # $k = $uplinks_hash{ $uplink };
                            $mesg = $mesg."对不起，您选择的链路（$k）已被第$i条规则使用，添加失败";
                            return($status, $mesg);   # last; return($status,$mesg);  bug：return前面执行了last就立即跳出不再执行其后面的语句，故last后面的return语句根本没有被执行才导致出现了bug
                        }
                    }
                }
            }
            $i++;
        }
    }
    # my $src_type = $par{'src_type'};
    # if( $src_type ne 'no_type' && $src_type ne 'ip_addr_type' && $src_type ne 'addr_member_type' ){
    #     $mesg = "对不起，无法识别源类型！";
    #     return($status, $mesg);
    # }

    my $dst_type = $par{'dst_type'};
    if( $dst_type ne 'no_type' && $dst_type ne 'isp_addr_type' && $dst_type ne 'ip_addr_type' ){
        $mesg = "对不起，无法识别目标类型！";
        return($status, $mesg);
    }
    # if( $par{'src_type'} eq "ip_addr_type"){
    #     my $src_ip = $par{'routing_src_ip_addr_textarea'};
    #     $src_ip =~ s/\n/\|/g;
    #     $src_ip =~ s/\r//g;
    #     my @src_ip = split( '\|', $src_ip );
    #     foreach( @src_ip ){
    #         if( !&validipormask( $_ ) ){
    #             $mesg = "对不起，源ip地址不合法";
    #             return($status, $mesg);
    #         }
    #     }
    # }
    
    # if( $par{'dst_type'} eq "ip_addr_type"){
    #     my $dst_ip = $par{'routing_dst_ip_addr_textarea'};
    #     $dst_ip =~ s/\n/\|/g;
    #     $dst_ip =~ s/\r//g;
    #     my @dst_ip = split( '\|', $dst_ip );
    #     foreach( @dst_ip ){
    #         if( !&validipormask( $_ ) ){
    #             $mesg = "对不起，目的ip地址不合法";
    #             return($status, $mesg);
    #         }
    #     }
    # }
    
    $status = 0; $mesg = "检查通过";
    return($status, $mesg);

}
sub save_data() {
    my $item_id = $par{'id'};
    my @lines;
    my $record ="";
    my ( $status, $mesg ) = (-1,"未保存");
    ( $status, $mesg ) = &handle_before_save_data();
    
    if($status != 0){
        &send_status( $status, 0, $mesg );
        return;
    }

    $record = &get_config_record( \%par ); # 
    my @cur_lines = ();
    if( $item_id eq '' ) {   # 此处就是‘添加’操作
        if( $par{'position'} eq "first_line" ){
            &read_config_lines( $config_file_path, \@cur_lines );
            if( @cur_lines == 0){
                ( $status, $mesg ) = &append_one_record( $config_file_path, $record );
            }
            else{
                ( $status, $mesg ) = &insert_one_record( $config_file_path, 0, $record );
            }
        }elsif( $par{'position'} eq "last_line" ){  # 
            ( $status, $mesg ) = &append_one_record( $config_file_path, $record );
        }else{
            ( $status, $mesg ) = &insert_one_record( $config_file_path, $par{'position'}, $record );
        }
        if( $status == -1 ){
            $mesg = "保存失败";  &send_status( $status, 0, $mesg );  return;
        }
        # $log_oper = "add";
    } else {  # 
        my ( $status, $mesg, $total_num ) = &read_config_lines( $config_file_path, \@lines);   
        my $last_line = $total_num -1;   # 
        if( $par{'position'} ne "first_line" && $par{'position'} ne "last_line" ){

            ( $status, $mesg ) = &insert_one_record( $config_file_path, $par{'position'}, $record );

            if( $par{'position'} > $item_id ){  # 
                ( $status, $mesg ) = &delete_one_record( $config_file_path, $item_id );
            }elsif( $par{'position'} <= $item_id ){  # 
                ( $status, $mesg ) = &delete_one_record( $config_file_path, $item_id+1 );  # 
            }
        }
        elsif( $par{'position'} eq "first_line" ){
            ( $status, $mesg ) = &insert_one_record( $config_file_path, 0, $record );
            ( $status, $mesg ) = &delete_one_record( $config_file_path, $item_id+1 );   # 

        }elsif( $par{'position'} eq "last_line" ){
            ( $status, $mesg ) = &append_one_record( $config_file_path, $record );
            ( $status, $mesg ) = &delete_one_record( $config_file_path, $item_id );   # 

        }
        if( $status == -1 ){
            $mesg = "保存失败";  &send_status( $status, 0, $mesg );  return;
        }
        # $log_oper = "edit";
    }

    if( $status == 0 ) {
        # $mesg = "保存成功";  #
        &create_need_reload_file();
    }
    &send_status( $status, 1, "" );
}

sub delete_data() {
    my $last_line = $par{'total_num'} -1;    # 
    my ( $status, $reload, $mesg ) = ( -1, 0, "未删除" );
    if( $par{'id'} eq "") { $mesg = "未检测到可删除项"; &send_status( $status, 0, $mesg ); return; }
    my @ids = split("&",$par{'id'});
    foreach my $id (@ids) {
        
    }
    ( $status, $mesg ) = &delete_several_records( $config_file_path, $par{'id'} );
    if( $status !=0 ){ $mesg = "删除选中的行失败"; &send_status( $status, 0, $mesg ); return; }
    
    # $mesg = "已成功删除";
    if( $status == 0 ){  &create_need_reload_file();  }
    # $log_oper = 'del';
    $reload = 1;
    &send_status( $status, $reload, "" );

}

sub show_page() {
    &openpage(_('智能路由'), 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    
    &closebigbox();
    &display_main_body();
    &closepage();
}
sub display_main_body() {
    printf<<EOF
    <div id="smart_routing_mesg_box" style="width: 96%;margin: 20px auto;"></div>
    <div id="smart_routing_add_panel"      style="width: 96%;margin: 20px auto;"></div>
    <div id="smart_routing_list_panel"      style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
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

    return $search;
}

sub get_config_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'enabled'}      = $temp[0];
    $config{'routing_name'}         = $temp[1];
    $config{'routing_src'}  = $temp[2];
    $config{'routing_dst'}  = $temp[3];
    $config{'protocal'}     = $temp[4];
    $config{'links'}        = $temp[5];
    $config{'time'}         = $temp[6];
    $config{'scheduler'}    = $temp[7];
    # $config{'last'}         = $temp[8];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;   # 
    my @record_items = ();  # 
        
    if ( $hash_ref->{'enabled'} eq "" ) {
        push( @record_items, "off" );
    }else {
        push( @record_items, $hash_ref->{'enabled'} );
    }
    push( @record_items, $hash_ref->{'routing_name'} );
# 源字段值的存储
    push( @record_items, "" );   # 源字段先暂时存储为空值
    # if ( $par{'src_type'} eq "no_type" ) {
    #     push( @record_items, "" );

    # }elsif ( $par{'src_type'} eq "ip_addr_type" ) {
    # my $src_ip = $par{'routing_src_ip_addr_textarea'};
    # my @src_ip = split('\n', $src_ip);
    # my $str = join("|",@src_ip);
    # push( @record_items, $str );
    #     push( @record_items, "IP:".$par{'routing_src_ip_addr_textarea'} );   # 

    # }elsif ( $par{'src_type'} eq "addr_member_type" ) {

    #     push( @record_items, "IP_NODE:".$par{'SELECTED_IP_NODE'}."|"."IP_GROUP:".$par{'SELECTED_IP_GROUP'} );   # 
    # }
# 目标字段值的存储
    if ( $par{'dst_type'} eq "no_type" ) {
        push( @record_items, "" );

    }elsif ( $par{'dst_type'} eq "isp_addr_type" ) {

        push( @record_items, "ISP:".$par{'isp_name_select_options'} );   # 

    }elsif ( $par{'dst_type'} eq "ip_addr_type" ) {
        my $dst_ip = $par{'routing_dst_ip_addr_textarea'};
        # my @dst_ip = split('\n', $dst_ip);
        # my $str = join("|",@dst_ip);
        # my $str = join("|",@dst_ip);
        $dst_ip =~ s/\n/\|/g;
        $dst_ip =~ s/\r//g;
        push( @record_items, "IP:".$dst_ip );
        # push( @record_items, "IP:".$par{'routing_dst_ip_addr_textarea'} );   # 
    }
    # push( @record_items, $hash_ref->{'protocal'} );
    # 协议字段先暂时一律存储为TCP
    push( @record_items, "TCP" );

    push( @record_items, $hash_ref->{'SELECTED_UPLINKS'} );
    # push( @record_items, $hash_ref->{'time'} );
    push( @record_items, "" );   # 时间字段先暂时一律存储为空值
    if( $hash_ref->{'scheduler'} eq "none"){
        push( @record_items, "" );
    }else{
        push( @record_items, $hash_ref->{'scheduler'} );
    }
    # push( @record_items, $hash_ref->{'scheduler'} );

    return join ",", @record_items;
}

sub get_query_hash($){
    my $query_ref = shift;
    my $query_string = $ENV{'QUERY_STRING'};

    if ( $query_string eq '' ) {
        return;
    }

    my @key_values = split( "&", $query_string );
    foreach my $key_value ( @key_values ) {
        my ( $key, $value ) = split( "=", $key_value );
        $query_ref->{ $key } = $value;
        #===对获取的值进行一些处理===#
        $query_ref->{ $key } =~ s/\r//g;
        $query_ref->{ $key } =~ s/\n//g;
        chomp( $query_ref->{ $key } );
    }

    return;
}
sub send_status($$$) {
    my ($status, $reload, $mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'reload'} = $reload;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
    # &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
}