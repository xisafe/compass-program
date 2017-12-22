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
    $logs               = 'botnet_log';
    $sid_info           = '/usr/local/bin/get_sid_info.py';
    $logs_name          = "僵尸网络日志";
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/all_log.css" />
                    <link rel="stylesheet" type="text/css" href="/include/jquery-ui.min.css" />
                    <script language="JavaScript" src="/include/jquery-1.12.1.min.js"></script>
                    <script language="JavaScript" src="/include/jquery-ui.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/logs_search.js"></script>
                    <script type="text/javascript" src="/include/jsencrypt.min.js"></script>
                    <script type="text/javascript" src="/include/logs_delete.js"></script>
                    <script language="JavaScript" src="/include/botnet_log.js"></script>';
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-END==============================#
}

sub do_action() {
    #==一般ACTION只会通过一种方式传过来，开发者需要自己判断从哪种方式传过来==#
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};

    if($action ne 'down_log' && $query_action ne 'down_log' && $query_action ne 'down_log') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#

    if ( $action eq 'load_data' && $panel_name eq 'list_panel' ) {
        &load_data_extend();
    }
    elsif ( $action eq 'search'   ) {
        &search_items();
    }
    elsif ( $action eq 'importLog') {
        ($errormessage, $notemessage) = &importLog_asynchronous(\%par,$logs);
        &show_page();
    } 
    elsif( $action eq 'query_suggestion' ) {
        &query_suggestion();
    }
    elsif( $action eq 'down_log') {
        ($errormessage, $notemessage) = &down_log(\%par, $logs,$logs_name);
        &showhttpheaders();
        &show_page();
    }
    elsif( $action eq 'delete') {
        &delete_data_extend();
        # &show_page();
    }
    elsif( $action eq 'clearLog') {
        # ($errormessage, $notemessage) = &clearLog_in_dataBase(\%par, $logs);
        &clear_Log($logs);
        # &show_page();
    }
    else {
        &show_page();
    }
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

sub load_data_extend() {

    my $time = $par{'time'};
    my $search = $par{'search'};
    my $page_size = $par{'page_size'};
    my $current_page = $par{'current_page'};
    my $data = `sudo $cmd -l $logs -N $current_page -S $page_size`;
    # print "sudo $cmd -l $logs -N $current_page -S $page_size";
    # print $data;
    my @arrCache;
    my @arr;
    my %resData;
    my $total_len;
    if($data ne '') {
        $data =~ /\W+total_num\W+ \[(\d+)\]\}/;
        $total_len = int($1);
        $data = $json->decode($data);
        @arrCache = @$data;
        shift(@arrCache);
        if($search ne '') {
            $search = &prepare_search( $search );
            my $cmd_temp = "sudo /usr/local/bin/findlog.py -n 'virus_log' -f $search -t $time";
            my $result = `$cmd_temp`;
            if($result){
                $result = $json->decode($result);
                my  @arrTemp = @$result;
                for(my $i=0; $i<@arrTemp; $i++) {
                    $arrTemp[$i]->{'actionView'} = $arrTemp[$i]->{'action'};
                }
                @arr = @arrTemp;
            }
        }else {
            for(my $i=0; $i<@arrCache; $i++) {
                
                $arrCache[$i]->{'id'} = $i;
                $arrCache[$i]->{'actionView'} = $arrCache[$i]->{'action'};

            }
            @arr = @arrCache;
        }
    }
    else{
        @arr = ();
    }
    $resData{'detail_data'} = \@arr;
    $resData{'time'} = $time;
    $resData{'reload'} = 0;
    $resData{'status'} = 0;
    $resData{'total_num'} = $total_len;
    
    my $result = $json->encode(\%resData);
    print $result;
}



sub search_items() {
    my $reload = 0;
    my $temp_hash;
    my @content_arr = &get_config_record( \%par );

    my $temp = "sudo $cmd -l $logs";
    my @temp_arr = ('-f','-e','-s','-d','-o','-t','-N','-S');

    for (my $i = 0; $i < @content_arr; $i++) {
        if (@content_arr[$i] ne '') {
            $temp = $temp.' '.@temp_arr[$i].' "'.@content_arr[$i].'"';
        }
    }

    my $res = `$temp`;
    my @temp_arr;
    $res =~ /\W+total_num\W+ \[(\d+)\]\}/;
    $total_len = int($1);
    if($res ne ''){
        $temp_hash = $json->decode($res);
    }
    else {
        $temp_hash = $res;
    }

    my $len = scalar(@$temp_hash);
        @temp_arr = @$temp_hash;
        shift(@temp_arr);

    $resData{'detail_data'} = \@temp_arr;
    $resData{'total_num'} = $total_len;
    $resData{'reload'} = 0;
    $resData{'status'} = 0;
    
    my $result = $json->encode(\%resData);
    print $result;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    my $finish;
   
    my $current_page = $hash_ref->{'current_page'};
    my $page_size = $hash_ref->{'page_size'};
    my $start_date = $hash_ref->{'start_date'};
    my $start_time_hour = $hash_ref->{'start_time_hour'};
    my $start_time_minute = $hash_ref->{'start_time_minute'};

    my $begin = $start_date." ".$start_time_hour.":".$start_time_minute; 
    
    if ($start_date eq '') {
        $begin = '';
    }
    push( @record_items, $begin );

    my $end_date = $hash_ref->{'end_date'};
    my $end_time_hour = $hash_ref->{'end_time_hour'};
    my $end_time_minute = $hash_ref->{'end_time_minute'};
    if ($hash_ref->{'end_time_minute'} eq '59') {
        $finish = $end_date." ".$end_time_hour.":".$end_time_minute.':'.'59';
    }
    else {
        $finish = $end_date." ".$end_time_hour.":".$end_time_minute;     
    }
    if ($end_date eq '') {
        $finish = '';
    }
    push( @record_items, $finish );

    my $sourceIP = $hash_ref->{'sourceIP'};
    push( @record_items, $sourceIP);

    my $destinationIP = $hash_ref->{'destinationIP'};
    push( @record_items, $destinationIP);

    my $sourceUser = $hash_ref->{'sourceUser'};
    push( @record_items, $sourceUser);

    my $destinationUser = $hash_ref->{'destinationUser'};
    push( @record_items, $destinationUser);
    
    push( @record_items, $current_page);
    push( @record_items, $page_size);
    return @record_items;

}

sub query_suggestion() {
    my %ret_data;
    my $sid = $par{'type'};
    %ret_data->{'mesg'} = `sudo $sid_info -s $sid`;
    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub delete_data_extend() {
    
    my $start_time = "'".$par{'start_time'}.' '.$par{'start_hour'}.':'.$par{'start_min'}."'";
    my $end_time = "'".$par{'end_time'}.' '.$par{'end_hour'}.':'.$par{'end_min'}."'";
    my $status;
    if($par{'start_time'} eq '' && $par{'end_time'} eq '') {
        $status = `sudo $cmd -X $logs`;
    }
    elsif($par{'start_time'} eq '') {
        if($par{'end_min'} eq '59') {
            $end_time = "'".$par{'end_time'}.' '.$par{'end_hour'}.':'.$par{'end_min'}.':'.'59'."'";
        }
        $status = `sudo $cmd -X $logs -e $end_time`;
    }
    elsif($par{'end_time'} eq '') {
        $status = `sudo $cmd -X $logs -f $start_time`;
    }
    else {
        if($par{'end_min'} eq '59') {
            $end_time = "'".$par{'end_time'}.' '.$par{'end_hour'}.':'.$par{'end_min'}.':'.'59'."'";
        }
        $status = `sudo $cmd -X $logs -f $start_time -e $end_time`;
    }

    my %resData;
    
    if( $status == 1 ) {
        $notemessage= '删除日志成功!';
        %resData->{'status'} = 0;
        %resData->{'mesg'} = '删除日志成功';
    }else {
        $errormessage = '删除日志失败!';
        %resData->{'status'} = -1;
        %resData->{'mesg'} = '删除日志失败';
    }
    
    my $result = $json->encode(\%resData);
    print $result;
}

sub clear_Log($) {
    my $name = shift;

    my $status = `sudo /usr/local/bin/filter_log.py -C $name`;
    # print "sudo /usr/local/bin/filter_log.py -C $name";
    # my $a = "sudo /usr/local/bin/filter_log.py -C $name";
    # system("echo $a>/var/efw/chensisi.debug");
    my %ret_data;
    $status =~ s/\n//g;
    if($status eq '1'){
        %ret_data->{'mesg'} = '清空成功';
    }
    else {
        %ret_data->{'mesg'} = '清空失败';
    }
    %ret_data->{'status'} = $status;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}