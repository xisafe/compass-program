#!/usr/bin/perl -w
use CGI();
use URI::Escape;

require "/var/efw/header.pl";
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
my ($name,$path) = split(/=/, $ENV{'QUERY_STRING'});
my $file_path;
&validateUser();
if ($path eq "oray") {
	$file_path = "/var/efw/phlinux/settings";
}
else{
	$file_path = "/var/efw/gnhostlinux/settings";
}
readhash($file_path,\%conf);
my $status = `/usr/sbin/checkddns.py $conf{'DOMAIN'}`;
chomp($status);
if ($status eq "error_domain"){
	$status = "<font color='red'>域名设置不正确！</font>";
	}
elsif (!validip($status)) {
	$status = "连接异常";
}
print $status;
