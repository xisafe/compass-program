#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 关机页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================


require '/var/efw/header.pl';

my %cgiparams;
my $death = 0;
my $rebirth = 0;
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;
my $system_title;

sub read_config(){
	if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
	$system_title = $system_settings{'SYSTEM_TITLE'};
}

&showhttpheaders();
&read_config();

$cgiparams{'ACTION'} = '';
&getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq 'shutdown')
{
	$death = 1;
	my $log_message = "关闭".$system_title;
	&user_log($log_message);
	&log($system_title."关闭");
	system '/usr/local/bin/ipcopdeath';

}
elsif ($cgiparams{'ACTION'} eq 'reboot')
{
	$rebirth = 1;
	my $log_message = "重启".$system_title;
	&user_log($log_message);
	system '/usr/local/bin/ipcoprebirth';

}
if ($death == 0 && $rebirth == 0) {
	&openpage(_('Shutdown control'), 1, '');

        &openbigbox($errormessage, $warnmessage, $notemessage);

	&openbox('100%', 'left', _('Shutdown'));
	printf <<END
<table width='100%'>
<tr style="height:30px;line-height:30px;" class="env">
	<td align='center'>
            <form method='post' action='$ENV{'SCRIPT_NAME'}'>
              <input type='hidden' name='ACTION' value='reboot' />
              <input class="net_button" type='submit' name='submit' value='%s' />
            </form>
        </td>

	<td align='center'>
            <form method='post' action='$ENV{'SCRIPT_NAME'}'>
              <input type='hidden' name='ACTION' value='shutdown' />
              <input class="net_button" type='submit' name='submit' value='%s' />
            </form>
        </td>
</tr>
</table>
END
, _('Reboot'), _('Shutdown')
	;
	&closebox();

}
else
{
	my ($message,$title);
	if ($death)
	{
		$title = _('Shutting down');
		$message = _($system_title."正在关闭......");
	}
	else
	{
		$title = _('Rebooting');
		$message = _($system_title."正在重启......");
	}
	&openpage($title, 0, '');
	my $url = "https://".$ENV{'SERVER_ADDR'}.":10443";
    &openbigbox($errormessage, $warnmessage, $notemessage);
	printf <<END
<div align='center'>
<table width='100%' bgcolor='#ffffff'>
<tr><td align='center'>
<br /><br /><img src='/images/reboot_splash.png' /><br /><br /><br />
</td></tr>
</table>
<br />
<font size='6'>$message</font>
</div>

<script>
    var des='https://'+self.parent.parent.location.host+'/index.cgi';
	self.parent.parent.location.href=des;//重启后跳转页面
	document.cookie = "";//重启后清空缓存 
</script>
END
;
}

&closebigbox();

&closepage();
