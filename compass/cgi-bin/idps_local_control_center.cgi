#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:Snort本级控制中心界面
#
# AUTHOR: 王琳, 245105947@qq.com
# COMPANY: capsheaf
# HISTORY:
#    2014.04.29-13:00 Created by WangLin
#
#===============================================================================


require '/var/efw/header.pl';

my %par;
my %settings;
my $config_file_dir     = "${swroot}/ipsconsole";
my $config_file         = "${swroot}/ipsconsole/settings";
my $father_config_dir   = "${swroot}/ipsfatherconsole";
my $father_config_file  = "${swroot}/ipsfatherconsole/settings";
my $father_connected    = "/var/efw/ipsfatherconsole/CONNECTED";
my $father_disconnect   = "/var/efw/ipsfatherconsole/DISCONNECT";
my $logips_manager      = "/usr/local/bin/logips_manager -c";
my $distributeCM        = "/usr/local/bin/distributeCM";
my $updatechildstatus   = "/usr/local/bin/updatechildstatus -f";
my $errormessage        = '';
my $warnmessage         = '';
my $notemessage         = '';
my $extraheader         = '<link rel="stylesheet" type="text/css" href="/include/idps_local_control_center.css"/>
                            <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css"/>
                            <link rel="stylesheet" type="text/css" href="/include/waiting_mesgs.css"/>
                            <script type="text/javascript" src="/include/popup_mesgs.js"></script>
                            <script type="text/javascript" src="/include/waiting_mesgs.js"></script>';

#========页面主体==================#
&make_file();
&getcgihash(\%par);
&doaction();
#==================================#

sub make_file(){
    if(!-e $config_file_dir)
    {
        system("mkdir -p $config_file_dir");
    }

    if(!-e $config_file)
    {
        system("touch $config_file");
    }
}

sub doaction() {
    readhash($config_file, \%settings);
    if($par{'save'} ne '') {
        my ( $if_can, $errormesg ) = &save_check(\%par);
        if ( $if_can ) {
            $settings{'CONSOLENAME'} = $par{'CONSOLENAME'};
            $settings{'CONSOLEIP'} = $par{'CONSOLEIP'};
            $settings{'REPORTEVENT'} = $par{'REPORTEVENT'};
            $settings{'ENABLED'} = $par{'ENABLED'};
            if( $par{'ENABLED'} ne 'on' ) {
                $settings{'ENABLED'} = 'off';
            }
            &writehash($config_file, \%settings);
            my $result = system( $logips_manager );
            if( $result == 0 ) {
                $notemessage = "保存成功";
            } else {
                $notemessage = "保存失败，错误代码$result";
            }
        } else {
            $errormessage = $errormesg;
        }
    } elsif ( $par{'syn_now'} ne '') {
        my $result_update       = system( $updatechildstatus );
        my $result_distribute   = system( $distributeCM );
        if( $result_update == 0 && result_distribute == 0 ) {
            $notemessage = "同步成功";
        } else {
            $errormessage = "同步异常,错误代码$result_update和$result_distribute";
        }
    }
    
    &show_page();
}

sub save_check($) {
    #=====================================#
    #
    #   如果能保存，返回大于0的数
    #   如果不能保存，返回0和错误消息
    #
    #=====================================#
    my $data = shift;
    my ( $if_can, $errormesg ) = ( 0, "" );
    #=====================================#
    $if_can = 1;
    #=====================================#
    return ( $if_can, $errormesg );
}

sub show_page() {
    &showhttpheaders();
    &openpage("本级控制中心", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &openbox('100%', 'left', '本级控制中心');
    &display_control_center();
    &closebox();
    &openbox('100%', 'left', '上级状态');
    &display_father_control_status();
    &closebox();
    &check_form();
    &closepage();
}

sub display_control_center(){
    my @REPORTEVENT = split(/\|/, $settings{'REPORTEVENT'});
    my %REPORTEVENT_checked;
    foreach my $REPORTEVENT_item ( @REPORTEVENT ) {
        $REPORTEVENT_checked{$REPORTEVENT_item} = "checked";
    }

    my $ENABLED_checked = "";
    if( $settings{'ENABLED'} eq 'on') {
        $ENABLED_checked = "checked";
    }
    printf <<EOF
    <form name='CONTROL_CENTER_FORM' enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tbody>
                <tr class ='odd'>
                    <td class="add-div-type">控制中心名称 *</td>
                    <td>
                        <input type="text" name="CONSOLENAME" value="$settings{'CONSOLENAME'}"/>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class="add-div-type">IP地址 *</td>
                    <td>
                        <input type="text" name="CONSOLEIP" value="$settings{'CONSOLEIP'}"/>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class="add-div-type">上报事件</td>
                    <td>
                        <div class="single_line">
                            <input type="checkbox" id="REPORTEVENT_high" name="REPORTEVENT" value="high" $REPORTEVENT_checked{"high"}/>
                            <label for="REPORTEVENT_high">高危险事件</label>
                        </div>
                        <div class="single_line">
                            <input type="checkbox" id="REPORTEVENT_medium" name="REPORTEVENT" value="medium" $REPORTEVENT_checked{"medium"}/>
                            <label for="REPORTEVENT_medium">中危险事件</label>
                        </div>
                        <div class="single_line">
                            <input type="checkbox" id="REPORTEVENT_low" name="REPORTEVENT" value="low" $REPORTEVENT_checked{"low"}/>
                            <label for="REPORTEVENT_low">低危险事件</label>
                        </div>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class="add-div-type">启用</td>
                    <td>
                        <input type="checkbox" name="ENABLED" $ENABLED_checked/>
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr class="table-footer"> 
                    <td colspan="2">
                        <input class="net_button" type="submit" name="save" value="保存"/>
                        <input class="net_button" type="submit" name="syn_now" value="同步控制台配置"/>
                    </td>
                </tr>
            </tfoot>
        </table>
    </form>
EOF
    ;
}

sub display_father_control_status()
{
    my %father_settings;
    if ( -e $father_config_file ) {
        &readhash($father_config_file, \%father_settings);
    }

    if ( -e $father_connected && -e $father_config_file ) {
        $father_status = "<span class='connected'>已连接</span>";
    } elsif ( -e $father_disconnect && -e $father_config_file ) {
        $father_status = "<span class='disconnected'>未连接</span>";
    } elsif ( -e $father_config_file && !-e $father_connected && !-e $father_disconnect ) {
        $father_status = "<span class='disconnected'>未连接</span>";
    }
    printf <<EOF  
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr class ='odd'>
            <td class="add-div-type">上级控制中心名称</td>
            <td>
                $father_settings{'CONSOLENAME'}
            </td>
        </tr>
        <tr class ='odd'>
            <td width="20%" class="add-div-type">上级控制中心IP地址</td>
            <td>
                $father_settings{'CONSOLEIP'}
            </td>
        </tr>
        <tr class ='odd'>
            <td width="20%" class="add-div-type">连接状态</td>
            <td>
                $father_status
            </td>
        </tr>
    </table>
EOF
    ;
}

sub check_form() {
    printf <<EOF
    <script language="JavaScript">
        var object = {
            'form_name':'CONTROL_CENTER_FORM',
            'option'   :{
                'CONSOLENAME':{
                   'type':'text',
                   'required':'1',
                   'check':'name|',
                   'ass_check':function(){
                        
                    }
                },
                'CONSOLEIP':{
                   'type':'text',
                   'required':'1',
                   'check':'ip|',
                   'ass_check':function(){
                        
                    }
                }
            }
        }

        var check = new ChinArk_forms();
        //check._get_form_obj_table("CONTROL_CENTER_FORM");
        check._main(object);
    </script>
EOF
    ;
}
