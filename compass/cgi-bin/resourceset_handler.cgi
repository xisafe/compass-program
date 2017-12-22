#!/usr/bin/perl

#
#	@Author 王琳
#	@History 2013.09.22 First release
#

use strict;

require '/var/efw/header.pl';
&validateUser();
my $success = -1;

my %par;
getcgihash(\%par);
my $action = $par{'action'};
my $type = $par{'type'};

my $resg_name = $par{'resg_name'};
my $resg_description = $par{'resg_description'};

my $resource_name = $par{'resource_name'};
my $resource_description= $par{'resource_description'};
my $access_method= $par{'access_method'};
my $ip_addr= $par{'ip_addr'};
my $protocol= $par{'protocol'};
my $port= $par{'port'};
my $url_addr= $par{'url_addr'};
my $resource_grep= $par{'resource_grep'};
if($par{'resource_grep'} eq ''){
	$resource_grep = "默认资源组";
}


my $state = $par{'state'};
$state = 'on' if($par{'action'} eq 'enable');
$state = 'off' if($par{'action'} eq 'disable');


####返回的数据的头信息####
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

&doaction();

sub doaction(){
	my $result = 0;
	my $error = &check_value();
	if($error){
		print $error;
		return;
	}
	if($type eq 'resg'){
		if($action eq 'add'){
			$result = `sudo ResMng -resga "$resg_name" "$resg_description" "$state"`;
		}elsif($action eq 'edit'){
			$result = `sudo ResMng -resge "$resg_name" "$resg_description" "$state"`;
		}elsif($action eq 'enable'){
			$result = `sudo ResMng -resge "$resg_name" "$resg_description" "$state"`;
		}elsif($action eq 'disable'){
			$result = `sudo ResMng -resge "$resg_name" "$resg_description" "$state"`;
		}elsif($action eq 'del'){
			$result = `sudo ResMng -resgd "$resg_name"`;
		}
		if($result =~ /This name has already exist/){
			$result = '资源组名称"'.$resg_name.'"已存在，请重新填写';
		}
	}elsif($type eq 'res'){
		if($action eq 'add'){
			$result = `sudo ResMng -resa "$resource_name" "$resource_description" "$access_method" "$ip_addr" "$protocol" "$port" "$url_addr" "$state" "$resource_grep"`;
		}elsif($action eq 'edit'){
			$result = `sudo ResMng -rese "$resource_name" "$resource_description" "$access_method" "$ip_addr" "$protocol" "$port" "$url_addr" "$state" "$resource_grep"`;
		}elsif($action eq 'enable'){
			$result = `sudo ResMng -rese "$resource_name" "$resource_description" "$access_method" "$ip_addr" "$protocol" "$port" "$url_addr" "$state" "$resource_grep"`;
		}elsif($action eq 'disable'){
			$result = `sudo ResMng -rese "$resource_name" "$resource_description" "$access_method" "$ip_addr" "$protocol" "$port" "$url_addr" "$state" "$resource_grep"`;
		}elsif($action eq 'del'){
			$result = `sudo ResMng -resd "$resource_name"`;		
		}
		
		`/usr/local/bin/setvpnfw` if($result eq '1');
		if($result =~ /This resource name has already exist/){
			$result = '资源名称"'.$resource_name.'"已存在，请重新填写';
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

sub check_value(){
}