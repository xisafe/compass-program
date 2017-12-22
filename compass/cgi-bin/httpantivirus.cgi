#!/usr/bin/perl
#
# httpantivirus.cgi for Endian Firewall

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

my $CONFIG_ROOT='/var/efw';
require $CONFIG_ROOT.'/header.pl';


######zhouyuan 2011-09-27  添加帮助信息##########
my $help_hash1 = read_json("/home/httpd/help/httpantivirus_help.json","httpantivirus.cgi","不扫描以下 URL","-10","10","down");
#################################################


my $conffile_default = $CONFIG_ROOT.'/havp/default/settings';
my $conffile = $CONFIG_ROOT.'/havp/settings';

my $proxydir           = "${swroot}/proxy";
my $proxyrestart       = "$proxydir/restartproxy";
my $proxyreload        = "$proxydir/reloadproxy";

my $lastupdate = `tac /var/log/clamav/clamd.log| grep -m1 "Database updated" | awk {' print $2" "$1" "$3" "$8" "$9 '}`;

my $do_reload = 0;

my %conf = ();

my %checked = ( 0 => '', 1 => 'checked', 'on' => 'checked');

my $enabledfile = '/var/efw/havp/enable';

my $whitelistfile = $CONFIG_ROOT.'/havp/whitelist';
my $whitelist = "";

my $service_restarted = 0;

my $notifcation_script = '<script type="text/javascript">
    var error_view; 
    var notification_view; 
    var warning_view; 
    $(document).ready(function() {' .
        $hide_error . '
        notification_view = setTimeout(function() { $(\'.notification-fancy\').fadeOut(); }, 10000);
        error_view = setTimeout(function() { $(\'.error-fancy\').fadeOut(); }, 10000);
        warning_view = setTimeout(function() { $(\'.warning-fancy\').fadeOut(); }, 10000);
    });
 </script>';

sub toggle_file($$) {
    my $file = shift;
    my $set = shift;

    if ($set) {
        `touch $file`;
		`sudo fmodify $file`;
        return 1;
    }
    if (-e $file) {
        unlink($file);
		`sudo fdelete $file`;
    }
    return 0;
}


sub loadconfig() {
    if (-e $conffile_default) {
        &readhash($conffile_default, \%conf);
    }
    if (-e $conffile) {
        &readhash($conffile, \%conf);
    }
    if (-e $whitelistfile) {
        open(FILE, $whitelistfile);
        $whitelist = join("", <FILE>);
        close(FILE);
    }
}


sub save() {
    my %par;
    getcgihash(\%par);
    
    if ($par{'ACTION'} eq 'apply') {
        &log(_('Apply proxy settings'));
        if (-e $proxyrestart) {
            system("rm $proxyrestart");
            if(-e $proxyreload) {
                system("rm $proxyreload");
            }
            system("/usr/local/bin/restartsquid");
        }
        elsif(-e $proxyreload) {
            system("rm $proxyreload");
            system("/usr/local/bin/restartsquid --reload");
        }
        $service_restarted = 1;
        return (0, "", "");
    }
    if ($par{'action'} ne 'save') {
        return (0,'', "");
    }
    if (($par{'MAXSCANSIZE'} ne $conf{'MAXSCANSIZE'}) ||
            ($par{'WHITELIST'} ne $whitelist)) {
        if ($par{'MAXSCANSIZE'} !~ /\d+/) {
            return (1,_('invalid file size'));
        }
        $conf{'MAXSCANSIZE'} = $par{'MAXSCANSIZE'};
        $whitelist = $par{'WHITELIST'};
		###elvis 9-7 判断URL合法性
		#my @every_url= split(/\n/,$whitelist);
		$par{'WHITELIST'} =~ s/\n//g;
		$par{'WHITELIST'} =~ s/\r/,-,/g;
		my @every_url = split(/,-,/,$par{'WHITELIST'});
		foreach my $line (@every_url) {
			chomp($line);
			if (!$line) {
				next;
			}
			if ($line !~/^(http|file|ftp|telne|gopher|https|news|Idap):\/\//) {
				#$errormessage .= _("Invalid URL format '%s'",$line);
				#return (1,$errormessage);
			}
			$line =~ /(.*){3,6}:\/\/(.*)/;
			my $msg = $2;
			my @all = split(/\//,$msg);
			if (!&validdomainname($all[0]) && ($all[0] !~ /:\d+/)) {
				#$errormessage .= _("Invalid URL '%s'",$line);
				#return (1,$errormessage);
			}
			if ($all[0] =~ /:(\d+)/ && (!validport($1))) {
				#$errormessage .= _("Invalid port number '%s'",$1);
				#return (1,$errormessage);
			}
			for (my $j=1;$j<@all ;$j++) {
				if ($all[$j] !~ /^[a-zA-Z0-9-]/ && $all[$j]) {
				#	$errormessage .= _("Invalid URL '%s'",$line);
				#	return (1,$errormessage);
				}
			}
		}
		###end
		$do_reload = 1;
        &writehash($conffile, \%conf);
		`sudo fmodify $conffile`;
        open (OUT, ">$whitelistfile");
        print OUT $whitelist;
        close OUT;
		`sudo fmodify $whitelistfile`;
		return (0,'', _("成功修改配置信息"));
        
    }
}

sub display() {
    if (-e '/etc/FLASH') {
        $conf{'MAXSCANSIZE'} = 20;
        $fixed = 'DISABLED';
    }

    openbox('100%', 'left', _('HTTP antivirus'));
    printf <<EOF
<form name="ANTI" action="" method="post">
    <div>
    <table width="100%" BORDER='0' CELLSPACING='0' CELLPADDING='0'>
        <tr class="env">
            <td class="add-div-table">%s</td>
            <td>
                <select name="MAXSCANSIZE" $fixed>
EOF
    ,
    '扫描文件大小上限(MB)'
    ;
    my @entries = qw '0 1 2 5 10 15 20 25 30 40 50 80 100 150 200 500';
    foreach my $entry (@entries) {
        my $selected = '';
        if ($entry eq $conf{'MAXSCANSIZE'}) {
            $selected = 'selected';
        }
        printf <<EOF
                    <option $selected value="$entry">$entry</option>";
EOF
        ;
    }
    printf <<EOF
                </select>
            </td>
			</tr>
			<tr class="odd">
            <td class="add-div-table need_help">%s $help_hash1</td>
EOF
    ,
    _('Do not scan the following URLs'),
    ;    
        printf <<EOF
            <td><textarea name='WHITELIST' cols='37' rows='4' wrap='off'>$whitelist</textarea></td>
        </tr>
EOF
;
=q
if ($lastupdate ) {
        printf <<EOF
            <tr class="env">
			<td class="add-div-type"><b>%s</b></td>
            <td style="background-color: #fefefe;">
EOF
        ,
        '病毒库最新更新'
        ;

        system('tac /var/log/clamav/clamd.log| grep -m1 "Database updated" | awk {\' print $2" "$1" "$3" "$8" "$9 \'}');

        printf <<EOF
            </td></tr>
EOF
        ;
    }
=cut

printf <<EOF
    <tr class="table-footer">
	<td colspan="5">
         <input type='submit' name='submit' value='%s' class="net_button" />
         <input type="hidden" name="action" value="save" />
    </td>
	</tr>
	</table>
	</div>
</form>
EOF
,_('Save')
    ;
    closebox();
}

sub check_form(){
	printf <<EOF
	<script>
var object = {
       'form_name':'ANTI',
       'option'   :{
                    'WHITELIST':{
                               'type':'textarea',
                               'required':'0',
                               'check':'url|',
                             },
                 }
         }
var check = new  ChinArk_forms();
check._main(object);
//check._get_form_obj_table("ANTI");
</script>
EOF
;
}
&showhttpheaders();
openpage(_('HTTP antivirus'), 1, $notfication_script);

loadconfig();
my ($error, $errormessage, $notemessage) = save();

if ($do_reload) {
        system("touch $proxyreload");
    }

if (-e $proxyrestart || -e $proxyreload) {
    applybox(_("代理设置已经改变，为使之生效请点击应用"));
}
&openbigbox($errormessage, $warnmessage, $notemessage);
service_notifications(
    ['squid', 'dansguardian', 'havp', 'sarg'], 
    {
        'type' => $service_restarted == 1 ? "commit" : "observe",
        'interval' => 500, 
        'startMessage' => _("Proxy settings are being applied. Please hold..."),
        'endMessage' => _("Proxy settings have been applied successfully."),
        'updateContent' => '.service-switch-form'
    }
);

display();
closebigbox();
check_form();
closepage();
