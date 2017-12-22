#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: L2TP配置页面
#
# AUTHOR:  (XINZHIWEI), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2014/04/11-09:00
#===============================================================================

require '/var/efw/header.pl';

my $setting_dir = "/var/efw/xl2tpd";   #/var/efw/telnetproxy改成/var/efw/l2tp_config
my $setting_file = $setting_dir."/settings";  #同上
#my $default_setting_file = "${swroot}/l2tpd/default_settings";  #l2tp有没有默认的配置文件呢？这个目录写的对不对？
my $cmd = "sudo /usr/local/bin/restartxl2tpd";  #调用后台脚本/usr/local/bin/restartl2tpd  命令字符串必须用双引号括起来，切记不要用单引号。因为你调用语句是这样的，system($cmd);system括号里的参数必须是双引号才能识别
my %par;
my %save;
#记录日志的变量
my $CUR_PAGE = "l2tp配置" ;      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

my $extraheaders = '<script type="text/javascript" src="/include/l2tp.js"></script>';
my $errormessage='';
my $warnmessage='';
my $notemessage='';



&init();
&getcgihash(\%par);

&do_action();
&showhttpheaders();
&openpage("L2TP配置", 1, $extraheaders);
&openbigbox($errormessage, $warnmessage, $notemessage);
&closebigbox();
#&display_switch();
&openbox('100%', 'left', 'L2TP配置');
&display_form();
&closebox();
&check_form();
&closepage();


sub init() {
    if(! -e $setting_dir){
       # system('mkdir -p $setting_dir');     # 这里用单引号是错误的，此系统函数就不会执行，必须改成双引号才能识别
        system( "mkdir -p $setting_dir" );
    }
    if(! -e $setting_file){
        # system('touch $setting_file');     #错误同上  
        system( "touch $setting_file" );
    }
}

sub do_action(){
    #存在par{'ACTION'}则处理信息并存入配置文件。
    if ($par{'ACTION'} eq 'save') {
        my $needrestart = 0;
        #保存配置信息,文件不存在则创建。

        my %savehash = ();

        if( !$par{'ENABLED'} ) { $savehash{'ENABLED'} = "off"; }
        else { $savehash{'ENABLED'} = "on"; }

        $savehash{'LOCALIP'} = $par{'local_ip_addr'};
        $savehash{'REMOTEIPSTART'} = $par{'remote_ip_start'};
        $savehash{'REMOTEIPEND'} = $par{'remote_ip_end'};
        $savehash{'ENCRYPTION'} = $par{'encryp'};

        if( $par{'encryp'} eq "IPSEC") {   # 只有选择了‘加密’模式，才需要写PRESHARED值到后台文件
            $savehash{'PRESHARED'} = $par{'pre_shared'};
        }

        &writehash($setting_file,\%savehash);
        system($cmd);
        
        $log_oper = 'edit';
        &write_log($CUR_PAGE,$log_oper,0,$rule_or_congfig);
        $notemessage = "已成功保存当前修改";
    }
}



sub display_form(){
    &readhash( $setting_file, \%savehash );
	my $checked = "";
    my $encryp_selected = "";
    my $not_encryp_selected = "";

    $enabled = $savehash{'ENABLED'};
    if($enabled eq "on")  { $checked =' checked="checked" '; }
    $local_ip_addr = $savehash{'LOCALIP'};
    $remote_ip_start = $savehash{'REMOTEIPSTART'};
    $remote_ip_end = $savehash{'REMOTEIPEND'};
    $encryp = $savehash{'ENCRYPTION'};
    $pre_shared = $savehash{'PRESHARED'};

if($encryp eq "IPSEC")  {  $encryp_selected = ' selected="selected" ';   }
if($encryp eq "NOIPSEC")  {  $not_encryp_selected = ' selected="selected" ';  }
    printf <<EOF
    <form name="L2TP_FORM" enctype="multipart/form-data" method="post" action="$ENV{SCRIPT_NAME}">
        <table width="100%" border='0' cellspacing="0" cellpadding="4">
            <tr class="odd">
                <td width="15%" class="add-div-width">启用 *</td>
                <td><input type="checkbox" name="ENABLED"  $checked/></td><!--bug修复 20150525 去掉value="$enabled" -->
            </tr>

            <tr class="odd"><td class="add-div-width" rowspan="2">客户使用IP地址范围 *</td>
                <td><span><b>起始地址</b> </span> <input id="remote_ip_0" type="text" name="remote_ip_start" value="$remote_ip_start" ></td>
            </tr>
            <tr class="odd">
                <td><span><b>结束地址</b> </span> <input id="remote_ip_1" type="text" name="remote_ip_end" value="$remote_ip_end" ></td>
            </tr>
            <tr class="env">
                <td width="15%" class="add-div-width">本地隧道IP地址 *</td>
                <td><input id="local_ip_0" type="text" name="local_ip_addr" value="$local_ip_addr" style="width:208px"></td>
            </tr>
            <tr class="env">
                <td class="add-div-width">加密方式 *</td>
                <td>
                    <select id='encryp' name="encryp" value="" style="width:212px"/>
                        <option value="IPSEC" $encryp_selected>IPSEC 加密</option>
                        <option value="NOIPSEC" $not_encryp_selected>不加密</option>
                    </select>
                </td>
            </tr>

            <tr class="odd" id="pre_shared_tr">
                <td class="add-div-width">预共享密钥</td>
                <td><input id="show_pre" type="password" name="pre_shared" value="$pre_shared" style="width:208px"></td>
            </tr>

            <tr class="table-footer">
                <td colspan="2">
                    <input  type="submit" name="submit" class="net_button" value="保存" />
                    <input  type="hidden" name="ACTION" value="save" />
                </td>
            </tr>
    </table>
    </form>
EOF
    ;
}

sub check_form(){
}