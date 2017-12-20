#!/usr/bin/perl

require '/var/efw/header.pl';
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;
my $system_title;
# &validateUser();
sub read_config(){
	if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
	$system_title = $system_settings{'SYSTEM_TITLE'};
}

#陆芦驴貌录脺路脰html脨麓脠毛
sub frame_html()
{
&read_config();
printf <<EOF
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>$system_title</title>
<link rel="shortcut icon" href="/images/shortcut.ico" />
<link rel="stylesheet" type="text/css" href="/include/main.css" />
</head>
EOF
;
check_cookie_user();
printf <<EOF
<frameset rows="60,*,25" cols="*" framespacing="0" frameborder="no" border="0">
  <frame src="top.cgi" name="topFrame" scrolling="No" noresize="noresize" id="topFrame" />
  <frame src="center.cgi" name="mainFrame" scrolling="No" id="mainFrame"  />
  <frame src="footer.cgi" name="bottomFrame" scrolling="No" noresize="noresize" id="bottomFrame" />
  <div id="pop-div"></div>
</frameset>
<noframes><body>
</body>
</noframes>
</html>
EOF
,_("ChinArk Network Unified Threat Management System")
;
}

sub showhttpheaders_top
{
    calcURI();
    genFlavourMenus();
    checkForHASlave();
	print "Pragma: no-cache\n";
	print "Cache-control: no-cache\n";
	print "Connection: close\n";
	print "Content-type: text/html\n\n";
}
showhttpheaders_top();
frame_html();
