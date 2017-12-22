#!/usr/bin/perl
#
#author:chenwu
#
#date:2012-08-06
#
#description:IPV6配置页面
require '/var/efw/header.pl';
require './endianinc.pl';
my $ipv6setting='/var/efw/ipv6/isatap_node/settings';
my $save_filename_tmp='/var/efw/ipv6/isatap_node/tmpfile';
my %par;
my $errormessage = "";
my $notemessage ="";
my %isatapnode_setting;

sub is_valid($) 
{
    my $line = shift;
    if($line =~ /(?:(?:[^,]*),){9}/) 
	{
        return 1;
    }
    return 0;
}
sub read_config_file($) {
    my $filename = shift;
    my @lines;
    open(FILE, "<$filename");
    foreach my $line (<FILE>){
		chomp($line);
		$line =~ s/[\r\n]//g;
		if(is_valid($line)){
			next;
		}
		push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub get_eth2()
{
	my @all_hash;
	my $green  = `cat /var/efw/ethernet/br0`;
	my $orange = `cat /var/efw/ethernet/br1`;
	my $blue   = `cat /var/efw/ethernet/br2`;
	if($green ne "")
	{
	  my $a="br0";
	  push(@all_hash,$a);	
	}
	
	if($orange ne " ")
	{
			push(@all_hash,'br1');
	}
	my $temp_cmd = `ip a`;
	my @temp = split(/\n/,$temp_cmd);
	foreach my $line(@temp)
	{
		if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
		{
			$eth = $1;
			if($eth =~ /^eth/ || $eth =~ /^tap/)
			{
				push(@all_hash,$eth);
				
			}
		}
	}

	return @all_hash;
	
}

sub display()
{ 
    my %display;
   if (-e $ipv6setting) {
		readhash($ipv6setting,\%display);
	}
	my $checked="";
	if ($display{'ENABLED'} eq "on") {
		$checked = "checked='checked'";
	}
	my %selected;
	$selected{$display{'INTERFACE'}}="selected";
	my $select_block='';
	my @eth  =  get_eth2();
	foreach my $interface (@eth)
	{   
        $select_block.="<option $selected{$interface} value='$interface' >$interface</option>";
        
	}
 
    openbox('100%', 'left', _('IPV6配置'));
printf <<EOF
	<form   action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="env">
    <td width="30%">%s</td>
    <td><input type='checkbox' value='on' name='ENABLED' $checked /></td>
    </tr>
    <tr class="env" id="local_ip">
    <td  class="need_help">%s</td>
    <td><input type='text' name='ROUTER_IP' value="$display{'REMOTE_IPV4_ADDR'}" SIZE="14" MAXLENGTH="15" /></td>
    </tr>  
EOF
, _('启用ISATAP节点')
, _('ISATAP路由器地址')
;
printf <<EOF
 <tr class="odd" id="interface">
    <td class="need_help">%s </td>
    <td><select name='SECTION'>
EOF
, _('接口')
;
print $select_block;
	
printf <<EOF
    </select>
	</td>
  </tr>
  <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save"></input>
		<input type="submit" class="net_button" value="保存" align="middle" />
	</td>
  </tr>
  </table>
  </form>
EOF
;
&closebox();
}

sub save()
{
	if($par{'ACTION'} eq "save" )
	{
	  	if (!validip($par{'ROUTER_IP'}))
	    {
	       $errormessage="无效的IP地址，请输入正确的IP地址";
	    }
		
         if(!-e $ipv6setting )
		 {
		   system("mkdir /var/efw/ipv6/isatap_node/");
		    system("touch /var/efw/ipv6/isatap_node/settings");
		 }
		 
	
        my $used_interface =$par{'SECTION'};
        my $local_ip = $par{'ROUTER_IP'};	
       	  if ($par{'ENABLED'}) {
			   $isatapnode_setting{'ENABLED'} = $par{'ENABLED'} ;
		   }
		   else{
			   $isatapnode_setting{'ENABLED'} = "off" ;
		   }	
	
        $isatapnode_setting{'REMOTE_IPV4_ADDR'} = $local_ip;
        $isatapnode_setting{'INTERFACE'} = $used_interface;	
		&writehash(${ipv6setting}, \%isatapnode_setting);	
		if(!-e $save_filename_tmp )
		{
		  system("touch $save_filename_tmp");
		}
		system("sudo /usr/local/bin/ipv6_isatap.py node");
		$notemessage = "已经成功保存此配置！";
	}
}

&getcgihash(\%par); 
&showhttpheaders(); 
&openpage(_('配置页面'),1,""); 
&save();
&openbigbox($errormessage,$warnmessage,$notemessage);
&display();
&closepage();