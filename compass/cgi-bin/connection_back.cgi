#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2011-07-25

require '/var/efw/header.pl';
use CGI();
use URI::Escape;

#my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";


#my @starts = split(/=/, $parValue[0]);
#my $start = uri_unescape($starts[1]);
#$start =~ s/\+/ /g;
#print $start;
#$start = $start+3;

#百分比例图数据需要执行的命令
my $cmd_percent = `sudo conntrack -C&&sudo conntrack -L -p tcp | wc -l && sudo conntrack -L -p udp | wc -l&&sudo conntrack -L -p icmp | wc -l`;

my @temp_array = split("\n",$cmd_percent);
my $input;
my @arry;
&validateUser();
foreach my $str(@temp_array)
{
	if($str =~ /^\d+$/)
	{
		$input .= $str."=";
		push(@arry,$str);
	}
}
my $other = $arry[0]-$arry[1]-$arry[2]-$arry[3];
print $input.$other;


