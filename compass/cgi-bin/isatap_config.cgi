#!/usr/bin/perl
#
#author:chenwu
#
#date:2012-08-06
#
#description:IPV6配置页面
require '/var/efw/header.pl';
require './endianinc.pl';
my $ipv6setting='/var/efw/ipv6/isatap_router/settings';
my $save_filename_tmp='/var/efw/ipv6/isatap_router/tmpfile';
my %par;
my $errormessage = "";
my $notemessage ="";
my %ipv6config_setting;
my $enabled = 'on';
my %checked   = ( 'on' => 'checked','off' => '');
sub save_config_file_back($$)
{
	my $filename = shift;
	my $tmpValue = shift;
    open(FILE, ">$filename");	
	print FILE "$tmpValue\n";
}
sub is_valid($) 
{
    my $line = shift;
    if($line =~ /(?:(?:[^,]*),){9}/) 
	{
        return 1;
    }
    return 0;
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
 openbox('100%', 'left', _('IPV6配置'));
    printf <<EOF
	<form   action="$ENV{'SCRIPT_NAME'}"  method="post">
<table cellpadding="0" cellspacing="0" width="100%" border='0' >
  <tr class="env">
    <td width="30%">%s</td>
    <td><input type='checkbox'  name='ENABLED' $checked /></td>
  </tr>

  <tr class="env" id="local_ip">
    <td  class="need_help">%s</td>
    <td><input type='text' name='LOCAL_IP' value="$display{'LOCAL_IPV4_ADDR'}" SIZE="14" MAXLENGTH="15" /></td>
  </tr>

  <tr class="odd" id="ipv6_prefix">
    <td class="need_help">%s</td>
    <td><input type='text' name='IPV6_PREFIX' value="$display{'IPV6_PREFIX'}" SIZE="14" MAXLENGTH="25" /></td>
  </tr>

  <tr class="table-footer">
    <td colspan="2">
        <input type="hidden" class="action" name="ACTION" value="save"></input>
		<input type="submit" class="net_button" value="保存" align="middle"/>
	</td>
  </tr>
  </table>
  </form>
EOF
, _('启动ISATAP路由器')
, _('本地IPV4地址')
, _('IPV6前缀')

;
&closebox();
}
sub save()
{
	
	if($par{'ACTION'} eq "save" )
	{ 
	  	if (!validip($par{'LOCAL_IP'}) )
	    {
	       $errormessage="无效的IP地址，请输入正确的IP地址";
		   return;
	    }
      
		
		
        if(!-e $ipv6setting)
		{
	       system("mkdir /var/efw/ipv6/isatap_router/");
		   system("touch /var/efw/ipv6/isatap_router/settings");
		}
		   #my %tmp = ();
	       #readhash($ipv6setting,%tmp);
	       #$enabled = $tmp{'ENABLED'};
	       my $local_ip = $par{'LOCAL_IP'};
           my $ipv6_prefix = $par{'IPV6_PREFIX'} ;
		   if ($par{'ENABLED'}) {
			   $ipv6config_setting{'ENABLED'} = $par{'ENABLED'} ;
		   }
		   else{
			   $ipv6config_setting{'ENABLED'} = "off" ;
		   }
           $ipv6config_setting{'LOCAL_IPV4_ADDR'} = $local_ip;
           $ipv6config_setting{'IPV6_PREFIX'} = $ipv6_prefix;	
		   &writehash($ipv6setting, \%ipv6config_setting);	
		   my $tmpValue = "$local_ip,$ipv6_prefix";
		   if(!-e $save_filename_tmp )
		   {
		     system("touch $save_filename_tmp");
		   }
		   &save_config_file_back($save_filename_tmp,$tmpValue);
           system("sudo /usr/local/bin/ipv6_isatap.py router");	
		   $notemessage = "已经成功保存此配置！";
	  }
}
    
&getcgihash(\%par); 
&showhttpheaders();
&openpage(_('配置页面'), 1);
&save();
&openbigbox($errormessage,$warnmessage,$notemessage);
&display();
&closepage();


   