#!/usr/bin/perl

#file:HA_config.cgi
#author:ailei
#date:2013-11-14


require '/var/efw/header.pl';

my $heart_config="${swroot}/HA/heartdev";
my $backup_config="${swroot}/HA/backupdev";
my $HA_config="${swroot}/HA/hamode";
my $AA_config="${swroot}/HA/hamode.AA";
my $AS_config="${swroot}/HA/hamode.AS";
my $waiting_gif="/images/wait.gif";

my $STATUS_DIR="${swroot}/HA/status/";

my $extraheader="";
my @errormessages=();

my $is_AA= 0;
my $action;
my $sure = "";
my %par;
my $loadflag = 0;

my @sync_status = ("SYNC", "NOSYNC");
my @run_status = ("FAULT", "BACKUP", "MASTER", "QUIET");
my @link_status = ("CONNECTED", "NOCONNECTED");

my %sync_state = (
			"SYNC" => "已同步",
			"NOSYNC" => "未同步",
);
my %run_state = (
			"FAULT" => "故障状态",
			"BACKUP" => "备机状态",
			"MASTER" => "主机状态",
			"QUIET" => "静默状态",
);
my %link_state = (
			"CONNECTED" => "已连接",
			"NOCONNECTED" => "未连接",
);

my @ha_status = ("MASTER", "BACKUP");
my %status = (
			"MASTER" => "主机",
			"BACKUP" => "备机",
);

my @mask = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32);
my %masknumber = (
			"1" =>"128.0.0.0",
			"2"=>"192.0.0.0",
			"3"=>"224.0.0.0",
			"4"=>"240.0.0.0",
			"5"=>"248.0.0.0",
			"6"=>"252.0.0.0",
			"7"=>"254.0.0.0",
			"8"=>"255.0.0.0",
			"9"=>"255.128.0.0",
			"10"=>"255.192.0.0",
			"11"=>"255.224.0.0",
			"12"=>"255.240.0.0",
			"13"=>"255.248.0.0",
			"14"=>"255.252.0.0",
			"15"=>"255.254.0.0",
			"16"=>"255.255.0.0",
			"17"=>"255.255.128.0",
			"18"=>"255.255.192.0",
			"19"=>"255.255.224.0",
			"20"=>"255.255.240.0",
			"21"=>"255.255.248.0",
			"22"=>"255.255.252.0",
			"23"=>"255.255.254.0",
			"24"=>"255.255.255.0",
			"25"=>"255.255.255.128",
			"26"=>"255.255.255.192",
			"27"=>"255.255.255.224",
			"28"=>"255.255.255.240",
			"29"=>"255.255.255.248",
			"30"=>"255.255.255.252",
			"31"=>"255.255.255.254",
			"32"=>"255.255.255.255",
);
sub check_form(){
    printf <<EOF
    <script>
	function choose(){
		var value;
		var ob_as_ip = document.getElementById("as_manager_ip");
		var ob_aa_ip = document.getElementById("aa_manager_ip");
		var ob_as_mask = document.getElementById("as_manager_mask");
		var ob_aa_mask = document.getElementById("aa_manager_mask");

		var ob_as_id = document.getElementById("as_ha_id");
		var ob_as_side = document.getElementById("as_ha_side");
		var ob_as_enable = document.getElementById("as_enable");
		var ob_as_syn = document.getElementById("as_syn");

        var ob_aa_id1 = document.getElementById("aa_ha_id1");
		var ob_aa_side1 = document.getElementById("aa_ha_side1");
		var ob_aa_id2 = document.getElementById("aa_ha_id2");
		var ob_aa_side2 = document.getElementById("aa_ha_side2");
		var ob_aa_enable = document.getElementById("aa_enable");

		var elems = document.getElementsByName("workmode");
		for (var i=0; i<elems.length; i++)
		{
			if (elems.item(i).checked)
			{
				value = elems.item(i).getAttribute("value");
			}
		}
		if (value == "AS")
		{
			ob_as_ip.style.display="table-row";
			ob_as_mask.style.display="table-row";
			ob_as_id.style.display="table-row";
			ob_as_side.style.display="table-row";
			ob_as_enable.style.display="table-row";
			ob_as_syn.style.display="table-row";

			ob_aa_ip.style.display="none";
			ob_aa_mask.style.display="none";
			ob_aa_id1.style.display="none";
			ob_aa_side1.style.display="none";
			ob_aa_id2.style.display="none";
			ob_aa_side2.style.display="none";
			ob_aa_enable.style.display="none";
		}
		else
		{
			ob_as_ip.style.display="none";
			ob_as_mask.style.display="none";
			ob_as_id.style.display="none";
			ob_as_side.style.display="none";
			ob_as_enable.style.display="none";
			ob_as_syn.style.display="none";

			ob_aa_ip.style.display="table-row";
			ob_aa_mask.style.display="table-row";
			ob_aa_id1.style.display="table-row";
			ob_aa_side1.style.display="table-row";
			ob_aa_id2.style.display="table-row";
			ob_aa_side2.style.display="table-row";
			ob_aa_enable.style.display="table-row";
		}
	}
    var object = {
       'form_name':'HAMODE_FORM',
       'option'   :{
                      'as_manager_IP':{
                               'type':'text',
                               'required':'1',
                               'check':'ip',
                             },
					  'aa_manager_IP':{
                               'type':'text',
                               'required':'1',
                               'check':'ip',
                             },
					  'as_id':{
                               'type':'text',
                               'required':'1',
                               'check':'num',
							   'ass_check':function(eve){
								                        var msg="";
                                                        var asid = eve._getCURElementsByName("as_id","input","HAMODE_FORM")[0].value;
														if(asid > 255 || asid < 1)
	                                                    {
															 msg = '热备组编号范围需位于1-255';
                                                        }
														return msg;
                                                     }
                                 },
					  'aa_id1':{
                               'type':'text',
                               'required':'1',
                               'check':'num',
							   'ass_check':function(eve){
								                        var msg="";
                                                        var aaid1 = eve._getCURElementsByName("aa_id1","input","HAMODE_FORM")[0].value;
														if(aaid1 > 255 || aaid1 < 1)
	                                                    {
															 msg = '热备组编号范围需位于1-255';
                                                        }
														return msg;
                                                     }
                                 },
					  'aa_id2':{
                               'type':'text',
                               'required':'1',
                               'check':'num',
							   'ass_check':function(eve){
								                        var msg="";
														var aaid1 = eve._getCURElementsByName("aa_id1","input","HAMODE_FORM")[0].value;
                                                        var aaid2 = eve._getCURElementsByName("aa_id2","input","HAMODE_FORM")[0].value;
														if(aaid2 > 255 || aaid2 < 1)
	                                                    {
															 msg = '热备组编号范围需位于1-255';
                                                        }
														if(aaid1 == aaid2)
														{
															msg = '热备组2与热备组1编号不能相同';
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

sub run_ajax(){
	printf <<EOF
 		<script>
 		function begin_ajax(){
 			\$.get('/cgi-bin/checkHA.cgi', function(data){
				var strings=data.split("===");
		        var len = strings.length;
				var color="";
				var str="";
                var run_state = new Array("故障状态", "备机状态", "主机状态", "静默状态");
			    var elem = strings[1].split(",");
				if (elem[0] == "0")
	            {
					str ="<font color='red'>未连接</font>";
                }
				else
				{
					str ="<font color='green'>已连接</font>";
				}       
				\$("#Link_status").html(str);
               
				if (elem[1] == "0")
				{
					str ="<font color='red'>故障状态</font>";
				}
				else
				{
					var num = parseInt(elem[1]);
					str ="<font color='green'>" + run_state[num] + "</font>";
				}
				\$("#Run_status").html(str);

				if (elem[2] == "0")
	            {
					str ="<font color='red'>未同步</font>";
                }
				else
				{
					str ="<font color='green'>已同步</font>";
				}       
				\$("#Sync_status").html(str);

			});
 		}
 		window.setInterval("begin_ajax()",60000);
 		begin_ajax();
 		</script>
EOF
;
}

sub modify_ASmode($$$$$)
{
	my $as_mip = shift;
	my $as_mmask = shift;
	my $as_mid = shift;
	my $as_mside = shift;
	my $as_menable = shift;

	chomp($as_mip);
	my $as_net = $as_mip.'/'.$as_mmask;
	my %newAS;

	$newAS{'HA_MODE'} = 'AS';
	$newAS{'MANAGEIP'} = $as_net;
	$newAS{'HA_ID'} = $as_mid;
	$newAS{'HA_SIDE'} = $as_mside;

	if ($as_menable !~/^on$/) {
		$as_menable = 'off';
	}

	$newAS{'ENABLED'} = $as_menable;

	&writehash($AS_config,\%newAS);
	&writehash($HA_config,\%newAS);
}

sub modify_AAmode($$$$$$$)
{
	my $aa_mip = shift;
	my $aa_mmask = shift;
	my $aa_mid1 = shift;
	my $aa_mside1 = shift;
	my $aa_mid2 = shift;
	my $aa_mside2 = shift;
	my $aa_menable = shift;

	chomp($aa_mip);
	my $aa_net = $aa_mip.'/'.$aa_mmask;
	my %newAA;

	$newAA{'HA_MODE'} = 'AA';
	$newAA{'MANAGEIP'} = $aa_net;
	$newAA{'HA1_ID'} = $aa_mid1;
	$newAA{'HA1_SIDE'} = $aa_mside1;
	$newAA{'HA2_ID'} = $aa_mid2;
	$newAA{'HA2_SIDE'} = $aa_mside2;

	if ($aa_menable !~/^on$/) {
		$aa_menable = 'off';
	}

	$newAA{'ENABLED'} = $aa_menable;
	&writehash($AA_config,\%newAA);
	&writehash($HA_config,\%newAA);
}

sub display_hamode() {
    my ($work_mode);
	my ($as_manager_IP,$as_manager_mask, $as_enabled, $as_id, $as_side);
	my ($aa_manager_IP, $aa_manager_mask, $aa_enabled, $as_id1, $as_side1,$as_id2, $as_side2);
	my ($as_display, $aa_display ) = ('dispaly:none','dispaly:table-row');

	my $check_status="正在检测  "."<span><img src='$waiting_gif'/></span>";

	my %HA_hash;
	my %AS_hash;
	my %AA_hash;


    if (-e $HA_config) {
		&readhash($HA_config,\%HA_hash);
    }

	if (-e $AS_config) {
		&readhash($AS_config,\%AS_hash);
    }

	if (-e $AA_config) {
		&readhash($AA_config,\%AA_hash);
    }
    
	$work_mode = $HA_hash{'HA_MODE'};

	if ( $work_mode eq 'AS') {
		my $as_manager_network = $HA_hash{'MANAGEIP'};
	    my @as_net = split(/\//, $as_manager_network);
	    $as_manager_IP = $as_net[0];
	    $as_manager_mask = $as_net[1];
	    $as_enabled = $HA_hash{'ENABLED'};
	    $as_id = $HA_hash{'HA_ID'};
	    $as_side = $HA_hash{'HA_SIDE'};

		$as_checked = 'checked';
		$aa_checked = '';

		$as_display = "display:table-row";
		$aa_display = "display:none";
	}
	else
	{
		my $aa_manager_network = $HA_hash{'MANAGEIP'};
	    my @aa_net = split(/\//, $aa_manager_network);
	    $aa_manager_IP = $aa_net[0];
	    $aa_manager_mask = $aa_net[1];
	    $aa_enabled = $HA_hash{'ENABLED'};
	    $aa_id1 = $HA_hash{'HA1_ID'};
	    $aa_side1 = $HA_hash{'HA1_SIDE'};
	    $aa_id2 = $HA_hash{'HA2_ID'};
	    $aa_side2 = $HA_hash{'HA2_SIDE'};

		$aa_checked = 'checked';
		$as_checked = '';

		$aa_display = "display:table-row";
		$as_display = "display:none";
	}

	if($as_enabled =~/^on$/){
		$as_enabled = 'checked';
	}
	else{
		$as_enabled = '';
	}

	if($aa_enabled =~/^on$/){
		$aa_enabled = 'checked';
	}
	else{
		$aa_enabled = '';
	}


	openbox('100%', 'left', _('HA基本配置'));
    printf <<EOF
    </form>
    <form name="HAMODE_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>

	<input type="hidden" name="ACTION" value="save">

     <table width="100%" >
			<tr class="odd">
		          <td class="add-div-type">工作模式<font color="red" size = "3px">*</font></td>
				  <td><input type = 'radio' id = "asmode" name = "workmode"  value= "AS" onchange = "choose()" $as_checked />主备模式
				      <input type = 'radio' id = "aamode" name = "workmode" value= "AA" onchange = "choose()" $aa_checked/>主主模式
				  </td>
			</tr>
			<tr class="env" id="as_manager_ip" style="$as_display;">
		          <td class="add-div-width">管理IP地址<font color="red" size = "3px">*</font></td>
		          <td>
					<input type = 'text'  name = "as_manager_IP" style = "width:106px;" value= "$as_manager_IP">			   	
				  </td>
		    </tr>
			<tr class="env" id="aa_manager_ip" style="$aa_display;">
		          <td class="add-div-width">管理IP地址<font color="red" size = "3px">*</font></td>
		          <td>
					<input type = 'text'  name = "aa_manager_IP" style = "width:106px;" value= "$aa_manager_IP">	
				  </td>
		    </tr>

			<tr class="odd" id="as_manager_mask" style="$as_display;">
		          <td class="add-div-type" >子网掩码<font color="red" size = "3px">*</font></td>
				  <td><select name="as_manager_Mask" onchange="" onkeyup="" style = "width:147px;">
EOF
;
                  foreach my $num(@mask) {
	                  if($num eq $as_manager_mask)
	                  {
		                  print "<option  selected value='$num'>/$num - $masknumber{$num}</option>";
	                  }else{
		                  print "<option value='$num'>/$num - $masknumber{$num}</option>";
	                  }
                   }
                          
       printf<<EOF
	   	         </select>
	             </td>
		    </tr>
			<tr class="odd" id="aa_manager_mask" style="$aa_display;">
		          <td class="add-div-type">子网掩码<font color="red" size = "3px">*</font></td>
				  <td><select name="aa_manager_Mask" onchange="" onkeyup="" style = "width:147px;">
EOF
;
                  foreach my $num(@mask) {
	                  if($num eq $aa_manager_mask)
	                  {
		                  print "<option  selected value='$num'>/$num - $masknumber{$num}</option>";
	                  }else{
		                  print "<option value='$num'>/$num - $masknumber{$num}</option>";
	                  }
                   }
                          
       printf<<EOF
	   	         </select>
	             </td>
		    </tr>

			<tr class="env" id="as_ha_id" style="$as_display;">
		          <td class="add-div-width">热备组<font color="red" size = "3px">*</font></td>
				  <td>
				  <input type = 'text'  name = "as_id" style = "width:4%;" value= "$as_id">
				  (整数,位于1-255之间)
	            </td>
		    </tr>

			<tr class="odd" id="as_ha_side" style="$as_display;">
		          <td class="add-div-width">身份<font color="red" size = "3px">*</font></td>
				 <td><select name="as_side" onchange="" onkeyup="" style = "width:6%;">
EOF
;
                  foreach my $sta(@ha_status) {
	                  if($sta eq $as_side)
	                  {
		                  print "<option  selected value='$sta'>$status{$sta}</option>";
	                  }else{
		                  print "<option value='$sta'>$status{$sta}</option>";
	                  }
                   }
                          
       printf<<EOF
	   	         </select>
	             </td>
		    </tr>

			<tr class="env" id="as_enable" style="$as_display;">
			<td class="add-div-width"><b>启用</b></td>
			<td><input type='checkbox' name='as_enabled' $as_enabled /></td>
			</tr>

			<tr class="env" id="aa_ha_id1" style="$aa_display;">
			      <td class="add-div-width" rowspan = "2">热备组1<font color="red" size = "3px">*</font></td>
				  <td><div style = "float:left; width: 80px;">热备组</div>
				  <div style="float: left;width: 350px;"><input type = 'text'  name = "aa_id1" style = "width:43px;" value= "$aa_id1"/>
				  (整数,位于1-255之间)</div>
	            </td>
		    </tr>

			<tr class="odd" id="aa_ha_side1" style="$aa_display;">
				 <td><div style = "float:left; width: 80px;">身份</div>
				 <div style="float: left;width: 350px;">
				 <select name="aa_side1" onchange="" onkeyup="" style = "width:58px;">
EOF
;
                  foreach my $sta(@ha_status) {
	                  if($sta eq $aa_side1)
	                  {
		                  print "<option  selected value='$sta'>$status{$sta}</option>";
	                  }else{
		                  print "<option value='$sta'>$status{$sta}</option>";
	                  }
                   }
                          
       printf<<EOF
	   	         </select>
				 </div>
	             </td>
		    </tr>

			<tr class="env" id="aa_ha_id2" style="$aa_display;">
			      <td class="add-div-width" rowspan = "2">热备组2<font color="red" size = "3px">*</font></td>
				  <td><div style = "float:left; width: 80px;">热备组</div>
				  <div style="float: left;width: 350px;"><input type = 'text'  name = "aa_id2" style = "width:43px;" value= "$aa_id2"/>
				  (整数,位于1-255之间，且与热备组1不同)</div>
	            </td>
		    </tr>

			<tr class="odd" id="aa_ha_side2" style="$aa_display;">
				 <td><div style = "float:left; width: 80px;">身份</div>
				 <div style="float: left;width: 350px;">
				 <select name="aa_side2" onchange="" onkeyup="" style = "width:58px;">
EOF
;
                  foreach my $sta(@ha_status) {
	                  if($sta eq $aa_side2)
	                  {
		                  print "<option  selected value='$sta'>$status{$sta}</option>";
	                  }else{
		                  print "<option value='$sta'>$status{$sta}</option>";
	                  }
                   }
                          
       printf<<EOF
	   	         </select>
				 </div>
	             </td>
		    </tr>

			<tr class="env" id="aa_enable" style="$aa_display;">
			<td class="add-div-width"><b>启用</b></td>
			<td><input type='checkbox' name='aa_enabled' $aa_enabled /></td>
			</tr>

			<tr class="env" id="as_syn" style="$as_display;">
			<td class="add-div-width"><b>同步方式</b></td>
			<td><input type='button' name='syn_peer' value="同步到对端" onclick="goto_sync(0)" />
			<input type='button' name='syn_local' value="同步到本地" onclick="goto_sync(1)" /></td>
			</tr>


			<tr class="table-footer">
		    <td colspan="2"><input id="savebutton" class='submitbutton net_button' type='submit' name='ACTION_RESTART' value='保存' /></td>
	        </tr>

	    </table>

EOF
; 	
    closebox();
	printf <<END
		<div style = "float:left; width:100%; height:20px"></div>
    <table  class="ruleslist">
        <tr>
            <td  class="boldbase" style="width:100%;">%s</td>        
        </tr>
	
END
	, _('状态信息')
    ;

	printf <<EOF
	<tr class="oodd">
	<td>
	<div style = "float:left; font-weight:bold; text-align:center; width:33%">心跳口连接状态：<span id = "Link_status">$check_status</span>
	</div>

	<div style = "float:left; font-weight:bold; text-align:center; width:33%">运行状态：<span id = "Run_status">$check_status</span>
	</div>

	
	<div style = "float:left; font-weight:bold; text-align:center; width:33%">同步状态：<span id = "Sync_status">$check_status</span>
	</div>

    </td>
	</tr>

	    </table>
EOF
;
}

sub check(){
	system("/usr/bin/sudo /usr/local/bin/checksync");
	system("/usr/bin/sudo /usr/local/bin/checksshstatus");
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
		if ( $par{'workmode'} eq 'AS') {
			modify_ASmode(
				$par{'as_manager_IP'},
				$par{'as_manager_Mask'},
				$par{'as_id'},
				$par{'as_side'},
				$par{'as_enabled'});
		}
		else
		{
			modify_AAmode(
				$par{'aa_manager_IP'},
				$par{'aa_manager_Mask'},
				$par{'aa_id1'},
				$par{'aa_side1'},
				$par{'aa_id2'},
				$par{'aa_side2'},
				$par{'aa_enabled'});
		} 
		%par=();
		$loadflag = 1;
		return;
	}
}

$extraheader .="<script type='text/javascript' src='/include/HA_SYNC.js'></script><style type='text/css'>\@import url(/include/HA_CONFIG.css);</style>";
$extraheader .="<script type='text/javascript' src='/include/waiting.js'></script>";
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('HA基本配置'), 1, $extraheader);
save();
#check();
my $errormessage = "";
if(@errormessages>0)
{
	$reload = 0;
	foreach my $err(@errormessages)
	{
		$errormessage .= $err."<br />";
	}
}
&openbigbox($errormessage, $warnmessage, $notemessage);

if ($loadflag == 1) {
    applybox(_("配置已经更改，需要进行应用配置才能使更改生效!"));
}

display_hamode();
run_ajax();

check_form();
#&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&closepage();
