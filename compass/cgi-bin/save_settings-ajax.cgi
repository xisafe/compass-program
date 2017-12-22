#!/usr/bin/perl -w
#use CGI();
#use URI::Escape;
require "/var/efw/header.pl";
my $conffile = "/var/efw/logging/live_settings";
my $conffile_default = "/var/efw/logging/default/live_settings";
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

&validateUser();
my ($name,$value) = split(/=/,$parValue[0]);

if (! (-e $conffile)) {
	system ("cp $conffile_default $conffile");
}

my %conf;
&readhash($conffile,\%conf);
$value =~s/livelog_/LIVE_/;
if ($conf{$value} eq 'on') {
	$conf{$value} = 'off';
}
else{$conf{$value} = 'on';}
writehash($conffile,\%conf);
`sudo fmodify $conffile`;