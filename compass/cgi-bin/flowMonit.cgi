
#��ȡ��������ӿ�
require '/var/efw/header.pl';
&validateUser();
sub get_eth()
{
	my @all_hash;
	my $green  = `cat /var/efw/ethernet/br0`;
	my $orange = `cat /var/efw/ethernet/br1`;
	my $blue   = `cat /var/efw/ethernet/br2`;
	
	if($green)
	{
		my @green_eth = split("\\n",$green);
		foreach my $eth(@green_eth)
		{
			push(@all_hash,$eth);
		}
	}
	
	if($orange)
	{
		my @orange_eth = split("\\n",$orange);
		foreach my $eth(@orange_eth)
		{
			push(@all_hash,$eth);
		}
	}
	
	if($blue)
	{
		my @blue_eth = split("\\n",$blue);
		foreach my $eth(@blue_eth)
		{
			push(@all_hash,$eth);
		}
	}
	
	my $temp_cmd = `ip a`;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
		{
			$eth = $1;
			if($eth =~ /^ipsec/ || $eth =~ /^tap/)
			{
				push(@all_hash,$eth);
			}
		}
	}
	return @all_hash;
}

#��ȡ��ǰ���õ�����
sub get_zone()
{
	my %zone;
	my $green  = `cat /var/efw/ethernet/br0`;
	my $orange = `cat /var/efw/ethernet/br1`;
	my $blue   = `cat /var/efw/ethernet/br2`;
	if($green)
	{
		$zone{'br0'} = _('GREEN')."����";
	}
	if($orange)
	{
		$zone{'br1'} = _('ORANGE')."����";
	}
	if($blue)
	{
		$zone{'br2'} = _('BLUE')."����";
	}
	return %zone;
}