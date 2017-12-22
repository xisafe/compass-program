#!/usr/bin/perl

#file:loadbalance_server.cgi
#author:ailei
#date:2013-11-4


require '/var/efw/header.pl';

my $server_config="${swroot}/loadbalance/server";
my $group_config="${swroot}/loadbalance/group";

my $extraheader="";
my @errormessages=();

my $show="";
$EDIT_PNG="/images/edit.png";
$DELETE_PNG="/images/delete.png";

my $is_editing = 0;
my $action;
my $sure = "";
my %par;


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
       'form_name':'SERVICE_FORM',
       'option'   :{
            'serverName':{
                'type':'text',
                'required':'1',
                'check':'other|',
				'other_reg':'/[a-zA-Z0-9]{4,10}/',
                'ass_check':function(eve){
                    var msg="";
                    var key = 0;
					var line = eve._getCURElementsByName("line","input","SERVICE_FORM")[0].value;
                    var servername = eve._getCURElementsByName("serverName","input","SERVICE_FORM")[0].value;
					if(servername == "")
                    {
						 msg = '服务器名不能为空';
                    }
					if(servername.length < 4 || servername.length >20)
                    {
						 msg = '服务器组名长度需在4-20个字符内';
						 return msg;
                    }
                    if(!eve.servers){
                        \$.ajax({
                              type : "get",
                              url : '/cgi-bin/chinark_back_get.cgi',
                              async : false,
                              data : 'path=/var/efw/loadbalance/server',
                              success : function(data){ 
                                eve.servers = data;
                              }
                        });
                    }
                    var exist = eve.servers.split('\\n');
                    for (var i = 0; i < exist.length; i++) {
                        var tmp = exist[i].split(',');
                        if(servername == tmp[0] && i != line){
                            msg = '服务器名'+servername+'已存在';
                            break;
                        }
                    }
                    return msg;
                 }
            },
            'serverIp':{
               'type':'text',
               'required':'1',
               'check':'ip'
             },
			'serverPort':{
               'type':'text',
               'required':'1',
               'check':'port',
			   'associated':'serverIp',
			   'ass_check':function(eve){
                    var msg="";
                    var key = 0;
					var line = eve._getCURElementsByName("line","input","SERVICE_FORM")[0].value;
                    var serverip = eve._getCURElementsByName("serverIp","input","SERVICE_FORM")[0].value;
					var serverport = eve._getCURElementsByName("serverPort","input","SERVICE_FORM")[0].value;
                    if(!eve.servers){
                        \$.ajax({
                              type : "get",
                              url : '/cgi-bin/chinark_back_get.cgi',
                              async : false,
                              data : 'path=/var/efw/loadbalance/server',
                              success : function(data){ 
                                eve.servers = data;                                                                     
                              }
                        });
                    }
                    var exist = eve.servers.split('\\n');
                    for (var i = 0; i < exist.length; i++) {
                        var tmp = exist[i].split(',');
                        if(serverip == tmp[1] && serverport == tmp[2] && i != line){
                            msg = 'ip地址'+serverip+'的端口号'+serverport+'已存在';
                            break;
                        }
                    }
                    return msg;
                 }
            },
			'serverWeight':{
                   'type':'text',
                   'required':'1',
                   'check':'num',
				   'ass_check':function(eve){
                        var msg="";
                        var serverWeight = eve._getCURElementsByName("serverWeight","input","SERVICE_FORM")[0].value;
						if(serverWeight > 100)
                        {
							 msg = '服务器权重值不能大于100';
                        }
						return msg;
                    }
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("SERVICE_FORM");
    </script>
EOF
;
}

sub remove_config_file($){
	my $file = shift;
	system("sudo rm -f $file");
	`sudo fdelete $file`;
}

sub modify_line($$$$$)
{
	my $serline = shift;
	my $sername = shift;
	my $serip=shift;
    my $serport = shift;
	my $serweight = shift;

	my @lines_tosave;
	$sername =~s/,/，/;

	if( ! check_modify_values($serline,$sername,$serip,$serport)){
	   return 1;
	}

	my $file = $server_config;

	$line ="$sername,$serip,$serport,$serweight";
	push(@lines_tosave,$line);
	
	&update_lines($serline,$file,\@lines_tosave);

}
sub add_line($$$$){
	my $servername = shift;
	my $serverip=shift;
    my $serverport = shift;
	my $serverweight = shift;

	chomp($servername);
	chomp($serverip);
	chomp($serverport);
	chomp($serverweight);

	my @lines_tosave;
	$servername =~s/,/，/;
	if( ! check_values($servername,$serverip,$serverport)){
	   return 1;
	}
		
	my $file = $server_config;

	$line ="$servername,$serverip,$serverport,$serverweight";
	push(@lines_tosave,$line);
	&append_lines($file,\@lines_tosave);
}

#从配置文件中删除一个服务器
sub delete_line($) {
    my $servername = shift;
	my @lines = read_config_file($server_config);
	
	my $i=0;

	my $len=@lines;
	for($i; $i<$len; $i++)
	{
		if ($lines[$i] =~ /^$servername\,/) {	
			delete ($lines[$i]);
			last;
		}
	}

    save_config_file(\@lines,$server_config);
		
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
		`sudo fmodify $file`;
		return 1;
	}
}


sub check_modify_values($$$$){
   my $linenum = shift;
   my $name = shift;
   my $ipaddress = shift;
   my $portnumber = shift;

   my @lines = &read_config_file($server_config);

   my $linelength =  @lines;
   my $i=0;
   
   for($i;$i<$linelength;$i++)
   {
	   if ($i != $linenum) {
		    my $thisline = $lines[$i];
		    chomp($thisline);
		
		    my @line=split(/,/,$thisline);
			my $servername = $line[0];
			my $serverip = $line[1];
			my $serverport = $line[2];

			if ( $name eq $servername) {
				push(@errormessages,"该服务器名已存在！");
				return 0;
			}
			if ($serverip eq $ipaddress && $serverport eq $portnumber) {
				push(@errormessages,"该服务器IP地址与端口号已被使用！");
				return 0;
			}
	   }
   }
   return 1;
}

sub check_values($$$){
   my $name = shift;
   my $ipaddress = shift;
   my $portnumber = shift;

   my @lines = &read_config_file($server_config);

   if(@lines>0)
   {

		foreach my $thisline (@lines) {
			chomp($thisline);
		
			my @line=split(/,/,$thisline);
			my $servername = $line[0];
			my $serverip = $line[1];
			my $serverport = $line[2];

			if ( $name eq $servername) {
				push(@errormessages,"该服务器名已存在！");
				return 0;
			}
			if ($serverip eq $ipaddress && $serverport eq $portnumber) {
				push(@errormessages,"该服务器ip地址与端口号已被使用！");
				return 0;
			}
		}
   }  	
   return 1;
}

sub check_modify($){
   my $servername = shift;

   my @lines = &read_config_file($group_config);

   if(@lines>0)
   {
    foreach my $thisline (@lines) {
        chomp($thisline);
		
		my @line=split(/,/,$thisline);
		my @serversname = split(/&/,$line[1]);

		foreach my $alreadyname (@serversname) {
              chomp($alreadyname);

			  if ($alreadyname eq $servername) {
				  push(@errormessages,"服务器组配置中存在对该服务器的依赖，在解决该依赖前不能对本服务器配置执行修改或删除操作。");
				  return 0;
			  }
		}
	}
   }
   return 1;
}

sub display_add($) {
    my $lineno = shift;
    my ($serverName, $serverIp, $serverPort, $serverWeight);
    my $i=1;

    if (($is_editing) && ($par{'sure'} ne 'y')) {
        my @rl=split(/,/,read_config_line($lineno,$server_config));
	    $serverName = $rl[0];
		$serverIp = $rl[1];
	    $serverPort = $rl[2];
		$serverWeight = $rl[3];
    }
	else{
		$serverName = $par{'servername'};
		$serverIp = $par{'serverip'};
	    $serverPort = $par{'serverport'};
		$serverWeight = $par{'serverweight'};
	}

	$action = "add";
    my $title = _('添加服务器');
	my $buttontext=_("添加");
    if ($is_editing) {
        $action = 'modify';
        $title = _('编辑服务器');
		$show = "showeditor";
		$buttontext = _("编辑");
    }
	else{
		$show = "";
	}
	&openeditorbox($title,"", $show, "createrule",);
    printf <<EOF
    </form>
    <form name="SERVICE_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="ACTION" value="$action">
	<input type="hidden" name="line" value="$lineno">
	<input type="hidden" name="sure" value="y">
     <table width="100%" >
			<tr class="odd">
		          <td class="add-div-type">服务器名称<font color="red" size = "3px">*</font></td>
				  <td><input type = 'text' name = "serverName" style = "width:15%;" value= "$serverName">
				  ( 数字和字母的组合，长度为4-20个字符 )
				  </td>
			</tr>
			<tr class="env">
		          <td class="add-div-width">服务器IP地址<font color="red" size = "3px">*</font></td>
		          <td><input type = 'text'  name = "serverIp" style = "width:15%;" value= "$serverIp">				  
				  </td>
		    </tr>
			<tr class="odd">
		          <td class="add-div-type">探测端口号<font color="red" size = "3px">*</font></td>
				  <td><input type = 'text'  name = "serverPort" style = "width:15%;" value= "$serverPort">
				  (整数，位于1-65535之间</font> )
				  </td>
			</tr>
			<tr class="env">
		          <td class="add-div-width">权重值<font color="red" size = "3px">*</font></td>
		          <td><input type = 'text' name = "serverWeight" style = "width:15%;" value= "$serverWeight">
				  (整数，位于1-100之间</font> )
				  </td>
		    </tr>
	    </table>

EOF
;
						
    &closeeditorbox($buttontext, _("Cancel"), "routebutton", "createservice", $ENV{'SCRIPT_NAME'});
}

sub display_servers($) {
    my $line = shift;
    #&openbox('100%', 'left', '当前设备');
    display_add($line);
	#显示已有数据	
    printf <<END
    <table  class="ruleslist">
        <tr>
            <td  class="boldbase" style="width:20%;">%s</td>
            <td  class="boldbase" style="width:25%;">%s</td>
			<td  class="boldbase" style="width:20%;">%s</td>
            <td  class="boldbase" style="width:20%;">%s</td>
			<td  class="boldbase" style="width:10%;">%s</td>
        </tr>
	
END
	, _('服务器名称')
	, _('IP地址')
	, _('探测端口')
    , _('权重')
    , _('动作')
    ;
	
	my @lines = &read_config_file($server_config);
	
    my $i = 0;
	my $line = $par{'val_line'};
if(@lines>0)
{
    foreach my $thisline (@lines) {
        chomp($thisline);
		
		my @line=split(/,/,$thisline);
		my $servername = $line[0];
		my $serverip = $line[1];
		my $serverport =  $line[2];
		my $serverweight = $line[3];

		my $bgcolor = setbgcolor($is_editing, $line, $i);
        
		print "<tr class='$bgcolor'>";
		printf <<EOF
		<td style="text-align:center">$servername</td>
        <td style="text-align:center">$serverip</td>
		<td style="text-align:center">$serverport</td>
        <td style="text-align:center">$serverweight</td>
        <td class="actions" style="text-align:center;margin:0px auto;">
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="server_name" value="$servername">
				<input type="hidden" name="val_line" value="$i">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" onsubmit='return confirm("确认删除？")' style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="server_name" value="$servername">
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
	no_tr(5,"无内容");
}
print "</table>";

if($i>0)
{
			printf <<EOF
		<table class="list-legend" cellpadding="0" cellspacing="0">
		  <tr>
			<td>
			  <B>%s:</B>
<IMG SRC="$EDIT_PNG" title="%s" />
%s
<IMG SRC="$DELETE_PNG" title="%s" />
%s</td>
		  </tr>
		</table>
EOF
,
_('Legend'),
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

	if($action eq "edit")
	{
		$is_editing  = check_modify($par{'server_name'});
	}
	
    if ($action eq 'delete') {
		if (check_modify($par{'server_name'})) {
			delete_line($par{'server_name'});
			%par=();
			return;
		}
    }	
    if ($action eq 'add') {
		add_line(
			$par{'serverName'},
			$par{'serverIp'},
			$par{'serverPort'},
			$par{'serverWeight'});
		%par=();
		return;
	}
	
	if($action eq 'modify'){
        modify_line(
			$par{'line'},
			$par{'serverName'},
			$par{'serverIp'},
			$par{'serverPort'},
			$par{'serverWeight'}); 
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

display_servers($par{'val_line'});
check_form();
&closebigbox();
&closepage();
