#!/usr/bin/perl

use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $page_title;         #页面标题
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $username_cmd;
my $password_cmd;
my $flag_cmd;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
#记录日志的变量
my $CUR_PAGE = "VPN拨号用户" ;  #当前页面名称，用于记录日志
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
    $custom_dir         = '/dialuser';                      #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;          #规则所存放的文件夹
    $conf_file          = $conf_dir.'/config';              #规则所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_vpn';
    $cmd = "sudo /usr/bin/vpndialuser ";

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/remote_dial_vpn_init.js"></script>
                    <style>
                        tr.add-panel-odd-line td.add-panel-subtitle, tr.add-panel-even-line td.add-panel-subtitle{
                            text-indent:15px;
                            border-right:1px solid #999;
                            width:20%;
                            background-color:#e6eff8;
                            font-weight:bold;
}
                    </style>';
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
        &load_data();
    }elsif ($action eq 'save_data' && $panel_name eq 'add_panel') {
        &save_data();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
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
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_test_div();
    &closepage();
}

sub display_test_div() {
    printf<<EOF
    <div id="mesg_box_vpn" style="width: 96%;margin: 20px auto;">mesg</div>
    <div id="panel_vpn_add" style="width: 96%;margin: 20px auto;">adddd</div>
    <div id="panel_vpn_list" style="width: 96%;margin: 20px auto;">listttttt</div>
EOF
    ;
}

sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};
    my $username = $par{'username'};
    
    $username_cmd = $username;
    $password_cmd = $par{'pwd2'};
    
    my @lines;
    my ( $status, $mesg );
    &read_config_lines( $conf_file, \@lines );
    ( $status, $mesg ) = ( -1, "未保存" );
    
    
    if( $item_id eq '' ) {
        $flag_cmd = 'add';
        foreach (@lines){
            if($username eq (split(",",$_))[0]){
                ( $status, $mesg ) = ( -2, "用户名已存在" );
            }
        }
        if($status != -2){
            ( $status, $mesg ) = &append_one_record( $conf_file, $record );
            system($cmd.'add '.$username_cmd.' '.$password_cmd);
        }
        if( $status == 0 ) {
            $reload = 1;
            &create_need_reload_tag();
            $mesg = "添加成功";
        }
        $log_oper = "add";
    } else {
        $flag_cmd = 'edit';
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
        my $line_old = $lines[$item_id];
        my $username_old = (split(",",$line_old))[0];
        my $password_old = (split(",",$line_old))[1];
        system($cmd.'del '.$username_old.' '.$password_old);
        system($cmd.'add '.$username_cmd.' '.$password_cmd);
        if( $status == 0 ) {
            $reload = 1;
            &create_need_reload_tag();
            $mesg = "修改成功";
        }
        $log_oper = "edit";
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
            my %config = &get_config_hash(@lines[$i]);
               if($search ne ""){
                if (lc($config{'username'}) !~ m/$search/ &&
                  lc($config{'note'}) !~ m/$search/ 
                     ) {
                    next;
                }    
            }
            # if($search ne ""){
            #     my $searched = 0;
            #     my $where = -1;
            #     my @data = split(",", @lines[$i]);
            #     foreach my $field (@data) {
            #         #===转换成小写，进行模糊查询==#
            #         my $new_field = lc($field);
            #         $where = index($new_field, $search);
            #         if($where >= 0) {
            #             $searched++;
            #         }
            #     }
            #     #如果没有一个字段包含所搜寻到子串,则不返回
            #     if(!$searched){
            #         next;
            #     }
            # }
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
    my @lines;
    #$flag_cmd = 'delete';
    &read_config_lines( $conf_file, \@lines );
    my @ids = split("\&",$par{'id'});
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});
    foreach(@ids){
        my @date_line_delete = split(",",$lines[$_]);
        $username_cmd = $date_line_delete[0];
        $password_cmd = $date_line_delete[1];
        system($cmd.'del '.$username_cmd.' '.$password_cmd);
    }
    
    $reload = 1;
    &create_need_reload_tag();
    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'msg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    $log_oper = "del";
    #print $ret;
    &send_status( $status, $reload, $mesg );
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
    $config{'username'}   = $temp[0];
    $config{'pwd'}   = $temp[1];
    $config{'pwd2'}   = $temp[1];
    $config{'note'}   = $temp[2];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'username'} );
    push( @record_items, $hash_ref->{'pwd2'} );
    push( @record_items, $hash_ref->{'note'} );
    
    return join ",", @record_items;
}

sub toggle_enable($) {
    my $enable = shift;
    my $operation = "启用";
    $log_oper = 'enable';
    if ( $enable ne "on" ) {
        $operation = "禁用";
        $log_oper = 'disable';
    }
    my @lines = ();

    my ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, $mesg );
        return;
    }

    my %item_id_hash;
    my @item_ids = split( "&", $par{'id'} );
    foreach my $id ( @item_ids ) {
        $item_id_hash{$id} = $id;
    }

    my $len = scalar( @lines );

    for ( my $i = 0; $i < $len; $i++ ) {
        if( $item_id_hash{$i} eq "$i" ) {
            my %config = &get_config_hash( $lines[$i] );
            $config{'enable'} = $enable;
            $lines[$i] = &get_config_record(\%config);
        }
    }

    my ( $status, $mesg ) = &write_config_lines( $conf_file, \@lines );
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
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
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
    # if($flag_cmd eq 'add'){
        # system($cmd.'add '.$username_cmd.' '.$password_cmd);
    # }elsif($flag_cmd eq 'del'){
        # system($cmd.'del '.$username_cmd.' '.$password_cmd);
    # }elsif($flag_cmd eq 'edit'){
        # system($cmd.'del '.$username_cmd.' '.$password_cmd);
        # system($cmd.'add '.$username_cmd.' '.$password_cmd);
    # }
    &clear_need_reload_tag();
    $log_oper = "apply";
    &send_status( 0, 0, "应用成功" );
}

sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}