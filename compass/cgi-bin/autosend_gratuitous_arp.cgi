#!/usr/bin/perl
#
#    @author wl
#    @history     2013.09.25 First release
#                2014.03.03 Modified
#

#use strict;

require '/var/efw/header.pl';
my $conffile_dir     = "${swroot}/autoarp";
my $conffile         = "${swroot}/autoarp/settings";
my $flag_start       = "${swroot}/autoarp/start";
my $needreload       = "${swroot}/autoarp/needreload";
my $settings_ethernet ="/var/efw/ethernet/settings";
my $start            = "/usr/local/bin/autosend_gratuitous_arp start";
my $stop             = "/usr/local/bin/autosend_gratuitous_arp stop";
my %par;
my %conf;
my %hash_interface;
my @interface_eth;
my $errormessage    = '';
my $warnmessage        = '';
my $notemessage        = '';
my $CUR_PAGE = "定时发送免费ARP" ;      #当前页面名称，用于记录日志
my $log_oper;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

sub make_file(){
    if(!-e $conffile_dir)
    {
        `mkdir $conffile_dir`;
    }
    if(!-e $conffile)
    {
        `touch $conffile`;
        #将默认配置写入
        `echo >>$conffile ENABLED=off`;
        `echo >>$conffile INTERFACE=`;
        `echo >>$conffile INTERVAL=2500`;
    }
    if(!-e $interfaces)
    {
        `touch $interfaces`;
        #将默认配置写入
        `echo >>$interfaces INTERFACES=br0,br1`;
    }
}

sub readconfile(){
    if(-e $conffile){
       readhash($conffile, \%conf);
    }
    #readhash($settings_ethernet,\%hash_interface);
    @interface_eth = get_eth();
    my $green  = `cat /var/efw/ethernet/br0`;
    my $orange = `cat /var/efw/ethernet/br1`;
    my $blue   = `cat /var/efw/ethernet/br2`;
    my @br0s = split(/\n/,$green);
    my @br1s = split(/\n/,$orange);
    my @br2s = split(/\n/,$blue);
    for (my $i=0;$i<@interface_eth;$i++){
        foreach(@br0s){
            if($_ eq $interface_eth[$i]){
                delete ($interface_eth[$i]);
            }
        }
        foreach(@br1s){
            if($_ eq $interface_eth[$i]){
                delete ($interface_eth[$i]);
            }
        }
        foreach(@br2s){
            if($_ eq $interface_eth[$i]){
                delete ($interface_eth[$i]);
            }
        }
    }
    if(@br2s > 0){
        unshift(@interface_eth,'br2');
    }
    if(@br1s > 0){
        unshift(@interface_eth,'br1');
    }
    if($green){
        unshift(@interface_eth,'br0');
    }
	
	
}

sub display_switch() {
    my $arp_send_enabled = $conf{'ENABLED'};
    printf <<END
    <script type="text/javascript">
        \$(document).ready(function() {
            var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
            var sswitch = new ServiceSwitch('/cgi-bin/autosend_gratuitous_arp.cgi', SERVICE_STAT_DESCRIPTION);    
        });
        function check_switch(){
            var status = \$(".image img").attr("class");
            if(status=='on'){
                \$("#detail").css('display','none');
            }
            if(status=='off'){
               \$("#detail").css('display','block'); 
            }
        }
    </script>
    <form name="ARP_FORM" enctype='multipart/form-data' method='post' class="service-switch-form" id="access-form" action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" class="service-status" name="ARP_ENABLED" value='$arp_send_enabled' />
        <table cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td valign="top">
                <div id="access-policy" class="service-switch">
                    <div  ><span class="title">%s</span>
                    <span class="image"><img class="$arp_send_enabled" align="absbottom" src="/images/switch-%s.png" alt="" border="0" onclick="check_switch();"/></span>
                </div>
                        <div id="access-description" class="description" %s>%s</div>
                        <div id="access-policy-hold" class="spinner working">%s</div>
                        <div class="options-container efw-form" %s>
                            <div class="section first" >
                                要关闭免费ARP发送服务，使用上面的开关关闭它
                            </div>
            
    
END
, escape_quotes(_("免费ARP发送服务正在启动，请等待...")),
escape_quotes(_("免费ARP发送服务正在关闭，请等待...")),
escape_quotes(_("配置已经保存，免费ARP发送服务正在重启. 请稍等...")),
,_('免费ARP发送服务')
,$arp_send_enabled eq 'on'?'on':'off',
,$arp_send_enabled eq "on" ? 'style="display:none"' : '',
, _("要开启免费ARP发送服务，点击上面按钮开启"),
, _("免费ARP发送服务正在被重启，请稍等......"),
,$arp_send_enabled eq "on" ? '' : 'style="display:none"'
;
    printf <<EOF
                    </div>
                </div>
            
            </td>
        </tr>
    </table>
    <input type='hidden' name='ACTION' value='switch'  />
    </form>
EOF
;
    print "</form>\n";
        my $style;
        if($arp_send_enabled eq 'on')
        {
           $style = 'block';
        } else {
           $style= 'none';
        }
        
}

sub display_edit() {
    my $checked;
    if(-e $flag_start){
        $checked = "checked = 'checked'";
    }else{
        $checked = "";
    }
    printf <<EOF
    <script type="text/javascript">
        function change_switch(){
            var enabled = "";
            if(\$("#cbk_enable").is(":checked")){
                enabled = "on";
            }else{
                enabled = "off";
            }
            var sending_data = {
                ACTION: "switch",
                ENABLED: enabled
            };

            function ondatareceived(data) {
                
            }

            do_request(sending_data, ondatareceived);
        }
        function do_request(sending_data, ondatareceived) {
            \$.ajax({
                type: 'POST',
                url: '/cgi-bin/autosend_gratuitous_arp.cgi',
                data: sending_data,
                async: false,
                error: function(request){
                    show_error_mesg("网络错误,部分功能可能出现异常");
                },
                success: ondatareceived
            });
        }
    </script>
    
    <div id='detail' style='width:97%;margin:0px auto 10px;'>
    
        <form name="ARP_FREE_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        
        <table style="width:100%;margin:10px auto 0px;" cellpadding="0" cellspacing="0" style="font-size:12px;">
            <tr style="background-image:url(../images/con-header-bg.jpg);height:25px;">
                <td style="width:15%">
                    <span  style="display:block;margin:3px 10px auto auto;font-weight:bold;margin-left:22px;text-align:left">启用</span>
                </td>
                <td width="80%">
                    <input type='checkbox' $checked value="on"  id="cbk_enable" name="enabled" style="float:left;" onclick="change_switch();"/>
                </td>
            </tr>
        </table>
        
            <div id="submit_value">
EOF
;
    my @interface = split(/,/,$conf{'INTERFACE'});
    foreach my $interface (@interface){
        printf <<EOF
            <input type="hidden" name="interface" value="$interface"/>
EOF
;
    }
    printf <<EOF
            </div>
            <table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed" frame="box">
                <tbody>
                    <tr class="odd">
                        <td class="add-div-type need_help">接口设置</td>
                        <td>
                            <div style="margin:auto;">
                                <div id="left-div" style="float:left;">
                                    <div style="margin:5px auto;">待选接口</div>
                                    <div>
                                        <select id="left_select" name="left_select" multiple="multiple" size="8" style="width:200px;">
EOF
;
    foreach my $cacheinterface (@interface_eth){
        my $exist = 0;
        foreach my $interface (@interface){
            if($cacheinterface eq $interface){
                $exist++;
            }
        }
        if($exist <=> 0){
            $exist = 0;
            next;
        }else{
            if($cacheinterface){
                printf <<EOF
                <option>$cacheinterface</option>
EOF
;
            }
        }
    }
    printf <<EOF
                                        </select>
                                    </div>
                                </div>
                                <div style="float:left;margin: 45px 30px;">
                                    <div style="margin:5px;">
                                        <input id="add" type="button" value=">>" onclick="" class="mvbutton"/>
                                    </div>
                                    <div style="margin:5px;">
                                        <input id="del" type="button" value="<<" onclick="" class="mvbutton"/>
                                    </div>
                                </div>
                                <div id="right-div" style="float:left;">
                                    <div style="margin:5px auto;">定时发送接口</div>
                                    <div><select  id="right_select" name="right_select" multiple="multiple" size="8" style="width:200px;">
EOF
;
    foreach my $interface (@interface){
        printf <<EOF
            <option>$interface</option>
EOF
;
    }
    printf <<EOF
                                    </select></div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr class="env">
                        <td class="add-div-type need_help">发送间隔*</td>
                        <td>
                            <input type="text" id="arp_free_interval" name="arp_free_interval" value="$conf{'INTERVAL'}" style="width:200px;vertical-align:middle;padding:0px;margin:0px;">
                            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">毫秒(200-5000)</label>
                        </td>
                    </tr>       
                </tbody>
            </table>
            <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
                <tr class="add-div-footer">
                    <td width="50%">
                        <input class='net_button' type='submit' id="arp_free_submit" value='保存' style="display:block;float:right;color:black" onclick="\$('.service-switch-form').unbind('submit');"/>
                        <input type="hidden" name="ACTION" value="save"/>
                    </td>
                    <td width="50%">
                        <input class='net_button' type='button'  value='撤销' style="display:block;float:left;color:black" onclick=""/>
                        <span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
                        <input type="hidden" class="form" name="color" value=""  />
                    </td>
                </tr>
            </table>
        </form>
    </div>
EOF
;
}

sub check_form(){
    printf <<EOF
    <script type="text/javascript">
    var object = {
        'form_name':'ARP_FREE_FORM',
        'option'   :{
            'arp_free_interval':{
                'type':'text',
                'required':'1',
                'check':'int|',
                'ass_check':function(eve){
                    var interval = eve._getCURElementsByName("arp_free_interval","input","ARP_FREE_FORM")[0].value;
                    if(interval < 200 || interval > 5000){
                        return "发送间隔应填写200-5000的整数"
                    }
                }
            }
        }
    }
        var check = new ChinArk_forms();
        check._main(object);
        //check._get_form_obj_table("ARP_FREE_FORM");
    </script>
EOF
;
}

sub do_choose(){
    printf <<EOF
<script type="text/javascript">
    \$(document).ready(function(){
        // 添加
        \$("#add").click(function(){
            var fcy = \$("#left-div select option:selected");
            if(fcy.length){
                fcy.each(function(){
                    var hiddenInput = "<input type='hidden' name='interface' value="+\$(this).text()+" />";
                    \$("#submit_value").append(hiddenInput);
                });
                fcy.attr("selected", false).appendTo(\$("#right_select"));
            }
        });
        // 移除
        \$("#del").click(function(){
            var cy = \$("#right-div select option:selected");
            if(cy.length){
                cy.attr("selected", false).appendTo(\$("#left_select"));
                \$("#submit_value").empty();
                cy = \$("#right-div select option");
                cy.each(function(){
                    var hiddenInput = "<input type='hidden' name='interface' value="+\$(this).text()+" />";
                    \$("#submit_value").append(hiddenInput);
                });
            }
        });
    })
</script>
EOF
;
}

sub do_action() {
    if ($par{'ACTION'} eq 'save') {
        $conf{'INTERFACE'} = $par{'interface'};
        chomp($par{'interface'});
        $conf{'INTERFACE'} =~ s/\|/,/g;
        $conf{'INTERVAL'} = $par{'arp_free_interval'};
        if($par{'enabled'} eq 'on'){
            $conf{'ENABLED'} = 'on';
        }else{
            $conf{'ENABLED'} = 'off';
        }
        writehash($conffile,\%conf);
        `touch $needreload`;
        $log_oper = "edit";
        &write_log($CUR_PAGE,$log_oper,0,$rule_or_congfig);
    }
    
    if ($par{'ACTION'} eq 'switch') {
        print $par{'ENABLED'};
        if($par{'ENABLED'} eq 'on'){
            $conf{'ENABLED'} = 'on';
            writehash($conffile,\%conf);
            `$start`;
            `touch $flag_start`;
        } else {
            $conf{'ENABLED'} = 'off';
            writehash($conffile,\%conf);
            `$stop`;
            `rm $flag_start`;
        }
        # if(!$conf{'ENABLED'}){
            # `$stop`;
            # `rm $flag_start`;
        # }
    }
    
    if($par{'ACTION'} eq  'apply')
    {
        if($conf{'ENABLED'} eq 'on'){
            `$start`;
            `touch $flag_start`;
        } else {
            `$stop`;
            `rm $flag_start`;
        }
        `rm $needreload`;
        $log_oper = "apply";
        &write_log($CUR_PAGE,$log_oper,0,$rule_or_congfig);
    }
}

showhttpheaders();
getcgihash(\%par);
make_file();
readconfile();
openpage($name, 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
do_action();
readconfile();
openbigbox($errormessage, $warnmessage, $notemessage);
if (-e $needreload) {
    $warnmessage = "免费ARP发送服务设置已改变，请点击应用按钮以重启免费ARP发送服务！";
    applybox($warnmessage);
}
&display_edit();
do_choose();
check_form();
closebigbox();
closepage();


