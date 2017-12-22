#!/usr/bin/perl

#
# $Id: index.cgi,v 1.4 2003/12/11 11:06:41 riddles Exp $
#
require '/var/efw/header.pl';
use CGI();
&validateUser();
print "Status: 302 Moved\n";
print "Location: https://$ENV{'SERVER_ADDR'}:10443/monit/\n\n";
