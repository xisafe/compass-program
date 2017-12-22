#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/12/03
use Encode;

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

my $CUR_PAGE = "防护策略" ;  #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/ddosprotect';                            #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;                    #规则所存放的文件夹
    $conf_file          = $conf_dir.'/policy_template';              #策略模板所存放的文件
    $conf_file_rule     = $conf_dir.'/rule_config';                  #规则所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_ddos';    #启用信息所存放的文件
    $cmd                = "/usr/local/bin/restartddosprotect";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/policy_template_ddos_init.js"></script>';
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
    elsif ($action eq 'load_data' && $panel_name eq 'scan_panel') {
        #==加载数据==#
        &load_data_scan();
    } 
    elsif ($action eq 'load_data' && $panel_name eq 'transport_panel') {
        #==加载数据==#
        &load_data_transport();
    } 
    elsif ($action eq 'load_data' && $panel_name eq 'apply_panel') {
        #==加载数据==#
        &load_data_apply();
    } 
    elsif ($action eq 'load_data' && $panel_name eq 'strange_panel') {
        #==加载数据==#
        &load_data_strange();
    } 
    elsif ($action eq 'load_data' && $panel_name eq 'ip_panel') {
        #==加载数据==#
        &load_data_ip();
    } 
    elsif ($action eq 'load_data' && $panel_name eq 'tcp_panel') {
        #==加载数据==#
        &load_data_tcp();
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
    <div id="panel_tmp_scan" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_tmp_transport" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_tmp_apply" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_tmp_strange" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_tmp_ip" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_tmp_tcp" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_tmp_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}


sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};
    
    my @lines;
    &read_config_lines($conf_file,\@lines);

    my ( $status, $mesg ) = ( -1, "未保存" );
    if( $item_id eq '' ) {
        foreach (@lines){
            if($par{'name'} eq (split(",",$_))[0]){
                ( $status, $mesg ) = ( -2, $par{'name'}."已占用" );
            }
        }
        if($status != -2){
            ( $status, $mesg ) = &append_one_record( $conf_file, $record );
            $log_oper = "add";
        }
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
         $log_oper = "edit";
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
    $log_oper = 'del';
    my @lines = ();
    &read_config_lines($conf_file,\@lines);
    my @ids = split("\&",$par{'id'});
    my @ids_rule_del = ();
    foreach(@ids){
        my @data_line = split(",",$lines[$_]);
        my @sub_ids_rule = &get_ruleid_for_policy($data_line[0]);
        push(@ids_rule_del,@sub_ids_rule);
    }
    &delete_several_records( $conf_file_rule,join("\&",@ids_rule_del) );
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});
    
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
     &write_log($CUR_PAGE,$log_oper,$status,$rule_or_congfig);
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
    $config{'name'}   = $temp[0];
    $config{'description'}   = $temp[1];
    $config{'enable_ipaddr'}   = $temp[2];
    $config{'max_val_ipaddr'}   = $temp[3];
    $config{'enable_port'}   = $temp[4];
    $config{'max_val_port'}   = $temp[5];
    $config{'enable_syn'}   = $temp[6];
    $config{'num_syn_source'}   = $temp[7];
    $config{'num_syn_dest'}   = $temp[8];
    $config{'enable_ack'}   = $temp[9];
    $config{'num_ack_source'}   = $temp[10];
    $config{'num_ack_dest'}   = $temp[11];
    $config{'enable_udp'}   = $temp[12];
    $config{'num_udp_source'}   = $temp[13];
    $config{'num_udp_dest'}   = $temp[14];
    $config{'enable_icmp'}   = $temp[15];
    $config{'num_icmp_source'}   = $temp[16];
    $config{'num_icmp_dest'}   = $temp[17];
    $config{'enable_http'}   = $temp[18];
    $config{'num_http_source'}   = $temp[19];
    $config{'num_http_dest'}   = $temp[20];
    $config{'enable_dns'}   = $temp[21];
    $config{'num_dns_source'}   = $temp[22];
    $config{'num_dns_dest'}   = $temp[23];
    $config{'dns_type'}   = $temp[24];
    $config{'dns_query_style'}   = $temp[25];
    $config{'enable_land'}   = $temp[26];
    $config{'enable_smurf'}   = $temp[27];
    $config{'enable_winnuke'}   = $temp[28];
    $config{'enable_teardrop'}   = $temp[29];
    $config{'enable_targa3'}   = $temp[30];
    $config{'enable_fraggle'}   = $temp[31];
    $config{'enable_largest_icmp'}   = $temp[32];
    $config{'enable_ip_record'}   = $temp[33];
    $config{'enable_ip_time'}   = $temp[34];
    $config{'enable_ip_district'}   = $temp[35];
    $config{'enable_ip_strict'}   = $temp[36];
    $config{'enable_ip_safe'}   = $temp[37];
    $config{'enable_ip_unlaw'}   = $temp[38];
    $config{'enable_tcp_head0'}   = $temp[39];
    $config{'enable_tcp_head1'}   = $temp[40];
    $config{'enable_syn_fin'}   = $temp[41];
    $config{'enable_fin'}   = $temp[42];
    
    my @rules_for_policy = &get_ruleid_for_policy($temp[0]);
    $config{'rules_for_policy'}   = join("\&",@rules_for_policy);
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
    push( @record_items, $hash_ref->{'enable_ipaddr'} );
    push( @record_items, $hash_ref->{'max_val_ipaddr'} );
    push( @record_items, $hash_ref->{'enable_port'} );
    push( @record_items, $hash_ref->{'max_val_port'} );
    push( @record_items, $hash_ref->{'enable_syn'} );
    push( @record_items, $hash_ref->{'num_syn_source'} );
    push( @record_items, $hash_ref->{'num_syn_dest'} );
    push( @record_items, $hash_ref->{'enable_ack'} );
    push( @record_items, $hash_ref->{'num_ack_source'} );
    push( @record_items, $hash_ref->{'num_ack_dest'} );
    push( @record_items, $hash_ref->{'enable_udp'} );
    push( @record_items, $hash_ref->{'num_udp_source'} );
    push( @record_items, $hash_ref->{'num_udp_dest'} );
    push( @record_items, $hash_ref->{'enable_icmp'} );
    push( @record_items, $hash_ref->{'num_icmp_source'} );
    push( @record_items, $hash_ref->{'num_icmp_dest'} );
    push( @record_items, $hash_ref->{'enable_http'} );
    push( @record_items, $hash_ref->{'num_http_source'} );
    push( @record_items, $hash_ref->{'num_http_dest'} );
    push( @record_items, $hash_ref->{'enable_dns'} );
    push( @record_items, $hash_ref->{'num_dns_source'} );
    push( @record_items, $hash_ref->{'num_dns_dest'} );
    push( @record_items, $hash_ref->{'dns_type'} );
    push( @record_items, $hash_ref->{'dns_query_style'} );
    push( @record_items, $hash_ref->{'enable_land'} );
    push( @record_items, $hash_ref->{'enable_smurf'} );
    push( @record_items, $hash_ref->{'enable_winnuke'} );
    push( @record_items, $hash_ref->{'enable_teardrop'} );
    push( @record_items, $hash_ref->{'enable_targa3'} );
    push( @record_items, $hash_ref->{'enable_fraggle'} );
    push( @record_items, $hash_ref->{'enable_largest_icmp'} );
    push( @record_items, $hash_ref->{'enable_ip_record'} );
    push( @record_items, $hash_ref->{'enable_ip_time'} );
    push( @record_items, $hash_ref->{'enable_ip_district'} );
    push( @record_items, $hash_ref->{'enable_ip_strict'} );
    push( @record_items, $hash_ref->{'enable_ip_safe'} );
    #push( @record_items, $hash_ref->{'enable_ip_unlaw'} );
    push( @record_items, "off" );
    push( @record_items, $hash_ref->{'enable_tcp_head0'} );
    push( @record_items, $hash_ref->{'enable_tcp_head1'} );
    push( @record_items, $hash_ref->{'enable_syn_fin'} );
    push( @record_items, $hash_ref->{'enable_fin'} );
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
    $log_oper = 'apply';
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
#加载扫描防护面板数据
sub load_data_scan() {
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_scan_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}
sub get_scan_detail_data($){
    my $content_array_ref = shift;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);

    # for( my $i = 0; $i < @lines; $i++ ) {
        # my %hash = &get_lib_config_hash( $lines[$i] );
        # if ( !$hash{'valid'} ) {
            # $total_num--;
            # next;
        # }
        # $hash{'id'} = $hash{'name'};
        # &load_data_handler( \%hash );
        # push( @$content_array_ref, \%hash );
    # }
    
    my $line_num = $par{'line_num'};
    my @data_line = split(",",$lines[$line_num]);
    #my ( $status, $mesg, $total_num ) = ( 0, "定义扫描面板", 0 );
    my @list_scan = ("ipaddr_scan","port_scan");
    $total_num = @list_scan;
    for(my $i = 0; $i < @list_scan; $i++){
        my %hash;
        %hash->{'policy_name'} = $list_scan[$i];
        %hash->{'id'} = $i;
        if($lines[$line_num]){
            if($list_scan[$i] eq "ipaddr_scan"){
                %hash->{'config_policy_param'} = $data_line[3];
                %hash->{'enable'} = $data_line[2];
            }else{
                %hash->{'config_policy_param'} = $data_line[5];
                %hash->{'enable'} = $data_line[4];
            }
            
        }
        
        push( @$content_array_ref, \%hash );
    }
    

    return ( $status, $mesg, $total_num );
}

sub load_data_transport() {
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_transport_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_transport_detail_data($){
    my $content_array_ref = shift;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);

    my $line_num = $par{'line_num'};
    my @data_line = split(",",$lines[$line_num]);
    my @list_transport = ("syn","ack","udp","icmp");
    $total_num = @list_transport;
    for(my $i = 0; $i < @list_transport; $i++){
        my %hash;
        %hash->{'policy_name'} = $list_transport[$i];
        %hash->{'id'} = $i;
        if($lines[$line_num]){
            if($list_transport[$i] eq "syn"){
                %hash->{'num_syn_source'} = $data_line[7];
                %hash->{'num_syn_dest'} = $data_line[8];
                %hash->{'enable'} = $data_line[6];
            }elsif($list_transport[$i] eq "ack"){
                %hash->{'num_ack_source'} = $data_line[10];
                %hash->{'num_ack_dest'} = $data_line[11];
                %hash->{'enable'} = $data_line[9];
            }elsif($list_transport[$i] eq "udp"){
                %hash->{'num_udp_source'} = $data_line[13];
                %hash->{'num_udp_dest'} = $data_line[14];
                %hash->{'enable'} = $data_line[12];
            }elsif($list_transport[$i] eq "icmp"){
                %hash->{'num_icmp_source'} = $data_line[16];
                %hash->{'num_icmp_dest'} = $data_line[17];
                %hash->{'enable'} = $data_line[15];
            }
            
        }
        
        push( @$content_array_ref, \%hash );
    }
    

    return ( $status, $mesg, $total_num );
}

sub load_data_apply() {
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_apply_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_apply_detail_data($){
    my $content_array_ref = shift;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);

    my $line_num = $par{'line_num'};
    my @data_line = split(",",$lines[$line_num]);
    my @list_apply = ("http","dns");
    $total_num = @list_apply;
    for(my $i = 0; $i < @list_apply; $i++){
        my %hash;
        %hash->{'policy_name'} = $list_apply[$i];
        %hash->{'id'} = $i;
        if($lines[$line_num]){
            if($list_apply[$i] eq "http"){
                %hash->{'num_http_source'} = $data_line[19];
                %hash->{'num_http_dest'} = $data_line[20];
                %hash->{'enable'} = $data_line[18];
            }elsif($list_apply[$i] eq "dns"){
                %hash->{'num_dns_source'} = $data_line[22];
                %hash->{'num_dns_dest'} = $data_line[23];
                %hash->{'dns_type'} = $data_line[24];
                %hash->{'dns_query_style'} = $data_line[25];
                %hash->{'enable'} = $data_line[21];
            }
            
        }
        
        push( @$content_array_ref, \%hash );
    }
    

    return ( $status, $mesg, $total_num );
}

sub load_data_strange() {
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_strange_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_strange_detail_data($){
    my $content_array_ref = shift;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);

    my $line_num = $par{'line_num'};
    my @data_line = split(",",$lines[$line_num]);
    my @list_strange = ("land","smurf","winnuke","teardrop","targa3","fraggle","largest_icmp");
    $total_num = @list_strange;
    for(my $i = 0; $i < @list_strange; $i++){
        my %hash;
        %hash->{'policy_name'} = $list_strange[$i];
        %hash->{'id'} = $i;
        if($lines[$line_num]){
            if($list_strange[$i] eq "land"){
                %hash->{'enable'} = $data_line[26];
            }elsif($list_strange[$i] eq "smurf"){
                %hash->{'enable'} = $data_line[27];
            }elsif($list_strange[$i] eq "winnuke"){
                %hash->{'enable'} = $data_line[28];
            }elsif($list_strange[$i] eq "teardrop"){
                %hash->{'enable'} = $data_line[29];
            }elsif($list_strange[$i] eq "targa3"){
                %hash->{'enable'} = $data_line[30];
            }elsif($list_strange[$i] eq "fraggle"){
                %hash->{'enable'} = $data_line[31];
            }elsif($list_strange[$i] eq "largest_icmp"){
                %hash->{'enable'} = $data_line[32];
            }
            
        }
        
        push( @$content_array_ref, \%hash );
    }
    

    return ( $status, $mesg, $total_num );
}

sub load_data_ip() {
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_ip_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_ip_detail_data($){
    my $content_array_ref = shift;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);

    my $line_num = $par{'line_num'};
    my @data_line = split(",",$lines[$line_num]);
    my @list_strange = ("ip_record","ip_time","ip_district","ip_strict","ip_safe","ip_unlaw");
    $total_num = @list_strange;
    for(my $i = 0; $i < @list_strange; $i++){
        my %hash;
        %hash->{'policy_name'} = $list_strange[$i];
        %hash->{'id'} = $i;
        if($lines[$line_num]){
            if($list_strange[$i] eq "ip_record"){
                %hash->{'enable'} = $data_line[33];
            }elsif($list_strange[$i] eq "ip_time"){
                %hash->{'enable'} = $data_line[34];
            }elsif($list_strange[$i] eq "ip_district"){
                %hash->{'enable'} = $data_line[35];
            }elsif($list_strange[$i] eq "ip_strict"){
                %hash->{'enable'} = $data_line[36];
            }elsif($list_strange[$i] eq "ip_safe"){
                %hash->{'enable'} = $data_line[37];
            }elsif($list_strange[$i] eq "ip_unlaw"){
                %hash->{'enable'} = $data_line[38];
            }
            
        }
        
        push( @$content_array_ref, \%hash );
    }
    

    return ( $status, $mesg, $total_num );
}

sub load_data_tcp() {
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_tcp_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_tcp_detail_data($){
    my $content_array_ref = shift;

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);

    my $line_num = $par{'line_num'};
    my @data_line = split(",",$lines[$line_num]);
    my @list_tcp = ("tcp_head0","tcp_head1","syn_fin","fin");
    $total_num = @list_tcp;
    for(my $i = 0; $i < @list_tcp; $i++){
        my %hash;
        %hash->{'policy_name'} = $list_tcp[$i];
        %hash->{'id'} = $i;
        if($lines[$line_num]){
            if($list_tcp[$i] eq "tcp_head0"){
                %hash->{'enable'} = $data_line[39];
            }elsif($list_tcp[$i] eq "tcp_head1"){
                %hash->{'enable'} = $data_line[40];
            }elsif($list_tcp[$i] eq "syn_fin"){
                %hash->{'enable'} = $data_line[41];
            }elsif($list_tcp[$i] eq "fin"){
                %hash->{'enable'} = $data_line[42];
            }
            
        }
        
        push( @$content_array_ref, \%hash );
    }
    

    return ( $status, $mesg, $total_num );
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