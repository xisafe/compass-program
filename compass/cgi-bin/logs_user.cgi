#!/usr/bin/perl
#==============================================================================#
#
# 描述: 添加规则列表规则页面
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.09.23 WangLin创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'logs_common.pl';

#=================初始化全局变量到init_data()中去初始化========================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my $log_name = "用户登录/注销";
my $errormessage    = '';
my $notemessage     = '';
#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post请求传过来的变量
    &getcgihash(\%par);
    #获取get请求传过来的变量
    &get_query_hash(\%query);
    #初始化变量值
    &init_data();
    # &make_file();
    #做出响应
    &do_action();
}

sub init_data(){

    $errormessage       = '';
    $notemessage        = '';
    $cmd                = '/usr/local/bin/filter_log.py';
    $logs               = 'logs_event';
    $logs_event         ='/var/log/userlogin';
    $logname          ="userlogin";
    $sid_info           = '/usr/local/bin/get_sid_info.py';

    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/all_log.css" />
                    <link rel="stylesheet" type="text/css" href="/include/jquery-ui.min.css" />
                    <script language="JavaScript" src="/include/jquery-3.1.0.min.js"></script>
                    <script language="JavaScript" src="/include/jquery-ui.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script type="text/javascript" src="/include/jsencrypt.min.js"></script>
                    <script type="text/javascript" src="/include/logs_delete.js"></script>
                    <script type="text/javascript" src="/include/ESONCalendar.js"></script>
                    <script type="text/javascript" src="/include/jquery.md5.js"></script>
                    <link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />
                    <script language="JavaScript" src="/include/logs_user.js"></script>';
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-END==============================#
}

sub do_action() {
    #==一般ACTION只会通过一种方式传过来，开发者需要自己判断从哪种方式传过来==#
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};

    if($action ne 'download' && $query_action ne 'download' && $query_action ne 'download') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#

    if ( $action eq 'load_data' && $panel_name eq 'list_panel' ) {
        &load_data();
    }
    elsif ( $action eq 'search'   ) {
        &load_data();
    }
    elsif( $action eq 'query_suggestion' ) {
        &query_suggestion();
    }
    elsif ( $action eq 'importLog') {
        ($errormessage,$notemessage) = &importLog(\%par,'userlogin');
        &show_page();
    }       
    elsif ( $action eq 'delete') {
        &deleteLog();
    }    
    elsif ( $action eq 'clearLog') {
        &clearLogForPass();
    }    
    else {
        if ($action eq 'download') {
            $errormessage = &download($par{'export_log'});
            &showhttpheaders();
            &show_page();
        }
        else {
            &show_page();
        }
    }
}

sub dateToFilestring($) {
    my $date = shift;
    $date =~ s/\-//g;
    return $date;
}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_main_body();
    &closepage();
}

sub display_main_body() {
    
    printf<<EOF
    
    <div id="mesg_box" class="container"></div>
    <div id="add_panel" class="container"></div>
    <div id="list_panel" class="container"></div>
    <div id="importLog_panel" class="container"></div>
    <input type="hidden" id="log-mesg-error" value="$errormesg">
    <input type="hidden" id="log-mesg-note" value="$notemessage">   
    
EOF
    ;
}

sub load_data(){
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub download($) {
    my $select_date = shift;
    my $today = &getDate(time);
    if ($select_date eq '') {
        $select_date = $today;
    }
    my $filestr = $logs_event;
    if ($select_date ne $today) {
        $filestr="${logs_event}-".dateToFilestring($select_date).".gz";
    }
    &down_file($filestr,$par{'ACTION'},$select_date,$log_name);

}
sub deleteLog(){
    my %ret_data;
    my $select_date = $par{'searchTime'};
    my $today = &getDate(time);
    if ($select_date eq '') {
        $select_date = $today;
    }
    my $filestr = $logname;
    if ($select_date ne $today) {
        $filestr="${logname}-".dateToFilestring($select_date).".gz";
    }
    %ret_data->{'filestr'} = 'delete='.$filestr;
    my $ret = $json->encode(\%ret_data);
    print $ret;
}
sub clearLogForPass(){
    my %ret_data;
    my $filestr = 'clear='.'userlogin';
    %ret_data->{'filestr'} = $filestr;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub get_detail_data($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;
    my $search =  $par{'search'} ;
    my $note = $par{'note'};

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $logs_event, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records( $logs_event, $page_size, $current_page, \@lines );
    }
    @lines = reverse @lines;
    $total_num = 0; #重新初始化总数
    for( my $i = 0; $i < @lines; $i++ ) {
        my $id = $from_num + $i;
        if( !$LOAD_ONE_PAGE ) {
            $id = $i;
        }
        my %hash = &get_config_hash( $lines[$i] );

        if ( !$hash{'valid'} ) {
            next;
        }

        #===实现查询===#
        if ( $search ne "" ) {
            my $datetime = lc $hash{'datetime'};
            if ( !($datetime =~ m/$search/)  ) {
                #===对名字，说明进行搜索===#
                next;
            }
        }

        if ( $note ne "" ) {
            my $messages = lc $hash{'user_description'};
            if ( !($messages =~ m/$note/)  ) {
                #===对名字，说明进行搜索===#
                next;
            }
        }

        $hash{'id'} = $id; #自定义id，id可以是任何字符，只要能唯一区别每一条数据
        $hash{'result'}='成功';
        push( @$content_array_ref, \%hash );
        $total_num++;
    }

    return ( $status, $mesg, $total_num );
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
    my @temp = split(/ /, $line_content);
    my @temp_test = split(/--/,$temp[6]);
    if ( $temp_test[0] eq '=level:') {
        $config{'datetime'}        = $temp[8].' '.$temp[2];
        my @temp_user = split(/-/,$temp[4]);
        $temp_user[1] =~ s/\://g ;
        $config{'user_name'}        = $temp_user[1];
        my @temp_add_mes = split(/--/,$temp[5]);
        $config{'mainframe_add'}        = $temp_add_mes[0];
        $config{'user_description'}        = $temp_add_mes[1];
        $config{'result'}        = '成功';
    }else{
        $config{'datetime'}        = $temp[9].' '.$temp[3];
        my @temp_user = split(/-/,$temp[5]);
        $temp_user[1] =~ s/\://g ;
        $config{'user_name'}        = $temp_user[1];
        my @temp_add_mes = split(/--/,$temp[6]);
        $config{'mainframe_add'}        = $temp_add_mes[0];
        $config{'user_description'}        = $temp_add_mes[1];
        $config{'result'}        = '成功';
    }
    


    #============自定义字段组装-END===========================#
    return %config;
}

sub send_status($$$) {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 1 表示重新应用，其他表示不应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $reload, $mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'reload'} = $reload;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}

sub prepare_search($) {
    my $search = shift;

    $search =~ s/\^/\\\^/g;
    $search =~ s/\$/\\\$/g;
    $search =~ s/\./\\\./g;
    $search =~ s/\|/\\\|/g;
    $search =~ s/\(/\\\(/g;
    $search =~ s/\)/\\\)/g;
    $search =~ s/\[/\\\[/g;
    $search =~ s/\]/\\\]/g;
    $search = lc $search;

    return $search;
}

sub prepare_note($) {
    my $note = shift;
    $note =~ s/\n/ /g;
    $note =~ s/,/，/g;
    return $note;
}

sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}

sub getDate($) {
    my $now = shift;
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($now);
    $year += 1900;
    $mon++;
    return sprintf("%04d-%02d-%02d", $year, $mon, $mday);
}


