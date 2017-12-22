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

my $mactabfile = '/var/efw/ethernet/mactab';
my $bondfiles = '/var/efw/ethernet/bond*';
my $ifacesjson = '/var/cache/ethconfig/interfaces.json';

my %ethconfighash=();
my $ethconfig=\%ethconfighash;
my @sortedethconfig = ();

use JSON::XS;

sub init_ethconfig() {
#    load_ethconfig();
}

sub getifbynum($) {
    my $search = shift;
    my $devs = listdevices(0);
    return @$devs[$search];
}

sub getifbydevice($) {
    my $search = shift;
    return $ethconfig->{$search};
}

sub ifnum2device($) {
    my $ifnumbers = shift;
    my $ret = "";
    foreach my $item (split(/\|/, $ifnumbers)) {
	next if ($item =~ /^$/);
	my $devinfo = getifbynum($item);
	next if (!$devinfo);
	$ret.=$devinfo->{'device'}.'|';
    }
    return $ret;
}

sub get_system_vlans() {
    my %rethash = ();
    my $ret = \%rethash;
    my $vlanfile = '/proc/net/vlan/config';

    foreach my $line (`sudo cat $vlanfile`) {
	next if ($line !~ /^eth|bond/);
	my ($dev, $vid, $phys) = split(/\ *\|\ */, $line);
	chomp($dev);
	chomp($vid);
	chomp($phys);

	if (! $ret->{$phys}) {
	    my %subhash = ();
	    $ret->{$phys} = \%subhash;
	}
	$ret->{$phys}->{$vid} = $dev;
    }

    return $ret;
}

sub create_vlan_data($$) {
    my $vid = shift;
    my $iface = shift;

    my %vlanrhash = ();
    my $vlanr = \%vlanrhash;
    $vlanr->{'vid'} = $vid;
    $vlanr->{'device'} = "$iface.$vid";
    $vlanr->{'physdev'} = "$iface";
    $vlanr->{'priority'} = "";
    return $vlanr;
}

sub get_vlan_ids($) {
    my $device = shift;
    my %rethash = ();
    my $ret = \%rethash;

    return 0 if (! -e "/var/efw/ethernet/vlan_${device}");
    open(F, "/var/efw/ethernet/vlan_${device}") || return 0;
    foreach my $line (<F>) {
	chomp($line);
	next if ($line =~ /^\ *$/);
	my $vid = $line;
	my $data = create_vlan_data($vid, $device);
	$ret->{$data->{'device'}} = $data;
    }
    close(F);
    return 0 if (scalar(%rethash) == 0);
    return $ret;
}

sub get_bonds() {
    my %bonds = ();
    my $ret = \%bonds;
    foreach my $bondfile (`ls -1 $bondfiles 2>/dev/null`) {
	chomp($bondfile);
	next if ($bondfile !~ /(bond\d+)$/);
	my $bond = $1;
	$ret->{$bond} = get_zone_devices($bond);
    }
    return $ret;
}

sub bond_of_if($$) {
    my $bonds = shift;
    my $iff = shift;

    foreach my $bond (keys %$bonds) {
	my $iffarr = $bonds->{$bond};
	foreach my $bondiff (@$iffarr) {
	    return $bond if ($bondiff eq $iff);
	}
    }
    return "";
}

sub explode_vlans($$) {
    my $eths = shift;
    my $item = shift;
    my @arr = @$eths;
    if ($item->{'vlans'} == 0) {
	return \@arr;
    }

    my $vlans = $item->{'vlans'};
    foreach my $vdevice (sort keys(%$vlans)) {
	my %newitemhash = ();
	my $newitem = \%newitemhash;
	my $vdata = $vlans->{$vdevice};
	$newitem->{'mac'} = $item->{'mac'};
	$newitem->{'description'} = _('VLAN %s on %s', $vdata->{'vid'}, $item->{'description.orig'});
	$newitem->{'shortdesc'} = _('VLAN %s on %s', $vdata->{'vid'}, $item->{'shortdesc.orig'});
	$newitem->{'portlabel'} = _('VLAN %s on %s', $vdata->{'vid'}, $item->{'portlabel'});
	$newitem->{'device'} = $vdevice;
	$newitem->{'physdev'} = $item->{'device'};
	$newitem->{'vid'} = $vdata->{'vid'};
	$newitem->{'businfo'} = $item->{'businfo'};
	if ($item->{'port'} > 0) {
	    $newitem->{'port'} = $item->{'port'}.'.'.$vdata->{'vid'};
	}
	$newitem->{'bondname'} = $item->{'bondname'};
	$newitem->{'zone'} = getzonebyinterface($newitem->{'device'});
	$newitem->{'parent'} = $item;
	push(@arr, $newitem);
    }
    return \@arr;
}

sub getPortByDevice($) {
    my $iffref = shift;
    my @ret = ();
    foreach my $iff (@$iffref) {
	push(@ret, $ethconfig->{$iff}->{'port'});
    }
    return @ret;
}

sub load_ethconfig($) {
    my $checklink = shift;
    my $mac="";
    my $desc="";
    my $businfo="";
    my $label="";
    my $device="";
    my $bonds = get_bonds();
    my %businfosorted_hash = ();
    my $businfosorted = \%businfosorted_hash;
    my $i = 0;

    if (! -e $ifacesjson) {
	system("sudo /usr/sbin/ethconfig --json --output $ifacesjson");
    }
    open(J, $ifacesjson);
    my $jsonobj = JSON::XS->new->utf8->decode (join('', <J>));
    close J;

    foreach my $item (@$jsonobj) {
		$mac = $item->{'mac'};
		$desc = $item->{'name'};
		$label = $item->{'label'};
		$businfo = $item->{'businfo'};
		$device = $item->{'iface'};
		$driver = $item->{'driver'};
		my %recordhash = ();
		my $record = \%recordhash;
		$device =~/eth(\d+)/;
		$record->{'port'} = $1;
		$record->{'mac'} = $mac;
		$record->{'description'} = $desc;
		($record->{'shortdesc'}) = split(/ /, $desc);
		$record->{'description.orig'} = $record->{'description'};
		$record->{'shortdesc.orig'} = $record->{'shortdesc'};
		$record->{'portlabel'} = _('Interface %s', $record->{'port'});

		$record->{'label'} = $label;
		$record->{'device'} = $device;
		$record->{'businfo'} = $businfo;

		$record->{'bond'} = bond_of_if($bonds, $device);
		if ($record->{'bond'}) {
			$record->{'description'} .= ' '. _('bonded in %s', $record->{'bond'});
			$record->{'shortdesc'} .= ' '. _('bonded in %s', $record->{'bond'});
			$record->{'portlabel'} = $record->{'shortdesc'};
		}

		$record->{'vlans'} = 0;
		$record->{'vid'} = 0;
		my $vlans = get_vlan_ids($device);
		if ($vlans) {
			$record->{'vlans'} = $vlans;
			$record->{'description'} .= ' '. _("with VLANs");
			$record->{'shortdesc'} .= ' '. _("with VLANs");
		}

		$record->{'enabled'} = 1;
		if ($record->{'bond'} ne "") {
			$record->{'enabled'} = 0;
		}
		$ethconfig->{$device} = $record;
		if ($businfo =~ /^\s*n\/a\s*$/) {
			$businfosorted->{$businfo.$device} = $device;
		} else {
			$businfosorted->{$record->{'port'}} = $device;
		}

		$record->{'zone'} = getzonebyinterface($device);
    }

    @bondsmac = `ifconfig | grep bond`;#===查找bond口的mac字符串，2014.12.05 WangLin修改====#

    foreach my $bond (keys %$bonds) {
		my %recordhash = ();
		my $record = \%recordhash;
		my $bondedports = join("，", getPortByDevice($bonds->{$bond}));
		$device = $bond;
		$record->{'description'} = _('Bond with ports %s', $bondedports);
		$record->{'description.orig'} = $record->{'description'};
		$record->{'shortdesc'} = _('Bond');
		$record->{'shortdesc.orig'} = $bond;
		$record->{'portlabel'} = _('Bond %s', $device);
		$record->{'label'} = "";
		$record->{'device'} = $device;
		$record->{'bondname'} = $device;
		$record->{'bonddevices'} = $bonds->{$device};
		$record->{'vlans'} = 0;
		$record->{'vid'} = 0;

		my $vlans = get_vlan_ids($device);
		if ($vlans) {
			$record->{'vlans'} = $vlans;
		}
		$record->{'enabled'} = 1;
        # $record->{'port'} = 0; #2014.12.05 WangLin注释
		$record->{'port'} = $bondedports;
		$ethconfig->{$device} = $record;
		$businfosorted->{'00'.$device} = $device;
		$record->{'zone'} = getzonebyinterface($device);

        #===查找mac，2014.12.05 WangLin修改====#
        foreach my $mac_line ( @bondsmac ) {
            if ( $mac_line =~ m/$device     Link encap:Ethernet  HWaddr ([0-9a-zA-Z]{2}(?:\:[0-9a-zA-Z]{2}){5})/ ) {
                $record->{'mac'} = $1;
                last;
            }
        }
    }

    my @mactable = ();
    my @description = ();
    my $i = 0;

    my @sorted = ();

    if (-e "/var/efw/ethernet/fixed_nics") {
		# sorted by device name, but they has been presorted by businfotab
		@sorted = sort(keys(%$ethconfig));
		my $j = 0;
		foreach my $item (@sorted) {
			if ($ethconfig->{$item}->{'device'} !~ /bond/) {
				my $device = $ethconfig->{$item}->{'device'};
				$device =~/eth(\d+)/;
				$ethconfig->{$item}->{'port'} = $1+1;
			}
		}
    } 
	else {
		# sort by businfo
		my @orderby = ();
		if (-e "/var/efw/ethernet/reverse_nics") {
			@orderby = sort{$b cmp $a} (keys(%$businfosorted));
		} 
		else {
			@orderby = sort{$a <=> $b} (keys(%$businfosorted));
		}
		my $j = 0;
		foreach my $businfo (@orderby) {
			my $item = $businfosorted->{$businfo};
			if ($item->{'device'} !~ /bond/) {
				$j++;
				$item->{'port'} = $j;
			}
			push(@sorted, $item);
		}
    }
    @sortedethconfig=();
    foreach my $item (@sorted) {
		push(@sortedethconfig, $ethconfig->{$item});
		my $retarr = explode_vlans(\@sortedethconfig, $ethconfig->{$item});
		@sortedethconfig = @$retarr;
    }
    add_numerator(\@sortedethconfig);
    format_description(\@sortedethconfig, $checklink);
    return \@sortedethconfig;
}



sub listdevices($) {
    my $showlink = shift;
    if ($#sortedethconfig <= 0) {
		load_ethconfig($showlink)
    }
    return \@sortedethconfig;
}

sub add_numerator($) {
    my $eths = shift;
    my $i = 0;
    foreach my $item (@$eths) {
	$item->{'index'} = $i;
	$i++;
    }
}

my %linkStatusCache = {};
sub refreshLinkStatus() {
    for my $line (`sudo /usr/sbin/ifplugstatus 2>/dev/null`) {
	my ($iff, $status) = split(/:/, $line);
	if ($line =~ /link beat detected$/) {
	    $linkStatusCache{$iff} = "LINK OK";
	    next;
	}
	if ($line =~ /unplugged$/) {
	    $linkStatusCache{$iff} = "NO LINK";
	    next;
	}
	$linkStatusCache{$iff} = "LINK STATUS N/A";
    }
}

sub check_link($) {
    my $iface = shift;
    if ($linkStatusCache{$iface} =~ /^$/) {
	refreshLinkStatus();
    }
    my $status = $linkStatusCache{$iface};
    if ($status =~ /^$/) {
	return "LINK STATUS N/A";
    }
    return $status;
}

sub format_description($$) {
    my $eths = shift;
    my $checklink = shift;
    refreshLinkStatus();
    foreach my $item (@$eths) {
	my $device = $item->{'device'};

	# *** link check ***
	my $link = '';
	my $linkcaption = _('Link status n/a');
	my $linkicon = 'linkna';
	if ($checklink) {
        # 开启bond口的功能，2014.12.05 WangLin注释
	    # if ($item->{'device'} !~ /bond/) {
		if ($item->{'vid'} != 0) {
		    $link = $item->{'parent'}->{'link'};
		} else {
		    $link = check_link($device);
		}
		if ($link eq 'LINK OK') {
		    $linkcaption = _('Link OK');
		    $linkicon = 'linkok';
		}
		if ($link eq 'NO LINK') {
		    $linkcaption = _('NO Link');
		    $linkicon = 'linknotok';
		}
	    # }
	}

	# *** DESCRIPTION ***
	my $desc = $item->{'description'};
	my $shortdesc = $item->{'shortdesc'};
	my $mac = $item->{'mac'};
	if ($mac =~ /^$/) {
	    $mac = _('No MAC');
	}

	# *** INDEX ***
	my $port = $item->{'port'};
	if ( $port eq "" ) {
	    $port = 'n/a';
	}

	$item->{'port'} = $port;
	$item->{'link'} = $link;
	$item->{'linkcaption'} = $linkcaption;
	$item->{'linkicon'} = $linkicon;
	$item->{'caption'} = $port.") $device: $desc - $mac [$linkcaption]";
	$item->{'label'} = $port.") $device: $desc [$linkcaption]";
	$item->{'shortlabel'} = $port.") $device: $shortdesc [$linkcaption]";
    }
}

sub list_devices_description($$$) {
    my $layer = shift;
    my $showzones = shift;
    my $showlink = shift;
    # layer:
    # 1: bond selector  (on top of which can be done ALL of those: bonding, vlan tagging, bridging, ethernet)
    # 2: vlan selector  (on top of which can be done ALL of those: vlan tagging, bridging, ethernet)
    # 3: ip assigning   (on top of which can be done ALL of those: bridging, ethernet)
    # 99: all devices
    #
    # negative means display only that type of devices. (-1 = only bonds, -2 = only vlans, -3 = only assignable)
    #
    # zones:
    # combinations of values: NONE, GREEN, BLUE, ORANGE, RED
    #
    # showlink:
    # decides whether to check if the link of the device is present or not.
    # Note that this value may be cached from earlier load_ethconfig() calls

    my $devlist = listdevices($showlink);
    my @ret = ();
    my %rethash = ();

    foreach my $item (@$devlist) {
	if ($layer > 0) {
	    # *** hide because of level? ***
	    if ($layer < 99) {
		# hide devices which are part of a bond
		next if ($item->{'bond'});
	    }
	    if ($layer <= 3) {
		# hide devices which have vlans on top of them
		# exception: a device can have multiple vlans therefore don't
		#            hide them in layer which will be used for vlan
		#            tagging selection.
		if ($layer != 2) {
		    next if ($item->{'vlans'});
		}
	    }
	    if ($layer <= 2) {
		# hide virtual vlan devices
		next if ($item->{'vid'} != 0);
	    }
	    if ($layer <= 1) {
		# hide bonding devices
		next if ($item->{'bonddevices'});
	    }
	} else {
	    if ($layer == -1) {
		next if (! $item->{'bonddevices'});
	    }
	    if ($layer == -2) {
		next if ($item->{'vid'} == 0);
	    }
	}

	# *** hide because of assigned to zone? ***
	my $device = $item->{'device'};
	my $zone = $item->{'zone'};
	if ($showzones ne -1) {
	    if ($zone =~ /^$/) {
		$zone = 'NONE';
	    }
	    next if ($showzones !~ /$zone/);
	}

	push(@ret, $item);
	$rethash{$device} = $item;
    }
    return (\@ret, \%rethash);
}

1;
