#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 计划中的备份页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
# MODEFIED BY:Liu Julong 2015/03/06
#===============================================================================

# -------------------------------------------------------------
# some definitions
# -------------------------------------------------------------
require '/var/efw/header.pl';
my $conffile          = "${swroot}/backup/settings";
my $conffile_default  = "${swroot}/backup/default/settings";
my $restart           = '/usr/local/bin/restartbackup';
my $cmd_judgeCF       = 'sudo /usr/local/bin/Judge_CF_Sata.sh';
my $cmd_checkCF       = 'sudo /usr/local/bin/Check_CF_Sata.sh';
my $sendmail          = '/usr/local/bin/sendautobackup';
my %checked           = ( 0 => '', 1 => 'checked', 'on' => 'checked' );
my %frequency         = ('hourly' => '', 'daily' => '', 'weekly' => '', 'monthly' => '');

my $name = _('Scheduled automatic backups');
my $errormessage='';

my %confhash = ();
my $conf = \%confhash;
my %par;

my $logid = 'backupschedule.cgi';
my $is_hidden = "style='display:none;'";

##################周圆 2011-09-27 添加帮助信息##############

my $help_hash1 = read_json("/home/httpd/help/backupschedule_help.json","backupschedule.cgi","系统-备份-备份计划-保留存档","-10","10","down");

my $help_hash2 = read_json("/home/httpd/help/backupschedule_help.json","backupschedule.cgi","系统-备份-备份计划-备份配置-包含日志文件","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/backupschedule_help.json","backupschedule.cgi","系统-备份-备份计划-备份配置-包含日志档案","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/backupschedule_help.json","backupschedule.cgi","系统-备份-备份计划-自动备份的时间表","-10","10","down");

my $help_hash5 = read_json("/home/httpd/help/backupschedule_help.json","backupschedule.cgi","系统-备份-备份计划-通过电子邮件发送备份文件-接收者电子邮件地址","-10","10","down");

my $help_hash6 = read_json("/home/httpd/help/backupschedule_help.json","backupschedule.cgi","系统-备份-备份计划-通过电子邮件发送备份文件-发送者电子邮件地址","-10","10","down");

my $help_hash7 = read_json("/home/httpd/help/backupschedule_help.json","backupschedule.cgi","系统-备份-备份计划-通过电子邮件发送备份文件-智能主机被使用","-10","10","down");


my $help_hash8 = read_json("/home/httpd/help/backupschedule_help.json","backupschedule.cgi","系统-备份-备份计划-通过电子邮件发送备份文件-启用","-10","10","down");

############################################################
&validateUser();

sub setfrequency() {
    $frequency{'hourly'} = '';
    $frequency{'daily'} = '';
    $frequency{'weekly'} = '';
    $frequency{'monthly'} = '';
    $frequency{$conf->{'BACKUP_SCHEDULE'}} = 'checked="checked"';
}

sub loadconfig() {
    my $count = 0;
    if (-e $conffile_default) {
      readhash($conffile_default, $conf);
      $count = 1;
    }
    if (-e $conffile) {
      readhash($conffile, $conf);
      $count = 1;
    }
    if($count eq 0)
    {
        $conf->{'BACKUP_ENABLED'} = "";
    }
    
    if($conf->{'BACKUP_MAIL'} eq "on")
    {
        $is_hidden = "style='display:table-row;'";
    }else{
        $is_hidden = "style='display:none;'";
    }
    
    setfrequency();
}

# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------

sub save() {
    #$conf->{'BACKUP_ENABLED'} = "on";
    #writehash($conffile, $conf);
    if ($par{'BACKUP_RETENTION'} !~ /^\d+$/) {
        $errormessage = _('Retention value need to be a number!');
        return;
    }
    
    #modified at 2015.06.04
    # if (($par{'BACKUP_LOGS'} !~ /on/) && ($par{'BACKUP_SETTINGS'} !~ /on/) && ($par{'BACKUP_LOGARCHIVES'} !~ /on/)) {
        # $errormessage = _('Include at least something to backup!');
        # return;
    # }
    
    if (($par{'BACKUP_SETTINGS'} !~ /on/)) {
        $errormessage = _('Include at least something to backup!');
        return;
    }

    if ($par{'BACKUP_MAIL'} =~ /on/) {
        if ($par{'BACKUP_RCPTTO'} =~ /^$/) {
            $errormessage = _('Recipient email address is required!');
            return;
        }
        # if ($par{'BACKUP_MAILFROM'} =~ /^$/) {
            # $errormessage = "发送者电子邮件地址不能为空!";
            # return;
        # }
        if (! validemail($par{'BACKUP_RCPTTO'})) {
            $errormessage = _('"%s" is no valid email address!', $par{'BACKUP_RCPTTO'});
            return;
        }
        # if ($par{'BACKUP_MAILFROM'} !~ /^$/) {
            # if (! validemail($par{'BACKUP_MAILFROM'})) {
                # $errormessage = _('"%s" is no valid email address!', $par{'BACKUP_MAILFROM'});
                # return;
            # }
        # }
        if ($par{'BACKUP_SMARTHOST'} !~ /^$/) {
        if (!validhostname($par{'BACKUP_SMARTHOST'}) && 
        !validfqdn($par{'BACKUP_SMARTHOST'}) && 
        !is_ipaddress($par{'BACKUP_SMARTHOST'})) 
        {
                $errormessage = _('Smarthost "%s" is no valid hostname or IP address!', $par{'BACKUP_SMARTHOST'});
                return;
            }
        }
        #$par{'BACKUP_LOGARCHIVES'} = 'off';
        $is_hidden = "style='display:table-row;'";
    }else{
        $is_hidden = "style='display:none;'";
    }

        #print STDERR "$logid: writing new configuration file\n";
    $needrestart = 1;
    $conf->{'BACKUP_ENABLED'} = $par{'ENABLED'};
    $conf->{'BACKUP_SCHEDULE'} = $par{'BACKUP_SCHEDULE'};
    $conf->{'BACKUP_LOGS'} = $par{'BACKUP_LOGS'};
    $conf->{'BACKUP_SETTINGS'} = $par{'BACKUP_SETTINGS'};
    $conf->{'BACKUP_IPS'} = $par{'BACKUP_IPS'};
    $conf->{'BACKUP_LOGARCHIVES'} = $par{'BACKUP_LOGARCHIVES'};
    $conf->{'BACKUP_DBDUMP'} = $par{'BACKUP_DBDUMP'};
    $conf->{'BACKUP_RETENTION'} = $par{'BACKUP_RETENTION'};
    $conf->{'BACKUP_MAIL'} = $par{'BACKUP_MAIL'};
    if($par{'BACKUP_MAIL'} eq 'on')
    {
        $conf->{'BACKUP_RCPTTO'} = $par{'BACKUP_RCPTTO'};
    }else{
        $conf->{'BACKUP_RCPTTO'} = "";
    }
    $conf->{'BACKUP_MAILFROM'} = $par{'BACKUP_MAILFROM'};
    $conf->{'BACKUP_SMARTHOST'} = $par{'BACKUP_SMARTHOST'};
    setfrequency();
    writehash($conffile, $conf);
    `sudo fmodify $conffile`;
    $notemessage = "备份策略配置成功！";
    if ($needrestart) {
        system("$cmd_judgeCF");
        if($? >> 8 == 5){
            $notemessage = '备份数目最大限制为5，系统可能不会完成自动备份';
            return;
        }else{
            system($restart);
        }
    }
    if ($par{'SENDNOW'} !~ /^$/) {
        system($sendmail);
        `sudo fcmd $sendmail`;
        $notemessage = _('成功发送备份信息');
    }
    %par = ();
}

sub display() {

my $service_status = $conf->{'BACKUP_ENABLED'};
#openbox('100%', 'left', $name);
printf <<END
<script type="text/javascript">
    \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('/cgi-bin/backupschedule.cgi', SERVICE_STAT_DESCRIPTION);
    });
</script>
<form enctype='multipart/form-data' method='post' class="service-switch-form" id="access-form" action='$ENV{SCRIPT_NAME}'>
<input type="hidden" class="service-status" name="ENABLED" value="$service_status" />
<table>
    <tr>
        <td valign="top">
            <div id="access-policy" class="service-switch">
                <div><span class="title">%s</span>
                    <span class="image"><img class="$service_status" align="absbottom" src="/images/switch-%s.png" alt="" border="0"/></span>
                </div>
                    <div id="access-description" class="description" %s>%s</div>
                    <div id="access-policy-hold" class="spinner working">%s</div>
                    <br/>
                    <div id="access-options" class="options-container" %s>
                    


<table style="border:1px solid #999;" id="tables">
  <tr class="env">
    <td style="width:180px;"  class="add-div-width need_help" rowspan="1">%s $help_hash1</td>
    <td colspan="4">
      <select name='BACKUP_RETENTION'>
END
, escape_quotes(_("The backup server configuration is being applied. Please hold...")),
escape_quotes(_("The backup server is being shutdown. Please hold...")),
escape_quotes(_("Settings are saved and the backup server is being restarted. Please hold...")),
_('启用自动定期备份'),
$conf->{'BACKUP_ENABLED'} eq 'on' ? 'on' : 'off',
$conf->{'BACKUP_ENABLED'} eq 'on' ? 'style="display:none"' : '',
 _("Use the switch above to enable the backup server."),
'',
$conf->{'BACKUP_ENABLED'} eq 'on' ? '' : 'style="display:none"',
, _('保留最近备份数')
;

    my @entries = qw '2 3 4 5 6 7 8 9 10';
    system("$cmd_checkCF");
    if($? >> 8 == 1){
        @entries = qw '1 2';
    }
    foreach my $entry (@entries) {
    my $selected = '';
    if ($entry eq $conf->{'BACKUP_RETENTION'}) {
        $selected = 'selected';
    }
    print "<option $selected value=\"$entry\">$entry</option>";
    }

    printf <<END
        </select>
    </td>
  </tr>

 <tr class="odd">
    <td class="add-div-width" rowspan="2">%s</td>
    <td width="150px">%s</td>
    <td colspan="4">
      <input type='checkbox' name='BACKUP_SETTINGS' value='on' $checked{$conf->{'BACKUP_SETTINGS'}} />
      <input class="hidden_class"  type='checkbox' name='BACKUP_DBDUMP' value='on'  />
    </td>
  </tr>
  
  <!--新增规则库配置 -->
  <tr class="odd">
    <td width="150px" class="need_help">包含规则库</td>
    <td colspan="4">
      <input type='checkbox' name='BACKUP_IPS' id="rulelib" value='on' $checked{$conf->{'BACKUP_IPS'}} />
    </td>
  </tr>
  
  <!--<tr class="odd ">
    <td width="150px" class="need_help">%s $help_hash2</td>
    <td colspan="4">
      <input type='checkbox' name='BACKUP_LOGS' value='on' $checked{$conf->{'BACKUP_LOGS'}} />
    </td>
  </tr>
  <tr class="odd">
    <td width="150px" class="need_help">%s $help_hash3</td>
    <td colspan="4">
      <input type='checkbox' name='BACKUP_LOGARCHIVES' id="logarchive" value='on' $checked{$conf->{'BACKUP_LOGARCHIVES'}} />
    </td>
  </tr>-->
  

  <tr class="env">
    <td class="add-div-width need_help" rowspan="1"><b>%s</b> $help_hash4</td>
    <td><input type="radio" name="BACKUP_SCHEDULE" $frequency{'hourly'} value="hourly"> %s </td>
    <td><input type="radio" name="BACKUP_SCHEDULE" $frequency{'daily'} value="daily"> %s </td>
    <td><input type="radio" name="BACKUP_SCHEDULE" $frequency{'weekly'} value="weekly"> %s </td>
    <td><input type="radio" name="BACKUP_SCHEDULE" $frequency{'monthly'} value="monthly"> %s</td>
  </tr>

END
, _('backup config')
, _('Include configuration')
, _('Include log files')
, _('Include log archives')
, _('Schedule for automatic backups')
, _('Hourly')
#, _('Daily')
, _('每天')
, _('Weekly')
, _('Monthly')
;

printf <<END
  <tr class="odd">
    <td class="add-div-width">%s</td>
    <td colspan="4" >
      <input type='checkbox' style='margin-bottom:10px;' name='BACKUP_MAIL' id='mail_backup' $checked{$conf->{'BACKUP_MAIL'}}/> %s
      
      <ul id="mail_item0"  $is_hidden width="100%" >
        <li style='float:left;'><input type="button" class="net_button" value="设置发送者邮件地址" onclick="parent.window.document.getElementById('rightFrame').src='idps_email_alarm.cgi';"/></li>
        <li style='float:left;'>%s <input type='text' name='BACKUP_RCPTTO' value='$conf->{'BACKUP_RCPTTO'}' style='display:inline-block;' /></li>
        <!--<li style='float:left;'>%s *<input type='text' name='BACKUP_MAILFROM' value='$conf->{'BACKUP_MAILFROM'}' style='display:inline-block' />
        </li>
        <li style='float:left;'>%s <input type='text' name='BACKUP_SMARTHOST' value='$conf->{'BACKUP_SMARTHOST'}' style='display:inline-block'/></li>-->
      </ul>
    </td>
  </tr>
</table>
<table ">
  <tr class="add-div-footer" >
    <td colspan="2" >
      <input type='hidden' name='ACTION' value='save' />
      <input class='net_button' type='submit' name='SUBMIT' value='%s' onclick="\$('.service-switch-form').unbind('submit');" />
    </td>
    <td colspan="3" >
      <input id="mail_item4" class='net_button mail_item' $is_hidden  type='submit' name='SENDNOW' value='%s' onclick="\$('.service-switch-form').unbind('submit');" />
    </td>
  </tr>
</table>
</div>
        </div>
        </td>
    </tr>
</table>
  
</form>
END
, _('Send backups via email')
, _('Enabled')
#, _('email address of recipient')
, _('接收者电子邮件地址：')
, _('email address of sender')
, _('邮件中继主机地址')
, _('Save')
#, _('Send a backup now')
, _('立即备份与发送')
;

    #closebox();

}

# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------
getcgihash(\%par);
showhttpheaders();
loadconfig();
#print "haha1:".$is_hidden;
if (!defined($conf)) {
  $erromessage = _('Cannot read configuration!');
}

my $extraheader = '<script type="text/javascript">
function check_email(){
   var obj1 = document.getElementById("logarchive");
   var obj2 = document.getElementById("mail_backup");
   if((obj1.checked)&& (obj2.checked))
   {
     alert("由于当前配置包括历史档案，可能会造成邮件过大而无法发送，所以不会定时发送到指定邮箱，如需要备份文件，请到【备份恢复】页面下载该备份文件!");
     obj2.checked=false;
   }
}
</script>
<script type="text/javascript" src="/include/serviceswitch.js"></script>
<script type="text/javascript" src="/include/backupschedule.js"></script>
<style type="text/css"> #mail_item4 { width: 120px; } </style>
';
openpage($name, 1, $extraheader);

if ($par{'ACTION'} eq 'save') {
    if($par{'ENABLED'} eq 'off')
    {
        $par{'ENABLED'} = "";
    }
    $conf->{'BACKUP_ENABLED'} = $par{'ENABLED'};
    writehash($conffile,$conf);
    # added by xqy 2013-12-16: run $restart to stop autobackup
    if($par{'ENABLED'} eq '')
    {
        system($restart);
    }
    save();
}
&openbigbox($errormessage, $warnmessage, $notemessage);
display();
closebigbox();
closepage();

