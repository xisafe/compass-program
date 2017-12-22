#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/12/03
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
my $cmd_app_ctrl;
my $cmd_updateips;
my $cmd_conn_ctrl;
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
my $CUR_PAGE = "IP管理";  #当前页面名称，用于记录日志
my $log_oper;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置


#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){

    $custom_dir         = '/objects/ip_object';                            #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;                    #规则所存放的文件夹
    $conf_file          = $conf_dir.'/ip_group';              #策略模板所存放的文件
    $conf_file_rule     = $conf_dir.'/rule_config';                  #规则所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_tmp';     #启用信息所存放的文件
    $cmd                = "/usr/local/bin/restartddosprotect";
    $cmd_ipgroups       = "/usr/local/bin/generateipgroup.py"; #调用编辑ip组脚本
    $cmd_app_ctrl       = "/usr/local/bin/app_ctrl.py";
    $cmd_updateips      = "/usr/local/bin/updateips.py";
    $cmd_conn_ctrl      = "/usr/local/bin/conn_ctrl.py";
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/jquery.min.js"></script>
                   
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/ipgroups.js"></script>';
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
    # elsif ($action eq 'enable_data') {
    #     #==启用规则==#
    #     &toggle_enable( $par{'id'}, "on" );
    # }
    # elsif ($action eq 'disable_data') {
    #     #==禁用规则==#
    #     &toggle_enable( $par{'id'}, "off" );
    # }
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


sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};
    my @lines;
    my $maxid = 0;
    my @id_arr;
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
            #get the maxid 
            $maxid = (max( @id_arr ) >= 0) ? max( @id_arr ) + 1 : 1;
            ( $status, $mesg ) = &append_one_record( $conf_file, "$maxid,$record" );
            my $cmd_add = $cmd_ipgroups.' -i '.$maxid.' -a '.$maxid.','.$record;
            my $str1 = `sudo $cmd_add`;
          
        }
        $log_oper = "add";
    } else {
        #修改
        ( $status, $mesg ) = &update_one_record_by_id( $conf_file, $item_id, "$item_id,$record" );
        my $cmd_edit = $cmd_ipgroups.' -i ' .$item_id.' -r '.$item_id.','.$record;
        `sudo $cmd_edit`;
        $log_oper = "edit";
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg);
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
    my ( $status, $mesg );
    &read_config_lines($conf_file,\@lines);
    my @ids = split("\&",$par{'id'});
    my $var_ips = $par{'id'};
     $var_ips =~ s/&/\\&/g;
    my @ids_rule_del = ();
    foreach(@ids){
        my @data_line = split(",",$lines[$_]);
        my @sub_ids_rule = &get_ruleid_for_policy($data_line[0]);
        push(@ids_rule_del,@sub_ids_rule);
    }
    my $cmd_del = $cmd_ipgroups.' -i '.$var_ips.' -x '.1;
    my  $del_str = `sudo $cmd_del`;
    if($del_str == 256){
        $status = '-1';
        $mesg = 'ip组已经被引用！';
    }
    # &delete_several_records( $conf_file_rule,join("\&",@ids_rule_del) );
    else{
      ( $status, $mesg ) = &delete_several_records_by_id( $conf_file, $par{'id'});   
    }
    
    
    if($status eq '0'){
        $mesg = '删除成功！';
         $log_oper = "del";
         &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
    }
    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;
    %ret_data->{'ids'} = $cmd_del;

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
            # $config{'id'} = $i;
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
    $config{'name'}   = $temp[1];
    $temp[2] =~ s/\|/\n/g; 
    $config{'ip'}     = $temp[2];
    $config{'description'}   = $temp[3];
   
    # my @rules_for_policy = &get_ruleid_for_policy($temp[0]);
    # $config{'rules_for_policy'}   = join("\&",@rules_for_policy);
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'name'} );

    my $ip = $hash_ref->{'ip'};
    $ip =~ s/\r//g;
    $ip =~ s/\n+/\|/g;
    $ip =~ s/\|+$|\r|\s*//g;
    push( @record_items, $ip);

    my $description = $hash_ref->{'description'};
    $description =~ s/,/，/g;
    push( @record_items, $description );
    
    return join (",", @record_items);
}

# sub toggle_enable($$) {
#     my $item_id = shift;
#     my $enable = shift;

#     my ( $status, $mesg, $line_content ) = &get_one_record( $conf_file, $item_id );
#     if( $status != 0 ) {
#         $mesg = "操作失败";
#         &send_status( $status, $mesg );
#         return;
#     }

#     my %config = &get_config_hash( $line_content );
#     $config{'enable'} = $enable;
#     $line_content = &get_config_record(\%config);

#     my ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $line_content );
#     if( $status != 0 ) {
#         $mesg = "操作失败";
#     }

#     &send_status( $status, $mesg );
#     return;
# }

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
    my $result;
    system($cmd);
    $result = $?;
    chomp($result);
    my $msg;
    if($result == 0){
        $msg = "应用成功";
        `sudo $cmd_app_ctrl`;
        `sudo $cmd_updateips`;
        `sudo $cmd_conn_ctrl`;
    }else{
        $msg = "应用失败";
    }
    &clear_need_reload_tag();
    $log_oper = "apply";
    &send_status( 0, 0, $msg );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
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
