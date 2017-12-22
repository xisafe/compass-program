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

my $zonefw_config = "${swroot}/zonefw6/config";
my $zonefw_settings = "${swroot}/zonefw6/settings";
my $zonefw_default_settings = "${swroot}/zonefw6/default/settings";
my $ethernet_settings = "${swroot}/ethernet/settings";
my $setzonefw = "/usr/local/bin/setzonefw6";
my $zonefwdir = '/etc/firewall/zonefw/';
my $needreload = "${swroot}/zonefw6/needreload";

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


my (%par,%checked,%selected,%ether,%zonefw);
my $errormessage = '';
my $policy = 'DENY';
my $log_accepts = 'off';
my @nets;
my $reload = 0;
my %zonefwhash=();
my $zonefw = \%zonefwhash;

my $devices, $deviceshash = 0;

my $services_file = '/var/efw/zonefw/services';
my $services_custom_file = '/var/efw/zonefw/services.custom';

&readhash($ethernet_settings, \%ether);

if (-e $zonefw_default_settings) {
    &readhash($zonefw_default_settings, \%zonefw);
}
if (-e $zonefw_settings) {
    &readhash($zonefw_settings, \%zonefw);
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
    if (($policy ne $par{'POLICY'}) || 
    ($log_accepts ne $par{'LOG_ACCEPTS'})
    ) {
        if ($par{'POLICY'} eq "off") {
            $policy = "ALLOW";
			my @cur_user=&getCurUser();
	        my $input_user=$cur_user[0];
	        system("/usr/bin/logger","-p","daemon.notice","-t","userLog-$input_user","成功关闭IPV6防火墙");
			
        }
        else {
            $policy = "DENY";
			my @cur_user=&getCurUser();
	        my $input_user=$cur_user[0];
	        system("/usr/bin/logger","-p","daemon.notice","-t","userLog-$input_user","成功打开IPV6防火墙");
        }
        $log_accepts = $par{'LOG_ACCEPTS'};
        open(FILE,">$zonefw_settings") or die "Unable to open config file '$zonefw_settings' because $!.";
        print FILE "POLICY=$policy\n";
        print FILE "LOG_ACCEPTS=$log_accepts\n";
        close FILE;
		`sudo fmodify $zonefw_settings`;
    }
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
    my @lines = read_config_file($zonefw_config);
    return $lines[$line];
}

sub save_config_file_back($) {
    my $ref = shift;
    my @lines = @$ref;
    open (FILE, ">$zonefw_config");
    foreach my $line (@lines) {
        if ($line ne "") {
        print FILE "$line\n";
        }
    }
    close(FILE);
	`sudo fmodify $zonefw_config`;
    $reload = 1;
}

sub line_count() {
    open (FILE, "$zonefw_config") || return 0;
    my $i = 0;
    foreach (<FILE>) {
    $i++;
    }
    close FILE;
    return $i;
}

sub append_config_file($) {
    my $line = shift;
    open (FILE, ">>$zonefw_config");
    print FILE $line."\n";
    close FILE;
	`sudo fmodify $zonefw_config`;
    $reload = 1;
}

sub is_valid($) {
    my $line = shift;
    if ($line =~ /(?:(?:[^,]*),){10}/) {
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
    $config{'enabled'} = $temp[0];
    $config{'protocol'} = $temp[1];
    $config{'source'} = $temp[2];
    $config{'destination'} = $temp[3];
    $config{'port'} = $temp[4];
    $config{'target'} = $temp[5];
    $config{'mac'} = $temp[6];
    $config{'remark'} = $temp[7];
    $config{'log'} = $temp[8];
    $config{'src_dev'} = $temp[9];
    $config{'dst_dev'} = $temp[10];
    $config{'valid'} = 1;

    return %config;
}

sub toggle_enable($$) {
    my $line = shift;
    my $enable = shift;
    if ($enable) {
    $enable = 'on';
    } else {
    $enable = 'off';
    }

    my %data = config_line(read_config_line($line));
    $data{'enabled'} = $enable;

    return save_line($line,
             $data{'enabled'},
             $data{'protocol'},
             $data{'source'},
             $data{'destination'},
             $data{'port'},
             $data{'target'},
             $data{'mac'},
             $data{'remark'},
             $data{'log'},
             $data{'src_dev'},
             $data{'dst_dev'});
}

sub move($$) {
    my $line = shift;
    my $direction = shift;
    my $newline = $line + $direction;
    if ($newline < 0) {
    return;
    }
    my @lines = read_config_file($zonefw_config);

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
    my @lines = read_config_file($zonefw_config);
    my $myline = $lines[$old];
    my @newlines = ();

    # nothing to do
    if ($new == $old) {
    return;
    }
   
    if ($new > $#lines+1) {
        $new = $#lines+1;
    }

    open (FILE, ">$zonefw_config");

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
	`sudo fmodify $zonefw_config`;
    close(FILE);
}

sub delete_line($) {
    my $line = shift;
    my @lines = read_config_file($zonefw_config);
    if (! @lines[$line]) {
    return;
    }
    delete (@lines[$line]);
    save_config_file_back(\@lines);
}

sub create_line($$$$$$$$$$$) {

    my $enabled = shift;
    my $protocol = shift;
    my $source = shift;
    my $dest = shift;
    my $port = shift;
    my $target = shift;
    my $mac = shift;
    my $remark = shift;
    my $log = shift;
    my $src_dev = shift;
    my $dst_dev = shift;

    return "$enabled,$protocol,$source,$dest,$port,$target,$mac,$remark,$log,$src_dev,$dst_dev";
}

sub check_values($$$$$$$$$$) {
    my $enabled = shift;
    my $protocol = shift;
    my $source = shift;
    my $dest = shift;
    my $port = shift;
    my $target = shift;
    my $mac = shift;
    my $log = shift;
    my $src_dev = shift;
    my $dst_dev = shift;

    my %valid_proto = ('TCP' => 1, 'UDP' => 1, 'TCP&UDP' => 1, 'ESP' => 1, 'GRE' => 1, 'ICMP' => 1, 'ETHER' => 1);
    my %valid_targets = ( 'ACCEPT' => 1, 'ALLOW' => 1, 'DROP' => 1, 'REJECT' => 1 );

    if ($protocol !~ /^$/) {
        if (! $valid_proto{uc($protocol)}) {
         push(@errormessages, _('Invalid protocol'));
        }
    }
=p
    foreach my $item (split(/&/, $source)) {
    if (! is_ipaddress($item)) {
         push(@errormessages, _('Invalid source IP address "%s"', $item));
    }
    }

    foreach my $item (split(/&/, $dest)) {
    if (!is_ipaddress($item)) {
         push(@errormessages, _('Invalid destination IP address "%s"', $item));
    }
    }
=cut
    foreach my $item (split(/&/, $mac)) {
    if (!validmac($item)) {
         push(@errormessages, _('Invalid MAC address "%s"', $item));
    }
    }

    foreach my $ports (split(/&/, $port)) {
        if ($ports !~ /^(\d{1,5})(?:\:(\d{1,5}))?$/) {
         push(@errormessages, _('Invalid destination port "%s"', $ports));
    }
    my $port1 = $1;
    my $port2 = '65535';
    if ($2) {
        $port2 = $2;
    }

    if (($port1 < 0) || ($port1 > 65535)) {
            push(@errormessages, _('Invalid destination port "%s"', $port1));
    }

    if (($port2 < 0) || ($port2 > 65535)) {
         push(@errormessages,  _('Invalid destination port "%s"', $port2));
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

sub save_line($$$$$$$$$$$$) {
    my $line = shift;
    my $enabled = shift;
    my $protocol = shift;
    my $source = shift;
    my $dest = shift;
    my $port = shift;
    my $target = shift;
    my $mac = shift;
    my $remark = shift;
    my $log = shift;
    my $src_dev = shift;
    my $dst_dev = shift;

    $source =~ s/\n/&/gm;
    $source =~ s/\r//gm;
    $dest =~ s/\n/&/gm;
    $dest =~ s/\r//gm;
    $port =~ s/\n/&/gm;
    $port =~ s/\r//gm;
    $port =~ s/\-/:/g;
    $mac =~ s/\n/&/gm;
    $mac =~ s/\r//gm;
    $mac =~ s/\-/:/g;
    $remark =~ s/\,//g;

    $src_dev =~ s/\|/&/g;
    $dst_dev =~ s/\|/&/g;
    $source =~ s/\|/&/g;
    $dest =~ s/\|/&/g;

    if ($source =~ /none/) {
        $source = '';
    }
    if ($dest =~ /none/) {
        $dest = '';
    }

    if ($src_dev =~ /ALL/) {
        $src_dev = 'ALL';
    }
    if ($dst_dev =~ /ALL/) {
        $dst_dev = 'ALL';
    }
    if ($src_dev =~ /none/) {
        $src_dev = '';
    }
    if ($dst_dev =~ /none/) {
        $dst_dev = '';
    }

    if ($source !~ /^$/) {
        $src_dev = '';
    }
    if ($dest !~ /^$/) {
        $dst_dev = '';
    }
    if ($mac !~ /^$/) {
        $source = '';
        $src_dev = '';
    }

    if ($port =~ /any/) {
       $port = '';
    }
    if ($protocol =~ /any/) {
        $protocol = '';
    }

    if ($protocol eq 'icmp') {
        $port = '8&30';
    }

    if (! check_values($enabled, $protocol, $source, $dest, $port, $target, $mac, $log, $src_dev, $dst_dev)) {
    return 0;
    }

    my $tosave = create_line($enabled, $protocol, $source, $dest, $port, $target, $mac, $remark, $log, $src_dev, $dst_dev);

    if ($line !~ /^\d+$/) {
    append_config_file($tosave);
    return 1;
    }
    my @lines = read_config_file($zonefw_config);
    if (! $lines[$line]) {
    $errormessage = _('Configuration line not found!');
    return 0;
    }

    my %split = config_line($lines[$line]);
    if (($split{'enabled'} ne $enabled) ||
    ($split{'protocol'} ne $protocol) ||
    ($split{'source'} ne $source) ||
    ($split{'destination'} ne $dest) ||
    ($split{'port'} ne $port) ||
    ($split{'target'} ne $target) ||
    ($split{'mac'} ne $mac) ||
    ($split{'log'} ne $log) ||
    ($split{'src_dev'} ne $src_dev) ||
    ($split{'dst_dev'} ne $dst_dev) ||
    ($split{'remark'} ne $remark)) {
    $lines[$line] = $tosave;
    save_config_file_back(\@lines);
    }
    return 1;
}

sub generate_addressing($$$$) {
    my $addr = shift;
    my $dev = shift;
    my $mac = shift;
    my $rulenr = shift;

    my @addr_values = ();

    foreach my $item (split(/&/, $addr)) {
      push(@addr_values, $item);
    }
    foreach my $item (split(/&/, $dev)) {
        if ($item =~ /^PHYSDEV:(.*)$/) {
            my $device = $1;
            my $data = $deviceshash->{$device};

          push(@addr_values, "<font color='". $zonecolors{$data->{'zone'}} ."'>".$data->{'portlabel'}."</font>");
        } else {
          push(@addr_values, "<font color='". $zonecolors{$item} ."'>".$strings_zone{$item}."</font>");
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
           
sub get_all_eth()
{
	my $temp_cmd = `ip a`;
	my %all_hash;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
		{
			$all_hash{$1} = $1;
		}
	}
	return %all_hash;
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

	my %all_eth = get_all_eth();
	
    printf <<END
<table class="ruleslist" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td class="boldbase" align="center" width="2%">
      <b>#</b>
    </td>
    <td class="boldbase" align="center" width="15%">
      <b>%s</b>
    </td>
    <td class="boldbase" align="center" width="15%">
      <b>%s</b>
    </td>

    <td class="boldbase" align="center" width="12%">
      <b>%s</b>
    </td>

    <td class="boldbase" align="center" width="10%">
      <b>%s</b>
    </td>
    <td class="boldbase" align="center" width="22%">
      <b>%s</b>
    </td>

END
, _('Source')
, _('Destination')
, _('Service')
, _('Policy')
, _('Remark')
;

    if ($editable) {
        printf <<END
        <td class="boldbase" align="center" width="18%">%s</td>
END
        , _('Actions')
        ;
    }
    printf <<END
    </tr>
END
    ;

    my $i = 0;
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
            my $destination = $splitted{'destination'};
            my $dst_dev = $splitted{'dst_dev'};
            my $src_dev = $splitted{'src_dev'};
            my $port = $splitted{'port'};

            my $target = $splitted{'target'};
            my $policy_gif = $IPS_PNG;
            my $policy_alt = _('ALLOW with IPS');
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

            my $log = '';
            if ($splitted{'log'} eq 'on') {
                $log = _('yes');
            }
            my $mac = $splitted{'mac'};

            my $bgcolor = setbgcolor($is_editing, $line, $i);
            my $dest_long_value = '';
			
			$dest_long_value = generate_addressing($destination, $dst_dev, '', $i);
            if ($dest_long_value =~ /(?:^|&)ANY/) {
                $dest_long_value = "&lt;"._('ANY')."&gt;";
            }
			
			my $src_long_value = "";
			
				$src_long_value = generate_addressing($source, $src_dev, $mac, $i);
				if ($src_long_value =~ /(?:^|&)ANY/) {
					$src_long_value = "&lt;"._('ANY')."&gt;";
				}
			
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


            printf <<EOF
  <tr>
    <TD VALIGN="top" ALIGN="center">$num</TD>
    <TD VALIGN="top">$src_long_value</TD>
    <TD VALIGN="top">$dest_long_value</TD>
    <TD VALIGN="top">$service_long_value</TD>
    <TD VALIGN="top" ALIGN="center">
      <IMG SRC="$policy_gif" ALT="$policy_alt" TITLE="$policy_alt">
    </TD>
    <TD VALIGN="top" >$remark</TD>
EOF
            ;

            if ($editable) {
                printf <<EOF
    <TD class="actions" VALIGN="top" ALIGN="center" nowrap="nowrap">
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
      <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left" onsubmit="confirm('确定要删除此规则？')">
        <input class='imagebutton' type='image' NAME="submit" SRC="$DELETE_PNG" ALT="%s" />
        <INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
        <INPUT TYPE="hidden" NAME="line" VALUE="$i">
      </FORM>
    </TD>

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
    printf <<EOF
    </TR>
EOF
;
if($i eq 0)
{
	no_tr(7,"无内容");
}
printf <<EOF
</TABLE>
EOF
;
if($i>0)
{
printf <<EOF
<table class="list-legend" cellpadding="0" cellspacing="0">
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
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')
;
}
}

sub display_switch() {
    my %checked;

    $checked{'LOG_ACCEPTS'}{$log_accepts} = 'checked = checked';
   
    my $is_editing = 0;
    if ($par{'ACTION'} eq 'edit') {
        $is_editing = 1;
    }
    if ($is_editing ne 1 && $#errormessages ne -1) {
        $is_editing = 1;
    }
    
    printf <<END
    <div class="service-switch">
    <script type="text/javascript">
        \$(document).ready(function() {
            var SERVICE_STAT_DESCRIPTION = {'on' : "%s", 'off' : "%s", 'restart' : "%s"};
            var sswitch = new ServiceSwitch('/cgi-bin/ipv6fw.cgi', SERVICE_STAT_DESCRIPTION);
        });
    </script>

    <form enctype='multipart/form-data' class="service-switch-form" id="ssh-form" method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" class="service-status" name="POLICY" value="$service_satus" />

    <table cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td v>
                <div id="access-policy" class="service-switch">
                    <div><span class="title">%s</span>
                        <span class="image"><img class="$service_status" align="absbottom" src="/images/switch-$service_status.png" alt="" border="0"/></span>
                    </div>
                    
                        <div id="access-description" class="description %s">%s</div>
                        <div id="access-policy-hold" class="spinner working">%s</div>
                        <div id="access-options" class="options-container %s">
                            <div class="divider"><img src="/images/clear.gif" width="1" height="1" alt="" border="0" /></div>
                            <div class="options">
                                <p><input class="checkbox" type='checkbox' name='LOG_ACCEPTS' $checked{'LOG_ACCEPTS'}{'on'} /> <span class="cb-caption">%s</span></p>
                            </div>
                            <div class="save-button">
                                <input class='submitbutton save-button net_button' type='submit' name='ACTIONBUTTON' value='%s' />
                            </div>
                        
                    </div>
                </div>
            </td>
        </tr>
    </table>
        <input type='hidden' name='ACTION' value='save' />
    </form>
	<div class="options-container %s">
END
    ,
    escape_quotes(_("正在激活IPV6访问控制,请稍候...")),
    escape_quotes(_("正在关闭IPV6访问控制,请稍候...")),
    escape_quotes(_("正在应用IPV6访问控制,请稍候...")),
    _('IPV6访问控制'),
    $service_status eq 'on' ? 'hidden' : '',
    _("使用上面的开关来开启IPV6访问控制."),
    _("正在关闭IPV6访问控制,请稍候..."),
    $service_status eq 'off' ? 'hidden' : '',
    _('记录允许的IPV6连接'),
    _('Save'),
	$service_status eq 'off' ? 'hidden' : '',
    ;
 display_rules($is_editing, $par{'line'});
print "</div></div>";
}


sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;

    my %checked;
    $checked{'LOG_ACCEPTS'}{$log_accepts} = 'checked = checked';

    #&openbox('100%', 'left', _('Current rules'));
    display_add($is_editing, $line);
    generate_rules($zonefw_config, $is_editing, $line, 1);
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
    $target = 'ALLOW';
    $enabled = 'on';  # hacky.. i assume if target is not set, default options must be used.
    }
    my $protocol = $config{'protocol'};
    if (! $protocol && !$is_editing) {
    $protocol = 'any';
    }
    my $src_dev = $config{'src_dev'};
    my $dst_dev = $config{'dst_dev'};
    my $source = $config{'source'};
    my $source_ip = '';
    my $source_user = '';
    my $destination = $config{'destination'};
    my $destination_ip = '';
    my $destination_user = '';
    my $port = $config{'port'};
    my $remark = $config{'remark'};

    my $mac = $config{'mac'};
    my $log = $config{'log'};
    my $src_type = 'ip';
    my $dst_type = 'dev';

    $checked{'ENABLED'}{$enabled} = 'checked';
    $checked{'LOG'}{$log} = 'checked';
    $selected{'POLICY'}{$policy} = 'selected';
    $selected{'PROTOCOL'}{$protocol} = 'selected';
    $selected{'TARGET'}{$target} = 'selected';
    if ($source =~ /^$/) {
        foreach my $item (split(/&/, $src_dev)) {
            $selected{'src_dev'}{$item} = 'selected';
        }
        if ($src_dev !~ /^$/) {
            $src_type = 'dev';
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

    if ($source !~ /^$/) {
        $source_ip = $source;
        if ($source_ip !~ /^$/) {
            $src_type = 'ip';
        }
    }
    if ($destination !~ /^$/) {
        $destination_ip = $destination;
        if ($destination_ip !~ /^$/) {
            $dst_type = 'ip';
        }
    }
    if ($mac !~ /^$/) {
        $src_type = 'mac';
    }
    if ($is_editing) {
        if (($source =~ /^$/) && ($src_dev =~ /^$/) &&! ($mac !~ /^$/)) {
            $src_type = 'any';
        }
        if (($destination =~ /^$/) && ($dst_dev =~ /^$/)) {
            $dst_type = 'any';
        }
    }

    $selected{'src_type'}{$src_type} = 'selected';
    $selected{'dst_type'}{$dst_type} = 'selected';

    my %foil = ();
    $foil{'title'}{'src_any'} = 'none';
    $foil{'title'}{'src_dev'} = 'none';
    $foil{'title'}{'src_ip'} = 'none';
    $foil{'title'}{'src_mac'} = 'none';
    $foil{'value'}{'src_any'} = 'none';
    $foil{'value'}{'src_dev'} = 'none';
    $foil{'value'}{'src_ip'} = 'none';
    $foil{'value'}{'src_mac'} = 'none';

    $foil{'title'}{'dst_any'} = 'none';
    $foil{'title'}{'dst_dev'} = 'none';
    $foil{'title'}{'dst_ip'} = 'none';
    $foil{'value'}{'dst_any'} = 'none';
    $foil{'value'}{'dst_dev'} = 'none';
    $foil{'value'}{'dst_ip'} = 'none';

    $foil{'title'}{"src_$src_type"} = 'block';
    $foil{'value'}{"src_$src_type"} = 'block';
    $foil{'title'}{"dst_$dst_type"} = 'block';
    $foil{'value'}{"dst_$dst_type"} = 'block';

    $source_ip =~ s/&/\n/gm;
    $destination_ip =~ s/&/\n/gm;
    $mac =~ s/&/\n/gm;
    $port =~ s/&/\n/gm;

    my $line_count = line_count();

    if ("$par{'line'}" eq "") {
        # if no line set last line
        #print "BIO";
        #$line = $line_count -1;
    }

    my $src_dev_size = int((length(%$deviceshash) + $#nets) / 3);
    if ($src_dev_size < 3) {
       $src_dev_size = 3;
    }
    my $dst_dev_size = $src_dev_size;

    my $action = 'add';
    my $sure = '';
    my $title = _('Add zone firewall rule');
	my $addoredit = "新建IPV6访问控制规则";
    if ($is_editing) {
		$action = 'edit';
		$sure = '<INPUT TYPE="hidden" NAME="sure" VALUE="y">';
		$title = _('Edit zone firewall rule');
		$addoredit = "编辑IPV6访问控制规则";
    }

    my $show = "";
    my $button = ($par{'ACTION'} eq 'add' || $par{'ACTION'} eq '' ? _("Add Rule") : _("Update Rule"));
    if ($is_editing) {
        $show = "showeditor";
        # print "<div id=\"ruleedit\" style=\"display: block\">\n";
    }
    
    openeditorbox($addoredit, $title, $show, "createrule",);
    #&openbox('100%', 'left', $title);
    printf <<EOF
        <!-- begin source -->
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr class="env">
		  <td class="add-div-type" rowspan="1"><b>%s</b></td>
            <td>%s * &nbsp;&nbsp;
              <select name="src_type" onchange="toggleTypes('src');" onkeyup="toggleTypes('src');">
                <option value="any" $selected{'src_type'}{'any'}>&lt;%s&gt;</option>
                <option value="dev" $selected{'src_type'}{'dev'}>%s</option>
                <option value="ip" $selected{'src_type'}{'ip'}>%s</option>
                <option value="mac" $selected{'src_type'}{'mac'}>%s</option>
              </select>
            </td>

            <td colspan = "2">
              <div id="src_any_t" style="display:$foil{'title'}{'src_any'}">%s</div>
              <div id="src_dev_t" style="display:$foil{'title'}{'src_dev'}">%s:</div>
              <div id="src_ip_t" style="display:$foil{'title'}{'src_ip'}">%s:</div>
              <div id="src_mac_t" style="display:$foil{'title'}{'src_mac'}">%s:</div>

              <div id="src_any_v" style="display:$foil{'value'}{'src_any'}" style="width: 250px; height: 90px;">&nbsp;</div>

EOF
, _('Source')
, _('Type')
, _('ANY')
, _('Zone/Interface')
, _('IPV6')
, _('MAC')

, _('This rule will match any destination')
, _('Select interfaces (hold CTRL for multiselect)')
, _('插入IPV6地址(每行一个)')
, _('Insert MAC Addresses (one per line)')
;

##########
# SOURCE #
##########

#### Device begin ###########################################################
    printf <<EOF
              <div id='src_dev_v' style='display:$foil{'value'}{'src_dev'}'>
                <select name="src_dev" multiple style="width: 250px; height: 90px;">
EOF
;
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
                </select>
              </div>
EOF
;
#### Device end #############################################################

#### IP begin ###############################################################
    printf <<EOF
              <div id='src_ip_v' style='display:$foil{'value'}{'src_ip'}'>
                <textarea name='source' wrap='off' style="width: 250px; height: 90px;">$source_ip</textarea>
              </div>
EOF
;
#### IP end #################################################################

#### MAC begin ##############################################################
    printf <<EOF
              <div id='src_mac_v' style='display:$foil{'value'}{'src_mac'}'>
                <textarea name='mac' wrap='off' style="width: 250px; height: 90px;">$mac</textarea>
              </div>
EOF
;
#### MAC end ################################################################

    printf <<EOF
            </td>
          </tr>

        <!-- end source field -->
 
        <!-- begin destination -->
        
       
          <tr class="odd">
		  <td class="add-div-type" rowspan="1"><b>%s</b></td>
            <td>%s *&nbsp;&nbsp;
              <select name="dst_type" onchange="toggleTypes('dst');" onkeyup="toggleTypes('dst');">
                <option value="any" $selected{'dst_type'}{'any'}>&lt;%s&gt;</option>
                <option value="dev" $selected{'dst_type'}{'dev'}>%s</option>
                <option value="ip" $selected{'dst_type'}{'ip'}>%s</option>
              </select>
            </td>
         
            <td colspan = "2">
              <div id="dst_any_t" style="display:$foil{'title'}{'dst_any'}">%s</div>
              <div id="dst_dev_t" style="display:$foil{'title'}{'dst_dev'}">%s:</div>
              <div id="dst_ip_t" style="display:$foil{'title'}{'dst_ip'}">%s:</div>

              <div id="dst_any_v" style="display:$foil{'value'}{'src_any'}" style="width: 250px; height: 90px;">&nbsp;</div>

EOF
, _('Destination')
, _('Type')
, _('ANY')
, _('Zone/Interface')
, _('IPV6')
, _('This rule will match any source')
, _('Select interfaces (hold CTRL for multiselect)')
, _('插入IPV6(每行一个)')
;

###############
# DESTINATION #
###############

#### Device begin ###########################################################
    printf <<EOF
              <div id='dst_dev_v' style='display:$foil{'title'}{'dst_dev'}' style="width: 250px; height: 90px;">
                <select name="dst_dev" multiple style="width: 250px; height: 90px;">
EOF
;
    foreach my $item (@nets) {
    printf <<EOF
              <option value="$item" $selected{'dst_dev'}{$item}>%s</option>
EOF
,$strings_zone{$item}
;
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

    printf <<EOF
            </td>
          </tr>
        
        <!-- end destination -->

      <!-- end source/dest -->

    <tr class="env">
        <td class="add-div-type" rowspan="1">
        <b>%s</b>
	    </td>
        <td >%s *
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
if ($protocol eq "" || $protocol eq "any" ||$protocol eq "icmp") {
    $portsdisabled = 'disabled="true"';
}
    printf <<EOF
              </select>
            </td>
            <td >%s *
              <select name="protocol" onchange="updateService('protocol', 'service_port', 'port');" onkeyup="updateService('protocol', 'service_port', 'port');">
                <option value="any" $selected{'PROTOCOL'}{'any'}>&lt;%s&gt;</option>
                <option value="tcp" $selected{'PROTOCOL'}{'tcp'}>TCP</option>
                <option value="udp" $selected{'PROTOCOL'}{'udp'}>UDP</option>
            <option value="tcp&udp" $selected{'PROTOCOL'}{'tcp&udp'}>TCP + UDP</option>
            <option value="esp" $selected{'PROTOCOL'}{'esp'}>ESP</option>
            <option value="gre" $selected{'PROTOCOL'}{'gre'}>GRE</option>
            <option value="icmp" $selected{'PROTOCOL'}{'icmp'}>ICMP</option>
            <option value="ether" $selected{'PROTOCOL'}{'ether'}>ETHER</option>
              </selected>
            </td>
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
            <td>
			  <ul id="port_ul" $isdisplay><li>%s</li>
              <li><textarea name="port" rows="3" $portsdisabled onkeyup="updateService('protocol', 'service_port', 'port');">$port</textarea></li>
			  </ul>
EOF
, _('Destination port (one per line)')
;

printf <<EOF
				<ul id="port_ul2" ><li>%s</li></ul>
EOF
,_('This rule will match all the destination ports')
;

printf <<EOF
            </td>
          </tr>
        
    <tr class="odd">
      <td class="add-div-type" rowspan="1">
        <b>%s</b></td>
            <td colspan=3">%s *&nbsp;
              <select name="target">
                <option value="ACCEPT" $selected{'TARGET'}{'ACCEPT'}>%s</option>
                <option value="DROP" $selected{'TARGET'}{'DROP'}>%s</option>
                <option value="REJECT" $selected{'TARGET'}{'REJECT'}>%s</option>
              </select>
            </td>
    </tr>
	<tr class="env">
			<td class="add-div-type" rowspan="4">%s</td>
            <td colspan="3">%s
              <input name="remark" value="$remark" size="50" maxlength="50" type="text">
            </td>
    </tr>
	<tr class="env">
            <td colspan="3">%s *&nbsp;
              <select name="position">
                <option value="0">%s</option>
EOF
, _('Policy')
, _('Action')
, _('ALLOW')
, _('DENY')
, _('REJECT')
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
	
	<tr class="env">
            <td colspan="3"><input name="log" value="on" $checked{'LOG'}{'on'} type="checkbox">%s</td>
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

    &closeeditorbox($button, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

    # end of ruleedit div
    #print "</div>"

}

sub reset_values() {
    %par = ();
    $par{'POLICY'} = $policy;
    $par{'LOG_ACCEPTS'} = $log_accepts;
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    if ($action eq 'apply') {
        system($setzonefw);	
		system("rm $needreload");
		`sudo fcmd $setzonefw`;
        $notemessage = _("Firewall rules applied successfully");
        return;
    }
    if ($action eq 'save') {
        set_policy();
        reset_values();
        system($setzonefw);		
		`sudo fcmd $setzonefw`;
		
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
	my @cur_user=&getCurUser();
    my $input_user=$cur_user[0];
	system("/usr/bin/logger","-p","daemon.notice","-t","userLog-$input_user","用户成功删除了一条IPV6访问控制规则");		
    reset_values();
    return;
    }

    if ($action eq 'enable') {
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
	if($action eq 'add')
	{
	    my @cur_user=&getCurUser();
        my $input_user=$cur_user[0];
	    system("/usr/bin/logger","-p","daemon.notice","-t","userLog-$input_user","用户成功添加了一条IPV6访问控制规则");		
	
	}
	
	if((($action eq 'edit')&&($sure eq 'y')))
	{
	    my @cur_user=&getCurUser();
        my $input_user=$cur_user[0];
	    system("/usr/bin/logger","-p","daemon.notice","-t","userLog-$input_user","用户成功修改了一条IPV6访问控制规则");		
	
	}
	

    my $src_type = $par{'src_type'};
    my $dst_type = $par{'dst_type'};

        my $src = '';
        my $mac = '';
        my $dst = '';
        my $src_dev = '';
        my $dst_dev = '';
        my $old_pos = $par{'line'};

        if ($src_type eq 'ip') {
            $src = $par{'source'};
        }
        if ($dst_type eq 'ip') {
            $dst = $par{'destination'};
        }
        if ($src_type eq 'dev') {
            $src_dev = $par{'src_dev'};
        }
        if ($dst_type eq 'dev') {
            $dst_dev = $par{'dst_dev'};
        }
        if ($src_type eq 'mac') {
            $mac = $par{'mac'};
        }

    my $enabled = $par{'enabled'};
    if (save_line($par{'line'},
              $enabled,
              $par{'protocol'},
              $src,
              $dst,
              $par{'port'},
              $par{'target'},
              $mac,
              $par{'remark'},
              $par{'log'},
              $src_dev,
              $dst_dev
              )) {

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
    }
}

&getcgihash(\%par);
$policy = $zonefw{'POLICY'};
if ($policy eq "ALLOW") {
    $service_status = "off";
}
else {
    $service_status = "on";
}
$log_accepts = $zonefw{'LOG_ACCEPTS'};

&showhttpheaders();
my $extraheader = '<script language="JavaScript" src="/include/firewall_type.js"></script>
<script language="JavaScript" src="/include/services_selector.js"></script>
<script type="text/javascript" src="/include/serviceswitch.js"></script>';

&openpage(_('Zone firewall'), 1, $extraheader);

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
    printf <<END
    <div class="service-switch"><div class="options-container %s">
END
    ,
    $service_status eq 'off' ? 'hidden' : '',
    ;

    applybox(_("Firewall rules have been changed and need to be applied in order to make the changes active"));

    print "</div></div>";
}

display_switch();

&closebigbox();
&closepage();
