#!/usr/bin/perl
#DATE:2013-6-5
#author:殷其雷

require '/var/efw/header.pl';
use CGI::Carp qw (fatalsToBrowser);
use CGI qw(:standard);

my $cgi= new CGI; 
my %par;
getcgihash(\%par);
my $action = $par{'ACTION'};

my $errormessage;
my $notemessage;
my $serial_num_file = "/var/openvpn/license/serialNumber";
# my $serial_num_path = "/usr/local/bin/license/getSerialnumber";
my $serial_num_path = "cat /etc/license/identify";
my $max_user_path="/usr/local/bin/license/getMaxusers";
my $check_license="/usr/local/bin/license/checkLicense";
my $license_file="/var/openvpn/license/license.enc";
my $license_file_old="/var/openvpn/license/license.old";
my $current_users_num   = '/usr/bin/openvpn-sudo-user longlist | wc -l';
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;

&do_action();

showhttpheaders();
my $extraheader .= "<style type='text/css'>
.add-help_p{
height:12px;
text-indent:30px;
font-weight:bold;
font-size:12px;
padding:0px;
}
</style>";
&openpage(_('授权管理'), 1, $extraheader);
openbigbox($errormessage,"", $notemessage);
&show_help();
&show_serial_num();
&show_activate();
&show_info();
closebigbox();
&closepage();

sub do_action(){
    if($action eq 'upload')
	{
	  &uploads();
	}
}


sub uploads(){
	my $file_length = 0;
	my $upload_filehandle = $cgi->upload('active_file');
	my $upload_filename = $upload_filehandle;
	my @splited_filenames = split(/\./, $upload_filename);
	foreach my $splited_filename (@splited_filenames)
	{
	   $file_length++;
	}
	if($file_length == 0)
	{
	   $errormessage = '请选择一个激活文件再上传！';
	} else {
	   $file_length--;
	   my $filename = "/var/openvpn/license/license.new";
	   open ( UPLOADFILE, ">$filename" ) or die "$!";
	   binmode UPLOADFILE;
	   while ( <$upload_filehandle> )
 	   {
		      print UPLOADFILE;
	   }
	   close UPLOADFILE;
	   my $result = `$check_license $filename`;
       chomp($result);
	   if($result eq 0)
	   {
	      `mv $license_file $license_file_old`;
		  `mv $filename $license_file`;
	      $notemessage = "激活成功！";
	   } else {
	      `rm $filename`;
	      $errormessage = "激活文件无效，激活失败！";
	   }
	}
}

sub show_help() {
	if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    openmybox('100%', 'left', _('提示'));
    printf <<EOF
	<table class="odd" style="width:100%;height:120px;fame:void;padding-top:5px;">
	  <tr style="height:15px;">
	   <td style="border:0px;padding:0px;"><p class="add-help_p" style="margin-top:3px;">激活帮助：</p></td>
	  </tr>
	  <tr style="height:12px;">
	   <td style="border:0px;padding:0px;"><p class="add-help_p">1.将系统序列号，最大SSL VPN用户数，通过电话/Email告知 "%s";</p></td>
	  </tr>
	  <tr style="height:12px;">
	   <td style="border:0px;padding:0px;"><p class="add-help_p">2.获得由 "%s" 提供的激活文件;</p></td>
	  </tr>
	  <tr style="height:12px;">
	   <td style="border:0px;padding:0px;"><p class="add-help_p">3.在下面选择激活文件，点击 "激活" 按钮即可完成激活。</p></td>
	  </tr>
	</table>
	<br />
EOF
	,$system_settings{'COMPANY_FULL_NAME'}
	,$system_settings{'COMPANY_FULL_NAME'}
;
    closebox();
}

sub show_serial_num() {
    openmybox('100%', 'left', _('序列号'));
	if(!(-e $serial_num_file))
	{
	  `sudo $serial_num_path > $serial_num_file`;
	}
	my $serial_num = `cat /etc/license/identify`;
	printf <<EOF
    <table width="100%" cellpadding="0" cellspacing="0">
	 <tr class="odd" style="height:30px;">
	 <td class="add-div-type" style="width:180px;font-size:15px;">本系统序列号：</td>
	 <td style="color:red;font-size:15px;font-weight:bold;">$serial_num
	 </td>
	 </tr>
	 </table>
EOF
;
	closebox();
}

sub show_activate() {
    openmybox('100%', 'left', _('激活'));
	printf <<EOF
     <table width="100%" cellpadding="0" cellspacing="0">
	 <tr class="odd">
	 <td class="add-div-type" style="width:180px;">选择激活文件</td>
	 <td>
	  <form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
	   <input type="file" name="active_file" style="width:200px" />
	   <input type="submit" name="submit" value="激活" style="width:40px" >
	   <input type='hidden' name='ACTION' value='upload'>
	  </form>
	 </td>
	 </tr>
	 </table>
EOF
;
	closebox();
}

sub show_info() {
    openmybox('100%', 'left', _('授权信息'));
	my $activate="未激活";
	my $max_users;
	my $current_users;
	my $status_color = "red";
	if(-e $license_file)
	{
	  $activate="已激活";
	  $status_color = "green";
	  $max_users=`$max_user_path`;
	  $current_users = `$current_users_num`;
	}
	
	printf <<EOF
	<table width="100%" cellpadding="0" cellspacing="0">
	 <tr class="odd" style="height:28px;">
	 <td class="add-div-type" style="width:180px;">当前状态：</td>
	 <td style="color:$status_color;">$activate
	 </td>
	 </tr>
	 <tr class="odd" style="height:28px;">
	 <td class="add-div-type">支持的最大用户数：</td>
	 <td>$max_users
	 </td>
	 </tr>
	 <tr class="odd" style="height:28px;">
	 <td class="add-div-type">当前系统已添加的用户数：</td>
	 <td>$current_users
	 </td>
	 </tr>
	 </table>
EOF
;
	closebox();
}

sub openmybox{
    $width = $_[0];
    $align = $_[1];
    $caption = $_[2];
    $id = $_[3];
    
    if($id ne '') {
        $id = "id=\"$id\"";
    }
    else {
        $id="";
    }
    
    
    printf <<EOF
<div class="containter-div">
EOF
    ;
    if ($caption) {
        printf <<EOF
     <span class="containter-div-header"><span style="display:block;float:left;margin-top:3px;"><img src='/images/applications-blue.png' />$caption</span><span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;"></span></span>
EOF
;
    }
    else {
        	 printf <<EOF
        <span class="containter-div-header"><img src='/images/applications-blue.png' />&nbsp;</span>
EOF
;
    }
    
    printf <<EOF
	<div class="containter-div-content">
EOF
    ;
}
