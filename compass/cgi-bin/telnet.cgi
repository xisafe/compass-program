#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: telnet代理页面
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2014/04/11-09:00
#===============================================================================

require '/var/efw/header.pl';

my $setting_dir = "/var/efw/telnetproxy";
my $setting_file = "/var/efw/telnetproxy/settings";
my $default_setting_file = "${swroot}/telnetproxy/default_settings";
my $cmd = 'sudo /usr/local/bin/restarttelnetproxy.py >/dev/null';
my %par;
my %save;
my $titlename = _('Telnet Proxy');
my $extraheaders = '<script type="text/javascript" src="/include/serviceswitch.js"></script>';
my $errormessage='';
my $warnmessage='';
my $notemessage='';

&init();
&getcgihash(\%par);
&do_action();
&showhttpheaders();
&openpage($titlename, 1, $extraheaders);
&openbigbox($errormessage, $warnmessage, $notemessage);
&display_switch();
&closebigbox();
&check_form();
&closepage();


sub init() {
    if(! -e $setting_dir){
        system('mkdir -p $setting_dir');
    }
    
    if(! -e $setting_file){
        system('touch $setting_file');
    }

    if(! -e $default_setting_file){
        system('touch $default_setting_file');
        system("echo TELNET_ENABLED=off > $default_setting_file");
        system("echo GREEN_ENABLED=untransparent >> $default_setting_file");
        system("echo ORANGE_ENABLED=untransparent >> $default_setting_file");
        system("echo GREEN_PORT=1123 >> $default_setting_file");
        system("echo ORANGE_PORT=1123 >> $default_setting_file");
    }
}
sub do_action(){
    #存在par{'ACTION'}则处理信息并存入配置文件。
    if ($par{'ACTION'} eq 'save') {
        my $needrestart = 0;
        #保存配置信息,文件不存在则创建。
        my %savehash = ();
        $savehash{'TELNET_ENABLED'} = "on";#能点击保存说明是开启状态
        $savehash{'GREEN_ENABLED'} = $par{'GREEN_ENABLED'};
        $savehash{'GREEN_PORT'} = $par{'GREEN_PORT'};
        if($par{'GREEN_ENABLED'} eq 'transparent') {
            #设置为透明方式就启用默认端口号
            $savehash{'GREEN_PORT'} = 23;
        }
        $savehash{'ORANGE_ENABLED'} = $par{'ORANGE_ENABLED'};
        $savehash{'ORANGE_PORT'} = $par{'ORANGE_PORT'};
        if($par{'ORANGE_ENABLED'} eq 'transparent') {
            #设置为透明方式就启用默认端口号
            $savehash{'ORANGE_PORT'} = 23;
        }
        if($par{'ORANGE_ENABLED'} eq '') {
            #说明当前没有启用DMZ
            $savehash{'ORANGE_ENABLED'} = "untransparent";
            $savehash{'ORANGE_PORT'} = 23;
        }
        writehash($setting_file,\%savehash);
        system($cmd);
        $notemessage = "已成功保存当前修改";
    }
    if ($par{'ACTION'} eq 'switch') {
        my %savehash = ();
        if (-e $setting_file) {
           readhash($setting_file,\%savehash);
        }
        else{
           readhash($default_setting_file,\%savehash);
        }
        if($savehash{'TELNET_ENABLED'} eq 'on'){
            $savehash{'TELNET_ENABLED'} = 'off';
        } else {
            $savehash{'TELNET_ENABLED'} = 'on';
        }
        writehash($setting_file,\%savehash);
        system($cmd);
    }
}

sub display_switch(){
    my %savedhash = ();
    if (-e $setting_file) {
       readhash($setting_file,\%savedhash);
    }
    else{
       readhash($default_setting_file,\%savedhash);
    }
    my $TELNET_ENABLED = $savedhash{'TELNET_ENABLED'};
    
    printf <<END
    <script type="text/javascript">
        \$(document).ready(function() {
            var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
            var sswitch = new ServiceSwitch("$ENV{'SCRIPT_NAME'}", SERVICE_STAT_DESCRIPTION);
    
        });
        function change_switch_value() {
            \$("#switch_value").attr("value","save");
        }
        function toggle_switch(tr, value) {
            if(value == "untransparent") {
                document.getElementById(tr).style.display = "table-row";
            } else {
                document.getElementById(tr).style.display = "none";
            }
        }
    </script>
    <form name="TELNET_FORM" enctype='multipart/form-data' method='post' class="service-switch-form" id="access-form" action='$ENV{'SCRIPT_NAME'}'>
        <table cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td valign="top">
                    <div id="access-policy" class="service-switch">
                        <div >
                            <span class="title">%s</span>
                            <span class="image"><img class="$TELNET_ENABLED" align="absbottom" src="/images/switch-%s.png" alt="" border="0"/></span>
                        </div>
                        <div id="access-description" class="description" %s>%s</div>
                        <div id="access-policy-hold" class="spinner working">%s</div>
                        <div class="options-container efw-form" %s>
                        <div class="section first" >
                            要关闭Telnet代理服务，使用上面的开关关闭它
                            <input type="hidden" name="TELNET_ENABLED" value="$TELNET_ENABLED" />
                        </div>
      
  
END
, escape_quotes(_("Telnet代理服务正在启动，请等待...")),
escape_quotes(_("Telnet代理服务正在关闭，请等待...")),
escape_quotes(_("配置已经保存，Telnet代理服务正在重启. 请等待...")),
,'Telnet代理'
,$TELNET_ENABLED eq 'on'?'on':'off',
,$TELNET_ENABLED eq "on" ? 'style="display:none"' : '',
, _("要开启Telnet代理服务，点击上面按钮开启")
, _("Telnet代理服务正在被重启，请等待......"),
,$TELNET_ENABLED eq "on" ? '' : 'style="display:none"'
    ;
    openbox('100%', 'left', $titlename);
    display_edit();
    closebox();
    printf <<EOF
                    </div>
                </td>
            </tr>
        </table>
    </form>
EOF
    ;
}

sub display_edit(){
    my %savedhash;
    my %selected_g=();
    my %selected_o=();
    my ($g_hidden, $o_hidden) = ("hidden", "hidden");
    if( -e $default_setting_file) {
        readhash($default_setting_file, \%savedhash);
    }
    if( -e $setting_file) {
        readhash($setting_file, \%savedhash);
    }
    $selected_g{$savedhash{'GREEN_ENABLED'}} = "selected='selected'";
    $selected_o{$savedhash{'ORANGE_ENABLED'}} = "selected='selected'";
    if($savedhash{'GREEN_ENABLED'} eq 'untransparent') {
        $g_hidden = "";
    }
    if($savedhash{'ORANGE_ENABLED'} eq 'untransparent') {
        $o_hidden = "";
    }
    printf <<EOF
    <table border='0' cellspacing="0" cellpadding="4">
        <tr class="odd">
            <td width="15%" class="add-div-width">%s<font color="$colourgreen">%s区</font></td>
            <td >
                <select name='GREEN_ENABLED' onchange="toggle_switch('green_port_tr',this.value);">
                    <option value="transparent" $selected_g{'transparent'}>透明</option>
                    <option value="untransparent" $selected_g{'untransparent'}>不透明</option>
                </select>
            </td>
        </tr>
        <tr id="green_port_tr" class="odd $g_hidden">
            <td width="15%" class="add-div-width"><font color="$colourgreen">%s区</font>端口</td>
            <td>
                <input name="GREEN_PORT" value="$savedhash{'GREEN_PORT'}"/>
            </td>
        </tr>
EOF
    ,_('Enabled on')
    ,_('GREEN')
    ,_('GREEN')
    ;

    if (orange_used()) {
        printf <<EOF
        <tr class="odd">
            <td class="add-div-width">%s<font color="$colourorange">%s区</font></td>
            <td >
                <select name='ORANGE_ENABLED' onchange="toggle_switch('orange_port_tr',this.value);">
                    <option value="transparent" $selected_o{'transparent'}>透明</option>
                    <option value="untransparent" $selected_o{'untransparent'}>不透明</option>
                </select>
            </td>
        </tr>
        <tr id="orange_port_tr" class="odd $o_hidden">
            <td width="15%" class="add-div-width"><font color="$colourorange">%s区</font>端口</td>
            <td>
                <input name="ORANGE_PORT" value="$savedhash{'ORANGE_PORT'}"/>
            </td>
        </tr>
EOF
        ,_('Enabled on')
        ,_('ORANGE')
        ,_('ORANGE')
        ;
    }

    printf <<EOF
        <tr class="table-footer">
            <td colspan="2">
                <input class='submitbutton net_button' type='submit' name='submit' value='保存' onclick="\$('.service-switch-form').unbind('submit');change_switch_value();"/>
                <input id="switch_value" type="hidden" name="ACTION" value="switch" />
            </td>
        </tr>
    </table>
EOF
    ;
}

sub check_form(){

    printf <<EOF
    <script>
    var object = {
       'form_name':'TELNET_FORM',
       'option'   :{
            'GREEN_PORT':{
               'type':'text',
               'required':'1',
               'check':'port|',
            },
            'ORANGE_PORT':{
               'type':'text',
               'required':'1',
               'check':'port|',
            },
        }
    }
    var check = new ChinArk_forms();
    //check._get_form_obj_table("TELNET_FORM");
    check._main(object);
    </script>
EOF
    ;
}