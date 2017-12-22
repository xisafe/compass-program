#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: ÓÊ¼þÏßÂ·Ò³Ãæ
#
# AUTHOR: ÖÜÔ² (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================

require '/var/efw/header23.pl';
require './endianinc.pl';
require '/var/efw/header.pl';
&validateUser();
my (%cgiparams);
my $filename = "${swroot}/smtpscan/bcc";
my $need_restart = "/var/efw/smtpscan/needrestart2";

$cgiparams{'ACTION'} = '';

&getcgihash(\%cgiparams);

&showhttpheaders();

if ( -f $filename ) {
    open(FILE, $filename) or die 'Unable to open config file.';
    @current = <FILE>;
    close(FILE);
}

&readhash("${swroot}/main/settings", \%settings);


if ($ENV{'QUERY_STRING'} =~ /RECIPIENT|BCC|DIRECTION/ ) {
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
	my @rule = read_config_file();
	if(!$cgiparams{'ADDRESS'})
	{
		$errormessage = _('Invalid email address.');
	}elsif(!validemail($cgiparams{'ADDRESS'}))
	{
		$errormessage = _('Invalid email address.');
	}elsif(!$cgiparams{'BCC'})
	{
		$errormessage = _('"%s" is no valid email address!',"BCC");
	}elsif(!validemail($cgiparams{'BCC'}))
	{
		$errormessage = _('"%s" is no valid email address!',"BCC");
	}else{
		my $key = 0;
		my $row_num = 0;
		foreach my $line(@rule)
		{
			my @temp = split(",",$line);
			if($temp[0] eq $cgiparams{'DIRECTION'} && $temp[1] eq $cgiparams{'ADDRESS'} && $temp[2] eq $cgiparams{'BCC'})
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
			$row_num++;
		
		}
		
		if($key eq 1)
		{
			$errormessage = _('The rules already exits');
		}
	}
  if (( ! $errormessage) && ($cgiparams{'DIRECTION'}))
  {
    if ($cgiparams{'KEY1'} eq '') #Add or Edit ?
    {
      unshift (@current, "$cgiparams{'DIRECTION'},$cgiparams{'ADDRESS'},$cgiparams{'BCC'}\n");
      &log(_('BCC address added'));
    } else {
      @current[$cgiparams{'KEY1'}] = "$cgiparams{'DIRECTION'},$cgiparams{'ADDRESS'},$cgiparams{'BCC'}\n";
      &log(_('BCC address changed'));
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
	$notemessage = _("邮件监听规则应用成功！");
	system ("rm $need_restart");#输出提示完后删除need_restart.
}

if ($cgiparams{'ACTION'} eq 'edit')
{
  my @temp = split(/\,/,@current[$cgiparams{'KEY1'}]);
  $cgiparams{'DIRECTION'} = $temp[0];
  $cgiparams{'ADDRESS'} = $temp[1];
  $cgiparams{'BCC'} = $temp[2];
}

if ($cgiparams{'ACTION'} eq 'remove')
{
  open(FILE, ">$filename") or die 'Unable to open config file.';
  splice (@current,$cgiparams{'KEY1'},1);
  print FILE @current;
  close(FILE);
  undef ($cgiparams{'KEY1'});  # End remove mode
  &log(_('BCC address changed'));
  `sudo fmodify $filename`;
  system ("touch $need_restart");#创建need_restart以供提示重启。
}

&openpage(_('SMTP Proxy'), 1, '');
openbigbox($errormessage, $warnmessage, $notemessage);

#存在need_restart则显示重启按钮。
if(-e $need_restart){
   &display_restart();
}

my $show = "";
$title = "添加邮件路由";
if($cgiparams{'ACTION'} eq 'edit') {
    $show = "showeditor";
    $title = "编辑邮件路由";
}

my $button = ($cgiparams{'ACTION'} eq 'edit') ? _("Update Mail Route") : _("Add Mail Route");
openeditorbox($title, $title, $show, "createrule", @errormessages);
  my $help_hash1 = read_json("/home/httpd/help/smtprouting_help.json","smtprouting.cgi","方向","-10","30","down");
  my $help_hash2 = read_json("/home/httpd/help/smtprouting_help.json","smtprouting.cgi","邮件地址","-10","30","down");
  my $help_hash3 = read_json("/home/httpd/help/smtprouting_help.json","smtprouting.cgi","BCC地址","-10","30","down");
#&openbox('100%', 'left', _('Settings'));
my $buttontext = _('Add');
if ($cgiparams{'KEY1'} ne '') { $buttontext = _('Update'); }

$selected{$cgiparams{'DIRECTION'}} = 'selected=selected'; 

printf <<END
</form>
<form name="PROXY" method= "post" action="$ENV{'SCRIPT_NAME'}"  >
  <input type='hidden' name='KEY1' value='$cgiparams{'KEY1'}' >
  <input type='hidden' name='ACTION' value='add' >
<table width='100%' cellpadding="0" cellspacing="0">
<tr class="env">
<td class="add-div-type need_help">%s:&nbsp;$help_hash1</td>
<td><select name="DIRECTION" size="1">
      <option $selected{'RECIPIENT'} value=RECIPIENT>%s</option>
      <option $selected{'SENDER'} value=SENDER>%s</option>
    </select>
</td>
</tr>

<tr class="odd">
<td class="add-div-type need_help">%s:&nbsp;$help_hash2</td>
<td><input type='text' name='ADDRESS' value='$cgiparams{'ADDRESS'}' size='25' tabindex='1' ></td>
</tr>

<tr class="env">
<td class="add-div-type need_help">%s:&nbsp;$help_hash3</td>
<td><input type='text' name='BCC' value='$cgiparams{'BCC'}' size='25' tabindex='2' ></td>
</tr>
</table>
END
,
_('Direction'),
_('Recipient'),
_('Sender'),
_('Mail address'),
_('BCC address')
;
&closeeditorbox($button, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

printf <<END
<br />
<div >
<table class="ruleslist" width='100%' cellpadding="0" cellspacing="0">
<tr>
<td class="boldbase" ><b>%s</b></td>
<td class="boldbase" width="20%" align="center"><b>%s</b></td>
<td class="boldbase" ></td>
<td class="boldbase" width="20%" align="center"><b>%s</b></td>
<td class="boldbase" >%s</td>
</tr>
END
,
_('Direction'),
_('Address'),
_("BCC Address"),
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
  if ( $temp[0] eq 'RECIPIENT') 
  {	
    printf "<td >"._('Recipient')."</td>\n";
  } else {
    printf "<td >"._('Sender')."</td>\n";
  }
  print "<td >$temp[1]</td>\n";
  print "<td class='center'>-></td>\n";
  print "<td >$temp[2]</td>\n";

  printf<<END
<td >
<form method='post' action='$ENV{'SCRIPT_NAME'}' style="display:block;float:left;margin-left:5px;">
<input type='hidden' name='ACTION' value='edit' >
<input class='imagebutton' type='image' name='%s' src='/images/edit.png' alt='%s' title='%s' >
<input type='hidden' name='KEY1' value='$key' >
</form>

<form method='post' action='$ENV{'SCRIPT_NAME'}' style="display:block;float:left;margin-left:5px;">
<input type='hidden' name='ACTION' value='remove' >
<input class='imagebutton' type='image' name='%s' src='/images/delete.png' alt='%s' title='%s' >
<input type='hidden' name='KEY1' value='$key' >
</form>
</td>


END
,
_('Edit'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
_('Remove')
;
  print "</tr>\n";
  $key++;
}
}else{
no_tr(7,_('Current no content'));
}
print "</table>";
print "</div>\n";

# If the file contains entries, print Key to action icons
if ( $key > 0) 
{

  printf <<END
<table cellpadding="0" cellspacing="0" class="list-legend">
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
    applybox(_("邮件监听规则已改变并且需要被应用以使改变有效！"));
}

sub check_form(){
	printf <<EOF
<script>
var object = {
       'form_name':'PROXY',
       'option'   :{
                    'ADDRESS':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|',
                             },
                    'BCC':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|',
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
    if ($qs eq 'DIRECTION') {  
      @a = split(/\./,$entries{$a}->{DIRECTION});
      @b = split(/\./,$entries{$b}->{DIRECTION});
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
    if ($qs eq 'BCC') {
      @a = split(/\./,$entries{$a}->{BCC});
      @b = split(/\./,$entries{$b}->{BCC});
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
    $line =~ /(.*),(.*),(.*)/;
    @record = ('name',$key++,'DIRECTION',$1,'ADDRESS',$2,'BCC',$3);
    $record = {};                        # create a reference to empty hash
    %{$record} = @record;                # populate that hash with @record
    $entries{$record->{name}} = $record; # add this to a hash of hashes
  }
  open(FILE, ">$filename") or die 'Unable to open config file.';
  foreach my $entry (sort bymysort keys %entries) 
  {
    print FILE "$entries{$entry}->{DIRECTION},$entries{$entry}->{ADDRESS},$entries{$entry}->{BCC}\n";
  }
  close(FILE);

  # Reload sorted  @current
  open (FILE, "$filename");
  @current = <FILE>;
  close (FILE);
}
