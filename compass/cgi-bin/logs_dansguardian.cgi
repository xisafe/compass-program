#!/usr/bin/perl

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
my $log_name = "内容过滤";
my %cgiparams;
my %logsettings;
my %ips;
my %save;
my %selected;
my %checked;
my %mapip;

my $logfile="/var/log/dansguardian/access.log";
my @files = sort(glob("${logfile}-*.gz"));
my $name = "dansguardian";

my @abbr = qw(Zero Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );

# Enable DNS
my $ip2addr = 'on';

$cgiparams{'ACTION'} = '';
$cgiparams{'SEARCHFILTER'} = "";

&getcgihash(\%cgiparams);
$logsettings{'LOGVIEW_REVERSE'} = 'off';

&readhash("${swroot}/logging/default/settings", \%logsettings);
eval {
    &readhash("${swroot}/logging/settings", \%logsettings);
};

if ($logsettings{'LOGVIEW_SIZE'} =~ /^\d+$/) {
    $viewsize = $logsettings{'LOGVIEW_SIZE'};
}


&writehash("${swroot}/proxy/viewersettings", \%save);
&readhash("${swroot}/proxy/viewersettings", \%save);

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
my $years; 
if ($cgiparams{'DATE'} =~ /[\d\/]+/) {
    $date = $cgiparams{'DATE'};
}
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

my $searchfilter = $cgiparams{'SEARCHFILTER'};
if($searchfilter =~/\(|\)|\[|\]|\*/){
	$errormessage = "筛选关键字中包含系统屏蔽的非法字符";
	$searchfilter = "";
}

my $filetotal=scalar(@files);

my ($firstdatestring) = ($files[0] =~ /\-(\d+).gz$/);
if ($firstdatestring eq '') {
    $firstdatestring = dateToFilestring($today);
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


my $thiscode = '$temp =~ /$filter/;';
eval($thiscode);
if ($@ ne '') {
    $errormessage = _('Bad ignore filter').":$@<P>";
    $filter = '';
}
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
my $heads = $offset *$viewsize;
my $tempd,$get_line_num;
if ($cgiparams{'status'} eq 'down') {
	if ($searchfilter) {
		$tempd=`tac $filestr |grep "$searchfilter" -m  $heads|head -n $heads |tail -n $viewsize`;
		$get_line_num=`grep "$searchfilter" $filestr |wc -l`;
		if ($filestr =~ /\.gz$/) {
			$get_line_num = `gzip -dc $filestr |grep "$searchfilter"| wc -l`;
			$tempd = `gzip -dc $filestr |grep "$searchfilter" |sort -r|head -n $heads |tail -n $viewsize`; 
		}
	}
	else{
		$tempd=`tac $filestr |head -n $heads |tail -n $viewsize`;
		$get_line_num=`wc -l $filestr`;
		if ($filestr =~ /\.gz$/) {
			$get_line_num = `gzip -dc $filestr | wc -l`;
			$tempd = `gzip -dc $filestr |sort -r|head -n $heads |tail -n $viewsize`; 
		}
	}	
}
else{
	if ($searchfilter) {
		$tempd=`cat $filestr |grep "$searchfilter" -m  $heads|head -n $heads |tail -n $viewsize`;
		$get_line_num=`grep "$searchfilter" $filestr |wc -l`;
		if ($filestr =~ /\.gz$/) {
			$get_line_num = `gzip -dc $filestr |grep "$searchfilter"| wc -l`;
			$tempd = `gzip -dc $filestr |grep "$searchfilter" |head -n $heads |tail -n $viewsize`; 
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
}
$lines = $get_line_num;
@log = split(/\n/,$tempd);
my @dis_log;
foreach my $line (@log) {
	chomp($line);
	my ($dow, $day, $hours, $host, $processname, $dg_date,$dg_time,$username,$ip,$url,@rest) = split(/\s+/, $line);
	my ($YEARdt, $MONTHdt, $DAYdt) = split(/\./, $dg_date);
	my ($HOURdt, $MINdt, $SECdt)   = split(/:/, $dg_time);

	if (($searchfilter !~ /^$/) && ($line !~ /$searchfilter/)) {
	    next;
	}

	$extra = join('', @rest); 
	if ($extra =~ /\*denied\*/i) {
	    $extra = 'DENIED';
	} else {
	    $extra = 'ok';
	}
	my $temp = "$dow $day $hours $ip $username $url $extra";
	push(@dis_log,$temp);
}
my $totaloffset=POSIX::ceil($lines/$viewsize);
if ($offset > $totaloffset) {
    $offset = $totaloffset;
}


&openpage(_('Proxy log viewer'), 1, $extraheaders);

####发改委项目添加日志删除 by elvis 2012-6-13
&save();
####end
&openbigbox($errormessage, $warnmessage, $notemessage);



&openbox('100%', 'left', _('log'));

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
print "<div class='paging-div-header'>";
oldernewer();
print "</div>";	
printf <<END

<div style="max-height:500px;overflow:auto;margin:25px 0;">
<table width='100%' class='ruleslist'>
  <tr>
    <td width='10%' nowrap="nowrap" align='center' class='boldbase'><b>%s</b> $sort_time</td>
    <td width='15%' nowrap="nowrap" align='center' class='boldbase'><b>%s</b></td>
    <td width='67%' align='center' class='boldbase'><b>%s</b></td>
    <td width='8%' align='center' class='boldbase'><b>%s</b></td>
  </tr>
END
,
_('Time'),
_('Source IP'),
_('Website'),
_('Status')
;


my $i = 0;
my $currentcolor = 0;
my %map = ();

foreach my $line (@dis_log) {
    if ($i % 2) {
	print "<tr class='env_thin'>\n";
    } else {
	print "<tr class='odd_thin'>\n";
    }
    my ($mon,$date, $time,$ip,$username,$url, $extra) = split(/\s+/, $line);
    $url =~ /(^.{0,100})/;
    my $part = $1;
    unless (length($part) < 60) { $part = "${part}..."; }  
    $url = &cleanhtml($url,"y");
    $part = &cleanhtml($part,"y");
    my $name = ip2addr($ip);
    if (!($map{$ip})) {
	get_colors();	
	$map{$ip} = $color;
    }
    my $user = '';
    if ($username ne '-') {
	$user = " (".$username.")";
    }
	my $timestamp = $mon." ".$date." ".$time;
	$timestamp = change_time($timestamp);
	$timestamp =~s/^\s//;
	$timestamp = $years."-".$timestamp;
    printf <<END
	<td align='center' nowrap="nowrap">$timestamp</td>
	<td align='center' nowrap="nowrap"><span>${name}</span>${user}</td>
	<td align='left'><a href='$url' title='$url' target='_new'>$part</a></td>
	<td align='center'>$extra</td>
      </tr>
END
;
    $i++;
}
if ($i==0) {
	no_tr(4,_('Current no content'));
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
	<td width='190px'>%s: <input type="text" size="18" name='SEARCHFILTER' VALUE="$searchfilter"></td>
    <td width='180px'>%s: <input type="text" SIZE="12" id="inputDate" name='DATE' VALUE="$date" />
<script type="text/javascript"> ESONCalendar.bind("inputDate");</script>

	</td>
    <td  align='left'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
	</form>
    <td  align='right'>
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="DATE" value="$prevday">
    <input type="hidden" name="SEARCHFILTER" value="$searchfilter">
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
    <input type="hidden" name="SEARCHFILTER" value="$searchfilter">
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
    <input type="hidden" name="SEARCHFILTER" value="$searchfilter">
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
    <input type="hidden" name="SEARCHFILTER" value="$searchfilter">
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
    <input type="hidden" name="SEARCHFILTER" value="$searchfilter">
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
		<input type="hidden" name="SEARCHFILTER" value="$searchfilter">
		<input class='submitbutton' type="submit" style="background:none;border:0;cursor:pointer" name="ACTION" value='%s' />
	</form>
		</td>
		<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<td  align='right' >%s: <input type="text" SIZE="2" name='OFFSET' VALUE="$offset"></td>
        <td  align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
		<input type="hidden" name="SEARCHFILTER" value="$searchfilter">
		<input type="hidden" name="DATE" value="$date">
		<input type='hidden' name='status' value='$status'>
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


###############################
# get colors
###############################
sub get_colors() {
    my @colors = (
		  "style='color: #CC0000'",
		  "style='color: #FF9900'",
		  "style='color: #009900'",
		  "style='color: #33CCCC'",
		  "style='color: #CC33CC'",
		  "style='color: #333333'",
		  "style='color: #000099'",
		  );
    if ( $currentcolor > $#colors ) { $currentcolor = 0; }
    $color = $colors[$currentcolor];
    $currentcolor++;
}

################################
# Resolv IPs to hostnames
################################
sub ip2addr() {
    undef $name;
    if ( $ip2addr eq 'on' ) {
	my $ip = shift;
	use Socket;
	my $addr = inet_aton($ip);
	if ( !( $mapip{$ip} ) ) {
	    $mapip{$ip} = gethostbyaddr( $addr, AF_INET );
	}
	if ( !( $mapip{$ip} ) ) {
	    $mapip{$ip} = $ip;
	}
	return $name = $mapip{$ip};
    }
    if (!($name)) { $name = $ip }
}
