#!/usr/bin/perl

#file:globalsetting.cgi
#author:ailei
#date:2013-12-22


require '/var/efw/header.pl';

my $settings="${swroot}/tunnelmulticast/globalsettings";


my $extraheader="";
my @errormessages=();

my $action;
my %par;
my $loadflag = 0;

sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'GLOBAL_FORM',
       'option'   :{
					'Global_Network':{
                               'type':'text',
                               'required':'1',
                               'check':'',
							   'ass_check':function(eve){
								                        var msg="";
														var global_network = eve._getCURElementsByName("Global_Network","input","GLOBAL_FORM")[0].value;                                                     
														if(global_network == "")
	                                                    {
															 msg = '组播地址组不能为空';
															 return msg;
                                                        }
														var pattern = /^(?:22[4-9]|23[0-9])\\.(?:\\d|[1-9]\\d|1\\d\\d|2[0-4]\\d|25[0-5])\\.(?:\\d|[1-9]\\d|1\\d\\d|2[0-4]\\d|25[0-5])\\.(?:\\d|[1-9]\\d|1\\d\\d|2[0-4]\\d|25[0-5])\\/(?:[4-9]|[12][0-9]|3[012])\$/;
														if(!pattern.test(global_network)){
															msg = "组播地址组地址不正确,示例:224.1.1.1/24";
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
sub get_close_eth()
{
	my %close_eth;
	if ( -f $settings) {
		my %close_hash;
		&readhash($settings,\%close_hash);

		my @close_interfaces = split(/&/,$close_hash{'MULTICASTIF'});
	
		foreach my $close_interface(@close_interfaces)
		{
			chomp($close_interface);
			$close_interface =~ s/[\r\n]//g;
			$close_eth{$close_interface} = $close_interface;
		}
	}
	return %close_eth;
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
			 my $red_settings = $dir."/".$red."/settings";
			 my %conf_hash = ();
			 readhash($red_settings,\%conf_hash);
			 my $eth = $conf_hash{'RED_DEV'};
			 $red_eth{$eth} = $eth;
		}
	}

	return %red_eth;
}

sub get_color_eth()
{
	my %color_eth;
	my $dir = "/var/efw/ethernet/";
	my $ethernet_settings = $dir."settings";
	my ($green_br, $orange_br, $blue_br);
	opendir (DIR, $dir) or die  _("can’t open the directory!");
	if($dir !~ /^\./ && -f $ethernet_settings)
	{
		my %conf_hash = ();
		readhash($ethernet_settings,\%conf_hash);

		$green_br = $conf_hash{'GREEN_DEV'};
		$orange_br = $conf_hash{'ORANGE_DEV'};
		$blue_br = $conf_hash{'BLUE_DEV'};
		
		if ($conf_hash{'GREEN_IPS'} ne ''){
		    $color_eth{$green_br} = $green_br;
		}
		if ($conf_hash{'ORANGE_IPS'} ne ''){
		    $color_eth{$orange_br} = $orange_br;
		}
		if ($conf_hash{'BLUE_IPS'} ne ''){
		    $color_eth{$blue_br} = $blue_br;
		}
	}

	return %color_eth;
}


sub get_available_interface()
{
	my %available_interface;
	my %red_interface = get_red_eth();
	my %color_interface = get_color_eth();
	my %close_interface = get_close_eth();

	foreach my $red_eth(keys %red_interface)
	{
		$available_interface{$red_eth} = $red_eth;
	}

	foreach my $color_eth(keys %color_interface)
	{
		$available_interface{$color_eth} = $color_eth;
	}

	foreach my $temp_eth(keys %available_interface)
    {
		foreach my $close_eth(keys %close_interface)
		{
			if($temp_eth eq $close_eth)
			{
				 delete ($available_interface{$close_eth});
			}
		}
	}
	return %available_interface;
	
}

sub modify_setting($$)
{
	my $network = shift;
	my $interfaces=shift;


	my %newHA;

	$interfaces=~s/\|/&/g;

	$newHA{'GROUPPREFIX'} = $network;
	$newHA{'MULTICASTIF'} = $interfaces;

	&writehash($settings,\%newHA);
}



sub display_globalsetting() {
    my ($StaticRP, $GlobalPrefix, $MulticastIF);
	my %global_hash;

	my %open_interface = get_available_interface();
	my %close_interface = get_close_eth();

    if (-e $settings) {
		&readhash($settings,\%global_hash);
    }
    
	$StaticRP = $global_hash{'RP'};
    $GlobalPrefix = $global_hash{'GROUPPREFIX'};

	openbox('100%', 'left', _('全局配置'));

    printf <<EOF
    </form>
    <form name="GLOBAL_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>

	<input type="hidden" name="ACTION" value="save">
    <table width="100%" >
			<tr class="odd">
		          <td class="add-div-type">组播地址组*</td>
				  <td><input type = 'text'  name = "Global_Network" style = "width:106px;" value= "$GlobalPrefix">
				  </td> 
		    </tr>
			<tr class="odd">
		          <td class="add-div-width">组播接口设置</td>
		          <td>
							<div id="submit_value" style="margin:auto;">
							</div>
							<div>
								<div id="left-div" style="float:left;">
									<div style="margin:5px auto;">开启的接口</div>
									<div>
										<select id="left_select" name="left_select" multiple="multiple" size="8" style="width:150px;height:160px;">
EOF
;
	 foreach my $temp_open_eth(keys %open_interface){
		                  print "<option>$temp_open_eth</option>";
                   }
	printf <<EOF
										</select>
									</div>
								</div>
								<div style="float:left;margin: 45px 30px;">
									<div style="margin:5px;">
										<input id="add" type="button" value=">>" onclick="" class="mvbutton"/>
									</div>
									<div style="margin:5px;">
										<input id="del" type="button" value="<<" onclick="" class="mvbutton"/>
									</div>
								</div>
								<div id="right-div" style="float:left;">
									<div style="margin:5px auto;">关闭的接口</div>
									<div><select  id="right_select" name="right_select" multiple="multiple" size="8" style="width:150px;height:160px;">
EOF
;
	
	 foreach my $temp_close_eth(keys %close_interface){
		                  print "<option>$temp_close_eth</option>";
                   }
	printf <<EOF
									</select></div>
								</div>
							</div>
					</td>
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

sub do_choose(){
	printf <<EOF
<script type="text/javascript">
	\$(document).ready(function(){
		inital();
		// 添加
		\$("#add").click(function(){
			var fcy = \$("#left-div select option:selected");
			if(fcy.length){
				fcy.each(function(){
					var hiddenInput = "<input type='hidden' name='interfaces' value="+\$(this).text()+" />";
					\$("#submit_value").append(hiddenInput);
				});
				fcy.attr("selected", false).appendTo(\$("#right_select"));
			}
		});
		// 移除
		\$("#del").click(function(){
			del();
		});
		
	})
	var del = function(){
		var cy = \$("#right-div select option:selected");
		if(cy.length){
			cy.attr("selected", false).appendTo(\$("#left_select"));
			\$("#submit_value").empty();
			cy = \$("#right-div select option");
			cy.each(function(){
				var hiddenInput = "<input type='hidden' name='interfaces' value="+\$(this).text()+" />";
				\$("#submit_value").append(hiddenInput);
			});
		}
	}
	var inital = function(){
		var cy = \$("#right-div select option");
		cy.each(function(){
			var hiddenInput = "<input type='hidden' name='interfaces' value="+\$(this).text()+" />";
			\$("#submit_value").append(hiddenInput);
		});
	}
</script>
EOF
;
}

sub save() {
	$action = $par{'ACTION'};

	if ($action eq 'apply') {
		&log("隧道组播全局设置");
		system("/usr/bin/sudo /usr/local/bin/restarttunnelmulticast");
		$notemessage ="成功应用当前配置.";
        return;
    }

	if($action eq 'save'){
        modify_setting(
			$par{'Global_Network'},
			$par{'interfaces'}
			); 
		$loadflag = 1;
		%par=();
		return;
	}
}


$extraheader .="<script type='text/javascript' src='/include/waiting.js'></script>";
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('隧道组播全局配置'), 1, $extraheader);
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
display_globalsetting();
do_choose();
check_form();
#&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&closepage();
