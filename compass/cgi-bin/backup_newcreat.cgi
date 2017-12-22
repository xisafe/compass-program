#!/usr/bin/perl
#===============================================================================
#
# 描述: 新建备份页面
#
# 作者: Liu Julong
# 公司：Caphseaf
# 历史：
#       2015.01.28 刘炬隆创建
#       2015.02.11 王琳修改 
#===============================================================================

require '/home/httpd/cgi-bin/backup-lib.cgi';
require '/var/efw/header.pl';
#$usbstickdetected=`cat /var/tmp/efw-backupusb 2>/dev/null`;
$virtualization=`/bin/rpm -q efw-virtualization | grep endian`;
my $validation_error = 0;
my $setting_file_newcreat = '/var/efw/backup/newcreat/settings';
my $setting_file_export = '/var/efw/backup/export/settings';
my %settings_newcreat;
my %query;
my $cmd_export_local = 'sudo /usr/local/bin/LocalExportBackfile.py -f ';
my $cmd_export_remote = 'sudo /usr/local/bin/BackupFileRemote.py -e -f ';

##################自定义js文件引用#####################
my $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/backup_newcreat.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/waiting.js"></script>
                    <script language="JavaScript" src="/include/backup_newcreat_init.js"></script>';

##################添加帮助信息##############

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
my $logDate = `date "+%Y-%m-%d"`;
&validateUser();
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
printf <<END
    <div id="mesg_box_backup" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_backup_remote" style="width: 96%;margin: 20px auto;"></div>
END
;
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
    <tr class="odd_thin">
      <td class="add-div-type">包含规则库</td>
      <td><input type='checkbox' name='RULES' checked="checked" /></td>
    </tr>
END
, _('Include configuration')
;

    #读取配置文件信息
    if ( -e $setting_file_newcreat) {
        &readhash($setting_file_newcreat, \%settings_newcreat);
    }
    my $checked_local_enable = "";
    my $checked_remote_enable = "";
    if($settings_newcreat{'LOCAL_ENABLE'} eq 'on'){
        $checked_local_enable = "checked";
    }
    if($settings_newcreat{'REMOTE_ENABLE'} eq 'on'){
        $checked_remote_enable = "checked";
    }
    my $REMOTE_HOST_FTP;
    my $USERNAME_FTP;
    my $PASSWORD_FTP;
    my $REMOTE_HOST_CAPSHEAF;
    my $USERNAME_CAPSHEAF;
    my $PASSWORD_CAPSHEAF;
    if($settings_newcreat{'REMOTE_TYPE'} eq 'ftp'){
        $REMOTE_HOST_FTP = $settings_newcreat{'REMOTE_HOST'};
        $USERNAME_FTP = $settings_newcreat{'USERNAME'};
        $PASSWORD_FTP = $settings_newcreat{'PASSWORD'};
    }else{
        $REMOTE_HOST_CAPSHEAF = $settings_newcreat{'REMOTE_HOST'};
        $USERNAME_CAPSHEAF = $settings_newcreat{'USERNAME'};
        $PASSWORD_CAPSHEAF = $settings_newcreat{'PASSWORD'};
    }
printf <<END
    <tr class="hidden_class">
        <td class="add-div-type " >%s </td>
        <td><input type='checkbox' name='DBDUMPS'  /></td>
    </tr>
    <!--<tr class="env_thin">
        <td class="add-div-type need_help" >%s $help_hash1</td>
        <td><input type='checkbox' name='LOGS' checked /></td>
    </tr>
    <tr class="odd_thin">
        <td class="add-div-type need_help">%s $help_hash2</td>
        <td><input type='checkbox' name='LOGARCHIVES' $disabled $checked />&nbsp;$note</td>
    </tr>-->
    <tr class="env_thin">
        <td class="add-div-type need_help" rowspan="2">文件备份</td>
        <td><input type='checkbox' name='LOCAL_ENABLE' value="on" $checked_local_enable />本地存储(默认)</td>
    </tr>
    <tr class="env_thin">
        <td><input type='checkbox' id="REMOTE_ENABLE" name='REMOTE_ENABLE' value="on" $checked_remote_enable onclick="change_server();"/>远程存储
          <div id="remote_server" style="margin-left:20px">
            <div style="margin-top:10px;"><input type="radio" name="REMOTE_TYPE" value="ftp" onclick="change_server_type();"/>FTP服务器</div>
            <div id="content_ftp">
              <div style="margin-top:5px;margin-left:20px;">服务器地址<input style="margin-left:10px;" type="text" name="SERVER_ADDR_FTP" value="$REMOTE_HOST_FTP"></div>
              <div style="margin-top:5px;margin-left:45px;"><span>用户名</span><input style="margin-left:10px;" type="text" name="USER_NAME_FTP" value="$USERNAME_FTP"></div>
              <div style="margin-top:5px;margin-left:45px;"><span>密&nbsp;&nbsp;&nbsp;码</span><input style="margin-left:10px;" type="password" name="PWD_FTP" value="$PASSWORD_FTP"></div>
            </div>
            <div style="margin-top:5px;"><input type="radio" name="REMOTE_TYPE" value="capsheaf" checked onclick="change_server_type();"/>顶点灾备机</div>
            <div id="content_capsheaf">
              <div style="margin-top:5px;margin-left:20px;">服务器地址<input type="text" style="margin-left:10px;" name="SERVER_ADDR_CAPSHEAF" value="$REMOTE_HOST_CAPSHEAF"></div>
              <div style="margin-top:5px;margin-left:45px;"><span>用户名</span><input type="text" style="margin-left:10px;" name="USER_NAME_CAPSHEAF" value="$USERNAME_CAPSHEAF"></div>
              <div style="margin-top:5px;margin-left:45px;"><span>密&nbsp;&nbsp;&nbsp;码</span><input type="password" style="margin-left:10px;" name="PWD_CAPSHEAF" value="$PASSWORD_CAPSHEAF"></div>
            </div>
          </div>
        </td>
    </tr>
    %s
    <tr class="odd_thin">
        <td class="add-div-type" >%s</td>
        <td><input type='text' name='REMARK' size='36' /></td>
    </tr>
    
END
, _('Include database dumps')
, _('Include log files')
, _('Include log archives')
, $virtualization eq "" ? sprintf("<input type='hidden' name='VIRTUALMACHINES' value='0' />") : 
                          sprintf("<tr><td>%s</td><td><input type='checkbox' name='VIRTUALMACHINES' checked /></td></tr>",_('Include virtual machines'))
, _('Remark')
;

print <<END
    
  </table>
END
;

closeeditorbox(_("Create Backup"), _("Cancel"), "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

printf <<END
<table class="ruleslist" id="backuplist" width="100%" cellpadding="0" cellspacing="0">
  <tr style="background-image:url('../images/con-header-bg.jpg');">
    <td colspan="5">
        <!--
        <a id="export-all-link" href="/cgi-bin/backup_newcreat.cgi?ACTION=export_local" onmouseover="append_selected_items_to_link();"><input id="btn_local" class="net_button" type="button" value="批量本地导出"/></a>
        -->
        <form style="display:inline-block" action="/cgi-bin/backup_newcreat.cgi" method="post" enctype="multipart/form-data">
            <input id="btn_local" class="net_button" type="submit" value="批量本地导出" onclick="exportFile();"/>
            <input type="hidden" value="" name="file_names">
            <input type="hidden" value="export_local" name="ACTION">
        </form>
        <input id="btn_remote" class="net_button" type="button" value="远程导出" onclick="add_panel.show();"/>
    </td>
  </tr>
  <tr>
    <td style="background-image:url('../images/con-header-bg.jpg');text-align:center;" width="5%"><input style="margin-left:3px;text-align:center;" id="cbk_checkall" type="checkbox" onclick="select_all();"></td>
    <td class='boldbase' width="20%">%s</td>
    <td class='boldbase' width="20%">%s</td>
    <td class='boldbase' width="25%">%s</td>
    <td class='boldbase' width="20%">%s</td>
  </tr>
END
, _('Creation date')
, _('Content')
, _('Remark')
, _('Actions')
;

my $j=0;
foreach my $archive (reverse glob("${backupsets}/backup-*.tar.gz.dat")){
        $j++;
}

if($j>0)
{
    my $i = 0;
    foreach my $archive (reverse glob("${backupsets}/backup-*.tar.gz.dat")) {
        my $bgcolor = "env_thin";
        $archive =~ s/\.meta$//;
        $archive =~ s/\.dat$//;
        $archive =~ /\/(backup[^\/]+)$/;
        my $basename = $1;

        $archive =~ /\/backup-(\d+)-([^\s\.]+\.[^\s]+?)-([^\.]+)\.tar\.gz/;
        my $date = $1;
        my $dns = $2;
        my $content_part = $3;

        my $content = '';
        if ($content_part =~ /settings/) {
            $content = '<span class="letter_span" title="配置备份"><a href="#">S</a></span>';
        }
        if ($content_part =~ /rules/) {
            $content .= '<span class="letter_span" title="规则库"><a href="#">R</a></span>';
        }
        #if ($content_part =~ /db/) {
        #    $content .= '<span class="letter_span" title="'.$D.'"><a href="#">D</a></span>';
        #}
        if ($content_part =~ /logs/) {
            $content .= '<span class="letter_span" title="'.$L.'"><a href="#">L</a></span>';
        }
        if ($content_part =~ /logarchive/) {
            $content .= '<span class="letter_span" title="'.$A.'"><a href="#">A</a></span>';
        }
        if ($content_part =~ /cron/) {
            $content .= '<span class="letter_span" title="自动备份"><a href="#">C</a></span>';
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
        #    $content .= '<span class="letter_span" title="'.$U.'"><a href="#">U</a></span>';
        #}
        if($i % 2 != 0)
        {
            $bgcolor = "odd_thin";
        }
        my $meta = get_meta("${archive}.meta");
        $meta =~ s/-/ - /g;
        my $remark = value_or_nbsp($meta);
        my $deal_date = substr($date,0,4)."-".substr($date,4,2)."-".substr($date,6,2)." ".substr($date,8,2).":".substr($date,10,2).":".substr($date,12,2);
        if(-e "${archive}.dat"){
printf <<END
  <tr class="$bgcolor">
    <td style="text-align:center"><input name="cbk_checkone" type="checkbox" value="$basename.dat" /></td>
    <td style="text-align:center">$deal_date</td>
    <td >$content</td>
    <td>$remark</td>
END
;

        if (-e "${archive}.dat") {
        printf <<END
    <td class="actions" style="text-align:center">
      <!--<a href="/backup/${basename}.gpg"><img class="imagebutton" border="0"  src='/images/download_encrypted.png' alt='%s' title='%s' /></a> -->
      <a href="/backup/${basename}.dat" style="display:inline-block;"><img style="margin:0px 0px 0px 0px" class="imagebutton" border="0"  src='/images/download.png' alt='%s' title='%s' /></a>
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
=cut    else {
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
      <form method='post' action='$ENV{'SCRIPT_NAME'}' onSubmit="return confirm('%s');" style="display:inline-block;">
        <input type='hidden' name='ACTION' value='remove' />
        <input type='hidden' name='ARCHIVE' value='${basename}' />
        <input class='imagebutton' type='image' name='submit' src='/images/delete.png' alt='%s' title='%s' />
      </form>
      <form method='post' action='$ENV{'SCRIPT_NAME'}' onSubmit="return confirm('%s');" style="display:inline-block;">
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
        }


        $i++;
    }
    
    printf <<END
    </table>
  <table class="list-legend" cellpadding="0" cellspacing="0" >
  <tr class="more_tr">
    <td>%s: <img src='/images/download.png' class="no-indent"/>: %s 
<img src='/images/delete.png' class="no-indent" />: %s
<img src='/images/reload.png' class="no-indent" />: %s  &nbsp; &nbsp; S:配置备份 &nbsp; R:规则库备份  &nbsp; C:自动备份
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
    no_tr(5,_('Current no content'));
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
#=cut    # import
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
=cut

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
#, _('Factory defaults')
, _('恢复出厂设置')
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
                    'check':'note|'
                }
            }
    };
    var object2 = {
       'form_name':'IMPORT',
       'option'   :{
            'IMPORT_FILE':{
                'type':'file',
                'required':'1'
            },
            'REMARK':{
                'type':'text',
                'required':'0',
                'check':'note|'
            }
        }
    };

    var check = new ChinArk_forms();
    check._main(object);

    var check2 = new ChinArk_forms();
    check2._main(object2);

    </script>
EOF
    ;
}

sub begin(){
    printf <<EOF
    <script>
      RestartService("正在生产需要导出的文件，需要一定时间，请等待.....");
    </script>
EOF
;
}
sub ends(){
    printf <<EOF
    <script>
      endmsg("文件导出成功");
    </script>
EOF
;
}

sub getqueryhash($){
    my $query = shift;
    my $query_string = $ENV{'QUERY_STRING'};
    if ($query_string ne '') {
        my @key_values = split("&", $query_string);
        foreach my $key_value (@key_values) {
            my ($key, $value) = split("=", $key_value);
            $query->{$key} = $value;
            #===对获取的值进行一些处理===#
            $query->{$key} =~ s/\r//g;
            $query->{$key} =~ s/\n//g;
            chomp($query->{$key});
        }
    }
    return;
}

sub download_backups($) {
    my $action = shift;

    if($action eq 'export_local'){
        my $file_names = $par{'file_names'};

        if ( $file_names eq "" ) {
            $errormessage = "请选择要导出的备份";
            return;
        }
        system("$cmd_export_local'$file_names'");
        if ( $? != 0 ) {
            $errormessage = "生成备份文件失败";
            return;
        }
        my $file =  '/tmp/BackupPackage.tar';
        my $filename = 'BackupPackage.tar';
        if( -e "$file"){
            open(DLFILE, "<$file") || Error('open', "$file");  
            @fileholder = <DLFILE>;  
            close (DLFILE) || Error ('close', "$file"); 
            print "Content-Type:application/x-download\n";  
            print "Content-Disposition:attachment;filename=$filename\n\n";
            print @fileholder;
            exit;
        }else{
            $errormessage = "导出文件生成失败";
            return;
        }
    }
}
&getcgihash(\%par);
my $action = $par{'ACTION'};
if($action eq 'export_local'){
    download_backups( $action );
}

&getcgihash(\%par, {'wantfile' => 1, 'filevar' => 'IMPORT_FILE'});
$action = $par{'ACTION'};
&getqueryhash(\%query);
if( !$action ) {
    $action = $query{'ACTION'};
}

&showhttpheaders();
if($action eq 'export_remote'){
    my %hash_export;
    if ( -e $setting_file_export) {
        &readhash($setting_file_export, \%hash_export);
    }
    $hash_export{'REMOTE_HOST'} = $par{'remote_addr_export'};
    $hash_export{'USERNAME'} = $par{'username_export'};
    $hash_export{'PASSWORD'} = $par{'password_export'};
    
    # if ( $hash_export{'REMOTE_HOST'} ) {
        
    # }

    &writehash($setting_file_export,\%hash_export);
    my $file_names = $par{'file_names'};
    system("$cmd_export_remote'$file_names'");
    #my $cmd_run = "$cmd_export_remote '$file_names' -d";
    # `$cmd_run`;
    # print $cmd_run;
    # print $?;
    #`$cmd_run`;
    my $result = "远程导出失败";
    if($? == 0 ){
        $result = "远程导出成功";
    }
    print $result;
    exit;
}
&openpage(_('Backup configuration'), 1, $extraheader);
if ( -e "${swroot}/backup/default/settings") {
    &readhash("${swroot}/backup/default/settings", $conf);
}
if ( -e "${swroot}/backup/settings") {
    &readhash("${swroot}/backup/settings", $conf);
}
my $reboot = doaction();
if($par{'ACTION'} eq 'create')
{
    #保存新增字段到配置文件中，modified by Liu Julong,2015/01/29
    my $local_enable = "off";
    my $remote_enable = "off";
    if($par{'LOCAL_ENABLE'} eq 'on'){
        $local_enable = "on";
    }
    if($par{'REMOTE_ENABLE'} eq 'on'){
        $remote_enable = "on";
    }
    $settings_newcreat{'LOCAL_ENABLE'} = $local_enable;
    $settings_newcreat{'REMOTE_ENABLE'} = $remote_enable;
    $settings_newcreat{'REMOTE_TYPE'} = $par{'REMOTE_TYPE'};
    if($settings_newcreat{'REMOTE_TYPE'} eq 'ftp'){
        $settings_newcreat{'REMOTE_HOST'} = $par{'SERVER_ADDR_FTP'};
        $settings_newcreat{'USERNAME'} = $par{'USER_NAME_FTP'};
        $settings_newcreat{'PASSWORD'} = $par{'PWD_FTP'};
    }else{
        $settings_newcreat{'REMOTE_HOST'} = $par{'SERVER_ADDR_CAPSHEAF'};
        $settings_newcreat{'USERNAME'} = $par{'USER_NAME_CAPSHEAF'};
        $settings_newcreat{'PASSWORD'} = $par{'PWD_CAPSHEAF'};
    }
    
    # if( !(-e $setting_file_newcreat)){
        # `touch $setting_file_newcreat`;
    # }
    &writehash($setting_file_newcreat,\%settings_newcreat);
    
    #if($par{'SETTINGS'} || $par{'LOGS'} || $par{'LOGARCHIVES'})
    if($par{'SETTINGS'})
    {
        $notemessage = _("备份正在生成,由于生成备份需要一定的时间,<br />所以若备份列表中没有生成新备份内容,请稍作等待后刷新本页面即可");
    }
    if($errormessage eq 'nospace'){
        $errormessage = '';
        $notemessage = _("当前备份数已达到系统最大限制，如需备份，请先删除部分备份文件");
    }
}

if($errormessage eq 'nospaceforCF'){
    $errormessage = '';
    $notemessage = _("当前备份数已达到系统最大限制，但恢复备份时需要创建一个当前备份，如需还原备份，请先删除部分备份文件");
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

