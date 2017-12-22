#!/usr/bin/perl

use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $conf_file_sender;
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/warn/email_warn';               #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;           #规则所存放的文件夹
    $conf_file          = $conf_dir.'/reciver_config';      #收件人信息所存放的文件
    $conf_file_sender   = $conf_dir.'/sender_settings';     #发件人信息所存放的文件
    $cmd                = "/usr/local/bin/email_warn -t -a ";

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/idps_email_alarm.css" />

                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/idps_email_alarm_init.js"></script>';
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
    elsif ($action eq 'save_sender') {
        #==保存发件人配置==#
        &save_sender();
        &show_page();
    }
    elsif ($action eq 'sending_mail_test') {
        #==测试邮件==#
        &sending_mail_test();
    }
    elsif ($action eq 'delete_data') {
        #==删除数据==#
        &delete_data();
    }
    elsif ($action eq 'enable_data') {
        #==启用规则==#
        &toggle_enable( "on" );
    }
    elsif ($action eq 'disable_data') {
        #==禁用规则==#
        &toggle_enable( "off" );
    }
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_sender_div();
    &display_list_div();
    &closepage();
}

sub display_list_div() {
    printf<<EOF
    <div id="panel_email_mesg" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_email_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_email_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub display_sender_div(){
    openbox('100%', 'left', _('发件人配置'));
    &readhash( $conf_file_sender, \%settings );
    my $cbk_ssl = "";
    my $cbk_auth = "";
    if(($settings{'ENABLED_SSL'}) eq "on"){
        $cbk_ssl = "checked";
    }
    if(($settings{'ENABLED_AUTH'}) eq "on"){
        $cbk_auth = "checked";
    }
    
    printf<<EOF
    <form name="SENDER_SETTING_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="odd">
    <td class="add-div-type">发件人邮箱*</td>
    <td><input type="text" class="send" name='SENDER_EMAILADDRESS' value="$settings{'SENDER_EMAILADDRESS'}"/></td>
    </tr>
    <tr class="odd">
    <td  class="add-div-type">SMTP服务器地址*</td>
    <td><input type="text" class="send" name='SMTPSERVER_ADDR' value="$settings{'SMTPSERVER_ADDR'}"/><span>（IP地址或域名）</span></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">SMTP服务器端口*</td>
    <td><input type="text" class="send" name='SMTPSERVER_PORT' value="$settings{'SMTPSERVER_PORT'}"/></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">使用SSL加密</td>
    <td><input type="checkbox" id="ENCODE_SSL" $cbk_ssl name='ENABLED_SSL' value="on"/><span>启用加密</span></td>
    </tr><hr>
    <tr class="odd">
    <td class="add-div-type" rowspan="3">身份认证</td>
    <td><input type="checkbox" id="AUTH" $cbk_auth name='ENABLED_AUTH' value="on" onclick="changeFormCheck()"/><span>启用身份认证</span></td>
    </tr>
    <tr class="odd">
        <td><span>账户*:&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</span><input type="text" id="ACCOUNT" class="auth" name='USERNAME' value="$settings{'USERNAME'}"/></td>
    </tr>
    <tr class="odd">
        <td><span>密码*:&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</span><input type="password" id="PWD" class="auth" name='PASSWD' value="$settings{'PASSWD'}"/></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">测试发件人配置</td>
    <td><span style="margin-right:5px">邮件接收地址</span><input type="text" class="send" name='TESTED_RECIVER_EMAILADDRESS' value="$settings{'TESTED_RECIVER_EMAILADDRESS'}"/>
        <input type="button" class="net_button" value="发送测试邮件" align="middle" onclick="sending_mail_test()" />
    </td>
    </tr>
    
    <tr class="odd" style="display:none;">
    <td class="add-div-type">邮件告警时间*</td>
    <!--<td><input type="text" class="send" name='TIMING' value="$settings{'TIMING'}"/>分钟</td>-->
    <td><input type="text" class="send" name='TIMING' value="30"/>分钟</td>
    </tr>
    
    <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save_sender"></input>
        <!--<input type="button" class="net_button" value="测试" align="middle" onclick="sending_mail_test()" />-->
        <input type="submit" class="net_button" value="保存" align="middle"/>
    </td>
    </tr>
    </table>
    </form>
EOF
    ;
    &closebox();
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
        #$reload = 1;
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

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}


sub delete_data() {
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'msg'} = $mesg;

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
    $config{'reciever'}   = $temp[0];
    $config{'description'}   = $temp[1];
    $config{'enable'}   = $temp[2];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'reciever'} );
    push( @record_items, $hash_ref->{'description'} );
    if($hash_ref->{'enable'}){
        push( @record_items, $hash_ref->{'enable'} );
    }else{
        push( @record_items, "off" );
    }
    return join ",", @record_items;
}

sub toggle_enable($) {
    my $enable = shift;
    my $operation = "启用";
    if ( $enable ne "on" ) {
        $operation = "禁用";
    }
    my @lines = ();
    my $reload = 0;

    my ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        $mesg = "$operation失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    my %item_id_hash;
    my @item_ids = split( "&", $par{'id'} );
    foreach my $id ( @item_ids ) {
        $item_id_hash{$id} = $id;
    }

    my $len = scalar( @lines );

    for ( my $i = 0; $i < $len; $i++ ) {
        if( $item_id_hash{$i} eq "$i" ) {
            my %config = &get_config_hash( $lines[$i] );
            $config{'enable'} = $enable;
            $lines[$i] = &get_config_record(\%config);
        }
    }

    my ( $status, $mesg ) = &write_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        $mesg = "$operation失败";
    } else {
        $mesg = "$operation成功";
        $reload = 0; # 不应用
    }

    &send_status( $status, $reload, $mesg );
    return;
}

sub send_status($$$) {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status,$reload, $mesg) = @_;
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
    
    if(! -e $conf_file_sender){
        system("touch $conf_file_sender");
    }
}
#邮件测试函数
sub sending_mail_test(){
    # my $len = read_config_lines($conf_file);
    # if(!$len){
        # $len = 0;
    # }
    my $MAIL_BOX_SENDER = $par{'SENDER_EMAILADDRESS'};
    my $ADDR_SMTP = $par{'SMTPSERVER_ADDR'};
    my $PORT_SMTP = $par{'SMTPSERVER_PORT'};
    my $ENCODE_SSL;
    if($par{'ENABLED_SSL'} eq 'on'){
        $ENCODE_SSL = '-e';
    }
    my $AUTH;
    if($par{'ENABLED_AUTH'} eq 'on'){
        $AUTH = '-i';
    }
    my $ACCOUNT = $par{'USERNAME'};
    my $PWD = $par{'PASSWD'};
    my $TESTED_RECIVER = $par{'TESTED_RECIVER_EMAILADDRESS'};
    #system($cmd.'$ADDR_SMTP -p $PORT_SMTP -s $MAIL_BOX_SENDER -e $ENCODE_SSL -i $AUTH -z $ACCOUNT -m $PWD -r $TESTED_RECIVER');
    my $sending_state = `$cmd $ADDR_SMTP -p $PORT_SMTP -s $MAIL_BOX_SENDER $ENCODE_SSL $AUTH -z $ACCOUNT -m $PWD -r $TESTED_RECIVER`;
    my %hash;
    %hash ->{'sending_state'} = $sending_state;
    
    my $result = $json->encode(\%hash);
    print $result;
}

sub save_sender(){
    $settings{'SENDER_EMAILADDRESS'} = $par{'SENDER_EMAILADDRESS'};
    $settings{'SMTPSERVER_ADDR'} = $par{'SMTPSERVER_ADDR'};
    $settings{'SMTPSERVER_PORT'} = $par{'SMTPSERVER_PORT'};
    $settings{'ENABLED_SSL'} = $par{'ENABLED_SSL'};
    $settings{'ENABLED_AUTH'} = $par{'ENABLED_AUTH'};
    $settings{'USERNAME'} = $par{'USERNAME'};
    $settings{'PASSWD'} = $par{'PASSWD'};
    $settings{'TESTED_RECIVER_EMAILADDRESS'} = $par{'TESTED_RECIVER_EMAILADDRESS'};
    $settings{'TIMING'} = $par{'TIMING'};
    &writehash( $conf_file_sender, \%settings );
}