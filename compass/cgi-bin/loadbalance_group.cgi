#!/usr/bin/perl

#file:loadbalance_group.cgi
#author:ailei
#date:2013-11-6


require '/var/efw/header.pl';

my $server_config="${swroot}/loadbalance/server";
my $group_config="${swroot}/loadbalance/group";
my $all_config="${swroot}/loadbalance/config";

my $extraheader="";
my @errormessages=();

my $show="";
$EDIT_PNG="/images/edit.png";
$DELETE_PNG="/images/delete.png";

my $is_editing = 0;
my $action;
my $sure = "";
my %par;

my @detection = ( "icmp","tcp", "udp");
my @loadmethod = ( "rr","wrr", "lc","wlc","sh", "dh");

my %method = (
			"rr" => "轮流",
			"wrr" => "加权轮流",
			"lc" => "最少连接",
			"wlc" => "加权最少连接",
			"sh" => "源地址作hash查找",
			"dh" => "目的地址作hash查找",
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
       'form_name':'SERVERS_FORM',
       'option'   :{
          'groupName':{
               'type':'text',
               'required':'1',
               'check':'name|note',
               'ass_check':function(eve){
                    var msg="";
					var line = eve._getCURElementsByName("line","input","SERVERS_FORM")[0].value;
                    var groupname = eve._getCURElementsByName("groupName","input","SERVERS_FORM")[0].value;
					if(groupname == "")
                    {
						 msg = '服务器组名不能为空';
						 return msg;
                    }
					if(groupname.length < 4 || groupname.length >20)
                    {
						 msg = '服务器组名长度需在4-20个字符内';
						 return msg;
                    }
                    if(!eve.servers){
                        \$.ajax({
                              type : "get",
                              url : '/cgi-bin/chinark_back_get.cgi',
                              async : false,
                              data : 'path=/var/efw/loadbalance/group',
                              success : function(data){ 
                                eve.servers = data;
                              }
                        });
                    }
                    var exist = eve.servers.split('\\n');
                    for (var i = 0; i < exist.length; i++) {
                        var tmp = exist[i].split(',');
                        if(groupname == tmp[0] && i != line){
                            msg = '服务器组名'+groupname+'已存在';
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


sub check_modify_values($$$){
   my $linenum = shift;
   my $name = shift;
   my $servers = shift;

   my @lines = &read_config_file($group_config);

   my $linelength =  @lines;
   my $i=0;

   for($i;$i<$linelength;$i++)
   {
	   if ($i != $linenum) {
		    my $thisline = $lines[$i];
		    chomp($thisline);
		
		    my @line=split(/,/,$thisline);
			my $groupname = $line[0];

			if ( $name eq $groupname) {
				push(@errormessages,"该服务器组名已存在！");
				return 0;
			}
	   }
   }

   if ($servers eq '') {
	   push(@errormessages,"该服务器组没有添加服务器！");
	   return 0;

   }
   
   return 1;
}

sub check_values($$){
   my $name = shift;
   my $servers = shift;

   my @lines = &read_config_file($group_config);

   if(@lines>0)
   {

		foreach my $thisline (@lines) {
			chomp($thisline);
		
			my @line=split(/,/,$thisline);
			my $groupname = $line[0];

			if ( $name eq $groupname) {
				push(@errormessages,"该服务器组名已存在！");
				return 0;
			}
		}
   } 
   if ($servers eq '') {
	   push(@errormessages,"该服务器组没有添加服务器！");
	   return 0;

   }
   return 1;
}

sub remove_config_file($){
	my $file = shift;
	system("sudo rm -f $file");
	`sudo fdelete $file`;
}

sub modify_line($$$$$)
{
	my $groupline = shift;
	my $groupname = shift;
	my $groupserver=shift;
    my $groupload = shift;
	my $groupdetect = shift;

	my @lines_tosave;
	$groupname =~s/,/，/;
	$groupserver=~s/\|/&/g;

	if( ! check_modify_values($groupline,$groupname,$groupserver)){
	   return 1;
	}

	my $file = $group_config;

	$line ="$groupname,$groupserver,$groupload,$groupdetect";
	push(@lines_tosave,$line);
	
	&update_lines($groupline,$file,\@lines_tosave);

}
sub add_line($$$$){
	my $groupname = shift;
	my $groupserver=shift;
    my $loadmethod = shift;
	my $classdetect = shift;

	chomp($groupname);
	chomp($groupserver);
	chomp($loadmethod);
	chomp($classdetect);

	my @lines_tosave;
	$groupname =~s/,/，/g;
	$groupserver=~s/\|/&/g;
	if( ! check_values($groupname,$groupserver)){
	   return 1;
	}
		
	my $file = $group_config;

	$line ="$groupname,$groupserver,$loadmethod,$classdetect";
	push(@lines_tosave,$line);
	&append_lines($file,\@lines_tosave);
}

#从配置文件中删除一个服务器
sub delete_line($) {
    my $groupname = shift;
	my @lines = read_config_file($group_config);
	
	my $i=0;

	my $len=@lines;
	for($i; $i<$len; $i++)
	{
		if ($lines[$i] =~ /^$groupname\,/) {	
			delete ($lines[$i]);
			last;
		}
	}

    save_config_file(\@lines,$group_config);
		
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

sub check_modify($){
   my $groupname = shift;

   my @lines = &read_config_file($all_config);

   if(@lines>0)
   {
    foreach my $thisline (@lines) {
        chomp($thisline);
		
		my @line=split(/,/,$thisline);
        if ($groupname eq $line[6]) {
			push(@errormessages,"服务器负载均衡配置中存在对该服务器组的依赖，在解决该依赖前不能对本服务器组配置执行修改或删除操作。");
			return 0;
		}
	}
   }
   return 1;
}

sub get_all_server($)
{
	my $file=shift;
	my @servers;
    my @lines = &read_config_file($file);
	if (@lines > 0) {
	    foreach my $line (@lines) {
            chomp($line);
            $line =~ s/[\r\n]//g;
		    my @rl=split(/,/,$line);
            push(@servers, $rl[0]);
        }
	}
   # $notemessage = "@lines";
    return @servers;
}

sub get_group_server($)
{
	my @group_servers;
	my $file=shift;
    open (FILE,"$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
		my @rl=split(/,/,$line);
		my @rm=split(/&/,$rl[1]);
        push(@group_servers, @rm);
    }
    close (FILE);
    return @group_servers;
}


sub display_add($) {
    my $lineno = shift;
    my ($groupName, $groupServer, $loadMethod, $groupDetection);
    my $i=1;
	my @all_server = get_all_server($server_config);
	my @group_all_server = get_group_server($group_config);

    if (($is_editing) && ($par{'sure'} ne 'y')) {
        my @rl=split(/,/,read_config_line($lineno,$group_config));
	    $groupName = $rl[0];
		$groupServer = $rl[1];
	    $loadMethod = $rl[2];
		$groupDetection = $rl[3];
    }
	else{
		$groupName = $par{'groupName'};
		$groupServer = $par{'servers'};
	    $loadMethod = $par{'loadMethod'};
		$groupDetection = $par{'groupDetection'};
	}

    my @group_server = split(/&/,$groupServer);
	$action = "add";
    my $title = _('添加服务器组');
	my $buttontext=_("添加");
    if ($is_editing) {
        $action = 'modify';
        $title = _('编辑服务器组');
		$show = "showeditor";
		$buttontext = _("编辑");
    }
	else{
		$show = "";
	}
	&openeditorbox($title,"", $show, "createrule",);
    printf <<EOF
    </form>
    <form name="SERVERS_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>

	<input type="hidden" name="ACTION" value="$action">
	<input type="hidden" name="line" value="$lineno">
	<input type="hidden" name="sure" value="y">
     <table width="100%" >
			<tr class="odd">
		          <td class="add-div-type">服务器组名<font color="red" size = "3px">*</font></td>
				  <td><input type = 'text' name = "groupName" style = "width:15.8%;" value= "$groupName">
				  (数字和字母的组合，长度为4-20个字符 )
				  </td>
			</tr>
			<tr class="env">
		          <td class="add-div-width">选择服务器<font color="red" size = "3px">*</font></td>
		          <td>
							<div id="submit_value" style="margin:auto;">
							</div>
							<div>
								<div id="left-div" style="float:left;">
									<div style="margin:5px auto;">待选服务器</div>
									<div>
										<select id="left_select" name="left_select" multiple="multiple" size="8" style="width:150px;height:160px;">
EOF
;
	foreach my $remain_server (@all_server){
		my $exist = 0;
		foreach my $already_server (@group_all_server){
			if($remain_server eq $already_server){
				$exist++;
			}
		}
		if($exist != 0){
			$exist = 0;
			next;
		}else{
			printf <<EOF
				<option>$remain_server</option>
EOF
;
		}
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
									<div style="margin:5px auto;">已选服务器</div>
									<div><select  id="right_select" name="right_select" multiple="multiple" size="8" style="width:150px;height:160px;">
EOF
;
	foreach my $thegroupserver (@group_server){
		printf <<EOF
			<option>$thegroupserver</option>
EOF
;
	}
	printf <<EOF
									</select></div>
								</div>
							</div>
						</td>
				 
		    </tr>
			<tr class="odd">
		          <td class="add-div-type">负载均衡方式<font color="red" size = "3px">*</font></td>
				  <td><select name="loadMethod" onchange="" onkeyup="" style = "width:15.8%;">
EOF
;
                  foreach my $load_method (@loadmethod) {
                      chomp($load_method);
	                  if($load_method eq $loadMethod)
	                  {
		                  print "<option  selected value='$load_method'>$method{$load_method}</option>";
	                  }else{
		                  print "<option value='$load_method'>$method{$load_method}</option>";
	                  }
                   }
                          
       printf<<EOF
	   	         </select>
	             </td>
		    </tr>
			<tr class="env">
		          <td class="add-div-width">健康类型检测<font color="red" size = "3px">*</font></td>
				  <td>
		          <select name="groupDetection" onchange="" onkeyup="" style = "width:15.8%;">
EOF
;
    foreach my $classdetect (@detection) {
        chomp($classdetect);
	    if($classdetect eq $groupDetection)
	    {
		    print "<option  selected value='$classdetect'>$classdetect</option>";
	    }else{
		    print "<option value='$classdetect'>$classdetect</option>";
	    }
    }
       printf<<EOF 
	            </select>
	            </td>
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
            <td  class="boldbase" style="width:20%;">%s</td>
            <td  class="boldbase" style="width:25%;">%s</td>
			<td  class="boldbase" style="width:20%;">%s</td>
            <td  class="boldbase" style="width:20%;">%s</td>
			<td  class="boldbase" style="width:10%;">%s</td>
        </tr>
	
END
	, _('服务器组名')
	, _('组内服务器')
	, _('负载均衡方式')
    , _('健康类型检测')
    , _('动作')
    ;
	
	my @lines = &read_config_file($group_config);
	
    my $i = 0;
	my $line = $par{'val_line'};
if(@lines>0)
{
    foreach my $thisline (@lines) {
        chomp($thisline);
		
		my @line=split(/,/,$thisline);
		my $groupname = $line[0];
		my $groupserver = $line[1];
		my $loadbalmethod = $line[2];
		my $groupdetection =  $line[3];

		$groupserver =~s/&/ /g;

        if ( $groupserver eq "" ) {
			$groupserver = "无";
        }

		my $bgcolor = setbgcolor($is_editing, $line, $i);
        
		print "<tr class='$bgcolor'>";
		printf <<EOF
		<td style="text-align:center">$groupname</td>
        <td>$groupserver</td>
		<td style="text-align:center">$method{$loadbalmethod}</td>
        <td style="text-align:center">$groupdetection</td>
        <td class="actions" style="text-align:center">
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="group_name" value="$groupname">
				<input type="hidden" name="val_line" value="$i">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" onsubmit='return confirm("确认删除？")' style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="group_name" value="$groupname">
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
					var hiddenInput = "<input type='hidden' name='servers' value="+\$(this).text()+" />";
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
				var hiddenInput = "<input type='hidden' name='servers' value="+\$(this).text()+" />";
				\$("#submit_value").append(hiddenInput);
			});
		}
	}
	var inital = function(){
		var cy = \$("#right-div select option");
		cy.each(function(){
			var hiddenInput = "<input type='hidden' name='servers' value="+\$(this).text()+" />";
			\$("#submit_value").append(hiddenInput);
		});
	}
</script>
EOF
;
}

sub save() {
	$action = $par{'ACTION'};
    $sure = $par{'sure'};

	if($action eq "edit")
	{
		$is_editing  = check_modify($par{'group_name'});
	}
	
    if ($action eq 'delete') {
		if (check_modify($par{'group_name'})) {
			delete_line($par{'group_name'});
			%par=();
			return;
		}
    }	
    if ($action eq 'add') {
		add_line(
			$par{'groupName'},
			$par{'servers'},
			$par{'loadMethod'},
			$par{'groupDetection'});
		%par=();
		return;
	}
	
	if($action eq 'modify'){
        modify_line(
			$par{'line'},
			$par{'groupName'},
			$par{'servers'},
			$par{'loadMethod'},
			$par{'groupDetection'}); 
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

display_group($par{'val_line'});
do_choose();
check_form();
#&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&closepage();
