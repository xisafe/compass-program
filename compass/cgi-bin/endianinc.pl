#!/usr/bin/perl
#
# shared code for Endian's CGIs for Endian Firewall
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


return 1;

require '/var/efw/header.pl';

my $register_status_hash;

# -----------------------------------------------------------
# $hashref = readconf("fname"):
#    returns a hashref with the key/val pairs defined
#    in the properties-style configuration file "fname"
# -----------------------------------------------------------
sub readconf
{
  my $fname = shift;
  my $line;
  my %conf;
  open(IN, $fname) or die();
  while ($line = <IN>) {
    next if ($line =~ /^\s*$/ or $line =~ /^\s*#/);
    if ($line =~ /^\s*(.+)\s*=\s*(.+)/) {
      $conf{$1} = $2;
    }
  }
  close(IN);
  return \%conf;
}


# -----------------------------------------------------------
# $out = filter($in)
# -----------------------------------------------------------
sub filter
{
  my $in = shift;
  $in =~ s/=/-/g;  # used in conf files
  $in =~ s/"/''/g;  # used in HTML fields
  return $in;
}

# -----------------------------------------------------------
# return 1 if $value = on or 1
# -----------------------------------------------------------
sub is_on($) {
        my $value = shift;
        if ( ( $value == 1 ) || ( $value eq 'on' ) ) {
                return 1;
        }
        else {
                return 0;
        }
}

# ----------------------------------------------------------
# return checked='checked' if $value is on (for checkboxes)
# ----------------------------------------------------------
sub check($) {
        my $value = shift;
        if ( is_on($value) ) {
                return "checked='checked'";
        }
        else {
                return "";
        }
}

# ----------------------------------------------------------
# check if $value is a hostname
# ----------------------------------------------------------
sub is_hostname($) {
        my $hostname = shift;
        if ( $hostname =~ m/^[a-zA-Z._0-9\-]*$/ ) {
                return 1;
        }
        $errormessage = _('Invalid hostname.');
        return 0;
}


# ----------------------------------------------------------
# check if $value is a ipaddress (not ip/net)
# ----------------------------------------------------------
sub is_ipaddress($) {
        my $addr = shift;
        if ( $addr !~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/ ) {
                return 0;
        }

        my @parts = { $1, $2, $3, $4 };
        foreach my $number (@parts) {
                $number = s/\D//;
                if ( ( $number < 0 ) || ( $number > 255 ) ) {
                        return 0;
                }
        }
        return 1;
}


# ----------------------------------------------------------
# check if $value is a port
# ----------------------------------------------------------
sub is_port($) {
        my $port = shift;
        if ( ( $port < 0 ) || ( $port > 65535 ) || ( $port !~ /^[0-9]*$/ ) ) {
                $errormessage = _('invalid destination port');
                return 0;
        }
        return 1;
}



# ----------------------------------------------------------
#  translate from german "Umlaute"
# ----------------------------------------------------------
sub translate_from_umlaute($)
{
    my $ret = "";
    foreach my $word (split /\b/, $_[0]) {
        $word =~ s/ä/ae/g;
        $word =~ s/ö/oe/g;
        $word =~ s/ü/ue/g;
        if ( $word =~ /[a-z]/ ) {
            $word =~ s/Ä/Ae/g;
            $word =~ s/Ö/Oe/g;
            $word =~ s/Ü/Ue/g;
            $word =~ s/ß/ss/g;
        } else {
            $word =~ s/Ä/AE/g;
            $word =~ s/Ö/OE/g;
            $word =~ s/Ü/UE/g;
            $word =~ s/ß/SS/g;
        }
        $ret = $ret . $word;
    }
 return $ret;

}

# ----------------------------------------------------------
#  translate to german "Umlaute"
#  ----------------------------------------------------------
sub translate_to_umlaute($)
{
    my $ret = "";
    foreach my $word (split /\b/, $_[0]) {
        $word =~ s/ae/ä/g;
        $word =~ s/oe/ö/g;
        $word =~ s/ue/ü/g;
        if ( $word =~ /[a-z]/ ) {
            $word =~ s/Ae/Ä/g;
            $word =~ s/Oe/Ö/g;
            $word =~ s/Ue/Ü/g;
        } else {
            $word =~ s/AE/Ä/g;
            $word =~ s/OE/Ö/g;
            $word =~ s/UE/Ü/g;
        }
        $ret = $ret . $word;
    }
 return $ret;

}

sub getpid($) {
    my $pidfile = shift;

    if (! open(FILE, "${pidfile}")) {
        return 0;
    }
    my $pid = <FILE>;
    $pid =~ s/^ +//;  # 周计, 2015-05-19, 去除前面的空格
    chomp $pid;
    close FILE;
    return $pid;
}

sub getprocname($) {
    my $pid = shift;
    if ($pid == 0) {
        return '';
    }
    if (! open(FILE, "/proc/${pid}/status")) {
        return '';
    }

    my $cmd = '';
    while (<FILE>) {
        if (/^Name:\W+(.*)/) {
            $cmd = $1;
            last;
        }
    }
    close FILE;
    return $cmd;
}


sub getcmdline($) {
    my $pid = shift;
    if ($pid == 0) {
        return '';
    }
    if (! open(FILE, "/proc/${pid}/cmdline")) {
        return '';
    }
    my $cmdline = <FILE>;
    close FILE;

    return $cmdline;
}

sub isrunning() {
    my $process = shift;
    my $exename = $process->[0];
    my $pidfile = $process->[1];
    my $args = $process->[2];

    if ($pidfile eq '') {
        $pidfile = '/var/run/'.$exename.'.pid';
    }
    my $pid = getpid($pidfile);
    if ($pid == 0) {
        # 作者：周计
        # 日期：2015-05-19
        # 作用：针对某些在运行但不会/var/run/下面建立pid文件的程序，使用ps命令查看是否运行
        # HACK_START{
        if (($exename eq 'aaaDaemon.py') || ($exename eq 'loadbalanced.py')) {
            my $return_str = "";
            if (! $args eq '') {
                $return_str = `ps aux | grep -w "$exename" | grep -w "$args" | grep -v grep`;
            } else {
                $return_str = `ps aux | grep -w "$exename" | grep -v grep`;
            }

            if ( ! $return_str eq '' ) {
                return 1;
            }
        }
        # }HACK_END

        return 0;
    }
    my $cmd = getprocname($pid);
    if ($cmd eq '') {
        return 0;
    }
    if ($cmd ne $exename) {
        return 0;
    }

    if ($args eq '') {
        return 1;
    }
    my $cmdline = getcmdline($pid);
    if ($cmdline !~ /$args/) {
        return 0;
    }
    return 1;
}


# ----------------------------------------------------------
#  Hotspot Editor
# ----------------------------------------------------------

sub hotspoteditpage(){
    my $language = shift;
    my $menu = shift;

    hotspotadminheader();
    hotspotcontentedit($language,$menu);
}

# ----------------------------------------------------------
#  Hotspot Header
# ----------------------------------------------------------
sub hotspotadminheader() {

    require '/var/efw/header.pl';
    &showhttpheaders();

    my $helpuri = get_helpuri($menu);
    $title = $brand.' '.$product." - Hotspot";

printf <<EOF
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<HTML>
<HEAD><META CONTENT="text/html; charset=utf-8" HTTP-EQUIV="Content-Type">
    <TITLE>$title</TITLE>
    <META CONTENT="text/html; charset=UTF-8" HTTP-EQUIV="Content-Type">
    <LINK HREF="/images/shortcut.ico" REL="shortcut icon">
    <STYLE TYPE="text/css">\@import url(/include/style.css);</STYLE>
    <STYLE TYPE="text/css">\@import url(/include/menu.css);</STYLE>
    <STYLE TYPE="text/css">\@import url(/include/content.css);</STYLE>
    <script language="javascript" type="text/javascript" src="/include/jquery.js"></script>
    <script language="javascript" type="text/javascript" src="/include/jquery.ifixpng.js"></script>
    <script language="JavaScript" type="text/javascript" src="/include/overlib_mini.js"></script>

    <script language="javascript" type="text/javascript" src="/include/uplink.js"></script>
    <link rel="stylesheet" type="text/css" media="screen" title="Uplinks Status" href="/include/uplinks-status.css" />

</HEAD>
<BODY>
<div id="flames">
  <DIV ID="main">
    <DIV ID="header">
EOF
;

    $image_path = `ls /home/httpd/html/images/product_*.jpg 2>/dev/null`;
    if ( ! $image_path ) {
        $image_path = `ls /home/httpd/html/images/endian_logo.png 2>/dev/null`;
    }
    if ( $image_path ) {
        $filename=substr($image_path,24);
        print "     <img id=\"logo-product\" src=\"/images/$filename\" alt=\"$product $brand\" />";
    };

printf <<EOF
      <DIV ID="header-icons">
      <ul>
           <li><a href="#" onclick="javascript:window.open('$helpuri','_blank','height=700,width=1000,location=no,menubar=no,scrollbars=yes');"><img src="/images/help.gif" alt="Help" border="0"> Help</a></li>
    	   <li><a href="/cgi-bin/logout.cgi" target="_self"><img src="/images/logout.gif" alt="Logout" border="0"> Logout</a></li>
      </ul>
      </DIV><!-- header-icons -->
      <DIV STYLE="margin-left: 25px;" ID="menu-top">
        <UL>
    <LI>
        <DIV CLASS="rcorner">
        <A HREF="/admin/">Hotspot</A>
        </DIV>
    </LI>
    <LI>
        <DIV CLASS="rcorner">
        <A HREF="/cgi-bin/hotspot-dial.cgi">%s</A>
        </DIV>
    </LI>
    </UL>
      </DIV><!-- menu-top -->
    </DIV><!-- header -->
EOF
,
_('Dialin'),
;
}

sub init_register_status($) {
    $register_status_hash = shift;
}

sub register_status($$) {
    my $item = shift;
    my $arr = shift;

    $register_status_hash->{$item} = $arr;
}
