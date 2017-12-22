#!/usr/bin/perl

#file:detect_ajax.cgi
#author:zhangzheng
use CGI();
use URI::Escape;
require '/var/efw/header.pl';
my $file = "/var/efw/ip-mac/scanedip";
my $download_file = "/var/efw/ip-mac/download";
my $needreload = "/var/efw/ip-mac/needreload";
my $data_file = "/var/efw/ip-mac/arptables";
my $ini_scan = "/var/efw/ip-mac/ini_scanedip";
$ENV{'QUERY_STRING'} = uri_unescape($ENV{'QUERY_STRING'});
my @parValue = split(/&/, $ENV{'QUERY_STRING'});
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
my $name,$value,$scan_value,$method_value,$enabled_value,$enabled_line;
my $scaned;
&validateUser();
foreach $par(@parValue){
	($name,$value) = split(/=/, $par);
	if ($name eq "method") {
		$method_value = $value;
	}
	if ($name eq "iface") {
		$scan_value = $value;
	}
	if ($name eq "enabled") {
		$enabled_line = $value;
	}
	if ($name eq "yes_no") {
		$enabled_value = $value;
	}
	if ($name eq "hunhe") {
		$hunhe = $value;
	}
	if ($name eq "changeiface") {
		$changed = $value;
	}
}

sub read_config_file($) {
    my @lines;
	my $file=shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}
sub copy_down(){
	open(FILE,">$download_file");
	foreach my $line (read_config_file($data_file)) {
		my @temp = split(/,/,$line);
		print FILE "$temp[0],$temp[1]\n";
	}		
	close(FILE);
}
###如果是扫描，则进入扫描阶段
my @final_save;
if ($ENV{'QUERY_STRING'} =~ /method=/) {
	if ($method_value ne 'searched') {
		if ($method_value eq "scan_ip") {
			system("sudo /usr/local/bin/ipscan.sh -n $scan_value");
			system("cp $file $ini_scan");
			sleep 1;
		}
		if ($method_value eq "scan_iface") {
			system("sudo /usr/local/bin/ipscan.sh -i $scan_value");
			system("cp $file $ini_scan");
			sleep 1;
		}
		my @scaned_line = read_config_file($file);
		for (my $i=0; $i<@scaned_line ;$i++) {
			my @temp=split(/,/,$scaned_line[$i]);
			my $flag = 1;
			foreach my $elem (read_config_file($data_file)) {
				if ($elem =~ /$temp[0]/ || $elem =~ /$temp[1]/) {	
					$flag = 0;
				}
			}
			if ($flag) {	
				$scaned  .= "===$temp[0],$temp[1]";
				push(@final_save,$scaned_line[$i])
			}
		}
		save_config_file(\@final_save,$file);
	}
	else{
		system("cp $ini_scan $file");
		my @saves;
		my @scaned_line = read_config_file($file);
		foreach my $line (@scaned_line) {
			if ($line =~/$scan_value/) {
				my @temp=split(/,/,$line);
				my $flag = 1;
				foreach my $elem (read_config_file($data_file)) {
					if ($elem =~ /$temp[0]/ || $elem =~ /$temp[1]/) {	
						$flag = 0;
					}
				}
				if ($flag) {					
					$scaned  .= "===$temp[0],$temp[1]";
					push(@saves,$line);
				}
			}
		}
		save_config_file(\@saves,$file);
	}
	print $scaned;
}
###结束
###如果点选复选框，则添加该IP/MAC的on属性

if ($ENV{'QUERY_STRING'} =~/enabled/) {
	my @scaned_line = read_config_file($file);
	if ($enabled_line eq '0') {
		for (my $i=0; $i<@scaned_line ;$i++) {
			my @tmp=split(/,/,$scaned_line[$i]);
			$scaned_line[$i] = "$tmp[0],$tmp[1],$scan_value,,$enabled_value";
		}
	}
	else{
		my @tmp=split(/,/,$scaned_line[$enabled_line-1]);
		$scaned_line[$enabled_line-1] = "$tmp[0],$tmp[1],$scan_value,,$enabled_value";
	}
	save_config_file(\@scaned_line,$file);
}
###如果改变端口，则如下操作
if ($ENV{'QUERY_STRING'} =~/changeiface/) {
	my @scaned_line = read_config_file($file);
	for (my $i=0;$i<@scaned_line ;$i++) {
		$scaned_line[$i] =~s/br0/$changed/;
		$scaned_line[$i] =~s/br1/$changed/;
	}
	save_config_file(\@scaned_line,$file);
}
###保存选中的
if ($ENV{'QUERY_STRING'} =~/save/) {
	my @scaned_line = read_config_file($file);
	my @data_line = read_config_file($data_file);
	foreach my $line (@scaned_line) {
		if ($line =~/,on$/) {
			push (@data_line,$line);
		}
	}
	save_config_file(\@data_line,$data_file);
	if (@scaned_line >= 1) {
		system("touch $needreload");
	}
}
&copy_down();