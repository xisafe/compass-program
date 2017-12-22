#!/usr/bin/perl
#
# SMTP Proxy CGI for Endian Firewall
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
require './smtpscan.pl';
require '/var/efw/header.pl';
&validateUser();
my $dg_conf_default = "/var/efw/smtpscan/default/settings";
my $dg_conf= "/var/efw/smtpscan/settings";
my $phrasedir   = "/var/efw/smtpscan/phraselists";
my @titlelist = split(/\n/, `ls $phrasedir`);
my @contentlist = split(/\n/, `ls $phrasedir`);
	
my %smtp_conf = ();
if (-e $dg_conf_default) {
    readhash($dg_conf_default, \%smtp_conf);
}

if (-e $dg_conf) {
    readhash($dg_conf, \%smtp_conf);
}

my $help_hash1 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","LAN","-10","10","down");

my $help_hash2 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","DMZ","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","WAN","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","WIFI","-10","10","down");

my $help_hash5 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","垃圾邮件过滤器","-10","10","down");

my $help_hash6 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","选择垃圾邮件处理方法","-10","10","down");

my $help_hash7 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","垃圾邮件主题","-10","10","down");

my $help_hash8 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","垃圾邮件标签等级","-10","10","down");

my $help_hash9 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","垃圾邮件隔离等级","-10","10","down");

my $help_hash10 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","垃圾邮件通知用电子邮件地址(垃圾邮件管理员)","-10","10","down");

my $help_hash11 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","垃圾邮件标记等级","-10","10","down");

my $help_hash12 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","日本化","-10","10","down");

my $help_hash13 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","邮件病毒扫描器","-10","10","down");

my $help_hash14 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","选择病毒处理方法","-10","10","down");

my $help_hash15 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","病毒通知电子邮件地址(病毒管理员)","-10","10","down");

my $help_hash16 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","文件设置","-10","10","down");

my $help_hash17 = read_json("/home/httpd/help/smtpconfig_help.json","smtpconfig.cgi","垃圾邮件过滤器","-10","10","down");

	
sub get_spam_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "SA_ENABLED",
        V_TOGGLE_ACTION => 1,
        T_CHECKBOX => _("Enable"),
        V_HELP =>  $help_hash5,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "FINAL_SPAM_DESTINY", 
        V_OPTIONS => [
            {V_VALUE => "D_DISCARD_DEFAULT",
             T_OPTION => _("move to default quarantine location")},
            {V_VALUE => "D_DISCARD",
             T_OPTION => _("move to custom quarantine location")},
            {V_VALUE => "D_DISCARD_EMAIL",
             T_OPTION => _("隔离到自定义邮箱")},
            {V_VALUE => "D_PASS",
             T_OPTION => _("mark as spam")},
        ],
        V_TOGGLE_ACTION => 1,
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
        V_HELP =>  $help_hash6,
    );
    push(@fields, {H_FIELD => get_selectfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "SA_SPAM_SUBJECT_TAG",
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
        V_HELP =>  $help_hash7,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "SA_TAG_LEVEL_DEFLT",
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
        V_HELP =>  $help_hash8,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "SA_KILL_LEVEL_DEFLT",
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
        V_HELP =>  $help_hash9,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "GREYLISTING_ENABLED",
        V_TOGGLE_ACTION => 1,
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "GREYLISTING_DELAY",
        V_TOGGLE_ID => "sa_enabled greylisting_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}) eq 0 && $conf{GREYLISTING_ENABLED} eq "on" ? 0 : 1,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    if ($commtouch eq 1) {
        my %params = (
            V_NAME => "COMMTOUCH_ENABLED",
            V_TOGGLE_ACTION => 1,
            V_TOGGLE_ID => "sa_enabled",
            V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
            T_CHECKBOX => _("Activate commtouch for spam filtering")
        );
        push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    }
    else {
        my %params = ();
        #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    }
    
    my %params = (
        V_ID => "spam_default_quarantine",
        V_TOGGLE_ID => "sa_enabled final_spam_destiny D_DISCARD_DEFAULT",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}) eq 0 && $conf{FINAL_SPAM_DESTINY} eq "D_DISCARD_DEFAULT" ? 0 : 1,
    );
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_ID => "spam_pass",
        V_TOGGLE_ID => "sa_enabled final_spam_destiny D_PASS",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}) eq 0 && $conf{FINAL_SPAM_DESTINY} eq "D_PASS" ? 0 : 1,
    );
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_NAME => "SPAM_QUARANTINE_TO",
        V_TOGGLE_ID => "sa_enabled final_spam_destiny D_DISCARD",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}) eq 0 && $conf{FINAL_SPAM_DESTINY} eq "D_DISCARD" ? 0 : 1,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "SPAM_QUARANTINE_TO_EMAIL",
        V_TOGGLE_ID => "sa_enabled final_spam_destiny D_DISCARD_EMAIL",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}) eq 0 && $conf{FINAL_SPAM_DESTINY} eq "D_DISCARD_EMAIL" ? 0 : 1,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "SPAM_ADMIN",
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
        V_HELP =>  $help_hash10,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "SA_TAG2_LEVEL_DEFLT",
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
        V_HELP =>  $help_hash11,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "SA_DSN_CUTOFF_LEVEL",
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
        
    my %params = (
        V_NAME => "JAPANIZATION_ENABLED",
        V_TOGGLE_ACTION => 1,
        V_TOGGLE_ID => "sa_enabled",
        V_HIDDEN => is_field_hidden($conf{"SA_ENABLED"}),
        T_CHECKBOX => _("Enable"),
        V_HELP =>  $help_hash12,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_virus_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "AV_ENABLED",
         V_TOGGLE_ACTION => 1,
        T_CHECKBOX => _("Enable"),
        V_HELP =>  $help_hash13,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "FINAL_VIRUS_DESTINY",
        V_OPTIONS => [
            {V_VALUE => "D_DISCARD_DEFAULT",
             T_OPTION => _("move to default quarantine location")},
            {V_VALUE => "D_DISCARD",
             T_OPTION => _("move to custom quarantine location")},
            {V_VALUE => "D_DISCARD_EMAIL",
             T_OPTION => _("发送到隔离病毒的邮箱")},
            {V_VALUE => "D_PASS",
             T_OPTION => _("pass to recipient (regardless of bad contents)")},
        ],
        V_TOGGLE_ACTION => 1,
        V_TOGGLE_ID => "av_enabled",
        V_HIDDEN => is_field_hidden($conf{"AV_ENABLED"}),
        V_HELP =>  $help_hash14,
    );
    push(@fields, {H_FIELD => get_selectfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = ();
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_ID => "virus_default_quarantine",
        V_TOGGLE_ID => "av_enabled final_virus_destiny D_DISCARD_DEFAULT",
        V_HIDDEN => is_field_hidden($conf{"AV_ENABLED"}) eq 0 && $conf{FINAL_VIRUS_DESTINY} eq "D_DISCARD_DEFAULT" ? 0 : 1,
    );
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_ID => "virus_pass",
        V_TOGGLE_ID => "av_enabled final_virus_destiny D_PASS",
        V_HIDDEN => is_field_hidden($conf{"AV_ENABLED"}) eq 0 && $conf{FINAL_VIRUS_DESTINY} eq "D_PASS" ? 0 : 1,
    );
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_NAME => "VIRUS_QUARANTINE_TO",
        V_TOGGLE_ID => "av_enabled final_virus_destiny D_DISCARD",
        V_HIDDEN => is_field_hidden($conf{"AV_ENABLED"}) eq 0 && $conf{FINAL_VIRUS_DESTINY} eq "D_DISCARD" ? 0 : 1,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "VIRUS_QUARANTINE_TO_EMAIL",
        V_TOGGLE_ID => "av_enabled final_virus_destiny D_DISCARD_EMAIL",
        V_HIDDEN => is_field_hidden($conf{"AV_ENABLED"}) eq 0 && $conf{FINAL_VIRUS_DESTINY} eq "D_DISCARD_EMAIL" ? 0 : 1,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
        
    my %params = (
        V_NAME => "VIRUS_ADMIN",
        V_TOGGLE_ID => "av_enabled",
        V_HIDDEN => is_field_hidden($conf{"AV_ENABLED"}),
        V_HELP =>  $help_hash15,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_file_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "EXT_ENABLED",
        V_TOGGLE_ACTION => 1,
        T_CHECKBOX => get_field_label("EXT_ENABLED"),
        V_HELP =>  $help_hash16,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "FINAL_BANNED_DESTINY",
        V_OPTIONS => [
            {V_VALUE => "D_DISCARD_DEFAULT",
             T_OPTION => _("move to default quarantine location")},
            {V_VALUE => "D_DISCARD",
             T_OPTION => _("move to custom quarantine location")},
            {V_VALUE => "D_DISCARD_EMAIL",
             T_OPTION => _("发送到隔离邮箱")},
            {V_VALUE => "D_PASS",
             T_OPTION => _("pass to recipient (regardless of blocked files)")},
        ],
        V_TOGGLE_ACTION => 1,
        V_TOGGLE_ID => "ext_enabled",
        V_HIDDEN => is_field_hidden($conf{"EXT_ENABLED"}),
    );
    push(@fields, {H_FIELD => get_selectfield_widget(\%params, \%conf)});
    
    my @options = ();
    my @file_extensions = read_config_file($extensions_file);
    my @custom_file_extensions = read_config_file($extensions_file_custom);
    push(@file_extensions, @custom_file_extensions);
    
    foreach $line (sort @file_extensions) {
        my @extension = split(/\|/, $line);
        push(@options, {V_VALUE => "$extension[0]",
                        T_OPTION => "$extension[1] (.$extension[0])"});
    };
    
    my %params = (
        V_NAME => "BANNEDFILES", 
        V_OPTIONS => \@options,
        V_TOGGLE_ID => "ext_enabled",
        V_HIDDEN => is_field_hidden($conf{"EXT_ENABLED"}),
    );
    push(@fields, {H_FIELD => get_multiselectfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = ();
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_ID => "banned_default_quarantine",
        V_TOGGLE_ID => "ext_enabled final_banned_destiny D_DISCARD_DEFAULT",
        V_HIDDEN => is_field_hidden($conf{"EXT_ENABLED"}) eq 0 && $conf{FINAL_BANNED_DESTINY} eq "D_DISCARD_DEFAULT" ? 0 : 1,
    );
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_ID => "banned_pass",
        V_TOGGLE_ID => "ext_enabled final_banned_destiny D_PASS",
        V_HIDDEN => is_field_hidden($conf{"EXT_ENABLED"}) eq 0 && $conf{FINAL_BANNED_DESTINY} eq "D_PASS" ? 0 : 1,
    );
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_NAME => "BANNED_QUARANTINE_TO",
        V_TOGGLE_ID => "ext_enabled final_banned_destiny D_DISCARD",
        V_HIDDEN => is_field_hidden($conf{"EXT_ENABLED"}) eq 0 && $conf{FINAL_BANNED_DESTINY} eq "D_DISCARD" ? 0 : 1,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "BANNED_QUARANTINE_TO_EMAIL",
        V_TOGGLE_ID => "ext_enabled final_banned_destiny D_DISCARD_EMAIL",
        V_HIDDEN => is_field_hidden($conf{"EXT_ENABLED"}) eq 0 && $conf{FINAL_BANNED_DESTINY} eq "D_DISCARD_EMAIL" ? 0 : 1,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "BANNED_ADMIN",
        V_TOGGLE_ID => "ext_enabled",
        V_HIDDEN => is_field_hidden($conf{"EXT_ENABLED"}),
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
        
    my %params = (
        V_NAME => "DE_ENABLED",
        V_TOGGLE_ID => "ext_enabled",
        V_HIDDEN => is_field_hidden($conf{"EXT_ENABLED"}),
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_bypass_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
   
    my %params = (
        V_NAME => "BYPASS_SOURCE",
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});    
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "BYPASS_DESTINATION",
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});    
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_bomb_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
   
    my %params = (
        V_NAME => "TIME",
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});    
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "CLIENT_LIMIT",
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});    
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}
#为数组消重
sub check_compeate($)
{
	my $str = shift;
	my $length = length($str);
	if(!($length%2))
	{
		my $tem1= substr($str,0,$length/2);
		my $tem2= substr($str,$length/2,$length/2);
		if($tem1 eq $tem2)
		{
			return $tem1;
		}else{
			return $str;
		}
	}else{
		return $str;
	}
}


#周圆-发改委项目-2012-08-08#
sub get_title_form($@)
{
	my @tmplist = @_;
	my $type = shift;
	my %phrasecategories = ();
	my %conf_phraselist = ();

    foreach my $item (split(/;/, $smtp_conf{$type})) {
        $conf_phraselist{$type."_" . $item} = 'on';
    }
	if (-e "$phrasedir/categories") {
        readhash("$phrasedir/categories", \%phrasecategories);
    }else {
        %phrasecategories = ();
    }
	
	my $form = "<div style='width:100%;min-height:150px;background:#fff;'>";
	my $uncategorized = "";
	my %tmp = %phrasecategories;
	my $uncategorized = "";
	
	foreach my $b (@tmplist) {
    my $found = 0;
    if ($b eq "categories") {
        next;
    }
    foreach my $c (keys %tmp) {
        foreach my $cb (split(/\|/, $tmp{$c})) {
            if ($b eq $cb) {
                $found = 1;
                $phrasecategories{$c} .= "$b|";
                last;
            }
        }
        if ($found eq 1) {
            last;
        }
    }
    if ($found eq 0) {
        $uncategorized .= "$b|";
    }
}

	foreach my $cat (sort(keys %phrasecategories)) {
		
		if ($cat eq "categories" || $phrasecategories{$cat} eq "") {next;}
		undef %is_in_cat;
		my $countchecked = 0;
		my $countnotchecked = 0;
		my @tmps = split(/\|/, $phrasecategories{$cat});
		foreach my $tmps (@tmps) {
			$tmps = check_compeate($tmps);
			if ($tmps eq "categories") {
				next;
			}
			
			$is_in_cat{$tmps} = 1;
			if ($conf_phraselist{$type."_" . $tmps} ne "on") {
				$countnotchecked++;
			}else{
				$countchecked++;
			}
		}
    my $allchecked = "none";
    if ($countnotchecked eq 0) {
        $allchecked = "all";
    } elsif ($countchecked ne 0) {
        $allchecked = "some";
    }

    my $catname = $cat;
    $catname =~ s/_/ /g;

    my %subcategories = ();
    for my $item (@tmplist){
        if ($item eq "categories"){next;}
        if ($is_in_cat{$item} eq 1){
            $subcategories{$type."_$item"} = $item;
        }
    }
    $form .= "<div style='float:left;margin-left:20px;margin-top:5px;' >";
	$form .= get_categorys("phrase_$cat", _(ucfirst($catname)), $allchecked, \%subcategories, \%conf_phraselist);
	$form .= "</div>";
	
}
	$form .="<div style='clear:both'></div></div>";
	
	return $form;
}

sub _hashToJSON {
    my $hashref = shift;
    my %hash = %$hashref;
    my $json = '{';
    my @key_value_pairs = ();
    foreach $key (keys %hash) {
		if(($value = _hashToJSON($hash{$key})) ne '{}')
		{
			push(@key_value_pairs, sprintf("\"%s\": %s ",$key,$value));
		}else{
			$value = $hash{$key};
			push(@key_value_pairs, sprintf("\"%s\": \"%s\"", $key,$value));
		}
    }
    $json .= join(',', @key_value_pairs);
    $json .= '}';
    return $json;
}

sub get_categorys {
    my $name = shift;      # name of the marker
    my $text = shift;      # text to display
    my $checked = shift; # are all subcategories checked? (all/some/none)
    my($subcategories) = shift;
    my($status) = shift;
    
    my @subcategories = ();
    for my $item (keys %$subcategories) {
        my $subname = $subcategories->{$item};
        my $allowed = 0;
        if ($status->{$item} ne "") {
            $allowed = 1;
        }
        push(@subcategories, {T_TITLE => $subname, V_NAME => $item, V_ALLOWED => $allowed});
    }

    my %params = (T_TITLE => $text, V_NAME => $name, V_SUBCATEGORIES => \@subcategories, V_HIDDEN => 1);
    return get_category_widget(\%params);
}

sub render_templates($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    my $template = get_zonestatus_widget(_("Unfold to define the status of the SMTP proxy per zone (active, transparent mode, inactive)."), 
                                            \%conf, "", 1);
    my %accordionparams = (
        V_ACCORDION => [
            {T_TITLE => _("Spam settings"),
             H_CONTAINER => get_spam_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("Virus settings"),
             H_CONTAINER => get_virus_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("防垃圾炸弹"),
             H_CONTAINER => get_bomb_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("File settings"),
             H_CONTAINER => get_file_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("Bypass transparent proxy"),
             H_CONTAINER => get_bypass_form(\%conf),
             V_HIDDEN => 1},
			 #{T_TITLE => _("过滤邮件标题包含以下关键字列表"), 
             #H_CONTAINER =>  get_title_form("TITLE",@titlelist),
             #V_HIDDEN => 1},                                 
			 #{T_TITLE => _("过滤邮件内容包含以下关键字列表"), 
             #H_CONTAINER =>  get_title_form("BODY",@contentlist),
             #V_HIDDEN => 1}         
        ]
    );
    
    $template .= get_accordion_widget(\%accordionparams);
    $template =~s/LAN/LAN区/;
    $template =~s/DMZ/DMZ区/;
    $template =~s/WAN/WAN区/;
    $template =~s/不活动/禁用/g;
    $template =~s/活动/不透明模式/g;
    my %switchparams = (
        #V_SERVICE_NOTIFICATION_NAME => "smtpscan",
        V_SERVICE_ON => $conf{"SMTPSCAN_ENABLED"},
        V_SERVICE_AJAXIAN_SAVE => 1,
        H_OPTIONS_CONTAINER => $template,
        T_SERVICE_TITLE => _('Enable SMTP Proxy'),
        T_SERVICE_STARTING => _("The SMTP Proxy is being enabled. Please hold..."),
        T_SERVICE_SHUTDOWN => _("The SMTP Proxy is being disabled. Please hold..."),
        T_SERVICE_RESTARTING => _("The SMTP Proxy is being restarted. Please hold..."),
        T_SERVICE_STARTED => _("The SMTP Proxy was restarted successfully"),
        T_SERVICE_DESCRIPTION => _("Use the switch above to set the status of the SMTP Proxy. Click on the save button below to make the changes active."),
    );
    
    print get_switch_widget(\%switchparams);
}

sub validate_fields($) {
    my $params_ref = shift;
    my %params = %$params_ref;
    my $errors = "";
    
    if ($params{SA_ENABLED} eq "on") {
        $errors .= check_field("FINAL_SPAM_DESTINY", \%params);
        if ($params{FINAL_SPAM_DESTINY} eq "D_DISCARD") {
            $errors .= check_field("SPAM_QUARANTINE_TO", \%params);
        }
        if ($params{FINAL_SPAM_DESTINY} eq "D_DISCARD_EMAIL") {
            $errors .= check_field("SPAM_QUARANTINE_TO_EMAIL", \%params); 
        }
        $errors .= check_field("SA_SPAM_SUBJECT_TAG", \%params);
        $errors .= check_field("SPAM_ADMIN", \%params);
        $errors .= check_field("SA_TAG_LEVEL_DEFLT", \%params);
        $errors .= check_field("SA_TAG2_LEVEL_DEFLT", \%params);
        $errors .= check_field("SA_KILL_LEVEL_DEFLT", \%params);
        $errors .= check_field("SA_DSN_CUTOFF_LEVEL", \%params);
		if($params{SA_DSN_CUTOFF_LEVEL} > 10 || $params{SA_DSN_CUTOFF_LEVEL} <0)
		{
			$errors .=_("\"%s\" should be \"%s\"",_("Send notification only below level"),_("0-10"));
		}
		
        if ($params{GREYLISTING_ENABLED} eq "on") {
            $errors .= check_field("GREYLISTING_DELAY", \%params);
        }
    }
    
    if ($params{AV_ENABLED} eq "on") {
        $errors .= check_field("FINAL_VIRUS_DESTINY", \%params);
        if ($params{FINAL_VIRUS_DESTINY} eq "D_DISCARD") {
            $errors .= check_field("VIRUS_QUARANTINE_TO", \%params);
        }
        if ($params{FINAL_VIRUS_DESTINY} eq "D_DISCARD_EMAIL") {
            $errors .= check_field("VIRUS_QUARANTINE_TO_EMAIL", \%params); 
        }
        $errors .= check_field("VIRUS_ADMIN", \%params);
    }
    
    if ($params{EXT_ENABLED} eq "on") {
        $errors .= check_field("FINAL_BANNED_DESTINY", \%params);
        if ($params{FINAL_BANNED_DESTINY} eq "D_DISCARD") {
			#$errors .= check_field("BANNED_QUARANTINE_TO", \%params);
        }
        if ($params{FINAL_VIRUS_DESTINY} eq "D_DISCARD_EMAIL") {
            $errors .= check_field("BANNED_QUARANTINE_TO_EMAIL", \%params); 
        }
        $errors .= check_field("BANNED_ADMIN", \%params);
    }
    
    $errors .= check_field("BYPASS_SOURCE", \%params);
    $errors .= check_field("BYPASS_DESTINATION", \%params);
    
    return $errors;
}

%field_definition = (
    SA_ENABLED => {
        label => _("Mail spam filter"),
        required => 1},
    COMMTOUCH_ENABLED => {
        label => _("Commtouch spam engine"),
        required => 1},
    FINAL_SPAM_DESTINY => {
        label => _("Choose spam handling"),
        required => 1},
    SA_SPAM_SUBJECT_TAG => {
        label => _("Spam subject"),
        required => 0},
    GREYLISTING_ENABLED => {
        label => _("Spam filtering"),
        required => 1},
    SPAM_QUARANTINE_TO => {
        label => _("Spam quarantine location"),
        required => 1},
    SPAM_QUARANTINE_TO_EMAIL => {
        label => _("设置隔离垃圾邮件的邮箱地址"),
        required => 1,
        checks => ["email"]},
    SPAM_ADMIN => {
        label => _("垃圾邮件通知的管理员邮箱"),
        checks => ["email"]},
    SA_TAG_LEVEL_DEFLT => {
        label => _("Spam tag level"),
        required => 1,
        checks => ["float"]},
    SA_TAG2_LEVEL_DEFLT => {
        label => _("Spam mark level"),
        required => 1,
        checks => ["float"]},
    SA_KILL_LEVEL_DEFLT => {
        label => _("垃圾邮件隔离等级"),
        required => 1,
        checks => ["float"]},
    SA_DSN_CUTOFF_LEVEL => {
        label => _("仅在低于此等级时则发送通知"),
        required => 1,
        checks => ["float"]},
                
    GREYLISTING_DELAY => {
        label => _("Delay for greylisting (sec)"),
        required => 1,
        checks => ["int"]},
    
    AV_ENABLED => {
        label => _("Mail virus scanner"),
        required => 1},
    FINAL_VIRUS_DESTINY => {
        label => _("Choose virus handling"),
        required => 1},
    VIRUS_QUARANTINE_TO => {
        label => _("Virus quarantine location"),
        required => 1},
    VIRUS_QUARANTINE_TO_EMAIL => {
        label => _("隔离病毒所用的电子邮件地址"),
        required => 1,
        checks => ["email"]},
    VIRUS_ADMIN => {
        label => _("Email used for virus notifications (virus admin)"),
        checks => ["email"]},
    
    EXT_ENABLED => {
        label => _("Enable"),
        required => 1},
    FINAL_BANNED_DESTINY => {
        label => _("Choose handling of blocked files"),
        required => 1},
    BANNEDFILES => {
        label => _("Choose filetypes to block (by extension)")},
    BANNED_QUARANTINE_TO => {
        label => _("Blocked files quarantine location"),
        required => 1},
    BANNED_QUARANTINE_TO_EMAIL => {
        label => _("Blocked files quarantine email address"),
        required => 1,
        checks => ["email"]},
    BANNED_ADMIN => {
        label => _("Email used for blocked file notifications (file admin)"),
        checks => ["email"]},
    DE_ENABLED => {
        label => _("Block files with double extension")},
    
    BYPASS_SOURCE => {
        label => _("设置绕过代理服务器的源"),
        required => 0,
        checks => ["ip", "subnet", "mac"]},
    BYPASS_DESTINATION => {
        label => _("设置绕过代理服务器的目标"),
        required => 0,
        checks => ["ip", "subnet"]},
    JAPANIZATION_ENABLED => {
        label => _("Japanization"),
        required => 1},    
    TIME => {
        label => _("允许发送垃圾邮件的时间间隔(s)"),
        required => 0},    
    CLIENT_LIMIT => {
        label => _("单位时间允许单IP发送的邮件上限"),
        required => 0},
);

showhttpheaders();

(my $default_conf_ref, my $conf_ref) = reload_par();
my %default_conf = %$default_conf_ref;
my %conf = %$conf_ref;
my @checkboxes = ("SA_ENABLED", "COMMTOUCH_ENABLED", "AV_ENABLED", "EXT_ENABLED", "GREYLISTING_ENABLED", "DE_ENABLED","JAPANIZATION_ENABLED");
my $errormessage = "";
                
getcgihash(\%par);
if ( $par{ACTION} eq 'save' ) {
    $par{SMTPSCAN_ENABLED} = $par{SERVICE_STATUS};
    $errormessage = validate_fields(\%par);
    if ($errormessage ne "") {
        %conf = %par;
    }else {
			my $save_titlelist="";
			foreach my $item (@titlelist) {
				chomp;
				if ($par{'TITLE_'.$item} eq 1) {
					$save_titlelist .= "$item;"; 
			}
			}

			my $save_contentlist="";
			foreach my $item (@contentlist) {
				chomp;
				if ($par{'BODY_'.$item} eq 1) {
					$save_contentlist .= "$item;"; 
				}
			}
        my $changed = save_settings(\%default_conf, \%conf, \%par, \@checkboxes);
		
        ($default_conf_ref, $conf_ref) = reload_par();
        %default_conf = %$default_conf_ref;
        %conf = %$conf_ref;
		
		my %temps = ();
		&readhash($dg_conf, \%temps);
		$temps{'TITLE'}  = $save_titlelist;
		$temps{'BODY'} = $save_contentlist;
		&writehash($dg_conf, \%temps);
		&readhash($dg_conf, \%smtp_conf);
        if ($changed eq 1 || $save_titlelist || $save_contentlist) {
            system('/usr/local/bin/restartsmtpscan --force >/dev/null 2>&1');
			$notemessage = _("Config successfully changed.");
        }
    }
}

sub check_form(){
	printf <<EOF
<script>
var object = {
       'form_name':'PROXY',
       'option'   :{
                    'SA_SPAM_SUBJECT_TAG':{
                               'type':'text',
                               'required':'0',
                               'check':'other|',
                               'other_reg':'/^.*\$/',
                             },
                    'SA_TAG_LEVEL_DEFLT':{
                               'type':'text',
                               'required':'1',
                               'check':'float|',
                             },
                    'SA_KILL_LEVEL_DEFLT':{
                               'type':'text',
                               'required':'1',
                               'check':'float|',
                             },
                    'GREYLISTING_DELAY':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                             },
                    'SPAM_QUARANTINE_TO':{
                               'type':'text',
                               'required':'1',
							   'check':'other',
							   'other_reg':'!/[\\\/:*?"<>\|]/'
                             },
                    'SPAM_QUARANTINE_TO_EMAIL':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|',
                             },
                    'TIME':{
                               'type':'text',
                               'required':'0',
                               'check':'num|', 
                               'ass_check':function(eve){
                                                         var time = eve._getCURElementsByName("TIME","input","PROXY")[0].value;
                                                         var limit = eve._getCURElementsByName("CLIENT_LIMIT","input","PROXY")[0].value;
                                                         var msg = "";
                                                         if((time && !limit) || (!time && limit)){
                                                             msg = "填写此项后需要填写单位时间允许单IP发送的邮件上限才能生效";
                                                         }  
                                                         return msg;
                                                     }
                             },
                    'CLIENT_LIMIT':{
                               'type':'text',
                               'required':'0',
                               'check':'num|',
                               'ass_check':function(eve){
                                                         var time = eve._getCURElementsByName("TIME","input","PROXY")[0].value;
                                                         var limit = eve._getCURElementsByName("CLIENT_LIMIT","input","PROXY")[0].value;
                                                         var msg = "";
                                                         if((time && !limit) || (!time && limit)){
                                                             msg = "填写此项后需要填写允许发送垃圾邮件的时间间隔才能生效";
                                                         }  
                                                         return msg;
                                                     }
                             },
                    'SPAM_ADMIN':{
                               'type':'text',
                               'required':'0',
                               'check':'mail|',
                             },
                    'SA_TAG2_LEVEL_DEFLT':{
                               'type':'text',
                               'required':'1',
                               'check':'float|',
                             },
                    'SA_DSN_CUTOFF_LEVEL':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                               'ass_check':function(eve){
														 var v = eve._getCURElementsByName("SA_DSN_CUTOFF_LEVEL","input","PROXY")[0].value;
														 var msg = "";
														 if(v>10 || v<0){
															 msg = "应在0-10之间";
														 }	
														 return msg;
                                                     }
                             },
                    'VIRUS_QUARANTINE_TO':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
							   'other_reg':'!/[\\\/:*?"<>\|]/'
                             },
                    'VIRUS_QUARANTINE_TO_EMAIL':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|',
                             },
                    'VIRUS_ADMIN':{
                               'type':'text',
                               'required':'0',
                               'check':'mail|',
                             },
                    'BANNED_QUARANTINE_TO':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
							   'other_reg':'!/[\\\/:*?"<>\|]/'
                             },
                    'BANNED_QUARANTINE_TO_EMAIL':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|',
                             },
                    'BANNED_ADMIN':{
                               'type':'text',
                               'required':'0',
                               'check':'mail|',
                             },
                    'BANNEDFILES':{
                               'type':'select-multiple',
                               'required':'1',
                             },
                    'BYPASS_SOURCE':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|ip_mask|mac|',
                             },
                    'BYPASS_DESTINATION':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|ip_mask|',
                             },
                 }
         }
var check = new ChinArk_forms();
//check._get_form_obj_table("PROXY");
check._main(object);
</script>
EOF
;
}
openpage(_("SMTP Configuration"), 1, 
    '<script type="text/javascript" src="/include/serviceswitch.js"></script>
	 <script type="text/javascript" src="/include/category.js"></script>
     <script type="text/javascript" src="/include/fields.js"></script>');

openbigbox($errormessage, $warnmessage, $notemessage);

render_templates(\%conf);

closebigbox();
check_form();
closepage();
