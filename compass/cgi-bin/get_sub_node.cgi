#!/usr/bin/perl
#DATE:2013-7-7
#author:殷其雷
use URI::Escape;
require '/var/efw/header.pl';
my $node_dir = "/var/efw/openvpn/forns/node_structure/";
#获取传来参数,默认只有一个参数.
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
&validateUser();
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my @par_line = split(/=/, $parValue[0]);
my $name = $node_dir;
$name .= uri_unescape(@par_line[1]);
my $returnvalue = "";
opendir(DIR,$name);
my @nodes = readdir(DIR);
foreach my $one (@nodes)
{
	if($one ne 'node-info' && $one ne 'node-info.old' && $one ne '.' && $one ne '..')
	{
	   $returnvalue .= $one;
	   $returnvalue .= ",";
	}
}
print $returnvalue;
1;