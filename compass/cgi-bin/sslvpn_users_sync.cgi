#!/usr/bin/perl
use POSIX qw(strftime);
require '/var/efw/header.pl';

my $errormessage,$warnmessage,$notemessage;
my $conffile_dir = "/var/efw/openvpn/sync";
my $conffile = "/var/efw/openvpn/sync/settings";
my $sync_policy = "/var/efw/openvpn/sync/policy";
my $sync_whitelist = "/var/efw/openvpn/syn_whitelist";
my $sync_passwd = "/var/efw/openvpn/syn_passwd";
my $passwd = "/var/efw/openvpn/passwd";
my $restart = "/usr/local/bin/restartsslvpnusersyn";
my $syn_operation = "sudo /usr/local/bin/syntoremote.sh";
my $needreload = "/var/efw/openvpn/sync/needreload";

my $name        = "用户同步";
my $extraheader     = "<link rel='stylesheet' type='text/css' href='/extjs/resources/css/ext-all.css'>
                    <link rel='stylesheet' type='text/css' href='/include/sslvpn_users.css'>
                    <script type='text/javascript' src='/extjs/ext-debug.js'></script>
                    <script language='javascript' type='text/javascript' src='/include/sslvpn_users_opfunc.js'></script>
                    <script language='javascript' type='text/javascript' src='/include/sslvpn_users_sync.js'></script>";

my @errormessages;
my $action;
my %par;
&validateUser();
&make_file();
getcgihash(\%par);
&doaction();
showhttpheaders();
openpage($name, 1, $extraheader);
openbigbox($errormessage,$warnmessage,$notemessage);
&apply();
&display_policy_save();
&check_form();
closebigbox();
closepage();

sub apply(){
    if(-e $needreload){
        applybox("同步配置以改变，需要应用以使配置生效。");
    }
}

sub make_file(){
    if(!-e $conffile_dir){
        `mkdir $conffile_dir`;
    }
    
    if(!-e $conffile){
        `touch $conffile`;
    }
    
    if(!-e $sync_policy){
        `touch $sync_policy`;
    }
}

sub display_policy_save(){
    &openbox('100%', 'left', _('设置'));
    my %policy;
    &readhash($sync_policy, \%policy);
    
    my $sync_checked = 'checked';
    my $service_selected = 'selected';
    my $client_selected = '';
    my $model = 'none';
    my $service_ip = $policy{'SERVICE_IP'};
    if($policy{'ENABLE'} ne 'on'){
        $sync_checked = '';
    }
    if($policy{'MODEL'} ne 'service'){
        $service_selected = '';
        $client_selected = 'selected';
        $model = 'table-row';
    }
    
    ##要设置的内容
    printf <<EOF
    <form name="SYNC_POLICY_FORM"  method="post" action="$ENV{'SCRIPT_NAME'}" >
        <table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
            <tbody>
                <tr  class="odd">
                    <td class="add-div-type" style="width:18%;">启用用户同步</td>
                    <td>
                        <input type='checkbox' name='ENABLED' $sync_checked />
                    </td>
                </tr>
                <tr class="env">
                    <td class="add-div-type" >模式选择<font color="red"><b>*</b></font></td>
                    <td>
                        <select id="sync_policy" name="sync_policy" style="width:136px" onchange="toggleModel('sync_policy');" onkeyup="toggleModel('sync_policy');">
                            <option  value="service" $service_selected>服务器</option>
                            <option  value="client" $client_selected>客户端</option>
                        </select>
                    </td>
                </tr>
                <tr class="odd" id="server_ip_tr" style="display:$model;">
                    <td class="add-div-type">服务器端IP地址<font color="red"><b>*</b></font></td>
                    <td>
                        <input type='text' name='server_ip' value="$service_ip"/>(<font color="red"><b>*</b></font>填写IP地址)
                    </td>
                </tr>
            </tbody>
            <tr  class="table-footer">
                <td colspan="2">
                  <input class='submitbutton net_button' type='submit' name='submit' value='保存'/>
                  <input type="hidden" name="ACTION" value="save" />
                </td>
            </tr>
    </table>
    </form>
EOF
;
    &closebox();
    
    my $model_display = 'block';
    if($policy{'MODEL'} ne 'service'){
        $model_display = 'none';
    }
    
    print "<div id='service_div' style='display:$model_display'>";
    &display_sync_policy_add();
    &display_rules();
    print "</div>";
}

sub display_sync_policy_add(){
    my $buttontext = "";
    $action = $par{'ACTION'};
    my $config_line;
    if($par{'ACTION'} eq ''){
        $action = 'add';
    }
    if ($action eq 'edit') {
          &openeditorbox("编辑同步策略", "","showeditor", "createrule", @errormessages);
        $buttontext = "编辑";
        $config_line = &read_conf_line($conffile,$par{'line'});
    }else{
        &openeditorbox("添加同步策略", "","", "createrule", @errormessages);
        $buttontext = "添加";
    }
    my @configs = split(/,/, $config_line);
    my $sync_name = $configs[0];
    my $description = $configs[1];
    my $client_addr = $configs[2];
    my $sync_orgs = $configs[3];
    my $last_time = $configs[4];
    my $sync_now_checked = "checked";
    
    ##要添加的内容
    printf <<EOF
    </form>
    <form enctype="multipart/form-data" name="USERS_SYNC_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}">
        <!--此table是为了消除Firefox中内容漂移问题-->
        <table></table>
        <table border='0' cellspacing="0" cellpadding="4">
            <tr  class="odd">
                <td class="add-div-type" style="width:18%;">名称<font color="red"><b>*</b></font></td>
                <td>
                    <input type='text' name='sync_name' value="$sync_name"/>(<font color="red"><b>*</b></font>1~20字符，可为中文字符)
                </td>
            </tr>
            <tr class="env">
                <td class="add-div-type" >描述</td>
                <td>
                    <input type='text' name='description' value="$description" size="20"/>(0~20个字符，可为中文)
                </td>
            </tr>
            <tr  class="odd">
                <td class="add-div-type" >同步客户端地址<font color="red"><b>*</b></font></td>
                <td>
                    <input type='text' name='client_addr' value="$client_addr"/>(<font color="red"><b>*</b></font>IP地址或域名)
                </td>
            </tr>
            <tr class="env">
                <td class="add-div-type">同步用户组的用户组织结构<font color="red"><b>*</b></font></td>
                <td>
                    <input type='text' id="sync_orgs" name='sync_orgs' readonly value="$sync_orgs" onclick="createTreeWindow('sync_orgs');" style="width:400px;"/>
                </td>
            </tr>
            <tr  class="odd">
                <td class="add-div-type" >是否立即同步</td>
                <td>
                    <input type='checkbox' name='sync_right_now' $sync_now_checked/>
                </td>
            </tr>
        </table>
        <input type='hidden' name='ACTION' value='$action' />
        <input type="hidden" name="sure" value="y">
        <input type="hidden" name="line" value="$par{'line'}"/>
        <input type="hidden" name="last_time" value="$last_time"/>
EOF
;    
    &closeeditorbox($buttontext, _("Cancel"), "submitbutton", "createrule", $ENV{'SCRIPT_NAME'});
}

sub display_rules(){
    printf <<EOF
    <table class="ruleslist">
        <tr>
            <td width="4%" class="boldbase">序号</td>
            <td width="10%" class="boldbase">名称</td>
            <td width="15%" class="boldbase">描述</td>
            <td width="15%" class="boldbase">同步客户端地址</td>
            <td width="33%" class="boldbase">同步的用户组结构</td>
            <td width="15%" class="boldbase">上次同步时间</td>
            <td width="8%" class="boldbase">活动动作</td>
        </tr>
    
EOF
    ;
    my $length = 0;
    my @config = read_conf_file($conffile);
    $length = @config;
    if($length > 0){
        my $i = 0;
        for($i = 0; $i < $length; $i++){
            my @temp = split(/,/, $config[$i]);
            my $sync_name = $temp[0];
            my $description = $temp[1];
            my $client_addr = $temp[2];
            my $sync_orgs = $temp[3];
            $sync_orgs = "<div>".$sync_orgs."</div>";
            $sync_orgs =~ s/;/\<\/div\>\<div\>/g; 
            my $last_time = $temp[4];
            my $tr_class = "";
            if ($par{'line'} eq $i) 
            {
                $tr_class = "selected";
            } elsif ($i % 2) {
                $tr_class = "odd";
            } else {
                $tr_class = "env";
            }
            printf <<EOF
            <tr class="$tr_class">
                <td width="%" class="">$i</td>
                <td width="%" class="">$sync_name</td>
                <td width="%" class="">$description</td>
                <td width="%" class="">$client_addr</td>
                <td width="%" class="">$sync_orgs</td>
                <td width="%" class="">$last_time</td>
                <td width="%" align='center'>
                    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
                        <input type='hidden' name='ACTION' value='sync' />
                        <input class='imagebutton' type='image' name='submit' src='/images/up-top.png' alt='立即同步' title='立即同步' />
                        <input type='hidden' name='line' value='$i' />
                        <input type='hidden' name='sync_orgs' value='$temp[3]' />
                    </form>
                    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
                        <input type='hidden' name='ACTION' value='edit' />
                        <input class='imagebutton' type='image' name='submit' src='/images/edit.png' alt='编辑' title='编辑' />
                        <input type='hidden' name='line' value='$i' />
                    </form>
                    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
                        <input type='hidden' name='ACTION' value='remove' />
                        <input class='imagebutton' type='image' name='submit' src='/images/delete.png' alt='删除' title='删除' />
                        <input type='hidden' name='line' value='$i' />
                    </form>
                </td>
            </tr>
EOF
            ;
        }
        printf <<EOF
        <tr class="table-footer">
            <td colspan="7">
                  <b>标签:</b>
                <img src="/images/up-top.png" title="立即同步">
                立即同步
                <img src="/images/edit.png" title="编辑">
                编辑
                <img src="/images/delete.png" title="移除">
                移除
            </td>
        </tr>
    </table>
EOF
        ;
    }else{
        no_tr(7,_('Current no content'));
    }
}

sub check_form(){
    printf <<EOF
    <script>
        var object = {
            'form_name':'USERS_SYNC_FORM',
            'option'   :{
                'sync_name':{
                    'type':'text',
                    'required':'1',
                    'check':'other|',
                    'other_reg':'/\.+/',
                    'ass_check':function(eve){
                        var state = eve._getCURElementsByName("submitbutton","input","USERS_SYNC_FORM")[0].value;
                        if(state == '编辑'){
                            return;
                        }
                        var msg="";
                        var key = 0;
                        var sync_name = eve._getCURElementsByName("sync_name","input","USERS_SYNC_FORM")[0].value;
                        if(!eve.settins){
                            \$.ajax({
                                  type : "get",
                                  url : '/cgi-bin/chinark_back_get.cgi',
                                  async : false,
                                  data : 'path=/var/efw/openvpn/sync/settings',
                                  success : function(data){ 
                                    eve.settins = data;                                                                     
                                  }
                            });
                        }
                        var exist = eve.settins.split('\\n');
                        for (var i = 0; i < exist.length; i++) {
                            var tmp = exist[i].split(',');
                            if(sync_name == tmp[0]){
                                msg = '名称'+sync_name+'已存在';
                                break;
                            }
                        }
                        return msg;              
                    }
                },
                'description':{
                    'type':'text',
                    'required':'0',
                    'check':'note|',
                    'ass_check':function(eve){
                                          
                    }
                },
                'client_addr':{
                    'type':'text',
                    'required':'1',
                    'check':'ip|domain|',
                    'ass_check':function(){
                        
                    }
                },
                'sync_orgs':{
                    'type':'text',
                    'required':'1',
                    'check':'other|',
                    'other_reg':'/\.+/',
                    'ass_check':function(){
                        
                    }
                }
            }
        }
        var object2 = {
            'form_name':'SYNC_POLICY_FORM',
            'option'   :{
                'server_ip':{
                    'type':'text',
                    'required':'1',
                    'check':'ip|'
                }
            }
         }
         
        var check = new ChinArk_forms();
        check._main(object);
        check._main(object2);
        //check._get_form_obj_table("SYNC_POLICY_FORM");
    </script>
EOF
;
}

sub doaction(){
    $action = $par{'ACTION'};
    
    if($action eq 'apply'){
        
        `$restart`;
        `rm $needreload`;
        $notemessage = "同步策略成功应用";
        %par = ();
    }
    
    if($action eq 'save'){
        
        my %policy;
        $policy{'ENABLE'} = $par{'ENABLED'};
        $policy{'MODEL'} = $par{'sync_policy'};
        if($policy{'MODEL'} eq 'client'){
            $policy{'SERVICE_IP'} = $par{'server_ip'};
        }else{
            $policy{'SERVICE_IP'} = '';
        }
        &writehash("$sync_policy", \%policy);
        `touch $needreload`;
        #$notemessage = "保存成功！";
        %par = ();
    }
    
    my $exc_result;
    if($action eq 'add'  || ($action eq 'edit' && $par{'sure'} eq 'y')){
        ##先检查传入值是否正确
        my $line = $par{'line'};
        my $sync_name = $par{'sync_name'};
        my $description = $par{'description'};
        my $client_addr = $par{'client_addr'};
        my $sync_orgs = $par{'sync_orgs'};
        my $sync_now = $par{'sync_right_now'};
        my $date = &getTime();#获取当前系统时间的Hash
        my $time = $date->{'mydate'};#获取具体时间,精确到秒 
        my $last_time = $par{'last_time'};
        ##再保存
        #组装字符串~
        my $record = "";
        if($sync_now eq 'on'){
            $record = "$sync_name,$description,$client_addr,$sync_orgs,$time";
            #同步操作
            $sync_orgs =~ s/;/:/g;
            #$exc_result = `sudo ResMng -syn "$sync_orgs"`;
            $exc_result = `$syn_operation "$client_addr" "$sync_orgs"`;
        }else{
            $record = "$sync_name,$description,$client_addr,$sync_orgs,$last_time";
        }
        my @lines = read_conf_file($conffile);
        #如果有行号则复写内容
        if($line ne ''){
            $lines[$line] = $record;
        }else{
            push(@lines, $record);
        }
        save_config_file(\@lines,$conffile);
        %par = ();
        chomp($exc_result);
        if ($sync_now eq 'on'){
            if( $exc_result eq '1' ){
                $notemessage = "同步成功";
            }else{
                if($exc_result eq "error. can't link to remote host."){
                    $errormessage = "同步失败，不能连接到远程服务器";
                }elsif($exc_result eq "error. password is invaliad."){
                    $errormessage = "同步失败，连接远程服务器失败";
                }elsif($exc_result =~ /用户组不存在/){
                    $exc_result =~ s/error. //g;
                    $errormessage = "同步失败，";
                    $errormessage .= $exc_result;
                }else{
                    $errormessage = "同步失败";
                }
            }
        }
    }
    
    
    if($action eq 'sync'){
        my $line = $par{'line'};
        my @lines = read_conf_file($conffile);
        my $record = "";
        if($line ne ''){
            $record = $lines[$line];
            my $sync_orgs = $par{'sync_orgs'};
            chomp($sync_orgs);
            $sync_orgs =~ s/;/:/g;
            #同步操作
            #$notemessage .= $sync_orgs;
            #$exc_result = `sudo ResMng -syn "$sync_orgs"`;
            my @records = split(/,/, $record);
            $exc_result = `$syn_operation "$records[2]" "$sync_orgs"`;
            my $date = &getTime();#获取当前系统时间的Hash
            my $time = $date->{'mydate'};#获取具体时间,精确到秒 
            $record = "$records[0],$records[1],$records[2],$records[3],$time";
            $lines[$line] = $record;
            save_config_file(\@lines,$conffile);
        }
        %par = ();
        chomp($exc_result);
        if( $exc_result eq '1' ){
            $notemessage = "同步成功";
        }else{
            if($exc_result eq "error. can't link to remote host."){
                $errormessage = "同步失败，不能连接到远程服务器";
            }elsif($exc_result eq "error. password is invaliad."){
                $errormessage = "同步失败，连接远程服务器失败";
            }elsif($exc_result =~ /用户组不存在/){
                $exc_result =~ s/error. //g;
                $errormessage = "同步失败，";
                $errormessage .= $exc_result;
            }else{
                $errormessage = "同步失败";
            }
        }
    }
    
    if($action eq 'remove'){
        
        my $line = $par{'line'};
        my @lines = read_conf_file($conffile);
        if($line ne ''){
            delete $lines[$line];
            save_config_file(\@lines,$conffile);
            $notemessage = "删除成功！";
        }
        %par = ();
    }
}

sub getTime()
{
    #time()函数返回从1970年1月1日起累计秒数
    my $time = shift || time();
    
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($time);
    
    $mon ++;
    $sec  = ($sec<10)?"0$sec":$sec;#秒数[0,59]
    $min  = ($min<10)?"0$min":$min;#分数[0,59]
    $hour = ($hour<10)?"0$hour":$hour;#小时数[0,23]
    $mday = ($mday<10)?"0$mday":$mday;#这个月的第几天[1,31]
    $mon  = ($mon<10)?"0".($mon+1):$mon;#月数[0,11],要将$mon加1之后，才能符合实际情况。
    $year+=1900;#从1900年算起的年数
    
    #$wday从星期六算起，代表是在这周中的第几天[0-6]
    #$yday从一月一日算起，代表是在这年中的第几天[0,364]
    #$isdst只是一个flag
    my $weekday = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat')[$wday];
    return { 'second' => $sec,
             'minute' => $min,
             'hour'   => $hour,
             'day'    => $mday,
             'month'  => $mon,
             'year'   => $year,
             'weekNo' => $wday,
             'wday'   => $weekday,
             'yday'   => $yday,
             'date'   => "$year年$mon月$mday日",
             'mydate' => "$year年$mon月$mday日 $hour:$min:$sec"
          };
}

#已废弃
sub sync_passwd(){
    my @sync_users = read_conf_file($sync_whitelist);
    my @passwd_users = read_conf_file($passwd);
    my @sync_passwd_users;
    foreach my $syn_user (@sync_users){
        my @syn_user_splitted = split(/,/, $syn_user);
        foreach my $passwd_user (@passwd_users){
            my @passwd_user_splitted = split(/:/, $passwd_user);
            if(    $syn_user_splitted[0] eq $passwd_user_splitted[0]){
                push(@sync_passwd_users, $passwd_user);
            }
        }
    }
    if(!-e $sync_passwd){
        `touch $sync_passwd`;
    }
    save_config_file(\@sync_passwd_users, $sync_passwd);
}
