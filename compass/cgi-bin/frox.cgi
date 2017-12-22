#!/usr/bin/perl
#
# Frox CGI for Endian Firewall
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
my $conffile    = "${swroot}/frox/settings";
my $conffile2    = "${swroot}/frox/settings22";
my $conffile_default = "${swroot}/frox/default/settings";
my $conffile_path = "${swroot}/frox/";
my $conffile_default_path = "${swroot}/frox/default/";
my $enable_green_file  = "${swroot}/frox/enable_green";
my $enable_blue_file  = "${swroot}/frox/enable_blue";
my $enable_orange_file  = "${swroot}/frox/enable_orange";
my $restart     = 'sudo /usr/local/bin/restartfrox';
my $name        = _('FTP virus scanner');
my $source_bypass_file = "${swroot}/frox/source_bypass";
my $destination_bypass_file = "${swroot}/frox/destination_bypass";
my $transparent_source_bypass = '';
my $transparent_destination_bypass = '';
my $help_hash1 = read_json("/home/httpd/help/frox_help.json","frox.cgi","代理-FTP-透明Green","-10","10","down");
my $help_hash2 = read_json("/home/httpd/help/frox_help.json","frox.cgi","代理-FTP-透明Blue","-10","10","down");
my $help_hash3 = read_json("/home/httpd/help/frox_help.json","frox.cgi","代理-FTP-透明Orange","-10","10","down");
my $help_hash4 = read_json("/home/httpd/help/frox_help.json","frox.cgi","代理-FTP-记录外出连接的防火墙记录","-10","10","down");
my $help_hash5 = read_json("/home/httpd/help/frox_help.json","frox.cgi","代理-FTP-对这些来源绕过透明代理","-10","10","down");
my $help_hash6 = read_json("/home/httpd/help/frox_help.json","frox.cgi","代理-FTP-对这些目的地址绕过FTP代理","-10","10","down");
my %par;
my %confhash = ();
my $conf = \%confhash;
my $change_value = 'switch';


sub toggle_files($$) {
    my $file = shift;
    my $set = shift;
    if ($set) {
    	`touch $file`;
    	`sudo fmodify $file`;
    	return 1;
    }
    if (-e $file) {
    	unlink($file);
    	`sudo fdelete $file`;
    }
    return 0;
}

sub check_acl($) {
    my $data = shift;
    my $ret = '';
    @temp = split(/\n/,$data);
    foreach my $item (@temp) {
        $item =~ s/^\s+//g;
        $item =~ s/\s+$//g;
        next if ($item =~ /^$/);
	if (! validmac($item) && ! validipormask($item)) {
	    $errormessage = _('"%s" is no valid IP address, network or MAC address', $item);
            return (1, $data);
        }
        $ret .= ipmask_to_cidr($item)."\n";
    }
    return (0, $ret);
}

sub read_bypass(){
    if (-e "$source_bypass_file") {
        open(FILE, "$source_bypass_file");
		$transparent_source_bypass = '';
        foreach my $line (<FILE>) {
            $transparent_source_bypass .= $line;
        };
    close(FILE);
    }
    if (-e "$destination_bypass_file") {
        open(FILE, "$destination_bypass_file");
		$transparent_destination_bypass = '';
        foreach my $line (<FILE>) {
            $transparent_destination_bypass .= $line;
        };
    close(FILE);
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

sub display_edit(){
=p    
    my $selected_1;
	my $selected_2;
    if($conf->{'GREEN_ENABLED'} eq "transparent"){
	  $selected_1 = "selected";
	}
	if($conf->{'GREEN_ENABLED'} eq "untransparent"){
	  $selected_2 = "selected";
	}
=cut
    my %selected_g=();
    my %selected_o=();
    $selected_g{$conf->{'GREEN_ENABLED'}} = "selected='selected'";
    $selected_o{$conf->{'ORANGE_ENABLED'}} = "selected='selected'";
    printf <<EOF
    <!--<form  name='PROXY'  enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>-->
    <!--<input type='hidden' name='ACTION' value='save' />-->
    <table border='0' cellspacing="0" cellpadding="4">

      <tr class="env">
      <td style="width:180px;" class="add-div-width need_help">%s <font color="$colourgreen">%s区</font> $help_hash1</td>
      <td >
		  <select name='GREEN_ENABLED'>
		     <option value="transparent" $selected_g{'transparent'}>%s</option>
			 <option value="" $selected_g{''}>%s</option>
		  </select>
      </td>
EOF
,_('Enabled on')
,_('GREEN')
,_('透明')
,_('不透明')
;

    if (orange_used()) {
        printf <<EOF
        </tr><tr class="odd">
        <td class="add-div-width need_help">%s <font color="$colourorange">%s区</font> $help_hash3</td>
        <td >
          <select name='ORANGE_ENABLED'>
		     <option value="transparent" $selected_o{'transparent'}>%s</option>
			 <option value="" $selected_o{''}>%s</option>
		  </select>
        </td>
EOF
,_('Enabled on')
,_('ORANGE')
,_('透明')
,_('不透明')
;
}

        my $checked;
		if($conf->{'LOG_FIREWALL'} eq '1'){
		   $checked = 'checked';
		}
        printf <<EOF
      </tr>

    <tr class="env">
      <td class="add-div-width need_help">%s $help_hash4</td>
      <td><input type='checkbox' name='LOG_FIREWALL' $checked /></td>
    </tr>

EOF
,
_('Firewall logs outgoing connections')
;
        printf <<EOF
          <tr class="odd">
        <td class="add-div-width need_help">%s $help_hash5</td>
	    <td>
          <textarea name='TRANSPARENT_SOURCE_BYPASS' cols='32' rows='6' wrap='off'>$transparent_source_bypass</textarea>
        </td>
   
    
      </tr>
      <tr class="env">
        <td class="add-div-width need_help">%s&nbsp;$help_hash6</td>
        <td>
          <textarea name='TRANSPARENT_DESTINATION_BYPASS' cols='32' rows='6' wrap='off'>$transparent_destination_bypass</textarea>
        </td>
      </tr>
  


      <tr class="table-footer">
        <td colspan="4">
          <input class='submitbutton net_button' type='submit' name='submit' value='%s' onclick="\$('.service-switch-form').unbind('submit');change_switch_value();"/>
        </td>
      </tr>
	  <input id="switch_value" type="hidden" name="ACTION" value="$change_value" />



</table>
<!--</form>-->
EOF
, _('Bypass the transparent Proxy from Source')
, _('Bypass the transparent Proxy to Destination')
, _('Save')
;
}

sub display_switch(){
    my $frox_enabled = $conf->{'FROX_ENABLED'};
    
    printf <<END
    <script type="text/javascript">
	        \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('/cgi-bin/frox.cgi', SERVICE_STAT_DESCRIPTION);
		
    });
	function change_switch_value() {
		    \$("#switch_value").attr("value","save");
		}
    </script>
	<form name="FROX_FORM" enctype='multipart/form-data' method='post' class="service-switch-form" id="access-form" action='$ENV{'SCRIPT_NAME'}'>
        <table cellpadding="0" cellspacing="0" border="0">
	    <tr>
		    <td valign="top">
			    <div id="access-policy" class="service-switch">
				    <div  ><span class="title">%s</span>
                    <span class="image"><img class="$frox_enabled" align="absbottom" src="/images/switch-%s.png" alt="" border="0"/></span>
                </div>
					    <div id="access-description" class="description" %s>%s</div>
					    <div id="access-policy-hold" class="spinner working">%s</div>
					    <div class="options-container efw-form" %s>
						    <div class="section first" >
							    要关闭FTP代理服务，使用上面的开关关闭它
							    <input type="hidden" name="FROX_ENABLED" value="$frox_enabled" />
						    </div>
			
	
END
, escape_quotes(_("FTP服务正在启动，请等待...")),
escape_quotes(_("FTP服务正在关闭，请等待...")),
escape_quotes(_("配置已经保存，FTP服务正在重启. 请等待...")),
,_('FTP代理')
,$frox_enabled eq 'on'?'on':'off',
,$frox_enabled eq "on" ? 'style="display:none"' : '',
, _("要开启FTP代理，点击上面按钮开启")
, _("FTP代理正在被重启，请等待......"),
,$frox_enabled eq "on" ? '' : 'style="display:none"'
;
    openbox('100%', 'left', $name);
    display_edit();
    closebox();
    printf <<EOF
				    </div>
			    </div>
		    
		    </td>
	    </tr>
    </table>
	</form>
EOF
;
}

sub check_form(){

	printf <<EOF
	<script>
var object = {
       'form_name':'FROX_FORM',
       'option'   :{
                    'TRANSPARENT_SOURCE_BYPASS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|mac|',
                             },
                    'TRANSPARENT_DESTINATION_BYPASS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|mac|',
                             },
                 }
         }
	var check = new ChinArk_forms();
	//check._get_form_obj_table("FROX_FORM");
	check._main(object);
	</script>
EOF
;
}

sub readconfile(){
    if(-e $conffile){
	   readhash($conffile, $conf);
	} else {
       readhash($conffile_default, $conf);
	}
	read_bypass();
}
sub do_action(){

	#存在par{'ACTION'}则处理信息并存入配置文件。
	if ($par{'ACTION'} eq 'save') {
    	my $logid = "$0 [" . scalar(localtime) . "]";
    	my $needrestart = 0;

    	if (-e '/etc/FLASH') {
	        $flash = 1;
    	}

    	my $log = 0;
    	if ($par{'LOG_FIREWALL'} eq 'on') {
      	    $log = 1;
    	}
        else{
            $log = 0;
        }
    	#保存配置信息,文件不存在则创建。
    	my %savehash = ();
		$savehash{'FROX_ENABLED'} = "on";
		$savehash{'LOG_FIREWALL'} = $log;
		$savehash{'GREEN_ENABLED'} = $par{'GREEN_ENABLED'};
		$savehash{'ORANGE_ENABLED'} = $par{'ORANGE_ENABLED'};
		writehash($conffile,\%savehash);
		$needrestart = 1;

    	my $error = 0;
    	($error, $transparent_destination_bypass) = check_acl($par{'TRANSPARENT_DESTINATION_BYPASS'});
    	($error, $transparent_source_bypass) = check_acl($par{'TRANSPARENT_SOURCE_BYPASS'});
        
    	if (! $error) {
       		$transparent_source_bypass = uc($transparent_source_bypass);
        	$transparent_destination_bypass = uc($transparent_destination_bypass);
        	writelist($source_bypass_file, $transparent_source_bypass);
        	writelist($destination_bypass_file, $transparent_destination_bypass);   
        
        	# TODO:restart only if needed
        	$needrestart = 1 
    	}

    	if (($needrestart) and (! $error)) {
        	print STDERR `$restart --force`; 
        	print STDERR "$logid: restarting done\n";
    	}
		#保存完毕后设置当前显示值。
	  	$notemessage = "已成功保存当前修改";
	}
	
	if ($par{'ACTION'} eq 'switch') {
	   my %savehash = ();
       if (-e $conffile) {
           readhash($conffile,\%savehash);
       }
       else{
           readhash($conffile_default,\%savehash);
       }
		if($savehash{'FROX_ENABLED'} eq 'on'){
		  $savehash{'FROX_ENABLED'} = 'off';
		} else {
		  $savehash{'FROX_ENABLED'} = 'on';
		}
		writehash($conffile,\%savehash);
            print STDERR `$restart --force`; 
            print STDERR "$logid: restarting done\n";
	}


}
# -------------------------------------------------------------
# ouput page
# -------------------------------------------------------------


showhttpheaders();
getcgihash(\%par);
openpage($name, 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
#openbox('100%', 'left', "$name");
do_action();
readconfile();
&openbigbox($errormessage, $warnmessage, $notemessage);
display_switch();
#closebox();
closebigbox();
check_form();
closepage();

