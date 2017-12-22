#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
# (c) Endian GmbH/srl
#
# Copyright (C) 01-02-2002 Graham Smith <grhm@grhm.co.uk>
#              - Fixed DHCP Leases added
#
# $Id: dhcp.cgi,v 1.14.2.24 2004/11/29 10:49:16 eoberlander Exp $
#
#  Franck    -rewrite for two or more interface
#  nov/2004    -check range is in correct subnet
#        -add NTP option
#        -add display sorting of actives leases
#
# to do : choose a correct format for displaying dates
#
require '/var/efw/header.pl';
use Net::IPv4Addr qw (:all);
use HTML::Entities;

my %dhcpsettings;
my %netsettings;
my %hostsettings;
my %hotspotsettings;
my $filename = "${swroot}/dhcp/fixleases";

my $conffile    = "${swroot}/dhcp/settings";
my $conffile_default = "${swroot}/dhcp/default/settings";
my $restart     = '/usr/local/bin/restartdhcp';

my %enable_file = ();
$enable_file{'GREEN'}  = "${swroot}/dhcp/enable_green";
$enable_file{'BLUE'}   = "${swroot}/dhcp/enable_blue";
$enable_file{'ORANGE'} = "${swroot}/dhcp/enable_orange";

my $ntp_enable_file = "${swroot}/time/enable";

my $custom_global = "";
my $custom_global_file="${swroot}/dhcp/custom.tpl";
my $errormessage = "";
my $notemessage  = "";
my %enable = ();
$enable{'GREEN'} = 0;
if (-e $enable_file{'GREEN'}) {
  $enable{'GREEN'} = 1;
}
$enable{'BLUE'} = 0;
if (-e $enable_file{'BLUE'}) {
  $enable{'BLUE'} = 1;
}
$enable{'ORANGE'} = 0;
if (-e $enable_file{'ORANGE'}) {
  $enable{'ORANGE'} = 1;
}

$ntp_enable = 0;
if (-e $ntp_enable_file) {
  $ntp_enable = 1;
}

sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'DHCP_FORM',
       'option'   :{
                    'START_ADDR_GREEN':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                               'ass_check':function(eve){
                                                            var msg = "";
                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                            var ip_end = eve._getCURElementsByName("END_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                            var ip_segment = ip_start + "-"  + ip_end;
                                                            if(!eve.rangeip(ip_segment)){
                                                                msg = "与结束地址不匹配";
                                                            }
                                                            else if(!eve.green_ip){
                                                                 \$.ajax({
                                                                    type : "get",
                                                                    url : '/cgi-bin/chinark_back_get.cgi',
                                                                    async : false,
                                                                    data : 'path=/var/efw/ethernet/settings',
                                                                    success : function(data){
                                                                        eve.green_ip = data;                                                                        
                                                                    }
                                                                    });
                                                            }
                                                            var exist = eve.green_ip.split('\\n');
                                                            var green,orange;
                                                            for (var i = 0; i < exist.length; i++) {
                                                                var tmp = exist[i].split('=');
                                                                if(tmp[0] == "GREEN_IPS"){
                                                                  green = tmp[1];
                                                                }
                                                            }
                                                            if(!eve.same_green(ip_start,green)){
                                                                 msg = '必须与%s接口同网段';
                                                            }
                                                            return msg;
                                                     }
                             },
                    'END_ADDR_GREEN':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                               'ass_check':function(eve){
                                                            var msg = "";
                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                            var ip_end = eve._getCURElementsByName("END_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                            var ip_segment = ip_start + "-" + ip_end;
                                                            if(!eve.rangeip(ip_segment)){
                                                                msg = "与起始地址不匹配";
                                                            }
                                                           else if(!eve.green_ip){
                                                                 \$.ajax({
                                                                    type : "get",
                                                                    url : '/cgi-bin/chinark_back_get.cgi',
                                                                    async : false,
                                                                    data : 'path=/var/efw/ethernet/settings',
                                                                    success : function(data){
                                                                        eve.green_ip = data;                                                                        
                                                                    }
                                                                    });
                                                            }
                                                            var exist = eve.green_ip.split('\\n');
                                                            var green,orange;
                                                            for (var i = 0; i < exist.length; i++) {
                                                                var tmp = exist[i].split('=');
                                                                if(tmp[0] == "GREEN_IPS"){
                                                                  green = tmp[1];
                                                                }
                                                            }
                                                            if(!eve.same_green(ip_end,green)){
                                                                 msg = '必须与%s接口同网段';
                                                            }
                                                            return msg;
                                                     }
                             },
                    'DEFAULT_LEASE_TIME_GREEN':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                           var msg = "";
                                                           var defaults = eve._getCURElementsByName("DEFAULT_LEASE_TIME_GREEN","input","DHCP_FORM")[0].value;                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                           var max = eve._getCURElementsByName("MAX_LEASE_TIME_GREEN","input","DHCP_FORM")[0].value;
                                                           defaults = parseInt(defaults);
                                                           max = parseInt(max);
                                                           if (defaults > max  ){
                                                                msg = "默认租约不能大于最大租约"
                                                           }
                                                           return msg;
                                                     }
                             },
                    'MAX_LEASE_TIME_GREEN':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                           var msg = "";
                                                           var defaults = eve._getCURElementsByName("DEFAULT_LEASE_TIME_GREEN","input","DHCP_FORM")[0].value;                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                           var max = eve._getCURElementsByName("MAX_LEASE_TIME_GREEN","input","DHCP_FORM")[0].value;
                                                           defaults = parseInt(defaults);
                                                           max = parseInt(max);
                                                           if (defaults > max  ){
                                                                msg = "最大租约不能小于默认租约"
                                                           }
                                                           return msg;
                                                     }
                             },
                    'DOMAIN_NAME_GREEN':{
                               'type':'text',
                               'required':'1',
                               'check':'name|'
                             },
                    'GATEWAY_GREEN':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'DNS1_GREEN':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|'
                             },
                    'DNS2_GREEN':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|'
                             },
                    'NTP1_GREEN':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|'
                             },
                    'NTP2_GREEN':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|'
                             },
                    'WINS1_GREEN':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|'
                             },
                    'WINS2_GREEN':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|'
                             },
                    'START_ADDR_ORANGE':{
                               'type':'text',
                               'required':'1',
                               'ajax':'1',
                               'check':'ip|',
                               'ass_check':function(eve){
                                                            var msg = "";
                                                            var ip_start_o = eve._getCURElementsByName("START_ADDR_ORANGE","input","DHCP_FORM")[0].value;                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                            var ip_end_o = eve._getCURElementsByName("END_ADDR_ORANGE","input","DHCP_FORM")[0].value;
                                                            var ip_segment = ip_start_o + "-" + ip_end_o;
                                                            if(!eve.rangeip(ip_segment)){
                                                                msg = "与结束地址不匹配";
                                                            }
                                                            else if(!eve.orange_ip){
                                                                 \$.ajax({
                                                                    type : "get",
                                                                    url : '/cgi-bin/chinark_back_get.cgi',
                                                                    async : false,
                                                                    data : 'path=/var/efw/ethernet/settings',
                                                                    success : function(data){
                                                                        eve.orange_ip = data;                                                                        
                                                                    }
                                                                    });
                                                            }
                                                            var exist = eve.orange_ip.split('\\n');
                                                            var green,orange;
                                                            for (var i = 0; i < exist.length; i++) {
                                                                var tmp = exist[i].split('=');
                                                                if(tmp[0] == "ORANGE_IPS"){
                                                                  orange = tmp[1];
                                                                }
                                                            }
                                                            if(!eve.same_orange(ip_start_o,orange)){
                                                                 msg = '必须与%s接口同网段';
                                                            }
                                                            return msg;
                                                     }
                             },
                    'END_ADDR_ORANGE':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                               'ass_check':function(eve){
                                                            var msg = "";
                                                            var ip_start_o = eve._getCURElementsByName("START_ADDR_ORANGE","input","DHCP_FORM")[0].value;                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                            var ip_end_o = eve._getCURElementsByName("END_ADDR_ORANGE","input","DHCP_FORM")[0].value;
                                                            var ip_segment = ip_start_o + "-" +　ip_end_o;
                                                            if(!eve.rangeip(ip_segment)){
                                                                msg = "与起始地址不匹配";
                                                            }
                                                            else if(!eve.orange_ip){
                                                                 \$.ajax({
                                                                    type : "get",
                                                                    url : '/cgi-bin/chinark_back_get.cgi',
                                                                    async : false,
                                                                    data : 'path=/var/efw/ethernet/settings',
                                                                    success : function(data){
                                                                        eve.orange_ip = data;                                                                        
                                                                    }
                                                                    });
                                                            }
                                                            var exist = eve.orange_ip.split('\\n');
                                                            var green,orange;
                                                            for (var i = 0; i < exist.length; i++) {
                                                                var tmp = exist[i].split('=');
                                                                if(tmp[0] == "ORANGE_IPS"){
                                                                  orange = tmp[1];
                                                                }
                                                            }
                                                            if(!eve.same_orange(ip_end_o,orange)){
                                                                 msg = '必须与%s接口同网段';
                                                            }
                                                            return msg;
                                                     }
                             },
                    'DEFAULT_LEASE_TIME_ORANGE':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                            var msg = "";
                                                            var defaults = eve._getCURElementsByName("DEFAULT_LEASE_TIME_ORANGE","input","DHCP_FORM")[0].value;                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                            var max = eve._getCURElementsByName("MAX_LEASE_TIME_ORANGE","input","DHCP_FORM")[0].value;
                                                            defaults = parseInt(defaults);
                                                            max = parseInt(max);
                                                            if (defaults > max  ){
                                                                 msg = "默认租约不能大于最大租约"
                                                            }
                                                            return msg;
                                                     }
                             },
                    'MAX_LEASE_TIME_ORANGE':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                            var msg = "";
                                                            var defaults = eve._getCURElementsByName("DEFAULT_LEASE_TIME_ORANGE","input","DHCP_FORM")[0].value;                                                            var ip_start = eve._getCURElementsByName("START_ADDR_GREEN","input","DHCP_FORM")[0].value;
                                                            var max = eve._getCURElementsByName("MAX_LEASE_TIME_ORANGE","input","DHCP_FORM")[0].value;
                                                            defaults = parseInt(defaults);
                                                            max = parseInt(max);
                                                            if (defaults > max  ){
                                                                 msg = "最大租约不能小于默认租约"
                                                            }
                                                            return msg;
                                                     }
                             },
                    'DOMAIN_NAME_ORANGE':{
                               'type':'text',
                               'required':'1',
                               'check':'name|'
                             },
                    'GATEWAY_ORANGE':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'DNS1_ORANGE':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|'
                             },
                    'DNS2_ORANGE':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|'
                             },
                    'NTP1_ORANGE':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|'
                             },
                    'NTP2_ORANGE':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|'
                             },
                    'WINS1_ORANGE':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|'
                             },
                    'WINS2_ORANGE':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|'
                             }
                 }
         };
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("DHCP_FORM");
    </script>
EOF
,_('GREEN')
,_('GREEN')
,_('ORANGE')
,_('ORANGE')
;
}
sub toggle_files($$) {
    my $file = shift;
    my $set = shift;
    if ($set) {
		`touch $file`;
		`sudo fmodify $file`;
		return 1;
    }
    if (-e $file) {
		unlink($file);
		`sudo fdelete $file`;
    }
    return 0;
}

sub read_file($) {
    my $f = shift;
    open(F, $f) || return "";
    my @lines = <F>;
    close(F);
    return join("", @lines);
}

sub write_file($$) {
    my $f = shift;
    my $data = shift;
    open(F, ">$f") || return;
    print F $data;
    close(F);
}

sub ip2long {
    return unpack("l*", pack("l*", unpack("N*", inet_aton(shift))));
}

sub read_dhcp_conf() {

    if (-e $conffile_default) {
    readhash($conffile_default, \%dhcpsettings);
    }
    if (-e $conffile) {
    readhash($conffile, \%dhcpsettings);
    }
    $custom_global = read_file($custom_global_file);
}

&showhttpheaders();
@ITFs=('GREEN');

if (orange_used()) {
    push(@ITFs, 'ORANGE');
}
if (blue_used()) {
    push(@ITFs, 'BLUE');
}

my %interface_title = (
    'GREEN' => _('Green interface'),
    'ORANGE' => _('Orange interface'),
    'BLUE' => _('Blue interface')
);
####help_msg
my @help_hash="";
for (my $i=0;$i<43 ;$i++) {
	my $num = $i+1;
	$help_hash[$i] = read_json("/home/httpd/help/dhcp_help.json","dhcp.cgi","mark".$num,"-10","30","down");
}
##
my %elvishash=(
	"GREEN" => _('GREEN')."区域",
	"ORANGE" => _('ORANGE')."区域",
	"BLUE" => _('BLUE')."区域",
);
# dependent interface variable
foreach $itf (@ITFs) {
  $dhcpsettings{"ENABLE_${itf}"} = '';
  $dhcpsettings{"START_ADDR_${itf}"} = '';
  $dhcpsettings{"END_ADDR_${itf}"} = '';
  $dhcpsettings{"ONLY_FIXEDLEASE_${itf}"} = '';
  $dhcpsettings{"DOMAIN_NAME_${itf}"} = '';
  $dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} = '';
  $dhcpsettings{"MAX_LEASE_TIME_${itf}"} = '';
  $dhcpsettings{"GATEWAY_${itf}"} = '';
  $dhcpsettings{"WINS1_${itf}"} = '';
  $dhcpsettings{"WINS2_${itf}"} = '';
  $dhcpsettings{"DNS1_${itf}"} = '';
  $dhcpsettings{"DNS2_${itf}"} = '';
  $dhcpsettings{"NTP1_${itf}"} = '';
  $dhcpsettings{"NTP2_${itf}"} = '';
}

$dhcpsettings{'FIX_MAC'} = '';
$dhcpsettings{'FIX_ADDR'} = '';
$dhcpsettings{'ENABLED'} = 'on';
$dhcpsettings{'FIX_NEXTADDR'} = '';
$dhcpsettings{'FIX_FILENAME'} = '';
$dhcpsettings{'FIX_ROOTPATH'} = '';
$dhcpsettings{'FIX_DESCRIPTION'} = '';

&getcgihash(\%dhcpsettings);

my @current = ();
if ( -e $filename) {
    open(FILE, "$filename") or die 'Unable to open fixed leases file.';
    @current = <FILE>;
    close(FILE);
}

&readhash("${swroot}/ethernet/settings", \%netsettings);
&readhash("${swroot}/host/settings", \%hostsettings);

if (-e "/usr/lib/efw/hotspot/default/settings") {
    &readhash("/usr/lib/efw/hotspot/default/settings", \%hotspotsettings);
}
if (-e "${swroot}/hotspot/settings") {
    &readhash("${swroot}/hotspot/settings", \%hotspotsettings);
}

foreach $itf (@ITFs) {
    if ($netsettings{"${itf}_NETADDRESS"} ne "" and $netsettings{"${itf}_NETMASK"} ne "") {
        my $netaddress = $netsettings{"${itf}_NETADDRESS"};
        my $fwaddress = $netsettings{"${itf}_ADDRESS"};
        my $broadcastaddress = ipv4_broadcast($netsettings{"${itf}_NETADDRESS"}, $netsettings{"${itf}_NETMASK"});
        my @ip = split(/\./, $fwaddress);
        my @net = split(/\./, $netaddress);
        my @broadcast = split(/\./, $broadcastaddress);
        if (@ip[3] eq @broadcast[3] - 1) {
            if ($dhcpsettings{"START_ADDR_${itf}"} eq "") {
                $dhcpsettings{"START_ADDR_${itf}"} = @net[0].".".@net[1].".".@net[2].".".(@net[3] + 1);
            }
            if ($dhcpsettings{"END_ADDR_${itf}"} eq "") {
                $dhcpsettings{"END_ADDR_${itf}"} = @ip[0].".".@ip[1].".".@ip[2].".".(@ip[3] - 1);
            }
        }
        else {
            if ($dhcpsettings{"START_ADDR_${itf}"} eq "") {
                $dhcpsettings{"START_ADDR_${itf}"} = @ip[0].".".@ip[1].".".@ip[2].".".(@ip[3] + 1);
            }
            if ($dhcpsettings{"END_ADDR_${itf}"} eq "") {
                $dhcpsettings{"END_ADDR_${itf}"} = @broadcast[0].".".@broadcast[1].".".@broadcast[2].".".(@broadcast[3] - 1);
            }
        }
    }
}

my @errormessages = ();
if ($dhcpsettings{'ACTION'} eq 'save')
{
  foreach $itf (@ITFs) {
      if ($dhcpsettings{"ENABLE_${itf}"} ne $enable{$itf}) {
          $enable{$itf} = &toggle_files($enable_file{$itf}, $dhcpsettings{"ENABLE_${itf}"});
      }
      if ($enable{$itf} || !$enable{$itf}) {
        # "Start" is defined, need "End" and vice versa
        if ($dhcpsettings{"START_ADDR_${itf}"}) {
            if (!(&validip($dhcpsettings{"START_ADDR_${itf}"}))) {
                $errormessage = _('DHCP on %s: invalid start address.', $itf);
                goto ERROR;
            }
            if (!$dhcpsettings{"END_ADDR_${itf}"}) {
                $errormessage = _('DHCP on %s: invalid end address.', $itf);
                goto ERROR;
            }
            if (! &IpInSubnet ( $dhcpsettings{"START_ADDR_${itf}"}, 
                                $netsettings{"${itf}_NETADDRESS"},
                                $netsettings{"${itf}_NETMASK"})) {
                $errormessage = _('DHCP on %s: invalid start address.', $itf);
                goto ERROR;
            }
        }
        if ($dhcpsettings{"END_ADDR_${itf}"}) {
            if (!(&validip($dhcpsettings{"END_ADDR_${itf}"}))) {
                $errormessage = _('DHCP on %s: invalid end address.', $itf);
                goto ERROR;
            }
            if (!$dhcpsettings{"START_ADDR_${itf}"}) {
                $errormessage = _('DHCP on %s: invalid start address.', $itf);
                goto ERROR;
            }
            if (! &IpInSubnet ( $dhcpsettings{"END_ADDR_${itf}"}, 
                                $netsettings{"${itf}_NETADDRESS"},
                                $netsettings{"${itf}_NETMASK"})) { 
                $errormessage = _('DHCP on %s: invalid end address.', $itf);
                goto ERROR;
            }
            #swap if necessary!
            if (ip2long($dhcpsettings{"START_ADDR_${itf}"})  >= ip2long($dhcpsettings{"END_ADDR_${itf}"})) {
                my $tmp = $dhcpsettings{"START_ADDR_${itf}"};
                $dhcpsettings{"START_ADDR_${itf}"} = $dhcpsettings{"END_ADDR_${itf}"};
                $dhcpsettings{"END_ADDR_${itf}"} = $tmp;
            }
        }
        if (ip2long($dhcpsettings{"START_ADDR_${itf}"})  >= ip2long($dhcpsettings{"END_ADDR_${itf}"})) {
            $errormessage = _('DHCP on %s: Pool start address must be lesser than end address!', $itf);
            goto ERROR;
        }
        if ($dhcpsettings{"START_ADDR_${itf}"} eq $netsettings{"${itf}_NETADDRESS"}) {
            $errormessage = _('DHCP on %s: invalid start address', $itf);
            goto ERROR;
        }
        if ($dhcpsettings{"END_ADDR_${itf}"} eq ipv4_broadcast($netsettings{"${itf}_NETADDRESS"}, $netsettings{"${itf}_NETMASK"})) {
            $errormessage = _('DHCP on %s: invalid end address', $itf);
            goto ERROR;
        }
    
    if (!($dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} =~ /^\d+$/))
    {
        $errormessage = _('DHCP on %s: invalid default lease time: %s.', $itf, $dhcpsettings{'DEFAULT_LEASE_TIME_${itf}'});
        goto ERROR;
    }
	if ($dhcpsettings{"DOMAIN_NAME_${itf}"} !~ /^[A-Za-z0-9_]+$/)
    {
        $errormessage = $itf."上".$dhcpsettings{"DOMAIN_NAME_${itf}"}."为不合法域名后缀.";
        goto ERROR;
    }
    if (!($dhcpsettings{"MAX_LEASE_TIME_${itf}"} =~ /^\d+$/))
    {
        $errormessage = _('DHCP on %s: invalid default lease time: %s.', $itf, $dhcpsettings{'DEFAULT_LEASE_TIME_${itf}'});
        $errormessage = _('DHCP on %s: invalid max lease time: %s', $itf, $dhcpsettings{'MAX_LEASE_TIME_${itf}'});
        goto ERROR;
    }

    if ($dhcpsettings{"GATEWAY_${itf}"})
    {
        if (!(&validip($dhcpsettings{"GATEWAY_${itf}"})))
        {
            $errormessage = _('DHCP on %s: invalid gateway %s.', $itf, $dhcpsettings{"GATEWAY_${itf}"});
            goto ERROR;
        }
    }
	if (!$dhcpsettings{"GATEWAY_${itf}"}) {
		$errormessage = "$elvishash{$itf}默认网关不能为空!";
        goto ERROR;
	}


    if ($dhcpsettings{"DNS1_${itf}"})
    {
        if (!(&validip($dhcpsettings{"DNS1_${itf}"})))
        {
            $errormessage = _('DHCP on %s: invalid primary DNS.', $itf);
            goto ERROR;
        }
    }
    if ($dhcpsettings{"DNS2_${itf}"})
    {
        if (!(&validip($dhcpsettings{"DNS2_${itf}"})))
        {
            $errormessage = _('DHCP on %s: invalid secondary DNS.', $itf);
            goto ERROR;
        }
            if (! $dhcpsettings{"DNS1_${itf}"})
            {
            $errormessage = _('DHCP on %s: cannot specify secondary DNS without specifying primary.', $itf); 
            goto ERROR;
            }
    }

    if ($dhcpsettings{"WINS1_${itf}"})
    {
        if (!(&validip($dhcpsettings{"WINS1_${itf}"})))
        {
            $errormessage = _('DHCP on %s: invalid WINS server address.', $itf);
            goto ERROR;
        }
    }
    if ($dhcpsettings{"WINS2_${itf}"})
    {
        if (!(&validip($dhcpsettings{"WINS2_${itf}"})))
        {
            $errormessage = _('DHCP on %s: invalid WINS server address.', $itf);
            goto ERROR;
        }
        if (! $dhcpsettings{"WINS1_${itf}"} ) {
            $errormessage = _('DHCP on %s: cannot specify secondary WINS without specifying primary.', $itf);
            goto ERROR;
        }        
    }

     if ($dhcpsettings{"NTP1_${itf}"})
     {
         if (!(&validip($dhcpsettings{"NTP1_${itf}"})))
         {
             $errormessage = _('DHCP on %s: invalid primary NTP server address', $itf);
             goto ERROR;
         }
         if ($dhcpsettings{"NTP1_${itf}"} eq $netsettings{"${itf}_ADDRESS"} && (! $ntp_enable))
         {
             $warnNTPmessage = _('DHCP on %s: local NTP server specified but not enabled', $itf);
             #goto ERROR;
         }
     }
     if ($dhcpsettings{"NTP2_${itf}"})
     {
         if (!(&validip($dhcpsettings{"NTP2_${itf}"})))
         {
             $errormessage = _('DHCP on %s: invalid secondary NTP server address', $itf);
             goto ERROR;
         }
         if ($dhcpsettings{"NTP2_${itf}"} eq $netsettings{"${itf}_ADDRESS"} && (! $ntp_enable))
         {
             $warnNTPmessage = _('DHCP on %s: local NTP server specified but not enabled', $itf);
             #goto ERROR;
         }
         if (! $dhcpsettings{"NTP1_${itf}"})
         {
             $errormessage = _('DHCP on %s: Cannot specify Secondary NTP server without specifying Primary', $itf);
             goto ERROR;
         }
     }
      } # enabled
    }#loop interface verify
	if($errormessage eq "")
	{
		$notemessage = _("DHCP服务器已经成功修改");
	}
    $dhcpsettings{'CUSTOM_GLOBAL'} =~ s/\r//;
    decode_entities($dhcpsettings{'CUSTOM_GLOBAL'});
    write_file($custom_global_file, $dhcpsettings{'CUSTOM_GLOBAL'});
	`sudo fmodify $custom_global_file`;
    $custom_global=$dhcpsettings{'CUSTOM_GLOBAL'};
    $dhcpsettings{'CUSTOM_GLOBAL'} = unset;
    &writehash("${swroot}/dhcp/settings", \%dhcpsettings);
	`sudo fmodify "${swroot}/dhcp/settings"`;
	###
=p
	my %temp;
	readhash("${swroot}/dhcp/settings",\%temp);
	foreach $itf (@ITFs) {
		if ($temp{"ENABLED_$itf"} eq "on") {
			`touch "${swroot}/dhcp/enable_"`
		}
	}
=cut
	###
    &buildconf;
ERROR:
}

#Sorting of fixed leases
if ($ENV{'QUERY_STRING'} =~ /^FETHER|^FIPADDR/ ) {
    my $newsort=$ENV{'QUERY_STRING'};
    read_dhcp_conf();
    $act=$dhcpsettings{'SORT_FLEASELIST'};
    #Reverse actual ?
    if ($act =~ $newsort) {
        if ($act !~ 'Rev') {$Rev='Rev'};
        $newsort.=$Rev
    };

    $dhcpsettings{'SORT_FLEASELIST'}=$newsort;
    &writehash("${swroot}/dhcp/settings", \%dhcpsettings);
	`sudo fmodify "${swroot}/dhcp/settings"`;
    &sortcurrent;
    $dhcpsettings{'ACTION'} = 'SORT';  # avoid the next test "First lauch"
}

#Sorting of allocated leases
&CheckSortOrder;

if ($dhcpsettings{'ACTION'} eq '' ) { # First launch

    read_dhcp_conf();
	foreach $itf (@ITFs) { 
	 	    if ($dhcpsettings{"ENABLE_${itf}"} ne 'on' ) 
	 	    { 
	 	            if (!($dhcpsettings{"DNS1_${itf}"})) { $dhcpsettings{"DNS1_${itf}"} = $netsettings{"${itf}_ADDRESS"} }; 
	 	        #$dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} = '60'; 
	 	        #$dhcpsettings{"MAX_LEASE_TIME_${itf}"} = '120'; 
	 	        $dhcpsettings{"GATEWAY_${itf}"} = $netsettings{"${itf}_ADDRESS"}; 
	 	        $dhcpsettings{"DOMAIN_NAME_${itf}"} = $hostsettings{'DOMAINNAME'}; 
	 	    } 
	 	    } 
    
}

&openpage(_('DHCP configuration'), 1, '');

&openbigbox($errormessage, $warnmessage, $notemessage);
if ($warnNTPmessage)
{
    $warnNTPmessage = "<td>$warnNTPmessage</td>";
}

printf <<EOF

<form name="DHCP_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='save' >
EOF
;

my $j=0;##判断是哪个接口
my $key = 0;
my $open = "";
foreach $itf (@ITFs) {
	if($key eq 0)
	{
		$open = "open";
	}else{
		$open = "";
	}
	$key++;
    my %checked;
	my $k = 14*$j;
    $checked{'ENABLE'}{0} = '';
    $checked{'ENABLE'}{1} = '';
    $checked{'ENABLE'}{$enable{$itf}} = "checked='checked'";

    $checked{'ONLY_FIXEDLEASE'}{'off'} = '';
    $checked{'ONLY_FIXEDLEASE'}{'on'} = '';
    $checked{'ONLY_FIXEDLEASE'}{$dhcpsettings{"ONLY_FIXEDLEASE_${itf}"}} = "checked='checked'";

    if ($netsettings{"${itf}_DEV"} ne '' ) { # Show only defined interface

		
		#&openbox('100%', 'left', 'DHCP  '.$interface_title{$itf});
		# my $start = get_folding("CUSTOMLIST", "start", 'DHCP  '.$interface_title{$itf},$open);
    openeditorbox('DHCP  '.$interface_title{$itf}, _("Add a fixed lease"), ($dhcpsettings{'ACTION'} eq 'edit' || scalar(@errormessages) > 0 ? "showeditor" : ""), "fixedleases", );
		# print $start;
        my $lc_itf=lc($itf);
        
        if ($itf eq "BLUE" && $hotspotsettings{'HOTSPOT_ENABLED'} eq "on") { # check if hotspot is enabled on blue
            printf <<END
<table cellpadding="0" cellspacing="0" border="0">
<tr>
    <td width='25%' class='boldadd-div-width'><b><font color="$colour${lc_itf}">%s</font></b></td>
    <td width="75%"class='add-div-width'>%s</td>
</tr>
</table>
END
            ,
            $interface_title{$itf},
            _("DHCP configuration is managed by hotspot")
            ;
        }
        else {        
            printf <<END
<table cellpadding="0" cellspacing="0" border="0" style="border-left:1px solid #999;">
<tr class="env">
	<td style='width:150px;' class="add-div-width need_help">%s </td>
    <td class="need_help"><input type='checkbox' name='ENABLE_${itf}' $checked{'ENABLE'}{1} >$help_hash[$k]</td>
    <td class='add-div-width need_help'>%s </td>
    <td class="need_help"><input type='checkbox' name='ONLY_FIXEDLEASE_${itf}' value='on' $checked{'ONLY_FIXEDLEASE'}{'on'} >$help_hash[$k+1]</td>
</tr>
<tr class="odd">
    <td width='15%' class='add-div-width need_help'>%s * </td>
    <td width='30%' class="need_help"><input type='text' name='START_ADDR_${itf}' value='$dhcpsettings{"START_ADDR_${itf}"}' >$help_hash[$k+2]</td>
    <td width='15%' class='add-div-width need_help'>%s * $help_hash[$k+3]</td>
    <td width='40%' class="need_help"><input type='text' name='END_ADDR_${itf}' value='$dhcpsettings{"END_ADDR_${itf}"}' >$help_hash[$k+3]</td>
</tr>
<tr class="env">
    <td class='add-div-width need_help'>%s *</td>
    <td class="need_help"><input type='text' maxlength="4" name='DEFAULT_LEASE_TIME_${itf}' value='$dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"}' >$help_hash[$k+4]</td>
    <td class='add-div-width need_help'>%s *</td>
    <td class="need_help"><input type='text' maxlength="5" name='MAX_LEASE_TIME_${itf}' value='$dhcpsettings{"MAX_LEASE_TIME_${itf}"}' >$help_hash[$k+5]</td>
</tr>
<tr class="odd">
    <td class='add-div-width need_help'>%s </td>
    <td class="need_help"><input type='text' name='DOMAIN_NAME_${itf}' value='$dhcpsettings{"DOMAIN_NAME_${itf}"}' >$help_hash[$k+6]</td>
    <td class='add-div-width need_help'>%s *</td>
    <td class="need_help"><input type='text' name='GATEWAY_${itf}' value='$dhcpsettings{"GATEWAY_${itf}"}' >$help_hash[$k+7]</td>
</tr>
<tr class="env">
    <td class='add-div-width need_help'>%s</td>
    <td class="need_help"><input type='text' name='DNS1_${itf}' value='$dhcpsettings{"DNS1_${itf}"}' >$help_hash[$k+8]</td>
    <td class='add-div-width need_help'>%s</td>
    <td class="need_help"><input type='text' name='DNS2_${itf}' value='$dhcpsettings{"DNS2_${itf}"}' >$help_hash[$k+9]</td>
</tr>
<tr class="odd">
     <td class='add-div-width need_help'>%s</td>
     <td class="need_help"><input type='text' name='NTP1_${itf}' value='$dhcpsettings{"NTP1_${itf}"}' >$help_hash[$k+10]</td>
     <td class='add-div-width need_help'>%s</td>
     <td class="need_help"><input type='text' name='NTP2_${itf}' value='$dhcpsettings{"NTP2_${itf}"}' >$help_hash[$k+11]</td>
</tr>
<tr class="env">
    <td class='add-div-width need_help'>%s</td>
    <td class="need_help"><input type='text' name='WINS1_${itf}' value='$dhcpsettings{"WINS1_${itf}"}' >$help_hash[$k+12]</td>
    <td class='add-div-width need_help'>%s</td>
    <td class="need_help"><input type='text' name='WINS2_${itf}' value='$dhcpsettings{"WINS2_${itf}"}' >$help_hash[$k+13]</td>
</tr>
</table>
END
            ,
			_('Enabled'),
            _('Allow only fixed leases'),
            _('Start address'),
            _('End address'),
            _('Default lease time (min)'),
            _('Max lease time (min)'),
            _('Domain name suffix'),
            _('Default Gateway'),
            _('Primary DNS'),
            _('Secondary DNS'),
            _('Primary NTP server'),
            _('Secondary NTP server'),
            _('Primary WINS server address'),
            _('Secondary WINS server address'),
            ;
            #print get_folding("folding_$itf");
        }
		#closebox();
		my $end_str = get_folding();
		print $end_str;
    }# Show only defined interface	
	$j++;
}#foreach itf
printf <<END  
   <table cellpadding="0" cellspacing="0" border="0" style="width: 96.2%;margin: -20px auto;">
   <tr class="table-footer">
	<td>
		<input class='submitbutton net_button' type='submit' name='submit' value='%s' >
	</td>
	</tr>
   </table>
   <script>
     \$('#add-div-content').show();
   </script>
END
,_('Save')
;
# &closeeditorbox($buttontext, _("Cancel"), "leasebutton", "fixedleases",$ENV{'SCRIPT_NAME'});
print "</form>";
&closebigbox();
print "<br /><br /><br /><br />";  
check_form()
&closepage();

# Build the configuration file mixing  settings and lease
sub buildconf {
    system '/usr/local/bin/restartdhcp --force';
}


