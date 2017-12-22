#!/usr/bin/perl
#DATE:2013-7-8
#author:殷其雷
use URI::Escape;
require '/var/efw/header.pl';   

#获取传来参数,默认只有一个参数.
my @parValue = split(/&/, $ENV{'QUERY_STRING'});

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
&validateUser();
my @par_line = split(/=/, $parValue[0]);
my $path = uri_unescape(@par_line[1]);
my %node_conf;
$path .= "/node-info";
my $returnvalue = "";
if(!-e $path)
{
   print "SSLVPN服务器信息获取失败！当前节点不存在！";
} else {
   readhash($path,\%node_conf);
   printf <<EOF
   <table class="ruleslist" style="width:100%">
    <tr>
	   <td class="boldbase">SSLVPN服务器名称</td>
	   <td class="boldbase">电子政务网SSLVPN服务器地址</td>
	   <td class="boldbase">Internet网SSLVPN服务器地址</td>
	   <td class="boldbase">CA服务器地址</td>
	</tr>
	<tr>
	   <td>$node_conf{'node_name'}</td>
	   <td>$node_conf{'e-government-ip'}</td>
	   <td>$node_conf{'internet-government-ip'}</td>
	   <td>$node_conf{'ca-ip'}</td>
	</tr>
  </table>
  <br />
  <br />
  <br />
  <input class='submitbutton net_button' type='submit' name='submit' value='关闭' onclick="hide()" />
EOF
;	  
}
1;