#!/usr/bin/perl
#

#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
#        |         Endian GmbH/Srl                                                     |
#        |         Bergweg 41 Via Monte                                                |
#        |         39057 Eppan/Appiano                                                 |
#        |         ITALIEN/ITALIA                                                      |
#        |         info@endian.it                                                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        | http://www.fsf.org/                                                         |
#        +-----------------------------------------------------------------------------+
#

require '/var/efw/header.pl';
require 'logs_common.pl';
use POSIX();
use CGI ':standard';
use CGI::Carp qw (fatalsToBrowser);
my $log_name = "防火墙";
my $logfile="/var/log/urlfilter";
my @files = sort(glob("${logfile}-*.gz"));
my $name = "firewall";
###定义哈希值，保存部分数据，也就是筛选条件
my %cgiparams;
my %selected;
my %logsettings;
my %filterchange;
my %chaindisplay;
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
my %protocol_hash = (
    "TCP" => "TCP",
    "UDP" => "UDP",
    "ICMP" => "ICMP"
);
my %time_hash = (
    "00|01|02" => "0时-3时",
    "03|04|05" => "3时-6时",
    "06|07|08" => "6时-9时",
    "09|10|11" => "9时-12时",
    "12|13|14" => "12时-15时",
    "15|16|17" => "15时-18时",
    "18|19|20" => "18时-21时",
    "21|22|23" => "21时-24时",
);
my %rule_hash;
$rule_hash{'INCOMINGFW'}="流入防火墙";
$rule_hash{'OUTGOINGFW'}="流出防火墙";
$rule_hash{'ZONEFW'}="区域防火墙";
$rule_hash{'VPNFW'}="VPN防火墙";
$rule_hash{'INPUT'}="系统访问";
$rule_hash{'FORWARD'}="转发";
$rule_hash{'PROX'}="代理";
$rule_hash{'PORTFWACCESS'}="DNAT";
#$rule_hash{'DNAT'}="DNAT";    #过滤的的判断值用的PORTFWACCESS by wl 2013.12.19
#$rule_hash{'SNAT'}="SNAT"; #SNAT没有日志记录功能 by wl 2013.12.19
my %action_hash;
#$action_hash{'ALLOW'}="通过入侵防御";
$action_hash{'DROP'}="丢弃";
$action_hash{'ACCEPT'}="允许";
$action_hash{'REJECT'}="拒绝";

my $eth_all = `ifconfig |grep eth`;
my @temp = split(/\n/,$eth_all);
my @eths;
foreach my $elem(@temp){
    $elem =~ /(eth\d+)\s*/;
    push(@eths,$1);
}
push(@eths,"br0");
push(@eths,"br1");
&getcgihash(\%cgiparams);
$logsettings{'LOGVIEW_REVERSE'} = 'off';

&readhash("${swroot}/logging/default/settings", \%logsettings);
eval {
    &readhash("${swroot}/logging/settings", \%logsettings);
};

foreach $key (keys %chaindisplay) {
    $filterchange{$chaindisplay{$key}}=$key;
}
$filterchange{'非SYN连接'}="NEW not SYN?";
$filterchange{"系统访问"}="INPUT";
if ($logsettings{'LOGVIEW_SIZE'} =~ /^\d+$/) {
    $viewsize = $logsettings{'LOGVIEW_SIZE'};
}

######获取筛选条件，并赋值
my $src_ip = $cgiparams{'src_ip'};
my $dst_ip = $cgiparams{'dst_ip'};
my $dst = $cgiparams{'dst'};
$selected{$cgiparams{'times'}} = "selected";
$selected{$cgiparams{'actions'}} = "selected";
$selected{$cgiparams{'rules'}} = "selected";
$selected{$cgiparams{'protocols'}} = "selected";
$selected{$cgiparams{'ifaces'}} = "selected";
if (!validip($src_ip) && $src_ip) {
    $errormessage = "无效的源IP地址";
    $src_ip = "";
}
if (!validip($dst_ip) && $dst_ip) {
    $errormessage = "无效的目的IP地址";
    $dst_ip = "";
}
my $hidden_class = "
    <input type='hidden' name='src_ip' value='$src_ip'>
    <input type='hidden' name='dst_ip' value='$dst_ip'>
    <input type='hidden' name='times' value='$cgiparams{'times'}'>
    <input type='hidden' name='actions' value='$cgiparams{'actions'}'>
    <input type='hidden' name='rules' value='$cgiparams{'rules'}'>
    <input type='hidden' name='protocols' value='$cgiparams{'protocols'}'>
    <input type='hidden' name='ifaces' value='$cgiparams{'ifaces'}'>

    ";
sub get_filter(){
    my $filter_search = "";
    if ($cgiparams{'rules'}) {
        $filter_search .= ".*$cgiparams{'rules'}";
    }
    if ($cgiparams{'actions'}) {
       $filter_search .= ".*$cgiparams{'actions'}";
    }
    if ($cgiparams{'ifaces'}) {
       $filter_search .= ".*$cgiparams{'ifaces'}";
    }
    if ($src_ip) {
       $filter_search .= ".*SRC=$src_ip";
    }
    if ($dst_ip) {
       $filter_search .= ".*DST=$dst_ip";
    }
    if ($dst) {
       $filter_search .= ".*$dst";
    }
    if ($cgiparams{'protocols'}) {
       $filter_search .= ".*PROTO=$cgiparams{'protocols'}";
    }
    $filter_search = "/".$filter_search."/";
    if ($cgiparams{'times'}) {
        $filter_search .=  " {if(\$3~/^($cgiparams{'times'})/)  print }";
    }
    $filter_search =~s/^\/\.\*/\//;
    return     $filter_search;
}
sub getDate($) {
    my $now = shift;
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($now);
    $year += 1900;
    $mon++;
    return sprintf("%04d-%02d-%02d", $year, $mon, $mday);
}

sub dateToFilestring($) {
    my $date = shift;
    $date =~ s/\-//g;
    return $date;
}

sub dateToArray($) {
    my $date = shift;
    $date =~ s/\-//g;
    my @datearr = ($date =~ /^(\d{4})(\d{2})(\d{2})$/);
    return \@datearr;
}

sub stringToDate($) {
    my $date = shift;
    my $arr = dateToArray($date);
    return $lala = mktime(0, 0, 0, @$arr[2], @$arr[1] - 1, @$arr[0] - 1900);
}

my $today = getDate(time);
my     $date = $today;
if ($cgiparams{'DATE'} =~ /[\d\/]+/) {
    $date = $cgiparams{'DATE'};
}
my $years; 
my @t = split(/-/,$date);
$years=$t[0];
my $day_length = length($t[2]);
#changed by elvis on 6.13 for month-value
my $month_length = length($t[1]);
if ($month_length == 1) {
    $t[1] = "0".$t[1];
    $date = "$t[0]-$t[1]-$t[2]";
}
#end
if ($day_length == 1) {
    $t[2] = "0".$t[2];
    $date = "$t[0]-$t[1]-$t[2]";
}
my $filter = $cgiparams{'FILTER'};
if($filter =~/\(|\)|\[|\]|\*/){
    $errormessage = "筛选关键字中包含系统屏蔽的非法字符";
    $filter = "";
}

my $filetotal=scalar(@files);
my $filetotal1 = 2;
my ($firstdatestring) = ($files[0] =~ /\-(\d+).gz$/);
if ($firstdatestring eq '') {
    $firstdatestring = dateToFilestring($today);
}

if ((dateToFilestring($date) < $firstdatestring) || (dateToFilestring($date) > dateToFilestring($today))) {
        
    $errormessage = _('Please select date between "%s" and "%s" ,now goto logs file for today!',$firstdatestring,dateToFilestring($today));
    $date = $today;
}

my $filestr = $logfile;
if ($date ne $today) {
    $filestr="${logfile}-".dateToFilestring($date).".gz";
}
my $hostname = $settings{'HOSTNAME'};

if (!(open (FILE,($filestr =~ /.gz$/ ? "gzip -dc $filestr |" : $filestr)))) {
    #$errormessage = _('No (or only partial) logs exist for the given day')."!";
}

my $lines = 0;
###新增日志导出功能 by elvis 2012-8-28
down_file($filestr,$cgiparams{'ACTION'},$date,$log_name);
&showhttpheaders();

$extraheaders = <<EOF
<script type="text/javascript" src="/include/jquery.js"></script>
<script type="text/javascript" src="/include/ESONCalendar.js"></script>
<script type="text/javascript" src="/include/jsencrypt.min.js"></script>
<script type="text/javascript" src="/include/logs_delete.js"></script>
<link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />

EOF
;

####按时间排序或反序的代码
my $status = "up";
my $unstatus = 'down';
my $alt = "点击按时间反序";
if ($cgiparams{'status'} eq 'down') {
    $status = "down";
    $unstatus = 'on';
    $alt = "点击按时间排序";
}
my $sort_time = "<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}' style='display:inline'>";
$sort_time .= "<input class='submitbutton' type='image' name='ACTION' title='$alt' src='/images/stock_$status-16.png'>";
$sort_time .= "<input type='hidden' name='DATE' value='$date'><input type='hidden' name='status' value='$unstatus'>$hidden_class</form>";
####按时间排序或反序的代码结束
my $firstdatearr = dateToArray($firstdatestring);
my $lastdatearr = dateToArray($today);

my $offset = 1;
if ($cgiparams{'OFFSET'} =~ /^\d+$/) {
    $offset = $cgiparams{'OFFSET'};
}
elsif($cgiparams{'OFFSET'}){
    $errormessage = "跳转页面必须输入整数,请重新输入,现在跳转到首页.";
}
if ($offset < 1) {
    $offset = 1;
}
if ($offset > $cgiparams{'totaled'} && $cgiparams{'totaled'}) {
    $offset = $cgiparams{'totaled'};
}
####这部分在读文件了

my $filter_search = get_filter();
`echo "$filter_search" >/tmp/dnatfilter`;
my $heads = ($offset - 1) * $viewsize + 1;
my $ends = ($heads +  $viewsize - 1) . "p";
my $tempd,$get_line_num;
if ($cgiparams{'status'} eq 'down') {
    if ($filter_search ne "//") {
        $tempd=`awk '$filter_search' $filestr|sort -r|sed -n $heads,$ends`;
        $get_line_num=`awk '$filter_search' $filestr |wc -l`;
        if ($filestr =~ /\.gz$/) {
            $get_line_num = `gzip -dc $filestr |awk '$filter_search'| wc -l`;
            $tempd = `gzip -dc $filestr |awk '$filter_search' |sort -r|sed -n $heads,$ends`; 
        }
    }
    else{
        $tempd=`tac $filestr |sed -n $heads,$ends`;
        $get_line_num=`wc -l $filestr`;
        if ($filestr =~ /\.gz$/) {
            $get_line_num = `gzip -dc $filestr | wc -l`;
            $tempd = `gzip -dc $filestr |sort -r|sed -n $heads,$ends`; 
        }
    }    
}
else{
    if ($filter_search ne "//") {
        $tempd=`awk '$filter_search' $filestr|sed -n $heads,$ends`;
        $get_line_num=`awk '$filter_search' $filestr |wc -l`;
        if ($filestr =~ /\.gz$/) {
            $get_line_num = `gzip -dc $filestr |awk '$filter_search'| wc -l`;
            $tempd = `gzip -dc $filestr |awk '$filter_search' |sed -n $heads,$ends`; 
        }
    }
    else{
        $tempd=`sed -n $heads,$ends $filestr`;
        $get_line_num=`wc -l $filestr`;
        if ($filestr =~ /\.gz$/) {
            $get_line_num = `gzip -dc $filestr | wc -l`;
            $tempd = `gzip -dc $filestr |sed -n $heads,$ends`; 
        }
    }
}
$lines = $get_line_num;
@log = split(/\n/,$tempd);
###文件内容读取完毕

####新的读取文件方式
sub read_log_file($$$){    
    my $viewsize = shift;
    my $offset = shift;
    my $filestr = shift;
    my @log;
    my $start_line = ($offset - 1)  * $viewsize;
    my $end_line = $offset * $viewsize;
    my $num = 0;
    if (!(open (FILE,($filestr =~ /.gz$/ ? "gzip -dc $filestr |" : $filestr)))) {
        $errormessage = "读取日志文件失败，请重试!";
    }
    foreach my $line(<FILE>){
        if(!$src_ip && !$dst_ip && !$cgiparams{'times'} && !$cgiparams{'actions'} && !$cgiparams{'rules'} && !$cgiparams{'protocols'} && !$cgiparams{'ifaces'}){
            if ($lines >= $start_line && $lines < $end_line && $line =~ /SRC=/) {
                push(@log,$line);
                $num++;
            }
            $lines++;
        }

    }
    close(FILE);
    return @log;
}



#my @log = read_log_file($viewsize,$offset,$filestr);
my $totaloffset=POSIX::ceil($lines/$viewsize);
if ($offset > $totaloffset) {
    $offset = $totaloffset;
}

my $prev = $offset+1;
my $next = $offset-1;
my $prevday = $date;
my $nextday = $date;

#if ($cgiparams{'ACTION'} eq _('Last day') || $cgiparams{'ACTION'} eq _('Next day')) {
    my $daybefore = getDate(stringToDate($date)-86400);
    if (dateToFilestring($daybefore) >= $firstdatestring) {
        $prevday = $daybefore;
    }
    my $dayafter = getDate(stringToDate($date)+86400);
    if (dateToFilestring($dayafter) <= dateToFilestring($today)) {
        $nextday = $dayafter;
    }
#}

if ($offset == $totaloffset) {
    $prev = -1;
}
if ($offset == 1) {
    $next = -1;
}

&openpage(_('Firewall log'), 1, $extraheaders);

####发改委项目添加日志删除 by elvis 2012-6-13
&save();####end

&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&openbox('100%', 'left', _('log'));
print "<div class='paging-div-header'>";
oldernewer();
print "</div>";

printf <<END
<div style="max-height:500px;overflow:auto;margin:25px 0;">
<table width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
<tr>
        <td width='18%' align='center' class='boldbase'><b>%s $sort_time</b></td>
        <td width='7%' align='center'  class='boldbase'><b>%s</b></td>
        <td width='6%' align='center'  class='boldbase'><b>%s</b></td>
        <td width='6%' align='center' class='boldbase'><b>%s</b></td>
        <td width='20%' align='center' class='boldbase'><b>%s</b></td>
        <td width='20%' align='center' class='boldbase'><b>%s</b></td>
</tr>
END
,
_('Time'),
_('第几条'),
_('流入口'),
_('流出口'),
_('Source'),
_('Destination'),
;

if ($logsettings{'LOGVIEW_REVERSE'} eq 'on') { @slice = reverse @slice; }
my $i = 0;
foreach my $line (@log) {
    $line =~ /(^... .. ..:..:..) [\w\-]+ ulogd\[.*\]:(.*)(IN=.*)$/;
    my $timestamp = $1; my $comment = $2; my $packet = $3;
    $timestamp = change_time($timestamp);
    $timestamp =~s/^\s//;
    $timestamp = $years."-".$timestamp;
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
    my $len = @chaintemp;
    if($len eq 4){    
        for(my $i=0;$i<$len;$i++) {
            if($i eq 0){
                $chaintemp[$i] = 'URL过滤';
            }
            if($i eq 2){
                if($chaintemp[$i] eq 'DROP'){
                    $chaintemp[$i] = '丢弃';
                }elsif($chaintemp[$i] eq 'REJECT'){
                    $chaintemp[$i] = '拒绝';
                }elsif($chaintemp[$i] eq 'ACCEPT'){
                    $chaintemp[$i] = '接受';
                }else{
                    $chaintemp[$i] = '其他';
                }
                $chaintemp[$i] = "<b>".$chaintemp[$i]."</b>";
            }
        }
        $chaintemp[3]=~s/\s//g;
        if ($chaintemp[3] && $chaintemp[3]=~/^\d+$/) {
            $chaintemp[3]="第$chaintemp[3]条";
        }
        else{
            $chaintemp[3] = "默认规则";
        }
    }else{
        $chaintemp[4]=~s/\s//g;
        if ($chaintemp[4] && $chaintemp[4]=~/^\d+$/) {
            $chaintemp[4]="第$chaintemp[4]条";
        }
        else{
            $chaintemp[4] = "默认规则";
        }
    }
        
        if (!$chaintemp[0]) {
            $chaintemp[0] = "其他";
        }
        if (!$chaintemp[2]) {
            $chaintemp[2] = "其他";
        }
        if ($i % 2) {
        print "<tr class='env_thin'>\n";
        } else {
        print "<tr class='odd_thin'>\n";
        }
        if($len eq 4){
        printf <<END
        <td align='center'>$timestamp</td>
        <td align='center'>$chaintemp[3]</td>
        <td align='center'>$in_iface</td>
        <td align='center'>$out_iface</td>
        <td align='center'>$printsrcaddr</td>
        <td align='center'>$chaintemp[1]</td>
        </tr>
END
;
        }else{
        my $des_data = $chaintemp[1].':'.$chaintemp[2];
        printf <<END
        <td align='center'>$timestamp</td>
        <td align='center'>$chaintemp[4]</td>
        <td align='center'>$in_iface</td>
        <td align='center'>$out_iface</td>
        <td align='center'>$printsrcaddr</td>
        <td align='center'>$des_data</td>
        </tr>
END
;
        }
        
    
    $i++;
}
if ($i==0) {
    if ($cgiparams{'FILTER'}) {
        no_tr(9,"无筛选结果，请区分大小写且尽量按全词筛选!");
    }
    else{
        no_tr(9,_('Current no content')); 
    }
}
print "</table></div>";
turn_page();
my $filestr_change = $filestr;
$filestr_change =~s/\//_/g;
####发改委项目添加日志删除 by elvis 2012-6-13
printf <<EOF
        <div class='containter-div-header' style='padding:0px 5px 5px;margin:0px auto 10px;width:95%;text-align:center'>
          <table><tr><td style="text-align:right">
              <input class='net_button' type='submit' style='color: black; background-image: url(\"/images/button.jpg\");' value='删除日志' onclick="warning_box('$filestr_change')" name='routebutton'>
            </td><td style="text-align:left">
            <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
            <input class='net_button' type='submit' style='color: black; background-image: url(\"/images/button.jpg\");' value='导出日志' name='routebutton'>
            <input type="hidden" name="ACTION" value="download">
            </form></td></tr></table>
        </div>
EOF
;
####end
&closebox();
&closebigbox();

&closepage();
sub oldernewer {
    printf <<END
        <div class='page-footer' style='padding:0px 0px;margin:0px auto ;width:100%'>
<table width='100%' align='center'>
    <tr>
    <form enctype='multipart/form-data' method='post' name="SEARCH_FORM" action='$ENV{'SCRIPT_NAME'}'>
    <td>%s: <input type="text" SIZE="12" id="inputDate" name='DATE' VALUE="$date"/>
<script type="text/javascript"> 
    ESONCalendar.bind("inputDate");
</script>

    </td>
    <td  align='left'>时间 <select name="times" >
    <option value=''>任意</option>
END
,
_('选择日期')
;
    foreach my $key(sort {$a<=>$b} keys %time_hash){
        print "<option value='$key' $selected{$key}>$time_hash{$key}</option>";
    }
    printf <<END
    </select> </td>
    <!--<td  align='left'>规则 <select name="rules" >
    <option value=''>任意</option>-->
END
;
    # foreach my $key(keys %rule_hash){
        # print "<option value='$key' $selected{$key}>$rule_hash{$key}</option>";
    # }
    printf <<END
    <!--</select> </td>
    <td  align='left'>动作 <select name="actions" >
    <option value=''>任意</option>-->
END
;
    # foreach my $key(keys %action_hash){
        # print "<option value='$key' $selected{$key}>$action_hash{$key}</option>";
    # }
    printf <<END
    <!--</select> </td>
    <td  align='left'>协议 <select name="protocols" >
    <option value=''>任意</option>-->
END
;
    # foreach my $key(keys %protocol_hash){
        # print "<option value='$key' $selected{$key}>$protocol_hash{$key}</option>";
    # }
    printf <<END
    </select> </td>
    <td  align='left'>接口 <select name="ifaces" >
    <option value=''>任意</option>
END
;
    foreach my $key(@eths){
        print "<option value='$key' $selected{$key}>$key</option>";
    }
    printf <<END
    </select> </td>
    <td  align='left'>源 <input type='text' name='src_ip' value='$src_ip' width='5%'/></td>
    <td  align='left'>目标 <input type='text' name='dst' value='$dst' /></td>
    <td  align='left'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
    </form>
    
    </tr>
</table>
    
    </div>
END
,
_('sure'),
;

}
sub turn_page(){
    #####翻页的代码以及跳转页面的代码
printf <<END

    <div class='page-footer' style='padding:0px 5px;margin:0px auto ;width:95%;border-top:1px solid #999;'>
    <table width='100%' align='center'>
    <tr>
        <td width='40%' align='right'>
        <td  align='right'>
        <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type="hidden" name="DATE" value="$prevday">
        $hidden_class
        <input class='submitbutton' type="submit" style="background:none;border:0;cursor:pointer" name="ACTION" value='上一天' />
        </form>
        </td>
        <td width='2%' align='right'>
END
,
;
    if ($next != -1) {
printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="1">
    <input type="hidden" name="DATE" value="$date">
    <input type='hidden' name='status' value='$status'>
    $hidden_class
    <input class='submitbutton' type="image" title='%s' name="ACTION" src="/images/first-page.png">
    </form>
END
,
_('First page')
;
    } else {

    print "<input class='submitbutton' type='image' name='ACTION' title='"._('First page')."' src='/images/first-page-off.png'>";
    }
    print "</td><td width='2%'>\n";
    if ($next != -1) {
printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$next">
    <input type="hidden" name="DATE" value="$date">
    <input type='hidden' name='status' value='$status'>
    $hidden_class
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/last-page.png">
    </form>
END
,
_('Last page')
;
    }
    else {

    print "<input class='submitbutton' type='image' name='ACTION' title='"._('Last page')."' src='/images/last-page-off.png'>";
    }
    printf <<END
        <td  align='center'>%s</td>
        <td  align='center'>%s</td>
END
,
_('Total %s pages',$totaloffset),
_('Current %s page',$offset),
;

    print "<td width='2%' align='right'>";
    if ($prev != -1) {
printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$prev">
    <input type="hidden" name="DATE" value="$date">
    <input type='hidden' name='status' value='$status'>
    $hidden_class
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/next-page.png">
    </form>
END
,
_('Next page')
;
    } 
    else {
        print "<input class='submitbutton' type='image' name='ACTION' title='"._('Next page')."' src='/images/next-page-off.png'>";
    }
    print "</td><td width='2%'>\n";
     if ($prev != -1) {
printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$totaloffset">
    <input type="hidden" name="DATE" value="$date">
    <input type='hidden' name='status' value='$status'>
    $hidden_class
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/end-page.png">
    </form>
END
,
_('End page')
;
    } 
    else {
        print "<input class='submitbutton' type='image' name='ACTION' title='"._('End page')."' src='/images/end-page-off.png'>";
    }
    printf <<END
        </td>
        <td width='2%'>
        <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type="hidden" name="DATE" value="$nextday">
        $hidden_class
        <input class='submitbutton' type="submit" style="background:none;border:0;cursor:pointer" name="ACTION" value='%s' />
        </form>
        </td>
        <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <td  align='right' >%s: <input type="text" SIZE="8" name='OFFSET' VALUE="$offset"></td>
        <td  align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
        <input type="hidden" name="DATE" value="$date">
        <input type='hidden' name='status' value='$status'>
        <input type="hidden" name="totaled" value="$totaloffset">
        $hidden_class
        </form>
    </tr>
    </table>
    </div>
END
,
_('Next day'),
_('Jump to Page'),
_('Go')
;
}
####发改委项目添加日志删除 by elvis 2012-6-13
sub save(){
    if ($cgiparams{'ACTION'} eq "delete") {
        system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl $filestr");
        my $log_message = "删除了$date的$log_name日志";
        &user_log($log_message);
        @log=();
        $offset = 0;
        $totaloffset = 0;
    }
}
