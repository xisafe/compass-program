#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:qos设备获取
#
# AUTHOR: 张征 (zhangzheng), elviszhang2010@gmail.com
# COMPANY: great.chinark
# CREATED: 2011/11/29-10:00
#===============================================================================
use strict;
use warnings;

require '/var/efw/header.pl';
my $green_file = "/var/efw/ethernet/br0";
my $orange_file = "/var/efw/ethernet/br1";
my $blue_file = "/var/efw/ethernet/br2";
my $uplinkdir = "/var/efw/uplinks/";
my $openvpn = "/var/efw/openvpn/settings";
my $openvpnclient = "/var/efw/openvpnclients/";
my $ipsec = "/var/efw/vpn/config";
my %main_hash;
my %uplink_hash;


sub read_config_file($) {
    my @lines;
	my $file=shift;
    open (FILE,"$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}
sub read_dir($){
	my $dir = shift;
	my @dirs;
	opendir(DIR,"$dir");
	@dirs = readdir(DIR);
	close(DIR);
	return @dirs;
} 
&readhash($uplinkdir."main/settings",\%main_hash);
my @green_dev = read_config_file($green_file);
my @orange_dev = read_config_file($orange_file);
my @blue_dev = read_config_file($blue_file);
my $orange_num = @orange_dev;
my $blue_num = @blue_dev;
my $ipsec_all = `ifconfig |grep ipsec`;
my @ipsec_tmp=split(/\n/,$ipsec_all);
my @ipsecs;
foreach my $elem (@ipsec_tmp) {
	$elem =~/^(ipsec\d+) /;
	push (@ipsecs,$1);
}
my %vpn;
my %vpnclient;
my @vpnclients;
my @ipsecname;
my @ipsecline=read_config_file($ipsec);
foreach my $line (@ipsecline) {
	chomp($line);
	if ($line) {
		my @tmp  = split(/,/,$line);
		push (@ipsecname,$tmp[2]);
	}
}
if (-e $openvpn) {
	&readhash($openvpn,\%vpn);
}
foreach my $vpnclientdir (read_dir($openvpnclient)) {
	chomp($vpnclientdir);
	if (($vpnclientdir !~/^\./) && ($vpnclientdir ne "default") && ($vpnclientdir ne "empty")) {
		push(@vpnclients,$vpnclientdir);
	}
}

sub ethname(){
	my @eth_num = `ifconfig|grep -E "^eth" | awk '{print $1}'`;
	my $tap_num = `ifconfig|grep -E "^tap[0-9]+[^:^\.]"|wc -l`;
	my $ipsec_num = `ifconfig|grep -E "^ipsec[0-9]+[^:^\.]"|wc -l`;	
	my $pppoe_num = `ifconfig|grep -E "^ppp[0-9]+[^:^\.]"|wc -l`;
	my %ethernet=("GREEN" =>_('GREEN'),);
	if ($orange_dev[0]) {
		$ethernet{"ORANGE"} = _('ORANGE');
	}
	if ($blue_dev[0]) {
		$ethernet{"BLUE"} = _('BLUE');
	}
	if ($tap_num >0) {
		if ($vpn{'PURPLE_DEVICE'} && $vpn{'OPENVPN_ENABLED'} eq "on") {
			$ethernet{"$vpn{'PURPLE_DEVICE'}"} = "SSLVPN_服务器";
		}
		foreach my $elem (@vpnclients) {
			my $client_file = $openvpnclient."$elem/settings";
			if(-e $client_file){
				&readhash($client_file,\%vpnclient);
			}
			$ethernet{"$vpnclient{'DEVICE'}"} = "SSLVPN[$elem]";
		}

	}
	foreach my $eth (@eth_num) {
		$eth =~ /eth(\d+)/;
		my $j = $1 + 1;
		$ethernet{"PHYSDEV:eth".$1} = "接口".$j;
	}
	if (($ipsec_num > 0) &&(-e $ipsec) &&(@ipsecline >0)) {
		for (my $i = 0;$i<@ipsecs ;$i++) {
			$ethernet{$ipsecs[$i]} = "IPSEC_$ipsecname[$i]";
		}
	}
	if ($pppoe_num > 0) {
		my $temp_line = `grep -R  "ppp" $uplinkdir`;
		my @temp = split(/\n/,$temp_line);
		foreach my $elem (@temp) {
			if($elem =~/$uplinkdir(.*)\/data:/){
				my $dir = $1;
				my %data_hash;
				&readhash($uplinkdir."$dir/settings",\%uplink_hash);
				&readhash($uplinkdir."$dir/data",\%data_hash);
				if($dir eq "main"){
					$uplink_hash{'NAME'} = "main";
				}
				$ethernet{$data_hash{'interface'}}="PPPOE_$uplink_hash{'NAME'}";
			}
		}
	}
	foreach my $key (keys %ethernet) {
		if ($key =~/PHYSDEV:(.*)/) {
			my $eth_dev = $1;
			foreach my $elem (@green_dev) {
				if ($eth_dev eq $elem) {
					$ethernet{$key} .= "_"._('GREEN');
				}
			}
			foreach my $elem (@orange_dev) {
				if ($eth_dev eq $elem) {
					$ethernet{$key} .= "_"._('ORANGE');
				}
			}
			if ($eth_dev eq $main_hash{'RED_DEV'}) {
				$ethernet{$key} .= "_"._('Main uplink');
			}
			foreach my $dir (read_dir($uplinkdir)) {
				chomp($dir);
				my $flag = 0;
				if (-e $uplinkdir."$dir/settings"){
					$flag = 1;
				}
				if ($dir !~/^\./ && $dir && $dir ne "main" && $flag) {
					if(-e $uplinkdir."$dir/settings"){
						&readhash($uplinkdir."$dir/settings",\%uplink_hash);
					}					
					if ($eth_dev eq $uplink_hash{'RED_DEV'}) {					    
						$ethernet{$key} .= "_$uplink_hash{'NAME'}";						
					}
				}
			}
		}
	}
	return \%ethernet;
}

1;