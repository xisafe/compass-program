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
if($type ne "")
{
	$type = ' -p '.$type;
}
#百分比例图数据需要执行的命令
my $cmd_percent = 'sudo conntrack -L -s '.$src_ip.' '.$type.' |sort +2 -n -r';
#print $cmd_percent;
my $detail = `$cmd_percent`;

print $detail; 