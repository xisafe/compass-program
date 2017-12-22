#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 备份页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
# modify by:zhouyuan
# date:2011-07-14
# 修改目的 ：同一页面显示风格 
#===============================================================================




require '/home/httpd/cgi-bin/backup-lib.cgi';
require '/var/efw/header.pl';
#$usbstickdetected=`cat /var/tmp/efw-backupusb 2>/dev/null`;
$virtualization=`/bin/rpm -q efw-virtualization | grep endian`;
my $validation_error = 0;

##################周圆 2011-09-27 添加帮助信息##############

my $help_hash1 = read_json("/home/httpd/help/backup_help.json","backup.cgi","代理-系统-系统备份-新建备份-包含日志文件","-10","10","down");

my $help_hash2 = read_json("/home/httpd/help/backup_help.json","backup.cgi","代理-系统-系统备份-新建备份-包含日志档案","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/backup_help.json","backup.cgi","代理-系统-系统备份-加密备份文件","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/backup_help.json","backup.cgi","代理-系统-系统备份-出厂配置","-10","10","down");

############################################################


my $S = _('Settings');
my $D = _('Database dumps');
my $E = _('Archive is encrypted');
my $L = _('Log files');
my $A = _('Log archives');
my $err = _('Error sending backup');
my $C = _('Created automatically with a Schedule');
my $U = _('Backup is on USB Stick');
my $have_tar = 0;

#if ( ! -x "/usr/local/bin/efw-backupusb" ) {
#    undef $usbstickdetected;
#}

#判断当前日志是否有压缩文件 zhouyuan-2021-10-28#########
sub check_is_tar()
{
	opendir(DIR,"/var/log");
	my @dir=readdir(DIR);
	closedir(DIR);
	foreach $file(@dir)
	{
		if($file =~ /gz$/ || $file =~ /tar$/)
		{
			$have_tar = 1;
			last;
		}else{
			opendir(DIRS,"/var/log/".$file);
			my @temp_dir=readdir(DIRS);
			closedir(DIRS);
			foreach $files(@temp_dir)
			{
				if($files =~ /gz$/ || $files =~ /tar$/)
				{
					$have_tar = 1;
					last;
				}
			}
		}
	}
}
########################################################
sub display() { 

&openeditorbox(_('Create new Backup'), _("Create new Backup"), "", "createrule", @errormessages);
#openbox('100%', 'left', _('Create new Backup'));
check_is_tar();
my $disabled = "";
my $checked = "checked";
my $note = "";
if(!$have_tar)
{
	$disabled = "disabled";
	$checked = "";
	$note = "当前无压缩文件";
}
printf <<END
</form>
		<form name="BACKUP_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
  <input type='hidden' name='ACTION' value='create' />
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr class="env_thin">
      <td class="add-div-type">%s </td>
      <td><input type='checkbox' name='SETTINGS' checked="checked" /></td>
	  </tr>
END
, _('Include configuration')
;


printf <<END
    <tr class="hidden_class">
        <td class="add-div-type " >%s </td>
        <td><input type='checkbox' name='DBDUMPS'  /></td>
    </tr>
    <tr class="odd_thin">
        <td class="add-div-type need_help" >%s $help_hash1</td>
        <td><input type='checkbox' name='LOGS' checked /></td>
    </tr>
    <tr class="env_thin">
        <td class="add-div-type need_help">%s $help_hash2</td>
        <td><input type='checkbox' name='LOGARCHIVES' $disabled $checked />&nbsp;$note</td>
    </tr>
    %s
    <tr class="odd_thin">
        <td class="add-div-type" >%s</td>
        <td><input type='text' name='REMARK' size='30' /></td>
    </tr>
    <tr>
END
, _('Include database dumps')
, _('Include log files')
, _('Include log archives')
, $virtualization eq "" ? sprintf("<input type='hidden' name='VIRTUALMACHINES' value='0' />") : 
                          sprintf("<tr><td>%s</td><td><input type='checkbox' name='VIRTUALMACHINES' checked /></td></tr>",_('Include virtual machines'))
, _('Remark')
;

print <<END
    </tr>
  </table>
END
;

closeeditorbox(_("Create Backup"), _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

printf <<END
<table class="ruleslist" id="backuplist" width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td class='boldbase' width="25%">%s</td>
    <td class='boldbase' width="25%">%s</td>
    <td class='boldbase' width="30%">%s</td>
    <td class='boldbase' width="20%">%s</td>
  </tr>
END
, _('Creation date')
, _('Content')
, _('Remark')
, _('Actions')
;

my $j=0;
foreach my $archive (reverse glob("${backupsets}/backup-*.tar.gz*meta")){
		$j++;
}

if($j>0)
{
	my $i = 0;
	foreach my $archive (reverse glob("${backupsets}/backup-*.tar.gz*meta")) {
		my $bgcolor = "env_thin";
		$archive =~ s/\.meta$//;
		$archive =~ /\/(backup[^\/]+)$/;
		my $basename = $1;

		$archive =~ /\/backup-(\d+)-([^\s\.]+\.[^\s]+?)-([^\.]+)\.tar\.gz/;
		my $date = $1;
		my $dns = $2;
		my $content_part = $3;

		my $content = '';
		if ($content_part =~ /settings/) {
			$content = '<span class="letter_span" title="'.$S.'"><a href="#">S</a></span>';
		}
		#if ($content_part =~ /db/) {
		#	$content .= '<span class="letter_span" title="'.$D.'"><a href="#">D</a></span>';
		#}
		if ($content_part =~ /logs/) {
			$content .= '<span class="letter_span" title="'.$L.'"><a href="#">L</a></span>';
		}
		if ($content_part =~ /logarchive/) {
			$content .= '<span class="letter_span" title="'.$A.'"><a href="#">A</a></span>';
		}
		if ($content_part =~ /cron/) {
			$content .= '<span class="letter_span" title="'.$C.'"><a href="#">C</a></span>';
		}
		if ($content_part =~ /virtualmachines/) {
			$content .= '<span class="letter_span" title="'.$V.'"><a href="#">V</a></span>';
		}
		if (-e "${archive}.gpg") {
			$content .= '<span class="letter_span" title="'.$E.'"><a href="#">E</a></span>';       
		}
		if (-e "${archive}.mailerror") {
			$content .= '<span class="letter_span" title="'.$err.'"><a href="#">!</a></span>';
		}
		if (-e "${archive}.gpg.mailerror") {
			$content .= '<span class="letter_span" title="'.$err.'"><a href="#">!</a></span>';
		}
		#if (-l "${archive}.meta") {
		#	$content .= '<span class="letter_span" title="'.$U.'"><a href="#">U</a></span>';
		#}
		if($i % 2 != 0)
		{
			$bgcolor = "odd_thin";
		}
		my $meta = get_meta("${archive}.meta");
		$meta =~ s/-/ - /g;
		my $remark = value_or_nbsp($meta);
		my $deal_date = substr($date,0,4)."-".substr($date,4,2)."-".substr($date,6,2)." ".substr($date,8,2).":".substr($date,10,2).":".substr($date,12,2);
printf <<END
  <tr class="$bgcolor">
    <td>$deal_date</td>
    <td >$content</td>
    <td>$remark</td>
END
;

		if (-e "${archive}.gpg") {
        printf <<END
    <td class="actions">
      <a href="/backup/${basename}.gpg"><img class="imagebutton" border="0"  src='/images/download_encrypted.png' alt='%s' title='%s' /></a>
     <!-- <a href="/backup/${basename}"><img class="imagebutton" border="0"  src='/images/download.png' alt='%s' title='%s' /></a> -->
END
, _('Export encrypted archive')
, _('Export encrypted archive')
#, _('Export plain archive')
#, _('Export plain')
;
		} 
		else{
			print "<td>";
		}
=cut	else {
        printf <<END
    <td>
      <a href="/backup/${basename}"><img class="imagebutton" border="0" src='/images/download.png' alt='%s' title='%s' /></a>
END
, _('Export')
, _('Export')
;
	}
=cut
printf <<END
      <form method='post' action='$ENV{'SCRIPT_NAME'}' onSubmit="return confirm('%s');">
        <input type='hidden' name='ACTION' value='remove' />
        <input type='hidden' name='ARCHIVE' value='${basename}' />
        <input class='imagebutton' type='image' name='submit' src='/images/delete.png' alt='%s' title='%s' />
      </form>
      <form method='post' action='$ENV{'SCRIPT_NAME'}' onSubmit="return confirm('%s');">
        <input type='hidden' name='ACTION' value='restore' />
        <input type='hidden' name='ARCHIVE' value='${basename}' />
        <input class='imagebutton' type='image' name='submit' src='/images/reload.png' alt='%s' title='%s' />
      </form>
    </td>
  </tr>
END
, _('Do you really want to remove the backup archive %s?', $basename)
, _('Delete')
, _('Delete')
, _('Do you really want to restore the backup archive %s? All existing data will be overwritten and then %s %s will reboot!', $basename,$brand,$product )
, _('Restore')
, _('Restore')
;

		$i++;
	}
	
	printf <<END
	</table>
  <table class="list-legend" cellpadding="0" cellspacing="0" >
  <tr class="more_tr">
    <td>%s: <img src='/images/download_encrypted.png' class="no-indent"/>: %s
<img src='/images/delete.png' class="no-indent" />: %s
<img src='/images/reload.png' class="no-indent" />: %s  &nbsp; &nbsp; S:配置备份 &nbsp; L:日志备份  &nbsp; C:自动备份  &nbsp; E:加密备份文件  &nbsp; A:日志档案备份
</td>
  </tr>
</table>
END
, _('Legend')
, _('下载存档')
, _('Delete archive')
, _('Restore archive')
;
}else{
	no_tr(4,_('Current no content'));
	print "</table>";
}


print "<br /><br />";
=cut# import gpgkey
openbox('100%', 'left', _('Encrypt backup archives with a GPG public key'));
printf <<EOF
  <form  name="GPG"  method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
  <input type='hidden' name='ACTION' value='gpgkey' />
  <table width="100%" cellpadding="0" cellspacing="0" >
EOF
;
	my $note_img = "";
    if ($conf->{'BACKUP_ENCRYPT'} !~ /^$/) {
        my ($r, $e, $keyinfo) = call("$gpgwrap --show-key ".$conf->{'BACKUP_GPGKEY'});
        my $keyinfo_sanitized = cleanhtml($keyinfo, 'y');
		if($keyinfo_sanitized ne "")
		{
        printf <<END
<tr class="odd"><td colspan="2" ><div style="width:98%;border:1px solid green;margin:3px auto;padding:3px 5px;"><p class="note">%s </p>$keyinfo_sanitized</div></td></tr>
END
, _('The following GPG public key will be used to encrypt the backup archives')
;
	$note_img = "";
}
	
    }
printf <<END

    <tr class="env">
      <td class="add-div-type need_help" rowspan="1" width="30%">%s $help_hash3</td>
      <td><input type='checkbox' name='BACKUP_ENCRYPT' $checked{$conf->{'BACKUP_ENCRYPT'}} value='on' /></td>
    </tr>
    <tr class="odd">
      <td class="add-div-type" rowspan="1" >%s $note_img</td>
      <td><input type='file' name='IMPORT_FILE' size='40' /></td>
    </tr>
    <tr class="table-footer">
      <td colspan="2"><input class='net_button' type='submit' name='submit' value='%s'   /></td>
    </tr>
  </table>
  </form>
END
, _('Encrypt backup archives')
, _('Import GPG public key')
, _('Save')
;
    closebox();
=cut    # import
    openbox('100%', 'left', _('Import backup archive'));
printf <<END
  <form name="IMPORT" method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
  <input type='hidden' name='ACTION' value='import' />
  <table width="100%" cellpadding="0" cellspacing="0" >
    <tr class="env">
      <td class="add-div-type"  rowspan="1" >%s</td>
      <td><input type='file' name='IMPORT_FILE' size='40' /></td>
    </tr>
    <tr class="odd">
      <td class="add-div-type"  rowspan="1"  >%s</td>
      <td><input type='text' name='REMARK' size='40' /></td>
    </tr>
    <tr class="table-footer"> 
      <td colspan="2"><input class='net_button' type='submit' name='submit' value='%s' /></td>
    </tr>
  </table>
  </form>
END
, _('File')
, _('Remark')
, _('Import')
;
    closebox();


    # factory default
    if (-e $factoryfile) {
        openbox('100%', 'left', _('恢复出厂设置'));
        printf <<END
  <form method='post' action='$ENV{'SCRIPT_NAME'}' onSubmit="return confirm('%s');">
    <input type='hidden' name='ACTION' value='factory' />
    <table cellpadding="0" cellspacing="0" width="100%">
	<tr class="env">
	<td class="need_help"  align="center">
      <input class='net_button' type='submit' name='submit' value='%s' />
    $help_hash4</td></tr>
	</table>
  </form>
END
, _('Do you really want to reset to factory defaults?')
, _('Factory defaults')
;
        closebox();
    }
}

sub check_form()
{
#表单检查代码添加-2012-08-30-zhouyuan
printf <<EOF
<script>	
var object = {
       'form_name':'BACKUP_FORM',
       'option'   :{
                    'REMARK':{
                               'type':'text',
                               'required':'0',
                               'check':'note|',
                             },
                 }
         }
var object2 = {
       'form_name':'IMPORT',
       'option'   :{
                    'IMPORT_FILE':{
                               'type':'file',
                               'required':'1',
                             },
                    'REMARK':{
                               'type':'text',
                               'required':'0',
                               'check':'note|',
                             },
                 }
         }

var check = new ChinArk_forms();
check._main(object);

var check2 = new ChinArk_forms();
check2._main(object2);

</script>
EOF
;
}


&getcgihash(\%par, {'wantfile' => 1, 'filevar' => 'IMPORT_FILE'});
&showhttpheaders();
&openpage(_('Backup configuration'), 1, '');
if ( -e "${swroot}/backup/default/settings") {
    &readhash("${swroot}/backup/default/settings", $conf);
}
if ( -e "${swroot}/backup/settings") {
    &readhash("${swroot}/backup/settings", $conf);
}
my $reboot = doaction();
if($par{'ACTION'} eq 'create')
{
	if($par{'SETTINGS'} || $par{'LOGS'} || $par{'LOGARCHIVES'})
	{
		$notemessage = _("备份正在生成,由于生成备份需要一定的时间,<br />所以若备份列表中没有生成新备份内容,请稍作等待后刷新本页面即可");
	}
}
&openbigbox($errormessage, $warnmessage, $notemessage);
if ($reboot == 0) {
  display();
} else {
  display_reboot();
}
&check_form();
closebigbox();
closepage();
exit 0;

