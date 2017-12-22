#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: log.dat,v 1.6.2.5 2004/09/15 13:27:09 alanh Exp $
#

require '/var/efw/header.pl';
use POSIX();

my %cgiparams;
my %logsettings;
my %filters = (
        'all' => '([^:]*)',
	'efw' => '(efw)',
	'red' => '(red.*|kernel: usb.*|pppd\[.*\]|chat\[.*\]|pppoe\[.*\]|pptp\[.*\]|pppoa\[.*\]|pppoa3\[.*\]|pppoeci\[.*\]|ipppd|ipppd\[.*\]|kernel: ippp\d|kernel: isdn.*|ibod\[.*\]|kernel: eth.*|dhclient|modem_run.*)',
	'dns' => '(dnsmasq)\[.*\]',
	'dhcp' => '(dhcpd)', 
	'cron' => '(fcron)\[.*\]',
	'ntp' => '(ntpd|ntpdate)\[.*\]',
	'ssh' => '(sshd(?:\(.*\))?\[.*\])',
	'auth' => '(\w+\(pam_unix\)\[.*\])',
	'kernel' => '(kernel)',
	'backup' => '(autobackup|backup\-create|backup\-restore)',
	'ipsec' => '(ipsec_.*|pluto\[.*\])');
$cgiparams{'SECTION'} = 'all';
$cgiparams{'ACTION'} = "";
&getcgihash(\%cgiparams);
$logsettings{'LOGVIEW_REVERSE'} = 'off';

&readhash("${swroot}/logging/default/settings", \%logsettings);
eval {
    &readhash("${swroot}/logging/settings", \%logsettings);
};

if ($logsettings{'LOGVIEW_SIZE'} =~ /^\d+$/) {
    $viewsize = $logsettings{'LOGVIEW_SIZE'};
}

my $logfile="/var/log/messages";
my @files = sort(glob("${logfile}-*.gz"));
my $name = "system";

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
my $date = $today;

if ($cgiparams{'DATE'} =~ /[\d\-]+/) {
    $date = $cgiparams{'DATE'};
}

my $filter = $cgiparams{'FILTER'};

my $filetotal=scalar(@files);

my ($firstdatestring) = ($files[0] =~ /\-(\d+).gz$/);
if ($firstdatestring eq '') {
    $firstdatestring = dateToFilestring($today);
}

if ((dateToFilestring($date) < $firstdatestring) || (dateToFilestring($date) > dateToFilestring($today))) {
    $date = $today;
}

my $filestr = $logfile;
if ($date ne $today) {
    $filestr="${logfile}-".dateToFilestring($date).".gz";
}
my $hostname = $settings{'HOSTNAME'};

if (!(open (FILE,($filestr =~ /.gz$/ ? "gzip -dc $filestr |" : $filestr)))) {
    $errormessage = _('No (or only partial) logs exist for the given day').": "._('%s could not be opened', $filestr);
}

my $section = $filters{$cgiparams{'SECTION'}};

my $lines = 0;
my @log = ();

if (!$skip) {
    foreach my $line (<FILE>) {
	if ($line !~ /(^... .. ..:..:..) [\w\-]+ ${section}: (.*)$/) {
	    next;
	}
	if (($filter !~ /^$/) && ($line !~ /$filter/)) {
	    next;
	}
	$log[$lines] = $line;
	$lines++;
    }
    close (FILE);
}

if ($cgiparams{'ACTION'} eq _('Export')) {
    my $datestr = dateToFilestring($date);
    print <<EOF
Content-type: text/plain
Cache-Control: no-cache
Connection: close
Content-Disposition: attachement; filename="${hostname}-${name}-${datestr}.log"

EOF
;

    if ($filter eq '') {
	print _("Firewall log of day %s.", $date);
    } else {
	print _("Firewall log of day %s with filter '%s'.", $date, $filter);
    }

    print "Section: $cgiparams{'SECTION'}\r\n";
    
    if ($logsettings{'LOGVIEW_REVERSE'} eq 'on') { @log = reverse @log; }

    foreach my $line (@log) {
	$line =~ /(^... .. ..:..:..) [\w\-]+ ${section}: (.*)$/;
	print "$1 $2 $3\r\n";
    }
    exit 0;
}

&showhttpheaders();

my %selected;

$selected{'SECTION'}{'all'} = '';
$selected{'SECTION'}{'efw'} = '';
$selected{'SECTION'}{'red'} = '';
$selected{'SECTION'}{'dns'} = '';
$selected{'SECTION'}{'dhcp'} = '';
$selected{'SECTION'}{'ssh'} = '';
$selected{'SECTION'}{'cron'} = '';
$selected{'SECTION'}{'ntp'} = '';
$selected{'SECTION'}{'auth'} = '';
$selected{'SECTION'}{'kernel'} = '';
$selected{'SECTION'}{'ipsec'} = '';
$selected{'SECTION'}{'backup'} = '';
$selected{'SECTION'}{$cgiparams{'SECTION'}} = "selected='selected'";

$extraheaders = <<EOF
<script type="text/javascript" src="/include/jquery.js"></script>
<script type="text/javascript" src="/include/jquery-calendar.js"></script>
<style type="text/css">\@import url(/include/jquery-calendar.css);</style>
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

$extraheaders .= <<EOF
<script>
  \$(document).ready(function(){
    \$('#calendar').calendar(
			    {dateFormat: 'YMD-',
			    minDate: new Date(@$firstdatearr[0], @$firstdatearr[1]-1, @$firstdatearr[2]),
			    maxDate: new Date(@$lastdatearr[0], @$lastdatearr[1]-1, @$lastdatearr[2]),
			    speed: 'immediate'
			    });
  });
</script>
EOF
;


my $offset = 1;
if ($cgiparams{'OFFSET'} =~ /\d+/) {
    $offset = $cgiparams{'OFFSET'};
}
if ($offset < 1) {
    $offset = 1;
}
my $totaloffset=POSIX::ceil($lines/$viewsize);
if ($offset > $totaloffset) {
    $offset = $totaloffset;
}

&openpage(_('System log viewer'), 1, $extraheaders);

&openbigbox($errormessage, $warnmessage, $notemessage);

&openbox('100%', 'left', _('Settings'));

printf <<END
<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
  <tr>
    <td width='20%'>%s:</td>
    <td width='20%'><select name='SECTION'>
        <option $selected{'SECTION'}{'all'} value='all'>All</option>
        <option $selected{'SECTION'}{'efw'} value='efw'>System</option>
        <option $selected{'SECTION'}{'red'} value='red'>RED</option>
        <option $selected{'SECTION'}{'dns'} value='dns'>DNS</option>
        <option $selected{'SECTION'}{'dhcp'} value='dhcp'>%s %s %s</option>
        <option $selected{'SECTION'}{'ssh'} value='ssh'>SSH</option>
        <option $selected{'SECTION'}{'ntp'} value='ntp'>NTP</option>
        <option $selected{'SECTION'}{'cron'} value='cron'>Cron</option>
        <option $selected{'SECTION'}{'auth'} value='auth'>%s</option>
        <option $selected{'SECTION'}{'kernel'} value='kernel'>%s</option>
        <option $selected{'SECTION'}{'backup'} value='backup'>%s</option>
        <option $selected{'SECTION'}{'ipsec'} value='ipsec'>IPSec</option>
      </select>
    </td>
    <td width='20%' class='base'>%s:</td>
    <td width='20%'><input type="text" size="25" name='FILTER' VALUE="$filter"></td>

    <td width='20%' align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
  </tr>
  <tr>
    <td>%s:</td><td><input type="text" SIZE="9" id="calendar" name='DATE' VALUE="$date"></td>

    <td>%s:</td><td><input type="text" SIZE="2" name='OFFSET' VALUE="$offset"></td>
    <td align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
  </tr>
</table>
</form>
END
,
_('Section'),
_('DHCP server'),
_('GREEN'),
_('BLUE'),
_('Login/Logout'),
_('Kernel'),
_('Backup'),
_('Filter'),
_('Update'),
_('Jump to Date'),
_('Jump to Page'),
_('Export')

;

&closebox();

&openbox('100%', 'left', _('log'));

my $start = $lines - ($viewsize * $offset);
my $prev = $offset+1;
my $next = $offset-1;
my $prevday = $date;
my $nextday = $date;

if ($start <= 0) { 
    $start = 0;
    $prev = 1;
    my $daybefore = getDate(stringToDate($date)-86400);
    if (dateToFilestring($daybefore) >= $firstdatestring) {
	$prevday = $daybefore;
    } else {
	$prev = -1;
    }
}
if ($next < 1) {
    $next = 1;
    $next = 99999999999;
    my $dayafter = getDate(stringToDate($date)+86400);
    if (dateToFilestring($dayafter) <= dateToFilestring($today)) {
	$nextday = $dayafter;
    } else {
	$next = -1;
    }
}

my @slice = splice(@log, $start, $viewsize);

if ($logsettings{'LOGVIEW_REVERSE'} eq 'on') { @slice = reverse @slice; }

print "<p><b>"._('Total number of lines matching selected criteria for day %s', $date).": $lines - "._('Page %s of %s', $offset, $totaloffset). "</b></p>";

&oldernewer();

printf <<END
<table width='100%'>
END
;

my $i = 0;

foreach my $line (@slice) {
    $line =~ /(^... .. ..:..:..) [\w\-]+ ${section}: (.*)$/;
    if ($i % 2) {
	print "<tr class='even'>\n";
    } else {
	print "<tr class='odd'>\n";
    }
    printf <<END
    <td>$1 $2 $3</td>
  </tr>
END
;
    $i++;
}
print "</table>";

if ($#slice > 10) {
    &oldernewer();
}


&closebigbox();

&closepage();


sub oldernewer {
    printf <<END
<table width='100%'>
  <tr>
END
;

    print "<td align='center' width='50%'>";
    if ($prev != -1) {
printf <<END
<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$prev">
    <input type="hidden" name="DATE" value="$prevday">
    <input type="hidden" name="FILTER" value="$filter">
    <input type="hidden" name="SECTION" value="$cgiparams{'SECTION'}">
    <input class='submitbutton' type="submit" name="ACTION" value="%s">
</form>
END
,_('Older')
;
    } else {
	print _('Older');
    }
    print "</td>\n";

    print "<td align='center' width='50%'>";
    if ($next != -1) {
printf <<END
<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$next">
    <input type="hidden" name="DATE" value="$nextday">
    <input type="hidden" name="FILTER" value="$filter">
    <input type="hidden" name="SECTION" value="$cgiparams{'SECTION'}">
    <input class='submitbutton' type="submit" name="ACTION" value="%s">
</form>
END
,_('Newer')
;
    } else {
	print _('Newer');
    }
    print "</td>\n";

    printf <<END
</tr>
</table>
END
;
}
