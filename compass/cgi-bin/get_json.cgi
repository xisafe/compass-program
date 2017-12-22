#!/usr/bin/perl
require '/var/efw/header.pl';

my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my @paths = split(/=/, $parValue[0]);
my $path = uri_unescape($paths[1]);
$path =~ s/\+/ /g;

my @types = split(/=/, $parValue[1]);
my $type = uri_unescape($types[1]);
$type =~ s/\+/ /g;


my @strs = split(/=/, $parValue[1]);
my $str = uri_unescape($strs[1]);
$str =~ s/\+/ /g;
&validateUser();
#func：读文件以一个字符串返回
#传入：文件路径
sub read_file_string($)
{
	my $path = shift;
	my $string = "";
	my $count = 0;
	if($type eq 'json' || $type eq 'text')
	{
	open(MYFILE,"$path");
	foreach my $line (<MYFILE>) 
	{

		if($type eq 'json')
		{
			chomp($line);
			$line =~s/\n//g;
			$line =~s/\r//g;
			$line =~s/\s//g;
			$string .= $line;
		}elsif($type eq 'text')
		{
			chomp($line);
			if($line)
			{
				$string .= $line."\n";
			}
		}
	}
		close (MYFILE);
		return $string;
	}else{
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
		@pairs = split(/&/, $buffer);
		foreach (@pairs) {
			print $_;
			($name, $value) = split(/=/, $_);
			$name  =  &uri_unescape($name);
			$value =  &uri_unescape($value);
			if($name eq "path")
			{
				$path = $value;
			}
			if($name eq "str")
			{
				$str = $value;
			}
		}
		open(MYFILE,">$path");
		print MYFILE $str;
		close (MYFILE);
		return "ok";
	}
}

my $file_content = read_file_string($path);
print $file_content;