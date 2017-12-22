#!/usr/bin/perl

require '/var/efw/header.pl';

my (%settings, %checked);
my $conffile         = "${swroot}/snmp/settings";
my $conffile_default = "${swroot}/snmp/default/settings";
my $name             = _('SNMP');
my $errormessage = '';
my $warnmessage = '';
my $notemessage = '';

&showhttpheaders();
&getcgihash(\%settings);

if ($settings{'ACTION'} eq 'save')
{
	if ($settings{'ENABLED'} eq 'on') {
		&log(_('SNMP server is enabled.  Restarting.'));
    } else {
		&log(_('SNMP server is disabled.  Stopping.'));
	}

	 delete $settings{'__CGI__'};
	if ($settings{'SNMP_OVERRIDE'} eq 'on' && !validemail($settings{'SNMP_CONTACT_EMAIL'})) {
		$errormessage = _('Invalid email address.');
	}
	#先判断是v1还是v2，是v3才判断密码长度
	if($settings{'PROT'} eq 'v3'){
		if (length($settings{'PASS'})< 8 || length($settings{'PASS_ENCRY'}) < 8) {
			$errormessage="密码或密钥长度错误。";
		}
	}
	if ($errormessage eq '') {
		&writehash($conffile, \%settings);
		`sudo fmodify $conffile`;
		system('sudo /usr/local/bin/restartsnmp.py --force >/dev/null 2>&1') == 0
    		or $errormessage = _('Helper program returned error code')." " . $?/256;
    }
	$notemessage = "已成功保存当前修改";
}



if ( -e $conffile_default ) {
    &readhash( "$conffile_default", \%settings );
}
if ( -e $conffile ) {
	&readhash( "$conffile", \%settings );
}

&openpage(_('SNMP'), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
&openbigbox($errormessage, $warnmessage, $notemessage);

#&openbox('100%', 'left', _("Settings"));
 ####help_msg
	my $help_hash1 = read_json("/home/httpd/help/snmp_help.json","snmp.cgi","服务-SNMP服务-团体字符串","-10","30","down");
	my $help_hash2 = read_json("/home/httpd/help/snmp_help.json","snmp.cgi","服务-SNMP服务-位置","-10","30","down");
	my $help_hash3 = read_json("/home/httpd/help/snmp_help.json","snmp.cgi","服务-SNMP服务-系统联系电子邮件地址","-10","30","down");
    my $help_hash4 = read_json("/home/httpd/help/snmp_help.json","snmp.cgi","服务-SNMP服务-SNMP","-10","30","down");
	###
$service_status = $settings{'ENABLED'};
my $is_hidden = "";
if($settings{'SNMP_OVERRIDE'} ne 'on')
{
	$is_hidden = "hidden_class";
}
my $is_v3 = "";
if($settings{'PROT'} ne 'v3')
{
	$is_v3 = "hidden_class";
}

my $v1_checked = "";
my $v2_checked = "";
my $v3_checked = "";
if($settings{'PROT'} eq 'v1')
{
	$v1_checked = "checked";
}elsif($settings{'PROT'} eq 'v2')
{
	$v2_checked = "checked";
}
else
{
	$v3_checked = "checked";
}

my $AUTHEN__MD5_select = "selected";
my $AUTHEN__SHA_select = "";
if($settings{'AUTHEN'} eq 'SHA'){
	$AUTHEN__MD5_select = "";
	$AUTHEN__SHA_select = "selected";
}

my $ENCRYT_DES_selected = "selected";
my $ENCRYT_AES_selected = "";
if($settings{'ENCRYT'} eq 'AES'){
	$ENCRYT_DES_selected = "";
	$ENCRYT_AES_selected = "selected"
}




printf <<END
<script type="text/javascript">
    \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('/cgi-bin/snmp.cgi', SERVICE_STAT_DESCRIPTION);
    });
    function emailActivation () {
    	if (\$('#emailC').get()[0].checked)
		{
    		\$('#emailF').get()[0].disabled = false;
			\$('#email_tr').css("display","table-row");
		}else{
    		\$('#emailF').get()[0].disabled = 'disabled';
			\$('#email_tr').css("display","none");
			
		}
    }
	
	function prot_show () {
    	if (\$('#v3_id').get()[0].checked)
		{
    		\$('#user').get()[0].disabled = false;
			\$('#user_tr').css("display","table-row");
			\$('#pass').get()[0].disabled = false;
			\$('#pass_tr').css("display","table-row");
			\$('#authen').get()[0].disabled = false;
			\$('#authen_tr').css("display","table-row");
			\$('#encry').get()[0].disabled = false;
			\$('#encry_tr').css("display","table-row");
			\$('#passencry').get()[0].disabled = false;
			\$('#passencry_tr').css("display","table-row");
		}else{
    				
			\$('#user').get()[0].disabled = 'disabled';
			\$('#user_tr').css("display","none");
			\$('#pass').get()[0].disabled = 'disabled';
			\$('#pass_tr').css("display","none");
			\$('#authen').get()[0].disabled = 'disabled';
			\$('#authen_tr').css("display","none");
			\$('#encry').get()[0].disabled = 'disabled';
			\$('#encry_tr').css("display","none");
			\$('#passencry').get()[0].disabled = 'disabled';
			\$('#passencry_tr').css("display","none");
			
		}
    }
	
</script>

<div id="validation-error" class="error-fancy" style="width: 504px; display:none">
        <div class="content">
            <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td class="sign" valign="middle"><img src="/images/bubble_red_sign.png" alt="" border="0" /></td>
                    <td id="validation-error-text" class="text" valign="middle"></td>
                </tr>
            </table>
        </div>
        <div class="bottom"><img src="/images/clear.gif" width="1" height="1" alt="" border="0" /></div>
</div>

<form name="SNMP_FORM" enctype='multipart/form-data' class="service-switch-form" id="snmp-form" method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type="hidden" class="service-status" name="ENABLED" value="$service_status" />

<table cellpadding="0" cellspacing="0" border="0" >
    <tr>
        <td valign="top">
            <div id="access-policy" class="service-switch">
                <div  ><span class="title">%s</span>
                    <span class="image"><img class="$service_status" align="absbottom" src="/images/switch-%s.png" alt="" border="0"/></span>
                </div>
									<br />
                    <div id="access-description" class="description" %s>%s</div>

                    <div id="access-policy-hold" class="spinner working">%s</div>
					<br />
                    <div id="access-options" class="options-container" %s>
                        <div class="options">
                            <table class="data_table">
							
							 <tr class="env">
                                <td class="need_help" width="35%">协议版本</td>
                                <td><input type='radio' id="v1_id" class="text" name='PROT' value='v1' $v1_checked onclick='prot_show();'/>V1  
								<input type='radio' id="v2_id" class="text" name='PROT' value='v2' $v2_checked onclick='prot_show();'/>V2
								<input type='radio' id="v3_id" class="text" name='PROT' value='v3' $v3_checked onclick='prot_show();'/>V3
								</td>
                            </tr>
							
                            <tr class="odd">
                                <td class="need_help" width="35%">%s * $help_hash1</td>
                                <td><input type='text' class="text" name='SNMP_COMMUNITY_STRING' value='$settings{'SNMP_COMMUNITY_STRING'}' /></td>
                            </tr>
                            <tr class="env">
                                <td class="need_help">%s $help_hash2</td>
                                <td><input type='text' class="text" name='SNMP_LOCATION' value='$settings{'SNMP_LOCATION'}' /></td>
                            </tr>   
							 <tr class="odd $is_v3" id="user_tr">
                                <td id="user" class="need_help" width="35%">用户名 *</td>
                                <td><input type='text' class="text" name='USER' value='$settings{'USER'}' />  (8位以上,默认用户名:SNMPMANAGE)</td>
                            </tr>
							<tr class="env $is_v3" id="pass_tr">
                                <td id="pass" class="need_help" width="35%">密码 *</td>
                                <td><input type='password' class="text" name='PASS' value='$settings{'PASS'}' />  (8位以上,默认密码:SNMP123456)</td>
                            </tr>
							 <tr class="odd $is_v3" id="authen_tr">
                                <td id="authen" class="need_help" width="35%">认证算法</td>
                                <td>
								<select name="AUTHEN">
										<option value="MD5" $AUTHEN__MD5_select>MD5</option>
										<option value="SHA" $AUTHEN__SHA_select>SHA</option>
										
								</select>
								</td>
                            </tr>
							<tr class="env $is_v3" id="encry_tr">
                                <td id="encry" class="need_help">加密算法</td>
                                <td>
								<select name="ENCRYT">
										<option value="DES" $ENCRYT_DES_selected>DES</option>
										<option value="AES" $ENCRYT_AES_selected>AES</option>
										
								</select>
								</td>
                            </tr> 
							<tr class="odd $is_v3" id="passencry_tr">
                                <td class="need_help" width="35%">加密密钥 *</td>
                                <td><input id="passencry" type='password' class="text" name='PASS_ENCRY' value='$settings{'PASS_ENCRY'}' /> (8位以上,默认密钥:SNMP123456)</td>
                            </tr>
                            <tr class="env">
                                <td class="need_help">%s $help_hash4</td>
                                <td><input id='emailC' type='checkbox' class="text" name='SNMP_OVERRIDE' %s onclick='emailActivation();' /></td>
                            </tr>    
                            <tr class="odd $is_hidden" id="email_tr">
                                <td class="need_help">%s $help_hash3</td>
                                <td><input id='emailF' type='text' class="text" name='SNMP_CONTACT_EMAIL' value='$settings{'SNMP_CONTACT_EMAIL'}' %s /></td>
                            </tr>
							<tr class="table-footer"><td colspan="4"> 
							<input  class="net_button" type='submit' name='submit' value='%s' onclick="\$('.service-switch-form').unbind('submit');" /></td></tr>
                            </table>
                        </div>
                       
                        </div>
                    </div>
                </div>
        </td>
    </tr>
</table>
    <input type='hidden' name='ACTION' value='save'  />
</form>
END
, escape_quotes(_("The SNMP server configuration is being applied. Please hold...")),
escape_quotes(_("The SNMP server is being shutdown. Please hold...")),
escape_quotes(_("Settings are saved and the SNMP server is being restarted. Please hold...")),
_('Enable SNMP Server'),
$settings{'ENABLED'} eq 'on' ? 'on' : 'off',
$settings{'ENABLED'} eq 'on' ? 'style="display:none"' : '',
 _("Use the switch above to enable the SNMP server."),
'',
 $settings{'ENABLED'} eq 'off' ? 'style="display:none"' : '',

_('Community String'),
_('Location'),
_('使用SNMP管理员邮件进行通知'),
$settings{'SNMP_OVERRIDE'} eq 'on' ? "checked='checked'" : '',
_('邮箱地址'),
$settings{'SNMP_OVERRIDE'} eq 'on' ? '' : "disabled='disabled'",
_('Save'),
;

#&closebox();
print "</form>\n";
&check_form;
&closebigbox();
&closepage();


sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'SNMP_FORM',
       'option'   :{
                    'SNMP_COMMUNITY_STRING':{
                               'type':'text',
                               'required':'1',
                               'check':'name|'
                             },
                    'SNMP_LOCATION':{
                               'type':'text',
                               'required':'0',
                               'check':'name|'
                             },
					'USER':{
					   'type':'text',
					   'required':'1',
					   'check':'name|',
					   'ass_check':function(eve){
							var msg = "";
							var name = eve._getCURElementsByName("USER","input","SNMP_FORM")[0].value;
							if(name.length < 8){
								msg = "用户名长度必须大于等于8位";
							}
							return msg;
						}
					},
					 'PASS':{
						'type':'text',
						'required':'1',
						'check':'other|',
						'other_reg':'!/^\$/',
						'ass_check':function(eve){
							var msg = "";
							var pass = eve._getCURElementsByName("PASS","input","SNMP_FORM")[0].value;
							if(pass.length < 8){
								msg = "密码长度必须大于等于8位";
							}
							return msg;
						}
                    },
                    'PASS_ENCRY':{
						'type':'text',
						'required':'1',
						'check':'other|',
						'other_reg':'!/^\$/',
						'ass_check':function(eve){
							var msg = "";
							var pass_encry = eve._getCURElementsByName("PASS_ENCRY","input","SNMP_FORM")[0].value;
							if(pass_encry.length < 8){
								msg = "密钥长度必须大于等于8位";
							}
							return msg;
						}
                    },
                    'SNMP_CONTACT_EMAIL':{
						'type':'text',
						'required':'1',
						'check':'mail|'
					}
         }
		 }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("SNMP_FORM");
    </script>
EOF
;
}