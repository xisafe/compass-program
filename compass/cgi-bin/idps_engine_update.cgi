#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:Snort引擎升级界面
#
# AUTHOR: 王琳, 245105947@qq.com
# COMPANY: capsheaf
# HISTORY:
#    2014.04.28-17:00 Created by WangLin
#
#===============================================================================


require '/var/efw/header.pl';
require 'file_relevant_time.pl';

my $engine_config_file_dir  = "${swroot}/updateips/engine";
my $engine_config_file      = "${swroot}/ipsconsole/child/engine.config";
my $engine_choice           = "$engine_config_file_dir/choice.engine";
my $version_file            = "$engine_config_file_dir/release";
my $log_file                = "/var/log/snort/updateengine.log";

my $uploaded_tag            = "$engine_config_file_dir/idps_engine_uploaded_tag";
my $need_decryption_tag     = "$engine_config_file_dir/idps_engine_decryption_tag";
my $need_update_tag         = "$engine_config_file_dir/idps_engine_updating_tag";

my $tmp_dir                 = "/var/updata";
my $systemconfig            = "${swroot}/systemconfig/settings";

my $decryptionengine        = "sudo /usr/local/bin/decryption_ips_engine.py >/dev/null 2>&1 &";
my $updateipsengine         = "sudo /usr/local/bin/update_ips_engine.py >/dev/null 2>&1 &";

my $errormessage            = '';
my $warnmessage             = '';
my $notemessage             = '';

my $extraheader             = '<link rel="stylesheet" type="text/css" href="/include/idps_engine_update.css"/>
                                <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css"/>
                                <link rel="stylesheet" type="text/css" href="/include/waiting_mesgs.css"/>
                                <script type="text/javascript" src="/include/popup_mesgs.js"></script>
                                <script type="text/javascript" src="/include/waiting_mesgs.js"></script>
                                <script type="text/javascript" src="/include/idps_engine_update.js"></script>';
my %par;
my %settings;
my %system_settings;

#========页面主体==================#
&make_file();
&read_system_config();#一进入就读取系统信息,包含标题等信息
&getcgihash(\%par);
&do_action();
#======================================#

sub make_file(){
    if(!-e $engine_config_file_dir)
    {
        `mkdir -p $engine_config_file_dir`;
    }
    if(!-e $engine_config_file)
    {
        `touch $engine_config_file`;
    }
}

sub do_action() {
    if($par{'import_file'} ne '') {
        &import_file();
    }

    if($par{'updated_check'} ne '') {
        &showhttpheaders();
        if( $par{'updated_check'} eq 'uploaded_check' ) {
            &uploaded_check();
        } elsif ( $par{'updated_check'} eq 'do_decryption' ) {
            &do_decryption();
        } elsif ( $par{'updated_check'} eq 'decryption_check' ) {
            &decryption_check();
        } elsif ( $par{'updated_check'} eq 'update_engine' ) {
            &update_engine();
        } elsif ( $par{'updated_check'} eq 'updated_check' ) {
            &updated_check();
        }
    } else {
        &show_page();
    }
}

sub import_file() {
    my $cgi = new CGI; 
    my $fh = $cgi->param('IDPS_ENGINE_FILE');

    if(!$fh || $fh !~ /\.bin$/) {
        $errormessage = "文件格式错误";
        return 0;
    }
    
    if( !-e $tmp_dir) {
        system("mkdir -p $tmp_dir");
    }
    
    if(!open(UPLOAD, ">$tmp_dir/$fh")) { $errormessage="打开文件失败"; return false; } 
    binmode UPLOAD;
    my $count = 0;
    while(<$fh>) { $count = 1; print UPLOAD; }
    close UPLOAD;

    if(!$count) {
        $errormessage = "文件内容为空";
        return 0;
    }
    system("touch $uploaded_tag");#上传文件标识
    system("touch $need_decryption_tag");#需要马上解密的标识
}

sub uploaded_check() {
    my ($is_opted, $status, $mesg) = (-1, -1, "");#默认未进行升级操作
    if( -e $uploaded_tag ) {
        $is_opted = 0;
        if ( -e $need_decryption_tag ) {
            $status = 2;#上传了,没解密,需要解密
        } else {
            $status = 3;
        }

        if ( -e $need_update_tag ) {
            $status = 1;#已经解密成功,但是未下发子引擎
            system("rm $need_update_tag")
        }
    }
    &send_status($is_opted, $status, $mesg);
}

sub do_decryption() {
    system("rm $need_decryption_tag");#不管解密结果如何,不再解密
    system($decryptionengine); #进行解密
    &send_status(0, -1, "");#已经开始解密
}

sub decryption_check() {
    #===分析日志看解密是否完成===#
    my @logs = &read_conf_file($log_file);
    my $result = join " ", @logs;
    my ($is_opted, $status, $mesg) = (-1, -1, "");
    if ( $result =~ /decrption the .*\.bin successd/ || $result =~ /decrption the .*\.bin failed/ ) {
        #====说明解密完毕=======#
        $is_opted = 0;
        if( $result =~ /decrption the .*\.bin successd/ ) {
            $status = 0; #解密成功
            $mesg = "解密成功";
            system("touch $need_update_tag");#解密成功,需要下发策略
        } elsif ( $result =~ /decrption the .*\.bin failed/ ) {
            $status = -1;
            $mesg = "解密失败";
        }
    }
    &send_status($is_opted, $status, $mesg);
}

sub update_engine() {
    my @engines = &read_conf_file($engine_config_file);
    my $engine_count = @engines;
    my @engine_ips;
    for( my $i = 0; $i < $engine_count; $i++ ) {
        if( $par{$i} == $i ) {
            my @temp = split(",", $engines[$i]);
            push( @engine_ips, $temp[1] );
        }
    }

    &save_config_file(\@engine_ips, $engine_choice);

    my $result = system($updateipsengine);
    &send_status($result, -1, "已开始下发");
}

sub updated_check() {
    my @logs = &read_conf_file($log_file);
    my $result = join " ", @logs;
    my ($is_opted, $status, $mesg) = (-1, -1, "");
    if ( $result =~ /send is over\./ ) {
        $is_opted = 0; #下发完成
        $status = 0;
        my @mesgs;
        foreach my $log ( @logs ) {
            if ( $log =~ /update host (.*) successd\./ ) {
                push( @mesgs, "下发$1成功");
            } elsif ( $log =~ /update host (.*) failed\./) {
                push( @mesgs, "下发$1失败");
            }
        }
        $mesg = join "\n", @mesgs;
        system("rm $uploaded_tag");
    }
    &send_status($is_opted, $status, $mesg);
}

sub show_page() {
    &showhttpheaders();
    &openpage("引擎升级", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'left', '引擎升级');
    &show_update();
    &closebox();
    &display_engines();
    &openbox('100%', 'left', '版本状态');
    &show_version();
    &closebox();
    &check_form();
    &closepage();
}

sub check_updated_result() {
    my @logs;
    my ($is_opted, $status, $mesg) = (-1, -1, "升级失败");
    if( -e $log_file ) {
        @logs = read_conf_file($log_file);
        foreach my $log ( @logs ) {
            if( $log =~ /your system is new, need not updata, goodbye\./ ) {
                $status = -1;
                $mesg = "系统已达到最新状态,升级失败";
                &send_status($is_opted, $status, $mesg);
                return;
            }
        }
    } else {
        &send_status($is_opted, $status, $mesg);
        return;
    }
}

sub send_status($$$) {
    #==========状态解释=========================#
    # => $status: 1 表示进行了相应操作，其他表示未操作
    #       0表示操作成功
    # => $mesg: 相关的消息
    #===========================================#
    my ($is_opted, $status, $mesg) = @_;
    my %hash;
    %hash->{'is_opted'} = $is_opted;
    %hash->{'status'} = $status;
    %hash->{'mesg'} = $mesg;
    my $json = new JSON::XS;
    my $result = $json->encode(\%hash);
    print $result;
}

sub display_engines() {
    my @lines = read_conf_file($engine_config_file);
    my $engines_count = @lines;
    printf <<EOF
    <div id="popup-mesg-box-back" class="popup-cover"></div>
    <div id="engine_list" class="popup-div">
        <div class="popup-div-head">
            <input type="image" id="hide_engine_list" src="/images/close.gif" onclick="hide_engine_list();"/>
        </div>
        <table  class="ruleslist enginelist"  cellpadding="0" cellspacing="0" width='100%'>
            <thead>
                <tr class="table-header">
                    <td class="boldbase">
                        <input type="checkbox" id="engines_all" onclick="toggle_check_all(this);" />
                    </td>
                    <td style="width:45%;" class="boldbase">
                        引擎名称
                    </td>
                    <td style="width:45%;" class="boldbase">
                        引擎IP地址
                    </td>
                </tr>
            </thead>
EOF
    ;
    if ( $engines_count > 0 ) {
        my $i = 0;
        my $bgcolor = "env";
        for( $i = 0; $i < $engines_count; $i++ ) {
            my @line_content = split(",", $lines[$i]);
            my $engine_name = $line_content[0];
            my $engine_ip = $line_content[1];
            if( $i % 2 == 0 ) {
                $bgcolor = "env";
            } else {
                $bgcolor = "odd";
            }

            printf <<EOF
            <tr class="$bgcolor">
                <td>
                    <input type="checkbox" class="engines" value="$i"/>
                </td>
                <td>$engine_name</td>
                <td>$engine_ip</td>
            </tr>
EOF
            ;
        }

        printf <<EOF
        <tr class="add-div-footer">
            <td colspan="3">
                <input class="net_button" type="button" name="update_engines" value="升级" onclick="update_engines();"/>
            </td>
        </tr>
EOF
        ;
    } else {
        no_tr(3,_('Current no content'));
    }

    printf <<EOF
        </table>
    </div>
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
    printf <<EOF
    <form name='ENGINE_UPDATE_FORM' enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr class ='odd'>
                <td class='add-div-type'>导入引擎升级文件</td>
                <td>
                    <input type="file" id="IDPS_ENGINE_FILE" name="IDPS_ENGINE_FILE"/>
                    导入引擎升级文件(*.bin)
                    <input class="net_button" type="submit" name="import_file" value="导入" onclick="import_engine_file();"/>
                </td>
            </tr>
            <tr class="table-footer"> 
                <td colspan="2">
                    <span style="float:right;">请到<a onclick='jump("http://%s")' style='cursor:pointer' color='blue'>%s</a>下载最新升级包</span>
                </td>
            </tr>
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
