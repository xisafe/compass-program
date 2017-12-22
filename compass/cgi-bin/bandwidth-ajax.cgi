#!/usr/bin/perl
use CGI();
use URI::Escape;
require '/var/efw/header.pl';

my $settingfile="/var/efw/qos/settings";
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
&validateUser();
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
foreach $par(@parValue){
	($name,$value) = split(/=/, $par);
}
my $data;
my %settings;
if (-e $settingfile) {
	&readhash($settingfile,\%settings);
}
$data = $settings{$value};
print $data;