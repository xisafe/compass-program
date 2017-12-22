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
require './endianinc.pl';

use Net::IPv4Addr qw (:all);
use Spreadsheet::WriteExcel;
use CGI::Carp qw (fatalsToBrowser);
use CGI qw(:standard);
use Encode;
use URI::Escape;
my $cgi= new CGI; 


my $restart  = '/usr/local/bin/restartopenvpn';
my $passwd   = '/usr/bin/openvpn-sudo-user';
my $etherconf = "/var/efw/ethernet/settings";
my $openvpnconf = "/var/efw/openvpn/settings";
my $whitelist_file = "/var/efw/openvpn/whitelist";
my $cert_dir = "/var/efw/openvpn/cert/";
my $max_user_path="/usr/local/bin/license/getMaxusers";
my $current_users_num   = '/usr/bin/openvpn-sudo-user longlist | wc -l';
my $upload_error_file = "/var/efw/openvpn/error_upload_users";
my $static_ip_file = '/var/efw/openvpn/static_ipaddr';


my $dirtyfile  = '/var/efw/openvpn/dirtyuserconfig';

my $name        = _('OpenVPN server');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked');
my $self = $ENV{SCRIPT_NAME};

my %par;
my $action = '';
my $sure = '';
my $username = '';
my $errormessage = '';
my $my_notemessage = '';
my $err = 1;
my $config = 0;
my $CACERT_FILE = '/var/efw/openvpn/cacert.pem';
my @errormessages;
my $search_value_offset='';


sub check_form(){
  printf <<EOF
  <script>
  var check = new ChinArk_forms();
  var object = {
       'form_name':'USER_FORM',
       'option'   :{
                    'username':{
                               'type':'text',
                               'required':'1',
                               'check':'name|',
                               'ass_check':function(eve){
                                                        var msg="";
                                                        var key = 0;
                                                        var username = eve._getCURElementsByName("username","input","USER_FORM")[0].value;
                                                        if(!eve.users){
                                                            \$.ajax({
                                                                  type : "get",
                                                                  url : '/cgi-bin/chinark_back_get.cgi',
                                                                  async : false,
                                                                  data : 'path=/var/efw/openvpn/passwd',
                                                                  success : function(data){ 
                                                                    eve.users = data;                                                                     
                                                                  }
                                                            });
                                                        }
                                                        var exist = eve.users.split('\\n');
                                                        for (var i = 0; i < exist.length; i++) {
                                                            var tmp = exist[i].split(':');
                                                            if(username == tmp[0]){
                                                                msg = '用户名'+username+'已存在';
                                                                break;
                                                            }
                                                        }
                                                        return msg;
                                                     }
                             },
                    'password':{
                               'type':'password',
                               'required':'1',
                             },
                    'password2':{
                               'type':'password',
                               'required':'1',
                               'ass_check':function(eve){
                                   var msg ='';
                                   var pass1 = eve._getCURElementsByName("password","input","USER_FORM")[0].value;
                                   var pass2 = eve._getCURElementsByName("password2","input","USER_FORM")[0].value;
                                   if (pass1 != pass2){
                                      msg = "密码不一致";
                                   }
                                   return msg;
                               }
                             },
                    'custom_domain':{
                               'type':'text',
                               'required':'0',
                               'check':'domain_suffix|',
                             },
                    'main_dns':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'second_dns':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'comments':{
                               'type':'text',
                               'required':'0',
							   'check':'other|',
                               'other_reg':'!/^\$/',
							   'ass_check':function(eve){
							                              var msg = "";
														  var str = eve._getCURElementsByName("comments","input","USER_FORM")[0].value;
														  var reg = /[@#\$\%^&*~`]/;
					                                      if(str.length<=20){
						                                     if(reg.test(str)){msg=str+"含有非法字符！";}
					                                      } else{
						                                     msg="注释长度应小于等于20个字符！";
					                                      }
														  return msg;
							                            }
                             },
                    'remotenets':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip_mask|',
                             },
                    'explicitroutes':{
                               'type':'textarea',
                               'required':'0',
                               'check':'other|',
							   'other_reg':'!/^\$/',
							   'ass_check':function(eve){
                                                        var msg = ""; 
                                                        var ips = eve._getCURElementsByName("explicitroutes","textarea","USER_FORM")[0].value;
                                                        var ip = ips.split("\\n");
                                                        if(ips.length==1&&ip[0]=='')
														{
														   return msg;
														}
                                                        
													    for(var i=0;i<ip.length;i++)
														{
														   msg = '';
														   if(ip[i]!='')
														   {
														      var one_split = ip[i].split("/");
															  var one_ip = one_split[0];
															  var mask = one_split[1];
															  var zero = /^0+/;
															  
															  if (mask < 1 || mask >32 || one_split.length != 2 || zero.test(mask)){
		                                                          msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
																  return msg;
	                                                          }
															  
															  var ip_reg = /^([1-9]|[1-9]\\d|1\\d{2}|2[0-1]\\d|22[0-3])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3}\$/;
															  if(!ip_reg.test(one_ip))
															  {
															      msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
																  return msg;
															  }
															  var total_str = "";
		                                                      var temp = new Array(); 
		                                                      temp = one_ip.split(".");
															  for (var j = 0;j < 4;j ++){
			                                                     temp[j] = parseInt(temp[j]);
			                                                     temp[j] = eve.formatIP(temp[j]);
			                                                     total_str += temp[j];
		                                                      }
															  var segment = total_str.substring(mask);
		                                                      var all_zero = /^0+\$/;
		                                                      if(mask==32||all_zero.test(segment))
															  {
															  } else {
															     msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
																 return msg;
															  }
														   } else {
														      msg = '不能出现空行！';
															  return msg;
														   }
														}
														return msg;
                                                     }
                             },                           
                    'cert_sn':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'!/^\$/',
                               'ass_check':function(eve){
                                                        var msg = ""; 
                                                        var cert_sn = eve._getCURElementsByName("cert_sn","input","USER_FORM")[0].value;
                                                        var sn = cert_sn.split(":");
                                                        var reg = /^([\\dA-Fa-f]{2})\$/;
                                                        for (var i = 0; i < sn.length; i++) {
                                                            if(!reg.test(sn[i])){
                                                                msg = "证书序列号格式有误";
                                                                break;
                                                            }
                                                        }
                                                        return msg;
                                                     }
                             },
                    'static_ip':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                               'ass_check':function(eve){
							                            var msg="";
                                                        var ip = eve._getCURElementsByName("static_ip","input","USER_FORM")[0].value;
							                            if(!eve.subnet){
                                                            \$.ajax({
                                                                  type : "get",
                                                                  url : '/cgi-bin/sslvpn_getnet.cgi',
                                                                  async : false,
                                                                  data : 'path=/var/efw/openvpn/settings"',
                                                                  success : function(data){ 
                                                                    eve.subnet = data; 
                                                                  }
                                                            });
                                                        }
                                                        
														     var subnet = eve.subnet.split("/");
															 var net_number = subnet[1];
															 var nets = new Array();
															 nets = subnet[0].split(".");
															 var total_str = "";
															 for (i = 0;i < 4;i ++){
			                                                     nets[i] = parseInt(nets[i]);
			                                                     nets[i] = eve.formatIP(nets[i]);
			                                                     total_str += nets[i];
		                                                     }
															 var netnum = total_str.substr(0,subnet[1]);
															 
															 nets = new Array();
															 nets = ip.split(".");
															 total_str = "";
															 for (i = 0;i < 4;i ++){
			                                                     nets[i] = parseInt(nets[i]);
			                                                     nets[i] = eve.formatIP(nets[i]);
			                                                     total_str += nets[i];
		                                                     }
															 var newnet = total_str.substr(0,net_number);
															 if(newnet!=netnum)
															 {
															    msg="IP地址不在已设定的虚拟网段"+eve.subnet+"中！";
															 }
															 return msg;
                                                     }
                             },
                    'custom_dns':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|',
                             },
                 }
         }
  check._main(object);
  //check._get_form_obj_table("USER_FORM");
  </script>
EOF
;
}

sub ip2long {
    return unpack("l*", pack("l*", unpack("N*", inet_aton(shift))));
}

sub read_config_line($$){
    my $name = shift;
    my $file = shift;
    my $line;
    foreach my $elem(read_conf_file($file)){
        if ($elem =~ /^$name,/ && $name) {
            $line = $elem;
            last;
        }
    }
    return $line;
}

sub restart() {
    my $logid = "$0 [" . scalar(localtime) . "]";
	system("rm $dirtyfile");
    print STDERR `$restart --force`; 
    print STDERR "$logid: restarting done\n";
    $notemessage = _('OpenVPN server has been restarted!');
}

sub list_users() {

    my $canreadcacert = 0;
    if (open F, $CACERT_FILE) {
        $canreadcacert = 1;
        close(F);
    }

    #openbox('100%', 'left', _('Account configuration'));
printf <<EOF
<table class="ruleslist" style="height:30px;">
	<tr>
	    <td style="background-image: url(../images/con-header-bg.jpg);border: 1px solid #999;color: #073662;font-weight: bold;">
		  <table width="100%">
		  <tr>
		      <td style="border:0px;padding-left:30px;vertical-align:middle;">
			      <form method="post" action="$ENV{'SCRIPT_NAME'}" onsubmit="return check_search();">
				    <input style="width:240px;" type="text" maxlength="20" name="search_value" id="search_value" />
			        &nbsp;&nbsp;<input type="submit" value="搜索" />
					<label style="margin-left:10px;font-weight:normal;">(*可根据用户名或备注或搜索用户。)</label>
					<input type="hidden" name="ACTION" value="search" />
				  </form>
			  </td>
		  </tr>
		  </table>
		</td>
	</tr>
</table>
<table border="0" class="ruleslist" cellspacing="0" cellpadding="4" width="100%">
  <tr>
    <td width="16%" class="boldbase"><b>用户名</b></td>
    <td width="16%" class="boldbase"><b>本地子网</b></td>
    <td width="16%" class="boldbase"><b>地址分配</b></td>
    <td width="16%" class="boldbase"><b>证书序列号</b></td>
    <td width="16%" class="boldbase"><b>备注</b></td>
    <td width="16%" class="boldbase"><b>活动/动作</b></td>
  </tr>
EOF
;

EOF
;

    my @users = split(/\n/, `$passwd longlist`);
	if($action eq 'search')
	{
	   my @new_users;
	   my $count = 0;
	   my $new_count = 0;
	   my $key = $par{'search_value'};
	   foreach my $line (@users)
	   {
	      my @splited = split(/:/,$line);
		  my $tmp_username = $splited[0];
		  my $whitelist_line = read_config_line($tmp_username,$whitelist_file);
		  my @list_value = split(/,/,$whitelist_line);
		  my $tmp_comments = $list_value[5];
	      if($tmp_username=~/$key/||$tmp_comments=~/$key/)
		  {
		    $new_users[$new_count++] = $users[$count];
		  }
		  $count++;
	   }
	   @users = @new_users;
	   $search_value_offset = $par{'search_value'};
	}
	#值不为空意为搜索到指定内容后翻页。
    if($par{'search_value_offset'} ne '')
    {
       my $key = $par{'search_value_offset'};
	   my @new_users;
	   my $count = 0;
	   my $new_count = 0;
	   foreach my $line (@users)
	   {
	      my @splited = split(/:/,$line);
		  my $tmp_username = $splited[0];
		  my $whitelist_line = read_config_line($tmp_username,$whitelist_file);
		  my @list_value = split(/,/,$whitelist_line);
		  my $tmp_comments = $list_value[5];
	      if($tmp_username=~/$key/||$tmp_comments=~/$key/)
		  {
		    $new_users[$new_count++] = $users[$count];
		  }
		  $count++;
	   }
	   @users = @new_users;
	   $search_value_offset = $par{'search_value_offset'};
    }
    my $i = 0;
	my $length = @users;
	#跳转页面参数控制 殷其雷 2013-3-7
	my $offset;
	my $total;
	my $next;
	my $last;
	#END
	if($length >0)
	{
	#页面参数设置并只显示当前页面20条记录 殷其雷 2013-3-7
	$offset = 1; 
	if ($par{'OFFSET'} =~ /^\d+$/) {
		$offset = $par{'OFFSET'};
	}
	if ($offset < 1) {
		$offset = 1;
	}
	$total = POSIX::ceil($length/20);
	if ($offset > $total) {
		$offset = $total;
	}
    $next = $offset + 1;
	$last = $offset - 1;
	my $num = 0;
	$num = $num + $last*20;
	if ($num < 0) {
		$num = 0;
	}
	my $start = ($offset-1) * 20;
	
    foreach my $line (@users) {
	   if($i >= $start && $i < $start+20) {        
    my $whitelist_line = read_config_line($username,$whitelist_file);
    my @list_value = split(/,/,$whitelist_line);
    my $cert_sn = $list_value[2];
    my $comments = $list_value[5];
	my @split = split(/:/, $line);
	my $user = $split[0];
	my $remotenets = $split[5];
	$remotenets =~ s/,/<BR>/;
	my $pushnets = $split[7];
	$pushnets =~ s/,/<BR>/;
	my $staticips = $split[8];
	$staticips =~ s/,/<BR>/;

	if ($split[6] eq 'on') {
	    $pushnet = _('None');
	}
	if ($staticips eq '') {
	    $staticips = _('dynamic');
	}

	my $oddeven = 'oodd';
	if ($i % 2) {
	    $oddeven = 'even';
	}
    ###获取白名单相关信息
    my $whitelist_line = read_config_line($user,$whitelist_file);
    my @list_value = split(/,/,$whitelist_line);
    my $cert_sn = $list_value[2];
	#2013-7-21 按长度2截取cert_sn 并添加冒号
	$cert_sn = add_maohao($cert_sn);
	#
    my $whitelist_enabled = $list_value[4];
    my $comments = $list_value[5];
    my $whitelist_png;    
    my $whitelist_note;
    if ($whitelist_enabled  eq "on") {        
        $whitelist_png = '/images/white_list.png';    
        $whitelist_note = '移除白名单';
    }
    else{
        $whitelist_png = '/images/black_list.png';    
        $whitelist_note = '加入白名单';
    }
	###处理结束
	my $gif = 'off.png';
	my $enabled_action = 'enable';
	my $enabled_description = _('Enable account');
	if ($split[1] eq 'enabled') {
	    $gif = 'on.png';
	    $enabled_action = 'disable';
	    $enabled_description = _('Disable account');
	}

	printf <<EOF
<tr class="$oddeven">
  <td>$user</td>
  <td>$pushnets</td>
  <td>$staticips</td>
  <td>$cert_sn</td>
  <td>$comments</td>
EOF
;


        printf <<EOF
  <td>
<form method='post' action='$self' style="float:left;margin-left:5px;">
    <input class='imagebutton' type='image' name='$enabled_description' src='/images/$gif' alt='$enabled_description' title='$enabled_description'>
    <input type="hidden" name="ACTION" value="$enabled_action">
    <input type="hidden" name="username" value="$user">
</form>

<form method='post' action='$self' style="float:left;margin-left:5px;">
    <input class='imagebutton' type='image' name='%s' src='/images/edit.png' alt='%s' title='%s'>
    <input type="hidden" name="ACTION" value="set">
    <input type="hidden" name="username" value="$user">
</form>

<form method='post' action='$self' style="float:left;margin-left:5px;">
    <input class='imagebutton' type='image' src='$whitelist_png' title='$whitelist_note'>
    <input type="hidden" name="ACTION" value="remove">
    <input type="hidden" name="status" value="$whitelist_enabled">
    <input type="hidden" name="username" value="$user">
</form>

<form method='post' action='$self' onSubmit="return confirm('确定删除?')" style="float:left;margin-left:5px;">
    <input class='imagebutton' type='image' name='%s' src='/images/delete.png' alt='%s' title='%s'>
    <input type="hidden" name="ACTION" value="delete">
    <input type="hidden" name="username" value="$user">
</form>


</td>
</tr>
EOF
,
_('Really delete the VPN client %s?', $user),	
_('Edit'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
_('Remove'),
;
}
#END
	$i++;
    }
}else{
	no_tr(6,_('Current no content'));
}


printf <<END


</table>
END
;

if($length >0)
{
printf <<END
<table cellpadding="0" cellspacing="0" class="list-legend">
<tr>
        <td><b>%s</b>
        <img src='/images/on.png' alt='%s' >
        %s
        <img src='/images/off.png' alt='%s' />
        %s
        <img src='/images/edit.png' alt='%s' >
        %s
        <img src='/images/delete.png' alt='%s' >
        %s
		<img src='/images/white_list.png' alt='%s' >
        %s
        <img src='/images/black_list.png' alt='%s' >
        %s</td>
END
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
"移除白名单",
"移除白名单",
"加入白名单",
"加入白名单"
;
#显示跳转以及上下页翻页 殷其雷 2013-3-7
printf <<END
        <td>
		<div>
<table width='100%' align='center' border="0">
	<tr>
	<td width='2%' align='right'>
END
;
	if ($last > 0 ) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="OFFSET" value="1">
	<input type="hidden" name="search_value_offset" value="$search_value_offset">
    <input class='submitbutton' type="image" title='%s' name="ACTION" src="/images/first-page.png">
	</form>
END
,
_('First page')
;
    } else {

	print "<input class='submitbutton' type='image' name='ACTION' title='"._('First page')."' src='/images/first-page-off.png'>";
    }
    print "</td><td width='2%'>\n";
	if ($last > 0) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$last">
	<input type="hidden" name="search_value_offset" value="$search_value_offset">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/last-page.png">
	</form>
END
,
_('Last page')
;
    }
	else {

	print "<input class='submitbutton' type='image' name='ACTION' title='"._('Last page')."' src='/images/last-page-off.png'>";
    }
	printf <<END
		<td  align='center'>%s</td>
		<td  align='center'>%s</td>
END
,
_('Total %s pages',$total),
_('Current %s page',$offset),
;

    print "<td width='2%' align='right'>";
    if (!($next > $total)) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$next">
	<input type="hidden" name="search_value_offset" value="$search_value_offset">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/next-page.png">
	</form>
END
,
_('Next page')
;
    } else {
	print "<input class='submitbutton' type='image' name='ACTION' title='"._('Next page')."' src='/images/next-page-off.png'>";
    }
	print "</td><td width='2%'>\n";
	 if (!($next > $total)) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="OFFSET" value="$total">
	<input type="hidden" name="search_value_offset" value="$search_value_offset">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/end-page.png">
    </form>
END
,
_('End page')
;
    } else {
	print "<input class='submitbutton' type='image' name='ACTION' title='"._('End page')."' src='/images/end-page-off.png'>";
    }
    printf <<END
		</td>	
		<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<td  align='right' >%s: <input type="text" SIZE="2" name='OFFSET' VALUE="$offset"><input type="hidden" name="search_value_offset" value="$search_value_offset"></td>
		<td  align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
		</form>
		<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<td  align='center'><input class='submitbutton' type='submit' name='ACTION' value='下载全部用户' /></td>
		</form>
</tr>
</table>
	</div>
	</td>
	</tr>
	</table>
END
,_('Jump to Page')
,_('Go')
;
#END
}

    #closebox();

}

# -------------------------------------------------
# EDIT ACCOUNT
# -------------------------------------------------

sub show_set($$) {
    my $username = shift;
    my $action = shift;
    my @split = ();
    my %selected;
    my $password = '';
    my $whitelist_line = read_config_line($username,$whitelist_file);
    my @list_value = split(/,/,$whitelist_line);
    my $cert_sn = $list_value[2];
	#2013-7-21 按长度2截取cert_sn 并添加冒号
	$cert_sn = add_maohao($cert_sn);
	#
    my $comments = $list_value[5];
	my $ori_cert_type = "";
	my $auto_input;
	my $hand_input;
	my $hand_display;
    $selected{$list_value[1]} = "selected='selected'";
    $checked{'whitelist_enabled'}{$whitelist_enabled} = ' ';
    if ($list_value[4] eq 'on') {
         $checked{'whitelist_enabled'}{$whitelist_enabled} = "checked='checked'";
    
    }
    if ($action eq 'set') {
      	&openeditorbox(_('编辑用户'), "","showeditor", "createrule", @errormessages);
      	@split = split(/:/, `$passwd getuser "$username"`);
      	$password = '_NOTCHANGED_';
      	$buttontext = _('Update');
		#只有编辑时，旧的用户证书为上传方式时才需要设置$ori_cert_type为"upload";
		if($selected{'upload'} ne '')
		{
		   $ori_cert_type = "upload";
		}
    } 
    else {
  		my $text;
        $username = "";
  		if ($errormessage) {
        $text='showeditor';
      }
  	  &openeditorbox(_('添加用户'), "","$text", "createrule", @errormessages);
  	  $password = '';
  	  $buttontext = _('Add');
	  $comments = "";
	  $checked{'whitelist_enabled'}{$whitelist_enabled} = "checked";
	  $selected{'upload'} = "selected";
	  $selected{'input'} = "";
	  $selected{'none'} = "";
	  $cert_sn = "";
	  
    }

    $checked{'setred'}{$setred} = ' ';
    if ($split[1] eq 'setred') {
	     $checked{'setred'}{$setred} = "checked='checked'";
    }
    $checked{'user_enabled'}{$user_enabled} = ' ';
    if ($split[0] ne 'disabled') {
         $checked{'user_enabled'}{$user_enabled} = "checked='checked'";
    }

    $checked{'setorange'}{$setorange} = '';		
    if ($split[2] eq 'setorange') {
	     $checked{'setorange'}{$setorange} = "checked='checked'";	
    }

    $checked{'setblue'}{$setblue} = '';		
    if ($split[3] eq 'setblue') {
	$checked{'setblue'}{$setblue} = "checked='checked'";	
    }

    my $remotenets = $split[4];
    $remotenets =~ s/,/\n/g;
    chomp($remotenets);

    $checked{'dontpushroutes'}{$dontpushroutes} = ' ';
    if ($split[5] eq 'on') {
	$checked{'dontpushroutes'}{$dontpushroutes} = "checked='checked'";
    }

    my $explicitroutes = $split[6];
    $explicitroutes =~ s/,/\n/g;
    chomp($explicitroutes);

    my $static_ip = $split[7];;
    $static_ip =~ s/,/\n/g;
    chomp($static_ip);
    
	#静态地址为空，则为动态分配，不为空，则为静态分配。新建用户时选择静态又未输入地址的情况需由输入时限制，若未限制将导致编辑开始时选择的是自动分配。
	if($static_ip eq '')
	{
	   $auto_input="checked";
	   $hand_input="";
	   $hand_display="none";
	} else {
	   $auto_input = "";
	   $hand_input = "checked";
	   $hand_display="block"
	}
	
    my $custom_dns = $split[8];
    my $main_dns;
    my $second_dns;
    $checked{'push_custom_dns'}{$push_custom_dns} = ' ';
    if ($custom_dns) {
        ($main_dns,$second_dns) = split(/,/,$custom_dns);
        $checked{'push_custom_dns'}{$push_custom_dns} = "checked='checked'";
    }

    my $custom_domain = $split[9];

    if ($split[10] =~ /on/) {
	$checked{'push_custom_dns'}{$push_custom_dns} = "checked='checked'";
    }
    if ($split[11] =~ /on/) {
	$checked{'push_custom_domain'}{$push_custom_domain} = "checked='checked'";
    }

    my $usernamelabel = _('Username');
    if ($config->{'AUTH_TYPE'} eq 'cert') {
        $usernamelabel = _('Common name');
    }
####help_msg
	my $help_hash1 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","通过vpn引导客户流量","-10","30","down");
	my $help_hash2 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","networt_behind_client","-10","30","down");
	my $help_hash3 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","push_only_these_net","-10","30","down");
	my $help_hash4 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","推送域名服务器","-10","30","down");
	my $help_hash5 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","推送域","-10","30","down");
	###
    printf <<EOF
    </form>
     <form enctype="multipart/form-data" name="USER_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
<table border='0' cellspacing="0" cellpadding="4">
<tr class="env">
  <td class="add-div-table" rowspan="6"><b>%s</b></td>
  <td>%s *</td>
EOF
, _('Account information')
, $usernamelabel
;

    if ($action ne 'set') {
	printf <<EOF
  <td><input type='text' name='username' value='' /></td>
EOF
;
    } else {
	printf <<EOF
  <td><input type='text' name='usernamedisabled' value='$username' disabled /> <input type='hidden' name='username' value='$username' /></td>
 
EOF
;
    }

    my $defaultpw = '_NOTCHANGED_';
    if ($action ne 'set') {
	$defaultpw = '';
    }
    if ($config->{'AUTH_TYPE'} ne 'cert') {
        printf <<EOF
<tr class="odd">
  <td >%s *</td>
  <td><input type='password' name='password' value='$defaultpw' /></td>
</tr>
<tr class="env">
  <td>%s *</td>
  <td><input type='password' name='password2' value='$defaultpw' /></td>
</tr>
EOF
, _('Password')
, _('Verify password')
;
    } else {
        printf <<EOF
<input type='hidden' name='password' value='_NOTCHANGED_' />
<input type='hidden' name='password2' value='_NOTCHANGED_' />
EOF
;
    }

printf <<EOF
    <tr class="odd">
       <td>
       用户证书 *
       </td>
       <td>
        <select name="user_cert" id="user_cert" onchange="change_cert_type()">
            <option value="upload" $selected{'upload'}>上传</option>
            <option value="input" $selected{'input'}>输入证书序列号</option>
            <option value="none" $selected{'none'}>暂不设置</option>
        </select>
       <input class="hidden_class" type="file" name="cert_file" id="cert_file" />  
       <input class="hidden_class" type="text" name="cert_sn" id="cert_sn" value="$cert_sn" />
	   <input type="hidden" name="ori_cert_type" value="$ori_cert_type" />
       </td>
     </tr>
     <tr class="env">
       <td>备注 </td>
       <td>
        <input id="comments" name="comments" type="text" value="$comments" maxlength="20" style="width:200px;"/>
        </td>
     </tr>
     <tr class="odd">
       <td>
        是否加入白名单
       </td>
       <td>
            <input type="checkbox" id="whitelist" name="whitelist" $checked{'whitelist_enabled'}{$whitelist_enabled}  />加入白名单
       </td>
     </tr>
     <tr class="env">
  <td class="add-div-table" rowspan="7">接入时用户计算机设置</td>
  <td width="300px">地址分配</td>
  <td>
  <p style="height:25px;padding:0px;margin-top:5px;">
           <input type="radio" name="addresschoose" value="autoset" style="vertical-align:middle;" onchange="address_choose();" $auto_input/>
           <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">自动分配</label>
         </p>         
         <p style="height:25px;padding:0px;margin:0px;">
           <input type="radio" name="addresschoose" value="byhand" style="float:left;margin-left:5px;vertical-align:middle;" onchange="address_choose();" $hand_input/>
           <label style="float:left;vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">&nbsp;手动设置</label>
           <label style="float:left;vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;display:$hand_display;" id="ipaddress_text">IP地址：*</label>
           <label style="float:left;vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">
            <input type="text" name="static_ip" id="ipaddress" value="$static_ip" style="float:left;vertical-align:middle;width:100px;display:$hand_display;"/>
           </label>
    <text cols="17" rows="2" name='static_ip' value="$static_ip">
  </td>
</tr>
</tr>
<tr  class="odd">
  <td class="need_help" width="300px">本地子网 $help_hash3
  </td>
  <td>
    <textarea cols="17" rows="2" name='explicitroutes'>$explicitroutes</textarea>
  </td>
</tr>
<tr  class="env" >
  <td class="need_help">接入时用户计算机使用右边的DNS服务器地址 $help_hash4</td>
  <td>
    <p style="margin-bottom:2px;">
            <input type="checkbox" id="push_custom_dns" name="push_custom_dns" $checked{'push_custom_dns'}{$push_custom_dns} style="vertical-align:middle;padding:0px;margin:0px;" onchange="start_dns();" />
            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">启用</label>
          </p>
          <p id="first_dns_display" style="display:block;">
            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">首选DNS服务器：*</label>
            <input type="text" id="firstdns" name="main_dns" value="$main_dns" style="vertical-align:middle;padding:0px;margin:0px;" />
          </p>
          <p id="second_dns_display" style="display:block;margin-top:1px;margin-bottom:2px;">
            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">备选DNS服务器：*</label>
            <input type="text" id="seconddns" name="second_dns" value="$second_dns" style="vertical-align:middle;padding:0px;margin:0px;" />
          </p>
  </td>
</tr>
<tr  class="odd" >
  <td class="need_help">接入时将用户计算机加入此域 $help_hash5</td>
    <td valign="top">
      <input type='checkbox' name='push_custom_domain' value='on' $checked{'push_custom_domain'}{$push_custom_domain}>&nbsp;%s</input>
      <input type="text" name='custom_domain' value="$custom_domain" />
    </td>
</tr>
<tr class="env">
  <td class="need_help">接入时用户计算机使用此服务器作为默认网关 $help_hash1</td>
  <td ><input type="checkbox" name="setred" value="set" $checked{'setred'}{$setred}>启用</td>
</tr>
<tr  class="odd">
  <td class="need_help">远程网络 $help_hash2</td>
  <td>
    <textarea cols="17" rows="2" name='remotenets'>$remotenets</textarea>
  </td>
</tr>
<tr class="env">
  <td class="need_help">此账户是否启用 $help_hash1</td>
  <td ><input type="checkbox" name="user_enabled" value="set" $checked{'user_enabled'}{$user_enabled}>启用</td>
</tr>
EOF
;   

=p 原始代码
    printf <<EOF


<tr class="odd">
  <td class="add-div-table" rowspan="5">%s</td>
  <td class="need_help">%s $help_hash1</td>
  <td ><input type="checkbox" name="setred" value="set" $checked{'setred'}{$setred}></td>
</tr>

<tr class="odd">
  <td>%s</td>
  <td><input type="checkbox" name="dontpushroutes" value="on" $checked{'dontpushroutes'}{$dontpushroutes}></td>
</tr>
EOF
, _('Client routing')
, _('通过VPN服务器引导用户流量')
, _("Push only global options to this client")
;

       if (blue_used()) {
           printf <<EOF
<tr class="odd">  
   <td>%s</td>
   <td><input type="checkbox" name="setblue" value="set" $checked{'setblue'}{$setblue}></td>
</tr>
EOF
,_('Push route to blue zone')
;
        }

       if (orange_used()) {
           printf <<EOF
<tr class="odd">
  <td>%s</td>
  <td><input type="checkbox" name="setorange" value="set" $checked{'setorange'}{$setorange}></td>
</tr>
EOF
,_('Push route to orange zone')
;
       }


printf <<EOF
<tr  class="odd">
  <td class="need_help">%s $help_hash2</td>
  <td>
    <textarea cols="17" rows="2" name='remotenets'>$remotenets</textarea>
  </td>
</tr>

<tr  class="odd">
  <td class="need_help" width="300px">%s $help_hash3
  </td>
  <td>
    <textarea cols="17" rows="2" name='explicitroutes'>$explicitroutes</textarea>
  </td>
</tr>

</table>
<table border="0" cellspacing="0" cellpadding="4" width="100%">

<tr class="env" >
  <td class="add-div-table" rowspan="3"><b>%s</b></td>
  <td width="300px">%s</td>
  <td>
    <textarea cols="17" rows="2" name='static_ip'>$static_ip</textarea>
  </td>
</tr>

<tr  class="env" >
  <td class="need_help">%s $help_hash4</td>
  <td>
    <ul><li><input type='checkbox' name='push_custom_dns' value='on' $checked{'push_custom_dns'}{$push_custom_dns}>&nbsp;%s</input></li>
    <li><textarea cols="17" rows="2" name='custom_dns'>$custom_dns</textarea></li></ul>
  </td>
</tr>

<tr  class="env" >
  <td class="need_help">%s $help_hash5</td>
    <td valign="top">
      <ul><li><input type='checkbox' name='push_custom_domain' value='on' $checked{'push_custom_domain'}{$push_custom_domain}>&nbsp;%s</input></li>
      <li><input type="text" name='custom_domain' value="$custom_domain" /></li></ul>
    </td>
</tr>
=cut
printf <<EOF
</table>

<input type='hidden' name='ACTION' value='$action' />
<input type="hidden" name="sure" value="y">
		
EOF

,_('远程网络')
,_('只推送这些网络到客户端')
,_('Custom push configuration')
,_('Static ip addresses')
,_('Push these nameservers')
,_('Enable')
,_('Push domain')
,_('Enable')

,_('Save')
;

    &closeeditorbox($buttontext, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

}


sub cracklib($$) {
    my $password = shift;
    my $password1 = shift;

    if ($password !~ /^[A-Za-z0-9_]+$/) {
		return (0, _('Invalid characters in password.'));
    }
    if ($password ne $password1) {
		return (0, _('passwords are not identical'));
    }
    if (length($password) < 6 || length($password) > 32) {
		return (0, _('密码长度不正确，只能输入6至32个字符!'));
    }
    return 1;

}

sub sanitize($) {
    my $data = shift;
    $data =~ s/\"/\\\"/;
    return $data;
}

sub delete_whitelist($){
    my $user = shift;
    my @save_lines = read_conf_file($whitelist_file);
    for (my $i = 0; $i < @save_lines; $i++) {
        if ($save_lines[$i] =~/^$user,/) {
            delete $save_lines[$i];
        }        
    }
    save_config_file(\@save_lines,$whitelist_file);
}

sub enabled_whitelist ($$){
    my $user = shift;
    my $enabled = shift;
    my @save_lines = read_conf_file($whitelist_file);
    for (my $i = 0; $i < @save_lines; $i++) {
        if ($save_lines[$i] =~/^$user,/) {
             my @tmp = split(/,/,$save_lines[$i]);
            if ($enabled eq "enable") {
                $save_lines[$i] = "$tmp[0],$tmp[1],$tmp[2],$tmp[3],$tmp[4],$tmp[5],on";
            }
            else{
                $save_lines[$i] = "$tmp[0],$tmp[1],$tmp[2],$tmp[3],$tmp[4],$tmp[5],";
            }
        }        
    }
    save_config_file(\@save_lines,$whitelist_file);
}

sub remove_whitelist($$){
    my $user = shift;
    my $enabled = shift;
    my @save_lines = read_conf_file($whitelist_file);
    for (my $i = 0; $i < @save_lines; $i++) {
        if ($save_lines[$i] =~/^$user,/) {
            my @tmp = split(/,/,$save_lines[$i]);
            if ($enabled eq "on") {
                $save_lines[$i] = "$tmp[0],$tmp[1],$tmp[2],$tmp[3],,$tmp[5],$tmp[6]";
            }
            else{
                $save_lines[$i] = "$tmp[0],$tmp[1],$tmp[2],$tmp[3],on,$tmp[5],$tmp[6]";
            }
        }        
    }
    save_config_file(\@save_lines,$whitelist_file);
}

sub uploads_cert($){
    my $uploadname = shift;
    my $filehandle = $cgi->param('cert_file');
    my $filename = $filehandle;
    my @tmp = split(/\./,$filename);
    if ($tmp[1] ne "p12" && $tmp[1] ne "crt" && $tmp[1] ne "cer" && $tmp[1] ne "pem" ) {
	    if($filehandle eq '')
		{
		   $errormessage = "请选择一个本地证书文件并上传！";
		} else {
		   $errormessage = "证书格式不正确，必须是crt,p12,cer,pem证书";
		}
		#删除静态IP
		my $old_ip = '';
		my @tmp_users = split(/\n/, `$passwd longlist`);
		foreach my $one (@tmp_users)
		{
		    my @split = split(/:/,$one);
			if($uploadname eq $split[0])
			{
			   $old_ip = $split[8];
			   break;
		    }
		}
		&rm_static($old_ip);
		#
        system("$passwd del \"$uploadname\"");
        `sudo fcmd "$passwd del $uploadname"`;
        return ;
    }
    $filename = "$cert_dir$uploadname.$tmp[1]"; 
    system("touch $filename");
    open ( UPLOADFILE, ">$filename" ) or die "$!";
    binmode UPLOADFILE;
    while (<$filehandle>) 
	{
        print UPLOADFILE;
    }
    close UPLOADFILE;
	return "$uploadname.$tmp[1]";
}

sub save_whitelist($){
    my $action = shift;
    my $line;
    my $sn_number = "";
    my $user = $par{'username'};
    my @save_lines = read_conf_file($whitelist_file);
	my $filename = "";
	my $change = 1;
	my $snhex = "";
	my $sndec = "";
	my $old_snhex = "";
	my $old_sndec = "";
    for (my $i = 0; $i < @save_lines; $i++) {
         if ($save_lines[$i] =~ /^$user,/) {
		    my @split = split(/,/,$save_lines[$i]);
			$old_snhex = $split[2];
			$old_sndec = $split[3];
            delete $save_lines[$i];
        }
    }
    $par{'comments'} =~s/,/，/g;
    if ($par{'user_cert'} eq "none" || $par{'user_cert'} eq "upload" ) {
        if ($par{'user_cert'} eq "upload") {
		    #$par{'ori_cert_type'}为upload $par{'user_cert'} 也为upload,同时filehandle为空，意为编辑时没有改变旧的上传用户证书，不需调用uploads_cert。
			my $filehandle = $cgi->param('cert_file');
		    if($par{'ori_cert_type'} eq 'upload' && $filehandle eq '')
			{
			  #上传用户证书未改变。
			  $change = 0;
			} else {
			  #上传方式改变了，或者选了新的证书文件上传。
			  #uploads_cert中出错了，会删掉已写入的用户信息。
              $filename = uploads_cert($par{'username'});
			}
			
        }
		#NONE情况可无条件写入白名单。
		if($par{'user_cert'} eq "none" )
		{
		   $line = "$par{'username'},$par{'user_cert'},,,$par{'whitelist'},$par{'comments'},$par{'whitelist'}";
           push(@save_lines,$line);
		}
		#UPLOAD情况只有uploads_cert没有出错才添加进白名单。
		if($par{'user_cert'} eq "upload" && $errormessage eq "")
		{
		   $snhex = "($user";
	       $snhex .= "_snhex)";
	       $sndec = "($user";
	       $sndec .= "_sndec)";
		   if($change)
		   {
		      $line = "$par{'username'},$par{'user_cert'},$snhex,$sndec,$par{'whitelist'},$par{'comments'},$par{'whitelist'}";
		   } else {
		      #upload未change时读取旧的序列号再写入。
			  $line = "$par{'username'},$par{'user_cert'},$old_snhex,$old_sndec,$par{'whitelist'},$par{'comments'},$par{'whitelist'}";
		   }
           push(@save_lines,$line);
		}
    }
    elsif($par{'user_cert'} eq "input" ){
        my $sn = $par{'cert_sn'};
        $sn =~s/://g;
        $sn_number = hex($sn);
		#2013-7-21 将第3位 $par{'cert_sn'} 换为 $sn
        $line = "$par{'username'},$par{'user_cert'},$sn,$sn_number,$par{'whitelist'},$par{'comments'},$par{'whitelist'}";
        push(@save_lines,$line);
    }
    save_config_file(\@save_lines,$whitelist_file);
    if ($par{'user_cert'} eq "upload" && $errormessage eq '') {
	    my $result = -1;
		#新加入或改变了上传方式时调用解析证书序列号，返回是否成功，未完成。
		if($change)
		{
		   #error 返回1 正确返回0
		   `sudo /usr/local/bin/getcertsn.py $user $filename`;
		}
          open(FILE,"/tmp/getcertsn_tmp");
		  $result = <FILE>;
		  close(FILE);
		  chomp($result);
		  `rm /tmp/getcertsn_tmp`;
		if($result)
		{
		   $errormessage = "证书错误！请重新添加用户并上传正确的证书！";
		   #删除静态IP
		    my $old_ip = '';
		    my @tmp_users = split(/\n/, `$passwd longlist`);
		    foreach my $one (@tmp_users)
		    {
		       my @split = split(/:/,$one);
			   if($username eq $split[0])
			   {
			      $old_ip = $split[8];
			      break;
		       }
		    }
		    &rm_static($old_ip);
		    #
            system("$passwd del \"$user\"");
            `sudo fcmd "$passwd del $user"`;
		    `rm $cert_dir$filename`;
		    &delete_whitelist($username);
            return "error";
		} else {
		  $notemessage = _("Account \"%s\" successfully", $username);
		  return "true";
		}
    } else {
	    if($errormessage ne '')
		{
		   #errormessage错误情况下，给MODIFY的情况删除白名单对应行,ADD的情况因为没有添加进去而无影响。
		   &delete_whitelist($username);
		   return "error";
		} else {
		   $notemessage = _("Account \"%s\" successfully", $username);
	       return "true";
		}
	}
}
sub disable_user ($) {
    my $user = shift;
    `$passwd set \"$user\" --toggle='disable' --rewrite-users`;
	`sudo fcmd "$passwd set \"$user\" --toggle"`;	
    #`sudo fmodify "/var/efw/openvpn/passwd"`;
}

sub enable_user ($) {
    my $user = shift;
    `$passwd set \"$user\" --toggle='enable' --rewrite-users`;
	`sudo fcmd "$passwd set \"$user\" --toggle"`;	
	#`sudo fmodify "/var/efw/openvpn/passwd"`;
}

sub checkuser() {
    if ($username =~ /^$/) {
		$errormessage = _('用户名不能为空.');
		return 0;
    }
	if (length($username) < 4 || length($username) > 20) {
		$errormessage = _('用户名长度不正确，只能输入4至20个字符!');
		return 0;
    }
    return 1;
}

sub getStaticIPs() {
    my %hash;
    my $ret = \%hash;

    my @users = split(/\n/, `$passwd longlist`);
    foreach my $line (@users) {
      	my @split = split(/:/, $line);
      	my $user = $split[0];
      	my $staticips = $split[8];
      	foreach my $ip (split(/,/, $staticips)) {
      	    $ret->{$ip} = $user;
      	}
    }
    return $ret;
}

sub checkvalues() {

    my $remotenets = $par{'remotenets'};
    my $explicitroutes = $par{'explicitroutes'};
    my $custom_dns = $par{'custom_dns'};
    my $static_ip = $par{'static_ip'};
    my $custom_domain = $par{'custom_domain'};

    if ($remotenets) {
		my ($ok, $nok) = checkIPs($remotenets, 32);
		if ($nok ne '') {
			$errormessage = _('Networks behind client "%s" are invalid', $nok);
			return 0;
		}
    }
    if ($explicitroutes) {
	    #2013-7-23 修改checkIPS为新写函数checkmyIPs 以支持检测后缀名为32 若要恢复把下行my删除并修改checkform  
		my ($ok, $nok) = checkmyIPs($explicitroutes, 32);
		if ($nok ne '') {
			$errormessage = _('Networks to be pushed "%s" are invalid', $nok);
			return 0;
		}
    }
    if ($custom_dns) {
		my @dnss = split(/[\r\n,]/, $custom_dns);
		foreach my $elem (@dnss) {
			if (!&validdomainname($elem)) {
				$errormessage = _('Custom nameserver addresses "%s" are invalid', $elem);
				return 0;
			}
			if (length($elem) > 67) {
				$errormessage = _('域名服务器 "%s" 太长，必须小于等于67字符', $elem);
				return 0;
			}
		}
    }
    if ($custom_domain) {
		if (! validdomainname($custom_domain)) {
			$errormessage = _('Domain name to be pushed "%s" is invalid', $custom_domain);
			return 0;
		}
    }

    my $remoteips = getStaticIPs();
    if ($static_ip) {
	my ($ok, $nok) = checkIPs($static_ip, 33);
	if ($nok ne '') {
	    $errormessage = _('Static ip addresses "%s" are invalid', $nok);
	    return 0;
	}

	my $ether;
	if (-e $etherconf) {
	    $ether = readconf($etherconf);
	}

	my $openvpn;
	if (-e $openvpnconf) {
	    $openvpn = readconf($openvpnconf);
	    
	}
	my $purple_begin_long = ip2long($openvpn->{PURPLE_IP_BEGIN});
	my $purple_end_long = ip2long($openvpn->{PURPLE_IP_END});


	foreach my $ipcidr (split(/[\r\n,]/, $static_ip)) {
	    my ($ip, $cidr) = split(/\//, $ipcidr);
	    if ($ip eq $ether->{GREEN_BROADCAST}) {
			$errormessage = _('Static ip address "%s" can\'t be same as broadcast ip of VPN segment "%s".', $ip, $b);
			return 0;
	    }
	    if ($ip eq $ether->{GREEN_NETADDRESS}) {
			$errormessage = _('Static ip address "%s" can\'t be same as network ip of VPN segment "%s".', $ip, $a);
			return 0;
	    }
	    if ($ip eq $ether->{GREEN_ADDRESS}) {
			$errormessage = _('Static ip address "%s" can\'t be same as GREEN ip address', $ip);
			return 0;
	    }
	    if ($remoteips->{$ip} && ($remoteips->{$ip} ne $username)) {
			$errormessage = _('Static ip address "%s" is already assigned to user "%s"!', $ip, $remoteips->{$ip});
			return 0;
	    }
	    my $longip = ip2long($ip);
	    if (($longip >= $purple_begin_long) && ($longip <= $purple_end_long)) {
			$errormessage = _('Static ip address "%s" can\'t be part of dynamic ip pool %s - %s!', 
					  $ip, $openvpn->{PURPLE_IP_BEGIN}, $openvpn->{PURPLE_IP_END});
			return 0;
	    }
	}
    }

    return 1;
}

sub nl2coma($) {
    my $string = shift;
    my $ret = '';
    foreach my $item (split(/[\n\r]/, $string)) {
	next if ($item =~ /^$/);
	$ret .= ','.$item;
    }
    $ret =~ s/^,//;
    return $ret;
}

sub setdirty($$) {
    my $username = shift;
    my $remotenets = shift;
    my @split = split(/:/, `$passwd getuser "$username"`);
    my $oldremotenets = $split[4];
    makedirty();
    return if ($remotenets eq $oldremotenets);
}

sub makedirty() {
    `touch $dirtyfile`;
}


sub my_warnbox($) {
    my $caption = shift;
    if ($caption =~ /^\s*$/) {
        return;
    }
    printf <<EOF
<div id="warning_box">
<img src='/images/dialog-warning.png' alt='_("Warning")' >
<span>$caption</span>
<form method='post' action='$self' enctype='multipart/form-data' style="margin-top:5px;">
  <input type='hidden' name='ACTION' value='restart' />
  <input type='submit' value='%s' class="net_button"/>
</form>
</div>
EOF
,_('restart')
;
}

##导入用户及下载模板 殷其雷 2013-3-8
sub display_add(){
    &openuploadbox(_('导入用户'), "", "uploaduser", @errormessages);
	printf <<EOF
     <table width="100%" cellpadding="0" cellspacing="0">
	 <tr class="odd"><td class="add-div-type">导入用户</td>
	 <td style="width:260px">
	 <form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}' onsubmit="return check_upload_file();">
	 <input type="file" name="up_file" style="width:200px" />
	 <input type="submit" name="submit" value="上传" style="width:40px" >
	 <input type='hidden' name='ACTION' value='upload'>
	 </form>
	 </td>
	 <td align='left'>
	 <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	 <input type="submit" value="下载模板" style="width:60px"><input type="hidden" name='ACTION' value="download" />
	 </form>
	 </td>
	 </tr>
	 </table>
EOF
;
    &closeuploadbox();
}

sub uploads($$){
	my $uploadname = shift;
	my $upload_dir = shift;
	my $file_length = 0;
	my $upload_filehandle = $cgi->param('up_file');
	my $upload_filename = $upload_filehandle;
	my @splited_filenames = split(/\./, $upload_filename);
	foreach my $splited_filename (@splited_filenames)
	{
	   $file_length++;
	}
	if($file_length == 0)
	{
	   $errormessage = '请选择一个xls文件再上传！';
	} else {
	   $file_length--;
	   if ($splited_filenames[$file_length] eq 'xls')
	   {
	       my $filename = "/tmp/temp.xls";
	       open ( UPLOADFILE, ">$filename" ) or die "$!";
	       binmode UPLOADFILE;
	       while ( <$upload_filehandle> )
 	      {
		      print UPLOADFILE;
	      }
	      close UPLOADFILE;
		  #`perl openvpn_users_upload.pl`;
		  system('perl openvpn_users_upload.pl &');
		  #调用改了显示时间的上方notemessage框
		  $my_notemessage = "数据已成功上传，正在后台处理，不符合要求及重复的数据会自动过滤。处理阶段此页面无法操作，请耐心等待一段时间后手动刷新此页面，数据全部出现之前不要上传新数据以免丢失。";
	   } else {
	      $errormessage = '只支持处理xls文件！';
	   }
	}
}

sub show_script(){
    printf <<EOF
    <script type="text/javascript">
    window.onload = function(){
        change_cert_type();
        start_dns();
    }
    function user_certificate(){
       var obj1 = document.getElementById("up_file");
       var obj2 = document.getElementById("serial_num");
       var elems = document.getElementsByName("certificate");
       var value;
       for(var i=0;i<elems.length;i++)
       {
           if(elems.item(i).checked)
           {
              value = elems.item(i).getAttribute("value");
           }
       }
       if(value=="upload")
       {
          obj1.style.display = "block";
          obj2.style.display = "none";
       }
       if(value=="enter")
       {
          obj1.style.display = "none";
          obj2.style.display = "block";
       }
       if(value=="not")
       {
          obj1.style.display = "none";
          obj2.style.display = "none";
       }
    }
    function address_choose(){
       var obj = document.getElementById("ipaddress");
       var obj1 = document.getElementById("ipaddress_text");
       var elems = document.getElementsByName("addresschoose");
       var value;
       for(var i=0;i<elems.length;i++)
       {
           if(elems.item(i).checked)
           {
              value = elems.item(i).getAttribute("value");
           }
       }
       if(value=="autoset")
       {
           obj.style.display="none";
           obj1.style.display="none";
       } else {
           obj.style.display="block";
           obj1.style.display="block";  
       }
    }
    function start_dns() {
       var obj = document.getElementById("push_custom_dns");
       var obj1 = document.getElementById("first_dns_display");
       var obj2 = document.getElementById("second_dns_display");
       if(obj.checked)
       {
         obj1.style.display="block";  
         obj2.style.display="block";  
       } else {
         obj1.style.display="none";
         obj2.style.display="none";
       }
    }
    function add_domain(){
       var obj = document.getElementById("adddomain");
       var obj1 = document.getElementById("adddomain_add");
       if(obj.checked)
       {
         obj1.style.display="block";  
       } else {
         obj1.style.display="none";
       }
    }

    function change_cert_type() {
       var cert_type = document.getElementById("user_cert");
       var cert_sn = document.getElementById("cert_sn");
       var cert_file = document.getElementById("cert_file");
       if (cert_type.value == "upload") {
           cert_file.style.display = "inline";
           cert_sn.style.display = "none";
       }
       else if(cert_type.value == "input"){
           cert_file.style.display = "none";
           cert_sn.style.display = "inline";
       }
       else{
           cert_file.style.display = "none";
           cert_sn.style.display = "none";
       }
    }
    </script>
EOF
;
}

sub openuploadbox($$$$@) {
    my $linktext = shift;
    my $show = shift;
    my $linkname = shift;
    my @errormessages = @_;
    my $disp_editor = "none";
    my $disp_link = "";
    if ($show eq "showeditor" || $#errormessages ne -1) {
        $disp_link = "none";
        $disp_editor = "";
    }

    if ($linktext ne "") {
        printf <<EOF
    <div id="add-div_upload" >

     <div id="add-div-header_upload">
<span style="display:block;float:left;margin:0px auto auto 5px;"><img src="/images/add.png" />&nbsp;$linktext</span></div>
EOF
        ;
    }
    printf <<EOF
   <div id="add-div-content_upload"  style="display:$disp_editor;">
EOF
;

    if ($#errormessages ne -1) {
        printf <<EOF
        <div class="editorerror" name="$linkname">
            <div>
                <ul style="padding-left: 20px">
EOF
        ;
        foreach my $errormessage (@errormessages) {
            printf <<EOF
                    <li style="color: red;">
                        <font color="red">$errormessage</font>
                    </li>
EOF
            ;
        }
        printf <<EOF
                </ul>
            </div>
            <hr size="1" color="#cccccc">
        </div>
EOF
        ;
    }
    ;
}

sub closeuploadbox {

    printf <<EOF 
    <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
    <tr class="add-div-footer"><td width="50%">	</td><td width="50%" align="right">*请严格按照模板创建新用户数据，只支持处理xls表格。</td></tr>
	</table>
	</form>     
    </div>  </div>	
EOF
;
}

sub download_all {
    my $file = '/tmp/all_users.xls';
    my @users = split(/\n/, `$passwd longlist`);
	my $row_num = 1;
	my $sheetName = 'My sheet';
	my $book = new Spreadsheet::WriteExcel( $file );
	my $sheet = $book->add_worksheet( $sheetName );
	#设置格式
	$sheet->set_column('A:A',20);
	$sheet->set_column('C:C',30);
	$sheet->set_column('D:D',20);
	$sheet->set_column('E:E',40);
	my $center_format = $book -> add_format();
	$center_format->set_align('center');
	#输出表头
	$sheet->write(0, 0, decode('utf8','用户名'),$center_format);
	$sheet->write(0, 1, decode('utf8','密码'),$center_format);
	$sheet->write(0, 2, decode('utf8','序列号'),$center_format);
	$sheet->write(0, 3, decode('utf8','静态地址'),$center_format);
	$sheet->write(0, 4, decode('utf8','注释'),$center_format);
	$sheet->write(0, 5, decode('utf8','加入白名单'),$center_format);
	$sheet->write(0, 6, decode('utf8','是否启用'),$center_format);
	#输出内容
	foreach my $line (@users) {
	   my @split = split(/:/, $line); 
	   my $username = $split[0];
	   my $staticips = $split[8];
	   my $enabled = $split[1];
	   if($enabled eq 'enabled')
	   {
	      $enabled = "启用";
	   } else {
	      $enabled = "禁用";
	   }
	   my $whitelist_line = read_config_line($username,$whitelist_file);
       my @list_value = split(/,/,$whitelist_line);
       my $cert_sn = $list_value[2];
	   my $comments = $list_value[5];
	   my $white_enable = "否";
	   if($list_value[4] eq 'on')
	   {
	      $white_enable = "是";
	   }
	   
	   $staticips =~ s/,/;/;
	   $sheet->write_string($row_num, 0, decode('utf8',$username));
	   $sheet->write_string($row_num, 1, '******');
	   $sheet->write_string($row_num, 2, decode('utf8',$cert_sn));
	   $sheet->write_string($row_num, 3, decode('utf8',$staticips));
	   $sheet->write_string($row_num, 4, decode('utf8',$comments));
	   $sheet->write_string($row_num, 5, decode('utf8',$white_enable),$center_format);
	   $sheet->write_string($row_num, 6, decode('utf8',$enabled),$center_format);
	   $row_num++;
	}
	$book->close();
	return $file;
} 

sub make_module {
    my $file = '/tmp/module.xls';
    my @users = split(/\n/, `$passwd longlist`);
	my $sheetName = 'My sheet';
	my $book = new Spreadsheet::WriteExcel( $file );
	my $sheet = $book->add_worksheet( $sheetName );
	my $center_format = $book -> add_format();
	$center_format->set_align('center');
	$sheet->write(0, 0, decode('utf8','用户名'),$center_format);
	$sheet->write(0, 1, decode('utf8','密码'),$center_format);
	$sheet->write(0, 2, decode('utf8','序列号'),$center_format);
	$sheet->write(0, 3, decode('utf8','静态地址'),$center_format);
	$sheet->write(0, 4, decode('utf8','注释'),$center_format);
	$sheet->write(0, 5, decode('utf8','加入白名单'),$center_format);
	$sheet->write(0, 6, decode('utf8','是否启用'),$center_format);
	for(my $i=1;$i<=5;$i++)
	{
	    my $name = '用户';
		$name .= $i;
		my $pwd = '密码';
		$pwd .= $i;
		my $serial = '序列号';
		$serial .= $i;
		my $ip = '192.168.0.';
		$ip .= $i;
		my $comment = "备注";
		$comment .= $i;
		
	    $sheet->write($i, 0, decode('utf8',$name));
	    $sheet->write($i, 1, decode('utf8',$pwd));
		$sheet->write($i, 2, decode('utf8',$serial));
		$sheet->write($i, 3, decode('utf8',$ip));
		$sheet->write($i, 4, decode('utf8',$comment));
		$sheet->write($i, 5, decode('utf8','是'),$center_format);
		$sheet->write($i, 6, decode('utf8','启用'),$center_format);
	}
	$book->close();
	return $file;
}
#END
sub check_max_users(){
    my $max_users=`$max_user_path`;
	my $current_users = `$current_users_num`;
	if($current_users >= $max_users )
	{
	   return 1;
	} else {
	   return 0;
	}
}

sub doaction() {
    if(!$action) 
	{
		return;
    }

    if ($action eq 'apply') 
	{
		restart();
		$warnmessage= "";
		#应用成功后清空动作
		$par{'ACTION'} = '';
	    $action = '';
		return;
    }

    if ($action eq 'delete') 
	{
		if (!checkuser()) 
		{
            return;
		}
		#删除静态IP
		my $old_ip = '';
		my @tmp_users = split(/\n/, `$passwd longlist`);
		foreach my $one (@tmp_users)
		{
		    my @split = split(/:/,$one);
			if($username eq $split[0])
			{
			   $old_ip = $split[8];
			   break;
		    }
		}
		&rm_static($old_ip);
		#
		system("$passwd del \"$username\"");
		`sudo fcmd "$passwd del $username"`;	
        &delete_whitelist($username);
		#`sudo fmodify "/var/efw/openvpn/passwd"`;
		$notemessage = _('User \'%s\' successfully deleted', $username);
		#删除成功后清空动作
		$par{'ACTION'} = '';
	    $action = '';
		return;
    }

    if(($action eq 'add') ||(($action eq 'set')&& ($sure eq 'y')))
	{

		if (!checkuser()) 
		{
			return;
		}
	
		if(!checkvalues()) 
		{
			return;
		}

		if($action eq 'add')
		{
		   if(check_max_users())
		   {
		      $errormessage = "当前已达到系统支持最大用户数，添加失败！";
		      return;
		   }
		}
	    my $pass1 = $par{'password'};
	    my $pass2 = $par{'password2'};

	    my $remotenets = nl2coma($par{'remotenets'});
	    my $explicitroutes = nl2coma($par{'explicitroutes'});
	    my $custom_dns = "$par{'main_dns'},$par{'second_dns'}";
	    my $static_ip = nl2coma($par{'static_ip'});
	    my $custom_domain = $par{'custom_domain'};
	    $remotenets = 'None' if ($remotenets eq '');
	    $explicitroutes = 'None' if ($explicitroutes eq '');
	    $custom_dns = 'None' if ($par{'push_custom_dns'} eq '');
	    $custom_domain = 'None' if ($par{'push_custom_domain'} eq '');
	    $static_ip = 'None' if ($static_ip eq '');
		
		#2013-6-28
		if($par{'addresschoose'} eq 'autoset')
		{
		   $static_ip = 'None';
		}
		#

		#2013-7-19 编辑时获取旧静态IP
		my $old_ip = '';
		if($action eq 'set')
		{
		   my @tmp_users = split(/\n/, `$passwd longlist`);
		   foreach my $one (@tmp_users)
		   {
		      my @split = split(/:/,$one);
			  if($username eq $split[0])
			  {
			     $old_ip = $split[8];
				 break;
			  }
		   }
		}
		#
	    $setred = 'on';
	    $setblue = 'on';
	    $setorange = 'on';
	    $setred = 'off' if ($par{'setred'} ne 'set');
	    $setblue = 'off' if ($par{'setblue'} ne 'set');
	    $setorange = 'off' if ($par{'setorange'} ne 'set');
	    $par{'dontpushroutes'} = 'off' if ($par{'dontpushroutes'} ne 'on');

	    my $push_custom_domain = 'on';
	    my $push_custom_dns = 'on';
	    $push_custom_domain = 'off' if ($par{'push_custom_domain'} ne 'on');
	    $push_custom_dns = 'off' if ($par{'push_custom_dns'} ne 'on');

	    ($err, $errormessage) = cracklib($pass1, $pass2);
	    if ($err) {

	        $cmd = "$passwd set \"$username\" --password \"$pass1\"";
	        $cmd .= " --dns=$custom_dns";
	        $cmd .= " --domain=$custom_domain";
	        $cmd .= " --static-ips=$static_ip";
	        $cmd .= " --dont-push-routes $par{'dontpushroutes'}";
	        $cmd .= " --explicit-routes $explicitroutes";
	        $cmd .= " --networks $remotenets";
	        $cmd .= " --route-blue $setblue";
	        $cmd .= " --route-orange $setorange";
	        $cmd .= " --route-red $setred";
	        $cmd .= " --push-domain=$push_custom_domain";
	        $cmd .= " --push-dns=$push_custom_dns";

	        # kill the user in order to enforce the configuration change.
            system("$passwd kill \"$username\"");
			`sudo fcmd "$passwd kill $username"`;

            system("$cmd --rewrite-users");
			`sudo fcmd "$cmd --rewrite-users"`;
			
            if (!$par{'user_enabled'}) {
                disable_user($username);
            }
            else{
                enable_user($username);
            }
			#将静态IP加入配置文件中 2013-7-19
			if($action eq 'set')
			{
			    &rm_static($old_ip);
				&add_static($static_ip);
			}
			if($action eq 'add')
			{
			    &add_static($static_ip);
			}
            ####保存白名单文件以及上传证书
            my $add_result=&save_whitelist($action);
			if($add_result eq 'true')
			{
			   #不需要重启提示
			   #setdirty($username, $remotenets);
			}
		    #添加\设置成功后清空动作
		    $par{'ACTION'} = '';
	        $action = '';
	    }
	    return;
    }
    
    if ($action eq 'enable') {
	   if (!checkuser()) {
	      return;
	   }

	   enable_user($username);
       &enabled_whitelist($username,'enable');
	   #启用成功后清空动作
	   $par{'ACTION'} = '';
	   $action = '';
	   return;
    }
    
    if ($action eq 'disable') {
	   if (!checkuser()) {
	      return;
	   }

	   disable_user($username);
       &enabled_whitelist($username,'disable');
	   #禁用成功后清空动作
	   $par{'ACTION'} = '';
	   $action = '';
	   return;
    }

    if ($action eq 'remove') {
       
       remove_whitelist($username,$par{'status'});
       #禁用成功后清空动作
       $par{'ACTION'} = '';
       $action = '';
       return;
    }
	
	#下载用户
	if ($action eq 'download') {
	    my $file = make_module();
		if( -e "$file"){
			open(DLFILE, "<$file") || Error('open', "$file");  
			@fileholder = <DLFILE>;  
			close (DLFILE) || Error ('close', "$file"); 
			print "Content-Type:application/x-download\n";  
			print "Content-Disposition:attachment;filename=$file\n\n";
			print @fileholder;
			exit;
		}
		else{
            print "Content-type:text/html\n\n";
            print qq{<html><head><title>The file doesn't exist.</title></head><body><br/><br/>
                <br/><center><h1>The file does not exist.</h1></center></body></html>};
            exit;
		}
		#应用成功后清空动作
		$par{'ACTION'} = '';
	    $action = '';
	}
	
	if ($action eq '下载全部用户') {
	   my $file = download_all();
	   if( -e "$file"){
			open(DLFILE, "<$file") || Error('open', "$file");  
			@fileholder = <DLFILE>;  
			close (DLFILE) || Error ('close', "$file"); 
			print "Content-Type:application/x-download\n";  
			print "Content-Disposition:attachment;filename=$file\n\n";
			print @fileholder;
			exit;
		}
		else{
            print "Content-type:text/html\n\n";
            print qq{<html><head><title>The file doesn't exist.</title></head><body><br/><br/>
                <br/><center><h1>The file does not exist.</h1></center></body></html>};
            exit;
		}
	   #应用成功后清空动作
	   $par{'ACTION'} = '';
	   $action = '';
	}
	
	if ($action eq 'upload') {
	   $uploadname='temp';
	   $dir = "/tmp";
	   uploads($uploadname,$dir);
	   #应用成功后清空动作
	   $par{'ACTION'} = '';
	   $action = '';
	}
	
	#END
	
}

sub add_maohao($){
    my $line = shift;
	my $return_line;
	if(length($line)<=2)
	{
	   return $line;
	} else {
	   $return_line = substr($line,0,2);
	   $line = substr($line,2,length($line)-2);
	   do{
	      $return_line .= ":";
	      $return_line .= substr($line,0,2);
		  $line = substr($line,2,length($line)-2);
	   } while (length($line)>=2)
	}
	return $return_line;
}

sub add_static($){
    my $ip = shift;
	if($ip eq '' || $ip eq 'None')
	{
	   return;
	}
	if(!-e $static_ip_file)
	{
	   `touch $static_ip_file`;
	}
	`echo >>$static_ip_file $ip `;
}

sub rm_static($){
    my $ip = shift;
	if($ip eq '' || $ip eq 'None')
	{
	   return;
	}
	open(FILE,$static_ip_file);
	my @ips = <FILE>;
	close(FILE);
	my @new_ips;
	foreach my $one (@ips)
	{
	   #去掉尾部换行符
	   $one = nl2coma($one);
	   #
	   if($one ne $ip)
	   {
	      push(@new_ips,$one);
	   }
	}
	`rm $static_ip_file`;
	`touch $static_ip_file`;
	foreach my $one (@new_ips)
	{
	   `echo >>$static_ip_file $one`;
	}
}

sub show_upload_error(){
    if(-e $upload_error_file)
	{
	   open(FILE,$upload_error_file);
	   my @errors = <FILE>;
	   close(FILE);
	   openmybox('100%', 'left', "上传错误信息");
	   printf <<EOF
	   <table class="ruleslist" style="width:100%;">
	   <tr>
	     <td class="boldbase">错误用户名</td>
		 <td class="boldbase">错误原因</td>
	   </tr>
EOF
;
       my $i=0;
	   my $style;
       foreach my $error (@errors)
	   {
	      if($i%2)
		  {
		     $style="odd";
		  } else {
		     $style="env";
		  }
		  $i++;
	      my @split = split(/,/,$error);
		  printf <<EOF
		  <tr class="$style" >
		   <td>$split[0]</td>
		   <td>$split[1]</td>
		  </tr>
EOF
;
	   }
       printf <<EOF
	   </table>
EOF
;
	   closebox();
	   `rm $upload_error_file`;
	}
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

sub checkmyIPs($$) {
    my $ip = shift;
    my $maxcidr = shift;
    my @ips = split(/[\r\n,]/, $ip);
    my @ok = ();
    my @nok = ();

    foreach my $net (@ips) {
	next if ($net =~ /^\s*$/);
	my $ok = 0;
	my $checknet = $net;
	$checknet .= '/32' if ($checknet !~ /\//);
	eval {
	    my ($ip, $cidr) = ipv4_parse($checknet);
	    if (($cidr > 0 and $cidr < $maxcidr)||$cidr == 32) {
		push(@ok, "$ip/$cidr");
		$ok = 1;
	    }
	};
	if (! $ok) {
	    push(@nok, $net);
	}
    }
    return (join(",", @ok), join(",", @nok));
}

#给上传用户成功时使用，显示时间调整，延长为10秒
sub my_notificationbox($) {
    my $text = shift;
    my $id = shift;
    my $style = shift;
    if ($text =~ /^\s*$/) {
        return;
    }
    $id = ($id ne "") ? "id=\"$id\"" : "";
    printf <<EOF
<div id="pop-note-div">
<span><img src="/images/Emoticon.png" /> %s</span>
<br />
</div>
EOF
, $text
;

printf <<EOF
<script>
window.setTimeout(fade_out,10000);
function fade_out()
{
	\$("#pop-note-div").fadeOut("slow");
}
</script>
EOF
;
}

getcgihash(\%par);
$action = $par{'ACTION'};
$sure   = $par{'sure'};
$username = sanitize($par{'username'});
doaction();
# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------



# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------

showhttpheaders();

$extraheader .= "<script type='text/javascript'> 
  \$(document).ready(function(){
	\$('#add-div-header_upload').click(function(){
            if(\$('#add-div-content_upload').css('display')=='none')
			{
				\$('#add-div-content_upload').slideDown('1000');
				\$('#add-div-header_upload img').attr('src','/images/del.png');
			}else{
				\$('#add-div-content_upload').slideUp('1000');
				\$('#add-div-header_upload img').attr('src','/images/add.png');
			}
        });
	function upload_wait() {
	    
	}
});
 function check_upload_file() {
    var label=false;
    var file = document.getElementsByName('up_file')[0];
    if(file.value)
    {
	   var filename_splited = file.value.split('.');
	   if(filename_splited[1]=='xls')
	   {
	      label=true;
	   }
	   else
	   {
	      alert('只支持处理xls文件！');
	      label=false;
	   }
	}
    else
    {
	  alert('请选择文件');
	}
    return label;
 }
function check_search(){
   var obj = document.getElementById('search_value');
   if(obj.value=='')
   {
      alert('搜索字段不能为空！');
	  return false;
   }
   if(obj.value.length>20)
   {
	  alert('搜索字段长度不能超过20！');
      return false;
   }
   var reg = /^[_0-9a-zA-Z\\u4e00-\\u9fa5]+\$/;
   if(!reg.test(obj.value))
   {
      alert('搜索字段只支持中文英文数字及下划线，请不要输入其他字符！');
	  return false;
   }
   return true;
   
} 
</script>";

$extraheader .= "<style type='text/css'>
#add-div_upload{
width:96%;
margin:20px auto;
border:1px solid #DDD;
height:auto;
}

#add-div-header_upload{
width:100%;
padding-top:2px;
height:25px;
line-height:25px;
background-image:url(../images/con-header-bg.jpg);
border-bottom:1px solid #999;
font-size:13px;
color:#192027;
font-weight:bold;
cursor:pointer;
}

#add-div-header_upload img{
display:block;
float:left;
margin:5px 0px -5px 5px;
cursor:pointer;
}

#add-div-content_upload{
width:100%;
}

#add-div-content_upload table{
width:100%;
}

#add-div-content_upload >table>tr>td{
border-bottom:1px solid #AAA;
height:30px;
line-height:30px;
font-size:12px;
}
</style>";
openpage($name, 1,$extraheader);
&show_script();
sleep(2);
openbigbox($errormessage,"", $notemessage);
#upload上传成功使用提示框，渐变退出效果延长为10秒钟。
my_notificationbox($my_notemessage);
if (-e $dirtyfile) {
    $warnmessage = _('Configuration has been changed.You may need to restart openVPN server in order to make the changes active.Clients will reconnect automatically after the restart.');
	applybox($warnmessage);
}
#当不存在动作时默认给action赋值add
if (!$par{'ACTION'} ) {
	$action = 'add';
}
show_upload_error();
show_set($username, $action);
display_add();
list_users();
&check_form();
closebigbox();
closepage();
