#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
# (c) Endian GmbH/srl
#
# Copyright (C) 01-02-2002 Graham Smith <grhm@grhm.co.uk>
#              - Fixed DHCP Leases added
#
# $Id: dhcp.cgi,v 1.14.2.24 2004/11/29 10:49:16 eoberlander Exp $
#
#  Franck    -rewrite for two or more interface
#  nov/2004    -check range is in correct subnet
#        -add NTP option
#        -add display sorting of actives leases
#
# to do : choose a correct format for displaying dates
#
require '/var/efw/header.pl';
use Net::IPv4Addr qw (:all);
use HTML::Entities;

my %dhcpsettings;
my %netsettings;
my %hostsettings;
my %hotspotsettings;
my $filename = "${swroot}/dhcp/fixleases";

my $conffile    = "${swroot}/dhcp/settings";
my $conffile_default = "${swroot}/dhcp/default/settings";
my $restart     = '/usr/local/bin/restartdhcp';

my %enable_file = ();
$enable_file{'GREEN'}  = "${swroot}/dhcp/enable_green";
$enable_file{'BLUE'}   = "${swroot}/dhcp/enable_blue";
$enable_file{'ORANGE'} = "${swroot}/dhcp/enable_orange";

my $ntp_enable_file = "${swroot}/time/enable";

my $custom_global = "";
my $custom_global_file="${swroot}/dhcp/custom.tpl";

my %enable = ();
$enable{'GREEN'} = 0;
if (-e $enable_file{'GREEN'}) {
  $enable{'GREEN'} = 1;
}
$enable{'BLUE'} = 0;
if (-e $enable_file{'BLUE'}) {
  $enable{'BLUE'} = 1;
}
$enable{'ORANGE'} = 0;
if (-e $enable_file{'ORANGE'}) {
  $enable{'ORANGE'} = 1;
}

$ntp_enable = 0;
if (-e $ntp_enable_file) {
  $ntp_enable = 1;
}

sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'DHCP_FORM',
       'option'   :{
                    'FIX_MAC':{
                               'type':'text',
                               'required':'1',
                               'check':'mac|'
                             },
                    'FIX_ADDR':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'FIX_DESCRIPTION':{
                               'type':'text',
                               'required':'0',
                               'check':'note|'
                             },
                    'FIX_NEXTADDR':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|'
                             },
                    'FIX_FILENAME':{
                               'type':'text',
                               'required':'0',
                               'check':'name|'
                             },
                    'FIX_ROOTPATH':{
                               'type':'text',
                               'required':'0',
                               'check':'name|'
                             }
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("DHCP_FORM");
    </script>
EOF
;
}
sub toggle_file($$) {
    my $file = shift;
    my $set = shift;

    if ($set) {
    `touch $file`;
    return 1;
    }
    if (-e $file) {
    unlink($file);
    }
    return 0;
}

sub read_file($) {
    my $f = shift;
    open(F, $f) || return "";
    my @lines = <F>;
    close(F);
    return join("", @lines);
}

sub write_file($$) {
    my $f = shift;
    my $data = shift;
    open(F, ">$f") || return;
    print F $data;
    close(F);
}

sub ip2long {
    return unpack("l*", pack("l*", unpack("N*", inet_aton(shift))));
}

sub read_dhcp_conf() {

    if (-e $conffile_default) {
    readhash($conffile_default, \%dhcpsettings);
    }
    if (-e $conffile) {
    readhash($conffile, \%dhcpsettings);
    }
    $custom_global = read_file($custom_global_file);
}

&showhttpheaders();
@ITFs=('GREEN');

if (orange_used()) {
    push(@ITFs, 'ORANGE');
}
if (blue_used()) {
    push(@ITFs, 'BLUE');
}

my %interface_title = (
    'GREEN' => _('Green interface'),
    'ORANGE' => _('Orange interface'),
    'BLUE' => _('Blue interface')
);

# dependent interface variable
foreach $itf (@ITFs) {
  $dhcpsettings{"ENABLE_${itf}"} = '';
  $dhcpsettings{"START_ADDR_${itf}"} = '';
  $dhcpsettings{"END_ADDR_${itf}"} = '';
  $dhcpsettings{"ONLY_FIXEDLEASE_${itf}"} = '';
  $dhcpsettings{"DOMAIN_NAME_${itf}"} = '';
  $dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} = '';
  $dhcpsettings{"MAX_LEASE_TIME_${itf}"} = '';
  $dhcpsettings{"GATEWAY_${itf}"} = '';
  $dhcpsettings{"WINS1_${itf}"} = '';
  $dhcpsettings{"WINS2_${itf}"} = '';
  $dhcpsettings{"DNS1_${itf}"} = '';
  $dhcpsettings{"DNS2_${itf}"} = '';
  $dhcpsettings{"NTP1_${itf}"} = '';
  $dhcpsettings{"NTP2_${itf}"} = '';
}

$dhcpsettings{'FIX_MAC'} = '';
$dhcpsettings{'FIX_ADDR'} = '';
$dhcpsettings{'ENABLED'} = '';
$dhcpsettings{'FIX_NEXTADDR'} = '';
$dhcpsettings{'FIX_FILENAME'} = '';
$dhcpsettings{'FIX_ROOTPATH'} = '';
$dhcpsettings{'FIX_DESCRIPTION'} = '';

&getcgihash(\%dhcpsettings);
####help_msg
	my $help_hash1 = read_json("/home/httpd/help/confirm_dhcp_help.json","confirm_dhcp.cgi","服务-DHCP服务器-固定租约-MAC地址","-10","30","down");
	my $help_hash2 = read_json("/home/httpd/help/confirm_dhcp_help.json","confirm_dhcp.cgi","服务-DHCP服务器-固定租约-IP地址","-10","30","down");
	my $help_hash3 = read_json("/home/httpd/help/confirm_dhcp_help.json","confirm_dhcp.cgi","服务-DHCP服务器-固定租约-描述","-10","30","down");
	my $help_hash4 = read_json("/home/httpd/help/confirm_dhcp_help.json","confirm_dhcp.cgi","服务-DHCP服务器-固定租约-下一跳地址","-10","30","down");
	my $help_hash5 = read_json("/home/httpd/help/confirm_dhcp_help.json","confirm_dhcp.cgi","服务-DHCP服务器-固定租约-根路径","-10","30","down");
###
my @current = ();
if ( -e $filename) {
    open(FILE, "$filename") or die 'Unable to open fixed leases file.';
    @current = <FILE>;
    close(FILE);
}

&readhash("${swroot}/ethernet/settings", \%netsettings);
&readhash("${swroot}/host/settings", \%hostsettings);

if (-e "/usr/lib/efw/hotspot/default/settings") {
    &readhash("/usr/lib/efw/hotspot/default/settings", \%hotspotsettings);
}
if (-e "${swroot}/hotspot/settings") {
    &readhash("${swroot}/hotspot/settings", \%hotspotsettings);
}

foreach $itf (@ITFs) {
    if ($netsettings{"${itf}_NETADDRESS"} ne "" and $netsettings{"${itf}_NETMASK"} ne "") {
        my $netaddress = $netsettings{"${itf}_NETADDRESS"};
        my $fwaddress = $netsettings{"${itf}_ADDRESS"};
        my $broadcastaddress = ipv4_broadcast($netsettings{"${itf}_NETADDRESS"}, $netsettings{"${itf}_NETMASK"});
        my @ip = split(/\./, $fwaddress);
        my @net = split(/\./, $netaddress);
        my @broadcast = split(/\./, $broadcastaddress);
        if (@ip[3] eq @broadcast[3] - 1) {
            if ($dhcpsettings{"START_ADDR_${itf}"} eq "") {
                $dhcpsettings{"START_ADDR_${itf}"} = @net[0].".".@net[1].".".@net[2].".".(@net[3] + 1);
            }
            if ($dhcpsettings{"END_ADDR_${itf}"} eq "") {
                $dhcpsettings{"END_ADDR_${itf}"} = @ip[0].".".@ip[1].".".@ip[2].".".(@ip[3] - 1);
            }
        }
        else {
            if ($dhcpsettings{"START_ADDR_${itf}"} eq "") {
                $dhcpsettings{"START_ADDR_${itf}"} = @ip[0].".".@ip[1].".".@ip[2].".".(@ip[3] + 1);
            }
            if ($dhcpsettings{"END_ADDR_${itf}"} eq "") {
                $dhcpsettings{"END_ADDR_${itf}"} = @broadcast[0].".".@broadcast[1].".".@broadcast[2].".".(@broadcast[3] - 1);
            }
        }
    }
}

my @errormessages = ();

# Toggle enable/disable field on specified lease.
if ($dhcpsettings{'ACTION'} eq 'toggle')
{
    my @temp = split(/\,/,@current[$dhcpsettings{'KEY1'}]);
    if ($temp[2] eq 'on') {
    $temp[2] = '';
    } else {
    $temp[2] = 'on';
    }
    @current[$dhcpsettings{'KEY1'}] = "$temp[0],$temp[1],$temp[2],$temp[3],$temp[4],$temp[5],$temp[6]";
    $dhcpsettings{'KEY1'} = ''; # End edit mode
    &log(_('Fixed IP lease modified'));
    open(FILE, ">$filename") or die 'Unable to open fixed leases file.';
    print FILE @current;
    close(FILE);
	`sudo fmodify $filename`;
    #Write changes to dhcpd.conf.
    read_dhcp_conf();
    &buildconf;
}


if ($dhcpsettings{'ACTION'} eq 'add')
{
    $dhcpsettings{'FIX_MAC'} =~ tr/-/:/;
    unless(&validip($dhcpsettings{'FIX_ADDR'})) { 
        push(@errormessages, _('Invalid fixed IP address'));
    }
    unless(&validmac($dhcpsettings{'FIX_MAC'})) {
        push(@errormessages, _('Invalid fixed MAC address'));
    }
    if ($dhcpsettings{'FIX_NEXTADDR'}) 
    {
        unless(&validip($dhcpsettings{'FIX_NEXTADDR'})) {
            push(@errormessages, _('Invalid next fixed IP address'));
        }
    }
    
    my $key = 0;
    foreach my $line (@current)
    {
        my @temp = split(/\,/,$line);
        if($dhcpsettings{'KEY1'} ne $key)
        {
        if(lc($dhcpsettings{'FIX_MAC'}) eq lc($temp[0]) && $dhcpsettings{'FIX_MAC'} ne "")
        {
            push(@errormessages, _('MAC address \'%s\' already in use', $dhcpsettings{'FIX_MAC'}));
        }
        if($dhcpsettings{'FIX_ADDR'} eq $temp[1] && $dhcpsettings{'FIX_ADDR'} ne "")
        {
            push(@errormessages, _('IP address \'%s\' already in use', $dhcpsettings{'FIX_ADDR'}));
        }
    }
    $key++;
}
    
    if ($#errormessages eq -1) {
        if ($dhcpsettings{'KEY1'} eq '') #add or edit ?
        {
        unshift (@current, "$dhcpsettings{'FIX_MAC'},$dhcpsettings{'FIX_ADDR'},$dhcpsettings{'ENABLED'},$dhcpsettings{'FIX_NEXTADDR'},$dhcpsettings{'FIX_FILENAME'},$dhcpsettings{'FIX_ROOTPATH'},$dhcpsettings{'FIX_DESCRIPTION'}\n");
        &log(_('Fixed IP lease added'));
        } else {
        @current[$dhcpsettings{'KEY1'}] = "$dhcpsettings{'FIX_MAC'},$dhcpsettings{'FIX_ADDR'},$dhcpsettings{'ENABLED'},$dhcpsettings{'FIX_NEXTADDR'},$dhcpsettings{'FIX_FILENAME'},$dhcpsettings{'FIX_ROOTPATH'},$dhcpsettings{'FIX_DESCRIPTION'}\n";
        $dhcpsettings{'FIX_MAC'}='';
        $dhcpsettings{'FIX_ADDR'}='';
        $dhcpsettings{'FIX_NEXTADDR'}='';
        $dhcpsettings{'FIX_FILENAME'}='';
        $dhcpsettings{'FIX_ROOTPATH'}='';
        $dhcpsettings{'FIX_DESCRIPTION'}='';
        $dhcpsettings{'ENABLED'}='on';
        $dhcpsettings{'KEY1'} = '';       # End edit mode
        &log(_('Fixed IP lease modified'));
		`sudo fmodify $filename`;
        }
        

        #Write changes to dhcpd.conf.
        read_dhcp_conf();
        &sortcurrent;     # sort newly added/modified entry
        &buildconf;       # before calling buildconf which use fixed lease file !
    } else {
        my %temp_settings = %dhcpsettings;
        read_dhcp_conf();
        $dhcpsettings{'FIX_MAC'}= $temp_settings{'FIX_MAC'};
        $dhcpsettings{'FIX_ADDR'}= $temp_settings{'FIX_ADDR'};
        $dhcpsettings{'FIX_NEXTADDR'}= $temp_settings{'FIX_NEXTADDR'};
        $dhcpsettings{'FIX_FILENAME'}= $temp_settings{'FIX_FILENAME'};
        $dhcpsettings{'FIX_ROOTPATH'}= $temp_settings{'FIX_ROOTPATH'};
        $dhcpsettings{'FIX_DESCRIPTION'}= $temp_settings{'FIX_DESCRIPTION'};
        $dhcpsettings{'ENABLED'}= $temp_settings{'ENABLED'};
        $dhcpsettings{'KEY1'} = $temp_settings{'KEY1'};
    }
}

if ($dhcpsettings{'ACTION'} eq 'edit')
{
    my @temp = split(/\,/,@current[$dhcpsettings{'KEY1'}]);
    read_dhcp_conf();
    $dhcpsettings{'FIX_MAC'}=$temp[0];
    $dhcpsettings{'FIX_ADDR'}=$temp[1];
    $dhcpsettings{'ENABLED'}=$temp[2];
    $dhcpsettings{'FIX_NEXTADDR'}=$temp[3];
    $dhcpsettings{'FIX_FILENAME'}=$temp[4];
    $dhcpsettings{'FIX_ROOTPATH'}=$temp[5];
    $dhcpsettings{'FIX_DESCRIPTION'}=$temp[6];
}


if ($dhcpsettings{'ACTION'} eq 'remove')
{
    splice (@current,$dhcpsettings{'KEY1'},1);
    open(FILE, ">$filename") or die 'Unable to open fixed lease file.';
    print FILE @current;
    close(FILE);
	`sudo fmodify $filename`;
    &log(_('Fixed IP lease removed'));

    #Write changes to dhcpd.conf.
    read_dhcp_conf();
    undef ($dhcpsettings{'KEY1'});  # End remove mode
    &buildconf;
}



#Sorting of fixed leases
if ($ENV{'QUERY_STRING'} =~ /^FETHER|^FIPADDR/ ) {
    my $newsort=$ENV{'QUERY_STRING'};
    read_dhcp_conf();
    $act=$dhcpsettings{'SORT_FLEASELIST'};
    #Reverse actual ?
    if ($act =~ $newsort) {
        if ($act !~ 'Rev') {$Rev='Rev'};
        $newsort.=$Rev
    };

    $dhcpsettings{'SORT_FLEASELIST'}=$newsort;
    &writehash("${swroot}/dhcp/settings", \%dhcpsettings);
	`sudo fmodify "${swroot}/dhcp/settings"`;
    &sortcurrent;
    $dhcpsettings{'ACTION'} = 'SORT';  # avoid the next test "First lauch"
}

#Sorting of allocated leases
&CheckSortOrder;

if ($dhcpsettings{'ACTION'} eq '' ) { # First launch

    read_dhcp_conf();

    # Set default DHCP values only if blank and disabled
    foreach $itf (@ITFs) {
    if ($dhcpsettings{"ENABLE_${itf}"} ne 'on' )
    {
            if (!($dhcpsettings{"DNS1_${itf}"})) { $dhcpsettings{"DNS1_${itf}"} = $netsettings{"${itf}_ADDRESS"} };
        $dhcpsettings{"DEFAULT_LEASE_TIME_${itf}"} = '60';
        $dhcpsettings{"MAX_LEASE_TIME_${itf}"} = '120';
        $dhcpsettings{"GATEWAY_${itf}"} = $netsettings{"${itf}_ADDRESS"};
        $dhcpsettings{"DOMAIN_NAME_${itf}"} = $hostsettings{'DOMAINNAME'};
    }
    }
}

&openpage(_('DHCP configuration'), 1, '');
my $errormessage = "";
foreach my $line_temp(@errormessages)
{
	$errormessage.=$line_temp."<br />";
}
&openbigbox($errormessage, $warnmessage, $notemessage);
if ($warnNTPmessage)
{
    $warnNTPmessage = "<td>$warnNTPmessage</td>";
}

printf <<EOF

<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='save' >
EOF
;

#&openbox('100%', 'left', _('Fixed Leases'));

my %fixchecked;
$fixchecked{'ENABLED'}{'off'} = '';
$fixchecked{'ENABLED'}{'on'} = '';  
$fixchecked{'ENABLED'}{$dhcpsettings{'ENABLED'}} = "checked='checked'";

my $buttontext = _("Add");
my $title = "添加固定租约";
if ($dhcpsettings{'KEY1'} ne '') {
    $buttontext = _('Update');
    #&openbox('100%', 'left', _('Edit an existing lease'));
} else {
    #&openbox('100%', 'left', _('Add a new fixed lease'));
}
if ($dhcpsettings{'ACTION'} eq 'edit') {
	$buttontext = _("Edit");
	$title =  '编辑固定租约';
}
#&openbox('100%', 'left', _('Current fixed leases'), "fixedleases");
my $id = $dhcpsettings{'FIX_MAC'};
$id =~ s/://g;
printf <<END
</form>
    <input class="form" type="hidden" name="ID" value="$id" />
END
;

openeditorbox($title, _("Add a fixed lease"), ($dhcpsettings{'ACTION'} eq 'edit' || scalar(@errormessages) > 0 ? "showeditor" : ""), "fixedleases", );

printf <<END
</form>
     <form name="DHCP_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
    <table width='100%' cellpadding="0" cellspacing="0">
    <tr class="env">
        <td class='add-div-type need_help'>%s *</td>
        <td class="need_help"><input class="form" type='text' name='FIX_MAC' value='$dhcpsettings{'FIX_MAC'}' size='18' />$help_hash1</td>
	</tr>
	<tr class="odd">
        <td class='add-div-type need_help'>%s *</td>
        <td class="need_help"><input class="form" type='text' name='FIX_ADDR' value='$dhcpsettings{'FIX_ADDR'}' size='18' />$help_hash2</td>
	</tr>
	<tr class="env">
        <td class='add-div-type need_help'>%s</td>
        <td class="need_help"><input class="form" type='text' name='FIX_DESCRIPTION' value='$dhcpsettings{'FIX_DESCRIPTION'}' size='18' />$help_hash3</td>
    </tr>
    <tr class="odd"> 
        <td class='add-div-type need_help'>%s</td>
        <td class="need_help"><input class="form" type='text' name='FIX_NEXTADDR' value='$dhcpsettings{'FIX_NEXTADDR'}' size='18' />$help_hash4</td>
	</tr>
	<tr class="env">
        <td class='add-div-type'>%s</td>
        <td><input class="form" type='text' name='FIX_FILENAME' value='$dhcpsettings{'FIX_FILENAME'}' size='18' /></td>
	</tr>
	<tr class="odd" style = "display:none">
        <td class='add-div-type need_help'>%s$help_hash5</td>
        <td><input class="form" type='text' name='FIX_ROOTPATH' value='$dhcpsettings{'FIX_ROOTPATH'}' size='18' /></td>
    </tr>
    <tr class="env">
        <td class='add-div-type'>%s
		</td>
		<td>
			<input class="form" type='checkbox' name='ENABLED' $fixchecked{'ENABLED'}{'on'} />
	
            <input type='hidden' name='ACTION' value='add' />
        </td>
    </tr>
    </table>
END
,
_('MAC address'),
_('IP address'),
_('Description'),
_('Next address'),
_('Filename'),
_('Root path'),
_('Enabled'),
;

#Edited line number passed until cleared by 'save' or 'remove' or 'new sort order'
print "<input type='hidden' name='KEY1' value='$dhcpsettings{'KEY1'}' >";

&closeeditorbox($buttontext, _("Cancel"), "leasebutton", "fixedleases",$ENV{'SCRIPT_NAME'});

#&closebox();

printf <<END
<table width='100%' cellspacing="0" cellpadding="0" class="ruleslist">
<tr>
    <td width='16%' nowrap="nowrap" class='boldbase'>%s</td>
    <td width='16%' nowrap="nowrap"  class='boldbase'>%s</td>
    <td width='16%' nowrap="nowrap" class='boldbase'><b>%s</b></td>
    <td width='16%' nowrap="nowrap"  class='boldbase'><b>%s</b></td>
    <td width='8%'  nowrap="nowrap" class='boldbase'><b>%s</b></td>
    <td width='16%' nowrap="nowrap" class='boldbase'><b>%s</b></td>
    <td width='16%' nowrap="nowrap" class='boldbase'><b>%s</b></td>
</tr>
END
,
_('MAC address'),
_('IP address'),
_('Next address'),
_('Filename'),
_('Root path'),
_('Description'),
_("Actions")
;

my $key = 0;
foreach my $line (@current)
{
    my $gif = '';
    my $gdesc = '';
    chomp($line);
    my @temp = split(/\,/,$line);
    
    if ($temp[2] eq "on") {
        $gif = 'on.png';
        $gdesc = _('Enabled (click to disable)');
    }
    else {
        $gif = 'off.png';
        $gdesc = _('Disabled (click to enable)'); 
    }
        
    if ($key % 2) {
        $origcolor = "even"; 
    }
    else {
        $origcolor = "oodd"; 
    }
    
    if ($dhcpsettings{'KEY1'} eq $key) {
        $color = "selected";
    }
    else {
        $color = $origcolor;
    }
    
    my %toggle;
    $toggle{'ENABLED'}{'off'} = '';
    $toggle{'ENABLED'}{'on'} = '';  
    $toggle{'ENABLED'}{'$temp[2]'} = "checked='checked'";
    
    my $id = $temp[0];
    $id =~ s/://g; 

        printf <<END
<tr class="$color" id="row_$id">
<td align='center'>$temp[0]</td>
<td align='center'>$temp[1]</td>
<td align='center'>$temp[3]&nbsp;</td>
<td align='center'>$temp[4]&nbsp;</td>
<td align='center'>$temp[5]&nbsp;</td>
<td align='center'>$temp[6]&nbsp;</td>

<td class="actions">
<input type="hidden" class="$id" name="rowcolor" value="$origcolor" />
<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}#fixedleases'>
<input class='imagebutton' type='image' name='submit' src='/images/$gif' alt='$gdesc' title='$gdesc'>
<input type='hidden' name='ACTION' value='toggle'>
<input type='hidden' name='KEY1' value='$key'>
<input type='hidden' name='ENABLED' value='$toggle{'ENABLED'}{'on'}'>
</form>
<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}#fixedleases'>
<input type='hidden' name='ACTION' value='edit' />
<input class='imagebutton' type='image' name='submit' src='/images/edit.png' alt='%s' title='%s'>
<input type='hidden' name='KEY1' value='$key' />
</form>
<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}#fixedleases'>
    <input type='hidden' name='ACTION' value='remove'>
<input class='imagebutton' type='image' name='submit' src='/images/delete.png' alt='%s' title='%s'>
<input type='hidden' name='KEY1' value='$key'>
</form>
</td>
</tr>
END
,
_('Enable or Disable'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')

;
    $key++;
}
if ($key eq '0') {
	no_tr(7,_('Current no content'));
}
print "</table>";

# If the fixed lease file contains entries, print Key to action icons
if ( $key > 0) {
printf <<END
<table cellpadding="0" cellspacing="0" class="list-legend">
<tr><td>
<b>%s:</b>
<img src='/images/on.png' alt='%s' >
%s
<img src='/images/off.png' alt='%s' />
%s
<img src='/images/edit.png' alt='%s' >
%s
<img src='/images/delete.png' alt='%s' >
%s</td>
</tr>
</table>
END
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')

;
}
#&closebox();
#&closebox();

&closebigbox();
check_form();
&closepage();


sub fixedleasesort {
    if (rindex ($dhcpsettings{'SORT_FLEASELIST'},'Rev') != -1)
    {
        $qs=substr ($dhcpsettings{'SORT_FLEASELIST'},0,length($dhcpsettings{'SORT_FLEASELIST'})-3);
    if ($qs eq 'FIPADDR') {
        @a = split(/\./,$entries{$a}->{$qs});
        @b = split(/\./,$entries{$b}->{$qs});
        ($b[0]<=>$a[0]) ||
        ($b[1]<=>$a[1]) ||
        ($b[2]<=>$a[2]) ||
        ($b[3]<=>$a[3]);
    }else {
        $entries{$b}->{$qs} cmp $entries{$a}->{$qs};
    }
    }
    else #not reverse
    {
    $qs=$dhcpsettings{'SORT_FLEASELIST'};
    if ($qs eq 'FIPADDR') {
        @a = split(/\./,$entries{$a}->{$qs});
        @b = split(/\./,$entries{$b}->{$qs});
        ($a[0]<=>$b[0]) ||
        ($a[1]<=>$b[1]) ||
        ($a[2]<=>$b[2]) ||
        ($a[3]<=>$b[3]);
    }else {
        $entries{$a}->{$qs} cmp $entries{$b}->{$qs};
    }
    }
}
# Sort the "current" array according to choices
sub sortcurrent
{
    #Use an associative array (%entries)
    my $key = 0;
    foreach my $line (@current)
    {
        $line =~ /^(.*),(.*),(.*,.*,.*,.*,.*)$/; # 00:X:X:X:X:X,10.0.0.1,on,,,,
        $record = {};                           # create a reference to empty hash
        if ( $3 ) {
            @record = ('FETHER',$1,'FIPADDR',$2,'DATA',$3);
        } else {
            $line =~ /^(.*),(.*),(.*,.*,.*,.*)$/; # 00:XX:XX:XX:XX:XX,10.0.0.1,on,,,
            $data = $3 . ",";
            @record = ('FETHER',$1,'FIPADDR',$2,'DATA',$data);
        }
        %{$record} = @record;                   # populate that hash with @record
        $entries{$record->{FIPADDR}} = $record; # add this to a hash of hashes
    }
    
    open(FILE, ">$filename") or die 'Unable to open fixed lease file.';
    foreach my $entry ( sort fixedleasesort keys %entries)
    {
        print FILE "$entries{$entry}->{FETHER},$entries{$entry}->{FIPADDR},$entries{$entry}->{DATA}\n";
    }
    close(FILE);
	`sudo fmodify $filename`;	
    # Reload sorted  @current
    open (FILE, "$filename");
    @current = <FILE>;
    close (FILE);
    undef (%entries);  #This array is reused latter. Clear it.
}
                            
# Build the configuration file mixing  settings and lease
sub buildconf {
    system '/usr/local/bin/restartdhcp --force';
}


