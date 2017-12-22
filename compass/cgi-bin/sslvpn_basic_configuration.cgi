#!/usr/bin/perl
#
# openvpn CGI for Endian Firewall
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
require './endianinc.pl';
use Net::IPv4Addr qw (:all);
use File::Copy;
use File::Temp qw/ tempdir tempfile/;

my $passwd   = '/usr/bin/openvpn-sudo-user';
my $dirtyfile  = '/var/efw/openvpn/dirtyuserconfig';
my $conffile = "${swroot}/openvpn/settings";
my $conffile_default = "${swroot}/openvpn/default/settings";
my $hostconffile = "${swroot}/host/settings";
my $etherconf = "${swroot}/ethernet/settings";
my $openvpn_diffie = '/var/efw/openvpn/dh1024.pem';
my $openvpn_diffie_lock = '/var/lock/openvpn_diffie.lock';

my $PKCS_FILE = '/var/efw/openvpn/pkcs12.p12';
my $PKCS_IMPORT_FILE = "${PKCS_FILE}.import";
my $CACERT_FILE = '/var/efw/openvpn/cacert.pem';
my $CRL_FILE = '/var/efw/openvpn/crl.pem';
my $SUBJECT_FILE = '/var/efw/openvpn/subject.txt';
my $ISSUER_FILE = '/var/efw/openvpn/issuer.txt';


my $restart  = '/usr/local/bin/run-detached /usr/local/bin/restartopenvpn';

my $name        = _('OpenVPN server');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked="checked"');
my %selected = ();
my $self = $ENV{SCRIPT_NAME};

my %par;
my %confhash = ();
my $conf = \%confhash;
my $pool_begin = '';
my $pool_end = '';
my $port = '';
my $protocol = '';
my $netpart = undef;
my $ether = undef;
my $enabled = 0;
my $action = '';
my $errormessage = '';
my $warnmessage= "";
my $err = 1;
my $block_dhcp = '';
my $config = 0;
my %hosthash = ();
my $host = \%hosthash;

my $globalnetworks = '';
my $globalnameserver = '';
my $domain = '';
my ($a, $b);
my $abcast = '';
my $bnetwork = '';
my $needrestart = 0;
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'VPNS_FORM',
       'option'   :{
                    'PURPLE_NET':{
                               'type':'text',
                               'required':'1',
                               'check':'ip_mask|'
                             },
                    'OPENVPN_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|'
                             },
                    'IPPOOL_BEGIN':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                               'ajax': '1',
                               'ass_check':function(eve){
                                                                       var msg="";
                                                                       var title_ip;
                                                          var begin_ip = eve._getCURElementsByName("IPPOOL_BEGIN","input","VPNS_FORM")[0].value;
                                                          var end_ip = eve._getCURElementsByName("IPPOOL_END","input","VPNS_FORM")[0].value;
                                                          var new_ip_range = begin_ip+'-'+end_ip;
                                                                        var iface = eve._getCURElementsByName("BRIDGE_TO","select","VPNS_FORM")[0].value;
                                                          if(!eve.rangeip(new_ip_range)){
                                                              msg = '不能大于结束地址';
                                                          }
                                                          if (!eve.interface_ip){
                                                              \$.ajax({
                                                                    type : "get",
                                                                    url : '/cgi-bin/chinark_back_get.cgi',
                                                                    async : false,
                                                                    data : 'path=/var/efw/ethernet/settings',
                                                                    success : function(data){
                                                                        eve.interface_ip = data;
                                                                    }
                                                                    });
                                                          }       
                                                          var exist = eve.interface_ip.split('\\n');
                                                          for (var i = 0; i < exist.length; i++) {
                                                              var titles = iface+"_IPS";
                                                              var tmp = exist[i].split('=');
                                                              if(tmp[0] == titles){
                                                                title_ip = tmp[1];
                                                                break;
                                                              }
                                                          } 
                                                          if(iface == 'GREEN'){
                                                            if(!eve.same_green(begin_ip,title_ip)){
                                                              msg = '虚拟IP开始地址必须与%s接口同网段';
                                                            }
                                                          }
                                                          else{
                                                            if(!eve.same_orange(begin_ip,title_ip)){
                                                              msg = "虚拟IP开始地址必须与%s接口同网段";
                                                            }
                                                          }                                                                                           
                                                                                    return msg;
                                                      }
                             },
                    'IPPOOL_END':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                               'ass_check':function(eve){
                                                                       var msg="";
                                                          var title_ip;
                                                          var begin_ip = eve._getCURElementsByName("IPPOOL_BEGIN","input","VPNS_FORM")[0].value;
                                                          var end_ip = eve._getCURElementsByName("IPPOOL_END","input","VPNS_FORM")[0].value;
                                                          var new_ip_range = begin_ip+'-'+end_ip;
                                                           var iface = eve._getCURElementsByName("BRIDGE_TO","select","VPNS_FORM")[0].value;
                                                          if(!eve.rangeip(new_ip_range)){
                                                              msg = '不能小于开始地址';
                                                          }
                                                          if (!eve.interface_ip){
                                                              \$.ajax({
                                                                    type : "get",
                                                                    url : '/cgi-bin/chinark_back_get.cgi',
                                                                    async : false,
                                                                    data : 'path=/var/efw/ethernet/settings',
                                                                    success : function(data){
                                                                        eve.interface_ip = data;
                                                                    }
                                                                    });
                                                          }       
                                                          var exist = eve.interface_ip.split('\\n');
                                                          for (var i = 0; i < exist.length; i++) {
                                                              var titles = iface+"_IPS";
                                                              var tmp = exist[i].split('=');
                                                              if(tmp[0] == titles){
                                                                title_ip = tmp[1];
                                                                break;
                                                              }
                                                          } 
                                                          if(iface == 'GREEN'){
                                                            if(!eve.same_green(end_ip,title_ip)){
                                                              msg = '虚拟IP结束地址必须与%s接口同网段';
                                                            }
                                                          }
                                                          else{
                                                            if(!eve.same_orange(end_ip,title_ip)){
                                                              msg = "虚拟IP结束地址必须与%s接口同网段";
                                                            }
                                                          }                                                                     
                                                          return msg;
                                                      }
                             }
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("VPNS_FORM");
    </script>
EOF
,_('GREEN')
,_('ORANGE')
,_('GREEN')
,_('ORANGE')
;
}
sub checkuser() {
    if ($username !~ /^$/) {
    return 1;
    }
    $err = 0;
    $errormessage = _('Username not set.');
    return 0;
}

sub kill_vpn($) {
    my $user = shift;
    `$passwd kill \"$user\"`;
    `sudo fcmd $passwd kill "$user"`;
}

sub tos($){
    my $num = shift;
    my $mod = $num % 2;
    if ($num < 2) {
        return $num;
    }
    $num = ($num - $mod)/2;
    return tos($num).$mod;
        
}
sub my_warnbox($) {
    my $caption = shift;
    if ($caption =~ /^\s*$/) {
        return;
    }
    printf <<EOF
<div id="warning_box">
<img src='/images/dialog-warning.png' alt='_("Warning")' >
<span>$caption</span>
<form method='post' action='$self' enctype='multipart/form-data' style="margin-top:5px;">
  <input type='hidden' name='ACTION' value='restart' />
  <input type='submit' value='%s' class="net_button"/>
</form>
</div>
EOF
,_('restart')
,_('restart')
;
}

sub restart() {
    my $logid = "$0 [" . scalar(localtime) . "]";
    print STDERR `$restart --force`; 
    `sudo fcmd $restart --force`;
    print STDERR "$logid: restarting done\n";
    $needrestart = 1;
    #$notemessage = _('OpenVPN server has been restarted!');
}

sub doaction() {

    if (!$action) {
        return;
    }

    if ($action eq 'save') {
        ($err,$errormessage) = save();
        getconfig();
        $action = '';
        return;
    }
    if ($action eq 'RESET') {
        system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl /var/efw/openvpn/cacert.pem");
        system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl /var/efw/openvpn/dh1024.pem");
        system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl /var/efw/openvpn/pkcs12.p12");
        restart();
    }
    if ($action eq 'apply') 
    {
        restart();
        $warnmessage= "";
        `rm $dirtyfile`;
        return;
    }
    
    if ($action eq 'kill') {
        if (!checkuser()) {
            return;
        }

        kill_vpn($username);
        return;
    }

}

sub human_time($) {
    my $seconds = shift;
    use integer;

    my $days = $seconds / 86400;
    $seconds -= $days * 86400;
    my $hours = $seconds / 3600;
    $seconds -= $hours * 3600;
    my $minutes = $seconds / 60;
    $seconds -= $minutes * 60;

    my $ret = '';
    if ($days != 0) {
    $ret .= $days.'d ';
    }
    if ($hours != 0) {
    $ret .= $hours.'h ';
    }
    if ($minutes != 0) {
    $ret .= $minutes.'m ';
    }
    if ($ret eq '') {
    $ret = '< 1m';
    }
    return $ret;
}


sub shorten($) {
    my $val = shift;
    return int($val * 10) / 10;
}

sub human_bytes($) {
    my $bytes = shift;

    my $giga = $bytes / 1073741824;
    if ($giga > 1.4) {
    return shorten($giga) . ' GiB';
    }
    my $mega = $bytes / 1048576;
    if ($mega > 1.4) {
    return shorten($mega) . ' MiB';
    }
    my $kilo = $bytes / 1024;
    if ($kilo > 1.4) {
    return shorten($kilo) . ' KiB';
    }
    return $bytes . 'b';
}

sub list_connections() {
    openbox('100%', 'left', _('Connection status and control'));

    my @conn = split(/\n/, `$passwd status`);
    my $i = 0;

    printf <<EOF
    <br />
<table class="ruleslist" cellpadding="0" cellspacing="0" width="100%" border='0'>
  <tr>
    <td width="18%" class="boldbase"><b>%s</b></td>
    <td width="9%"  class="boldbase"><b>%s</b></td>
    <td width="13%" class="boldbase"><b>%s</b></td>
    <td width="16%" class="boldbase"><b>%s / %s</b></td>
    <td width="21%" class="boldbase"><b>%s</b></td>
    <td width="10%" class="boldbase"><b>%s</b></td>
    <td width="13%" align="center" class="boldbase"><b>%s</b></td>
  </tr>
EOF
,
_('User'),
_('Assigned IP'),
_('Real IP'),
_('RX'),
_('TX'),
_('开始连接时间'),
_('Uptime'),
_('Cut connections')
;

    my $length = @conn;
    my $count = 0;
    foreach my $line (@conn) {
        my @split = split(/,/, $line);
        if ($split[0] ne 'CLIENT_LIST') {
            next;
            }
            $count++;
    }
    if($count >0)
    {
    foreach my $line (@conn) {
    my @split = split(/,/, $line);
    if ($split[0] ne 'CLIENT_LIST') {
        next;
    }
    my $oddeven = 'oodd';
    if ($i % 2) {
        $oddeven = 'even';
    }
    my $conntime = human_time(time() - $split[7]);
    my $user = $split[1];
    my $rx = human_bytes($split[4]);
    my $tx = human_bytes($split[5]);

    my $realip = $split[2];
    $realip =~ s/:.*$//;

#CLIENT_LIST,r3,80.108.92.192:49542,192.168.0.180,68830,67705,Wed Feb 23 07:56:26 2005,1109141786
    my $deal_date = deal_date($split[6]);
    $deal_date =~s/(.*)\s(\d+):(\d+):(\d+)/$1 $2:$3:$4/;
    printf <<EOF
  <tr class="$oddeven">
    <td>$user</td>
    <td>$split[3]</td>
    <td>$realip</td>
    <td nowrap='nowrap'>$rx / $tx</td>
    <td nowrap='nowrap'>$deal_date</td>
    <td nowrap='nowrap'>$conntime</td>
    <td nowrap='nowrap' style="text-align:center;">
      <form method="post" action="$self" style="display:inline;">
        <input class='submitbutton' type='image' name="submit" value="kill" src="/images/cut.png" >
        <input type="hidden" name="username" value="$user">
        <input type="hidden" name="ACTION" value="kill">
      </form>
    </td>
  </tr>
EOF
;

    $i++;
    }
}else{
    no_tr(7,_("Current no content"));
}
    print '</table></br>';


    closebox();
     print '</br>';
}

sub ip2long {
    return unpack("l*", pack("l*", unpack("N*", inet_aton(shift))));
}

sub long2ip {
    return inet_ntoa(pack("N*", shift));
}

sub smallPools($$) {
    my $netaddress = shift;
    my $cidr = shift;
    my $ip = $netaddress;
    my $cidr = int($cidr) + 1;

    my $a = "$ip/$cidr";

    my $broadcast = ipv4_broadcast($a);
    $ip = long2ip(ip2long($broadcast) + 1);
    my $b = "$ip/$cidr";

    return ($a, $b);
}

sub checkSubnetInZone($) {
    my $subnet = shift;

    my $zones = validzones();
    foreach my $zone (@$zones) {
    next if ($zone eq 'RED');
    my @ips = split(/,/, $ether->{uc($zone) . "_IPS"});
    foreach my $zonenet (@ips) {
            if (ipv4_in_network($subnet, $zonenet)) {
        return($zone, $zonenet);
        }
    }
    }
    return (0,0);
}

sub save () {

    $config = \%par;
    my $logid = "$0 [" . scalar(localtime) . "]";
    my $needrestart = 0;
    my $ippool_begin = $par{IPPOOL_BEGIN};
    my $ippool_end = $par{IPPOOL_END};
    $block_dhcp = $par{DROP_DHCP};
    $port = $par{OPENVPN_PORT};
    $protocol = $par{OPENVPN_PROTOCOL};
    local $auth_type = $par{AUTH_TYPE};
    my $ret = 0;
    my $error = '';
    my $purple_net = $par{'PURPLE_NET'};
    ######changed by elvis 2012-8-2 for IP comparison  END at line 449
      my $begin = 1,$end = 1;
      my $green0 = 1;
      my $orange0 = 1,$blue0 = 1;
      ###将结束地址和起始地址转换为二进制数，且为补满0的八位,以下会对各接口的IP作相同的处理再来比对是否同网段
      foreach my $ip (split(/\./,$ippool_begin)) {
           $ip = tos($ip);
           $ip=~s/(\d+)/sprintf("%08s",$1)/eg;
           $begin .= $ip;
      }
      foreach my $ip (split(/\./,$ippool_end)) {
          $ip = tos($ip);
          $ip=~s/(\d+)/sprintf("%08s",$1)/eg;
          $end .= $ip;
      }
     ###起止转换结束，以下各判断语句为各网段的转换
    if ($par{'BRIDGED'} eq 'on') {
        if (!validip($ippool_begin) ||
            !validip($ippool_end)) {
            return (0, _('Invalid IP address'));
        }
        if (ip2long($ippool_begin)  >= ip2long($ippool_end)) {
            return (0, _('Pool start IP must be lesser than end ip!'));
        }
        if ($par{'BRIDGE_TO'} eq 'GREEN') {
            my @green_ips = split(/,/, $ether->{GREEN_IPS});
            my $valid_check = 0;
            foreach my $ont_green_ip_item (@green_ips){
                chomp($ont_green_ip_item);
                $ont_green_ip_item =~ /(.*)\/(\d+)/;
                my $green_ip = $1;
                my $mask = $2;
                foreach my $ip (split(/\./,$green_ip)) {
                    $ip = tos($ip);
                    $ip=~s/(\d+)/sprintf("%08s",$1)/eg;
                    $green0 .= $ip;
                }
                if (substr($begin,1,$mask) eq substr($green0,1,$mask)) {
                    if (substr($end,1,$mask) eq substr($green0,1,$mask)) {
                        $valid_check = 1;
                    }
                }
                $green0 = 1;
            }
            if(! $valid_check){
                return (0, "虚拟IP开始和结束地址必须与"._('GREEN')."接口同网段!");
            }
        }
        
        if ($par{'BRIDGE_TO'} eq 'ORANGE') {
            my @orange_ips = split(/,/, $ether->{ORANGE_IPS});
            my $valid_check = 0;
            foreach my $ont_orange_ip_item (@orange_ips){
                chomp($ont_orange_ip_item);
                $ont_orange_ip_item =~ /(.*)\/(\d+)/;
                my $orange_ip = $1;
                my $mask = $2;
                foreach my $ip (split(/\./,$orange_ip)) {
                    $ip = tos($ip);
                    $ip=~s/(\d+)/sprintf("%08s",$1)/eg;
                    $orange0 .= $ip;
                }
                if (substr($begin,1,$mask) eq substr($orange0,1,$mask)) {
                    if (substr($end,1,$mask) eq substr($orange0,1,$mask)) {
                        $valid_check = 1;
                    }
                }
                $orange0 = 1;
            }
            if(! $valid_check){
                return (0, "虚拟IP开始和结束地址必须与"._('ORANGE')."接口同网段!");
            }
        }
        
        if ($par{'BRIDGE_TO'} eq 'BLUE') {
            my @blue_ips = split(/,/, $ether->{BLUE_IPS});
            my $valid_check = 0;
            foreach my $ont_blue_ip_item (@blue_ips){
                chomp($ont_blue_ip_item);
                $ont_blue_ip_item =~ /(.*)\/(\d+)/;
                my $blue_ip = $1;
                my $mask = $2;
                foreach my $ip (split(/\./,$blue_ip)) {
                    $ip = tos($ip);
                    $ip=~s/(\d+)/sprintf("%08s",$1)/eg;
                    $blue0 .= $ip;
                }
                if (substr($begin,1,$mask) eq substr($blue0,1,$mask)) {
                    if (substr($end,1,$mask) eq substr($blue0,1,$mask)) {
                        $valid_check = 1;
                    }
                }
                $blue0 = 1;
            }
            if(! $valid_check){
                return (0, "虚拟IP开始和结束地址必须与"._('BLUE')."接口同网段!");
            }
        }
############changed by elvis 2012-8-2 for IP comparison   BEGIN at line 377
    } else {
        $par{'BRIDGED'} = 'off';
        if (!validipandmask($purple_net)) {
            return (0, _("子网网段输入不合法", $purple_net));
        }
        
        `/usr/local/bin/checkNetAddr $purple_net`;
        open(FILE,'/var/efw/openvpn/netaddr_result');
        my $result = <FILE>;
        close(FILE);
        if($result eq '0' )
        {
           return (0, _("保存失败，子网%s不能和系统已使用的子网段重复！", $purple_net));
        }
        
        my ($conflictzone, $conflictnet) = checkSubnetInZone($par{'PURPLE_NET'});
        if ($confictzone) {
            return (0, _('VPN subnet conflicts with %s of zone %s.',
                 $conflictnet,
                 $string_zone{$conflictzone}));
        }
    }

    # XXX: vpn ippool and green dhcp ip pool has to be disjunct! check it!

    if (! validport($par{OPENVPN_PORT})) {
    return (0, _('Invalid port'));
    }

    if ( ($conf->{PURPLE_IP_BEGIN} ne $ippool_begin) or
     ($conf->{PURPLE_IP_END} ne $ippool_end) or
     ($conf->{CLIENT_TO_CLIENT} ne $par{CLIENT_TO_CLIENT}) or
     ($conf->{DROP_DHCP} ne $par{DROP_DHCP}) or
     ($conf->{OPENVPN_PORT} ne $par{OPENVPN_PORT}) or
     ($conf->{OPENVPN_PROTOCOL} ne $par{OPENVPN_PROTOCOL}) or
     ($conf->{PUSH_GLOBAL_NETWORKS} ne $par{PUSH_GLOBAL_NETWORKS}) or
     ($conf->{GLOBAL_NETWORKS} ne $par{GLOBAL_NETWORKS}) or
     ($conf->{PUSH_GLOBAL_DNS} ne $par{PUSH_GLOBAL_DNS}) or
     ($conf->{GLOBAL_DNS} ne $par{GLOBAL_DNS}) or
     ($conf->{PUSH_DOMAIN} ne $par{PUSH_DOMAIN}) or
     ($conf->{DOMAIN} ne $par{DOMAIN}) or
     ($conf->{OPENVPN_ENABLED} ne $par{ENABLE}) or
     ($conf->{BRIDGED} ne $par{BRIDGED}) or
     ($conf->{BRIDGE_TO} ne $par{BRIDGE_TO}) or
     ($conf->{PURPLE_NET} ne $par{PURPLE_NET}) or
     ($conf->{AUTH_TYPE} ne $par{AUTH_TYPE})
     ) {
    print STDERR "$logid: writing new configuration file\n";
    $needrestart = 1;
    $conf->{PURPLE_IP_BEGIN} = $ippool_begin;
    $conf->{PURPLE_IP_END} = $ippool_end;
    $conf->{CERT_AUTH} = $par{CERT_AUTH};
    $conf->{DROP_DHCP} = $par{DROP_DHCP};

    $conf->{OPENVPN_PROTOCOL} = $par{OPENVPN_PROTOCOL};
    $conf->{OPENVPN_PORT} = $par{OPENVPN_PORT};
    $conf->{AUTH_TYPE} = $par{AUTH_TYPE};

    $conf->{PUSH_GLOBAL_NETWORKS} = $par{PUSH_GLOBAL_NETWORKS};
    $conf->{PUSH_GLOBAL_DNS} = $par{PUSH_GLOBAL_DNS};
    $conf->{GLOBAL_NETWORKS} = $par{GLOBAL_NETWORKS};
    $conf->{GLOBAL_DNS} = $par{GLOBAL_DNS};
    $conf->{GLOBAL_NETWORKS} =~ s/[\r\n]+/,/g;
    $conf->{GLOBAL_DNS} =~ s/[\r\n]+/,/g;

    $conf->{PUSH_DOMAIN} = $par{PUSH_DOMAIN};
    $conf->{DOMAIN} = $par{DOMAIN};

    $conf->{CLIENT_TO_CLIENT} = $par{CLIENT_TO_CLIENT};
    $conf->{OPENVPN_ENABLED} = $par{ENABLE};

    $conf->{BRIDGED} = $par{BRIDGED};
    $conf->{BRIDGE_TO} = $par{BRIDGE_TO};
    $conf->{PURPLE_NET} = $par{PURPLE_NET};

    $config = $conf;

    writehash($conffile, $conf);
    `sudo fmodify $conffile`;
        &log(_('Written down Openvpn configuration'));
    }

    if (!$enabled and $par{ENABLE} eq 'on') {
        print STDERR "$logid: changing status from 'off' -> 'on'\n";
        $needrestart = 1;
        $enabled = 1;
    } elsif ($enabled and $par{ENABLE} ne 'on') {
        print STDERR "$logid: changing status from 'on' -> 'off'\n";
        $needrestart = 1;
        $enabled = 0;
    }
    `touch $dirtyfile`;
    #print STDERR `$restart --force`; 
    #print STDERR "$logid: restarting done\n";
    return 1;
}

sub read_file($) {
    my $f = shift;
    open (CA, $f) || return _("Could not open file '%s'.", $f);
    my $str = <CA>;
    close CA;
    return $str;
}

sub display() {
    if ($config->{'AUTH_TYPE'} =~ /^$/) {
        $config->{'AUTH_TYPE'} = 'psk';
    }

    $selected{'OPENVPN_PROTOCOL'}{uc($protocol)} = 'selected';
    $selected{'BRIDGE_TO'}{uc($config->{'BRIDGE_TO'})} = 'selected="selected"';
    $selected{$config->{'BRIDGED'}} = 'selected="selected"';
    my %authtype = ();
    $authtype{$config->{'AUTH_TYPE'}} = 'checked="checked"';

    my $canreadpkcs = 0;
    if (open F, $PKCS_FILE) {
        $canreadpkcs = 1;
        close(F);
    }

    my $canreadcacert = 0;
    if (open F, $CACERT_FILE) {
        $canreadcacert = 1;
        close(F);
    }

    my $displaypsk = 'display: none';
    if ($config->{'AUTH_TYPE'} eq 'psk') {
        $displaypsk = 'display: block';
    }

    my $displaycert = 'display: none';
    if ($config->{'AUTH_TYPE'} =~ /cert/) {
        $displaycert = 'display: block';
    }

    if (($pool_begin eq '') && ($pool_end eq '')) {
    if ($ether->{'GREEN_CIDR'} <= 28) {
        my ($a, $b) = smallPools($ether->{'GREEN_NETADDRESS'}, $ether->{'GREEN_CIDR'});
        my ($ip, $cidr) = split(/\//, $b);
        ($a, $b) = smallPools($ip, $cidr);
        ($pool_begin, ) = split(/\//, $a);
        ($pool_end, ) = split(/\//, $b);
        $pool_begin = long2ip(ip2long($pool_begin) + 1);
        $pool_end = long2ip(ip2long($pool_end) - 2);
    }
    }
 ####help_msg
    my $help_hash1 = read_json("/home/httpd/help/openvpn_server_help.json","openvpn_server.cgi","桥","-10","30","down");
    my $help_hash2 = read_json("/home/httpd/help/openvpn_server_help.json","openvpn_server.cgi","bridge_to","-10","30","down");
    my $help_hash3 = read_json("/home/httpd/help/openvpn_server_help.json","openvpn_server.cgi","虚拟ip池开始地址","-10","30","down");
    my $help_hash4 = read_json("/home/httpd/help/openvpn_server_help.json","openvpn_server.cgi","虚拟ip池结束地址","-10","30","down");
    my $help_hash5 = read_json("/home/httpd/help/openvpn_server_help.json","openvpn_server.cgi","VPN_subnet","-10","30","down");
    ###
    printf <<EOF
<form name='VPNS_FORM' method='post' action='$self' enctype='multipart/form-data'>
  <input type='hidden' name='ACTION' id="ACTION" value='save' />
  <input type='hidden' name='CLIENT_TO_CLIENT' value='$config->{'CLIENT_TO_CLIENT'}' />
  <input type='hidden' name='DROP_DHCP' value='$config->{'DROP_DHCP'}' />
  <input type='hidden' name='AUTH_TYPE' value='$config->{'AUTH_TYPE'}' />
  <input type='hidden' name='PUSH_GLOBAL_NETWORKS' value='$config->{'PUSH_GLOBAL_NETWORKS'}'>
  <input type='hidden' name='GLOBAL_NETWORKS' value='$config->{'GLOBAL_NETWORKS'}'>
  <input type='hidden' name='PUSH_GLOBAL_DNS' value='$config->{'PUSH_GLOBAL_DNS'}'>
  <input type='hidden' name='GLOBAL_DNS' value='$config->{'GLOBAL_DNS'}'>
  <input type='hidden' name='PUSH_DOMAIN' value='$config->{'PUSH_DOMAIN'}'>
  <input type='hidden' name='DOMAIN' value='$config->{'DOMAIN'}'>

EOF
;

    openbox('100%', 'left', '基本配置');
    printf <<EOF
<table cellpadding="0" cellspacing="0" width="100%" border='0' >
  <tr class="env hidden_class">
    <td width="30%">%s</td>
    <td><input type='checkbox' value='on' name='ENABLE' $checked{$enabled} /></td>
  </tr>

  <tr class="odd">
    <td class="add-div-type need_help">%s </td>
    <td class="need_help"><select id='bridged' name="BRIDGED" value="$config->{'BRIDGED'}" onchange="toggleBridged();" style="width:114px"/>
        <option value="on" $selected{'on'}>桥接模式</option>
        <option value="off" $selected{'off'}>子网模式</option>
        </select> $help_hash1</td>
  </tr>

  <tr class="env" id="purplenet">
    <td class="add-div-type need_help">%s </td>
    <td class="need_help"><input type='text' name='PURPLE_NET' value="$config->{'PURPLE_NET'}" SIZE="18" MAXLENGTH="18" style="width:110px"/>$help_hash5</td>
  </tr>

  <tr class="env" id="bridgeto">
    <td class="add-div-type">%s </td>
    <td class="need_help">
      <select name="BRIDGE_TO" style="width:114px">
EOF
, _('OpenVPN server enabled')
, '启用模式'
, '虚拟子网网段*'
, '桥接到'
;

    my $zones = validzones();
    foreach my $zone (@$zones) {
    next if ($zone eq 'RED');
    printf <<EOF
        <option value="$zone" $selected{'BRIDGE_TO'}{$zone}>%s</option>
EOF
, $strings_zone{$zone}
;
    }

    printf <<EOF
      </select>$help_hash2
    </td>
  </tr>

  <tr class="odd" id="ippoolbegin">
    <td  class="add-div-type need_help">%s *$help_hash3</td>
    <td><input type='text' name='IPPOOL_BEGIN' value="$pool_begin" SIZE="14" MAXLENGTH="15" />&nbsp;&nbsp;%s</td>
  </tr>

  <tr class="env" id="ippoolend">
    <td class="add-div-type need_help">%s *$help_hash4</td>
    <td><input type='text' name='IPPOOL_END' value="$pool_end" SIZE="14" MAXLENGTH="15" /></td>
  </tr>
  <tr class="odd">
    <td  class="add-div-type need_help">VPN监听的端口 *</td>
    <td><input type='text' name='OPENVPN_PORT' value="$config->{'OPENVPN_PORT'}" SIZE="14" MAXLENGTH="5" />(默认端口1194，若本设备没有直连外网，请在前端设备上做该端口的映射给本设备)</td>
  </tr>

  <tr class="env">
    <td class="add-div-type need_help">VPN使用的通信协议 *$help_hash4</td>
    <td>
      <select name="OPENVPN_PROTOCOL" style="width:114px">
        <option value="tcp" $selected{'OPENVPN_PROTOCOL'}{'TCP'}>TCP</option>
        <option value="udp" $selected{'OPENVPN_PROTOCOL'}{'UDP'}>UDP</option>
      </select>    
    </td>
  </tr>
  <tr class="table-footer">
    <td colspan="2">
      <input class='submitbutton net_button' type='submit' name='ACTION_RESTART' value='%s' />&nbsp;&nbsp;
EOF
, '虚拟IP池开始地址'
, ''
, '虚拟IP池结束地址'
, _('Save')
;
    if ($canreadcacert) {
        printf <<EOF
    <input class='submitbutton net_button' type='submit' name='ACTION_RESTART' onclick='change_action();' value='更新证书' />&nbsp;&nbsp;
      <a href="showca.cgi?type=pem">%s</a>
EOF
, _('Download CA certificate')
;
    } else {
  printf <<EOF
      &nbsp;
EOF
;
    }


printf <<EOF
    </td>
  </tr>

</table>
</form>
EOF
;

    closebox();


}


# -------------------------------------------------------------
# get settings and CGI parameters
# -------------------------------------------------------------
sub getconfig () {

    if (-e $hostconffile) {
    readhash($hostconffile, $host);
    }
    if (-e $conffile_default) {
    readhash($conffile_default, $conf);
    }
    if (-e $conffile) {
    readhash($conffile, $conf);
    $pool_begin = $conf->{PURPLE_IP_BEGIN};
    $pool_end = $conf->{PURPLE_IP_END};
    }

    my $greenaddress = '';
    if (-e $etherconf) {
    $ether = readconf($etherconf);

    my @green = split(/\./, $ether->{GREEN_ADDRESS});
    $netpart = $green[0].'.'.$green[1].'.'.$green[2];
    $greenaddress = $ether->{GREEN_ADDRESS};
    }

    $block_dhcp = $conf->{DROP_DHCP};
    $port = $conf->{OPENVPN_PORT};
    $protocol = $conf->{OPENVPN_PROTOCOL};

    $globalnetworks = $conf->{GLOBAL_NETWORKS};
    $globalnameserver = $conf->{GLOBAL_DNS};
    $domain = $conf->{DOMAIN};

    $globalnetworks =~ s/,/\n/g;
    $globalnameserver =~ s/,/\n/g;
    if ($domain =~ /^$/) {
        $domain = $host->{'DOMAINNAME'};
    }
    if ($globalnameserver =~ /^$/) {
    $globalnameserver = $greenaddress;
    }

    if ($conf->{'OPENVPN_ENABLED'} eq 'on') {
    $enabled = 1;
    }
    $config = $conf;

}

sub sanitize($) {
    my $data = shift;
    $data =~ s/\"/\\\"/;
    return $data;
}

getconfig();
getcgihash(\%par);
$action = $par{ACTION};


# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------

$username = sanitize($par{'username'});
doaction();


# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------

showhttpheaders();
my $extraheader = '<script language="JavaScript" src="/include/switchVisibility.js"></script>';

$extraheader .="
        <script type=\"text/javascript\">
            function toggleBridged() {
                var checked = document.getElementById('bridged').value;
                if (checked =='on') {
                    \$('#bridgeto').css({'display':'table-row'});
                    \$('#ippoolbegin').css({'display':'table-row'});
                    \$('#ippoolend').css({'display':'table-row'});
                    \$('#purplenet').css({'display':'none'});
                } else {
                    \$('#bridgeto').css({'display':'none'});
                    \$('#ippoolbegin').css({'display':'none'});
                    \$('#ippoolend').css({'display':'none'});
                    \$('#purplenet').css({'display':'table-row'});
                }
            }
            \$(document).ready(function () {toggleBridged();});
            function change_action(){
                \$('#ACTION').val('RESET');
            }
        </script>
";

openpage($name, 1, $extraheader);

if (! -e $openvpn_diffie && -e $openvpn_diffie_lock) {
    $notemessage=_('OpenVPN is generating the Diffie Hellman parameters. This will take several minutes. During this time OpenVPN can <b>not</b> be started!');
    $notemessage .= "请稍后刷新。";
}

$service_restarted = $needrestart;
if ($needrestart) {
    service_notifications(["openvpnserver"], 
                      {'type' => $service_restarted == 1 ? "commit" : 
                                                           "observe",
                       'interval' => 1000, 
                       'startMessage' => _("OpenVPN server is being restarted". 
                                           " Please hold..."),
                       'endMessage' => _("OpenVPN server was restarted " . 
                                         "successfully ")});
}

#sleep(1);
openbigbox($errormessage,"", $notemessage);
if (-e $dirtyfile) {
    $warnmessage =_('Configuration has been changed.You may need to restart openVPN server in order to make the changes active.Clients will reconnect automatically after the restart.');
    applybox($warnmessage);
}
display();

closebigbox();

openbigbox();
list_connections();
check_form();
closebigbox();

closepage();

