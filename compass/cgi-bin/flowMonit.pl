#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 流量监控头文件
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================

require '/var/efw/header.pl';


%time = (
				"ts" => "0_及时",
				"fm" => "1_5分钟",
				"hh" => "2_30分钟",
				"th" => "3_2小时",
				"od" => "4_24小时",
				"ow" => "5_一周"
		);
%type = (
				"service" => "基于服务的统计",
				"pro"     => "基于协议的统计"
);

			
#获取所有网络接口
sub get_eth()
{
	my @all_hash;
	my $green  = `cat /var/efw/ethernet/br0`;
	my $orange = `cat /var/efw/ethernet/br1`;
	my $blue   = `cat /var/efw/ethernet/br2`;

	if($green =~ /eth/)
	{
		my @green_eth = split("\\n",$green);
		foreach my $eth(@green_eth)
		{
			push(@all_hash,$eth);
		}
	}
	
	if($orange =~ /eth/)
	{
		my @orange_eth = split("\\n",$orange);
		foreach my $eth(@orange_eth)
		{
			push(@all_hash,$eth);
		}
	}
	
	if($blue =~ /eth/)
	{
		my @blue_eth = split("\\n",$blue);
		foreach my $eth(@blue_eth)
		{
			push(@all_hash,$eth);
		}
	}
	
	my $temp_cmd = `ip a`;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
		{
			$eth = $1;
			if($eth =~ /^ipsec/ || $eth =~ /^tap/)
			{
				push(@all_hash,$eth);
			}
		}
	}
	return @all_hash;
}

#获取当前启用的区域
sub get_zone()
{
	my %zone;
	my $green  = `cat /var/efw/ethernet/br0`;
	my $orange = `cat /var/efw/ethernet/br1`;
	my $blue   = `cat /var/efw/ethernet/br2`;
	if($green=~ /eth/)
	{
		$zone{'br0'} = _('GREEN')."区域";
	}
	if($orange=~ /eth/)
	{
		$zone{'br1'} = _('ORANGE')."区域";
	}
	if($blue=~ /eth/)
	{
		$zone{'br2'} = _('BLUE')."区域";
	}
	return %zone;
}

1;