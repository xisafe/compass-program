#!/usr/bin/perl

#############################################################################
#
#作者：周计
#时间：2013-11-20
#描述：处理使用execl文件导入的sslvpn用户，配合前台设置的uploadsetting设置
#
#############################################################################

use Spreadsheet::ParseExcel;
use Net::IPv4Addr qw (:all);
use Encode;
use POSIX;

require '/var/efw/header.pl';

my $whitelist_file = "/var/efw/openvpn/whitelist";
my $upload_error_file = "/var/efw/openvpn/error_upload_users";
my $passwd = '/usr/bin/openvpn-sudo-user';
my $max_user_path="/usr/local/bin/license/getMaxusers";
my $current_users_num   = '/usr/bin/openvpn-sudo-user longlist | wc -l';
my $static_ip_file = '/var/efw/openvpn/static_ipaddr';
my @error_messages;
my $sys_max_users=`$max_user_path`;
my $sys_current_users = `$current_users_num`;
my $left_users = $sys_max_users - $sys_current_users;
my $conffile = "/var/efw/openvpn/settings";
my $set_net;
my $set_net_mask = "";
my $all = "";
my $re_file = '/tmp/chachong_re';
my $chachong = '/usr/local/bin/openvpnuploadchachong.sh';
my $hexToDecimal = '/usr/local/bin/hexToDecimal';
my $filename = '/tmp/temp.xls';
my $uploadsetting = '/var/efw/openvpn/uploadsetting';
my $default_group = '所有用户/默认用户组';
my $coveruser = '';

my $total_upload_users = 0;
my $have_handled_users = 0;
my $statistics_file = '/tmp/sslvpn_user_upload_statistics';

sub read_uploadsetting()
{
	if ( -e $uploadsetting )
	{
		$default_group = `grep DEFAULTGROUP $uploadsetting | cut -d "=" -f2`;
		$coveruser = `grep COVERUSER $uploadsetting | cut -d "=" -f2`;
		
		chomp($coveruser);
		chomp($default_group);
		$coveruser = '' if ( $coveruser ne 'on');		
		$default_group = '所有用户/默认用户组' if ( $default_group eq '');	
	}
}

sub excel_phrase($){
    my $file = shift;
	my $book = Spreadsheet::ParseExcel::Workbook->Parse($file);
    my @sheets = @{ $book->{Worksheet} };
	my $sheet = $sheets[0];
	my ( $minRow, $maxRow ) = $sheet->row_range();
    my ( $minCol, $maxCol ) = $sheet->col_range();
	my @new_lines;
	my $count = 0;
	foreach my $row ( $minRow .. $maxRow )
	{
	  my $new_line="";
	  foreach my $col ( $minCol .. $maxCol )
	  {
		my $value = "";
	    my $cell = $sheet->get_cell( $row, $col );
		#注意！当单元格内容为空时，cell对象取不到！此时直接调用$cell->value程序会处问题。
		if(!$cell)
		{
			$value="";
		} else {
			$value = $cell->value;
		}
		$value = encode('utf8',$value); 
		$new_line .= $value;
		if($col < $maxCol)
		{
			$new_line .="#";
		}
	  }
	  #去掉表格头及空行
	  if($row ne $minRow && $new_line ne '')
	  {
		push(@new_lines,$new_line);
		$total_upload_users =  $total_upload_users + 1;
      }
	}
    &filter_upload(\@new_lines);
}

#是子网，返回1；不是，返回0
sub isSubNet($$)
{
	my $ip = shift;
    my $cidr = shift;
	
	#print "$ip/$cidr  ";
	return 1 if ($cidr eq '32');
	#print " -- going on";
	
	my @ips = split(/\./, $ip);
	my $addr_1 = int($ips[0]);
	$addr_1 = $addr_1 * 16 * 16 * 16 * 16 * 16 * 16;
	my $addr_2 = int($ips[1]);
	$addr_2 = $addr_2 * 16 * 16 * 16 * 16; 
	my $addr_3 = int($ips[2]);
	$addr_3 = $addr_3 * 16 * 16;
	my $addr_4 = int($ips[3]);
	my $addr = $addr_1 + $addr_2 + $addr_3 + $addr_4 ;
	
	my $mask = 0xFFFFFFFF >> $cidr;
	
	my $result = $addr & $mask;

	return 1 if ( $result == 0 );
	return 0;
}

sub checkmyIPs($$) {
    my $ip = shift;
    my $maxcidr = shift;
    my @ips = split(/[\r\n,]/, $ip);
    my @ok = ();
    my @nok = ();

    foreach my $net (@ips) {
		next if ($net =~ /^\s*$/);
		my $ok = 0;
		my $checknet = $net;
		#$checknet .= '/32' if ($checknet !~ /\//);
		if ($checknet !~ /\//)
		{
			push(@nok, $net);
			next;
		}
		eval {
			my ($ip, $cidr) = ipv4_parse($checknet);
			if (($cidr > 0 and $cidr < $maxcidr)||$cidr == 32) {
				#判断子网与掩码是否合适
				if ( &isSubNet($ip, $cidr) )
				{
					push(@ok, "$ip/$cidr");
					$ok = 1;
				}
			}
		};
		if (! $ok) {
			push(@nok, $net);
		}
    }
    return (join(",", @ok), join(",", @nok));
}

sub update_statistics{
	my $need_hours = 0;
	my $need_minutes = 0;
	my $need_seconds = 0;
	
	my $need_seconds = $total_upload_users - $have_handled_users;
	if ( $need_seconds > 60 )
	{
		$need_minutes = int($need_seconds/60);
		$need_seconds = $$need_seconds % 60;
	}
	if ( $need_minutes > 60 )
	{
		$need_hours = int($need_minutes/60);
		$need_minutes = $$need_minutes % 60;
	}
	
	my $statistics_info = "现在正在处理第$have_handled_users个用户，上传用户数总数为$total_upload_users。大约还需";
	$statistics_info .= "$need_hours小时" if ( $need_hours > 0 );
	$statistics_info .= "$need_minutes分" if ( $need_minutes > 0 );
	$statistics_info .= "$need_seconds秒，";
	$statistics_info .= "请耐心等待！";
	
	`echo $statistics_info > $statistics_file`;
}

sub filter_upload(){
    my ($new_lines) = @_;
	my $count = 0;
	my $exist = 0;
	#每行一个用户信息，属性依次为：[0]用户名、[1]密码、[2]用户证书序列号、[3]备注、[4]所属用户组、[5]是否加入白名单、[6]静态地址、[7]本地子网、[8]DNS服务器、[9]加入域、[10]是否使用默认网管、[11]远程网络、[12]是否启用
	foreach my $one_line (@$new_lines)
	{
		#my $temp_line = $one_line;
		#$temp_line =~ s/\n/,/g;
		#`echo "-----&".$temp_line."&----\n" >> $upload_error_file`;
		
		#更新统计信息
		$have_handled_users = $have_handled_users + 1;
		&update_statistics();
		
	    my @split = split(/#/,$one_line);
	    if(&check_count($count))
		{
		   &write_error_log($split[0],"已达最大用户数！");
		   last;
		}
		
		#去掉每个属性值末尾的换行符
		chomp($split[0]); $split[0] = '' if ($split[0] =~ /^\s*$/);
		chomp($split[1]); $split[1] = '' if ($split[1] =~ /^\s*$/);
		chomp($split[2]); $split[2] = '' if ($split[2] =~ /^\s*$/);
		chomp($split[3]); $split[3] = '' if ($split[3] =~ /^\s*$/);
		chomp($split[4]); $split[4] = '' if ($split[4] =~ /^\s*$/);
		chomp($split[5]); $split[5] = '' if ($split[5] =~ /^\s*$/);
		chomp($split[6]); $split[6] = '' if ($split[6] =~ /^\s*$/);
		chomp($split[7]); $split[7] = '' if ($split[7] =~ /^\s*$/);
		chomp($split[8]); $split[8] = '' if ($split[8] =~ /^\s*$/);
		chomp($split[9]); $split[9] = '' if ($split[9] =~ /^\s*$/);
		chomp($split[10]);$split[10] = '' if ($split[10] =~ /^\s*$/);
		chomp($split[11]);$split[11] = '' if ($split[11] =~ /^\s*$/);
		chomp($split[12]);$split[12] = '' if ($split[12] =~ /^\s*$/);
		
		#检测用户名是否有空格
	    if ($split[0] =~ /^$/) {
		   #&write_error_log($split[0],"用户名不能为空！");
		   next;
        }
		
		my $all_error_messages = '';
		my $is_error = 0;
		
		#检测用户名是否有非法字符
	    if ($split[0] !~ /^[A-Za-z0-9\.\-_@]+$/) {
		   #&write_error_log($split[0],"用户名含非法字符！");		   
		   #next;
		   $all_error_messages .=  "用户名含非法字符！";
		   $is_error = 1;
        }
		
		#检查用户名长度是否正确
	    if (length($split[0]) < 4 || length($split[0]) > 20) {
		   #&write_error_log($split[0],"用户名长度不正确，长度应该在4~20字符！");
		   #next;
		   $all_error_messages .=  "用户名长度不正确，长度应该在4~20字符！";
		   $is_error = 1;
        }
		
		#—_—注：若是前台设置了用户名重复时，覆盖以前的值，这里还需添加代码处理
		#检查是否和已有用户名重名
		my $user_existed =  &check_exist($split[0]);
	    if ($coveruser ne 'on' && $user_existed) {
		   #&write_error_log($split[0],"该用户已经存在！");
		   #next;
		   $all_error_messages .=  "该用户已经存在！";
		   $is_error = 1;
		}
		
		#检查密码长度是否规范
	    if(length($split[1]) < 6 || length($split[1]) > 16) {
	       #&write_error_log($split[0],"密码长度不正确！");
		   #next;
		   $all_error_messages .=  "密码长度不正确！";
		   $is_error = 1;
	    }
		
		#检查密码是否包含非法字符
		if ($split[1] !~ /^[A-Za-z0-9]+$/) {
		   #&write_error_log($split[0],"密码包含非法字符！");
		   #next;
		   $all_error_messages .=  "密码包含非法字符！";
		   $is_error = 1;
        }
		
	    #序列号格式错误
	    if($split[2] ne '')
	    {
		   $exist = 0;
	       my @certs = split(/:/,$split[2]);
		   foreach my $cert (@certs)
		   {
		       #chomp($cert);
		       if($cert !~ /^[\dA-Fa-f]{2}$/)
			   {
			      #&write_error_log($split[0],"序列号格式错误！");
			      $exist = 1;
				  last;
			   }
		   }
		   if($exist)
		   {
			#next;
			$all_error_messages .=  "序列号格式错误！";
		    $is_error = 1;
		   }	      
	    }	    
		
		#检查备注是否包含\n、\t特殊字符
		$split[3] =~ s/,/，/g;
		if($split[3] ne '' && $split[3] =~ /[\n\t]/)
		{
			#&write_error_log($split[0],"备注内容不能换行!");
			#next;
			$all_error_messages .=  "备注内容不能换行!";
		    $is_error = 1;
		}
		#备注长度是否小于等于20
	    if(length($split[3]) > 20*3)
	    {
	       #&write_error_log($split[0],"备注长度不能大于20！");
	   	   #next;
		   $all_error_messages .=  "备注长度不能大于20！";
		   $is_error = 1;
	    }
		
		#检查是否有所属用户组，如果有所属用户组，则格式为：所有用户/xxxx[/xxx]
		#注xxx：这个匹配格式还有待修改
		if($split[4] ne '')
		{
			$exist = 0;
			my @ugs = split(/\n/,$split[4]);
		    foreach my $ug (@ugs)
		    {
			   next if ($ug =~ /^\s*$/);
			   chomp($ug);
		       if($ug ne '' && $ug !~ /^所有用户\/.*/ )
			   {
			      $exist = 1;
				  last;
			   }
		    }
			if ($exist)
			{
				#&write_error_log($split[0],"所属用户组内容有误！"); 
				#next;
				$all_error_messages .=  "所属用户组内容有误！";
				$is_error = 1;
			}
		}
		
		#检查”是否加入白名单“
		#if($split[5] ne '' && $split[5] !~ /^[是否]{1}$/)
		if($split[5] ne '' && $split[5] ne '是' && $split[5] ne '否')
		{
			#&write_error_log($split[0],"是否加入白名单只能为是或否！"); 
			#next;
			$all_error_messages .=  "是否加入白名单只能为是或否！";
			$is_error = 1;
		}
		
		#检查静态地址是否符合规范
	    if($split[6] ne '' && $split[6] !~ /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}$/ )
	    {
	       #&write_error_log($split[0],"静态IP地址格式不正确！");
	   	   #next;
		   $all_error_messages .=  "静态IP地址格式不正确！";
		   $is_error = 1;
	    }
		
		#静态地址是否是已设虚拟网络内的IP
		#应该放宽这条个检测条件，因为很可能更改虚拟地址池的范围
		#if($split[6] ne '' && check_in($split[6]))
		#{
		#   &write_error_log($split[0],"IP不在已设的虚拟网段内！");
	   	#   next;
		#}	
		
		#如果用户已经存在且以前的静态地址不为空，则删除以前的静态地址
		my $old_staticip = '';
		$old_staticip = get_user_staticip($split[0]) if ($user_existed);
		del_static($old_staticip) if ($user_existed && $old_staticip ne '');
		
		#检查静态地址是否重复
		if($split[6] ne '' && check_ip_exist($split[6]))
	    {
		    #&write_error_log($split[0],"与已添加用户的静态地址重复！");
		    #next;
			$all_error_messages .=  "与已添加用户的静态地址重复！";
		    $is_error = 1;
		}

		#检查本地子网$split[7]
		my ($local_ok, $local_nok) = &checkmyIPs($split[7], 32);
		if ($local_nok ne '') {
			#&write_error_log($split[0],"本地子网不符合要求！");
		    #next;
			$all_error_messages .=  "本地子网不符合要求！";
		    $is_error = 1;
		}
		$split[7] = $local_ok;
		
		#检查DNS服务器$split[8]
		if($split[8] ne '')
		{
			$exist = 0;
			my @dnss = split(/\n/,$split[8]);
		    foreach my $dns (@dnss)
		    {
			   next if ($dns =~ /^\s*$/);
		       chomp($dns);
		       if($dns ne '' && $dns !~ /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}$/)
			   {
			      $exist = 1;
				  last;
			   }
		    }
			if ($exist)
			{
				#&write_error_log($split[0],"DNS服务器地址填写错误！"); 
				#next;
				$all_error_messages .=  "DNS服务器地址填写错误！";
				$is_error = 1;
			}
		}
		
		#检查加入域$split[9]
		
		#检查是否使用默认网关$split[10]
		#if($split[10] ne '' && $split[10] !~ /^[是否]{1}$/)
		if($split[10] ne '' && $split[10] ne '是' && $split[10] ne '否')
		{
			#&write_error_log($split[0],"是否使用默认网关只能为是或否！"); 
			#next;
			$all_error_messages .=  "是否使用默认网关只能为是或否！";
			$is_error = 1;
		}
		
		#检查远程网络$split[11]
		my ($remote_ok, $remote_nok) = checkmyIPs($split[11], 32);
		if ($remote_nok ne '') {
			#&write_error_log($split[0],"远程网络不符合要求！");
		    #next;
			$all_error_messages .=  "远程网络不符合要求！";
			$is_error = 1;
		}
		$split[11] = $remote_ok;
		
		#坚持是否启用$split[12]
		#if($split[12] ne '' && $split[12] !~ /^[是否]{1}$/)
		if($split[12] ne '' && $split[12] ne '是' && $split[12] ne '否')
		{
			#&write_error_log($split[0],"是否启用只能为是或否！"); 
			#next;
			$all_error_messages .=  "是否启用只能为是或否！";
			$is_error = 1;
		}
		
		if ( $is_error )
		{
			&write_error_log($split[0], $all_error_messages); 
			next;
		}
		
		#通过全部检测，加入此用户
		my $username = $split[0];
		
		my $password = $split[1];
		
		my $user_cert_value = $split[2];
		my $user_cert = '';
		my $user_cert_value_number = '';
		if ( $user_cert_value eq '')
		{
			$user_cert = 'none';
		}else{
			#2013-7-21 序列号直接不用分隔
			$user_cert_value =~ s/://g;
			$user_cert_value = uc($user_cert_value);
			#
			$user_cert = 'input';
			$user_cert_value_number = `$hexToDecimal $user_cert_value`;
			chomp($user_cert_value_number);
		}
		
		my $comments = $split[3];
		
		my $group_info='';
		if ($split[4] eq '')
		{
			#注：如果前台配置了，没有所有用户组的导入特定用户组，这里为特定用户组
			$group_info = $default_group;
		}
		else
		{
			my @ugs = split(/\n/,$split[4]);
			my $index=0;
		    foreach my $ug (@ugs)
		    {
			   next if ($ug =~ /^\s*$/);
		       chomp($ug);
		       if($ug ne '')
			   {
				  if ($index != 0)
				  {
					$group_info .= ":";
				  }
			      $group_info .= $ug;
				  $index = $index+1;
			   }			  
		    }			
			if ($group_info eq '')
			{
				$group_info = $default_group;
			}
		}
		
		my $whitelist = 'on';
		$whitelist = '' if ( $split[5] eq '否' ) ;
		
		my $static_ip = $split[6];	
		
		my $explicitroutes = $split[7];
		$explicitroutes =  'None' if ($explicitroutes eq '');
		
		my $custom_dns = 'None';
		my $push_custom_dns = 'off';
		if ($split[8] ne '')
		{
			$custom_dns = '';
			my $index = 0;
			my @dnss = split(/\n/,$split[8]);
		    foreach my $dns (@dnss)
		    {
			   next if ($dns =~ /^\s*$/);
		       chomp($dns);
		       if($dns ne '')
			   {
				  last if ($index >= 2);
				  $custom_dns .= ',' if ($index != 0);					
			      $custom_dns .= $dns;
				  $index = $index + 1;
				  $push_custom_dns = 'on'; 
			   }
		    }
			if ($index == 1)
			{
				my $temp = $custom_dns;
				$custom_dns .= ",";
				$custom_dns .= $temp;
			}
			if ($custom_dns eq '')
			{
				$custom_dns = 'None';
				$push_custom_dns = 'off';
			}
		}
		
		my $push_custom_domain = 'off';
		my $custom_domain = 'None';
		if ($split[9] ne '')
		{
			$push_custom_domain = 'on';
			$custom_domain = $split[9];
		}		
		
		my $setred = 'on';
		$setred = 'off' if ( $split[10] eq '否');
		
		my $remotenets = $split[11];
		$remotenets = 'None' if ($remotenets eq '');
		
		my $user_enabled = 'on';
		$user_enabled = '' if ( $split[12] eq '否');
	   
	    #？？注：如果用户存在时，是否给予覆盖用户处理
		
	    #执行添加命令
		#使用ResMng添加用户到用户组织结构和whitelist中
		my $result = '';
		if ( $coveruser eq 'on' && $user_existed)
		{
			$result = `sudo ResMng -ue "$username" "$user_cert"  "$user_cert_value" "$user_cert_value_number" "$whitelist" "$comments" "$user_enabled" "$group_info"`;
		}else {
			$result = `sudo ResMng -ua "$username" "$user_cert"  "$user_cert_value" "$user_cert_value_number" "$whitelist" "$comments" "$user_enabled" "$group_info"`;
		}
		#my $xxx = "sudo ResMng -ua \"$username\" \"$user_cert\"  \"$user_cert_value\" \"$user_cert_value_number\" \"$whitelist\" \"$comments\" \"$user_enabled\" \"$group_info\"";
		#`echo  $xxx >> $upload_error_file`;
		
		#在新添加用户时，whitlist中有用户，但是passwd中没有用户，这是一个bug
		#此时添加用户应该成功，重新使用ResMng -ue来修改用户信息
		if( $result =~ /^The user has already exist/ ){			
			$result = `sudo ResMng -ue "$username" "$user_cert"  "$user_cert_value" "$user_cert_value_number" "$whitelist" "$comments" "$user_enabled" "$group_info"`;
		}
		
		chomp($result);
		if ($result eq '1')
		{
			#如果ResMng添加成功，则把今天地址添加到static_ipaddr文件中
			#2013-7-19
			add_static($static_ip);
			#
		}else{
			if ( $result =~ /^This user group does not exist: / || $result =~ /^Unable to add to UserGroup/)
			{
				@result_split = split(/:/, $result);
				$result = "用户组不存在：$result_split[1] !";
			}
			&write_error_log($split[0],$result); 
			next;
		}
		
		#先断开该用户的连接
		system("$passwd kill \"$username\"");
	    `sudo fcmd "$passwd kill $username"`;

=pod		
		#直接向/var/efw/openvpn/passwd文件中写内容
		{
		my $passwd_line = "$username";
		
		$passwdcrypt = '/root/passwdcrypt.py';
		my $crypt_passwd = `$passwdcrypt $password`;
		chomp($crypt_passwd);
		$passwd_line .= ":$crypt_passwd";
		
		$passwd_line .= ":enabled" if($user_enabled eq 'on');
		$passwd_line .= ":disabled" if($user_enabled ne 'on');
		
		$passwd_line .= ":unsetred" if( $setred eq 'off');
		$passwd_line .= ":setred" if( $setred eq 'on');
		
		$passwd_line .= ":unsetorange";
		$passwd_line .= ":unsetblue";
		
		$passwd_line .= ":" if ($remotenets eq 'None');
		$passwd_line .= ":$remotenets" if ($remotenets ne 'None');
		
		$passwd_line .= ":off";
		
		$passwd_line .= ":" if ($explicitroutes eq 'None');
		$passwd_line .= ":$explicitroutes" if ($explicitroutes ne 'None');
		
		$passwd_line .= ":$static_ip";
		
		$passwd_line .= ":" if ($custom_dns eq 'None');
		$passwd_line .= ":$custom_dns" if ($custom_dns ne 'None');
		
		$passwd_line .= ":" if ($custom_domain eq 'None');
		$passwd_line .= ":$custom_domain" if ($custom_domain ne 'None');
		
		$passwd_line .= ":$push_custom_dns";
		$passwd_line .= ":$push_custom_domain";	

		`sed -i "/^$username:.*\$/d"  /var/efw/openvpn/passwd`;
		`echo "$passwd_line" >> /var/efw/openvpn/passwd`;
		}		
=cut			

		#使用openvpn-sudo-user添加用户		
		my $openvpn_cmd = "$passwd set \"$username\" --password \"$password\"";
		$openvpn_cmd .= " --dns=$custom_dns";
		$openvpn_cmd .= " --domain=$custom_domain";
		$openvpn_cmd .= " --static-ips=$static_ip";
		$openvpn_cmd .= " --dont-push-routes off";#这项上传信息中没有
		$openvpn_cmd .= " --explicit-routes $explicitroutes";
		$openvpn_cmd .= " --networks $remotenets";
		$openvpn_cmd .= " --route-blue off"; #这项上传信息中没有
		$openvpn_cmd .= " --route-orange off"; #这项上传信息中没有
		$openvpn_cmd .= " --route-red $setred";
		$openvpn_cmd .= " --push-domain=$push_custom_domain";
		$openvpn_cmd .= " --push-dns=$push_custom_dns";
		
		system("$openvpn_cmd --rewrite-users");
	    `sudo fcmd "$openvpn_cmd --rewrite-users"`;
		#`echo  $openvpn_cmd >> $upload_error_file`;

		if($user_enabled eq 'on')
	    {
	       &enable_user($username);
		   #`echo  "enable_user:"$username >> $upload_error_file`;
	    } else {
	       &disable_user($username);
		   #`echo  "disable_user:"$username >> $upload_error_file`;
	    }	
		$count++;
	}
	write_error_all();
	`rm -r $filename`;
}

sub disable_user ($) {
    my $user = shift;
    `$passwd set \"$user\" --toggle='disable' --rewrite-users`;
	`sudo fcmd "$passwd set \"$user\" --toggle"`;	
    #`sudo fmodify "/var/efw/openvpn/passwd"`;
}

sub enable_user ($) {
    my $user = shift;
    `$passwd set \"$user\" --toggle='enable' --rewrite-users`;
	`sudo fcmd "$passwd set \"$user\" --toggle"`;	
	#`sudo fmodify "/var/efw/openvpn/passwd"`;
}

sub check_max_users(){
    my $max_users=`$max_user_path`;
	my $current_users = `$current_users_num`;
	if($current_users >= $max_users )
	{
	   return 1;
	} else {
	   return 0;
	}
}

sub check_count($){
    my $count = shift;
	if($count >= $left_users)
	{
	   return 1;
	} else {
	   return 0;
	}
}

sub check_exist($){
	my $value = shift;
	if(-e $re_file)
	{
	   `rm $re_file`;
	}
	`touch $re_file`;
	`sudo $chachong $value >>$re_file `;
	my $result = `cat $re_file`;
	`rm $re_file`;
	if($result=~/success/)
	{
	   return 1;
	} else {
	   return 0;
	}
}

sub check_ip_exist($){
	my $ip = shift;
	chomp($ip);
	if(!-e $static_ip_file)
	{
	   return 0;
	}
	return 1 if (`sed -n /^$ip\$/p $static_ip_file` ne '');
	return 0;
}

sub check_in($){
    #本地子网和掩码值不存在时直接允许检测通过
    if($set_net_mask eq '' || $all eq '')
	{
	   return 0;
	}
    my $get_ip = shift;
    my @new_set_nums;
	@new_set_nums = split(/\./,$get_ip);
	$new_set_nums[0] = unpack("B*",pack("N",$new_set_nums[0]));
	$new_set_nums[1] = unpack("B*",pack("N",$new_set_nums[1]));
	$new_set_nums[2] = unpack("B*",pack("N",$new_set_nums[2]));
	$new_set_nums[3] = unpack("B*",pack("N",$new_set_nums[3]));
    $new_set_nums[0] = substr($new_set_nums[0],-8);
    $new_set_nums[1] = substr($new_set_nums[1],-8);
	$new_set_nums[2] = substr($new_set_nums[2],-8);
	$new_set_nums[3] = substr($new_set_nums[3],-8);
    my $all2 = "";
	$all2 = $new_set_nums[0];
	$all2 .= $new_set_nums[1];
	$all2 .= $new_set_nums[2];
    $all2 .= $new_set_nums[3];
    $all2 = substr($all2,0,$set_net_mask);
	if($all ne $all2)
    {
	   return 1;
    } else {
	   return 0;
	}
}

sub write_error_log($$){
    my $error_username = shift;
	my $error_detail = shift;
	my $new_line = $error_username;
	$new_line .= ",";
	$new_line .= $error_detail;
	push(@error_messages,$new_line);
}

sub write_error_all(){
   if(scalar(@error_messages) > 0)
   {
      foreach my $error (@error_messages)
	  {
	     `echo >>$upload_error_file $error`;
	  }
   }
}

sub add_static($){
    my $ip = shift;
	if($ip eq '' || $ip eq 'None')
	{
	   return;
	}
	if(!-e $static_ip_file)
	{
	   `touch $static_ip_file`;
	}
	`echo >>$static_ip_file $ip `;
}

sub del_static($){
    my $ip = shift;
	chomp($ip);
	if($ip eq '' || $ip eq 'None')
	{
	   return;
	}
	if(!-e $static_ip_file)
	{
	   `touch $static_ip_file`;
	   return;
	}
	`sed -i /^$ip\$/d $static_ip_file`;
}

sub get_user_staticip($)
{
	my $user_names = shift;
	return '' if ($user_names eq '');
	
	my $static_ip = '';
	$static_ip = `$passwd getuser $user_names| cut -d : -f8`;
	return $static_ip;
}


if(-e $conffile)
{
   open(FILE,$conffile);
   my @lines = <FILE>;
   close(FILE);
   foreach my $one (@lines){
      if($one =~/PURPLE_NET/)
      {
	     my @split = split(/=/,$one);
	   	 $set_net = $split[1];
		 last;
      }
   }
   #系统刚初始化时PURPLE_NET可能不存在
   if($set_net ne ''){
   my @set_split = split(/\//,$set_net);
   my $set_net_num = $set_split[0];
   $set_net_mask = $set_split[1];
   my @set_net_nums = split(/\./,$set_net_num);
   $set_net_nums[0] = unpack("B*",pack("N",$set_net_nums[0]));
   $set_net_nums[1] = unpack("B*",pack("N",$set_net_nums[1]));
   $set_net_nums[2] = unpack("B*",pack("N",$set_net_nums[2]));
   $set_net_nums[3] = unpack("B*",pack("N",$set_net_nums[3]));
   $set_net_nums[0] = substr($set_net_nums[0],-8);
   $set_net_nums[1] = substr($set_net_nums[1],-8);
   $set_net_nums[2] = substr($set_net_nums[2],-8);
   $set_net_nums[3] = substr($set_net_nums[3],-8);
   $all = $set_net_nums[0];
   $all .= $set_net_nums[1];
   $all .= $set_net_nums[2];
   $all .= $set_net_nums[3];
   $all = substr($all,0,$set_net_mask);
   }
}

#删除错误日志文件
`rm $upload_error_file`;

#从上传用户配置文件中获取配置信息
read_uploadsetting();

#执行上传处理
excel_phrase($filename);

#上传文件处理完成，删除文件/tmp/sslvpnuseruploading，告诉前台上传完成
`rm /tmp/sslvpnuseruploading` ;

#删除统计文件
`rm $statistics_file`;
1;