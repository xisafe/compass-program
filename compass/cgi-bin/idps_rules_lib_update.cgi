#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:Snort特征库升级界面
#
# AUTHOR: 王琳, 245105947@qq.com
# COMPANY: capsheaf
# HISTORY:
#    2014.04.18-14:00 Created by WangLin
#
#===============================================================================


require '/var/efw/header.pl';
require 'file_relevant_time.pl';

my $config_file_dir = "${swroot}/updateips/rules";
my $config_file     = "$config_file_dir/settings";
my $version_file    = "$config_file_dir/status";
my $log_file        = "/var/log/snort/updaterules.log";
my $updated_tag     = "$config_file_dir/updated_last_time";

my $offline_update  = "sudo /usr/local/bin/fetchsnortrules.py ";
my $update_now      = "sudo /usr/local/bin/fetchsnortrules.py";
my $autogetrule     = "sudo /usr/local/bin/restartsnortrules";

my $tmp_dir         = "/tmp";
my $systemconfig    = "${swroot}/systemconfig/settings";

my $errormessage    = '';
my $warnmessage     = '';
my $notemessage     = '';

my $extraheader     = '<link rel="stylesheet" type="text/css" href="/include/idps_rules_lib_update.css"/>
                        <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css"/>
                        <link rel="stylesheet" type="text/css" href="/include/waiting_mesgs.css"/>
                        <script type="text/javascript" src="/include/popup_mesgs.js"></script>
                        <script type="text/javascript" src="/include/waiting_mesgs.js"></script>
                        <script type="text/javascript" src="/include/idps_rules_lib_update.js"></script>';
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


sub getVersion(){ #获取版本信息#
    my $temp_cmd = "/usr/local/bin/getUpdateRelease.py -t app_rule";
    my $json_res = `$temp_cmd`;
    return $json_res;

}
sub save_conf() {
    #===升级服务器===#
    $settings{'UPDATE_SERVER'} = $par{'UPDATE_SERVER'};
    my $update_server = "192.168.4.49";
    if($par{'UPDATE_SERVER'} eq 'custom') {
        $update_server = $par{'SNORT_RULES_URL'};
    }
    $settings{'SNORT_RULES_URL'} = "http://".$update_server."/package/IpsFeatureLib.dat";
    #===自动下发控制台===#
    $settings{'ONLINE_SEND'} = $par{'ONLINE_SEND'};
    if($par{'ONLINE_SEND'} ne 'on') {
        $settings{'ONLINE_SEND'} = 'off';
    }
    #===升级方案===#
    $settings{'ENABLED_RULES'} = '';
    if($par{'ENABLED_RULES'} eq 'on') {
        $settings{'ENABLED_RULES'} = 'auto';
        $settings{'UPDATE_SCHEDULE'} = $par{'UPDATE_SCHEDULE'};
    }

    &writehash($config_file, \%settings);
    `sudo fmodify $config_file`;
}

sub doaction() {
    &read_conf();
  
    if($par{'down-load'} ne ''){ #在线升级点击下载#
        my $self_url = $par{'self_url'};
        if($self_url =~ /[a-zA-Z0-9:.\/]/){
            system("echo $self_url > /var/efw/unify_update/app_rule/address");

            my $temp_cmd = "sudo /usr/local/bin/downloadUpdatePakage.py -u $self_url -n online_app_rule.dat";
            my $res = `$temp_cmd`;
            if($res eq "yes"){
                $notemessage ="下载成功!";
            }else{
                $errormessage ="下载失败！";
            }
        }
    }
    if($par{'update_now'} ne ''){
        my $temp_cmd = "/usr/local/bin/online_rules_update.py -t app_rule -n online_app_rule.dat";
        my $res = `$temp_cmd`;
        if($res eq "yes"){
                $notemessage ="升级成功!";
            }else{
                $errormessage ="升级失败！";
            }
    }
    if($par{'import_rules'} ne '') {
        # my $file = $par{'IDS_RULES_FILE'};
        my $cgi = new CGI; 
        my $file = $cgi->param('IDS_RULES_FILE');
        if(!$file || $file !~ /\.dat/) {
            $errormessage = "文件格式错误";
        }else{
            if( !-e $tmp_dir) {
                system("mkdir -p $tmp_dir");
            }
            
            if(!open(UPLOAD, ">$tmp_dir/IpsFeatureLib.dat")) { $errormessage="打开文件失败"; return false; } 
            binmode UPLOAD;
            my $count = 0;
            while(<$file>) { $count = 1; print UPLOAD; }
            close UPLOAD;
            if(!$count) {
                $errormessage = "文件内容为空";
                return 0;
            }
           my $temp_cmd = "sudo /usr/local/bin/unify_rules_update.py -t app_rule -n IpsFeatureLib.dat ";
           my $res = `$temp_cmd`;
            if($res eq "yes"){
                $notemessage ="升级成功!";
            }else{
                $errormessage ="升级失败!";
                
            } 
        }
        
    }

    &show_page();

    # if($par{'updated_check'} ne '') {
    #     &showhttpheaders('json');
    #     if( $par{'updated_check'} eq 'updated_check' ) {
    #         if ( -e $updated_tag ) {
    #             system("rm $updated_tag");
    #             &send_status(1, 0, "");#进行了升级操作
    #         } else {
    #             &send_status(0,0,"");#未进行升级操作
    #         }
    #     } elsif ( $par{'updated_check'} eq 'check_updated_result' ) {
    #         &check_updated_result();
    #     }
    # } else {
    #     &show_page();
    # }
}

sub import_rules() {
    $settings{'OFFLINE_SEND'} = $par{'OFFLINE_SEND'};
    if($par{'OFFLINE_SEND'} ne 'on') {
        $settings{'OFFLINE_SEND'} = 'off';
    }
    &writehash($config_file, \%settings);

    my $cgi = new CGI; 
    my $fh = $cgi->param('IDS_RULES_FILE');

    if(!$fh || $fh !~ /\.dat/) {
        $errormessage = "文件格式错误";
        return 0;
    }
    
    if( !-e $tmp_dir) {
        system("mkdir -p $tmp_dir");
    }
    
    if(!open(UPLOAD, ">$tmp_dir/IpsFeatureLib.dat")) { $errormessage="打开文件失败"; return false; } 
    binmode UPLOAD;
    my $count = 0;
    while(<$fh>) { $count = 1; print UPLOAD; }
    close UPLOAD;

    if(!$count) {
        $errormessage = "文件内容为空";
        return 0;
    }

    #===后台执行，前台立即返回===#
    #system("$offline_update $tmp_dir/$fh system >/dev/null &");
    system("$offline_update /tmp/IpsFeatureLib.dat system >/dev/null &");
    system("touch $updated_tag");#升级标识
}

sub check_updated_result() {
    my @logs;
    my ($is_updated, $status, $mesg) = (0, -1, "升级失败");
    
    my @cur_user=&getCurUser();
    my $IP = $ENV{'REMOTE_ADDR'};
    my $input_user=$cur_user[0];

    
    if( -e $log_file ) {
        @logs = read_conf_file($log_file);
        foreach my $log ( @logs ) {
            if( $log =~ /the current version is over the packge version, please enter a new update packge/ ) {
                $status = -1;
                $mesg = "系统已达到最新状态,升级失败";
                &send_status($is_updated, $status, $mesg);

		system("/usr/bin/logger","-p","local6.notice","-t","userLog-$input_user","$IP--系统已达到最新状态,特征库升级失败");
                return;
            }

            if( $log =~ /ok, snort rule update successd\./) {
                $status = 0; #升级成功
                $mesg = "升级成功";
                &send_status($is_updated, $status, $mesg);
		system("/usr/bin/logger","-p","local6.notice","-t","userLog-$input_user","$IP--特征库升级成功");
                return;
            }

            if( $log =~ /decryption file packge failed\./) {
                $status = -1; 
                $mesg = "文件解密失败,升级失败";
                &send_status($is_updated, $status, $mesg);
		system("/usr/bin/logger","-p","local6.notice","-t","userLog-$input_user","$IP--文件解密失败,特征库升级失败");
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

sub show_page() {
    &read_conf();
    &showhttpheaders();
    &openpage("类型识别库升级", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'left', '离线升级');
    &show_update();
    &closebox();
    #=== 隐藏在线升级功能 ===#
    &openbox('100%', 'left', '在线升级');
    &show_update_online();
    &closebox();
    
    &openbox('100%', 'left', '版本状态');
    &show_version();
    &closebox();
    &check_form();
    &closepage();
}

sub show_update_online(){
    #===升级服务器====#
    my %update_server_checked;
    $update_server_checked{$settings{'UPDATE_SERVER'}} = "checked";
    $settings{'SNORT_RULES_URL'} =~ m{http://(.*)/package/IpsFeatureLib.dat};
    my $snort_rules_url = $1;
    my $snort_rules_url_disabled = "";
    my $snort_rules_url_class = "";
    if($settings{'UPDATE_SERVER'} eq 'auto') {
        $snort_rules_url = "";
        $snort_rules_url_disabled = "disabled";
        $snort_rules_url_class = "hidden";
    }
    #===自动下发控制台===#
    my $online_send_checked = "checked";
    if($settings{'ONLINE_SEND'} ne 'on') {
        $online_send_checked = "";
    }
    #===升级方案===#
    my %update_schedule_checked;
    $update_schedule_checked{$settings{'UPDATE_SCHEDULE'}} = "checked";
    my $enabled_rules_checked = "checked";
    my $update_schdule_disabled = "";
    my $update_schdule_disabled_class = "";
    if($settings{'ENABLED_RULES'} eq '') {
        $enabled_rules_checked = "";
        $update_schdule_disabled = "disabled";
        $update_schdule_disabled_class = "disabled";
    }
    my $self_url = `cat /var/efw/unify_update/app_rule/address`;
    printf <<EOF
    <form name='RULES_UPDATE_ONLINE' enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tbody>
                <tr class ='odd'>
                    <td class='add-div-type'>URL</td>
                    <td>
                        <input type="text" name="self_url"/ value="$self_url">
                    
                        <input type="submit" name="down-load" value="下载" onclick="downLoad();"/>
                       
                        <input type="submit" id="update_now" onclick="updateNow();" class="net_button" name="update_now" value="升级"/>
                    </td>

                </tr>
            </tbody>
            <tfoot>
                <tr class="table-footer">
                    <td colspan="2">
                        <!--<input type="submit" class="net_button" name="save" value="保存"/>
                        <input type="submit" class="net_button" name="update_now" value="立即升级"/>-->
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
    my $obj = &getVersion();
    my $json = new JSON::XS;
    my $hash = $json->decode($obj);

    if($obj eq 'no')
    {
       printf <<EOF
        <div id="pop-note-div">
            <span>暂无版本信息</span>
        </div>
EOF
        ;
    } else {
        my $release = $hash->{'detail'}[0]->{'release'};
        my $updatetime = $hash->{'detail'}[0]->{'updatetime'};
        printf <<EOF  
        <table width="100%" cellpadding="0" cellspacing="0">
            <tbody>
                <tr class="odd">
                    <td class="add-div-type">当前版本</td>
                    <td>$release</td>
                </tr>
                <tr class="odd odd_last_line">
                    <td class="add-div-type">更新时间</td>
                    <td>$updatetime</td>
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
                    <td class='add-div-type'>导入特征库文件</td>
                    <td>
                        <input type="file" id="IDS_RULES_FILE" name="IDS_RULES_FILE"/>
                        导入特征库文件(*.dat)
                        <input class="net_button" type="submit" name="import_rules" value="升级" onclick="offline_update();"/>
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr class="table-footer"> 
                    <td colspan="2">
                        <span style="float:right;">请到<a onclick='window.open("http://%s")' style='cursor:pointer' color='blue'>%s</a>下载最新升级包</span>
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
