#!/usr/bin/perl

#file:detect_ajax.cgi
#author:zhangzheng
use CGI();
use URI::Escape;
require '/var/efw/header.pl';

my @parValue = split(/=/,$ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
&validateUser();

sub read_jsons($$$$$$)
{
	my $jsonfile = shift;
	my $page_name = shift;
	my $page_mark = shift;
	my $top  = shift;
	my $left = shift;
	my $up   = shift;
	my $is_show_tr_1 = "";
	my $is_show_tr_2 = "";
	my $is_show_tr_3 = "";
	my $is_show_tr_4 = "";
	my $is_show_tr_5 = "";
	
	my $string = "";
	open(MYFILE,"$jsonfile");
	foreach my $line (<MYFILE>) 
	{
		chomp($line);
		$string .= $line;
	}
	close (MYFILE);

	$string =~ s/\r//g;
	$string =~ s/\n//g;
	$string =~ s/\t//g;
	
	my $hash = JSON::XS->new->decode($string);
	my $mark_content = $hash->{$page_name}{$page_mark};
	if($mark_content)
	{
	###获取描述列表
	my $Describe = $mark_content->{"Describe"};
	my $Describe_ul = "";
	if($Describe ne "无" && $Describe ne "")
	{
		$Describe_ul = "<ul class='sub_ul'>";
		my @temp_describe = split("<br />",$Describe);
		foreach $decri(@temp_describe)
		{
			$Describe_ul .= "<li>".$decri."</li>";
		}
		$Describe_ul .= "</ul>";
	}else{
		$is_show_tr_1 = "class='hidden_class'";
	}
	###获取格式列表
	my $Format = $mark_content->{"Format"};
	my $Format_ul = "";
	if($Format ne "无" && $Format ne "")
	{
		$Format_ul = "<ul class='sub_ul'>";
		my @temp_format = split("<br />",$Format);
		foreach $for(@temp_format)
		{
			$Format_ul .= "<li>".$for."</li>";
		}
		$Format_ul .= "</ul>";
	}else{
		$is_show_tr_2 = "class='hidden_class'";
	}
	###获取例子列表
	my $Example = $mark_content->{"Example"};
	my $Example_ul = "";
	if($Example ne "无" && $Example ne "")
	{
		$Example_ul = "<ul class='sub_ul'>";
		my @temp_example = split("<br />",$Example);
		foreach $ex(@temp_example)
		{
			$Example_ul .= "<li>".$ex."</li>";
		}
		$Example_ul .= "</ul>";
	}else{
		$is_show_tr_3 = "class='hidden_class'";
	}
	###获取例子说明列表
	my $Example_notes = $mark_content->{"Example_notes"};
	my $Example_notes_ul = "";
	if($Example_notes ne "无" && $Example_notes ne "")
	{
		$Example_notes_ul = "<ul class='sub_ul'>";
		my @temp_example_notes = split("<br />",$Example_notes);
		foreach $exno(@temp_example_notes)
		{
			$Example_notes_ul .= "<li>".$exno."</li>";
		}
		$Example_notes_ul .= "</ul>";
	}else{
		$is_show_tr_4 = "class='hidden_class'";
	}
	###获取提示列表
	my $Tips = $mark_content->{"Tips"};
	my $Tips_ul = "";
	if($Tips ne "无" && $Tips ne "")
	{
		$Tips_ul = "<ul class='sub_ul'>";
		my @temp_Tips = split("<br />",$Tips);
		foreach $tips(@temp_Tips)
		{
			$Tips_ul .= "<li>".$tips."</li>";
		}
		$Tips_ul .= "</ul>";
	}else{
		$is_show_tr_5 = "class='hidden_class'";
	}
	my $str = "";
	if($up eq "down")
	{
		$str = "<div class='help_div_box' style='position:relative;zoom:1;width:1px;height:1px;'><div class='help_div' style='position:absolute;top:".$top."px;left:".$left."px;background:  url(/images/bubble_top.png) no-repeat right top;width:350px;font-size: 0.9em;font-weight:normal;color:#666;display:none;z-index:9;'><div class='help_ul'  style='	padding:0px 8px 8px 10px;margin:11px 0px 10px 27px;border-left:1px solid #415f6e;border-right:1px solid #415f6e;border-bottom:1px solid #415f6e;background-color:#def1fe;'><table cellpadding='0' cellspacing='0' style='border:none;' ><tr ".$is_show_tr_1."><td width='53px' nowrap='nowrap'  valign='top' style='border:none;' ><b class='notes'>描述信息</b></td><td  style='border:none;' align='left' >".$Describe_ul."</td></tr><tr ".$is_show_tr_2."><td valign='top' nowrap='nowrap' style='border:none;'><b class='notes'>格式要求</b></td><td  nowrap='nowrap' align='left' style='border:none;'>".$Format_ul."</td></tr><tr ".$is_show_tr_3."><td valign='top' nowrap='nowrap' style='border:none;'><b class='notes'>示例展示</b></td><td  style='border:none;' align='left' >".$Example_ul."</td><tr ".$is_show_tr_4."><td valign='top'  nowrap='nowrap' style='border:none;'><b class='notes'>示例说明</b></td><td style='border:none;' align='left'>".$Example_notes_ul."</td><tr ".$is_show_tr_5."><td valign='top'  nowrap='nowrap' style='border:none;'><b class='notes'>提示信息</b></td><td  style='border:none;' >".$Tips_ul."</td></tr></table></div></div></div>";
	}else{
		$str = "<div class='help_div_box' style='position:relative;zoom:1;width:0px;height:0px;'><div class='help_div' style='position:absolute;top:".$top."px;left:".$left."px;background:  url(/images/bubble_bottom.png) no-repeat right bottom;width:350px;font-size: 0.9em;font-weight:normal;color:#666;display:none;z-index:9;'><div class='help_ul'  style='	padding:8px 8px 8px 10px;margin:0px 0px 10px 27px;border-left:1px solid #415f6e;border-right:1px solid #415f6e;border-top:1px solid #415f6e;background-color:#def1fe;'><table cellpadding='0' cellspacing='0' style='border:none;' ><tr ".$is_show_tr_1."><td width='53px' nowrap='nowrap'  valign='top' style='border:none;' ><b class='notes'>描述信息</b></td><td  style='border:none;' align='left' >".$Describe_ul."</td></tr><tr ".$is_show_tr_2."><td valign='top' nowrap='nowrap' style='border:none;'><b class='notes'>格式要求</b></td><td  nowrap='nowrap' align='left' style='border:none;'>".$Format_ul."</td></tr><tr ".$is_show_tr_3."><td valign='top' nowrap='nowrap' style='border:none;'><b class='notes'>示例展示</b></td><td  style='border:none;' align='left' >".$Example_ul."</td><tr ".$is_show_tr_4."><td valign='top'  nowrap='nowrap' style='border:none;'><b class='notes'>示例说明</b></td><td style='border:none;' align='left'>".$Example_notes_ul."</td><tr ".$is_show_tr_5."><td valign='top'  nowrap='nowrap' style='border:none;'><b class='notes'>提示信息</b></td><td  style='border:none;' >".$Tips_ul."</td></tr></table></div></div></div>";
	}
		return $str;
	}else{
		return "";
	}
	

}
my %help;
&readhash("/var/efw/help/setting",\%help);
if ($help{"HELP_ENABLED"} eq "on"){
	my $string="";
	my $devices_help_hash1 = read_jsons("/home/httpd/help/qos_devices_help.json","devices","目标设备","-10","30","down");
	my $devices_help_hash2 = read_jsons("/home/httpd/help/qos_devices_help.json","devices","下行带宽","-10","30","down");
	my $devices_help_hash3 = read_jsons("/home/httpd/help/qos_devices_help.json","devices","上行带宽","-10","30","down");
	my $class_help_hash1 = read_jsons("/home/httpd/help/qos_class_help.json","class","qos device","-10","30","down");
	my $class_help_hash2 = read_jsons("/home/httpd/help/qos_class_help.json","class","类名称","-10","30","down");
	my $class_help_hash3 = read_jsons("/home/httpd/help/qos_class_help.json","class","保留","-10","30","down");
	my $class_help_hash4 = read_jsons("/home/httpd/help/qos_class_help.json","class","限制","-10","30","down");
	my $rules_help_hash1 = read_jsons("/home/httpd/help/qos_rules_help.json","rules","源","-10","30","down");
	my $rules_help_hash2 = read_jsons("/home/httpd/help/qos_rules_help.json","rules","目标类","-10","30","down");
	my $rules_help_hash3 = read_jsons("/home/httpd/help/qos_rules_help.json","rules","目的ip","-10","30","down");
	my $rules_help_hash4 = read_jsons("/home/httpd/help/qos_rules_help.json","rules","服务","-10","30","down");
	my $rules_help_hash5 = read_jsons("/home/httpd/help/qos_rules_help.json","rules","TOS-DSCP","-10","30","down");

	$string = $devices_help_hash1."-###".$devices_help_hash2."-###".$devices_help_hash3."---###".$class_help_hash1."-###".$class_help_hash2."-###".$class_help_hash3."-###".$class_help_hash4."---###".$rules_help_hash1."-###".$rules_help_hash2."-###".$rules_help_hash3."-###".$rules_help_hash4."-###".$rules_help_hash5;
	print $string;
}