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
#        | tdis program is free software; you can redistribute it and/or               |
#        | modify it under tde terms of tde GNU General Public License                 |
#        | as published by tde Free Software Foundation; eitder version 2              |
#        | of tde License, or (at your option) any later version.                      |
#        |                                                                             |
#        | tdis program is distributed in tde hope tdat it will be useful,             |
#        | but WItdOUT ANY WARRANTY; witdout even tde implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See tde               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of tde GNU General Public License           |
#        | along witd tdis program; if not, write to tde Free Software                 |
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
my $service_restarted = 0;

my $help_hash1 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-代理设置","10","10","down");

my $help_hash2 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-代理设置-代理使用的端口","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-代理设置-代理使用的可视主机名","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-代理设置-上传上限","-10","10","down");

my $help_hash5 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-代理设置-下载上限","-10","10","down");

my $help_hash6 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-代理设置-用于通知的管理员电子邮件","-10","10","down");

my $help_hash7 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-允许的端口和ssl端口","10","10","down");

my $help_hash8 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-允许的端口和ssl端口-允许端口(来自客户机)","-10","10","down");

my $help_hash9 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-允许的端口和ssl端口-允许的ssl端口(来自客户机)","-10","10","down");

my $help_hash10 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-记录设置","10","10","down");

my $help_hash11 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-记录设置-HTTP代理记录","-10","10","down");

my $help_hash12 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-记录设置-HTTP代理记录","-10","10","down");

my $help_hash13 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-记录设置-内容过滤记录","-10","10","down");

my $help_hash14 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-记录设置-用户代理记录","-10","10","down");

my $help_hash15 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-记录设置-防火墙记录(仅透明代理)","-10","10","down");

my $help_hash16 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-绕过透明代理","10","10","down");

my $help_hash17 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-绕过透明代理-绕过代理服务器的SUBNET/IP/MAC设置","-10","10","down");

my $help_hash18 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-绕过透明代理-绕过代理服务器到子网/IP","-10","10","down");

my $help_hash19 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-上级代理","10","10","down");

my $help_hash20 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-上级代理-上级服务器","-10","10","down");

my $help_hash21 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-上级代理-上级端口","-10","10","down");

my $help_hash22 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-上级代理-Upstream用户名","-10","10","down");

my $help_hash23 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-上级代理-Upstream密码","-10","10","down");

my $help_hash24 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-上级代理-客户机用户名/IP转发","-10","10","down");

my $help_hash25 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-缓存管理","10","10","down");

my $help_hash26 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-缓存管理-单个文件上限（KB）","-10","10","down");

my $help_hash27 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-缓存管理-单个文件下限（KB）","-10","10","down");

my $help_hash28 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-缓存管理-缓存离线模式","-10","10","down");

my $help_hash29 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-缓存管理-清空缓存","-10","10","down");

my $help_hash30 = read_json("/home/httpd/help/proxyconfig_help.json","proxyconfig.cgi","代理-HTTP-配置-缓存管理-不缓存此目的","-10","10","down");



sub get_server_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "PROXY_PORT",
        V_HELP => $help_hash2,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "VISIBLE_HOSTNAME",
        V_HELP => $help_hash3,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    
    my %params = (
        V_NAME => "MAX_OUTGOING_SIZE",
        V_HELP => $help_hash4,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    
    my %params = (
        V_NAME => "MAX_INCOMING_SIZE",
        V_HELP => $help_hash5,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    
    my %params = (
        V_NAME => "ADMIN_MAIL_ADDRESS",
        V_HELP => $help_hash6,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "ERR_LANGUAGE", 
        V_STYLE=> "display:none;",
        V_OPTIONS => [
            {V_VALUE => "en",
             T_OPTION => _("English")},
            {V_VALUE => "de",
             T_OPTION => _("German")},
            {V_VALUE => "it",
             T_OPTION => _("Italian")},
        ],
    );
    push(@fields, {H_FIELD => get_selectfield_widget(\%params, \%conf)});
    
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_port_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "PORTS",
        V_HELP => $help_hash8,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "SSLPORTS",
        V_HELP => $help_hash9,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});    
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_log_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();

    my %params = (
        V_NAME => "LOGGING",
        V_TOGGLE_ACTION => 1,
        T_CHECKBOX => _("Enable"),
        V_HELP => $help_hash11,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "LOGQUERY",
        V_TOGGLE_ID => "logging",
        T_CHECKBOX => _("Enable"),
        V_HELP => $help_hash12,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "DANSGUARDIAN_LOGGING",
        V_TOGGLE_ID => "logging",
        T_CHECKBOX => _("Enable"),
        V_HELP => $help_hash13,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = ();
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    my %params = (
        V_NAME => "LOGUSERAGENT",
        V_TOGGLE_ID => "logging",
        V_STYLE => "display:none",
        T_CHECKBOX => _("Enable"),
        V_HELP => $help_hash14,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "LOG_FIREWALL",
        V_TOGGLE_ID => "logging",
        T_CHECKBOX => _("Enable"),
        V_HELP => $help_hash15,
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
        V_HELP => $help_hash17,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});    
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "BYPASS_DESTINATION",
        V_HELP => $help_hash18,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});    
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_cache_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "CACHE_SIZE",

    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "CACHE_MEM",
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "MAX_SIZE",
        V_HELP => $help_hash26,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "MIN_SIZE",
        V_HELP => $help_hash27,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "OFFLINE_MODE",
        V_HELP => $help_hash28,
        T_CHECKBOX => _("Enable offline mode")
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "CLEAR_CACHE",
        V_HELP => $help_hash29,
        T_BUTTON => _("clear cache"),
        ONCLICK => "window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=clearcache','_self');"
    );
    push(@fields, {H_FIELD => get_buttonfield_widget(\%params)});
    
    my %params = (
        V_NAME => "DST_NOCACHE",
        V_HELP => $help_hash30,
    );
    push(@fields, {H_FIELD => get_textareafield_widget(\%params, \%conf)});
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    return $form;
}

sub get_upstream_form($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "UPSTREAM_ENABLED",
        T_CHECKBOX => _("使用上级代理"),
        V_TOGGLE_ACTION => 1,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "UPSTREAM_SERVER",
        V_TOGGLE_ID => "upstream_enabled",
        V_HIDDEN => is_field_hidden($conf{"UPSTREAM_ENABLED"}),
        V_HELP => $help_hash20,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "UPSTREAM_PORT",
        V_TOGGLE_ID => "upstream_enabled",
        V_HIDDEN => is_field_hidden($conf{"UPSTREAM_ENABLED"}),
        V_HELP => $help_hash21,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
    my %params = (
        V_NAME => "UPSTREAM_USER",
        V_TOGGLE_ID => "upstream_enabled",
        V_HIDDEN => is_field_hidden($conf{"UPSTREAM_ENABLED"}),
        V_HIDDEN => is_field_hidden($conf{"UPSTREAM_ENABLED"}),
        V_HELP => $help_hash22,
    );
    push(@fields, {H_FIELD => get_textfield_widget(\%params, \%conf)});
    
      my %params = (
        V_NAME => "UPSTREAM_PASSWORD",
        V_TOGGLE_ID => "upstream_enabled",
        V_HIDDEN => is_field_hidden($conf{"UPSTREAM_ENABLED"}),
        V_HELP => $help_hash23,
    );
    push(@fields, {H_FIELD => get_passwordfield_widget(\%params, \%conf)});
=pod    
    my %params = (
        V_NAME => "FORWARD_USERNAME",
        T_CHECKBOX => _("Forward username to upstream proxy"),
        V_TOGGLE_ID => "upstream_enabled",
        V_HIDDEN => is_field_hidden($conf{"UPSTREAM_ENABLED"}),
        V_HIDDEN => is_field_hidden($conf{"UPSTREAM_ENABLED"}),

    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
=cut   
    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = ();
    #push(@fields, {H_FIELD => get_emptyfield_widget(\%params)});
    
    
    
  
    
    my %params = (
        V_NAME => "FORWARD_IPADDRESS",
        T_CHECKBOX => _("将 用户名/IP 地址转发到上级代理 "),
        V_TOGGLE_ID => "upstream_enabled",
        V_HIDDEN => is_field_hidden($conf{"UPSTREAM_ENABLED"}),
        V_HELP => $help_hash24,
    );
    push(@fields, {H_FIELD => get_checkboxfield_widget(\%params, \%conf)});
   
    my %params = (V_FIELDS => \@fields);
    ###hidden this field at 2012-12-17
    #$form .= get_form_widget(\%params);
    
    return $form;
}

sub render_templates($) {
    my $conf_ref = shift;
    my %conf = %$conf_ref;
    
    my @options = ();
    
    push(@options, {V_NAME => "", T_DESCRIPTION => _("不透明模式")});
    push(@options, {V_NAME => "transparent", T_DESCRIPTION => _("透明模式")});
    
    my $template = get_zonestatus_widget("", \%conf, \@options);
    
    my %accordionparams = (
        V_ACCORDION => [
            {T_TITLE => _("Proxy settings"),
             V_HELP => $help_hash1,
             H_CONTAINER => get_server_form(\%conf),
             V_HIDDEN => 0},
            {T_TITLE => _("允许来自客户端的端口"),
             V_HELP => $help_hash7,
             H_CONTAINER => get_port_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("日志设置"),
             V_HELP => $help_hash10,
             H_CONTAINER => get_log_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("Bypass transparent proxy"),
             V_HELP => $help_hash16,
             H_CONTAINER => get_bypass_form(\%conf),
             V_HIDDEN => 1},
            {T_TITLE => _("Cache management"),
             H_CONTAINER => get_cache_form(\%conf),
              V_HELP => $help_hash25,
             V_HIDDEN => 1},
            {T_TITLE => _("上级代理"),
             V_HELP => $help_hash19,
             H_CONTAINER => get_upstream_form(\%conf),
             V_HIDDEN => 1},
        ]
    );
    
    $template .= get_accordion_widget(\%accordionparams);
    $template =~s/LAN/LAN区/;
    $template =~s/DMZ/DMZ区/;
    my %switchparams = (
        V_SERVICE_ON => $conf{"PROXY_ENABLED"},
        V_SERVICE_AJAXIAN_SAVE => 1,
        H_OPTIONS_CONTAINER => $template,
        T_SERVICE_TITLE => _('HTTP代理服务'),
        T_SERVICE_STARTING => _("HTTP代理正在开启，请等待...."),
        T_SERVICE_SHUTDOWN => _("HTTP代理正在关闭，请等待...."),
        T_SERVICE_RESTARTING => _("HTTP代理正在重启，请等待...."),
        T_SERVICE_STARTED => _("HTTP代理重启成功"),
         T_SERVICE_DESCRIPTION => _("使用上面的开关来设置 HTTP 代理的状态"),
    );
    
    print get_switch_widget(\%switchparams);
}

sub validate_fields($) {
    my $params_ref = shift;
    my %params = %$params_ref;
    my $errors = "";
    
    if ($params{"PROXY_PORT"} eq "80") {
        $errors .= _("Port 80 is already used.");
    }
    $errors .= check_field("VISIBLE_HOSTNAME", \%params);
    $errors .= check_field("PROXY_PORT", \%params);
    $errors .= check_field("MAX_INCOMING_SIZE", \%params);
    $errors .= check_field("MAX_OUTGOING_SIZE", \%params);
    $errors .= check_field("ADMIN_MAIL_ADDRESS", \%params);
    $errors .= check_field("PORTSPORTS", \%params);
    $errors .= check_field("SSLPORTS", \%params);
    $errors .= check_field("BYPASS_SOURCE", \%params);
    $errors .= check_field("BYPASS_DESTINATION", \%params);
    $errors .= check_field("CACHE_SIZE", \%params);
    $errors .= check_field("CACHE_MEM", \%params);
    $errors .= check_field("DST_NOCACHE", \%params);
    $errors .= check_field("MAX_SIZE", \%params);
    $errors .= check_field("MIN_SIZE", \%params);
        
    if ($params{UPSTREAM_ENABLED} eq "on") {
        $errors .= validip($params{"UPSTREAM_SERVER"})?"":"【上级代理】->【上级服务器】地址不合法";
        $errors .= check_field("UPSTREAM_PORT", \%params);
    }
    
    return $errors;
}

%field_definition = (
    PROXY_PORT => {
        label => _("Port used by proxy"),
        required => 1,
        checks => ["port"]},
    VISIBLE_HOSTNAME => {
        label => _("设置代理服务器的主机名"),
        required => 0,
        checks => ["hostname"]},
    ADMIN_MAIL_ADDRESS => {
        label => _("管理员邮件地址"),
        required => 0,
        checks => ["email"]},
    ERR_LANGUAGE => {
        label => _("Error Language"),
        required => 1},
    MAX_INCOMING_SIZE => {
        label => _("请求上限(KB)"),
        required => 1,
        checks => ["int"]},
    MAX_OUTGOING_SIZE => {
        label => _("响应上限(KB)"),
        required => 1,
        checks => ["int"]},
    
    PORTS => {
        label => _("Allowed Ports (from client)"),
        required => 0,
        checks => ["portdesc", "portrangedesc"]},
    SSLPORTS => {
        label => _("Allowed SSL Ports (from client)"),
        required => 0,
        checks => ["portdesc", "portrangedesc"]},
    
    LOGGING => {
        label => _("HTTP 代理日志"),
        required => 0},
    LOGQUERY => {
        label => _("Query term logging"),
        required => 0},
    LOGUSERAGENT => {
        label => _("Useragent logging"),
        required => 0},
    DANSGUARDIAN_LOGGING => {
        label => _("Contentfilter logging"),
        required => 0},
    LOG_FIREWALL => {
        label => _("Firewall logging (transparent proxies only)"),
        required => 0},
    
    BYPASS_SOURCE => {
        label => _("设置绕过代理服务器的源"),
        required => 0,
        checks => ["ip", "subnet", "mac"]},
    BYPASS_DESTINATION => {
        label => _("设置绕过代理服务器的目标"),
        required => 0,
        checks => ["ip", "subnet"]},
    
    CACHE_SIZE => {
        label => _("硬盘缓存大小 (MB)"),
        required => 1,
        checks => ["int"]},
    OFFLINE_MODE => {
        label => _("Cache offline mode"),
        required => 0,
        checks => ["int"]},
    CACHE_MEM => {
        label => _("内存中的缓存大小(MB)"),
        required => 1,
        checks => ["int"]},
    DST_NOCACHE => {
        label => _("不缓存此目的地"),
        required => 0,
        checks => ["ip", "domain", "subdomain"]},
    MAX_SIZE => {
        label => _("Maximum object size (KB)"),
        required => 1,
        checks => ["int"]},
    MIN_SIZE => {
        label => _("Minimum object size (KB)"),
        required => 1,
        checks => ["int"]},
    CLEAR_CACHE => {
        label => _("Clear cache")},
    
    UPSTREAM_ENABLED => {
        label => _("上级代理"),
        required => 0},
    UPSTREAM_SERVER => {
        label => _("上级服务器"),
        required => 1,
        checks => ["ip", "hostname", "domain", "fqdn"]},
    UPSTREAM_PORT => {
        label => _("上级端口"),
        required => 1,
        checks => ["port"]},
    UPSTREAM_USER=> {
        label => _("认证用户名"),
        required => 0},
    UPSTREAM_PASSWORD => {
        label => _("认证密码"),
        required => 0},

    FORWARD_IPADDRESS => {
        label => _("客户机用户名/IP转发"),
        required => 0},
);


sub check_form()
{
#表单检查代码添加-2012-09-03-zhouyuan
printf <<EOF
<script>    
var object = {
       'form_name':'PROXY',
       'option'   :{
                    'PROXY_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|',
                             },
                    'VISIBLE_HOSTNAME':{
                               'type':'text',
                               'required':'0',
                               'check':'other',
                               'other_reg':'/^[0-9a-zA-Z]{4,20}\$/'
                             },
                    'MAX_OUTGOING_SIZE':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                             },
                    'MAX_INCOMING_SIZE':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                             },
                    'ADMIN_MAIL_ADDRESS':{
                               'type':'text',
                               'required':'0',
                               'check':'mail|',
                             },
                    'CACHE_SIZE':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                             },
                    'CACHE_MEM':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                             },
                    'MAX_SIZE':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                               'ass_check':function(eve){
                                                        var msg = "";
                                                        var max_size = eve._getCURElementsByName("MAX_SIZE","input","PROXY")[0].value;
                                                        var min_size = eve._getCURElementsByName("MIN_SIZE","input","PROXY")[0].value;
                                                        if(parseInt(max_size)<= parseInt(min_size)){msg = "单个文件上限应该比下限大";}
                                                        return msg;
                                                    }
                             },
                    'MIN_SIZE':{
                               'type':'text',
                               'required':'1',
                               'check':'int|',
                                'ass_check':function(eve){
                                                        var msg = "";
                                                        var max_size = eve._getCURElementsByName("MAX_SIZE","input","PROXY")[0].value;
                                                        var min_size = eve._getCURElementsByName("MIN_SIZE","input","PROXY")[0].value;
                                                        if(parseInt(max_size)<= parseInt(min_size)){msg = "单个文件上限应该比下限大";}
                                                        return msg;
                                                    }
                             },
                    'UPSTREAM_SERVER':{
                               'type':'text',
                               'required':'1',
                               'check':'ip|',
                             },
                    'UPSTREAM_PORT':{
                               'type':'text',
                               'required':'1',
                               'check':'port|',
                             },
                    'UPSTREAM_USER':{
                               'type':'text',
                               'required':'0',
                               'check':'name|',
                             },
                    'PORTS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'port|port_range',
                             },
                    'SSLPORTS':{
                               'type':'textarea',
                               'required':'0',
                               'check':'port|port_range',
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
                    'DST_NOCACHE':{
                               'type':'textarea',
                               'required':'0',
                               'check':'ip|domain|',
                             }
                 }
         }
var check = new  ChinArk_forms();
check._main(object);
//check._get_form_obj_table("PROXY");
</script>
EOF
;
}



my $extendheaders = '<script type="text/javascript" src="/include/serviceswitch.js"></script>
                     <script type="text/javascript" src="/include/fileds.js" ></script>
                     <script type="text/javascript" src="/include/waiting.js"></script>
                     <script type="text/javascript" src="/include/proxyconfig.js"></script>';
my $running_tag = "${swroot}/proxy/runningtag";
my $json = new JSON::XS;

getcgihash(\%par);
showhttpheaders();

if ( $par{'ACTION'} eq "check_running" ) {
    my %ret_data;

    if ( -e $running_tag ) {
        %ret_data->{'running'} = 1;
    } else {
        %ret_data->{'running'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret;
    exit;
}

openpage(_("HTTP Configuration"), 1, $extendheaders);
(my $default_conf_ref, my $conf_ref) = reload_par();
my %default_conf = %$default_conf_ref;
my %conf = %$conf_ref;
my @checkboxes = ("LOGGING", "LOGQUERY", "LOGUSERAGENTS", "DANSGUARDIAN_LOGGING", "LOG_FIREWALL", "OFFLINE_MODE", "FORWARD_IPADDRESS", "UPSTREAM_ENABLED");
my $errormessage = "";

my $cgi_objekt = new CGI;
my $action = $cgi_objekt->param('ACTION');
if ( $par{ACTION} eq 'save' ) {
    $par{PROXY_ENABLED} = $par{SERVICE_STATUS};
    $errormessage = validate_fields(\%par);
    if ($errormessage ne "") {
        %conf = %par;
    }
    else {
        my $forcerestart = 0;
        if ($par{PROXY_ENABLED} ne $conf{PROXY_ENABLED}) {
            $forcerestart = 1;
        }
        my $changed = save_settings(\%default_conf, \%conf, \%par, \@checkboxes);
        ($default_conf_ref, $conf_ref) = reload_par();
        %default_conf = %$default_conf_ref;
        %conf = %$conf_ref;
        if ($changed eq 1) {
            system("touch $proxyrestart");
            $notemessage = _("成功修改配置信息");
        }
        if ($forcerestart eq 1) {
            $service_restarted = 1;
            system("/usr/local/bin/restartsquid --force");
        }
    }
    
}

if ($par{'ACTION'} eq 'apply'){
    &log(_('Apply proxy settings'));
    applyaction();
}
elsif ( $action eq 'clearcache') {
    $service_restarted = 1;
    system('/usr/local/bin/restartsquid --flush');
}
showapplybox(\%conf);


openbigbox($errormessage, $warnmessage, $notemessage);

render_templates(\%conf);

printf <<EOF
<script>
if(!document.getElementById("logging").checked)
{
    \$(".logging").css("display","none");
}
\$(document).ready(function(){
    \$("#logging").click(function(){
        if(!document.getElementById("logging").checked)
        {
            \$(".logging").css("display","none");
        }else{
                var version = CheckBrowser();
                if(version == "firefox")
                {
                    \$(".logging").css("display","table-row");
                }else{
                    \$(".logging").css("display","block");
                }
            }
        });
});
if(!document.getElementById("upstream_enabled").checked)
{
    \$(".upstream_enabled").css("display","none");
}
\$(document).ready(function(){
    \$("#upstream_enabled").click(function(){
        if(!document.getElementById("upstream_enabled").checked)
        {
            \$(".upstream_enabled").css("display","none");
        }else{
                var version = CheckBrowser();
                if(version == "firefox")
                {
                    \$(".upstream_enabled").css("display","table-row");
                }else{
                    \$(".upstream_enabled").css("display","block");
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

&check_form();
closepage();
