#!/usr/bin/perl
#2012-09-04
#zhouyuan
#��������������õ��ĺ�̨ͨ�ýű�

require '/var/efw/header.pl';

my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my @paths = split(/=/, $parValue[0]);
my @names = split(/=/, $parValue[1]);
my $name = ( @names > 1) ? @names[1] : "";

my $passwd   = '/usr/bin/openvpn-sudo-user';
my $path = uri_unescape($paths[1]);
$path =~ s/\+/ /g;
my $data;
# &validateUser();
if ($path !~ /openvpn\/passwd/ && $path !~ /var\/efw\/userinfo\/userslist/ ) {
	open(FILE,$path);
	foreach my $line(<FILE>) 
	{
		$data .= $line;
	}
}
elsif( $path =~ /var\/efw\/userinfo\/userslist/ ){
	
	open(FILE,$path);
	foreach my $line(<FILE>) 
	{
		chomp($line);
		my $username = (split(/,/,$line))[0];
		if( $name && ($name eq $username)){
				$data = 1;
				last;
		}
		# $data .= $username."\n";
	}
}
else{
	$data = `$passwd longlist`;
}
close FILE;
print $data;