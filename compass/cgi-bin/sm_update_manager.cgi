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
use Data::Dumper;
require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'file_relevant_time.pl';

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

my $config_file_dir = "${swroot}/updateips/rules";
my $config_file     = "$config_file_dir/settings";

my $tmp_dir         = "/tmp";
my $systemconfig    = "${swroot}/systemconfig/settings";

my $temp_update     = '/usr/local/bin/libUpdateOperate.py';
# my $temp_cmd ;
my $errormessage    = '';
my $warnmessage     = '';
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
    &make_file();

    &read_system_config();#一进入就读取系统信息,包含标题等信息
    #做出响应
    &do_action();
}

sub init_data(){

	$errormessage       = '';
	$notemessage        = '';
    $cmd                = '/usr/local/bin/getUpdateManageMessage.py';
    $test_status        = '/usr/local/bin/getUpdateStatus.py';

    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/sm_update_manager.css" />
                    <link rel="stylesheet" type="text/css" href="/include/tips.css" />

                    <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css"/>
                    <link rel="stylesheet" type="text/css" href="/include/waiting_mesgs.css"/>
                    <script type="text/javascript" src="/include/popup_mesgs.js"></script>
                    <script type="text/javascript" src="/include/waiting_mesgs.js"></script>

                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/tips.js"></script>
                    <script language="JavaScript" src="/include/sm_update_manager.js"></script>';
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-END==============================#
}

sub do_action() {
    #==一般ACTION只会通过一种方式传过来，开发者需要自己判断从哪种方式传过来==#
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};
    
    &read_conf();

    if($action ne 'export_data' && $query_action ne 'export_data' && $query_action ne 'export_selected') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#

    if ( $action eq 'load_data' && $panel_name eq 'list_panel' ) {
        &load_data_extend();
    }
    elsif ($action eq 'upgrade'){
        &update_file();
        &show_page();
        
    }elsif( $action eq 'load_data' && $panel_name eq 'log_detail_panel' ) {
        &load_log();
    }elsif($action eq 'update') {
        &show_update_detail();
    }elsif($action eq 'reset_status') {
        `sudo $test_status -r -t $par{'type'}`

    }

    else {
        &show_page();
    }
}

sub load_log() {
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

sub get_detail_data($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;
    # my $search = &prepare_search( $par{'search'} );
    $conf_file = "/var/efw/unify_update/".$par{'type'}."/update.log" ;
    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records( $conf_file, $page_size, $current_page, \@lines );
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
        # if ( $search ne "" ) {
        #     my $name = lc $hash{'name'};
        #     my $note = lc $hash{'note'};
        #     if ( !($name =~ m/$search/) && !($note =~ m/$search/) ) {
        #         #===对名字，说明进行搜索===#
        #         next;
        #     }
        # }

        $hash{'id'} = $id; #自定义id，id可以是任何字符，只要能唯一区别每一条数据
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
    my @temp = split(/\|/, $line_content);
    $config{'update_time'}       = $temp[0];
    $config{'update_action'}       = $temp[1];
    $config{'update_res'}     = $temp[2];

    #============自定义字段组装-END===========================#
    return %config;
}

# 检测升级状态函数
sub show_update_detail() {
    my $lib_type = $par{'lib_type'};
    # my $temp = $par{'temp'};
    # if ($temp eq 'direct_get') {
        $status = `$test_status -t $lib_type`;
        $status =~ s/\n//g;  
        &send_status($lib_type ,0,$status);
        return;
    # }
    # my $update_status;
    # for (my $i = 0; ; $i++) {
    #     $status = `$test_status -t $lib_type`;
    #     $status =~ s/\n//g;   
    #     if( $status =~ m/COMPLETED|ERROR/){
    #         $status =~ m/COMPLETED/ ? $update_status = '升级成功' : $status =~ m/ERROR/ ? $update_status = '升级成功' : '';
    #         last;
    #     }
    #     if ($temp ne $status) {
    #         last;
    #     }
    # }
    # &send_status(0,0,$status);
    # return;
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
    <div id="log_detail_panel" class="container"></div>
	<input type="hidden" id="log-mesg-error" value="$errormesg">
	<input type="hidden" id="log-mesg-note" value="$notemessage">	
	
EOF
    ;
}

sub read_conf(){
    if ( -f $config_file ) {
       &readhash( "$config_file", \%settings );
    }
}

sub update_file() {
    my $cgi = new CGI; 
    my $file = $cgi->param('file_lib');
    my $tmp_fp = `mktemp`;
    my $lib_type = $cgi->param('lib_type');
    my $temp_cmd = "sudo $temp_update -t $lib_type -p $tmp_fp ";

    if(!open(UPLOAD, ">$tmp_fp")) { $errormessage="打开文件失败"; return false; } 
    binmode UPLOAD;
    my $count = 0;
    while(<$file>) { $count = 1; print UPLOAD; }
    close UPLOAD;
    if(!$count) {
        $errormessage = "文件内容为空";
        return 0;
    }
    # 执行升级脚本
    my $msg = `$temp_cmd`;
    if ($msg eq 'MUSTSINGLE') {
        $errormessage='升级失败，有其他用户正在升级，请稍后再试！';
    }else{
        $notemessage = '上传成功，请于操作栏查看升级过程或结果';
    }
    # 当捕捉到成功或失败时结束循环
    # for (my $i = 0; ; $i++) {
    #     my $status = `$test_status -t $lib_type`;   
    #     if( $status =~ m/COMPLETED|ERROR/){
    #         $status =~ m/COMPLETED/ ? $notemessage = '升级成功' : $status =~ m/ERROR/ ? $errormessage = '升级失败' : '';
    #         last;
    #     }
    # }
    return;      
 
}

sub load_data_extend() {


    my %ret_data;

    my @content_array;
    my @lib_type_array;

    my $res = `$cmd`;
    my $temp_hash = $json->decode($res);
    my $content_arr = $temp_hash->{'detail'};

    for (my $i = 0; $i < @$content_arr; $i++) {

        @$content_arr[$i]->{'index'} =$i+1;

        if (@$content_arr[$i]->{'version'} eq '') {
            @$content_arr[$i]->{'version'} = Encode::decode_utf8('暂无当前版本');
        }elsif(@$content_arr[$i]->{'version'} eq 'no'){
            @$content_arr[$i]->{'version'} = Encode::decode_utf8('无版本信息');
        }
        if (@$content_arr[$i]->{'deadtime'} eq '') {
            @$content_arr[$i]->{'deadtime'} = Encode::decode_utf8('序列号无效');
        }elsif(@$content_arr[$i]->{'deadtime'} eq 'no'){
            @$content_arr[$i]->{'deadtime'} = Encode::decode_utf8('永久有效');
        }

        @$content_arr[$i]->{'update_status'} = Encode::decode_utf8(`$test_status -t @$content_arr[$i]->{'lib_type'}`);
        # @$content_arr[$i]->{'update_status'} = Encode::decode_utf8('ERROR:您上一次升级出现异常');
        # @$content_arr[$i]->{'update_status'} = Encode::decode_utf8('COMPLETED:成功');
        # @$content_arr[$i]->{'update_status'} = Encode::decode_utf8('UPGRADING:有用户正在升级');
        @$content_arr[$i]->{'update_status'} =~ s/\n//g;
        push( @content_array, @$content_arr[$i] );
        push( @lib_type_array, @$content_arr[$i]->{'lib_type'} );
    }

    # foreach $item (@lib_type_array){
    #     my $update_status = `$test_status -t $item`;
    #     if ($update_status eq '0') {
    #         $errormessage ="升级异常!";
    #     }elsif($update_status eq '1'){
    #         $notemessage ="升级成功!";
    #     }
    # }
    my $total_num = scalar(@$content_arr);

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    $resData{'reload'} = 0;
    $resData{'status'} = 0;

    my $ret = $json->encode(\%ret_data);
    print $ret; 

}

sub make_file(){
    if(!-e $config_file_dir)
    {
        `mkdir -p $config_file_dir`;
    }
    if(!-e $config_file)
    {
        `touch $config_file`;
    }
}

sub read_system_config(){
    if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    $system_title = $system_settings{'SYSTEM_TITLE'};
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
    # &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
    print $result;
}
