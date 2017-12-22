#!/usr/bin/perl

#file:devices.cgi
#author:zhangzheng


require '/var/efw/header.pl';
require 'ESONCalendar.pl';
my $settingfile = "/var/efw/risk/warning/settings";
my $attfile = "/var/efw/risk/warning/attacktype";
my $extraheader="";
my $errormessage="";
if(! -e "/var/efw/risk/warning"){
	system("mkdir /var/efw/risk/warning");
}
my @day =  (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23);
my @hour = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59);
my %week = (
			1 => "星期一",
			2 => "星期二",
			3 => "星期三",
			4 => "星期四",
			5 => "星期五",
			6 => "星期六",
			7 => "星期天"
);
my @attlines = read_config_file($attfile);
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
sub save(){
	my $action = $par{"ACTION"};
	my $sure = $par{'sure'};
	my %save_setting;
	if ($action eq "save") {
		$par{'START_DAY'} = change_date($par{'START_DAY'});
		$par{'END_DAY'} = change_date($par{'END_DAY'});
		$par{'ALERT_DEVICE'}=~s/[\n\r]/=/g;
		$par{'ALERT_DEVICE'}=~s/==/\|/g;
		$par{'ALERT_TIME_DAY'} = $par{'START_DAY'}."|".$par{'END_DAY'};
		$par{'ALERT_TIME_HOUR'} = $par{'START_HOUR'}.":".$par{'START_MIN'}."|".$par{'END_HOUR'}.":".$par{'END_MIN'};		
		###判断是否全选了攻击类型 
		my $nums = 0;
		my $nums = split(/\|/,$par{'ALERT_TYPE'});
		if ($nums == 35) {
			$par{'ALERT_TYPE'}= "ALL";
		}
		###end
		if ($par{'ALERT_TIME_WEEK'} eq "1|2|3|4|5|6|7") {
			$par{'ALERT_TIME_WEEK'} = "ALL";
		}
		if (!check_value()) {
			return 0;
		}
		if (!$par{'ALERT_DEVICE'}) {
			$par{'ALERT_DEVICE'} = "ALL";
		}
		if (!$par{'ALERT_MAIL'}) {
			$par{'ALERT_MAIL'} = "NULL";
		}
		 open(FILE,">$settingfile");
		 print FILE "ALERT_METHOD=$par{'ALERT_METHOD'}\n";
		 print FILE "ALERT_DEVICE=$par{'ALERT_DEVICE'}\n";
		 print FILE "ALERT_TYPE=$par{'ALERT_TYPE'}\n";
		 print FILE "ALERT_TIME_DAY=$par{'ALERT_TIME_DAY'}\n";
		 print FILE "ALERT_TIME_WEEK=$par{'ALERT_TIME_WEEK'}\n";
		 print FILE "ALERT_TIME_HOUR=$par{'ALERT_TIME_HOUR'}\n";
		 print FILE "ALERT_LEVEL=$par{'ALERT_LEVEL'}\n";
		 print FILE "ALERT_MAIL=$par{'ALERT_MAIL'}\n";
		 close(FILE);
		`sudo fmodify $settingfile`;
		 $notemessage = "告警设置参数配置成功！";
	}
}
sub check_value{
	if (!$par{'ALERT_METHOD'}) {
		push(@errormessages,  _('告警方式必须选择一种！'));
	}
 	if ($par{'ALERT_METHOD'} =~ "MAIL" && !validemail($par{'ALERT_MAIL'})) {
		push(@errormessages,  _('邮件地址不正确！'));
	}
	foreach my $ip (split(/\|/,$par{'ALERT_DEVICE'})) {
		if (!is_ipaddress($ip)) {
			my $message = "IP地址".$ip."不正确！".$par{'ALERT_DEVICE'};
			push(@errormessages, $message );
		}
	}
	if ($par{'ALERT_TYPE'} eq "") {
		push(@errormessages,  _('攻击类型不能为空！'));
	}
	if (!$par{'ALERT_TIME_WEEK'}) {
		push(@errormessages,  _('周不能为空！'));
	}
	if(!(dateToFilestring($par{'END_DAY'}) > dateToFilestring($par{'START_DAY'}))){
		push(@errormessages,  _('结束日期必须大于起始日期！'));
	}
	if (!$par{'ALERT_LEVEL'}) {
		push(@errormessages,  _('告警等级不能为空！'));
	}
	if ($#errormessages ne -1) {
		return 0;
	}
	return 1;
}
sub display_setting(){
	my %selected;
	my $style="style='display:none;'";
	if ($par{'ALERT_METHOD'} =~ "MAIL") {
		$style="style='display:inline;'";
	}
	my $all_selected;
	my $checked;
	if ($par{'ALERT_TYPE'} eq "ALL") {
		$checked="checked='checked'";
		$all_selected = "selected";
	}
	else{
		foreach my $elem (split(/\|/,$par{'ALERT_TYPE'})) {
			$selected{$elem} = "selected";
		}
	}
	my $num = 0;
	foreach my $elem (split(/\|/,$par{'ALERT_LEVEL'})) {
		$selected{$elem} = "selected";
		$num ++;
	}
	if ($num == 4) {
		$checked1="checked='checked'";
	}
	my @week_day = split(/,/,$par{'ALERT_TIME_WEEK'});
	my @att_type = split(/,/,$par{'ALERT_TYPE'});
	my @levels = split(/,/,$par{'ALERT_LEVEL'});
	my ($start_day,$end_day) = split(/\|/,$par{'ALERT_TIME_DAY'});
	my ($start_time,$end_time) = split(/\|/,$par{'ALERT_TIME_HOUR'});
	if ($par{'ALERT_DEVICE'} ne "ALL") {
		$par{'ALERT_DEVICE'} =~s/\|/\n/g;
	}
	else{$par{'ALERT_DEVICE'} = "";}
	if ($par{'ALERT_METHOD'} =~ /INTERFACE/) {
		$selected{'INTERFACE'} = "selected";
	}
	if ($par{'ALERT_METHOD'} =~ /MAIL/) {
		$selected{'MAIL'} = "selected";
	}
	if ($par{'ALERT_MAIL'} eq "NULL") {
		$par{'ALERT_MAIL'} = "";
	}
	printf <<EOF
	<form method='post' action='$self' enctype='multipart/form-data'>
	<input type='hidden' name='ACTION' value='save' />
	<table cellpadding="0" cellspacing="0" width="100%" border='0' >
	<tr class="env">
		<td class="add-div-type">告警方式 *</td>
		<td style="width:20%"><select style="width:128px" id="w_type" multiple name="ALERT_METHOD">
		<option value="INTERFACE" $selected{'INTERFACE'}>界面告警</option>
		<option value="MAIL" $selected{'MAIL'}>邮件告警</option>
		</select></td>
		<td colspan="2" ><div $style id="mail">邮件地址 *<input type="text" name="ALERT_MAIL" value="$par{'ALERT_MAIL'}" /></div></td>
	</tr>
	<tr class="odd">
		<td class="add-div-type">告警设备 </td>
		<td>
			<div  style="display: table-row;">请输入IP/IP范围(每行一个)</div>
			<div  style="display: table-row;">留空表示所有</div>
		</td>
		<td colspan="2">
			<textarea name="ALERT_DEVICE">$par{'ALERT_DEVICE'}</textarea>
		</td>
	</tr>
	<tr class="env">
		<td class="add-div-type">攻击类型 *</td>
		<td><input $checked type="checkbox" name="all_att" id="all_att" />全选</td>
		<td colspan="2"><select multiple="multiple" style="height:70px" name="ALERT_TYPE" id="ATTACK_TYPE">
EOF
;
	my $nums = 0;
	foreach my $line (@attlines) {
		if ($line) {
			my @tmp = split(/,/,$line);
			print "<option class='for_select' value='$nums' $all_selected $selected{$nums} >$tmp[0]--$tmp[1]</option>";
			$nums ++;
		}
	}
	printf <<EOF
		</select></td>
	</tr>
	<tr class="odd">
		<td class="add-div-type" rowspan="2">告警时间</td>
EOF
;	
	if (!$par{'ALERT_TIME_DAY'}) {
		$end_day = `date "+%Y-%m-%d"`;
		$start_day = `date "+%Y-%m-%d"`;
	}
	printf <<EOF
	<td>
	 起始时间点：<input type="text" SIZE="12" id="startDate" name='START_DAY' value="$start_day" />
		<script type="text/javascript"> 
		ESONCalendar.bind("startDate");
		</script>
		</td>
		<td colspan="2">
			结束时间点：<input type="text" SIZE="12" id="endDate" name='END_DAY' value="$end_day" />
			<script type="text/javascript">
			ESONCalendar.bind("endDate");
			</script>  
            </td>
	</tr><tr class="env">
			<td>周:
			<select  id="week" name="ALERT_TIME_WEEK" multiple style="width: 150px; height: 80px;">
EOF
;
if($par{'ALERT_TIME_WEEK'} eq "ALL"){
	foreach my $day(sort keys %week){
		print "<option class='for_week' selected = 'selected' value='$day'>$week{$day}</option>";
	}
}else{
	my @weeks = split(/|/,$par{'ALERT_TIME_WEEK'});
	foreach my $day(sort keys %week)
		{
		my $key = 0;
		foreach my $week(@weeks)
		{
			if($week eq $day)
			{
				$key = 1;
			}
		}
		if($key)
		{
			print "<option selected = 'selected' value='".$day."'>".$week{$day}."</option>";
		}else{
			print "<option value='".$day."'>".$week{$day}."</option>";
		}
	}
}
my @start = split(/:/,$start_time);
my @end = split(/:/,$end_time);

printf <<EOF
			</select>

			</td>
			<td>每日起始时间
			<select name="START_HOUR">
EOF
;

foreach my $hour (@day)
{
	if($start[0] eq $hour)
	{
		print "<option selected value='$hour'>$hour</option>";
	}else{
		print "<option value='$hour'>$hour</option>";
	}
}
printf <<EOF
			</select>
			时
			<select  name="START_MIN">
EOF
;

foreach my $min (@hour)
{
	if($start[1] eq $min)
	{
		print "<option  selected value='$min'>$min</option>";
	}else{
		print "<option value='$min'>$min</option>";
	}
}


printf <<EOF
	</select>
	</td>
	<td >每日结束时间
	<select name="END_HOUR">
EOF
;

foreach my $hour (@day)
{
	if($end[0] eq $hour)
	{
		print "<option selected value='$hour'>$hour</option>";
	}else{
		print "<option value='$hour'>$hour</option>";
	}
}
printf <<EOF
			</select>时
			<select name="END_MIN">
EOF
;
foreach my $min (@hour)
{
	if($end[1] eq $min)
	{
		print "<option  selected value='$min'>$min</option>";
	}else{
		print "<option  value='$min'>$min</option>";
	}
}

printf <<EOF
			</select></td>
			</tr>
	<tr class="odd">
		<td class="add-div-type">告警等级</td>
		<td><input type="checkbox" name="all_level" $checked1 id="all_level" />全选</td>
		<td colspan="2"><select name="ALERT_LEVEL" style="width:60px" multiple="multiple">
		<option class="for_level" value="URGENT" $selected{'URGENT'}>紧急</option>
		<option class="for_level" value="SERIOUS" $selected{'SERIOUS'}>严重</option>
		<option class="for_level" value="COMMON" $selected{'COMMON'}>一般</option>
		<option class="for_level" value="SLIGHT" $selected{'SLIGHT'}>微小</option>
		</select></td>
	</tr>
	<tr class="table-footer">
		<td colspan="4"><input id="savebutton" class='submitbutton net_button' type='submit' name='ACTION_RESTART' value='保存' /></td>
	</tr>
	</table>
	</form>
EOF
;
}
$extraheader .="<script type='text/javascript' src='/include/warningsetting.js'></script>";
$extraheader .= "<script type='text/javascript' src='/include/ESONCalendar.js'></script><link rel='stylesheet' href='/include/datepicker/css/datepicker.css' type='text/css' />";
&getcgihash(\%par);
&showhttpheaders();


&openpage(_('带宽管理'), 1, $extraheader);

save();
if (-e $settingfile) {
	readhash($settingfile,\%par);
}

if (-e $needreload) {
	applybox(_("带宽管理规则以改变需要应用以使规则生效!<p style='color:red'>警告:应用静态QOS规则将会覆盖动态QOS中对应设备的规则！</p>"));
}
foreach my $line(@errormessages){
	$errormessage.=$line."<br />";
}

&openbigbox($errormessage, $warnmessage, $notemessage);
openbox('100%', 'left', _('告警设置'));

display_setting();

closebox();
&closebigbox();
&closepage();
