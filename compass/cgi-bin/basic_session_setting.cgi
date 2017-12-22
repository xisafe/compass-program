#!/usr/bin/perl
#
#author:刘炬隆（Liu Julong）
#
#date:2014/09/15
#
#description:基本会话配置页面
require '/var/efw/header.pl';
my $custom_dir = 'sessionmanager';
my $conf_dir = '/var/efw/'.$custom_dir;
my $default_dir = '/var/efw/'.$custom_dir.'/default';
my $conf_file = $conf_dir.'/settings';
my $conf_default_file = $default_dir.'/settings';
my $needreload = '/var/efw/'.$custom_dir.'/needreload';
my $restart = 'sudo /usr/local/bin/session_set.py &>/dev/null';
my $reload = 0;
my %par;
my %settings;
my $extraheader;
my $errormessage = "";
my $notemessage ="";
my $CUR_PAGE = "基本会话配置";      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

sub display(){
    &create_mesg_boxs();
    &readhash( $conf_default_file, \%settings );
    if( -f $conf_file ) {
        &readhash( $conf_file, \%settings );
    }
openbox('100%', 'left', _('基本会话设置'));
printf <<EOF
    <form name="BASIC_SESSION_SETTING_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="table-footer">
    <td colspan="2" style="text-align:left;font-weight:bold">
      <span>TCP协议</span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type" style="width:250px">TCP连接的SYN_SENT状态老化时间</td>
    <td><input type="text" class="ctr_tcp" name='SYN_SENT' value="$settings{'SYN_SENT'}"/><span>（10-86400秒，默认值：60）</span></td>
    </tr>
    <tr class="odd">
    <td  class="add-div-type" style="text-align:left;font-weight:bold">TCP连接的SYN_RCV状态老化时间</td>
    <td><input type="text" class="ctr_tcp" name='SYN_RCV' value="$settings{'SYN_RCV'}"/><span>（10-86400秒，默认值：60）</span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">TCP连接的FIN_WAIT状态老化时间</td>
    <td><input type="text" class="ctr_tcp" name='FIN_WAIT' value="$settings{'FIN_WAIT'}"/><span>（10-86400秒，默认值：60）</span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">TCP连接的WAIT状态老化时间</td>
    <td><input type="text" class="ctr_tcp" name='TIME_WAIT' value="$settings{'TIME_WAIT'}"/><span>（10-86400秒，默认值：60）</span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">TCP连接的ESTABLISED状态老化时间</td>
    <td><input type="text" id="ESTABLISHED" name='ESTABLISHED' value="$settings{'ESTABLISHED'}"/><span>（10-86400秒，默认值：3600）</span></td>
    </tr>
    <tr class="table-footer">
    <td colspan="2" style="text-align:left;font-weight:bold">
      <span>UDP协议</span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">UDP连接OPEN状态老化时间</td>
    <td><input type="text" id="UDP_CONNECT" name='UDP_CONNECT' value="$settings{'UDP_CONNECT'}"/><span>（10-86400秒，默认值：180）</span></td>
    </tr>
    <tr class="odd">
    <td  class="add-div-type">UDP连接半闭状态老化时间</td>
    <td><input type="text" id="UDP_CLOSE" name='UDP_CLOSE' value="$settings{'UDP_CLOSE'}"/><span>（10-86400秒，默认值：30）</span></td>
    </tr>
    <tr class="table-footer">
    <td colspan="2" style="text-align:left;font-weight:bold">
      <span>ICMP协议</span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">ICMP连接CLOSE状态老化时间</td>
    <td><input type="text" id="ICMP_CLOSE" name='ICMP_CLOSE' value="$settings{'ICMP_CLOSE'}"/><span>（10-86400秒，默认值：30）</span></td>
    </tr>
    <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save"></input>
      <input type="submit" class="net_button" value="保存" align="middle"/>
      <input type="submit" class="net_button" value="恢复默认值" align="middle" onclick="recovery_data();"/>
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
        &openpage(_('会话基本配置'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
        $log_oper = "apply";
        &write_log($CUR_PAGE,$log_oper,0,$rule_or_config);
    }
    
    if($action eq 'save') {
        my @data_save;
        my @conf_template_fileds = ("SYN_SENT","SYN_RCV","FIN_WAIT","TIME_WAIT","ESTABLISHED","UDP_CONNECT","UDP_CLOSE","ICMP_CLOSE");
        my @conf_keys = ("SYN_SENT","SYN_RCV","FIN_WAIT","TIME_WAIT","ESTABLISHED","UDP_CONNECT","UDP_CLOSE","ICMP_CLOSE");
        my $length = @conf_keys;
        for(my $i=0;$i<$length;$i++){
            my $item = $conf_keys[$i].'='.$par{$conf_template_fileds[$i]};
            push (@data_save,$item)
        }
        if(! -e $conf_file){
        `touch $conf_file`;
        }
        
        &save_data_to_file(\@data_save,$conf_file);
        $reload = 1;
        $log_oper = "edit";
        &write_log($CUR_PAGE,$log_oper,0,$rule_or_config);
    }
    
    if($action ne 'apply') {
        &showhttpheaders(); 
        &openpage(_('会话基本配置'),1,$extraheader); 
        &reload();
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}
#初始化数据
sub init_data(){
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/idps_basic_session_controller.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />';
    &make_file();
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $default_dir){
        `mkdir -p $default_dir`;
    }
    
    
    if(! -e $conf_default_file){
        `touch $conf_default_file`;
        system("echo SYN_SENT=60 >> $conf_default_file");
        system("echo SYN_RCV=60 >> $conf_default_file");
        system("echo FIN_WAIT=60 >> $conf_default_file");
        system("echo TIME_WAIT=60 >> $conf_default_file");
        system("echo ESTABLISHED=3600 >> $conf_default_file");
        system("echo UDP_CONNECT=180 >> $conf_default_file");
        system("echo UDP_CLOSE=30 >> $conf_default_file");
        system("echo ICMP_CLOSE=30 >> $conf_default_file");
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