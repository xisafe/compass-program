#!/usr/bin/perl
#
############################################
# AUTHOR:sandfoam
#
# DATE:2012年 07月 18日 星期三 10:16:12 CST
#
# FILE:linkage.pl
#
# TO DO:
############################################
#

require '/var/efw/header.pl';

my $h3c_default_settings = "${swroot}/Linkage/default/settings";
my $h3c_settings = "${swroot}/Linkage/settings";
my $conffile="/var/efw/Linkage/config";
my $autoconf="/var/efw/Linkage/rule";
my $needreload="/var/efw/Linkage/needreload";
my $snmp_settings = "/var/efw/snmp/settings";
my $errormessage = ();
my %h3c_settings_hash = ();
my %h3c_settings_hash2 = ();
my %h3c_rule_hash = ();
my %h3c_black_rule_hash = ();
my %par = ();
my $reload = 0;
my $EDIT_PNG="/images/edit.png";
my $DELETE_PNG="/images/delete.png";
my $ON_PNG="/images/on.png";
my $OFF_PNG="/images/off.png";
my %policies = (
            "ALLOW" => "允许",
            "DROP" => "丢弃",
            "REJECT" => "拒绝"
);

if (-e $h3c_default_settings) {
    &readhash($h3c_default_settings, \%h3c_settings_hash);
}
if (-e $h3c_settings) {
    &readhash($h3c_settings, \%h3c_settings_hash);
}
my $service_status = $h3c_settings_hash{'ENABLED'};
if (!$service_status) {
	$service_status = "off";
}
sub display_switch() {
	
    printf <<END
    <script type="text/javascript">
        \$(document).ready(function() {
            var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
            var sswitch = new ServiceSwitch('linkage.cgi', SERVICE_STAT_DESCRIPTION);
			initial();
        });
		function hideRule()
		{
			var status = \$(".image img").attr("class");
			if(status=='off'){
			   \$("#switch").css('display','block');
			}
			if(status=='on'){
			   \$("#switch").css('display','none'); 
			}
			\$(".ruletr").hide();
			\$(".emptytip").show();
		}
		function initial()
		{
			var status = \$(".image img").attr("class");
			if(status=='on'){
			   \$("#switch").css('display','block');
			}
			if(status=='off'){
			   \$("#switch").css('display','none'); 
			}
		}
    </script>

    <form name="LINKAGE_FORM1" enctype='multipart/form-data' class="service-switch-form" id="ssh-form" method='post' action='$ENV{'SCRIPT_NAME'}'>
    <table cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td valign="top">
                <div id="access-policy" class="service-switch">
                    <div><span class="title"> %s</span>
                        <span class="image"><img class="$service_status" align="absbottom" src="/images/switch-$service_status.png" alt="" border="0" onclick='hideRule();'/></span>
						</div>
                        <div id="access-description"  class="description %s">%s</div>
                        <div id="access-policy-hold" class="spinner working">%s</div>
                        <div id="access-options" class="options-container %s">
                        <input class='action' type='hidden' name='ACTION_2' value='switch' />
                        <INPUT TYPE="hidden" NAME="line" class="line">
                        <INPUT TYPE="hidden" id='snmp_enabled' value='$snmp_enabled' />
            
END
    ,
    escape_quotes(_("设备联动正在启动，请稍后...")),
    escape_quotes(_("设备联动正在关闭，请稍后...")),
    escape_quotes(_("正在应用配置. 请等待...")),
    _('开启设备联动'),
    $service_status eq 'on' ? 'hidden' : '',
    _("请用上面的切换按钮启动设备联动,开启设备联动后将会自动开启SNMP服务!<br />设备联动能够与入侵检测配合抵制攻击。"),
    _("设备联动正在关闭. 请等待..."),
    $service_status eq 'off' ? 'hidden' : '',
    ;
printf <<END
                                <div class="divider"><img src="/images/clear.gif" width="1" height="1" alt="" border="0" /></div>
                            </div>
                        </div>
                    </div>
                </div>
            </td>
        </tr>
    </table>
	</form>
END
    ;

    display_devices(($par{'ACTION'} eq 'edit'), $lineno);
}

sub reset_values() {
    %par = ();
}
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'LINKAGE_FORM',
       'option'   :{
                    'dev_ip':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|'
                             },
                    'dev_name':{
                               'type':'text',
                               'required':'1',
                               'check':'name|',
                               'ajax': '1',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var flag = 0;
                                                        var input_name = eve._getCURElementsByName("dev_name","input","LINKAGE_FORM")[0].value;                                                    
                                                        input_name = input_name.replace(/(^\\s*)|(\\s*\$)/g,"");
                                                        var line = eve._getCURElementsByName("line","input","LINKAGE_FORM")[0].value;
                                                        if (!eve.name){
                                                            \$.ajax({
                                                                type : "get",
                                                                url : '/cgi-bin/chinark_back_get.cgi',
                                                                async : false,
                                                                data : 'path=/var/efw/Linkage/config',
                                                                success : function(data){
                                                                    eve.name = data;
                                                                }
                                                            });
                                                        }      
                                                        var exist = eve.name.split('\\n');
                                                        for (var i = 0; i < exist.length; i++) {
                                                            var tmp = exist[i].split(",");    
                                                            if(tmp[0] == input_name){
                                                                flag = 1;
                                                                break;
                                                            }
                                                        }   
                                                        if(flag && line == "none"){ 
                                                            msg = input_name+"IDS设备名称已存在，请更换！" 
                                                        }                                                                             
                                                        return msg;
                                                      }
                             }
                 }
         };
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("LINKAGE_FORM");
    </script>
EOF
;
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
sub save_dev{
    my $linenum = shift;
    my $dev_name = shift;
    my $dev_ip = shift;
    my $new_line = "$dev_name,$dev_ip";
    #读取原有的联动数据
    my @back_lines = read_config_file($conffile);
    my @save_lines;  
    #当添加设备时将原有数据存至保存数据的数组中再添加新的数据
    # modified by squall:
    # add new function to reject disallowed data
    if ($par{"ACTION"} eq "add") {
        foreach my $elem (@back_lines) {
            push(@save_lines,$elem);
        }
        my $valid = 1;
        my ($dev,$ip);
        foreach my $elem (@back_lines) {
            ($dev,$ip) = split(",",$elem); 
            if ($dev_name eq $dev or $dev_ip eq $ip) {
                $valid = 0;
                last;
            }
        }
        if ($valid) {
            push(@save_lines,$new_line);
            save_config_file(\@save_lines,$conffile);
            system("touch $needreload");
        } else {
            errorbox(_("设备名称或设备ip重复，添加失败！"));
        }
        
        %par=();
    }
    #修改设备
    else{
        my $valid = 1;
        my ($dev,$ip);
        for (my $num=0;$num<@back_lines ;$num++) {

            if ($num != $linenum) {
                ($dev,$ip) = split(",",$back_lines[$num]); 
                if ($dev_name eq $dev or $dev_ip eq $ip) {
                    $valid = 0;
                    last;
                }
            }
        }
        # change only if valid
        if ($valid) {
            for (my $num=0;$num<@back_lines ;$num++) {
                if ($num != $linenum) {
                    push(@save_lines,$back_lines[$num]);
                } else {
                    push(@save_lines,$new_line);
                }
            }   
            save_config_file(\@save_lines,$conffile);
            system("touch $needreload");
        } else {
            #save_config_file(\@back_lines,$conffile);
            errorbox(_("设备名称或设备ip重复，修改失败！"));
        }

        %par=();
    }
    # end -------------------------------------
}

sub save_file{
    my $linenum = shift;
    my $src_ip = shift;
    my $src_port = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    my $prot = shift;
    my $policy = shift;
    my $enabled = shift;
    if (! check_value($src_ip,$src_port,$dst_ip,$dst_port)) {
        return 0;
    }
    if (!$enabled) {
        $enabled = "off";
    }
    if ($prot eq "ICMP") {
        $src_port="";
        $dst_port="";
    }
    my $new_line = "$src_ip,$src_port,$dst_ip,$dst_port,$prot,$policy,$enabled";
    #读取原有的规则数据
    my @back_lines = read_config_file($conffile);
    my @save_lines;
    #当添加规则时将原有数据存至保存数据的数组中再添加新的数据
    if ($par{"ACTION"} eq "add") {
        foreach my $elem (@back_lines) {
            push(@save_lines,$elem);
        }
        push(@save_lines,$new_line);
        save_config_file(\@save_lines,$conffile);
        system("touch $needreload");;
        %par=();
    }
    #修改规则
    else{
        for (my $num=0;$num<@back_lines ;$num++) {
            if ($num != $linenum) {
                push(@save_lines,$back_lines[$num]);
            }
            else{push(@save_lines,$new_line);}
        }   
        save_config_file(\@save_lines,$conffile);
        system("touch $needreload");;
        %par=();
    }
}

sub delete_dev{
    my $linenum = shift;
    my @back_lines = read_config_file($conffile);
    my @save_lines; 
    for (my $num=0;$num<@back_lines ;$num++) {
        if ($num != $linenum) {
            push(@save_lines,$back_lines[$num]);
        }
    }

    save_config_file(\@save_lines,$conffile);
    system("touch $needreload");;
    %par=();
}
sub delete_line{
    my $linenum = shift;
    my @back_lines = read_config_file($conffile);
    my @save_lines; 
    for (my $num=0;$num<@back_lines ;$num++) {
        if ($num != $linenum) {
            push(@save_lines,$back_lines[$num]);
        }
    }

    save_config_file(\@save_lines,$conffile);
    system("touch $needreload");;
    %par=();
}
sub toggle_line{
    my $linenum = shift;
    my $enabled = shift;
    my @back_lines = read_config_file($conffile);
    my @save_lines; 
    for (my $num=0;$num<@back_lines ;$num++) {
        if ($num != $linenum) {
            push(@save_lines,$back_lines[$num]);
        }
        else{
            if ($enabled eq 'off') {
                $back_lines[$num]=~s/off$/on/;
            }
            else{
                $back_lines[$num]=~s/on$/off/;
            }
            push(@save_lines,$back_lines[$num]);
        }
    }
    save_config_file(\@save_lines,$conffile);
    system("touch $needreload");;
    %par=();
}
sub check_value{
    my $src_ip = shift;
    my $src_port = shift;
    my $dst_ip = shift;
    my $dst_port = shift;
    if (!is_ipaddress($src_ip) && $src_ip) {
        $errormessage = "源IP地址".$src_ip."有误!";
        return 0;
    }
    if (($par{'prot'} ne "ICMP")  && $src_port) {
        if (!($src_port =~ /^(\d+)\:(\d+)$/)) {
            if (!validport($src_port)) {
                $errormessage = "源端口号".$src_port."有误!";
                return 0;
            }
        }
        else{
            my @tmp = split(/\:/,$$src_port);
            if (!validport($tmp[0]) || !validport($tmp[1]) || $tmp[0] > $tmp[1] || $tmp[0] == $tmp[1]) {
                $errormessage = "源端口号范围".$src_port."有误!";
                return 0;
            }
        }
    }
    
    if (!is_ipaddress($dst_ip) && $dst_ip) {
        $errormessage = "目标IP地址".$dst_ip."有误!";
        return 0;
    }
    if (($par{'prot'} ne "ICMP") && $dst_port) {
        if (!($dst_port =~ /^(\d+)\:(\d+)$/)) {
            if (!validport($dst_port)) {
                $errormessage = "目标端口号".$dst_port."有误!";
                return 0;
            }
        }
        else{
            my @tmp = split(/\:/,$$dst_port);
            if (!validport($tmp[0]) || !validport($tmp[1]) || $tmp[0] > $tmp[1] || $tmp[0] == $tmp[1]) {
                $errormessage = "目标端口号范围".$dst_port."有误!";
                return 0;
            }
        }
    }
    return 1;
}

sub display_config () {
    #===读取SNMP配置===#
    my %snmp_settings;
    if ( -e $snmp_settings ) {
        readhash($snmp_settings,\%snmp_settings);
    }
    my $snmp_status = "关闭";
    my $status_class = "close";
    my $snmp_version = $snmp_settings{'PROT'};
    my %display_config;
    if ( -e $h3c_default_settings ) {
        readhash($h3c_default_settings,\%display_config);
    }
    if ( -e $h3c_settings ) {
        readhash($h3c_settings,\%display_config);
    }
    my %level_checked;
    $level_checked{$display_config{'LEVEL'}} = "checked";
    if(!$h3c_settings_hash{'LEVEL'}) {
        $level_checked{'authPriv'} = "checked";
    }
    if($snmp_settings{'ENABLED'} eq 'on') {
        $snmp_status = "开启";
        $status_class = "open";
    }

    #&openbox('100%', 'left', "设备联动状态");
    printf <<EOF
    <div class="congif-box">
        <form name="LINKAGE_FORM" method='post' action='$self' enctype='multipart/form-data'>
            <table width="100%" border='0' cellspacing="0" cellpadding="4" style="padding:0px;">
                <tr><td colspan="2" class="tr-head" style="font-size:15px">设备联动配置</td></tr>
                <tr class="odd">
                    <td class="add-div-type">SNMP状态</td>
                    <td>
                        <span class="$status_class">$snmp_status</span>
                    </td>
                </tr>
                <tr class="odd">
                    <td class="add-div-type">SNMP版本</td>
                    <td>
                        $snmp_version
                    </td>
                </tr>
                <tr class="odd">
                    <td class="add-div-type">认证等级 *</td>
                    <td>
                        <input type="radio" name="auth_level" id="authPriv" value="authPriv" $level_checked{'authPriv'}/>
                        <label for="authPriv">认证加密</label>
                        <input type="radio" name="auth_level" id="authNoPriv" value="authNoPriv" $level_checked{'authNoPriv'}/>
                        <label for="authNoPriv">认证不加密</label>
                        <input type="radio" name="auth_level" id="noAuthNoPriv" value="noAuthNoPriv" $level_checked{'noAuthNoPriv'}/>
                        <label for="noAuthNoPriv">不认证不加密</label>
                    </td>
                </tr>
                <tr  class="table-footer">
                    <td colspan="2">
                        <input class='submitbutton net_button' type='submit' name='submit' value='保存' />
                        <input type="hidden" name="ACTION" value="save_config" />
                    </td>
                </tr>
            </table>
        </form>
    </div>
EOF
    ;
    #&closebox();
}

sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;
    my @rules = read_config_file($conffile);
    my $checked = "";
    my %selected;
=p   注释以前的代码，以备将来改动需要还原 
    my ($src_ip,$src_port,$dst_ip,$dst_port,$prot,$policy,$enabled);
    if (($is_editing) && ($par{'sure'} ne 'y')) {
        my @tmp = split(/,/,$rules[$line]);
        $src_ip = $tmp[0];
        $src_port = $tmp[1];
        $dst_ip = $tmp[2];
        $dst_port = $tmp[3];
        $prot = $tmp[4];
        $policy = $tmp[5];
        $enabled = $tmp[6];
    }
    else{
        $src_ip = $par{'src_ip'};
        $src_port = $par{'src_port'};
        $dst_ip = $par{'dst_ip'};
        $dst_port = $par{'dst_port'};
        $prot = $par{'prot'};
        $policy = $par{'policy'};
        $enabled = $par{'checked'};
    }
    if ($enabled eq "on") {
        $checked="checked";
    }
=cut    
    ###新代码
    my ($dev_name,$dev_ip);
    if (($is_editing) && ($par{'sure'} ne 'y')) {
        my @tmp = split(/,/,$rules[$line]);
        $dev_name = $tmp[0];
        $dev_ip = $tmp[1];
    }
    else{
        $dev_name = $par{'dev_name'};
        $dev_ip = $par{'dev_ip'};
    }
    my $action = 'add';
    my $title = _('添加联动设备');
    my $buttontext=_("Add");
    if ($is_editing || $par{'ACTION'} eq "modify") {
        $action = 'modify';
        $title = _('编辑联动设备');
        $buttontext = _("Edit");
    }
    if($par{'ACTION'} eq 'edit' || $errormessage ne '') {
        $show = "showeditor";
    }
    my $style;
    $selected{$prot}="selected";
    $selected{$policy}="selected";
    if ($prot eq "ICMP") {
        $style="style='display:none'";
    }

    openeditorbox($title, $title, $show, "addqosdevice", @errormessages);
    printf <<EOF
    </form>
    <form name="LINKAGE_FORM" method='post' action='$self' enctype='multipart/form-data'>
     <table width="100%" cellpadding="0" cellspacing="0">
     <!--
     <tr class="env">
        <td class="add-div-type">源IP </td>
        <td><input type="text" value="$src_ip" name="src_ip" /></td>
     </tr>
     <tr id="srcport" $style class="odd">
        <td class="add-div-type">源端口 </td>
        <td><input type="text" value="$src_port" name="src_port" /></td>
     </tr>
     <tr class="env">
        <td class="add-div-type">目标IP </td>
        <td><input type="text" value="$dst_ip" name="dst_ip" /></td>
     </tr>
     <tr id="dstport" $style class="odd">
        <td class="add-div-type">目标端口 </td>
        <td><input type="text" value="$dst_port" name="dst_port" /></td>
     </tr>
     <tr class="env">
        <td class="add-div-type">协议</td>
        <td><select id="protocal" name="prot" style="width:125px">
        <option value="TCP" $selected{'TCP'} >TCP</option>
        <option value="UDP" $selected{'UDP'} >UDP</option>
        <option value="ICMP" $selected{'ICMP'} >ICMP</option>
        </select></td>
     </tr>
     <tr class="odd">
        <td class="add-div-type">策略</td>
        <td><select name="policy" style="width:125px">
        <option value="ALLOW" $selected{'ALLOW'} >允许</option>
        <option value="DROP" $selected{'DROP'} >丢弃</option>
        <option value="REJECT" $selected{'REJECT'} >拒绝</option>
        </select></td>
     </tr>
     <tr class="env">
        <td class="add-div-type">启用</td>
        <td><input type="checkbox" $checked name="checked" /></td>
     </tr>
     -->
     <tr class="env">
        <td class="add-div-type">IDS设备名称 </td>
        <td><input type="text" value="$dev_name" name="dev_name" /></td>
     </tr>     
     <tr class="odd">
        <td class="add-div-type">IDS设备IP </td>
        <td><input type="text" value="$dev_ip" name="dev_ip" /></td>
     </tr>
EOF
;

   printf <<EOF
        </table>
    <input type="hidden" name="ACTION" value="$action">
    <input type="hidden" name="sure" value="y">
    <input type="hidden" name="line" value="$line">
EOF
;
                        
    &closeeditorbox($buttontext, _("Cancel"), "routebutton", "createdevice", "$ENV{SCRIPT_NAME}");
}
sub display_devices($$) {

    my $is_editing = shift;
    my $line = shift;
   
    printf <<END
	<div id="switch">
END
;	
    &display_config();
    display_add($is_editing, $line);
    #显示已有手动数据
=p  注释以前代码       
    printf <<END
        
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr><td colspan="8" class="boldbase" style="font-size:15px">自主规则</td></tr>
        <tr>
            <td class="boldbase" style="width:10%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>
            <td class="boldbase" style="width:10%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>
            <td class="boldbase" style="width:10%;">%s</td>     
            <td class="boldbase" style="width:10%;">%s</td>
            <td class="boldbase" style="width:10%;">%s</td>
            <td class="boldbase" style="width:10%;">%s</td>
        </tr>
    
END
    , _('序号')
    , _('源IP')
    , _('源端口号')
    , _('目标IP')
    ,_('目标端口号')
    ,_('协议')
    ,_('策略')
    ,_('活动/动作')
;
    foreach my $line (read_config_file($conffile)) {
        my @tmp = split(/,/,$line);
        my $linenum=$num + 1;
        my $enabled_gif = $ON_PNG;
        my $enabled_action = "on";
        if ($tmp[6] eq "off") {
            $enabled_gif = $OFF_PNG;
            $enabled_action = "off";
        }
        if (!$tmp[0]) {
            $tmp[0] = "任意";
        }
        
        if (!$tmp[2]) {
            $tmp[2] = "任意";
        }
        if ($tmp[4] eq "ICMP") {
            $tmp[1] = "无";
            $tmp[3] = "无";
        }
        elsif (!$tmp[1]) {
            $tmp[1] = "任意";
        }
        if (!$tmp[3] && $tmp[4] ne "ICMP") {
            $tmp[3] = "任意";
        }
        my $classes="class='odd'";
        if ($num % 2) {
            $classes="class='env'";
        }
printf <<EOF
        <tr $classes>
            <td>$linenum</td>
            <td>$tmp[0]</td>
            <td>$tmp[1]</td>
            <td>$tmp[2]</td>
            <td>$tmp[3]</td>
            <td>$tmp[4]</td>
            <td>$policies{$tmp[5]}</td>
            <td>
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                    <input class='imagebutton' type='image' NAME="submit" SRC="$enabled_gif" ALT="$enabled_alt" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="$enabled_action">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$num">
                </form>
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                    <input class='imagebutton' type='image' NAME="submit" SRC="$EDIT_PNG" ALT="%s" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="edit">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$num">
                </form>
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left" onsubmit="return confirm('确认删除？')">
                    <input class='imagebutton' type='image' NAME="submit" SRC="$DELETE_PNG" ALT="%s" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$num">
                </form>
            </td>
        </tr>
EOF
;
        $num++;
    }
if (!$num){
    no_tr(8,_('Current no content'));
}
print "</table>";

if($num != 0){
            printf <<EOF
        
        <table class="list-legend" cellpadding="0" cellspacing="0">
          <tr>
            <td class="boldbase">
              <B>%s:</B>
            <IMG SRC="$ENABLED_PNG" title="%s" />
            %s
            <IMG SRC='$DISABLED_PNG' title="%s" />
            %s
            <IMG SRC="$EDIT_PNG" title="%s" />
            %s
            <IMG SRC="$DELETE_PNG" title="%s" />
            %s</td>
          </tr>
        </table>
EOF
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
;
}
=cut
    ###显示现在的规则    
    my $num = 0;
    printf <<END
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr><td colspan="4" class="boldbase" style="font-size:15px">联动设备</td></tr>
        <tr>
            <td class="boldbase" style="width:10%;">序号</td>
            <td class="boldbase" style="width:30%;">IDS设备名称</td>
            <td class="boldbase" style="width:30%;">IDS设备IP</td>
            <td class="boldbase" style="width:20%;">活动/动作</td>
        </tr>    
        
END
;        
    foreach my $line(read_config_file($conffile)){
        my @tmp = split(/,/,$line);
        my $linenum=$num + 1; 
        my $bgcolor = setbgcolor($is_editing, $line,$line);       
        my $classes="class='odd $bgcolor'";
        if ($num % 2) {
            $classes="class='env $bgcolor'";
        }
        
        printf <<EOF
        <tr $classes>
            <td style="text-align:center">$linenum</td>
            <td style="text-align:center">$tmp[0]</td>
            <td style="text-align:center">$tmp[1]</td>
            <td style="text-align:center">
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="display:inline-block">
                    <input class='imagebutton' type='image' NAME="submit" SRC="$EDIT_PNG" ALT="%s" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="edit">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$num">
                </form>
                <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="display:inline-block" onsubmit="return confirm('确认删除？')">
                    <input class='imagebutton' type='image' NAME="submit" SRC="$DELETE_PNG" ALT="%s" />
                    <INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
                    <INPUT TYPE="hidden" NAME="line" VALUE="$num">
                </form>
            </td>
        </tr>
EOF
;
        $num++;
    }
    if (!$num){
    no_tr(4,_('Current no content'));
}
print "</table>";

if($num != 0){
            printf <<EOF
        
        <table class="list-legend" cellpadding="0" cellspacing="0">
          <tr>
            <td class="boldbase">
              <B>%s:</B>
            <IMG SRC="$ENABLED_PNG" title="%s" />
            %s
            <IMG SRC='$DISABLED_PNG' title="%s" />
            %s
            <IMG SRC="$EDIT_PNG" title="%s" />
            %s
            <IMG SRC="$DELETE_PNG" title="%s" />
            %s</td>
          </tr>
        </table>
EOF
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
;
}
    #显示自动规则
    my $num2=0;
     printf <<END
    <br />  <br />  
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr><td colspan="9" class="boldbase" style="font-size:15px">联动规则</td></tr>
        <tr>
            <td class="boldbase" style="width:5%;">%s</td>
            <td class="boldbase" style="width:15%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>     
            <td class="boldbase" style="width:10%;">%s</td>
            <td class="boldbase" style="width:10%;">%s</td>    
            <td class="boldbase" style="width:10%;">%s</td>
            <td class="boldbase" style="width:10%;">%s</td>
        </tr>
    
END
    , _('序号')
    ,_('IDS设备名称')
    , _('源IP')
    , _('目标IP')
    ,_('目标端口号')
    ,_('协议')
    ,_('策略')
    ,_('剩余时间')
;
    foreach my $line (read_config_file($autoconf)) {
        if ($line) {
        my @tmp = split(/,/,$line);
        my $linenum=$num2 + 1;
        my $enabled_gif = $ON_PNG;
        my $enabled_action = "on";
        if ($tmp[6] eq "off") {
            $enabled_gif = $OFF_PNG;
            $enabled_action = "off";
        }
        if (!$tmp[2]) {
            $tmp[0] = "任意";
        }
        
        if (!$tmp[4]) {
            $tmp[2] = "任意";
        }
        if ($tmp[5] eq "ICMP") {
            $tmp[2] = "无";
            $tmp[4] = "无";
        }
        my $classes="class='odd'";
        if ($num2 % 2) {
            $classes="class='env'";
        }
        my $times  = `date +%s`;
        $times -= $tmp[6];
        $times = 180 - $times;
        # add by squall-----
        # ensure linkage_firewall_checkdaemon is running
        # and do not show negtive value
        if ($times < 0) {
            $times = 0;
            system("/usr/local/bin/linkage_firewall restart_checkdaemon &");
        }
        # end---------------
printf <<EOF
        <tr $classes>
            <td>$linenum</td>
            <td>$tmp[0]</td>
            <td>$tmp[1]</td>
            <td>$tmp[2]</td>
            <td>$tmp[3]</td>
            <td>$tmp[4]</td>
            <td>$policies{$tmp[5]}</td>
            <td>$times s</td>
        </tr>
EOF
;
        $num2++;
        }
    }
if (!$num2){
    no_tr(9,_('Current no content'));
}
print "</table>";
print "</div>";

    #&closebox();
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    my $linenum = $par{'line'};
    my $src_ip = $par{'src_ip'};
    my $src_port = $par{'src_port'};
    my $dst_ip = $par{'dst_ip'};
    my $dst_port = $par{'dst_port'};
    my $prot = $par{'prot'};
    my $policy = $par{'policy'};
    my $enabled = $par{'checked'};
    my $dev_name =  $par{'dev_name'};    
    my $dev_ip =  $par{'dev_ip'};
    if($par{'ACTION_2'} eq 'switch'){
        if($service_status eq "on")
        {
            $h3c_settings_hash{'ENABLED'} = "off"; 
            $log_message = "关闭设备联动";
            &user_log($log_message);
        
        } else {
            $h3c_settings_hash{'ENABLED'} = "on";
            system("/usr/local/bin/linkage_firewall on &");
            if (! -e $snmp_settings) {
                system("echo 'ENABLED=on' >$snmp_settings");
            }
            else{
                readhash($snmp_settings,\%snmp_hash);
                $snmp_hash{'ENABLED'} = "on";
                &writehash($snmp_settings, \%snmp_hash);
            }
            system('sudo /usr/local/bin/restartsnmp.py --force >/dev/null 2>&1');
            $log_message = "开启设备联动";
            &user_log($log_message);

        }
        if( !(-e $h3c_settings) )
        {
            system("touch ${h3c_settings}");
        }
        if ($h3c_settings_hash{'ENABLED'} eq "off") {
            system("/usr/local/bin/linkage_firewall off");            
            system("rm $needreload");
        }
        #关闭设备联动定时调用命令
        &writehash($h3c_settings, \%h3c_settings_hash);
        return;
    }

    #====新增保存动作==by wl 2014.4.10===#
    if ($action eq "save_config") {
        my %to_be_saved_config = ();
        readhash($h3c_settings,\%to_be_saved_config);
        $to_be_saved_config{'LEVEL'} = $par{'auth_level'};
        `echo $par{'auth_level'} >> /tmp/auth_level`;
        writehash($h3c_settings, \%to_be_saved_config);
    }
    #====end=============================#
    if ($action eq "add" || $action eq "modify") {
      if($action eq "add"){
        $log_message = "添加了联动设备$dev_name";
        &user_log($log_message);          
      }
       if($action eq "modify"){
           my $num = $linenum + 1;
           $log_message = "修改了联动设备$dev_name";
           &user_log($log_message);           
      }
        #save_file($linenum,$src_ip,$src_port,$dst_ip,$dst_port,$prot,$policy,$enabled);
        save_dev($linenum,$dev_name,$dev_ip);
    }
    if ($action eq "delete") {
        my $num = $linenum + 1;
        $log_message = "删除了联动设备$dev_name";
        &user_log($log_message);        
       #delete_line($linenum);
       delete_dev($linenum);
    }
    if ($action eq "off") {
        my $num = $linenum + 1;
        $log_message = "启用了第$num条模块联动规则";
        &user_log($log_message);
        toggle_line($linenum,"off");
    }
    if ($action eq "on") {
        my $num = $linenum + 1;
        $log_message = "禁用了第$num条模块联动规则";
        &user_log($log_message);
        toggle_line($linenum,"on");
    }
    if ($action eq 'apply') {
        system ("/usr/local/bin/linkage_firewall manual");
        system ("rm $needreload");
        $notemessage = _("联动规则应用成功 !");        
        $log_message = "应用联动规则";
        &user_log($log_message);
    }
	if($action eq 'switch'){
		print $service_status;
		if($service_status eq "on")
		{
			$h3c_settings_hash{'ENABLED'} = "off"; 
            $log_message = "开启设备联动";
            &user_log($log_message);
		} else {
			$h3c_settings_hash{'ENABLED'} = "on";
			system("/usr/local/bin/linkage_firewall on");
			$log_message = "关闭设备联动";
            &user_log($log_message);
		}
		if( !(-e $h3c_settings) )
		{
			system("touch ${h3c_settings}");
		}
		if ($h3c_settings_hash{'ENABLED'} eq "off") {
			system("/usr/local/bin/linkage_firewall off");
		}
		#关闭设备联动定时调用命令
		&writehash($h3c_settings, \%h3c_settings_hash);
		return;
	}
	
}

&getcgihash(\%par);

&showhttpheaders();


my $extraheader = '<meta http-equiv="refresh" content="300">
<link rel="stylesheet" type="text/css" href="/include/linkage.css"/>
<script type="text/javascript" src="/include/serviceswitch.js"></script><script type="text/javascript" src="/include/linkage.js">';
&openpage(_('设备联动'), 1, $extraheader);
save();
if (-e $needreload) {
    applybox(_("联动规则已修改需要应用使更改生效!"));
}
&openbigbox($errormessage, $warnmessage, $notemessage);
$lineno = $par{'line'};
if ($lineno !~ /\d+/) {
    $lineno = "none";
}
display_switch();
check_form();
&closebigbox();
&closepage();
