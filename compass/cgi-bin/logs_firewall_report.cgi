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


use POSIX();
use CGI ':standard';
use CGI::Carp qw (fatalsToBrowser);
use GD;
use GD::Graph::bars;
use GD::Graph::Data;
use GD::Graph::Error;
use Encode;
use warnings;
use Spreadsheet::WriteExcel;
require '/var/efw/header.pl';
require 'logs_common.pl';
my %cgiparams;
my $json = new JSON::XS;
my %selected;
my %allows,%drops;
my $log_name = "防火墙";
my %name = ("SRC" => "源IP","DST" => "目的IP");

my $logfile="/var/log/firewall";
my $bars = "/images/bars.png";
my @files = sort(glob("${logfile}-*.gz"));
my $name = "firewall";

&getcgihash(\%cgiparams);
 
my $eth_all = `ifconfig |grep eth`;
my @temp = split(/\n/,$eth_all);
my @eths;
foreach my $elem(@temp){
	$elem =~ /(eth\d+)\s*/;
	push(@eths,$1);
}
push(@eths,"br0");
push(@eths,"br1");

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
my $type = $cgiparams{'type'};
if (!$cgiparams{'type'}) {
    $type = 'SRC';
}
my $iface = $cgiparams{'iface'};
my $report_title = $cgiparams{'report_title'};
$selected{$type} = "selected";
$selected{$iface} = "selected";
my $lines = 0;
my @log = ();
my $test=0;
&export_file("/tmp/export.xls",$cgiparams{'ACTION'},$date,$log_name);
&showhttpheaders();
if($cgiparams{'ACTION'} eq 'load_data'){
    my %ret_data;
    %ret_data->{'eths'} = \@eths;
    my $ret = $json->encode(\%ret_data);
    print $ret;
    exit;
}
$extraheaders = <<EOF
<script type="text/javascript" src="/include/jquery.js"></script>
<link rel="stylesheet" type="text/css" href="/include/jquery-ui.min.css" />
<script language="JavaScript" src="/include/jquery.js"></script>
<script language="JavaScript" src="/include/jquery-ui.js"></script>
<script type="text/javascript" src="/include/waiting.js"></script>
<script type="text/javascript" src="/include/jquery.flot.js"></script>
<script type="text/javascript" src="/include/ESONCalendar.js"></script>
<script language="JavaScript" src="/include/add_panel.js"></script>
<script language="JavaScript" src="/include/list_panel.js"></script>
<script language="JavaScript" src="/include/message_manager.js"></script>
<script type="text/javascript" src="/include/logs_firewall_report.js"></script>
<link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />
<link rel="stylesheet" href="/include/all_log.css" type="text/css" />
<link rel="stylesheet" href="/include/add_list_base.css" type="text/css" />

EOF
;

my $firstdatearr = dateToArray($firstdatestring);
my $lastdatearr = dateToArray($today);

&openpage(_('Firewall log'), 1, $extraheaders);

&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
&openbox_for_report('100%', 'left', _('统计报表'));
print "<div class='paging-div-header'>";
oldernewer();
print "</div>";
begin();
&display_table();
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
sub draw_pic{
    my $data = shift;
    system("/usr/bin/sudo /home/httpd/cgi-bin/draw_report.pl $data");  
}
sub get_data{
    my %data;
    my $filestr = shift;
    my $type = shift;
    my $iface = shift;
    if (!(open (FILE,($filestr =~ /.gz$/ ? "gzip -dc $filestr |" : $filestr)))) {
    #$errormessage = _('No (or only partial) logs exist for the given day')."!";
    }
    while (defined($line = <FILE>)){
        if ($iface) {
            if($line =~ /$iface.*$type=(\d+\.\d+\.\d+\.\d+)/){
                my $ip = $1;
                if ($data{$ip} < 1) {
                    $data{$ip} = 1;
                }
                else{
                    $data{$ip} ++;
                }
                if ($line =~ /ACCEPT|ALLOW/) {
                    if ($allows{$ip} < 1) {
                        $allows{$ip} = 1;
                    }
                    else{
                        $allows{$ip} ++;
                    }
                }
                elsif($line =~ /DROP|REJECT/){
                    if ($drops{$ip} < 1) {
                        $drops{$ip} = 1;
                    }
                    else{
                        $drops{$ip} ++;
                    }
                }
            }
        }
        else{
            if($line =~ /$type=(\d+\.\d+\.\d+\.\d+)/){
                my $ip = $1;
                if ($data{$ip} < 1) {
                    $data{$ip} = 1;
                }
                else{
                    $data{$ip} ++;
                }

                if ($line =~ /ACCEPT|ALLOW/) {
                    if ($allows{$ip} < 1) {
                        $allows{$ip} = 1;
                    }
                    else{
                        $allows{$ip} ++;
                    }
                }
                elsif($line =~ /DROP|REJECT/){
                    if ($drops{$ip} < 1) {
                        $drops{$ip} = 1;
                    }
                    else{
                        $drops{$ip} ++;
                    }
                }
            }
        }
    }
    close(FILE);
    return %data;
}
sub display_table(){
    my %data = &get_data($filestr,$type,$iface);
    my $num = 0;
    my $all_data = "begin";
    my $titles = $report_title."防火墙日志报表";
    my @ip;
    foreach my $key(sort { $data{$b} <=> $data{$a} } keys %data){
        my $elem = "$key,$data{$key}";
        $all_data .= "-$elem";
        $num ++;
        push(@ip,$key);
        if ($num >= 15) {
             last;
         } 
    }
    $num ++;


    if ($num > 1) {
       open(FILE,">/tmp/datafile");
       print FILE "$titles,$name{$type},,\n";
        for (my $i = 0;$i < @ip;$i ++){
            if (!$allows{$ip[$i]}) {
                $allows{$ip[$i]} = 0;
            }
            if (!$drops{$ip[$i]}) {
                $drops{$ip[$i]} = 0;
            }
            if (!$data{$ip[$i]}) {
                $data{$ip[$i]} = 0;
            }
            print FILE "$ip[$i],$data{$ip[$i]},$allows{$ip[$i]},$drops{$ip[$i]}\n";###将数据写入文件，生成报表
        }
       close(FILE);
       &draw_pic($all_data);
    printf <<END
    <div style="max-height:500px;overflow:auto;margin:25px 0;">
    <table id="summarize" width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
    <tr><td colspan="5" class="boldbase" id="report_title">$titles</td></tr>
    <tr><td rowspan="$num" width="50%"><img id="images" src="/images/bars.png" ALT="统计图表" TITLE="test"></td><td id="names">$name{$type}</td><td>总次数</td><td>允许次数</td><td>阻断次数</td></tr>
END
;  
    for (my $i = 0;$i < @ip;$i ++){
        if (!$allows{$ip[$i]}) {
            $allows{$ip[$i]} = 0;
        }
        if (!$drops{$ip[$i]}) {
            $drops{$ip[$i]} = 0;
        }
        if (!$data{$ip[$i]}) {
            $data{$ip[$i]} = 0;
        }
        print "<tr><td>$ip[$i]</td><td>$data{$ip[$i]}</td><td>$allows{$ip[$i]}</td><td>$drops{$ip[$i]}</td></tr>";
    }

    printf <<END  
    </table>
    </div>
END
;   
    }
    else{
        printf <<END
        <div style="max-height:500px;overflow:auto;margin:25px 0;">
        <table id="summarize" width='100%' cellpadding="0" class='ruleslist' cellspacing="1">
        <tr class="env table_note fordel"><td><div><img src="/images/pop_warn_min.png" />无审计信息</div></td></tr>
        </table>
    </div>
END
;    
    }
    
}
sub oldernewer {
    printf <<END
		<div id="oldernewer">
	<tr>
	<div id="button-install" class="toolbar">
    <button class="imaged-button" style="margin-left:6px; margin-top:3px; float:left;" onclick="install_for_report();">
        <img class="button-image" src="../images/searchlog.png">
        <span class="button-text">报表条件设置</span>
    </button>
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input class='submitbutton' type='hidden' name='ACTION' value='download' />
    <td align="right"><input class='imaged-button' type='submit' style='color: black; margin-left:15px; margin-top:3px; background-image: url(\"/images/phbackground.png\");' value='导出报表' id='export' "></td>
    </form>
    </div>
</script>
END
;	
}
sub export_file(){
    my $file = shift;
    my $action = shift;
    my $date = shift;
    my $log_name = shift;
    if ($action eq 'download') {
        if( -e "$file"){
            my $log_message = "导出了".$date."的".$log_name."报表";
            &user_log($log_message);
            open(DLFILE, "<$file") || Error('open', "$file");  
            @fileholder = <DLFILE>;  
            close (DLFILE) || Error ('close', "$file"); 
            print "Content-Type:application/x-download\n";  
            print "Content-Disposition:attachment;filename=firewall_logs.xls\n\n";
            print @fileholder;
            exit;
        }
        else{
          print "Content-type:text/html\n\n";
          print qq{<html><head><title>The file doesn't exist.</title></head><body><br/><br/>
                <br/><center><h1>The file does not exist.</h1></center></body></html>};
          exit;
        }
    }
}

sub opentitle
{
    my $error=shift;
    my $warning=shift;
    my $note=shift;

    errorbox($error);
    warnbox($warning);
    notificationbox($note);
}

sub closebigbox {
    return;
}

sub openbox_for_report
{
    $width = $_[0];
    $align = $_[1];
    $caption = $_[2];
    $id = $_[3];
    
    if($id ne '') {
        $id = "id=\"$id\"";
    }
    else {
        $id="";
    }
    
    
    printf <<EOF
<div $id class="containter-div">
EOF
    ;
    printf<<EOF
    <div id="mesg_box" class="container"></div>
    <input type="hidden" id="apply-control" value="$reload">
    <div id="add_panel" class="container"></div>
EOF
    ;
    if ($caption) {
        printf <<EOF
     <span class="toolbar"><span style="display:block;float:left;margin-top:6px;margin-left:10px;"><img src='/images/applications-blue.png' />$caption</span><span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;">*表示必选项</span></span>
EOF
;
    }
    else {
             printf <<EOF
        <span class="toolbar"><img src='/images/applications-blue.png' />&nbsp;</span>
EOF
;
    }
    
    printf <<EOF
    <div class="containter-div-content">
EOF
    ;
}
