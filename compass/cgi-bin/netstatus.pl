#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 网络状态页面头文件
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================

require '/var/efw/header.pl';

$in_str;#存放传入字节
$out_str;#存放传出字节
%up_eth;
my %console;
readhash("/var/efw/console/settings",\%console);
my $interface_number = `ifconfig |grep eth |wc -l`;
my $enabled = "on";
if($console{"ENABLED"} eq "off" || $console{"ENABLED_NUMBER"} > $interface_number ){
	$enabled = "off";
}
my $interface_i = 0;
sub trans_bytes($)
{
	my $str = shift;
	$str=~ s/i//g;
	return $str;
}

sub trans_int($)
{
	my $str = shift;
	my @arry = split("\\s",$str);
	my $new_str = $arry[0]+0;#用于存放换算完进率后的值
	$arry[1] =~ s/\s//g;#去掉不必要的空格字符串
	#定义不同的单位的进率
	my %unit = (
		'mib' => 1000000,
		'kib' => 1000,
		'gib' => 1000000000,
		'b' => 1
		);
	foreach my $units(keys %unit)
	{
		if($units  eq  lc($arry[1]))
		{
			$new_str = $unit{$units}*$arry[0]/1000000;
		}
	}
	return $new_str;
}

sub get_red_interface($)
{
	my $red_class = shift;
	my @red_interface;
	my $dir = "/var/efw/uplinks/";
	opendir (DIR, $dir) or die  _("can’t open the directory!");
	@red_interface = readdir DIR;
	closedir(DIR);
	my $red_title = _('红色接口');
	my $red_RX;#红口总上传流量
	my $red_TX;#红口总接收流量
	my $sub_str;
	my $types = "reds";
	my $all_red_in;
	my $all_red_out;
	my $i = 0;
	foreach my $red(@red_interface)
	{
		if($dir !~ /^\./ && -f $dir."/".$red."/settings")
		{
			 my $settings = $dir."/".$red."/settings";
			 my %conf_hash = ();
			 readhash($settings,\%conf_hash);
			 my $eth = $conf_hash{'RED_DEV'};
			 my $type = $conf_hash{'RED_TYPE'};
			 my $cmd = `ifconfig $eth`;
			 if($eth && $cmd =~ /.*inet +addr:(\d+\.\d+\.\d+\.\d+).*Mask:(\d+\.\d+\.\d+\.\d+)[\w\W]+RX +bytes:(\d+ +)\((.*)\).*TX +bytes:(\d+ +)\((.*)\)/)
			{
				my $ip   = $1;
				my $mask = $2;
				$in_str  = $3;
				$out_str = $5;
				my $RX   = $4;
				my $TX   = $6;
				$red_TX += trans_int($TX);
				$red_RX += trans_int($RX);
				my $temp_RX= trans_bytes($RX);
				my $temp_TX= trans_bytes($TX);
				$mask = &ipmask_dec2bin($mask);
				my $img_id = "img".$interface_i;
				my $tr_id = "tr".$interface_i;
				$sub_str .= "<tr $red_class id='$img_id'  style='cursor:pointer;' onclick='show_detail(\"$eth\")'  onmouseover=\"odd_over('$img_id')\"   onmouseout=\"odd_out('$img_id')\" ><td>$eth ( $type )</td><td>$ip/$mask</td><td class='RX'  name='$in_str' >$temp_RX</td><td class='TX'  name='$out_str'>$temp_TX</td><td  class='speed_in' >0b/s</td><td class='speed_out'>0b/s</td></tr>";
				$up_eth{$eth} = $eth;
			}
		}
		$i++;
		$interface_i++;
	}
	print $sub_str;
}


sub get_interface_detail($)
{
	my $type = shift;
	#硬件地址命令
	my $mac_cmd  = `ifconfig $type | grep HWaddr`;
	if($mac_cmd =~ /([a-zA-Z0-9]+\:[a-zA-Z0-9]+\:[a-zA-Z0-9]+\:[a-zA-Z0-9]+\:[a-zA-Z0-9]+\:[a-zA-Z0-9]+)/)
	{
		$mac_cmd = $1;
	}else{
		$mac_cmd = _("未知");
	}
	
	#连接状态命令
	my $current_state_cmd      = `sudo ethtool $type | grep "Link detected"`;
	if($current_state_cmd =~ /Link detected: ([a-zA-Z]+)/ )
	{
		if($1 eq "no")
		{
			$current_state_cmd = _("未连接");
		}elsif($1 eq "yes")
		{
			$current_state_cmd = _("已连接");
		}else{
			$current_state_cmd = _(" 未知");
		}
	}else{
		$current_state_cmd = _(" 未知");
	}
	
	
	#链路层协议状态命令
	my $link_state_cmd         = `ip link | grep $type`;
	if(($link_state_cmd =~ /(,UP,)/) || ($link_state_cmd =~ /(<UP,)/) || ($link_state_cmd =~ /(,UP>)/))
	{
		$link_state_cmd = _("启用");
	}else{
		$link_state_cmd = _("关闭");
	}
	
	
	#连接速率命令
	my $connect_cmd            = `sudo ethtool $type | grep Speed`;
	if(($connect_cmd =~ /(10Mb)/) || ($connect_cmd =~ /(100Mb)/) || ($connect_cmd =~ /(1000Mb)/))
	{
		$connect_cmd = $1."/s";
	}else{
		$connect_cmd = _("未知");
	}
	
	
	
	#连接类型（全/半双工）命令
	my $connect_type           = `sudo ethtool $type | grep Duplex`;
	if(($connect_type =~ /(Full)/) || ($connect_type =~ /(Half)/))
	{
		$connect_type = $1;
	}else{
		$connect_type = _("未知");
	}
	
	#连接介质命令
	my $connect_port_cmd       = `sudo ethtool $type | grep Port`;
	if(($connect_port_cmd =~ /(Twisted Pair)/) || ($connect_port_cmd =~ /(Twisted Pair)/))
	{
		if($1 eq "Twisted Pair")
		{
			$connect_port_cmd = _("双绞线");
		}else{
			$connect_port_cmd = _("光纤");
		}
	}else{
			$connect_port_cmd = _("未知");
	}
	
	
	#自协商命令
	my $auto_cmd = `sudo ethtool $type | grep Auto-negotiation`;
	if( ($auto_cmd  =~ /(on)/) || ($auto_cmd  =~ /(off)/))
	{
		$auto_cmd = $1;
	}else{
		$auto_cmd = _(" 未知");
	}
	

	my $str = '<table cellpadding="0" cellspacing="0" width="100%" style="border-left:1px solid #999;"><tr class="env_thin"><td class="add-div-table">'._("MAC地址").'</td><td class="add-div-table">'._("连接状态").'</td><td class="add-div-table">'._("链路层协议状态").'</td><td class="add-div-table">'._("连接速率").'</td><td class="add-div-table">'._("连接类型").'</td><td class="add-div-table">'._("连接介质").'</td><td class="add-div-table">'._("自协商").'</td></tr><tr class="odd_thin"><td>'.$mac_cmd.'</td><td>'.$current_state_cmd.'</td><td>'.$link_state_cmd.'</td><td>'.$connect_cmd.'</td><td>'.$connect_type.'</td><td>'.$connect_port_cmd.'</td><td>'.$auto_cmd.'</td></tr></table>';
	return $str;
}



#获得接口信息
sub get_interface($$$$)
{
	my $title = shift;
	my $interface = shift;
	my $class = shift;
	my $type = shift;
	my $cmd = `ifconfig $interface`;
	if($cmd =~ /.*inet +addr:(\d+\.\d+\.\d+\.\d+).*Mask:(\d+\.\d+\.\d+\.\d+)[\w\W]+RX +bytes:(\d+ +)\((.*)\).*TX +bytes:(\d+ +)\((.*)\)/)
	{
		my $ip   = $1;
		my $mask = $2;
		$in_str  = $3;
		$out_str = $5;
		my $RX   = $4;
		my $TX   = $6;
		$mask = &ipmask_dec2bin($mask);
		my $temp_RX= trans_bytes($RX);
		my $temp_TX= trans_bytes($TX);
		my $img_id = "img".$interface;
		my $tr_id = "tr".$interface;
		my $js = "";

		if(($interface !~ /ipsec/) && ($interface !~ /ppp/) && ($interface !~ /tap/))
		{
			$js = "style='cursor:pointer;' onclick='show_detail(\"$interface\")'  onmouseover='odd_over(\"$img_id\")'   onmouseout='odd_out(\"$img_id\")'";
		}
		my $str = "<tr $class id='$img_id'  $js ><td >$interface $title</td><td>$ip/$mask</td><td class='RX'  name='$in_str' >$temp_RX</td><td class='TX'  name='$out_str'>$temp_TX</td><td class='speed_in'>0b/s</td><td class='speed_out' >0b/s</td></tr>";
		$up_eth{$interface} = $interface;
		print $str;	
	}elsif($cmd =~ /.*RX +bytes:(\d+ +)\((.*)\).*TX +bytes:(\d+ +)\((.*)\)/)
	{
		$in_str  = $1;
		$out_str = $3;
		my $RX   = $2;
		my $TX   = $4;
		my $temp_RX= trans_bytes($RX);
		my $temp_TX= trans_bytes($TX);
		my $js = "";
		my $img_id = "img".$interface;
		my $tr_id = "tr".$interface;
		if(($interface !~ /ipsec/) && ($interface !~ /ppp/) && ($interface !~ /tap/))
		{
			$js = "style='cursor:pointer;' onclick='show_detail(\"$interface\")'  onmouseover='odd_over(\"$img_id\")'   onmouseout='odd_out(\"$img_id\")'";
		}
		my $str = "";

		$str = "<tr $class id='$img_id' $js><td >$interface $title</td><td>&nbsp;</td><td class='RX'  name='$in_str' >$temp_RX</td><td class='TX'  name='$out_str'>$temp_TX</td><td class='speed_in'>0b/s</td><td class='speed_out'>0b/s</td></tr>";
		$up_eth{$interface} = $interface;
		print $str;
	}
}

#获取LAN口、DMZ口的接口信息
sub get_interface_sub($$$)
{
	my $interface = shift;
	my $type = shift;
	my $class = shift;
	my $cmd = `cat /var/efw/ethernet/$interface`;
	my @arry_eth = split("\\n",$cmd);
	my $i = 0;
	my $eth_num = `ls -l  /sys/class/net/|grep "eth*"|wc -l`;
	foreach my $eth(@arry_eth)
	{
		if($enabled eq 'on' && $eth eq "eth0"){
			next;
		}
		my $cmd_sub = `ifconfig $eth`;
		if($cmd_sub =~ /.*RX +bytes:(\d+ +)\((.*)\).*TX +bytes:(\d+ +)\((.*)\)/)
		{
			my $RX     = $2;
			my $TX     = $4;
			$in_str    = $1;
			$out_str   = $3;
			my $temp_RX= trans_bytes($RX);
			my $temp_TX= trans_bytes($TX);
			my $img_id = "img".$interface_i;
			my $tr_id = "tr".$interface_i;
			my $str = "<tr $class   style='cursor:pointer;'  id='$img_id' onclick='show_detail(\"$eth\")'  onmouseover='odd_over(\"$img_id\")'   onmouseout='odd_out(\"$img_id\")' ><td>$eth </td><td>&nbsp;</td><td class='RX'  name='$in_str' >$temp_RX</td><td class='TX'  name='$out_str'>$temp_TX</td><td class='speed_in'>0b/s</td><td class='speed_out'>0b/s</td>
</tr>";
			$up_eth{$eth} = $eth;
			print $str;
		
		}
		$i++;
		$interface_i++;
		
	}
	
}


sub display()
{
printf <<END
<table class="ruleslist" cellpadding="0" cellspacing="0" style="margin-top:20px;">
        <tr>
            <td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="15%">%s</td>
			<td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="15%">%s</td>
		</tr>
END
    , _('Interface')
    , _('IP/Mask')
    , _('RX bytes')
    , _('TX bytes')
	, _('In rate')
    , _('Out rate')
    ;
}




#### 将十进制表示的 IP/子网掩码转换成二进制形式
sub ipmask_dec2bin {
    my $prefix = "";
    my $result;
    map { 
		$result .= &dectobin($_); 
    } 
	split (/\./,shift);
	my @temp = split("",$result);
	my $count = 0;
	foreach my $char(@temp)
	{
		if($char eq "1")
		{
			$count++;
		}
	}
	return $count;
}


sub dectobin {
    substr(unpack("B32",pack("N",shift)) , -8);
}

sub get_all_eth()
{
	my $temp_cmd = `ip a`;
	my %all_hash;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
		{
			$all_hash{$1} = $1;
		}
	}
	return %all_hash;
}

sub get_more_eth()
{
	my $temp_cmd = `ip a`;
	my @eth_ary;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		
		if(($line =~ /^[0-9]+\: +(ipsec[0-9]+)\:/) || ($line =~ /^[0-9]+\: +(tap[0-9]+)\:/) || ($line =~ /^[0-9]+\: +(ppp[0-9]+)\:/))
		{
			push(@eth_ary,$1);
		}
	}
	return @eth_ary;
}
1;
