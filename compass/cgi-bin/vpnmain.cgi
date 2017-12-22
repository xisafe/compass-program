#!/usr/bin/perl
#
# This file is part of the IPCop Firewall.
#
# IPCop is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPCop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IPCop; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Copyright (C) 2003-05-25 Mark Wormgoor <mark@wormgoor.com>
#
# $Id: vpnmain.cgi,v 1.10.2.22 2004/10/03 12:11:23 alanh Exp $
#

use Net::DNS;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use Net::IPv4Addr qw (:all);
use Socket;
use CGI::Carp qw (fatalsToBrowser);
use CGI qw(:standard);
require '/var/efw/header.pl';
require '/var/efw/countries.pl';
my $applymessage = "";
my $cgi= new CGI;
###
### Initialize variables
###
my (%netsettings,%hostsettings,%cgiparams,%vpnsettings,%checked,%confighash,%cahash,%hotspotsettings);
my $sleepDelay = 4;    # after a call to ipsecctrl S or R, wait this delay (seconds) before reading status
            # (let the ipsec do its job)
my $restart = '/usr/local/bin/restartipsec --force';
my $greconfig = '/var/efw/vpn/greconfig';
#2013.12.22 check_modify()函数所需的两个配置文件，用于判断该条ipsec连接是否也被使用在以下这两个配置文件中。 by ailei
my $tunnelrouting_config = '/var/efw/tunnelrouting/config';
my $tunnelmulticast_config = '/var/efw/tunnelmulticast/config';

my $warnmessage = '';
my $needreload = "${swroot}/vpn/needreload";
&readhash("${swroot}/ethernet/settings", \%netsettings);
&readhash("${swroot}/host/settings", \%hostsettings);
$cgiparams{'ENABLED'} = 'off';
$cgiparams{'ENABLED_BLUE'} = 'off';
$cgiparams{'ENABLED_ORANGE'} = 'off';
$cgiparams{'EDIT_ADVANCED'} = 'off';
$cgiparams{'NAT'} = 'off';
$cgiparams{'COMPRESSION'} = 'off';
$cgiparams{'ONLY_PROPOSED'} = 'off';
&getcgihash(\%cgiparams, {'wantfile' => 1, 'filevar' => 'FH'});



$commareplacement = "/";

my %strings_auth = (
    'psk' => _('PSK'),
    'cert' => _('Certificate')
);
my %strings_type = (
    'net' => _('Net'),
    'host' => _('Host'),
);

my $localip = '';
if (-e "${swroot}/uplinks/main/data") {
    my %hash = ();
    readhash("${swroot}/uplinks/main/data", \%hash);
    $localip = $hash{'ip_address'};
    chomp ($localip);
}

if (-e "/usr/lib/efw/hotspot/default/settings") {
    &readhash("/usr/lib/efw/hotspot/default/settings", \%hotspotsettings);
}
if (-e "${swroot}/hotspot/settings") {
    &readhash("${swroot}/hotspot/settings", \%hotspotsettings);
}
sub check_form_home(){
    printf <<EOF
    <script>
    var object_glb = {
        'form_name':'GLB_FORM',
        'option':{
            'VPN_OVERRIDE_MTU':{
               'type':'text',
               'required':'0',
               'check':'int|'
            }
        }
    }
    var object_caa = {
        'form_name':'CAA_FORM',
        'option':{
            'CA_NAME':{
                'type':'text',
                'required':'1',
                'check':'name|'
            },
            'FH':{
                'type':'file',
                'required':'1',
                'ass_check':function(){
                                               //此处添加你自己的代码吧
                }
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object_glb);
    check._main(object_caa);
    //check._get_form_obj_table("GLB_FORM");
    //check._get_form_obj_table("CAA_FORM");
    </script>
EOF
;
}
sub check_form_cn(){
    printf <<EOF
    <script>
    var object = {
        'form_name':'CN_FORM',
        'option':{
            'NAME':{
                'type':'text',
                'required':'1',
                'check':'name|'
            },
            'LOCAL_SUBNET':{
                'type':'textarea',
                'required':'1',
                'check':'ip_mask|'
            },
            'LOCAL_ID':{
                'type':'text',
                'required':'0',
                'check':'other',
                'other_reg':'/\.*/',
                'ass_check': function(eve){
                    var msg = "";
                    var LOCAL_ID = eve._getCURElementsByName("LOCAL_ID","input","CN_FORM")[0].value;
                    if(!eve.validip(LOCAL_ID) && !eve.validdomainname(LOCAL_ID)){
                        var pattern = /^[a-zA-Z][a-zA-Z0-9]{3,19}\$/;
                        if(!pattern.test(LOCAL_ID)){
                            msg = "不合法的字串、IP或者域名,字串由4-20位字母开头的字母和数字组成";
                        }
                    }
                    return msg;
                }
            },
            'REMOTE':{
                'type':'text',
                'required':'1',
                'check':'remoteip|domain|'
            },
            'REMOTE_ID':{
                'type':'text',
                'required':'0',
                'check':'other',
                'other_reg':'/\.*/',
                'ass_check': function(eve){
                    var msg = "";
                    var REMOTE_ID = eve._getCURElementsByName("REMOTE_ID","input","CN_FORM")[0].value;
                    if(!eve.validip(REMOTE_ID) && !eve.validdomainname(REMOTE_ID)){
                        var pattern = /^[a-zA-Z][a-zA-Z0-9]{3,19}\$/;
                        if(!pattern.test(REMOTE_ID)){
                            msg = "不合法的字串、IP或者域名,字串由4-20位字母开头的字母和数字组成";
                        }
                    }
                    return msg;
                }
            },
            'REMOTE_SUBNET':{
                'type':'textarea',
                'required':'1',
                'check':'ip_mask|'
            },
            'REMARK':{
                'type':'text',
                'required':'0',
                'check':'note|'
            },
            'PSK':{
                'type':'password',
                'required':'1',
                'ass_check':function(eve){
                    var msg ='';
                    var PSK = eve._getCURElementsByName("PSK","input","CN_FORM")[0].value;
                    var pattern = /[\\s'"`\\\\]+/;
                    if(pattern.test(PSK)){
                        msg = "输入含有非法字符,不能包含空格、单引号、双引号、反斜杠(\\\\)和(`)";
                    }
                    return msg;
                }
            },
            'FH':{
                'type':'file',
                'required':'1'
            },
            'P12_PASS':{
                'type':'password',
                'required':'1'
            },
            'CERT_NAME':{
                'type':'text',
                'required':'1',
                'check':'name|'
            },
            'CERT_EMAIL':{
                'type':'text',
                'required':'1',
                'check':'mail|'
            },
            'CERT_OU':{
                'type':'text',
                'required':'1',
                'check':'name|'
            },
            'CERT_ORGANIZATION':{
                'type':'text',
                'required':'1',
                'check':'name|'
            },
            'CERT_CITY':{
                'type':'text',
                'required':'1',
                'check':'name|'
            },
            'CERT_STATE':{
                'type':'text',
                'required':'1',
                'check':'name|'
            },
            'SUBJECTALTNAME':{
                'type':'text',
                'required':'1',
                'check':'name|',
                'other_reg':'\s'
            },
            'CERT_PASS1':{
                'type':'password',
                'required':'1'
            },
            'CERT_PASS2':{
                'type':'password',
                'required':'1'
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("CN_FORM");
    </script>
EOF
;
}
sub check_form_root(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'ROOT_FORM',
       'option'   :{
            'ROOTCERT_ORGANIZATION':{
                'type':'text',
                'required':'1',
                'check':'name|'
            },
            'ROOTCERT_HOSTNAME':{
                'type':'text',
                'required':'1',
                'check':'ip|domain|'
            },
            'ROOTCERT_EMAIL':{
                'type':'text',
                'required':'0',
                'check':'mail|'
            },
            'ROOTCERT_OU':{
                'type':'text',
                'required':'0',
                'check':'name|'
            },
            'ROOTCERT_CITY':{
                'type':'text',
                'required':'0',
                'check':'name|'
            },
            'ROOTCERT_STATE':{
                'type':'text',
                'required':'0',
                'check':'name|'
            },
            'SUBJECTALTNAME':{
                'type':'text',
                'required':'0',
                'check':'other|',
                'other_reg':'!/^\$/',
                'ass_check':function(eve){
                    var msg;
                    var flag = true;
                    var tmp = new Array();
                    var value = eve._getCURElementsByName("SUBJECTALTNAME","input","ROOT_FORM")[0].value;
                    //判断是否有多个名称,如果有逐个判断
                    var reg1 = /,/;
                    if (reg1.test(value)) {
                        tmp = value.split(",");
                    }
                    else{
                        tmp[0] = value;
                    }
                    //判断每个项目是否正确
                    for(var i = 0;i < tmp.length; i++){                                                            
                        //判断是否以标准格式开始
                        var reg0 = /^(email|IP|DNS|URI|RID):/;
                        if (!reg0.test(tmp[i])){
                            flag = false;
                        }
                        else{
                            flag = true;
                        }
                        //判断mail
                        var reg2 = /email:(.*)/;
                        if(reg2.test(tmp[i])){
                            reg2.exec(tmp[i]);
                            var val = RegExp.\$1;
                            var myReg = /^[-_A-Za-z0-9]+@([_A-Za-z0-9]+\.)+[A-Za-z0-9]{2,3}\$/; 
                            flag = myReg.test(val);
                            if(!flag){
                                break;
                            }
                        }
                        //判断IP
                        var reg3 = /DNS:(.*)/;
                        var reg10 = /IP:(.*)/;
                        if(reg3.test(tmp[i]) || reg10.test(tmp[i])){
                            reg3.exec(tmp[i]);
                            var val = RegExp.\$1;
                            flag = eve.validip(val);
                            if(!flag){
                                break;
                            }
                        }
                        //判断URI
                        var reg4 = /URI:(.*)/;
                        if(reg4.test(tmp[i])){
                            reg4.exec(tmp[i]);
                            var val = RegExp.\$1;
                            flag = eve.validurl(val);
                            if(!flag){
                                break;
                            }
                        }
                        //判断RIP
                        var reg5 = /URI:(.*)/;
                        if(reg5.test(tmp[i])){
                            reg5.exec(tmp[i]);
                            var val = RegExp.\$1;
                            if(!val){
                                flag = false;
                                break;
                            }
                        }
                    }
                    if(!flag){
                        msg = "旧项目名称不正确，请参考帮助信息";
                    }
                    return msg;
                }
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("ROOT_FORM");
    </script>
EOF
;
}
sub readvpnsettings($) {
    my $hash = shift;
    if (-f "${swroot}/vpn/default/settings") {
    &readhash("${swroot}/vpn/default/settings", $hash);
    }
    if (-f "${swroot}/vpn/settings") {
    &readhash("${swroot}/vpn/settings", $hash);
    }
}

sub readhasharrayOrEmpty($$) {
    my $filename = shift;
    my $hash = shift;
    if (-f "$filename") {
    &readhasharray("$filename", $hash);
    }
}
#2013.12.22 判断该条连接是否可以被修改，即是否可以被删除或编辑。 by ailei
sub check_modify($){
    my $linkname = shift;

    my @tunnelrouting_lines = read_conf_file($tunnelrouting_config);
    my @tunnelmulticast__lines = read_conf_file($tunnelmulticast_config);

    if(@tunnelrouting_lines>0)
    {
        foreach my $thisline (@tunnelrouting_lines) {
            chomp($thisline);
        
            my @line=split(/,/,$thisline);
            my $tunnelroutingname = $line[3];

            if ($tunnelroutingname eq $linkname) {
                $errormessage = "隧道路由中存在对该连接的依赖，在解决该依赖前不能对连接配置执行启禁用、修改、删除操作。";
                return 1;
            }
        }
    }
    if(@tunnelmulticast__lines>0)
    {
        foreach my $thisline (@tunnelmulticast__lines) {
            chomp($thisline);
        
            my @line=split(/,/,$thisline);
            my $tunnelmulticastname = $line[1];

            if ($tunnelmulticastname eq $linkname) {
                $errormessage = "隧道组播中存在对该连接的依赖，在解决该依赖前不能对连接配置执行启用/禁用、修改、删除操作。";
                return 1;
            }
        }
    }
    return 0;
}

###
### Useful functions
###
sub valid_dns_host {
    my $hostname = $_[0];
    unless ($hostname) { return "No hostname"};
    my $res = new Net::DNS::Resolver;
    my $query = $res->search("$hostname");
    if ($query) {
        foreach my $rr ($query->answer) {
            ## Potential bug - we are only looking at A records:
            return 0 if $rr->type eq "A";
        }
    } else {
        return $res->errorstring;
    }
}

###
### Just return true is one interface is vpn enabled
###
sub vpnenabled {
    return ($vpnsettings{'ENABLED'} eq 'on' || 
        $vpnsettings{'ENABLED_ORANGE'} eq 'on' ||
        $vpnsettings{'ENABLED_BLUE'} eq 'on');
}

####help_msg
    my $help_hash1 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","覆盖默认MTU","-10","30","down");
    my $help_hash2 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","连接配置-本地子网","-10","30","down");
    my $help_hash3 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","本地ID","-10","30","down");
    my $help_hash4 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","远程","-10","30","down");
    my $help_hash5 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","修改高级设置","-10","30","down");
    my $help_hash6 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","使用预共享密钥","-10","30","down");
    my $help_hash7 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","Upload a certificate request","-10","30","down");
    my $help_hash8 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","上传证书","-10","30","down");
    my $help_hash9 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","上传pkcs12文件","-10","30","down");
    my $help_hash10 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","产生一个证书","-10","30","down");
    my $help_hash11 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","高级连接参数-完美的前向安全性","-10","30","down");
    my $help_hash12 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","协商载荷压缩","-10","30","down");
    my $help_hash13 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","组织和机构名称","-10","30","down");
    my $help_hash14 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","主机名","-10","30","down");
    my $help_hash15 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","邮件地址","-10","30","down");
    my $help_hash16 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","部门名称","-10","30","down");
    my $help_hash17 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","省份和州","-10","30","down");
    my $help_hash18 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","项目名称","-10","30","down");
    my $help_hash19 = read_json("/home/httpd/help/vpnmain_help.json","vpnmain.cgi","文件名","-10","30","down");
    ###
    ###

###
### old version: maintain serial number to one, without explication. 
### this         : let the counter go, so that each cert is numbered.
###
sub cleanssldatabase
{
    if (open(FILE, ">${swroot}/vpn/ca/certs/serial")) {
    print FILE "01";
    close FILE;
    `sudo fmodify "${swroot}/vpn/ca/certs/serial"`;
    }
    if (open(FILE, ">${swroot}/vpn/ca/certs/index.txt")) {
    print FILE "";
    close FILE;
    `sudo fmodify "${swroot}/vpn/ca/certs/index.txt"`;
    }
    unlink ("${swroot}/vpn/ca/certs/index.txt.old");
    unlink ("${swroot}/vpn/ca/certs/serial.old");
    unlink ("${swroot}/vpn/ca/certs/01.pem");
    `sudo fmodify "${swroot}/vpn/ca/certs/01.pem"`;
}
sub newcleanssldatabase
{
    if (! -s "${swroot}/vpn/ca/certs/serial" )  {
        open(FILE, ">${swroot}/vpn/ca/certs/serial");
        print FILE "01";
        close FILE;
        `sudo fmodify "${swroot}/vpn/ca/certs/serial"`;
    }
    if (! -s ">${swroot}/vpn/ca/certs/index.txt") {
    system ("touch ${swroot}/vpn/ca/certs/index.txt");
    `sudo fmodify "${swroot}/vpn/ca/certs/index.txt"`;
    }
    unlink ("${swroot}/vpn/ca/certs/index.txt.old");
    unlink ("${swroot}/vpn/ca/certs/serial.old");
#   unlink ("${swroot}/vpn/ca/certs/01.pem");        numbering evolves. Wrong place to delete
}


sub debug($){
    return;
	my $log = shift;
	if (open(FILE, ">>/var/efw/pt.log")) {
		print FILE $log."\n";
		close FILE;
    }
}
###
### Call openssl and return errormessage if any
###
sub callssl ($) {
    my $opt = shift;
	debug("/usr/bin/openssl $opt 2>&1");
    my $retssl =  `/usr/bin/openssl $opt 2>&1`;    #redirect stderr
    my $ret = '';
    foreach my $line (split (/\n/, $retssl)) {
    &log("ipsec", "$line") if (0);        # 1 for verbose logging
    $ret .= '<br>'.$line if ( $line =~ /error|unknown/ );
    }
    if ($ret) {
        $ret= &cleanhtml($ret);
    }
    return $ret ? _('OpenSSL produced an error').": $ret" : '' ;
}
###
### Obtain a CN from given cert
###
sub getCNfromcert ($) {
    #&log("ipsec", "Extracting name from $_[0]...");
    my $temp = `/usr/bin/openssl x509 -text -in $_[0]`;
    $temp =~ /Subject:.*CN=(.*)[\n]/;
    $temp = $1;
    $temp =~ s+/Email+, E+;
    $temp =~ s/ ST=/ S=/;
    $temp =~ s/,//g;
    $temp =~ s/\'//g;
    return $temp;
}
###
### Obtain Subject from given cert
###
sub getsubjectfromcert ($) {
    #&log("ipsec", "Extracting subject from $_[0]...");
    my $temp = `/usr/bin/openssl x509 -text -in $_[0]`;
    $temp =~ /Subject: (.*)[\n]/;
    $temp = $1;
    $temp =~ s+/Email+, E+;
    $temp =~ s/ ST=/ S=/;
    return $temp;
}
sub delete_greconfig($){
    my $name = shift;
    my @exists = read_conf_file($greconfig);
    for (my $i = 0; $i < @exists; $i++) {
        if ($exists[$i] =~ /,$name,/) {
            delete $exists[$i];
        }
    }
    save_config_file(\@exists,$greconfig);
}
sub switch_greconfig($$){
    my $name = shift;
    my $enable = shift;
    my @exists = read_conf_file($greconfig);
    for (my $i = 0; $i < @exists; $i++) {
        if ($exists[$i] =~ /,$name,/) {
            #进行字段替换
            my @temp = split(/,/, $exists[$i]);
            my $line_content = "$enable,$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6]";
            $exists[$i] = $line_content; 
        }
    }
    &save_conf_file(\@exists,$greconfig);
}
sub save_greconfig($$$$$$$){
    my $enable = shift;
    my $gre = shift;
    my $name = shift;
    my $uplink = shift;
    my $local_net = shift;
    my $remote_ip = shift;
    my $remote_net = shift;
    my $flag = 0;
    my $save_line = "$enable,$gre,$name,$uplink,$local_net,$remote_ip,$remote_net";
    my @exists = read_conf_file($greconfig);
    my $exist_total = @exists;
    for(my $i = 0; $i < $exist_total; $i++){
        my @tmp = split(/,/,$exists[$i]);
        if ($tmp[2] eq "$name") {
            $flag = 1;
            $exists[$i] = $save_line;
        }
    }
    if(!$flag){
        push(@exists, $save_line);
    }
    &save_conf_file(\@exists,$greconfig);
}

sub save_conf_file($$) {
    my $ref = shift;
    my $filename= shift;
    my @lines = @$ref;
    open (FILE, ">$filename");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
}



###
### Combine local subnet and connection name to make a unique name for each connection section 
### (this sub is not used now)
###
sub makeconnname ($) {
    my $conn = shift;
    my $subnet = shift;

    $subnet =~ /^(.*?)\/(.*?)$/;    # $1=IP $2=mask
    my $ip = unpack('N', &Socket::inet_aton($1));
    if (length ($2) > 2) {
    my $mm =  unpack('N', &Socket::inet_aton($2));
    while ( ($mm & 1)==0 ) {
        $ip >>= 1; 
        $mm >>= 1;
    };
    } else {
    $ip >>=  (32 - $2);
    }
    return sprintf ("%s-%X", $conn, $ip);
}

###
### Save main settings
###
if ($cgiparams{'ACTION'} eq 'apply') {
    `$restart`;    
        `sudo fcmd $restart`;
        system("rm $needreload");
        sleep $sleepDelay;
        $notemessage = _("IPsec vpn rules applied successfully !");
}

if ($cgiparams{'ACTION'} eq _('Save') && $cgiparams{'TYPE'} eq '' && $cgiparams{'KEY'} eq '') {
    &readvpnsettings(\%vpnsettings);

    unless ($cgiparams{'VPN_OVERRIDE_MTU'} =~ /^(|[0-9]{1,5})$/ ) { #allow 0-99999
        $errormessage = _('VPN MTU is invalid');
        goto SAVE_ERROR;
    }

    unless ($cgiparams{'VPN_WATCH'} =~ /^(|off|on)$/ ) {
        $errormessage = _('Invalid input');
        goto SAVE_ERROR;
    }    
    map ($vpnsettings{$_} = $cgiparams{$_},
      ('ENABLED','ENABLED_ORANGE','ENABLED_BLUE','DBG_CRYPT','DBG_PARSING','DBG_EMITTING','DBG_CONTROL',
      'DBG_KLIPS','DBG_DNS'));

    $vpnsettings{'VPN_OVERRIDE_MTU'} = $cgiparams{'VPN_OVERRIDE_MTU'};
    $vpnsettings{'VPN_WATCH'} = $cgiparams{'VPN_WATCH'};
    &writehash("${swroot}/vpn/settings", \%vpnsettings);
      `sudo fmodify "${swroot}/vpn/settings"`;
      system("touch $needreload");
    SAVE_ERROR:
###
### Reset all 
###
} 
elsif ($cgiparams{'ACTION'} eq 'reset') {
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);

    foreach my $key (keys %confighash) {
        if ($confighash{$key}[4] eq 'cert') {
            #同时要是关联了gre,要删除相应的配置 by wl 2013.12.17
            &delete_greconfig($confighash{$key}[1]);
            `sudo fmodify "${swroot}/vpn/greconfig"`;
            #end 2013.12.17
            delete $confighash{$key};
        }
    }
    while (my $file = glob("${swroot}/vpn/ca/{cacerts,certs,crls,private}/*")) {
          unlink $file;
		  debug("sudo fdelete $file");
          `sudo fdelete $file`;
    }
    &cleanssldatabase();
    if (open(FILE, ">${swroot}/vpn/caconfig")) {
        print FILE "";
        close FILE;
            `sudo fmodify "${swroot}/vpn/caconfig"`
    }
    
    &writehasharray("${swroot}/vpn/config", \%confighash);
      `sudo fmodify "${swroot}/vpn/config"`;
    system("touch $needreload");

###
### Upload CA Certificate
###
} 
elsif ($cgiparams{'ACTION'} eq _('Upload CA certificate')) {
    &readhasharrayOrEmpty("${swroot}/vpn/caconfig", \%cahash);
    if (length($cgiparams{'CA_NAME'}) >60) {
          $errormessage = _('User\'s full name or system hostname is too long');
          goto VPNCONF_ERROR;
    }

    if ($cgiparams{'CA_NAME'} eq 'ca') {
          $errormessage = _('CA名称不能为"ca"');
          goto UPLOADCA_ERROR;
    }

    # Check if there is no other entry with this name
    foreach my $key (keys %cahash) {
          if ($cahash{$key}[0] eq $cgiparams{'CA_NAME'}) {
              $errormessage = _('A CA certificate with this name already exists.');
              goto UPLOADCA_ERROR;
          }
    }

    if (ref ($cgiparams{'FH'}) ne 'Fh') {
          $errormessage = _('There was no file upload.');
          goto UPLOADCA_ERROR;
    }
    # Move uploaded ca to a temporary file
    (my $fh, my $filename) = tempfile( );
    if (copy ($cgiparams{'FH'}, $fh) != 1) {
          $errormessage = $!;
          goto UPLOADCA_ERROR;
    }
    my $temp = `/usr/bin/openssl x509 -text -in $filename`;
    if ($temp !~ /CA:TRUE/i) {
          $errormessage = _('Not a valid CA certificate.');
          unlink ($filename);
          goto UPLOADCA_ERROR;
    } 
      else {
          move($filename, "${swroot}/vpn/ca/cacerts/$cgiparams{'CA_NAME'}cert.pem");
          if ($? ne 0) {
              $errormessage = _('Certificate file move failed').": $!";
              unlink ($filename);
              goto UPLOADCA_ERROR;
          }
          `sudo fmodify "${swroot}/vpn/ca/cacerts/$cgiparams{'CA_NAME'}cert.pem"`;
    }

    my $key = &findhasharraykey (\%cahash);
    $cahash{$key}[0] = $cgiparams{'CA_NAME'};
    $cahash{$key}[1] = &cleanhtml(getsubjectfromcert ("${swroot}/vpn/ca/cacerts/$cgiparams{'CA_NAME'}cert.pem"));
    &writehasharray("${swroot}/vpn/caconfig", \%cahash);
    `sudo fmodify "${swroot}/vpn/caconfig"`;
    system("touch $needreload");

    UPLOADCA_ERROR:

###
### Display ca certificate
###
}
######5月28号临时修改代码
elsif ($cgiparams{'ACTION'} eq "upload_pkcs12") {
    my $upload_filehandle = $cgi->upload('FH_pkcs12');
    if ($upload_filehandle !~/\.p12$/) {
        $errormessage = "上传的PKCS12证书格式不对";
    }
    else{
        my $filename = "/tmp/".$upload_filehandle;
        open ( UPLOADFILE, ">$filename" ) or die "$!";
        binmode UPLOADFILE;
        while ( <$upload_filehandle> ){
            print UPLOADFILE;
        }
        close UPLOADFILE;  
        system("sudo /usr/local/bin/import_cert.py $upload_filehandle $cgiparams{'pkcs12_passwd'}"); 
        my $val;
        if (-e "/tmp/zz") {
           open(FILE,"/tmp/zz");
           $val = <FILE>;
           close(FILE);
        }        
        $val =~ /(^\d)/;
        $val = $1;
        if ($val ne "0") {
            $errormessage = "上传PKCS12证书失败，请确保证书与密码匹配!";
        }
        else{
            $notemessage = "PKCS12证书上传成功!";  
        }           
    }
}
elsif ($cgiparams{'ACTION'} eq "upload_crl") {
    my $upload_filehandle = $cgi->upload('FH_crl');
    if ($upload_filehandle !~/\.pem$/) {
        $errormessage = "撤销证书格式不对";
    }
    else{
        my $filename = "/tmp/".$upload_filehandle;
        open ( UPLOADFILE, ">$filename" ) or die "$!";
        binmode UPLOADFILE;
        while ( <$upload_filehandle> ){
            print UPLOADFILE;
        }
        close UPLOADFILE;   
        $notemessage = "成功撤销证书"; 
        system("sudo /usr/local/bin/revoke_cert.py $upload_filehandle");     
    }
}
####结束
elsif ($cgiparams{'ACTION'} eq _('Show CA certificate')) {
    &readhasharrayOrEmpty("${swroot}/vpn/caconfig", \%cahash);

    if ( -f "${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem") {
          &showhttpheaders();
          &openpage(_('VPN configuration - main'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
        &openbigbox($errormessage, $warnmessage, $notemessage);
          &openbox('100%', 'LEFT', _('CA certificate'));
          $output = `/usr/bin/openssl x509 -text -in ${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem`;
          $output = &cleanhtml($output,"y");
          print "<pre>$output</pre>\n";
          &closebox();
          print "<DIV ALIGN='CENTER'><A HREF='/cgi-bin/vpnmain.cgi'>"._('Back')."</A></DIV>";
          &closebigbox();
          
          &closepage();
          exit(0);
    } 
    else {
         $errormessage = _('Invalid key.');
    }
###
### Download ca certificate
###
} 
elsif ($cgiparams{'ACTION'} eq _('Download CA certificate')) {
    &readhasharrayOrEmpty("${swroot}/vpn/caconfig", \%cahash);
    if ( -f "${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
          print "Content-Type: application/force-download\n";
          print "Content-Type: application/octet-stream\r\n";
          print "Content-Disposition: attachment; filename=$cahash{$cgiparams{'KEY'}}[0]cert.pem\r\n\r\n";
          print `/usr/bin/openssl x509 -in ${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem`;
          exit(0);
    } 
    else {
           $errormessage = _('Invalid key.');
    }

###
### Remove ca certificate (step 2)
###
} 
elsif ($cgiparams{'ACTION'} eq _('Remove CA certificate') && $cgiparams{'AREUSURE'} eq 'yes') {
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);
    &readhasharrayOrEmpty("${swroot}/vpn/caconfig", \%cahash);

    if ( -f "${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
        foreach my $key (keys %confighash) {
            my $test = `/usr/bin/openssl verify -CAfile ${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem ${swroot}/vpn/ca/certs/$confighash{$key}[1]cert.pem`;
            if ($test =~ /: OK/) {
                  # Delete connection
                  unlink ("${swroot}/vpn/ca/certs/$confighash{$key}[1]cert.pem");
                  `sudo fdelete "${swroot}/vpn/ca/certs/$confighash{$key}[1]cert.pem"`;
                  unlink ("${swroot}/vpn/ca/certs/$confighash{$key}[1].p12");
                  `sudo fdelete "${swroot}/vpn/ca/certs/$confighash{$key}[1].p12"`;
                  delete $confighash{$key};
                  &writehasharray("${swroot}/vpn/config", \%confighash);
                  `sudo fmodify "${swroot}/vpn/config"`;
                  system("touch $needreload");
                  # `$restart`;
            }
        }
        unlink ("${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
        `sudo fdelete "${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem"`;
        delete $cahash{$cgiparams{'KEY'}};
        &writehasharray("${swroot}/vpn/caconfig", \%cahash);
        `sudo fmodify "${swroot}/vpn/config"`;
        system("touch $needreload");
    } 
    else {
           $errormessage = _('Invalid key.');
    }
###
### Remove ca certificate (step 1)
###
} 
elsif ($cgiparams{'ACTION'} eq _('Remove CA certificate')) {
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);
    &readhasharrayOrEmpty("${swroot}/vpn/caconfig", \%cahash);

    my $assignedcerts = 0;
    if ( -f "${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem" ) {
          foreach $key (keys %confighash) {
              $test = `/usr/bin/openssl verify -CAfile ${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem ${swroot}/vpn/ca/certs/$confighash{$key}[1]cert.pem`;
              if ($test =~ /: OK/) {
              $assignedcerts += 1;
              }
          }
          if ($assignedcerts) {
              &showhttpheaders();
              &openpage(_('VPN configuration - main'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
              
              &openbigbox($errormessage, $warnmessage, $notemessage);
              &openbox('100%', 'LEFT', _('Are you sure?'));
              printf <<END
              <TABLE><FORM enctype='multipart/form-data'  METHOD='POST'><INPUT TYPE='HIDDEN' NAME='AREUSURE' VALUE='yes'>
                     <INPUT TYPE='HIDDEN' NAME='KEY' VALUE='$cgiparams{'KEY'}'>
                  <TR><TD ALIGN='CENTER'>
                  <B><FONT COLOR='$colourred'>%s</FONT></B>:
                  %s
                  <TR><TD ALIGN='CENTER'><INPUT class='submitbutton' TYPE='SUBMIT' NAME='ACTION' VALUE='%s'>
                  <INPUT class='submitbutton' TYPE='SUBMIT' NAME='ACTION' VALUE='%s'></TD></TR>
              </FORM></TABLE>
END
,
_('WARNING'),
_('%s connections are associated with this CA. Deleting the CA will delete these connections as well.', $assignedcerts),
_('Remove CA certificate'),
_('Cancel')
;

              &closebox();
              closebigbox();
              
              closepage();
              exit (0);
          } else {
              unlink ("${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem");
              `sudo fdelete "${swroot}/vpn/ca/cacerts/$cahash{$cgiparams{'KEY'}}[0]cert.pem"`;
              delete $cahash{$cgiparams{'KEY'}};
              &writehasharray("${swroot}/vpn/caconfig", \%cahash);
              `sudo fmodify "${swroot}/vpn/caconfig"`;
              system("touch $needreload");
         # `$restart`;
         # sleep $sleepDelay;
          }
    } 
    else {
           $errormessage = _('Invalid key.');
    }

###
### Display root certificate
###
} 
elsif ($cgiparams{'ACTION'} eq _('Show root certificate') || $cgiparams{'ACTION'} eq _('Show host certificate')) {
    my $output;
    &showhttpheaders();
    &openpage(_('VPN configuration - main'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
    &openbigbox($errormessage, $warnmessage, $notemessage);
    if ($cgiparams{'ACTION'} eq _('Show root certificate')) {
          &openbox('100%', 'LEFT', _('Root certificate'));
          $output = `/usr/bin/openssl x509 -text -in ${swroot}/vpn/ca/cacerts/cacert.pem`;
    } 
      else {
          &openbox('100%', 'LEFT', _('Host certificate'));
          $output = `/usr/bin/openssl x509 -text -in ${swroot}/vpn/ca/certs/hostcert.pem`;
    }
    $output = &cleanhtml($output,"y");
    print "<pre>$output</pre>\n";
    &closebox();
    print "<div align='center'><a href='/cgi-bin/vpnmain.cgi'>". _('Back') ."</a></div>";
    &closebigbox();    
    &closepage();
    exit(0);

###
### Download root certificate
###
}
 elsif ($cgiparams{'ACTION'} eq _('Download root certificate')) {
    if ( -f "${swroot}/vpn/ca/cacerts/cacert.pem" ) {
            print "Content-Type: application/force-download\n";
            print "Content-Disposition: attachment; filename=$hostsettings{'HOSTNAME'}-cacert.pem\r\n\r\n";
            print `/usr/bin/openssl x509 -in ${swroot}/vpn/ca/cacerts/cacert.pem`;
            exit(0);
    }
###
### Download host certificate
###
} 
elsif ($cgiparams{'ACTION'} eq _('Download host certificate')) {
    if ( -f "${swroot}/vpn/ca/certs/hostcert.pem" ) {
          print "Content-Type: application/force-download\n";
          print "Content-Disposition: attachment; filename=$hostsettings{'HOSTNAME'}-hostcert.pem\r\n\r\n";
          print `/usr/bin/openssl x509 -in ${swroot}/vpn/ca/certs/hostcert.pem`;
          exit(0);
    }
###
### Form for generating a root certificate
###
} 
elsif ($cgiparams{'ACTION'} eq _('Generate root/host certificates') || $cgiparams{'ACTION'} eq _('Upload PKCS12 file')) {

    if (-f "${swroot}/vpn/ca/cacerts/cacert.pem") {
          $errormessage = _('A valid root certificate already exists.');
          goto ROOTCERT_ERROR;
    }
    &readvpnsettings(\%vpnsettings);
    if ($cgiparams{'ROOTCERT_HOSTNAME'} eq '') {
        if (-e "${swroot}/uplinks/main/active") {
                if ($localip !~ /^$/) {
                      $cgiparams{'ROOTCERT_HOSTNAME'} = (gethostbyaddr(pack("C4", split(/\./, $localip)), 2))[0];
                      if ($cgiparams{'ROOTCERT_HOSTNAME'} eq '') {
                          $cgiparams{'ROOTCERT_HOSTNAME'} = $localip;
                      }
                }
      }
        $cgiparams{'ROOTCERT_COUNTRY'} = $vpnsettings{'ROOTCERT_COUNTRY'} if (!$cgiparams{'ROOTCERT_COUNTRY'});
    } 
    elsif ($cgiparams{'ROOTCERT_COUNTRY'} ne '') {

          # Validate input since the form was submitted
          if ($cgiparams{'ROOTCERT_ORGANIZATION'} eq ''){
              $errormessage = _('Organization can\'t be empty.');
              goto ROOTCERT_ERROR;
          }
          if (length($cgiparams{'ROOTCERT_ORGANIZATION'}) >64) {
              $errormessage = _('Organization is too long; it should not be longer than 64 characters.');
              goto ROOTCERT_ERROR;
          }
          if ($cgiparams{'ROOTCERT_ORGANIZATION'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
              $errormessage = _('Invalid input for organization');
              goto ROOTCERT_ERROR;
          }
          if ($cgiparams{'ROOTCERT_HOSTNAME'} eq ''){
              $errormessage = _('Hostname can\'t be empty.');
              goto ROOTCERT_ERROR;
          }
          unless (validfqdn($cgiparams{'ROOTCERT_HOSTNAME'}) || validip($cgiparams{'ROOTCERT_HOSTNAME'})) {
              $errormessage = _('Invalid input for hostname.');
              goto ROOTCERT_ERROR;
          }
          if ($cgiparams{'ROOTCERT_EMAIL'} ne '' && (! validemail($cgiparams{'ROOTCERT_EMAIL'}))) {
              $errormessage = _('Invalid input for email address.');
              goto ROOTCERT_ERROR;
          }
          if (length($cgiparams{'ROOTCERT_EMAIL'}) > 40) {
              $errormessage = _('Email address is too long; it should not be longer than 40 characters.');
              goto ROOTCERT_ERROR;
          }
          if ($cgiparams{'ROOTCERT_OU'} ne '' && $cgiparams{'ROOTCERT_OU'} !~ /^[a-zA-Z0-9\x80-\xff_]*$/) {
              $errormessage = _('Invalid input for department.');
              goto ROOTCERT_ERROR;
          }
          if (length($cgiparams{'ROOTCERT_OU'}) > 64) {
              $errormessage = _('部门名称长度太长,不能超过64个字符.');
              goto ROOTCERT_ERROR;
          }
          if ($cgiparams{'ROOTCERT_CITY'} ne '' && $cgiparams{'ROOTCERT_CITY'} !~ /^[a-zA-Z0-9\x80-\xff_]*$/) {
              $errormessage = _('Invalid input for city.');
              goto ROOTCERT_ERROR;
          }
          if (length($cgiparams{'ROOTCERT_CITY'}) > 128) {
              $errormessage = _('城市名称长度太长,不能超过128个字符.');
              goto ROOTCERT_ERROR;
          }
          if ($cgiparams{'ROOTCERT_STATE'} ne '' && $cgiparams{'ROOTCERT_STATE'} !~ /^[a-zA-Z0-9\x80-\xff_]*$/) {
              $errormessage = _('Invalid input for state or province.');
              goto ROOTCERT_ERROR;
          }
          if (length($cgiparams{'ROOTCERT_STATE'}) > 128) {
              $errormessage = _('省分/州长度太长,不能超过128个字符.');
              goto ROOTCERT_ERROR;
          }
          if ($cgiparams{'ROOTCERT_COUNTRY'} !~ /^[A-Z]*$/) {
              $errormessage = _('Invalid input for country.');
              goto ROOTCERT_ERROR;
          }

    #the exact syntax is a list comma separated of 
    #  email:any-validemail
    #    URI: a uniform resource indicator
    #   DNS: a DNS domain name
    #   RID: a registered OBJECT IDENTIFIER
    #   IP: an IP address
    # example: email:franck@foo.com,IP:10.0.0.10,DNS:franck.foo.com

        if ($cgiparams{'SUBJECTALTNAME'} ne '' && $cgiparams{'SUBJECTALTNAME'} !~ /^(email|URI|DNS|RID|IP):[a-zA-Z0-9 :\/,\.\-_@]*$/) {
            $errormessage = _('旧项目名称格式错误!');
            #goto VPNCONF_ERROR;   原来版本跳转到一开始的页面
              goto ROOTCERT_ERROR;# 现在改为跳到自己出错的页面
        }
        else{
              $flag = 0;
              if ($cgiparams{'SUBJECTALTNAME'} =~/^email:(.*)/) {
                  if (!&validemail($1)) {
                      $flag = 1;
                  }
              }
              if ($cgiparams{'SUBJECTALTNAME'} =~/^DNS|IP:(.*)/) {
                  if (!&validdomainname($1) && !&validip($1) ) {
                      $flag = 1;
                  }
              }
              if ($cgiparams{'SUBJECTALTNAME'} =~/^URI:(.*)/) {
                  my $uri = $1;
                  my $last;
                  if ($uri !~/^(http|file|ftp|telne|gopher|https|news|Idap):\/\/(.*)/) {
                      $flag = 1;
              }
              else{
                      $uri =~/^(http|file|ftp|telne|gopher|https|news|Idap):\/\/(.*)/;
                      $last = $1;
                      if (!&validdomainname($last)) {
                          $flag = 1;
                      }
                  }
              }
              if ($flag) {
                  $errormessage = _('旧项目名称格式错误!');
                  #goto VPNCONF_ERROR;   原来版本跳转到一开始的页面
                  goto ROOTCERT_ERROR;# 现在改为跳到自己出错的页面
            }
        }
    # Copy the cgisettings to vpnsettings and save the configfile
        $vpnsettings{'ROOTCERT_ORGANIZATION'}    = $cgiparams{'ROOTCERT_ORGANIZATION'};
        $vpnsettings{'ROOTCERT_HOSTNAME'}    = $cgiparams{'ROOTCERT_HOSTNAME'};
        $vpnsettings{'ROOTCERT_EMAIL'}         = $cgiparams{'ROOTCERT_EMAIL'};
        $vpnsettings{'ROOTCERT_OU'}        = $cgiparams{'ROOTCERT_OU'};
        $vpnsettings{'ROOTCERT_CITY'}        = $cgiparams{'ROOTCERT_CITY'};
        $vpnsettings{'ROOTCERT_STATE'}        = $cgiparams{'ROOTCERT_STATE'};
        $vpnsettings{'ROOTCERT_COUNTRY'}    = $cgiparams{'ROOTCERT_COUNTRY'};
        &writehash("${swroot}/vpn/settings", \%vpnsettings);
        `sudo fmodify "${swroot}/vpn/settings"`;

        # Replace empty strings with a .
        (my $ou = $cgiparams{'ROOTCERT_OU'}) =~ s/^\s*$/\./;
        (my $city = $cgiparams{'ROOTCERT_CITY'}) =~ s/^\s*$/\./;
        (my $state = $cgiparams{'ROOTCERT_STATE'}) =~ s/^\s*$/\./;

        # Create the CA certificate
        if (!$errormessage) {
            &log("ipsec", "Creating cacert...");
            if (open(STDIN, "-|")) {
               my $opt  = " req -x509 -nodes -rand /proc/interrupts:/proc/net/rt_cache";
                 $opt .= " -config /etc/ipsec/openssl.conf";
                 $opt .= " -days 999999";
                 $opt .= " -newkey rsa:2048";
                 $opt .= " -keyout ${swroot}/vpn/ca/private/cakey.pem";
                 $opt .= " -out ${swroot}/vpn/ca/cacerts/cacert.pem";

                $errormessage = &callssl ($opt);
            } 
          else {    #child
                  print  "$cgiparams{'ROOTCERT_COUNTRY'}\n";
                  print  "$state\n";
                  print  "$city\n";
                  print  "$cgiparams{'ROOTCERT_ORGANIZATION'}\n";
                      print  "$ou\n";
                  print  "$cgiparams{'ROOTCERT_ORGANIZATION'} CA\n";
                  print  "$cgiparams{'ROOTCERT_EMAIL'}\n";
                  exit (0);
            }
        }

        # Create the Host certificate request
        if (!$errormessage) {
            &log("ipsec", "Creating host cert...");
            if (open(STDIN, "-|")) {
               my $opt  = " req -nodes -rand /proc/interrupts:/proc/net/rt_cache";
                 $opt .= " -config /etc/ipsec/openssl.conf";
                 $opt .= " -newkey rsa:1024";
                 $opt .= " -keyout ${swroot}/vpn/ca/certs/hostkey.pem";
                 $opt .= " -out ${swroot}/vpn/ca/certs/hostreq.pem";
                 $errormessage = &callssl ($opt);
            } 
          else {    #child
                  print  "$cgiparams{'ROOTCERT_COUNTRY'}\n";
                  print  "$state\n";
                  print  "$city\n";
                  print  "$cgiparams{'ROOTCERT_ORGANIZATION'}\n";
                print  "$ou\n";
                print  "$cgiparams{'ROOTCERT_HOSTNAME'}\n";
                print  "$cgiparams{'ROOTCERT_EMAIL'}\n";
                print  ".\n";
                print  ".\n";
                  exit (0);
            }
          # added by squall: change hostkey.pem form to DER
          `/usr/bin/openssl rsa -in ${swroot}/vpn/ca/certs/hostkey.pem -out /tmp/hostkey_der.pem -outform DER`;
		  `cp ${swroot}/vpn/ca/certs/hostkey.pem ${swroot}/vpn/ca/certs/hostkey.pem.src`;
		  debug("`/usr/bin/openssl rsa -in ${swroot}/vpn/ca/certs/hostkey.pem -out /tmp/hostkey_der.pem -outform DER");
		  debug("cp ${swroot}/vpn/ca/certs/hostkey.pem ${swroot}/vpn/ca/certs/hostkey.pem.src");
          `mv /tmp/hostkey_der.pem ${swroot}/vpn/ca/certs/hostkey.pem`;
		  debug("`mv /tmp/hostkey_der.pem ${swroot}/vpn/ca/certs/hostkey.pem");
        }

    # Sign the host certificate request
       if (!$errormessage) {
           &log("ipsec", "Self signing host cert...");
           #No easy way for specifying the contain of subjectAltName without writing a config file...
           my ($fh, $v3extname) = tempfile ('/tmp/XXXXXXXX');
           print $fh <<END
           basicConstraints=CA:FALSE
           nsComment="OpenSSL Generated Certificate"
           subjectKeyIdentifier=hash
           authorityKeyIdentifier=keyid,issuer:always
END
;
            print $fh "subjectAltName=$cgiparams{'SUBJECTALTNAME'}" if ($cgiparams{'SUBJECTALTNAME'});
            close ($fh);
            
            my  $opt  = " ca -days 999999";
              $opt .= " -batch -notext";
              $opt .= " -config /etc/ipsec/openssl.conf";
              $opt .= " -in ${swroot}/vpn/ca/certs/hostreq.pem";
              $opt .= " -out ${swroot}/vpn/ca/certs/hostcert.pem";
              $opt .= " -extfile $v3extname";
	      $opt .= " -cert /var/efw/vpn/ca/cacerts/cacert.pem";
	      $opt .= " -keyfile /var/efw/vpn/ca/private/cakey.pem";
            $errormessage = &callssl ($opt);
            # unlink ("${swroot}/vpn/ca/certs/hostreq.pem"); #no more needed
            # unlink ($v3extname);
        }

        # Create an empty CRL
        if (!$errormessage) {
            &log("ipsec", "Creating emptycrl...");
            my  $opt  = " ca -gencrl";
              $opt .= " -config /etc/ipsec/openssl.conf";
              $opt .= " -out ${swroot}/vpn/ca/crls/cacrl.pem";
            $errormessage = &callssl ($opt);
        }
        
        # Successfully build CA / CERT!
        if (!$errormessage) {
            &cleanssldatabase();
            goto ROOTCERT_SUCCESS;
        }
        
        #Cleanup
        unlink ("${swroot}/vpn/ca/cacerts/cacert.pem");
        unlink ("${swroot}/vpn/ca/certs/hostkey.pem");
        unlink ("${swroot}/vpn/ca/certs/hostcert.pem");
        unlink ("${swroot}/vpn/ca/crls/cacrl.pem");
        &cleanssldatabase();
      system("fmodify /var/efw/vpn/");

  }
 if ($cgiparams{'ACTION'} eq _('Upload PKCS12 file')) {
          &log("ipsec", "Importing from p12...");
          system("echo aa >> /tmp/testme");
          if (ref ($cgiparams{'FH'}) ne 'Fh') {
               $errormessage = _('There was no file upload.');
               goto ROOTCERT_ERROR;
          }
          # Move uploaded certificate request to a temporary file
          (my $fh, my $filename) = tempfile( );
          if (copy ($cgiparams{'FH'}, $fh) != 1) {
              $errormessage = $!;
              goto ROOTCERT_ERROR;
          }

          # Extract the CA certificate from the file
          &log("ipsec", "Extracting caroot from p12...");
          if (open(STDIN, "-|")) {
              my  $opt  = " pkcs12 -cacerts -nokeys";
            $opt .= " -in $filename";
            $opt .= " -out /tmp/newcacert";
              $errormessage = &callssl ($opt);
          } else {  #child
              print "$cgiparams{'P12_PASS'}\n";
              exit (0);
          }

              # Extract the Host certificate from the file
          if (!$errormessage) {
              &log("ipsec", "Extracting host cert from p12...");
              if (open(STDIN, "-|")) {
                my  $opt  = " pkcs12 -clcerts -nokeys";
                $opt .= " -in $filename";
                $opt .= " -out /tmp/newhostcert";
                $errormessage = &callssl ($opt);
              } 
              else {  #child
                print "$cgiparams{'P12_PASS'}\n";
                exit (0);
              }
          }

          # Extract the Host key from the file
          if (!$errormessage) {
              &log("ipsec", "Extracting private key from p12...");
              if (open(STDIN, "-|")) {
                my  $opt  = " pkcs12 -nocerts -nodes";
                $opt .= " -in $filename";
                $opt .= " -out /tmp/newhostkey";
              $errormessage = &callssl ($opt);
              } 
              else {  #child
                print "$cgiparams{'P12_PASS'}\n";
                exit (0);
              }
          }

          if (!$errormessage) {
              &log("ipsec", "Moving cacert...");
              move("/tmp/newcacert", "${swroot}/vpn/ca/cacerts/cacert.pem");
              $errormessage = _('Certificate file move failed').": $!" if ($? ne 0);
              `sudo fmodify "${swroot}/vpn/ca/cacerts/cacert.pem"`;
            }

          if (!$errormessage) {
              &log("ipsec", "Moving host cert...");
              move("/tmp/newhostcert", "${swroot}/vpn/ca/certs/hostcert.pem");
              $errormessage = _('Certificate file move failed').": $!" if ($? ne 0);
              `sudo fmodify "${swroot}/vpn/ca/certs/hostcert.pem"`;
          }

          if (!$errormessage) {
              &log("ipsec", "Moving private key...");
              move("/tmp/newhostkey", "${swroot}/vpn/ca/certs/hostkey.pem");
              $errormessage = _('Certificate file move failed').": $!" if ($? ne 0);
              `sudo fmodify "${swroot}/vpn/ca/certs/hostkey.pem"`;
          }
          
          #cleanup temp files
          unlink ($filename);
          unlink ('/tmp/newcacert');
          unlink ('/tmp/newhostcert');
          unlink ('/tmp/newhostkey');
          if ($errormessage) {
              unlink ("${swroot}/vpn/ca/cacerts/cacert.pem");
              unlink ("${swroot}/vpn/ca/certs/hostcert.pem");
              unlink ("${swroot}/vpn/ca/certs/hostkey.pem");
              `sudo fdelete "${swroot}/vpn/ca/certs/hostkey.pem"`;
              `sudo fdelete "${swroot}/vpn/ca/certs/hostcert.pem"`;
              `sudo fdelete "${swroot}/vpn/ca/cacerts/cacert.pem"`;
              goto ROOTCERT_ERROR;
          }

          # Create empty CRL cannot be done because we don't have
          # the private key for this CAROOT
          # Ipcop can only import certificates

          &log("ipsec", "p12 import completed!");
          &cleanssldatabase();
          system("fmodify /var/efw/vpn/");
          goto ROOTCERT_SUCCESS;

    } 
    ROOTCERT_ERROR:
    &showhttpheaders();
    &openpage(_('VPN configuration - main'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
    ###by elvis 2011-10-8 for errormessage
    ###把后台看不懂的报错信息换成易懂的错误信息
      if ($errormessage=~/^OpenSSL .*name=subjectAltName/) {
          $errormessage = "项目名称填写格式有误.";
      }
      if ($errormessage=~/^OpenSSL .*Mac verify error: invalid password?/) {
          $errormessage = "PKCS文件密码错误.";
      }
      if(($cgiparams{'ACTION'} eq _('Upload PKCS12 file')) && ($errormessage=~/^OpenSSL/)){
          $errormessage = "上传的PKCS12文件格式不对.";
      }
    ###end
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'LEFT', _('Generate root/host certificates'));
    printf <<END
    <FORM METHOD='POST' name="ROOT_FORM" ENCTYPE='multipart/form-data'>
    <TABLE WIDTH='100%' BORDER='0' CELLSPACING='0' CELLPADDING='0'>
    <TR class="env">
    <TD class="add-div-table need_help">%s* $help_hash13</TD>
    <TD><INPUT TYPE='TEXT' NAME='ROOTCERT_ORGANIZATION' VALUE='$cgiparams{'ROOTCERT_ORGANIZATION'}' SIZE='32'></TD>
    </TR>
    
    <TR class="odd">
    <TD class="add-div-table need_help">%s* $help_hash14</TD>
    <TD><INPUT TYPE='TEXT' maxlength="64" NAME='ROOTCERT_HOSTNAME' VALUE='$cgiparams{'ROOTCERT_HOSTNAME'}' SIZE='32'></TD>
    </TR>
    
    <TR class="env">
    <TD class="add-div-table need_help">%s $help_hash15</TD>
    <TD  NOWRAP><INPUT TYPE='TEXT' NAME='ROOTCERT_EMAIL' VALUE='$cgiparams{'ROOTCERT_EMAIL'}' SIZE='32'></TD>
    </TR>
    
    <TR class="odd">
    <TD class="add-div-table need_help">%s $help_hash16</TD>
    <TD><INPUT TYPE='TEXT' NAME='ROOTCERT_OU' VALUE='$cgiparams{'ROOTCERT_OU'}' SIZE='32'></TD>
    </TR>
    
    <TR class="env">
    <TD class="add-div-table">%s</TD>
    <TD><INPUT TYPE='TEXT' NAME='ROOTCERT_CITY' VALUE='$cgiparams{'ROOTCERT_CITY'}' SIZE='32'></TD>
    </TR>
    
    <TR class="odd">
    <TD class="add-div-table need_help">%s $help_hash17</TD>
    <TD><INPUT TYPE='TEXT' NAME='ROOTCERT_STATE' VALUE='$cgiparams{'ROOTCERT_STATE'}' SIZE='32'></TD>
    </TR>
    
    <TR class="env">
    <TD class="add-div-table" >%s</TD>
    <TD ><SELECT NAME='ROOTCERT_COUNTRY'>
END
,
_('主机名'),
_('主机地址'),
_('邮件'),
_('部门'),
_('城市'),
_('省份'),
_('国家')
;
    foreach my $country (sort keys %countries) {
        print "<OPTION VALUE='$countries{$country}'";
        if ( $countries{$country} eq $cgiparams{'ROOTCERT_COUNTRY'} ) {
        print " selected='selected'";
        }
        print ">$country</option>\n";
    }
    printf <<END
        </SELECT></TD>
        </TR>
    
     <tr class="odd">
     <td class="add-div-table need_help">%s (email:*,URI:*,DNS:*,RID:*,IP:*) $help_hash18</td>
    <td><input type='text' name='SUBJECTALTNAME' value="$cgiparams{'SUBJECTALTNAME'}" size='32' /></td>
    </tr>
    
    <TR class="env hidden">
    <TD colspan="2" class="add-div-table"><B><FONT COLOR='$colourred'>%s</FONT></B>: %s </TD>
    </TR>
    
    <TR class="table-footer">
    <TD colspan="2"><INPUT class='submitbutton net_button' TYPE='submit' NAME='ACTION' VALUE='%s'></TD>
    </TR>
    </table>
  </FORM>
END
,
_('Subject alt name'),
_('WARNING'),
_('Generating the root and host certificates may take a long time. It can take up to several minutes on older hardware. Please be patient.'),
_('Generate root/host certificates'),
;

&closebox();
&openbox('100%', 'LEFT', _('Upload PKCS12 file'),);
printf<<END
<FORM METHOD='POST'  ENCTYPE='multipart/form-data'>
    <table WIDTH='100%' BORDER='0' CELLSPACING='0' CELLPADDING='0'>
    <TR class="env">
    <TD class="add-div-table">%s*</TD>
    <TD><INPUT TYPE='FILE' NAME='FH' SIZE='32'></TD>
    </TR>
    
    <TR class="odd">
    <TD class="add-div-table">%s&nbsp;*</TD>
    <TD><INPUT TYPE='PASSWORD' NAME='P12_PASS' VALUE='$cgiparams{'P12_PASS'}' SIZE='32'></TD>
    </TR>
    
    <TR class="env">
    <TR class="table-footer">
        <TD colspan="2">
        <INPUT class='submitbutton net_button' TYPE='SUBMIT' NAME='ACTION' VALUE='%s'>

        </TD>
    </TR>
    </TABLE>
  </FORM>
END
,
_('Upload PKCS12 file'),
_('PKCS12 file password'),
_('Upload PKCS12 file'),
_('Upload PKCS12 file'),
;
    &closebox();
    &closebigbox();
    check_form_root();

    
    &closepage();
    exit(0);

    ROOTCERT_SUCCESS:
    system("touch $needreload");
    system("fmodify /var/efw/vpn/");
   # `$restart`;
   # sleep $sleepDelay;
    ROOTCERT_SKIP:
###
### Download PKCS12 file
###
} 
elsif ($cgiparams{'ACTION'} eq _('Download PKCS12 file')) {
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);
    print "Content-Type: application/force-download\n";
    print "Content-Disposition: attachment; filename=" . $confighash{$cgiparams{'KEY'}}[1] . ".p12\r\n";
    print "Content-Type: application/octet-stream\r\n\r\n";
    print `/bin/cat ${swroot}/vpn/ca/certs/$confighash{$cgiparams{'KEY'}}[1].p12`;
    exit (0);

###
### Display certificate
###
} elsif ($cgiparams{'ACTION'} eq _('Show certificate')) {
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);

    if ( -f "${swroot}/vpn/ca/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem") {
    &showhttpheaders();
    &openpage(_('VPN configuration - main'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
    
        &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'LEFT', _('Certificate'));
    $output = `/usr/bin/openssl x509 -text -in ${swroot}/vpn/ca/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem`;
    $output = &cleanhtml($output,"y");
    print "<pre>$output</pre>\n";
    &closebox();
    print "<DIV ALIGN='CENTER'><A HREF='/cgi-bin/vpnmain.cgi'>"._('Back')."</A></DIV>";
    &closebigbox();
    
    &closepage();
    exit(0);
    }

###
### Download Certificate
###
} elsif ($cgiparams{'ACTION'} eq _('Download certificate')) {
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);

    if ( -f "${swroot}/vpn/ca/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem") {
    print "Content-Type: application/force-download\n";
    print "Content-Disposition: attachment; filename=" . $confighash{$cgiparams{'KEY'}}[1] . "cert.pem\r\n\r\n";
    print `/bin/cat ${swroot}/vpn/ca/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem`;
    exit (0);
    }

###
### Enable/Disable connection
###
} elsif ($cgiparams{'ACTION'} eq _('Enable or Disable')) {
    &readvpnsettings(\%vpnsettings);
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
    #2013.12.22 判断该条连接是否可以被编辑。 by ailei
    if (check_modify($confighash{$cgiparams{'KEY'}}[1])){
        goto VPNCONF_END;
    }
    if ($confighash{$cgiparams{'KEY'}}[0] eq 'off') {
        $confighash{$cgiparams{'KEY'}}[0] = 'on';
        &writehasharray("${swroot}/vpn/config", \%confighash);
        `sudo fmodify "${swroot}/vpn/caconfig"`;
        if($confighash{$cgiparams{'KEY'}}[3] eq 'net'){
            #2013.12.07 这里要更新greconfig中的配置 by wl
            &switch_greconfig($confighash{$cgiparams{'KEY'}}[1], $confighash{$cgiparams{'KEY'}}[0]);
        }
        system("touch $needreload");
   # `$restart`;
   # sleep $sleepDelay;
    } else {
        $confighash{$cgiparams{'KEY'}}[0] = 'off';
        &writehasharray("${swroot}/vpn/config", \%confighash);
        `sudo fmodify "${swroot}/vpn/caconfig"`;
        system("touch $needreload");
        if($confighash{$cgiparams{'KEY'}}[3] eq 'net'){
            #2013.12.07 这里要更新greconfig中的配置 by wl
            &switch_greconfig($confighash{$cgiparams{'KEY'}}[1], $confighash{$cgiparams{'KEY'}}[0]);
        }
   # `$restart`;
   # sleep $sleepDelay;
    }
    } else {
    $errormessage = _('Invalid key.');
    }

###
### Restart connection
###
} elsif ($cgiparams{'ACTION'} eq _('Restart')) {
    &readvpnsettings(\%vpnsettings);
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
    system("touch $needreload");
   # `$restart`;
   # sleep $sleepDelay;
    } else {
    $errormessage = _('Invalid key.');
    }

###
### Remove connection
###
} 
elsif ($cgiparams{'ACTION'} eq _('Remove')) {
    &readvpnsettings(\%vpnsettings);
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);

    if ($confighash{$cgiparams{'KEY'}}) {
        #2013.12.22 判断该条连接是否可以被编辑。 by ailei
        if (check_modify($confighash{$cgiparams{'KEY'}}[1])){
            goto VPNCONF_END;
        }
          unlink ("${swroot}/vpn/ca/certs/$confighash{$cgiparams{'KEY'}}[1]cert.pem");
          unlink ("${swroot}/vpn/ca/certs/$confighash{$cgiparams{'KEY'}}[1].p12");
        &delete_greconfig("$cgiparams{'del_name'}");
          delete $confighash{$cgiparams{'KEY'}};
          &writehasharray("${swroot}/vpn/config", \%confighash);
          `sudo fmodify "${swroot}/vpn/config"`;
        `sudo fmodify "${swroot}/vpn/greconfig"`;
          system("touch $needreload");
         # `$restart`;
         # sleep $sleepDelay;
    } 
    else {
         $errormessage = _('Invalid key.');
    }

###
### Choose between adding a host-net or net-net connection
###
} 
elsif ($cgiparams{'ACTION'} eq _('Add') && $cgiparams{'TYPE'} eq '') {
    &showhttpheaders();
    &openpage(_('VPN configuration - main'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'LEFT', _('Connection type'));    
    print "</form>";
    print "<form name='CN_FORM enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>";
    printf <<END  
        <TABLE cellpadding="0" cellspacing="0" border="0">
        <FORM enctype='multipart/form-data'  METHOD='POST'>
        <TR class="env"><TD class="add-div-table" rowspan="2">%s</td><td><INPUT TYPE='RADIO' NAME='TYPE' VALUE='host' checked='checked'></TD><TD>%s</TD></TR>
        <TR class="env"><TD><INPUT TYPE='RADIO' NAME='TYPE' VALUE='net'></TD>
        <TD>%s</TD></TR>
        <TR class="table-footer"><TD ALIGN='CENTER' COLSPAN='3'><INPUT class='submitbutton net_button' TYPE='SUBMIT' NAME='ACTION' VALUE='%s'></TD></TR>
        </FORM></TABLE>
END
,
_('Connection type'),
_('主机-网络 虚拟专用网络'),
_('网络-网络 虚拟专用网络'),
_('Add')
;
    &closebox();
    closebigbox();
    
    closepage();
    exit (0);
###
### Adding a new connection
###
} 
elsif (($cgiparams{'ACTION'} eq _('Add')) ||
     ($cgiparams{'ACTION'} eq _('Edit')) ||
     ($cgiparams{'ACTION'} eq _('Save') && $cgiparams{'ADVANCED'} eq '')) {
    $cgiparams{'AUTH'} =~s/(.*)\|certgen/$1/;
    &readvpnsettings(\%vpnsettings);
    &readhasharrayOrEmpty("${swroot}/vpn/caconfig", \%cahash);
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);

    if ($cgiparams{'ACTION'} eq _('Edit')) {
        if (! $confighash{$cgiparams{'KEY'}}[0]) {
            $errormessage = _('Invalid key.');
            goto VPNCONF_END;
        }
        #2013.12.22 判断该条连接是否可以被编辑。 by ailei
        if (check_modify($confighash{$cgiparams{'KEY'}}[1])){
            goto VPNCONF_END;
        }
        $cgiparams{'ENABLED'}    = $confighash{$cgiparams{'KEY'}}[0];
        $cgiparams{'NAME'}    = $confighash{$cgiparams{'KEY'}}[1];
        $cgiparams{'TYPE'}    = $confighash{$cgiparams{'KEY'}}[3];
        $cgiparams{'AUTH'}     = $confighash{$cgiparams{'KEY'}}[4];
        $cgiparams{'PSK'}    = $confighash{$cgiparams{'KEY'}}[5];
        $cgiparams{'LOCAL_ID'}        = $confighash{$cgiparams{'KEY'}}[7];
        #2013-6-21 add
        open(FILE,"/var/efw/vpn/greconfig");
        my @tmp_lines = <FILE>;
        close(FILE);
        foreach my $one_line (@tmp_lines)
        {
            #2013.12.18 这里不能直接看是否包含$cgiparams{'NAME'}，如果存在两条连接如con2和con22,后一条的信息会被读成为前一条的 by wl
          #if($one_line =~ /$cgiparams{'NAME'}/) #注释掉以前的
          if($one_line =~ /,$cgiparams{'NAME'},/) #现在的判断，这样就可以判断出完整的名字
          {
            my @splited_line = split(',',$one_line);
            $cgiparams{'GRE_INTERFACE'} = $splited_line[1];
            $cgiparams{'LOCAL_SUBNET'} = $splited_line[4];
            $cgiparams{'REMOTE_SUBNET'} = $splited_line[6];
          }
        }
        #$cgiparams{'LOCAL_SUBNET'} = $confighash{$cgiparams{'KEY'}}[8];
        #2013.12.09 当添加主机模式时，点击编辑不能显示本地子网的bug by wl
        if($cgiparams{'TYPE'} eq 'host'){
            $cgiparams{'LOCAL_SUBNET'} = $confighash{$cgiparams{'KEY'}}[8];
        }
        #2013.12.09 end
        $cgiparams{'REMOTE_ID'}            = $confighash{$cgiparams{'KEY'}}[9];
        $cgiparams{'REMOTE'}            = $confighash{$cgiparams{'KEY'}}[10];
        #2013-6-21 change remote_submnet to remote for gretuunel.
        #$cgiparams{'REMOTE_SUBNET'}     = $confighash{$cgiparams{'KEY'}}[11];
        $cgiparams{'REMARK'}            = $confighash{$cgiparams{'KEY'}}[25];
        $cgiparams{'INTERFACE'}            = $confighash{$cgiparams{'KEY'}}[26];
        $cgiparams{'DPD_ACTION'}        = $confighash{$cgiparams{'KEY'}}[27];
        $cgiparams{'IKE_ENCRYPTION'}     = $confighash{$cgiparams{'KEY'}}[18];
        $cgiparams{'IKE_INTEGRITY'}      = $confighash{$cgiparams{'KEY'}}[19];
        $cgiparams{'IKE_GROUPTYPE'}      = $confighash{$cgiparams{'KEY'}}[20];
        $cgiparams{'IKE_LIFETIME'}       = $confighash{$cgiparams{'KEY'}}[16];
        $cgiparams{'ESP_ENCRYPTION'}     = $confighash{$cgiparams{'KEY'}}[21];
        $cgiparams{'ESP_INTEGRITY'}      = $confighash{$cgiparams{'KEY'}}[22];
        $cgiparams{'ESP_KEYLIFE'}        = $confighash{$cgiparams{'KEY'}}[17];
        $cgiparams{'AGGRMODE'}             = $confighash{$cgiparams{'KEY'}}[12];
        $cgiparams{'COMPRESSION'}        = $confighash{$cgiparams{'KEY'}}[13];
        $cgiparams{'ONLY_PROPOSED'}      = $confighash{$cgiparams{'KEY'}}[24];
        $cgiparams{'PFS'}                = $confighash{$cgiparams{'KEY'}}[28];
        $cgiparams{'VHOST'}                = $confighash{$cgiparams{'KEY'}}[14];
    
    } elsif ($cgiparams{'ACTION'} eq _('Save')) {
    $cgiparams{'REMARK'} = &cleanhtml($cgiparams{'REMARK'});
    if ($cgiparams{'TYPE'} !~ /^(host|net)$/) {
        $errormessage = _('Connection type is invalid.');
        goto VPNCONF_ERROR;
    }

    if ($cgiparams{'NAME'} !~ /^[a-zA-Z0-9_]+$/) {
        $errormessage = _('连接名格式不合法.');
        goto VPNCONF_ERROR;
    }

    if ($cgiparams{'NAME'} =~ /^(host|01|block|private|clear|packetdefault)$/) {
        $errormessage = _('Name is invalid');
        goto VPNCONF_ERROR;
    }

    if (length($cgiparams{'NAME'}) >60) {
        $errormessage = _('User\'s full name or system hostname is too long');
        goto VPNCONF_ERROR;
    }

    $cgiparams{'REMOTE_ID'} =~ s/\ //g;
    $cgiparams{'LOCAL_ID'} =~ s/\ //g;
    $cgiparams{'REMOTE_ID'} =~ s/,/$commareplacement/g;
    $cgiparams{'LOCAL_ID'} =~ s/,/$commareplacement/g;

    # Check if there is no other entry with this name
    if (! $cgiparams{'KEY'}) {
        foreach my $key (keys %confighash) {
        if ($confighash{$key}[1] eq $cgiparams{'NAME'}) {
            $errormessage = _('A connection with this name already exists.');
            goto VPNCONF_ERROR;
        }
        }
    }
=pod    
    #2013.12.09 现在要判断只要上行线路相同即不能建立连接
    if (! $cgiparams{'KEY'}) {
        foreach my $key (keys %confighash) {
            if ($confighash{$key}[26] eq $cgiparams{'INTERFACE'}) {
                $errormessage = "一个具有相同上行线路的连接已存在。";
                goto VPNCONF_ERROR;
            }
        }
    }
=cut

#    if (($cgiparams{'TYPE'} eq 'net') && (! $cgiparams{'REMOTE'})) {
#        $errormessage = _('Invalid input for remote host/ip.');
#        goto VPNCONF_ERROR;
#    }

    if ($cgiparams{'REMOTE'}) {
        if (! &validip($cgiparams{'REMOTE'})) {
            if (! &validfqdn ($cgiparams{'REMOTE'}))  
            {
                $errormessage = _('Invalid input for remote host/ip.');
                goto VPNCONF_ERROR;
            }else{
#                    if (&valid_dns_host($cgiparams{'REMOTE'})) {
#                    $warnmessage = _('DNS check of "%s" failed', $cgiparams{'REMOTE'});
#                 }
        }
        }
    }

        #unless (&validipandmask($cgiparams{'LOCAL_SUBNET'})) {
        #   $errormessage = _('Local subnet is invalid.');
        #goto VPNCONF_ERROR;
    #    }

    # Allow only one roadwarrior/psk without remote IP-address
    if ($cgiparams{'REMOTE'} eq '' && $cgiparams{'AUTH'} eq 'psk') {
        foreach my $key (keys %confighash) {
        if(($cgiparams{'KEY'} ne $key) && 
           ($confighash{$key}[4] eq 'psk') &&
           ($confighash{$key}[10] eq '')) {
            $errormessage = _('系统已存在一个使用预共享密钥的连接，不能设置多个使用预共享密钥的连接<br />请选择其他身份认证方式.');
            goto VPNCONF_ERROR;
        }
        }
    }
    if ($cgiparams{'ENABLED'} !~ /^(on|off)$/) {
        $errormessage = _('Invalid input');
        goto VPNCONF_ERROR;
    }
    if ($cgiparams{'EDIT_ADVANCED'} !~ /^(on|off)$/) {
        $errormessage = _('Invalid input');
        goto VPNCONF_ERROR;
    }

    # Allow nothing or a string (DN,FDQN,)
    # with no comma but slashes between RID eg @O=FR/C=Paris/OU=myhome/CN=franck
    #if (($cgiparams{'LOCAL_ID'} ne '') && ($cgiparams{'LOCAL_ID'} !~ /^([0-9a-zA-Z_])+$/)) {
    if (($cgiparams{'LOCAL_ID'} ne '') && ($cgiparams{'LOCAL_ID'} !~ /^[a-zA-Z][0-9a-zA-Z]{3,19}$/)) {#字母串只能是数字和字母，并且字母开头 2013.12.19 by wl
        #2013.12.19 修改为LOCAL_ID允许字串(字母和数字，字母开头，4-20位)、IP和域名 by wl
        if( !validip($cgiparams{'LOCAL_ID'}) && !validdomainname($cgiparams{'LOCAL_ID'}) ){
            $errormessage = _('Invalid local id.');
            goto VPNCONF_ERROR;
        }
    }
    #if (($cgiparams{'REMOTE_ID'} ne '') && ($cgiparams{'REMOTE_ID'} !~ /^([0-9a-zA-Z_])+$/)) {
    if (($cgiparams{'REMOTE_ID'} ne '') && ($cgiparams{'REMOTE_ID'} !~ /^[a-zA-Z][0-9a-zA-Z]{3,19}$/)) {#字母串只能是数字和字母，并且字母开头 2013.12.19 by wl
        #2013.12.19 修改为可以通过IP 和域名类型 by wl
        if( !validdomainname($cgiparams{'REMOTE_ID'}) && !validip($cgiparams{'REMOTE_ID'}) ){
            $errormessage = _('Invalid remote id.');
            goto VPNCONF_ERROR;
        }
    }
    if ( ($cgiparams{'REMOTE_ID'} eq $cgiparams{'LOCAL_ID'}) && ($cgiparams{'LOCAL_ID'} ne '') ) {
        $errormessage = _('When used, leftid and rightid must not be equal.');
        goto VPNCONF_ERROR;
    }
    # If Auth is DN, verify existance of Remote ID.
    if ( $cgiparams{'REMOTE_ID'} eq '' && 
         ($cgiparams{'AUTH'} eq 'auth-dn'||            # while creation
          $confighash{$cgiparams{'KEY'}}[2] eq '%auth-dn')){ # while editing
        $errormessage = _('选择远程ID验证时，远程ID不能为空.');
        goto VPNCONF_ERROR;
    }

    if ($cgiparams{'AUTH'} eq 'psk')  {
        if (! length($cgiparams{'PSK'}) ) {
        $errormessage = _('Pre-shared key is too short.');
        goto VPNCONF_ERROR;
        }
        if ($cgiparams{'PSK'} =~ /['",&]/) {  #'
        $errormessage = _('Invalid characters found in pre-shared key.');
        goto VPNCONF_ERROR;
        }
    } elsif ($cgiparams{'AUTH'} eq 'certreq') {
        if ($cgiparams{'KEY'}) {
        $errormessage = _('Can\'t change certificates.');
        goto VPNCONF_ERROR;
        }
        if (ref ($cgiparams{'FH'}) ne 'Fh') {
        $errormessage = _('There was no file upload.');
        goto VPNCONF_ERROR;
        }

        # Move uploaded certificate request to a temporary file
        (my $fh, my $filename) = tempfile( );
        if (copy ($cgiparams{'FH'}, $fh) != 1) {
        $errormessage = $!;
        goto VPNCONF_ERROR;
        }

        # Sign the certificate request and move it
        &log("ipsec", "Signing your cert $cgiparams{'NAME'}...");
            my     $opt  = " ca -days 999999";
        $opt .= " -config /etc/ipsec/openssl.conf";
        $opt .= " -batch -notext";
        $opt .= " -in $filename";
        $opt .= " -out ${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem";
        $errormessage = &callssl ($opt);
        if ($errormessage =~/Expecting: CERTIFICATE REQUEST/) {
            $errormessage = "上传的证书有误!";
        }
        if ( $errormessage ) {
        unlink ($filename);
        unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
        &cleanssldatabase();
        goto VPNCONF_ERROR;
        } else {
        unlink ($filename);
        &cleanssldatabase();
        }

        
        $cgiparams{'CERT_NAME'} = getCNfromcert ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
        if ($cgiparams{'CERT_NAME'} eq '') {
        $errormessage = _('Could not retrieve common name from certificate.');
        goto VPNCONF_ERROR;
        }
    } elsif ($cgiparams{'AUTH'} eq 'pkcs12') {
        &log("ipsec", "Importing from p12...");

        if (ref ($cgiparams{'FH'}) ne 'Fh') {
            $errormessage = _('There was no file upload');
                goto ROOTCERT_ERROR;
        }

        # Move uploaded certificate request to a temporary file
        (my $fh, my $filename) = tempfile( );
        if (copy ($cgiparams{'FH'}, $fh) != 1) {
            $errormessage = $!;
            goto ROOTCERT_ERROR;
        }

        # Extract the CA certificate from the file
        &log("ipsec", "Extracting caroot from p12...");
        if (open(STDIN, "-|")) {
                my    $opt  = " pkcs12 -cacerts -nokeys";
            $opt .= " -in $filename";
            $opt .= " -out /tmp/newcacert";
            $errormessage = &callssl ($opt);    
        } else {    #child
            print "$cgiparams{'P12_PASS'}\n";
            exit (0);
        }

            # Extract the Host certificate from the file
        if (!$errormessage) {
            &log("ipsec", "Extracting host cert from p12...");
            if (open(STDIN, "-|")) {
                my  $opt  = " pkcs12 -clcerts -nokeys";
            $opt .= " -in $filename";
            $opt .= " -out /tmp/newhostcert";
            $errormessage = &callssl ($opt);
            } else {    #child
            print "$cgiparams{'P12_PASS'}\n";
            exit (0);
            }
        }

        if (!$errormessage) {        
            &log("ipsec", "Moving cacert...");
            #If CA have new subject, add it to our list of CA
            my $casubject = &cleanhtml(getsubjectfromcert ('/tmp/newcacert'));
            my @names;
            foreach my $x (keys %cahash) {
            $casubject='' if ($cahash{$x}[1] eq $casubject);
            unshift (@names,$cahash{$x}[0]);
            }
            if ($casubject) { # a new one!
            my $temp = `/usr/bin/openssl x509 -text -in /tmp/newcacert`;
            if ($temp !~ /CA:TRUE/i) {
                $errormessage = _('Not a valid CA certificate');
            } else {
                #compute a name for it
                my $idx=0;
                while (grep(/Imported-$idx/, @names) ) {$idx++};
                $cgiparams{'CA_NAME'}="Imported-$idx";
                $cgiparams{'CERT_NAME'}=&cleanhtml(getCNfromcert ('/tmp/newhostcert'));
                move("/tmp/newcacert", "${swroot}/vpn/ca/cacerts/$cgiparams{'CA_NAME'}cert.pem");
                $errormessage = _('Certificate file move failed').": $!" if ($? ne 0);
                if (!$errormessage) {
                my $key = &findhasharraykey (\%cahash);
                $cahash{$key}[0] = $cgiparams{'CA_NAME'};
                $cahash{$key}[1] = $casubject;
                &writehasharray("${swroot}/vpn/caconfig", \%cahash);
                `sudo fmodify "${swroot}/vpn/caconfig"`;
                system("touch $needreload");
                }
                }
            }    
        }
        if (!$errormessage) {
            &log("ipsec", "Moving host cert...");
            move("/tmp/newhostcert", "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
            $errormessage = _('Certificate file move failed').": $!" if ($? ne 0);
            `sudo fmodify "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem"`;
        }

        #cleanup temp files
        unlink ($filename);
        unlink ('/tmp/newcacert');
        unlink ('/tmp/newhostcert');
        if ($errormessage) {
            unlink ("${swroot}/vpn/ca/cacerts/$cgiparams{'CA_NAME'}cert.pem");
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
            `sudo fdelete "${swroot}/vpn/ca/cacerts/$cgiparams{'NAME'}cert.pem"`;
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem"`;
            goto VPNCONF_ERROR;
        }
        &log("ipsec", "p12 import completed!");
    } elsif ($cgiparams{'AUTH'} eq 'certfile') {
        if ($cgiparams{'KEY'}) {
        $errormessage = _('Can\'t change certificates.');
        goto VPNCONF_ERROR;
        }
        if (ref ($cgiparams{'FH'}) ne 'Fh') {
        $errormessage = _('There was no file upload.');
        goto VPNCONF_ERROR;
        }
        # Move uploaded certificate to a temporary file
        (my $fh, my $filename) = tempfile( );
        if (copy ($cgiparams{'FH'}, $fh) != 1) {
        $errormessage = $!;
        goto VPNCONF_ERROR;
        }

        # Verify the certificate has a valid CA and move it
        &log("ipsec", "Validating imported cert against our known CA...");
        my $validca = 1;
        my $test = `/usr/bin/openssl verify -CAfile ${swroot}/vpn/ca/cacerts/cacert.pem $filename`;
        chomp($test);
        if ($test !~ /OK$/) {
            $validca = 0;
            foreach $key (keys %cahash) {
                $test = `/usr/bin/openssl verify -CAfile ${swroot}/vpn/ca/cacerts/$cahash{$key}[0]cert.pem $filename`;
                chomp($test);
                if ($test =~ /OK$/) {
                    $validca = 1;
                    last;
                }
            }
        }
        if (!$validca) {
            $errormessage .= _('Certificate does not have a valid CA associated with it.');
            unlink ($filename);
            goto VPNCONF_ERROR;
        } else {
            move($filename, "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
            if ($? ne 0) {
                $errormessage = _('Certificate file move failed: \'%s\'', $!);
                unlink ($filename);
                goto VPNCONF_ERROR;
            }
            `sudo fmodify "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem"`;
        }

        $cgiparams{'CERT_NAME'} = getCNfromcert ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
        if ($cgiparams{'CERT_NAME'} eq '') {
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem"`;
            $errormessage = _('Could not retrieve common name from certificate.');
            goto VPNCONF_ERROR;
        }
    } elsif ($cgiparams{'AUTH'} eq 'certgen') {
        if ($cgiparams{'KEY'}) {
            $errormessage = _('Can\'t change certificates.');
            goto VPNCONF_ERROR;
        }
        # Validate input since the form was submitted
        if (length($cgiparams{'CERT_NAME'}) >60) {
            $errormessage = _('User\'s full name or system hostname is too long');
            goto VPNCONF_ERROR;
        }
        if ($cgiparams{'CERT_NAME'} !~ /^[a-zA-Z0-9 ,\.\-_]+$/) {
            $errormessage = _('Invalid input for user\'s full name or system hostname');
            goto VPNCONF_ERROR;
        }
        if ($cgiparams{'CERT_EMAIL'} ne '' && (! validemail($cgiparams{'CERT_EMAIL'}))) {
            $errormessage = _('Invalid input for email address.');
            goto VPNCONF_ERROR;
        }
        if (length($cgiparams{'CERT_EMAIL'}) > 40) {
            $errormessage = _('Email address is too long; it should not be longer than 40 characters.');
            goto VPNCONF_ERROR;
        }
        if ($cgiparams{'CERT_OU'} ne '' && $cgiparams{'CERT_OU'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
            $errormessage = _('Invalid input for department.');
            goto VPNCONF_ERROR;
        }
        if (length($cgiparams{'CERT_ORGANIZATION'}) >60) {
            $errormessage = _('Organization is too long; it should not be longer than 60 characters.');
            goto VPNCONF_ERROR;
        }
        if ($cgiparams{'CERT_ORGANIZATION'} !~ /^[a-zA-Z0-9 ,\.\-_]+$/) {
            $errormessage = _('Invalid input for organization');
            goto VPNCONF_ERROR;
        }
        if ($cgiparams{'CERT_CITY'} ne '' && $cgiparams{'CERT_CITY'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
            $errormessage = _('Invalid input for city.');
            goto VPNCONF_ERROR;
        }
        if ($cgiparams{'CERT_STATE'} ne '' && $cgiparams{'CERT_STATE'} !~ /^[a-zA-Z0-9 ,\.\-_]*$/) {
            $errormessage = _('Invalid input for state or province.');
            goto VPNCONF_ERROR;
        }
        if ($cgiparams{'CERT_COUNTRY'} !~ /^[A-Z]*$/) {
            $errormessage = _('Invalid input for country.');
            goto VPNCONF_ERROR;
        }
        #the exact syntax is a list comma separated of 
        #  email:any-validemail
        #    URI: a uniform resource indicator
        #   DNS: a DNS domain name
        #   RID: a registered OBJECT IDENTIFIER
        #   IP: an IP address
        # example: email:franck@foo.com,IP:10.0.0.10,DNS:franck.foo.com

        if ($cgiparams{'SUBJECTALTNAME'} ne '' && $cgiparams{'SUBJECTALTNAME'} !~ /^(email|URI|DNS|RID|IP):[a-zA-Z0-9 :\/,\.\-_@]*$/) {
            $errormessage = _('SubjectAltName is a comma separated list of email, dns, uri, rid and IP objects.<br />email:an email address. Syntax email:copy takes the email field from the cert to be used.<br />DNS:a valid domain name.<br />URI:any valid uri.<br />RID:registered object identifier.<br />IP:an IP address.<br />Note:charset is limited and case is significant.<br />Example:<br /><b>email:</b>user@yourmail.com<b>,email:</b>copy<b>,DNS:</b>www.yourdomain.com<b>,IP:</b>127.0.0.1<b>,URI:</b>http://url/to/something');
            goto VPNCONF_ERROR;
        }
        else{
            $flag = 0;
            if ($cgiparams{'SUBJECTALTNAME'} =~/^email:(.*)/) {
                if (!validemail($1)) {
                    $flag = 1;
                }
            }
            if ($cgiparams{'SUBJECTALTNAME'} =~/^DNS|IP:(.*)/) {
                if (!validdomainname($1) && !validip($1) ) {
                    $flag = 1;
                }
            }
            if ($cgiparams{'SUBJECTALTNAME'} =~/^URI:(.*)/) {
                my $uri = $1;
                my $last;
                if ($uri !~/^(http|file|ftp|telne|gopher|https|news|Idap):\/\/(.*)/) {
                    $flag = 1;
                }
                else{
                    $uri =~/^(http|file|ftp|telne|gopher|https|news|Idap):\/\/(.*)/;
                    $last = $1;
                    if (!&validdomainname($last)) {
                        $flag = 1;
                    }
                }
            }
            if ($flag) {
                $errormessage = _('旧项目名称格式错误!');
                #goto VPNCONF_ERROR;   原来版本跳转到一开始的页面
                goto ROOTCERT_ERROR;# 现在改为跳到自己出错的页面
            }
        }
        if (length($cgiparams{'CERT_PASS1'}) < 6) {
            $errormessage = _('Password is too short.');
            goto VPNCONF_ERROR;
        }
        if($cgiparams{'CERT_PASS1'} !~/^[a-zA-Z0-9]+$/){
            $errormessage = _('PKCS12 文件保护密码只能由数字和字母组成.');
            goto VPNCONF_ERROR;
        }
        if ($cgiparams{'CERT_PASS1'} ne $cgiparams{'CERT_PASS2'}) {
            $errormessage = _('Passwords do not match.');
            goto VPNCONF_ERROR;
        }

        # Replace empty strings with a .
        (my $ou = $cgiparams{'CERT_OU'}) =~ s/^\s*$/\./;
        (my $city = $cgiparams{'CERT_CITY'}) =~ s/^\s*$/\./;
        (my $state = $cgiparams{'CERT_STATE'}) =~ s/^\s*$/\./;

        # Create the Host certificate request
        &log("ipsec", "Creating a cert...");


        if (open(STDIN, "-|")) {
            my $opt  = " req -nodes -rand /proc/interrupts:/proc/net/rt_cache";
        $opt .= " -config /etc/ipsec/openssl.conf";
        $opt .= " -newkey rsa:1024";
        $opt .= " -keyout ${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem";
        $opt .= " -out ${swroot}/vpn/ca/certs/$cgiparams{'NAME'}req.pem";

        if ( $errormessage = &callssl ($opt) ) {
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem");
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}req.pem");
            goto VPNCONF_ERROR;
            }
        } else {    #child
            print  "$cgiparams{'CERT_COUNTRY'}\n";
            print  "$state\n";
            print  "$city\n";
            print  "$cgiparams{'CERT_ORGANIZATION'}\n";
            print  "$ou\n";
            print  "$cgiparams{'CERT_NAME'}\n";
            print  "$cgiparams{'CERT_EMAIL'}\n";
            print  ".\n";
            print  ".\n";
            exit (0);
        }
        
        # Sign the host certificate request
        &log("ipsec", "Signing the cert $cgiparams{'NAME'}...");

        #No easy way for specifying the contain of subjectAltName without writing a config file...
        my ($fh, $v3extname) = tempfile ('/tmp/XXXXXXXX');
        print $fh <<END
        basicConstraints=CA:FALSE
        nsComment="OpenSSL Generated Certificate"
        subjectKeyIdentifier=hash
        authorityKeyIdentifier=keyid,issuer:always
END
;
        print $fh "subjectAltName=$cgiparams{'SUBJECTALTNAME'}" if ($cgiparams{'SUBJECTALTNAME'});
        close ($fh);

        my $opt  = " ca -days 999999 -batch -notext";
        $opt .= " -config /etc/ipsec/openssl.conf";
        $opt .= " -in ${swroot}/vpn/ca/certs/$cgiparams{'NAME'}req.pem";
        $opt .= " -out ${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem";
        $opt .= " -extfile $v3extname";

        if ( $errormessage = &callssl ($opt) ) {
            # unlink ($v3extname);
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem");
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}req.pem");
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem"`;
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}req.pem"`;
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem"`;
            &cleanssldatabase();
            goto VPNCONF_ERROR;
        } else {
            # unlink ($v3extname);
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}req.pem");
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}req.pem"`;
            &cleanssldatabase();
        }

        # Create the pkcs12 file
        &log("ipsec", "Packing a pkcs12 file...");
        $opt  = " pkcs12 -export"; 
        $opt .= " -inkey ${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem";
        $opt .= " -in ${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem";
        $opt .= " -name \"$cgiparams{'NAME'}\"";
        $opt .= " -passout pass:$cgiparams{'CERT_PASS1'}";
        $opt .= " -certfile ${swroot}/vpn/ca/cacerts/cacert.pem";
        $opt .= " -caname \"$vpnsettings{'ROOTCERT_ORGANIZATION'} CA\"";
        $opt .= " -out ${swroot}/vpn/ca/certs/$cgiparams{'NAME'}.p12";

        if ( $errormessage = &callssl ($opt) ) {
			debug('#1');
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem");
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem");
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}.p12");
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem"`;
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}.p12"`;
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}cert.pem"`;
            goto VPNCONF_ERROR;
        } else {
			debug('#2');
            unlink ("${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem");
            `sudo fdelete "${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem"`;
			debug("sudo fdelete \"${swroot}/vpn/ca/certs/$cgiparams{'NAME'}key.pem\"");
        }
    } elsif ($cgiparams{'AUTH'} eq 'cert') {
        ;# Nothing, just editing
    } elsif ($cgiparams{'AUTH'} eq 'auth-dn') {
        $cgiparams{'CERT_NAME'} = '%auth-dn';    # a special value saying 'no cert file'
    } else {
        $errormessage = _('Invalid input for authentication method.');
        goto VPNCONF_ERROR;
    }

    # 1)Error message here is not accurate.
    # 2)Test is superfluous, openswan can reference same cert multiple times
    # 3)Present since initial version (1.3.2.11), it isn't a bug correction
    # Check if there is no other entry with this certificate name
    #if ((! $cgiparams{'KEY'}) && ($cgiparams{'AUTH'} ne 'psk') && ($cgiparams{'AUTH'} ne 'auth-dn')) {
    #    foreach my $key (keys %confighash) {
    #    if ($confighash{$key}[2] eq $cgiparams{'CERT_NAME'}) {
    #        $errormessage = $Lang::tr{'a connection with this common name already exists'};
    #        goto VPNCONF_ERROR;
    #    }
    #    }
    #}

        # Save the config
    my $key = $cgiparams{'KEY'};
    my $local_net = "";
    foreach my $elem(split(/\r\n/,$cgiparams{'LOCAL_SUBNET'})){
        $elem = "$elem&";
        $local_net = $local_net.$elem;
    }
    my $remote_net = "";
    foreach my $elem(split(/\r\n/,$cgiparams{'REMOTE_SUBNET'})){
        $elem = "$elem&";
        $remote_net = $remote_net.$elem;
    }
    $local_net =~s/&$//;
    $remote_net =~s/&$//;
    if (! $key) {
        $key = &findhasharraykey (\%confighash);
        foreach my $i (0 .. 28) { $confighash{$key}[$i] = "";}
    }
    $confighash{$key}[0] = $cgiparams{'ENABLED'};
    $confighash{$key}[1] = $cgiparams{'NAME'};
    if ((! $cgiparams{'KEY'}) && $cgiparams{'AUTH'} ne 'psk') {
        $confighash{$key}[2] = $cgiparams{'CERT_NAME'};
    }
    $confighash{$key}[3] = $cgiparams{'TYPE'};
    if ($cgiparams{'AUTH'} eq 'psk') {
        $confighash{$key}[4] = 'psk';
        $confighash{$key}[5] = $cgiparams{'PSK'};
    } else {
        $confighash{$key}[4] = 'cert';
    }
    if ($cgiparams{'TYPE'} eq 'net') {
=pod
      #2013-7-25 新加若远程ID不为空时将config文件中第11个字段改为存储远程ID+/32，为空时照旧为远程IP+/32
      if($cgiparams{'REMOTE_ID'} ne '')
      {
          $confighash{$key}[11] = $cgiparams{'REMOTE_ID'};
      } else {
          $confighash{$key}[11] = $cgiparams{'REMOTE'};
      }
=cut
        #2013.12.06 修改为关联了gre,则填写gre中的远程地址
        if($cgiparams{'GRE_INGTERFACE'} ne '' || $cgiparams{'GRE_INGTERFACE'} ne 'None')
        {
            $confighash{$key}[11] = $cgiparams{'REMOTE_ID'};
        } else {
            $confighash{$key}[11] = $cgiparams{'REMOTE'};
        }
      
      #
      $confighash{$key}[11] .= "/32";
      #2013-6-21 change
        # $confighash{$key}[11] = $remote_net;#$cgiparams{'REMOTE_SUBNET'};
    }
    $confighash{$key}[7] = $cgiparams{'LOCAL_ID'};
    

  #2013-6-21 add
  if($cgiparams{'INTERFACE'} eq 'UPLINK:main')
  {
       open(READFILE,"/var/efw/uplinks/main/settings");
  } else {
       my @split = split(':',$cgiparams{'INTERFACE'});
       my $path = "/var/efw/uplinks/";
       $path .= $split[1];
       $path .="/settings";
       open(READFILE,$path);
  }
 
  my @main_result = <READFILE>;
  close(READFILE);
  my $local_one_net = "";
  foreach my $one (@main_result)
  {
      my @split = split('=',$one);
      if($split[0] eq 'RED_ADDRESS')
        {
          $local_one_net = $split[1];
          $local_one_net =~ s/[\r\n]//;
          $local_one_net .= "/32";
        }
  }

    $confighash{$key}[8] = $local_one_net;#$cgiparams{'LOCAL_SUBNET'};
    #2013.12.09 当是主机模式是，点击编辑不能显示本地子网的 bug by wl
    if($cgiparams{'TYPE'} eq 'host'){
        $confighash{$key}[8] = $cgiparams{'LOCAL_SUBNET'};
    }
    #2013.12.09 end
    $confighash{$key}[9] = $cgiparams{'REMOTE_ID'};
    $confighash{$key}[10] = $cgiparams{'REMOTE'};
    $confighash{$key}[25] = $cgiparams{'REMARK'};
    $confighash{$key}[26] = $cgiparams{'INTERFACE'};
    $confighash{$key}[27] = $cgiparams{'DPD_ACTION'};

    #dont forget advanced value
    $confighash{$key}[18] = $cgiparams{'IKE_ENCRYPTION'};
    $confighash{$key}[19] = $cgiparams{'IKE_INTEGRITY'};
    $confighash{$key}[20] = $cgiparams{'IKE_GROUPTYPE'};
    $confighash{$key}[16] = $cgiparams{'IKE_LIFETIME'};
    $confighash{$key}[21] = $cgiparams{'ESP_ENCRYPTION'};
    $confighash{$key}[22] = $cgiparams{'ESP_INTEGRITY'};
    #ESP_GROUPTYPE is not supported anymore since openswan 2.6.21
    $confighash{$key}[17] = $cgiparams{'ESP_KEYLIFE'};
    $confighash{$key}[12] = $cgiparams{'AGGRMODE'};
    $confighash{$key}[13] = $cgiparams{'COMPRESSION'};
    $confighash{$key}[24] = $cgiparams{'ONLY_PROPOSED'};
    $confighash{$key}[28] = $cgiparams{'PFS'};
    $confighash{$key}[14] = $cgiparams{'VHOST'};

    #free unused fields!
    $confighash{$key}[15] = 'off';
    $confighash{$key}[23] = 'off';
    #2013.12.06 如果关联了gre,要另外保存gre配置中的本地地址和远程地址
    #读取gre中的配置
    my @gre_configs = read_conf_file("/var/efw/gre/config");
    my $choosed_gre_item;
    foreach my $gre_config (@gre_configs){
        my @gre_config_splitted = split(/,/, $gre_config);
        if($gre_config_splitted[0] eq $cgiparams{'GRE_INTERFACE'}){
            $choosed_gre_item = $gre_config;
            last;
        }
    }
    my @choosed_gre_configs = split(/,/, $choosed_gre_item);
    my $local_addr = $choosed_gre_configs[1];
    my $remote_addr = $choosed_gre_configs[2];
    

    ####保存配置文件
    if ($cgiparams{'TYPE'} eq 'net') {
        #2013.12.06 如果关联了gre,要另外保存gre配置中的本地地址和远程地址
        if($cgiparams{'GRE_INTERFACE'} eq '' || $cgiparams{'GRE_INTERFACE'} eq 'None' ){
            $confighash{$key}[8] = $local_net;
            $confighash{$key}[11] = $remote_net;
            &writehasharray("${swroot}/vpn/config", \%confighash);
        }else{
            $confighash{$key}[8] = $local_addr."/32";
            $confighash{$key}[11] = $remote_addr."/32";
            &writehasharray("${swroot}/vpn/config", \%confighash);
        }
    }else{
        &writehasharray("${swroot}/vpn/config", \%confighash);
    }
    `sudo fmodify "${swroot}/vpn/config"`;
    system("touch $needreload");
    ####如果是子网方式保存路由信息
    if ($cgiparams{'TYPE'} eq 'net') {
        #2013.12.06 如果关联了gre,要另外保存gre配置中的本地地址和远程地址
        if($cgiparams{'GRE_INTERFACE'} eq '' || $cgiparams{'GRE_INTERFACE'} eq 'None' ){
            #2013-7-25 新加远程ID不为空时将greconfig中的原$cgiparams{'REMOTE'} 改为存储 $cgiparams{'REMOTE_ID'}
            if($cgiparams{'REMOTE_ID'} ne '')
            {
               &save_greconfig($cgiparams{'ENABLED'},$cgiparams{'GRE_INTERFACE'},$cgiparams{'NAME'},$cgiparams{'INTERFACE'},$local_net,$cgiparams{'REMOTE_ID'},$remote_net);
            } else {
               &save_greconfig($cgiparams{'ENABLED'},$cgiparams{'GRE_INTERFACE'},$cgiparams{'NAME'},$cgiparams{'INTERFACE'},$local_net,$cgiparams{'REMOTE'},$remote_net);
            }
        }else{
            &save_greconfig($cgiparams{'ENABLED'},$cgiparams{'GRE_INTERFACE'},$cgiparams{'NAME'},$local_addr,$local_net,$remote_addr,$remote_net);
        }
    }
    
   # `$restart`;
   # sleep $sleepDelay;
    if ($cgiparams{'EDIT_ADVANCED'} eq 'on') {
        $cgiparams{'KEY'} = $key;
        $cgiparams{'ACTION'} = _('Advanced');
    }
    goto VPNCONF_END;
    } else {
        $cgiparams{'ENABLED'} = 'on';
    if ( ! -f "${swroot}/vpn/ca/private/cakey.pem" ) {
        $cgiparams{'AUTH'} = 'psk';
    } elsif ( ! -f "${swroot}/vpn/ca/cacerts/cacert.pem") {
        $cgiparams{'AUTH'} = 'certfile';
    } else {
            $cgiparams{'AUTH'} = 'certgen';
    }
    $cgiparams{'LOCAL_SUBNET'}      = $netsettings{'GREEN_NETADDRESS'}."/".$netsettings{'GREEN_CIDR'};
    $cgiparams{'CERT_EMAIL'}     = $vpnsettings{'ROOTCERT_EMAIL'};
    $cgiparams{'CERT_OU'}         = $vpnsettings{'ROOTCERT_OU'};
    $cgiparams{'CERT_ORGANIZATION'} = $vpnsettings{'ROOTCERT_ORGANIZATION'};
    $cgiparams{'CERT_CITY'}         = $vpnsettings{'ROOTCERT_CITY'};
    $cgiparams{'CERT_STATE'}        = $vpnsettings{'ROOTCERT_STATE'};
    $cgiparams{'CERT_COUNTRY'}      = $vpnsettings{'ROOTCERT_COUNTRY'};


    # choose appropriate dpd action    
    if ($cgiparams{'TYPE'} eq 'host') {
        $cgiparams{'DPD_ACTION'} = 'clear';
    } else {
        $cgiparams{'DPD_ACTION'} = 'restart';
    }

    # Default is yes for 'pfs'
    $cgiparams{'PFS'}     = 'on';
    
    # ID are empty
    $cgiparams{'LOCAL_ID'}  = '';
    $cgiparams{'REMOTE_ID'} = '';

    #use default advanced value
    $cgiparams{'IKE_ENCRYPTION'} = 'aes128|3des';    #[18];
    $cgiparams{'IKE_INTEGRITY'}  = 'sha|md5';    #[19];
    $cgiparams{'IKE_GROUPTYPE'}  = '1536|1024';    #[20];
    $cgiparams{'IKE_LIFETIME'}   = '1';        #[16];
    $cgiparams{'ESP_ENCRYPTION'} = 'aes128|3des';    #[21];
    $cgiparams{'ESP_INTEGRITY'}  = 'sha1|md5';    #[22];
    $cgiparams{'ESP_KEYLIFE'}    = '8';        #[17];
    $cgiparams{'AGGRMODE'}         = 'off';        #[12];
    $cgiparams{'COMPRESSION'}    = 'off';        #[13];
    $cgiparams{'ONLY_PROPOSED'}  = 'off';        #[24];
    $cgiparams{'PFS'}         = 'on';        #[28];
    $cgiparams{'VHOST'}          = 'on';         #[14];
    }

    VPNCONF_ERROR:
    $checked{'ENABLED'}{'off'} = '';
    $checked{'ENABLED'}{'on'} = '';
    $checked{'ENABLED'}{$cgiparams{'ENABLED'}} = 'CHECKED';
    $checked{'ENABLED_ORANGE'}{'off'} = '';
    $checked{'ENABLED_ORANGE'}{'on'} = '';
    $checked{'ENABLED_ORANGE'}{$cgiparams{'ENABLED_ORANGE'}} = "checked='checked'";
    $checked{'ENABLED_BLUE'}{'off'} = '';
    $checked{'ENABLED_BLUE'}{'on'} = '';
    $checked{'ENABLED_BLUE'}{$cgiparams{'ENABLED_BLUE'}} = 'CHECKED';

    $checked{'EDIT_ADVANCED'}{'off'} = '';
    $checked{'EDIT_ADVANCED'}{'on'} = '';
    $checked{'EDIT_ADVANCED'}{$cgiparams{'EDIT_ADVANCED'}} = 'CHECKED';

    $checked{'AUTH'}{'psk'} = '';
    $checked{'AUTH'}{'certreq'} = '';
    $checked{'AUTH'}{'certgen'} = '';
    $checked{'AUTH'}{'certfile'} = '';
    $checked{'AUTH'}{'pkcs12'} = '';
    $checked{'AUTH'}{'auth-dn'} = '';;
    $checked{'AUTH'}{$cgiparams{'AUTH'}} = 'CHECKED';

    $selected{'INTERFACE'}{'RED'} = '';
    $selected{'INTERFACE'}{'ORANGE'} = '';
    $selected{'INTERFACE'}{'GREEN'} = '';
    $selected{'INTERFACE'}{'BLUE'} = '';
    $selected{'INTERFACE'}{$cgiparams{'INTERFACE'}} = "selected='selected'";
    if ($selected{'INTERFACE'}{'RED'} ne "") {
            %upinfo = get_uplink_info('main','');
            if ($upinfo{'RED_TYPE'} ne 'NONE') {
                  $selected{'INTERFACE'}{'UPLINK:main'} = "selected='selected'";
            } else {
                @uplinks = get_uplinks_list();
                foreach my $tmp_uplink (@uplinks) {
                    %upinfo = get_uplink_info($tmp_uplink,'');
                    if ($upinfo{'RED_TYPE'} ne 'NONE') {
                          $selected{'INTERFACE'}{'UPLINK:'.$tmp_uplink} = "selected='selected'";
                    }                    
                }            
            }
    }

    $selected{'DPD_ACTION'}{'clear'} = '';
    $selected{'DPD_ACTION'}{'hold'} = '';
    $selected{'DPD_ACTION'}{'restart'} = '';
    $selected{'DPD_ACTION'}{$cgiparams{'DPD_ACTION'}} = "selected='selected'";

    if (1) {
    &showhttpheaders();
    &openpage(_('虚拟专用网络'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
        if ($errormessage =~/invalid password/) {
            $errormessage = "证书密码错误!";
        }
        if (($cgiparams{'AUTH'} eq "pkcs12") && $errormessage && ($errormessage !~/invalid password/)) {
            $errormessage = "pkcs12证书错误!";
        }

        &openbigbox($errormessage, $warnmessage, $notemessage);


    print<<END
        <FORM METHOD='POST' name="CN_FORM" ENCTYPE='multipart/form-data'>
        <input type='hidden' name='TYPE' value='$cgiparams{'TYPE'}' />
        <input type='hidden' name='IKE_ENCRYPTION' value='$cgiparams{'IKE_ENCRYPTION'}' />
        <input type='hidden' name='IKE_INTEGRITY' value='$cgiparams{'IKE_INTEGRITY'}' />
        <input type='hidden' name='IKE_GROUPTYPE' value='$cgiparams{'IKE_GROUPTYPE'}' />
        <input type='hidden' name='IKE_LIFETIME' value='$cgiparams{'IKE_LIFETIME'}' />
        <input type='hidden' name='ESP_ENCRYPTION' value='$cgiparams{'ESP_ENCRYPTION'}' />
        <input type='hidden' name='ESP_INTEGRITY' value='$cgiparams{'ESP_INTEGRITY'}' />
        <input type='hidden' name='ESP_KEYLIFE' value='$cgiparams{'ESP_KEYLIFE'}' />
        <input type='hidden' name='AGGRMODE' value='$cgiparams{'AGGRMODE'}' />
        <input type='hidden' name='COMPRESSION' value='$cgiparams{'COMPRESSION'}' />
        <input type='hidden' name='ONLY_PROPOSED' value='$cgiparams{'ONLY_PROPOSED'}' />
        <input type='hidden' name='PFS' value='$cgiparams{'PFS'}' />
        <input type='hidden' name='VHOST' value='$cgiparams{'VHOST'}' />
END
;
    if ($cgiparams{'KEY'}) {
        print "<input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />";
        print "<input type='hidden' name='AUTH' value='$cgiparams{'AUTH'}' />";
    }

    &openbox('100%', 'LEFT', _('Connection configuration'));
    print "<TABLE cellpadding='0' cellspacing='0' border='0'>\n";
    print "<TR class='env'><TD WIDTH='25%' CLASS='add-div-table need_help'>"._('连接名')." *$help_hash19</TD>";
    if ($cgiparams{'KEY'}) {
        print "<TD colspan='3'><INPUT TYPE='HIDDEN' NAME='NAME' VALUE='$cgiparams{'NAME'}'>$cgiparams{'NAME'}</TD>";
    } else {
        print "<TD colspan='3'><INPUT TYPE='TEXT' NAME='NAME' VALUE='$cgiparams{'NAME'}' MAXLENGTH='20' SIZE='30'></TD>";
    }
    printf <<END
    </tr>
    <tr class="odd">
        <td class="add-div-table">%s</td>
        <td colspan="3"><input type='checkbox' name='ENABLED' $checked{'ENABLED'}{'on'} /></td>
    </tr>
END
, _('Enabled')
;
    if ($cgiparams{'TYPE'} ne 'host') {
        printf <<END
        <!--2013.12.5 by wl begin-->
        <tr class="env">
            <td class="add-div-table">关联gre接口</td>
            <td colspan="3">
                <select name="GRE_INTERFACE">
                    <option value="">不选择</option>
END
        ;
                #打印未被使用的gre接口
                #如果是编辑状态，则要打印自己之前的接口，并标为选中
                my @gre_interfaces = read_conf_file("/var/efw/gre/config");
                my @choosed_gres = read_conf_file("/var/efw/vpn/greconfig");
                foreach my  $gre_interface (@gre_interfaces){
                    my @gre_interface_splitted = split(/,/, $gre_interface);
                    my $choosed = 0;
                    my $selected = 0;#编辑状态下选中的
                    foreach my $choosed_gre (@choosed_gres){
                        my @choosed_gre_splitted = split(/,/, $choosed_gre);
                        if($gre_interface_splitted[0] eq $choosed_gre_splitted[1]){
                            $choosed = 1;
                            if($cgiparams{'GRE_INTERFACE'} eq $choosed_gre_splitted[1]){#如果是我之前选的
                                $selected = 1;
                            }
                            last;
                        }
                    }
                    if(!$choosed){
                        print '<option value="'.$gre_interface_splitted[0].'">gre'.$gre_interface_splitted[0].'</option>';
                    }else{
                        if($selected){
                            print '<option value="'.$gre_interface_splitted[0].'" selected>gre'.$gre_interface_splitted[0].'</option>';
                        }
                    }
                }
        
        printf <<END
                </select>
            </td>
        </tr>
        <!--2013.12.5 by wl end-->
END
        ;
        }
    printf <<END
     <tr class="env">
        <td class="add-div-table" rowspan="3"><b>%s *</b></td>
END
, _('Local')
;


        $uplinkoptions = "";
        foreach my $ref (@{get_uplinks_list()}) {
            my $name = $ref->{'name'};
            my $key = $ref->{'dev'};
            my $desc = $ref->{'description'};
            $uplinkoptions .= sprintf("<option value='$key' %s>%s $desc</option>\n",
                                      $selected{'INTERFACE'}{$key},
                                      _("Uplink"));
        }

    if ($cgiparams{'TYPE'} eq 'host') {
        print "<TD>"._('Interface')."</TD>";
        print "<TD colspan='2'><SELECT NAME='INTERFACE'>";
        print $uplinkoptions;
        if ($netsettings{'BLUE_DEV'} ne '' && $hotspotsettings{'HOTSPOT_ENABLED'} ne 'on') {
            printf "<OPTION VALUE='BLUE' $selected{'INTERFACE'}{'BLUE'}>%s",_('BLUE');
        }
        printf "<OPTION VALUE='ORANGE' $selected{'INTERFACE'}{'ORANGE'}>%s",_('ORANGE');
         printf "<OPTION VALUE='GREEN' $selected{'INTERFACE'}{'GREEN'}>%s",_('GREEN');
        print "</SELECT></TD></tr>";
        printf <<END
            <tr class="env">
            <TD class="need_help">%s *$help_hash2</td>
            <td colspan="2"><input  NAME='LOCAL_SUBNET' value="$cgiparams{'LOCAL_SUBNET'}" ></TD>
            </tr>
            
            <tr class="env">
            <td class="need_help">%s $help_hash3</td>
            <td colspan="2"><input type='text' name='LOCAL_ID' value='$cgiparams{'LOCAL_ID'}' /></td>
            </tr>
            
            <tr class="odd">
            <TD class="add-div-table" rowspan="2">%s *</td>
            <td class="need_help">%s *</TD>
            <TD colspan="2"><INPUT TYPE='TEXT' NAME='REMOTE' VALUE='$cgiparams{'REMOTE'}' SIZE='30'></TD>
            </tr>
            
            <tr class="odd">
            <td>%s&nbsp;</td>
            <td colspan="2"><input type='text' name='REMOTE_ID' value='$cgiparams{'REMOTE_ID'}' /></td>
            </tr>
END
, _('Local subnet')
, _('Local ID')
,_('Remote')
,_('远程IP')
,_('Remote ID')
;
    } else {
        $cgiparams{'LOCAL_SUBNET'} =~s/&/\n/g;
        $cgiparams{'REMOTE_SUBNET'} =~s/&/\n/g;
        printf <<END
            <TD>%s</TD>
            <TD colspan="2">
            <select name="INTERFACE">
            $uplinkoptions
            </select>
            </TD>
            </tr>
            
        <TR class="env">
        <TD class="need_help">%s *$help_hash2</TD>
        <TD colspan="2"><textarea NAME='LOCAL_SUBNET' wrap="off" >$cgiparams{'LOCAL_SUBNET'}</textarea></TD>
        </tr>
        
        <tr class="env">
        <td class="need_help">%s&nbsp;$help_hash3</td>
        <td colspan="2"><input type='text' name='LOCAL_ID' value='$cgiparams{'LOCAL_ID'}' /></td>
        </tr>
        
        <tr class="odd">
        <TD class="add-div-table" rowspan="3">%s *</td>
         <TD>%s</TD>
        <TD colspan="2"><INPUT TYPE='TEXT' NAME='REMOTE' VALUE='$cgiparams{'REMOTE'}'></TD>
        </TR>
            
        <tr class="odd">
        <td class="need_help">%s * $help_hash4</TD>
        <TD colspan="2"><textarea NAME='REMOTE_SUBNET' wrap="off" >$cgiparams{'REMOTE_SUBNET'}</textarea></TD>
        </TR>
        
        <tr class="odd">
        <td>%s&nbsp;</td>
        <td colspan="2"><input type='text' name='REMOTE_ID' value='$cgiparams{'REMOTE_ID'}' /></td>
        </tr>
            
END
,_('Interface')
, _('Local subnet')
, _('Local ID')
,_('Remote')
,_('远程IP')
,_('Remote subnet')
,_('Remote ID')
;
    }
    
    my $num = 2;
    if (!$cgiparams{'KEY'})
    {
        $num = 3;
    }else{
        $num =2;
    }
    printf <<END
     <tr class="env">
     <td class="add-div-table" rowspan=$num>%s</td>
     <td>%s</td>
     <td colspan="2"><select name='DPD_ACTION'>
            <option value='clear' $selected{'DPD_ACTION'}{'clear'}>%s</option>
            <option value='hold' $selected{'DPD_ACTION'}{'hold'}>%s</option>
            <option value='restart' $selected{'DPD_ACTION'}{'restart'}>%s</option>
        </select>&nbsp;
    </td>
    </tr>

    <tr class="env">
    <td>%s &nbsp;</td><td  colspan="2"><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='55' maxlength='50' /></td>
    </tr>
END
, _('Options')
, _('Dead peer detection action')
, _('Clear')
, _('Hold')
, _('Restart')
, _('Remark')
;
    if (!$cgiparams{'KEY'}) {
        print "<tr class='env'><td colspan='1' class='need_help'> "._('Edit advanced settings')."$help_hash5</td><td ><input type='checkbox' name='EDIT_ADVANCED' $checked{'EDIT_ADVANCED'}{'on'} /></td></tr>";
    }
    
    
    if ($cgiparams{'KEY'} && $cgiparams{'AUTH'} eq 'psk') {
        
        printf <<END
        <TR class="odd">
        <TD class="add-div-table">%s *</TD>
        <td class='need_help'>%s *$help_hash6</td>
        <TD colspan="2"><INPUT TYPE='password' NAME='PSK' SIZE=32 VALUE='$cgiparams{'PSK'}'></TD></TR>
END
,_('Authentication'),
,_('Use a pre-shared key')
;
    } elsif (! $cgiparams{'KEY'}) {
        my $disabled;
        my $cakeydisabled='';
        my $cacrtdisabled='';
        my $row = 2;
    my $option = "<option value='psk'>使用预共享密钥</option>";
        my $hidden_class;
        if ( ! -f "${swroot}/vpn/ca/private/cakey.pem" ) 
        {
            $cakeydisabled = "disabled='disabled'" ;
        } else { 
            $cakeydisabled = "" 
        };
        if ( ! -f "${swroot}/vpn/ca/cacerts/cacert.pem" ) { $cacrtdisabled = "disabled='disabled'" ;$row = 1; $hidden_class="hidden_class";} 
      else { 
        $cacrtdisabled = "";
        $option .= "<option value='certfile'>选择对端证书</option>"
      }; 
        printf <<END
        <TR class="odd">      
    <td class="add-div-table" rowspan="1">%s *</td>
    <TD class='need_help'>
    <select NAME="AUTH" id="AUTH">
    $option
    </select>
    </TD>
    <TD colspan="2" ><INPUT id='psk_value' TYPE='password' NAME='PSK' SIZE=32 VALUE='$cgiparams{'PSK'}'>
    <INPUT id="filed" TYPE='FILE' NAME='FH' SIZE='32' class="hidden_class" $cacrtdisabled>
    </TD>
      <!--
        <TD class='need_help'><INPUT  TYPE='RADIO' NAME='AUTH' VALUE='psk' $checked{'AUTH'}{'psk'}>%s *$help_hash6</TD>
        <TD colspan="2" ><INPUT TYPE='password' NAME='PSK' SIZE=32 VALUE='$cgiparams{'PSK'}'></TD>
    -->

        </TR>
        
        <TR class="odd hidden_class">
        <TD><INPUT TYPE='RADIO' NAME='AUTH' VALUE='certfile' $checked{'AUTH'}{'certfile'} $cacrtdisabled> %s $help_hash7</TD>
        <TD colspan="2"  class='need_help'>  <INPUT TYPE='FILE' NAME='FH' SIZE='32' $cacrtdisabled></TD>
        </TR>
        
        <TR class="odd hidden_class">
        <TD><INPUT TYPE='RADIO' NAME='AUTH' VALUE='certreq' $checked{'AUTH'}{'certreq'} $cakeydisabled> </TD>
        <TD class='need_help'>%s $help_hash8</TD>
        </TR>
        
        <tr class="odd hidden_class">
        <td><input type='radio' name='AUTH' value='pkcs12' $cacrtdisabled /></td>
        <td class='need_help'><ul><li>%s</li><li>%s &nbsp;<input type='password' name='P12_PASS'/></li></ul>$help_hash9</td>
        </tr>
        
        <tr class="odd hidden_class">
        <td><input type='radio' name='AUTH' value='auth-dn' $checked{'AUTH'}{'auth-dn'} $cacrtdisabled /></td>
        <td colspan="2">%s</td>
        </tr>

        <TR class="odd hidden_class">
        <TD><INPUT TYPE='RADIO' NAME='AUTH' VALUE='certgen' $checked{'AUTH'}{'certgen'} $cakeydisabled></TD>
        <TD colspan="2" class='need_help'>%s $help_hash10</TD>
        </TR>
        
        <TR class="odd hidden_class">
        <td></td>
        <TD >%s</TD>
        <TD ><INPUT TYPE='TEXT' NAME='CERT_NAME' VALUE='$cgiparams{'CERT_NAME'}' SIZE='32' $cakeydisabled></TD>
        </TR>
        
        <TR class="odd hidden_class">
        <td></td>
        <TD>%s&nbsp;</TD>
        <TD ><INPUT TYPE='TEXT' NAME='CERT_EMAIL' VALUE='$cgiparams{'CERT_EMAIL'}' SIZE='32' $cakeydisabled></TD>
        </TR>
        
        <TR class="odd hidden_class">
        <td></td>
        <TD>%s&nbsp;</TD>
        <TD><INPUT TYPE='TEXT' NAME='CERT_OU' VALUE='$cgiparams{'CERT_OU'}' SIZE='32' $cakeydisabled></TD>
        </TR>
        
        <TR class="odd hidden_class">
        <td></td>
        <TD >%s&nbsp;</TD>
        <TD  NOWRAP><INPUT TYPE='TEXT' NAME='CERT_ORGANIZATION' VALUE='$cgiparams{'CERT_ORGANIZATION'}' SIZE='32' $cakeydisabled></TD>
        </TR>
        
        <TR class="odd hidden_class" >
        <td></td>
        <TD >%s&nbsp;</TD>
        <TD  NOWRAP><INPUT TYPE='TEXT' NAME='CERT_CITY' VALUE='$cgiparams{'CERT_CITY'}' SIZE='32' $cakeydisabled></TD>
        </TR>
        
        <TR class="odd hidden_class">
        <td></td>
        <TD >%s&nbsp;</TD>
        <TD  NOWRAP><INPUT TYPE='TEXT' NAME='CERT_STATE' VALUE='$cgiparams{'CERT_STATE'}' SIZE='32' $cakeydisabled></TD>
        </TR>
        
        <TR class="odd hidden_class">
        <td></td>
        <TD >%s</TD>
        <TD ><SELECT NAME='CERT_COUNTRY' $cakeydisabled>
END
,
_('Authentication'),
_('Upload a certificate'),
_('Upload PKCS12 file'),
_('PKCS12 file password'),
_('Peer is identified by either IPV4_ADDR, FQDN, USER_FQDN or DER_ASN1_DN string in remote ID field'),
_('Generate a certificate'),
_('User\'s full name or system hostname'),
_('User\'s email address'),
_('User\'s department'),
_('Organization name'),
_('City'),
_('State or province'),
_('Country')
;
        foreach my $country (sort keys %countries) {
        print "<OPTION VALUE='$countries{$country}'";
        if ( $countries{$country} eq $cgiparams{'CERT_COUNTRY'} ) {
            print " SELECTED";
        }
        print ">$country</option>\n";
        }
        printf <<END
        </SELECT></TD></TR>

          <tr class="odd hidden_class">
        <td></td>
            <td class="need_help">%s* (subjectAltName=email:*,URI:*,DNS:*,RID:*,IP:*) $help_hash18</td>
            <td nowrap='nowrap'><input type='text' name='SUBJECTALTNAME' value='$cgiparams{'SUBJECTALTNAME'}' size='32' $cakeydisabled /></td>
        </tr>
        <tr class="odd hidden_class">
        <td></td>
            <td >%s *</td>
            <td  nowrap='nowrap'><input type='password' name='CERT_PASS1' value='$cgiparams{'CERT_PASS1'}' size='32' $cakeydisabled /></td>
        </tr>
        <tr  class="odd hidden_class">
        <td></td>
            <td >%s(%s) *</td>
            <td  nowrap='nowrap'><input type='password' name='CERT_PASS2' value='$cgiparams{'CERT_PASS2'}' size='32' $cakeydisabled /></td>
        </tr>
    
END
, _('Subject alt name')
, _('PKCS12 file password')
, _('PKCS12 file password')
, _('Confirmation')
;
       
    }

    print "<tr class='table-footer'><td colspan='2'><INPUT class='submitbutton net_button' style='display:block;float:right;color:black'  TYPE='SUBMIT' NAME='ACTION' VALUE='"._('Save')."'> ";
    if ($cgiparams{'KEY'}) {
        print "<INPUT class='submitbutton net_button' TYPE='SUBMIT' NAME='ACTION' VALUE='"._('Advanced')."'> ";
    }
     my $cancelvalue = _('Cancel');
     my $url = $ENV{'SCRIPT_NAME'};
    printf <<EOF
                </td>
                <td colspan='2'>
                    <input class='net_button' type='button'  value='$cancelvalue' style="display:block;float:left;color:black" onclick="parent.window.document.getElementById('rightFrame').src='$url'"/>
                </td>
            </tr>
        </FORM>
    </table>
EOF
;
    print "";
    &closebox();
    closebigbox();
    check_form_cn();
    system("fmodify /var/efw/vpn/");
    closepage();
    exit (0);
    }
    VPNCONF_END:
}

###
### Advanced settings
###
if(($cgiparams{'ACTION'} eq _('Advanced')) ||
   ($cgiparams{'ACTION'} eq _('Save') && $cgiparams{'ADVANCED'} eq 'yes')) {
    &readvpnsettings(\%vpnsettings);
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);
    if (! $confighash{$cgiparams{'KEY'}}) {
    $errormessage = _('Invalid key.');
    goto ADVANCED_END;
    }

    if ($cgiparams{'ACTION'} eq _('Save')) {
    # I didn't read any incompatibilities here....
    #if ($cgiparams{'VHOST'} eq 'on' && $cgiparams{'COMPRESSION'} eq 'on') {
    #    $errormessage = $Lang::tr{'cannot enable both nat traversal and compression'};
    #    goto ADVANCED_ERROR;
    #}
    my @temp = split('\|', $cgiparams{'IKE_ENCRYPTION'});
    if ($#temp < 0) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
    }
    #2013-7-20 新加SM1
    foreach my $val (@temp) {
        if ($val !~ /^(aes256|aes128|SM1|3des|twofish256|twofish128|serpent256|serpent128|blowfish256|blowfish128|cast128)$/) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
        }
    }
    @temp = split('\|', $cgiparams{'IKE_INTEGRITY'});
    if ($#temp < 0) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
    }
    foreach my $val (@temp) {
        if ($val !~ /^(sha2_512|sha2_256|sha|md5)$/) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
        }
    }
    @temp = split('\|', $cgiparams{'IKE_GROUPTYPE'});
    if ($#temp < 0) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
    }
    foreach my $val (@temp) {
        if ($val !~ /^(768|1024|1536|2048|3072|4096|6144|8192)$/) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
        }
    }
    if ($cgiparams{'IKE_LIFETIME'} !~ /^\d+$/) {
        $errormessage = _('Invalid input for IKE lifetime');
        goto ADVANCED_ERROR;
    }
    if ($cgiparams{'IKE_LIFETIME'} < 1 || $cgiparams{'IKE_LIFETIME'} > 8) {
        $errormessage = _('IKE lifetime should be between 1 and 8 hours.');
        goto ADVANCED_ERROR;
    }
    @temp = split('\|', $cgiparams{'ESP_ENCRYPTION'});
    if ($#temp < 0) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
    }
    foreach my $val (@temp) {
        if ($val !~ /^(aes256|aes128|3des|twofish256|twofish128|serpent256|serpent128|blowfish256|blowfish128)$/) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
        }
    }
    @temp = split('\|', $cgiparams{'ESP_INTEGRITY'});
    if ($#temp < 0) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
    }
    foreach my $val (@temp) {
        if ($val !~ /^(sha2_512|sha2_256|sha1|md5)$/) {
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
        }
    }

    if ($cgiparams{'ESP_KEYLIFE'} !~ /^\d+$/) {
        $errormessage = _('输入错误的ESP周期.');
        goto ADVANCED_ERROR;
    }
    if ($cgiparams{'ESP_KEYLIFE'} < 1 || $cgiparams{'ESP_KEYLIFE'} > 24) {
        $errormessage = _('ESP key life should be between 1 and 24 hours.');
        goto ADVANCED_ERROR;
    }

    if (
        ($cgiparams{'AGGRMODE'} !~ /^(|on|off)$/) ||
        ($cgiparams{'COMPRESSION'} !~ /^(|on|off)$/) ||
        ($cgiparams{'ONLY_PROPOSED'} !~ /^(|on|off)$/) ||
        ($cgiparams{'PFS'} !~ /^(|on|off)$/) ||
        ($cgiparams{'VHOST'} !~ /^(|on|off)$/)
    ){
        $errormessage = _('Invalid input');
        goto ADVANCED_ERROR;
    }

    $confighash{$cgiparams{'KEY'}}[18] = $cgiparams{'IKE_ENCRYPTION'};
    $confighash{$cgiparams{'KEY'}}[19] = $cgiparams{'IKE_INTEGRITY'};
    $confighash{$cgiparams{'KEY'}}[20] = $cgiparams{'IKE_GROUPTYPE'};
    $confighash{$cgiparams{'KEY'}}[16] = $cgiparams{'IKE_LIFETIME'};
    $confighash{$cgiparams{'KEY'}}[21] = $cgiparams{'ESP_ENCRYPTION'};
    $confighash{$cgiparams{'KEY'}}[22] = $cgiparams{'ESP_INTEGRITY'};
    #ESP_GROUPTYPE is not supported anymore since openswan 2.6.21
    $confighash{$cgiparams{'KEY'}}[23] = '';
    $confighash{$cgiparams{'KEY'}}[17] = $cgiparams{'ESP_KEYLIFE'};
    $confighash{$cgiparams{'KEY'}}[12] = $cgiparams{'AGGRMODE'};
    $confighash{$cgiparams{'KEY'}}[13] = $cgiparams{'COMPRESSION'};
    $confighash{$cgiparams{'KEY'}}[24] = $cgiparams{'ONLY_PROPOSED'};
    $confighash{$cgiparams{'KEY'}}[28] = $cgiparams{'PFS'};
    $confighash{$cgiparams{'KEY'}}[14] = $cgiparams{'VHOST'};
    &writehasharray("${swroot}/vpn/config", \%confighash);
    `sudo fmodify "${swroot}/vpn/caconfig"`;
    system("touch $needreload");
   # `$restart`;
   # sleep $sleepDelay;
    goto ADVANCED_END;
    } else {
    $cgiparams{'IKE_ENCRYPTION'} = $confighash{$cgiparams{'KEY'}}[18];
    $cgiparams{'IKE_INTEGRITY'}  = $confighash{$cgiparams{'KEY'}}[19];
    $cgiparams{'IKE_GROUPTYPE'}  = $confighash{$cgiparams{'KEY'}}[20];
    $cgiparams{'IKE_LIFETIME'}   = $confighash{$cgiparams{'KEY'}}[16];
    $cgiparams{'ESP_ENCRYPTION'} = $confighash{$cgiparams{'KEY'}}[21];
    $cgiparams{'ESP_INTEGRITY'}  = $confighash{$cgiparams{'KEY'}}[22];
    $cgiparams{'ESP_KEYLIFE'}    = $confighash{$cgiparams{'KEY'}}[17];
    $cgiparams{'AGGRMODE'}       = $confighash{$cgiparams{'KEY'}}[12];
    $cgiparams{'COMPRESSION'}    = $confighash{$cgiparams{'KEY'}}[13];
    $cgiparams{'ONLY_PROPOSED'}  = $confighash{$cgiparams{'KEY'}}[24];
    $cgiparams{'PFS'}           = $confighash{$cgiparams{'KEY'}}[28];
    $cgiparams{'VHOST'}          = $confighash{$cgiparams{'KEY'}}[14];

    if ($confighash{$cgiparams{'KEY'}}[3] eq 'net' || $confighash{$cgiparams{'KEY'}}[10]) {
        $cgiparams{'VHOST'}            = 'off';
    }
    }

    ADVANCED_ERROR:
    $checked{'NAT'}{'off'} = '';
    $checked{'NAT'}{'on'} = '';
    $checked{'NAT'}{$cgiparams{'NAT'}} = 'CHECKED';
    $checked{'COMPRESSION'}{'off'} = '';
    $checked{'COMPRESSION'}{'on'} = '';
    $checked{'COMPRESSION'}{$cgiparams{'COMPRESSION'}} = 'CHECKED';
    $checked{'IKE_ENCRYPTION'}{'aes256'} = '';
    $checked{'IKE_ENCRYPTION'}{'aes128'} = '';
    $checked{'IKE_ENCRYPTION'}{'3des'} = '';
    #2013-7-20
    $checked{'IKE_ENCRYPTION'}{'SM1'} = '';
    #
    $checked{'IKE_ENCRYPTION'}{'twofish256'} = '';
    $checked{'IKE_ENCRYPTION'}{'twofish128'} = '';
    $checked{'IKE_ENCRYPTION'}{'serpent256'} = '';
    $checked{'IKE_ENCRYPTION'}{'serpent128'} = '';
    $checked{'IKE_ENCRYPTION'}{'blowfish256'} = '';
    $checked{'IKE_ENCRYPTION'}{'blowfish128'} = '';
    $checked{'IKE_ENCRYPTION'}{'cast128'} = '';
    my @temp = split('\|', $cgiparams{'IKE_ENCRYPTION'});
    foreach my $key (@temp) {$checked{'IKE_ENCRYPTION'}{$key} = "selected='selected'"; }
    $checked{'IKE_INTEGRITY'}{'sha2_512'} = '';
    $checked{'IKE_INTEGRITY'}{'sha2_256'} = '';
    $checked{'IKE_INTEGRITY'}{'sha'} = '';
    $checked{'IKE_INTEGRITY'}{'md5'} = '';
    @temp = split('\|', $cgiparams{'IKE_INTEGRITY'});
    foreach my $key (@temp) {$checked{'IKE_INTEGRITY'}{$key} = "selected='selected'"; }
    $checked{'IKE_GROUPTYPE'}{'768'} = '';
    $checked{'IKE_GROUPTYPE'}{'1024'} = '';
    $checked{'IKE_GROUPTYPE'}{'1536'} = '';
    $checked{'IKE_GROUPTYPE'}{'2048'} = '';
    $checked{'IKE_GROUPTYPE'}{'3072'} = '';
    $checked{'IKE_GROUPTYPE'}{'4096'} = '';
    $checked{'IKE_GROUPTYPE'}{'6144'} = '';
    $checked{'IKE_GROUPTYPE'}{'8192'} = '';
    @temp = split('\|', $cgiparams{'IKE_GROUPTYPE'});
    foreach my $key (@temp) {$checked{'IKE_GROUPTYPE'}{$key} = "selected='selected'"; }
    $checked{'ESP_ENCRYPTION'}{'aes256'} = '';
    $checked{'ESP_ENCRYPTION'}{'aes128'} = '';
    $checked{'ESP_ENCRYPTION'}{'3des'} = '';
    $checked{'ESP_ENCRYPTION'}{'twofish256'} = '';
    $checked{'ESP_ENCRYPTION'}{'twofish128'} = '';
    $checked{'ESP_ENCRYPTION'}{'serpent256'} = '';
    $checked{'ESP_ENCRYPTION'}{'serpent128'} = '';
    $checked{'ESP_ENCRYPTION'}{'blowfish256'} = '';
    $checked{'ESP_ENCRYPTION'}{'blowfish128'} = '';
    @temp = split('\|', $cgiparams{'ESP_ENCRYPTION'});
    foreach my $key (@temp) {$checked{'ESP_ENCRYPTION'}{$key} = "selected='selected'"; }
    $checked{'ESP_INTEGRITY'}{'sha2_512'} = '';
    $checked{'ESP_INTEGRITY'}{'sha2_256'} = '';
    $checked{'ESP_INTEGRITY'}{'sha1'} = '';
    $checked{'ESP_INTEGRITY'}{'md5'} = '';
    @temp = split('\|', $cgiparams{'ESP_INTEGRITY'});
    foreach my $key (@temp) {$checked{'ESP_INTEGRITY'}{$key} = "selected='selected'"; }
    $checked{'AGGRMODE'} = $cgiparams{'AGGRMODE'} eq 'on' ? "checked='checked'" : '' ;
    $checked{'COMPRESSION'} = $cgiparams{'COMPRESSION'} eq 'on' ? "checked='checked'" : '' ;
    $checked{'ONLY_PROPOSED'} = $cgiparams{'ONLY_PROPOSED'} eq 'on' ? "checked='checked'" : '' ;
    $checked{'PFS'} = $cgiparams{'PFS'} eq 'on' ? "checked='checked'" : '' ;
    $checked{'VHOST'} = $cgiparams{'VHOST'} eq 'on' ? "checked='checked'" : '' ;

    &showhttpheaders();
    &openpage(_('VPN configuration - main'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
    
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'LEFT', _('Advanced connection parameters'));
    printf <<EOF
    <form method='post' enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'>
    <input type='hidden' name='ADVANCED' value='yes' />
    <input type='hidden' name='KEY' value='$cgiparams{'KEY'}' />
    <table width='100%' BORDER='0' CELLSPACING='0' CELLPADDING='0'>

    <tr class="env">
        <td class="add-div-table" rowspan="4"><b>%s</b></td>
        <td>%s</td>
        <td>
            <select name='IKE_ENCRYPTION' multiple='multiple' style="width:170px;">
                <option value='aes256' $checked{'IKE_ENCRYPTION'}{'aes256'}>AES (256 bit)</option>
                <option value='aes128' $checked{'IKE_ENCRYPTION'}{'aes128'}>AES (128 bit)</option>
                <option value='3des' $checked{'IKE_ENCRYPTION'}{'3des'}>3DES</option>
                <!--2013-7-20-->
                <option value='SM1' $checked{'IKE_ENCRYPTION'}{'SM1'}>SM1</option>
<!--
        <option value='twofish256' $checked{'IKE_ENCRYPTION'}{'twofish256'}>Twofish (256 bit)</option>
        <option value='twofish128' $checked{'IKE_ENCRYPTION'}{'twofish128'}>Twofish (128 bit)</option>
        <option value='serpent256' $checked{'IKE_ENCRYPTION'}{'serpent256'}>Serpent (256 bit)</option>
        <option value='serpent128' $checked{'IKE_ENCRYPTION'}{'serpent128'}>Serpent (128 bit)</option>
        <option value='blowfish256' $checked{'IKE_ENCRYPTION'}{'blowfish256'}>Blowfish (256 bit)</option>
        <option value='blowfish128' $checked{'IKE_ENCRYPTION'}{'blowfish128'}>Blowfish (128 bit)</option>
        <option value='cast128' $checked{'IKE_ENCRYPTION'}{'cast128'}>Cast (128 bit)</option>
-->
            </select>
        </td>
    </tr>
    <tr class="env">
        <td>%s</td>
        <td>
            <select name='IKE_INTEGRITY' multiple='multiple' style="width:170px;">
<!--
        <option value='sha2_512' $checked{'IKE_INTEGRITY'}{'sha2_512'}>SHA2 (512)</option>
        <option value='sha2_256' $checked{'IKE_INTEGRITY'}{'sha2_256'}>SHA2 (256)</option>
-->
                <option value='sha' $checked{'IKE_INTEGRITY'}{'sha'}>SHA</option>
                <option value='md5' $checked{'IKE_INTEGRITY'}{'md5'}>MD5</option>
            </select>
        </td>
    </tr>
    <tr class="env">
        <td>%s</td>
        <td>
            <select name='IKE_GROUPTYPE' multiple='multiple' style="width:170px;">
                <option value='8192' $checked{'IKE_GROUPTYPE'}{'8192'}>%s</option>
                <option value='6144' $checked{'IKE_GROUPTYPE'}{'6144'}>%s</option>
                <option value='4096' $checked{'IKE_GROUPTYPE'}{'4096'}>%s</option>
                <option value='3072' $checked{'IKE_GROUPTYPE'}{'3072'}>%s</option>
                <option value='2048' $checked{'IKE_GROUPTYPE'}{'2048'}>%s</option>
                <option value='1536' $checked{'IKE_GROUPTYPE'}{'1536'}>%s</option>
                <option value='1024' $checked{'IKE_GROUPTYPE'}{'1024'}>%s</option>
            </select>
        </td>
    </tr>
    <tr class="env">
        <td>%s</td>
        <td>
            <input type='text' name='IKE_LIFETIME' value='$cgiparams{'IKE_LIFETIME'}' size='5' /> %s
        </td>
    </tr>
    <tr class="odd">
        <td class="add-div-table" rowspan="3"><b>%s</b></td>
        <td>%s</td>
        <td>
            <select name='ESP_ENCRYPTION' multiple='multiple' style="width:170px;">
                <option value='aes256' $checked{'ESP_ENCRYPTION'}{'aes256'}>AES (256 bit)</option>
                <option value='aes128' $checked{'ESP_ENCRYPTION'}{'aes128'}>AES (128 bit)</option>
                <option value='3des' $checked{'ESP_ENCRYPTION'}{'3des'}>3DES</option>
<!--
        <option value='twofish256' $checked{'ESP_ENCRYPTION'}{'twofish256'}>Twofish (256 bit)</option>
        <option value='twofish128' $checked{'ESP_ENCRYPTION'}{'twofish128'}>Twofish (128 bit)</option>
        <option value='serpent256' $checked{'ESP_ENCRYPTION'}{'serpent256'}>Serpent (256 bit)</option>
        <option value='serpent128' $checked{'ESP_ENCRYPTION'}{'serpent128'}>Serpent (128 bit)</option>
        <option value='blowfish256' $checked{'ESP_ENCRYPTION'}{'blowfish256'}>Blowfish (256 bit)</option>
        <option value='blowfish128' $checked{'ESP_ENCRYPTION'}{'blowfish128'}>Blowfish (128 bit)</option>
-->
            </select>
        </td>
    </tr>
    <tr class="odd">
        <td >%s</td>

        <td>
            <select name='ESP_INTEGRITY' multiple='multiple' style="width:170px;">
<!--
                <option value='sha2_512' $checked{'ESP_INTEGRITY'}{'sha2_512'}>SHA2 (512)</option>
                <option value='sha2_256' $checked{'ESP_INTEGRITY'}{'sha2_256'}>SHA2 (256)</option>
-->
                <option value='sha1' $checked{'ESP_INTEGRITY'}{'sha1'}>SHA1</option>
                <option value='md5' $checked{'ESP_INTEGRITY'}{'md5'}>MD5</option>
            </select>
        </td>
    </tr>
    <tr class="odd">
        <td>%s</td>
        <td>
            <input type='text' name='ESP_KEYLIFE' value='$cgiparams{'ESP_KEYLIFE'}' /> %s
        </td>
    </tr>
    
    <tr class="env">
        <td class="add-div-table" rowspan="4"><b>%s</b></td>
        <td colspan='2'>
            <input type='checkbox' name='AGGRMODE' $checked{'AGGRMODE'} />%s
        </td>
    </tr>
    
    <tr class="env">
        <td colspan="2" class="need_help"><input type='checkbox' name='PFS' $checked{'PFS'} />%s $help_hash11</td>
    </tr>
    
    <tr class="env">
        <td colspan="2" class="need_help"><input type='checkbox' name='COMPRESSION' $checked{'COMPRESSION'} />%s $help_hash12</td>
    </tr>
EOF
, _('Internet Key Exchange protocol configuration')
, _('IKE encryption')
, _('IKE integrity')
, _('IKE group type')
, _('DH group %s (%s bits)', 18, 8192)
, _('DH group %s (%s bits)', 17, 6144)
, _('DH group %s (%s bits)', 16, 4096)
, _('DH group %s (%s bits)', 15, 3072)
, _('DH group %s (%s bits)', 14, 2048)
, _('DH group %s (%s bits)', 5, 1536)
, _('DH group %s (%s bits)', 2, 1024)
, _('IKE lifetime')
, _('hours')
, _('Encapsulating security payload configuration')
, _('ESP encryption')
, _('ESP integrity')
, _('ESP key life')
, _('hours')
, _('Additional options')
, _('IKE aggressive mode allowed. Avoid if possible (pre-shared key is transmitted in clear text)!')
, _('Perfect Forward Secrecy (PFS)')
, _('Negotiate payload compression')
;

    if ($confighash{$cgiparams{'KEY'}}[3] eq 'net') {
    print "<input type='hidden' name='VHOST' value='off' />";
    } elsif ($confighash{$cgiparams{'KEY'}}[10]) {
    print "<tr class='env'><td colspan='2'><input type='checkbox' name='VHOST' $checked{'VHOST'} disabled='disabled' />";
    print _('Roadwarrior virtual IP (sometimes called inner-IP)')." </td></tr>";
    } else {
    print "<tr class='env'><td colspan='2'><input type='checkbox' name='VHOST' $checked{'VHOST'} />";
    print _('Roadwarrior virtual IP (sometimes called inner-IP)')." </td></tr>";
    }
    printf  <<EOF
    <tr class='table-footer'><td colspan='3'><input type='submit' class='submitbutton net_button' name='ACTION' value='%s' />&nbsp;&nbsp;<input type='submit' class='submitbutton net_button' name='ACTION' value='%s' /></td></tr>
    </table></form>
EOF
,_('Save')
,_('Cancel')
;
    
   
    &closebox();
    &closebigbox();
    
    &closepage();
    exit(0);

    ADVANCED_END:
}

###
### Default status page
###
    %cgiparams = ();
    %cahash = ();
    %confighash = ();
    &readvpnsettings(\%vpnsettings);
    &readhasharrayOrEmpty("${swroot}/vpn/caconfig", \%cahash);
    &readhasharrayOrEmpty("${swroot}/vpn/config", \%confighash);
    $cgiparams{'CA_NAME'} = '';
    if (-e $needreload) {
        $applymessage =_("IPsec vpn rules have been changed and need to be applied in order to make the changes active !");
    }
    my @status = `sudo /usr/sbin/ipsec auto --status 2>/dev/null`;

    map ($checked{$_} = $vpnsettings{$_} eq 'on' ? "checked='checked'" : '',
    ('ENABLED','ENABLED_ORANGE','ENABLED_BLUE','DBG_CRYPT','DBG_PARSING','DBG_EMITTING','DBG_CONTROL',
     'DBG_KLIPS','DBG_DNS'));

    &showhttpheaders();
    &openpage(_('虚拟专用网络'), 1, '<script src="/include/vpnmain.js" type="text/javascript"></script>');
    
    &openbigbox($errormessage, $warnmessage, $notemessage);
    if($applymessage ne "")
    {
        &applybox($applymessage);
    }
    &openbox('100%', 'LEFT', _('Global settings'));
    my $checkbox="";
    printf <<END
    <FORM enctype='multipart/form-data' name='GLB_FORM'  METHOD='POST'>
    <TABLE WIDTH='100%'  cellpadding="0" cellspacing="0">
    <TR class="env">
    <TD CLASS='add-div-table'>%s</TD>
    <TD><INPUT TYPE='CHECKBOX' NAME='ENABLED' $checked{'ENABLED'}></TD>
    </TR>
END
,_('Enabled')
;

    if ($netsettings{'ORANGE_DEV'} ne '' && orange_used ()) {
    printf <<END
    <TR class="odd">
    <TD class="add-div-table">%s</TD>
    <TD><INPUT TYPE='CHECKBOX' NAME='ENABLED_ORANGE' $checked{'ENABLED_ORANGE'}></TD>
    </TR>
END
,
_('VPN on ORANGE');
    }

    if ($netsettings{'BLUE_DEV'} ne '' && $hotspotsettings{'HOTSPOT_ENABLED'} ne 'on' && blue_used ()) {
    printf <<END
    <TR class="odd">
    <TD class="add-div-table">%s</TD>
    <TD><INPUT TYPE='CHECKBOX' NAME='ENABLED_BLUE' $checked{'ENABLED_BLUE'}></TD>
    </TR>
END
,
_('VPN on BLUE');
    }
    printf <<END
    <tr class="env">
    <td class="add-div-table need_help">%s</td>
    <td class="need_help"><input type='text' name='VPN_OVERRIDE_MTU' maxlength="5" value="$vpnsettings{'VPN_OVERRIDE_MTU'}" /> $help_hash1</td>
    </tr>
END
,
_('Override default MTU')
;

    printf <<END
<tr class="odd hidden_class">
<td class="add-div-table" rowspan="4">%s</td>
<td><input type='checkbox' name='DBG_PARSING' $checked{'DBG_PARSING'}>&nbsp;&nbsp;%s</input></td>
</tr>
<tr class="odd hidden_class">
<td><input type='checkbox' name='DBG_EMITTING' $checked{'DBG_EMITTING'}>&nbsp;&nbsp;%s</input></td>
</tr>
<tr class="odd hidden_class">
<td><input type='checkbox' name='DBG_KLIPS' $checked{'DBG_KLIPS'}>&nbsp;&nbsp;%s</input></td>
</tr>
<tr class="odd hidden_class">
<td><input type='checkbox' name='DBG_DNS' $checked{'DBG_DNS'}>&nbsp;&nbsp;%s</input></td>
</td>
<tr class="table-footer">
<td colspan="2"><input type='submit' name='ACTION' value='%s' class="net_button" /></td>
</tr>
</table>
END
, _('Debug options')
, _('Show the structure of input messages')
, _('Show the structure of output messages')
, _("Show interaction with kernel IPsec support (KLIPS)")
, _("Show interaction with DNS")
, _('Save')
;
    print "</form>";
&closebox();


    &openbox('100%', 'LEFT', _('Connection status and control'));
     printf <<END
    <TABLE WIDTH='100%' style="margin:5px;">
    <FORM enctype='multipart/form-data' METHOD='POST'>
    <TR><TD ALIGN='left' COLSPAN='9'><INPUT class='submitbutton net_button' TYPE='SUBMIT' NAME='ACTION' VALUE='%s'></TD>
    </FORM>
    </TR></TABLE>
END
,
_('Add')
    ;
    printf <<END
    <table width='100%' border='0' cellspacing='0' class="ruleslist" cellpadding='0'>
    <TR>
    <TD WIDTH='10%' CLASS='boldbase' ALIGN='CENTER'><B>%s</B></TD>
    <TD WIDTH='20%' CLASS='boldbase' ALIGN='CENTER'><B>%s</B></TD>
    <TD WIDTH='20%' CLASS='boldbase' ALIGN='CENTER'><B>%s</B></TD>
    <TD WIDTH='25%' CLASS='boldbase' ALIGN='CENTER'><B>%s</B><BR><IMG SRC='/images/null.png' WIDTH='125' HEIGHT='1' BORDER='0'></TD>
    <TD WIDTH='10%' CLASS='boldbase' ALIGN='CENTER'><B>%s</B></TD>
    <TD WIDTH='15%' CLASS='boldbase' ALIGN='CENTER'><B>%s</B></TD>
    </TR>
END
,
_('连接名'),
_('Type'),
_('Common name'),
_('Remark'),
_('Status'),
_('Actions')

    ;
    my $id = 0;
    my $length = 0;
    foreach $key (keys %confighash) {
        $length++;
    }
    
if($length >0)
{
    #对hash排序，以保证储存的顺序的唯一性 by wl 2012.12.16
    my @keys =sort {$a <=> $b} keys %confighash;
    #foreach $key (keys %confighash) {# 以前的遍历方法 by wl 2012.12.16
    foreach $key (@keys) {
    if ($confighash{$key}[0] eq 'on') { $gif = 'on.png'; } else { $gif = 'off.png'; }

    if ($id % 2) {
        print "<TR class='env'>\n";
    } else {
        print "<TR class='odd'>\n";
    }
    print "<TD ALIGN='CENTER' NOWRAP>$confighash{$key}[1]</TD>";
        print "<TD ALIGN='CENTER' NOWRAP>" .$strings_type{$confighash{$key}[3]} . " (" . $strings_auth{$confighash{$key}[4]} . ")</TD>";
    if ($confighash{$key}[2] eq '%auth-dn') {
        print "<td align='left' nowrap='nowrap'>$confighash{$key}[9]</td>";
    } elsif ($confighash{$key}[4] eq 'cert') {
        print "<TD ALIGN='LEFT' NOWRAP>$confighash{$key}[2]</TD>";
    } else {
        print "<TD ALIGN='LEFT'>&nbsp;</TD>";
    }
    print "<TD ALIGN='CENTER'>$confighash{$key}[25]</TD>";
    my $active = "<font color='$colourred'>"._('CLOSED')."</font>";
    if ($confighash{$key}[0] eq 'off') {
        $active = "<font color='$colourred' align='center'>"._('CLOSED')."</font>";
    } else {
        foreach $line (@status) {
        if ($line =~ /$confighash{$key}[1].*IPsec SA established/) {
            $active = "<font color='$colourgreen' align='center'>"._('OPEN')."</font>";
        }
        }
    }
    printf <<END
    <TD ALIGN='CENTER'>$active</TD>
    <td><table style="width:90%;margin:0px auto;" border="0" CELLSPACING='0' CELLPADDING='0' ><tr>
    <FORM enctype='multipart/form-data'  METHOD='POST' NAME='frm${key}a'><TD ALIGN='CENTER' style="border:0px;width:13%;">
        <input class='imagebutton' type='image'  NAME='%s' src='/images/reload.png' alt='%s' title='%s' border='0'>
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <INPUT TYPE='hidden' NAME='KEY' VALUE='$key'>
    </TD></FORM>
END
,
_('Restart'),
_('Restart'),
_('Restart'),
_('Restart')

    ;
    if (($confighash{$key}[4] eq 'cert') && ($confighash{$key}[2] ne '%auth-dn')) {
        printf <<END
        <td align='center' style="border:0px;width:15%;display:none">
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='image' name='%s' src='/images/info.png' border='0' alt='%s' title='%s' />
        <input type='hidden' name='ACTION' value='%s' />
        <input type='hidden' name='KEY' value='$key' />
        </form>
        </td>
END
, _('Show certificate')
, _('Show certificate')
, _('Show certificate')
, _('Show certificate')
;
    } else {
        print "<td style='border:0px;width:15%;display:none'>&nbsp;</td>";
    }


    if ($confighash{$key}[4] eq 'cert' && -f "${swroot}/vpn/ca/certs/$confighash{$key}[1].p12") { 
        printf <<END
        <td align='center' style="border:0px;width:15%;margin-right:5px;">
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='image' name='%s' src='/images/download.png' border='0' alt='%s' title='%s' />
        <input type='hidden' name='ACTION' value='%s' />
        <input type='hidden' name='KEY' value='$key' />
        </form>
    </td>
END
, _('Download PKCS12 file')
, _('Download PKCS12 file')
, _('Download PKCS12 file')
, _('Download PKCS12 file')
;
    } elsif (($confighash{$key}[4] eq 'cert') && ($confighash{$key}[2] ne '%auth-dn')) {
        printf <<END
        <td align='center' style="border:0px;width:15%;display:none;">
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='image' name='%s' src='/images/download.png' border='0' alt='%s' title='%s' />
        <input type='hidden' name='ACTION' value='%s' />
        <input type='hidden' name='KEY' value='$key' />
        </form>
    </td>
END
, _('Download certificate')
, _('Download certificate')
, _('Download certificate')
, _('Download certificate')
;
    } else {
        print "<td style='border:0px;width:15%;display:none'>&nbsp;</td>";
    }



    printf <<END
    <FORM enctype='multipart/form-data' METHOD='POST' NAME='frm${key}d'><TD ALIGN='CENTER' style="border:0px;width:15%">
        <input class='imagebutton' type='image' NAME='%s' src='/images/$gif' alt='%s' title='%s' border='0'>
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <INPUT TYPE='hidden' NAME='KEY' VALUE='$key'>
    </TD></FORM>

    <FORM enctype='multipart/form-data' METHOD='POST' NAME='frm${key}e'><TD ALIGN='CENTER' style="border:0px;width:15%">
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <input class='imagebutton' type='image' NAME='%s' src='/images/edit.png' alt='%s' title='%s' border='0'>
        <INPUT TYPE='hidden' NAME='KEY' VALUE='$key'>
    </TD></FORM>
    <FORM enctype='multipart/form-data' METHOD='POST' NAME='frm${key}f'><TD ALIGN='CENTER' style="border:0px;width:15%">
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <input class='imagebutton' type='image'  NAME='%s' src='/images/delete.png' alt='%s' title='%s' border='0'>
        <INPUT TYPE='hidden' NAME='KEY' VALUE='$key'>
        <INPUT TYPE='hidden' NAME='del_name' VALUE='$confighash{$key}[1]'>
    </TD></FORM>
    </tr></table></td>
    </TR>
END
,
_('Enable or Disable'),
_('Enable or Disable'),
_('Enable or Disable'),
_('Enable or Disable'),
_('Edit'),
_('Edit'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
_('Remove'),
_('Remove')
;
    $id++;
    }
}else{
    no_tr(11,_('Current no content'));
}
    print "</table>";

    # If the config file contains entries, print Key to action icons
    if ($id) {
    printf <<END
    <table cellpadding="0" cellspacing="0" class="list-legend">
    <tr>
    <td><b>%s</b>
    <img src='/images/on.png' alt='%s' />
    %s
    <img src='/images/info.png' alt='%s' />
    %s
    <img src='/images/edit.png' alt='%s' />
    %s
    <img src='/images/delete.png' alt='%s' />
    %s
    <img src='/images/off.png' />
    %s
    <img src='/images/download.png' />
    %s
    <img src='/images/reload.png' />
    %s</td>
    </tr>
    </table>
    
END
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Show certificate'),
_('Show certificate'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
_('Disabled (click to enable)'),
_('Download certificate'),
_('Restart')
;
    }

    print "<br />";
    &closebox();

    &openbox('100%', 'LEFT', _('Certificate authorities'));
    print "<br />";
    printf <<EOF
    <TABLE  width='100%' border='0' cellspacing='0' class="ruleslist" cellpadding='0'>
    <TR>
    <TD WIDTH='25%' CLASS='boldbase' ALIGN='CENTER'><B>%s</B></TD>
    <TD WIDTH='65%' CLASS='boldbase' ALIGN='CENTER'><B>%s</B></TD>
    <TD WIDTH='10%' CLASS='boldbase' COLSPAN='3' ALIGN='CENTER'><B>%s</B></TD>
    </TR>
EOF
,
_('Name'),
_('Subject'),
_('Actions')
;
    if (-f "${swroot}/vpn/ca/cacerts/cacert.pem") {
    my $casubject = &cleanhtml(getsubjectfromcert ("${swroot}/vpn/ca/cacerts/cacert.pem"));
    printf <<END
    <TR class='oodd'>
    <TD >%s</TD>
    <TD >$casubject</TD>
    <td>
    <table  style="width:90%;margin:0px auto;"  BORDER='0' CELLSPACING='0' CELLPADDING='0' >
    <tr>
    <TD style="border:0px;width:30%;display:inline-block" ><FORM enctype='multipart/form-data' METHOD='POST' NAME='frm${key}a' style="display:inline-block">
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <input class='imagebutton' type='image' NAME='%s' src='/images/info.png' alt='%s' title='%s' border='0' style="display:inline-block;float:inherit">
    </FORM></TD>
    <TD style="border:0px;width:30%;display:inline-block" ><FORM enctype='multipart/form-data' METHOD='POST' NAME='frm${key}a' style="display:inline-block">
        <input class='imagebutton' type='image' NAME='%s' src='/images/download.png' alt='%s' title='%s' border='0' style="display:inline-block">
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
    </FORM></TD>
    <TD style="border:0px;" ></td>
    </tr>
    </table>
    </td>
    </TR>
END
,
_('Root certificate'),
_('Show root certificate'),
_('Edit'),
_('Show root certificate'),
_('Show root certificate'),
_('Download root certificate'),
_('Download root certificate'),
_('Download root certificate'),
_('Download root certificate')
    ;
    } else {
    # display rootcert generation buttons
    printf <<END
    <TR class='even'>
    <TD >%s</TD>
    <TD >%s</TD>
    <TD >&nbsp;</TD></TR>
END
,
_('Root certificate'),
_('<b>Not</b> present')

    ;
    }

    if (-f "${swroot}/vpn/ca/certs/hostcert.pem") {
    my $hostsubject = &cleanhtml(getsubjectfromcert ("${swroot}/vpn/ca/certs/hostcert.pem"));

    printf <<END
    <TR class='oodd'>
    <TD >%s</TD>
    <TD >$hostsubject</TD>
    <td><table style="width:90%;margin:0px auto;" BORDER='0' CELLSPACING='0' CELLPADDING='0' ><tr>
    <TD  style="border:0px;width:30%;display:inline-block"><FORM enctype='multipart/form-data' METHOD='POST' NAME='frm${key}a' style="display:inline-block">
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <input class='imagebutton' type='image' NAME='%s' src='/images/info.png' alt='%s' title='%s' border='0' style="display:inline-block;float:inherit">
    </FORM></TD>
    <TD style="border:0px;width:30%;display:inline-block"><FORM enctype='multipart/form-data' METHOD='POST' NAME='frm${key}a' style="display:inline-block">
        <input class='imagebutton' type='image' NAME='%s' src='/images/download.png' alt='%s' title='%s' border='0'>
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
    </FORM></TD>
        <td style="border:0px;"></td>
    </tr></table></td></TR>
END
,
_('Host certificate'),
_('Show host certificate'),
_('Show host certificate'),
_('Show host certificate'),
_('Show host certificate'),
_('Download host certificate'),
_('Download host certificate'),
_('Download host certificate'),
_('Download host certificate')
;
    } else {
    # Nothing
    printf <<END
    <TR class='oodd'>
    <TD WIDTH='25%' >%s</TD>
    <TD >%s</TD>
    </TD><TD COLSPAN='3'>&nbsp;</TD></TR>
END
,
_('Host certificate'),
_('<b>Not</b> present')
;
    }

    if (! -f "${swroot}/vpn/ca/cacerts/cacert.pem") {
        print "<TR class='table-footer' ><TD COLSPAN='5' ALIGN='CENTER'><FORM enctype='multipart/form-data' METHOD='POST' style='display:block;margin:0px auto;'>";
    print "<INPUT class='submitbutton net_button' TYPE='SUBMIT' NAME='ACTION' style='display:block;margin:0px auto;'  VALUE='"._('Generate root/host certificates')."'>";
        print "</FORM></TD></TR>\n";
    }

    if (keys %cahash > 0) {
    
    foreach $key (keys %cahash) {
        if (($key + 1) % 2) {
        print "<TR class='odd'>\n";
        } else {
        print "<TR class='env'>\n";
        }
        print "<TD >$cahash{$key}[0]</TD>\n";
        print "<TD >$cahash{$key}[1]</TD>\n";
        printf <<END
        <TD><table style="width:90%;margin:0px auto;" BORDER='0' CELLSPACING='0' CELLPADDING='0' ><tr>
        <FORM enctype='multipart/form-data' METHOD='POST' NAME='cafrm${key}a'><TD ALIGN='CENTER' style="border:0px;width:30%">
        <input class='imagebutton' type='image' NAME='%s' src='/images/info.png' alt='%s' title='%s' border='0'>
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <INPUT TYPE='hidden' NAME='KEY' VALUE='$key'>
        </TD></FORM>
        <FORM enctype='multipart/form-data' METHOD='POST' NAME='cafrm${key}b'><TD ALIGN='CENTER' style="border:0px;width:30%">
        <input class='imagebutton' type='image' NAME='%s' src='/images/download.png' alt='%s' title='%s' border='0'>
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <INPUT TYPE='hidden' NAME='KEY' VALUE='$key'>
        </TD></FORM>
        <FORM enctype='multipart/form-data' METHOD='POST' NAME='cafrm${key}c'><TD ALIGN='CENTER' style="border:0px;">
        <INPUT TYPE='hidden' NAME='ACTION' VALUE='%s'>
        <input class='imagebutton' type='image'  NAME='%s' src='/images/delete.png' alt='%s' title='%s' border='0'>
        <INPUT TYPE='hidden' NAME='KEY' VALUE='$key'>
        </TD></FORM></tr></table></TD></TR>
END
,
_('Show CA certificate'),
_('Show CA certificate'),
_('Show CA certificate'),
_('Show CA certificate'),
_('Download CA certificate'),
_('Download CA certificate'),
_('Download CA certificate'),
_('Download CA certificate'),
_('Remove CA certificate'),
_('Remove CA certificate'),
_('Remove CA certificate'),
_('Remove CA certificate')
;
    }
    }
print "</TABLE>";
    # If the file contains entries, print Key to action icons
    if ( -f "${swroot}/vpn/ca/cacerts/cacert.pem") {
    printf <<END
    <table class="list-legend" cellpadding="0" cellspacing="0" >
    <tr>
    <td><b>%s</b>
    <img src='/images/info.png' alt='%s' />
    %s
    <img src='/images/download.png' alt='%s' />
    %s</td>
    </tr>
    </table>
END
,
_('Legend'),
_('Show certificate'),
_('Show certificate'),
_('Download certificate'),
_('Download certificate')
;
    }

    #########5月28日临时代码修改
    printf <<END 

    <form  METHOD='POST' name="CAA_FORM" ENCTYPE='multipart/form-data' >
    <TABLE  width='100%' border='0' cellspacing='0' class="ruleslist" cellpadding='0'>
    <TR class="oodd"><TD width="20%">%s&nbsp; <INPUT TYPE='TEXT' NAME='CA_NAME' VALUE='$cgiparams{'CA_NAME'}' SIZE='15'></td>
    <td width="25%"><INPUT TYPE='FILE' NAME='FH' SIZE='32'></td>
    <td width="55%"><INPUT class='submitbutton net_button' TYPE='SUBMIT' NAME='ACTION' VALUE='%s'></TD>
    </tr>
    </TABLE>    
    </form>
END
,_('CA name')
,_('Upload CA certificate')
;
#####5月28日临时代码
 printf <<END 
    <!--2013.12.07 删除 by wl
    <form  METHOD='POST' ENCTYPE='multipart/form-data' >
    <TABLE  width='100%' border='0' cellspacing='0' class="ruleslist" cellpadding='0'>
    <tr class="oodd" width="15%"><td>CRL列表</td>
    <td width="25%"><INPUT TYPE='FILE' NAME='FH_crl' SIZE='32'></td>
    <td width="60%"><INPUT class='submitbutton net_button' TYPE='SUBMIT' VALUE='撤销'>
    <input type = "hidden" name = "ACTION" value="upload_crl" />
    </td>
    </tr>
    </table>    
    </form>
    -->
    <!--
    <form  METHOD='POST' ENCTYPE='multipart/form-data' >
    <TABLE  width='100%' border='0' cellspacing='0' class="ruleslist" cellpadding='0'>
    <tr class="oodd" width="15%"><td>PKCS12证书</td>
    <td width="25%"><INPUT TYPE='FILE' NAME='FH_pkcs12' SIZE='32'></td>
    <td width="15%"><INPUT TYPE='password' NAME='pkcs12_passwd'>证书密码</td>
    <td width="45%"><INPUT class='submitbutton net_button' TYPE='SUBMIT' VALUE='上传'>
    <input type = "hidden" name = "ACTION" value="upload_pkcs12" />
    </td>
    </tr>
    </table>    
    </form>
    -->
END
;    

###结束
    printf <<END
    <br />
    <table class="data_table">
    <tr class="table-footer"><td>
    <FORM enctype='multipart/form-data' METHOD='POST' onsubmit="return confirm('%s');">
    <INPUT TYPE='hidden' NAME='ACTION' VALUE='reset'>
    <INPUT class='submitbutton net_button' TYPE='SUBMIT' NAME='ACTIONSUBMIT' VALUE='%s'>
   </FORM>
    </td></tr>
    </table>
END
, _('Resetting the VPN configuration will remove the root CA, the host certificate and all certificate based connections')
, _('Reset')
, _('This feature has been sponsored by')
;
    &closebigbox();
    system("fmodify /var/efw/vpn/");
    &check_form_home();
    &closepage();

