#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: dial.cgi,v 1.4 2003/12/11 11:06:40 riddles Exp $
#
#use CGI::Carp qw(fatalsToBrowser);
require '/var/efw/header.pl';

my %cgiparams;
&validateUser();
$cgiparams{'ACTION'} = '';
&getcgihash(\%cgiparams);
$uplink = $cgiparams{'UPLINK'};
my $cgi = CGI->new ();
$user_agent = $cgi->user_agent();

sub uplinkaction($$) {
    my $uplink = shift;
    my $switch = shift;

    my %uldata = 0;
    my $settingsfile = "${swroot}/uplinks/$uplink/settings";

    return if (! -e $settingsfile);
    readhash($settingsfile, \%uldata);
    if ($switch eq 'start') {
	$uldata{'AUTOSTART'} = 'on';
	&log("Toggle on manually uplink '%s'");
    } elsif ($switch eq 'stop') {
	$uldata{'AUTOSTART'} = 'off';
	&log("Toggle off manually uplink '%s'");
    }
    writehash($settingsfile, \%uldata);

    open (UPLINKSTART, "sudo /etc/rc.d/uplinks $switch $uplink|");
    close UPLINKSTART;
}

sub status
{
        my $status;
        opendir UPLINKS, "/var/efw/uplinks" or die "Cannot read uplinks: $!";
                foreach my $uplink (sort grep !/^\./, readdir UPLINKS) {
                    if ( -f "${swroot}/uplinks/${uplink}/active") {
                        if ( ! $status ) {
                                $timestr = &age("${swroot}/uplinks/${uplink}/active");
                                print "$uplink:Connected:$timestr\n";
                        } else {
                                $timestr = &age("${swroot}/uplinks/${uplink}/active");
                                print "$uplink:$status:$uplink\n";
                        }
                    } elsif ( -f "${swroot}/uplinks/${uplink}/connecting") {
                        if ( ! $status ) {
                                print "$uplink:Connecting:\n";
                        } else {
                                print "$uplink:Failure:$status\n";
                        }
                    } else {
		    if ( ! $status ) {
		    	print "$uplink:Idle:\n";
                    } else {
		    	print "$uplink:Failure:\n";	
		    }
	    }	
	}
}

# backwards compatible
if ($cgiparams{'ACTION'} eq _('Connect')) {
    uplinkaction($uplink, 'start');
} elsif ($cgiparams{'ACTION'} eq _('Disconnect')) {
    uplinkaction($uplink, 'stop');
}
# action should not be language specific
elsif ($cgiparams{'ACTION'} eq 'Connect') {
    uplinkaction($uplink, 'start');
} elsif ($cgiparams{'ACTION'} eq 'Disconnect') {
    uplinkaction($uplink, 'stop');
}


if ($user_agent eq "EFW-Client") {
  	&showhttpheaders();
  	print status();
	exit;
} else {
	print "Status: 302 Moved\nLocation: /cgi-bin/main.cgi\n\n";
}
