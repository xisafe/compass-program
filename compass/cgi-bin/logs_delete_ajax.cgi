#!/usr/bin/perl
use CGI();
use URI::Escape;
use Digest::MD5; 
require '/var/efw/header.pl';
require 'logs_common.pl';

my $userfile="/var/efw/userinfo/userslist";
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
my @user_info = read_users_file();
$name = &get_cookie_user();
$ENV{'QUERY_STRING'} =~ /pass=(.*)&path=(.*)/;
my ($pass,$path) = ($1,$2);
# $path =~ s/\%2F/\//g;
# $path =~ s/\%3D/\=/g;
# $pass =~ s/\%2F/\//g;
$pass = URI::Escape::uri_unescape($pass);
$path = URI::Escape::uri_unescape($path);
# system("echo $name $pass $path > /var/efw/chensisi.debug");
my @PathForDetail = split('=',$path);

if ($PathForDetail[0] ne "clear") {
	$PathForDetail[1] =~s/_/\//g;
}
# my $md5 = Digest::MD5->new;
# $md5->add($pass);
# $pass = $md5->hexdigest;
$pass = &decryptFn($pass); #解密
# system("echo $pass > /var/efw/chensisi.debug");
my $msg;
foreach	my $user(@user_info){
	my @info = split(/,/,$user);
	if (($info[0] eq $name) &&( $info[1] eq $pass) && ($info[5] eq "0")) {
		$msg = "success";
		if ($PathForDetail[0] eq 'delete') {
			system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl /var/log/$PathForDetail[1]");
		}
		elsif($PathForDetail[0] eq 'all_logs') {
			`sudo /usr/local/bin/delete_log_in_time.py`;

		}
		else {
			system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl /var/log/$PathForDetail[1]");
			system("rm /var/log/'$PathForDetail[1]'-*.gz -f");
			# system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl /var/log/$PathForDetail[1]-*.gz");
		}
		# system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl $path");
		# my $log_message = "删除了日志文件$path";
		# if ($path eq "all_logs") {
		# 	$log_message = "清空了日志文件";
		# }
		&user_log($log_message);
	}
}
print "$msg";