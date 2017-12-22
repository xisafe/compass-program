#!/usr/bin/perl
# # CollapsedSubs: toggle_file
# P3Scan CGI for Endian Firewall
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
my $conffile    = "${swroot}/p3scan/settings";
my $conffile_default = "${swroot}/p3scan/default/settings";
my $enable_green_file  = "${swroot}/p3scan/enable_green";
my $enable_blue_file  = "${swroot}/p3scan/enable_blue";
my $enable_orange_file  = "${swroot}/p3scan/enable_orange";
my $restart     = '/usr/local/bin/restartpopscan &';
my $name        = _('email scanner (POP3)');
my %checked     = ( 0 => '', 1 => 'checked' );
my %selected_transparent    = ('transparent' => 'selected');
my %selected_untransparent    = ('untransparent' => 'selected');
my %selected_on    = ('on' => 'selected');
my %selected_off   = ('off' => 'selected');
my %par;
my %confhash = ();
my $conf = \%confhash;
my $change_value = 'switch';
my $pop_enabled;


sub toggle_file($$) {
    my $file = shift;
    my $set = shift;

    if ($set) {
        `touch $file`;
        return 1;
    }
    if (-e $file) {
        unlink($file);
    }
    return 0;
}

sub display_edit() {
  printf <<EOF
  <!--<form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>-->
    <input id="switch_value" type='hidden' name='ACTION' value='$change_value' />
    <input type='hidden' name='JUSTDELETE' value="1"/>
    <table border='0' cellspacing="0" cellpadding="4">

      <tr  class="env">
        <td style="text-indent:15px; border-right:1px solid #999; width:180px; background-color:#c7e4f4; font-weight:bold;" >%s <font color="$colourgreen">%s区</font></td>
        <td >
		  <select name='GREEN_ENABLED'>
		     <option value="transparent" $selected_transparent{$conf->{'GREEN_ENABLED'}}>%s</option>
			 <option value="untransparent" $selected_untransparent{$conf->{'GREEN_ENABLED'}}>%s</option>
		  </select>
        </td>
      </tr>
EOF
,
_('Enabled on'),
_('GREEN'),
_('透明'),
_('不透明')
;

  if (blue_used()) {
    printf <<EOF
      <tr>
        <td style="text-indent:15px; border-right:1px solid #999; width:180px; background-color:#c7e4f4; font-weight:bold;" >%s <font color="$colourblue">%s区</font>:</td>
        <td >
          <select name='BLUE_ENABLED'>
		     <option value="transparent" $selected_transparent{$conf->{'BLUE_ENABLED'}}>%s</option>
			 <option value="untransparent" $selected_untransparent{$conf->{'BLUE_ENABLED'}}>%s</option>
		  </select>
        </td>
      </tr>
EOF
,_('Enabled on'),
_('BLUE'),
_('透明'),
_('不透明')
;
}


if (orange_used()) {
    printf <<EOF
      <tr class="odd">
        <td style="text-indent:15px; border-right:1px solid #999; width:180px; background-color:#c7e4f4; font-weight:bold;">%s <font color="$colourorange">%s区</font></td>
        <td >
          <select name='ORANGE_ENABLED'>
		     <option value="transparent" $selected_transparent{$conf->{'ORANGE_ENABLED'}}>%s</option>
			 <option value="untransparent" $selected_untransparent{$conf->{'ORANGE_ENABLED'}}>%s</option>
		  </select>
        </td>
      </tr>
EOF
,_('Enabled on'),
_('ORANGE'),
_('透明'),
_('不透明')
;
}

#显示红色区
    printf <<EOF
      <tr  class="env">
        <td style="text-indent:15px; border-right:1px solid #999; width:180px; background-color:#c7e4f4; font-weight:bold;" >%s <font color="$colourred">%s区</font></td>
        <td >
		  <select name='RED_ENABLED'>
		     <option value="on" $selected_on{$conf->{'RED_ENABLED'}}>%s</option>
			 <option value="off" $selected_off{$conf->{'RED_ENABLED'}}>%s</option>
		  </select>
        </td>
      </tr>
EOF
,
_('Enabled on'),
_('RED'),
_('不透明模式'),
_('禁用')
;

    printf <<EOF
       <tr  class="env">
         <td style="text-indent:15px; border-right:1px solid #999; width:180px; background-color:#c7e4f4; font-weight:bold;">%s</td>
          <td >
            <input type='checkbox' name='CHECKVIRUS' $checked{$conf->{CHECKVIRUS}} />
          </td>
       </tr>
       <tr class="odd">
         <td style="text-indent:15px; border-right:1px solid #999; width:180px; background-color:#c7e4f4; font-weight:bold;">%s</td>
         <td ><input type='checkbox' name='CHECKSPAM' $checked{$conf->{CHECKSPAM}} /></td>
       </tr>

       <tr class="env">
         <td style="text-indent:15px; border-right:1px solid #999; width:180px; background-color:#c7e4f4; font-weight:bold;">%s</td>
         <td><input type='checkbox' name='LOG_FIREWALL' $checked{$conf->{'LOG_FIREWALL'}} /></td>
       </tr>	   

       <tr  class="table-footer">
         <td colspan="2">
          <input class='submitbutton net_button' type='submit' name='submit' value='%s' onclick="\$('.service-switch-form').unbind('submit');change_switch_value();"/>
         </td>
       </tr>
    </table>
  <!--</form>-->
EOF
,
_('Virus scanner'),
_('Spam filter'),
_('Firewall logs outgoing connections'),
_('Save')
;
    
}

sub display_switch() {
    $pop_enabled = $conf->{'POP_ENABLED'};
    printf <<END
    <script type="text/javascript">
	        \$(document).ready(function() {
        var SERVICE_STAT_DESCRIPTION = {'on' : '%s', 'off' : '%s', 'restart' : '%s'};
        var sswitch = new ServiceSwitch('/cgi-bin/p3scan.cgi', SERVICE_STAT_DESCRIPTION);
		
    });
	function change_switch_value() {
		    \$("#switch_value").attr("value","save");
		}
    </script>
	<form name="POP3_FORM" enctype='multipart/form-data' method='post' class="service-switch-form" id="access-form" action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" class="service-status" name="POP_ENABLED" value='$pop_enabled' />
        <table cellpadding="0" cellspacing="0" border="0">
	    <tr>
		    <td valign="top">
			    <div id="access-policy" class="service-switch">
				    <div  ><span class="title">%s</span>
                    <span class="image"><img class="$pop_enabled" align="absbottom" src="/images/switch-%s.png" alt="" border="0"/></span>
                </div>
					    <div id="access-description" class="description" %s>%s</div>
					    <div id="access-policy-hold" class="spinner working">%s</div>
					    <div class="options-container efw-form" %s>
						    <div class="section first" >
							    要关闭POP3扫描服务，使用上面的开关关闭它
						    </div>
			
	
END
, escape_quotes(_("POP3扫描服务正在启动，请等待...")),
escape_quotes(_("POP3扫描正在关闭，请等待...")),
escape_quotes(_("配置已经保存，POP3扫描服务正在重启. 请等待...")),
,_('POP3扫描')
,$pop_enabled eq 'on'?'on':'off',
,$pop_enabled eq "on" ? 'style="display:none"' : '',
, _("要开启POP3扫描，点击上面按钮开启"),
, _("POP3扫描正在被重启，请等待......"),
,$pop_enabled eq "on" ? '' : 'style="display:none"'
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

sub do_action() {
    if ($par{ACTION} eq 'save') {

        my $logid = "$0 [" . scalar(localtime) . "]";
        my $needrestart = 0;

        my $checkspam = 0;
        if ($par{'CHECKSPAM'} eq 'on') {
             $checkspam = 1;
        }

        my $checkvirus = 0;
        if ($par{'CHECKVIRUS'} eq 'on') {
          $checkvirus = 1;
        }

        my $log = 0;
        if ($par{'LOG_FIREWALL'} eq 'on') {
          $log = 1;
        }

        if (-e '/etc/FLASH') {
            $flash = 1;
        }
		
		#保存配置信息。
		my %savehash = ();
		$savehash{'POP_ENABLED'} = $par{'POP_ENABLED'};
		$savehash{'LOG_FIREWALL'} = $log;
		$savehash{'GREEN_ENABLED'} = $par{'GREEN_ENABLED'};
		$savehash{'ORANGE_ENABLED'} = $par{'ORANGE_ENABLED'};
		$savehash{'RED_ENABLED'} = $par{'RED_ENABLED'};
		$savehash{'BLUE_ENABLED'} = $par{'BLUE_ENABLED'};
		$savehash{'CHECKSPAM'} = $checkspam;
		$savehash{'CHECKVIRUS'} = $checkvirus;
		$savehash{'JUSTDELETE'} = $par{'JUSTDELETE'};
		writehash($conffile,\%savehash);
		$needrestart = 1;
		
		#保存完毕后设置当前显示值。
	  	$notemessage = "已成功保存当前修改";
        system("$restart");
    }
	
	if ($par{'ACTION'} eq 'switch') {
	    my %savehash = ();
		if(!(-e $conffile)) {
		   readhash($conffile_default,\%savehash);
		} else {
		   readhash($conffile,\%savehash);
		}
		if($savehash{'POP_ENABLED'} eq 'on'){
		  $savehash{'POP_ENABLED'} = 'off';
		} else {
		  $savehash{'POP_ENABLED'} = 'on';
		}
		writehash($conffile,\%savehash);
        `$restart`;
	}
}

sub readconfile() {
    if(-e $conffile){
	   readhash($conffile, $conf);
	} else {
       readhash($conffile_default, $conf);
	} 
}

showhttpheaders();

if (!defined($conf)) {
  $errormessage=_("Cannot read configuration!");
}

getcgihash(\%par);
openpage($name, 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script>');
do_action();
readconfile();
openbigbox($errormessage, $warnmessage, $notemessage);
#openbox('100%', 'left', $name);
display_switch();
#closebox();
closebigbox();
closepage();


