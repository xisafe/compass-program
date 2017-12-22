#!/usr/bin/perl

require '/var/efw/header.pl';

my (%settings, %checked);
my $conffile         = "${swroot}/synflood/settings";
my $conffile_default = "${swroot}/synflood/default/settings";

&showhttpheaders();
$errormessage = '';
&getcgihash(\%settings);

&openpage(_('抗DDOS攻击'), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
save();
readconf();
&openbigbox($errormessage, $warnmessage, $notemessage);

display_table();
check_form();
&closebigbox();
&closepage();

sub readconf(){
   if ( -f $conffile_default ) {
        &readhash( "$conffile_default", \%settings );
    }
    if ( -f $conffile ) {
        &readhash( "$conffile", \%settings );
    } 
}
sub display_table(){
    my $help_hash1 = read_json("/home/httpd/help/synflood_help.json","synflood.cgi","最大连接数","-10","30","down");
    my $help_hash2 = read_json("/home/httpd/help/synflood_help.json","synflood.cgi","骤增值","-10","30","down");
    my $help_hash3 = read_json("/home/httpd/help/synflood_help.json","synflood.cgi","添加间隙","-10","30","down");
    my $help_hash4 = read_json("/home/httpd/help/synflood_help.json","synflood.cgi","删除间隙","-10","30","down");

    $service_status = $settings{'ENABLED'};
printf <<END
<script type="text/javascript">
    \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('/cgi-bin/synflood.cgi', SERVICE_STAT_DESCRIPTION);
    });
</script>

<div id="validation-error" class="error-fancy" style="width: 504px; display:none">
        <div class="content">
            <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td class="sign" valign="middle"><img src="/images/bubble_red_sign.png" alt="" border="0" /></td>
                    <td id="validation-error-text" class="text" valign="middle"></td>
                </tr>
            </table>
        </div>
        <div class="bottom"><img src="/images/clear.gif" width="1" height="1" alt="" border="0" /></div>
</div>

<form name="SYNFLOOD_FORM" enctype='multipart/form-data' class="service-switch-form" id="snmp-form" method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type="hidden" class="service-status" name="ENABLED" value="$service_status" />

<table cellpadding="0" cellspacing="0" border="0" >
    <tr>
        <td valign="top">
            <div id="access-policy" class="service-switch">
                <div  ><span class="title">%s</span>
                    <span class="image"><img class="$service_status" align="absbottom" src="/images/switch-%s.png" alt="" border="0"/></span>
                </div>
                                    <br />
                    <div id="access-description" class="description" %s>%s</div>

                    <div id="access-policy-hold" class="spinner working">%s</div>
                    <br />
                    <div id="access-options" class="options-container" %s>
                        <div class="options">
                            <table class="data_table">
                            <tr class="env">
                                <td class="need_help add-div-type" width="35%">%s* $help_hash1</td>
                                <td><input type='text' class="text" name='MAX' value='$settings{'MAX'}' /></td>
                            </tr>
                            <tr class="odd">
                                <td class="need_help add-div-type">%s* $help_hash2</td>
                                <td><input type='text' class="text" name='SPAN' value='$settings{'SPAN'}' /></td>
                            </tr>    
                            <tr class="env">
                                <td class="need_help add-div-type">%s* $help_hash4</td>
                                <td><input type='text' class="text" name='ADDGAP' value="$settings{'ADDGAP'}" /></td>
                            </tr>    
                            <tr class="odd">
                                <td class="need_help add-div-type">%s* $help_hash3</td>
                                <td><input type='text' class="text" name='DELGAP' value='$settings{'DELGAP'}' /></td>
                            </tr>
                            <tr class="table-footer"><td colspan="4"> 
                            <input  class="net_button" type='submit' name='submit' value='%s' onclick="\$('.service-switch-form').unbind('submit');" /></td></tr>
                            </table>
                        </div>
                       
                        </div>
                    </div>
                </div>
        </td>
    </tr>
</table>
    <input type='hidden' name='ACTION' value='save'  />
</form>
END
, escape_quotes(_("抗DDOS攻击服务正在启动，请稍等...")),
escape_quotes(_("抗DDOS攻击服务正在关闭，请稍等...")),
escape_quotes(_("抗DDOS攻击服务正在应用，请稍等...")),
_('启用抗DDOS攻击服务'),
$settings{'ENABLED'} eq 'on' ? 'on' : 'off',
$settings{'ENABLED'} eq 'on' ? 'style="display:none"' : '',
 _("使用上面的开关来启用抗DDOS攻击服务."),
'',
 $settings{'ENABLED'} eq 'off' ? 'style="display:none"' : '',
_('最大连接数'),
_('骤增值'),
_('添加间隙'),
_('删除间隙'),
_('Save'),
;
}
sub save(){
    if ($settings{'ACTION'} eq 'save'){
        delete $settings{'__CGI__'};
        delete $settings{'submit'};
        delete $settings{'perform_switch'};
        if ($errormessage eq '') {
            &writehash($conffile, \%settings);
            system('sudo /usr/local/bin/restartsynflood >/dev/null 2>&1') == 0
                or $errormessage = _('Helper program returned error code')." " . $?/256;
        }
        $notemessage = "已成功保存当前修改";
    }
}
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'SYNFLOOD_FORM',
       'option'   :{
                    'MAX':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var num = eve._getCURElementsByName("MAX","input","SYNFLOOD_FORM")[0].value;
                                                        num = parseInt(num);
                                                        if(num < 1 || num > 1000){
                                                            msg = "最大连接数范围是1-1000";
                                                        }
                                                        return msg;
                               }
                             },
                    'SPAN':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var num = eve._getCURElementsByName("SPAN","input","SYNFLOOD_FORM")[0].value;
                                                        num = parseInt(num);
                                                        if(num < 1 || num > 1000){
                                                            msg = "骤增值范围是1-1000";
                                                        }
                                                        return msg;
                               }
                             },
                    'ADDGAP':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var num = eve._getCURElementsByName("ADDGAP","input","SYNFLOOD_FORM")[0].value;
                                                        num = parseInt(num);
                                                        if(num < 1 || num > 500){
                                                            msg = "添加间隙范围是1-500";
                                                        }
                                                        return msg;
                               }
                             },
                    'DELGAP':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var num = eve._getCURElementsByName("DELGAP","input","SYNFLOOD_FORM")[0].value;
                                                        num = parseInt(num);
                                                        if(num < 1 || num > 500){
                                                            msg = "删除间隙范围是1-500";
                                                        }
                                                        return msg;
                               }
                             },
                 }
         }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("SYNFLOOD_FORM");
    </script>
EOF
;
}