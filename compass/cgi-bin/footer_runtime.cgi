#!/usr/bin/perl
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
require '/var/efw/header.pl';

my $green_class="class='env green bold'";
my $orange_class="class='env orange bold'";
my $red_class="class='env red bold'";
my $host_dir = "hostname";
my $hostname = "";
my $hirel_dir = "/var/efw/hirel/settings";
my $hirel;
my $hirel_enabled = 0;
my %hirel_setting ;
my $logDate = `date "+%Y-%m-%d"`;							
my %par; 
&validateUser();
&getcgihash(\%par);
if ($par{'action'} eq 'get_user_status') {
	my $user = &get_cookie_user('user');
	if ($user eq $par{'val'}) {
		print '0';
		return;
	}else{
		print $user;
		print '1';
	}
	
}
my @cur_user=getCurUser();
my $input_user=$cur_user[0];
if ($input_user eq '') {
	return;
}
my $IP = $ENV{'REMOTE_ADDR'};
sub read_host()
{
	$hostname = `$host_dir`;
	my @temp = split(/\./,$hostname);
	$hostname = $temp[0];
}

sub sys_run_time($)
{
	my $sys_time = shift;
	my @time = split("\\s",$sys_time);
	my $run_time = $time[0];
	my $run_days=int($run_time / 86400);
	my $run_hour=int(($run_time % 86400)/3600);
	my $run_minute=int(($run_time % 3600)/60);
	print $run_days."=";
	print $run_hour."=";
	print $run_minute."=";
}

sub read_timeout()
{
	my $time = 30;
	my %time = ();
	readhash("/var/efw/userinfo/user_config",\%time);
	$time = $time{"TIMEOUT"}+0;
	my %time_out_hash = ();
	my $path = "/var/efw/userinfo/timeout";
	readhash($path,\%time_out_hash);
	
	my $addr = $ENV{'REMOTE_ADDR'};
	$addr =~ s/\./_/g;
	$addr =~ s/\:/_/g;

	my $key = &get_cookie_user('key');
	my $last_time = $time_out_hash{$key};
	
	my $cur_time = `date +%s`;
	my $outtime=$cur_time - $last_time - $time*60;
	my $level;
	my @user_info = read_users_file();
    foreach my $user1(@user_info)
		{    
			my @user_temp = split(",",$user1);
			if($input_user eq @user_temp[0]){
				$level = "=level: ".$user_temp[4];
			}
		}
	if($outtime >= 0)
	{
	    
	    my $logmsg="用户超时退出系统";
		$logmsg = $IP."--".$logmsg;
		system("/usr/bin/logger","-p","local6.notice","-t","userRecord-$input_user","$logmsg","$level","$logDate");  
	}
	print $outtime;
}

my $uptime = `cat /proc/uptime`;
sys_run_time($uptime);
my $cur_time = `date "+%Y-%m-%d %H:%M"`."=";
print "$cur_time";
read_host();
print $hostname."=";
read_timeout();
