#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:用户管理页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04       
#===============================================================================


require '/var/efw/header.pl';
use Digest::MD5;

my %par;
my $fingerdir    =  "/var/efw/userinfo/finger_info/";
my $user_conf    =  "/var/efw/userinfo/userslist";#用户信息所在文件路径
my $user_lock    =  "/var/efw/userinfo/user_lock_tmp";#用户锁定所在文件路径
my $passwd_modify_time_file = "/var/efw/userinfo/passwd_modify_time";
my $time_out     =  "/var/efw/userinfo/timeout";#用户登录时间文件路径
my $is_editing   =  0;
my $action       =  'add';
my $sure         =  '';
my $change       =  "";
my $button       =  _("Add");
my $errormessage =  "";
my $warnmessage  =  "";
my $notemessage  =  "";
my @user_info    =  read_users_file();
my $edit_PNG     =  "/images/edit.png";
my $delete_PNG   =  "/images/delete.png";
my $ini_name     =  "";#点击编辑按钮时，用户名框默认的值
my $ini_psw      =  "";#点击编辑按钮时，密码框默认的值
my $discription  =  "";#点击编辑按钮时，描述框默认的值
my $mail_box     =  "";#点击编辑按钮时，邮箱框默认的值
my $bgcolor      =  "";#点击编辑后的td高亮样式
my $line         =  "";#标记当前是第几行被选中
my $is_edit      =  "";#标记当前用户名是否可以改变
my $is_show      =  "";#表示当前密码框和确认密码框是否显示
my $button_show  =  "hidden_class";#表示当前密码框和确认密码button是否显示
my $show         =  "";
my $psdLength    = &readPsdLength();
my $title;
my $user_typed;
my @errormessages;
=p
my %user_type = (
	1=>"日志管理员",
	0=>"配置管理员",
	2=>"用户管理员",
	3=>"安全保密员",
);
=cut
my @cur_user=getCurUser();
my $now_user = $cur_user[0];
if ($cur_user[0] eq "admin") {
	$title = "添加配置管理员";
	$user_typed = "0";
}
if ($cur_user[0] eq "logerauth") {
	$title = "添加日志审计员";
	$user_typed = "3";
}
if ($cur_user[0] eq "safeauth") {
	$title = "添加安全保密员";
	$user_typed = "1";
}
###添加指纹信息 Elvis 2012-7-14
if(! -e "/var/efw/userinfo/finger_info"){
	system("mkdir /var/efw/userinfo/finger_info");
}
###添加指纹信息 END
sub save(){
	if($par{'ACTION'} ne ""){
		$action = $par{'ACTION'};
	}
	$line       = $par{'line'};
	$sure       = $par{'sure'};
	$change     = $par{'test'};
	my $name    = $par{'name'};
    my $psw     = $par{'psw'};
	my $repsw   = $par{'re_psw'};
	my $dis     = $par{'discription'};
	my $finger  = $par{'tpdata'};#指纹信息获取
	$dis =~ s/,/，/g;
	$dis =~ s/\n//g;
	my $mail    = $par{'mail'};
	my $new_str = "";

	###添加指纹信息 Elvis 2012-7-2
	if (!$finger && $par{'finger'}) {
		$errormessage = "请刷入指纹信息!";
		return 0;
	}

	###添加指纹信息 END
	if (($par{'ACTION'} eq 'add')||(($par{'ACTION'} eq 'edit') && ($sure eq 'y'))) {
		#print $line;
		$psw = &decryptFn($psw);
		$repsw = &decryptFn($repsw);
		if(check_form_perl($name,$psw,$repsw,$dis,$mail,$change,$action)){
			if(($par{'ACTION'} eq 'edit') && ($sure eq 'y')){
				foreach my $str(@user_info){
					if ( $str eq "" ) {
						next; #过滤掉空行 Added By WangLin 2015.04.17
					}
					my @temp = split(",",$str);
					if($temp[0] eq $name){
						if($name eq 'admin' || $name eq 'logerauth' || $name eq 'safeauth'){
							$par{'USER_TYPE'} = 2;
						}
						if($psw){
							# my $md5 = Digest::MD5->new;#将密码用MD5 加密处理
							# $md5->add($psw);
							# $psw = $md5->hexdigest;


							#使用私钥解密modify by pujiao 2017-3-22
							# $psw = &decryptFn($psw);

							$new_str .= $name.",".$psw.",".$dis.",".$mail.",".$par{'USER_TYPE'}.",".$par{'lock'}.","."\n";
							# 修改密码，则重置修改密码的时间戳
							&reset_passwd_modify_time( $name );
						}
						else{
							$new_str .= $name.",".$temp[1].",".$dis.",".$mail.",".$par{'USER_TYPE'}.",".$par{'lock'}.","."\n";
						}
					}
					else{
						$new_str .= $str."\n";
					}
				}
				delete_user_file($new_str);
			    $log_message = "修改用户$name";
        		&user_log($log_message);	
				$notemessage = _('Modify user information successful');
			}
			else{
				# my $md5 = Digest::MD5->new;#将密码用MD5 加密处理
				# $md5->add($psw);
				# $psw = $md5->hexdigest;

				# $psw = &decryptFn($psw);

				# 2016-09-18 modify by pujiao : add a signl of time
				my $time_str = time;  
				$new_str .= $name.",".$psw.",".$dis.",".$mail.",".$par{'USER_TYPE'}.",0,";
				append_user_file($new_str);
				$notemessage = _('Add user successful');
				$log_message = "添加用户$name";
				# 新增用户，则重置修改密码的时间戳，确保之前如果存在这样的用户也重置其时间戳
				&reset_passwd_modify_time( $name );
        		&user_log($log_message);	
			}
			###添加指纹信息 Elvis 2012-7-2
			if ($finger) {
				save_finger_info($name,$finger);
			}
			###添加指纹信息 END
			$par{'ACTION'} = 'add';
			$action = 'add';
		}
	}
	###添加指纹信息 Elvis 2012-7-16
	if ($action eq "delete_finger") {
		delete_finger_info();
	}
	###添加指纹信息 END
	if($action eq "delete")
	{
		my $j = 0;
		my $new_str = "";
		my $delete_user = "";
		foreach my $str(@user_info){   
			my @temp = split(",",$str);
			if($j ne $line){
				$new_str .= $str."\n";
			}
			else{
				my @temp = split(",",$str);
				$delete_user = $temp[0];
			}		
	    $j++;
		}
		delete_user_file($new_str);
		###添加指纹信息 Elvis 2012-7-2 删除用户时删除指纹文件
		my $ufile = $fingerdir.$par{'ufile'};
		system("rm $ufile");
		###添加指纹信息 END
		$log_message = "删除用户$delete_user";
		# 删除用户，则重置修改密码的时间戳
		&reset_passwd_modify_time( $name );
        &user_log($log_message);	
		$notemessage = _('Delete user "%s" successful',$delete_user);
		$action ="add";
	}
	
	if($action eq "lock")
	{
		my $j = 0;
		my $new_str = "";
		my $delete_user = "";
		foreach my $str(@user_info)
		{
			if($j ne $line){
				$new_str .= $str."\n";
			}
			else{
				my @temp = split(",",$str);
				if($par{'LOCK'}){
					readhash($user_lock,\%user_lock_hash);
					$temp[5] = "0";
					$delete_user = $temp[0];
					$user_lock_hash{$delete_user} = "0";
					writehash($user_lock,\%user_lock_hash);
	                $log_message = "解锁用户$delete_user";
        			&user_log($log_message);
				}
				else{
					$temp[5] = "1";
					$delete_user = $temp[0];
					$log_message = "锁定用户$delete_user";
        			&user_log($log_message);
				}
				foreach my $str(@temp){
					$new_str .= $str.",";
				}
				$new_str .= "\n";
			}
			$j++;
		}
		delete_user_file($new_str);
		
		$notemessage = _('操作已成功');
		$action ="add";
	}
	

}


# 重置某个用户密码修改时间
sub reset_passwd_modify_time($) {
    my $username = shift;
    my %user_passwd_md_time;
    my %timeout_user;
    if ( !-f $passwd_modify_time_file ) {
        system( "touch $passwd_modify_time_file" );
        return;
    }
    readhash( $passwd_modify_time_file, \%user_passwd_md_time );
    if ( exists $user_passwd_md_time{$username} ) {
        delete $user_passwd_md_time{$username};
        writehash( $passwd_modify_time_file, \%user_passwd_md_time );
       
    }
}

#将新添加的用户信息写入文件中
sub append_user_file($) {
    my $line = shift;
    open (FILE, ">>$user_conf");
    print FILE $line."\n";
    close FILE;
	`sudo fmodify $user_conf`;
}

#将删除后的用户信息写入文件中
sub delete_user_file($) {
    my $line = shift;
    open (FILE, ">$user_conf");
    print FILE $line;
    close FILE;
	`sudo fmodify $user_conf`;
}

###添加指纹信息 Elvis 2012-7-2
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
sub delete_finger_info(){
	my $finger_info_num = $par{'finger_num'};
	my $fingerfile = $fingerdir.$par{'user'};
	my @save_finger_infos;
	foreach my $elem (read_config_file($fingerfile)) {
		my @tmp = split(/,/,$elem);
		if ($tmp[1] == $finger_info_num) {
			next;
		}
		push(@save_finger_infos,$elem);
	}
	save_config_file(\@save_finger_infos,$fingerfile);
	my @lasts = read_config_file($fingerfile);
	my $nums = @lasts;
	if ($nums < 1) {
		system("rm $fingerfile");
	}
}
sub change_value($){
	my $index = shift;
	if ($index eq "A") {
		$index = 10
	}
	return $index;
}
sub save_finger_info($$){
	my $user   = shift;
	my $finger = shift;
	my $userfile=$fingerdir."$user";
	my @finger_file="";
	opendir(DIR,"$fingerdir");
	my @finger_file = readdir(DIR);
	close(DIR);
	my $flag = 0;
	foreach my $file (@finger_file) {
		next if ($file =~ /^\./);
		next if ($file !~ /$user/);
		$flag = 1;
	}
	
	my @save_line = split(/&&/,$finger);
	for (my $num=0;$num<@save_line ;$num++) {
		my $position = substr($save_line[$num],3,1);
		$save_line[$num] = $save_line[$num].",".$position;
	}
	save_config_file(\@save_line,$userfile);
}
sub save_config_file($$) {
    my $ref = shift;
	my $file= shift;
    my @lines = @$ref;
    open (FILE, ">$file");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
	$reload=1;
	`sudo fmodify $file`;
    close(FILE);
}
###添加指纹信息 END

sub check_form_perl($$$$$$$){
	my $name  = shift;
	my $psw   = shift;
	my $repsw = shift;
	my $dis   = shift;
	my $mail  = shift;
	my $change= shift;
	my $type  = shift;#标记当前是添加还是编辑
	my $is_exit = 0;
	
	if($type eq "add")
	{
		if (!$mail) {
			 push(@errormessages,_('邮箱不能为空.'));
		}elsif($mail !~ /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/) 
		{
			 push(@errormessages,_('邮箱地址格式不正确.'));
		}
		if($name eq "")
		{
			 push(@errormessages, _('用户名不能为空.'));
		}elsif($name !~ /^[a-zA-Z0-9]*$/)
		{
			 push(@errormessages, _('用户名格式不正确.'));
		}elsif(length($name)>20){
			 push(@errormessages,_('用户名长度必须小于等于20.'));
		}elsif(length($name)<4)
		{
			 push(@errormessages,_('用户名长度必须大于等于4.'));
		}elsif($psw eq ""){
		
			 push(@errormessages,_('密码不能为空.'));
		
		}
		elsif($psw !~ /^[a-zA-Z0-9]*$/){
		
			 my $pswCheckMesg = '密码含有非法字符！'; 
			 push(@errormessages, $pswCheckMesg);
		
		}
		elsif($psw ne $repsw){
		
			 push(@errormessages,_("密码输入不一致."));
			 
		}
		else{
				foreach my $exit_user(@user_info)
				{
					my @temp_usr = split(",",$exit_user);
					if($temp_usr[0] eq $name)
					{
						$is_exit = 1;
					}
				}
				if($is_exit eq 1)
				{
					 push(@errormessages, _('用户名已存在.'));
				}
		}	
	}
	if($change eq "change")
	{
		if($psw eq "")
		{
			 push(@errormessages,_('密码不能为空.'));
		}
		elsif($psw !~ /^[a-zA-Z0-9]*$/)
		{
			push(@errormessages, _('密码包含非法字符！'));
		}
		# elsif(length($psw) == 32){
			 # my $pswCheckMesg = '密码长度必须等于' . $psdMinLength . '个字符'; 
			 # push(@errormessages, $pswCheckMesg);
		# }
		if($psw ne $repsw)
		{
			 push(@errormessages,_("密码和确认密码不一致"));
		}
	}
	if (!$mail) {
		 push(@errormessages,_('邮箱不能为空.'));
	}elsif($mail !~ /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/) 
	{
		 push(@errormessages,_('邮箱地址格式不正确.'));
	}
	if ($#errormessages ne -1) {
        return 0;
    }
    return 1;
}



sub show_add()
{
    $button = _("Save");
	my $finger_scr = "指纹验证";
	if($par{'USER'} eq 'admin')
	{
		$user_type_show = "hidden_class";
	}else{
		$user_type_show = "";
	}
		
		
	if($action eq 'edit')
	{
			$title       = _("编辑用户");
			$is_edit     = "readonly='readonly'";
			$is_show     = "hidden_class";
			$button_show = "";
			$is_editing  = 1;
			if($action eq "edit")
			{
				my $j        = 0;
				foreach my $str(@user_info)
				{
					if($j eq $line)
					{
						my @temp      = split(",",$str);
						$ini_name     = $temp[0];
						$ini_psw      = $temp[1];
						$discription  = $temp[2];
						$mail_box     = $temp[3];
					}
					$j++;
				}
		
			}
	}
	else{
			$ini_name     = $par{'name'};
			$discription  = $par{'discription'};
			$mail_box     = $par{'mail'};
		}
    if($action eq 'edit' || $errormessage ne '') 
	{
        $show = "showeditor";
		$finger_scr = "修改指纹";
	}
	my @ini_values=(0,0,0,0,0,0,0,0,0,0);
	my $ini_value,$fingerinfo;
	###添加指纹信息 Elvis 2012-7-2
	if (-e $fingerdir.$ini_name) {
		foreach my $line (read_config_file($fingerdir.$ini_name)) {
			my ($a,$b) = split(/,/,$line);
			$fingerinfo = $fingerinfo."&&".$a;
			$b = change_value($b);
			$b = $b - 1;
			$ini_values[$b]=1;
		}
	}
	foreach my $elem (@ini_values) {
		$ini_value.=$elem;
	}
	$fingerinfo =~s/^&&//;
	###添加指纹信息 END
	&openeditorbox($title,"", $show, "createrule",);
printf <<EOF
</form>
<form name="USER" action="$ENV{ 'SCRIPT_NAME' }" method="post" id ="forPswMd5"/>
<table width="100%" cellpadding="0" cellspacing="0">
<tr class="env">
	<td width="15%" class="add-div-table">%s*</td>
	<td><input type="text" $is_edit  name="name" id="name"  value="$ini_name"   /><span id="name_span"  class="note_str hidden_class note" > %s</span><span id="name_span_note"></span></td>
</tr>
<tr class="odd">
	<td width="15%" class="add-div-table">%s*</td>
	<td><input class="$is_show" type="password" name="psw" id="psw"  value="" /><input class="hidden_class" type="text"  name="test" id="hidden"  value="" /> <span id="psw_span" class="note_str hidden_class note" >%s</span><span id="psw_span_note"></span><input id="change_psw"  type="button" value="%s" class="$button_show" /></td>
</tr>
<tr class="env $is_show" id="repswshow">
	<td width="15%" class="add-div-table">%s*</td>
	<td><input type="password" name="re_psw" id="re_psw"  value="" )" /> <span id="re_psw_span" class="note_str hidden_class note" > %s</span><span id="re_psw_span_note"></span></td>
</tr>
<tr class="odd hidden_class" >
	<td width="15%" class="add-div-table">用户类型</td>
	<td><input type="text" name="USER_TYPE" value="$user_typed">
EOF
,_("Username")
,_("5至14个字符，其中包括(数字、字母)")
,_("密码")
,_("password length of 6-14,the letter a case-sensitive")
,_("Change password")
,_("Verify password")
,_("password should be identical")
;

printf <<EOF
</td>
</tr>

<tr class="odd">
	<td width="15%" class="add-div-table">%s</td>
	<td> <input type="text" name="discription" style="width:154px" value="$discription"></td>
</tr>
<tr class="env">
	<td width="15%" class="add-div-table">%s*</td>
	<td><input type="text" name="mail" id="mail" value="$mail_box"  /> <span id="mail_span" class="note_str hidden_class note" > %s</span><span id="mail_span_note"></span></td>
</tr>
<tr class="odd">
	<td width="15%" class="add-div-table">$finger_scr</td>
	<td><input type="checkbox" id="finger" name="finger" onclick="if(isIE())display_finger()"/><b style='display:none;' id='finger_note'>指纹录入须在IE浏览器下</b><input type="text" style="display:none;" id="tpdata" name="tpdata" value="$fingerinfo" size="28">
	</td>
</tr>



<SCRIPT language="javascript">
function isIE() 
{ //ie?
  if (!!window.ActiveXObject || "ActiveXObject" in window)
     return true;
  else
     return false;
}

function splitFingerData(s, defaultPrefix){
	if (defaultPrefix === undefined) defaultPrefix = '01';
	var lst = [];
	var idx = 2;
	var lenIdx = 4;
	var padding = 4;
	var cnt = parseInt(s.slice(0,2), 16);
	for (var i=0; i < cnt; i++){
		var len = parseInt(s.slice(idx+lenIdx , idx+lenIdx+2), 16);
		var fg = s.slice(idx, idx + lenIdx + padding + len*2);
		lst.push(defaultPrefix+fg);
		console.log(fg)
		idx = idx + lenIdx + padding + len*2;
	}
	return lst;	
}

    if(!isIE()){
		\$("#finger").attr("disabled","disabled")
	    \$("#finger_note").css("display","inline");	
	}
    function InitNetSsVerify() {
        token = FReg.token.value;
        iRt = UCtrl.InitInstance(token);
        FReg.initReturnValue.value = iRt;
        document.all.UCtrl.SetParameter(0);
        document.all.UCtrl.SetHexFlg(1);
    }
	function display_finger(){
		if (\$("#finger").attr("checked")){
			\$("#finger_img").css("display", "table-row");
		}
		else{\$("#finger_img").css("display", "none");}
	}
    function InitFingerInfo() { //重新设置已注册手指
        document.all.UCtrl.FingerInfo.value = "0001000100";
        document.all.UCtrl.SetOperateParam("0001000100");
        document.all.UCtrl.SetParameter(0);
        document.all.UCtrl.SetHexFlg(1);
    }

function unique(a) {  
	var res = [];  
	for (var i = 0, len = a.length; i < len; i++) {  
		var item = a[i];  
		for (var j = 0, jLen = res.length; j < jLen; j++) {  
			if (res[j] === item)  break;  
    		}
  
    		if (j === jLen) res.push(item);  
	}
	return res;  
}  

    function getfpdata(){
	tp = document.all.UCtrl.GetFingerPrintData();
	console.log(tp);
	var _tp = splitFingerData(tp);
	exist = \$("#tpdata").val();
	if (exist){
		\$.each(exist.split('&&'),function(i,v){ if(v) _tp.push(v)})
		_tp = unique(_tp);
	}
	// console.log(_tp)
	tp = _tp.join('&&');
	\$("#tpdata").val(tp);
    }
     function HasGotFeatureEvent(){
        getfpdata();
    } 
	window.onload = function(){
		if(isIE()){
			document.all.UCtrl.SetHexFlg(1);
		}
	}
</SCRIPT>
<tr class="env" id="finger_img" style="display:none"><td class="add-div-table">录入指纹</td>
<td>
<OBJECT ID="UCtrl" width="343" height="228"
CLASSID="CLSID:57FA9034-0DC3-4882-A932-DDDA228FEE05">
<param name="Token" value="12345678912345678912345678912345" />
<param name="CtrlType" value="Register" />
<param name="FingerInfo" value="$ini_value" />
</OBJECT>
<script for="UCtrl" event="GotFeatureEvent()" language="javascript">
	HasGotFeatureEvent();
</script>
</td></tr>





</table>
	<input type="hidden" name="ACTION" value="$action">
	<input type="hidden" name="line" value="$line">
    <input type="hidden" name="sure" value="y">
	<input type="hidden" name="lock" value="$par{'lock'}">
EOF
,_("Description")
,_("mailbox")
,_("please input a correct mail address")
,_("This field may be blank")
;
	
	&closeeditorbox($button, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
}

sub show_user()
{
	@user_info = read_users_file();
	
printf <<END
    <table class="ruleslist" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td class="boldbase" width="8%">%s</td>
            <td class="boldbase" width="10%">%s</td>
			<td class="boldbase" width="40%">%s</td>
            <td class="boldbase" width="10%">%s</td>
			<td class="boldbase" width="14%">%s</td>
			<td class="boldbase" width="15%">%s</td>
		</tr>
END
, _('Username')
, _('用户类型')
, _('Description')
, _('mailbox')
, _('删除指纹')
, _('Action')
;
	my $class;
	my $i = $j = 0;
	#print $is_editing;
	foreach my $user(@user_info){
		my @temp = split(",",$user);
		my $user_type;
		my $bgcolor = setbgcolor($is_editing,$line,$i);
		my $finger_file = $fingerdir.$temp[0];
		my $is_hidden = "hidden_class";
		if ($now_user eq "admin") {
			if($temp[4] eq "0" || $temp[0] eq "admin"){
				$is_hidden = "";
				$j++;
			}
			$user_type = "配置管理员";
		}
		if ($now_user eq "logerauth") {
			if($temp[4] eq "3"  || $temp[0] eq "logerauth"){
				$is_hidden = "";
				$j++;
			}
			$user_type = "日志审计员";
		}
		if ($now_user eq "safeauth") {
			if($temp[4] eq "1"  || $temp[0] eq "safeauth"){
				$is_hidden = "";
				$j++;
			}
			$user_type = "安全保密员";
		}
		if($j % 2!=0){
			$class = "class='odd_thin $is_hidden'";
		}else{
		    $class = "class='env_thin $is_hidden'";
		}
		printf <<EOF
		<tr $class >
		<td class='$bgcolor'>$temp[0]</td>
		<td class='$bgcolor'>$user_type</td>
		<td class='$bgcolor' title="$temp[2]">$temp[2]</td>
		<td class='$bgcolor' title="$temp[3]">$temp[3]</td>
		<td class='$bgcolor'>
EOF
;
		if (-e $finger_file) {
			foreach my $line (read_config_file($finger_file)) {
				my @tmp  = split(/,/,$line);
				my $which_finger;
				if ($tmp[1] < 6) {
					$which_finger = "R".$tmp[1];
				}
				else{
					my $num = $tmp[1]-5;
					$which_finger = "L".$num;
				}
                $which_finger =~s/RA/L5/; 
				printf <<EOF
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;" onsubmit="return confirm('确认删除该指位指纹信息？')">
					<input type="submit" value="$which_finger" />
					<INPUT TYPE="hidden" NAME="finger_num" VALUE="$tmp[1]">
					<INPUT TYPE="hidden" NAME="user" VALUE="$temp[0]">
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="delete_finger">
				</form>
EOF
;
			}
		}
		else{
			print "无";
		}
		printf <<EOF
		</td>
		<td class='$bgcolor' style="text-align:center">
		<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="display:inline-block;">
            <input class="imagebutton" type='image' NAME="submit" SRC="$edit_PNG" ALT="%s" />
            <INPUT TYPE="hidden" NAME="ACTION" VALUE="edit">
			<INPUT TYPE="hidden" NAME="USER" VALUE="$temp[0]">
			<INPUT TYPE="hidden" NAME="USER_TYPE" VALUE="$temp[4]">
            <INPUT TYPE="hidden" NAME="line" VALUE="$i">
			<INPUT TYPE="hidden" NAME="lock" VALUE="$temp[5]">
        </form>
EOF
;

		if($temp[0] ne $now_user){	
			print "<form METHOD='post' action='$ENV{'SCRIPT_NAME'}'' style='display:inline-block'>";
			if($temp[5]){
				 print '<input class="imagebutton" type="image" NAME="submit" SRC="/images/lock.png"  />';
			}

			else{
				 print '<input class="imagebutton" type="image" NAME="submit" SRC="/images/unlock.png"  />';
			} 

			printf <<EOF     
            <INPUT TYPE="hidden" NAME="ACTION" VALUE="lock">
			<INPUT TYPE="hidden" NAME="LOCK" VALUE="$temp[5]">
            <INPUT TYPE="hidden" NAME="line" VALUE="$i">
            </form>
EOF
;            

		}	
		if($temp[0] ne $now_user)
		{
printf <<EOF
		<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="display:inline-block" onsubmit="if(confirm('确认要删除此用户？')){return true;}return false;">
            <input class="imagebutton" type='image' NAME="submit" SRC="$delete_PNG" ALT="%s" />
            <INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
            <INPUT TYPE="hidden" NAME="line" VALUE="$i">
			<INPUT TYPE="hidden" NAME="ufile" VALUE="$temp[0]">
        </form>
EOF
;
		}
printf <<EOF
		</td>
		</tr>
EOF
;
		$i++;
	}
printf <<EOF
</table>
<table class="list-legend" cellpadding="0" cellspacing="0">
<tr>
<td CLASS="boldbase"><b>%s</b>
<IMG SRC="$EDIT_PNG" alt="%s" />
%s
<IMG SRC="$DELETE_PNG" ALT="%s" />
%s
<IMG SRC="/images/lock.png" ALT="%s" />
%s
<IMG SRC="/images/unlock.png" ALT="%s" />
%s
 </tr>
</table>
EOF
,
_('Legend'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
_('锁定'),
_('锁定'),
_('未锁定'),
_('未锁定')
;
}

###功能：防止用户手动修改浏览器url，使之跳转到此页面
sub check_user()
{
	my @cur_user=getCurUser();
	if($cur_user[0] ne "admin")
	{
		my $url = "\"https://".$ENV{'SERVER_ADDR'}.":10443/cgi-bin/main.cgi\"";
		print "<script>window.parent.parent.location.replace(".$url."); </script>";
	}
}

sub check_form(){
   printf <<EOF
<script>
var object = {
       'form_name':'USER',
       'option'   :{
                    'name':{
                               'type':'text',
                               'required':'1',
                               'check':'name|',
							   'ass_check':function(eve){
								  var name=eve._getCURElementsByName("name","input","USER")[0].value;
								  name = name.replace(/(^\\s*)|(\\s*\$)/g,"");
								  var action=eve._getCURElementsByName("ACTION","input","USER")[0].value;
								  var key=0;
								  var msg = "";

							  
								  \$.ajax({
									  type:'get',
									  url:'/cgi-bin/chinark_back_get.cgi',
									  data:"path=/var/efw/userinfo/userslist&name="+name,
									  async:false,
									  success:function(data){




										 if(data == 1){
										 	key = 1;
										 } 
									  }
								  });
								  





							   if(key && action == "add"){ msg=name+"用户名已存在，请更换！" }
									  return msg;
							   }

                             },
                    'psw':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
														 var psw =eve._getCURElementsByName("psw","input","USER")[0].value; 
														 var msg = "";
														 if (\!\/\^\[a\-zA\-Z0\-9\]\*\$\/.test(psw)) {
														 	msg = "密码不能有特殊字符";
														 }
														 else if(psw.length < parseInt($psdLength)){
															 msg = "密码长度最少应为" + $psdLength + "位！";

														 }else if (psw.length >50) {
															msg = "密码长度最多为50位！";
														 }

														 else if((/^\\d+\$/.test(psw)) || (!/\\d/.test(psw))){
															 msg="密码不能只有数字或者字母，必须包含数字及字母！";
														 }
														
														 return msg;
														
                                                     }

						},
                    're_psw':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
														 var psw =eve._getCURElementsByName("psw","input","USER")[0].value; 
														 var repsw =eve._getCURElementsByName("re_psw","input","USER")[0].value; 
														 var msg = "";
														 if(psw != repsw){
															 msg = "密码和确认密码不一致！";
														 }
														 return msg;
                                                     }
                             },
                    'mail':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|'

                             },
                    'discription':{
                               'type':'text',
                               'required':'0',
                               'check':'note|'
                             }


                 }
         }
var check = new ChinArk_forms();
check._main(object);
//var nameObj= check._getCURElementsByName("name","input","USER")[0];
//var actionVal=check._getCURElementsByName("ACTION","input","USER")[0].value;
//var fn_obj = function(){
	//\$.ajax({
			  //type:'get',
			  //url:'/cgi-bin/chinark_back_get.cgi',
			  //data:"path=/var/efw/userinfo/userslist&name="+nameObj.value,
			  //async:false,
			  //success:function(data){
				 //if((data == 1) && (actionVal == "add")){
				 	//check._tip(object.option['name'],'name',nameObj.value +"用户名已存在，请更换",object['form_name']);
				 	//return false;
				 //} 
			  //}
		  //});
//}
//check.addEvent(nameObj,"blur",fn_obj);
\$("#forPswMd5").on("submit", function(){

	//nameObj.blur(fn_obj);
	forPswMd5();
	});
	

</script>
EOF
;
}


my $extraheader = "<script type='text/javascript' src='/include/jquery.md5.js'></script>
					<script type='text/javascript' src='/include/jsencrypt.min.js'></script>
					<script type='text/javascript' src='/include/usermanagement.js'></script>";
&showhttpheaders();
&getcgihash(\%par);


&openpage(_('User management'), 1, $extraheader);
&save();
foreach my $line(@errormessages)
{
	$errormessage.=$line."<br />";
}

&openbigbox($errormessage,$warnmessage,$notemessage);
&show_add();
&show_user();
check_form();
&closepage();

