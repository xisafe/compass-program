#!/usr/bin/perl
#!/usr/bin/perl

#file:devices.cgi
#author:zhangzheng

require '/var/efw/header.pl';
require 'ip_mac_binding.pl';

use CGI::Carp qw (fatalsToBrowser);
use CGI qw(:standard);
use Encode;
my $cgi= new CGI; 
my $setting_file = "/var/efw/ip-mac/settings";
my $tmp_file = "/var/efw/ip-mac/";
my $download_file = "/var/efw/ip-mac/download";
my $scan_file = "/var/efw/ip-mac/scanedip";
my $data_file = "/var/efw/ip-mac/arptables";
my $needreload = "/var/efw/ip-mac/needreload";
my $extraheader="";
my %par;
my @errormessages=();

# add by squall: for validate bridges
my $ETHERNET_SETTINGS = "/var/efw/ethernet/settings";
# end -------------------------------

my $EDIT_PNG="/images/edit.png";
my $DISABLED_PNG = "/images/off.png";
my $ENABLED_PNG = "/images/on.png";
my $DELETE_PNG="/images/delete.png";
my $offset = 1; 
$reload=0;
my $line_num = "";
my $errormessage = "";
my $notemessage = "";

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
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'IPMAC_FORM',
       'option'   :{
                    'ip_value':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'mac_value':{
                               'type':'text',
                               'required':'1',
                               'check':'mac|',
                             },
                    'notice':{
                               'type':'text',
                               'required':'0',
                               'check':'note|',
                             },
                 }
         }
	var object2 = {
       'form_name':'IPMAC_FORM_2',
       'option'   :{
                    'scan_ip':{
                               'type':'text',
                               'required':'1',
							   'check':'other|',
							   'other_reg':'!/^\$/',
							   'ass_check':function(eve){
                                                        var msg = "";
                                                        var ips = eve._getCURElementsByName("scan_ip","input","IPMAC_FORM_2")[0].value;
														var ip =   /^([1-9]|[1-9]\\d|1\\d{2}|2[0-1]\\d|22[0-3])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3}\$/;
														var temp = ips.split("-");
														var ip1 = temp[0];
													
														if(!ip.test(ip1)){
															return ip1 + "是不合法的ip地址";
														}
														
														if(temp.length < 2){
															return "两个ip地址用'-'隔开";
														}
														var ip2 = temp[1];
														if(!ip.test(ip2)){
															return ip2 + "是不合法的ip地址";
														}
														
														//检查ip是哪一类IP地址--A,B,C
														var splitip1 = ip1.split("\\.");
														var splitip2 = ip2.split("\\.");
														//想填写A类地址
														if(splitip1[0] >= 1 && splitip1[0] <= 126){
															if(splitip1[0] != splitip2[0]){
																return ip1 + "和" + ip2 + "不在同一个网段";
															}
															if(parseInt(splitip1[1]) > parseInt(splitip2[1])){
																return "'-'后面的地址不能小于'-'前面的地址";
															}
														}
														
														//想填写B类地址
														else if(splitip1[0] >= 128 && splitip1[0] <= 191){
															if(splitip1[0] != splitip2[0] || splitip1[1] != splitip2[1]){
																return ip1 + "和" + ip2 + "不在同一个网段";
															}
															if(parseInt(splitip1[2]) > parseInt(splitip2[2])){
																return "'-'后面的地址不能小于'-'前面的地址";
															}
														}
														
														//想填写C类地址
														else if(splitip1[0] >= 192 && splitip1[0] <= 223){
															if(splitip1[0] == splitip2[0] && splitip1[1] == splitip2[1] && splitip1[2] == splitip2[2]){
																if(parseInt(splitip1[3]) > parseInt(splitip2[3])){
																	return "'-'后面的地址不能小于'-'前面的地址";
																}
															}else{
																return ip1 + "和" + ip2 + "不在同一个网段";
															}
														}
														
														else{
															//不在ABC地址范围内
															return ip1 + "是不合法的ip地址";
														}
														
														//检查所填写的地址是否在设置的绿口橙口设置的地址范围内
														//先获取配置
														if(!eve.settings){
                                                            \$.ajax({
                                                                  type : "get",
                                                                  url : '/cgi-bin/chinark_back_get.cgi',
                                                                  async : false,
                                                                  data : 'path=/var/efw/ethernet/settings',
                                                                  success : function(data){ 
                                                                    eve.settings = data;                                                                     
                                                                  }
                                                            });
                                                        }
														var exist = eve.settings.split('\\n');
														var green_ips = "";
														var orange_ips = "";
														for (var i = 0; i < exist.length; i++) {
                                                            var tmp = exist[i].split('=');
                                                            if(tmp[0] == 'GREEN_IPS'){
                                                                green_ips = tmp[1];
                                                            }
															if(tmp[0] == 'ORANGE_IPS'){
                                                                orange_ips = tmp[1];
                                                            }
                                                        }
														
														//再检查地址段是否在此两个区域段内,如果两个地址都没有设置，直接返回
														if(green_ips == "" && orange_ips == ""){
															return;
														}
														
														var config_ips = "";
														if(green_ips != ""){
															config_ips = green_ips;
														}
														if(orange_ips != ""){
															if(config_ips != ""){
																config_ips = config_ips + "," + orange_ips;
															}else{
																config_ips = orange_ips;
															}
														}
														
														
														var OKflag = false;
														var config_ip_array = config_ips.split(',');
														var i = 0;
														for( i = 0; i < config_ip_array.length; i++ ){
															var config_ips_splitted = config_ip_array[i].split('\/');
															var config_ips_section = config_ips_splitted[0].split("\\.");
															if(config_ips_splitted[1] == '8'){
																//检查第一位是否相同
																if(config_ips_section[0] == splitip1[0]){
																	OKflag = true;
																}
																
															}else if(config_ips_splitted[1] == '16'){
																//检查前两位位是否相同
																if(config_ips_section[0] == splitip1[0] && config_ips_section[1] == splitip1[1]){
																	OKflag = true;
																}
															}else if(config_ips_splitted[1] == '24'){
																//检查前三位是否相同
																if(config_ips_section[0] == splitip1[0] && config_ips_section[1] == splitip1[1] && config_ips_section[2] == splitip1[2]){
																	OKflag = true;
																}
															}else{
																//如果掩码为空或者为其他数字怎么处理？？？--by wl 2013.10.30 --暂时不处理，只要橙口绿口有一个不为空，就应该检查是否在该范围内
															}
														}
														
														if(OKflag == false){
															return "所填地址段不在LAN区"+green_ips+"子网内，也不在DMZ区"+orange_ips+"子网内，请重新填写";
														}
														
                                }
                    },
            }
        }
    var check = new ChinArk_forms();
    check._main(object);
    check._main(object2);
    //check._get_form_obj_table("IPMAC_FORM");
    </script>
EOF
;
}
sub save() {
    my $action = $par{'ACTION'};
	$line_num  = $par{'line'};
    my $sure = $par{'sure'};
    if ($par{'OFFSET'} =~ /^\d+$/) {
		$offset = $par{'OFFSET'};
	}
	if ($action eq "global_save") {
		save_global($par{'access'},$par{'type'});
		%par="";
	}
	if ($action eq "binding_save" || $action eq "modify") {
		if(save_binding($par{'ip_value'},$par{'mac_value'},$par{'iface'},$par{'enabled'},$par{'notice'},$par{'line'}))
		{
			$notemessage = "IP/MAC绑定规则已成功添加!";
			%par="";
		}
	}
	if ($action eq 'delete') {
		delete_line($par{'line'});
	}
	if ($action eq 'on') {
		toggle_line($par{'line'},'off');
	}
	if ($action eq 'off') {
		toggle_line($par{'line'},'on');
	}
	if ($action eq 'upload') {
		$uploadname='temp';
		$dir = "/tmp";
		uploads($uploadname,$dir);
		%par="";
	}
	if ($action eq "apply") {
		 `rm $needreload`;
		system("sudo /usr/local/bin/ipscan.sh");
		$notemessage = "IP/MAC绑定规则已成功应用!";
	}
	copy_down();
}
sub copy_down(){
	open(FILE3,">$download_file");
	foreach my $line (read_config_file($data_file)) {
		my @temp = split(/,/,$line);
		print FILE3 $line."\n";
	}		
	close(FILE3);
	`sudo fmodify $download_file`;
}
###上传文件添加
sub fileparse{
	my $para = shift;
	my @parse = split(/\./,$para);
	my $extension = $parse[@parse-1];
	pop(@parse);
	my $name = join('.',@parse);
	return ($name, $extension);
}
sub down_file(){
	if ($par{'ACTION'} eq 'download') {
		my $file = $data_file;
		if( -e "$file"){
			open(DLFILE, "<$file") || Error('open', "$file");  
			@fileholder = <DLFILE>;  
			close (DLFILE) || Error ('close', "$file"); 
			print "Content-Type:application/x-download\n";  
			print "Content-Disposition:attachment;filename=$file\n\n";
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



sub uploads{
	my $uploadname = shift;
	my $upload_dir = shift;
=p
    #文件名合法的字符
	my $safe_filename_characters = "a-zA-Z0-9_.-";
    #文件保存的路径

	my $filename = $cgi->param($uploadname);
	my ( $name, $extension ) = fileparse ($filename);
    
	###end
	
		$filename = $name . $extension;
		$filename =~ tr/ /_/;
		$filename =~ s/[^$safe_filename_characters]//g;
		printf <<EOF
 <script>
 alert("$uploadname"); 
 </script>
EOF
;

		if ( $filename =~ /^([$safe_filename_characters]+)$/ )
		{
			$filename = $1;
		}
		else
		{
			die "Filename contains invalid characters";
		}

		#创建文件上传句柄
		my $upload_filehandle = $cgi->upload($uploadname);
		if (!$upload_filehandle) {
			print $cgi->header(-status=>$cgi->cgi_error);
			exit 0;
		}

		if($extension){
			$filename=$upload_dir.$name.".".$extension;
		}else{
			$filename=$upload_dir.$name;
		}
=cut
		my $upload_filehandle = $cgi->upload('upload_file');
		my $filename = "/tmp/temp";
		open ( UPLOADFILE, ">$filename" ) or die "$!";
		binmode UPLOADFILE;
		while ( <$upload_filehandle> )
		{
			print UPLOADFILE;
		}

		close UPLOADFILE;
		write_correct($filename);
		#return $filename;
}

# --------------------------
# added by squall 2013-05-24
# --------------------------
sub get_ethernets($) {
	my $setting_file = shift;
	my @bridges = ();

	open (FILE, $setting_file);
	while ( <FILE> ) {
		my $line = $_;
		chomp($line);
		if ( $line =~ /_DEV=(\w*)/ ) {
			push(@bridges,$1);
		}
	}
	close FILE;

	return @bridges;
}

# -----------------------------
# modified by squall 2013-05-24
# -----------------------------
sub write_correct($){
	my $filename = shift;
	my @lines =  read_config_file($data_file);
	my $line;
	my @ethernets = get_ethernets($ETHERNET_SETTINGS);
	my @temp = filter_upload($filename);
	foreach my $elem (@temp) {
		# ip,mac,if,comment,enabled
		my @temp=split(/,/,$elem);
		$temp[0] =~ s/\s//g;
		$temp[1] =~ s/\s//g;
		# 将mac地址转为小写
		$temp[1] = lc($temp[1]);
		if (validmac($temp[1]) && validip($temp[0]))
		{
			if(!filter_repeat($temp[0],$temp[1],$data_file)){
				# ip , mac
				if ($#temp == 1) {
					$line = "$temp[0],$temp[1],br0,,on";
					push(@lines,$line);
				}
				# ip , mac , br , comment , enabled
				elsif ($#temp == 4) {
					my $is_valid_bridge = 0;
					# check whether bridge is valid
					foreach my $brx (@ethernets) {
						if ( $temp[2] eq $brx ) {
							$is_valid_bridge++;
						}
					}
					if ( $is_valid_bridge == 0 ) {
						next;
					}
					# ensure length of comment is less than 50 chars
					Encode::_utf8_on($temp[3]);
					if ( length($temp[3]) > 50 ) {
						$temp[3] = substr($temp[3],0,50);
					}
					# check whether enabled field is valid
					if ( $temp[4] eq "on" or $temp[4] eq "off") {
						$line = "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4]";
						push(@lines,$line);
					}
				}

			}
		}
	}
	save_config_file(\@lines,$data_file);
	system("touch $needreload");
	system("rm $uploaddir/tmp")
	&copy_down();
}

sub filter_upload($)
{
	my $file  = shift;
	my @lines = read_config_file($file);
	my @temp;
	my %exist;
	foreach my $line(@lines)
	{
		my @temp_new = split(",",$line);
		if ($exist{$temp_new[0]}){
			next;
		}
		else{
			push(@temp,$line);
			$exist{$temp_new[0]} = 1;
		}
	}
	return @temp;
}

sub filter_repeat($$$)
{
	my $ip = shift;
	my $mac = shift;
	my $file = shift;
	my @lines =  read_config_file($file);
	my $count =0;
	foreach my $line(@lines)
	{
		my @temp = split(",",$line); 
		if ($temp[0] eq $ip or $temp[1] eq $mac) {
			$count++;
			last
		}
	}
	return $count;
}

###保存手动添加配置
sub save_binding($$$$$$){
	my $ip = shift;
	my $mac = shift;
	$mac = lc($mac);#统一转成小写存储2013.12.19 by wl
	my $iface = shift;
	my $enabled = shift;
	my $notice = shift;
	my $line_num = shift;
	$mac =~s/-/:/g;
	if (!check_values($ip,$mac,$line_num)) {
		return 0;
	}
	if (!$enabled) {
		$enabled = "off";
	}
	$notice =~s/,/，/g;
	my @lines = read_config_file($data_file);	
	my $line = "$ip,$mac,$iface,$notice,$enabled";
	if ($par{'ACTION'} eq "binding_save") {		
		push (@lines,$line);
	}
	else{
		$lines[$line_num]=$line;
	}
	save_config_file(\@lines,$data_file);
	system("touch $needreload");
	&copy_down();
	return 1;
}
###保存全局配置
sub save_global($$){
	my $access = shift;
	my $type = shift ;
	my %save;
	$save{'access'} = $access;
	$save{'type'} = $type;
	&writehash($setting_file,\%save);
	`sudo fmodify $setting_file`;
	`sudo fmodify $setting_file`;
	system("touch $needreload");
}
###删除绑定
sub delete_line($){
	my $line = shift;
	my @save_lines;
	my @lines = read_config_file($data_file);
	for (my $i = 0;$i<@lines ;$i++) {
		if ($i ne $line) {
			push(@save_lines,$lines[$i]);
		}
	}
	save_config_file(\@save_lines,$data_file);
	system("touch $needreload");
	&copy_down();
}
sub toggle_line($$){
	my $line = shift;
	my $enable = shift;
	my @lines = read_config_file($data_file);
	if ($enable eq 'on') {
		$lines[$line] =~s/off$/on/;
	}
	else{
		$lines[$line] =~s/on$/off/;
	}
	save_config_file(\@lines,$data_file);
	system("touch $needreload");
	&copy_down();
}
###检查数据合法性
sub check_values($$$){
	my $ip = shift;
	my $mac = shift;
	my $line_num = shift;
	if (!$ip) {
		$errormessage="IP地址不能为空!";
		return 0;
	}
	if (!&is_ipaddress($ip)) {
		$errormessage="无效的IP地址$ip!";
		return 0;
	}
	if (!$mac) {
		$errormessage="MAC地址不能为空!";
		return 0;
	}
	if (!&validmac($mac)) {
		$errormessage="无效的MAC地址$mac!";
		return 0;
	}
	
	
	my @file_lines =  read_config_file($data_file);
	my $is_used = 0;
	my $used_ip = 0;
	my $used_mac = 0;
	my $i = 0;
	foreach my $line(@file_lines)
	{
		my @temp = split(",",$line);
		if(($temp[0] eq $ip or $temp[1] eq $mac) && $line_num ne $i)
		{
			if($temp[0] eq $ip) {
				$used_ip++;
			}
			if($temp[1] eq $mac) {
				$used_mac++;
			}
			$is_used++;
		}
		$i++;
	}

		if ($is_used) {
			my $str_ip = $used_ip?"IP":"";
			my $str_mac = $used_mac?"MAC":"";
			$errormessage="此$str_ip $str_mac地址已经在绑定列表!";
			return 0;
		}
	
	return 1;
}
###全局配置选项卡
sub display_golbal() {
	my %golbal_setting;
	my %checked;
	my $show="";
	readhash($setting_file,\%golbal_setting);
	my $access = $golbal_setting{'access'};
	my $type = $golbal_setting{'type'};
	$checked{$access} = "checked";
	$checked{$type} = "checked";
	openaddbox("全局配置", "全局配置", $show, "Globle", @errormessages);
	printf <<EOF
     <table width="100%" cellpadding="0" cellspacing="0">
	 <tr class="odd">
	 <td rowspan="2" class="add-div-type">访问控制</td>	 
	 <td><input name="access" type="radio" value="allow" $checked{"allow"} />允许绑定以外的IP/MAC访问</td>
	 </tr>
	 <tr class="env">
	 <td><input name="access" type="radio" value="deny" $checked{"deny"}/>禁止绑定以外的IP/MAC访问</td>
	 </tr>
	 <tr class="odd">
	 <td class="add-div-type">绑定类型</td>	 
	 <td><input name="type" type="radio" value="ip-mac" $checked{"ip-mac"}/>IP-MAC-接口</td>
	 </tr>
	 </table>
	<input type="hidden" name="ACTION" value="global_save">
	<input type="text" id="urlvalue" value="$url_value" style="display:none">
EOF
;
	&closeaddbox("保存", _("Cancel"), "routebutton", "createdevice", "$ENV{SCRIPT_NAME}");
}
##添加选项卡
sub  display_add(){
	my $show="";
	my $url = "https://".$ENV{'SERVER_ADDR'}.":10443".'/cgi-bin/ipmac_post.cgi';
	openotherbox("添加IP/MAC绑定", "添加IP/MAC绑定", $show, "Globle", @errormessages);
	printf <<EOF
	</form>
	<form method='post' name="IPMAC_FORM_2" enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}' >
     <table width="100%" cellpadding="0" cellspacing="0">
	 <tr class="odd">
		<td class="add-div-type">IP/MAC扫描</td>
		<td><select id="method_select" style="width:130px" onchange="add_method('unknown')">
			<option value="scan_iface">按接口扫描</option>
			<option value="scan_ip">按IP扫描</option>
		</select></td>
		<td>
			<select id="scan_select" name="iface" style="width:130px">
				<option value="br0">%s区域</option>
EOF
,_('GREEN')
;
		if (&orange_used()) {
			printf <<EOF
			<option value='br1'>%s区域</option>
EOF
,_('ORANGE')
;
		}
	printf <<EOF
			</select>
			<input name="scan_ip" id="in_ip" size="35" type="text" value=""/>
			<input type='button' value='扫描' onclick="goto_scan(0,0,0)" />
			<span id="note_message">请输入IP地址段</span>
		</td>
     </tr>
	 <tr class="odd"><td class="add-div-type">导入</td>
	 <td>导入IP/MAC绑定文件</td>
	 <td>
	 <!--
	<div id="file-uploader"  style="display:block;float:left;">               
	</div>
	<script>
		var uploader = new qq.FileUploader({
			element: document.getElementById('file-uploader'),
			allowedExtensions: ['txt',''], 
			action:'$url',
			debug:false,
			onSubmit: function(id, fileName){},
			onProgress: function(id, fileName, loaded, total){},
			onComplete: function(id, fileName, responseJSON){alert("文件上传成功");document.location.href="/cgi-bin/ip_mac_binding.cgi";},
			onCancel: function(id, fileName){},
			showMessage: function(message){ alert(message); }
		});
	</script>
	 <a href="#" onclick='location.href = "/cgi-bin/download.cgi";' style="display:block;float:left;margin-top:30px;">下载文件模板 </a>
	 -->
	 <input type="file" name="upload_file" />
	 <input type="submit" name="submit" value="上传" />
	 <a href="#" onclick='location.href = "/cgi-bin/download.cgi";' >下载文件模板 </a>
	 <input type='hidden' name='ACTION' value='upload'>
	 </td>
	 </tr>
	 <tr class="env"><td class="add-div-type">手动添加IP/MAC绑定</td>
	 <td colspan="2"><input name="method" type="radio" value="input" onclick="add_method('manual');" />输入IP及MAC以绑定</td></tr>
	 </table>
EOF
;
	&closeotherbox("保存", _("Cancel"), "routebutton", "createdevice", "$ENV{SCRIPT_NAME}");
}
###手动添加或编辑选项卡
sub  display_assitant($$){
	my $is_editing = shift;
    my $line = shift;
	my $checked="";
	my $ip_value,$mac_value,$iface,$notice,$enabled; 
	$selected{"br0"} = "selected";
	my @lines = read_config_file($data_file);
	my @temp = split(/,/,$lines[$line]);
	if($par{'ACTION'} eq "edit"){
		$ip_value = $temp[0];
		$mac_value = $temp[1];
		$iface = $temp[2];
		$notice = $temp[3];
		$enabled = $temp[4];
	}
	else  {
	   $ip_value = $par{'ip_value'};
	   $mac_value = $par{'mac_value'};
	   $iface = $par{'iface'};
	   $notice = $par{'notice'};
	   $enabled = $par{'enabled'};
	}
	if ($iface eq "br1") {
		$selected{"br1"} = "selected";
	}
	if ($enabled eq "on") {
		$checked="checked";
	}
	my $action = 'binding_save';
	if ($par{'ACTION'}) {
		$action = $par{'ACTION'};
	}
    my $title = _('手动添加');
	my $buttontext=_("Add");
    if ($is_editing || $action eq "modify") {
        $action = 'modify';
        $title = _('编辑');
		$buttontext = _("Edit");
    }else{
		$action = 'binding_save';
	}
	if($par{'ACTION'} eq 'edit' || $errormessage ne '') {
        $show = "showeditor";
    }
	if ($errormessage eq '文件后缀名错误，只能上传TXT文件!') {
		$show = "";
	}
	print "<div id='manual_id' style='display:none'>";
	openeditorbox("$title", "$title", $show, "Globle", @errormessages);
	printf <<EOF
	</form>
	<form method='post' name="IPMAC_FORM" enctype='multipart/form-data' action='$ENV{'SCRIPT_NAME'}'>
     <table width="100%" cellpadding="0" cellspacing="0">
	 <tr class="odd">
		<td class="add-div-type">IP *</td>
		<td><input name="ip_value" type="text" value="$ip_value" /></td>
	 </tr>
	 <tr class="env">
		<td class="add-div-type">MAC *</td>
		<td><input name="mac_value" type="text" value="$mac_value" /></td>
	 </tr>
	 <tr class="odd">
		<td class="add-div-type">接口 *</td>
		<td>
			<select name="iface" style="width:130px">
				<option value="br0" $selected{'br0'}>%s区域</option>
EOF
,_('GREEN')
;
		if (&orange_used()) {
			printf <<EOF
			<option value='br1' $selected{'br1'}>%s区域</option>;
EOF
,_('ORANGE')
;
		}
	printf <<EOF
			</select>
		</td>
	 </tr>
	 <tr class="env">
		<td class="add-div-type">启用 </td>
		<td><input type="checkbox" name="enabled" $checked/></td>
	 </tr>
	 <tr class="odd">
		<td class="add-div-type" >备注</td>
		<td><input name="notice" type="text" value="$notice" /></td>
	 </tr>
	 </table>
	 <input type="hidden" name="ACTION" value="$action">
	 <INPUT TYPE="hidden" NAME="line" VALUE="$line_num">
	 <input TYPE="hidden" NAME="OFFSET" value="$offset">
EOF
;
	&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createdevice", "$ENV{SCRIPT_NAME}");
	print "</div>";
}
sub display_devices($$) {
    my $is_editing = shift;
    my $line = shift;
	my $enabled_gif = "/images/off.png";
	my $enabled_alt = _('Disabled (click to enable)');
    #&openbox('100%', 'left', _('Dynamic DNS'));
	display_golbal();
    display_add();
	display_assitant($is_editing, $line);
	my $num = 0;

#显示已有数据，即IP/MAC绑定对
	if ($offset < 1) {
		$offset = 1;
	}
	my $total_num = `cat $data_file |wc -l`;
	my $total = POSIX::ceil($total_num/10);
	if ($offset > $total) {
		$offset = $total;
	}
    my $next = $offset + 1;
	my $last = $offset - 1;
	my $num = 0;
	$num = $num + $last*10;
	if ($num < 0) {
		$num = 0;
	}
	my $start = ($offset-1) * 10;
	my $last_num = $total_num - $start;
	my $temp = `cat $data_file |tail -n $last_num | head -10`;
	my @dis = split(/\n/,$temp);
	my $ip,$mac,$iface,$notice;
    printf <<END
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr>
            <td class="boldbase" style="width:10%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>
			<td class="boldbase" style="width:20%;">%s</td>
			<td class="boldbase" style="width:10%;">%s</td>
        </tr>
	
END
	, _('IP')
	, _('MAC')
    , _('接口')
    , _('备注')
	,_('活动/动作')
;
		
		foreach my $line_elem (@dis) {
			my @elem = split(/,/,$line_elem);
			my $enabled_status = $elem[4];	
			$iface = _('GREEN')."区域";
			my $pic = $ENABLED_PNG;
			my $pic_alt = _('Enabled (click to disable)');
			if ($num % 2) {
				print "<tr class='env'>";
			}
			else{print "<tr class='odd'>";}
			if ($elem[2] eq "br1") {
				$iface = _('ORANGE')."区域";
			}
			if ($elem[4] eq "off") {
				$pic = $DISABLED_PNG;
				$pic_alt = _('Disabled (click to enable)');
			}
			printf <<EOF
			<td>$elem[0]</td>
            <td>$elem[1]</td>
            <td>$iface</td>
			<td>$elem[3]</td>
			<td>
			<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                <input class='imagebutton' type='image' NAME="submit" SRC="$pic" ALT="$pic_alt" />
				<input TYPE="hidden" NAME="OFFSET" value="$offset">
                <INPUT TYPE="hidden" NAME="ACTION" VALUE="$enabled_status">
                <INPUT TYPE="hidden" NAME="line" VALUE="$num">
            </form>
            <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                 <input class='imagebutton' type='image' NAME="submit" SRC="$EDIT_PNG" ALT="%s" />
                 <INPUT TYPE="hidden" NAME="ACTION" VALUE="edit">
				 <input type="hidden" name="OFFSET" value="$offset">
                 <INPUT TYPE="hidden" NAME="line" VALUE="$num">
             </form>
             <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                 <input class='imagebutton' type='image' NAME="submit" SRC="$DELETE_PNG" ALT="%s" />
                 <INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
				 <input type="hidden" name="OFFSET" value="$offset">
                 <INPUT TYPE="hidden" NAME="line" VALUE="$num">
             </form>
			</td>
			</tr>
EOF
    ,_('Edit')
	,_('Remove')
;
			$num ++;
		}
		if ($num == 0) {
			no_tr(5,_('Current no content'));
		}

if($num != 0)
{
			printf <<EOF
		
		<table class="list-legend" cellpadding="0" cellspacing="0">
		  <tr>
			<td class="boldbase">
			  <B>%s:</B>
			<IMG SRC="$ENABLED_PNG" title="%s" />
			%s
			<IMG SRC='$DISABLED_PNG' title="%s" />
			%s
			<IMG SRC="$EDIT_PNG" title="%s" />
			%s
			<IMG SRC="$DELETE_PNG" title="%s" />
			%s</td>
			<td>
EOF
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')
;

###跳转以及上下页翻页

printf <<END
		<div>
<table width='100%' align='center' border="0">
	<tr>
	<td width='2%' align='right'>
END
;
	if ($last > 0 ) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="OFFSET" value="1">
    <input class='submitbutton' type="image" title='%s' name="ACTION" src="/images/first-page.png">
	</form>
END
,
_('First page')
;
    } else {

	print "<input class='submitbutton' type='image' name='ACTION' title='"._('First page')."' src='/images/first-page-off.png'>";
    }
    print "</td><td width='2%'>\n";
	if ($last > 0) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$last">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/last-page.png">
	</form>
END
,
_('Last page')
;
    }
	else {

	print "<input class='submitbutton' type='image' name='ACTION' title='"._('Last page')."' src='/images/last-page-off.png'>";
    }
	printf <<END
		<td  align='center'>%s</td>
		<td  align='center'>%s</td>
END
,
_('Total %s pages',$total),
_('Current %s page',$offset),
;

    print "<td width='2%' align='right'>";
    if (!($next > $total)) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$next">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/next-page.png">
	</form>
END
,
_('Next page')
;
    } else {
	print "<input class='submitbutton' type='image' name='ACTION' title='"._('Next page')."' src='/images/next-page-off.png'>";
    }
	print "</td><td width='2%'>\n";
	 if (!($next > $total)) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="OFFSET" value="$total">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/end-page.png">
    </form>
END
,
_('End page')
;
    } else {
	print "<input class='submitbutton' type='image' name='ACTION' title='"._('End page')."' src='/images/end-page-off.png'>";
    }
    printf <<END
		</td>	
		<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<td  align='right' >%s: <input type="text" SIZE="2" name='OFFSET' VALUE="$offset"></td>
        <td  align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
		</form>
		<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<td align='right' ><input type="submit" value="导出全部"><input type="hidden" name='ACTION' value="download" /></td>
		</form>
</tr>
</table>
	</div>
END
,_('Jump to Page')
,_('Go')
;
###翻页END
printf <<EOF
			</td>
		  </tr>
		</table>
EOF
;
}
	#&closebox();
}


$extraheader .="<script type='text/javascript' src='/include/ip_mac_binding.js'></script><style type='text/css'>\@import url(/include/ip_mac_binding.css);</style>";
$extraheader  .= '<script language="JavaScript" src="/include/fileuploader.js"></script>';
$extraheader .= "<style type='text/css'>\@import url(/include/fileuploader.css);</style>";
&getcgihash(\%par);
down_file();
&showhttpheaders();
&openpage(_('IP/MAC绑定'), 1, $extraheader);

save();

if (-e $needreload) {
	applybox("IP/MAC绑定规则已改变并且需要被应用以使改变有效!");
}
&openbigbox($errormessage, $warnmessage, $notemessage);
my $url_value="https://".$ENV{'SERVER_ADDR'}.":10443". $ENV{'SCRIPT_NAME'};
$lineno = $par{'line'};
display_devices(($par{'ACTION'} eq 'edit'), $lineno);
if($par{'ACTION'} eq 'edit' || $errormessage ne '') {
		printf <<EOF
		<script>add_method("manual")</script>
EOF
		;
    }

&closebigbox();
&check_form();
&closepage();
