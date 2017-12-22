#!/usr/bin/perl

#	@Author 王琳
#	@History 2013.09.05 First release
#

use strict;

require '/var/efw/header.pl';

my $openvpnusers   = '/usr/bin/openvpn-sudo-user';
my $success = -1;
my %par;
getcgihash(\%par);
my $action = $par{'action'};
my $type = $par{'type'};

my $full_name = $par{'full_name'};
chomp($full_name);
my $description = $par{'description'};
my $related_resource = $par{'related_resource'};
$related_resource = '' if( $par{'related_resource'} eq 'undefined');
$related_resource =~ s/\|/,/g;
my $state = $par{'state'};
$state = 'on' if($par{'action'} eq 'enable');
$state = 'off' if($par{'action'} eq 'disable');

####返回的数据的头信息####
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
&validateUser();
&doaction();

sub doaction(){
	my $result = 0;
	
	if($type eq 'orgz'){
		if($action eq 'add'){
			$result = `sudo ResMng -orga "$full_name" "$description" "$state"`;
		}elsif($action eq 'edit'){
			$result = `sudo ResMng -orge "$full_name" "$description" "$state"`;
		}elsif($action eq 'enable'){
			$result = `sudo ResMng -orge "$full_name" "$description" "$state"`;
		}elsif($action eq 'disable'){
			$result = `sudo ResMng -orge "$full_name" "$description" "$state"`;
		}elsif($action eq 'del'){
			$result = `sudo ResMng -orgd "$full_name"`;
		}
		if($result =~ /The Orgnization has already exist/){
			$result = '组织结构"'.$full_name.'"已存在，请重新选择其所属上级或更换组织名称'
		}
	}elsif($type eq 'ugrp'){
		my $cmd = '';
		if($action eq 'add'){
			$result = `sudo ResMng -uga "$full_name" "$description" "$related_resource" "$state"`;
		}elsif($action eq 'edit'){
			$result = `sudo ResMng -uge "$full_name" "$description" "$related_resource" "$state"`;
		}elsif($action eq 'enable'){
			$result = `sudo ResMng -uge "$full_name" "$description" "$related_resource" "$state"`;	
		}elsif($action eq 'disable'){
			$result = `sudo ResMng -uge "$full_name" "$description" "$related_resource" "$state"`;
		}elsif($action eq 'del'){
			$result = `sudo ResMng -ugd "$full_name"`;
		}
		if($result =~ /This user group name has already exist/){
			$result = '用户组"'.$full_name.'"已存在，请重新选择其所属组织或更换用户组名称'
		}
	}
	#判断是否操作成功
	if($result eq '1'){
		$success = 1;
	}else{
		$success = $result;
	}
	#返回结果
	print $success;
}