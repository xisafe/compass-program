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

if (-e 'header.pl') {
    require 'header.pl';
} else {
    require '/var/efw/header.pl';
}
require '/home/httpd/cgi-bin/ethconfig.pl';
require '/home/httpd/cgi-bin/netwizard_tools.pl';

my $session = 0;
my %ifaces = {};
my @validifaces= qw 'eth vlan';
my $bridgefiles = 'ethernet/';
my $par = 0;
my %console;
readhash("/var/efw/console/settings",\%console);
my $interface_number = `ifconfig |grep eth |wc -l`;
my $enabled = "on";
if($console{"ENABLED"} eq "off" || $console{"ENABLED_NUMBER"} > $interface_number ){
	$enabled = "off";
}
sub validzones() {
    my @ret = ();

    push(@ret, 'GREEN');
    if (orange_used()) {
	push(@ret, 'ORANGE');
    }
    if (blue_used()) {
	push(@ret, 'BLUE');
    }
    if (!is_modem()) {
	push(@ret, 'RED');
    }

    return \@ret;
}

sub blank_config() {
    foreach my $zone (@zones) {
	$session->{$zone.'_DEVICES'} = "";
    }
}

sub load_ifacesconfig() {
    blank_config();
    my $validzones=validzones();
    foreach my $zone (@$validzones) {
	my $devicelist = 0;
	if ($zone eq 'RED') {
	    my %mainuplink = ();
	    if (-e "${swroot}/uplinks/main/settings") {
		&readhash("${swroot}/uplinks/main/settings", \%mainuplink);
	    };
            my @devarr = ();
            $devicelist = \@devarr;
            push(@devarr, $mainuplink{'RED_DEV'});
	} else {
	    $devicelist = get_zone_devices($session->{$zone.'_DEV'});
	}

	foreach my $dev (@$devicelist) {
	    $session->{$zone.'_DEVICES'} .= $dev.'|';
	}
    }
}

sub load_ifaces() {
    load_ifacesconfig();
    my $validzones=validzones();
    if (! -e "${swroot}/main/initial_wizard_step2") {
	foreach my $zone (@$validzones) {
	    if (($session->{$zone.'_DEVICES'}) && ($zone ne 'GREEN')) {
		return;
	    }
	}
    }
    setdefaultifaces();
}

sub setdefaultifaces() {
    my $devices = listdevices(1);
    my $i = 0;
    foreach my $item (@$devices) {
	my $dev = $item->{"device"};
	if ($i==0) {
	    $session->{"GREEN_DEVICES"}=$dev;
	}
	if ($i==1) {
	    if (orange_used()) {
		$session->{"ORANGE_DEVICES"}=$dev;
	    }
	}
	if ($i==2) {
	    if (blue_used()) {
		$session->{"BLUE_DEVICES"}=$dev;
	    }
	}
	if ($i==3) {
	    if (!is_modem()) {
		$session->{"RED_DEVICES"}=$dev;
	    }
	}
	if ($i>=4) {
	    $session->{"GREEN_DEVICES"}.='|'.$dev;
	}
	$i++;
    }
}

sub ifisinzone($$) {
    my $conf=shift;
    my $dev=shift;
    my $search=$conf.'|';
    if ($search =~ /$dev\|/) {
	return $dev;
    }
    return 0;
}

sub getzonebyiface($) {
    my $dev = shift;

    my $validzones=validzones();
    foreach my $zone (@$validzones) {
	if (ifisinzone($session->{$zone.'_DEVICES'}, $dev)) {
	    return $zone;
	}
    }
    return "";
}

sub ifacesusedbyzone($$) {
    my $devs = shift;
    my $zone = shift;

    return 0 if (! $session->{$zone.'_DEVICES'});

    foreach my $dev (split(/\|/, $devs)) {
	chomp($dev);
	next if ($dev =~ /^$/);
	my $retdev=ifisinzone($session->{$zone.'_DEVICES'}, $dev);
	return $retdev if ($retdev);
    }
    return 0;
}

sub init_ifacetools($$) {
    $session = shift;
    $par = shift;
    $bridgefiles = ${swroot}.'/ethernet/';
}

sub get_if_number() {
    if ($session->{'IF_COUNT'}) {
	return $session->{'IF_COUNT'};
    }
    my ($devices) = list_devices_description(3, -1, 0);
    my @devarr = @$devices;
    $session->{'IF_COUNT'} = $#devarr + 1;
    return $session->{'IF_COUNT'};
}

sub pick_device($) {
    my $devices=shift;
    my @arr = split(/\|/, $devices);
    return $arr[0];
}

sub isvalidzone($) {
    my $zone = shift;
    my $validzones=validzones();
    if (defined(get_pos($validzones, $zone))) {
	return 1;
    }
    return 0;
}

sub get_iface_by_name($) {
    my $name = shift;
    my $devices = listdevices(1);
    foreach my $dev (@$devices) {
	if ($dev->{'device'} eq $name) {
	    return $dev
	}
    }
    return 0;
}


sub disable_conflicting_uplinks($) {
    my $device = shift;
    my $uplinks = get_uplink_by_device($device);
    foreach my $ul (@$uplinks) {
	if (($ul !~ /^$/) && ($ul ne 'main')) {
	    disable_uplink($ul);
	}
    }
}

sub write_ifaces($$) {
    my $file = shift;
    my $selecteddevices = shift;

    my %devices = ();

    foreach my $dev (split(/\|/, $selecteddevices)) {
	next if $dev =~ /^$/;
	my $device = get_iface_by_name($dev);
	next if ($device eq 0);
	my $bond = $device->{'bond'};
	if ($bond =~ /^$/) {
	    $devices{$dev} = 1;
	}
	disable_conflicting_uplinks($dev);
    }

    if (!open(F, ">$file")) {
	warn("Could not open '$file' because $!");
	return;
    }
    print F join("\n", keys(%devices));
    print F "\n";
    close(F);
	`sudo fmodify $file`;
}

sub write_bridges() {
    foreach my $zone (@zones) {
	next if ($zone eq "RED");
	my $devices = "";
	if (isvalidzone($zone)) {
	    $devices = $session->{$zone.'_DEVICES'};
	}
	my $ifacename=$session->{$zone.'_DEV'};
	next if ($ifacename =~ /^$/);
	write_ifaces($bridgefiles.$ifacename, $devices);
    }
}

sub create_ifaces_list($) {
    my $zone = shift;

    my @prof = ();
    my $index = 0;

    my ($devices) = list_devices_description(3, -1, 1);

    foreach my $item (@$devices) {
	my $assignedzone = getzonebyiface($item->{'device'});
	my $selected = ($zone eq $assignedzone);
	my $disabled = 0;
	my $hide = 0;
	if ($zone eq 'RED') {
	    if (! $selected && $assignedzone) {
		$hide = 1;
		$disabled = 1;
	    }
	}
	if (($assignedzone eq '') && ($item->{'zone'} eq 'RED')) {
	    $assignedzone = 'RED';
	}

	my %hash = (
	    DEV_LOOP_INDEX => $index,
	    DEV_LOOP_NAME => $item->{'index'},
	    DEV_LOOP_PORT => $item->{'port'},
	    DEV_LOOP_DESCRIPTION => $item->{'description'},
	    DEV_LOOP_SHORT_DESC => $item->{'shortdesc'},
            DEV_LOOP_MAC => $item->{'mac'},
            DEV_LOOP_LINK => $item->{'link'},
            DEV_LOOP_LINKCAPTION => $item->{'linkcaption'},
            DEV_LOOP_LINKICON => $item->{'linkicon'},
            DEV_LOOP_BGCOLOR => (($index % 2) ? 'even' : 'odd'),
	    DEV_LOOP_SELECTED => ($selected ? 'selected' : ''),
	    DEV_LOOP_CHECKED => ($selected ? 'checked' : ''),
            DEV_LOOP_ZONECOLOR => $zonecolors{$assignedzone},
            DEV_LOOP_DISABLED => ($disabled ? 'disabled' : ''),
            DEV_LOOP_HIDE => ($hide ? 'hide' : ''),
            DEV_LOOP_DEVICE => $item->{'device'},
			ENABLED => $enabled,
	    );
	push(@prof, \%hash);

	$index++;
    }

    return \@prof;
}

sub check_iface_free($$) {
    my $devices = shift;
    my $zone = shift;
    my $err = "";

    if ($zone eq 'GREEN') {
	return $err;
    }
    
    my $greendev = ifacesusedbyzone($devices, 'GREEN');
    if ($greendev) {
	$err .= $greendev.' '._('interface already assigned to zone %s', _('GREEN')).'<BR>';
    }
    if ($zone eq 'ORANGE') {
	return $err;
    }

    if (orange_used()) {
	my $orangedev = ifacesusedbyzone($devices, 'ORANGE');
	if ($orangedev) {
	    $err .= $orangedev.' '._('interface already assigned to zone %s', _('ORANGE')).'<BR>';
	}
    }
    if ($zone eq 'BLUE') {
	return $err;
    }

    if (blue_used()) {
	my $bluedev = ifacesusedbyzone($devices, 'BLUE');
	if ($bluedev) {
	    $err .= $bluedev.' '._('interface already assigned to zone %s', ('BLUE')).'<BR>';
	}
    }

    return $err;
}


# checks if there are overlappings in the address spaces.
sub network_overlap($$) {
    my $subnetlist1 = shift;
    my $subnetlist2 = shift;

    foreach my $subnet1 (split(/,/, $subnetlist1)) {
	foreach my $subnet2 (split(/,/, $subnetlist2)) {
	    if (ipv4_in_network($subnet1, $subnet2)) {
		return 1;
	    }
	    if (ipv4_in_network($subnet2, $subnet1)) {
		return 1;
	    }
	}
    }
    return 0;
}


# store the ip/mask pair into session if it is an ordinary ip/mask pair.
sub store_ip($$) {
    my $_ip = shift;
    my $_mask = shift;
    my ($ret, $ip, $mask);

    ($ret, $ip, $mask) = check_ip($par->{$_ip}, $par->{$_mask});
    if (! $ret) {
	return 0;
    }

    $session->{$_ip} = $ip;
    $session->{$_mask} = $mask;
    return 1;
}

# picks the primary ip address and returns it in cidr and bits notation
sub getPrimaryIP($) {
    my $subnets = shift;
    my @ips = split(/,/, $subnets);
    my $primary = $ips[0];
    return '' if ($primary eq '');
    my ($ip, $cidr) = ipv4_parse($primary);
    my $mask = ipv4_cidr2msk($cidr);
    return ($primary, $ip, $mask, $cidr);
}

sub getAdditionalIPs($) {
    my $subnets = shift;
    my @ips = split(/,/, $subnets);
    shift(@ips);
    return join(",", @ips);
}

sub checkIPs($$) {
    my $ip = shift;
    my $maxcidr = shift;
    my @ips = split(/[\r\n,]/, $ip);
    my @ok = ();
    my @nok = ();

    foreach my $net (@ips) {
	next if ($net =~ /^\s*$/);
	my $ok = 0;
	my $checknet = $net;
	$checknet .= '/32' if ($checknet !~ /\//);
	eval {
	    my ($ip, $cidr) = ipv4_parse($checknet);
	    if ($cidr > 0 and $cidr < $maxcidr) {
		push(@ok, "$ip/$cidr");
		$ok = 1;
	    }
	};
	if (! $ok) {
	    push(@nok, $net);
	}
    }
    return (join(",", @ok), join(",", @nok));
}


sub createIPS($$) {
    my $primary = shift;
    my $additional = shift;
    return checkIPs($primary.",".$additional, 32);
}

sub checkNetaddress($) {
    my $subnets = shift;

    my @ret = ();
    foreach my $net (split(/,/, $subnets)) {
	my ($netaddr,) = ipv4_network($net);
	my ($ip,) = ipv4_parse($net);

	if ($netaddr eq $ip) {
	    push(@ret, $net);
	}
    }
    return \@ret;
}

sub checkBroadcast($) {
    my $subnets = shift;

    my @ret = ();
    foreach my $net (split(/,/, $subnets)) {
	my ($bcast,) = ipv4_broadcast($net);
	my ($ip,) = ipv4_parse($net);

	if ($bcast eq $ip) {
	    push(@ret, $net);
	}
    }
    return \@ret;
}

sub checkInvalidMask($) {
    my $subnets = shift;

    my @ret = ();
    foreach my $net (split(/,/, $subnets)) {
	my ($ip,$mask) = ipv4_parse($net);

	if ($mask eq '255.255.255.255') {
	    push(@ret, $net);
	}
    }
    return \@ret;
}

sub loadNetmasks($) {
    my $selected = shift;
    my @arr = ();

    if ($selected eq '') {
	$selected = '24';
    }

    for (my $i=0; $i<=32; $i++) {
	my $bits = ipv4_cidr2msk($i);
	my $caption = "/$i - $bits";
	my %hash = (
		    'MASK_LOOP_INDEX'    => $i,
		    'MASK_LOOP_VALUE'    => $i,
		    'MASK_LOOP_CAPTION'  => $caption,
		    'MASK_LOOP_SELECTED' => ($selected eq $i ? 'selected':'')
		    );
	push(@arr, \%hash);
    }
    return \@arr;
}

sub is_modem {
    if ($session->{'CONFIG_TYPE'} =~ /^[0145]$/) {
	return 1;
    }
    return 0;
}

sub orange_used () {
    if ($session->{'CONFIG_TYPE'} =~ /^[1357]$/) {
	return 1;
    }
    return 0;
}

sub blue_used () {
    if ($session->{'CONFIG_TYPE'} =~ /^[4567]$/) {
	return 1;
    }
    return 0;
}

sub replace_primary_ip($$) {
    my $ips = shift;
    my $primary = shift;

    $ips =~ s/^[^,]+,/$primary,/;
    if ($ips =~ /^$/) {
	$ips = $primary;
    }
    return $ips;
}


1;

