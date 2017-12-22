#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:设备自检界面
#
# AUTHOR: 王琳, 245105947@qq.com
# COMPANY: capsheaf
# HISTORY:
#    2014.05.02-17:00 Created by WangLin
#
#===============================================================================


require '/var/efw/header.pl';

my $errormessage    = '';
my $warnmessage     = '';
my $notemessage     = '';
my $extraheader     =  '<link rel="stylesheet" type="text/css" href="/include/idps_system_self_scan.css"/>
                        <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css"/>
                        <script type="text/javascript" src="/include/popup_mesgs.js"></script>
                        <script type="text/javascript" src="/include/idps_system_self_scan.js"></script>';
my %par;
my %settings;

&getcgihash(\%par);
&do_action();

sub do_action() {
    my $action = $par{'ACTION'};


    &showhttpheaders();
    if ( $action ne '' ) {
        &do_check();
    } else {
        &show_page();
    }
}

sub do_check() {
    my ($opt, $status, $mesg) = ( 0, 0, "成功");
    #===========调用命令,执行检查===============#
    my $cmd = "sudo /usr/local/bin/checksystem.py -".$par{'ACTION'};
    $status = system($cmd);
    if ( $status != 0 ) {
        $mesg = "失败";
    }
    &send_result($opt, $status, $mesg);
}

sub send_result($$$) {
    #==========状态解释=========================#
    # => $opt: 0 表示操作完成
    # => $status: 0 表示操作成功，其他表示(-1)表示失败
    # => $mesg: 相关的消息
    #===========================================#
    my ($opt, $status, $mesg) = @_;
    my %hash;
    %hash->{'opt'} = $opt;
    %hash->{'status'} = $status;
    %hash->{'mesg'} = $mesg;
    my $json = new JSON::XS;
    my $result = $json->encode(\%hash);
    print $result;
}

sub show_page() {
    &openpage("设备自检", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'left', '检查设备当前健康状态');
    &show_scanning();
    &closebox();
    &closepage();
}

sub show_scanning() {
    printf <<EOF
    <div id="scanning" class="scanning">
        <div class="scanning-header">
            <div class="scanning-header-left">
                <span id="scanning-header-left-text" class="scanning-header-left-text">0%</span>
            </div>
            <div class="scanning-header-middle">
                <div id="scanning-rate" class="progress-bar">
                    <strong id="finished" class="finished"></strong>
                    <!--<div class="unfinished"></div>-->
                </div>
            </div>
            <div class="scanning-header-right">
                <input type="button" class="net_button scanning-header-right-button" id="begin_self_scan"　name="self_scan" value="立即自检" onclick="begin_scan();"/>
                <input type="button" class="net_button scanning-header-right-button" id="stop_self_scan" name="stop_scanning" value="停止" onclick="abort_scan();" disabled/>
            </div>
        </div>
        <div class="scanning-body">
            <table class="scanning-result">
                <tr>
                    <td width="60%">
                        检查内核镜像文件完整性
                    </td>
                    <td class="icon-column" width="10%" >
                        <img id="kernel_image_file" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="kernel_image_file_td" class="error-text" width="30%">
                    </td>
                </tr>
                <tr>
                    <td>
                        检查引导记录文件完整性
                    </td>
                    <td class="icon-column">
                        <img id="boot_record_file" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="boot_record_file_td" class="error-text">
                    </td>
                </tr>
                <tr>
                    <td>
                        检查设备硬件完整性
                    </td>
                    <td class="icon-column">
                        <img id="device_hardware" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="device_hardware_td" class="error-text">
                    </td>
                </tr>
                <tr>
                    <td>
                        检查执行文件完整性
                    </td>
                    <td class="icon-column">
                        <img id="executable_file" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="executable_file_td" class="error-text">
                    </td>
                </tr>
                <tr>
                    <td>
                        检查配置文件完整性
                    </td>
                    <td class="icon-column">
                        <img id="configuration_file" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="configuration_file_td" class="error-text">
                    </td>
                </tr>
                <tr>
                    <td>
                        检查系统内存完整性
                    </td>
                    <td class="icon-column">
                        <img id="system_memory" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="system_memory_td" class="error-text">
                    </td>
                </tr>
                <tr>
                    <td>
                        检查硬盘可用空间
                    </td>
                    <td class="icon-column">
                        <img id="available_space" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="available_space_td" class="error-text">
                    </td>
                </tr>
                <tr>
                    <td>
                        检查引擎库文件完整性
                    </td>
                    <td class="icon-column">
                        <img id="engine_lib_file" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="engine_lib_file_td" class="error-text">
                    </td>
                </tr>
                <tr class="last_line">
                    <td>
                        检查特征库文件完整性
                    </td>
                    <td class="icon-column">
                        <img id="rule_lib_file" class="hidden" src="../images/indicator.gif"/>
                    </td>
                    <td id="rule_lib_file_td" class="error-text">
                    </td>
                </tr>
            </table>
        </div>
    </div>
EOF
    ;
}