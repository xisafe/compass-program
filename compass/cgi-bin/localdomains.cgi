#!/usr/bin/perl
#

#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
#        |         Endian GmbH/Srl                                                     |
#        |         Bergweg 41 Via Monte                                                |
#        |         39057 Eppan/Appiano                                                 |
#        |         ITALIEN/ITALIA                                                      |
#        |         info@endian.it                                                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        | http://www.fsf.org/                                                         |
#        +-----------------------------------------------------------------------------+
#

require '/var/efw/header.pl';
require './endianinc.pl';

my (%cgiparams);
my $filename = "${swroot}/dnsmasq/local_nameserver";
my $rebootmessage = "";
$cgiparams{'ACTION'} = '';


sub check_form(){
printf<<EOF
<script>
var object = {
       'form_name':'LOCAL_DOMAIN',
       'option'   :{
                    'DOMAIN':{
                               'type':'text',
                               'required':'1',
                               'check':'domain_suffix|'
                             },
                    'SERVER':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'REMARK':{
                               'type':'text',
                               'required':'0',
                               'check':'note|'
                             }
                 }
         }
var check = new ChinArk_forms();
check._main(object);
//check._get_form_obj_table("LOCAL_DOMAIN");
</script>
EOF
;
}


&getcgihash(\%cgiparams);

&showhttpheaders();

my @current = ();
if (open(FILE, $filename)) {
    @current = <FILE>;
    close(FILE);
}

&readhash("${swroot}/main/settings", \%settings);

if ($cgiparams{'ACTION'} eq 'add')
{
	my @rule = read_config_file();
  if($cgiparams{'DOMAIN'} eq "")
  {
	$errormessage = _('域名为空');
  }elsif($cgiparams{'SERVER'} eq "")
  {
	$errormessage = _('服务器名为空');
  }else{
		my $key = 0;
		foreach my $line(@rule)
		{
			if($cgiparams{'KEY1'} ne '')
			{
				if($rule[$cgiparams{'KEY1'}] ne $line)
				{
					my @temp = split(",",$line);
					if($temp[1] eq $cgiparams{'DOMAIN'} && $temp[2] eq $cgiparams{'SERVER'})
					{
						$key = 1;
					}
				}
			}else{
					my @temp = split(",",$line);
					if($temp[1] eq $cgiparams{'DOMAIN'} && $temp[2] eq $cgiparams{'SERVER'})
					{
						$key = 1;
					}
			}
		
		}
		
		if($key eq 1)
		{
			$errormessage = _('The rules already exits');
			$cgiparams{'ACTION'} = 'edit';
		}
	}
  
  
  if ( (! $errormessage) && ($cgiparams{'DOMAIN'}) && ($cgiparams{'SERVER'}))
  {
    if ($cgiparams{'KEY1'} eq '') #Add or Edit ?
    {
      unshift (@current, "on,$cgiparams{'DOMAIN'},$cgiparams{'SERVER'},$cgiparams{'REMARK'}\n");
      &log(_('Domain was successfully added.'));
	  $notemessage = _('Domain was successfully added.');
    } else {
      @current[$cgiparams{'KEY1'}] = "on,$cgiparams{'DOMAIN'},$cgiparams{'SERVER'},$cgiparams{'REMARK'}\n";
      &log(_('Domain was successfully changed.'));
	  $notemessage =  _('Domain was successfully changed.');
      undef (%cgiparams); # End edit mode and clear fields.
    }
	open(FILE, ">$filename") or die 'Unable to open config file.';
  print(FILE @current);
  close(FILE);
  `sudo fmodify $filename`;
  $warnmessage = _("configures have been changed and need to be reboot in order to make the changes active!");
  }
}

if ($cgiparams{'ACTION'} eq 'restart') 
{
    system('/usr/local/bin/restartdnsmasq --force >/dev/null 2>&1 &');
	$notemessage = _("reboot successfully!");
}

if ($cgiparams{'ACTION'} eq 'edit')
{
  my @temp = split(/\,/,@current[$cgiparams{'KEY1'}]);
  $cgiparams{'ENABLED'} = $temp[0];
  $cgiparams{'DOMAIN'} = $temp[1];
  $cgiparams{'SERVER'} = $temp[2];
  $cgiparams{'REMARK'} = $temp[3];
}

if ($cgiparams{'ACTION'} eq 'remove')
{
  open(FILE, ">$filename") or die 'Unable to open config file.';
  splice (@current,$cgiparams{'KEY1'},1);
  print FILE @current;
  close(FILE);
  `sudo fmodify $filename`;
  undef ($cgiparams{'KEY1'});  # End remove mode
  &log(_('Domain was successfully changed.'));
  $notemessage = _('Domain was successfully changed.');
  $warnmessage = _("配置已经被删除，为使之生效需要重启！");
}

sub read_config_file() {
    my @lines;
    open (FILE, $filename);
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}


sub my_warnbox($) {
    my $caption = shift;
    if ($caption =~ /^\s*$/) 
	{
        return;
    }
    printf <<EOF
<div id="warning_box">
<img src='/images/dialog-warning.png' alt='_("Warning")' >
<span>$caption</span>
<form method='post' action='$self' enctype='multipart/form-data' style="margin-top:5px;">
  <input type='hidden' name='ACTION' value='restart' />
  <input type='submit' value='%s' class="net_button"/>
</form>
</div>
EOF
,_('restart')
,_('restart')
;
}


&openpage(_('DNS Proxy - Custom Nameserver for Domains'), 1, '');
#&openapplybox($applymessage,$notemessage,$errormessage);
&my_warnbox($warnmessage);
&openbigbox($errormessage,"", $notemessage);
#&openbox('100%', 'left', );
#&openbox('100%', 'left', _('Current configuration'));
my $addoredit = '为指定的域添加一个自定义域名服务器';
my $buttontext = _('Add');
if ($cgiparams{'KEY1'} ne '') {
  $buttontext = _('Update');
}
my $show = "";
if($cgiparams{'ACTION'} eq 'edit') {
    $show = "showeditor";
    $addoredit = '为指定的域编辑一个自定义域名服务器';
}
&openeditorbox($addoredit, _("Add Custom Domain"), $show, "createrule", @errormessages);

printf <<END
</form>
<form name="LOCAL_DOMAIN" action="$ENV{ 'SCRIPT_ADDR' }" method="post"  >
<input type='hidden' name='ACTION' value='add' >
<table cellpadding="0" cellspacing="0" width="100%" border='0'>
    <tr class="env">
        <td class="add-div-type" >%s *</td>
        <td ><input type='text' name='DOMAIN' value='$cgiparams{'DOMAIN'}' size='25' tabindex='1' ><input type='hidden' name='KEY1' value='$cgiparams{'KEY1'}' /></td>
    </tr>
    <tr class="odd">
        <td  class="add-div-type">%s *</td>
        <td ><input type='text' name='SERVER' value='$cgiparams{'SERVER'}' size='25' tabindex='2' ></td>
    </tr>
    <tr class="env">
        <td  class="add-div-type">%s</td>
        <td ><input type='text' name='REMARK' value='$cgiparams{'REMARK'}' size='25' tabindex='2' ></td>
    </tr>
</table>
END
,
_('Domain'),
_('DNS Server'),
_('Remark')

;
#&closebox();

&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createrule", "$ENV{SCRIPT_NAME}");

printf <<END
<br />
<div align='center'>
<table width='100%' cellpadding="0" cellspacing="0" class="ruleslist">
<tr>
    <td class="boldbase"  width="30%">%s</td>
    <td class="boldbase"  width="30%">%s</td>
    <td class="boldbase"  width="30%">%s</td>
    <td class="boldbase"  width="10%">%s</td>
</tr>
END
,
_('Domain'),
_('Nameserver'),
_('Remark'),
_('Actions')
;

my $key = 0;
my $length = @current;
if($length >0)
{
foreach my $line (@current)
{
  chomp($line);
  next if $line =~ /^$/;
  my @temp = split(/\,/,$line);

  if ($cgiparams{'KEY1'} eq $key) 
  {
    print "<tr class='selected'>\n";
  } elsif ($key % 2) 
  {
    print "<tr class='even'>\n";
  } else 
  {
    print "<tr class='oodd'>\n";
  }
  print "<td align='center'>$temp[1]</td>\n";
  print "<td align='center'>$temp[2]</td>\n";
  print "<td align='center'>$temp[3]</td>\n";
  printf <<END
<td class="actions">
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='edit' >
<input class='imagebutton' type='image' name='submit' src='/images/edit.png' alt='%s' title='%s' >
<input type='hidden' name='KEY1' value='$key' >
</form>
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='ACTION' value='remove' >
<input class='imagebutton' type='image' name='submit' src='/images/delete.png' alt='%s' title='%s' >
<input type='hidden' name='KEY1' value='$key' >
</form>
</td>


END
,
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
;
  print "</tr>\n";
  $key++;
}
}else{
	no_tr(4,_('Current no content'));
}
print "</table>";
print "</div>\n";

# If the file contains entries, print Key to action icons
if ( $key > 0) 
{
  printf <<END
<table cellpadding="0" cellspacing="0" class="list-legend">
<tr>
<td class='boldbase'><b>%s:</b>
<img src='/images/edit.png' alt='%s' >
%s
&nbsp; &nbsp; <img src='/images/delete.png' alt='%s' >
%s</td>
</tr>
</table>
END
,
_('Legend'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
;
}

#&closebox();
&closebigbox();
check_form();
&closepage();
