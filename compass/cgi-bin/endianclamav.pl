#!/usr/bin/perl
#
# Update CGI for Endian Firewall
#
#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
#        |         Endian GmbH/Srl                                                     |
#        |         Bergweg 41 Via Monte                                                |
#        |         39057 Eppan/Appiano                                                 |
#        |         ITALIEN/ITALIA                                                      |
#        |         info@endian.it                                                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        | http://www.fsf.org/                                                         |
#        +-----------------------------------------------------------------------------+
#


require '/var/efw/header.pl';

my $avuplogs_file = "/var/log/clamav/clam-update.log";
my $conffile = "/var/efw/clamav/settings";
my $conffile_default = "/var/efw/clamav/default/settings";

my %checked = ( 0 => '', 'on' => "checked='checked'" );
my %frequency = ('hourly' => '', 'daily' => '', 'weekly' => '', 'monthly' => '');

my %block = ( 'block' => '', 'pass' => '' );

my $do_reload = 0;

my %conf_hash = ();
my $conf = \%conf_hash;

my $restart = '/usr/local/bin/restartclamav';
my $callfreshclam = 'sudo /usr/bin/freshclam';
my $restartfreshclam = '/usr/local/bin/restartfreshclam';
my $restarthavp = '/usr/local/bin/restarthavp';

sub setfrequency() {
    $frequency{'hourly'} = '';
    $frequency{'daily'} = '';
    $frequency{'weekly'} = '';
    $frequency{'monthly'} = '';
    $frequency{$conf->{'UPDATE_SCHEDULE'}} = 'checked="checked"';

    $block{'block'} = '';
    $block{'pass'} = '';
    if ($conf->{'ARCHIVE_BLOCK_MAX'} eq 'on') {
	$block{'block'} = 'selected="selected"';
    } else {
	$block{'pass'} = 'selected="selected"';
    }
}

sub loadconfig() {
    if (-e $conffile_default) {
	readhash($conffile_default, $conf);
    }
    if (-e $conffile) {
	readhash($conffile, $conf);
    }
    setfrequency();
}

sub save() {
    my %par;
    getcgihash(\%par);

    if ($par{'action'} eq 'freshclam') {
        `$restartfreshclam`;
        `$callfreshclam`;
	return (0,'');
    }

    if ($par{'action'} ne 'save') {
	return (0,'');
    }

    if (($par{'ARCHIVE_MAXFILESIZE'} !~ /^\d+$/) or 
	($par{'ARCHIVE_MAXFILESIZE'} < 0)){
	return (0,_('Invalid max archive size'));
    }

    if (($par{'ARCHIVE_MAXRECURSION'} !~ /^\d+$/) or 
	($par{'ARCHIVE_MAXRECURSION'} < 0)){
	return (0,_('Invalid max nested archives value'));
    }

    if (($par{'ARCHIVE_MAXFILES'} !~ /^\d+$/) or 
	($par{'ARCHIVE_MAXFILES'} < 0)){
	return (0,_('Invalid max files count'));
    }
    if (($par{'ARCHIVE_MAXCOMPRESSIONRATIO'} !~ /^\d+$/) or 
	($par{'ARCHIVE_MAXCOMPRESSIONRATIO'} < 0)){
	return (0,_('Invalid compression ratio'));
    }

    if (($par{'ARCHIVE_MAXFILESIZE'} ne $conf->{'ARCHIVE_MAXFILESIZE'}) or
	($par{'UPDATE_SCHEDULE'} ne $conf->{'UPDATE_SCHEDULE'}) or
	($par{'ARCHIVE_MAXRECURSION'} ne $conf->{'ARCHIVE_MAXRECURSION'}) or
	($par{'ARCHIVE_MAXFILES'} ne $conf->{'ARCHIVE_MAXFILES'}) or
	($par{'ARCHIVE_BLOCK_ENCRYPTED'} ne $conf->{'ARCHIVE_BLOCK_ENCRYPTED'}) or
	($par{'ARCHIVE_BLOCK_MAX'} ne $conf->{'ARCHIVE_BLOCK_MAX'}) or
	($par{'ARCHIVE_MAXCOMPRESSIONRATIO'} ne $conf->{'ARCHIVE_MAXCOMPRESSIONRATIO'})
	) {


	$conf->{'ARCHIVE_MAXFILESIZE'}=$par{'ARCHIVE_MAXFILESIZE'};
	$conf->{'ARCHIVE_MAXRECURSION'}=$par{'ARCHIVE_MAXRECURSION'};
	$conf->{'ARCHIVE_MAXFILES'}=$par{'ARCHIVE_MAXFILES'};
	$conf->{'ARCHIVE_MAXCOMPRESSIONRATIO'}=$par{'ARCHIVE_MAXCOMPRESSIONRATIO'};

	$conf->{'ARCHIVE_BLOCK_ENCRYPTED'}=$par{'ARCHIVE_BLOCK_ENCRYPTED'};
	$conf->{'ARCHIVE_BLOCK_MAX'}=$par{'ARCHIVE_BLOCK_MAX'};

	$conf->{'UPDATE_SCHEDULE'}=$par{'UPDATE_SCHEDULE'};

	writehash($conffile, $conf);
	setfrequency();
	$do_reload = 1;
    }
    if ($do_reload) {
        `$restart --force`;
        `$restarthavp`;
    }
    return (0,'');
}

sub display_clamsigantures() {
    my $lastupdate = `tac /var/log/clamav/clamd.log| grep -m1 "Database updated"`;
    my $maincvd = `tac /var/log/clamav/clamd.log| grep -m1 "main.cvd"`;
    my $mainupdated = `tac /var/log/clamav/clamd.log| grep -m1 "main.cvd updated"`;
    my $dailycvd = `tac /var/log/clamav/clamd.log| grep -Em1 "daily.(inc|cvd)"`;
    my $dailyupdated = `tac /var/log/clamav/clamd.log| grep -Em1 "daily.(inc|cvd) updated"`;

    my $updatedate = "";
    my $totalsig = "";
    my $from = "";

    my $maincheckdate = "";
    my $mainsig = "";
    my $mainver = "";
    my $mainupdatedate = "";

    my $dailycheckdate = "";
    my $dailysig = "";
    my $dailyver = "";
    my $dailyupdatedate = "";

#root@vienna:/etc/cron.hourly # tac /var/log/clamav/clamd.log| grep -m1 "Database updated"
#Jun 16 20:01:04 vienna freshclam[11765]: Database updated (60044 signatures) from db.local.clamav.net (IP: 129.27.65.27)
    if ($lastupdate =~ /^(... .. ..:..:..)[^\(]+\(([\d]+) signatures\) from ([^\ ]+)/) {
	$updatedate = $1;
	chomp($updatedate);
	$totalsig = $2;
	chomp($totalsig);
	$from = $3;
	chomp($from);
    }


#root@vienna:/etc/cron.hourly # tac /var/log/clamav/clamd.log| grep -m1 "main.cvd"
#Jun 17 20:01:03 vienna freshclam[30846]: main.cvd is up to date (version: 39, sigs: 58116, f-level: 8, builder: tkojm)
    if ($maincvd =~ /^(... .. ..:..:..).*version: ([\d]+), sigs: ([\d]+)/) {
	$maincheckdate = $1;
	chomp($maincheckdate);
	$mainsig = $2;
	chomp($mainsig);
	$mainver = $3;
	chomp($mainver);
    }


#root@vienna:/etc/cron.hourly # tac /var/log/clamav/clamd.log| grep -m1 "main.cvd updated"
    if ($mainupdated =~ /^(... .. ..:..:..).*/) {
	$mainupdatedate = $1;
	chomp($mainupdatedate);
    }

#root@vienna:/etc/cron.hourly # tac /var/log/clamav/clamd.log| grep -m1 "daily.cvd"
#Jun 17 20:01:03 vienna freshclam[30846]: daily.cvd is up to date (version: 1548, sigs: 1928, f-level: 8, builder: ccordes)
    if ($dailycvd =~ /^(... .. ..:..:..).*version: ([\d]+), sigs: ([\d]+)/) {
	$dailycheckdate = $1;
	chomp($dailycheckdate);
	$dailysig = $2;
	chomp($dailysig);
	$dailyver = $3;
	chomp($dailyver);
    }

#root@vienna:/etc/cron.hourly # tac /var/log/clamav/clamd.log| grep -m1 "daily.cvd updated"
#Jun 16 20:01:04 vienna freshclam[11765]: daily.cvd updated (version: 1548, sigs: 1928, f-level: 8, builder: ccordes)
    if ($dailyupdated =~ /^(... .. ..:..:..).*/) {
	$dailyupdatedate = $1;
	chomp($dailyupdatedate);
    }


    $updatedate = value_or_nbsp($updatedate);
    $totalsig = value_or_nbsp($totalsig);
    $from = value_or_nbsp($from);
    $maincheckdate = value_or_nbsp($maincheckdate);
    $mainsig = value_or_nbsp($mainsig);
    $mainver = value_or_nbsp($mainver);
    $mainupdatedate = value_or_nbsp($mainupdatedate);
    $dailycheckdate = value_or_nbsp($dailycheckdate);
    $dailysig = value_or_nbsp($dailysig);
    $dailyver = value_or_nbsp($dailyver);
    $dailyupdatedate = value_or_nbsp($dailyupdatedate);

    openbox('100%', 'left', _('Clamav virus signatures'));

    printf <<END

%s

<br>
<br>
<table cols="5" cellpadding="0" cellspacing="0" class="ruleslist">
    <tr>
        <td  class="boldbase" width="25%"><b>%s</b></td>
        <td   class="boldbase" width="25%"><b>%s</b></td>
        <td   class="boldbase" width="10%"><b>%s</b></td>
        <td   class="boldbase" width="10%"><b>%s</b></td>
        <td   class="boldbase" width="25%"><b>%s</b></td>
    </tr>
    <tr class='oodd'>
        <td>$maincheckdate</td>
        <td>%s</td>
        <td>$mainsig</td>
        <td>$mainver</td>
        <td>$mainupdatedate</td>
    </tr>
    <tr class='even'>
        <td>$dailycheckdate</td>
        <td>%s</td>
        <td>$dailysig</td>
        <td>$dailyver</td>
        <td>$dailyupdatedate</td>
    </tr>
</table>
<br /><br />
<table cellpadding="0" cellspacing="0" border="0"  width="100%">
<tr class="table-footer">
<td>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<div style="margin-top: 6px;">
  <input type="hidden" name="action" value="freshclam">
  <input class='submitbutton net_button' type='submit' name='submit' value="%s" /> %s <span style="text-align: right;"><a href="http://clamav-du.securesites.net/cgi-bin/clamgrok" target="_blank">%s</a></span>
</div>
</form>
</td>
</tr>
</table>
END
,

_('Last signature updated on <b>%s</b> from <b>%s</b> which loaded a total of <b>%s</b> signatures.', $updatedate, $from, $totalsig),
_('Last synchronization check'),
_('Type'),
_('Version'),
_('Count'),
_('Last update'),
_('Main signatures'),
_('Volatile signatures'),
_('Update signatures now'),
_("or"),
_('Search the online virus database')
;
    closebox();

}

sub display() {
    openbox('100%', 'left', _('Clamav configuration'));
    $statusonly = shift;
    printf <<EOF
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <table>
		<tr class="env" >
		<td class="add-div-type" rowspan="6" >%s</td>
        <td><label id="username_field" for="username">%s *</label></td>
        <td colspan="4"><input type="text" name="ARCHIVE_MAXFILESIZE" value="$conf->{'ARCHIVE_MAXFILESIZE'}" SIZE="5" MAXLENGTH="5" /></td>
        </tr>
		<tr class="env">
        <td><label id="password_field" for="password">%s *</label></td>
        <td colspan="4">
		<input type="text" name="ARCHIVE_MAXRECURSION" value="$conf->{'ARCHIVE_MAXRECURSION'}" SIZE="5" MAXLENGTH="5" />
		</td>
        </tr>
		<tr class="env">
		<td><label id="username_field" for="username">%s *</label></td>
        <td colspan="4">
		<input type="text" name="ARCHIVE_MAXFILES" value="$conf->{'ARCHIVE_MAXFILES'}" SIZE="5" MAXLENGTH="5" /></td>
		</tr>
		<tr class="env">
		<td><label id="password_field" for="password">%s *</label></td>
        <td colspan="4">
		<input type="text" name="ARCHIVE_MAXCOMPRESSIONRATIO" value="$conf->{'ARCHIVE_MAXCOMPRESSIONRATIO'}" SIZE="5" MAXLENGTH="5" /></td>
        </tr>
		<tr class="env">
        <td><label id="username_field" for="username">%s *</label></td>
        <td colspan="4">
		<select name="ARCHIVE_BLOCK_MAX">
            <option value="" $block{'pass'}>%s</option>
            <option value="on" $block{'block'}>%s</option>
        </select>
		</td>
        </tr>
		<tr class = "env">
		<td><input type="checkbox" name="ARCHIVE_BLOCK_ENCRYPTED" $checked{$conf->{'ARCHIVE_BLOCK_ENCRYPTED'}} value="on" /></td>
        <td colspan="4"><label id="username_field" for="username">%s</label></td>
        </tr>
        <tr class="odd">
		<td class="add-div-type" rowspan="1" >%s</td>
        <td><input type="radio" name="UPDATE_SCHEDULE" $frequency{'hourly'} value="hourly">
            <label id="username_field" for="username">%s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></label></td>
        <td>
            <input type="radio" name="UPDATE_SCHEDULE" $frequency{'daily'} value="daily">
            <label id="username_field" for="username">%s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></label></td>
        <td>
            <input type="radio" name="UPDATE_SCHEDULE" $frequency{'weekly'} value="weekly">
            <label id="username_field" for="username">%s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></label></td>
        <td>     
            <input type="radio" name="UPDATE_SCHEDULE" $frequency{'monthly'} value="monthly">
            <label id="username_field" for="username">%s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></label></td>
        </tr>
	</table>
	<table class="table-footer">
	<tr><td>
		<input class="net_button" type='submit' name='submit' value='%s' />   
        <input type="hidden" name="action" value="save" />
		</td>
    </tr>
	</table>
 </form>
EOF
,
_('Anti archive bomb'),
_('Max. archive size'),
_('Max. nested archives'),
_('Max. files in archive'),
_('Max compression ratio'),
_('Handle bad archives'),
_('Do not scan but pass'),
_('Block as virus'),
_('Block encrypted archives'),
_('Clamav signature update schedule')
, _('Hourly')
, _('Every hour on that minute when the system has been booted')
, _('Daily')
, _('Every day at that time when the system has been booted')
, _('Weekly')
, _('Every week at that weekday and time when the system has been booted')
, _('Monthly')
, _('Every month on that day and time when the system has been booted')
, _('Save')
;
    closebox();
}

