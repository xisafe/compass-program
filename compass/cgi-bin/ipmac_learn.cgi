#!/usr/bin/perl
#==============================================================================#
#
# 描述: ipmac绑定【学习】页面
#
# 作者: 辛志薇
# 公司: capsheaf
# 历史:
#   2015-1-5 创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';    # 如果/cgi-bin目录下有list_panel_opt.pl那么你引用时就不用加目录前缀，直接写文件名好了

#=====初始化全局变量到init_data()中去初始化=====================================#
my $ipmac_dynamic_file;
my $ipmac_bind_file_path;
my $arp_table_file_path;
my $ipmac_table_file_path;
my $snmp_settings_file_path;
my $running_tag_file_path;

my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变

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
    $ipmac_dynamic_file = '/var/efw/ip-mac/3L-ip-mac/ipmac_dynamic';
    $ipmac_bind_file_path = "/var/efw/ip-mac/3L-ip-mac/ipmac_bind";
    $arp_table_file_path   = '/var/efw/ip-mac/arp_table';
    $ipmac_table_file_path = '/var/efw/ip-mac/ipmac_table';
    $snmp_settings_file_path = '/var/efw/ip-mac/3L-ip-mac/settings';
    $running_tag_file_path = '/var/efw/ip-mac/running_tag_file';
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/waiting.js"></script>
                    <script language="JavaScript" src="/include/ipmac_learn.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#
}

sub make_file(){
    if(! -e $ipmac_dynamic_file){
        system("touch $ipmac_dynamic_file");
    }
    if(! -e $ipmac_bind_file_path){
        system("touch $ipmac_bind_file_path");
    }
    if(! -e $arp_table_file_path){
        system("touch $arp_table_file_path");
    }
}

sub do_action() {
    my $action = $par{'ACTION'};           # 这个是post方法发送过来的 ACTION 参数值
    my $query_action = $query{'ACTION'};   # 这个是get方法发送过来的 ACTION 参数值
    my $panel_name = $par{'panel_name'};

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if( $action eq 'load_init_data'){
        &load_init_data();
    }
    elsif( $action eq 'save_method' ){
        &save_method();
    }
    elsif ( $action eq 'START_LEARNING' ) {    # 这个动作即【开始学习】
        &start_learning();
    }
    elsif( $action eq 'check_running' ){
        &check_running();
    }
    elsif( $action eq 'load_data'){
        &view_the_results();
    }
    elsif( $action eq 'SYNCHRONIZE'){      # 这个动作即【同步ipmac条目到ip/mac绑定设置页面】
        &synchronize_learned_data();
    }
    else {
        &show_page();
    }
}

sub load_init_data(){
    my %read_hash = ();
    my %ret_data;
    my $status,$bind;
    if(-e $snmp_settings_file_path){
        &readhash( $snmp_settings_file_path, \%read_hash );
    }
    $status = $read_hash{'LAYER'};
    if($status eq 'none'){
        %ret_data->{'status'} = "none";
    }
    elsif($status eq 'three'){
        %ret_data->{'status'} = "three";
    }
    elsif($status eq 'two'){
        %ret_data->{'status'} = "two";
    }
    $bind = $read_hash{'BIND'};
    if( $bind eq "enable" ){
        %ret_data->{'bind'} = "on";
    }else{
        %ret_data->{'bind'} = "off";
    }
    %ret_data->{'running'} = &is_learn_running();
    my $ret = $json->encode(\%ret_data);
    print $ret;
}
=p
=cut

sub save_method(){
    my $method = $par{'METHOD'};
    my %read_hash = ();
    &readhash( $snmp_settings_file_path, \%read_hash );
    my %save_hash = %read_hash;
    $save_hash{'LAYER'} = $method;
    &writehash( $snmp_settings_file_path, \%save_hash );
}


sub check_running(){
    my %response;
    $response{'running'} = &is_learn_running();
    my $result = $json->encode(\%response);
    print $result;
}

sub is_learn_running() {
    my $result = -1;
    if( -e $running_tag_file_path ){
        $result = 1;
    }
    return $result;
}


sub start_learning(){
    my %read_hash = ();
    if(-e $snmp_settings_file_path){
        &readhash( $snmp_settings_file_path, \%read_hash );
    }
    my ( $status, $mesg ) = (-1, "学习开启失败");

    # if ( &is_learn_running() == 1 ) {
    #     &send_status( -1, -1, "学习正在进行中，请稍后操作" );
    #     return;
    # }
    my %save_hash = %read_hash;
    if( $par{'LEARN_METHOD'} eq 'by_switchboard' ){
        $save_hash{'LAYER'} = 'three';
        &writehash( $snmp_settings_file_path, \%save_hash );
        system("/usr/local/bin/ipmac_learn");
        if( $? == 0 ){  $status = 0;  $mesg = "三层交换机学习开启成功";  }
    }
    elsif( $par{'LEARN_METHOD'} eq 'by_baowen' ){
        $save_hash{'LAYER'} = 'two';
        &writehash( $snmp_settings_file_path, \%save_hash );
        system("/usr/local/bin/ipmac_learn");
        if( $? == 0 ){  $status = 0;  $mesg = "报文学习开启成功";  }
    }
    my $running = 1;  # my $running = &is_learn_running();
    &send_status( $status, $running, $mesg );
}



sub view_the_results(){
    my ($status, $reload, $mesg) = (-1, 0, "");
    my $total_num = 0; my @lines;
    my @content_array; my %ret_data;
    my $layer_flag;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;

    if( ( $par{'LEARN_METHOD'} eq 'by_switchboard')  ){
        my @temp_arr = ();
        &read_config_lines( $ipmac_dynamic_file, \@temp_arr);
        $total_num += @temp_arr;
        $layer_flag = "three";
        push( @lines, @temp_arr );
    }
    #bug修复 原来下面用的是elsif，导致判断条件不成立故才导致了报文学习的配置文件内容没有读取并加载而交换机配置文件的内容读取和加载是成功的
    #bug修复，从elsif改成了if
    elsif( ( $par{'LEARN_METHOD'} eq 'by_baowen')  ){
        # if( $par{'ACTION'} eq 'load_data')       {  `echo 111 >/tmp/haha`;  测试成功 }
        # if( $par{'paging_action'} eq "refresh")  {  `echo 222 >>/tmp/haha`; 测试成功 }
        my @temp_arr = ();
        &read_config_lines( $arp_table_file_path, \@temp_arr);
        # $total_num = @temp_arr;
        $total_num += @temp_arr;
        $layer_flag = "two";
        for( my $i = 0; $i < @temp_arr; $i++ ) {
            my @arr = split(/,/, $temp_arr[$i]);
            # $arr[1] = "$arr[1]" . ",2";  # ",来自报文学习"  2就代表来自报文学习
            # $arr[2] = "$arr[2]" . ",2";
            $temp_arr[$i] = join ",", @arr;
            push( @lines, $temp_arr[$i] );
        }
    }

    for( my $i = 0; $i < @lines; $i++ ) {
        my $id = $from_num + $i;
        my %hash = ();

        if( !$LOAD_ONE_PAGE ) {    $id = $i;   }

        %hash = &get_config_hash( $lines[$i] );
        $hash{'id'} = $id;
        push( @content_array, \%hash );
    }

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'layer_flag'} = $layer_flag;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}



sub synchronize_learned_data(){
    my $layer_flag = $par{'layer_flag'};
    my @ids = split('\|', $par{'id'});
    
    my $ids = join ",", @ids;
    my @array = split('\n', $par{'detail_data'} );

    my $record;
    my ( $status, $mesg ) = (-1, "");
    my @arr;
    my $source;
    my @file_holder;   my $flag;

    if ( &is_learn_running() == 1 ) {
        &send_status( -1, 1, "学习正在进行中，请稍后操作" );
        return;
    }
    open( FILEBIND, ">>$ipmac_bind_file_path" );
    open( FILETABLE, ">>$ipmac_table_file_path" );
    foreach my $item( @array ){
        @arr = split(/,/, $item );    # 因为item里有4个字段，'on,ip_addr,mac_addr,source'所以arr数组里就有4个
        $source = $arr[3];
        $record = $item;

        $flag = 0;
        if( $layer_flag =~ "three" ){    # 以后得改成 匹配ip正则式即可
            # 下面开始查重
            open(FILE_HOLDER, "<$ipmac_bind_file_path");
            @file_holder = <FILE_HOLDER>;
            close(FILE_HOLDER);
            foreach( @file_holder ){
                my @array = split( /,/, $_ );
                $_ = "$array[1],$array[2],$array[3]";
                if( $_=~ /$arr[1],$arr[2],$source/ )  {  $flag = 1;  }
            }
            # 查重结束
            if($flag == 0){
                print FILEBIND "$record\n";
            }else{
                # $mesg = "$mesg"."\n来自交换机学习的$arr[1],$arr[2],$source发生重复，已被过滤掉\n";
            }
        }
        else{
            # 下面开始查重
            open(FILE_HOLDER, "<$ipmac_table_file_path");
            @file_holder = <FILE_HOLDER>;
            close(FILE_HOLDER);
            foreach( @file_holder ){
                my @array = split( /,/, $_ );
                $_ = "$array[1],$array[2]";
                if( $_=~ /$arr[1],$arr[2]/ )  {  $flag = 1;  }  #  /$arr[0],$arr[1],$source/
            }
            # 查重结束
            if($flag == 0){
                # 其实这时$source的值就已经是'来自报文学习'了,因为$source的值就只有两种，一种是交换机ip即192.168这样的值，一种即等于'来自报文学习'
                print FILETABLE "$record\n";
            }else{
                # $mesg = "$mesg"."\n来自报文学习的$arr[1],$arr[2]发生重复，已被过滤掉\n";
            }
        }
    }
    close FILEBIND;
    close FILETABLE;
    system("/usr/local/bin/restartipmac");
    &send_status( 0, 0, "同步已完成".$mesg );
}
sub show_page() {
    &openpage(_('IP/MAC绑定学习'), 1, $extraheader);
    # &openbigbox($errormessage, $warnmessage, $notemessage);
    # &closebigbox();
    &display_test_div();
    &closepage();
}

sub display_test_div() {
    printf<<EOF
    <div id="mesg_box_id" style="width: 96%;margin: 20px auto;"></div>
    <div id="learn_method_panel_config" style="width: 96%;margin: 20px auto;"></div>
    <div id="learn_result_list_panel_config" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub get_config_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'ip_addr'}     = $temp[1];    # $temp[0];
    $config{'mac_addr'}    = $temp[2];    # $temp[1];
    $config{'source'}      = $temp[3];    # $temp[2];
    #============自定义字段组装-END===========================#
    return %config;
}


sub send_status($$$) {
    my ($status, $running, $mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'running'} = $running;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}
