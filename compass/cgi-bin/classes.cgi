#!/usr/bin/perl

#file:classes.cgi
#author:zhangzheng
#modified by wanglin 2014.05.06


require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'qos_ethernet.pl';
my $qosclass="/var/efw/shaping/classes";
my $qosdevice="/var/efw/shaping/devices";
my $qosconfig="/var/efw/shaping/config";
my $needreload = "${swroot}/shaping/needreload";
my $extraheader="";
my @errormessages=();

$EDIT_PNG="/images/edit.png";
$DELETE_PNG="/images/delete.png";
$reload=0;

my $action = $par{'ACTION'};
my %youxian=(
       "10" =>"10 -- 高",
       "9"=>"9",
       "8"=>"8",
       "7"=>"7",
       "6"=>"6",
       "5"=>"5 -- 中",
       "4"=>"4",
       "3"=>"3",
       "2"=>"2",
       "1"=>"1 -- 低",
);
my $temp = &ethname();
my %ethname = %$temp;
sub read_config_line($$) {
    my $classnum = shift;
    my $file=shift;

    my @lines = read_config_file($file);
    foreach $thisline (@lines)
    {
        chomp($thisline);
        my @rl = split(/,/,$thisline);
        if($rl[1] eq $classnum)
        {
              return $thisline; 
        }
    }
}
sub check_form(){
    printf <<EOF
    <script>
       var check = new ChinArk_forms();
       var object = {
       'form_name':'CLASS_FORM',
       'option':{
            'classn':{
               'type':'text',
               'required':'0',
               'check':'num|'
            },
            'filen':{
                   'type':'text',
                   'required':'1',
                   'check':'other|',
                   'other_reg':'!/^\$/',
                   'ass_check':function(eve){
                          var msg="";
                          var title_ip;
                          var names = eve._getCURElementsByName("filen","input","CLASS_FORM")[0].value;
                          var dev = eve._getCURElementsByName("devicen","select","CLASS_FORM")[0].value;
                          var action = eve._getCURElementsByName("ACTION","input","CLASS_FORM")[0].value;
                          var reg = /\^[0-9a-zA-Z\\u4e00-\\u9fa5][_0-9a-zA-Z\\u4e00-\\u9fa5]+\$/;
                          var len = 30;
                          if((names.length >= 4) && (names.length <= len)){
                              if(/\\s/.test(names)){msg = names+"含有空格！";}
                              if(!reg.test(names)){msg = names+"含有非法字符或空格！";}
                          }
                          else{                        
                              if(names.length < 4 || names.length > 30){
                                  msg = names + "应4个字符以上30各字符以内！";
                              }
                          }
                          if (action == "add"){
                              if (!eve.named){
                                  \$.ajax({
                                        type : "get",
                                        url : '/cgi-bin/chinark_back_get.cgi',
                                        async : false,
                                        data : 'path=/var/efw/shaping/classes',
                                        success : function(data){
                                            eve.named = data;
                                        }
                                        });
                              }       
                              var exist = eve.named.split('\\n');
                              for (var i = 0; i < exist.length; i++) {
                                  var tmp = exist[i].split(',');
                                  if(tmp[3] == names){
                                    msg = "类名已存在";
                                    break;
                                  }
                              }   
                          }                                                                
                          return msg;
                      }
                },
                'saven':{
                   'type':'text',
                   'required':'1',
                   'check':'num|percent|',
                   'ass_check':function(eve){
                              var msg="";
                              var title_ip;
                              var save = eve._getCURElementsByName("saven","input","CLASS_FORM")[0].value;
                              var limit = eve._getCURElementsByName("limitn","input","CLASS_FORM")[0].value;
                              var dev = eve._getCURElementsByName("devicen","select","CLASS_FORM")[0].value;
                              if (!eve.band){
                                   \$.ajax({
                                         type : "get",
                                         url : '/cgi-bin/chinark_back_get.cgi',
                                         async : false,
                                         data : 'path=/var/efw/shaping/devices',
                                         success : function(data){
                                             eve.band = data;
                                         }
                                         });
                               }       
                               var exist = eve.band.split('\\n');
                               var reg = /\%/;
                               if(!((((save >= 1) && (limit >= 1)) || ((reg.test(save)) && (reg.test(limit)))) && (parseInt(save) < parseInt(limit)))){
                                     msg = "保留带宽需小于限制带宽且需同数据类型";
                               }
                               if(!save){
                                       msg = "";
                               }  
                               for (var i = 0; i < exist.length; i++) {
                                      var tmp = exist[i].split(',');
                                      if(tmp[0] == dev){
                                          var max = tmp[2] * 0.12;
                                          if(save > max){
                                                msg = "不能大于设备上行带宽的96%";    
                                                break;                                                                      
                                          }
                                      }
                               }                                              
                              return msg;
                         }
                     },
                'limitn':{
                   'type':'text',
                   'required':'1',
                   'check':'percent|num|',
                   'ass_check':function(eve){
                          var msg="";
                          var title_ip;
                          var limit = eve._getCURElementsByName("limitn","input","CLASS_FORM")[0].value;
                          var save = eve._getCURElementsByName("saven","input","CLASS_FORM")[0].value;
                          var dev = eve._getCURElementsByName("devicen","select","CLASS_FORM")[0].value;
                          if (!eve.band){
                               \$.ajax({
                                     type : "get",
                                     url : '/cgi-bin/chinark_back_get.cgi',
                                     async : false,
                                     data : 'path=/var/efw/shaping/devices',
                                     success : function(data){
                                         eve.band = data;
                                     }
                                     });
                           }       
                           var exist = eve.band.split('\\n');      
                           var reg = /\%/;                                                      
                           if(!((((save >= 1) && (limit >= 1)) || ((reg.test(save)) && (reg.test(limit)))) && (parseInt(save) < parseInt(limit)))){
                                 msg = "保留带宽需小于限制带宽且需同数据类型";
                           }   
                           if(!save){
                                   msg = "";
                           }    
                           for (var i = 0; i < exist.length; i++) {
                                  var tmp = exist[i].split(',');
                                  if(tmp[0] == dev){
                                      var max = tmp[2] * 0.12;
                                      if(limit > max){
                                            msg = "不能大于设备上行带宽的96%";
                                            break;                                                                          
                                    }
                                }
                            }                                                   
                        return msg;
                    }
                }
            }
    }
    check._main(object);
    //check._get_form_obj_table("CLASS_FORM");
    </script>
EOF
;
}
sub remove_config_file($){
    my $file = shift;
    system("sudo rm -f $file");
    `sudo fdelete $file`;
}

sub check_values($$$){
   my $filename = shift;
   my $saves = shift;
   my $limits = shift;
   my @devices = read_config_file($qosdevice);
   my $maxband;
   foreach my $line (@devices) {
       my @temp = split(/,/,$line);
       if ($temp[0] eq $par{'devicen'}) {
           $maxband = $temp[2] * 0.96;
       }
   }
   if($filename =~ /^$/){
        push(@errormessages,"类名不能为空.");
        return 0;
    } 
    if($filename!~ /^[a-zA-Z0-9\x80-\xff]|_/){
        push(@errormessages,"类名不合法.");
        return 0;
    }
    if($par{'ACTION'} eq 'add'){
        foreach my $line (read_config_file($qosclass)) {
            $line =~/class(\d+),,(.*),.*,.*,\d+/;
            my $existname = $2;
            if ($filename eq $existname) {
                push(@errormessages,"类名已存在.");
                return 0;
            }
        }
    }
    if($limits !~ /^(\d+)%$|^\d+$/){
        push(@errormessages,"限制带宽格式不对.");
        return 0;
        }
        elsif($1<0 || $1 >100){
        push(@errormessages,"限制带宽格式不对.");
        return 0;
        }
    if($limits > $maxband){
        push(@errormessages,"限制带宽数值不能大于设备上行带宽的96%.");
        return 0;
    }
    if($saves  !~ /^(\d+)%$|^\d+$/){
        push(@errormessages,"保留带宽格式不对.");
        return 0;
        }
        elsif($1<0 || $1 >100){
        push(@errormessages,"保留带宽格式不对.");
        return 0;
        }
    if($saves > $maxband){
        push(@errormessages,"保留带宽数值不能大于设备上行带宽的96%.");
        return 0;
    }
    return 1;
}

sub check_saves($$$) {
    my $saves = shift;
    my $devicename = shift;
    my $classnum = shift;
    my $device_limit = '';
    my %exist_saven;
    my @devices = read_config_file( $qosdevice );
    my @classes = read_config_file( $qosclass );

    foreach my $thisline ( @devices ) {
        my @temp = split( ",", $thisline );
        if ( $devicename eq $temp[0] ) {
            $device_limit = $temp[2];
            last;
        }
    }

    foreach my $thisline ( @classes ) {
        my @temp = split( ",", $thisline );
        if ( $devicename eq $temp[0] ) {
            $exist_saven{$temp[1]} = $temp[4];
        }
    }

    foreach my $thisline ( keys %exist_saven ) {
        if ( $exist_saven{$thisline} =~ /^(\d+)%$/ ) {
            #百分比的都转成具体带宽
            $exist_saven{$thisline} = $device_limit * $1 / 100;
        }
    }
    my $left_limit = $device_limit;

    my $left_limit_perctg = '';
    foreach my $thisline ( keys %exist_saven ) {
        if ( $thisline ne $classnum ) {
            $left_limit = $left_limit - $exist_saven{$thisline};
        }
    }

    $left_limit_perctg = int( $left_limit / $device_limit * 100 );
    my $left_limit_str = int( $left_limit );
  
    if ( $saves =~ /^(\d+)%$/ ) {
        #==填入的是百分比==#
        my $saves_true = $device_limit * $1 / 100;
        if ( $saves_true > $left_limit ) {
            if ( $left_limit_str == 0 ) {
                push(@errormessages,"当前无可用保留带宽,请先修改其他类再继续当前操作");
            } else {
                push(@errormessages,"保留带宽数值不能大于 $left_limit_perctg%.");
            }
            return 0;
        }
    } else {
        #==填入的是数值==#
        if ( $saves > $left_limit ) {
            if ( $left_limit_str == 0 ) {
                push(@errormessages,"当前无可用保留带宽,请先修改其他类再继续当前操作");
            } else {
                push(@errormessages,"保留带宽数值不能大于 $left_limit_str kbit/s.");
            }
            return 0;
        }
    }

    return 1;
}

sub save_line_add($$$$$$){
    my $devicename = shift;
    my $saves=shift;
    my $limits=shift;
    my $filename=shift;
    my $precedence=shift;
    my $lineno = shift;
    my $kong = "";
    my $line="";
    my $classnum="";
    if( ! check_values($filename,$saves,$limits)){
       return 1;
    }
    #====对相同设备的不同类的保留带宽之和不能大于该设备的上行带宽===#
    if( ! check_saves( $saves, $devicename, $classnum ) ){
       return 1;
    }
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
    #读取用户输入的值并编号保存到qosclass文件
    if($lineno =~ /^\S/){
        $filename=$lineno;
    }
    if($precedence eq "10 -- 高"){
       $precedence = 10;
    }
    elsif($precedence eq "5 -- 中"){
       $precedence = 5;
    }
    elsif($precedence eq "0 -- 低"){
       $precedence = 0;
    }
    my @lines_tosave;
    $saves =~s/^0+//;
    $limits =~s/^0+//;
    &debug2file($saves);
    &debug2file('asdf');
    if ($saves eq '%') {
      $saves = '0%'
    }
    if ($limits eq '%') {
      $limits = '0%'
    }
    $line ="$devicename,$classnum,$kong,$filename,$saves,$limits,$precedence";
    push(@lines_tosave,$line);
        
    my $file = $qosclass;
    &append_lines($file,\@lines_tosave);
}

sub save_line_edit($$$$$$){
    my $devicename = shift;
    my $saves=shift;
    my $limits=shift;
    my $filename=shift;
    my $precedence=shift;
    my $lineno= shift;
    my $kong = "";

    my $line="";
    my $classnum="";
    
    if( ! check_values($filename,$saves,$limits)){
       return 1;
    }
    #====对相同设备的不同类的保留带宽之和不能大于该设备的上行带宽===#
    if( ! check_saves( $saves, $devicename, $lineno ) ){
       return 1;
    }
    #读取用户输入的值并编号保存到qosclass文件
    if($lineno =~ /^\S/){
        $classnum=$lineno;
    }
    my @lines_tosave;
    $saves =~s/^0+//;
    $limits =~s/^0+//;
    &debug2file($saves);
    &debug2file('asdf');
    if ($saves eq '%') {
      $saves = '0%'
    }
    if ($limits eq '%') {
      $limits = '0%'
    }
    $line ="$devicename,$classnum,$kong,$filename,$saves,$limits,$precedence";
    push(@lines_tosave,$line);
    my $file = $qosclass;
    if ($classnum =~ /^\S/){
        &update_lines($classnum,$file,\@lines_tosave);
    }
}

sub delete_line($$) {
    my $classnum = shift;
    my $precedence = shift;
    my @lines = read_config_file($qosclass);
    my @lines2 = read_config_file($qosconfig);
    my $j=0;
    my $i=0;
    my $len=@lines;
    my $len2=@lines2;
    for($i; $i<$len; $i++)
    {

        if (($lines[$i] =~ /$classnum/) && ($lines[$i] =~ /$precedence/)) {    
            delete (@lines[$i]);
            last;
        }
    }
    for($j; $j<$len; $j++)
    {

        if ($lines[$j] =~ /$classnum/) {    
            delete (@lines2[$j]);
            last;
        }
    }
    save_config_file(\@lines,$qosclass);
    save_config_file(\@lines2,$qosconfig);
}

sub update_line($$$){
    my $classnum=shift;
    my $file=shift;
    my $line=shift;
    my @lines = &read_config_file($file);
    my $i=0;
    my $len=@lines;
    
    for($i; $i<$len; $i++)
    {
        if ($lines[$i] =~ /$classnum/) {
            chomp($lines[$i]);
            chomp($line);
            if($lines[$i] !~ /$line/){
                $lines[$i]=$line;
                last;
            }
        }
    }
    
    save_config_file(\@lines,$qosclass);
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
    my $classnum=shift;
    my $file=shift;
    my (@head,@body,@tail)=("","","");
    my @lines = &read_config_file($file);
    my $len = @lines;
    my $i=0;
    for($i; $i<$len; $i++)
    {
        last if($lines[$i] =~ /$classnum\,/);
        push(@head,$lines[$i]);
    }

    for($i; $i<$len; $i++)
    {
        last if($lines[$i] !~ /$classnum\,/);
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
sub delete_lines_qosconfig($$){
    my $classnum=shift;
    my $file=shift;
    my (@head,@body,@tail)=("","","");
    my @lines = &read_config_file($file);
    my $len = @lines;
    my $i=0;
    for($i; $i<$len; $i++)
    {
        last if($lines[$i] =~ /$classnum\,/);
        push(@head,$lines[$i]);
    }

    for($i; $i<$len; $i++)
    {
        last if($lines[$i] !~ /$classnum\,/);
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
    my $classnum=shift;
    my $file=shift;
    my $ref=shift;
    my (@head,@body,@tail)=("","","");
    my @lines = &read_config_file($file);
    my $len = @lines;
    my $i=0;
    for($i; $i<$len; $i++)
    {
        last if($lines[$i] =~ /$classnum/);
        push(@head,$lines[$i]);
    }

    for($i; $i<$len; $i++)
    {
        last if($lines[$i] !~ /$classnum/);
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
        %par=();
        return 1;
    }
}
sub display_add($$) {

    my $is_editing = shift;
    my $line = shift;
    my ($devicename, $filename, $classnum, $kong, $saves, $limits, $precedence);
    my %selected;
=p
    if ($is_editing ne 1 && $#errormessages ne -1) {
            $is_editing = 1;
    }
=cut
    if (($is_editing) && ($par{'sure'} ne 'y')) {
       
        my @rl=split(/,/,read_config_line($line,$qosclass));
         $devicename = $rl[0];
         $classnum = $rl[1];
         $kong =  $rl[2];
         $filename = $rl[3];
         $saves = $rl[4];
         $limits = $rl[5];
         $precedence = $rl[6];
    }
    else{
         $devicename = $par{'devicen'};
         $classnum = $par{'classn'};
         $kong = "";
         $filename = $par{'filen'};
         $saves = $par{'saven'};
         $limits = $par{'limitn'};
         $precedence = $par{'precen'};
    }
    if ($saves !~ /%/) {
      $saves = $saves/8;
  
    }
    if ($limits !~ /%/) {
      $limits = $limits/8;
  
    }
    my $action = 'add';
    my $title = _('添加QOS类');
    my $show="";
    my $buttontext=_("添加");
    if ($is_editing) {
        $action = 'edit';
        $title = _('编辑QOS类');
        $show = "showeditor";
        $buttontext = _("编辑");
    }
    if ($#errormessages ne -1) {        
        $show = "showeditor";
    }
    my $read_only="";
    $selected{$precedence} = "selected='selected'";
    $selected{$devicename} = "selected='selected'";
    openeditorbox($title, $title, $show, "addqosclass", );
    printf <<EOF
</form>
    <form name="CLASS_FORM" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="val_line" value="$par{'val_line'}"/>
     <table> 
       <tr class="env">
         <td class="add-div-type">%s</td>
         <td> <select name = "devicen" style="width:30.5%">
EOF
     , _('QOS设备')
;
     if($action eq 'edit'){
         $read_only="readonly";
         printf <<EOF
                  <option name="devicen" value = "$devicename">$ethname{$devicename}</option>
                     
EOF
;
    }
    else{
        foreach my $thisline (read_config_file($qosdevice)){
                 chomp($thisline);
                 my @liness=split(/,/,$thisline);
                 push(@temp,$liness[0]);
        }
        foreach $devicename (@temp) {
            chomp($devicename);
            print "<option name='devicen' $selected{$devicename} value = '$devicename'>$ethname{$devicename}</option>";
        }
    }
    printf <<EOF

                    </select></td></tr>
                  <tr class="odd" style="display:none;"><td class="add-div-type">%s</td>
                  <td><input type = 'text' name = "classn"  value = '$classnum' >
                  </td></tr>
                  <tr class="env"><td class="add-div-type">%s *</td>
                  <td><input type = 'text' maxlength="300"  name = "filen" style = "width:30%;" value='$filename' $read_only></td></tr>
                  <tr class="odd"><td class="add-div-type">%s *</td>
                   <td><input type = 'text' name = "limitn" style = "width:30%;" value= '$limits'></td></tr>
                  <tr class="odd"><td class="add-div-type">%s *</td>
                  <td><input type = 'text' name = "saven" style = "width:30%;" value= '$saves'></td></tr>
                   <tr class="odd"><td class="add-div-type">%s *</td>
                   <td>
                  <select type = 'text' name = "precen" style = "width:30.5%;">
                  <script>
                    \$('input[name="saven"]').blur(function(){
                      \$('#CLASS_FORMsavenCHINARK_ERROR_TIP').hide();
                    });
                    \$('input[name="limitn"]').blur(function(){
                      \$('#CLASS_FORMlimitnCHINARK_ERROR_TIP').hide();
                    });
                  </script>
EOF
     , _('classnum')
     , _('类名')
     , _('限制带宽(KB/s或%)')
     , _('保留带宽(KB/s或%)')
     , _('优先级(0-10)')
;
            foreach my $key (sort {$a<=>$b} keys %youxian) {
                print "<option value='$key' $selected{$key}>$youxian{$key}</option>";
            }
     printf <<EOF                 
                   </select>    
                   </td>
                   </tr> 
                   </table>
                  <script>\$('.add-div-type').css('width','20%');</script>

                    <input type="hidden" name="ACTION" value="$action">
                    <input type="hidden" name="line" value="$line">
                    <input type="hidden" name="sure" value="y">
EOF
;
    &closeeditorbox($buttontext, _("Cancel"), "routebutton", "createclass", "$ENV{SCRIPT_NAME}");
}

sub display_devices($$) {

    my $is_editing = shift;
    my $line = shift;

    #&openbox('100%', 'left', '当前设备类别');
    display_add($is_editing, $line);

#显示已有数据，即qos设备    
    printf <<END
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr>
            <td class="boldbase" style="width:25%;">%s</td>
            <td class="boldbase" style="width:20%;">%s</td>
            <td class="boldbase" style="width:100px;">%s</td>
            <td class="boldbase" style="width:100px;">%s</td>
            <td class="boldbase" style="width:100px;">%s</td>
            <td class="boldbase" style="width:100px;">%s</td>
        </tr>
    
END
    , _('Device')
    , _('类名')
    , _('Reserved')
    , _('Limit')
    , _('优先级')
    , _('Actions')
    ;
    
    my @lines = &read_config_file($qosclass);
    my $i = 0;

    if(@lines>0)
    {
        
    foreach my $thisline (@lines) {
        chomp($thisline);
        
        my @line=split(/,/,$thisline);
        my $devicename = $line[0];
        my $classnum = $line[1];
        my $kong =  $line[2];
        my $filename = $line[3];
        my $saves = $line[4];
        my $limits = $line[5];
        if ($saves !~ /%/) {
          $saves = $saves/8;
        }
        if ($limits !~ /%/) {
          $limits = $limits/8;
        }
        my $precedence = $line[6];
        my $bgcolor;
        my $line = $par{'val_line'};
        my $bgcolor = setbgcolor($is_editing, $line, $i); 
        print "<tr class='$bgcolor'>";
        printf <<EOF
        <td>$ethname{$devicename}</td>
        <td>$filename</td>
        <td>$saves</td>
        <td>$limits</td>
        <td>$precedence</td>
        <td>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}"  class="inline">
                <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="line" value="$classnum">
                <input type="hidden" name="val_line" value="$i">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" style = "margin-left:10px;" class="inline" onsubmit='return confirm("确认删除？")'>
                <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" title="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="line" value="$classnum">
            </form>
        </td>
    </tr>
EOF
,
_('Edit'),
_('Delete');
        $i++;
    }
}else{

    no_tr(6,"无内容");
}
print "</table>";
            
if($i>0)
{
            printf <<EOF
        <table class="list-legend" cellpadding="0" cellspacing="0">
          <tr>
            <td>
              <B>%s:</B>
            <IMG SRC="$EDIT_PNG" title="%s" />
            %s
            <IMG SRC="$DELETE_PNG" title="%s" />
            %s</td>
          </tr>
        </table>
EOF
,
_('Legend'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')
;

}
    #&closebox();
}

sub save() {
    my $sure = $par{'sure'};
    $action = $par{'ACTION'};
    if ($action eq 'delete') {
        delete_line($par{'line'},$par{'precen'});
        delete_lines($par{'line'},$qosclass);
        delete_lines_qosconfig($par{'line'},$qosconfig);
        %par=();
        $reload = 1;
        return;
    }
    
    if ($action eq 'add') {
        my $filename = $par{'filen'};
        $filename =~ s/([\&\;\`\\\|\*\?\~\<\>\^\(\)\[\]])//g;
        if ($par{'saven'} !~ /%/) {
          $par{'saven'} = $par{'saven'}*8;
        }
        if ($par{'limitn'} !~ /%/) {
          $par{'limitn'} = $par{'limitn'}*8;
        }
        if ($par{'saven'} eq '%') {
          $par{'saven'} = '0%';
        }
        if ($par{'limitn'} eq '%') {
          $par{'limitn'} = '0%';
        }

        save_line_add(
            $par{'devicen'},
            $par{'saven'},
            $par{'limitn'},
            $filename,
            $par{'precen'},
            $par{'classn'}
        );
        
        return;
    }
    
    if ($action eq 'apply') {
        system("/usr/local/bin/restartqos");
        $notemessage ="成功应用当前配置.";
    }
    
    if(($action eq 'edit')&&($sure eq 'y')){
        my $filename = $par{'filen'};
        $filename =~ s/([\,\&\;\`\\\|\*\?\~\<\>\^\(\)\[\]])//g;
        if ($par{'saven'} !~ /%/) {
          $par{'saven'} = $par{'saven'}*8;
        }
        if ($par{'limitn'} !~ /%/) {
          $par{'limitn'} = $par{'limitn'}*8;
        }

        save_line_edit(
            $par{'devicen'},
            $par{'saven'},
            $par{'limitn'},
            $filename,
            $par{'precen'},
            $par{'classn'}
        );
        if( @errormessages > 0 ) {
            #do nothing
        } else {
            %par=();
            $reload = 1;
        }
        return;
    }
    
}


$extraheader .="<script type='text/javascript' src='/include/waiting.js'></script>";
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('QOS设备'), 1, $extraheader);

$classnum = $par{'line'};
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
if ($reload) {
    system("touch $needreload");
}

if (-e $needreload) {
    applybox(_("配置已经更改，需要应用才能使更改生效!"));
}
&openbigbox($errormessage, $warnmessage, $notemessage);
display_devices(($par{'ACTION'} eq 'edit'), $classnum);
check_form();
&closebigbox();
&closepage();