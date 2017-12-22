#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2011-08-03

require '/var/efw/header.pl';
use CGI();
use URI::Escape;
&validateUser();
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my $cut_cmd = 'sudo conntrack -F ';
my $cut_out = `$cut_cmd`;
