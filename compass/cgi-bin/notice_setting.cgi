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
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;

#审查日志所需变量
my $CUR_PAGE = "公告配置" ;  #当前页面名称，用于记录日志
my $log_oper;                      #当前操作，用于记录日志. 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '0';         #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/AAA';              #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;           #规则所存放的文件夹
    $notice_html        = $conf_dir.'/html';
    $conf_file          = $conf_dir.'/notice';              #发件人信息所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_notice';#启用信息所存放的文件
    $cmd                = "sudo /usr/local/bin/restartAAA";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/notice_setting_init.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par,0,1);
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
    <div id="mesg_box_notice" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_notice_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_notice_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}


sub save_data() {
    my $reload = 0;
    
    my $item_id = $par{'id'};
    
    my @lines;
    &read_config_lines($conf_file,\@lines);
    
    if($item_id ne ''){
        delete $lines[$item_id] ;
    }

    my ( $status, $mesg ) = ( -1, "未保存" );
    foreach (@lines){
        if($par{'notice_title'} eq (split(",",$_))[0]){
            ( $status, $mesg ) = ( -2, $par{'notice_title'}."已占用" );
        }
    }
    
    if ($status ne '-2') {
        my $record = &get_config_record( \%par );
        if( $item_id eq '' ) {
            ( $status, $mesg ) = &append_one_record( $conf_file, $record );
            $log_oper = "add";
        } else {
            ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
            $log_oper = "edit";
        }
    }

    if( $status == 0 ) {
        $reload = 0;
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
    my $sequence = 1;
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
            $conf_data{'sequence'} = $sequence;
            $sequence++;
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
        %ret_data->{'reload'} = 0;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}


sub delete_data() {
    my @dele_lines = ();
    my ( $status, $error_mesg ) = &read_config_lines( $conf_file, \@dele_lines );
    my @temp = split(/,/, $dele_lines[$par{'id'}]);
    `rm -f $temp[1]`;
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = '删除公告成功';
    $log_oper = 'del';

    &send_status($status,0,$mesg);
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
    my $sequence = 1;
    for ( my $i = $from_num; $i < $total_num; $i++ ) {
        my %config = &get_config_hash( $lines[$i] );
        if( $config{'valid'} ) {
            $config{'id'} = $i;
            $config{'sequence'} = $sequence;
            $sequence++;
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
    $config{'notice_title'}   = $temp[0];
    $config{'notice_content'} = `cat $temp[1]`;
    $config{'create_time'}   = $temp[2];
    #============自定义字段组装-END===========================#
    return %config;
}
sub randstr($) {
    my $len = shift;
    my $str;
    my @W = ('0' .. '9', 'a' .. 'z', 'A' .. 'Z');
    my $i = 0;
    while ($i++ < $len) {
        $str .= $W[rand(@W)];
    }
    return $str;
}
sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    if ($par{'id'} ne '') {
        my @dele_lines = ();
        my ( $status, $error_mesg ) = &read_config_lines( $conf_file, \@dele_lines );
        my @temp = split(/,/, $dele_lines[$par{'id'}]);
        `rm -f $temp[1]`;
    }
        my $notice_title = $hash_ref->{'notice_title'} ;
        my $notice_content = $hash_ref->{'notice_content'} ;
        my $rand_filename = &randstr(16);
        $notice_title =~ s/\,/\，/g ;
        $notice_title =~ s/\n/\;/g ;
        $notice_html_addr = $notice_html.'/' . $rand_filename;
        if(! -e $notice_html_addr){
            system("touch $notice_html_addr");
        }
        my $notice_html_cont =  $notice_content ;  
        my @lines = () ;
        $lines[0] = $notice_html_cont ; 
        my ($status ,$mesg) = &write_config_lines( $notice_html_addr , \@lines );
        push( @record_items, $notice_title );
        push( @record_items, $notice_html_addr );
        my $date = &getTime();
        my $ymd = $date -> {'date'};
        push( @record_items, $ymd );    
 
    
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
    # my $enable = shift;
    # my $operation = "启用";
    # $log_oper = 'enable';
    # if ( $enable ne "on" ) {
    #     $operation = "禁用";
    #     $log_oper = 'disable';
    # }
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
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
    if(! -e $notice_html){
        system("mkdir -p $notice_html");
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
    $log_oper = 'apply';
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
sub getTime{
    #time()函数返回从1970年1月1日起累计秒数
    my $time = shift || time();
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($time);
   
    $mon ++;
    $sec  = ($sec<10)?"0$sec":$sec;#秒数[0,59]
    $min  = ($min<10)?"0$min":$min;#分数[0,59]
    $hour = ($hour<10)?"0$hour":$hour;#小时数[0,23]
    $mday = ($mday<10)?"0$mday":$mday;#这个月的第几天[1,31]
    $mon  = ($mon<10)?"0$mon":$mon;#月数[0,11],要将$mon加1之后，才能符合实际情况。
    #$mon  = ($mon<9)?"0".($mon+1):$mon;#月数[0,11],要将$mon加1之后，才能符合实际情况。
    $year+=1900;#从1900年算起的年数
   
    #$wday从星期六算起，代表是在这周中的第几天[0-6]
    #$yday从一月一日算起，代表是在这年中的第几天[0,364]
    # $isdst只是一个flag
    my $weekday = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat')[$wday];
    return { 'second' => $sec,
             'minute' => $min,
             'hour'   => $hour,
             'day'    => $mday,
             'month'  => $mon,
             'year'   => $year,
             'weekNo' => $wday,
             'wday'   => $weekday,
             'yday'   => $yday,
             'date'   => $year."-".$mon."-".$mday,
          };
}