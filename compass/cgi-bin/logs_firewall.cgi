#!/usr/bin/perl
#==============================================================================#
#
# 描述: 添加规则列表规则页面
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.09.23 WangLin创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'logs_common.pl';

#=================初始化全局变量到init_data()中去初始化========================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 1;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my $DEBUG  = "OFF";
my $log_name = "防火墙";
my $READ_OPEN_ERROR    = "读取数据时，打开文件失败";
my $WRITE_OPEN_ERROR   = "写入数据时，打开文件失败";

my $NONE_READ_ERROR    = "未读取数据";
my $NONE_WRITE_ERROR   = "未写入数据";
my $NONE_CHANGE_ERROR  = "数据没有变化";

my $READ_SUCCEEDED     = "读取数据成功";
my $WRITE_SUCCEEDED    = "写入数据成功";

my $FILE_NOT_FOUND     = "文件不存在";
my %chaindisplay;

my $errormessage    = '';
my $notemessage     = '';
$chaindisplay{'INCOMINGFW'}="流入防火墙";
$chaindisplay{'OUTGOINGFW'}="流出防火墙";
$chaindisplay{'ZONEFW'}="区域防火墙";
$chaindisplay{'ZONEFW6'}="IPV6防火墙";
$chaindisplay{'VPNFW'}="VPN防火墙";
$chaindisplay{'INPUT'}="系统访问";
$chaindisplay{'INPUTFW'}="系统访问";
$chaindisplay{'ALLOW'}="通过入侵防御";
$chaindisplay{'DROP'}="丢弃";
$chaindisplay{'ACCEPT'}="允许";
$chaindisplay{'REJECT'}="拒绝";
$chaindisplay{'BADTCP'}="错误TCP连接";
$chaindisplay{'PORTFWACCESS'}="DNAT";
$chaindisplay{'FORWARD'}="转发";
$chaindisplay{'PROXIES'}="代理";
$chaindisplay{'HTTP-PROXY'}="HTTP代理";
$chaindisplay{'FTP-PROXY'}="FTP代理";
$chaindisplay{'POLICYROUTING'}="策略路由";
$chaindisplay{'PORTSCAN'}="端口扫描";
$chaindisplay{'不带SYN标志'}="非SYN连接";
#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post请求传过来的变量
    &getcgihash(\%par);
    #获取get请求传过来的变量
    &get_query_hash(\%query);
    #初始化变量值
    &init_data();
    # &make_file();
    #做出响应
    &do_action();
}

sub init_data() {

    $errormessage     = '';
    $notemessage     = '';
	$logfile          ="/var/log/firewall";
    $logname          ="firewall";
    # $logfile_test     =`cat /var/log/firewall_test`;
    $logfile_test =`head /var/log/firewall -n $from_num | tail -n $page_size`;

    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/all_log.css" />
                    <link rel="stylesheet" type="text/css" href="/include/jquery-ui.min.css" />
                    <script language="JavaScript" src="/include/jquery-3.1.0.min.js"></script>
                    <script language="JavaScript" src="/include/jquery-ui.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/logs_search.js"></script>
                    <script type="text/javascript" src="/include/jsencrypt.min.js"></script>
                    <script type="text/javascript" src="/include/logs_delete.js"></script>
                    <script type="text/javascript" src="/include/ESONCalendar.js"></script>
                    <script type="text/javascript" src="/include/jquery.md5.js"></script>
                    <link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />
                    <script language="JavaScript" src="/include/logs_firewall.js"></script>';
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-END==============================#
}

sub  do_action() {
	#==一般ACTION只会通过一种方式传过来，开发者需要自己判断从哪种方式传过来==#
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};

    if($action ne 'download' && $query_action ne 'download' && $query_action ne 'download') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#

    if ( $action eq 'load_data' && $panel_name eq 'list_panel' ) {
        &load_data();
    }
    elsif ( $action eq 'search_log' ) {
        &load_data();
    }
    elsif ( $action eq 'importLog') {
        ($errormessage,$notemessage) = &importLog(\%par,'firewall');
        &show_page();
    }       
    elsif ( $action eq 'delete') {
        &deleteLog();
    }    
    elsif ( $action eq 'clearLog') {
        &clearLogForPass();
    }    
    else {
        if ($action eq 'download') {
            $errormessage = &download($par{'export_log'});
            &showhttpheaders();
            &show_page();
        }
        else {
            &show_page();
        }
    }
}

sub dateToFilestring($) {
    my $date = shift;
    $date =~ s/\-//g;
    return $date;
}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_main_body();
    &closepage();
}

sub display_main_body() {
    
	printf<<EOF
	
    <div id="mesg_box" class="container"></div>
    <div id="add_panel" class="container"></div>
    <div id="importLog_panel" class="container"></div>
    <div id="list_panel" class="container"></div>
    <input type="hidden" id="log-mesg-error" value="$errormesg">	
	
EOF
    ;
}

sub get_config_hash($) {

    my $line_content = shift;
    chomp($line_content);
    my %config;
    $config{'valid'} = 1; #默认是合法的行，如果有不合法的，将该字段置为0
    if ($line_content eq '') {
        $config{'valid'} = 0;
        return %config;
    }
    #============自定义字段组装-BEGIN=========================#
    $line_content =~ /(^... .. ..:..:..) [\w\-]+ ulogd\[.*\]: (.*) APPID=(.*) (IN=.*)$/;
    my $timestamp = $1;
    my $comment = $2; 
    my $packet = $4;  
    # $config{'datetime'} = $datetime;
    #============自定义字段组装-END===========================#
    $timestamp = change_time($timestamp);
    $timestamp =~s/^\s//;
    $config{'datetime'} = $timestamp;

    $packet =~ /IN=(\w+)/;      my $in_iface=$1;
    $packet =~ /OUT=(.*)MAC/;      my $out_iface=$1;
    $packet =~ /SRC=([\d\.]+)/; my $srcaddr=$1;
    $packet =~ /DST=([\d\.]+)/; my $dstaddr=$1;
    $packet =~ /MAC=([\w+\:]+)/; my $macaddr=$1;
    $packet =~ /PROTO=(\w+)/;   my $proto=$1;
    $packet =~ /SPT=(\d+)/;     my $srcport=$1;
    $packet =~ /DPT=(\d+)/;     my $dstport=$1;
    my $printsrcport = $srcport;
    my $printdstport = $dstport;
    if ($out_iface eq " ") {
        $out_iface="无";
    }
    if ($comment=~ /ZONEFW6/) {
        $packet =~ /SRC=(.*)\sDST/;
        $srcaddr = $1;
        $packet =~ /DST=(.*)\sLEN/; 
        $dstaddr=$1;
    }
    my $printsrcaddr = $srcaddr." : ".$srcport;
    my $printdstaddr = $dstaddr." : ".$dstport;
    if (($srcport eq $dstport) && ($srcport eq $proto)) {
        $printsrcaddr = $srcaddr;
        $printdstaddr = $dstaddr;
    }
    if ($proto ==2) {
        $proto = "IGMP";
    }

    my @chaintemp=split(/\:/,$comment);
    for(my $i=0;$i<2;$i++) {
        $chaintemp[$i]=~s/\s//g;
        if ($chaintemp[$i]=~/NEWnotSYN/) {
            $chaintemp[$i] = "不带SYN标志";
        }
        $chaintemp[$i]=$chaindisplay{$chaintemp[$i]};
        if ($chaintemp[$i] eq "拒绝" || $chaintemp[$i] eq "丢弃") {
            $chaintemp[$i] = $chaintemp[$i];
        }
    }
    $chaintemp[2]=~s/\s//g;
    if ($chaintemp[2] && $chaintemp[2]=~/^\d+$/) {
        $chaintemp[2]="第$chaintemp[2]条";
    }
    else{
        $chaintemp[2] = "默认规则";
    }
    if (!$chaintemp[0]) {
        $chaintemp[0] = "其他";
    }
    if (!$chaintemp[1]) {
        $chaintemp[1] = "其他";
    }

    $config{'en_port'}     = $in_iface;
    $config{'ex_port'}     = $out_iface;
    $config{'src'}         = $printsrcaddr;
    $config{'des'}         = $printdstaddr; 
    $config{'protocol'}    = $proto;  
    $config{'rule'}        = $chaintemp[0];
    $config{'rule_action'} = $chaintemp[1];
    $config{'num'}         = $chaintemp[2];
    return %config;

}

sub get_compare_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    #============自定义比较字段-BEGIN=========================#
    #一般来说比较的字段和保存的字段几乎都一致，但是存在保存时，
    #要更新修改时间等就不一样了，需要自己定义比较哪些字段=====#
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'note'} );
    push( @record_items, $hash_ref->{'enable'} );
    #============自定义比较字段-END===========================#
    return join ",", @record_items;
}

sub load_data() {

	my %ret_data;

	my @content_array = ();
	my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );
    my $eth_all = `ifconfig |grep eth`;
    my @temp = split(/\n/,$eth_all);
    my @eths;
    foreach my $elem(@temp){
        $elem =~ /(eth\d+)\s*/;
        push(@eths,$1);
    }
    push(@eths,"br0");
    push(@eths,"br1");
    my @content_array_rev = reverse(@content_array);

    %ret_data->{'detail_data'} = \@content_array_rev;
    %ret_data->{'eths'} = \@eths;
    %ret_data->{'total_num'} = $total_num;
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub download($) {
    my $select_date = shift;
    my $today = &getDate(time);
    if ($select_date eq '') {
        $select_date = $today;
    }
    my $filestr = $logfile;
    if ($select_date ne $today) {
        $filestr="${logfile}-".dateToFilestring($select_date).".gz";
    }
    &down_file($filestr,$par{'ACTION'},$select_date,$log_name);

}
sub deleteLog(){
    my %ret_data;
    my $select_date = $par{'searchTime'};
    my $today = &getDate(time);
    if ($select_date eq '') {
        $select_date = $today;
    }
    my $filestr = $logname;
    if ($select_date ne $today) {
        $filestr="${logname}-".dateToFilestring($select_date).".gz";
    }
    %ret_data->{'filestr'} = 'delete='.$filestr;
    my $ret = $json->encode(\%ret_data);
    print $ret;
}
sub clearLogForPass(){
    my %ret_data;
    my $filestr = 'clear='.'firewall';
    %ret_data->{'filestr'} = $filestr;
    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub get_detail_data($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;

    #===============获得查询条件===============#
    my $select_date = $par{'searchTime'};
    my $today = &getDate(time);
    my @select_arr = ();
    my $date;
    if ($select_date ne '') {
        my @temp = split('-',$select_date);
        my $date_day_select = int($temp[2]);
        my $date_month_select = int($temp[1]);

        if ($date_month_select == 1) {
            $date_month_select = 'Jan';
        }
        if ($date_month_select == 2) {
            $date_month_select = 'Feb';
        }
        if ($date_month_select == 3) {
            $date_month_select = 'Mar';
        }
        if ($date_month_select == 4) {
            $date_month_select = 'Apr';
        }
        if ($date_month_select == 5) {
            $date_month_select = 'May';
        }
        if ($date_month_select == 6) {
            $date_month_select = 'Jun';
        }
        if ($date_month_select == 7) {
            $date_month_select = 'Jul';
        }
        if ($date_month_select == 8) {
            $date_month_select = 'Aug';
        }
        if ($date_month_select == 9) {
            $date_month_select = 'Sep';
        }
        if ($date_month_select == 10) {
            $date_month_select = 'Oct';
        }
        if ($date_month_select == 11) {
            $date_month_select = 'Nov';
        }
        if ($date_month_select == 12) {
            $date_month_select = 'Dec';
        }

        if ($date_day_select < 10) {
            $date_day_select = $date_day_select + 0;
            $date = $date_month_select.' '.' '.$date_day_select;
        }
        if ($date_day_select >= 10) {
            $date = "$date_month_select $date_day_select";
        }

    }
    my $time_select = $par{'searchHours'};
    my $rule_select = $par{'searchRule'};
    my $action_select = $par{'searchAction'};
    my $protocol_select = $par{'searchProtocol'};
    my $interface_select = $par{'searchInterface'};
    my $src_ip = $par{'searchSrcIp'};
    my $des_ip = $par{'searchDesIp'};
    #===============获得查询条件===============#

    #================将查询条件封装============#
    my $better_cnt = '';
    if ($LOAD_ONE_PAGE) {
       # $better_cnt = "-m ".$page_size * $current_page;
    }
    # my $time_select = 'egrep'.' '.'\'('.$time_select.')'.':[0-9][0-9]:[0-9][0-9]'.' '.'localhost'.'\''.$logfile.'|';
    if ($date ne '') 
        { 
            $date_select = "fgrep \'$date\'";
            push(@select_arr, $date_select);
        }
    if ($rule_select ne '')
        { 
            $rule_select = "fgrep \'$rule_select\'";
            push(@select_arr, $rule_select);
        }
    if ($action_select ne '') 
        { 
            $action_select = "fgrep \'$action_select\'";
            push(@select_arr, $action_select);
        }
    if ($protocol_select ne '')
        { 
            $protocol_select = "fgrep \'$protocol_select\'";
            push(@select_arr, $protocol_select);
        }
    if ($interface_select ne '') 
        {
            $interface_select = "fgrep \'$interface_select\'";
            push(@select_arr, $interface_select);
        }
    if ($src_ip ne '') 
        { 
            $src_ip = "fgrep \'SRC=$src_ip\'";
            push(@select_arr, $src_ip);
        }
    if ($des_ip ne '') 
        { 
            $des_ip = "fgrep \'DST=$des_ip\'";
            push(@select_arr, $des_ip);
        }
    if ($time_select ne '') 
        { 
            $time_select = "egrep $better_cnt \'($time_select):[0-9][0-9]:[0-9][0-9] localhost\'";
            push(@select_arr, $time_select);
        } # last
    my $select_join = join ("|", @select_arr);
    my $log_select;
    my $all_logfile;
    # if ($select_date eq ''){
        # $log_select = "(cat $logfile 2>/dev/null ; ls $logfile-*.gz 2>/dev/null| sort -n | xargs zcat 2>/dev/null)";
        # $select_date = $today;
    # }
    # if ($select_join ne '' && $today eq $select_date) {
    #     $log_select = "cat $logfile |";
    # }
    # elsif ($select_join ne '' && $select_date ne '' && $today ne $select_date) {
    #     my $filestr="${logfile}-".dateToFilestring($select_date).".gz";
    #     $log_select = "zcat $filestr |";
    #     # print $log_select.'aaa';
    # }    
    # elsif ($select_join ne '' && $select_date eq '') {
    #      $log_select = "(cat $logfile 2>/dev/null ; ls $logfile-*.gz 2>/dev/null| sort -n | xargs zcat 2>/dev/null) |";
    # }
    # else {
    #      $log_select = "(cat $logfile 2>/dev/null ; ls $logfile-*.gz 2>/dev/null| sort -n | xargs zcat 2>/dev/null)";
    # }
    # $log_select = "(cat $logfile 2>/dev/null ; ls $logfile-*.gz 2>/dev/null| sort -n | xargs zcat 2>/dev/null)";
    if($select_join eq '') {
        $log_select = "(cat $logfile 2>/dev/null ; ls $logfile-*.gz 2>/dev/null| sort -n | xargs zcat 2>/dev/null)";
    }
    else{
        $log_select = "(cat $logfile 2>/dev/null ; ls $logfile-*.gz 2>/dev/null| sort -n | xargs zcat 2>/dev/null) |";
    }
    my $search_select = $log_select.$select_join;
    #================将查询条件封装============#
    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $logfile, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records_better( $logfile, $page_size, $current_page, \@lines, $search_select );

    }
    for( my $i = 0; $i < @lines; $i++ ) {
        my %hash = &get_config_hash( $lines[$i] );
        if ( !$hash{'valid'} ) {
            next;
        }

        #===实现查询===#
        if ( $searchtime ne "" ) {
            my $date = lc $hash{'datetime'};
            # my $date = $hash{'datetime'};
            my @temp_date = split(' ',$date);
            $date = $temp_date[0];
            $hour = $temp_date[1];
            my $note = lc $hash{'note'};
            if ( !($date =~ m/$searchtime/) && !($date =~ m/$searchtime/) ) {
                #===对名字，说明进行搜索===#
                next;
            }
        }

        $hash{'id'} = $id; #自定义id，id可以是任何字符，只要能唯一区别每一条数据
        $hash{'result'}='成功';
        push( @$content_array_ref, \%hash );
    }

    return ( $status, $mesg, $total_num );
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
    # %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
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
    $search = lc $search;

    return $search;
}

sub prepare_note($) {
    my $note = shift;
    $note =~ s/\n/ /g;
    $note =~ s/,/，/g;
    return $note;
}


sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
   
    my $time_check = $hash_ref->{'time_check'};

    return join (",", @record_items);
}

sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}

sub getDate($) {
    my $now = shift;
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($now);
    $year += 1900;
    $mon++;
    return sprintf("%04d-%02d-%02d", $year, $mon, $mday);
}

