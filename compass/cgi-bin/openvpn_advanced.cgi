#!/usr/bin/perl
#
# openvpn CGI for Endian Firewall
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
require './endianinc.pl';
use Net::IPv4Addr qw (:all);
use File::Copy;
use File::Temp qw/ tempdir tempfile/;
use IPC::Open3;

my $conffile = "${swroot}/openvpn/settings";
my $conffile_default = "${swroot}/openvpn/default/settings";
my $hostconffile = "${swroot}/host/settings";
my $etherconf = "${swroot}/ethernet/settings";
my $restart  = '/usr/local/bin/run-detached /usr/local/bin/restartopenvpn';
my $openvpn_diffie = '/var/efw/openvpn/dh1024.pem';
my $openvpn_diffie_lock = '/var/lock/openvpn_diffie.lock';

my $PKCS_FILE = '/var/efw/openvpn/pkcs12.p12';
my $PKCS_IMPORT_FILE = "${PKCS_FILE}.import";
my $CACERT_FILE = '/var/efw/openvpn/cacert.pem';
my $CRL_FILE = '/var/efw/openvpn/crl.pem';
my $SUBJECT_FILE = '/var/efw/openvpn/subject.txt';
my $ISSUER_FILE = '/var/efw/openvpn/issuer.txt';

my $dirtyfile  = '/var/efw/openvpn/dirtyuserconfig';

my $name        = _('OpenVPN server');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked="checked"');
my %selected = ();
my $self = $ENV{SCRIPT_NAME};

my %par;
my %confhash = ();
my $conf = \%confhash;
my $pool_begin = '';
my $pool_end = '';
my $port = '';
my $protocol = '';
my $netpart = undef;
my $ether = undef;
my $enabled = 0;
my $action = '';
my $errormessage = '';
my $err = 1;
my $block_dhcp = '';
my $config = 0;
my %hosthash = ();
my $host = \%hosthash;

my $globalnetworks = '';
my $globalnameserver = '';
my $domain = '';
my ($a, $b);
my $abcast = '';
my $bnetwork = '';

sub restart() {
    my $logid = "$0 [" . scalar(localtime) . "]";
    print STDERR `$restart --force`; 
    print STDERR "$logid: restarting done\n";
    $notemessage = _('OpenVPN server has been restarted!');
}

sub ip2long {
    return unpack("l*", pack("l*", unpack("N*", inet_aton(shift))));
}

sub long2ip {
    return inet_ntoa(pack("N*", shift));
}

sub smallPools() {
    my $ip = $ether->{GREEN_NETADDRESS};
    my $cidr = int($ether->{GREEN_CIDR}) + 1;

    my $a = "$ip/$cidr";

    my $broadcast = ipv4_broadcast($a);
    $ip = long2ip(ip2long($broadcast) + 1);
    my $b = "$ip/$cidr";

    return ($a, $b);
}

sub save () {

    $config = \%par;
    my $logid = "$0 [" . scalar(localtime) . "]";
    my $needrestart = 0;
    my $ippool_begin = $par{PURPLE_IP_BEGIN};
    my $ippool_end = $par{PURPLE_IP_END};
    $block_dhcp = $par{DROP_DHCP};
    $port = $par{PORT};
    $protocol = $par{PROTOCOL};
    local $auth_type = $par{AUTH_TYPE};
    my $ret = 0;
    my $error = '';

    if (! validport($par{PORT})) {
	return (0, _('Invalid port'));
    }

    if ( ($conf->{PURPLE_IP_BEGIN} ne $ippool_begin) or
	 ($conf->{PURPLE_IP_END} ne $ippool_end) or
	 ($conf->{CLIENT_TO_CLIENT} ne $par{CLIENT_TO_CLIENT}) or
	 ($conf->{DROP_DHCP} ne $par{DROP_DHCP}) or
	 ($conf->{PORT} ne $par{PORT}) or
	 ($conf->{PROTOCOL} ne $par{PROTOCOL}) or
	 ($conf->{PUSH_GLOBAL_NETWORKS} ne $par{PUSH_GLOBAL_NETWORKS}) or
	 ($conf->{GLOBAL_NETWORKS} ne $par{GLOBAL_NETWORKS}) or
	 ($conf->{PUSH_GLOBAL_DNS} ne $par{PUSH_GLOBAL_DNS}) or
	 ($conf->{GLOBAL_DNS} ne $par{GLOBAL_DNS}) or
	 ($conf->{PUSH_DOMAIN} ne $par{PUSH_DOMAIN}) or
	 ($conf->{DOMAIN} ne $par{DOMAIN}) or
	 ($conf->{AUTH_TYPE} ne $par{AUTH_TYPE})
	 ) {
	print STDERR "$logid: writing new configuration file\n";
	$needrestart = 1;

	$conf->{PURPLE_IP_BEGIN} = $ippool_begin;
	$conf->{PURPLE_IP_END} = $ippool_end;
	$conf->{CERT_AUTH} = $par{CERT_AUTH};
	$conf->{DROP_DHCP} = $par{DROP_DHCP};

	$conf->{PROTOCOL} = $par{PROTOCOL};
	$conf->{PORT} = $par{PORT};
	$conf->{AUTH_TYPE} = $par{AUTH_TYPE};

	$conf->{PUSH_GLOBAL_NETWORKS} = $par{PUSH_GLOBAL_NETWORKS};
	$conf->{PUSH_GLOBAL_DNS} = $par{PUSH_GLOBAL_DNS};
	$conf->{GLOBAL_NETWORKS} = $par{GLOBAL_NETWORKS};
	$conf->{GLOBAL_DNS} = $par{GLOBAL_DNS};
	$conf->{GLOBAL_NETWORKS} =~ s/[\r\n]+/,/g;
	$conf->{GLOBAL_DNS} =~ s/[\r\n]+/,/g;

	$conf->{PUSH_DOMAIN} = $par{PUSH_DOMAIN};
	$conf->{DOMAIN} = $par{DOMAIN};

	$conf->{CLIENT_TO_CLIENT} = $par{CLIENT_TO_CLIENT};
	$conf->{OPENVPN_ENABLED} = $par{OPENVPN_ENABLED};
	$config = $conf;

	writehash($conffile, $conf);
        &log(_('Written down Openvpn configuration'));
    }

    ($errcode, $errstr) = import_p12();
    if ($errcode == 0) {
        return ($errcode, $errstr);
    }

    print STDERR `$restart --force`; 
    print STDERR "$logid: restarting done\n";
    return 1;
}

sub crlimport() {
    return if (ref ($par{'IMPORT_FILE'}) ne 'Fh');

    my ($fh, $tmpfile) = tempfile("import.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.pem');
    if (!copy ($par{'IMPORT_FILE'}, $fh)) {
	return (0, _('Unable to import certificate revocation list file \'%s\'', $par{'IMPORT_FILE'}, $!));
    }
    close($fh);

    if (`openssl crl -in $tmpfile -text 2>&1 >/dev/null` !~ /^$/) {
        unlink($tmpfile);
        return (0, _('Invalid certificate revocation list! Import failed!'));
    }

    if (! move($tmpfile, $CRL_FILE)) {
        unlink($tmpfile);
        return (0, _('Could not bring imported certificate revocation list file in place! (%s)', $!));
    }
    $notemessage = _('Certificate revocation list has been imported successfully!');
    return 1;
}

sub import_p12() {
    return 1 if (ref ($par{'IMPORT_FILE'}) ne 'Fh');

    my ($fh, $tmpfile) = tempfile("import.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.p12');
    if (!copy ($par{'IMPORT_FILE'}, $fh)) {
	return (0, _('Unable to import PKCS#12 file \'%s\'', $par{'IMPORT_FILE'}, $!));
    }
    close($fh);

    if ($par{'IMPORT_PASSWORD'} =~ /^$/) {
	if (! move($tmpfile, $PKCS_IMPORT_FILE)) {
            unlink($tmpfile);
            return (0, _('Could not bring imported PKCS#12 file in place! (%s)', $!));
        }
        if (system("openssl pkcs12 -in $PKCS_IMPORT_FILE -password pass: -nodes -noout &>/dev/null") != 0) {
            unlink($PKCS_IMPORT_FILE);
            return (0, _('Invalid PKCS#12 file! Import failed!'));
        }
        return 1;
    }

    my $challenge = $par{'IMPORT_PASSWORD'};
    # decrypt
    my $cmd = "openssl pkcs12 -in $tmpfile -nodes -out ${tmpfile}.decrypted -password stdin &>/dev/null";
    $pid = open3(\*WRITE, \*READ, \*ERROR, $cmd);
    if (! $pid) {
	unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not decrypt PKCS#12 file! Import failed!'));
    }
    print WRITE $challenge;
    close READ;
    close WRITE;
    close ERROR;
    waitpid($pid, 0);
    if ($? != 0) {
	unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not decrypt PKCS#12 file! Import failed!'));
    }
    if (system("openssl pkcs12 -export -in ${tmpfile}.decrypted -out $PKCS_IMPORT_FILE -password pass: &>/dev/null") != 0) {
        unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, _('Could not store decrypted PKCS#12 file! Import failed!'));
    }
    unlink($tmpfile);
    unlink("${tmpfile}.decrypted");
    return 1;
}

sub read_file($) {
    my $f = shift;
    open (CA, $f) || return _("Could not open file '%s'.", $f);
    my $str = <CA>;
    close CA;
    return $str;
}

sub get_crldate() {
    my $output = `/usr/bin/openssl crl -in $CRL_FILE -lastupdate -noout 2>/dev/null`;
    $output =~ s/lastUpdate=//;
    $output =~ s/\s+$//;
    $output = &cleanhtml($output,"y");
    return $output;
}

sub get_crlvaliduntil() {
    my $output = `/usr/bin/openssl crl -in $CRL_FILE -nextupdate -noout 2>/dev/null`;
    $output =~ s/nextUpdate=//;
    $output =~ s/\s+$//;
    $output = &cleanhtml($output,"y");
    return $output;
}

sub display() {
    if ($config->{'AUTH_TYPE'} =~ /^$/) {
        $config->{'AUTH_TYPE'} = 'psk';
    }

    $selected{'PROTOCOL'}{uc($protocol)} = 'selected';

    my %authtype = ();
    $authtype{$config->{'AUTH_TYPE'}} = 'checked="checked"';

    my $last_crl_import = _('No import');
    if (-e $CRL_FILE) {
        $last_crl_import = get_crldate();
    }
    my $next_crl_import = _('No import');
    if (-e $CRL_FILE) {
        $next_crl_import = get_crlvaliduntil();
    }

    my $canreadpkcs = 0;

    if (open F, $PKCS_FILE) {
        $canreadpkcs = 1;
        close(F);
    }

    my $canreadcacert = 0;

    if (open F, $CACERT_FILE) {
        $canreadcacert = 1;
        close(F);
    }

    my $subject = _('No host certificate');
    my $issuer = _('No CA certificate');

    if (-e $SUBJECT_FILE) {
        $subject = read_file($SUBJECT_FILE);
    }
    if (-e $ISSUER_FILE) {
        $issuer = read_file($ISSUER_FILE);
    }

    my $displaypsk = 'display: none';
    if ($config->{'AUTH_TYPE'} eq 'psk') {
        $displaypsk = 'display: block';
    }

    my $displaycert = 'display: none';
    if ($config->{'AUTH_TYPE'} =~ /cert/) {
        $displaycert = 'display: block';
    }

    printf <<EOF
<form method='post' action='$self' enctype='multipart/form-data'>
  <input type='hidden' name='ACTION' value='save' />
  <input type='hidden' name='OPENVPN_ENABLED' value='$config->{'OPENVPN_ENABLED'}' />
  <input type='hidden' name='PURPLE_IP_BEGIN' value='$config->{'PURPLE_IP_BEGIN'}' />
  <input type='hidden' name='PURPLE_IP_END' value='$config->{'PURPLE_IP_END'}' />
EOF
;

    openbox('100%', 'left', _('Advanced settings'));
    printf <<EOF
<table columns="4" width="100%">
  <tr>
    <td width="20%">%s:</td>
    <td width="20%"><input type='text' name='PORT' value='$port' SIZE="5" MAXLENGTH="6" /></td>
    <td width="38%">%s:</td>
    <td width="22%"><input type='checkbox' name='DROP_DHCP' value='on' $checked{$block_dhcp} /></td>
  </tr>

  <tr>
    <td>%s:</td>
    <td>
      <select name="PROTOCOL">
        <option value="udp" $selected{'PROTOCOL'}{'UDP'}>UDP</option>
        <option value="tcp" $selected{'PROTOCOL'}{'TCP'}>TCP</option>
      </select>
    </td>
    <td>%s:</td>
    <td><input type='checkbox' name='CLIENT_TO_CLIENT' value='on' $checked{$client_to_client} /></td>
  </tr>


  <tr>
    <td colspan="4" valign="top">
      <div style="font-size: 9px;">%s</div>
    </td>
  </tr>

  <tr>
    <td colspan="4">&nbsp;</td>
  </tr>

  <tr>
    <td colspan="4">
      <input class='submitbutton' type='submit' name='SAVE' value='%s' />
    </td>
  </tr>

</table>

EOF
, _('Port')
, _('Block DHCP responses coming from tunnel')
, _('Protocol')
, _("Don't block traffic between clients")
, _('Note: You may allow multiple ports by port forwarding them')
, _('Save and restart')
;
    closebox();



    globaloptions();


#
# Authentication settings
#



    openbox('100%', 'left', _('Authentication settings'));
    printf <<EOF
<table columns="2" width="100%">
  <tr>
    <td colspan="2"><b>%s</b></td>
  </tr>

  <tr>
    <td colspan="2">
      <input type="radio" name="AUTH_TYPE" value="psk" $authtype{'psk'}  onchange="switchVisibility('psk', 'on'); switchVisibility('cert', 'off'); switchVisibility('psk_t', 'on'); switchVisibility('cert_t', 'off');">%s</input>
    </td>
  </tr>

  <tr>
    <td colspan="2">
      <input type="radio" name="AUTH_TYPE" value="cert" $authtype{'cert'} onchange="switchVisibility('psk', 'off'); switchVisibility('cert', 'on'); switchVisibility('psk_t', 'off'); switchVisibility('cert_t', 'on');">%s</input>
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <input type="radio" name="AUTH_TYPE" value="certpsk" $authtype{'certpsk'} onchange="switchVisibility('psk', 'off'); switchVisibility('cert', 'on'); switchVisibility('psk_t', 'off'); switchVisibility('cert_t', 'on');">%s</input>
    </td>
  </tr>
  <tr>
    <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
    <td colspan="2"><b>%s</b></td>
  </tr>
</table>
EOF
, _('Authentication type')
, _('PSK (username/password)')
, _('X.509 certificate')
, _('X.509 certificate & PSK (two factor)')

, _('Certificate management')
;

    printf <<EOF
<div id="psk" style="$displaypsk">
<table columns="2" width="100%">
EOF
;

    if ($canreadcacert) {
        printf <<EOF
  <tr>
    <td><A HREF="showca.cgi?type=pem">%s</A></td>
    <td>%s</td>
  </tr>
EOF
, _('Download CA certificate')
, _('Use this file as CA certificate for clients.')
;
    }

    if ($canreadpkcs) {
        printf <<EOF
  <tr>
    <td><A HREF='showca.cgi?type=p12'>%s</A></td>
    <td colspan="4">%s</td>
  </tr>
EOF
, _('Export CA as PKCS#12 file')
, _('Use this file for import on OpenVPN fallback servers.')
;
    }

    printf <<EOF
  <tr>
    <td colspan="2">&nbsp;</td>
  </tr>
</table>
</div>
EOF
;

    printf <<EOF
<table columns="2" width="100%">
  <tr>
    <td colspan="2">
      <div id="cert_t" style="$displaycert">%s</div>
      <div id="psk_t" style="$displaypsk">%s</div>
    </td>
  </tr>

  <tr>
    <td width="35%">%s:</td>
    <td width="65%"><input type="file" name="IMPORT_FILE"></td>
  </tr>
  <tr>
    <td>%s:</td>
    <td><input type="password" name="IMPORT_PASSWORD"></td>
  </tr>

  <tr class="odd">
    <td>%s:</td>
    <td>$subject</td>
  </tr>
  <tr class="odd">
    <td>%s:</td>
    <td>$issuer</td>
  </tr>
  <tr>
    <td colspan="2">
      <input class='submitbutton' type='submit' name='submit' value='%s' />
    </td>
  </tr>
</table>
</form>
EOF
, _('Import server certificate from external Certification Authority (CA)')
, _('Import server certificate from primary OpenVPN server or external Certification Authority (CA)')
, _('PKCS#12 file')
, _('Challenge password')
, _('Host certificate')
, _('CA certificate')
, _('Save and restart')
;


    printf <<EOF
<form method='post' action='$self' enctype='multipart/form-data'>
  <input type='hidden' name='ACTION' value='importcrl' />
<div id="cert" style="$displaycert">
<table columns="2" width="100%">
  <tr>
    <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
    <td colspan="2"><b>%s</b></td>
  </tr>
  <tr>
    <td width="35%">%s:</td>
    <td width="65%">
      <input type="file" name="IMPORT_FILE"> &nbsp; <input class='submitbutton' type='submit' name='SAVE' value='%s' />
    </td>
  </tr>
  <tr class="odd">
    <td>%s:</td>
    <td colspan="2">${last_crl_import}&nbsp;</td>
  </tr>
  <tr class="odd">
    <td>%s:</td>
    <td colspan="2">${next_crl_import}&nbsp;</td>
  </tr>
</table>
</div>
</form>
EOF
, _('Certificate revocation')
, _('Import revocation list (CRL) as PEM file')
, _('Import revocation list')
, _('Last import')
, _('Valid until')
;

    closebox();

}

sub globaloptions() {

    my %push_global_networks = ();
    $push_global_networks{$config->{'PUSH_GLOBAL_NETWORKS'}} = 'checked="checked"';
    my %push_global_dns = ();
    $push_global_dns{$config->{'PUSH_GLOBAL_DNS'}} = 'checked="checked"';
    my %push_domain = ();
    $push_domain{$config->{'PUSH_DOMAIN'}} = 'checked="checked"';

    openbox('100%', 'left', _('Global push options'));
    printf <<EOF
<table columns="2" width="100%">
  <tr>
    <td valign="top" width="30%">%s:</td>
    <td valign="top">
      <input type='checkbox' name='PUSH_GLOBAL_NETWORKS' value='on' $push_global_networks{'on'}>%s</input><br />
      <textarea cols="17" rows="2" name='GLOBAL_NETWORKS'>$globalnetworks</textarea>
    </td>
  </tr>
  <tr>
    <td valign="top">%s:</td>
    <td valign="top">
      <input type='checkbox' name='PUSH_GLOBAL_DNS' value='on' $push_global_dns{'on'}>%s</input><br />
      <textarea cols="17" rows="2" name='GLOBAL_DNS'>$globalnameserver</textarea>
    </td>
  </tr>
  <tr>
    <td valign="top">%s:</td>
    <td valign="top">
      <input type='checkbox' name='PUSH_DOMAIN' value='on' $push_domain{'on'}>%s</input><br />
      <input type="text" name='DOMAIN' value="$domain" />
    </td>
  </tr>
  <tr><td>&nbsp;</td></tr>
  <tr>
    <td colspan="5">
      <input class='submitbutton' type='submit' name='submit' value='%s' />
    </td>
  </tr>
</table>
EOF
, _('Push these networks')
, _('Enable')
, _('Push these nameservers')
, _('Enable')
, _('Push domain')
, _('Enable')
, _('Save and restart')
;
    closebox();


}


# -------------------------------------------------------------
# get settings and CGI parameters
# -------------------------------------------------------------
sub getconfig () {

    if (-e $hostconffile) {
	readhash($hostconffile, $host);
    }
    if (-e $conffile_default) {
	readhash($conffile_default, $conf);
    }
    if (-e $conffile) {
	readhash($conffile, $conf);
	$pool_begin = $conf->{PURPLE_IP_BEGIN};
	$pool_end = $conf->{PURPLE_IP_END};
    }

    my $greenaddress = '';
    if (-e $etherconf) {
	$ether = readconf($etherconf);

	my @green = split(/\./, $ether->{GREEN_ADDRESS});
	$netpart = $green[0].'.'.$green[1].'.'.$green[2];
	$greenaddress = $ether->{GREEN_ADDRESS};
    }

    $block_dhcp = $conf->{DROP_DHCP};
    $port = $conf->{OPENVPN_PORT};
    $protocol = $conf->{OPENVPN_PROTOCOL};

    $globalnetworks = $conf->{GLOBAL_NETWORKS};
    $globalnameserver = $conf->{GLOBAL_DNS};
    $domain = $conf->{DOMAIN};

    $client_to_client = $conf->{CLIENT_TO_CLIENT};

    $globalnetworks =~ s/,/\n/g;
    $globalnameserver =~ s/,/\n/g;
    if ($domain =~ /^$/) {
        $domain = $host->{'DOMAINNAME'};
    }
    if ($globalnameserver =~ /^$/) {
	$globalnameserver = $greenaddress;
    }

    if ($conf->{'OPENVPN_ENABLED'} eq 'on') {
	$enabled = 1;
    }
    $config = $conf;
}

sub sanitize($) {
    my $data = shift;
    $data =~ s/\"/\\\"/;
    return $data;
}

sub doaction() {

    if (!$action) {
	return;
    }

    if ($action eq 'save') {
	($err,$errormessage) = save();
	getconfig();
	$action = '';
	return;
    }
    if ($action eq 'importcrl') {
	($err,$errormessage) = crlimport();
	$action = '';
	return;
    }
}

getconfig();
getcgihash(\%par, {'wantfile' => 1, 'filevar' => 'IMPORT_FILE'});
$action = $par{ACTION};

# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------

$username = sanitize($par{'username'});
doaction();


# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------

showhttpheaders();
my $extraheader = '<script language="JavaScript" src="/include/switchVisibility.js"></script>';

openpage($name, 1, $extraheader);

if (-e $dirtyfile) {
    $warnmessage = _('User configuration has been changed. Since it affects other users you may need to restart OpenVPN server in order to push the changes to the other clients.'). ' '._('Clients will reconnect automatically after a timeout.');
}

if (! -e $openvpn_diffie && -e $openvpn_diffie_lock) {
    $notemessage=_('OpenVPN is generating the Diffie Hellman parameters. This will take several minutes. During this time OpenVPN can <b>not</b> be started!');
}

openbigbox($errormessage, $warnmessage, $notemessage);


display();
closebigbox();
closepage();

