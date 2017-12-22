#!/usr/bin/perl

require '/var/efw/header.pl';

my (%settings, %checked);
my $conffile         = "${swroot}/openvpn/settings";
my $conffile_default = "${swroot}/openvpn/default/settings";
my $restart  = '/usr/local/bin/run-detached /usr/local/bin/restartopenvpn';
my $name             = _('SNMP');

&showhttpheaders();
$errormessage = '';
&getcgihash(\%settings);

if ($settings{'ACTION'} eq 'save'){

	delete $settings{'__CGI__'};
    if ( -f $conffile_default ) {
        &readhash( "$conffile_default", \%new_settings );
    }
    if ( -f $conffile ) {
        &readhash( "$conffile", \%new_settings );
    }
    $new_settings{'OPENVPN_ENABLED'} = $settings{'OPENVPN_ENABLED'};
	&writehash($conffile, \%new_settings);
	`sudo fmodify $conffile`;
	system('/usr/local/bin/run-detached /usr/local/bin/restartopenvpn');
}

if ( -f $conffile_default ) {
    &readhash( "$conffile_default", \%settings );
}
if ( -f $conffile ) {
    &readhash( "$conffile", \%settings );
}

&openpage(_('SSL VPN'), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
&openbigbox($errormessage, $warnmessage, $notemessage);


$service_status = $settings{'OPENVPN_ENABLED'};
my $is_hidden = "";
if($settings{'SNMP_OVERRIDE'} ne 'on')
{
	$is_hidden = "hidden_class";
}

printf <<END
<script type="text/javascript">
    \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('$ENV{'SCRIPT_NAME'}', SERVICE_STAT_DESCRIPTION);
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
<input type="hidden" class="service-status" name="OPENVPN_ENABLED" value="$service_status" />

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
                    <div id="access-options" class="options-container" %s>
                    使用上面的开关来关闭 SSL VPN 服务.
                        <div class="options">
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
, escape_quotes("正在应用SSL VPN服务,请稍等..."),
escape_quotes("正在关闭SSL VPN服务,请稍等..."),
escape_quotes("配置已更改正在重启SSL VPN服务,请稍等..."),
'SSL VPN 服务',
$settings{'OPENVPN_ENABLED'} eq 'on' ? 'on' : 'off',
$settings{'OPENVPN_ENABLED'} eq 'on' ? 'style="display:none"' : '',
 "使用上面的开关来启用 SSL VPN 服务.",
'',
 $settings{'OPENVPN_ENABLED'} eq 'off' || $settings{'OPENVPN_ENABLED'} eq '' ? 'style="display:none"' : '',
_('Save'),
;

#&closebox();
print "</form>\n";
&closebigbox();
&closepage();

