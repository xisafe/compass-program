#!/usr/bin/perl

    use strict;
    use CGI::Carp qw(fatalsToBrowser);
    use Digest::MD5;
    my $uploaddir = '/var/efw/ip-mac/';
	my $data_file = "/var/efw/ip-mac/arptables";
	my $download_file = '/var/efw/ip-mac/download';
	require '/var/efw/header.pl';
	my $needreload = "/var/efw/ip-mac/needreload";
    my $maxFileSize = 0.5 * 1024 * 1024; # 1/2mb max file size...
    &validateUser();
    use CGI;
    my $IN = new CGI;

    my $file = $IN->param('POSTDATA');
    my $temp_id = $IN->param('temp_id');
    print STDERR "Making dir: $uploaddir/$temp_id \n";

    mkdir("$uploaddir/$temp_id");

    open(WRITEIT, ">$uploaddir/tmp") or die "Cant write to $uploaddir/tmp. Reason: $!";
        print WRITEIT $file;
    close(WRITEIT);

    my $check_size = -s "$uploaddir/tmp";

    print STDERR qq|Main filesize: $check_size  Max Filesize: $maxFileSize \n\n|;

    print $IN->header();

    print qq|{ "success": true }|;

    print STDERR "file has been successfully uploaded... thank you.\n";
  
  
sub write_correct($){
	my $filename = shift;
	my @lines =  read_config_file($data_file);
	my $line;
	my @temp = filter_upload($filename);
	foreach my $elem (@temp) {
		my @temp=split(/,/,$elem);
		$temp[1] =~ s/\s//g;
		$temp[0] =~ s/\s//g;
		if (validmac($temp[1]) && validip($temp[0]))
		{
			if(!filter_repeat($temp[0],$data_file)){
				if ($elem =~ /br/) {
					push(@lines,$elem);					
				}
				else{
					$line = "$temp[0],$temp[1],br0,,on";
               		push(@lines,$line);
				}		

			}
		}
	}	
	save_config_file(\@lines,$data_file);
	system("touch $needreload");
	system("rm $uploaddir/tmp")
	&copy_down();
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
	open(FILE3,">$download_file");
	foreach my $line (read_config_file($data_file)) {
		my @temp = split(/,/,$line);
		print FILE3 "$temp[0],$temp[1]\n";
	}		
	close(FILE3);
	`sudo fmodify $download_file`;
}


sub filter_upload($)
{
	my $file  = shift;
	my @lines = read_config_file($file);
	my @temp;
	my %exist;
	foreach my $line(@lines)
	{
		my @temp_new = split(",",$line);
		if ($exist{$temp_new[0]}){
			next;
		}
		else{
			push(@temp,$line);
			$exist{$temp_new[0]} = 1;
		}
	}
	return @temp;
}

###消除数组重复数据
sub filter_repeat($$)
{
	my $temp_line = shift;
	my $file = shift;
	my @lines =  read_config_file($file);
	my $key =0;
	foreach my $line(@lines)
	{
		if($line =~ /^$temp_line/)
		{
			$key ++;
		}
	}
	return $key;
}
write_correct("/var/efw/ip-mac/tmp");
