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
sub get_smarthost_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_ID => "smarthost_enable",
        V_NAME => "SMARTHOST_ENABLED",
        V_CHECKED => is_field_checked($conf{SMARTHOST_ENABLED}),
        V_TOGGLE_ACTION => 1,
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (
        V_ID => "smarthost",
        V_NAME => "SMARTHOST",
        V_VALUE => $conf{SMARTHOST},
        V_TOGGLE_ID => "smarthost_enable",
        V_HIDDEN => is_field_hidden($conf{SMARTHOST_ENABLED}), 
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params)});
    
    my %params = (
        V_ID => "smarthost_auth",
        V_NAME => "SMARTHOST_AUTH_REQUIRED",
        V_CHECKED => is_field_checked($conf{SMARTHOST_AUTH_REQUIRED}),
        V_TOGGLE_ACTION => 1,
        V_TOGGLE_ID => "smarthost_enable",
        V_HIDDEN => is_field_hidden($conf{SMARTHOST_ENABLED}), 
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (
        V_ID => "smarthost_username",
        V_NAME => "SMARTHOST_USERNAME",
        V_VALUE => $conf{SMARTHOST_USERNAME},
        V_TOGGLE_ID => "smarthost_auth",
        V_HIDDEN => is_field_hidden($conf{SMARTHOST_AUTH_REQUIRED}), 
    );
    push(@fields, {V_TOGGLE_ID => "smarthost_enable", 
                    V_HIDDEN => $conf{SMARTHOST_ENABLED} eq "on" ? 0 : 1, 
                    H_FIELD => get_textfield_widget(\%params)});
    
    my %params = (
        V_ID => "smarthost_password",
        V_NAME => "SMARTHOST_PASSWORD",
        V_VALUE => $conf{SMARTHOST_PASSWORD},
        V_TOGGLE_ID => "smarthost_auth",
        V_HIDDEN => is_field_hidden($conf{SMARTHOST_AUTH_REQUIRED}), 
    );
    push(@fields, {V_TOGGLE_ID => "smarthost_enable", 
                    V_HIDDEN => is_field_hidden($conf{SMARTHOST_ENABLED}), 
                    H_FIELD => get_passwordfield_widget(\%params)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = ();
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_ID => "smarthost_port",
        V_NAME => "SMARTHOST_PORT",
        V_VALUE => $conf{SMARTHOST_PORT},
        V_TOGGLE_ID => "smarthost_enable",
        V_HIDDEN => is_field_hidden($conf{SMARTHOST_ENABLED}), 
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params)});
    
    my %params = (V_TOGGLE_ID => "smarthost_enable", 
                    V_HIDDEN => is_field_hidden($conf{SMARTHOST_ENABLED}));
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my $selection_ref = get_field_selection($conf{AUTH_SMARTHOST_METHOD});
    my %selection = %$selection_ref;
    
    my @options = ();
    push(@options, {V_VALUE => "PLAIN", T_OPTION => "PLAIN", V_SELECTED => $selection{"PLAIN"}});
    push(@options, {V_VALUE => "LOGIN", T_OPTION => "LOGIN", V_SELECTED => $selection{"LOGIN"}});
    push(@options, {V_VALUE => "CRAM-MD5", T_OPTION => "CRAM-MD5", V_SELECTED => $selection{"CRAM-MD5"}});
    push(@options, {V_VALUE => "DIGEST-MD5", T_OPTION => "DIGEST-MD5", V_SELECTED => $selection{"DIGEST-MD5"}});
    
    my %params = (
        V_ID => "smarthost_auth_method",
        V_NAME => "AUTH_SMARTHOST_METHOD",
        V_OPTIONS => \@options,
        V_SIZE => 4,
        V_TOGGLE_ID => "smarthost_auth",
        V_HIDDEN => is_field_hidden($conf{SMARTHOST_AUTH_REQUIRED}), 
    );
    push(@fields, {V_TOGGLE_ID => "smarthost_enable", 
                    V_HIDDEN => is_field_hidden($conf{SMARTHOST_ENABLED}),
                    H_FIELD => get_multiselectfield_widget(\%params)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_imap_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_ID => "smtp_auth",
        V_NAME => "SMTPD_IMAP_AUTH_ENABLED",
        V_CHECKED => is_field_checked($conf{SMTPD_IMAP_AUTH_ENABLED}),
        V_TOGGLE_ACTION => 1,
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (
        V_ID => "smtp_imap_server",
        V_NAME => "IMAP_AUTH_SERVER",
        V_VALUE => $conf{IMAP_AUTH_SERVER},
        V_TOGGLE_ID => "smtp_auth",
        V_HIDDEN => is_field_hidden($conf{SMTPD_IMAP_AUTH_ENABLED}),
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my $selection_ref = get_field_selection($conf{AUTH_DAEMONS});
    my %selection = %$selection_ref;
    
    my $string = _("authentication daemons");
    my @options = ();
    push(@options, {V_VALUE => "1", T_OPTION => "1 " . _("authentication daemon"), V_SELECTED => $selection{"1"}});
    push(@options, {V_VALUE => "3", T_OPTION => "3 " . $string, V_SELECTED => $selection{"3"}});
    push(@options, {V_VALUE => "5", T_OPTION => "5 " . $string, V_SELECTED => $selection{"5"}});
    push(@options, {V_VALUE => "8", T_OPTION => "8 " . $string, V_SELECTED => $selection{"8"}});
    push(@options, {V_VALUE => "10", T_OPTION => "10 " . $string, V_SELECTED => $selection{"10"}});
    push(@options, {V_VALUE => "12", T_OPTION => "12 " . $string, V_SELECTED => $selection{"12"}});
    push(@options, {V_VALUE => "15", T_OPTION => "15 " . $string, V_SELECTED => $selection{"15"}});
    push(@options, {V_VALUE => "20", T_OPTION => "20 " . $string, V_SELECTED => $selection{"20"}});
    
    my %params = (
        V_ID => "smtp_auth_daemons",
        V_NAME => "AUTH_DAEMONS",
        V_OPTIONS => \@options,
        V_TOGGLE_ID => "smtp_auth",
        V_HIDDEN => is_field_hidden($conf{SMTPD_IMAP_AUTH_ENABLED}),
    );
    push(@fields, {H_FIELD => get_selectfield_widget(\%params)});
    
    my %params = (
        V_ID => "smtp_imap_port",
        V_NAME => "IMAP_AUTH_PORT",
        V_VALUE => $conf{IMAP_AUTH_PORT},
        V_TOGGLE_ID => "smtp_auth",
        V_HIDDEN => is_field_hidden($conf{SMTPD_IMAP_AUTH_ENABLED}),
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_advanced_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_ID => "smtp_helo",
        V_NAME => "SMTPD_HELO_REQUIRED",
        V_CHECKED => is_field_checked($conf{SMTPD_HELO_REQUIRED}),
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (
        V_ID => "smtp_helo_name",
        V_NAME => "SMTP_HELO_NAME",
        V_VALUE => $conf{SMTP_HELO_NAME},
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params)});
    
    my $selection_ref = get_field_selection($conf{MAILTEMPLATE_LANGUAGE});
    my %selection = %$selection_ref;
    
    my @options = ();
    push(@options, {V_VALUE => "en", T_OPTION => _("English mailtemplate"), V_SELECTED => $selection{"en"}});
    push(@options, {V_VALUE => "de", T_OPTION => _("German mailtemplate"), V_SELECTED => $selection{"de"}});
    push(@options, {V_VALUE => "it", T_OPTION => _("Italian mailtemplate"), V_SELECTED => $selection{"it"}});
    
    my %params = (
        V_ID => "smtp_mailtemplate",
        V_NAME => "MAILTEMPLATE_LANGUAGE",
        V_OPTIONS => \@options,
    );
	#push(@fields, {H_FIELD => get_selectfield_widget(\%params)});
    
    my $selection_ref = get_field_selection($conf{SMTPD_HARD_ERROR_LIMIT});
    my %selection = %$selection_ref;
    
    my $string = _("hard errors");
    my @options = ();
    push(@options, {V_VALUE => "1", T_OPTION => "1 " . _("hard error"), V_SELECTED => $selection{"1"}});
    push(@options, {V_VALUE => "5", T_OPTION => "5 " . $string, V_SELECTED => $selection{"5"}});
    push(@options, {V_VALUE => "10", T_OPTION => "10 " . $string, V_SELECTED => $selection{"10"}});
    push(@options, {V_VALUE => "20", T_OPTION => "20 " . $string, V_SELECTED => $selection{"20"}});
    push(@options, {V_VALUE => "30", T_OPTION => "30 " . $string, V_SELECTED => $selection{"30"}});
    
    my %params = (
        V_ID => "smtp_error_limit",
        V_NAME => "SMTPD_HARD_ERROR_LIMIT",
        V_OPTIONS => \@options,
    );
    push(@fields, {H_FIELD => get_selectfield_widget(\%params)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_ID => "smtp_invalid_hostname",
        V_NAME => "REJECT_INVALID_HOSTNAME",
        V_CHECKED => is_field_checked($conf{REJECT_INVALID_HOSTNAME}),
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (
        V_ID => "smtp_bcc_address",
        V_NAME => "ALWAYS_BCC_ADDRESS",
        V_VALUE => $conf{ALWAYS_BCC_ADDRESS},
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params)});
    
    my %params = (
        V_ID => "smtp_verify_recipient",
        V_NAME => "VERIFY_RECIPIENTS",
        V_CHECKED => is_field_checked($conf{VERIFY_RECIPIENTS}),
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my $selection_ref = get_field_selection($conf{MESSAGE_SIZE_LIMIT});
    my %selection = %$selection_ref;
    
    my $string = _("email contentsize");
    my @options = ();
    push(@options, {V_VALUE => "5000000", T_OPTION => " 5 MB " . $string, V_SELECTED => $selection{"5000000"}});
    push(@options, {V_VALUE => "10240000", T_OPTION => "10 MB " . $string, V_SELECTED => $selection{"10240000"}});
    push(@options, {V_VALUE => "15000000", T_OPTION => "15 MB " . $string, V_SELECTED => $selection{"15000000"}});
    push(@options, {V_VALUE => "20000000", T_OPTION => "20 MB " . $string, V_SELECTED => $selection{"20000000"}});
    push(@options, {V_VALUE => "25600000", T_OPTION => "25 MB " . $string, V_SELECTED => $selection{"25600000"}});
    push(@options, {V_VALUE => "30720000", T_OPTION => "30 MB " . $string, V_SELECTED => $selection{"30720000"}});
    push(@options, {V_VALUE => "35840000", T_OPTION => "35 MB " . $string, V_SELECTED => $selection{"35840000"}});
    push(@options, {V_VALUE => "40960000", T_OPTION => "40 MB " . $string, V_SELECTED => $selection{"40960000"}});
    push(@options, {V_VALUE => "0", T_OPTION => _("unlimited") . " " . $string, V_SELECTED => $selection{"0"}});
    
    my %params = (
        V_ID => "smtp_maximal_contentsize",
        V_NAME => "MESSAGE_SIZE_LIMIT",
        V_OPTIONS => \@options,
    );
    push(@fields, {H_FIELD => get_selectfield_widget(\%params)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_prevention_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_ID => "smtp_fqdn_recipient",
        V_NAME => "REJECT_NON_FQDN_RECIPIENT",
        V_CHECKED => is_field_checked($conf{REJECT_NON_FQDN_RECIPIENT}),
        T_CHECKBOX => _("Enable"),
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (
        V_ID => "smtp_recipient_domain",
        V_NAME => "REJECT_UNKNOWN_RECIPIENT_DOMAIN",
        V_CHECKED => is_field_checked($conf{REJECT_UNKNOWN_RECIPIENT_DOMAIN}),
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_ID => "smtp_fqdn_sender",
        V_NAME => "REJECT_NON_FQDN_SENDER",
        V_CHECKED => is_field_checked($conf{REJECT_NON_FQDN_SENDER}),
        T_CHECKBOX => _("Enable"),
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (
        V_ID => "smtp_sender_domain",
        V_NAME => "REJECT_UNKNOWN_SENDER_DOMAIN",
        V_CHECKED => is_field_checked($conf{REJECT_UNKNOWN_SENDER_DOMAIN}),
        T_CHECKBOX => _("Enable")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}


sub check_form(){
	printf <<EOF
	<script>
var object = {
       'form_name':'PROXY',
       'option'   :{
                    'SMARTHOST':{
                               'type':'text',
                               'required':'1',
                               'check':'domain|'
                             },
                    'SMARTHOST_USERNAME':{
                               'type':'text',
                               'required':'1',
                               'check':'name|'
                             },
                    'SMARTHOST_PASSWORD':{
                               'type':'password',
                               'required':'1'
                             },
                    'SMARTHOST_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|'
                             },
                    'IMAP_AUTH_SERVER':{
                               'type':'text',
                               'required':'1',
                               'check':'domain|'
                             },
                    'IMAP_AUTH_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|'
                             },
                    'SMTP_HELO_NAME':{
                               'type':'text',
                               'required':'1',
                               'check':'name|'
                             },
                    'ALWAYS_BCC_ADDRESS':{
                               'type':'text',
                               'required':'0',
                               'check':'mail|'
                             },
                    'AUTH_SMARTHOST_METHOD':{
                               'type':'select-multiple',
                               'required':'1'
                             }
                 }
         }
	var check = new ChinArk_forms();
	check._main(object);
	</script>
EOF
;
}


sub render_templates($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my %zoneparams = ();
    
    my %accordionparams = (
        V_ACCORDION => [
            {T_TITLE => _("Smarthost configuration"),
             T_DESCRIPTION => _("Unfold to enable/disable the smarthost."),
             H_CONTAINER => get_smarthost_form(\%conf)},
            {T_TITLE => _("IMAP server for SMTP authentication"),
             T_DESCRIPTION => _("Unfold to enable/disable SMTP authentication with external IMAP server."),
             H_CONTAINER => get_imap_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("Mail server settings"),
             T_DESCRIPTION => _("Unfold to set advanced settings."),
             H_CONTAINER => get_advanced_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("防垃圾邮件设置"),
             T_DESCRIPTION => _("Unfold to enable/disable Spam prevention (invalid, unknown recipient/sender)"),
             H_CONTAINER => get_prevention_form(\%conf),
             V_HIDDEN => 1}
        ]
    );
    
    $params{"H_FORM_CONTAINER"} = get_accordion_widget(\%accordionparams);
    
    print get_saveform_widget(\%params);
}

sub validate_fields($) {
    my $params_ref = shift;
    my %params = %$params_ref;
    my $errors = "";
    
    if ($params{SMARTHOST_ENABLED} eq "on") {
        $errors .= check_field("SMARTHOST", \%params);
        $errors .= check_field("SMARTHOST_PORT", \%params);
        if ($params{SMARTHOST_AUTH_REQUIRED} eq "on") {
            $errors .= check_field("SMARTHOST_USERNAME", \%params);
            $errors .= check_field("SMARTHOST_PASSWORD", \%params);
        }
    }
    if ($params{SMTPD_IMAP_AUTH_ENABLED} eq "on") {
        $errors .= check_field("IMAP_AUTH_SERVER", \%params);
        $errors .= check_field("IMAP_AUTH_PORT", \%params);
    }
    $errors .= check_field("SMTP_HELO_NAME", \%params);
    $errors .= check_field("ALWAYS_BCC_ADDRESS", \%params);
    
    return $errors;
}

%field_definition = (
    SMARTHOST_ENABLED => {
        required => 1,
        label => _("使用邮件中继主机分发"),},
    SMARTHOST_AUTH_REQUIRED => {
        required => 1,
        label => _("Smarthost authentication"),},
    SMARTHOST_USERNAME => {
        required => 1,
        label => _("Smarthost username"),},
    SMARTHOST_PASSWORD => {
        required => 1,
        label => _("Smarthost password"),},
    SMARTHOST => {
        required => 1,
        label => "邮件中继主机地址",
        checks => ["ip", "fqdn", "hostname", "domain"]},
    SMARTHOST_PORT => {
        required => 1,
        label => _("Smarthost port"),
        checks => ["port"]},
    AUTH_SMARTHOST_METHOD => {
        required => 1,
        label => _("Choose authentication method"),},
    
    SMTPD_IMAP_AUTH_ENABLED => {
        required => 1,
        label => _("SMTP authentication"),},
    IMAP_AUTH_SERVER => {
        required => 1,
        label => _("IMAP authentication server")."<span class='note'>("._("for example")."imap.com)</span>",
        checks => ["ip", "fqdn", "hostname", "domain"]},
    IMAP_AUTH_PORT => {
        required => 1,
        label => _("IMAP authentication port"),
        checks => ["port"]},
    AUTH_DAEMONS => {
        required => 1,
        label => _("Choose number of authentication daemons"),},
    
    SMTPD_HELO_REQUIRED => {
        required => 1,
        label => _("客户端发送HELO命令"),},
    SMTP_HELO_NAME => {
        label => _("发送HELO命令的主机名"),},
    SMTPD_HARD_ERROR_LIMIT => {
        label => _("硬故障上限"),
        required => 1,},
    MAILTEMPLATE_LANGUAGE => {
        label => _("Choose mailtemplate language"),
        required => 1,},
    REJECT_INVALID_HOSTNAME => {
        required => 1,
        label => _("Reject invalid hostname"),},
    ALWAYS_BCC_ADDRESS => {
        label => _("邮件密送给此地址"),
        checks => ["email"]},
    VERIFY_RECIPIENTS => {
        label => _("Verify recipient address")},
    MESSAGE_SIZE_LIMIT => {
        required => 1,
        label => _("邮件内容字数上限"),},
    
    REJECT_NON_FQDN_RECIPIENT => {
        required => 1,
        label => _("拒绝无效的收信人"),},
    REJECT_UNKNOWN_RECIPIENT_DOMAIN => {
        required => 1,
        label => _("拒绝未知的收信域名"),},
    REJECT_NON_FQDN_SENDER => {
        required => 1,
        label => _("拒绝无效的发信人"),},
    REJECT_UNKNOWN_SENDER_DOMAIN => {
        required => 1,
        label => _("拒绝未知的发送域名"),},
);

showhttpheaders();

(my $default_conf_ref, my $conf_ref) = reload_par();
my %default_conf = %$default_conf_ref;
my %conf = %$conf_ref;
my @checkboxes = ("SMARTHOST_ENABLED", "SMARTHOST_AUTH_REQUIRED", 
                    "SMTPD_IMAP_AUTH_ENABLED", "SMTPD_HELO_REQUIRED",
                    "REJECT_INVALID_HOSTNAME", "REJECT_NON_FQDN_RECIPIENT",
                    "REJECT_UNKNOWN_RECIPIENT_DOMAIN", "REJECT_NON_FQDN_SENDER",
                    "REJECT_UNKNOWN_SENDER_DOMAIN", "VERIFY_RECIPIENTS");
my $errormessage = "";

getcgihash(\%par);
if ( $par{ACTION} eq 'save' ) {
    $errormessage = validate_fields(\%par);
    if ($errormessage ne "") {
        %conf = %par;
    }
    else {
        my $changed = save_settings(\%default_conf, \%conf, \%par, \@checkboxes);
        ($default_conf_ref, $conf_ref) = reload_par();
        %default_conf = %$default_conf_ref;
        %conf = %$conf_ref;
        if ($changed eq 1) {
            system('/usr/local/bin/restartsmtpscan --force >/dev/null 2>&1');
        }
    }
}


# <script type="text/javascript" src="/include/jquery-ui.packed.js"></script>

openpage(_("SMTP Advanced Settings"), 1, 
    '<script type="text/javascript" src="/include/category.js"></script>
     <script type="text/javascript" src="/include/fields.js"></script>');

openbigbox($errormessage, $warnmessage, $notemessage);

render_templates(\%conf);

closebigbox();
check_form();
closepage();
