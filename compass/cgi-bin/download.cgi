#!/usr/bin/perl
use strict;
require '/var/efw/header.pl';
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
&validateUser();

my $file ="/var/efw/ip-mac/TEMPLATE";
my $filename="TEMPLATE";
		
		if( -e "$file")
		{
		open(DLFILE, "<$file") || Error('open', "$file");  
		my @fileholder = <DLFILE>;  
		close (DLFILE) || Error ('close', "$file"); 
		print "Content-Type:application/x-download\n";  
		print "Content-Disposition:attachment;filename=$filename\n\n";
		print @fileholder;
		exit;
		}
		else
		{
          print "Content-type:text/html\n\n";
          print qq{<html><head><title>文件不存在！</title></head><body><br/><br/>
                <br/><center><h1>The file does not exist.</h1></center></body></html>};
          exit;
		}