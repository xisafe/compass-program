#!/usr/bin/perl
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

require '/home/httpd/cgi-bin/netwizard_tools.pl';

my $uplinks = 'uplinks/';
my $session = 0;
my $settings = 0;

sub init_redtools($$) {
    $session = shift;
    $settings = shift;
    $uplinks = ${swroot}.'/uplinks/';
}


sub set_red_default($) {
    my $uplink = shift;

    if ($uplink !~ /^$/) {
	$uplink .= '_';
    }

    if (! $session->{$uplink.'ENABLED'}) {
	$session->{$uplink.'ENABLED'} = 'on';
    }
    $session->{$uplink.'RED_TYPE'} = $session->{'RED_TYPE'};
    if (! $session->{$uplink.'RED_DEV'}) {
	$session->{$uplink.'RED_DEV'} = $session->{'RED_DEV'};
    }
    if (! $session->{$uplink.'AUTOSTART'}) {
	$session->{$uplink.'AUTOSTART'} = "on";
    }
    if (! $session->{$uplink.'ONBOOT'}) {
	$session->{$uplink.'ONBOOT'} = "on";
    }
    if (! $session->{$uplink.'MANAGED'}) {
	$session->{$uplink.'MANAGED'} = "on";
    }
}

sub load_red($) {
    my $uplink = shift;
    $uplink = lc($uplink);
    return if ($uplink =~ /^$/);
    my $red_settings = readconf($uplinks.$uplink.'/settings');
    my @keys = keys(%$red_settings);
    load_all_keys($session, \@keys, $red_settings, 0, 0);
    load_all_keys($settings, \@keys, $red_settings, 0, 0);
}

sub save_red($$) {
    my $uplink = shift;
    my $data = shift;
    $uplink = lc($uplink);
    return if ($uplink =~ /^$/);
    writeconf($uplinks.$uplink.'/settings', $data);	
	`sudo fmodify $uplinks.$uplink.'/settings'`;
}

1;
