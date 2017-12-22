#!/usr/bin/perl
#
# author:zhouyuan
#
# date:2011-08-30
require '/var/efw/header.pl';
require '/home/httpd/cgi-bin/netstatus.pl';
require '/home/httpd/cgi-bin/ethconfig.pl';

my @parValue = split(/&/, $ENV{'QUERY_STRING'});
my $length = @parValue;
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
&validateUser();

my $eth = "";
for(my $i = 0;$i<$length;$i++)
{
	my @temp = split(/=/, $parValue[$i]);
	if($temp[0] eq "eth")
	{
		$eth = uri_unescape($temp[1]);
	}
}

my $str = get_interface_detail($eth);
print $str;
