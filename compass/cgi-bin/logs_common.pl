#!/usr/bin/perl
require "/var/efw/header.pl";
require "/home/httpd/cgi-bin/list_panel_opt.pl";
sub change_time($){
	my $time = shift;
	my %month=(
	   "Jan " => " 01",
	   "Feb " => " 02",
	   "Mar " => " 03",
	   "Apr " => " 04",
	   "May " => " 05",
	   "Jun " => " 06",
	   "Jul " => " 07",
	   "Aug " => " 08",
	   "Sep " => " 09",
	   "Oct " => " 10",
	   "Nov " => " 11",
	   "Dec " => " 12"
	);
	$time =~ /^(... )(.*) ..:..:../;
	my $mon = $1;
	my $dat = $2;
	$time =~s /^$mon/$month{$mon}-/;
	if ($dat < 10){
		$dat = "0".$dat;
		$dat =~s /\s//g;
		$time =~s/(.*)-.* (..:..:..)/$1-$dat $2/;
	}
	return $time;
}

sub down_file(){
	my $file = shift;
	my $action = shift;
	my $date = shift;
	my $log_name = shift;
	my @fileholder = ();
	my $errormessage = '暂无相关日志信息';
	if ($action eq 'download') {
		if( -s "$file"){			
			if($file =~ /\.gz/){
				my $str = `zcat '$file'`;
				if($str eq ''){
					return $errormessage;
				}
				else{
					@fileholder = split("\n", $str);
					# 保证格式一致，末尾都有换行符
					foreach(@fileholder) {
						$_ .= "\n";
					}
				}
			}else{
				open(DLFILE, "<$file") || Error('open', "$file");
				@fileholder = <DLFILE>;
				close (DLFILE) || Error ('close', "$file");
			}
			
			if($log_name eq '用户审计') {
			    @fileholder = &screen_file(@fileholder); 
			}
			@fileholder = &addLogDate($date, \@fileholder);



			my $log_message = "导出了".$date."的".$log_name."日志";
			&user_log($log_message);
			print "Content-Type:application/x-download\n";  
			print "Content-Disposition:attachment;filename='$log_name-$date'\n\n";
			print &log_encrypt('en',$log_name,join("",@fileholder));
			exit;
		}
		else{
			return $errormessage;
		}
	}
	
}

#用于根据不同用户权限，筛选不同的日志内容用于下载
sub screen_file() {
	my @cur_user = &getCurUser();
	my $cur_user_type = &get_user_type($cur_user[0]);
	my $extra = "";

	if($cur_user_type eq "0") {
		$extra = "admin";
	}elsif($cur_user_type eq "1") {
		$extra = "safeauth";
	}elsif($cur_user_type eq "3") {
		$extra = "logerauth";
	}else {
		$extra = $cur_user[0];
		# if($cur_user[0] eq "admin") {
		# 	$extra = "admin";
		# 	$cur_user_type = "0";
		# }elsif($cur_user[0] eq "safeauth") {
		# 	$extra = "safeauth";
		# 	$cur_user_type = "1";
		# }else {
		# 	$extra = "logerauth";
		# 	$cur_user_type = "3";
		# }
	}
	my @newFileholder = ();
	&debug2file("aaa");
	foreach(@_) {
		$_ =~ /user[^-]+-(.+):.*=level:\s([0-9])/;
		&debug2file("line:$_ \$1:$1 \$2$2 type:$cur_user_type extra:$extra");
		if($cur_user_type eq $2 && $extra eq $1){
			push (@newFileholder, $_);
		}
	}
	return @newFileholder;
}
sub addLogDate() {
	my $date = shift;
	$date =~ s/-//g;
	my $arr = shift;
	my @arr = @$arr;
	my @newFileholder = ();
	foreach(@arr) {
		# $_ = s/\n//;
		# $_ = s/\r//;
		$_ = '####'.$date.'#### '.$_;
		push (@newFileholder, $_);
	}
	return @newFileholder;
	
}

sub debug2file($$){ 
        my $str = shift; 
        my $filepath = shift; 
        if (!$filepath){ $filepath = '/var/efw/debug.log2';} 
        open(FILE, ">>$filepath") or die "Cant append to $filepath: $!"; 
                print FILE $str ; 
                print FILE "\n"; 
        close(FILE); 
} 




1;
