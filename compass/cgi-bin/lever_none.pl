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

my @static_keys = (
		   'RED_TYPE',
		   'DNS1',
		   'DNS2',
		   'DEFAULT_GATEWAY',
		   'CHECKHOSTS',
		   'RED_DEV',

		   'AUTOSTART',
		   'ONBOOT',
		   'ONBOOT',
		   'ENABLED',

		   );

my %substeps = (
		1 => _('Internet access preferences'),
		);
my $substepnum = scalar(keys(%substeps));

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
    return;
}

sub lever_savedata() {
    my $step = $live_data->{'step'};
    my $substep = $live_data->{'substep'};

    my $err = "";

    if ($substep eq '0') {
	die('invalid transition. step has no substeps');
    }
    $session->{'DNS_N'} = 1;


    my ($ok, $ip, $mask) = (0,0,0);
    ($ok, $ip, $mask) = check_ip($par->{'DEFAULT_GATEWAY'}, '255.255.255.0');
    if (! $ok) {
	$err .= _('The RED IP address or network mask is not correct.'). '<BR>';
    } else {
	$session->{'DEFAULT_GATEWAY'} = $ip;
    }

    return $err;
}

sub lever_apply() {
    $session->{'RED_DEV'} = $session->{'GREEN_DEV'};
    if (! $session->{'CHECKHOSTS'}) {
	$session->{'CHECKHOSTS'} = "127.0.0.1";
    }
    save_red('main', select_from_hash(\@static_keys, $session));
    return;
}

sub lever_check_substep() {
    return defined($substeps{$live_data->{'substep'}});
}

1;

