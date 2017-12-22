#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 接口配置页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: Capsheaf
# HISTORY: 2011.10.26  ZhouYuan Created
#          2015.01.28  WangLin Modified
#          2015.05.13  WangLin Modified
#===============================================================================


require '/var/efw/header.pl';
require 'qos_ethernet.pl';
my $qosdevice="/var/efw/shaping/devices";
my $qosclass="/var/efw/shaping/classes";
my $qosconfig="/var/efw/shaping/config";
my $ethernets="/var/efw/ethernet";
my $extraheader="";
my @errormessages=();
my $needreload = "${swroot}/shaping/needreload";
my $show="";
$EDIT_PNG="/images/edit.png";
$DELETE_PNG="/images/delete.png";
$reload=0;
my $is_editing = 0;
my $action;
my $sure = "";
my %par;
my $temp = &ethname();
my %ethname = %$temp;


sub read_config_line($$) {
    my $devicename = shift;
    my $file = shift;
    my @lines = read_config_file($file);
    foreach $thisline (@lines)
    {
        chomp( $thisline );
        if ( $thisline =~ /$devicename/ )
        {
               return $thisline; 
        }
    }    
}
sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'DEVICE_FORM',
       'option'   :{
            'dst_net':{
                'type':'select-one',
                'required':'1',
                'ass_check':function(eve){
                    var msg="";
                    var dev = eve._getCURElementsByName("dst_net","select","DEVICE_FORM")[0].value;
                    if (dev == "none"){
                        msg = "必须选择一个设备";
                    }
                    return msg;
                }
            },
            'upwidth':{
                'type':'text',
                'required':'1',
                'check':'num|',
                'ass_check':function(eve){
                    var msg="";
                    var up = eve._getCURElementsByName("upwidth","input","DEVICE_FORM")[0].value;
                    if (up < 2){
                        msg = "不能小于2";
                    }
                    return msg;
                }
            },
            'downwidth':{
                'type':'text',
                'required':'1',
                'check':'num|',
                'ass_check':function(eve){
                    var msg="";
                    var down = eve._getCURElementsByName("downwidth","input","DEVICE_FORM")[0].value;
                    if (down < 2){
                        msg = "不能小于2";
                    }
                    return msg;
                }
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object);
    // check._get_form_obj_table("DEVICE_FORM");
    </script>
EOF
    ;
}

sub remove_config_file($){
    my $file = shift;
    $reload=1;
    system("sudo rm -f $file");
    `sudo fdelete $file`;
}

sub toggle_enable($$) {
    my $devicename = shift;
    my $enable = shift;
    if ( $enable ) {
        $enable = 'on';
    }
    else {
        $enable = 'off';
    }

    my @line=split(/,/,read_config_line($devicename,$qosdevice));

    &save_line($devicename,$line[2],$line[1],$enable);
    $reload = 1;
}

###添加设备的同时添加4个类别到classes文件中
sub save_class($){
    my $devicename = shift;
    my $saves = "";
    my $limits = "";
    my $filename = "";
    my $precedence = "";
    my $classnum = "";
    my $kong = "";
    my @savearr = ("55%","30%","10%","5%");
    my @limitarr = ("100%","100%","80%","100%");
    my $asc_len = 0;
    my $class_name = $ethname{$devicename};
    my $len = rindex $ethname{$devicename}."\$","\$";
    while( $ethname{$devicename} =~ /(.)/g ) {
        my $elem = $1;
        if ($elem =~ /\d+|_|[a-z]/) {
            $asc_len ++;
        }
        
    }
    $len = ($len - $asc_len)/3 + $asc_len;
    if ($len > 14 ) {
        my @temp = split(/_/,$class_name);
        $class_name = $temp[0];
    }
    my @filearr = ($ethname{$devicename}."_高优先级",$ethname{$devicename}."_中优先级",$ethname{$devicename}."_低优先级",$ethname{$devicename}."_超大流量");
    my @precearr = (10,7,4,2);
    for(my $i = 0;$i < 4;$i++){
        #判断当前未使用的classnum最小值并赋值给当前添加的类别
        my $headword = "class";
        my $num = length($j);
        my $numword = "0001";
        $classnum = "class0001";
        foreach my $thisline (read_config_file($qosclass)){
            chomp($thisline);
            my @liness=split(/,/,$thisline);
            push(@temp,$liness[1]);
        }
        @temp = sort(@temp);
        foreach $innum (@temp) {
            if ($classnum eq $innum){
                $numword = $numword + 1;
                $num = length($numword);
                if($num eq 1){
                   $numword = "000".$numword;
                }
                elsif($num eq 2){
                   $numword = "00".$numword;
                }
                elsif($num eq 3){
                   $numword = "0".$numword;
                }
                $classnum = $headword.$numword;
                $num = length($numword);
            }
            
        }

        my @lines_tosave;
        $line ="$devicename,$classnum,$kong,$filearr[$i],$savearr[$i],$limitarr[$i],$precearr[$i]";
        push(@lines_tosave,$line);
        my $file = $qosclass;
        &append_lines($file,\@lines_tosave);
    }
}

sub check_values($$){
   my $upbondwith = shift;
   my $downbandwidth = shift;
   if ( $par{'dst_net'} eq 'none' ) {
        push( @errormessages,"请选择一个设备." );
        if ($par{'ACTION'} eq 'modify') {
            $is_editing = 1;
        }
        return 0;
    }
    if( $upbondwith !~ /^(\d+)%$|^\d+$/) {
        push( @errormessages,"上行带宽格式不对." );
        if ($par{'ACTION'} eq 'modify') {
            $is_editing = 1;
        }
        return 0;
    }
    elsif( $1 < 0 || $1 > 100 ) {
        push( @errormessages,"上行带宽格式不对." );
        if ( $par{'ACTION'} eq 'modify' ) {
            $is_editing = 1;
        }
        return 0;
    }
    if( $downbandwidth !~ /^(\d+)%$|^\d+$/ ){
        push( @errormessages,"下行带宽格式不对." );
        if ( $par{'ACTION'} eq 'modify' ) {
            $is_editing = 1;
        }
        return 0;
    }
    elsif( $1 < 0 || $1 >100 ) {
        push( @errormessages,"下行带宽格式不对." );
        if ( $par{'ACTION'} eq 'modify' ) {
            $is_editing = 1;
        }
        return 0;
    }    
    return 1;
}


sub save_line($$$$){
    my $lineno = shift;
    my $upbandwidth=shift;
    my $downbandwidth = shift;;
    my $checked=shift;
    my $enabled='off';

    chomp($lineno);
    if($checked =~ /^on$/)
    {
        $enabled='on';
    }
    my $line="";
    my $lastline="";
    my $devicename="";
    
    my %sidhash=();

    if( ! check_values($upbandwidth, $downbandwidth) ) {
       return 1;
    }

    #读取用户输入的值并编号保存到qosdevice文件
    if ( $lineno =~ /^\w/ ){
        $devicename = $lineno;
    }
    my @lines_tosave;
    $downbandwidth =~ s/^0+//;
    $upbandwidth =~ s/^0+//;
    $line = "$devicename,$downbandwidth,$upbandwidth,$enabled";
    push(@lines_tosave,$line);
        
    my $file = $qosdevice;
    if ( $par{'ACTION'} eq "add" ){
        &append_lines( $file,\@lines_tosave );
        save_class( $par{'dst_net'} );
    }
    else{
        &update_lines( $devicename, $file, \@lines_tosave );
    }
    $reload = 1;

}
sub delete_line($) {
    my $devicename = shift;
    my @lines3 = read_config_file( $qosconfig );
    my @lines2 = read_config_file( $qosclass );
    my @lines = read_config_file( $qosdevice );
    my @tmp;
    my @temp;
    my $i=0;
    my $j=0;
    my $k=0;
    my $len3 = @lines3;
    my $len1 = @lines2;
    my $len = @lines;
    for( $i; $i<$len; $i++ )
    {
        if ($lines[$i] =~ /^$devicename\,/) {
            delete (@lines[$i]);
            last;
        }
    }
    for($j; $j<$len1; $j++)
    {
        if ($lines2[$j] =~ /^$devicename/) {
            @tmp = split(/,/,$lines2[$j]);
            push (@temp,$tmp[1]);
            delete (@lines2[$j]);
        }
    }
    foreach my $vari (@temp) {
        for($k=0; $k<$len3; $k++){
            if($lines3[$k] =~ /^$vari/){
                delete (@lines3[$k]);
            }
        }
    }
    save_config_file(\@lines2,$qosclass);
    save_config_file(\@lines,$qosdevice);
    save_config_file(\@lines3,$qosconfig);
    $reload = 1;
}

sub update_line($$$){
    my $devicename=shift;
    my $file=shift;
    my $line=shift;
    my @lines = &read_config_file($file);
    my $i=0;
    my $len=@lines;
    
    for($i; $i<$len; $i++)
    {
        if ($lines[$i] =~ /^$devicename\,/) {
            chomp($lines[$i]);
            chomp($line);
            if($lines[$i] !~ /$line/){
                $lines[$i]=$line;
                last;
            }
        }
    }
    
    save_config_file(\@lines,$qosdevice);
}
sub append_lines($$){
    my $file=shift;
    my $ref=shift;
    foreach my $line (@$ref)
    {
        &append_config_file($line,$file);
    }
}

sub delete_lines($$){
    my $devicename=shift;
    my $file=shift;
    my (@head,@body,@tail)=("","","");
    my @lines = &read_config_file($file);
    my $len = @lines;
    my $i=0;
    for($i; $i<$len; $i++)
    {
        last if($lines[$i] =~ /^$devicename\,/);
        push(@head,$lines[$i]);
    }

    for($i; $i<$len; $i++)
    {
        last if($lines[$i] !~ /^$devicename\,/);
        push (@body,$lines[$i]);
    }
    
    for($i; $i<$len; $i++)
    {
        push (@tail,$lines[$i]);
    }
    @lines=();
    push(@lines,@head);
    push(@lines,@tail);
    
    &save_config_file(\@lines,$file);
}

sub update_lines($$$){
    my $devicename=shift;
    my $file=shift;
    my $ref=shift;
    my (@head,@body,@tail)=("","","");
    my @lines = &read_config_file($file);
    my $len = @lines;
    my $i=0;
    for($i; $i<$len; $i++)
    {
        last if($lines[$i] =~ /^$devicename\,/);
        push(@head,$lines[$i]);
    }

    for($i; $i<$len; $i++)
    {
        last if($lines[$i] !~ /^$devicename\,/);
    }

    for($i; $i<$len; $i++)
    {
        push (@tail,$lines[$i]);
    }

    my @tmp_lines="";
    
    push(@tmp_lines,@head);
    push(@tmp_lines,@$ref);
    push(@tmp_lines,@tail);

    &remove_config_file($file);
    &save_config_file(\@tmp_lines,$file);
}

sub append_config_file($$) {
    my $line = shift;
    my $file = shift;    
    if($line !~ /^$/)
    {
        open (FILE, ">>$file");
        print FILE ($line."\n");
        close FILE;
        $reload=1;
        `sudo fmodify $file`;
        return 1;
    }
}
sub display_add($) {
    my $line = shift;
    my ($devicename, $upbandwidth, $downbandwidth, $checked);
    
    if (($is_editing) && ($par{'sure'} ne 'y')) {
        my @rl=split(/,/,read_config_line($line,$qosdevice));
        $devicename = $rl[0];
        $upbandwidth = $rl[2];
        $downbandwidth = $rl[1];
        $checked = $rl[3];
    }
    else{
        $devicename = $par{'dst_net'};
        $upbandwidth = $par{'upwidth'};
        $downbandwidth = $par{'downwidth'};
    }
    if(!$checked || $checked =~/^on$/){
        $checked = 'checked';
    }
    elsif($checked = /^off$/){
        $checked = '';
    }
    if ($upbandwidth !~ /%/) {
        $upbandwidth = $upbandwidth/8 ;
    }
    if ($downbandwidth !~ /%/) {
        $downbandwidth = $downbandwidth/8 ;
    }
    $action = "add";
    my $title = _('添加接口');
    my $buttontext=_("添加");
    if ($is_editing) {
        $action = 'modify';
        $title = _('编辑接口');
        $show = "showeditor";
        $buttontext = _("编辑");
    }
    elsif(@errormessages >0){
        $show = "showeditor";
    }
    else{
        $show = "";
    }
    my @devs_line = read_config_file($qosdevice);
    my $dev_added = ",";
    foreach my $line (@devs_line) {
        my @elem = split(/,/,$line);
        $dev_added .= "$elem[0],"
    }
    &openeditorbox($title,"", $show, "createrule",);
    printf <<EOF
    </form>
    <form name="DEVICE_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type="hidden" name="ACTION" value="$action">
        <input type="hidden" name="line" value="$line">
        <input type="hidden" name="sure" value="y">
        <table width="100%" >
            <tr class="env">
                <td class="add-div-type">
                    目标设备*
                </td>
                <td>
                    <select name="dst_net" onchange="" onkeyup="" style = "width:289px;">
EOF
    ;
    if($action eq 'modify'){
        printf <<EOF
                        <option name="dst_net" value = "$devicename" >$ethname{$devicename}</option>
EOF
        ;
    }
    else{
        print "<option value='none'>请选择</option>";
        foreach my $key (sort keys %ethname) {
            if ($dev_added !~ $key) {
                print "<option value=$key>$ethname{$key}</option>";
            }
        }
    }

   printf<<EOF 
                    </select>
                </td>
            </tr>
            <tr class="odd">
                <td class="add-div-width">
                    上行带宽(KB/s)*
                </td>
                <td>
                    <input type = 'text' maxlength="8" name = "upwidth" style = "width:30%;" value= $upbandwidth>
                </td>
            </tr>
            <tr class="env">
                <td class="add-div-width">
                    下行带宽(KB/s)*
                </td>
                <td>
                    <input type = 'text' maxlength="8" name = "downwidth" style = "width:30%;" value= $downbandwidth>
                </td>
            </tr>
       

EOF
    ;
    printf <<EOF
            <tr  class="odd">
                <td class="add-div-width">
                    <b>启用</b>
                </td>
                <td>
                    <input type='checkbox' name='enabled' $checked />
                </td>
            </tr>
        </table>
    
EOF
, _('sid')
;
                        
    &closeeditorbox($buttontext, _("Cancel"), "routebutton", "createdevice", $ENV{'SCRIPT_NAME'});
}

sub display_devices($) {
    my $line = shift;
    display_add($line);
    #显示已有数据，即qos设备    
    printf <<END
    <table  class="ruleslist">
        <tr>
            <td  class="boldbase" style="width:25%;">%s</td>
            <td  class="boldbase" style="width:20%;">%s</td>
            <td  class="boldbase" style="width:20%;">%s</td>
            <td  class="boldbase" style="width:10%;">%s</td>
        </tr>
    
END
    , _('设备')
    , _('上行带宽(KB/s)')
    , _('下行带宽(KB/s)')
    , _('动作')
    ;
    
    my @lines = &read_config_file($qosdevice);
    
    my $i = 0;
    my $line = $par{'val_line'};
    if ( @lines > 0 )
    {
        foreach my $thisline (@lines) {
            chomp($thisline);
            
            my @line=split(/,/,$thisline);
            my $devicename = $line[0];
            my $upbandwidth =  $line[2]/8;
            my $downbandwidth = $line[1]/8;
            my $enabled = $line[3];
            my $enabled_gif = $DISABLED_PNG;
            my $enabled_alt = _('Disabled (click to enable)');
            if ($enabled eq 'on') {
                $enabled_gif = $ENABLED_PNG;
                $enabled_alt = _('Enabled (click to disable)');
            }
            my $bgcolor = setbgcolor($is_editing, $line, $i);
            
            print "<tr class='$bgcolor'>";
            printf <<EOF
        <td>$ethname{$devicename}</td>
        <td>$upbandwidth</td>
        <td>$downbandwidth</td>
        <td class="actions">
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" title="$enabled_alt" />
                <input type="hidden" name="ACTION" value="$enabled">
                <input type="hidden" name="line" value="$devicename">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
                <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="line" value="$devicename">
                <input type="hidden" name="val_line" value="$i">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" onsubmit='return confirm("确认删除？")'>
                <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="line" value="$devicename">
            </form>
        </td>
    </tr>
EOF
            ,
            _('Edit'),
            _('Delete');
            $i++;
        }
    } else {
        no_tr(4,"无内容");
    }
    print "</table>";

    if ( $i > 0 )
    {
        printf <<EOF
        <table class="list-legend" cellpadding="0" cellspacing="0">
            <tr>
                <td>
                    <B>%s:</B>
                    <IMG SRC="$ENABLED_PNG" title="%s" />
                    %s
                    <IMG SRC='$DISABLED_PNG' title="%s" />
                    %s
                    <IMG SRC="$EDIT_PNG" title="%s" />
                    %s
                    <IMG SRC="$DELETE_PNG" title="%s" />
                    %s
                </td>
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

sub save() {
    $action = $par{'ACTION'};
    $sure = $par{'sure'};

    if($action eq "edit")
    {
        $is_editing = 1;
    }
    
    if ($action eq 'delete') {
        delete_line($par{'line'});
        delete_lines($par{'line'},$qosdevice);
        %par=();
        return;
    }

    if ($action eq 'off') {
        toggle_enable($par{'line'}, 1);
        %par=();
        return;
        
    }
   if ($action eq 'on') {
        toggle_enable($par{'line'}, 0);
        %par=();
       return;
       
   } 
    if ($par{'upwidth'} !~ /%/) {
          $par{'upwidth'} = $par{'upwidth'}*8;
      }
      if ($par{'downwidth'} !~ /%/) {
          $par{'downwidth'} = $par{'downwidth'}*8;
      }   
    if ($action eq 'add') {
        save_line(
            $par{'dst_net'},
            $par{'upwidth'},
            $par{'downwidth'},
            $par{'enabled'});
        %par=();
        return;
    }
    
    if($action eq 'modify'){
        save_line(
            $par{'dst_net'},
            $par{'upwidth'},
            $par{'downwidth'},
            $par{'enabled'}); 
        %par=();

        return;
    }
}


$extraheader .="<script type='text/javascript' src='/include/waiting.js'></script>";
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('QOS设备'), 1, $extraheader);
save();
my $errormessage = "";
if(@errormessages>0)
{
    $reload = 0;
    foreach my $err(@errormessages)
    {
        $errormessage .= $err."<br />";
    }
}
&openbigbox($errormessage, $warnmessage, $notemessage);


if ($reload) {
    system("touch $needreload");
}
if (-e $needreload ) {
    if ($par{'ACTION'} ne 'apply') {
        applybox(_("配置已经更改，需要应用才能使更改生效!"));
    }
}

$lineno = $par{'line'};
display_devices($lineno);
check_form()
&closebigbox();

if ($par{'ACTION'} eq 'apply') {
    printf <<EOF
    <script>
        RestartService("正在应用配置，请稍后...");
    </script>
EOF
    ;
    &log("QOS应用规则配置");
    system("/usr/local/bin/restartqos");
    printf <<EOF
    <script>
        endmsg("成功应用当前配置.");
    </script>
EOF
    ;
}

&closepage();
