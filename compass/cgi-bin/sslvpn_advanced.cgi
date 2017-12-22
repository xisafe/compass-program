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
use IPC::Open3;
use CGI::Carp qw (fatalsToBrowser);
use CGI qw(:standard);
my $dirtyfile  = '/var/efw/openvpn/dirtyuserconfig';
my $conffile = "${swroot}/openvpn/settings";
my $conffile_default = "${swroot}/openvpn/default/settings";
my $hostconffile = "${swroot}/host/settings";
my $etherconf = "${swroot}/ethernet/settings";
my $restart  = '/usr/local/bin/run-detached /usr/local/bin/restartopenvpn';
my $openvpn_diffie = '/var/efw/openvpn/dh1024.pem';
my $openvpn_diffie_lock = '/var/lock/openvpn_diffie.lock';
my $client_file = '/home/httpd/sslvpn/dingdian_SSL_VPN/config/client.vpn';

my $PKCS_FILE = '/var/efw/openvpn/pkcs12.p12';
my $PKCS_IMPORT_FILE = "${PKCS_FILE}.import";
my $CACERT_FILE = '/var/efw/openvpn/cacert.pem';
my $CRL_FILE = '/var/efw/openvpn/crl.pem';
my $SUBJECT_FILE = '/var/efw/openvpn/subject.txt';
my $ISSUER_FILE = '/var/efw/openvpn/issuer.txt';
my $gen_cert = '/usr/local/bin/openvpngencsr';
my $modify_cert = 'sudo /usr/local/bin/openvpnmodifycert';
my $check_input = 'sudo /usr/local/bin/check_input_CRL';

my $uplink_settings = "/var/efw/uplinks/main/settings";
my %uplink_settings_hash;
readhash($uplink_settings, \%uplink_settings_hash);
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

sub restart() {
    my $logid = "$0 [" . scalar(localtime) . "]";
    print STDERR `$restart --force`; 
    print STDERR "$logid: restarting done\n";                
    `sudo fcmd $restart --force`;
    $notemessage = _('OpenVPN server has been restarted!');
}

sub ip2long {
    return unpack("l*", pack("l*", unpack("N*", inet_aton(shift))));
}

sub long2ip {
    return inet_ntoa(pack("N*", shift));
}
sub check_form_crl(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'CRL_FORM',
       'option'   :{
                    'CRL_ADDR':{
                               'type':'text',
                               'required':'1',
                               'check':'url|'
                             }
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("CRL_FORM");
    </script>
EOF
;
}
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'ADVANCED_FORM',
       'option'   :{
                    'PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|'
                             },
                    'OUT_IP':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|domain|'
                             },
                    'MAIN_DNS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'SECOND_DNS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'OUT_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|'
                             },
                    'DOMAIN':{
                               'type':'text',
                               'required':'0',
                               'check':'domain_suffix|'
                             },
                    'GLOBAL_NETWORKS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'other|',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg = ""; 
                                                        var ips = eve._getCURElementsByName("GLOBAL_NETWORKS","textarea","ADVANCED_FORM")[0].value;
                                                        var ip = ips.split("\\n");
                                                        if(ips = ' '){
                                                          return msg;
                                                        }
                                                        if(ips.length==1&&ip[0]=='')
                                                        {
                                                           return msg;
                                                        }
                                                        
                                                        for(var i=0;i<ip.length;i++)
                                                        {
                                                           msg = '';
                                                           if(ip[i]!='')
                                                           {
                                                              var one_split = ip[i].split("/");
                                                              var one_ip = one_split[0];
                                                              var mask = one_split[1];
                                                              var zero = /^0+/;
                                                              
                                                              if (mask < 1 || mask >32 || one_split.length != 2 || zero.test(mask)){
                                                                  msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
                                                                  return msg;
                                                              }
                                                              
                                                              var ip_reg = /^([1-9]|[1-9]\\d|1\\d{2}|2[0-1]\\d|22[0-3])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3}\$/;
                                                              if(!ip_reg.test(one_ip))
                                                              {
                                                                  msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
                                                                  return msg;
                                                              }
                                                              var total_str = "";
                                                              var temp = new Array(); 
                                                              temp = one_ip.split(".");
                                                              for (var j = 0;j < 4;j ++){
                                                                 temp[j] = parseInt(temp[j]);
                                                                 temp[j] = eve.formatIP(temp[j]);
                                                                 total_str += temp[j];
                                                              }
                                                              var segment = total_str.substring(mask);
                                                              var all_zero = /^0+\$/;
                                                              if(mask==32||all_zero.test(segment))
                                                              {
                                                              } else {
                                                                 msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
                                                                 return msg;
                                                              }
                                                           } else {
                                                              msg = '不能出现空行！';
                                                              return msg;
                                                           }
                                                        }
                                                        return msg;
                                                     }
                                            
                             },
                    'GLOBAL_DNS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|'
                             }
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("ADVANCED_FORM");
    
    var object2 = {
       'form_name':'IMPORT_FORM',
       'option'   :{
                    'device_key':{
                               'type':'file',
                               'required':'1'
                             },
                    'ca_key':{
                               'type':'file',
                               'required':'1'
                             }
                 }
         }
    var check2 = new ChinArk_forms();
    check2._main(object2);
    //check2._get_form_obj_table("IMPORT_FORM");
    
    var object3 = {
       'form_name':'MAKE_FORM',
       'option'   :{
                    'cert_country':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[A-Z]{2}\$/'
                             },
                    'cert_department':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[a-zA-Z]{1,10}\$/'
                             },
                    'cert_province':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[a-zA-Z]{1,10}\$/'
                             },
                    'cert_to':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[a-zA-Z]{1,10}\$/'
                             },
                    'cert_city':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[a-zA-Z]{1,10}\$/'
                             },
                    'cert_email':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|'
                             },
                    'cert_company':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[a-zA-Z]{1,10}\$/'
                             }
                 }
         }
    var check3 = new ChinArk_forms();
    check3._main(object3);
    //check3._get_form_obj_table("MAKE_FORM");
    </script>
EOF
;
}
sub save_client_file($$$$){
    my $ip = shift;
    my $port = shift;
    my $proto = shift;
    my $out_port = shift;
    if($uplink_settings_hash{'RED_TYPE'} eq "NONE") {
        $port = $out_port;
    }
    open(FILE,">$client_file");
    print FILE "client\n";
    print FILE "dev tap\n";
    print FILE "proto $proto\n";
    print FILE "remote $ip $port\n";
    print FILE "auth-user-pass\n";
    print FILE "resolv-retry 3\n";
    print FILE "nobind\n";
    print FILE "persist-key\n";
    print FILE "persist-tun\n";
    print FILE "ca dingdian.pem\n";
    print FILE "comp-lzo\n";
    print FILE "verb 3\n";
    close(FILE);
    `sudo fmodify $client_file`;
}
sub smallPools() {
    my $ip = $ether->{GREEN_NETADDRESS};
    my $cidr = int($ether->{GREEN_CIDR}) + 1;

    my $a = "$ip/$cidr";

    my $broadcast = ipv4_broadcast($a);
    $ip = long2ip(ip2long($broadcast) + 1);
    my $b = "$ip/$cidr";

    return ($a, $b);
}

sub save () {

    $config = \%par;
    my $logid = "$0 [" . scalar(localtime) . "]";
    my $needrestart = 0;
    my $ippool_begin = $par{PURPLE_IP_BEGIN};
    my $ippool_end = $par{PURPLE_IP_END};
    $block_dhcp = $par{DROP_DHCP};
    $port = $par{OPENVPN_PORT};
    $protocol = $par{OPENVPN_PROTOCOL};
    local $auth_type = $par{AUTH_TYPE};
    my $ret = 0;
    my $error = '';
    ####如果自动撤销列表则需要判断输入内容的合法性
    if ($par{'checkcrl'}) {
        `sudo /usr/local/bin/checkCRL $par{'CRL_ADDR'}`;
        my @lines = read_conf_file("/var/efw/openvpn/crl_result");
        `rm /var/efw/openvpn/crl_result`;
        if($lines[0] ne "0"){
            return(0,"无效的撤销证书(CRL)文件地址");
        }
    }
    if (!$par{GLOBAL_DNS}) {        
        $par{GLOBAL_DNS} = "$par{MAIN_DNS}\n$par{SECOND_DNS}";  
    }
    if ( ($conf->{PURPLE_IP_BEGIN} ne $ippool_begin) or
     ($conf->{PURPLE_IP_END} ne $ippool_end) or
     ($conf->{CRL_ADDR} ne $par{CRL_ADDR}) or
     ($conf->{CRL_TYPE} ne $par{CRL_TYPE}) or
     ($conf->{CRL_AUTO_TIME} ne $par{CRL_AUTO_TIME}) or
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
     ($conf->{OUT_IP} ne $par{OUT_IP}) or
     ($conf->{OUT_PORT} ne $par{OUT_PORT}) or
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

    $conf->{CRL_ADDR} = $par{CRL_ADDR};
    $conf->{CRL_TYPE} = $par{CRL_TYPE};
    $conf->{CRL_AUTO_TIME} = $par{CRL_AUTO_TIME};
    
    $conf->{PUSH_DOMAIN} = $par{PUSH_DOMAIN};
    $conf->{DOMAIN} = $par{DOMAIN};
    ##检测数据合法性
    if ($conf->{DOMAIN}) {
        if (!&validdomainname($conf->{DOMAIN})) {
            return(0,"推送域格式不对");
        }
    }
    if ($conf->{GLOBAL_NETWORKS}) {
        my @nets = split(/,/, $conf->{GLOBAL_NETWORKS});
        foreach my $elem (@nets) {
            my @both = split(/\//,$elem);
            if (!&validip($both[0])) {
                return(0,"推送网络格式不对");
            }
            if(!$both[1]){
                return(0,"推送网络需包含子网掩码");
            }
            else{
                if ($both[1]<1 || $both[1]>32) {
                    return(0,"子网掩码必须在1-32之间");
                }
            }
        }
    }
    if ($conf->{GLOBAL_DNS}) {
        my @nets = split(/,/, $conf->{GLOBAL_DNS});
        foreach my $elem (@nets) {
            if (!&validdomainname($elem)) {
                return(0,"推送域名服务器$elem格式不对");
            }
        }
    }
    ###end
    $conf->{OUT_IP} = $par{OUT_IP};
    $conf->{OUT_PORT} = $par{OUT_PORT};
    $conf->{CLIENT_TO_CLIENT} = $par{CLIENT_TO_CLIENT};
    $conf->{OPENVPN_ENABLED} = $par{OPENVPN_ENABLED};
    $config = $conf;

    writehash($conffile, $conf);    
    `sudo fmodify $conffile`;
    &log(_('Written down Openvpn configuration'));
    if ($par{'checkcrl'}) {
        `sudo /usr/local/bin/restartdownloadCRL`;        
    }
    }
    save_client_file($par{'OUT_IP'},$par{'PORT'},$par{'PROTOCOL'},$par{'OUT_PORT'});
    ($errcode, $errstr) = import_p12();
    if ($errcode == 0) {
        return ($errcode, $errstr);
    }
    `touch $dirtyfile`;
    #print STDERR `$restart --force`; 
    #print STDERR "$logid: restarting done\n";
    return 1;
}

sub crlimport() {
    return if (ref ($par{'IMPORT_FILE'}) ne 'Fh');

    my ($fh, $tmpfile) = tempfile("import.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.pem');
    if (!copy ($par{'IMPORT_FILE'}, $fh)) {
    return (0, _('Unable to import certificate revocation list file \'%s\'', $par{'IMPORT_FILE'}, $!));
    }
    close($fh);

    my $input_result_file = '/var/efw/openvpn/input_crl_result';
    `rm $input_result_file`;
    `touch $input_result_file`;
    `$check_input $tmpfile`;
    open(FILE,$input_result_file);
    my @results = <FILE>;
    close(FILE);
    if($results[0]!~/s/)
    {
        return (0, '废弃列表格式错误！');
    }
    
    if (`openssl crl -in $tmpfile -text 2>&1 >/dev/null` !~ /^$/) {
        unlink($tmpfile);
        return (0, _('Invalid certificate revocation list! Import failed!'));
    }

    if (! move($tmpfile, $CRL_FILE)) {
        unlink($tmpfile);
        return (0, _('Could not bring imported certificate revocation list file in place! (%s)', $!));
    }
    `sudo fmodify $CRL_FILE`;
    `sudo /usr/local/bin/unlinkautoCRL`;
    `sudo fcmd /usr/local/bin/unlinkautoCRL`;
    &save();
    $notemessage = _('Certificate revocation list has been imported successfully!');
    return 1;
}

sub import_p12() {
    return 1 if (ref ($par{'IMPORT_FILE'}) ne 'Fh');

    my ($fh, $tmpfile) = tempfile("import.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.p12');
    if (!copy ($par{'IMPORT_FILE'}, $fh)) {
    return (0, _('Unable to import PKCS#12 file \'%s\'', $par{'IMPORT_FILE'}, $!));
    }
    close($fh);

    if ($par{'IMPORT_PASSWORD'} =~ /^$/) {
    if (! move($tmpfile, $PKCS_IMPORT_FILE)) {
            unlink($tmpfile);
            return (0, _('Could not bring imported PKCS#12 file in place! (%s)', $!));
        }
        if (system("openssl pkcs12 -in $PKCS_IMPORT_FILE -password pass: -nodes -noout &>/dev/null") != 0) {
            unlink($PKCS_IMPORT_FILE);
            return (0, _('Invalid PKCS#12 file! Import failed!'));
        }
        return 1;
    }

    my $challenge = $par{'IMPORT_PASSWORD'};
    # decrypt
    my $cmd = "openssl pkcs12 -in $tmpfile -nodes -out ${tmpfile}.decrypted -password stdin &>/dev/null";
    $pid = open3(\*WRITE, \*READ, \*ERROR, $cmd);
    if (! $pid) {
    unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not decrypt PKCS#12 file! Import failed!'));
    }
    print WRITE $challenge;
    close READ;
    close WRITE;
    close ERROR;
    waitpid($pid, 0);
    if ($? != 0) {
    unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not decrypt PKCS#12 file! Import failed!'));
    }
    if (system("openssl pkcs12 -export -in ${tmpfile}.decrypted -out $PKCS_IMPORT_FILE -password pass: &>/dev/null") != 0) {
        unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not store decrypted PKCS#12 file! Import failed!'));
    }
    unlink($tmpfile);
    unlink("${tmpfile}.decrypted");
    `sudo fmodify $PKCS_IMPORT_FILE`;
    return 1;
}

sub import_p12_2(){
    #密码需要修改
    my $challenge = "jcb410";
    `echo >>/tmp/test 0`;
    my $pk12_file = "/etc/openvpn/otherpartca/server.p12";
    if(!-e $pk12_file)
    {
       return (0,'p12文件不存在！');
    }
    
    my ($fh, $tmpfile) = tempfile("import.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.p12');
    if (!copy ($pk12_file, $fh)) {
    return (0, _('Unable to import PKCS#12 file \'%s\'', $pk12_file, $!));
    }
    close($fh);
    
    # decrypt
    my $cmd = "openssl pkcs12 -in $tmpfile -nodes -out ${tmpfile}.decrypted -password stdin &>/dev/null";
    $pid = open3(\*WRITE, \*READ, \*ERROR, $cmd);
    if (! $pid) {
    unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not decrypt PKCS#12 file! Import failed!'));
    }
    print WRITE $challenge;
    close READ;
    close WRITE;
    close ERROR;
    waitpid($pid, 0);
    if ($? != 0) {
    unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not decrypt PKCS#12 file! Import failed!'));
    }
    if (system("openssl pkcs12 -export -in ${tmpfile}.decrypted -out $PKCS_IMPORT_FILE -password pass: &>/dev/null") != 0) {
        unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not store decrypted PKCS#12 file! Import failed!'));
    }
    unlink($tmpfile);
    unlink("${tmpfile}.decrypted");
    `sudo fmodify $PKCS_IMPORT_FILE`;
    return 1;
}

sub read_file($) {
    my $f = shift;
    open (CA, $f) || return _("Could not open file '%s'.", $f);
    my $str = <CA>;
    close CA;
    return $str;
}

##################################################
# 功能：将英文时间转换为中文时间格式
#       英文时间格式："月  日 时:分:秒 年 GMT"
#       中文时间格式: "x年 x月 x日 时:分:秒"
##################################################
my %months = ('Jan'=>'01',
                'Feb'=>'02',
                'Mar'=>'03',
                'Apr'=>'04',
                'May'=>'05',
                'Jun'=>'06',
                'Jul'=>'07',
                'Aug'=>'08',
                'Sep'=>'09',
                'Oct'=>'10',
                'Nov'=>'11',
                'Dec'=>'12' );
sub changeTimeStyleFromEN2CN($){
    my $en_time = shift;
    $en_time =~ s/\s+/ /g;
    my @split_time = split(/ /, $en_time);
    
    my $cn_time = "$split_time[3]年 $months{$split_time[0]}月 $split_time[1]日 $split_time[2]";

    return $cn_time;
}

sub get_crldate() {
    my $output = `/usr/bin/openssl crl -in $CRL_FILE -lastupdate -noout 2>/dev/null`;
    $output =~ s/lastUpdate=//;
    $output =~ s/\s+$//;
    $output = &changeTimeStyleFromEN2CN($output);
    $output = &cleanhtml($output,"y");
    return $output;
}

sub get_crlvaliduntil() {
    my $output = `/usr/bin/openssl crl -in $CRL_FILE -nextupdate -noout 2>/dev/null`;
    $output =~ s/nextUpdate=//;
    $output =~ s/\s+$//;
    $output = &changeTimeStyleFromEN2CN($output);
    $output = &cleanhtml($output,"y");
    return $output;
}
sub display() {
    my $out_port_style = "style='display:none'";
    if($uplink_settings_hash{'RED_TYPE'} eq "NONE"){
        $out_port_style = "style='display:table-row'";
    }
    if ($config->{'AUTH_TYPE'} =~ /^$/) {
        $config->{'AUTH_TYPE'} = 'psk';
    }

    $selected{'PROTOCOL'}{uc($protocol)} = 'selected';

    my %authtype = ();
    $authtype{$config->{'AUTH_TYPE'}} = 'checked="checked"';

    my $last_crl_import = _('No import');
    if (-e $CRL_FILE) {
        $last_crl_import = get_crldate();
    }
    my $next_crl_import = _('No import');
    if (-e $CRL_FILE) {
        $next_crl_import = get_crlvaliduntil();
    }

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

    my $subject = _('No host certificate');
    my $issuer = _('No CA certificate');

    if (-e $SUBJECT_FILE) {
        $subject = read_file($SUBJECT_FILE);
    }
    if (-e $ISSUER_FILE) {
        $issuer = read_file($ISSUER_FILE);
    }

    my $displaypsk = 'display: none';
    if ($config->{'AUTH_TYPE'} eq 'psk') {
        $displaypsk = 'display: table-row';
    }

    my $displaycert = 'display: none';
    if ($config->{'AUTH_TYPE'} =~ /cert/) {
        $displaycert = 'display: block';
    }

    printf <<EOF
<form name="ADVANCED_FORM" method='post' action='$self' enctype='multipart/form-data'>
  <input type='hidden' name='ACTION' value='save' />
  <input type='hidden' name='OPENVPN_ENABLED' value='$config->{'OPENVPN_ENABLED'}' />
  <input type='hidden' name='PURPLE_IP_BEGIN' value='$config->{'PURPLE_IP_BEGIN'}' />
  <input type='hidden' name='PURPLE_IP_END' value='$config->{'PURPLE_IP_END'}' />
  <input type='hidden' name='OPENVPN_PORT' value='$config->{'OPENVPN_PORT'}' />
  <input type='hidden' name='OPENVPN_PROTOCOL' value='$config->{'OPENVPN_PROTOCOL'}' />
  <input type='hidden' name='OUT_PORT' value='$config->{'OUT_PORT'}' />
  <input type='hidden' name='OUT_IP' value='$config->{'OUT_IP'}' />
  <input type='hidden' name='CRL_AUTO_TIME' value='$config->{'CRL_AUTO_TIME'}' />
  <input type='hidden' name='CRL_TYPE' value='$config->{'CRL_TYPE'}' />
  <input type='hidden' name='CRL_ADDR' value='$config->{'CRL_ADDR'}' />
EOF
;
=p
    openbox('100%', 'left', _('Advanced settings'));
    printf <<EOF
<table border=0 cellspacing="0" cellpadding="0" width="100%">
  <tr class="env">
    <td class="add-div-type">%s *</td>
    <td><input type='text' name='PORT' value='$port' SIZE="5" MAXLENGTH="6" /></td>
 </tr>
  <tr class="env">
    <td  class="add-div-type">%s</td>
    <td>
      <select name="PROTOCOL">
        <option value="udp" $selected{'PROTOCOL'}{'UDP'}>UDP</option>
        <option value="tcp" $selected{'PROTOCOL'}{'TCP'}>TCP</option>
      </select>
    </td>
 </tr>
 

<tr class="env">
    <td class="add-div-type">客户端接入IP *</td>
    <td><input type='text' name='OUT_IP' value='$out_ip' /></td>
 </tr>
 <tr class="odd" $out_port_style>
    <td class="add-div-type">客户端接入端口 *</td>
    <td><input type='text' name='OUT_PORT' value='$out_port' /></td>
 </tr>

  <tr class="env">
    <td colspan="2">
      %s
    </td>
  </tr>


  <tr class="table-footer">
    <td colspan="2">
      <input class='submitbutton net_button' type='submit' name='SAVE' value='%s' />
    </td>
  </tr>

</table>
EOF
, _('Port')
, _('Protocol')
, _('Note: You may allow multiple ports by port forwarding them')
, _('Save')
;
    closebox();
=cut    
    globaloptions();

#
# Authentication settings
#



    openbox('100%', 'left', _('Authentication settings'));
    printf <<EOF
<table border=0 cellspacing="0" cellpadding="0" width="100%">
  <tr class="env">
    <td class="add-div-table" rowspan="2" style="width:200px"><b>%s</b></td>
    <td colspan="2">
      <input type="radio" name="AUTH_TYPE" value="psk" $authtype{'psk'}  onclick="switchVisibility('psk', 'on'); switchVisibility('cert', 'off'); switchVisibility('psk_t', 'on'); switchVisibility('cert_t', 'off');">%s</input>
    </td>
  </tr>

  <tr class="env">
    <td colspan="2">
      <input type="radio" name="AUTH_TYPE" value="cert" $authtype{'cert'} onclick="switchVisibility('psk', 'off'); switchVisibility('cert', 'on'); switchVisibility('psk_t', 'off'); switchVisibility('cert_t', 'on');">%s</input>
    </td>
  </tr>
  
  <tr class="env hidden">
    <td colspan="2">
      <input type="radio" name="AUTH_TYPE" value="certpsk" $authtype{'certpsk'} onclick="switchVisibility('psk', 'off'); switchVisibility('cert', 'on'); switchVisibility('psk_t', 'off'); switchVisibility('cert_t', 'on');">%s</input>
    </td>
  </tr>
  
  
  <tr class="odd">
    <td id="rownum" class="add-div-type" rowspan="6"><b>%s</b></td>

EOF
, _('Authentication type')
, 'PSK(用户名/密码) 认证'
, 'X.509 证书认证'
, 'X.509证书和PSK(用户名/密码)双因子认证' 
, _('Certificate management')
;

    

    printf <<EOF
    <td colspan="2" class="add-div-table">
      <div id="cert_t" style="$displaycert">%s</div>
      <div id="psk_t" style="$displaypsk">%s</div>
    </td>
  </tr>

  <tr class="odd">
    <td>%s</td>
    <td><input type="file" name="IMPORT_FILE"></td>
  </tr>
  <tr class="odd">
    <td>%s</td>
    <td><input type="password" name="IMPORT_PASSWORD"></td>
  </tr>

  <tr class="odd">
    <td>%s</td>
    <td>$subject</td>
  </tr>
  <tr class="odd">
    <td>%s</td>
    <td>$issuer</td>
  </tr>
  <tr class="odd" id="psk" style="$displaypsk" >
    <td>
EOF
, '从主SSLVPN 设备导入设备证书或导入第三方认证机构(CA)颁发的设备证书' 
,'从主SSLVPN 设备导入设备证书或导入第三方认证机构(CA)颁发的设备证书' 
, _('PKCS#12 file')
, 'PKCS#12 文件密码'
, '设备证书'
, _('CA certificate')
;
    if ($canreadcacert) {
        printf <<EOF
    <A HREF="showca.cgi?type=pem">%s</A> &nbsp; &nbsp;%s
EOF
, _('Download CA certificate')
, _('Use this file as CA certificate for clients.')
;
    }
print "</td><td>";
    if ($canreadpkcs) {
        printf <<EOF
  
   <A HREF='showca.cgi?type=p12'>%s</A> &nbsp;&nbsp;%s
EOF
, '将设备证书导出为PKCS#12文件'
, '使用此文件作为 SSLVPN 备用服务器的设备证书'
;
    }
    printf <<EOF
</td></tr>
</table>
  
  <table>
  <tr class="table-footer">
    <td colspan="3">
      <input class='submitbutton net_button' type='submit' name='submit' value='%s' />
    </td>
  </tr>
</table>
</form>

EOF
, _('Save')
;
closebox();
#2013-7-14 添加导入公钥及生成证书功能
my $key_file = "/etc/openvpn/otherpartca/server.key";
if(-e $key_file)
{
   &import_key();
}
&make_cert();
#

 printf <<EOF
<div id="cert" style="$displaycert;" >
<form method='post' action='$self' name="CRL_FORM" enctype='multipart/form-data'>
EOF
;
openbox('100%', 'left',_('Certificate revocation'));
my %auto_time = ();
$auto_time{$config->{'CRL_AUTO_TIME'}} = 'checked="checked"';
my %types = ();
$types{$config->{'CRL_TYPE'}} = "checked='checked'";
my $tmp_action = "importcrl";
my $display_auto = "style='display:none'";
my $display_manual = "";
if ($config->{'CRL_TYPE'} eq "auto") {
    $tmp_action = "save";
    $display_auto = "style='display:table-row'";
    $display_manual = "style='display:none'";
}
else{
    $display_manual = "style='display:table-row'";
    $tmp_action = "importcrl";
    $types{'manual'} = "checked='checked'";
}
my $margin = "style='margin-left:8px;'";
foreach my $key(keys %$conf){
    if (($key ne "CRL_TYPE") && ($key ne "CRL_ADDR") && ($key ne "CRL_AUTO_TIME")) {
        print "<input type='hidden' name='$key' value='$config->{$key}' />";
    }  
}
printf <<EOF
<input type='hidden' id="action_type" name='ACTION' value='$tmp_action' />
<input type='hidden' name='checkcrl' value='1' />
<table border=0 cellspacing="0" cellpadding="0" width="100%">
<tr class="odd">
    <td>废弃列表(CRL)导入方式</td>
    <td>
    <input type="radio" $types{'manual'} value="manual" name="CRL_TYPE" onclick="check_time(this)">手动导入废弃列表(CRL)文件
    <input $margin type="radio" $types{'auto'} value="auto" name="CRL_TYPE"  onclick="check_time(this)">自动导入废弃列表(CRL)文件
    </td>
  </tr>
  <tr class="env manual" $display_manual>
    <td>%s:</td>
    <td>
      <input type="file" name="IMPORT_FILE"> &nbsp; <input class='submitbutton net_button' type='submit' name='SAVE' value='%s' />
    </td>
  </tr>
  <tr class="odd manual" $display_manual>
    <td>%s:</td>
    <td>${last_crl_import}&nbsp;</td>
  </tr>
  <tr class="env manual" $display_manual>
    <td>%s:</td>
    <td>${next_crl_import}&nbsp;</td>
  </tr>
  <tr class="env auto" $display_auto>
    <td>撤销证书(CRL)文件地址* </td>
    <td><input type="text" name="CRL_ADDR" size="50" value="$conf->{'CRL_ADDR'}"></td>
  </tr>  
  <tr class="odd auto" $display_auto>
    <td>自动更新撤销证书(CRL)文件的时间间隔:</td>
    <td>
    <input type="radio" value="daily" $auto_time{'daily'} name="CRL_AUTO_TIME">每日
    <input $margin type="radio" value="weekly" $auto_time{'weekly'} name="CRL_AUTO_TIME">每周
    <input $margin type="radio" value="monthly" $auto_time{'monthly'} name="CRL_AUTO_TIME">每月
    </td>
  </tr>
  <tr class="table-footer auto" $display_auto>
    <td colspan="2">
      <input class='submitbutton net_button' type='submit' name='submit' value='保存' />
    </td>
  </tr>
</table>
</div>
</form>
EOF
, _('Import revocation list (CRL) as PEM file')
, _('Import revocation list')
, _('废弃列表更新时间')
, _('废弃列表有效期到')
;
;
closebox();


    closebox();
}

sub globaloptions() {

    my %push_global_networks = ();
    $push_global_networks{$config->{'PUSH_GLOBAL_NETWORKS'}} = 'checked="checked"';
    my %push_global_dns = ();
    $push_global_dns{$config->{'PUSH_GLOBAL_DNS'}} = 'checked="checked"';
    my %push_domain = ();
    $push_domain{$config->{'PUSH_DOMAIN'}} = 'checked="checked"';
    my %push_client = ();
    $push_client{$config->{'CLIENT_TO_CLIENT'}} = 'checked="checked"';
    my ($MAIN_DNS,$SECOND_DNS) = split(/\n/,$globalnameserver);
    my $dis = "style='display:none'";
    if ($config->{'PUSH_GLOBAL_DNS'} eq 'on') {
        $dis = "style='display:block;margin-bottom:1px'";
    }
    ####help_msg
    my $help_hash1 = read_json("/home/httpd/help/openvpn_advanced_help.json","openvpn_advanced.cgi","push_these_net","-10","30","down");
    my $help_hash2 = read_json("/home/httpd/help/openvpn_advanced_help.json","openvpn_advanced.cgi","推送这些域名服务器","-10","30","down");
    my $help_hash3 = read_json("/home/httpd/help/openvpn_advanced_help.json","openvpn_advanced.cgi","推送这些域","-10","30","down");
    openbox('100%', 'left', '用户网络通信设置');
    printf <<EOF
<table border=0 cellspacing="0" cellpadding="0" width="100%">
 <tr class="odd">
    <td  class="add-div-type" style ="width:200px">%s</td>
    <td><input type='checkbox' name='CLIENT_TO_CLIENT' value='on' $push_client{'on'} />拦截通信</td>
  </tr>
  <tr class="env">
    <td class="add-div-type need_help">%s </td>
    <td class="need_help">
      <input type='checkbox' name='PUSH_GLOBAL_NETWORKS' value='on' $push_global_networks{'on'}>%s</input> &nbsp;&nbsp;
      <textarea cols="17" rows="2" name='GLOBAL_NETWORKS' style="width:150px",
>$globalnetworks </textarea>$help_hash1
    </td>
  </tr>
  <tr class="odd">
    <td class="add-div-type need_help">%s </td>
    <td class="need_help">

    <p style="margin-bottom:2px;">
          <input type='checkbox' id='PUSH_GLOBAL_DNS' name='PUSH_GLOBAL_DNS' $push_global_dns{'on'}  onchange="check_enabled()" />%s</input>&nbsp;&nbsp;
          </p>
          <p $dis id="MAIN_DNS" style="margin-bottom:1px">
            首选DNS：*
            <input type="text" name="MAIN_DNS" value="$MAIN_DNS" />
          </p>
          <p $dis id="SECOND_DNS">
            备选DNS：*
            <input type="text" name="SECOND_DNS" value="$SECOND_DNS" />
          </p>$help_hash2
    </td>
  </tr>
  <tr class="env">
    <td class="add-div-type need_help">%s </td>
    <td class="need_help">
      <input type='checkbox' name='PUSH_DOMAIN' value='on' $push_domain{'on'}>%s</input>&nbsp;&nbsp;
      <input type="text" name='DOMAIN' value="$domain" />$help_hash3
    </td>
  </tr>  
 <tr class="odd hidden_class">
    <td  class="add-div-type">%s</td>
    <td><input type='checkbox' name='DROP_DHCP' value='on' $checked{$block_dhcp} /></td>
  </tr>
  <tr class="table-footer">
    <td colspan="2">
      <input class='submitbutton net_button' type='submit' name='submit' value='%s' />
    </td>
  </tr>
</table>
EOF
,'是否拦截用户计算机之间的通信'
, _('本地子网')
, _('Enable')
, _('接入时用户计算机使用此DNS<p>服务器作为首选的DNS服务器</p>')
, _('Enable')
, _('接入时将用户计算机加入此域')
, _('Enable')
,'阻止来自隧道的DHCP应答'
, _('Save')
;
    closebox();


}

sub import_key(){
    openbox('100%', 'left', '导入公钥证书');
    printf <<EOF
    <form name='IMPORT_FORM' method='post' action='$self' enctype='multipart/form-data' >
       <table border='0' cellspacing="0" cellpadding="4">
         <tr  class="odd">
           <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >导入设备公钥证书*</td>
           <td >
             <input type='file' name='device_key' />
           </td>
         </tr>
         <tr  class="env">
           <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >导入CA公钥证书*</td>
           <td>
             <input type='file' name='ca_key' />
           </td>
         </tr>
         <tr  class="table-footer">
           <td colspan="4">
               <input class='submitbutton net_button' type='submit' name='submit' value='上传' />
             <input type="hidden" name="ACTION" value="import_key" />
           </td>
         </tr>
       </table>
    </form>
EOF
;
    closebox();
}

sub make_cert(){
    openeditorbox("生成证书请求文件", "","", "createrule", @errormessages);
    printf <<EOF
    </form>
    <form name='MAKE_FORM' enctype='multipart/form-data' method='post' action='$self'>
      <table border='0' cellspacing="0" cellpadding="4">

         <tr  class="odd">
          <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:120px;font-weight:bold;" >国家*</td>
          <td style="width:500px">
           <input type='text' name='cert_country'  />
           &nbsp;（请填写国家字符缩写标识，如:中国-CN，美国-US）
          </td>
          <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:120px;font-weight:bold;" >部门*</td>
          <td >
           <input type='text' name='cert_department'  />
          </td>
         </tr>
         
         <tr  class="env">
          <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:120px;font-weight:bold;" >省份*</td>
          <td >
           <input type='text' name='cert_province'  />
          </td>
          <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:120px;font-weight:bold;" >颁发给*</td>
          <td >
           <input type='text' name='cert_to'  />
          </td>
         </tr>
         
         <tr  class="odd">
          <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:120px;font-weight:bold;" >城市*</td>
          <td >
           <input type='text' name='cert_city'  />
          </td>
          <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:120px;font-weight:bold;" >E-mail*</td>
          <td >
           <input type='text' name='cert_email'  />
          </td>
         </tr>
         
         <tr  class="env">
          <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:120px;font-weight:bold;" >公司*</td>
          <td >
           <input type='text' name='cert_company'  />
          </td>
          <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:120px;font-weight:bold;" >秘钥长度</td>
          <td >
           <select name='cert_length' style="width:156px;">
              <option value='1024'>1024</option>
              <option value='2048'>2048</option>
           </select>
          </td>
         </tr>
         <input type="hidden" name="ACTION" value="make_cert" />
      </table>
EOF
;
    closeeditorbox("生成并下载", "撤销", "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
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
    $out_ip = $conf->{OUT_IP};
    $out_port = $conf->{OUT_PORT};
    $globalnetworks = $conf->{GLOBAL_NETWORKS};
    $globalnameserver = $conf->{GLOBAL_DNS};
    $domain = $conf->{DOMAIN};
    $client_to_client = $conf->{CLIENT_TO_CLIENT};
    $crl_addr = $conf->{CRL_ADDR};
    $crl_type = $conf->{CRL_TYPE};
    $crl_auto_time = $conf->{CRL_AUTO_TIME};
    $globalnetworks =~ s/,/\n/g;
    $globalnameserver =~ s/,/\n/g;
    #不要默认值 2013.08.15 王琳
    #if ($domain =~ /^$/) {
    #    $domain = "localdomain";
    #}
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
;
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
    if ($action eq 'apply') {
        restart();
        `rm $dirtyfile`;
        return;
    }    
    if ($action eq 'importcrl') {
        ($err,$errormessage) = crlimport();
        $action = '';
        return;
    }   
    if ($action eq 'save_manual') {
        ($err,$errormessage) = save_auto();
        $action = '';
        return;
    }
    if($action eq 'import_key'){
        my $cgi= new CGI;
        #上传设备证书
        my $filehandle = $cgi->param('device_key');
        my $filename = $filehandle;
        my @tmp = split(/\./,$filename);
        my $result_file = '/tmp/modify_cert_result';
        if($filehandle eq '')
        {
           $errormessage = "设备证书不能为空！";
           return;
        }
        
        if($filehandle ne '' && $tmp[1] ne 'crt')
        {
           $errormessage = "请选择crt文件上传！";
           return;
        }
        
        if($filehandle ne '')
        {
          my $tmp_name = "/tmp/server.crt";
          if(-e $tmp_name)
          {
             `rm $tmp_name`;
          }
          `touch $tmp_name`;
          open ( UPLOADFILE, ">$tmp_name" ) or die "$!";
          binmode UPLOADFILE;
          while (<$filehandle>) 
          {
             print UPLOADFILE;
          }
          close UPLOADFILE;
          if(-e $result_file)
          {
             `rm $result_file`;
             `touch $result_file`;
          } else {
             `touch $result_file`;
          }
          `$modify_cert $tmp_name`;
        }
        open(FILE,$result_file);
        my @result = <FILE>;
        close(FILE);
        if($result[0]!~/success/)
        {
           $errormessage = '设备公钥证书格式错误！';
           return;
        }
        `rm $result_file`;
        
        #上传CA证书
        $filehandle = $cgi->param('ca_key');
        $filename = $filehandle;
        @tmp = split(/\./,$filename);
        
        if($filehandle eq '')
        {
           $errormessage = "CA证书不能为空！";
           return;
        }
        
        if($filehandle ne '' && $tmp[1] ne 'crt')
        {
           $errormessage = "请选择crt文件上传！";
           return;
        }
        
        if($filehandle ne '')
        {
          my $tmp_name = "/tmp/ca.crt";
          if(-e $tmp_name)
          {
             `rm $tmp_name`;
          }
          `touch $tmp_name`;
          open ( UPLOADFILE, ">$tmp_name" ) or die "$!";
          binmode UPLOADFILE;
          while (<$filehandle>) 
          {
             print UPLOADFILE;
          }
          close UPLOADFILE;
          if(-e $result_file)
          {
             `rm $result_file`;
             `touch $result_file`;
          } else {
             `touch $result_file`;
          }
          `$modify_cert $tmp_name`;
        }
        
        open(FILE,$result_file);
        my @result = <FILE>;
        close(FILE);
        if($result[0]!~/success/)
        {
           $errormessage = 'CA公钥证书格式错误！';
           return;
        }
        `rm $result_file`;
        
        `openssl pkcs12 -export -clcerts -in /tmp/server.crt  -inkey /etc/openvpn/otherpartca/server.key -passin pass:jcb410  -out /etc/openvpn/otherpartca/server.p12 -passout pass:jcb410 -CAfile /tmp/ca.crt -chain`;
        ($err,$errormessage) = import_p12_2();
        if($err)
        {
           `rm /etc/openvpn/otherpartca/*`;
           $notemessage="公钥证书上传成功！";
           `touch $dirtyfile`;
        }
        return        
    }
    if($action eq 'make_cert')
    {
       my $country = $par{'cert_country'};
       my $province = $par{'cert_province'};
       my $city = $par{'cert_city'};
       my $department = $par{'cert_department'};
       my $company = $par{'cert_company'};
       my $to = $par{'cert_to'};
       my $email = $par{'cert_email'};
       my $length = $par{'cert_length'};
       `sudo $gen_cert $length $country $province $city $company $department $to $email`;
       #`echo >>/tmp/test c=$country,p=$province,c=$city,d=$department,c=$company,t=$to,e=$email,l=$length`;
       my $downfile = "/etc/openvpn/otherpartca/server.csr";
       if(!-e $downfile)
       {
          $errormessage="证书生成失败！";
          return;
       } else {
          open(DLFILE, "<$downfile") || Error('open', "$downfile");  
            @fileholder = <DLFILE>;  
            close (DLFILE) || Error ('close', "$downfile"); 
            print "Content-Type:application/x-download\n";  
            print "Content-Disposition:attachment;filename=server.csr\n\n";
            print @fileholder;
            exit;
       }
       $notemessage = "证书已成功生成！";
       return;
    }
}

getconfig();
getcgihash(\%par, {'wantfile' => 1, 'filevar' => 'IMPORT_FILE'});
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
my $extraheader = '<script language="JavaScript" src="/include/check_explorer.js"></script><script language="JavaScript" src="/include/switchVisibility.js"></script>';
openpage($name, 1, $extraheader);

if (! -e $openvpn_diffie && -e $openvpn_diffie_lock) {
    $notemessage=_('OpenVPN is generating the Diffie Hellman parameters. This will take several minutes. During this time OpenVPN can <b>not</b> be started!');
}

openbigbox($errormessage,"",$notemessage);
if (-e $dirtyfile) {
    $warnmessage = _('Configuration has been changed.You may need to restart openVPN server in order to make the changes active.Clients will reconnect automatically after the restart.');
    applybox($warnmessage);
}


display();
check_form();
check_form_crl();
closebigbox();
closepage();

