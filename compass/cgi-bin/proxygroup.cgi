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
my $text_tr = "";
my $textarea_tr = "";
my $content = "";
my $num = 1;
my $user_name = "";
my @group_name = "";

sub get_ncsagroup($$$) {
    my $conf_ref = shift;
    my $id = shift;
    my $action = shift;
    my %conf = %$conf_ref;
    
    my @fields = ();
    
    my %params = (
        V_NAME => "group",
    );
    $text_tr = get_textfield_div_widget(\%params, \%conf);

    my %params = (V_FIELDS => \@fields);
    my $form = get_form_widget(\%params);
    
    my @fields = ();
    
    my @users = read_config_file($ncsauser_file);
    my @options = ();
    foreach my $thisline (@users) {
        chomp($thisline);
        my %splitted = user_line($thisline);
        push(@options, {V_VALUE => $splitted{'user'}, T_OPTION => $splitted{'user'}});
    }
    my %params = (
        V_NAME => "users", 
        V_OPTIONS => \@options
    );
    $textarea_tr = get_multiselectfield_div_widget(\%params, \%conf);
    
    my %params = (V_FIELDS => \@fields);
    $form .= get_form_widget(\%params);
    
    my %params = (
        H_CONTAINER => $form,
        T_ADDRULE => _("Add NCSA group"),
        T_TITLE => _("NCSA group"),
        T_SAVE => $action eq "edit" ? _("Update group") : _("Create group"),
        V_OPEN => $action eq "edit" ? 1 : 0,
        V_ID => $id
    );
    #my $content = get_editorbox_widget(\%params);
    
    my @rows = ();
    $num = 1;
    
    my @groups = read_config_file($ncsagroup_file);
    
    foreach my $thisline (@groups) {
        chomp($thisline);
        my %splitted = group_line($thisline);
        my @cols = ();
        
        push(@cols, {V_CELL_CONTENT => $num});
        push(@cols, {V_CELL_CONTENT => $splitted{'group'}});
        
        my $users = $splitted{'users'};
        $users =~ s/\|/<br \/>/g;
        push(@cols, {V_CELL_CONTENT => $users});
        my $temp = "if(confirm('"._('Are you sure?')."')){window.open('" . $ENV{'SCRIPT_NAME'} . "?ACTION=remove&ID=".($num - 1)."','_self');}";
		
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
            {HEADING => _("groupname")},
            {HEADING => _("users")},
			{HEADING => _("Actions")},
        ],
        V_ACTIONS => 1,
        V_ROWS => \@rows,
    );
    $content .= get_listtable_widget(\%params);
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
		my @parValue = split(/&/, $ENV{'QUERY_STRING'});
		my @temp0 = split(/=/, $parValue[0]);
		my @temp1 = split(/=/, $parValue[1]);

		my $id;
		if($temp0[0] eq "ID")
		{
			$id = $temp0[1];
		}elsif($temp1[0] eq "ID"){
			$id = $temp1[1];
		}
		my @groups = read_config_file($ncsagroup_file);
		my @temp = split(",",$groups[$id]);
		$user_name = $temp[0];
		$temp[1] =~ s/\|/&/g;
		@group_name = split("&",$temp[1]);

	}else{
		$show = "";
		$buttontext = _("Add");
	}
	get_ncsagroup(\%conf_ref, $id, $action);
    &openeditorbox(_('Add NCSA group'), "",$show, "createrule", @errormessages);
	 printf <<EOF
	 </form>
		<form name="PROXYGROUP_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
	<table cellpadding="0" cellspacing="0" border="0">
	<tr class="env"><td class="add-div-type">%s</td><td><input id="group" name="group"  size="30" maxlength="" type="text" value=$user_name>
</td></tr>
	<tr class="odd"><td class="add-div-type">%s</td><td>
	 <select id="users" class="multiselect" style="width: 150px; height: 100px; padding: 5px;" name="users" multiple="multiple">

EOF
,_("Groups")
,_("User")
;
	my @users = read_config_file($ncsauser_file);
    my @options = ();
    foreach my $thisline (@users) {
        chomp($thisline);
        my %splitted = user_line($thisline);
		my $selected = "";
		foreach my $group(@group_name)
		{
			print $group;
			if($group eq $splitted{'user'})
			{
				$selected = "selected = 'selected'";
			}
		}
		printf <<EOF
        <option value="$splitted{'user'}" $selected >$splitted{'user'}</option>
EOF
;
}

printf <<EOF
</select>
</td></tr>
	</table>
	<input type='hidden' name='ACTION'  value='$action' />
	<input type='hidden' name='sure'    value='y' />
	<input type='hidden' name='EDIT_ID' value='$id' /> 
EOF
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
no_tr(5,_("Current no content"));
}

print "</table>";
}

sub validate_fields($) {
    my $params_ref = shift;
    my %params = %$params_ref;
    my $errors = "";
    
    return $errors;
}

%field_definition = (
);

showhttpheaders();
openpage(_("HTTP Configuration"), 1, '<script type="text/javascript" src="/include/serviceswitch.js"></script><script type="text/javascript" src="/include/fields.js"></script><script type="text/javascript" src="/include/waiting.js"></script>');


(my $default_conf_ref, my $conf_ref) = reload_par();
my %default_conf = %$default_conf_ref;
my %conf = %$conf_ref;
my @checkboxes = ();
my $errormessage = "";
my %par = ();
getcgihash(\%par);

my $cgi_objekt = new CGI;
my $action = $cgi_objekt->param('ACTION');
my $id = $cgi_objekt->param('ID');

if ( $par{ACTION} eq "add" ) {
    $errormessage = validate_fields(\%par);
	my @groups = read_config_file($ncsagroup_file);
    foreach my $thisline (@groups) {
        chomp($thisline);
        my @splitted = split(/,/, $thisline);
        if (@splitted[0] eq $par{'group'}) {
            $errormessage .= _("\"%s\" %s already exists!",$par{'group'}, _(""))."<br />";
            last;
        }
    }
	if($par{'group'} eq "")
	{
		$errormessage = _("Group name is null");
	}
    if ($errormessage ne "") {
        %conf = %par;
    }
    else {
        save_group(
            $par{'ID'},
            $par{'group'},
            $par{'users'}
        );
        system("touch $proxyreload");
		$notemessage = _("Group added successfully");
    }
	%par = ();
}
	my $sure = $cgi_objekt->param('sure');
	


if ($action eq "edit"  && $sure eq "y") {
	if($par{'group'} eq "")
	{
		$errormessage = _("Group name is null");
	}
	my $now_id = $par{'EDIT_ID'};
    %conf = group_line(read_config_line($now_id, $ncsagroup_file));
	if($sure eq "y")
	{
		%conf = %$conf_ref;
	}
	if(!($config{'group'} eq $par{'group'} && $config{'users'} eq $par{'users'}))
	{
		my $new_str =  $par{'group'}.",".$par{'users'};
		update_line($now_id,$ncsagroup_file,$new_str);
		system("touch $proxyreload");
		$notemessage = _("Group changed successfully");
	}  
}


elsif ($action eq "remove") {
    delete_line($id, $ncsagroup_file);
    system("touch $proxyreload");
	$notemessage = _("Group remove successfully");
	$action = "add";
}
elsif ($par{'ACTION'} eq 'apply'){
    &log(_('Apply proxy settings'));
	$notemessage = _('Apply proxy settings');
    applyaction();
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
       'form_name':'PROXYGROUP_FORM',
       'option'   :{
                    'group':{
                               'type':'text',
                               'required':'1',
                               'check':'name|',
                               'ass_check':function(eve){
                            	 //此处去后台获取已经添加的组名，判断当前组名是否重复
						var cur = eve._getCURElementsByName("group","input","PROXYGROUP_FORM")[0].value;
														var key = 0;
														var msg="";
														var action = eve._getCURElementsByName("ACTION","input","PROXYGROUP_FORM")[0].value;
														if(!eve.groupname && action != "edit"){
														\$.ajax({
																type:'get',
																url:'/cgi-bin/chinark_back_get.cgi', 
																data:"path=/var/efw/proxy/ncsagroups", 
																async:false,
																success:function(data){
																	eve.groupname = data;
																}
															});
														var exits = eve.groupname.split('\\n');
														for(var i =0;i<exits.length;i++){
															var tmp =exits[i].split(",");
															if(tmp[0] == cur){key = 1;}
														}
														if(key)msg = cur+"组名已存在，请更换！";

														}
														return msg;
                                                     }
                             },
                    'users':{
                               'type':'select-multiple',
                               'required':'0',
                             },
                 }
         }
var check = new  ChinArk_forms();
check._main(object);
//check._get_form_obj_table("PROXYGROUP_FORM");
</script>
EOF
;
}


openbigbox($errormessage, $warnmessage, $notemessage);
render_templates(\%conf, $id, $action);
closebigbox();
&check_form();
closepage();
