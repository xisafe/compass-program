#!/usr/bin/perl -w
#==============================================================================#
#
# 描述: 接收邮件过滤日志页面
#
# 作者：辛志薇(xinzhiwei) 
# 历史：2014-05-18 辛志薇创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

my $access_log_file_path;
my $base_dir;
my $common_cmd;
my $log_search_tmp_file_path;

my $need_reload_tag;
my $extraheader;
my %par;
my %query;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $errormessage,$warnmessage,$notemessage;


&main();

sub main() {
    # 获取post的值
    &getcgihash(\%par);
    # 获取get的值
    &get_query_hash(\%query);
    # 初始化变量值
    &init_data();
    # 做出响应
    &do_action();

}

sub init_data(){
    $access_log_file_path = "/var/log/p3scan.log";
    $base_dir = "/var/log/";
    $common_cmd = "/usr/local/bin/queryfilterlog.py";
    $log_search_tmp_file_path = "/tmp/p3scan.log";
    #============扩展的CSS和JS文件-BEGIN========================================================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/receive_email_filter_log.js"></script>
                    <script language="JavaScript" src="/include/ESONCalendar.js"></script>';
    #============扩展的CSS和JS文件-BEGIN=======================================================#
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $panel_name = $par{'panel_name'};
    my $query_action = $query{'ACTION'};

    if( $action ne 'export_data' && $query_action ne 'export_data' ) {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if( $action eq 'init_date' ){
        &init_date();
    }
    elsif ( $action eq 'load_data') {   # 加载日志（包含查询按钮）
        &load_data();
    }
    elsif ($action eq 'delete_data') {   # 删除日志
        &delete_data();
    }
    # else {
    #     &show_page();
    # }
    else {
        if( $query{'ACTION'} eq 'export_data' ){
            &export_data();
        }else {
            &show_page();
        }
    }
}

sub show_page() {
    &openpage( "接收邮件过滤日志", 1, $extraheader );
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &closebigbox();
    &display_main_body();
    &closepage();
}

sub display_main_body() {
    printf<<EOF
    <div id="mesg_box_id" class="container"></div>
    <div id="email_filter_log_panel" class="container"></div>
EOF
    ;
}

sub init_date(){
    my %ret_data;
    my $date = &get_current_time("yyyy-mm-dd");
    $ret_data{'SYS_DATE'} = $date;
    my $ret = $json->encode(\%ret_data);
    print $ret;

}

sub load_data(){
    my ($status, $mesg ) = (-1, "");
    my $total_num = 0;
    my @lines;
    my @content_array;
    my %ret_data;
    my $query_cmd;
    my $formated_date = &get_format_date( $par{'DATE'} );

    if( $par{'INIT_TAG'} eq 'true' ){
        # `echo 111 >/tmp/haha`;
        ($status,$mesg,$total_num) = &read_config_lines( $access_log_file_path, \@lines);
    }
    elsif( &is_today($formated_date) ){  # 注意传给is_today的日期参数必须要经过格式化 &is_today($par{'DATE'})错误！
        ($status,$mesg,$total_num) = &read_config_lines( $access_log_file_path, \@lines);
    }
    else{
        `echo 222 >/tmp/haha`;
        if( $par{'search'} ne ''){
            $query_cmd = $common_cmd." -p -m ".$formated_date." -g ".$par{'search'};
            `echo "$query_cmd" >>/tmp/haha`;  # /usr/local/bin/queryfilterlog.py -t -m 20150510 -g baidu
            system($query_cmd);
        }
        else{
            $query_cmd = $common_cmd." -p -m ".$formated_date;
            `echo "$query_cmd" >>/tmp/haha`;  # /usr/local/bin/queryfilterlog.py -t -m 201500510 多了一个0
            system($query_cmd);
        }
        ($status,$mesg,$total_num) = &read_config_lines( $log_search_tmp_file_path, \@lines);
    }

    for( my $i = 0; $i < @lines; $i++ ) {
        my %hash = ();
        if( !$LOAD_ONE_PAGE ) {    $id = $i;   }

        %hash = &get_config_hash( $lines[$i] );
        $hash{'id'} = $id;
        push( @content_array, \%hash );
    }
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_config_hash($){
    my $line_content = shift;
    chomp($line_content);
    my %config;
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/ /, $line_content);
    $config{'LOG_TIME'}     = $temp[0];
    $config{'SRC_IP'}       = $temp[1];
    $config{'SENDER_EMAIL'}   = $temp[2];
    $config{'RECIPIENT_EMAIL'}  = $temp[3];
    $config{'DETAILS'}  = $temp[4];
    $config{'ACTION'}       = $temp[5];
    #============自定义字段组装-END===========================#
    return %config;
}


sub get_format_date($){
    my $date = shift;
    my @arr = split(/-/,$date);
    my $month = $arr[1];
    my $day = $arr[2];
    if( $month < 10 && $month !~ /^0/ ){
        $month = "0".$month;
    }
    if( $day < 10 && $day !~ /^0/ ){
        $day = "0".$day;
    }
    $arr[1] = $month;   $arr[2] = $day;
    $date = join("-",@arr);
    $date =~ s/-//g;
    return $date;
}

sub is_today($){
    my $date = shift;   # 传进来的这个日期已经是格式化后的, 20150513
    my $current_date = &get_current_time("yyyy-mm-dd");  # 2015-05-12
    $current_date = &get_format_date($current_date);     # 20150512
    `echo "$current_date" >>/tmp/haha`;

    if( $date eq $current_date ){
        return 1;
    }
    return 0;
}


sub delete_data(){
    my ( $status, $mesg ) = (-1, "日志删除失败");
    my $formated_date = &get_format_date($par{'DATE'});
    my $cmd = $common_cmd." -p -e -m ".$formated_date;
    system($cmd);
    if($? == 0){
        $status = 0;
        $mesg = "日志删除成功";
    }
    # &send_status($status,$mesg);
    my %ret_data;
    $ret_data{'status'} = $status;
    $ret_data{'mesg'} = $mesg;
    my $ret = $json->encode(\%ret_data);
    print $ret;
}


sub export_data(){
    my $file_name;
    my $export_file_path;
    my $formated_date = &get_format_date( $query{'DATE'} );
      # 不要再写成par哈希获得'DATE'的值，得到的错误调试结果就是00
      # $formated_date的值是00，$file_name的值是p3scan.log-00gz

    `echo "$formated_date" >/tmp/haha`;
    if( &is_today($formated_date) ){   `echo is_today-is-true >>/tmp/haha`;
        $export_file_path = $base_dir."p3scan.log";
        $file_name = "p3scan.log";
    }
    else{
        $export_file_path = $base_dir."p3scan.log-".$formated_date.".gz";
        $file_name = "p3scan.log-".$formated_date.".gz";
    }
    `echo "$file_name" >>/tmp/haha`;
    my $status = 0;
    my @fileholder;
    open( DOWNLOADFILE, "<$export_file_path" ) or $status = -1;
    push( @fileholder, <DOWNLOADFILE> );
    close (DOWNLOADFILE);

    if( $status == 0) {
        print "Content-Type:application/x-download\n";
        print "Content-Disposition:attachment;filename=$file_name\n\n";
        print @fileholder;
    }else {
        &showhttpheaders();
        $errormessage = "对不起，$query{'DATE'}日的日志文件没有找到";
        &show_page();
    }
}

sub get_current_time{
    $_ = shift;
    my $t = shift;
    (!$t) and ($t = time);
    my ($sec,$min,$hour,$mday,$mon,$year) = localtime($t);
    $year += 1900;
    my $yy = substr $year,2,2;
    $mon++;
    s/yyyy/$year/gi;
    s/yy/$yy/gi;
    if ($mon < 10)  { s/mm/0$mon/gi;  } else { s/mm/$mon/gi; }
    if ($mday < 10) { s/dd/0$mday/gi; } else { s/dd/$mday/gi; }
    $_;
}