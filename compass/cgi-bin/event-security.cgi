#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 安全事件页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================
require '/var/efw/header.pl';
use warnings;
use File::Copy;

my $dir = '/var/efw/sec/'; 
my $default_eventwarn = $dir.'eventwarn/default/event-warn'; 
my $mail_address = $dir.'eventwarn/mail-address';
my $event_warn = $dir.'eventwarn/event-warn';
my $need = $dir.'eventwarn/reload-eventwarn';
my $needload = 'n'; #load applybox while F5
my $ENABLED = '/images/mail_enabled.png'; #open picture
my $DISABLED = '/images/mail_disabled.png'; #close picture

my $disabled_picture = $ENABLED;
my @errormessage = ();
my $status = 'on';
my %par;

my %securityEvents = (); #

my @help_hash;
$help_hash[0] = read_json("/home/httpd/help/event-security_help.json","event-security.cgi","系统-事件告警-安全事件-磁盘空间已满","-10","10","down");

$help_hash[1] = read_json("/home/httpd/help/event-security_help.json","event-security.cgi","系统-事件告警-安全事件-系统备份","-10","10","down");

$help_hash[2] = read_json("/home/httpd/help/event-security_help.json","event-security.cgi","系统-事件告警-安全事件-有uplink连接","-10","10","down");

$help_hash[3] = read_json("/home/httpd/help/event-security_help.json","event-security.cgi","系统-事件告警-安全事件-有uplink断开","-10","10","down");

$help_hash[4] = "";

$help_hash[5] = read_json("/home/httpd/help/event-security_help.json","event-security.cgi","系统-事件告警-安全事件-系统关闭","-10","10","down");

$help_hash[6] = read_json("/home/httpd/help/event-security_help.json","event-security.cgi","系统-事件告警-安全事件-系统重启","-10","10","down");

$help_hash[7] = "";

$help_hash[8] = "";

$help_hash[9] = read_json("/home/httpd/help/event-security_help.json","event-security.cgi","系统-事件告警-安全事件-Uplink失效","-10","10","down");

$help_hash[10] = read_json("/home/httpd/help/event-security_help.json","event-security.cgi","系统-事件告警-安全事件-Uplink恢复成功","-10","10","down");

#read file info
sub read_file($) {
    my $filename = shift;
    my @lines;
    open(FILE, "<$filename");
    foreach my $line (<FILE>){
		chomp($line);
#		$line =~ s/[\r\n]//g;
        if(is_valid($line)) {
			next;
		}
		push(@lines, $line);
    }
    close (FILE);
    return @lines;
} 
sub is_valid($) { #string with ","
    my $line = shift;
    if ($line =~ /(?:(?:[^,]*),){9}/) {
        return 1;
    }
    return 0;
}

#copy file ,first src_file,second dest_file
sub copy_file($$) 
{
   my $originFile = shift;
   my $copyFile = shift;
   if(!(-e $copyFile)){
        system("touch $copyFile");
   }
   my @lines = &read_file($originFile);
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

#read one line from file
sub read_file_line($$) 
{   
    my $filename = shift;
    my $line = shift;
    my @lines = read_file($filename);
    return $lines[$line];
}

sub save_file($) { 
	my $filename = shift;
	&copy_file($filename,"$filename.old"); #save file to file.old
	
    open(FILE, ">$filename"); #save updated info
	foreach my $key (sort keys %securityEvents) 
	{
	   $tmpValue = "$key,$securityEvents{$key}->{'descript'},$securityEvents{$key}->{'status'}";
	   print FILE "$tmpValue\n";
	}
    close(FILE);
   `sudo fmodify $filename`;
}


sub save()
{
	my $action = $par{'ACTION'};
	my $file;
    if(-e $event_warn){
        $file = $event_warn;
    }else{
        $file = $default_eventwarn;
    }
	my @conf_lines = read_file($file); #read config
    foreach my $thisline (@conf_lines)
    {
		chomp($thisline);
	    my ($tmp1,$tmp2,$tmp3) = split(/,/,$thisline);
		$securityEvents{$tmp1}->{'descript'} = $tmp2;
		$securityEvents{$tmp1}->{'status'} = $tmp3;
	}
	
   if($action eq "apply") {
		&log(_("change eventwarn"));
		$notemessage = _("change successfully!");
		system("rm $need");
		system("/usr/local/bin/restartsec &>/dev/null");
		return ;
	}elsif($action eq "")
	{   
		if(-e $need){ #
            &applybox(_('configures have been changed and need to be applied in order to make the changes active!'));
        }   			
    }else{
       foreach my $key (sort keys %securityEvents)
    	{
    		if($action eq $key)
    		{
				$needload = 'y'; 
				if($securityEvents{$action}->{'status'} eq 'on')
				{ 
					$securityEvents{$action}->{'status'} = 'off';
				}else{
					$securityEvents{$action}->{'status'} = 'on';
				}
			}
		}
		&applybox(_('configures have been changed and need to be applied in order to make the changes active!'));
		if(!(-e $event_warn)){
			system("touch $event_warn");
			`sudo fmodify $event_warn`;
		}
		&save_file($event_warn); 		
   }
}

sub display()
{

printf <<END
<br />                      
<table class="ruleslist" cellpadding="0" cellspacing="0" border="0">  
<tr>
<td class="boldbase" width="12%">%s</td>
<td class="boldbase" width="88%">%s</td>
</tr>
END
,_('事件描述')
,_('Actions')
;
    my $lines = 0;

	foreach my $key (sort keys %securityEvents)
	{
	    if($securityEvents{$key}->{'status'} eq 'on'){
		    $disabled = $ENABLED;
	    }else{
		    $disabled = $DISABLED;
	    }
	    my $color = 'odd';
	    if($lines % 2 == 0){
		    $color = 'env';
	    }
      my $descript = _($securityEvents{$key}->{'descript'}); 
      if ($descript eq "有uplink连接") {
        $descript = "上行线路连接启用";
      }
      if ($descript eq "有uplink断开") {
        $descript = "上行线路连接断开";
      }
      if ($descript eq "磁盘空间已满") {
        $descript = "磁盘空间将满";
      }
      $descript =~s /Uplinks|Uplink/上行线路/;

printf <<END
   <tr class='$color'>
         <td class="add-div-width need_help">%s $help_hash[$lines]</td>
         <td align="center">
             <form method="post" action="$ENV{'SCRIPT_NAME'}" style="width:20px;display:block;margin:0px auto;">
             <input type="hidden" name="ACTION" value="$key"/>
             <input class="imagebutton" name='submit' type='image' src=$disabled border="0"/>   
            </form>     
         </td>
    </tr>
END
,$descript
;
$lines++;
    }

printf <<END

</tbody>
<tr class="table-footer"><td colspan="2">&nbsp;</td></tr>
</table>
END
;

}

showhttpheaders();
&getcgihash(\%par);
&openpage(_('eventwarn'), 1,'');
&save();
if( $needload eq 'y')
{
	system("touch $need");
}

&display();

&closebigbox();
&closepage();

