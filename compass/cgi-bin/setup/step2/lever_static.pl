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

require '/home/httpd/cgi-bin/ifacetools.pl';
require '/home/httpd/cgi-bin/redtools.pl';

my %substeps = ();
my $session = 0;
my $settings = 0;
my $par = 0;
my $tpl_ph = 0;
my $live_data = 0;


my %substeps = (
		1 => _('Internet access preferences'),
		);
my $substepnum = scalar(keys(%substeps));

my @static_keys=(
		 'DNS1',
		 'DNS2',

		 'MTU',
                 'MAC',

		 'BACKUPPROFILE',
		 'ENABLED',
		 
		 'RED_DEV',
		 'RED_ADDRESS',
		 'RED_NETMASK',
		 'RED_CIDR',
		 'RED_NETADDRESS',
		 'RED_BROADCAST',
		 'DEFAULT_GATEWAY',
		 'RED_TYPE',
		 'RED_IPS',

		 'CHECKHOSTS',
		 'AUTOSTART',
		 'ONBOOT',
		 'MANAGED',

		);


sub lever_init($$$$$) {
    $session = shift;
    $settings = shift;
    $par = shift;
    $tpl_ph = shift;
    $live_data = shift;

    init_ifacetools($session, $par);
    init_redtools($session, $settings);
}


sub lever_load() {
    return;
}


sub lever_prepare_values() {

    my $step = $live_data->{'step'};
    my $substep = $live_data->{'substep'};

    $tpl_ph->{'subtitle'} = _('Substep')." $substep/$substepnum: ".$substeps{$substep};

    if ($substep eq '1') {
	$session->{'DNS_N'} = '1';

	my ($primary, $ip, $mask, $cidr) = getPrimaryIP($session->{'RED_IPS'});
	$tpl_ph->{'DISPLAY_RED_ADDRESS'} = $ip;
	$tpl_ph->{'DISPLAY_RED_NETMASK_LOOP'} = loadNetmasks($cidr);
	$tpl_ph->{'DISPLAY_RED_ADDITIONAL'} = getAdditionalIPs($session->{'RED_IPS'});
	$tpl_ph->{'DISPLAY_RED_ADDITIONAL'} =~ s/,/\n/g;
	$tpl_ph->{'IFACE_RED_LOOP'} = create_ifaces_list('RED');
	return;
    }
    return;
}

sub lever_savedata() {
    my $step = $live_data->{'step'};
    my $substep = $live_data->{'substep'};

    my $err = "";

    if ($substep eq '0') {
	die('invalid transition. step has no substeps');
    }

    if ($substep eq '1') {

	if ($session->{'ASK_DNSMANUAL'}) {
	    $session->{'DNS_N'} = $par->{'DNS_N'};
	}

	my $ifacelist = ifnum2device($par->{'RED_DEVICES'});
	my $reterr = check_iface_free($ifacelist, 'RED');
	if ($reterr) {
	    $err .= $reterr;
	} else {
	    $session->{'RED_DEVICES'} = $ifacelist;
	}
        if ($ifacelist =~ /^$/) {
            my $zone = _('RED');
	    $err .= _('Please select at least one interface for zone %s!', $zone).'<BR><BR>';
        }

        if ($par->{'MTU'} !~ /^$/) {
            if ($par->{'MTU'} !~ /^\d+$/) {
                $err .= _('The MTU value "%s" is invalid! Must be numeric.', $par->{'MTU'}).'<BR><BR>';
            }
  	    $session->{'MTU'} = $par->{'MTU'};
        } else {
  	    $session->{'MTU'} = '__EMPTY__';
        }

        if ($par->{'MAC'} !~ /^$/) {
            if (! validmac($par->{'MAC'})) {
                $err .= _('The MAC address "%s" is invalid. Correct format is: xx:xx:xx:xx:xx:xx!', $par->{'MAC'});
            }
            $session->{'MAC'} = $par->{'MAC'};
        } else {
  	    $session->{'MAC'} = '__EMPTY__';
        }

	if ($err ne '') {
	    return $err;
	}

	my ($ok_ips, $nok_ips) = createIPS($par->{'DISPLAY_RED_ADDRESS'}.'/'.$par->{'DISPLAY_RED_NETMASK'}, $par->{'DISPLAY_RED_ADDITIONAL'});
	if ($nok_ips eq '') {
	    $session->{'RED_IPS'} = $ok_ips;
	} else {
	    foreach my $nokip (split(/,/, $nok_ips)) {
		$err .= _('The RED IP address or network mask "%s" is not correct.', $nokip).'<BR>';
	    }
	}


	($valid, $ip, $mask) = check_ip($par->{'DEFAULT_GATEWAY'}, '255.255.255.255');
	if ($valid) {
	    $session->{'DEFAULT_GATEWAY'} = $ip;
	} else {
	    $err .= _('The gateway address is not correct.').'<BR>';
	}

	if ($err ne '') {
	    return $err;
	}

	if (network_overlap($session->{'RED_IPS'}, $session->{'GREEN_IPS'})) {
	    $err .= _('The RED and GREEN networks are not distinct.').'<BR>';
	}
	if (network_overlap($session->{'GREEN_IPS'}, $session->{'DEFAULT_GATEWAY'}. '/32')) {
	    $err .= _('The DEFAULT GATEWAY is within the GREEN network.').'<BR>';
	}
	if (orange_used()) {
	    if (network_overlap($session->{'RED_IPS'}, $session->{'ORANGE_IPS'},)) {
		$err .= _('The RED and ORANGE networks are not distinct.').'<BR>';
	    }
	    if (network_overlap($session->{'ORANGE_IPS'}, $session->{'DEFAULT_GATEWAY'}. '/32')) {
		$err .= _('The DEFAULT GATEWAY is within the ORANGE network.').'<BR>';
	    }
	}
	if (blue_used()) {
	    if (network_overlap($session->{'RED_IPS'}, $session->{'BLUE_IPS'})) {
		$err .= _('The RED and BLUE networks are not distinct.').'<BR>';
	    }
	    if (network_overlap($session->{'BLUE_IPS'}, $session->{'DEFAULT_GATEWAY'}. '/32')) {
		$err .= _('The DEFAULT GATEWAY is within the BLUE network.').'<BR>';
	    }
	}
	return $err;
    }

    return $err;
}

sub lever_apply() {
    my ($primary,$ip,$mask,$cidr) = getPrimaryIP($session->{'RED_IPS'});
    $session->{'RED_ADDRESS'} = $ip;
    $session->{'RED_NETMASK'} = $mask;
    $session->{'RED_CIDR'} = $cidr;

    ($session->{'RED_NETADDRESS'},) = ipv4_network($primary);
    $session->{'RED_BROADCAST'} = ipv4_broadcast($primary);
    $session->{'RED_DEV'} = pick_device($session->{'RED_DEVICES'});
    save_red('main', select_from_hash(\@static_keys, $session));
    return;
}

sub lever_check_substep() {
    return defined($substeps{$live_data->{'substep'}});
}


1;

