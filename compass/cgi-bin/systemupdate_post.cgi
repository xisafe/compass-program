#!/usr/bin/perl
#auther:Liu Julong
#createDate:2015/05/20
require '/var/efw/header.pl';
use strict;
use CGI::Carp qw(fatalsToBrowser);
use Digest::MD5;
my $uploaddir = '/tmp';
use CGI;
my $IN = new CGI;
my $file = $IN->param('POSTDATA');
my %query;
&getqueryhash(\%query);
#my $fileName = $query{'qqfile'};
my $fileName = "FWUpdateSystem.bin";
if(!-e $uploaddir)
{
   `sudo mkdir $uploaddir`;
}
open(WRITEIT, ">$uploaddir/$fileName") or die "Cant write to $uploaddir/$fileName. Reason: $!";
    print WRITEIT $file;
close(WRITEIT);
showhttpheaders();
print qq|{ "success": true,"filename":$fileName }|;

sub getqueryhash($){
    my $query = shift;
    my $query_string = $ENV{'QUERY_STRING'};
    if ($query_string ne '') {
        my @key_values = split("&", $query_string);
        foreach my $key_value (@key_values) {
            my ($key, $value) = split("=", $key_value);
            $query->{$key} = $value;
            #===对获取的值进行一些处理===#
            $query->{$key} =~ s/\r//g;
            $query->{$key} =~ s/\n//g;
            chomp($query->{$key});
        }
    }
    return;
}