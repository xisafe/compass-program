#!/usr/bin/perl

require '/var/efw/header.pl';

my $sslvpnuseruploading = "/tmp/sslvpnuseruploading";
my $sslvpnuseruploadstatistics = "/tmp/sslvpn_user_upload_statistics";

my $data = -1;

if(-e $sslvpnuseruploading){
	$data = "用户数据正在上传，请稍后刷新页面...";
	if(-e $sslvpnuseruploadstatistics){
		open(STATISTICS, "<$sslvpnuseruploadstatistics") or $data = "统计数据读取失败，请稍后刷新页面";
		my @s_data = <STATISTICS>;
		close(STATISTICS) or $data = "统计数据关闭失败，请稍后刷新页面";
		$data = $s_data[0];
		chomp($data);
	}
}

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
print $data;