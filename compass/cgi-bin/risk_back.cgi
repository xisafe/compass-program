#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2012-06-06
require '/var/efw/header.pl';
&validateUser();
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my $dir = "/var/efw/risk/evaluation/risk_evaluation.log";

my $data = "";

#获取风险日志数据
sub risk_data()
{
	my $count = 0;
	open(FILE,$dir);
	foreach my $line (<FILE>) 
	{
		chomp($line);
		if($count>0 && $line)
		{
			$data .= $line."\n";
		}
		$count++;
	}
	close FILE;
}

risk_data();
print $data;


