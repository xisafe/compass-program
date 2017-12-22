#!/usr/bin/python                                                        
# -*- coding:utf-8 -*-
#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2010 Endian                                              |
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

import cgitb, os, subprocess, time, string, datetime, sys
from endian.core.widget import *
from endian.data.ds import *
from os import popen
from configobj import ConfigObj
from uplinksdaemon.uplinks import UplinksPool
from endian.core.monit import Monit
import endian.core.i18n
endian.core.i18n.UNICODE_WORKAROUND=True
import elementtree.ElementTree as ElementTree
import glob
import time

UPLINKS_DIR = "/var/efw/uplinks"
ACTIVE_FILE = "%s/%s/active" % (UPLINKS_DIR, "%s")
UUID_FILE = '/etc/uuid'
RRD_DIR = '/var/lib/collectd/rrd'
SNORT_PATH = '/var/log/snort/alert'

_isCommunity = None

def isCommunity():
    global _isCommunity
    if _isCommunity == None:
        if glob.glob('/etc/product*'):
            _isCommunity = False
        else:
            _isCommunity = True
    return _isCommunity
##########modify by mawen at 2013-5-9#################################
def snort_hour():
    if not os.path.exists(SNORT_PATH):
	count=0
	return count
    f = file('/var/log/snort/alert','r')
    count = 0
    while True:
        line = f.readline()
        if len(line)==0:
            break
        if line[11]+line[12] == time.strftime('%H',time.localtime(time.time())):
            count = count + 1
    f.close()
    return count

def snort_daily():
    if not os.path.exists(SNORT_PATH):
	count=0
	return count
    f = file('/var/log/snort/alert','r')
    count = 0
    while True:
        line = f.readline()
        if len(line)==0:
            break
        count = count + 1
    f.close()
    return count

##########modify by mawen at 2013-5-9#################################
def getRRDInformation(file, step, start, end):
    if not file.startswith('/'):
        try:
            f = open(UUID_FILE,'r')
            uuid = f.read().strip()
            f.close()
        except Exception:
            uuid = 'invalid-uuid'
        file = '%s/%s/%s' %(RRD_DIR,uuid,file)
    if not os.path.exists(file):
        return 0
    cmd = ['/usr/bin/rrdtool','xport',
           '--step', step, '-e',end, '-s', start,
           'DEF:conn_avg=%s:value:AVERAGE' %file,
           'CDEF:mytime=conn_avg,TIME,TIME,IF',
           'CDEF:sample_len_raw=mytime,PREV(mytime),-',
           'CDEF:sample_len=sample_len_raw,UN,0,sample_len_raw,IF',
           'CDEF:conn_avg_sample=conn_avg,UN,0,conn_avg,IF,sample_len,*',
           'CDEF:conn_avg_sum=PREV,UN,0,PREV,IF,conn_avg_sample,+',
           'XPORT:conn_avg_sum:total']
    output = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0].strip()
    value = 0
    try:
        tree = ElementTree.fromstring(output)
        row = tree.find('data').findall('row')[-1]
        value = int(float(row.find('v').text))
    except Exception:
        return 0 
    os.system('touch /%s'%value)
    return value

def countCPUs():
    ret = 0
    f = open('/proc/cpuinfo')
    for line in f:
        if line.startswith('processor'):
            ret += 1
    f.close()
    return ret

def getIssue():
    ret = ''
    f = open('/etc/issue')
    ret = f.read().strip()
    f.close()
    return ret

def getSystemInformation():
    cpucount = countCPUs()
    version = ""
    try:
        version = getIssue()
    except:
        # file may be does not exist -> version remains empty
        pass
    version = version.split('(')
    deployset = "#0"
    if len(version) > 1:
        deployset = version[1][version[1].find('#'):-1]
    version = version[0].strip().split(' ')[-1]
    version = string.join(map(lambda x: x.strip(),version),'')
    model = "-"
    if isCommunity():
        model = "Community"
    else:
        try:
            f = open('/var/efw/appliance/info','r')
            model = f.read().strip().split('=')[1].capitalize()
            f.close()
        except Exception, e:
            pass
    
    if os.path.exists("/var/tmp/oldkernel"):
        kernel = "<a href=\"/cgi-bin/shutdown.cgi\" style=\"color: red;\"><b>%s</b></a>" % _('reboot required')
    else:
        try:
            f = open('/proc/version','r')
            info = f.readlines()[0]
            f.close()
            kernel = info.split(" ")[2]
        except Exception, e:
            kernel = ""
    
    uptime = subprocess.Popen(['/usr/bin/uptime'],stdout=subprocess.PIPE)\
                              .communicate()[0].strip().split('user')[0]\
                              .split('up ')[1].split(',')[0:-1]
    uptime = map(lambda x: x.strip(), uptime)
    if len(uptime) == 2:
        days = int(uptime[0].split(' ')[0])
        if uptime[1].count(':') > 0:
            hours = int(uptime[1].split(':')[0])
            minutes = int(uptime[1].split(':')[1])
        else:
            hours = 0
            minutes = int(uptime[1].split(' ')[0])
        uptime = "%dd %dh %dm" %(days, hours, minutes)
    elif len(uptime) == 1:
        if uptime[0].find(':') > 0:
            hours = int(uptime[0].split(':')[0])
            minutes = int(uptime[0].split(':')[1])
            uptime = "%dh %dm" %(hours, minutes)
        else:
            if uptime[0].find('m') > 0:
                uptime = '%dm' %(int(uptime[0].split(' ')[0]))
            else:
                uptime = '%dh' %(int(uptime[0].split(' ')[0]))
    
    ds = DataSource('en').settings
    sysid = ds.get('sysid')
    
    updates = "<div style=\"color: green;\">%s</div>" % _('up to date')
    if isCommunity():
        updates = "<a href=\"http://www.endian.com/de/community/efw-updates/\" style=\"color: green;\"><b>%s</b></a>" % _('please register')
    elif not sysid:
            updates = "<a href=\"/cgi-bin/register.cgi\" style=\"color: red;\"><b>%s</b></a>" % _('please register')    
    try:
        f = open('/var/cache/en/update_list','r')
        for line in f:
            if line.strip() != "":
                updates = "<a href=\"/cgi-bin/updates.cgi\" style=\"color: red;\"><b>%s</b></a>" % _('update required')
                break;
        f.close()
    except Exception, e:
        pass
    
    enBase = None
    enSophos = None
    enCommtouch = None
    # Check if the system is registered.
    if os.path.exists("/usr/bin/en-client"):
        info_file = '/var/cache/en-%s' % sysid
        if not os.path.exists(info_file):
            os.system("sudo en-client --check &>/dev/null")
        if os.path.exists(info_file):
            enInfo = ConfigObj(info_file)
            for key in enInfo.keys():
                if key.endswith("-base") or key.endswith("-early-adopter"):
                    enBase = enInfo.get(key)
                elif key == "sophos-antivirus":
                    enSophos = enInfo.get(key)
                elif key == "commtouch":
                    enCommtouch = enInfo.get(key)
    if not enBase:
        maintenance = "<b style=\"color: red;\">%s</b>" % _("not registered")
    else:
        subscribed = int(enBase.get('subscribed-timestamp'))
        expiration = int(enBase.get('expiration-timestamp'))
        now = time.time()
        
        daysleft = int((expiration - now) / 86400)
        if subscribed > now:
            maintenance = "<b style=\"color: red;\">%s</b>" % _('not yet')
        elif expiration < now:
            maintenance = "<b style=\"color: red;\">%s</b>" % _('expired'); 
        else:
            color = "green"
            tag = "div"
            if daysleft <= 31:
                color = "red"
                tag = "b"
            maintenance = "<%s style=\"color: %s;\">%s %s</%s>" % (tag, color, daysleft, _("days left"), tag)
    if not enSophos:
        sophos = None
    else:
        subscribed = int(enSophos.get('subscribed-timestamp'))
        expiration = int(enSophos.get('expiration-timestamp'))
        now = time.time()

        daysleft = int((expiration - now) / 86400)
        if subscribed > now:
            sophos = "<b style=\"color: red;\">%s</b>" % _('not yet')
        elif expiration < now:
            sophos = "<b style=\"color: red;\">%s</b>" % _('expired'); 
        else:
            color = "green"
            tag = "div"
            if daysleft <= 31:
                color = "red"
                tag = "b"
            sophos = "<%s style=\"color: %s;\">%s %s</%s>" % (tag, color, daysleft, _("days left"), tag)
    if not enCommtouch:
        commtouch = None
    else:
        subscribed = int(enCommtouch.get('subscribed-timestamp'))
        expiration = int(enCommtouch.get('expiration-timestamp'))
        now = time.time()

        daysleft = int((expiration - now) / 86400)
        if subscribed > now:
            commtouch = "<b style=\"color: red;\">%s</b>" % _('not yet')
        elif expiration < now:
            commtouch = "<b style=\"color: red;\">%s</b>" % _('expired'); 
        else:
            color = "green"
            tag = "div"
            if daysleft <= 31:
                color = "red"
                tag = "b"
            commtouch = "<%s style=\"color: %s;\">%s %s</%s>" % (tag, color, daysleft, _("days left"), tag)

    ds = DataSource('support').settings
    if ds.get('ENABLED', '') == "on":
        try:
            timestamp = float(ds.get('VALID_UNTIL', None))
            enabled = "%s %s" % (_("until"), datetime.datetime.fromtimestamp(timestamp).strftime("%Y.%m.%d %H:%M"))
        except:
            enabled = _("enabled")
        support = "<b style=\"color: red\">%s</b>" % enabled
    else:
        support = "<div style=\"color: green\">%s</div>" % _("disabled")
    memory = 0
    swap = 0
    memoryused = 0
    swapused = 0
    try:
        f = open('/proc/meminfo','r')
        for line in f:
            if line.startswith('MemTotal:'):
                memory = int(line.split(':')[1].strip().split(' ')[0])
            elif line.startswith('SwapTotal:'):
                swap = int(line.split(':')[1].strip().split(' ')[0])
            elif line.startswith('MemFree:'):
                memoryused = memory - int(line.split(':')[1].strip().split(' ')[0])
            elif line.startswith('Buffers:'):
                memoryused = memoryused - int(line.split(':')[1].strip().split(' ')[0])
            elif line.startswith('Cached:'):
                memoryused = memoryused - int(line.split(':')[1].strip().split(' ')[0])
            elif line.startswith('SwapFree:'):
                swapused = swap - int(line.split(':')[1].strip().split(' ')[0])
        f.close()
    except Exception, e:
        pass
    c = subprocess.Popen(['df','-h'],stdout=subprocess.PIPE).communicate()[0].strip()
    c = c.split("\n")
    disks = []
    logdisk=0
    for line in c[0:]:
        if len(line.split(' ')) > 2:
            disk = line.split(' ')
            # skip on errors
            try:
                disk[-2] = int(disk[-2][:-1])
                if disk[-1] == '/':
                    name = 'root'
                    desc = _('Main disk')
                elif disk[-1] == '/var':
                    name = 'var'
                    desc = _('Data disk')
                elif disk[-1] == '/boot':
                    name = 'boot'
                    desc = _('Boot disk')
                elif disk[-1] == '/var/efw':
                    name = 'efw'
                    desc = _('Config disk')
                elif disk[-1] == '/var/log':
##########by fanglang 2013-12-26
                    if logdisk == 0:
                        name = 'log'
                        desc = _('Log disk')
                        logdisk=1
                    else: 
                        continue
                else:
##########by fanglang 2013-12-26 for  cf tmpfs 
                    continue 
#                    name = disk[-1]
#                    desc = disk[-1]
            
                size = ""
                for field in disk[1:-2]:
                    if field != "":
                        size = field[:-1]+' '+field[-1]+'B'
                        break 
                
                disks.append({'KEY':'df-%s'%name,'USAGE':disk[-2],'NAME':desc,'TOTAL':size})
            except Exception, e:
                pass
    
    hostname = subprocess.Popen(['/bin/hostname'],stdout=subprocess.PIPE).communicate()[0].strip()
    versionlist = [hostname,
                   {'HEADER':_('Appliance'),'VALUE': model},
                   {'HEADER':_('Version'),'VALUE': version}]
    
    if not isCommunity():
        versionlist.append({'HEADER':_('Deployset'),'VALUE' : deployset})
    if kernel != "":
        versionlist.append({'HEADER':_('Kernel'),'VALUE' : kernel})
    versionlist.append({'HEADER':_('Uptime'),'VALUE' : uptime})
    
    updatelist = []
    if not isCommunity():
        updatelist.append({'HEADER':_('Update status'),'VALUE' : updates})
        updatelist.append({'HEADER':_('Maintenance'),'VALUE' : maintenance})
        if sophos:
            updatelist.append({'HEADER':_('Sophos'),'VALUE' : sophos})
        if commtouch:
            updatelist.append({'HEADER':_('Commtouch'),'VALUE' : commtouch})
        if os.path.exists('/var/efw/support/'):
            updatelist.append({'HEADER':_('Support access'),'VALUE' : support})
    hardwaredict= {'CPUCOUNT': cpucount, 
                  'PERCENTAGES':[]}
    if memory > 0:
        hardwaredict['PERCENTAGES'].append({'KEY': 'memory','USAGE': int((float(memoryused)/memory)*100),
                                            'TOTAL': "%d MB" %int(memory/1024), 'NAME':_('Memory')})
    if swap > 0:
        hardwaredict['PERCENTAGES'].append({'KEY': 'swap', 'USAGE': int((float(swapused)/swap)*100), 
                                            'TOTAL': "%d MB" %int(swap/1024), 'NAME':_('Swap')})
    hardwaredict['PERCENTAGES'] = hardwaredict['PERCENTAGES'] + disks
    return versionlist,updatelist,hardwaredict

def getNetworkInformation(uplinkcache, niccache):
    c = subprocess.Popen(['/sbin/ip','link'],
                         stdout=subprocess.PIPE).communicate()[0].strip()
    lines = c.split("\n")
    lines = map(lambda x: x.strip(),lines)
    devices = []
    ds = DataSource('ethernet').settings
    vpn = DataSource('openvpn').settings
    for line in lines:
        if not line.strip().startswith('link'):
            x = line.split(':')
            device = x[1].strip()
            if device == 'lo':
                continue
            elif device.find('@') > 0:
                device = device.split('@')[0].strip()
            on = _('已连接')
            if line.find('NO-CARRIER') >= 0:
                on = _('未连接')
            up = _('已启用')
            if line.find(',UP,') < 0 and line.find('<UP,') < 0 and line.find(',UP>') < 0:
                up = _('未启用')
            devices.append({'DEVICE':device,'LINK':on,'STATUS':up,'DISPLAY':device.replace('.','_')})
        else:
            x = line.split('link/')
            if len(x) > 1:
                typ = x[1].split(' ')[0]
            if typ == 'ether':
                typ = '以太网'
            if len(devices) > 0:
                devices[len(devices)-1]['TYPE'] = typ 
                devices[len(devices)-1]['IN'] = ''
                devices[len(devices)-1]['OUT'] = ''
    bridgeInterfaces = {}
    for device in devices:
        if device['DEVICE'].startswith('br') and os.path.exists('/var/efw/ethernet/%s' % device['DEVICE']):
            f = open('/var/efw/ethernet/%s'%device['DEVICE'],'r')
            bridgeInterfaces[device['DEVICE']] = []
            for line in f:
                if line.strip() != '':
                    bridgeInterfaces[device['DEVICE']].append(line.strip())
            f.close()
        elif ds.get('BLUE_DEV').startswith("tun") and ds.get('BLUE_DEV') == device['DEVICE']:
            bridgeInterfaces[device['DEVICE']] = []
    
    devicedict = {}
    usedInterfaces = []
    for dev, value in bridgeInterfaces.iteritems():
        for d in devices:
            if d['DEVICE'] == dev:
                devicedict[d['DEVICE']] = d
        devicedict[dev]['BRIDGE'] = True
        devicedict[dev]['CLASS'] = ''
        devicedict[dev]['CHECKED'] = 'checked'
        if ds.get('GREEN_DEV') == dev:
            devicedict[dev]['CLASS'] = 'green'
        elif ds.get('BLUE_DEV') == dev:
            devicedict[dev]['CLASS'] = 'blue'
        elif ds.get('ORANGE_DEV') == dev:
            devicedict[dev]['CLASS'] = 'orange'
        else:
            devicedict[dev]['CLASS'] = 'unknown'
        devicedict[dev]['PHYSICAL'] = []
        usedInterfaces.append(dev)
        for d in devices:
            if d['DEVICE'] in value and d['DEVICE'] not in usedInterfaces:
                d['CHECKED'] = ''
                devicedict[dev]['PHYSICAL'].append(d)
                usedInterfaces.append(d['DEVICE'])
    for d in devices:
        if d['DEVICE'] not in usedInterfaces:
            devicedict[d['DEVICE']] = d
            devicedict[d['DEVICE']]['BRIDGE'] = False
            devicedict[d['DEVICE']]['CLASS'] = 'unknown'
            devicedict[d['DEVICE']]['CHECKED'] = ''
            if vpn.get('PURPLE_DEVICE') == d['DEVICE']:
                devicedict[d['DEVICE']]['CLASS'] = 'purple'
                devicedict[d['DEVICE']]['CHECKED'] = 'checked'
            elif d['DEVICE'].startswith('ipsec'):
                devicedict[d['DEVICE']]['CLASS'] = 'purple'
                devicedict[d['DEVICE']]['CHECKED'] = 'checked'
            elif d['DEVICE'] in niccache:
                    devicedict[d['DEVICE']]['CLASS'] = 'red'
                    devicedict[d['DEVICE']]['CHECKED'] = 'checked'
            usedInterfaces.append(d['DEVICE'])
    newdict = {}
    for x, y in devicedict.iteritems():
        if y.get('CLASS') != 'unknown':
            newdict[x] = y
    sorting = newdict.keys()
    sorting.sort()
    return newdict, sorting

def loadUplinks():
    _uplinkCache = {}
    _nicCache = {}
    ups = UplinksPool()
    for uplink in ups.iterUplinks():
        settings = uplink.getSettings()
        name = uplink.uplinkname
        data = uplink.getData()
        _uplinkCache[name] = {
            'settings': settings,
            'data': data,
            }
        iff = settings.get('RED_DEV')
        if iff == None:
            iff = data.get('INTERFACE')
        _nicCache[iff] = _uplinkCache[name]
    return _uplinkCache, _nicCache

def getUplinkInformation(uplinkcache):
    pool = UplinksPool()
    info = pool.info()
    link_infos = []
    used_links = []
    for link in info:
        level = 0
        for uplink in link['uplinkChain']:
            up = pool.get(uplink['name'])
            settings = uplinkcache[uplink['name']]
            name = settings.get('NAME', uplink['name'])
            if name == "":
                name = uplink['name']
            if name == "main":
                name = _("主上行口")
            name =  name.replace("'", "")
            uplink['DATA'] = {
                'NAME': name, 
                'IP' : up.getAddress(), 
                'TYPE' : settings.get('RED_TYPE', None),
                'INTERFACE' : up.getInterface(), 
                'GATEWAY' : up.getGateway(),
                'LEVEL' : level
                }
            if uplink['name'] not in used_links:
                link_infos.append(uplink)
                used_links.append(uplink['name'])
            level += 1
    return link_infos

def getServiceInformation():
    m = Monit()
    returnlist = []
    presorteddict = {}
    postfix_static = {'queue':{'COUNT':0,'DESC':_('mails in queue'),'ID':'queue'}}
    postfix_dyn = {'incoming':{'COUNT':[getRRDInformation('tail-smtp/connections-incoming.rrd','1800','NOW-1h','NOW'),
                                        getRRDInformation('tail-smtp/connections-incoming.rrd','1800','NOW-1d','NOW')],
                               'DESC':_('mails received'),'ID':'incoming'},
                   'clean':{'COUNT':[getRRDInformation('tail-smtp/connections-clean.rrd','1800','NOW-1h','NOW'),
                                     getRRDInformation('tail-smtp/connections-clean.rrd','1800','NOW-1d','NOW')],
                            'DESC':_('clean mails received'),'ID':'clean'},
                   'spam':{'COUNT':[getRRDInformation('tail-smtp/connections-spam.rrd','1800','NOW-1h','NOW'),
                                    getRRDInformation('tail-smtp/connections-spam.rrd','1800','NOW-1d','NOW')],
                           'DESC':_('spam mails received'),'ID':'spam'},
                   'virus':{'COUNT':[getRRDInformation('tail-smtp/connections-virus.rrd','1800','NOW-1h','NOW'),
                                     getRRDInformation('tail-smtp/connections-virus.rrd','1800','NOW-1d','NOW')],
                            'DESC':_('viruses found'),'ID':'virus'},
                   'noqueue':{'COUNT':[getRRDInformation('tail-smtp/connections-noqueue.rrd','1800','NOW-1h','NOW'),
                                       getRRDInformation('tail-smtp/connections-noqueue.rrd','1800','NOW-1d','NOW')],
                              'DESC':_('mails rejected'),'ID':'noqueue'}}
    postfix_static_on = [{'queue':True}]
    postfix_dyn_on = [{'incoming':True},
                      {'clean':True},
                      {'spam':False},
                      {'virus':False},
                      {'noqueue':True}]
    p3scan = {'spam':{'COUNT':[getRRDInformation('tail-pop/connections-spam.rrd','1800','NOW-1h','NOW'),
                                  getRRDInformation('tail-pop/connections-spam.rrd','1800','NOW-1d','NOW')],
                         'DESC':_('spam mails found'),'ID':'spam'},
              'scanned':{'COUNT':[getRRDInformation('tail-pop/connections-scanned.rrd','1800','NOW-1h','NOW'),
                                  getRRDInformation('tail-pop/connections-scanned.rrd','1800','NOW-1d','NOW')],
                         'DESC':_('mails received'),'ID':'scanned'},
              'virus':{'COUNT':[getRRDInformation('tail-pop/connections-virus.rrd','1800','NOW-1h','NOW'),
                                getRRDInformation('tail-pop/connections-virus.rrd','1800','NOW-1d','NOW')],
                       'DESC':_('viruses found'),'ID':'virus'}}
    p3scan_on = [{'spam':True},
                 {'scanned':True},
                 {'virus':True}]
    snort = {'logged':{'COUNT':[snort_hour(),snort_daily()],
                       'DESC':_('attacks logged'),'ID':'logged'}}
#             'blocked':{'COUNT':[getRRDInformation('tail-snort/connections-drop.rrd','1800','NOW-1h','NOW'),
#                                 getRRDInformation('tail-snort/connections-drop.rrd','1800','NOW-1d','NOW')],
#                        'DESC':_('attacks blocked'),'ID':'blocked'}}
    snort_on = [{'logged':True},
                {'blocked':True}]
    squid = {'miss':{'COUNT':[getRRDInformation('tail-http/connections-miss.rrd','1800','NOW-1h','NOW'),
                              getRRDInformation('tail-http/connections-miss.rrd','1800','NOW-1d','NOW')],
                     'DESC':_('misses'),'ID':'miss'},
             'hit':{'COUNT':[getRRDInformation('tail-http/connections-hit.rrd','1800','NOW-1h','NOW'),
                             getRRDInformation('tail-http/connections-hit.rrd','1800','NOW-1d','NOW')],
                    'DESC':_('hits'),'ID':'hit'},
             'virus':{'COUNT':[getRRDInformation('tail-http/connections-virus.rrd','1800','NOW-1h','NOW'),
                               getRRDInformation('tail-http/connections-virus.rrd','1800','NOW-1d','NOW')],
                      'DESC':_('viruses found'),'ID':'virus'},
             'denied':{'COUNT':[getRRDInformation('tail-http/connections-denied.rrd','1800','NOW-1h','NOW'),
                                getRRDInformation('tail-http/connections-denied.rrd','1800','NOW-1d','NOW')],
                       'DESC':_('pages filtered'),'ID':'denied'}}
    squid_on = [{'miss':True},
                {'hit':True},
                {'denied':False},
                {'virus':False}]
    
    m = m.getStatus()
    if m.get('sections') != "":
        for key, value in m.get('sections').iteritems():
            if key == 'Process':
                for process in value:
                    name = process.get('name')
                    status = process.get('status')
                    proc = {'ID':name,'NAME':'','ON':False, 'LIVELOG':False, 'TASKS':{'DYNAMIC':[],'STATIC':[]}}
                    if process.get('status') == 'running':
                        proc['ON'] = True
                    if name == 'p3scan':
                        proc['NAME'] = _('POP3 Proxy')
                    elif name == 'amavisd' and status == 'running':
                        postfix_dyn_on[3]['virus'] = True
                    elif name == 'dansguardian' and status == 'running':
                        squid_on[2]['denied'] = True
                    elif name == 'havp' and status == 'running':
                        squid_on[3]['virus'] = True
                    elif name == 'snort':
                        proc['NAME'] = _('入侵防御')
                        proc['LIVELOG'] = "snort"
                    elif name == 'postfix':
                        proc['NAME'] = _('SMTP Proxy')
                        proc['LIVELOG'] = "smtp"
                    elif name == 'squid':
                        proc['NAME'] = _('HTTP Proxy')
                        proc['LIVELOG'] = "dansguardian,squid"
                    if proc['NAME'] != '':
                        presorteddict[name] = proc
    try:
        smtpscansettings = DataSource('smtpscan').settings
        if 'SA_ENABLED' in smtpscansettings and smtpscansettings['SA_ENABLED'] == 'on':
            postfix_dyn_on[2]['spam'] = True
    except Exception, e:
        pass
    if presorteddict.has_key('squid'):
        for feat in squid_on:
            for key, value in feat.iteritems():
                if value:
                    presorteddict['squid']['TASKS']['DYNAMIC'].append(squid.get(key))
        returnlist.append(presorteddict['squid'])
    if presorteddict.has_key('postfix'):
        for feat in postfix_dyn_on:
            for key, value in feat.iteritems():
                if value:
                    presorteddict['postfix']['TASKS']['DYNAMIC'].append(postfix_dyn.get(key))
        for feat in postfix_static_on:
            for key, value in feat.iteritems():
                if value:
                    presorteddict['postfix']['TASKS']['STATIC'].append(postfix_static.get(key))
        returnlist.append(presorteddict['postfix'])
    if presorteddict.has_key('p3scan'):
        for feat in p3scan_on:
            for key, value in feat.iteritems():
                if value:
                    presorteddict['p3scan']['TASKS']['DYNAMIC'].append(p3scan.get(key))
        returnlist.append(presorteddict['p3scan'])
    if presorteddict.has_key('snort'):
        for feat in snort_on:
            for key, value in feat.iteritems():
                if value:
                    presorteddict['snort']['TASKS']['DYNAMIC'].append(snort.get(key))
        returnlist.append(presorteddict['snort'])
    return returnlist


def buildPage():
    version,updates,hardware = getSystemInformation()
    uplinkCache, nicCache = loadUplinks()
    devices, netsort = getNetworkInformation(uplinkCache, nicCache)
    uplinks = getUplinkInformation(uplinkCache)
    services = getServiceInformation()
    sysmenu = [{'TITLE':version[0],'INFORMATION':version[1:]+updates}]
    percentmenu = {'TITLE':_('Hardware information'),'INFORMATION':hardware}
    netmenu = {'TITLE':_('Network Interfaces'),'INFORMATION':devices,'SORTING':netsort,
               'HEADERS':[_('show graph'),_('Device'),_('Type'),_('连接状态'),_('网卡状态'),_('流入速率'),_('流出速率')]}
    uplinkmenu = {'TITLE':_('Uplinks'),'INFORMATION':uplinks,
                  'HEADERS':[_('接口名'),_('IP Address'),_('激活'),_('托管'),_('reconnect')]}
    servicemenu = {'TITLE':_('安全服务'),'INFORMATION':services,
                   'HEADERS':[_('Status'),_('Name'),_('Information')]}
    
    body = BaseWidget('/usr/share/efw-gui/dashboard/widgets/dashboard.tmpl',cheetah=True)
    body.setValue('SYSTEM',sysmenu)
    body.setValue('INTERFACE',netmenu)
    body.setValue('PERCENTAGES',percentmenu)
    body.setValue('SERVICES',servicemenu)
    body.setValue('UPLINK',uplinkmenu)
    body.setValue('HOUR',_('Hour'))
    body.setValue('DAY',_('Today'))
    body.setValue('MAX_INTERFACES',6)
    body.setValue('Y_AXIS_TITLE',_('KB/s'))
    body.setValue('DATA_TS', time.strftime("%X"))
    body.display()

# modified by squall: Avoid showing python exceptions in front page
#cgitb.enable()
# end --------------

buildPage()
