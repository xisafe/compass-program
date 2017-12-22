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

require 'ifacetools.pl';
require '/var/efw/header.pl';
require './endianinc.pl';
use Net::IPv4Addr qw (:all);

my $restart  = '/usr/local/bin/restartopenvpn';
my $passwd   = '/usr/bin/openvpn-sudo-user';
my $etherconf = "/var/efw/ethernet/settings";
my $openvpnconf = "/var/efw/openvpn/settings";

my $dirtyfile  = '/var/efw/openvpn/dirtyuserconfig';

my $name        = _('OpenVPN server');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked');
my $self = $ENV{SCRIPT_NAME};

my %par;
my $action = '';
my $username = '';
my $errormessage = '';
my $err = 1;
my $config = 0;
my $CACERT_FILE = '/var/efw/openvpn/cacert.pem';

sub ip2long {
    return unpack("l*", pack("l*", unpack("N*", inet_aton(shift))));
}

sub restart() {
    my $logid = "$0 [" . scalar(localtime) . "]";
    print STDERR `$restart --force`; 
    print STDERR "$logid: restarting done\n";
    $notemessage = _('OpenVPN server has been restarted!');
}

sub list_users() {

    my $canreadcacert = 0;
    if (open F, $CACERT_FILE) {
        $canreadcacert = 1;
        close(F);
    }

    openbox('100%', 'left', _('Account configuration'));
printf <<EOF
<table border="0" cellspacing="0" cellpadding="4" width="100%">
  <tr>
    <td width="20%"><b>%s</b></td>
    <td width="20%"><b>%s</b></td>
    <td width="20%"><b>%s</b></td>
    <td width="20%"><b>%s</b></td>
    <td width="20%" colspan="3"><b>%s</b></td>
  </tr>
EOF
, _('Username')
, _('Remote nets')
, _('Push nets')
, _('Static ip')
, _('Actions')
;

EOF
;

    my @users = split(/\n/, `$passwd longlist`);
    my $i = 0;
    foreach my $line (@users) {

	my @split = split(/:/, $line);
	my $user = $split[0];
	my $remotenets = $split[5];
	$remotenets =~ s/,/<BR>/;
	my $pushnets = $split[7];
	$pushnets =~ s/,/<BR>/;
	my $staticips = $split[8];
	$staticips =~ s/,/<BR>/;

	if ($split[6] eq 'on') {
	    $pushnet = _('None');
	}
	if ($staticips eq '') {
	    $staticips = _('dynamic');
	}

	my $oddeven = 'odd';
	if ($i % 2) {
	    $oddeven = 'even';
	}
	
	my $gif = 'off.png';
	my $enabled_action = 'enable';
	my $enabled_description = _('Enable account');
	if ($split[1] eq 'enabled') {
	    $gif = 'on.png';
	    $enabled_action = 'disable';
	    $enabled_description = _('Disable account');
	}

	printf <<EOF
<tr class="$oddeven">
  <td>$user</td>
  <td>$remotenets</td>
  <td>$pushnets</td>
  <td>$staticips</td>
EOF
;


        printf <<EOF
  <td>
<form method='post' action='$self'>
    <input class='imagebutton' type='image' name='$enabled_description' src='/images/$gif' alt='$enabled_description' title='$enabled_description'>
    <input type="hidden" name="ACTION" value="$enabled_action">
    <input type="hidden" name="username" value="$user">
</form>
  </td>

  <td>
<form method='post' action='$self' onSubmit="return confirm('%s')">
    <input class='imagebutton' type='image' name='%s' src='/images/delete.png' alt='%s' title='%s'>
    <input type="hidden" name="ACTION" value="delete">
    <input type="hidden" name="username" value="$user">
</form>
  </td>

  <td>
<form method='post' action='$self'>
    <input class='imagebutton' type='image' name='%s' src='/images/edit.png' alt='%s' title='%s'>
    <input type="hidden" name="ACTION" value="set">
    <input type="hidden" name="username" value="$user">
</form>
  </td>


</tr>
EOF
,
_('Really delete the VPN client %s?', $user),
_('Remove'),
_('Remove'),
_('Remove'),
_('Edit'),
_('Edit'),
_('Edit')
;
	$i++;
    }
printf <<EOF
  <tr><td>&nbsp;</td></tr>
  <tr>
    <td>
<form method='post' action='$self' style="display:inline;">
  <input type="hidden" name="ACTION" value="add">
  <input class='submitbutton' type="submit" name="submit" value="%s">
</form>
    </td>
    <td colspan="2" align="center">
<form method='post' action='$self' style="display:inline;">
  <input type="hidden" name="ACTION" value="restart">
  <input class='submitbutton' type="submit" name="submit" value="%s">
</form>
    </td>
    <td colspan="2" align="right">
EOF
,_('Add account')
,_('Restart OpenVPN server')
;

    if ($canreadcacert) {
        printf <<EOF
    <a href="showca.cgi?type=pem">%s</a>
EOF
, _('Download CA certificate')
;
    } else {
	printf <<EOF
	    &nbsp;
EOF
;
    }

printf <<END

    </td>
  </tr>
</table>
<table cellpadding="0" cellspacing="0" class="list-legend">
<tr>
        <td class='boldbase'><b>%s:</b></td>
        <td>&nbsp; <img src='/images/on.png' alt='%s' ></td>
        <td class='base'>%s</td>
        <td>&nbsp; &nbsp; <img src='/images/off.png' alt='%s' /></td>
        <td class='base'>%s</td>
        <td>&nbsp; &nbsp; <img src='/images/edit.png' alt='%s' ></td>
        <td class='base'>%s</td>
        <td>&nbsp; &nbsp; <img src='/images/delete.png' alt='%s' ></td>
        <td class='base'>%s</td>
</tr>
</table>
END
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


    closebox();

}

# -------------------------------------------------
# EDIT ACCOUNT
# -------------------------------------------------

sub show_set($$) {
    my $username = shift;
    my $action = shift;

    my @split = ();
    my $password = '';
    if ($action eq 'set') {
	openbox('100%', 'left', _('Change account') . " $username");
	@split = split(/:/, `$passwd getuser "$username"`);
	$password = '_NOTCHANGED_';
    } else {
	openbox('100%', 'left', _('Add new user'));
	$password = '';
    }

    $checked{'setred'}{$setred} = ' ';
    if ($split[1] eq 'setred') {
	$checked{'setred'}{$setred} = "checked='checked'";
    }

    $checked{'setorange'}{$setorange} = '';		
    if ($split[2] eq 'setorange') {
	$checked{'setorange'}{$setorange} = "checked='checked'";	
    }

    $checked{'setblue'}{$setblue} = '';		
    if ($split[3] eq 'setblue') {
	$checked{'setblue'}{$setblue} = "checked='checked'";	
    }

    my $remotenets = $split[4];
    $remotenets =~ s/,/\n/g;
    chomp($remotenets);

    $checked{'dontpushroutes'}{$dontpushroutes} = ' ';
    if ($split[5] eq 'on') {
	$checked{'dontpushroutes'}{$dontpushroutes} = "checked='checked'";
    }

    my $explicitroutes = $split[6];
    $explicitroutes =~ s/,/\n/g;
    chomp($explicitroutes);

    my $static_ip = $split[7];;
    $static_ip =~ s/,/\n/g;
    chomp($static_ip);

    my $custom_dns = $split[8];
    $custom_dns =~ s/,/\n/g;
    chomp($custom_dns);

    my $custom_domain = $split[9];

    if ($split[10] =~ /on/) {
	$checked{'push_custom_dns'}{$push_custom_dns} = "checked='checked'";
    }
    if ($split[11] =~ /on/) {
	$checked{'push_custom_domain'}{$push_custom_domain} = "checked='checked'";
    }

    my $usernamelabel = _('Username');
    if ($config->{'AUTH_TYPE'} eq 'cert') {
        $usernamelabel = _('Common name');
    }

    printf <<EOF
<form method='post' action='$self'>
<table border='0' cellspacing="0" cellpadding="4">
<tr valign='top'>
  <td width="40%"><b>%s</b></td>
</tr>
<tr valign='top'>
  <td>%s:</td>
EOF
, _('Account information')
, $usernamelabel
;

    if ($action eq 'add') {
	printf <<EOF
  <td><input type='text' name='username' value='$username' /></td>
EOF
;
    } else {
	printf <<EOF
  <td><input type='text' name='usernamedisabled' value='$username' disabled /></td>
  <input type='hidden' name='username' value='$username' />
EOF
;
    }


    my $defaultpw = '_NOTCHANGED_';
    if ($action eq 'add') {
	$defaultpw = '';
    }
    if ($config->{'AUTH_TYPE'} ne 'cert') {
        printf <<EOF
<tr valign='top'>
  <td class='base'>%s:</td>
  <td class='base'><input type='password' name='password' value='$defaultpw' /></td>
</tr>
<tr valign='top'>
  <td class='base'>%s:</td>
  <td class='base'><input type='password' name='password2' value='$defaultpw' /></td>
</tr>
EOF
, _('Password')
, _('Verify password')
;
    } else {
        printf <<EOF
<input type='hidden' name='password' value='_NOTCHANGED_' />
<input type='hidden' name='password2' value='_NOTCHANGED_' />
EOF
;
    }

    printf <<EOF
<tr valign='top'>
  <td><b>&nbsp;</b></td>
</tr>

<tr valign='top'>
  <td><b>%s</b></td>
</tr>

<tr valign='top'>
  <td>%s:</td>
  <td><input type="checkbox" name="setred" value="set" $checked{'setred'}{$setred}></td>
</tr>

<tr valign='top'>
  <td>%s:</td>
  <td><input type="checkbox" name="dontpushroutes" value="on" $checked{'dontpushroutes'}{$dontpushroutes}></td>
</tr>
EOF
, _('Client routing')
, _('Direct all client traffic through the VPN server')
, _("Push only global options to this client")
;

       if (blue_used()) {
           printf <<EOF
<tr valign='top'>  
   <td>%s:</td>
   <td><input type="checkbox" name="setblue" value="set" $checked{'setblue'}{$setblue}></td>
</tr>
EOF
,_('Push route to blue zone')
;
        }

       if (orange_used()) {
           printf <<EOF
<tr valign='top'>
  <td>%s:</td>
  <td><input type="checkbox" name="setorange" value="set" $checked{'setorange'}{$setorange}></td>
</tr>
EOF
,_('Push route to orange zone')
;
       }


printf <<EOF
<tr valign='top'>
  <td><a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">%s</a>:</td>
  <td>
    <textarea cols="17" rows="2" name='remotenets'>$remotenets</textarea>
  </td>
</tr>

<tr valign='top'>
  <td>
    <a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">%s</a>:
    <br /><br />
    <div style="font-size: 9px; width: 30em">%s</div>
  </td>
  <td>
    <textarea cols="17" rows="2" name='explicitroutes'>$explicitroutes</textarea>
  </td>
</tr>

<tr valign='top'>
  <td><b>&nbsp;</b></td>
</tr>

<tr valign='top'>
  <td><b>%s</b></td>
</tr>


<tr valign='top'>
  <td><a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">%s</a>:</td>
  <td>
    <textarea cols="17" rows="2" name='static_ip'>$static_ip</textarea>
  </td>
</tr>

<tr valign='top'>
  <td><a href="javascript:void(0);" onmouseover="return overlib('%s',STICKY, MOUSEOFF);" onmouseout="return nd();">%s</a>:</td>
  <td>
    <input type='checkbox' name='push_custom_dns' value='on' $checked{'push_custom_dns'}{$push_custom_dns}>%s</input><br />
    <textarea cols="17" rows="2" name='custom_dns'>$custom_dns</textarea>
  </td>
</tr>

<tr>
  <td>%s:</td>
    <td valign="top">
      <input type='checkbox' name='push_custom_domain' value='on' $checked{'push_custom_domain'}{$push_custom_domain}>%s</input><br />
      <input type="text" name='custom_domain' value="$custom_domain" />
    </td>
</tr>

<tr valign='top'>
  <td><br/></td>
  <td><br/></td>
</tr>
<tr valign='top'>
  <td colspan="2">
  <input class='submitbutton' type='submit' name='submit' value='%s' /></td>
</tr>
</table>

<input type='hidden' name='ACTION' value='$action' />

</form>
EOF

,_('Put in one network per line in net/cidr notation (for example: 10.10.10.0/24).<br><br>This is only needed for Net2Net connections in Routed Mode. Routes to these networks will be pushed to each of the other clients')
,_('Networks behind client')
,_('Put in one network per line in net/cidr format (for example: 10.10.10.0/24).<br><br>This overrides all the routing configuration and pushes only routes for these networks to the client')
,_('Push only these networks')
,_('If this box is empty routes to each of the networks of the other clients will be pushed to this client whenever it connects')

,_('Custom push configuration')

,_('Assign static IP addresses instead of dynamic assignment.<br />One ip or ip/cidr pair per line<br /><br/>Example:<br/>10.2.2.2/24<br />10.3.3.3/25')
,_('Static ip addresses')

,_('Push these nameservers, only to this user.<br>One ip per line.')
,_('Push these nameservers')
,_('Enable')

,_('Push domain')
,_('Enable')

,_('Save')
;

    closebox();

}


sub cracklib($$) {
    my $password = shift;
    my $password1 = shift;

    if ($password =~ /[\$]/) {
	return (0, _('Invalid characters in password.'));
    }
    if ($password ne $password1) {
	return (0, _('passwords are not identical'));
    }
    if (length($password) < 5) {
	return (0, _('the password must have more than 5 characters'));
    }
    return 1;

}

sub sanitize($) {
    my $data = shift;
    $data =~ s/\"/\\\"/;
    return $data;
}

sub disable_user ($) {
    my $user = shift;
    `$passwd set \"$user\" --toggle='disable' --rewrite-users`;
}

sub enable_user ($) {
    my $user = shift;
    `$passwd set \"$user\" --toggle='enable' --rewrite-users`;
}

sub checkuser() {
    if ($username =~ /^$/) {
	$errormessage = _('Username not set.');
	return 0;
    }

    if ($username !~ /^[A-Za-z0-9\.\-_@]+$/) {
	$errormessage = _('Username "%s" contains invalid characters.', $username);
	return 0;
    }

    return 1;
}

sub getStaticIPs() {
    my %hash;
    my $ret = \%hash;

    my @users = split(/\n/, `$passwd longlist`);
    foreach my $line (@users) {
	my @split = split(/:/, $line);
	my $user = $split[0];
	my $staticips = $split[8];
	foreach my $ip (split(/,/, $staticips)) {
	    $ret->{$ip} = $user;
	}
    }
    return $ret;
}

sub checkvalues() {

    my $remotenets = $par{'remotenets'};
    my $explicitroutes = $par{'explicitroutes'};
    my $custom_dns = $par{'custom_dns'};
    my $static_ip = $par{'static_ip'};
    my $custom_domain = $par{'custom_domain'};

    if ($remotenets) {
	my ($ok, $nok) = checkIPs($remotenets, 32);
	if ($nok ne '') {
	    $errormessage = _('Networks behind client "%s" are invalid', $nok);
	    return 0;
	}
    }
    if ($explicitroutes) {
	my ($ok, $nok) = checkIPs($explicitroutes, 32);
	if ($nok ne '') {
	    $errormessage = _('Networks to be pushed "%s" are invalid', $nok);
	    return 0;
	}
    }
    if ($custom_dns) {
	my ($ok, $nok) = checkIPs($custom_dns, 33);
	if ($nok ne '') {
	    $errormessage = _('Custom nameserver addresses "%s" are invalid', $nok);
	    return 0;
	}
    }
    if ($custom_domain) {
	if (! validdomainname($custom_domain)) {
	    $errormessage = _('Domain name to be pushed "%s" is invalid', $custom_domain);
	    return 0;
	}
    }

    my $remoteips = getStaticIPs();
    if ($static_ip) {
	my ($ok, $nok) = checkIPs($static_ip, 33);
	if ($nok ne '') {
	    $errormessage = _('Static ip addresses "%s" are invalid', $nok);
	    return 0;
	}

	my $ether;
	if (-e $etherconf) {
	    $ether = readconf($etherconf);
	}

	my $openvpn;
	if (-e $openvpnconf) {
	    $openvpn = readconf($openvpnconf);
	    
	}
	my $purple_begin_long = ip2long($openvpn->{PURPLE_IP_BEGIN});
	my $purple_end_long = ip2long($openvpn->{PURPLE_IP_END});


	foreach my $ipcidr (split(/[\r\n,]/, $static_ip)) {
	    my ($ip, $cidr) = split(/\//, $ipcidr);
	    if ($ip eq $ether->{GREEN_BROADCAST}) {
		$errormessage = _('Static ip address "%s" can\'t be same as broadcast ip of VPN segment "%s".', $ip, $b);
		return 0;
	    }
	    if ($ip eq $ether->{GREEN_NETADDRESS}) {
		$errormessage = _('Static ip address "%s" can\'t be same as network ip of VPN segment "%s".', $ip, $a);
		return 0;
	    }
	    if ($ip eq $ether->{GREEN_ADDRESS}) {
		$errormessage = _('Static ip address "%s" can\'t be same as GREEN ip address', $ip);
		return 0;
	    }
	    if ($remoteips->{$ip} && ($remoteips->{$ip} ne $username)) {
		$errormessage = _('Static ip address "%s" is already assigned to user "%s"!', $ip, $remoteips->{$ip});
		return 0;
	    }
	    my $longip = ip2long($ip);
	    if (($longip >= $purple_begin_long) && ($longip <= $purple_end_long)) {
		$errormessage = _('Static ip address "%s" can\'t be part of dynamic ip pool %s - %s!', 
				  $ip, $openvpn->{PURPLE_IP_BEGIN}, $openvpn->{PURPLE_IP_END});
		return 0;
	    }
	}
    }

    return 1;
}

sub nl2coma($) {
    my $string = shift;
    my $ret = '';
    foreach my $item (split(/[\n\r]/, $string)) {
	next if ($item =~ /^$/);
	$ret .= ','.$item;
    }
    $ret =~ s/^,//;
    return $ret;
}

sub setdirty($$) {
    my $username = shift;
    my $remotenets = shift;
    my @split = split(/:/, `$passwd getuser "$username"`);
    my $oldremotenets = $split[4];

    return if ($remotenets eq $oldremotenets);
    makedirty();
}

sub makedirty() {
    `touch $dirtyfile`;
}

sub doaction() {

    if (!$action) {
	return;
    }

    if ($action eq 'restart') {
	restart();
	$action = '';
	return;
    }

    if ($action eq 'delete') {
	if (!checkuser()) {
            return;
	}

	system("$passwd del \"$username\"");
	$notemessage = _('User \'%s\' successfully deleted', $username);
	$action = '';
	return;
    }

    if ((($action eq 'add') ||
	 ($action eq 'set')) && ($par{'password'} ne '')) {

	if (!checkuser()) {
	    return;
	}
	
	if (!checkvalues()) {
	    return;
	}

	my $pass1 = $par{'password'};
	my $pass2 = $par{'password2'};

	my $remotenets = nl2coma($par{'remotenets'});
	my $explicitroutes = nl2coma($par{'explicitroutes'});
	my $custom_dns = nl2coma($par{'custom_dns'});
	my $static_ip = nl2coma($par{'static_ip'});
	my $custom_domain = $par{'custom_domain'};

	$remotenets = 'None' if ($remotenets eq '');
	$explicitroutes = 'None' if ($explicitroutes eq '');
	$custom_dns = 'None' if ($custom_dns eq '');
	$custom_domain = 'None' if ($custom_domain eq '');
	$static_ip = 'None' if ($static_ip eq '');

	$setred = 'on';
	$setblue = 'on';
	$setorange = 'on';
	$setred = 'off' if ($par{'setred'} ne 'set');
	$setblue = 'off' if ($par{'setblue'} ne 'set');
	$setorange = 'off' if ($par{'setorange'} ne 'set');
	$par{'dontpushroutes'} = 'off' if ($par{'dontpushroutes'} ne 'on');

	my $push_custom_domain = 'on';
	my $push_custom_dns = 'on';
	$push_custom_domain = 'off' if ($par{'push_custom_domain'} ne 'on');
	$push_custom_dns = 'off' if ($par{'push_custom_dns'} ne 'on');


	($err, $errormessage) = cracklib($pass1, $pass2);
	if ($err) {
	    setdirty($username, $remotenets);

	    $cmd = "$passwd set \"$username\" --password \"$pass1\"";
	    $cmd .= " --dns=$custom_dns";
	    $cmd .= " --domain=$custom_domain";
	    $cmd .= " --static-ips=$static_ip";
	    $cmd .= " --dont-push-routes $par{'dontpushroutes'}";
	    $cmd .= " --explicit-routes $explicitroutes";
	    $cmd .= " --networks $remotenets";
	    $cmd .= " --route-blue $setblue";
	    $cmd .= " --route-orange $setorange";
	    $cmd .= " --route-red $setred";
	    $cmd .= " --push-domain=$push_custom_domain";
	    $cmd .= " --push-dns=$push_custom_dns";

            system("$cmd --rewrite-users");

	    # kill the user in order to enforce the configuration change.
            system("$passwd kill \"$username\"");

	    $notemessage = _('Account \'%s\' successfully changed', $username);
	    $action = '';

	}
	return;
    }
    
    if ($action eq 'enable') {
	if (!checkuser()) {
	    return;
	}

	enable_user($username);
	return;
    }
    
    if ($action eq 'disable') {
	if (!checkuser()) {
	    return;
	}

	disable_user($username);
	return;
    }
}

getcgihash(\%par);
$action = $par{ACTION};

# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------

$username = sanitize($par{'username'});
doaction();

if (-e $dirtyfile) {
    $warnmessage = _('User configuration has been changed. Since it affects other users you may need to restart OpenVPN server in order to push the changes to the other clients.'). ' '._('Clients will reconnect automatically after a timeout.');
}



# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------

showhttpheaders();

openpage($name, 1);
openbigbox($errormessage, $warnmessage, $notemessage);

if ($action eq 'set') {
    show_set($username, $action);
} elsif ($action eq 'add') {
    show_set($username, $action);
} else {
    list_users();
}

closebigbox();
closepage();

