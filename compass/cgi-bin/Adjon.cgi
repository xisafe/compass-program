#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: VLAN页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/10/26-11:04
#===============================================================================
require '/home/httpd/cgi-bin/proxy.pl';
require '/var/efw/header.pl';
my %par = ();
my $ADS_username = "";
my $ADS_password = "";
my $errormessage = "";
my $action = "";

$reload=0;

sub save()
{
	$action = $par{"ACTION"};
	if($action eq "ADD")
	{
		 $ADS_username = $par{"user"};
		 $ADS_password = $par{"psw"};
		
		 if($ADS_username&&$ADS_password)
		 {
printf <<EOF
			<script>
				RestartService("Adjon正在加入域，请耐心等待");
			</script>
EOF
;
			my $cmd_result = `sudo net ads join -U $ADS_username%$ADS_password -s /etc/samba/winbind.conf`;
			`sudo fcmd net ads join -U $ADS_username%$ADS_password -s /etc/samba/winbind.conf`;

		 if($cmd_result =~ /Joined/)
		 {
			 $notemessage = _("Successfully joined domain.");
			 printf <<EOF
			<script>
				endmsg("Adjon连接成功");
			</script>
EOF
;
			 $reload = 1;
		 }else{
		 printf <<EOF
			<script>
				endmsg("Adjon加入域失败");
			</script>
EOF
;
		 if($cmd_result =~ /Kinit failed: Clock skew too great/)
		 {
			 $errormessage = _("Clock skew is too great. Make sure the Firewall as well as the PDC have a valid NTP (Network Time Protocol) setup.");
		 }elsif($cmd_result =~ /ads_connect: Cannot resolve network address/)
		 {
			 $errormessage = _("Cannot resolve PDC hostname in requested realm. Is the PDC listed in the host list?");
		 }elsif($cmd_result =~ /ads_connect: Operations error/)
		 {
			 $errormessage =  _("Error while connecting to PDC. Is the PDC listed in the custom nameserver list?");
		 }elsif($cmd_result =~ /ads_connect: Invalid argument\/ || $line =~ m\/ads_connect: Interrupted system call/)
		 {
			 $errormessage = _("Error while connecting to PDC. Is the authentication realm set to the correct value? Is the PDC active?");
		 }elsif($cmd_result =~ /Host is not configured as a member server./)
		 {
			 $errormessage = _("Host is not configured as a member server. Is authentication active on at least one zone?");
		 }elsif($cmd_result =~ /ads_connect: Preauthentication failed./)
		 {
			 $errormessage = _("Authenication on the PDC failed. Check username, password and the privileges of the PDC user.");
		 }elsif($cmd_result =~ /ads_connect: Client not found in Kerberos database"\) or line.endswith\("rpc: Logon failure/)
		 {
			$errormessage =  _("Authenication on the PDC failed. Check username, password and the privileges of the PDC user.");
		 }elsif($cmd_result =~ /ads_connect: Client not found in Kerberos database"\) or line.endswith\("rpc: Logon failure/)
		 {
			$errormessage =  _("Authenication on the PDC failed. Check username, password and the privileges of the PDC user.");
		 }else{
			$errormessage = $cmd_result;
		 }
	}
}else{
		$errormessage = _("用户名或密码不能为空");
	}
	}elsif($action eq "apply"){
		&log(_('Apply proxy settings'));
		applyaction();
	}
}

sub display_set()
{
	printf <<EOF
	<form name="ADJON_FORM"  method="post" action="$ENV{'SCRIPT_NAME'}" >
	<table>
	<tr class="env">
    <td class="add-div-type" >%s *</td>
    <td><input type="text" name="user" /></td>
	</tr>
	<tr class="odd">
    <td class="add-div-type" >%s *</td>
    <td><input type="password" name="psw" /></td>
	</tr>
	<tr class="table-footer">
	<td colspan="2">
	<input class="net_button" type = "submit" value="%s" />
	<input type="hidden" name="ACTION" value="ADD" />
	</td>
	</tr>
	</table>
	</form>
EOF
,_("ADS 管理员用户名")
,_("ADS 管理员密码")
,_("加入ADS")
;
}

sub check_form(){
	printf <<EOF
<script>
var object = {
       'form_name':'ADJON_FORM',
       'option'   :{
                    'user':{
                               'type':'text',
                               'required':'1',
                               'check':'name|',
                             },
                    'psw':{
                               'type':'password',
                               'required':'1',
                             },
                 }
         }
var check = new ChinArk_forms();
//check._get_form_obj_table("ADJON_FORM");
check._main(object);
</script>
EOF
;
}
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('ADjon'),1,'<script type="text/javascript" src="/include/waiting.js"></script>');
&save();

if ($reload) {
    system("touch $proxyreload");
}
if (-e $proxyreload) {
	applybox(_("配置已经更改，需要应用才能使更改生效"));
}
&openbigbox($errormessage,'', $notemessage);
&openbox('100%', 'left', _('设置'));
&display_set();
&closebox();
check_form();
&closepage();
