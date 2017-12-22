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

use eSession;
use eReadconf;
use Net::IPv4Addr qw (:all);
require '/var/efw/header.pl';
&validateUser();

##############################################################################
# part 1:  code common for all steps
##############################################################################

require 'header.pl' if (-e 'header.pl');  # if called from ipcop, header-pl is
                                          # already included.

require '/home/httpd/cgi-bin/netwizard_tools.pl';
require '/home/httpd/cgi-bin/ifacetools.pl';
require '/home/httpd/cgi-bin/ethconfig.pl';
require '/home/httpd/cgi-bin/redtools.pl';
require '/home/httpd/cgi-bin/strings.pl';

my %par;
getcgihash(\%par);

#
# definitions
#

my %steps = ( 
				1 => _('选择主上行接口类型'),
				2 => _('Choose network zones'),
				3 => _('Network preferences'),
				4 => _('Internet access preferences'),
				5 => _('configure DNS resolver'),
				6 => _('Configure default admin mail'),
				7 => _('Apply configuration'),
				8 => _('配置完成')
            );
my $stepnum = scalar(keys(%steps));
my $reload = '';

my $lever = '';

my %tpl_ph_hash = ();
my $tpl_ph = \%tpl_ph_hash;
my %session_hash = ();
my $session = \%session_hash;
my %settings_hash = ();
my $settings = \%settings_hash;
my $session_id;
my $if_available = 0;

my %live_data_hash = ();
my $live_data = \%live_data_hash;

my $ethernet_settings_default = 'ethernet/default/settings';
my $ethernet_settings = 'ethernet/settings';
my $main_settings = 'main/settings';
my $host_settings = 'host/settings';
my $autoconnect_file = '/var/efw/ethernet/noautoconnect';

# firstwizard ?
if ($0 =~ /step2\/*(netwiz|wizard).cgi/) {
    $pagename="firstwizard";
} else { 
    $pagename="netwizard";
}


###


my @eth_keys=('CONFIG_TYPE',

	      'GREEN_ADDRESS',
	      'GREEN_NETMASK',
	      'GREEN_NETADDRESS',
	      'GREEN_BROADCAST',
	      'GREEN_CIDR',
	      'GREEN_DEV',
	      'GREEN_IPS',

	      'ORANGE_ADDRESS',
	      'ORANGE_NETMASK',
	      'ORANGE_NETADDRESS',
	      'ORANGE_BROADCAST',
	      'ORANGE_CIDR',
	      'ORANGE_DEV',
	      'ORANGE_IPS',

	      'BLUE_ADDRESS',
	      'BLUE_NETMASK',
	      'BLUE_NETADDRESS',
	      'BLUE_BROADCAST',
	      'BLUE_CIDR',
	      'BLUE_DEV',
	      'BLUE_IPS',

	      );

my @main_keys=('LANGUAGE',
	       'KEYMAP',
	       'TIMEZONE',
	       'MAIN_ADMINMAIL',
	       'MAIN_MAILFROM',
	       'MAIN_SMARTHOST',
	       'WINDOWWITHHOSTNAME',
	       );

my @host_keys=('HOSTNAME',
	       'DOMAINNAME',
	       );

#red  blue orange
my %type_config=(
		 '000' => 0,
		 '001' => 1,
		 '100' => 2,
		 '101' => 3,
		 '010' => 4,
		 '011' => 5,
		 '110' => 6,
		 '111' => 7
		 );

my @dns_caption=(_('automatic'),
		 _('manual')
		 );

sub check_form_step3(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'STEP3_FORM',
       'option'   :{
                    'DISPLAY_GREEN_ADDRESS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'DISPLAY_ORANGE_ADDRESS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'HOSTNAME':{
                               'type':'text',
                               'required':'1',
                               'check':'name|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var hostname = eve._getCURElementsByName("HOSTNAME","input","STEP3_FORM")[0].value;
                                                        if (hostname.length > 15){
                                                            msg = "主机名最大长度为15";
                                                        }
                                                        return msg;
                               }
                             },
                    'DOMAINNAME':{
                               'type':'text',
                               'required':'1',
                               'check':'domain|name|',
                             },
                    'DISPLAY_GREEN_ADDITIONAL':{
                               'type':'textarea',
                               'required':'0',
                               'check':'other',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg = "";
                                                        var green = eve._getCURElementsByName("DISPLAY_GREEN_ADDRESS","input","STEP3_FORM")[0].value;
                                                        var green_mask = eve._getCURElementsByName("DISPLAY_GREEN_NETMASK","select","STEP3_FORM")[0].value;
                                                        var add = eve._getCURElementsByName("DISPLAY_GREEN_ADDITIONAL","textarea","STEP3_FORM")[0].value;
                                                        var test = add.split("/");
                                                        if(test.length < 2){
                                                            msg = "请输入正确IP和掩码";
                                                            return msg;
                                                        }
                                                        var ip = test[0];
                                                        var mask = test[1];
                                                        var final_mask;
                                                        if (!eve.validip(ip) || mask > 32 || mask < 1){
                                                            msg = "请输入正确IP和掩码"; 
                                                            return msg;
                                                        }
                                                        if (green_mask > mask){
                                                            final_mask = mask;
                                                        }
                                                        else{
                                                          final_mask = green_mask;
                                                        }
                                                        var temp_green = green.split(".");

                                                        var temp = ip.split(".");
                                                        var green_str="",add_str="";
                                                        for (i = 0; i < 4; i++) {
                                                            temp_green[i] = parseInt(temp_green[i]);
                                                            temp_green[i] = eve.formatIP(temp_green[i]);
                                                            green_str += temp_green[i];
                                                        }
                                                        for (i = 0; i < 4; i++) {
                                                            temp[i] = parseInt(temp[i]);
                                                            temp[i] = eve.formatIP(temp[i]);
                                                            add_str += temp[i];
                                                        }
                                                        var segment_green = green_str.substring(0,final_mask);
                                                        var segment = add_str.substring(0,final_mask);
                                                        /*if(segment == segment_green){
                                                            msg = "新增地址网段和原地址网段有重复"; 
                                                            return msg;
                                                        }*/
                                                        return msg;
                               }
                             },
                    'DISPLAY_ORANGE_ADDITIONAL':{
                               'type':'textarea',
                               'required':'0',
                               'check':'other',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg = "";
                                                        var green = eve._getCURElementsByName("DISPLAY_ORANGE_ADDRESS","input","STEP3_FORM")[0].value;
                                                        var green_mask = eve._getCURElementsByName("DISPLAY_ORANGE_NETMASK","select","STEP3_FORM")[0].value;
                                                        var add = eve._getCURElementsByName("DISPLAY_ORANGE_ADDITIONAL","textarea","STEP3_FORM")[0].value;
                                                        var test = add.split("/");
                                                        if(test.length < 2){
                                                            msg = "请输入正确IP和掩码";
                                                            return msg;
                                                        }
                                                        var ip = test[0];
                                                        var mask = test[1];
                                                        var final_mask;
                                                        if (!eve.validip(ip) || mask > 32 || mask < 1){
                                                            msg = "请输入正确IP和掩码"; 
                                                            return msg;
                                                        }
                                                        if (green_mask > mask){
                                                            final_mask = mask;
                                                        }
                                                        else{
                                                          final_mask = green_mask;
                                                        }
                                                        var temp_green = green.split(".");

                                                        var temp = ip.split(".");
                                                        var green_str="",add_str="";
                                                        for (i = 0; i < 4; i++) {
                                                            temp_green[i] = parseInt(temp_green[i]);
                                                            temp_green[i] = eve.formatIP(temp_green[i]);
                                                            green_str += temp_green[i];
                                                        }
                                                        for (i = 0; i < 4; i++) {
                                                            temp[i] = parseInt(temp[i]);
                                                            temp[i] = eve.formatIP(temp[i]);
                                                            add_str += temp[i];
                                                        }
                                                        var segment_green = green_str.substring(0,final_mask);
                                                        var segment = add_str.substring(0,final_mask);
                                                        /*if(segment == segment_green){
                                                            msg = "新增地址网段和原地址网段有重复"; 
                                                            return msg;
                                                        }*/
                                                        return msg;
                               }
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("STEP3_FORM");
    </script>
EOF
;
}
sub check_form_static(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'STATIC_FORM',
       'option'   :{
                    'DISPLAY_RED_ADDRESS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'DEFAULT_GATEWAY':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'MTU':{
                               'type':'text',
                               'required':'0',
                               'check':'num|',
                               'ass_check':function(eve){
                                                      var msg = "";
                                                      var value = eve._getCURElementsByName("MTU","input","STATIC_FORM")[0].value;
                                                      if(value > 5000 || value < 1){
                                                         msg = "MTU值必须在1-5000之间";
                                                      }
                                                      return msg;
                                                     }
                             },
                    'MAC':{
                               'type':'text',
                               'required':'0',
                               'check':'mac|',
                             },
                    'DISPLAY_RED_ADDITIONAL':{
                               'type':'textarea',
                               'required':'0',
                               'check':'other',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg = "";
                                                        var green = eve._getCURElementsByName("DISPLAY_RED_ADDRESS","input","STATIC_FORM")[0].value;
                                                        var green_mask = eve._getCURElementsByName("DISPLAY_RED_NETMASK","select","STATIC_FORM")[0].value;
                                                        var add = eve._getCURElementsByName("DISPLAY_RED_ADDITIONAL","textarea","STATIC_FORM")[0].value;
                                                        var test = add.split("/");
                                                        if(test.length < 2){
                                                            msg = "请输入正确IP和掩码";
                                                            return msg;
                                                        }
                                                        var ip = test[0];
                                                        var mask = test[1];
                                                        var final_mask;
                                                        if (!eve.validip(ip) || mask > 32 || mask < 1){
                                                            msg = "请输入正确IP和掩码"; 
                                                            return msg;
                                                        }
                                                        if (green_mask > mask){
                                                            final_mask = mask;
                                                        }
                                                        else{
                                                          final_mask = green_mask;
                                                        }
                                                        var temp_green = green.split(".");

                                                        var temp = ip.split(".");
                                                        var green_str="",add_str="";
                                                        for (i = 0; i < 4; i++) {
                                                            temp_green[i] = parseInt(temp_green[i]);
                                                            temp_green[i] = eve.formatIP(temp_green[i]);
                                                            green_str += temp_green[i];
                                                        }
                                                        for (i = 0; i < 4; i++) {
                                                            temp[i] = parseInt(temp[i]);
                                                            temp[i] = eve.formatIP(temp[i]);
                                                            add_str += temp[i];
                                                        }
                                                        var segment_green = green_str.substring(0,final_mask);
                                                        var segment = add_str.substring(0,final_mask);
                                                        /*if(segment == segment_green){
                                                            msg = "新增地址网段和原地址网段有重复"; 
                                                            return msg;
                                                        }*/
                                                        return msg;
                               }
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("STATIC_FORM");
    </script>
EOF
;
}
sub check_form_dhcp(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'DHCP_FORM',
       'option'   :{
                    'MTU':{
                               'type':'text',
                               'required':'0',
                               'check':'num|',
                               'ass_check':function(eve){
                                                      var msg = "";
                                                      var value = eve._getCURElementsByName("MTU","input","DHCP_FORM")[0].value;
                                                      if(value > 5000 || value < 1){
                                                         msg = "MTU值必须在1-5000之间";
                                                      }
                                                      return msg;
                                                     }
                             },
                    'MAC':{
                               'type':'text',
                               'required':'0',
                               'check':'mac|',
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("DHCP_FORM");
    </script>
EOF
;
}
sub check_form_pppoe(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'PPPOE_FORM',
       'option'   :{
                    'USERNAME':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
							   'other_reg':'/\.*/',
                             },
                    'PASSWORD':{
                               'type':'password',
                               'required':'1',
                             },
                    'MTU':{
                               'type':'text',
                               'required':'0',
                               'check':'num|',
                               'ass_check':function(eve){
                                                      var msg = "";
                                                      var value = eve._getCURElementsByName("MTU","input","PPPOE_FORM")[0].value;
                                                      if(value > 5000 || value < 1){
                                                         msg = "MTU值必须在1-5000之间";
                                                      }
                                                      return msg;
                                                     }
                             },
                    'SERVICENAME':{
                               'type':'text',
                               'required':'0',
                               'check':'name|',
                             },
                    'CONCENTRATORNAME':{
                               'type':'text',
                               'required':'0',
                               'check':'name|',
                             },
                    'DISPLAY_RED_ADDITIONAL':{
                               'type':'textarea',
                               'required':'0',
                               'check':'other',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg = "";
                                                        var add = eve._getCURElementsByName("DISPLAY_RED_ADDITIONAL","textarea","PPPOE_FORM")[0].value;
                                                        var test = add.split("/");
                                                        if(test.length < 2){
                                                            msg = "请输入正确IP和掩码";
                                                            return msg;
                                                        }
                                                        var ip = test[0];
                                                        var mask = test[1];
                                                        var final_mask;
                                                        if (!eve.validip(ip) || mask > 32 || mask < 1){
                                                            msg = "请输入正确IP和掩码"; 
                                                            return msg;
                                                        }
                                                        
                               }
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("PPPOE_FORM");
    </script>
EOF
;
}
sub check_form_gateway(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'GATEWAY_FORM',
       'option'   :{
                    'DEFAULT_GATEWAY':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("GATEWAY_FORM");
    </script>
EOF
;
}
sub check_form_dns(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'DNS_FORM',
       'option'   :{
                    'DNS1':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                               'ass_check':function(eve){
                                                      var msg = "";
                                                      var dns1 = eve._getCURElementsByName("DNS1","input","DNS_FORM")[0].value;
                                                      var dns2 = eve._getCURElementsByName("DNS2","input","DNS_FORM")[0].value;
                                                      if (dns1 == dns2) {
                                                          msg = "DNS不能重复";
                                                      }
                                                      return msg;
                                                     }
                             },
                    'DNS2':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|',
                               'ass_check':function(eve){
                                                      var msg = "";
                                                      var dns1 = eve._getCURElementsByName("DNS1","input","DNS_FORM")[0].value;
                                                      var dns2 = eve._getCURElementsByName("DNS2","input","DNS_FORM")[0].value;
                                                      if (dns1 == dns2) {
                                                          msg = "DNS不能重复";
                                                      }
                                                      return msg;
                                                     }
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("DNS_FORM");
    </script>
EOF
;
}
sub check_form_mail(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'MAIL_FORM',
       'option'   :{
                    'MAIN_ADMINMAIL':{
                               'type':'text',
                               'required':'0',
                               'check':'mail|',
                             },
                    'MAIN_MAILFROM':{
                               'type':'text',
                               'required':'0',
                               'check':'mail|',
                             },
                    'MAIN_SMARTHOST':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|domain|',
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("MAIL_FORM");
    </script>
EOF
;
}
sub init($) {
    $ethernet_settings_default = $swroot.'/ethernet/default/settings';
    $ethernet_settings = $swroot.'/ethernet/settings';
    $main_settings = $swroot.'/main/settings';
    $host_settings = $swroot.'/host/settings';
}

# initialize or check & load session
sub init_session() {

    # new session
    if (!defined($par{'session_id'})) {
	$session_id = session_start();
	session_save($session_id, $session);
	print_debug("$0: new session: $session_id\n");
	return;
    }

    # load session
    if (session_check($par{'session_id'})) {
	$session_id = $par{'session_id'};
	session_load($session_id, $session);
	print_debug("$0: existing session: $session_id\n");
	return;
    }

    die('invalid session');
}

sub load_red_items() {
    my $if_count = get_if_number();

    my @arr = ();

    my @types = (
		 {'name' => 'STATIC',
		  'caption' => '固定IP'},
		 {'name' => 'DHCP',
		  'caption' => 'DHCP'},
		 {'name' => 'PPPOE',
		  'caption' => _('PPPoE')},
		 {'name' => 'PPTP',
		  'caption' => _('PPTP')},
		 {'name' => 'NONE',
		  # 'caption' => '单臂,旁路'}
		  'caption' => '透明网关'}
		 );
    my $i = 0;
    foreach my $type (@types) {
	my $lever_file = 'lever_'.lc($type->{'name'}).'.pl';
	next if (! -e $lever_file);
	
	my %hash = (
		    'RED_LOOP_INDEX'    => $i,
		    'RED_LOOP_NAME'     => $type->{'name'},
		    'RED_LOOP_CAPTION'  => $type->{'caption'},
		    'RED_LOOP_SELECTED' => ($session->{'RED_TYPE'} eq $type->{'name'} ? 'checked':'')
		    );
	push(@arr, \%hash);

    }
    return \@arr;
}

sub load_zones_items() {
    my @arr = ();
    my $if_count = get_if_number() - 1; # green must exist
	
	my $sys_eth_num= @sys_eth;#获取系统接口数量

    if (($session->{'RED_TYPE'} ne 'ADSL') && 
	($session->{'RED_TYPE'} ne 'ISDN') &&
	($session->{'RED_TYPE'} ne 'ANALOG') &&
	($session->{'RED_TYPE'} ne 'NONE')) {
	$if_count--;
    }

    for (my $i=0; $i<2 && ($i-1 <= $if_count); $i++) {####如需放出蓝色接口接只需把$i<2改为$i<4即可  此处修改by-elvis 2012-10-23
		my $name = '';
		my $caption = '';
		if ($i == 0) {
		    $name = 'NONE';
		    $caption = _('NONE');
		}
		if ($i == 1) {
		    $name = 'ORANGE';
		    $caption = _('ORANGE')."区";
		}
		if ($i == 2) {
		    $name = 'BLUE';
		    $caption = _('BLUE');
		}
		if ($i == 3) {
		    $name = 'ORANGE_BLUE';
		    $caption = _('ORANGE & BLUE');
		}
		my %hash = (
			    'ZONES_LOOP_INDEX'    => $i,
			    'ZONES_LOOP_NAME'     => $name,
			    'ZONES_LOOP_CAPTION'  => $caption,
			    'ZONES_LOOP_SELECTED' => ($session->{'ZONES'} eq $name ? 'checked':'')
			    );
		if($sys_eth_num>=6)
		{
			if($if_count==1 && $i ==0){
				push(@arr, \%hash);

			}
			elsif($if_count==2 && ($i==0 ||$i ==1 || $i==2)){
				push(@arr, \%hash);
			}
			elsif($if_count==3 && ($i==0 ||$i ==1 || $i==2 || $i==3)){
				push(@arr, \%hash);
			}
			elsif($if_count>3){
				push(@arr, \%hash);
			}
		}else{
			if($if_count==0 && $i ==0)
			{
				push(@arr, \%hash);

			}

			elsif($if_count==1 && ($i==0 ||$i ==1 || $i==2))
			{
				push(@arr, \%hash);
			}

			elsif($if_count==2 && ($i==0 ||$i ==1 || $i==2 || $i==3))
			{
				push(@arr, \%hash);
			}elsif($if_count>2)
			{
				push(@arr, \%hash);
			}
		}
		
		if ($if_count <= 0) {
		    return \@arr;
		}
    }
    return \@arr;
}


# prepare placeholder data
sub prepare_values() {
    $tpl_ph->{'title'} = _('Step')." ".$live_data->{'step'}."/$stepnum:  ".$steps{$live_data->{'step'}};
    $tpl_ph->{'session_id'} = $session_id;
    $tpl_ph->{'self'} = '';
    $tpl_ph->{'step'} = $live_data->{'step'};
    $tpl_ph->{'substep'} = $live_data->{'substep'};

    my $if_count = get_if_number();
    $tpl_ph->{'if_count'} = $if_count;

    if ($live_data->{'step'} eq '1') {
	$tpl_ph->{'RED_LOOP'} = load_red_items();
	return;
    }
    if ($live_data->{'step'} eq '2') {
	$tpl_ph->{'ZONES_LOOP'} = load_zones_items();
	load_ifaces();
	return;
    }
    if (orange_used()) {
	$tpl_ph->{'HAVE_ORANGE'} = 1;
    }
    if (blue_used()) {
	$tpl_ph->{'HAVE_BLUE'} = 1;
    }

    if ($live_data->{'step'} eq '3') {

	my ($primary, $ip, $mask, $cidr) = getPrimaryIP($session->{'GREEN_IPS'});
	$tpl_ph->{'DISPLAY_GREEN_ADDRESS'} = $ip;
	$tpl_ph->{'DISPLAY_GREEN_NETMASK_LOOP'} = loadNetmasks($cidr);

	$tpl_ph->{'DISPLAY_GREEN_ADDITIONAL'} = getAdditionalIPs($session->{'GREEN_IPS'});
	$tpl_ph->{'DISPLAY_GREEN_ADDITIONAL'} =~ s/,/\n/g;
	load_ifaces();
	$tpl_ph->{'IFACE_GREEN_LOOP'} = create_ifaces_list('GREEN');
	if (orange_used()) {
	    my ($primary, $ip, $mask, $cidr) = getPrimaryIP($session->{'ORANGE_IPS'});
	    $tpl_ph->{'DISPLAY_ORANGE_ADDRESS'} = $ip;
	    $tpl_ph->{'DISPLAY_ORANGE_NETMASK_LOOP'} = loadNetmasks($cidr);
	    $tpl_ph->{'DISPLAY_ORANGE_ADDITIONAL'} = getAdditionalIPs($session->{'ORANGE_IPS'});
	    $tpl_ph->{'DISPLAY_ORANGE_ADDITIONAL'} =~ s/,/\n/g;

	    $tpl_ph->{'IFACE_ORANGE_LOOP'} = create_ifaces_list('ORANGE');
	}
	if (blue_used()) {
	    my ($primary, $ip, $mask, $cidr) = getPrimaryIP($session->{'BLUE_IPS'});
	    $tpl_ph->{'DISPLAY_BLUE_ADDRESS'} = $ip;
	    $tpl_ph->{'DISPLAY_BLUE_NETMASK_LOOP'} = loadNetmasks($cidr);
	    $tpl_ph->{'DISPLAY_BLUE_ADDITIONAL'} = getAdditionalIPs($session->{'BLUE_IPS'});
	    $tpl_ph->{'DISPLAY_BLUE_ADDITIONAL'} =~ s/,/\n/g;

	    $tpl_ph->{'IFACE_BLUE_LOOP'} = create_ifaces_list('BLUE');
	}
	return;
    }

    if ($live_data->{'step'} eq '4') {

	if ($lever ne '') {
	    lever_prepare_values();
	}

	$tpl_ph->{'DNS_SELECTED_0'} = ($session->{'DNS_N'} == 0 ? 'checked':'');
	$tpl_ph->{'DNS_SELECTED_1'} = ($session->{'DNS_N'} == 1 ? 'checked':'');
    }

    if ($live_data->{'step'} eq '5') {
	$tpl_ph->{'DNS_CAPTION'} = @dns_caption[$session->{'DNS_N'}];
	if ($session->{'DNS_N'} == 1) {
	    $tpl_ph->{'DNS_MANUAL'} = 1;
	}
    }
    if ($live_data->{'step'} eq '8') {
	my ($primary,$ip,$mask,$cidr) = getPrimaryIP($session->{'GREEN_IPS'});
	$tpl_ph->{'GREEN_LINK'} = 'https://'.$ip.':10443/cgi-bin/netwizard.cgi';
    }
}

sub set_config_type() {
    my $red = $session->{'RED_TYPE'};
    my $zones = $session->{'ZONES'};
    my $has_red = ($red =~ /ADSL|ISDN/ ? 0:1);
    my $has_blue = ($zones =~ /BLUE/? 1:0);
    my $has_orange = ($zones =~ /ORANGE/? 1:0);

    $session->{'CONFIG_TYPE'} = $type_config{"$has_red$has_blue$has_orange"};
}

# check parameters according to step,
# put valid parameters to the session and
# return error message if an invalid parameter was found
sub checkpar2session 
{
    ############ step 1

    if ($live_data->{'step'} eq '1') {
	my $red_type = $par{'RED_TYPE'};
	if (defined($red_type) && ($red_type =~ /(?:STATIC|DHCP|ADSL|PPPOE|NONE|ISDN|ANALOG)/)) {
	    $session->{'RED_TYPE'} = $red_type;
	    set_config_type();
	    return;
	}
	return _('Please select a type of RED interface!');
    }

    ############ step 2

    if ($live_data->{'step'} eq '2') {
	my $zones = $par{'ZONES'};
	if (defined($zones) && ($zones =~ /(?:NONE|BLUE|ORANGE|ORANGE_BLUE)/)) {
	    $session->{'ZONES'} = $zones;
	    set_config_type();
	    return;
	}
	return _('Invalid zone!');
    }


    ############ step 3

    if ($live_data->{'step'} eq '3') {
	listdevices(1);
	my $err = '';
	my $i=0;
	if ($par{'HOSTNAME'} eq '') {
	    $err .= _('Please insert the hostname!').'<BR>';
		
	} elsif (!($par{'HOSTNAME'} =~ /^[a-zA-Z]{1,1}[a-zA-Z0-9\.\-\_]{1,255}[a-zA-Z0-9]{1,1}$/)) {
	    $session->{'HOSTNAME'} = $par{'HOSTNAME'};
	    $err .= _('Please insert a valid hostname!').'<BR>';	
		
	} else {
	    if ($settings->{'HOSTNAME'} ne $par{'HOSTNAME'}) {
		$session->{'rebuildcert'} = 1;
	    }
	    $session->{'HOSTNAME'} = $par{'HOSTNAME'};
	}


	if ($par{'DOMAINNAME'} eq '') {
	    $err .= _('Please insert the domainname!').'<BR>';
		
        } elsif (! validdomainname($par{'DOMAINNAME'})) {
            $session->{'DOMAINNAME'} = $par{'DOMAINNAME'};
            $err .= _('Please insert a valid domainname!').'<BR>';  
						
	} else {
	    if ($settings->{'DOMAINNAME'} ne $par{'DOMAINNAME'}) {
		$session->{'rebuildcert'} = 1;
	    }
	    $session->{'DOMAINNAME'} = $par{'DOMAINNAME'};
	}

	my $ifacelist = ifnum2device($par{'GREEN_DEVICES'});
	$session->{'GREEN_DEVICES'} = $ifacelist;
        if ($ifacelist =~ /^$/) {
            my $zone = _('GREEN');
	    $err .= _('Please select at least one interface for zone %s!', $zone).'<BR>';
		
        }

	if (orange_used()) {
	    my $ifacelist = ifnum2device($par{'ORANGE_DEVICES'});
	    my $reterr = check_iface_free($ifacelist, 'ORANGE');
	    if ($reterr) {
		$err .= $reterr;
		
	    } else {
		$session->{'ORANGE_DEVICES'} = $ifacelist;
	    }
            if ($ifacelist =~ /^$/) {
                my $zone = _('ORANGE');
	        $err .= _('Please select at least one interface for zone %s!', $zone).'<BR>';
			
            }
	} else {
	    $session->{'ORANGE_DEVICES'} = unset;
	}
	if (blue_used()) {
	    my $ifacelist = ifnum2device($par{'BLUE_DEVICES'});
	    my $reterr = check_iface_free($ifacelist, 'BLUE');
	    if ($reterr) {
		$err .= $reterr;
		
	    } else {
		$session->{'BLUE_DEVICES'} = $ifacelist;
	    }
            if ($ifacelist =~ /^$/) {
                my $zone = _('BLUE');
	        $err .= _('Please select at least one interface for zone %s!', $zone).'<BR>';
			
            }
	} else {
	    $session->{'BLUE_DEVICES'} = unset;
	}

	my ($ok_ips, $nok_ips) = createIPS($par{'DISPLAY_GREEN_ADDRESS'}.'/'.$par{'DISPLAY_GREEN_NETMASK'}, $par{'DISPLAY_GREEN_ADDITIONAL'});
	if ($nok_ips ne '') {
	    foreach my $nokip (split(/,/, $nok_ips)) {
		$err .= _('The GREEN IP address or network mask "%s" is not correct.', $nokip).'<BR>';
		
	    }
	} else {
	    my ($primary, $ip, $mask, $cidr) = getPrimaryIP($ok_ips);
	    my ($oldprimary, $oldip, $oldmask, $oldcidr) = getPrimaryIP($session->{'GREEN_IPS'});
	    
	    if ($ip ne $oldip) {
		$session->{'green_changed'} = 1;
	    }

	    $session->{'GREEN_IPS'} = $ok_ips;

	    foreach my $invalid (@{checkNetaddress($session->{'GREEN_IPS'})}) {
		$err .= _("The GREEN IP address '%s' is the same as its network address, which is not allowed!", $invalid)."<BR>";
		
	    }
	    foreach my $invalid (@{checkBroadcast($session->{'GREEN_IPS'})}) {
		$err .= _("The GREEN IP address '%s' is the same as its broadcast address, which is not allowed!", $invalid)."<BR>";
		
	    }
	    foreach my $invalid (@{checkInvalidMask($session->{'GREEN_IPS'})}) {
		$err .= _("The network mask of the GREEN IP address '%s' addresses only 1 IP address, which will lock you out if applied. Choose another one!", $invalid)."<BR>";
		
	    }
	}

	if (orange_used()) {
	    my ($ok_ips, $nok_ips) = createIPS($par{'DISPLAY_ORANGE_ADDRESS'}.'/'.$par{'DISPLAY_ORANGE_NETMASK'}, $par{'DISPLAY_ORANGE_ADDITIONAL'});
	    if ($nok_ips ne '') {
		foreach my $nokip (split(/,/, $nok_ips)) {
		    $err .= _('The ORANGE IP address or network mask "%s" is not correct.', $nokip).'<BR>';
			
		}
	    } else {
		$session->{'ORANGE_IPS'} = $ok_ips;
		
		foreach my $invalid (@{checkNetaddress($session->{'ORANGE_IPS'})}) {
		    $err .= _("The ORANGE IP address '%s' is the same as its network address, which is not allowed!", $invalid)."<BR>";
			
		}
		foreach my $invalid (@{checkBroadcast($session->{'ORANGE_IPS'})}) {
		    $err .= _("The ORANGE IP address '%s' is the same as its broadcast address, which is not allowed!", $invalid)."<BR>";
			
		}
		foreach my $invalid (@{checkInvalidMask($session->{'ORANGE_IPS'})}) {
		    $err .= _("The network mask of the ORANGE IP address '%s' addresses only 1 IP address, which will lock you out if applied. Choose another one!", $invalid)."<BR>";
			
		}
	    }
	}
	if (blue_used()) {
	    my ($ok_ips, $nok_ips) = createIPS($par{'DISPLAY_BLUE_ADDRESS'}.'/'.$par{'DISPLAY_BLUE_NETMASK'}, $par{'DISPLAY_BLUE_ADDITIONAL'});
	    if ($nok_ips ne '') {
		foreach my $nokip (split(/,/, $nok_ips)) {
		    $err .= _('The BLUE IP address or network mask "%s" is not correct.', $nokip).'<BR>';
			
		}
	    } else {
		$session->{'BLUE_IPS'} = $ok_ips;
		
		foreach my $invalid (@{checkNetaddress($session->{'BLUE_IPS'})}) {
		    $err .= _("The BLUE IP address '%s' is the same as its network address, which is not allowed!", $invalid)."<BR>";
			
		}
		foreach my $invalid (@{checkBroadcast($session->{'BLUE_IPS'})}) {
		    $err .= _("The BLUE IP address '%s' is the same as its broadcast address, which is not allowed!", $invalid)."<BR>";
		}
		foreach my $invalid (@{checkInvalidMask($session->{'BLUE_IPS'})}) {
		    $err .= _("The network mask of the BLUE IP address '%s' addresses only 1 IP address, which will lock you out if applied. Choose another one!", $invalid)."<BR>";
		}
	    }
	}

	if ($err ne '') {
	    return $err;
	}

	if (orange_used()) {
	    if (network_overlap($session->{'GREEN_IPS'}, $session->{'ORANGE_IPS'})) {
		$err .= _('The GREEN and ORANGE networks are not distinct.').'<BR>';
	    }
	}
	if (blue_used()) {
	    if (network_overlap($session->{'GREEN_IPS'}, $session->{'BLUE_IPS'})) {
		$err .= _('The GREEN and BLUE networks are not distinct.').'<BR>';
		
	    }
	}
	if (blue_used() && orange_used()) {
	    if (network_overlap($session->{'ORANGE_IPS'}, $session->{'BLUE_IPS'})) {
		$err .= _('The ORANGE and BLUE networks are not distinct.').'<BR>';
		
	    }
	}

	return $err;
    }
    
    
    
    ############ step 4
    
    if ($live_data->{'step'} eq '4') {
	my $err = '';

	if ($lever ne '') {
	    return lever_savedata();
	}
	return $err;
    }


    if ($live_data->{'step'} eq '5') {
	if ($session->{'DNS_N'} == 0) {
	    return;
	}

	my $ip = '';
	my $mask = '';
	my $err = '';
	    
	($err, $ip, $mask) = check_ip($par{'DNS1'}, '255.255.255.255');
	$err = validip($par{'DNS1'});
	if ($err) {
	    $session->{'DNS1'} = $ip;
	} else {
	    $ret .= _('The IP address of DNS1 is not correct.').'<BR>';
	}
    if ($par{'DNS2'} ne "") {
        ($err, $ip, $mask) = check_ip($par{'DNS2'}, '255.255.255.255');
        $err = validip($par{'DNS2'});
        if ($err) {
            $session->{'DNS2'} = $ip;
        } else {
            $ret .= _('The IP address of DNS2 is not correct.').'<BR>';
        }
    }
    else{
        $session->{'DNS2'} = "__EMPTY__";
    }

	if ($ret ne '') {
	    return $ret;
	}
	return;
    }

    if ($live_data->{'step'} eq '6') {
	my $err = '';

	if ($par{'MAIN_MAILFROM'}) {
	    if (! validemail($par{'MAIN_MAILFROM'})) {
		$err .= _("Sender e-mail address '%s' is invalid", 
			  $par{'MAIN_MAILFROM'})."<BR>";
	    } else {
		$session->{'MAIN_MAILFROM'} = $par{'MAIN_MAILFROM'};
	    }
	}

	if ($par{'MAIN_ADMINMAIL'}) {
	    if (! validemail($par{'MAIN_ADMINMAIL'})) {
		$err .= _("Admin e-mail address '%s' is invalid", 
			  $par{'MAIN_ADMINMAIL'})."<BR>";
	    } else {
		$session->{'MAIN_ADMINMAIL'} = $par{'MAIN_ADMINMAIL'};
	    }
	}

	if ($par{'MAIN_SMARTHOST'}) {
	    my ($host, $port) = split(/:/, $par{'MAIN_SMARTHOST'});
	    my $ok = 1;
	    if (! (validip($host) || validfqdn($host) || validhostname($host))) {
		$err .= _("Host '%s' of mail smarthost '%s' is no valid fqdn, hostname or IP address",
			  $host, $par{'MAIN_SMARTHOST'}
		    );
		$ok = 0;
	    }
	    if ($port && !validport($port)) {
		$err .= _("Port '%s' of mail smarthost '%s' is no valid port.",
			  $port, $par{'MAIN_SMARTHOST'}
		    );
		$ok = 0;
	    }
	    if ($ok) {
		$session->{'MAIN_SMARTHOST'} = $par{'MAIN_SMARTHOST'};
	    }
	}

	return $err;
    }

    
    if ($live_data->{'step'} eq '7') {
	apply();
	$reload = 'YES DO IT';
	return;
    }
    
    return 'NOT IMPLEMENTED';
}

sub alter_eth_settings($) {
    my $ref = shift;
    my %config = %$ref;
    my $if_count = get_if_number();
    my $next_if = 1; # 0 == green
    my $fixed = 0;

    my ($primary,$ip,$mask,$cidr) = getPrimaryIP($config{'GREEN_IPS'});
    $config{'GREEN_ADDRESS'} = $ip;
    $config{'GREEN_NETMASK'} = $mask;
    $config{'GREEN_CIDR'} = $cidr;
    ($config{'GREEN_NETADDRESS'},) = ipv4_network($primary);
    $config{'GREEN_BROADCAST'} = ipv4_broadcast($primary);

    if (orange_used()) {
	my ($primary,$ip,$mask,$cidr) = getPrimaryIP($config{'ORANGE_IPS'});
	$config{'ORANGE_ADDRESS'} = $ip;
	$config{'ORANGE_NETMASK'} = $mask;
	$config{'ORANGE_CIDR'} = $cidr;
	($config{'ORANGE_NETADDRESS'},) = ipv4_network($primary);
	$config{'ORANGE_BROADCAST'} = ipv4_broadcast($primary);
    }
    if (blue_used()) {
	my ($primary,$ip,$mask,$cidr) = getPrimaryIP($config{'BLUE_IPS'});
	$config{'BLUE_ADDRESS'} = $ip;
	$config{'BLUE_NETMASK'} = $mask;
	$config{'BLUE_CIDR'} = $cidr;
	($config{'BLUE_NETADDRESS'},) = ipv4_network($primary);
	$config{'BLUE_BROADCAST'} = ipv4_broadcast($primary);
    }
    return \%config;
}

sub apply() {
    satanize($session);
    if ($session->{'RED_DEV'}) {
	disable_conflicting_uplinks($session->{'RED_DEV'});
    }
    my $eth_settings = alter_eth_settings(select_from_hash(\@eth_keys, $session));
    writeconf($ethernet_settings, $eth_settings);
    writeconf($main_settings, select_from_hash(\@main_keys, $session));
    writeconf($host_settings, select_from_hash(\@host_keys, $session));
    write_bridges();
    set_red_default("");

    if ($lever ne '') {
	lever_apply();
    }
}


# load all necessary values into the session, if not already present
sub load_values {
    my $eth_default = readconf($ethernet_settings_default);
    my $eth_settings = $eth_default;

    if (-e $ethernet_settings) {
	$eth_settings = readconf($ethernet_settings);
    }
    load_all_keys($session, \@eth_keys, $eth_settings, $eth_default, 0);
    load_all_keys($settings, \@eth_keys, $eth_settings, $eth_default, 0);

    my $main_settings = readconf($main_settings);
    load_all_keys($session, \@main_keys, $main_settings, 0, 0);
    load_all_keys($settings, \@main_keys, $main_settings, 0, 0);

    my $host_settings = readconf($host_settings);
    load_all_keys($session, \@host_keys, $host_settings, 0, 0);
    load_all_keys($settings, \@host_keys, $host_settings, 0, 0);

    if (orange_used()) {
	$session->{'ZONES'} = 'ORANGE';
    }
    if (blue_used()) {
	$session->{'ZONES'} = 'BLUE';
    }
    if (orange_used() && blue_used()) {
	$session->{'ZONES'} = 'ORANGE_BLUE';
    }
    if (! orange_used() && ! blue_used()) {
	$session->{'ZONES'} = 'NONE';
    }
    $session->{'GREEN_DEV'} = 'br0';
    $session->{'ORANGE_DEV'} = 'br1';
    $session->{'BLUE_DEV'} = 'br2';

    load_red('MAIN');
    if ($lever ne '') {
	lever_load();
    }
}


# realizes the substeps within modem configuration
sub substep($) {
    my $direction = shift;

    if (! lever_check_substep()) {
	$live_data->{'substep'} = 1;
	return;
    }
    $live_data->{'substep'} += $direction;
    if (! lever_check_substep()) {
	$live_data->{'step'} += $direction;
	$live_data->{'substep'} = 0;
    }
}

sub in_substep() {
    if (($live_data->{'step'} == 4) && ($lever ne '')) {
	return 1;
    }
    return 0;
}


sub set_lever() {
    if ($live_data->{'step'} != 4) {
	$lever = $session->{'lever'};
	return;
    }
    $lever = lc($session->{'RED_TYPE'});
    $session->{'lever'} = $lever;
}

sub load_lever() {
    my $lever_file = 'lever_skel.pl';
    if ($lever ne '') {
	$lever_file = 'lever_'.$lever.'.pl';
    }
    if (! -e $lever_file) {
	die("Lever file $lever_file not found!");
    }
    require $lever_file;
    lever_init($session, $settings, \%par, $tpl_ph, $live_data);
}


# check last step's parameters, update the session 
# and decide which step to do next
sub state_machine() {
    $live_data->{'step'} = $par{'step'};
    $live_data->{'substep'} = $par{'substep'};

    set_lever();
    load_lever();

    if (!exists($steps{$live_data->{'step'}})) {
	# first invocation -> step = 1
	$live_data->{'step'} = 1;
	return;
    }

    $tpl_ph->{'error_message'} = '';
    # follow up step -> see whether 'prev' or 'next' was pressed
    if (defined($par{'next'})) {
	# next -> check values and store them

	my $err = checkpar2session();
	my @error = split("<BR>",$err);
	my $j = 0;
	my $err_new = "";
	for(my $j = 0;$j<5;$j++)
	{
		if(@error>$j)
		{
			if($j eq 4)
			{
				$err_new.="<li style='text-align:left;'>".$error[$j]."......</li>";
			}else{
				$err_new.="<li style='text-align:left;'>".$error[$j]."</li>";
			}
		}
	}
	
	if (defined($err_new) and $err_new ne '') {
	    # valid: go to next page
	    $tpl_ph->{'error_message'} = $err_new;
	    return;
	}
	$direction = 1;

    } elsif (defined($par{'prev'})) {
	# prev -> forget parameters, go the previous page
	$direction = -1;
    } elsif (defined($par{'cancel'})) {
	my ($primary, $ip, $mask, $cidr) = getPrimaryIP($session->{'GREEN_IPS'});
        $header = '<meta http-equiv="refresh" content="20; URL=https://'.$ip.':10443/cgi-bin/main.cgi">';
    } else {
	die('no "next" or "prev" defined');
    }

    if (! in_substep()) {
	$live_data->{'step'} += $direction;
	if ($live_data->{'step'} == 0) {
	    $live_data->{'step'} = 1;
	}
    }

    set_lever();
    load_lever();

    if (in_substep()) {
	substep($direction);
	return;
    }
}

sub get_template($$) {
    
    use HTML::Template::Expr;

    my $filename = shift;
    my $values_ref = shift;
    my %values = %$values_ref;

    my $template = HTML::Template::Expr->new(filename => $filename,
					     die_on_bad_params => 0
					     );
    $template->param(%values);
    return $template->output();

}

sub satanize($) {
    my $ref = shift;
    foreach $key (%$ref) {
	if ($ref->{$key} eq '__EMPTY__') {
	    $ref->{$key} = '';
	}
    }
    return $ref;
}


# print template, filling placeholders with: %tr, %session and %tpl_ph
sub print_template($) {
    my $config_base = shift;
    my $filename = '';

    my %values_hash = ();
    my $values = \%values_hash;

    $values = hash_merge($values, \%strings);

    init($config_base);
    init_session();
    init_ifacetools($session, \%par);
    init_redtools($session, $settings);
    init_ethconfig();

    load_values();
    state_machine();
    prepare_values();

    $values = hash_merge($values, satanize(prefix('NW_VAL_',$session)));
    $values = hash_merge($values, satanize(prefix('NW_VAL_',$tpl_ph)));

    $filename = 'netwiz'.$live_data->{'step'};
    if ($live_data->{'substep'} != 0) {
	$filename .= "_".$lever."_".$live_data->{'substep'};
    }

    my $content = get_template('/usr/share/netwizard/' .$filename.'.tmpl', $values);
    session_save($session_id, $session);
    my $header = '';

    if ($reload eq 'YES DO IT') {
	my ($primary,$ip,$mask,$cidr) = getPrimaryIP($session->{'GREEN_IPS'});
        if ($pagename eq "firstwizard") {
            system('rm /var/efw/main/initial_wizard_step2');
            system('touch /var/efw/main/initial_wizard_step3');
            $header = '<meta http-equiv="refresh" content="20; URL=https://'.$ip.':10443/cgi-bin/netwizard.cgi" />';
        } else {
            $header = '<meta http-equiv="refresh" content="20; URL=https://'.$ip.':10443/cgi-bin/netwizard.cgi" />';
        }

    }
    return ($reload, $header, $content, $session->{'rebuildcert'});

}

# redirect to main page
if (($0 =~ /step2\/*(netwiz|wizard).cgi/) and (! -f "/var/efw/main/initial_wizard_step2" ) or (defined $par{'cancel'})) {
    print "Status: 302 Moved\n";
    print "Location: https://".$ENV{'SERVER_ADDR'}.":10443/cgi-bin/netwizard.cgi\n\n";
    exit;
}

1;
