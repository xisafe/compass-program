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
require 'list_panel_opt.pl';
require 'ethconfig.pl';
require 'qos_ethernet.pl';
require 'simple_conflict_detection.pl';
my $QOS_config = "${swroot}/shaping/config";
my $ethernet_settings = "${swroot}/ethernet/settings";
my $setincoming = "/usr/local/bin/setincoming";
my $needreload = "${swroot}/shaping/needreload";
my $app_file = '/var/efw/objects/application/app_system';#应用配置文件路径
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
my $show = "";
my $temp = &ethname();
my %ethname = %$temp;

my $userlist           = '/usr/local/bin/getGroupUserTree.py';#获取用户组数据python文件路径
my $applist            = '/usr/local/bin/application_get_tree.py -s';#获取应用数据PYthon文件路径
my $userlistObj        = `sudo $userlist`;
my $applistObj         = `sudo $applist`;
my (%par,%checked,%selected,%ether,%Qos);
my @errormessages = ();
my @nets;
my $reload = 0;
my %QOShash=();
my $Qos = \%QOShash;

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

my %ifacesdata = ();
my $ifacesdata = \%ifacesdata;

my $services_file = '/var/efw/shaping/services';
my @dst;
my @dst_class;
my @dst_devices;
my %dst_br0_config;
my $allTos = "style='display:none;'";
my $twoTos ="style='display:none;'";
my $thirdTos = "style='display:none;'";
my $fourTos = "style='display:none;'";
my %tos_tos =(
    '0' => ' 请选择',
	'1' => 'Minimize-Delay',
	'2' => 'Maximize-Throughput',
	'3' => 'Maximize-Reliability',
	'4' => 'Minimize-Cost',
	'5' => 'Normal-Service',
	);

my %dscp_class =(
    '00' => '请选择',
	'01' => 'BE default dscp (000000)',
	'02' => 'AF11 dscp (001010)',
	'03' => 'AF12 dscp (001100)',
	'04' => 'AF13 dscp (001110)',
	'05' => 'AF21 dscp (010010)',
	'06' => 'AF22 dscp (010100)',
	'07' => 'AF23 dscp (010110)',
	'08' => 'AF31 dscp (011010)',
	'09' => 'AF32 dscp (011100)',
	'10' => 'AF33 dscp (011110)',
	'11' => 'AF41 dscp (100010)',
	'12' => 'AF42 dscp (100100)',
	'13' => 'AF43 dscp (100110)',
	'14' => 'CS1(precedence 1) dscp (001000)',
	'15' => 'CS2(precedence 2) dscp (010000)',
	'16' => 'CS3(precedence 3) dscp (011000)',
	'17' => 'CS4(precedence 4) dscp (100000)',
	'18' => 'CS5(precedence 5) dscp (101000)',
	'19' => 'CS6(precedence 6) dscp (110000)',
	'20' => 'CS7(precedence 7) dscp (111000)',
	'21' => 'EF dscp (101110)',
    );
				
				
&readhash($ethernet_settings, \%ether);

sub check_form(){
    printf <<EOF
    <script>
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("RULE_FORM");
    </script>
EOF
;
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



sub readclass()
{
    my @lines = read_conf_file("/var/efw/shaping/classes");
    my @rules = read_conf_file("/var/efw/shaping/config");
    my $length = @lines;
    my $rules_lenght = @rules;
    for(my $i=0;$i<$length;$i++)
    {
        my @linestemp = split(',', $lines[$i]);
        my $device = $linestemp[0];
        my $class_name = $linestemp[1];
        @dst[$i] = $linestemp[3];
        @dst_class[$i] = $class_name;
        @dst_devices[$i] = $device;
        if($device eq 'GREEN'){
            %dst_br0_config->{$class_name} = 1;
            %dst_br0_config->{$class_name."sharecount"} = 0;
            for(my $j = 0; $j < $rules_lenght; $j++) {
                my @temp = split(",", $rules[$j]);
                if($temp[0] eq $class_name) {
                    %dst_br0_config->{$class_name}++;#对相同类名进行计数
                    #==根据$temp[14]来判断当前规则配置的是共享还是独占,为空表示共享
                    my $policy = "share";
                    if($temp[14] ne "") {
                        $policy = $temp[14];
                    }
                    %dst_br0_config->{$class_name."policy"} = $policy;
                    %dst_br0_config->{$class_name.$policy."count"}++;
                }
            }
            if(%dst_br0_config->{$class_name} > 1) {
                %dst_br0_config->{$class_name}--;#多进行了一次计数
            }
        }
    }
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


sub read_config_file($) {
    #print "enter read";
    my $filename = shift;
    my @lines;
    open (FILE, "<$filename");
    foreach my $line(<FILE>) {
    chomp($line);
    #print $line;
    $line =~ s/[\r\n]//g;
    #if (!is_valid($line)) {
    #    next;
    #}
    #print $line;
    push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub read_config_line($) {
    my $line = shift;
    my @lines = read_config_file($QOS_config);
    return $lines[$line];
}

sub save_config_file_back($) {
    my $ref = shift;
    my @lines = @$ref;
    open (FILE, ">$QOS_config");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
	`sudo fmodify $QOS_config`;
    $reload = 1;
}

sub line_count() {
    open (FILE, "$QOS_config") || return 0;
    my $i = 0;
    foreach (<FILE>) {
        $i++;
    }
    close FILE;
    return $i;
}

sub append_config_file($) {
    my $line = shift;
	my @lines = read_config_file($QOS_config);
    my @saves;
	if (@lines < 1) {
		push(@saves,$line);
	}
	else{
		for (my $num=0;$num<@lines;$num++) {
			if ($num < $par{'position'}) {
				push(@saves,$lines[$num]);
			}
			else{
				push(@tail,$lines[$num]);
			}
		}
		push(@saves,$line);
		foreach my $elem (@tail) {
			push(@saves,$elem);
		}
	}
	save_config_file_back(\@saves);
}

sub edit_config_file($) {
    my $line = shift;
	my @lines = read_config_file($QOS_config);
	delete $lines[$par{'line'}];
	save_config_file_back(\@lines);
	append_config_file($line);
}

sub is_valid($) {
    my $line = shift;
    if ($line =~ /(?:(?:[^,]*),){11}/) {
        return 1;
    }
    return 0;
}

sub config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    #if (! is_valid($line)) {
    #   return;
    #}
    my @temp = split(/,/, $line);
	$config{'dst_dev'} = $temp[0];
    $config{'enabled'} = $temp[1];
	$config{'note'} = $temp[2];
    $config{'protocol'} = $temp[3];
    $config{'src_ip'} = $temp[4];
	$config{'src_dev'} = $temp[5];
	$config{'mac'} = $temp[6];
	$config{'know'} = $temp[7];
    $config{'dst_ip'} = $temp[8];
    $config{'port'} = $temp[9];
    $config{'tos'} = $temp[10];
    # modified by squall:
    $config{'dscp_value'} = $temp[11];
    $config{'dscp_class'} = $temp[12];
    $config{'policy'} = $temp[14];
	$config{'limit'} = $temp[15];
    $config{'datestart'} = $temp[16];
    $config{'datestop'} = $temp[17];
    $config{'start_hour_min'} = $temp[18];
    $config{'end_hour_min'} = $temp[19];
    $config{'weekdays'} = $temp[20];
    $config{'SrcUserlistId'} = $temp[21];
    $config{'DesUserlistId'} = $temp[22];
    $config{'AppnameList'} = $temp[23];

    # end
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
					 $data{'dst_dev'},
                     $data{'enabled'},
					 $data{'note'},
                     $data{'protocol'},
                     $data{'src_ip'},
                     $data{'src_dev'},
					 $data{'mac'},
					 $data{'know'},
                     $data{'dst_ip'},
                     $data{'port'},
                     $data{'tos'},
					 $data{'dscp_class'},
					 $data{'dscp_value'},
                     $data{'policy'},
                     $data{'limit'},
                    $data{'datestart'},
                    $data{'datestop'},
                    $data{'start_hour_min'},
                    $data{'end_hour_min'},
                    $data{'weekdays'},
                    $data{'SrcUserlistId'},
                    $data{'DesUserlistId'},
                    $data{'AppnameList'}
					 )

}

sub move($$) {
    my $line = shift;
    my $direction = shift;
    my $newline = $line + $direction;
    if ($newline < 0) {
        return;
    }
    my @lines = read_config_file($QOS_config);

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
    my @lines = read_config_file($QOS_config);
    my $myline = $lines[$old];
    my @newlines = ();

    # nothing to do
    if ($new == $old) {
        return;
    }
   
    if ($new > $#lines+1) {
        $new = $#lines+1;
    }

    open (FILE, ">$QOS_config");

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
	`sudo fmodify $QOS_config`;
    close(FILE);
}

sub delete_line($) {
    my $line = shift;
    my @lines = read_config_file($QOS_config);
    if (! @lines[$line]) {
        return;
    }
    delete (@lines[$line]);
    save_config_file_back(\@lines);
}

sub create_line($$$$$$$$$$$$$$$$$$$$$$$) {

    my $dst_dev = shift;
    my $enabled = shift;
	my $note = shift;
    my $protocol = shift;
	my $src_ip = shift;
    my $src_dev = shift;
	my $mac = shift;
	my $know = shift;
    my $dst_ip = shift;
    my $port = shift;
	my $tos = shift;
	my $dscp_class = shift;
	my $dscp_value = shift;
	my $newone = '';
    my $policy = shift;
    my $limit = shift;
    my $datestart =shift;
    my $datestop =shift;
    my $start_hour_min=shift;
    my $end_hour_min=shift;
    my $weekdays=shift;
    my $SrcUserlistId=shift;
    my $DesUserlistId=shift;
    my $AppnameList=shift;
    #return "$dst_dev,$enabled,$note,$protocol,$src_ip,$src_dev,$mac,$know,$dst_ip,$port,$tos,$dscp_class,$dscp_value,$newone";
    #modified by squall:
    $dscp_class =~ /(\w+)/;
    $dscp_class = $1;
    return "$dst_dev,$enabled,$note,$protocol,$src_ip,$src_dev,$mac,$know,$dst_ip,$port,$tos,$dscp_value,$dscp_class,$newone,$policy,$limit,$datestart,$datestop,$start_hour_min,$end_hour_min,$weekdays,$SrcUserlistId,$DesUserlistId,$AppnameList";
}

sub check_values($$$$$$$$$$$$$) {

    my $dst_dev = shift;
    my $enabled = shift;
	my $note = shift;
    my $protocol = shift;
    my $src_ip = shift;
    my $src_dev = shift;
    my $mac = shift;
	my $know = shift;
    my $dst_ip = shift;
    my $port = shift;
	my $tos = shift;
	my $dscp_class = shift;
	my $dscp_value = shift;

    my %valid_proto = ('TCP' => 1, 'UDP' => 1, 'TCP&UDP' => 1, 'ESP' => 1, 'GRE' => 1, 'ICMP' => 1);
	if ($mac) {
		foreach my $item (split(/&/, $mac)) {
			if (!validmac($item)) {
				push(@errormessages, _('无效的源MAC地址 "%s"', $item));
				return 0;
			}
		}
	}
	if($src_ip ne "")
	{
    foreach my $item (split(/&/, $src_ip)) {
        if (! is_ipaddress($item) && ! validiprange($item)) {
            push(@errormessages, _('无效的源ip地址 "%s"', $item));
			return 0;
        }
    }
	}
	

    foreach my $item (split(/&/, $dst_ip)) {
        if (!is_ipaddress($item) && ! validiprange($item)) {
            push(@errormessages, _('无效的目的IP地址 "%s"', $item));
        }
    }
	foreach my $ports (split(/&/, $port)) {
        if ($ports !~ /^(\d{1,5})(?:\:(\d{1,5}))?$/) {
            push(@errormessages, _('无效的目的端口 "%s"', $ports));
        }
        my $port1 = $1;
        my $port2 = '65535';
        if ($2) {
            $port2 = $2;
        }
    
        if (($port1 < 0) || ($port1 > 65535)) {
            push(@errormessages, _('无效的目的端口 "%s"', $port1));
        }

        if (($port2 < 0) || ($port2 > 65535)) {
            push(@errormessages, _('无效的目的端口 "%s"', $port2));
        }
        if ($port1 > $port2) {
            push(@errormessages, _('目的端口的第一个值应该小于第二个值.'));
			return 0;
        }
    }
    if ($prot !~ /^$/) {
        if (! $valid_proto{uc($protocol)}) {
            push(@errormessages, _('无效的协议'));
        }
    }
    
	if($par{'tos_type'} eq 'dscp_class'){
		if($dscp_class eq "请选择"){
		  push(@errormessages, _('请选择一个dscp标志流量.'));
		}
	}
	elsif($par{'tos_type'} eq 'dscp_value'){
		if($dscp_value !~ /^\d+$/){
		  push(@errormessages, _('dscp值格式错误.'));
		}
	}
	elsif($par{'tos_type'} eq 'tos'){
		if($tos eq "0"){
		  push(@errormessages, _('请选择一个tos标志流量.'));
		}
	}
    if ($#errormessages ne -1) {
        return 0;
    }
    
    return 1;
}

sub get_father_limit($) {
    my $dev_class = shift;
    my @classes = read_conf_file("/var/efw/shaping/classes");
    my @devices = read_conf_file("/var/efw/shaping/devices");

    my $father_limit = 0;
    my $father_limit_perctg = 0;

    foreach my $class ( @classes ) {
        my @class_info = split( ",", $class );
        if ( $class_info[1] eq $dev_class ) {
            $father_limit_perctg = $class_info[5];#限制百分比
            foreach my $device ( @devices ) {
                my @device_info = split( ",", $device );
                if( $device_info[0] eq $class_info[0]) {
                    $father_limit = $device_info[2];#上行带宽
                    last;
                }
            }
            last;
        }
    }
    if( $father_limit_perctg =~ /^(\d+)%$/ ) {
        $father_limit_perctg = $1;
    }

    return int( $father_limit * $father_limit_perctg / 100 * 0.96 );
}

sub is_same_network($) {
    my $ips_line = shift;
    my @ips = split( /-/, $ips_line );
    my $length = @ips;
    if ( $length < 2 ) {
        return 1;
    } else {
        my @first_ips = split( /\./, $ips[0] );
        my @second_ips = split( /\./, $ips[1] );
        if ( $first_ips[0] eq $second_ips[0] && $first_ips[1] eq $second_ips[1] && $first_ips[2] eq $second_ips[2] ) {
            return 1;
        } else {
            return 0;
        }
    }
}

sub is_ip_mark($) {
    my $ips_line = shift;
    my @ips = split( /\//, $ips_line );
    my $length = @ips;
    if ( $length >= 2 ) {
        return 1;
    } else {
        return 0;
    }
}

#
# DESCRIPTION: 
# @param:      页面传入的基础信息
# @return:     格式化的line string
#
# sub format_line($$$$$$$$$$$$$$$$$$) {
#     my $line = shift;
#     my $enabled = shift;
#     my $protocol = shift;
#     my $source = shift;
#     my $dest = shift;
#     my $port = shift;
#     my $dst = shift;
#     my $mac = shift;
    
    
    
#     my $remark = shift;
#     my $log = shift;
#     my $src_dev = shift;
#     my $dst_dev = shift;
    
#     my $ret_string = "";
    
    
#     ##-----------------------------
#     #包过滤添加字段 2012-02-28 周圆
#     my $start_day = shift;
#     my $end_day = shift;
#     my $week = shift;
#     $week =~ s/\|/:/g;
    
#     my $start_hour_min = shift;
#     my $end_hour_min = shift;
#     ##------------------------------
#     my $src_port = shift;

#     $source =~ s/\n/&/gm;
#     $source =~ s/\r//gm;
#     $dest =~ s/\n/&/gm;
#     $dest =~ s/\r//gm;
#     $port =~ s/\n/&/gm;
#     $port =~ s/\r//gm;
#     $port =~ s/\-/:/g;
#     $mac =~ s/\n/&/gm;
#     $mac =~ s/\r//gm;
#     $mac =~ s/\-/:/g;
#     $remark =~ s/\,//g;

#     $src_dev =~ s/\|/&/g;
#     $dst_dev =~ s/\|/&/g;
#     $source =~ s/\|/&/g;
#     $dest =~ s/\|/&/g;
#     $src_port =~ s/\n/&/gm;
#     $src_port =~ s/\r//gm;
#     $src_port =~ s/\-/:/g;

#     if ($source =~ /none/) {
#         $source = '';
#     }
#     if ($dest =~ /none/) {
#         $dest = '';
#     }

#     if ($src_dev =~ /ALL/) {
#         $src_dev = 'ALL';
#     }
#     if ($dst_dev =~ /ALL/) {
#         $dst_dev = 'ALL';
#     }
#     if ($src_dev =~ /none/) {
#         $src_dev = '';
#     }
#     if ($dst_dev =~ /none/) {
#         $dst_dev = '';
#     }

#     if ($source !~ /^$/) {
#         $src_dev = '';
#     }
#     if ($dest !~ /^$/) {
#         $dst_dev = '';
#     }
#     if ($mac !~ /^$/) {
#         $source = '';
#         $src_dev = '';
#     }

#     if ($port =~ /any/) {
#        $port = '';
#     }
#     if ($protocol =~ /any/) {
#         $protocol = '';
#     }

#     if ($protocol eq 'icmp') {
#         $port = '8&30';
#     }
#     if (! check_values($enabled, $protocol, $source, $dest, $port, $dst, $mac,$log, $src_dev, $dst_dev,$start_hour_min,$end_hour_min,$start_day,$end_day)) {
#         return "";
#     }
#     $start_day = format_date($start_day);
#     $end_day = format_date($end_day);
#     #未选择时间则保存为空
#     if ($start_day eq '-0-0') 
#     {
#         $start_day = '';
           
#     }
#     if($end_day eq '-0-0')
#     {
#        $end_day = '';
#     }
    
#     $ret_string = create_line($enabled, $protocol, $source, $dest, $port, $dst, $mac, $remark, $log, $src_dev, $dst_dev,$src_port,$start_day,$end_day,$start_hour_min,$end_hour_min,$week);
    
#     return $ret_string;
# }
sub save_line($$$$$$$$$$$$$$$$$$$$$$$$) {

    my $line = shift;
	my $dst_dev = shift;
    my $enabled = shift;
	my $note = shift;
    my $protocol = shift;
    my $src_ip = shift;
    my $src_dev = shift;
	my $mac = shift;
	my $know = shift;
    my $dst_ip = shift;
    my $port = shift;
	my $tos = shift;
	my $dscp_class = shift;
	my $dscp_value = shift;
    my $policy = shift;
    my $limit = shift;

    my $datestart       = shift;
    my $datestop      = shift;
    my $start_hour_min = shift;
    my $end_hour_min  = shift;
    my $weekdays   = shift;
    my $SrcUserlistId   = shift;
    my $DesUserlistId   = shift;
    my $AppnameList     = shift; 

    $src_ip =~ s/\n/&/gm;
    $src_ip =~ s/\r//gm;
    $dst_ip =~ s/\n/&/gm;
    $dst_ip =~ s/\r//gm;
    $port =~ s/\n/&/gm;
    $port =~ s/\r//gm;
    $port =~ s/\-/:/g;
	$mac =~ s/\n/&/gm;
    $mac =~ s/\r//gm;
    $mac =~ s/\-/:/g;
    $src_dev =~ s/\|/&/g;
    $dst_dev =~ s/\|/&/g;
    $prot =~ s/\+/&/g;
    $src_ip = delete_same_data($src_ip);
    $dst_ip = delete_same_data($dst_ip);
    $mac = delete_same_data($mac);
    chomp($datestart); 
    chomp($datestop); 
    chomp($start_hour_min); 
    chomp($end_hour_min);
    chomp($weekdays); 
    if ($src_ip =~ /none/) {
        $src_ip = '';
    }
    if ($dst_ip =~ /none/) {
        $dst_ip = '';
    }

    if ($src_dev =~ /ALL/) {
        $src_dev = 'ALL';
    }
    if ($mac =~ /ALL/) {
        $mac = 'ALL';
    }
    if ($src_dev =~ /none/) {
        $src_dev = '';
    }
    if ($dst_dev =~ /none/) {
        $dst_dev = '';
    }
    if ($mac !~ /^$/) {
        $src_dev = '';
    }

    if ($port =~ /any/) {
        $port = '';
    }
    if ($prot =~ /any/) {
        $prot = '';
    }

    if ($prot eq 'icmp') {
        $port = '8&30';
    }

    #===判断带宽策略为什么，如果为独占，目标网络不能为任意===#
    #===by wanglin 2014.04.21================================#
    if($policy eq 'exclusive') {
        if($dst_ip eq '') {
            push(@errormessages, "独占带宽策略下,目标网络/IP不能为空!");
            return 0;
        }
    }
    #===end==================================================#

    #===如果带宽策略为独占，不能输入IP/MARK形式地址==========#
    #===by wanglin 2014.05.04================================#
    if($policy eq 'exclusive') {
        my @ip_rangs = split( /&/, $dst_ip );
        foreach my $ip_rang ( @ip_rangs ) {
            if( &is_ip_mark( $ip_rang ) ) {
                push(@errormessages, "独占带宽策略下,目标网络/IP不能填入IP/掩码形式地址!");
                return 0;
            }
        }
    }
    #===end==================================================#

    #===如果带宽策略为独占，不能输入跨网段地址===============#
    #===by wanglin 2014.05.04================================#
    if($policy eq 'exclusive') {
        my @ip_rangs = split( /&/, $dst_ip );
        foreach my $ip_rang ( @ip_rangs ) {
            if( ! &is_same_network( $ip_rang ) ) {
                push(@errormessages, "独占带宽策略下,目标网络/IP不能跨网段!");
                return 0;
            }
        }
    }
    #===end==================================================#

    #===如果带宽策略为独占，最大带宽不能大于父类的限制带宽===#
    #===by wanglin 2014.05.04================================#
    if($policy eq 'exclusive') {
        my $father_limit = &get_father_limit($dst_dev);
        if($limit > $father_limit) {
            push(@errormessages, "独占最大宽策不能大于父类限制带宽($father_limit kbit/s)!");
            return 0;
        }
    }
    #===end==================================================#

    if (! check_values(
	      $dst_dev,$enabled,$note,$protocol, 
	      $src_ip, $src_dev,$mac,$know,
	      $dst_ip,$port,$tos,$dscp_class,$dscp_value)
		) {
        return 0;
    }
	if($enabled eq '')
	{
	
	  $enabled = 'off';
	}
	if($tos =~ /请选择/)
	{
		$tos = "";
	}
	if($dscp_class =~ /请选择/)
	{
		$dscp_class = "";
	}

    my $tosave = create_line($dst_dev,$enabled,$note,$protocol,$src_ip,$src_dev,$mac,$know,$dst_ip,$port,$tos,$dscp_class,$dscp_value,$policy,$limit,$datestart,$datestop, $start_hour_min,$end_hour_min,$weekdays,$SrcUserlistId,$DesUserlistId,$AppnameList);

    if ($line !~ /^\d+$/) {
        append_config_file($tosave);
        return 1;
    }
	if ($par{'ACTION'} eq "edit") {
		edit_config_file($tosave);
		return 1;
	}
    my @lines = read_config_file($QOS_config);
	
	if (! $lines[$line]) {
        push(@errormessages, _('没有找到配置文件!'));
        return 0;
    }
	
    my %split = config_line($lines[$line]);
    if (($split{'dst_dev'} ne $dst_dev) ||
	        ($split{'enabled'} ne $enabled) ||
	        ($split{'note'} ne $note) ||
            ($split{'protocol'} ne $protocol) ||
            ($split{'src_dev'} ne $src_dev) ||
			($split{'src_ip'} ne $src_ip) ||
			($split{'mac'} ne $mac)||
			($split{'know'} ne $know)||
            ($split{'dst_ip'} ne $dst_ip) ||
            ($split{'port'} ne $port) ||
            ($split{'tos'} ne $tos)||
			($split{'dscp_class'} ne $dscp_class)||
			($split{'dscp_value'} ne $dscp_value)){
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
        }
        elsif ($item =~ /^UPLINK:(.*)$/) {
            my $ul = get_uplink_label($1);
            push(@addr_values, "<font color='". $zonecolors{'RED'} ."'>"._('Uplink')." ".$ul->{'name'}."</font>");
        }
        else {
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

sub generate_service($$$$) {
    my $ports = shift;
    my $protocol = shift;
    my $rulenr = shift;
    my $AppnameList = shift;
    $protocol = lc($protocol);
    my $display_protocol = $protocol;
    my @service_values = ();

    if ($protocol eq 'tcp+udp') {
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
    if (($#service_values == -1) && ($AppnameList eq '')) {
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


#通过Appid查询得到Appname
sub get_appName($) {
    my $AppnameList = shift;
    if($AppnameList){
        my @appid  = split("&",$AppnameList);
        my @lines;
        my @appname;
        my ( $status,$mesg ) = &read_config_lines( $app_file,\@lines );
        for( my $i=0; $i < @appid; $i++) {
            
            for( my $i2=0; $i2<@lines; $i2++ ) {
                
                my @line_data = split(",",$lines[$i2]); 
                if( $appid[$i] == $line_data[0] ) {
                    push( @appname,$line_data[2] ); 

                }
            }
        }
        return join ",", @appname;  
    }else{
        return "";
    }
   
}

sub getConfigFiles($) {
    my $dir = shift;
    my @arr = ();
    foreach my $f (glob("${dir}/*.conf")) {
    push(@arr, $f);
    }
    return \@arr;
}

sub generate_rules($$$$) 
{
    my $refconf = shift;
    my $is_editing = shift;
    my $line = shift;
    my $editable = shift;
	my $visible = "style='display: display;float:right;'";
	my $tipVisible = "style='display: display;width:185px;height:60px;margin:80px auto auto auto;'";
    my $line_count = line_count();
	
    my @configs = ();
    if (ref($refconf) eq 'ARRAY') {
        @configs = @$refconf;
    }
    else {
        push(@configs, $refconf);
    }
	
	
    printf <<END
    <table class="ruleslist" cellpadding="0" cellspacing="0" width="100%"  >
	<tr>
            <td class="boldbase" width="10%">%s</td>
            <td class="boldbase" width="10%">%s</td>
            <td class="boldbase" width="5%">%s</td>
            <td class="boldbase" width="10%">%s</td>
            <td class="boldbase" width="10%">%s</td>
            <td class="boldbase" width="5%">注释</td>
            <td class="boldbase" width="5%">时间段</td>
            <td class="boldbase" width="5%">每周</td>
            <td class="boldbase" width="10%">每天时间段</td>
            <td class="boldbase" width="10%">%s</td>
			<td class="boldbase" width="10%">%s</td>
END
    , _('源')
    , _('目标')
    , _('协议')
    , _('服务')
    , _('应用')    
	, _('流量类型')
    , _('TOS/DSCP')
    ;
	
	###7-4周圆)
    if ($editable) {
        printf <<END
        <td class="boldbase" width="10%">%s</td>
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

            #if (! $splitted{'valid'}) {
            #   next;
            #}
            
            # $config{'dst_dev'} = $temp[0];
            # $config{'enabled'} = $temp[1];
            # $config{'note'} = $temp[2];
            # $config{'protocol'} = $temp[3];
            # $config{'src_ip'} = $temp[4];
            # $config{'src_dev'} = $temp[5];
            # $config{'mac'} = $temp[6];
            # $config{'know'} = $temp[7];
            # $config{'dst_ip'} = $temp[8];
            # $config{'port'} = $temp[9];
            # $config{'tos'} = $temp[10];
            # # modified by squall:
            # $config{'dscp_value'} = $temp[11];
            # $config{'dscp_class'} = $temp[12];
            # $config{'policy'} = $temp[14];
            # $config{'limit'} = $temp[15];
            # $config{'datestart'} = $temp[16];
            # $config{'datestop'} = $temp[17];
            # $config{'start_hour_min'} = $temp[18];
            # $config{'end_hour_min'} = $temp[19];
            # $config{'weekdays'} = $temp[20];
            # $config{'SrcUserlistId'} = $temp[21];
            # $config{'DesUserlistId'} = $temp[22];
            # $config{'AppnameList'} = $temp[23];
            my $note = $splitted{'note'};
            my $AppnameList = $splitted{'AppnameList'};
            my $protocol = $splitted{'protocol'};
            my $src_ip = $splitted{'src_ip'};
            my $SrcUserlistId = $splitted{'SrcUserlistId'};
            my $num = $i+1;
            my $enabled_gif = $DISABLED_PNG;
            my $enabled_alt = _('Disabled (click to enable)');
            my $enabled_action = 'enable';
            if ($splitted{'enabled'} eq 'on') {
                $enabled_gif = $ENABLED_PNG;
                $enabled_alt = _('Enabled (click to disable)');
                $enabled_action = 'disable';
            }
            my $dst_ip = $splitted{'dst_ip'};
            my $DesUserlistId = $splitted{'DesUserlistId'};
            my $dst_dev = $splitted{'dst_dev'};
            my $policy = $splitted{'policy'};
            my $limit = $splitted{'limit'};
            my $src_dev = $splitted{'src_dev'};
            my $port = $splitted{'port'};
            my $mac = $splitted{'mac'};
			my $tos = $splitted{'tos'};
			my $dscp_class = $splitted{'dscp_class'};
			my $dscp_value = $splitted{'dscp_value'};
            my $bgcolor = setbgcolor($is_editing, $line, $i);
            my $src_long_value = $src_ip.$src_dev.$mac.$SrcUserlistId;
            my $dst_long_value = $dst_ip.$DesUserlistId;
			my $dst =$dst_dev."  ".$dst_ip;
            if ($src_long_value =~ /(?:^|&)ANY/) {
                $src_long_value = "&lt;"._('ANY')."&gt;";
            }
            if($dst_long_value =~ /(?:^|&)ANY/){
                $dst_long_value = "&lt;"._('ANY')."&gt;";
            }
####zhangzheng1-13修改tos/dscp只显示dscpclass的bug
           my $dscp_tos = $tos.$dscp_class.$dscp_value;
###zhangzheng_end


#=============================#
# added by 文虎先
# for 显示对应的流量类型
# 2011.01.04
#=============================#


            my @lines_tmp;
            my $conf = '/var/efw/shaping/classes';
            open (FILE, "<$conf");
            foreach my $line_tmp (<FILE>) {
                chomp($line_tmp);
                $line_tmp =~ s/[\r\n]//g;
                push(@lines_tmp, $line_tmp);
            }
            close (FILE);
	        my $length = @lines_tmp;
	        my $n;
            my $dst_dev_tmp;
            for($n=0;$n<$length;$n++)
	         {
	            my @linestemp = split(',', $lines_tmp[$n]);
	            if( $dst_dev eq $linestemp[1])
		        {
		            $dst_dev_tmp = $linestemp[3];
		        }
	        }

            #====判断是否独占====#
            #===2014.03.26 by wl=#
            if($policy eq "exclusive") {
                my $append_text = '<span class="exclusive"> (独占) </span>';
                $dst_dev_tmp = $dst_dev_tmp.$append_text;
            }

#=============================#
#end added by 文虎先
#=============================#


            my $service_long_value = generate_service($port, $protocol, $i,$AppnameList);
            my $service_new = "";
            if ($service_long_value =~ /(?:^|&)ANY/ ) {
                $service_long_value = "&lt;"._('ANY')."&gt;";
            }
            if($AppnameList){

                my @service_temp = split(":",$AppnameList);
                foreach my $app_id (@service_temp){
                    $app_id =~ s/:/&/g;
                     my $appNames = &get_appName($app_id);
                    $service_new .= "<li>".$appNames."</li>";
                }
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
			if(!$protocol && !$AppnameList){
			   $protocol = "任意";
			}
			if(!$src_long_value){
			   $src_long_value = "任意";
			}
			if(!$dst_ip){
			   $dst_ip = "任意";
			}
            if($dscp_tos eq "0"){
               $dscp_tos = "0";
            }
			elsif(!$dscp_tos){
			   $dscp_tos = "任意";
			}
			if(!$port && !$AppnameList){
			   $port = "任意";
			}
			
			my @temp_src = split(/&/,$src_long_value);
			my $src_new ="";
			foreach my $src_t(@temp_src){
				if (is_ipaddress($src_t) || validmac($src_t) || validiprange($src_t) || $src_t) {
					$src_new .= "<li>".$src_t."</li>";
				}else{$src_new .= "<li>".$ethname{$src_t}."</li>";}
			}
			if ($src_new eq "<li></li>") {
				$src_new = "任意";
			}
            my $dst_new ="";
            foreach my $dst_t(split(/&/,$dst_long_value)){
                $dst_new .= "<li>".$dst_t."</li>";
            }
            if ($dst_new eq "") {
                $dst_new = "任意";
            }
            printf <<EOF
        <tr class="$bgcolor">
            <td VALIGN="top"><ul>$src_new</ul></td>
            <td VALIGN="top">$dst_new</td>
            <td VALIGN="top">$protocol</td>
            <td VALIGN="top">$port</td>
            <td VALIGN="top">$service_new</td>
            <td VALIGN="top" title="$note">$note</td>
EOF
;
if($splitted{'datestart'} && $splitted{'datestop'})
{
printf <<EOF
            <td><b> $splitted{'datestart'}</b> 至 <b> $splitted{'datestop'}</b></td>
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
    if($splitted{'weekdays'})
    {
    my @weeks = split(":",$splitted{'weekdays'});
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
            <td VALIGN="top" ALIGN="center">$dst_dev_tmp</td>
            <td VALIGN="top" >$dscp_tos</td>
EOF
            ;

            if ($editable) {
                printf <<EOF
            <td VALIGN="top" class="actions">    
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                    <input class="imagebutton $style{'up'}" type='image' NAME="submit" SRC="$UP_PNG" ALT="%s" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="up">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$i">
                    <img class="clear $style{'clear_up'}" src="$CLEAR_PNG"/>
                </form>
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                    <input class="imagebutton $style{'down'}" type='image' NAME="submit" SRC="$DOWN_PNG" ALT="%s" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="down">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$i">
                    <img class="clear $style{'clear_down'}" src="$CLEAR_PNG"/>
                </form>
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                    <input class='imagebutton' type='image' NAME="submit" SRC="$enabled_gif" ALT="$enabled_alt" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="$enabled_action">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$i">
                </form>
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                    <input class='imagebutton' type='image' NAME="submit" SRC="$EDIT_PNG" ALT="%s" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="edit">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$i">
                </form>
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left" onsubmit="return confirm('确认删除?');">
                    <input class='imagebutton' type='image' NAME="submit" SRC="$DELETE_PNG" ALT="%s" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$i">
                </form>
            </td>

EOF
            ,_("Up")
            ,_("Down")
            , _('Edit')
            , _('Delete')
            ;
        }
        $i++;
        }
    }
 printf <<EOF
        </tr>
    
EOF
,
;

###7-4周圆（	
	if($line_count == 0)
	{
		no_tr(12,"无内容");
    }
	###7-4周圆）
	print "</table>";

	if($line_count != 0)
	{	
	printf <<EOF
<table class="list-legend" cellpadding="0" cellspacing="0">
<tr>
<td CLASS="boldbase"><b>%s</b>
<IMG SRC="$EDIT_PNG" alt="%s" />
%s
<IMG SRC="$DELETE_PNG" ALT="%s" />
%s
<IMG SRC="/images/stock_down-16.png" alt="%s"/>
%s
<IMG SRC="/images/stock_up-16.png" alt="%s"/>
%s
<IMG SRC="/images/on.png" alt="%s"/>
%s
<IMG SRC="/images/off.png" alt="%s"/>
%s
 </tr>
</table>
EOF
,
_('Legend'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
_('上移'),
_('上移'),
_('下移'),
_('下移'),
_('启用'),
_('启用'),
_('禁用'),
_('禁用')
;
}
}

sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;
    printf<<EOF
    <div id="SrcUserlist_panel" class="container"></div>
    <div id="DesUserlist_panel" class="container"></div>
    <div id="Appid_panel" class="container"></div>
    <div id="mesg_box" class="container"></div>
EOF
;
    display_add($is_editing, $line);
	generate_rules($QOS_config,$is_editing, $line, 1);  
} 
sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;
    my %config;
    my %checked;
    my %selected;
	my $enabled;
    if (($is_editing) && ($par{'sure'} ne 'y')) {
        %config = config_line(read_config_line($line));
		$enabled = $config{'enabled'};
		if ($config{'tos'}) {
			$config{'tos_type'} = 'tos';
		}
		if ($config{'dscp_class'}) {
			$config{'tos_type'} = 'dscp_class';
		}
		if ($config{'dscp_value'} || $config{'dscp_value'} eq "0") {
			$config{'tos_type'} = 'dscp_value';
		}
    }
    else {
        %config = %par;
		$enabled = 'on';
    }

    
    my $protocol = $config{'protocol'};
    if (! $protocol && !$is_editing) {
        $protocol = 'vvvvvv';
    }
    $protocal =~ s/&/+/g;

    my $src_type = 'src_type';

    my $dst_type = 'dst_type';
    my $cmd_type = 'service';
	my $tos_type = 'tos_type';


    my $src_dev = $config{'src_dev'};
    my $dst_dev = $config{'dst_dev'};
	my $note = $config{'note'};
    my $dst_ip = $config{'dst_ip'};
    my $policy = $config{'policy'};
    my $limit = $config{'limit'};
    my $src_ip = $config{'src_ip'};
	my $mac = $config{'mac'};
    my $port = $config{'port'};
	my $tos = $config{'tos'};
	my $dscp_class = $config{'dscp_class'};
	my $dscp_value = $config{'dscp_value'};
  
    my $datestop = $config{'datestop'};
    

    my $SrcUserlistId = $config{'SrcUserlistId'};
    my $DesUserlistId = $config{'DesUserlistId'};
    my $AppnameList   = $config{'AppnameList'};
    &debug2file('fdf');
    &debug2file($AppnameList);
    my $reglar_AppnameList =  $AppnameList;
        $reglar_AppnameList =~ s/:/&/g;
    my $appNames = &get_appName($reglar_AppnameList);
    $checked{'ENABLED'}{$enabled} = 'checked';
    $selected{'PROTOCOL'}{$protocol} = 'selected ';
	$selected{$dst_dev} = "selected";
	if ($source =~ /^$/) {
        foreach my $item (split(/&/, $src_dev)) {
            $selected{'src_dev'}{$item} = 'selected';
        }
        if ($src_dev !~ /^$/) {
            $src_type = 'dev';
        }
    }
	
	#判断源输入类型
        if ($src_dev !~ /^$/) 
		{
            $src_type = 'dev';
        }
		
		if($src_ip !~ /^$/) {
            $src_type = 'ip';
        }
		
		if($mac !~ /^$/) {
            $src_type = 'mac';
        }

        if($SrcUserlistId !~ /^$/){
            $src_type = 'userGroup';
        }


        if ($dst_ip !~ /^$/) 
        {
            $dst_type = 'ip';
        }
        
        if($DesUserlistId !~ /^$/) {
            $dst_type = 'userGroup';
        }
        
        if($AppnameList !~ /^$/){
            $cmd_type = 'apply';
        }

		if($tos)
		{
			$tos_type = 'tos';
			$twoTos ="style='display:display;'";
		}elsif($dscp_class)
		{
			$tos_type = 'dscp_class';
			$thirdTos = "style='display:display;'";
		}elsif($dscp_value)
		{
           $tos_type = 'dscp_value';
		   $fourTos = "style='display:display;'";
		}

	#判断tos输入类型	
		$tos_type = $config{'tos_type'};			
		
		
  if ($is_editing) {
        if (($src_ip =~ /^$/) && ($src_dev =~ /^$/) && ($mac =~ /^$/) && ($SrcUserlistId =~ /^$/)) {
            $src_type = 'any';
        }
        
        if( $AppnameList =~ /^$/ ){
            $cmd_type = 'service';
        }
		if (($tos =~ /^$/) && ($dscp_class =~ /^$/) && ($dscp_value =~ /^$/)) {
            $tos_type = "tos_all";
        }
    
    }
    if (($dst_ip =~ /^$/)  && ($DesUserlistId =~ /^$/)) {
            $dst_type = 'any';
        }
        &debug2file($cmd_type);
    $selected{'src_type'}{$src_type} = 'selected';
    $selected{'dst_type'}{$dst_type} = 'selected';
    $selected{'cmd_type'}{$cmd_type} = 'selected';
    $selected{'tos_type'}{$tos_type} = 'selected';
	$selected{'tos'}{$tos} = 'selected';

    my %foil = ();
    $foil{'title'}{'src_any'} = 'none';
    $foil{'title'}{'src_dev'} = 'none';
    $foil{'title'}{'src_ip'} = 'none';
	$foil{'title'}{'src_mac'} = 'none';
    $foil{'value'}{'src_any'} = 'none';
    $foil{'value'}{'src_dev'} = 'none';
    $foil{'value'}{'src_ip'} = 'none';
    $foil{'value'}{'src_mac'} = 'none';
	$foil{'value'}{'SrcUserlistIdGroup'} = 'none';

    $foil{'title'}{'src_type'} = 'none';
    $foil{'title'}{'dst_type'} = 'none';
    $foil{'title'}{'dst_any'} = 'none';
    $foil{'title'}{'dst_dev'} = 'none';
    $foil{'title'}{'dst_ip'} = 'none';
    $foil{'title'}{'dst_mac'} = 'none';
    $foil{'title'}{'DesUserlistIdGroup'} ='none';
    $foil{'title'}{'cmd_service'} ='none';
    $foil{'title'}{'cmd_apply'} ='none';
    

    $foil{'value'}{'src_type'} = 'none';
    $foil{'value'}{'dst_type'} = 'none';
    $foil{'value'}{'dst_any'} = 'none';
    $foil{'value'}{'dst_dev'} = 'none';
    $foil{'value'}{'dst_ip'} = 'none';
    $foil{'value'}{'dst_mac'} = 'none';
    $foil{'value'}{'DesUserlistIdGroup'} = 'none';
    $foil{'value'}{'cmd_service'} = 'none';
    $foil{'value'}{'cmd_apply'} = 'none';

    $foil{'title'}{"src_$src_type"} = 'block';
    $foil{'value'}{"src_$src_type"} = 'block';

    $foil{'title'}{"cmd_$cmd_type"} = 'block';
    $foil{'value'}{"cmd_$cmd_type"} = 'block';
   

    $foil{'title'}{"dst_$dst_type"} = 'block';
    $foil{'value'}{"dst_$dst_type"} = 'block';

    $src_ip =~ s/&/\n/gm;
    $dst_ip =~ s/&/\n/gm;
    $mac    =~ s/&/\n/gm;
    $port =~ s/&/\n/gm;

    my $policy_share_checked = "checked";
    my $policy_exclusive_checked = "";
    my $limit_hidden = "hidden";
    if($policy eq 'exclusive') {
        $policy_share_checked = "";
        $policy_exclusive_checked = "checked";
        $limit_hidden = "";
    }

    my $line_count = line_count();

    my $src_dev_size = int((length(%$deviceshash) + $#nets) / 3);
    if ($src_dev_size < 3) {
       $src_dev_size = 3;
    }
    my $dst_dev_size = $src_dev_size;
	my @configlines = read_config_file($QOS_config);
    my $action = 'add';
    my $sure = '';
    my $title = '添加规则';
    my $button = _("Create rule");
    if ($is_editing) {
        $action = 'edit';
        $button = "编辑规则";
        $show = "showeditor";
        $title = '编辑规则';
		
    }
    elsif(@errormessages >0) {
        $show = "showeditor";
    }
	else{$show = "";}

    my @temp;
	&openeditorbox($title,"", $show, "createrule",@temp);

    printf <<EOF
    </form>
    <form name="RULE_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr class="env">
            <td class="add-div-type" >%s*</td>
			<td>
              %s <select name="src_type" onchange="toggleTypes('src');" onkeyup="toggleTypes('src');" style="width:114px">
                <option value="any" $selected{'src_type'}{'any'}>&lt;%s&gt;</option>
                <!--<option value="dev" $selected{'src_type'}{'dev'}>%s</option>-->
                <option value="ip" $selected{'src_type'}{'ip'}>%s</option>
                <option value="userGroup" $selected{'src_type'}{'userGroup'}>%s</option>
                <!--<option value="mac" $selected{'src_type'}{'mac'}>%s</option>-->
              </select>
            </td>
            <td colspan="3">
              <div id="src_any_t" style="display:$foil{'title'}{'src_type'}">%s</div>
              <div id="src_dev_t" style="display:$foil{'title'}{'src_dev'}">%s:</div>
              <div id="src_ip_t" style="display:$foil{'title'}{'src_ip'}">%s:</div>
              <div id="src_userGroup_t" style="display:$foil{'title'}{'SrcUserlistIdGroup'}">%s:</div>
              <div id="src_userGroup_v" style="display:$foil{'title'}{'SrcUserlistIdGroup'}">
                <input type="text" id="SrcUserlist" value="$SrcUserlistId">
                <input type="hidden" id="SrcUserlistId" name="SrcUserlistId" value="$SrcUserlistId">
                <input type="button" value="配置" onclick="load_userlist(SrcUserlist_panel);">
              </div>
              <div id="src_mac_t" style="display:$foil{'title'}{'src_mac'}">%s:</div>
              <div id="src_any_v" style="display:$foil{'value'}{'src_any'}" >&nbsp;</div>

EOF
, _('Source')
, _('Type')
, _('ANY')
, _('区域/接口')
, _('Network/IP')
, _('用户组')
, _('MAC')

, _('该规则将匹配所有目标')
, _('选择接口（按CTRL多选）')
, _('Insert Network/IPs (one per line)')
, _('用户组')
, _('Insert MAC Addresses (one per line)')
;

##########
# SOURCE #
##########

#### Device begin ###########################################################
#     printf <<EOF
#               <div id='src_dev_v' style='display:$foil{'value'}{'src_dev'}'>
#               <select name="src_dev" multiple >
# EOF
# ;
# 	foreach my $key (sort keys %ethname) {
# 		 printf  printf <<EOF
# 							<option value=$key $selected{'src_dev'}{$key}>$ethname{$key}</option>
# EOF
# ; 	
# 	}
#         printf <<EOF
#                 </select>
#               </div>
# EOF
# ;
#### Device end #############################################################

#### IP begin ###############################################################
    printf <<EOF
              <div id='src_ip_v' style='display:$foil{'value'}{'src_ip'}'>
              <textarea name='src_ip' wrap='off' rows='5' cols='35'>$src_ip</textarea>
              </div>
EOF
;
#### IP end #################################################################

#### MAC begin ##############################################################
    printf <<EOF
              <div id='src_mac_v' style='display:$foil{'value'}{'src_mac'}'>
              <textarea name='mac' wrap='off'  rows='5' cols='35'>$mac</textarea>
              </div>		  
			  </td>
              </tr>
            <tr class="env">
            <td class="add-div-type" >目标 $dst_type *</td>
            <td>
              %s <select name="dst_type" onchange="toggleTypes('dst');" onkeyup="toggleTypes('dst');" style="width:114px">
                <option value="any" $selected{'dst_type'}{'any'}>&lt;%s&gt;</option>
                <option value="ip" $selected{'dst_type'}{'ip'}>%s</option>
                <option value="userGroup" $selected{'dst_type'}{'userGroup'}>%s</option>
              </select>
            </td>
            <td colspan="2">
              <div id="dst_any_t" style="display:$foil{'title'}{'dst_any'}">%s</div>
              <div id="dst_ip_t" style="display:$foil{'title'}{'dst_ip'}">%s:</div>
              <div id="dst_userGroup_t" style="display:$foil{'title'}{'DesUserlistIdGroup'}">%s:</div>
              <div id="dst_userGroup_v" style="display:$foil{'title'}{'DesUserlistIdGroup'}">
                <input type="text" id="DesUserlist" value="$DesUserlistId">
                <input type="hidden" id="DesUserlistId" name="DesUserlistId" value="$DesUserlistId">
                <input type="button" value="配置" onclick="load_userlist(DesUserlist_panel);">
              </div>
              <!--<div id="dst_mac_t" style="display:$foil{'title'}{'dst_mac'}">%s:</div>-->
              <div id="dst_any_v" style="display:$foil{'value'}{'dst_any'}" >&nbsp;</div>

EOF

, _('Type')
, _('ANY')
, _('Network/IP')
, _('用户组')

, _('该规则将匹配所有目标')
, _(' 目标网络/IP(网络IP一行一个)')
, _('用户组')
# , _('Insert MAC Addresses (one per line)')
;

##########
# SOURCE #
##########

#### Device begin ###########################################################
#     printf <<EOF
#               <div id='dst_dev_v' style='display:$foil{'value'}{'src_dev'}'>
#               <select name="dst_dev" multiple >
# EOF
# ;
#     foreach my $key (sort keys %ethname) {
#          printf  printf <<EOF
#                             <option value=$key $selected{'src_dev'}{$key}>$ethname{$key}</option>
# EOF
# ;   
#     }
#         printf <<EOF
#                 </select>
#               </div>
# EOF
# ;
#### Device end #############################################################

#### IP begin ###############################################################
    printf <<EOF
              <div id='dst_ip_v' style='display:$foil{'value'}{'dst_ip'}'>
              <textarea name='dst_ip' wrap='off' rows='5' cols='35'>$dst_ip</textarea>
              </div>
EOF
;
#### IP end #################################################################

#### MAC begin ##############################################################
    printf <<EOF
                
    </td>
    <td>
        <div id="policy_div" class="$policy_div_hidden">
            <span id="policy_text" class="left_text_label">带宽策略:</span>
            <span id="policy_choice" class="right_text_label">
                <span class="single_line">
                    <input type="radio" name="policy" id="policy_share" class="radio_input" value="share" onclick="change_policy(this.value)" $policy_share_checked/>
                    <label for="policy_share" class="label_for_radio">共享</label>
                </span>
                <span class="single_line">
                    <input type="radio" name="policy" id="policy_exclusive" class="radio_input" value="exclusive" onclick="change_policy(this.value)" $policy_exclusive_checked/>
                    <label for="policy_exclusive" class="label_for_radio">独占</label>
                    <span id="limit_content" class="inline_tag $limit_hidden">
                        <span class="left_text_label">最大带宽</span>
                        <input type="text" id="limit" name="limit" class="inline_input" value="$limit"/>
                        <span class="right_text_label">kbit/s</span>
                    </span>
                    <span class="alert_tip" id="conflict_tip"></span>
                </span>
            </span>
        </div>
    </td>
              </tr>
            <tr class="odd">
            <td class="add-div-type">
            <!-- begin destination -->
			目标设备/流量类型*</td>
                <td colspan="4">类型 <select id="dst_dev" name="dst_dev" onkeyup="toggle_policy(this);" onchange="toggle_policy(this);" style="width:114px">							 
EOF
,
;
readclass();
my $dirlength = @dst;
for (my $num=0;$num<$dirlength ;$num++) {
    my $br0_bridged_class = "";
    if(%dst_br0_config->{$dst_class[$num]}) {
        if(%dst_br0_config->{$dst_class[$num]."policy"} eq "exclusive") {
            #如果不是编辑状态，不显示，如果是编辑状态，显示当前正在被编辑的那一条
            if($dst_dev ne $dst_class[$num]) {
                next;#不显示
            }
        }
        $br0_bridged_class = "br0".%dst_br0_config->{$dst_class[$num]."policy"}.":".%dst_br0_config->{$dst_class[$num]."sharecount"};#加上次数
    }
    print "<option class='$br0_bridged_class' value='$dst_class[$num]' $selected{$dst_class[$num]}>$dst[$num]</option>";
}
#=============================#
# changed by 文虎先
# 用于实现qos规则页面编辑目标
# 设备记住上次选项的问题
# 2010.12.31
#=============================#
=p
my $dirlength = @dst;
my $tmp_offset;
my $tmp_class = $config{'dst_dev'};
for($z=0;$z<$dirlength;$z++)
{
    if ( $tmp_class eq $dst_class[$z])
    {
        $tmp_offset = $z;
    }
}

for($z=0;$z<$dirlength;$z++)
{
  if ($tmp_offset == $z)
  {
  printf <<EOF
  <option $selected{'dst_dev'}{$dst[$z]} selected="selected">$dst[$z]</option>	
EOF
,

  }
  else
  {
    printf <<EOF
  <option $selected{'dst_dev'}{$dst[$z]}>$dst[$z]</option>
EOF
    ,
    ;
}
}
=cut
#=============================#
# End of changed by文虎先
# 2010.12.31
#=============================#
    ##===判断当前选择的是否为br0(GREEN)接口===#
    my $policy_div_hidden = "hidden";
    if(%dst_br0_config->{$dst_dev}) {
        $policy_div_hidden = "";
    }
    if($dst_dev eq "" && @dst_devices[0] eq 'GREEN') {
        $policy_div_hidden = "";
    }
printf <<EOF			 
                            </select></td>
	<!--<td>
	目标网络/IP(网络IP一行一个)<br/>
    <textarea id='dst_ip_v' name='dst_ip' wrap='off'  rows='5' cols='35'>$dst_ip</textarea>
    </td>
    <td>
        <div id="policy_div" class="$policy_div_hidden">
            <span id="policy_text" class="left_text_label">带宽策略:</span>
            <span id="policy_choice" class="right_text_label">
                <span class="single_line">
                    <input type="radio" name="policy" id="policy_share" class="radio_input" value="share" onclick="change_policy(this.value)" $policy_share_checked/>
                    <label for="policy_share" class="label_for_radio">共享</label>
                </span>
                <span class="single_line">
                    <input type="radio" name="policy" id="policy_exclusive" class="radio_input" value="exclusive" onclick="change_policy(this.value)" $policy_exclusive_checked/>
                    <label for="policy_exclusive" class="label_for_radio">独占</label>
                    <span id="limit_content" class="inline_tag $limit_hidden">
                        <span class="left_text_label">最大带宽</span>
                        <input type="text" id="limit" name="limit" class="inline_input" value="$limit"/>
                        <span class="right_text_label">kbit/s</span>
                    </span>
                    <span class="alert_tip" id="conflict_tip"></span>
                </span>
            </span>
        </div>
    </td>-->
    </tr>
     
                          
EOF
, _('网络/IP（每行一个）')
;

###############
#   SERVICE   #
###############
    printf <<EOF
        <tr class="env">
            <td class="add-div-type">%s</td>
            <td class="add-div-type">
               %s<select name="cmd_type" onchange="toggleTypes('cmd');" onkeyup="toggleTypes('cmd');" style="width:108px">
                <option value="service"  $selected{'cmd_type'}{'service'} >&lt;服务&gt;</option>
                <option value="apply" $selected{'cmd_type'}{'apply'}>&lt;应用&gt;</option>
              </select>
            </td>
			<td width="180px">
                <div id="cmd_service_v" style="display:$foil{'value'}{'cmd_service'}">
                    服务 *<select name="service_port" onchange="selectService('protocol', 'service_port', 'port');" onkeyup="selectService('protocol', 'service_port', 'port');" style="width:108px">
                        <option value="any/any"> &lt;任意&gt;</option>
               
               
EOF
    , _('服务/应用')
    , _('类型')
   
    ;
   # my @arr = create_servicelist($protocol, $config{'port'});
	open(SERVICE_FILE, $services_file);
    @services = <SERVICE_FILE>;
    close(SERVICE_FILE);
	
	foreach my $line (@services) {
        my ($desc, $ports, $proto) = split(/,/, $line);
        chomp($desc);
        chomp($ports);
        chomp($proto);
        my $choosen='';
		$desc =~s/User define/用户自定义/;
        $proto = lc($proto);
        if (($proto eq $protocol) && ($ports eq $config{'port'})) {
            $choosen="selected";
            $selected="$ports/$proto";
        }
        print "<option value='$ports/$proto' $choosen>$desc</option>";
    }

# check if ports should be enabled
    if ($protocol eq "") {
        $portsdisabled = 'disabled="true"';
    }
my $time_enabled = "";
my $time_display = "none";	

if($datestop)
{
    $time_display = "table";
    $time_enabled = "checked='checked'";
}


    printf <<EOF

                </select>
            </div>
            <div id="cmd_apply_v" style="display:$foil{'value'}{'cmd_apply'}">
                应用<input type="text" id="Appname" value="$appNames" style="width:100px;">
                <input type="hidden" id="AppnameList" name="AppnameList" value="$AppnameList">
                <input type="button" value="配置" onclick="load_app();" >
            </div>
                        </td>
                        <td width="180px">
                            <div id="cmd_service_t" style="display:$foil{'title'}{'cmd_service'}">
                                 协议* <select  name="protocol" id="protocol_a" onchange="updateService('protocol', 'service_port', 'port');" onkeyup="updateService('protocol', 'service_port', 'port');" style="width:108px">
                                <option value="" $selected{'PROTOCOL'}{'any'}>&lt;任意&gt;</option>
                                <option value="tcp" $selected{'PROTOCOL'}{'tcp'}>TCP</option>
                                <option value="udp" $selected{'PROTOCOL'}{'udp'}>UDP</option>
                                <option value="tcp&udp" $selected{'PROTOCOL'}{'tcp&udp'}>TCP+UDP</option>
                                <option value="esp" $selected{'PROTOCOL'}{'esp'}>ESP</option>
                                <option value="gre" $selected{'PROTOCOL'}{'gre'}>GRE</option>
                                <option value="icmp" $selected{'PROTOCOL'}{'icmp'}>ICMP</option>
                            </selected>
                                
                            </div>
                           <td>
                                <div id="cmd_service_opt" style="display:$foil{'title'}{'cmd_service'}">
                                 这条规则将匹配所有目的端口<br />
                                <textarea   value ="port"  name ="port"  rows='5' cols='35' $portsdisabled onkeyup="updateService('protocol', 'service_port', 'port');">$port</textarea>
                                </div>
                            </td>
                            
                        </td>
                        
                    </tr>
            <tr class="env">
            <td class="add-div-type" >
            <b>时间段控制 *</b></td>
            <td colspan="4">
            <input name="TIME_ENABLED" id="time_enabled" type="checkbox"  $time_enabled  onclick ="show_hide('time_enabled','time_control')" >启用
            <span class="note">不勾选则不进行时间过滤(时间段控制范围为开始日期到结束日期，不包含结束日期)</span>
            <table width="100%" style="border:1px solid #999;display:$time_display" id="time_control">
            <tr class="odd">
            <td >
EOF
;
#2013-27 能士项目屏蔽入侵防御
#<option value="ALLOW" $selected{'dst'}{'ALLOW'}>%s</option>
#, _('入侵防御')
#2014-5-6 打开入侵防御
my $datestart;
if($config{'datestart'})
{
    $datestart = $config{'datestart'};
}else{
    $datestart = `date "+%Y-%m-%d"`;
}
my $end_day;
if($config{'end_day'})
{
    $end_day = $config{'end_day'};
}else{
    $end_day = `date "+%Y-%m-%d"`;
}


printf <<EOF
             开始日期：<input type="text" SIZE="12" id="startDate" name='START_DAY' value="$datestart" readOnly="readOnly" />
<script type="text/javascript"> 
ESONCalendar.bind("startDate");
</script>  
            </td>
            
            <td colspan="2">
            结束日期：<input type="text" SIZE="12" id="endDate" name='END_DAY' value="$datestop" readOnly="readOnly" />
<script type="text/javascript"> ESONCalendar.bind("endDate");
</script>  
            </td>
            
            </tr>
        
        <tr class="env">
            <td>周:
            <select  id="week" name="WEEK" multiple style="width: 150px; height: 80px;">
EOF
;
if($config{'weekdays'})
{
my @weeks = split(/|/,$config{'weekdays'});
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
        print "<option  selected = 'selected' value='".$day."'>".$week{$day}."</option>";
    }else{
        print "<option  value='".$day."'>".$week{$day}."</option>";
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
        <tr class="odd">
            <td class="add-div-type">%s *</td>
             <td colspan="2">%s
                            <select name="tos_type" id = "TOSID" onchange = "Check()">
	                            <option value="tos_any" $selected{'tos_type'}{'tos_any'}>%s</option>
                                <option value="tos" $selected{'tos_type'}{'tos'}>TOS</option>
                                <option value="dscp_class" $selected{'tos_type'}{'dscp_class'}>DSCP class</option>
                                <option value="dscp_value" $selected{'tos_type'}{'dscp_value'}>DSCP value</option>
                            </select>
             </td>    
			<td colspan="2"><div id = "allTos" $allTos name = "tos_all">该规则将匹配所有TOS/DSCP标志</div>
			<div id = "twoTos" $twoTos >匹配具有以下TOS标志的流量
	<select name = "tos">
EOF
, _('Protocol')
, _('ANY')
, _('Destination port (one per line)')
, _('TOS/DSCP')
, _('输入')
, _('ANY')
;

print <<EOF
<option value="0" $selected{'tos'}{'0'}>请选择</option>
<option value="Minimize-Delay" $selected{'tos'}{'Minimize-Delay'}>Minimize-Delay</option>
<option value="Maximize-Throughput" $selected{'tos'}{'Maximize-Throughput'}>Maximize-Throughput</option>
<option value="Maximize-Reliability" $selected{'tos'}{'Maximize-Reliability'}>Maximize-Reliability</option>
<option value="Minimize-Cost" $selected{'tos'}{'Minimize-Cost'}>Minimize-Cost</option>
<option value="Normal-Service" $selected{'tos'}{'Normal-Service'}>Normal-Service</option>
</select>
	</div>
	<div id = "thirdTos" $thirdTos>匹配具有以下DSCP标志的流量
	<select name = "dscp_class" >
EOF
;

my $tmp_class_key = '';
foreach my $tmp_key(sort keys %dscp_class)
{
    # modified by squall
    if ($dscp_class{$tmp_key} =~ $dscp_class or $dscp_class{$tmp_key} eq $dscp_class)
    {
        $tmp_class_key = $tmp_key;
    }
    # end
}

foreach my $k2 (sort keys %dscp_class)
{
    if ($k2 eq $tmp_class_key)
	{
        printf <<EOF
            <option value="$dscp_class{$k2}" selected="selected " id = "$k2">$dscp_class{$k2}</option>
EOF
,
;
	}
	else 
    {
        printf <<EOF
	    <option value="$dscp_class{$k2}"  id = "$k2">$dscp_class{$k2}</option>
EOF
,
;
    } 

}

printf <<EOF	
	</select></div>	<div id = "fourTos" $fourTos>匹配具有以下DSCP值的流量

	<input type = "text" maxlength="10" value="$dscp_value" name = "dscp_value"/>(整数,位于0-63之间)
	</div> 
	</td>
	</tr> 

EOF
,
; 
printf <<EOF

        <input type="hidden" name="ACTION" value="$action">
        <input id="edit_line" type="hidden" name="line" value="$line">
        <input type="hidden" name="sure" value="y">
   <tr class="env">
	<td class="add-div-type">注释</td>
	<td colspan="4"><input name = "note" type = "text" value = "$note" style="width:189px"></td>
	</tr>
	<tr class="env">
		<td class="add-div-type">插入位置</td>
		<td colspan="4"><select name="position" style="width:193px">
		<option value="0" $selected{'0'}>第一条</option>
EOF
;

my $lastselected;
if ($par{'line'} !~ /^\d+$/) {
	$lastselected = "selected";
}
else{
	$selected{$par{'line'}} = "selected";
}
for (my $num=1;$num<@configlines ;$num++) {
	print "<option value='$num' $selected{$num}>在规则 #$num 之后</option>";
}
if (@configlines > 0) {
	print "<option value='9999' $lastselected>最后一条</option>";
}
printf <<EOF
		</select></td>
	</tr>
	<tr class="odd">
		<td class="add-div-type">启用</td>
		<td colspan="4"><input name="enabled" value="on" $checked{'ENABLED'}{'on'} type="checkbox"></td>
	</tr>
	</table>
EOF
;
printf <<EOF
 <script>
	Check();
	toggleTypes('src');
 </script>
EOF
;
if ($action eq 'add') {
	printf <<EOF
 <script>
	selectService('protocol', 'service_port', 'port');
 </script>
EOF
;
}
if ($action eq 'edit') {
	printf <<EOF
 <script>
	updateService('protocol', 'service_port', 'port');
 </script>
EOF
;
}
	 &closeeditorbox($button, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
	 
}
   






sub reset_values() {
    %par = ();
    $par{'LOG_ACCEPTS'} = $log_accepts;
}


sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    if ($action eq 'apply') {
		&log("应用规则配置");
		system("/usr/local/bin/restartqos");
		$notemessage ="成功应用当前配置";
        return;
    }
    if ($action eq 'save') {
        reset_values();
        system($setincoming);
		$reload = 1;
        return;
    }
    if ($action eq 'up') {
        &log("上移第".($par{'line'}+1)."规则");
        move($par{'line'}, -1);
        reset_values();
		$reload = 1;
        return;
    }
    if ($action eq 'down') {
        &log("下移第".($par{'line'}+1)."规则");
        move($par{'line'}, 1);
        reset_values();
		$reload = 1;
        return;
    }
    if ($action eq 'delete') {
        &log("删除了第".($par{'line'}+1)."条规则");
        delete_line($par{'line'});
        reset_values();
		$reload = 1;
        return;
    }
   

    if ($action eq 'enable') {
        if (toggle_enable($par{'line'}, 1)) {
            &log("启用了第".($par{'line'}+1)."条规则");
            reset_values();
			$reload = 1;
            return;
        }
    }
    if ($action eq 'disable') {
        if (toggle_enable($par{'line'}, 0)) {
            &log("禁用了第".($par{'line'}+1)."条规则");
            reset_values();
			$reload = 1;
            return;
        }
    }
 
    # ELSE
    if (($action eq 'add') ||
	(($action eq 'edit')&&($sure eq 'y'))) {
        my $src_type = $par{'src_type'}; #1
        my $dst_type = $par{'dst_type'}; #2
        my $dst_dev = $par{'dst_dev'}; #3
        my $cmd_type = $par{'cmd_type'};#4
        my $TIME_ENABLED = $par{'TIME_ENABLED'};#5
        my $tos_type = $par{'tos_type'};#6
        my $note = $par{'note'};#7
        my $enabled = $par{'enabled'};#9
       
        my $mac = '';
        my $src_ip = '';
        my $src_dev = '';
        my $dst_ip = '';
        my $policy = $par{'policy'};
        my $limit = $par{'limit'};
        my $tos = '';
        my $dscp_class = '';
        my $dscp_value = '';
        my $protocol = '';
        my $port = '';
       

        my $datestart =$par{'START_DAY'} ;
        my $datestop = $par{'END_DAY'};
        

        my $weekdays = $par{'WEEK'};
        my $SrcUserlistId = '';
        my $DesUserlistId = '' ;
        my $AppnameList = '';

		#将dst_dev在class文件中进行映射
=p
        my @lines;
        my $conf = '/var/efw/shaping/classes';
        open (FILE, "<$conf");
        foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
        }
        close (FILE);
	    my $length = @lines;
	    my $i;
        for($i=0;$i<$length;$i++)
	    {
	     my @linestemp = split(',', $lines[$i]);
	     if( $dst_dev_temp eq $linestemp[3])
		 {
		     $dst_dev = $linestemp[1];
		 }
	    }
=cut
		
		
        if($policy ne 'exclusive'){
            $limit = "";
            $policy = "";
        }

        if ($src_type eq 'ip') {
            $src_ip = $par{'src_ip'};
           
        }
        if ($src_type eq 'userGroup') {
           
            $SrcUserlistId= $par{'SrcUserlistId'};
        }
      
        if ($src_type eq 'dev') {
            $src_dev = $par{'src_dev'};
        }
        
		if ($src_type eq 'mac') {
            $mac = $par{'mac'};
        }
		if($dst_type eq 'ip'){
            $dst_ip = $par{'dst_ip'}
        }
        if($dst_type eq 'userGroup'){
            $DesUserlistId = $par{'DesUserlistId'};
        }
        if($cmd_type eq 'service'){
            $protocol = $par{'protocol'};
            $port = $par{'port'};
        }
        if($cmd_type eq 'apply'){
            $AppnameList = $par{'AppnameList'}
        }
		if($tos_type eq 'tos')
		{
		    $tos = $par{'tos'};
		
		}
		
		if($tos_type eq 'dscp_class')
		{
		    $dscp_class = $par{'dscp_class'};
        }
		
		if($tos_type eq 'dscp_value')
		{
		    $dscp_value = $par{'dscp_value'};
		
		}

        my $start_hour_min = $par{'START_HOUR'}.":".$par{'START_MIN'};
        my $end_hour_min = $par{'END_HOUR'}.":".$par{'END_MIN'};
        if($par{'TIME_ENABLED'} ne "on")
        {
            $datestart = "";
            $datestop = "";
            $weekdays = "";
            $start_hour_min= "";
            $end_hour_min= "";
        }
        

        my $enabled = $par{'enabled'};
        my $note = $par{'note'};
#class_id,enabled,comment,protocol,src,inputdev,mac,sport,dst,dport,tos,
#dscp,dscp_class,l7filter,policy,limit,datestart,datestop,timestart,timestop,weekdays,SrcUserlistId,DesUserlistId,AppnameList
        
        if (save_line($par{'line'},
					  $dst_dev,
                      $enabled,
					  $note,
                      $protocol, #协议
                      $src_ip,
					  $src_dev,
                      $mac,
					  $know,
					  $dst_ip,
					  $port, #端口号
                      $tos,
					  $dscp_class,
					  $dscp_value,
                      $policy,
                      $limit,
                      $datestart,
                      $datestop,
                      $start_hour_min,
                      $end_hour_min,
                      $weekdays,
                      $SrcUserlistId,
                      $DesUserlistId,
                      $AppnameList
                      )){
					  
            if($action eq 'add')
            {
               &log("添加了一条规则,源IP为 ".$src."目的IP为 ".$dst.$src_dev);
			  
            }elsif($action eq 'edit')
            {
               &log("编辑了一条规则");
			;
            }
            reset_values();
        }
    }
}

&getcgihash(\%par);
$log_accepts = $incoming{'LOG_ACCEPTS'};

&showhttpheaders();


my $extraheaders = '<link rel="stylesheet" type="text/css" href="/include/style.min.css" />
<link rel="stylesheet" type="text/css" href="/include/qosrules.css"/>
<link rel="stylesheet" type="text/css" href="/include/add_list_base.css"/>
<script language="JavaScript" src="/include/jquery-3.1.0.min.js"></script>
<script language="JavaScript" src="/include/jstree.min.js"></script>
<script language="JavaScript" src="/include/ESONCalendar.js"></script>
<script language="JavaScript" src="/include/firewall_type.js"></script>

<script language="JavaScript" src="/include/list_panel.js"></script>
<script language="JavaScript" src="/include/message_manager.js"></script>
<script language="JavaScript" src="/include/services_selector.js"></script>
<script language="JavaScript" src="/include/qosrules.js"></script>';

$extraheaders .= <<EOF

 <script type="text/javascript">
      
	  function Check()
	  {
	    
	     var obj = document.getElementById('TOSID');  
         var m=obj.options[obj.selectedIndex].value;
         if( m == "tos_any")
		 {
           document.getElementById("allTos").style.display = "";
		   document.getElementById("twoTos").style.display = "none";
		   document.getElementById('thirdTos').style.display ="none";
		   document.getElementById('fourTos').style.display = "none";
         }
         if( m == "tos")
		 {
		   document.getElementById("allTos").style.display = "none";
		   document.getElementById("twoTos").style.display = "";
		   document.getElementById('thirdTos').style.display ="none";
		   document.getElementById('fourTos').style.display = "none";
         }
		 if( m == "dscp_class")
		 {
           document.getElementById("allTos").style.display = "none";
		   document.getElementById("twoTos").style.display = "none";
		   document.getElementById('thirdTos').style.display ="";
		   document.getElementById('fourTos').style.display = "none";
		 }
		 if( m == "dscp_value")
		 {
           document.getElementById("allTos").style.display = "none";
		   document.getElementById("twoTos").style.display = "none";
		   document.getElementById('thirdTos').style.display ="none";
		   document.getElementById('fourTos').style.display = "";
		 }
	  }
      //渲染用户组JS树
    function jstree_render(data) {
       
    if(\$("#for_jstree-qosrule")) {
        \$("#for_jstree-qosrule").remove();
    }
    var div = document.createElement("div");
    div.setAttribute("id","for_jstree-qosrule");
    var \$div = \$(div);
    \$("#list_panel_id_for_SrcUserlist_panel .container-main-body").append(\$div);
    \$("#list_panel_id_for_SrcUserlist_panel .container-main-body").css("min-height","200px");
    \$("#list_panel_id_for_SrcUserlist_panel .container-main-body .rule-list").remove();
    \$('#for_jstree-qosrule').jstree({
        "plugins" : [ 
            "checkbox",
            "state", "types", "wholerow" 
        ],
        "core" : {
            "themes" : { "stripes" : true },
            "data" : data
            
        },
        "types": {
            "user" : {
                
                "icon" : "../images/user.png",
            }
        },
        "checkbox" : {
                "keep_selected_style" : false
        },
    
    });
}

 function des_jstree_render(data) {
        
    if(\$("#for_des_jstree-qosrule")) {
        \$("#for_des_jstree-qosrule").remove();
    }
    var div = document.createElement("div");
    div.setAttribute("id","for_des_jstree-qosrule");
    var \$div = \$(div);
    \$("#list_panel_id_for_DesUserlist_panel .container-main-body").append(\$div);
    \$("#list_panel_id_for_DesUserlist_panel .container-main-body").css("min-height","200px");
    \$("#list_panel_id_for_DesUserlist_panel .container-main-body .rule-list").remove();
    \$('#for_des_jstree-qosrule').jstree({
        "plugins" : [ 
            "checkbox",
            "state", "types", "wholerow" 
        ],
        "core" : {
            "themes" : { "stripes" : true },
            "data" : data
            
        },
        "types": {
            "user" : {
                
                "icon" : "../images/user.png",
            }
        },
        "checkbox" : {
                "keep_selected_style" : false
        },
    
    });
}
//渲染应用JS树
function appJstree_render(data) {
    if(\$("#for_appJstree-qosrule")) {
        \$("#for_appJstree-qosrule").remove();
    }
    var div = document.createElement("div");
    div.setAttribute("id","for_appJstree-qosrule");
    var \$div = \$(div);
    \$("#list_panel_id_for_Appid_panel .container-main-body").append(\$div);
    \$("#list_panel_id_for_Appid_panel .container-main-body").css("min-height","200px");
    \$("#list_panel_id_for_Appid_panel .container-main-body .rule-list").remove();
 
    \$('#for_appJstree-qosrule').jstree({
        "plugins" : [ 
            "checkbox",
            "state", "types", "wholerow" 
        ],
        "core" : {
            "themes" : { "stripes" : true },
            "data" : data
            
        },
        "types": {
            "app" : {
                
                "icon" : "../images/application.png",
            }
        },
        "checkbox" : {
                "keep_selected_style" : false
        },
    
    });
}

\$(document).ready(function(){
        
        jstree_render($userlistObj);
        des_jstree_render($userlistObj);
        appJstree_render($applistObj);
    
});
 </script>
EOF
,
;	
 
 
&openpage(_('规则设置'), 1, $extraheaders);

&init_ethconfig();
&configure_nets();
($devices, $deviceshash) = list_devices_description(3, 'GREEN|ORANGE|BLUE', 0);
&save();

my $errormessage = "";
foreach my $line_temp(@errormessages)
{
	$errormessage.=$line_temp."<br />";
}
&openbigbox($errormessage, $warnmessage, $notemessage);

if ($reload) {
    system("touch $needreload");
}

if (-e $needreload) {
    applybox(_("配置已经更改，需要应用才能使更改生效!"));
}

my $is_editing = 0;
if ($par{'ACTION'} eq 'edit') {
    $is_editing = 1;
}
=p
if ($is_editing ne 1 && $#errormessages ne -1 &&) {
    $is_editing = 1;
}
=cut
my @lines = read_config_file("/var/efw/shaping/config");
my $length = @lines;
display_rules($is_editing, $par{'line'});
check_form();
&closebigbox();
&closepage();
