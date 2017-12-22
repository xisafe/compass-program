#!/usr/bin/perl
use strict;
use CGI::Carp qw(fatalsToBrowser);
use Digest::MD5;
require '/var/efw/header.pl';
&validateUser();
my $uploaddir = '/var/updata/';
use CGI;
my $IN = new CGI;
my $file = $IN->param('POSTDATA');
if(!-e $uploaddir)
{
   `sudo mkdir $uploaddir`;
}
open(WRITEIT, ">$uploaddir/updata_rules.bin") or die "Cant write to $uploaddir/updata_rules.bin. Reason: $!";
    print WRITEIT $file;
close(WRITEIT);
print qq|{ "success": true }|;