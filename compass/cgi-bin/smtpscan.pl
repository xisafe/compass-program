#!/usr/bin/perl
#
# SMTP Proxy CGI for Endian Firewall
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
require './endianinc.pl';
require '/var/efw/header23.pl';

$smtpscan_conffile         = "${swroot}/smtpscan/settings";
$smtpscan_conffile_default = "${swroot}/smtpscan/default/settings";
$extensions_file           = "${swroot}/smtpscan/default/extensions";
$extensions_file_custom    = "${swroot}/smtpscan/extensions";
$smtpd_domains             = "${swroot}/smtpscan/domains";

$commtouch = `rpm -q efw-commtouch` ne "package efw-commtouch is not installed\n" ? 1 : 0;

$commtouch_conffile         = "${swroot}/commtouch/settings";
$commtouch_conffile_default = "${swroot}/commtouch/default/settings";

$sender_whitelist_file = "${swroot}/smtpscan/sender_whitelist";
$sender_blacklist_file = "${swroot}/smtpscan/sender_blacklist";
$recipient_whitelist_file = "${swroot}/smtpscan/recipient_whitelist";
$recipient_blacklist_file = "${swroot}/smtpscan/recipient_blacklist";
$client_whitelist_file = "${swroot}/smtpscan/client_whitelist";
$client_blacklist_file = "${swroot}/smtpscan/client_blacklist";

$spam_whitelist_file = "${swroot}/smtpscan/spam_whitelist";
$spam_blacklist_file = "${swroot}/smtpscan/spam_blacklist";

$user_phraselist_subject_file = "${swroot}/smtpscan/phraselists/user_phraselist_subject";
$user_phraselist_body_file = "${swroot}/smtpscan/phraselists/user_phraselist_body";

$whitelist_client_file = "${swroot}/smtpscan/postgrey_whitelist_clients.local";
$whitelist_recipient_file = "${swroot}/smtpscan/postgrey_whitelist_recipients.local";

$rbl_file = "${swroot}/smtpscan/default/RBL";
$rbl_local_file = "${swroot}/smtpscan/default/RBL.local";

$transparent_source_bypass = "${swroot}/smtpscan/transparent_source_bypass";
$transparent_destination_bypass = "${swroot}/smtpscan/transparent_destination_bypass";

sub read_file($) {
    # read out a file: needed for blacklists
    # attributes: filepath (string)
    # returns: filevalue (string)
    my $file = shift;
    undef $lines;
    open(FILE,"$file");
    while (<FILE>) { $lines .= $_ };
    close(FILE);
    return $lines;
}

sub write_file($$) {
    # writes a string into a file
    # attributes: filepath (string), value of file (string)
    my $file = shift;
    my $value = shift;
    
    open (FILE, ">$file");
    print FILE $value;
	`sudo fmodify $file`;
    close (FILE);
}

sub read_config_file($) {
    my @lines;
    my $conffile = shift;
    open( FILE, $conffile );
    foreach my $line (<FILE>) {
        chomp($line);
        push( @lines, $line );
    }
    close(FILE);
    return @lines;
}

sub save_settings($$$$) {
    # save settings to config files
    # attributes:
    #     default settings (hash reference)
    #     current settings (hash reference)
    #     params which should be saved (hash reference)
    #     checkboxes inside the form you want to save (array reference)
    
    my $default_conf_ref = shift;
    my $conf_ref = shift;
    my $params_ref = shift;
    my $checkboxes_ref = shift; #needed because otherwhise we do not know when a checkbox is unchecked
    
    my %default_conf = %$default_conf_ref;
    my %conf = %$conf_ref;
    my %params = %$params_ref;
    my @checkboxes = @$checkboxes_ref;
        
    foreach $checkbox (@checkboxes) {
        if (!exists $params{$checkbox}) {
            $params{$checkbox} = "off";
            next;
        }
    }
    
    my @rbl_file = read_config_file($rbl_file);
    my $rbl_activated = "";
    
    my $changed = 0;
    my $saverbl = 0;
    
    while(($key, $value) = each(%params)) {
        # check if key needs to be saved
        if (!exists $conf{$key}) {
            next;
        }
        my $next = 0;
        foreach $line (@rbl_file) {
            my @rbl = split(/\|/, $line);
            if ($key ne $rbl[0]) {
                next;
            }
            else {
                $saverbl = 1;
            }
            if ($value eq "0") {
                if ( $rbl_activated ne "") { 
                    $rbl_activated = $rbl_activated . "," . $rbl[0];
                } else {
                    $rbl_activated = $rbl[0];
                }
                $next = 1;
                next;
            }
        }
        if ($next eq 1) {
            next;
        }
        
        # check if key changed
        if ($conf{$key} eq $value) {
            next;
        }
        $changed = 1;
        
        if ($key eq "SENDER_WHITELIST") {
            write_file($sender_whitelist_file, $value);
            next;
        }
		
        if ($key eq "SENDER_BLACKLIST") {
            write_file($sender_blacklist_file, $value);
            next;   
        }
        if ($key eq "RECIPIENT_WHITELIST") {
            write_file($recipient_whitelist_file, $value);
            next;
        }
        if ($key eq "RECIPIENT_BLACKLIST") {
            write_file($recipient_blacklist_file, $value);
            next;
        }
        if ($key eq "CLIENT_WHITELIST") {
            write_file($client_whitelist_file, $value);
            next;
        }
        if ($key eq "CLIENT_BLACKLIST") {
            write_file($client_blacklist_file, $value);
            next;
        }
        if ($key eq "USER_PHRASELIST_SUBJECT") {
            write_file($user_phraselist_subject_file, $value);
            next;
        }
        if ($key eq "USER_PHRASELIST_BODY") {
            write_file($user_phraselist_body_file, $value);
            next;
        }
        if ($key eq "WHITELIST_RECIPIENT") {
            write_file($whitelist_recipient_file, $value);
            next;
        }
        if ($key eq "WHITELIST_CLIENT") {
            write_file($whitelist_client_file, $value);
            next;
        }
        if ($key eq "SPAM_WHITELIST") {
            write_file($spam_whitelist_file, $value);
            next;
        }
        if ($key eq "SPAM_BLACKLIST") {
            write_file($spam_blacklist_file, $value);
            next;
        }
        if ($key eq "BYPASS_SOURCE") {
            write_file($transparent_source_bypass, $value);
            next;
        }
        if ($key eq "BYPASS_DESTINATION") {
            write_file($transparent_destination_bypass, $value);
            next;
        }
        
        $conf{$key} = $value;
    }
    
    if ($saverbl eq 1) {
        $conf{"RBL"} = $rbl_activated;
    }
    if ($commtouch eq 1) {
        my %commtouch_default_conf = ();
        my %commtouch_conf = ();
        
        if ( -e $commtouch_conffile_default ) {
            &readhash( "$commtouch_conffile_default", \%commtouch_default_conf );
            &readhash( "$commtouch_conffile_default", \%commtouch_conf );
        }
        if ( -e $commtouch_conffile ) {
            &readhash( "$commtouch_conffile", \%commtouch_conf );
        }
        $commtouch_conf{ENABLED} = $conf{COMMTOUCH_ENABLED};
        delete $conf{COMMTOUCH_ENABLED};
        
        # clean up settingsfile
        while(($key, $value) = each(%commtouch_conf)) {
            # delete values which do not differ from default settings
            if ($commtouch_default_conf{$key} eq $value) {
                delete $commtouch_conf{$key};
            }
            if (!exists $commtouch_default_conf{$key}) {
                delete $commtouch_conf{$key};
            }
        }

        writehash($commtouch_conffile, \%commtouch_conf);
    }
    
    # clean up settingsfile
    while(($key, $value) = each(%conf)) {
        # delete values which do not differ from default settings
        if ($default_conf{$key} eq $value) {
            delete $conf{$key};
        }
        if (!exists $default_conf{$key}) {
            delete $conf{$key};
        }
    }
    
    writehash($smtpscan_conffile, \%conf);
    
    return $changed;
}

sub reload_par() {
## -------------------------------------------------------------
## get settings and CGI parameters
## -------------------------------------------------------------
    %conf = (SENDER_WHITELIST => "", SENDER_BLACKLIST => "", 
             RECIPIENT_WHITELIST => "", RECIPIENT_BLACKLIST => "",
             CLIENT_WHITELIST => "", CLIENT_BLACKLIST => "",
             KEY_FILTER => "",
             USER_PHRASELIST_SUBJECT => "", USER_PHRASELIST_BODY => "",
             WHITELIST_CLIENT => "", WHITELIST_RECIPIENT => "",
             BYPASS_SOURCE => "", BYPASS_DESTINATION => "",
             SPAM_WHITELIST => "", SPAM_BLACKLIST => "");
    
    if ( -e $smtpscan_conffile_default ) {
        &readhash( "$smtpscan_conffile_default", \%default_conf );
        &readhash( "$smtpscan_conffile_default", \%conf );
    }
    if ( -e $smtpscan_conffile ) {
        &readhash( "$smtpscan_conffile", \%conf );
    }
    if ($commtouch eq 1) {
        my %commtouch_conf = ();
        if ( -e $commtouch_conffile_default ) {
            &readhash( "$commtouch_conffile_default", \%commtouch_conf );
        }
        if ( -e $commtouch_conffile ) {
            &readhash( "$commtouch_conffile", \%commtouch_conf );
        }
        $conf{COMMTOUCH_ENABLED} = $commtouch_conf{ENABLED};
    }
    if ( -e $sender_whitelist_file ) {
        $conf{SENDER_WHITELIST} = read_file($sender_whitelist_file);
    }
    if ( -e $sender_blacklist_file ) {
        $conf{SENDER_BLACKLIST} = read_file($sender_blacklist_file);
    }
    if ( -e $recipient_whitelist_file ) {
        $conf{RECIPIENT_WHITELIST} = read_file($recipient_whitelist_file);
    }
    if ( -e $recipient_blacklist_file ) {
        $conf{RECIPIENT_BLACKLIST} = read_file($recipient_blacklist_file);
    }
    if ( -e $client_whitelist_file ) {
        $conf{CLIENT_WHITELIST} = read_file($client_whitelist_file);
    }
    if ( -e $client_blacklist_file ) {
        $conf{CLIENT_BLACKLIST} = read_file($client_blacklist_file);
    }
    if ( -e $whitelist_client_file ) {
        $conf{WHITELIST_CLIENT} = read_file($whitelist_client_file);
    }
    if ( -e $user_phraselist_subject_file ) {
        $conf{USER_PHRASELIST_SUBJECT} = read_file($user_phraselist_subject_file);
    }
    if ( -e $user_phraselist_body_file ) {
        $conf{USER_PHRASELIST_BODY} = read_file($user_phraselist_body_file);
    }
    if ( -e $whitelist_recipient_file ) {
        $conf{WHITELIST_RECIPIENT} = read_file($whitelist_recipient_file);
    }
    if ( -e $spam_whitelist_file ) {
        $conf{SPAM_WHITELIST} = read_file($spam_whitelist_file);
    }
    if ( -e $spam_blacklist_file ) {
        $conf{SPAM_BLACKLIST} = read_file($spam_blacklist_file);
    }
    if ( -e $transparent_source_bypass ) {
        $conf{BYPASS_SOURCE} = read_file($transparent_source_bypass);
    }
    if ( -e $transparent_destination_bypass ) {
        $conf{BYPASS_DESTINATION} = read_file($transparent_destination_bypass);
    }
    my @rbls = read_config_file($rbl_file);
    foreach $line (@rbls) {
        my @rbl = split(/\|/, $line);
        $conf{$rbl[0]} = "0";
        foreach my $allowed_rbl (split(/,/, $conf{RBL})) {
            if ($rbl[0] eq $allowed_rbl) {
                $conf{$rbl[0]} = "1";
                last;
            }
        }
    }
    return \%default_conf, \%conf;
}
