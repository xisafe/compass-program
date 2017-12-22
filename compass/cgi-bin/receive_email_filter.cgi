#!/usr/bin/perl
#==============================================================================#
# 描述:接收邮件过滤页面
#
# 作者: 辛志薇
# 公司: capsheaf
# 历史:
#   2015-04-10 创建
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $settings_file_path;
my $white_list_file_path;
my $black_list_file_path;
my $running_tag_file_path;
my $needreload = '/var/efw/p3scan/needreload';
my $restartcmd = '/usr/local/bin/restartpopscan';
# my $reload = 0;
my $errormessage = "";
my $warnmessage = "";
my $notemessage = "";


my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变

#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post请求传过来的变量
    &getcgihash(\%par);
    #获取get请求传过来的变量
    &get_query_hash(\%query);
    #初始化变量值
    &init_data();
    &make_file();
    #做出响应
    &do_action();
}
sub init_data(){
    $settings_file_path = '/var/efw/p3scan/settings';
    $white_list_file_path = '/var/efw/spamassassin/whitelist';
    $black_list_file_path = '/var/efw/spamassassin/blacklist';
    $running_tag_file_path = '/var/efw/p3scan/running_tag_file';
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    # <link type="text/css" href="/include/add_list_base.css" /> 
    # 一开始用的样式文件是add_list_base.css，但为了和刘炬隆的web内容过滤页面样式相同，故就要用他使用的样式文件template_add_list.css
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/waiting.js"></script>
                    <script language="JavaScript" src="/include/receive_email_filter.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#
}

sub make_file(){

    if(! -e $settings_file_path){
        system("touch $settings_file_path");
    }
    if(! -e $white_list_file_path){
        system("touch $white_list_file_path");
    }
    if(! -e $black_list_file_path){
        system("touch $black_list_file_path");
    }
}


sub create_need_reload_file() {
    if(! -e $needreload){
        system( "touch $needreload" );
    }
}

sub clear_need_reload_file() {
    if( -e $needreload ){
        system( "rm $needreload" );
    }
}
sub apply_data() {
    system( $restartcmd );
    my $status = $?>>8;

    if( $status != 0 ){
        &send_status(-1, 0, "应用失败");
    }else{
        &clear_need_reload_file();
        &send_status(0, 0, "应用成功");
    }
}

sub do_action() {
    my $action = $par{'ACTION'};           # 这个是post方法发送过来的 ACTION 参数值
    my $query_action = $query{'ACTION'};   # 这个是get方法发送过来的 ACTION 参数值
    my $panel_name = $par{'panel_name'};

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if( $action eq 'apply_data' ){
        &apply_data();
    }
    elsif( $action eq 'check_running' ){
        &check_running();
    }
    elsif ( $action eq 'save_data' ) {
        &save_data();
        &create_need_reload_file();
    }
    elsif( $action eq 'load_data') {
        &load_data();
    }
    else {
        &show_page();   # 这种方式只适用于Ajax模式！
    }
    # &show_page();   # 切记在非Ajax模式下每一个动作函数执行之后都要执行&show_page();！
}


sub show_page() {
    &openpage(_('接收邮件过滤'), 1, $extraheader);
    &openbigbox($errormessage,$warnmessage,$notemessage);
    &closebigbox();
    &display_test_div();
    &closepage();
}

sub display_test_div() {
#     printf<<EOF
#     <div id="mesg_box_id" style="width: 96%;margin: 20px auto;"></div>
#     <div id="email_filter_panel_config" style="width: 96%;margin: 20px auto;"></div>
# EOF
#     ;
    # &create_mesg_boxs();
printf<<EOF
    <div id="mesg_box_id" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;

    &openbox('100%', 'left', _('配置邮件过滤'));

printf <<EOF
    <form name="RECEIVE_FILTER_FORM" id="form_id_for_receive_email_filter_panel" action="$ENV{'SCRIPT_NAME'}"
     method="post" onsubmit="return false;">  <!-- 注意如果你想要把表单提交方式改为Ajax的就必须先在form里把form的默认submit动作禁用掉 -->
        <table cellpadding="0" cellspacing="0" width="100%" border='0' >
            <tr class="table-footer">
                <td colspan="2" style="text-align:left;">
                    <input type="checkbox" name="POP_ENABLED" id="pop_enabled_id"/>
                    <span>启用邮件过滤功能</span>
                </td>
            </tr>
            <tr class="odd">
                <td class="add-div-type" style="width:250px">垃圾邮件过滤</td>
                <td>
                    <input type="checkbox" name='CHECKSPAM' id="checkspam_id"/>
                    <span>启用</span>
                </td>
            </tr>
            <tr class="odd">
                <td class="add-div-type" style="width:250px">病毒邮件过滤</td>
                <td>
                    <input type="checkbox" name='CHECKVIRUS' id="checkvirus_id"/>
                    <span>启用</span>
                    <span id="label_tip" style="color:red;"></span>
                </td>
            </tr>
            <tr class="odd">
                <td class="add-div-type" style="width:250px">垃圾邮件发送者黑白名单</td>
                <td>
                    <input type="checkbox" id="checklist_id" name='CHECKLIST' />
                    <span>启用</span>
                </td>
            </tr>
            <tr class="odd"  id="last_tr_id">
                <td class="add-div-type" style="width:250px"></td>
                <td>
                    <div style="width:280px;float:left;" class="checklist_textarea">
                        <span>黑名单(每行一个)</span>
                        <textarea style="width:250px;height:100px;float:left;" name="BLACKLIST"></textarea>
                    </div>
                    <div style="width:280px;float:left;" class="checklist_textarea">
                        <span>白名单(每行一个)</span>
                        <textarea style="width:250px;height:100px;" name="WHITELIST"></textarea>
                    </div>
                    <div style="width:500px;display:block;"><span>例如：\*\@capsheaf.com.cn或support\@capsheaf.com.cn</span></div>
                </td>
            </tr>
            <tr class="table-footer">
                <td colspan="2">
                    <input id="save_button_id" type="submit" class="net_button" value="保存" align="middle" />
                </td>
            </tr>
        </table>
    </form>
EOF
;
    &closebox();

}

sub check_running(){
    my %response;
    $response{'running'} = &is_popscan_running();
    my $result = $json->encode(\%response);
    print $result;
}

sub is_popscan_running() {
    my $result = -1;
    if( -e $running_tag_file_path ){
        $result = 1;
    }
    return $result;
}

sub check_repeated(){
    my %read_hash;
    &readhash( $settings_file_path, \%read_hash );
    my $pop_enabled = $par{'POP_ENABLED'}? 'on':'off';
    my $checkspam = $par{'CHECKSPAM'}? 1:0;
    my $checkvirus = $par{'CHECKVIRUS'}? 1:0;
    my $checklist = $par{'CHECKLIST'}? 1:0;
    my $blacklist = $par{'BLACKLIST'};
    my $whitelist = $par{'WHITELIST'};

    $blacklist =~ s/\r//g;
    $whitelist =~ s/\r//g;
    # $blacklist =~ /\r/;`echo "$_" >/tmp/xixi`;  测试页面黑名单里的值是否含有'\r'字符
    my @black_arr, @white_arr;
    &read_config_lines( $black_list_file_path, \@black_arr );
    &read_config_lines( $white_list_file_path, \@white_arr );

    if( $pop_enabled eq $read_hash{'POP_ENABLED'} && $checkspam eq $read_hash{'CHECKSPAM'} &&
        $checkvirus eq $read_hash{'CHECKVIRUS'} && $checklist eq $read_hash{'CHECKLIST'} &&
        $blacklist eq join("\n", @black_arr) && $whitelist eq join("\n", @white_arr) ){
        # my $str = join("\n",@black_arr);  if($blacklist eq $str) { `echo aa >/tmp/haha`; }
        # join()里的字符参数'\n'用单引号括起来是解析不到转义符\ , 从而会把\n直接识别成字符'n'！
        return 1;
    }
    return 0;
}


sub save_data(){
    my %read_hash = ();
    my %savehash = ();
    my ( $status, $mesg ) = ( -1, "保存失败" );

    if( &check_repeated() == 1 ) {
        &send_status( -1, 0, "对不起，请不要重复保存相同的配置！" );
        return;
    }
    if ( &is_popscan_running() == 1 ) {
        &send_status( -1, 0, "服务正在重启，请稍后操作" );
        return;
    }

    &readhash( $settings_file_path, \%read_hash );
    %savehash = %read_hash;   #
    if( $par{'POP_ENABLED'} ){
        $savehash{'POP_ENABLED'} = "on";
    }else{
        $savehash{'POP_ENABLED'} = "off";
    }

    if( !$par{'CHECKSPAM'} ){
        $savehash{'CHECKSPAM'} = 0;
    }else{  # $par{'CHECKSPAM'} eq "on"
        $savehash{'CHECKSPAM'} = 1;
    }
    if( !$par{'CHECKVIRUS'} ){
        $savehash{'CHECKVIRUS'} = 0;
    }else{  # $par{'CHECKVIRUS'} eq "on"
        $savehash{'CHECKVIRUS'} = 1;
    }
    if( !$par{'CHECKLIST'} ){
        $savehash{'CHECKLIST'} = 0;
    }else{  # $par{'CHECKLIST'} eq "on"
        $savehash{'CHECKLIST'} = 1;
    }
    &writehash( $settings_file_path, \%savehash );

    my $black = $par{'BLACKLIST'};
    my $white = $par{'WHITELIST'};
    # $blacklist =~ s/\n/\|/g;
    $black =~ s/\r//g;
    $white =~ s/\r//g;
    my @black_arr = split("\n", $black);
    my @white_arr = split("\n", $white);

    &write_config_lines( $black_list_file_path, \@black_arr );
    &write_config_lines( $white_list_file_path, \@white_arr );

    # system("/usr/local/bin/restartpopscan");  这个不自动执行，而是由页面的点击应用按钮再触发执行
    # 在保存数据之后要发送给页面status和running字段表示保存成功以及服务正在开启！
    my %ret_data;

    $ret_data{'status'} = 0;
    $ret_data{'reload'} = 1;
    $ret_data{'mesg'} = "保存成功";
    # $ret_data{'running'} = 1;
    
    # 上面的3句也可以用&send_status(0,1,"保存成功");来代替，不过可读性要差些
    # my $result = $json->encode(\%savehash);
    my $result = $json->encode(\%ret_data);
    print $result;

}



sub load_data(){
    my %ret_data;

    # my @content_array = ();
    # my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );
    # %ret_data->{'detail_data'} = \@content_array;
    my %read_hash = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \%read_hash );
    if(-e $needreload ) {
        %ret_data->{'reload'} = 1;
    }else{
        %ret_data->{'reload'} = 0;
    }
    %ret_data->{'detail_data'} = \%read_hash;
    $ret_data{'running'} = &is_popscan_running();
    system("sudo /usr/local/bin/judge_virus_enable.py -m clamav");
    $ret_data{'virus_enable'} = $? >> 8;
    # $ret_data{'virus_enable'} = 0;  测试用
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
# sub get_detail_data($){
#     my $content_array_ref = shift;
#     my %read_hash = ();
#     &readhash( $settings_file_path, \%read_hash );
#     push( @$content_array_ref, \%read_hash );  
#     你如果要把%read_hash哈希放在数组里那么你的js访问就应该写成response.detail_data[0].CHECKSPAM,response.detail_data[0].CHECKSPAM
#     return( 0, "读取完毕", 0 );
# }
sub get_detail_data($){
    my $read_hash_ref = shift;
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    # &readhash( $settings_file_path, \%read_hash );
    &readhash( $settings_file_path, $read_hash_ref );
    
    my @black_arr, @white_arr;
    &read_config_lines( $black_list_file_path, \@black_arr );
    &read_config_lines( $white_list_file_path, \@white_arr );

    $read_hash_ref->{'BLACKLIST'} = join("\n",@black_arr); # \@black_arr;
    $read_hash_ref->{'WHITELIST'} = join("\n",@white_arr); # \@white_arr;
}


sub send_status_old($$) {
    my ($status, $mesg) = @_;
    if( $status != 0 ){
        $errormessage = $mesg;
    }else{
        $notemessage = $mesg;
    }
}


sub send_status($$$) {
    my ($status, $running, $mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'running'} = $running;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}
