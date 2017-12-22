#!/usr/bin/perl

#file:hasync_ajax.cgi
#author:ailei
use CGI();
use URI::Escape;
require "/var/efw/header.pl";
&validateUser();
$ENV{'QUERY_STRING'} = uri_unescape($ENV{'QUERY_STRING'});
my @parValue = split(/&/, $ENV{'QUERY_STRING'});

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my $STATUS_DIR="${swroot}/HA/status/";
my $status = "";
my $exsit_flag = 0;
my $sync_file_path = "${swroot}/HA/status/SYNC";
my $nosync_file_path = "${swroot}/HA/status/NOSYNC";

foreach $par(@parValue){
	($name,$value) = split(/=/, $par);
	if ($name eq "flag") {
		$method_value = $value;
	}
}
if ($method_value == "0") {
	system("/usr/bin/sudo /usr/local/bin/checksync -p");
	system("/usr/bin/sudo /usr/local/bin/checksync");
}
else
{
	system("/usr/bin/sudo /usr/local/bin/checksync -l");
	system("/usr/bin/sudo /usr/local/bin/checksync");
}

if (-e $sync_file_path) {
	$exsit_flag = 1;
	$status= "===1";
}

if (-e $nosync_file_path) {
	$exsit_flag = 1;
	$status= "===0";
}

if ( $exsit_flag == 0 ) {
	$status = "===0";
}
print $status;

