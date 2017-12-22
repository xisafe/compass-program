#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 备份页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
# modify by:zhouyuan
# date:2011-07-14
# 修改目的 ：同一页面显示风格 
#===============================================================================

my %par  = ();
my %setting = ();
require '/var/efw/header.pl';

my $config = "/var/efw/risk/logic/config";#逻辑配置文件
my $risk_log = "/var/efw/risk/evaluation/risk_evaluation.log";
my $conffile  = "/var/efw/risk/settings";
my $snort = "/usr/local/bin/restartsnort.py";
my $enabled = "off";

sub save()
{
    if (-e $conffile) {
        readhash($conffile, \%setting);
		$enabled = $setting{"ENABLED"};
    }
	
	if ($par{'ACTION'} eq 'save') 
	{
		&readhash($conffile, \%setting);
		if($setting{'ENABLED'} eq 'on')
		{
			$setting{'ENABLED'} = 'off';
			`sudo $snort`;#关闭风险监控
		}else{
			$setting{'ENABLED'} = 'on';
			`sudo $snort -r`;#开启风险监控
		}
		&writehash($conffile, \%setting);
		`sudo fmodify $conffile`;
	}
	system("/usr/local/bin/restartsnort -f");
}


sub show_content()
{
print "<div id='monitor_content'  style='position:absolute;top:100px;left:0;width:100%;overflow:auto;'>";
if(-e $risk_log)
{
&openbox('100%','left',_('主机分类风险'));
printf <<EOF
<div id="IF_EXITS_LOG" style="height:180px;">
  <ul class="list">
  <li>
  请选择网络号：
  <select id="NET_NO">
  </select>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  请选择主机IP号:
  <select id="HOST_IP">
  </select>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  请选择风险类型:
  <select id="HOST_RISK">
  </select>
  </li>
  </ul>
   <div class="channels"  id="host_channels" style='width:90%;height:140px;float:left;margin-left:10px;'></div>
   <div class="host_type" id="host_legend" style="width:70px;height:70px;float:left;"></div>
   <div id="host_error" style="display:none">
	<table width="100%" style="height:140px;">
	<tr class="env table_note fordel"><td colspan="1">
	<div><img src="/images/pop_warn_min.png">此部门没有独立主机！</div> </td></tr>
    </table>
   </div>
</div>
EOF
;
&closebox();


&openbox('100%','left',_('主机整体风险'));
printf <<EOF
<div style="height:180px;">
  <ul class="list">
  <li>请选择网络号：
  <select id="NET_NO_ALL">
  </select>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;请选择主机IP号:<select id="HOST_IP_ALL">
  </select>

  </li>
  </ul>
  <div class="channels" id="host_all_channels" style='width:90%;height:140px;float:left;margin-left:10px;'></div>
  <div class="host_all"  id="host_all_legend" style="width:70px;height:70px;float:left;"></div>
  <div id="host_all_error" style="display:none">
	<table width="100%" style="height:140px;">
	<tr class="env table_note fordel"><td colspan="1">
	<div><img src="/images/pop_warn_min.png">此部门没有独立主机！</div> </td></tr>
    </table>
   </div>
</div>
EOF
;
&closebox();
&openbox('100%','left',_('网络分类风险'));
printf <<EOF
<div style="height:180px;">
  <ul class="list">
  <li>请选择网络号：
  <select id="NETS_NO">
  </select>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  请选择风险类型:
  <select id="NETS_RISK">
  </select>
  </li>
  </ul>
   <div class="channels" id="net_channels" style='width:90%;height:140px;float:left;margin-left:10px;'></div>
   <div class="net_type" style="width:70px;height:70px;float:left;"></div>
</div>
EOF
;
&closebox();
&openbox('100%','left',_('网络整体风险'));
printf <<EOF
<div style="height:180px;">
  <ul class="list">
  <li>请选择网络号：
  <select id="NETS_NO_ALL">
  </select>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

  </li>
  </ul>
    <div class="channels" id="net_all_channels" style='width:90%;height:140px;float:left;margin-left:10px;'></div>
	<div class="net_all"  style="width:70px;height:70px;float:left;"></div>
</div>
EOF
;
&closebox();
print "</div>";
}else{
		&note_box("当前尚无风险监控日志！");
	}
}


sub note_box($)
{
	my $note = shift;
	&openbox('100%','left',_('风险实时监控数据'));
	print "<table width=\"100%\">";
	&no_tr(1,$note);
	print "</table>";
	&closebox();
}

sub show_enabled()
{
printf <<EOF
<script type="text/javascript">
    \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('/cgi-bin/risk_monitor.cgi', SERVICE_STAT_DESCRIPTION, ajaxian_save=1, 0);
    });
</script>

<form enctype='multipart/form-data' method='post' class="service-switch-form" id="access-form" action='$ENV{'SCRIPT_NAME'}'>
<table cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td valign="top">
            <div id="access-policy" class="service-switch">
                <div><span class="title">%s</span>
                    <span class="image"><img id="on_off" class="$enabled" align="top" src="/images/switch-%s.png" alt="" border="0" onclick="location.href = location.href"/></span>
                </div>
                    <div id="access-description" class="description" %s>%s</div>
                    <div id="access-policy-hold" class="spinner working">%s</div>
                    <div class="options-container efw-form" %s>
						<div class="section first" >
							要关闭风险监控系统，使用上面的开关关闭它
							<input type="hidden" name="wantfile" value="1" />
							<input type="hidden" name="filevar" value="rules" />
							<input type='hidden' class="service-status" name='ENABLE_IDS' value='1' />
							<input type="hidden" name="ACTION" class="action" value="save" />
							<input type="hidden" name="ENABLED" value="$enabled" />
						</div>
EOF
, escape_quotes(_("正在开启风险监控，请等待...."))
, escape_quotes(_("正在关闭风险监控，请等待...."))
, escape_quotes(_("风险监控系统正在重启，请等待......"))
, _("开启风险监控"),
, $enabled,
, $enabled eq "on" ? 'style="display:none"' : '',
, _("要开启风险监控系统，点击上面按钮开启")
, _("风险监控正在被重启，请等待......"),
, $enabled eq "on" ? '' : 'style="display:none"'
;

	&show_content();

printf  <<EOF
					</div>
        </td>
    </tr>
</table>
</form>
EOF
;
}


&getcgihash(\%par);
&showhttpheaders();
my $extraheader = '<link rel="stylesheet" type="text/css" href="/include/main_risk.css">
					<script language="javascript" type="text/javascript" src="/include/excanvas.js"></script>
					<script language="javascript" type="text/javascript" src="/include/jquery.flot.js"></script>
				   <script language="javascript" type="text/javascript" src="/include/draw_monitor.js"></script>
				   <script type="text/javascript" src="/include/serviceswitch.js"></script>
				   <script type="text/javascript">var error_view; var notification_view; var warning_view; $(document).ready(function() {' .
    $hide_error . '
    notification_view = setTimeout(function() { $(\'.notification-fancy\').fadeOut(); }, 10000);
    error_view = setTimeout(function() { $(\'.error-fancy\').fadeOut(); }, 10000);
    warning_view = setTimeout(function() { $(\'.warning-fancy\').fadeOut(); }, 10000);
})</script>';

&openpage(_('风险监控'), 1, $extraheader);
&save();
if(!-e $config)
{
	&note_box("当前尚未配置逻辑资产，请到【资产管理】->【物理资产】中生成逻辑资产");
}else{
	&show_enabled();
}
&closepage();