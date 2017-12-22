#!/usr/bin/perl

#	@Author 王琳
#	@History 2013.09.05 First release
#

use strict;
use JSON::XS;

require '/var/efw/header.pl';
my $openvpnusers   = '/usr/bin/openvpn-sudo-user';
my %par;
getcgihash(\%par);
my $limit = $par{'limit'};
my $pageSize = $limit;
my $page  = $par{'page'};
my $search = $par{'search'};
chomp($search);
my $full_name = $par{'full_name'};
chomp($full_name);
my $type = $par{'type'};
my $start = ($page - 1)>0 ?  ($page - 1) * $limit : 0;
&validateUser();
##找出数据
my $users;
`echo "$full_name" >/tmp/openvpnuserdata`;
if($search eq ''){
	if($full_name eq ''){
		#如果没有发送组织名，就返回所有用户
		$users  = `sudo ResMng -orgq -u -c 所有用户`;
	}else{
		if($type eq 'org'){
			$users  = `sudo ResMng -orgq -u -c "$full_name"`;
		}elsif($type eq 'ug'){
			$users  = `sudo ResMng -ugq -u -c "$full_name"`;
		}
	}
}else{
	if($full_name eq ''){
		#如果没有发送组织名，就返回所有用户
		$users  = `sudo ResMng -orgq -u -f "$search" 所有用户`;
	}else{
		if($type eq 'org'){
			$users  = `sudo ResMng -orgq -u -f "$search" "$full_name"`;
		}elsif($type eq 'ug'){
			$users  = `sudo ResMng -ugq -u -f "$search" "$full_name"`;
		}
	}
}

##进行去重和排序处理
my @userArray = split(/\n/, $users);
my %hash;
####去重####
@userArray = grep { ++$hash{$_} < 2 } @userArray;
####排序####
@userArray = sort @userArray;
###################

my $total = 0;
my $userContent = '';
my @userContentArray;
#取出另一张表中,所有用户的配置数据
my @userList = `$openvpnusers  longlist`;
foreach my $array_user (@userArray){
##将要的用户所包含的数据项
	my $username = "";

	my $static_ip = "";

	my $explicitroutes = "";

	my $push_custom_dns = "false";
	my $firstdns = "";
	my $seconddns = "";
	my $custom_dns = "";

	my $push_custom_domain = "false";
	my $custom_domain = "";

	my $setred = "false";
	my $dontpushroutes = "false";

	my $remotenets = "";

	my $user_cert = "input";
	my $user_cert_value  = "";
	my $comments = "";
	my $whitelist = "false";
	my $user_enabled = "false";

	my $group_info = "";
	
	
	##取出一页大小
	if($total >= $start && $total < $start + $pageSize){
		chomp($array_user);
		my @array_user_split = split(/,/, $array_user);
		#在list中找到对应用户
		my $user_config = '';
		foreach my $list_user (@userList){
			my @list_user_split = split(/:/, $list_user);
			if($list_user_split[0] eq $array_user_split[0]){
				$user_config = $list_user;
				last;
			}
		}
		my @split = split(/:/, $user_config);
		##取出用户数据进行处理
		$username = $array_user_split[0];
		
		$user_enabled = 'false' if($split[1] ne 'enabled');
		
		$setred = 'true' if ($split[2] eq 'setred');
		
		$remotenets = $split[5];
		#$remotenets =~ s/,/<br\/>/g;
		
		$dontpushroutes = "false" if ($split[6] eq 'on');
		
		$explicitroutes = $split[7];
		#$explicitroutes =~ s/,/<br\/>/g;
		chomp($explicitroutes);
		
		$static_ip = $split[8];;
		$static_ip =~ s/,/\n/g;
		chomp($static_ip);
		
		$custom_dns = $split[9];
		if ($custom_dns ne '') {
			($firstdns,$seconddns) = split(/,/,$custom_dns);
			$push_custom_dns= 'true';
		}

		$custom_domain = $split[10];
		$push_custom_domain = 'true' if($custom_domain ne '');
		
		$push_custom_dns= 'true' if ($split[11] =~ /on/);
		
		$push_custom_domain= 'true' if ($split[12] =~ /on/);
		
		#读取whitelist中用户的旧数据,相对于启用/禁用，移除/移入白名单动作，用旧数据操作，以免出错
		#关于whitelist_file中信息的解读--2013.08.08，by wl
		#字段1：用户名											字段2：用户证书序列号输入方式none input upload
		#字段3：十六进制序列号									字段4：十进制的序列号
		#字段5：是否在白名单中，on代表在，没有内容表示不在		字段6：备注信息
		#字段7：启用on，没有内容表示禁用						字段8：用户分组信息
		$user_cert = 'none' if($array_user_split[1] eq 'none');
		$user_cert_value = &add_colon($array_user_split[2]);
		$whitelist = 'true' if($array_user_split[4] =~ /on/ );
		$comments = $array_user_split[5];
		$user_enabled = "true" if($array_user_split[6] =~ /on/);
		$group_info = $array_user_split[7];
		
		my %userdata;
		%userdata->{'username'} = $username;
		%userdata->{'user_enabled'} = $user_enabled;
		%userdata->{'setred'} = $setred;
		%userdata->{'remotenets'} = $remotenets;
		%userdata->{'dontpushroutes'} = $dontpushroutes;
		%userdata->{'explicitroutes'} = $explicitroutes;
		%userdata->{'static_ip'} = $static_ip;
		%userdata->{'push_custom_dns'} = $push_custom_dns;
		%userdata->{'firstdns'} = $firstdns;
		%userdata->{'seconddns'} = $seconddns;
		%userdata->{'push_custom_domain'} = $push_custom_domain;
		%userdata->{'custom_domain'} = $custom_domain;
		%userdata->{'user_cert'} = $user_cert;
		%userdata->{'user_cert_value'} = $user_cert_value;
		%userdata->{'whitelist'} = $whitelist;
		%userdata->{'comments'} = $comments;
		%userdata->{'group_info'} = $group_info;
		push(@userContentArray, \%userdata);
	}
	$total++;
}
my %userRetData;
%userRetData->{'users'} = \@userContentArray;
%userRetData->{'total'} = $total;
my $json = new JSON::XS;
$users = $json->encode(\%userRetData);

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
print $users;

sub add_colon($){
	#在读出的证书序列号中增加冒号
	my $line = shift;
	my $return_line;
	if(length($line)<=2)
	{
	   return $line;
	} else {
	   $return_line = substr($line,0,2);
	   $line = substr($line,2,length($line)-2);
	   do{
	      $return_line .= ":";
	      $return_line .= substr($line,0,2);
		  $line = substr($line,2,length($line)-2);
	   } while (length($line)>=2)
	}
	return $return_line;
}