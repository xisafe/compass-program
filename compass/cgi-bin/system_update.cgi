#!/usr/bin/perl
#DATE:2012-3-06
#author:zhouyuan
#MODIFY：殷其雷 2013/4/18

require '/var/efw/header.pl';

my $version_file_path = '/etc/release';
my $update_time = '/etc/sys_update_time';
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;

sub show_last()
{
	my $update_info = "";
	if(-e '/var/efw/sysupmsg/sysupmsg')
	{
		&openmybox('100%', 'left', _('上一次系统升级信息'));
		open(FILE,'/var/efw/sysupmsg/sysupmsg');
		foreach my $line(<FILE>)
		{
			$update_info .= $line."<br />";
		}
		close (FILE);
		print "<div style='margin:10px;'>".$update_info."</div>";
		&closebox();
	}
}

sub show_version()
{
    my $version;
	my $version_file;
	my $error = 0;
	if(!-e $version_file_path)
	{
	   $version = "系统版本文件不存在！";
	   $error = 1;
	} else {
	   unless(open (VERSIONFILE, "$version_file_path"))
	   {$version = "无法访问系统版本文件！";$error = 1;}
	   if($error) {
	   } else {
	      my $line = <VERSIONFILE>;
		  if($line =~ /\w*(\d+\.\d+.*)$/){
             $version = $1;
          } else {
             $version = "版本信息读取错误！";
             $error = 1;
          }
          #if($line =~ /CapSheaf.*(\d+\.\d+)$/){
		  #   $new_line = $line;
		  #	 $new_line =~s/CapSheaf//;
		  #   $version = $new_line;
	      #   #$version = $line;
	      #} else {
	      #   $version = "版本信息读取错误！";
	      #   $error = 1;
	      #}
		  close(VERSIONFILE);
	   }
	  
	}
	
	if($error)
	{
	   printf <<EOF
       <div id="pop-note-div">
         <span>错误：$version</span>
       </div>
EOF
;
	} else {
    open (TIMEFILE, "$update_time");
	my $time = <TIMEFILE>;
    close(TIMEFILE);
	printf <<EOF  
    <table class = "ruleslist" style="width:100%;">
	<tr>
	<td class="add-div-type" width="20%" align = "center">当 前 版 本：
	</td>
	<td>$version
	</td>
	</tr>
	<tr>
	<td class="add-div-type" align = "center">更 新 时 间：
	</td>
	<td>$time
	</td>
	</tr>
	</table>
EOF
;
    }
}

sub show_update()
{
	#读取系统信息
	if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
	my $url = "https://".$ENV{'SERVER_ADDR'}.":10443".'/cgi-bin/system_update_post.cgi';
	printf <<EOF
	<table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
    <tr class ='odd'><td width="20%" class='add-div-width' vlign='center' align='center' rowspan ='2'>选择本地文件升级系统：</td><td width = "80%"><div id="file-uploader"></div></td></tr>
	<!--<tr class ='odd'><td>升级完成后自动重启：<input type="checkbox" id="autoreboot"></td></tr>-->
	</table>
	<script>
		var uploader = new qq.FileUploader({
			element: document.getElementById('file-uploader'),
			allowedExtensions: ['bin'], 
			action:'$url',
			debug:true,
			onSubmit: function(id, fileName){},
			onProgress: function(id, fileName, loaded, total){},
			onComplete: function(id, fileName, responseJSON){
					var str = "<div id='pop-divs'></div>";
						str += "<div id='pop-text-div' style='padding:5px;min-height:170px;background-color:#FFF;border:3px solid #999;border-top:0px;position:absolute;z-index:6;left:2.5%;top:20%;text-align:center;width:60%;height:60px;margin-left:20%;padding:0;'>";
						str += "<div id='pop-text-div-header'><span style='display:block;float:left;padding:4px 5px;'><b>此次升级信息</b></span></div>";
						str += "<div id='data' style='height:130px;overflow-y:hidden;padding:5px;font-size:20px;font-weight:bold;'>正在获取本次升级信息，请稍后......<img src='/images/det_wait.gif' /></div>";
						str += "<div class='hidden_class' id='btn' style='width:100%;background-image:url(../images/con-header-bg.jpg);height:25px;'><b>是否确定此次系统升级？</b><input id='sure_update'  type='button' value='确定' />&nbsp;&nbsp;<input id='cancel_update'   type='button' value='取消' /></div>";
						str += "<div class='hidden_class' id='closebtn' style='width:100%;background-image:url(../images/con-header-bg.jpg);height:25px;display:none;'><input type='submit' class='net_button' onclick='hide();' value='关闭'></div>";
						str += "</div>";
					\$(str).appendTo("body");
				var filename = document.getElementById('filename').innerHTML;
				\$.get('/cgi-bin/system_update_get.cgi', {filename:filename}, function(data){
					if(data)
					{
						var temp = data.split("||");
						var str = "";
						str += "<br /><br />";
						for(var i =0;i<temp.length;i++)
						{
							str  += temp[i]+"<br />";
						}
						\$("#data").html(str);
						\$("#btn").css("display",'block');
					}else{
						\$("#data").text("升级信息获取失败！").css("font-size","20px").css("font-weight","bold").css("color","red");
						\$("#closebtn").css("display",'block');
					}
				});

			\$('#sure_update').click(function(){
				
                var auto_reboot = 0;
				if(auto_reboot==1)
				{  
				   \$("#data").html("系统正在执行升级过程，升级完成后自动重启，请耐心等待！<img src='/images/det_wait.gif' />");
				   \$.get('/cgi-bin/system_update_get.cgi', {cmd_name:'UPDATE',reboot:'yes'}, function(data){
						\$("#btn").css("display",'none');
						if(data=="升级成功!")
						{
						  \$("#data").text("系统升级完毕,正在重启系统,请稍后访问本系统！").css("font-size","20px").css("font-weight","bold");
						  \$("#closebtn").css("display",'block');
						  \$.get('/cgi-bin/update_reboot.cgi', {reboot:yes}, function(data){});
						  //parent.parent.window.document.location.href = "https://"+location.host;
						}
						if(data=="已经最新!")
                        {
						  \$("#data").text("错误，上传的升级文件版本需大于当前系统版本，若需升级请下载最新升级包!").css("font-size","20px").css("font-weight","bold").css("color","red");
						  \$("#closebtn").css("display",'block');
                        }
						else {
						  \$("#data").text("升级失败!").css("font-size","20px").css("font-weight","bold").css("color","red");
						  \$("#closebtn").css("display",'block');
						}
				   });
				} else {
				   \$("#data").html("系统正在执行升级过程，请耐心等待！<img src='/images/det_wait.gif' />");
				   \$.get('/cgi-bin/system_update_get.cgi', {cmd_name:'UPDATE',reboot:'no'}, function(data){
						\$("#btn").css("display",'none');
						if(data=="升级成功!")
						{
						  \$("#data").text("系统升级完毕，请手动重启系统！").css("font-size","20px").css("font-weight","bold");
						  \$("#closebtn").css("display",'block');
						  //parent.parent.window.document.location.href = "https://"+location.host;
						} else {
                          if(data=="已经最新!")
                          {
						    \$("#data").text("错误，上传的升级文件版本与当前系统版本一致，若需升级请下载最新升级包!").css("font-size","20px").css("font-weight","bold").css("color","red");
							\$("#closebtn").css("display",'block');
                          }						
						  else {
						    \$("#data").text("升级失败!").css("font-size","20px").css("font-weight","bold").css("color","red");
							\$("#closebtn").css("display",'block');
						  }
						}
				   });
				}
				
			});
		
			\$('#cancel_update').click(function(){
				hide();
	});
			},
			onCancel: function(id, fileName){},
			showMessage: function(message){ alert(message); }
		});
	function hide()
	{
		\$("#pop-divs").remove();
		\$("#pop-text-div").remove();
	}
	
	</script>
	<table class="table-footer" width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
    <tr><td width="70%"></td><td width="30%">请到<a onclick='jump("http://%s")' style='cursor:pointer' color='blue'>%s</a>下载最新升级包！</td></tr>
	</table>
EOF
	,$system_settings{'COMPANY_WEBSITE'}
	,$system_settings{'COMPANY_WEBSITE'}
;
}

sub openmybox
{
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

showhttpheaders();
my $extraheader  = '<script language="JavaScript" src="/include/fileuploader.js"></script>';
   $extraheader .= "<style type='text/css'>\@import url(/include/fileuploader.css);</style>";
   $extraheader .= '<script type="text/javascript">
   function jump(des){
       window.open(des);
   }
</script>';
   
&openpage(_('系统升级'), 1, $extraheader);
&show_last();
&openmybox('100%', 'left', _('离线升级'));
&show_update();
if(!-e "/var/efw/sysupmsg"){
	system("mkdir /var/efw/sysupmsg")
}
system("rm /var/systemupdate/*");
&closebox();
&openmybox('100%', 'left', _('版本状态'));
&show_version();
&closebox();
&closepage();
