#!/usr/bin/perl
require '/var/efw/header.pl';           
my $setting_default = "/var/efw/openvpn/forns/safedesktop/default/settings";
my $setting_file = "/var/efw/openvpn/forns/safedesktop/settings";
my $setting_dir = "/var/efw/openvpn/forns/safedesktop/";
my $default_dir = "/var/efw/openvpn/forns/safedesktop/default/";
my $cmd = '';
my %par;
my %save;
my %settings;
my $errormessage='';
my $warnmessage='';
my $notemessage='';
&showhttpheaders();
&getcgihash(\%par);
&make_file();
&save();
&read_conf();
&openpage(_('安全桌面'), 1, '');
&openbigbox($errormessage, $warnmessage, $notemessage);
&display_html();
&closebigbox();
&closepage();
&check_form();

sub save(){
    if($par{'ACTION'} eq "save"){ 
        $save{'COPY_TO_MOBILE'} = $par{'COPY_TO_MOBILE'};
		my $count = "not";
		$save{'BLACK_FILES'} = "";
		foreach my $one (split(/\r\n/,$par{'BLACK_FILES'}))
		{
		   if($count eq "add")
		   {
		      $save{'BLACK_FILES'} .=",";
		   }
		   $count = "add";
		   chomp($one);
		   $save{'BLACK_FILES'} .= $one;
		}
	    
		if(!-e $setting_file){
	       `touch $setting_file`;
 	    }
        writehash($setting_file,\%save);
        #system($cmd);
        $notemessage = "安全桌面配置成功！";
    }
}

sub make_file(){
    if(!-e $setting_dir)
    {
	    `mkdir $setting_dir`;
	}
	if(!-e $default_dir)
	{
		`mkdir $default_dir`;
	}
    if(!-e $setting_default){
	    `touch $setting_default`;
        my %default_settings;
		$default_settings{'COPY_TO_MOBILE'} = 'on';
		$default_settings{'BLACK_FILES'} = '.doc,.txt';
		writehash($setting_default,\%default_settings);
    }
}

sub read_conf(){
    if (-e $setting_file) {
        readhash($setting_file,\%settings);
    } else {
	    readhash($setting_default,\%settings);
	}
	
    if($settings{'COPY_TO_MOBILE'} eq 'on'){
       $checked = "checked='checked'";
    }
	
	$settings{'BLACK_FILES'}=~s/,/\n/g;
}

sub check_form()
{
  printf <<EOF
  <script>    
  var object = {
       'form_name':'SAFE_DESKTOP_FORM',
       'option'   :{
                    'BLACK_FILES':{
                               'type':'textarea',
                               'required':'0',
                               'check':'other|',
                               'other_reg':'/^[\\.][0-9a-zA-Z]{1,10}\$/',
							   'ass_check':function(eve){
							                              var msg = "";
														  var str = eve._getCURElementsByName("BLACK_FILES","textarea","SAFE_DESKTOP_FORM")[0].value;
														  var lines = new Array();
                                                          lines = str.split("\\n");
														  lines.sort();
														  for(var i=0;i<lines.length;i++)
														  {
														     if(lines[i+1]!=""&&lines[i]==lines[i+1])
															 {
															    msg="请不要输入重复的文件类型！";
																break;
															 }
														  }
														  return msg;
							                            }
                             },
                 }
         }
  var check = new  ChinArk_forms();
  check._main(object);
  //check._get_form_obj_table("SAFE_DESKTOP_FORM");
  </script>
EOF
;
}

sub display_html(){
    printf <<EOF
<div class="containter-div">
     <span class="containter-div-header"><span style="display:block;float:left;margin-top:3px;"><img src='/images/applications-blue.png' />设置安全桌面</span><span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;">*表示必选项</span></span>
    <div class="containter-div-content">
<form enctype='multipart/form-data' name="SAFE_DESKTOP_FORM" method='post' action='$ENV{'SCRIPT_NAME'}'>
<table border='0' cellspacing="0" cellpadding="4">

  <tr  class="odd">
    <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >授权读写空间</td>
    <td >
      <input type='checkbox' name='COPY_TO_MOBILE' $checked />
	  &nbsp;是否允许拷贝到移动设备
    </td>
  </tr>
  <tr  class="odd" style="height:50px;">
    <td class="add-div-type" style="text-indent:15px;border-right:1px solid #999;width:200px;font-weight:bold;" >文件黑名单</td>
    <td>
      <textarea name='BLACK_FILES' style="width:150px;height:100px;">$settings{'BLACK_FILES'}</textarea>
	  <label style="vertical-align:top;font-weight:normal">(一行输入一种文件后缀名)</label>
    </td>
  </tr>

  <tr  class="table-footer">
    <td colspan="4">
      <input class='submitbutton net_button' type='submit' name='submit' value='保存' />
      <input type="hidden" name="ACTION" value="save" />
    </td>
  </tr>

</table>
</form>
</div>
</div>

EOF
;
}
