#!/usr/bin/perl

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my %par ;
&getcgihash(\%par);

my $key1 = $par{'key1'};
my $key2 = $par{'key2'};
my $input_user = $par{'name'};

my $return_num;
my $return_str = " ";
my @register_key = split(/\n/, $key2);

foreach my $key(@register_key) {
	my @line;
	@line = split(/,/, $key);
	my $a;
	my $str;
	$a = hex("0x".substr($line[0], 6, 2)) * 2;
	$str = substr($line[0], 10, $a);

	my $return_num = system("sudo /usr/bin/BioneVerify $str $key1");

	if ($return_num > 90) {
		my $rand = &random_str(16);
		set_cookie($input_user, $rand);
		write_time($input_user, $rand);
		$return_str = "ok";
		return;
	}
}
if ($return_num < 90) {
	$return_str = "wrong";
	print "$return_str";

}

# 生成随机数
sub random_str($) {
	my $len = shift;
	my $str;
	my @W = ('0'..
		'9', 'a'..
		'z', 'A'..
		'Z');
	my $i = 0;
	while ($i++ < $len) {
		$str .= $W[rand(@W)];
	}
	return $str;
}

sub set_cookie($$)
{
		my $account = shift;
		my $rand = shift;
		my $addr = $ENV{'REMOTE_ADDR'};
		$addr =~ s/\./_/g;
		$addr =~ s/\:/_/g;
		my %user_settings;
		readhash( "/var/efw/userinfo/user_config", \%user_settings );
		$time = ($user_settings{'TIMEOUT'} + 1) * 60;
		$timeout = gmtime(time()+$time)." GMT";

		my $cookiepath = "/";
		# my $cachevalue = $account;
		my $key = &get_aes_key();
		$cipher = Crypt::CBC->new(
				-key    => $key,
				-cipher => "Crypt::OpenSSL::AES"
		);
		my $cookie = $addr."_".$account."_".$rand;
		my $encrypted = $cipher->encrypt($cookie);
		my $cachevalue = encode_base64($encrypted);
		$cachevalue =~ s/\n//g;

		# my $cachevalue = &forMd5($account);
		
		print "ee11cbb19052e40b07aac0ca060c23ee=$cachevalue; expires=$timeout; path=$cookiepath;";
}  

sub write_time($$)
{
	my $input_user = shift;
	my $rand = shift;
	my %time_out_hash = ();
	my $path = "/var/efw/userinfo/timeout";
	readhash($path,\%time_out_hash);
	my $addr = $ENV{'REMOTE_ADDR'};
	$addr =~ s/\./_/g;
	$addr =~ s/\:/_/g;

	my $key = $addr."_".$input_user."_".$rand;
	$time_out_hash{$key} = `date +%s`;
	chomp $time_out_hash{$key};
	writehash($path,\%time_out_hash);
}