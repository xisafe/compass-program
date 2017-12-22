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
require 'firewall.pl';

my $xtaccess_config = "${swroot}/xtaccess/config";
my $xtaccess_settings = "${swroot}/xtaccess/settings";
my $xtaccess_default_settings = "${swroot}/xtaccess/default/settings";
my $ethernet_settings = "${swroot}/ethernet/settings";
my $setxtaccess = "/usr/local/bin/setxtaccess";
my $inputfwdir = '/etc/firewall/inputfw/';
my $needreload = "${swroot}/xtaccess/needreload";

my $ALLOW_PNG = '/images/firewall_accept.png';
my $IPS_PNG = '/images/firewall_ips.png';
my $DENY_PNG = '/images/firewall_drop.png';
my $REJECT_PNG = '/images/firewall_reject.png';
my $UP_PNG = '/images/stock_up-16.png';
my $DOWN_PNG = '/images/stock_down-16.png';
my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $EDIT_PNG = '/images/edit.png';
my $DELETE_PNG = '/images/delete.png';
my $OPTIONAL_PNG = '/images/blob.png';

my @day =  (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23);
my @hour = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59);
my %week = (
            1 => "星期一",
            2 => "星期二",
            3 => "星期三",
            4 => "星期四",
            5 => "星期五",
            6 => "星期六",
            7 => "星期天"
);
my (%par,%checked,%selected,%ether,%xtaccess);
my $errormessage = '';
my $policy = 'DENY';
my $log_accepts = 'off';
my @nets;
my $reload = 0;
my %xtaccesshash=();
my $xtaccess = \%xtaccesshash;

my $devices, $deviceshash = 0;
my $services_file = '/var/efw/xtaccess/services';
my $services_custom_file = '/var/efw/xtaccess/services.custom';

&readhash($ethernet_settings, \%ether);

if (-e $xtaccess_default_settings) {
    &readhash($xtaccess_default_settings, \%xtaccess);
}
if (-e $xtaccess_settings) {
    &readhash($xtaccess_settings, \%xtaccess);
}
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

sub set_policy() {
    if ($log_accepts ne $par{'LOG_ACCEPTS'}) {
    $log_accepts = $par{'LOG_ACCEPTS'};
    open(FILE,">$xtaccess_settings") or die "Unable to open config file '$xtaccess_settings' because $!.";
    print FILE "LOG_ACCEPTS=$log_accepts\n";
    close FILE;
	`sudo fmodify $xtaccess_settings`;
    }
    $reload = 1;
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
    my @lines = read_config_file($xtaccess_config);
    return $lines[$line];
}

sub save_config_file_back($) {
    my $ref = shift;
    my @lines = @$ref;
    open (FILE, ">$xtaccess_config");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
	`sudo fmodify $xtaccess_config`;
    $reload = 1;
}

sub line_count() {
    open (FILE, "$xtaccess_config") || return 0;
    my $i = 0;
    foreach (<FILE>) {
        $i++;
    }
    close FILE;
    return $i;
}

sub append_config_file($) {
    my $line = shift;
    open (FILE, ">>$xtaccess_config");
    print FILE $line."\n";
    close FILE;
	`sudo fmodify $xtaccess_config`;
    $reload = 1;
}

sub is_valid($) {
    my $line = shift;
    if ($line =~ /(?:(?:[^,]*),){4}/) {
        return 1;
    }
    return 0;
}

sub config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    if (! is_valid($line)) {
        return;
    }
    my @temp = split(/,/, $line);
    $config{'protocol'} = $temp[0];
    $config{'source'} = $temp[1];
    $config{'port'} = $temp[2];
    $config{'enabled'} = $temp[3];
    $config{'destination'} = $temp[4];
    $config{'dst_dev'} = $temp[5];
    $config{'log'} = $temp[6];
    $config{'logprefix'} = $temp[7];
    $config{'target'} = $temp[8];
    $config{'mac'} = $temp[9];
    $config{'remark'} = $temp[10];
    $config{'start_day'}= $temp[11];
    $config{'end_day'}= $temp[12];
    $config{'start_hour_min'}= $temp[13];
    $config{'end_hour_min'}= $temp[14];
    $config{'week'}= $temp[15];
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
             $data{'protocol'},
             $data{'source'},
             $data{'port'},
             $data{'enabled'},
             $data{'destination'},
             $data{'dst_dev'},
             $data{'log'},
             $data{'target'},
             $data{'mac'},
             $data{'remark'},
             $data{'start_day'}, 
             $data{'end_day'}, 
             $data{'week'},
             $data{'start_hour_min'}, 
             $data{'end_hour_min'}
             );
}

sub move($$) {
    my $line = shift;
    my $direction = shift;
    my $newline = $line + $direction;
    if ($newline < 0) {
        return;
    }
    my @lines = read_config_file($xtaccess_config);

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
    my @lines = read_config_file($xtaccess_config);
    my $myline = $lines[$old];
    my @newlines = ();

    # nothing to do
    if ($new == $old) {
        return;
    }
   
    if ($new > $#lines+1) {
        $new = $#lines+1;
    }

    open (FILE, ">$xtaccess_config");

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
	`sudo fmodify $xtaccess_config`;
    close(FILE);
}

sub delete_line($) {
    my $line = shift;
    my @lines = read_config_file($xtaccess_config);
    if (! @lines[$line]) {
        return;
    }
    delete (@lines[$line]);
    save_config_file_back(\@lines);
}

sub create_line($$$$$$$$$$$$$$$) {
    my $protocol = shift;
    my $source = shift;
    my $port = shift;
    my $enabled = shift;
    my $destination = shift;
    my $dst_dev = shift;
    my $log = shift;
    my $target = shift;
    my $mac = shift;
    my $remark = shift;    
    my $start_day = shift;
    my $end_day = shift;
    my $start_hour_min = shift;
    my $end_hour_min = shift;
    my $week = shift;
    $destination = &delete_same_data($destination);
    $mac = &delete_same_data($mac);
    $source = &delete_same_data($source);
    return "$protocol,$source,$port,$enabled,$destination,$dst_dev,$log,INPUTFW,$target,$mac,$remark,$start_day,$end_day,$start_hour_min,$end_hour_min,$week";
}

sub check_values($$$$$$$$$) {
    my $protocol = shift;
    my $source = shift;
    my $port = shift;
    my $enabled = shift;
    my $destination = shift;
    my $dst_dev = shift;
    my $log = shift;
    my $target = shift;
    my $mac = shift;

    my %valid_proto = ('TCP' => 1, 'UDP' => 1, 'TCP&UDP' => 1, 'OSPF' => 1, 'ESP' => 1, 'GRE' => 1, 'ICMP' => 1);
    #2013-7-27 屏蔽入侵防御
	#2014-5-6 打开入侵防御
	my %valid_targets = ( 'ACCEPT' => 1, 'ALLOW' => 1, 'DROP' => 1, 'REJECT' => 1 );
	#my %valid_targets = ( 'ACCEPT' => 1, 'DROP' => 1, 'REJECT' => 1 );
    #
    if ($protocol !~ /^$/) {
        if (! $valid_proto{uc($protocol)}) {
             push(@errormessages,_('Invalid protocol'));
        }
    }

    foreach my $item (split(/&/, $source)) {
        if (! is_ipaddress($item) && ! validmac($item)) {
             push(@errormessages,_('Invalid source IP address "%s"', $item));
        }
    }

    foreach my $item (split(/&/, $mac)) {
        if (!validmac($item)) {
             push(@errormessages, _('Invalid MAC address "%s"', $item));
        }
    }

    foreach my $ports (split(/&/, $port)) {
        if ($ports !~ /^(\d{1,5})(?:\:(\d{1,5}))?$/) {
            push(@errormessages,_('Invalid destination port "%s"', $ports));
        }
        my $port1 = $1;
        my $port2 = '65535';
        if ($2) {
            $port2 = $2;
        }

        if (($port1 < 0) || ($port1 > 65535)) {
                push(@errormessages,_('Invalid destination port "%s"', $port1));
        }

        if (($port2 < 0) || ($port2 > 65535)) {
             push(@errormessages, _('Invalid destination port "%s"', $port2));

        }
        if ($port1 > $port2) {
            push(@errormessages, _('The destination port range has a first value that is greater than or equal to the second value.'));
        }
    }

    if (! $valid_targets{uc($target)}) {
         push(@errormessages, _('Invalid policy "%s"', $target));
    }
	if ($#errormessages ne -1) {
        return 0;
    }
    return 1;
}

sub save_line($$$$$$$$$$$$$$$$) {
    my $line = shift;
    my $protocol = shift;
    my $source = shift;
    my $port = shift;
    my $enabled = shift;
    my $destination = shift;
    my $dst_dev = shift;
    my $log = shift;
    my $target = shift;
    my $mac = shift;
    my $remark = shift;

    my $start_day = shift;
    my $end_day = shift;
    my $week = shift;
    $week =~ s/\|/:/g;
    
    my $start_hour_min = shift;
    my $end_hour_min = shift;
    $source =~ s/\n/&/gm;
    $source =~ s/\r//gm;
    $source =~ s/\-/:/g;
    $destination =~ s/\n/&/gm;
    $destination =~ s/\r//gm;
    $port =~ s/\n/&/gm;
    $port =~ s/\r//gm;
    $port =~ s/\-/:/g;
    $mac =~ s/\n/&/gm;
    $mac =~ s/\r//gm;
    $mac =~ s/\-/:/g;
    $remark =~ s/\,//g;

    $dst_dev =~ s/\|/&/g;
    $source =~ s/\|/&/g;
    $destination =~ s/\|/&/g;

    if ($source =~ /none/) {
        $source = '';
    }
    if ($destination =~ /none/) {
        $destination = '';
    }

    if ($dst_dev =~ /ALL/) {
        $dst_dev = 'ALL';
    }
    if ($dst_dev =~ /none/) {
        $dst_dev = '';
    }

    if ($destination !~ /^$/) {
        $dst_dev = '';
    }
    if ($mac !~ /^$/) {
        $source = '';
    }

    if ($port =~ /any/) {
       $port = '';
    }
    if ($protocol =~ /any/) {
        $protocol = '';
    }

    if ($protocol eq 'icmp') {
        $port = '';
    }

    if ($target eq '') {
        $target = 'ACCEPT';
    }

    if (! check_values($protocol, $source, $port, $enabled, $destination, $dst_dev, $log, $target, $mac)) {
        return 0;
    }
    $start_day = format_date($start_day);
    $end_day = format_date($end_day);
	#未选择时间则保存为空
	if ($start_day eq '-0-0') 
	{
		$start_day = '';
		   
	}
	if($end_day eq '-0-0')
	{
	   $end_day = '';
	}
    my $tosave = create_line($protocol, $source, $port, $enabled, $destination, $dst_dev, $log,$target, $mac, $remark, $start_day,$end_day,$start_hour_min,$end_hour_min,$week);

    if ($line !~ /^\d+$/) {
        append_config_file($tosave);
        return 1;
    }
    my @lines = read_config_file($xtaccess_config);
    if (! $lines[$line]) {
         push(@errormessages,_('Configuration line not found!'));
        return 0;
    }

    my %split = config_line($lines[$line]);
    $lines[$line] = $tosave;
    save_config_file_back(\@lines);
    return 1;
}

#
# DESCRIPTION: 
# @param:      页面传入的基础信息
# @return:     格式化的line string
#
sub format_line($$$$$$$$$$$$$$$$) {
    my $line = shift;
    my $protocol = shift;
    my $source = shift;
    my $port = shift;
    my $enabled = shift;
    my $destination = shift;
    my $dst_dev = shift;
    my $log = shift;
    my $target = shift;
    my $mac = shift;
    my $remark = shift;

    my $start_day = shift;
    my $end_day = shift;
    my $week = shift;
    $week =~ s/\|/:/g;
    
    my $start_hour_min = shift;
    my $end_hour_min = shift;
    $source =~ s/\n/&/gm;
    $source =~ s/\r//gm;
    $source =~ s/\-/:/g;
    $destination =~ s/\n/&/gm;
    $destination =~ s/\r//gm;
    $port =~ s/\n/&/gm;
    $port =~ s/\r//gm;
    $port =~ s/\-/:/g;
    $mac =~ s/\n/&/gm;
    $mac =~ s/\r//gm;
    $mac =~ s/\-/:/g;
    $remark =~ s/\,//g;

    $dst_dev =~ s/\|/&/g;
    $source =~ s/\|/&/g;
    $destination =~ s/\|/&/g;

    if ($source =~ /none/) {
        $source = '';
    }
    if ($destination =~ /none/) {
        $destination = '';
    }

    if ($dst_dev =~ /ALL/) {
        $dst_dev = 'ALL';
    }
    if ($dst_dev =~ /none/) {
        $dst_dev = '';
    }

    if ($destination !~ /^$/) {
        $dst_dev = '';
    }
    if ($mac !~ /^$/) {
        $source = '';
    }

    if ($port =~ /any/) {
       $port = '';
    }
    if ($protocol =~ /any/) {
        $protocol = '';
    }

    if ($protocol eq 'icmp') {
        $port = '';
    }

    if ($target eq '') {
        $target = 'ACCEPT';
    }

    if (! check_values($protocol, $source, $port, $enabled, $destination, $dst_dev, $log, $target, $mac)) {
        return 0;
    }
    $start_day = format_date($start_day);
    $end_day = format_date($end_day);
	#未选择时间则保存为空
	if ($start_day eq '-0-0') 
	{
		$start_day = '';
		   
	}
	if($end_day eq '-0-0')
	{
	   $end_day = '';
	}
    my $tosave = create_line($protocol, $source, $port, $enabled, $destination, $dst_dev, $log,$target, $mac, $remark, $start_day,$end_day,$start_hour_min,$end_hour_min,$week);
    return $tosave;
}

sub generate_addressing($$$$) {
    my $addr = shift;
    my $dev = shift;
    my $mac = shift;
    my $rulenr = shift;

    my @addr_values = ();

    foreach my $item (split(/&/, $addr)) {
        if (($addr eq '0.0.0.0/0') or ($addr eq '')) {
            push (@addr_values, 'ANY');
            next;
        }
        push(@addr_values, $item);
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
        elsif ($item =~ /^(?:.*:)?UPLINK:(.*)$/) {
            my $ul = get_uplink_label($1);
            push(@addr_values, "$preip<font color='". $zonecolors{'RED'} ."'>"._('Uplink')." ".$ul->{'description'}."</font>$postip");
        }
        elsif ($item =~ /^(?:.*:)?VPN:(.*)$/) {
            my $val = $1;
            if ($val eq 'ANY') {
                $val = _('ANY');
            }
            if ($val eq 'SERVER') {
                $val = _('SSLVPN Server');
            }
            push(@addr_values, "$preip<font color='". $colourvpn ."'>"._('VPN')." ".$val."</font>$postip");
        }
        elsif ($item =~ /^ANY$/) {
            my $val = $1;
            push(@addr_values, "ANY");
        }
        else {
	    my $zone = $item;
	    if ($ip !~ /^$/) {
		($ip,$zone) = split(/:/, $item);
	    }
            push(@addr_values, "$preip<font color='". $zonecolors{$zone} ."'>".$strings_zone{$zone}."</font>$postip");
        }
    }
    foreach my $item (split(/&/, $mac)) {
        push(@addr_values, $item);
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
        #push(@service_values, "$display_protocol/$port");
        #next;
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


sub count_sys_rules($$$$) {
    my $refconf = shift;
    my $is_editing = shift;
    my $line = shift;
    my $editable = shift;
	my $length = 0;
    my @configs = ();
    if (ref($refconf) eq 'ARRAY') {
        @configs = @$refconf;
    }
    else {
        push(@configs, $refconf);
    }

    foreach my $configfile (@configs) {
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
    <tr>
        <td class="boldbase" width="2%">#</td>
        <td class="boldbase" width="8%">%s</td>
        <td class="boldbase" width="8%">%s</td>
        <td class="boldbase" width="8%">%s</td>
        <td class="boldbase" width="12%">时间段</td>            
        <td class="boldbase" width="7.5%">每周</td>
        <td class="boldbase" width="12%">每天时间段</td>
        <td class="boldbase" width="3.5%">%s</td>
        <td class="boldbase" width="24%">%s</td>
END
    , _('Source address')
    , _('Source interface')
    , _('Service')
    , _('Policy')
    , _('Remark')
    ;
    if ($editable) {
        printf <<END
        <td class="boldbase" width="15%">%s</td>
END
        , _('Actions')
        ;
    }
    printf <<END
    </tr>
END
    ;

    my $i = 0;
	my $length = @configs;
if($length >0)
{
    foreach my $configfile (@configs) {
        my @lines = read_config_file($configfile);
        foreach my $thisline (@lines) {
            chomp($thisline);
            my %splitted = config_line($thisline);

            if (! $splitted{'valid'}) {
                next;
            }

            my $protocol = uc($splitted{'protocol'});
            my $source = $splitted{'source'};
            my $num = $i+1;

            my $enabled_gif = $DISABLED_PNG;
            my $enabled_alt = _('Disabled (click to enable)');
            my $enabled_action = 'enable';
            if ($splitted{'enabled'} eq 'on') {
                $enabled_gif = $ENABLED_PNG;
                $enabled_alt = _('Enabled (click to disable)');
                $enabled_action = 'disable';
            }
            my $dst_dev = $splitted{'dst_dev'};
            my $port = $splitted{'port'};
        
            my $target = $splitted{'target'};
			#2013-7-27 屏蔽入侵防御后修改默认图标
			#2014-5-6 打开入侵防御
            my $policy_gif = $IPS_PNG;
            #my $policy_alt = _('入侵防御');
            my $policy_alt = _('内容过滤');
			#my $policy_gif = $ALLOW_PNG;
            #my $policy_alt = _('ALLOW');
			#
            if ($target eq 'ACCEPT') {
                $policy_gif = $ALLOW_PNG;
                $policy_alt = _('ALLOW');
            }
            if ($target eq 'DROP') {
                $policy_gif = $DENY_PNG;
                $policy_alt = _('DENY');
            }
            if ($target eq 'REJECT') {
                $policy_gif = $REJECT_PNG;
                $policy_alt = _('REJECT');
            }
            my $remark = value_or_nbsp($splitted{'remark'});
            if (!$editable) {
                $remark = _('Service (%s)', $splitted{'logprefix'});
            }

            my $log = '';
            if ($splitted{'log'} eq 'on') {
                $log = _('yes');
            }
            my $mac = $splitted{'mac'};

            my $bgcolor = setbgcolor($is_editing, $line, $i);
            ###不显示BLUE
            $dst_dev =~s/BLUE&//;
            my $dest_long_value = generate_addressing($destination, $dst_dev, '', $i);
            if ($dest_long_value =~ /(?:^|&)ANY/) {
                $dest_long_value = "&lt;"._('ANY')."&gt;";
            }
            my $src_long_value = generate_addressing($source, 0, $mac, $i);
			#print $src_long_value."haha"."<br />";
            if (($src_long_value =~ /(?:^|&)ANY/) ) {
                $src_long_value = "&lt;"._('ANY')."&gt;";
            }
			#print $src_long_value."haha"."<br />";
            my $service_long_value = generate_service($port, $protocol, $i);
            if ($service_long_value =~ /(?:^|&)ANY/) {
                $service_long_value = "&lt;"._('ANY')."&gt;";
            }
            if ( $i eq 0 ) {
                $style{'up'} = "hidden";
                $style{'clear_up'} = "";
            }
            else {
                $style{'up'} = "";
                $style{'clear_up'} = "hidden";
            }
            if ( $i + 1 eq scalar(@lines) ) {
                $style{'down'} = "hidden";
                $style{'clear_down'} = "";
            }
            else {
                $style{'down'} = "";
                $style{'clear_down'} = "hidden";
            }


			if($src_long_value eq "<font color=''></font>")
			{
				$src_long_value = "&lt;"._('ANY')."&gt;";
			}
            printf <<EOF
  <tr class="$bgcolor">
    <TD VALIGN="top" ALIGN="center">$num</TD>
    <TD VALIGN="top">$src_long_value</TD>
    <TD VALIGN="top">$dest_long_value</TD>
    <TD VALIGN="top">$service_long_value</TD>
EOF
;
if($splitted{'start_day'} && $splitted{'end_day'}){
printf <<EOF
            <td><b> $splitted{'start_day'}</b> 至 <b> $splitted{'end_day'}</b></td>
            <td>
EOF
;
}else{
printf <<EOF
            <td></td>
            <td>
EOF
;
}
    if($splitted{'week'})
    {
    my @weeks = split(":",$splitted{'week'});
    my $length = @weeks;
    if($length eq 7)
    {
        print "整周";
    }else{
    print "<ul>";
    for my $line(@weeks)
    {
        print "<li>".$week{$line}."</li> ";
    }
    print "</ul>";
    }
    }else{
        print "";
    }
if($splitted{'start_hour_min'} && $splitted{'end_hour_min'})
{
printf <<EOF
            </td>
            <td><b>$splitted{'start_hour_min'}</b>至<b>$splitted{'end_hour_min'}</b></td>
EOF
;
}else{
    printf <<EOF
            </td>
            <td></td>
EOF
;
}
printf <<EOF     
    <TD VALIGN="top" ALIGN="center">
      <IMG SRC="$policy_gif" ALT="$policy_alt" TITLE="$policy_alt">
    </TD>
    <TD VALIGN="top" >$remark</TD>
EOF
            ;

            if ($editable) {
                printf <<EOF
    <TD class="actions" VALIGN="top" ALIGN="center" nowrap="nowrap" style="vertical-align:middle">
      <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left">
        <input class='imagebutton $style{'up'}' type='image' NAME="submit" SRC="$UP_PNG" ALT="%s" />
        <INPUT TYPE="hidden" NAME="ACTION" VALUE="up">
        <INPUT TYPE="hidden" NAME="line" VALUE="$i">
        <img class="clear $style{'clear_up'}" src="$CLEAR_PNG"/>
      </FORM>
      <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left">
        <input class='imagebutton $style{'down'}' type='image' NAME="submit" SRC="$DOWN_PNG" ALT="%s" />
        <INPUT TYPE="hidden" NAME="ACTION" VALUE="down">
        <INPUT TYPE="hidden" NAME="line" VALUE="$i">
        <img class="clear $style{'clear_down'}" src="$CLEAR_PNG"/>
      </FORM>
      <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left">
        <input class='imagebutton' type='image' NAME="submit" SRC="$enabled_gif" ALT="$enabled_alt" />
        <INPUT TYPE="hidden" NAME="ACTION" VALUE="$enabled_action">
        <INPUT TYPE="hidden" NAME="line" VALUE="$i">
      </FORM>
      <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left">
        <input class='imagebutton' type='image' NAME="submit" SRC="$EDIT_PNG" ALT="%s" />
        <INPUT TYPE="hidden" NAME="ACTION" VALUE="edit">
        <INPUT TYPE="hidden" NAME="line" VALUE="$i">
      </FORM>
      <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left" onsubmit="return confirm('确认删除?')">
        <input class='imagebutton' type='image' NAME="submit" SRC="$DELETE_PNG" ALT="%s" />
        <INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
        <INPUT TYPE="hidden" NAME="line" VALUE="$i">
      </FORM>
     </td>
	  </TR>

EOF
                , _('Up')
                , _('Down')
                , _('Edit')
                , _('Delete')
                ;
            }
            $i++;
        }
    }
}
if($i eq 0){
	no_tr(10,_('无内容'));
}
    printf <<EOF
   
</TABLE>
EOF
;

if($i>0)
{
printf <<EOF
<TABLE cellpadding="0" cellspacing="0" class="list-legend">
  <TR>
    <TD CLASS="boldbase">
      <B>%s:</B>

<IMG SRC="$ENABLED_PNG" ALT="%s" />
%s
<IMG SRC='$DISABLED_PNG' ALT="%s" />
%s
<IMG SRC="$EDIT_PNG" alt="%s" />
%s
<IMG SRC="$DELETE_PNG" ALT="%s" />
%s</TD>
  </TR>
</TABLE>
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

sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;

    my %checked;
    $checked{'LOG_ACCEPTS'}{$log_accepts} = 'checked = checked';

    printf <<END
<div class="extra_button" >
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td align="left">
      <form action="/cgi-bin/xtaccess.cgi" method="post"  class="service-switch-form">
	  <br />
        &nbsp;&nbsp;<input name="LOG_ACCEPTS" value="on" type="checkbox" $checked{'LOG_ACCEPTS'}{'on'}>%s&nbsp;&nbsp;
        <input type="hidden" name="ACTION" value="save">
        &nbsp;&nbsp;<input name="save" value="%s" type="submit" class="net_button">
		<br /><br />
      </form>
	  
    </td>
  </tr>
</table>
</div>
<br />
END
, _('Log packets')
, _('Save')
;
    display_add($is_editing, $line);
    generate_rules($xtaccess_config, $is_editing, $line, 1);
	my $sys_length = count_sys_rules(getConfigFiles($inputfwdir), 0, 0, 0);
    if($sys_length>0)
    {
    printf <<EOF

<div class="show_sys" >
<b>%s</b>&nbsp;&nbsp;<b><input onclick="swapVisibility('systemrules')" value=" &gt;&gt; " type="button"></b></div>
EOF
, _('Show rules of system services')
;
	    print "<div id=\"systemrules\" style=\"display: none\">\n";
        generate_rules(getConfigFiles($inputfwdir), 0, 0, 0);

        #&closebox();
        #print "</div>";
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
	$proto =~ s/\n//g;
	$proto =~ s/\r//g;
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
    } else {
    %config = %par;
    }

    my $enabled = $config{'enabled'};
    my $target = $config{'target'};
    if (! $target) {
	#2013-7-27 屏蔽入侵防御后修改默认值
	#2014-5-6 打开入侵防御
    $target = 'ALLOW';
    #$target = 'ACCEPT';
	#
    $enabled = 'on';  # hacky.. i assume if target is not set, default options must be used.
    }
    my $protocol = $config{'protocol'};
    if (! $protocol && !$is_editing) {
    $protocol = 'any';
    }
    my $dst_dev = $config{'dst_dev'};
    if ($dst_dev eq '0.0.0.0' or $dst_dev eq '') {
    $dst_dev = 'ANY';
    }
    my $source = $config{'source'};
    my $port = $config{'port'};
    my $remark = $config{'remark'};

    my $mac = $config{'mac'};
    my $log = $config{'log'};

    $checked{'ENABLED'}{$enabled} = 'checked';
    $checked{'LOG'}{$log} = 'checked';
    $selected{'PROTOCOL'}{$protocol} = 'selected';
    $selected{'TARGET'}{$target} = 'selected';

    foreach my $item (split(/&/, $dst_dev)) {
    $selected{'dst_dev'}{$item} = 'selected';
    }

    $source =~ s/&/\n/gm;
    $mac =~ s/&/\n/gm;
    $port =~ s/&/\n/gm;

    my $line_count = line_count();

    if ("$par{'line'}" eq "") {
        # if no line set last line
        #print "BIO";
        #$line = $line_count -1;
    }

    my $action = 'add';
    my $sure = '';
    my $title = _('Add a system access rule');
	my $addoredit ="添加系统访问规则";
    if ($is_editing) {
		$action = 'edit';
		$sure = '<INPUT TYPE="hidden" NAME="sure" VALUE="y">';
		$title = _('Edit system access rule');
		$addoredit ="修改系统访问规则";
    }

    my $show = "";
	my $addoredit = ($par{'ACTION'} eq 'add' || $par{'ACTION'} eq '' ? "添加规则" : "编辑规则");
    my $button = ($par{'ACTION'} eq 'add' || $par{'ACTION'} eq '' ? _("Add Rule") : "编辑规则");
    if ($is_editing || $errormessage) {
        $show = "showeditor";
    }
    #&openbox('100%', 'left', $title);
    openeditorbox($addoredit, $title, $show, "createrule",);
    printf <<EOF
  
      <!-- begin source/dest -->
		</form>
		<form name="XTACCESS_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
        <!-- begin source -->
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr class="env">
		  <td class="add-div-type" rowspan="1"><b>%s</b></td>
            <td colspan="3">
              <div>%s</div>

EOF
, _('Source address')
, _('Insert network/IPs/MACs (one per line).')
;

##########
# SOURCE #
##########

#### IP begin ###############################################################
    printf <<EOF
              <div>
                <textarea name='source' wrap='off' style="width: 350px; height: 90px;">$source</textarea>
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
		  <td class="add-div-type" rowspan="1"><b>%s</b></td>
            <td colspan="3">
              <div>%s</div>
EOF
, _('Source interface')
, _('Select interfaces (hold CTRL for multiselect)')
;

###############
# DESTINATION #
###############

#### Device begin ###########################################################
    printf <<EOF
              <div>
                <select name="dst_dev" multiple style="width: 350px; height: 90px;">
              <option value="ANY" $selected{'dst_dev'}{'ANY'}>%s</option>
EOF
, _('ANY')
;
    foreach my $item (@nets) {
    printf <<EOF
              <option value="$item" $selected{'dst_dev'}{$item}>%s</option>
EOF
,$strings_zone{$item}
;
    }
    printf <<EOF
              <option value="RED" $selected{'dst_dev'}{'RED'}>%s</option>
EOF
, _('RED')
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

        eval 
            my %ulhash;
            &readhash("${swroot}/uplinks/$name/settings", \%ul);
            foreach my $ipcidr (split(/,/, $ul{'RED_IPS'})) {
                my ($ip) = split(/\//, $ipcidr);
                next if ($ip =~ /^$/);
            }
        }

    foreach my $data (@$devices) {
        my $value = $data->{'portlabel'};
    my $key = "PHYSDEV:".$data->{'device'};
    my $zone = _("Zone: %s", $strings_zone{$data->{'zone'}});
    printf <<EOF
              <option value="$key" $selected{'dst_dev'}{$key}>$value ($zone)</option>
EOF
;
    }
    printf <<EOF
              <option value="VPN:ANY" $selected{'dst_dev'}{'VPN:ANY'}>%s</option>
	      <option value="VPN:IPSEC" $selected{'dst_dev'}{'VPN:IPSEC'}>IPSEC</option>
	<option value="VPN:SERVER" $selected{'dst_dev'}{'VPN:SERVER'}>%s</option>
EOF
, _('VPN')
, _('SSLVPN Server')
;

    foreach my $tap (@{get_taps()}) {
        my $key = "VPN:".$tap->{'name'};
	my $name = $tap->{'name'};
	my $addzone = '';
	if ($tap->{'bridged'}) {
	    my $zone = _("Zone: %s", $strings_zone{$tap->{'zone'}});
	    $addzone = "($zone)";
	}
        printf <<EOF 
                                    <option value='$key' $selected{'dst_dev'}{$key}>%s $name $addzone</option>
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

    printf <<EOF
            </td>
     <!-- end destination -->

      <!-- end source/dest -->
    </tr>
    <tr class="env">
      <td class="add-div-type">
        <b>%s</b></td>
        <td  nowrap="true">%s:&nbsp;
              <select name="service_port" onchange="selectService('protocol', 'service_port', 'port');" onkeyup="selectService('protocol', 'service_port', 'port');">
                <option value="any/any">&lt;%s&gt;</option>
EOF
, _('Service/Port')
, _('Service')
, _('ANY')
;
    my ($sel, $arr) = create_servicelist($protocol, $config{'port'});
    print @$arr;

# check if ports should be enabled
if ($protocol eq "" || $protocol eq "any") {
    $portsdisabled = 'disabled="true"';
}
    printf <<EOF
              </select>
            </td>
            <td style="width:20%">%s:
              <select name="protocol" onchange="updateService('protocol', 'service_port', 'port');" onkeyup="updateService('protocol', 'service_port', 'port');" style="width:168px">
                <option value="any" $selected{'PROTOCOL'}{'any'}>&lt;%s&gt;</option>
                <option value="tcp" $selected{'PROTOCOL'}{'tcp'}>TCP</option>
                <option value="udp" $selected{'PROTOCOL'}{'udp'}>UDP</option>
            <option value="tcp&udp" $selected{'PROTOCOL'}{'tcp&udp'}>TCP + UDP</option>
            <option value="ospf" $selected{'PROTOCOL'}{'ospf'}>OSPF</option>
            <option value="esp" $selected{'PROTOCOL'}{'esp'}>ESP</option>
            <option value="gre" $selected{'PROTOCOL'}{'gre'}>GRE</option>
            <option value="icmp" $selected{'PROTOCOL'}{'icmp'}>ICMP</option>
              </selected>
            </td>
            <td >
EOF
, _('Protocol')
, _('ANY')
;

my $isdisplay = "class='hidden_class'";
if($port ne "")
{
	$isdisplay = "";
}
my $time_enabled = "";
my $time_display = "none";
if($par{'line'} ne '')
{
    my $cur_line = read_config_line($par{'line'});
    @cur_line = split(",",$cur_line);
    if($cur_line[11])
    {
        $time_display = "table";
        $time_enabled = "checked='checked'";
    }
}
printf <<EOF
				<ul  id="port_ul" $isdisplay><li>%s: </li>
                <li><textarea name="port" rows="3" $portsdisabled onkeyup="updateService('protocol', 'service_port', 'port');">$port</textarea></li></ul>
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
      <td class="add-div-type" ><b>%s</b></td>
            <td colspan="3">%s:&nbsp;
              <select name="target" style="width:145px">
				 <option value="ALLOW" $selected{'TARGET'}{'ALLOW'}>%s</option>
                <option value="ACCEPT" $selected{'TARGET'}{'ACCEPT'}>%s</option>
                <option value="DROP" $selected{'TARGET'}{'DROP'}>%s</option>
                <option value="REJECT" $selected{'TARGET'}{'REJECT'}>%s</option>
              </select>
            </td>
    </tr>
	<tr class="env">
            <td class="add-div-type" >
            <b>时间段控制 *</b></td>
            <td colspan="3">
            <input name="TIME_ENABLED" id="time_enabled" type="checkbox"  $time_enabled  onclick ="show_hide('time_enabled','time_control')" >启用
            <span class="note">不勾选则不进行时间过滤(时间段控制范围为开始日期到结束日期，不包含结束日期)</span>
            <table width="100%" style="border:1px solid #999;display:$time_display" id="time_control">
            <tr class="odd">
            <td >

EOF
, _('Policy')
, _('Action')
#, _('入侵防御')
, _('内容过滤')
, _('ALLOW')
, _('DENY')
, _('REJECT')
;
#2013-27 能士项目屏蔽入侵防御
#<option value="ALLOW" $selected{'TARGET'}{'ALLOW'}>%s</option>
#, _('入侵防御')
#2014-5-6 打开入侵防御
my $start_day;
if($config{'start_day'})
{
    $start_day = $config{'start_day'};
}else{
    $start_day = `date "+%Y-%m-%d"`;
}
my $end_day;
if($config{'end_day'})
{
    $end_day = $config{'end_day'};
}else{
    $end_day = `date "+%Y-%m-%d"`;
}


printf <<EOF
             开始日期：<input type="text" SIZE="12" id="startDate" name='START_DAY' value="$start_day" readOnly="readOnly" />
<script type="text/javascript"> 
ESONCalendar.bind("startDate");
</script>  
            </td>
            
            <td colspan="2">
            结束日期：<input type="text" SIZE="12" id="endDate" name='END_DAY' value="$end_day" readOnly="readOnly" />
<script type="text/javascript"> ESONCalendar.bind("endDate");
</script>  
            </td>
            
            </tr>
        
        <tr class="env">
            <td>周:
            <select  id="week" name="WEEK" multiple style="width: 150px; height: 80px;">
EOF
;
if($config{'week'})
{
my @weeks = split(/|/,$config{'week'});
foreach my $day(sort keys %week)
{
    my $key = 0;
    foreach my $week(@weeks)
    {
        if($week eq $day)
        {
            $key = 1;
        }
    }
    if($key)
    {
        print "<option selected = 'selected' value='".$day."'>".$week{$day}."</option>";
    }else{
        print "<option value='".$day."'>".$week{$day}."</option>";
    }
}
}else{
    foreach my $day(sort keys %week)
    {
        print "<option selected = 'selected' value='".$day."'>".$week{$day}."</option>";
    }
}
my @start = split(/:/,$config{'start_hour_min'});
my @end = split(/:/,$config{'end_hour_min'});

printf <<EOF
            </select>

            </td>
            <td>每日起始时间
            <select name="START_HOUR">
EOF
;

foreach my $hour (@day)
{
    if($start[0] eq $hour)
    {
        print "<option selected value='".$hour."'>".$hour."</option>";
    }else{
        print "<option value='".$hour."'>".$hour."</option>";
    }
}
printf <<EOF
            </select>
            时
            <select  name="START_MIN">
EOF
;

foreach my $min (@hour)
{
    if($start[1] eq $min)
    {
        print "<option  selected value='".$min."'>".$min."</option>";
    }else{
        print "<option value='".$min."'>".$min."</option>";
    }
}


printf <<EOF
    </select>
    </td>
    <td >每日结束时间
    <select name="END_HOUR">
EOF
;

foreach my $hour (@day)
{
    #若为0点则$end[0] = 0 需添加||$end[0] eq 0 以判断此情况
    if($end[0]||$end[0] eq 0)
    {
        if($end[0] eq $hour)
        {
            print "<option selected value='".$hour."'>".$hour."</option>";
        }else{
            print "<option value='".$hour."'>".$hour."</option>";
        }
    }else{
        if('23' eq $hour)
        {
            print "<option selected value='".$hour."'>".$hour."</option>";
        }else{
            print "<option value='".$hour."'>".$hour."</option>";
        }
    }
}
printf <<EOF
            </select>时
            <select name="END_MIN">
EOF
;
foreach my $min (@hour)
{
    if($end[1])
    {
    if($end[1] eq $min)
    {
        print "<option  selected value='".$min."'>".$min."</option>";
    }else{
        print "<option  value='".$min."'>".$min."</option>";
    }
    }else{
        if('59' eq $min)
        {
            print "<option  selected value='".$min."'>".$min."</option>";
        }else{
            print "<option  value='".$min."'>".$min."</option>";
        }
    }
}

printf <<EOF
            </select></td>
            
            
            
            </tr>
            </table>
            <SCRIPT>
            function show_hide(id1,id2)
            {
                if(document.getElementById(id1).checked)
                {
                    document.getElementById(id2).style.display = document.all?"block":"table";
                }else{
                    document.getElementById(id2).style.display = "none";
                }
            }
            </SCRIPT>
            </td>
        </tr>
        <tr class ="odd">
            <td class="add-div-type" rowspan="4">%s</td>
            <td colspan="3">%s
                <input name="remark" value="$remark" size="50" maxlength="50" type="text" style="width:148px">
            </td>
        </tr>
        
        <tr class="odd">
            <td colspan="3">%s *&nbsp;
                            <select name="position" style="width:138px">
                                <option value="0">%s</option>
EOF
, _('Other')
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
          <tr class="env">
            <td colspan="3"><input name="enabled" value="on" $checked{'ENABLED'}{'on'} type="checkbox">%s</td>
          </tr>
		  <tr class="odd">
            <td colspan="3"><input name="log" value="on" $checked{'LOG'}{'on'} type="checkbox">%s</td>
          </tr>
        </table>
      </td>
    </tr>
    <input type="hidden" name="ACTION" value="$action">
    <input type="hidden" name="line" value="$line">
    <input type="hidden" name="sure" value="y">
  </table>
EOF
, _('Enabled')
, _('Log all accepted packets')
, _('Save')
;

    &closeeditorbox($button, _("Cancel"), "routebutton", "createrule", "$ENV{'SCRIPT_NAME'}");
    #&closebox();

    # end of ruleedit div
    #print "</div>"

}


sub display_deny() {
    my $is_editing = ($par{'ACTION'} eq 'edit');

    my %selected;
    my %checked;
    $checked{'LOG_ACCEPTS'}{$log_accepts} = 'checked = checked';
    $selected{'POLICY'}{$policy} = 'selected';
    
    #&openbox('100%', 'left', _('Current rules'));

    display_rules($is_editing, $par{'line'});
}

sub reset_values() {
    %par = ();
    $par{'LOG_ACCEPTS'} = $log_accepts;
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    my $log_message="";
    if ($action eq 'apply') {
        system($setxtaccess);		
    	`sudo fcmd $setxtaccess`;
        $notemessage = _("Firewall rules applied successfully");
        $log_message = "应用了系统访问规则";
        &user_log($log_message);
        %par=();
        return;
    }
    if ($action eq 'save') {
        set_policy();
        reset_values();
        $log_message = "修改了系统访问配置";
        &user_log($log_message);
        return;
    }
    if ($action eq 'up') {
        move($par{'line'}, -1);
        my $rule_num = $par{'line'} + 1;
        $log_message = "将第$rule_num条系统访问规则上移1";
        &user_log($log_message);
        reset_values();
        return;
    }
    if ($action eq 'down') {
        move($par{'line'}, 1);
        my $rule_num = $par{'line'} + 1;
        $log_message = "将第$rule_num条系统访问规则下移1";
        &user_log($log_message);
        reset_values();
        return;
    }
    if ($action eq 'delete') {
        delete_line($par{'line'});
        my $rule_num = $par{'line'} + 1;
        $log_message = "删除第$rule_num条系统访问规则";
        &user_log($log_message);    
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
            my $rule_num = $par{'line'} + 1;
            $log_message = "启用第$rule_num条系统访问规则";
            &user_log($log_message);
            reset_values();
            return;
        }
    }
    if ($action eq 'disable') {
        if (toggle_enable($par{'line'}, 0)) {
            my $rule_num = $par{'line'} + 1;
            $log_message = "禁用第$rule_num条系统访问规则";
            &user_log($log_message);
            reset_values();
            return;
        }
    }

 
    # ELSE
    if (($action eq 'add') || (($action eq 'edit')&&($sure eq 'y'))) {
	
        my $act;
        my $rule_num;
        if($action eq 'add'){
            $act = "添加";    
            $rule_num = $par{'position'} + 1;   
        }
        
        if((($action eq 'edit')&&($sure eq 'y'))){   
            $act = "修改";
            $rule_num = $par{'line'} + 1;
        }   
        my $src = '';
        my $mac = '';
        my $dst_dev = '';
        my $old_pos = $par{'line'};

        $src = $par{'source'};
        $dst_dev = $par{'dst_dev'};
        my $start_hour_min = $par{'START_HOUR'}.":".$par{'START_MIN'};
        my $end_hour_min = $par{'END_HOUR'}.":".$par{'END_MIN'};
        if($par{'TIME_ENABLED'} ne "on")
        {
            $par{'START_DAY'} = "";
            $par{'END_DAY'}= "";
            $par{'WEEK'}= "";
            $start_hour_min= "";
            $end_hour_min= "";
        }
        my $enabled = $par{'enabled'};
        #----------------------------------
        #冲突提示代码添加-2013-04-18-squall
        
        #获取格式化的line string
        my $old_line = read_config_line($par{'line'});
		my $current_line = format_line($par{'line'},
                                      $par{'protocol'},
                                      $src,
                                      $par{'port'},
                                      $enabled,
                                      '',
                                      $dst_dev,
                                      $par{'log'},
                                      $par{'target'},
                                      $mac,
                                      $par{'remark'},
                                      $par{'START_DAY'},
                                      $par{'END_DAY'},
                                      $par{'WEEK'},
                                      $start_hour_min,
                                      $end_hour_min);

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
        if (save_line($par{'line'},
                  $par{'protocol'},
                  $src,
                  $par{'port'},
                  $enabled,
                  '',
                  $dst_dev,
                  $par{'log'},
                  $par{'target'},
                  $mac,
                  $par{'remark'},
                  $par{'START_DAY'},
                  $par{'END_DAY'},
                  $par{'WEEK'},
                  $start_hour_min,
                  $end_hour_min
                  )) {

            if ($par{'line'} ne $par{'position'}) {
                    if ("$old_pos" eq "") {
                        $old_pos = line_count()-1;
                    }
                    if (line_count() > 1) {
                        set_position($old_pos, $par{'position'});
                    }
            }
            ####进行对比检测，查看修改的项目

            my $src_value = $src;
            my $dst_value = $dst_dev;
            my $pos = $par{'position'} + 1;
            my $lined = $par{'line'} + 1;
            my $week = $par{'WEEK'},$proto = $par{'protocol'},$remark = $par{'remark'};
            if (!$enabled) {
                $enabled = "off";
            }
            if (!$par{'log'}) {
                $par{'log'} = "off";
            }
            my $times = "$par{'START_DAY'} $start_hour_min -> $par{'END_DAY'} $end_hour_min";
            if ($par{'TIME_ENABLED'} ne "on") {
                $times = "未启用";
                $week = "未启用";
            }
            if ($par{'protocol'} eq "any") {
                $proto ="";
            }            
            if (!$par{'remark'}) {
                $remark ="空";
            }
            my $new_line = "$src_value,$dst_value,$enabled,$proto,$par{'port'},$par{'target'},$remark,$par{'log'},$times,$week,$pos";
            my $message = "源,源接口,启用状态,协议,端口,动作,注释,记录日志,启用时间,周,规则位置";
            if ($action eq 'add') {                
                $log_message = "添加了系统访问规则，";
                $log_message .= build_rule($new_line,$message);
                &user_log($log_message);
            }
            if (($action eq 'edit')&&($sure eq 'y')) {    
                my @tmp = split(/,/,$old_line);
                my $src_value = $tmp[1];  
                my $dst_value = $tmp[5]; 
                my $times =  "$tmp[11] $tmp[13] -> $tmp[12] $tmp[14]";
                my $week = $tmp[15]; 
                $src_value =~s/&/\|/g;
                $dst_value =~s/&/\|/g;
                $tmp[14] =~s/:/\|/g;  
                if (!$tmp[3]) {
                    $tmp[3] = "off";
                }                
                if (!$tmp[10]) {
                    $tmp[10] = "空";
                }
                if (!$tmp[6]) {
                    $tmp[6] = "off";
                }
                if (!$tmp[11]) {
                    $times = "未启用";
                    $week = "未启用";
                }    
                my $old_value = "$src_value,$dst_value,$tmp[3],$tmp[0],$tmp[2],$tmp[8],$tmp[10],$tmp[6],$times,$week,$lined";
                $log_message = "修改了第$lined条系统访问规则，";
                $log_message .= check_change($old_value,$new_line,$message);
                &user_log($log_message);
            }  
            reset_values();
        }
    }
}


sub check_form()
{
#表单检查代码添加-2012-08-30-zhouyuan
printf <<EOF
<script>	
var object = {
       'form_name':'XTACCESS_FORM',
       'option'   :{
                    'remark':{
                               'type':'text',
                               'required':'0',
                               'check':'note|'
                             },
                    'enabled':{
                               'type':'checkbox',
                               'required':'0'
                             },
                    'log':{
                               'type':'checkbox',
                               'required':'0'
                             },
                    'dst_dev':{
                               'type':'select-multiple',
                               'required':'0'
                             },
                    'source':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|ip_mask|mac|'
                             },
                    'port':{
                               'type':'textarea',
                               'required':'0',
                               'check':'port|port_range|'
                             },
                    'START_HOUR':{
                               'type':'select-one',
                               'required':'1',
                               'ass_check':function(eve){
                                                        var msg;
                                                        var start_hour = parseInt(eve._getCURElementsByName("START_HOUR","select","XTACCESS_FORM")[0].value);
                                                        var start_min = parseInt(eve._getCURElementsByName("START_MIN","select","XTACCESS_FORM")[0].value);
                                                        var end_hour = parseInt(eve._getCURElementsByName("END_HOUR","select","XTACCESS_FORM")[0].value);
                                                        var end_min = parseInt(eve._getCURElementsByName("END_MIN","select","XTACCESS_FORM")[0].value);
                                                        if (start_hour > end_hour) {
                                                            msg = "开始时间必须小于结束时间";
                                                        }
                                                        else if (start_hour == end_hour) {
                                                            if (start_min >= end_min) {
                                                                msg = "开始时间必须小于结束时间";
                                                            }
                                                        }
                                                        return msg;
                               }
                             },

                    'END_HOUR':{
                               'type':'select-one',
                               'required':'1',
                               'ass_check':function(eve){
                                                        var msg;
                                                        var start_hour = parseInt(eve._getCURElementsByName("START_HOUR","select","XTACCESS_FORM")[0].value);
                                                        var start_min = parseInt(eve._getCURElementsByName("START_MIN","select","XTACCESS_FORM")[0].value);
                                                        var end_hour = parseInt(eve._getCURElementsByName("END_HOUR","select","XTACCESS_FORM")[0].value);
                                                        var end_min = parseInt(eve._getCURElementsByName("END_MIN","select","XTACCESS_FORM")[0].value);
                                                        if (start_hour > end_hour) {
                                                            msg = "结束时间必须大于开始时间";
                                                        }
                                                        else if (start_hour == end_hour) {
                                                            if (start_min >= end_min) {
                                                                msg = "结束时间必须大于开始时间";
                                                            }
                                                        }
                                                        return msg;
                               }
                             },
                    'START_DAY':{
                               'type':'text',
                               'required':'1',
                               'check':'other',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg;
                                                        var start_day = eve._getCURElementsByName("START_DAY","input","XTACCESS_FORM")[0].value;
                                                        var end_day = eve._getCURElementsByName("END_DAY","input","XTACCESS_FORM")[0].value;
                                                        var reg = /^\\d+-\\d+-\\d+\$/;
                                                        if(!reg.test(start_day)){
                                                            msg = "开始日期格式不正确";
                                                        }
                                                        else{
                                                            var starts = start_day.split("-");
                                                            var ends = end_day.split("-");
                                                            for (i = 0;i < 3;i++) {
                                                                starts[i] = starts[i].replace(/\\b(0+)/gi,"");
                                                                ends[i] = ends[i].replace(/\\b(0+)/gi,"");
                                                                starts[i] = parseInt(starts[i]);
                                                                ends[i] = parseInt(ends[i]);
                                                            }
                                                            if(starts[0] > ends[0]){
                                                                msg = "开始日期必须小于结束日期";
                                                            }
                                                            else if(starts[0] == ends[0]){
                                                                if (starts[1] > ends[1]) {
                                                                    msg = "开始日期必须小于结束日期";
                                                                }
                                                                else if(starts[1] == ends[1]){
                                                                    if (starts[2] >= ends[2]) {
                                                                        msg = "开始日期必须小于结束日期";
                                                                    }
                                                                }
                                                            }
                                                        }
                                                        return msg;
                                }
                             },
                    'END_DAY':{
                               'type':'text',
                               'required':'1',
                               'check':'other',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg;
                                                        var start_day = eve._getCURElementsByName("START_DAY","input","XTACCESS_FORM")[0].value;
                                                        var end_day = eve._getCURElementsByName("END_DAY","input","XTACCESS_FORM")[0].value;
                                                        var reg = /^\\d+-\\d+-\\d+\$/;
                                                        if(!reg.test(end_day)){
                                                            msg = "结束日期格式不正确";
                                                        }
                                                        else{
                                                            var starts = start_day.split("-");
                                                            var ends = end_day.split("-");
                                                            for (i = 0;i < 3;i++) {
                                                                starts[i] = starts[i].replace(/\\b(0+)/gi,"");
                                                                ends[i] = ends[i].replace(/\\b(0+)/gi,"");
                                                                starts[i] = parseInt(starts[i]);
                                                                ends[i] = parseInt(ends[i]);
                                                            }
                                                            if(starts[0] > ends[0]){
                                                                msg = "结束日期必须大于开始日期";
                                                            }
                                                            else if(starts[0] == ends[0]){
                                                                if (starts[1] > ends[1]) {
                                                                    msg = "结束日期必须大于开始日期";
                                                                }
                                                                else if(starts[1] == ends[1]){
                                                                    if (starts[2] >= ends[2]) {
                                                                        msg = "结束日期必须大于开始日期";
                                                                    }
                                                                }
                                                            }
                                                        }
                                                        return msg;
                                }
                             }
                 }
         } 
var check = new  ChinArk_forms();
check._main(object);
//check._get_form_obj_table("XTACCESS_FORM");
</script>
EOF
;
}

&getcgihash(\%par);
$log_accepts = $xtaccess{'LOG_ACCEPTS'};

&showhttpheaders();
my $extraheader = '<script language="JavaScript" src="/include/services_selector.js"></script>
<script type="text/javascript" src="/include/conflict_detection.js"></script>
<script type="text/javascript" src="/include/ESONCalendar.js"></script>';
&openpage(_('System access'), 1, $extraheader);

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
    applybox(_("Firewall rules have been changed and need to be applied in order to make the changes active"));
}

display_deny();
&check_form();
&closebigbox();
&closepage();
