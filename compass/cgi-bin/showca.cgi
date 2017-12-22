#!/usr/bin/python
#
# openvpn CGI for Endian Firewall
# this script sends the ca public key
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
from sys import exit
import cgi
import cgitb; cgitb.enable()
from endian.data.ds import DataSource

SETTINGSDIR='/var/efw/'

ds = DataSource()

hostname = ds.host.settings.get('hostname', '')
cafile=''
args={}

argv = cgi.parse()
typ = argv.get('type', [])[0]

if typ == 'p12':
    args['filename'] = hostname + '.p12'
    args['content-type'] = 'application/x-pkcs12'
    cafile = SETTINGSDIR+'/openvpn/pkcs12.p12'
elif typ == 'pem':
    args['filename'] = hostname + '.pem'
    args['content-type'] = 'application/x-x509-ca-cert'
    cafile = SETTINGSDIR+'/openvpn/cacert.pem'
else:
    print """Cache-Control: no-cache
Connection: close

Wrong type
"""

    exit(0)

print """Cache-Control: no-cache
Connection: close
Content-Type: %(content-type)s
Content-Disposition: attachement; filename="%(filename)s"
"""%args

f = open (cafile)
for line in f:
    if line[-1] in ['\n', '\r']:
        print line[:-1]
    else:
        print line
f.close()
exit(0)
