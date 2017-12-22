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

######zhouyuan 2011-09-27  添加帮助信息##########
my $help_hash1 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-身份验证设置","10","10","down");

my $help_hash2 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-身份验证设置-验证域","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-身份验证设置-验证孩子节点的个数","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-身份验证设置-缓冲认证TTL(in minutes)","-10","10","down");

my $help_hash5 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-身份验证设置-用户/IP 缓存生存时间(TTL，以分钟计)","-10","10","down");

my $help_hash6 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NCSA专用配置","-10","10","down");

my $help_hash7 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NCSA专用配置-NCSA用户管理","-10","10","down");

my $help_hash8 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NCSA专用配置-NCSA组管理","-10","10","down");

my $help_hash9 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NCSA专用配置-最少的密码位数","-10","10","down");

my $help_hash10 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NTLM专用配置","-10","10","down");

my $help_hash11 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NTLM专用配置-AD服务器的域名","-10","10","down");

my $help_hash12 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NTLM专用配置-AD 服务器的 PDC 主机名","-10","10","down");

my $help_hash13 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NTLM专用配置-AD 服务器的 PDC IP 地址","-10","10","down");

my $help_hash14 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NTLM专用配置-AD服务器的域名","-10","10","down");

my $help_hash15 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NTLM专用配置-AD 服务器的 BDC 主机名","-10","10","down");

my $help_hash16 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-NTLM专用配置-AD 服务器的 BDC IP 地址","-10","10","down");

my $help_hash17 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-LDAP专用配置","-10","10","down");

my $help_hash18 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-LDAP专用配置-LDAP服务器","-10","10","down");

my $help_hash19 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-LDAP专用配置-LDAP服务器端口","-10","10","down");

my $help_hash20 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-LDAP专用配置-绑定DN设置","-10","10","down");

my $help_hash21 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-LDAP专用配置-组对象类","-10","10","down");

my $help_hash22 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-RADIUS专用配置","-10","10","down");

my $help_hash23 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-RADIUS专用配置-Radius服务器","-10","10","down");

my $help_hash24 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-RADIUS专用配置-RADIUS服务器端口","-10","10","down");

my $help_hash25 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-RADIUS专用配置-标志","-10","10","down");

my $help_hash26 = read_json("/home/httpd/help/proxyauth_help.json","proxyauth.cgi","代理-HTTP-身份认证-RADIUS专用配置-共享隐藏","-10","10","down");

##############################################################



sub get_auth_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
        
    my %params = (
        V_NAME => "AUTH_REALM",
		V_HELP => $help_hash2,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "AUTH_CHILDREN",
		V_HELP => $help_hash3,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    my @fields = ();
    
    my %params = ();
        
    my %params = (
        V_NAME => "AUTH_CACHE_TTL",
		V_HELP => $help_hash4,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    my %params = (
        V_NAME => "AUTH_MAX_USERIP",
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    my %params = (
        V_NAME => "AUTH_IPCACHE_TTL",
		V_HELP => $help_hash5,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_ncsa_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "NCSA_USER_GUI",
		V_HELP => $help_hash7,
        T_BUTTON => _("manage users"),
        ONCLICK => "window.open('/cgi-bin/proxyuser.cgi','_self');"
    );
    push(@fields, {H_FIELD => get_buttonfield_widget(\%params)});
    
   
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "NCSA_GROUP_GUI",
		V_HELP => $help_hash8,
        T_BUTTON => _("manage groups"),
        ONCLICK => "window.open('/cgi-bin/proxygroup.cgi','_self');"
    );
    push(@fields, {H_FIELD => get_buttonfield_widget(\%params)});
    
#	 my %params = (
#        V_NAME => "NCSA_MIN_PASS_LEN",
#		V_HELP => $help_hash9,
#    );
#push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
	
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_ntlm_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "NTLM_DOMAIN",
		V_HELP => $help_hash11,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "NTLM_PDC",
		V_HELP => $help_hash12,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "PDC_ADDRESS",
		V_HELP => $help_hash13,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "JOIN_DOMAIN",
		V_HELP => $help_hash14,
        T_BUTTON => _("join domain"),
        ONCLICK => "window.open('/cgi-bin/Adjon.cgi','_self');"
    );
    push(@fields, {H_FIELD => get_buttonfield_widget(\%params)});
    
    my %params = (
        V_NAME => "NTLM_BDC",
		V_HELP => $help_hash15,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});

    my %params = (
        V_NAME => "BDC_ADDRESS",
		V_HELP => $help_hash16,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_ldap_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "LDAP_SERVER",
		V_HELP => $help_hash18,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
	
	my %params = (
        V_NAME => "LDAP_PORT",
		V_HELP => $help_hash19,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
	
    my %params = (
        V_NAME => "LDAP_BASEDN",
		V_HELP => $help_hash20,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
     my %params = (
        V_NAME => "LDAP_TYPE", 
        V_OPTIONS => [
            {V_VALUE => "ADS",
             T_OPTION => _("Active Directory Server")},
            {V_VALUE => "V3",
             T_OPTION => _("LDAP v3 Server")},
            {V_VALUE => "V2",
             T_OPTION => _("LDAP v2 Server")},
            {V_VALUE => "NDS",
             T_OPTION => _("Novell eDirectory Server")},
        ],
    );
    push(@fields, {H_FIELD => get_selectfield_widget(\%params, \%conf)});
    my %params = (
        V_NAME => "LDAP_BINDDN_USER",
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "LDAP_BINDDN_PASS",
    );
    push(@fields, {H_FIELD => get_passwordfield_widget(\%params, \%conf)});

    my %params = (
        V_NAME => "LDAP_PERSON_OBJECT_CLASS",
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    
    
   
    
    
    
    my %params = (
        V_NAME => "LDAP_GROUP_OBJECT_CLASS",
		V_HELP => $help_hash21,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_radius_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "RADIUS_SERVER",
		V_HELP => $help_hash23,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "RADIUS_PORT",
        V_HELP => $help_hash24,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    my %params = (
        V_NAME => "RADIUS_IDENTIFIER",
        V_HELP => $help_hash25,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    
    my %params = (
        V_NAME => "RADIUS_SECRET",
		V_HELP => $help_hash26,
    );
    push(@fields, {H_FIELD => get_passwordfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub render_templates($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my %params = (
        V_NAME => "AUTH_METHOD", 
        V_OPTIONS => [
            {V_VALUE => "ncsa",
             T_OPTION => _("Local Authentication (NCSA)")},
            {V_VALUE => "ntlm",
             T_OPTION => _("Windows Active Directory (NTLM)")},
            {V_VALUE => "ldap",
             T_OPTION => _("LDAP (v2, v3, Novell eDirectory, AD)")},
            {V_VALUE => "radius",
             T_OPTION => _("RADIUS")},
        ],
        V_TOGGLE_ACTION => 1, 
    );
    my $container = '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #999;border:1px 0px 0px 1px;">'.get_selectfield_widget(\%params, \%conf) . "</table>";
    
    my %accordionparams = (
        V_ACCORDION => [
            {T_TITLE => _("Authentication settings"),
			 V_HELP =>  $help_hash1,
             H_CONTAINER => get_auth_form(\%conf)},
            {T_TITLE => _("NCSA specific settings"),
			 V_HELP =>  $help_hash6,
             H_CONTAINER => get_ncsa_form(\%conf),
             V_TOGGLE_ID => "auth_method ncsa",
             V_NOTVISIBLE => $conf{AUTH_METHOD} eq "ncsa" ? 0 : 1},
            {T_TITLE => _("NTLM specific settings"),
			V_HELP =>  $help_hash10,
             H_CONTAINER => get_ntlm_form(\%conf),
             V_TOGGLE_ID => "auth_method ntlm",
             V_NOTVISIBLE => $conf{AUTH_METHOD} eq "ntlm" ? 0 : 1},
            {T_TITLE => _("LDAP specific settings"),
			V_HELP =>  $help_hash17,
             H_CONTAINER => get_ldap_form(\%conf),
             V_TOGGLE_ID => "auth_method ldap",
             V_NOTVISIBLE => $conf{AUTH_METHOD} eq "ldap" ? 0 : 1},
            {T_TITLE => _("RADIUS specific settings"),
			V_HELP =>  $help_hash22,
             H_CONTAINER => get_radius_form(\%conf),
             V_TOGGLE_ID => "auth_method radius",
             V_NOTVISIBLE => $conf{AUTH_METHOD} eq "radius" ? 0 : 1},
        ]
    );
    
    $container .= get_accordion_widget(\%accordionparams);
    
    my %params = (
        H_FORM_CONTAINER => $container,
    );
    
    print get_saveform_widget(\%params);
    
}

sub validate_fields($) {
    my $params_ref = shift;
    my %params = %$params_ref;
    my $errors = "";
	my %temp;
	$temp{"AUTH_CHILDREN"} = $params{"AUTH_CHILDREN"};
	$temp{"AUTH_CACHE_TTL"} = $params{"AUTH_CACHE_TTL"};
	$temp{"AUTH_MAX_USERIP"} = $params{"AUTH_MAX_USERIP"};
    $temp{"AUTH_IPCACHE_TTL"} = $params{"AUTH_IPCACHE_TTL"};
	#$temp{"NCSA_MIN_PASS_LEN"} = $params{"NCSA_MIN_PASS_LEN"};
	#foreach my $elem (keys %temp) {
	#	if ($temp{$elem} !~ /^\d+$/) {
	#		$errors =$temp{$elem}."对于".$elem."是无效的";
	#	}
	#}
    $errors .= check_field("AUTH_REALM", \%params);
    $errors .= check_field("AUTH_CHILDREN", \%params);
    $errors .= check_field("AUTH_CACHE_TTL", \%params);
    $errors .= check_field("AUTH_MAX_USERIP", \%params);
    $errors .= check_field("AUTH_IPCACHE_TTL", \%params);
    
    if ($params{AUTH_METHOD} eq "ntlm") {
        $errors .= check_field("NTLM_DOMAIN", \%params);
        $errors .= check_field("NTLM_PDC", \%params);
        $errors .= check_field("NTLM_BDC", \%params);
        $errors .= check_field("PDC_ADDRESS", \%params);
        $errors .= check_field("BDC_ADDRESS", \%params);
        if ($params{NTLM_BDC} ne "" && $params{BDC_ADDRESS} eq "") {
            $errors .= _("\"%s\" is required!", get_field_label("BDC_ADDRESS")) . "<br />";
        }
    }
    if ($params{AUTH_METHOD} eq "ldap") {
        $errors .= check_field("LDAP_SERVER", \%params);
        $errors .= check_field("LDAP_PORT", \%params);
        $errors .= check_field("LDAP_BASEDN", \%params);
        $errors .= check_field("LDAP_BINDDN_USER", \%params);
        $errors .= check_field("LDAP_BINDDN_PASS", \%params);
        $errors .= check_field("LDAP_PERSON_OBJECT_CLASS", \%params);
        $errors .= check_field("LDAP_GROUP_OBJECT_CLASS", \%params);
    }
    if ($params{AUTH_METHOD} eq "radius") {
        $errors .= check_field("RADIUS_SERVER", \%params);
        $errors .= check_field("RADIUS_PORT", \%params);
        $errors .= check_field("RADIUS_IDENTIFIER", \%params);
        $errors .= check_field("RADIUS_SECRET", \%params);
    }
    
    return $errors;
}

%field_definition = (
    AUTH_METHOD => {
        label => _("Choose Authentication Method"),
        required => 1},
    AUTH_REALM => {
        label => _("Authentication Realm"),
        required => 1},
    AUTH_CHILDREN => {
        label => _("验证子节点的个数"),
        required => 1,
        checks => ["int"]},
    AUTH_CACHE_TTL => {
        label => _("Authentication cache TTL (in minutes)"),
        required => 1,
        checks => ["int"]},
    AUTH_MAX_USERIP => {
        label => _("单个用户使用的不同IP数上限"),
        required => 1,
        checks => ["int"]},
    AUTH_IPCACHE_TTL => {
        label => _("用户/IP缓存超时时间（分钟）"),
        required => 1,
        checks => ["int"]},
    
    NCSA_USER_GUI => {
        label => _("NCSA user management")},
    NCSA_GROUP_GUI => {
        label => _("NCSA group management")},
    
    NTLM_DOMAIN => {
        label => _("Domainname of AD server"),
        required => 1,
        checks => ["domain"]},
    JOIN_DOMAIN => {
        label => _("Join AD domain")},
    NTLM_PDC => {
        label => _("PDC hostname of AD server"),
        required => 1,
        checks => ["hostname"]},
    NTLM_BDC => {
        label => _("BDC hostname of AD server"),
        required => 0,
        checks => ["hostname"]},
    PDC_ADDRESS => {
        label => _("PDC ip address of AD server"),
        required => 1,
        checks => ["ip"]},
    BDC_ADDRESS => {
        label => _("BDC ip address of AD server"),
        checks => ["ip"]},
    
    LDAP_SERVER => {
        label => _("LDAP server"),
        required => 1,
        checks => ["ip", "hostname", "domain"]},
    LDAP_PORT => {
        label => _("Port of LDAP server"),
        required => 1,
        checks => ["port"]},
    LDAP_BASEDN => {
        label => _("Bind DN settings"),
        required => 1},
    LDAP_TYPE => {
        label => _("LDAP type"),
        required => 1},
    LDAP_BINDDN_USER => {
        label => _("Bind DN username")},
    LDAP_BINDDN_PASS => {
        label => _("Bind DN password")},
    LDAP_PERSON_OBJECT_CLASS => {
        label => _("user objectClass"),
        required => 1},
    LDAP_GROUP_OBJECT_CLASS => {
        label => _("group objectClass"),
        required => 1},
    
    RADIUS_SERVER => {
        label => _("RADIUS服务器"),
        required => 1,
        checks => ["ip","hostname", "domain"]},
    RADIUS_PORT => {
        label => _("Port of RADIUS server"),
        required => 1,
        checks => ["port"]},
    RADIUS_IDENTIFIER => {
        label => _("服务器标识"),
        required => 1},
    RADIUS_SECRET => {
        label => _("共享密码"),
        required => 1},
);

showhttpheaders();
openpage(_("HTTP Configuration"), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script><script type="text/javascript" src="/include/fields.js"></script><script type="text/javascript" src="/include/waiting.js"></script>');


(my $default_conf_ref, my $conf_ref) = reload_par();
my %default_conf = %$default_conf_ref;
my %conf = %$conf_ref;
my @checkboxes = ();
my $errormessage = "";

my $cgi_objekt = new CGI;
my $action = $cgi_objekt->param('ACTION');

getcgihash(\%par);

if ( $par{ACTION} eq 'save' ) {
    $errormessage = validate_fields(\%par);
    if ($errormessage ne "") {
        %conf = %par;
		
    }else {
        my $changed = save_settings(\%default_conf, \%conf, \%par, \@checkboxes);
        ($default_conf_ref, $conf_ref) = reload_par();
        %default_conf = %$default_conf_ref;
        %conf = %$conf_ref;
        if ($changed eq 1) {
            system("touch $proxyreload");
			$notemessage = _("成功修改配置信息");
			
        }
    }
	
}
elsif ($par{'ACTION'} eq 'apply'){
    &log(_('Apply proxy settings'));
    applyaction();
}
elsif ($action eq "join") {

    if ($conf{'AUTH_METHOD'} eq 'ntlm') {
        if ($conf{'AUTH_REALM'} eq '') {
            $errormessage = _('Please enter the realm for the NT domain');
        }
        if ($conf{'NTLM_DOMAIN'} eq '') {
            $errormessage = _('Windows domain name required');
        }
        if ($conf{'NTLM_PDC'} eq '') {
            $errormessage = _('Hostname for Primary Domain Controller required');
        }
        if (!&validhostname($conf{'NTLM_PDC'})) {
            $errormessage = _('Invalid hostname for Primary Domain Controller');
        }
        if ((!($conf{'NTLM_BDC'} eq '')) && (!&validhostname($par{'NTLM_BDC'}))) {
            $errormessage = _('Invalid hostname for Backup Domain Controller');
        }

        # check if we can resolv the name 
        use Net::hostent ':FIELDS';

        if (!(gethost($par{'NTLM_PDC'}))) {
            $errormessage = _('Cannot resolve PDC hostname. Is the PDC listed in the Host list?');
        }
    }
}

sub check_form()
{
	
	printf <<EOF
<script>
var object = {
       'form_name':'PROXY',
       'option'   :{
                    'AUTH_REALM':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^.*\$/',
                             },
                    'AUTH_CHILDREN':{
                               'type':'text',
                               'required':'1',
                               'check':'num|',
                             },
                    'AUTH_MAX_USERIP':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                             },
                    'AUTH_CACHE_TTL':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                             },
                    'AUTH_IPCACHE_TTL':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                             },
                    'NTLM_DOMAIN':{
                               'type':'text',
                               'required':'1',
                               'check':'domain|',
                             },
                    'NTLM_PDC':{
                               'type':'text',
                               'required':'1',
                               'check':'name|',
                             },
                    'PDC_ADDRESS':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'NTLM_BDC':{
                               'type':'text',
                               'required':'0',
                               'check':'name|',
                             },
                    'BDC_ADDRESS':{
                               'type':'text',
                               'required':'0',
                               'check':'ip|',
                             },
                    'LDAP_SERVER':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|domain|',
                             },
                    'LDAP_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|',
                             },
                    'LDAP_BASEDN':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^([a-zA-Z]+=([^u4E00-u9FA5]|[0-9a-zA-Z])+,)*[a-zA-Z]+=([a-zA-Z0-9]|[^u4E00-u9FA5])+\$/',
                             },
                    'LDAP_BINDDN_USER':{
                               'type':'text',
                               'required':'0',
                               'check':'other|',
			       'other':'!/^\$/',
                             },
                    'LDAP_PERSON_OBJECT_CLASS':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[a-zA-Z0-9]+\$/',
                             },
                    'LDAP_BINDDN_PASS':{
                               'type':'password',
                               'required':'1',
                             },
                    'LDAP_GROUP_OBJECT_CLASS':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[a-zA-Z0-9]+\$/',
                             },
                    'RADIUS_SERVER':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|domain|',
                             },
                    'RADIUS_IDENTIFIER':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'/^[a-zA-Z0-9]+\$/',
                             },
                    'RADIUS_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|',
                             },
                    'RADIUS_SECRET':{
                               'type':'password',
                               'required':'1',
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
showapplybox(\%conf);
openbigbox($errormessage, $warnmessage, $notemessage);
render_templates(\%conf);
closebigbox();
check_form();
closepage();
