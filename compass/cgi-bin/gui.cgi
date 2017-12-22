#!/usr/bin/perl
#
# IPCop CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) Bill Ward
#
# $Id: gui.cgi,v 1.2.2.4 2004/08/10 15:21:21 eoberlander Exp $
#

require '/var/efw/header.pl';

my %languages_hash = ();
my $languages = \%languages_hash;
my $i18n = '/usr/lib/efw/i18n/';

my $enterprise = 0;
if (-e '/var/efw/appliance/info') {
    $enterprise = 1;
}

sub load_languages() {
    my %ret_hash = ();
    my $ret = \%ret_hash;

    my %ret_hash_sorted = ();
    my $ret_sorted = \%ret_hash_sorted;

    opendir(my $fd, $i18n) || return ();
    foreach my $line(readdir($fd)) {
	my %hash = ();
        my $item = \%hash;
	readhash($i18n.'/'.$line, $item);
	next if ($item->{'ISO'} =~ /^$/);
        $ret_sorted->{$item->{'PRIORITY'}.$item->{'GENERIC'}} = $item;
        $ret->{$item->{'ISO'}} = $item;
    }
    close($fd);
    return ($ret, $ret_sorted);
}

my $restarthotspot = '/usr/local/bin/run-detached "sudo /usr/local/bin/restarthotspot"';

my (%cgiparams, %mainsettings, %checked);
$cgiparams{'WINDOWWITHHOSTNAME'} = 'off';

&getcgihash(\%cgiparams);

&showhttpheaders();
&readhash("${swroot}/main/settings",\%mainsettings);

my ($languages, $languages_sorted) = load_languages();

if ($cgiparams{'ACTION'} eq 'save')
{
	if ( ! $languages->{$cgiparams{'lang'}} )
	{
		$errormessage="$errormessage<P>". _('Invalid input');
		goto SAVE_ERROR;
	}

        # write cgi vars to the file.
	$mainsettings{'LANGUAGE'} = $cgiparams{'lang'};
        $mainsettings{'WINDOWWITHHOSTNAME'} = $cgiparams{'WINDOWWITHHOSTNAME'};
	&writehash("${swroot}/main/settings", \%mainsettings);
	expireMenuCache();
	system("sudo /etc/init.d/emi reload &>/dev/null");

} else {

	if ($mainsettings{'WINDOWWITHHOSTNAME'}) {
		$cgiparams{'WINDOWWITHHOSTNAME'} = $mainsettings{'WINDOWWITHHOSTNAME'};
	} else {
		$cgiparams{'WINDOWWITHHOSTNAME'} = 'off';
	}
}

$checked{'WINDOWWITHHOSTNAME'}{'off'} = '';
$checked{'WINDOWWITHHOSTNAME'}{'on'} = '';
$checked{'WINDOWWITHHOSTNAME'}{$cgiparams{'WINDOWWITHHOSTNAME'}} = "checked='checked'";
gettext_init($mainsettings{'LANGUAGE'}, "efw");
&openpage(_('GUI settings'), 1, "<script language='javascript' src='/include/gui.js'></script>");

&openbigbox($errormessage, $warnmessage, $notemessage);

&openbox('100%','left',_('Settings'));
printf <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type='hidden' name='ACTION' value='save' />
    <table cellpadding="0" cellspacing="0" >
	<tr class="env">
	<td class="add-div-type" rowspan="1">
    <label id="username_field" for="username">%s *</label>
	</td><td>
    <select name='lang'>
END
,_("Select your language")
;

my $id=0;
foreach my $lang (sort keys %$languages_sorted)
{
    $id++;
	my $item = $languages_sorted->{$lang};
	my $engname = $item->{'GENERIC'};
	my $natname = $item->{'ORIGINAL'};

	print "<option value='$item->{'ISO'}' ";
	if ($item->{'ISO'} =~ /$mainsettings{'LANGUAGE'}/)
	{
		print " selected='selected'";
	}
	printf <<END
>$engname ($natname)</option>
END
	;
}
printf <<END
                    </select>
				</td>
				</tr>
				<tr class="odd hidden_class" >
				<td class="add-div-type" rowspan="1">
				<label id="username_field" for="username">%s *</label>
				</td>
				<td>
                    <input type="checkbox" name="WINDOWWITHHOSTNAME" $checked{'WINDOWWITHHOSTNAME'}{'on'} />
               
           </td></tr>
        <tr class="table-footer">
        <td align="center" colspan="2">
		<input class='net_button' type='submit' name='submit' value='%s' />
		</td>
		</tr></table>

END
, _('Display hostname in window title')
, _("Save Changes")
;
if (! $enterprise and ! is_branded()) {
    printf <<END
        <div class="fields-row">
          <br class="cb" />
          <br class="cb" />
          <a href="https://launchpad.net/products/efw/trunk/+translations" target="_new">%s</a>
        </div>
END
, _('Help translating this project')
;
}

printf <<END
    </div>
    </td></tr></table>
</form>
END
;

&closebox();
&closebigbox();
&closepage();
exit;
