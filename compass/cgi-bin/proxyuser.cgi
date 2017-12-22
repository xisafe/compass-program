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
require './proxy.pl';
require '/var/efw/header.pl';
&validateUser();
my $text_tr = "";
my $psw_tr = "";
my $content = "";
my $num = 1;
my $errormessage = "";
my $notemeaasge = "";
sub get_ncsauser($$$) {
    my $conf_ref = shift;
    my $id = shift;
    my $action = shift;
    
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "user",
    );
    $text_tr =  get_textfield_div_widget(\%params, \%conf);

    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my %params = (
        V_NAME => "pass",
        V_VALUE => $action eq "edit" ? "lEaVeAlOnE" : ""
    );
    $psw_tr = get_passwordfield_div_widget(\%params, \%conf);
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    my %params = (
        H_CONTAINER => $form,
        T_ADDRULE => _("Add NCSA user"),
        T_TITLE => _("NCSA user"),
        T_SAVE => $action eq "edit" ? _("Update user") : _("Create user"),
        V_OPEN => $action eq "edit" ? 1 : 0,
        V_ID => $action eq "edit" ? $id : ""
    );
    #my $content = get_editorbox_widget(\%params);
    
    my @rows = ();
    $num = 1;
    
    my @users = read_config_file($ncsauser_file);
    
    foreach my $thisline (@users) {
        chomp($thisline);
        my @splitted = split(/:/, $thisline);
        my $user = @splitted[0];
        my @cols = ();

        push(@cols, {V_CELL_CONTENT => $num});
        push(@cols, {V_CELL_CONTENT => @splitted[0]});
         my $temp = "if(confirm('"._('Are you sure?')."')){window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=remove&ID=" . ($num - 1) . "','_self');}";
        my %params = (
            V_COLS => \@cols,
            STYLE => setbgcolor($action eq "edit" ? 1 : 0, $id, ($num - 1)),
            EDIT_ACTION => "window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=edit&ID=" . ($num - 1) . "','_self');",
            REMOVE_ACTION => $temp,
        );
        push(@rows, \%params);
        
        $num += 1;
    }
    
    my %params = (
        V_HEADINGS => [
            {HEADING => "#"},
            {HEADING => _("username")},
			{HEADING => _("Actions")},
			
        ],
        V_ACTIONS => 1,
        V_ROWS => \@rows,
    );
    $content = get_listtable_widget(\%params);
    
}

sub render_templates($$$) {
    my $conf_ref = shift;
    my $id = shift;
    my $action = shift;
    my %conf = %$conf_ref;
	my $show = "";
	if($action eq "edit")
	{
		$show = "showeditor";
		$buttontext = _("Update");
	}else{
		$show = "";
		$buttontext = _("Add");
	}
	get_ncsauser(\%conf, $id, $action);
    &openeditorbox(_('Add NCSA user'), "", $show, "createrule", @errormessages);
    printf <<EOF
	</form>
		<form name="PROXYUSER_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
	<table cellpadding="0" cellspacing="0" border="0">
	<tr class="env"><td class="add-div-type">%s</td><td>$text_tr</td></tr>
	<tr class="odd"><td class="add-div-type">%s</td><td>$psw_tr</td></tr>
	</table>
	<input type='hidden' name='ACTION'  value='$action' />
	<input type='hidden' name='sure'    value='y' />
	<input type='hidden' name='EDIT_ID' value='$id' /> 
EOF
,_("Username")
,_("Password")
;
	&closeeditorbox($buttontext, _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
	print $content;
	if($num >1)
	{
	printf <<EOF
	<table class="list-legend" cellpadding="0" cellspacing="0"><tr><td><b>%s</b><img src='/images/edit.png' alt='%s' >%s<img src='/images/delete.png' alt='%s' ></td></tr>
EOF
,
_('Legend'),
_('Edit'),
_('Edit'),
_('Remove'),
_('Remove'),
EOF
;
}else{
no_tr(4,_("Current no content"));
}

print "</table>";
}
# chenwu 2012 7 11
sub validate_fields($$) {
    my $params_ref = shift;
    my $conf_ref = shift;
    my %params = %$params_ref;
    my %conf = %$conf_ref;
    my $errors = "";
    
    #$errors .= check_field("user", \%params);
    #$errors .= check_field("pass", \%params);
    if($params{'user'} eq "")
	{
		$errors .= _("The username  is null")."<br />";
	}
	#用户名，密码位数均有限制
    if (length($params{'user'}) < 4 || length($params{'user'}) >20) {
        $errors .= _(length($params{ 'user' })."用户名\"%s\" 配置无效，请确定其在4-20之间!",$params{'user'}, _("Username"));
    }
    my @users = read_config_file($ncsauser_file);
    my $line = 0;
    foreach my $thisline (@users) {
        chomp($thisline);
        my @splitted = split(/:/, $thisline);
        if (@splitted[0] eq $params{'user'} && $line ne $params{'ID'} && $line ne $params{'EDIT_ID'}) {
            $errors .= _("\"%s\" %s already exists!", $params{'user'}, _("Username"))."<br />";
            last;
        }
        $line += 1;
    }
    if (length($params{'pass'}) < $conf{NCSA_MIN_PASS_LEN} && $params{'pass'} ne "lEaVeAlOnE" || length($params{'pass'}) >16) {
        $errors .= _("密码 \"%s\" 配置无效请确定其在6-16位之间!",$params{'pass'}, _("Password"));
    }
    return $errors;
}

%field_definition = (
    user => {
        label => _("Username"),
        required => 1},
    pass => {
        label => _("Password"),
        required => 1},
);

showhttpheaders();
openpage(_("HTTP Configuration"), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script><script type="text/javascript" src="/include/fields.js"></script><script type="text/javascript" src="/include/waiting.js"></script>');


(my $default_conf_ref, my $conf_ref) = reload_par();
my %default_conf = %$default_conf_ref;
my %conf = %$conf_ref;
my @checkboxes = ();
my $errormessage = "";

getcgihash(\%par);
my $cgi_objekt = new CGI;
my $action = $cgi_objekt->param('ACTION');
my $id = $cgi_objekt->param('ID');

if ( $par{ACTION} eq 'add' ) {
    $errormessage = validate_fields(\%par, \%conf);
    
    if ($errormessage ne "") {
        %conf = %par;
    }
    else {
        save_user(
            $par{'ID'},
            $par{'user'},
            $par{'pass'}
        );
        system("touch $proxyreload");
		$notemessage = _("user added successfully");
    }
	
}
	my $sure = $cgi_objekt->param('sure');

if ($action eq "edit") {
    %conf = user_line(read_config_line($id, $ncsauser_file));

	if($sure eq "y")
	{
		%conf = %$conf_ref;
		$errormessage = validate_fields(\%par, \%conf);
		if($errormessage eq "")
		{
			save_user(
            $par{'EDIT_ID'},
            $par{'user'},
            $par{'pass'}
        );	
			system("touch $proxyreload");
			$notemessage = _("user changed successfully");
		}
	}	
		
}

elsif ($action eq "remove") {
    delete_line($id, $ncsauser_file);
    system("touch $proxyreload");
	$notemessage = _("user remove successfully");
	$action = "add";
}

elsif ($par{'ACTION'} eq 'apply'){
    &log(_('Apply proxy settings'));
    applyaction();
	$notemessage = _("Apply proxy settings successfully");
}


showapplybox(\%conf);

if ($action eq "edit"  && $sure eq "y") {
	$action = "add";
}
if($action eq "")
{
	$action = "add";
}

sub check_form()
{
#表单检查代码添加-2012-08-30-zhouyuan
printf <<EOF
<script>	
var object = {
       'form_name':'PROXYUSER_FORM',
       'option'   :{
                    'user':{
                               'type':'text',
                               'required':'1',
                               'check':'name',
                               'ass_check':function(eve){
                                 //此处去后台获取已经添加的组名，判断当前用户名是否重复
															var cur = eve._getCURElementsByName("user","input","PROXYUSER_FORM")[0].value;
															var key = 0;
															var msg="";
															var action = eve._getCURElementsByName("ACTION","input","PROXYUSER_FORM")[0].value;
															if(!eve.username && action != "edit"){ 
																\$.ajax({
																type:'get',
																url:'/cgi-bin/chinark_back_get.cgi', 
																data:"path=/var/efw/proxy/ncsausers", 
																async:false,
																success:function(data){
																	eve.username = data;
																}
															});
														var exits = eve.username.split('\\n');
														 for(var i =0;i<exits.length;i++){
																var tmp =exits[i].split(":");
																if(tmp[0] == cur){key = 1;}
														}
														if(key)msg = cur+"用户名已存在，请更换！";

														 }
														 														return msg;
							   }
                             },
                    'pass':{
                               'type':'password',
                               'required':'1',
                             },
                 }
         }
var check = new  ChinArk_forms();
check._main(object);
//check._get_form_obj_table("PROXYUSER_FORM");
</script>
EOF
;
}


openbigbox($errormessage, $warnmessage, $notemessage);
render_templates(\%conf, $id, $action);

closebigbox();
&check_form();
closepage();
