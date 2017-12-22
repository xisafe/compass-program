#!/usr/bin/perl -w
#=====================================================================
#
# DESCRIPTION: 安全审计模块前台显示用函数集
#
# AUTHOR: Xiao Qianyu, wsxqyws@gmail.com
# CREATED: 2014-12-11
# LAST_MODIFIED: Fri Dec 12 11:21:09 CST 2014
#=====================================================================

use DBI();
use Encode;
use utf8

$EVENT_CLASS = "/etc/efw/idps_console/rules/event_class";

# 连接数据库，返回dbh
# complete
sub connect_sql()
{
    my $dbh;
    my $database = "ips";
    my $user = "root";
    my $pass = "capsheaf#8686";
    #my $user = "ipsloger";
    #my $pass = "mysql123456";

    $dbh = DBI->connect("DBI:mysql:database=$database;host=localhost",$user,$pass,{'RaiseError'=>1});
    $dbh->do("set names utf8");

    return $dbh;
}

# TODO
sub truncate_table($)
{
    my $dbh = shift;
    my $sql = "truncate ipslog";
    $dbh->do($sql);
}

#
# 简单的SQL关键字检测代码，检测到关键字后return 1 否则return 0
# TODO: test it!
#
sub check_SQL_keyword($)
{
    my $str = shift;

    my $key_words = 'select|insert|delete|from|count\(|drop table|update|truncate|asc\(|mid\(|char\(|exec master|netlocalgroup administrators|:|net user|or|and';
    my $key_words2 = '[-|;|,|\/|\(|\)|\[|\}|}|{|%|\@|*|!|\']';

    my $str2 = lc $str;
    if ( $str2 =~ m/$key_words/ || $str2 =~ m/$key_words2/ ) {
        return 1;
    }
    return 0;
}


sub get_all_tables($)
{
    my $dbh = shift;
    my @tables = ();

    my $sql = "show tables like \'ipslog%\'";
    my $sth = $dbh->prepare($sql);
    $sth->execute();
    while (@row = $sth->fetchrow_array()) {
        push(@tables,$row[0]);
    }

    return @tables;
}

#sub search($$$$$$$)
#{
#    my $keyword = shift;
#    my $time_start = shift;
#    my $time_end = shift;
#    my $page_num = shift;
#    my $total_page = shift;
#    my $conf = shift;
#    my $dbh = shift;
#
#    # 处理传入的page_num ,使其合法化
#    if ($page_num <= 0) {
#        $page_num = 1;
#    } elsif ($page_num > $total_page) {
#        $page_num = $total_page;
#    }
#
#
#    my $where_statement = "";
#    # 构造where语句
#    $where_statement = build_where_statement($keyword,$time_start,$time_end,$conf);
#
#    # 设置 order by 语句
#    my $order_by = "";
#    if ($conf->{'ORDER_BY'} eq "priority") {
#        #$order_by = "priority desc";
#    } else {
#        $order_by = "datetime desc";
#    }
#
#    my $start_row = ($page_num-1) * $conf->{'PAGESIZE'};
#
#    my $base_sql = "SELECT a.engine_ip,a.datetime, a.action, a.sid ,inet_ntoa(sip) AS sip,sport,smac,inet_ntoa(dip) AS dip,dport,dmac,response_type , b.msg, b.classification, b.priority, b.protocol";
#    $base_sql .= " FROM ipslog AS a LEFT JOIN t_sid AS b ON a.sid=b.sid";
#    $base_sql .= " $where_statement ORDER BY $order_by limit $start_row, $conf->{'PAGESIZE'}";
#
#
#    # print ">>>>>>>$base_sql\n";
#    my $sth = $dbh->prepare($base_sql);
#
#    $sth->execute();
#
#    return $sth;
#}


# 辅助函数，用来构造where statement
sub join_where($$)
{
    my $str = shift;
    my $join_str = shift;
    my $ret = "";
    if ($join_str eq "") {
        # 无新增条件时直接返回原始数据
        return $str;
    }
    if ( $str =~ /WHERE/ ) {
        $ret = "$str and $join_str";
    } else {
        $ret = "WHERE $join_str";
    }
    return $ret;
}

# 读取配置文件，生成键值对hash
sub loadConfig($)
{
    my $filename = shift;
    my %conf;
    open FH, "<$filename";
    while(my $line=<FH>) {
        chomp($line);
        if(not $line =~ m/^#/) {
            my ($key,$value) = split(/=/,$line);
            $conf{$key} = $value;
        }
    }
    return \%conf;
}

# 实时查询使用代码
# complete
sub intime_query($$$$$)
{
    my $dbh = shift;
    my $max_show = shift;
    my $priority = shift;
    my $search = shift;
    my $array_ref = shift;

    my $where_statement = "";

    # 更新最新的数据
    if ( -e "/usr/local/bin/log2sql.pl" ) {
        system("/usr/local/bin/log2sql.pl");
    }

    # limit max_show
    if ($max_show < 10) {
        $max_show = 10;
    }
    if ($max_show > 1000) {
        $max_show = 1000;
    }

    if($priority ne "" && $priority ne "all") {
        $where_statement = join_where($where_statement,"b.priority = $priority"); 
    }
    # search字段有内容 且 没有发现SQL 关键字
    if ($search ne "" && check_SQL_keyword($search) == 0) {
        $where_statement = join_where($where_statement,"b.event_name like \"\%$search\%\"");
    }
        $where_statement = join_where($where_statement,"action like \"\%log\%\"");  #jfj add 2017.8.17 

    my $sql = "SELECT a.id,a.merge_eid,time_start,time_end,a.sid,INET_NTOA(sip) AS sip,src_user,sport," .
              "INET_NTOA(dip) AS dip,dst_user,dport,merge_type,action as r_action, a.count AS merge_count, " . 
              "b.msg, b.event_name, b.chinese_classification, b.priority, b.protocol " .
              "FROM ipslog_merge AS a LEFT JOIN t_sid AS b ON a.sid = b.sid " .
              "$where_statement " .
              "ORDER BY time_start desc LIMIT $max_show";
    # print "$sql\n";
    my $sth = $dbh->prepare($sql);
    $sth->execute();

    while ( my $list=$sth->fetchrow_hashref()) {
        push(@$array_ref,$list);
    }
}

# 获取详细日志信息（合并前数据）
# complete
sub get_detail_by_eid($$$$)
{
    my $dbh = shift;
    my $eid = shift;
    my $sid = shift;
    my $array_ref = shift;

    my $sql = "SELECT a.id,a.merge_eid,datetime,a.sid,INET_NTOA(sip) AS sip,src_user,sport," .
              "INET_NTOA(dip) AS dip,dst_user,dport,action, " . 
              "b.msg, b.event_name, b.chinese_classification, b.priority, b.protocol " .
              "FROM ipslog AS a LEFT JOIN t_sid AS b ON a.sid = b.sid " .
              "WHERE a.merge_eid = $eid and a.sid = $sid and action like \"\%log\%\"";  #jfj add judge "action..." 2017.8.17   因在一个合并周期内发生的次数可能远大于所设置的最大次数，尤其是一秒内发生很多次，数据库中显示的时间是完全一样的，这样会报多条日志，若按照一条日志的合并时间来查询，返回的数据无法控制精准，故前台做    “已合并（x）”  事件时，没有按照每一次的合并来查 11.16
              #"and datetime < c.time_end and c.time_start < datetime;"
    my $sth = $dbh->prepare($sql);
    $sth->execute();

    while ( my $list=$sth->fetchrow_hashref()) {
        push(@$array_ref,$list);
    }
}

#--------------------------------------------------------------------------
# 历史查询

# (历史查询)构造where语句
# INPUT: $conf(hash)
#        $templete(hash)
sub build_where_statement($$)
{
    my $conf = shift;
    my $templete = shift; # templete(hash) contains time_range
                          # safe_type,priority,ip,port

    my $where_statement = "";
    # parse
    #TODO: 从JSON中获取查询用参数
    my $time_range;      #时间间隔
    my $safe_type;       #安全类型
    my $priority;        #事件级别
    my $ip;              #ip地址
    my $user;            #用户名
    my $port;            #通信端口 

    $time_range = $templete->{"time_range"};
    $safe_type = $templete->{"safe_type"};
    $priority = $templete->{"priority"};
    $ip = $templete->{"ip"};
    $user = $templete->{"user"};
    $port = $templete->{"port"};
    # 构造where语句
    $where_statement = join_where($where_statement,
                                  generate_time_range_condition($time_range));
    $where_statement = join_where($where_statement,
                                  generate_safe_type_condition($safe_type));
    $where_statement = join_where($where_statement,
                                  generate_priority_condition($priority));
    $where_statement = join_where($where_statement,
                                  generate_ip_condition($ip));
    $where_statement = join_where($where_statement,
                                  generate_user_condition($user));
    $where_statement = join_where($where_statement,
                                  generate_port_condition($port));
    $where_statement = join_where($where_statement,
                                  "action like \"\%log\%\"");  #jfj add 2017.8.17
    #print "$where_statement\n";

    return $where_statement;
}

# 根据time_range生成SQL用条件
# input: time_range(hash_ref) contains type(int) and 
#        value(string)                        (when type==1)
#        time_start(string), time_end(string) (when type==2)
# TODO: 时间上不够精确
#       是否加入星期几的字段？
sub generate_time_range_condition($)
{
    my $time_range = shift;
    my $condition = "";

    if ($time_range->{'type'} eq '1') {      # 相对时间
        # 可能出现的值
        # today,yesterday,thisweek,lastweek,thismonth,lastmonth,thisseason,
        # lastseason,lastday_N,lastweek_N,lastmonth_N
        my $time_value = $time_range->{'value'};
        if ($time_value eq "today") {
            $condition = "time_start >= CURRENT_DATE()";
        } elsif ($time_value eq "yesterday") {
            $condition = "time_start >= DATE_SUB(CURRENT_DATE(),INTERVAL 1 DAY) and time_end < CURRENT_DATE()";
        } elsif ($time_value eq "thisweek") {
            #$condition = "time_start >= DATE_SUB(CURRENT_DATE(),INTERVAL 7 DAY)";
            $condition = "YEARWEEK(date_format(time_start,'%Y-%m-%d')) = YEARWEEK(now())";
        } elsif ($time_value eq "lastweek") {
            #$condition = "time_start >= DATE_SUB(CURRENT_DATE(),INTERVAL 14 DAY) and time_end < DATE_SUB(CURRENT_DATE(),INTERVAL 7 DAY)";
            $condition = "YEARWEEK(date_format(time_start,'%Y-%m-%d')) = YEARWEEK(now())-1";
        } elsif ($time_value eq "thismouth") {
            #$condition = "time_start >= DATE_SUB(CURRENT_DATE(),INTERVAL 1 MONTH)";
            $condition = "date_format(time_start,'%Y-%m')=date_format(now(),'%Y-%m')";
        } elsif ($time_value eq "lastmouth") {
            #$condition = "time_start >= DATE_SUB(CURRENT_DATE(),INTERVAL 2 MONTH) and time_end < DATE_SUB(CURRENT_DATE(),INTERVAL 1 MONTH)";
            $condition = "date_format(time_start,'%Y-%m')=date_format(DATE_SUB(curdate(), INTERVAL 1 MONTH),'%Y-%m')";
        } elsif ($time_value eq "thisseason") {
            #$condition = " time_start >= DATE_SUB(CURRENT_DATE(),INTERVAL 1 QUARTER)";
            $condition = "QUARTER(time_start)=QUARTER(now())";
        } elsif ($time_value eq "lastseason") {
            #$condition = "time_start >= DATE_SUB(CURRENT_DATE(),INTERVAL 2 QUARTER) and time_end < DATE_SUB(CURRENT_DATE(),INTERVAL 1 QUARTER)";
            $condition = "QUARTER(time_start)=QUARTER(DATE_SUB(now(),interval 1 QUARTER))";
        } else {
            # lastday lastweek lastmonth
            # 前N天   N周      N月
            my $n = 0;
            if ($time_value =~ /lastday_(\d+)/) {
                $n = $1;
                $condition = "time_start >= DATE_SUB(CURRENT_DATE,INTERVAL $n DAY)";
            } elsif ($time_value =~ /lastweek_(\d+)/) {
                $n = $1 * 7;
                $condition = "time_start >= DATE_SUB(CURRENT_DATE,INTERVAL $n DAY)";
            } elsif ($time_value =~ /lastmonth_(\d+)/) {
                $n = $1;
                $condition = "time_start >= DATE_SUB(CURRENT_DATE,INTERVAL $n MONTH)";
            }
        }
    } elsif ($time_range->{'type'} eq '2') { # 绝对时间
        #yyyy-mm-dd HH:MM:SS
        my $time_start = $time_range->{'value'}->{'time_start'};
        my $time_end   = $time_range->{'value'}->{'time_end'};
        if ($time_start ne "" && $time_end ne "") {
            $condition = "time_start >= \"$time_start\" and time_end <= \"$time_end\"";
        } else {
            if ($time_start ne "") {
                $condition = "time_start >= \"$time_start\"";
            } elsif($time_end ne "") {
                $condition = "time_end <= \"$time_end\"";
            }
        }
    }
    return $condition;
}

#TODO :安全类型
sub generate_safe_type_condition($)
{
    my $safe_type = shift;
    my $condition = "";
    my @conditions;
    my %dict; # translate dict

    if ( $safe_type eq "" || $safe_type eq "all" ) {
        return "";
    }
    my @items = split(/,/ , $safe_type);

    # get translate dict from file


    open FILE ,"<$EVENT_CLASS" or return "";

    foreach my $line (<FILE>) {
        my $chinese_classification;
        my $classification;

        my @tmp = split(",",$line); 
        $chinese_classification = $tmp[0];
        $classification = $tmp[2];
        $dict{$classification} = $chinese_classification;
    }
    close FILE;

    foreach my $item (@items) {
        push(@conditions,"b.chinese_classification = \"$dict{$item}\"");
    }
    $condition = "(" . join(" or ",@conditions) . ")";

    return $condition;
}


# 根据危险等级生成SQL查询用语句
#input : priority(string)
sub generate_priority_condition($)
{
    my $priority = shift;
    my $condition = "";
    if ($priority eq "all" || $priority eq "") {
        return "";
    }
    my @items = split(/,/ , $priority);
    my @conditions; 
    foreach my $item (@items) {
        push(@conditions,"b.priority = $item");
    }
    $condition = "(" . join(" or ",@conditions) . ")";

    return $condition;
}


# 根据IP地址生成SQL查询用语句
#input : ip(list) contains ['ip,searchsrc,searchdst' , ...]
sub generate_ip_condition($)
{
    my $ip = shift;
    my $condition = "";
    my $src_condition = "";
    my $dst_condition = "";
    my $ips_ref = $ip;
    my @ips = @$ips_ref;

    my $ip_addr;
    my $search_src = 0;
    my $search_dst = 0;

    foreach my $ip_str (@ips) {
        ($ip_addr,$search_src,$search_dst) = split(",",$ip_str);
        if ($ip_addr eq '') {
            next;
        }
        if ($search_src eq 'on') {
            if ($ip_addr =~ /(\S+)-(\S+)/) { # ip_range
                $src_condition = "(sip >= INET_ATON('$1') and sip <= INET_ATON('$2'))";
            } else { # ip
                $src_condition = "sip = INET_ATON('$ip_addr')";
            }
            push(@src_conditions,$src_condition);
        }

        if ($search_dst eq 'on') {
            if ($ip_addr =~ /(\S+)-(\S+)/) { # ip_range
                $dst_condition = "(dip >= INET_ATON('$1') and dip <= INET_ATON('$2'))";
            } else { # ip
                $dst_condition = "dip = INET_ATON('$ip_addr')";
            }
            push(@dst_conditions,$dst_condition);
        }
    }

    if (@src_conditions && @dst_conditions) {
        $condition = "( " . join(" or ", @src_conditions) .
                    " ) or ( " .
                    join(" or ",@dst_conditions) . " )";
    } elsif(@src_conditions) {
        $condition = "( ". join(" or ", @src_conditions) ." )";
    } elsif(@dst_conditions) {
        $condition = "( ". join(" or ", @dst_conditions) ." )";
    }

    return $condition;
}

sub generate_user_condition($)
{   
    my $user = shift; 
    my $condition = ""; 
    my $src_condition = "";
    my $dst_condition = "";
    my $users_ref = $user;
    my @users = @$users_ref;
    
    my $user_addr;
    my $search_src = 0;
    my $search_dst = 0;
    
    my @src_conditions = ();
    my @dst_conditions = ();

    foreach my $user_str (@users) {
        ($user_addr,$search_src,$search_dst) = split(",",$user_str);
        $user_addr = decode("utf8",$user_addr);
        if ($user_addr eq ''){ 
            next;
        }
        if ($search_src eq 'on') {
            $src_condition = "src_user = '$user_addr'";
            push(@src_conditions,$src_condition);
        }
        
        if ($search_dst eq 'on') {
            $dst_condition = "dst_user = '$user_addr'";
            push(@dst_conditions,$dst_condition);
        }
    }
    
    if (@src_conditions && @dst_conditions) {
        $condition = "( " . join(" or ", @src_conditions) .
                    " ) or ( " .
                    join(" or ",@dst_conditions) . " )";
    } elsif(@src_conditions) {
        $condition = "( ". join(" or ", @src_conditions) ." )";
    } elsif(@dst_conditions) {
        $condition = "( ". join(" or ", @dst_conditions) ." )";
    }
    
    return $condition;
}

sub generate_port_condition($)
{
    my $port = shift;

    my $condition = "";
    my $src_condition = "";
    my $dst_condition = "";

    my $searchsrc_ref = $port->{'sport'}; #sport是一个数组引用
    my $searchdst_ref = $port->{'dport'}; #searchdst是一个数组引用
    my @searchsrc = @$searchsrc_ref;
    my @searchdst = @$searchdst_ref;

    my @src_conditions = ();
    my @dst_conditions = ();

    foreach my $src (@searchsrc) {
        if ($src =~ /(\S+)-(\S+)/) { # port_range
            $src_condition = "(sport >= $1 and sport <= $2)";
        } else { # single port
            $src_condition = "sport = $src";
        }
        push(@src_conditions,$src_condition);
    }

    foreach my $dst (@searchdst) {
        if ($dst =~ /(\S+)-(\S+)/) { # port_range
            $dst_condition = "(dport >= $1 and dport <= $2)";
        } else { # ip
            $dst_condition = "dport = $dst";
        }
        push(@dst_conditions,$dst_condition);
    }

    if (@src_conditions && @dst_conditions) {
        $condition = "( " . join(" or ", @src_conditions) .
                    " or " .
                    join(" or ",@dst_conditions) . " )";
    } elsif(@src_conditions) {
        $condition = "( ". join(" or ", @src_conditions) ." )";
    } elsif(@dst_conditions) {
        $condition = "( ". join(" or ", @dst_conditions) ." )";
    }
    return $condition;
}


# (历史查询)获取总页数,以及日志总数
# INPUT: $dbh database handler
#        $config(hash)
#        TODO: $templete JSON or hash??
sub get_total_page_num($$$)
{
    my $dbh = shift;           #database handler
    my $conf = shift;          #config hash
    my $templete = shift;      #templete name

    my $where_statement = "";
    my $log_count = 0;
    my $page_size = 0;
    my $total_page = 0;

    # 构造where语句
    $where_statement = build_where_statement($conf,$templete);

    my $sql = "SELECT count(a.id) AS count FROM ipslog_merge as a LEFT JOIN t_sid AS b ON a.sid = b.sid" .
              " $where_statement";
    #print "sql is $sql\n";
    my $sth = $dbh->prepare($sql);
    $sth->execute();

    while ( my $list=$sth->fetchrow_hashref()) {
        $log_count = $list->{'count'};
    }
    $page_size = $conf->{'PAGESIZE'}; 
    if( $log_count % $page_size == 0 && $log_count > 0 ) {
        $total_page =int( ( $log_count/$page_size ) );
    } else {
        $total_page =int( ( $log_count/$page_size ) ) + 1;
    }
    #print ">>>>get_total_page over $total_page,$log_count\n";
    
    return ($total_page,$log_count);
}

# 历史日志查询
sub query($$$$$$)
{
    my $dbh = shift;           #database handler
    my $conf = shift;          #config hash
    my $templete = shift;      #templete name
    my $page_num = shift;      #page number to query
    my $total_page = shift;    #current total page can show
    my $array_ref = shift;     #data array ref

    my $where_statement;
    my $sql;
    my $order_by;

    # 处理传入的page_num ,使其合法化
    if ($page_num <= 0) {
        $page_num = 1;
    } elsif ($page_num > $total_page) {
        $page_num = $total_page;
    }

    # 构造where语句
    $where_statement = build_where_statement($conf,$templete);

    # 构造order by 语句
    $order_by = "ORDER BY time_start desc";


    $start_row = ($page_num-1) * $conf->{'PAGESIZE'};

    $sql = "SELECT id,merge_eid,time_start,time_end, sid, INET_NTOA(sip) AS sip,src_user,sport, " .
              "INET_NTOA(dip) AS dip,dst_user,dport,merge_type,action as r_action, count AS merge_count, " . 
              "msg, event_name, chinese_classification, priority, protocol " .
              "FROM " .
              "  (SELECT a.*, " .
              "      b.msg, b.event_name, b.chinese_classification, b.priority, b.protocol " . 
              "   FROM ipslog_merge AS a LEFT JOIN t_sid AS b ON a.sid = b.sid " . 
              "   $where_statement $order_by " . 
              "   LIMIT $start_row, $conf->{'PAGESIZE'}" . 
              "  ) AS t";
    #print $mytime;
    my $sth = $dbh->prepare($sql);
    $sth->execute();

    while ( my $list=$sth->fetchrow_hashref()) {
        push(@$array_ref,$list);
    }
}

# test code
# sub test()
# {
#     my $dbh = connect_sql();
#     my @array = ();
#     intime_query($dbh, 1, "",\@array);
#     print "[";
#     foreach my $entry (@array) {
#         print "{";
#         foreach my $key ( keys %$entry ) {
#             printf "$key:\"$entry->{$key}\",";
#         }
#         print "},";
#     }
#     print "]";

# }
# test();

1;
