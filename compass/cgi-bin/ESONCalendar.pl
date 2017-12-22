#!/usr/bin/perl

sub change_date($){
	my $date = shift;
	my @t = split(/-/,$date);
	my $years=$t[0];
	my $day_length = length($t[2]);
	my $month_length = length($t[1]);
	if ($month_length == 1) {
		$t[1] = "0".$t[1];
		$date = "$t[0]-$t[1]-$t[2]";
	}
	if ($day_length == 1) {
		$t[2] = "0".$t[2];
		$date = "$t[0]-$t[1]-$t[2]";
	}
	return $date;
}
sub dateToFilestring($) {
    my $date = shift;
    $date =~ s/\-//g;
    return $date;
}

1;