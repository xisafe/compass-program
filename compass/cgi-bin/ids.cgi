#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: ids.cgi,v 1.13 2005/04/17 23:15:44 gespinasse Exp $
#

use IO::Socket;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;
use MIME::Base64;
use DateTime;
use DateTime::TimeZone;

require '/var/efw/header.pl';
require '/home/httpd/cgi-bin/endianinc.pl';

# Importing EFW Settings Module
use EFWConfig;
&showhttpheaders();
my $notemessage ="";
my $conffile    = "${swroot}/snort/settings";
my $conffile_default = "${swroot}/snort/default/settings";
my %conffile_setting;
my %conffile_default_setting;
my %par=();
my %checked=();
our $errormessage = '';
my $reload = 0;
my $needreload = "${swroot}/snort/needreload";
my %frequency = ();

my $restart = "sudo /usr/local/bin/restartsnort >/dev/null 2>&1";
my $rules_tmp_dir = "/tmp/snort_rules";
my $fetchrules = "/usr/local/bin/fetchsnortrules";

my $global_settings = undef;
$settings = get_settings();
# Tells whether a service was restarted or not
my $service_restarted = 0;

#获取网络接口列表
sub get_eth()
{
	my $temp_cmd = `ip a`;
	my @all_hash;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		if(($line =~ /^[0-9]+\: +(eth[0-9]+)\:/))
		{
			push(@all_hash,$1);
		}
	}
	return @all_hash;
}
=p
# Overrides openbigbox in header.pl. Adds functionality do optionally hide
# the box and let it be displayed using javascript.
#
# This is needed for ajax, since the site isn't reloaded, and error validation
# is done on the client-side with javascript.
sub openbigbox_(@@@) {
    my $error=shift;
    my $warning=shift;
    my $note=shift;

    errorbox($error->[0],"validation-error",($error->[1] eq "hide" ? "display:none" : ""));
    warnbox($warning);
    notificationbox($note);
}
=cut

sub get_settings() {
    if(!$global_settings) {
        $global_settings = new EFWConfig('snort.settings');
    }
    return $global_settings;
}

sub to_bool {
    my $val = shift;
    
    if("$val" eq 'on' || $val eq '1') {
        return '1';
    }
    if($val eq 'off' || $val eq '0') {
        return '0';
    }
    return undef;
}

sub snort_enabled {
    my $settings = get_settings();
    
    # If enabled is set return True
    if(to_bool($settings->get('enabled')) eq '1') {
        return 1;
    }
    return 0;
}

sub enabled_rule_targets() {
    $global_settings = undef;
    my $settings = get_settings();
    my $enabled_rule_targets_raw = $settings->get('enabled_rules');
    my @enabled_rules = split(",", $enabled_rule_targets_raw);
    return @enabled_rules;
}

sub readconfig() {
    # Forcing a reload of the settings
    $global_settings = undef;
    $settings = get_settings();
    
    # Resetting checked var
    $checked = undef;
    # Resetting frequency var
    $frequency = undef;
    
    $checked{UPDATE_SCHEDULE} = check($settings->get('update_schedule'));
    my @rules_tmp = enabled_rule_targets();
    $checked{RULE_MODE}{'custom'} = check(in_array('custom', \@rules_tmp));
    $checked{RULE_MODE}{'auto'} = check(in_array('auto', \@rules_tmp));
    
    $frequency{$settings->get('update_schedule')} = 'selected="selected"';
}

sub in_array {
    my $needle = shift;
    my $array = shift;
    my @haystack = @$array;
    
    foreach(@haystack) {
        if($_ eq $needle) { return 1 };
    }
    return 0;
}

# Per default action is empty
$par{'ACTION'} = '';

# Wantfile and filevar are used to tell those dumbfucks of original shorewall developers
# that fileuploads should be allowed and the file information included
# within the getcgihash hash.
&getcgihash(\%par, {'wantfile' => 1, 'filevar' => 'rules'});

# Setting up defaults if no action is set
if($par{'ACTION'} eq '') {
    &readconfig();
}
my $validation_error = 0;
if (-e $conffile_default) {
	&readhash($conffile_default, \%conffile_default_setting);
}


sub save()
{
	if ($par{'ACTION'} eq 'save') {
		if (-e $conffile) {

			system("echo $par{'ENABLED'} >/tmp/elvis");
			&readhash($conffile, \%conffile_setting);
			if($par{'ENABLED'} eq 'on')
			{
				$conffile_setting{'ENABLED'} = 1;
			}
			else{
				$conffile_setting{'ENABLED'} = 0;
			}
			$conffile_setting{'BYPASS'} = $par{'is_by_pass'};
		}
		else{
			&readhash($conffile_default, \%conffile_setting);
			if(($par{'ENABLED'} eq 'off') || ($par{'ENABLED'} eq ''))
			{
				$conffile_setting{'ENABLED'} = 1;
			}
			else{
				$conffile_setting{'ENABLED'} = 0;
			}
			$conffile_setting{'BYPASS'} = $par{'is_by_pass'};
		}
		&writehash($conffile, \%conffile_setting);
		begin();
		system("sudo /usr/local/bin/restartsnort -f");
		`sudo fmodify $conffile`;
		ends();
		$notemessage = "入侵防御寂静重启成功！";
	}
}
sub begin(){
	printf <<EOF
	<script>
	  RestartService("入侵防御正在重启......");
	</script>
EOF
;
}
sub ends(){
	printf <<EOF
	<script>
	setTimeout( function(){ endmsg("入侵防御重启成功！")},3000);
	window.location.href = window.location.href+"?ok";
	</script>
EOF
;
}


&openpage(_('Intrusion Prevention System'), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script><script type="text/javascript" src="/include/waiting.js"></script>');
save();
if($ENV{'QUERY_STRING'}){
	$notemessage = "入侵防御已经成功重启！";

}
openbigbox("","",$notemessage);


# If no custom rules are uploaded, only the field to add new rules is displayed
@rules = enabled_rule_targets();
%display = {};
# Don't display Enable/Disable checkbox
$display{'enabled'} = 'display:none';
$display{'enabled_class'} = 'custom_enabled';
$display{'upload'} = 'display:none';
$display{'upload_class'} = 'custom_upload';
$checked{'custom_enabled'} = '';

my $BYPASS;
my $by_pass;
my $no_by_pass;
my $INTERFACE;
my $interface_hidden;
if(-e $conffile)
{
	&readhash($conffile, \%conffile_setting);
	$BYPASS = $conffile_setting{'BYPASS'};
	
}else{
	&readhash($conffile_default, \%conffile_setting);
	$BYPASS = $conffile_default_setting{'BYPASS'};
	$INTERFACE = '';
}
if($BYPASS eq '1')
{
	$by_pass="selected='selected'";
	$no_by_pass="";
	$interface_hidden = "";
}else{
	$by_pass="";
	$no_by_pass="selected='selected'";
	$interface_hidden = "class='hidden_class'";
}
$service_status = 'on';
if (!$conffile_setting{'ENABLED'}) {
	$service_status = 'off';
}

#获取网络接口
#my @eth = get_eth();
printf <<END
<script type="text/javascript">
    \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('/cgi-bin/ids.cgi', SERVICE_STAT_DESCRIPTION, ajaxian_save=1, 0);
    });
</script>

<form enctype="multipart/form-data" class="service-switch-form" method="post" action='$ENV{'SCRIPT_NAME'}'>
<input type="hidden" class="service-status" name="ENABLED" value="%s" />
<table cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td valign="top">
            <div id="access-policy" class="service-switch">
                <div><span class="title">%s</span>
                    <span class="image"><img class="$service_status" align="top" src="/images/switch-%s.png" alt="" border="0"/></span>
                </div>
                    <div id="access-description" class="description" %s>%s</div>
                    <div id="access-policy-hold" class="spinner working">%s</div>
                    <div class="options-container efw-form" %s>
					<div style="margin:10px 0;padding;5px;font-size:13px;">
					<span style="float:left">请选择检测方式 :
					<select  id='is_by_pass' name="is_by_pass" >
						<option value='0' $no_by_pass>网关模式</option> 
						<option value="1" $by_pass >旁路模式</option> 
					</select></span>
END
, escape_quotes(_("Intrusion Prevention System is being restarted. Please hold...")),
escape_quotes(_("Intrusion Prevention System is being shutdown. Please hold..."))
, escape_quotes(_("Intrusion Prevention System settings are saved and the service is being restarted. Please hold..."))
, snort_enabled() ? 'on' : 'off',
, _("Enable Intrusion Prevention System"),
, snort_enabled() ? 'on' : 'off',
    , snort_enabled() ? 'style="display:none"' : '',
, _("要激活入侵防御系统，使用上面的开关启用;入侵防御系统需要和防火墙功能配合实现对攻击的检测和跟踪。"),
_("Intrusion Prevention System is being restarted. Please hold..."),
, snort_enabled() ? '' : 'style="display:none"'
, _("SNORT Rules Settings"),
_("Emerging Threats SNORT rules"),
_("Automatically fetch SNORT rules"),
_("Update rules now"),
(!$auto_on ? 'style="display:none"' : ''),
_("Choose update schedule")
, _('Hourly')
, _('Daily')
, _('Weekly')
, _('Monthly'),
_("Custom SNORT Rules"),
_("Custom rules"),
_("Overwrite"),
_("Upload custom rules"),
_("or"),
_("Cancel"),
_("You may either use a tar.gz, zip, or single .rules file containing the rules"),
_("Enable/Disable custom rules using the checkbox"),
_('Save and restart')
;


printf <<END					
					<br /><br />
					 <input class='net_button' type='submit'  value="保存"  title="保存" onclick="\$('.service-switch-form').unbind('submit');" />
					 <input name="ACTION" value="save" type="hidden">
				</div>
			</div>
			</div>
        </td>
    </tr>
</table>
</form>
END
;

&closebigbox();
&closepage();
