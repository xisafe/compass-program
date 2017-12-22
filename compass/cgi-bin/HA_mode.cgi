#!/usr/bin/perl
#author: LiuJulong
#createDate: 2015/05/05
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $status_dir;         #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $setting_file;       #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %hash_ipmask;
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $cmd_getinterface;
my $waiting_gif;
my $LOAD_ONE_PAGE = 0;
my $can_save = 0;
my $json = new JSON::XS;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/HA';                                       #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;                      #规则所存放的文件夹
    $status_dir         = $conf_dir.'/status';                         #规则所存放的文件夹
    $conf_file          = $conf_dir.'/backupgroup';                    #规则信息所存放的文件
    $setting_file       = $conf_dir.'/hamode';                         #规则信息所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload';           #启用信息所存放的文件
    $waiting_gif        = "/images/wait.gif";
    $cmd                = "/usr/local/bin/sethirl -f";
    $cmd_getinterface   = "sudo /usr/local/bin/netstatus_json.py";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/HA_SYNC.js"></script>
                    <script language="JavaScript" src="/include/waiting.js"></script>
                    <script language="JavaScript" charset="gb2312" src="/include/HA_mode_controller.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#

    &make_file();#检查要存放规则的文件夹和文件是否存在
    %hash_ipmask = (
            "1" =>"128.0.0.0",
            "2"=>"192.0.0.0",
            "3"=>"224.0.0.0",
            "4"=>"240.0.0.0",
            "5"=>"248.0.0.0",
            "6"=>"252.0.0.0",
            "7"=>"254.0.0.0",
            "8"=>"255.0.0.0",
            "9"=>"255.128.0.0",
            "10"=>"255.192.0.0",
            "11"=>"255.224.0.0",
            "12"=>"255.240.0.0",
            "13"=>"255.248.0.0",
            "14"=>"255.252.0.0",
            "15"=>"255.254.0.0",
            "16"=>"255.255.0.0",
            "17"=>"255.255.128.0",
            "18"=>"255.255.192.0",
            "19"=>"255.255.224.0",
            "20"=>"255.255.240.0",
            "21"=>"255.255.248.0",
            "22"=>"255.255.252.0",
            "23"=>"255.255.254.0",
            "24"=>"255.255.255.0",
            "25"=>"255.255.255.128",
            "26"=>"255.255.255.192",
            "27"=>"255.255.255.224",
            "28"=>"255.255.255.240",
            "29"=>"255.255.255.248",
            "30"=>"255.255.255.252",
            "31"=>"255.255.255.254",
            "32"=>"255.255.255.255",
    );
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $panel_name = $par{'panel_name'};
    if( !$action ) {
        $action = $query{'ACTION'};
    }

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==下载数据==#
        &load_data();
    } 
    elsif ($action eq 'save') {
        #==保存数据==#
        &save_data();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_list_div();
    &closepage();
}
sub display_ha_div(){
    if( -f $setting_file ) {
        &readhash( $setting_file, \%settings );
    }
    my $html_heartdev = "<select name='HEARTDEV'>";
    my @interfaces = &get_interfaces();
    foreach(@interfaces){
        my $is_checked = "";
        if($_ eq $settings{'HEARTDEV'}){
            $is_checked = "selected";
        }
        $html_heartdev .= "<option $is_checked value='$_'>$_</option>";
    }
    $html_heartdev .= "</option>";
    
    my $html_heartcidr = "<select name='HEART_CIDR'>";
    for(my $i=1; $i<33; $i++){
        my $is_checked_cidr = "";
        if($i eq $settings{'HEART_CIDR'}){
            $is_checked_cidr = "selected";
        }
        $html_heartcidr .= "<option $is_checked_cidr value='$i'>/$i - $hash_ipmask{$i}</option>"
    }
    $html_heartcidr .= "</option>";
    
    my $html_manageipcidr = "<select name='MANAGEIP_CIDR'>";
    for(my $i=1; $i<33; $i++){
        my $is_checked_managecidr = "";
        if($i eq $settings{'MANAGEIP_CIDR'}){
            $is_checked_managecidr = "selected";
        }
        $html_manageipcidr .= "<option $is_checked_managecidr value='$i'>/$i - $hash_ipmask{$i}</option>"
    }
    $html_manageipcidr .= "</option>";
    
    my ($is_selected_master,$is_selected_slave) = ("","");
    if($settings{'HA_SIDE'} eq "MASTER"){
        $is_selected_master = "selected";
    }else{
        $is_selected_slave = "selected";
    }
    
    my ($is_selected_master1,$is_selected_slave1) = ("","");
    if($settings{'HA1_SIDE'} eq "MASTER"){
        $is_selected_master1 = "selected";
    }else{
        $is_selected_slave1 = "selected";
    }
    
    my ($is_selected_master2,$is_selected_slave2) = ("","");
    if($settings{'HA2_SIDE'} eq "MASTER"){
        $is_selected_master2 = "selected";
    }else{
        $is_selected_slave2 = "selected";
    }
    
    my $is_checked_enabled = "";
    if($settings{'ENABLED'} eq 'on'){
        $is_checked_enabled = "checked";
    }
    
    my ($is_checked_as,$is_checked_aa) = ("","");
    if($settings{'HA_MODE'} eq 'AA'){
        $is_checked_aa = "checked";
    }else{
        $is_checked_as = "checked";
    }
    
    my $bac_group = $settings{'BACKGROUP'};
    my $bac_group1 = $settings{'BACKGROUP1'};
    my $bac_group2 = $settings{'BACKGROUP2'};
    
    my ($show_bac,$show_bac1,$show_bac2) = ("请选择备份组","请选择备份组","请选择备份组");
    if($bac_group){
        $show_bac = "已选备份组：".$bac_group;
        $show_bac =~ s/&/,/g;
    }
    if($bac_group1){
        $show_bac1 = "已选备份组：".$bac_group1;
        $show_bac1 =~ s/&/,/g;
    }
    if($bac_group2){
        $show_bac2 = "已选备份组：".$bac_group2;
        $show_bac2 =~ s/&/,/g;
    }
    openbox('100%', 'left', _('双机模式配置'));
printf <<EOF
    <form name="HAMODE_FILTER_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="odd">
    <td class="add-div-type" style="width:23%">启用</td>
    <td colspan="2"><input type="checkbox" id="ENABLED" name='ENABLED' $is_checked_enabled value="on"/></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type" style="width:250px">双机模式配置</td>
    <td colspan="2">
      <input type="radio" name='HA_MODE' $is_checked_as value="AS" onclick="change_show_mode();"/><span>主备模式</span>
      <input type="radio" name='HA_MODE' $is_checked_aa value="AA" onclick="change_show_mode();"/><span>主主模式</span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">心跳接口*</td>
    <td colspan="2">$html_heartdev</td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">本端心跳口IP*</td>
    <td colspan="2"><input type="text" id="HEART_IP" name='HEART_IP' value="$settings{'HEART_IP'}"/></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">子网掩码*</td>
    <td colspan="2">$html_heartcidr</td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">对端心跳口IP*</td>
    <td colspan="2"><input type="text" id="HEARTPEER_IP" name='HEARTPEER_IP' value="$settings{'HEARTPEER_IP'}"/><span>（必须与本端心跳口IP同网段）</span></td>
    </tr>
    <!--<tr class="odd">
    <td class="add-div-type">管理IP地址*</td>
    <td colspan="2"><input type="text" id="MANAGEIP" name='MANAGEIP' value="$settings{'MANAGEIP'}"/></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">子网掩码*</td>
    <td colspan="2">$html_manageipcidr</td>
    </tr>-->
    <tr class="odd ctr_as">
    <td class="add-div-type">热备组号*</td>
    <td colspan="2"><input type="text" id="HA_ID" name='HA_ID' value="$settings{'HA_ID'}"/><span>（范围1-255）</span></td>
    </tr>
    <tr class="odd ctr_as">
    <td class="add-div-type">身份*</td>
    <td colspan="2">
      <select name="HA_SIDE">
        <option $is_selected_master value="MASTER">主机</option>
        <option $is_selected_slave value="SLAVE">备机</option>
      </select>
    </td>
    </tr>
    <tr class="odd ctr_as">
    <td class="add-div-type">优先级*</td>
    <td colspan="2"><input type="text" id="HA_PRIORITY" name='HA_PRIORITY' value="$settings{'HA_PRIORITY'}"/><span>（范围1-255）</span></td>
    </tr>
    <tr class="odd ctr_as">
    <td class="add-div-type">备份组配置*</td>
    <td colspan="2">
      <!--<input type="button" class="net_button" id="btn_bac" value="配置" onclick="show_backgroup_panel(this,'$bac_group');"/>-->
      <a style="text-decoration:underline;cursor:pointer;" id="btn_bac" onclick="show_backgroup_panel(this,'$bac_group');">$show_bac</a>
      <input type="hidden" id="BACKGROUP" name='BACKGROUP' value="$settings{'BACKGROUP'}"/>
    </td>
    </tr>
    <tr class="odd ctr_as">
    <td class="add-div-type">同步方式</td>
    <td colspan="2">
      <input type="button" class="net_button" id="btn_ahead" value="同步到对端" onclick="goto_sync(0)"/>
      <input type="button" class="net_button" id="btn_local" value="同步到本地" onclick="goto_sync(1)"/>
    </td>
    </tr>
    
    <tr class="odd ctr_aa">
    <td class="add-div-type" rowspan="4">热备组1*</td>
    <td><span>热备组号</span></td>
    <td><input type="text" id="HA1_ID" name="HA1_ID" value="$settings{'HA1_ID'}"/><span>（范围1-255）</span></td>
    </tr>
    <tr class="odd ctr_aa">
    <td><span>优先级</span></td>
    <td><input type="text" id="HA1_PRIORITY" name="HA1_PRIORITY" value="$settings{'HA1_PRIORITY'}"/><span>（范围1-255）</span></td>
    </tr>
    <tr class="odd ctr_aa">
    <td><span>身份</span></td>
    <td>
      <select name="HA1_SIDE">
        <option $is_selected_master1 value="MASTER">主机</option>
        <option $is_selected_slave1 value="SLAVE">备机</option>
      </select>
    </td>
    </tr>
    <tr class="odd ctr_aa">
    <td><span>备份组配置</span></td>
    <td>
      <!--<input type="button" class="net_button" id="btn_h1bac" value="配置" onclick="show_backgroup_panel(this,'$bac_group1');"/>-->
      <a style="text-decoration:underline;cursor:pointer;" id="btn_h1bac" onclick="show_backgroup_panel(this,'$bac_group1');">$show_bac1</a>
      <input type="hidden" id="BACKGROUP1" name='BACKGROUP1' value="$settings{'BACKGROUP1'}"/>
    </td>
    </tr>
    
    <tr class="odd ctr_aa">
    <td class="add-div-type" rowspan="4">热备组2*</td>
    <td><span>热备组号</span></td>
    <td><input type="text" id="HA2_ID" name="HA2_ID" value="$settings{'HA2_ID'}"/><span>（范围1-255）</span></td>
    </tr>
    <tr class="odd ctr_aa">
    <td><span>优先级</span></td>
    <td><input type="text" id="HA2_PRIORITY" name="HA2_PRIORITY" value="$settings{'HA2_PRIORITY'}"/><span>（范围1-255）</span></td>
    </tr>
    <tr class="odd ctr_aa">
    <td><span>身份</span></td>
    <td>
      <select name="HA2_SIDE">
        <option $is_selected_master2 value="MASTER">主机</option>
        <option $is_selected_slave2 value="SLAVE">备机</option>
      </select>
    </td>
    </tr>
    <tr class="odd ctr_aa">
    <td><span>备份组配置</span></td>
    <td>
      <!--<input type="button" class="net_button" id="btn_h2bac" value="配置" onclick="show_backgroup_panel(this,'$bac_group2');"/>-->
      <a style="text-decoration:underline;cursor:pointer;" id="btn_h2bac" onclick="show_backgroup_panel(this,'$bac_group2');">$show_bac2</a>
      <input type="hidden" id="BACKGROUP2" name='BACKGROUP2' value="$settings{'BACKGROUP2'}"/>
    </td>
    </tr>
    
    
    <tr class="table-footer">
    <td colspan="3">
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
    
    
    my $check_status="正在检测  "."<span><img src='$waiting_gif'/></span>";
printf <<EOF
    <div style="margin-top: 20px;margin-bottom:20px;">
      <table class="ruleslist">
        <tr>
          <td  class="boldbase" style="width:100%;">状态信息</td>
        </tr>
        <tr class="oodd ctr_as">
          <td>
            <div style = "float:left; font-weight:bold; text-align:center; width:33%">心跳口连接状态：<span id = "Link_status">$check_status</span></div>
            <div style = "float:left; font-weight:bold; text-align:center; width:33%">运行状态：<span id = "Run_status">$check_status</span></div>
            <div style = "float:left; font-weight:bold; text-align:center; width:33%">同步状态：<span id = "Sync_status">$check_status</span></div>
          </td>
        </tr>
        <tr class="oodd ctr_aa">
          <td>
            <div style = "float:left; font-weight:bold; text-align:center; width:33%">心跳口连接状态：<span id = "Link_status2">$check_status</span></div>
            <div style = "float:left; font-weight:bold; text-align:center; width:33%">热备组1状态：<span id = "backgroup1_status">$check_status</span></div>
            <div style = "float:left; font-weight:bold; text-align:center; width:33%">热备组2状态：<span id = "backgroup2_status">$check_status</span></div>
          </td>
        </tr>
      </table>
    </div>
EOF
;
    &run_ajax();
}
sub display_list_div() {
    printf<<EOF
    <div id="panel_mesg"></div>
    <div id="panel_backgroup"></div>
EOF
;
    &display_ha_div();
}

sub run_ajax(){
    printf <<EOF
         <script>
         function begin_ajax(){
             \$.get('/cgi-bin/checkHA.cgi', function(data){
                var strings=data.split("===");
                var len = strings.length;
                var color="";
                var str="";
                var run_state = new Array("故障状态", "备机状态", "主机状态", "静默状态");
                var elem = strings[1].split(",");
                if (elem[0] == "0")
                {
                    str ="<font color='red'>未连接</font>";
                }
                else
                {
                    str ="<font color='green'>已连接</font>";
                }       
                \$("#Link_status").html(str);
                \$("#Link_status2").html(str);
               
                if (elem[1] == "0")
                {
                    str ="<font color='red'>故障状态</font>";
                }
                else
                {
                    var num = parseInt(elem[1]);
                    str ="<font color='green'>" + run_state[num] + "</font>";
                }
                \$("#Run_status").html(str);
                
                if (elem[2] == "0")
                {
                    str ="<font color='red'>故障状态</font>";
                }
                else
                {
                    var num = parseInt(elem[2]);
                    str ="<font color='green'>" + run_state[num] + "</font>";
                }
                \$("#backgroup1_status").html(str);
                
                if (elem[3] == "0")
                {
                    str ="<font color='red'>故障状态</font>";
                }
                else
                {
                    var num = parseInt(elem[3]);
                    str ="<font color='green'>" + run_state[num] + "</font>";
                }
                \$("#backgroup2_status").html(str);

                if (elem[4] == "0")
                {
                    str ="<font color='red'>未同步</font>";
                }
                else
                {
                    str ="<font color='green'>已同步</font>";
                }       
                \$("#Sync_status").html(str);

            });
         }
         window.setInterval("begin_ajax()",60000);
         begin_ajax();
         </script>
EOF
;
}

sub save_data(){
    $settings{'HA_MODE'} = $par{'HA_MODE'};
    $settings{'ENABLED'} = $par{'ENABLED'};
    # $settings{'MANAGEIP'} = $par{'MANAGEIP'};
    # $settings{'MANAGEIP_CIDR'} = $par{'MANAGEIP_CIDR'};
    $settings{'MANAGEIP'} = "";
    $settings{'MANAGEIP_CIDR'} = "";
    $settings{'HEART_IP'} = $par{'HEART_IP'};
    $settings{'HEART_CIDR'} = $par{'HEART_CIDR'};
    $settings{'HEARTDEV'} = $par{'HEARTDEV'};
    $settings{'HEARTPEER_IP'} = $par{'HEARTPEER_IP'};
    
    if($par{'HA_MODE'} eq 'AS'){
        $settings{'BACKGROUP'} = $par{'BACKGROUP'};
        $settings{'HA_SIDE'} = $par{'HA_SIDE'};
        $settings{'HA_ID'} = $par{'HA_ID'};
        $settings{'HA_PRIORITY'} = $par{'HA_PRIORITY'};
        if($par{'BACKGROUP'}){
            $can_save = 1;
        }
    }else{
        $settings{'BACKGROUP1'} = $par{'BACKGROUP1'};
        $settings{'HA1_SIDE'} = $par{'HA1_SIDE'};
        $settings{'HA1_ID'} = $par{'HA1_ID'};
        $settings{'HA1_PRIORITY'} = $par{'HA1_PRIORITY'};
        $settings{'BACKGROUP2'} = $par{'BACKGROUP2'};
        $settings{'HA2_SIDE'} = $par{'HA2_SIDE'};
        $settings{'HA2_ID'} = $par{'HA2_ID'};
        $settings{'HA2_PRIORITY'} = $par{'HA2_PRIORITY'};
        if($par{'BACKGROUP1'}){
            if($par{'BACKGROUP2'}){
                $can_save = 1;
            }
        }
    }
    
    if($can_save){
        &writehash($setting_file,\%settings);
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
        #&send_status( "0", $reload, $mesg );
        &show_page();
    }else{
        my %settings = ();
        &readhash( $setting_file, \%settings );
        $settings{'ENABLED'} = '';
        &writehash($setting_file,\%settings);
        $reload = 1;
        &create_need_reload_tag();
        &show_page();
        # &show_error_mesg("必须先配置备份组才能保存");
    }
}
sub show_error_mesg($){
    $mesg = shift;
    printf<<EOF
    <script>
      alert("$mesg");
    </script>
EOF
;
}

sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );
    
    my $record_num = @lines;
    my $search = $par{'search'};
    if($search){
        chomp($search);
        #===转换成小写，进行模糊查询==#
        $search = lc($search);
        for(my $i = 0; $i < $record_num; $i++){
            chomp(@lines[$i]);
            if($search ne ""){
                my $searched = 0;
                my $where = -1;
                my @data = split(",", @lines[$i]);
                foreach my $field (@data) {
                    #===转换成小写，进行模糊查询==#
                    my $new_field = lc($field);
                    $where = index($new_field, $search);
                    if($where >= 0) {
                        $searched++;
                    }
                }
                #如果没有一个字段包含所搜寻到子串,则不返回
                if(!$searched){
                    next;
                }
            }
            my %conf_data = &get_config_hash(@lines[$i]);
            if (! $conf_data{'valid'}) {
                next;
            }
            #$conf_data{'id'} = $i;
            push(@content_array, \%conf_data);
            $total_num++;
        }
    }else{
        ( $status, $error_mesg, $total_num ) = &get_content( \@content_array );
    }
    

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    # %ret_data->{'page_size'} = $PAGE_SIZE;
    
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}


sub get_content($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );

    my $from_num = ( $current_page - 1 ) * $page_size;
    my $to_num = $current_page * $page_size;

    my @lines = ();
    my ( $status, $error_mesg ) = &read_config_lines( $conf_file, \@lines );

    my $total_num = @lines;
    if( $total_num < $to_num ) {
        $to_num = $total_num;
    }

    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        #==全部加载===#
        $from_num = 0;
        $to_num = $total_num;
    }
    for ( my $i = $from_num; $i < $total_num; $i++ ) {
        my %config = &get_config_hash( $lines[$i] );
        if( $config{'valid'} ) {
            #$config{'id'} = $i;
            # if( $i % 5 == 0 ) {
            #     $config{'uneditable'} = 1;
            #     $config{'undeletable'} = 1;
            # }
            push( @$content_array_ref, \%config );
        }
    }
    return ( $status, $error_mesg, $total_num );
}

sub get_config_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    $config{'valid'} = 1;#默认是合法的行，如果有不合法的，将该字段置为0
    if ($line_content eq '') {
        $config{'valid'} = 0;
        return %config;
    }
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(/,/, $line_content);
    $config{'id'}   = $temp[0];
    $config{'name'}   = $temp[0];
    $config{'virtual_ip'}   = $temp[1];
    $config{'interface_backupgroup'}   = $temp[2];
    $config{'interface_listenner'}   = $temp[3];
    #============自定义字段组装-END===========================#
    return %config;
}


sub send_status($$$) {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 1 表示重新应用，其他表示不应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status,$reload,$mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'reload'} = $reload;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}

sub getqueryhash($){
    my $query = shift;
    my $query_string = $ENV{'QUERY_STRING'};
    if ($query_string ne '') {
        my @key_values = split("&", $query_string);
        foreach my $key_value (@key_values) {
            my ($key, $value) = split("=", $key_value);
            $query->{$key} = $value;
            #===对获取的值进行一些处理===#
            $query->{$key} =~ s/\r//g;
            $query->{$key} =~ s/\n//g;
            chomp($query->{$key});
        }
    }
    return;
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $setting_file){
        system("touch $setting_file");
    }
    
}

sub apply_data() {
    my $result;
    system($cmd);
    $result = $?;
    chomp($result);
    my $msg;
    if($result == 0){
        $msg = "应用成功";
    }else{
        $msg = "应用失败";
    }
    &clear_need_reload_tag();
    &send_status( 0, 0, $msg );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
#获取接口
sub get_interfaces(){
    my @all_hash;
    my @temp;
    my @items_na = ();
    
    my $str_json = `$cmd_getinterface`;
    chomp($str_json);
    my $href_json = $json->decode($str_json);
    @temp = @$href_json;
    
    foreach(@temp){
        if($_->{'Area'} eq 'N/A'){
            $href_item = $_->{'interface'};
            @items_na = @$href_item;
        }
    }
    
    my $len_item = @items_na;
    if($len_item){
        foreach my $interface(@items_na){
            push(@all_hash,$interface->{'name'});
        }
    }
    
    return @all_hash;
}