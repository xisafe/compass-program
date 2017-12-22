#!/usr/bin/perl
#
# dnsmasq CGI for Endian Firewall
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

require '/var/efw/header.pl';
my $conffile    = "${swroot}/dnsmasq/settings";
my $conffile_default = "${swroot}/dnsmasq/default/settings";
my $conffile_edefault = "${swroot}/dnsmasq/default/enterprise";
my $source_bypass_file = "${swroot}/dnsmasq/source_bypass";
my $destination_bypass_file = "${swroot}/dnsmasq/destination_bypass";
my $restart     = '/usr/local/bin/restartdnsmasq';

#发改委项目-zhouyuan-2012-08-23-添加DNS代理开关#
my $enabled_dir = "/var/efw/dnsmasq/enabled";

my $name        = _('Proxy settings');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked' );

######zhouyuan 2011-09-27  添加帮助信息##########
my $help_hash1 = read_json("/home/httpd/help/dnsmasq_help.json","dnsmasq.cgi","透明LAN","-10","10","down");

my $help_hash2 = read_json("/home/httpd/help/dnsmasq_help.json","dnsmasq.cgi","透明DMZ","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/dnsmasq_help.json","dnsmasq.cgi","透明WIFI","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/dnsmasq_help.json","dnsmasq.cgi","可以通过该透明代理服务的源地址","-10","10","down");

my $help_hash5 = read_json("/home/httpd/help/dnsmasq_help.json","dnsmasq.cgi","哪些通过透明代理服务器的目的地","-10","10","down");

#################################################



# -------------------------------------------------------------
# get settings and CGI parameters
# -------------------------------------------------------------
my %confhash = ();
my $conf = \%confhash;
my $transparent_source_bypass = '';
my $transparent_destination_bypass = '';

sub loadconf() {

	if (-e $conffile_default) {
		readhash($conffile_default, $conf);
	}
	if (-e $conffile_edefault) {
		readhash($conffile_edefault, $conf);
	}
	if (-e $conffile) {
		readhash($conffile, $conf);
	}

	if (-e "$source_bypass_file") {
		open(FILE, "$source_bypass_file");
		foreach my $line (<FILE>) {
			$transparent_source_bypass .= $line;
		};
		close(FILE);
	}
	if (-e "$destination_bypass_file") {
		open(FILE, "$destination_bypass_file");
		foreach my $line (<FILE>) {
			$transparent_destination_bypass .= $line;
		};
		close(FILE);
	}

}

# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------

my $flash = 0;
my $tagdisable = '';


sub check_acl($) {
	my $data = shift;
	my $ret = '';
	my $err = 0;
	@temp = split(/\n/,$data);
	foreach my $item (@temp) {
		$item =~ s/^\s+//g;
		$item =~ s/\s+$//g;
		next if ($item =~ /^$/);
		my $old = $item;
		$item =~ s/\/0+/\//g;
		if($item=~/\/$/)
		{
			$err = 1;
			$errormessage .= _('"%s" is no valid IP address, network or MAC address', $old)."\n";
		}
		elsif (! validmac($item) && ! validipormask($item)) {
			$err = 1;
			$errormessage .= _('"%s" is no valid IP address, network or MAC address', $old)."\n";
		}
	}

	if(!$err)
	{
		foreach my $item (@temp) 
		{
			$ret .= ipmask_to_cidr($item)."\n";
		}
		return (0, $ret);
	}else{
		return (1, $ret);
	}

}

sub writelist($$) {
	my $file = shift;
	my $data = shift;

	open(FILE, ">$file");
	print FILE $data;
	close(FILE);
	`sudo fmodify $file`;
}

sub save(){
	print $par{'ACTION'};
	if ($par{'ACTION'}  eq 'saves') {
		my $logid = "$0 [" . scalar(localtime) . "]";
		my $needrestart = 0;
		print "oooo";
		my $err = 0;
		my $transparent_destination_bypass_sanitized = '';
		my $transparent_source_bypass_sanitized = '';
		$transparent_destination_bypass_sanitized = $par{'TRANSPARENT_DESTINATION_BYPASS'};
		$transparent_source_bypass_sanitized = $par{'TRANSPARENT_SOURCE_BYPASS'};
		$needrestart = 1;
		$conf->{'DNSMASQ_TRANSPARENT_GREEN'} = $par{'DNSMASQ_TRANSPARENT_GREEN'};
		$conf->{'DNSMASQ_TRANSPARENT_BLUE'} = $par{'DNSMASQ_TRANSPARENT_BLUE'};
		$conf->{'DNSMASQ_TRANSPARENT_ORANGE'} = $par{'DNSMASQ_TRANSPARENT_ORANGE'};
		writehash($conffile, $conf);
		writelist($source_bypass_file, $transparent_source_bypass_sanitized);
		writelist($destination_bypass_file, $transparent_destination_bypass_sanitized);
		$transparent_source_bypass = $transparent_source_bypass_sanitized;
		$transparent_destination_bypass = $transparent_destination_bypass_sanitized;
	}
	if ($needrestart) {
		print STDERR `$restart --force`; 
		print STDERR "$logid: restarting done\n";
		$notemessage = _('Changes have been saved');
	}
}


sub display() {
	my %selected;
	$selected{$conf->{'DNSMASQ_TRANSPARENT_GREEN'}} = "selected";
	if (!$conf->{'DNSMASQ_TRANSPARENT_GREEN'}) {
		$selected{'off'} = "selected";
	}
	printf <<EOF
<!--<form  name="DNSMASQ"  enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>-->
<input type='hidden' name='ACTION' value='saves' />
<table border='0' width="100%" cellpadding="0" cellspacing="0">

  <tr class="env">
	<td style="width:230px;" class="add-div-width need_help"><font color="$colourgreen">%s区</font> $help_hash1</td>
	<td>
	  <select name="DNSMASQ_TRANSPARENT_GREEN">
	  	<option value="on" $selected{'on'}>透明</option>
	  	<option value="" $selected{'off'}>不透明</option>
	  </select>
	</td>
  </tr>
EOF
	, $strings_zone{'GREEN'}
	;

	if (blue_used()) {
		printf <<EOF
  <tr class="odd">
	<td style="width:200px;" class="add-div-width need_help">%s <font color="$colourblue">%s</font> $help_hash3</td>
	<td>
	  <input type='checkbox' name='DNSMASQ_TRANSPARENT_BLUE' $checked{$conf->{'DNSMASQ_TRANSPARENT_BLUE'}} />
	</td>
  </tr>
EOF
		, _('Transparent on')
		, $strings_zone{'BLUE'}
		;
	}
	
    #清空变量
	$selected{'off'} = '';
	if (orange_used()) {	
		$selected{$conf->{'DNSMASQ_TRANSPARENT_ORANGE'}} = "selected";
		if (!$conf->{'DNSMASQ_TRANSPARENT_ORANGE'}) {
			$selected{'off'} = "selected";
		}
		printf <<EOF
  <tr class="env">
	<td style="width:200px;" class="add-div-width need_help"><font color="#FF9933">%s区</font> $help_hash2</td>
	<td>
	  <select name="DNSMASQ_TRANSPARENT_ORANGE">
	  	<option value="on" $selected{'on'}>透明</option>
	  	<option value="" $selected{'off'}>不透明</option>
	  </select>
	</td>
  </tr>
EOF
		, $strings_zone{'ORANGE'}
		;
	}

	printf <<EOF
  <tr class="odd">
	<td style="width:200px;" class="add-div-width need_help">%s $help_hash4</td>
	 <td >
	 <ul>
	  <li><textarea name='TRANSPARENT_SOURCE_BYPASS' cols='32' rows='6' wrap='off'>$transparent_source_bypass</textarea></li>
	  </ul>
	</td>
  </tr>
  <tr class="env">
	<td class="add-div-width need_help">%s $help_hash5</td>
	<td>
	  <ul>
	  <li><textarea name='TRANSPARENT_DESTINATION_BYPASS' cols='32' rows='6' wrap='off'>$transparent_destination_bypass</textarea></li>
	  </ul>
	</td>
  </tr>

  <tr class="table-footer">
	<td colspan="2">
	  <input class='submitbutton net_button' type='submit' name='submit' value='%s' onclick="\$('.service-switch-form').unbind('submit');" />
	</td>
  </tr>
</table>
<!--</form>-->
EOF
	, _('绕过该透明代理的源')
	, _('绕过该透明代理的目标')
	, _('Save')
	;

}


sub display_switch()
{
	my %confs =();
	readhash($enabled_dir,\%confs);
my $service_status = $confs{"ENABLED"};

printf <<END
<script type="text/javascript">
	\$(document).ready(function() {
		var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
		var sswitch = new ServiceSwitch('/cgi-bin/df.cgi', SERVICE_STAT_DESCRIPTION, ajaxian_save=1, 0);
	});
	function write(){
		\$.get('/cgi-bin/dnsmasq_back.cgi', {}, function(data){});
	}
</script>

<table cellpadding="0" cellspacing="0" border="0">
	<tr>
		<td valign="top">
			<form name="DNSMASQ" enctype='multipart/form-data' method='post' class="service-switch-form" id="access-form" action='$ENV{'SCRIPT_NAME'}'>
			<div id="access-policy" class="service-switch">
				<div><span class="title">%s</span>
					<span class="image"><img id="on_off" class="$enabled" align="top" src="/images/switch-%s.png" alt="" border="0" onclick="\$.get('/cgi-bin/dnsmasq_back.cgi', {}, function(data){location.href=location.href;})" /></span>
				</div>
					<div id="access-description" class="description" %s>%s</div>
					<div id="access-policy-hold" class="spinner working">%s</div>
					<div class="options-container efw-form" %s>
						<div class="section first" >
							要关闭DNS代理服务，使用上面的开关关闭它
							<!--<input type="hidden" name="ACTION"  value="save" />-->
							<input type="hidden" name="ENABLED" value="$service_status" />
						</div>
			
	
END
, escape_quotes(_("DNS代理配置正在被应用，请稍后...."))
,escape_quotes(_("DNS代理配置正在被关闭，请稍后...."))
,escape_quotes(_("DNS代理配置正在被重启，请稍后...."))
,_('DNS代理')
,$service_status eq 'on'?'on':'off',
,$service_status eq "on" ? 'style="display:none"' : '',
, _("要开启DNS代理，点击上面按钮开启")
, _("DNS代理正在被重启，请等待......"),
, $service_status eq "on" ? '' : 'style="display:none"'
;
openbox('100%', 'left', $name);
display();
closebox();
printf <<EOF
				</div>
			</div>
		</form>
		</td>
	</tr>
</table>
EOF
;
}


sub check_form(){
	printf <<EOF
	<script>

	var object = {
	   'form_name':'DNSMASQ',
	   'option'   :{
					'TRANSPARENT_SOURCE_BYPASS':{
							   'type':'textarea',
							   'required':'0',
							   'check':'ip|ip_mask|mac|',
							 },
					'TRANSPARENT_DESTINATION_BYPASS':{
							   'type':'textarea',
							   'required':'0',
							   'check':'ip|mac|',
							 },
				 }
		 }

var check = new  ChinArk_forms();
check._main(object);
//check._get_form_obj_table("DNSMASQ");
</script>
EOF
	;
}
my %par;
getcgihash(\%par);
showhttpheaders();
openpage($name, 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
loadconf();

if ($par{'ACTION'}  eq 'saves') {
	my $logid = "$0 [" . scalar(localtime) . "]";
	my $needrestart = 0;
	my $err = 0;
	my $transparent_destination_bypass_sanitized = '';
	my $transparent_source_bypass_sanitized = '';
	$transparent_destination_bypass_sanitized = $par{'TRANSPARENT_DESTINATION_BYPASS'};
	$transparent_source_bypass_sanitized = $par{'TRANSPARENT_SOURCE_BYPASS'};
	$needrestart = 1;
	$conf->{'DNSMASQ_TRANSPARENT_GREEN'} = $par{'DNSMASQ_TRANSPARENT_GREEN'};
	$conf->{'DNSMASQ_TRANSPARENT_BLUE'} = $par{'DNSMASQ_TRANSPARENT_BLUE'};
	$conf->{'DNSMASQ_TRANSPARENT_ORANGE'} = $par{'DNSMASQ_TRANSPARENT_ORANGE'};
	writehash($conffile, $conf);
	writelist($source_bypass_file, $transparent_source_bypass_sanitized);
	writelist($destination_bypass_file, $transparent_destination_bypass_sanitized);
	$transparent_source_bypass = $transparent_source_bypass_sanitized;
	$transparent_destination_bypass = $transparent_destination_bypass_sanitized;
	$notemessage = _('Changes have been saved');
	print STDERR `$restart --force`; 
	print STDERR "$logid: restarting done\n";
}

openbigbox($errormessage, $warnmessage, $notemessage);
display_switch();
check_form();
closebigbox();
closepage();

