#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
# (c) Endian GmbH/srl
#
# Copyright (C) 01-02-2002 Graham Smith <grhm@grhm.co.uk>
#              - Fixed DHCP Leases added
#
# $Id: dhcp.cgi,v 1.14.2.24 2004/11/29 10:49:16 eoberlander Exp $
#
#  Franck    -rewrite for two or more interface
#  nov/2004    -check range is in correct subnet
#        -add NTP option
#        -add display sorting of actives leases
#
# to do : choose a correct format for displaying dates
#
require '/var/efw/header.pl';
use Net::IPv4Addr qw (:all);
use HTML::Entities;

my %dhcpsettings;
my %netsettings;
my %hostsettings;
my %hotspotsettings;
my $filename = "${swroot}/dhcp/fixleases";

my $conffile    = "${swroot}/dhcp/settings";
my $conffile_default = "${swroot}/dhcp/default/settings";
my $restart     = '/usr/local/bin/restartdhcp';

my %enable_file = ();
$enable_file{'GREEN'}  = "${swroot}/dhcp/enable_green";
$enable_file{'BLUE'}   = "${swroot}/dhcp/enable_blue";
$enable_file{'ORANGE'} = "${swroot}/dhcp/enable_orange";

my $ntp_enable_file = "${swroot}/time/enable";

my $custom_global = "";
my $custom_global_file="${swroot}/dhcp/custom.tpl";

my %enable = ();

sub PrintLeases()
{
    if (! -f "/var/lib/dhcp/dhcpd.leases") {
	return;
    }
    &openbox('100%', 'left', _('Current dynamic leases'));
    printf <<END
<br />
<table width='100%' cellpadding="0" cellspacing="0" class='ruleslist'>
<tr>
<td width='25%' align='center' class='boldbase'><b>%s</b></td>
<td width='25%' align='center' class='boldbase'><b>%s</b></td>
<td width='20%' align='center' class='boldbase'><b>%s</b></td>
<td width='30%' align='center' class='boldbase'><b>%s</b></td>
</tr>
END
,
_('IP address'),
_('MAC address'),
_('Hostname'),
_('Lease expires')
;

    open(LEASES,"/var/lib/dhcp/dhcpd.leases") or die "Can't open dhcpd.leases";
    while ($line = <LEASES>) {
	next if( $line =~ /^\s*#/ );
	chomp($line);
	@temp = split (' ', $line);

	if ($line =~ /^\s*lease/) {
	    $ip = $temp[1];
	    #All field are not necessarily read. Clear everything
	    $endtime = 0;
	    $ether = "";
	    $hostname = "";
	}

	if ($line =~ /^\s*ends/) {
	    $line =~ /(\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+)/;
	    $endtime = timegm($6, $5, $4, $3, $2 - 1, $1 - 1900);
	}

	if ($line =~ /^\s*hardware ethernet/) {
	    $ether = $temp[2];
	    $ether =~ s/;//g;
	}

	if ($line =~ /^\s*client-hostname/) {
	    $hostname = "$temp[1] $temp[2] $temp[3]";
	    $hostname =~ s/;//g;
	    $hostname =~ s/\"//g;
	}

	if ($line eq "}") {
	    @record = ('IPADDR',$ip,'ENDTIME',$endtime,'ETHER',$ether,'HOSTNAME',$hostname);
    	    $record = {};                        		# create a reference to empty hash
	    %{$record} = @record;                		# populate that hash with @record
	    $entries{$record->{'IPADDR'}} = $record;   	# add this to a hash of hashes
	}
    }
    close(LEASES);

    my $id = 0;
	my $count = 1;
    foreach my $key (sort leasesort keys %entries) {
	   `mkdir /tmp/$count`;
	   ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $dst) = localtime ($entries{$key}->{ENDTIME});
	   $enddate = sprintf ("%d/%02d/%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);

	   if ($entries{$key}->{ENDTIME} < time() ){
	      
	   } else {
	      my $hostname = &cleanhtml($entries{$key}->{HOSTNAME},"y");
          if ($id % 2) {
	          print "<tr class='even'>"; 
	      }
	      else {
	          print "<tr class='oodd'>"; 
	      }
		  printf <<END
                 <td align='center'>$entries{$key}->{IPADDR}</td>
                 <td align='center'>$entries{$key}->{ETHER}</td>
                 <td align='center'>&nbsp;$hostname </td>
                 <td align='center'>$enddate</td></tr>
END
;
          $id++;
	   }
	}
	if ($id eq '0') {
		no_tr(4,_('Current no content'));
    }
	print "</table><br />";
    &closebox();
}

$enable{'GREEN'} = 0;
if (-e $enable_file{'GREEN'}) {
  $enable{'GREEN'} = 1;
}
$enable{'BLUE'} = 0;
if (-e $enable_file{'BLUE'}) {
  $enable{'BLUE'} = 1;
}
$enable{'ORANGE'} = 0;
if (-e $enable_file{'ORANGE'}) {
  $enable{'ORANGE'} = 1;
}

$ntp_enable = 0;
if (-e $ntp_enable_file) {
  $ntp_enable = 1;
}
&showhttpheaders();

@ITFs=('GREEN');

if (orange_used()) {
    push(@ITFs, 'ORANGE');
}
if (blue_used()) {
    push(@ITFs, 'BLUE');
}

my %interface_title = (
    'GREEN' => _('Green interface'),
    'ORANGE' => _('Orange interface'),
    'BLUE' => _('Blue interface')
);

# dependent interface variable
foreach $itf (@ITFs) {
  $dhcpsettings{"ENABLE_${itf}"} = '';
  $dhcpsettings{"START_ADDR_${itf}"} = '';
  $dhcpsettings{"END_ADDR_${itf}"} = '';
  $dhcpsettings{"ONLY_FIXEDLEASE_${itf}"} = '';
  $dhcpsettings{"DOMAIN_NAME_${itf}"} = '';
  $dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} = '';
  $dhcpsettings{"MAX_LEASE_TIME_${itf}"} = '';
  $dhcpsettings{"GATEWAY_${itf}"} = '';
  $dhcpsettings{"WINS1_${itf}"} = '';
  $dhcpsettings{"WINS2_${itf}"} = '';
  $dhcpsettings{"DNS1_${itf}"} = '';
  $dhcpsettings{"DNS2_${itf}"} = '';
  $dhcpsettings{"NTP1_${itf}"} = '';
  $dhcpsettings{"NTP2_${itf}"} = '';
}

&getcgihash(\%dhcpsettings);

my @current = ();
if ( -e $filename) {
    open(FILE, "$filename") or die 'Unable to open fixed leases file.';
    @current = <FILE>;
    close(FILE);
}

&readhash("${swroot}/ethernet/settings", \%netsettings);
&readhash("${swroot}/host/settings", \%hostsettings);

if (-e "/usr/lib/efw/hotspot/default/settings") {
    &readhash("/usr/lib/efw/hotspot/default/settings", \%hotspotsettings);
}
if (-e "${swroot}/hotspot/settings") {
    &readhash("${swroot}/hotspot/settings", \%hotspotsettings);
}

foreach $itf (@ITFs) {
    if ($netsettings{"${itf}_NETADDRESS"} ne "" and $netsettings{"${itf}_NETMASK"} ne "") {
        my $netaddress = $netsettings{"${itf}_NETADDRESS"};
        my $fwaddress = $netsettings{"${itf}_ADDRESS"};
        my $broadcastaddress = ipv4_broadcast($netsettings{"${itf}_NETADDRESS"}, $netsettings{"${itf}_NETMASK"});
        my @ip = split(/\./, $fwaddress);
        my @net = split(/\./, $netaddress);
        my @broadcast = split(/\./, $broadcastaddress);
        if (@ip[3] eq @broadcast[3] - 1) {
            if ($dhcpsettings{"START_ADDR_${itf}"} eq "") {
                $dhcpsettings{"START_ADDR_${itf}"} = @net[0].".".@net[1].".".@net[2].".".(@net[3] + 1);
            }
            if ($dhcpsettings{"END_ADDR_${itf}"} eq "") {
                $dhcpsettings{"END_ADDR_${itf}"} = @ip[0].".".@ip[1].".".@ip[2].".".(@ip[3] - 1);
            }
        }
        else {
            if ($dhcpsettings{"START_ADDR_${itf}"} eq "") {
                $dhcpsettings{"START_ADDR_${itf}"} = @ip[0].".".@ip[1].".".@ip[2].".".(@ip[3] + 1);
            }
            if ($dhcpsettings{"END_ADDR_${itf}"} eq "") {
                $dhcpsettings{"END_ADDR_${itf}"} = @broadcast[0].".".@broadcast[1].".".@broadcast[2].".".(@broadcast[3] - 1);
            }
        }
    }
}

&openpage(_('DHCP configuration'), 1, '');

&openbigbox($errormessage, $warnmessage, $notemessage);
if ($warnNTPmessage)
{
    $warnNTPmessage = "<td>$warnNTPmessage</td>";
}
my $num=0;
foreach $itf (@ITFs) {
    if ($enable{$itf}) {
    &PrintLeases();
    $num++;
    last;             #Print one time only for all interfaces
    };
}
if ($num < 1){&PrintLeases();}
&closebigbox();
&closepage();