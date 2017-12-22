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


use Net::IPv4Addr qw (:all);

sub print_debug($) {
    my $msg = shift;

    return unless ($debug);
    print STDERR $msg;
}

sub prefix($$) {
    my $prefix = shift;
    my $ref = shift;
    my %ret_hash = ();
    my $ret = \%ret_hash;

    foreach $key (%$ref) {
	$ret->{$prefix.$key} = $ref->{$key};
    }

    return $ret;
}

sub hash_merge($$) {
    my $first = shift;
    my $second = shift;

    foreach my $key (keys %$second) {
	$first->{$key} = $second->{$key};
    }

    return $first;
}

sub select_from_hash($$) {
    my $ref = shift;
    my $session = shift;

    my @keys = @$ref;
    my %hash;

    foreach my $key (@keys) {
	$hash{$key} = $session->{$key};
    }
    return \%hash;
}

sub sanitize_ip {
    my $ip = shift;
    if ($ip =~ /^\d+\.\d+\.\d+\.\d+$/) {
	return $ip;
    }
    return '';
}

# check if this is a ordinary ip/mask pair.
sub check_ip ($$) {

    my $ip = shift;
    my $mask = shift;

    $ip   = sanitize_ip($ip);
    $mask = sanitize_ip($mask);

    $iptmp = eval { ipv4_parse($ip, $mask) };
    print_debug($iptmp);
    if (! defined($iptmp)) {
	return (0);
    }

    return (1, $ip, $mask);
}

sub get_pos($$) {
    my $ref = shift;
    my $search = shift;
    my @arr = @$ref;
    my $counter = 0;
    foreach $item (@arr) {
	if ($item eq $search) {
	    return $counter;
	}
	$counter++;
    }
    return undef;
}

# loads all values iedntified by the keys from the value_base into the session.
sub load_all_keys($$$$$) {
    my $session = shift;
    my $keys_ref = shift;
    my $value_base = shift;
    my $default_base = shift;
    my $override = shift;
    my @keys = @$keys_ref;

    foreach (@keys) {
	$key = $_;
	load_to_session($session, $key, $value_base, $default_base, $override);
    }
}


# loads one value identified by the key from the value_base into the session, if
# it does not already exist.
sub load_to_session($$$$$) {
    my $session = shift;
    my $key = shift;
    my $value_base = shift;
    my $default_base = shift;
    my $override = shift;

    if (($override == 0) && exists($session->{$key})) {
	return;
    }

    if (exists($value_base->{$key})) {
	$session->{$key} = $value_base->{$key};
	return;
    }

    if ($default_base == 0) {
	return;
    }
    if (exists($default_base->{$key})) {
	$session->{$key} = $default_base->{$key};
	return;
    }
}

1;

