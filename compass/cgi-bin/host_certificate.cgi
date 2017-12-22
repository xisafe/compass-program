#!/usr/bin/perl
#author: ChenSisi
#createDate: 2017/09/04
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $ca_create_cmd = "sudo /usr/local/bin/generate_cert_request.py";

my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $name = 'CA证书';

#审查日志所需变量
my $CUR_PAGE = "公告配置" ;  #当前页面名称，用于记录日志
my $log_oper;                      #当前操作，用于记录日志. 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '0';         #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
my $errormessage,$warnmessage,$notemessage;
my $file;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){

    # $file = '/tmp/name.pem';  #下载证书路径
    $errormessage     = '';
    $notemessage     = '';
    $custom_dir         = '/vpn';              #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;                 #ca证书存放的文件
    $conf_file          = $conf_dir.'/ca/host_config';            #读取CA的配置文件
    $ca_config_file     = $conf_dir.'/req_config';                # 存放CA信息的配置文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_notice';#启用信息所存放的文件
    $cmd                = "sudo /usr/local/bin/restartAAA";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/host_certificate.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par,0,1);
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

    if($action ne 'save_data' && $query_action ne 'save_data' && $query_action ne 'save_data') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data' && $panel_name eq 'list_panel') {
        #==下载数据==#
        &load_data();
    } 
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }    
    elsif ( $action eq 'import_data') {
        &upload_file();
        &show_page();
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
        if ($action eq 'save_data') {
            &save_data();
            my @lines;
            &read_config_lines($ca_config_file, \@lines);
            my $record = $lines[0];
            $record =~ /CN=(.*)/;
            my $name = $1;
            $file = "/tmp/$name.pem";
            # system("echo $file>/var/efw/chensisi.debug");
            $errormessage = &download($file, $name);
            &showhttpheaders();
            &show_page();
        }
        else{
            &show_page();
        }# &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &closebigbox();
    &display_list_div();
    &closepage();
}

sub display_list_div() {
    printf<<EOF
    <div id="mesg_box_notice" style="width: 96%;margin: 20px auto;"></div>
    <div id="create_CA_add_panel_config" style="width:96%; margin:20px auto;"></div>
    <div id="panel_notice_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_notice_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub upload_file(){
    my $cgi = new CGI; 
    my $filename = $cgi->param('file_lib');
    # my $tmp_fp = `mktemp`;
    my $file_path = `mktemp -p /tmp`;
     # system("echo $file_path>>/var/efw/chensisi.debug");

    open ( UPLOADFILE, ">$file_path" ) or $errormessage = "对不起，打开写入上传文件失败！";
    binmode UPLOADFILE;
    while ( <$filename> )
    {
        print UPLOADFILE $_;
    }
    close UPLOADFILE;

    # system("echo $file_path>/var/efw/chensisi.debug");

    my $temp_cmd = "sudo /usr/local/bin/import_host_certification.py -n $filename -f $file_path";

    my $status = `$temp_cmd`;
    if ($status eq '0') {
        $notemessage = "导入成功";
    }
    else {
        $errormessage = "导入失败";
    }
}



sub save_data() {

    my $record = &get_config_record( \%par );

    my @lines = $record;
    &write_config_lines($ca_config_file,\@lines);

    `$ca_create_cmd`;
    # my $status = 0;
    # my $mesg = '操作成功';

    # &send_status( $status, $reload, $mesg );
}

sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );
    
    my $record_num = @lines;
    my $sequence = 1;
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
            $conf_data{'sequence'} = $sequence;
            $sequence++;
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
        %ret_data->{'reload'} = 0;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}


sub delete_data() {
    my $delete_id = $par{'id'};
    my @del_id = split('&', $delete_id);
    my $len = @del_id;
    my @tmp;
    my $del_cmd;
    my $r = join('|', @del_id);
    $del_cmd = "/usr/local/bin/delete_certification.py -t host -i ".'"'.$r.'"';
    my $mesg;
    my $status = `$del_cmd`;
    if ($status eq '0') {
        $mesg = '删除成功';
    }
    else {
        $mesg = '删除失败';
    }

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;
    $log_oper = 'del';

    &send_status($status,0,$mesg);
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
    my $sequence = 1;
    for ( my $i = $from_num; $i < $total_num; $i++ ) {
        my %config = &get_config_hash( $lines[$i] );
        if( $config{'valid'} ) {
            $config{'id'} = $i;
            $config{'sequence'} = $sequence;
            $sequence++;
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
    my @temp = split(/;/, $line_content);
    $config{'idForCA'}               = $temp[0];
    $config{'certificate_name'}      = $temp[1];
    $config{'certificate_type'}      = $temp[2];
    $config{'authorizer'}            = $temp[3];
    $config{'theme'}                 = $temp[4];
    $config{'start_time'}            = $temp[5];
    $config{'end_time'}              = $temp[6];
    #============自定义字段组装-END===========================#
    return %config;
}
sub randstr($) {
    my $len = shift;
    my $str;
    my @W = ('0' .. '9', 'a' .. 'z', 'A' .. 'Z');
    my $i = 0;
    while ($i++ < $len) {
        $str .= $W[rand(@W)];
    }
    return $str;
}
sub  get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();

    my $name = "CN=$hash_ref->{'name'}";
    my $country = "C=$hash_ref->{'country'}";
    my $province = "ST=$hash_ref->{'province'}";
    my $city = "L=$hash_ref->{'city'}";
    my $organization = "O=$hash_ref->{'organization'}";
    my $department = "OU=$hash_ref->{'department'}";
    my $email = "EA=$hash_ref->{'email'}";

    push( @record_items, $name);
    push( @record_items, $country);
    push( @record_items, $province);
    push( @record_items, $city);
    push( @record_items, $organization);
    push( @record_items, $department);
    push( @record_items, $email);

    return join ("\n", @record_items);
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
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
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
    if(! -e $notice_html){
        system("mkdir -p $notice_html");
    }    
    if(! -e $ca_config_file){
        system("touch $ca_config_file");
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
    $log_oper = 'apply';
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
sub getTime{
    #time()函数返回从1970年1月1日起累计秒数
    my $time = shift || time();
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($time);
   
    $mon ++;
    $sec  = ($sec<10)?"0$sec":$sec;#秒数[0,59]
    $min  = ($min<10)?"0$min":$min;#分数[0,59]
    $hour = ($hour<10)?"0$hour":$hour;#小时数[0,23]
    $mday = ($mday<10)?"0$mday":$mday;#这个月的第几天[1,31]
    $mon  = ($mon<10)?"0$mon":$mon;#月数[0,11],要将$mon加1之后，才能符合实际情况。
    #$mon  = ($mon<9)?"0".($mon+1):$mon;#月数[0,11],要将$mon加1之后，才能符合实际情况。
    $year+=1900;#从1900年算起的年数
   
    #$wday从星期六算起，代表是在这周中的第几天[0-6]
    #$yday从一月一日算起，代表是在这年中的第几天[0,364]
    # $isdst只是一个flag
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
             'date'   => $year."-".$mon."-".$mday,
          };
}

sub download(){
    my $file = shift;
    my $log_name = shift;
    my @fileholder = ();
    my $errormessage = '文件不存在';
    if( -e "$file"){            
        if($file =~ /\.gz/){
            my $str = `zcat '$file'`;
            @fileholder = split("\n", $str);
            foreach(@fileholder) {
                $_ .= "\n";
            }
        }else{
            open(DLFILE, "<$file") || Error('open', "$file");
            @fileholder = <DLFILE>;
            close (DLFILE) || Error ('close', "$file");

        }
        print "Content-Type:application/x-download\n";  
        print "Content-Disposition:attachment;filename='$log_name'\n\n";
        print @fileholder;
        exit;
        
    }
    else{
        return $errormessage;
    }
}
