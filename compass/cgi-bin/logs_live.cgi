#!/usr/bin/perl
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

require '/var/efw/header.pl';
use POSIX();
use Encode;

## defining standard variables we need
my %cgiparams;
my %logsettings;
%livelogsettings;

&getcgihash(\%cgiparams);

$logsettings{'LOGVIEW_REVERSE'} = 'off';
#2013-7-21 删除入侵防御 要时再加入下方logTypes
#'SNORT'    => { 'color' => '#ee7d67', 'string' => _('入侵防御'), 'default' => 'off' },
#
%logTypes = (
	     # 'SQUID'    => { 'color' => '#39c4f4', 'string' => _('Web proxy'), 'default' => 'off' },
		 'BACKUP'   => { 'color' => '#eebd67', 'string' => _('Backup'), 'default' => 'off' },
		 'RED' => { 'color' => '#eee367', 'string' => _('上行线路'), 'default' => 'off' },
		 'DHCPD'   => { 'color' => '#adaff1', 'string' => _('DHCP服务器'), 'default' => 'off' },
		 # 'DNSMASQ'    => { 'color' => '#c7eaa7', 'string' => _('DNS代理'), 'default' => 'off' },
		 'IPSEC'    => { 'color' => '#adf1eb', 'string' => _('IPSEC'), 'default' => 'off' },
	     'OPENVPN'  => { 'color' => '#add7f1', 'string' => _('SSLVPN'), 'default' => 'off' },
	     'FIREWALL' => { 'color' => '#d3adf1', 'string' => _('Firewall'), 'default' => 'off' },
	     'DANSGUARDIAN' => { 'color' => '#e8adf1', 'string' => _('Content filter'), 'default' => 'off' },
	     );

foreach $key (keys %logTypes) {
  $livelogsettings{'LIVE_'.$key} = $logTypes{$key}{'default'};
  $livelogsettings{$key.'_COLOR'} = $logTypes{$key}{'color'};
}
$livelogsettings{'HIGHLIGHT_COLOR'} = '#ffcc00';
$livelogsettings{'AUTOSCROLL'} = 'on';

if (-e "${swroot}/logging/default/settings") {
  &readhash("${swroot}/logging/default/settings", \%logsettings);
}
if (-e "${swroot}/logging/settings") {
  &readhash("${swroot}/logging/settings", \%logsettings);
}
if (-e "${swroot}/logging/default/live_settings") {
  &readhash("${swroot}/logging/default/live_settings", \%livelogsettings);
}
if (-e "${swroot}/logging/live_settings") {
  &readhash("${swroot}/logging/live_settings", \%livelogsettings);
}

$allowsave = 'true';
$new_window = 0;

if ($ENV{'QUERY_STRING'} ne '') {
  my @values = split(/&/,$ENV{'QUERY_STRING'});
  foreach my $i (@values) {
    my ($fieldname, $data) = split (/=/,$i);

    if ($fieldname eq 'show' && $data eq 'single') {

      $new_window = 1;

    } elsif ($fieldname eq 'showfields') {

	@types = split /,/, $data;
	my %helphash;
	foreach $field (@types) {
	    $helphash{$field} = 'on';
	}
	foreach $field (keys %logTypes) {
	    if (exists($helphash{lc($field)})) {
		$livelogsettings{'LIVE_'.$field} = 'on';
	    } else {
		$livelogsettings{'LIVE_'.$field} = 'off';
	    }
	}

    } elsif ($fieldname eq 'nosave') {

      $allowsave = 'false';

    }
  }
}

&showhttpheaders();

if ($new_window == 0) {
  &openpage(_('Firewall live log'), 1, '');
} else {
  &open_single_page();
}

&openbigbox($errormessage, $warnmessage, $notemessage);

&openbox('100%', 'left', _('实时显示设定'));

&writepage();

&closebox();

&writelogstable();

&closebigbox();

if ($new_window == 0) {
  &closepage();
} else {
  &close_single_page();
}
 
## This function writes down the table which will then be filled 
## with the log entries by our javascript
sub writelogstable () {
  my $resize = "";
  
  if ($new_window != 0) {
      $resize = sprintf <<END
            <span style="margin-top:0px;" id="resize_buttons"><button onclick="resizeLogs('shrink');">%s</button>&nbsp;&nbsp;&nbsp;&nbsp;<button onclick="resizeLogs('grow');">%s</button></span>
END
,
_('Decrease height'),
_('Increase height');
    }
    else {
        $resize = "";
    }

  printf <<END
  <h3 style="height: 24px;display:none;"><span style="float: left;">%s</span> $resize</h3>
  <div id="test" class="containter-div-header" style="width:96%;margin:10px auto 0px;">%s	  
  </div>
  <div id='live_logs_div' style="height: 455px; overflow: auto; border-bottom: solid 1px #aaa; border-left: solid 1px #aaa;">
   <center id="logs_loading" style="font-weight: bold; vertical-align: middle;" ><nowrap><img src="/images/loading.gif" alt="Loading" border="0"/> %s</nowrap></center>
   <div id="live_logs"  style="width:96%;margin:0px auto;border:1px solid gray;border-top:0px;"></div><table id='no_msg_table' style="width:96.5%;margin:0px auto;display:none"><tr class="env table_note"><td><div><img src="/images/pop_warn.png" />%s</div></td></tr></table>
  <script language="javascript" type="text/javascript">get_logs();</script>
  </div>
END
  ,
  _('Event'),
  _('实时信息'),
  _('Loading...'),
  _('Current no content')
;
}


## This function writes the configuration part of our live log viewer
sub writepage () {
  my $load_renderers = '';
  while (defined($next = </home/httpd/html/include/log_renderer_*.js>)) {
    $next =~ s/\/home\/httpd\/html//;
    $load_renderers .= "<script language='javascript' type='text/javascript' src='$next'></script>\n";
  }

  $megatable = sprintf <<END
    <link type="text/css" rel="stylesheet" href="/include/logs.css" />
    <!--[if lt IE 8]>
    <link type="text/css" rel="stylesheet" href="/include/logs_ie.css" />
    <![endif]-->
    <script language="javascript" type="text/javascript" src="/include/ajax.js"></script>
    <script language="javascript" type="text/javascript" src="/include/live_log_data.js"></script>
    %s
    <script language="javascript" type="text/javascript" src="/include/log_renderer.js"></script>
    <script language="javascript" type="text/javascript" src="/include/live_logs.js"></script>
    <script language="javascript" type="text/javascript">
    <!--
    function popupPalette(type) {
        if (document.getElementById('palette_lock').value == 'off') { 
          document.getElementById('palette_lock').value = 'on'; 
          document.getElementById('palette_type').value = type;
          showPalette(type);
        }
    }
    var log_type_names = new Array();
    -->
    </script>
	<!--此表格显示所有复选框-->
    <table  cellpadding="0" cellspacing="0" width='100%'>
		
END
,$load_renderers;
  foreach $key (sort keys %logTypes) {
      $percent = '5';
      if ($i % 5 == 0) {
          $megatable .= "<tr class='odd'>";
      } elsif ($i % 5 == 1) {
          $percent = '6';
      }
      $megatable .= sprintf <<END
          <td  id="td_%s" class="add-div-table">
	      <input type="checkbox" name="LIVE_%s" id='livelog_%s'  %s onclick='save_settings("livelog_$key")'/>
            %s
            <input type="hidden" name="%s_COLOR" id="%s_color" value="%s" />
          </td>
END
      ,
      lc($key),
      $key,
      lc($key),
      ($livelogsettings{'LIVE_'.$key} eq 'on') ? 'checked="checked"' : '',
      $logTypes{$key}{'string'},
      $key,
      lc($key),
      $livelogsettings{$key.'_COLOR'};
            
      if ($i % 5 == 4) {
	$megatable .= "</tr>";
      }
      $i++;
  }
  #2013-7-22 填补入侵防御屏蔽后的空白
  $megatable .= sprintf <<END
		    <td  id="empty" class="add-div-table">
			</td>
      <td class="add-div-table">
      </td>
      <td class="add-div-table">
      </td>
END
;
  #若恢复入侵防御请删除
  if ($i %5 != 0) {
    $megatable .= "</tr>";
  }

  printf <<END
    %s
    </table>

    <table  cellpadding="0" cellspacing="0" width='100%'>
    <tr class="odd">
      <td>%s:<input  tabindex="1" type="text" id='livelog_filter'    size="12"/></td>
      <td>%s:<input tabindex="2" type="text" id='livelog_highlight' size="12"/></td>

      <td class="hidden_class" >%s:</td>
	  <td class="hidden_class" >
		<input tabindex="3" type="text" id="livelog_filter_2" size="12" disabled="disabled"/>
	  </td>
      <td class="hidden_class">%s:</td>
      <td class="hidden_class" >
        <iframe width="80" height="42px" name="palette_frame_hl" id="palette_frame_hl" src="/palette_hl.html" marginwidth="0" marginheight="0" scrolling="no" style="position:absolute;visibility:hidden;"></iframe>
        <input type="hidden" id='hl_color' value="%s" name="HIGHLIGHT_COLOR" onchange="saveLiveLogSettings();" />
        <a href="javascript:void(0);"><img alt="%s" onclick="popupPalette('hl');" id="hl_color_preview" src="/images/null.gif" width="14px" height="14px" style="background: %s; border: solid 1px; vertical-align: middle; border-color: darkgrey;"/></a>
      </td>
      <td class="hidden_class">%s:</td>
	  <td><button id="pause_button" alttext="%s" onclick="doPause();" >%s</button></td>
      <td>%s:<input type="checkbox" id="autoscroll" %s /></td>
    </tr>
    </table>
    <div style="display:none;" align="left" id='actual' onclick="showFullOptions();">
     %s
     <center>
      <span id="toggle_visibility_link" alttext="%s">
       <u>%s</u>
      </span>
     </center>
    </div>
    </div><!-- page_container end -->

    <input type="hidden" id="livelog_reverse" value="%s"/>
    <input type="hidden" id="palette_type" value="hl" />
    <input type="hidden" id="palette_lock" value="off" />
    <input type="hidden" id="allow_save" value="%s" />
    <input type="hidden" id="paused" value="false" />
END
  ,
  $megatable,
  _('Filter'),
  _('Highlight'),
  _('Additional filter'),
  _('Highlight color'),
  $livelogsettings{'HIGHLIGHT_COLOR'},
  _('Highlight color preview'),
  $livelogsettings{'HIGHLIGHT_COLOR'},
  _('Pause output'),
  _('Continue'),
  _('暂停显示'),
  _('Autoscroll'),
  ($livelogsettings{'AUTOSCROLL'} eq 'on') ? 'checked="checked"' : '',
  #show_buttons(),
  activeLogs(),
  '<u>'._('Close').'</u>',
  _('Show more'),
  $logsettings{'LOGVIEW_REVERSE'},
  ($allowsave eq 'true') ? 'on' : 'off';
}


## Header for the separate window
sub open_single_page () {
  printf <<END
  <html>
  <head>
  <title>%s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <link rel="shortcut icon" href="/images/shortcut.ico" />
  <link rel="stylesheet" type="text/css" href="/include/style.css" />
  <link rel="stylesheet" type="text/css" href="/include/menu.css" />
  <link rel="stylesheet" type="text/css" href="/include/content.css" />
  <style type="text/css">
    body {
      background: white;
      font-size: 9px;
      font-family: tahoma, verdana, arial, sans-serif;
      margin: 10px;
      min-width: 600px;
    }
    
    td {
	font-size: 10px;
    }
  </style>
    <script language="javascript" type="text/javascript">
            function swapVisibility(id) {
                el = document.getElementById(id);
	        if(el.style.display != 'block') {
    	    	    el.style.display = 'block';
        	} else {
                    el.style.display = 'none';
	        }
	    }
    </script>
  </head>
  <body>
END
,
_('%s %s live logs', $brand, $product);
}

## Footer for the separate window
sub close_single_page() {
  printf <<END
  </body>
  </html>
END
;
}

## If the log viewer is opened in a separate window the "Open in
## new window will not be shown
sub show_buttons () {
  my $buttons = '';
  if ($new_window == 0) {
    my $new = _('Open this page in a new window');
    $buttons = "<tr><td width='100%' align='center' colspan='6' ><a href='javascript:void(0);' id='logs_window' onclick=\"window.open('/cgi-bin/logs_live.cgi?show=single','_blank','height=700,width=1000,location=no,menubar=no,scrollbars=yes');\" name='OPEN_WINDOW'>".$new."</a></td></tr>";
  } else {
    $buttons = '';
  }
  return $buttons;
}

## This function returns a string containing the list of the logTypes that will
## be shown
sub activeLogs() {
    my $activeLogs = 0;
    my $logString = '<span align="center">'._('Now showing:').'</span>';
    my $jscript = '<script type="text/javascript" language="javascript"><!--';
    
    foreach $key (sort keys %logTypes) {
        if ($livelogsettings{'LIVE_'.$key} eq 'on') {
    	    $activeLogs++;
	    $display = 'block';
	} else {
	    $display = 'none';
	}
	
	$color = $livelogsettings{$key.'_COLOR'};
	$logString .= '<span  style="display:block;background-color:'.$color.';width: 100%">'.$logTypes{$key}{'string'}.' </span>';
#2013-7-27 检测元素是否存在
	$newjs = sprintf <<END
	
if (log_colors['%s'] && document.getElementById('show_%s')) {
    document.getElementById('show_%s').style.color = log_colors['%s'];
    //document.getElementById('td_%s').style.color = log_colors['%s'];
}

log_type_names['%s'] = '%s';

END
,
$color,
#2013-7-27 修改dangerous 被屏蔽 加了lc($key),
lc($key),
#
lc($key),
$color,
lc($key),
$color,
lc($key),
(length Encode::decode_utf8($logTypes{$key}{'string'}) > 8) ? Encode::encode_utf8(substr(Encode::decode_utf8($logTypes{$key}{'string'}), 0, 8)).'..' : $logTypes{$key}{'string'};

	$jscript .= "\n".$newjs."\n";
    }
    $jscript .= "--></script>";
    $logString .= $jscript;
    
    return $logString;
}
