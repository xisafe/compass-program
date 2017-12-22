#!/usr/bin/perl
#
#author:刘炬隆（Liu Julong）
#
#date:2014/12/09
#
#description:基本会话配置页面
require '/var/efw/header.pl';
my $custom_dir    = 'AAA';
my $conf_dir      = '/var/efw/'.$custom_dir;
my $default_dir   = '/var/efw/'.$custom_dir.'/default';
my $conf_file     = $conf_dir.'/config';
my $conf_file_old = $conf_dir.'/config.old';
my $conf_default_file = $default_dir.'/config';
my $needreload = '/var/efw/'.$custom_dir.'/needreload';
my $restart = '/usr/local/bin/rstAAA';
my $cmd_test = '/usr/local/bin/aaaTestConn';
my $reload = 0;
my %par;
my %settings;
my $extraheader;
my $errormessage = "";
my $notemessage ="";
my %hash_showtime = (
    "0" => "今天（默认）",
    "1" => "最近一天",
    "2" => "最近两天",
    "3" => "最近三天"
);

my $CUR_PAGE = "认证配置" ;      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

sub display(){
    &create_mesg_boxs();
    &readhash( $conf_default_file, \%settings );
    if( -f $conf_file ) {
        &readhash( $conf_file, \%settings );
    }
    my $is_checked_yes;
    my $is_checked_no;
    if($settings{'enable'} eq '0'){
        $is_checked_yes = 'checked';
        $is_checked_no = '';
    }else{
        $is_checked_yes = '';
        $is_checked_no = 'checked';
    }
    
    my $is_checked_http;
    my $is_checked_https;
    if($settings{'http'} eq 'http'){
        $is_checked_http = 'checked';
        $is_checked_https = '';
    }else{
        $is_checked_https = 'checked';
        $is_checked_http = '';
    }
    my $is_checked_local;
    my $is_checked_radius;
    my $is_checked_ldap;
    if($settings{'method'} eq 'LOCAL'){
        $is_checked_local = 'checked';
        $is_checked_radius = '';
        $is_checked_ldap = '';
    }elsif($settings{'method'} eq 'RADIUS'){
        $is_checked_local = '';
        $is_checked_radius = 'checked';
        $is_checked_ldap = '';
    }elsif($settings{'method'} eq 'LDAP'){
        $is_checked_local = '';
        $is_checked_radius = '';
        $is_checked_ldap = 'checked';
    }
    my @options_ip = split("\&",$settings{'IP_SELECTED'});
    my $val_ips = join("\r\n",@options_ip);
    my @options_ip_source = split("\&",$settings{'IP_SOURCE'});
    my $val_ips_source = join("\r\n",@options_ip_source);
    # my $html_options;
    # foreach(@options_ip){
        # my $one_option = '<option value="'.$_.'" selected>'.$_.'</option>';
        # $html_options .= $one_option;
    # }
    my $options_showtime = "";
    for(my $i=0;$i<4;$i++){
        if($i ==  $settings{'Notice'}){
            $options_showtime .= '<option value="'.$i.'" selected>'.$hash_showtime{$i}.'</option>';
        }else{
            $options_showtime .= '<option value="'.$i.'">'.$hash_showtime{$i}.'</option>';
        }
    }
    #LDAP服务器版本展示
    my $options_LDAP_server_version = "";
    for(my $i=2;$i<4;$i++){
        if($i ==  $settings{'LDAP_server_version'}){
            $options_LDAP_server_version .= '<option value="'.$i.'" selected>'.$i.'</option>';
        }else{
            $options_LDAP_server_version .= '<option value="'.$i.'">'.$i.'</option>';
        }
    }
&openmybox('100%', 'left', _('认证配置'));
printf <<EOF
    <form name="AUTH_SETTING_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="odd">
    <td class="add-div-type" style="width:250px">是否启用</td>
    <td>
        <span><input type="radio" name="enable" value="0" $is_checked_yes/>是</span>
        <span style="margin-left:50px"><input type="radio" name="enable" value="1" $is_checked_no/>否</span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type" style="width:250px">免认证目的IP</td>
    <td>
        <textarea class="input-textarea" id="IP_SELECTED" name='IP_SELECTED'>$val_ips</textarea>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type" style="width:250px">免认证源IP</td>
    <td>
        <textarea class="input-textarea" id="IP_SOURCE" name='IP_SOURCE'>$val_ips_source</textarea>
    </td>
    </tr>
    <!--<tr class="odd">
    <td  class="add-div-type">http/https</td>
    <td><input type="radio" name='http' value="http" $is_checked_http /><span>http</span>
    <input type="radio" style="margin-left:50px;" name='http' value="https" $is_checked_https /><span>https</span></td>
    </tr>-->
    <tr class="odd">
    <td class="add-div-type">认证方法</td>
    <td><div><input type="radio" name='method' value="LOCAL" onclick="show_detail_method();" $is_checked_local/><span>本地认证</span></div>
        <div><input type="radio" name='method' value="RADIUS" onclick="show_detail_method();" $is_checked_radius/><span>RADIUS认证</span></div>
        <div id="detail_radius" style="margin-left:12px;">
            <div>服务器地址：<input type="text" style="margin-left:32px;" class="input-text" id="RADIUS_server_ip" name="RADIUS_server_ip" value="$settings{'RADIUS_server_ip'}"/>（IP地址）</div>
            <div>共享密钥：<input type="password" style="margin-left:43px;" class="input-text" id="RADIUS_SKEY" name="RADIUS_SKEY" value="$settings{'RADIUS_SKEY'}"/></div>
            <div>认证端口号：<input type="text" style="margin-left:32px;" class="input-text" id="RADIUS_port_auth" name="RADIUS_port_auth" value="$settings{'RADIUS_port_auth'}"/></div>
            <div>计费端口号：<input type="text" style="margin-left:32px;" class="input-text" id="RADIUS_PPORT" name="RADIUS_PPORT" value="$settings{'RADIUS_PPORT'}"/></div>
            <div>认证报文超时时间：<input type="text" class="input-text" id="RADIUS_timeout" name="RADIUS_timeout" value="$settings{'RADIUS_timeout'}"/>秒（5-20的整数）</div>
            <div>认证报文重传次数：<input type="text" class="input-text" id="RADIUS_time_resend" name="RADIUS_time_resend" value="$settings{'RADIUS_time_resend'}"/>次（3-5的整数）</div>
            <div><input type="button" style="margin-left:150px;" class="net_button" value="测试连接" onclick="testConn();"/></div>
        </div>
        <div><input type="radio" name='method' value="LDAP" onclick="show_detail_method();" $is_checked_ldap/><span>LDAP认证</span></div>
        <div id="detail_ldap" style="margin-left:12px;">
            <div>服务器版本：<select style="margin-left:32px;" id="LDAP_server_version" name="LDAP_server_version" value="">$options_LDAP_server_version</select></div>
            <div>服务器地址：<input type="text" style="margin-left:32px;" class="input-text" id="LDAP_server_ip" name="LDAP_server_ip" value="$settings{'LDAP_server_ip'}"/></div>
            <div>服务器端口：<input type="text" style="margin-left:32px;" class="input-text" id="LDAP_port" name="LDAP_port" value="$settings{'LDAP_port'}"/></div>
            <div>Base DN：<input type="text" style="margin-left:42px;" class="input-text" id="LDAP_BaseDN" name="LDAP_BaseDN" value="$settings{'LDAP_BaseDN'}"/></div>
            <div>管理员DN：<input type="text" style="margin-left:36px;" class="input-text" id="LDAP_managerDN" name="LDAP_managerDN" value="$settings{'LDAP_managerDN'}"/></div>
            <div>管理员密码：<input type="password" style="margin-left:32px;" class="input-text" id="LDAP_password_manager" name="LDAP_password_manager" value="$settings{'LDAP_password_manager'}"/></div>
            <div><input type="button" style="margin-left:150px;" class="net_button" value="测试连接" onclick="testConn();"/></div>
        </div>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">用户老化时间：</td>
    <td><input type="text" class="input-text" name='Timeout' value="$settings{'Timeout'}"/><span>分钟【默认值：30，填写范围30-60】</span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">公告展示：</td>
    <td><select id="Notice" name="Notice" style="width:204px">$options_showtime</select>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">禁止上线时间：</td>
    <td><input type="text" class="input-text" name='Forbid' value="$settings{'Forbid'}"/><span>分钟【默认值：10，填写范围10-60】</span></td>
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
        #my $result = $?;
        #chomp($result);
        `rm $needreload`;
        $notemessage = "规则应用成功";
        # if($result == 0){
            # $notemessage = "规则应用成功";#此行消息可以自定义
        # }else{
            # $notemessage = "规则应用失败"; #此行消息可以自定义
        # }
        &openpage(_('认证配置'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
    
    if($action eq 'save') {
        &save_data();
    }
    
    if($action eq 'testconn') {
        &showhttpheaders();
        &readhash( $conf_default_file, \%settings );
        if( -f $conf_file ) {
            &readhash( $conf_file, \%settings );
        }
        $method = $par{'method'};
        $settings{'method'} = $method;
        if($method eq 'RADIUS'){
            $settings{'method'} = 'RADIUS';
            $settings{'RADIUS_SKEY'} = $par{'RADIUS_SKEY'};
            $settings{'RADIUS_server_ip'} = $par{'RADIUS_server_ip'};
            $settings{'RADIUS_port_auth'} = $par{'RADIUS_port_auth'};
            $settings{'RADIUS_timeout'} = $par{'RADIUS_timeout'};
            $settings{'RADIUS_PPORT'} = $par{'RADIUS_PPORT'};
            $settings{'RADIUS_time_resend'} = $par{'RADIUS_time_resend'};
        }else{
            $settings{'method'} = 'LDAP';
            $settings{'LDAP_server_version'} = $par{'LDAP_server_version'};
            $settings{'LDAP_server_ip'} = $par{'LDAP_server_ip'};
            $settings{'LDAP_port'} = $par{'LDAP_port'};
            $settings{'LDAP_BaseDN'} = $par{'LDAP_BaseDN'};
            $settings{'LDAP_managerDN'} = $par{'LDAP_managerDN'};
            $settings{'LDAP_password_manager'} = $par{'LDAP_password_manager'};
        }
        
        &writehash($conf_file, \%settings);
        
        system($cmd_test);
        
        #print "test";
    }
    
    if($action ne 'apply' && $action ne 'testconn') {
        &showhttpheaders(); 
        &openpage(_('认证配置'),1,$extraheader); 
        &reload();
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
    if ($action eq 'apply' || $action eq 'save') {
        if ($action eq 'apply') {
            $log_oper = 'apply';
        }else{
            $log_oper = 'edit';
        }
        &write_log($CUR_PAGE,$log_oper,0,$rule_or_congfig);
    }
}
#初始化数据
sub init_data(){
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/auth_setting_controller.js"></script>
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
        system("echo enable=0 >> $conf_default_file");
        system("echo IP_SELECTED=1.1.1.1 >> $conf_default_file");
        system("echo method=LOCAL >> $conf_default_file");
        system("echo Timeout=30 >> $conf_default_file");
        system("echo Notice=0 >> $conf_default_file");
        system("echo Forbid=10 >> $conf_default_file");
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

sub save_data(){
    my @data_save;
    my @conf_keys = ("enable","IP_SELECTED","IP_SOURCE","method","Timeout","Notice","Forbid");
    if($par{'method'} eq 'RADIUS'){
        my @keys_radius = ("RADIUS_server_ip","RADIUS_SKEY","RADIUS_port_auth","RADIUS_PPORT","RADIUS_timeout","RADIUS_time_resend");
        push(@conf_keys,@keys_radius);
    }elsif($par{'method'} eq 'LDAP'){
        my @keys_ldap = ("LDAP_server_version","LDAP_server_ip","LDAP_port","LDAP_BaseDN","LDAP_managerDN","LDAP_password_manager");
        push(@conf_keys,@keys_ldap);
    }
    my $length = @conf_keys;
    for(my $i=0;$i<$length;$i++){
        my $item;
        if($conf_keys[$i] eq "IP_SELECTED" || $conf_keys[$i] eq "IP_SOURCE"){
            $item = $conf_keys[$i].'='.join("\&",split(/\r\n/,$par{$conf_keys[$i]}));
        }else{
            $item = $conf_keys[$i].'='.$par{$conf_keys[$i]};
        }
        push (@data_save,$item)
    }
    
    if(! -e $conf_file){
    `touch $conf_file`;
    }
    `cp $conf_file $conf_file_old`;
    &save_data_to_file(\@data_save,$conf_file);
    $reload = 1;
}

#自定义显示框
sub openmybox
{
    $width = $_[0];
    $align = $_[1];
    $caption = $_[2];
    $id = $_[3];
    
    if($id ne '') {
        $id = "id=\"$id\"";
    }
    else {
        $id="";
    }
    
    
    printf <<EOF
<div class="containter-div">
EOF
    ;
    if ($caption) {
        printf <<EOF
     <span class="containter-div-header"><span style="display:block;float:left;margin-top:3px;"><img src='/images/applications-blue.png' />$caption</span><span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;"></span></span>
EOF
;
    }
    else {
             printf <<EOF
        <span class="containter-div-header"><img src='/images/applications-blue.png' />&nbsp;</span>
EOF
;
    }
    
    printf <<EOF
    <div class="containter-div-content">
EOF
    ;
}

&init_data();
&getcgihash(\%par);
&do_action();