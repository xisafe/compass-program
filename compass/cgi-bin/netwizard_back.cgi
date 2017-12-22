#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:网络配置添加帮助信息 
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
	
my $help_hash_tmpl1 = read_json("/home/httpd/help/netwizard_help.json","netwizard.cgi","系统-网络设置-网络向导-选择红色接口的类型","7","30","down");
my $help_hash_tmpl2 = read_json("/home/httpd/help/netwizard_help.json","netwizard.cgi","系统-网络设置-网络向导-选择需要启用的内网区域","7","10","down");
my $help_hash_tmpl3 = read_json("/home/httpd/help/netwizard_help.json","netwizard.cgi","系统-网络设置-网络向导-网络参数设置-绿色-IP地址","-10","0","down");
my $help_hash_tmpl4 = read_json("/home/httpd/help/netwizard_help.json","netwizard.cgi","系统-网络设置-网络向导-网络参数设置-绿色-附加IP地址","-10","0","down");
my $help_hash_tmpl5 = read_json("/home/httpd/help/netwizard_help.json","netwizard.cgi","系统-网络设置-网络向导-网络参数设置-绿色-接口","-10","0","down");


print $help_hash{"HELP_ENABLED"}."&&&&&&&&&&".$help_hash_tmpl1."&&&&&&&&&&".$help_hash_tmpl2."&&&&&&&&&&".$help_hash_tmpl3."&&&&&&&&&&".$help_hash_tmpl4."&&&&&&&&&&".$help_hash_tmpl5;
