#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2011-07-25
#
#modify:2011-07-29

require '/var/efw/header.pl';
use CGI();
use URI::Escape;

my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my @starts = split(/=/, $parValue[0]);
my $start = uri_unescape($starts[1]);
$start =~ s/\+/ /g;
my $page = $start;

#定义页面每页显示的连接数
my $per_page = 10;

#存放临时的连接ip的文件路径
#my $tmp_conf = "/tmp/connection_ip";

#统计当前有多少种连接(按源IP统计)
my $count_cmd = 'sudo  conntrack -L | grep -o -P "src=\S+" | sed -n "p;n"|grep -o -P "\d\S+"|sort -u |wc -l';
my $cmd_count = `$count_cmd`;
my $count_ip = "";
&validateUser();
if($cmd_count%$per_page == 0)
{
	$count_ip = int($cmd_count/$per_page)."=";
}else{
	$count_ip = int(($cmd_count/$per_page)+1)."=";
}

#输出有几页
print $count_ip;


#按连接数从高到低的得到源IP
my $ip_cmd ='sudo  conntrack -L | grep -o -P "src=\d\S+"|sed -n "p;n"|grep -o -P "\d\S+" | sort |uniq -c| sort -r -g';

my $ip_output = `$ip_cmd`;

my @temp_ip = split('\n',$ip_output);
my @temp;
my $i = 0;
foreach my $ip(@temp_ip)
{
	#print $ip;
	if($i<$page*$per_page && ($page-1)*$per_page<=$i)
	{
		$ip =~ /(\d+) +(\d+\.\d+\.\d+\.\d+)/;
		push(@temp,$2.",".$1);
	}	
	$i++;
}

foreach my $src_ip(@temp)
{
	my @temp         =split(",",$src_ip);
	my $cmd_tcp      = 'sudo conntrack -L -s '.$temp[0].' -p tcp |wc -l';
	my $cmd_udp      = 'sudo conntrack -L -s '.$temp[0].' -p udp |wc -l';
	my $cmd_icmp     = 'sudo conntrack -L -s '.$temp[0].' -p icmp |wc -l';
	my $tcp_output   = `$cmd_tcp`;
	my $udp_output   = `$cmd_udp`;
	my $icmp_output  = `$cmd_icmp`;
	my $other_output = $temp[1]-$tcp_output-$udp_output-$icmp_output;
	if($other_output < 0)
	{
		$other_output = 0;
	}
	print $src_ip.",".$tcp_output.",".$udp_output.",".$icmp_output.",".$other_output."=";
}






