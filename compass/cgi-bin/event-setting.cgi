#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 事件设定页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================

require '/var/efw/header.pl';
use warnings;
use File::Copy;

my $dir = '/var/efw/sec/'; 
my $default_dir = $dir."eventwarn/default"; #default dir
my $default_mail = $default_dir.'/mail-address'; #default mail address
my $mail_address = $dir.'eventwarn/mail-address';
my $main_mail = '/var/efw/main/settings'; #sysmanager mail address
my $need = $dir."eventwarn/reload-mail";
my @securityEvents;
my %selected;
my $select_number = 0;
my $errorMessage = "";
$selected{'custommail'} = ''; 
$selected{'defaultmail'} = '';
$selected{'offmail'} = '';
	
my @errormessage = ();
my $status = 'on';
my $fmail = ""; # send mail
my $tmail = ""; #recv mail
my $lt = 'y' ;
my $smarthost = "";
my (@par);

my $help_hash1 = read_json("/home/httpd/help/event-setting_help.json","event-setting.cgi","系统-事件告警-设定-邮件通知","-10","10","down");

sub read_file($) {
    my $filename = shift;
    my @lines;
    open(FILE, "<$filename");
    foreach my $line (<FILE>){
		chomp($line);
#		$line =~ s/[\r|\n]//g;
		if(is_valid($line)) {
			next;
		}
		push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub is_valid($) {
    my $line = shift;
    if ($line =~ /(?:(?:[^,]*),){9}/) {
        return 1;
    }
    return 0;
}
sub check_form(){
	printf <<EOF
	<script>
	var object = {
       'form_name':'EVENT_FORM',
       'option'   :{
                    'tmail':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|',
                    },
					'fmail':{
                               'type':'text',
                               'required':'1',
                               'check':'mail|',
                    },
                    'smarthost':{
                               'type':'text',
                               'required':'0',
                               'check':'domain|ip',
                    },
        }
    }
	var check = new ChinArk_forms();
	check._main(object);
	//check._get_form_obj_table("EVENT_FORM");
	</script>
EOF
;
}
#save file,first is filename,second is value
sub save_file($$){
   my $filename = shift;
   my $tmpV = shift;
   &copy_file($filename,"$filename.old");
   open(FILE, ">$filename");	
   print FILE "$tmpV\n";
   close FILE;
   `sudo fmodify $filename`;
}

#copy file
sub copy_file($$)
{
   my $originFile = shift;
   my $copyFile = shift;
   if(!(-e $copyFile))
   {
        system("touch $copyFile");
   }
   my @lines = read_file($originFile);
   open(FILE,">$copyFile");
   my $count = 0;
   my $total = scalar(@lines);
   while($count < $total)
   {
        print FILE "$lines[$count]\n";
	$count++;
   }
   close FILE;
   `sudo fmodify $copyFile`;
}

sub save()
{
   $fmail = $par{'fmail'};
   $tmail = $par{'tmail'};
   $smarthost = $par{'smarthost'};
   my $action = $par{'ACTION'};
   my $select_number = $par{'select_mail'};
   my $tmpValue = "$fmail,$tmail,$smarthost,$select_number";
   readhash($main_mail,\%global_mail);
   
   if( $action eq 'apply') {
		&log("change event");
		system("rm $need");
		system("/usr/local/bin/restartsec &>/dev/null");
   }   
   if( $action eq 'save'){
   		my $file;
		my $sig="0";
        if(-e $mail_address){
            $file = $mail_address;
			$sig = "1";
        }
        else{
            $file = $default_mail;
        }
        
        
		if($select_number =~ /1/){  
			#custom address
			if(!$tmail){
				$errorMessage = _("收件人地址不能为空!");
			}
		    if(($global_mail{'MAIN_ADMINMAIL'} ne $tmail) || ($global_mail{'MAIN_SMARTHOST'} ne $smarthost)){				   
				if($tmail =~ /\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*/ && $fmail =~ /\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*/){
					$tmpValue = "$fmail,$tmail,$smarthost,$select_number";
					&save_file($mail_address,$tmpValue);
					system("touch $need");
					&applybox(_('configures have been changed and need to be applied in order to make the changes active!'));
				}
				else{
					$errorMessage = _("Mail recipient address format is incorret");
				}
			}
		}
		elsif($select_number =~ /2/){ 
			#no notice
			if(($sig eq "0") or ($select_number ne $tmp4)){
				$tmpValue = ",,,$select_number";
				if(!(-e $mail_address)){
					system("touch $mail_address");
				}
				&save_file($mail_address,$tmpValue);
				if(!(-e $need))
				{
					system("touch $need");
				}			
				&applybox(_('The configuration has been changed and needs to be applied in order to make the changes active!'));
			}
		}

		elsif($select_number =~ /0/){ #default mail
			if(($sig eq "0") or ($select_number ne $tmp4)){
				my @default = &read_file($main_mail);
				foreach my $thisline (@default){ #get system manager mail
					my ($f1,$f2) = split(/=/,$thisline);
					if( $f1 eq 'MAIN_ADMINMAIL'){
						$tmail = $f2;
					}elsif($f1 eq 'MAIN_MAILFROM'){
						$fmail = $f2;
					}elsif($f1 eq 'MAIN_SMARTHOST'){
						$smarthost = $f2;
					}
				}
				if(( $fmail eq "") && ( $tmail eq "") && ( $smarthost eq "")){
					$errorMessage = _("默认电子邮件地址为空，请在系统参数设置->接口设置->配置向导中配置！");
				}
				else{
					my $tmpValue = "$fmail,$tmail,$smarthost,$select_number";
					if(!(-e $mail_address)){
						system("touch $mail_address");
					}
					&save_file($mail_address,$tmpValue);
					if(!(-e $need))
					{
						system("touch $need");
					}
					&applybox(_('The configuration has been changed and needs to be applied in order to make the changes active!'));
				}
			}
		}
	}
	else{
	    if (-e $need){
			&applybox(_('The configuration has been changed and needs to be applied in order to make the changes active!'));
		}
	}   
}


sub display() #show
{
    my $file;
    if(-e $mail_address){
        $file = $mail_address;
    }else{
        $file = $default_mail;
    }
    my @mail = read_file($file);  #get the values of $fmail,$tmail,$smarthost...
    my $show_enable = "none"; 
    my $tmp ="";
    ($fmail,$tmail,$smarthost,$tmp) = split(/,/,$mail[0]);

    $selected{$tmp} = "selected='selected'";
    if ($tmp eq "1") {
    	$show_enable = "";
    }
	&openbigbox($errorMessage, , );
    &openbox('100%','left',_('Settings'));
printf <<END

 <form name="EVENT_FORM" id="settingseditor" class="notificationsettings required settingseditor" action="" method="post">
 <table>
 <tr class="env">
 <td  class="add-div-type need_help" >%s $help_hash1</td>
 <td ><select style="width:300px" name="select_mail" class="singleselectfield" id="select_mail" onclick = "Check()">
                    <option value="0" $selected{'0'}>%s</option>
					<option value="1" $selected{'1'}>%s</option>
					<option value="2" $selected{'2'}>%s</option>
     </select>
	 </td>
	 </tr>
	 </table>

<table id="mail_address" value="1234" style="display:$show_enable;">
			
<tr class="odd">
<td class="add-div-type">%s*</td>
<td><input type="text" class="textfield" name="tmail" value="$tmail"/></td>
</tr>
<tr class="env">
<td class="add-div-type">发信人地址*</td>
<td><input type="text" class="textfield" name="fmail" value="$fmail"/></td>
</tr>
<tr class="odd">
<td class="add-div-type">邮件中继主机地址</td>
<td><input type="text" class="textfield" name="smarthost" value="$smarthost"/></td>
</tr>
</table>
<table>
<tr class="table-footer">
<td>
<input type="hidden" name="ACTION" value="save"></input>
<input type="submit" value="%s" class="net_button">
<input id="lt" name="lt" value="$lt" type="hidden"></input>
</td>
</table>
</form>

END
,
_('Mail notify'),
_('notify using default email address'),
_('notify using custom email address'),
_('do not notify'),
_('Mail recipient address'),
_('Save')
;
    &closebox(); 
    &closebigbox();
}
&getcgihash(\%par);
&showhttpheaders();

&openpage(_('eventwarn'), 1,'<script language="javascript" type="text/javascript" src="/include/event-setting.js"></script>');

&save();
&display();
check_form();
closepage();

