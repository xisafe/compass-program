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
my $filename = "${swroot}/dnsmasq/hosts";
my $need = "${swroot}/dnsmasq/needreload";
my $apply_message = "";
my $action = 'add';

&getcgihash(\%cgiparams);
&showhttpheaders(); 
###读取原来文件的内容
#open(FILE,$filename);
@current = read_file($filename);
#close(FILE);

&openpage(_('Hostname'), 1, '');
save();
if (-e $need) {
   $apply_message = _('configures have been changed and need to be applied in order to make the changes active!');
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
        unless(&validip($cgiparams{'IPADDR'})){
           push(@errormessages,_('Invalid fixed IP address'));
        }
        unless(&validhostname($cgiparams{'HOSTNAME'})){
           push(@errormessages,_('Invalid hostname.'));
        }
        if ($cgiparams{'DOMAINNAME'}){
          unless(&validdomainname($cgiparams{'DOMAINNAME'})){
             push(@errormessages,_('Invalid domain name.'));
          }
        }
        if($cgiparams{'ACTION'} eq 'add'){
            foreach my $line (@current) {
                chomp($line);
                my @tmp = split(/,/,$line);
                if (($tmp[2] eq $cgiparams{'HOSTNAME'}) && ($tmp[3] eq $cgiparams{'DOMAINNAME'}) && $cgiparams{'ACTION'} ne 'edit') {
                     push(@errormessages, _('Hostname and Domainname can not repeat at the same time!'));
                }
            }
        }
        if ($#errormessages eq -1){
            if ($cgiparams{'KEY1'} eq '') {
                push(@current, "on,$cgiparams{'IPADDR'},$cgiparams{'HOSTNAME'},$cgiparams{'DOMAINNAME'}");
                &log(_('hosts config added'));
            } 
            else {
                @current[$cgiparams{'KEY1'}] = "on,$cgiparams{'IPADDR'},$cgiparams{'HOSTNAME'},$cgiparams{'DOMAINNAME'}";
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
    if($cgiparams{'ACTION'} eq 'apply') {
        $notemessage = _('hosts config changed successfully!');
        system("rm $need");
        system("/usr/local/bin/restartdnsmasq &>/dev/null");
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
print "<div align='left'>";
if ($cgiparams{'ACTION'} eq 'edit'){
    my @temp = split(/\,/,@current[$cgiparams{'KEY1'}]);
    $cgiparams{'IPADDR'} = $temp[1];
    $cgiparams{'HOSTNAME'} = $temp[2];
    $cgiparams{'DOMAINNAME'} = $temp[3];
} 
my $show = "";
my @errormessages = ();
my $title = "添加主机";
$buttontext = $cgiparams{'ACTION'} eq 'edit' || $cgiparams{'KEY1'} ne '' ? _("编辑主机") : _("Add Host");

if($cgiparams{'ACTION'} eq 'edit' || $errormessage ne '') {
    $show = "showeditor";
    $action = "edit";
    $title = "编辑主机";
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
            <input type='text' name='IPADDR' value='$cgiparams{'IPADDR'}' size='25' tabindex='1' ></span>
         </td>
         </tr>
         <tr class="env">
         <td  class="add-div-type">
                   %s *
        </td>
         <td>
                <input type='text' name='HOSTNAME' value='$cgiparams{'HOSTNAME'}' size='25' tabindex='2' >
       </td>
       <tr class="odd">
       <td class="add-div-type"> 
                   %s
        </td>
        <td>
                <input type='text' name='DOMAINNAME' value='$cgiparams{'DOMAINNAME'}' size='25' tabindex='3' >
                <input type='hidden' name='ACTION' value='$action' />
                <input type='hidden' name='SURE' value='y' />
                <input type='hidden' name='current' value='$cgiparams{'HOSTNAME'}' />
                <input type='hidden' name='KEY1' value='$cgiparams{'KEY1'}' >

            </td>
</tr></table>
END
,
_('IP Address'),
_('Hostname'),
_('Domain name'),
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
        <td class="boldbase">%s</td>
        </tr>
END
,
_('Host IP address'),
_('Hostname'),
_('Domain name'),
_("Actions")
;
my $length = @current;

my $key = 0;
if($length > 0)
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
        print "<tr class='even'>\n";
    } else 
    {
        print "<tr class='oodd'>\n";
    }
    print "<td>$temp[1]</td>\n";
    print "<td>$temp[2]</td>\n";
    print "<td>$temp[3]</td>\n";
    printf <<END
<td align='center' class="actions">
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='hidden' name='ACTION' value='edit' />
        <input class='imagebutton' type='image' name='submit' src='/images/edit.png' alt='%s' title='%s' />
        <input type='hidden' name='KEY1' value='$key' />
    </form>
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='hidden' name='ACTION' value='remove' />
        <input class='imagebutton' type='image' name='submit' src='/images/delete.png' alt='%s' title='%s' />
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
                    'IPADDR':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'HOSTNAME':{
                               'type':'text',
                               'required':'1',
							   'check':'other|',
							   'other_reg':'/\.+/',
                               'ajax' : '1',
                               'ass_check':function(eve){
                                                      var msg=""; 
                                                      var key = 0;
                                                      var hostname = eve._getCURElementsByName("HOSTNAME","input","HOST_FORM")[0].value;
                                                      var current = eve._getCURElementsByName("current","input","HOST_FORM")[0].value;
                                                      var action = eve._getCURElementsByName("ACTION","input","HOST_FORM")[0].value;
													//检测主机名输入是否合法--2013.08.26 王琳
													var reg  = /^[a-zA-Z0-9]{1}[a-zA-Z0-9-]{0,61}[a-zA-Z0-9]{1}\$/;
													if(!reg.test(hostname)){
														return "主机名由2-63位字母、数字、短横线组成,并以字母、数字做开头、结尾,如h-t";
													}
													//END--王琳
                                                      hostname = hostname.replace(/(^\\s*)|(\\s*\$)/g,"");
                                                      if(!eve.datas){
                                                              \$.ajax({
                                                                  type : "get",
                                                                  url : '/cgi-bin/chinark_back_get.cgi',
                                                                  async : false,
                                                                  data : 'path=/var/efw/dnsmasq/hosts',
                                                                  success : function(data){ 
                                                                      eve.datas = data;                                                                     
                                                                  }
                                                                  });
                                                       }
                                                      var exist = eve.datas.split('\\n');
                                                      for (var i = 0; i < exist.length; i++) {
                                                           var tmp = exist[i].split(',');
                                                           if((tmp[2] == hostname) && (hostname != current)) {
                                                               key = 1;
                                                               break;
                                                           }
                                                      }
                                                      if(key){
                                                          msg = '主机名'+hostname+'已存在';
                                                      }
                                                      return msg;
                                                     }
                             },
                    'DOMAINNAME':{
                               'type':'text',
                               'required':'0',
                               'check':'domain|',
                             },
                 }
         }
  check._main(object);
  //check._get_form_obj_table("HOST_FORM");
  </script>
EOF
;
}