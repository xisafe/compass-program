#!/usr/bin/perl

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

require 'routing.pl';

my $restartscript = "/usr/local/bin/setrouting";
#2013.12.24 重新定义应用文件，以与策略路由分开。 by wl
my $sr_needreload = "${swroot}/routing/static_routing_needreload";

my $ENABLED_PNG = '/images/on.png';
my $DISABLED_PNG = '/images/off.png';
my $EDIT_PNG = '/images/edit.png';
my $DELETE_PNG = '/images/delete.png';
my $OPTIONAL_PNG = '/images/blob.png';

my (%par,%checked,%selected);
#my $errormessage = '';

sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;

    printf <<END
    
    <table  class="ruleslist"  cellpadding="0" cellspacing="0" width='100%'>
        <tr class="table-header">    
            <td  class="boldbase" style="width:15%;">%s</td>
            <td  class="boldbase" style="width:15%;">%s</td>
            <td  class="boldbase" style="width:15%;">%s</td>
            <td  class="boldbase" style="width:10%;">Metric值</td>
            <td  class="boldbase" style="width:25%;">%s</td>
            <td  class="boldbase" style="width:20%;">%s</td>
        </tr>
END
    ,
    _('Source Network'),
    _('Destination Network'),
    _('Via Gateway'),
    _('Remark'),
    _('Actions')
    ;

    my @lines = read_config_file();

    my $j = 0;
    foreach my $thisline (@lines) {
    chomp($thisline);
    my %splitted = config_line($thisline);

    if (! $splitted{'valid'}) {
        next;
    }
    if ($splitted{'protocol'} ne "") {
        next;
    }

    my $source = value_or_nbsp($splitted{'source'});
    my $destination = value_or_nbsp($splitted{'destination'});
    if (! validipormask($destination) and ! validipormask($source)) {
        next;
    }
    $j++;
    }
    
    my $i =-1;

if($j > 0)
{
    foreach my $thisline (@lines) {
    chomp($thisline);
    my %splitted = config_line($thisline);

    if (! $splitted{'valid'}) {
        next;
    }
    
    $i++;
    
    if ($splitted{'protocol'} ne "") {
        next;
    }

    my $source = value_or_nbsp($splitted{'source'});
    my $destination = value_or_nbsp($splitted{'destination'});
    if (! validipormask($destination) and ! validipormask($source)) {
        next;
    }

    my $gw = $splitted{'gw'};
    if ($gw =~ /^UPLINK:(.*)$/) {
        my $uplink = $1;
        chomp($uplink);
        my %uplinkinfo = get_uplink_info($uplink);
        $gw = "<font color='". $zonecolors{'RED'} ."'>".$uplinkinfo{'NAME'}."</font>";
    }
    $gw = value_or_nbsp($gw);
    my $remark = value_or_nbsp($splitted{'remark'});
    my $tos = value_or_nbsp($splitted{'tos'});

    my $enabled_gif = $DISABLED_PNG;
    my $enabled_alt = _('Disabled (click to enable)');
    my $enabled_action = 'enable';
    if ($splitted{'enabled'} eq 'on') {
        $enabled_gif = $ENABLED_PNG;
        $enabled_alt = _('Enabled (click to disable)');
        $enabled_action = 'disable';
    }

    my $metric = $splitted{'metric'};

    my $bgcolor = setbgcolor($is_editing, $line, $i);

        printf <<EOF
    <tr class="$bgcolor">
        <td>$source</td>
        <td>$destination</td>
        <td>$gw</td>
        <td style="text-align:center">$metric</td>
        <td>$remark</td>
        <td class="actions" style="text-align:center">
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" ALT="$enabled_alt" />
                <input type="hidden" name="ACTION" value="$enabled_action">
                <input type="hidden" name="line" value="$i">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s" />
                <input type="hidden" name="ACTION" value="edit">
                <input type="hidden" name="line" value="$i">
            </form>
            <form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline" style="display:inline-block">
                <input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s" />
                <input type="hidden" name="ACTION" value="delete">
                <input type="hidden" name="line" value="$i">
            </form>
        </td>
    </tr>
EOF
,
_('Edit'),
_('Delete');
    }
}else{
    no_tr(6,_('Current no content'));
}

    printf <<EOF
</table>
EOF
;

if($j >0)
{
printf <<EOF
<table class="list-legend" cellpadding="0" cellspacing="0">
  <tr>
    <td class="boldbase">
      <B>%s:</B>
    </td>
    <td>&nbsp;<IMG SRC="$ENABLED_PNG" ALT="%s" /> %s<IMG SRC='$DISABLED_PNG' ALT="%s" />%s<IMG SRC="$EDIT_PNG" alt="%s" />%s<IMG SRC="$DELETE_PNG" ALT="%s" />%s</td>
  </tr>
</table>
EOF
,
_('Legend'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove')
;
}

    &closebox();
    
}

sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;
    my %config;
    my %checked;

    if (($is_editing) && ($par{'sure'} ne 'y')) {
        %config = config_line(read_config_line($line));
    }
    else {
        %config = %par;
    }
    
    my $enabled = $config{'enabled'};
    my $source = $config{'source'};
    my $destination = $config{'destination'};
    my $gateway = $config{'gw'};
    my $remark = $config{'remark'};
    my $tos = $config{'tos'};
    #===2015.02.06 added by wl===#
    my $metric = $config{'metric'};

    my $via_type = 'gw';
    my $via_type_rowspan = 2;
    my $metric_tr_class = "";
    my %selected;
    if ($gateway =~ /^UPLINK:/) {
        $via_type = 'uplink';
        $via_type_rowspan = 1;
        $metric_tr_class = "hidden";
    }

    $selected{'uplink'}{$gateway} = 'selected';
    $selected{'via_type'}{$via_type} = 'selected';

    my $action = 'add';
    my $sure = '';
    my $title = _('添加路由规则');
    my $buttontext = _('添加规则');
    if ($is_editing) {
        $action = 'edit';
        $sure = '<input type="hidden" name="sure" value="y">';
        $title = _('更新路由规则');
        $buttontext = _('更新规则');
    }
    else {
        $enabled = 'on';
    }

    $checked{'ENABLED'}{$enabled} = 'checked';

    my %foil = ();
    $foil{'value'}{'via_gw'} = 'none';
    $foil{'value'}{'via_uplink'} = 'none';
    $foil{'value'}{"via_$via_type"} = 'block';

    if($par{'ACTION'} eq 'edit' || $errormessage ne '') {
        $show = "showeditor";
    }

    &openeditorbox($title, $title, $show, "createrule", @errormessages);

    printf <<EOF
<table width="80%">
  <tr class="env">
    <td class="add-div-type" rowspan="2">%s</td>
    <td  width="20%">%s </td><td><input type="text" name="source" value="$source" />
    </td>
  </tr>
  <tr class="env">
    <td>%s </td><td><input type="text" name="destination" value="$destination" />
    </td>
  </tr>
  <tr id="route_tr" class="odd">
    <td  id="via_type_td" class="add-div-type" rowspan="$via_type_rowspan">%s *</td>
    <td>
      <select name="via_type" onchange="toggleTypes('via');toggleMetric(this);clear_gw();" onkeyup="toggleTypes('via');toggleMetric(this);"  style="display:block;float:left;margin-left:5px;width:186px">
        <option value="gw" $selected{'via_type'}{'gw'}>%s</option>
        <option value="uplink" $selected{'via_type'}{'uplink'}>%s</option>
      </select>
      </td><td>
      <div ID='via_gw_v' style='display:$foil{'value'}{'via_gw'};'>
        <input type="text" name="gw" value="$gateway" />
      </div>
      <div ID='via_uplink_v' style='display:$foil{'value'}{'via_uplink'};float:left;'>
        <select name="uplink" style="width: 139px;">
EOF
, '选择器*'
, _('Source Network')
, _('Destination Network')
, _('Route Via')
, _('Static Gateway')
, _('Uplink')
;

    foreach my $name (@{get_uplinks()}) {
        my $key = "UPLINK:$name";
        my %uplinkinfo = get_uplink_info($name);
        printf <<EOF 
                  <option value='$key' $selected{'uplink'}{$key}>$uplinkinfo{'NAME'}</option>
EOF
;
    }

    printf <<EOF
        </select>
      </div>
    </td>
  <tr id="metric_tr" class="odd $metric_tr_class">
    <td>Metric值</td>
    <td><input type="text" name="metric" value="$metric"/></td>
  </tr>
  </tr>
  <tr class="env">
    <td class="add-div-type" rowspan="1" >%s</td>
    <td  colspan="2">
      <input type="checkbox" name="enabled" value="on" $checked{'ENABLED'}{'on'}/>
    </td>
  </tr>

  <tr class="odd">
    <td class="add-div-type" rowspan="1">%s</td>
    <td colspan="2">
      <input type="text" name="remark" value="$config{'remark'}" size="52" maxlength="50" />
    </td>
  </tr>
</table>
<input type="hidden" name="ACTION" value="$action">
<input type="hidden" name="line" value="$line">
<input type="hidden" name="sure" value="y">
EOF
, _('Enabled')
, _('Remark')
;

&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

}

sub reset_values() {
    %par = ();
}

sub save() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
    if ($action eq 'apply') {
        system($setrouting);
        system($setpolicyrouting);
        `sudo fcmd $setrouting`;
        `sudo fcmd $setpolicyrouting`;
        #2013.12.24 重新定义的应用文件，以与策略路由分开。 by wl
        `rm $sr_needreload`;
        $notemessage = _("Routing rules applied successfully");
        return;
    }
    if ($action eq 'delete') {
        delete_line($par{'line'});
        reset_values();
        return;
    }

    if ($action eq 'enable') {
        if (toggle_enable($par{'line'}, 1)) {
            reset_values();
            return;
        }
    }
    if ($action eq 'disable') {
        if (toggle_enable($par{'line'}, 0)) {
            reset_values();
            return;
        }
    }

 
        # ELSE
    if (($action eq 'add') ||
        (($action eq 'edit')&&($sure eq 'y'))) {
        my $via = '';
        if ($par{'via_type'} eq 'gw') {
            $via = $par{'gw'};
            $metric = $par{'metric'};
        }
        if ($par{'via_type'} eq 'uplink') {
            $via = $par{'uplink'};
            $metric = "";
        }

        if(! ($par{'source'} or $par{'destination'})) {
            $errormessage = _('源IP及目的IP不能同时为空!');
            return;
        }

        my $enabled = $par{'enabled'};
        #===added by WangLin 2015.01.14 ===#
        if ( $enabled ne "on" ) {
            $enabled = "off";
        }
        if (save_line($par{'line'},
                  $enabled,
                  $par{'source'},
                  $par{'destination'},
                  $via,
                  $par{'remark'},
                  $par{'tos'},
                  "",
                  "",
                  "",
                  "",
                  "",
                  "",
                  $metric)) {

            reset_values();
        }
    }
}

&getcgihash(\%par);

&showhttpheaders();
my $extraheader = '<script language="JavaScript" src="/include/firewall_type.js"></script>
                   <script language="JavaScript" src="/include/routingCheck.js"></script>';
&openpage(_('Routing'), 1, $extraheader);

save();
if ($reload) {
    system("touch $sr_needreload");#2013.12.24 重新定义的应用文件，以与策略路由分开。 by wl
}

&openbigbox($errormessage, $warnmessage, $notemessage);

if (-e $sr_needreload) {#2013.12.24 重新定义的应用文件，以与策略路由分开。 by wl
    applybox(_("Routing rules have been changed and need to be applied in order to make the changes active"));
}

#&openbox('100%', 'left', _('Current routing entries'));
display_add(($par{'ACTION'} eq 'edit'), $par{'line'});
display_rules(($par{'ACTION'} eq 'edit'), $par{'line'});
#&closebox();

&closebigbox();
&closepage();
