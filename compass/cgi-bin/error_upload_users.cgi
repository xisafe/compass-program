#!/usr/bin/perl

require '/var/efw/header.pl';

my $conffile =  '/var/efw/openvpn/error_upload_users';
my $errorreadflag = '/var/efw/openvpn/errorreadflag';
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;
&validateUser();
if ( -f $systemconfig ) {
   &readhash( "$systemconfig", \%system_settings );
}

print <<EOF
Pragma: no-cache
Cache-control: no-cache
Connection: close
Content-type: text/html

<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
		<link rel="shortcut icon" href="/images/shortcut.ico" >
        <title>$system_settings{'SYSTEM_TITLE'}</title>
		<link rel='stylesheet' type='text/css' href='/include/main.css'>
		<link rel='stylesheet' type='text/css' href='/include/content.css'>
	</head>
	
	<body style="overflow-y:scroll;background-color:#F0F8FF">
	<br />
	<br />
	<br />
	<center><font color="black" size="5px"><b>导入用户失败统计信息</b></font></center>
	<br />
	<table class="ruleslist" style="width:90%">
		<tbody>
			<tr>
				<td width="5%" class="boldbase">序号</td>
				<td width="10%" class="boldbase">用户名</td>
				<td width="85%" class="boldbase">失败信息</td>
			</tr>
EOF
;
	my $length = 0;
	my @config = read_conf_file($conffile);
	$length = @config;
	if($length > 0){
		my $i = 0;
		for($i = 0; $i < $length; $i++){
			my @temp = split(/,/, $config[$i]);
			my $username = $temp[0];
			my $description = $temp[1];
			my $client_addr = $temp[2];
			my $tr_class = "";
			if ($i % 2) {
				$tr_class = "odd";
			} else {
				$tr_class = "env";
			}
			printf <<EOF
			<tr class="$tr_class">
				<td width="%" class="">$i</td>
				<td width="%" class="">$username</td>
				<td width="%" class="">$description</td>
			</tr>
EOF
			;
		}
	}else{
		no_tr(3,_('Current no content'));
	}

print <<EOF
			<tr class="table-footer">
				<td colspan="3"></td>
			</tr>
		</tbody>
	</table>
	<br />
	<br />
  </body>
</html>
EOF
;

`rm $errorreadflag`;