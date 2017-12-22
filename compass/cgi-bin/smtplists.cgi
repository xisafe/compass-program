#!/usr/bin/perl
#
# SMTP Proxy CGI for Endian Firewall
#

# -------------------------------------------------------------
# some definitions
# -------------------------------------------------------------
require './smtpscan.pl';
require '/var/efw/header.pl';
&validateUser();
(my $default_conf_ref, my $conf_ref) = reload_par();
my %default_conf = %$default_conf_ref;
my %conf = %$conf_ref;
my $errormessage = "";
my $extraheader = '<script type="text/javascript" src="/include/category.js"></script>
                    <script type="text/javascript" src="/include/fields.js"></script>';

%field_definition = (
    SENDER_WHITELIST => {
        label => _("Whitelist sender"),
        checks => ["email", "domain", "subdomain"]},
    RECIPIENT_WHITELIST => {
        label => _("Whitelist recipient"),
        checks => ["email", "domain", "subdomain"]},
    CLIENT_WHITELIST => {
        label => _("客户机白名单"),
        checks => ["ip", "subnet"]},
    SENDER_BLACKLIST => {
        label => _("发送者黑名单"),
        checks => ["email", "domain", "subdomain"]},
    RECIPIENT_BLACKLIST => {
        label => _("Blacklist recipient"), 
        checks => ["email", "domain", "subdomain"]},
    CLIENT_BLACKLIST => {
        label => _("客户机黑名单"),
        checks => ["ip", "subnet"]},

    SPAM_WHITELIST => {
        label => _("Whitelist sender"),
        checks => ["email", "domain", "subdomain"]},
    SPAM_BLACKLIST => {
        label => _("Blacklist sender"),
        checks => ["email", "domain", "subdomain"]},

    KEY_FILTER => {
        label => "启用"},
    USER_PHRASELIST_SUBJECT => {
        label => "基于邮件主题的关键字过滤",
        checks => ["note"]},
    USER_PHRASELIST_BODY => {
        label => "基于邮件内容的关键字过滤",
        checks => ["note"]},

    WHITELIST_RECIPIENT => {
        label => _("Whitelist recipient"),
        checks => ["email", "domain", "subdomain"]},
    WHITELIST_CLIENT => {
        label => _("客户机白名单"),
        checks => ["ip", "subnet", "domain"]},
);
my @checkboxes = ("KEY_FILTER");

##################周圆 2011-09-27 添加帮助信息##############
my $help_hash1 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","收件-发送者白名单","-10","10","down");

my $help_hash2 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","收件-接收者白名单","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","收件-客户机白名单","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","收件-发送者黑名单","-10","10","down");

my $help_hash5 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","收件-接收者黑名单","-10","10","down");

my $help_hash6 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","收件-客户机黑名单","-10","10","down");

my $help_hash7 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","实时黑名单(RBL)","-10","10","down");

my $help_hash8 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","接收者白名单","-10","10","down");

my $help_hash9 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","将客户机列入白名单","-10","10","down");

my $help_hash10 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","垃圾邮件(黑/白名单)","-10","10","down");

my $help_hash11 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","邮件-主题关键字过滤","-10","10","down");

my $help_hash12 = read_json("/home/httpd/help/smtplists_help.json","smtplists.cgi","邮件-内容关键字过滤","-10","10","down");
############################################################

#============页面主体=======================================#
getcgihash(\%par);
&do_action();
showhttpheaders();
openpage(_("SMTP Black- & Whitelists"), 1, $extraheader);
openbigbox($errormessage, $warnmessage, $notemessage);
&render_templates(\%conf);
closebigbox();
check_form();
closepage();
#===========================================================#

sub do_action() {
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
}

sub get_rbl_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @ipsubcategories = ();
    my @domainsubcategories = ();
    
    @rbl_file = read_config_file($rbl_file);
    foreach $line (@rbl_file) {        
        my @rbl = split(/\|/, $line);
        if( $rbl[3] ne '') {
            $link = $rbl[3];
        }
        else {
            $link = $rbl[1];
        }
        if($rbl[2] eq "IP") {
            push(@ipsubcategories, {T_TITLE => $rbl[1], V_NAME => $rbl[0], V_HREF => $link, V_ALLOWED => $conf{$rbl[0]} eq "1" ? 0 : 1});
        }
        elsif($rbl[2] eq "DOMAIN") {
            push(@domainsubcategories, {T_TITLE => $rbl[1], V_NAME => $rbl[0], V_HREF => $link, V_ALLOWED => $conf{$rbl[0]} eq "1" ? 0 : 1});
        }
    }
    
     push(@subcategories, {T_TITLE => $rbl[1], V_NAME => $rbl[0], V_ALLOWED => 1});
     push(@subcategories, {T_TITLE => "subtitle", V_NAME => "subname", V_ALLOWED => 0});
    
    my @fields = ();
    my %params = (T_TITLE => _("IP based RBL"), V_NAME => "IP", V_SUBCATEGORIES => \@ipsubcategories);
    my $form .= get_category_widget(\%params) ;
    my @fields = ();
    my %params = (T_TITLE => _("DOMAIN based RBL"), V_NAME => "DOMAIN", V_SUBCATEGORIES => \@domainsubcategories);
    $form .= get_category_widget(\%params) ;
    $string1 = _("RBL enabled");
    $string2 = _("RBL disabled");
    $form .= "<br class=\"cb\" /><div style=\"float: left; padding-right: 10px;\"><img src=\"/images/accept.png\"/><span style=\"padding-left: 5px;\">$string1</span></div>
              <div style=\"float: left; padding-right: 10px;\"><img src=\"/images/deny.png\"/><span style=\"padding-left: 5px;\">$string2</span></div>";
    return $form;
}

sub get_list_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "SENDER_WHITELIST",
        V_HELP => $help_hash1,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "RECIPIENT_WHITELIST",
        V_HELP => $help_hash2,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "CLIENT_WHITELIST",
        V_HELP => $help_hash3,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "SENDER_BLACKLIST",
        V_HELP => $help_hash4,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "RECIPIENT_BLACKLIST",
        V_HELP => $help_hash5,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "CLIENT_BLACKLIST",
        V_HELP => $help_hash6,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);

    return $form;
}

sub get_spam_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "SPAM_WHITELIST",
        V_HELP => $help_hash10,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "SPAM_BLACKLIST",
        V_HELP => $help_hash10,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_mail_key_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    my %params = (
        V_NAME => "KEY_FILTER",
        V_TOGGLE_ACTION => 1,
        T_CHECKBOX => _("Enable"),
        V_HELP => "",
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});

    my %params = (
        V_NAME => "USER_PHRASELIST_SUBJECT",
        V_TOGGLE_ID => "key_filter",
        V_HELP => $help_hash11,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "USER_PHRASELIST_BODY",
        V_TOGGLE_ID => "key_filter",
        V_HELP => "$help_hash12",
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_grey_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "WHITELIST_RECIPIENT",
        V_HELP => "$help_hash8",
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "WHITELIST_CLIENT",
        V_HELP => "$help_hash9",
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub render_templates($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
        
    my %accordionparams = (
        V_ACCORDION => [
            {T_TITLE => _("Accepted mail (Black- & Whitelists)"),
             H_CONTAINER => get_list_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("Realtime Blacklist (RBL)"),
             H_CONTAINER => get_rbl_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => "基于邮件关键字过滤",
             H_CONTAINER => get_mail_key_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("Spam greylistling (Whitelists)"),
             H_CONTAINER => get_grey_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("Spam (Black- & Whitelists)"),
             H_CONTAINER => get_spam_form(\%conf),
             V_HIDDEN => 1}
        ]
    );
    
    my %params = (
        H_FORM_CONTAINER => get_accordion_widget(\%accordionparams),
    );
    
    print get_saveform_widget(\%params);
}

sub validate_fields($) {
    my $params_ref = shift;
    my %params = %$params_ref;
    my $errors = "";
    
    $errors .= check_field("SENDER_WHITELIST", \%params);
    $errors .= check_field("RECIPIENT_WHITELIST", \%params);
    $errors .= check_field("CLIENT_WHITELIST", \%params);
    $errors .= check_field("SENDER_BLACKLIST", \%params);
    $errors .= check_field("RECIPIENT_BLACKLIST", \%params);
    $errors .= check_field("CLIENT_BLACKLIST", \%params);
    $errors .= check_field("WHITELIST_RECIPIENT", \%params);
    $errors .= check_field("WHITELIST_CLIENT", \%params);
    $errors .= check_field("SPAM_WHITELIST", \%params);
    $errors .= check_field("SPAM_BLACKLIST", \%params);
    return $errors;
}

sub check_form(){
    printf <<EOF
    <script>
    var object = {
       'form_name':'PROXY',
       'option'   :{
            'SENDER_WHITELIST':{
               'type':'textarea',
               'required':'0',
               'check':'mail|domain',
            },
            'RECIPIENT_WHITELIST':{
               'type':'textarea',
               'required':'0',
               'check':'mail|domain',
            },
            'CLIENT_WHITELIST':{
               'type':'textarea',
               'required':'0',
               'check':'ip|ip_mask',
            },
            'SENDER_BLACKLIST':{
               'type':'textarea',
               'required':'0',
               'check':'mail|domain',
            },
            'RECIPIENT_BLACKLIST':{
               'type':'textarea',
               'required':'0',
               'check':'mail|domain',
            },
            'CLIENT_BLACKLIST':{
               'type':'textarea',
               'required':'0',
               'check':'ip|ip_mask',
            },
            'WHITELIST_RECIPIENT':{
               'type':'textarea',
               'required':'0',
               'check':'mail|domain',
            },
            'WHITELIST_CLIENT':{
               'type':'textarea',
               'required':'0',
               'check':'ip|ip_mask|domain',
            },
            'SPAM_WHITELIST':{
               'type':'textarea',
               'required':'0',
               'check':'mail|domain',
            },
            'SPAM_BLACKLIST':{
               'type':'textarea',
               'required':'0',
               'check':'mail|domain',
            },
            'USER_PHRASELIST_SUBJECT':{
               'type':'textarea',
               'required':'0',
               'check':'note|',
            },
            'USER_PHRASELIST_BODY':{
               'type':'textarea',
               'required':'0',
               'check':'note|',
            },
        }
    }
    var check = new ChinArk_forms();
    //check._get_form_obj_table("PROXY");
    check._main(object);
    if(!document.getElementById("key_filter").checked)
    {
        \$(".key_filter").css("display","none");
    }
    \$(document).ready(function(){
        \$("#key_filter").click(function(){
            if(!document.getElementById("key_filter").checked)
            {
                \$(".key_filter").css("display","none");
            }else{
                    var version = CheckBrowser();
                    if(version == "firefox")
                    {
                        \$(".key_filter").css("display","table-row");
                    }else{
                        \$(".key_filter").css("display","block");
                    }
                }
            });
    });

    function CheckBrowser()
    {
      var app=navigator.appName;
      var verStr=navigator.appVersion;
      if (app.indexOf('Netscape') != -1) {
        return "firefox";
      }else if (app.indexOf('Microsoft') != -1) {
        if (verStr.indexOf("MSIE 3.0")!=-1 || verStr.indexOf("MSIE 4.0") != -1 || verStr.indexOf("MSIE 5.0") != -1 || verStr.indexOf("MSIE 5.1") != -1) {
          return "IE_old";

        } else { return "IE_new";}
      }
    }
    </script>
EOF
    ;
}
