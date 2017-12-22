#!/usr/bin/perl
require '/var/efw/header.pl';

my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
&validateUser();
my @langs = split(/=/, $parValue[0]);
my @show_titles = split(/=/, $parValue[1]);

my $lang = uri_unescape($langs[1]);
$lang =~ s/\+/ /g;
my $show_title = uri_unescape($show_titles[1]);
$show_title =~ s/\+/ /g;

my %mainsettings;
&readhash("${swroot}/main/settings",\%mainsettings);
$mainsettings{'LANGUAGE'} = $lang;
$mainsettings{'WINDOWWITHHOSTNAME'} = $show_title;
&writehash("${swroot}/main/settings", \%mainsettings);
expireMenuCache();
system("sudo /etc/init.d/emi reload &>/dev/null");
print "success";