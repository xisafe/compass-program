#!/usr/bin/perl

#file:HA_network.cgi
#author:ailei
#date:2013-11-11


require '/var/efw/header.pl';

my $heart_config="${swroot}/HA/heartdev";
my $backup_config="${swroot}/HA/backupdev";


my $loadflag = 0;
my $extraheader="";
my @errormessages=();

my $action;
my %par;

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

sub get_HA_eth()
{
	my %heart_eth;
	if ( -f $heart_config) {
		my %heart_hash;
		&readhash($heart_config,\%heart_hash);

		my @heart_interface = split(/&/,$heart_hash{'HEARTDEV'});
	
		foreach my $heart(@heart_interface)
		{
			chomp($heart);
			$heart =~ s/[\r\n]//g;
			$heart_eth{$heart} = $heart;
		}
	}
	return %heart_eth;
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


sub get_available_eth()
{
	my %all_interface = get_all_eth();
#	my %red_interface = get_red_eth();
#	my %color_interface = get_color_eth();
	my %backup_interface = get_backup_eth();
	my %HA_interface = get_HA_eth();
	delete ($all_interface{'lo'});

	foreach my $temp_eth(keys %all_interface)
    {
		
		if ( $temp_eth !~ /^eth/) {
			delete ($all_interface{$temp_eth});
		}
		if ( $temp_eth =~ /\./) {
			delete ($all_interface{$temp_eth});
		}

		#foreach my $red_eth(keys %red_interface)
		#{
		#	if($temp_eth eq $red_eth)
		#	{
		#		 delete ($all_interface{$red_eth});
		#	}
		#}

		#foreach my $color_eth(keys %color_interface)
		#{
		#	if($temp_eth eq $color_eth)
		#	{
		#		 delete ($all_interface{$color_eth});
		#	}
		#}

		foreach my $backup_eth(keys %backup_interface)
		{
			if($temp_eth eq $backup_eth)
			{
				 delete ($all_interface{$backup_eth});
			}
		}
		
		foreach my $HA_eth(keys %HA_interface)
		{
			if($temp_eth eq $HA_eth)
			{
				 delete ($all_interface{$HA_eth});
			}
		}
    }

	return %all_interface;
	
}

sub modify_backup($)
{
	my $backup_eth = shift;

	my %newHA;

	$backup_eth=~s/\|/&/g;

	$newHA{'HA_DEVS'} = $backup_eth;

	&writehash($backup_config,\%newHA);
}



sub display_HAnetwork() {

	my %HAnetwork_hash;

	my %available_eth = get_available_eth();
    my %backup_eth = get_backup_eth();
 
	openbox('100%', 'left', _('HA备份网口'));

    printf <<EOF
    </form>
    <form name="HA_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>

	<input type="hidden" name="ACTION" value="save">
    <table width="100%" >
			<tr class="odd">
		          <td class="add-div-width">选择HA备份网口</td>
		          <td>
							<div id="submit_value" style="margin:auto;">
							</div>
							<div>
								<div id="left-div" style="float:left;">
									<div style="margin:5px auto;">待选网口</div>
									<div>
										<select id="left_select" name="left_select" multiple="multiple" size="8" style="width:150px;height:160px;">
EOF
;
	 foreach my $temp_available_eth(keys %available_eth){
		                  print "<option>$temp_available_eth</option>";
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
									<div style="margin:5px auto;">已选网口</div>
									<div><select  id="right_select" name="right_select" multiple="multiple" size="8" style="width:150px;height:160px;">
EOF
;
	
	 foreach my $temp_back_eth(keys %backup_eth){
		                  print "<option>$temp_back_eth</option>";
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
		&log("HA心跳口配置");
		system("/usr/bin/sudo /usr/local/bin/setheartdevip");
		$notemessage ="成功应用当前配置.";
        return;
    }

	if($action eq 'save'){
        modify_backup($par{'interfaces'}); 
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

display_HAnetwork();
do_choose();
#&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&closepage();
