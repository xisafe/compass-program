#!/usr/bin/perl

#file:loadbalance_main.cgi
#author:ailei
#date:2013-11-7


require '/var/efw/header.pl';

my $server_config="${swroot}/loadbalance/server";
my $group_config="${swroot}/loadbalance/group";
my $all_config="${swroot}/loadbalance/config";

my $needreload = "${swroot}/loadbalance/needreload";

my $extraheafder="";
my @errormessages=();

my $show="";
$EDIT_PNG="/images/edit.png";
$DELETE_PNG="/images/delete.png";
$reload=0;

my $is_editing = 0;
my $action;
my $sure = "";
my %par;

my @protocol = ( "udp + tcp","udp", "tcp");
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


sub read_config_file($) {
    my @lines;
	my $file=shift;
    open (FILE,"$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub read_config_line($$) {
    my $line = shift;
	my $file=shift;
    my @lines = read_config_file($file);
#	foreach $thisline (@lines)
#	{
#		chomp($thisline);
#		if($thisline=~/$devicename/)
#		{
    return $lines[$line]; 
#		}
#	}	
}
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'VIRTUAL_FORM',
       'option'   :{
            'virtualName':{
               'type':'text',
               'required':'1',
               'check':'name|note',
               'ass_check':function(eve){
                    var msg="";
					var line = eve._getCURElementsByName("line","input","VIRTUAL_FORM")[0].value;
                    var virtualname = eve._getCURElementsByName("virtualName","input","VIRTUAL_FORM")[0].value;
					if(virtualname == "")
                    {
						 msg = '虚服务器名不能为空';
						 return msg;
                    }
					if(virtualname.length < 4 || virtualname.length >20)
                    {
						 msg = '虚服务器名长度需在4-20个字符内';
						 return msg;
                    }
					
                    if(!eve.servers){
                        \$.ajax({
                              type : "get",
                              url : '/cgi-bin/chinark_back_get.cgi',
                              async : false,
                              data : 'path=/var/efw/loadbalance/config',
                              success : function(data){ 
                                eve.servers = data;                                                                     
                              }
                        });
                    }
                    var exist = eve.servers.split('\\n');
                    for (var i = 0; i < exist.length; i++) {
                        var tmp = exist[i].split(',');
                        if(virtualname == tmp[1] && i != line){
                            msg = '虚服务器名'+virtualname+'已存在';
                            break;
                        }
                    }
	
                    return msg;
                }
            },
			'virtualIP':{
                   'type':'text',
                   'required':'1',
                   'check':'ip'
            },
		    'virtualPort':{
                   'type':'text',
                   'required':'1',
                   'check':'port',
				   'associated':'virtualIP',
				   'ass_check':function(eve){
                        var msg="";
                        var key = 0;
						var line = eve._getCURElementsByName("line","input","VIRTUAL_FORM")[0].value;
                        var virtualip = eve._getCURElementsByName("virtualIP","input","VIRTUAL_FORM")[0].value;
						var virtualport = eve._getCURElementsByName("virtualPort","input","VIRTUAL_FORM")[0].value;
                        if(!eve.servers){
                            \$.ajax({
                                  type : "get",
                                  url : '/cgi-bin/chinark_back_get.cgi',
                                  async : false,
                                  data : 'path=/var/efw/loadbalance/config',
                                  success : function(data){ 
                                    eve.servers = data;                                                                     
                                  }
                            });
                        }
                        var exist = eve.servers.split('\\n');
                        for (var i = 0; i < exist.length; i++) {
                            var tmp = exist[i].split(',');
                            if(virtualip == tmp[2] && virtualport == tmp[4] && i != line){
                                msg = 'ip地址'+virtualip+'的端口号'+virtualport+'已存在';
                                break;
                            }
                        }
                        return msg;
                     }
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("SERVERS_FORM");
    </script>
EOF
;
}


sub check_modify_values($$$$$){
   my $linenum = shift;
   my $name = shift;
   my $ipaddress = shift;
   my $portnumber = shift;
   my $sergroup = shift;

   my @lines = &read_config_file($all_config);

   my $linelength =  @lines;
   my $i=0;
   
   for($i;$i<$linelength;$i++)
   {
	   if ($i != $linenum) {
		    my $thisline = $lines[$i];
		    chomp($thisline);
		
		    my @line=split(/,/,$thisline);
			my $virualname = $line[1];
			my $virualip = $line[2];
			my $virualport = $line[4];

			if ( $name eq $virualname) {
				push(@errormessages,"该虚服务名已存在！");
				return 0;
			}
			if ($virualip eq $ipaddress && $virualport eq $portnumber) {
				push(@errormessages,"该虚服务ip地址与端口号已被使用！");
				return 0;
			}
	   }
   }
   if ($sergroup eq '') {
	    push(@errormessages,"该虚服务没有添加服务器组！");
	    return 0;

   }
   return 1;
}

sub check_values($$$$){
   my $name = shift;
   my $ipaddress = shift;
   my $portnumber = shift;
   my $sergroup = shift;

   my @lines = &read_config_file($all_config);

   if(@lines>0)
   {

		foreach my $thisline (@lines) {
			chomp($thisline);
		
			my @line=split(/,/,$thisline);
			my $virualname = $line[1];
			my $virualip = $line[2];
			my $virualport = $line[4];

			if ( $name eq $virualname) {
				push(@errormessages,"该虚服务名已存在！");
				return 0;
			}
			if ($virualip eq $ipaddress && $virualport eq $portnumber) {
				push(@errormessages,"该虚服务ip地址与端口号已被使用！");
				return 0;
			}
		}
   }  	
   if ($sergroup eq '') {
	    push(@errormessages,"该虚服务没有添加服务器组！");
	    return 0;

   }
   return 1;
}


sub remove_config_file($){
	my $file = shift;
	$reload=1;
	system("sudo rm -f $file");
	`sudo fdelete $file`;
}

sub toggle_enable($$) {
    my $lineno = shift;
    my $enable = shift;
    if ($enable) {
        $enable = 'on';
    } 
    else {
        $enable = 'off';
    }
	
	my $file = $all_config;
	my @line=split(/,/,read_config_line($lineno,$file));

    my @lines_tosave;
	$line ="$enable,$line[1],$line[2],$line[3],$line[4],$line[5],$line[6]";
	push(@lines_tosave,$line);
	
   &update_lines($lineno,$file,\@lines_tosave);;
}


sub modify_line($$$$$$$$)
{
	my $checked=shift;
	my $virtualline = shift;
	my $virtualname = shift;
	my $virtualip=shift;
    my $virtualmask = shift;
	my $virtualport = shift;
	my $virtualprotocol = shift;
	my $virtualgroup = shift;

	my $enabled='off';
	if($checked =~ /^on$/)
	{
		$enabled='on';
	}
	my @lines_tosave;
	$virtualname =~s/,/，/;
	if ( $virtualprotocol eq "udp + tcp") {
		$virtualprotocol = "";
	}
    if( ! check_modify_values($virtualline,$virtualname,$virtualip,$virtualport,$virtualgroup)){
	    return 1;
	}

	my $file = $all_config;

	$line ="$enabled,$virtualname,$virtualip,$virtualmask,$virtualport,$virtualprotocol,$virtualgroup";
	push(@lines_tosave,$line);
	
	&update_lines($virtualline,$file,\@lines_tosave);

}
sub add_line($$$$$$$){
	my $checked=shift;
	my $virtualname = shift;
	my $virtualip=shift;
    my $virtualmask = shift;
	my $virtualport = shift;
	my $virtualprotocol = shift;
	my $virtualgroup = shift;

	my $enabled='off';
	if($checked =~ /^on$/)
	{
		$enabled='on';
	}

	my @lines_tosave;
	$virtualname =~s/,/，/g;
	if ( $virtualprotocol eq "udp + tcp") {
		$virtualprotocol = "";
	}
	if( ! check_values($virtualname,$virtualip,$virtualport,$virtualgroup)){
	    return 1;
	}
		
	my $file = $all_config;

	$line ="$enabled,$virtualname,$virtualip,$virtualmask,$virtualport,$virtualprotocol,$virtualgroup";
	push(@lines_tosave,$line);
	&append_lines($file,\@lines_tosave);
}

#从配置文件中删除一个虚服务
sub delete_line($) {
    my $lineno = shift;
	my @lines = read_config_file($all_config);
	
	my $i=0;

	my $len=@lines;
	for($i; $i<$len; $i++)
	{
		if ($i == $lineno) {	
			delete ($lines[$i]);
			last;
		}
	}

    save_config_file(\@lines,$all_config);
	$reload = 1;	
}

sub append_lines($$){
	my $file=shift;
	my $ref=shift;
	foreach my $line (@$ref)
	{
		&append_config_file($line,$file);
	}
}

sub update_lines($$$){
	my $serline=shift;
	my $file=shift;
	my $ref=shift;
	my (@head,@body,@tail)=("","","");
	my @lines = &read_config_file($file);
	my $len = @lines;
	my $i=0;
	for($i; $i<$serline; $i++)
	{
		push(@head,$lines[$i]);
	}

    $i=$i+1;

	for($i; $i<$len; $i++)
	{
		push (@tail,$lines[$i]);	
	}

	my @tmp_lines="";
	
	push(@tmp_lines,@head);
	push(@tmp_lines,@$ref);
	push(@tmp_lines,@tail);

	&remove_config_file($file);
	&save_config_file(\@tmp_lines,$file);	
}

sub append_config_file($$) {
    my $line = shift;
	my $file = shift;	
	if($line !~ /^$/)
	{
		open (FILE, ">>$file");
		print FILE ($line."\n");
		close FILE;
		$reload=1;
		`sudo fmodify $file`;
		return 1;
	}
}

sub get_all_group($)
{
	my $file=shift;
	my @groups;
    my @lines = &read_config_file($file);
	if (@lines > 0) {
	    foreach my $line (@lines) {
            chomp($line);
            $line =~ s/[\r\n]//g;
		    my @rl=split(/,/,$line);
            push(@groups, $rl[0]);
        }
	}
    return @groups;
}

sub get_used_group($)
{
	my @used_groups;
	my $file=shift;
    open (FILE,"$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
		my @rm=split(/,/,$line);
        push(@used_groups, $rm[6]);
    }
    close (FILE);
    return @used_groups;
}


sub display_add($) {
    my $lineno = shift;
    my ($virtualName, $virtualIP, $virtualMask, $virtualPort,$virtualProtocol,$serverGroup,$checked);

	my @all_group = get_all_group($group_config);
	my @used_group = get_used_group($all_config);

    if (($is_editing) && ($par{'sure'} ne 'y')) {
        my @rl=split(/,/,read_config_line($lineno,$all_config));
		$checked = $rl[0];
	    $virtualName = $rl[1];
		$virtualIP = $rl[2];
	    $virtualMask = $rl[3];
		$virtualPort = $rl[4];
		$virtualProtocol = $rl[5];
		$serverGroup = $rl[6];
    }
	else{
		$virtualName = $par{'virtualname'};
		$virtualIP = $par{'virtualip'};
	    $virtualMask = $par{'virtualmask'};
		$virtualPort = $par{'virtualport'};
	    $virtualProtocol = $par{'virtualprotocol'};
		$serverGroup = $par{'servergroup'};
		$checked = $par{'enabled'};
	}

    if ( $virtualProtocol eq "") {
		$virtualProtocol = "udp + tcp";
    }

	if(!$checked || $checked =~/^on$/){
		$checked = 'checked';
	}
	elsif($checked = /^off$/){
		$checked = '';
	}

	$action = "add";
    my $title = _('添加虚服务');
	my $buttontext=_("添加");
    if ($is_editing) {
        $action = 'modify';
        $title = _('编辑虚服务');
		$show = "showeditor";
		$buttontext = _("编辑");
    }
	else{
		$show = "";
	}
	&openeditorbox($title,"", $show, "createrule",);
    printf <<EOF
    </form>
    <form name="VIRTUAL_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>

	<input type="hidden" name="ACTION" value="$action">
	<input type="hidden" name="line" value="$lineno">
	<input type="hidden" name="sure" value="y">
     <table width="100%" >
			<tr class="odd">
		          <td class="add-div-type">虚服务名称<font color="red" size = "3px">*</font></td>
				  <td><input type = 'text' name = "virtualName" style = "width:15%;" value= "$virtualName">
				  (数字和字母的组合，长度为4-20个字符 )
				  </td>
			</tr>
			<tr class="env">
		          <td class="add-div-width">虚服务IP地址<font color="red" size = "3px">*</font></td>
		          <td>
				  <input type = 'text'  name = "virtualIP" style = "width:15%;" value= "$virtualIP">				  
				  </td>
		    </tr>

			<tr class="odd">
		          <td class="add-div-type">掩码<font color="red" size = "3px">*</font></td>
				  <td><select name="virtualMask" onchange="" onkeyup="" style = "width:15.5%;">
EOF
;
                  foreach my $themask (@mask) {
	                  if($themask eq $virtualMask)
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
		          <td class="add-div-width">端口号<font color="red" size = "3px">*</font></td>
		          <td><input type = 'text'  name = "virtualPort" style = "width:15%;" value= "$virtualPort">
				  (整数，位于1-65535之间)
				  </td>
		    </tr>

			<tr class="odd">
		          <td class="add-div-type">协议类型<font color="red" size = "3px">*</font></td>
				  <td><select name="virtualProtocol" onchange="" onkeyup="" style = "width:15.5%;">
EOF
;
                  foreach my $theprotocol (@protocol) {
	                  if($theprotocol eq $virtualProtocol)
	                  {
		                  print "<option  selected value='$theprotocol'>$theprotocol</option>";
	                  }else{
		                  print "<option value='$theprotocol'>$theprotocol</option>";
	                  }
                   }
       printf<<EOF
	   	         </select>
	             </td>
		    </tr>

			<tr class="env">
		          <td class="add-div-width">服务器组</td>
				  <td>
		          <select name="serverGroup" onchange="" onkeyup="" style = "width:15.5%;">
EOF
;
    foreach my $theallgroup (@all_group) {
	    my $exist = 0;
		foreach my $theusedgroup (@used_group){
			if($theallgroup eq $theusedgroup){
				$exist = 1;
				if ( $theallgroup eq $serverGroup ) {
					$exist = 2;
				}
			}
		}
		if($exist == 1){
			next;
		}
		if ($exist == 0) {
			printf <<EOF
				<option value='$theallgroup'>$theallgroup</option>
EOF
;
		}
		if ($exist == 2) {
			printf <<EOF
				<option selected value='$theallgroup'>$theallgroup</option>
EOF
;
		}
	}
       printf<<EOF 
	            </select>
	            </td>
		    </tr>
			<tr  class="odd">
			<td class="add-div-width"><b>启用</b></td>
			<td><input type='checkbox' name='enabled' $checked /></td>
			</tr>

	    </table>

EOF
; 			
    &closeeditorbox($buttontext, _("Cancel"), "routebutton", "createservice", $ENV{'SCRIPT_NAME'});
}

sub display_group($) {
    my $line = shift;
    #&openbox('100%', 'left', '当前设备');
    display_add($line);
	#显示已有数据	
    printf <<END
    <table  class="ruleslist">
        <tr>
            <td  class="boldbase" style="width:15%;">%s</td>
            <td  class="boldbase" style="width:15%;">%s</td>
			<td  class="boldbase" style="width:15%;">%s</td>
            <td  class="boldbase" style="width:10%;">%s</td>
		    <td  class="boldbase" style="width:20%;">%s</td>
		    <td  class="boldbase" style="width:15%;">%s</td>
			<td  class="boldbase" style="width:10%;">%s</td>
        </tr>
	
END
	, _('虚服务名称')
	, _('虚服务IP地址')
	, _('掩码')
	, _('端口号')
    , _('协议类型')
    , _('服务器组')
	, _('动作')
    ;
	
	my @lines = &read_config_file($all_config);
	
    my $i = 0;
	my $line = $par{'val_line'};
if(@lines>0)
{
    foreach my $thisline (@lines) {
        chomp($thisline);
		
		my @line=split(/,/,$thisline);

		$enabled = $line[0];
	    $virtualname = $line[1];
		$virtualip = $line[2];
	    $virtualmask = $line[3];
		$virtualport = $line[4];
		$virtualprotocol = $line[5];
		$servergroup = $line[6];

        if ( $servergroup eq "" ) {
			$servergroup = "无";
        }

		if ( $virtualprotocol eq "" ) {
			$virtualprotocol = "udp + tcp";
        }

        my $enabled_gif = $DISABLED_PNG;
        my $enabled_alt = _('Disabled (click to enable)');
        if ($enabled eq 'on') {
            $enabled_gif = $ENABLED_PNG;
            $enabled_alt = _('Enabled (click to disable)');
        }

		my $bgcolor = setbgcolor($is_editing, $line, $i);
        
		print "<tr class='$bgcolor'>";
		printf <<EOF
		<td style="text-align:center">$virtualname</td>
        <td style="text-align:center">$virtualip</td>
		<td style="text-align:center">$virtualmask</td>
        <td style="text-align:center">$virtualport</td>
		<td style="text-align:center">$virtualprotocol</td>
		<td style="text-align:center">$servergroup</td>
        <td class="actions" style="text-align:center">
		    <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" title="$enabled_alt" />
                <input type="hidden" name="ACTION" value="$enabled">
                <input type="hidden" name="val_line" value="$i">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="virtualname" value="$virtualname">
				<input type="hidden" name="val_line" value="$i">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" onsubmit='return confirm("确认删除？")' style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="virtualname" value="$virtualname">
				<input type="hidden" name="val_line" value="$i">
            </form>
        </td>
    </tr>
EOF
,
_('Edit'),
_('Delete');
		$i++;
    }
}else{
	no_tr(7,"无内容");
}
print "</table>";

if($i>0)
{
			printf <<EOF
		<table class="list-legend" cellpadding="0" cellspacing="0">
		  <tr>
			<td>
			  <B>%s:</B>
<IMG SRC="$ENABLED_PNG" title="%s" />
%s
<IMG SRC='$DISABLED_PNG' title="%s" />
%s
<IMG SRC="$EDIT_PNG" title="%s" />
%s
<IMG SRC="$DELETE_PNG" title="%s" />
%s</td>
		  </tr>
		</table>
EOF
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')
;
	#&closebox();
	}
}

sub save() {
	$action = $par{'ACTION'};
    $sure = $par{'sure'};


	if ($action eq 'apply') {
		&log("负载均衡应用规则配置");
		system("/usr/local/bin/loadbalance");
		$notemessage ="成功应用当前配置.";
        return;
    }

	if($action eq "edit")
	{
		$is_editing  = 1;
	}
	
    if ($action eq 'delete') {
        delete_line($par{'val_line'});
		%par=();
        return;
    }	

	if ($action eq 'off') {
        toggle_enable($par{'val_line'}, 1);
           %par=();
           return;
        
    }
   if ($action eq 'on') {
        toggle_enable($par{'val_line'}, 0);
            %par=();
           return;
       
   }	

    if ($action eq 'add') {
		add_line(
			$par{'enabled'},
			$par{'virtualName'},
			$par{'virtualIP'},
			$par{'virtualMask'},
			$par{'virtualPort'},
			$par{'virtualProtocol'},
			$par{'serverGroup'},
		);
		%par=();
		return;
	}
	
	if($action eq 'modify'){
        modify_line(
			$par{'enabled'},
			$par{'line'},
			$par{'virtualName'},
			$par{'virtualIP'},
			$par{'virtualMask'},
			$par{'virtualPort'},
			$par{'virtualProtocol'},
			$par{'serverGroup'},); 
		%par=();
		return;
	}
}


$extraheader .="<script type='text/javascript' src='/include/waiting.js'></script>";
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('服务器设置'), 1, $extraheader);
save();
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

if ($reload) {
    system("touch $needreload");
}

if (-e $needreload) {
    applybox(_("配置已经更改，需要应用才能使更改生效!"));
}

display_group($par{'val_line'});
check_form();
#&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&closepage();
