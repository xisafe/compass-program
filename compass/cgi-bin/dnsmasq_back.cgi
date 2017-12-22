#!/usr/bin/perl
#
# dnsmasq CGI for Endian Firewall
#

#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
#        |         Endian GmbH/Srl                                                     |
#        |         Bergweg 41 Via Monte                                                |
#        |         39057 Eppan/Appiano                                                 |
#        |         ITALIEN/ITALIA                                                      |
#        |         info@endian.it                                                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        | http://www.fsf.org/                                                         |
#        +-----------------------------------------------------------------------------+
#


# -------------------------------------------------------------
# some definitions
# -------------------------------------------------------------

require '/var/efw/header.pl';
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
#发改委项目-zhouyuan-2012-08-23-添加DNS代理开关#
my $enabled_dir = "/var/efw/dnsmasq/enabled";
my $restart     = '/usr/local/bin/restartdnsmasq';
my $stop = 'sudo /etc/init.d/dnsmasq stop';
&validateUser();
my %par;
&readhash($enabled_dir, \%setting);
if($setting{'ENABLED'} eq 'on')
{
	$setting{'ENABLED'} = 'off';
}else{
	$setting{'ENABLED'} = 'on';
}
&writehash($enabled_dir, \%setting);

        `$restart --force`;
