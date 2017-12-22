#!/usr/bin/perl
#
# openvpn CGI for Endian Firewall
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


# -------------------------------------------------------------
# some definitions
# -------------------------------------------------------------

require '/var/efw/header.pl';
require './endianinc.pl';

my $passwd   = '/usr/bin/openvpn-sudo-user';

my $name        = _('OpenVPN server');
my $self = $ENV{SCRIPT_NAME};

my %par;
my $username = '';
my $errormessage = '';
my $err = 1;

sub human_time($) {
    my $seconds = shift;
    use integer;

    my $days = $seconds / 86400;
    $seconds -= $days * 86400;
    my $hours = $seconds / 3600;
    $seconds -= $hours * 3600;
    my $minutes = $seconds / 60;
    $seconds -= $minutes * 60;

    my $ret = '';
    if ($days != 0) {
	$ret .= $days.'d ';
    }
    if ($hours != 0) {
	$ret .= $hours.'h ';
    }
    if ($minutes != 0) {
	$ret .= $minutes.'m ';
    }
    if ($ret eq '') {
	$ret = '< 1m';
    }
    return $ret;
}


sub shorten($) {
    my $val = shift;
    return int($val * 10) / 10;
}

sub human_bytes($) {
    my $bytes = shift;

    my $giga = $bytes / 1073741824;
    if ($giga > 1.4) {
	return shorten($giga) . ' GiB';
    }
    my $mega = $bytes / 1048576;
    if ($mega > 1.4) {
	return shorten($mega) . ' MiB';
    }
    my $kilo = $bytes / 1024;
    if ($kilo > 1.4) {
	return shorten($kilo) . ' KiB';
    }
    return $bytes . 'b';
}


sub list_connections() {
    openbox('100%', 'left', _('Connection status and control'));

    my @conn = split(/\n/, `$passwd status`);
    my $i = 0;

    printf <<EOF
<table cols="9">
  <tr>
    <td width="18%" class="boldbase"><b>%s</b></td>
    <td width="9%" class="boldbase"><b>%s</b></td>
    <td width="13%" class="boldbase"><b>%s</b></td>
    <td width="16%" class="boldbase"><b>%s / %s</b></td>
    <td width="21%" class="boldbase"><b>%s</b></td>
    <td width="10%" class="boldbase"><b>%s</b></td>
    <td width="13%" align="center" class="boldbase"><b>%s</b></td>
  </tr>
EOF
,
_('User'),
_('Assigned IP'),
_('Real IP'),
_('RX'),
_('TX'),
_('Connected since'),
_('Uptime'),
_('Actions')
;


    foreach my $line (@conn) {
	my @split = split(/,/, $line);
	if ($split[0] ne 'CLIENT_LIST') {
	    next;
	}
	my $oddeven = 'odd';
	if ($i % 2) {
	    $oddeven = 'even';
	}
	my $conntime = human_time(time() - $split[7]);
	my $user = $split[1];
	my $rx = human_bytes($split[4]);
	my $tx = human_bytes($split[5]);

	my $realip = $split[2];
	$realip =~ s/:.*$//;

#CLIENT_LIST,r3,80.108.92.192:49542,192.168.0.180,68830,67705,Wed Feb 23 07:56:26 2005,1109141786
	printf <<EOF
  <tr class="$oddeven">
    <td>$user</td>
    <td>$split[3]</td>
    <td>$realip</td>
    <td nowrap='nowrap'>$rx / $tx</td>
    <td nowrap='nowrap'>$split[6]</td>
    <td nowrap='nowrap'>$conntime</td>
    <td nowrap='nowrap'>
      <form method="post" action="$self" style="display:inline;">
        <input class='submitbutton' type="submit" name="submit" value="kill" style="padding-left: 2px; padding-right: 2px;">
        <input type="hidden" name="username" value="$user">
        <input type="hidden" name="ACTION" value="kill">
      </form>
    </td>
  </tr>
EOF
;

	$i++;
    }
    print '</table>';


    closebox();
}

sub checkuser() {
    if ($username !~ /^$/) {
	return 1;
    }
    $err = 0;
    $errormessage = _('Username not set.');
    return 0;
}

sub sanitize($) {
    my $data = shift;
    $data =~ s/\"/\\\"/;
    return $data;
}

sub kill_vpn($) {
    my $user = shift;
    `$passwd kill \"$user\"`;
}

sub doaction() {

    if (!$action) {
	return;
    }

    if ($action eq 'kill') {
	if (!checkuser()) {
	    return;
	}

	kill_vpn($username);
	return;
    }
}

getcgihash(\%par);
$action = $par{ACTION};


# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------

$username = sanitize($par{'username'});
doaction();


# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------

showhttpheaders();

openpage($name, 1, '');
openbigbox($errormessage, $warnmessage, $notemessage);
list_connections();
closebigbox();
closepage();

