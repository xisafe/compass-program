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

use eReadconf;
require '/home/httpd/cgi-bin/netwizard_tools.pl';

my @dns=(
	 'Automatic',
	 'Manual'
	 );

my @auth=('pap-or-chap', 'pap', 'chap');


my @adsl_type=('RFC2364|', 
	       'RFC1483|PPPOE',
	       'RFC1483|STATIC',
	       'RFC1483|DHCP',
	       );


my @adsl_type_caption=(_('PPPoA'),
		       _('PPPoE'),
		       _('RFC1483 static ip'),
		       _('RFC1483 dhcp')
		       );

my $session = 0;

my $uplinks_etc = "/usr/lib/uplinks/";

sub init_modemtools($) {
    $session = shift;
}

sub get_dns_value($) {
    my $dns_n = shift;
    return $dns[$dns_n];
}

sub get_auth_value($) {
    my $auth_n = shift;
    return $auth[$auth_n];
}

sub get_adsl_type_value($) {
    my $adsl_type_n = shift;
    return $adsl_type[$adsl_type_n];
}

sub get_adsl_type_caption_value($) {
    my $adsl_type_caption_n = shift;
    return $adsl_type_caption[$adsl_type_caption_n];
}

sub ppp_load($$) {
    my $file = shift;
    my $override = shift;

    my $default = readconf($ppp_settings_file_default);
    my $conf = $default;

    if (-e $file) {
	$conf = readconf($file);
    }
    my @keys = keys(%$conf);
    load_all_keys($session, \@keys, $conf, $default, $override);
}

sub encap_values() {

    my @arr = ();
    my $vc = _('VCmux');
    my $llc = _('LLC');
    my $til = 2;

    if ($session->{'ADSL_TYPE_N'} > 1) {
	$vc = _('bridged VC');
	$llc = _('bridged LLC');
	$til = 4;
    }
    for (my $i=0; $i<$til; $i++) {

	my $name = '';
	my $caption = '';
	my $value = 0;

	if ($i == 0) {
	    $name = '0';
	    $caption = $vc;
	    $value = 0;
	}
	if ($i == 1) {
	    $name = '1';
	    $caption = $llc;
	    $value = 1;
	}
	if ($i == 2) {
	    $name = '2';
	    $caption = _('routed VC');
	    $value = 1;
	}
	if ($i == 3) {
	    $name = '3';
	    $caption = _('routed LLC');
	    $value = 1;
	}

	my %hash = (
		    'ENCAP_LOOP_INDEX'    => $i,
		    'ENCAP_LOOP_NAME'     => $name,
		    'ENCAP_LOOP_CAPTION'  => $caption,
		    'ENCAP_LOOP_SELECTED' => ($session->{'ENCAP'} == $name ? 'selected':'')
		    );
	push(@arr, \%hash);
    }

    return \@arr;
}


# some values in the settings files can't be processed by the wizard because they are combined
# into one field variable. this function creates values which are understandable for the wizard.
sub process_ppp_values($$) {

    my $conf = shift;
    my $override = shift;
    my @keys = ('AUTH_N', 'ADSL_TYPE_N', 'DNS_N');
    my %values = {};

    if ($conf->{'METHOD'} eq "PPPOE_PLUGIN") {
	$conf->{'METHOD'} = "PPPOE";
    }

    $values{'AUTH_N'} = get_pos(\@auth, $conf->{'AUTH'});
    $values{'ADSL_TYPE_N'} = get_pos(\@adsl_type, $conf->{'PROTOCOL'}.'|'.$conf->{'METHOD'});
    $values{'DNS_N'} = get_pos(\@dns, $conf->{'DNS'});

    load_all_keys($session, \@keys, \%values, 0, $override);
}

sub iterate_comports() {
    my $dir = "/dev/";
    my @ret = glob("/dev/ttyS*");
    push(@ret, glob("/dev/ttyUSB*"));
    push(@ret, glob("/dev/ttyACM*"));
    return \@ret;
}

sub iterate_modems($) {
    my $type = shift;
    my $dir = "$uplinks_etc/$type/";

    my @ret = ();

    opendir(DIR, $dir);
    @names = readdir(DIR) or return \@ret;
    foreach my $name (@names) {
        next if ($name eq ".");
        next if ($name eq "..");
        next if (! -e "$dir/$name/info");
	push(@ret, $name);
    };
    return \@ret;
}

sub get_info($$) {
    my $type = shift;
    my $modem = shift;

    open (FILE, "$uplinks_etc$type/$modem/info") or return '';
    my @f = <FILE>;
    close(FILE);

    return $f[0];
}

sub detect($$) {
    my $type = shift;
    my $modem = shift;
    return `$uplinks_etc$type/$modem/detect`;
}


1;

