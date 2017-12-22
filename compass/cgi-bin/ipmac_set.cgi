#!/usr/bin/perl
#==============================================================================#
#
# 描述: ipmac绑定配置页面
#
# 作者: 辛志薇
# 公司: capsheaf
# 历史:
#   2015-1-5 创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $base_dir;
# my $sb_learn_dir;  # 两个目录三个文件
my $ipmac_bind_file_path;
my $snmp_settings_file_path;        # settings文件路径
my $sb_config_file_path;   # config  文件路径
my $ipmac_table_file_path;
my $template_file_path;
my $uploading_tag_file;

my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希

my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变

my $errormessage,$warnmessage,$notemessage;
#=========================全部变量定义end=======================================#

&main();

sub main() {

    &getcgihash(\%par);

    &get_query_hash(\%query);
    
    &init_data();
    
    &make_file();
    
    &do_action();

}
sub init_data(){
    $base_dir = '/var/efw/ip-mac/3L-ip-mac';
    $snmp_settings_file_path = $base_dir.'/settings';
    $sb_config_file_path = $base_dir.'/config';
    $template_file_path = '/var/efw/ip-mac/TEMPLATE';
    # $sb_learn_dir = $base_dir.'/ipmac-bind';   #即/var/efw/ip-mac/3L-ip-mac/ipmac-bind/
    $ipmac_bind_file_path = '/var/efw/ip-mac/3L-ip-mac/ipmac_bind';

    $ipmac_table_file_path = '/var/efw/ip-mac/ipmac_table';
    $uploading_tag_file = '/var/efw/ip-mac/uploading_tag_file';
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/ipmac_set.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#
}

sub make_file(){

    if(! -e $base_dir){
        system("mkdir -p $base_dir");
    }
    # if(! -e $sb_learn_dir){
    #     system("mkdir -p $sb_learn_dir");
    # }
    if(! -e $ipmac_bind_file_path){
        system("touch $ipmac_bind_file_path");
    }
    if(! -e $snmp_settings_file_path){
        system("touch $snmp_settings_file_path");
    }
    if(! -e $sb_config_file_path){
        system("touch $sb_config_file_path");
    }
    if(! -e $ipmac_table_file_path){
        system("touch $ipmac_table_file_path");
    }
}

sub restartipmac(){
    system("/usr/local/bin/restartipmac");
    # 执行上面system调用的脚本，脚本执行的状态返回值有 0 和 非0(一般是大于0的整数) 两种，
    # 0代表脚本执行成功退出(程序员在脚本里可以显式的写exit 0也可以不写exit 0，因为系统默认会为执行正确的脚本返回0值); 
    # 非0的话就是这个脚本里开发者必须自己显式地写的错误返回值，有多种错误就对应多种错误值，
    # 比如exit 256, exit 128, exit 64等
}

sub do_action() {
    my $action      = $par{'ACTION'};    # 千万注意par哈希里面装的是post提交过来的数据
    my $panel_name  = $par{'panel_name'};  # 同上

    my $location      = $par{'id'};

    my $query_action = $query{'ACTION'};  # 千万注意query哈希里面装的是get提交过来的数据
    # my $query_panel_name = $query{'panel_name'};  # 同上

    my $status;
    if( $action ne 'export_data' && $query_action ne 'export_data' && $query_action ne 'export_template_file') {
        &showhttpheaders();
    }
    if( $action eq 'load_init_data' ){
        &load_init_data();
    }
    elsif ( $action eq 'IP_MAC_START' ){
        &ip_mac_start();
    }
    elsif ( $action eq 'IP_MAC_CLOSE' ) {
        &ip_mac_close();
    }
    elsif ( $action eq 'CROSS_ON' ) {
        &save_cross_level("on");
    }
    elsif ( $action eq 'CROSS_OFF' ) {
        &save_cross_level("off");
    }
    elsif ( $action eq 'save_data' ) {
        &save_data_branch();
    }
    elsif( $action eq 'check_uploading' ){
        &check_uploading();
    }
    elsif( $action eq 'import_data' ){
        &upload_file();
    }
    elsif( $action eq 'load_snmp_data' ){    # init_snmp_config
        &load_snmp_data();
    }
    elsif ( $action eq 'load_data' ) {
        &load_data_branch();
    }
    elsif ($action eq 'enable_data' ) {
        &toggle_enable("on");
    }
    elsif ($action eq 'disable_data' ) {
        &toggle_enable("off");
    }
    elsif ($action eq 'delete_data') {
        # `echo "$par{'id'}" >/tmp/haha`;
        &delete_data();
    }
    else {
        if( $query{'ACTION'} eq 'export_data' && $query{'panel_name'} eq 'ipmac_list_panel'){
            &handle_ipmac_download_file();
        }elsif( $query{'ACTION'} eq 'export_template_file'){
            &handle_export_templ_file();
        }else {
            &show_page();
        }
    }

}

sub show_page() {
    &openpage(_('IP/MAC绑定设置'), 1, $extraheader);
    printf<<EOF
    <script>
        var status = 0;
        var mesg = '';
EOF
;
        if($errormessage ne ''){
            print "status = -1;  mesg = '$errormessage';";
            # print括起来的语句要用双引号括起来里面的$errormesg变量才会被识别为一个变量而非一个直接字符串！
        }else{
            print "status = 0;  mesg = '$notemessage';";
        }
    printf<<EOF
    </script>
EOF
;
    # &openbigbox($errormessage, $warnmessage, $notemessage);
    # &closebigbox();
    &display_main_body();
    &closepage();
}
sub display_main_body() {  #第一个首先写一个开启整个绑定功能的div
    &show_body();
}

sub show_body(){
    printf<<EOF
    <div id="toggle_switch_panel_config" style="width:96%; margin:20px auto;"></div>
    <div id="message_box_config" style="width:96%; margin:20px auto;"></div>
    <div id="snmp_add_panel_config" style="width:96%; margin:20px auto;"></div>

    <div id="switchboard_add_panel_config"      style="width:96%; margin:20px auto;"></div>
    <div id="switchboard_list_panel_config"      style="width:96%; margin:20px auto;"></div>

    <div id="ipmac_add_panel_config"      style="width:96%; margin:20px auto;"></div>
    <div id="ipmac_batch_import_panel_config" style="width:96%; margin:20px auto;"></div>
    <div id="ipmac_list_panel_config"      style="width:96%; margin:20px auto;"></div>
EOF
    ;
}
sub ip_mac_start(){
    my %read_hash = ();
    if(-e $snmp_settings_file_path){
        &readhash( $snmp_settings_file_path, \%read_hash );
    }
    my ( $status, $mesg ) = (-1, "开启失败");
    my %save_hash = %read_hash;
    if( $read_hash{'BIND'} eq 'disable'){  # 只有在后台状态为‘关闭’时才允许执行开启脚本！
        # 而你如果不判断的话很可能用户已经开启了一次后再点击若干次开启，这样就会导致多个开启脚本同时在执行！！这是很危险的！
        $save_hash{'BIND'} = 'enable';
        &writehash( $snmp_settings_file_path, \%save_hash );
        &restartipmac();  # 调用脚本重启
        if( $? == 0 ){
            $status = 0;  $mesg = "开启成功";
        }else {
            $mesg .= " 错误码:". $?>>8;  # 记住在$?的值为非0时必须要右移8位才是错误返回值，
            # 为0的时候可以不写右移8位，因为0右移了8位值还是0
        }
    }
    &send_status( $status, $mesg );
}

sub ip_mac_close(){
    my %read_hash = ();
    if(-e $snmp_settings_file_path){
        &readhash( $snmp_settings_file_path, \%read_hash );
    }
    my ( $status, $mesg ) = (-1, "关闭失败");
    my %save_hash = %read_hash;
    if( $read_hash{'BIND'} eq 'enable'){  # 只有在后台状态为‘开启’时才允许执行关闭脚本！
        # 而你如果不判断的话很可能用户已经关闭了一次后再点击若干次关闭，这样就会导致多个关闭脚本同时在执行！！这是很危险的！
        $save_hash{'BIND'} = 'disable';
        &writehash( $snmp_settings_file_path, \%save_hash );
        &restartipmac();  # 调用脚本重启
        if( $? == 0 ){
            $status = 0;  $mesg = "已关闭";
        } else {
            $mesg .= " 错误码:". $?>>8;  # 记住在$?的值为非0时必须要右移8位才是错误返回值，
            # 为0的时候可以不写右移8位，因为0右移了8位值还是0
        }
    }
    &send_status( $status, $mesg );
}


sub save_cross_level($){
    my $value = shift;
    my %read_hash = ();
    &readhash( $snmp_settings_file_path, \%read_hash );
    my %save_hash = %read_hash;
    $save_hash{'CROSS'} = $value;
    &writehash( $snmp_settings_file_path, \%save_hash );
    &restartipmac();  # 调用脚本重启
    if( $? == 0 ){
        $status = 0;  $mesg = "已关闭";
    } else {
        $status = -1;  $mesg .= " 错误码:". $?>>8;
    }
    &send_status( $status, $mesg );
}

sub save_data_branch(){
    if( $par{'panel_name'} eq "snmp_add_panel" ){
        &save_snmp_data();
    }
    elsif( $par{'panel_name'} eq "switchboard_add_panel" ){
        &save_switchboard_data();
    }
    elsif( $par{'panel_name'} eq "ipmac_add_panel" ){
        &save_ipmac_data();
    }
}

sub load_data_branch(){
    if ( $par{'panel_name'} eq "switchboard_list_panel" ) {
        &load_data("switchboard");
    }
    elsif ( $par{'panel_name'} eq "ipmac_list_panel" ) {
        &load_data("ipmac");
    }
}

sub check_uploading(){
    my %response;
    $response{'running'} = &is_file_uploading();
    my $result = $json->encode(\%response);
    print $result;
}

sub is_file_uploading() {
    my $result = -1;
    if( -e $uploading_tag_file ){
        $result = 1;
    }
    return $result;
}

sub upload_file(){
    my ( $status, $mesg ) = &handle_ipmac_upload_file();
    # &send_status($status, $mesg);
    if( $status != 0 ) {
        $errormessage = $mesg;
    }else{
        $notemessage = $mesg;
        &restartipmac();  # 调用脚本重启,前提是文件成功导入了哦
    }
    &show_page();
}


sub handle_ipmac_upload_file(){     # 切记这个函数里捕获到错误状态和错误信息一定要用return返回，你之前写的都是{send_status(-1,"字段个数不正确"); return; }，那是大错特错的!!!
    my $cgi = new CGI;
    if( ! $cgi->param('upload_file') ){  #
        return(-1, "对不起，您没有上传文件！");
    }
    my $file_holder = $cgi->param('upload_file');   #
    my $file_path = $ipmac_table_file_path;   #
    my @fileholder = <$file_holder>;
    my $flag = 0;  my $mesg = "";

    open ( UPLOADFILE, ">>$file_path" ) or return(-1 ,"对不起，批量导入失败！");
    # binmode UPLOADFILE;
    # 开始检查上传文件的格式和内容是否合法！
    foreach( @fileholder ){
        if( $_ eq "\r\n" or $_ =~ /^#/ ){   # 这里是空行和若干以#号开头的行的情况，直接跳过即过滤掉这些行，不要报错
            # if($_ eq "\r\n") {`echo 1 >>/tmp/dd`;} 空行测试成功
            next;
        }else{
            if( $_ !~ /\r\n$/ ){  # 如果用户忘记在最后一行末尾处按下回车键那么自动为其加上，否则就会导致一个bug
                $_ = $_."\r\n";
            }
            my @temp = split(/,/, $_);
            if( @temp != 5 ){  return(-1, "对不起，字段的个数必须为5个，请检查并修改后重新上传");   }
            if($temp[0] ne "on" && $temp[0] ne "off"){  return(-1, "第1个字段值必须是on或off，请您修改后重新上传");   }
            if( 0 == &validip($temp[1]) ){  return(-1, "第2个字段必须是ip类型，请您修改后重新上传");   }
            if( 0 == &validmac($temp[2]) ){  return(-1, "第3个字段必须是mac类型，请您修改后重新上传");   }
        }
    }
    system("touch $uploading_tag_file");
    foreach( @fileholder ){
        # $_ =~ s/\r\n/\n/;
        $_ =~ s/\n\r//g;
        $_ =~ s/\r//;  # 此句非常重要！！即要把每行中所有的\r替换为空(经测试每行中好像有两个\r所以必须要用全局替换/g (后注：一行中出现两个\r是自己造成的一个bug，已修复) )
        $_ = encode("utf8",decode("gb2312",$_)); #  这个还是不能要！！否则上传上去时中文就是乱码！虽然查看ipmac_table文件的编码确实转为UTF-8了
        my @temp = split(/,/, $_);
        if( !validip($temp[3]) ){ $temp[3] = "手动增加"; }
        my $copy = join( ",", @temp ); # my $copy = $_;   #
        $flag = 0;       # flag要重置为0，否则很有可能是上次$flag = 1的状态
        if( $_ eq "\n" or $_ =~ /^#/ ){   # 这里就是空行的情况，空行不能上传，否则显示在页面上就是多个空白行，很不好
            next;
        }elsif( &validip($temp[3]) ){
            my $fpath = $ipmac_bind_file_path;
            open(FILE_HOLDER, "<$fpath");
            while( <FILE_HOLDER> ){
                my @array = split( /,/, $_ );   # 切记这里的$_和外层的$_不一样！
                $_ = "$array[1],$array[2],$array[3]";    # 记住你在这里把$_更改了，那么到了外一层里你就不能再使用它了，要小心
                if( $_ =~ /$temp[1],$temp[2],$temp[3]/ )  {  $flag = 1;  }
            }
            close(FILE_HOLDER);
            if( $flag == 0 ){
                # $copy里要去除掉交换机ip值的那个字段
                # 切记要把$temp[4]里的换行符去除掉否则函数会自动给它添加一个换行字符导致$fpath文件里会多出一个空行
                    # $temp[4] =~ s/\r//;
                    # $temp[4] =~ s/\n//;
                    # &append_one_record( $fpath , $copy );   记住append()方法向文件里添加多行会导致多出一行，所以用文件句柄方式最可靠
                open( SB_UPLOADFILE, ">>$fpath" ) or return(-1 ,"对不起，批量导入失败！");
                print SB_UPLOADFILE $copy;
            }
        }else{
            open(FILE_HOLDER, "<$file_path");
            while( <FILE_HOLDER> ){
                my @array = split( /,/, $_ );
                $_ = "$array[1],$array[2],$array[3]";
                if( $_=~ /$temp[1],$temp[2],$temp[3]/ )  {  $flag = 1;  }
            }
            close(FILE_HOLDER);
            if($flag == 0){
                print UPLOADFILE $copy;   # 这里用的就是文件句柄的方式！所以导入的行全都是报文学习的行时没有出现多出一行的问题！
            }
        }
    }
    close UPLOADFILE;
    system("rm $uploading_tag_file");
    return( 0, "文件已上传成功!".$mesg );
}
sub get_current_time{
    $_ = shift;
    my $t = shift;
    (!$t) and ($t = time);
    my ($sec,$min,$hour,$mday,$mon,$year) = localtime($t);
    $year += 1900;
    my $yy = substr $year,2,2;
    $mon++;
    s/yyyy/$year/gi;
    s/yy/$yy/gi;
    if ($mon < 10)  { s/mm/0$mon/gi;  } else { s/mm/$mon/gi; }
    if ($mday < 10) { s/dd/0$mday/gi; } else { s/dd/$mday/gi; }
    if ($hour < 10) { s/hh/0$hour/gi; } else { s/hh/$hour/gi; }
    if ($min < 10)  { s/mi/0$min/gi;  } else { s/mi/$min/gi; }
    if ($sec < 10)  { s/ss/0$sec/gi;  } else { s/ss/$sec/gi; }
 
    $_;
}
sub handle_ipmac_download_file(){
    # 你要把从交换机学习的条目和其他来源的条目合并到一个文件里并导出
    my $status = 0;

    open( DOWNLOADFILE, "<$ipmac_table_file_path" ) or $status = -1;
    my @fileholder = <DOWNLOADFILE>;
    close ( DOWNLOADFILE );

    my $time = &get_current_time("yyyy-mm-dd hh:mi:ss");
    # my $export_filename = "BAND-TABLE-".$time.".CSV";  把下载的文件的后缀改为txt，因为后缀为CSV的文件下载后打开里面的中文都是乱码
    my $export_filename = "BAND-TABLE-".$time.".txt";

    my $filename = $export_filename;
    # my @lines = ();
    # &read_config_lines($ipmac_bind_file_path,\@lines);
    # push( @fileholder, @lines );   切记这个方法会导致下载的文件里的行之间没有换行符而是完全连起来了！
    open( DOWNLOADFILE, "<$ipmac_bind_file_path" ) or $status = -1;
    push( @fileholder, <DOWNLOADFILE> );
    close (DOWNLOADFILE);

    foreach( @fileholder ){
        $_ =~ s/\n/\r\n/;    # 此句不能删，否则下载的配置行之间还是只有'LF'而不是'CRLF'即无法换行
        # 可是怪异的是若下载模板文件时执行此句却是严重错误的！会出bug
        $_ = encode("gb2312",decode("utf8",$_)); #
        push(@lines,$_);
    }
    if( $status == 0) {
        print "Content-Type:application/x-download\n";
        print "Content-Disposition:attachment;filename=$filename\n\n";
        print @lines;
    }else {
        &showhttpheaders();
        $errormessage = "文件不存在，读取导出内容失败";
        &show_page();
    }
}
sub handle_export_templ_file(){
    my $status = 0;
    my @fileholder;
    my @lines;
    open( DOWNLOADFILE, "<$template_file_path" ) or $status = -1;
    push( @fileholder, <DOWNLOADFILE> );
    close (DOWNLOADFILE);

    foreach( @fileholder ){
        # $_ =~ s/\n/\r\n/;  # bug修复：此句会导致下载下来的模板文件每行的末尾字符为'\r\r\n'即'CRCRLF'
        $_ = encode("gb2312",decode("utf8",$_)); #
        push(@lines,$_);
    }
    if( $status == 0) {
        print "Content-Type:application/x-download\n";
        print "Content-Disposition:attachment;filename=TEMPLATE.txt\n\n";
        print @lines;
    }else {
        &showhttpheaders();
        $errormessage = "文件不存在，读取导出内容失败";
        &show_page();
    }
}
sub toggle_enable($) {   # 2*2=4 此一个函数便可以处理4种情形下的启用禁用动作啦
    my $enable_str = shift;
    my @lines = ();
    my ( $status, $mesg ) = (-1, "未操作");

    my $config_file_path;
    my $position;
    if( $par{'id'} =~ /(.+):(.+)/) {  # id里有下划线_说明这是来自ipMac列表里的行
        # `echo "$1" >/tmp/xin_file`;   # 'ipmac_table_file'
        # `echo "$2" >>/tmp/xin_file`;  # '4'
        $position = $2;   # 把$2的值保存到$position里，不然它出了这个if块域就消失无效了！
        if( "$1" eq "ipmac_table_file" ){
            $config_file_path = $ipmac_table_file_path;
        }
        elsif( "$1" eq "ipmac_bind_file" ){
            # $config_file_path = $sb_learn_dir.'/'."$1";
            $config_file_path = $ipmac_bind_file_path;
        }
    }else{
        $config_file_path = $sb_config_file_path;
    }

    ( $status, $mesg ) = &read_config_lines( $config_file_path, \@lines );
    if( $position ne ''){  # $position的值就是$2的值哦

        for ( my $i = 0; $i < @lines; $i++ ) {
            if( "$position" eq "$i" ) {   # "$2" eq "$i"
                my @arr = split(/,/, $lines[$i]);
                $arr[0] = $enable_str;
                $lines[$i] = join ",", @arr;
                if ($arr[4] eq '') {
                    $lines[$i] .= ',';
                }
            }
        }
    }else{
        for ( my $i = 0; $i < @lines; $i++ ) {
            if( $par{'id'} eq "$i" ) {
                my @arr = split(/,/, $lines[$i]);
                $arr[0] = $enable_str;
                $lines[$i] = join ",", @arr;
            }
        }
    }
    ( $status, $mesg ) = &write_config_lines( $config_file_path, \@lines );
    if( $status != 0 ){
        if($enable_str eq "on")     {  $mesg = "启用失败";  }
        elsif($enable_str eq "off") {  $mesg = "禁用失败";  }
        &send_status( $status, $mesg );
        return;
    }else{
        &restartipmac();  # 调用脚本重启,前提是操作成功哦
        if($enable_str eq "on")     {  $mesg = "启用成功";  }
        elsif($enable_str eq "off") {  $mesg = "禁用成功";  }
        &send_status( $status, $mesg );
    }
}

sub get_sb_config_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;

    my @temp = split(/,/, $line_content);
    # $config{'enabled'}       = $temp[0];
    $config{'enable'} = $temp[0];
    $config{'ip_address'}    = $temp[1];
    $config{'read_community'}    = $temp[2];
    return %config;
}

sub get_sb_config_record($) {
    my $hash_ref = shift;        # 因为实参就是\%par,所以 $hash_ref == \%par
    my @record_items = ();
    if( !$hash_ref->{'enable'} ){
        push( @record_items, "off" );   # 记住第一个字段填写的是启用禁用！
    }else{
        push( @record_items, "on" );
    }
    push( @record_items, $hash_ref->{'ip_address'} );
    push( @record_items, $hash_ref->{'read_community'} );

    return join ",", @record_items;
}


sub get_ipmac_config_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    my $type;

    my @temp = split(/,/, $line_content);
    # $config{'enabled'}      = $temp[0];
    $config{'enable'} = $temp[0];
    $config{'IP_ADDR'}      = $temp[1];
    $config{'MAC_ADDR'}     = $temp[2];

    $type = $temp[3];
    if( $type eq '1' )     {  $config{'IPMAC_SOURCE'} = "手动增加";  }
    else{  $config{'IPMAC_SOURCE'} = $type;  }
    $config{'ipmac_note'}   = $temp[4];
    
    return %config;
}

sub get_ipmac_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    my $line_id;
    my ( $status, $mesg, $record );
    my ( $ip_addr, $mac_addr, $source );
    my @temp;

    if( $hash_ref->{'id'} eq ''){
        if( !$hash_ref->{'enable'} ){
            push( @record_items, "off" );
        }else{
            push( @record_items, "on" );
        }
        push( @record_items, $hash_ref->{'IP_ADDR'} );
        push( @record_items, $hash_ref->{'MAC_ADDR'} );
        push( @record_items, "手动增加" );
        # if( $hash_ref->{'id'} eq ''){
        #     push( @record_items, "1" );     # "手动增加"
        # }else{
        #     push( @record_items, $hash_ref->{'IPMAC_SOURCE'} );
        # }
        push( @record_items, $hash_ref->{'ipmac_note'} );
    }else{
        $hash_ref->{'id'} =~ /(.+):(.+)/;
        if( "$1" eq "ipmac_table_file" ){
            $line_id = $2;
            ( $status, $mesg, $record ) = &get_one_record( $ipmac_table_file_path, $line_id );
            @temp = split(/,/, $record );
            ( $ip_addr, $mac_addr, $source ) = ( $temp[1], $temp[2], $temp[3] );
        }elsif( "$1" eq "ipmac_bind_file" ){
            $line_id = $2;
            ( $status, $mesg, $record ) = &get_one_record( $ipmac_bind_file_path, $line_id );
            @temp = split(/,/, $record );
            ( $ip_addr, $mac_addr, $source ) = ( $temp[1], $temp[2], $temp[3] );
        }
        if( !$hash_ref->{'enable'} ){
            push( @record_items, "off" );
        }else{
            push( @record_items, "on" );
        }
        push( @record_items, ( $ip_addr, $mac_addr, $source ) );
        push( @record_items, $hash_ref->{'ipmac_note'} );

    }
    return join ",", @record_items;
}

sub save_snmp_data() {
    my $reload = 0;
    my %read_hash = ();
    my %savehash = ();

    if (-e $snmp_settings_file_path) {
       &readhash( $snmp_settings_file_path, \%read_hash );
    }

    %savehash = %read_hash;   # 注意要把savehash初始化为上次保存的内容，即这里的保存是在文件原来内容的基础上添加，而不是清空重写，否则你会丢失掉'BIND=enable'和'LAYER=two'！！
    $savehash{'SNMP_TIMEOUT'}  = $par{'timeout_limit'};
    $savehash{'SNMP_INTERVAL'} = $par{'time_interval'};
    $savehash{'VERSION'}       = $par{'version'};
    my ( $status, $mesg ) = ( -1, "未保存" );
    &writehash( $snmp_settings_file_path, \%savehash );  # writehash函数是header.pl里实现的，其他的头文件里查了，没有

    $status = 0;
    if( $status == 0 ) {
        $mesg = "SNMP配置保存成功";
        &restartipmac();  # 调用脚本重启,前提是操作成功了哦
    }
    &send_status( $status, $mesg );
}
sub save_switchboard_data(){
    # my $reload = 0;
    if( 0 == &validip($par{'ip_address'}) )   { &send_status(-1,"对不起，您输入的IP地址不合法");  return;  }
    
    my $record = &get_sb_config_record( \%par );

    my $item_id = $par{'id'};

    my ( $status, $mesg ) = ( -1, "未保存" );
    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $sb_config_file_path, $record );
    } else {
        ( $status, $mesg ) = &update_one_record( $sb_config_file_path, $item_id, $record );
    }
    if( $status == 0 && $item_id eq '' ) {
        $mesg = "交换机配置保存成功";  # $reload = 1;
        &restartipmac();  # 调用脚本重启,前提是操作成功了哦
    }
    if( $status == 0 && $item_id ne '' ) {
        $mesg = "交换机配置编辑成功";
        &restartipmac();  # 调用脚本重启,前提是操作成功了哦
    }

    &send_status( $status, $mesg );
}
sub save_ipmac_data(){
    if( $par{'id'} eq '' ){
        if( 0 == &validip($par{'IP_ADDR'}) )   { &send_status(-1,"对不起，您输入的IP地址不合法");  return;  }
        if( 0 == &validmac($par{'MAC_ADDR'}) )   { &send_status(-1,"对不起，您输入的MAC地址不合法");  return;  }
    }
    $par{'MAC_ADDR'} =~ s/\-/\:/g;
    my $record = &get_ipmac_config_record( \%par );

    my $item_id = $par{'id'};
    my $flag = 0;
    my ( $status, $mesg ) = ( -1, "操作失败" );
    if( $item_id eq '' ) {
        # 下面开始查重
        open(FILE_HOLDER, "<$ipmac_table_file_path");
        @file_holder = <FILE_HOLDER>;
        close(FILE_HOLDER);
        foreach( @file_holder ){
            my @array = split( /,/, $_ );
            $_ = "$array[1],$array[2],$array[3]";
            $add = "$par{'IP_ADDR'},$par{'MAC_ADDR'},1";   # "$par{'IP_ADDR'},$par{'MAC_ADDR'},来自手动增加！";
            if( $_=~ /$add/ )  {  $flag = 1;  }
        }
        # 查重结束
        if($flag == 0){
            ( $status, $mesg ) = &append_one_record( $ipmac_table_file_path, $record );
        }else{
            # $mesg = "$mesg"."\n来自手动添加的$par{'IP_ADDR'},$par{'MAC_ADDR'}发生重复，已被过滤掉\n";
        }
    } else {  # 这时就是编辑的情况
        my $line_id;
        if( $item_id =~ /(.+):(.+)/ ){   # 非贪婪模式(.+?)要慎用！id里有：说明这是来自ipMac列表里的行
            if( "$1" eq "ipmac_table_file" ){
                $line_id = $2;
                ( $status, $mesg ) = &update_one_record( $ipmac_table_file_path, $line_id, $record );
            }elsif( "$1" eq "ipmac_bind_file" ){
                $line_id = $2;
                ( $status, $mesg ) = &update_one_record( $ipmac_bind_file_path, $line_id, $record );
            }
        }
    }
    # &send_status( 0, "新增已完成".$mesg  );
    if( $status == 0 && $item_id eq '' ){ $mesg = "添加成功"; &restartipmac();  }
    if( $status == 0 && $item_id ne '' ){ $mesg = "编辑成功"; &restartipmac();  }
    &send_status( $status, $mesg );
}
sub load_init_data(){
    my %read_hash = ();
    my %ret_data;
    my $status;
    if(-e $snmp_settings_file_path){
        &readhash( $snmp_settings_file_path, \%read_hash );
    }
    $status = $read_hash{'BIND'};
    if($status eq 'enable'){
        %ret_data->{'status'} = "on";
    }else{
        %ret_data->{'status'} = "off";
    }
    %ret_data->{'cross'} = $read_hash{'CROSS'};
    my $ret = $json->encode(\%ret_data);
    print $ret;

}

sub load_snmp_data(){
    my %read_hash = ();
    my %ret_data;
    if (-e $snmp_settings_file_path) {
       &readhash( $snmp_settings_file_path, \%read_hash );
    }
    else{       # 这里就是文件不存在，读取失败
    }
    %ret_data->{'snmp_hash'} = \%read_hash;
    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_data($){
    my $type = shift;
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( $type, \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
sub get_detail_data($$) {
    my $type = shift;
    my $content_array_ref = shift;

    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;
    my $search = $par{'search'};
    
    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        # 读交换机配置文件
        if( $type eq "switchboard" ){
            ( $status, $mesg, $total_num ) = &read_config_lines( $sb_config_file_path, \@lines);
            for( my $i = 0; $i < @lines; $i++ ) {
                my $id = $from_num + $i;
                if( !$LOAD_ONE_PAGE ) {
                    $id = $i;
                }
                my %hash = ();
                %hash = &get_sb_config_hash( $lines[$i] );
                $hash{'id'} = $id;
                push( @$content_array_ref, \%hash );
            }
        }
        # 读ipmac_table配置文件
        elsif( $type eq "ipmac" ){
            ( $status, $mesg, $total_num ) = &read_config_lines( $ipmac_table_file_path, \@lines);
            for( my $i = 0; $i < @lines; $i++ ) {
                my $id = $from_num + $i;
                if( !$LOAD_ONE_PAGE ) {
                    $id = $i;
                }
                my %hash = ();
                %hash = &get_ipmac_config_hash( $lines[$i] );
                $hash{'id'} = "ipmac_table_file".":".$id;

                if ( $search ne "" ) {
                    if ( !( $hash{'IP_ADDR'} =~ m/$search/ ) ) {
                            $total_num--;
                            next;
                    }else{
                        push( @$content_array_ref, \%hash );
                    }
                }else {
                    push( @$content_array_ref, \%hash );
                }

                # push( @$content_array_ref, \%hash );
            }
            # 读取存放交换机ip-mac条目的配置文件里的所有行
            @lines = ();
            &read_config_lines( $ipmac_bind_file_path, \@lines);
            $total_num += @lines;
            for( my $i = 0; $i < @lines; $i++ ) {
                my $id = $from_num + $i;
                if( !$LOAD_ONE_PAGE ) {
                    $id = $i;
                }
                my %hash = ();
                %hash = &get_ipmac_config_hash( $lines[$i] );
                $hash{'id'} = "ipmac_bind_file".":".$id;

                if ( $search ne "" ) {
                    if ( !( $hash{'IP_ADDR'} =~ m/$search/ ) ) {
                            $total_num--;
                            next;
                    }else{
                        push( @$content_array_ref, \%hash );
                    }
                }else {
                    push( @$content_array_ref, \%hash );
                }
                # push( @$content_array_ref, \%hash );
            }
        }
    } else {
        # 只加载一页的时候哦
    }
    return ( $status, $mesg, $total_num );
}

sub handle_before_save_data(){

}

sub delete_data() {
    # my $file_path = shift;
    my ( $status, $mesg ) = (-1, "");
    my @ipmac_ids, @sb_learn_ids, @sb_conf_ids;
    my $sb_fname = "";
    my @ids = split( "&", $par{'id'} );

    my %name_hash;
    my @hash_arr;
    my %id_hash;
    my ( $key, $value );
    
    foreach my $id_item( @ids ){
        if( $id_item =~ /(.+):(.+)/ ){   # 非贪婪模式(.+?)要慎用！id里有：说明这是来自ipMac列表里的行
            if( "$1" eq "ipmac_table_file" ){
                push( @ipmac_ids, $2 );
            }elsif( "$1" eq "ipmac_bind_file" ){
                # $sb_fname = $1;
                push( @sb_learn_ids, $2 );
            }
        }else{
            push( @sb_conf_ids, $id_item );
        }
    }

    if( scalar(@ipmac_ids) != 0 ){
        ( $status, $mesg ) = &delete_several_records( $ipmac_table_file_path, join("&",@ipmac_ids) );
        if( $status !=0 ){ $mesg = "删除选中的行失败"; &send_status( $status, $mesg ); return; }
    }
    if( scalar(@sb_learn_ids) != 0 ){
        ( $status, $mesg ) = &delete_several_records( $ipmac_bind_file_path, join("&",@sb_learn_ids) );
        if( $status !=0 ){ $mesg = "删除选中的行失败"; &send_status( $status, $mesg ); return; }
    }
    if( scalar(@sb_conf_ids) != 0 ){
        ( $status, $mesg ) = &delete_several_records( $sb_config_file_path, join("&",@sb_conf_ids) );
        if( $status !=0 ){ $mesg = "删除选中的行失败"; &send_status( $status, $mesg ); return; }
    }
    if($status == 0){  $mesg = "删除成功";  &restartipmac();  &send_status( $status, $mesg );  }
    
}
sub send_status($$) {
    my ( $status, $mesg ) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}