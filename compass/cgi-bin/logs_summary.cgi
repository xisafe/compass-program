#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: summary.dat,v 1.3.2.4 2004/09/15 13:27:09 alanh Exp $
#

require '/var/efw/header.pl';
use POSIX();

my %titles = (
    'dhcpd' => _('DHCP server'),
    'free/swan' => _('VPN'),
    'httpd' => _('HTTP server'),
    'init' => _('Init'),
    'kernel' => _('Kernel and firewall'),
    'modprobe' => _('Module loader'),
    'pam_unix' => _('Local user logins'),
    'sshd' => _('Remote user logins'),
    'syslogd' => _('Syslogd'),
    'amavis' => _('Spam filter'),
    'postfix' => _('SMTP Proxy'),
    'iptables firewall' => _('Firewall'),
);

sub get_title($) {
    my $key = shift;
    if ($titles{$key} eq '') {
        return $key;
    }
    return $titles{$key};
}

sub format_width($$) {
    my $line = shift;
    my $width = shift;
    my $i=0;
    foreach my $tok (split(/\s/, $line)) {
        my $toklen=length($tok);
        if ($toklen > $width) {
            print "\n";
            $tok =~ s/(.{$width}[\d\w]*[\s,\.!?\-])/\1\n    /g;
            $i=0;
            print $tok;
            next;
        }
        if ($toklen+$i > $width) {
            print "\n    ";
            $i=0;
        }
        $i+=$toklen;
        print $tok." ";
    }
    print "\n";

}


my %cgiparams;

my @longmonths = ( _('January'), _('February'), _('March'),
	_('April'), _('May'), _('June'), _('July'), _('August'),
	_('September'), _('October'), _('November'),
	_('December') );

my @now = localtime();
my $year = $now[5]+1900;

$cgiparams{'MONTH'} = '';
$cgiparams{'DAY'} = '';
$cgiparams{'ACTION'} = '';

&getcgihash(\%cgiparams);

my $start = -1;
if ($ENV{'QUERY_STRING'} && $cgiparams{'ACTION'} ne _('Update'))
{
	my @temp = split(',',$ENV{'QUERY_STRING'});
	$start = $temp[0];
	$cgiparams{'MONTH'} = $temp[1];
	$cgiparams{'DAY'} = $temp[2];
}

if (!($cgiparams{'MONTH'} =~ /^(0|1|2|3|4|5|6|7|8|9|10|11)$/) ||
	!($cgiparams{'DAY'} =~ /^(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)$/))
{
	# Reports are generated at the end of the day, so if nothing is selected
	# we need to display yesterdays (todays won't have been generated yet)
	my @temp_then;
	my @temp_now = localtime(time);
	$temp_now[4] = $now[4];
	$temp_now[3] = $now[3];
	@temp_then = localtime(POSIX::mktime(@temp_now) - 86400);
	   ## Retrieve the same time on the previous day -
	   ## 86400 seconds in a day
	$cgiparams{'MONTH'} = $temp_then[4];
	$cgiparams{'DAY'} = $temp_then[3];
}
elsif($cgiparams{'ACTION'} eq '>>')
{
	my @temp_then;
	my @temp_now = localtime(time);
	$temp_now[4] = $cgiparams{'MONTH'};
	$temp_now[3] = $cgiparams{'DAY'};
	@temp_then = localtime(POSIX::mktime(@temp_now) + 86400);
	   ## Retrieve the same time on the next day -
	   ## 86400 seconds in a day
	$cgiparams{'MONTH'} = $temp_then[4];
	$cgiparams{'DAY'} = $temp_then[3];
}
elsif($cgiparams{'ACTION'} eq '<<')
{
	my @temp_then;
	my @temp_now = localtime(time);
	$temp_now[4] = $cgiparams{'MONTH'};
	$temp_now[3] = $cgiparams{'DAY'};
	@temp_then = localtime(POSIX::mktime(@temp_now) - 86400);
	   ## Retrieve the same time on the previous day -
	   ## 86400 seconds in a day
	$cgiparams{'MONTH'} = $temp_then[4];
	$cgiparams{'DAY'} = $temp_then[3];
}

if (($cgiparams{'DAY'} ne $now[3]) || ($cgiparams{'MONTH'} ne $now[4]))
{
	if ( ($cgiparams{'MONTH'} eq $now[4]) && ($cgiparams{'DAY'} > $now[3]) ||
	     ($cgiparams{'MONTH'} > $now[4]) ) {
		$year = $year - 1;
	}
}

my $monthnum = $cgiparams{'MONTH'} + 1;
my $monthstr;
if ($monthnum <= 9) {
	$monthstr = "0$monthnum"; }
else {
	$monthstr = $monthnum;
}
my $longmonthstr = $longmonths[$cgiparams{'MONTH'}];
my $day = $cgiparams{'DAY'};
my $daystr;
if ($day <= 9) {
	$daystr = "0$day"; }
else {
	$daystr = $day;
}

my $skip=0;
my $filestr="/var/log/logwatch/$year-$monthstr-$daystr";

if (!(open (FILE,$filestr))) {
	$errormessage = _('No (or only partial) logs exist for the day queried.').":".
                        _('%s could not be opened', $filestr)."<br><br>".
                        _('The summary will be generated nightly from the log files of the last day.')." ".
                        _('Therefore summaries for the current day are not yet available.');
	$skip=1;
	# Note: This is in case the log does not exist for that date
}
my $lines = 0;
my @log;


if (!$skip)
{
	while (<FILE>)
	{
		$log[$lines++] = $_;
	}
	close (FILE);
	if (!$lines)
	{
		$errormessage = _('No (or only partial) logs exist for the given day').": $filestr";
		$skip=1;
	}
}

if ($cgiparams{'ACTION'} eq _('Export'))
{
	print "Content-type: text/plain\n\n";

	foreach $_ (@log)
	{
		print "$_\r\n";
	}
	exit 0;
}

&showhttpheaders();

&openpage(_('Log summary'), 1, '');

&openbigbox($errormessage, $warnmessage, $notemessage);

&openbox('100%', 'left', _('Settings'));

printf <<END
<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr>
	<td width='10%' class='base'>%s:</td>
	<td width='25%'>
	<select name='MONTH'>
END
,_('Month')
;
my $month;
for ($month = 0; $month < 12; $month++)
{
	print "\t<option ";
	if ($month == $cgiparams{'MONTH'}) {
		print "selected='selected' "; }
	print "value='$month'>$longmonths[$month]</option>\n";
}
printf <<END
	</select>
	</td>
	<td width='10%' class='base'>%s:</td>
	<td width='25%'>
	<select name='DAY'>
END
,_('Day')
;
for ($day = 1; $day <= 31; $day++) 
{
	print "\t<option ";
	if ($day == $cgiparams{'DAY'}) {
		print "selected='selected' "; }
	print "value='$day'>$day</option>\n";
}
printf <<END
</select>
</td>
<td width='5%'  align='center'><input class='submitbutton' type='submit' name='ACTION' title='%s' value='&lt;&lt;' /></td>
<td width='5%'  align='center'><input class='submitbutton' type='submit' name='ACTION' title='%s' value='&gt;&gt;' /></td>
<td width='10%' align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
<td width='10%' align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
</tr>
</table>
</form>
END
,
_('Day before'),
_('Day after'),
_('Update'),
_('Export')

;

&closebox();

my $header = 0;
my @content;

if(!$skip)
{
  foreach $_ (@log)
  {
 if (/^\s*--+ ([^-]+) Begin --+\s*$/) {
      # New Section. open box
      @content = ();
      &openbox('100%', 'left', get_title($1));
      print "<pre>";
    } elsif (/^\s*--+ ([^-]+) End --+\s*$/) {
      # End of Section, kill leading and trailing blanks, print info, close
      # box
      while ( $content[0] =~ /^\s*$/ ) { shift @content; }
      while ( $content[$#content] =~ /^\s*$/ ) { pop @content; }
      foreach $_ (@content) { $_ =~ s/\s*$//; format_width(&cleanhtml($_,"y"), 60)."\n"; }
      print "\n</pre>";
      &closebox();
    } elsif (/^\s*#+ LogWatch [^#]+[)] #+\s*$/) {
      # Start of logwatch header, skip it
      $header = 1;
    } elsif (/^\s*#+\s*$/) {
      # End of logwatch header
      $header = 0;
    } elsif (/^\s*#+ LogWatch End #+\s*$/) {
      # End of report
    } elsif ($header eq 0) {
      push(@content,$_);
    }
  }
}

&closebigbox();

&closepage();
;
