#!/usr/bin/perl
#
# openvpn CGI for Endian Firewall
#

#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
#        |         Endian GmbH/Srl                                                     |
#        |         Bergweg 41 Via Monte                                                |
#        |         39057 Eppan/Appiano                                                 |
#        |         ITALIEN/ITALIA                                                      |
#        |         info@endian.it                                                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        | http://www.fsf.org/                                                         |
#        +-----------------------------------------------------------------------------+
#


# -------------------------------------------------------------
# some definitions
# -------------------------------------------------------------

require 'ifacetools.pl';
require '/var/efw/header.pl';
require 'description_lib.pl';
require './endianinc.pl';
use Net::IPv4Addr qw (:all);

my $restart  = '/usr/local/bin/restartopenvpn';
my $passwd   = '/usr/bin/openvpn-sudo-user';
my $etherconf = "/var/efw/ethernet/settings";
my $openvpnconf = "/var/efw/openvpn/settings";
#auth:wangzhengxia
#date:2013.01.29
#dis:max ssl vpn users file
my $maxsslvpnusers = "/var/efw/openvpn/maxsslvpnusers";
#auth:wangzhengxia
#date:2013.01.29
#dis:max ssl vpn users file


my $dirtyfile  = '/var/efw/openvpn/dirtyuserconfig';

my $name        = _('资源配置');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked');
my $self = $ENV{SCRIPT_NAME};

my %par;
my $action = '';
my $username = '';
my $errormessage = '';
my $err = 1;
my $config = 0;
my $CACERT_FILE = '/var/efw/openvpn/cacert.pem';
my @errormessages;

my $resource_folder = "/var/efw/openvpn/resources/";
my $web_resource_file = "/var/efw/openvpn/resources/web_resources";
my $other_resource_file = "/var/efw/openvpn/resources/other_resources";
my $description_folder = "";
my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my @web_resources;
my @other_resources;

sub list_resources() {

printf <<EOF
<table border="0" class="ruleslist" cellspacing="0" cellpadding="4" width="100%">
  <tr>
    <td width="40px;" class="boldbase" style="text-indent:0px;"><b>%s</b></td>
    <td width="200px;" class="boldbase" style="text-indent:0px;"><b>%s</b></td>
    <td width="100px;" class="boldbase" style="text-indent:0px;"><b>%s</b></td>
	<td width="250px;" class="boldbase" style="text-indent:0px;"><b>%s</b></td>
    <td class="boldbase" style="text-indent:0px;"><b>%s</b></td>
    <td width="150px;" class="boldbase"><b>%s</b></td>
  </tr>
EOF
, _('序号')
, _('资源名称')
, _('访问方式')
, _('地址')
, _('描述')
, _('动作')
;

EOF
;
    my $web_length = scalar(@web_resources);
	my $other_length = scalar(@other_resources);
	my @resource_splited;
    my $count = 0;
	if(($web_length ne 0) || ($other_length ne 0))
	{
	   if($web_length ne 0){
	      foreach my $resource (@web_resources){
		     $count++;
		     @resource_splited = split(/,/,$resource);
			 my $one_resource_name = $resource_splited[0];
			 my $one_href = $resource_splited[1];
			 my $enabled = $resource_splited[2];
			 chomp($enabled);
			 if($count%2 == 0)
		 	 {
		    	 print '<tr class="odd" style="height:25px;">';
		 	 } else {
		    	 print '<tr class="env" style="height:25px;">';
		 	 }
			 
			 printf <<EOF
                    <td>$count</td>
                    <td id="name$count" style="size:12px;font-family:宋体;">$one_resource_name</td>
                    <td id="type$count" style="size:12px;font-family:宋体;">WEB资源</td>
					<td id="href$count" style="size:12px;font-family:宋体;">$one_href</td>
                    <td>
					  <table width="100%" frame="void" border="1" cellspacing="0" cellpadding="0">
				      <tr>
					    <td style="border:0;text-indent:0px;"><p id="des$count" style="size:12px;font-family:宋体;">读取中描述信息中，请稍候......</p></td>
						<td width="40px;" style="border:0;">
						      <a style="size:12px;font-family:宋体;cursor:pointer;text-decoration:underline;" onclick="detail(document.getElementById('rename$count').value)">详细</a>
						</td>
					  </tr>
					</table>
					</td>
					<td>
					   <form method='post' action='$self' style="float:left;margin-left:5px;">
    					<input type="hidden" name="ACTION" value="onoff">
    					<input type="hidden" name="status" value="$enabled">
						<input type="hidden" name="resource_name" value="$one_resource_name">
						<input type="hidden" name="type" value="web">
EOF
;                       if($enabled eq 'on') 
    					{
						   printf <<EOF 
						    <input class="imagebutton" type="image" name="submit" src="$ENABLED_PNG" alt="" />
EOF
;
						} else {
						   printf <<EOF
						    <input class="imagebutton" type="image" name="submit" src="$DISABLED_PNG" alt="" />
EOF
;
						}
			printf <<EOF
					   </form>
                        <form method='post' action='$self' style="float:left;margin-left:5px;">
                            <input class='imagebutton' type='image' name='edit' src='/images/edit.png' alt='edit' title='edit'>
                            <input type="hidden" name="ACTION" value="edit">
                            <input type="hidden" name="resource_name" value="$one_resource_name">
							<input id="rename$count" type="hidden" value="$one_resource_name">
							<input type="hidden" name="access_type" value="web">
							<input type="hidden" name="href" value="$one_href">
							<input type="hidden" name="status" value="$enabled">
                        </form>
                        <form method='post' action='$self' onSubmit="return confirm('确定删除此资源?')" style="float:left;margin-left:5px;">
                            <input class='imagebutton' type='image' name='remove' src='/images/delete.png' alt='remove' title='remove'>
                            <input type="hidden" name="ACTION" value="delete">
                            <input type="hidden" name="resource_name" value="$one_resource_name">
                        </form>
                    </td>
				  </tr>	
EOF
;
		  }
		  
	   }
	   if($other_length ne 0)
	   {
	      foreach my $line (@other_resources){
		     $count++;
			 my @line_splited = split(/,/,$line);
			 my $resource = $line_splited[0];
			 my $enabled = $line_splited[1];
			 chomp($enabled);
			 my $one_resource_name = $resource;
			 
			 if($count%2 == 0)
		 	 {
		    	 print '<tr class="odd" style="height:25px;">';
		 	 } else {
		    	 print '<tr class="env" style="height:25px;">';
		 	 }
			 
			 printf <<EOF
                    <td>$count</td>
                    <td id="name$count" style="size:12px;font-family:宋体;">$one_resource_name</td>
                    <td id="type$count" style="size:12px;font-family:宋体;">其他资源</td>
					<td id="href$count" style="size:12px;font-family:宋体;"></td>
                    <td>
					<table width="100%" frame="void" border="1" cellspacing="0" cellpadding="0">
				      <tr>
					    <td style="border:0;text-indent:0px;"><p id="des$count" style="size:12px;font-family:宋体;">读取中描述信息中，请稍候......</p></td>
						<td width="40px;" style="border:0;">
						      <a style="size:12px;font-family:宋体;cursor:pointer;text-decoration:underline;" onclick="detail(document.getElementById('rename$count').value)">详细</a>
						</td>
					  </tr>
					</table>
					</td>
					<td>
					   <form method='post' action='$self' style="float:left;margin-left:5px;">
    					<input type="hidden" name="ACTION" value="onoff">
    					<input type="hidden" name="status" value="$enabled">
						<input type="hidden" name="resource_name" value="$one_resource_name">
						<input type="hidden" name="type" value="other">
EOF
;                       if($enabled eq 'on') 
    					{
						   printf <<EOF 
						    <input class="imagebutton" type="image" name="submit" src="$ENABLED_PNG" alt="" />
EOF
;
						} else {
						   printf <<EOF
						    <input class="imagebutton" type="image" name="submit" src="$DISABLED_PNG" alt="" />
EOF
;
						}
			printf <<EOF
					   </form>
                        <form method='post' action='$self' style="float:left;margin-left:5px;">
                            <input class='imagebutton' type='image' name='edit' src='/images/edit.png' alt='edit' title='edit'>
                            <input type="hidden" name="ACTION" value="edit">
                            <input type="hidden" name="resource_name" value="$one_resource_name">
							<input id="rename$count" type="hidden" value="$one_resource_name">
							<input type="hidden" name="access_type" value="other">
							<input type="hidden" name="href" value="">
							<input type="hidden" name="status" value="$enabled">
                        </form>
                        <form method='post' action='$self' onSubmit="return confirm('确定删除此资源?')" style="float:left;margin-left:5px;">
                            <input class='imagebutton' type='image' name='remove' src='/images/delete.png' alt='remove' title='remove'>
                            <input type="hidden" name="ACTION" value="delete">
                            <input type="hidden" name="resource_name" value="$one_resource_name">
                        </form>
                    </td>
				  </tr>	
EOF
;
		  }
	   }
   }else{
	no_tr(6,_('Current no content'));
}


printf <<END


</table>
END
;

if($other_length >0 || $web_length >0)
{
printf <<EOF
<table cellpadding="0" cellspacing="0" class="list-legend">
  <tr>
    <td class="boldbase">
      <b>%s</b>
    <img src="$ENABLED_PNG" alt="%s" />
    %s
    <img src='$DISABLED_PNG' alt="%s" />
    %s
    <img src="$EDIT_PNG" alt="%s" />
    %s
    <img src="$DELETE_PNG" alt="%s" />
    %s</td>
  </tr>
</table>
<br />
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

    #closebox();

}

sub show_set() {
    if ($action eq 'edit') {
      openeditorbox(_('修改资源配置'), "","showeditor", "createrule", @errormessages);
	  my $origin_name = $par{'resource_name'};
	  my $origin_type = $par{'access_type'};
	  my $href = $par{'href'};
	  my $enabled = $par{'status'};
	  my $se1="";
	  my $se2="";
	  my $display = "none";
	  my $enable ="";
	  if($origin_type eq "web")
	  {
         $se1 = "selected";
         $display = "table-row";
	  } else {
	     $se2 = "selected";	
	  }
	  if($enabled eq 'on')
	  {
	     $enable = "checked";
	  }
	  printf <<EOF
	  </form>
	  <form name="USER_FORM" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}' >
	  <table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
	 <tbody>
	   <tr class="env" style="height:25px;">
	     <td class="add-div-type need_help" style="width:15%;">资源名称*</td>
	     <td style="vertical-align:middle;font-size:12px;padding:0px;height:25px;text-indent:10px;">
		 <p style="font-family:宋体;">
		   <input style="height:14px;width:250px;vertical-align:middle;padding:0px;margin:0px;" type="text" id="modify_name"  MaxLength="50" name="modify_name" value="$origin_name" onblur="">
		   <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">(1-50个字符)</label>
		 </p>
		 </td>
	   </tr>
	   <tr class="odd" style="height:25px;">
	     <td class="add-div-type need_help" style="width:15%;">访问方式*</td>
	     <td style="vertical-align:middle;">
	        <select id="modify_type" name="modify_type" onchange="change();">
			  <option  value="web" $se1>WEB访问</option>
			  <option  value="other" $se2>其他访问</option>
			</select>
			<label style="display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">(web访问方式指可以通过浏览器直接访问的资源，包括web站点和可web化的资源，例如ftp;其他访问方式，指除web访问方式涵盖的资源之外的其他所有资源)</label>
		 </td>
	   </tr>
	   <tr class="env" id="hreftr" style="display:$display;">
		  <td class="add-div-type need_help" >地址*</td>
	      <td>
		     <input type="text" id="modify_href"  MaxLength="100" name="modify_href" style="width:250px;" value="$href" /> 
		     (1-100个字符，例如:http://www.baidu.com, ftp://192.168.1.1)
		  </td>
	   </tr>
	   <tr class="odd" style="height:150px;" >
	     <td class="add-div-type need_help" style="width:15%;">描述*</td>
	     <td >
		 <textarea id="modify_description" style="height:150px;width:400px;" name="modify_description"></textarea>
		 </td>
	   </tr>
	   <tr class="env" style="height:25px;">
	     <td class="add-div-type need_help" style="width:15%;">是否启用</td>
	     <td style="vertical-align:middle;text-indent:10px;height:25px;padding:0px;">
	        <p>
			  <input type="checkbox" id="modify_enable" name="modify_enable" style="vertical-align:middle;padding:0px;margin:0px;" $enable>
			  <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">启用</label>
			</p>
			<input type="hidden" name="ACTION" value="modify">
			<input type="hidden" id="origin_name"  name="origin_name" value="$origin_name" >
			<input type="hidden" id="origin_type"  name="origin_type" value="$origin_type" >
		 </td>
	   </tr>
	   <script type="text/javascript">
	     var des_file_name = document.getElementById('origin_name').value;
	     \$.get("description_html.cgi", {resource_name:des_file_name}, function(data){
		       if(data=="描述信息不存在！")
			   {
			      document.getElementById('modify_description').value = "";
			   } else {
			      document.getElementById('modify_description').value = data;
			   }
		 });
	   </script>
	 </tbody>
	</table>
EOF
;     closeeditorbox("修改资源", "撤销", "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
    } 
    else {
  	  openeditorbox(_('添加新资源'), "","", "createrule", @errormessages);
	  printf <<EOF
	  </form>
	  <form name="USER_FORM" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
	  <table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
	  <tbody>
	   <tr class="env" style="height:25px;">
	     <td class="add-div-type need_help" style="width:15%;">资源名称*</td>
	     <td style="vertical-align:middle;font-size:12px;padding:0px;height:25px;text-indent:10px;">
		 <p style="font-family:宋体;">
		   <input style="height:14px;width:250px;vertical-align:middle;padding:0px;margin:0px;" type="text" MaxLength="50" id="new_name" name="new_name" value="" onblur="">
		   <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">(1-50个字符)</label>
		 </p>
		 </td>
	   </tr>
	   <tr class="odd" style="height:25px;">
	     <td class="add-div-type need_help" style="width:15%;">访问方式*</td>
	     <td style="vertical-align:middle;">
	        <select id="new_type" name="new_type" onchange="change2();">
			  <option value="web"  selected="selected">WEB访问</option>
			  <option value="other" >其他访问</option>
			</select>
			<label style="display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">(web访问方式指可以通过浏览器直接访问的资源，包括web站点和可web化的资源，例如ftp;其他访问方式，指除web访问方式涵盖的资源之外的其他所有资源)</label>
		 </td>
	   </tr>
	   <tr class="env" id="hreftr" style="height:25px;">
		 <td class="add-div-type need_help" style="width:15%;">地址*</td>
	     <td>
		    <input type="text" MaxLength="100" id="new_href"  name="new_href" style="width:250px;"  /> 
		   (1-100个字符,例如:http://www.baidu.com, ftp://192.168.1.1)
		 </td>
	   </tr>
       <tr class="odd" style="height:150px;border-top:1px solid gray;">
	     <td class="add-div-type need_help" style="width:15%;">描述*</td>
	     <td >
		 <textarea id="new_description" style="height:150px;width:400px;" name="new_description" ></textarea>
		 </td>
	   </tr>
	   <tr class="env" style="height:25px;">
	     <td class="add-div-type need_help" style="width:15%;">是否启用</td>
	     <td style="vertical-align:middle;text-indent:10px;height:25px;padding:0px;">
	        <p>
			<input type="checkbox" id="new_enable" name="new_enable" style="vertical-align:middle;padding:0px;margin:0px;" checked>
			<label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">启用</label>
			</p>
			<input type="hidden" name="ACTION" value="add">
		 </td>
	   </tr>	   
	 </tbody>
	</table>
EOF
;
    closeeditorbox("创建资源", "撤销", "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
    }
}

sub show_cover() {
    printf <<EOF
	<div id="cover_div" style="width:100%;">
	</div>
	<div id="protocol_div" style="width:900px;">
	  <table width="100%" class="ruleslist" style="border:3px;">
	  <tr style="height:30px;" class="env">
	       <td style="width:150px;font-weight:bold;" >资源名称</td><td><a id="title_name" style="color:black"></a></td>
	  </tr>
	  <tr class="env" style="height:300px;">
	       <td style="font-weight:bold;">资源描述</td><td><div id="detail_display_div" class="odd" sytle="width:100%;"><textarea id="detail_display_p" readOnly=true;>描述信息读取中，请稍候.......</textarea></div></td>
	  </tr>
	  <tr style="height:30px;" class="table-footer">
	       <td colspan="2"><div width="100%" style="text-align:center"><input type="submit" class="net_button" value="关闭窗口" onclick="remove_cover();" /><input type="submit" id="confirm_button2" class="net_button" value="关闭窗口" onclick="remove_cover();" style="display:none"/></div></td>
	  </tr>
	  </table>
	</div>
	<div id="detail_div" style="width:350px;">
	  <img id="close_button" src="../images/close.png" onclick="remove_cover();" onmouseover="this.src='../images/close_hover.png';" onmouseout="this.src='../images/close.png';" />
	  <div>
	  <table border="0" cellspacing="0" cellpadding="0">
	   <tr class="img_tr">
	     <td id="img" class="img_td">
		   <img src="../images/warning.png" />
		   <!--<img src="../images/Emoticon.png" />-->
		 </td>
		 <td id="information_td">
		 </td>
	   </tr>
	   <tr class="bottom_button">
	     <td colspan=2>
		   <input id="confirm_button" class="confirm" type="submit" value="确 认"  onclick="remove_cover();" />
		   <!--&nbsp;&nbsp;-->
		   <input id="cancel_button" style="display:none" class="cancel" type="submit" value="取 消"  onclick="remove_cover();" />
		 </td>
	   </tr>
	  </table>
	  </div>
	</div>
	<!--计算弹出框位置js，不能放到前面去！-->
	<script language="javascript" type="text/javascript" src="/include/cover.js"></script>
EOF
;
}

sub show_script() {
    printf <<EOF
	<script language="javascript" type="text/javascript" src="/include/resourceset.js"></script>
EOF
;
}

sub displaymymenu(){
    printf <<EOF
  <ul class="tab-div">
	<li class="active">
	  <a href="resourceset.cgi">资源配置</a>
	</li>
  </ul>
EOF
;
}
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;
my $system_title;

sub read_config(){
	if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
	$system_title = $system_settings{'SYSTEM_TITLE'};
}
sub openmypage {
    my $title = shift;
    my $boh = shift;
    my $extrahead = shift;
    &readhash("${swroot}/main/settings", \%settings);
	&read_config();
	&write_login_time();
    if(!($nomenu == 1)) {
        &genmenu();
    }
    my $h2 = gettitle($menu);
    my $helpuri = get_helpuri($menu);

    $title = $system_title." -". $title;
	$gui_set = $settings{'LANGUAGE'};
    if ($settings{'WINDOWWITHHOSTNAME'} eq 'on') {
        $title = $system_title." -". $title;
    }

	#####周圆 2011-09-21用于添加头部帮助悬浮层显示消失功能######
	my $help_file = "/var/efw/help/setting";
	&readhash($help_file,\%help_hash);
	############################################################
	
	
    printf <<END
<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <title>$title</title>
         <link rel="shortcut icon" href="/images/shortcut.ico" />
		<style type="text/css">\@import url(/include/main.css);</style>
        <style type="text/css">\@import url(/include/style.css);</style>
        <style type="text/css">\@import url(/include/menu.css);</style>
        <style type="text/css">\@import url(/include/content.css);</style>
        <style type="text/css">\@import url(/include/folding.css);</style>
		<style type="text/css">\@import url(/include/detail_cover.css);</style>
        <style type="text/css">\@import url(/include/service-notifications.css);</style>
        <script language="JavaScript" type="text/javascript" src="/include/overlib_mini.js"></script>
        <script language="javascript" type="text/javascript" src="/include/jquery.js"></script>
        <script language="javascript" type="text/javascript" src="/include/jquery.ifixpng.js"></script>
        <script language="javascript" type="text/javascript" src="/include/jquery.selectboxes.js"></script>
        <script language="javascript" type="text/javascript" src="/include/folding.js"></script>
		<script language="javascript" type="text/javascript" src="/include/datepicker.js"></script>
        <script language="javascript" type="text/javascript" src="/include/form.js"></script>
		<script type="text/javascript" src="/include/right_content.js"></script>
		<script type="text/javascript" src="/include/for_iE6_png.js"></script>
		<script language="JavaScript" src="/include/ChinArk_form.js"></script>
END
;
		if($help_hash{"HELP_ENABLED"} eq "on")
		{
			printf <<EOF
			<script type="text/javascript" src="/include/help.js"></script>
EOF
;
		}
printf <<END
        <!-- Include Service Notification API -->
        <script language="javascript" type="text/javascript" src="/include/servicesubscriber.js"></script>
		
        $extrahead
    
        <script type="text/javascript">
            overlib_pagedefaults(WIDTH,300,FGCOLOR,'#ffffcc',BGCOLOR,'#666666');
            function swapVisibility(id) {
                el = document.getElementById(id);
                if(el.style.display != 'block') {
                    el.style.display = 'block'
                }
                else {
                    el.style.display = 'none'
                }
            }
        </script>
        <script type="text/javascript" src="/include/accordion.js"></script>
END
;
    if($ENV{'SCRIPT_NAME'} eq '/cgi-bin/main.cgi' && -e '/home/httpd/html/include/uplink.js') {
        printf <<END
            <script language="javascript" type="text/javascript" src="/include/uplink.js"></script>
            <link rel="stylesheet" type="text/css" media="screen" title="Uplinks Status" href="/include/uplinks-status.css" />
END
;
    }
    if($ENV{'SCRIPT_NAME'} eq '/cgi-bin/uplinkeditor.cgi') {
        printf <<END
            <script language="javascript" type="text/javascript" src="/include/uplinkeditor.js"></script>
END
;
    }
    if ($ENV{'SCRIPT_NAME'} eq '/cgi-bin/updates.cgi' && -e '/home/httpd/html/include/ajax.js'  && -e '/home/httpd/cgi-bin/updates-ajax.cgi'
        && -e '/home/httpd/html/include/updates.js' && -e'/home/httpd/html/include/updates.css') {
      printf <<END

        <style type="text/css">\@import url(/include/updates.css);</style>
        <script type="text/javascript" language="JavaScript" src="/include/ajax.js"></script>
        <script type="text/javascript" language="JavaScript" src="/include/updates.js"></script>
    </head>
    <body>
END
;
    } else {
      printf <<END
      </head>
      <body>
END
;
    }
    #&showmenu();
	&show_cover();
    &displaymymenu();
    print "<div id='elvis_right_content'  class='right-content'>";
#    eval {
#	require 'endian-network.pl';
#	$supported = check_support();
#	warn_unsupported($supported);
#    };
if ( -e '/var/tmp/oldkernel' && $ENV{'SCRIPT_NAME'} eq '/cgi-bin/main.cgi') {
    printf <<END                                                                                                                                                                
    <h3 class="warning">%s</h3>                                                                                                                                                 
    <table class="list"><tr><td align="center"><img src="/images/dialog-warning.png"/></td><td align="left">%s</td></tr></table>                                                
    <br/>                                                                                                                                                                       
END
,                                                                                                                                                                    
_('Old kernel'),
_('You are not running the latest kernel version. If your Firewall has been updated this could mean that a new kernel has been installed. To activate it you will have to <a href="%s">reboot</a> the system.<br/>If this is not the case you should check your %s file and make sure that the newest kernel will be booted after a restart.',"/cgi-bin/shutdown.cgi","/boot/grub/grub.conf")
;                 
}
    # Add HTML required to display notifications posted from service(s)
	my $help_enabled = $ENV{'SCRIPT_NAME'};
    printf <<END
<div id="notification-view"  style="display:none;top:50px;"></div>
<div id="module-content">
<span id='gui_set'  class='hidden_class' >$gui_set</span>
<input id="help_hidden" value='$help_enabled' class="hidden_class" />
END
;
check_cookie_user();
}

sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'USER_FORM',
       'option'   :{
                    'new_name':{
                               'type':'text',
                               'required':'1',
							   'check':'other|',
							   'other_reg':'!/^\$/',
                               'ass_check':function(eve){
							                              var msg = "";
														  var str = eve._getCURElementsByName("new_name","input","USER_FORM")[0].value;
														  var reg = /^[_0-9a-zA-Z\\u4e00-\\u9fa5]+\$/;
					                                      if(str.length<=50){
						                                     if(/\\s/.test(str)){msg=str+"含有空格！";}
						                                     if(!reg.test(str)){msg=str+"含有非法字符！";}
					                                      } else{
						                                     msg="资源名长度应小于50个字符！";
					                                      }
														  return msg;
							                            }
                             },
                    'new_href':{
                               'type':'text',
                               'required':'1',
                               'check':'url|',
                             },
                    'new_description':{
                               'type':'textarea',
                               'required':'1',
                               'check':'other|',
							   'other_reg':'!/^\$/',
							   'ass_check':function(eve){
							                              var msg = "";
														  var str = eve._getCURElementsByName("new_description","textarea","USER_FORM")[0].value;
														  var reg = /[@#\$\%^&*~`]/;
					                                      if(str.length<=200){
						                                     if(reg.test(str)){msg=str+"含有非法字符！";}
					                                      } else{
						                                     msg="描述长度应小于200个字符！";
					                                      }
														  reg = /^[()<>|;"“”,，《》（）、]+\$/;
														  if(reg.test(str))
														  {
														     msg="描述中不能单独出现特殊字符！";
														  }
														  return msg;
							                            }
                             },
					'modify_name':{
                               'type':'text',
                               'required':'1',
							   'check':'other|',
							   'other_reg':'!/^\$/',
                               'ass_check':function(eve){
							                              var msg = "";
														  var str = eve._getCURElementsByName("modify_name","input","USER_FORM")[0].value;
														  var reg = /^[_0-9a-zA-Z\\u4e00-\\u9fa5]+\$/;
					                                      if(str.length<=50){
						                                     if(/\\s/.test(str)){msg=str+"含有空格！";}
						                                     if(!reg.test(str)){msg=str+"含有非法字符！";}
					                                      } else{
						                                     msg="资源名长度应小于50个字符！";
					                                      }
														  return msg;
							                            }
                             },
                    'modify_href':{
                               'type':'text',
                               'required':'1',
                               'check':'url|',
                             },
                    'modify_description':{
                               'type':'textarea',
                               'required':'1',
                               'check':'other|',
							   'other_reg':'!/^\$/',
							   'ass_check':function(eve){
							                              var msg = "";
														  var str = eve._getCURElementsByName("modify_description","textarea","USER_FORM")[0].value;
														  var reg = /[@#\$\%^&*~`]/;
					                                      if(str.length<=200){
						                                     if(reg.test(str)){msg=str+"含有非法字符！";}
					                                      } else{
						                                     msg="描述长度应小于200个字符！";
					                                      }
														  reg = /^[()<>|;"“”,，《》（）、]+\$/;
														  if(reg.test(str))
														  {
														     msg="描述中不能单独出现特殊字符！";
														  }
														  return msg;
							                            }
                             },
                 }
    }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("USER_FORM");
    </script>
EOF
;
}

sub doaction() {

    if(!$action) 
	{
		return;
    }
	
	if($action eq 'onoff')
	{
	   my $change_name = $par{'resource_name'};
	   my $status = $par{'status'};
	   my $type = $par{'type'};
	   if($type eq 'web')
	   {
	      my @new_web_resources;
		  my $count = 0;
		  my $new_count = 0;
		  foreach my $one_resource(@web_resources)
		  {
		     my @line_splited = split(/,/,$one_resource);
		     $name = $line_splited[0];
			 if($name eq $change_name)
		     {     
		        my $newline = $name;
				$newline .= ",";
				$newline .= $line_splited[1];
				$newline .= ",";
				if($status eq 'on')
				{
				   $newline .= "off";
				   
				} else {
				   $newline .= "on";
				}
				$new_web_resources[$new_count] = $newline;
		     } else {
			    $new_web_resources[$new_count] = $web_resources[$count];
		     }
			 $new_count++;
		     $count++;
		  }
		  @web_resources = @new_web_resources;
		  &write_web_resources();
	   } else {
	      my @new_other_resources;
		  my $count = 0;
		  my $new_count = 0;
		  foreach my $one_resource(@other_resources)
		  {
		     my @line_splited = split(/,/,$one_resource);
		     $name = $line_splited[0];
			 if($name eq $change_name)
		     {     
		        my $newline = $name;
				$newline .= ",";
				if($status eq 'on')
				{
				   $newline .= "off";
				   
				} else {
				   $newline .= "on";
				}
				$new_other_resources[$new_count] = $newline;
		     } else {
			    $new_other_resources[$new_count] = $other_resources[$count];
		     }
			 $new_count++;
		     $count++;
		  }
		  @other_resources = @new_other_resources;
		  &write_other_resources();
	   }
	   if($status eq 'on')
	   {
		  $notemessage = "资源禁用成功！";
	   } else {
		  $notemessage = "资源启用成功！";
	   }
	   return;
    }
	
    if ($action eq 'delete') 
	{
		my $dele_name = $par{'resource_name'};
		my @new_web_resources;
		my @new_other_resources;
		my $count = 0;
		my $new_count = 0;
		my $name;
		foreach my $one_resource(@web_resources)
		{
		   my @line_splited = split(/,/,$one_resource);
		   $name = $line_splited[0];
		   if($name eq $dele_name)
		   {     
		      #my $del_file = $description_folder;
			  #$del_file .= $dele_name;
		      #`rm -r $del_file`;
			  rmdesfile($name);
		   } else {
			  
		      $new_web_resources[$new_count++] = $web_resources[$count];
		   }
		   $count++;
		}
		$count = 0;
		$new_count = 0;
		$name = "";
		$dele_name = $par{'resource_name'};
		foreach my $one_resource(@other_resources)
		{
		   my @line_splited = split(/,/,$one_resource);
		   $name = $line_splited[0];
		   if($name eq $dele_name)
		   {
		      #my $del_file = $description_folder;
			  #$del_file .= $dele_name;
		      #`rm -r $del_file`;
			  rmdesfile($name);
		   } else {
		      $new_other_resources[$new_count++] = $other_resources[$count];
		   }
		   $count++;
		}
		
		@web_resources = @new_web_resources;
		@other_resources = @new_other_resources;
		&write_web_resources();
		&write_other_resources();
		$notemessage = "删除成功！";
		return;
    }

    if(($action eq 'add'))
	{
        my $resource_name = $par{'new_name'};
		my $access_type = $par{'new_type'};
		my $href = $par{'new_href'};
		my $des = $par{'new_description'};
		my $new_des;
		foreach my $line(split(/\n/,$des)){
			chomp($line);
			$new_des .= $line;
		}
		my $enabled = $par{'new_enable'};
		if($enabled eq 'on')
		{
		   $enabled = "on";
		} else {
		   $enabled = "off";
		}
        my $check = 0;
		my $web_length=0;
		my $other_length=0;
        foreach my $one_resource(@web_resources)
		{
		   my @line_splited = split(/,/,$one_resource);
		   $name = $line_splited[0];
		   chomp($name);
		   if($name eq $resource_name)
		   {     
			   $check = 1;
		   }
		   $web_length++;
		}
		foreach my $one_resource(@other_resources)
		{
		   my @line_splited = split(/,/,$one_resource);
		   $name = $line_splited[0];
		   if($name eq $resource_name)
		   {
			   $check = 1;
		   }
		   $other_length++;
		}
		
		if($check)
		{
		   $errormessage = "已存在同名资源，添加失败！";
		   return
		}
		my $new_des_file = $description_folder;
		$new_des_file .= $resource_name;
		if($access_type eq 'web')
		{
		  if($web_length >= 50)
		  {
		    $errormessage = "网络资源数已达最大数量50，添加失败！";
		    return
		  }
		  my $new_line = $resource_name;
		  $new_line .= ",";
		  $new_line .= $href;
		  $new_line .= ",";
		  $new_line .= $enabled;
		  `echo >>$web_resource_file $new_line`;
		  if($new_des ne "")
		  {
		     mkdesfile($resource_name,$new_des);
		     #`touch $new_des_file`;
		     #`echo >>$new_des_file $new_des`;
		  }
		} else {
		  if($other_length >= 50)
		  {
		    $errormessage = "网络资源数已达最大数量50，添加失败！";
		    return
		  }
		  my $new_line = $resource_name;
		  $new_line .= ",";
		  $new_line .= $enabled;
		  `echo >>$other_resource_file $new_line`;
		  if($new_des ne "")
		  {
		    mkdesfile($resource_name,$new_des);
		    #`touch $new_des_file`;
		    #`echo >>$new_des_file $new_des`;
		  }
		}
		$notemessage = "新资源添加成功！";
	    return;
    }
    
    if($action eq 'modify')
	{
	    my $resource_name = $par{'modify_name'};
		my $access_type = $par{'modify_type'};
		my $href = $par{'modify_href'};
		my $des = $par{'modify_description'};
		my $new_des;
		foreach my $line(split(/\n/,$des)){
			chomp($line);
			$new_des .= $line;
		}
		my $enabled = $par{'modify_enable'};
		if($enabled eq 'on')
		{
		   $enabled = "on";
		} else {
		   $enabled = "off";
		}
		my $origin_name = $par{'origin_name'};
		my $origin_type = $par{'origin_type'};
		
		my $same = 0;
		foreach my $line (@web_resources)
		{
		   my @line_splited = split(/,/,$line);
		   my $name = $line_splited[0];
           if($origin_name ne $name)
           {
		      if($resource_name eq $name)
			  {
			     $same = 1;
			  }
           }		   
		}
		foreach my $line (@other_resources)
		{
		   my @line_splited = split(/,/,$line);
		   my $name = $line_splited[0];
           if($origin_name ne $name)
           {
		      if($resource_name eq $name)
			  {
			     $same = 1;
			  }
           }		   
		}
		if($same)
		{
		   $errormessage = "已存在同名的资源，修改失败！";
		} else {
		   #ACCESTYPE没变时
		   if($access_type eq $origin_type)
		   {
		      #WEB类
		      if($access_type eq "web") 
              {
			     my @new_web_resources;
				 my $new_count = 0 ;
				 my $count = 0;
                 foreach my $line (@web_resources)
                 {
				    my @line_splited = split(/,/,$line);
		            my $name = $line_splited[0];
					if($name eq $origin_name)
					{
					   my $new_line = $resource_name;
					   $new_line .= ",";
					   $new_line .= $href;
					   $new_line .= ",";
		               $new_line .= $enabled;
					   $new_web_resources[$new_count++] = $new_line;
					} else {
					   $new_web_resources[$new_count++] = $web_resources[$count];
					}
					$count++;
                 }
                 @web_resources = @new_web_resources;
                 &write_web_resources();
				 #my $old_des_file = $description_folder;;
				 #$old_des_file .= $origin_name;
				 #my $new_des_file = $description_folder;
		         #$new_des_file .= $resource_name;
				 rmdesfile($origin_name);
                 #`rm $old_des_file`;
			     #`rm $new_des_file`;
				 if($new_des ne "")
				 {
				   mkdesfile($resource_name,$new_des);
                   #`touch $new_des_file`;
                   #`echo >>$new_des_file $new_des`;
                 }
                 $notemessage = "资源修改成功！";
                 return;				 
              }	else {
			  #OTHER类
			     my @new_other_resources;
				 my $new_count = 0 ;
				 my $count = 0;
                 foreach my $line (@other_resources)
                 {
					my @line_splited = split(/,/,$line);
		            my $name = $line_splited[0];
					if($name ne $origin_name)
					{
					   $new_other_resources[$new_count++] = $other_resources[$count];
					} else {
					   my $new_line = $resource_name;
					   $new_line .= ",";
		               $new_line .= $enabled;
					   $new_other_resources[$new_count++] = $new_line;
					}
					$count++;
                 }
                 @other_resources = @new_other_resources;
                 &write_other_resources();
				 #my $old_des_file = $description_folder;;
				 #$old_des_file .= $origin_name;
				 #my $new_des_file = $description_folder;
		         #$new_des_file .= $resource_name;
				 rmdesfile($origin_name);
                 #`rm $old_des_file`;
			     #`rm $new_des_file`;
				 if($new_des ne "")
				 {
				   mkdesfile($resource_name,$new_des);
                   #`touch $new_des_file`;
                   #echo >>$new_des_file $new_des`;		   
				 }
				 $notemessage = "资源修改成功！";
                 return;
              }			  
		   } else {
		   #ACCESSTYPE改变了
              if($origin_type eq 'web')
              {  #新TYPE为OTHER
			     my @new_web_resources;
				 my $new_count = 0 ;
				 my $count = 0;
			     foreach my $line (@web_resources)
                 {
				    my @line_splited = split(/,/,$line);
					if($line_splited[0] ne $origin_name)
					{
					   $new_web_resources[$new_count++] = $web_resources[$count];
					}
					$count++;
                 }
				 @web_resources = @new_web_resources;
				 &write_web_resources();
				 my $length = scalar(@other_resources);
				 my $new_line = $resource_name;
				 $new_line .= ",";
		         $new_line .= $enabled;
				 $other_resources[$length] = $new_line;
				 &write_other_resources();
				 #my $old_des_file = $description_folder;;
				 #$old_des_file .= $origin_name;
				 #my $new_des_file = $description_folder;
		         #$new_des_file .= $resource_name;
				 #`rm $old_des_file`;
				 #`rm $new_des_file`;
				 rmdesfile($origin_name);
				 if($new_des ne "")
				 {
				   mkdesfile($resource_name,$new_des);
                   #`touch $new_des_file`;
                   #`echo >>$new_des_file $new_des`;
				 }
				 $notemessage = "资源修改成功！";
                 return;
              } else {
			     #新TYPE为WEB
				 my @new_other_resources;
				 my $new_count = 0 ;
				 my $count = 0;
			     foreach my $line (@other_resources)
                 {
					my @line_splited = split(/,/,$line);
		            my $name = $line_splited[0];
					if($name ne $origin_name)
					{
					   $new_other_resources[$new_count++] = $other_resources[$count];
					}
					$count++;
                 }
				 @other_resources = @new_other_resources;
				 &write_other_resources();
				 my $length = scalar(@web_resources);
				 my $new_line = $resource_name;
				 $new_line .= ",";
				 $new_line .= $href;
				 $new_line .= ",";
		         $new_line .= $enabled;
				 $web_resources[$length] = $new_line;
				 &write_web_resources();
				 #my $old_des_file = $description_folder;;
				 #$old_des_file .= $origin_name;
				 #my $new_des_file = $description_folder;
		         #$new_des_file .= $resource_name;
				 #`rm $old_des_file`;
				 #`rm $new_des_file`;
				 rmdesfile($origin_name);
				 if($new_des ne "")
				 {
				   mkdesfile($resource_name,$new_des);
                   #`touch $new_des_file`;
                   #`echo >>$new_des_file $new_des`;
				 }
				 $notemessage = "资源修改成功！";
                 return;
              }			      
		   }
		}
	    return;
	}
	return;
}

sub read_web_resources(){
    open(FILE,$web_resource_file);
	@web_resources = <FILE>;
	close(FILE);
}

sub read_other_resources(){
    open(FILE,$other_resource_file);
	@other_resources = <FILE>;
	close(FILE);
}

sub write_web_resources(){
    `rm $web_resource_file`;
    `touch $web_resource_file`;
    foreach my $new_web (@web_resources) 
	{
	   `echo >>$web_resource_file $new_web`;
	}
}

sub write_other_resources(){
    `rm $other_resource_file`;
	`touch $other_resource_file`;
    foreach my $new_other (@other_resources) 
	{
	   `echo >>$other_resource_file $new_other`;
	}
}

my $extraheader  = '';
if(!(-e $resource_folder))
{
   `mkdir $resource_folder`;
}
getcgihash(\%par);
$action = $par{'ACTION'};

&read_web_resources();
&read_other_resources();
doaction();
&read_web_resources();
&read_other_resources();
showhttpheaders();
openmypage('资源配置', 1,$extraheader);
openbigbox($errormessage,"", $notemessage);
#当不存在动作时默认给action赋值add
if (!$par{'ACTION'} ) {
	$action = 'add';
}
show_set();
list_resources();
check_form();
&show_script();
closebigbox();
closepage();