#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2011-07-25

require '/var/efw/header.pl';
use CGI();
use URI::Escape;
&validateUser();
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my @src_ips = split(/=/, $parValue[0]);
my $src_ip  = uri_unescape($src_ips[1]);
$src_ip     =~ s/\+/ /g;

my @types = split(/=/, $parValue[1]);
my $type  = uri_unescape($types[1]);
$type     =~ s/\+/ /g;

my @sorts = split(/=/, $parValue[2]);
my $sort  = uri_unescape($sorts[1]);
$sort     =~ s/\+/ /g;

my @indexs = split(/=/, $parValue[3]);
my $index  = uri_unescape($indexs[1]);
$index     =~ s/\+/ /g;


my @up_or_downs = split(/=/, $parValue[4]);
my $up_or_down  = uri_unescape($up_or_downs[1]);
$up_or_down     =~ s/\+/ /g;

if($up_or_down eq "up_to_down")
{
	$up_or_down  = "-r";
}else{
	$up_or_down  = "";
}


if($type ne "")
{
	$type = ' -p '.$type;
}
my $detail = "";
my $cmd_percent = "";

#百分比例图数据需要执行的命令
if($sort ne "sort")
{
	$cmd_percent = 'sudo conntrack -L -s '.$src_ip.' '.$type.' |sort +2 -n -r';
	#print $cmd_percent;
	$detail = `$cmd_percent`;
}else{
	$cmd_percent = 'sudo conntrack -L -s '.$src_ip.' '.$type.' |sort -t= +'.$index.' -g '.$up_or_down;
	#print $cmd_percent;
	$detail = `$cmd_percent`;
}
#print $cmd_percent;
print $detail;


