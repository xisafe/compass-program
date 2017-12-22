# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
# Copyright (C) 2002 Alex Hudson - getcgihash() rewrite
# Copyright (c) 2002/04/13 Steve Bootes - add alias section, helper functions
# Copyright (c) 2002/08/23 Mark Wormgoor <mark@wormgoor.com> validfqdn()
# Copyright (c) 2003/09/11 Darren Critchley <darrenc@telus.net> srtarray()
# Copyright (c) 2005/2007 Endian GmbH/srl <info@endian.it>
#
# $Id: header.pl,v 1.34.2.39 2004/11/26 15:51:27 alanh Exp $
#
use CGI();
use CGI::Cookie;
use Socket;
use Time::Local;
use endian_locale;
use Net::IPv4Addr qw (:all);
use HTML::Entities;
use JSON::XS;
use URI::Escape;
use Encode;
use Data::Dumper;
use Digest::MD5;
use Crypt::OpenSSL::AES;
use Crypt::CBC;
use Try::Tiny;
use MIME::Base64;
#use Unicode::Escape qw(escape unescape);

require '/var/efw/authorization.pl';
require "/home/httpd/cgi-bin/menuconf.pl";
require "/home/httpd/cgi-bin/list_panel_opt.pl";

$|=1; # line buffering

sub escape_quotes($) {
	$var = shift;
	$var =~ s/(["\"", "'"])/\\$1/g;
	return $var;
}

sub get_version() {
	$version_custom = </etc/release*.custom>;
	$version_vendor = </etc/release*.vendor>;

	if ( $version_custom ) {
		$release = $version_custom;
	} elsif ( $version_vendor ) {
		$release = $version_vendor;
	} else {
		$release = '/etc/release';
	}
 
	open(FILE, $release);
	while (<FILE>) {
		$read_ver = $_;
	}

	if ($read_ver =~ /^$/) {
		return "Endian Firewall (unknown version)";
	}
	return $read_ver;
}

#author:zhouyuan
#date:2011-07-11
#function:当表格没有内容时的提示信息
sub no_tr($$)
{
	my $cols = shift;#当前表格的列数
	my $note_str = shift;#当前没有内容的提示信息
printf <<EOF
	<tr class="env table_note fordel"><td colspan='$cols' ><div><img src="/images/pop_warn_min.png" />%s</div></td></tr>
EOF
,$note_str
;
}

#author:zhouyuan
#date:2011-09-30
#function:当没有曲线图时
sub no_graph($)
{
	my $note_str = shift;#当前没有内容的提示信息
	my $str = '<table><tr class="env table_note fordel"><td><div><img src="/images/pop_warn_min.png" />'.$note_str.'</div></td></tr></table>';
	return $str;
}


#author:zhouyuan
#date:2011-09-30
#function:处理系统的日期格式
sub deal_date($)
{
	$current_data = shift;
	my $year;
	my $month;
	my $day;
	my $hour;
	my $min;
	my $sec;
	
	my %month =(
				 'Jan' => '1',
				 'Feb' => '2',
				 'Mar' => '3',
				 'Apr' => '4',
				 'May' => '5',
				 'Jun' => '6',
				 'Jul' => '7',
				 'Aug' => '8',
				 'Sep' => '9',
				 'Oct' => '10',
				 'Nov' => '11',
				 'Dec' => '12',
			);
			
	#匹配TUE May 31 01:10:10 2011这种格式
	if($current_data =~ /[A-Za-z]+ +([A-Za-z]+) ([0-9]+) +([0-9]+)\:([0-9]+)\:([0-9]+) +([0-9]+)/)
	{
		$month = $month{$1};
		$day   = $2;
		$hour  = $3;
		$min   = $4;
		$sec   = $5;
		$year  = $6;
		return $year."-".$month."-".$day." ".$hour.":".$min.":".$sec;
	}
	
	#匹配May 31 01:10:10这种格式Sun, 01 Apr 2012 05:10:12
	if($current_data =~ /^([A-Za-z]+) +([0-9]+) +([0-9]+)\:([0-9]+)\:([0-9]+)/)
	{
		$month = $month{$1};
		$day   = $2;
		$hour  = $3;
		$min   = $4;
		$sec   = $5;
		return $month."月".$day."日 ".$hour.":".$min.":".$sec;
	}
	
	#匹配Tue, 31 May 2011 00:42:42这种格式
	elsif($current_data =~ /[A-Za-z]+, +([0-9]+) +([A-Za-z]+) +([0-9]+) +([0-9]+)\:([0-9]+)\:([0-9]+)/)
	{
		$month = $month{$2};
		$day   = $1;
		$hour  = $4;
		$min   = $5;
		$sec   = $6;
		$year  = $3;
		return  $year."-".$month."-".$day." ".$hour.":".$min.":".$sec;
	}elsif($current_data =~ /[A-Za-z]+ +([A-Za-z]+) +([0-9]+) +([0-9]+)\:([0-9]+)\:([0-9]+) +([0-9]+)/)
	{
		$month = $month{$1};
		$day   = $2;
		$hour  = $5;
		$min   = $4;
		$sec   = $3;
		$year  = $6;
		return  $year."-".$month."-".$day." ".$hour.":".$min.":".$sec;
	}{
		return $current_data;
	}
}


###修改时间：2011-09-20      ###
###修改人  ：周圆              ###
###目的    ：读帮助的json文件###
sub read_json($$$$$$)
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
		$str = "<div class='help_div_box' style='position:relative;zoom:1;width:1px;height:1px;'><div class='help_div' style='position:absolute;top:".$top."px;left:".$left."px;background:  url(../images/bubble_top.png) no-repeat right top;width:350px;font-size: 0.9em;font-weight:normal;color:#666;display:none;z-index:9;'><div class='help_ul'  style='    padding:0px 8px 8px 10px;margin:11px 0px 10px 27px;border-left:1px solid #415f6e;border-right:1px solid #415f6e;border-bottom:1px solid #415f6e;background-color:#def1fe;'><table cellpadding='0' cellspacing='0' style='border:none;' ><tr ".$is_show_tr_1."><td width='53px' nowrap='nowrap'  valign='top' style='border:none;' ><b class='notes'>描述信息</b></td><td  style='border:none;' align='left' >".$Describe_ul."</td></tr><tr ".$is_show_tr_2."><td valign='top' nowrap='nowrap' style='border:none;'><b class='notes'>格式要求</b></td><td  nowrap='nowrap' align='left' style='border:none;'>".$Format_ul."</td></tr><tr ".$is_show_tr_3."><td valign='top' nowrap='nowrap' style='border:none;'><b class='notes'>示例展示</b></td><td  style='border:none;' align='left' >".$Example_ul."</td><tr ".$is_show_tr_4."><td valign='top'  nowrap='nowrap' style='border:none;'><b class='notes'>示例说明</b></td><td style='border:none;' align='left'>".$Example_notes_ul."</td><tr ".$is_show_tr_5."><td valign='top'  nowrap='nowrap' style='border:none;'><b class='notes'>提示信息</b></td><td  style='border:none;' >".$Tips_ul."</td></tr></table></div></div></div>";
	}else{
		$str = "<div class='help_div_box' style='position:relative;zoom:1;width:0px;height:0px;'><div class='help_div' style='position:absolute;top:".$top."px;left:".$left."px;background:  url(../images/bubble_bottom.png) no-repeat right bottom;width:350px;font-size: 0.9em;font-weight:normal;color:#666;display:none;z-index:9;'><div class='help_ul'  style='  padding:8px 8px 8px 10px;margin:0px 0px 10px 27px;border-left:1px solid #415f6e;border-right:1px solid #415f6e;border-top:1px solid #415f6e;background-color:#def1fe;'><table cellpadding='0' cellspacing='0' style='border:none;' ><tr ".$is_show_tr_1."><td width='53px' nowrap='nowrap'  valign='top' style='border:none;' ><b class='notes'>描述信息</b></td><td  style='border:none;' align='left' >".$Describe_ul."</td></tr><tr ".$is_show_tr_2."><td valign='top' nowrap='nowrap' style='border:none;'><b class='notes'>格式要求</b></td><td  nowrap='nowrap' align='left' style='border:none;'>".$Format_ul."</td></tr><tr ".$is_show_tr_3."><td valign='top' nowrap='nowrap' style='border:none;'><b class='notes'>示例展示</b></td><td  style='border:none;' align='left' >".$Example_ul."</td><tr ".$is_show_tr_4."><td valign='top'  nowrap='nowrap' style='border:none;'><b class='notes'>示例说明</b></td><td style='border:none;' align='left'>".$Example_notes_ul."</td><tr ".$is_show_tr_5."><td valign='top'  nowrap='nowrap' style='border:none;'><b class='notes'>提示信息</b></td><td  style='border:none;' >".$Tips_ul."</td></tr></table></div></div></div>";
	}
		return $str;
	}else{
		return "";
	}
	

}







#author:zhouyuan
#date:2011-07-11
#function: 一个可以伸缩隐藏的div层
sub show_hidden_box($)
{
	my $title = shift;
printf <<EOF
<div class="show_hidden">
<div class="show_hidden_header"><img src="/images/show.png"  />$title</div>
<div class="show_hidden_content">
EOF
;
}


#author:zhouyuan
#date:2011-07-11
#function: 结束一个可以伸缩隐藏的div层
sub close_show_hidden()
{
printf <<EOF
</div>
</div>
EOF
;
}



#处理得到的字符串显示形式，将其嵌套在表格内
#author：zhouyuan
#Date：2011-07-01
sub pre_string($$)
{
	my $ini_str = shift;
	my $separate = shift;
	my @str_ary = split('\\n',$ini_str);
	my $new_str = "";#用于存放处理过后的字符串
	foreach my $str(@str_ary )
	{
		
		my @sub_arry = split('$separate',$str);

		$sub_arry[0] = $sub_arry[0] + 0;#将$sub_arry[0]强制转化为数字
		my $class = "class='odd'";
		
		if($sub_arry[0] != 0)
		{
			$class="class='env'";
		}
		$new_str .= "<tr  ".$class."><td>".$str."</td></tr>";
		
	}
	print $new_str;
}

###delete the same data
###eg 192.1.1.1 192.1.1.1 192.1.1.2  will delete one 192.1.1.1
sub delete_same_data($){
	my $data = shift;
	my %exist,@temp;
	my $save = "";
	@temp = split(/&/,$data);
	foreach my $elem (@temp){
		if (!$exist{$elem}) {
			$save = $save."&".$elem;
		}
		$exist{$elem} = 1;
	}
	$save =~s/^\&//;
	return $save;
}

sub logger_with_prefix($$$$$){
	my $prefix = shift;
	my $user = shift;
	my $message = shift;
	my $level = shift;
	my $date = shift;
	system("/usr/bin/logger","-p","local6.notice","-t","$prefix-$user","$message","$level","$date");	
}

sub user_log_login{
	my $date = `date "+%Y-%m-%d"`;
	my @cur_user=&getCurUser();
	my $user=$cur_user[0];
	my @user_info = read_users_file();
	my $level;
	foreach my $user1(@user_info)
		{    
			my @user_temp = split(",",$user1);
			if($user eq @user_temp[0]){
				$level = "=level: ".$user_temp[4];
			}
		}
	my $IP = $ENV{'REMOTE_ADDR'};
	my $message = $IP."--";
	foreach (@_){
		$message .= $_.",";
	}
	$message =~ s/,$//;
	&logger_with_prefix('userRecord',$user,$message,$level,$date);
	# system("/usr/bin/logger","-p","local6.notice","-t","userLog-$user","$message","$level","$date");
}

sub user_log{
	my $date = `date "+%Y-%m-%d"`;
	my @cur_user=&getCurUser();
	my $user=$cur_user[0];
	my @user_info = read_users_file();
	my $level;
	foreach my $user1(@user_info)
		{    
			my @user_temp = split(",",$user1);
			if($user eq @user_temp[0]){
				$level = "=level: ".$user_temp[4];
			}
		}
	my $IP = $ENV{'REMOTE_ADDR'};
	my $message = $IP."--";
	foreach (@_){
		$message .= $_.",";
	}
	$message =~ s/,$//;
	&logger_with_prefix('userLog',$user,$message,$level,$date);
	# system("/usr/bin/logger","-p","local6.notice","-t","userLog-$user","$message","$level","$date");
}
sub write_log($$$) {
    my ($cur_page,$operation,$operation_status,$rule_or_congfig )= @_ ; 
    # print ($cur_page,$operation,$operation_status,$rule_or_congfig ); 
    $operation_status = ($operation_status eq '0' ? Encode::decode_utf8("成功") : Encode::decode_utf8("失败")) ; 
    $rule_or_congfig = ($rule_or_congfig eq '0' ? Encode::decode_utf8("规则") : Encode::decode_utf8("配置")) ; 
    if ($operation eq 'add') {
        $operation = Encode::decode_utf8("新增") ;
    }elsif ($operation eq 'edit'){
        $operation = Encode::decode_utf8("更新") ;
    }elsif ($operation eq 'del'){
        $operation = Encode::decode_utf8("删除") ;
    }elsif ($operation eq 'apply'){
        $operation = Encode::decode_utf8("应用") ;
    }elsif ($operation eq 'enable'){
        $operation = Encode::decode_utf8("启用") ;
    }elsif ($operation eq 'disable'){
        $operation = Encode::decode_utf8("禁用") ;
    }elsif ($operation eq 'move'){
        $operation = Encode::decode_utf8("移动") ;
    }else{
    	$operation = "error" ;
    }

    my $log_mesg = '['.Encode::decode_utf8($cur_page).'] '.$operation.$rule_or_congfig.' '.$operation_status;
    if ($operation eq 'error') {
    	$log_mesg = "操作 [".$cur_page."]时发生了未知错误".' '."未知错误";
    }
    $log_mesg = Encode::decode_utf8($log_mesg);
    # print $log_mesg;
    &user_log($log_mesg);
}

# Return all brand specific settings
sub get_brand_settings {
	my $hash = shift;
	
	if(-f "/etc/custom.conf") {
		&readhash("/etc/custom.conf", $hash);
		$branded = true;
	}
}

# Is the firewall branded or not.
sub is_branded() {
	return $branded;
}

sub get_company() {
	&get_brand_settings(\%brandsettings);
	
	chomp($brandsettings{'COMPANY'});
	return (is_branded()) ? $brandsettings{'COMPANY'} : "CapSheaf";
}

sub get_brand() {
	&get_brand_settings(\%brandsettings);
	
	chomp($brandsettings{'BRAND'});
	return (is_branded()) ? $brandsettings{'BRAND'} : "CapSheaf";
}

sub get_product() {
	&get_brand_settings(\%brandsettings);
	
	chomp($brandsettings{'PRODUCT'});
	return (is_branded()) ? $brandsettings{'PRODUCT'} : "UTM";
	
}


# 定义变量；
my $webroot = '/home/httpd/cgi-bin/';
if ($ENV{'DOCUMENT_ROOT'}) {
	$webroot = $ENV{'DOCUMENT_ROOT'};
}

my $menuCache = '/var/cache/menu/';
my $menuRegistry = '/home/httpd/menus/';

$version = get_version();
$brand = get_brand();
$product = get_product();
# Is the firewall branded?
$branded = false;
$revision = 'final';
$swroot = '/var/efw';
$pagecolour = '#ffffff';
#$tablecolour = '#a0a0a0';
$tablecolour = '#FFFFFF';
$bigboxcolour = '#F6F4F4';
$boxcolour = '#EAE9EE';
$bordercolour = '#000000';
$table1colour = '#E0E0E0';
$table2colour = '#F0F0F0';
$colourred = '#993333';
$colourorange = '#FF9933';
$colouryellow = '#FFFF00';
$colourgreen = '#339933';
$colourblue = '#333399';
$colourfw = '#000000';
$colourvpn = '#990099';
$colourerr = '#FF0000';
$viewsize = 150;
$errormessage = '';
$notemessage = '';
$warnmessage = '';
my %menuhash = ();
my $menu = \%menuhash;
my %flavourmenushash = ();
my $flavourmenus = \%flavourmenushash;
my $useFlavour = 'main';
%settings = ();
%hostsettings = ();
%ethsettings = ();
@URI = ();
$supported=0;

$HOTSPOT_ENABLED = '/var/efw/hotspot/enabled';

$ALLOW_PNG = '/images/stock_ok.png';
$DENY_PNG = '/images/stock_stop.png';
$ADD_PNG = '/images/add.png';
$UP_PNG = '/images/stock_up-16.png';
$DOWN_PNG = '/images/stock_down-16.png';
$ENABLED_PNG = '/images/on.png';
$DISABLED_PNG = '/images/off.png';
$EDIT_PNG = '/images/edit.png';
$DELETE_PNG = '/images/delete.png';
$OPTIONAL_PNG = '/images/blob.png';
$CLEAR_PNG = '/images/clear.gif';

my %cookies = fetch CGI::Cookie;

### Initialize environment
if (-e "${swroot}/host/settings") {
	&readhash("${swroot}/host/settings", \%hostsettings);
}
&readhash("${swroot}/main/settings", \%settings);
&readhash("${swroot}/ethernet/settings", \%ethsettings);

# make backwards compatible
$settings{'HOSTNAME'} = $hostsettings{'HOSTNAME'};
$settings{'DOMAINNAME'} = $hostsettings{'DOMAINNAME'};

$language = $settings{'LANGUAGE'};
$hostname = $settings{'HOSTNAME'};
$hostnameintitle = 0;

### Initialize language
if ($language =~ /^(\w+)$/) {$language = $1;}
gettext_init($language, "efw");
gettext_init($language, "efw.enterprise");
gettext_init($language, "efw.vendor");

@zones = qw 'GREEN ORANGE BLUE RED';
%zonecolors = (
		RED => $colourred,
		BLUE => $colourblue,
		GREEN => $colourgreen,
		ORANGE => $colourorange,
		LOCAL => $colourfw
);
%strings_zone = (
	'GREEN' => _('GREEN'),
	'BLUE' => _('BLUE'),
	'ORANGE' => _('ORANGE'),
	'RED' => _('RED'),
	'LOCAL' => _('LOCAL'),
);

@bypassuris = qw '/welcome /hotspot /template.cgi';
#generalRedirect();

sub generalRedirect() {
	### Make sure this is an SSL request
	return if (! $ENV{'SERVER_ADDR'});
	return if ($ENV{'HTTPS'} eq 'on');
	foreach my $uri (@bypassuris) {
	return if ($ENV{'SCRIPT_NAME'} =~ $uri);
	}
	print "Status: 302 Moved\r\n";
	print "Location: https://$ENV{'SERVER_ADDR'}:10443/$ENV{'PATH_INFO'}\r\n\r\n";
	exit 0;
}


sub expireMenuCache() {
	my $cachefile = "${menuCache}/${useFlavour}.json";
	if (-e $cachefile) {
		unlink($cachefile);
	}
}

sub cacheMenu($$) {
	my $menu = shift;
	my $flavour = shift;
	my $cachefile = "${menuCache}/${flavour}.json";
	if (! open(J, ">$cachefile")) { #读取指定路径下的文件，成功返回非0，失败返回0；

	warn("Could not cache menu to '$cachefile' due to $!");
	return;
	}
	my $jsonobj = jsonifyMenu($menu);
	print J $jsonobj;
	close(J);
}

sub loadMenuFromCache($) {
	my $flavour = shift;
	my $cachefile = "${menuCache}/${flavour}.json";

	open(J, $cachefile);

	# $cachefile content *is* utf-8 encoded, don't ask why json
	# needs it to load as latin1. I don't know.
	# It's however necessary to use the latin1 encoder
	# otherwise it will be encoded as utf-8 twice.
	my $jsonobj = JSON::XS->new->latin1->decode (join('', <J>));
	close J;
	# print "cachefile".Dumper($cachefile)."\n";
	# print "jsonobj".Dumper($jsonobj)."\n";
	return $jsonobj;
}

sub isMenuCacheExpired($) {
	my $flavour = shift;
	my $cachefile = "${menuCache}/${flavour}.json";

	if (! -e $cachefile) {
		return 1;
	}
	my $dirtime = (stat("$menuRegistry/$flavour"))[9]; #获取菜单最近一次的修改时间；
	my $filetime = (stat($cachefile))[9];#获取缓存菜单的最近一次修改时间；
	if ($filetime < $dirtime) {
		return 1;
	}

	return 0;
}

sub registerMenus($) {
	my $flavour = shift;
	my %emptyhash;
	$menu = \%emptyhash;
	foreach my $regfile (glob("$menuRegistry/$flavour/menu-*.pl")) {
		require $regfile;
	}
	disableInexistentMenus($menu);
	cacheMenu($menu, $flavour);

	return $menu;
}

sub genFlavourMenus() {
	$flavourmenus->{$useFlavour} = $menu;

	foreach my $flavour (glob("$menuRegistry/*")) {
		$flavour =~ s#^.*/([^/]+)$#\1#;

		if (isMenuCacheExpired($flavour)) {
			$menu = registerMenus($flavour);
		} else {
			$menu = loadMenuFromCache($flavour);

		}

		$flavourmenus->{$flavour} = $menu;
	}
	$menu = $flavourmenus->{$useFlavour};
   

}

sub setFlavour($) {
	my $flavour = shift;
	$useFlavour = $flavour;
}

sub getHTTPRedirectHost() {
	my $httphost = $ENV{'HTTP_HOST'};

	if ($ENV{'HTTPS'} ne 'on') {
		my ($host, $port) = split(/:/, $httphost);
		if ($port =~ /^$/) {
			$port = '10443';
		}

		$httphost = "$host:$port";
	}
	return $httphost;
}

### Check whether this system is a HA slave or not - if so redirect to an info-page
sub checkForHASlave() {
	return if ( ! -e "${swroot}/ha/settings");
	&readhash("${swroot}/ha/settings",\%hasettings);
	return if ($hasettings{'HA_ENABLED'} ne 'on');
	return if ($hasettings{'HA_STATE'} ne 'slave');
	
	setFlavour('haslave');
	return if ($ENV{'SCRIPT_NAME'} eq '/cgi-bin/ha_slave.cgi');
	if (! gettitle($flavourmenus->{$useFlavour})) {
	my $host = getHTTPRedirectHost();
	print "Location: https://$host/cgi-bin/ha_slave.cgi\r\n\r\n";
	}
}

sub orange_used () {
	if ($ethsettings{'CONFIG_TYPE'} =~ /^[1357]$/) {
	return 1;
	}
	return 0;
}

sub blue_used () {
	if ($ethsettings{'CONFIG_TYPE'} =~ /^[4567]$/) {
	return 1;
	}
	return 0;
}

sub is_modem {
	if ($ethsettings{'CONFIG_TYPE'} =~ /^[0145]$/) {
	return 1;
	}
	return 0;
}


### Initialize menu
#
# New dynamic menu structure:
#
# Right now there is a 'main' menu, which is backwards compatible and
# allows legacy registration in header.pl and legacy registration
# through hooks in /home/httpd/cgi-bin/menu-*.pl using the
# register_menuitem() registration function.
#
# New style menu item registration allows for more different main menus
# which allow to be selected by setting the global $useFlavour variable.
#
# Menu items can be registered by creating a hook file in 
# /home/httpd/menus/$flavour/menu-*.pl which then use the registering
# function register_menuitem()
#
# The main menu is called 'main'. Right now there is one more menu
# 'haslave'. A 'hotspot' menu may follow.
#
##
sub genmenu {
	if ($useFlavour ne 'main') {
		$menu = $flavourmenus->{$useFlavour};
	}
	return $menu;
}

sub calcURI() {
	if ($ENV{'SCRIPT_NAME'} =~ '/template.cgi') {
		my $cgi = CGI->new ();
		%vars = $cgi->Vars();
		$URI[0] = "/cgi-bin/".$vars{'SCRIPT_NAME'};
		$URI[1] = $vars{'PARAMETER'};
		return;
	}

	@URI=split ('\?',  $ENV{'REQUEST_URI'} );
}


#author:zhouyuan
#date:2011-07-22
#function:读出用户文件的所有为列表形式
sub read_users_file() {
	my @lines;
	open (FILE, "/var/efw/userinfo/userslist");
	foreach my $line (<FILE>) {
		chomp($line);
		$line =~ s/[\r\n]//g;
		push(@lines, $line);
	}
	close (FILE);
	return @lines;
}


#author:zhouyuan
#date:2011-07-22
#function:修改特定用户的特定列
sub modify_user_list($$$)
{
	my $username = shift;
	my $colum = shift;
	my $value = shift;
	my $j=0;
	my @userlines = read_users_file();
	foreach my $myline (@userlines)
	{
		@arrline = split(/,/,$myline);
		if($arrline[0] eq $username)
		{
			$arrline[$columdic{$colum}] = $value;
			my $i = 0;
			my $length = @arrline;
			$userlines[$j] = "";
			foreach my $line(@arrline)
			{
				if($i<$length-1)
				{
					$userlines[$j]  .= $line.',';
				}else{
					$userlines[$j]  .= $line;
				}
				$i++;
			}
		}
		$j++;
	}
	write_users_file(\@userlines);
}


#author:zhouyuan
#date:2011-07-22
#function:用户文件的列信息字典
%columdic = (
		'account'   => 0,
		'password'  => 1,
		'describe'  => 2,
		'mail'      => 3,
		'level'     => 4,
		'is_lock'   => 5,
		'timestamp' => 6
	);


#author:zhouyuan
#date:2011-07-22
#function: 写入修改后的用户信息到用户文件
sub write_users_file($)
{
	my $para = shift;
	my @userlines = @$para;
	my $filename = '/var/efw/userinfo/userslist';
	open (FILE, ">$filename");
	foreach my $myline ( @userlines )
	{
		print FILE "$myline\n";
	}
	close (FILE);
}

sub setCache($)
{
		my $account = shift;

		my %user_settings;
		readhash( "/var/efw/userinfo/user_config", \%user_settings );
		$time = ($user_settings{'TIMEOUT'} + 1) * 60;
		$timeout = gmtime(time()+$time)." GMT";
		my $cookiepath = "/";
		my $cache = &get_cookie_user('code');		
		print "Set-Cookie: ee11cbb19052e40b07aac0ca060c23ee=$cache; expires=$timeout; path=$cookiepath;\r\n";
}
sub rewrite_cookie(){
	my @users = getCurUser();
	if($users[0]){
		setCache($users[0]);
	}
}
sub get_cookie_user($) {
	my $need_data = shift;
	my %cookie = fetch CGI::Cookie;
	my @user = split(/;/,$cookie{'ee11cbb19052e40b07aac0ca060c23ee'});
		@user = split(/=/,$user[0]);

	my @userInfo = &read_conf_file("/var/efw/userinfo/userslist");
	my @userName;
	@user = split(/_/,$user[1]);
	
	$user[0] = URI::Escape::uri_unescape($user[0]);
	$user[0] =~ s/\ /\+/g;

	# $user[0] =~ s/\%20/\+/g;
	# $user[0] =~ s/\%2F/\//g;
	# $user[0] =~ s/\%3D/\=/g;
	if ($need_data eq 'code') {
		return $user[0];
	}
	my $key = &get_aes_key();
	$cipher = Crypt::CBC->new(
            -key    => $key,
            -cipher => "Crypt::OpenSSL::AES"
    );
    $decrypted = decode_base64($user[0]); 
	try{
		$decrypted = $cipher->decrypt($decrypted);
	}catch{
		$decrypted = '';
	};
	if ($need_data eq 'key') {
		return $decrypted;
	}
	my @temp = split(/\_/,$decrypted);
	return $temp[4];
}
###写cookie的函数by 张征 2012-1-6 END
###新增cookie用户检测，如果不属于注册用户则不允许进入系统by 张征 2012-1-6
sub check_cookie_user(){
	my $filename = '/var/efw/userinfo/userslist';
	my @cur_user=getCurUser();
	my $flag = 0;

	open (FILE, "$filename");
	foreach my $line(<FILE>){

		if($line =~ /^$cur_user[0],/){
			$flag = 1;
		}
	}
	close(FILE);
	if($flag eq "0" && $ENV{'SCRIPT_NAME'}!~/index/ ){

		#my $url = "\"https://".$ENV{'SERVER_ADDR'}.":10443/\"";
		print "<script>var des='https://'+window.parent.parent.location.host+'/index.cgi';window.parent.parent.location.replace(des); </script>";
		exit;
	}
	#else{
	#   #my $url = "\"https://".$ENV{'SERVER_ADDR'}.":10443/cgi-bin/footer.cgi\"";
	#   print "<script>var des='https://'+window.parent.parent.location.host+'/cgi-bin/footer.cgi';window.parent.parent.document.getElementById('bottomFrame').src=des</script>";
	#}
}
###新增cookie用户检测，如果不属于注册用户则不允许进入系统by 张征 2012-1-6 END

# ###根据现有菜单初始化cgi权限hash
# sub init_hash_cgirole(){
#     foreach my $k1( sort keys %$menu ){
#         my $menu_name = (split(/\./,$k1))[1];
#         my %menu_number = read_menu_settings();
#         #if(exists $menu_number{$menu_name}){
#             my $subMenu = $menu->{$k1}->{'subMenu'};
#             foreach my $k2 (sort keys %$subMenu) {
#                 my $sub_subMenu = $subMenu->{$k2}->{'subMenu'};
#                 foreach my $k3 (sort keys %$sub_subMenu ) {
#                     my $sub_subItem = $sub_subMenu->{$k3};
#                     my $script_name = $sub_subItem->{'uri'};
#                     my $sub_level = $sub_subItem->{'level'};
#                     if(($sub_subItem->{'enabled'} eq '0' && !exists $sub_subItem->{'vars'}) || !exists $menu_number{$menu_name}){
#                         $sub_level = '7';
#                     }
#                     if(exists $sub_subItem->{'level'}){
#                         $authorized_url{$script_name} = $sub_level;
#                     }
#                 }
#             }
#         #}
#     }
# }

###新增用户权限判断by Liu Julong 2015-07-23
my $AUTH_NOTFOUND = 2;
my $AUTH_FORBIDDEN = 0;
my $AUTH_PROMISE = 1;
my $AUTH_WHITE_LIST = 3;
sub judge_authrize($$){ 
	# 查找权限hash中对应该uri的角色值，类似'0_1_3'
	# 然后判断当前登陆的用户的身份是否具备访问此uri对应的那个页面的权限！！
	my $uri = shift;
	my $user = shift;
	my $cur_user_type = &get_user_type($user);

	my $level = "0";
	
	if(exists $authorized_url{$uri}){
		$level = $authorized_url{$uri};
	}else{
		# 白名单判断
		if (exists $authorized_white_list{$uri}) {
			return $AUTH_WHITE_LIST;
		}else{
			return $AUTH_NOTFOUND;
		}
	}
	
	if($level eq $authorized_to_all || $level eq $authorized_to_admin || 
		$level eq $authorized_to_safeauth || $level eq $authorized_to_users_admin || 
		$level eq $authorized_to_logerauth){
		#2016-11-18
		my @levels = split(/_/,$level);
		if($cur_user_type eq '2'){
			if($user eq 'admin' && (($level =~ /0/ && $level =~ /2/) || $level =~ /^2$/) ){
				 return $AUTH_PROMISE;
			}
			if($user eq 'safeauth' && (($level =~ /1/ && $level =~ /2/) || $level =~ /^2$/)){
				return $AUTH_PROMISE;
			}
			if($user eq 'logerauth' && (($level =~ /3/ && $level =~ /2/) || $level =~ /^2$/)){
				return $AUTH_PROMISE;
			}
			
		}
		else{
			foreach my $lev(@levels){
				if($cur_user_type eq $lev){
					return $AUTH_PROMISE;   
				}
			}
		}
		return $AUTH_FORBIDDEN;
	}else{
		return $AUTH_NOTFOUND;
	}
}

# sub getENV(){
#   my $tmp = '';
#   while(my ($key,$value)=each %)
#   {
#       $tmp=$tmp." | $key: $value";
#   }
#   return $tmp;
# }

my $fpath_404page = '/home/httpd/html/error_pages/404.html';
sub showhttpheaders
{
	my $content_type = shift;
	calcURI();
	genFlavourMenus();
	# &init_hash_cgirole();
	#checkForHASlave();
	
	
	###modified by Liu Julong 2015-07-23 14:52
	my @cur_user = &getCurUser();
	#pj：
	# my $auth =1;
	my $auth = &judge_authrize( $ENV{'SCRIPT_NAME'}, $cur_user[0] );
	my $timeout = &judge_timeout();
	print "Pragma: no-cache\n";
	print "Cache-control: no-cache\n";
	print "Connection: close\n";
	if ( $content_type eq "json" ) {
		print "Content-type: application/json; charset=utf-8\n";
	} else {
		print "Content-type: text/html; charset=utf-8\n";
	}
   
	if ($auth == $AUTH_PROMISE) {
		if ($timeout eq 0){	
			rewrite_cookie();
			print "\n";
		}else{	
		        my $httphost = getHTTPRedirectHost();
		        print "Status: 200\r\n";
			print "CapsheafAuth: offline\r\n";
			print "\r\n";
		        print "<script>var hosts = document.location.host;var temp = hosts.split(':');var ip = temp[0];document.cookie='ee11cbb19052e40b07aac0ca060c23ee=;path=/';window.top.location.href='https://${httphost}/index.cgi';</script>";
		        exit;
		}
	} else {
		
		print "Status: 404\n";
		print "\n";
		print `cat $fpath_404page`;
		exit;
	}
}

sub judge_timeout() {
	my $time = 30;
	my %time = ();
	readhash("/var/efw/userinfo/user_config",\%time);
	$time = $time{"TIMEOUT"}+0;
	my %time_out_hash = ();
	my $path = "/var/efw/userinfo/timeout";
	readhash($path,\%time_out_hash);
	my @cur_user=getCurUser();
	my $timeout_status = 0;
	my $key = &get_cookie_user('key');
	if ($time_out_hash{$key}) {
		my $last_time = $time_out_hash{$key};
		my $user=$cur_user[0];
		my $cur_time = `date +%s`;
		chomp $cur_time;
		my $outtime=$cur_time - $last_time - $time*60 - 33;
		if ($outtime > 0) {
			$timeout_status = -1 ;
		}
	}else{
		$timeout_status = -1 ;
	}
	return $timeout_status ;
}


sub export_judge_auth() {
	# 判断导出权限 2015.09.07 #
	my @cur_user = &getCurUser();
	my $auth = &judge_authrize( $ENV{'SCRIPT_NAME'}, $cur_user[0] );

	if ( $auth != $AUTH_PROMISE ) {
		print "Pragma: no-cache\n";
		print "Cache-control: no-cache\n";
		print "Connection: close\n";
		print "Content-type: text/html; charset=utf-8\n";
		print "Status:404\n";
		print "\n";
		print `cat $fpath_404page`;
		exit;
	}
}

sub showhttpheaders_without_rewrite
{
	calcURI();
	genFlavourMenus();
	#checkForHASlave();
	print "Pragma: no-cache\n";
	print "Cache-control: no-cache\n";
	print "Connection: close\n";
	print "Content-type: text/html\n\n";
}

sub is_menu_visible($) {
	my $link = shift;
	$link =~ s#\?.*$##;
	if ( $link =~ /^http:\/\// ) {
		return 1;
	}
	if ($link !~ /\.cgi$/) {
	return 1;
	}
	return (-e $webroot."/../$link");
}


sub getlink($) {
	my $root = shift;
	if (! $root->{'enabled'}) {
		
		return '';
	}
	if ($root->{'uri'} !~ /^$/) {
		my $vars = '';
		if ($root->{'vars'} !~ /^$/) {
		 $vars = '?'. $root->{'vars'};
		}

		if (! is_menu_visible($root->{'uri'})) {
			
			return '';
		}
		

		return $root->{'uri'}.$vars;
	}
	my $submenus = $root->{'subMenu'};
	if (! $submenus) {
		return '';
	}
	# print "891".Dumper($submenus);
	foreach my $item (sort keys %$submenus) {
		my $link = getlink($submenus->{$item});
		if ($link ne '') {
		return $link;
		}

	}
	return '';
}


sub compare_url($) {
	my $conf = shift;

	my $uri = $conf->{'uri'};
	my $vars = $conf->{'vars'};
	my $novars = $conf->{'novars'};

	if ($uri eq '') {
	return 0;
	}
	if ($uri ne $URI[0]) {
	return 0;
	}
	if ($novars) {
	if ($URI[1] !~ /^$/) {
		return 0;
	}
	}
	if (! $vars) {
	return 1;
	}
	return ($URI[1] =~ /$vars.*/);
}


sub gettitle($) {
	my $root = shift;

	if (! $root) {
	return '';
	}
	foreach my $item (sort keys %$root) {
	my $val = $root->{$item};
	if (compare_url($val)) {
		$val->{'selected'} = 1;
		if ($val->{'title'} !~ /^$/) {
		return $val->{'title'};
		}
		return 'EMPTY TITLE';
	}

	my $title = gettitle($val->{'subMenu'});
	if ($title ne '') {
		$val->{'selected'} = 1;
		return $title;
	}
	}
	return '';
}

sub disableInexistentMenus($) {
	my $root = shift;
	if (! $root) {
	return;
	}
	foreach my $item (sort keys %$root) {
	my $node = $root->{$item};
	if ($node->{'subMenu'}) {
		disableInexistentMenus($node->{'subMenu'});
	}
	if (! $node->{'enabled'}) {
		next;
	}
	if (! $node->{'uri'}) {
		next;
	}
	if (! is_menu_visible($node->{'uri'})) {
		$node->{'enabled'} = 0;
		next;
	}
	}
}

sub showmenu() {
	printf <<EOF
  <div id="menu-top">
	<ul>
EOF
;
	foreach my $k1 ( sort keys %$menu ) {
	if (! $menu->{$k1}{'enabled'}) {
		next;
	}

	my $link = getlink($menu->{$k1});
	if ($link eq '') {
		next;
	}
	if (! is_menu_visible($link)) {
		next;
	}
	if ($menu->{$k1}->{'selected'}) {
		print '<li class="selected">';
	} else {
		print '<li>';
	}

	printf <<EOF
	<div class="rcorner">
	  <a href="$link">$menu->{$k1}{'caption'}</a>
	</div>
  </li>
EOF
;
	}

	printf <<EOF
	</ul>
  </div>
EOF
;    
}

sub getselected($) {
	my $root = shift;
	if (!$root) {
		return 0;
	}

	foreach my $item (%$root) {
		if ($root->{$item}{'selected'}) {
			return $root->{$item};
		}
	}
}

# PT
sub dynamicDisable($$){
	my $username = shift;
	my %menus = shift;
	if(! exists %authorized_url_except->{$username}){

		return;
	}
	my @arr = %authorized_url_except->{$username};
	foreach my $item(%menus){
		if($item{'uri'} ~~ @arr){
			$item{'enabled'} == 0;
		}
	}
}


sub showsubsection($$) {
	my $root = shift;
	my $id = shift;
	if ($id eq '') {
	$id = 'menu-left';
	}

	if (! $root) {
		print '<div style="width: 85px;"></div>';
	return;
	}
	my $selected = getselected($root);
	if (! $selected) {
		print '<div style="width: 85px;"></div>';
	return;
	}
	my $submenus = $selected->{'subMenu'};
	if (! $submenus) {
		print '<div style="width: 85px;"></div>';
	return;
	}

	printf <<EOF
<ul  class="tab-div">
EOF
;

#hack disabled
	my @username = &getCurUser();
	&dynamicDisable(@username[0], %$submenus);

	foreach my $item (sort keys %$submenus) {

	my $hash = $submenus->{$item};
	

	if (! $hash->{'enabled'}) {
		next;
	}

	if( $hash->{'uri'} eq '/cgi-bin/pagemanagement.cgi' and $username[0] ne 'safeauth'){
		next;
	}

	my $link = getlink($hash);
	if ($link eq '') {
		next;
	}
	if (! is_menu_visible($link)) {
		next;
	}
	my $caption = $hash->{'caption'};
	if ($hash->{'selected'}) {
		print '<li class="active" >';
		print "<a href=\"$link\">$caption</a></li>";
	} else {
		print '<li class="not_active">';
		print "<a href=\"$link\">$caption</a></li>";
	}

	#printf <<EOF
#
#EOF
#;
	}

	printf <<EOF
	</ul>
EOF
;    

}


sub showsubsubsection($) {
	my $root = shift;
	if (!$root) {
	return;
	}
	my $selected = getselected($root);
	if (! $selected) {
	return
	}
	if (! $selected->{'subMenu'}) {
	return
	}

	showsubsection($selected->{'subMenu'}, 'menu-subtop');
}


sub get_helpuri_recursive($) {
	my $root = shift;

	if (! $root) {
	return '';
	}
	foreach my $item (sort keys %$root) {
	my $val = $root->{$item};
	if (compare_url($val)) {
		$val->{'selected'} = 1;
		if ($val->{'helpuri'} !~ /^$/) {
		return $val->{'helpuri'};
		}
		return '';
	}

	my $helpuri = get_helpuri_recursive($val->{'subMenu'});
	if ($helpuri ne '') {
		$val->{'selected'} = 1;
		return $helpuri;
	}
	}
	return '';
}
sub get_helpuri($) {
	my $root = shift;
	
	# Retrieve brand settings
	&get_brand_settings(\%brandsettings);
	
	my $uri = get_helpuri_recursive($root);
	# Retrieve docs URL from custom.conf for custom branding
	my $rooturi = 'http://docs.endian.com/2.2/en/';
	if($brandsettings{'DOCS_URL'} ne '') {
		$rooturi = $brandsettings{'DOCS_URL'} . '/';
		# replace efw. for branding
		$uri =~ s/efw.//g
	}
	
	return $uri if ($uri =~ /^http:/);
	return $uri if ($uri =~ /^\//);
	return $rooturi.$uri;
}

sub jsonifyMenu($) {
	my $menu = shift;
	# $menu *is* utf-8 encoded, don't ask why json
	# needs it as latin1. I don't know.
	# It's however necessary to use the latin1 encoder
	# otherwise it will be encoded as utf-8 twice.
	return JSON::XS->new->latin1->encode($menu);
}

sub menu_to_json {
	print jsonifyMenu($menu);
}
sub get_aes_key{
	return `cat /var/efw/webkey/uuid[0-7] | tr -d '\n'`
}

sub getCurUser()
{
	my %cookie = fetch CGI::Cookie;
	my @user = split(/;/,$cookie{'ee11cbb19052e40b07aac0ca060c23ee'});
		@user = split(/=/,$user[0]);

	my @userInfo = &read_conf_file("/var/efw/userinfo/userslist");
	my @userName;
	if($user[0] eq "ee11cbb19052e40b07aac0ca060c23ee")
	{
		@user = split(/_/,$user[1]);
		$user[0] = URI::Escape::uri_unescape($user[0]);
		$user[0] =~ s/\ /\+/g;
		# $user[0] =~ s/\%20/\+/g;
		# $user[0] =~ s/\%2F/\//g;
		# $user[0] =~ s/\%3D/\=/g;
		my $key = &get_aes_key();
		$cipher = Crypt::CBC->new(
                -key    => $key,
                -cipher => "Crypt::OpenSSL::AES"
        );
        $decrypted = decode_base64($user[0]); 
		try{
			$decrypted = $cipher->decrypt($decrypted);
		}catch{
			$decrypted = '';
		};
		my @temp = split(/\_/,$decrypted);
		foreach (@userInfo) {
			my @line = split(/,/,$_);
			if($line[0] eq $temp[4]) {

		
				push(@userName,$line[0]);
			}
			
		}
	}
	else
	{
		@userName = ();
	}
	my $data = join("," ,@userName);
	my $data .= "-" . $user[0] . '-' . $userInfo[4];
	
	return @userName;
}


#author:zhouyuan
#date:2011-07-19
#function:检查cookie是否包含用户信息
sub checkforLoginSD()
{
	my @user = &getCurUser();
	if($ENV{'SCRIPT_NAME'} eq '/cgi-bin/logs_live.cgi' || $ENV{'SCRIPT_NAME'} eq '/cgi-bin/ips_threads.cgi')
	{
		if($user[0] eq '')
		{
			 #my $url = "\"https://".$ENV{'SERVER_ADDR'}.":10443/\"";
			 print "<script>var des='https://'+window.parent.parent.location.host+'/index.cgi';window.parent.parent.location.replace(des); </script>";
		}

	}
	else{
			if ($ENV{'SCRIPT_NAME'} ne '/index.cgi') {
			if ($user[0] eq '') {
					#my $url = "\"https://".$ENV{'SERVER_ADDR'}.":10443/\"";
					print "<script>var des='https://'+window.parent.parent.location.host+'/index.cgi';window.parent.parent.location.replace(des); </script>";
			}
			
		}
	}
	
}
#sandfoam




my $gui_set="";
sub openpage {
	my $title = shift;
	my $boh = shift;
	my $extrahead = shift;
	&readhash("${swroot}/main/settings", \%settings);
	
	my $systemconfig = "${swroot}/systemconfig/settings";
	my %system_settings;
	my $system_title;
	if ( -f $systemconfig ) {
	   &readhash( "$systemconfig", \%system_settings );
	}
	$system_title = $system_settings{'SYSTEM_TITLE'}; #读取系统的名称；
	
	&write_login_time();
	if(!($nomenu == 1)) {
		
		&genmenu();
	}
	my $h2 = gettitle($menu);
	my $helpuri = get_helpuri($menu);

	$title = $system_title." -". $title;
	$gui_set = $settings{'LANGUAGE'};
	if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
		$title = $system_title." -". $title;
	}

	#####周圆 2011-09-21用于添加头部帮助悬浮层显示消失功能######
	my $help_file = "/var/efw/help/setting";
	&readhash($help_file,\%help_hash);
	############################################################
	
	
	printf <<END
<!DOCTYPE html 
	 PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
		<title>$title</title>
		<link rel="shortcut icon" href="/images/shortcut.ico" />
		<style type="text/css">\@import url(/include/main.css);</style>
		<style type="text/css">\@import url(/include/style.css);</style>
		<style type="text/css">\@import url(/include/menu.css);</style>
		<style type="text/css">\@import url(/include/content.css);</style>
		<style type="text/css">\@import url(/include/folding.css);</style>
		<style type="text/css">\@import url(/include/service-notifications.css);</style>
		<script language="JavaScript" type="text/javascript" src="/include/overlib_mini.js"></script>
		<script language="javascript" type="text/javascript" src="/include/jquery.js"></script>
		<script language="javascript" type="text/javascript" src="/include/jquery.ifixpng.js"></script>
		<script language="javascript" type="text/javascript" src="/include/jquery.selectboxes.js"></script>
		<script language="javascript" type="text/javascript" src="/include/folding.js"></script>
		<script language="javascript" type="text/javascript" src="/include/datepicker.js"></script>
		<script language="javascript" type="text/javascript" src="/include/form.js"></script>
		<script language="javascript" type="text/javascript" src="/include/right_content.js"></script>
		<script language="javascript" type="text/javascript" src="/include/for_iE6_png.js"></script>
		<script language="javascript" type="text/javascript" src="/include/ChinArk_form.js"></script>
		<script language="javascript" type="text/javascript" src="/include/manage.js"></script>
		<script language="javascript" type="text/javascript" src="/include/formSubmitIllegalDetection.js"></script>
END
;
		if($help_hash{"HELP_ENABLED"} eq "on")
		{
			printf <<EOF
			<script type="text/javascript" src="/include/help.js"></script>
EOF
;
		}
printf <<END
		<!-- Include Service Notification API -->
		<script language="javascript" type="text/javascript" src="/include/servicesubscriber.js"></script>
		
		$extrahead
	
		<script type="text/javascript">
			overlib_pagedefaults(WIDTH,300,FGCOLOR,'#ffffcc',BGCOLOR,'#666666');
			function swapVisibility(id) {
				el = document.getElementById(id);
				if(el.style.display != 'block') {
					el.style.display = 'block'
				}
				else {
					el.style.display = 'none'
				}
			}
		</script>
		<script type="text/javascript" src="/include/accordion.js"></script>
END
;
	if($ENV{'SCRIPT_NAME'} eq '/cgi-bin/main.cgi' && -e '/home/httpd/html/include/uplink.js') {
		printf <<END
			<script language="javascript" type="text/javascript" src="/include/uplink.js"></script>
			<link rel="stylesheet" type="text/css" media="screen" title="Uplinks Status" href="/include/uplinks-status.css" />
END
;
	}
	if($ENV{'SCRIPT_NAME'} eq '/cgi-bin/uplinkeditor.cgi') {
		printf <<END
			<script language="javascript" type="text/javascript" src="/include/uplinkeditor.js"></script>
END
;
	}
	if ($ENV{'SCRIPT_NAME'} eq '/cgi-bin/updates.cgi' && -e '/home/httpd/html/include/ajax.js'  && -e '/home/httpd/cgi-bin/updates-ajax.cgi'
		&& -e '/home/httpd/html/include/updates.js' && -e'/home/httpd/html/include/updates.css') {
	  printf <<END

		<style type="text/css">\@import url(/include/updates.css);</style>
		<script type="text/javascript" language="JavaScript" src="/include/ajax.js"></script>
		<script type="text/javascript" language="JavaScript" src="/include/updates.js"></script>
	</head>
	<body>
	<div class="right-waiting"><div class="right-pic"><div class="lds-css ng-scope"><div class="lds-spinner" style="100%;height:100%"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div></div></div></div>
END
;
	} else {
	  printf <<END
	  </head>
	  <body>
	<div class="right-waiting"><div class="right-pic"><div class="lds-css ng-scope"><div class="lds-spinner" style="100%;height:100%"><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div></div></div></div>

END
;
	}
	#&showmenu();
	&showsubsubsection($menu);
	print "<div id='elvis_right_content'  class='right-content'>";
#    eval {
#   require 'endian-network.pl';
#   $supported = check_support();
#   warn_unsupported($supported);
#    };
if ( -e '/var/tmp/oldkernel' && $ENV{'SCRIPT_NAME'} eq '/cgi-bin/main.cgi') {
	printf <<END                                                                                                                                                                
	<h3 class="warning">%s</h3>                                                                                                                                                 
	<table class="list"><tr><td align="center"><img src="/images/dialog-warning.png"/></td><td align="left">%s</td></tr></table>                                                
	<br/>                                                                                                                                                                       
END
,                                                                                                                                                                    
_('Old kernel'),
_('You are not running the latest kernel version. If your Firewall has been updated this could mean that a new kernel has been installed. To activate it you will have to <a href="%s">reboot</a> the system.<br/>If this is not the case you should check your %s file and make sure that the newest kernel will be booted after a restart.',"/cgi-bin/shutdown.cgi","/boot/grub/grub.conf")
;                 
}
	# Add HTML required to display notifications posted from service(s)
	my $help_enabled = $ENV{'SCRIPT_NAME'};
	printf <<END
<div id="notification-view"  style="display:none;top:50px;"></div>
<div id="module-content">
<span id='gui_set'  class='hidden_class' >$gui_set</span>
<input id="help_hidden" value='$help_enabled' class="hidden_class" />
END
;
check_cookie_user();
}

sub write_login_time()
{
	my %time_out_hash = ();
	my $path = "/var/efw/userinfo/timeout";
	readhash($path,\%time_out_hash);
	my $key = &get_cookie_user('key');
	my $value = `date +%s`;
	chomp $value;
	$time_out_hash{$key} = $value;
	writehash($path,\%time_out_hash);
}
sub get_user_type($)
{
	my $cur_user = shift;
	open(MYFILE,"/var/efw/userinfo/userslist");
	foreach my $line (<MYFILE>) {
		chomp($line);
		my @temp = split(",",$line);
		if($temp[0] eq $cur_user)
		{
			return $temp[4];
		}
	}
	close (MYFILE);
}

#获取系统接口数量
sub get_eth()
{
	my @all_hash;
	my $temp_cmd = `ip a`;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
		{
			$eth = $1;
			if($eth =~ /^eth/)
			{
				push(@all_hash,$eth);
			}
		}
	}
	return @all_hash;
}

####for frame version-by zhouyuan######
#====Modified By WangLin 2015.01.09===#
#====重构菜单项 2015.01.09============#
sub showmenu_frame($) {
	my $ext_func = shift; #判断扩展菜单的点击方法是否定义
	my $is_first_dd = 0;#判断当前是不是第一个一级菜单项
	my $is_first_li = 0;#判断当前是不是第一个二级菜单项
	my $toggle_img_src = "";
	my $dt_a_class = "";
	my $dt_class = "";
	my $dd_style = "";
	my $return_false="";
	my $sigal = 0;
	my @sys_eth = get_eth();
	my $sys_eth_num= @sys_eth;#获取系统接口数量

	my @cur_user=getCurUser();
	my $cur_user_type = get_user_type($cur_user[0]);

	
	if( $ext_func ){
		$ext_func = ", ".$ext_func;
		$return_false = "return false;";
	}
 
	foreach my $k1 ( sort keys %$menu ) {
		#$is_first_dd++;

	 if (! $menu->{$k1}{'enabled'}) {
			next;
		}





		#manager访问控制(为每个创建管理员符子管理员权限)
		 if ($cur_user[0] eq 'admin') {

		   if( !( ($menu->{$k1}{'level'} =~ /2/ && $menu->{$k1}{'level'} =~ /0/)||$menu->{$k1}{'level'} =~/^0_2_3$/||$menu->{$k1}{'level'} =~/^2$/ ) )
			{    
				next;
			}
		}
		 if ($cur_user[0] eq 'logerauth') {

		   if( !( ($menu->{$k1}{'level'} =~ /2/ && $menu->{$k1}{'level'} =~ /3/)||$menu->{$k1}{'level'} =~/^0_2_3$/||$menu->{$k1}{'level'} =~/^2$/ ) )
			{    
				next;
			}
		}
		if ($cur_user[0] eq 'safeauth') {

			if( !( ($menu->{$k1}{'level'} =~ /2/ && $menu->{$k1}{'level'} =~ /1/)||$menu->{$k1}{'level'} =~/^0_2_3$/||$menu->{$k1}{'level'} =~/^2$/ ) )
			{    
				next;
			}
		}
		# if ($cur_user[0] eq 'admin' || $cur_user[0] eq 'logerauth' || $cur_user[0] eq 'safeauth') {
		#     if($menu->{$k1}{'level'} !~ /2/ )
		#     {    
		#         next;
		#     }
		# }
		#loger访问控制
		#日志审计员的访问控制--2013.08.28 王琳
		if ( $cur_user_type eq 3) {
			if($menu->{$k1}{'level'} !~ /3/)
			{    
				next;
			}
		}
		#安全保密员访问控制--2013.08.28 王琳
		if ( $cur_user_type eq 1) {
			if($menu->{$k1}{'level'} !~ /1/)
			{    
				next;
			}
		}
		#admin访问控制
		if ( $cur_user_type eq 0) {
			if($menu->{$k1}{'level'} !~ /0/)
			{    
				next;
			}
		}
		my $link = getlink($menu->{$k1});
		
		if ($link eq '') {
			next;
		}
		if (! is_menu_visible($link)) {
			next;
		}
		if ($menu->{$k1}->{'selected'}) {
			my $ifselected="class=\"selected\"";
			# my $ifselected="";
		} else {
			my $ifselected="";
		}
		# pj:2016/09/27
		if( $cur_user_type eq 1 ){
			
			if($link eq "/cgi-bin/main_start.cgi"){
				$sigal = 1;
				$is_first_dd = 1;
				$is_first_li = 0;
			}else{
				$sigal = 0;
				$is_first_dd = 0;
				$is_first_li =0;
			}

			# $is_first_li = 0;
		}
		else{
			$sigal = 1 ;
			 $is_first_dd++;#之前放在第一行，如果有跳过，逻辑就出错了 2013.02.24 Modified by WangLin    
		}
		
		#if($is_first_dd eq 1)#用eq会出问题
		if($is_first_dd == 1 && $sigal )#之前的比较有问题,导致进入系统时第一个菜单图标显示为toggle-expand.gif 2014.02.20 Modified by WangLin
		{
			$toggle_img_src = "carat_open"; # -
		}else{
			$toggle_img_src = "carat";# +
		}
		#if($is_first_dd eq 1)
		if($is_first_dd == 1 && $sigal)#之前的比较有问题,导致进入系统时第一个菜单图标显示为toggle-expand.gif 2014.02.20 Modified by WangLin
		{
			$dt_a_class="class='dt_selected'";
			$dt_class = "class='sele_fir_menu'";
			$dd_style="";
		}else{
			$dt_a_class="";
			$dt_class="";
			$dd_style="class='hide'";
			 
		}
		printf <<EOF
		<dt $dt_class><a $dt_a_class href="$link" onclick="onclick_first_level_menu( this $ext_func );return false;"><span><span class="$toggle_img_src"></span><span data-hover=$menu->{$k1}{'caption'} class="menu_name">$menu->{$k1}{'caption'}</span></span></a></dt><dd $dd_style>
EOF
		;
	
		my $submenus = $menu->{$k1}->{'subMenu'};
		if (! $submenus) {
			return;
		}





		print "<ul>";
	
		foreach my $item (sort keys %$submenus) {
			my $hash = $submenus->{$item};
	
			if (! $hash->{'enabled'}) {
				next;
			}


			#manager访问控制
			# if ( $cur_user_type eq 2) {
			if ($cur_user_type eq 2 && $cur_user[0] eq 'admin') {
			   if( !( ($hash->{'level'} =~ /2/ && $hash->{'level'} =~ /0/)|| $hash->{'level'} =~/^0_2_3$/||$hash->{'level'} =~/^2$/ ) )
				{    
					next;
				}
			}
			if ($cur_user_type eq 2 && $cur_user[0] eq 'logerauth') {
			   if( !( ($hash->{'level'} =~ /2/ && $hash->{'level'} =~ /3/)|| $hash->{'level'} =~/^0_2_3$/||$hash->{'level'} =~/^2$/ ) )
				{    
					next;
				}
			}
			if ($cur_user_type eq 2 && $cur_user[0] eq 'safeauth') {
			   if( !( ($hash->{'level'} =~ /2/ && $hash->{'level'} =~ /1/)|| $hash->{'level'} =~/^0_2_3$/||$hash->{'level'} =~/^2$/ ) )
				{    
					next;
				}
			}
				# if($hash->{'level'} !~ /2/)
				# {    
				#     next;
				# }
			# }



			#loger访问控制
			if ( $cur_user_type eq 3) {
				if($hash->{'level'} !~ /3/)
				{    
					next;
				}
			}
			#安全审计员访问控制 --2013.08.28 王琳
			if ( $cur_user_type eq 1) {
				if($hash->{'level'} !~ /1/)
				{    
					next;
				}
			}
		
			#admin访问控制
			if ( $cur_user_type eq 0) {
				if($hash->{'level'} !~ /0/)
				{    
					next;
				}
			}




			my $link = getlink($hash);
			if ($link eq '') {
				next;
			}
			if (! is_menu_visible($link)) {
				next;
			}
			my $caption = $hash->{'caption'};










			if(!($sys_eth_num<6 && ($link eq "/cgi-bin/hirel.cgi")))
			{
				$is_first_li++;
				# if ($is_first_dd eq 1 && $is_first_li eq 1) {
				if ($is_first_dd == 1 && $is_first_li == 1) {
					print "<li class=\"selected\" onclick=\"onclick_sec_level_menu(this $ext_func);$return_false\">";
					print "<a href=\"$link\" target='right'> $caption</a>"; 
				} else {
					print "<li onclick='onclick_sec_level_menu(this $ext_func);$return_false'>";
					print "<a href=\"$link\" target='right'> $caption</a>";
				}



				#===遍历subMenu，打印隐藏的三级菜单===#
				print '<div style="display:none;">';
				my $sub_subMenu = $hash->{'subMenu'};
				foreach my $sub_key (sort keys %$sub_subMenu ) {
					my $sub_subItem = $sub_subMenu->{$sub_key};
					if (! $sub_subItem->{'enabled'}) {
						next;
					}
					#manager访问控制
					if ( $cur_user_type eq 2) {
						if($sub_subItem->{'level'} !~ /2/)
						{    
							next;
						}
					}
					#loger访问控制
					if ( $cur_user_type eq 3) {


						if($sub_subItem->{'level'} !~ /3/)
						{    
							next;
						}
					}




					#安全审计员访问控制
					if ( $cur_user_type eq 1) {
						if($sub_subItem->{'level'} !~ /1/)
						{    
							next;
						}
					}





					#admin访问控制
					if ( $cur_user_type eq 0) {
						if($sub_subItem->{'level'} !~ /0/)
						{    
							next;
						}
					}
					print "<span>".$sub_subItem->{'uri'}."</span>";
				}





				print '</div>';
				print "</li>"
			}
		}

 
		printf <<EOF
		</ul>
	</dd>

EOF
		;
	}

}

#####END##########



sub closepage () {

print <<END
	 </div><!-- right_content -->
	</div>
	<br />
	<br />
  </body>
</html>
END
;
}

sub openbigbox($$$) {
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

sub openbox
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
	if ($caption) {
		printf <<EOF
	 <span class="containter-div-header"><span style="display:block;float:left;margin-top:3px;"><img src='/images/applications-blue.png' />$caption</span><span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;">*表示必选项</span></span>
EOF
;
	}
	else {
			 printf <<EOF
		<span class="containter-div-header"><img src='/images/applications-blue.png' />&nbsp;</span>
EOF
;
	}
	
	printf <<EOF
	<div class="containter-div-content">
EOF
	;
}

sub closebox
{
	printf <<EOF
</div>
</div>
EOF
	;
}

sub openeditorbox($$$$@)
{
	my $linktext = shift;
	my $title = shift;
	my $show = shift;
	my $linkname = shift;
	my @errormessages = @_;
	#my @errormessages = $errormessages;
	my $disp_editor = "none";
	my $disp_link = "block";
	if ($show eq "showeditor" || $#errormessages ne -1) {
		$disp_link = "none";
		$disp_editor = "block";
	}

	if ($linktext ne "") {
		printf <<EOF
	<div id="add-div" >

	 <div id="add-div-header">
<span style="display:block;float:left;margin:0px auto auto 5px;"><img src="/images/add.png" />&nbsp;$linktext</span>
EOF
		;
		if($title eq "2") {
			printf <<EOF
			<form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}' >
				<input type="submit" value="清空日志"  class="net_button" style="float: right; margin-top: -2px;">
				<input type="hidden" name="ACTION" value="clearLog">
			</form>
EOF
			;        
	}
		print "</div>";
	}
	printf <<EOF
   <div id="add-div-content"  style="display:$disp_editor">
EOF
;

	#if($title ne '') {
	#    printf <<EOF
	#    <div class="editortitle"><b>$title</b></div>
#EOF
	#    ;
	#}
	if ($#errormessages ne -1) {
		printf <<EOF
		<div class="editorerror" name="$linkname">
			<div>
				<ul style="padding-left: 20px">
EOF
		;
		foreach my $errormessage (@errormessages) {
			printf <<EOF
					<li style="color: red;">
						<font color="red">$errormessage</font>
					</li>
EOF
			;
		}
		printf <<EOF
				</ul>
			</div>
			<hr size="1" color="#cccccc">
		</div>
EOF
		;
	}
	printf <<EOF
		<form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}' >
EOF
	;
}

sub closeeditorbox
{
	my $submitvalue = shift;
	my $cancelvalue = shift;
	my $submitname = shift;
	my $cancelname = shift;
	my $cancellink = shift;
	
	if ($cancellink eq "") {
		$cancellink = "#$cancelname";
	}
	#my $url = "https://".$ENV{'SERVER_ADDR'}.":10443". $ENV{'SCRIPT_NAME'};
	my $url = $ENV{'SCRIPT_NAME'};
	printf <<EOF
<table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
<tr class="add-div-footer"><td width="50%">
<input class='net_button' type='submit' name='$submitname' value='$submitvalue' style="display:block;float:right;color:black" />
</td><td width="50%">
<input class='net_button' type='button'  value='$cancelvalue' style="display:block;float:left;color:black" onclick="parent.window.document.getElementById('rightFrame').src='$url'"/>
<span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
<input type="hidden" class="form" name="color" value=""  /></td></tr>
</table>
   </form>     
	</div>  </div>  
EOF
	,
	_("This Field is required.")
	;
}

sub log
{
	my $logmessage = $_[0];
	$logmessage =~ /([\w\W]*)/;
	$logmessage = $1;
	if (is_branded()){
		system('/usr/bin/logger', '-t', "$brand", $logmessage)
	} else {
		system('/usr/bin/logger', '-t', 'efw', $logmessage);
	}
}

sub age
{
	my ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size,
			$atime, $mtime, $ctime, $blksize, $blocks) = stat $_[0];
	my $now = time;

	my $totalsecs = $now - $mtime;
	my $days = int($totalsecs / 86400);
	my $totalhours = int($totalsecs / 3600);
	my $hours = $totalhours % 24;
	my $totalmins = int($totalsecs / 60);
	my $mins = $totalmins % 60;
	my $secs = $totalsecs % 60;

	return "${days}d ${hours}h ${mins}m ${secs}s";
}

sub validip
{
	my $ip = $_[0];
	if (!($ip =~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/)) {
		return 0; 
	}else{
		my @octets = ($1, $2, $3, $4);
		if($1 == 0)
		{
			if(!(($2 == 0 )&& ($3 == 0) && ($4 == 0)))
			{
				return 0 ;
			}
		}
		foreach $_ (@octets)
		{
			if ($_ < 0 || $_ > 255 || ($_ =~/^0/ && $_)) 
			{
				return 0; 
			}
		}
		return 1;
	}
}

sub validip_addr_segment{
	my $ip = $_[0];
	if( $ip =~ /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}\/([8-9]|[1-2]\d|3[0-1])$/ ){
		return 1;
	}
	else{
		return 0;
	} 
}
sub validmask
{
	my $mask = $_[0];
	# secord part an ip?
	if (&validip($mask)) {
		return 1; }
	# second part a number?
	if (/^0/) {
		return 0; }
	if (!($mask =~ /^\d+$/)) {
		return 0; }
	if ($mask >= 0 && $mask <= 32) {
		return 1; }
	return 0;
}

sub validipormask
{
	my $ipormask = $_[0];

	# see if it is a IP only.
	if (&validip($ipormask)) {
		return 1; }
	# split it into number and mask.
	if (!($ipormask =~ /^(.*?)\/(.*?)$/)) {
		return 0; }
	$ip = $1;
	$mask = $2;
	# first part not a ip?
	if (!(&validip($ip))) { return 0; }
	return &validmask($mask);
}

sub validipandmask
{
	my $ipandmask = $_[0];

	# split it into number and mask.
	if (!($ipandmask =~ /^(.*?)\/(.*?)$/)) {
		return 0; }
	$ip = $1;
	$mask = $2;
	# first part not a ip?
	if (!(&validip($ip))) {
		return 0; }
	return &validmask($mask);
}

sub validport
{
	$_ = $_[0];

	if (!/^\d+$/) {
		return 0; }
	if (/^0./) {
		return 0; }
	if ($_ >= 1 && $_ <= 65535) {
		return 1; }
	return 0;
}

sub is_ipaddress($) {
	my $addr = shift;   
	if ($addr !~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?:\/(\d{1,2}))?$/) {
		return 0;
	}

	if($1 == 0)
	{
			if(!(($2 == 0 )&& ($3 == 0) && ($4 == 0)))
			{
				return 0 ;
			}
	}
	my $total = 0;
	push (@parts,$1);
	push (@parts,$2);
	push (@parts,$3);
	push (@parts,$4);
	my $cidr = '';
	if ($5) {
	$cidr = $5;
	}
	foreach my $number (@parts) {
	$total ++;
	if (($number < 0) || ($number > 255)|| ($number =~ /^0/ && $number)) {
		return 0;
	}
	}
	if ($cidr ne '') {
	if (($cidr < 1) || ($cidr > 32)) {
		return 0;
	}
	}
	return $total;
}

sub validiprange($){
	my $ip_range = shift;
	chomp($ip_range);
	my @ips = split(/-/,$ip_range);
	my $lenght = @ips;
	if($lenght != 2){
		return 0;
	}else{
		if(!is_ipaddress($ips[0]) || !is_ipaddress($ips[1])){
			return 0;
		}
		my @beginip =  split(/\./, $ips[0]);
		my @endip =  split(/\./, $ips[1]);
		my $begin_ip = $beginip[0] << 24 | $beginip[1] << 16 | $beginip[2] << 8 | $beginip[3];
		my $end_ip = $endip[0] << 24 | $endip[1] << 16 | $endip[2] << 8 | $endip[3];
		if($begin_ip < $end_ip){
			return 1;
		}else{
			return 0;
		}
	}
}

sub validmac($) {
	my $addr = shift;
	if ($addr !~ /^([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2})$/i) {
	return 0;
	}
	return 1;
}

sub validhostname
{
	# Checks a hostname against RFC1035
		my $hostname = $_[0];

	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($hostname) < 2 || length ($hostname) > 63) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($hostname !~ /^[a-zA-Z0-9-]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($hostname, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($hostname, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
		return 0;}
	return 1;
}

sub validdomainname
{
	# Checks a domain name against RFC1035
		my $domainname = $_[0];
	my @parts = split (/\./, $domainname);  # Split hostname at the '.'
	$domainname =~ s/\.//g;
	if ($domainname =~/^(\d+)$/){return &validip($_[0]);}
	foreach $part (@parts) {
		# Each part should be at least one characters in length
		# but no more than 63 characters
		if (length ($part) < 1 || length ($part) > 63) {
			return 0;}
		# Only valid characters are a-z, A-Z, 0-9 and -
		if ($part !~ /^[a-zA-Z0-9-]*$/) {
			return 0;}
		# First character can only be a letter or a digit
		if (substr ($part, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
		# Last character can only be a letter or a digit
		if (substr ($part, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
	}
	return 1;
}

sub validfqdn
{
	# Checks a fully qualified domain name against RFC1035
		my $fqdn = $_[0];   
	if ($fqdn =~/(\d+\.)+\d+/){return &validip($fqdn);}     
	my @parts = split (/\./, $fqdn);    # Split hostname at the '.'
	if (scalar(@parts) < 2) {       # At least two parts should
		return 0;}          # exist in a FQDN
						# (i.e. hostname.domain)
	foreach $part (@parts) {
		# Each part should be at least 1 characters in length
		# but no more than 63 characters
		if (length ($part) < 1 || length ($part) > 63) {
			return 0;}
		# Only valid characters are a-z, A-Z, 0-9 and -
		if ($part !~ /^[a-zA-Z0-9-]*$/) {
			return 0;}
		# First character can only be a letter or a digit
		if (substr ($part, 0, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
		# Last character can only be a letter or a digit
		if (substr ($part, -1, 1) !~ /^[a-zA-Z0-9]*$/) {
			return 0;}
	}
	return 1;
}

sub validportrange # used to check a port range 
{
	my $port = $_[0]; # port values
	$port =~ tr/-/:/; # replace all - with colons just in case someone used -
	my $srcdst = $_[1]; # is it a source or destination port

	if (!($port =~ /^(\d+)\:(\d+)$/)) {
	
		if (!(&validport($port))) {  
			if ($srcdst eq 'src'){
				return _('Source port must be a valid port number or port range.');
			} else  {
				return _('Destination port must be a valid port number or port range.');
			} 
		}
	}
	else 
	{
		@ports = ($1, $2);
		if ($1 >= $2){
			if ($srcdst eq 'src'){
				return _('The Source port range has a first value that is greater than or equal to the second value.');
			} else  {
				return _('The destination port range has a first value that is greater than or equal to the second value.');
			} 
		}
		foreach $_ (@ports)
		{
			if (!(&validport($_))) {
				if ($srcdst eq 'src'){
					return _('Source port must be a valid port number or port range.'); 
				} else  {
					return _('Destination port must be a valid port number or port range.');
				} 
			}
		}
		return;
	}
}

# Test if IP is within a subnet
# Call: IpInSubnet (Addr, Subnet, Subnet Mask)
#       Subnet can be an IP of the subnet: 10.0.0.0 or 10.0.0.1
#       Everything in dottted notation
# Return: TRUE/FALSE
sub IpInSubnet
{
	$ip = unpack('N', inet_aton(shift));
	$start = unpack('N', inet_aton(shift));
	$mask  = unpack('N', inet_aton(shift));
	$start &= $mask;  # base of subnet...
	$end   = $start + ~$mask;
	return (($ip >= $start) && ($ip <= $end));
}

sub validemail {
	my $mail = shift;
	return 0 if ( $mail !~ /^[0-9a-zA-Z\.\-\_]+\@[0-9a-zA-Z\.\-]+$/ );
	return 0 if ( $mail =~ /^[^0-9a-zA-Z]|[^0-9a-zA-Z]$/);
	return 0 if ( $mail !~ /([0-9a-zA-Z]{1})\@./ );
	return 0 if ( $mail !~ /.\@([0-9a-zA-Z]{1})/ );
	return 0 if ( $mail =~ /.\.\-.|.\-\..|.\.\..|.\-\-./g );
	return 0 if ( $mail =~ /.\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_./g );
	return 0 if ( $mail !~ /\.([a-zA-Z]{2,})$/ );
	return 1;
}

sub readhasharray {
	my ($filename, $hash) = @_;

	open(FILE, $filename) or die _('Unable to read file %s', $filename);

	while (<FILE>) {
	my ($key, $rest, @temp);
	chomp;
	($key, $rest) = split (/,/, $_, 2);
	if ($key =~ /^[0-9]+$/ && $rest) {
		@temp = split (/,/, $rest);
		$hash->{$key} = \@temp;
		}
	}
	close FILE;
	return;
}

sub writehasharray {
	my ($filename, $hash) = @_;
	my ($key, @temp);

	open(FILE, ">$filename") or die "Unable to write to file $filename";
	
	#对hash排序，以保证储存的顺序的唯一性 by wl 2012.12.16
	my @keys =sort {$a <=> $b} keys %$hash;

	#foreach $key (keys %$hash) { #以前的遍历方法 by wl 2012.12.16
	foreach $key (@keys) {
	if ( $hash->{$key} ) {
		print FILE "$key";
		foreach $i (0 .. $#{$hash->{$key}}) {
		print FILE ",$hash->{$key}[$i]";
		}
	}
	print FILE "\n";
	}
	close FILE;
	my @sync_list = synch();
	foreach my $line(@sync_list){
		if($filename =~ /$line/ || $line =~ /$filename/){
			`sudo fmodify $filename`;
		}
	}
	return;
}
sub save_config_file($$) {
	my $ref = shift;
	my $filename= shift;
	my @lines = @$ref;
	open (FILE, ">$filename");
	foreach my $line (@lines) {
		if ($line ne "") {
			print FILE "$line\n";
		}
	}
	close(FILE);
	my @sync_list = synch();
	foreach my $line(@sync_list){
		if($filename =~ /$line/ || $line =~ /$filename/){
			`sudo fmodify $filename`;
		}
	}
}
sub findhasharraykey {
	foreach my $i (1 .. 1000000) {
	if ( ! exists $_[0]{$i}) {
		 return $i;
	}
	}
}

sub cleanhtml
{
	my $outstring =$_[0];
	$outstring =~ tr/,/ / if not defined $_[1] or $_[1] ne 'y';
	$outstring =~ s/&/&amp;/g;
	$outstring =~ s/\'/&#039;/g;
	$outstring =~ s/\"/&quot;/g;
	$outstring =~ s/</&lt;/g;
	$outstring =~ s/>/&gt;/g;
	return $outstring;
}
sub connectionstatus
{
		my $status;
		opendir UPLINKS, "/var/efw/uplinks" or die "Cannot read uplinks: $!";
				foreach my $uplink (sort grep !/^\./, readdir UPLINKS) {
					if ( -f "${swroot}/uplinks/${uplink}/active") {
						if ( ! $status ) {
								$timestr = &age("${swroot}/uplinks/${uplink}/active");
								$status = _('Connected').": $uplink (<span class='ipcop_StatusBigRed'>$timestr</span>) ";
						} else {
								$timestr = &age("${swroot}/uplinks/${uplink}/active");
								$status = "$status , $uplink (<span class='ipcop_StatusBigRed'>$timestr</span>) ";
						}
					} elsif ( -f "${swroot}/uplinks/${uplink}/connecting") {
						if ( ! $status ) {
								$status = _('Connecting...')." $uplink";
						} else {
								$status = "$status , "._('Connecting...')." $uplink (<span class='ipcop_StatusBigRed'>$timestr</span>) ";
						}
					}
					$lines++;
				}
				closedir(UPLINKS);
				if ( ! $status ) {
						$status = _('Idle');
				}
				$connstate = "<span class='ipcop_StatusBig'>$status</span>";
	return $connstate;
}

sub srtarray 
# Darren Critchley - darrenc@telus.net - (c) 2003
# &srtarray(SortOrder, AlphaNumeric, SortDirection, ArrayToBeSorted)
# This subroutine will take the following parameters:
#   ColumnNumber = the column which you want to sort on, starts at 1
#   AlphaNumberic = a or n (lowercase) defines whether the sort should be alpha or numberic
#   SortDirection = asc or dsc (lowercase) Ascending or Descending sort
#   ArrayToBeSorted = the array that wants sorting
#
#   Returns an array that is sorted to your specs
#
#   If SortOrder is greater than the elements in array, then it defaults to the first element
# 
{
	my ($colno, $alpnum, $srtdir, @tobesorted) = @_;
	my @tmparray;
	my @srtedarray;
	my $line;
	my $newline;
	my $ttlitems = scalar @tobesorted; # want to know the number of rows in the passed array
	if ($ttlitems < 1){ # if no items, don't waste our time lets leave
		return (@tobesorted);
	}
	my @tmp = split(/\,/,$tobesorted[0]);
	$ttlitems = scalar @tmp; # this should be the number of elements in each row of the passed in array

	# Darren Critchley - validate parameters
	if ($colno > $ttlitems){$colno = '1';}
	$colno--; # remove one from colno to deal with arrays starting at 0
	if($colno < 0){$colno = '0';}
	if ($alpnum ne '') { $alpnum = lc($alpnum); } else { $alpnum = 'a'; }
	if ($srtdir ne '') { $srtdir = lc($srtdir); } else { $srtdir = 'src'; }

	foreach $line (@tobesorted)
	{
		chomp($line);
		if ($line ne '') {
			my @temp = split(/\,/,$line);
			# Darren Critchley - juggle the fields so that the one we want to sort on is first
			my $tmpholder = $temp[0];
			$temp[0] = $temp[$colno];
			$temp[$colno] = $tmpholder;
			$newline = "";
			for ($ctr=0; $ctr < $ttlitems ; $ctr++) {
				$newline=$newline . $temp[$ctr] . ",";
			}
			chomp($newline);
			push(@tmparray,$newline);
		}
	}
	if ($alpnum eq 'n') {
		@tmparray = sort {$a <=> $b} @tmparray;
	} else {
		@tmparray = (sort @tmparray);
	}
	foreach $line (@tmparray)
	{
		chomp($line);
		if ($line ne '') {
			my @temp = split(/\,/,$line);
			my $tmpholder = $temp[0];
			$temp[0] = $temp[$colno];
			$temp[$colno] = $tmpholder;
			$newline = "";
			for ($ctr=0; $ctr < $ttlitems ; $ctr++){
				$newline=$newline . $temp[$ctr] . ",";
			}
			chomp($newline);
			push(@srtedarray,$newline);
		}
	}

	if ($srtdir eq 'dsc') {
		@tmparray = reverse(@srtedarray);
		return (@tmparray);
	} else {
		return (@srtedarray);
	}
}

sub speedtouchversion
{
	if (-f "/proc/bus/usb/devices")
	{
		$speedtouch=`/bin/cat /proc/bus/usb/devices | /bin/grep 'Vendor=06b9 ProdID=4061' | /usr/bin/cut -d ' ' -f6`;
		if ($speedtouch eq '') {
			$speedtouch= _('Connect the modem');
		}
	} else {
		$speedtouch='USB '._('not running');
	}
	return $speedtouch
}

sub CheckSortOrder {
#Sorting of allocated leases
	if ($ENV{'QUERY_STRING'} =~ /^IPADDR|^ETHER|^HOSTNAME|^ENDTIME/ ) {
	my $newsort=$ENV{'QUERY_STRING'};
		&readhash("${swroot}/dhcp/settings", \%dhcpsettings);
		$act=$dhcpsettings{'SORT_LEASELIST'};
		#Reverse actual ?
		if ($act =~ $newsort) {
			if ($act !~ 'Rev') {$Rev='Rev'};
			$newsort.=$Rev
		};

		$dhcpsettings{'SORT_LEASELIST'}=$newsort;
	&writehash("${swroot}/dhcp/settings", \%dhcpsettings);
		$dhcpsettings{'ACTION'} = 'SORT';  # avoid the next test "First lauch"
	}

}

sub PrintActualLeases
{
	if (! -f "/var/lib/dhcp/dhcpd.leases") {
	return;
	}
	&openbox('100%', 'left', _('Current dynamic leases'));
	printf <<END
<br />
<table width='100%' cellpadding="0" cellspacing="0" class='ruleslist'>
<tr>
<td width='25%' align='center' class='boldbase'><b>%s</b></td>
<td width='25%' align='center' class='boldbase'><b>%s</b></td>
<td width='20%' align='center' class='boldbase'><b>%s</b></td>
<td width='30%' align='center' class='boldbase'><b>%s</b></td>
</tr>
END
,
_('IP address'),
_('MAC address'),
_('Hostname'),
_('Lease expires')
;

	open(LEASES,"/var/lib/dhcp/dhcpd.leases") or die "Can't open dhcpd.leases";
	while ($line = <LEASES>) {
	next if( $line =~ /^\s*#/ );
	chomp($line);
	@temp = split (' ', $line);

	if ($line =~ /^\s*lease/) {
		$ip = $temp[1];
		#All field are not necessarily read. Clear everything
		$endtime = 0;
		$ether = "";
		$hostname = "";
	}

	if ($line =~ /^\s*ends/) {
		$line =~ /(\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+)/;
		$endtime = timegm($6, $5, $4, $3, $2 - 1, $1 - 1900);
	}

	if ($line =~ /^\s*hardware ethernet/) {
		$ether = $temp[2];
		$ether =~ s/;//g;
	}

	if ($line =~ /^\s*client-hostname/) {
		$hostname = "$temp[1] $temp[2] $temp[3]";
		$hostname =~ s/;//g;
		$hostname =~ s/\"//g;
	}

	if ($line eq "}") {
		@record = ('IPADDR',$ip,'ENDTIME',$endtime,'ETHER',$ether,'HOSTNAME',$hostname);
			$record = {};                               # create a reference to empty hash
		%{$record} = @record;                       # populate that hash with @record
		$entries{$record->{'IPADDR'}} = $record;    # add this to a hash of hashes
	}
	}
	close(LEASES);

	my $id = 0;
	foreach my $key (sort leasesort keys %entries) {

	my $hostname = &cleanhtml($entries{$key}->{HOSTNAME},"y");

	if ($id % 2) {
		print "<tr class='even'>"; 
	}
	else {
		print "<tr class='oodd'>"; 
	}

	printf <<END
<td align='center'>$entries{$key}->{IPADDR}</td>
<td align='center'>$entries{$key}->{ETHER}</td>
<td align='center'>&nbsp;$hostname </td>
<td align='center'>
END
	;

	($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $dst) = localtime ($entries{$key}->{ENDTIME});
	$enddate = sprintf ("%d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

	if ($entries{$key}->{ENDTIME} < time() ){
		print "<p style='text-decoration:line-through'>$enddate</p>";
	} else {
		print "$enddate";
	}
	print "</td></tr>";
	$id++;
	}
	if ($id eq '0') {
		no_tr(4,_('Current no content'));
	}
	print "</table><br />";
	&closebox();
}


# This sub is used during display of actives leases
sub leasesort {
	if (rindex ($dhcpsettings{'SORT_LEASELIST'},'Rev') != -1)
	{
		$qs=substr ($dhcpsettings{'SORT_LEASELIST'},0,length($dhcpsettings{'SORT_LEASELIST'})-3);
		if ($qs eq 'IPADDR') {
			@a = split(/\./,$entries{$a}->{$qs});
			@b = split(/\./,$entries{$b}->{$qs});
			($b[0]<=>$a[0]) ||
			($b[1]<=>$a[1]) ||
			($b[2]<=>$a[2]) ||
			($b[3]<=>$a[3]);
		}else {
			$entries{$b}->{$qs} cmp $entries{$a}->{$qs};
		}
	}
	else #not reverse
	{
		$qs=$dhcpsettings{'SORT_LEASELIST'};
		if ($qs eq 'IPADDR') {
		@a = split(/\./,$entries{$a}->{$qs});
			@b = split(/\./,$entries{$b}->{$qs});
			($a[0]<=>$b[0]) ||
		($a[1]<=>$b[1]) ||
		($a[2]<=>$b[2]) ||
			($a[3]<=>$b[3]);
		}
		else {
			$entries{$a}->{$qs} cmp $entries{$b}->{$qs};
		}
	}
}

sub get_uplinks() {
	my @uplinks = ();
	opendir(DIR, "${swroot}/uplinks/") || return \@uplinks;
	foreach my $dir (readdir(DIR)) {
		next if ($dir =~ /^\./);
		next if (!(-f "${swroot}/uplinks/$dir/settings"));
		push(@uplinks, $dir);
	}
	closedir(DIR);
	return \@uplinks;
}

sub get_uplink_info($$) {
	my $name = shift;
	my $getbackup = shift;
	my %uplink = {};
	
	# uplinks settings file
	my $uplink_dir = "${swroot}/uplinks/$name";
	my $uplink_file = "$uplink_dir/settings";
	my $uplink_data_file = "$uplink_dir/data";
	
	# if the uplink doesn't exist (has no settings file), false
	# is returned, else the settings are read.
	if (! -e $uplink_file) {
		return {};
	}
	readhash($uplink_file, \%uplink);

	$uplink{'ID'} = $name;
	
	if ($uplink{'NAME'} eq "") {
		if ($name eq "main") {
			$uplink{'NAME'} = _("Main uplink");
		}
		else {
			$uplink{'NAME'} = "ID: ".$name;
		}
	}
	
	# non connected uplinks don't have an data file,
	# hence reading that file would 'cause the script
	# to fail.
	if(-e $uplink_data_file) {
		my %data = {};
		readhash($uplink_data_file, \%data);
		$uplink{'data'} = \%data;
	}
	
	if ($uplink{'BACKUPPROFILE'} eq "main") {
		$uplink{'BACKUPPROFILENAME'} = _("Main uplink");
	}
	elsif ($uplink{'BACKUPPROFILE'} ne "" && -e "${swroot}/uplinks/$uplink{'BACKUPPROFILE'}/settings") {
		readhash("${swroot}/uplinks/$uplink{'BACKUPPROFILE'}/settings", \%backuplink);
		if ($backuplink{'NAME'} eq "") {
			$backuplink{'NAME'} = "ID: " . $name;
		}
		$uplink{'BACKUPPROFILENAME'} = $backuplink{'NAME'};
	}
	else {
		$uplink{'BACKUPPROFILE'} = "";
		$uplink{'BACKUPPROFILENAME'} = _("None");
	}
	
	return %uplink;
}

sub get_iface($) {
	my $uplink = shift;
	eval {
		&readhash("${swroot}/uplinks/$uplink/data", \%set);
	};
	$iface = $set{'interface'};
	return $iface;
}

sub get_red_ifaces_by_type($) {
	my $type=shift;
	my @gottypeiface = ();
	my @gottypeuplink = ();
	my @gottype = ();

	my $ref=get_uplinks();
	my @uplinks=@$ref;
	my %set = ();
	foreach my $link (@uplinks) {
	eval {
		&readhash("${swroot}/uplinks/$link/data", \%set);
	};
	push(@gottype, $link);

	my $iface = $set{'interface'};
	next if (!$iface);

	if ($set{'RED_TYPE'} eq $type) {
		push(@gottypeiface, $iface);
		push(@gottypeuplink, $link);
	}
	}
	return (\@gottypeiface, \@gottypeuplink, \@gottype);
}

sub get_red_ifaces() {
	my @uplinks = ();
	my @gottypeiface = ();
	opendir(DIR, "${swroot}/uplinks/") || return \@uplinks;
	foreach my $dir (readdir(DIR)) {
		next if ($dir =~ /^\./);
		next if (!(-f "${swroot}/uplinks/$dir/data"));
		&readhash("${swroot}/uplinks/$dir/data", \%set);
		push(@gottypeiface, $set{'interface'});
	}
	closedir(DIR);
	return \@gottypeiface;
}

sub get_zone_devices($) {
	my $bridge = shift;
	my @ifaces = ();
	open (FILE, "${swroot}/ethernet/$bridge") || return "";
	foreach my $line (<FILE>) {
	chomp($line);
	next if (!$line);
	push(@ifaces, $line);
	}
	close(FILE);
	return \@ifaces;
}


sub register_submenuitem($$$$) {
	my $menuitem = shift;
	my $submenuitem = shift;
	my $newitem = shift;
	my $hash = shift;

	$menu->{$menuitem}->{'subMenu'}->{$submenuitem}->{'subMenu'}->{$newitem} = $hash;
	return ($menu->{$menuitem}->{'subMenu'}->{$submenuitem}->{'subMenu'}->{$newitem} == $hash);

}

sub register_menuitem($$$) {
	my $menuitem = shift;
	my $newitem = shift;
	my $hash = shift;
	
	if ( ! $newitem ) {
		$menu->{$menuitem} = $hash;
		return ($menu->{$menuitem} == $hash);
	} 
	
	$menu->{$menuitem}->{'subMenu'}->{$newitem} = $hash;
	return ($menu->{$menuitem}->{'subMenu'}->{$newitem} == $hash);

	# sample:
	#
	# my $menuitem = {
	#                 'caption' => _('Home'),
	#                 'uri' => '/cgi-bin/index.cgi',
	#                 'title' => _('Home'),
	#                 'enabled' => 1,
	#                };
	# 
	# register_menuitem('01.system', '01.home', $menuitem);
	#
	#
	#
}

sub validzones() {
	my @ret = ();

	push(@ret, 'GREEN');
	if (orange_used()) {
	push(@ret, 'ORANGE');
	}
	if (blue_used()) {
	push(@ret, 'BLUE');
	}
	if (!is_modem()) {
	push(@ret, 'RED');
	}

	return \@ret;
}


sub get_red_devices() {
	my $ref = get_uplinks();
	my @ret = ();
	foreach my $uplink (@$ref) {
	my %config = ();
	eval {
		&readhash("${swroot}/uplinks/$uplink/settings", \%config);
	};
	my $iface = "";
	if (($config{'RED_TYPE'} eq "STATIC") || 
			($config{'RED_TYPE'} eq "DHCP") || 
			($config{'RED_TYPE'} eq "PPPOE") || 
			($config{'RED_TYPE'} eq "PPTP")) {
		$iface = $config{'RED_DEV'};
	}
	next if ($iface =~ /^$/);
	push(@ret, $iface);
	}
	return \@ret;
}

sub get_uplink_by_device($) {
	my $device = shift;
	my $ref = get_uplinks();
	my @ret = ();
	foreach my $uplink (@$ref) {
	my %config = ();
	eval {
		&readhash("${swroot}/uplinks/$uplink/settings", \%config);
	};
	my $iface = $config{'RED_DEV'};
	push(@ret, $uplink) if ($iface eq $device);
	}
	return \@ret;
}

sub disable_uplink($) {
	my $uplink = shift;
	return 0 if (! -e "${swroot}/uplinks/$uplink/settings");
	eval {
	my %confhash;
	&readhash("${swroot}/uplinks/$uplink/settings", \%confhash);
	$confhash{'ENABLED'} = 'off';
	&writehash("${swroot}/uplinks/$uplink/settings", \%confhash);
	return 1;
	};
	return 0
}

sub setbgcolor($$$) {
	my $is_editing = shift;
	my $line = shift;
	my $i = shift;

	if ($is_editing) {
	if ($line == $i) {
		return 'selected';
	}
	}
	if ($i % 2) {
		return 'env';
	}
	return 'odd';
}

sub value_or_nbsp($) {
	my $value = shift;
	if ($value =~ /^$/) {
	return '&nbsp;';
	}
	return $value;
}

sub get_hotspot_dev() {
	if (! -e "$HOTSPOT_ENABLED") {
	return "";
	}

	open (F, "$ethernet_dir/br2") || return "";
	my @file = <F>;
	close(F);
	my $dev = $file[0];
	chomp($dev);
	return $dev;
}

sub getzonebyinterface($) {
	my $iface = shift;
	my $zones = validzones();
	foreach my $zone (@$zones) {
		my $devices = get_zone_devices($ethsettings{$zone.'_DEV'});
		return $zone if (grep(/^$iface$/, @$devices));
	}
	my $reddev = get_red_devices();
	return 'RED' if (grep(/^$iface$/, @$reddev));
	return '';
}

sub joinbridge($$) {
	my $bridge = shift;
	my $device = shift;

	my $bridge_ifaces = get_zone_devices($bridge);
	return if (grep (/^$device$/, @$bridge_ifaces));

	my $file = "/var/efw/ethernet/$bridge";
	if (!open(F, ">>$file")) {
		warn("Could not open '$file' because $!");
		return;
	}
	print F "$device\n";
	close(F);
}

sub removefrombridge($$) {
	my $bridge = shift;
	my $device = shift;
	my $bridge_ifaces = get_zone_devices($bridge);

	my $file = "/var/efw/ethernet/$bridge";
	if (!open(F, ">$file")) {
		warn("Could not open '$file' because $!");
		return;
	}
	foreach my $iface (@$bridge_ifaces) {
		next if ($iface eq $device);
		print F "$iface\n";
	}
	close(F);
}

sub toggle_file($$) {
	my $file = shift;
	my $set = shift;

	if ($set) {
		`touch $file`;
		return 1;
	}
	if (-e $file) {
		unlink($file);
	}
	return 0;
}

sub applybox($) {
	my $text = shift;

	printf <<EOF
<div id="pop-apply-div">
<span><img src="/images/pop_apply.png" /> $text</span>
<span id="cancel">
<form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
<input class="net_button" type="submit" name="save" value="%s">
<input type="hidden" name="ACTION" value="apply">
</form>
</span>
</div>
EOF
, _('Apply')
;
}

sub errorbox($) {
	my $text = shift;
	my $id = shift;
	my $style = shift;
	if ($text =~ /^\s*$/) {
		return;
	}
	$id = ($id ne "") ? "id=\"$id\"" : "";
	my @temp = split("<br />",$text);
	my $length = @temp;
	foreach my $error(@temp)
	{
		$new_text .= "<li style='text-align:left;'>".$error."</li>";
	}

	my $height = ($length*16+40)."px";
	printf <<EOF
<div style="height:$height;" id="pop-error-div">
<span ><ul id="error_ul"  style="float:left;position:relative;left:50%;"><li style="float:left;position:relative;right:50%;"><img src="/images/pop_error.png" style="display:block;float:left;margin-top:-6px;"/><ul style="float:left;">%s</ul></li></ul></span>
<br />
</div>
EOF
, $new_text
, _('sure')
;


printf <<EOF
<script>

window.setTimeout(fade_out,4000);
function fade_out()
{
	\$("#pop-error-div").fadeOut("slow");
}
</script>
EOF
;
}


sub warnbox($) {
	my $caption = shift;
	if ($caption =~ /^\s*$/) {
		return;
	}
	printf <<EOF, _('Warning');
<h3 class="warning">%s</h3>
<div class="warning"><img class="warning" src='/images/dialog-warning.png' alt='_("Warning")'>$caption</div>
EOF
;
}

sub notificationbox($) {
	my $text = shift;
	my $id = shift;
	my $style = shift;
	if ($text =~ /^\s*$/) {
		return;
	}
	$id = ($id ne "") ? "id=\"$id\"" : "";
	printf <<EOF
<div id="pop-note-div">
<span><img src="/images/Emoticon.png" /> %s</span>
<br />
</div>
EOF
, $text
;

printf <<EOF
<script>
window.setTimeout(fade_out,4000);
function fade_out()
{
	\$("#pop-note-div").fadeOut("slow");
}
</script>
EOF
;
}

sub get_category {
	# this is deprecated use get_category_template instead
	
	my $name = shift;      # name of the marker
	my $text = shift;      # text to display
	my $checked = shift; # are all subcategories checked? (all/some/none)
	my($subcategories) = shift;
	my($status) = shift;
	
	my @subcategories = ();
	
	for my $item (keys %$subcategories) {
		my $subname = $subcategories->{$item};
		my $allowed = 0;
		if ($status->{$item} ne "") {
			$allowed = 1;
		}
		push(@subcategories, {T_TITLE => $subname, V_NAME => $item, V_ALLOWED => $allowed});
	}

	my %params = (T_TITLE => $text, V_NAME => $name, V_SUBCATEGORIES => \@subcategories, V_HIDDEN => 1);
	print get_category_widget(\%params);
}

sub get_folding {
	my $name = shift;      # name of the marker
	my $status = shift;    # start/EOF
	my $text = shift;      # text to display
	my $open = shift;      # "open" if value should be shown per default
	
	my $expand_png = "/images/expand.png";
	my $collapse_png = "/images/collapse.png";
	
	my $disp = "hidden";
	my $src = $expand_png;
	
	if ($open eq "open") {
		undef $disp;
		$src = $collapse_png;
	}

	my $start = "<div class=\"folding\" name=\"$name\">
					<div class=\"foldingtitle\" name=\"$name\">
						<img name=\"fold_$name\" src=\"$src\" />
						&nbsp;
						<span style=\"line-height: 11px;\">$text</span>
					</div>";
	
	if ( $status eq "start" ) {
		return $start . "<div style=\"clear: both;width:100%;\"/><div class=\"foldingcontent $disp\" id=\"$name\">";
	}
	else {
		return "</div></div><div style=\"clear: both;width:100%;\"/>";
	}
}

sub ipmask_to_cidr($) {
   my $addr = shift;
   if ($addr =~ /\//) {
	   my ($ip,$msklen) = ipv4_parse($addr);
	   return "$ip/$msklen";
   }
   return $addr;
}

sub get_taps() {
	my @ret = ();

	if (open (F, "${swroot}/openvpn/clientconfig")) {
	foreach my $line (<F>) {
		chomp($line);
		my @arr = split(/:/, $line);
		next if ($arr[0] ne 'on');
		next if ($arr[6] eq 'bridged');
		
		my $iface = $arr[1];
		my $name = $arr[2];
		chomp($iface);
		chomp($name);
		next if ($iface =~ /^$/);
		next if ($name =~ /^$/);
		my %hash = ();
		my $ref = \%hash;
		$ref->{'name'} = $name;
		$ref->{'tap'} = $iface;
		push(@ret, $ref);
	}
	close(F);
	}

	if (opendir(DIR, "${swroot}/openvpnclients")) {
	foreach my $dir (readdir(DIR)) {
		next if ($dir =~ /^\./);
		next if ($dir =~ /^default$/);
		next if (! -f "${swroot}/openvpnclients/$dir/settings");
		my %conf;
		readhash("${swroot}/openvpnclients/$dir/settings", \%conf);
		my $dev = $conf{'DEVICE'};
		chomp($dev);
		next if ($dev =~ /^$/);

		my %hash = ();
		my $ref = \%hash;
		$ref->{'name'} = $dir;
		$ref->{'tap'} = $dev;
		$ref->{'bridged'} = 0;
		if ($conf{'ROUTETYPE'} eq 'bridged') {
		$ref->{'bridged'} = 1;
		$ref->{'zone'} = uc($conf{'BRIDGE'});
		}
		if ($ref->{'zone'} eq '') {
		$ref->{'zone'} = 'GREEN';
		}
		push(@ret, $ref);
	}
	}
	return \@ret;
}

sub get_uplink_label($) {
	my $uplink = shift;
	my %set = ();
	eval {
	&readhash("${swroot}/uplinks/$uplink/settings", \%set);
	};
	my %hash = ();
	my $ref = \%hash;
	$ref->{'name'} = $uplink;
	$ref->{'dev'} = "UPLINK:$uplink";
	$ref->{'title'} = $set{'NAME'};
	if ($ref->{'title'}) {
	$ref->{'description'} = $ref->{'title'};
	} else {
	$ref->{'description'} = $uplink;
	}
	return $ref;
}

sub get_uplinks_list() {
	my $uplinks=get_uplinks();
	my @arr = ();
	my $ret = \@arr;
	foreach my $link (@$uplinks) {
	push(@arr, get_uplink_label($link));
	}
	return $ret;
}

sub get_aliases() {
	my $uplinks=get_uplinks();
	my @arr = ();
	my $ret = \@arr;
	foreach my $link (@$uplinks) {
	my %set = ();
	eval {
		&readhash("${swroot}/uplinks/$link/settings", \%set);
	};
	my %hash = ();
	my $ref = \%hash;
	$ref->{'name'} = $link;
	$ref->{'value'} = "UPLINK:$link,0.0.0.0";
	$ref->{'dev'} = "UPLINK:$link";
	$ref->{'title'} = $set{'NAME'};
	push(@arr, $ref);
	my $ips = $set{'RED_IPS'};
	next if ($ips =~ /^$/);
	foreach my $addr (split(/,/, $ips)) {
		next if ($addr =~ /^$/);
		my ($ip,$cidr) = ipv4_parse($addr);     
		next if ($ip =~ /^$/);
		my %hash = ();
		my $ref = \%hash;
		$ref->{'name'} = "$link - $ip";
		$ref->{'value'} = "UPLINK:$link,$ip";
		$ref->{'ip'} = "$ip";
		$ref->{'dev'} = "$link";
		push(@arr, $ref);
	}
	}
	my $taps = get_taps();
	foreach my $tap (@$taps) {
	my %hash = ();
	my $ref = \%hash;
	$ref->{'name'} = _('VPN') . ' ' . $tap->{'name'};
	$ref->{'value'} = 'VPN:'.$tap->{'name'}.',0.0.0.0';
	$ref->{'ip'} = '0.0.0.0';
	$ref->{'dev'} = $tap->{'name'};
	push(@arr, $ref);
	}
	my %hash = ();
	my $ref = \%hash;
	$ref->{'name'} = _('VPN') . ' ' . _('IPsec');
	$ref->{'value'} = 'VPN:IPSEC,0.0.0.0';
	$ref->{'ip'} = '0.0.0.0';
	$ref->{'dev'} = 'ipsec+';
	push(@arr, $ref);

	return $ret;
}


sub getSpareMemory() {
	my $swapfree = 0;
	my $used = 0;
	foreach my $line (`/usr/bin/free`) {
	if ($line =~ /cache:\s+(\d+)\s+(\d+)$/) {
		$used = $1;
	}
	if ($line =~ /Swap:\s+(\d+)\s+(\d+)\s+(\d+)$/) {
		$swapfree = $3;
	}
	}
	return ($swapfree-$used)*1024;
}

sub fileStayInMemory($) {
	my $filename = shift;
	return 0 if (! -e $filename);

	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
	$atime,$mtime,$ctime,$blksize,$blocks)
	= stat($filename);
	return 0 if ($size > getSpareMemory());
	return 1;
}

sub writehash
{
	my $filename = $_[0];
	my $hash = $_[1];
	
		if (-e $filename) {
			system("cp -f $filename ${filename}.old &>/dev/null");
		}
	# write cgi vars to the file.
	open(FILE, ">${filename}") or die "Unable to write file $filename";
	flock FILE, 2;
	foreach $var (keys %$hash) 
	{
		
		$val = $hash->{$var};
		
		#$val = decode_entities($hash->{$var});
		# Darren Critchley Jan 17, 2003 added the following because when submitting with a graphic, the x and y
		# location of the mouse are submitted as well, this was being written to the settings file causing
		# some serious grief! This skips the variable.x and variable.y
		if (!($var =~ /(.x|.y)$/)) {
			
			$val = decode_entities($val);
			if ($val =~ /\s/) {
				$val = "\'$val\'"; 
				

			}
			if (!($var =~ /^ACTION/)) {
				print FILE "${var}=${val}\n";
				

			}
		}
	}
	close FILE;
	my @sync_list = synch();
	foreach my $line(@sync_list){
		if($filename =~ /$line/ || $line =~ /$filename/){
			`sudo fmodify $filename`;
		}
	}
}
###读取双机热备列表内容
sub synch() {
	my $filename ="/usr/sbin/synch.list";
	my @lines;
	open(FILE, "<$filename");
	foreach my $line (<FILE>){
		chomp($line);
		$line =~ s/[\r\n]//g;
		push(@lines, $line);
	}
	close (FILE);
	return @lines;
}
sub readhash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	open(FILE, $filename) or return;
	
	while (<FILE>)
	{
		chomp;
		($var, $val) = split /=/, $_, 2;
		if ($var)
		{
			$val =~ s/^\'//g;
			$val =~ s/\'$//g;

			# Untaint variables read from hash
			$var =~ /([A-Za-z0-9_-]*)/;        $var = $1;
			$val =~ /([\w\W]*)/; $val = $1;
			$hash->{$var} = encode_entities($val,"'\"");
		}
	}
	close FILE;
}
sub read_conf_file($) {
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
# 读取文件中特定的一行
sub read_conf_line($$) {
	my $file=shift;
	my $line=shift;
	my @lines = read_conf_file($file);
	my $count = @lines;
	if($count < $line){
		return "";
	}else{
		return $lines[$line];
	}
}

sub getcgihash {
	my ($hash, $params, $flag) = @_;
	my $cgi = CGI->new ();
	$hash->{'__CGI__'} = $cgi;
	return if ($ENV{'REQUEST_METHOD'} ne 'POST');
	if (!$params->{'wantfile'}) {
		$CGI::DISABLE_UPLOADS = 1;
		$CGI::POST_MAX = 512 * 1024;
	}
	else {
		$CGI::POST_MAX = 10 * 1024 * 1024;
	}

	$cgi->referer() =~ m/^https?\:\/\/([^\/]+)/;
	my $referer = $1;
	$cgi->url() =~ m/^https?\:\/\/([^\/]+)/;

	my $servername = uri_unescape($1);
	return if ($referer ne $servername);

	### Modified for getting multi-vars, split by |
	%temp = $cgi->Vars();
	foreach my $key (keys %temp) {
		$hash->{$key} = $temp{$key};
		$hash->{$key} =~ s/\0/|/g;
		$hash->{$key} =~ s/^\s*(.*?)\s*$/$1/;
		if( !$flag ) {
			$hash->{$key} = encode_entities(uri_unescape($hash->{$key}),"'\"");
		}
	}

	if (($params->{'wantfile'})&&($params->{'filevar'})) {
		$hash->{$params->{'filevar'}} = $cgi->upload($params->{'filevar'});
	}
	return;
}

# Converts an array to JSON format
sub arrayToJSON {
	my $refarray = shift;
	my @array = @$refarray;
	my $json = '[';
	my @value_pairs = ();
	
	foreach (@array) {
		push(@value_pairs, sprintf("\"%s\"", $_));
	}
	
	$json .= join(',', @value_pairs);
	$json .= ']';
	
	return $json;
}

# Convert hash to JSON format
sub hashToJSON {
	my $hashref = shift;
	my %hash = %$hashref;
	my $json = '{';
	my @key_value_pairs = ();
	foreach $key (keys %hash) {
		push(@key_value_pairs, sprintf("\"%s\": \"%s\"", $key, $hash{$key}));
	}
	$json .= join(',', @key_value_pairs);
	$json .= '}';
	
	return $json;
}

# Helper to display notifications on the web interface
sub service_notifications {
	my $servicesref = shift;
	my $optionsref = shift;
	
	printf <<END
		<script type="text/javascript">
			\$(document).ready(function() {
				
				/* Enable visualization of service notifications */
				display_notifications(%s, %s);
			})
		</script>
END
, arrayToJSON($servicesref)
, hashToJSON($optionsref);
}
####格式化日期的函数将小于10的月份和日期前补0   2013-1-4 by 张征
sub format_date($){
	my $time = shift;
	my @elem = split(/-/,$time);
	if($elem[1] < 10){
		$len = rindex $elem[1]."\$", "\$";
		if($len < 2){
			$elem[1] = "0".$elem[1];
		}
	}
	if($elem[2] < 10){
		$len = rindex $elem[2]."\$", "\$";
		if($len < 2){
			$elem[2] = "0".$elem[2];
		}
	}
	return "$elem[0]-$elem[1]-$elem[2]";
}
sub debug_info($){
	my $mesg = shift;
	# $mesg =~ s/(>|<)//g;
	$mesg =~ s/"/\\"/g;

	# $mesg =~ s/&/+/g;
	# $mesg =~ s/ /+/g;
	# $mesg =~ s/(\$)/d/g;
	my $t=  localtime(time);
	system("echo -e \"$t:$mesg\" >> /var/efw/debug.log");    
}
#######end 2013-1-4 by 张征

#处理用户非法操作
sub detIllOpe($) {
	my @data = @_;
	my $status = 0;
	my $errorMesg = "";
	foreach( @data ) {
		if ( /[@#\$^%&*~`;]/ ) {
			$status = 1; 
			$errorMesg = '非法操作';
			return ( $status, $errorMesg );
		}
	}
	return ( $status, $errorMesg );
}

sub forMd5($) {
	my $data = shift;
	my $md5 = Digest::MD5->new;
	$md5->add($data);
	my $data = $md5->hexdigest;
	return $data;
}

sub readPsdLength() {
	my $save_filename = '/var/efw/userinfo/user_config';
	my %temp_config = ();
	&readhash($save_filename, \%temp_config);
	return $temp_config{'PSD_LENGTH'};
}

###添加日志导入功能面板 by leo 2016-11-30
sub importLogPanel() {
	&openeditorbox("导入日志","2","3","4");
	printf <<EOF
		<div class="importlog-content">
			<div class="importlog-left">
				<span>选择日志文件</span>
			</div>
			<div class="importlog-right">
				<a href="javascript:;" class="file">选择文件
					<input type="file" name="upload_file" id="upload_file">
				</a>
				<label id="upload_file_tip">未选择日志文件</label>
			</div>
		</div>
		<input type="hidden" name="ACTION" value="importLog">
		<script language="JavaScript">
		!function() {
			document.getElementById("upload_file").onchange = function() {
				var str = document.getElementById("upload_file").value;
				if(str == "") {
					document.getElementById("upload_file_tip").innerText = "未选择日志文件";
				}else {
					var arr = str.split("\\\\");
					document.getElementById("upload_file_tip").innerText = arr.pop();
				}
			}
		}();
		</script> 
EOF
;
	&closeeditorbox("导入","取消","7","8","9");
	
	
}

###添加日志导入功能 by leo 2016-11-30
sub importLog($$) {
	my $par = shift;
	my $logType = shift;
	my $cgi = new CGI;
	my $file_name = $cgi->param('upload_file');
	my $ACTION = $par->{'ACTION'};
	
	if ($ACTION eq "importLog") {

		my $file_path = `mktemp -p /tmp`;

		my $content = '';
		while ( <$file_name> )
		{
			$content .= $_;

		}
		$content = &log_encrypt('de',$logType,$content);

		open ( UPLOADFILE, ">$file_path" ) or $errormessage = "对不起，打开写入上传文件失败！";
		binmode UPLOADFILE;
			print UPLOADFILE $content;
		close UPLOADFILE;

		$flag = `sudo /usr/local/bin/logs_import.py  -t $logType -f $file_path`;
		$flag =~ s/\n//g;
		$flag =~ s/\r//g;

		if($flag eq 'OK') {
			$notemessage = "导入日志成功!";
			my $log_message = "导入了日志";
			&user_log($log_message);
		}
		elsif($flag eq 'NO_DATA') {
			$notemessage = "导入的文件中没有日志，无须导入";
		}
		else {
			$errormessage = "导入日志失败，请检查文件格式!";
		}	
		system("rm -f $file_path");
		return ($errormessage,$notemessage);


	}
}
###添加日志导入功能asynchronous by leo 2016-12-14
sub importLog_asynchronous($$) {
	my $par = shift;
	my $logType = shift;
	my $cgi = new CGI;
	my $file_name = $cgi->param('upload_file');
	my $ACTION = $par->{'ACTION'};
	
	if ($ACTION eq "importLog") {
		
		my $file_path = `mktemp -p /tmp`;
		my $content = '';
		while ( <$file_name> )
		{
			$content .= $_;
		}
		$content = &log_encrypt('de',$logType,$content);
		
		open ( UPLOADFILE, ">$file_path" ) or $errormessage = "对不起，打开写入上传文件失败！";
		binmode UPLOADFILE;
			print UPLOADFILE $content;
		close UPLOADFILE;

		my $flag = `sudo /usr/local/bin/import_mysql_log.py -t $logType -f $file_path`;

		if($flag =~ /0/) {
			$notemessage = "导入日志成功!";
			my $log_message = "导入了日志";
			&user_log($log_message);
		}else {
			$errormessage = "导入的日志文件内容有误，请检查!";
		}
		system("rm -f $file_path");
		return ($errormessage,$notemessage);
	}
}
###添加日志清空功能 by leo 2016-1-16
sub clearLog($$) {
	my $par = shift;
	my $file = shift;
	my $ACTION = $par->{'ACTION'};
	if($ACTION eq 'clearLog') {
		system("rm /var/log/'$file' -f");
		system("rm /var/log/'$file'-*.gz -f");
	}
}


###添加日志清空功能 by leo 2016-1-16
sub clearLog_in_dataBase($$) {
	my $par = shift;
	my $name = shift;
	my $ACTION = $par->{'ACTION'};
	if($ACTION eq 'clearLog') {
		`sudo /usr/local/bin/filter_log.py -c $name`;
	}
}

###添加日志导入功能面板asynchronous by leo 2016-12-14
sub importLogPanel_asynchronous() {
	&openeditorbox("导入日志","2","3","4");
	printf <<EOF
		<div class="importlog-content">
			<div class="importlog-left">
				<span>选择日志文件</span>
			</div>
			<div class="importlog-right">
				<a href="javascript:;" class="file">选择文件
					<input type="file" name="upload_file" id="upload_file">
				</a>
				<label id="upload_file_tip">未选择日志文件</label>
			</div>
		</div>
		<input type="hidden" name="ACTION" value="importLog">
		<script language="JavaScript">
		!function() {
			document.getElementById("upload_file").onchange = function() {
				var str = document.getElementById("upload_file").value;
				if(str == "") {
					document.getElementById("upload_file_tip").innerText = "未选择日志文件";
				}else {
					var arr = str.split("\\\\");
					document.getElementById("upload_file_tip").innerText = arr.pop();
				}
			}
		}();
		
		</script> 
EOF
;
	&closeeditorbox("导入","取消","7","8","9");
	
	
}
###下载日志by leo 2016-12-14
sub down_log($$$) {
	my $json = new JSON::XS;
	my $par = shift;
	my $type = shift;
	my $name = shift;
	my $conf_dir = '/home/httpd/html/log';

	my $start_time = $par->{'start_time'};
	my $start_hour = $par->{'start_hour'};
	my $start_min = $par->{'start_min'};	

	my $end_time = $par->{'end_time'};
	my $end_hour = $par->{'end_hour'};
	my $end_min = $par->{'end_min'};

	my $st= '"'.$start_time.' '.$start_hour.':'.$start_min.'"';
	my $et= '"'.$end_time.' '.$end_hour.':'.$end_min.'"';

	my $today = &GetDate(time);
	$today =~ s/\-//g;

	$errormessage_default = '暂无相关日志信息';
	my $time;
	my $file;
	my $path;
	my $ext = '.dat';
	my $status;
	if ($start_time eq '' && $end_time eq '') {
		$time = $today;
		$file = $name . '_' . $time .$ext;
		$path = $conf_dir . $file;
		$status = `sudo /usr/local/bin/filter_log.py -E $type -p $path`;
	}
	elsif ($start_time eq '') {
		if ($end_min eq '59') {
			$et= '"'.$end_time.' '.$end_hour.':'.$end_min.':'.'59'.'"';
		}
		$end_time =~ s/\-//g;
		$time = '*'.'-'.$end_time.$end_hour.$end_min;
		$file = $name . '_' . $time .$ext;
		$path = $conf_dir . $file;
		$status = `sudo /usr/local/bin/filter_log.py -E $type -e $et -p $path`;
	} 
	elsif ($end_time eq '') {
		$start_time =~ s/\-//g;
		$time = $start_time.$start_hour.$start_min.'-'.'*';
		$file = $name . '_' . $time . $ext;
		$path = $conf_dir . $file;
		$status = `sudo /usr/local/bin/filter_log.py -E $type -f $st -p $path`;
	}
	else {
		if ($end_min eq '59') {
			$et= '"'.$end_time.' '.$end_hour.':'.$end_min.":".'59'.'"';
		}
		$start_time =~ s/\-//g;
		$end_time =~ s/\-//g;
		$time = $start_time.$start_hour.$start_min.'-'.$end_time.$end_hour.$end_min;
		$file =  $name . '_' . $time . $ext;
		$path = $conf_dir . $file;
		$status = `sudo /usr/local/bin/filter_log.py -E $type -f $st -e $et -p $path`;
	}
	if( $status =~ /0/ ) {
  		$notemessage = '导出日志成功!';
    	}else {
        	$errormessage = '导出日志失败!';
		return ($errormessage, $notemessage);
	}

	my $str;
	if( -s "$path"){			
			if($file =~ /\.gz/){
				$str = `zcat '$path'`;
			}else{
				$str = &read_file("$path");
			}
			&debug2file($str);
			$str = &log_encrypt('en',$type,$str);
			print "Content-Type:application/x-download\n";  
			print "Content-Disposition:attachment;filename='$file'\n\n";
			print $str;
			exit;
	}
	else{
		$errormessage = $errormessage_default;
	}
	if ($errormessage) {$notemessage = ''};
 	return ($errormessage, $notemessage);
}

#读取公钥
sub readPublicKey(){
	my $str;
	my $publicKeyFile = '/var/efw/webkey/pub.pem';
	open( FILE , $publicKeyFile );
	while( <FILE> ){
		
		$str .= $_;
	}
	chomp($str);
	return $str;
}

#使用私钥解密
sub decryptFn($){
	my $key = shift;
	my $privateKeyFile = '/var/efw/webkey/key.pem';
	my $result;
	my $cmd_str = "echo  '$key'  | sudo base64 -d  |sudo openssl rsautl -inkey $privateKeyFile -decrypt";
	$result = `$cmd_str`;
	return $result;
}

sub GetDate($) {
    my $now = shift;
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($now);
    $year += 1900;
    $mon++;
    return sprintf("%04d-%02d-%02d", $year, $mon, $mday);
}
1;
sub validateUser()
{
	# pengtian
	# 用于用户名验证，不要修改该函数名
	# 验证通过不作操作
	# 验证失败直接exit
	# 该函数需要被python cgi(validate_user.py)或者perl cgi调用
	my @cur_user = &getCurUser();
	my $auth = &judge_authrize( $ENV{'SCRIPT_NAME'}, $cur_user[0] );
	
	if ($auth == $AUTH_PROMISE || $auth == $AUTH_WHITE_LIST){
		return 0;
	}else{
		print "Pragma: no-cache\n";
		print "CapsheafAuth: fail\n";
		print "Cache-control: no-cache\n";
		print "Connection: close\n";
		print "\n";
		exit 1;
	}
}
sub get_log_aes_key($){
	my $log_type = shift;
	my %log_type_hash = (
		# 文件类型
		# 本机安全事件
		'eventwarn.log'   =>  'logs_event',
		'系统告警'   =>  'logs_event',

		'network.log_new'   =>  'logs_action',
		'系统操作'   =>  'logs_action',

		'useroptions'   =>  'logs_user_audit',
		'用户审计'   =>  'logs_user_audit',

		'firewall'   =>  'logs_firewall',
		'防火墙'   =>  'logs_firewall',

		# 'logs_firewall_report'   =>  'logs_firewall_report',

		'ddosflood'   =>  'logs_ddosflood',
		'DDOS防护'   =>  'logs_ddosflood',

		'ipmac'   =>  'logs_ipmac',
		'IP盗用发现'   =>  'logs_ipmac',

		'logs_portscan'   =>  'logs_portscan',

		'connctrl'   =>  'logs_connctrl',
		'连接控制'   =>  'logs_connctrl',

		# 'logs_real_time_events'   =>  'logs_real_time_events',
		# 'logs_history_events'   =>  'logs_history_events',
		# 'logs_user'   =>  'logs_user',
		# 'logs_backup'   =>  'logs_backup',

		'userlogin'   =>  'logs_user_secretauth',
		'用户登录/注销'   =>  'logs_user_secretauth',

		'appctrl'   =>  'logs_appctrl',
		'应用控制'   =>  'logs_appctrl',

		# 数据库类型
	
		'urlfilter_log'   =>  'url_log',
		'filetypefilter_log'   =>  'filter_log',
		'webdefend_log'   =>  'web_log',
		'virus_log'   =>  'virus_log',
		'keywordfilter_log'   =>  'keywordfilter_log',
		'botnet_log'   =>  'botnet_log'
	);
	my $log_key = `cat /var/efw/log_key/log_key`;
	if ($log_type_hash{$log_type}) {
		return $log_type_hash{$log_type}.$log_key;
	}else{
		return '';
	}
	
}

sub log_encrypt($$$){
	my $enOrde=shift;
	my $type=shift;
	my $log=shift;
	my $key = &get_log_aes_key($type);
	$cipher = Crypt::CBC->new(
		-key    => $key,
		-cipher => "Crypt::OpenSSL::AES"
	);
	if ($enOrde eq 'en') {
		return $cipher->encrypt($log);
	}else{
		return $cipher->decrypt($log);
	}
}

sub read_file($) {
	my $file = shift;
	my $content = '';
	open FILE,"$file" or die $!;
	{
	        $content = do { local $/=undef; <FILE>; };
	        # local $/=undef;
	        # $content= <FILE>;
	        # close FILE;
	}
	return $content;

}