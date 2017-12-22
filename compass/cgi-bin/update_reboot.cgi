#!/usr/bin/perl
# AUTHOR: “Û∆‰¿◊ 2013/4/23
require '/var/efw/header.pl';
&validateUser();
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

sleep(3);
system '/usr/local/bin/ipcoprebirth';