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
	my $sync_name = $par{'sync_name'};
	chomp($sync_name);
	if($sync_name ne ''){
		my $userGroup = '';
		#根据名字，查找同步配置中的用户组信息
		my @conflines = read_conf_file($conffile);
		foreach my $line (@conflines){
			my @splitted = split(/,/, $line); 
			if($sync_name eq $splitted[0]){
				$userGroup = $splitted[3];
				last;
			}
		}
		if($userGroup ne ''){
			$userGroup =~ s/;/:/g;
			$result = `sudo ResMng -orgq -ch -s "$userGroup" 所有用户`;
		}else{
			$result = `sudo ResMng -orgq -ch 所有用户`;
		}
	}else{
		$result = `sudo ResMng -orgq -ch 所有用户`;
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