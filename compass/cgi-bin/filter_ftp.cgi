#!/usr/bin/perl
#
#author:刘炬隆（Liu Julong）
#
#date:2015/04/20
#
#description:发送邮件过滤全局设置页面
require '/var/efw/header.pl';
my $custom_dir = 'frox';
my $conf_dir = '/var/efw/'.$custom_dir;
my $conf_file = $conf_dir.'/settings';
my $conf_file_white = $conf_dir.'/white_list';
my $conf_file_black = $conf_dir.'/black_list';
my $needreload = '/var/efw/'.$custom_dir.'/needreload';
my $restart = '/usr/local/bin/restartfrox';
my $reload = 0;
my %par;
my %settings;
my $extraheader;
my $errormessage = "";
my $notemessage ="";
my $status_havp = "off";
my $cmd = "sudo /usr/local/bin/judge_virus_enable.py -m clamav";
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
    my ($is_checked_frox,$is_checked_av,$is_checked_ftp) = ("","","");
    if($settings{'FROX_ENABLED'} eq 'on'){
        $is_checked_frox = "checked";
    }
    if($settings{'AV_ENABLED'} eq 'on' && $status_havp eq 'on'){
        $is_checked_av = "checked";
    }
    if($settings{'FTP_LIST'} eq 'on'){
        $is_checked_ftp = "checked";
    }
    
    my $val_white_list = `cat $conf_file_white`;
    my $val_black_list = `cat $conf_file_black`;
    
    chop($val_white_list);
    chop($val_black_list);
    
openbox('100%', 'left', _('FTP过滤'));
printf <<EOF
    <form name="FTP_FILTER_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="table-footer">
    <td colspan="2" style="text-align:left;">
      <input type="checkbox" name="FROX_ENABLED" $is_checked_frox value="on"/>
      <span>启用FTP过滤功能</span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type" style="width:250px">病毒过滤</td>
    <td><input type="checkbox" id="AV_ENABLED" name='AV_ENABLED' $is_checked_av value="on"/>
      <span>启用</span>
      <span id="label_tip" style="color:red;"></span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">黑白名单</td>
    <td><input type="checkbox" id="FTP_LIST" name='FTP_LIST' $is_checked_ftp value="on" onclick="change_show_ftp();"/><span>启用</span></td>
    </tr>
    <tr class="odd ctr_ftp">
    <td class="add-div-type"></td>
    <td>
      <div>
        <div style="float:left;width:50%;">
          <div>白名单</div>
          <div><textarea name="white_list" style="width:300px;height:100px;">$val_white_list</textarea></div>
        </div>
        <div>
          <div>黑名单</div>
          <div><textarea name="black_list" style="width:300px;height:100px;">$val_black_list</textarea></div>
        </div>
      </div>
      <div>例如:192.168.1.1，每行一个</div>
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
        &openpage(_('FTP过滤'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
    
    if($action eq 'save') {
        if( -f $conf_file ) {
            &readhash( $conf_file, \%settings );
        }
        $settings{'FROX_ENABLED'} = $par{'FROX_ENABLED'};
        my $av_enabled = "off";
        if($par{'AV_ENABLED'}){
            $av_enabled = $par{'AV_ENABLED'};
        }
        $settings{'AV_ENABLED'} = $av_enabled;
        #$settings{'AV_ENABLED'} = $status_havp;
        $settings{'FTP_LIST'} = $par{'FTP_LIST'};
        &writehash( $conf_file, \%settings );
        
        my $str_white_list = $par{'white_list'};
        my $str_black_list = $par{'black_list'};
        
        if($str_white_list){
            system("echo '$str_white_list' > $conf_file_white");
        }else{
            system("cat /dev/null >$conf_file_white");
        }
        if($str_black_list){
            system("echo '$str_black_list' > $conf_file_black");
        }else{
            system("cat /dev/null >$conf_file_black");
        }
        $reload = 1;
    }
    
    if ($action eq 'judge_havp') {
        #==判断启用杀毒==#
        &showhttpheaders();
        &judge_havp();
    }
    
    if($action ne 'apply' && $action ne 'judge_havp') {
        &showhttpheaders(); 
        &openpage(_('FTP过滤'),1,$extraheader); 
        &reload();
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}
#初始化数据
sub init_data(){
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/filter_ftp_controller.js"></script>
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
    
    if(! -e $conf_file_white){
        `touch $conf_file_white`;
    }
    
    if(! -e $conf_file_black){
        `touch $conf_file_black`;
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