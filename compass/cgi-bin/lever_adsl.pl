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

# this module contains adsl relevant code


require 'header.pl' if (-e 'header.pl');  # if called from ipcop, header-pl is
                                          # already included.

require '/home/httpd/cgi-bin/netwizard_tools.pl';
require '/home/httpd/cgi-bin/modemtools.pl';
use eReadconf;

my @need_auth=('RFC2364|',
	       'RFC1483|PPPOE',
	       '',
	       ''
	       );

my @no_auto_dns=('',
		 '',
		 'RFC1483|STATIC',
		 '',
		 );

my @ppp_keys=(
	      'BROADCAST',
	      'GATEWAY',
	      'IP',
	      'NETMASK',
	      'CIDR',
          'RED_IPS',

	      'MTU',

	      'VCI',
	      'VPI',
	      'ENCAP',
	      'PASSWORD',
	      'USERNAME',
	      'TYPE',
	      'AUTH',
	      'PROTOCOL',
	      'METHOD',
	      'DNS',
	      'DNS1',
	      'DNS2',
	      'MAXRETRIES',

	      'BACKUPPROFILE',
	      'ENABLED',
	      'RED_TYPE',

	      'CHECKHOSTS',
	      'AUTOSTART',
	      'ONBOOT',
	      'MANAGED',

	      );




my %substeps = (
		1 => _('choose modem'),
		2 => _('choose ADSL connection type'),
		3 => _('supply connection information')
		);
my $substepnum = scalar(keys(%substeps));

my $session = 0;
my $settings = 0;
my $par = 0;
my $tpl_ph = 0;
my $live_data = 0;

sub is_adsl_static() {
    return ($session->{'ADSL_TYPE_N'} == 2);
}

sub load_modems() {
    my $index = 0;
    my @modems = ();
    my $i=0;

    my %hash = (
	'CONF_MODEMS_LOOP_INDEX' => $i++,
	'CONF_MODEMS_LOOP_NAME' => 'none',
	'CONF_MODEMS_LOOP_CAPTION' => _('select a modem'),
	'CONF_MODEMS_LOOP_SELECTED' => ($session->{'TYPE'} eq 'none' ? 'selected' : '')
	);
    push(@modems, \%hash);

    my $modeminforef = iterate_modems('adsl');
    my @modeminfo = @$modeminforef;
    my $sel = 0;

    foreach my $modem (@modeminfo) {
	my $caption = get_info('adsl',$modem);
	next if ($caption eq '');

	my $detected = '';
	if (detect('adsl',$modem) > 0) {
	    $caption .= ' '.'-->'._('detected').'<--';
	    $detected = 1;
	}

	my $selected = '';
	if ($session->{'TYPE'} eq '') {
	    if ((! $sel) && ($detected ne '')) {
		$selected = 'selected';
		$sel = 1;
	    }
	} elsif ($session->{'TYPE'} eq $modem) {
	    $selected = 'selected';
	}

	my %item = (
	    'CONF_MODEMS_LOOP_INDEX' => $i++,
	    'CONF_MODEMS_LOOP_NAME' => $modem,
	    'CONF_MODEMS_LOOP_CAPTION' => $caption,
	    'CONF_MODEMS_LOOP_SELECTED' => $selected
	    );
	push(@modems, \%item);
    }
    close(FILE);
    return \@modems;
}

sub alter_ppp_settings($) {
    my $ref = shift;
    my %config = %$ref;

    $config{'AUTH'} = get_auth_value($session->{'AUTH_N'});
    ($config{'PROTOCOL'}, $config{'METHOD'}) = split(/\|/, get_adsl_type_value($session->{'ADSL_TYPE_N'}));
    $config{'DNS'} = get_dns_value($session->{'DNS_N'});
    # set maxretries
    $config{'MAXRETRIES'} = 5;
    return \%config;
}


#
#
#
#  functions which are defined in the interface
#
#

sub lever_init($$$$$) {
    $session = shift;
    $settings = shift;
    $par = shift;
    $tpl_ph = shift;
    $live_data = shift;

    init_modemtools($session);
}



sub lever_load() {

    # custom, load from ppp-file
    process_ppp_values($session, 0);
}


sub lever_prepare_values() {

    my $step = $live_data->{'step'};
    my $substep = $live_data->{'substep'};

    $tpl_ph->{'subtitle'} = _('Substep')." $substep/$substepnum: ".$substeps{$substep};

    if ($substep eq '1') {
	$tpl_ph->{'CONF_MODEMS_LOOP'} = load_modems();
	return;
    }

    if ($substep eq '3') {
	$tpl_ph->{'ADSL_TYPE_CAPTION'} = get_adsl_type_caption_value($session->{'ADSL_TYPE_N'});
	my $encap_values = encap_values();
	$tpl_ph->{'ENCAP_LOOP'} = $encap_values;

	my $encap = @$encap_values[$session->{'ENCAP'}];
	$tpl_ph->{'ENCAP_CAPTION'} = $encap->{'ENCAP_LOOP_CAPTION'};
    
	if (is_adsl_static()) {
	    $tpl_ph->{'STATIC'} = 1;
        $tpl_ph->{'DISPLAY_RED_ADDITIONAL'} = getAdditionalIPs($session->{'RED_IPS'});
        $tpl_ph->{'DISPLAY_RED_ADDITIONAL'} =~ s/,/\n/g;
	}
    else {
        $tpl_ph->{'DISPLAY_RED_ADDITIONAL'} = $session->{'RED_IPS'};
        $tpl_ph->{'DISPLAY_RED_ADDITIONAL'} =~ s/,/\n/g;
    }
	return;
    }

}

# check the parameters according to substep
# and put the valid parameters to the session
# return error message if an invalid parameter was found
sub lever_savedata() {
    my $step = $live_data->{'step'};
    my $substep = $live_data->{'substep'};

    $session->{'RED_DEV'} = unset;
    $session->{'RED_DEVICES'} = unset;
    if ($substep eq '0') {
	die('invalid transition. step has no substeps');
    }
    if ($substep eq '1') {

	if ($par->{'TYPE'} eq 'none') {
	    return _('you need to select a modem');
	}
	$session->{'TYPE'} = $par->{'TYPE'};
	return;
    }

    if ($substep eq '2') {
	$session->{'ADSL_TYPE_N'} = $par->{'ADSL_TYPE_N'};
	if ($need_auth[$session->{'ADSL_TYPE_N'}] ne '') {
	    $session->{'AUTHENTICATION'} = 1;
	} else {
	    undef $session->{'AUTHENTICATION'};
	}
	$session->{'ASK_DNSMANUAL'} = 1;
	if ($no_auto_dns[$session->{'ADSL_TYPE_N'}] ne '') {
	    $session->{'DNS_N'} = 1;
	    undef $session->{'ASK_DNSMANUAL'};
	}
	return;
    }

    if ($substep eq '3') {

        if ($par->{'MTU'} !~ /^$/) {
            if ($par->{'MTU'} !~ /^\d+$/) {
                $err .= _('The MTU value "%s" is invalid! Must be numeric.', $par->{'MTU'}).'<BR><BR>';
            }
  	    $session->{'MTU'} = $par->{'MTU'};
        } else {
  	    $session->{'MTU'} = '__EMPTY__';
        }

	my $ret = '';
	if ($session->{'AUTHENTICATION'} == 1) {
	    $session->{'AUTH_N'} = $par->{'AUTH_N'};
	    if ($par->{'USERNAME'} eq '') {
		$ret .= _('you must supply a username for the authentication on your provider');
	    }
	    if ($par->{'PASSWORD'} eq '') {
		$ret .= _('you must supply a password for the authentication on your provider');
	    }
	    $session->{'USERNAME'} = $par->{'USERNAME'};
	    $session->{'PASSWORD'} = $par->{'PASSWORD'};
	}

	$session->{'ENCAP'} = $par->{'ENCAP'};
	if (($par->{'VPI'} eq '') or 
	    ($par->{'VCI'} eq '')) {
	    $ret .= _('no VPI or VCI number supplied');
	} else {
	    $session->{'VPI'} = $par->{'VPI'};
	    $session->{'VCI'} = $par->{'VCI'};
	}
    
	if (is_adsl_static()) {
	    my $ip = '';
	    my $mask = '';
	    my $err = '';

	    ($err, $ip, $mask) = check_ip($par->{'IP'}, $par->{'NETMASK'});
	    if ($err) {
		$session->{'IP'} = $ip;
		$session->{'NETMASK'} = $mask;
		$session->{'CIDR'} = ipv4_msk2cidr($mask);
	    } else {
		$ret .= _('The IP address or network mask is not correct.').'<BR>';
	    }
	    my ($ok_ips, $nok_ips) = createIPS($par->{'IP'}.'/'.$par->{'NETMASK'}, $par->{'DISPLAY_RED_ADDITIONAL'});
    	if ($nok_ips eq '') {
    	    $session->{'RED_IPS'} = $ok_ips;
    	} else {
    	    foreach my $nokip (split(/,/, $nok_ips)) {
    		$ret .= _('The RED IP address or network mask "%s" is not correct.', $nokip).'<BR>';
    	    }
    	}
	    ($err, $ip, $mask) = check_ip($par->{'GATEWAY'}, $par->{'NETMASK'});
	    if ($err) {
		$session->{'GATEWAY'} = $ip;
	    } else {
		$ret .= _('The gateway address is not correct.').'<BR>';
	    }
	}
    else {
        my ($ok_ips, $nok_ips) = createIPS("", $par->{'DISPLAY_RED_ADDITIONAL'});
    	if ($nok_ips eq '') {
    	    $session->{'RED_IPS'} = $ok_ips;
    	} else {
    	    foreach my $nokip (split(/,/, $nok_ips)) {
    		$ret .= _('The RED IP address or network mask "%s" is not correct.', $nokip).'<BR>';
    	    }
    	}
    }
	
	if ($session->{'ASK_DNSMANUAL'} == 1) {
	    $session->{'DNS_N'} = $par->{'DNS_N'};
	}

	if ($ret ne '') {
	    return $ret;
	}
	return;
    }
}

sub lever_apply() {
    my $ppp_settings = alter_ppp_settings(select_from_hash(\@ppp_keys, $session));
    set_red_default('');
    save_red('main', $ppp_settings);
}

sub lever_check_substep() {
    return defined($substeps{$live_data->{'substep'}});
}


1;
