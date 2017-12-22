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
use Net::IPv4Addr qw (:all);
use File::Copy;
use File::Temp qw/ tempdir tempfile/;

my $passwd   = '/usr/bin/openvpn-sudo-user';

my $conffile = "${swroot}/openvpn/settings";
my $conffile_default = "${swroot}/openvpn/default/settings";
my $hostconffile = "${swroot}/host/settings";
my $etherconf = "${swroot}/ethernet/settings";
my $openvpn_diffie = '/var/efw/openvpn/dh1024.pem';
my $openvpn_diffie_lock = '/var/lock/openvpn_diffie.lock';

my $PKCS_FILE = '/var/efw/openvpn/pkcs12.p12';
my $PKCS_IMPORT_FILE = "${PKCS_FILE}.import";
my $CACERT_FILE = '/var/efw/openvpn/cacert.pem';
my $CRL_FILE = '/var/efw/openvpn/crl.pem';
my $SUBJECT_FILE = '/var/efw/openvpn/subject.txt';
my $ISSUER_FILE = '/var/efw/openvpn/issuer.txt';

my $dirtyfile  = '/var/efw/openvpn/dirtyuserconfig';

my $restart  = '/usr/local/bin/run-detached /usr/local/bin/restartopenvpn';

my $name        = _('OpenVPN server');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked="checked"');
my %selected = ();
my $self = $ENV{SCRIPT_NAME};

my %par;
my %confhash = ();
my $conf = \%confhash;
my $pool_begin = '';
my $pool_end = '';
my $port = '';
my $protocol = '';
my $netpart = undef;
my $ether = undef;
my $enabled = 0;
my $action = '';
my $errormessage = '';
my $err = 1;
my $block_dhcp = '';
my $config = 0;
my %hosthash = ();
my $host = \%hosthash;

my $globalnetworks = '';
my $globalnameserver = '';
my $domain = '';
my ($a, $b);
my $abcast = '';
my $bnetwork = '';
my $needrestart = 0;

sub checkuser() {
    if ($username !~ /^$/) {
	return 1;
    }
    $err = 0;
    $errormessage = _('Username not set.');
    return 0;
}

sub kill_vpn($) {
    my $user = shift;
    `$passwd kill \"$user\"`;
}

sub doaction() {

    if (!$action) {
	    return;
    }

    if ($action eq 'save') {
	($err,$errormessage) = save();
	getconfig();
	$action = '';
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

sub ip2long {
    return unpack("l*", pack("l*", unpack("N*", inet_aton(shift))));
}

sub long2ip {
    return inet_ntoa(pack("N*", shift));
}

sub smallPools($$) {
    my $netaddress = shift;
    my $cidr = shift;
    my $ip = $netaddress;
    my $cidr = int($cidr) + 1;

    my $a = "$ip/$cidr";

    my $broadcast = ipv4_broadcast($a);
    $ip = long2ip(ip2long($broadcast) + 1);
    my $b = "$ip/$cidr";

    return ($a, $b);
}

sub checkSubnetInZone($) {
    my $subnet = shift;

    my $zones = validzones();
    foreach my $zone (@$zones) {
	next if ($zone eq 'RED');
	my @ips = split(/,/, $ether->{uc($zone) . "_IPS"});
	foreach my $zonenet (@ips) {
            if (ipv4_in_network($subnet, $zonenet)) {
		return($zone, $zonenet);
	    }
	}
    }
    return (0,0);
}

sub save () {

    $config = \%par;
    my $logid = "$0 [" . scalar(localtime) . "]";
    #my $needrestart = 0;
    my $ippool_begin = $par{IPPOOL_BEGIN};
    my $ippool_end = $par{IPPOOL_END};
    $block_dhcp = $par{DROP_DHCP};
    $port = $par{OPENVPN_PORT};
    $protocol = $par{OPENVPN_PROTOCOL};
    local $auth_type = $par{AUTH_TYPE};
    my $ret = 0;
    my $error = '';
    my $purple_net = $par{'PURPLE_NET'};

    if ($par{'BRIDGED'} eq 'on') {
	if (!validip($ippool_begin) ||
	    !validip($ippool_end)) {
	    return (0, _('Invalid IP address'));
	}
	if (ip2long($ippool_begin)  >= ip2long($ippool_end)) {
	    return (0, _('Pool start IP must be lesser than end ip!'));
	}
    } else {
	$par{'BRIDGED'} = 'off';
	if (!validipandmask($purple_net)) {
	    return (0, _("VPN subnet '%s' is not a valid ip/mask pair",
			 $purple_net));
	}
	my ($conflictzone, $conflictnet) = checkSubnetInZone($par{'PURPLE_NET'});
	if ($confictzone) {
	    return (0, _('VPN subnet conflicts with %s of zone %s.',
			 $conflictnet,
			 $string_zone{$conflictzone}));
	}
    }

    # XXX: vpn ippool and green dhcp ip pool has to be disjunct! check it!

    if ($ippool_begin eq $ether->{GREEN_ADDRESS}) {
	return (0, _('Pool start IP cannot be the same as GREEN address!'));
    }
    if ($ippool_end eq $ether->{GREEN_ADDRESS}) {
	return (0, _('Pool end IP cannot be the same as GREEN address!'));
    }

    if (! validport($par{OPENVPN_PORT})) {
	return (0, _('Invalid port'));
    }

    if ( ($conf->{PURPLE_IP_BEGIN} ne $ippool_begin) or
	 ($conf->{PURPLE_IP_END} ne $ippool_end) or
	 ($conf->{CLIENT_TO_CLIENT} ne $par{CLIENT_TO_CLIENT}) or
	 ($conf->{DROP_DHCP} ne $par{DROP_DHCP}) or
	 ($conf->{OPENVPN_PORT} ne $par{OPENVPN_PORT}) or
	 ($conf->{OPENVPN_PROTOCOL} ne $par{OPENVPN_PROTOCOL}) or
	 ($conf->{PUSH_GLOBAL_NETWORKS} ne $par{PUSH_GLOBAL_NETWORKS}) or
	 ($conf->{GLOBAL_NETWORKS} ne $par{GLOBAL_NETWORKS}) or
	 ($conf->{PUSH_GLOBAL_DNS} ne $par{PUSH_GLOBAL_DNS}) or
	 ($conf->{GLOBAL_DNS} ne $par{GLOBAL_DNS}) or
	 ($conf->{PUSH_DOMAIN} ne $par{PUSH_DOMAIN}) or
	 ($conf->{DOMAIN} ne $par{DOMAIN}) or
	 ($conf->{OPENVPN_ENABLED} ne $par{ENABLE}) or
	 ($conf->{BRIDGED} ne $par{BRIDGED}) or
	 ($conf->{BRIDGE_TO} ne $par{BRIDGE_TO}) or
	 ($conf->{PURPLE_NET} ne $par{PURPLE_NET}) or
	 ($conf->{AUTH_TYPE} ne $par{AUTH_TYPE})
	 ) {
	print STDERR "$logid: writing new configuration file\n";
	$needrestart = 1;

	$conf->{PURPLE_IP_BEGIN} = $ippool_begin;
	$conf->{PURPLE_IP_END} = $ippool_end;
	$conf->{CERT_AUTH} = $par{CERT_AUTH};
	$conf->{DROP_DHCP} = $par{DROP_DHCP};

	$conf->{OPENVPN_PROTOCOL} = $par{OPENVPN_PROTOCOL};
	$conf->{OPENVPN_PORT} = $par{OPENVPN_PORT};
	$conf->{AUTH_TYPE} = $par{AUTH_TYPE};

	$conf->{PUSH_GLOBAL_NETWORKS} = $par{PUSH_GLOBAL_NETWORKS};
	$conf->{PUSH_GLOBAL_DNS} = $par{PUSH_GLOBAL_DNS};
	$conf->{GLOBAL_NETWORKS} = $par{GLOBAL_NETWORKS};
	$conf->{GLOBAL_DNS} = $par{GLOBAL_DNS};
	$conf->{GLOBAL_NETWORKS} =~ s/[\r\n]+/,/g;
	$conf->{GLOBAL_DNS} =~ s/[\r\n]+/,/g;

	$conf->{PUSH_DOMAIN} = $par{PUSH_DOMAIN};
	$conf->{DOMAIN} = $par{DOMAIN};

	$conf->{CLIENT_TO_CLIENT} = $par{CLIENT_TO_CLIENT};
	$conf->{OPENVPN_ENABLED} = $par{ENABLE};

	$conf->{BRIDGED} = $par{BRIDGED};
	$conf->{BRIDGE_TO} = $par{BRIDGE_TO};
	$conf->{PURPLE_NET} = $par{PURPLE_NET};

	$config = $conf;

	writehash($conffile, $conf);
        &log(_('Written down Openvpn configuration'));
    }

    if (!$enabled and $par{ENABLE} eq 'on') {
        print STDERR "$logid: changing status from 'off' -> 'on'\n";
        $needrestart = 1;
        $enabled = 1;
    } elsif ($enabled and $par{ENABLE} ne 'on') {
        print STDERR "$logid: changing status from 'on' -> 'off'\n";
        $needrestart = 1;
        $enabled = 0;
    }

    print STDERR `$restart --force`; 
    print STDERR "$logid: restarting done\n";
    return 1;
}

sub read_file($) {
    my $f = shift;
    open (CA, $f) || return _("Could not open file '%s'.", $f);
    my $str = <CA>;
    close CA;
    return $str;
}

sub display() {
    if ($config->{'AUTH_TYPE'} =~ /^$/) {
        $config->{'AUTH_TYPE'} = 'psk';
    }

    $selected{'OPENVPN_PROTOCOL'}{uc($protocol)} = 'selected';
    $selected{'BRIDGE_TO'}{uc($config->{'BRIDGE_TO'})} = 'selected="selected"';

    my %authtype = ();
    $authtype{$config->{'AUTH_TYPE'}} = 'checked="checked"';

    my $canreadpkcs = 0;
    if (open F, $PKCS_FILE) {
        $canreadpkcs = 1;
        close(F);
    }

    my $canreadcacert = 0;
    if (open F, $CACERT_FILE) {
        $canreadcacert = 1;
        close(F);
    }

    my $displaypsk = 'display: none';
    if ($config->{'AUTH_TYPE'} eq 'psk') {
        $displaypsk = 'display: block';
    }

    my $displaycert = 'display: none';
    if ($config->{'AUTH_TYPE'} =~ /cert/) {
        $displaycert = 'display: block';
    }

    if (($pool_begin eq '') && ($pool_end eq '')) {
	if ($ether->{'GREEN_CIDR'} <= 28) {
	    my ($a, $b) = smallPools($ether->{'GREEN_NETADDRESS'}, $ether->{'GREEN_CIDR'});
	    my ($ip, $cidr) = split(/\//, $b);
	    ($a, $b) = smallPools($ip, $cidr);
	    ($pool_begin, ) = split(/\//, $a);
	    ($pool_end, ) = split(/\//, $b);
	    $pool_begin = long2ip(ip2long($pool_begin) + 1);
	    $pool_end = long2ip(ip2long($pool_end) - 2);
	}
    }

    printf <<EOF
<form method='post' action='$self' enctype='multipart/form-data'>
  <input type='hidden' name='ACTION' value='save' />
  <input type='hidden' name='CLIENT_TO_CLIENT' value='$config->{'CLIENT_TO_CLIENT'}' />
  <input type='hidden' name='OPENVPN_PORT' value='$config->{'OPENVPN_PORT'}' />
  <input type='hidden' name='OPENVPN_PROTOCOL' value='$config->{'OPENVPN_PROTOCOL'}'  />
  <input type='hidden' name='DROP_DHCP' value='$config->{'DROP_DHCP'}' />
  <input type='hidden' name='AUTH_TYPE' value='$config->{'AUTH_TYPE'}' />
  <input type='hidden' name='PUSH_GLOBAL_NETWORKS' value='$config->{'PUSH_GLOBAL_NETWORKS'}'>
  <input type='hidden' name='GLOBAL_NETWORKS' value='$config->{'GLOBAL_NETWORKS'}'>
  <input type='hidden' name='PUSH_GLOBAL_DNS' value='$config->{'PUSH_GLOBAL_DNS'}'>
  <input type='hidden' name='GLOBAL_DNS' value='$config->{'GLOBAL_DNS'}'>
  <input type='hidden' name='PUSH_DOMAIN' value='$config->{'PUSH_DOMAIN'}'>
  <input type='hidden' name='DOMAIN' value='$config->{'DOMAIN'}'>

EOF
;

    openbox('100%', 'left', _('Global settings'));
    printf <<EOF
<table columns="4" width="100%">
  <tr>
    <td width="38%">%s:</td>
    <td width="22%"><input type='checkbox' value='on' name='ENABLE' $checked{$enabled} /></td>
    <td width="20%">&nbsp;</td>
    <td width="20%">&nbsp;</td>
  </tr>

  <tr>
    <td>%s:</td>
    <td><input type='checkbox' value='on' name='BRIDGED' id='bridged' $checked{$config->{'BRIDGED'}} onclick="toggleBridged();"/></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>

  <tr id="purplenet">
    <td align="left">%s:</td>
    <td><input type='text' name='PURPLE_NET' value="$config->{'PURPLE_NET'}" SIZE="14" MAXLENGTH="15" /></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>

  <tr id="bridgeto">
    <td>%s:</td>
    <td>
      <select name="BRIDGE_TO">
EOF
, _('OpenVPN server enabled')
, _('Bridged')
, _('VPN subnet')
, _('Bridge to')
;

    my $zones = validzones();
    foreach my $zone (@$zones) {
	next if ($zone eq 'RED');
	printf <<EOF
        <option value="$zone" $selected{'BRIDGE_TO'}{$zone}>%s</option>
EOF
, $strings_zone{$zone}
;
    }

    printf <<EOF
      </select>
    </td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>

  <tr id="ippoolbegin">
    <td align="left">%s:</td>
    <td><input type='text' name='IPPOOL_BEGIN' value="$pool_begin" SIZE="14" MAXLENGTH="15" /></td>
    <td colspan="2" rowspan="2" valign="top">%s</td>
  </tr>

  <tr id="ippoolend">
    <td align="left">%s:</td>
    <td><input type='text' name='IPPOOL_END' value="$pool_end" SIZE="14" MAXLENGTH="15" /></td>
  </tr>

  <tr>
    <td>
      <input class='submitbutton' type='submit' name='ACTION_RESTART' value='%s' />
    </td>

    <td>
EOF
, _('Dynamic IP pool start address')
, _('Note: Traffic to this IP pool has to be filtered using the VPN firewall!')
, _('Dynamic IP pool end address')
, _('Save and restart')
;

    if ($canreadcacert) {
        printf <<EOF
      <a href="showca.cgi?type=pem">%s</a>
EOF
, _('Download CA certificate')
;
    } else {
	printf <<EOF
	    &nbsp;
EOF
;
    }


printf <<EOF
    </td>
    <td colspan="2">&nbsp;</td>
  </tr>

</table>
</form>
EOF
;

    closebox();


}


# -------------------------------------------------------------
# get settings and CGI parameters
# -------------------------------------------------------------
sub getconfig () {

    if (-e $hostconffile) {
	readhash($hostconffile, $host);
    }
    if (-e $conffile_default) {
	readhash($conffile_default, $conf);
    }
    if (-e $conffile) {
	readhash($conffile, $conf);
	$pool_begin = $conf->{PURPLE_IP_BEGIN};
	$pool_end = $conf->{PURPLE_IP_END};
    }

    my $greenaddress = '';
    if (-e $etherconf) {
	$ether = readconf($etherconf);

	my @green = split(/\./, $ether->{GREEN_ADDRESS});
	$netpart = $green[0].'.'.$green[1].'.'.$green[2];
	$greenaddress = $ether->{GREEN_ADDRESS};
    }

    $block_dhcp = $conf->{DROP_DHCP};
    $port = $conf->{OPENVPN_PORT};
    $protocol = $conf->{OPENVPN_PROTOCOL};

    $globalnetworks = $conf->{GLOBAL_NETWORKS};
    $globalnameserver = $conf->{GLOBAL_DNS};
    $domain = $conf->{DOMAIN};

    $globalnetworks =~ s/,/\n/g;
    $globalnameserver =~ s/,/\n/g;
    if ($domain =~ /^$/) {
        $domain = $host->{'DOMAINNAME'};
    }
    if ($globalnameserver =~ /^$/) {
	$globalnameserver = $greenaddress;
    }

    if ($conf->{'OPENVPN_ENABLED'} eq 'on') {
	$enabled = 1;
    }
    $config = $conf;

}

sub sanitize($) {
    my $data = shift;
    $data =~ s/\"/\\\"/;
    return $data;
}

getconfig();
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
my $extraheader = '<script language="JavaScript" src="/include/switchVisibility.js"></script>';

$extraheader .="
        <script type=\"text/javascript\">
	        function toggleBridged() {
	        	var checked = document.getElementById('bridged').checked;
	        	if (checked) {
	        		\$('#bridgeto').css({'display':'table-row'});
				\$('#ippoolbegin').css({'display':'table-row'});
				\$('#ippoolend').css({'display':'table-row'});
				\$('#purplenet').css({'display':'none'});
	        	} else {
	        		\$('#bridgeto').css({'display':'none'});
				\$('#ippoolbegin').css({'display':'none'});
				\$('#ippoolend').css({'display':'none'});
				\$('#purplenet').css({'display':'table-row'});
	        	}
	        }
	        \$(document).ready(function () {toggleBridged();});
        </script>
";

openpage($name, 1, $extraheader);

if (-e $dirtyfile) {
    $warnmessage = _('User configuration has been changed. Since it affects other users you may need to restart OpenVPN server in order to push the changes to the other clients.'). ' '._('Clients will reconnect automatically after a timeout.');
}

if (! -e $openvpn_diffie && -e $openvpn_diffie_lock) {
    $notemessage=_('OpenVPN is generating the Diffie Hellman parameters. This will take several minutes. During this time OpenVPN can <b>not</b> be started!');
}

$service_restarted = $needrestart;
service_notifications(["openvpnserver"], 
                      {'type' => $service_restarted == 1 ? "commit" : 
                                                           "observe",
                       'interval' => 500, 
                       'startMessage' => _("OpenVPN server is being restarted". 
                                           " Please hold..."),
                       'endMessage' => _("OpenVPN server was restarted " . 
                                         "successfully ")});

openbigbox($errormessage, $warnmessage, $notemessage);

display();
closebigbox();

openbigbox();
list_connections();
closebigbox();

closepage();

