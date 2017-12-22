#!/usr/bin/perl
#
#author:zhangzheng
#date:2012-07-23 09:00
#
#

require '/var/efw/header.pl';
require 'logs_common.pl';
use POSIX();

my %cgiparams;
my %logsettings;
my %filterchange;
my %weeks = (
			1 => "星期一",
			2 => "星期二",
			3 => "星期三",
			4 => "星期四",
			5 => "星期五",
			6 => "星期六",
			7 => "星期天"
);
my %levels = (
			1 => "一般",
			2 => "严重",
			3 => "紧急",
			0 => "微小"
);
my $logfile="/var/log/risk/warning/warning.log";
my $countsfile="/var/log/risk/warning/counts";
my $attfile = "/var/efw/risk/warning/attacktype";
my @files = sort(glob("${logfile}-*.gz"));
my $name = "firewall";
my @attlines = read_config_file($attfile);
my @atttype;
foreach my $line (@attlines) {
	my @tmp = split(/,/,$line);
	push(@atttype,$tmp[0]);
}
sub read_config_file($) {
    my @lines;
	my $file=shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
		if ($line) {
			chomp($line);
			$line =~ s/[\r\n]//g;
			push(@lines, $line);
		}
    }
    close (FILE);
    return @lines;
}
&getcgihash(\%cgiparams);
$logsettings{'LOGVIEW_REVERSE'} = 'off';

&readhash("${swroot}/logging/default/settings", \%logsettings);
eval {
    &readhash("${swroot}/logging/settings", \%logsettings);
};

if ($logsettings{'LOGVIEW_SIZE'} =~ /^\d+$/) {
    $viewsize = $logsettings{'LOGVIEW_SIZE'};
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
my 	$date = $today;
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
my @log = ();

my $filter_search = $filter;

###如果筛选词是星期，则保存该key
if ($filter) {	
	foreach my $key (keys %weeks) {
		if ($weeks{$key} =~ $filter) {
			$filter_search = $key;
		}
	}
	###如果筛选词是攻击类型，则返回类型的数值
	for (my $nums=0;$nums<@attlines ;$nums++) {
		if ($attlines[$nums] =~ $filter) {
			$filter_search = $nums;
		}
	}
	###告警等级
	foreach my $key (keys %levels) {
		if ($levels{$key} =~ $filter) {
			$filter_search = $key;
		}
	}
}

&showhttpheaders();

$extraheaders = <<EOF
<script type="text/javascript" src="/include/jquery.js"></script>
<script type="text/javascript" src="/include/ESONCalendar.js"></script>
<link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />
<link rel="stylesheet" href="/include/flotpie.css" type="text/css" />
<script type="text/javascript" src="/include/jquery.flot.js"></script>
<script type="text/javascript" src="/include/jquery.flot.pie.js"></script>
<script type="text/javascript" src="/include/logs_warning.js"></script>
EOF
;

$language = $settings{'LANGUAGE'};
if (-e "/home/httpd/html/include/jquery-calendar-$language.js") {
    $extraheaders .= <<EOF
<script type="text/javascript" src="/include/jquery-calendar-$language.js"></script>
EOF
;
}
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

my $heads = $offset *$viewsize;
my $tempd,$get_line_num;
if ($filter) {
	$tempd=`cat $filestr |grep "$filter_search" -m  $heads|head -n $heads |tail -n $viewsize`;
	$get_line_num=`grep "$filter_search" $filestr |wc -l`;
	if ($filestr =~ /\.gz$/) {
		$get_line_num = `gzip -dc $filestr |grep "$filter_search"| wc -l`;
		$tempd = `gzip -dc $filestr |grep "$filter_search" |head -n $heads |tail -n $viewsize`; 
	}
}
else{
	$tempd=`cat $filestr |head -n $heads |tail -n $viewsize`;
	$get_line_num=`wc -l $filestr`;
	if ($filestr =~ /\.gz$/) {
		$get_line_num = `gzip -dc $filestr | wc -l`;
		$tempd = `gzip -dc $filestr |head -n $heads |tail -n $viewsize`; 
	}
}
$lines = $get_line_num;
@log = split(/\n/,$tempd);
my $totaloffset=POSIX::ceil($lines/$viewsize);
if ($offset > $totaloffset) {
    $offset = $totaloffset;
}


my $start = $viewsize * ($offset-1);
my $prev = $offset+1;
my $next = $offset-1;
my $prevday = $date;
my $nextday = $date;
if ($start < 0) {
	$start = 0;
}
if ($cgiparams{'ACTION'} eq _('Last day') || $cgiparams{'ACTION'} eq _('Next day')) {
	my $daybefore = getDate(stringToDate($date)-86400);
	if (dateToFilestring($daybefore) >= $firstdatestring) {
		$prevday = $daybefore;
	}
	my $dayafter = getDate(stringToDate($date)+86400);
	if (dateToFilestring($dayafter) <= dateToFilestring($today)) {
		$nextday = $dayafter;
	}
}

if ($offset == $totaloffset) {
	$prev = -1;
}
if ($offset == 1) {
	$next = -1;
}
&openpage(_('Firewall log'), 1, $extraheaders);
####发改委项目添加日志删除 by elvis 2012-6-13
&save();
####end
&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
if(-e $logfile)
{
&openbox('100%', 'left', _('log'));
print "<div class='paging-div-header'>";
oldernewer();
print "</div>";

if(read_file($logfile))
{
print "<div class='paging-div-header'>";
pie_display();
print "</div>";
}

printf <<END
<div style="max-height:500px;overflow:auto;margin:25px 0;">
<table width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
<tr>
        <td width='15%' align='center' class='boldbase'><b>%s</b></td>
        <td width='6%' align='center' class='boldbase'><b>%s</b></td>
        <td width='20%' align='center'  class='boldbase'><b>%s</b></td>
        <td width='5%' align='center'  class='boldbase'><b>%s</b></td>
        <td width='15%' align='center'  class='boldbase'><b>%s</b></td>
        <td width='8%' align='center' class='boldbase'><b>%s</b></td>
        <td width='8%' align='center' class='boldbase'><b>%s</b></td>
</tr>
END
,
_('Time'),
_('星期'),
_('告警方式'),
_('告警级别'),
_('告警类型'),
_('IP'),
_('阈值'),
;
my @slice = @log;

if ($logsettings{'LOGVIEW_REVERSE'} eq 'on') { @slice = reverse @slice; }
my $i = 0;
foreach my $line (@log) {
	my @tmp = split(/,/,$line);
	my @times = split(/\s/,$tmp[0]);
	my $time = $times[0]." ".$times[2];
	my $week = $times[1];
	my $method = $tmp[1];
	my $ip = $tmp[2];	
	my $level = $tmp[3];
	my $type = $attlines[$tmp[4]];
	my @type_tmp = split(/,/,$type);
	$type = $type_tmp[0];
	my $threshold = $tmp[5];
	if ($method eq "2") {
		$method = "邮件告警 ".$tmp[6];
	}
	else{
		$method = "界面告警";
	}
    if ($i % 2) {
	print "<tr class='env_thin'>\n";
    } else {
	print "<tr class='odd_thin'>\n";
    }
    printf <<END
	<td align='center'>$time</td>
	<td align='center'>$weeks{$week}</td>
	<td align='center'>$method</td>
	<td align='center'>$levels{$level}</td>
	<td align='center'>$type</td>
	<td align='center'>$ip</td>
	<td align='center'>$threshold</td>\
        </tr>
END
;
    $i++;
}
if ($i==0) {
	no_tr(9,_('Current no content'));
}
print "</table></div>";
####发改委项目添加日志删除 by elvis 2012-6-13
printf <<EOF
		<div class='containter-div-header' style='padding:0px 5px 5px;margin:0px auto 10px;width:95%;text-align:center'>
			<form onsubmit="return confirm('确定要删除当天的日志？')" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input class='net_button' type='submit' style='color: black; background-image: url(\"/images/button.jpg\");' value='删除日志' name='routebutton'>
			<input type="hidden" name="ACTION" value="delete">
			<input type="hidden" name="DATE" value="$date">
			</form>
		</div>
EOF
;
####end

&closebox();
}else{
	note_box();
}

sub note_box()
	{
		&openbox('100%','left',_('风险告警日志'));
		print "<table width=\"100%\">";
		&no_tr(1,"当前尚无日志数据，请查看风险监控功能是否开启！");
		print "</table>";
		&closebox();
	}
&closepage();
sub oldernewer {
    printf <<END
		<div class='page-footer' style='padding:0px 5px 5px;margin:0px auto 10px;width:95%'>
<table width='100%' align='center'>
	<tr>
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<td width='190px'>%s: <input type="text" size="18" name='FILTER' VALUE="$filter"></td>
    <td width='180px'>%s: <input type="text" SIZE="12" id="inputDate" name='DATE' VALUE="$date" />
<script type="text/javascript"> 
    ESONCalendar.bind("inputDate");
</script>

	</td>
    <td  align='left'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
	</form>
    <td  align='right'>
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="DATE" value="$prevday">
    <input type="hidden" name="FILTER" value="$filter">
    <input class='submitbutton' type="submit" style="background:none;border:0;cursor:pointer;" name="ACTION" value='%s' />
	</form>
	</td>
	<td width='2%' align='right'>
END
,
_('Filter'),
_('Jump to Date'),
_('sure'),
_('Last day'),
;
	if ($next != -1) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="OFFSET" value="1">
    <input type="hidden" name="FILTER" value="$filter">
	<input type="hidden" name="DATE" value="$nextday">
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
    <input type="hidden" name="FILTER" value="$filter">
	<input type="hidden" name="DATE" value="$nextday">
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
	<input type="hidden" name="DATE" value="$prevday">
    <input type="hidden" name="FILTER" value="$filter">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/next-page.png">
	</form>
END
,
_('Next page')
;
    } else {
	print "<input class='submitbutton' type='image' name='ACTION' title='"._('Next page')."' src='/images/next-page-off.png'>";
    }
	print "</td><td width='2%'>\n";
	 if ($prev != -1) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="OFFSET" value="$totaloffset">
	<input type="hidden" name="DATE" value="$prevday">
    <input type="hidden" name="FILTER" value="$filter">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/end-page.png">
    </form>
END
,
_('End page')
;
    } else {
	print "<input class='submitbutton' type='image' name='ACTION' title='"._('End page')."' src='/images/end-page-off.png'>";
    }
    printf <<END
		</td>
		<td width='2%'>
		<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input type="hidden" name="DATE" value="$nextday">
		<input type="hidden" name="FILTER" value="$filter">
		<input class='submitbutton' type="submit" style="background:none;border:0;cursor:pointer" name="ACTION" value='%s' />
	</form>
		</td>
		<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<td  align='right' >%s: <input type="text" SIZE="2" name='OFFSET' VALUE="$offset"></td>
        <td  align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
		<input type="hidden" name="FILTER" value="$filter">
		<input type="hidden" name="DATE" value="$prevday">
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
		@log=();
		$offset = 0;
		$totaloffset = 0;
	}
}
###饼图显示结果
sub pie_display(){
	my $datas = get_data();
	printf <<EOF
		 <input type="hidden" value="$datas" id="data00" />
		<table width='100%' align='center' class="ruleslist">
			<tr>
				<td colspan="2" width="25%" class="boldbase">告警攻击类型比例图</td>
				<td colspan="2" width="25%" class="boldbase">告警时间段比例图图</td>
				<td colspan="2" width="25%" class="boldbase">告警设备比例图</td>
				<td colspan="2" width="25%" class="boldbase">入侵防御告警历史统计</td>
			<tr>
				<td class="tdbg"><div id="graph1" class="graph"></div></td><td><div class="labels" id="graph1hover"></div></td>
				<td class="tdbg"><div id="graph2" class="graph"></div></td><td><div class="labels" id="graph2hover"></div></td>
				<td class="tdbg"><div id="graph3" class="graph"></div></td><td><div class="labels" id="graph3hover"></div></td>
				<td class="tdbg"><div id="graph4" class="graph"></div></td><td><div class="labels" id="graph4hover"></div></td>
			</tr>
		</table>
EOF
;
}

sub read_file($)
{
	my $file =shift;
	my $string = "";
	open(MYFILE,"$file");
	foreach my $line (<MYFILE>) 
	{
		chomp($line);
		$line =~ s/\s//g;
		$string .= $line;
	}
	close (MYFILE);
	return $string;
}


###获取饼图所需要的数据包括设备、类型、时间段和入侵告警的数据
###将所有数据整合到一个字符串传入js作处理，设备和告警类型分别记录名称和个数形式为name=value__name=value,时间段和入侵数据只记录个数形式为value&&value&&value，4类数据之间以"|||"隔开
sub get_data(){
	my $attack_data_num,$dev_data_num,$time_data_num,$snort_data_num;
	my %snorts,%devs,%times,%attacks;
	my @data_line = read_config_file($logfile);
	my $devinfo,$attackinfo;
	my $time1=0,$time2=0,$time3=0,$time4=0,$time5=0,$time6=0;
	foreach my $line (@data_line) {
		my @elems = split(/,/,$line);
		if (!$devs{$elems[2]}) {
			$devs{$elems[2]} = 1;
		}
		else{
			$devs{$elems[2]}++;
		}
		if (!$attacks{$atttype[$elems[4]]}) {
			$attacks{$atttype[$elems[4]]} = 1;
		}
		else{
			$attacks{$atttype[$elems[4]]}++;
		}
		my @tmp = split(/\s/,$elems[0]);
		$tmp[2] =~ /(\d+):\d+:\d/;
		if ($1 < 4) {
			$time1 ++;
		}
		elsif ($1 < 8) {
			$time2 ++;
		}
		elsif ($1 < 12) {
			$time3 ++;
		}
		elsif ($1 < 16) {
			$time4 ++;
		}
		elsif ($1 < 20) {
			$time5 ++;
		}
		elsif ($1 < 24) {
			$time6 ++;
		}
	}
	##获取攻击数据
	foreach my $key ( sort { $attacks{$b} <=> $attacks{$a} } keys %attacks ) {
		my $value = $attacks{$key};
		if ($attackinfo) {
			$attackinfo = $attackinfo."__".$key."=".$value;
		}
		else{
			$attackinfo = $key."=".$value;
		}
	}
	##获取时间数据
	$time_data_num = "$time1&&$time2&&$time3&&$time4&&$time5&&$time6";
	##获取设备数据
	foreach my $key ( sort { $devs{$b} <=> $devs{$a} } keys %devs ) {
		my $value = $devs{$key};
		if ($devinfo) {
			$devinfo = $devinfo."__".$key."=".$value;
		}
		else{
			$devinfo = $key."=".$value;
		}
	}
	##获取入侵告警数据
	readhash($countsfile,\%snorts);
	$snorts{'total'} =~ s/\.//g;
	$snorts{'pass_alert'} =~ s/\.//g;
	$snorts{'drop_alert'} =~ s/\.//g;
	my $passed = $snorts{'total'} - $snorts{'pass_alert'} - $snorts{'drop_alert'}+0;
	$snort_data_num = "$snorts{'pass_alert'}&&$snorts{'drop_alert'}&&$passed";
	return "$attackinfo|||$time_data_num|||$devinfo|||$snort_data_num";
}