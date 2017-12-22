#!/usr/bin/perl
#
#author:lina
#
#date:2016-10-18
#
#require '/var/efw/header.pl';
require '/var/efw/header.pl';
use CGI();
my %par;
my $errormessage = '';
my $serialNumber = `sudo /usr/local/bin/get_devid.py`;
&getcgihash(\%par);
my $ACTION = $par{'ACTION'};
&importClient();
print "Content-type:text/html\r\n\r\n";

print "<!DOCTYPE HTML>";
print '<html>';
print '<head>';
print '<meta charset="utf-8">';
printf <<EOF
	<script type="text/javascript" src="/include/jquery.js"></script>
	<script type="text/javascript" src="/include/client.js"></script>	
	<link rel="stylesheet" type="text/css" href="/include/client.css" />

EOF
;
print '<title>认证中心</title>';
print '</head>';
print '<body>';
printf <<EOF
<script>
	console.log("$ACTION");
	if("$errormessage") {
		alert("$errormessage");
	}
</script>
<form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}' >
	<div class= "importlicence-main">
		<div class="importlicence-header">
			<span>设备授权</span>
		</div>
		<div class="importlicence-number">
			<div class="importlicence-left">
				<span>设备序列号</span>
			</div>
			<div class="importlicence-right">
				<span>$serialNumber</span>
			</div>
		</div>
		
		<div class="importlicence-content">
			<div class="importlicence-left">
				<span>选择授权文件</span>
			</div>
			<div class="importlicence-right">

				<label id="upload_file_tip" title="未选择授权文件">未选择授权文件</label>
				<a href="javascript:;" class="file">浏览
					<input type="file" name="upload_file" id="upload_file">
				</a>
			</div>
		</div>
		<div class="importlicence-submit">
			<input type="hidden" name="ACTION" value="importLicence">
			<input type="submit" value="确定授权">
		</div>
	</div>
</form>
EOF
;

print '</body>';
print '</html>';
sub importClient() {
	my $licence = `sudo /usr/local/bin/check_license.py`;
	$licence =~ s/\n//g;
	$licence =~ s/\r//g;
	if($licence eq '0') {
		print "Location: /index.cgi\r\n\r\n";
	}
    my $cgi = new CGI;
    my $file_name = $cgi->param('upload_file');	

	if ($ACTION eq "importLicence") {
		

		# my $name = $file_name;
		# my $file_path = $upload_dir . $name;

		# if( ($par{'ACTION'} eq "") && $par{'upload_file'} eq ""){
			# &send_status(-1, "对不起，您没有上传文件！"); # return 0; #
			# return "";
		# }
		# if ( &dir_size( $upload_dir ) + $ENV{CONTENT_LENGTH} > MAX_DIR_SIZE ) {
			# &send_status( -1, "对不起，目录已满，文件无法上传" );  # return 0; #
			# return "";
		# }
		# if( -s($file_name) > MAX_FILE_SIZE ){
			# &send_status( -1, "对不起，你的文件大小超过了5M" );  # return 0; #
			# return "";
		# }

		
		my $file_path = `mktemp -p /tmp`;
		chomp($file_path);
		# print $file_path;
		open ( UPLOADFILE, ">$file_path" ) or $errormessage = "对不起，打开写入上传文件失败！";
		binmode UPLOADFILE;
		while ( <$file_name> )
		{
			print UPLOADFILE $_;
		}
		close UPLOADFILE;
		
		my $flag = `sudo /usr/local/bin/import_license.py -f $file_path -t firewall `;
		# system("echo \"sudo /usr/local/bin/import_license.py -f $file_path -t firewall \" >> /var/efw/pt.log");
		# system("rm $file_path -f");
		$flag =~ s/\n//g;
		$flag =~ s/\r//g;
		
		# my @flag = &read_conf_file("/tmp/impotLogResults");
		# my $flag = $flag[0];

		if($flag ne '0') {
			$errormessage = "您导入的授权文件有误，请选择正确的授权文件";
		}else {
			# print $file_path;
			print "Location: /index.cgi\r\n\r\n";
			# print "<script>window.location.href = './index.cgi'</script>";
			
			exit;
		}
		# return 1;}
	}
}


