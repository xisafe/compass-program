#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 系统状态页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================

require '/var/efw/header.pl';
require '/home/httpd/cgi-bin/endianinc.pl';
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
&validateUser();
my (%netsettings);
&readhash("${swroot}/ethernet/settings", \%netsettings);

my %disk_name = (
	'/s'       => _('Main disk'),
	'/var'     => _('Data disk'),
	'/var/efw' => _('Config disk'),
	'/var/log' => _('Log disk'),
	);

my %cgiparams;
#2013-7-22屏蔽入侵防御显示
 #_('入侵防御系统') => ['suricata', '/var/run/snort_eth0.pid','' ],
 #
my %servicenames = (
            _('时间同步服务')       => ['ntpd', '', ''],
            _('DHCP服务')           => ['dhcpd', '', ''],
            _('SNMP服务')           => ['snmpd', '', ''],
            #_('RIP动态路由')        => [],
            #_('OSPF动态路由')       => [],
            _('入侵防御')           => ['snort', '/var/run/snort_0.pid','' ],
            _('用户认证')           => ['aaaDaemon.py', '', 'start'],
            _('流量统计')           => ['trafficstat', '', ''],

            _('SSL VPN')            => ['openvpn0', '/var/run/openvpn/openvpn0.pid', ''],
            _('IPSEC VPN')          => ['pluto', '/var/run/pluto/pluto.pid', ''],
            _('L2TP VPN')           => ['xl2tpd', '/var/run/xl2tpd.pid', ''],
            _('PPTP VPN')           => ['pptpd', '', ''],

            _('双机热备')           => ['keepalived', '', ''],
            _('服务器负载均衡')     => ['loadbalanced.py', '', 'start'],

            _('WEB内容过滤')        => ['squid', '', ''],
            #_('发送邮件过滤')       => ['postfix', '', ''],
            _('发送邮件过滤')       => ['master', '/var/spool/postfix/pid/master.pid', ''],
            _('接收邮件过滤')       => ['p3scan', '/var/run/p3scan/p3scan.pid', ''],
            _('DNS过滤')            => ['dnsmasq', '', ''],
            _('FTP过滤')            => ['frox', '/var/run/frox/frox.pid', ''],

            #_('网管服务') => ['httpd', '', ''],
            #_('日志记录服务') => ['syslog-ng', '', ''],
            #_('HTTP病毒扫描') => ['havp', '/var/run/havp/havp.pid', ''],
            #_('病毒扫描') => ['clamd', '/var/run/clamav/clamd.pid', ''],
            );

init_register_status(\%servicenames);

foreach my $regfile (glob("/home/httpd/cgi-bin/status-*.pl")) {
    require $regfile;
}


printf <<END
    <table width='100%' cellspacing='0' border='0' >
END
;

my $lines = 0;
my $length = 0;
foreach my $key (sort keys(%servicenames)) {
	$length++;
}

foreach my $key (sort keys(%servicenames)) {
    my $color = 'odd';
	$color = 'odd';
    my $statuscolor = "";
    my $statuscaption = "[ "._('STOPPED')." ]";
    if (isrunning($servicenames{$key})) {
	$statuscolor = "note";
	$statuscaption = _('RUNNING')."  <image src='/images/running.gif'  style='margin:0px 0px -5px 5px'  />";
    }

    if (!($lines % 2)) {
    printf <<END
        <tr>
            <td  style='line-height:25px;border-bottom:1px dotted #999' class='$statuscolor'  >$key </td><td   class='$statuscolor'  style='line-height:25px;border-bottom:1px dotted #999;width:70px;'> $statuscaption </td>
END
;
}else{
	 printf <<END
            <td  style='line-height:25px;border-bottom:1px dotted #999'  class='$statuscolor'>$key </td><td class='$statuscolor' style='line-height:25px;border-bottom:1px dotted #999;width:70px;'>  $statuscaption</td> </tr>
END
;
}
	 $lines++;
}

if($length %2)
{
	print "<td></td><td></td></tr>";
}
print '</table>';

