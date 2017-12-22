#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:获取公钥的cgi
#
      
#===============================================================================
require '/var/efw/header.pl';
# &validateUser();
my %par;
print "Content-type:text/html\r\n\r\n";
&getcgihash(\%par);
if( $par{'ACTION'} eq 'getPublicKey'){
		my $pkey;
		$pKey = &readPublicKey();
		print $pKey;
		exit;

}
