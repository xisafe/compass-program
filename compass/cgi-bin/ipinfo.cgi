#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# (c) 2002 Josh Grubman <jg@false.net> - Multiple registry IP lookup code
#
# $Id: ipinfo.cgi,v 1.4 2003/12/11 11:06:40 riddles Exp $
#

use IO::Socket;
require '/var/efw/header.pl';

my %cgiparams;

&showhttpheaders();

&getcgihash(\%cgiparams);

$ENV{'QUERY_STRING'} =~s/&//g;
my @addrs = split(/ip=/,$ENV{'QUERY_STRING'});

my %whois_servers = ("RIPE"=>"whois.ripe.net","APNIC"=>"whois.apnic.net","LACNIC"=>"whois.lacnic.net");

&openpage(_('IP Information'), 1, '');

&openbigbox($errormessage, $warnmessage, $notemessage);

my $addr;
foreach $addr (@addrs) {
next if $addr eq "";

	undef $extraquery;
	undef @lines;
	my $whoisname = "whois.arin.net";
	my $iaddr = inet_aton($addr);
	my $hostname = gethostbyaddr($iaddr, AF_INET);
	if (!$hostname) { $hostname = _('Reverse lookup failed'); }

	my $sock = new IO::Socket::INET ( PeerAddr => $whoisname, PeerPort => 43, Proto => 'tcp');
	if ($sock)
	{
		print $sock "$addr\n";
		while (<$sock>) {
			$extraquery = $1 if (/NetType:    Allocated to (\S+)\s+/);
			push(@lines,$_);
		}
		close($sock);
		if (defined $extraquery) {
			undef (@lines);
			$whoisname = $whois_servers{$extraquery};
			my $sock = new IO::Socket::INET ( PeerAddr => $whoisname, PeerPort => 43, Proto => 'tcp');
			if ($sock)
			{
				print $sock "$addr\n";
				while (<$sock>) {
					push(@lines,$_);
				}
			}
			else
			{
				@lines = ( _('Unable to contact: \'%s\'', $whoisname));
			}
		}
	}
	else
	{
		@lines = ( _('Unable to contact: \'%s\''), $whoisname);
	}

my $hostiplink=" &nbsp;<A HREF=\"http://www.hostip.info/map/index.html?ip=$addr\" TARGET=\"_new\">hostip.info</A>";
	&openbox('100%', 'left', $addr . ' (' . $hostname . ') : '.$whoisname.$hostiplink);

	print "<pre>\n";
	foreach $line (@lines) {
		print &cleanhtml($line,"y");
	}
	print "</pre>\n";
	&closebox();
}

printf <<END
<div align='center'>
<table width='80%'>
<tr>
	<td align='center'><a href='$ENV{'HTTP_REFERER'}'>%s</a></td>
</tr>
</table>
</div>
END
, _('BACK')
;

&closebigbox();

&closepage();
