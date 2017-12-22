#!/usr/bin/perl

#	@Author 王琳
#	@History 2013.09.05 First release
#

use strict;
use JSON::XS;
my $json = new JSON::XS;

require '/var/efw/header.pl';
my $root_res_group = "所有资源";
my %par;
getcgihash(\%par);
my $limit = $par{'limit'};
my $pageSize = $limit;
my $page  = $par{'page'};
my $search = $par{'search'};
my $full_name = $par{'full_name'};
my $type = $par{'type'};
my $start = ($page - 1)>0 ?  ($page - 1) * $limit : 0;


print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my $resources;
##找出数据
if($search eq ''){
	if($full_name eq ''){
		#如果没有发送资源组名，就返回所有资源
		$resources  = `sudo ResMng -resgq -r -c "$root_res_group"`;
	}else{
		$resources  = `sudo ResMng -resgq -r -c "$full_name"`;
		
	}
}else{
	if($full_name eq ''){
		#如果没有发送资源组名，就返回所有资源
		$resources  = `sudo ResMng -resgq -r -f "$search" "$root_res_group"`;
	}else{
		$resources  = `sudo ResMng -resgq -r -f "$search" $full_name`;
	}
}
my @resourcesArray = split(/\n/, $resources);
my $total = 0;
my @resourcesContent;

if($limit ne 'nolimit'){
	foreach my $array_resources (@resourcesArray){
		##取出一页大小
		if($total >= $start && $total < $start + $pageSize){
			my %resourceitem = getResourceContent($array_resources);
			push(@resourcesContent,\%resourceitem);
		}
		$total++;
	}
}else{
	foreach my $array_resources (@resourcesArray){	
		#全部传回去
		my %resourceitem = getResourceContent($array_resources);
		push(@resourcesContent,\%resourceitem);
		$total++;
	}
}
my %resourcesRetData;
%resourcesRetData->{'resources'} = \@resourcesContent;
%resourcesRetData->{'total'} = $total;
$resources = $json->encode(\%resourcesRetData);
print $resources;

sub getResourceContent($){
	my $resource_item  = shift;
	my $json_obj = $json->decode($resource_item);
	my %resourceitem;
	%resourceitem->{'name'} = $json_obj->{'name'};
	%resourceitem->{'desc'} = $json_obj->{'desc'};
	%resourceitem->{'am'} = $json_obj->{'am'};
	%resourceitem->{'ip'} = $json_obj->{'ip'};
	%resourceitem->{'protocol'} = $json_obj->{'protocol'};
	%resourceitem->{'port'} = $json_obj->{'port'};
	%resourceitem->{'url'} = $json_obj->{'url'};
	%resourceitem->{'state'} = $json_obj->{'state'};
	%resourceitem->{'res_group'} = $json_obj->{'res_group'};
	%resourceitem->{'user_groups'} = $json_obj->{'user_groups'};
	return %resourceitem;
}
