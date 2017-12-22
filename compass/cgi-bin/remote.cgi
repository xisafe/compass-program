#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: remote.cgi,v 1.6.2.1 2004/03/13 06:12:04 eoberlander Exp $
#

require '/var/efw/header.pl';

my (%remotesettings, %checked);

&showhttpheaders();

$remotesettings{'ENABLE_SSH'} = 'off';
$remotesettings{'ENABLE_SSH_PROTOCOL1'} = 'off';
$remotesettings{'ENABLE_SSH_PORTFW'} = 'off';
$remotesettings{'ACTION'} = '';

if (-e "${swroot}/ha/settings") {
    readhash("${swroot}/ha/settings", \%hasettings);
}

&getcgihash(\%remotesettings);

if ($remotesettings{'ACTION'} eq 'save')
{
	# not existing here indicates the box is unticked
	$remotesettings{'ENABLE_SSH_PASSWORDS'} = 'off' unless exists $remotesettings{'ENABLE_SSH_PASSWORDS'};
	if ($hasettings{'HA_ENABLED'} eq "on") {
	    $remotesettings{'ENABLE_SSH'} = 'on';
	    $remotesettings{'ENABLE_SSH_KEYS'} = 'on';
	}
	else {
	    $remotesettings{'ENABLE_SSH_KEYS'} = 'off' unless exists $remotesettings{'ENABLE_SSH_KEYS'};
    }

	&writehash("${swroot}/remote/settings", \%remotesettings);
	if ($remotesettings{'ENABLE_SSH'} eq 'on')
	{
		&log(_('SSH is enabled.  Restarting.'));
		if  ($remotesettings{'ENABLE_SSH_PASSWORDS'} eq 'off'
		 and $remotesettings{'ENABLE_SSH_KEYS'}      eq 'off')
		{
			$errormessage = _('You have not allowed any authentication methods; this will stop you logging in');
		}
		#system ('/bin/touch', "${swroot}/remote/enablessh");
	}
	elsif ($hasettings{'HA_ENABLED'} ne "on")
	{
		&log(_('SSH is disabled.  Stopping.'));
		#unlink "${swroot}/remote/enablessh";
	}
	
	if ($remotesettings{'ENABLE_SSH_PROTOCOL1'} eq 'on')
	{
		&log(_('SSHv1 is enabled, old clients will be supported.'));
	}
	else
	{
		&log(_('SSHv1 is disabled, a version 2 client will be required.'));
	}

	system('/usr/local/bin/restartssh') == 0
		or $errormessage = _('Helper program returned error code')." " . $?/256;
}

if (-e "${swroot}/remote/default/settings") {
    readhash("${swroot}/remote/default/settings", \%remotesettings);
}
if (-e "${swroot}/remote/settings") {
    readhash("${swroot}/remote/settings", \%remotesettings);
}


# not existing here means they're undefined and the default value should be
# used
	$remotesettings{'ENABLE_SSH_PASSWORDS'} = 'on' unless exists $remotesettings{'ENABLE_SSH_PASSWORDS'};
	$remotesettings{'ENABLE_SSH_KEYS'} = 'on' unless exists $remotesettings{'ENABLE_SSH_KEYS'};

$checked{'ENABLE_SSH'}{'off'} = '';
$checked{'ENABLE_SSH'}{'on'} = '';
$checked{'ENABLE_SSH'}{$remotesettings{'ENABLE_SSH'}} = "checked='checked'";
$checked{'ENABLE_SSH_PROTOCOL1'}{'off'} = '';
$checked{'ENABLE_SSH_PROTOCOL1'}{'on'} = '';
$checked{'ENABLE_SSH_PROTOCOL1'}{$remotesettings{'ENABLE_SSH_PROTOCOL1'}} = "checked='checked'";
$checked{'ENABLE_SSH_PORTFW'}{'off'} = '';
$checked{'ENABLE_SSH_PORTFW'}{'on'} = '';
$checked{'ENABLE_SSH_PORTFW'}{$remotesettings{'ENABLE_SSH_PORTFW'}} = "checked='checked'";
$checked{'ENABLE_SSH_PASSWORDS'}{'off'} = '';
$checked{'ENABLE_SSH_PASSWORDS'}{'on'} = '';
$checked{'ENABLE_SSH_PASSWORDS'}{$remotesettings{'ENABLE_SSH_PASSWORDS'}} = "checked='checked'";
$checked{'ENABLE_SSH_KEYS'}{'off'} = '';
$checked{'ENABLE_SSH_KEYS'}{'on'} = '';
$checked{'ENABLE_SSH_KEYS'}{$remotesettings{'ENABLE_SSH_KEYS'}} = "checked='checked'";


&openpage(_('Remote access'), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');

&openbigbox($errormessage, $warnmessage, $notemessage);

if ($hasettings{'HA_ENABLED'} eq "on") {
    $disabled{'ENABLE_SSH_KEYS'} = "disabled=disabled";
    $unbindswitch = "\$('.switch-image').unbind('click');";
    notificationbox(_("SSH can not be disabled because it is needed by High Availbility"));
}

&openbox('100%', 'left', _("Secure Shell Access Settings"));

$service_status = $remotesettings{'ENABLE_SSH'};

printf <<END

<script type="text/javascript">
    \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('/cgi-bin/remote.cgi', SERVICE_STAT_DESCRIPTION);
        $unbindswitch
    });
</script>

<form enctype='multipart/form-data' class="service-switch-form" id="ssh-form" method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type="hidden" class="service-status" name="ENABLE_SSH" value="$service_status" />

<table cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td >
            <div id="access-policy" class="service-switch">
                <div><span class="title">%s</span>
                    <span class="image"><img class="switch-image $service_status" align="absbottom" src="/images/switch-%s.png" alt="" border="0"/></span>
                </div>
                
                    <div id="access-description" class="description" %s>%s</div>
                    <div id="access-policy-hold" class="spinner working">%s</div>
                    <div id="access-options" class="options-container" %s>
                        <div class="title"><p class="form-section-title first">%s</p></div>
                        <div class="divider"><img src="/images/clear.gif" width="1" height="1" alt="" border="0" /></div>
                        <div class="options">
                            <p><input class="checkbox" type='checkbox' name='ENABLE_SSH_PROTOCOL1' $checked{'ENABLE_SSH_PROTOCOL1'}{'on'} /> <span class="cb-caption">%s</span></p>
                            <p><input class="checkbox" type='checkbox' name='ENABLE_SSH_PORTFW' $checked{'ENABLE_SSH_PORTFW'}{'on'} /> <span class="cb-caption">%s</span></p>
                            <p><input class="checkbox" type='checkbox' name='ENABLE_SSH_PASSWORDS' $checked{'ENABLE_SSH_PASSWORDS'}{'on'} /> <span class="cb-caption">%s</span></p>
                            <p><input class="checkbox" type='checkbox' name='ENABLE_SSH_KEYS' $checked{'ENABLE_SSH_KEYS'}{'on'} $disabled{'ENABLE_SSH_KEYS'} /> <span class="cb-caption">%s</span></p>
                        </div>
                        <div class="save-button">
                            <input class='submitbutton save-button' type='submit' name='submit' value='%s' /></div>
                    </div>
            
            </div>
        </td>
    </tr>
</table>
    <input type='hidden' name='ACTION' value='save' />
</form>
END
, escape_quotes(_("The Secure Shell is being started. Please hold...")),
escape_quotes(_("The Secure Shell is being shutdown. Please hold...")),
escape_quotes(_("Settings are saved and the Secure Shell is being restarted. Please hold..."))
,_('Enable Secure Shell Access'),
, $remotesettings{'ENABLE_SSH'} eq 'on' ? 'on' : 'off',
, $remotesettings{'ENABLE_SSH'} eq 'on' ? 'style="display:none"' : '',
, _("Use the switch above to enable access to your %s %s using the Secure Shell.<br />For security reasons the Secure Shell is disabled per default.", $brand , $product),
_("SSH Access is being disabled. Please hold..."),
, $remotesettings{'ENABLE_SSH'} eq 'off' ? 'style="display:none"' : '',
_("Secure Shell Options"),
_('Support SSH protocol version 1 (required only for old clients)'),
_('Allow TCP forwarding'),
_('Allow password based authentication'),
_('Allow public key based authentication'),
_('Save')
;

&closebox();


&openbox('100%', 'left', _('SSH host keys'));

print "<table cellspacing=\"0\" cellpadding=\"0\" class=\"ruleslist\">\n";

printf <<END
<tr><td class='boldbase'><b>%s</b></td>
    <td class='boldbase'><b>%s</b></td>
    <td class='boldbase'><b>%s</b></td></tr>
END
,
_('Key'),
_('Fingerprint'),
_('Size (bits)')
;

&viewkey("/etc/ssh/ssh_host_key.pub","RSA1");
&viewkey("/etc/ssh/ssh_host_rsa_key.pub","RSA2");
&viewkey("/etc/ssh/ssh_host_dsa_key.pub","DSA");

print "</table>\n";

&closebox();

&closebigbox();

&closepage();


sub viewkey
{
  my $key = $_[0];
  my $name = $_[1];

  if ( -e $key )
  {
    my @temp = split(/ /,`/usr/bin/ssh-keygen -l -f $key`);
    my $keysize = &cleanhtml($temp[0],"y");
    my $fingerprint = &cleanhtml($temp[1],"y");
    print "<tr><td>$key ($name)</td><td><code>$fingerprint</code></td><td align='center'>$keysize</td></tr>\n";
  }
}
