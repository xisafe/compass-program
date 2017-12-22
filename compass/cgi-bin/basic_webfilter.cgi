#!/usr/bin/perl
#
#author:刘炬隆（Liu Julong）
#
#date:2015/04/07
#
#description:WEB内容过滤基本设置页面
require '/var/efw/header.pl';
my $custom_dir = 'proxy';
my $conf_dir = '/var/efw/'.$custom_dir;
my $default_dir = '/var/efw/'.$custom_dir.'/default';
my $conf_file = $conf_dir.'/settings';
my $conf_default_file = $default_dir.'/settings';
my $needreload = '/var/efw/'.$custom_dir.'/needreload';
my $flag_run = $conf_dir.'/runningtag';
my $restart = '/usr/local/bin/restartsquid';
my $reload = 0;
my %par;
my %settings;
my $extraheader;
my $errormessage = "";
my $notemessage ="";
my $json = new JSON::XS;#处理json数据的变量，一般不变

sub display(){
    &create_mesg_boxs();
    &readhash( $conf_default_file, \%settings );
    if( -f $conf_file ) {
        &readhash( $conf_file, \%settings );
    }
    #装配数据
    my $is_checked_proxy = "";
    my $is_checked_log = "";
    my $is_checked_dans = "";
    my $is_checked_white = "";
    if($settings{'PROXY_ENABLED'} eq 'on'){
        $is_checked_proxy = "checked";
    }
    if($settings{'LOGGING'} eq 'on'){
        $is_checked_log = "checked";
    }
    if($settings{'DANSGUARDIAN_LOGGING'} eq 'on'){
        $is_checked_dans = "checked";
    }
    if($settings{'WHITELIST'} eq 'on'){
        $is_checked_white = "checked";
    }
    $settings{'BYPASS_SOURCE'} =~ s/,/\n/g;
    $settings{'BYPASS_DESTINATION'} =~ s/,/\n/g;
openbox('100%', 'left', _('基本设置'));
printf <<EOF
    <form name="BASIC_WEBFILTER_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="table-footer">
    <td colspan="2" style="text-align:left;">
      <input type="checkbox" name="PROXY_ENABLED" $is_checked_proxy value="on"/>
      <span>启用WEB内容过滤功能</span>
    </td>
    </tr>
    <!--<tr class="odd">
    <td class="add-div-type" style="width:150px">记录所有访问页面</td>
    <td><input type="checkbox" name='LOGGING' $is_checked_log value="on"/><span>启用</span></td>
    </tr>-->
    <tr class="odd">
    <td class="add-div-type">记录过滤的WEB页面</td>
    <td><input type="checkbox" name='DANSGUARDIAN_LOGGING' $is_checked_dans value="on"/><span>启用</span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">WEB白名单</td>
    <td><input type="checkbox" id="WHITELIST" name='WHITELIST' $is_checked_white value="on"/ onclick="change_show_lasttr();"><span>启用</span></td>
    </tr>
    <tr class="odd ctr_last">
    <td class="add-div-type"></td>
    <td><div style="width:50%;float:left;"><span>设置绕过过滤功能的客户端IP/网段/MAC地址(每行一个)</span>
        <textarea style="width:250px;height:100px;" name="BYPASS_SOURCE">$settings{'BYPASS_SOURCE'}</textarea>
      </div>
      <div><span>设置绕过过滤功能的服务器IP/网段/MAC地址(每行一个)</span>
        <textarea style="width:250px;height:100px;" name="BYPASS_DESTINATION">$settings{'BYPASS_DESTINATION'}</textarea>
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
        &begin();
        system($restart);
        &ends();
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
    }
    
    #检测后台是否在运行
    if ( $action eq 'check_running' ) {
        &showhttpheaders();
        &check_running();
    }
    
    if($action eq 'save') {
        my @data_save;
        my @conf_template_fileds = ("PROXY_ENABLED","DANSGUARDIAN_LOGGING","WHITELIST","BYPASS_SOURCE","BYPASS_DESTINATION");
        my @conf_keys = ("PROXY_ENABLED","DANSGUARDIAN_LOGGING","WHITELIST","BYPASS_SOURCE","BYPASS_DESTINATION");
        my $length = @conf_keys;
        for(my $i=0;$i<$length;$i++){
            my $value_form = $par{$conf_template_fileds[$i]};
            if($conf_keys[$i] eq 'BYPASS_SOURCE' || $conf_keys[$i] eq 'BYPASS_DESTINATION'){
                $value_form =~ s/\r//g;
                $value_form = join(",",split(/\n/,$value_form));
            }
            my $item = $conf_keys[$i].'='.$value_form;
            push (@data_save,$item)
        }
        push(@data_save,'SSLPORS=443,563,3001');
        push(@data_save,'PORTS=80,21,70,210,1025-65535,280,488,591,77,800');
        push(@data_save,'LOGGING=on');
        push(@data_save,'HAVP_ENABLED=on');
        push(@data_save,'OFFLINE_MODE=off');
        push(@data_save,'GREEN_ENABLED=transparent');
        push(@data_save,'ORANGE_ENABLED=transparent');
        if(! -e $conf_file){
        `touch $conf_file`;
        }
        
        &save_data_to_file(\@data_save,$conf_file);
        $reload = 1;
    }
    
    if($action ne 'apply' && $action ne 'check_running') {
        &showhttpheaders(); 
        &openpage(_('基本配置'),1,$extraheader); 
        &reload();
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}
#初始化数据
sub init_data(){
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/basic_webfilter_controller.js"></script>
                    <script type="text/javascript" src="/include/waiting.js"></script>
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
        system("echo PROXY_ENABLED=on >> $conf_default_file");
        system("echo LOGGING=on >> $conf_default_file");
        system("echo DANSGUARDIAN_LOGGING=on >> $conf_default_file");
        system("echo WHITELIST=on >> $conf_default_file");
        system("echo BYPASS_SOURCE=1.1.1.1,2.2.2.0/24 >> $conf_default_file");
        system("echo BYPASS_DESTINATION=3.3.3.3,4.4.4.0/24 >> $conf_default_file");
        system("echo SSLPORS=443,563,3001 >> $conf_default_file");
        system("echo PORTS=80,21,70,210,1025-65535,280,488,591,77,800 >> $conf_default_file");
        system("echo HAVP_ENABLED=on >> $conf_default_file");
        system("echo OFFLINE_MODE=off >> $conf_default_file");
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

sub begin(){
    printf <<EOF
    <script>
      RestartService("正在应用基本配置，请耐心等待.....");
    </script>
EOF
;
}
sub ends(){
    printf <<EOF
    <script>
      endmsg("");
    </script>
EOF
;
}
#检查后台是否在运行
sub check_running(){
    my %ret_data;
    if ( -e $flag_run ) {
        %ret_data->{'running'} = 1;
    }else {
        %ret_data->{'running'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret;
    exit;
}

&init_data();
&getcgihash(\%par);
&do_action();