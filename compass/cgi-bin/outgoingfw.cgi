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
use Data::Dumper;
my $outgoing_config = "${swroot}/outgoing/config";
my $outgoing_settings = "${swroot}/outgoing/settings";
my $outgoing_default_settings = "${swroot}/outgoing/default/settings";
my $ethernet_settings = "${swroot}/ethernet/settings";
my $setoutgoing = "/usr/local/bin/setoutgoing";
my $confdir = '/etc/firewall/outgoingfw/';
my $needreload = "${swroot}/outgoing/needreload";

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
my $excute_cmd = 'sudo /usr/local/bin/get_outgoingfw_info.py';
my $json = new JSON::XS;
my (%par,%checked,%selected,%ether,%outgoing);
my @errormessages = ();
my $policy = 'DENY';
my $log_accepts = 'off';
my @nets;
my $reload = 0;
my %outgoinghash=();
my $outgoing = \%outgoinghash;

my %ifacesdata = ();
my $ifacesdata = \%ifacesdata;

my $services_file = '/var/efw/outgoing/services';
my $services_custom_file = '/var/efw/outgoing/services.custom';

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

&readhash($ethernet_settings, \%ether);

if (-e $outgoing_default_settings) {
    &readhash($outgoing_default_settings, \%outgoing);
}
if (-e $outgoing_settings) {
    &readhash($outgoing_settings, \%outgoing);
}


sub check_form()
{
#表单检查代码添加-2012-08-30-zhouyuan
printf <<EOF
<script>    
var object = {
       'form_name':'OUTGOING_FORM',
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
                    'src_dev':{
                               'type':'select-multiple',
                               'required':'0'
                             },
                    'dst_dev':{
                               'type':'select-multiple',
                               'required':'0'
                             },
                    'source':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|ip_mask|'
                             },
                    'destination':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|ip_mask|'
                             },
                    'mac':{
                               'type':'textarea',
                               'required':'0',
                               'check':'mac|'
                             },
                    'port':{
                               'type':'textarea',
                               'required':'0',
                               'check':'port|port_range|'
                             },

                    'src_port':{
                               'type':'textarea',
                               'required':'0',
                               'check':'port|port_range|'
                             },                    
                    'START_HOUR':{
                               'type':'select-one',
                               'required':'1',
                               'ass_check':function(eve){
                                                        var msg;
                                                        var start_hour = parseInt(eve._getCURElementsByName("START_HOUR","select","OUTGOING_FORM")[0].value);
                                                        var start_min = parseInt(eve._getCURElementsByName("START_MIN","select","OUTGOING_FORM")[0].value);
                                                        var end_hour = parseInt(eve._getCURElementsByName("END_HOUR","select","OUTGOING_FORM")[0].value);
                                                        var end_min = parseInt(eve._getCURElementsByName("END_MIN","select","OUTGOING_FORM")[0].value);
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
                                                        var start_hour = parseInt(eve._getCURElementsByName("START_HOUR","select","OUTGOING_FORM")[0].value);
                                                        var start_min = parseInt(eve._getCURElementsByName("START_MIN","select","OUTGOING_FORM")[0].value);
                                                        var end_hour = parseInt(eve._getCURElementsByName("END_HOUR","select","OUTGOING_FORM")[0].value);
                                                        var end_min = parseInt(eve._getCURElementsByName("END_MIN","select","OUTGOING_FORM")[0].value);
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
                                                        var start_day = eve._getCURElementsByName("START_DAY","input","OUTGOING_FORM")[0].value;
                                                        var end_day = eve._getCURElementsByName("END_DAY","input","OUTGOING_FORM")[0].value;
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
                                                        var start_day = eve._getCURElementsByName("START_DAY","input","OUTGOING_FORM")[0].value;
                                                        var end_day = eve._getCURElementsByName("END_DAY","input","OUTGOING_FORM")[0].value;
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
//check._get_form_obj_table("OUTGOING_FORM");
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
    if (($service_status ne $par{'POLICY'}) || 
            ($log_accepts ne $par{'LOG_ACCEPTS'})) {
        if ($par{'POLICY'} eq "off") {
            $policy = "ALLOW";
			my @cur_user=&getCurUser();
	        my $input_user=$cur_user[0];
	        system("/usr/bin/logger","-p","daemon.notice","-t","userLog-$input_user","成功关闭流出防火墙");
        }
        else {
		    my @cur_user=&getCurUser();
	        my $input_user=$cur_user[0];
	        system("/usr/bin/logger","-p","daemon.notice","-t","userLog-$input_user","成功开启流出防火墙");
            $policy = "DENY";
        }
        $log_accepts = $par{'LOG_ACCEPTS'};
        open(FILE,">$outgoing_settings") or die "Unable to open config file '$outgoing_settings' because $!.";
        print FILE "POLICY=$policy\n";
        print FILE "LOG_ACCEPTS=$log_accepts\n";
        close FILE;
		`sudo fmodify $outgoing_settings`;
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
    my @lines = read_config_file($outgoing_config);
    return $lines[$line];
}

sub save_config_file_back($) {
    my $ref = shift;
    my @lines = @$ref;
    open (FILE, ">$outgoing_config");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
	`sudo fmodify $outgoing_config`;
    $reload = 1;
}

sub line_count() {
    open (FILE, "$outgoing_config") || return 0;
    my $i = 0;
    foreach (<FILE>) {
        $i++;
    }
    close FILE;
    return $i;
}

sub append_config_file($) {
    my $line = shift;
    open (FILE, ">>$outgoing_config");
    print FILE $line."\n";
    close FILE;
	`sudo fmodify $outgoing_config`;
    $reload = 1;
}
sub dateToFilestring($) {
    my $date = shift;
    $date =~ s/\-//g;
    return $date;
}
sub is_valid($) {
    my $line = shift;
    if ($line =~ /(?:(?:[^,]*),){9}/) {
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
    $config{'src_port'} = $temp[11];
    $config{'start_day'}= $temp[12];
    $config{'end_day'}= $temp[13];
    $config{'start_hour_min'}= $temp[14];
    $config{'end_hour_min'}= $temp[15];
    $config{'week'}= $temp[16];
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
                     $data{'source'},
                     $data{'destination'},
                     $data{'port'},
                     $data{'target'},
                     $data{'mac'},
                     $data{'remark'},
                     $data{'log'},
                     $data{'src_dev'},
                     $data{'dst_dev'},
					 $data{'start_day'}, 
					 $data{'end_day'}, 
					 $data{'week'}, 
					 $data{'start_hour_min'}, 
				     $data{'end_hour_min'},
                     $data{'src_port'});
}

sub move($$) {
    my $line = shift;
    my $direction = shift;
    my $newline = $line + $direction;
    if ($newline < 0) {
        return;
    }
    my @lines = read_config_file($outgoing_config);

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
    my @lines = read_config_file($outgoing_config);
    my $myline = $lines[$old];
    my @newlines = ();

    # nothing to do
    if ($new == $old) {
        return;
    }
   
    if ($new > $#lines+1) {
        $new = $#lines+1;
    }

    open (FILE, ">$outgoing_config");

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
}

sub delete_line($) {
    my $line = shift;
    my @lines = read_config_file($outgoing_config);
    if (! @lines[$line]) {
        return;
    }
    delete (@lines[$line]);
    save_config_file_back(\@lines);
}

sub create_line($$$$$$$$$$$$$$$$$) {

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
    my $src_port = shift;
    my $start_day = shift;
    my $end_day = shift;
    my $start_hour_min = shift;
    my $end_hour_min = shift;
    my $week = shift;

    $dest = &delete_same_data($dest);
    $mac = &delete_same_data($mac);
    $source = &delete_same_data($source);

    return "$enabled,$protocol,$source,$dest,$port,$target,$mac,$remark,$log,$src_dev,$dst_dev,$src_port,$start_day,$end_day,$start_hour_min,$end_hour_min,$week";
}
sub check_values($$$$$$$$$$$$$$) {
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
	my $start_hour_min= shift;
	my $end_hour_min = shift;
	my $start_day = shift;
	my $end_day   = shift;
	
	my @start = split(":",$start_hour_min);
	my @end =   split(":",$end_hour_min);
	
	$start_day = change_date($start_day);
	$end_day = change_date($end_day);
	my $new_start_day = dateToFilestring($start_day);
	my $new_end_day = dateToFilestring($end_day);
    my %valid_proto = ('TCP' => 1, 'UDP' => 1, 'TCP&UDP' => 1, 'OSPF' => 1, 'ESP' => 1, 'GRE' => 1, 'ICMP' => 1);
    #2013-7-27 能士项目屏蔽入侵防御
	#2014-5-6 打开入侵防御
	my %valid_targets = ( 'ACCEPT' => 1, 'ALLOW' => 1, 'DROP' => 1, 'REJECT' => 1 );
    #my %valid_targets = ( 'ACCEPT' => 1, 'DROP' => 1, 'REJECT' => 1 );
	#
    if ($protocol !~ /^$/) {
        if (! $valid_proto{uc($protocol)}) {
			push(@errormessages,  _('Invalid protocol'));
        }
    }

    foreach my $item (split(/&/, $source)) {
        if (! is_ipaddress($item)) {

			push(@errormessages, _('Invalid source IP address "%s"', $item));
        }
    }

    foreach my $item (split(/&/, $dest)) {
        if (!is_ipaddress($item)) {
			push(@errormessages, _('Invalid destination IP address "%s"',$item));
        }
    }
    foreach my $item (split(/&/, $mac)) {
        if (!validmac($item)) {
			push(@errormessages,  _('Invalid MAC address "%s"',$item));
        }
    }

    foreach my $ports (split(/&/, $port)) {
        if ($ports !~ /^(\d{1,5})(?:\:(\d{1,5}))?$/) {
			push(@errormessages,  _('Invalid destination port "%s"',$ports));
        }
        my $port1 = $1;
        my $port2 = '65535';
        if ($2) {
            $port2 = $2;
        }
    
        if (($port1 < 0) || ($port1 > 65535)) {
			push(@errormessages, _('Invalid destination port "%s"',$port1));
        }

        if (($port2 < 0) || ($port2 > 65535)) {
			push(@errormessages, _('Invalid destination port "%s"',$port2));
        }
        if ($port1 > $port2) {
			push(@errormessages,  _('The destination port range has a first value that is greater than or equal to the second value.'));
        }
    }

    if (! $valid_targets{uc($target)}) {
		push(@errormessages,  _('Invalid policy "%s"',$target));
    }
    
	if($par{'TIME_ENABLED'} eq "on")
	{
		if(($start[0]>$end[0]) || ($start[0] eq $end[0] && $start[1] > $end[1]))
		{
			push(@errormessages,  _('每日起始时间大于结束时间'));
		}
	

		if($new_end_day < $new_start_day || $new_end_day == $new_start_day){
			push(@errormessages,  _('结束日期必须大于起始日期'));
		}
	}
	
    if ($#errormessages ne -1) {
        return 0;
    }
    
    return 1;
}
sub change_date($){
	my $date = shift;
	my @t = split(/-/,$date);
	$years=$t[0];
	my $day_length = length($t[2]);
	#changed by elvis on 6.13 for month-value
	my $month_length = length($t[1]);
	if ($month_length == 1) {
		$t[1] = "0".$t[1];
		$date = "$t[0]-$t[1]-$t[2]";
	}
	#end
	if ($day_length == 1) {
		$t[2] = "0".$t[2];
		$date = "$t[0]-$t[1]-$t[2]";
	}
	return $date;
}
sub save_line($$$$$$$$$$$$$$$$$$) {
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
	
	
	##-----------------------------
	#包过滤添加字段 2012-02-28 周圆
	my $start_day = shift;
	my $end_day = shift;
	my $week = shift;
	$week =~ s/\|/:/g;
	
	my $start_hour_min = shift;
	my $end_hour_min = shift;
	##------------------------------
    my $src_port = shift;

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
    $src_port =~ s/\n/&/gm;
    $src_port =~ s/\r//gm;
    $src_port =~ s/\-/:/g;

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
    if (! check_values($enabled, $protocol, $source, $dest, $port, $target, $mac,$log, $src_dev, $dst_dev,$start_hour_min,$end_hour_min,$start_day,$end_day)) {
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
    my $tosave = create_line($enabled, $protocol, $source, $dest, $port, $target, $mac, $remark, $log, $src_dev, $dst_dev,$src_port,$start_day,$end_day,$start_hour_min,$end_hour_min,$week);
    
    foo("save-line:$line\n");
    if ($line !~ /^\d+$/) {
        append_config_file($tosave);
        return 1;
    }
    my @lines = read_config_file($outgoing_config);
    if (! $lines[$line]) {
        push(@errormessages, _('Configuration line not found!'));
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
sub format_line($$$$$$$$$$$$$$$$$$) {
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
    
    my $ret_string = "";
	
	
	##-----------------------------
	#包过滤添加字段 2012-02-28 周圆
	my $start_day = shift;
	my $end_day = shift;
	my $week = shift;
	$week =~ s/\|/:/g;
	
	my $start_hour_min = shift;
	my $end_hour_min = shift;
	##------------------------------
    my $src_port = shift;

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
    $src_port =~ s/\n/&/gm;
    $src_port =~ s/\r//gm;
    $src_port =~ s/\-/:/g;

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
    if (! check_values($enabled, $protocol, $source, $dest, $port, $target, $mac,$log, $src_dev, $dst_dev,$start_hour_min,$end_hour_min,$start_day,$end_day)) {
        return "";
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
	
    $ret_string = create_line($enabled, $protocol, $source, $dest, $port, $target, $mac, $remark, $log, $src_dev, $dst_dev,$src_port,$start_day,$end_day,$start_hour_min,$end_hour_min,$week);
    
    return $ret_string;
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
            push(@addr_values, "<font color='". $zonecolors{'RED'} ."'>"._('Uplink')." ".$ul->{'description'}."</font>");
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
            <td class="boldbase" >#</td>
            <td class="boldbase" >%s</td>
            <td class="boldbase" >%s</td>
            <td class="boldbase" >%s</td>
            <td class="boldbase" >%s</td>
			<td class="boldbase" >时间段</td>
			<td class="boldbase" >每周</td>
			<td class="boldbase" >每天时间段</td>
            <td class="boldbase" >%s</td>
            <td class="boldbase" >%s</td>
            <td class="boldbase" >%s</td>
END
    , _('Source')
    , _('源端口')
    , _('Destination')
    , _('Service')
    , _('Policy')
    , _('Remark')
    , _('命中数')
    ;
    if ($editable) {
        printf <<END
        <td class="boldbase" width="23%">%s</td>
END
        , _('Actions')
        ;
    }
    printf <<END
    </tr>
END
    ;
    my $hits = `$excute_cmd -s`;

    my $hits_hash = $json->decode($hits);
    
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
			#2013-7-27 能士项目屏蔽入侵防御 修改默认图标
			#2014-5-6 打开入侵防御 修改图标
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

            my $log = '';
            if ($splitted{'log'} eq 'on') {
                $log = _('yes');
            }
            my $mac = $splitted{'mac'};
            my $src_port = $splitted{'src_port'};
            if (!$src_port) {
                $src_port = "&lt;"._('ANY')."&gt;";
            }
            my $bgcolor = setbgcolor($is_editing, $line, $i);
            my $dest_long_value = generate_addressing($destination, $dst_dev, '', $i);
            if ($dest_long_value =~ /(?:^|&)ANY/) {
                $dest_long_value = "<font color='". $zonecolors{'RED'} ."'>".$strings_zone{'RED'}."</font>";
            }
            my $src_long_value = generate_addressing($source, $src_dev, $mac, $i);
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
            <td>$num</td>
            <td>$src_long_value</td>
            <td>$src_port</td>
            <td>$dest_long_value</td>
            <td>$service_long_value</td>
EOF
;
if($splitted{'start_day'} && $splitted{'end_day'})
{
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
			
			
            <td><IMG SRC="$policy_gif" ALT="$policy_alt" TITLE="$policy_alt"></td>
            <td>$remark</td>
            <td>$hits_hash->{$i}</td>
EOF
            ;

            if ($editable) {
                printf <<EOF
            <td class="actions">    
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
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left" onsubmit="return confirm('确认删除?')">
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
;
if($i eq 0)
{
	no_tr(11,"无内容");
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
            <td CLASS="boldbase"><b>%s</b>
            <IMG SRC="$ENABLED_PNG" ALT="%s" />
            %s
            <IMG SRC='$DISABLED_PNG' ALT="%s" />
            %s
            <IMG SRC="$EDIT_PNG" alt="%s" />
            %s
            <IMG SRC="$DELETE_PNG" ALT="%s" />
            %s
        </tr>
    </table>
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
            var sswitch = new ServiceSwitch('/cgi-bin/outgoingfw.cgi', SERVICE_STAT_DESCRIPTION);
        });
    </script>

    <form enctype='multipart/form-data' class="service-switch-form" id="ssh-form" method='post' action='$ENV{'SCRIPT_NAME'}' >
    <input type="hidden" class="service-status" name="POLICY" value="$service_satus" />

    <table cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td >
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
    escape_quotes(_("The Outgoing firewall is being activated. Please hold...")),
    escape_quotes(_("The Outgoing firewall is being deactivated. Please hold...")),
    escape_quotes(_("Settings are being applied. Please hold...")),
    _('启用流出防火墙'),
    $service_status eq 'on' ? 'hidden' : '',
    _("Use the switch above to enable the Outgoing firewall.<br />The Outgoing firewall gives the ability to globally DENY Outgoing traffic and explicitly configure Outgoung firewall rules."),
    _("The Outgoing firewall is being disabled. Please hold..."),
    $service_status eq 'off' ? 'hidden' : '',
    _('Log accepted outgoing connections'),
    _('Save'),
    $service_status eq 'off' ? 'hidden' : '',
    ;
    display_rules($is_editing, $par{'line'});

    print "</div></div>";
}

sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;

    # my %checked;
    # $checked{'LOG_ACCEPTS'}{$log_accepts} = 'checked = checked';

    #&openbox('100%', 'left', _('Current rules'));
    my $updateTime  = `$excute_cmd -t`;
    my $ruleMsg = `$excute_cmd -c`;
    chomp($ruleMsg);
    display_add($is_editing, $line);
    printf <<EOF
    <div style="margin: 20px;background-image: url(../images/con-header-bg.jpg);height: 25px;line-height: 25px;">
      <span><input type="button" value="规则检查" onclick="warning_box('$ruleMsg')"></span> <span class="updateTime">&nbsp;&nbsp;后台数据更新时间：$updateTime</span>
    </div>
EOF
;
    generate_rules($outgoing_config, $is_editing, $line, 1);
	my $sys_length = count_sys_rules(getConfigFiles($confdir), 0, 0, 0);
if($sys_length >0)
{
    printf <<EOF

<div class="show_sys"><b>%s</b>&nbsp;&nbsp;<b><input onclick="swapVisibility('systemrules')" value=" &gt;&gt; " type="button"></b></div>
EOF
, _('Show system rules')
;
    #&closebox();

    print "<div id=\"systemrules\" style=\"display: none\">\n<br />";
    #&openbox('100%', 'left', _('Rules automatic configured by the system'));
    generate_rules(getConfigFiles($confdir), 0, 0, 0);
    print "</div><br /><br /><br />";
    #&closebox();
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
		$proto =~ s/\r//g;
		$proto =~ s/\n//g;
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

    my $enabled = $config{'enabled'};
    my $target = $config{'target'};
    if (! $target) {
	    #2013-7-27 能士项目屏蔽入侵防御 修改默认为ACCEPT
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
    my $dst_type = 'any';
    my $src_port = $config{'src_port'};
    $src_port =~s /&/\n/g;
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

    # if ("$par{'line'}" eq "") {
    #     # if no line set last line
    #     #print "BIO";
    #     #$line = $line_count -1;
    # }

    my $src_dev_size = int((length(%$deviceshash) + $#nets) / 3);
    if ($src_dev_size < 3) {
       $src_dev_size = 3;
    }
    my $dst_dev_size = $src_dev_size;

    my $addoredit = "添加规则";
    my $action = 'add';
    my $sure = '';
    my $title = _('Outgoing firewall rule editor');
    my $button = _("Create rule");

    if ($is_editing) {
        $action = 'edit';
        my $sure = '<INPUT TYPE="hidden" NAME="sure" VALUE="y">';

        $addoredit = "编辑规则";
        #my $title = _('Edit Outgoing firewall rule');
        $button = _("编辑规则");
        $show = "showeditor";
    }
    else {
        $show = "";
    }
    #&openbox('100%', 'left', $title);
    openeditorbox($addoredit, $title, $show, "createrule",);
    printf <<EOF
                <!-- begin source -->
                </form>
                <form name="OUTGOING_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr class="env" ><td class="add-div-type" rowspan="1"><b>%s</b></td>
                        <td >%s *&nbsp;&nbsp;
                            <select name="src_type" onchange="toggleTypes('src');" onkeyup="toggleTypes('src');">
                                <option value="any" $selected{'src_type'}{'any'}>&lt;%s&gt;</option>
                                <option value="dev" $selected{'src_type'}{'dev'}>%s</option>
                                <option value="ip" $selected{'src_type'}{'ip'}>%s</option>
                                <option value="mac" $selected{'src_type'}{'mac'}>%s</option>
                            </select>
                        </td>
                        <td colspan="1">
                            <div id="src_any_t" style="display:$foil{'title'}{'src_any'}">%s</div>
                            <div id="src_dev_t" style="display:$foil{'title'}{'src_dev'}">%s</div>
                            <div id="src_ip_t" style="display:$foil{'title'}{'src_ip'}">%s</div>
                            <div id="src_mac_t" style="display:$foil{'title'}{'src_mac'}">%s</div>
                            <div id="src_any_v" style="display:$foil{'value'}{'src_any'}" style="width: 250px; height: 90px;">&nbsp;</div>
EOF
    , _('Source')
    , _('Type')
    , _('ANY')
    , _('Zone/Interface')
    , _('Network/IP')
    , _('MAC')
    , _('This rule will match any source')
    , _('Select interfaces (hold CTRL for multiselect)')
    , _('Insert network/IPs (one per line)')
    , _('Insert MAC addresses (one per line)')
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
                        <td><div>源端口(每行一个)</div><div><textarea name="src_port" wrap='off' style="width: 250px; height: 90px;">$src_port</textarea></div></td>
                    </tr>
                <!-- end source field -->
           
            <!-- begin destination -->
                    <tr class="odd"><td class="add-div-type" rowspan="1"><b>%s</b></td>
                        <td >%s *&nbsp;&nbsp;
                            <select name="dst_type" onchange="toggleTypes('dst');" onkeyup="toggleTypes('dst');">
                                <option value="any" $selected{'dst_type'}{'any'}>&lt;%s&gt;</option>
                                <option value="dev" $selected{'dst_type'}{'dev'}>%s</option>
                                <option value="ip" $selected{'dst_type'}{'ip'}>%s</option>
                            </select>
                        </td>
                        <td  colspan="2">
                            <div id="dst_any_t" style="display:$foil{'title'}{'dst_any'}">%s</div>
                            <div id="dst_dev_t" style="display:$foil{'title'}{'dst_dev'}">%s</div>
                            <div id="dst_ip_t" style="display:$foil{'title'}{'dst_ip'}">%s</div>
                            <div id="dst_any_v" style="display:$foil{'value'}{'src_any'}" style="width: 250px; height: 90px;">&nbsp;</div>
EOF
    , _('Destination')
    , _('Type')
    , _('RED')
    , _('Uplink')
    , _('Network/IP')
    , _('This rule will match the entire RED')
    , _('Select uplink')
    , _('Insert network/IPs (one per line)')
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
    foreach my $ref (@{get_uplinks_list()}) {
	my $name = $ref->{'name'};
	my $key = $ref->{'dev'};
	my $desc = $ref->{'description'};
        printf <<EOF 
                                    <option value='$key' $selected{'dst_dev'}{$key}>$desc</option>
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
                <b>%s</b></td>
            <td >%s *
                            <select name="service_port" onchange="selectService('protocol', 'service_port', 'port');" onkeyup="selectService('protocol', 'service_port', 'port');">
                                <option value="any/any">&lt;%s&gt;</option>
EOF
    , _('目的服务/端口')
    , _('Service')
    , _('ANY')
    ;
    my ($sel, $arr) = create_servicelist($protocol, $config{'port'});
    print @$arr;

# check if ports should be enabled
    if ($protocol eq "" || $protocol eq "any") {
        $portsdisabled = 'disabled="disabled"';
    }
	my $isdisplay = "class='hidden_class'";
	if($port ne "")
	{
		$isdisplay = "";
	}
    printf <<EOF
                            </select>
                        </td>
                        <td >%s *
                            <select name="protocol" id="protocol_a" onchange="updateService('protocol', 'service_port', 'port');" onkeyup="updateService('protocol', 'service_port', 'port');">
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
EOF
    , _('Protocol')
    , _('ANY')
;

printf <<EOF
                        <td>
						<ul id="port_ul" $isdisplay><li>%s</li>
                            <li><textarea name="port" rows="3" $portsdisabled onkeyup="updateService('protocol', 'service_port', 'port');">$port</textarea></li>
						</ul>
EOF
, _('目的地端口(每行一个)')
;

printf <<EOF
				<ul id="port_ul2" ><li>%s</li></ul>
EOF
,_('This rule will match all the destination ports')
;

my @cur_line;
my $time_enabled = "";
my $time_display = "none";
if($par{'line'} ne '')
{
	my $cur_line = read_config_line($par{'line'});
    @cur_line = split(",",$cur_line);
	if($cur_line[12])
	{
		$time_display = "table";
		$time_enabled = "checked='checked'";
	}
}


printf <<EOF
                        </td>
                    </tr>

  
        <tr class="odd">
            <td class="add-div-type" rowspan="1">
                <b>%s *</b></td>
			<td colspan="3">%s&nbsp;
                    <select name="target">
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
                <input name="remark" value="$remark" size="50" maxlength="50" type="text">
            </td>
		</tr>
		
		<tr class="odd">
            <td colspan="3">%s *&nbsp;
                            <select name="position">
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
                    <tr class="odd">
                        <td colspan="3"><input name="enabled" value="on" $checked{'ENABLED'}{'on'} type="checkbox">%s</td>
                    </tr>
					<tr class="odd">
                        <td  colspan="3"><input name="log" value="on" $checked{'LOG'}{'on'} type="checkbox">%s</td>
                    </tr>

        <input type="hidden" name="ACTION" value="$action">
        <input type="hidden" name="line" value="$line">
        <input type="hidden" name="sure" value="y">
    </table>
EOF
    , _('Enabled')
    , _('Log all accepted packets')
    ;
    
    &closeeditorbox($button, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
    #&closebox();
}

sub reset_values() {
    %par = ();
    $par{'POLICY'} = $policy;
    $par{'LOG_ACCEPTS'} = $log_accepts;
}


sub save() {
    my $action = $par{'ACTION'};
    my $log_message="";
    my $sure = $par{'sure'};
    if ($action eq 'apply') {
        system($setoutgoing);				
		`sudo fcmd $setoutgoing`;
        $notemessage = _("Firewall rules applied successfully");
        $log_message = "应用了流出防火墙规则";
        &user_log($log_message);
        return;
    }
    if ($action eq 'save') {
        set_policy();
        reset_values();
        system($setoutgoing);		
		`sudo fcmd $setoutgoing`;
        $log_message = "修改了流出防火墙配置";
        &user_log($log_message);
        return;
    }
    if ($action eq 'up') {
        move($par{'line'}, -1);
        my $rule_num = $par{'line'} + 1;
        $log_message = "将第$rule_num条流出防火墙规则上移1";
        &user_log($log_message);
        reset_values();
        return;
    }
    if ($action eq 'down') {
        move($par{'line'}, 1);
        my $rule_num = $par{'line'} + 1;
        $log_message = "将第$rule_num条流出防火墙规则下移1";
        &user_log($log_message);
        reset_values();
        return;
    }
    if ($action eq 'delete') {
        delete_line($par{'line'});
        my $rule_num = $par{'line'} + 1;
	    $log_message = "删除第$rule_num条流出防火墙规则";
        &user_log($log_message);		
        reset_values();
        return;
    }

    if ($action eq 'enable') {
        #----------------------------------
        #冲突提示代码添加-2013-04-17-squall
        
	
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
            $log_message = "启用第$rule_num条流出防火墙规则";
            &user_log($log_message);
            reset_values();
            return;
        }
    }
    if ($action eq 'disable') {
        if (toggle_enable($par{'line'}, 0)) {
            my $rule_num = $par{'line'} + 1;
            $log_message = "禁用第$rule_num条流出防火墙规则";
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
	
	
	#	#----------------------------------
        #冲突提示代码添加-2013-04-17-squall
        
        #获取格式化的line string
		my $current_line = format_line($par{'line'},
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
                                      $dst_dev,
               					   $par{'START_DAY'},
               					   $par{'END_DAY'},
               					   $par{'WEEK'},
               					   $start_hour_min,
               					   $end_hour_min,
                                      $par{'src_port'});
        
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
        my $old_line = read_config_line($par{'line'});
		
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
                      $dst_dev,
					  $par{'START_DAY'},
					  $par{'END_DAY'},
					  $par{'WEEK'},
					  $start_hour_min,
					  $end_hour_min,
                      $par{'src_port'})) {
            if ($par{'line'} ne $par{'position'}) {
                if ("$old_pos" eq "") {
                    $old_pos = line_count()-1;
                }
                if (line_count() > 1) {
                    set_position($old_pos, $par{'position'});
                }
            }
            ####进行对比检测，查看修改的项目

            my $src_value = $src_dev.$src;
            my $dst_value = $dst_dev.$dst;
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
            my $new_line = "$src_value,$dst_value,$enabled,$proto,$par{'port'},$par{'src_port'},$par{'target'},$remark,$par{'log'},$times,$week,$pos";
            my $message = "源,目的,启用状态,协议,端口,源端口,动作,注释,记录日志,启用时间,周,规则位置";
            if ($action eq 'add') {                
                $log_message = "添加了流出防火墙规则，";
                $log_message .= build_rule($new_line,$message);
                &user_log($log_message);
            }
            if (($action eq 'edit')&&($sure eq 'y')) {    
                my @tmp = split(/,/,$old_line);
                my $src_value = $tmp[2].$tmp[6].$tmp[9];  
                my $dst_value = $tmp[3].$tmp[10]; 
                my $times =  "$tmp[12] $tmp[14] -> $tmp[13] $tmp[15]";
                my $week = $tmp[16];  
                $src_value =~s/&/\|/g;
                $dst_value =~s/&/\|/g;
                $tmp[14] =~s/:/\|/g; 
                if (!$tmp[0]) {
                    $tmp[0] = "off";
                }                
                if (!$tmp[7]) {
                    $tmp[7] = "空";
                }
                if (!$tmp[8]) {
                    $tmp[8] = "off";
                }
                if (!$tmp[12]) {
                    $times = "未启用";
                    $week = "未启用";
                }    
                my $old_value = "$src_value,$dst_value,$tmp[0],$tmp[1],$tmp[4],$tmp[11],$tmp[5],$tmp[7],$tmp[8],$times,$week,$lined";
                $log_message = "修改了第$lined条流出防火墙规则，";
                $log_message .= check_change($old_value,$new_line,$message);
                &user_log($log_message);
            }
            reset_values();
        }

    }
}

&getcgihash(\%par);
$policy = $outgoing{'POLICY'};
if ($policy eq "ALLOW") {
    $service_status = "off";
}
else {
    $service_status = "on";
}
$log_accepts = $outgoing{'LOG_ACCEPTS'};

&showhttpheaders();


my $extraheader = '<script language="JavaScript" src="/include/firewall_type.js"></script>
<script language="JavaScript" src="/include/services_selector.js"></script>
<script type="text/javascript" src="/include/serviceswitch.js"></script>
<script type="text/javascript" src="/include/ESONCalendar.js"></script>
<script type="text/javascript" src="/include/conflict_detection.js"></script>
<link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />';


&openpage(_('Outgoing firewall'), 1, $extraheader);


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
&check_form();
&closepage();
