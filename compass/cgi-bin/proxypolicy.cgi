#!/usr/bin/perl
#
# HTTP Proxy CGI for Endian Firewall
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
require '/home/httpd/cgi-bin/proxy.pl';
require '/var/efw/header.pl';
&validateUser();
my $MIME_SAVE = "";
my $is_radius = 0;
######zhouyuan 2011-09-27  添加帮助信息##########
my $help_hash8 = read_json("/home/httpd/help/proxypolicy_help.json","proxypolicy.cgi","代理-HTTP-访问策略-添加访问策略-用户代理","-50","10","down");

my $help_hash2 = read_json("/home/httpd/help/proxypolicy_help.json","proxypolicy.cgi","代理-HTTP-访问策略-添加访问策略-选择源区域","-50","10","down");

my $help_hash3 = read_json("/home/httpd/help/proxypolicy_help.json","proxypolicy.cgi","代理-HTTP-访问策略-添加访问策略-插入源的网络/IP","-50","10","down");

my $help_hash4 = read_json("/home/httpd/help/proxypolicy_help.json","proxypolicy.cgi","代理-HTTP-访问策略-添加访问策略-插入源的MAC地址","-50","10","down");

my $help_hash5 = read_json("/home/httpd/help/proxypolicy_help.json","proxypolicy.cgi","代理-HTTP-访问策略-添加访问策略-选择目标区域","-50","10","down");

my $help_hash6 = read_json("/home/httpd/help/proxypolicy_help.json","proxypolicy.cgi","代理-HTTP-访问策略-添加访问策略-插入目标网络/IP","-50","10","down");

my $help_hash7 = read_json("/home/httpd/help/proxypolicy_help.json","proxypolicy.cgi","代理-HTTP-访问策略-添加访问策略-插入域","-50","10","down");

my $help_hash9 = read_json("/home/httpd/help/proxypolicy_help.json","proxypolicy.cgi","代理-HTTP-访问策略-添加访问策略-MIME类型","-10","10","down");

###########################################################################



sub save_line_policy($$$$$$$$$$$$$$$$$$$) {
    my $line = shift;
    my $enabled = shift;
    my $policy = shift;
    my $auth = shift;
    my $auth_group = shift;
    my $auth_user = shift;
    my $time_restriction = shift;
    my $days = shift;
    my $starthour = shift;
    my $startminute = shift;
    my $stophour = shift;
    my $stopminute = shift;
    my $filtertype = shift;
    my $src_type = shift;
    my $src = shift;
    my $dst_type = shift;
    my $dst = shift;
    my $mimetypes = shift;
    my $useragents = shift;
    
    $src =~ s/\n/&/gm;
    $src =~ s/\r//gm;
    $dst =~ s/\n/&/gm; 
    $dst =~ s/\r//gm;
    if ($src_type eq "mac") {
        $src =~ s/\-/:/g;
    }
    elsif($src_type eq "zone") {
        $src =~ s/\|/&/g;
    }
    if($dst_type eq "zone") {
        $dst =~ s/\|/&/g;
    }
    
	$mimetypes =~ s/\|/&/g;
    $useragents =~ s/\|/&/g;
        
    if (! check_policy($enabled,$policy,$auth,$auth_group,$auth_user,$time_restriction,$days,$starthour,$startminute,$stophour,$stopminute,$filtertype,$src_type,$src,$dst_type,$dst,$mimetypes,$useragents)) {
        return 0;
    }

    my $tosave = create_policy($enabled,$policy,$auth,$auth_group,$auth_user,$time_restriction,$days,$starthour,$startminute,$stophour,$stopminute,$filtertype,$src_type,$src,$dst_type,$dst,$mimetypes,$useragents);
	return $tosave;
}


sub get_timeframefield_widget($$) {
    my $params_ref = shift;
    my %params = %$params_ref;
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my $selection_ref = get_field_selection($conf{starthour});
    my %selection = %$selection_ref;

    my @options = ();
    for ($i=0;$i<=23;$i++) {
        my $hour = sprintf("%02s",$i);
        push(@options, {V_VALUE => $hour, T_OPTION => $hour, V_SELECTED => $selection{$hour}});
    }
    $params{V_STARTHOURS} = \@options;
    
    my $selection_ref = get_field_selection($conf{stophour});
    my %selection = %$selection_ref;
    
    my @options = ();
    for ($i=0;$i<=23;$i++) {
        my $hour = sprintf("%02s",$i);
        push(@options, {V_VALUE => $hour, T_OPTION => $hour, V_SELECTED => $selection{$hour}});
    }
    $params{V_STOPHOURS} = \@options;
    
    my $selection_ref = get_field_selection($conf{startminute});
    my %selection = %$selection_ref;
    
    my @options = ();
    for ($i=0;$i<=59;$i++) {
        my $minute = sprintf("%02s",$i);
        push(@options, {V_VALUE => $minute, T_OPTION => $minute, V_SELECTED => $selection{$minute}});
    }
    $params{V_STARTMINUTES} = \@options;
    
    my $selection_ref = get_field_selection($conf{stopminute});
    my %selection = %$selection_ref;
    
    my @options = ();
    for ($i=0;$i<=59;$i++) {
        my $minute = sprintf("%02s",$i);
        push(@options, {V_VALUE => $minute, T_OPTION => $minute, V_SELECTED => $selection{$minute}});
    }
    $params{V_STOPMINUTES} = \@options;
    
    return get_field_widget("/usr/share/efw-gui/proxy/widgets/timeframe.pltmpl", \%params);
}

sub get_policyrules($$$$) {
    my $info_ref = shift;
    my $conf_ref = shift;
    my $id = shift;
    my $action = shift;
    
    my %info = %$info_ref;
    my %conf = %$conf_ref;
    
    $info{'id'} = $id;
    $info{'src_' . $info{src_type}} = $info{src};
    $info{'dst_' . $info{dst_type}} = $info{dst};
    
    if ($action ne "edit") {
        $info{'policy'} = "allow";
        $info{'enabled'} = "on";
        $info{'days'} = "MTWHFAS";
        $info{'starthour'} = "00";
        $info{'startminute'} = "00";
        $info{'stophour'} = "23";
        $info{'stopminute'} = "59";
    }
    $info{'days'} =~ s/|/\|/g;
	$MIME_SAVE = $info{'mimetypes'};
    $info{'mimetypes'} =~ s/&/\n/g;
    
    my $valid_zones_ref = validzones();
    my @valid_zones = @$valid_zones_ref;
    my @zones = ();
	my $zone_display;
    foreach $zone (@valid_zones) {
        if (uc($zone) eq "RED") {
            next;
        }
		if (uc($zone) eq "GREEN") {
            $zone_display = _('GREEN');
        }
		if (uc($zone) eq "ORANGE") {
            $zone_display = _('ORANGE');
        }
		if (uc($zone) eq "BLUE") {
            $zone_display = _('BLUE');
        }
        push(@zones, {V_VALUE => uc($zone), T_OPTION => uc($zone_display)});
    }
    
    my @fields = ();
    
    my %params = (
        V_NAME => "src_type", 
        V_OPTIONS => [
            {V_VALUE => "any",
            T_OPTION => "&lt;" . _("ANY") . "&gt;"},
            {V_VALUE => "zone",
             T_OPTION => _("Zone")},
            {V_VALUE => "ip",
             T_OPTION => _("Network/IP")},
            {V_VALUE => "mac",
             T_OPTION => _("MAC")},
        ],
        V_TOGGLE_ACTION => 1, 
    );
    my $src_col1 = get_selectfield_div_widget(\%params, \%info);
    
    my %params = (
        V_TOGGLE_ID => "src_type any",
        V_HIDDEN => $info{src_type} eq "" || $info{src_type} eq "any" ? 0 : 1,
        T_TEXT => _("This rule will match any source"),
    );
    my $src_col21 = get_emptyfield_div_widget(\%params);
    
    my %params = (
        V_NAME => "src_zone", 
        V_OPTIONS => \@zones,
        V_TOGGLE_ID => "src_type zone",
        V_HIDDEN => $info{src_type} eq "zone" ? 0 : 1,
        V_HELP => $help_hash2,
    );
    my $src_col22 = get_multiselectfield_div_widget(\%params, \%info);
    
    my %params = (
        V_NAME => "src_ip", 
        V_TOGGLE_ID => "src_type ip",
        V_HIDDEN => $info{src_type} eq "ip" ? 0 : 1,
		V_HELP => $help_hash3,
    );
     my $src_col23 =get_textareafield_div_widget(\%params, \%info);
    
    my %params = (
        V_NAME => "src_mac", 
        V_TOGGLE_ID => "src_type mac",
        V_HIDDEN => $info{src_type} eq "mac" ? 0 : 1,
		 V_HELP => $help_hash4,
    );
    my $src_col24 =  get_textareafield_div_widget(\%params, \%info);
    
   
    
    my %params = (
        V_TOGGLE_ID => "auth user group",
        V_HIDDEN => $info{auth} eq "none" || $info{auth} eq "" ? 1 : 0,
    );
    my $auth_col21 =  get_emptyfield_div_widget(\%params);
    
    my %params = (
        V_NAME => "time_restriction",
        T_CHECKBOX => _("enable time restrictions"),
        V_TOGGLE_ACTION => 1
    );
    my $time_col1 =  get_checkboxfield_div_widget(\%params, \%info);
    
    my @options = ();
    push(@options, {V_VALUE => "M", T_OPTION => _("Monday")});
    push(@options, {V_VALUE => "T", T_OPTION => _("Tuesday")});
    push(@options, {V_VALUE => "W", T_OPTION => _("Wednesday")});
    push(@options, {V_VALUE => "H", T_OPTION => _("Thursday")});
    push(@options, {V_VALUE => "F", T_OPTION => _("Friday")});
    push(@options, {V_VALUE => "A", T_OPTION => _("Saturday")});
    push(@options, {V_VALUE => "S", T_OPTION => _("Sunday")});
    
    my %params = (
        V_TOGGLE_ID => "time_restriction",
        V_HIDDEN => $info{time_restriction} eq "on" ? 0 : 1,
        V_NAME => "days", 
        V_OPTIONS => \@options,
    );
        my $time_col21 = get_multiselectfield_div_widget(\%params, \%info);

    my @options = ();
    my @useragents = read_config_file($useragent_file);
    my @custom_useragents = read_config_file($custom_useragent_file);
    push(@useragents, @custom_useragents);
	my %useragent_selected = (
		"MSIE" => "selected"
	
	
	);
    foreach $line (@useragents) {
        my @useragent = split(/,/, $line);
		
		if($action eq "edit")
		{

			 my @lines = read_config_file($policyrules);
			 my @temp = split(/,/,$lines[$id]);
			 my @rule = split(/&/,$temp[17]);
			 my $test = $rule[0];
			
			 my $selected = "";
			 foreach my $rules(@rule)
			 {
				
				if(@useragent[0] eq $rules)
				{
					$selected = "selected";
				}
				
			 }
			 push(@options, {V_VALUE => @useragent[0], T_OPTION => @useragent[1],V_SELECTED =>$selected});
		}else{
			my $selected = "";
			
			push(@options, {V_VALUE => @useragent[0], T_OPTION => @useragent[1],V_SELECTED =>$selected});
		}
        
    }
    
	
    my %params = (
		V_NAME => "useragents", 
        V_OPTIONS => \@options,
		V_HELP  => $help_hash8,
    );
        my $user_agent = get_multiselectfield_div_widget(\%params, \%info); 
    
    my %params = (
        V_NAME => "policy", 
        V_OPTIONS => [
            {V_VALUE => "allow",
            T_OPTION => _("Allow access")},
            {V_VALUE => "deny",
             T_OPTION => _("Deny access")},
        ],
        V_TOGGLE_ACTION => 1
    );
    my $policy_col1 =  get_selectfield_div_widget(\%params, \%info);
    
    my %params = (
        V_NAME => "enabled",
        T_CHECKBOX => _("Enable")
    );
    my $policy_enabled = get_checkboxfield_div_widget(\%params, \%info);
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();

    my %params = (
        V_NAME => "dst_type", 
        V_OPTIONS => [
            {V_VALUE => "any",
            T_OPTION => "&lt;" . _("ANY") . "&gt;"},
            {V_VALUE => "zone",
             T_OPTION => _("Zone")},
            {V_VALUE => "ip",
             T_OPTION => _("Network/IP")},
            {V_VALUE => "domain",
             T_OPTION => _("Domain")},
        ],
        V_TOGGLE_ACTION => 1,
    );
    my $dst_col1 =  get_selectfield_div_widget(\%params, \%info);
    
    my %params = (
        V_TOGGLE_ID => "dst_type any",
        V_HIDDEN => $info{dst_type} eq "" || $info{dst_type} eq "any" ? 0 : 1,
        T_TEXT => _("This rule will match any destination"),
    );
    my $dst_col21 =get_emptyfield_div_widget(\%params);
    
    my @zones = ();
	my $zone_display;
    foreach $zone (@valid_zones) {
        if (uc($zone) eq "RED") {
            next;
        }
		if (uc($zone) eq "GREEN") {
            $zone_display = _('GREEN');
        }
		if (uc($zone) eq "ORANGE") {
            $zone_display = _('ORANGE');
        }
		if (uc($zone) eq "BLUE") {
            $zone_display = _('BLUE');
        }
        push(@zones, {V_VALUE => uc($zone), T_OPTION => uc($zone_display)});
    }
    
    my %params = (
        V_NAME => "dst_zone", 
        V_OPTIONS => \@zones,
        V_TOGGLE_ID => "dst_type zone",
        V_HIDDEN => $info{dst_type} eq "zone" ? 0 : 1,
        V_HELP => $help_hash5,
    );
   my $dst_col22 = get_multiselectfield_div_widget(\%params, \%info);
    
    my %params = (
        V_NAME => "dst_ip", 
        V_TOGGLE_ID => "dst_type ip",
        V_HIDDEN => $info{dst_type} eq "ip" ? 0 : 1,
		V_HELP => $help_hash6,
    );
    my $dst_col23 = get_textareafield_div_widget(\%params, \%info);
    
    my %params = (
        V_NAME => "dst_domain", 
        V_TOGGLE_ID => "dst_type domain",
        V_HIDDEN => $info{dst_type} eq "domain" ? 0 : 1,
		V_HELP => $help_hash7,
    );
    my $dst_col24 = get_textareafield_div_widget(\%params, \%info);
    
    
    my @options = ();
    
    if ($conf{AUTH_METHOD} eq "ntlm" || $conf{AUTH_METHOD} eq "ldap") {
        @tmp_groups = `/usr/local/bin/get-groups.py`;
        for my $group (@tmp_groups) {
            if ($group =~ m/\*\*\*./) {
                next;
            }
            $group =~ s/\n//g;
            my $groupid = $group;
            $groupid =~ s/,/&/g;
            push(@options, {V_VALUE => $groupid, T_OPTION => $group});
        }
    }
    elsif ($conf{AUTH_METHOD} eq "ncsa") {
        my @groups = read_config_file($ncsagroup_file);
        
        foreach my $thisline (@groups) {
            chomp($thisline);
            my %splitted = group_line($thisline);
            push(@options, {V_VALUE => $splitted{group}, T_OPTION => $splitted{group}});
        }
    }else{
		$is_radius = 1;
	}
    
	
	 my %params;
	 if($is_radius)
	 {
	    %params = (
          V_NAME => "auth", 
          V_OPTIONS => [
            {V_VALUE => "none",
            T_OPTION => _("disabled")},
            {V_VALUE => "group",
             T_OPTION => _("启用")},
          ],
          V_TOGGLE_ACTION => 1,
      );
	}else{
		%params = (
          V_NAME => "auth", 
          V_OPTIONS => [
            {V_VALUE => "none",
            T_OPTION => _("disabled")},
            {V_VALUE => "user",
             T_OPTION => _("user based")},
            {V_VALUE => "group",
             T_OPTION => _("group based")},
          ],
          V_TOGGLE_ACTION => 1,
      );
	}
    my $auth_col1 = get_selectfield_div_widget(\%params, \%info);
	
	
    #No Connection to the ADS/LDAP Directory
	my $auth_col22 = "";
    if (scalar(@options) eq 0) {
        my $text = _("No groups available");
        if ($conf{AUTH_METHOD} eq "ntlm" || $conf{AUTH_METHOD} eq "ldap") {
            $text = _("Can´t find the AD / LDAP server.");
        }
        my %params = (
            T_LABEL => _("Allowed groups"),
			T_TEXT => $text,
            V_TOGGLE_ID => "auth group",
            V_HIDDEN => $info{auth} eq "group" ? 0 : 1,
            V_STYLE => ""
        );
        $auth_col22 = get_emptyfield_div_widget(\%params);
    }
    else {
        my %params = (
            V_NAME => "auth_group", 
            V_OPTIONS => \@options,
            V_TOGGLE_ID => "auth group",
            V_HIDDEN => $info{auth} eq "group" ? 0 : 1,
        );
        $auth_col22 = get_multiselectfield_div_widget(\%params, \%info);
    }
    
    my @options = ();
    
    if ($conf{AUTH_METHOD} eq "ntlm" || $conf{AUTH_METHOD} eq "ldap") {
        @tmp_groups = `/usr/local/bin/get-users.py`;
        for my $group (@tmp_groups) {
            if ($group =~ m/\*\*\*./) {
                next;
            }
            $group =~ s/\n//g;
            my $groupid = $group;
            $groupid =~ s/,/&/g;
            push(@options, {V_VALUE => $groupid, T_OPTION => $group});
        }
    }
    elsif ($conf{AUTH_METHOD} eq "ncsa") {
        my @users = read_config_file($ncsauser_file);
        
        foreach my $thisline (@users) {
            chomp($thisline);
            my %splitted = user_line($thisline);
            push(@options, {V_VALUE => $splitted{user}, T_OPTION => $splitted{user}});
        }
    }else{
		
	}
    
    #No Connection to the ADS/LDAP Directory
	my $author_col21 = "";
    if (scalar(@options) eq 0) {
        my $text = _("No users available");
        if ($conf{AUTH_METHOD} eq "ntlm" || $conf{AUTH_METHOD} eq "ldap") {
            $text = _("Can´t find the AD / LDAP server.");
        }
        my %params = (
	        T_LABEL => _('Allowed users'),
            T_TEXT => $text,
            V_TOGGLE_ID => "auth user",
            V_HIDDEN => $info{auth} eq "user" ? 0 : 1,
            V_STYLE => ""
        );
        $author_col21 = get_emptyfield_div_widget(\%params);
    }
    else {
        my %params = (
            V_NAME => "auth_user", 
            V_OPTIONS => \@options,
            V_TOGGLE_ID => "auth user",
            V_HIDDEN => $info{auth} eq "user" ? 0 : 1,
        );
       $author_col21 = get_multiselectfield_div_widget(\%params, \%info);
    }
    
    my %params = (
        V_TOGGLE_ID => "auth none",
        V_HIDDEN => $info{auth} eq "none" || $info{auth} eq "" ? 0 : 1,
    );
    my $author_col22 = get_emptyfield_div_widget(\%params);
        
    my %params = ();
    push(@fields, {H_FIELD => get_emptyfield_div_widget(\%params)});
    
    my %params = (
        T_LABELSTARTHOUR => _("起始小时时间点"),
        T_LABELSTARTMINUTE => _("起始分钟时间点"),
        T_LABELSTOPHOUR => _("终止小时时间点"),
        T_LABELSTOPMINUTE => _("终止分钟时间点"),
        V_TOGGLE_ID => "time_restriction",
        V_HIDDEN => $info{time_restriction} eq "on" ? 0 : 1,
    );
    my $time_col22 = get_timeframefield_widget(\%params, \%info);

    my %params = (
        V_NAME => "mimetypes", 
        V_TOGGLE_ID => "policy deny",
        V_HIDDEN => $info{policy} eq "deny" ? 0 : 1,
		V_HELP => $help_hash9,
    );
    my $policy_col21 = get_MIME();
    
    my %params = (
        V_TOGGLE_ID => "policy allow",
        V_HIDDEN => $info{policy} eq "deny" ? 1 : 0,
        V_STYLE => "",
        T_LABEL => _("Mimetypes"),
        T_TEXT => _("Only available with Deny access policies.")
    );
   my $policy_col22 = get_emptyfield_div_widget(\%params);
    
    my @options = ();
    push(@options, {V_VALUE => "none", T_OPTION => _("none")});
    my $profiles_ref = get_dg_profiles();
    my @profiles = @$profiles_ref;
    foreach my $profile (@profiles) {
        push(@options, {V_VALUE => $profile, T_OPTION => get_dg_profile_info($profile)});
    }
    push(@options, {V_VALUE => "havp", T_OPTION => _("virus detection only")});
    
    my %params = (
        V_NAME => "filtertype", 
        V_OPTIONS => \@options,
        V_TOGGLE_ACTION => 1,
        V_TOGGLE_ID => "policy allow",
        V_HIDDEN => $info{policy} eq "deny" ? 1 : 0,
    );
    my $policy_col23 =  get_selectfield_div_widget(\%params, \%info);
    
    my %params = (
        V_TOGGLE_ID => "policy deny",
        V_HIDDEN => $info{policy} eq "deny" ? 0 : 1,
    );
    push(@fields, {H_FIELD => get_emptyfield_div_widget(\%params)});
    
    my @options = ();
    my $count = line_count($policyrules);
    if ($action ne "edit") {
        $count += 1;
    }
    for (my $i = 0; $i < $count; $i++) {
        push(@options, {V_VALUE => $i, T_OPTION => $i eq 0 ? _("First position") : ($i eq ($count - 1) ? _("Last position") : _("position %s", ($i + 1)))});
    }
    
    my %params = (
        V_NAME => "id",
        V_OPTIONS => \@options
    );
    my $position_tr =  get_selectfield_div_widget(\%params, \%info);

    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    my %params = (
        H_CONTAINER => $form,
        T_ADDRULE => _("Add access policy"),
        T_SAVE => $action eq "edit" ? _("Update policy") : _("Create policy"),
        V_OPEN => $action eq "edit" ? 1 : 0,
        V_ID => $id
    );
    my $content = "";
	my $show ="";
	my $buttontext = "";
	if($action eq "edit")
	{
		$show = "showeditor";
		$buttontext =  _("Update");
	}else{
		$show = "";
		$buttontext =  _("Add")
	}
    &openeditorbox(_('Add access policy'), "", $show, "createrule", @errormessages);
	print "</form><form method='post' name='PROXY_FORM'  action='".$ENV{"SCRIPT_NAME"  }."'>";
    my @lines = read_config_file($policyrules);
    my @rows = ();
    my $num = 1;
    
    foreach my $thisline (@lines) {
        chomp($thisline);
        my %splitted = policy_line($thisline);
        my @cols = ();
        push(@cols, {V_CELL_CONTENT => $num});
        
        my $policy = "<font color='$colourred'><b>" . _("access denied") . "</b></font>";
        if($splitted{'policy'} eq "allow") {
            if($splitted{'filtertype'} eq "havp") {
                $policy = "<font color='$colourorange'><b>" . _("filter for virus") . "</b></font>";
            }
            elsif($splitted{'filtertype'} =~ /content/) {
                $policy = "<font color='$colourblue'><b>" . _("filter using '" . $splitted{'filtertype'} . "'") . "</b></font>";
            }
            else {
                $policy = "<font color='$colourgreen'><b>" . _("unfiltered access") . "</b></font>";
            }
        }
        elsif ($splitted{'mimetypes'} ne "") {
            $policy .= "<br/>" . $splitted{'mimetypes'};
            $policy =~ s/&/<br\/>/g;
        }
        push(@cols, {V_CELL_CONTENT => $policy});
        
        my $source = $splitted{'src'};
        $source =~ s/\|/<br\/>/g;
        $source =~ s/GREEN/<font color='$colourgreen'>LAN<\/font>/g;
        $source =~ s/ORANGE/<font color='$colourorange'>DMZ<\/font>/g;
        $source =~ s/BLUE/<font color='$colourblue'>WIFI<\/font>/g;
        push(@cols, {V_CELL_CONTENT => $source eq "" ? "<b>" . _("ANY") . "</b>" : $source});
        
        my $destination = $splitted{'dst'};
        $destination =~ s/\|/<br\/>/g;
        $destination =~ s/GREEN/<font color='$colourgreen'>LAN<\/font>/g;
        $destination =~ s/ORANGE/<font color='$colourorange'>DMZ<\/font>/g;
        $destination =~ s/BLUE/<font color='$colourblue'>WIFI<\/font>/g;
        push(@cols, {V_CELL_CONTENT => $destination eq "" ? "<b>" . _("ANY") . "</b>" : $destination});
        
        my $auth = _("not required");
        if ($splitted{'auth'} eq "group") {
            $auth = $splitted{'auth_group'};
            $auth =~ s/&/,/g;
            $auth =~ s/\|/<br\/>/g;
        }
        elsif ($splitted{'auth'} eq "user") {
            $auth = $splitted{'auth_user'};
            $auth =~ s/&/,/g;
            $auth =~ s/\|/<br\/>/g;
        }
        elsif ($splitted{'auth'} eq "all") {
            $auth = "<b>" . _("ALL") . "</b>";
        }
        
        push(@cols, {V_CELL_CONTENT => $auth});
        
        if ($splitted{'time_restriction'} ne "on") {
            push(@cols, {V_CELL_CONTENT => _("Always")});
        }
        else {
            my $when = _("All day long");
            if ($splitted{'starthour'} ne "00" || $splitted{'startminute'} ne "00" || $splitted{'stophour'} ne "24" || $splitted{'stopminute'} ne "00") {
                $when = $splitted{'starthour'} . ":" . $splitted{'startminute'} . "-" . $splitted{'stophour'} . ":" . $splitted{'stopminute'};
            }
            
            push(@cols, {V_CELL_CONTENT => $splitted{'days'} . "<br />" . $when});
        }
        
        my $useragents = $splitted{'useragents'};
        $useragents =~ s/\|/<br\/>/g;
        push(@cols, {V_CELL_CONTENT => $useragents eq "" ? "<b>" . _("ANY") . "</b>" : $useragents});
        
        my %params = (
            V_COLS => \@cols,
            STYLE => setbgcolor($action eq "edit" ? 1 : 0, $id, ($num - 1)),
            EDIT_ACTION => "window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=edit&ID=" . ($num - 1) . "','_self');",
            REMOVE_ACTION => "window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=remove&ID=" . ($num - 1) . "','_self');",
            UP_ACTION => "window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=up&ID=" . ($num - 1) . "','_self');",
            DOWN_ACTION => "window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=down&ID=" . ($num - 1) . "','_self');",
            ON_ACTION => $splitted{'enabled'} eq "on" ? "window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=on&ID=" . ($num - 1) . "','_self');" : 0,
            OFF_ACTION => $splitted{'enabled'} eq "on" ? 0 : "window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=off&ID=" . ($num - 1) . "','_self');",
        );
        push(@rows, \%params);
        
        $num += 1;
    }
    
    my %params = (
        V_HEADINGS => [
            {HEADING => "#"},
            {HEADING => _("Policy")},
            {HEADING => _("Source")},
            {HEADING => _("Destination")},
            {HEADING => _("Authgroup/-user")},
            {HEADING => _("时间限制")},
            {HEADING => _("Useragent")},
			{HEADING => _("Actions")},
        ],
        V_ACTIONS => 1,
        V_ROWS => \@rows,
    );

	printf <<EOF
 <table cellpadding="0" cellspacing="0" border="0">
 <tr class="env">
 <td class="add-div-table">%s*</td>
 <td>$src_col1</td>
 <td  colspan="2">$src_col21 $src_col22 $src_col23 $src_col24</td>
 </tr>
 <tr class="odd">
 <td class="add-div-table">%s*</td>
 <td>$dst_col1</td>
 <td  colspan="2">$dst_col21 $dst_col22 $dst_col23 $dst_col24</td>
 </tr>
 <tr class="env">
 <td class="add-div-table">%s</td>
EOF
,_("Source")
,_("Destination")
,_("Authentication")
;
 
 if(!$is_radius)
 {
	printf <<EOF
 <td>$auth_col1</td>
 <td colspan="2">$author_col21  $author_col22  $auth_col22 </td>
EOF
;
}else{
	printf <<EOF
 <td colspan="3">$auth_col1</td>
EOF
;

}
	printf <<EOF
 </tr>
 <tr class="odd">
 <td class="add-div-table">%s</td>
 <td width="250px">$time_col1</td>
 <td>$time_col21</td><td width="450px"> $time_col22</td>
 </tr>
 <tr class="env">
 <td class="add-div-table">%s </td>
 <td colspan="3'>$user_agent</td>
 </tr>
 <tr class="odd">
 <td class="add-div-type">%s*</td>
 <td>$policy_col1</td>
 <td>$policy_col21  $policy_col22</td>
 <td>$policy_col23</td>
 </tr>
 <tr class="env">
 <td class="add-div-type">%s</td>
 <td colspan="3">$policy_enabled</td>
 </tr>
 <tr class="odd">
 <td class="add-div-type">%s </td>
 <td colspan="3">$position_tr</td>
 </tr>
 </table>
  <input type='hidden' name='ACTION' value='$action' />
  <input type='hidden' name='sure'   value='y' />
  <input type='hidden' name='ID'   value='$id' />
EOF
,_("Time restriction")
,_("Useragents")
,_("Access policy")
,_("Policy status")
,_("Position")
;

	&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
    my $table = get_listtable_widget(\%params);
	
	print $table;
if($num >1)
{
printf <<EOF
</table>
<table class="list-legend" cellpadding="0" cellspacing="0"><tr><td><b>%s</b><img src='/images/edit.png' alt='%s' >%s<img src='/images/delete.png' alt='%s' >%s<img src='/images/stock_up-16.png' alt='%s' />%s<img src='/images/stock_down-16.png' alt='%s' />%s<img src="/images/on.png" alt='%s' />%s<img src="/images/off.png" alt='%s' />%s</td></tr></table>
EOF
,
_('Legend'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
_('Move Up'),
_('Move Up'),
_('Move Down'),
_('Move Down'),
_('Enabled (click to disable)'),
_('Enabled (click to disable)'),
_('Disabled (click to enable)'),
_('Disabled (click to enable)'),
;
}else{
	no_tr(9,_('Current no content'));

}
	print "</table>";
    $content .= "<br / ><br /><br /><br /><br />";
    return $content;
}

sub render_templates($$$$) {
    my $info_ref = shift;
    my $conf_ref = shift;
    my $id = shift;
    my $action = shift;
    
    my %info = %$info_ref;
    my %conf = %$conf_ref;
    
    print get_policyrules(\%info, \%conf, $id, $action);
}

sub validate_fields($) {
    my $params_ref = shift;
    my %params = %$params_ref;
    my $errors = "";
    
    if ($par{'src_type'} eq "ip") {
        #$errors .= validip($params{"src_ip"})?"":"插入源的IP格式错误";    
    }
    elsif ($par{'src_type'} eq "mac") {
        #$errors .= check_field("src_mac", \%params);
    }
    if ($par{'dst_type'} eq "ip") {
         #$errors .= validip($params{"dst_ip"})?"":"插入目的的IP格式错误";    
    }
    elsif ($par{'dst_type'} eq "domain") {
        #$errors .= validdomainname($params{'dst_domain'})?"":"插入目标域格式错误";
    }
    if ($par{'time_restriction'} eq "on") {
        if ($par{'days'} eq "") {
            $errors .= _("Select at least one day on which the policy should be active.") . "<br />";
        }
        if (($par{'starthour'} > $par{'stophour'}) ||
            ($par{'starthour'} eq $par{'stophour'} && $par{'startminute'} > $par{'stopminute'})) {
            $errors .= _("Start time must be earlier than stop time.") . "<br />";
        }
        elsif ($par{'starthour'} eq $par{'stophour'} && $par{'startminute'} eq $par{'stopminute'}) {
            $errors .= _("Start time must differ from stop time.") . "<br />";
        }
    }
    
    return $errors;
}

%field_definition = (
    policy => {
        label => _("Access policy"),
        required => 1},
    
    filtertype => {
        label => _("Filter profile"),
        required => 1},
    
    time_restriction => {
        label => _("Time restriction")},
    days => {
        label => _("Active days"),
        required => 1},
    
    src => {
        required => 1},
    src_type => {
        label => _("Source Type"),
        required => 1},
    src_zone => {
        label => _("Select Source Zone"),
        required =>1},
    src_ip => {
        label => _("Insert Source Network/IPs"),
        checks => ["subnet", "ip"],
        required =>1},
    src_mac => {
        label => _("Insert Source MAC Addresses"),
        checks => ["mac"],
        required =>1},
    
    dst => {
        required => 1},
    dst_type => {
        label => _("Destination Type"),
        required => 1},
    dst_zone => {
        label => _("Select Destination Zone"),
        required =>1},
    dst_ip => {
        label => _("Insert Destination Network/IPs"),
        checks => ["subnet", "ip"],
        required =>1},
    dst_domain => {
        label => _("插入域"),
        checks => ["domain", "subdomain", "hostname", "fqdn"],
        required =>1},
    
    auth => {
        label => _("Authentication")},
    auth_group => {
        label => _("Allowed Groups")},
    auth_user => {
        label => _("Allowed Users")},
    
    enabled => {
        label => _("Policy status")},
    id => {
        label => _("Position"),
        required => 1},
    
    mimetypes => {
        label => _("Mimetypes")},
    useragents => {
        label => _(" "),
        description => _("hold CTRL (CMD on mac) for multiselect or unselect")},
);

showhttpheaders();

(my $default_conf_ref, my $conf_ref) = reload_par();
my %default_conf = %$default_conf_ref;

openpage(_("HTTP Configuration"), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script><script type="text/javascript" src="/include/fields.js"></script><script type="text/javascript" src="/include/waiting.js"></script>');

my %conf = %$conf_ref;
my @checkboxes = ("enabled", "time_restriction", "check_mimetypes", "check_useragents");
my $errormessage = "";

getcgihash(\%par);

my $cgi_objekt = new CGI;
my $action = $cgi_objekt->param('ACTION');
my $id = $cgi_objekt->param('ID');

my %info = ();

if ( $par{ACTION} eq 'add' ) {
    $par{'days'} =~ s/\|//g;
    if ($par{'src_type'} eq "zone") {
        $par{'src'} = $par{'src_zone'};
    }
    elsif ($par{'src_type'} eq "ip") {
        $par{'src'} = $par{'src_ip'};
    }
    elsif ($par{'src_type'} eq "mac") {
        $par{'src'} = $par{'src_mac'};
    }
    if ($par{'dst_type'} eq "zone") {
        $par{'dst'} = $par{'dst_zone'};
    }
    elsif ($par{'dst_type'} eq "ip") {
        $par{'dst'} = $par{'dst_ip'};
    }
    elsif ($par{'dst_type'} eq "domain") {
        $par{'dst'} = $par{'dst_domain'};
    }
	$par{'mimetypes'} =~ s/\|/&/g;
    $errormessage = validate_fields(\%par);
    if ($errormessage ne "") {
        %info = %par;
        $action = "edit";
    }
    else {
        my $success = save_policy(
            $par{'ID'},
            $par{'enabled'},
            $par{'policy'},
            $par{'auth'},
            $par{'auth_group'},
            $par{'auth_user'},
            $par{'time_restriction'},
            $par{'days'},
            $par{'starthour'},
            $par{'startminute'},
            $par{'stophour'},
            $par{'stopminute'},
            $par{'filtertype'},
            $par{'src_type'},
            $par{'src'},
            $par{'dst_type'},
            $par{'dst'},
            $par{'mimetypes'},
            $par{'useragents'}
        );
        
        if ($success eq 1) {
            my $oldid = $par{'ID'};
            if ($oldid !~ /^\d+$/) {
                $oldid = line_count($policyrules) - 1;
            }
			set_policy_position($oldid, $par{'id'});
        }
        
        system("touch $proxyreload");
		$notemessage = _("policy added successfully");
    }
}

my $sure = $cgi_objekt->param('sure');
if ($action eq "edit" && %info == ()) {
    %info = policy_line(read_config_line($id, $policyrules));
	$info{'src'} =~ s/GREEN/LAN/g;
	if($sure eq "y")
	{
		$par{'days'} =~ s/\|//g;
		if ($par{'src_type'} eq "zone") {
			$par{'src'} = $par{'src_zone'};
		}elsif ($par{'src_type'} eq "ip") {
			$par{'src'} = $par{'src_ip'};
		}elsif ($par{'src_type'} eq "mac") {
			$par{'src'} = $par{'src_mac'};
		}
		
		if ($par{'dst_type'} eq "zone") {
			$par{'dst'} = $par{'dst_zone'};
		}elsif ($par{'dst_type'} eq "ip") {
			$par{'dst'} = $par{'dst_ip'};
		}elsif ($par{'dst_type'} eq "domain") {
			$par{'dst'} = $par{'dst_domain'};
		}
		
		$errormessage = validate_fields(\%par);
	if($errormessage eq "")
	{
	my $new_str = save_line_policy($id,
            $par{'enabled'},
            $par{'policy'},
            $par{'auth'},
            $par{'auth_group'},
            $par{'auth_user'},
            $par{'time_restriction'},
            $par{'days'},
            $par{'starthour'},
            $par{'startminute'},
            $par{'stophour'},
            $par{'stopminute'},
            $par{'filtertype'},
            $par{'src_type'},
            $par{'src'},
            $par{'dst_type'},
            $par{'dst'},
            $par{'mimetypes'},
            $par{'useragents'}
			);
		my @lines = read_config_file($policyrules);

		@lines[$id] = $new_str;
		my $str = "";
		foreach my $line(@lines)
		{
			$str .= $line."\n";
		}
		open (FILE, ">$policyrules");
		print FILE $str;
		close (FILE);	
        my $oldid = $par{'ID'};
        set_policy_position($id, $par{'id'});
		$notemessage = _("policy changed successfully");
		}
	}
}
elsif ($action eq "remove") {
    delete_line($id, $policyrules);
    system("touch $proxyreload");
	$notemessage = _("policy remove successfully");
	$action = "add";
}
elsif ($action eq "on" or $action eq "off") {
	if($action eq "on")
	{
		$notemessage = _("policy off successfully");
	}else{
		$notemessage = _("policy on successfully");
	}
    toggle_policy($id, $action eq "on" ? 0 : 1);
    system("touch $proxyreload");
	$action = "add";
}
elsif ($action eq "up" or $action eq "down") {
    move_policy($id, $action eq "up" ? -1 : 1);
    system("touch $proxyreload");
	$notemessage = _("policy ".$action." successfully");
	$action = "add";
}
elsif ($par{'ACTION'} eq 'apply'){
    &log(_('Apply proxy settings'));
    applyaction();
	$action = "add";
}

#2012-09-7-zhouyuan-bug776-mime 类型限制#
sub get_MIME(){
	my $mime_str = `cat /var/efw/httpd/MIME`;
	my %mime_hash =();
	my @mime_ary = split( "\n",$mime_str );
	foreach my $line( @mime_ary ){
		if( $line=~/^([a-zA-Z])/){
			if($mime_hash{$1}){
				my $temp = $mime_hash{$1};
				my @temp = @$temp;
				push(@temp,$line);
				$mime_hash{$1} = \@temp;
			}
			else{ my @temp;
				  $temp[0]=$line;
				  $mime_hash{$1} = \@temp;
		    }
		}
	}
	my @mime = split("&",$MIME_SAVE);
    my %checked;
	my %mime_hash_save = ();
	foreach my $mimes(@mime){
        $checked{$mimes} = "checked";
	}
	my $new_str = "";
	if($MIME_SAVE){
   		$new_str .="<div id='mimetypes_field' class='deny policy'";
	}else{ 
        $new_str .="<div id='mimetypes_field' class='deny policy hidden'";
	}
   $new_str .= "style='overflow-y:auto;overflow-x:hidden;top:25px;";
   $new_str .= "background:#fff;height:200px;border:1px solid #999;'>";

	foreach my $key(sort keys %mime_hash ){
		$new_str .= "<div style='width:96%;clear:both;padding-top:3px;";
		$new_str .= "border-bottom:1px solid green;'>";
		$new_str .= "<b class='note' style='width:28px;height:28px;";
		$new_str .= "float:left;font-size:25px;'>".$key."</b>";
		$new_str .= "<div style='float:right;width:88%;padding:3px;'>";
		my $temp = $mime_hash{$key};
		my @temp = @$temp;
		foreach my $lines(@temp){
			if($lines =~ /^([a-zA-Z]+)\s+(.+)$/){
		    	$new_str .= "<span style='width:370px;float:left;margin-left:5px;'>";
                $new_str .= "<input  $checked{$2} name='mimetypes' class='MIME_OPTION' type='checkbox' value=$2 />";
		    	$new_str .=  "  ".$2." </span>";
		   }
		}
		$new_str .= "</div></div><div style='clear:both'></div>";
	}
	$new_str .="</div>";
	return $new_str;
	
}

sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'PROXY_FORM',
       'option'   :{
                    'src_zone':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'dst_zone':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'auth_user':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'auth_group':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'days':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'starthour':{
                               'type':'select-one',
                               'required':'1',
							   'ass_check':function(eve){
									var msg = "";
									var starthour = parseInt(eve._getCURElementsByName("starthour","select","PROXY_FORM")[0].value);
									var startminute = parseInt(eve._getCURElementsByName("startminute","select","PROXY_FORM")[0].value);
									var stophour = parseInt(eve._getCURElementsByName("stophour","select","PROXY_FORM")[0].value);
									var stopminute = parseInt(eve._getCURElementsByName("stopminute","select","PROXY_FORM")[0].value);
									 if(starthour>stophour){
										 msg = "起始小时应该小于等于结束小时";
								     }
									 return msg;
								}
                             },
                    'startminute':{
                               'type':'select-one',
                               'required':'1',
                               'ass_check':function(eve){
									var msg = "";
									var starthour = parseInt(eve._getCURElementsByName("starthour","select","PROXY_FORM")[0].value);
                            		var starthour = parseInt(eve._getCURElementsByName("starthour","select","PROXY_FORM")[0].value);
									var startminute = parseInt(eve._getCURElementsByName("startminute","select","PROXY_FORM")[0].value);
									var stophour = parseInt(eve._getCURElementsByName("stophour","select","PROXY_FORM")[0].value);
									var stopminute = parseInt(eve._getCURElementsByName("stopminute","select","PROXY_FORM")[0].value);
									 if(starthour == stophour && startminute >= stopminute){
										 msg = "起始分钟应该小于等于结束分钟";
								     }
									 return msg;
                                }
                             },
                    'stophour':{
                               'type':'select-one',
                               'required':'1',
                               'ass_check':function(eve){
									var msg = "";
									var starthour = parseInt(eve._getCURElementsByName("starthour","select","PROXY_FORM")[0].value);
									var starthour = parseInt(eve._getCURElementsByName("starthour","select","PROXY_FORM")[0].value);
									var startminute = parseInt(eve._getCURElementsByName("startminute","select","PROXY_FORM")[0].value);
									var stophour = parseInt(eve._getCURElementsByName("stophour","select","PROXY_FORM")[0].value);
									var stopminute = parseInt(eve._getCURElementsByName("stopminute","select","PROXY_FORM")[0].value);
									 if(starthour>stophour){
										 msg = "起始小时应该小于等于结束小时";
								     }
									 return msg;
                                }
                             },
                    'stopminute':{
                               'type':'select-one',
                               'required':'1',
                               'ass_check':function(eve){
									var msg = "";
									var starthour = parseInt(eve._getCURElementsByName("starthour","select","PROXY_FORM")[0].value);
                            		var starthour = parseInt(eve._getCURElementsByName("starthour","select","PROXY_FORM")[0].value);
									var startminute = parseInt(eve._getCURElementsByName("startminute","select","PROXY_FORM")[0].value);
									var stophour = parseInt(eve._getCURElementsByName("stophour","select","PROXY_FORM")[0].value);
									var stopminute = parseInt(eve._getCURElementsByName("stopminute","select","PROXY_FORM")[0].value);
									 if(starthour == stophour && startminute >= stopminute){
										 msg = "起始分钟应该小于等于结束分钟";
								     }
									 return msg;
                                }
                             },
                    'useragents':{
                               'type':'select-multiple',
                               'required':'0',
                             },
                    'src_ip':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|ip_mask|',
                             },
                    'src_mac':{
                               'type':'textarea',
                               'required':'0',
                               'check':'mac|',
                             },
                    'dst_ip':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|ip_mask|',
                             },
                    'dst_domain':{
                               'type':'textarea',
                               'required':'0',
                               'check':'domain|',
                             },
                 }
         }
    var check = new ChinArk_forms();
	 //check._get_form_obj_table("PROXY_FORM");
	check._main(object);
	</script>
EOF
;
}


showapplybox(\%conf);
openbigbox($errormessage, $warnmessage, $notemessage);

if ($action eq "edit"  && $sure eq "y") {
	$action = "add";
    system("touch /var/efw/proxy/reloadproxy");
    printf <<EOF
 <script>
 window.location.href =  window.location.href;
 </script>
EOF
;
}
if($action eq "")
{
	$action = "add";
}
render_templates(\%info, \%conf, $action eq "edit" ? $id : "", $action);
closebigbox();

check_form();
closepage();
