#!/usr/bin/perl
#
# IPCop CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The IPCop Team
#
# $Id: config.dat,v 1.2.2.3 2004/03/13 12:53:58 eoberlander Exp $
#

require '/var/efw/header.pl';
my (%logsettings, %checked, %selected, $errormessage, %outgoingsettings, %par);

&showhttpheaders();

$logsettings{'LOGVIEW_SIZE'} = $viewsize;
$logsettings{'LOG_KEEP'} = '56';

$logsettings{'LOG_MAX_PERCENT'} = '75';


$logsettings{'ENABLE_REMOTELOG'} = 'off';
$logsettings{'REMOTELOG_ADDR'} = '';
$logsettings{'ACTION'} = '';

$logsettings{'LOG_BADTCP'} = 'off';
$logsettings{'LOG_NEWNOTSYN'} = 'off';
$logsettings{'LOG_DROPS'} = 'off';

$outgoingfw{'LOG_ACCEPTS'} = 'off';
$cmd = "/usr/local/bin/padding_log";
####获取日志磁盘大小
my $disk_size = `/bin/df -h | /bin/grep local-log`;
my @disk_temp = split(/\s+/,$disk_size);
# | /bin/sed "s/ \{2,\}/ /g" | /bin/cut -d " " -f2`; 
#{}&> /tmp/disk_size');
# $disk_size = `cat /tmp/disk_size; rm -f /tmp/disk_size`;
# $disk_size =~ s/[\r\n]$//;
# $disk_size =~ s/G//;
# $logsettings{'LOG_MAX_CAPACITY'} = $disk_size;

&getcgihash(\%par);
sub check_form(){
    printf <<EOF
    <script>
    var ass_url = "/cgi-bin/logs_config.cgi";

    var message_box_config = {
      url: ass_url,
      check_in_id: "mesg_box",
      panel_name: "mesg_box",
    }

    \$(document).ready(function(){
      message_manager.render();

    })
    var object = {
        'form_name':'LOGS_FORM',
        'option'   :{
                    /*'LOGVIEW_SIZE':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var viewsize = eve._getCURElementsByName("LOGVIEW_SIZE","input","LOGS_FORM")[0].value;
                                                        if (viewsize > 2000) {
                                                            msg = "请输入1-2000之间的整数";
                                                        }
                                                        return msg;
                                                     }
                             },*/
                    'LOG_KEEP':{
                               'type':'text',
                               'required':'1',
                               'check':'num|'
                             },
                    'REMOTELOG_ADDR':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'RECVMAIL':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|'
                             },
                    'RECIVER_NAME':{
                               'type':'text',
                               'required':'0',
                               'check':'specify_name-2|'
                             },
                    'SENDER_ADDR':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|'
                             },
                    'SENDER_NAME':{
                               'type':'text',
                               'required':'0',
                               'check':'specify_name-2|'
                             },
                    'SUBJECT':{
                               'type':'text',
                               'required':'0',
                               'check':'other|',
                               'other_reg':'/.*/'
                             },
                    'ACCOUNT':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/.*/'
                             },
                    'PASSWORD':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/.*/'
                             },
                    'LOG_MAX_PERCENT':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var max = eve._getCURElementsByName("LOG_MAX_PERCENT","input","LOGS_FORM")[0].value;
                                                        //var disk = eve._getCURElementsByName("disk_size","input","LOGS_FORM")[0].value;
                                                        //disk = parseInt(disk);
                                                        if (max > 100 || max < 25) {
                                                            msg = "请输入25-"+100+"之间的整数";
                                                        }
                                                         return msg;
                                                     }
                             },                    
                    'LOGDISKPERCENT':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var max = eve._getCURElementsByName("LOGDISKPERCENT","input","LOGS_FORM")[0].value;
                                                        max = parseInt(max);
                                                        if (max > 99 || max < 1) {
                                                            msg = "请输入1-99之间的整数";
                                                        }
                                                        return msg;
                                                     }
                             }
                 }
         }
	
    var check = new ChinArk_forms();
    check._main(object);
    var message_manager = new MessageManager( message_box_config );
    </script>
EOF
;
}
if (-f "${swroot}/logging/settings") {
    &readhash("${swroot}/logging/settings", \%logsettings);
}
if (-f "${swroot}/outgoing/settings") {
    &readhash("${swroot}/outgoing/settings", \%outgoingsettings);
}
=p
if($par{'ACTION'} eq 'delete'){
    system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl all_logs");
    my $log_message = "清空日志文件";
    &user_log($log_message);
    $notemessage = "日志文件已清空!";
}
=cut
if ($par{'ACTION'} eq 'save')
{

  unless ($par{'LOG_KEEP'} =~ /^\d+$/)
  {
    $errormessage = _('Keep time must be a valid number');
  }
  
   unless ($par{'LOG_MAX_PERCENT'} =~ /^\d+$/ && $par{'LOG_MAX_PERCENT'}<=100 && $par{'LOG_MAX_PERCENT'}>=25)
  {
    $errormessage = '日志阈值请填写25-100之间的整数.';
  }
  
  
  
  # unless ($par{'LOGVIEW_SIZE'} =~ /^(\d+)$/ && $1>0)
  # {
  #   $errormessage = _('Number of lines must be a valid number');
  # }
  # if ($par{'LOGVIEW_SIZE'} > 2000) {
  #      $errormessage = "每页显示行数应为1-2000！";
  # }
  # if (($par{'LOG_MAX_CAPACITY'} !~ /[1-9][1-9]*/) || $par{'LOG_MAX_CAPACITY'} > $disk_size || $par{'LOG_MAX_CAPACITY'} < 1) {
	 #   $errormessage = "请设置正确的日志空间！";
  # }#else{
	   # my $bNum = ( $disk_size - $par{'LOG_MAX_CAPACITY'} )*1024*1024*1024;
	  
	   # `sudo $cmd setmem $bNum > /tmp/logs_config_result`;
	   # my @flag = &read_conf_file("/tmp/logs_config_result");
	   # system("rm -f /tmp/logs_config_result");
	   # my $flag = $flag[0];
	   # if($flag ne 'OK') {
		   # $errormessage = "设置日志空间失败！";
	   # }
  # }
  

  
  unless ($errormessage) {
	
    #$logsettings{'LOGVIEW_REVERSE'} = $par{'LOGVIEW_REVERSE'};
    $logsettings{'LOGVIEW_SIZE'} = $par{'LOGVIEW_SIZE'};
    #$logsettings{'LOGWATCH_LEVEL'} = $par{'LOGWATCH_LEVEL'};
    $logsettings{'LOG_KEEP'} = $par{'LOG_KEEP'};
    $logsettings{'LOG_MAX_PERCENT'} = $par{'LOG_MAX_PERCENT'};
    $outgoingsettings{'LOG_ACCEPTS'} = $par{'LOG_ACCEPTS'};

    $logsettings{'LOG_BADTCP'} = $par{'LOG_BADTCP'};
    $logsettings{'PORTSCAN'} = $par{'PORTSCAN'};
    $logsettings{'LOG_NEWNOTSYN'} = $par{'LOG_NEWNOTSYN'};
    $logsettings{'LOG_DROPS'} = $par{'LOG_DROPS'};
    $logsettings{'LOGMAIL'} = $par{'LOGMAIL'};    
    $logsettings{'RECVMAIL'} = $par{'RECVMAIL'};  
    $logsettings{'LOGDISKPERCENT'} = $par{'LOGDISKPERCENT'};
    $logsettings{'DISKNOFREE'} = $par{'DISKNOFREE'};
    $logsettings{'REMOTELOG_ADDR'} = $par{'REMOTELOG_ADDR'};
    $logsettings{'ENABLE_REMOTELOG'} = $par{'ENABLE_REMOTELOG'};
	$logsettings{'LOG_MAX_CAPACITY'} = $par{'LOG_MAX_CAPACITY'};

    #====2014.06.24 发邮件新增字段 by wl====#
    $logsettings{'RECIVER_NAME'}  = $par{'RECIVER_NAME'};
    $logsettings{'SENDER_ADDR'}   = $par{'SENDER_ADDR'};
    $logsettings{'SENDER_NAME'}   = $par{'SENDER_NAME'};
    $logsettings{'SUBJECT'}       = $par{'SUBJECT'};
    $logsettings{'ACCOUNT'}       = $par{'ACCOUNT'};
    $logsettings{'PASSWORD'}      = $par{'PASSWORD'};
    $logsettings{'ENABLE_SSL'}    = $par{'ENABLE_SSL'};

    &writehash("${swroot}/logging/settings", \%logsettings);
    &writehash("${swroot}/outgoing/settings", \%outgoingsettings);
    `sudo fmodify "${swroot}/logging/settings"`;
    `sudo fmodify "${swroot}/outgoing/settings"`;
	
    $notemessage = "审计配置保存成功!";
    my $new_value = "$par{'LOG_BADTCP'},$par{'LOG_NEWNOTSYN'},$par{'LOG_ACCEPTS'},$par{'LOG_DROPS'},$par{'PORTSCAN'}";
    # 当前 防火墙日志记录 功能处于屏蔽状态，所以此处日志记录也屏蔽
    # my $log_message = changes_log($par{'old_value'},$new_value);
    # if ($log_message) {        
    #     &user_log($log_message);
    # }
    system('/usr/local/bin/restartsyslog >/dev/null ') == 0
      or $errormessage = _('Helper program returned error code')." " . $?/256;
    system('sudo /etc/rc.d/rc.firewall reload >/dev/null') == 0
      or $errormessage = _('Helper program returned error code')." " . $?/256;
    system('/usr/local/bin/restartsnmp -f >/dev/null') == 0
      or $errormessage = _('Helper program returned error code')." " . $?/256;
    system('sudo /usr/local/bin/setoutgoing.py >/dev/null') == 0
      or $errormessage = _('Helper program returned error code')." " . $?/256;

  }

}

if (-f "${swroot}/logging/settings") {
    &readhash("${swroot}/logging/settings", \%logsettings);
}
if (-f "${swroot}/outgoing/settings") {
    &readhash("${swroot}/outgoing/settings", \%outgoingsettings);
}

$checked{'LOG_ACCEPTS'}{'off'} = '';
$checked{'LOG_ACCEPTS'}{'on'} = '';
$checked{'LOG_ACCEPTS'}{$outgoingsettings{'LOG_ACCEPTS'}} = "checked='checked'";

$checked{'LOG_BADTCP'}{'off'} = '';
$checked{'LOG_BADTCP'}{'on'} = '';
$checked{'LOG_BADTCP'}{$logsettings{'LOG_BADTCP'}} = "checked='checked'";

$checked{'LOG_NEWNOTSYN'}{'off'} = '';
$checked{'LOG_NEWNOTSYN'}{'on'} = '';
$checked{'LOG_NEWNOTSYN'}{$logsettings{'LOG_NEWNOTSYN'}} = "checked='checked'";

$checked{'ENABLE_REMOTELOG'}{'off'} = '';
$checked{'ENABLE_REMOTELOG'}{'on'} = '';
$checked{'ENABLE_REMOTELOG'}{$logsettings{'ENABLE_REMOTELOG'}} = "checked='checked'";

$checked{'ENABLE_SSL'}{'off'} = '';
$checked{'ENABLE_SSL'}{'on'} = '';
$checked{'ENABLE_SSL'}{$logsettings{'ENABLE_SSL'}} = "checked='checked'";

$checked{'LOGMAIL'}{'off'} = '';
$checked{'LOGMAIL'}{'on'} = '';
$checked{'LOGMAIL'}{$logsettings{'LOGMAIL'}} = "checked='checked'";

$checked{'PORTSCAN'}{'off'} = '';
$checked{'PORTSCAN'}{'on'} = '';
$checked{'PORTSCAN'}{$logsettings{'PORTSCAN'}} = "checked='checked'";

$checked{'LOG_DROPS'}{'off'} = '';
$checked{'LOG_DROPS'}{'on'} = '';
$checked{'LOG_DROPS'}{$logsettings{'LOG_DROPS'}} = "checked='checked'";
$selected{$logsettings{'DISKNOFREE'}} = "selected";
my $old_value = "$logsettings{'LOG_BADTCP'},$logsettings{'LOG_NEWNOTSYN'},$outgoingsettings{'LOG_ACCEPTS'},$logsettings{'LOG_DROPS'},$logsettings{'PORTSCAN'}";
my $help_hash1 = read_json("/home/httpd/help/logs_help.json","logs_config.cgi","日志-设定-日志选项-日志查看选项-显示数字行","-10","30","down");
my $help_hash2 = read_json("/home/httpd/help/logs_help.json","logs_config.cgi","日志-设定-日志选项-防火墙日志记录","-10","30","down");
my $help_hash3 = read_json("/home/httpd/help/logs_help.json","logs_config.cgi","日志-设定-日志选项-日志管理-日志保留天数","-10","30","down");
my $display = "style='display:none;'";
my $colspan = "colspan='2'";
if ($checked{'ENABLE_REMOTELOG'}{'on'} eq "checked='checked'") {
    $display = "style='display:table-cell;'";
  $colspan = "colspan='1'";
}

&openpage(_('Log settings'), 1, '<script type="text/javascript" src="/include/jsencrypt.min.js"></script><link rel="stylesheet" type="text/css" href="/include/add_list_base.css" /><script type="text/javascript" src="/include/logs_delete.js"></script><script language="JavaScript" src="/include/message_manager.js"></script><script type="text/javascript" src="/include/logs_config.js"></script><script type="text/javascript" src="/include/jquery.md5.js"></script>');

&openbigbox($errormessage, $warnmessage, $notemessage);
printf <<EOF
    <div id="mesg_box" class="container"></div>
EOF
  ;


&openbox('100%', 'left', _('Log options'));
printf <<END

<form enctype='multipart/form-data' name="LOGS_FORM" method='post' action='$ENV{'SCRIPT_NAME'}'>
    <table >
   <input type='hidden' name='ACTION' value='save' />
    <!--<tr class="env">
     <td class="add-div-type need_help">%s $help_hash1</td>
     <td width="25%">%s *</td>
     <td><input type='text' name='LOGVIEW_SIZE' size="5" value="$logsettings{'LOGVIEW_SIZE'}" style="width:124px" /><input type='hidden' name='old_value' value="$old_value" /></td>
     </tr>-->
      <tr class="odd hidden">
        <td class="add-div-type need_help" rowspan="3">%s $help_hash2</td>
        <td>%s</td>
        <td><input type='checkbox' name='LOG_BADTCP' value='on' $checked{'LOG_BADTCP'}{'on'} /></td>
      </tr>
      <tr class="env hidden">
        <td>%s</td>
        <td><input type='checkbox' name='LOG_NEWNOTSYN' value='on' $checked{'LOG_NEWNOTSYN'}{'on'} /></td>
      </tr>
      <tr class="odd hidden">
        <td>%s</td>
        <td><input type='checkbox' name='LOG_ACCEPTS' value='on' $checked{'LOG_ACCEPTS'}{'on'} /></td>
      </tr>
      <tr class="env hidden">
        <td>%s</td>
        <td><input type='checkbox' name='LOG_DROPS' value='on' $checked{'LOG_DROPS'}{'on'} /></td>
      </tr>    
    <tr class="odd hidden">
    <td>记录端口扫描的包</td>
    <td><input type='checkbox' name='PORTSCAN' value='on' $checked{'PORTSCAN'}{'on'} /></td>
    </tr>
    
    
      <tr class="odd">
        <td class="add-div-type need_help" id="log_manage" rowspan="3">%s $help_hash3</td>
        <td >%s *</td>
        <td><input type='text' name='LOG_KEEP' value='$logsettings{'LOG_KEEP'}' maxlength='3' size='4' style="width:124px"/></td>
      </tr>
      <tr class="env">
        <td>日志阈值(容量<span>$disk_temp[1]</span>) *</td>
        <td><input type='text' class="hidden_class" name='disk_size' value='$logsettings{'LOG_MAX_PERCENT'}' size='4' /> <input type='text' name='LOG_MAX_PERCENT' value='$logsettings{'LOG_MAX_PERCENT'}' size='4' style="width:124px"/> %</td>
      </tr>
      <tr class="env">
        <td>达到日志阈值时执行</td>
        <td><select name="DISKNOFREE" >
            <option $selected{'on'} value="on">自动删除最早日志</option>
            <option $selected{'off'} value="off">不记录新日志</option>
        </select></td>
      </tr>
    <tr class="env">
    <td class = "add-div-type">远程日志管理</td>
    <td id="colspaned" $colspan><input type='checkbox' id='ENABLE_REMOTELOG' name='ENABLE_REMOTELOG' value='on' $checked{'ENABLE_REMOTELOG'}{'on'} onclick='display_remote()'/></td>    
    <td id= "REMOTELOG_ADDR" $display>服务器地址 *<input type='text' name='REMOTELOG_ADDR' value='$logsettings{'REMOTELOG_ADDR'}'/></td>
    </tr>
      <tr class="table-footer">
        <td colspan="3"><input class='net_button' type='submit' name='SUBMIT' value='%s'/></td>
      </tr>

    </table>
      </form>
      <table >
       <input type='hidden' name='ACTION' value='delete' />
        <tr class="table-footer">
         <td colspan="3"><input class='net_button' type='submit' name='SUBMIT' onclick="warning_box('all_logs','所有')" value='清空日志'/></td>
        </tr>
        </table>


END
,
_('Log viewing options'),
_('每页显示行数'),
_('Firewall logging'),
_('Log packets with BAD constellation of TCP flags'),
_('记录不带SYN标志的包'),
_('记录所有接受的流出包'),
_('记录防火墙丢弃的包'),
_('Log manage'),
_('Log keep days'),
_('Save')
;
&closebox();

###结束
printf <<EOF

EOF
;
&closebigbox();
&check_form();
&closepage();


sub changes_log($$){
    my $old_value = shift;
    my $new_value = shift;
    my @old = split(/,/,$old_value);
    my @new = split(/,/,$new_value);
    my $message;
    if ($old[0] ne $new[0]) {
        if ($old[0] eq "on") {
            $message .= "关闭记录bad TCP包日志;";
        }
        else{
            $message .= "开启记录bad TCP包日志;";
        }
    }
    if ($old[1] ne $new[1]) {
        if ($old[1] eq "on") {
            $message .= "关闭记录不带SYN标志的包日志;";
        }
        else{
            $message .= "开启记录不带SYN标志的包日志;";
        }
    }
    if ($old[2] ne $new[2]) {
        if ($old[2] eq "on") {
            $message .= "关闭记录所有接受的流出包日志;";
        }
        else{
            $message .= "开启记录所有接受的流出包日志;";
        }
    }
    if ($old[3] ne $new[3]) {
        if ($old[3] eq "on") {
            $message .= "关闭记录防火墙拒绝的包日志;";
        }
        else{
            $message .= "开启记录防火墙拒绝的包日志;";
        }
    }
    if ($old[4] ne $new[4]) {
        if ($old[4] eq "on") {
            $message .= "关闭记录端口扫描的包日志;";
        }
        else{
            $message .= "开启记录端口扫描的包日志;";
        }
    }
    return $message;
}
