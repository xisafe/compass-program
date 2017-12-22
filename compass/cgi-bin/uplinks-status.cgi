#!/usr/bin/python
#
# shared code for Endian's CGIs for Endian Firewall
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
# Author: Lukas Pitschl <lukas@endian.com>
#
"""Uplink Status - JSON Interface for the Uplinks Daemon

This interface allows the access of uplinks related information via
GET requests. The returned data is formatted as JSON.
"""

import os, sys
from os import popen
from time import time
import simplejson, cgi
from datetime import datetime
from endian.core.settingsfile import SettingsFile
from uplinksdaemon.uplinks import UplinksPool

UPlINKS_DIR = "/var/efw/uplinks"
ACTIVE_FILE = "%s/%s/active" % (UPlINKS_DIR, "%s")

def list_():
    # print http-header
    init()
    info = pool.info()
    link_infos = []
    for link in info:
        uplink = link['uplinkChain'][0]
        uplink['uptime'] = age(uplink['name'])
        uplink_info = pool.get(uplink['name'])
        uplink['data'] = uplinkData(uplink_info)
        link_infos.append(uplink)
    print simplejson.dumps(link_infos)

def start(uplink):
    if not uplink: return None
    return change_status(uplink, "start")

def stop(uplink):
    if not uplink: return None
    return change_status(uplink, "stop")

def change_status(uplink, status):
    #print "$# %s" % (uplinks_cmd % (status, uplink))
    res = popen(uplinks_cmd % (status, uplink)).close()
    return res == 0

def toDate(timestamp):
    """Returns a human readable version of the timestamp"""
    if timestamp == 0: return ""
    d = datetime.fromtimestamp(timestamp)
    
    return d.strftime("%H:%M:%S")

def uplinkData(up):
    return {'ip' : up.getAddress(), 'type' : up.getSettings().get('RED_TYPE', None),
             'interface' : up.getInterface(), 'gateway' : up.getGateway(),
             'last_retry' : toDate(up.failureTimestamp)}

def status(uplink, error=False):
    # Refresh the status
    pool.scanUplinks()
    up = pool.get(uplink)
    info = up.info()
    info['uptime'] = age(info['name'])
    if error:
        info['error'] = True
    info['data'] = uplinkData(up)
    init()
    print simplejson.dumps(info)

def init():
    """Issues the Content-Type HTTP-Header which is needed, to be executed
    as a CGI."""
    print "Content-type: text/html\r\n"
    
def age(uplink):
    if not os.path.exists(ACTIVE_FILE % uplink):
        return ""
    stat = os.stat(ACTIVE_FILE % uplink)
    now = time()
    unixsecs = now - stat[8]
    # calculating days
    days = int(unixsecs / 86400)
    totalhours = int(unixsecs / 3600)
    hours = totalhours % 24
    totalmins = int(unixsecs / 60)
    mins = totalmins % 60
    secs = int(unixsecs % 60)
    
    return "%sd %sh %sm %ss" % (days, hours, mins, secs)

def manage(uplink):
    manage_flag(uplink, True)

def unmanage(uplink):
    manage_flag(uplink, False)

def manage_flag(uplink, flag):
    # loading settings file
    up = SettingsFile("%s/%s/settings" % (UPlINKS_DIR, uplink))
    # setting the managed flag
    up['MANAGED'] = flag and "on" or "off"
    # saving the changes
    up.write()

request = cgi.FieldStorage()
action = request.getvalue('action', None)
uplink = request.getvalue('uplink', None)

uplinks_cmd = "sudo /etc/rc.d/uplinks %s %s --with-hooks"

if len(sys.argv) > 1:
    uplink = sys.argv[1]
    action = sys.argv[2]

# create the pool to access uplinks
pool = UplinksPool()
ret = False
if action == None or action == "list":
    list_()
elif action == "start":
    ret = start(uplink)
elif action == "stop":
    ret = stop(uplink)
elif action == "status":
    status(uplink)
elif action == "manage":
    manage(uplink)
elif action == "unmanage":
    unmanage(uplink)

if uplink:
    try:
        status(uplink, error = ret)
    except:
        import traceback
        traceback.print_exc()
