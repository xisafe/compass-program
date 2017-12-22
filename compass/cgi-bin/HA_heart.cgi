#!/usr/bin/perl

#file:HA_heart.cgi
#author:ailei
#date:2013-11-11


require '/var/efw/header.pl';

my $heart_config="${swroot}/HA/heartdev";
my $backup_config="${swroot}/HA/backupdev";

my $extraheader="";
my @errormessages=();

my $action;
my %par;
my $loadflag = 0;

my @mask = (
       "128.0.0.0","192.0.0.0","224.0.0.0","240.0.0.0","248.0.0.0","252.0.0.0",
	   "254.0.0.0","255.0.0.0","255.128.0.0","255.192.0.0","255.224.0.0","255.240.0.0",
	   "255.248.0.0","255.252.0.0","255.254.0.0","255.255.0.0","255.255.128.0","255.255.192.0",
	   "255.255.224.0","255.255.240.0","255.255.248.0","255.255.252.0","255.255.254.0","255.255.255.0",
	   "255.255.255.128","255.255.255.192","255.255.255.224","255.255.255.240","255.255.255.248","255.255.255.252",
	   "255.255.255.254","255.255.255.255"
);
my %masknumber = (
			"128.0.0.0" => "/1",
			"192.0.0.0" => "/2",
			"224.0.0.0" => "/3",
			"240.0.0.0" => "/4",
			"248.0.0.0" => "/5",
			"252.0.0.0" => "/6",
			"254.0.0.0" => "/7",
			"255.0.0.0" => "/8",
			"255.128.0.0" => "/9",
			"255.192.0.0" => "/10",
			"255.224.0.0" => "/11",
			"255.240.0.0" => "/12",
			"255.248.0.0" => "/13",
			"255.252.0.0" => "/14",
			"255.254.0.0" => "/15",
			"255.255.0.0" => "/16",
			"255.255.128.0" => "/17",
			"255.255.192.0" => "/18",
			"255.255.224.0" => "/19",
			"255.255.240.0" => "/20",
			"255.255.248.0" => "/21",
			"255.255.252.0" => "/22",
			"255.255.254.0" => "/23",
			"255.255.255.0" => "/24",
			"255.255.255.128" => "/25",
			"255.255.255.192" => "/26",
			"255.255.255.224" => "/27",
			"255.255.255.240" => "/28",
			"255.255.255.248" => "/29",
			"255.255.255.252" => "/30",
			"255.255.255.254" => "/31",
			"255.255.255.255" => "/32",
);
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'HA_FORM',
       'option'   :{
                    'heart_IP':{
                               'type':'text',
                               'required':'1',
                               'check':'ip',
                             },
					'peer_IP':{
                               'type':'text',
                               'required':'1',
                               'check':'ip',
                             },
					'HA_device':{
                               'type':'text',
                               'required':'1',
                               'check':'',
							   'ass_check':function(eve){
								                        var msg="";
                                                        var ha_device = eve._getCURElementsByName("HA_device","input","HA_FORM")[0].value;
														if(ha_device eq 'choose')
	                                                    {
															 msg = '请选择HA心跳口';
                                                        }
														return msg;
                                                     }
                             },							 
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("SERVERS_FORM");
    </script>
EOF
;
}


sub get_backup_eth()
{
	my %backup_eth;
	if ( -f $backup_config) {
		my %backup_hash;
		&readhash($backup_config,\%backup_hash);

		my @backup_interface = split(/&/,$backup_hash{'HA_DEVS'});
	
		foreach my $backup(@backup_interface)
		{
			chomp($backup);
			$backup =~ s/[\r\n]//g;
			$backup_eth{$backup} = $backup;
		}
	}
	return %backup_eth;
}

sub get_red_eth()
{
	my %red_eth;
	my @red_interface;
	my $dir = "/var/efw/uplinks/";
	opendir (DIR, $dir) or die  _("can’t open the directory!");
	@red_interface = readdir DIR;
	closedir(DIR);
	
	foreach my $red(@red_interface)
	{
		if($dir !~ /^\./ && -f $dir."/".$red."/settings")
		{
			 my $settings = $dir."/".$red."/settings";
			 my %conf_hash = ();
			 readhash($settings,\%conf_hash);
			 my $eth = $conf_hash{'RED_DEV'};
			 $red_eth{$eth} = $eth;
		}
	}

	return %red_eth;
}

sub get_color_eth()
{
	my %color_eth;
	my @red_interface;
	my $dir = "/var/efw/ethernet/";
	my $settings = $dir."settings";
	my ($green_br, $orange_br, $blue_br);
	opendir (DIR, $dir) or die  _("can’t open the directory!");
	if($dir !~ /^\./ && -f $settings)
	{
		my %conf_hash = ();
		readhash($settings,\%conf_hash);

		$green_br = $conf_hash{'GREEN_DEV'};
		$orange_br = $conf_hash{'ORANGE_DEV'};
		$blue_br = $conf_hash{'BLUE_DEV'};

		my $green_file = $dir.$green_br;
		my $orange_file = $dir.$orange_br;
		my $blue_file = $dir.$blue_br;

		$color_eth{$green_br} = $green_br;
		$color_eth{$orange_br} = $orange_br;
		$color_eth{$blue_br} = $blue_br;

		if (-e $green_file) {
			open (FILE,"$green_file");
            foreach my $line (<FILE>) {
				chomp($line);
				$line =~ s/[\r\n]//g;
				$color_eth{$line} = $line;
			}
			close (FILE);
		}
		if (-e $orange_file) {
			open (FILE,"$orange_file");
            foreach my $line (<FILE>) {
				chomp($line);
				$line =~ s/[\r\n]//g;
				$color_eth{$line} = $line;
			}
			close (FILE);
		}
		if (-e $blue_file) {
			open (FILE,"$blue_file");
            foreach my $line (<FILE>) {
				chomp($line);
				$line =~ s/[\r\n]//g;
				$color_eth{$line} = $line;
			}
			close (FILE);
		}
	}

	return %color_eth;
}

sub get_all_eth()
{
	my $temp_cmd = `ip a`;
	my %all_hash;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
		{
			$all_hash{$1} = $1;
		}
	}
	return %all_hash;
}


sub get_heart_interface()
{
	my %all_interface = get_all_eth();
	my %red_interface = get_red_eth();
	my %color_interface = get_color_eth();
	my %backup_interface = get_backup_eth();
	delete ($all_interface{'lo'});

	foreach my $temp_eth(keys %all_interface)
    {
		foreach my $red_eth(keys %red_interface)
		{
			if($temp_eth eq $red_eth)
			{
				 delete ($all_interface{$red_eth});
			}
		}

		foreach my $color_eth(keys %color_interface)
		{
			if($temp_eth eq $color_eth)
			{
				 delete ($all_interface{$color_eth});
			}
		}

		foreach my $backup_eth(keys %backup_interface)
		{
			if($temp_eth eq $backup_eth)
			{
				 delete ($all_interface{$backup_eth});
			}
		}

		if ( $temp_eth !~ /^eth/) {
			delete ($all_interface{$temp_eth});
		}

		if ( $temp_eth =~ /\./) {
			delete ($all_interface{$temp_eth});
		}
    }
	return %all_interface;
	
}

sub modify_HA($$$$$)
{
	my $devicename = shift;
	my $ipaddress = shift;
	my $ipmask=shift;
    my $peerip = shift;
	my $enable = shift;

	my %newHA;

	if ($enable eq '') {
		$enable = 'off';
	}

	$newHA{'HEARTENABLED'} = $enable;
	$newHA{'HEARTDEV'} = $devicename;
	$newHA{'HEART_IP'} = $ipaddress;
	$newHA{'HEART_NETMASK'} = $ipmask;
	$newHA{'HEARTPEER_IP'} = $peerip;

	&writehash($heart_config,\%newHA);
}



sub display_HA() {
    my ($HA_device, $heart_IP, $netmask, $peer_IP, $checked);
	my %HA_hash;

	my %heart_interface = get_heart_interface();

    if (-e $heart_config) {
		&readhash($heart_config,\%HA_hash);
    }
    
	$HA_device = $HA_hash{'HEARTDEV'};
    $heart_IP = $HA_hash{'HEART_IP'};
	$netmask = $HA_hash{'HEART_NETMASK'};
	$peer_IP = $HA_hash{'HEARTPEER_IP'};
	$checked = $HA_hash{'HEARTENABLED'};

    if(!$checked || $checked =~/^on$/){
		$checked = 'checked';
	}
	elsif($checked = /^off$/){
		$checked = '';
	}
	openbox('100%', 'left', _('HA心跳口配置'));

    printf <<EOF
    </form>
    <form name="HA_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>

	<input type="hidden" name="ACTION" value="save">
    <table width="100%" >
			<tr class="odd">
		          <td class="add-div-type">HA心跳口<font color="red" size = "3px">*</font></td>
				  <td><select name="HA_device" onchange="" onkeyup="" style = "width:6%;">
EOF
;
				  my $flag = 0;
                  foreach my $temp_eth(keys %heart_interface){
	                  if($temp_eth eq $HA_device)
	                  {
						  $flag = 1;
		                  print "<option  selected value='$temp_eth'>$temp_eth</option>";
	                  }else{
		                  print "<option value='$temp_eth'>$temp_eth</option>";
	                  }
                   }
				   if($flag == 0)
				   {
						  print "<option  selected value='choose'>请选择</option>";
				   }
                          
       printf<<EOF
	   	         </select>
	             </td>	  
			</tr>
			<tr class="env">
		          <td class="add-div-width">心跳口IP<font color="red" size = "3px">*</font></td>
				  <td><input type = 'text'  name = "heart_IP" style = "width:106px;" value= "$heart_IP">
				  </td> 
		    </tr>
			<tr class="odd">
		          <td class="add-div-type">子网掩码<font color="red" size = "3px">*</font></td>
				  <td><select name="netmask" onchange="" onkeyup="" style = "width:147px;">
EOF
;
                  foreach my $themask (@mask) {
	                  if($themask eq $netmask)
	                  {
		                  print "<option  selected value='$themask'>$masknumber{$themask} - $themask</option>";
	                  }else{
		                  print "<option value='$themask'>$masknumber{$themask} - $themask</option>";
	                  }
                   }
                          
       printf<<EOF
	   	         </select>
	             </td>
		    </tr>
			<tr class="env">
		          <td class="add-div-width">对端心跳口IP<font color="red" size = "3px">*</font></td>
				  <td><input type = 'text'  name = "peer_IP" style = "width:106px;" value= "$peer_IP">
				  ( <font color="red">需与心跳口ip地址位于同一网段</font> )
				  </td> 
		    </tr>
			<tr  class="odd">
			<td class="add-div-width"><b>启用</b></td>
			<td><input type='checkbox' name='enabled' $checked /></td>
			</tr>
			<tr class="table-footer">
		    <td colspan="2"><input id="savebutton" class='submitbutton net_button' type='submit' name='ACTION_RESTART' value='保存' /></td>
	        </tr>
	    </table>

EOF
; 			
    closebox();
    #&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createservice", $ENV{'SCRIPT_NAME'});
}



sub save() {
	$action = $par{'ACTION'};

	if ($action eq 'apply') {
		&log("HA心跳口配置");
		system("/usr/bin/sudo /usr/local/bin/setheartdevip");
		$notemessage ="成功应用当前配置.";
        return;
    }

	if($action eq 'save'){
        modify_HA(
			$par{'HA_device'},
			$par{'heart_IP'},
			$par{'netmask'},
			$par{'peer_IP'},
			$par{'enabled'}); 
		$loadflag = 1;
		%par=();
		return;
	}
}


$extraheader .="<script type='text/javascript' src='/include/waiting.js'></script>";
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('HA心跳口'), 1, $extraheader);
save();
my $errormessage = "";
if(@errormessages>0)
{
	foreach my $err(@errormessages)
	{
		$errormessage .= $err."<br />";
	}
}
&openbigbox($errormessage, $warnmessage, $notemessage);

if ($loadflag == 1) {
    applybox(_("配置已经更改，需要进行应用配置才能使更改生效!"));
}
display_HA();
check_form();
#&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&closepage();
