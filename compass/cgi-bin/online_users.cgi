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
#2013-6-4 殷其雷

require '/var/efw/header.pl';

my %par;
my $action = '';
my $username = '';
my $errormessage = '';
my $search_value_offset = '';
my $passwd   = '/usr/bin/openvpn-sudo-user';
my $whitelist_file = "/var/efw/openvpn/whitelist";
my @errormessages;
my @conn;

getcgihash(\%par);
$action = $par{'ACTION'};
$username = &sanitize($par{'username'});
showhttpheaders();

my $extraheader .= "
<script type='text/javascript'>
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
   var reg = /^[._0-9a-zA-Z\\u4e00-\\u9fa5]+\$/;
   if(!reg.test(obj.value))
   {
      alert('搜索字段只支持中文英文数字下划线及IP，请不要输入其他字符！');
	  return false;
   }
   return true;
   
}
</script>";
openpage('启停服务', 1,$extraheader);
&read_conf();
&do_action();
&show_users();
closepage();

sub show_users(){
    openbox('100%', 'left', _('Connection status and control'));
    printf <<EOF
	<br />
<table class="ruleslist" style="height:30px;">
	<tr>
	    <td style="background-image: url(../images/con-header-bg.jpg);border: 1px solid #999;color: #073662;font-weight: bold;">
		  <table width="100%">
		  <tr>
		      <td style="border:0px;padding-left:30px;vertical-align:middle;">
			      <form method="post" action="$ENV{'SCRIPT_NAME'}" onsubmit="return check_search();">
				    <input style="width:240px;" type="text" maxlength="20" name="search_value" id="search_value" />
			        &nbsp;&nbsp;<input type="submit" value="搜索" />
					<label style="margin-left:10px;font-weight:normal;">(*可根据用户，备注或本次分配的地址搜索在线用户。)</label>
					<input type="hidden" name="ACTION" value="search" />
				  </form>
			  </td>
		  </tr>
		  </table>
		</td>
	</tr>
</table>
<br />
<table class="ruleslist" cellpadding="0" cellspacing="0" width="100%" border='0'>
  <tr>
    <td width="8%" class="boldbase"><b>%s</b></td>
    <td width="11%"  class="boldbase"><b>%s</b></td>
    <td width="11%" class="boldbase"><b>%s</b></td>
    <td width="16%" class="boldbase"><b>%s / %s</b></td>
    <td width="10%" class="boldbase"><b>%s</b></td>
    <td width="10%" class="boldbase"><b>%s</b></td>
	<td width="21%" class="boldbase"><b>%s</b></td>
    <td width="13%" align="center" class="boldbase"><b>%s</b></td>
  </tr>
EOF
,
_('User'),
_('本次分配的地址'),
_('本次登录的地址'),
_('RX'),
_('TX'),
_('登录时间'),
_('连接时间'),
_('备注'),
_('Cut connections')
;

	my $length = scalar(@conn);
	my $i = 0;
	my $user_name;
	#跳转页面参数控制
	my $offset;
	my $total;
	my $next;
	my $last;
	if($length >0)
	{
	   #页面参数设置并只显示当前页面20条记录
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
	   
	   my %conf;
	   my $filepath = "/var/efw/openvpn/settings";
	   readhash($filepath,\%conf);
	   my $current_type = $conf{'AUTH_TYPE'};
		
	   foreach my $line (@conn)
	   {  
	      if($i >= $start && $i < $start+20) 
		  {
	         my @split = split(/,/,$line);
	         my $oddeven = 'oodd';
	         if ($i % 2) {
	            $oddeven = 'even';
	         }
			
	         my $conntime = &human_time(time() - $split[7]);
			 my $user;
			 if($current_type eq 'cert')
			 {
			    my @users;
			    open(FILE,"/var/efw/openvpn/whitelist");
				@users = <FILE>;
				close(FILE);
				foreach my $one (@users)
				{
				   my @split_one = split(/,/,$one);
				   if($split_one[2] eq $split[1])
				   {
				      $user = $split_one[0];
					  $user_name = $split_one[2];
				   }
				}
			 } else {
	            $user = $split[1];
				$user_name = $split[1];
			 }
	         my $rx = &human_bytes($split[4]);
	         my $tx = &human_bytes($split[5]);

	         my $realip = $split[2];
	         $realip =~ s/:.*$//;

#CLIENT_LIST,r3,80.108.92.192:49542,192.168.0.180,68830,67705,Wed Feb 23 07:56:26 2005,1109141786
	         my $deal_date = deal_date($split[6]);
	         $deal_date =~s/(.*)\s(\d+):(\d+):(\d+)/$1 $2:$3:$4/;
			 
			 #备注。
			 my $whitelist_line = &read_config_line($user,$whitelist_file);
		     my @list_value = split(/,/,$whitelist_line);
		     my $comment = $list_value[5];
			 my $self = $ENV{SCRIPT_NAME};
	         printf <<EOF
             <tr class="$oddeven">
              <td>$user</td>
              <td>$split[3]</td>
              <td>$realip</td>
              <td nowrap='nowrap'>$rx / $tx</td>
              <td nowrap='nowrap'>$deal_date</td>
              <td nowrap='nowrap'>$conntime</td>
			  <td nowrap='nowrap'>$comment</td>
              <td nowrap='nowrap' style="text-align:center;">
               <form method="post" action="$self" style="display:inline;">
                <input class='submitbutton' type='image' name="submit" value="kill" src="/images/cut.png" />
                <input type="hidden" name="username" value="$user_name" />
                <input type="hidden" name="ACTION" value="kill" />
               </form>
              </td>
            </tr>
EOF
;
          }
	      $i++;
       }
	} else{
	     no_tr(8,_("Current no content"));
    }
    print '</table>';
if($length >0)
{
printf <<END
<table cellpadding="0" cellspacing="0" class="list-legend">
<tr>
        <td style="width:630px;"><b>%s</b>
        <img src='/images/cut.png' alt='%s' >
        %s
		</td>
END
,
_('Legend'),
"断开连接",
"断开连接"
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
		<td  align='right' >%s: 
		  <input type="text" SIZE="2" name='OFFSET' VALUE="$offset">
		  <input type="hidden" name="search_value_offset" value="$search_value_offset">
		</td>
		<td  align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
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
} else {
    print '</br>';
}
    closebox();
	print '</br>';
}

sub do_action(){
   my %conf;
   my $filepath = "/var/efw/openvpn/settings";
   readhash($filepath,\%conf);
   my $current_type = $conf{'AUTH_TYPE'};
   
   if($action eq 'search')
   {
      my $key = $par{'search_value'};
	  my @new_conn;
	  my $new_count=0;
	  my $count=0;
	  
	  foreach my $line (@conn)
	  {
	     my @split = split(/,/,$line);
		 
		 my $tmp_username;
		 if($current_type eq 'cert')
		 {
			my @users;
			open(FILE,"/var/efw/openvpn/whitelist");
			@users = <FILE>;
			close(FILE);
			foreach my $one (@users)
			{
				my @split_one = split(/,/,$one);
				if($split_one[2] eq $split[1])
				{
				   $tmp_username = $split_one[0];
				}
			}
		} else {
	        $tmp_username = $split[1];
	    }
		
		 my $tmp_ip = $split[3];
		 my $whitelist_line = &read_config_line($tmp_username,$whitelist_file);
		 my @list_value = split(/,/,$whitelist_line);
		 my $tmp_comments = $list_value[5];
		 if($tmp_username=~/$key/||$tmp_ip eq $key||$tmp_comments=~/$key/)
		 {
		    $new_conn[$new_count++] = $conn[$count];
		 }
		 $count++;
	  }
	  @conn = @new_conn;
	  $search_value_offset = $par{'search_value'};
   }
   
   #值不为空意为搜索到指定内容后翻页。
   if($par{'search_value_offset'} ne '')
   {
      my $key = $par{'search_value_offset'};
	  my @new_conn;
	  my $new_count=0;
	  my $count=0;
	  foreach my $line (@conn)
	  {
	     my @split = split(/,/,$line);
		 
		 my $tmp_username;
		 if($current_type eq 'cert')
		 {
			my @users;
			open(FILE,"/var/efw/openvpn/whitelist");
			@users = <FILE>;
			close(FILE);
			foreach my $one (@users)
			{
				my @split_one = split(/,/,$one);
				if($split_one[2] eq $split[1])
				{
				   $tmp_username = $split_one[0];
				}
			}
		} else {
	        $tmp_username = $split[1];
	    }
		
		 my $tmp_ip = $split[3];
		 my $whitelist_line = &read_config_line($tmp_username,$whitelist_file);
		 my @list_value = split(/,/,$whitelist_line);
		 my $tmp_comments = $list_value[5];
		 if($tmp_username=~/$key/||$tmp_ip eq $key||$tmp_comments=~/$key/)
		 {
		    $new_conn[$new_count++] = $conn[$count];
		 }
		 $count++;
	  }
	  @conn = @new_conn;
	  $search_value_offset = $par{'search_value_offset'};
   }
   
   if ($action eq 'kill') {
	if (!&checkuser()) {
	    return;
	}

	&kill_vpn($username);
	return;
    }
}

sub sanitize($) {
    my $data = shift;
    $data =~ s/\"/\\\"/;
    return $data;
}

sub checkuser() {
    if ($username !~ /^$/) {
	return 1;
    }
    $err = 0;
    $errormessage = _('Username not set.');
    return 0;
}

sub kill_vpn($) {
    my $user = shift;
    `$passwd kill \"$user\"`;
	`sudo fcmd $passwd kill "$user"`;
}

sub read_conf(){
   @conn = split(/\n/, `$passwd status`);
   my @new_conn;
   my $new_count = 0;
   foreach my $line (@conn) 
   {
	 my @split = split(/,/,$line);
	 if ($split[0] eq 'CLIENT_LIST')
	 {
	    $new_conn[$new_count++] = $line;
     }
   }
   @conn = @new_conn;
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

sub human_time($) {
    my $seconds = shift;
    use integer;

    my $days = $seconds / 86400;
    $seconds -= $days * 86400;
    my $hours = $seconds / 3600;
    $seconds -= $hours * 3600;
    my $minutes = $seconds / 60;
    $seconds -= $minutes * 60;

    my $ret = '';
    if ($days != 0) {
	$ret .= $days.'天 ';
    }
    if ($hours != 0) {
	$ret .= $hours.'小时 ';
    }
    if ($minutes != 0) {
	$ret .= $minutes.'分钟 ';
    }
    if ($ret eq '') {
	$ret = '< 1分钟';
    }
    return $ret;
}

sub shorten($) {
    my $val = shift;
    return int($val * 10) / 10;
}

sub human_bytes($) {
    my $bytes = shift;

    my $giga = $bytes / 1073741824;
    if ($giga > 1.4) {
	return shorten($giga) . ' GB';
    }
    my $mega = $bytes / 1048576;
    if ($mega > 1.4) {
	return shorten($mega) . ' MB';
    }
    my $kilo = $bytes / 1024;
    if ($kilo > 1.4) {
	return shorten($kilo) . ' KB';
    }
    return $bytes . 'b';
}