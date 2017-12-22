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

require '/var/efw/header.pl';
$reload = 0;
$routing_config = "${swroot}/ipv6/route/config";
$needreload = "${swroot}/routing/needreload";
sub read_config_file() {
    my @lines;
    open (FILE, "$routing_config");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        if (!is_valid($line)) {
            next;
        }
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub read_config_line($) {
    my $line = shift;
    my @lines = read_config_file();
    return $lines[$line];
}

sub save_config_file_back($) {
    my $ref = shift;
    my @lines = @$ref;
    open (FILE, ">$routing_config");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
	`sudo fmodify $routing_config`;
    close(FILE);
    $reload = 1;
}

sub line_count() {
    open (FILE, "$routing_config") || return 0;
    my $i = 0;
    foreach (<FILE>) {
        $i++;
    }
    close FILE;
    return $i;
}

sub append_config_file($) {
    my $line = shift;
    open (FILE, ">>$routing_config");
    print FILE $line."\n";
    close FILE;
	`sudo fmodify $routing_config`;
    $reload = 1;
}

sub is_valid($) {
    my $line = shift;
    # temporary hack;
    # if ($line =~ /(?:(?:[^,]*),){10}/ || $line =~ /(?:(?:[^,]*),){7}/) {
    #     return 1;
    # }
    return 1;
}

sub config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    if (! is_valid($line)) {
        return;
    }
    my @temp = split(/,/, $line);
    $config{'destination'} = $temp[0];
    $config{'gw'} = $temp[1];
    $config{'dev'} = $temp[2];
    return %config;
}

sub toggle_enable($$) {
    my $line = shift;
    my $enable = shift;
    if ($enable) {
        $enable = 'on';
    } 
    else {
        $enable = 'off';
    }

    my %data = config_line(read_config_line($line));
    $data{'enabled'} = $enable;

    return save_line($line,
                     $data{'destination'},
                     $data{'gw'},
                     $data{'dev'},
                   );
}

sub delete_line($) {
    my $line = shift;
    my @lines = read_config_file();
    if (! @lines[$line]) {
        return;
    }
    delete (@lines[$line]);
    save_config_file_back(\@lines);
}

sub create_line($$$) {
    my $destination = shift;
    my $gateway = shift;
    my $dev = shift;
    return "$destination,$gateway,$dev";
}

sub save_line($$$$) {
    my $line = shift;
    my $destination = shift;
    my $gateway = shift;
    my $dev = shift;
    my $tosave = create_line($destination, $gateway, $dev);
    append_config_file($tosave);
    my @lines = read_config_file();
    if (! $lines[$line]) {
        push(@errormessages, _('Configuration line not found!'));
        return 0;
    }

    my %split = config_line($lines[$line]);
    if (($split{'destination'} ne $destination) ||($split{'gw'} ne $gateway) ||($split{'dev'} ne $dev) ) 
	{
        $lines[$line] = $tosave;
        save_config_file_back(\@lines);
    }
    return 1;
}

