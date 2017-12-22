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
require '/home/httpd/cgi-bin/modemtools.pl';
require '/home/httpd/cgi-bin/redtools.pl';

my %substeps = ();
my $session = 0;
my $settings = 0;
my $par = 0;
my $tpl_ph = 0;
my $live_data = 0;

my %substeps = (
		1 => _('supply connection information')
		);
my $substepnum = scalar(keys(%substeps));

my @isdn_keys=(
		'DNS',
		'DNS1',
		'DNS2',

        'RED_IPS',

		'MTU',

		'TYPE',
		'PROTOCOL',
		'MODULE_PARAMS',

		'TIMEOUT',
		'USEDOV',
		'USEIBOD',
		'TELEPHONE',
		'BOTHCHANNELS',
		'MAXRETRIES',
		'MSN',

		'USERNAME',
		'PASSWORD',
		'AUTH',

		'BACKUPPROFILE',
		'ENABLED',

	        'CHECKHOSTS',
	        'AUTOSTART',
	        'ONBOOT',
	        'MANAGED',

		'RED_TYPE'
		);


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

    my $modeminforef = iterate_modems('isdn');
    my @modeminfo = @$modeminforef;
    my $sel = 0;

    foreach my $modem (@modeminfo) {
	my $caption = get_info('isdn',$modem);
	next if ($caption eq '');

	my $detected = '';
	if (detect('isdn',$modem) > 0) {
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


sub lever_init($$$$$) {
    $session = shift;
    $settings = shift;
    $par = shift;
    $tpl_ph = shift;
    $live_data = shift;
    init_modemtools($session);
}


sub lever_load() {
    process_ppp_values($session, 0);
    return;
}


sub load_timeouts() {
    my @timeouts = ();
    my $i = 0;
    foreach my $item (qw 'off 1 2 5 10 15 20 30 60 120') {
	my %hash = (
		'CONF_TIMEOUT_LOOP_INDEX' => $i++,
		'CONF_TIMEOUT_LOOP_NAME' => $item,
		'CONF_TIMEOUT_LOOP_CAPTION' => $item,
		'CONF_TIMEOUT_LOOP_SELECTED' => ($session->{'TIMEOUT'} eq $item ? 'selected' : '')
		);
	push(@timeouts, \%hash);
    }
    return \@timeouts;
}

sub lever_prepare_values() {

    my $step = $live_data->{'step'};
    my $substep = $live_data->{'substep'};

    $tpl_ph->{'subtitle'} = _('Substep')." $substep/$substepnum: ".$substeps{$substep};

    if ($substep eq '1') {
	$session->{'DNS_N'} = '0';
	$tpl_ph->{'CONF_MODEMS_LOOP'} = load_modems();
	$tpl_ph->{'CONF_TIMEOUT_LOOP'} = load_timeouts();
    $tpl_ph->{'DISPLAY_RED_ADDITIONAL'} = $session->{'RED_IPS'};
	$tpl_ph->{'DISPLAY_RED_ADDITIONAL'} =~ s/,/\n/g;
	if ($session->{'USEDOV'} eq 'on') {
	    $tpl_ph->{'USEDOV_SELECTED'} = 'checked';
	}
	if ($session->{'BOTHCHANNELS'} eq 'on') {
	    $tpl_ph->{'BOTHCHANNELS_SELECTED'} = 'checked';
	}
	if ($session->{'USEIBOD'} eq 'on') {
	    $tpl_ph->{'USEIBOD_SELECTED'} = 'checked';
	}
	return;
    }

    return;
}

sub lever_savedata() {
    my $step = $live_data->{'step'};
    my $substep = $live_data->{'substep'};

    my $ret = '';

    if ($substep eq '0') {
	die('invalid transition. step has no substeps');
    }

    if ($substep eq '1') {
	my %checked = ();
	$checked{0} = 'off';
	$checked{1} = 'on';

	if ($par->{'TYPE'} eq 'none') {
	    $ret .= _('you need to select a modem');
	}
	$session->{'TYPE'} = $par->{'TYPE'};

	if ($par->{'USERNAME'} eq '') {
	    $ret .= _('you must supply a username for the authentication on your provider');
	}
	if ($par->{'PASSWORD'} eq '') {
	    $ret .= _('you must supply a password for the authentication on your provider');
	}
	$session->{'USERNAME'} = $par->{'USERNAME'};
	$session->{'PASSWORD'} = $par->{'PASSWORD'};

	$session->{'AUTH_N'} = $par->{'AUTH_N'};
	$session->{'DNS_N'} = $par->{'DNS_N'};

	if ($par->{'TELEPHONE'} !~ /\d+/) {
	    $ret .= _('invalid phone number');
	}
	$session->{'TELEPHONE'} = $par->{'TELEPHONE'};

	my ($ok_ips, $nok_ips) = createIPS("", $par->{'DISPLAY_RED_ADDITIONAL'});
	if ($nok_ips eq '') {
	    $session->{'RED_IPS'} = $ok_ips;
	} else {
	    foreach my $nokip (split(/,/, $nok_ips)) {
		$ret .= _('The RED IP address or network mask "%s" is not correct.', $nokip).'<BR>';
	    }
	}

        if ($par->{'MTU'} !~ /^$/) {
            if ($par->{'MTU'} !~ /^\d+$/) {
                $ret .= _('The MTU value "%s" is invalid! Must be numeric.', $par->{'MTU'}).'<BR><BR>';
            }
  	    $session->{'MTU'} = $par->{'MTU'};
        } else {
  	    $session->{'MTU'} = '__EMPTY__';
        }

    if ($ret ne '') {
        return $ret;
    }
	if (!$par->{'USEDOV'}) {
	    $par->{'USEDOV'} = 0;
	}
	if (!$par->{'BOTHCHANNELS'}) {
	    $par->{'BOTHCHANNELS'} = 0;
	}
	if (!$par->{'USEIBOD'}) {
	    $par->{'USEIBOD'} = 0;
	}

	$session->{'USEDOV'} = $checked{$par->{'USEDOV'}};
	$session->{'BOTHCHANNELS'} = $checked{$par->{'BOTHCHANNELS'}};
	$session->{'USEIBOD'} = $checked{$par->{'USEIBOD'}};

	$session->{'TIMEOUT'} = $par->{'TIMEOUT'};
        if ($par->{'MTU'} !~ /^$/) {
	    $session->{'MSN'} = $par->{'MSN'};
	} else {
	    $session->{'MSN'} = '__EMPTY__';
	}
	return $ret;
    }

    return $ret;
}

sub alter_ppp_settings($) {
    my $ref = shift;
    my %config = %$ref;

    if ($config{'TIMEOUT'} !~ /^\d+$/) {
	$config{'TIMEOUT'} = 0;
    }
    $config{'PROTOCOL'} = '0'; # boh (hdlc == default)
    $config{'MODULE_PARAMS'} = ''; # boh

    $config{'AUTH'} = get_auth_value($session->{'AUTH_N'});
    $config{'DNS'} = get_dns_value($session->{'DNS_N'});
    # set maxretries
    $config{'MAXRETRIES'} = 5;
    return \%config;
}


sub lever_apply() {
    my $ppp_settings = alter_ppp_settings(select_from_hash(\@isdn_keys, $session));
    if ($session->{'DNS_N'} == 0) {
	$session->{'DNS1'} = "";
	$session->{'DNS2'} = "";
    }
    save_red('main', $ppp_settings);
    return;
}


sub lever_check_substep() {
    return defined($substeps{$live_data->{'substep'}});
}


1;

