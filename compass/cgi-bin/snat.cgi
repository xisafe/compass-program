#!/usr/bin/perl

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

require '/var/efw/header.pl';
require 'ethconfig.pl';
require 'simple_conflict_detection.pl';

my $configfile = "${swroot}/snat/config";
my $ethernet_settings = "${swroot}/ethernet/settings";
my $setsnat = "/usr/local/bin/setsnat";
my $openvpn_passwd   = '/usr/bin/openvpn-sudo-user';
my $confdir = '/etc/firewall/snat/';
my $needreload = "${swroot}/snat/needreload";

my $ALLOW_PNG = '/images/firewall_accept.png';
my $DENY_PNG = '/images/firewall_drop.png';
my $UP_PNG = '/images/stock_up-16.png';
my $DOWN_PNG = '/images/stock_down-16.png';
my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $EDIT_PNG = '/images/edit.png';
my $DELETE_PNG = '/images/delete.png';
my $OPTIONAL_PNG = '/images/blob.png';

my (%par,%checked,%selected,%ether);
my @errormessages = ();
my $errormessage;
my $log_accepts = 'off';
my @nets;
my $reload = 0;

my $devices, $deviceshash = 0;

my $services_file = '/var/efw/snat/services';
my $services_custom_file = '/var/efw/snat/services.custom';

&readhash($ethernet_settings, \%ether);

sub have_net($) {
    my $net = shift;

    # AAAAAAARGH! dumb fools
    my %net_config = (
        'GREEN' => [1,1,1,1,1,1,1,1,1,1],
        'ORANGE' => [0,1,0,3,0,5,0,7,0,0],
        'BLUE' => [0,0,0,0,4,5,6,7,0,0]
    );

    if ($net_config{$net}[$ether{'CONFIG_TYPE'}] > 0) {
        return 1;
    }
    return 0;
}

sub configure_nets() {
    my @totest = ('GREEN', 'BLUE', 'ORANGE');

    foreach (@totest) {
        my $thisnet = $_;
        if (! have_net($thisnet)) {
            next;
        }
        if ($ether{$thisnet.'_DEV'}) {
            push (@nets, $thisnet);
        }
    }

}

sub get_openvpn_lease() {
    my @users = sort split(/\n/, `$openvpn_passwd list`);
    return \@users;
}

sub read_config_file($) {
    my $filename = shift;
    my @lines;
    open (FILE, "$filename");
    foreach my $line (<FILE>) {
    chomp($line);
    $line =~ s/[\r\n]//g;
    if (!is_valid($line)) {
        next;
    }
    push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub read_config_line($) {
    my $line = shift;
    my @lines = read_config_file($configfile);
    return $lines[$line];
}

sub save_config_file_back($) {
    my $ref = shift;
    my @lines = @$ref;
    open (FILE, ">$configfile");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
	
	`sudo fmodify $configfile`;
    $reload = 1;
}

sub line_count() {
    open (FILE, "$configfile") || return 0;
    my $i = 0;
    foreach (<FILE>) {
        $i++;
    }
    close FILE;
    return $i;
}

sub append_config_file($) {
    my $line = shift;
    open (FILE, ">>$configfile");
    print FILE $line."\n";
    close FILE;	
	`sudo fmodify $configfile`;
    $reload = 1;
}

sub is_valid($) {
    my $line = shift;
    # temporary hack;
    # if ($line =~ /(?:(?:[^,]*),){10}/ || $line =~ /(?:(?:[^,]*),){7}/) {
    #     return 1;
    # }
    return 1;
}

sub config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    if (! is_valid($line)) {
        return;
    }
    my @temp = split(/,/, $line);
    $config{'enabled'} = $temp[0];
    $config{'proto'} = $temp[1];
    $config{'src_ip'} = $temp[2];
    $config{'dst_ip'} = $temp[3];
    $config{'dst_port'} = $temp[4];
    $config{'dst_dev'} = $temp[5];
    $config{'target'} = $temp[6];
    $config{'remark'} = $temp[7];
    $config{'log'} = $temp[8];
    $config{'snat_to'} = $temp[9];
    $config{'valid'} = 1;

    return %config;
}

sub toggle_enable($$) {
    my $line = shift;
    my $enable = shift;
    if ($enable) {
        $enable = 'on';
    } 
    else {
        $enable = 'off';
    }

    my %data = config_line(read_config_line($line));
    $data{'enabled'} = $enable;

    return save_line($line,
                    $data{'enabled'},
                    $data{'proto'},
                    $data{'src_ip'},
                    $data{'dst_ip'},
                    $data{'dst_port'},
                    $data{'dst_dev'},
                    $data{'target'},
                    $data{'remark'},
                    $data{'log'},
                    $data{'snat_to'});
}

sub move($$) {
    my $line = shift;
    my $direction = shift;
    my $newline = $line + $direction;
    if ($newline < 0) {
        return;
    }
    my @lines = read_config_file($configfile);

    if ($newline >= scalar(@lines)) {
        return;
    }

    my $temp = $lines[$line];
    $lines[$line] = $lines[$newline];
    $lines[$newline] = $temp;
    save_config_file_back(\@lines);
}

sub set_position($$) {
    my $old = shift;
    my $new = shift;
    my @lines = read_config_file($configfile);
    my $myline = $lines[$old];
    my @newlines = ();

    # nothing to do
    if ($new == $old) {
        return;
    }
   
    if ($new > $#lines+1) {
        $new = $#lines+1;
    }

    open (FILE, ">$configfile");

    for ($i=0;$i<=$#lines+1; $i++) {
        if (($i == $new) && (($i==0) || ($i == $#lines) || ($old > $new))) {
            print FILE "$myline\n";
            if (!("$lines[$i]" eq "")) {
                print FILE "$lines[$i]\n";
            }
        }
        elsif (($i == $new)) {
            if (!("$lines[$i]" eq "")) {
                print FILE "$lines[$i]\n";
            }
            print FILE "$myline\n";                
        }
        else {
            if ($i != $old) {
                if (!("$lines[$i]" eq "")) {
                    print FILE "$lines[$i]\n";
                }
            }
        }
    }
    $reload = 1;
    `sudo fmodify $configfile`;
    close(FILE);
}

sub delete_line($) {
    my $line = shift;
    my @lines = read_config_file($configfile);
    if (! @lines[$line]) {
        return;
    }
    delete (@lines[$line]);
    save_config_file_back(\@lines);
}

sub create_line($$$$$$$$$$) {

    my $enabled = shift;
    my $proto = shift;
    my $src_ip = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $dst_dev = shift;
    my $target = shift;
    my $remark = shift;
    my $log = shift;
    my $snat_to = shift;

    return "$enabled,$proto,$src_ip,$dst_ip,$dst_port,$dst_dev,$target,$remark,$log,$snat_to";
}

sub check_values($$$$$$$$$$) {
    my $enabled = shift;
    my $protocol = shift;
    my $src_ip = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $dst_dev = shift;
    my $target = shift;
    my $remark = shift;
    my $log = shift;
    my $snat_to = shift;
    
    my %valid_proto = ('TCP' => 1, 'UDP' => 1, 'TCP&UDP' => 1, 'OSPF' => 1, 'ESP' => 1, 'GRE' => 1, 'ICMP' => 1);
    
    if ($protocol !~ /^$/) {
        if (! $valid_proto{uc($protocol)}) {
            push(@errormessages, _('非法的协议'));
        }
    }
    
    if ($dst_ip eq "" && $dst_dev eq "") {
        push(@errormessages, 'SNAT目的必须定义');
    }
    
    foreach my $item (split(/&/, $src_ip)) {
        next if ($item =~ /^$/);
        next if ($item =~ /^OPENVPNUSER:/);
        if (! is_ipaddress($item)) {
            push(@errormessages, '非法的源IP   '.$item);
        }
    }

    foreach my $item (split(/&/, $dst_ip)) {
        next if ($item =~ /^OPENVPNUSER:/);
        next if ($item =~ /^$/);
        if (!is_ipaddress($item)) {
            push(@errormessages,'非法的目的IP   ' .$item);
        }
    }

    foreach my $ports (split(/&/, $dst_port)) {
        if ($ports !~ /^(\d{1,5})(?:\:(\d{1,5}))?$/) {
            push(@errormessages, '非法的目的端口  '.$ports);
        }
        my $port1 = $1;
        my $port2 = '65535';
        if ($2) {
            $port2 = $2;
        }

        if (($port1 < 0) || ($port1 > 65535)) {
            push(@errormessages, '非法的目的端口'.$port1);
        }
        if(($port2 < 0) || ($port2 > 65535)) {
            push(@errormessages, '非法的目的端口'.$port2);
        }
        if ($port1 > $port2) {
            push(@errormessages, '目的端口范围第一个值应该小于第二个');
        }
    }

    foreach my $item (split(/&/, $snat_to)) {
        next if ($item =~ /^UPLINK:/);
        next if ($item =~ /^VPN:/);
        next if ($item =~ /^GREEN|ORANGE|BLUE/);
        next if ($item =~ /^$/);
        if (!is_ipaddress($item)) {
            push(@errormessages, '非法的源IP'.$item);
        }
    }

    if ($target eq 'NETMAP') {
	if (($snat_to =~ /^$/) || !validipandmask($snat_to)) {
	    push(@errormessages, $snat_to."不是一个子网");
	} else {
	    my ($eat,$target_bits) = ipv4_parse($snat_to);
	    if ($src_ip eq '') {
		push(@errormessages, "源必须是一个子网");
	    }
	    foreach my $item (split(/&|\-/, $src_ip)) {
		next if ($item =~ /^$/);
		if (!validipandmask($item)) {
		    push(@errormessages, "源".$item."不是一个子网");
		    next;
		}
		my ($eat,$item_bits) = ipv4_parse($item);
		if ($target_bits ne $item_bits) {
		    push(@errormessages, "网络映射中源".$item."和映射子网".$snat_to."不匹配");
		    next;
		}
	    }
	}
    }

    if ($#errormessages eq -1) {
        return 1
    }
    else {
        return 0;
    } 
}

sub save_line($$$$$$$$$$$) {
    my $line = shift;
    my $enabled = shift;
    my $proto = shift;
    my $src_ip = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $dst_dev = shift;
    my $target = shift;
    my $remark = shift;
    my $log = shift;
    my $snat_to = shift;
        
    $src_ip =~ s/\n/&/gm;
    $src_ip =~ s/\r//gm;
    $dst_ip =~ s/\n/&/gm;
    $dst_ip =~ s/\r//gm;
    $dst_port =~ s/\n/&/gm;
    $dst_port =~ s/\r//gm;
    $dst_port =~ s/\-/:/g;
    $remark =~ s/\,//g;
    $dst_dev =~ s/\|/&/g;
    $src_ip =~ s/\|/&/g;
    $dst_ip =~ s/\|/&/g;
    $dst_ip = delete_same_data($dst_ip);
    $src_ip = delete_same_data($src_ip);
    if ($src_ip =~ /OPENVPNUSER:ALL/) {
        $src_ip = 'OPENVPNUSER:ALL';
    }
    if ($dst_ip =~ /OPENVPNUSER:ALL/) {
        $dst_ip = 'OPENVPNUSER:ALL';
    }
    if ($src_ip =~ /none/) {
        $src_ip = '';
    }
    if ($dst_ip =~ /none/) {
        $dst_ip = '';
    }

    if ($dst_dev =~ /ALL/) {
        $dst_dev = 'ALL';
    }
    if ($dst_dev =~ /none/) {
        $dst_dev = '';
    }

    if ($dst_ip !~ /^$/) {
        $dst_dev = '';
    }
    if ($dst_port =~ /any/) {
       $dst_port = '';
    }
    if ($proto =~ /any/) {
        $proto = '';
    }

    if ($proto eq 'icmp') {
        $dst_port = '8&30';
    }

    if (! check_values($enabled, $proto, $src_ip, $dst_ip, $dst_port, $dst_dev, $target, $remark, $log, $snat_to)) {
        return 0;
    }
    
    my $tosave = create_line($enabled, $proto, $src_ip, $dst_ip, $dst_port, $dst_dev, $target, $remark, $log, $snat_to);
    
    if ($line !~ /^\d+$/) {
        append_config_file($tosave);
        return 1;
    }
    my @lines = read_config_file($configfile);
    if (! $lines[$line]) {
        push(@errormessages, _('Configuration line not found!'));
        return 0;
    }

    my %split = config_line($lines[$line]);
    if (($split{'enabled'} ne $enabled) ||
            ($split{'proto'} ne $proto) ||
            ($split{'src_ip'} ne $src_ip) ||
            ($split{'dst_ip'} ne $dst_ip) ||
            ($split{'dst_port'} ne $dst_port) ||
            ($split{'dst_dev'} ne $dst_dev) ||
            ($split{'target'} ne $target) ||
            ($split{'remark'} ne $remark) ||
            ($split{'log'} ne $log) ||
            ($split{'snat_to'} ne $snat_to)) {
        $lines[$line] = $tosave;
        save_config_file_back(\@lines);
    }
    return 1;
}

sub format_line($$$$$$$$$$$) {
    my $line = shift;
    my $enabled = shift;
    my $proto = shift;
    my $src_ip = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $dst_dev = shift;
    my $target = shift;
    my $remark = shift;
    my $log = shift;
    my $snat_to = shift;
        
    $src_ip =~ s/\n/&/gm;
    $src_ip =~ s/\r//gm;
    $dst_ip =~ s/\n/&/gm;
    $dst_ip =~ s/\r//gm;
    $dst_port =~ s/\n/&/gm;
    $dst_port =~ s/\r//gm;
    $dst_port =~ s/\-/:/g;
    $remark =~ s/\,//g;
    $dst_dev =~ s/\|/&/g;
    $src_ip =~ s/\|/&/g;
    $dst_ip =~ s/\|/&/g;
    $dst_ip = delete_same_data($dst_ip);
    $src_ip = delete_same_data($src_ip);
    if ($src_ip =~ /OPENVPNUSER:ALL/) {
        $src_ip = 'OPENVPNUSER:ALL';
    }
    if ($dst_ip =~ /OPENVPNUSER:ALL/) {
        $dst_ip = 'OPENVPNUSER:ALL';
    }
    if ($src_ip =~ /none/) {
        $src_ip = '';
    }
    if ($dst_ip =~ /none/) {
        $dst_ip = '';
    }

    if ($dst_dev =~ /ALL/) {
        $dst_dev = 'ALL';
    }
    if ($dst_dev =~ /none/) {
        $dst_dev = '';
    }

    if ($dst_ip !~ /^$/) {
        $dst_dev = '';
    }
    if ($dst_port =~ /any/) {
       $dst_port = '';
    }
    if ($proto =~ /any/) {
        $proto = '';
    }

    if ($proto eq 'icmp') {
        $dst_port = '8&30';
    }

    if (! check_values($enabled, $proto, $src_ip, $dst_ip, $dst_port, $dst_dev, $target, $remark, $log, $snat_to)) {
        return 0;
    }
    
    my $tosave = create_line($enabled, $proto, $src_ip, $dst_ip, $dst_port, $dst_dev, $target, $remark, $log, $snat_to);
    return $tosave;
}
sub generate_addressing($$$$) {
    my $addr = shift;
    my $dev = shift;
    my $mac = shift;
    my $rulenr = shift;
    my @addr_values = ();

    foreach my $item (split(/&/, $addr)) {
        if ($item =~ /^OPENVPNUSER:(.*)$/) {
            my $user = $1;
            push(@addr_values, _("%s (OpenVPN User)", $user));
        }
        else {
            push(@addr_values, $item);
        }
    }
    foreach my $item (split(/&/, $dev)) {
        if ($item =~ /^PHYSDEV:(.*)$/) {
            my $device = $1;
            my $data = $deviceshash->{$device};

          push(@addr_values, "<font color='". $zonecolors{$data->{'zone'}} ."'>".$data->{'portlabel'}."</font>");
        }
        elsif ($item =~ /^VPN:(.*)$/) {
            my $dev = $1;
            push(@addr_values, "<font color='". $colourvpn ."'>".$dev."</font>");
        }
        elsif ($item =~ /^UPLINK:(.*)$/) {
            my $ul = get_uplink_label($1);
            push(@addr_values, "<font color='". $zonecolors{'RED'} ."'>"._('Uplink')." ".$ul->{'description'}."</font>");
        }
        else {
            push(@addr_values, "<font color='". $zonecolors{$item} ."'>".$strings_zone{$item}."</font>");
        }
    }

    if ($#addr_values == -1) {
        return 'ANY';
    }

    if ($#addr_values == 0) {
        return $addr_values[0];
    }

    my $long = '';
    foreach my $addr_value (@addr_values) {
        $long .= sprintf <<EOF
<div>$addr_value</div>
EOF
;
    }
    return $long;
}

sub generate_service($$$) {
    my $ports = shift;
    my $protocol = shift;
    my $rulenr = shift;
    $protocol = lc($protocol);
    my $display_protocol = $protocol;
    my @service_values = ();

    if ($protocol eq 'tcp&udp') {
        $display_protocol = 'TCP+UDP';
    }
    else {
        $display_protocol = uc($protocol);
    }

    if (($display_protocol ne '') && ($ports eq '')) {
        return "$display_protocol/"._('ANY');
    }

    foreach my $port (split(/&/, $ports)) {
        my $service = uc(getservbyport($port, $protocol));
        # FIXME: this should use the services file
        #if ($service =~ /^$/) {
        #    push(@service_values, "$display_protocol/$port");
        #    next;
        #}
        #push(@service_values, "$service");
        push(@service_values, "$display_protocol/$port");
    }
    if ($#service_values == -1) {
        return 'ANY';
    }

    if ($#service_values == 0) {
        return $service_values[0];
    }

    my $long = '';
    foreach my $value (@service_values) {
        $long .= sprintf <<EOF
<div>$value</div>
EOF
;
    }
    return $long;
}

sub getConfigFiles($) {
    my $dir = shift;
    my @arr = ();
    foreach my $f (glob("${dir}/*.conf")) {
    push(@arr, $f);
    }
    return \@arr;
}

sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;

    display_add($is_editing, $line);

    generate_rules($configfile, $is_editing, $line, 1);
	
	my $sys_length = count_sys_rules(getConfigFiles($confdir), 0, 0, 0);

	if($sys_length>0)
{
    printf <<EOF

<div class="show_sys" ><b>%s</b>&nbsp;&nbsp;<b><input onclick="swapVisibility('systemrules')" value=" &gt;&gt; " type="button"></b></div>
EOF
, _('Show system rules')
;


    print "<div id=\"systemrules\" style=\"display: none\">\n";
    #&openbox('100%', 'left', _('Rules automatically configured by the system'));
    generate_rules(getConfigFiles($confdir), 0, 0, 0);
    #&closebox();
    print "</div>";
}
    
}


sub count_sys_rules($$$$) {
    my $refconf = shift;
    my $is_editing = shift;
    my $line = shift;
    my $editable = shift;
	my $length=0;
    my @configs = ();
    if (ref($refconf) eq 'ARRAY') {
        @configs = @$refconf;
    }
    else {
        push(@configs, $refconf);
    }

		foreach my $configfile (@configs) 
		{
			my @lines = read_config_file($configfile);

			foreach my $thisline (@lines) {
			
				chomp($thisline);
				my %splitted = config_line($thisline);

				if (! $splitted{'valid'}) {
					next;
				}
			$length++;
		}
	
	}
	return $length;
}



sub generate_rules($$$$) {
    my $refconf = shift;
    my $is_editing = shift;
    my $line = shift;
    my $editable = shift;

    my @configs = ();
    if (ref($refconf) eq 'ARRAY') {
        @configs = @$refconf;
    }
    else {
        push(@configs, $refconf);
    }

    printf <<END
    <table class="ruleslist" cellpadding="0" cellspacing="0" width="100%">
        <tr class="first_tr">
            <td class="boldbase" width="2%">#</td>
            <td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="12%">%s</td>
            <td class="boldbase" width="12%">%s</td>
            <td class="boldbase" width="22%">%s</td>
            <td class="boldbase" style="width: 150px;">%s</td>
        </tr>
END
    , _('Source')
    , _('Destination')
    , _('Service')
    , _('NAT to')
    , _('Remark')
    , _('Actions')
    ;

    my $i = 0;

    foreach my $configfile (@configs) {
        my @lines = read_config_file($configfile);
		my $length = @lines;
		if($length >0)
		{
        foreach my $thisline (@lines) {
			
            chomp($thisline);
            my %splitted = config_line($thisline);

            if (! $splitted{'valid'}) {
                next;
            }
            my $protocol = uc($splitted{'proto'});
            my $source = $splitted{'src_ip'};
            my $num = $i+1;
        
            my $enabled_gif = $DISABLED_PNG;
            my $enabled_alt = _('Disabled (click to enable)');
            my $enabled_action = 'enable';
            if ($splitted{'enabled'} eq 'on') {
                $enabled_gif = $ENABLED_PNG;
                $enabled_alt = _('Enabled (click to disable)');
                $enabled_action = 'disable';
            }
            my $destination = $splitted{'dst_ip'};
            my $dst_dev = $splitted{'dst_dev'};
            my $snat_to = $splitted{'snat_to'};
            if ($splitted{'target'} eq 'RETURN') {
                $snat_to = _('No NAT');
            } elsif ($splitted{'target'} eq 'NETMAP') {
		$snat_to = _('Map Network to %s', $snat_to);
	    } else {
                if (!is_ipaddress($splitted{'snat_to'})) {
                    $snat_to = generate_addressing('', $splitted{'snat_to'}, '', $i);
                }
                if ($snat_to eq 'ANY') {
                    $snat_to = _('Auto');
                }
            }
        
            my $port = $splitted{'dst_port'};
            my $remark = value_or_nbsp($splitted{'remark'});
            my $bgcolor = setbgcolor($is_editing, $line, $i);

            my $dest_long_value = generate_addressing($destination, $dst_dev, '', $i);
            if ($dest_long_value =~ /(?:^|&)ANY/) {
                $dest_long_value = "&lt;"._('ANY')."&gt;";
            }
            my $src_long_value = generate_addressing($source, '', '', $i);
            if ($src_long_value =~ /(?:^|&)ANY/) {
                $src_long_value = "&lt;"._('ANY')."&gt;";
            }
            my $service_long_value = generate_service($port, $protocol, $i);
            if ($service_long_value =~ /(?:^|&)ANY/) {
                $service_long_value = "&lt;"._('ANY')."&gt;";
            }

	    my $style = ();
            if ($i eq 0) {
                $style{'up'} = "hidden";
                $style{'clear_up'} = "";
            }
            else {
                $style{'up'} = "";
                $style{'clear_up'} = "hidden";
            }
            if ($i + 1 eq scalar(@lines)) {
                $style{'down'} = "hidden";
                $style{'clear_down'} = "";
            }
            else {
                $style{'down'} = "";
                $style{'clear_down'} = "hidden";
            }
        
            printf <<EOF
            <tr class="$bgcolor">
                <td v align="center">$num</td>
                <td v>$src_long_value</td>
                <td v>$dest_long_value</td>
                <td v>$service_long_value</td>
                <td v>$snat_to</td>
                <td v title="$remark">$remark</td>
                <td class="actions" v nowrap="nowrap">
EOF
            ;
            if ($editable) {
		printf <<EOF
                    <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-top:5px;margin-left:42px;display:inline-block;vertical-align:top">
                        <input class='imagebutton $style{'up'}' type='image' name="submit" SRC="$UP_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="up">
                        <input TYPE="hidden" name="line" value="$i">
			<img class="clear $style{'clear_up'}" src="$CLEAR_PNG"/>
                    </form>
EOF
                    , _("Up")
                    ;
                printf <<EOF
EOF
                ;
		printf <<EOF
                    <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="display:inline-block;vertical-align:top;margin-top:5px;">
                        <input class='imagebutton $style{'down'}' type='image' name="submit" SRC="$DOWN_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="down">
                        <input TYPE="hidden" name="line" value="$i">
			<img class="clear $style{'clear_down'}" src="$CLEAR_PNG"/>
                    </form>
EOF
                    , _("Down")
                    ;
                printf <<EOF
                    <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="display:inline-block;vertical-align:top;margin-top:5px;">
                        <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" ALT="$enabled_alt" />
                        <input TYPE="hidden" name="ACTION" value="$enabled_action">
                        <input TYPE="hidden" name="line" value="$i">
                    </FORM>
                    <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="display:inline-block;vertical-align:top;margin-top:5px;">
                        <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="edit">
                        <input TYPE="hidden" name="line" value="$i">
                    </FORM>
                    <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="display:inline-block;vertical-align:top;margin-top:5px;" onsubmit="return confirm('确认删除？')">
                        <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="delete">
                        <input TYPE="hidden" name="line" value="$i">
                    </FORM>
                </td>
            </tr>
EOF
            , _('Edit')
            , _('Delete');
        }
        $i++;
    }
}else{
	no_tr(7,_('Current no content'));
}
}
    
    printf <<EOF
    </table>
EOF
;
if($length >0)
{
printf <<EOF
    <table class="list-legend" cellpadding="0" cellspacing="0">
        <tr>
            <td CLASS="boldbase">%s:<IMG SRC="$ENABLED_PNG" ALT="%s" />%s<IMG SRC='$DISABLED_PNG' ALT="%s" />%s<IMG SRC="$EDIT_PNG" alt="%s" />%s<IMG SRC="$DELETE_PNG" ALT="%s" />%s</td>
        </tr>
    </table>
EOF
, _('Legend')
, _('Enabled (click to disable)')
, _('Enabled (click to disable)')
, _('Disabled (click to enable)')
, _('Disabled (click to enable)')
, _('Edit')
, _('Edit')
, _('Remove')
, _('Remove')
;
	}
}

sub create_servicelist($$) {
    my $selected_protocol = lc(shift);
    my $selected_ports = shift;
    chomp($selected_protocol);
    chomp($selected_ports);
    
    my $selected = '';
    my @ret = ();
    if ($selected_protocol || $selected_ports) {
        $selected_cus = 'selected';
    }
    my $userdef = sprintf <<EOF
<option value="" $selected_cus>%s</option>
EOF
    , _('User defined')
    ;
    push(@ret, $userdef);

    my @services = ();
    open(SERVICE_FILE, $services_file) || return ($selected, \@ret);
    @services = <SERVICE_FILE>;
    close(SERVICE_FILE);

    if (open(SERVICE_FILE, $services_custom_file)) {
        foreach my $line (<SERVICE_FILE>) {
            push(@services, $line);
        }
        close(SERVICE_FILE);
    }

    foreach my $line (sort(@services)) {
        my ($desc, $ports, $proto) = split(/,/, $line);
        chomp($desc);
        chomp($ports);
        chomp($proto);
        my $choosen='';
        $proto = lc($proto);
        if (($proto eq $selected_protocol) && ($ports eq $selected_ports)) {
            $choosen='selected';
            $selected="$ports/$proto";
        }
        push (@ret, "<option value='$ports/$proto' $choosen>$desc</option>");
    }

    return ($selected, \@ret);
}

sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;
    my %config;
    my %checked;
    my %selected;
        
    if (($is_editing) && ($par{'sure'} ne 'y')) {
        %config = config_line(read_config_line($line));
    }
    else {
        %config = %par;
    }

    if (! $is_editing) {
	# put default values here
	$config{'enabled'} = 'on';
    }

    my $enabled = $config{'enabled'};
    my $protocol = $config{'proto'};
    if (! $protocol && !$is_editing) {
        $protocol = 'any';
    }
    my $dst_dev = $config{'dst_dev'};
    my $source = $config{'src_ip'};
    my $source_ip = '';
    my $source_user = '';
    my $destination = $config{'dst_ip'};
    my $destination_ip = '';
    my $destination_user = '';
    my $destination_dev = '';
    my $port = $config{'dst_port'};
    my $remark = $config{'remark'};
    my $snat_to = $config{'snat_to'};
    my $snat_to_ip = '';
    my $snat_to_map = '';
    my $target = $config{'target'};
    if ($target =~ /^$/) {
    $target = 'SNAT';
    }

    my $src_type = 'ip';
    my $dst_type = 'dev';

    $checked{'ENABLED'}{$enabled} = 'checked';
    $selected{'PROTOCOL'}{$protocol} = 'selected';
    
    if ($source !~ /^$/) {
        if ($source =~ /OPENVPNUSER:/) {
            $source_user = $source;
            foreach $item (split(/&/, $source_user)) {
                $selected{'src_user'}{$item} = 'selected';
            }
            $src_type = 'user';
        }
        else {
            $source_ip = $source;
            if ($source_ip !~ /^$/) {
                $src_type = 'ip';
            }
        }
    }

    if ($destination =~ /^$/) {
        foreach my $item (split(/&/, $dst_dev)) {
            $selected{'dst_dev'}{$item} = 'selected';
        }
        if ($dst_dev !~ /^$/) {
            $dst_type = 'dev';
        }
    }

    if ($destination !~ /^$/) {
        if ($destination =~ /OPENVPNUSER:/) {
            $destination_user = $destination;
            foreach $item (split(/&/, $destination_user)) {
                $selected{'dst_user'}{$item} = 'selected';
            }
            $dst_type = 'user';
        }
        else {
            $destination_ip = $destination;
            if ($destination_ip !~ /^$/) {
                $dst_type = 'ip';
            }
        }
    }

    if ($target eq 'NETMAP') {
	$snat_to_map = $snat_to;
    } else {
	$snat_to_ip = $snat_to;
    }
    $selected{'src_type'}{$src_type} = 'selected';
    $selected{'dst_type'}{$dst_type} = 'selected';
    
    $selected{'target'}{$target} = 'selected';
    $selected{'snat_to'}{$snat_to} = 'selected';

    my %foil = ();
    $foil{'title'}{'src_user'} = 'none';
    $foil{'title'}{'src_ip'} = 'none';
    $foil{'value'}{'src_user'} = 'none';
    $foil{'value'}{'src_ip'} = 'none';

    $foil{'title'}{'dst_user'} = 'none';
    $foil{'title'}{'dst_ip'} = 'none';
    $foil{'title'}{'dst_dev'} = 'none';
    $foil{'value'}{'dst_user'} = 'none';
    $foil{'value'}{'dst_ip'} = 'none';
    $foil{'value'}{'dst_dev'} = 'none';

    $foil{'title'}{"src_$src_type"} = 'block';
    $foil{'value'}{"src_$src_type"} = 'block';
    $foil{'title'}{"dst_$dst_type"} = 'block';
    $foil{'value'}{"dst_$dst_type"} = 'block';
    
    $foil{'value'}{'to_RETURN'} = 'none';
    $foil{'value'}{'to_SNAT'} = 'none';
    $foil{'value'}{'to_NETMAP'} = 'none';
    $foil{'value'}{"to_$target"} = 'block';

    $source_ip =~ s/&/\n/gm;
    $destination_ip =~ s/&/\n/gm;
    $port =~ s/&/\n/gm;

    my $line_count = line_count();

    if ("$par{'line'}" eq "") {
        # if no line set last line
        #print "BIO";
        #$line = $line_count -1;
    }

    my $openvpn_ref = get_openvpn_lease();
    my @openvpnusers = @$openvpn_ref;

    my $src_user_size = int($#openvpnusers / 5);
    if ($src_user_size < 5) {
       $src_user_size = 5;
    }
    my $dst_user_size = $src_user_size;
    my $action = 'add';
    my $sure = '';
    $button = _("Create Rule");
    my $title = _('Source NAT rule editor');
    my $named = "添加SNAT规则";
    if ($is_editing) {
        $action = 'edit';
        my $sure = '<input TYPE="hidden" name="sure" value="y">';
        $button = _("编辑规则");
        $show = "showeditor";
        $named = "编辑SNAT规则";
    }
    else {
        $show = "";
    }
	 if ($#errormessages ne -1) { $show = "showeditor";}
    openeditorbox($named, $title, $show, "createrule",);
    #&openbox('100%', 'left', $title);
    printf <<EOF
       
                <!-- begin source -->
					</form>
					<form name="SNAT_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr class="env">
                            <td class="add-div-type" rowspan="1" style="width:15%"><b>%s</b></td>
                            <td style="width:30%">
                                %s *&nbsp;&nbsp;<select name="src_type" onchange="toggleTypes('src');" onkeyup="toggleTypes('src');" style="width:225px">
                                    <option value="ip" $selected{'src_type'}{'ip'}>%s</option>
                                    <option value="user" $selected{'src_type'}{'user'}>%s</option>
                                </select>
                            </td>
                            <td colspan="2">
                                <div id="src_ip_t" style="display:$foil{'title'}{'src_ip'}">%s</div>
                                <div id="src_user_t" style="display:$foil{'title'}{'src_user'}" style="width: 250px; height: 90px;">%s</div>
EOF
, _('Source')
, _('Type')
, _('Network/IP')
, _('OpenVPN User')
, _('Insert network/IPs (one per line)')
, _('Select OpenVPN users (hold CTRL for multiselect)')
;

##########
# SOURCE #
##########

#### User begin #############################################################
    printf <<EOF
                            <div id='src_user_v' style='display:$foil{'value'}{'src_user'}'>
                                <select name="src_user" multiple style="width: 250px; height: 90px;">
                                    <option value="OPENVPNUSER:ALL" $selected{'src_user'}{"OPENVPNUSER:ALL"}>&lt;%s&gt;</option>
EOF
    , _('ANY')
    ;
    foreach my $item (@openvpnusers) {
        printf <<EOF
                                    <option value="OPENVPNUSER:$item" $selected{'src_user'}{"OPENVPNUSER:$item"}>$item</option>
EOF
    ;
    }
    printf <<EOF
                                </select>
                            </div>
EOF
;
#### User end ###############################################################

#### IP begin ###############################################################
    printf <<EOF
                            <div id='src_ip_v' style='display:$foil{'value'}{'src_ip'}'>
                                <textarea name='source' wrap='off' style="width: 250px; height: 90px;">$source_ip</textarea>
                            </div>
EOF
    ;
#### IP end #################################################################

    printf <<EOF
                        </td>
                    </tr>

                <!-- end source field -->
          
                <!-- begin destination -->

                    <tr class="odd">
                        <td class="add-div-type" rowspan="1" ><b>%s</b></td>
                        <td>%s *&nbsp;&nbsp;<select name="dst_type" onchange="toggleTypes('dst');" onkeyup="toggleTypes('dst');" style="width: 225px">
                                <option value="dev" $selected{'dst_type'}{'dev'}>%s</option>
                                <option value="ip" $selected{'dst_type'}{'ip'}>%s</option>
                                <option value="user" $selected{'dst_type'}{'user'}>%s</option>
                            </select>
                        </td>
                        <td colspan="2">
                            <div id="dst_dev_t" style="display:$foil{'title'}{'dst_dev'}">%s</div>
                            <div id="dst_ip_t" style="display:$foil{'title'}{'dst_ip'}">%s</div>
                            <div id="dst_user_t" style="display:$foil{'title'}{'dst_user'}" style="width: 254px; height: 90px;">%s</div>
EOF
    , _('Destination')
    , _('Type')
    , _('Zone/VPN/Uplink')
    , _('Network/IP')
    , _('OpenVPN User')
    , _('Select interfaces (hold CTRL for multiselect)')
    , _('Insert network/IPs (one per line)')
    , _('Select OpenVPN users (hold CTRL for multiselect)')
;

###############
# DESTINATION #
###############

#### Device begin ###########################################################
    printf <<EOF
                            <div id='dst_dev_v' style='display:$foil{'value'}{'dst_dev'}'>
                                <select name="dst_dev" multiple style="width: 256px; height: 90px;">
EOF
;
    foreach my $item (@nets) {
        printf <<EOF
                                    <option value="$item" $selected{'dst_dev'}{$item}>%s</option>
EOF
,$strings_zone{$item}
;
    }
=pod 2013.12.12 去掉此接口
    foreach my $data (@$devices) {
        my $value = $data->{'portlabel'};
	my $key = "PHYSDEV:".$data->{'device'};
	my $zone = _("Zone: %s", $strings_zone{$data->{'zone'}});
	printf <<EOF
	    <option value="$key" $selected{'dst_dev'}{$key}>$value ($zone)</option>
EOF
;
    }
=cut
    printf <<EOF
                                    <option value="VPN:IPSEC" $selected{'dst_dev'}{'VPN:IPSEC'}>IPSEC</option>
EOF
    ;
    foreach my $tap (@{get_taps()}) {
        my $key = "VPN:".$tap->{'name'};
	my $name = $tap->{'name'};
	next if ($tap->{'bridged'});
        printf <<EOF 
                                    <option value='$key' $selected{'dst_dev'}{$key}>%s $name</option>
EOF
, _('VPN')
;
    }

    printf <<EOF 
                                    <option value='UPLINK:ANY' $selected{'dst_dev'}{'UPLINK:ANY'}>&lt;%s&gt;</option>
EOF
, _('ANY Uplink')
;

    foreach my $ref (@{get_uplinks_list()}) {
	my $name = $ref->{'name'};
	my $key = $ref->{'dev'};
	my $desc = $ref->{'description'};
        printf <<EOF 
                                    <option value='$key' $selected{'dst_dev'}{$key}>%s $desc [%s]</option>
EOF
, _('Uplink')
, _('RED')
;
    }
    printf <<EOF
                                </select>
                            </div>
EOF
    ;
#### Device end #############################################################

#### IP begin ###############################################################
    printf <<EOF
                            <div id='dst_ip_v' style='display:$foil{'title'}{'dst_ip'}'>
                                <textarea name='destination' wrap='off' style="width: 250px; height: 90px;">$destination_ip</textarea>
                            </div>
EOF
    ;
#### IP end #################################################################

#### User begin #############################################################
    printf <<EOF
                            <div id='dst_user_v' style='display:$foil{'title'}{'dst_user'}'>
                                <select name="dst_user" multiple style="width: 250px; height: 90px;">
                                    <option value="OPENVPNUSER:ALL" $selected{'dst_user'}{'OPENVPNUSER:ALL'}>&lt;%s&gt;</option>
EOF
    , _('ANY')
    ;
    foreach my $item (@openvpnusers) {
        printf <<EOF
                                    <option value="OPENVPNUSER:$item" $selected{'dst_user'}{"OPENVPNUSER:$item"}>$item</option>
EOF
        ;
    }
    printf <<EOF
                                </select>
                            </div>
EOF
    ;
#### User end ###############################################################

    printf <<EOF
                        </td>
                    </tr>

                <!-- end destination -->
           

        <tr class="env">
            <td class="add-div-type" rowspan="1"><b>%s</b></td>
            <td v nowrap="true">%s *
                <select name="service_port" onchange="selectService('protocol', 'service_port', 'port');" onkeyup="selectService('protocol', 'service_port', 'port');" style="width:229px">
                    <option value="any/any">&lt;%s&gt;</option>
EOF
    , _('Service/Port')
    , _('Service')
    , _('ANY')
    ;
    my ($sel, $arr) = create_servicelist($protocol, $config{'dst_port'});
    print @$arr;
# check if ports should be enabled
    if ($protocol eq "") {
        $portsdisabled = 'disabled="true"';
    }
    printf <<EOF
                </select>
            </td>
            <td v style="width:25%">%s *
                <select name="protocol" onchange="updateService('protocol', 'service_port', 'port');" onkeyup="updateService('protocol', 'service_port', 'port');" style="width:216px">
                    <option value="any" $selected{'PROTOCOL'}{'any'}>&lt;%s&gt;</option>
                    <option value="tcp" $selected{'PROTOCOL'}{'tcp'}>TCP</option>
                    <option value="udp" $selected{'PROTOCOL'}{'udp'}>UDP</option>
                    <option value="tcp&udp" $selected{'PROTOCOL'}{'tcp&udp'}>TCP + UDP</option>
                    <option value="ospf" $selected{'PROTOCOL'}{'ospf'}>OSPF</option>
                    <option value="esp" $selected{'PROTOCOL'}{'esp'}>ESP</option>
                    <option value="gre" $selected{'PROTOCOL'}{'gre'}>GRE</option>
                    <option value="icmp" $selected{'PROTOCOL'}{'icmp'}>ICMP</option>
                </select>
            </td>
            <td v>
EOF
    , _('Protocol')
    , _('ANY')
;
my $isdisplay = "class='hidden_class'";
if($port ne "")
{
	$isdisplay = "";
}
printf <<EOF
				<ul  id="port_ul" $isdisplay><li>%s</li>
                <li><textarea name="port" rows="3" $portsdisabled onkeyup="updateService('protocol', 'service_port', 'port');">$port</textarea></li>
				</ul>
EOF
, _('Destination port (one per line)')
;

printf <<EOF
				<ul id="port_ul2" $note_display><li>%s</li></ul>
EOF
,_('This rule will match all the destination ports')
;

printf <<EOF
            </td>
        </tr>

        <tr class="odd">
            <td class="add-div-type"><b>%s</b></td>
            <td>
                <select name="to_type" onchange="toggleTypes('to');" onkeyup="toggleTypes('to');" style="width:269px">
                    <option value="SNAT" $selected{'target'}{'SNAT'}>%s</option>
                    <option value="RETURN" $selected{'target'}{'RETURN'}>%s</option>
                    <option value="NETMAP" $selected{'target'}{'NETMAP'}>%s</option>
                </select>
            </td>
            <td colspan="2">
                <div id='to_RETURN_t'></div>
                <div id='to_RETURN_v' style='display:$foil{'value'}{'to_RETURN'}'>&nbsp;</div>
                <div id='to_NETMAP_t'></div>
                <div id='to_NETMAP_v' style='display:$foil{'value'}{'to_NETMAP'}'>%s 
                  <input name='snat_to_map' value="$snat_to_map" size="10" type="text" style="width: 150px;" />
                </div>
                <div id='to_SNAT_t'></div>
                <div id='to_SNAT_v' style='display:$foil{'value'}{'to_SNAT'}'>%s 
                    <select name="snat_to_ip" style="width: 200px;">
                          <option value='' $selected{'snat_to'}{''}>%s</option>
EOF
    , _('NAT 策略')
    , 'NAT'
    , _('Do not NAT')
    , _('网络映射')

    , _('to Subnet')
    , _('to source address')
    , _('Auto')
    ;

    foreach my $ref (@{get_uplinks_list()}) {
	my $name = $ref->{'name'};
	my $key = $ref->{'dev'};
	my $desc = $ref->{'description'};
        printf <<EOF
                          <option value='$key' $selected{'snat_to'}{$key}>%s $desc - %s:%s</option>
EOF
        , _('Uplink')
        , _('IP')
        , _('Auto')
        ;
        eval {
            my %ulhash;
            &readhash("${swroot}/uplinks/$name/settings", \%ul);
            foreach my $ipcidr (split(/,/, $ul{'RED_IPS'})) {
                my ($ip) = split(/\//, $ipcidr);
                next if ($ip =~ /^$/);
                printf <<EOF
                          <option value='$ip' $selected{'snat_to'}{$ip}>%s $desc - %s:$ip</option>
EOF
                , _('Uplink')
                , _('IP')
                , _('Auto')
                ;
            }
        }
    }

    foreach my $tap (@{get_taps()}) {
        my $key = "VPN:".$tap->{'name'};
        my $name = $tap->{'name'};
	next if ($tap->{'bridged'});
        printf <<EOF
                                    <option value='$key' $selected{'snat_to'}{$key}>%s $name - %s:%s</option>
EOF
        , _('VPN')
        , _('IP')
        , _('Auto')
        ;
    }

    foreach my $name (@nets) {
        printf <<EOF
                                    <option value="$name" $selected{'snat_to'}{$name}>%s %s - %s:%s</option>
EOF
        , _('Zone')
        , $strings_zone{$name}
        , _('IP')
        , _('Auto')
        ;
        
        foreach my $ipcidr (split(/,/, $ether{$name.'_IPS'})) {
            my ($ip) = split(/\//, $ipcidr);
            next if ($ip =~ /^$/);

            printf <<EOF
                                    <option value="$ip" $selected{'snat_to'}{$ip}>%s %s - %s:$ip</option>
EOF
            , _('Zone')
            , $strings_zone{$name}
            , _('IP')
            ;
        }
    }

    printf <<EOF
                    </select>
                </div>
            </td>
        </tr>
        <tr class="env">
			<td class="add-div-type" rowspan ="3">%s</td>
            <td colspan="3"><input name="enabled" value="on" $checked{'ENABLED'}{'on'} type="checkbox">%s</td>
		</tr>
		<tr class="env">
            <td colspan="3">%s
                <input name="remark" value="$remark" size="50" maxlength="50" type="text" style="width:235px"/>
            </td>
		</tr>
		<tr class="env">
            <td colspan="3" >%s *&nbsp;
                <select name="position" style="width:225px">
                    <option value="0">%s</option>
EOF
    , _('Other')
    , _('Enabled')
    , _('Remark')
    , _('Position')
    , _('First')
    ;

    my $i = 1;
    while ($i <= $line_count) {
        my $title = _('After rule #%s', $i);
        my $selected = '';
        if ($i == $line_count) {
            $title = _('Last');
        }
        if ($line == $i || ($line eq "" && $i == $line_count)) {
            $selected = 'selected';
        }
        printf <<EOF
                    <option value="$i" $selected>$title</option>
EOF
        ;
        $i++;
    }

    printf <<EOF
                </select>
            </td>
        </tr>
    </table>
    <input type="hidden" name="ACTION" value="$action">
    <input type="hidden" name="line" value="$line">
    <input type="hidden" name="sure" value="y">
EOF
;

    &closeeditorbox($button, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
}

sub reset_values() {
    %par = ();
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    if ($action eq 'apply') {
        system($setsnat);		
		`sudo fcmd $setsnat`;
        $notemessage = _("NAT rules applied successfully");
        return;
    }
    if ($action eq 'save') {
        reset_values();
        return;
    }
    if ($action eq 'up') {
        move($par{'line'}, -1);
        reset_values();
        return;
    }
    if ($action eq 'down') {
        move($par{'line'}, 1);
        reset_values();
        return;
    }
    if ($action eq 'delete') {
        delete_line($par{'line'});
        reset_values();
        return;
    }

    if ($action eq 'enable') {
        #----------------------------------
        #冲突提示代码添加-2013-04-18-squall
        
        #这里的$par{'line'}从0开始计数
        my %data = config_line(read_config_line($par{'line'}));
        $data{'seq'} = $par{'line'}+1;
        my @conflict_list = conflict_detection(\%data,$action,"$ENV{'SCRIPT_NAME'}");
        
        #如果存在冲突
        if (@conflict_list) {
            print generate_conflict_warning_msg(\@conflict_list,$data{'seq'});
        }
        #end
        #----------------------------------
        if (toggle_enable($par{'line'}, 1)) {
            reset_values();
            return;
        }
    }
    if ($action eq 'disable') {
        if (toggle_enable($par{'line'}, 0)) {
            reset_values();
            return;
        }
    }
        # ELSE
    if (($action eq 'add') ||
            (($action eq 'edit')&&($sure eq 'y'))) {
        my $src_type = $par{'src_type'};
        my $dst_type = $par{'dst_type'};
        my $source = '';
        my $destination = '';
        my $src_dev = '';
        my $old_pos = $par{'line'};

        if ($src_type eq 'ip') {
            $source = $par{'source'};
        }
        if ($dst_type eq 'ip') {
            $destination = $par{'destination'};
        }
        if ($src_type eq 'user') {
            $source = $par{'src_user'};
        }
        if ($dst_type eq 'user') {
            $destination = $par{'dst_user'};
        }
        if ($dst_type eq 'dev') {
            $dst_dev = $par{'dst_dev'};
        }
        my $snat_to = '';
        if ($par{'to_type'} eq 'RETURN') {
            $snat_to = '';
        } elsif ($par{'to_type'} eq 'NETMAP') {
            $snat_to = $par{'snat_to_map'};
        } else {
            $snat_to = $par{'snat_to_ip'};
        }
        my $enabled = $par{'enabled'};
        #----------------------------------
        #冲突提示代码添加-2013-04-18-squall
        
        #获取格式化的line string
		my $current_line = format_line($par{'line'},
                                      $enabled,
                                      $par{'protocol'},
                                      $source,
                                      $destination,
                                      $par{'port'},
                                      $dst_dev,
                                      $par{'to_type'},
                                      $par{'remark'},
                                      '',
                                      $snat_to);
        # print $current_line;
        #这里的$par{'line'}从0开始计数
        my %data = config_line($current_line);
        my $tmp_action = $action;
        $data{'seq'} = $par{'position'}+1;
        if ($action eq 'edit') {
            my $old_seq = $old_pos;
            $old_seq = $old_pos+1;
            $tmp_action = $action."_$old_seq";
        }
        my @conflict_list = conflict_detection(\%data,$tmp_action,"$ENV{'SCRIPT_NAME'}");
        
        #如果存在冲突
        if (@conflict_list) {
            print generate_conflict_warning_msg(\@conflict_list,$data{'seq'});
        }
        #end
        #----------------------------------
        if ($current_line ne 0 && save_line($par{'line'},
                      $enabled,
                      $par{'protocol'},
                      $source,
                      $destination,
                      $par{'port'},
                      $dst_dev,
                      $par{'to_type'},
                      $par{'remark'},
                      '',
                      $snat_to)) {

            if ($par{'line'} ne $par{'position'}) {
                if ("$old_pos" eq "") {
                    $old_pos = line_count()-1;
                }
                if (line_count() > 1) {
                    set_position($old_pos, $par{'position'});
                }
            }
            reset_values();
        }
	else {
	    $par{'sure'} = 'n';
	}
    }
}

#表单检查代码添加-2012-08-30-zhouyuan
sub check_form(){
printf <<EOF
<script language="JavaScript" src="/include/ChinArk_form.js"></script>
<script>
var object = {
       'form_name':'SNAT_FORM',
       'option'   :{
                    'snat_to_map':{
                               'type':'text',
                               'required':'1',
                               'check':'ip_mask'
                             },
                    'remark':{
                               'type':'text',
                               'required':'0',
                               'check':'note|'
                             },
                    'src_type':{
                               'type':'select-one',
                               'required':'1'
                             },
                    'src_user':{
                               'type':'select-multiple',
                               'required':'0'
                             },
                    'dst_type':{
                               'type':'select-one',
                               'required':'1'
                             },
                    'dst_dev':{
                               'type':'select-multiple',
                               'required':'1'
                             },
                    'dst_user':{
                               'type':'select-multiple',
                               'required':'1'
                             },
                    'position':{
                               'type':'select-one',
                               'required':'1'
                             },
                    'source':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|ip_mask|'
                             },
                    'destination':{
                               'type':'textarea',
                               'required':'1',
                               'check':'ip|ip_mask|'
                             },
                    'port':{
                               'type':'textarea',
                               'required':'0',
                               'check':'port|port_range|'
                             }
                 }
};

var check = new  ChinArk_forms();
check._main(object);
</script>
EOF
;
}
#表单检查代码添加-2012-08-30-zhouyuan

&getcgihash(\%par);

&showhttpheaders();
my $extraheader = '<script language="JavaScript" src="/include/firewall_type.js"></script>
<script language="JavaScript" src="/include/services_selector.js"></script>
<script type="text/javascript" src="/include/conflict_detection.js"></script>';
&openpage(_('Source NAT configuration'), 1, $extraheader);

init_ethconfig();
configure_nets();
($devices, $deviceshash) = list_devices_description(3, 'GREEN|ORANGE|BLUE', 0);
save();

if ($reload) {
    system("touch $needreload");
}

foreach my $line(@errormessages)
{
	$errormessage.=$line."<br />";
}
&openbigbox($errormessage, $warnmessage, $notemessage);

if (-e $needreload) {
    applybox(_("Source NAT rules have been changed and need to be applied in order to make the changes active"));
}

my $is_editing = ($par{'ACTION'} eq 'edit');
display_rules($is_editing, $par{'line'});
&check_form();
&closebigbox();
&closepage();
