#!/usr/bin/perl

use CGI qw(:standard);
use Encode;
require '/var/efw/header.pl';
&validateUser();
my $getsn = "sudo /usr/local/bin/getcerthexsn.py";
my $status = 1;
my $sn = "";

&uploads();

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";
print '{"status": "'.$status.'","sn":"'.$sn.'"}';


sub uploads(){
	my $filename = "/tmp/temp.pem";
	my $file_length = 0;
	my $cgi = new CGI; 
	my $upload_filehandle = $cgi->param('cert_file');
	my $upload_filename = $upload_filehandle;
	my @splited_filenames = split(/\./, $upload_filename);
	foreach my $splited_filename (@splited_filenames)
	{
		$file_length++;
	}
	if($file_length == 0)
	{
		$status = '请选择一个pem,crt,cer,p12文件再上传！';
	} else {
		$file_length--;
		if ($splited_filenames[$file_length] eq 'pem' || $splited_filenames[$file_length] eq 'crt' || $splited_filenames[$file_length] eq 'cer' || $splited_filenames[$file_length] eq 'p12')
		{	
			open ( UPLOADFILE, ">$filename" ) or $status = "无法打开文件";
			binmode UPLOADFILE;
			while ( <$upload_filehandle> )
			{
				print UPLOADFILE;
			}
			close UPLOADFILE;
			$sn = `$getsn $filename`;
			chomp($sn);
		} else {
			$status = '只支持处理pem,crt,cer,p12文件！请选择一个pem,crt,cer,p12文件再上传！';
		}
	}
}