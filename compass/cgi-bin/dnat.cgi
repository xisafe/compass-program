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

my $configfile = "${swroot}/dnat/config";
my $ethernet_settings = "${swroot}/ethernet/settings";
my $setdnat = "/usr/local/bin/setdnat";
my $openvpn_passwd   = '/usr/bin/openvpn-sudo-user';
my $confdir = '/etc/firewall/dnat/';
my $needreload = "${swroot}/dnat/needreload";

my $ALLOW_PNG = '/images/firewall_accept.png';
my $IPS_PNG = '/images/firewall_ips.png';
my $DENY_PNG = '/images/firewall_drop.png';
my $REJECT_PNG = '/images/firewall_reject.png';
my $RETURN_PNG = '/images/return.png';
my $MAP_PNG = '/images/map.png';
my $UP_PNG = '/images/stock_up-16.png';
my $DOWN_PNG = '/images/stock_down-16.png';
my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $ADD_PNG = '/images/add.png';
my $EDIT_PNG = '/images/edit.png';
my $DELETE_PNG = '/images/delete.png';
my $OPTIONAL_PNG = '/images/blob.png';

my (%par,%checked,%selected,%ether);
my @errormessages = ();
my $log_accepts = 'off';
my @nets;
my $reload = 0;

my $devices, $deviceshash = 0;

my $services_file = '/var/efw/dnat/services';
my $services_custom_file = '/var/efw/dnat/services.custom';

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
    $config{'protocol'} = $temp[1];
    $config{'src_dev'} = $temp[2];
    $config{'source'} = $temp[3];
    $config{'dst_dev'} = $temp[4];
    $config{'destination'} = $temp[5];
    $config{'port'} = $temp[6];
    $config{'target_ip'} = $temp[7];
    $config{'target_port'} = $temp[8];
    $config{'nat_target'} = $temp[9];
    $config{'remark'} = $temp[10];
    $config{'log'} = $temp[11];
    $config{'filter_target'} = $temp[12];
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
		     $data{'protocol'},
		     $data{'src_dev'},
		     $data{'source'},
		     $data{'dst_dev'},
		     $data{'destination'},
		     $data{'port'},
		     $data{'target_ip'},
		     $data{'target_port'},
		     $data{'nat_target'},
		     $data{'remark'},
		     $data{'log'},
		     $data{'filter_target'});
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

    close(FILE);
    $reload = 1;
	`sudo fmodify $configfile`;
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

sub create_line($$$$$$$$$$$$$) {

    my $enabled = shift;
    my $proto = shift;
    my $src_dev = shift;
    my $src_ip = shift;
    my $dst_dev = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $target_ip = shift;
    my $target_port = shift;
    my $nat_target = shift;
    my $remark = shift;
    my $log = shift;
    my $filter_target = shift;
    return "$enabled,$proto,$src_dev,$src_ip,$dst_dev,$dst_ip,$dst_port,$target_ip,$target_port,$nat_target,$remark,$log,$filter_target";
}

sub check_values($$$$$$$$$$$$$) {
    my $enabled = shift;
    my $proto = shift;
    my $src_dev = shift;
    my $src_ip = shift;
    my $dst_dev = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $target_ip = shift;
    my $target_port = shift;
    my $nat_target = shift;
    my $remark = shift;
    my $log = shift;
    my $filter_target = shift;
    
    my %valid_proto = ('TCP' => 1, 'UDP' => 1, 'TCP&UDP' => 1, 'ESP' => 1, 'GRE' => 1, 'ICMP' => 1);
    
    if ($protocol !~ /^$/) {
        if (! $valid_proto{uc($protocol)}) {
            push(@errormessages, _('Invalid protocol'));
			return ;
        }
    }
    
    if ($dst_ip eq "" && $dst_dev eq "") {
        push(@errormessages, _('Incoming IP must be defined'));
			return ;
    }
    
    foreach my $src (split(/\|/, $src_ip)) {
        foreach my $item (split(/&|\-/, $src)) {
            next if ($item =~ /^$/);
            next if ($item =~ /^OPENVPNUSER:/);
            next if ($item =~ /^any$/);
            if (! is_ipaddress($item)) {
                push(@errormessages, _('Invalid source IP address "%s"', $item));
			return ;
            }
        }
    }

    foreach my $item (split(/&|\-/, $dst_ip)) {
        next if ($item =~ /^OPENVPNUSER:/);
        next if ($item =~ /^$/);
        if (!is_ipaddress($item)) {
            push(@errormessages, _('Invalid destination IP address "%s"', $item));
			return ;
        }
    }

    foreach my $ports (split(/&|\-/, $dst_port)) {
        if ($ports !~ /^(\d{1,5})(?:\:(\d{1,5}))?$/) {
            push(@errormessages, _('Invalid incoming port "%s"', $ports));
			return ;
        }
        my $port1 = $1;
        my $port2 = '65535';
        if ($2) {
            $port2 = $2;
        }

        if (($port1 < 0) || ($port1 > 65535)) {
            push(@errormessages, _('Invalid incoming port "%s"', $port1));
			return ;
        }
        if(($port2 < 0) || ($port2 > 65535)) {
            push(@errormessages, _('Invalid incoming port "%s"', $port2));
			return ;
        }
        if ($port1 > $port2) {
            push(@errormessages, _('The incoming port range has a first value that is greater than or equal to the second value.'));
			return ;
        }
    }

    foreach my $item (split(/&|\-/, $target_ip)) {
        next if ($item =~ /^OPENVPNUSER:/);
        next if ($item =~ /^$/);
        if (!is_ipaddress($item)) {
            push(@errormessages, _('Invalid target IP address "%s"', $item));
			return ;
        }
    }

    if ($target eq 'NETMAP') {
	if (!validipandmask($target_ip)) {
	    push(@errormessages, _('Translation target "%s" is no subnet. Net mapping requires a subnet.', $target_ip));
			return ;
	}
	my ($eat,$target_bits) = ipv4_parse($target_ip);

	if ($dst_ip eq '') {
	    push(@errormessages, _('Target must be a subnet!'));
			return ;
	}
	foreach my $item (split(/&|\-/, $dst_ip)) {
	    next if ($item =~ /^$/);
	    if (!validipandmask($item)) {
		push(@errormessages, _('Target "%s" is no subnet. Net mapping requires a subnet.', $item));
			return ;
		next;
	    }
	    my ($eat,$item_bits) = ipv4_parse($item);
	    if ($target_bits ne $item_bits) {
		push(@errormessages, _('Net mapping requires destination (%s) and translation subnet (%s) of equal size.', $item, $target_ip));
			return ;
		next;
	    }
	}
    }

    foreach my $ports (split(/&|\-/, $target_port)) {
        if ($ports !~ /^(\d{1,5})(?:\:(\d{1,5}))?$/) {
            push(@errormessages, _('Invalid target port "%s"', $ports));
			return ;
        }
        my $port1 = $1;
        my $port2 = '65535';
        if ($2) {
            $port2 = $2;
        }

        if (($port1 < 0) || ($port1 > 65535)) {
            push(@errormessages, _('Invalid target port "%s"', $port1));
			return ;
        }
        if(($port2 < 0) || ($port2 > 65535)) {
            push(@errormessages, _('Invalid target port "%s"', $port2));
			return ;
        }
        if ($port1 > $port2) {
            push(@errormessages, _('The target port range has a first value that is greater than or equal to the second value.'));
			return ;
        }
    }

    if ($#errormessages eq -1) {
        return 1
    }
    else {
        return 0;
    } 
}
sub nat_type($){
       my $type = shift;
       my %selected=();
       $selected{'filter_policy'}{$type} = 'selected';
       printf <<EOF
                            &nbsp;&nbsp;
                            <div style='display:inline-block;' class="filter_policy $policy">
                                %s
                                <!-- begin policy -->
                                <select id="filter_policy" name="filter_policy" $disabled style="width:184px">
									
                                    <option value="RETURN" $selected{'filter_policy'}{'ACCEPT'}>%s</option>
                                    <option value="DROP" $selected{'filter_policy'}{'DROP'}>%s</option>
                                    <option value="REJECT" $selected{'filter_policy'}{'REJECT'}>%s</option>
                                </select>
                                <!-- end policy -->
                            </div>
                   
EOF
        , _('Filter policy')
        , _('ALLOW')
        , _('DROP')
        , _('REJECT')
        ;
#2013-7-26 能士项目屏蔽入侵防御
#<option value="ALLOW" $selected{'filter_policy'}{'ALLOW'}>%s</option>
#, _('入侵防御')
##2014-5-6 打开入侵防御
}
sub save_line($$$$$$$$$$$$$$) {

    my $line = shift;
    my $enabled = shift;
    my $proto = shift;
    my $src_dev = shift;
    my $src_ip = shift;
    my $dst_dev = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $target_ip = shift;
    my $target_port = shift;
    my $nat_target = shift;
    my $remark = shift;
    my $log = shift;
    my $filter_target = shift;
    if($par{'target_type'} eq 'ip'){
        $filter_target =~s /(.*)\|.*\|.*/$1/;
    }
    if($par{'target_type'} eq 'user'){
        $filter_target =~s /.*\|(.*)\|.*/$1/;
    }
    if($par{'target_type'} eq 'lb'){
        $filter_target =~s /.*\|.*\|(.*)/$1/;
    }

    $src_dev =~s/\|/&/g;
    $src_dev = delete_same_data($src_dev);
    $src_dev =~s/&/\|/g;
    $src_ip =~s/\|/&/g;
    $src_ip = delete_same_data($src_ip);
    $src_ip =~s/&/\|/g;
    # $src_ip =~ s/\n/&/gm;
    # $src_ip =~ s/\r//gm;
    $dst_ip =~ s/\n/&/gm;
    $dst_ip =~ s/\r//gm;    
    $dst_ip = delete_same_data($dst_ip);
    $target_ip =~ s/\n/&/gm;
    $target_ip =~ s/\r//gm;
    $dst_port =~ s/\n/&/gm;
    $dst_port =~ s/\r//gm;
    $target_port =~ s/\-/:/g;
    $target_port =~ s/\n/&/gm;
    $target_port =~ s/\r//gm;
    $remark =~ s/\,//g;
    $dst_dev =~ s/\|/&/g;
    #$src_dev =~ s/\|/&/g;
    #$src_ip =~ s/\|/&/g;
    $dst_ip =~ s/\|/&/g;
    $target_ip =~ s/\|/&/g;
    $proto =~ s/\+/&/g;

    # if ($src_ip =~ /OPENVPNUSER:ALL/) {
    #     $src_ip = 'OPENVPNUSER:ALL';
    # }
    if ($target_ip =~ /OPENVPNUSER:ALL/) {
        $target_ip = 'OPENVPNUSER:ALL';
    }
    # if ($src_ip =~ /none/) {
    #     $src_ip = '';
    # }
    if ($dst_ip =~ /none/) {
        $dst_ip = '';
    }

    # if ($src_dev =~ /ALL/) {
    #     $src_dev = 'ALL';
    # }
    if ($src_dev =~ /none/) {
        $src_dev = '';
    }
    if ($dst_dev =~ /none/) {
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

    if ($nat_target eq 'NETMAP') {
	$filter_target = 'RETURN';
    }
    if ($nat_target eq 'RETURN') {
	$filter_target = 'RETURN';
    }

    if (! check_values($enabled, $proto, $src_dev, $src_ip, $dst_dev, 
		       $dst_ip, $dst_port, $target_ip, $target_port, 
		       $nat_target, $remark, $log, $filter_target)) {
        return 0;
    }
    my $tosave = create_line($enabled, $proto, $src_dev, $src_ip, $dst_dev, 
			     $dst_ip, $dst_port, $target_ip, $target_port, 
			     $nat_target, $remark, $log, $filter_target);
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
    if (
	($split{'enabled'} ne $enabled) ||
	($split{'protocol'} ne $proto) ||
	($split{'src_dev'} ne $src_dev) ||
	($split{'source'} ne $src_ip) ||
	($split{'dst_dev'} ne $dst_dev) ||
	($split{'destination'} ne $dst_ip) ||
	($split{'port'} ne $dst_port) ||
	($split{'target_ip'} ne $target_ip) ||
	($split{'target_port'} ne $target_port) ||
	($split{'nat_target'} ne $nat_target) ||
	($split{'filter_target'} ne $filter_target) ||
	($split{'remark'} ne $remark) ||
	($split{'log'} ne $log)
	) {
        $lines[$line] = $tosave;
        save_config_file_back(\@lines);
    }
    return 1;
}

sub format_line($$$$$$$$$$$$$$) {

    my $line = shift;
    my $enabled = shift;
    my $proto = shift;
    my $src_dev = shift;
    my $src_ip = shift;
    my $dst_dev = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $target_ip = shift;
    my $target_port = shift;
    my $nat_target = shift;
    my $remark = shift;
    my $log = shift;
    my $filter_target = shift;
    if($par{'target_type'} eq 'ip'){
        $filter_target =~s /(.*)\|.*\|.*/$1/;
    }
    if($par{'target_type'} eq 'user'){
        $filter_target =~s /.*\|(.*)\|.*/$1/;
    }
    if($par{'target_type'} eq 'lb'){
        $filter_target =~s /.*\|.*\|(.*)/$1/;
    }

    $src_dev =~s/\|/&/g;
    $src_dev = delete_same_data($src_dev);
    $src_dev =~s/&/\|/g;
    $src_ip =~s/\|/&/g;
    $src_ip = delete_same_data($src_ip);
    $src_ip =~s/&/\|/g;
    # $src_ip =~ s/\n/&/gm;
    # $src_ip =~ s/\r//gm;
    $dst_ip =~ s/\n/&/gm;
    $dst_ip =~ s/\r//gm;    
    $dst_ip = delete_same_data($dst_ip);
    $target_ip =~ s/\n/&/gm;
    $target_ip =~ s/\r//gm;
    $dst_port =~ s/\n/&/gm;
    $dst_port =~ s/\r//gm;
    $target_port =~ s/\-/:/g;
    $target_port =~ s/\n/&/gm;
    $target_port =~ s/\r//gm;
    $remark =~ s/\,//g;
    $dst_dev =~ s/\|/&/g;
    #$src_dev =~ s/\|/&/g;
    #$src_ip =~ s/\|/&/g;
    $dst_ip =~ s/\|/&/g;
    $target_ip =~ s/\|/&/g;
    $proto =~ s/\+/&/g;

    # if ($src_ip =~ /OPENVPNUSER:ALL/) {
    #     $src_ip = 'OPENVPNUSER:ALL';
    # }
    if ($target_ip =~ /OPENVPNUSER:ALL/) {
        $target_ip = 'OPENVPNUSER:ALL';
    }
    # if ($src_ip =~ /none/) {
    #     $src_ip = '';
    # }
    if ($dst_ip =~ /none/) {
        $dst_ip = '';
    }

    # if ($src_dev =~ /ALL/) {
    #     $src_dev = 'ALL';
    # }
    if ($src_dev =~ /none/) {
        $src_dev = '';
    }
    if ($dst_dev =~ /none/) {
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

    if ($nat_target eq 'NETMAP') {
	$filter_target = 'RETURN';
    }
    if ($nat_target eq 'RETURN') {
	$filter_target = 'RETURN';
    }

    if (! check_values($enabled, $proto, $src_dev, $src_ip, $dst_dev, 
		       $dst_ip, $dst_port, $target_ip, $target_port, 
		       $nat_target, $remark, $log, $filter_target)) {
        return 0;
    }
    my $tosave = create_line($enabled, $proto, $src_dev, $src_ip, $dst_dev, 
			     $dst_ip, $dst_port, $target_ip, $target_port, 
			     $nat_target, $remark, $log, $filter_target);
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
	my $ip = '';
	my $preip = '';
	my $postip = '';
	if ($item =~ /^(\d[\d\.]*):/) {
	    $ip = $1;
	    $preip = "$ip (";
	    $postip = ")";
	}
        if ($item =~ /^(?:.*:)?PHYSDEV:(.*)$/) {
            my $device = $1;
            my $data = $deviceshash->{$device};

	    push(@addr_values, "$preip<font color='". $zonecolors{$data->{'zone'}} ."'>".$data->{'portlabel'}."</font>$postip");
        }
        elsif ($item =~ /^(?:.*:)?VPN:(.*)$/) {
            my $dev = $1;
            push(@addr_values, "$preip<font color='". $colourvpn ."'>".$dev."</font>$postip");
        }
        elsif ($item =~ /^(?:.*:)?UPLINK:(.*)$/) {
            my $ul = get_uplink_label($1);
            push(@addr_values, "$preip<font color='". $zonecolors{'RED'} ."'>"._('Uplink')." ".$ul->{'description'}."</font>$postip");
        }
        else {
	    my $zone = $item;
	    if ($ip !~ /^$/) {
		($ip,$zone) = split(/:/, $item);
	    }
            push(@addr_values, "$preip<font color='". $zonecolors{$zone} ."'>".$strings_zone{$zone}."</font>$postip");
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

sub display_rules($$$$$$) {
    my $is_editing = shift;
    my $add_external = shift;
    my $edit_external = shift;
    my $source = shift;
    my $src_dev = shift;
    my $line = shift;

    #&openbox('100%', 'left', _('Current rules'));
    display_add($is_editing, $add_external, $edit_external, $source, $src_dev, $line);

    generate_rules($configfile, $is_editing, $add_external, $edit_external, $source, $src_dev, $line, 1);

    
}

sub generate_rules($$$$$$$$) {
    my $refconf = shift;
    my $is_editing = shift;
    my $add_external = shift;
    my $edit_external = shift;
    my $old_source = shift;
    my $old_src_dev = shift;
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
        <tr>
            <td class="boldbase" width="2%">#</td>
            <td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="12%">%s</td>
            <td class="boldbase" width="10%">%s</td>
            <td class="boldbase" width="20%">%s</td>
            <td class="boldbase" width="20%">%s</td>
            <td class="boldbase" style="width: 150px;">%s</td>
        </tr>
END
    , _('Incoming IP')
    , _('Service')
    , _('Policy')
    , _('Translate to')
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
            my $protocol = uc($splitted{'protocol'});
            my $source = $splitted{'source'};
            my $src_dev = $splitted{'src_dev'};
            my $num = $i+1;
        
            my $enabled_gif = $DISABLED_PNG;
            my $enabled_alt = _('Disabled (click to enable)');
            my $enabled_action = 'enable';
            if ($splitted{'enabled'} eq 'on') {
                $enabled_gif = $ENABLED_PNG;
                $enabled_alt = _('Enabled (click to disable)');
                $enabled_action = 'disable';
            }
            my $destination = $splitted{'destination'};
            my $dst_dev = $splitted{'dst_dev'};
            my $nat_target = $splitted{'nat_target'};
            my $filter_target = $splitted{'filter_target'};

            my $policy_gif = $DENY_PNG;
            my $policy_alt = _('DENY');
            my $policy_text = _('DENY from');
            my $policy_color = $colourred;
            if ($nat_target eq 'RETURN') {
                $policy_gif = $RETURN_PNG;
                $policy_alt = _('Do not NAT');
                $policy_text = _('Do not NAT from');
                $policy_color = $colourred;
            }
            if ($nat_target eq 'NETMAP') {
                $policy_gif = $MAP_PNG;
                $policy_alt = _('Map network');
                $policy_text = _('Map network from');
                $policy_color = $colourgreen;
            }
            if ($nat_target eq 'DNAT') {
		# 2013-7-26 能士项目屏蔽入侵防御 修改默认图标为ACCEPT
		# 2014-5-6 打开入侵防御
                # $policy_gif = $IPS_PNG;
                # $policy_alt = _('入侵防御');
                # $policy_text = _('通过入侵防御');
                # $policy_color = $colourgreen;
                # 2017-12-6 不再显示成入侵防御
		$policy_gif = $ALLOW_PNG;
                $policy_alt = _('ALLOW');
                $policy_text = _('ALLOW from');
                $policy_color = $colourgreen;
		#若要恢复删除上方未注释内容并取消4行注释
            if ($filter_target eq 'REJECT') {
                $policy_gif = $REJECT_PNG;
                $policy_alt = _('拒绝');
                $policy_text = _('拒绝来自');
                $policy_color = $colourred;
            }
            if ($filter_target eq 'DROP') {
                $policy_gif = $DENY_PNG;
                $policy_alt = _('丢弃');
                $policy_text = _('丢弃来自');
                $policy_color = $colourred;
            }
            if ($filter_target eq 'ACCEPT') {
                $policy_gif = $ALLOW_PNG;
                $policy_alt = _('ALLOW');
                $policy_text = _('ALLOW from');
                $policy_color = $colourgreen;
            }
        }
        
            my $port = $splitted{'port'};
            my $remark = value_or_nbsp($splitted{'remark'});
            my $editing = 0;
            if ($is_editing || $add_external) {
                $editing = 1;
            }
            my $bgcolor = setbgcolor($editing, $line, $i);

            my $dest_long_value = generate_addressing($destination, $dst_dev, '', $i);
            if ($dest_long_value =~ /(?:^|&)ANY/) {
                $dest_long_value = "&lt;"._('ANY')."&gt;";
            }
            my $service_long_value = generate_service($port, $protocol, $i);
            if ($service_long_value =~ /(?:^|&)ANY/) {
                $service_long_value = "&lt;"._('ANY')."&gt;";
            }

            my $target_ip = $splitted{'target_ip'};
            my $target_port = $splitted{'target_port'};

            my $target_long_value = generate_addressing($target_ip, '', '', $i);
            if ($target_long_value =~ /(?:^|&)ANY/) {
                $target_long_value = "&lt;"._('ANY')."&gt;";
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

	    my $display_target_port = '';
	    if ($target_port ne '') {
		$display_target_port = ": $target_port";
	    }
            printf <<EOF
            <tr class="$bgcolor">
                <td v align="center">$num</td>
                <td v>$dest_long_value</td>
                <td v>$service_long_value</td>
                <td v align="center">
                  <img src="$policy_gif" alt="$policy_alt" title="$policy_alt">
                </td>
                <td v>$target_long_value $display_target_port</td>
                <td v title="$remark">$remark</td>

                <td class="actions" v nowrap="nowrap">
EOF
            ;
            if ($editable) {
                printf <<EOF
                    <!--<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                        <input class="imagebutton $style{'up'}" type='image' name="submit" SRC="$UP_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="up"/>
                        <input TYPE="hidden" name="line" value="$i"/>
			<img class="clear $style{'clear_up'}" src="$CLEAR_PNG"/>
                    </form>-->
EOF
                    , _("Up")
                    ;
                printf <<EOF
                    <!--<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                        <input class='imagebutton $style{'down'}' type='image' name="submit" SRC="$DOWN_PNG" ALT="%s"/>
                        <input TYPE="hidden" name="ACTION" value="down"/>
                        <input TYPE="hidden" name="line" value="$i"/>
			<img class="clear $style{'clear_down'}" src="$CLEAR_PNG"/>
                    </form>-->
EOF
                    , _("Down")
                    ;
                printf <<EOF
                    <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                        <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" ALT="$enabled_alt"/>
                        <input TYPE="hidden" name="ACTION" value="$enabled_action"/>
                        <input TYPE="hidden" name="line" value="$i"/>
                    </FORM>
                    <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                        <input class='imagebutton' type='image' name="submit" SRC="$ADD_PNG" ALT="%s"/>
                        <input TYPE="hidden" name="ACTION" value="add_external"/>
                        <input TYPE="hidden" name="line" value="$i"/>
                    </FORM>                    
                    <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                        <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s"/>
                        <input TYPE="hidden" name="source" value="$source"/>
                        <input TYPE="hidden" name="src_dev" value="$src_dev"/>
                        <input TYPE="hidden" name="ACTION" value="edit"/>
                        <input TYPE="hidden" name="line" value="$i"/>
                    </FORM>
                    <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" onsubmit="return confirm('确定要删除此规则？')" style=";margin-top:3px;">
                        <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="delete"/>
                        <input TYPE="hidden" name="line" value="$i"/>
                    </FORM>
                </td>
            </tr>
EOF
            , _('Add access rule')
            , _('Edit')
            , _('Delete');
	    }
        
	    if ($target ne 'NETMAP') {
            foreach my $src (split(/\|/, $source)) {
                my $editing = 0;
                if ($edit_external && ($src eq $old_source)) {
                    $editing = 1;
                }
                $bgcolor = setbgcolor($editing, $line, $i);
                my $src_long_value = generate_addressing($src, '', '', $i);
                if ($src_long_value =~ /(?:^|&)ANY/ || $src_long_value =~ /^any$/) {
                    $src_long_value = "&lt;"._('ANY')."&gt;";
                }
                printf <<EOF
            <tr class="$bgcolor">
              <td>&nbsp;</td>
              <td v colspan='3'><font color='$policy_color'>$policy_text</font>:</td>
              <td align='left' colspan='2'>$src_long_value</td>
              <td class="actions" v nowrap="nowrap" >
                  <img class="clear" src="$CLEAR_PNG"/>
                  <img class="clear" src="$CLEAR_PNG"/>
                  <img class="clear" src="$CLEAR_PNG"/>
                  <img class="clear" src="$CLEAR_PNG"/>
                  <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                      <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s" />
                      <input TYPE="hidden" name="source" value="$src"/>
                      <input TYPE="hidden" name="ACTION" value="edit_external"/>
                      <input TYPE="hidden" name="line" value="$i"/>
                  </FORM>
                  <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                      <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s" />
                      <input TYPE="hidden" name="old_source" value="$src"/>
                      <input TYPE="hidden" name="ACTION" value="delete_external"/>
                      <input TYPE="hidden" name="line" value="$i"/>
                  </FORM>
              </td>
            </tr>
EOF
                ;
            }
            foreach my $src (split(/\|/, $src_dev)) {
                my $editing = 0;
                if ($edit_external && ($src eq $old_src_dev)) {
                    $editing = 1;
                }
                $bgcolor = setbgcolor($editing, $line, $i);
                my $src_long_value = generate_addressing('', $src, '', $i);
                if ($src_long_value =~ /(?:^|&)ANY/) {
                    $src_long_value = "&lt;"._('ANY')."&gt;";
                }
                printf <<EOF
            <tr class="$bgcolor">
              <td>&nbsp;</td>
              <td v colspan='3'><font color='$policy_color'>$policy_text</font>:</td>
              <td align='left' colspan='2'>$src_long_value</td>
              <td class="actions" v nowrap="nowrap" >
                  <img class="clear" src="$CLEAR_PNG"/>
                  <img class="clear" src="$CLEAR_PNG"/>
                  <img class="clear" src="$CLEAR_PNG"/>
                  <img class="clear" src="$CLEAR_PNG"/>
                  <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                      <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s" />
                      <input TYPE="hidden" name="src_dev" value="$src"/>
                      <input TYPE="hidden" name="ACTION" value="edit_external"/>
                      <input TYPE="hidden" name="line" value="$i"/>
                  </FORM>
                  <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style=";margin-top:3px;">
                      <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s" />
                      <input TYPE="hidden" name="old_src_dev" value="$src"/>
                      <input TYPE="hidden" name="ACTION" value="delete_external"/>
                      <input TYPE="hidden" name="line" value="$i"/>
                  </FORM>
              </td>
            </tr>
EOF
                , _('access from')
                ;
            }
	    } else {
		printf <<EOF
	    <tr class="$bgcolor">
              <td colspan="6">&nbsp;</td>
            </tr>
EOF
;
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

if($i>0)
{
printf <<EOF
    <table class="list-legend" cellpadding="0" cellspacing="0">
        <tr>
            <td CLASS="boldbase">%s:
            <IMG SRC="$ENABLED_PNG" ALT="%s" />
            %s
            <IMG SRC='$DISABLED_PNG' ALT="%s" />
            %s
            <IMG SRC="$EDIT_PNG" alt="%s" />
            %s
            <IMG SRC="$DELETE_PNG" ALT="%s" />
            %s
			    <IMG SRC="$ADD_PNG" ALT="%s" />
            %s
			</td>
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
, _('Add')
, _('Add')
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

    my $userdef = sprintf <<EOF
<option value="">%s</option>
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

sub display_add($$$$$) {
    my $is_editing = shift;
    my $add_external = shift;
    my $edit_external = shift;
    my $source = shift;
    my $src_dev = shift;    
    my $line = shift;
    my $old_source = $source;
    my $old_src_dev = $src_dev;
    
    my %config;
    my %checked;
    my %selected;
    
    if (($is_editing || $add_external || $edit_external) && ($par{'sure'} ne 'y')) {
        %config = config_line(read_config_line($line));
    }
    else {
        %config = %par;
    }
    if (! $is_editing) {
	# put default values here
	$config{'enabled'} = 'on';
    }
    
    my $exteranl = 0;
    my $disabled = "";
    if ($add_external || $edit_external) {
        $external = 1;
        $disabled = "disabled";
    }
    my $enabled = $config{'enabled'};
    my $log = $config{'log'};
    my $protocol = $config{'protocol'};
    if (! $protocol && !$is_editing) {
        $protocol = 'any';
    }
    my $dst_dev = $config{'dst_dev'};
    if ($is_editing) {
        $source = $config{'source'};
        $src_dev = $config{'src_dev'};
    }
    my $src_ip = '';
    my $src_user = '';
    my $destination = $config{'destination'};
    my $dst_ip = '';
    my $dst_user = '';
    my $target = $config{'target_ip'};
    my $target_ip_ip = '';
    my $target_ip_user = '';
    my $target_ip_lb = '';
    my $target_ip_map = '';
    my $port = $config{'port'};
    my $target_port = $config{'target_port'};
    my $remark = $config{'remark'};
    my $nat_policy = $config{'nat_target'};
    my $filter_policy = $config{'filter_target'};
    if ($nat_policy =~ /^$/) {
	$nat_policy = 'DNAT';
    }
    if ($filter_policy =~ /^$/) {
	#2013-7-26 能士项目屏蔽入侵防御后修改$filter_policy默认值，由ALLOW改为ACCEPT
	#2014-5-6 打开入侵防御
	$filter_policy = 'ALLOW';
	#$filter_policy = 'ACCEPT';
    }

    my $src_type = 'any';
    my $dst_type = 'dev';
    my $target_type = 'ip';

    $checked{'ENABLED'}{$enabled} = 'checked';
    $checked{'LOG'}{$log} = 'checked';
    $selected{'PROTOCOL'}{$protocol} = 'selected';

    if ($source =~ /^$/ || $source =~ /^any$/) {
        $src_type = 'any';
        foreach my $item (split(/&/, $src_dev)) {
            $selected{'src_dev'}{$item} = 'selected';
        }
        if ($src_dev !~ /^$/) {
            $src_type = 'dev';
        }
    }
    else {
        if ($source =~ /OPENVPNUSER:/) {
            $src_user = $source;
            foreach $item (split(/&/, $src_user)) {
                $selected{'src_user'}{$item} = 'selected';
            }
            $src_type = 'user';
        }
        else {
            $src_ip = $source;
            if ($src_ip !~ /^$/) {
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
            $dst_user = $destination;
            foreach $item (split(/&/, $dst_user)) {
                $selected{'dst_user'}{$item} = 'selected';
            }
            $dst_type = 'user';
        }
        else {
            $dst_ip = $destination;
            if ($dst_ip !~ /^$/) {
                $dst_type = 'ip';
            }
        }
    }

    if ($target !~ /^$/) {
        if ($target =~ /OPENVPNUSER:/) {
            $target_ip_user = $target;
            foreach $item (split(/&/, $target_ip_user)) {
                $selected{'target_user'}{$item} = 'selected';
            }
            $target_type = 'user';
        }
        else {
	    if ($target =~ /\-/) {
		$target_type = 'lb';
		$target_ip_lb = $target;
	    } else {
		$target_type = 'ip';
		$target_ip_ip = $target;
	    }
        }
    }
    if ($nat_policy eq 'NETMAP') {
	$target_type = 'map';
	$target_ip_map = $target;
    }
    
    $selected{'src_type'}{$src_type} = 'selected';
    $selected{'dst_type'}{$dst_type} = 'selected';
    $selected{'target_type'}{$target_type} = 'selected';
    $selected{'nat_policy'}{$nat_policy} = 'selected';
    $selected{'filter_policy'}{$filter_policy} = 'selected';

    my %foil = ();
    $foil{'title'}{'src_any'} = 'none';
    $foil{'title'}{'src_user'} = 'none';
    $foil{'title'}{'src_ip'} = 'none';
    $foil{'title'}{'src_dev'} = 'none';
    $foil{'value'}{'src_any'} = 'none';
    $foil{'value'}{'src_user'} = 'none';
    $foil{'value'}{'src_ip'} = 'none';
    $foil{'value'}{'src_dev'} = 'none';

    $foil{'title'}{'dst_user'} = 'none';
    $foil{'title'}{'dst_ip'} = 'none';
    $foil{'title'}{'dst_dev'} = 'none';
    $foil{'value'}{'dst_user'} = 'none';
    $foil{'value'}{'dst_ip'} = 'none';
    $foil{'value'}{'dst_dev'} = 'none';

    $foil{'title'}{'target_user'} = 'none';
    $foil{'title'}{'target_ip'} = 'none';
    $foil{'title'}{'target_lb'} = 'none';
    $foil{'title'}{'target_map'} = 'none';
    $foil{'value'}{'target_user'} = 'none';
    $foil{'value'}{'target_ip'} = 'none';
    $foil{'value'}{'target_lb'} = 'none';
    $foil{'value'}{'target_map'} = 'none';

    $foil{'title'}{"src_$src_type"} = 'table-row';
    $foil{'value'}{"src_$src_type"} = 'table-row';
    $foil{'title'}{"dst_$dst_type"} = 'table-row';
    $foil{'value'}{"dst_$dst_type"} = 'table-row';
    $foil{'title'}{"target_$target_type"} = 'table-row';
    $foil{'value'}{"target_$target_type"} = 'table-row';
    
    $src_ip =~ s/&/\n/gm;
    $dst_ip =~ s/&/\n/gm;
    $source =~ s/&/\n/gm;
    $destination =~ s/&/\n/gm;
    $port =~ s/&/\n/gm;
    $target_port =~ s/&/\n/gm;

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
    my $button = _("Create Rule");
    my $title = '';
    
   
    my $policy = "";
    if ($filter_policy eq "RETURN") {
        $policy = "hidden";
    }

	$titles = "添加DNAT规则";
    
    if ($is_editing) {
        $action = 'edit';
        $button = _("Update Rule");
        $show = "showeditor";
		$titles =  "编辑DNAT规则";
    }
	 if ($#errormessages ne -1) { $show = "showeditor";}
    elsif ($add_external) {
        $action = 'add_external';
        $button = _("Add access rule");
        $show = "showeditor";
        $title = _("Access Rule Editor");
    }
    elsif ($edit_external) {
        $action = 'edit_external';
        $button = _("Update access rule");
        $show = "showeditor";
        $title = _("Access Rule Editor");
    }
    
    openeditorbox($titles, $title, $show, "createrule");
	if($external){
		printf <<EOF
			</form>
		<form name="DNAT_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
        <table width="100%" cellpadding="0" cellspacing="0">
EOF
;
	}
    if (!$external) {
	
    printf <<EOF
		</form>
		<form name="DNAT_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr class="env">
                <td class="add-div-type">%s</td>
                <td width="200px" >%s *<select name="dst_type" id="dst_type" $disabled onchange="toggleTypes('dst');" onkeyup="toggleTypes('dst');" style="width:149px">
                          <option value="dev" $selected{'dst_type'}{'dev'}>%s</option>
                          <option value="ip" $selected{'dst_type'}{'ip'}>%s</option>
                          <option value="user" $selected{'dst_type'}{'user'}>%s</option>
                    </select>
                </td>
               <td colspan="3">
                      <div width='200px' class="all_dst" id="dst_dev_t" style="display:$foil{'title'}{'dst_dev'}">%s</div>
                      <div width='200px' class="all_dst" id="dst_ip_t" style="display:$foil{'title'}{'dst_ip'}">%s</div>
                      <div width='200px' class="all_dst" id="dst_user_t" style="display:$foil{'title'}{'dst_user'}" style="width:350px; height: 90px;">%s</div>
EOF
        , _('Incoming IP')
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
                                <div id='dst_dev_v' class="all_dst" style='display:$foil{'value'}{'dst_dev'}'>
                                    <select name="dst_dev" multiple $disabled style="width: 350px; height: 90px;">
EOF
    ;
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
                                        <option value='$key' $selected{'dst_dev'}{$key}>%s $desc - %s:%s</option>
EOF
            , _('Uplink')
            , _('IP')
            , _('All known')
            ;
            eval {
                my %ulhash;
                &readhash("${swroot}/uplinks/$name/settings", \%ul);
                foreach my $ipcidr (split(/,/, $ul{'RED_IPS'})) {
                    my ($ip) = split(/\//, $ipcidr);
                    next if ($ip =~ /^$/);
                    printf <<EOF
                                        <option value='$ip:$key' $selected{'dst_dev'}{"$ip:$key"}>%s $desc - %s:$ip</option>
EOF
                    , _('Uplink')
                    , _('IP')
                    ;
                }
            }
        }

        foreach my $item (@nets) {
            printf <<EOF
                                        <option value="$item" $selected{'dst_dev'}{$item}>%s %s - %s:%s</option>
EOF
            , _('Zone')
            , $strings_zone{$item}
            , _('IP')
            , _('All known')
            ;
            foreach my $ipcidr (split(/,/, $ether{$item.'_IPS'})) {
                my ($ip) = split(/\//, $ipcidr);
                next if ($ip =~ /^$/);

                printf <<EOF
                                        <option value="$ip:$item" $selected{'dst_dev'}{"$ip:$item"}>%s %s - %s:$ip</option>
EOF
                , _('Zone')
                , $strings_zone{$item}
                , _('IP')
                ;
            }
        }

        foreach my $tap (@{get_taps()}) {
            my $key = "VPN:".$tap->{'name'};
            my $name = $tap->{'name'};
            next if ($tap->{'bridged'});
            printf <<EOF
                                        <option value='$key' $selected{'dst_dev'}{$key}>%s $name - %s:%s</option>
EOF
            , _('VPN')
            , _('IP')
            , _('All known')
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
                                <div id='dst_ip_v' class="all_dst" style='display:$foil{'title'}{'dst_ip'}'>
                                    <textarea name='dst_ip' wrap='off' $disabled style="width: 350px; height: 90px;">$dst_ip</textarea>
                                </div>
EOF
        ;
    #### IP end #################################################################

    #### User begin #############################################################
        printf <<EOF
                                <div id='dst_user_v' class="all_dst" style='display:$foil{'title'}{'dst_user'}'>
                                    <select name="dst_user" multiple $disabled style="width: 350px; height: 90px;">
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
				<tr class="odd">
                <td class="add-div-type"> %s</td>
                <td >%s *
                                <select name="service_port" $disabled onchange="selectService('protocol', 'service_port', 'port');toggleTypes('target')" onkeyup="selectService('protocol', 'service_port', 'port');">
                                    <option value="any/any">&lt;%s&gt;</option>
EOF
        , _('Incoming Service/Port')
        , _('Service')
        , _('ANY')
        ;
        my ($sel, $arr) = create_servicelist($protocol, $config{'port'});
        print @$arr;
        # check if ports should be enabled
        if ($protocol eq "" || $protocol eq "any" || $protocol eq "icmp") {
        $portsdisabled = 'disabled="disabled"';
        }
        printf <<EOF
                                </select>
                </td>
				<td>%s *
                                <select name="protocol" $disabled onchange="updateService('protocol', 'service_port', 'port');toggleTypes('target');" onkeyup="updateService('protocol', 'service_port', 'port');" style="width:144px">
                                    <option value="any" $selected{'PROTOCOL'}{'any'}>&lt;%s&gt;</option>
                                    <option value="tcp" $selected{'PROTOCOL'}{'tcp'}>TCP</option>
                                    <option value="udp" $selected{'PROTOCOL'}{'udp'}>UDP</option>
                                    <option value="tcp&udp" $selected{'PROTOCOL'}{'tcp&udp'}>TCP + UDP</option>
                                    <option value="esp" $selected{'PROTOCOL'}{'esp'}>ESP</option>
                                    <option value="gre" $selected{'PROTOCOL'}{'gre'}>GRE</option>
                                    <option value="icmp" $selected{'PROTOCOL'}{'icmp'}>ICMP</option>
                                </select>
                            </td> 
							
							
                <td colspan="2">
EOF
        , _('Protocol')
        , _('ANY')
;
my $isdisplay = "class='hidden_class'";
if($port ne "")
{
	$isdisplay = "";
	#如果端口不为空，屏蔽This rule will match all the destination ports的字样 by wl 2013.12.17
	$note_display = "class='hidden_class'";
}
printf <<EOF
				<ul  id="port_ul" $isdisplay><li>%s</li>
                    <li><textarea  name="port"$disabled rows="3" $portsdisabled onkeyup="updateService('protocol', 'service_port','port');">$port</textarea></li>
				</ul>
EOF
, _('Incoming port/range (one per line, e.g. 80, 80:88)')
;

printf <<EOF
				<ul id="port_ul2" $note_display><li>%s</li></ul>
EOF
,_('This rule will match all the destination ports')
;
printf <<EOF
                            </td>
                        </tr>
       
            <tr class="env">
            <td id="translate_to_td" class="add-div-type" rowspan="" style='border-bottom:1px solid #999;'>%s *</td>
			<td class="add-div-type" >%s</td>
			<td  colspan='3'><select id="target_type" name="target_type" $disabled onchange="toggleTypes('target');" onkeyup="toggleTypes('target');" style="width:184px">
                                <option value="ip" $selected{'target_type'}{'ip'} >%s</option>
                                <option value="user" $selected{'target_type'}{'user'} >%s</option>
                                <option value="lb" $selected{'target_type'}{'lb'} >%s</option>
                                <option value="map" $selected{'target_type'}{'map'} >%s</option>
                 </select>
            </td>
			</tr>
EOF
        , _('Translate to')
        , _('Type')

        , _('IP')
        , _('OpenVPN User')
        , _('流量均衡')
        , _('网络映射')
        ;

    ##########
    # TARGET #
    ##########

    #### IP begin ###############################################################
        printf <<EOF

        <tr class="env target_tr_ip all_tr" id='target_ip_v' style='display:$foil{'value'}{'target_ip'}'>
		<td class="add-div-type" >%s *</td>
		<td colspan="3">
            <input name='target_ip_ip' value="$target_ip_ip"  size="10" type="text" style="width: 180px;" />
        </td>
		</tr>
		
		<tr class="env target_tr_ip all_tr all_port_tr" id='target_ip_v' style='display:$foil{'value'}{'target_ip'}'>
        <td class="add-div-type" >%s </td>
		<td colspan="3">
            <input name='target_port_ip' value="$target_port"  size="10" type="text" style="width: 150px;"  />
        </td>
        </tr>
		
        <tr class="env target_tr_ip all_tr" id='target_ip_v' style='display:$foil{'value'}{'target_ip'}'>
        <td class="add-div-type" >%s *</td>       
        <td colspan="3">
        <select class="policy" name="policy_ip" $disabled  style="width:184px">
            <option value="DNAT" $selected{'nat_policy'}{'DNAT'}>%s</option>
            <option value="RETURN" $selected{'nat_policy'}{'RETURN'}>%s</option>
        </select>
EOF
, _('Insert IP')
, _('Port/Range (e.g. 80, 80:88)')
, _('NAT策略')
 , 'NAT'
 , _('Do not NAT')
 ;		
 
if (!$external) {
    &nat_type($filter_policy);
}
	


    #### IP end #################################################################

    #### User begin #############################################################
        printf <<EOF
		        </td>
        </tr>
        <tr class="env target_tr_user all_tr" id='target_user_v' style='display:$foil{'value'}{'target_user'}'>
            <td class="add-div-type" >%s</td>
            <td colspan="3">
                <select name="target_ip_user" $disabled style="width: 250px;">
EOF
, _('Select OpenVPN user')
;
		foreach my $item (@openvpnusers) 
		{
            printf <<EOF
           <option value="OPENVPNUSER:$item" $selected{'target_ip_user'}{"OPENVPNUSER:$item"}>$item</option>
EOF
;
        }
        printf <<EOF
                        </select>
                    </td>		
        </tr>
        <tr class="env target_tr_user all_tr  all_port_tr" id='target_user_v' style='display:$foil{'value'}{'target_user'}'>
			<td class="add-div-type" >%s *</td>
			<td colspan="3">
                <input name='target_port_user' value="$target_port" $disabled size="10" type="text" style="width: 150px;"  />
            </td>
		</tr>
		<tr class="env target_tr_user all_tr" id='target_user_v' style='display:$foil{'value'}{'target_user'}'>
            <td class="add-div-type" >%s</td>
                   
EOF
        , _('Port/Range (e.g. 80, 80:88)')
        , _('NAT策略')
;
		
printf <<EOF
                    
                    <td colspan="3">
                        <select class="policy" name="policy_user" $disabled>
                            <option value="DNAT" $selected{'nat_policy'}{'DNAT'}>%s</option>
                            <option value="RETURN" $selected{'nat_policy'}{'RETURN'}>%s</option>
                        </select>
                    

EOF
        , 'NAT'
        , _('Do not NAT')
;
if (!$external) {
    &nat_type($filter_policy);
}
print "</td></tr>";
    #### User end ###############################################################

    #### IP RANGE begin #########################################################
        printf <<EOF
        <tr class="env target_tr_lb all_tr" id='target_lb_v' style='display:$foil{'value'}{'target_lb'}'>
            <td class="add-div-type" >%s *</td>
			<td colspan="3">
                <input name='target_ip_lb' value="$target_ip_lb" $disabled size="10" type="text" style="width: 250px;" />
            </td>
		</tr>
		<tr class="env target_tr_lb all_tr  all_port_tr" id='target_lb_v' style='display:$foil{'value'}{'target_lb'}'>
            <td class="add-div-type" >%s </td>
			 <td colspan="3">
                <input name='target_port_lb' value="$target_port" $disabled size="10" type="text" style="width: 150px;" />
            </td>
		</tr>
		<tr class="env target_tr_lb all_tr" id='target_lb_v' style='display:$foil{'value'}{'target_lb'}'>
            <td class="add-div-type" >%s</td>
			<td colspan="3">
                <select class="policy" name="policy_lb" $disabled>
                    <option value="DNAT" $selected{'nat_policy'}{'DNAT'}>%s</option>
                    <option value="RETURN" $selected{'nat_policy'}{'RETURN'}>%s</option>
                </select>
            
        
EOF
        , _('IP范围')
        , _('Port/Range (e.g. 80, 80:88)')
        , _('NAT策略')
        , 'NAT'
        , _('Do not NAT')
        ;
if (!$external) {
    &nat_type($filter_policy);
}
print "</td></tr>";
    #### IP RANGE end ###########################################################

    #### NETMAP begin ###########################################################
        printf <<EOF
        <tr class="env target_tr_map all_tr" id='target_map_v' style='display:$foil{'value'}{'target_map'}' colspan="3">
            <td class="add-div-type" >%s</td>
			<td colspan="3">
                <input name='target_ip_map' value="$target_ip_map" $disabled size="10" type="text" style="width: 250px;" />
            </td>
</tr>
		
EOF
        , _('Insert subnet')
        ;
        }

        if ($add_external || $edit_external) {
            $hidden = "";
        }
        if (!($old_source =~ m/\|/) && !($old_src_dev =~ m/\|/) && !($old_source && $old_src_dev)) {
            printf <<EOF
			<tr class="odd">
            <td class="add-div-type">%s</td>
            <td width="200px" >%s &nbsp;&nbsp;
                    <select id="src_type" name="src_type" onchange="toggleTypes('src');" onkeyup="toggleTypes('src');">
                        <option value="any" $selected{'src_type'}{'any'}>%s</option>
                        <option value="dev" $selected{'src_type'}{'dev'}>%s</option>
                        <option value="ip" $selected{'src_type'}{'ip'}>%s</option>
                        <option value="user" $selected{'src_type'}{'user'}>%s</option>
                    </select>
            </td>
			<td>
                <div id="src_any_t" class="all_src" style="display:$foil{'title'}{'src_any'};">%s</div>
                <div id="src_dev_t" class="all_src" style="display:$foil{'title'}{'src_dev'};"></div>
                <div id="src_ip_t" class="all_src" style="display:$foil{'title'}{'src_ip'};">%s</div>
                <div id="src_user_t" class="all_src" style="display:$foil{'title'}{'src_user'};">%s</div>
EOF
    , _('访问源')
    , _('SourceType')
    , _('ANY')
    , _('Zone/VPN/Uplink')
    , _('Network/IP')
    , _('OpenVPN User')
    , _('Access from every zone')
    , _('Insert network/IPs (one per line)')
    , _('Select OpenVPN users (hold CTRL for multiselect)')
    ;

    ##########
    # SOURCE #
    ##########

    #### Device begin ###########################################################
    printf <<EOF
                                    <div id='src_dev_v'  class="all_src" style='display:$foil{'value'}{'src_dev'}'>
                                        请按住CTRL多选<br /><select name="src_dev" multiple style="width: 250px; height: 90px;">
EOF
    ;

    printf <<EOF 
                                            <option value='UPLINK:ANY' $selected{'src_dev'}{'UPLINK:ANY'}>&lt;%s&gt;</option>
EOF
    , _('ANY Uplink')
    ;

    foreach my $ref (@{get_uplinks_list()}) {
    my $name = $ref->{'name'};
    my $key = $ref->{'dev'};
    my $desc = $ref->{'description'};
        printf <<EOF 
                                            <option value='$key' $selected{'src_dev'}{$key}>%s $desc [%s]</option>
EOF
    , _('Uplink')
    , _('RED')
    ;
    }

    foreach my $item (@nets) {
        printf <<EOF
                                            <option value="$item" $selected{'src_dev'}{$item}>%s</option>
EOF
    ,$strings_zone{$item}
    ;
    }
    foreach my $data (@$devices) {
        my $value = $data->{'portlabel'};
    my $key = "PHYSDEV:".$data->{'device'};
    my $zone = _("Zone: %s", $strings_zone{$data->{'zone'}});
    printf <<EOF
                                            <option value="$key" $selected{'src_dev'}{$key}>$value ($zone)</option>
EOF
    ;
    }
    printf <<EOF
                                            <option value="VPN:IPSEC" $selected{'src_dev'}{'VPN:IPSEC'}>IPSEC</option>
EOF
    ;
    foreach my $tap (@{get_taps()}) {
        my $key = "VPN:".$tap->{'name'};
    my $name = $tap->{'name'};
    next if ($tap->{'bridged'});
        printf <<EOF 
                                            <option value='$key' $selected{'src_dev'}{$key}>%s $name</option>
EOF
    , _('VPN')
    ;
    }

    printf <<EOF
                                        </select>
										</div>
                                  
EOF
    ;
    #### Device end #############################################################


    #### User begin #############################################################
    printf <<EOF
                                    <div id='src_user_v' class="all_src" style='display:$foil{'value'}{'src_user'}'>
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
                                    <div id='src_ip_v' class="all_src" style='display:$foil{'value'}{'src_ip'}'>
                                        <textarea name='src_ip' wrap='off' style="width: 250px; height: 90px;">$src_ip</textarea>
                                    </div>
									</td>
EOF
;
    #### IP end #################################################################

    }
    
    printf <<EOF
              </tr>
EOF
    ;
    if (!$external) {
    #### NETMAP end #############################################################
    printf <<EOF

            <tr class="odd">
				<td class="add-div-type" rowspan="4">%s</td>
                <td colspan="3"><input name="enabled" value="on" $disabled $checked{'ENABLED'}{'on'} type="checkbox">%s</td>
			</tr>
			<tr class="odd">
                <td  colspan="3"><input name="log" value="on" $disabled $checked{'LOG'}{'on'} type="checkbox">%s</td>
    	    </tr>
			
			<tr class="odd">
                <td  colspan="3">%s
                    <input name="remark" value="$remark" $disabled size="57" maxlength=50" type="text"/>
                </td>
            </tr>

			<tr class="odd">
                <td  colspan="3">%s *&nbsp;
                    <select name="position" $disabled style="width:140px"> 
                        <option value="0">%s</option>
EOF
        , _('Other')
        , _('Enabled')
        , _('Log')
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
EOF
        ;
        }
        printf <<EOF
        <input type="hidden" name="ACTION" value="$action"/>
        <input type="hidden" name="line" value="$line"/>
        <input type="hidden" name="old_source" value="$old_source"/>
        <input type="hidden" name="old_src_dev" value="$old_src_dev"/>
        <input type="hidden" name="sure" value="y"/>
EOF
        ;
        if (($old_source =~ m/\|/ || $old_src_dev =~ m/\|/) || ($old_source && $old_src_dev)) {
            printf <<EOF
        <input type="hidden" name="source" value="$old_source"/>
        <input type="hidden" name="src_dev" value="$old_src_dev"/>
EOF
            ;
        }

        &closeeditorbox($button, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

}

sub reset_values() {
    %par = ();
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    my $lof = $par{'log'};
    if ($action eq 'apply') {
        system($setdnat);
		`sudo fcmd $setdnat`;
        $notemessage = _("NAT rules applied successfully");
        &user_log("[目的地址转换] 应用规则");#应用了dnat规则")；#bug:Unrecognized character \xEF in column 41 at ./dnat.cgi line  => so change it to en
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
    
    if (((($action eq 'add_external') || ($action eq 'edit_external')) && ($sure eq 'y')) || ($action eq 'delete_external')) {
        my $line = $par{'line'};
        my $src_type = $par{'src_type'};
        
        my %config = config_line(read_config_line($line));
        
        my $source = "";
        my $src_dev = "";
        my $old_source = "";
        my $old_src_dev = "";
        my $old_source = $par{'old_source'};
        my $old_src_dev = $par{'old_src_dev'};
        
        if ($action ne 'delete_external') {
            if ($src_type eq 'any') {
                $source = 'any';
            }
            if ($src_type eq 'ip') {
                $source = $par{'src_ip'};
            }
            if ($src_type eq 'user') {
                $source = $par{'src_user'};
            }
            if ($src_type eq 'dev') {
                $src_dev = $par{'src_dev'};
            }
            $source =~ s/\n/&/gm;
            $source =~ s/\r//gm;
            $source =~ s/\|/&/g;
            $src_dev =~ s/\|/&/g;
        }
        if ($action eq 'add_external') {
            $config{'source'} .= "|$source";
            $config{'src_dev'} .= "|$src_dev";
        }
        else {
            if ($old_source) {
                $config{'source'} =~ s/($old_source)/$source/g;
            }
            elsif ($source) {
                $config{'source'} .= "|$source";
            }
            if ($old_src_dev) {
                $config{'src_dev'} =~ s/($old_src_dev)/$src_dev/g;
            }
            elsif ($src_dev) {
                $config{'src_dev'} .= "|$src_dev";
            }
        }
        
        $config{'source'} =~ s/\|\|/\|/g;
        $config{'source'} =~ s/^\|//g;
        $config{'source'} =~ s/\|$//g;
        $config{'src_dev'} =~ s/\|\|/\|/g;
        $config{'src_dev'} =~ s/^\|//g;
        $config{'src_dev'} =~ s/\|$//g;
        
        if (save_line($line,
                $config{'enabled'},
                $config{'protocol'},
                $config{'src_dev'},
                $config{'source'},
                $config{'dst_dev'},
                $config{'destination'},
                $config{'port'},
                $config{'target_ip'},
                $config{'target_port'},
                $config{'nat_target'},
                $config{'remark'},
                $config{'log'},
                $config{'filter_target'})) {
            reset_values();
        }
        else {
            $par{'src_dev'} = $src_dev;
            $par{'source'} = $source;
            $par{'sure'} = 'n';
        }
    }
    
    if (($action eq 'add') ||
        (($action eq 'edit')&&($sure eq 'y'))) {
        my $src_type = $par{'src_type'};
        my $dst_type = $par{'dst_type'};
        my $target_type = $par{'target_type'};
        my $source = '';
        my $destination = '';
        my $target = '';
        my $target_port = '';
        my $src_dev = '';
        my $dst_dev = '';
        my $old_pos = $par{'line'};
        my $nat_policy = '';
        my $filter_policy = '';
        if ($src_type eq 'any') {
            $source = 'any';
        }
        if ($src_type eq 'ip') {
            $source = $par{'src_ip'};
        }
        if ($src_type eq 'user') {
            $source = $par{'src_user'};
        }
        if ($dst_type eq 'ip') {
            $destination = $par{'dst_ip'};
        }
        if ($dst_type eq 'user') {
            $destination = $par{'dst_user'};
        }
        if ($src_type eq 'dev') {
            $src_dev = $par{'src_dev'};
        }
        if ($src_type eq '') {
            $source = $par{'source'};
            $src_dev = $par{'src_dev'};
        }
        else {
            $source =~ s/\n/&/gm;
            $source =~ s/\r//gm;
            $source =~ s/\|/&/g;
            $src_dev =~ s/\|/&/g;
        }
        if ($dst_type eq 'dev') {
            $dst_dev = $par{'dst_dev'};
        }
        if ($target_type eq 'ip') {
            $target = $par{'target_ip_ip'};
            $target_port = $par{'target_port_ip'};
            $nat_policy = $par{'policy_ip'};
        }
        if ($target_type eq 'user') {
            $target = $par{'target_ip_user'};
            $target_port = $par{'target_port_user'};
            $nat_policy = $par{'policy_user'};
        }
        if ($target_type eq 'lb') {
            $target = $par{'target_ip_lb'};
            $target_port = $par{'target_port_lb'};
            $nat_policy = $par{'policy_lb'};
        }
        if ($target_type eq 'map') {
            $target = $par{'target_ip_map'};
            $nat_policy = "NETMAP";
        }

        my $enabled = $par{'enabled'};
        #----------------------------------
        #冲突提示代码添加-2013-04-18-squall
        
        #获取格式化的line string
		my $current_line = format_line($par{'line'},
                        		      $enabled,
                        		      $par{'protocol'},
                        		      $src_dev,
                        		      $source,
                        		      $dst_dev,
                        		      $destination,
                        		      $par{'port'},
                        		      $target,
                        		      $target_port,
                        		      $nat_policy,
                        		      $par{'remark'},
                        		      $par{'log'},
                        		      $par{'filter_policy'});

        #这里的$par{'line'}从0开始计数
        my %data = config_line($current_line);
        my $tmp_action = $action;
        $data{'seq'} = $par{'position'}+1;
        if ($action eq 'edit') {
            my $old_seq = $old_pos;
            $old_seq = $old_pos+1;
            $tmp_action = $action."_$old_seq";
            foo(">>>>>old_seq = $old_seq\n");
            $data{'seq'} = $data{'seq'} -1;
        }
        my @conflict_list = conflict_detection(\%data,$tmp_action,"$ENV{'SCRIPT_NAME'}");
        
        #如果存在冲突
        if (@conflict_list) {
            print generate_conflict_warning_msg(\@conflict_list,$data{'seq'});
        }
        #end
        #----------------------------------
	if (save_line($par{'line'},
		      $enabled,
		      $par{'protocol'},
		      $src_dev,
		      $source,
		      $dst_dev,
		      $destination,
		      $par{'port'},
		      $target,
		      $target_port,
		      $nat_policy,
		      $par{'remark'},
		      $par{'log'},
		      $par{'filter_policy'})) {

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
            $par{'enabled'} = $enabled;
            $par{'src_dev'} = $src_dev;
            $par{'source'} = $source;
            $par{'dst_dev'} = $dst_dev;
            $par{'destination'} = $destination;
            $par{'target_ip'} = $target;
            $par{'target_port'} = $taret_port;
            $par{'nat_target'} = $nat_policy;
            $par{'filter_target'} = $par{'filter_policy'};
            $par{'sure'} = 'n';
        }
    }
}

sub check_form()
{
#表单检查代码添加-2012-08-30-zhouyuan
printf <<EOF
<script>	
var object = {
       'form_name':'DNAT_FORM',
       'option'   :{
                    'target_ip_ip':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'target_ip_user':{
                               'type':'select',
                               'required':'1',
                    },
                    'target_port_ip':{
                               'type':'text',
                               'required':'0',
                               'check':'port|port_range|',
                             },
                    'target_port_user':{
                               'type':'text',
                               'required':'1',
                               'check':'port|port_range|',
                             },
                    'target_ip_lb':{
                               'type':'text',
                               'required':'1',
                               'check':'ip_range|',
                             },
                    'target_port_lb':{
                               'type':'text',
                               'required':'1',
                               'check':'port|port_range|',
                             },
                    'target_ip_map':{
                               'type':'text',
                               'required':'1',
                               'check':'ip_mask|',
                             },
                    'remark':{
                               'type':'text',
                               'required':'0',
                               'check':'note|',
                             },
                    'dst_dev':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'dst_user':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'src_dev':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'src_user':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'dst_ip':{
                               'type':'textarea',
                               'required':'1',
                               'check':'ip|ip_mask|',
                             },
                    'port':{
                               'type':'textarea',
                               'required':'0',
                               'check':'port|port_range|',
                             },
                    'src_ip':{
                               'type':'textarea',
                               'required':'1',
                               'check':'ip|ip_mask|',
                             },
                 }
         }	 
var check = new  ChinArk_forms();
check._main(object);
//check._get_form_obj_table("DNAT_FORM");
</script>
EOF
;
}

&getcgihash(\%par);

&showhttpheaders();
my $extraheader = '
<script language="JavaScript" src="/include/services_selector.js"></script>
<script language="JavaScript" src="/include/check_explorer.js"></script>
<script type="text/javascript" src="/include/conflict_detection.js"></script>
<script language="JavaScript" src="/include/dnat.js"></script>';
&openpage(_('Port forwarding / Destination NAT configuration'), 1, $extraheader);

init_ethconfig();
configure_nets();
($devices, $deviceshash) = list_devices_description(3, 'GREEN|ORANGE|BLUE', 0);
save();

if ($reload) {
    system("touch $needreload");
}

my $errormessage = "";
foreach my $error(@errormessages)
{
	$errormessage .= $error."<br />";
}
&openbigbox($errormessage , $warnmessage, $notemessage);

if (-e $needreload) {
    applybox(_("Port forwarding / Destination NAT rules have been changed and need to be applied in order to make the changes active"));
}



my $is_editing = ($par{'ACTION'} eq 'edit');
my $add_external = ($par{'ACTION'} eq 'add_external');
my $edit_external = ($par{'ACTION'} eq 'edit_external');
display_rules($is_editing, $add_external, $edit_external, $par{'source'}, $par{'src_dev'}, $par{'line'});

&check_form();
&closebigbox();
&closepage();
