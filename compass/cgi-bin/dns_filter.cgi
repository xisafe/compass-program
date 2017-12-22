#!/usr/bin/perl
#==============================================================================#
# 描述:DNS过滤页面
#
# 作者: 辛志薇
# 公司: capsheaf
# 历史:
#   2015-05-12 创建
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $dns_config_file_path;
my $dns_settings_file_path;
my $dns_src_bypass_file;
my $dns_dst_bypass_file;
my $needreload = '/var/efw/dnsmasq/needreload';
my $restartcmd = '/usr/local/bin/restartdnsmasq';

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
    $dns_config_file_path = '/var/efw/dnsmasq/enabled';
    $dns_settings_file_path = '/var/efw/dnsmasq/settings';
    $dns_src_bypass_file = '/var/efw/dnsmasq/source_bypass';
    $dns_dst_bypass_file = '/var/efw/dnsmasq/destination_bypass';

    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/waiting.js"></script>
                    <script language="JavaScript" src="/include/dns_filter.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#
}

sub make_file(){
    my @files = ($dns_config_file_path,$dns_settings_file_path,$dns_src_bypass_file,$dns_dst_bypass_file);
    foreach my $file( @files ){
        if(! -e $file){
            system("touch $file");
        }
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
    my %ret_data;
    if( $status != 0 ){
        $ret_data{'status'} = -1;
        $ret_data{'mesg'} = "应用失败";
    }else{
        &clear_need_reload_file();
        $ret_data{'status'} = 0;
        $ret_data{'mesg'} = "应用成功";
    }
    my $result = $json->encode(\%ret_data);
    print $result;
}

sub do_action() {
    my $action = $par{'ACTION'};           # 

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if( $action eq 'apply_data' ){
        &apply_data();
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
    &openpage(_('DNS过滤'), 1, $extraheader);
    &openbigbox($errormessage,$warnmessage,$notemessage);
    &closebigbox();
    &display_main_div();
    &closepage();
}

sub display_main_div(){
    printf<<EOF
    <div id="mesg_box_id" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;

    &openbox('100%', 'left', _('配置DNS过滤'));

printf <<EOF
    <form name="DNS_FILTER_FORM" id="form_id_for_dns_filter_panel" action="$ENV{'SCRIPT_NAME'}"
     method="post" onsubmit="return false;">  <!-- 注意如果你想要把表单提交方式改为Ajax的就必须先在form里把form的默认submit动作禁用掉 -->
        <table cellpadding="0" cellspacing="0" width="100%" border='0' >
            <tr class="table-footer">
                <td colspan="2" style="text-align:left;">
                    <input type="checkbox" name="DNS_ENABLED" id="dns_enabled_id"/>
                    <span>启用DNS过滤功能</span>
                </td>
            </tr>
            <tr class="odd">
                <td class="add-div-type" style="width:250px">DNS白名单</td>
                <td>
                    <input type="checkbox" id="whitelist_id" name='WHITELIST' />
                    <span>启用</span>
                </td>
            </tr>
            <tr class="odd"  id="last_tr_id">
                <td class="add-div-type" style="width:250px"></td>
                <td>
                    <div style="width:300px;float:left;" class="whitelist_textarea">
                        <span>设置绕过过滤功能的客户端IP/MAC地址(每行一个)  </span>
                        <textarea id="CLIENT_BYPASS" style="width:270px;height:100px;float:left;" name="CLIENT_BYPASS"></textarea>
                    </div>
                    <div style="width:300px;float:left;" class="whitelist_textarea">
                        <span>设置绕过过滤功能的服务器IP/MAC地址(每行一个)</span>
                        <textarea id="SERVER_BYPASS" style="width:270px;height:100px;" name="SERVER_BYPASS"></textarea>
                    </div>
                    <div style="width:500px;display:block;"><span></span></div>
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

sub save_data(){

    my %read_hash = ();
    my %savehash = ();
    my ( $status, $mesg ) = ( -1, "配置保存失败" );

    &readhash( $dns_config_file_path, \%read_hash );
    %savehash = %read_hash;   #
    if( $par{'DNS_ENABLED'} ){
        $savehash{'ENABLED'} = "on";
    }else{
        $savehash{'ENABLED'} = "off";
    }
    &writehash( $dns_config_file_path, \%savehash );


    %read_hash = (); %savehash = ();
    &readhash( $dns_settings_file_path, \%read_hash );
    %savehash = %read_hash;   #
    if( $par{'WHITELIST'} ){
        $savehash{'TRANSPARENT'} = "on";
    }else{
        $savehash{'TRANSPARENT'} = "off";
    }
    &writehash( $dns_settings_file_path, \%savehash );

    my $client, $server;

    if( $par{'WHITELIST'} ){
        $client = $par{'CLIENT_BYPASS'};
        $server = $par{'SERVER_BYPASS'};
        $client =~ s/\r//g;
        $client =~ s/\-/:/g;
        $server =~ s/\r//g;
        $server =~ s/\-/:/g;
        my @client_arr = split("\n", $client);
        my @server_arr = split("\n", $server);
        &write_config_lines( $dns_src_bypass_file, \@client_arr );
        &write_config_lines( $dns_dst_bypass_file, \@server_arr );
    }

    ( $status, $mesg ) = ( 0, "配置保存成功" );
    my %ret_data;
    $ret_data{'status'} = $status;
    $ret_data{'reload'} = 1;
    # $ret_data{'running'} = 1;
    $ret_data{'mesg'} = $mesg;
    my $result = $json->encode(\%ret_data);
    print $result;

}


sub load_data(){
    my %ret_data;
    my %read_hash = ();
    &get_detail_data( \%read_hash );
    if(-e $needreload ) {
        %ret_data->{'reload'} = 1;
    }else{
        %ret_data->{'reload'} = 0;
    }
    %ret_data->{'detail_data'} = \%read_hash;
    # $ret_data{'running'} = &is_popscan_running();
    my $result = $json->encode(\%ret_data);
    print $result; 

}

sub get_detail_data($){
    my $read_hash_ref = shift;
    my %read_hash;
    &readhash( $dns_config_file_path, \%read_hash );
    $read_hash_ref->{'DNS_ENABLED'} = $read_hash{'ENABLED'};
    &readhash( $dns_settings_file_path, \%read_hash );
    $read_hash_ref->{'WHITELIST'} = $read_hash{'TRANSPARENT'};

    my @client_arr, @server_arr;
    &read_config_lines( $dns_src_bypass_file, \@client_arr );
    &read_config_lines( $dns_dst_bypass_file, \@server_arr );

    $read_hash_ref->{'CLIENT_BYPASS'} = join("\n",@client_arr);
    $read_hash_ref->{'SERVER_BYPASS'} = join("\n",@server_arr);
}

sub send_status($$$){

}

