#!/usr/bin/perl
#DATE:2013-5-7
#author:殷其雷
#MODIFY:2013-6-5

require '/var/efw/vpn_header.pl';
require 'description_lib.pl';
require '/var/efw/header.pl';
use utf8;
use Encode;
use URI::Escape;
&validateUser();
#获取传来参数,默认只有一个参数.
my @parValue = split(/&/, $ENV{'QUERY_STRING'});

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my @par_line = split(/=/, $parValue[0]);
my $description_name = @par_line[1];
#将URL编码转为UTF8编码
my $name = uri_unescape($description_name);
my $description_line = readdesfile($name);
print $description_line;
=p
#my $description_line = read_description($description_name);


if(($description_line eq "描述信息不存在!")||($description_line eq "描述信息文件打开失败!")||($description_line eq "描述信息为空!"))
{
    print $description_line;
} else {
    my @description = split(/&/,$description_line);
	my $return_description = "";
	my $length = scalar(@description);
	my $count = 0;
    foreach my $one_description(@description)
	{
	    $count++;
	    $return_description .= $one_description;
		if(($count ne $length))
		{
		   $return_description .= "";
		}
	}
	print $return_description;
}
=cut
1;