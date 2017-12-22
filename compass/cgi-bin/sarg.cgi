#!/usr/bin/perl
#
# Sarg CGI for Endian Firewall
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


# -------------------------------------------------------------
# some definitions
# -------------------------------------------------------------

require '/var/efw/header.pl';
my $conffile    = "${swroot}/sarg/settings";
my $conffile_default = "${swroot}/sarg/default/settings";
my $restart     = '/usr/local/bin/restartsarg';
my $sarg_dir    = '/var/www/sarg/';
my $name        = _('Proxy analysis report generator');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked' );

# -------------------------------------------------------------
# get settings and CGI parameters
# -------------------------------------------------------------

my %confhash = ();
my $conf = \%confhash;

if (-e $conffile_default) {
  readhash($conffile_default, $conf);
}
if (-e $conffile) {
  readhash($conffile, $conf);
}

my %par;
getcgihash(\%par);

# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------

sub save() {
    return if ($par{'ACTION'} ne 'save');

    my $logid = "sarg.cgi";
    my $needrestart = 0;
    if ( ($conf->{'SARG_ENABLED'} ne $par{'SARG_ENABLED'}) ) {
        &log(_("%s - writing new configuration file", $logid));
        $needrestart = 1;
        $conf->{'SARG_ENABLED'} = $par{'SARG_ENABLED'};
        $conf->{'SARG_LANGUAGE'} = $par{'SARG_LANGUAGE'};
        writehash($conffile, $conf);
        $notemessage=_('Configuration saved successfully');
    }

    if ($needrestart) {
        print STDERR `$restart`; 
        &log(_("%s - restarting done", $logid));
    }

}



# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------

sub display() {
    openbox('100%', 'left', "$name");
    printf <<EOF
<form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
<input type='hidden' name='ACTION' value='save' />
<table>
  <tr>
    <td>%s:</td>
    <td><input type='checkbox' name='SARG_ENABLED' $checked{$conf->{'SARG_ENABLED'}} /></td>
  </tr>
  <tr>
    <td colspan="2">
      <input class='submitbutton' type='submit' name='submit' value='%s' />
    </td>
  </tr>
</table>
</form>
EOF
,
_('Enable'),
_('Save')
;
    closebox();
}

sub display_report() {
    return if ($conf->{'SARG_ENABLED'} ne 'on');

    openbox('100%', 'left', _('Show proxy analysis reports'));
    if ((! -e "$sarg_dir/daily/index.html") &&
       (! -e "$sarg_dir/weekly/index.html") &&
       (! -e "$sarg_dir/monthly/index.html")) {
        printf <<EOF
  <div>%s</div>
  <div>%s</div>
EOF
, _('There are no reports because there are no log files for this period.')
, _('The report will be generated nightly with the log files of the last day.')
, _('Therefore reports for the current day are not yet available.')

;
    }

    if ( -e "$sarg_dir/daily/index.html") {
        printf <<EOF
  <div>
    <a href='/sarg/daily/index.html' target='_blank'>%s</a>
  </div>
EOF
, _('Daily report')
;
    }

    if ( -e "$sarg_dir/weekly/index.html") {
        printf <<EOF
  <div>
    <a href='/sarg/weekly/index.html' target='_blank'>%s</a>
  </div>
EOF
, _('Weekly report')
;
    }

    if ( -e "$sarg_dir/monthly/index.html") {
        printf <<EOF
  <div>
    <a href='/sarg/monthly/index.html' target='_blank'>%s</a>
  </div>
EOF
, _('Monthly report')
;
EOF
    }
    closebox();
}

showhttpheaders();

openpage($name, 1, '');

save();
&openbigbox($errormessage, $warnmessage, $notemessage);
display();
display_report();

closebigbox();
closepage();

