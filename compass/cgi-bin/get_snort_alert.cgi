#!/usr/bin/perl -w
use CGI();
use URI::Escape;

my $log="/var/efw/risk/evaluation/risk_evaluation.log";
my $attfile = "/var/efw/risk/warning/attacktype";
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
&validateUser();
sub read_config_file($) {
    my @lines;
	my $file=shift;
	if (-e $file) {
		open (FILE, "$file");
		foreach my $line (<FILE>) {
			chomp($line);
			$line =~ s/[\r\n]//g;
			push(@lines, $line);
		}
		close (FILE);
	}
    return @lines;
}
my @lines = read_config_file($log);
my @attlines = read_config_file($attfile);
my $str="";
my $num = @lines;
if (!$num) { 
	print "no message";
}
else{
	for (my $i=0;$i<2 ;$i++) {
		my @tmp = split(/,/,$lines[$i]);
		my ($attack,$trans) = split(/,/,$attlines[$tmp[4]]);
		my $num=0;
		if (!$str) {
			$str = "<p>检测到来自".$tmp[2]."的".$attack."攻击.详情请看风险告警日志审计.</p>";
			$num = 1;
		}
		elsif ($str !~ $tmp[2]) {
			$str = $str."<p>检测到来自".$tmp[2]."的".$attack."攻击.如需关闭提示，请在高级设置中关闭界面告警。</p>";
		}
		if ($num == 1) {
			$str .= "<p>如需关闭提示，请在高级设置中关闭界面告警.</p>";
		}
	}
	print $str;
}

