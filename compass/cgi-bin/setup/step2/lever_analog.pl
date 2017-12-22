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
                1 => _('choose modem'),
		2 => _('supply connection information')
		);
my $substepnum = scalar(keys(%substeps));

my @analog_keys=(
		'DNS',
		'DNS1',
		'DNS2',
		
        'RED_IPS',

		'MTU',

		'TELEPHONE',

		'USERNAME',
		'PASSWORD',
		'AUTH',

		'MODEMTYPE',
		'COMPORT',
		'SPEED',
		'APN',

		'BACKUPPROFILE',
		'ENABLED',

	        'CHECKHOSTS',
	        'AUTOSTART',
	        'ONBOOT',
	        'MANAGED',

		'RED_TYPE'
		);


sub load_speeds() {
    my $index = 0;
    my @speeds = ();
    my $i = 0;

    my %hash = (
	'CONF_SPEED_LOOP_INDEX' => $i++,
	'CONF_SPEED_LOOP_NAME' => 'none',
	'CONF_SPEED_LOOP_CAPTION' => _('select a baud rate'),
	'CONF_SPEED_LOOP_SELECTED' => ($session->{'TYPE'} eq 'none' ? 'selected' : '')
	);
    push(@speedconf, \%hash);

    my @speeds = ('300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800');
    my $sel = 0;

    my $selection = $session->{'SPEED'};
    if (($selection =~ /^$/) && ($session->{'MODEMTYPE'} =~ /^(?:hsdpa|cdma)$/)) {
	$selection = '460800';
    }

    foreach my $speed (@speeds) {
	my $selected = '';
	if ($selection eq $speed) {
	    $selected = 'selected';
	}
	my %item = (
	    'CONF_SPEED_LOOP_INDEX' => $i++,
	    'CONF_SPEED_LOOP_NAME' => $speed,
	    'CONF_SPEED_LOOP_CAPTION' => $speed,
	    'CONF_SPEED_LOOP_SELECTED' => $selected
	    );
	push(@speedconf, \%item);
    }
    close(FILE);
    return \@speedconf;
}


sub load_modems() {
    my $index = 0;
    my @modems = ();
    my $i=0;

    my %hash = (
	'CONF_MODEMS_LOOP_INDEX' => $i++,
	'CONF_MODEMS_LOOP_NAME' => 'none',
	'CONF_MODEMS_LOOP_CAPTION' => _('select a serial port'),
	'CONF_MODEMS_LOOP_SELECTED' => ($session->{'TYPE'} eq 'none' ? 'selected' : '')
	);
    push(@modems, \%hash);

    my $modeminforef = iterate_comports();
    my @modeminfo = @$modeminforef;
    my $sel = 0;

    foreach my $modem (@modeminfo) {
	my $selected = '';
	if ($session->{'COMPORT'} eq '') {
	    if ((! $sel) && ($detected ne '')) {
		$selected = 'selected';
		$sel = 1;
	    }
	} elsif ($session->{'COMPORT'} eq $modem) {
	    $selected = 'selected';
	}

	my %item = (
	    'CONF_MODEMS_LOOP_INDEX' => $i++,
	    'CONF_MODEMS_LOOP_NAME' => $modem,
	    'CONF_MODEMS_LOOP_CAPTION' => $modem,
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


sub lever_prepare_values() {

    my $step = $live_data->{'step'};
    my $substep = $live_data->{'substep'};

    $tpl_ph->{'subtitle'} = _('Substep')." $substep/$substepnum: ".$substeps{$substep};

    if ($substep eq '1') {
	$tpl_ph->{'CONF_MODEMS_LOOP'} = load_modems();
        return;
    }

    if ($substep eq '2') {
	$session->{'DNS_N'} = '0';
    $tpl_ph->{'DISPLAY_RED_ADDITIONAL'} = $session->{'RED_IPS'};
	$tpl_ph->{'DISPLAY_RED_ADDITIONAL'} =~ s/,/\n/g;
	$tpl_ph->{'CONF_SPEED_LOOP'} = load_speeds();

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
	if ($par->{'COMPORT'} eq 'none') {
	    return _('you need to select a modem');
	}
        $session->{'COMPORT'} = $par->{'COMPORT'};
        $session->{'MODEMTYPE'} = $par->{'MODEMTYPE'};
    }

    if ($substep eq '2') {
	my %checked = ();
	$checked{0} = 'off';
	$checked{1} = 'on';

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

	if ($par->{'TELEPHONE'} !~ /^\d*$/) {
	    $ret .= _('invalid phone number');
	}
	$session->{'TELEPHONE'} = $par->{'TELEPHONE'};
	$session->{'SPEED'} = $par->{'SPEED'};

        if ($par->{'MTU'} !~ /^$/) {
            if ($par->{'MTU'} !~ /^\d+$/) {
                $ret .= _('The MTU value "%s" is invalid! Must be numeric.', $par->{'MTU'}).'<BR><BR>';
            }
  	    $session->{'MTU'} = $par->{'MTU'};
        } else {
  	    $session->{'MTU'} = '';
        }


        if ($session->{'MODEMTYPE'} eq "hsdpa") {
            if ($par->{'APN'} !~ /^[a-zA-Z]{1,1}[a-zA-Z0-9\.\-\_]{1,255}[a-zA-Z0-9]{1,1}$/) {
                $ret .= _('The APN host "%s" is invalid! Must be a hostname.', $par->{'APN'}).'<BR><BR>';
            }
	    $session->{'APN'} = $par->{'APN'};
        }
    	my ($ok_ips, $nok_ips) = createIPS("", $par->{'DISPLAY_RED_ADDITIONAL'});
    	if ($nok_ips eq '') {
    	    $session->{'RED_IPS'} = $ok_ips;
    	} else {
    	    foreach my $nokip (split(/,/, $nok_ips)) {
    		$ret .= _('The RED IP address or network mask "%s" is not correct.', $nokip).'<BR>';
    	    }
    	}
	return $ret;
    }

    return $ret;
}

sub alter_ppp_settings($) {
    my $ref = shift;
    my %config = %$ref;

    $config{'AUTH'} = get_auth_value($session->{'AUTH_N'});
    $config{'DNS'} = get_dns_value($session->{'DNS_N'});
    return \%config;
}


sub lever_apply() {
    my $ppp_settings = alter_ppp_settings(select_from_hash(\@analog_keys, $session));
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

