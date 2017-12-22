#!/usr/bin/perl

require '/var/efw/header.pl';

my $conffile         		= "${swroot}/dhcp_relay/settings";
my $conffile_dir         	= "${swroot}/dhcp_relay";
my $conffile_default 		= "${swroot}/dhcp_relay/default/settings";
my $conffile_default_dir 	= "${swroot}/dhcp_relay/default";
my $config_dir 				= "${swroot}/dhcp_relay/";
my $config 					= "${swroot}/dhcp_relay/dhcp_ip";
my $dhcpconfig				= "${swroot}/dhcp/settings";
my $needreload 				= "${swroot}/dhcp_relay/needreload";
my $notice 					= "${swroot}/dhcp_relay/notice";
my $restartdhcp_relay 		= 'sudo /usr/local/bin/restartdhcp_relay.py';
my %par;
my %settings;
my $dhcp_ips;
my $errormessage='';
my $warnmessage='';
my $notemessage='';
my $noticemessage='';
#my $noticemessage = "当前LAN/DMZ区已启用DHCP服务，请先关闭DHCP服务再进行当前操作!";

&showhttpheaders();
&getcgihash(\%par);
&make_file();
#初次加载页面的时候要读取配置信息
&read_conf();
&save();
#页面进行操作之后，同样需要读取配置信息
&read_conf();
&openpage(_('DHCP中继设置'), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
&openbigbox($errormessage, $warnmessage, $notemessage);
if (-e $notice) {
    $noticemessage = "当前LAN区已启用DHCP服务，请先关闭DHCP服务再进行当前操作!";
	&warningbox($noticemessage);
}
if (-e $needreload) {
    $warnmessage = "DHCP中继设置设置已改变，请点击应用按钮以重启DHCP中继服务！";
	applybox($warnmessage);
}
&display_switch_body();
&check_form();
&closebigbox();
&closepage();

sub save(){
    if ($par{'ACTION'} eq 'switch')
	{
		my %new_settings;
        if ( -f $conffile_default ) {
           &readhash( "$conffile_default", \%new_settings );
        }
        if ( -f $conffile ) {
           &readhash( "$conffile", \%new_settings );
        }
        $new_settings{'ENABLED'} = $par{'ENABLED'};
		if($par{'ENABLED'} eq 'on'){
			my %temp;
			if(-f $dhcpconfig){
				readhash($dhcpconfig,\%temp);
			}
			if ($temp{"ENABLE_GREEN"} eq "on") {
				$new_settings{'ENABLED'} = 'off';
				$errormessage = "当前LAN/DMZ区已启用DHCP服务，请先关闭DHCP服务再进行当前操作!";
				`touch $notice`;
			}
		}
		&writehash($conffile, \%new_settings);
		`sudo fmodify $conffile`;
		`$restartdhcp_relay`;
	}
	
	if($par{'ACTION'} eq  'notice')
	{
		`rm $notice`;
	}
    if($par{'ACTION'} eq  'apply')
	{
	    `$restartdhcp_relay`;
		`rm $needreload`;
	}
	
	if($par{'ACTION'} eq 'save')
	{
	    my $data = $par{"DHCP_IPS"};
		my %temp;
		if(-f $dhcpconfig){
			readhash($dhcpconfig,\%temp);
		}
		if ($temp{"ENABLE_GREEN"} eq "on") {
			`touch $notice`;
		}else{
			save_config_data($data);
			$notemessage = '保存成功！';
			`touch $needreload`;
		}
	}
}

sub read_conf(){
    if ( -f $conffile_default ) {
       &readhash( "$conffile_default", \%settings );
    }

    if ( -f $conffile ) {
       &readhash( "$conffile", \%settings );
    }
	&get_config_data()
}

###############################################################
	#配置文件$config = "${swroot}/dhcp_delay/settings"
	#增删改查函数  ---2013.08.20 wanglin
	#储存数据格式为192.168.9.8这样的地址，每行一个，不得重复
###############################################################
sub check_record($){
	#删除重复的ip地址
	my $data = shift;
	#去重...
	my @temp1 = split(/\n/,$data);
	my @temp2;
	foreach my $line (@temp1){
		chomp($line);
        $line =~ s/[\r\n]//g;
		
		my $i = 0;
		my $count = @temp2;
		my $existed = 0;
		for( $i = 0; $i < $count; $i++){
			if($line eq $temp2[$i]){
				$existed++;
			}
		}
		if($existed){
			$errormessage .= "存在重复的IP地址,已做去重处理";
			next;
		}
		push(@temp2, $line);
	}
	$data = '';
	foreach my $line (@temp2){
		$data .= $line."\n";
	}
	return $data;
	
}

sub save_config_data($){
    my $data = shift;
	$data = &check_record($data);
    open(FILE, ">$config");
    print FILE $data;
    close(FILE);
	`sudo fmodify $file`;
}

sub get_config_data(){
	open(FILE, "$config");
	$dhcp_ips = '';
	foreach my $line (<FILE>) {
		$dhcp_ips .= $line;
	};
    close(FILE);
}

sub make_file(){
	# $conffile         	= "${swroot}/dhcp_relay/switch_settings";
	# $conffile_dir         = "${swroot}/dhcp_relay";
	# $conffile_default 	= "${swroot}/dhcp_relay/default/switch_settings";
	# $conffile_default_dir = "${swroot}/dhcp_relay/default";
	# $config_dir 			= '/var/efw/dhcp_relay/';
	# $config 				= '/var/efw/dhcp_relay/settings';
    if(!-e $config_dir)
	{
	    `mkdir $config_dir`;
	}
	if(!-e $config)
    {
	    `touch $config`;
	}
    if(!-e $conffile_default_dir)
	{
	    `mkdir $conffile_default_dir`;
		`touch $conffile_default`;
		`echo >>$conffile_default ENABLED=off`;
	}
	if(!-e $conffile_dir)
	{
	    `mkdir $conffile_dir`;
	}
	
	if(!-e $conffile)
    {
	    `touch $conffile`;
	}
}

sub display_switch_body(){
	&read_conf();
	$service_status = $settings{'ENABLED'};
	printf <<END
	<script type="text/javascript">
		\$(document).ready(function() {
			var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
			var sswitch = new ServiceSwitch('/cgi-bin/dhcp_relay.cgi', SERVICE_STAT_DESCRIPTION);
		});
		function check_switch(){
			var status = \$(".image img").attr("class");
			if(status=='on'){
				\$("#detail").css('display','none');
			}
			if(status=='off'){
			   \$("#detail").css('display','block'); 
			}
		}
	</script>

	<div id="validation-error" class="error-fancy" style="width: 504px; display:none">
			<div class="content">
				<table cellpadding="0" cellspacing="0" border="0">
					<tr>
						<td class="sign" valign="middle"><img src="/images/bubble_red_sign.png" alt="" border="0" /></td>
						<td id="validation-error-text" class="text" valign="middle"></td>
					</tr>
				</table>
			</div>
			<div class="bottom"><img src="/images/clear.gif" width="1" height="1" alt="" border="0" /></div>
	</div>

	<form name="DHCP_FORM" enctype='multipart/form-data' class="service-switch-form" id="dhcp-form" method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" class="service-status" name="ENABLED" value="$service_status" />

	<table cellpadding="0" cellspacing="0" border="0" >
		<tr>
			<td valign="top">
				<div id="access-policy" class="service-switch">
					<div  ><span class="title">%s</span>
						<span class="image"><img class="$service_status" align="absbottom" src="/images/switch-%s.png" alt="" border="0" onclick="check_switch()";/></span>
					</div>
										<br />
						<div id="access-description" class="description" %s>%s</div>

						<div id="access-policy-hold" class="spinner working">%s</div>
						<div id="access-options" class="options-container" %s>
						要关闭DHCP中继服务，请点击上面开关关闭.
							<div class="options">
							</div>
							</div>
						</div>
					</div>
			</td>
		</tr>
	</table>
		<input type='hidden' name='ACTION' value='switch'  />
	</form>
END
	,escape_quotes("DHCP中继服务正在启动,请稍等..."),
	escape_quotes("DHCP中继服务正在关闭,请稍等..."),
	escape_quotes("配置已更改,正在重启DHCP中继服务,请稍等..."),
	'DHCP中继服务',
	$settings{'ENABLED'} eq 'on' ? 'on' : 'off',
	$settings{'ENABLED'} eq 'on' ? 'style="display:none"' : '',
	"要开启DHCP中继服务，请点击上面开关开启",
	"",
	$settings{'ENABLED'} eq 'off' || $settings{'ENABLED'} eq '' ? 'style="display:none"' : '',
	_('Save'),
;
	print "</form>\n";
	my $style;
	if($settings{'ENABLED'} eq 'on')
	{
	   $style = 'block';
	} else {
	   $style= 'none';
	}
	print "<div id='detail' style='display:$style'>";
	openbox('100%', 'left', "DHCP中继服务配置");
	&display_html();
    closebox();
	print "</div>";
}

sub check_form(){
	printf <<EOF
	<script>
		var object = {
			'form_name':'DHCP_FORM_AE',
			'option'   :{
				'DHCP_IPS':{
					'type':'text',
					'required':'1',
					'check':'ip|'
				}
            }
         }
		var check = new  ChinArk_forms();
		check._main(object);
		//check._get_form_obj_table("DHCP_FORM_AE");
	</script>
EOF
;
}

sub display_html(){
    printf <<EOF
	<form name="DHCP_FORM_AE" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
		<table border='0' cellspacing="0" cellpadding="4">
			<tr class="odd">
				<td class="add-div-width need_help">%s&nbsp</td>
				<td>
					<input type="text" name='DHCP_IPS' value='$dhcp_ips'/>
				</td>
			</tr>

			<tr class="table-footer">
				<td colspan="4">
					<input class='submitbutton net_button' type='submit' name='submit' value='%s'/>
				</td>
			</tr>
			<input id="switch_value" type="hidden" name="ACTION" value="save" />
		</table>
	</form>
EOF
	, _('LAN区DHCP服务器IP')
	, _('Save')
;
}

sub warningbox($) {
    my $text = shift;
	if ($text =~ /^\s*$/) {
        return;
    }
    printf <<EOF
	<div id="pop-notice-div">
		<span><img src="/images/pop_notice.png" /> $text</span>
		<span id="cancel">
			<form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
				<input class="net_button" type="submit" name="save" value="%s">
				<input type="hidden" name="ACTION" value="notice">
			</form>
		</span>
	</div>
EOF
	, _('sure')
;
}