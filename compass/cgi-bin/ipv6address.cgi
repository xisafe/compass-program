#!/usr/bin/perl

#file:devices.cgi
#author:zhangzheng


require '/var/efw/header.pl';
my $settingfile = "/var/efw/ipv6/addr/settings";
my $br0="/var/efw/ethernet/br0";
my $br1="/var/efw/ethernet/br1";
my $extraheader="";
my $errormessage="";
my %ipv6_all;
my $ipv6br0 = `sh /usr/local/bin/get_ipv6_addr.sh br0`;
my $ipv6br1 = `sh /usr/local/bin/get_ipv6_addr.sh br1`;

my $eth_num = `ifconfig|grep -E "^eth[0-9]+[^:^\.]"|wc -l`;
sub other_ethernet(){
	my $green = `cat $br0`;
	my $orange = `cat $br1`;
	my @other;
	for (my $i=0;$i<$eth_num ;$i++) {
		my $eth = "eth".$i;
		if ($green !~ $eth && $orange !~ $eth) {
			push (@other,$eth);
		}
	}
	return @other;
}
my %ethernet=();
for (my $num=0;$num<30 ;$num++) {
	my $n = $num+1;
	$ethernet{'eth'.$num} = "接口$n";
}
if(! -e "/var/efw/ipv6/addr"){
	system("mkdir -p /var/efw/ipv6/addr");
}
sub save(){
	my $action = $par{"ACTION"};
	if ($action eq "save") {
		delete $par{'__CGI__'};
		$par{'br0'} =~s/[\n\r]/&/g;
		$par{'br0'} =~s/&&/,/g;
		$par{'br1'} =~s/[\n\r]/&/g;
		$par{'br1'} =~s/&&/,/g;
		foreach my $eth (other_ethernet()) {
			$par{$eth} =~s/[\n\r]/&/g;
			$par{$eth} =~s/&&/,/g;
		}
		my @delete,@add;
		my %back,%new;
		if (-e $settingfile) {
			readhash($settingfile,\%init);
		}
		 writehash($settingfile,\%par);
		`sudo fmodify $settingfile`;
		 $notemessage = "IPV6地址配置成功！";
		 ####将删除的地址执行删除命令
		 foreach my $key (keys %init) {
			 foreach my $ipv6s (split(/,/,$init{$key})) {
				 system("sudo /usr/local/bin/ipv6_addr.py del $ipv6s $key");
			 }
		 }
		 ####将新增的地址执行新添命令
		 foreach my $key (keys %par) {
			 foreach my $ipv6s (split(/,/,$par{$key})) {
				 system("sudo /usr/local/bin/ipv6_addr.py add $ipv6s $key");
			 }
		 }
	}
}

sub display_setting(){
	my $class = "class='env'";
	my $i = 0;
	my %br0s,%br1s;
	foreach my $elem (split(/,/,$par{'br0'})) {
		$br0s{$elem} = 1;
	}
	foreach my $elem (split(/\s/,$ipv6br0)) {
		if (!$br0s{$elem}) {
			$br0init .= "<p>$elem</p>";
		}
	}
	$br0init =~s/\|+$//;
	foreach my $elem (split(/,/,$par{'br1'})) {
		$br1s{$elem} = 1;
	}
	foreach my $elem (split(/\s/,$ipv6br1)) {
		if (!$br1s{$elem}) {
			$br1init .= "<p>$elem</p>";
		}
	}
	$br1init =~s/\|+$//;
	$par{'br0'} =~s/,/\n/g;
	$par{'br1'} =~s/,/\n/g;
	my $greeneth  = `cat /var/efw/ethernet/br0`;
	my $orangeeth = `cat /var/efw/ethernet/br1`;
	my $greens,$oranges;
	foreach my $elem (split(/\n/,$greeneth)) {
		$elem = $ethernet{$elem};
		$greens = $greens."$elem,";
	}
	foreach my $elem (split(/\n/,$orangeeth)) {
		$elem = $ethernet{$elem};
		$oranges = $oranges."$elem,";
	}
	$greens =~s/,$//;
	$oranges =~s/,$//;
	if ($br0init) {
		$br0init .= "(自动IPV6地址)";
	}
	if ($br1init) {
		$br1init .= "(自动IPV6地址)";
	}
	printf <<EOF
	<form method='post' action='$self' enctype='multipart/form-data'>
	<input type='hidden' name='ACTION' value='save' />
	<table cellpadding="0" cellspacing="0" width="100%" border='0' >
	<tr class = "odd">
		<td width="20%" class="add-div-type">%s区域 ($greens)</td>
		<td width="25%"><div style="display: table-row;">请输入ipv6地址(每行一个)</div><textarea style="width:220px;height:50px;" name="br0">$par{'br0'}</textarea></td>
		<td>$br0init</td>
	</tr>
EOF
,_('GREEN')
;   
	if (&orange_used) {
		print "<tr class = 'env'>";
		printf <<EOF 
		<td class='add-div-type'>%s区域 ($oranges)</td>
EOF
,_('ORANGE')
;
		print "<td><div style='display: table-row;'>请输入ipv6地址(每行一个)</div><textarea style='width:220px;height:50px;' name='br1'>$par{'br1'}</textarea></td>";
		print "<td>$br1init</td></tr>";
		$i = 1;
	}
	foreach my $eth (other_ethernet()) {
		if ($i % 2) {
			$class = "class='odd'";
		}
		else{
			$class = "class='env'";
		}
		my %eths;
		my $ethinit;
		$ipv6_all{$eth} = `sh /usr/local/bin/get_ipv6_addr.sh $eth`;
		foreach my $elem (split(/,/,$par{$eth})) {
			$eths{$elem} = 1;
		}
		foreach my $elem (split(/\s/,$ipv6_all{$eth})) {
			if (!$eths{$elem}) {
				$ethinit .= "<p>$elem</p>";
			}
		}
		$ethinit =~s/\|+$//;
		$par{$eth} =~s/,/\n/g;
		if ($ethinit) {
			$ethinit .= "(自动IPV6地址)";
		}
	printf <<EOF
	<tr $class>
		<td class="add-div-type">$ethernet{$eth}</td>
		<td><div style="display: table-row;">请输入ipv6地址(每行一个)</div><textarea style="width:220px;height:50px;" name="$eth">$par{$eth}</textarea></td>
		<td>$ethinit</td>
	</tr>
EOF
;
	$i++;
	}
	printf <<EOF
	<tr class="table-footer">
		<td colspan="3"><input id="savebutton" class='submitbutton net_button' type='submit' name='ACTION_RESTART' value='保存' /></td>
	</tr>
	</table>
	</form>
EOF
;
}
$extraheader .="<script type='text/javascript' src='/include/ip_mac_binding.js'></script><script type='text/javascript' src='/include/warningsetting.js'></script><style type='text/css'>\@import url(/include/ip_mac_binding.css);</style>";
$extraheader .= "<script type='text/javascript' src='/include/ESONCalendar.js'></script><link rel='stylesheet' href='/include/datepicker/css/datepicker.css' type='text/css' />";
&getcgihash(\%par);
&showhttpheaders();


&openpage(_('地址配置'), 1, $extraheader);

save();
if (-e $settingfile) {
	readhash($settingfile,\%par);
}

foreach my $line(@errormessages){
	$errormessage.=$line."<br />";
}
&openbigbox($errormessage, $warnmessage, $notemessage);
openbox('100%', 'left', _('地址配置'));

display_setting();

closebox();
&closebigbox();
&closepage();
