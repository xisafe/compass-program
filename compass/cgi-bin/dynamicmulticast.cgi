#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/11/07
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $settings_file;      #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd_rip;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/multicastrouting/dynamicmulticast';              #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;           #规则所存放的文件夹
    $conf_file          = $conf_dir.'/config';              #发件人信息所存放的文件
    $settings_file      = $conf_dir.'/settings';            #启用信息所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_dynamic';#启用信息所存放的文件
    $cmd_rip = "/usr/local/bin/DynamicMulticast";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/dynamicmulticast_init.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#

    &make_file();#检查要存放规则的文件夹和文件是否存在
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $panel_name = $par{'panel_name'};
    if( !$action ) {
        $action = $query{'ACTION'};
    }

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data' && $panel_name eq 'list_panel') {
        #==下载数据==#
        &load_data();
    } 
    elsif ($action eq 'save_data' && $panel_name eq 'add_panel') {
        #==保存数据==#
        &save_data();
    }
    elsif ($action eq 'switch') {
        #==启用禁用==#
        &switch();
    }
    elsif ($action eq 'save_interface') {
        #==保存接口设置==#
        &save_interface();
        &show_page();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ($action eq 'load_usable_interface') {
        #==获取系统可用接口==#
        &get_useable_interface();
    }
    elsif ($action eq 'delete_data') {
        #==删除数据==#
        &delete_data();
    }
    elsif ($action eq 'enable_data') {
        #==启用规则==#
        &toggle_enable( $par{'id'}, "on" );
    }
    elsif ($action eq 'disable_data') {
        #==禁用规则==#
        &toggle_enable( $par{'id'}, "off" );
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

sub display_list_div() {
    if(-e $settings_file){
       readhash($settings_file, \%settings);
    }
    my $checked = "";
    if($settings{'ENABLED_DYNAMIC'} eq 'on'){
        $checked = "checked = 'checked'";
    }
    printf<<EOF
    <div id="mesg_box_dynamic" style="width: 96%;margin: 20px auto;"></div>
    <div id="enable_box_dynamic" class="toolbar" style="width: 94.5%;margin: 20px auto;padding:10px;">
        <input type="checkbox" $checked value="on" id="enableDYNAMIC" />
        <span>启用动态组播路由</span>
        <button class="imaged-button" onclick="change_switch();">确定</button>
    </div>
EOF
    ;
    openbox('100%', 'left', _('接口设置'));
    printf<<EOF
        <form name="INTERFACE_SETTING_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
        <table cellpadding="0" cellspacing="0" width="100%" border='0' >
        <tr class="odd">
                        <td class="add-div-type">组播接口设置</td>
                        <td>
                            <div style="margin:auto;">
                                <div id="left-div" style="float:left;">
                                    <div style="margin:5px auto;">开启的接口</div>
                                    <div>
                                        <select id="left_select" name="left_select" multiple="multiple" size="8" style="width:200px;">
                                        </select>
                                    </div>
                                </div>
                                <div style="float:left;margin: 45px 30px;">
                                    <div style="margin:5px;">
                                        <input id="add" type="button" value=">>" onclick="add_interface();" class="mvbutton"/>
                                    </div>
                                    <div style="margin:5px;">
                                        <input id="del" type="button" value="<<" onclick="delete_interface();" class="mvbutton"/>
                                    </div>
                                </div>
                                <div id="right-div" style="float:left;">
                                    <div style="margin:5px auto;">关闭的接口</div>
                                    <div><select  id="right_select" name="right_select" multiple="multiple" size="8" style="width:200px;">
                                    </select>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
        <tr class="table-footer">
        <td colspan="2">
          <input type="hidden" class="action" name="ACTION" value="save_interface"></input>
            <input type="submit" class="net_button" value="保存" align="middle"/>
            <!--<input type="reset" class="net_button" value="重置" align="middle"/>-->
        </td>
        </tr>
        </table>
        </form>
EOF
    ;
    &closebox();
    printf<<EOF
    <div id="panel_dynamic_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_dynamic_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}


sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};

    my ( $status, $mesg ) = ( -1, "未保存" );
    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $conf_file, $record );
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
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
            $conf_data{'id'} = $i;
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


sub delete_data() {
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;

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
            $config{'id'} = $i;
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
    $config{'point_rp'}   = $temp[0];
    $config{'multicast_addrgroup'}   = $temp[1];
    $config{'model'}   = $temp[2];
    $config{'interval_CRP'}   = $temp[3];
    $config{'level'}   = $temp[4];
    $config{'enable'}   = $temp[5];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'point_rp'} );
    push( @record_items, $hash_ref->{'multicast_addrgroup'} );
    push( @record_items, $hash_ref->{'model'} );
    push( @record_items, $hash_ref->{'interval_CRP'} );
    push( @record_items, $hash_ref->{'level'} );
    if($hash_ref->{'enable'}){
        push( @record_items, $hash_ref->{'enable'} );
    }else{
        push( @record_items, "off" );
    }
    return join (",", @record_items);
}

sub toggle_enable($$) {
    my $item_id = shift;
    my $enable = shift;

    my ( $status, $mesg, $line_content ) = &get_one_record( $conf_file, $item_id );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, $mesg );
        return;
    }

    my %config = &get_config_hash( $line_content );
    $config{'enable'} = $enable;
    $line_content = &get_config_record(\%config);

    my ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $line_content );
    if( $status != 0 ) {
        $mesg = "操作失败";
    }

    &send_status( $status, $mesg );
    return;
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
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
    
    if(! -e $settings_file){
        system("touch $settings_file");
        `echo >>$settings_file ENABLED_DYNAMIC=off`;
        `echo >>$settings_file DISABLED=`;
    }
}
#获取系统可用接口
sub get_useable_interface(){
    my $green  = `cat /var/efw/ethernet/br0`;
    my $orange = `cat /var/efw/ethernet/br1`;
    my $blue   = `cat /var/efw/ethernet/br2`;
    my @br0s = split(/\n/,$green);
    my @br1s = split(/\n/,$orange);
    my @br2s = split(/\n/,$blue);
    my @ethes = get_eth();
    for (my $i=0;$i<@ethes;$i++){
        foreach(@br0s){
            if($_ eq $ethes[$i]){
                delete ($ethes[$i]);
            }
        }
        foreach(@br1s){
            if($_ eq $ethes[$i]){
                delete ($ethes[$i]);
            }
        }
        foreach(@br2s){
            if($_ eq $ethes[$i]){
                delete ($ethes[$i]);
            }
        }
    }
    if(@br2s > 0){
        unshift(@ethes,'br2');
    }
    if(@br1s > 0){
        unshift(@ethes,'br1');
    }
    if(@br0s > 0){
        unshift(@ethes,'br0');
    }
    my @useable_interfaces = ();
    foreach(@ethes){
        if($_){
            #my $item = "{text:'$_',value:'$_'}";
            push(@useable_interfaces,$_);
        }
    }
    readhash($settings_file, \%settings);
    my @opened_interface = split(",",$settings{'DISABLED'});
    my %hash;
    %hash->{'useable_interfaces'} = \@useable_interfaces;
    %hash->{'opened_interface'} = \@opened_interface;
    my $ret = $json->encode(\%hash);
    print $ret; 
}
#启用禁用
sub switch(){
    readhash($settings_file, \%settings);
    $settings{'ENABLED_DYNAMIC'} = $par{'ENABLED'};
    writehash($settings_file,\%settings);
    my $reload = 1;
    &create_need_reload_tag();
    &send_status( 0, $reload, "操作成功" );
}
sub apply_data() {
    my $result;
    system($cmd_rip);
    $result = $?;
    &clear_need_reload_tag();
    &send_status( 0, 0, "应用成功" );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
#保存接口设置
sub save_interface(){
    readhash($settings_file, \%settings);
    $settings{'DISABLED'} = $par{'right_select'};
    chomp($settings{'DISABLED'});
    $settings{'DISABLED'} =~ s/\|/,/g;
    writehash($settings_file,\%settings);
}