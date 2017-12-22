#!/usr/bin/perl

#	@Author 王琳
#	@History 2013.09.05 First release
#

require '/var/efw/header.pl';

my $openvpnusers   = '/usr/bin/openvpn-sudo-user';
my $hextodecimal   = '/usr/local/bin/hexToDecimal';
my $openvpn_dir = "${swroot}/openvpn";
my $whitelist_file = "${swroot}/openvpn/whitelist";
my $static_ip_file = '/var/efw/openvpn/static_ipaddr';
my $success = -1;
&validateUser();
my %par;
getcgihash(\%par);
my $cgi= new CGI; 
my $action = $par{'action'};
my $username = $par{'username'};
my $password = $par{'password'};
my $password2 = $par{'password'};

my $static_ip = &to_string($par{'static_ip'});
$static_ip = 'None' if ($static_ip eq '');

my $explicitroutes = &to_string($par{'explicitroutes'});
$explicitroutes = 'None' if ($explicitroutes eq '');

my $push_custom_dns = 'on';
$push_custom_dns = 'off' if ($par{'push_custom_dns'} eq 'false');
my $firstdns = $par{'firstdns'};
my $seconddns = $par{'seconddns'};
my $custom_dns = "$firstdns,$seconddns";
$custom_dns = 'None' if ($par{'push_custom_dns'} eq 'false');

my $push_custom_domain = 'on';
$push_custom_domain = 'off' if ($par{'push_custom_domain'} eq 'false');
my $custom_domain = $par{'custom_domain'};
$custom_domain = 'None' if ($par{'push_custom_domain'} eq 'false');

my $setred = 'on';
my $setblue = 'on';
my $setorange = 'on';
$setred = 'off' if($par{'setred'} ne 'true');
$setblue = 'off' if ($par{'setblue'} ne 'true');
$setorange = 'off' if ($par{'setorange'} ne 'true');
my $dontpushroutes = 'on';
$dontpushroutes = 'off' if ($par{'dontpushroutes'} ne 'true');

my $remotenets = &to_string($par{'remotenets'});
$remotenets = 'None' if ($remotenets eq '');

my $user_cert = $par{'user_cert'};
my $user_cert_value = $par{'user_cert_value'};
$user_cert_value =~s/://g;
$user_cert_value =~s/ //g;
$user_cert_value = uc($user_cert_value);
my $user_cert_value_number = `$hextodecimal $user_cert_value`;
chomp($user_cert_value_number);
if($par{'user_cert_value'} eq ''){
	$user_cert_value = '';
	$user_cert_value_number = '';
}
my $comments = $par{'comments'};
$comments =~s/,/，/g;
$comments = '' if( $par{'comments'} eq '' );
my $whitelist = 'on';
$whitelist = '' if( $par{'whitelist'} eq 'false' );
my $user_enabled = 'on';
$user_enabled = '' if( $par{'user_enabled'} eq 'false' );

my $enable_user = 'enable';
$enable_user = 'disable' if( $par{'user_enabled'} ne 'true' );

my $group_info = $par{'group_info'};
chomp($group_info);
$group_info = '所有用户/默认用户组' if( $group_info eq '' );

####返回的数据的头信息####
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
&make_file();
&doaction();

sub make_file(){
	if(!-e $openvpn_dir){
		`mkdir $openvpn_dir`;
	}
	
	if(!-e $whitelist_file){
		`touch $whitelist_file`;
	}
	
	if(!-e $static_ip_file){
		`touch $static_ip_file`;
	}
}

sub doaction(){
	my $error = 0;
	my $error = &check_user($username, $action);
	if($error){
		print $error;
		return;
	}
	if($action eq 'add' || $action eq 'edit'){
		#添加
		$error = &check_values();
		if($error){
			print $error;
			return;
		}
		$error = &addEditUser();
	}elsif($action eq 'disable'){
		#禁用
		$error = &enable_or_disable_user($username, $action, '');
	}elsif($action eq 'enable'){
		#启用
		$error = &enable_or_disable_user($username, $action, 'on');
	}elsif($action eq 'remove'){
		#移除白名单
		$error = &remove_shift_whitelist($username, '');
	}elsif($action eq 'shiftin'){
		#移入白名单
		$error = &remove_shift_whitelist($username, 'on');
	}elsif($action eq 'del'){
		#删除
		$error = &delete_user($username);
	}
	if($error eq '0'){
		$success = 1;
		print $success;
	}else{
		print $error;
	}
}

sub check_user($$){
	my $username = shift;
	my $action = shift;
	my $error = 0;
	if($action eq 'add'){
		#检查是否达到用户数上限
		my $max_users_num=`/usr/local/bin/license/getMaxusers`;
		my $current_users_num = `/usr/bin/openvpn-sudo-user longlist | wc -l`;
		if($current_users_num >= $max_users_num )
		{
		   $error = "当前已达到系统支持最大用户数，添加失败~";
		   return $error;
		}
		#检查是否重名
		my @tmp_users = split(/\n/, `$openvpnusers longlist`);
		foreach my $one (@tmp_users)
		{
		    my @split = split(/:/,$one);
			if($username eq $split[0])
			{
			   $error = "用户名已存在，请重新填写用户名~";
			   break;
		    }
		}
	}else{
		#检查用户是否存在
		#检查在原系统是中否存在
		my @tmp_users1 = split(/\n/, `$openvpnusers longlist`);
		my $exist1 = 0;
		foreach my $one (@tmp_users1)
		{
		    my @split1 = split(/:/,$one);
			if($username eq $split2[0])
			{
			   $exist1++;
			   break;
		    }
		}
		#检查在黑白名单中是否存在
		my @tmp_users2 = read_conf_file($whitelist_file);
		my $exist2 = 0;
		foreach my $one (@tmp_users2)
		{
		    my @split2 = split(/,/,$one);
			if($username eq $split2[0])
			{
			   $exist2++;
			   break;
		    }
		}
		if(!$exist1 && !$exist2){
			#$error = "用户不存在，不能操作，请重试~"
			$error = "$exist1 $exist2~"
		}
	}
	return $error;
}

sub check_values(){
	my $error = &cracklib($password, $password2);
	if($error){
		return $error;
	}
	
	
	return 0;
}	
sub to_string($) {
    my $string = shift;
    my $ret = '';
    foreach my $item (split(/[\n\r]/, $string)) {
	next if ($item =~ /^$/);
	$ret .= ','.$item;
    }
    $ret =~ s/^,//;
    return $ret;
}

sub addEditUser(){
	my $result = 0;
	my $error = 1;
		
	#保存静态IP
	#删除原来的ip
	my $old_ip = &getUserStacticIP($username);
	&replace_static_ip($old_ip,$static_ip);
	
	my $cmd = "$openvpnusers set \"$username\" --password \"$password\"";
	$cmd .= " --dns=$custom_dns";
	$cmd .= " --domain=$custom_domain";
	$cmd .= " --static-ips=$static_ip";
	#新构建的页面中不存在此项
	$cmd .= " --dont-push-routes $dontpushroutes";
	
	$cmd .= " --explicit-routes $explicitroutes";
	$cmd .= " --networks $remotenets";
	#此两项不存在
	$cmd .= " --route-blue $setblue";
	$cmd .= " --route-orange $setorange";
	
	$cmd .= " --route-red $setred";
	$cmd .= " --push-domain=$push_custom_domain";
	$cmd .= " --push-dns=$push_custom_dns";

	# kill the user in order to enforce the configuration change.
	`$openvpnusers kill "$username"`;
	`sudo fcmd "$openvpnusers kill $username"`;

	`$cmd --rewrite-users`;
	`sudo fcmd "$cmd --rewrite-users"`;
	
	&enable_or_disable($username, $enable_user);
	
	#关于whitelist_file中信息的解读--2013.08.08，by wl
	#字段1：用户名											字段2：用户证书序列号输入方式none input upload
	#字段3：十六进制序列号									字段4：十进制的序列号
	#字段5：是否在白名单中，on代表在，没有内容表示不在		字段6：备注信息
	#字段7：启用on，没有内容表示禁用						字段8：用户分组信息
	if($action eq 'add'){
		$result = `sudo ResMng -ua "$username" "$user_cert" "$user_cert_value" "$user_cert_value_number" "$whitelist" "$comments" "$user_enabled" "$group_info"`;
	}elsif($action eq 'edit'){
		$result = `sudo ResMng -ue "$username" "$user_cert" "$user_cert_value" "$user_cert_value_number" "$whitelist" "$comments" "$user_enabled" "$group_info"`;
	}
	chomp($result);
	if($result eq '1'){
		$error = 0;
	}else{
		#如果有后一步没添加成功，要删除前一步添加的用户
		if($action eq 'add'){
			`$openvpnusers del "$username"`;
			`sudo fcmd "$openvpnusers del $username"`;
		}
		$error = $result;
	}
	
	return $error;
}

sub cracklib($$) {
    my $password = shift;
    my $password1 = shift;

    if ($password =~ /[\s'"\\`]+/) {
		return "密码输入含有非法字符,不能包含空格、单引号、双引号、反斜杠(\\)和(`)";
    }
    if ($password ne $password1) {
		return "两次密码不一致，请修改~";
    }
    if (length($password) < 6 || length($password) > 32) {
		return "密码长度不正确，只能输入6至32个字符，请修改~";
    }
    return 0;

}

sub enable_or_disable ($$) {
    my $user = shift;
	my $enable_user = shift;
    `$openvpnusers set "$user" --toggle=$enable_user --rewrite-users`;
	`sudo fcmd "$passwd set \"$user\" --toggle"`;	
}

sub enable_or_disable_user ($$$) {
    my $user = shift;
	my $enableuser = shift;
	my $userenabled = shift;
	my $myresult;
	my $myerror;
	&enable_or_disable($user, $enableuser);
	my $data = `sudo ResMng -uq -c "$user"`;
	chomp($data);
	my @temp = split(/,/,$data);
	$myresult = `sudo ResMng -ue "$temp[0]" "$temp[1]" "$temp[2]" "$temp[3]" "$temp[4]" "$temp[5]" "$userenabled" "$temp[7]"`;
	chomp($myresult);
	if($myresult eq '1'){
		$myerror = 0;
	}else{
		$myerror = $myresult;
	}
	return $myerror;
}
sub remove_shift_whitelist ($$) {
    my $user = shift;
	my $remove_shift_whitelist = shift;
	my $myresult;
	my $myerror;
	my $data = `sudo ResMng -uq -c "$user"`;
	chomp($data);
	my @temp = split(/,/,$data);
	$myresult = `sudo ResMng -ue "$temp[0]" "$temp[1]" "$temp[2]" "$temp[3]"  "$remove_shift_whitelist" "$temp[5]" "$temp[6]" "$temp[7]"`;
	chomp($myresult);
	if($myresult eq '1'){
		$myerror = 0;
	}else{
		$myerror = $myresult;
	}
	return $myerror;
}
sub delete_user($){
	my $user = shift;
	my $myresult;
	my $myerror;
	#删除静态IP，先于删除用户，否者会出错
	&replace_static_ip(&getUserStacticIP($user),'');
	#删除用户信息
	$myresult = `sudo ResMng -ud $user`;
	`$openvpnusers del "$user"`;
	`sudo fcmd "$openvpnusers del $user"`;
	chomp($myresult);
	if($myresult eq '1'){
		$myerror = 0;
	}else{
		$myerror = $myresult;
	}
	return $myerror;
}

sub getUserStacticIP($){
	my $user = shift;
	my @tmp_users = split(/\n/, `$openvpnusers longlist`);
	my $old_ip = '';
	foreach my $one (@tmp_users)
	{
		my @split = split(/:/,$one);
		if($user eq $split[0])
		{
			$old_ip = $split[8];
			break;
		}
	}
	return $old_ip;
}

sub replace_static_ip($$){
	my $old_ip = shift;
	my $new_ip = shift;	
	my @ips = read_conf_file($static_ip_file);
	my @new_ips;
	foreach my $one (@ips)
	{
	   if($one ne $old_ip)
	   {
			push(@new_ips,$one);
	   }
	}
	if($new_ip eq '' || $new_ip eq 'None')
	{
		save_config_file(\@new_ips,$static_ip_file);
	}else{
		push(@new_ips,$new_ip);
		save_config_file(\@new_ips,$static_ip_file);
	}	
}

sub get_user_cert_value(){
	
}