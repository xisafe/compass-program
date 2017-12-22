#!/usr/bin/perl

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
require '/home/httpd/cgi-bin/endianinc.pl';

my $config_passwd = "${swroot}/spamassassin/spamtrainimap";
my $settings = "${swroot}/spamassassin/settings";
my $default_settings = "${swroot}/spamassassin/default/settings";
my $restartsatrain = "/usr/local/bin/restartsatrain";
my $restartspamassassin = "/usr/local/bin/restartspamassassin";
my $satrain = "/usr/local/bin/learnfromimap";
my $sudosatrain = "sudo /usr/local/bin/learnfromimap.py";
my $pidfile = "/var/run/learnfromimap.pid";

my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $EDIT_PNG = '/images/edit.png';
my $DELETE_PNG = '/images/delete.png';
my $OPTIONAL_PNG = '/images/blob.png';
my $TEST_PNG = '/images/test_connection.png';
my $CONNECTION_OK = '/images/stock_ok.png';
my $CONNECTION_NOTOK = '/images/stock_stop.png';


my (%par,%checked,%selected,%ether,%vpnfw);
my $errormessage = '';
my $reload = 0;
my %confighash=();
my $config = \%confighash;
my %connectiontest_hash = ();
my $connectiontest_values = \%connectiontest_hash;

my %safrequency = ('hourly' => '', 'daily' => '',  'weekly' => '', 'monthly' => '');


sub setsafrequency() {
    $safrequency{'hourly'} = '';
    $safrequency{'daily'} = '';
    $safrequency{'weekly'} = '';
    $safrequency{'monthly'} = '';
    $safrequency{$config->{'SA_UPDATE_SCHEDULE'}} = 'checked="checked"';
}

if (-e $default_settings) {
    &readhash($default_settings, $config);
}
if (-e $settings) {
    &readhash($settings, $config);
}

sub read_config_file() {
    my @lines;
    open (FILE, "$config_passwd");
    foreach my $line (<FILE>) {
    chomp($line);
    if (!is_valid($line)) {
        next;
    }
    push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub read_config_line($) {
    my $line = shift;
    my @lines = read_config_file();
    return $lines[$line];
}

sub save_config_file_back($) {
    my $ref = shift;
    my @lines = @$ref;
    open (FILE, ">$config_passwd");
    foreach my $line (@lines) {
        if ($line ne "") {
        print FILE "$line\n";
        }
    }
    close(FILE);
    $reload = 1;
}

sub append_config_file($) {
    my $line = shift;
    open (FILE, ">>$config_passwd");
    print FILE $line."\n";
    close FILE;
    $reload = 1;
}

sub is_valid($) {
    my $line = shift;
    if ($line =~ /(?:(?:[^,]*),){7}/) {
    return 1;
    }
    return 0;
}

sub config_line($) {
    my $line = shift;
    my %record;
    $record{'valid'} = 0;
    if (! is_valid($line)) {
    return;
    }
    my @temp = split(/,/, $line);
    $record{'enabled'} = $temp[0];
    $record{'host'} = $temp[1];
    $record{'user'} = $temp[2];
    $record{'password'} = $temp[3];
    $record{'ham'} = $temp[4];
    $record{'spam'} = $temp[5];
    $record{'delete'} = $temp[6];
    $record{'remark'} = $temp[7];
    $record{'valid'} = 1;

    return %record;
}

sub toggle_enable($$) {
    my $line = shift;
    my $enable = shift;
    if ($enable) {
    $enable = 'on';
    } else {
    $enable = 'off';
    }

    my %data = config_line(read_config_line($line));
    $data{'enabled'} = $enable;

    return save_line($line,
             $data{'enabled'},
             $data{'host'},
             $data{'user'},
             $data{'password'},
             $data{'ham'},
             $data{'spam'},
             $data{'delete'},
             $data{'remark'});
}

sub delete_line($) {
    my $line = shift;
    my @lines = read_config_file();
    if (! @lines[$line]) {
    return;
    }
    delete (@lines[$line]);
    save_config_file_back(\@lines);
}

sub create_line($$$$$$$$) {

    my $enabled = shift;
    my $host = shift;
    my $user = shift;
    my $password = shift;
    my $ham = shift;
    my $spam = shift;
    my $delete = shift;
    my $remark = shift;

    return "$enabled,$host,$user,$password,$ham,$spam,$delete,$remark";
}

sub check_values($$$$$$$$$) {
    my $enabled = shift;
    my $host = shift;
    my $user = shift;
    my $password = shift;
    my $ham = shift;
    my $spam = shift;
    my $delete = shift;
    my $line = shift;


    $user =~ s/\,//g;
    $password =~ s/\,//g;
    $ham =~ s/\,//g;
    $spam =~ s/\,//g;
    $remark =~ s/\,//g;

    foreach my $value qw($user $password $ham $spam $remark) {
        if ($value =~ /,/) {
            if ($line) {
            $errormessage .= _('Illegal character "," in value "%s" of line %s!', $value, $line)."<br><br>";
            } else {
            $errormessage .= _('Illegal character "," in value "%s"!', $value)."<br><br>";
            }
        return 0;
        }
    }

    return 1;
}

sub save_line($$$$$$$$$) {
    my $line = shift;
    my $enabled = shift;
    my $host = shift;
    my $user = shift;
    my $password = shift;
    my $ham = shift;
    my $spam = shift;
    my $delete = shift;
    my $remark = shift;

    if (! check_values($enabled, $host, $user, $password, $ham, $spam, $delete, $remark, 0)) {
    return 0;
    }

    my $tosave = create_line($enabled, $host, $user, $password, $ham, $spam, $delete, $remark);

    if ($line !~ /^\d+$/) {
    append_config_file($tosave);
    return 1;
    }
    my @lines = read_config_file();
    if (! $lines[$line]) {
    $errormessage = _('Configuration line not found!');
    return 0;
    }

    my %split = config_line($lines[$line]);
    if (($split{'enabled'} ne $enabled) ||
    ($split{'host'} ne $host) ||
    ($split{'user'} ne $user) ||
    ($split{'password'} ne $password) ||
    ($split{'ham'} ne $ham) ||
    ($split{'spam'} ne $spam) ||
    ($split{'delete'} ne $delete) ||
    ($split{'remark'} ne $remark)) {
    $lines[$line] = $tosave;
    save_config_file_back(\@lines);
    }
    return 1;
}

sub is_running_salearn() {
    return 0 if (! -e $pidfile);
    my $pid = getpid($pidfile);
    return 0 if ($pid == 0);
    return 0 if (! -e "/proc/$pid/status");
    return 1;
}


sub display_entries($$) {
    my $is_editing = shift;
    my $line = shift;

    my %checked;

    printf <<END
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td align="right">
      <form method="post" class="more_button" style="float:right;margin-top:10px;">
        <input type="hidden" name="ACTION" value="test_connections" >
        <input name="save" value="%s" type="submit"  class= "net_button">
      </form>
END
, _('Test all connections')
;

    if (is_running_salearn()) {
        printf _('Training is running ...');
    } else {
        printf <<END
      <form method="post" class="more_button" style="float:right;margin-top:10px;">
        <input type="hidden" name="ACTION" value="start"  >
        <input name="save" value="%s" type="submit"  class= "net_button">
      </form>
END
, _('Start training now')
;
    }

    printf <<END
    </td>
  </tr>
</table>
END
;

display_default();

display_add($is_editing, $line);

printf <<END
<table width="100%" class="ruleslist" cellpadding="0" cellspacing="0">
  <tr>
    <td class="boldbase" width="15%">%s</td>
    <td class="boldbase" width="15%">%s</td>
    <td class="boldbase" width="15%">%s</td>
    <td class="boldbase" width="15%">%s</td>
    <td class="boldbase" width="10%">%s</td>
    <td class="boldbase" style="width: 60px;" colspan="2">%s</td>
    <td class="boldbase" style="width: 120px;">%s</td>
  </tr>

END
, _('IMAP Host')
, _('Username')
, _('Ham folder')
, _('Spam folder')
, _('Remark')
, _('Connection')
, _('Actions')
;

    my @lines = read_config_file();
    my $i = 0;
	my $length = @lines;
if($length >0)
{
    foreach my $thisline (@lines) {
    chomp($thisline);
    my %splitted = config_line($thisline);

    if (! $splitted{'valid'}) {
        $i++;
        next;
    }

    my $host = value_or_nbsp($splitted{'host'});
    my $user = value_or_nbsp($splitted{'user'});
    my $ham = value_or_nbsp($splitted{'ham'});
    my $spam = value_or_nbsp($splitted{'spam'});
    my $remark = value_or_nbsp($splitted{'remark'});

        if ($splitted{'host'} =~ /^$/) {
            $host = "<i>".value_or_nbsp($config->{'DEFAULT_HOST'})."</i>";
        }
        if ($splitted{'user'} =~ /^$/) {
            $user = "<i>".value_or_nbsp($config->{'DEFAULT_USERNAME'})."</i>";
        }
        if ($splitted{'spam'} =~ /^$/) {
            $spam = "<i>".value_or_nbsp($config->{'DEFAULT_SPAMFOLDER'})."</i>";
        }
        if ($splitted{'ham'} =~ /^$/) {
            $ham = "<i>".value_or_nbsp($config->{'DEFAULT_HAMFOLDER'})."</i>";
        }

    my $enabled_gif = $DISABLED_PNG;
    my $enabled_alt = _('Disabled (click to enable)');
    my $enabled_action = 'enable';
    if ($splitted{'enabled'} eq 'on') {
        $enabled_gif = $ENABLED_PNG;
        $enabled_alt = _('Enabled (click to disable)');
        $enabled_action = 'disable';
    }

    my $connection_status = "";
    my $connection_info = "";

        if ($connectiontest_values) {
            my $testdata = $connectiontest_values->{$i+1};
            if ($testdata->{'status'} eq 'OK') {
                $connection_status = $CONNECTION_OK;
                $connection_info = _('Connection to IMAP server is OK');
            } elsif ($testdata->{'status'} eq 'NOT OK') {
                $connection_status = $CONNECTION_NOTOK;
                my $errormsg = $testdata->{'error'};
                $errormsg =~ s/\"//g;
                $errormsg =~ s/\'//g;
                $connection_info = _('Error connecting to IMAP server (%s)', $errormsg);
            }
        }

    my $enabled_gif = $DISABLED_PNG;
    my $enabled_alt = _('Disabled (click to enable)');
    my $enabled_action = 'enable';
    if ($splitted{'enabled'} eq 'on') {
        $enabled_gif = $ENABLED_PNG;
        $enabled_alt = _('Enabled (click to disable)');
        $enabled_action = 'disable';
    }

    my $bgcolor = setbgcolor($is_editing, $line, $i);

        printf <<EOF
  <tr class="$bgcolor">
    <td align="center" VALIGN="top">$host</td>
    <td align="center" VALIGN="top">$user</td>
    <td align="center" VALIGN="top">$ham</td>
    <td align="center" VALIGN="top">$spam</td>
    <td align="center" VALIGN="top">$remark</td>

EOF
;


        if ($connection_status !~ /^$/) {
            printf <<EOF
    <td VALIGN="top">
      <a href="javascript:void(0);" onmouseover="return overlib('$connection_info',STICKY, MOUSEOFF);" onmouseout="return nd();"><img SRC="$connection_status"></a>
    </td>

EOF
;
        } else {
            printf <<EOF
    <td>&nbsp;</td>
EOF
;
        }


        printf <<EOF

    <td valign="top">
      <form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
        <input class='imagebutton' type='image' name="submit" SRC="$TEST_PNG" ALT="%s" />
        <input type="hidden" name="ACTION" VALUE="test_connection">
        <input type="hidden" name="line" VALUE="$i">
      </form>
    </td>
    <td class="actions">
      <form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
        <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" ALT="$enabled_alt" />
        <input type="hidden" name="ACTION" VALUE="$enabled_action">
        <input type="hidden" name="line" VALUE="$i">
      </form>
      <form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
        <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s" />
        <input type="hidden" name="ACTION" VALUE="edit">
        <input type="hidden" name="line" VALUE="$i">
      </form>
      <form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
        <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s" />
        <input type="hidden" name="ACTION" VALUE="delete">
        <input type="hidden" name="line" VALUE="$i">
      </form>
    </td>
  </tr>

EOF
, _('Test')
, _('Edit')
, _('Remove');

    $i++;
    }
}else{
	no_tr(8,_('Current no content'));
}


    printf <<EOF
</table>
EOF
;
if($length >0)
{
printf <<EOF
<table class="list-legend" cellpadding="0" cellspacing="0">
  <tr>
    <td><b>%s:</b>
    <img SRC="$ENABLED_PNG" ALT="%s" />
    %s
    <img SRC='$DISABLED_PNG' ALT="%s" />
    %s
    <img SRC="$EDIT_PNG" alt="%s" />
    %s
    <img SRC="$DELETE_PNG" ALT="%s" />
    %s
    <img SRC="$TEST_PNG" ALT="%s" />
    %s</td>
  </tr>
</table>
EOF
, _('Legend')
, _('Enabled (click to disable)')
, _('Enabled (click to disable)')
, _('Disabled (click to enable)')
, _('Disabled (click to enable)')
, _('Edit')
, _('Edit')
, _('Remove')
, _('Remove')
, _('Test connection')
, _('Test connection')
;


    &closebox();
   } 
}

sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;
    my %conf;
    my %checked;
    my %selected;

    if (($is_editing) && ($par{'sure'} ne 'y')) {
    %conf = config_line(read_config_line($line));
    } else {
    %conf = %par;
    }

    my $enabled = $conf{'enabled'};
    my $remove_mails = $conf{'delete'};
    my $remark = $conf{'remark'};

    my $host = $conf{'host'};
    my $user = $conf{'user'};
    my $password = $conf{'password'};
    my $spam = $conf{'spam'};
    my $ham = $conf{'ham'};

    $checked{'enabled'}{'on'} = 'checked';
    $checked{'delete'}{'on'} = 'checked';

    my $action = 'add';
    my $sure = '';
    my $title = _('Add IMAP spam training source');
    if ($is_editing) {
    $action = 'edit';
    $sure = '<input type="hidden" name="sure" VALUE="y">';
    $title = _('Edit IMAP spam training source');
    }
    my $show = "";
    if ($is_editing) {
        #print "<div id=\"ruleedit\" style=\"display: block\">\n";
        $show = "showeditor";
    }
    else {
        #print "<div id=\"ruleedit\" style=\"display: none\">\n";
    }

    &openeditorbox($title, $title, $show, "createrule", @errormessages);
    
    printf <<EOF
  <table width="100%" columns="4">
    <tr class="env">
      <td>%s</td>
      <td><input type='checkbox' name='enabled' $checked{'enabled'}{$enabled} value='on' /></td>
      <td>%s</td>
      <td><input type='text' name='remark' size='30' value="$remark" /></td>
    </tr>
    <tr class="odd">
      <td>%s</td>
      <td><input type='text' name='host' size='30' value="$host" /></td>
      <td>%s</td>
      <td><input type='checkbox' name='delete' $checked{'delete'}{$remove_mails} value='on' /></td>
    </tr>
    <tr class="env">
      <td>%s</td>
      <td><input type='text' name='user' size='20' value="$user" /></td>
      <td>%s</td>
      <td><input type='password' name='password' size='20' value="$password" /></td>
    </tr>
    <tr class="odd">
      <td>%s</td>
      <td><input type='text' name='ham' size='20' value="$ham" /></td>
      <td>%s</td>
      <td><input type='text' name='spam' size='20' value="$spam" /></td>
    </tr>
    <tr class="odd">
      <td colspan="4" class="note">%s</td>
    </tr>
    <input type="hidden" name="ACTION" value="$action">
    <input type="hidden" name="line" value="$line">
    <input type="hidden" name="sure" value="y">
  </table>
EOF
, _('Enabled')
, _('Remark')

, _('IMAP Host')
, _('Delete processed mails')
, _('Username')
, _('Password')

, _('Ham folder')
, _('Spam folder')

, _('Leave field blank where you want to use the respective default value')
, _('Save')
;

    &closeeditorbox(($par{'ACTION'} eq 'add' || $par{'ACTION'} eq '' || $par{'ACTION'} eq 'save' ? _("Add Training Source") : _("Update Training Source")), _("Cancel"), "createrule", "createrule", $ENV{'SCRIPT_NAME'});
    
    # end of ruleedit div
    #print "</div>"

}


sub display_default() {
    my $host = $config->{'DEFAULT_HOST'};
    my $user = $config->{'DEFAULT_USERNAME'};
    my $password = $config->{'DEFAULT_PASSWORD'};
    my $spam = $config->{'DEFAULT_SPAMFOLDER'};
    my $ham = $config->{'DEFAULT_HAMFOLDER'};

    if ($config->{'UPDATE_SCHEDULE'} =~ /^$/) {
        $config->{'UPDATE_SCHEDULE'} = 'disabled';
    }
    my %frequency = ();
    $frequency{$config->{'UPDATE_SCHEDULE'}} = 'checked="checked"';

    

    &openbox('100%', 'left', _("Edit configuration"));
    printf <<EOF
<form action="$ENV{'SCRIPT_NAME'}" method="post" enctype='multipart/form-data'>
  <input type="hidden" name="ACTION" value="save">
  <table width="100%" columns="4">
    <tr class="env">
      <td class="add-div-type" rowspan="5">%s</td>
	  <td>%s</td>
      <td colspan="4"><input type='text' name='DEFAULT_HOST' size='30' value="$host" /></td>
    </tr>
    <tr class="env">
      <td>%s</td>
      <td colspan="4"><input type='text' name='DEFAULT_USERNAME' size='20' value="$user" /></td>
	  </tr>
	<tr class="env">
      <td>%s</td>
      <td colspan="4"><input type='password' name='DEFAULT_PASSWORD' size='20' value="$password" /></td>
    </tr>
    <tr class="env">
      <td>%s</td>
      <td colspan="4"><input type='text' name='DEFAULT_HAMFOLDER' size='20' value="$ham" /></td>
	</tr>
	<tr class="env">
      <td>%s</td>
      <td colspan="4"><input type='text' name='DEFAULT_SPAMFOLDER' size='20' value="$spam" /></td>
    </tr>

<!--
    <tr class="env">
      <td colspan="4"><b>%s</b></td>
    </tr>
    <tr class="odd">
      <td>%s</td>
      <td><input type="file" name="IMPORT_FILE"> <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a>
      </td>
      <td>%s</td>
      <td><input type='radio' name='IMPORT_TYPE' value="merge" checked /></td>
    </tr>
    <tr class="env">
      <td colspan="2">&nbsp;</td>
      <td>%s</td>
      <td  ><input type='radio' name='IMPORT_TYPE' value="replace" /></td>
    </tr>
-->
 
    <tr class="odd">
      <td class="add-div-type" >%s</td>
	  <td><input type="radio" name="UPDATE_SCHEDULE" $frequency{'disabled'} value="disable"> %s </td>
      <td><input type="radio" name="UPDATE_SCHEDULE" $frequency{'hourly'} value="hourly"> %s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></td>
      <td><input type="radio" name="UPDATE_SCHEDULE" $frequency{'daily'} value="daily"> %s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></td>
      <td><input type="radio" name="UPDATE_SCHEDULE" $frequency{'weekly'} value="weekly"> %s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></td>
      <td><input type="radio" name="UPDATE_SCHEDULE" $frequency{'monthly'} value="monthly"> %s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></td>
    </tr>
    
    <tr class="table-footer">
      <td align="center" colspan="6">
        <input type='submit' name='submit' value='%s' class="net_button" />
      </td>
    </tr>
  </table>

</form>
EOF
, _('Default config')
, _('Default IMAP host')
, _('Default username')
, _('Default password')

, _('Default ham folder')
, _('Default spam folder')

, _('Import spam training sources at once')
, _('Import CSV file')
, _('File format: enabled (on/off),hostname,username,password,spam folder,ham folder,remove processed mails,remark')
, _('Merge with configuration')
, _('Replace configuration')

, _('Schedule for automatic spam filter training')
, _('Disabled')
, _('Hourly')
, _('Every hour one minute after the full hour. (XX:01)')
, _('Daily')
, _('Every day at 01:25 am')
, _('Weekly')
, _('Every Sunday at 02:47 am')
, _('Monthly')
, _('Every 1st day of month on 03:52 am')

, _('Save')
;


    &closebox();

    # end of ruleedit div

}

sub reset_values() {
    %par = ();
}

sub store_config() {
    if (($par{'DEFAULT_HOST'} ne $config->{'DEFAULT_HOST'}) or
        ($par{'UPDATE_SCHEDULE'} ne $config->{'UPDATE_SCHEDULE'}) or
        ($par{'DEFAULT_USERNAME'} ne $config->{'DEFAULT_USERNAME'}) or
        ($par{'DEFAULT_PASSWORD'} ne $config->{'DEFAULT_PASSWORD'}) or
        ($par{'DEFAULT_SPAMFOLDER'} ne $config->{'DEFAULT_SPAMFOLDER'}) or
        ($par{'DEFAULT_HAMFOLDER'} ne $config->{'DEFAULT_HAMFOLDER'}) or
	($par{'SA_UPDATE_SCHEDULE'} ne $config->{'SA_UPDATE_SCHEDULE'})
        ) {

        $config->{'DEFAULT_HOST'}=$par{'DEFAULT_HOST'};
        $config->{'DEFAULT_USERNAME'}=$par{'DEFAULT_USERNAME'};
        $config->{'DEFAULT_PASSWORD'}=$par{'DEFAULT_PASSWORD'};
        $config->{'DEFAULT_SPAMFOLDER'}=$par{'DEFAULT_SPAMFOLDER'};
        $config->{'DEFAULT_HAMFOLDER'}=$par{'DEFAULT_HAMFOLDER'};
        $config->{'UPDATE_SCHEDULE'}=$par{'UPDATE_SCHEDULE'};
        $config->{'SA_UPDATE_SCHEDULE'}=$par{'SA_UPDATE_SCHEDULE'};
        if (!(check_default_value($par{'DEFAULT_HOST'},$par{'DEFAULT_USERNAME'},$par{'DEFAULT_HAMFOLDER'},$par{'DEFAULT_SPAMFOLDER'}))) {
			return 0;
        }
        writehash($settings, $config);
        $reload = 1;
    }

#    if (ref ($par{'IMPORT_FILE'}) eq 'Fh')  {
#        save_csv();
#    }

}
##elvis check_value
sub check_default_value(){
	my $host = shift;
    my $user = shift;
	my $ham = shift;
	my $spam = shift;
    if (!validhostname($host)) {
        $errormessage = _('Invalid hostname.');
	    return 0;
    }
	if ($user !~ /^([A-Za-z0-9_])+$/) {
        $errormessage = _('Username must not include illegal characters');
        return 0;
    }
	if ($ham !~ /^([A-Za-z0-9_])+$/) {
        $errormessage = _('Hamfolder must not include illegal characters');
        return 0;
    }
	if ($spam !~ /^([A-Za-z0-9_])+$/) {
        $errormessage = _('Spamfolder must not include illegal characters');
        return 0;
    }
	return 1;
}
###
sub search_config($$$$$$$$) {
    my $lines = shift;
    my @config = @$lines;
    my $host = shift;
    my $user = shift;
    my $ham = shift;
    my $spam = shift;

    my $i = 0;
    foreach my $line (@config) {
        $i++;
        my %splitted = config_line($line);
        next if ($splitted{'host'} ne $host);
        next if ($splitted{'user'} ne $user);
        next if ($splitted{'ham'} ne $ham);
        next if ($splitted{'spam'} ne $spam);
        return $i;
    }
}

sub save_csv() {
    my @lines = ();
    if ($par{'IMPORT_TYPE'} eq 'merge') {
        @lines = read_config_file();
    }

    my $FH = $par{'IMPORT_FILE'};
    my $i = 0;
    foreach my $importline (<FH>) {
        my $i++;
        my %config = config_line($importline);
        if (! $config{'valid'}) {
            $errormessage .= _('Invalid format in line "%s"', $i)."<br><br>";
            next;
        }
        if (! check_values($config{'enabled'}, $config{'host'}, $config{'user'},
                           $config{'password'}, $config{'ham'}, $config{'spam'}, $config{'delete'}, $config{'remark'}, $i)) {
            next;
        }
        my $line = search_config(\@lines, $config{'enabled'}, $config{'host'}, $config{'user'},
                                 $config{'password'}, $config{'ham'}, $config{'spam'}, $config{'delete'});

        if ($line != -1) {
            $line = $lines;
            $lines[$line] = $importline;
            next;
        }
        $lines[$#lines +1] = $importline;
    }
}

sub execparse_conntest($) {
    my $cmd = shift;

    use IPC::Open3;
    $pid = open3(\*WRITE, \*READ, \*ERROR, $cmd);
    if (! $pid) {
        $err = _('Could not start connection check');
    }
    close WRITE;
    close READ;

    my @error = <ERROR>;
    close ERROR;
    waitpid($pid,0);

    my $singlestatus = "";
    foreach my $line (@error) {
        my %hash = ();
        my $hash_ref = \%hash;
        my $num = -1;

        if ($line =~ /\s+\{(\d+)\}\s+\S+\s+(.*)$/) {
            my $number = $1;
            chomp($number);
            $num = $number;

            my $val = $2;
            chomp($val);

            if ($val =~ /TEST OK/) {
                $hash_ref->{'status'} = 'OK';
            } else {
                $hash_ref->{'status'} = 'NOT OK';
                $hash_ref->{'error'} = $val;
            }
            $connectiontest_values->{$num} = $hash_ref;
        }
        if ($line =~ /TEST OK/) {
            $singlestatus = "TEST OK";
        }
        if ($line =~ /ERROR\s+\S+:\s(.*)$/) {
            my $err = $1;
            chomp($err);
            $singlestatus = $err;
        }

    }
    return $singlestatus;
}

sub check_connection($) {
    my $line = shift;
    my %conf = config_line(read_config_line($line));

    my %hash = ();
    my $hash_ref = \%hash;
    $connectiontest_values->{$line} = $hash_ref;

    if ($conf{'enabled'} ne 'on') {
        $hash_ref->{'status'} = 'NOT OK';
        $hash_ref->{'error'} = _('Connection is disabled');
        return;
    }

    my $host = $config->{'DEFAULT_HOST'};
    my $username = $config->{'DEFAULT_USERNAME'};
    my $password = $config->{'DEFAULT_PASSWORD'};
    my $ham = $config->{'DEFAULT_HAMFOLDER'};
    my $spam = $config->{'DEFAULT_SPAMFOLDER'};

    if ($conf{'host'} ne '') {
        $host = $conf{'host'};
    }
    if ($conf{'user'} ne '') {
        $user = $conf{'user'};
    }
    if ($conf{'password'} ne '') {
        $password = $conf{'password'};
    }
    if ($conf{'spam'} ne '') {
        $spam = $conf{'spam'};
    }
    if ($conf{'ham'} ne '') {
        $ham = $conf{'ham'};
    }

    my $opt = "--host $host --username $user --password $password ";
    if ($ham ne "") {
        $opt = "$opt --ham $ham ";
    }
    if ($spam ne "") {
        $opt = "$opt --spam $spam ";
    }

    my %hash = ();
    my $hash_ref = \%hash;
    my $errmsg = execparse_conntest("$sudosatrain --test $opt");
    if ($errmsg eq 'TEST OK') {
        $hash_ref->{'status'} = 'OK';
    } else {
        $hash_ref->{'status'} = 'NOT OK';
        $hash_ref->{'error'} = $errmsg;
    }
    $connectiontest_values->{$line+1} = $hash_ref;
}

sub check_connections() {
    return if (! -e $config_passwd);

    my $opt = '';
    my $host = $config->{'DEFAULT_HOST'};
    my $username = $config->{'DEFAULT_USERNAME'};
    my $password = $config->{'DEFAULT_PASSWORD'};
    my $ham = $config->{'DEFAULT_HAMFOLDER'};
    my $spam = $config->{'DEFAULT_SPAMFOLDER'};

    if ($host ne "") {
        $opt = "$opt --host $host";
    }
    if ($user ne "") {
        $opt = "$opt --username $user";
    }
    if ($ham ne "") {
        $opt = "$opt --ham $ham ";
    }
    if ($spam ne "") {
        $opt = "$opt --spam $spam ";
    }

    execparse_conntest("$sudosatrain $opt --test --csv $config_passwd");
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    if ($action eq 'save') {
    store_config();
    return;
    }
    if ($action eq 'test_connection') {
        check_connection($par{'line'});
        return;
    }
    if ($action eq 'test_connections') {
        check_connections();
        return;
    }
    if ($action eq 'start') {
        return if (! -e $config_passwd);
        return if (is_running_());

        my $opt = "";

        if ($config->{'DEFAULT_HOST'} !~ /^$/) {
            $opt="$opt --host ".$config->{'DEFAULT_HOST'};
        }
        if ($config->{'DEFAULT_USERNAME'} !~ /^$/) {
            $opt="$opt --username ".$config->{'DEFAULT_USERNAME'};
        }
        if ($config->{'DEFAULT_PASSWORD'} !~ /^$/) {
            $opt="$opt --password ".$config->{'DEFAULT_PASSWORD'};
        }
        if ($config->{'DEFAULT_HAMFOLDER'} !~ /^$/) {
            $opt="$opt --ham ".$config->{'DEFAULT_HAMFOLDER'};
        }
        if ($config->{'DEFAULT_SPAMFOLDER'} !~ /^$/) {
            $opt="$opt --spam ".$config->{'DEFAULT_SPAMFOLDER'};
        }

        `$satrain $opt --csv $config_passwd`;
        sleep(1);

        return;
    }


    if ($action eq 'delete') {
    delete_line($par{'line'});
    reset_values();
    return;
    }

    if ($action eq 'enable') {
    return if (toggle_enable($par{'line'}, 1));
    }
    if ($action eq 'disable') {
    return if (toggle_enable($par{'line'}, 0));
    }

    if ($action eq 'save_schedule') {
	store_config();
	`$restartspamassassin --re-schedule`;
	return;
    }
 
    # ELSE
    if (($action eq 'add') ||
    (($action eq 'edit')&&($sure eq 'y'))) {


    my $enabled = $par{'enabled'};
    if (save_line($par{'line'},
          $enabled,
          $par{'host'},
          $par{'user'},
          $par{'password'},
          $par{'ham'},
          $par{'spam'},
          $par{'delete'},
          $par{'remark'},
         )) {
    reset_values();
    }
    }
}

sub display_schedule() {
    setsafrequency();
    printf <<EOF
<form action="$ENV{'SCRIPT_NAME'}" method="post" enctype='multipart/form-data'>
  <input type="hidden" name="ACTION" value="save_schedule" />
<table  width="100%">
  <tr class="env">
    <td class="add-div-type" >%s</td>
    <td><input type="radio" name="SA_UPDATE_SCHEDULE" $safrequency{'hourly'} value="hourly"> %s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></td>
    <td><input type="radio" name="SA_UPDATE_SCHEDULE" $safrequency{'daily'} value="daily"> %s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></td>
    <td><input type="radio" name="SA_UPDATE_SCHEDULE" $safrequency{'weekly'} value="weekly"> %s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></td>
    <td><input type="radio" name="SA_UPDATE_SCHEDULE" $safrequency{'monthly'} value="monthly"> %s <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">?</a></td>
  </tr>

  <tr class="table-footer">
    <td colspan="5">
      <input class='net_button' type='submit' name='save_update' value='%s' />
    </td>
  </tr>
</table>
</form>
EOF
, _('Schedule for SpamAssassin rule updates')
, _('Hourly')
, _('Every hour one minute after the full hour. (XX:01)')
, _('Daily')
, _('Every day at 01:25 am')
, _('Weekly')
, _('Every Sunday at 02:47 am')
, _('Monthly')
, _('Every 1st day of month on 03:52 am')
, _('Save');
}

&getcgihash(\%par, {'wantfile' => 1, 'filevar' => 'IMPORT_FILE'});

&showhttpheaders();
&openpage(_('Spam filter training'), 1);

save();

&openbigbox($errormessage, $warnmessage, $notemessage);

my $is_editing = ($par{'ACTION'} eq 'edit');


display_entries($is_editing, $par{'line'});

&openbox('100%','left', _('SpamAssassin Rule Update Schedule'));
display_schedule();
&closebox();

if ($reload) {
    `$restartsatrain`;
}

&closebigbox();
&closepage();
