#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2011-07-25

require '/var/efw/header.pl';
my @total_connect;
my @tcp_connect;
my @udp_connect;
my @icmp_connect;
my @other_connect;
&validateUser();
sub show_state()
{
	&openbox('100%','left',_('Connections'));
printf <<EOF
<br />
<!--当比例图，曲线图未画出来时，显示等待界面 -->
	<div id="wait" width="100%" height="200px" align="center">
	<img src="/images/det_wait.gif" />%s
	</div>
	
	<table border="0" width="100%" id="main_table">
	<tr>
<!--此处是连接情况比例图的开始 -->
	<td width="25%" valign="top" border="1">
	<table >
	<tr height="25px"><td width="25%" class="title_td" >共计</td><td id="total" width="10%"></td><td id="totalpercent" width="45%"></td><td width="15%"></td></tr>
	<tr height="25px"><td class="title_td">TCP  </td><td id="tcp">  </td><td id="tcppercent"></td><td></td></tr>
	<tr height="25px"><td class="title_td">UDP  </td><td id="udp">  </td><td id="udppercent"></td><td></td></tr>
	<tr height="25px"><td class="title_td">ICMP </td><td id="icmp"> </td><td id="icmppercent"></td><td></td></tr>
	<tr height="25px"><td class="title_td">其他</td><td id="other"></td><td id="otherpercent"></td><td></td></tr>
	</table>
	</td>
<!--此处是连接情况比例图的结束 -->

<!--此处是连接情况曲线图的开始 -->
	<td width="75%">
	<table>
	<tr><td width="95%">
	<div id="connect_channels" ></div>
	</td><td width="50px" valign="top">
	<div class="rx-text"></div>
	</td></tr>
	</table>
	</td>
<!--此处是连接情况曲线图的结束 -->
	</tr>
	</table>
EOF
,_("Loading...")
;
&closebox();
}


sub read_count()
{
	my $count_cmd ='sudo  conntrack -L | grep -o -P "src=\S+" | sed -n "p;n"|grep -o -P "\d\S+"|sort -u > /tmp/connection_ip';
	`$count_cmd`;
}



sub show_connect()
{
printf <<END
<br />
<table class="ruleslist" cellpadding="0" cellspacing="0" width="100%" border='0'>
<tr>
			<td class="boldbase" width="20%">%s</td>
            <td class="boldbase" width="16%">%s</td>
            <td class="boldbase" width="16%">%s</td>
            <td class="boldbase" width="16%">%s</td>
            <td class="boldbase" width="16%">%s</td>
			<td class="boldbase" width="16%">%s</td>
</tr>
</table>
<table class="page-footer">
<tr>
<td>按IP筛选(源IP，目的IP) <input id="choice_by_ip" type="text" /><input type="button" value="%s" onclick="choice_by_ip()"/> </td>
<td id="error_page" ></td>
<td class="page_button"  >
<img src="/images/first-page.gif"  title="%s"   onclick="first_page()" />
<img src="/images/last-page.gif"   title="%s"   onclick="last_page()"  />
<span><b id="count_pre"></b><b id="count"></b><b id="count_las"></b></span>
<span id="pages" ></span>
<img src="/images/next-page.gif"   title="%s"   onclick="next_page()"  />
<img src="/images/end-page.gif"    title="%s"   onclick="end_page()"   />
</td>
<td><img src = "/images/refresh.png"  title="%s" id="return_td" onclick="get_connect()" class="cursor" /></td>
<td><img src="/images/cut.png"   title="%s" onclick="cut_connections()" class="cursor"/></td>
<td>%s <input id="skip_page" type="text" /><input type="button" value="%s" onclick="skip_page()"/></td>
</tr>
</table>
END
    , _('Source IP')
    , _('Connections')
    , _('TCP')
    , _('UDP')
	, _('ICMP')
    , _('OTHER')
    , _('sure')
	, _('首页')
	, _('上一页')
	, _('下一页')
	, _('末页')
	, _('Refresh')
	, _('Cut off connections')
	, _('跳转到这一页')
	, _('go')
    ;
}

&getcgihash(\%par);
&showhttpheaders();
&openpage(_('Connects'), 1, '<script language="javascript" type="text/javascript" src="/include/excanvas.js"></script><script language="javascript" type="text/javascript" src="/include/jquery.flot.js"></script><script language="javascript" src="/include/connect.js"></script>');
#&read_count();
&show_state();
&show_connect();
&closepage();

