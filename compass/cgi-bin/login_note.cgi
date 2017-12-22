#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2011-07-25

require '/var/efw/header.pl';
use CGI();
use URI::Escape;

my @parValue = split(/&/, $ENV{'QUERY_STRING'});
my $length = @parValue;
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

&validateUser();
my @starts = split(/=/, $parValue[0]);
my $type= "";
for(my $i = 0;$i<$length;$i++)
{
	my @temp = split(/=/, $parValue[$i]);
	if($temp[0] eq "write" && $temp[1] eq "write")
	{
		$type = uri_unescape($temp[1]);
	}elsif($temp[0] eq "read" && $temp[1] eq "read"){
		$type = uri_unescape($temp[1]);
	}
}

my $note_conf = "/home/httpd/html/note";


if($type eq "read")
{
	open (FILE, "<$note_conf");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    print $lines[0];
}else{
	open (FILE, ">$note_conf");
	print FILE "no";
	close (FILE);
}
