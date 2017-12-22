#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: Ìí¼ÓÖ÷»úÒ³Ãæ
#
# AUTHOR: ÖÜÔ² (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================

require '/var/efw/header.pl';

my (%cgiparams);
my $filename = "${swroot}/tunnelnat/config";
my $need = "${swroot}/tunnelnat/needreload";
my $apply_message = "";
my $action = 'add';
my $EDIT_PNG           =  "/images/edit.png";
my $DELETE_PNG         =  "/images/delete.png";
my $ON_PNG             =  "/images/on.png";
my $OFF_PNG            =  "/images/off.png";

&getcgihash(\%cgiparams);
&showhttpheaders(); 
###读取原来文件的内容
#open(FILE,$filename);
@current = read_file($filename);
#close(FILE);

&openpage(_('隧道内NAT设置'), 1, '');
save();
if (-e $need) {
   $apply_message = _('configures have been changed and need to be applied in order to make the changes active!');
}
if($apply_message ne ""){
   &applybox($apply_message);
}
&openbigbox($errormessage, $warnmessage, $notemessage);
&add_rules();
&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
&display_rules();
check_form();
&closebigbox();
&closepage();
sub read_file($) {
    my @lines;
    my $file=shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}
###保存数据的函数
sub save(){
    if ($cgiparams{'ACTION'} eq 'add' || ($cgiparams{'ACTION'} eq 'edit' && $cgiparams{'SURE'} eq 'y')){       
        if ($#errormessages eq -1){
            if ($cgiparams{'KEY1'} eq '') {
                push(@current, "$cgiparams{'INIT_IP'},$cgiparams{'PROXY_IP'},$cgiparams{'LOG'},$cgiparams{'ENABLED'}");
                &log(_('hosts config added'));
            } 
            else {
                @current[$cgiparams{'KEY1'}] = "$cgiparams{'INIT_IP'},$cgiparams{'PROXY_IP'},$cgiparams{'LOG'},$cgiparams{'ENABLED'}";
                &log(_('hosts config changed'));
                undef (%cgiparams); 
            }
            if(!(-e $need)){
                system("touch $need");
            }
        } 
        $apply_message = _('configures have been changed and need to be applied in order to make the changes active!');
        save_config_file(\@current,$filename);
        undef (%cgiparams);
    }
    if ($cgiparams{'ACTION'} eq 'on') {
        @current[$cgiparams{'KEY1'}] =~s/,on$/,/;
        $apply_message = _('configures have been changed and need to be applied in order to make the changes active!');
        save_config_file(\@current,$filename);
        &log(_('hosts config changed'));
        undef (%cgiparams); 
    }
    if ($cgiparams{'ACTION'} eq 'off') {
        @current[$cgiparams{'KEY1'}] =~s/,$/,on/;
        $apply_message = _('configures have been changed and need to be applied in order to make the changes active!');
        save_config_file(\@current,$filename);
        &log(_('hosts config changed'));
        undef (%cgiparams); 
    }
    if($cgiparams{'ACTION'} eq 'apply') {
        $notemessage = '隧道内NAT规则应用成功!';
        system("rm $need");
        system("sudo /usr/local/bin/settunnelnat &>/dev/null");
   }
   if ($cgiparams{'ACTION'} eq 'remove'){
        delete$current[$cgiparams{'KEY1'}];
        save_config_file(\@current,$filename);
        `sudo fmodify $filename`;
        undef (%cgiparams);
        if(!(-e $need)){
            system("touch $need");
        }
        $apply_message = _('configures have been changed and need to be applied in order to make the changes active!');
      
    }
    open(FILE,$filename);
    @current = <FILE>;
    close(FILE);
}

###显示添加或编辑的函数主题
sub add_rules(){
    my %checked;
    print "<div align='left'>";
    if ($cgiparams{'ACTION'} eq 'edit'){
        my @temp = split(/\,/,@current[$cgiparams{'KEY1'}]);
        $cgiparams{'INIT_IP'} = $temp[0];
        $cgiparams{'PROXY_IP'} = $temp[1];
        $cgiparams{'LOG'} = $temp[2];
        $cgiparams{'ENABLED'} = $temp[3];
        if ($temp[2] =~ "on") {
            $checked{$cgiparams{'LOG'}} = "checked='checked'";
        }        
        if ($cgiparams{'ENABLED'} =~ "on") {
            $checked{$cgiparams{'ENABLED'}} = "checked='checked'";
        }
    } 
    my $show = "";
    my @errormessages = ();
    my $title = "添加规则";
    $buttontext = $cgiparams{'ACTION'} eq 'edit' || $cgiparams{'KEY1'} ne '' ? "编辑规则": "添加规则";

    if($cgiparams{'ACTION'} eq 'edit' || $errormessage ne '') {
        $show = "showeditor";
        $action = "edit";
        $title = "编辑规则";
    }

&openeditorbox($title, "", $show, "createrule", @errormessages);

printf <<END
    </form>
    <form name="HOST_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
        <table cellpadding="0" cellspacing="0" border="0">
         <tr class="odd">
         <td class="add-div-type">  
                    %s *
         </td>
         <td>
            <input type='text' name='INIT_IP' value='$cgiparams{'INIT_IP'}' size='25' tabindex='1' ></span>
         </td>
         </tr>
         <tr class="env">
         <td  class="add-div-type">
                   %s *
        </td>
         <td>
                <input type='text' name='PROXY_IP' value='$cgiparams{'PROXY_IP'}' size='25' tabindex='2' >
       </td>
       </tr>
       <tr class="env">
         <td  class="add-div-type">
                   %s 
        </td>
         <td>
                <input type='checkbox' name='LOG' $checked{$cgiparams{'LOG'}} tabindex='4' >
       </td>
       </tr>
       <tr class="env">
       <td class="add-div-type"> 
                   %s
        </td>
        <td>
                <input type='checkbox' name='ENABLED' $checked{$cgiparams{'ENABLED'}} tabindex='4' >

            </td>
</tr>
            
                <input type='hidden' name='ACTION' value='$action' />
                <input type='hidden' name='SURE' value='y' />
                <input type='hidden' name='current' value='$cgiparams{'PROXY_IP'}' />
                <input type='hidden' name='KEY1' value='$cgiparams{'KEY1'}' >
</table>
END
,
_('原子网网段'),
_('代理子网网段'),
_('日志'),
_('启用'),
;
}
###显示规则的函数
sub display_rules(){
    printf <<END
    <table class="ruleslist" cellpadding="0" cellspacing="0" width="100%">
        <tr>
        <td class="boldbase">%s</td>
        <td class="boldbase">%s</td>
        <td class="boldbase">%s</td>
        </tr>
END
,
_('原子网网段'),
_('代理子网网段'),
_("Actions")
;
my $length = @current;
my $enabled = "on";
my $enabled_gif = $ON_PNG;
my $key = 0;
if($length > 0){
    foreach my $line (@current){
        chomp($line);
        my @temp = split(/\,/,$line);

        if ($cgiparams{'KEY1'} eq $key) {
            print "<tr class='selected'>\n";
        } 
        elsif ($key % 2) {
            print "<tr class='even'>\n";
        } 
        else {
            print "<tr class='oodd'>\n";
        }
        if (!$temp[3]) {            
            $enabled = "off";
            $enabled_gif = $OFF_PNG;
            $note = "点击启用";
        }
        else{
            $enabled = "on";
            $enabled_gif = $ON_PNG;
            $note = "点击禁止";
        }
    print "<td>$temp[0]</td>\n";
    print "<td>$temp[1]</td>\n";
    printf <<END
<td align='center' class="actions">
    <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
        <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" title="$note" />
        <input type="hidden" name="ACTION" value="$enabled">
        <input type='hidden' name='KEY1' value='$key' />
            </form>
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='hidden' name='ACTION' value='edit' />
        <input class='imagebutton' type='image' name='submit' src='$EDIT_PNG' alt='%s' title='%s' />
        <input type='hidden' name='KEY1' value='$key' />
    </form>
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='hidden' name='ACTION' value='remove' />
        <input class='imagebutton' type='image' name='submit' src='$DELETE_PNG' alt='%s' title='%s' />
        <input type='hidden' name='KEY1' value='$key' />
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
    print "</table>";
}else{
    no_tr(4,_('Current no content'));
    print "</table>";
}


if($key > 0)
 {
 printf <<END
  <table class="list-legend" cellpadding="0" cellspacing="0">
    <tr>
    <td colspan="4"><b>%s</b><img src='/images/edit.png' alt='%s' >%s<img src='/images/delete.png' alt='%s' >%s</td>
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
print "</table>";
print "</div>\n";
}
###表单检测函数
sub check_form(){
  printf <<EOF
  <script>
  var check = new ChinArk_forms();
  var object = {
       'form_name':'HOST_FORM',
       'option'   :{
            'INIT_IP':{
                'type':'text',
                'required':'1',
                'check':'ip_mask|'
            },
            'PROXY_IP':{
                'type':'text',
                'required':'1',
                'check':'ip_mask|'
            },
            'LOG':{
                    'type':'text',
                    'required':'0',
                    'check':'note|'
                }
            }
        }
  check._main(object);
  //check._get_form_obj_table("HOST_FORM");
  </script>
EOF
;
}