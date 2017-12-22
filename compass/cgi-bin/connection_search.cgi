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
&validateUser();
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my @starts = split(/=/, $parValue[0]);
my $start = uri_unescape($starts[1]);
$start =~ s/\+/ /g;
my $page = $start;


my @ips = split(/=/, $parValue[1]);
my $ip = uri_unescape($ips[1]);
$ip =~ s/\+/ /g;

#print $ip;
#定义页面每页显示的连接数
my $per_page = 10;


#按连接数从高到低的得到源IP
my $ip_dst_cmd ='sudo conntrack -L -d '.$ip.' | grep -o -P "src=\d\S+"|sed -n "p;n" |grep -o -P "\d\S+"|sort |uniq -c|sort -r ';
my $ip_output = `$ip_dst_cmd`;

#print $ip_output;
my @temp_ip = split('\n',$ip_output);
my @temp;
my $i = 0;
my $src_cmd = 'sudo conntrack -L -s '.$ip.'|wc -l';
my $src_out = `$src_cmd`;
push(@temp,$ip.",".$src_out);

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
my $cmd_count = @temp_ip;
my $count_ip;
if(($cmd_count+1)%$per_page == 0)
{
	$count_ip = int(($cmd_count+1)/$per_page)."=";
}else{
	$count_ip = int((($cmd_count+1)/$per_page)+1)."=";
}

#输出有几页
print $count_ip;

foreach my $src_ip(@temp)
{
	my @temp         = split(",",$src_ip);
	my $cmd_tcp      = 'sudo conntrack -L -s '.$temp[0].' -p tcp |wc -l';
	my $cmd_udp      = 'sudo conntrack -L -s '.$temp[0].' -p udp |wc -l';
	my $cmd_icmp     = 'sudo conntrack -L -s '.$temp[0].' -p icmp |wc -l';
	my $tcp_output   = `$cmd_tcp`;
	my $udp_output   = `$cmd_udp`;
	my $icmp_output  = `$cmd_icmp`;
	my $other_output = $temp[1]-$tcp_output-$udp_output-$icmp_output;
	print $src_ip.",".$tcp_output.",".$udp_output.",".$icmp_output.",".$other_output."=";
}






