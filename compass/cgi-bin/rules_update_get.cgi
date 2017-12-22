#!/usr/bin/perl
# AUTHOR: 殷其雷 2013/4/18

require '/var/efw/header.pl';
use warnings;
use strict;

&validateUser();
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
my $updata_rule_log = "/var/log/updata_rule.log";
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
my $num = @parValue;
if($num > 1)
{
    #运行升级
	my $rule_version = '';
	open(VERSION,'</var/updata/updata_utm_rules/updata_rules/release');
	my @versionmsg = <VERSION>;
	$rule_version = $versionmsg[0];
	chomp($rule_version);
	my $cmd = "/usr/local/bin/updata_rules.py ";
    $cmd .="$rule_version";
	`sudo $cmd`;
	

    #返回升级信息
	open(MYFILE,"$updata_rule_log") or die "Cant open the log file!";
	my $line;
	my $success = 0;
	my $check = 0;
	while($line = <MYFILE>)
	{ 
	    if($line =~ /\.*updata rules successd.*$/){
		  $success = 1;
		}
		if($line = ~/\.*need not updata, goodbye.*$/){
		  $check = 1;
		}
	}
	close(MYFILE);
	if($success)
	{
	   `sudo /usr/local/bin/delete_updata.py`;
	   print "升级成功!";
	} else {
	   if($check)
       {
	      `sudo /usr/local/bin/delete_updata.py`;
		  print "已经最新!";
	   }
	   else {
	      `sudo /usr/local/bin/delete_updata.py`;
	      print "升级失败!";
	   }
	}
}
else{
    #先换名
=cut	my @new_name = split(/=/, $parValue[0]);
    my $new_name= uri_unescape(@new_name[1]);
    `mv /var/updata/updata_rules.bin /var/updata/$new_name`;
	#运行解密
	$new_name=~s/\./=/g;
	my @name_splited = split(/=/,$new_name);
	my @name_version = split(/_/,$name_splited[0]);
	my $index3 = scalar(@name_version);
	$index3--;
=cut
	
	`sudo /etc/update/decryption_rule.py`;
	
	#获取解密后包内信息并返回给页面
	my $rule_version = '';
	open(VERSION,'</var/updata/updata_utm_rules/updata_rules/release');
	my @versionmsg = <VERSION>;
	$rule_version = $versionmsg[0];
	chomp($rule_version);
	
	my $update_info= '';
	my $file;
	open(LOGFILE,"$updata_rule_log") or die "Cant open the log file!";
	my $line;
	my $decry_check = 0;
	my $tar_check = 0;
	while($line = <LOGFILE>) {
	     if($line =~/\.*decrption.*successd.*$/){
		    $decry_check = 1;
		 }
		 if($line =~/\.*tar.*successd.*$/){
		    $tar_check = 1;
		 }
	}
	close(LOGFILE);
	if($decry_check&&$tar_check){
	     $update_info .= "检测到新规则库，系统规则库即将更新到新版本：";
	     $update_info .= "$rule_version";
	}

	print $update_info;
}




























