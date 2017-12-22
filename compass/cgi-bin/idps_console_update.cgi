#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:Snort控制台升级界面
#
# AUTHOR: 王琳, 245105947@qq.com
# COMPANY: capsheaf
# HISTORY:
#    2014.04.28-14:00 Created by WangLin
#
#===============================================================================


require '/var/efw/header.pl';
require 'file_relevant_time.pl';

my $config_file_dir = "${swroot}/updateips/console";
my $config_file     = "$config_file_dir/settings";
my $version_file    = "$config_file_dir/release";
my $updated_tag     = "$config_file_dir/console_updated_last_time";
my $log_file        = "/var/log/snort/updatecontrol.log";

my $systemconfig    = "${swroot}/systemconfig/settings";
my $tmp_dir         = "/tmp";

my $offline_update  = "sudo /usr/local/bin/decryption_ips_control.py";  #离线升级
my $update_now      = "sudo /usr/local/bin/autoget_ipscontrol.py";      #立即升级
my $autogetrule     = "sudo /usr/local/bin/restartsnortcontrol.py";     #自动升级

my $errormessage    = '';
my $warnmessage     = '';
my $notemessage     = '';

my $extraheader     = '<link rel="stylesheet" type="text/css" href="/include/idps_rules_lib_update.css"/>
                        <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css"/>
                        <link rel="stylesheet" type="text/css" href="/include/waiting_mesgs.css"/>
                        <script type="text/javascript" src="/include/popup_mesgs.js"></script>
                        <script type="text/javascript" src="/include/waiting_mesgs.js"></script>
                        <script type="text/javascript" src="/include/idps_console_update.js"></script>';
my %par;
my %settings;
my %system_settings;

#========页面主体==================#
&make_file();
&read_system_config();#一进入就读取系统信息,包含标题等信息
&getcgihash(\%par);
&doaction();
#======================================#

sub make_file(){
    if(!-e $config_file_dir)
    {
        `mkdir -p $config_file_dir`;
    }
    if(!-e $config_file)
    {
        `touch $config_file`;
    }
}

sub read_conf(){
    if ( -f $config_file ) {
       &readhash( "$config_file", \%settings );
    }
}

sub save_conf() {
    #===升级服务器===#
    $settings{'UPDATE_SERVER'} = $par{'UPDATE_SERVER'};
    my $update_server = "192.168.4.49";
    if($par{'UPDATE_SERVER'} eq 'custom') {
        $update_server = $par{'CONTROL_URL'};
    }
    $settings{'CONTROL_URL'} = "http://".$update_server."/package/IpsControl.bin";
    #===自动下发控制台===#
    $settings{'ONLINE_SEND'} = $par{'ONLINE_SEND'};
    if($par{'ONLINE_SEND'} ne 'on') {
        $settings{'ONLINE_SEND'} = 'off';
    }
    #===升级方案===#
    $settings{'ENABLED'} = $par{'ENABLED'};
    if($par{'ENABLED'} eq 'on') {
        $settings{'ENABLED'} = $par{'ENABLED'};
        $settings{'UPDATE_SCHEDULE'} = $par{'UPDATE_SCHEDULE'};
    } else {
        $settings{'ENABLED'} = 'off';
    }

    &writehash($config_file, \%settings);
    `sudo fmodify $config_file`;
}

sub doaction() {
    &read_conf();
    if ($par{'save'} ne '')
    {
        &save_conf();
        #===后台执行，前台立即返回===#
        $autogetrule = $autogetrule." &";
        system($autogetrule);
        $notemessage = "保存成功!";
    }
    
    if ($par{'update_now'} ne'')
    {
        &save_conf();
        #===后台执行，前台立即返回===#
        $update_now = $update_now." &";
        system($update_now);
        system("touch $updated_tag");#升级标识
    }

    if($par{'import_rules'} ne '') {
        &import_rules();
    }

    if($par{'updated_check'} ne '') {
        &showhttpheaders();
        if( $par{'updated_check'} eq 'updated_check' ) {
            if ( -e $updated_tag ) {
                system("rm $updated_tag");
                &send_status(1, 0, "");#进行了升级操作
            } else {
                &send_status(0,0,"");#未进行升级操作
            }
        } elsif ( $par{'updated_check'} eq 'check_updated_result' ) {
            &check_updated_result();
        }
    } else {
        &show_page();
    }
}

sub import_rules() {
    $settings{'OFFLINE_SEND'} = $par{'OFFLINE_SEND'};
    if($par{'OFFLINE_SEND'} ne 'on') {
        $settings{'OFFLINE_SEND'} = 'off';
    }
    &writehash($config_file, \%settings);

    my $cgi = new CGI; 
    my $fh = $cgi->param('IDPS_CONSOLE_FILE');

    if(!$fh || $fh !~ /\.bin$/) {
        $errormessage = "文件格式错误";
        return 0;
    }
    
    if( !-e $tmp_dir) {
        system("mkdir -p $tmp_dir");
    }
    
    if(!open(UPLOAD, ">$tmp_dir/IpsControl.bin")) { $errormessage="打开文件失败"; return false; } 
    binmode UPLOAD;
    my $count = 0;
    while(<$fh>) { $count = 1; print UPLOAD; }
    close UPLOAD;

    if(!$count) {
        $errormessage = "文件内容为空";
        return 0;
    }

    #===后台执行，前台立即返回===#
    # system("$offline_update $tmp_dir/$fh custom >/dev/null &");
    system("$offline_update &");
    system("touch $updated_tag");#升级标识
}

sub show_page() {
    &read_conf();
    &showhttpheaders();
    &openpage("控制台升级", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'left', '离线升级');
    &show_update();
    &closebox();
    &openbox('100%', 'left', '在线升级');
    &show_updateonline();
    &closebox();
    &openbox('100%', 'left', '版本状态');
    &show_version();
    &closebox();
    &check_form();
    &closepage();
}

sub check_updated_result() {
    my @logs;
    my ($is_updated, $status, $mesg) = (0, -1, "升级失败");
    if( -e $log_file ) {
        @logs = read_conf_file($log_file);
        foreach my $log ( @logs ) {
            if( $log =~ /your system is new, need not updata, goodbye\./ ) {
                $status = -1;
                $mesg = "系统已达到最新状态,升级失败";
                &send_status($is_updated, $status, $mesg);
                return;
            }

            if( $log =~ /this is new version, no need update to download\./ ) {
                $status = -1;
                $mesg = "系统已达到最新状态,升级失败";
                &send_status($is_updated, $status, $mesg);
                return;
            }

            if( $log =~ /now,updata system successd\./) {
                $status = 0; #升级成功
                $mesg = "升级成功";
                &send_status($is_updated, $status, $mesg);
                return;
            }

            if( $log =~ /decrption.*\.bin failed\./) {
                $status = -1; #升级成功
                $mesg = "文件解密失败,升级失败";
                &send_status($is_updated, $status, $mesg);
                return;
            }

            if( $log =~ /md5 is error,file is modified, please check, updata failed\./) {
                $status = -1; #升级成功
                $mesg = "文件解密失败,文件已改变,升级失败";
                &send_status($is_updated, $status, $mesg);
                return;
            }

            if( $log =~ /have no updata file,please check, updata failed\./) {
                $status = -1; #升级成功
                $mesg = "没有升级文件,升级失败";
                &send_status($is_updated, $status, $mesg);
                return;
            }
        }
        $status = -1;
        $mesg = "升级异常";
        &send_status($is_updated, $status, $mesg);#防止没有任何一种情况匹配
        return;
    } else {
        &send_status($is_updated, $status, $mesg);
        return;
    }
}

sub send_status($$$) {
    #==========状态解释=========================#
    # => $is_updated: 1 表示升级了，其他表示未升级
    # => $status: 0 表示升级成功，其他表示-1表示升级失败
    # => $mesg: 相关的消息
    #===========================================#
    my ($is_updated, $status, $mesg) = @_;
    my %hash;
    %hash->{'is_updated'} = $is_updated;
    %hash->{'status'} = $status;
    %hash->{'mesg'} = $mesg;
    my $json = new JSON::XS;
    my $result = $json->encode(\%hash);
    print $result;
}

sub show_updateonline(){
    #===升级服务器====#
    my %update_server_checked;
    $update_server_checked{$settings{'UPDATE_SERVER'}} = "checked";
    $settings{'CONTROL_URL'} =~ m{http://(.*)/package/IpsControl.bin};
    my $control_url = $1;
    my $control_url_disabled = "";
    my $control_url_class = "";
    if($settings{'UPDATE_SERVER'} eq 'auto') {
        $control_url = "";
        $control_url_disabled = "disabled";
        $control_url_class = "hidden";
    }
    #===自动下发控制台===#
    my $online_send_checked = "checked";
    if($settings{'ONLINE_SEND'} ne 'on') {
        $online_send_checked = "";
    }
    #===升级方案===#
    my %update_schedule_checked;
    $update_schedule_checked{$settings{'UPDATE_SCHEDULE'}} = "checked";
    my $enabled_checked = "checked";
    my $update_schdule_disabled = "";
    my $update_schdule_disabled_class = "";
    if($settings{'ENABLED'} eq '') {
        $enabled_checked = "";
        $update_schdule_disabled = "disabled";
        $update_schdule_disabled_class = "disabled";
    }

    printf <<EOF
    <form name='RULES_UPDATE_ONLINE' enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tbody>
                <tr class ='odd'>
                    <td class='add-div-type'>默认升级服务器</td>
                    <td>
                        <input type="radio" name="UPDATE_SERVER" value="auto" $update_server_checked{'auto'} onclick="toggle_update_server(this);"/>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>自定义升级服务器</td>
                    <td>
                        <input type="radio" name="UPDATE_SERVER" value="custom" $update_server_checked{'custom'} onclick="toggle_update_server(this);"/>
                        <span class="addition">
                            <input type="text" class="$control_url_class" name="CONTROL_URL" id="snort_rules_url" value="$control_url" $control_url_disabled/>
                        </span>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>自动下发子控制台</td>
                    <td>
                        <input type="checkbox" name="ONLINE_SEND" $online_send_checked/>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>选择升级方案</td>
                    <td>
                        <input type="checkbox" name="ENABLED" $enabled_checked onclick="toggle_update_schedule(this);"/>

                        <span class="addition">
                            <input type="radio" name="UPDATE_SCHEDULE" id="schedule_hourly" value="hourly" class="radio_input update_schedule_radio" $update_schedule_checked{'hourly'} $update_schdule_disabled/>
                            <label for="schedule_hourly" class="label_for_radio update_schedule_label $update_schdule_disabled_class">每小时</label>

                            <input type="radio" name="UPDATE_SCHEDULE" id="schedule_daily" value="daily" class="radio_input update_schedule_radio" $update_schedule_checked{'daily'} $update_schdule_disabled/>
                            <label for="schedule_daily" class="label_for_radio update_schedule_label $update_schdule_disabled_class">每天</label>

                            <input type="radio" name="UPDATE_SCHEDULE" id="schedule_weekly" value="weekly" class="radio_input update_schedule_radio" $update_schedule_checked{'weekly'} $update_schdule_disabled/>
                            <label for="schedule_weekly" class="label_for_radio  update_schedule_label $update_schdule_disabled_class">每周</label>

                            <input type="radio" name="UPDATE_SCHEDULE" id="schedule_monthly" value="monthly" class="radio_input update_schedule_radio" $update_schedule_checked{'monthly'} $update_schdule_disabled/>
                            <label for="schedule_monthly" class="label_for_radio update_schedule_label $update_schdule_disabled_class">每月</label>
                        </span>
                    </td>
                </tr>
            </tbody>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tfoot>
                <tr class="table-footer">
                    <td width="50%">
                        <input class="net_button" name="save" value="保存" style="display:block;float:right;color:black" type="submit">
                    </td>
                    <td width="50%">
                        <input class="net_button" name="update_now" value="立即升级" style="display:block;float:left;color:black"  type="submit">
                    </td>
                </tr>
            </tfoot>
        </table>
    </form>
EOF
;
}

sub show_version()
{
    my $version;
    my $error = 0;
    if(!-e $version_file)
    {
        $version = "系统版本文件不存在！";
        $error = 1;
    } else {
        unless(open (VERSIONFILE, "$version_file")){
            $version = "无法访问系统版本文件！";$error = 1;
        }
        if($error) {
        } else {
            my $line = <VERSIONFILE>;
            if($line ne ''){
                chomp($line);
                $version = $line;
            } else {
                $version = "版本信息读取错误！";
                $error = 1;
            }
            close(VERSIONFILE);
       }
    }
    
    
    if($error)
    {
       printf <<EOF
        <div id="pop-note-div">
            <span>错误：$version</span>
        </div>
EOF
        ;
    } else {
        my $update_time = &get_file_mtime_by_formatday($version_file, "-");
        printf <<EOF  
        <table width="100%" cellpadding="0" cellspacing="0">
            <tbody>
                <tr class="odd">
                    <td class="add-div-type">当前版本</td>
                    <td>$version</td>
                </tr>
                <tr class="odd odd_last_line">
                    <td class="add-div-type">更新时间</td>
                    <td>$update_time</td>
                </tr>
            </tbody>
        </table>
EOF
        ;
    }
}

sub show_update(){
    #读取系统信息
    my $offline_send_checked = "checked";
    if($settings{'OFFLINE_SEND'} ne 'on') {
        $offline_send_checked = "";
    }
    printf <<EOF
    <form name='RULES_UPDATE_OFFLINE' enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tbody>
                <tr class ='odd'>
                    <td class='add-div-type'>自动下发子控制台</td>
                    <td>
                        <input type="checkbox" name="OFFLINE_SEND" $offline_send_checked/>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>导入控制台升级文件</td>
                    <td>
                        <input type="file" id="IDPS_CONSOLE_FILE" name="IDPS_CONSOLE_FILE"/>
                        导入控制台升级文件(*.bin)
                        <input class="net_button" type="submit" name="import_rules" value="升级" onclick="offline_update();"/>
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr class="table-footer"> 
                    <td colspan="2">
                        <span style="float:right;">请到<a onclick='jump("http://%s")' style='cursor:pointer' color='blue'>%s</a>下载最新升级包</span>
                    </td>
                </tr>
            </tfoot>
        </table>
    </form>
EOF
    ,$system_settings{'COMPANY_WEBSITE'}
    ,$system_settings{'COMPANY_WEBSITE'}
    ;
}

sub check_form() {
    printf <<EOF
    <script language="JavaScript">
        check._main(object);
        check._main(object2);
    </script>
EOF
    ;
}

sub read_system_config(){
    if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    $system_title = $system_settings{'SYSTEM_TITLE'};
}
