#!/usr/bin/perl
#
#author:刘炬隆（Liu Julong）
#
#date:2015/04/20
#
#description:发送邮件过滤全局设置页面
require '/var/efw/header.pl';
my $custom_dir = 'smtpscan';
my $conf_dir = '/var/efw/'.$custom_dir;
my $conf_file = $conf_dir.'/basic_settings';
my $needreload = '/var/efw/'.$custom_dir.'/needreload';
my $restart = '/usr/local/bin/restartsmtpscan';
my $cmd = "sudo /usr/local/bin/judge_virus_enable.py -m clamav";
my $reload = 0;
my %par;
my %settings;
my $extraheader;
my $errormessage = "";
my $notemessage = "";
my $status_havp = "off";
my $json = new JSON::XS;

sub display(){
    &create_mesg_boxs();
    if( -f $conf_file ) {
        &readhash( $conf_file, \%settings );
    }
    system("$cmd");
    if($? >> 8 == 0){
        $status_havp = "on";
    }
    #装配数据
    my ($is_checked_av,$is_checked_bomb,$is_checked_efilter,$is_checked_ext,$is_checked_key,$is_checked_sa,$is_checked_de) = ("","","","","","","");
    if($settings{'SMTPSCAN_ENABLED'} eq 'on'){
        $is_checked_efilter = "checked";
    }
    if($settings{'SA_ENABLED'} eq 'on'){
        $is_checked_sa = "checked";
    }
    if($settings{'AV_ENABLED'} eq 'on' && $status_havp eq 'on'){
        $is_checked_av = "checked";
    }
    if($settings{'GARBAGE_BOMB'} eq 'on'){
        $is_checked_bomb = "checked";
    }
    if($settings{'EXT_ENABLED'} eq 'on'){
        $is_checked_ext = "checked";
    }
    if($settings{'KEY_FILTER'} eq 'on'){
        $is_checked_key = "checked";
    }
    if($settings{'DE_ENABLED'} eq 'on'){
        $is_checked_de = "checked";
    }
    
    #装配拦截文件类型
    my ($is_checked_exe,$is_checked_pdf,$is_checked_ppt,$is_checked_dat,
        $is_checked_tar,$is_checked_doc,$is_checked_docx,$is_checked_html,
        $is_checked_zip,$is_checked_xls) = ("","","","","","","","","","");
    my @bannedeiles = split(/\|/,$settings{'BANNEDFILES'});
    foreach(@bannedeiles){
        if($_ eq 'exe'){
            $is_checked_exe = "checked";
        }elsif($_ eq 'pdf'){
            $is_checked_pdf = "checked";
        }elsif($_ eq 'ppt'){
            $is_checked_ppt = "checked";
        }elsif($_ eq 'dat'){
            $is_checked_dat = "checked";
        }elsif($_ eq 'tar'){
            $is_checked_tar = "checked";
        }elsif($_ eq 'doc'){
            $is_checked_doc = "checked";
        }elsif($_ eq 'docx'){
            $is_checked_docx = "checked";
        }elsif($_ eq 'html'){
            $is_checked_html = "checked";
        }elsif($_ eq 'zip'){
            $is_checked_zip = "checked";
        }elsif($_ eq 'xls'){
            $is_checked_xls = "checked";
        }
        
    }
    
    my $val_bannedeiles_user = $settings{'BANNEDFILES_USER'};
    $val_bannedeiles_user =~ s/\|/\n/g;
    
openbox('100%', 'left', _('全局配置'));
printf <<EOF
    <form name="EMAIL_FILTER_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="table-footer">
    <td colspan="2" style="text-align:left;">
      <input type="checkbox" name="SMTPSCAN_ENABLED" $is_checked_efilter value="on"/>
      <span>启用邮件过滤功能</span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type" style="width:250px">垃圾邮件过滤</td>
    <td><input type="checkbox" name='SA_ENABLED' $is_checked_sa value="on"/><span>启用</span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">病毒邮件扫描</td>
    <td><input type="checkbox" id="AV_ENABLED" name='AV_ENABLED' $is_checked_av value="on"/>
      <span>启用</span>
      <span id="label_tip" style="color:red;"></span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">邮件关键字过滤</td>
    <td><input type="checkbox" id="KEY_FILTER" name='KEY_FILTER' $is_checked_key value="on"/><span>启用</span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">防邮件炸弹</td>
    <td>
      <input type="checkbox" id="GARBAGE_BOMB" name='GARBAGE_BOMB' $is_checked_bomb value="on" onclick="change_show_bomb();"/><span>启用</span>
      <div class="ctr_bomb">
        <span>发送邮件单位时间</span><input type="text" id="TIME" name="TIME" value="$settings{'TIME'}"/>
        <span>s（默认：60）</span>
      </div>
      <div class="ctr_bomb">
        <span>该时间类允许发送的邮件上限</span><input type="text" id="CLIENT_LIMIT" name="CLIENT_LIMIT" value="$settings{'CLIENT_LIMIT'}"/>
        <span>封（默认：10）</span>
      </div>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">邮件附件类型过滤</td>
    <td>
      <input type="checkbox" id="EXT_ENABLED" name='EXT_ENABLED' $is_checked_ext value="on" onclick="change_show_ext();"/><span>启用</span>
      <div class="ctr_ext">
        <div style="margin-left:20px;">拦截文件类型（扩展名）</div>
        <div style="margin-left:40px;">
          <span><input type="checkbox" name="BANNEDFILES" value="exe" $is_checked_exe/>exe</span>
          <span><input type="checkbox" name="BANNEDFILES" value="pdf" $is_checked_pdf/>pdf</span>
          <span><input type="checkbox" name="BANNEDFILES" value="ppt" $is_checked_ppt/>ppt</span>
          <span><input type="checkbox" name="BANNEDFILES" value="dat" $is_checked_dat/>dat</span>
          <span><input type="checkbox" name="BANNEDFILES" value="tar" $is_checked_tar/>tar</span>
        </div>
        <div style="margin-left:40px;">
          <span><input type="checkbox" name="BANNEDFILES" value="doc" $is_checked_doc/>doc</span>
          <span><input type="checkbox" name="BANNEDFILES" value="docx" $is_checked_docx/>docx</span>
          <span><input type="checkbox" name="BANNEDFILES" value="html" $is_checked_html/>html</span>
          <span><input type="checkbox" name="BANNEDFILES" value="zip" $is_checked_zip/>zip</span>
          <span><input type="checkbox" name="BANNEDFILES" value="xls" $is_checked_xls/>xls</span>
        </div>
        <div style="margin-left:40px;">
          <div>用户自定义（例如：exe,每行一个）</div>
          <textarea id="BANNEDFILES_USER" name="BANNEDFILES_USER">$val_bannedeiles_user</textarea>
        </div>
      </div>
      <div style="margin-left:20px;" class="ctr_ext">
        </span><input type="checkbox" id="DE_ENABLED" $is_checked_de name="DE_ENABLED" value="on"/>
        <span>启用拦截文件双重扩展名</span>
      </div>
    </td>
    </tr>
    <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save"></input>
      <input type="submit" class="net_button" value="保存" align="middle"/>
      <!--<input type="reset" class="net_button" value="重置" align="middle"/>-->
    </td>
    </tr>
    </table>
    </form>
EOF
;
&closebox();

}



sub do_action(){
    my $action = $par{'ACTION'};
    
    if ($action eq 'apply') {            
        &showhttpheaders();
        #my $result=`$restart`;#重启服务
        system($restart);
        my $result = $?;
        #chomp($result);
        `rm $needreload`;
        if($result == 0){
            $notemessage = "规则应用成功";#此行消息可以自定义
        }else{
            $notemessage = "规则应用失败"; #此行消息可以自定义
        }
        &openpage(_('全局配置'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
    
    if($action eq 'save') {
        my @data_save;
        my @conf_keys = ("SMTPSCAN_ENABLED","SA_ENABLED","AV_ENABLED","KEY_FILTER","GARBAGE_BOMB","TIME","CLIENT_LIMIT","EXT_ENABLED","BANNEDFILES","BANNEDFILES_USER","DE_ENABLED");
        if($par{'SMTPSCAN_ENABLED'} ne 'on'){
            #delete $conf_keys[0];
            splice(@conf_keys,0,1);
        }
        my $length = @conf_keys;
        for(my $i=0;$i<$length;$i++){
            my $value_form = $par{$conf_keys[$i]};
            if($conf_keys[$i] eq 'BANNEDFILES_USER'){
                my $file_user = $par{'BANNEDFILES_USER'};
                $file_user =~ s/\r//g;
                $file_user =~ s/\n/\|/g;
                if($file_user){
                    $value_form = $file_user;
                }
            }
            if($conf_keys[$i] eq 'AV_ENABLED'){
                if($par{'AV_ENABLED'} eq 'on'){
                    $value_form = "on";
                }else{
                    $value_form = $status_havp;
                }
            }
            
            my $item = $conf_keys[$i].'='.$value_form;
            push (@data_save,$item);
        }
        
        if( -f $conf_file ) {
            &readhash( $conf_file, \%settings );
        }
        push (@data_save,"RBL=$settings{'RBL'}");
        push (@data_save,"FINAL_BANNED_DESTINY=$settings{'FINAL_BANNED_DESTINY'}");
        &save_data_to_file(\@data_save,$conf_file);
        
        # my %hash_tmp = %settings;
        # &readhash( $conf_file, \%settings );
        # $settings{'RBL'} = $hash_tmp{'RBL'};
        # $settings{'FINAL_BANNED_DESTINY'} = $hash_tmp{'FINAL_BANNED_DESTINY'};
        # &writehash( $conf_file, \%settings );
        $reload = 1;
    }
    
    if($action eq 'enable_smtpscan'){
        system($restart);
    }
    
    if ($action eq 'judge_havp') {
        #==判断启用杀毒==#
        &showhttpheaders();
        &judge_havp();
    }
    
    if($action ne 'apply' && $action ne 'judge_havp') {
        &showhttpheaders(); 
        &openpage(_('全局配置'),1,$extraheader); 
        &reload();
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}
#初始化数据
sub init_data(){
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/email_filter_setting_controller.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />';
    &make_file();
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $conf_file){
        `touch $conf_file`;
    }
}

sub create_mesg_boxs() {
    printf <<EOF
    <div id="all-mesg-box">
        <div id="apply-mesg-box" class="mesg-box">
            <div class="mesg-box-main">
                <img src="/images/pop_apply.png"/>
                <span id="apply-mesg" class="mesg-body">规则已改变,需应用该规则以使改变生效</span>
            </div>
            <div class="mesg-box-foot">
                <button id="apply-config" onclick="apply_config();">应用</button>
            </div>
        </div>
        <div id="note-mesg-box" class="mesg-box tips-mesg-box">
            <img src="/images/Emoticon.png"/>
            <span id="note-mesg" class="mesg-body">操作成功</span>
        </div>
        <div id="warn-mesg-box" class="mesg-box tips-mesg-box">
            <img src="/images/dialog-warning.png"/>
            <span id="warn-mesg" class="mesg-body">操作有误</span>
        </div>
        <div id="error-mesg-box" class="mesg-box tips-mesg-box">
            <img src="/images/pop_error.png"/>
            <span id="error-mesg" class="mesg-body">操作失败</span>
        </div>
        <div id="popup-mesg-box-back" class="popup-cover"></div>
        <div id="popup-mesg-box" class="popup-mesg-box">
            <div class="popup-mesg-box-head-tool">
                <span class="tool-right">
                    <img id="close-popup-mesg-box" src="/images/close_mesg_box.png" onclick="hide_detail_error_mesg();"/>
                </span>
            </div>
            <table class="rule-list popup-mesg-box-table">
                <thead class="popup-mesg-box-toolbar">
                    <tr class="popup-mesg-box-thead">
                        <td>导入错误信息如下</td>
                    </tr>
                </thead>
                <tbody id="popup-mesg-tbody" class="popup-mesg-box-tbody">
                </tbody>
                <tfoot class="popup-mesg-box-toolbar">
                    <tr class="popup-mesg-box-tfoot">
                        <td><input type="button" class="net_button" value="确定" onclick="hide_detail_error_mesg();"/></td>
                    </tr>
                </tfoot>
            </table>
        </div>
        <div id="popup-mesg-box-loading" class="popup-mesg-box">
            <img src="/images/ajax_loading.gif"/>
        </div>
    </div>
EOF
    ;
}

#将记录写入文件
sub save_data_to_file(){
    my $ref_conf_data = shift;
    my @conf_data = @$ref_conf_data;
    my $filename= shift;
    
    open (FILE, ">$filename");
    foreach my $line (@conf_data) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
}

sub reload(){
    if ($reload) {
        system("touch $needreload");
    }
    if (-e $needreload) {
        applybox(_("规则已改变，需应用该规则以使改变生效"));
    }
    $reload = 0;
}

#判断启用杀毒
sub judge_havp(){
    system("$cmd");
    my %ret;
    %ret -> {'status'} = $?>>8;
    if($ret{'status'} == 0){
        $status_havp = "on";
    }else{
        $status_havp = "off";
    }
    my $result = $json->encode(\%ret);
    print $result;
}

&init_data();
&getcgihash(\%par);
&do_action();