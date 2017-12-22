#! /usr/bin/perl

my $event=shift(@ARGV);
if($event =~ /\.gz$/ || $event =~/efw\/openvpn/){
   unlink $event;
}
elsif($event eq "all_logs"){
	`sh /home/httpd/cgi-bin/delete_logs.sh`;
}
else{
   system("cat /dev/null > $event"); 
   system("/usr/local/bin/restartsyslog --force >>/dev/NULL");
}

