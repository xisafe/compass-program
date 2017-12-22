#!/usr/bin/perl
# AUTHOR: 周圆
# COMPANY: great.chinark
# CREATED: 2012/03/13

require '/var/efw/header.pl';
my $setting = '/var/efw/stp/setting';
my %config = ();
my %par = ();
my %zone =(
			'GREEN_ENABLED' => _('GREEN')."区",
			'ORANGE_ENABLED' => _('ORANGE')."区",
			'BLUE_ENABLED' => _('BLUE')."区"
);

my %zone_hash =(
			'GREEN_ENABLED' => 'br0',
			'ORANGE_ENABLED' => 'br1',
			'BLUE_ENABLED' => 'br2'
);

my %enabled=(
			'on' => '开启',
			'off' => '关闭'
);

sub save()
{
	my $zone = $par{'ACTION'};#标记当前选中的是那个按钮
	if($zone)
	{
		my $value = $par{'ENABLED'};
		if($value eq 'off')
		{
			$config{$zone} = 'on';
		}else{
			$config{$zone} = 'off';
		}
		&writehash($setting, \%config);
		$notemessage = $zone{$zone}."已经成功".$enabled{$config{$zone}}."最小生成树";
		my $temp = uc($config{$zone});
		`sudo /usr/local/bin/stp_$zone_hash{$zone} $temp`;
	}
}

sub config()
{
	if(-e $setting)
	{
		&readhash($setting, \%config);
	}else{
		$config{'GREEN_ENABLED'} = 'off';
		$config{'ORANGE_ENABLED'} = 'off';
		$config{'BLUE_ENABLED'} = 'off';
	}
}

#获取LAN、WIFI色、DMZ口的接口信息
sub get_interface($)
{
	my $interface = shift;
	my $cmd = `cat /var/efw/ethernet/$interface`;
	return $cmd;
}

sub show_eth($$$)
{
	my $name = shift;
	my $key = shift;
	my $eth = shift;
	
		printf <<EOF
		<tr class="env">
			<td class="add-div-type">$name</td>
			<td width='100px' >$eth</td>
			<td>
				<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}' >
				<input type="image" src="/images/switch-%s.png"  title="%s"/>
				<input type='hidden' name='ACTION' value='$key' />
				<input type="hidden" name="ENABLED" value="%s" />
				</form></td>
	    </tr>
EOF
,$config{$key}
,$config{$key} eq 'on'?'点击此按钮关闭最小生成树':'点击此按钮开启最小生成树'
,$config{$key}
;
	
}

sub show_config()
{
	#获取LAN口信息
	my $green = get_interface('br0');
	#获取DMZ口信息
	my $orange = get_interface('br1');
	#获取WIFI口信息
	my $blue = get_interface('br2');

	&openbox('100%', 'left', _('最小生成树配置'));

	print "<table>";
	
	if($green=~/eth/)
	{
		show_eth(_('GREEN')."区域",'GREEN_ENABLED',$green);
	}
	if($orange=~/eth/)
	{
		show_eth(_('ORANGE')."区域",'ORANGE_ENABLED',$orange);
	}
	
	if($blue=~/eth/)
	{
		show_eth(_('BLUE')."区域",'BLUE_ENABLED',$blue);
	}
	print "<tr class='table-footer' ><td colspan='3'></td></tr></table>";
	&closebox();

}


&getcgihash(\%par);
showhttpheaders();
my $extraheader  = '';
&config();
&save();
&openpage(_('最小生成树'), 1, $extraheader);
&openbigbox($errormessage, $warnmessage, $notemessage);
&show_config();
&closepage();