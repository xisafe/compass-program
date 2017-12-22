#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 网络状态页面AJAX 刷新
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================



require '/var/efw/header.pl';
require '/home/httpd/cgi-bin/netstatus.pl';
require '/home/httpd/cgi-bin/ethconfig.pl';

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";


my $green_class="class='odd_thin green bold' style='background-color:#e8f5d9;cursor:pointer;'";
my $orange_class="class='odd_thin orange bold' style='background-color:#fef6d1;cursor:pointer;'";
my $red_class="class='odd_thin red bold' style='background-color:#f6d7d3;cursor:pointer;'";
my $blue_class="class='odd_thin  bold' style='background-color:#c8e6ed;color:#2898c2;cursor:pointer;'";
readhash("/var/efw/console/settings",\%console);
my $interface_number = `ifconfig |grep eth |wc -l`;
my $enabled = "on";
if($console{"ENABLED"} eq "off" || $console{"ENABLED_NUMBER"} > $interface_number ){
	$enabled = "off";
}

display();
my $eth_class="class='odd_thin  bold' ";
my $eth_num = `ls -l  /sys/class/net/|grep "eth*"|wc -l`;
if ($enabled eq 'on') {
	get_interface('(管理口)','eth0',$eth_class,"");
}
get_interface(_('GREEN')."接口","br0",$green_class,"greens");
get_interface_sub("br0","greens",$green_class);
get_interface(_('ORANGE')."接口","br1",$orange_class,"oranges");
get_interface_sub("br1","oranges",$orange_class);
get_interface(_('BLUE')."接口","br2",$blue_class,"blue");
get_interface_sub("br2","blue",$blue_class);
get_red_interface($red_class);
my @eth_more = get_more_eth();
foreach my $eth(@eth_more)
{
    #2013-7-5 屏蔽gre mast开头的接口显示
    if($eth=~/^gre/||$eth=~/^mast/)
	{
	   next;
	}
	#
	if($eth =~ /tap/)
	{
		my $class="class='odd_thin  bold' style='color:#f451fe;'";
		get_interface('',$eth,$class,"");
	}elsif($eth =~ /ipsec/)
	{
		my $class="class='odd_thin  bold' style='color:#5c0f75;'";
		get_interface('',$eth,$class,"");
	}elsif($eth =~ /ppp/)
	{
		my $class="class='odd_thin  bold' style='color:#0f756f;'";
		get_interface('',$eth,$class,"");
	}
}

my %all_eth = get_all_eth();
delete ($all_eth{'lo'});

foreach my $temp_eth(keys %all_eth)
{
	foreach my $up_eth(keys %up_eth)
	{
		if($up_eth eq $temp_eth)
		{
			 delete ($all_eth{$temp_eth});
		}
	}
}

foreach my $temp_eth(keys %all_eth)
{
	my $class="class='odd_thin  bold' style='color:#666;background-color:#ddd;cursor:pointer;'";
	#2013-7-5 屏蔽gre mast开头的接口显示
	if($temp_eth=~/^gre/||$temp_eth=~/^mast/)
	{
	   next;
	#
	} else {
	   get_interface('(不可达)',$temp_eth,$class,"");
	}
}

print '<tr class="table-footer"><td colspan="6">&nbsp;</td></tr></table>';

