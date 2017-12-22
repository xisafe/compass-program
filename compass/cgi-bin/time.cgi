#!/usr/bin/perl
#
# IPCop CGIs
#
# This file is part of the IPCop Project
# 
# This code is distributed under the terms of the GPL
#
# (c) Eric Oberlander June 2002
#
# (c) Darren Critchley June 2003 - added real time clock setting, etc

require '/var/efw/header.pl';

my $conffile_default = '/var/efw/time/default/settings';
my $ntp_server      = '/var/efw/time/default/default_ntp_server';
my $ntp_conf        = '/etc/ntp/ntp.conf.tmpl';
my $conffile        = '/var/efw/time/settings';
my $enabled_file    = '/var/efw/time/enable';
my $mainsettings    = '/var/efw/main/settings';
my $enabled     = 0;
my %conf_hash   = ();
my $conf        = \%conf_hash;
my $restart     = '/usr/local/bin/restartntp';
my $sync        = '/usr/local/bin/restartntp --synchronize-now';
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked');
my $extraheader =  '<link rel="stylesheet" type="text/css" href="/include/waiting_mesgs.css" />
                        <script language="JavaScript" type="text/javascript" src="/include/waiting_mesgs.js"></script>';
                        
####help_msg##########
my $help_hash1  = read_json("/home/httpd/help/time_help.json","time.cgi","服务-时间服务器-覆盖默认的NTP服务器","-90","30","down");
#######################

my %par;
# sub toggle_file($$) {
#     my $file = shift;
#     my $set = shift;
#         
#     if ($set ne "") {
#         `touch $file`;
#         return 1;
#     }
#     if (-e $file) {
#         unlink($file);
#     }
#     return 0;
# }

my @all_lines= read_config_file($ntp_conf);
my @default_ntp;
foreach my $line (@all_lines) {
    chomp($line);
    if ($line !~ /server/) {
        next;
    }
    else{
        $line =~s /^server //;
        if (&validdomainname($line) || &validip($line)) {
            push (@default_ntp,$line);
        }
    }
}
foreach my $line (@default_ntp) {
    chomp($line);
    if ($ntps) {
        $ntps = $ntps."<br />".$line;
    }
    else{$ntps .= $line;}
}

sub read_config_file($) {
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

sub loadconfig() {
    if (-e $conffile_default) {
        readhash($conffile_default, $conf);
    }
    if (-e $conffile) {
        readhash($conffile, $conf);
    }
    if ($conf->{'TIMEZONE'} =~ /^$/) {
        my %mainhash = ();
        my $mainconf = \%mainhash;
        readhash($mainsettings, $mainconf);
        $conf->{'TIMEZONE'} = $mainconf->{'TIMEZONE'};
        $conf->{'TIMEZONE'} =~ s+/usr/share/zoneinfo/(posix/)?++;
    }
    if (($conf->{'NTP_ADDR_1'} !~ /^$/) || ($conf->{'NTP_ADDR_2'} !~ /^$/)) {
        $conf->{'NTP_SERVER_LIST'} .= $conf->{'NTP_ADDR_1'}.",".$conf->{'NTP_ADDR_2'}.","
    }

    delete($conf->{'NTP_ADDR_1'});
    delete($conf->{'NTP_ADDR_2'});

    if (-e $enabled_file) {
        $enabled = 1;
    }
}

sub begin(){
    printf <<EOF
    <script>
      show_waiting_mesg("请稍等...");
    </script>
EOF
    ;
}

sub ends(){
    printf <<EOF
    <script>
      hide_waiting_mesg("设置成功");
    </script>
EOF
    ;
}

my $is_reload=0;
sub action() {
    if ($par{'SYNCACTION'} !~ /^$/) {
        `$sync`;
        `sudo fcmd $sync`;
        return;
    }
    if ($par{'ACTION'} eq 'update') {
        updatetime();
        my @cur_user=&getCurUser();
        my $input_user=$cur_user[0];
        system("/usr/bin/logger","-p","daemon.notice","-t","userLog-$input_user","用户已修改系统时间");

        return;
    }
    if ($par{'ACTION'} eq "save") {
        save();
        return;
    }
    # if ($par{'ACTION'} eq 'save') {
    #     if ($par{'NTP_ENABLE'} eq "on") {
    #         `touch $enabled_file`;
    #     }
    #     else {
    #         #unlink($enabled_file);
    #         `rm $enabled_file`;
    #     }
    #     `$restart`;
    #     return;
    # }
}

sub updatetime() {
    if ($par{'SETHOUR'} eq '' || $par{'SETHOUR'} < 0 || $par{'SETHOUR'} > 23) {
        $errormessage = _('Invalid time entered.');
        return;
    }
    if ($par{'SETMINUTES'} eq '' || $par{'SETMINUTES'} < 0 || $par{'SETMINUTES'} > 59) {
        $errormessage = _('Invalid time entered.');
        return;
    }
    if ($par{'SETDAY'} eq '' || $par{'SETDAY'} < 1 || $par{'SETDAY'} > 31) {
        $errormessage = _('Invalid date entered.');
        return;
    }
    if ($par{'SETMONTH'} eq '' || $par{'SETMONTH'} < 1 || $par{'SETMONTH'} > 12) {
        $errormessage = _('Invalid date entered.');
        return;
    }
    if ($par{'SETMONTH'} eq '' || $par{'SETMONTH'} == 2|| $par{'SETMONTH'} == 4||$par{'SETMONTH'} ==6|| $par{'SETMONTH'} ==9|| $par{'SETMONTH'} ==11) {
    if ( $par{'SETDAY'} == 31) {
        $errormessage = _('Invalid date entered.');
        return;
    }
    
    }  #月份为2，4，6，9，11时，天数如果设置为31，就会报错
    
    if(!isleapyear($par{'SETYEAR'}))    #特殊情况，当年数不为闰年时，2月没有30天
    { 
        if($par{'SETMONTH'} == 2 && $par{'SETDAY'} > 28) {
            $errormessage = _('Invalid date entered.');
            return;
        }
    }else{
        if($par{'SETMONTH'} == 2 && $par{'SETDAY'} > 29) {
            $errormessage = _('Invalid date entered.');
            return;
        }

    }
    if ($par{'SETYEAR'} eq '' || $par{'SETYEAR'} < 2003 || $par{'SETYEAR'} > 2300) {
        $errormessage = _('Invalid date entered.');
        return;
    
    }
    # we want date in YYYY-MM-DD HH:MM format for date command
    # EAO changed datestring to ISO 6801 format 2003-08-11
    my $datestring = "$par{'SETYEAR'}-$par{'SETMONTH'}-$par{'SETDAY'}";
    my $timestring = "$par{'SETHOUR'}:$par{'SETMINUTES'}";
    # EAO setdate.c also revised for ISO 6801 date format 2003-08-11
    # needed to split date and time setting because of ha
    system ('/usr/bin/sudo /bin/date -s \''.$datestring.'\' >/dev/null 2>&1');
    system ('/usr/bin/sudo /bin/date -s \''.$timestring.'\' >/dev/null 2>&1');
    `sudo fcmd '/usr/bin/sudo /bin/date -s \''.$datestring.'\' >/dev/null 2>&1'`;
    `sudo fcmd '/usr/bin/sudo /bin/date -s \''.$timestring.'\' >/dev/null 2>&1'`;
    my $set_time = $datestring." ".$timestring ; 
    my $log_message = "将系统时间修改为".$set_time;
    &user_log($log_message);
    system ( '/usr/bin/sudo /usr/local/bin/logtime_recover.sh > /dev/null 2>&1');
    &log(_('Time/Date manually reset.')." $datestring $timestring");
    printf <<EOF
    <script>
        window.parent.parent.document.getElementById('bottomFrame').contentWindow.document.getElementById('run_time').innerText = "$set_time";
    </script>
EOF
    ;
    $is_reload = 1;
}


sub isleapyear($) #判断闰年函数
{ 
    my $year = shift;
    if(($year%4==0&&$year%100!=0)||$year%400==0)
    { return 1;}
    else
    {return 0;}
}
    
    
sub save() {

    $par{'NTP_SERVER_LIST'} =~ s/\r?\n/,/g;
    foreach my $server (split(/,/, $par{'NTP_SERVER_LIST'})) {
        next if ($server =~ /^$/);
        my $aaa=&is_ipaddress($server);
        if ( !( &validfqdn($server) || &is_ipaddress  ($server))) {
            $errormessage = _('Invalid NTP server address "%s".', $server);
            return;
        }
    }
    if ($par{'SERVER_OVERRIDE'} eq 'on') {
        if ($par{'NTP_SERVER_LIST'} eq '') {
            $errormessage = _('Cannot override NTP servers with empty server list.');
            return;
        }
    }   
    my $reload = 0;
    if (($par{'NTP_SERVER_LIST'} ne $conf->{'NTP_SERVER_LIST'}) ||
        ($par{'TIMEZONE'} ne $conf->{'TIMEZONE'}) ||
        ($par{'SERVER_OVERRIDE'} ne $conf->{'SERVER_OVERRIDE'})) {
       
        $conf->{'NTP_SERVER_LIST'} = $par{'NTP_SERVER_LIST'};   
        $conf->{'SERVER_OVERRIDE'} = $par{'SERVER_OVERRIDE'};   
        $conf->{'TIMEZONE'} = $par{'TIMEZONE'};    
        $reload = 1;

        writehash($conffile, $conf);
        `sudo fmodify $conffile`;
        &log(_('Written down NTP configuration'));
    }

    # if ($par{'NTP_ENABLE'} ne $enabled) {
    #     $enabled = toggle_file($enabled_file, $par{'NTP_ENABLE'});
    #     $reload = 1;
    # }

    if ($reload) {
        $is_reload = 1;
    }
}

sub timezone_select {
    my $select_box = "<select name='TIMEZONE'>";
    use DateTime::TimeZone;
    foreach my $zone (DateTime::TimeZone::all_names) {
        my $checked = '';
        if ($conf->{'TIMEZONE'} eq $zone) {
            $checked = 'selected';
        }
        $select_box .= "<option value='$zone' $checked>$zone</option>";
    }
    $select_box .= "</select>";
    return $select_box;
}

sub display() {
    my $ntp_servers = $conf->{'NTP_SERVER_LIST'};
    $ntp_servers =~ s/,/\n/g;
    my $show_servers = "hidden";
    
    if ($checked{$conf->{'SERVER_OVERRIDE'}}) {
        $show_servers = "";
    }
    
    &openbox('100%', 'left', _('Use a network time server'));
    
    printf <<END
    <script type="text/javascript">
        \$(document).ready(function() {
            \$('#custom-server').click(function() {
                if(\$('#custom-server').get(0).checked) 
                    \$('#server-list').show();
                else
                    \$('#server-list').hide();
            });
        });
    </script>
    <form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <input type='hidden' name='ACTION' value='save' />
            <tr class="odd">
                <td class="add-div-type" rowspan="2"> %s</td>
                <td ><b>%s</b></td><td><ul>
END
    ,_('Settings')
    ,_('Default NTP servers')
;
    foreach my $elem (@default_ntp) {
        printf <<EOF
        <li>$elem</li>
EOF
;
      }
    my $disd="style='display:none;'";
    if ($checked{$conf->{'SERVER_OVERRIDE'}} eq "checked") {
          $disd="style='display:block;'";
    }
    printf <<END
                    </ul></td>
                </tr>
            <tr class="odd">
                <td class="need_help" width="200px">
                    <label id="username_field" for="custom-server">%s *</label>
                    <input type='checkbox' style="margin-left: 5px;" id="custom-server" name='SERVER_OVERRIDE' $checked{$conf->{'SERVER_OVERRIDE'}} value='on'/>
                    
                </td>
                <td class="need_help">
                    <textarea  id="server-list" name='NTP_SERVER_LIST' cols='20' rows='4' wrap='off' $disd>$ntp_servers</textarea>$help_hash1
                </td>
            </tr>
            <tr style="display:none;">
                <td colspan="3">%s</td>
            </tr> 
            <tr class="table-footer">
                <td colspan="3">
                    <input class='net_button' type='submit' name='SUBMITACTION' value='%s' />&nbsp;&nbsp;
                    <input class='net_button' type='submit' name='SYNCACTION' value='%s' />
                </td>
            </tr>
        </table>
    </form>

END
    ,_('使用自定义的NTP服务器'),
    &timezone_select,
    _('Save'),
    _('Synchronize now')
;
    &closebox();

    use DateTime;
    my $dt = DateTime->now(time_zone=>$conf->{'TIMEZONE'});
    my $year = $dt->year;
    my $month  = $dt->month;
    my $day    = $dt->day;
    my $hour   = $dt->hour;
    my $minute = $dt->minute;

    &openbox('100%', 'left', _('Adjust manually'));

    printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}' name="update_time_form">
    <input type='hidden' name='ACTION' value='update' />
    <table width='100%'>
        <tr class="env">
            <td>
                <input type='text' name='SETYEAR' size='4' maxlength='4' value='$year' />
                %s <input type='text' name='SETMONTH' size='2' maxlength='2' value='$month' />
                %s <input type='text' name='SETDAY' size='2' maxlength='2' value='$day' />
                %s <input type='text' name='SETHOUR' size='2' maxlength='2' value='$hour' />
                %s <input type='text' name='SETMINUTES' size='2' maxlength='2' value='$minute' />%s
                <input class='submitbutton net_button' type='submit' name='submit' value='%s' />
            </td>
        </tr>
    </table>
    </form>
END
,
    _('Year'),
    _('月'),
    _('日'),
    _('Hours'),
    _('Minutes'),
    _('Set time')
    ;
    &closebox();
    &check_form();
}


getcgihash(\%par);
loadconfig();
showhttpheaders();
&openpage(_('NTP configuration'), 1, $extraheader);
action();
&openbigbox($errormessage, $warnmessage, $notemessage);
display();
closebigbox();
if ($is_reload) {
    begin();
    `$restart`;
    ends();
}
closepage();

sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'update_time_form',
       'option'   :{
            'SETYEAR':{
                'type':'text',
                'required':'1',
                'check':'num|',
                'ass_check':function(eve){
                    var msg="";
                    var viewsize = eve._getCURElementsByName("SETYEAR","input","update_time_form")[0].value;
                    if (viewsize.length > 20) {
                    msg = "请输入1-20字符";
                    }
                    return msg;
                }
            },
            'SETMONTH':{
                'type':'text',
                'required':'1',
                'check':'num|',
                'ass_check':function(eve){
                    var msg="";
                    var viewsize = eve._getCURElementsByName("SETMONTH","input","update_time_form")[0].value;
                    if (Number(viewsize)>12) {
                        msg = "请输入1-12的数字";
                    }
                    return msg;
                }
            },
            'SETDAY':{
                'type':'text',
                'required':'1',
                'check':'note|',
                'ass_check':function(eve){
                    var msg="";
                    var viewsize = eve._getCURElementsByName("SETDAY","input","update_time_form")[0].value;
                    if (/\\D/g.test(viewsize)) {
                        msg = "请输入0-31的数字";
                    }else{
                        if (Number(viewsize)>31 || Number(viewsize)<0) {
                            msg = "请输入0-31的数字";
                        }
                    }
                    return msg;
                }
            },
            'SETHOUR':{
                'type':'text',
                'required':'1',
                'check':'note|',
                'ass_check':function(eve){
                    var msg="";
                    var viewsize = eve._getCURElementsByName("SETHOUR","input","update_time_form")[0].value;
                    if (/\\D/g.test(viewsize)) {
                        msg = "请输入0-23的数字";
                    }else{
                        if (Number(viewsize)>24 || Number(viewsize)<0) {
                            msg = "请输入0-23的数字";
                        }
                    }
                    return msg;
                }
            },
            'SETMINUTES':{
                'type':'text',
                'required':'1',
                'check':'note|',
                'ass_check':function(eve){
                    var msg="";
                    var viewsize = eve._getCURElementsByName("SETMINUTES","input","update_time_form")[0].value;
                    if (/\\D/g.test(viewsize)) {
                        msg = "请输入0-59的数字";
                    }else{
                        if (Number(viewsize)>59 || Number(viewsize)<0) {
                            msg = "请输入0-59的数字";
                        }
                    }
                    return msg;
                }
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object);
    </script>
EOF
    ;
}