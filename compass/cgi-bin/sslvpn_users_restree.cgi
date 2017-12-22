#!/usr/bin/perl

require '/var/efw/header.pl';

my $conffile_dir = "/var/efw/openvpn/sync";
my $conffile = "/var/efw/openvpn/sync/settings";

my %par;
&validateUser();
getcgihash(\%par);
&make_file();
&query();

sub query(){
	my $related_resource = $par{'related_resource'};
	chomp($related_resource);
	if($related_resource ne ''){
		$related_resource =~ s/,/:/g;
		$result = `sudo ResMng -resgq -cld -s "$related_resource" 所有资源`;
	}else{
		$result = `sudo ResMng -resgq -cld 所有资源`;
	}
}

sub make_file(){
	if(!-e $conffile_dir){
		`mkdir $conffile_dir`;
	}
	
	if(!-e $conffile){
		`touch $conffile`;
	}
}

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
print $result;