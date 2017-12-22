#!/usr/bin/perl

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
require 'passwd-lib.pl';

my %cgiparams;

&showhttpheaders();

$cgiparams{'ACTION_ADMIN'} = '';
$cgiparams{'ACTION_DIAL'} = '';

&getcgihash(\%cgiparams);

foreach my $regfile (glob("/home/httpd/cgi-bin/passwordDialogue-*.pl")) {
    require $regfile;
}

callPasswordSaves();
&openpage(_('Change passwords'), 1, '');
&openbigbox($errormessage, $warnmessage, $notemessage);
&openbox('100%', 'left', _('Change Passwords'));

printf <<END
    <div class="efw-form">
END
;

callPasswordDisplays(0);

printf <<END
        <br class="cb" />
    </div>

END
;

&closebox();
&closebigbox();
&closepage();
