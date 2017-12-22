#!/usr/bin/perl
#
#author:刘炬隆（Liu Julong）
#
#date:2015/04/22
#
#description:发送邮件邮件关键字页面
require '/var/efw/header.pl';
my $custom_dir = 'smtpscan/phraselists';
my $conf_dir = '/var/efw/'.$custom_dir;
my $conf_file_sublist = $conf_dir.'/user_phraselist_subject';
my $conf_file_body = $conf_dir.'/user_phraselist_body';
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
    my $val_sub = `cat $conf_file_sublist`;
    my $val_body = `cat $conf_file_body`;
    chop($val_sub);
    chop($val_body);
openbox('100%', 'left', _('邮件关键字过滤'));
printf <<EOF
    <form name="KEYWORDS_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="odd">
      <td>
        <div style="float:left;width:50%;margin-left:50px;">
          <div>邮件主题关键字(每行一个)：</div>
          <div><textarea name="user_phraselist_sublist" style="width:300px;height:100px;">$val_sub</textarea></div>
        </div>
        <div>
          <div>邮件正文关键字(每行一个)：</div>
          <div><textarea name="user_phraselist_body" style="width:300px;height:100px;">$val_body</textarea></div>
        </div>
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
        &openpage(_('邮件关键字过滤'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
    
    if($action eq 'save') {
        my $str_user_phraselist_sublist = $par{'user_phraselist_sublist'};
        my $str_user_phraselist_body = $par{'user_phraselist_body'};
        
        system("echo '$str_user_phraselist_sublist' > $conf_file_sublist");
        system("echo '$str_user_phraselist_body' > $conf_file_body");
        $reload = 1;
    }
    
    if($action ne 'apply') {
        &showhttpheaders(); 
        &openpage(_('邮件关键字过滤'),1,$extraheader); 
        &reload();
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}
#初始化数据
sub init_data(){
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/sender_keywords_controller.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />';
    &make_file();
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $conf_file_sublist){
        `touch $conf_file_sublist`;
    }
    
    if(! -e $conf_file_body){
        `touch $conf_file_body`;
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