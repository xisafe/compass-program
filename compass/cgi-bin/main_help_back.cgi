#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 主面板添加帮助信息 
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/23-11:04
#===============================================================================

require '/var/efw/header.pl';
use CGI();
use URI::Escape;
&validateUser();
#my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my $help_file = "/var/efw/help/setting";
&readhash($help_file,\%help_hash);
	
my $help_hash_disk = read_json("/home/httpd/help/main_start_help.json","main_start.cgi","系统-系统概况-硬件信息","-10","10","down");
my $help_hash_interface = read_json("/home/httpd/help/main_start_help.json","main_start.cgi","系统-系统概况-网络接口","-10","10","down");
my $help_hash_http = read_json("/home/httpd/help/main_start_help.json","main_start.cgi","系统-系统概况-服务状态-HTTP代理","-10","10","down");
my $help_hash_smtp = read_json("/home/httpd/help/main_start_help.json","main_start.cgi","系统-系统概况-服务状态-SMTP代理","-10","10","down");
my $help_hash_pop3 = read_json("/home/httpd/help/main_start_help.json","main_start.cgi","系统-系统概况-服务状态-POP3代理","-10","10","down");
my $help_hash_ids = read_json("/home/httpd/help/main_start_help.json","main_start.cgi","系统-系统概况-服务状态-入侵防御","-10","10","down");
my $help_hash_state = read_json("/home/httpd/help/main_start_help.json","main_start.cgi","系统-系统概况-服务状态-上行接口","-485","-30","up");

print $help_hash{"HELP_ENABLED"}."&&&&&&&&&&".$help_hash_disk."&&&&&&&&&&".$help_hash_interface."&&&&&&&&&&".$help_hash_http."&&&&&&&&&&".$help_hash_smtp."&&&&&&&&&&".$help_hash_pop3."&&&&&&&&&&".$help_hash_ids."&&&&&&&&&&".$help_hash_state;
