#!/usr/bin/perl

#file:devices.cgi
#author:zhangzheng
use JSON::XS;
use Data::Dumper;
require '/var/efw/header.pl';
my $gicpconf="/var/efw/phlinux/settings";
my $get_domain="/var/log/phlinux/get_domain";
my $gnwayconf="/var/efw/gnhostlinux/settings";
my $needreload1="/var/efw/phlinux/needreload";
my $needreload2="/var/efw/gnhostlinux/needreload";
my $needreload3="/var/efw/gnhostlinux/needreload3";
my $extraheader="";
my @errormessages=();

my $json = new JSON::XS;
my $EDIT_PNG="/images/edit.png";
my $DELETE_PNG="/images/delete.png";
my $waiting_gif="/images/wait.gif";
$reload=0;
#my %ethernet=();
my $Oray_exist = 0;
my $Gnway_exist = 0;

#for (my $num=0;$num<30 ;$num++) {
#	my $n = $num+1;
#	$ethernet{'eth'.$num} = "接口$n";
#	$ethernet{'ppp'.$num} = "ppp$num";
#}
# my @gottypeiface = ();
#    opendir(DIR, "${swroot}/uplinks/") || return \@uplinks;
#    foreach my $dir (readdir(DIR)) {
#        next if ($dir =~ /^\./);
#        next if (!(-f "${swroot}/uplinks/$dir/data"));
#        &readhash("${swroot}/uplinks/$dir/data", \%set);
#        push(@gottypeiface, $set{'interface'});
#    }
#    closedir(DIR);

my $wan_faces ;
sub update_wan_faces(){
	my $json_str,$json_str_rev; 
	$json_str = `sudo /usr/local/bin/getAllWanJson.py`;
	$wan_faces = $json->decode($json_str);
}
&update_wan_faces();
# print join('|',@gottypeiface);
sub read_config_file($) {
    my @lines;
	my $file=shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'DDNS_FORM',
       'option'   :{
                    'USERNAME':{
                               'type':'text',
                               'required':'1',
                               'check':'name|'
                             },
                    'PASSWORD':{
                               'type':'password',
                               'required':'1'
                             },
                    'DOMAIN':{
                               'type':'text',
                               'required':'1',
                               'check':'domain|'
                             }
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("DDNS_FORM");
    </script>
EOF
;
}
sub run_ajax(){
	if (-e $gicpconf) {
		readhash($gicpconf,\%confgicp);
		if ($confgicp{'ENABLED'}) {
			`/etc/init.d/dnsmasq reload`;
				printf <<EOF
 					<script>
 						function begin_ajax(){
 							\$.get('/cgi-bin/checkddns.cgi', {path:"oray"}, function(data){
								\$("#gicp_sta").html(data);
							});
 						}
 						window.setInterval("begin_ajax()",100000);
 						begin_ajax();
 					</script>
EOF
;
		}
	}
	if (-e $gnwayconf) {
		readhash($gnwayconf,\%confgnway);
		if ($confgnway{'ENABLED'}) {
			`/etc/init.d/dnsmasq reload`;
				printf <<EOF
 					<script>
 						function begin_ajax(){
 							\$.get('/cgi-bin/checkddns.cgi', {path:"gnway"}, function(data){
								\$("#gnway_sta").html(data);
							});
 						}
 						window.setInterval("begin_ajax()",100000);
 						begin_ajax();
 					</script>
EOF
;			
		}
	}
}
sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;

    ####help_msg
	my $help_hash1 = read_json("/home/httpd/help/ddns_help.json","ddns.cgi","服务-动态DNS-添加动态DNS-选择服务商","-10","30","down");
	my $help_hash2 = read_json("/home/httpd/help/ddns_help.json","ddns.cgi","服务-动态DNS-添加动态DNS-填写用户名","-10","30","down");
	my $help_hash3 = read_json("/home/httpd/help/ddns_help.json","ddns.cgi","服务-动态DNS-添加动态DNS-填写密码","-10","30","down");
	my $help_hash4 = read_json("/home/httpd/help/ddns_help.json","ddns.cgi","服务-动态DNS-添加动态DNS-填写域名","-10","30","down");
	###


    my ($name, $password, $checked,$domain,$dev);
	my @service;
	my %selected;

    if ($Oray_exist==0) {
		push (@service,'Oray');
	}
	if ($Gnway_exist==0) {
		push (@service,'Gnway');
	}
	my $num=@service;
	my $display = "style=display:none;";
	if ($num) {
		$display = "style=display:table-row;";
	}
    if (($is_editing) && ($par{'sure'} ne 'y')) {
	    $display = "style=display:none;";
        my %lines;
		if ($line eq 'Oray') {
			readhash($gicpconf,\%lines);
		}
		if ($line eq 'Gnway') {
			readhash($gnwayconf,\%lines);
		}
		$name = $lines{'USERNAME'};
		$domain = $lines{'DOMAIN'};
		$checked = $lines{'ENABLED'};
		$password = $lines{'PASSWORD'};
		$dev = $lines{'DEV'};
		# $dev = $line{'DEV'};
    }
	#chomp($checked);
	$selected{$dev} = "selected";
	if($checked eq 1)
	{
	   $checked = 'checked';
	} else {
	   $checked = '';
	}
=q
	if(!$checked || $checked =~/^on$/){
		$checked = 'checked';
	}
	elsif($checked = /^off$/){
		$checked = '';
	}
=cut
	my $action = 'add';
    my $title = _('添加动态DNS');
	my $buttontext=_("Add");
    if ($is_editing) {
        $action = 'edit1';
        $title = _('编辑动态DNS');
		$buttontext = _("Edit");
    }
	if($par{'ACTION'} eq 'edit' || $errormessage ne '') {
        $show = "showeditor";
    }
	if ($num || $is_editing) {
    openeditorbox($title, $title, $show, "addqosdevice", @errormessages);
    printf <<EOF
    </form>
     <form name="DDNS_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
     <table width="100%" cellpadding="0" cellspacing="0"> 
	   <tr $display class='odd'>
	     <td class="add-div-type need_help">%s *$help_hash1</td>
		 <td><select name="service" style='width:172px;'>
EOF
,_('Service provider')
;
       foreach my $elem (@service) {
		   chomp($elem);
		   my $name="花生壳";
		   if ($elem eq 'Gnway') {
			   $name="金万维";
		   }
		   print "<option value='$elem'>$name</option>"
       }
	   printf <<EOF
		 </select></td>
       </tr>
       <tr class='env'>
	     <td width='220px' class="add-div-type need_help">自动启用</td>
		 <td><input type="checkbox" name="autorun" $checked/></td>
       </tr>	   
	   <tr class='odd'>
	     <td width='220px' class="add-div-type need_help">%s *$help_hash2</td>
		 <td><input type="text" name="USERNAME" value='$name' /></td>
       </tr>
	   <tr class='env'>
	     <td class="add-div-type need_help">%s *$help_hash3</td>
		 <td><input type="password" name="PASSWORD" value='$password' /></td>
       </tr>
	   <tr class='odd'>
	   	 <td class="add-div-type need_help">%s *$help_hash5</td>
		 <td><select name="DEV" style="width:172px;">
EOF
,_('Username')
,_('Password')
,_('上行线')
;
		foreach	my $red_dev(keys %{$wan_faces} ){
			my $text = ${$wan_faces}{$red_dev} ;# ne '' ? ${$wan_faces}{$red_dev} : '上行线已失效';
			print "<option value='$red_dev' $selected{$red_dev}>$text</option>}
			option"
		}

		#foreach	my $red_dev(@gottypeiface){
		#	print "<option value='$red_dev' $selected{$red_dev}>$ethernet{$red_dev}</option>}
		#	option"
		#}
printf <<EOF		 
		 </select></td></tr>
       <tr class='env'>	     
	     <td class="add-div-type need_help">%s *$help_hash4</td>
		 <td><input onfocus="display_alt()" onblur="display_alt()" type="text" name="DOMAIN" value='$domain' /><span id="alt_msg" style="margin-left:10px;display:none;">%s</span></td>
       </tr>

EOF
,_('Domain name')
,_('请输入与用户名对应的域名.')
;

   printf <<EOF
		</table>
	<input type="hidden" name="ACTION" value="$action">
	<input type="hidden" name="sure" value="y">
	<input type="hidden" name="line" value="$line">
EOF
;
						
    &closeeditorbox($buttontext, _("Cancel"), "routebutton", "createdevice", "$ENV{SCRIPT_NAME}");
	}
}

sub display_devices($$) {

    my $is_editing = shift;
    my $line = shift;
    my %confgicp,%confgnway;
	my $num = 0;
	my $num1 = 0;
	my $gicp_status="正在连接  "."<span><img src='$waiting_gif'/></span>";
	my $gnway_status="正在连接  "."<span><img src='$waiting_gif'/></span>";

	if (-e $gicpconf) {
		readhash($gicpconf,\%confgicp);
	}
	if (-e $gnwayconf) {
		readhash($gnwayconf,\%confgnway);
	}
	if($confgicp{'USERNAME'}){
	    $num1 = 1;
		$num = 1;
		$Oray_exist = 1;
	}
	if($confgnway{'USERNAME'}){
		$num = 2;
		$Gnway_exist = 1;
	}
	if (!$confgicp{'ENABLED'}) {
		$gicp_status="未连接";
	}
	if (!$confgnway{'ENABLED'}) {
		$gnway_status="未连接";
	}
	my $enabled_gif = "/images/off.png";
	my $enabled_alt = _('Disabled (click to enable)');
    #&openbox('100%', 'left', _('Dynamic DNS'));
    display_add($is_editing, $line);
	

    printf <<END
		<script>
		   function display_alt(){
		if (document.getElementById("alt_msg").style.display != "none") {
			document.getElementById("alt_msg").style.display = "none";
		}
		else{document.getElementById("alt_msg").style.display="inline";}
	}
		</script>
    <table style='margin-top:20px'  width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr>
            <td class="boldbase" style="width:16%;">%s</td>
            <td class="boldbase" style="width:16%;">%s</td>
            <td class="boldbase" style="width:16%;">%s</td>
			<td class="boldbase" style="width:16%;">%s</td>
			<td class="boldbase" style="width:16%;">%s</td>
			<td class="boldbase" style="width:16%;">%s</td>
        </tr>
	
END
	, _('Service provider')
	, _('Username')
    , _('上行线')
    , _('Domain name')
	,_('Status')
    , _('Actions')
    ;
	
		if ($num == 0) {
			no_tr(6,_('Current no content'));
		}
		if ($num1 == 1 ){
			if ($confgicp{'ENABLED'} == 1) {
				$enabled_gif = "/images/on.png";
				$enabled_alt = _('Enabled (click to disable)');
			}
		my $style;
		if ($par{'line'} eq 'Oray'&& $par{'ACTION'} eq 'edit') {
			$style = 'selected';
		}
		my $tmp_dev = ${$wan_faces}{$confgicp{'DEV'}} ? ${$wan_faces}{$confgicp{'DEV'}}:"上行线（$confgicp{'DEV'}）无效";

        printf <<EOF
		<tr class="odd_thin $style">
        <td>花生壳</td>
        <td>$confgicp{'USERNAME'}</td>
        <td>$tmp_dev </td>
        <td>$confgicp{'DOMAIN'}</td>
		<td id="gicp_sta">$gicp_status</td>
        <td>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input  type='image' name="submit" SRC="$enabled_gif" title="$enabled_alt" />
                <input type="hidden" name="ACTION" value="toggle">
                <input type="hidden" name="line" value="Oray">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input  type='image' name="submit" SRC="$EDIT_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="line" value="Oray">
            </form>            
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" onsubmit="return confirm('确认删除规则?')">
                <input  type='image' name="submit" SRC="$DELETE_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="line" value="Oray">
            </form>
        </td>
    </tr>
EOF
,
_('Edit'),
_('Delete');
		}
		if ($num == 2 ){
			if ($confgnway{'ENABLED'} == 1) {
				$enabled_gif = "/images/on.png";
				$enabled_alt = _('Enabled (click to disable)');
			}
			else{
				$enabled_gif = "/images/off.png";
			    $enabled_alt = _('Disabled (click to enable)');
			}
			my $style;
			if ($par{'line'} eq 'Gnway' && $par{'ACTION'} eq 'edit') {
				$style = 'selected';
			}
		my $tmp_dev = ${$wan_faces}{$confgnway{'DEV'}} ? ${$wan_faces}{$confgnway{'DEV'}}:"上行线（$confgnway{'DEV'}）无效";

        printf <<EOF
		<tr class="env_thin $style">
        <td>金万维</td>
        <td>$confgnway{'USERNAME'}</td>
        <td>$tmp_dev</td>
        <td>$confgnway{'DOMAIN'}</td>
		<td id="gnway_sta">$gnway_status</td>
        <td>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input  type='image' name="submit" SRC="$enabled_gif" title="$enabled_alt" />
                <input type="hidden" name="ACTION" value="toggle">
                <input type="hidden" name="line" value="Gnway">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input type='image' name="submit" SRC="$EDIT_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="line" value="Gnway">
            </form>            
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" onsubmit="return confirm('确认删除规则?')">
                <input  type='image' name="submit" SRC="$DELETE_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="line" value="Gnway">
            </form>
        </td>
    </tr>
EOF
,
_('Edit'),
_('Delete');
		}

print "</table>";

if($num != 0)
{
			printf <<EOF
		
		<table class="list-legend" cellpadding="0" cellspacing="0">
		  <tr>
			<td class="boldbase">
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
}
	#&closebox();
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
	my %saveconf;
	if($par{'autorun'} eq 'on')
	{
	  $saveconf{'ENABLED'} = 1;
	} else {
	  $saveconf{'ENABLED'} = 0;
	}
	`echo >>/tmp/test $par{'autorun'}`;
	$saveconf{'USERNAME'} = $par{'USERNAME'};
	$saveconf{'PASSWORD'} = $par{'PASSWORD'};
	$saveconf{'DOMAIN'} = $par{'DOMAIN'};
	$saveconf{'DEV'} = $par{'DEV'};
	if ($action eq 'add' || $action eq 'edit1') {
		if (!$par{'USERNAME'}) {
			$errormessage = _('用户名不能为空!');
			return 0;
		}
		if (!$par{'PASSWORD'}) {
			$errormessage = _('密码不能为空!');
			return 0;
		}
		if (!$par{'DOMAIN'}) {
			$errormessage = _('域名不能为空！');
			return 0;
		}
		if (!&validdomainname($par{'DOMAIN'})) {
			$errormessage = _('域名不合法！');
			return 0;
		}
	}
    if ($action eq 'add') {
		my $service = $par{'service'};
		if ($service eq 'Oray') {
			$service = 'phlinux';
			&writehash($gicpconf,\%saveconf);
			`sudo fmodify $gicpconf`;
			system ("touch $needreload1");
		}
		if ($service eq 'Gnway') {
			$service = 'gnhostlinux';
			&writehash($gnwayconf,\%saveconf);
			`sudo fmodify $gnwayconf`;
			system ("touch $needreload2");
		}
	}
	if ($action eq 'delete') {
		my $service = $par{'line'};
		my %nullconf;
		if ($service eq 'Oray') {
		    &writehash($gicpconf,\%nullconf);
			&writehash($get_domain,\%nullconf);
			system ("rm $get_domain");
			`sudo fmodify $gicpconf`;
			system ("touch $needreload1");
		}
		if ($service eq 'Gnway') {
			&writehash($gnwayconf,\%nullconf);			
			`sudo fmodify $gnwayconf`;
			system ("touch $needreload2");
		}
	}
	if(($action eq 'edit1')&&($sure eq 'y')){
        my $service = $par{'line'};
		my %saveconf;
		if ($service eq 'Oray') {
			&readhash($gicpconf,\%saveconf);
            if($par{'autorun'} eq 'on')
	        {
	           $saveconf{'ENABLED'} = 1;
	        } else {
	           $saveconf{'ENABLED'} = 0;
	        }			
			$saveconf{'USERNAME'} = $par{'USERNAME'};
			$saveconf{'PASSWORD'} = $par{'PASSWORD'};
			$saveconf{'DOMAIN'} = $par{'DOMAIN'};
			$saveconf{'DEV'} = $par{'DEV'};
            &writehash($gicpconf,\%saveconf);
			`sudo fmodify $gicpconf`;
			my %old;
			readhash($gicpconf.".old",\%old);
			my $num = 0;
			foreach $key (keys %old) {
				if ($saveconf{$key} ne $old{$key}) {
					$num = 1;
				}
			}
			if ($num) {
				system ("touch $needreload1");
			}
		}
		if ($service eq 'Gnway') {
			&readhash($gnwayconf,\%saveconf);
            if($par{'autorun'} eq 'on')
	        {
	           $saveconf{'ENABLED'} = 1;
	        } else {
	           $saveconf{'ENABLED'} = 0;
	        }			
			$saveconf{'USERNAME'} = $par{'USERNAME'};
			$saveconf{'PASSWORD'} = $par{'PASSWORD'};
			$saveconf{'DOMAIN'} = $par{'DOMAIN'};
			$saveconf{'DEV'} = $par{'DEV'};
            &writehash($gnwayconf,\%saveconf);
			`sudo fmodify $gnwayconf`;
            my %old;
			readhash($gnwayconf.".old",\%old);
			my $num = 0;
			foreach $key (keys %old) {
				if ($saveconf{$key} ne $old{$key}) {
					$num = 1;
				}
			}
			if ($num) {
				system ("touch $needreload2");
			}
		}	
	}
    if ($action eq 'toggle') {
		my $service = $par{'line'};
		my %saveconf;
		if ($service eq 'Oray') {
			&readhash($gicpconf,\%saveconf);
			if ($saveconf{'ENABLED'}) {
				$saveconf{'ENABLED'} = 0;
			}
			else{$saveconf{'ENABLED'} = 1;}
            &writehash($gicpconf,\%saveconf);
			`sudo fmodify $gicpconf`;
			system ("touch $needreload1");
		}
		if ($service eq 'Gnway') {
			&readhash($gnwayconf,\%saveconf);			
			if ($saveconf{'ENABLED'}) {
				$saveconf{'ENABLED'} = 0;
			}
			else{$saveconf{'ENABLED'} = 1;}
            &writehash($gnwayconf,\%saveconf);
			`sudo fmodify $gnwayconf`;
			system ("touch $needreload2");
		}	
	}
	if ($action eq 'apply') {
		if (-e $needreload2) {
			system ("sudo /usr/local/bin/restartgnhostlinux.py -f >/dev/null");
			system ("rm $needreload2");
			$notemessage = _("Gnway service applied successfully !");
		}
		elsif (-e $needreload1) {
			system ("sudo /usr/local/bin/restartphlinux.py >/dev/null");
			system ("rm $needreload1");
			$notemessage = _("Oray service applied successfully !");
		}
		elsif (-e $needreload3){
			system ("sudo /usr/local/bin/restartgnhostlinux.py -f >/dev/null");
			system ("sudo /usr/local/bin/restartphlinux.py >/dev/null");
			system ("rm $needreload3");
			$notemessage = _("Oray service and Gnway service applied successfully !");
		}
	}
}


$extraheader .="<script type='text/javascript' src='/include/waiting.js'></script>";
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('Dynamic DNS'), 1, $extraheader);
save();
if ((-e $needreload2) &&(-e $needreload1)) {
	system ("rm $needreload2");
	system ("rm $needreload1");
	system ("touch $needreload3");
	applybox(_("Oray service and gnway service have been changed and need to be applied in order to make the changes active!"));
}
if (-e $needreload1) {
	applybox(_("Oray service have been changed and need to be applied in order to make the changes active!"));
}
if (-e $needreload2) {
	applybox(_("Gnway service have been changed and need to be applied in order to make the changes active!"));
}
&openbigbox($errormessage, $warnmessage, $notemessage);

$lineno = $par{'line'};
display_devices(($par{'ACTION'} eq 'edit'), $lineno);
run_ajax();
check_form();
&closebigbox();
&closepage();
