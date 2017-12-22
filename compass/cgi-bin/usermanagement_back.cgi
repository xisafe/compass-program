#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2011-07-25

require '/var/efw/header.pl';
use CGI();
use URI::Escape;

my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

&validateUser();
my @names = split(/=/, $parValue[0]);
my $name = uri_unescape($names[1]);
$name =~ s/\+/ /g;
my @user_info    =  read_users_file();
my $is_exit = 0;
foreach my $exit_user(@user_info)
{
	my @temp_usr = split(",",$exit_user);
	if($temp_usr[0] eq $name)
	{
		$is_exit = 1;
	}
}
print $is_exit;