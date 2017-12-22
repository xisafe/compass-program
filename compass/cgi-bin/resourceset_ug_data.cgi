#!/usr/bin/perl

#	@Author 王琳
#	@History 2013.09.05 First release
#

use strict;
use JSON::XS;

require '/var/efw/header.pl';
my $result = '';
my %groupinfohash;
my @groupinfoarray;
my %par;
&validateUser();
getcgihash(\%par);
my $user_groups = $par{'userGroups'};
$user_groups =~ s/,/:/g ;

my $json = new JSON::XS->utf8;
my @user_groups_splitted = split(/\n/, `sudo ResMng -ugq -mugq "$user_groups"`);
foreach my $ugroupinfo (@user_groups_splitted){
	chomp($ugroupinfo);
	my $json_obj = $json->decode($ugroupinfo);
	my %ugrouph;
	%ugrouph->{'full_name'} = $json_obj->{'full_name'};
	%ugrouph->{'desc'} = $json_obj->{'desc'};
	push(@groupinfoarray, \%ugrouph);
}
%groupinfohash->{'data'} = \@groupinfoarray;
$result = $json->encode(\%groupinfohash);
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
print $result;
