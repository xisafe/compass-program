#!/usr/bin/perl

#
# $Id: chpasswd.cgi,v 1.0 2005/01/25 00:00:00 marco Exp $
#
require '/var/efw/header.pl';
use CGI qw(param);
use encoding 'utf8';
use endian_locale;


$swroot = "/var/efw";

my %cgiparams;
my %mainsettings;
my %proxysettings;
&validateUser();
$proxysettings{'NCSA_MIN_PASS_LEN'} = 6;

### Initialize environment
&readhash("${swroot}/main/settings", \%mainsettings);
&readhash("${swroot}/proxy/settings", \%proxysettings);
$language = $mainsettings{'LANGUAGE'};

### Initialize language
if ($language =~ /^(\w+)$/) {$language = $1;}
gettext_init($language, "efw");

my $userdb = "$swroot/proxy/ncsausers";

&readhash("$swroot/ethernet/settings", \%netsettings);

my $success = 0;

&getcgihash(\%cgiparams);

if ($cgiparams{'ACTION'} eq 'change')
{
	if ($cgiparams{'USERNAME'} eq '')
	{
		$errormessage = _('Username cannot be empty');
		goto ERROR;
	}
	if (($cgiparams{'OLD_PASSWORD'} eq '') || ($cgiparams{'NEW_PASSWORD_1'} eq '') || ($cgiparams{'NEW_PASSWORD_2'} eq ''))
	{
		$errormessage = _('Password cannot be empty');
		goto ERROR;
	}
	if (!($cgiparams{'NEW_PASSWORD_1'} eq $cgiparams{'NEW_PASSWORD_2'}))
	{
		$errormessage = _('Passwords don\'t match');
		goto ERROR;
	}
	if (length($cgiparams{'NEW_PASSWORD_1'}) < $proxysettings{'NCSA_MIN_PASS_LEN'})
	{
		$errormessage = _('Password must have at least %s characters', $proxysettings{'NCSA_MIN_PASS_LEN'});
		goto ERROR;
	}
	if (! -z $userdb)
	{
		open FILE, $userdb;
		@users = <FILE>;
		close FILE;

		$username = '';
		$cryptpwd = '';

		foreach (@users)
		{
 			chomp;
			@temp = split(/:/,$_);
			if ($temp[0] =~ /^$cgiparams{'USERNAME'}$/i)
			{
				$username = $temp[0];
				$cryptpwd = $temp[1];
			}
		}
	}
	if ($username eq '')
	{
		$errormessage = _('Username does not exist');
		goto ERROR;
	}
	if (!(crypt($cgiparams{'OLD_PASSWORD'}, $cryptpwd) eq $cryptpwd))
	{
		$errormessage = _('Password incorrect');
		goto ERROR;
	}
	$returncode = system("/usr/bin/htpasswd -b $userdb $username $cgiparams{'NEW_PASSWORD_1'}");
	if ($returncode == 0)
	{
		$success = 1;
		undef %cgiparams;
	} else {
		$errormessage = _('Password could not be changed');
		goto ERROR;
	}
}

ERROR:

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

printf <<END
<html>
  <head>
    <title>Change Proxy Password</title>
    <meta http-equiv="Cache-control" content="no-cache" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="shortcut icon" href="/favicon.ico" />
    <style type="text/css">\@import url(/include/style.css);</style>
    <style type="text/css">\@import url(/include/menu.css);</style>
    <style type="text/css">\@import url(/include/content.css);</style>
    <style type="text/css">\@import url(/include/hotspot.css);</style>
    <style type="text/css">\@import url(/include/hotspot.css);</style>
  </head>

  <body>

<div id="main">

<div id="header">
  <img id="logo-product" src="/images/logo_efw.png">
  <img id="logo-endian" src="/images/logo_endian.png">
  <div id="header-icons">
    <img src="/images/help.png">
  </div>
</div>

<br /><br /><br />
<br /><br /><br />
<center>
  <h1>%s</h1>
</center>

<center>

<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type="hidden" name="ACTION" value="change"/>
<table border="0" width="100%" cellspacing="0" cellpadding="10">
  <tr>
    <td class="menu" width="100%"></td>

<!-- Slimmer inner table -->
<tr  bgcolor="#eeeeee">
  <td align="center">
    <table border="0" width="300">
END
,
_('C h a n g e &nbsp; w e b &nbsp; a c c e s s &nbsp; p a s s w o r d')
;

if ($errormessage || $success) {
    my $message="$errormessage";
    my $class="error-fancy";
    my $image="/images/bubble_red_sign.png";
    
    if ($success) {
        $message=_('Password for web access successfully changed');
        $class="notification-fancy";
        $image="/images/bubble_yellow_sign.png";
    }
    
    printf <<EOF
    <tr>
    <td colspan="2">
    <div class="$class" style="width: 504px;">
        <div class="content">
            <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td class="sign" valign="middle"><img src="$image" alt="" border="0" /></td>
                    <td class="text" valign="middle">$message</td>
                </tr>
            </table>
        </div>
        <div class="bottom"><img src="/images/clear.gif" width="1" height="1" alt="" border="0" /></div>
    </div>
    </td>
    </tr>
EOF
}

printf <<END
      <tr><td colspan="2"></td></tr>
      <tr>
        <td align="right" class="light"><b>%s:</b></td>
        <td align="left" class="light" nowrap="nowrap">
          <input type="text" tabindex="1" name="USERNAME" value="$cgiparams{'USERNAME'}" size="15">
        </td>
      </tr>
      <tr>
        <td align="right" class="light"><b>%s:</b></td>
        <td align="left" class="light" nowrap="nowrap">
          <input type="password" tabindex="2" name="OLD_PASSWORD" value="$cgiparams{'OLD_PASSWORD'}" size="15">
        </td>
      </tr>
      <tr>
        <td align="right" class="light"><b>%s:</b></td>
        <td align="left" class="light" nowrap="nowrap">
          <input type="password" tabindex="3" name="NEW_PASSWORD_1" value="$cgiparams{'NEW_PASSWORD_1'}" size="15">
        </td>
      </tr>
      <tr>
        <td align="right" class="light"><b>%s:</b></td>
        <td align="left" class="light" nowrap="nowrap">
          <input type="password" tabindex="4" name="NEW_PASSWORD_2" value="$cgiparams{'NEW_PASSWORD_2'}" size="15">
        </td>
      </tr>
       <tr>
        <td></td>
        <td align="left" class="light">
          <input class='submitbutton' type="submit" name="SUBMIT" tabindex="5" value="  %s  "/>
        </td>
      </tr>
    </table>
  </td>
</tr>
</table>
</form>
<br /><br /><br />

</body>
</html>
END
,
_('Username'),
_('Current password'),
_('New password'),
_('New password (confirm)'),
_('Change password')
;

# -------------------------------------------------------------------

sub readhash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	if (-e $filename)
	{
		open(FILE, $filename) or die "Unable to read file $filename";
		while (<FILE>)
		{
			chomp;
			($var, $val) = split /=/, $_, 2;
			if ($var)
			{
				$val =~ s/^\'//g;
				$val =~ s/\'$//g;
	
				# Untaint variables read from hash
				$var =~ /([A-Za-z0-9_-]*)/;        $var = $1;
				$val =~ /([\w\W]*)/; $val = $1;
				$hash->{$var} = $val;
			}
		}
		close FILE;
	}
}

# -------------------------------------------------------------------

sub getcgihash
{
	my ($hash, $params) = @_;
	my $cgi = CGI->new ();
	return if ($ENV{'REQUEST_METHOD'} ne 'POST');
	if (!$params->{'wantfile'}) {
		$CGI::DISABLE_UPLOADS = 1;
		$CGI::POST_MAX        = 512 * 1024;
	} else {
		$CGI::POST_MAX = 10 * 1024 * 1024;
	}

	$cgi->referer() =~ m/^https?\:\/\/([^\/]+)/;
	my $referer = $1;
	$cgi->url() =~ m/^https?\:\/\/([^\/]+)/;
	my $servername = $1;
	return if ($referer ne $servername);

	### Modified for getting multi-vars, split by |
	%temp = $cgi->Vars();
	foreach my $key (keys %temp) {
		$hash->{$key} = $temp{$key};
		$hash->{$key} =~ s/\0/|/g;
		$hash->{$key} =~ s/^\s*(.*?)\s*$/$1/;
	}

	if (($params->{'wantfile'})&&($params->{'filevar'})) {
		$hash->{$params->{'filevar'}} = $cgi->upload
					($params->{'filevar'});
	}
	return;
}

# -------------------------------------------------------------------
