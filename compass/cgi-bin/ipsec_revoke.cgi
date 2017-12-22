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
my $dirtyfile  = '/var/efw/openvpn/dirtyuserconfig';
my $conffile = "${swroot}/vpn/settings";
my $conffile_default = "${swroot}/vpn/default/settings";
my $hostconffile = "${swroot}/host/settings";
my $etherconf = "${swroot}/ethernet/settings";
my $restart  = '/usr/local/bin/run-detached /usr/local/bin/restartopenvpn';
my $openvpn_diffie = '/var/efw/openvpn/dh1024.pem';
my $openvpn_diffie_lock = '/var/lock/openvpn_diffie.lock';
my $client_file = '/home/httpd/sslvpn/dingdian_SSL_VPN/config/client.vpn';

my $PKCS_FILE = '/var/efw/openvpn/pkcs12.p12';
my $PKCS_IMPORT_FILE = "${PKCS_FILE}.import";
my $CACERT_FILE = '/var/efw/openvpn/cacert.pem';
my $CRL_FILE = '/var/efw/vpn/ca/crls/cacrl.pem';
my $SUBJECT_FILE = '/var/efw/openvpn/subject.txt';
my $ISSUER_FILE = '/var/efw/openvpn/issuer.txt';

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
                               'check':'url|',
                             },
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
                               'check':'port|',
                             },
                    'OUT_IP':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|domain|',
                             },
                    'MAIN_DNS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'SECOND_DNS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'OUT_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|',
                             },
                    'DOMAIN':{
                               'type':'text',
                               'required':'0',
                               'check':'domain_suffix|',
                             },
                    'GLOBAL_NETWORKS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip_mask|',
                             },
                    'GLOBAL_DNS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|',
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("ADVANCED_FORM");
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
    ####如果自动撤销列表则需要判断输入内容的合法性
    if ($par{'CRL_TYPE'} eq "auto") {
        `sudo /usr/local/bin/checkIpsecCRL $par{'CRL_ADDR'}`;
        my @lines = read_conf_file("/var/efw/vpn/crl_result");
        `rm /var/efw/openvpn/crl_result`;
        if($lines[0] ne "0"){
            return(0,"无效的撤销证书(CRL)文件地址");
        }
    }
    if (-e $conffile_default) {
       readhash($conffile_default, $conf);
    }
    if (-e $conffile) {
        readhash($conffile, $conf);
    }
    $conf->{CRL_ADDR} = $par{CRL_ADDR};
    $conf->{CRL_TYPE} = $par{CRL_TYPE};
    $conf->{CRL_AUTO_TIME} = $par{CRL_AUTO_TIME};
    $config = $conf;
    writehash($conffile, $conf);    
    `sudo fmodify $conffile`;
    if ($par{'CRL_TYPE'} eq "auto") {
        `sudo /usr/local/bin/restartdownloadIpsecCRL`;  
        `sudo fcmd /usr/local/bin/restartdownloadIpsecCRL`;            
    }  
    return 1;
}

sub crlimport() {
    return if (ref ($par{'IMPORT_FILE'}) ne 'Fh');

    my ($fh, $tmpfile) = tempfile("ipseccrl.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.pem');
    if (!copy ($par{'IMPORT_FILE'}, $fh)) {
    return (0, _('Unable to import certificate revocation list file \'%s\'', $par{'IMPORT_FILE'}, $!));
    }
    close($fh);

    if (`openssl crl -in $tmpfile -text 2>&1 >/dev/null` !~ /^$/) {
        unlink($tmpfile);
        return (0, _('Invalid certificate revocation list! Import failed!'));
    }

    if (! move($tmpfile, $CRL_FILE)) {
        unlink($tmpfile);
        return (0, _('Could not bring imported certificate revocation list file in place! (%s)', $!));
    }
    `sudo fmodify $CRL_FILE`;
    `sudo /usr/local/bin/unlinkautoIpsecCRL`;
    `sudo fcmd /usr/local/bin/unlinkautoIpsecCRL`;
    &save();
    $notemessage = _('Certificate revocation list has been imported successfully!');
    return 1;
}



sub read_file($) {
    my $f = shift;
    open (CA, $f) || return _("Could not open file '%s'.", $f);
    my $str = <CA>;
    close CA;
    return $str;
}
=p
sub get_crldate() {
    my $output = `/usr/bin/openssl crl -in $CRL_FILE -lastupdate -noout 2>/dev/null`;
    $output =~ s/lastUpdate=//;
    $output =~ s/\s+$//;
    $output = &cleanhtml($output,"y");
    return $output;
}

sub get_crlvaliduntil() {
    my $output = `/usr/bin/openssl crl -in $CRL_FILE -nextupdate -noout 2>/dev/null`;
    $output =~ s/nextUpdate=//;
    $output =~ s/\s+$//;
    $output = &cleanhtml($output,"y");
    return $output;
}
=cut

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
    }

    $crl_addr = $conf->{CRL_ADDR};
    $crl_type = $conf->{CRL_TYPE};
    $crl_auto_time = $conf->{CRL_AUTO_TIME};
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
sub get_crldate() {
    my $output = `/usr/bin/openssl crl -in $CRL_FILE -lastupdate -noout 2>/dev/null`;
    $output =~ s/lastUpdate=//;
    $output =~ s/\s+$//;
    $output = &cleanhtml($output,"y");
    return $output;
}

sub get_crlvaliduntil() {
    my $output = `/usr/bin/openssl crl -in $CRL_FILE -nextupdate -noout 2>/dev/null`;
    $output =~ s/nextUpdate=//;
    $output =~ s/\s+$//;
    $output = &cleanhtml($output,"y");
    return $output;
}
sub ipsec_revoke(){
    printf <<EOF
    <form method='post' action='$self' name="CRL_FORM" enctype='multipart/form-data'>
EOF
;
openbox('100%', 'left',_('Certificate revocation'));
my $last_crl_import = _('No import');
if (-e $CRL_FILE) {
    $last_crl_import = get_crldate();
}
my $next_crl_import = _('No import');
if (-e $CRL_FILE) {
    $next_crl_import = get_crlvaliduntil();
}
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
  <tr class="odd manual hidden_class" $display_manual>
    <td>%s:</td>
    <td>${last_crl_import}&nbsp;</td>
  </tr>
  <tr class="env manual hidden_class" $display_manual>
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
, _('Last import')
, _('Valid until')
;
;
closebox();
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
    if ($action eq 'importcrl') {
        ($err,$errormessage) = crlimport();
        $action = '';
        return;
    }  
}

getconfig();
getcgihash(\%par, {'wantfile' => 1, 'filevar' => 'IMPORT_FILE'});
$action = $par{'ACTION'};

showhttpheaders();
my $extraheader = '<script language="JavaScript" src="/include/check_explorer.js"></script><script language="JavaScript" src="/include/switchVisibility.js"></script>';
openpage($name, 1, $extraheader);
doaction();
openbigbox($errormessage,"",$notemessage);
ipsec_revoke();
check_form_crl();
closebigbox();
closepage();

