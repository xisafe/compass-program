#!/usr/bin/perl

use CGI();
use URI::Escape;
use Digest::MD5; 
require '/var/efw/header.pl';
require 'logs_common.pl';

my $userfile="/var/efw/userinfo/userslist";
# my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

$ENV{'QUERY_STRING'} =~ /pass=(.*)/;
my ($pass) = ($1);
my $pass = URI::Escape::uri_unescape($pass);
my $passes = &decryptFn($pass);
# print ($passes);

my @user_info = read_users_file();
$name = &get_cookie_user();

my $msg;
foreach	my $user(@user_info){
	my @info = split(/,/,$user);
	if (( $info[1] eq $passes)) {
		$msg = "success";
		# &user_log($log_message);
		print $msg;
		return $msg;
	}
}
print "$msg";