#!/usr/bin/perl
require '/var/efw/header.pl';
&validateUser();
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

$result = `sudo ResMng -orgq 所有用户`;
print $result;