#!/usr/bin/perl
#
#author:刘炬隆（Liu Julong）
#
#date:2015/04/22
#
#description:发送邮件垃圾邮件过滤页面
require '/var/efw/header.pl';
my $custom_dir = 'smtpscan';
my $conf_dir = '/var/efw/'.$custom_dir;
my $conf_file = $conf_dir.'/basic_settings';
my $conf_file_spam_whitelist = $conf_dir.'/spam_whitelist';
my $conf_file_spam_blacklist = $conf_dir.'/spam_blacklist';
my $needreload = '/var/efw/'.$custom_dir.'/needreload';
my $restart = '/usr/local/bin/restartsmtpscan';
my $reload = 0;
my %par;
my %settings;
my $extraheader;
my $errormessage = "";
my $notemessage ="";

sub display(){
    &create_mesg_boxs();
    if( -f $conf_file ) {
        &readhash( $conf_file, \%settings );
    }
    my $is_checked_rbl = "";
    my $selected_discard = "";
    my $selected_pass = "";
    if($settings{'RBL'} eq 'on'){
        $is_checked_rbl = "checked";
    }

    if($settings{'FINAL_SPAM_DESTINY'} eq 'D_PASS'){
        $selected_pass = "selected";
    }else{
        # 默认选中“丢弃”
        $selected_discard = "selected";
    }
    
    my $val_spam_whitelist = `cat $conf_file_spam_whitelist`;
    my $val_spam_blacklist = `cat $conf_file_spam_blacklist`;
    
    chop($val_spam_whitelist);
    chop($val_spam_blacklist);
openbox('100%', 'left', _('垃圾邮件过滤'));
printf <<EOF
    <form name="JUNK_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="odd">
      <td>
        <div style=";margin-left:50px;">
          <span>处理垃圾邮件方法</span>
          <select name="FINAL_SPAM_DESTINY">
            <option value="D_DISCARD" $selected_discard>丢弃</option>
            <option value="D_PASS" $selected_pass>增加垃圾标签继续发送</option>
          </select>
        </div>
      </td>
    </tr>
    <tr class="odd">
      <td>
        <div style=";margin-left:50px;">
          <span>实时黑名单（RBL）</span>
          <input type="checkbox" name="RBL" value="on" $is_checked_rbl/>
          <span>启用</span>
        </div>
      </td>
    </tr>
    <tr class="odd">
      <td>
        <div style="float:left;width:50%;margin-left:50px;">
          <div>发件人邮箱黑名单：</div>
          <div><textarea name="spam_blacklist" style="width:300px;height:100px;">$val_spam_blacklist</textarea></div>
        </div>
        <div>
          <div>发件人邮箱白名单：</div>
          <div><textarea name="spam_whitelist" style="width:300px;height:100px;">$val_spam_whitelist</textarea></div>
        </div>
        <div style="margin-left:50px;">例如：capsheaf.com或support@capsheaf.com.cn,每行一个</div>
      </td>
    </tr>
    <tr class="table-footer">
    <td>
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
        &openpage(_('垃圾邮件过滤'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
    
    if($action eq 'save') {
        my $str_spam_whitelist = $par{'spam_whitelist'};
        my $str_spam_blacklist = $par{'spam_blacklist'};
        &readhash( $conf_file, \%settings );
        
        $settings{'RBL'} = $par{'RBL'};
        $settings{'FINAL_SPAM_DESTINY'} = $par{'FINAL_SPAM_DESTINY'};
        &writehash( $conf_file, \%settings );
        
        system("echo '$str_spam_whitelist' > $conf_file_spam_whitelist");
        system("echo '$str_spam_blacklist' > $conf_file_spam_blacklist");
        $reload = 1;
    }
    
    if($action ne 'apply') {
        &showhttpheaders(); 
        &openpage(_('垃圾邮件过滤'),1,$extraheader); 
        &reload();
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}
#初始化数据
sub init_data(){
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/sender_filter_junk_controller.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />';
    &make_file();
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $conf_file_spam_blacklist){
        `touch $conf_file_spam_blacklist`;
    }
    
    if(! -e $conf_file_spam_whitelist){
        `touch $conf_file_spam_whitelist`;
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

&init_data();
&getcgihash(\%par);
&do_action();
