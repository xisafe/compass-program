#!/usr/bin/perl
#
#author:刘炬隆（Liu Julong）
#
#date:2015/04/22
#
#description:发送邮件邮件黑白名单页面
require '/var/efw/header.pl';
my $custom_dir = 'smtpscan';
my $conf_dir = '/var/efw/'.$custom_dir;
my $conf_file_sender_whitelist = $conf_dir.'/sender_whitelist';
my $conf_file_sender_blacklist = $conf_dir.'/sender_blacklist';
my $conf_file_recipient_whitelist = $conf_dir.'/recipient_whitelist';
my $conf_file_recipient_blacklist = $conf_dir.'/recipient_blacklist';
my $conf_file_client_whitelist = $conf_dir.'/client_whitelist';
my $conf_file_client_blacklist = $conf_dir.'/client_blacklist';
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
    my $val_sender_whitelist = `cat $conf_file_sender_whitelist`;
    my $val_sender_blacklist = `cat $conf_file_sender_blacklist`;
    my $val_recipient_whitelist = `cat $conf_file_recipient_whitelist`;
    my $val_recipient_blacklist = `cat $conf_file_recipient_blacklist`;
    my $val_client_whitelist = `cat $conf_file_client_whitelist`;
    my $val_client_blacklist = `cat $conf_file_client_blacklist`;
    
    chop($val_sender_whitelist);
    chop($val_sender_blacklist);
    chop($val_recipient_whitelist);
    chop($val_recipient_blacklist);
    chop($val_client_whitelist);
    chop($val_client_blacklist);
openbox('100%', 'left', _('全局配置'));
printf <<EOF
    <form name="BWLIST_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="table-footer">
    <td style="text-align:left;">
      <span>发件人邮箱地址:</span>
    </td>
    </tr>
    <tr class="odd">
      <td>
        <div style="float:left;width:50%;margin-left:50px;">
          <div>白名单：</div>
          <div><textarea id="sender_whitelist" name="sender_whitelist" style="width:300px;height:100px;">$val_sender_whitelist</textarea></div>
        </div>
        <div>
          <div>黑名单：</div>
          <div><textarea id="sender_blacklist" name="sender_blacklist" style="width:300px;height:100px;">$val_sender_blacklist</textarea></div>
        </div>
        <div style="margin-left:50px;">例如：capsheaf.com或support@capsheaf.com.cn,每行一个</div>
      </td>
    </tr>
    <tr class="table-footer">
    <td style="text-align:left;">
      <span>收件人邮箱地址:</span>
    </td>
    </tr>
    <tr class="odd">
      <td>
        <div style="float:left;width:50%;margin-left:50px;">
          <div>白名单：</div>
          <div><textarea id="recipient_whitelist" name="recipient_whitelist" style="width:300px;height:100px;">$val_recipient_whitelist</textarea></div>
        </div>
        <div>
          <div>黑名单：</div>
          <div><textarea id="recipient_blacklist" name="recipient_blacklist" style="width:300px;height:100px;">$val_recipient_blacklist</textarea></div>
        </div>
        <div style="margin-left:50px;">例如：capsheaf.com或support@capsheaf.com.cn,每行一个</div>
      </td>
    </tr>
    <tr class="table-footer">
    <td style="text-align:left;">
      <span>发件人IP地址:</span>
    </td>
    </tr>
    <tr class="odd">
      <td>
        <div style="float:left;width:50%;margin-left:50px;">
          <div>白名单：</div>
          <div><textarea id="client_whitelist" name="client_whitelist" style="width:300px;height:100px;">$val_client_whitelist</textarea></div>
        </div>
        <div>
          <div>黑名单：</div>
          <div><textarea id="client_blacklist" name="client_blacklist" style="width:300px;height:100px;">$val_client_blacklist</textarea></div>
        </div>
        <div style="margin-left:50px;">例如：192.168.1.1,每行一个</div>
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
        &openpage(_('邮件黑白名单'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
    
    if($action eq 'save') {
        my $str_sender_whitelist = $par{'sender_whitelist'};
        my $str_sender_blacklist = $par{'sender_blacklist'};
        my $str_recipient_whitelist = $par{'recipient_whitelist'};
        my $str_recipient_blacklist = $par{'recipient_blacklist'};
        my $str_client_whitelist = $par{'client_whitelist'};
        my $str_client_blacklist = $par{'client_blacklist'};
        
        system("echo '$str_sender_whitelist' > $conf_file_sender_whitelist");
        system("echo '$str_sender_blacklist' > $conf_file_sender_blacklist");
        system("echo '$str_recipient_blacklist' > $conf_file_recipient_blacklist");
        system("echo '$str_recipient_whitelist' > $conf_file_recipient_whitelist");
        system("echo '$str_client_blacklist' > $conf_file_client_blacklist");
        system("echo '$str_client_whitelist' > $conf_file_client_whitelist");
        $reload = 1;
    }
    
    if($action ne 'apply') {
        &showhttpheaders(); 
        &openpage(_('邮件黑白名单'),1,$extraheader); 
        &reload();
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}
#初始化数据
sub init_data(){
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/sender_black_white_list_controller.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />';
    &make_file();
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $conf_file_client_blacklist){
        `touch $conf_file_client_blacklist`;
    }
    
    if(! -e $conf_file_client_whitelist){
        `touch $conf_file_client_whitelist`;
    }
    
    if(! -e $conf_file_sender_blacklist){
        `touch $conf_file_sender_blacklist`;
    }
    
    if(! -e $conf_file_sender_whitelist){
        `touch $conf_file_sender_whitelist`;
    }
    
    if(! -e $conf_file_recipient_blacklist){
        `touch $conf_file_recipient_blacklist`;
    }
    
    if(! -e $conf_file_recipient_whitelist){
        `touch $conf_file_recipient_whitelist`;
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