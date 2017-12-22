#!/usr/bin/perl
#DATE:2013-7-7
#author:殷其雷

require '/var/efw/header.pl';

use CGI::Carp qw (fatalsToBrowser);
use CGI qw(:standard);
use Encode;

my $cgi= new CGI;       
my $update_file = "/var/efw/openvpn/forns/server_update/update_server";
my $backup_file = "/var/efw/openvpn/forns/server_update/backup_server";
my $node_dir = "/var/efw/openvpn/forns/node_structure/";
my $node_dir2 = "/var/efw/openvpn/forns/node_structure";
my $update_dir = "/var/efw/openvpn/forns/server_update/";
my $setting_dir = "/var/efw/openvpn/forns/node_setting/";
my $setting = "/var/efw/openvpn/forns/node_setting/settings";
my $cmd = 'sudo /usr/local/bin/mv_install.sh';
my $cmd_serverupdate = 'sudo /usr/local/bin/update_sslvpnserversetting';
my %par;
my %node_save;
my %update_save;
my %backup_save;
my %update_settings;
my %backup_settings;
my %node_conf;
my %client_type_selected;
my $errormessage='';
my $warnmessage='';
my $notemessage='';
my $node_count = 0;
&showhttpheaders();
&getcgihash(\%par);
&make_file();
&save();
&make_node_settings();
&read_update_conf();
my $extraheader = "<script language='JavaScript' type='text/javascript' src='/include/sslvpn_server.js'></script>";
&openpage(_('SSLVPN服务器管理'), 1, $extraheader);
&openbigbox($errormessage, $warnmessage, $notemessage);
&display_html();
&display_add();
&display_structure();
&closebigbox();
&closepage();
&check_form();

sub save(){
    if($par{'ACTION'} eq "save_update"){ 
        
        #$update_save{'SERVER'} = $par{'sslvpn_main'};
        $par{'sslvpn_bakcup'} =~ s/[\r\n\s]+/\n/g;
        chomp($par{'sslvpn_bakcup'});
        $par{'sslvpn_bakcup'} =~ s/\n/,/g;
        $update_save{'SERVER'} = $par{'sslvpn_bakcup'};
        $backup_save{'SERVER'} = $par{'sslvpn_bakcup'};
        $backup_save{'version'} = $par{'version'};
        $backup_save{'client_type'} = $par{'client_type'};
        
        #上传最新SSLVPN客户端程序
        my $filehandle = $cgi->param('UP_FILE');
        my $filename = $filehandle;
        my @tmp = split(/\./,$filename);
        
        if($filehandle ne '' && $tmp[1] ne 'exe')
        {
           $errormessage = "客户端安装程序上传错误，请选择一个exe文件上传！";
           return;
        }
        
        if($filehandle ne '')
        {
          my $tmp_name = "/var/efw/openvpn/forns/dingdian_sslvpn_installer.exe";
          if(-e $tmp_name)
          {
             `rm $tmp_name`;
          }
          `touch $tmp_name`;
          open ( UPLOADFILE, ">$tmp_name" ) or die "$!";
          binmode UPLOADFILE;
          while (<$filehandle>) 
          {
             print UPLOADFILE;
          }
          close UPLOADFILE;
        }
        #`$cmd`;
        
        if(!-e $update_file){
           `touch $update_file`;
         }
        writehash($update_file,\%update_save);
        
        if(!-e $backup_file){
           `touch $backup_file`;
           `echo >>$backup_file version=1.0`;
           `echo >>$backup_file client_type=psk`;
         }
        writehash($backup_file,\%backup_save);
        
        $notemessage = "SSLVPN更新服务器配置成功！";
    }
    
    if($par{'ACTION'} eq "save_node"){
        $node_save{'node_name'} = $par{'node_name'};
        $node_save{'e-government-ip'} = $par{'e-government-ip'};
        $node_save{'internet-government-ip'} = $par{'internet-government-ip'};
        $node_save{'ca-ip'} = $par{'ca-ip'};
        
        if($par{'first-father'} eq '')
        {
           #创建省级服务器
           my $path = $node_dir;
           &make_node($path);
        }
        
        if($par{'second-father'} eq '' && $par{'first-father'} ne '')
        {
           #创建市级服务器
           my $path = $node_dir;
           $path .= $par{'first-father'};
           $path .= '/';
           my $result = &make_node($path);
        }
        
        if($par{'third-father'} eq '' && $par{'second-father'} ne '' && $par{'first-father'} ne '')
        {
           #创建县级服务器
           my $path = $node_dir;
           $path .= $par{'first-father'};
           $path .= '/';
           $path .= $par{'second-father'};
           $path .= '/';
           my $result = &make_node($path);
        }
        
        if($par{'third-father'} ne '' && $par{'second-father'} ne '' && $par{'first-father'} ne '')
        {
           #创建底层服务器
            my $path = $node_dir;
           $path .= $par{'first-father'};
           $path .= '/';
           $path .= $par{'second-father'};
           $path .= '/';
           $path .= $par{'third-father'};
           $path .= '/';
           my $result = &make_node($path);
        }
        
        if($result ne 0)
        {
          $notemessage = "新SSLVPN服务器创建成功！";
        } else {
          $errormessage = "服务器创建失败，父服务器不存在或已被修改！";
        }
    }
    
    if($par{'ACTION'} eq 'edit_node')
    {
        $node_save{'node_name'} = $par{'node_name'};
        $node_save{'e-government-ip'} = $par{'e-government-ip'};
        $node_save{'internet-government-ip'} = $par{'internet-government-ip'};
        $node_save{'ca-ip'} = $par{'ca-ip'};
        
        my $old_path = $par{'path'};
        my @old_splited = split(/\//,$old_path);
        my $new_path;
        my $count = 0;
        foreach my $one (@old_splited)
        {
            if($count < scalar(@old_splited)-1 )
            {
               $new_path .= $one;
               $new_path .= "/";
            }
            $count++;
        }
        $new_path .= $par{'node_name'};
        
        if($par{'node_name'} ne $par{'old_name'})
        {
           if(-e $new_path)
           {
              $errormessage = "当前位置已存在同名的服务器，编辑失败！";
              return
           } else {
              `mv $old_path $new_path`;
              $new_path .= "/";
              $new_path .= "node-info";
              writehash($new_path,\%node_save);
              $notemessage = "SSLVPN服务器编辑成功！";
           }
        } else {
           $old_path .= "/";
           $old_path .= "node-info";
           writehash($old_path,\%node_save);
           $notemessage = "SSLVPN服务器编辑成功！";
        }
         
    }
    
    if($par{'ACTION'} eq 'remove')
    {
       my $del_path = $par{'path'};
       `rm -r $del_path`;
       $notemessage = "SSLVPN服务器删除成功";
    }
}

sub make_node($){
    my $path = shift;
    
    if(!-e $path)
    {
        return 0;
    }
    
    $path .= $node_save{'node_name'};
    $path .= "/";
    `mkdir $path`;
    $path .= 'node-info';
    `touch $path`;
    writehash($path,\%node_save);
    return 1;
}

sub make_file(){
    if(!-e $update_dir)
    {
        `mkdir $update_dir`;
    }
    
    if(!-e $node_dir)
    {
        `mkdir $node_dir`;
    }
    if(!-e $setting_dir)
    {
        `mkdir $setting_dir`;
    }
    if(!-e $backup_file)
    {
        `touch $backup_file`;
        `echo >>$backup_file version=1.0`;
        `echo >>$backup_file client_type=psk`;
    }
}

sub read_first_node(){
    opendir(DIR,$node_dir);
    my @nodes = readdir(DIR);
    foreach my $one (@nodes)
    {
       if($one ne 'node-info' && $one ne 'node-info.old' && $one ne '.' && $one ne '..')
       {
          print "<option value='$one'>$one</option>";
       }
    }
}

sub display_one_node($$){
    my $path = shift;
    my $class = shift;
    opendir(DIR,$path);
    my @nodes = readdir(DIR);
    foreach my $one (@nodes)
    {
       if($one ne 'node-info' && $one ne 'node-info.old' && $one ne '.' && $one ne '..')
       {
         
         my $new_path = $path;
         $new_path .= "/";
         $new_path    .= $one;
         &display_node($class,$one,$new_path);
         my $new_class = $class + 1;
         &display_one_node($new_path,$new_class);
       }
    }
}

sub display_node($$$){
    $node_count++;
    my $class=shift;
    my $name=shift;
    my $path=shift;
    my $indent_px = 40 * $class;
    $indent_px .= 'px';
    printf <<EOF
    <tr class="odd">
       <td style='width:90%;text-indent:$indent_px;border-left:none;border-top:none;border-bottom:none;'>
EOF
;
       if($class ne 0)
       {
           #2013-7-23 屏蔽横线显示print "-----";
       }
    printf <<EOF
        <label style="cursor:pointer;text-decoration:underline;color:blue;" onclick='show_detail("$path");'>$name</label>
       </td>
       <td style="text-align:center;">
          <form method='post' action='$ENV{'SCRIPT_NAME'}'>
             <input type='hidden' name='ACTION' value='edit' />
             <input type='hidden' name='path' value='$path' />
             <input class='imagebutton' type='image' name='edit' src='/images/edit.png' alt='编辑$name服务器' title='编辑$name服务器'>
          </form>
          
          <form method='post' action='$ENV{'SCRIPT_NAME'}' onSubmit="return confirm('确定删除$name服务器?此服务器所有子服务器也会同时被删除！')">
             <input type='hidden' name='ACTION' value='remove' />
             <input type='hidden' name='path' value='$path' />
             <input class='imagebutton' type='image' name='remove' src='/images/delete.png' alt='删除$name服务器' title='删除$name服务器'>
          </form>
       </td>
    </tr>
EOF
;
}

sub make_node_settings(){
    if(-e $setting)
    {
       `rm $setting`;
       `touch $setting`;
    } else {
       `touch $setting`;
    }
    &make_backup_setting();
    &make_one_node($node_dir2,"");
    `$cmd_serverupdate`;
}

sub make_backup_setting(){
     my %tmp_backup_conf;
     my %tmp_auth_conf;
     readhash($backup_file,\%tmp_backup_conf);
     my $line0 = 'auth_type='.$tmp_backup_conf{'client_type'};
     my $line1 = 'backup_server_ip='.$tmp_backup_conf{'SERVER'};
     my $line2 = 'version='.$tmp_backup_conf{'version'};
     my $line3 = '==========';
     `echo >>$setting $line0`;
     `echo >>$setting $line1`;
     `echo >>$setting $line2`;
     `echo >>$setting $line3`;
}
sub make_one_node($$){
     my $path = shift;
     my $name = shift;
     opendir(DIR,$path);
     my @nodes = readdir(DIR);
     foreach my $one (@nodes)
     {
        if($one ne 'node-info' && $one ne 'node-info.old' && $one ne '.' && $one ne '..')
        {
           my $new_path = $path;
           $new_path .= "/";
           $new_path .= $one;
           my $file_path = $new_path;
           $file_path .= "/node-info";
           my %settings_conf;
           readhash($file_path,\%settings_conf);
           my $new_name = $name;
           #$new_name .= "/";父子服务器名字之间取消分隔符，若有必要可恢复，2013-7-9
           $new_name .= $settings_conf{'node_name'};
           my $e_ip = $settings_conf{'e-government-ip'};
           my $i_ip = $settings_conf{'internet-government-ip'};
           my $c_ip = $settings_conf{'ca-ip'};
           
           #e_ip为空则生成配置文件时设为0.0.0.0 --2013.08.14 wanlgin
           if($e_ip eq '')
           {
              $e_ip = "0.0.0.0";
           }
           
           #i_ip为空则生成配置文件时设为0.0.0.0
           if($i_ip eq '')
           {
              $i_ip = "0.0.0.0";
           }
           
           my $line = $new_name.','.$e_ip.','.$i_ip.','.$c_ip;
           my $line_decode = encode('gb2312',decode('utf8',$line));
           `echo >>$setting $line_decode`;
           make_one_node($new_path,$new_name);
        }
     }
}

sub read_update_conf(){
    if (-e $update_file) {
        readhash($update_file,\%update_settings);
    }
    if (-e $backup_file) {
        readhash($backup_file,\%backup_settings);
        $backup_settings{'SERVER'} =~ s/,/\n/g;
        $client_type_selected{'psk'} = '';
        $client_type_selected{'cert'} = '';
        $client_type_selected{'cert'} = 'selected' if ( $backup_settings{'client_type'} eq 'cert');
        $client_type_selected{'psk'} = 'selected' if ( $backup_settings{'client_type'} eq 'psk');        
    }
}

sub check_form(){
  printf <<EOF
  <script>    
  var object = {
       'form_name':'SAFE_DESKTOP_FORM',
       'option'   :{
                    'sslvpn_main':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|'
                             },
                    'sslvpn_bakcup':{
                               'type':'textarea',
                               'required':'1',
                               'check':'ip|domain|'                              
                             },
                    'version':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[0-9]+(\\.[0-9]+)?\$/'
                             },
                    'UP_FILE':{
                               'type':'file',
                               'required':'0'
                             }
                 }
         }

  var object2 = {
       'form_name':'USER_FORM',
       'option'   :{
                    'node_name':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                         var msg="";
                                                         var reg = /^[_0-9a-zA-Z\\u4e00-\\u9fa5]+\$/;
                                                         var firstfather = document.getElementById('first-father').options[document.getElementById('first-father').selectedIndex].value;
                                                         var secondfather = document.getElementById('second-father').options[document.getElementById('second-father').selectedIndex].value;
                                                         var thirdfather = document.getElementById('third-father').options[document.getElementById('third-father').selectedIndex].value;
                                                         var node_name = eve._getCURElementsByName("node_name","input","USER_FORM")[0].value;
                                                         if(node_name.length<2||node_name.length>20)
                                                         {
                                                            msg="SSLVPN服务器名称长度应大于2并小于20！";
                                                            return msg;
                                                         }
                                                         if(!reg.test(node_name))
                                                         {
                                                            msg="SSLVPN服务器名称中含有非法字符！";
                                                            return msg;
                                                         }
                                                         var ajax_value='name=';
                                                         if(firstfather!='')
                                                         {
                                                            ajax_value += '/';
                                                            ajax_value += firstfather;
                                                            if(secondfather!='')
                                                            {
                                                               ajax_value += '/';
                                                               ajax_value += secondfather;
                                                               if(thirdfather!='')
                                                               {
                                                                  ajax_value += '/';
                                                                  ajax_value += thirdfather;
                                                               }
                                                            }
                                                         }
                                                         var option = document.getElementById('ACTION').value;
                                                         var old_name;
                                                         var old_path;
                                                         
                                                         if(option=='edit_node')
                                                         {
                                                            old_name = document.getElementById('old_name').value;;
                                                            old_path = document.getElementById('path').value;
                                                            var path_splited = new Array();
                                                            path_splited = old_path.split('/');
                                                            var path='name=';
                                                            var count=0;
                                                            for(var i=0;i<path_splited.length-1;i++)
                                                            {
                                                               if(path_splited[i]!=''&&path_splited[i]!='var'&&path_splited[i]!='efw'&&path_splited[i]!='openvpn'&&path_splited[i]!='forns'&&path_splited[i]!='node_structure')
                                                               {
                                                                   path += "/";
                                                                 path += path_splited[i];
                                                               }
                                                            }
                                                            ajax_value = path;
                                                         }
                                                         if(!eve.users){
                                                            \$.ajax({
                                                                  type : "get",
                                                                  url : '/cgi-bin/get_sub_node.cgi',
                                                                  async : false,
                                                                  data : ajax_value,
                                                                  success : function(data){ 
                                                                    eve.users = data;                                                            
                                                                  }
                                                            });
                                                         }
                                                         var nodes = new Array();
                                                         nodes = eve.users.split(',');
                                                         for(var i=0;i<nodes.length;i++)
                                                         {
                                                             if(option=='save_node')
                                                             {  
                                                               if(nodes[i]!=''&&nodes[i]==node_name)
                                                               {
                                                                  msg = "当前位置已有同名SSLVPN服务器存在！";
                                                                  break;
                                                               }
                                                             }
                                                             if(option=='edit_node')
                                                             {
                                                               if(nodes[i]!=''&&nodes[i]==node_name&&nodes[i]!=old_name)
                                                               {
                                                                  msg = "当前位置已有同名SSLVPN服务器存在！";
                                                                  break;
                                                               }
                                                             }
                                                         }
                                                         eve.users = "";                                                         
                                                         return msg;
                                                     }
                             },
                    'e-government-ip':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|url|',
                               'ass_check':function(ip){
                                        var gip_value = ip._getCURElementsByName("e-government-ip","input","USER_FORM")[0].value;
                                        var iip_value = ip._getCURElementsByName("internet-government-ip","input","USER_FORM")[0].value;
                                        
                                        if (gip_value.length <= 0 && iip_value.length <= 0)
                                        {
                                            msg="电子政务网SSLVPN服务器地址、Internet网SSLVPN服务器地址必须填写一个！";
                                            return msg;
                                        }
                                    }
                             },
                    'internet-government-ip':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|url|',
                               'ass_check':function(ip){
                                        var gip_value = ip._getCURElementsByName("e-government-ip","input","USER_FORM")[0].value;
                                        var iip_value = ip._getCURElementsByName("internet-government-ip","input","USER_FORM")[0].value;
                                        
                                        if (gip_value.length <= 0 && iip_value.length <= 0)
                                        {
                                            msg="电子政务网SSLVPN服务器地址、Internet网SSLVPN服务器地址必须填写一个！";
                                            return msg;
                                        }
                                    }
                             },
                    'ca-ip':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|url|'
                             }
                 }
         }
  var check = new  ChinArk_forms();
  check._main(object);
  //check._get_form_obj_table("SAFE_DESKTOP_FORM");
  var check2 = new  ChinArk_forms();
  check2._main(object2);
  //check2._get_form_obj_table("USER_FORM");
  </script>
EOF
;
}

sub display_html(){
    printf <<EOF
<div class="containter-div">
     <span class="containter-div-header"><span style="display:block;float:left;margin-top:3px;"><img src='/images/applications-blue.png' />配置SSLVPN更新服务器</span><span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;">*表示必选项</span></span>
    <div class="containter-div-content">
<form enctype='multipart/form-data' name="SAFE_DESKTOP_FORM" method='post' action='$ENV{'SCRIPT_NAME'}'>
<table border='0' cellspacing="0" cellpadding="4">

  <tr  class="odd hidden">
    <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >SSLVPN主更新服务器*</td>
    <td >
      <input type='text' name='sslvpn_main' value='$update_settings{'SERVER'}' />
    </td>
  </tr>
  <tr  class="odd">
    <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >SSLVPN更新服务器地址*</td>
    <td>
      <textarea name='sslvpn_bakcup' style="width:154px;height:60px;">$backup_settings{'SERVER'}</textarea>
    </td>
  </tr>
  
  <tr  class="odd">
    <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >SSLVPN客户端登陆方式*</td>
    <td>
      <select id='client_type' name='client_type' style="width:156px">
        <option value='psk'  $client_type_selected{'psk'} >用户名/密码登陆</option>
        <option value='cert' $client_type_selected{'cert'}>证书登陆</option>
      </select>
    </td>
  </tr>
  
  <tr  class="odd">
    <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >SSLVPN客户端版本号*</td>
    <td>
      <input type='text' name='version' value='$backup_settings{'version'}' />
    </td>
  </tr>
  
  <tr  class="odd">
    <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >上传SSLVPN客户端安装包</td>
    <td>
      <input type='file' name='UP_FILE' />
    </td>
  </tr>

  <tr  class="table-footer">
    <td colspan="4">
      <input class='submitbutton net_button' type='submit' name='submit' value='保存' />
      <input type="hidden" name="ACTION" value="save_update" />
    </td>
  </tr>

</table>
</form>
</div>
</div>

EOF
;
}

sub display_add(){
    my $position_display;
    if($par{'ACTION'} eq 'edit')
    {
       my $path = $par{'path'};
       $path .= "/node-info";
       if(-e $path)
       {
          readhash($path,\%node_conf);
          openeditorbox(_('编辑SSLVPN服务器'), "","showeditor", "createrule", @errormessages);
          $position_display = "style='display:none;'";
       } else {
          openeditorbox(_('添加SSLVPN服务器'), "","", "createrule", @errormessages);
          $errormessage = "所选择的SSLVPN服务器已不存在！";
       }
    } else {
       openeditorbox(_('添加SSLVPN服务器'), "","", "createrule", @errormessages);
    }
    printf <<EOF
    </form>
    <form name="USER_FORM" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
    <table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
      <tbody>
       <tr class="odd" $position_display>
         <td class="add-div-type" style="width:200px;">SSLVPN服务器位置</td>
         <td>
            省 <select id='first-father' name='first-father' onchange="show_second_detail()">
                        <option value=''>不选择</option>
EOF
;
    &read_first_node();
    print <<EOF
                      </select>
            &nbsp;&nbsp;市 <select id='second-father' name='second-father' onchange="show_third_detail()">
                        <option value=''>不选择</option>
                      </select>
            &nbsp;&nbsp;县 <select id='third-father' name='third-father'>
                        <option value=''>不选择</option>
                      </select>
            &nbsp;&nbsp;(注意：服务器位置一旦设定无法更改！默认或都不选择则新服务器为省级服务器！)
         </td>
       </tr>
       <tr class="env">
         <td class="add-div-type" style="width:20%;">服务器名称*</td>
         <td>
            <input type="text" name='node_name' value="$node_conf{'node_name'}" />
         </td>
       </tr>
       <tr class="odd">
         <td class="add-div-type" >电子政务网SSLVPN服务器地址</td>
         <td>
            <input type="text" name='e-government-ip' value="$node_conf{'e-government-ip'}" />
         </td>
       </tr>
       <tr class="env">
         <td class="add-div-type" >Internet网SSLVPN服务器地址</td>
         <td>
            <input type="text" name='internet-government-ip' value="$node_conf{'internet-government-ip'}" />
         </td>
       </tr>
       <tr class="odd">
         <td class="add-div-type" >CA服务器地址*</td>
         <td>
            <input type="text" name='ca-ip' value="$node_conf{'ca-ip'}" />
         </td>
       </tr>
      </tbody>
     </table>
EOF
;
     if($par{'ACTION'} eq 'edit')
     {
        my $path = $par{'path'};
        my $old_name = $node_conf{'node_name'};
        printf <<EOF
        <input type="hidden" id="ACTION" name="ACTION" value="edit_node" />
        <input type="hidden" id="old_name" name="old_name" value="$old_name" />
        <input type="hidden" id="path" name="path" value="$path" />
EOF
;
     } else {
        print '<input type="hidden" id="ACTION" name="ACTION" value="save_node" />';
     }
EOF
;
    closeeditorbox("保存", "撤销", "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
}

sub display_structure(){
    printf <<EOF
    <table class="ruleslist" style="rules:none;" >
    <tr>
      <td class="boldbase">SSLVPN服务器</td>
      <td class="boldbase">活动/动作</td>
    </tr>
EOF
;
    $node_count = 0;
    &display_one_node($node_dir2,0);
    if(!$node_count)
    {
       no_tr(2,_('Current no content'));
    }
   printf <<EOF
    </table>
EOF
;
}
