#!/usr/bin/perl
#
# openvpn client CGI for Endian Firewall
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
use File::Copy;
use File::Temp qw/ tempdir tempfile/;

require '/var/efw/header.pl';
my $conffile  = "${swroot}/openvpn/settings";
my $etherfile = "${swroot}/ethernet/settings";
my $openvpn_dir = "${swroot}/openvpnclients/";
my $lockfile_dir = "/var/openvpn/";
my $configfile  = "${swroot}/openvpnclients/";
my $restart   = '/usr/local/bin/restartopenvpnclients';
my $ca_suffix = '.pem';
my $ca_prefix = 'ca_';
my $reload_prefix = 'reload_';
my $tapticket = "sudo /usr/bin/ticket --file /var/lib/ticketregistry/tap --realm openvpnclients";
my $tunticket = "sudo /usr/bin/ticket --file /var/lib/ticketregistry/tun --realm openvpnclients --startid 10";

my $invalid_ca_prefix = 'invalidca_';
my $authfailed_prefix = 'authfailed_';
my $notresolved_prefix = 'notresolved_';
my $connecting_prefix = 'connecting_';
my $refused_prefix = 'refused_';
my $badproxy_prefix = 'badproxy_';


my $name      = _('OpenVPN Net2Net client');
my %dhcpchecked = ('on' => 'checked');
my %natchecked = ('on' => 'checked');
my %compchecked = ('on' => 'checked');
my %selected = ();

my %checked   = ( 0 => '', 1 => 'checked', 'on' => 'checked' );
my $self      = $ENV{SCRIPT_NAME};

my %par;
my $openvpnconf = undef;
my %etherhash;
my $ether = \%etherhash;
my $errormessage = '';
my $err = 1;

my $defaultprotocol = 'udp';
my $defaultport = 'default';

my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $EDIT_PNG = '/images/edit.png';
my $DELETE_PNG = '/images/delete.png';
my $OPTIONAL_PNG = '/images/blob.png';
my @nets;

sub have_net($) {
    my $net = shift;

    # AAAAAAARGH! dumb fools
    my %net_config = (
        'GREEN' => [1,1,1,1,1,1,1,1,1,1],
        'ORANGE' => [0,1,0,3,0,5,0,7,0,0],
        'BLUE' => [0,0,0,0,4,5,6,7,0,0]
    );

    if ($net_config{$net}[$ether->{'CONFIG_TYPE'}] > 0) {
        return 1;
    }
    return 0;
}

sub configure_nets() {
    my @totest = ('GREEN', 'BLUE', 'ORANGE');

    foreach (@totest) {
        my $thisnet = $_;
        if (! have_net($thisnet)) {
            next;
        }
        if ($ether->{$thisnet.'_DEV'}) {
            push (@nets, $thisnet);
        }
    }
}

sub check_errors($) {

    my $name = shift;

    if ($name =~ /^$/) {
	return '';
    }

    if (-e "$lockfile_dir/$badproxy_prefix$name") {
	return _('bad HTTP proxy');
    }
    if (-e "$lockfile_dir/$refused_prefix$name") {
	return _('connection refused');
    }
    if (-e "$lockfile_dir/$notresolved_prefix$name") {
	return _('resolve error');
    }
    if (-e "$lockfile_dir/$invalid_ca_prefix$name") {
	return _('invalid CA certificate');
    }
    if (-e "$lockfile_dir/$authfailed_prefix$name") {
	return _('authentication failed');
    }
    if (-e "$lockfile_dir/$connecting_prefix$name") {
	return _('connecting...');
    }
    return '';
}

sub flag_reload($) {
    my $name = shift;

    $reload = 1;
    if ($name !~ /^$/) {
	system("touch $lockfile_dir/$reload_prefix$name");
	`sudo fmodify "$lockfile_dir/$reload_prefix$name"`;
    }
}

sub display_conns() {

#openbox('100%', 'left', _('OpenVPN tunnel to'));
printf <<EOF
<div style="margin:10px;">
<form method='post' action='$self' style="float:left;margin-right:5px;">
                <input type="hidden" name="ACTION" value="add">
                <input class='submitbutton net_button' type="submit" name="submit" value="%s">
            </form>

<form method='post' action='$self' style="float:left;margin-right:5px;">
                <input type="hidden" name="ACTION" value="import">
                <input class='submitbutton net_button' type="submit" name="submit" value="%s">
            </form>
</div>
<br />
<br />
EOF
,
_('Add tunnel configuration'),
_('Import profile from OpenVPN Access Server'),
;

printf <<EOF
<table border="0" cellspacing="0" cellpadding="0" class="ruleslist" cols="6" width="100%">
  <tr>
    <td width="15%" class="boldbase"><b>%s</b></td>
    <td width="25%" class="boldbase"><b>%s</b></td>
    <td width="20%" class="boldbase"><b>%s</b></td>
    <td width="25%" class="boldbase"><b>%s</b></td>
    <td width="15%" align="center" class="boldbase"><b>%s</b></td>
  </tr>

EOF
,
_('Status'),
_('Connection name'),
_('Options'),
_('Remark'),
_('Actions')
;
	my $length=0;
	foreach my $name (`ls -1 $openvpn_dir 2>/dev/null`) {
	chomp($name);
    my $file = $openvpn_dir.$name.'/settings';
	next if (! -f $file);
	next if ($name eq 'default');
	$length++;
	}
    my $line = 0;
	if($length>0)
	{
    foreach my $name (`ls -1 $openvpn_dir 2>/dev/null`) {
	chomp($name);
        my $file = $openvpn_dir.$name.'/settings';
	next if (! -f $file);
	next if ($name eq 'default');

	my %confighash = ();
	my $conf = \%confighash;
	readhash($file, $conf);

	my $description = $conf->{'REMARK'};
	my $route_type = $conf->{'ROUTETYPE'};
	my $drop_dhcp = $conf->{'BLOCKDHCP'};
	my $bridge = $conf->{'BRIDGE'};
	if (! $bridge) {
	    $bridge = 'GREEN';
	}
	my $nat = $conf->{'NAT_OUT'};
	my $bgcolor = setbgcolor(($par{'action'} eq 'edit'), $line, $line);
	my $enabled_action = 'enable';
	my $enabled_description = _('enable connection');
	my $enabled_png = $DISABLED_PNG;
	if ($conf->{'ENABLED'} eq 'on') {
	    $enabled_action = 'disable';
	    $enabled_png = $ENABLED_PNG;
	    $enabled_description = _('disable connection');
	}

	my $status = _('closed');

	my $error = check_errors($name);
	if ($error ne '') {
	    $status = $error;
	} else {
	    if (system('/sbin/ifconfig '.$conf->{'DEVICE'}.' >/dev/null 2>&1') == 0) {
		$status = _('established');
	    }
	}
	$options = '&nbsp;';
	if ($route_type eq 'bridged') {
	    $options .= '<font color="'.$zonecolors{$bridge}.'">'._('bridged to %s', $strings_zone{$bridge}).'</font>&nbsp;';
	    if ($drop_dhcp eq 'on') {
		$options .= _('drop DHCP').'&nbsp;';
	    }
	}
        if ($nat eq 'on') {
            $options .= _('NAT').'&nbsp;';
        }

        printf <<EOF
<tr class="$bgcolor">
  <td>$status</td>
  <td>$name</td>
  <td>$options</td>
  <td>$description</td>
	
  <td>
<form method='post' action='$self' style="float">
    <input type="hidden" name="ACTION" value="$enabled_action">
    <input type="hidden" name="NAME" value="$name">
    <input class='imagebutton' type='image' name="submit" src="$enabled_png" alt="$enabled_description" />
</form>

<form method='post' action='$self'>
    <input class='imagebutton' type='image' name="submit" src="$EDIT_PNG" alt="%s" />
    <input type="hidden" name="ACTION" value="edit">
    <input type="hidden" name="NAME" value="$name">
</form>

<form method='post' action='$self' onSubmit="return confirm('%s')">
    <input class='imagebutton' type='image' name="submit" src="$DELETE_PNG" alt="%s" />
    <input type="hidden" name="ACTION" value="delete">
    <input type="hidden" name="NAME" value="$name">
</form>
  </td>
</tr>
EOF
,
_('Edit'),
_('Really delete the VPN tunnel %s?', $name),
_('delete')
;
	$line++;
    }
}else{
	no_tr(7,_('Current no content'));
}


    printf <<EOF
</table>
EOF
;

if($length >0)
{
printf <<EOF
<table cellpadding="0" cellspacing="0" class="list-legend">
  <tr>
    <td class="boldbase">
      <b>%s</b>
    <img src="$ENABLED_PNG" alt="%s" />
    %s
    <img src='$DISABLED_PNG' alt="%s" />
    %s
    <img src="$EDIT_PNG" alt="%s" />
    %s
    <img src="$DELETE_PNG" alt="%s" />
    %s</td>
  </tr>
</table>
<br />
EOF
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')
;
}
    #closebox();
}

sub display() {
    my $action = $par{'ACTION'};
    my $name = $par{'NAME'};

    if (($action eq 'edit') or ($action eq 'add')) {
		show_add($name, $action);
		return;
    }
    if ($action eq 'import') {
        if ($par{'NAME'} eq "") {
            $par{'SSL'} = "true";
        }
        show_import($name, $action);
        return;
    }
    display_conns();
}

sub read_credentials($$) {
    my $name = shift;
    my $type = shift;
    my @data = ();
    if ($type eq 'proxy') {
        $type = "${type}_";
    }
    my $file = $openvpn_dir.$name."/${type}credentials";
    return ('','') if (! -e $file);

    open(FILE, $file) or return ('', '');
    @data = <FILE>;
    close(FILE);
    chomp($data[0]);
    chomp($data[1]);

    return ($data[0], $data[1]);
}

sub save_credentials($$$$) {
    my $name = shift;
    my $newusername = shift;
    my $newpassword = shift;
    my $type = shift;

    my $username = '';
    my $password = '';
    
    if ($type eq 'proxy') {
        $type = "${type}_";
    }
    my $filename = $openvpn_dir.$name."/${type}credentials";
    ($username, $password) = read_credentials($name, $type);
    
    if ($newpassword eq '') {
        $newpassword = $password;
    }
    
    my $error = check_credentials($newusername, $newpassword);
    if ($error) {
        return $error;
    }
    
    if (($newusername eq $username) && ($newpassword eq $password)) {
        return '';
    }
    
    umask(0077);
    open(FILE, ">$filename") or return _('Could not save credentials file');
    print FILE $newusername."\n";
    print FILE $newpassword."\n";
    close(FILE);	
	`sudo fmodify $filename`;    
    flag_reload($name);
    return '';
}

sub call($) {
    my $cmd = shift;
    use IPC::Open3;

    $pid = open3(\*WRITE, \*READ, \*ERROR, $cmd);
    if (! $pid) {
        return (0, _('Could  not call "%s"', $cmd));
    }
    close WRITE;
    my @out = <READ>;
    my @err = <ERROR>;
    close READ;
    close ERROR;

    my $reterr = join(" ", @err);
    my $retout = join(" ", @out);

    my $ret = 0;
    waitpid($pid, 0);
    if ($? == 0) {
        $ret = 1;
    }
    return ($ret, $reterr, $retout);
}


sub getCertType($) {
    my $filename = shift;
    my ($ret, $reterr, $retout);

    ($ret, $reterr, $retout) = call("openssl x509 -in $filename");
    return 'x509' if ($ret);

    ($ret, $reterr, $retout) = call("openssl pkcs12 -password pass: -nodes -in $filename");
    return 'pkcs12' if ($ret);
    return 'pkcs12' if ($reterr !~ /:error:/);

    return 'error';
}


sub import_pem($) {
    my $name = shift;
    if (ref ($par{'IMPORT_FILE'}) ne 'Fh') {
        return 1;
    }
    
    my ($fh, $tmpfile) = tempfile("import.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.pem');
    if (!copy ($par{'IMPORT_FILE'}, $fh)) {
        close($fh);
        unlink($tmpfile);
        return (0, 'error', _('Unable to store certificate file \'%s\'', $par{'IMPORT_FILE'}, $!));
    }
    close($fh);
    
    # check for certificate type in order to set AUTH_CERT
    my $cafile = $openvpn_dir.$name.'/ca.pem';
    my $p12file = $openvpn_dir.$name.'/certs.p12';
    my $storefile = '';
    my $certtype = getCertType($tmpfile);

    if ($certtype eq 'error') {
        unlink($tmpfile);
        return (0, 'error', _('No certificate file! Import failed!'));
    }

    if ($certtype eq 'x509') {
	$storefile = $cafile;
	if (! move($tmpfile, $storefile)) {
            unlink($tmpfile);
            return (0, 'x509', _('Could not bring uploaded CA certificate in place! (%s)', $!));
        }
        unlink($p12file);
        return (1, 'x509', '');
    }

    # it's a p12 file
    $storefile = $p12file;
    if ($par{'IMPORT_PASSWORD'} =~ /^$/) {
	if (! move($tmpfile, $storefile)) {
            unlink($tmpfile);
            return (0, 'pkcs12', _('Could not bring uploaded PKCS#12 file in place! (%s)', $!));
        }
        if (system("openssl pkcs12 -in $storefile -password pass: -nodes -noout &>/dev/null") != 0) {
            unlink($storefile);
            return (0, 'pkcs12', _('PKCS#12 file is encrypted! Challenge password is required! Import failed!'));
        }
        unlink($cafile);
        return (1, 'pkcs12', '');
    }

    my $challenge = $par{'IMPORT_PASSWORD'};
	`sudo fmodify $cafile`;
    # decrypt
    if (system("openssl pkcs12 -in $tmpfile -nodes -out ${tmpfile}.decrypted -password pass:$challenge &>/dev/null") != 0) {
	unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, 'pkcs12', _('Could not decrypt PKCS#12 file! Import failed!'));
    }
    if (system("openssl pkcs12 -export -in ${tmpfile}.decrypted -out $storefile -password pass: &>/dev/null") != 0) {
        unlink($tmpfile);
        unlink("${tmpfile}.decrypted");
        return (0, 'pkcs12', _('Could not store decrypted PKCS#12 file! Import failed!'));
    }
    unlink($tmpfile);
    unlink($cafile);
	`sudo fdelete $cafile`;
    unlink("${tmpfile}.decrypted");
    return (1, 'pkcs12', '');
}

sub getP12Infos($) {
    my $filename = shift;
    my $issuer = '';
    my $subject = '';
    return if (! -e $filename);

    my ($ret, $err, $out) = call("openssl pkcs12 -info -nodes -nokeys -clcerts -info -password pass: -in $filename");
    return if (! $ret);

    foreach my $line (split(/\n/, $out)) {
	if ($line =~ /issuer=/) {
	    $issuer = $line;
	    $issuer =~ s/^.*issuer=\///;
	    chomp($issuer);
	}
	if ($line =~ /subject=/) {
	    $subject = $line;
	    $subject =~ s/^.*subject=\///;
	    chomp($subject);
	}
	if ($line =~ /localKeyID:/) {
	    $fingerprint = $line;
	    $fingerprint =~ s/^.*localKeyID: //;
	    chomp($fingerprint);
	    $fingerprint =~ s/ *$//;
	    $fingerprint =~ tr/ /:/;
	}
    }
    return ($issuer, $subject, $fingerprint);
}

sub getCAFingerprint($) {
    my $filename = shift;
    my $fingerprint = '';
    return if (! -e $filename);

    my ($ret, $err, $out) = call("openssl x509 -in $filename -fingerprint -noout");
    return if (! $ret);
    $fingerprint = $out;
    chomp($fingerprint);
    $fingerprint =~ s/^[^=]*=//;
    return ($fingerprint);
}

sub getTLSmd5($) {
    my $filename = shift;
    my $md5 = '';
    return if (! -e $filename);

    my ($ret, $err, $out) = call("md5sum $filename");
    return if (! $ret);
    @md5array = split(/ /, $out);
    $md5 = $md5array[0];
    chomp($md5);
    return ($md5);
}


sub show_add($$) { 
    my $name = shift;
    my $action = shift;
    my %config = ();
    my $enabled = 'on';
    my $leaveblank = '';
    my $authentication_type = _('Not yet configured');

    my $remotes_fallback = '';
    my $remotes = '';
    my $proxy_username = '';
    my $proxy_password = '';
    my $issuer = '';
    my $subject = '';
    my $fingerprint = '';
    
    print "<form method='post' action='$self' enctype='multipart/form-data'>";
    if ($action eq 'edit') {
        if ($par{'sure'} ne 'y') {
            my $file = $openvpn_dir.$name.'/settings';
            if ( -f $file) {
                readhash($file, \%config);
            }
	    	($config{'username'}, $config{'password'}) = 
	        read_credentials($name, '');
            if ($config{'PROXY_CREDENTIALS'} eq 'on') {
  	        ($proxy_username, $proxy_password) = 
	            read_credentials($name, 'proxy');
            }
        } else {
	    	%config = %par;
        }
        openbox('100%', 'left', _('Edit VPN tunnel settings'));
		$enabled = $config{'ENABLED'};
		$leaveblank = _('(Leave blank to keep the old value)');

        if ($config{'AUTH_CERT'} eq 'on') {
            $authentication_type = _('X.509 or two Factor');
	    	($issuer, $subject, $fingerprint) = getP12Infos($openvpn_dir.$name.'/certs.p12');
		    if (! -e $openvpn_dir.$name.'/certs.p12') {
				$authentication_type = _('No certificate');
				$issuer = _('No certificate');
				$subject = _('No certificate');
				$fingerprint = _('No certificate');
		    }
        } else {
            $authentication_type = _('PSK');
		    $fingerprint = getCAFingerprint($openvpn_dir.$name.'/ca.pem');
		    if (! -e $openvpn_dir.$name.'/ca.pem') {
				$authentication_type = _('No certificate');
				$fingerprint = _('No certificate');
		    }
        }
		my @remotes_arr = split(/,/, $config{'REMOTES'});
        $remotes = $remotes_arr[0];
        delete($remotes_arr[0]);
        $remotes_fallback = join("\r\n", @remotes_arr);

    } else {
	
        openbox('100%', 'left', _('Add VPN tunnel'));
	 	$enabled = 'on';
		$config{'ROUTETYPE'} = 'routed';
		$config{'BRIDGE'} = 'GREEN';
		$config{'PROTOCOL'} = 'udp';
    }

    my $http_proxy = '';
    if ($config{'PROXY'} eq 'on') {
        $http_proxy = $config{'PROXY_SERVER'};
        if ($config{'PROXY_PORT'} ne '') {
            $http_proxy .= ':'.$config{'PROXY_PORT'};
        }
    }
    if ($config{'BRIDGE'} =~ /^$/) {
		$config{'BRIDGE'} = 'GREEN';
    }
	if (!$config{'DEV_TYPE'} || $config{'DEV_TYPE'} =~ /^$/) {
		$config{'DEV_TYPE'} = 'tap';
	}
	if (!$config{'COMP_LZO'} || $config{'COMP_LZO'} eq '') {
		$config{'COMP_LZO'} = 'on';
	}

    $selected{'PROTOCOL'}{uc($config{'PROTOCOL'})} = 'selected="selected"';
    $selected{'ROUTETYPE'}{lc($config{'ROUTETYPE'})} = 'selected="selected"';
    $selected{'DEV_TYPE'}{lc($config{'DEV_TYPE'})} = 'selected="selected"';
    $selected{'BRIDGE'}{uc($config{'BRIDGE'})} = 'selected="selected"';
    my $direction = "omit";
    if ($config{'TLS_DIRECTION'} ne "") {
        $direction = $config{'TLS_DIRECTION'};
    }
    $selected{'TLS_DIRECTION'}{$direction} = 'selected="selected"';
    ####help_msg
	my $help_hash1 = read_json("/home/httpd/help/openvpn_client_help.json","openvpnclient.cgi","连接到","-10","30","down");
	my $help_hash2 = read_json("/home/httpd/help/openvpn_client_help.json","openvpnclient.cgi","上传证书","-10","30","down");
	my $help_hash3 = read_json("/home/httpd/help/openvpn_client_help.json","openvpnclient.cgi","pkcs12查询密码","-10","30","down");
	my $help_hash4 = read_json("/home/httpd/help/openvpn_client_help.json","openvpnclient.cgi","备用vpn服务器","-10","30","down");
	my $help_hash5 = read_json("/home/httpd/help/openvpn_client_help.json","openvpnclient.cgi","设备类型","-10","30","down");
	my $help_hash6 = read_json("/home/httpd/help/openvpn_client_help.json","openvpnclient.cgi","网络地址转换","-10","30","down");
    printf <<EOF
<table border="0" cellspacing="0" cellpadding="0" width="100%">
  <tr class="env">
    <td  class="add-div-type">%s *</td>
EOF
, _('Connection name')
;

    if ($action eq 'edit') {
        printf <<EOF
    <td>$name</td>
    <input type='hidden' name='NAME' value='$name'>
EOF
;
    } else {
        printf <<EOF
    <td><input type='text' name='NAME' size="40" value='$config{'NAME'}'/></td>
EOF
;
    }

    printf <<EOF
  </tr>

  <tr  class="odd">
    <td class="add-div-type need_help">%s *$help_hash1</td>
    <td><input type='text' name='REMOTES' value='$remotes' size="40" /></td>
  </tr>

  <tr class="env">
    <td class="add-div-type  need_help">%s *$help_hash2</td>
    <td>
      <input type="file" name="IMPORT_FILE" size='40'/>
    </td>
  </tr>

  <tr class="odd">
    <td class="add-div-type  need_help">%s $help_hash3</td>
    <td><input type='password' name='IMPORT_PASSWORD' size="40"/></td>
  </tr>

EOF
, _('连接地址')
, _('Upload certificate')
, _('PKCS#12 challenge password')
;


    if ($action eq 'edit') {
	printf <<EOF
  <tr  class="env">
    <td class="add-div-type">%s *</td>
    <td>$authentication_type</td>
  </tr>
EOF
, _('Authentication type')
;

	printf <<EOF
  <tr  class="odd">
    <td class="add-div-type">%s *</td>
    <td>$fingerprint</td>
  </tr>
EOF
, _('Fingerprint')
;

        if ($config{'AUTH_CERT'} eq 'on') {
	    printf <<EOF
  <tr  class="env">
    <td class="add-div-type">%s</td>
    <td>$subject</td>
  </tr>
  <tr  class="odd">
    <td class="add-div-type">%s</td>
    <td>$issuer</td>
  </tr>
EOF
, _('Host certificate')
, _('CA certificate')
;
	}
    }

    printf <<EOF
 
  <tr class="env">
    <td class="add-div-type">%s&nbsp;*</td>
    <td><input type='text' name='username' value='$config{'username'}' size="40"/></td>
  </tr>

  <tr class="odd">
    <td class="add-div-type">%s&nbsp;*<br /><div style="font-size: 9px; width: 20em;">%s</div></td>
    <td><input type='password' name='password' size="40"/></td>
  </tr>

  <tr class="env">
    <td class="add-div-type">%s&nbsp;</td>
    <td><input type='text' name='REMARK'  value='$config{'REMARK'}' size="40" /></td>
  </tr>



  <tr class="odd">
    <td>
      <b>%s <input type="button" onclick="swapVisibility('advanced'); swapVisibility('tls');" value=" >> "/></b>
    </td>
	<td>
      
    </td>
  </tr>


  <tr  class="table-footer">
    <td colspan="2">
      <input class='submitbutton net_button' type='submit' name='submit' value='%s' />
    </td>

  </tr>

</table>
EOF
, _('Username')
, _('Password')
, $leaveblank
, _('Remark')
, _('Advanced tunnel configuration')
, _('Save')
;

	closebox();

	printf <<EOF
<div id="advanced" style="display: none">
EOF
;
        openbox('100%', 'left', _('Advanced tunnel configuration'));

	printf <<EOF
  <table border="0" cellspacing="0" cellpadding="0" width="100%">

    <tr class="odd">
      <td class="add-div-type" rowspan="7"><b>%s</b></td>
      <td class="need_help" valign="top">%s $help_hash4</td>
      <td>
        <textarea cols="40" name='REMOTES_FALLBACK'>$remotes_fallback</textarea>
      </td>
    </tr>

    <tr class="env">
      <td class="need_help">%s $help_hash5</td>
      <td>
        <script type="text/javascript">
	        function showHideRouteType() {
	        	var value = document.getElementById('advancedDeviceType').value;
	        	if (value == 'tun') {
					\$('#routeTableRow').css({'display':'none'});        		
	        	} else {
	        		\$('#routeTableRow').css({'display':'table-row'});
	        	}
	        }
	        \$(document).ready(function () {showHideRouteType();});
        </script>
        <select name="DEV_TYPE" id="advancedDeviceType" onclick="showHideRouteType();">
          <option value="tap" $selected{'DEV_TYPE'}{'tap'}>%s</option>
          <option value="tun" $selected{'DEV_TYPE'}{'tun'}>%s</option>
        </select>
      </td>
    </tr>

    <tr id="routeTableRow" class="odd">
      <td>%s</td>
      <td>
        <script type="text/javascript">
	        function showHideBridge() {
	        	var value = document.getElementById('advancedRouteType').value;
	        	if (value == 'routed') {
					\$('#advancedBridgedTo').css({'display':'none'});        		
	        	} else {
	        		\$('#advancedBridgedTo').css({'display':'table-row'});
	        	}
	        }
	        \$(document).ready(function () {showHideBridge();});
        </script>
        <select name="ROUTETYPE" id="advancedRouteType" onclick="showHideBridge();">
          <option value="routed" $selected{'ROUTETYPE'}{'routed'}>%s</option>
          <option value="bridged" $selected{'ROUTETYPE'}{'bridged'}>%s</option>
        </select>
      </td>
    </tr>

    <tr id="advancedBridgedTo" class="odd">
      <td>%s</td>
      <td>
        <select name="BRIDGE">
EOF
, _('Connection configuration')
, _('Fallback VPN servers')
, _('Device type')
, _('TAP')
, _('TUN')
, _('Connection type')
, _('Routed')
, _('Bridged')
, _('Bridge to')
;


    foreach my $item (@nets) {
	printf <<EOF
	    <option value="$item" $selected{'BRIDGE'}{$item}>%s</option>
EOF
,$strings_zone{$item}
;
    }

    printf <<EOF
        </select>
      </td>
    </tr>

    <tr  class="env">
      <td width="250px">%s</td>
      <td><input type='checkbox' name='BLOCKDHCP'  value='on' $dhcpchecked{$config{'BLOCKDHCP'}}/></td>
    </tr>

    <tr  class="odd">
      <td class="need_help">%s $help_hash6</td>
      <td><input type='checkbox' name='NAT_OUT' value='on' $natchecked{$config{'NAT_OUT'}}/></td>
    </tr>

    <tr  class="env">
      <td>%s&nbsp;</td>
      <td><input type='checkbox' name='COMP_LZO' value='on' $compchecked{$config{'COMP_LZO'}}/></td>
    </tr>

    <tr  class="odd">
      <td>%s&nbsp;</td>
      <td>
        <script type="text/javascript">
	        function showHideProxy() {
	        	var value = document.getElementById('advancedProtocolSelection').value;
	        	if (value == 'udp') {
					\$('.advancedConfigurationProxy').css({'display':'none'});        		
	        	} else {
	        		\$('.advancedConfigurationProxy').css({'display':'table-row'});
	        	}
	        }
	        \$(document).ready(function () {showHideProxy();});
        </script>
        <select id="advancedProtocolSelection" name="PROTOCOL" onclick="showHideProxy();">
          <option value="udp" $selected{'PROTOCOL'}{'UDP'}>UDP</option>
          <option value="tcp" $selected{'PROTOCOL'}{'TCP'}>TCP</option>
        </select>
      </td>
    </tr>



	<tr id="advancedConfigurationProxy" class="advancedConfigurationProxy env">
		<td rowspan="4" class="add-div-type">%s</td>
		<td>%s</td>
		<td><input type='text' name='HTTP_PROXY' value='$http_proxy' size="40"/></td>
	</tr>
	<tr id="advancedConfigurationProxy" class="advancedConfigurationProxy odd" >
		<td>%s</td>
		<td><input type='text' name='proxy_username' value='$proxy_username' size="40"/></td>
	</tr>
	<tr id="advancedConfigurationProxy" class="advancedConfigurationProxy env">
		<td>%s</td>
		<td><input type='password' name='proxy_password' size="40"/></td>
	</tr>
	<tr id="advancedConfigurationProxy" class="advancedConfigurationProxy odd">
		<td>%s</td>
		<td><input type='text' name='PROXY_USERAGENT' value='$config{'PROXY_USERAGENT'}' size="40"/></td>
	</tr>
    <tr  class="table-footer">
      <td colspan="3">
        <input class='submitbutton net_button' type='submit' name='submit' value='%s' />
      </td>
    </tr>

  </table>

EOF
, _('Block DHCP responses coming from tunnel')
, _('NAT')
, _('Use LZO compression')
, _('Protocol')
, _('HTTP proxy configuration')
, _('HTTP proxy')
, _('Proxy username')
, _('Proxy password')
, _('Forge proxy user-agent')
, _('Save')
;
	closebox();

	printf <<EOF
<input type='hidden' name='AUTH_TLS' value="$config{'AUTH_TLS'}"/>
<input type='hidden' name='TLS_DIRECTION' value="$config{'TLS_DIRECTION'}"/>
<input type="hidden" name="ENABLED" value="$enabled"/>

<input type='hidden' name='ACTION' value='$action'/>
<input type='hidden' name='sure' value='y'/>
</div>
</form>
EOF
;

    if ($name ne '') {
        printf <<EOF
<div id="tls" style="display: none">
    <form method='post' action='$self' enctype='multipart/form-data'>
EOF
        ;
        $md5 = getTLSmd5($openvpn_dir.$name.'/tls.key');
        openbox('100%', 'left', _('TLS 身份'));
        printf <<EOF
  <table  width="100%">

    <tr class="odd">
      <td colspan="2" clsss="add-div-type"><b>%s</b>&nbsp;</td>
    </tr>

    <tr class="env">
	  <td clsss="add-div-type">%s&nbsp;</td>
	  <td>
	    <input type="file" name="IMPORT_FILE" size='40'/>
	  </td>
	</tr>
	<tr class="odd">
        <td clsss="add-div-type">%s</td>
        <td>$md5</td>
    </tr>
    <tr class="env">
        <td clsss="add-div-type">%s</td>
        <td>
            <select name="TLS_DIRECTION">
              <option value="" $selected{'TLS_DIRECTION'}{'omit'}>%s</option>
              <option value="0" $selected{'TLS_DIRECTION'}{'0'}>0</option>
              <option value="1" $selected{'TLS_DIRECTION'}{'1'}>1</option>
            </select>
        </td>
    </tr>
    <tr class="table-footer">
      <td colspan="2">
        <input class="submitbutton net_button" type='submit' name='submit' value='%s' />
      </td>
    </tr>

  </table>
  <input type='hidden' name='MD5' value='$md5'/>
  <input type='hidden' name='NAME' value='$name'/>
  <input type='hidden' name='ACTION' value='tls-auth'/>
  <input type='hidden' name='sure' value='y'/>
EOF
, _('TLS Authentication')
, _('TLS key file')
, _('MD5')
, _('Direction')
, _('omit')
, _('Save')
;
        closebox();
        printf <<EOF
  </form>
</div>
EOF
        ;
    }
}

sub show_import() {
    print "<form method='post' action='$self' enctype='multipart/form-data'>";
    openbox('100%', 'left', _('Import VPN tunnel from OpenVPN Access Server'));
    my $checked = "";
    if ($par{'SSL'} ne "") {
        $checked = "checked";
    }
    printf <<EOF
    <table border="0" cellspacing="0" cellpadding="0"  width="100%">
        <tr  class="env">
            <td class="add-div-type">%s&nbsp;*</td>
            <td><input type='text' name='NAME' value='$par{'NAME'}' size="40" /></td>
        </tr>
        <tr  class="odd">
            <td class="add-div-type">%s&nbsp;*</td>
            <td><input type='text' name='HOST' value='$par{'HOST'}' size="40" /></td>
        </tr>
        <tr  class="env">
            <td class="add-div-type">%s&nbsp;*</td>
            <td><input type='text' name='USERNAME' value='$par{'USERNAME'}' size="40" /></td>
        </tr>
        <tr  class="odd">
            <td class="add-div-type">%s&nbsp;*</td>
            <td><input type='password' name='PASSWORD' value='$par{'PASSWORD'}' size="40" /></td>
        </tr>
        <tr  class="env">
            <td class="add-div-type">%s&nbsp;*</td>
            <td ><input type='checkbox' name='SSL' $checked/></td>
        </tr>
        <tr  class="odd">
            <td class="add-div-type">%s</td>
            <td><input type='text' name='REMARK' value='$par{'REMARK'}' size="40" /></td>
        </tr>
        <tr  class="table-footer">
            <td colspan="2">
                <input class='submitbutton net_button' type='submit' name='submit' value='%s' />
            </td>
        </tr>
    </table>
    <input type='hidden' name='ACTION' value='doimport' />
EOF
    ,
    _("Connection name"),
    _("Access Server URL"),
    _("Username"),
    _("Password"),
    _("Verify SSL certificate"),
    _("Remark"),
    _("Import profile")
    ;
    closebox();
    print "</form>";
}

# -------------------------------------------------------------
# get settings and CGI parameters
# -------------------------------------------------------------
sub getconfig () {
    if (-e $conffile) {
	readhash($conffile, \%openvpnconf);
    }
    if (-e $etherfile) {
	readhash($etherfile, $ether);
    }
}

sub sanitize($) {
    my $data = shift;
    $data =~ s/\"/\\\"/;
    return $data;
}

sub checkremote($) {
    local $remote = shift;

    if ($remote =~ /^$/) {
		return _('Remote address is empty');
    }

    if (($remote =~ /^localhost/) || 
		($remote =~ /^127.0.0/) ||
		($remote =~ /^$ether->{'GREEN_ADDRESS'}(:[0-9]+)?$/) ||
		($remote =~ /^$ether->{'BLUE_ADDRESS'}(:[0-9]+)?$/) ||
		($remote =~ /^$ether->{'ORANGE_ADDRESS'}(:[0-9]+)?$/)) {
		return _('Cannot create an openvpn connection to myself!');
    }

    if ($remote !~ /^[A-Za-z0-9\.\-_:]*$/) {
		return _('Invalid remote address "%s"', $remote);
    }

    return '';
}

sub reset_values() {
    %par = {};
    $par{'ACTION'} = '';
}

sub toggle_enable($$) {
    my $name = shift;
    my $switch = shift;

    my $file = $openvpn_dir.$name.'/settings';
    return if (! -f $file);
    my %confhash = ();
    readhash($file, \%confhash);
    my %values = (0 => 'off', 1 => 'on');

    if ($confhash{'ENABLED'} eq $values{$switch}) {
	return;
    }
    $confhash{'ENABLED'} = $values{$switch};
    writehash($file, \%confhash);	
	`sudo fmodify $file`;
    flag_reload('');
    return 1;
}

sub delete_connection($) {
    my $name = shift;

    return if (! -d $openvpn_dir.$name);
    system("sudo /etc/init.d/openvpnclient stop $name &>/dev/null");
	`sudo fcmd "/etc/init.d/openvpnclient stop $name &>/dev/null"`;
    system("rm -Rf $openvpn_dir$name");
	`sudo fdelete $openvpn_dir$name`;
    system("$tapticket --unregister openvpnclients/$name/settings");
	`sudo fcmd $tapticket --unregister openvpnclients/$name/settings`;
    unlink("$lockfile_dir/*_$name");
    $reload = 1;
}

sub check_credentials($$) {
    my $username = shift;
    my $password = shift;

    if ($username eq '') {
		return _('Username not set.');
    }
    if ($password eq '') {
		return _('Password not set.');
    }
    return '';
}


sub updatehash($$) {
    my $hash = shift;
    my $addhash = shift;

    foreach my $key (keys %$addhash) {
        delete($hash->{$key});
        $hash->{$key} = $addhash->{$key};
    }
}

sub store_config($$$) {
    my $name = shift;
    my $importtype = shift;
    my $conf = shift;
    my $username = $conf->{'username'};
    my $password = $conf->{'password'};
    my $proxy_username = $conf->{'proxy_username'};
    my $proxy_password = $conf->{'proxy_password'};
    my $remotes = $conf->{'REMOTES'};
    my $remotes_fallback = $conf->{'REMOTES_FALLBACK'};
    
    $name = lc $name;
    
    delete($conf->{'REMOTES'});
    delete($conf->{'REMOTES_FALLBACK'});
    delete($conf->{'username'});
    delete($conf->{'password'});
    delete($conf->{'proxy_username'});
    delete($conf->{'proxy_password'});
    delete($conf->{'sure'});
    delete($conf->{'CA_FILE'});
    delete($conf->{'submit'});
    delete($conf->{'__CGI__'});

    my $file = $openvpn_dir.$name.'/settings';
    my %fileconf = ();
    if (-e $openvpn_dir.'/default/settings') {
        readhash($openvpn_dir.'/default/settings', \%fileconf);
    }
    if (-e $file) {
        readhash($file, \%fileconf);
    }

    updatehash(\%fileconf, $conf);
    
    # checkboxes need special handling, since empty means not defined!
    if (! $conf->{'NAT_OUT'}) {
		$fileconf{'NAT_OUT'} = '';
    }

	if (! $conf->{'COMP_LZO'}) {
		$fileconf{'COMP_LZO'} = 'off';	
	}
	
    if (! $conf->{'BLOCKDHCP'}) {
		$fileconf{'BLOCKDHCP'} = '';
    }

    if (! $conf->{'DEV_TYPE'}) {
		$fileconf{'DEV_TYPE'} = 'tap';
    }

	if ($fileconf{'DEV_TYPE'} eq 'tun') {
		$fileconf{'ROUTETYPE'} = 'routed';
	}
    
    if ($importtype eq 'pkcs12') {
		$fileconf{'AUTH_CERT'} = 'on';
    } elsif ($importtype eq 'x509') {
		$fileconf{'AUTH_CERT'} = 'off';
    } else {
	#dont change
	;
    }

    if ($fileconf{'AUTH_CERT'} eq 'on') {
		if (! -e $openvpn_dir.$name.'/certs.p12') {
		    $errormessage = _('No certificate imported!');
		    return 0;
		}
		if ($username =~ /^$/) {
            $fileconf{'AUTH_USERPASS'} = 'off';
        } else {
            $fileconf{'AUTH_USERPASS'} = 'on';
            $error = save_credentials($name, $username, $password, '');
            if ($error) {
                $errormessage = $error;
                return 0;
            }
        }
    } else {
		if (! -e $openvpn_dir.$name.'/ca.pem') {
		    $errormessage = _('No certificate imported!');
		    return 0;
		}
        $error = save_credentials($name, $username, $password, '');
        if ($error) {
            $errormessage = $error;
            return 0;
        }
    }
    
    $fileconf{'REMOTES'} = '';
    my %remoteshash = ();
    foreach my $remote (split(/[,\r\n]/, $remotes.','.$remotes_fallback)) {
        next if ($remote =~ /^$/);
        next if ($remotehash{$remote});
		$errormessage = checkremote($remote);
		if ($errormessage ne '') {
		    return 0;
		}
        $fileconf{'REMOTES'} .= ','.$remote;
        $remoteshash{$remote} = 1;
    }
    $fileconf{'REMOTES'} =~ s/^,//;

    ($fileconf{'PROXY_SERVER'}, $fileconf{'PROXY_PORT'}) = split(/:/, $fileconf{'HTTP_PROXY'});
    if ($fileconf{'PROXY_PORT'} =~ /^$/) {
		$fileconf{'PROXY_PORT'} = '8080'
    }
    if ($fileconf{'PROXY_SERVER'} ne '') {
        $fileconf{'PROXY'} = 'on';
        $fileconf{'PROTOCOL'} = 'tcp';

        $fileconf{'PROXY_CREDENTIALS'} = 'off';
        if ($proxy_username ne '') {
            $fileconf{'PROXY_CREDENTIALS'} = 'on';
            $error = save_credentials($name, $proxy_username, $proxy_password, 'proxy');
            if ($error) {
                $errormessage = $error;
                return 0;
            }
        }
    } else {
        $fileconf{'PROXY'} = 'off';
    }
    
    $fileconf{'AUTH_TLS'} = $conf->{'AUTH_TLS'};
    $fileconf{'TLS_DIRECTION'} = $conf->{'TLS_DIRECTION'};
    
    writehash($file, \%fileconf);	
	`sudo fmodify $file`;
    $notemessage = _('OpenVPN connection "%s" saved', $name);
    if (($importtype eq 'x509') || ($importtype eq 'pkcs12')) {
		if ($importtype eq 'x509') {
		    $importtype = 'CA';
		}
		$notemessage .= '&nbsp;-&nbsp;' . _('%s certificate has been imported successfully', uc($importtype));
    }
    return 1;
}

sub add_tlsauth() {
    $errormessage = "";
    if ($par{'NAME'} =~ /^$/) {
        $errormessage = _('Please save the settings before uploading a TLS authentication key!');
        return 0; 
    }
    if (ref ($par{'IMPORT_FILE'}) ne 'Fh' and $par{'MD5'} eq "") {
        $errormessage = _('Could not handle file!');
        return 0;
    }
    if (ref ($par{'IMPORT_FILE'}) eq 'Fh') {
        my ($fh, $tmpfile) = tempfile("import.XXXXXX", DIR=>'/tmp/', SUFFIX=>'.key');
        if (!copy ($par{'IMPORT_FILE'}, $fh)) {
            $errormessage = _('Unable to store TLS authentication key!');
            return 0;
        }
        close($fh);
        
        # check for certificate type in order to set AUTH_CERT
        my $storefile = $openvpn_dir.$par{'NAME'}.'/tls.key';
        
        if (! move($tmpfile, $storefile)) {
            unlink($tmpfile);
            $errormessage = _('Could not place uploaded TLS authentication key!');
            return 0;
        }
    }
    
    my %fileconf = ();
    my $file = $openvpn_dir.$par{'NAME'}.'/settings';
    if (-e $openvpn_dir.'/default/settings') {
        readhash($openvpn_dir.'/default/settings', \%fileconf);
    }
    if (-e $file) {
        readhash($file, \%fileconf);
    }
    $fileconf{'AUTH_TLS'} = 'on';
    $fileconf{'TLS_DIRECTION'} = $par{'TLS_DIRECTION'};
    writehash($file, \%fileconf);	
	`sudo fmodify $file`;
    unlink($tmpfile);
	`sudo fmodify $storefile`;
    return 1;
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    $par{'NAME'} = lc $par{'NAME'};
    my $remotes =  $par{'REMOTES'};
    my $name = $par{'NAME'};
    if ($action eq 'delete') {
		delete_connection($name);
		reset_values();
		return;
    }

    if ($action eq 'enable') {
		if (toggle_enable($name, 1)) {
		    reset_values();
		    return;
		}
    }
    if ($action eq 'disable') {
		if (toggle_enable($name, 0)) {
		    reset_values();
		    return;
		}
    }
    if ($action eq 'tls-auth') {
		if (add_tlsauth()) {
            my $file = $openvpn_dir.$name.'/settings';
            my %fileconf = ();
            if (-e $openvpn_dir.'/default/settings') {
                readhash($openvpn_dir.'/default/settings', \%fileconf);
            }
            if (-e $file) {
                readhash($file, \%fileconf);
            }
            
            updatehash(\%fileconf, \%par);
            %par = %fileconf;
            $par{'ACTION'} = 'edit';
            return;
		}
    }
    # ELSE
    if (($action eq 'add') || ($action eq 'edit')) {
        if ($sure ne 'y') {
            return;
        }
        
        if ($name eq "") {
            $errormessage = _('Name must not be empty');
            return;
        }
		if ($name !~ /^[A-Za-z0-9_]*$/) {
            $errormessage = _('Name must not include illegal characters');
            return;
        }
		if (!$remotes) {
			$errormessage = _('连接地址不能为空.');
            return;
		}
		elsif($remotes !~/\:/){
			if (!validip($remotes) && !validdomainname($remotes)) {
				$errormessage = _('连接地址输入有误.');
				return;
			}
		}
		else{
			if ($remotes =~/(.*):(.*):(.*)/) {
				my $ip_part = $1;
				my $port_part = $2;
				my $proto_part = $3;
				if (!validip($ip_part) && !validdomainname($ip_part)) {
					$errormessage = _('连接地址输入有误.');
					return;
				}
				if (($port_part>65535 || $port_part < 0)  && $port_part) {
					$errormessage = _('连接地址输入有误.');
					return;
				}
				if (($proto_part !~/^tcp|udp|icmp|gre|esp$/) && $proto_part) {
					$errormessage = '连接地址输入有误.';
					return;
				}
			}
			else{
				$errormessage = _('连接地址输入有误.');
				return;
			}
		}
        if (! -d $openvpn_dir.$name) {
            mkdir($openvpn_dir.$name);
        }
        ($error, $importtype, $errormessage) = import_pem($name);
        return 0 if (! $error); 
        if (store_config($name, $importtype, \%par)) {
            reset_values();
            $reload = 1;
        }
    }
    if ($action eq 'doimport') {
        use IPC::Open3;
        if  (!$par{'SSL'}) {
            $pid = open3(\*WRITE, \*READ, \*ERROR, "/usr/local/bin/openvpn-access-import.py", "-n", $par{'NAME'}, "-o", $par{'HOST'}, "-u", $par{'USERNAME'}, "-s", "-r", $par{'REMARK'},);
        }
        else {
            $pid = open3(\*WRITE, \*READ, \*ERROR, "/usr/local/bin/openvpn-access-import.py", "-n", $par{'NAME'}, "-o", $par{'HOST'}, "-u", $par{'USERNAME'}, "-r", $par{'REMARK'});
        }
        print WRITE "$par{'PASSWORD'}\n";
        close READ;
        close WRITE;
        close ERROR;
        waitpid($pid, 0);
        $ret = $? >> 8;
        if ($ret == 0) {
            $par{'ACTION'} = 'edit';
            return;
        }
        elsif ($ret == 1) {
            $errormessage = _("服务器URL输入不正确.");
        }
        elsif ($ret == 2) {
            $errormessage = _("Unable to verify the SSL certificate. You can try again with the \"Verify SSL certificate\" option unchecked.");
        }
        elsif ($ret == 3) {
            $errormessage = _("Unable to connect to the OpenVPN Access Server.");
        }
        elsif ($ret == 4) {
            $errormessage = _("Can not import OpenVPN profile because it is not generic.");
        }
        elsif ($ret == 5) {
            $errormessage = _("Unable to import OpenVPN profile.");
        }
        elsif ($ret == 6) {
            $errormessage = _("用户名或者密码不正确.");
        }
        $par{'ACTION'} = 'import';
        return;
    }
}

getcgihash(\%par, {'wantfile' => 1, 'filevar' => 'IMPORT_FILE'});
# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------

showhttpheaders();
		#print $name;
getconfig();
configure_nets();

my $refresh = '';
if (($par{'ACTION'} =~ /^$/) || 
    ($par{'ACTION'} =~ /^enable$/) || 
    ($par{'ACTION'} =~ /^disable$/) || 
    ($par{'ACTION'} =~ /^delete$/)) {
    $refresh = '<META HTTP-EQUIV="Refresh" CONTENT="5">';
}

openpage($name, 1, $refresh);
save();
openbigbox($errormessage, $warnmessage, $notemessage);
if ($reload) {
    `$restart`;
    sleep(1);
}
display();

closebigbox();
closepage();

