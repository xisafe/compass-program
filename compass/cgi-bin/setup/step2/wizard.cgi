#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: ÍøÂçÅäÖÃÏÔÊ¾Ò³Ãæ
#
# AUTHOR: ÖÜÔ² (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================

##############################################################################
# this file makes the wizard ipcop capable.
##############################################################################


#
# IPCop stuff
#

require '/var/efw/header.pl';
require '/home/httpd/cgi-bin/netwiz.cgi';

getcgihash(\%par);

my $reload_from_wizard = '/usr/local/bin/restart_from_wizard';

#
# start IPCop-style page
#

if ($0 =~ /step2\/*(netwiz|wizard).cgi/) {
    $pagename =  "firstwizard";
    $nomenu = 1;
    setFlavour('setup');
    $nostatus = 1;
} else {
    undef $pagename;
    undef $nomenu;
    undef $nostatus;
}

# redirect if cancel is pressed
if (( ! -f "/var/efw/main/initial_wizard_step2") and ( $pagename eq "firstwizard") and (! -f "/var/efw/appliance/force_registration")) {
	my $httphost = getHTTPRedirectHost();
        print "Status: 302 Moved\n";
        print "Location: https://${httphost}/cgi-bin/netwizard.cgi\n\n";
        exit;
} else {

showhttpheaders();
my ($reload, $extraheader, $content, $rebuildcert) = print_template($swroot);

openpage(_('Network setup wizard'), 1, $extraheader.'<script type="text/javascript" src="/include/netwizard.js"></script>');
my $help_enabled = $ENV{'SCRIPT_NAME'};
printf <<EOF
<input id="help_hidden" value='$help_enabled' class="hidden_class" />
EOF
;
&openbigbox($errormessage, $warnmessage, $notemessage);


print $content;

#
# end IPCop-style page
#

#closebox();
closebigbox();
check_form_step3();
check_form_static();
check_form_dhcp();
check_form_pppoe();
check_form_gateway();
check_form_dns();
check_form_mail();
closepage($nostatus=$nostatus);

if ($reload eq 'YES DO IT') {

    my $options = '';
    if ($rebuildcert) {
	$options .= 'REBUILDCERT';
    }

    if ( -x $reload_from_wizard) {
	# `sudo /usr/local/bin/run-detached $reload_from_wizard $options `;
	`/usr/local/bin/run-detached "sudo /etc/rc.d/rc.netwizard.reload"`;
	`sudo /usr/local/bin/run-detached fcmd "/etc/rc.d/rc.netwizard.reload"`;
    }
}
}
1;
