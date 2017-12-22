#!/usr/bin/perl
#
#author:chenwu(陈武)
#
#date:2012-08-06
#
#description:IPV6路由配置页面
require 'ipv6_routing.pl';

my $ipv6routing_config ='/var/efw/ipv6/route/config';

my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $EDIT_PNG = '/images/edit.png';
my $DELETE_PNG = '/images/delete.png';
my $OPTIONAL_PNG = '/images/blob.png';
my @eth  =  get_eth();
my (%par,%checked,%selected);

sub reset_values() {
    %par = ();
}
sub get_eth1()
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


sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
	my $destination = $par{'destination'};
	my $dev= $par{'SECTION'};
	my $gw = $par{'gw'}; 
	my $config_line = "$destination,$gw,$dev";
    if ($action eq 'apply') {
	    system("rm -rf  $needreload");
        $notemessage = _("Routing rules applied successfully");
        return;
    }
    if ($action eq 'delete') {
	    my %del_line;
        %del_line= config_line(read_config_line($par{'line'}));
		 my $destination =$del_line{'destination'}; 
		 my $dev = $del_line{'dev'};
		 my $gw  = $del_line{'gw'};
		system("sudo /usr/local/bin/ipv6_route.py del $destination $dev $gw");
        delete_line($par{'line'});
        reset_values();
        return;
    }

    if ($action eq 'enable') {
        if (toggle_enable($par{'line'}, 1)) {
            reset_values();
            return;
        }
    }

   
    if (($action eq 'add') ||
        (($action eq 'edit')&&($sure eq 'y'))) {
 
        if(!$par{'destination'}) {
            $errormessage = _('目的IP不能为空!');
            return;
        }
		if(!-e '/var/efw/ipv6/route/config')
		{
		  system("mkdir /var/efw/ipv6/route/");
          system("touch /var/efw/ipv6/route/config");
		  append_config_file($config_line);
		} else{
		      append_config_file($config_line);
		}
        my $enabled = $par{'enabled'};
        system("sudo /usr/local/bin/ipv6_route.py add $destination $dev $gw");
    }
}

sub display_add($$) 
{
    my %display;
    my $is_editing = shift;
    my $line = shift;
    my %config;
    my %checked;
    my $select_block='';
	my %selected;
	%display  =  config_line(read_config_line($line));
	$selected{$display{'dev'}}="selected";
	my @eth  =  get_eth1();
	foreach my $interface (@eth)
	{   
        $select_block.="<option $selected{$interface} value='$interface' >$interface</option>";
        
	}
 
    if (($is_editing) && ($par{'sure'} ne 'y')) {
        %config = config_line(read_config_line($line));
    }
    else {
        %config = %par;
    }
    my $destination = $config{'destination'};
    my $gateway = $config{'gw'};

    my $tos = $config{'tos'};
 
 
    my $action = 'add';
    my $sure = '';
    my $title = _('Add routing entry');
    if ($is_editing) {
        $action = 'edit';
        $sure = '<input type="hidden" name="sure" value="y">';
        $title = _('Edit routing entry');
    }
 

    $checked{'ENABLED'}{$enabled} = 'checked';
    $buttontext = $par{'ACTION'} eq 'edit' || $par{'KEY1'} ne '' ? _("Update Route") : _("Add Route");

    if($par{'ACTION'} eq 'edit' || $errormessage ne '') {
        $show = "showeditor";
    }

    &openeditorbox(_('Add a new route'), $title, $show, "createrule", @errormessages);

    printf <<EOF
<table width="80%">
  <tr class="env">
    <td class="add-div-type" rowspan="2">%s</td>
    <td>%s </td>
	<td>
	<input type="text" name="destination" value="$destination" />
    </td>
  </tr>
  <tr class="env">
    <td >%s </td>
    <td><input type="text" name="gw" value="$gateway" />
	</td>
  </tr>
EOF
, _('选择器')
, _('目的网络')
, _('经网关')
;
printf <<EOF
 <tr class="odd" id="interface">
    <td  class="add-div-type" >%s </td>
    <td colspan="2"><select name='SECTION'>
EOF
, _('设备')
; 
print $select_block;
	
	printf <<EOF
		</select>
	 </td>
     </tr>  
	 </table>
	 <input type="hidden" name="ACTION" value="$action">
     <input type="hidden" name="line" value="$line">
     <input type="hidden" name="sure" value="y">
EOF
;
&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
}

sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;

    printf <<END
    
    <table  class="ruleslist"  cellpadding="0" cellspacing="0" width='100%'>
        <tr class="table-header">    
        
            <td  style="width:20%;">%s</td>
            <td  style="width:20%;">%s</td>
            <td  style="width:40%;">%s</td>
            <td  style="width:20%;">%s</td>
        </tr>
END
    ,
    _('目的网络'),
    _('经网关'),
    _('设备'),
    _('活动/动作')
    ;
    my @lines = read_config_file();
    my $j = 0;
	foreach my $thisline (@lines) {
    chomp($thisline);
    my %splitted = config_line($thisline);
    my $destination = value_or_nbsp($splitted{'destination'});

    $j++;
	}
	my $i =-1;

if($j > 0)
{
    foreach my $thisline (@lines) {
    chomp($thisline);
    my %splitted = config_line($thisline);
    $i++;
    my $destination = value_or_nbsp($splitted{'destination'});
    my $gw = value_or_nbsp($splitted{'gw'});
    my $dev = value_or_nbsp($splitted{'dev'});
    my $tos = value_or_nbsp($splitted{'tos'});
    my $enabled_gif = $DISABLED_PNG;
    my $enabled_alt = _('Disabled (click to enable)');
    my $enabled_action = 'enable';
    if ($splitted{'enabled'} eq 'on') {
        $enabled_gif = $ENABLED_PNG;
        $enabled_alt = _('Enabled (click to disable)');
        $enabled_action = 'disable';
    }

    my $bgcolor = setbgcolor($is_editing, $line, $i);

        printf <<EOF
    <tr class="$bgcolor">
        <td>$destination</td>
        <td>$gw</td>
        <td>$dev</td>
        <td class="actions">
           
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="line" value="$i">
            </form>
        </td>
    </tr>
EOF
,
_('Edit'),
_('Delete');
    }
}else{
	no_tr(5,_('Current no content'));
}

printf <<EOF
</table>
EOF
;

if($j >0)
{
printf <<EOF
<table class="list-legend" cellpadding="0" cellspacing="0">
  <tr>
    <td class="boldbase">
      <B>%s:</B>
  
   <IMG SRC="$DELETE_PNG" ALT="%s" />%s</td>
  </tr>
</table>
EOF
,
_('Legend'),
_('Remove'),
_('Remove')
;
}

&closebox();
    
}

&getcgihash(\%par);
&showhttpheaders();
my $extraheader = '<script language="JavaScript" src="/include/firewall_type.js"></script>';
&openpage(_('Routing'), 1, $extraheader);
save();
if ($reload) {
    system("touch $needreload");
}
&openbigbox($errormessage, $warnmessage, $notemessage);
if (-e $needreload) {
    applybox(_("Routing rules have been changed and need to be applied in order to make the changes active"));
}
#&openbox('100%', 'left', _('Current routing entries'));
display_add(($par{'ACTION'} eq 'edit'), $par{'line'});
display_rules(($par{'ACTION'} eq 'edit'), $par{'line'});
#&closebox();
&closebigbox();
&closepage();
