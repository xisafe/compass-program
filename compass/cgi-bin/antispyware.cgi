#!/usr/bin/perl
#
# antispyware CGI for Endian Firewall
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
my $whitelist_file = "${swroot}/dnsmasq/blackholedns.ignore";
my $blacklist_file = "${swroot}/dnsmasq/blackholedns.custom";
my $restart     = '/usr/local/bin/restartdnsblackhole';
my $name        = _('Anti-spyware');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked', 'redirect' => 'checked');
my %frequency = ('hourly' => '', 'daily' => '', 'weekly' => '', 'monthly' => '');


# -------------------------------------------------------------
# get settings and CGI parameters
# -------------------------------------------------------------
my %confhash = ();
my $conf = \%confhash;
my $whitelist = '';
my $blacklist = '';

######zhouyuan 2011-09-27  添加帮助信息##########
my $help_hash1 = read_json("/home/httpd/help/antispyware_help.json","antispyware.cgi","代理-DNS-反间谍软件-启用","-10","10","down");

my $help_hash2 = read_json("/home/httpd/help/antispyware_help.json","antispyware.cgi","代理-DNS-反间谍软件-间谍","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/antispyware_help.json","antispyware.cgi","代理-DNS-反间谍软件-白名单列表","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/antispyware_help.json","antispyware.cgi","代理-DNS-反间谍软件-黑名单列表","-10","10","down");

my $help_hash5 = read_json("/home/httpd/help/antispyware_help.json","antispyware.cgi","代理-DNS-反间谍软件-间谍软件域名列表升级计划","-10","10","down");

#################################################



sub setfrequency() {
	$frequency{'hourly'} = '';
	$frequency{'daily'} = '';
	$frequency{'weekly'} = '';
	$frequency{'monthly'} = '';
	$frequency{$conf->{'DNSMASQ_UPDATE_SCHEDULE'}} = 'checked="checked"';
}

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

	if (-e "$whitelist_file") {
		open(FILE, "$whitelist_file");
		foreach my $line (<FILE>) {
			$whitelist .= $line;
		};
		close(FILE);
	}
	if (-e "$blacklist_file") {
		open(FILE, "$blacklist_file");
		foreach my $line (<FILE>) {
			$blacklist .= $line;
		};
		close(FILE);
	}
	setfrequency();
}


my %par;
getcgihash(\%par);

# -------------------------------------------------------------
# action to do?
# -------------------------------------------------------------

sub check($) {
	my $data = shift;
	my $ret = '';
	@temp = split(/\n/,$data);
	foreach my $item (@temp) {
		$item =~ s/^\s+//g;
		$item =~ s/\s+$//g;
		next if ($item =~ /^$/);
		if (! validdomainname($item)) {
			$errormessage = _('"%s" is no valid domain name', $item);
			return (1, $data);
		}
		$ret .= $item."\n";
	}
	return (0, $ret);
}


sub writelist($$) {
	my $file = shift;
	my $data = shift;

	open(FILE, ">$file");
	print FILE $data;
	close(FILE);
	`sudo fmodify $file`;
}

sub save() {
	if ($par{'ACTION'} ne 'save') {
		return;
	}

	my $logid = "$0 [" . scalar(localtime) . "]";
	my $needrestart = 0;
	my $err = 0;
	($err, $whitelist) = check($par{'DNSMASQ_WHITELIST'});
	return if ($err);
	$whitelist = $par{'DNSMASQ_WHITELIST'};

	($err, $blacklist) = check($par{'DNSMASQ_BLACKLIST'});
	return if ($err);
	$blacklist = $par{'DNSMASQ_BLACKLIST'};

		print STDERR "$logid: writing new configuration file\n";
		$needrestart = 1;
		$conf->{'DNSMASQ_ANTISPYWARE'} = $par{'DNSMASQ_ANTISPYWARE'};
		$conf->{'DNSMASQ_BLACKHOLE'} = $par{'DNSMASQ_BLACKHOLE'};
		$conf->{'DNSMASQ_UPDATE_SCHEDULE'} = $par{'DNSMASQ_UPDATE_SCHEDULE'};
		writehash($conffile, $conf);
		`sudo fmodify $conffile`;
		writelist($whitelist_file, $whitelist);
		writelist($blacklist_file, $blacklist);
		setfrequency();

	if ($needrestart) {
		print STDERR `$restart`; 
		print STDERR "$logid: restarting done\n";
		$notemessage = _('Changes have been saved');
	}
}

sub display() {

	printf <<EOF
<form  name="DNS_FORM"  enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
  <input type='hidden' name='ACTION' value='save' />
<table border='0' cellspacing="0" cellpadding="4">

  <tr   class="env">
	<td style="width:170px;"  class="add-div-width  need_help">%s $help_hash1</td>
	<td colspan="4">
	  <input type='checkbox' name='DNSMASQ_ANTISPYWARE' $checked{$conf->{'DNSMASQ_ANTISPYWARE'}} />
	</td>
 </tr>
 <tr class="odd">
	<td style="width:170px;"  class="add-div-width need_help">%s $help_hash2</td>
	<td colspan="4">
	  <input type='checkbox' name='DNSMASQ_BLACKHOLE' $checked{$conf->{'DNSMASQ_BLACKHOLE'}} value="redirect"/>
	</td>
  </tr>

EOF
	, _('Enabled')
	, _('Redirect requests to spyware listening post')
	, _('The Malwaredomains community constantly improves its anti-spyware rules.')

	;

	printf <<EOF

  <tr class="env">
	<td style="width:170px;"  class="add-div-width  need_help">%s $help_hash3</td>
	<td colspan="4">
	  <textarea name='DNSMASQ_WHITELIST' cols='32' rows='6' wrap='off'>$whitelist</textarea>
	</td>
</tr>
<tr class="odd">
	<td style="width:170px;"  class="add-div-width  need_help">%s $help_hash4</td>
	<td colspan="4">
	  <textarea name='DNSMASQ_BLACKLIST' cols='32' rows='6' wrap='off'>$blacklist</textarea>
	</td>
  </tr>


  <tr  class="env" style="display:none;">
	<td style="width:170px;"  class="add-div-width  need_help"><b>%s</b> $help_hash5</td>
	<td><input type="radio" name="DNSMASQ_UPDATE_SCHEDULE" $frequency{'hourly'} value="hourly"> %s </td>
	<td><input type="radio" name="DNSMASQ_UPDATE_SCHEDULE" $frequency{'daily'} value="daily"> %s </td>
	<td><input type="radio" name="DNSMASQ_UPDATE_SCHEDULE" $frequency{'weekly'} value="weekly"> %s </td>
	<td><input type="radio" name="DNSMASQ_UPDATE_SCHEDULE" $frequency{'monthly'} value="monthly"> %s </td>
  </tr>


  <tr class="table-footer">
	<td colspan="5">
	  <input class='submitbutton net_button' type='submit' name='submit' value='%s' />
	</td>
  </tr>

</table>

</form>
EOF
	, _('白名单域列表')
	, _('黑名单域列表')
	, _('Spyware domain list update schedule')
	, _('Hourly')
	, _('Daily')
	, _('Weekly')
	, _('Monthly')
	, _('Save')
	;

}

sub check_form(){
	printf <<EOF
		<script>
		var object = {
			'form_name':'DNS_FORM',
			'option':{
				'DNSMASQ_WHITELIST':{
						'type':'textarea',
						'required':'0',
						'check':'domain|',
						'ass_check':function(eve){
							var msg = "";
							var white = eve._getCURElementsByName( "DNSMASQ_WHITELIST","textarea","DNS_FORM")[0].value;
							var black = eve._getCURElementsByName( "DNSMASQ_BLACKLIST","textarea","DNS_FORM")[0].value;
								var whites = white.split("\\n");
								var blacks = black.split("\\n");
								var key = 0;
								var value = "";
								for(var i =0;i<whites.length;i++){
									if(/^\s*\$/.test(whites[i])){continue;}	
										for(var j =0;j<blacks.length;j++){
											if(/^\s*\$/.test(blacks[j])){ continue; }
											else if(whites[ i] == blacks[ j]){
												key = 1;
												value = whites[i];
											}
										}
									if(key){return value+"不能同时包含在黑白名单中!"}
								}
						}
				},
				'DNSMASQ_BLACKLIST':{
						   'type':'textarea',
						   'required':'0',
						   'check':'domain|',
							'ass_check':function(eve){
								var msg = "";
								var white = eve._getCURElementsByName( "DNSMASQ_WHITELIST","textarea","DNS_FORM")[0].value;
								var black = eve._getCURElementsByName( "DNSMASQ_BLACKLIST","textarea","DNS_FORM")[0].value;
								var whites = white.split("\\n");
								var blacks = black.split("\\n");
								var key = 0;
								var value = "";
								for(var i =0;i<whites.length;i++){
									if(/^\s*\$/.test(whites[i])){continue;}	
									for(var j =0;j<blacks.length;j++){
										if(/^\s*\$/.test(blacks[j])){ continue; }
										else if(whites[ i] == blacks[ j]){
											key = 1;
											value = whites[i];
										}
									}
									if(key){return value+"不能同时包含在黑白名单中!"}
								}
							}
				} 
		 }
}

var check = new  ChinArk_forms();
check._main(object);
//check._get_form_obj_table("DNS_FORM");

</script>
EOF
;
}

showhttpheaders();
loadconf();
save();

openpage($name, 1, '');
openbigbox($errormessage, $warnmessage, $notemessage);
openbox('100%', 'left', $name);
display();
closebox();
check_form();
closepage();

