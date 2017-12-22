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

require '/var/efw/header23.pl';
require './endianinc.pl';
require '/var/efw/header.pl';
&validateUser();
my (%cgiparams);
my $filename = "${swroot}/smtpscan/domains";
my $need_restart = "/var/efw/smtpscan/needrestart";

$cgiparams{'ACTION'} = '';

&getcgihash(\%cgiparams);

&showhttpheaders();

open(FILE, $filename) or die 'Unable to open config file.';
my @current = <FILE>;
close(FILE);

&readhash("${swroot}/main/settings", \%settings);

if ($ENV{'QUERY_STRING'} =~ /DOMAIN|SERVER/ ) {
  my $newsort=$ENV{'QUERY_STRING'};
  $act=$settings{'SORT_HOSTSLIST'};
  #Reverse actual ?
  if ($act =~ $newsort) {
    if ($act !~ 'Rev') {$Rev='Rev'};
    $newsort.=$Rev
  };
  
  $settings{'SORT_HOSTSLIST'}=$newsort;
  &writehash("${swroot}/main/settings", \%settings);
  
  #Need to sort the file...
  &sortcurrent;
}

if ($cgiparams{'ACTION'} eq 'add')
{
  if(!$cgiparams{'DOMAIN'})
  {
	$errormessage = _("Invalid domain name");
  }elsif(!$cgiparams{'SERVER'})
  {
	$errormessage = _("Invalid IP address");
  }elsif(!validip($cgiparams{'SERVER'}))
  {
	$errormessage = _("Invalid IP address");
  }else{
		my @rule = read_config_file();
		my $key = 0;
		my $i =0;
		my $row_num = 0;
		foreach my $line(@rule)
		{
			my @temp = split(",",$line);
			my $length =@temp;
			my $firet_value = "";
			if($length >2)
			{
				for(my $i = 0;$i<$length-1;$i++)
				{
					$firet_value .= $temp[$i].",";
				}
			}else{
					$firet_value = $temp[0];
			}
			if ($cgiparams{'KEY1'} ne '' && $cgiparams{'KEY1'} ne $i) #Edit
			{
				if($firet_value eq $cgiparams{'DOMAIN'} && $temp[$length-1] eq $cgiparams{'SERVER'} )
				{
					#若为添加模式，检测到匹配则设置相同字段为1，若为编辑模式，进一步检测是否和原规则相同，和原规则相同则不设置为1.
			        if($cgiparams{'KEY1'} eq '')
	                {
				       $key = 1;
				    } else {
				       if(!($cgiparams{'KEY1'} eq $row_num))
				       {
				           $key = 1;
                       }
				    }
				}
			}else{
				if($firet_value eq $cgiparams{'DOMAIN'} && $temp[$length-1] eq $cgiparams{'SERVER'} )
				{
					#若为添加模式，检测到匹配则设置相同字段为1，若为编辑模式，进一步检测是否和原规则相同，和原规则相同则不设置为1.
			        if($cgiparams{'KEY1'} eq '')
	                {
				       $key = 1;
				    } else {
				       if(!($cgiparams{'KEY1'} eq $row_num))
				       {
				           $key = 1;
                       }
				    }
				}
			}
			$row_num++;
			
		}
		if($key eq 1)
		{
			$errormessage = _('The rules already exits');
		}
		$i++;
  }
  
  if( (! $errormessage) && ($cgiparams{'DOMAIN'}) && ($cgiparams{'SERVER'}))
  {
  
    if ($cgiparams{'KEY1'} eq '') #Add or Edit ?
    {
      unshift (@current, "$cgiparams{'DOMAIN'},$cgiparams{'SERVER'}\n");
      &log(_('Domain was successfully added.'));
    } else {
      @current[$cgiparams{'KEY1'}] = "$cgiparams{'DOMAIN'},$cgiparams{'SERVER'}\n";
      &log(_('Domain was successfully changed.'));
      undef (%cgiparams); # End edit mode and clear fields.
    }
	
    system ("touch $need_restart");#创建need_restart以供提示重启。
    #Sort here the file. So that resorting is much less time consuming next time.
    &sortcurrent;
    `sudo fmodify $filename`;
  } 
}

if ($cgiparams{'ACTION'} eq 'apply') 
{
    system('/usr/local/bin/restartsmtpscan --force >/dev/null 2>&1 &');
    `sudo fcmd '/usr/local/bin/restartsmtpscan --force >/dev/null 2>&1 &'`;
	  $notemessage = _("邮件域名转换规则应用成功!");
	  system ("rm $need_restart");#输出提示完后删除need_restart.
}

if ($cgiparams{'ACTION'} eq 'edit')
{
  my @temp = split(/\,/,@current[$cgiparams{'KEY1'}]);
  my $length = @temp;
  my $firet_value = "";
  if($length >2)
  {
	for(my $i = 0;$i<$length-1;$i++)
	{
		$firet_value .= $temp[$i].",";
	}
  }else{
	$firet_value = $temp[0];
  }
  $cgiparams{'DOMAIN'} = $firet_value;
  $cgiparams{'SERVER'} = $temp[$length-1];
}

if ($cgiparams{'ACTION'} eq 'remove')
{
  open(FILE, ">$filename") or die 'Unable to open config file.';
  splice (@current,$cgiparams{'KEY1'},1);
  print FILE @current;
  close(FILE);
  undef ($cgiparams{'KEY1'});  # End remove mode
  `sudo fmodify $filename`;
  &log(_('Domain was successfully changed.'));
  system ("touch $need_restart");#创建need_restart以供提示重启。
}

&openpage(_('SMTP Proxy'), 1, '');
openbigbox($errormessage, $warnmessage, $notemessage);

#存在need_restart则显示重启按钮。
if(-e $need_restart){
   &display_restart();
}

my $buttontext = _('Add');
if ($cgiparams{'KEY1'} ne '') {
  $buttontext = _('Update');
}

my $show = "";
$title = "添加域";
if($cgiparams{'ACTION'} eq 'edit') {
    $show = "showeditor";
    $title = "编辑域";
}

my $button = ($cgiparams{'ACTION'} eq 'edit') ? _("Update domain") : _("Add domain");
&openeditorbox($title, $title, $show, "createrule", @errormessages);
my $help_hash1 = read_json("/home/httpd/help/smtpdomains_help.json","smtp_domain_exchange_help.cgi","域","-10","30","down");
my $help_hash2 = read_json("/home/httpd/help/smtpdomains_help.json","smtp_domain_exchange_help.cgi","邮件服务器IP","-10","30","down");
printf <<END
</form>
<form name="PROXY" method= "post" action="$ENV{ 'SCRIPT_NAME' }" >
<table  width='100%' cellpadding="0" cellspacing="0">
<tr class="env">
<td class="add-div-type need_help">%s:&nbsp;*$help_hash1</td>
<td><input type='text' name='DOMAIN' value='$cgiparams{'DOMAIN'}' size='25' tabindex='1' /></td>
</tr>
<tr class="odd">
<td class="add-div-type need_help">%s:&nbsp;*$help_hash2</td>
<td><input type='text' name='SERVER' value='$cgiparams{'SERVER'}' size='25' tabindex='2' /></td>
</tr>
</table>
<input type='hidden' name='KEY1' value='$cgiparams{'KEY1'}' >
<input type='hidden' name='ACTION' value='add' >
END
,
_('Domain'),
_('Mailserver IP')
;

&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

printf <<END

<br/>
<div align='center'>
<table class="ruleslist" width='100%' cellpadding="0" cellspacing="0">
<tr>
<td class="boldbase">%s</td>
<td class="boldbase">%s</td>
<td class="boldbase">%s</td>
</tr>
END
,
_('Domain'),
_('Mailserver'),
_("Actions")
;

my $key = 0;
my $length = @current;

if($length >0)
{
foreach my $line (@current)
{
  chomp($line);
  my @temp = split(/\,/,$line);
  my $length = @temp;
  my $firet_value = "";
  if($length >2)
  {
	for(my $i = 0;$i<$length-1;$i++)
	{
		$firet_value .= $temp[$i].",";
	}
  }else{
	$firet_value = $temp[0];
  }
  if ($cgiparams{'KEY1'} eq $key) 
  {
    print "<tr class='selected'>\n";
  } elsif ($key % 2) 
  {
    print "<tr class='env_thin'>\n";
  } else 
  {
    print "<tr class='odd_thin'>\n";
  }
  print "<td align='center'>$firet_value</td>\n";
  print "<td align='center'>$temp[$length-1]</td>\n";
  printf <<END
<td>
<form method='post' action='$ENV{'SCRIPT_NAME'}' style="display:block;float:left;margin-left:5px;">
<input type='hidden' name='ACTION' value='edit' >
<input class='imagebutton' type='image' name='submit' src='/images/edit.png' alt='%s' title='%s' >
<input type='hidden' name='KEY1' value='$key' >
</form>

<form method='post' action='$ENV{'SCRIPT_NAME'}' style="display:block;float:left;margin-left:5px;">
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
_('Remove')
;
  print "</tr>\n";
  $key++;
}
}else{
no_tr(3,_('Current no content'));
}
print "</table>";
print "</div>\n";

# If the file contains entries, print Key to action icons
if ( $key > 0) 
{
  printf <<END
<TABLE cellpadding="0" cellspacing="0" class="list-legend">
<tr>
<td><b>%s:</b>
<img src='/images/edit.png' alt='%s' >
%s
<img src='/images/delete.png' alt='%s' >
%s</td>
</tr>
</table>
END
,
_('Legend'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')
;
}

&closebigbox();
check_form();
&closepage();

#显示重启提示
sub display_restart(){
    applybox(_("邮件域名转换规则已改变并且需要被应用以使改变有效！"));
}

sub check_form(){
printf <<EOF
<script>
var object = {
       'form_name':'PROXY',
       'option'   :{
                    'DOMAIN':{
                               'type':'text',
                               'required':'1',
                               'check':'domain_suffix|',
                             },
                    'SERVER':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                 }
         }
var check = new ChinArk_forms();
check._main(object);
</script>
EOF
;
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


# Sort function
sub bymysort {
  if (rindex ($settings{'SORT_HOSTSLIST'},'Rev') != -1)
  {
    $qs=substr ($settings{'SORT_HOSTSLIST'},0,length($settings{'SORT_HOSTSLIST'})-3);
    if ($qs eq 'DOMAIN') {  
      @a = split(/\./,$entries{$a}->{DOMAIN});
      @b = split(/\./,$entries{$b}->{DOMAIN});
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
    $qs=$settings{'SORT_HOSTSLIST'};
    if ($qs eq 'SERVER') {
      @a = split(/\./,$entries{$a}->{SERVER});
      @b = split(/\./,$entries{$b}->{SERVER});
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
    $line =~ /(.*),(.*)/;
    @record = ('name',$key++,'DOMAIN',$1,'SERVER',$2);
    $record = {};                        # create a reference to empty hash
    %{$record} = @record;                # populate that hash with @record
    $entries{$record->{name}} = $record; # add this to a hash of hashes
  }
  open(FILE, ">$filename") or die 'Unable to open config file.';
  foreach my $entry (sort bymysort keys %entries) 
  {
    print FILE "$entries{$entry}->{DOMAIN},$entries{$entry}->{SERVER}\n";
  }
  close(FILE);

  # Reload sorted  @current
  open (FILE, "$filename");
  @current = <FILE>;
  close (FILE);
}
