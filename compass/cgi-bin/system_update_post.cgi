#!/usr/bin/perl
require '/var/efw/header.pl';
use strict;
use CGI::Carp qw(fatalsToBrowser);
use Digest::MD5;
my $uploaddir = '/var/updata/';
use CGI;
my $IN = new CGI;
my $file = $IN->param('POSTDATA');
if(!-e $uploaddir)
{
   `sudo mkdir $uploaddir`;
}
open(WRITEIT, ">$uploaddir/updata_sys.bin") or die "Cant write to $uploaddir/updata_sys.bin. Reason: $!";
    print WRITEIT $file;
close(WRITEIT);
showhttpheaders();
print qq|{ "success": true }|;