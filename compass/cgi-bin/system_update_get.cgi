#!/usr/bin/perl
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2012/03/06-11:04
# MODIFY：殷其雷 2013/4/18

require '/var/efw/header.pl';
#use warnings;
#use strict;
&validateUser();
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
my $updata_sys_log = "/var/log/updata_sys.log";
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
my $num = @parValue;
if($num > 1)
{
    #运行升级
	my $version = '';
	open(VERSION,'</var/updata/updata_utm_sys/updata_sys/release');
	my @versionmsg = <VERSION>;
	close(VERSION);#新增 by wl 2014.4.17
	$version = $versionmsg[0];
	chomp($version);
	my $cmd = "/usr/local/bin/updata_sys.py ";
	$cmd .="$version";
	`sudo $cmd`;
	#返回升级信息
	my $line;
	my $success = 0;
	my $check = 0;
	my @log_lines = read_conf_file($updata_sys_log);
	foreach $line (@log_lines) {
	    if($line =~ /\.*updata system successd.*$/){
		  $success = 1;
		}
		if($line =~ /\.*need not updata, goodbye.*$/){
		  $check = 1;
		}
	}
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
	my @new_name = split(/=/, $parValue[0]);
    my $new_name= uri_unescape(@new_name[1]);
    `mv /var/updata/updata_sys.bin /var/updata/$new_name;`;
	#运行解密

	$new_name=~s/\./=/g;
	my @name_splited = split(/=/,$new_name);
	my @name_version = split(/_/,$name_splited[0]);
	my $index3 = scalar(@name_version);
	$index3--;
    `sudo /etc/update/decryption_sys.py`; 
	#根据日志查看解密解压是否成功并返回给前台页面显示
	my $version = '';
	open(VERSION,'</var/updata/updata_utm_sys/updata_sys/release');
	my @versionmsg = <VERSION>;
	$version = $versionmsg[0];
	chomp($version);
	my $update_info= '';
	my $file;
	open(LOGFILE,"$updata_sys_log") or die "Cant open the log file!";
	my $line;
	my $decry_check = 0;
	my $tar_check = 0;
	while($line = <LOGFILE>) {
	     if($line =~ /\.*decrption.*successd.*$/){
		    $decry_check = 1;
		 }

		 if($line =~ /\.*tar.*successd.*$/){
		    $tar_check = 1;
		 }
	}
	close(LOGFILE);
	if($decry_check&&$tar_check){
	     $update_info .= "检测到新系统版本，系统即将升级到新版本";
	     $update_info .= "$version";
	}
	print $update_info;
}




























