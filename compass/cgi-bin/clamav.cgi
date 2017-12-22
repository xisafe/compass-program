#!/usr/bin/perl
#
# Update CGI for Endian Firewall
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


require '/var/efw/header.pl';
require './endianclamav.pl';

my %par;
getcgihash(\%par);

loadconfig();

showhttpheaders();
openpage(_('Clamav AntiVirus'), 1, '');

my ($error, $errormessage) = save();
&openbigbox($errormessage, $warnmessage, $notemessage);
display();

my $status = `/etc/init.d/clamd status`;
my $exitcode = $?;

if ($exitcode eq 0)
{
    display_clamsigantures();
} else {
    openbox('100%', 'left', _('Clamav virus signatures'));	
    print _('None of the activated services are currently using Clamav antivirus. Therefore updates are disabled.');
	print "<br /><br />";
    closebox();
}	

closebigbox();
closepage();

