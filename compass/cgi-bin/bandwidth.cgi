#!/usr/bin/perl

#file:devices.cgi
#author:zhangzheng


require '/var/efw/header.pl';
require 'ip_mac_binding.pl';
my $conffile = "/var/efw/qos/ip_limit.conf";
my $settingfile = "/var/efw/qos/settings";
my $needreload = "/var/efw/qos/needreload";
my $restart="sudo /usr/local/bin/ip_qos.py";
my $extraheader="";
my $errormessage="";


my $EDIT_PNG="/images/edit.png";
my $DELETE_PNG="/images/delete.png";
my $ON_PNG="/images/on.png";
my $ON_PNG="/images/off.png";
my %ethernet=();
for (my $num=0;$num<30 ;$num++) {
	my $n = $num+1;
	$ethernet{'eth'.$num} = "接口$n";
}
my @gottypeiface = ();
    opendir(DIR, "${swroot}/uplinks/") || return \@uplinks;
    foreach my $dir (readdir(DIR)) {
        next if ($dir =~ /^\./);
        next if (!(-f "${swroot}/uplinks/$dir/settings"));
        &readhash("${swroot}/uplinks/$dir/settings", \%set);
        push(@gottypeiface, $set{'RED_DEV'});
    }
    closedir(DIR);
my @reds = @gottypeiface;#获取WAN接口
my @greens = read_config_file("/var/efw/ethernet/br0");#获取LAN接口
my @oranges = read_config_file("/var/efw/ethernet/br1");#获取DMZ接口
my @inner = ethernet_select();

my $help_hash1 = read_json("/home/httpd/help/bandwidth_help.json","bandwidth.cgi","上行带宽","-10","30","down");
my $help_hash2 = read_json("/home/httpd/help/bandwidth_help.json","bandwidth.cgi","下行带宽","-10","30","down");
sub ethernet_select(){
	my @inner=();
	foreach my $green (@greens) {
		if ($green) {
			$green =~ /(\d+)$/;
			my $num = $1+1;
			$ethernet{$green} = "接口$num"."("._('GREEN').")";
			push(@inner,$green);
		}
	}
	foreach my $orange (@oranges) {
		if ($orange) {
			$orange =~ /(\d+)$/;
			my $num = $1+1;
			$ethernet{$orange} = "接口$num"."("._('ORANGE').")";
			push(@inner,$orange);
		}
	}
	return @inner;
}
sub check_form(){
    printf <<EOF
    <script>
    var object1 = {
       'form_name':'GBL_FORM',
       'option'   :{
                    'uplink_upload':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                             },
                    'uplink_download':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                             },
                 }
         }
    var check1 = new ChinArk_forms();
    check1._main(object1);
    //check1._get_form_obj_table("GBL_FORM");
    var object2 = {
       'form_name':'RULE_FORM',
       'option'   :{
                    'upband':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                             },
                    'downband':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                             },
                    'note':{
                               'type':'text',
                               'required':'0',
                               'check':'note|',
                             },
                    'control_ip':{
                               'type':'textarea',
                               'required':'1',
                               'check':'ip|ip_range|',
                             },
                 }
         }
    var check1 = new ChinArk_forms();
    check1._main(object2);
    //check1._get_form_obj_table("RULE_FORM");
    </script>
EOF
;
}
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
sub read_config_line($$) {
    my $linenum = shift;
	my $file=shift;
    my @lines = read_config_file($file);
	return $lines[$linenum];	
}
sub iprange($){
	my $ip_range = shift;
	if ($ip_range!~/(.*)-(.*)/) {
		return 0;
	}
	if (!validip($1) || !validip($2)) {
		return 0
	}
	my $lit = $1;
	my $large = $2;
	$lit=~s/(\d+)/sprintf("%03s",$1)/eg;
	$large=~s/(\d+)/sprintf("%03s",$1)/eg;
	$lit=~s/\.//g;
	$large=~s/\.//g;
	if (!($large > $lit)) {
		return 0;
	}
	return 1;
}
sub check_values{
	my $ip = shift;
	my $upband = shift;
	my $downband = shift;
	my @ips=split(/\n/,$ip);	
	foreach my $ip_elem (@ips) {
		$ip_elem =~s/[\r\n]//g;
		if (!(validip($ip_elem) || iprange($ip_elem))) {
			$errormessage="IP/IP范围".$ip_elem."有误,请输入正确的IP/IP范围！";
			return 0;
		}
	}
	if (!$ip) {
		$errormessage="IP/IP范围不能为空！";
		return 0;
	}
	if ($upband<1 || $upband>9999999 || $upband!~/^\d+$/) {
		$errormessage="上行带宽".$upband."有误,请输入正确上行带宽数值1-9999999！";
		return 0;
	}
	if ($downband<1 || $downband>9999999 || $downband!~/^\d+$/) {
		$errormessage="下行带宽".$downband."有误,请输入正确下行带宽数值1-9999999！";
		return 0;
	}
	return 1;
}
sub save(){
	my $action = $par{"ACTION"};
	my $sure = $par{'sure'};
	if ($action eq "addrule" || $action eq "modify") {
		save_conffile($par{'line'},$par{'control_ip'},$par{'upband'},$par{'downband'},$par{'inner_interface'},$par{'uplink'},$par{'note'});
        return;
	}
	if ($action eq "delete") {
		delete_line($par{'line'},$conffile);
		return;
	}
	if ($action eq "on") {
		toggle($par{'line'},'on');
		return;
	}
	if ($action eq "off") {
		toggle($par{'line'},'off');
		return;
	}
	if ($action eq "global_save") {
		save_global($par{'uplinks'},$par{'uplink_upload'},$par{'uplink_download'});
		return;
	}
	if ($action eq "apply") {	
		`$restart`;
		$notemessage = "带宽管理配置应用成功!";
		system("rm $needreload");
	}
}
sub save_global(){
	my $interface = shift;
	my $upband= shift;
	my $downband = shift;
	my %saveline;
	if ($upband<1 || $upband>9999999 || $upband!~/^\d+$/) {
		$errormessage="上行带宽".$upband."有误,请输入正确上行带宽数值1-9999999！";
		return 0;
	}
	if ($downband<1 || $downband>9999999 || $downband!~/^\d+$/) {
		$errormessage="下行带宽".$downband."有误,请输入正确下行带宽数值1-9999999！";
		return 0;
	}
	$upband=~s/^0+//;
	$downband=~s/^0+//;
	if (-e $settingfile) {
		&readhash($settingfile,\%saveline);
	}
	$saveline{$interface}="$upband,$downband";
	&writehash($settingfile,\%saveline);
	`sudo fmodify $settingfile`;
	$notemessage="上行线路带宽全局配置成功！";
}
sub toggle($$){
	my $line = shift;
	my $enabled = shift;
	my @lines = &read_config_file($conffile);
	if ($enabled eq 'on') {
		$lines[$line] = "#$lines[$line]";
	}
	else{
		$lines[$line] =~s/^#//;
	}
	save_config_file(\@lines,$conffile);
	%par=();
	system("touch $needreload");
}
sub save_conffile(){
	my $line = shift;
	my $ip = shift;
	my $upband = shift;
	my $downband = shift;
	my $inner = shift;
	my $uplink = shift;
	my $note = shift;
	my $saveline;
	if( ! check_values($ip,$upband,$downband)){
	   return 1;
	}
	$note =~s/,/，/g;
	$ip=~s/[\r\n]/-/g;
	$ip=~s/--/ /g;
	$upband.="Kbit";
	$downband.="Kbit";
	if ($line =~/^\d+$/) {
		$saveline = "$ip,$upband,$downband,$inner,$uplink,$note";
			&update_lines($line,$conffile,$saveline);
	}
	else{
		$saveline = "$ip,$upband,$downband,$inner,$uplink,$note";
		&append_config_file($saveline,$conffile);
	}
}
sub append_config_file($$) {
    my $line = shift;
	my $file = shift;
	if($line !~ /^$/){
		open (FILE, ">>$file");
		print FILE ($line."\n");
		close FILE;
		system("touch $needreload");
		`sudo fmodify $file`;
		%par=();
		return 1;
	}
}
sub update_lines($$$){
	my $linenum=shift;
	my $file=shift;
	my $saveline=shift;


	my @lines = &read_config_file($file);
	if ($lines[$linenum] =~ /^#/ && $par{'ACTION'} eq "modify") {
		$saveline = "#".$saveline;
	}
	$lines[$linenum] = $saveline;
	&save_config_file(\@lines,$file);
	system("touch $needreload");
	%par=();
}
sub delete_line($$){
	my $linenum=shift;
	my $file=shift;
	my @save_lines;
	my @rulelist=read_config_file($conffile);
	for (my $num=0;$num<@rulelist ;$num++) {
		if ($num ne $linenum) {
			push(@save_lines,$rulelist[$num]);
		}
	}
	save_config_file(\@save_lines,$file);
	system("touch $needreload");
	%par=();
}
sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;
	my $rule_flag=0;
	my @uplinkd;
	my @rule_line=read_config_file($settingfile);
	foreach my $line (@rule_line) {
		if ($line) {
			my @tmp = split(/=/,$line);
			push (@uplinkd,$tmp[0]);
		}
	}
	my $rule_flag = @uplinkd;
	my %selected;
	my %settings;	
	my $ip,$upband,$downband,$inner,$uplink,$note;
	my $uplink_up,$uplink_down;
	if (-e $settingfile) {
		readhash($settingfile,\%settings);
	}
	($uplink_up,$uplink_down) = split(/,/,$settings{$reds[0]});
    if (($is_editing) && ($par{'sure'} ne 'y')) {
	    my @rl=split(/,/,read_config_line($line,$conffile));
		$ip = $rl[0];
		$ip =~s /#//;
		$upband = $rl[1];
		$downband = $rl[2];
		$inner = $rl[3];
		$uplink = $rl[4];
		$note = $rl[5];
		$ip =~s/\s/\r/g;
		$upband =~s/Kbit//;
		$downband =~s/Kbit//;
    }
	else{
		$ip = $par{"control_ip"};
		$upband = $par{"upband"};
		$downband = $par{"downband"};
		$inner = $par{"inner"};
		$uplink = $par{"uplink"};
		$note = $par{"note"};
	}
	$selected{$inner} = "selected";
	$selected{$uplink} = "selected";
	my $action = 'addrule';
    my $title = _('添加带宽管理规则');
	my $buttontext=_("Add");
    if ($is_editing || $par{"ACTION"} eq "modify") {
        $action = 'modify';
        $title = _('编辑带宽管理规则');
		$buttontext = _("Edit");
    }
	if($par{'ACTION'} eq 'edit' || $errormessage ne '') {
        $show = "showeditor";
    }
	if ($par{'ACTION'} ne "global_save") {
		$show = "";
	}
	openbox('100%', 'left', _('上行线路带宽配置'));
	#openaddbox("上行线路带宽配置", "全局配置", $show, "Globle", @errormessages);
	printf <<EOF
	<form name="GBL_FORM" method='post' action='$self' enctype='multipart/form-data'>
     <table width="100%" cellpadding="0" cellspacing="0">
	 <tr class="odd">
	 <td class="add-div-type need_help" style="width:10%">上行线路</td>
	 <td><select id="uplinks" name="uplinks" style="width:130px" onchange="change_value()">
EOF
;
	foreach my $elem (@reds) {
		print "<option value='$elem'>$ethernet{$elem}</option>"
	}
printf <<EOF
	 </select></td>
	 </tr>
	 <tr class="env">
	 <td class="add-div-type need_help"  style="width:10%">上行带宽 *$help_hash1</td>
	 <td><input type="text" id="upload" maxlength="7" value="$uplink_up" name="uplink_upload" />Kbit</td>
	 </tr>
	 <tr class="odd">
	 <td class="add-div-type need_help" style="width:10%">下行带宽 *$help_hash2</td>
	 <td><input type="text" id="download" maxlength="7" value="$uplink_down" name="uplink_download" />Kbit</td>
	 </tr>
	 <tr class="table-footer">
		<td colspan="2"><input id="savebutton" class='submitbutton net_button' type='submit' name='ACTION_RESTART' value='保存' /></td>
	</tr>
	 </table>
	<input type="hidden" name="ACTION" value="global_save">
	</form>
EOF
;	
	closebox();
	#&closeaddbox("保存", _("Cancel"), "routebutton", "createdevice", "$ENV{SCRIPT_NAME}");
	$show = "";
	if($par{'ACTION'} eq 'edit' || $errormessage ne '') {
        $show = "showeditor";
    }
	if ($par{'ACTION'} eq "global_save") {
		$show = "";
	}
if($rule_flag){
    openeditorbox($title, $title, $show, "addqosdevice", @errormessages);
    printf <<EOF
    </form>
    <form name="RULE_FORM" method='post' action='$self' enctype='multipart/form-data'>
     <table width="100%" cellpadding="0" cellspacing="0"> 
	   <tr class='odd'>
	   <td class="add-div-type need_help">IP/IP范围 *</td>
	   <td>
	   <div id="dst_ip_t" style="display: table-row;">请输入IP/IP范围（每行一个）</div>
	   <div id="dst_ip_v" style="display: table-row;">
			<textarea style="width: 250px; height: 90px;" wrap="off" name="control_ip">$ip</textarea>
		</div>
	   </td>
       </tr> 
	   <tr class='env'>
	   <td class="add-div-type need_help" style="width:10%">上行带宽 *</td>
	   <td><input type="text" maxlength="7" value="$upband" name="upband" />Kbit</td>
       </tr>
	   <tr class='odd'>
	   <td class="add-div-type need_help" style="width:10%">下行带宽 *</td>
	   <td><input type="text" maxlength="7" value="$downband" name="downband" />Kbit</td>
	   </tr>
	   <tr class='env'>
	   <td class="add-div-type need_help">内部接口</td>
	   <td>
EOF
;
		print "<select name='inner_interface' style='width:100px'>";
		foreach my $elem (@inner) {
			print "<option $selected{$elem} value='$elem'>$ethernet{$elem}</option>";
		}
		print "</select>";
printf <<EOF
	   </td>
       </tr>
	   <tr class='odd'>
	   <td class="add-div-type need_help">流出接口</td>
	   <td>
	   <select name="uplink" style="width:100px">
	   
EOF
;
	foreach my $elem (@uplinkd) {
		print "<option $selected{$elem} value='$elem'>$ethernet{$elem}</option>"
	}
printf <<EOF
	   </select>
	   </td>
       </tr>
	   <tr class='env'>
	   <td class="add-div-type need_help">注释</td>
	   <td><input maxlength="50" size="50" value="$note" type="text" name="note" /></td>
       </tr>
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
	my $enabled_gif = "/images/off.png";
	my $enabled_alt = _('Disabled (click to enable)');
    display_add($is_editing, $line);
    printf <<END
		
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr>
            <td class="boldbase" style="width:10%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>
			<td class="boldbase" style="width:10%;">%s</td>
			<td class="boldbase" style="width:10%;">%s</td>
			<td class="boldbase" style="width:10%;">%s</td>
			<td class="boldbase" style="width:10%;">%s</td>
		<td class="boldbase" style="width:10%;">%s</td>
        </tr>
	
END
	, _('序号')
	, _('带宽管理类型')
    , _('上行带宽')
    , _('下行带宽')
	,_('内部接口')
	,_('流出接口')
	,_('注释')
	,_('活动/动作')
    ;
my $num=0;
my $enabled_gif = $ENABLED_PNG;
my $enabled = "on";
my @rulelist=read_config_file($conffile);
foreach my $ruleline (@rulelist) {
	my @rl = split(/,/,$ruleline);
	my $ln = $num+1;
	if (!$rl[5]) {
		$rl[5] = "无";
	}
	if ($rl[0] =~ /^#/) {
		$enabled_gif = $DISABLED_PNG;
		$enabled = "off";
	}
	else {
		$enabled_gif = $ENABLED_PNG;
		$enabled = "on";
	}
	$rl[0] =~s/^#//;
	printf <<EOF
	<tr>
	<td>$ln</td>
	<td>$rl[0]</td>
	<td>$rl[1]</td>
	<td>$rl[2]</td>
	<td>$ethernet{$rl[3]}</td>
	<td>$ethernet{$rl[4]}</td>
	<td>$rl[5]</td>
	<td>
	<form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" title="%s" />
                <input type="hidden" name="ACTION" value="$enabled">
                <input type="hidden" name="line" value="$num">
            </form>
	<form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="line" value="$num">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" onsubmit='return confirm("确认删除？")'>
                <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="line" value="$num">
            </form>
	</td>
	</tr>
EOF
;
	$num++;
}
if (!$num) {
	no_tr(8,"无内容");
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

$extraheader .="<script type='text/javascript' src='/include/ip_mac_binding.js'></script><script type='text/javascript' src='/include/bandwidth.js'></script><style type='text/css'>\@import url(/include/ip_mac_binding.css);</style>";
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('带宽管理'), 1, $extraheader);
save();
if (-e $needreload) {
	applybox(_("带宽管理规则以改变需要应用以使规则生效!<p style='color:red'>警告:应用静态QOS规则将会覆盖动态QOS中对应设备的规则！</p>"));
}
&openbigbox($errormessage, $warnmessage, $notemessage);

$lineno = $par{'line'};
display_devices(($par{'ACTION'} eq 'edit'), $lineno);
check_form();
&closebigbox();
&closepage();
