#!/usr/bin/perl
#
############################################
# AUTHOR:张征
#
# DATE:2013年 1月 10日 星期三 9:16:12 CST
#
# TO DO:
############################################
#

require '/var/efw/header.pl';
###各文件路劲以及执行的命令定义
my $rule_file        = "${swroot}/ddosflood/config";
my $linkspolices_file        = "${swroot}/ddosflood/linkspolices";
my $restart = "sudo /usr/local/bin/restartddoslinks &";
my $needreload = "${swroot}/ddosflood/needreload_linkspolices";
###各图标定义
my $EDIT_PNG="/images/edit.png";
my $DELETE_PNG="/images/delete.png";
my $ON_PNG="/images/on.png";
my $OFF_PNG="/images/off.png";
my %par=();
$help_hash1 = read_json("/home/httpd/help/ddosflood.json","ddosflood.cgi","linksFlood连接数","-10","10","down");
&showhttpheaders();
$errormessage = '';
&getcgihash(\%par);
my $global_action = $par{'ACTION'};
&openpage('连接耗尽保护', 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
&save();
&openbigbox($errormessage, $warnmessage, $notemessage);
&check_display();
&closebigbox();
&closepage();


sub display_rule(){
    my @rules = read_conf_file($linkspolices_file);
    my $nums = 0;
    printf <<END
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr>
            <td class="boldbase" style="width:6%;">序号</td>
            <td class="boldbase" style="width:15%;">源IP地址</td>
            <td class="boldbase" style="width:15%;">目标IP地址</td>
            <td class="boldbase" style="width:15%;">时间</td>
            <td class="boldbase" style="width:15%;">目标端口</td>
            <td class="boldbase" style="width:10%;">连接数</td>
            <td class="boldbase" style="width:14%;">活动/动作</td>
        </tr>
    
END
;
    foreach my $line(@rules){
        my @elem = split(/,/,$line);
        my $line_num = $nums + 1;
        my $enabled_gif = $ON_PNG;
        my $enabled_alt = "点击禁用规则";
        if ($elem[0] eq 'off') {
            $enabled_gif = $OFF_PNG;
            $enabled_alt = "点击启用规则";
        }
        if ($elem[1] eq "") {
            $elem[1] = "<任意>";
        }
        if ($elem[3] eq "icmp") {
            $elem[4] = "无";
        }
        elsif(!$elem[4]){
            $elem[4] = "<任意>";
        }
        printf <<EOF
            <tr>
            <td>$line_num</td>
            <td>$elem[1]</td>
            <td>$elem[2]</td>
            <td>$elem[3]</td>
            <td>$elem[4]</td>
            <td>$elem[5]</td>
            <td>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                        <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" title="$enabled_alt" />
                        <input type="hidden" name="ACTION" value="$elem[0]">
                        <input type="hidden" name="line" value="$nums">
                    </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                        <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" title="编辑" />
                        <input type="hidden" name="ACTION" value="edit_rule">
                        <input type="hidden" name="line" value="$nums">
                    </form>
                    <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" onsubmit='return confirm("确认删除？")'>
                        <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" title="删除" />
                        <input type="hidden" name="ACTION" value="rule_delete">
                        <input type="hidden" name="line" value="$nums">
                    </form>
            </td>
            </tr>
EOF
;
        $nums++;
    }
    if (!$nums) {
        no_tr(7,"无内容");
    }
    else{
        &display_legend();
    }
}
sub display_add_rule($$){
    my $is_edit = shift;
    my $line_number = shift;
    my @rules = read_conf_file($linkspolices_file);
    my $enabled,$src_ip,$dst_ip,$protocol,$port,$link_num;
    if ($line_number ne 'none') {
        ($enabled,$src_ip,$dst_ip,$protocol,$port,$link_num) = split(/,/,$rules[$line_number]);
    }
    my $checked = "checked='checked'";
    if ($enabled eq 'off') {
        $checked = "";
    }

    my $action = 'rule_add';
    my $title = _('添加规则');
    my $buttontext=_("Add");
    my $show = "";
    if ($is_edit eq "edit_rule") {
        $title = _('编辑规则');
        $buttontext = _("Edit");
        $show = "showeditor";
    }
    openeditorbox($title, $title, $show, "addqosdevice", @errormessages);
    printf <<END
    </form>
    <form name="RULE_FORM" method='post' action='$self' enctype='multipart/form-data'>
        <table width="100%" cellpadding="0" cellspacing="0"> 
            <tr class='odd'>
                <td class="add-div-type need_help">源IP地址 </td>
                <td><input type="text" value="$src_ip" name="src_ip" /></td>
            </tr> 
            <tr class='env'>
                <td class="add-div-type need_help" >目标IP地址 *</td>
                <td><input type="text" value="$dst_ip" name="dst_ip" /></td>
            </tr>
            <tr class='odd'>
                <td class="add-div-type need_help" >时间(s) *</td>
                <td><input type="text" value="$protocol" name="protocol" /></td>
            </tr>
            <tr class='env'>
            <td class="add-div-type need_help" >目标端口 </td>
                <td><input type="text" value="$port" name="port" /></td>
            </tr>
            <tr class='odd' id="link_num">
                <td class="add-div-type need_help" >新建连接数 *$help_hash1</td>
                <td><input type="text" value="$link_num" name="link_num" /></td>
            </tr>            
            <tr class='env' id="enabled">
            <td class="add-div-type need_help" >启用 </td>
                <td><input name='enabled' type="checkbox" $checked /></td>
            </tr>
        </table>
    <input type="hidden" name="ACTION" value="$action">
    <input type="hidden" name="line" value="$line_number">
END
;
    &closeeditorbox($buttontext, _("Cancel"), "routebutton", "createdevice", "$ENV{SCRIPT_NAME}");
    &check_form();
}


sub save(){
    if($global_action eq 'rule_add') {
        save_file($par{'line'},$par{'src_ip'},$par{'dst_ip'},$par{'protocol'},$par{'port'},$par{'link_num'},$par{'enabled'});
        `touch $needreload`;
        $global_action = "";
        %par = ();
    }
    elsif($global_action eq 'on') {
        &toggle_rule($par{'line'},'off');
        `touch $needreload`;
        $global_action = "";
        %par = ();
        return;
    }
    elsif($global_action eq 'off') {
        &toggle_rule($par{'line'},'on');
        `touch $needreload`;
        $global_action = "";
        %par = ();
        return;
    }
    elsif($global_action eq 'rule_delete') {
        &delete_file($par{'line'});
        `touch $needreload`;
        $global_action = "";
    }
    elsif($global_action eq 'apply') {
        `$restart`;
        `rm $needreload`;
        $global_action = "";
        %par = ();
    }
}
sub check_display(){
    if (-e $needreload) {
        applybox("连接耗尽保护配置已更改需要应用使更改生效!");
    }
    if($global_action eq 'edit_rule') {
        display_add_rule("edit_rule",$par{'line'});
    }    
    elsif(!$global_action) {
        display_add_rule("none","none");
    }
    display_rule();
}
sub save_file(){
    my $line = shift;
    my $src_ip = shift;
    my $dst_ip = shift;
    my $protocol = shift;
    my $port = shift;
    my $link_num = shift;
    my $enabled = shift;
    if (!$enabled) {
        $enabled = 'off';
    }
    if (protocol eq 'icmp') {
        $port = "";
    }
    my $save_line = "$enabled,$src_ip,$dst_ip,$protocol,$port,$link_num";
    my @rules = read_conf_file($linkspolices_file);
    ###添加时直接把行添加到原文件
    if ($line eq "none") {
        push(@rules,$save_line);
    }
    ###修改时将修改后的值保存至原文件
    else{
        for (my $num = 0; $num < @rules; $num++) {
            if ($line == $num) {
                $rules[$num] = $save_line;
            }
        }
    }
    save_config_file(\@rules,$linkspolices_file);
}
sub toggle_rule($$){
    my $line = shift;
    my $enabled = shift;
    my @rules = read_conf_file($linkspolices_file);
    if ($enabled eq 'on') {
        $rules[$line] =~s/^off/on/;
    }
    else{
        $rules[$line] =~s/^on/off/;
    }
    save_config_file(\@rules,$linkspolices_file);
}
sub delete_file($){
    my $line = shift;
    my @rules = read_conf_file($linkspolices_file);
    delete($rules[$line]);
    save_config_file(\@rules,$linkspolices_file);
}
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'RULE_FORM',
       'option'   :{
                    'src_ip':{
                               'type':'text',
                               'required':'0',
                               'check':'ip_mask|ip|',
                             },
                    'dst_ip':{
                               'type':'text',
                               'required':'1',
                               'check':'ip_mask|ip|',
                             },
                    'link_num':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg = ""; 
                                                        var link_num = eve._getCURElementsByName("link_num","input","RULE_FORM")[0].value;
                                                        link_num = parseInt(link_num);
                                                        if (link_num < 1 || link_num > 254){
                                                            msg = "新建连接数必须在1-254之间";
                                                        }
                                                        return msg;
                                                    }
                             },                             
                    'protocol':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg = ""; 
                                                        var link_num = eve._getCURElementsByName("protocol","input","RULE_FORM")[0].value;
                                                        link_num = parseInt(link_num);
                                                        if (link_num < 1 || link_num > 300){
                                                            msg = "时间必须在1-300之间";
                                                        }
                                                        return msg;
                                                    }
                             },
                    'port':{
                               'type':'text',
                               'required':'0',
                               'check':'port|port_range|',
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("RULE_FORM");
    </script>
EOF
;
}
sub display_legend(){
        printf <<EOF 
        <table class="list-legend" cellpadding="0" cellspacing="0">
          <tr>
            <td class="boldbase">
              <B>%s:</B>
            <IMG SRC="$ON_PNG" title="%s" />
            %s
            <IMG SRC='$OFF_PNG' title="%s" />
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
_('Remove')
;
}
