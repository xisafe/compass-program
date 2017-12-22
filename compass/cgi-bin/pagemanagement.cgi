#!/usr/bin/perl
#
# (c) 2001 Jack Beglinger <jackb_guppy@yahoo.com>
#
# (c) 2003 Dave Roberts <countzerouk@hotmail.com> - colour coded netfilter/iptables rewrite for 1.3
#
# $Id: connections.cgi,v 1.6.2.4 2004/10/07 07:24:07 eoberlander Exp $

# huangjun 2011-1-26

# Setup GREEN, ORANGE, IPCOP, VPN CIDR networks, masklengths and colours only once

require '/var/efw/header.pl';
my %par;
my $timeout = 30;  #页面超时间
my $managertimes = 10;  #管理员连续登录失败次数
my $auth_passwd = 5;   #非法用户的最大登录次数
my $psdLength = 8;
my $PASSWD_TIMEOUT = 7;
my $save_filename = '/var/efw/userinfo/user_config'; 
my $errormessage = "";
my $notemessage = "";
my $warnmessage = "";

my %usrlogincount_setting;
#判断每一行是否有空行，无效行
sub is_valid($) 
{
    my $line = shift;
    if($line =~ /(?:(?:[^,]*),){9}/) 
	{
        return 1;
    }
    return 0;
}

#读取文件信息，将每一行为列表项，返回整个列表
sub read_config_file($) {
    my $filename = shift;
    my @lines;
    open(FILE, "<$filename");
    foreach my $line (<FILE>){
		chomp($line);
		$line =~ s/[\r\n]//g;
		if(is_valid($line)){
			next;
		}
		push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

#文件的复制，前一个参数为要进行复制的文件，后一个参数为要写入的文件 
sub copy_config_file($$)
{
   my $originFile = shift;
  my $copyFile = shift;
   my @lines = read_config_file($originFile);
   open(FILE,">$copyFile");
   my $count = 0;
   my $total = scalar(@lines);
   while($count < $total)
   {
      print FILE "$lines[$count]\n";
	  $count++;
   }
   close FILE;
   return 1;
}
   


#保存信息到文件
sub save_config_file($$)
{
	my $filename = shift;
	my $tmpValue = shift;
    open(FILE, ">$filename");	
	print FILE "$tmpValue\n";
}

#对即将写入文件的数进行边界检测
sub save()
{
	my $action = $par{'ACTION'};
	my $errorValue = 0;
	my %temp_config = ();
	if($action eq 'defaultConf')
	{
		$usrlogincount_setting{'TIMEOUT'} = 30;
	    $usrlogincount_setting{'MANAGERTIME'} = 10;
	    $usrlogincount_setting{'AUTH_PASSWD'} = 5;
		$usrlogincount_setting{'PSD_LENGTH'} = 8;		
		$usrlogincount_setting{'PASSWD_TIMEOUT'} = 7;		
		&writehash($save_filename, \%usrlogincount_setting);
		$notemessage = "已经成功恢复默认配置！";
	}
	&readhash($save_filename,\%temp_config);
	$timeout      = $temp_config{'TIMEOUT'};
	$managertimes = $temp_config{'MANAGERTIME'};
	$auth_passwd  = $temp_config{'AUTH_PASSWD'};
	$psdLength    = $temp_config{'PSD_LENGTH'};
	$PASSWD_TIMEOUT = $temp_config{'PASSWD_TIMEOUT'};
	
	if($action eq 'save')
	{
		$timeout = $par{'timeout'};
		$managertimes = $par{'managertimes'};
		$auth_passwd = $par{'auth_passwd'};
		$psdLength   = $par{'psdLength'};
		$PASSWD_TIMEOUT = $par{'PASSWD_TIMEOUT'};
		if(!($timeout >= 1 && $timeout <=480  && $timeout =~/^\d+$/))
		{
			$errormessage = "请确认页面超时时间为1-480内的数";
			$errorValue = 1;
			return;
			
		}
		if(!($managertimes >=2 && $managertimes <=50  && $managertimes =~/^\d+$/))
		{
          $errormessage = "请确认管理员最大登录重复次数为2-50范围内的数！";
          $errorValue = 1;
		  
		  return;
		  
		  
		}
		if(!($auth_passwd >= 2 && $auth_passwd <=50 && $auth_passwd =~/^\d+$/))
		{   
			$errormessage = "请确认非法用户最大重复登录次数为2-50范围内的数！";
			$errorValue = 1;
  		    return;
		
		}
		# if($auth_passwd > $managertimes)
		# {
		# 	$errormessage="请确认非法用户的错误登录次数小于用户的错误登录重复次数！";
		# 	$errorValue = 1;
		# 	return;
		# }
		if($psdLength < 8) 
		{
			$errormessage="请确任用户密码长度设置值不小于8！";
			$errorValue = 1;
			return;
		}
		if($PASSWD_TIMEOUT < 1 || $PASSWD_TIMEOUT >7 ) {
			$errormessage="请确任设置的口令周期格式正确！";
			$errorValue = 1;
			return;
		}

		if(!$errormessage){
			$usrlogincount_setting{'TIMEOUT'} = $timeout;
			$usrlogincount_setting{'MANAGERTIME'} = $managertimes;
			$usrlogincount_setting{'AUTH_PASSWD'} = $auth_passwd;
			$usrlogincount_setting{'PSD_LENGTH'} = $psdLength;
			$usrlogincount_setting{'PASSWD_TIMEOUT'} = $PASSWD_TIMEOUT;
			&writehash($save_filename, \%usrlogincount_setting);
			$notemessage = "已经成功保存此配置！";
		}
	}

}
	
	


sub display()
{
	
	&openbox('100%','left',_('配置'));
printf <<END
<form   name="PAGEUSER" action="$ENV{'SCRIPT_NAME'}"  method="post">
	<table>
		<tr class="odd">
			<td class="add-div-type" style="width:180px">页面超时时间限制</td>
			<td><input value="$timeout"  name="timeout" style="width:100px" /> (1-480分钟；默认值：30)</td>
		</tr>

		<tr class="odd">
			 <td class="add-div-type">错误登录次数限制</td>
			 <td><input  value="$managertimes"   class="textfield" name="managertimes" style="width:100px" /> (任意用户名错误登录次数限制上限，超过将锁定该屏幕；范围：2-50；默认值：10)</td>
		</tr>

		<tr class="odd">
			<td class="add-div-type">管理员账户锁定次数限制</td>
	        <td><input class="textfield" name="auth_passwd" value="$auth_passwd" style="width:100px" /> (普通管理员错误次数限制上限，超过将锁定该管理员账户；范围：2-50；默认值：5)</td>
		</tr>
		
		<tr class="odd">
			<td class="add-div-type">密码范围最小值设置</td>
	        <td><input class="textfield" name="psdLength" value="$psdLength" style="width:100px" /> (最小值为8；最大值：25；默认值：8)</td>
		</tr>
		
		<tr class="odd">
			<td class="add-div-type">口令周期</td>
	        <td><input class="textfield" name="PASSWD_TIMEOUT" value="$PASSWD_TIMEOUT" style="width:100px" /> (单位:天;默认值：7;范围：1-7天)</td>
		</tr>

	    <tr class="table-footer">
		<td colspan="2">
		<input type="hidden" class="action" name="ACTION" value="save"></input>
		<input type="submit" class="net_button" value="保存" align="middle"/>
		<input type="submit" class="net_button" value="默认配置" onclick="\$('.action').val('defaultConf');"/>	
		</td>
		</tr>
</table>
</form>
END
;
check_form();
&closebox();
}
sub check_form(){
	printf <<EOF
	<script>
var object = {
       'form_name':'PAGEUSER',
       'option'   :{
                    'timeout':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                               'ass_check':function(eve){
														 var timeout = eve._getCURElementsByName("timeout","input","PAGEUSER")[0].value;
														 var msg = "";
														 if(timeout>480 || timeout <1){
															 msg="页面超时时间应在1-480之间！";
														 }
														 return msg;
                                                     }
                             },
                    'managertimes':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                               'ass_check':function(eve){
														 var mtimes = eve._getCURElementsByName("managertimes","input","PAGEUSER")[0].value;
														 var msg = "";
														 mtimes = parseInt(mtimes);
														 if(mtimes<2 || mtimes >50){
															 msg = "错误登录次数应在2-50之间！"
														 }
														 return msg;
                                                     }
                             },
                    'auth_passwd':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                               'ass_check':function(eve){
														 var ftimes = eve._getCURElementsByName("auth_passwd","input","PAGEUSER")[0].value;
														 ftimes = parseInt(ftimes);
														 var msg = "";
														 if(ftimes<2 || ftimes >50){
															 msg = "错误登录次数应在2-50之间！"
														 }
														 return msg;
                                                     }
                             },
					'psdLength':{
                               'type':'text',
                               'required':'1',
                               'check':'note|',
                               'ass_check':function(eve){
	
														 //var area = eve._getCURElementsByName("psdLength","input","PAGEUSER")[0].value;
														 //var reg = /^([1-9][0-9]*)-([1-9][0-9]*)\$/;
														 //var arr = area.match(reg);
														 //if(!arr || arr.length != 3) {
															//return "非法的密码范围";
														 //}
														 //var min = parseInt(arr[1]);
														 //var max = parseInt(arr[2]);
														 //if(min > max || min < 8 || max < 8) {
															//return "非法的密码范围";
														 //}
														 //return "";
														 var area = eve._getCURElementsByName("psdLength","input","PAGEUSER")[0].value;
														 var reg = /^[1-9][0-9]*\$/;
														 var arr = area.match(reg);
														 var mesg = "";
														 if(!arr || arr.length != 1) {
															mesg = "非法的密码长度";
														 }else if(parseInt(arr[0]) < 8) {
															mesg = "密码长度不能低于8位";
														 }else if(parseInt(arr[0]) > 50) {
															mesg = "密码长度不能大于50";
														 }
														 return mesg;
                                                     }
                             },
					'PASSWD_TIMEOUT':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                               'ass_check':function(eve){
									var timeout= eve._getCURElementsByName("PASSWD_TIMEOUT","input","PAGEUSER")[0].value;
									var mesg = "";
									if(timeout<1 || timeout>7) {
										mesg = "请确任设置的口令周期格式正确！";
									}
									return mesg;
								}
                            }
                 }
         }
var check = new ChinArk_forms();
	check._main(object);
	</script>
EOF
;
}
&getcgihash(\%par); 
&showhttpheaders(); #初始化
&save();
&openpage(_('页面管理'),1,); #加载页面信息
&openbigbox($errormessage,$warnmessage,$notemessage);
&display();
