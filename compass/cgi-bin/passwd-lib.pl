#!/usr/bin/perl
#
# password dialogue library
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

sub chpass($) {
    my $pass = shift;
    use IPC::Open3;
    $pid = open3(\*WRITE, \*READ, \*ERROR, '/usr/bin/sudo', '/usr/local/bin/chrootpasswd');
    print WRITE "$pass\n";
    close READ;
    close WRITE;
    close ERROR;
    waitpid($pid,0);
}

sub chsmbpass($$) {
    my $user = shift;
    my $pass = shift;
    use IPC::Open3;
    $pid = open3(\*WRITE, \*READ, \*ERROR, '/usr/bin/sudo', '/usr/bin/smbpasswd', '-s', '-a', $user);
    print WRITE "$pass\n";
    print WRITE "$pass\n";
    close READ;
    close WRITE;
    close ERROR;
    waitpid($pid,0);
}

my @passRegistry;
my %passRegistryByUser;
my %cgiparams;
$cgiparams{'ACTION_ADMIN'} = '';
$cgiparams{'ACTION_DIAL'} = '';

&getcgihash(\%cgiparams);

sub doPasswordSave($$$) {
    my $var = shift;
    my $user = shift;
    my $type = shift;

    if ($cgiparams{"ACTION_${var}"} ne 'save') {
	return;
    }
    my $password1 = $cgiparams{"${var}_PASSWORD1"};
    my $password2 = $cgiparams{"${var}_PASSWORD2"};	
    if ($password1 ne $password2) {
	$errormessage = _('Passwords do not match.');
	return;
    }
    if ($password1 =~ m/\s|\"/) {
	$errormessage = _('Password contains invalid characters.');
	return;
    }
    if (length($password1) < 6) {
	$errormessage = _('Passwords must be at least 6 characters in length');
	return;
    }

    if ($type eq 'web') {
	system('/usr/bin/sudo /usr/bin/htpasswd -m -b ' . ${swroot} . '/auth/users ' . $user . ' ' . ${password1});
    } 
    elsif ($type eq 'smb') {
        chsmbpass($user, $password1);
    }
    elsif ($type == 'system') {
	chpass($password1);
    }
    &log(_('Password of user "%s" has been changed.', $user));
}

sub displayPasswordDialogue($$$) {
    my $var = shift;
    my $title = shift;
    my $multiform = shift;

    if (! $multiform) {
	printf <<END
	<form action="$ENV{'SCRIPT_NAME'}" method="post">
END
;
    }

    printf <<END
            <div class="section first multi-column">
                <input type='hidden' name='ACTION_${var}' value='save' />
                <div class="title"><h2 class="title">$title</h2></div> 
                <div class="fields-row">
                    <span class="multi-field">
                        <label id="username_field" for="username">%s *</label>
                        <input type="password" name="${var}_PASSWORD1" SIZE="5" /></span>
                    <br class="cb" />
                </div>
                <div class="fields-row">
                    <span class="multi-field">
                        <label id="password_field" for="password">%s *</label>
                        <input type="password" name="${var}_PASSWORD2" SIZE="5" /></span>
                    <br class="cb" />
                </div>
END
, _("Password")
, _("Confirm Password")
;


    if (! $multiform) {
	printf <<END
                <div class="fields-row">
                    <span class="multi-field submit save-button">
                        <input class='submitbutton save-button' type="submit" name="submit" value="%s" /></span>
                    <br class="cb" />
                </div>
END
, _("Change Password")
;
    }

	printf <<END
            </div>
END
;

    if (! $multiform) {
	printf <<END
        </form>
END
;
    }

}

sub registerPasswordDialogues($$$$) {
    my $var = shift;
    my $user = shift;
    my $type = shift;
    my $title = shift;

    my %item = (
	'var' => $var,
	'user' => $user,
	'type' => $type,
	'title' => $title
	);
    push(@passRegistry, \%item);
    $passRegistryByUser{$user} = \%item;
}

sub callPasswordSaves() {
    foreach my $item (@passRegistry) {
	doPasswordSave($item->{'var'}, $item->{'user'}, $item->{'type'});
    }
}

sub displayUserPasswordDialogue($$) {
    my $user = shift;
    my $multiform = shift;
    my $item = $passRegistryByUser{$user};
    return if (! $item);
    displayPasswordDialogue($item->{'var'}, $item->{'title'}, $multiform);
}

sub callPasswordDisplays($) {
    my $multiform = shift;
    foreach my $item (@passRegistry) {
	displayPasswordDialogue($item->{'var'}, $item->{'title'}, $multiform);
    }
}

1;

