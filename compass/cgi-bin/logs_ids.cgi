#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# Copyright (C) 18-03-2002 Mark Wormgoor <mark@wormgoor.com>
#              - Added links to Snort database and ipinfo.cgi
#
# $Id: ids.dat,v 1.6.2.2 2004/09/15 13:27:09 alanh Exp $
#
require '/var/efw/header.pl';
require 'logs_common.pl';
use POSIX();
use CGI ':standard';
use CGI::Carp qw (fatalsToBrowser);
my $log_name = "入侵防御";
my %cgiparams;
my %logsettings;

my $logfile="/var/log/snort/alert";
my @files = sort(glob("${logfile}-*.gz"));
my $name = "ids";
my $filter_search;

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
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
	localtime($now);
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
my $_v = "";
$filter_search = $cgiparams{'FILTER'};
###将中文搜索换位文件字段
if ($filter =~ /阻|断/) {
	$filter = "[Drop]";
}
elsif ($filter =~ /阻|断/) {
	$filter = "Drop";
	$_v = "-v";
}
elsif ($filter eq "低") {
	$filter = "Priority: 3";
}
elsif ($filter eq "中") {
	$filter = "Priority: 2";
}
elsif ($filter eq "高") {
	$filter = "Priority: 1";
}
elsif ($filter eq "TCP") {
	$filter = "ICMP";
}
my $filetotal=scalar(@files);

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

my $lines = 0;
my ($title,$classification,$priority,$time,$srcip,$srcport,$destip,$destport, $sid, @refs);


###新增日志导出功能 by elvis 2012-8-28
down_file($filestr,$cgiparams{'ACTION'},$date,$log_name);
&showhttpheaders();

$extraheaders = <<EOF
<script type="text/javascript" src="/include/jquery.js"></script><script type="text/javascript" src="/include/ESONCalendar.js"></script>
<link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />

EOF
;
 
$language = $settings{'LANGUAGE'};
if (-e "/home/httpd/html/include/jquery-calendar-$language.js") {
    $extraheaders .= <<EOF
<script type="text/javascript" src="/include/jquery-calendar-$language.js"></script>
EOF
;
}
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
$sort_time .= "<input type='hidden' name='DATE' value='$date'><input type='hidden' name='status' value='$unstatus'><input type='hidden' name='FILTER' value='$filter'></form>";

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
if ($offset > $cgiparams{'totaled'} && $cgiparams{'totaled'} ) {
    $offset = $cgiparams{'totaled'};
}
my $heads = $offset * $viewsize;
my $tails = $viewsize;
my $tempd,$get_line_num;
if ($cgiparams{'status'} eq 'down') {
	if ($filter) {
		if ($filestr =~ /\.gz$/) {
			$get_line_num = `gzip -dc $filestr |grep "$filter"| wc -l`;
			if ($heads > $get_line_num) {
				$tails = $get_line_num - ($offset - 1) * $viewsize;
			}
			$tempd = `gzip -dc $filestr |grep "$filter" |sort -r|head -n $heads |tail -n $tails`; 
		}
		else{
			$get_line_num=`grep "$filter" $filestr |wc -l`;
			if ($heads > $get_line_num) {
				$tails = $get_line_num - ($offset - 1) * $viewsize;
			}
			$tempd=`tac $filestr |grep "$filter" -m  $heads|head -n $heads |tail -n $tails`;
		}		
	}
	else{
		if ($filestr =~ /\.gz$/) {
			$get_line_num = `gzip -dc $filestr | wc -l`;
			if ($heads > $get_line_num) {
				$tails = $get_line_num - ($offset - 1) * $viewsize;
			}
			$tempd = `gzip -dc $filestr |sort -r|head -n $heads |tail -n $tails`; 
		}
		else{
			$get_line_num=`wc -l $filestr`;
			if ($heads > $get_line_num) {
				$tails = $get_line_num - ($offset - 1) * $viewsize;
			}
			$tempd=`tac $filestr |head -n $heads |tail -n $tails`;
		}
	}	
}
else{
	if ($filter) {
		if ($filestr =~ /\.gz$/) {
			$get_line_num = `gzip -dc $filestr |grep "$filter"| wc -l`;
			if ($heads > $get_line_num) {
				$tails = $get_line_num - ($offset - 1) * $viewsize;
			}
			$tempd = `gzip -dc $filestr |grep "$filter" |head -n $heads |tail -n $tails`; 
		}
		else{
			$get_line_num=`grep "$filter" $filestr |wc -l`;
			if ($heads > $get_line_num) {
				$tails = $get_line_num - ($offset - 1) * $viewsize;
			}
			$tempd=`cat $filestr |grep "$filter" -m  $heads|head -n $heads |tail -n $tails`;
		}
		
	}
	else{
		if ($filestr =~ /\.gz$/) {
			$get_line_num = `gzip -dc $filestr | wc -l`;
			if ($heads > $get_line_num) {
				$tails = $get_line_num - ($offset - 1) * $viewsize;
			}
			$tempd = `gzip -dc $filestr |head -n $heads |tail -n $tails`; 
		}
		else{
			$get_line_num=`wc -l $filestr`;
			if ($heads > $get_line_num) {
				$tails = $get_line_num - ($offset - 1) * $viewsize;
			}
			$tempd=`cat $filestr |head -n $heads |tail -n $tails`;				
		}		
	}
}
$lines = $get_line_num;
@log = split(/\n/,$tempd);
#print "$lines,$nums,$heads,$tails,$viewsize";
my @dis_log;
foreach my $line (@log) {
	chomp($line);
	if (($filter !~ /^$/) && ($line !~ /$filter/)) {
	    next;
	}
	#$i++;
	my ($title,$classification,$priority,$date,$time,$srcip,$srcport,$destip,$destport,$sid,$protocol) = ("n/a","Preproccess","n/a","n/a","n/a","n/a","n/a","n/a","n/a","n/a","n/a");
	@refs = ();
	if ($line =~ m/:[0-9]{1,4}\] ([^\[{]*)/) {
	    $title = &cleanhtml($1,"y");
	}

	if ($line =~ m/Classification: (.*)\] \[Priority: (\d)\] \{(.*)\}/) {
	    $classification = &cleanhtml($1,"y");
	    $priority = $2;
		$portocal = $3;
	}
	if ($line =~ /\[Priority: (\d)\] \{(.*)\}/) {
		$priority = $1;
		$portocal = $2;
	}
	if ($line =~ m/([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}) \-\> ([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})/) {
	    $srcip = $1 . "." . $2 . "." . $3 . "." . $4;
	    $destip = $5 . "." . $6 . "." . $7 . "." . $8;
	}
	if ($line =~ m/([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\:([0-9]{1,6}) \-\> ([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\:([0-9]{1,6})/) {
	    $srcip = $1 . "." . $2 . "." . $3 . "." . $4;
	    $srcport = $5;
	    $destip = $6 . "." . $7 . "." . $8 . "." . $9;
	    $destport = $10;
	}

	if ($line  =~ m/^(\d+\/\d+\/\d+)-(\d{2}:\d{2}:\d{2})\./) {
	    ($date,$time) = ($1,$2);
	}
	if ($line =~ m/\[Xref \=\>.*\]/) {
	    $line =~ s/\]\[Xref \=\> /, /g;
	    $line =~ m/\[Xref \=\> (.*)\]/;
	    push(@refs, $1);
	}
	if ($line =~ m/\[([0-9]+):([0-9]+):[0-9]+\]/) {
		if ($1 == 1) {
			$sid = $2;
		}
		else{$sid = $1.":".$2}
	}
	#检测到[Drop],设置动作为丢弃，否则默认警报
	$action = "告警";
	if($line =~ /\[Drop\]/) {
	  $action = "阻断";
	}
	$i++;
	my $temp = "$date $time|$title|$priority|$classification|$srcip|$srcport|$destip|$destport|$sid|$portocal|$action";
	push(@dis_log,$temp);
}
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

&openpage(_('IDS log viewer'), 1, $extraheaders);
####发改委项目添加日志删除 by elvis 2012-6-13
&save();
####end
&openbigbox($errormessage, $warnmessage, $notemessage);

&openbox('100%', 'left', _('log'));
print "<div class='paging-div-header'>";
oldernewer();
print "</div>";
printf <<END
<div style="max-height:500px;overflow:auto;margin:25px 0;">
<table width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
<tr>
        <td width='15%' align='center' class='boldbase'><b>%s</b> $sort_time</td>
        <td width='24%' align='center' class='boldbase'><b>%s</b></td>
        <td width='7%' align='center' class='boldbase'><b>%s</b></td>
        <td width='11%' align='center' class='boldbase'><b>%s</b></td>
		<td width='8%' align='center' class='boldbase'><b>%s</b></td>
        <td width='25%' align='center' class='boldbase'><b>%s</b></td>
        <td width='5%' align='center' class='boldbase'><b>%s</b></td>
        <td width='5%' align='center' class='boldbase'><b>%s</b></td>
</tr>
END
,
_('Date'),
_('入侵描述'),
_('危险级'),
_('入侵类型'),
_('动作'),
_('源 -> 目标'),
'ID',
_('Protocol'),
;

my %prece=(
	"0" => "超高",
	"1" => "高",
	"2" => "中",
	"3" => "低",
	"n/a" => "低"
);
my $i = 0;
foreach my $line (@dis_log) {
    if ($i % 2) {
	print "<tr class='env_thin'>\n";
    } else {
	print "<tr class='odd_thin'>\n";
    }
    my ($datetime,$title,$priority,$classification,$srcip,$srcport,$destip,$destport,$sid,$protocol,$action) = split(/\|/, $line);
  	$datetime =~ m/(\d+)\/(\d+)\/(\d+)\s(\d{2}:\d{2}:\d{2})/;
  	$years = $3;
  	$datetime = "$1-$2 $4";
	$datetime = $years."-".$datetime;

	my $src_dst="$srcip:$srcport -> $destip:$destport";
	$src_dst =~s/:n\/a//g;
	$title=~s/\(snort decoder\)//g;
    printf <<END
		<td align='center'>$datetime</td>
		<td align='center'>$title</td>
		<td align='center'>$prece{$priority}</td>
		<td align='center'>$classification</td>
		<td align='center'>$action</td>
		<td align='center'>$src_dst</td>
		<td align='center'>$sid</td>
		<td align='center'>$protocol</td>
</tr>
END
;
    $i++;
}
if ($i==0) {
	no_tr(8,_('Current no content'));
}
print "</table></div>";
####发改委项目添加日志删除 by elvis 2012-6-13
printf <<EOF
		<div class='containter-div-header' style='padding:0px 5px 5px;margin:0px auto 10px;width:95%;text-align:center'>
			<table><tr><td style="text-align:right">
			<form onsubmit="return confirm('确定要删除当天的日志？')" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input class='net_button' type='submit' style='color: black; background-image: url(\"/images/button.jpg\");' value='删除日志' name='routebutton'>
			<input type="hidden" name="ACTION" value="delete">
			<input type="hidden" name="DATE" value="$date">
			</form></td><td style="text-align:left">
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
		<div class='page-footer' style='padding:0px 5px 5px;margin:0px auto 10px;width:95%'>
<table width='100%' align='center'>
	<tr>
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<td width='190px'>%s: <input type="text" size="18" name='FILTER' VALUE="$filter_search"></td>
    <td width='180px'>%s: <input type="text" SIZE="12" id="inputDate" name='DATE' VALUE="$date" />
<script type="text/javascript"> ESONCalendar.bind("inputDate");</script>

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
	<input type="hidden" name="DATE" value="$date">
	<input type='hidden' name='status' value='$status'>
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
	<input type="hidden" name="DATE" value="$date">
	<input type='hidden' name='status' value='$status'>
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
    <input type="hidden" name="FILTER" value="$filter">
	<input type='hidden' name='status' value='$status'>
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
	<input type="hidden" name="DATE" value="$date">
    <input type="hidden" name="FILTER" value="$filter">
	<input type='hidden' name='status' value='$status'>
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
		<input type="hidden" name="DATE" value="$date">
		<input type='hidden' name='status' value='$status'>
		<input type='hidden' name='totaled' value='$totaloffset'>
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
		my $log_message = "删除了".$date."的".$log_name."日志";
		&user_log($log_message);
		@dis_log=();
		$offset = 0;
		$totaloffset = 0;
	}
}
####end
