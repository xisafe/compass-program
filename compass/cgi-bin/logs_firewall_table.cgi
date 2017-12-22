#!/usr/bin/perl
#

#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
#        |         Endian GmbH/Srl                                                     |
#        |         Bergweg 41 Via Monte                                                |
#        |         39057 Eppan/Appiano                                                 |
#        |         ITALIEN/ITALIA                                                      |
#        |         info@endian.it                                                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        | http://www.fsf.org/                                                         |
#        +-----------------------------------------------------------------------------+
#

require '/var/efw/header.pl';
require 'logs_common.pl';
use POSIX();
use CGI ':standard';
use CGI::Carp qw (fatalsToBrowser);

my %cgiparams;
my %logsettings;
my %filterchange;
my %chaindisplay;
$chaindisplay{'INCOMINGFW'}="流入访问控制";
$chaindisplay{'OUTGOINGFW'}="流出访问控制";
$chaindisplay{'ZONEFW'}="区域访问控制";
$chaindisplay{'ZONEFW6'}="IPV6访问控制";
$chaindisplay{'VPNFW'}="VPN访问控制";
$chaindisplay{'INPUT'}="系统访问";
$chaindisplay{'INPUTFW'}="系统访问";
$chaindisplay{'ALLOW'}="进入入侵检测";
$chaindisplay{'DROP'}="丢弃";
$chaindisplay{'ACCEPT'}="允许";
$chaindisplay{'REJECT'}="拒绝";
$chaindisplay{'BADTCP'}="错误TCP连接";
$chaindisplay{'PORTFWACCESS'}="DNAT";
$chaindisplay{'FORWARD'}="转发";
$chaindisplay{'PROXIES'}="代理";
$chaindisplay{'HTTP-PROXY'}="HTTP代理";
$chaindisplay{'FTP-PROXY'}="FTP代理";
$chaindisplay{'POLICYROUTING'}="策略路由";
$chaindisplay{'不带SYN标志'}="非SYN连接";

my $logfile="/var/log/firewall";
my @files = sort(glob("${logfile}-*.gz"));
my $name = "firewall";

&getcgihash(\%cgiparams);
my %iface;
for (my $i = 0; $i < 20; $i++) {
	my $eth = 'eth'.$i;
	$iface{$eth} = 0 ;
}
$iface{'br0'} = $iface{'br1'} = 0;
my $today = getDate(time);
my 	$date = $today;
if ($cgiparams{'DATE'} =~ /[\d\/]+/) {
    $date = $cgiparams{'DATE'};
}
my $years; 
my @t = split(/-/,$date);
$years=$t[0];
my $day_length = length($t[2]);
#changed by elvis on 6.13 for month-value
my $month_length = length($t[1]);
if ($month_length == 1) {
	$t[1] = "0".$t[1];
	$date = "$t[0]-$t[1]-$t[2]";
}
#end
if ($day_length == 1) {
	$t[2] = "0".$t[2];
	$date = "$t[0]-$t[1]-$t[2]";
}

my $filetotal=scalar(@files);
my $filetotal1 = 2;
my ($firstdatestring) = ($files[0] =~ /\-(\d+).gz$/);
if ($firstdatestring eq '') {
    $firstdatestring = dateToFilestring($today);
}

if ((dateToFilestring($date) < $firstdatestring) || (dateToFilestring($date) > dateToFilestring($today))) {
    	
	$errormessage = _('Please select date between "%s" and "%s" ,now goto logs file for today!',$firstdatestring,dateToFilestring($today));
	$date = $today;
}

my $filestr = $logfile;
if ($date ne $today) {
    $filestr="${logfile}-".dateToFilestring($date).".gz";
}

my $lines = 0;
my @log = ();
my $test=0;
###新增日志导出功能 by elvis 2012-8-28
&showhttpheaders();

$extraheaders = <<EOF
<script type="text/javascript" src="/include/jquery.js"></script>
<script type="text/javascript" src="/include/waiting.js"></script>
<script type="text/javascript" src="/include/ESONCalendar.js"></script>
<link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />

EOF
;

$language = $settings{'LANGUAGE'};
if (-e "/home/httpd/html/include/jquery-calendar-$language.js") {
    $extraheaders .= <<EOF
<script type="text/javascript" src="/include/jquery-calendar-$language.js"></script>
EOF
;
}
my $firstdatearr = dateToArray($firstdatestring);
my $lastdatearr = dateToArray($today);

&openpage(_('Firewall log'), 1, $extraheaders);

&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&openbox('100%', 'left', _('统计报表'));
begin();
print "<div class='paging-div-header'>";
oldernewer();
print "</div>";

&display_table($filestr);
ends();
####end
&closebox();

&closebigbox();

&closepage();

sub getDate($) {
    my $now = shift;
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($now);
    $year += 1900;
    $mon++;
    return sprintf("%04d-%02d-%02d", $year, $mon, $mday);
}

sub dateToFilestring($) {
    my $date = shift;
    $date =~ s/\-//g;
    return $date;
}

sub dateToArray($) {
    my $date = shift;
    $date =~ s/\-//g;
    my @datearr = ($date =~ /^(\d{4})(\d{2})(\d{2})$/);
    return \@datearr;
}

sub stringToDate($) {
    my $date = shift;
    my $arr = dateToArray($date);
    return $lala = mktime(0, 0, 0, @$arr[2], @$arr[1] - 1, @$arr[0] - 1900);
}
sub read_config_file($) {
    my @lines;
	my $file=shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}
sub begin(){
	printf <<EOF
	<script>
	  RestartService("正在生成统计报表，请等待.....");
	</script>
EOF
;
}
sub ends(){
	printf <<EOF
	<script>
	  endmsg("报表已生成，请查阅或导出");
	</script>
EOF
;
}
sub display_table($){
	my $filestr = shift;
	my @message = read_config_file($filestr);
	if ($filestr =~ /\.gz$/) {
		@message = `gzip -dc $filestr`;
	}
	my $total_num = @message;
	my $tcp = $udp = $other = 0;
	my $accept = $reject = $drop = $allow = $proxy = 0;
	my %src_ip=();
	my %dst_ip=();
	foreach my $line(@message){
		####全局统计数据获取
		###判断协议分类统计
		if ($line =~/PROTO=TCP/) {
			$tcp ++;
		}
		elsif($line =~/PROTO=UDP/){
			$udp ++;
		}
		else{
			$other ++;
		}
		###协议分类结束
		###计算动作分类统计
		if ($line =~/:ALLOW/) {
			$allow ++;
		}
		elsif($line =~/DROP/){
			$drop ++;
		}
		elsif($line =~/ACCEPT/){
			$accept ++;
		}		
		elsif($line =~/REJECT/){
			$reject ++;
		}
		else{
			$proxy ++;
		}
		###动作分类结束
		####全局统计数据获取结束


		####按源统计数据获取
		if($line =~ /SRC=(.*)\sDST/){
			my $ip = $1;
			if ($src_ip{$ip} < 1) {
				$src_ip{$ip} = 1;
			}
			else{
				$src_ip{$ip} ++;
			}
		}
		
		####按源统计数据获取结束
		####按目的统计数据获取
		if($line =~ /DST=(\d+\.\d+\.\d+\.\d+)/){
			my $ip = $1;
			if ($dst_ip{$ip} < 1) {
				$dst_ip{$ip} = 1;
			}
			else{
				$dst_ip{$ip} ++;
			}
		}
		
		####按目的统计数据获取结束
		####按接口统计数据获取
		foreach	my $key(keys %iface){
			if ($line =~ /$key/) {
				$iface{$key} ++;
			}
		}
		
		####按接口统计数据获取结束
	}
	printf <<EOF
	<script  type="text/javascript" charset="utf-8" >
		function export_to_excel()   { 
			var oExcel = new ActiveXObject("Excel.Application");   //创建Excel对象   
			var oWork = oExcel.Workbooks.Add();                      //新建一个Excel工作簿  
			oWork.Sheets.Add();
			oWork.Worksheets("Sheet1").Activate();
			var oSheet = oWork.ActiveSheet;                      //指定要写入内容的工作表为活动工作表  	
			var table_summarize = document.all.summarize;              //指定要写入的数据源的id
			var table_src_ip = document.all.src_ip; 
			var table_dst_ip = document.all.dst_ip; 			
			var table_iface = document.all.iface;
			var summarizeRow = table_summarize.rows.length;               //取数据源行数  
			var summarizeCell = table_summarize.rows(1).cells.length;           //取数据源列数 
			
		  	//开始全局表格
			for (i=0;i<summarizeRow;i++){//在Excel中写行  
				if(i == 0){
					oSheet.Cells(i+1,1).value = table_summarize.rows(i).cells(0).innerText;					
					oSheet.Cells(i+1,1).Interior.ColorIndex = 17 ;
					oSheet.Cells(i+1,1).Font.ColorIndex = 6;
					oSheet.Cells(i+1,1).Font.Bold = true;
					oSheet.Cells(i+1,1).HorizontalAlignment = 3;
					oSheet.Range(oSheet.Cells(i+1, 1), oSheet.Cells(i+1, 10)).MergeCells = true;
				}
				else{
					for (j=0;j<summarizeCell;j++){//在Excel中写列  
					//定义格式  
					oSheet.Cells(2,j+1).Font.Bold = true;//加粗  
					oSheet.Cells(i+1,j+1).Font.Size = 10;//字体大小
					if(table_summarize.rows(i).cells(j).innerHTML.toLowerCase().indexOf('<img')!=-1){//如果其HTML代码包括<img  
						oSheet.Cells(i+1,j+1).Select();//选中Excel中的单元格  
						oSheet.Pictures.Insert(table_summarize.rows(i).cells(j).getElementsByTagName('img')[0].src);//插入图片  
					}  
					else{  
						oSheet.Cells(i+1,j+1).value = table_summarize.rows(i).cells(j).innerText;//向单元格写入值 
					}  
				  }
				}
			}   
			oExcel.Visible = true;   
			oExcel.Columns.AutoFit;
			oExcel.UserControl = true;	
			//开始源IP表格
			
			oWork.Worksheets("Sheet2").Activate();
			oSheet = oWork.ActiveSheet;
			var src_ipRow = table_src_ip.rows.length;               //取数据源行数  
			var src_ipCell = table_src_ip.rows(2).cells.length;
			src_ipCell ++;
			for (i=0;i<src_ipRow;i++){//在Excel中写行  
				if(i == 0){
					oSheet.Cells(i+1,1).value = table_src_ip.rows(i).cells(0).innerText;					
					oSheet.Cells(i+1,1).Interior.ColorIndex = 17 ;
					oSheet.Cells(i+1,1).Font.ColorIndex = 6;
					oSheet.Cells(i+1,1).Font.Bold = true;
					oSheet.Cells(i+1,1).HorizontalAlignment = 3;
					oSheet.Range(oSheet.Cells(i+1, 1), oSheet.Cells(i+1, 11)).MergeCells = true;
				}
				else if(i == 1){
					oSheet.Cells(i+1,1).value = table_src_ip.rows(i).cells(0).innerText;
					oSheet.Cells(i+1,2).value = table_src_ip.rows(i).cells(1).innerText;
					oSheet.Cells(i+1,6).value = table_src_ip.rows(i).cells(2).innerText;
					oSheet.Cells(i+1,2).Font.ColorIndex = 40;
					oSheet.Cells(i+1,6).Font.ColorIndex = 43;
					oSheet.Cells(i+1,2).HorizontalAlignment = 3;					
					oSheet.Cells(i+1,6).HorizontalAlignment = 3;
					oSheet.Cells(i+1,2).Font.Bold = true;
					oSheet.Cells(i+1,6).Font.Bold = true;
					oSheet.Range(oSheet.Cells(i+1, 1), oSheet.Cells(i+2, 1)).MergeCells = true;
					oSheet.Range(oSheet.Cells(i+1, 2), oSheet.Cells(i+1, 5)).MergeCells = true;
					oSheet.Range(oSheet.Cells(i+1, 6), oSheet.Cells(i+1, 11)).MergeCells = true;
				}
				else{
					for (j=0;j<src_ipCell;j++){
					oSheet.Cells(i+1,j+1).Font.Size = 10;//字体大小 
					if (i == 2) {
						if (j < 10) {
							oSheet.Cells(i+1,j+2).value = table_src_ip.rows(i).cells(j).innerText;
						}
					}
					else{
						oSheet.Cells(i+1,j+1).value = table_src_ip.rows(i).cells(j).innerText;
					}
				  }
				}
			} 
			oExcel.Visible = true;   
			oExcel.Columns.AutoFit;
			oExcel.UserControl = true;
			//开始目的IP表格
			
			oWork.Worksheets("Sheet3").Activate();
			oSheet = oWork.ActiveSheet;
			var dst_ipRow = table_dst_ip.rows.length;               //取数据源行数  
			var dst_ipCell = table_dst_ip.rows(2).cells.length;
			dst_ipCell ++;
			for (i=0;i<dst_ipRow;i++){//在Excel中写行  
				if(i == 0){
					oSheet.Cells(i+1,1).value = table_dst_ip.rows(i).cells(0).innerText;					
					oSheet.Cells(i+1,1).Interior.ColorIndex = 17 ;
					oSheet.Cells(i+1,1).Font.ColorIndex = 6;
					oSheet.Cells(i+1,1).Font.Bold = true;
					oSheet.Cells(i+1,1).HorizontalAlignment = 3;
					oSheet.Range(oSheet.Cells(i+1, 1), oSheet.Cells(i+1, 11)).MergeCells = true;
				}
				else if(i == 1){
					oSheet.Cells(i+1,1).value = table_dst_ip.rows(i).cells(0).innerText;
					oSheet.Cells(i+1,2).value = table_dst_ip.rows(i).cells(1).innerText;
					oSheet.Cells(i+1,6).value = table_dst_ip.rows(i).cells(2).innerText;
					oSheet.Cells(i+1,2).Font.ColorIndex = 40;
					oSheet.Cells(i+1,6).Font.ColorIndex = 43;
					oSheet.Cells(i+1,2).HorizontalAlignment = 3;					
					oSheet.Cells(i+1,6).HorizontalAlignment = 3;
					oSheet.Cells(i+1,2).Font.Bold = true;
					oSheet.Cells(i+1,6).Font.Bold = true;
					oSheet.Range(oSheet.Cells(i+1, 1), oSheet.Cells(i+2, 1)).MergeCells = true;
					oSheet.Range(oSheet.Cells(i+1, 2), oSheet.Cells(i+1, 5)).MergeCells = true;
					oSheet.Range(oSheet.Cells(i+1, 6), oSheet.Cells(i+1, 11)).MergeCells = true;
				}
				else{
					for (j=0;j<dst_ipCell;j++){
					oSheet.Cells(i+1,j+1).Font.Size = 10;//字体大小 
					if (i == 2) {
						if (j < 10) {
							oSheet.Cells(i+1,j+2).value = table_dst_ip.rows(i).cells(j).innerText;
						}
					}
					else{
						oSheet.Cells(i+1,j+1).value = table_dst_ip.rows(i).cells(j).innerText;
					}
				  }
				}
			} 
			oExcel.Visible = true;   
			oExcel.Columns.AutoFit;
			oExcel.UserControl = true;
			//开始网络接口表格
			
			oWork.Worksheets("Sheet4").Activate();
			oSheet = oWork.ActiveSheet;
			var ifaceRow = table_iface.rows.length;               //取数据源行数  
			var ifaceCell = table_iface.rows(2).cells.length;
			ifaceCell ++;
			for (i=0;i<ifaceRow;i++){//在Excel中写行  
				if(i == 0){
					oSheet.Cells(i+1,1).value = table_iface.rows(i).cells(0).innerText;					
					oSheet.Cells(i+1,1).Interior.ColorIndex = 17 ;
					oSheet.Cells(i+1,1).Font.ColorIndex = 6;
					oSheet.Cells(i+1,1).Font.Bold = true;
					oSheet.Cells(i+1,1).HorizontalAlignment = 3;
					oSheet.Range(oSheet.Cells(i+1, 1), oSheet.Cells(i+1, 11)).MergeCells = true;
				}
				else if(i == 1){
					oSheet.Cells(i+1,1).value = table_iface.rows(i).cells(0).innerText;
					oSheet.Cells(i+1,2).value = table_iface.rows(i).cells(1).innerText;
					oSheet.Cells(i+1,6).value = table_iface.rows(i).cells(2).innerText;
					oSheet.Cells(i+1,2).Font.ColorIndex = 40;
					oSheet.Cells(i+1,6).Font.ColorIndex = 43;
					oSheet.Cells(i+1,2).HorizontalAlignment = 3;					
					oSheet.Cells(i+1,6).HorizontalAlignment = 3;
					oSheet.Cells(i+1,2).Font.Bold = true;
					oSheet.Cells(i+1,6).Font.Bold = true;
					oSheet.Range(oSheet.Cells(i+1, 1), oSheet.Cells(i+2, 1)).MergeCells = true;
					oSheet.Range(oSheet.Cells(i+1, 2), oSheet.Cells(i+1, 5)).MergeCells = true;
					oSheet.Range(oSheet.Cells(i+1, 6), oSheet.Cells(i+1, 11)).MergeCells = true;
				}
				else{
					for (j=0;j<ifaceCell;j++){
					oSheet.Cells(i+1,j+1).Font.Size = 10;//字体大小 
					if (i == 2) {
						if (j < 10) {
							oSheet.Cells(i+1,j+2).value = table_iface.rows(i).cells(j).innerText;
						}
					}
					else{
						oSheet.Cells(i+1,j+1).value = table_iface.rows(i).cells(j).innerText;
					}
				  }
				}
			} 
			oExcel.Visible = true;   
			oExcel.Columns.AutoFit;
			oExcel.UserControl = true;


			oWork.Worksheets("Sheet1").Activate();
			oExcel.null();
		}

	</script>
	<!-- 全局概况表格 -->
	<div style="max-height:500px;overflow:auto;margin:25px 0;">
	<table id="summarize" width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
		<tr>
			<td class="boldbase" colspan='10'>$date全局统计</td>
		</tr>
		<tr>
			<td style = "width:7%"></td>
			<td style = "width:7%">TCP协议</td>
			<td style = "width:10%">UDP协议</td>
			<td style = "width:10%">其他协议</td>
			<td style = "width:10%">允许的数据包</td>
			<td style = "width:10%">阻断的数据包</td>
			<td style = "width:10%">入侵防御的数据包</td>
			<td style = "width:10%">丢弃的数据包</td>	
			<td style = "width:10%">代理的数据包</td>		
			<td style = "width:10%">防火墙日志总数</td>
		</tr>
		<tr>
			<td>匹配的规则条数</td>
			<td>$tcp</td>
			<td>$udp</td>
			<td>$other</td>
			<td>$accept</td>
			<td>$reject</td>
			<td>$allow</td>
			<td>$drop</td>
			<td>$proxy</td>
			<td>$total_num</td>
		</tr>
	</table>
	</div>
EOF
;	
	if ($total_num) {
		my $src_max = $dst_max = $ifa_max = 1;
		printf <<EOF
	<!-- 按源统计表格 -->
	<div style="max-height:500px;overflow:auto;margin:25px 0;">
	<table id="src_ip" width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
		<tr>
			<td class="boldbase" colspan='11'>$date按源IP统计(前十)</td>
		</tr>
		<tr>
			<td class="boldbase" rowspan="2">源IP</td>
			<td class="boldbase" colspan="4">协议分类</td>
			<td class="boldbase" colspan="6">防火墙动作分类</td>
		</tr>
		<tr>
			<td style = "width:7%">TCP协议</td>
			<td style = "width:7%">UDP协议</td>
			<td style = "width:8%">其他协议</td>
			<td style = "width:8%">分类总数</td>
			<td style = "width:10%">允许的数据包</td>
			<td style = "width:10%">阻断的数据包</td>
			<td style = "width:10%">入侵防御的数据包</td>
			<td style = "width:10%">丢弃的数据包</td>
			<td style = "width:10%">代理的数据包</td>
			<td style = "width:10%">分类总数</td>		
		</tr>
EOF
;
		foreach my $ip (sort { $src_ip{$b} <=> $src_ip{$a} } keys %src_ip){
			if ($src_max < 11) {	
				if ($filestr =~ /\.gz$/) {
					$src_ip{$ip}{'tcp'} = `gzip -dc $filestr|head -$total_num|grep "SRC=$ip "|grep TCP|wc -l`;
					$src_ip{$ip}{'udp'} = `cgzip -dc $filestr|head -$total_num|grep "SRC=$ip "|grep UDP|wc -l`;
					$src_ip{$ip}{'other'} = $src_ip{$ip} - $src_ip{$ip}{'tcp'} - $src_ip{$ip}{'udp'};
					$src_ip{$ip}{'allow'} = `gzip -dc $filestr|head -$total_num|grep "SRC=$ip "|grep ALLOW|wc -l`;
					$src_ip{$ip}{'accept'} = `gzip -dc $filestr|head -$total_num|grep "SRC=$ip "|grep ACCEPT|wc -l`;
					$src_ip{$ip}{'reject'} = `gzip -dc $filestr|head -$total_num|grep "SRC=$ip "|grep REJECT|wc -l`;
					$src_ip{$ip}{'drop'} = `gzip -dc $filestr|head -$total_num|grep "SRC=$ip "|grep DROP|wc -l`;
					$src_ip{$ip}{'proxy'} = $src_ip{$ip} - $src_ip{$ip}{'drop'} - $src_ip{$ip}{'reject'} -$src_ip{$ip}{'accept'} -$src_ip{$ip}{'allow'};
				}
				else{
					$src_ip{$ip}{'tcp'} = `cat $filestr|head -$total_num|grep "SRC=$ip "|grep TCP|wc -l`;
					$src_ip{$ip}{'udp'} = `cat $filestr|head -$total_num|grep "SRC=$ip "|grep UDP|wc -l`;
					$src_ip{$ip}{'other'} = $src_ip{$ip} - $src_ip{$ip}{'tcp'} - $src_ip{$ip}{'udp'};
					$src_ip{$ip}{'allow'} = `cat $filestr|head -$total_num|grep "SRC=$ip "|grep ALLOW|wc -l`;
					$src_ip{$ip}{'accept'} = `cat $filestr|head -$total_num|grep "SRC=$ip "|grep ACCEPT|wc -l`;
					$src_ip{$ip}{'reject'} = `cat $filestr|head -$total_num|grep "SRC=$ip "|grep REJECT|wc -l`;
					$src_ip{$ip}{'drop'} = `cat $filestr|head -$total_num|grep "SRC=$ip "|grep DROP|wc -l`;
					$src_ip{$ip}{'proxy'} = $src_ip{$ip} - $src_ip{$ip}{'drop'} - $src_ip{$ip}{'reject'} -$src_ip{$ip}{'accept'} -$src_ip{$ip}{'allow'};
				}		
				printf <<EOF
				<tr>
					<td style = "width:10%">$ip</td>
					<td style = "width:7%">$src_ip{$ip}{'tcp'}</td>
					<td style = "width:7%">$src_ip{$ip}{'udp'}</td>
					<td style = "width:8%">$src_ip{$ip}{'other'}</td>
					<td style = "width:8%">$src_ip{$ip}</td>
					<td style = "width:10%">$src_ip{$ip}{'accept'}</td>
					<td style = "width:10%">$src_ip{$ip}{'reject'}</td>
					<td style = "width:10%">$src_ip{$ip}{'allow'}</td>
					<td style = "width:10%">$src_ip{$ip}{'drop'}</td>
					<td style = "width:10%">$src_ip{$ip}{'proxy'}</td>
					<td style = "width:10%">$src_ip{$ip}</td>		
				</tr>
EOF
;		
				$src_max ++;
			}	
		}
		printf <<EOF
		</table>
		</div>
		<!-- 按目的统计表格 -->
		<div style="max-height:500px;overflow:auto;margin:25px 0;">
		<table id="dst_ip" width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
			<tr>
				<td class="boldbase" colspan='11'>$date按目的IP统计(前十)</td>
			</tr>
			<tr>
				<td class="boldbase" rowspan="2">目的IP</td>
				<td class="boldbase" colspan="4">协议分类</td>
				<td class="boldbase" colspan="6">防火墙动作分类</td>
			</tr>
			<tr>
				<td style = "width:7%">TCP协议</td>
				<td style = "width:7%">UDP协议</td>
				<td style = "width:8%">其他协议</td>
				<td style = "width:8%">分类总数</td>
				<td style = "width:10%">允许的数据包</td>
				<td style = "width:10%">阻断的数据包</td>
				<td style = "width:10%">入侵防御的数据包</td>
				<td style = "width:10%">丢弃的数据包</td>
				<td style = "width:10%">代理的数据包</td>
				<td style = "width:10%">分类总数</td>		
			</tr>
EOF
;
		foreach my $ip (sort { $dst_ip{$b} <=> $dst_ip{$a} } keys %dst_ip){
			if ($dst_max < 11) {
				if ($filestr =~ /\.gz$/) {
					$dst_ip{$ip}{'tcp'} = `gzip -dc $filestr|head -$total_num|grep "DST=$ip "|grep TCP|wc -l`;
					$dst_ip{$ip}{'udp'} = `cgzip -dc $filestr|head -$total_num|grep "DST=$ip "|grep UDP|wc -l`;
					$dst_ip{$ip}{'other'} = $dst_ip{$ip} - $dst_ip{$ip}{'tcp'} - $dst_ip{$ip}{'udp'};
					$dst_ip{$ip}{'allow'} = `gzip -dc $filestr|head -$total_num|grep "DST=$ip "|grep ALLOW|wc -l`;
					$dst_ip{$ip}{'accept'} = `gzip -dc $filestr|head -$total_num|grep "DST=$ip "|grep ACCEPT|wc -l`;
					$dst_ip{$ip}{'reject'} = `gzip -dc $filestr|head -$total_num|grep "DST=$ip "|grep REJECT|wc -l`;
					$dst_ip{$ip}{'drop'} = `gzip -dc $filestr|head -$total_num|grep "DST=$ip "|grep DROP|wc -l`;
					$dst_ip{$ip}{'proxy'} = $dst_ip{$ip} - $dst_ip{$ip}{'drop'} - $dst_ip{$ip}{'reject'} -$dst_ip{$ip}{'accept'} -$dst_ip{$ip}{'allow'};
				}
				else{
					$dst_ip{$ip}{'tcp'} = `cat $filestr|head -$total_num|grep "DST=$ip "|grep TCP|wc -l`;
					$dst_ip{$ip}{'udp'} = `cat $filestr|head -$total_num|grep "DST=$ip "|grep UDP|wc -l`;
					$dst_ip{$ip}{'other'} = $dst_ip{$ip} - $dst_ip{$ip}{'tcp'} - $dst_ip{$ip}{'udp'};
					$dst_ip{$ip}{'allow'} = `cat $filestr|head -$total_num|grep "DST=$ip "|grep ALLOW|wc -l`;
					$dst_ip{$ip}{'accept'} = `cat $filestr|head -$total_num|grep "DST=$ip "|grep ACCEPT|wc -l`;
					$dst_ip{$ip}{'reject'} = `cat $filestr|head -$total_num|grep "DST=$ip "|grep REJECT|wc -l`;
					$dst_ip{$ip}{'drop'} = `cat $filestr|head -$total_num|grep "DST=$ip "|grep DROP|wc -l`;
					$dst_ip{$ip}{'proxy'} = $dst_ip{$ip} - $dst_ip{$ip}{'drop'} - $dst_ip{$ip}{'reject'} -$dst_ip{$ip}{'accept'} -$dst_ip{$ip}{'allow'};
				}	
				printf <<EOF
				<tr>
					<td style = "width:10%">$ip</td>
					<td style = "width:7%">$dst_ip{$ip}{'tcp'}</td>
					<td style = "width:7%">$dst_ip{$ip}{'udp'}</td>
					<td style = "width:8%">$dst_ip{$ip}{'other'}</td>
					<td style = "width:8%">$dst_ip{$ip}</td>
					<td style = "width:10%">$dst_ip{$ip}{'accept'}</td>
					<td style = "width:10%">$dst_ip{$ip}{'reject'}</td>
					<td style = "width:10%">$dst_ip{$ip}{'allow'}</td>
					<td style = "width:10%">$dst_ip{$ip}{'drop'}</td>
					<td style = "width:10%">$dst_ip{$ip}{'proxy'}</td>
					<td style = "width:10%">$dst_ip{$ip}</td>		
				</tr>
EOF
;			
				$dst_max ++;
			}
		}
		printf <<EOF
		</table>
		</div>
		<!-- 按网络接口统计表格 -->
		<div style="max-height:500px;overflow:auto;margin:25px 0;">
		<table id="iface" width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
		<tr>
			<td class="boldbase" colspan='11'>$date按网络接口统计(前十)</td>
		</tr>
		<tr>
			<td class="boldbase" rowspan="2">网络接口</td>
			<td class="boldbase" colspan="4">协议分类</td>
			<td class="boldbase" colspan="6">防火墙动作分类</td>
		</tr>
		<tr>
			<td style = "width:7%">TCP协议</td>
			<td style = "width:7%">UDP协议</td>
			<td style = "width:8%">其他协议</td>
			<td style = "width:8%">分类总数</td>
			<td style = "width:10%">允许的数据包</td>
			<td style = "width:10%">阻断的数据包</td>
			<td style = "width:10%">入侵防御的数据包</td>
			<td style = "width:10%">丢弃的数据包</td>
			<td style = "width:10%">代理的数据包</td>
			<td style = "width:10%">分类总数</td>		
		</tr>
EOF
;
		foreach my $ip (sort { $iface{$b} <=> $iface{$a} } keys %iface){
			if ($ifa_max < 11 && $iface{$ip} > 0) {
				if ($filestr =~ /\.gz$/) {
					$iface{$ip}{'tcp'} = `gzip -dc $filestr|head -$total_num|grep "$ip "|grep TCP|wc -l`;
					$iface{$ip}{'udp'} = `cgzip -dc $filestr|head -$total_num|grep "$ip "|grep UDP|wc -l`;
					$iface{$ip}{'other'} = $iface{$ip} - $iface{$ip}{'tcp'} - $iface{$ip}{'udp'};
					$iface{$ip}{'allow'} = `gzip -dc $filestr|head -$total_num|grep "$ip "|grep ALLOW|wc -l`;
					$iface{$ip}{'accept'} = `gzip -dc $filestr|head -$total_num|grep "$ip "|grep ACCEPT|wc -l`;
					$iface{$ip}{'reject'} = `gzip -dc $filestr|head -$total_num|grep "$ip "|grep REJECT|wc -l`;
					$iface{$ip}{'drop'} = `gzip -dc $filestr|head -$total_num|grep "$ip "|grep DROP|wc -l`;
					$iface{$ip}{'proxy'} = $iface{$ip} - $iface{$ip}{'drop'} - $iface{$ip}{'reject'} -$iface{$ip}{'accept'} -$iface{$ip}{'allow'};
				}
				else{
					$iface{$ip}{'tcp'} = `cat $filestr|head -$total_num|grep "$ip "|grep TCP|wc -l`;
					$iface{$ip}{'udp'} = `cat $filestr|head -$total_num|grep "$ip "|grep UDP|wc -l`;
					$iface{$ip}{'other'} = $iface{$ip} - $iface{$ip}{'tcp'} - $iface{$ip}{'udp'};
					$iface{$ip}{'allow'} = `cat $filestr|head -$total_num|grep "$ip "|grep ALLOW|wc -l`;
					$iface{$ip}{'accept'} = `cat $filestr|head -$total_num|grep "$ip "|grep ACCEPT|wc -l`;
					$iface{$ip}{'reject'} = `cat $filestr|head -$total_num|grep "$ip "|grep REJECT|wc -l`;
					$iface{$ip}{'drop'} = `cat $filestr|head -$total_num|grep "$ip "|grep DROP|wc -l`;
					$iface{$ip}{'proxy'} = $iface{$ip} - $iface{$ip}{'drop'} - $iface{$ip}{'reject'} -$iface{$ip}{'accept'} -$iface{$ip}{'allow'};
				}	
				printf <<EOF
				<tr>
					<td style = "width:10%">$ip</td>
					<td style = "width:7%">$iface{$ip}{'tcp'}</td>
					<td style = "width:7%">$iface{$ip}{'udp'}</td>
					<td style = "width:8%">$iface{$ip}{'other'}</td>
					<td style = "width:8%">$iface{$ip}</td>
					<td style = "width:10%">$iface{$ip}{'accept'}</td>
					<td style = "width:10%">$iface{$ip}{'reject'}</td>
					<td style = "width:10%">$iface{$ip}{'allow'}</td>
					<td style = "width:10%">$iface{$ip}{'drop'}</td>
					<td style = "width:10%">$iface{$ip}{'proxy'}</td>
					<td style = "width:10%">$iface{$ip}</td>		
				</tr>
EOF
;			
				$ifa_max ++;
			}
		}
EOF
;
		print "</table></div>"			
	}		
	printf <<EOF
	<div class='containter-div-header' style='padding:0px 5px 5px;margin:0px auto 10px;width:95%;text-align:center'>
		  <table><tr><td style="text-align:center">
			<input class='net_button' type='submit' style='color: black; background-image: url(\"/images/button.jpg\");' value='导出报表' id='export' onclick="export_to_excel();">
			</td></tr></table>
		</div>
EOF
;	
}
sub oldernewer {
    printf <<END
		<div class='page-footer' style='padding:0px 5px 5px;margin:0px auto 10px;width:95%'>
<table width='100%' align='center'>
	<tr>
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <td width='180px'>%s: <input type="text" SIZE="12" id="inputDate" name='DATE' VALUE="$date" />
<script type="text/javascript"> 
    ESONCalendar.bind("inputDate");
</script>

	</td>
    <td  align='left'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
	</form>
  </tr></table>	
END
,
_('Jump to Date'),
_('sure'),
;
}
