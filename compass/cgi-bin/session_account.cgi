#!/usr/bin/perl

use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $conf_file_break;    #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $conf_file_detail;   #详细信息存放的文件
my $total_file;
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my %hash_total;
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $LOAD_ONE_PAGE = 0;
my $CMD;
my $cmd_restart;
my $json = new JSON::XS;
my $CUR_PAGE = "会话统计" ;      #当前页面名称，用于记录日志
my $log_oper;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/sessionmanager/statistic';               #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/lib".$custom_dir;                    #规则所存放的文件夹
    $conf_file          = $conf_dir.'/choicefile';                   #规则所存放的文件
    $conf_file_break    = '/var/efw/sessionmanager/block/config';    #规则所存放的文件
    $conf_file_detail   = $conf_dir.'/detailfile';
    $total_file         = $conf_dir.'/totalfile';
    $CMD                = "sudo /usr/local/bin/countconn ";
    $CMD                = "sudo /usr/local/bin/countconn2.py ";
    $cmd_restart        = "sudo /usr/local/bin/session_block.py";
    $need_reload_tag    = $conf_dir.'/need_reload_account';

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/session_account_init.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#

    &make_file();#检查要存放规则的文件夹和文件是否存在
    #前台展示之前对数据进行排序
    # my @lines_conf;
    # &read_config_lines( $conf_file, \@lines_conf );
    # %sort_hash;
    # for ( my $i = 0; $i < @lines_conf; $i++ ) {
        # my @temp = split( " ", $lines_conf[$i]);
        # $sort_hash{$temp[0]} = $temp[1];
    # }
}

sub do_action() {
    my $action = $par{'ACTION'};
    if( !$action ) {
        $action = $query{'ACTION'};
    }

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==下载数据==#
        &load_data();
    } 
    elsif ($action eq 'save_data') {
        &save_data();
        $log_oper = "edit";
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
        $log_oper = "apply";
    }
    elsif($action eq 'load_data_linkage'){
        &load_data_linkage();
    } 
    elsif($action eq 'generate_data_detail'){
        &generate_data_detail();
    } 
    elsif ($action eq 'delete_data') {
        #==下载数据==#
        &delete_data();
    }
    elsif ($action eq 'enable_data') {
        #==下载数据==#
        &toggle_enable( $par{'id'}, "on" );
    }
    elsif ($action eq 'disable_data') {
        #==下载数据==#
        &toggle_enable( $par{'id'}, "off" );
    }
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
    &write_log($CUR_PAGE,$log_oper,0,$rule_or_config);
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_test_div();
    &closepage();
}

sub display_test_div() {
    printf<<EOF
    <div id="message_box_account" style="width: 96%;margin: 20px auto;"></div>
    
    <div style="margin:0 auto;width:96%;margin-top:20px">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="table-footer">
    <td colspan="2" style="text-align:left;font-weight:bold">
      <span>实时连接状态</span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">当前实时连接总数</td>
    <td><span id="total"></span></td>
    </tr>
    <tr class="odd">
    <td  class="add-div-type">TCP实时连接总数</td>
    <td><span id="tcp"></span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">UDP实时连接总数</td>
    <td><span id="udp"></span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">ICMP实时连接总数</td>
    <td><span id="icmp"></span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">其他</td>
    <td><span id="other"></span></td>
    </tr>
    
    <tr class="table-footer">
    <td colspan="2">
    </td>
    </tr>
    </table>
    </div>
    
    <div id="panel_block_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_detail" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_account" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub get_ip_with_mask($){
	my $ip = shift;
	my @ips = split('\/',$ip);
	if ($ip ne '' && @ips == 1){
		return $ip.'/32';
	}
	if (!ip){
		return '0.0.0.0';
	}
	return $ip;
}

sub load_data(){
    my %ret_data;
    my @content_array,@panel_header;
    my $panel_name = $par{'panel_name'};
    my @query_parameter = split('\/',$par{'query_parameter'});
    if($panel_name eq 'list_panel'){
        @panel_header = &config_list_panel_header();
        if($par{'style_account'} eq 's_ip'){
            my $s_ip = $par{'query_parameter'};
            if($s_ip ne '' && @query_parameter == 1){
                $s_ip .= '/32';
            }
            if(!$s_ip){
                $s_ip = "0.0.0.0";
            }
            system($CMD.'-C -p all -s '.$s_ip.' -f '.$conf_file);
        }elsif($par{'style_account'} eq 'd_ip'){
            my $d_ip = $par{'query_parameter'};
            if($d_ip ne '' && @query_parameter == 1){
                $d_ip .= '/32';
            }
            if(!$d_ip){
                $d_ip = "0.0.0.0";
            }
            system($CMD.'-C -p all -d '.$d_ip.' -f '.$conf_file);
        }elsif($par{'style_account'} eq 's_port'){
            my $s_port = $par{'query_parameter'};
            if(!$s_port){
                $s_port = "0";
            }
            system($CMD.'-C -p all -r '.$s_port.' -f '.$conf_file);
        }
    }
    my ( $status, $error_mesg, $total_num ) = &get_content_array( \@content_array );
    if($? != 0){
        $error_mesg .= ",命令执行失败$?";
    }
    
    my $reload = 0;
    # if(-e $need_reload_tag){
    #     $reload = 1;
    # }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'reload'} = $reload;
    %ret_data->{'error_mesg'} = $error_mesg;
    # %ret_data->{'page_size'} = $PAGE_SIZE;
    if($panel_name eq 'list_panel'){
        %ret_data->{'panel_header'} = \@panel_header;
    }
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub load_data_linkage(){
    system($CMD."-C -f ".$total_file);
    my @lines = read_conf_file($total_file);
    %hash_total = (
                    "total" => (split(" ",$lines[0]))[1],
                    "tcp"   => (split(" ",$lines[1]))[1],
                    "udp"   => (split(" ",$lines[2]))[1],
                    "icmp"  => (split(" ",$lines[3]))[1],
                    "other" => (split(" ",$lines[4]))[1],
                   );
    my $result = $json->encode(\%hash_total);
    print $result;
}

sub generate_data_detail(){

    if($par{'count_type'} eq 's_ip'){
    	$param = &get_ip_with_mask($par{'param'});
        system($CMD.'-L -s '.$param.' -f '.$conf_file_detail);
    }elsif($par{'count_type'} eq 'd_ip'){
    	$param = &get_ip_with_mask($par{'param'});
        system($CMD.'-L -d '.$param.' -f '.$conf_file_detail);
    }else{
	    $param = $par{'param'};
        system($CMD.'-L -r '.$param.' -f '.$conf_file_detail);
    }
    &load_data();
}

sub delete_data() {
    my ( $status, $mesg ) = &delete_one_record( $conf_file, $par{'id'});

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'msg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_content_array($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );

    my $from_num = ( $current_page - 1 ) * $page_size;
    my $to_num = $current_page * $page_size;
    my $status, $error_mesg;

    my @lines = ();
    if($par{'panel_name'} eq 'list_panel'){
        ( $status, $error_mesg ) = &read_config_lines( $conf_file, \@lines );
    }else{
        ( $status, $error_mesg ) = &read_config_lines( $conf_file_detail, \@lines );
    }
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
    
    #前台展示之前对数据进行排序
    my @lines_conf;
    &read_config_lines( $conf_file, \@lines_conf );
    %sort_hash;
    for ( my $i = 0; $i < @lines_conf; $i++ ) {
        my @temp = split( " ", $lines_conf[$i]);
        $sort_hash{$temp[0]} = $temp[1];
    }
    
    my $ret_total = 0;
    if($par{'panel_name'} eq 'list_panel'){
        foreach my $key ( sort { $sort_hash{$b} <=> $sort_hash{$a} } keys %sort_hash ) {
            
            my %config = &get_config_hash( "$key $sort_hash{$key}" );
            if( $config{'valid'}) {
                $config{'id'} = $config{'ip_or_port'};
                if ( ! ( validip( $config{'ip_or_port'} ) || validport( $config{'ip_or_port'} ) ) ) {
                    next;
                }
                # if( $i % 5 == 0 ) {
                #     $config{'uneditable'} = 1;
                #     $config{'undeletable'} = 1;
                # }
                push( @$content_array_ref, \%config );
                $ret_total++;
            }
        }
    }else{
        for ( my $i = $from_num; $i < $total_num; $i++ ) {
            my %config = &get_config_hash( $lines[$i] );
            if( $config{'valid'} ) {
                $config{'id'} = $i;
                # if( $i % 5 == 0 ) {
                #     $config{'uneditable'} = 1;
                #     $config{'undeletable'} = 1;
                # }
                push( @$content_array_ref, \%config );
                $ret_total++;
            }
        }
    }
    
    return ( $status, $error_mesg, $ret_total );
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
    my @temp = split(" ", $line_content);
    if($par{'panel_name'} eq 'list_panel'){
        if($temp[0] ne '127.0.0.1' && $temp[0] ne '0.0.0.0' && $temp[0] ne '0000:0000:0000:'){
            $config{'ip_or_port'}          = $temp[0];
            $config{'session_num'}   = $temp[1];
        }else{
            $config{'valid'} = 0;
        }
        # $config{'ip_or_port'}          = $temp[0];
        # $config{'session_num'}   = $temp[1];
        
    }else{
        $config{'protocol'}   = $temp[0];
        $config{'s_session_sender'}   = $temp[1];
        $config{'d_session_sender'}   = $temp[2];
        $config{'s_session_reciver'}   = $temp[3];
        $config{'d_session_reciver'}   = $temp[4];
        #$config{'state'}   = $temp[5];
        $config{'left_time'}   = $temp[5];
    }

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'ip_or_port'} );
    push( @record_items, $hash_ref->{'session_num'} );
    return join " ", @record_items;
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
    my ($status, $reload, $mesg) = @_;
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

sub config_list_panel_header() {
    #====第三步，配置表头=============#
    my %functions = (
        "onclick" => "toggle_check(this);",
    );
    my %hash = (
        "enable"    => 0,           #用户控制表头是否显示
        "type"      => "checkbox",  #type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title"     => "",          #不同类型的，title需要的情况不同，一般text类型需要title
        "name"      => "checkbox",  #用户装载数据之用
        "id"        => "",          #元素的id号
        "class"     => "",          #元素的class
        "td_class"  => "",          #这一列td的class，主要用于控制列和列内元素
        "width"     => "5%",        #所有表头加起来应该等于100%,以精确控制你想要的宽度
        # "functions" => \%functions, #一般只有checkbox才会有这个字段
    );
    push( @panel_header, \%hash );

    if( $par{'style_account'} eq "s_ip" ) {
        my %hash = (
            "enable"    => 1,
            "type"      => "text",
            "title"     => "源IP地址",
            "td_class"  => "align-center",
            "name"      => "ip_or_port",
            "width"     => "30%",
        );
        push( @panel_header, \%hash );
    } elsif ( $par{'style_account'} eq "d_ip" ) {
        my %hash = (
            "enable"    => 1,
            "type"      => "text",
            "title"     => "目的IP地址",
            "td_class"  => "align-center",
            "name"      => "ip_or_port",
            "width"     => "30%",
        );
        push( @panel_header, \%hash );
    } elsif ( $par{'style_account'} eq "s_port" ) {
        my %hash = (
            "enable"    => 1,
            "type"      => "text",
            "title"     => "服务端口",
            "td_class"  => "align-center",
            "name"      => "ip_or_port",
            "width"     => "30%",
        );
        push( @panel_header, \%hash );
    }
    
    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "会话总数",        #一般action列都是这个标题
        "name"      => "session_num",
        "td_class"  => "align-center",
        "class"     => "",
        "width"     => "30%",
    );
    push( @panel_header, \%hash );
    
    my %hash = (
        "enable"    => 1,
        "type"      => "action",
        "title"     => "操作",        #一般action列都是这个标题
        "name"      => "action",
        "class"     => "",
        "td_class"  => "align-center",
        "width"     => "30%",
    );
    push( @panel_header, \%hash );

    return @panel_header;
}
#添加临时阻断
sub save_data() {
    my $reload = 0;
    my $record = &get_config_record_breck( \%par );
    my $item_id = $par{'id'};

    my ( $status, $mesg ) = ( -1, "未保存" );
    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $conf_file_break, $record );
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file_break, $item_id, $record );
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "添加成功";
    }

    &send_status( $status, $reload, $mesg );
}

sub get_config_record_breck($) {
    my $hash_ref = shift;
    my @record_items = ();
    my $protocol = $hash_ref->{'protocol'};
    push( @record_items, $protocol );
    push( @record_items, $hash_ref->{'source'} );
    if($protocol eq 'tcp' || $protocol eq 'udp' || $protocol eq 'all'){
        push( @record_items, $hash_ref->{'s_port'} );
    }else{
        push( @record_items, $hash_ref->{'type'} );
    }
    push( @record_items, $hash_ref->{'dest'} );
    if($protocol eq 'tcp' || $protocol eq 'udp' || $protocol eq 'all'){
        push( @record_items, $hash_ref->{'d_port'} );
    }else{
        push( @record_items, $hash_ref->{'code'} );
    }
    push( @record_items, $hash_ref->{'left_time'} );
    push( @record_items, "0" );
    return join ",", @record_items;
}
sub apply_data() {
    system($cmd_restart);
    &clear_need_reload_tag();
    &send_status( 0, 0, "应用成功" );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
