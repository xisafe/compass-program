#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 上行线路编辑器页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================


require 'ifacetools.pl';
require 'netwizard_tools.pl';
require '/var/efw/header.pl';
require 'ethconfig.pl';
require 'modemtools.pl';

my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $refresh = "<script type='text/javascript'>function disedit(eve){var event = eve||window.event;var target = (event.srcElement||event.target).value;var mask_edit = document.getElementById(target+'RED_NETMASK').value;var red_mask = document.getElementById('red_mask').options;for(var i=0;i<red_mask.length;i++){if(red_mask[i].value == mask_edit){red_mask[i].selected = 'selected';break;}}document.getElementById('add-div-content').style.display='block';}</script>";

my %allow = ("NONE" => -1, "STATIC" => -1, "DHCP" => -1, "PPPOE" => -1, "ADSL" => 1 ,"ISDN" => 1 ,"PPTP" => -1, "ANALOG" => -1);
my %device_used = ();
my %uplink_networks = ();

my $eth_value = `ifconfig | grep HWaddr|sed 's/  */ /g'|cut -d " " -f1,5|sed 's/ /=/g'`;
my @eth_values = split(/\n/,$eth_value);
my $last_eth_value="";
foreach my $elem(@eth_values){
    $last_eth_value .=$elem."&";
}
my @red_types = ();
my %red_names = ();
foreach my $regfile (glob("/home/httpd/cgi-bin/uplinkType-*.pl")) {
    require $regfile;
	if ($#red_types < 0) {
    	$red_types[0] = $uplink_code;
	} else {
    	$red_types[$#red_types+1] = $uplink_code;
	}
    $red_names{$uplink_code} = $uplink_name;
}

my @adsl_protocols = ("RFC2364", "RFC1483", "STATIC", "DHCP");
my %adsl_names = ("RFC2364" => "PPPoA", "RFC1483" => "PPPoE", "STATIC" => "PPPoE static", "DHCP" => "PPPoE dhcp");
my @auth_types = ("pap-or-chap", "pap", "chap");
my %auth_names = ("pap-or-chap" => "PAP or CHAP", "pap" => "PAP", "chap" => "CHAP");
my %encap_names = ("0" => "bridged VC", "1" => "bridged LLC", "2" => "routed VC", "3" => "routed LLC");
my @pptp_methods = ("STATIC", "DHCP");
my %pptp_names = ("STATIC" => _("static"), "DHCP" => "dhcp");
my @analog_modems = ("modem", "hsdpa", "cdma");
my %analog_modem_names = ("modem" => "Simple analog modem", "hsdpa" => "UMTS/HSDPA modem", "cdma" => "UMTS/CDMA modem");
my @speeds = ('300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800');

init_ethconfig();
(my $ifaces, my $ifacesdata) = list_devices_description(3, 'RED|NONE', 1);

my $adsl_modems = iterate_modems("adsl");
my $isdn_modems = iterate_modems("isdn");
my $modeminforef = iterate_comports();
my @comports = @$modeminforef;

my $uplinkdir = '/var/efw/uplinks';

my $UP_PNG = '/images/stock_up-16.png';
my $DOWN_PNG = '/images/stock_down-16.png';
my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $EDIT_PNG = '/images/edit.png';
my $DELETE_PNG = '/images/delete.png';
my $OPTIONAL_PNG = '/images/blob.png';

my @errormessages = ();

my @uplinklist = ();
my %uplinks = ();
my %uplink_info = ();

my $show_advanced = false;

my %selected = ();
my %checked = ();
my %display = ();
sub check_form(){
    printf <<EOF
    <script>
    var check = new ChinArk_forms();
    var object = {
       'form_name':'UPLINK_FORM',
       'option'   :{
                    'NAME':{
                               'type':'text',
                               'required':'0',
                               'check':'other|',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                  var msg="";
                                  var names = eve._getCURElementsByName("NAME","input","UPLINK_FORM")[0].value;
                                  var reg = /\^[0-9a-zA-Z\\u4e00-\\u9fa5][_0-9a-zA-Z\\u4e00-\\u9fa5]+\$/;
                                  if(/\\s/.test(names)){msg = names+"含有空格！";}
                                  if(!reg.test(names)){msg = names+"含有非法字符或空格！";}
                                  return msg;
                               }
                             },
                    'APN':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'VPI':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'VCI':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'RED_ADDRESS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'RED_NETMASK':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'TELEPHONE':{
                               'type':'text',
                               'required':'0',
                               'check':'num|'
                             },
                    'USERNAME':{
                               'type':'text',
                               'required':'1',
                               'check':'name|'
                             },
                    'PASSWORD':{
                               'type':'password',
                               'required':'1'
                             },
                    'MSN':{
                               'type':'text',
                               'required':'0',
                               'check':'mail|'
                             },
                    'DEFAULT_GATEWAY':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'DNS1':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'DNS2':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|',
                               'ass_check':function(eve){
                                                        var msg;
                                                        var dns1 = eve._getCURElementsByName("DNS1","input","UPLINK_FORM")[0].value;
                                                        var dns2 = eve._getCURElementsByName("DNS2","input","UPLINK_FORM")[0].value;
                                                        if (dns1 == dns2) {
                                                          msg = "次DNS和主DNS不能相同"
                                                        }
                                                        return msg;
                                }
                             },
                    'MAC':{
                               'type':'text',
                               'required':'1',
                               'check':'mac|',
                               'ass_check':function(eve){
                                                        var msg;
                                                        var mac = eve._getCURElementsByName("MAC","input","UPLINK_FORM")[0].value;
                                                        var all_mac = eve._getCURElementsByName("eth_value","input","UPLINK_FORM")[0].value;
                                                        var eth = eve._getCURElementsByName("RED_DEV","select","UPLINK_FORM")[0].value;
                                                        mac = mac.toUpperCase();
                                                        var reg = eth+"="+mac;
                                                        var reg = eval("/"+reg+"/");
                                                        var mac = eval("/"+mac+"/");
                                                        if(!reg.test(all_mac) && mac.test(all_mac)){
                                                            msg = "MAC地址不能与其他网口MAC地址相同";
                                                        }
                                                        return msg;
                                }

                             },
                    'CONCENTRATORNAME':{
                               'type':'text',
                               'required':'0',
                               'check':'name|'
                             },
                    'SERVICENAME':{
                               'type':'text',
                               'required':'0',
                               'check':'name|'
                             },
                    'RECONNECT_TIMEOUT':{
                               'type':'text',
                               'required':'0',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg = ""; 
                                                        var mtu_num = eve._getCURElementsByName("RECONNECT_TIMEOUT","input","UPLINK_FORM")[0].value;
                                                        if (mtu_num > 60 || mtu_num < 1){
                                                            msg = "重试超时时间必须在1-60之间";
                                                        }
                                                        return msg;
                                                     }
                             },
                    'MTU':{
                               'type':'text',
                               'required':'0',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg = ""; 
                                                        var mtu_num = eve._getCURElementsByName("MTU","input","UPLINK_FORM")[0].value;
                                                        if (mtu_num > 5000 || mtu_num < 1){
                                                            msg = "MTU值必须在1-5000之间";
                                                        }
                                                        return msg;
                                                     }
                             },
                    'RED_IPS':{
                               'type':'textarea',
                               'required':'1',
                               'check':'other',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg = "";
                                                        var green = eve._getCURElementsByName("RED_ADDRESS","input","UPLINK_FORM")[0].value;
                                                        var green_mask = eve._getCURElementsByName("RED_NETMASK","select","UPLINK_FORM")[0].value;
                                                        var add = eve._getCURElementsByName("RED_IPS","textarea","UPLINK_FORM")[0].value;
                                                        var display = eve._getCURElementsByName("UPLINKADDRESS","div","UPLINK_FORM")[0].style.display;
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
                                                        if (display != "none"){
                                                            //把子网转换为数字
                                                            var mask_old="";
                                                            var maskArr = green_mask.split(".");
                                                            for(i = 0;i < 4;i++){
                                                                maskArr[i] = parseInt(maskArr[i]).toString(2);
                                                                maskArr[i] = maskArr[i].toString();
                                                                if(i == 0){
                                                                   mask_old = maskArr[i];
                                                                }
                                                                else{
                                                                   mask_old += maskArr[i];
                                                                }
                                                            }
                                                            mask_old = mask_old.indexOf(0);
                                                            if (mask_old > mask){
                                                                final_mask = mask;
                                                            }
                                                            else{
                                                              final_mask = mask_old;
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
                                                        }
                                                        else{
                                                            return msg;
                                                        }
                                                        
                               }
                             },
                    'CHECKHOSTS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|domain|'
                             }
                 }
         };
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("UPLINK_FORM");
    </script>
EOF
;
}
sub check_device() { #check if network device is already used, if yes uplink is disabled 
    if ($device_used{$par{'RED_DEV'}}) {
        if (($par{'ENABLED'} eq "on") && ($device_used{$par{'RED_DEV'}} ne $save)) {
            %info = get_uplink_info($device_used{$par{'RED_DEV'}});
            $notification = _("Could not Enable Uplink. Device <b>%s</b> is already used by <b>%s</b>", $par{'RED_DEV'}, $info{'NAME'});
            $par{'ENABLED'} = "";
        }
    }
}
sub check_tel($){
    my $tel = shift;
    if (($tel !~ /^\d+\-\d+$/) || ($tel !~/(\d){2,3}\-(\d){7,8}/)) {
		push(@errormessages, _("Telephone number format is wrong.You could add by this 028-12345678"));
        return;
    }
}
sub check_ips() {
    my $redip = "";
    if ($par{'RED_TYPE'} eq "STATIC" || ($par{'RED_TYPE'} eq "PPTP" && $par{'METHOD'} eq "STATIC")) {
        if ($par{'RED_ADDRESS'} eq "") {
            push(@errormessages, _("IP address must not be <b>empty</b>."));
            return;
        }
        if ($par{'RED_NETMASK'} eq "") {
            push(@errormessages, _("Netmask must not be <b>empty</b>."));
            return;
        }
        $redip = $par{'RED_ADDRESS'}.'/'.$par{'RED_NETMASK'};
    }
    else {
        $par{'RED_ADDRESS'} = "";
        $par{'RED_NETMASK'} = "";
    }
    ($red_ips, $nok_ips) = createIPS($redip, $par{'RED_IPS'});
    $par{'RED_IPS'} = $red_ips;
    #$red_ips = $ok_ips;
    if ($nok_ips eq "") {
        foreach my $invalid (@{checkNetaddress($red_ips)}) {
            push(@errormessages, _("The IP address '%s' is the same as its network address, which is not allowed!", $invalid));
        }
        foreach my $invalid (@{checkBroadcast($red_ips)}) {
            push(@errormessages, _("The IP address '%s' is the same as its broadcast address, which is not allowed!", $invalid));
        }
        foreach my $invalid (@{checkInvalidMask($red_ips)}) {
            push(@errormessages, _("The network mask of the IP address '%s' addresses only 1 IP address, which will lock you out if applied. Choose another one!", $invalid));
        }
    }
    else {
        foreach my $nokip (split(/,/, $nok_ips)) {
            push(@errormessages, _('The RED IP address or network mask "%s" is not correct.', $nokip));
        }
    }
    foreach my $uplink (keys %uplink_networks) {
        if ($uplink eq $par{'ID'} || $uplink_networks{$uplink} eq "") {
            next;
        }
        if (network_overlap($red_ips, $uplink_networks{$uplink},)) {
            push(@errormessages, _("The networks of this uplink are not distinct with \"%s\" networks.", $uplink));
        }
    }
    if (network_overlap($red_ips, $settings{'GREEN_IPS'},)) {
        push(@errormessages, _('The RED and GREEN networks are not distinct.'));
    }
    if (orange_used()) {
        if (network_overlap($red_ips, $settings{'ORANGE_IPS'},)) {
            push(@errormessages, _('The RED and ORANGE networks are not distinct.'));
        }
    }
    if (blue_used()) {
        if (network_overlap($red_ips, $settings{'BLUE_IPS'})) {
            push(@errormessages, _('The RED and BLUE networks are not distinct.'));
        }
    }
}

sub check_hosts() { #check if the checkhosts are valid
    if ($par{'CHECKHOSTS'} eq "") {
        push(@errormessages, _("'Check if these hosts are reachable' must not be empty!"));
        return;
    }
    @temp = split(/\n/,$par{'CHECKHOSTS'});
    foreach (@temp)    {
        s/^\s+//g; s/\s+$//g;
        if ($_) {
            chomp $_;
            if (!check_ip($_, "255.255.255.0") && !validdomainname($_) && $_ ne "") {
                push(@errormessages, _("'%s' is not a valid IP address or domain name!", $_));
                $show_advanced = true;
            }
        }
    }
}

sub check_apn() { #check if the apn is valid
    if ($par{'APN'} && !check_ip($par{'APN'}, "255.255.255.0") && !validdomainname($par{'APN'})) {
        push(@errormessages, _("Access Point Name: '%s' is not a valid IP address or domain name!", $_));
        $show_advanced = true;
    }
}

sub check_gateway() { #check if gateway is correct
    undef $valid;
    if ($par{'DEFAULT_GATEWAY'} eq "") {
        push(@errormessages, _("Default gateway must not be <b>empty</b>."));
    }
    elsif ($par{'RED_TYPE'} eq "NONE") {
        (my $valid, my $ip, my $mask) = check_ip($par{'DEFAULT_GATEWAY'}, '255.255.255.0');
        if (!$valid) {
            push(@errormessages, _('The gateway address is not correct.'));
        }
    }
    else {
        (my $valid, my $ip, my $mask) = check_ip($par{'DEFAULT_GATEWAY'}, '255.255.255.255');
        if (!$valid) {
            push(@errormessages, _('The gateway address is not correct.'));
            return @errormessages
        }
        if (network_overlap($settings{'GREEN_IPS'}, $par{'DEFAULT_GATEWAY'}. '/32')) {
            push(@errormessages, _('The DEFAULT GATEWAY is within the GREEN network.'));
        }
        if (orange_used()) {
            if (network_overlap($settings{'ORANGE_IPS'}, $par{'DEFAULT_GATEWAY'}. '/32')) {
                push(@errormessages, _('The DEFAULT GATEWAY is within the ORANGE network.'));
            }
        }
        if (blue_used()) {
            if (network_overlap($settings{'BLUE_IPS'}, $par{'DEFAULT_GATEWAY'}. '/32')) {
                push(@errormessages, _('The DEFAULT GATEWAY is within the BLUE network.'));
            }
        }
    }
}

sub check_dns() { #check if dns entries are valid
    undef $valid;
    if ($par{'DNS'} eq "on") {
        if ($par{'DNS1'} eq "" && $par{'DNS2'} eq "") {
            push(@errormessages, _("Primary DNS must not be <b>empty</b>."));
        }
        else {
            (my $valid, my $ip, my $mask) = check_ip($par{'DNS1'}, "255.255.255.255");
			my $valid = validip($par{'DNS1'});
            if (!$valid) {
                push(@errormessages, _('无效的主DNS.'));
            }
            elsif ($par{'DNS2'} eq "") { # if DNS1 is correct and DNS2 is empty DNS2 is set to DNS1
                #$par{'DNS2'} = $par{'DNS1'};
            }
			else{
				(my $valid, my $ip, my $mask) = check_ip($par{'DNS2'}, "255.255.255.255");
				my $valid = validip($par{'DNS2'});
				if (!$valid) {
					push(@errormessages, _('无效的次DNS.'));
				}
				elsif ($par{'DNS2'} eq "") {
					$par{'DNS1'} = $par{'DNS2'};
				}
       }	}
    }
}
#chenwu 2012  7 10
sub check_mac() { #check if mac address is valid
    if ($par{'MACACTIVE'} eq "on") {
        if ($par{'MAC'} eq "") {
            push(@errormessages, _("The MAC address must not be <b>empty</b>"));
            $show_advanced = true;
        }
        elsif (! validmac($par{'MAC'})) {
            push(@errormessages, _('MAC地址填写错误，请正确填写(十六进制)!', $par{'MAC'}));
            $show_advanced = true;
        }
    }
}

sub toggle_enable($$) {
    my $uplink = shift;
    my $enable = shift;
    if ($enable) {
        $enable = 'on';
    } else {
        $enable = 'off';
    }
    &readhash("$uplinkdir/$uplink/settings", \%settings);
    $settings{'ENABLED'} =  $enable;
    &writehash("$uplinkdir/$uplink/settings", \%settings );
	`sudo fmodify "$uplinkdir/$uplink/settings"`;
    system("sudo /etc/rc.d/uplinks stop $uplink");
}

sub save_uplink() {
    my $restart = 1;
    my %oldsettings = ();
    
    my %config = ();
    
    &readhash('/var/efw/ethernet/settings', \%settings);
    
    # check if it is the default profile
    if ($par{'NAME'} eq _("Main uplink")) {
        $save = "main";
        $name = _("Main uplink");
    }
    $save = $par{'ID'};
    if ($save eq "main" && $par{'NAME'} eq "") {
        $par{'NAME'} = _("Main uplink");
    }
    $old_name = $par{'OLD_NAME'};
    $name = $par{'NAME'};
    
    if ($save ne "main") {
        if ($name eq "") {
            $name = sprintf "%s $red_names{$par{'RED_TYPE'}}", _("Uplink");
        }
        elsif ($name eq _("Main uplink")) {
            $name = sprintf "%s $red_names{$par{'RED_TYPE'}}", _("Uplink");
        }
        if (($name ne $old_name)) {
            $i = 0;
            $exists = 1;
            $tmp_name = $name;
            while ($exists eq 1) {
                $exists = 0;
                foreach (@{get_uplinks()}) {
                    $u_info = get_uplink_info($_);
                    if ("$u_info{'NAME'}" eq "$name") {
                        $exists = 1;
                        $name = "$tmp_name $i";
                    }
                    $i++;
                }
            }
        }
    }
    $config{'NAME'} = $name;
    ##elvis 2011-12-27
	
	##end
    if ($save eq "") {
        $restart = 0;
        $tmpdir = "$uplinkdir/uplink";
        $i = 1;
        $dir = "$tmpdir$i";
        $save = "uplink$i";
        while ( -e "$dir/settings" && ! -z "$dir/settings") {
            $dir = "$tmpdir$i";
            $save = "uplink$i";
            $i++;
        }
        if (! (-d $dir)) {
            mkdir($dir);
        }
    }
    else {
        $dir = "$uplinkdir/$save";
        if (-e "$uplinkdir/$save/settings") {
            &readhash("$uplinkdir/$save/settings", \%oldsettings);
            $config{'DOWNLOAD'} = $oldsettings{'DOWNLOAD'};
            $config{'UPLOAD'} = $oldsettings{'UPLOAD'};
            $config{'SHAPING'} = $oldsettings{'SHAPING'};
        }
    }

    if ($par{'RED_IPS_ACTIVE'} ne "on") {
        $par{'RED_IPS'} = "";
    }
    if ($par{'BACKUPPROFILEACTIVE'} ne "on" || $par{'BACKUPPROFILE'} eq $par{'ID'}) {
        $par{'BACKUPPROFILE'} = "";
    }
    $config{'BACKUPPROFILE'} = $par{'BACKUPPROFILE'};
    if ($par{'LINKCHECK'} eq "on") {
        check_hosts();
    }
    $config{'LINKCHECK'} = $par{'LINKCHECK'};
    if ($par{'PROTOCOL'} eq "STATIC" || $par{'PROTOCOL'} eq "DHCP") {
        $config{'METHOD'} = $par{'PROTOCOL'};
        $config{'PROTOCOL'} = "RFC1483";
    }
    
    if ($par{'MACACTIVE'} ne "on") {
        $par{'MAC'} = "";
    }
    if ($par{'MTU'} ne "" && ($par{'MTU'} < 1|| $par{'MTU'}>5000)) {
        push(@errormessages, _('MTU值必须在1-5000之间.'));
    }
    if ($par{'RECONNECT_TIMEOUT'} ne "" && ! ($par{'RECONNECT_TIMEOUT'} =~ m/^\d+$/)) {
        push(@errormessages, _('超时重试时间必须输入整数.'));
    }
    if ($par{'RED_TYPE'} eq "NONE") {
        $config{'RED_DEV'} = "";
        if ($par{'CHECKHOSTS'} eq "") {
            $par{'CHECKHOSTS'} = "127.0.0.1";
        }
        $config{'CHECKHOSTS'} = $par{'CHECKHOSTS'};
        check_gateway();
        $config{'DEFAULT_GATEWAY'} = $par{'DEFAULT_GATEWAY'};
        $par{'DNS'} = "on";
        check_dns();
    }
    elsif ($par{'RED_TYPE'} eq "STATIC") {
        check_device();
        $config{'RED_DEV'} = $par{'RED_DEV'};
        check_ips();
        check_gateway();
        $config{'DEFAULT_GATEWAY'} = $par{'DEFAULT_GATEWAY'};
        $par{'DNS'} = "on";
        check_dns();
        check_mac();
        $config{'MAC'} = $par{'MAC'};
    }
    elsif ($par{'RED_TYPE'} eq "DHCP") {
        check_device();
        $config{'RED_DEV'} = $par{'RED_DEV'};
        $par{'RED_IPS'} = "";
        check_ips();
        check_dns();
        check_mac();
        $config{'MAC'} = $par{'MAC'};
    }
    elsif ($par{'RED_TYPE'} eq "PPPOE") {
        $config{'METHOD'} = "PPPOE";
        $config{'PROTOCOL'} = "RFC1483";
        check_device();
        $config{'RED_DEV'} = $par{'RED_DEV'};
        $config{'AUTH'} = $par{'AUTH'};
        check_ips();
        check_dns();
        check_mac();
        $config{'MAC'} = $par{'MAC'};
        $config{'CONCENTRATORNAME'} = $par{'CONCENTRATORNAME'};
        $config{'SERVICENAME'} = $par{'SERVICENAME'};
    }
    elsif ($par{'RED_TYPE'} eq "PPTP") {
        check_device();
        $config{'RED_DEV'} = $par{'RED_DEV'};
        $config{'METHOD'} = $par{'METHOD'};
        $config{'PHONENUMBER'} = $par{'TELEPHONE'};
        $config{'AUTH'} = $par{'AUTH'};
        check_ips();
		check_tel($par{'TELEPHONE'});
        if ($par{'METHOD'} eq "STATIC") {
            check_gateway();
            $config{'DEFAULT_GATEWAY'} = $par{'DEFAULT_GATEWAY'};
            $par{'DNS'} = "";
        }
        else {
            check_dns();
        }
        check_mac();
        $config{'MAC'} = $par{'MAC'};
    }
    elsif ($par{'RED_TYPE'} eq "ADSL") {
        $config{'RED_DEV'} = "";
        $config{'TYPE'} = $par{'ADSL_TYPE'};
        $config{'PROTOCOL'} = $par{'PROTOCOL'};
        $config{'METHOD'} = $par{'METHOD'};
        $config{'ENCAP'} = $par{'ENCAP'};
        
        check_ips();
        if ($par{'VCI'} eq "" || $par{'VPI'} eq "") {
            push(@errormessages, _("VCI and VPI must not be <b>empty</b>."));
        }
        if ($par{'VCI'} < 32 || $par{'VCI'} > 65535) {
            push(@errormessages, _("VCI must be between 32 and 65535."));
        }
        if ($par{'VPI'} < 0 || $par{'VPI'} > 255) {
            push(@errormessages, _("VPI must be between 0 and 255."));
        }
        $config{'VCI'} = $par{'VCI'};
        $config{'VPI'} = $par{'VPI'};
        
        if ($par{'PROTOCOL'} ne "RFC1483") {
            $config{'AUTH'} = $par{'AUTH'};
        }
        
        if ($par{'PROTOCOL'} eq "RFC1483" && $par{'METHOD'} eq "STATIC") {
            check_gateway();
            # with RFC1483 uplinksdaemon currently uses GATEWAY. will save DEFAULT_GATEWAY & GATEWAY in this case, so it also works in future
            $config{'GATEWAY'} = $par{'DEFAULT_GATEWAY'};
            $config{'DEFAULT_GATEWAY'} = $par{'DEFAULT_GATEWAY'};
            $par{'DNS'} = "on";
            check_dns();
        }
        elsif ($par{'PROTOCOL'} eq "RFC2364" || ($par{'PROTOCOL'} eq "RFC1483" && $par{'METHOD'} eq "PPPOE")) {
            check_dns();
        }
    }
    elsif ($par{'RED_TYPE'} eq "ISDN") {
        $config{'RED_DEV'} = "";
        $config{'TELEPHONE'} = $par{'TELEPHONE'};
        $config{'AUTH'} = $par{'AUTH'};
        $config{'MSN'} = $par{'MSN'};
        check_ips();
        check_dns();
		check_tel($par{'TELEPHONE'});
        $config{'TYPE'} = $par{'ISDN_TYPE'};
        $config{'TIMEOUT'} = $par{'RECONNECT_TIMEOUT'};
    }
    elsif ($par{'RED_TYPE'} eq "ANALOG") {
        $config{'RED_DEV'} = "";
        $config{'TELEPHONE'} = $par{'TELEPHONE'};
        $config{'COMPORT'} = $par{'COMPORT'};
        $config{'MODEMTYPE'} = $par{'MODEMTYPE'};
        $config{'SPEED'} = $par{'SPEED'};
        $config{'AUTH'} = $par{'AUTH'};
        check_ips();
        check_dns();
		check_tel($par{'TELEPHONE'});
        check_apn();
        $config{'APN'} = $par{'APN'};
        
    }

    if ($par{'DNS'} eq "") {
        $config{'DNS'} = "Automatic";
        $config{'DNS1'} = "";
        $config{'DNS2'} = "";
    }
    else {
        $config{'DNS'} = "Manuell";
        $config{'DNS1'} = $par{'DNS1'};
        $config{'DNS2'} = $par{'DNS2'};
    }
    # check if errormessage is empty if not show the errors and do not save.
    if (scalar(@errormessages) eq 0) {
        $config{'RED_TYPE'} = $par{'RED_TYPE'};        
        $config{'RED_ADDRESS'} = $par{'RED_ADDRESS'};
        $config{'RED_NETMASK'} = $par{'RED_NETMASK'};
        $config{'CIDR'} = $config{'RED_CIDR'};
        $config{'RED_IPS'} = $par{'RED_IPS'};
        $config{'USERNAME'} = $par{'USERNAME'};
        $config{'PASSWORD'} = $par{'PASSWORD'};
        $config{'RECONNECT_TIMEOUT'} = $par{'RECONNECT_TIMEOUT'};
        $config{'MTU'} = $par{'MTU'};
        
        @temp = split(/[\r\n,]/,$par{'CHECKHOSTS'});
        $par{'CHECKHOSTS'} = "";
        foreach (@temp) {
            if ($_) {
                chomp $_;
                if (/$_/ ne "") {
                    if ($par{'CHECKHOSTS'} eq "") {
                        $par{'CHECKHOSTS'} = $_;
                    }
                    else {
                        $par{'CHECKHOSTS'} = $par{'CHECKHOSTS'}.",".$_;
                    }
                }
            }
        }
        $config{'CHECKHOSTS'} = $par{'CHECKHOSTS'};
        
        if($par{'ENABLED'} ne "on") {
            $par{'ENABLED'} = "off";
        }
        $config{'ENABLED'} = $par{'ENABLED'};
        
        if($par{'MANAGED'} ne "on") {
            $par{'MANAGED'} = "off";
        }
        $config{'MANAGED'} = $par{'MANAGED'};
        
        if($par{'ONBOOT'} ne "on") {
            $par{'ONBOOT'} = "off";
        }
        $config{'ONBOOT'} = $par{'ONBOOT'};
        $config{'AUTOSTART'} = $par{'ONBOOT'};
		if (! (-d $dir)) {
            mkdir($dir);
        }
        &writehash("$dir/settings", \%config );
		`sudo fmodify "$dir/settings"`;
       
        if ($restart ne 0 && %oldsettings ne ()) {
            for my $key (keys %oldsettings) {
                if ($key eq "CHECKHOST" || $key eq "NAME" || $key eq "BACKUPPROFILE") {
                    next;
                }
                if ($oldsettings{$key} ne $config{$key}) {
                    $restart = 0;
                    last;
                }
            }
        }
        
        %par = ();
        if ($restart eq 0) {
            system("sudo /etc/rc.d/uplinks stop $save");
        }
    }
}

sub delete_uplink() {
    #iterate over all uplinks to check if the uplinks is used as backupuplink
    foreach (@{get_uplinks()}) {
        if ($_ ne $par{'ID'}) { # do not check if uplink is its own backupuplink
            my %backup_info = get_uplink_info($_);
            if ($backup_info{'BACKUPPROFILE'} eq $par{'ID'}) {
                %uplink_info = get_uplink_info($par{"ID"});
                $errormessage = "上行线路".$uplink_info{'NAME'}."已经被".$backup_info{'NAME'}."使用";
                return;
            }
        }
    }
    # delete uplink if it is not used as backupuplink
    system("sudo /etc/rc.d/uplinks stop $par{'ID'}");
    $rmdir = "$uplinkdir/$par{'ID'}";
    system("rm -R \"$rmdir\"");
	`sudo fdelete "$rmdir"`;
}

sub get_uplink_display() {
    $display{'uplinkeditor'} = "";
    $display{'folding_advanced'} = "";
    if (scalar(@errormessages) eq 0) {
        undef $disabled;
    }
    else {
        $display{'uplinkeditor'} = "showeditor";
        if ($show_advanced eq true) {
            $display{'folding_advanced'} = "open";
        }
    }
    if ($par{'RED_TYPE'} eq "") {
        $par{'RED_TYPE'} = "NONE";
    }
    if ($par{'RED_IPS_ACTIVE'} eq "on") {
        $checked{'RED_IPS_ACTIVE'} = "checked=\"checked\"";
    }
    if ($par{'MACACTIVE'} eq "on") {
        $checked{'MACACTIVE'} = "checked=\"checked\"";
    }
    if ($par{'DNS'} eq "on") {
        $checked{'DNS'} = "checked=\"checked\"";
    }
    if ($par{'MACACTIVE'} eq "on") {
        $checked{'MACACTIVE'} = "checked=\"checked\"";
    }
    if ($uplink ne "" || $#errormessages ne -1) {
        $button = _("Save");
        $selected{$par{'RED_TYPE'}} = "selected=\"selected\"";
    }
    else {
        $button = _("Save");
        $selected{'NONE'} = "selected=\"selected\"";
    }
    if ($par{'ENABLED'} eq "on") {
        $checked{'ENABLED'} = "checked=\”checked\""
    }
    if ($par{'MANAGED'} eq "on") {
        $checked{'MANAGED'} = "checked=\”checked\""
    }
    if ($par{'ONBOOT'} eq "on") {
        $checked{'ONBOOT'} = "checked=\”checked\""
    }
    if ($par{'BACKUPPROFILE'} ne "") {
        if (-e "${swroot}/uplinks/$par{'BACKUPPROFILE'}/settings") {
            $checked{'BACKUPPROFILEACTIVE'} = "checked=\"checked\"";
        }
    }
}

sub show_uplink_types() {
    printf <<EOF
    <div class="uplinktypes" id="uplinkdevice">
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
                <td><select class="form" name="RED_DEV">
EOF
    ,
    _("Device"),
    ;
    foreach $iface (@$ifaces) {
        if ($iface->{'device'} eq $par{'RED_DEV'}) {
            $selected = "selected=\"selected\"";
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$iface->{'device'}" $selected >$iface->{'shortlabel'}</option>
EOF
;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkisdntype" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
                <td><select class="form" name="ISDN_TYPE">
EOF
    ,
    _("ISDN modem"),
    ;
    foreach my $modem (@$isdn_modems) {
        my $caption = get_info('isdn', $modem);
        next if ($caption eq '');
        my $detected = '';
        if (detect('isdn', $modem) > 0) {
            $caption .= ' '.'-->'._('detected').'<--';
        }
        if ( $modem eq $par{'ISDN_TYPE'}) {
            $selected = "selected=\"selected\"";
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$modem" $selected>$caption</option>
EOF
        ,
        ;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkcomport" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
                <td><select class="form" name="COMPORT">
EOF
    ,
    _("Serial/USB Port"),
    ;
    foreach my $comport (@comports) {
        if ( $comport eq $par{'COMPORT'}) {
            $selected = "selected=\"selected\"";
        }
        else {
            undef $selected;
        }
        my $caption = $comport;
        $caption =~ s/\/dev\/tty//g; #make it more human readable
        $caption =~ s/^S/Serial Port /g;
        $caption =~ s/^USB/USB Port /g;
        printf <<EOF
                        <option value="$comport" $selected>$caption</option>
EOF
        ,
        ;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkmodemtype" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
                <td><select class="form" name="MODEMTYPE">
EOF
    ,
    _("Modem type"),
    ;
    foreach my $modem (@analog_modems) {
        my $caption = $analog_modem_names{$modem};
        if ( $modem eq $par{'MODEMTYPE'}) {
            $selected = "selected=\"selected\"";
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$modem" $selected>$caption</option>
EOF
        ,
        ;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkspeeds" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
                <td><select class="form" name="SPEED">
EOF
    ,
    _("Baud-rate"),
    ;
    foreach my $speed (@speeds) {
        if ($speed eq $par{'SPEED'}) {
            $selected = "selected=\"selected\""
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$speed" $selected>$speed</option>
EOF
        ,
        ;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkapn" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s</td>
                <td><input class="form" type="text" value="$par{'APN'}" name="APN"/></td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkprotocol" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%" >%s *</td>
				<td><select class="form" name="PROTOCOL">
EOF
    ,
    _("Access Point Name"),
    _("ADSL protocol"),
    ;
    foreach $protocol (@adsl_protocols) {
        if ($protocol eq $par{'PROTOCOL'} || ($par{'PROTOCOL'} eq "RFC1483" && $protocol eq $par{'METHOD'})) {
            $selected = "selected=\"selected\"";
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$protocol" $selected>$adsl_names{$protocol}</option>
EOF
        ,
        ;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkadsltype" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
                <td><select class="form" name="ADSL_TYPE">
EOF
    ,
    _("ADSL modem/router"),
    ;
    foreach my $modem (@$adsl_modems) {
        my $caption = get_info('adsl', $modem);
        next if ($caption eq '');
        my $detected = '';
        if (detect('adsl', $modem) > 0) {
            $caption .= ' '.'-->'._('detected').'<--';
            $selected = "selected=\"selected\"";
        }
        if ( $modem eq $par{'ADSL_TYPE'}) {
            $selected = "selected=\"selected\"";
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$modem" $selected>$caption</option>
EOF
        ,
        ;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkmethod" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
                <td><select class="form" name="METHOD">
EOF
    ,
    _("PPTP method"),
    ;
    foreach $method (@pptp_methods) {
        if ($method eq $par{'METHOD'}) {
            $selected = "selected=\"selected\""
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$method" $selected>$pptp_names{$method}</option>
EOF
        ,
        ;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkvcivpi" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">VPI *</td><td><input class="form" type="text" maxlenght="3" size="5" value="$par{'VPI'}" name="VPI"/></td></tr>
            <tr class="odd"><td class="sub_td_type"   width="20%">VCI *</td><td><input class="form" type="text" maxlength="5" size="5" value="$par{'VCI'}" name="VCI"/></td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkencap" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
                <td><select class="form" name="ENCAP">
EOF
    ,
    _("Encapsulation type"),
    ;
    for (my $type=0; $type<4; $type++) {
        if ($type eq $par{'ENCAP'}) {
            $selected = "selected=\"selected\""
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$type" $selected>$encap_names{$type}</option>
EOF
        ,
        ;
    }
my @mask = ("0.0.0.0",
	        "128.0.0.0",
			"192.0.0.0",
			"224.0.0.0",
			"240.0.0.0",
			"248.0.0.0",
			"252.0.0.0",
			"254.0.0.0",
			"255.0.0.0",
			"255.128.0.0",
			"255.192.0.0",
			"255.224.0.0",
			"255.240.0.0",
			"255.248.0.0",
			"255.252.0.0",
			"255.254.0.0",
			"255.255.0.0",
			"255.255.128.0",
			"255.255.192.0",
			"255.255.224.0",
			"255.255.240.0",
			"255.255.248.0",
			"255.255.252.0",
			"255.255.254.0",
			"255.255.255.0",
			"255.255.255.128",
			"255.255.255.192",
			"255.255.255.224",
			"255.255.255.240",
			"255.255.255.248",
			"255.255.255.252",
			"255.255.255.254",
			"255.255.255.255"
		);
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div name="UPLINKADDRESS" class="uplinktypes" id="uplinkaddress" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
				<td><input class="form" type="text" maxlength="15" size="15"  name="RED_ADDRESS" /></td>
             </tr>
			 <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
				<td>
				<select id="red_mask" name="RED_NETMASK">
EOF
,_("IP address")
, _("Netmask")
;
foreach my $masks(@mask){
		print "<option value='".$masks."'>".$masks."</option>";
}
printf <<EOF
</select> 
</td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkipsactive" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%"><input class="form" type="checkbox" style="margin-left:0px;" name="RED_IPS_ACTIVE" $checked{'RED_IPS_ACTIVE'}/>&nbsp;%s</td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkips" >
        <table width="100%" >
            <tr class="odd">
                <td class="sub_td_type"   width="20%">
                <textarea class="form" cols="30" rows="6" style="padding: 0px;" name="RED_IPS">$par{'RED_IPS'}</textarea>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkphonenumber" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s</td>
				<td><input class="form" type="text" value="$par{'TELEPHONE'}" name="TELEPHONE"/></td>
            </tr>
        </table>
    </div>  
    <div class="uplinktypes" id="uplinkuserpass" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s</td>
				<td><input class="form" type="text" value="$par{'USERNAME'}" name="USERNAME"/></td>
				</tr>
				<tr class="odd">

                <td class="sub_td_type"   width="20%">%s</td>
				<td><input class="form" type="password" value="$par{'PASSWORD'}" name="PASSWORD"/></td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkmsn" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s</td>
				<td><input class="form" type="text" value="$par{'MSN'}" name="MSN"/></td>
               
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkauth" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
				<td>
                    <select class="form" name="AUTH">
EOF
    ,
    _("Add additional addresses (one IP/Netmask or IP/CIDR per line)"),
    _("Phone number"),
    _("Username"),
    _("Password"),
    _("Caller ID/MSN"),
    _("Authentication method"),
    ;
    foreach my $auth (@auth_types) {
        if ($auth eq $par{'AUTH'}) {
            $selected = "selected=\"selected\""
        }
        else {
            undef $selected;
        }
        printf <<EOF
                        <option value="$auth" $selected>$auth_names{$auth}</option>
EOF
        ,
        ;
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkgateway" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
				<td><input class="form" type="text" value="$par{'DEFAULT_GATEWAY'}" name="DEFAULT_GATEWAY"/></td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkdns" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%"><input class="form" type="checkbox" style="margin:0px;" name="DNS" $checked{'DNS'}/>&nbsp;%s</td>
            </tr>
        </table>
    </div>
    <div class="uplinktypes" id="uplinkmanualdns" >
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td class="sub_td_type"   width="20%">%s *</td>
				<td><input class="form" type="text" value="$par{'DNS1'}" name="DNS1"/></td>
			</tr>
			<tr class="odd">
                <td class="sub_td_type"   width="20%">%s</td>
				<td><input class="form" type="text" value="$par{'DNS2'}" name="DNS2"/></td>
            </tr>
        </table>
    </div>
    
EOF
    ,
    _("Default gateway"),
    _("Use custom DNS settings"),
    _("Primary DNS"),
    _("Secondary DNS"),
    ;
}

sub show_uplink_advanced() {
    print get_folding("advanced", "start", _("Advanced settings"), $display{'folding_advanced'});
    printf <<EOF
        <div class="uplinktypes" id="uplinkmacactive" border ="0">
            <table width="100%" border ="0" cellpadding="0" cellspacing="0">
                <tr>
                    <td colspan="5" style="padding-bottom: 0px;"><input class="form" type="checkbox" style="margin:0px;" name="MACACTIVE" $checked{'MACACTIVE'}/>&nbsp;%s</td>
                </tr>
            </table>
        </div>
        <div class="uplinktypes" id="uplinkmac" border ="0">
            <table width="100%" border ="0" cellpadding="0" cellspacing="0">
                <tr>
                    <td><input class="form" type="text" value="$par{'MAC'}" maxlength="17" size="17" name="MAC" /> *</td>
                </tr>
            </table>
        </div>
        <div class="uplinktypes" id="uplinkconcentrator" border ="0">
            <table width="100%" border ="0" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="width: 100px;">%s &nbsp;<input class="form" type="text" value="$par{'CONCENTRATORNAME'}" name="CONCENTRATORNAME"/></td>
                    
                    <td style="width: 100px;">%s &nbsp;<input class="form" type="text" value="$par{'SERVICENAME'}" name="SERVICENAME"/></td>
                </tr>
            </table>
        </div>
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr>
                <td style="width: 100px;">%s &nbsp;<input class="form" type="text"  name="RECONNECT_TIMEOUT" value="$uplink_info{'RECONNECT_TIMEOUT'}"></td>
               
                <td style="width: 100px;">%s &nbsp;<input class="form" type="text"  name="MTU" value="$uplink_info{'MTU'}"></td>
            </tr>
        </table>
EOF
    ,
    _("Use <b>custom</b> MAC address"),
    _("Concentrator name"),
    _("Service name"),
    _("Reconnection timeout"),
    _("MTU"),
    ;
    print get_folding();
}

sub show_uplink() {
    openeditorbox("添加上行线路", _("Uplink editor"), $display{'uplinkeditor'}, "createuplink", );

    printf <<EOF
EOF
    ,
    ;
    if ($uplink ne "main") {
        printf <<EOF
        </form>
     <form name="UPLINK_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
        <input type="hidden" name="ACTION" value="save" />
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="env">
                <td class="add-div-type" rowspan = "1">%s</td>
                <td>
                    <input class="form" type="text" name="NAME" value="$par{'NAME'}" maxlength="20" />
                    <input class="form" type="hidden" name="OLD_NAME" value="$par{'OLD_NAME'}"/>
                    <input class="form" type="hidden" name="ID" value="$par{'ID'}"/>
                    <input class="hidden" type="text" name="eth_value" value="$last_eth_value" /> 
                </td>
            </tr>
EOF
        ,
        _("Description"),
        ;
    }
    printf <<EOF
            <tr class="odd">
                <td class="add-div-type" rowspan = "1">%s *</td>
                <td>
                    <select class="form" name="RED_TYPE" id="type_chooser" style="width:156px">
EOF
        ,
        _("Type"),
        ;
        foreach $type (@red_types) {
            if ($type eq $par{'RED_TYPE'}) {
                $selected = "selected=\"selected\"";
            }
            else {
                undef $selected;
            }
            if ($red_names{$type} eq "网关") {
				# bug:1714 建议修改为'单臂，旁路'
              #$red_names{$type} = "Gateway";
              $red_names{$type} = "透明网关";
            }
            if ($red_names{$type} eq "以太网DHCP") {
              $red_names{$type} = "DHCP";
            }
            if ($red_names{$type} eq "以太网静态(地址)") {
              $red_names{$type} = "Static";
            }
            printf <<EOF
                    <option value="$type" $selected>$red_names{$type}</option>
EOF
            ,
            ;
        }
        printf <<EOF
                    </select>
                    <input class="form" type="hidden" name="OLD_RED_TYPE" value="$par{'OLD_RED_TYPE'}" />
                </td>
            </tr>
		<tr><td class="add-div-type"></td><td>

EOF
    ,
    ;
    show_uplink_types();
    printf <<EOF
    <table width="100%" border ="0" cellpadding="0" cellspacing="0">
        <tr class="odd sub_td_type" >
            <td><input class="form" type="checkbox" style="margin:0px;" name="ENABLED" $checked{'ENABLED'}/>&nbsp;%s</td>
            <td><input class="form" type="checkbox" style="margin:0px;" name="ONBOOT" $checked{'ONBOOT'} />&nbsp;%s</td>
            <td><input class="form" type="checkbox" style="margin:0px;" name="MANAGED" $checked{'MANAGED'}/>&nbsp;%s</td>
        </tr>
    </table>
EOF
    ,
    _("Uplink is enabled"),
    _("Start uplink on boot"),
    _("Uplink is managed")
    ;
    
    if (@uplinklist <= 0) {
        $disabled = "disabled=\"disabled\"";
    }
    printf <<EOF
   
    <table width="100%" border ="0" cellpadding="0" cellspacing="0">
        <tr class="odd sub_td_type">
            <td colspan="5">
                $uplink
                <input class="form" type="checkbox" style="margin:0px;" name="BACKUPPROFILEACTIVE" $disabled $checked{'BACKUPPROFILEACTIVE'} />
                &nbsp;%s
                <select class="form" name="BACKUPPROFILE" $disabled style="width:128px;">
EOF
    ,
    _("如果此上行线路启用失败，则使用"),
    ;

    foreach $backup (@uplinklist) {
        #if ($backup ne $uplink) {
            foreach $b (@uplinklist) {
                if ($b eq $backup) {
                    %backup_info = get_uplink_info($b);
                }
                if ($backup eq $par{'BACKUPPROFILE'}) {
                    $selected = "selected=\"selected\"";
                    last;
                }
                else {
                    undef $selected;
                }
            }
            printf <<EOF
                        <option value="$backup" $selected>$backup_info{'NAME'} ($backup)</option>
EOF
            ,
            ;
        #}
    }
    printf <<EOF
                    </select>
                </td>
            </tr>
            <tr class="odd sub_td_type">
                <td><input class="form" type="checkbox" style="margin:0px;" name="LINKCHECK" $checked{'LINKCHECK'} /> %s</td>
            </tr>
        </table>
        <div id="uplinkcheckhosts" >
            <table>
                <tr class="odd sub_td_type">
                    <td vlign="top">
                        <textarea class="form" cols="30" rows="3" name="CHECKHOSTS">$par{'CHECKHOSTS'}</textarea>
					&nbsp;&nbsp;%s
					</td>
                </tr>
            </table>
        </div>
        
EOF
,_("Check if these hosts are reachable")
,_("Please input IP address or domain name")
;
    
    
    printf <<EOF
    </div>
    <input type="hidden" name="createbutton" value="%s" />
    <input type="hidden" name="updatebutton" value="%s" />
    </div>
	</td></tr><tr ><td style="border-top:1px solid #999;border-bottom:1px solid #999;"  class="add-div-type">%s</td><td  >
EOF
,
 _("Create Uplink"),
_("Update Uplink"),
_("Advanced settings")
;

printf <<EOF
<div class="uplinktypes" id="uplinkmacactive" border ="0">
	<table width="100%" border ="0" cellpadding="0" cellspacing="0">
        <tr class="odd">
            <td width="50%"><input class="form" type="checkbox" style="margin:0px;" name="MACACTIVE" $checked{'MACACTIVE'}/>&nbsp;%s</td>
			<td><div class="uplinktypes" id="uplinkmac" border ="0">
<input class="form" type="text" value="$par{'MAC'}" maxlength="17" size="17" name="MAC" /> *
</div></td>
        </tr>
	</table>
</div>



<div class="uplinktypes" id="uplinkconcentrator" border ="0">
    <table width="100%" border ="0" cellpadding="0" cellspacing="0">
        <tr class="odd">
            <td width="50%">%s &nbsp;<input class="form" type="text" value="$par{'CONCENTRATORNAME'}" name="CONCENTRATORNAME"/></td>
                    
            <td style="width: 100px;">%s &nbsp;<input class="form" type="text" value="$par{'SERVICENAME'}" name="SERVICENAME"/></td>
        </tr>
    </table>
</div>
        <table width="100%" border ="0" cellpadding="0" cellspacing="0">
            <tr class="odd">
                <td width="50%">%s &nbsp;<input class="form" type="text"  name="RECONNECT_TIMEOUT" value="$uplink_info{'RECONNECT_TIMEOUT'}" maxlength="20" /></td>
               
                <td style="width: 100px;">%s &nbsp;<input class="form" type="text"  name="MTU" value="$uplink_info{'MTU'}" maxlength="20" /></td>
            </tr>
        </table>
EOF
    ,
    _("Use <b>custom</b> MAC address"),
    _("Concentrator name"),
    _("Service name"),
    _("超时重试"),
    _("MTU"),
    ;
printf <<EOF
	</td></tr></table>
EOF
;
    &closeeditorbox($button, _("Cancel"), "uplinkbutton", "createuplink", $ENV{'SCRIPT_NAME'});
}

sub show_uplinklist() {
    #openbox('100%', "center", _("Current uplinks"));
    show_uplink();
    @uplinklist = @{get_uplinks()};
    if (scalar(@uplinklist) >= 0) {
        printf <<EOF
    <table class="ruleslist" id="ruleslist" width="100%" cellspacing="0" cellpadding="0">
        <tr>
            <td class="boldbase">%s</td>
            <td class="boldbase" width="30%">%s</td>
            <td class="boldbase" width="16%">%s</td>
            <td class="boldbase" width="30%">%s</td>
            <td class="boldbase" width="10%">%s</td>
        </tr>
EOF
        ,
        _("上行线路"),
        _("Description"),
        _("Type"),
        _("Backup-link"),
        _("Actions"),
        ;
        $count = 0;
        foreach $uplink (@uplinklist) {
            %uplink_info = get_uplink_info($uplink);
            
            my ($primary, $ip, $mask, $cidr) = getPrimaryIP($uplink_info{'RED_IPS'});
            $uplink_info{'RED_ADDRESS'} = $ip;
            $uplink_info{'RED_NETMASK'} = $mask;
            $uplink_info{'CIDR'} = $cidr;
            $uplink_info{'MACACTIVE'} = $uplink_info{'MAC'} eq "" ? "" : "on";
            if ($uplink_info{'RED_TYPE'} eq "STATIC" || $uplink_info{'RED_TYPE'} eq "PPTP") {
                $uplink_info{'RED_IPS'} = getAdditionalIPs($uplink_info{'RED_IPS'});
            }
            if ($uplink_info{'RED_TYPE'} eq "PPTP") {
                $uplink_info{'TELEPHONE'} = $uplink_info{'PHONENUMBER'};
            }
            if ($uplink_info{'RED_TYPE'} eq "ISDN") {
                $uplink_info{'ISDN_TYPE'} = $uplink_info{'TYPE'};
            }
            my $enabled_gif = $DISABLED_PNG;
            my $enabled_alt = _('Disabled (click to enable)');
            my $enabled_action = 'enable';
            if ($uplink_info{'ENABLED'} eq 'on') {
                $enabled_gif = $ENABLED_PNG;
                $enabled_alt = _('Enabled (click to disable)');
                $enabled_action = 'disable';
            }
            if ( $count % 2 eq 1 ) {
                $color = "even";
            }
            else {
                $color = "oodd";
            }
            $count++;

            printf <<EOF
        <tr class="$color" id="row_$uplink">
            <td>$uplink</td>
            <td>$uplink_info{'NAME'}</td>
            <td>$red_names{$uplink_info{'RED_TYPE'}}</td>
            <td>$uplink_info{'BACKUPPROFILENAME'}</td>
            <td class="actions" style="text-align:center">
                <form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:none;display:inline-block">
                  <input class='imagebutton' type='image' name="submit" src="$enabled_gif" alt="$enabled_alt" style="display:inline-block;float:none"/>
                  <input TYPE="hidden" name="ACTION" value="$enabled_action">
                  <input TYPE="hidden" name="ID" value="$uplink">
                </form>
                <input class="imagebutton" type="image" name="edituplink" value="$uplink" src="$EDIT_PNG" alt="%s" title="%s" onclick="disedit(event)" style="display:inline-block;float:none"/>
                <input type="hidden" class="$uplink" name="rowcolor" value="$color" />
EOF
            ,
            _("Edit"),
            _("Edit uplink"),
            ;
            for $key (keys %uplink_info) {
                if ($key eq "DNS") {
                    if ($uplink_info{$key} eq "Automatic") {
                        $uplink_info{$key} = "off";
                    }
                    else {
                        $uplink_info{$key} = "on";
                    }
                }
                printf <<EOF
                <input type="hidden" class="$uplink" id="$uplink$key" name="$key" value="$uplink_info{$key}" />
EOF
                ;
            }

            if ($uplink ne "main") {
                printf <<EOF
                <form enctype="multipart/form-data" method="post" onsubmit="return confirm('%s');" action="$ENV{SCRIPT_NAME}" style="display:inline-block">
                    <input type="hidden" name="ACTION" value="delete" />
                    <input type="hidden" name="ID" value="$uplink" />
                    <input class="imagebutton" type="image" name="submit" src="$DELETE_PNG" alt="%s" title="%s" />
                </form>
EOF
                ,
                _("Do you really want to delete this uplink?"),
                _("Remove"),
                _("Remove uplink"),
                ;
            }
            printf <<EOF
            </td>
        </tr>
EOF
;
        }
        printf <<EOF
    </table>
    <input type="hidden" name="default_checkhosts" value="" />
EOF
        ;
        printf <<EOF
    <table class="list-legend" cellspacing="0" cellpadding="0">
        <tr>
            <td class="boldbase">&nbsp; <b>%s:</b>
            <IMG SRC="$ENABLED_PNG" alt="%s" />
            %s
            <IMG SRC='$DISABLED_PNG' ALT="%s" />
            %s
            <img src='$EDIT_PNG' alt="%s" />
            %s
            <img src="$DELETE_PNG" alt="%s" />
            %s</td>
        </tr>
    </table>
	<br /><br />
EOF
        ,
        _('Legend'),
        _('Enabled (click to disable)'),
        _('Enabled (click to disable)'),
        _('Disabled (click to enable)'),
        _('Disabled (click to enable)'),
        _('Edit'),
        _('Edit'),
        _('Delete'),
        _('Delete'),
        ;
    }
    else {
        printf <<EOF
    <table>
        <tr>
            <td><i>%s</></td>
        </tr>
    </table>
	<br /><br />
EOF
        ,
        _("No uplinks available"),
        ;
    }
    #&closebox();

}

sub reload_par() {
    getcgihash( \%par );
    if ($par{'BACKUPPROFILEACTIVE'} ne "on") {
        $par{'BACKUPPROFILE'} = "";
    }
    $par{'RED_IPS'} =~ s/,/\n/g;
    $par{'CHECKHOSTS'} =~ s/,/\n/g;
    @uplinklist = @{get_uplinks()};
}


$notification = "";

&showhttpheaders();
reload_par();

for my $uplink (@uplinklist) {
    my %tmp = get_uplink_info($uplink); #check if maximum amount of the red_type is reached
    if ($allow{$tmp{'RED_TYPE'}} > 0) {
        $allow{$tmp{'RED_TYPE'}}--;
    }
    $uplink_networks{$uplink} = $tmp{'RED_IPS'};
    if ($tmp{'ENABLED'} eq "on") {  #check which devices are already used
        if (($tmp{'RED_TYPE'} eq "STATIC") || ($tmp{'RED_TYPE'} eq "DHCP") || ($tmp{'RED_TYPE'} eq "PPPOE") || ($tmp{'RED_TYPE'} eq "PPTP")) {
            $device_used{$tmp{'RED_DEV'}} = $uplink;
        }
    }
}

&openpage(_('Uplinks configuration'), 1, $refresh);

if ( $par{'ACTION'} eq "save" ) {
# ----------------------------------------------------------------
# save uplink
# ----------------------------------------------------------------
    save_uplink();
    reload_par();
    %par = ();
}

elsif ( $par{'ACTION'} eq "enable" ) {
# ----------------------------------------------------------------
# delete uplink
# ----------------------------------------------------------------
    toggle_enable($par{'ID'}, 1);
    reload_par();
}
elsif ( $par{'ACTION'} eq "disable" ) {
# ----------------------------------------------------------------
# delete uplink
# ----------------------------------------------------------------
    toggle_enable($par{'ID'}, 0);
    reload_par();
}
elsif ( $par{'ACTION'} eq "delete" ) {
# ----------------------------------------------------------------
# delete uplink
# ----------------------------------------------------------------
    delete_uplink();
    reload_par();
}

if ($notification ne "") {
    notificationbox($notification);
}

foreach my $line(@errormessages)
{
	$errormessage .= $line."<br />";
}

&openbigbox($errormessage, $warnmessage, $notemessage);
&readhash("/etc/uplinksdaemon/uplinksdaemon.conf", \%default);

get_uplink_display();

show_uplinklist();
check_form();
&closepage();
