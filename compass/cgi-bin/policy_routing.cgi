#!/usr/bin/perl
#===============================================================================
#
# 描述: 策略路由页面
#
# 作者: 周圆 (zhouyuan), 834613209@qq.com
# 公司: Capsheaf
# 历史: 2011.09.02 ZhouYuan 创建
#       2015.05.23 WangLin  修改
#===============================================================================

require 'routing.pl';
require 'ethconfig.pl';
require 'list_panel_opt.pl';
my (%par,%checked,%selected,%ether,%routing);
my @errormessages = ();
my $log_accepts = 'off';
my @nets;
my %routinghash=();
my $routing = \%routinghash;
my $devices, $deviceshash = 0;

my $services_file           = '/var/efw/routing/services';
my $services_custom_file    = '/var/efw/routing/services.custom';
my $app_file = '/var/efw/objects/application/app_system';#应用配置文件路径
my $pr_needreload   = "${swroot}/routing/policy_routing_needreload";
   $routing_config  = "${swroot}/routing/config_policy";

my @tostypes = ("CS0", "CS1", "CS2", "CS3", "CS4", "CS5", "CS6", "CS7", "AF11",
                "AF12", "AF13", "AF21", "AF22", "AF23", "AF31", "AF32", "AF33",
                "AF41", "AF42", "AF43", "EF");
my $applist            = '/usr/local/bin/application_get_tree.py -s';#获取应用数据PYthon文件路径
my $applistObj         = `sudo $applist`;
my %toslist = (
    CS0 => "000000",
    CS1 => "001000",
    CS2 => "010000",
    CS3 => "011000",
    CS4 => "100000",
    CS5 => "101000",
    CS6 => "110000",
    CS7 => "111000",
    AF11 => "001010",
    AF12 => "001100",
    AF13 => "001110",
    AF21 => "010010",
    AF22 => "010100",
    AF23 => "010110",
    AF31 => "011010",
    AF32 => "011100",
    AF33 => "011110",
    AF41 => "100010",
    AF42 => "100100",
    AF43 => "100110",
    EF => "101110"
);

my $extraheader =  '<script language="JavaScript" src="/include/jquery-3.1.0.min.js"></script>
                    <script language="JavaScript" src="/include/firewall_type.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/jstree.min.js"></script>
                    <script language="JavaScript" src="/include/services_selector.js"></script>
                    <script language="JavaScript" src="/include/policy_routing.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/style.min.css" />
                    <link rel="stylesheet" type="text/css" href="/include/add_list_base.css"/>';        
$extraheader .= <<EOF
<script type="text/javascript">

//渲染应用JS树
function appJstree_render(data) {
    if(\$("#for_appJstree-policyRouting")) {
        \$("#for_appJstree-policyRouting").remove();
    }
    var div = document.createElement("div");
    div.setAttribute("id","for_appJstree-policyRouting");
    var \$div = \$(div);
    \$("#list_panel_id_for_Appid_panel .container-main-body").append(\$div);
    \$("#list_panel_id_for_Appid_panel .container-main-body").css("min-height","200px");
    \$("#list_panel_id_for_Appid_panel .container-main-body .rule-list").remove();
    \$('#for_appJstree-policyRouting').jstree({
        "plugins" : [ 
            "checkbox",
            "state", "types", "wholerow" 
        ],
        "core" : {
            "themes" : { "stripes" : true },
            "data" : data
            
        },
        "types": {
            "app" : {
                
                "icon" : "../images/application.png",
            }
        },
        "checkbox" : {
                "keep_selected_style" : false
        },
    
    });
}
\$(document).ready(function(){
    appJstree_render($applistObj);
    
});

</script>
EOF
,
;
&readhash($ethernet_settings, \%ether);

if (-e $routing_default_settings) {
    &readhash($routing_default_settings, \%routing);
}
if (-e $routing_settigns) {
    &readhash($routing_settigns, \%routing);
}

&getcgihash(\%par);
$log_accepts = $routing{'LOG_ACCEPTS'};

&showhttpheaders();
&openpage(_('Policy Routing'), 1, $extraheader);

init_ethconfig();
configure_nets();
($devices, $deviceshash) = list_devices_description(3, 'GREEN|ORANGE|BLUE', 0);
save();

if ($reload) {
    system("touch $pr_needreload");
}

&openbigbox($errormessage, $warnmessage, $notemessage);

if (-e $pr_needreload) {
    applybox(_("Routing rules have been changed and need to be applied in order to make the changes active"));
}

my $is_editing = ($par{'ACTION'} eq 'edit');
display_rules($is_editing, $par{'line'});
check_form();
&closebigbox();
&closepage();

sub have_net($) {
    my $net = shift;

    # AAAAAAARGH! dumb fools
    my %net_config = (
        'GREEN' => [1,1,1,1,1,1,1,1,1,1],
        'ORANGE' => [0,1,0,3,0,5,0,7,0,0],
        'BLUE' => [0,0,0,0,4,5,6,7,0,0]
    );

    if ($net_config{$net}[$ether{'CONFIG_TYPE'}] > 0) {
        return 1;
    }
    return 0;
}

#通过Appid查询得到Appname
sub get_appName($) {
    my $appids = shift;
    if($appids){
        my @appid  = split("&",$appids);
        my @lines;
        my @appname;
        my ( $status,$mesg ) = &read_config_lines( $app_file,\@lines );
        for( my $i=0; $i < @appid; $i++) {
            
            for( my $i2=0; $i2<@lines; $i2++ ) {
                
                my @line_data = split(",",$lines[$i2]); 
                if( $appid[$i] == $line_data[0] ) {
                    push( @appname,$line_data[2] ); 

                }
            }
        }
        return join ",", @appname;  
    }else{
        return "";
    }
   
}
sub configure_nets() {
    my @totest = ('GREEN', 'BLUE', 'ORANGE');

    foreach (@totest) {
        my $thisnet = $_;
        if (! have_net($thisnet)) {
            next;
        }
        if ($ether{$thisnet.'_DEV'}) {
            push (@nets, $thisnet);
        }
    }

}

sub get_openvpn_lease() {
    my @users = sort split(/\n/, `$openvpn_passwd list`);
    return \@users;
}

sub move($$) {
    my $line = shift;
    my $direction = shift;
    my $newline = $line + $direction;
    if ($newline < 0) {
        return;
    }
    my @lines = read_config_file();

    if ($newline >= scalar(@lines)) {
        return;
    }

    my $temp = $lines[$line];
    $lines[$line] = $lines[$newline];
    $lines[$newline] = $temp;
    save_config_file_back(\@lines);
}

sub set_position($$) {
    my $old = shift;
    my $new = shift;
    my @lines = read_config_file();
    my $myline = $lines[$old];
    my @newlines = ();

    # nothing to do
    if ($new == $old) {
        return;
    }
   
    if ($new > $#lines+1) {
        $new = $#lines+1;
    }

    open (FILE, ">$routing_config");

    for ($i=0;$i<=$#lines+1; $i++) {
        if (($i == $new) && (($i==0) || ($i == $#lines) || ($old > $new))) {
            print FILE "$myline\n";
            if (!("$lines[$i]" eq "")) {
                print FILE "$lines[$i]\n";
            }
        }
        elsif (($i == $new)) {
            if (!("$lines[$i]" eq "")) {
                print FILE "$lines[$i]\n";
            }
            print FILE "$myline\n";
        }
        else {
            if ($i != $old) {
                if (!("$lines[$i]" eq "")) {
                    print FILE "$lines[$i]\n";
                }
            }
        }
    }    
    `sudo fmodify $routing_config`;
    close(FILE);
}

sub generate_addressing($$$$) {
    my $addr = shift;
    my $dev = shift;
    my $mac = shift;
    my $rulenr = shift;
    my @addr_values = ();

    foreach my $item (split(/&/, $addr)) {
        if ($item =~ /^OPENVPNUSER:(.*)$/) {
            my $user = $1;
            if ( $user eq "ALL" ) {
                $user = _('ANY');
            }
            push(@addr_values, _("%s (OpenVPN User)", $user));
        }
        else {
            push(@addr_values, $item);
        }
    }
    foreach my $item (split(/&/, $dev)) {
        if ($item =~ /^PHYSDEV:(.*)$/) {
            my $device = $1;
            my $data = $deviceshash->{$device};

          push(@addr_values, "<font color='". $zonecolors{$data->{'zone'}} ."'>".$data->{'portlabel'}."</font>");
        }
        elsif ($item =~ /^VPN:(.*)$/) {
            my $dev = $1;
            push(@addr_values, "<font color='". $colourvpn ."'>".$dev."</font>");
        }
        elsif ($item =~ /^UPLINK:(.*)$/) {
            #my $ul = $1;
            my %ul = get_uplink_info($1);
            push(@addr_values, "<font color='". $zonecolors{'RED'} ."'>".$ul{'NAME'}."</font>");
        }
        else {
            push(@addr_values, "<font color='". $zonecolors{$item} ."'>".$strings_zone{$item}."</font>");
        }
    }
    foreach my $item (split(/&/, $mac)) {
        push(@addr_values, $item);
    }

    if ($#addr_values == -1) {
        return 'ANY';
    }

    if ($#addr_values == 0) {
        return $addr_values[0];
    }

    my $long = '';
    foreach my $addr_value (@addr_values) {
        $long .= sprintf <<EOF
        <div>$addr_value</div>
EOF
        ;
    }
    return $long;
}

sub generate_service($$$) {
    my $ports = shift;
    my $protocol = shift;
    my $rulenr = shift;
    $protocol = lc($protocol);
    $ports =~ s/&&/,/g;
    my $display_protocol = $protocol;
    my @service_values = ();

    if ($protocol eq 'tcp&udp') {
        $display_protocol = 'TCP+UDP';
    }
    else {
        $display_protocol = uc($protocol);
    }

    if ( ($display_protocol eq '') && ($ports eq '') ) {
        return 'ANY';
    }

    if ( ($display_protocol ne '') && ($ports eq '') ) {
        return "$display_protocol<br />"._('ANY');
    }

    if ( ($display_protocol eq '') && ($ports ne '') ) {
        return _('ANY')."<br />$ports";
    }

    return "$display_protocol<br />$ports";
}

sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;
     printf<<EOF
    <div id="Appid_panel" class="container"></div>
EOF
;
    display_add($is_editing, $line);
    
    printf <<END
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr>
            <td class="boldbase" width="3%">#</td>
            <td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="15%">%s</td>
            <td class="boldbase" width="12%">%s</td>
            <td class="boldbase" width="10%">%s</td>
            <td class="boldbase" width="10%">%s</td>
    <!--    <td class="boldbase" width="10%">应用</td>    -->
            <td class="boldbase" width="10%">%s</td>
            <td class="boldbase" width="15%">%s</td>
        </tr>
END
    , _('Source')
    , _('Destination')
    , _('ToS/DSCP值')
    ,_('Via Gateway')
    , _('Service')
    , _('Remark')
    , _('Actions')
    ;

    my @lines = read_config_file();
    my $length = @lines;
    my $i = 0;
    if ( $length > 0 ) {
        foreach my $thisline (@lines) {
            chomp($thisline);
            my %splitted = config_line($thisline);
            if ( ! $splitted{'valid'} ) {
                next;
            }
            my $protocol = uc($splitted{'protocol'});
            my $source = $splitted{'source'};
            my $num = $i+1;

            my $enabled_gif = $DISABLED_PNG;
            my $enabled_alt = _('Disabled (click to enable)');
            my $enabled_action = 'enable';
            if ($splitted{'enabled'} eq 'on') {
                $enabled_gif = $ENABLED_PNG;
                $enabled_alt = _('Enabled (click to disable)');
                $enabled_action = 'disable';
            }
            my $destination = $splitted{'destination'};
            my $src_dev = $splitted{'src_dev'};
            my $tos = $splitted{'tos'};
            my $gateway = '';
            my $backup_allow = $splitted{'backup_allow'};
            if ($splitted{'gw'} =~ /^UPLINK:(.*)$/) {
                $gateway = generate_addressing('', $splitted{'gw'}, '', $i);
            }
            else {
                $gateway = $splitted{'gw'};
            }
            my $port = $splitted{'port'};
            my $remark = value_or_nbsp($splitted{'remark'});
            my $log = '';
            if ($splitted{'log'} eq 'on') {
                $log = _('yes');
            }
            my $mac = $splitted{'mac'};
            my $bgcolor = setbgcolor($is_editing, $line, $i);
            my $src_long_value = generate_addressing($source, $src_dev, $mac, $i);
            if ($src_long_value =~ /(?:^|&)ANY/) {
                $src_long_value = "&lt;"._('ANY')."&gt;";
            }
            my $dest_long_value = generate_addressing($destination, '', '', $i);
            if ($dest_long_value =~ /(?:^|&)ANY/) {
                $dest_long_value = "&lt;"._('ANY')."&gt;";
            }
            my $service_long_value = generate_service($port, $protocol, $i);
            if ($service_long_value =~ /(?:^|&)ANY/) {
                $service_long_value = "&lt;"._('ANY')."&gt;";
            }

            my $appids   = $splitted{'appids'};
            
            $appids =~ s/:/&/g;
            my $appNames = &get_appName($appids);

            if (!$tos) {
                $tos = "&lt;"._('ANY')."&gt;";
            }
            if ( $i eq 0 ) {
                $style{'up'} = "style='visibility:hidden'";
            }
            else {
                $style{'up'} = "";
            }
            if ( $i eq (@lines - 1) ) {
                $style{'down'} = "style='visibility:hidden'";
            }
            else {
                $style{'down'} = "";
            }
            printf <<EOF
            <tr class="$bgcolor">
                <td valign="top" align="center">$num</td>
                <td valign="top">$src_long_value</td>
                <td valign="top">$dest_long_value</td>
                <td valign="top">$tos</td>
                <td valign="top">$gateway</td>
                <td valign="top">$service_long_value</td>
        <!--    <td valign="top">$appNames</td> -->
                <td valign="top">$remark</td>
                <td >
                    <form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                        <input class='imagebutton' $style{'up'}  type='image' name="submit" SRC="$UP_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="up">
                        <input TYPE="hidden" name="line" value="$i">
                    </form>
                    <form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                        <input class='imagebutton ' $style{'down'}  type='image' name="submit" SRC="$DOWN_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="down">
                        <input TYPE="hidden" name="line" value="$i">
                    </form>
                    <form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
                        <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" ALT="$enabled_alt" />
                        <input TYPE="hidden" name="ACTION" value="$enabled_action">
                        <input TYPE="hidden" name="line" value="$i">
                    </form>

                    <form method="post" action="$ENV{'SCRIPT_NAME'}">
                        <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="edit">
                        <input TYPE="hidden" name="line" value="$i">
                    </form>

                    <form method="post" action="$ENV{'SCRIPT_NAME'}">
                        <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s" />
                        <input TYPE="hidden" name="ACTION" value="delete">
                        <input TYPE="hidden" name="line" value="$i">
                    </form>
                </td>
            </tr>
EOF
            ,
            _("Up"),
            _("Down"),
            _('Edit'),
            _('Delete');

            $i++;
        }
    } else {
        no_tr(9,_('Current no content'));
    }
    
    print "</table>";
    if( $length > 0 )
    {
        printf <<EOF
        <table class="list-legend"  cellpadding="0" cellspacing="0" >
            <tr>
                <td ><B>%s</B><IMG SRC="$ENABLED_PNG" ALT="%s" />%s<IMG SRC='$DISABLED_PNG' ALT="%s" />%s<IMG SRC="$EDIT_PNG" alt="%s" />%s<IMG SRC="$DELETE_PNG" ALT="%s" />%s</td>
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
}

sub create_servicelist($$) {
    my $selected_protocol = lc(shift);
    my $selected_ports = shift;
    chomp($selected_protocol);
    chomp($selected_ports);
    
    my $selected = '';
    my $selected_cus = '';
    my @ret = ();
    if ($selected_protocol || $selected_ports) {
        $selected_cus = 'selected';
    }
    my $userdef = sprintf <<EOF
    <option value="" $selected_cus>%s</option>
EOF
    , _('User defined')
    ;
    push(@ret, $userdef);

    my @services = ();
    open(SERVICE_FILE, $services_file) || return ($selected, \@ret);
    @services = <SERVICE_FILE>;
    close(SERVICE_FILE);

    if (open(SERVICE_FILE, $services_custom_file)) {
        foreach my $line (<SERVICE_FILE>) {
            push(@services, $line);
        }
        close(SERVICE_FILE);
    }
    foreach my $line (sort(@services)) {
        my ($desc, $ports, $proto) = split(/,/, $line);
        chomp($desc);
        chomp($ports);
        chomp($proto);
        my $choosen='';
        $proto = lc($proto);
        if (($proto eq $selected_protocol) && ($ports eq $selected_ports)) {
            $choosen='selected';
            $selected="$ports/$proto";
        }
        push (@ret, "<option value='$ports/$proto' $choosen>$desc</option>");
    }
    return ($selected, \@ret);
}

sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;
    my %config;
    my %checked;
    my %selected;
        
    if (($is_editing) && ($par{'sure'} ne 'y')) {
        %config = config_line(read_config_line($line));
    }
    else {
        %config = %par;
        $config{'enabled'} = "on";
    }
    
    my $enabled = $config{'enabled'};
    my $protocol = $config{'protocol'};
    if (! $protocol && !$is_editing) {
        $protocol = 'any';
    }
    my $src_dev = $config{'src_dev'};
    my $source = $config{'source'};
    my $source_ip = '';
    my $source_user = '';
    my $destination = $config{'destination'};
    my $destination_ip = '';
    my $destination_user = '';
    my $gateway = $config{'gw'};
    my $uplink = '';
    my $backup_allow = $config{'backup_allow'};
    my $tos = $config{'tos'};
    my $port = $config{'port'};
    my $remark = $config{'remark'};

    my $mac = $config{'mac'};
    my $log = $config{'log'};
    my $src_type = 'ip';
    my $dst_type = 'ip';
    my $appids   = $config{'appids'};
    my $reglar_appids =  $appids;
        $reglar_appids =~ s/:/&/g;
    my $appNames = &get_appName($reglar_appids);
    $checked{'ENABLED'}{$enabled} = 'checked';
    $checked{'BACKUP_ALLOW'}{$backup_allow} = 'checked';
    $checked{'LOG'}{$log} = 'checked';
    $selected{'PROTOCOL'}{$protocol} = 'selected';
    
    if ($source =~ /^$/) {
        foreach my $item (split(/&/, $src_dev)) {
            $selected{'src_dev'}{$item} = 'selected';
        }
        if ($src_dev !~ /^$/) {
            $src_type = 'dev';
        }
    }

    if ($source !~ /^$/) {
        if ($source =~ /^OPENVPNUSER:/) {
            $source_user = $source;
            foreach $item (split(/&/, $source_user)) {
                $selected{'src_user'}{$item} = 'selected';
            }
            $src_type = 'user';
        }
        else {
            $source_ip = $source;
            if ($source_ip !~ /^$/) {
                $src_type = 'ip';
            }
        }
    }
    if ($destination !~ /^$/) {
        if ($destination =~ /^OPENVPNUSER:/) {
            $destination_user = $destination;
            foreach $item (split(/&/, $destination_user)) {
                $selected{'dst_user'}{$item} = 'selected';
            }
            $dst_type = 'user';
        }
        else {
            $destination_ip = $destination;
            if ($destination_ip !~ /^$/) {
                $dst_type = 'ip';
            }
        }
    }
    if ($mac !~ /^$/) {
        $src_type = 'mac';
    }
    if ($is_editing) {
        if (($source =~ /^$/) && ($src_dev =~ /^$/) &&! ($mac !~ /^$/)) {
            $src_type = 'any';
        }
        if ($destination =~ /^$/) {
            $dst_type = 'any';
        }
    }

    $selected{'src_type'}{$src_type} = 'selected';
    $selected{'dst_type'}{$dst_type} = 'selected';
    
    my $via_type = 'gw';
    if ($gateway =~ /^UPLINK:/) {
        $via_type = 'uplink';
        $uplink = $gateway;
        $gateway = '';
    }
    $selected{'uplink'}{$uplink} = 'selected';
    $selected{'via_type'}{$via_type} = 'selected';

    my %foil = ();
    $foil{'title'}{'src_any'} = 'none';
    $foil{'title'}{'src_dev'} = 'none';
    $foil{'title'}{'src_user'} = 'none';
    $foil{'title'}{'src_ip'} = 'none';
    $foil{'title'}{'src_mac'} = 'none';
    $foil{'value'}{'src_any'} = 'none';
    $foil{'value'}{'src_dev'} = 'none';
    $foil{'value'}{'src_user'} = 'none';
    $foil{'value'}{'src_ip'} = 'none';
    $foil{'value'}{'src_mac'} = 'none';

    $foil{'title'}{'dst_any'} = 'none';
    $foil{'title'}{'dst_user'} = 'none';
    $foil{'title'}{'dst_ip'} = 'none';
    $foil{'value'}{'dst_any'} = 'none';
    $foil{'value'}{'dst_user'} = 'none';
    $foil{'value'}{'dst_ip'} = 'none';

    $foil{'title'}{"src_$src_type"} = 'block';
    $foil{'value'}{"src_$src_type"} = 'block';
    $foil{'title'}{"dst_$dst_type"} = 'block';
    $foil{'value'}{"dst_$dst_type"} = 'block';
    
    $foil{'value'}{'via_gw'} = 'none';
    $foil{'value'}{'via_uplink'} = 'inline';
    $foil{'value'}{"via_$via_type"} = 'inline;float:left';

    $source_ip =~ s/&/\n/gm;
    $destination_ip =~ s/&/\n/gm;
    $mac =~ s/&/\n/gm;
    $port =~ s/&&/\n/gm;

    my $line_count = line_count();

    my $openvpn_ref = get_openvpn_lease();
    my @openvpnusers = @$openvpn_ref;

    my $src_user_size = int($#openvpnusers / 5);
    if ($src_user_size < 5) {
       $src_user_size = 5;
    }
    my $dst_user_size = $src_user_size;
    my $src_dev_size = int((length(%$deviceshash) + $#nets) / 3);
    if ($src_dev_size < 3) {
       $src_dev_size = 3;
    }
    my $action = 'add';
    my $sure = '';
    my $addoredit = "添加路由规则";
    $button = _("Create Rule");
    my $title = _('Policy routing rule editor');
    
    if ($is_editing) {
        $action = 'edit';
        my $sure = '<input TYPE="hidden" name="sure" value="y">';
        $button = _("更新规则");
        $show = "showeditor";
        $addoredit = "更新路由规则";
    }
    elsif(@errormessages > 0) {
        $show = "showeditor";
    }
    else{
        $show = "";
    }
    openeditorbox($addoredit, $title, $show, "createrule", @errormessages);
    printf <<EOF
    </form>
     <form name="ROUTING_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <!-- begin source -->
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr class="env">
                            <td class="add-div-type" rowspan="1">%s</td>
                                <td>%s   <select name="src_type" onchange="toggleTypes('src');" onkeyup="toggleTypes('src');">
                                    <option value="any" $selected{'src_type'}{'any'}>&lt;%s&gt;</option>
                                    <option value="dev" $selected{'src_type'}{'dev'}>%s</option>
                                    <option value="user" $selected{'src_type'}{'user'}>%s</option>
                                    <option value="ip" $selected{'src_type'}{'ip'}>%s</option>
                                    <option value="mac" $selected{'src_type'}{'mac'}>%s</option>
                                </select>
                            </td>
                            <td colspan="2">
                                <div id="src_any_t" style="display:$foil{'title'}{'src_any'}">%s</div>
                                <div id="src_dev_t" style="display:$foil{'title'}{'src_dev'}">%s</div>
                                <div id="src_user_t" style="display:$foil{'title'}{'src_user'}">%s</div>
                                <div id="src_ip_t" style="display:$foil{'title'}{'src_ip'}">%s</div>
                                <div id="src_mac_t" style="display:$foil{'title'}{'src_mac'}">%s</div>
                                <div id="src_any_v" style="display:$foil{'value'}{'src_any'}" style="width: 250px; height: 90px;">&nbsp;</div>
EOF
    , _('Source')
    , _('Type')
    , _('ANY')
    , _('Zone/Interface')
    , _('OpenVPN User')
    , _('Network/IP')
    , _('MAC')
    , _('This rule will match any source')
    , _('Select interfaces (hold CTRL for multiselect)')
    , _('Select OpenVPN users (hold CTRL for multiselect)')
    , _('Insert network/IPs (one per line)')
    , _('Insert MAC addresses (one per line)')
    ;

##########
# SOURCE #
##########

#### Device begin ###########################################################
    printf <<EOF
                            <div id='src_dev_v' style='display:$foil{'value'}{'src_dev'}'>
                                <select name="src_dev" multiple style="width: 250px; height: 90px;">
                                    <option value="LOCAL" $selected{'src_dev'}{"LOCAL"}>%s</option>
EOF
, _('LOCAL')
;
    foreach my $item (@nets) {
        printf <<EOF
                                    <option value="$item" $selected{'src_dev'}{$item}>%s</option>
EOF
        ,$strings_zone{$item}
        ;
    }
    foreach my $data (@$devices) {
        my $value = $data->{'portlabel'};
    my $key = "PHYSDEV:".$data->{'device'};
    my $zone = _("Zone: %s", $strings_zone{$data->{'zone'}});
    printf <<EOF
              <option value="$key" $selected{'src_dev'}{$key}>$value ($zone)</option>
EOF
;
    }
    printf <<EOF
                                    <option value="VPN:IPSEC" $selected{'src_dev'}{'VPN:IPSEC'}>IPSEC</option>
                                </select>
                            </div>
EOF
    ;
#### Device end #############################################################


#### User begin #############################################################
    printf <<EOF
                            <div id='src_user_v' style='display:$foil{'value'}{'src_user'}'>
                                <select name="src_user" multiple style="width: 250px; height: 90px;">
                                    <option value="OPENVPNUSER:ALL" $selected{'src_user'}{"OPENVPNUSER:ALL"}>&lt;%s&gt;</option>
EOF
    , _('ANY')
    ;
    foreach my $item (@openvpnusers) {
        printf <<EOF
                                    <option value="OPENVPNUSER:$item" $selected{'src_user'}{"OPENVPNUSER:$item"}>$item</option>
EOF
    ;
    }
    printf <<EOF
                                </select>
                            </div>
EOF
;
#### User end ###############################################################

#### IP begin ###############################################################
    printf <<EOF
                            <div id='src_ip_v' style='display:$foil{'value'}{'src_ip'}'>
                                <textarea name='source' wrap='off' style="width: 250px; height: 90px;">$source_ip</textarea>
                            </div>
EOF
    ;
#### IP end #################################################################

#### MAC begin ##############################################################
    printf <<EOF
                            <div id='src_mac_v' style='display:$foil{'value'}{'src_mac'}'>
                                <textarea name='mac' wrap='off' style="width: 250px; height: 90px;">$mac</textarea>
                            </div>
EOF
    ;
#### MAC end ################################################################

    printf <<EOF
                        </td>
                    </tr>
                <!-- end source field -->
           
                    <tr class="odd">
                        <td  class="add-div-type" rowspan="1">%s</td>
                        <td>%s  <select name="dst_type" onchange="toggleTypes('dst');" onkeyup="toggleTypes('dst');">
                                <option value="any" $selected{'dst_type'}{'any'}>&lt;%s&gt;</option>
                                <option value="user" $selected{'dst_type'}{'user'}>%s</option>
                                <option value="ip" $selected{'dst_type'}{'ip'}>%s</option>
                            </select>
                        </td>
                        <td colspan="2">
                            <div id="dst_any_t" style="display:$foil{'title'}{'dst_any'}">%s</div>
                            <div id="dst_user_t" style="display:$foil{'title'}{'dst_user'}">%s</div>
                            <div id="dst_ip_t" style="display:$foil{'title'}{'dst_ip'}">%s</div>
                            <div id="dst_any_v" style="display:$foil{'value'}{'src_any'}" style="width: 250px; height: 90px;">&nbsp;</div>
EOF
    , _('Destination')
    , _('Type')
    , _('ANY')
    , _('OpenVPN User')
    , _('Network/IP')
    , _('This rule will match any destination')
    , _('Select OpenVPN users (hold CTRL for multiselect)')
    , _('Insert network/IPs (one per line)')
;

###############
# DESTINATION #
###############

#### User begin #############################################################
    printf <<EOF
                            <div id='dst_user_v' style='display:$foil{'title'}{'dst_user'}'>
                                <select name="dst_user" multiple style="width: 250px; height: 90px;">
                                    <option value="OPENVPNUSER:ALL" $selected{'src_user'}{'OPENVPNUSER:ALL'}>&lt;%s&gt;</option>
EOF
    , _('ANY')
    ;
    foreach my $item (@openvpnusers) {
        printf <<EOF
                                    <option value="OPENVPNUSER:$item" $selected{'dst_user'}{"OPENVPNUSER:$item"}>$item</option>
EOF
        ;
    }
    printf <<EOF
                                </select>
                            </div>
EOF
    ;
#### User end ###############################################################

#### IP begin ###############################################################
    printf <<EOF
                            <div id='dst_ip_v' style='display:$foil{'title'}{'dst_ip'}'>
                                <textarea name='destination' wrap='off' style="width: 250px; height: 90px;">$destination_ip</textarea>
                            </div>
EOF
    ;
#### IP end #################################################################

    printf <<EOF
                        </td>
                    </tr>

                <!-- end destination -->
           
        <tr class="env">
           <td class="add-div-type" rowspan="1"><b>%s</b></td>

            <td>%s * 
<select name="service_port" onchange="selectService('protocol', 'service_port', 'port');" onkeyup="selectService('protocol', 'service_port', 'port');">
                    <option value="any/any">&lt;%s&gt;</option>

EOF
    , _('Service/Port')
    , _('Service')
    , _('ANY')
    ;
    my ($sel, $arr) = create_servicelist($protocol, $config{'port'});
    print @$arr;

# check if ports should be enabled
    if ($protocol eq "") {
        $portsdisabled = 'disabled="true"';
    }
    printf <<EOF
                </select>
            </td>
            <td valign="center">%s *
                <select name="protocol" onchange="updateService('protocol', 'service_port', 'port');" onkeyup="updateService('protocol', 'service_port', 'port');">
                    <option value="any" $selected{'PROTOCOL'}{'any'}>&lt;%s&gt;</option>
                    <option value="tcp" $selected{'PROTOCOL'}{'tcp'}>TCP</option>
                    <option value="udp" $selected{'PROTOCOL'}{'udp'}>UDP</option>
                    <option value="tcp&udp" $selected{'PROTOCOL'}{'tcp&udp'}>TCP + UDP</option>
                    <option value="esp" $selected{'PROTOCOL'}{'esp'}>ESP</option>
                    <option value="gre" $selected{'PROTOCOL'}{'gre'}>GRE</option>
                    <option value="icmp" $selected{'PROTOCOL'}{'icmp'}>ICMP</option>
                </select>
            </td>
                           <td colspan="2">
EOF
        , _('Protocol')
        , _('ANY')
;
my $isdisplay = "class='hidden_class'";
if($port ne "")
{
    $isdisplay = "";
}
printf <<EOF
                <ul  id="port_ul" $isdisplay><li>%s</li>
               <li> <textarea name="port" rows="3" $portsdisabled onkeyup="updateService('protocol', 'service_port', 'port');">$port</textarea></li>
               </ul>
         
EOF
    , _('Destination port (one per line)')
;

printf <<EOF
                <ul id="port_ul2" $note_display><li>%s</li></ul>
EOF
,_('This rule will match all the destination ports')
;
$foil{'value'}{'via_gw'} = 'none';#强关闭 wl 2013.11.22
$selected{'via_type'}{'uplink'} = 'selected';#强制选中 wl 2013.11.22
printf <<EOF

           </td>
        </tr>

<!--
     <tr class="odd">
        <td class="add-div-type" rowspan="1"><b>应用</b></td>
        <td>
            <input type="text" id="Appname" value="$appNames">
            <input type="hidden" id="AppnameList" name="AppnameList" value="$appids">
            <input type="button" value="配置" onclick="load_app();" >
        </td>
        <td colspan="2"></td>
     </tr>
-->
        <tr class="odd">
            <td class="add-div-type" rowspan="1"><b>%s</b></td>
            <td >                
                <div id='via_uplink_v' style='display:block'>
                    <select name="uplink" style="width: 139px;">
EOF
    , _('Route via')
    , _("Uplink")
    ;
    foreach my $name (@{get_uplinks()}) {
        my $key = "UPLINK:$name";
        my %uplinkinfo = get_uplink_info($name);
        printf <<EOF
                          <option value='$key' $selected{'uplink'}{$key}>$uplinkinfo{'NAME'}</option>
EOF
        ;
    }

    printf <<EOF
                    </select>
                <!--</div>-->
            </td>
            <td colspan="2">
                <!--<div id='via_uplink_t' style='display:$foil{'value'}{'via_uplink'}'>-->
                    <input name="backup_allow" value="on" $checked{'BACKUP_ALLOW'}{'on'} type="checkbox">&nbsp;%s
                <!--</div>
                <div id='via_gw_t' style='display:$foil{'value'}{'via_gw'}'></div>-->
            </td>
        </tr>
  
        <tr class="env">
            <td class="add-div-type" rowspan="2">%s</td>
            <td>
                <select name="tos" style="width: 139px;">
                    <option value=''>%s</option>
EOF
    , _('如果此条上行链路失效，则使用备份上行链路')
    , _('TOS/DSCP值')
    , _('任意')
    ;
    foreach my $key (@tostypes) {
        my $selected = "";
        if ($toslist{$key} eq $tos) {
            $selected = 'selected';
        }
        printf <<EOF
                    <option value='$toslist{$key}' $selected>$key - $toslist{$key}</option>
EOF
        ;
    }

    printf <<EOF
                </select>
            </td>
            <td align="top">%s
                <input name="remark" value="$remark" size="50" maxlength="50" type="text">
            </td>
            <td align="left">%s&nbsp;
                <select name="position">
                    <option value="0">%s</option>
EOF
    , _('Remark')
    , _('Position')
    , _('First')
    ;

    my $i = 1;
    while ($i <= $line_count) {
        my $title = _('After rule #%s', $i);
        my $selected = '';
        if ($i == $line_count) {
            $title = _('Last');
        }
        if ($line == $i || ($line eq "" && $i == $line_count)) {
            $selected = 'selected';
        }
        printf <<EOF
                    <option value="$i" $selected>$title</option>
EOF
        ;
        $i++;
    }

    printf <<EOF
                </select>
            </td>
        </tr>
        <tr class="env">
            <td><input name="enabled" value="on" $checked{'ENABLED'}{'on'} type="checkbox">%s</td>
            <td colspan="2"><input name="log" value="on" $checked{'LOG'}{'on'} type="checkbox">%s</td>
        </tr>
    </table>
    <input type="hidden" name="ACTION" value="$action">
    <input type="hidden" name="line" value="$line">
    <input type="hidden" name="sure" value="y">
EOF
    , _('Enabled')
    , _('记录允许的包')
    ;

    #&closebox();
    &closeeditorbox($button, _("Cancel"), "routebutton", "createrule", "$ENV{SCRIPT_NAME}");

    # end of ruleedit div
    #print "</div>"

}

sub reset_values() {
    %par = ();
    $par{'LOG_ACCEPTS'} = $log_accepts;
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    if ($action eq 'apply') {
        system($setrouting);
        system($setpolicyrouting);                
        `sudo fcmd $setrouting`;    
        `sudo fcmd $setpolicyrouting`;
        #2013.12.24 重新定义的应用文件，以与静态路由分开。 by wl
        `rm $pr_needreload`;
        $notemessage = _("Routing rules applied successfully");
        return;
    }
    if ($action eq 'save') {
        reset_values();
        return;
    }
    if ($action eq 'up') {
        move($par{'line'}, -1);
        reset_values();
        return;
    }
    if ($action eq 'down') {
        move($par{'line'}, 1);
        reset_values();
        return;
    }
    if ($action eq 'delete') {
        delete_line($par{'line'});
        reset_values();
        return;
    }

    if ($action eq 'enable') {
        if (toggle_enable($par{'line'}, 1)) {
            reset_values();
            return;
        }
    }
    if ($action eq 'disable') {
        if (toggle_enable($par{'line'}, 0)) {
            reset_values();
            return;
        }
    }

 
    # ELSE
    if (($action eq 'add') ||
            (($action eq 'edit')&&($sure eq 'y'))) {

        my $src_type = $par{'src_type'};
        my $dst_type = $par{'dst_type'};

        my $source = '';
        my $mac = '';
        my $destination = '';
        my $src_dev = '';
        my $old_pos = $par{'line'};
	       my $metric = '';
        if ($src_type eq 'ip') {
            $source = $par{'source'};
        }
        if ($dst_type eq 'ip') {
            $destination = $par{'destination'};
        }
        if ($src_type eq 'user') {
            $source = $par{'src_user'};
        }
        if ($dst_type eq 'user') {
            $destination = $par{'dst_user'};
        }
        if ($src_type eq 'dev') {
            $src_dev = $par{'src_dev'};
        }
        if ($src_type eq 'mac') {
            $mac = $par{'mac'};
        }

        my $gateway = $par{'uplink'};
        my $enabled = $par{'enabled'};
        my $appids = $par{'AppnameList'};
        # print $appids;
        if (save_line($par{'line'},
                      $enabled,
                      $source,
                      $destination,
                      $gateway,
                      $par{'remark'},
                      $par{'tos'},
                      $par{'protocol'},
                      $par{'port'},
                      $mac,
                      $par{'log'},
                      $src_dev,
                      $par{'backup_allow'},
		              $metric,
                      $appids,
                      $par{'service_port'})) {

            if ($par{'line'} ne $par{'position'}) {
                $reload = 1;
                if ("$old_pos" eq "") {
                    $old_pos = line_count()-1;
                }
                if (line_count() > 1) {
                    set_position($old_pos, $par{'position'});
                }
            }
            reset_values();
        }
    }
}

sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'ROUTING_FORM',
       'option'   :{
            'remark':{
                'type':'text',
                'required':'0',
                'check':'note|'
            },
            'src_dev':{
                'type':'select-multiple',
                'required':'0'
            },
            'src_user':{
                'type':'select-multiple',
                'required':'0'
            },
            'dst_user':{
                'type':'select-multiple',
                'required':'0'
            },
            'source':{
                'type':'textarea',
                'required':'0',
                'check':'ip|ip_mask|'
            },
            'mac':{
                'type':'textarea',
                'required':'0',
                'check':'mac|'
            },
            'destination':{
                'type':'textarea',
                'required':'0',
                'check':'ip|ip_mask|'
            },
            'port':{
                'type':'textarea',
                'required':'0',
                'check':'port|port_range|'
            },

            'gw':{
                'type':'text',
                'required':'1',
                'check':'ip|'
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("ROUTING_FORM");
    </script>
EOF
    ;
}
