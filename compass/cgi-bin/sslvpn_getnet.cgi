#!/usr/bin/perl

require '/var/efw/header.pl';
#获取传来参数,默认只有一个参数.

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my $conffile = "${swroot}/openvpn/settings";
&validateUser();
if(-e $conffile)
{
   open(FILE,$conffile);
   my @lines = <FILE>;
   close(FILE);
   foreach my $one (@lines){
      if($one =~/PURPLE_NET/)
	  {
	     my @split = split(/=/,$one);
		 print $split[1];
	  }
   }
} else {
   print "0";
}
1;