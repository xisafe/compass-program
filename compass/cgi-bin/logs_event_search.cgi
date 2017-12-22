#!/usr/bin/perl

use Encode;

require '/var/efw/header.pl';
require 'list_panel.pl';
require 'logs_event_search.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #配置数据所存放的文件
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my $classification_file;
my $engine_list_file;
my $create_engine_list;
my $fetch_new_data;
my %classification_hash_cn;
my %classification_hash_en;
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
#=========================全部变量定义end=======================================#
&validateUser();
&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = "ipslog";
    $conf_dir           = "${swroot}/ipslog";
    $conf_file          = "$conf_dir/searchsettings";

    $engine_list_file   = $conf_dir.'/enginelist';
    $create_engine_list = '/usr/local/bin/restarttopology -e';

    $fetch_new_data     = '/usr/local/bin/log2sql';

    $page_title         = "事件查询";


    $classification_file = "${swroot}/ipsconsole/rules/classification";

    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/list_panel.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/logs_event_search.css" />
                    <script language="JavaScript" src="/include/logs_event_search.js"></script>
                    <script type="text/javascript" src="/include/ESONCalendar.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css" />
                    <script language="JavaScript" src="/include/popup_mesgs.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    &get_classification_hash( \%classification_hash_cn, \%classification_hash_en );
    #====获取通过post或者get方法传过来的值-END=========#

    system( $create_engine_list );#生成引擎列表文件

    &make_file();

    &readhash( $conf_file, \%settings );

    #========配置列表面板的数据-BEGIN==================#
    &config_list_panel( \%list_panel_config );
    #========配置列表面板的数据-END====================#
}

sub do_action() {
    my $action = $par{'ACTION'};
    if( !$action ) {
        $action = $query{'ACTION'};
    }

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==下载数据==#
        &load_data();
    } elsif( $action eq 'query_suggestion' ) {
        &query_suggestion();
    } elsif ( $action eq 'save_data' ) {
        &save_data();
    } elsif($action eq 'delete_all'){
        &delete_all();
    } else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &create_parameter_config_widget();
    &display_list_panel(\%list_panel_config);
    &closepage();
}

sub load_data(){
    #====第一步，看传过来的参数是否有改变，有改变先保存====#
    &save_data_without_feedback();

    #====第二步，执行命令获取新的数据======================#
    system( $fetch_new_data );

    #====第三步，获取返回数据==============================#
    my %ret_data;

    my @content_array, @display_cols;
    my ( $total_page, $total_num ) = &get_searched_content( \@content_array );
    &get_display_cols( \@display_cols, $list_panel_config{'panel_header'} );

    %ret_data->{'display_cols'} = \@display_cols;
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_page'} = $total_page;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'page_size'} = $settings{'PAGESIZE'};

    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);

    print $ret; 
}

sub get_searched_content($) {
    my $content_array = shift;
    my $current_page    = $par{'current_page'};
    my $search          = $par{'search'};
    my $time_start      = $par{'time_start'};
    my $time_end        = $par{'time_end'};

    my ( $total_page, $total_num ) = ( 0, 0 );
    if (-e $conf_file) {
        my $dbh = connect_sql();
        my $conf = loadConfig($conf_file);

        ( $total_page, $total_num ) = get_total_page_num( $search, $time_start, $time_end, $conf, $dbh );
        my $sth = search( $search, $time_start, $time_end, $current_page, $total_page, $conf, $dbh );
        while ( my $list=$sth->fetchrow_hashref()) {
            push( @$content_array, $list );
        }
        $dbh->disconnect();
    }

    return ( $total_page, $total_num );
}

sub get_display_cols($$) {
    my $display_cols = shift;
    my $panel_header = shift;
    foreach my $item ( @$panel_header ) {
        if( $item->{'enable'} ) {
            push( @$display_cols, $item->{'name'} );
        }
    }
    return $colspan;
}

sub save_data() {
    if( $settings{'PRIORITY'} ne $par{'PRIORITY'} || $settings{'ENGINE'} ne $par{'ENGINE'} || $settings{'ORDER_BY'} ne $par{'ORDER_BY'} || $settings{'PAGESIZE'} ne $par{'PAGESIZE'} ) {
    # if( $settings{'PRIORITY'} ne $par{'PRIORITY'} ) {
        $settings{'PRIORITY'} = $par{'PRIORITY'};
        $settings{'ENGINE'} = $par{'ENGINE'};
        $settings{'ORDER_BY'} = $par{'ORDER_BY'};
        $settings{'PAGESIZE'} = $par{'PAGESIZE'};
        &writehash( $conf_file, \%settings );
    }
    my %ret_data;
    %ret_data->{'status'} = 0;

    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);

    print $ret;
}

sub save_data_without_feedback() {
    if( $settings{'PRIORITY'} ne $par{'PRIORITY'} || $settings{'ENGINE'} ne $par{'ENGINE'} || $settings{'ORDER_BY'} ne $par{'ORDER_BY'} || $settings{'PAGESIZE'} ne $par{'PAGESIZE'} ) {
    # if( $settings{'PRIORITY'} ne $par{'PRIORITY'} ) {
        $settings{'PRIORITY'} = $par{'PRIORITY'};
        $settings{'ENGINE'} = $par{'ENGINE'};
        $settings{'ORDER_BY'} = $par{'ORDER_BY'};
        $settings{'PAGESIZE'} = $par{'PAGESIZE'};
        &writehash( $conf_file, \%settings );
    }
}

sub delete_all() {
    my $dbh = connect_sql();
    &truncate_table( $dbh );
    $dbh->disconnect();


    my %ret_data;
    %ret_data->{'status'} = 0;

    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);

    print $ret;
}

sub query_suggestion() {
    my %ret_data;
    if( $classification_hash_cn{$par{'type'}} || $classification_hash_en{$par{'type'}} ) {
        if( $classification_hash_cn{$par{'type'}} ) {
            %ret_data->{'mesg'} = $classification_hash_cn{$par{'type'}};
        } else {
            %ret_data->{'mesg'} = $classification_hash_en{$par{'type'}};
        }
    } else {
        %ret_data->{'mesg'} = "暂无建议";
    }

    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);

    print $ret;
}

sub create_parameter_config_widget($) {
    my %PRIORITY_SELECT, %ENGINE_SELECT, %ORDER_BY_SELECT;
    $PRIORITY_SELECT{ $settings{'PRIORITY'} } = "selected";
    $ENGINE_SELECT{ $settings{'ENGINE'} } = "selected";
    $ORDER_BY_SELECT{ $settings{'ORDER_BY'} } = "selected";
    printf <<EOF
    <div class="parameter_config_panel">
        <div class="parameter_config_panel_boder">
            <form id="LOGS_EVENT_SEARCH_FORM" name="LOGS_EVENT_SEARCH_FORM">
            <span class="parameter_config_items">
                <span class="opt-tools"></span>
                <span class="parameter_config_item">
                    <label for="PRIORITY" class="prefix-lable-for-text">窗口定义</label>
                    <select id="PRIORITY" name="PRIORITY" class="parameter_config_select parameter_config_commit extend_search_for_logs_event_search">
                        <option value="高"  $PRIORITY_SELECT{'高'}>高</option>
                        <option value="中"  $PRIORITY_SELECT{'中'}>中</option>
                        <option value="低"  $PRIORITY_SELECT{'低'}>低</option>
                        <option value="all" $PRIORITY_SELECT{'all'}>全部</option>
                    </select>
                </span>
                <span class="parameter_config_item">
                    <label for="ENGINE" class="prefix-lable-for-text">引擎</label>
                    <select id="ENGINE" name="ENGINE" class="parameter_config_select parameter_config_commit extend_search_for_logs_event_search">
EOF
    ;
    my @engine_list = &read_conf_file( $engine_list_file );
    foreach my $item ( @engine_list ) {
        if( $item =~ /\((.*)\)/ ) {
            my $value = $1;
            my $text = $item;
            print "<option value='$value' ".$ENGINE_SELECT{ $value }.">$text</option>"
        }
    }

    printf <<EOF
                        <option value="all" $ENGINE_SELECT{'all'}>全部</option>
                    </select>
                </span>
                <span class="parameter_config_item">
                    <label for="ORDER_BY" class="prefix-lable-for-text">事件排序</label>
                    <select id="ORDER_BY" name="ORDER_BY" class="parameter_config_select parameter_config_commit extend_search_for_logs_event_search">
                        <option value="priority" $ORDER_BY_SELECT{'priority'}>基于危险级别</option>
                        <option value="date" $ORDER_BY_SELECT{'date'}>基于时间</option>
                    </select>
                </span>
                <span class="parameter_config_item">
                    <label for="PAGESIZE" class="prefix-lable-for-text">最大事件显示系数</label>
                    <input tyep="text" id="PAGESIZE" name="PAGESIZE" class="parameter_config_text parameter_config_commit extend_search_for_logs_event_search" value="$settings{'PAGESIZE'}">
                    (15-100)
                </span>
                <span class="parameter_config_item">
                    <input type="button" class="net_button" value="保存参数" onclick="save_parameter_config();">
                </span>
            </span>
            </form>
            <div class="clear_both"></div>
        </div>
    </div>
EOF
    ;
}

sub config_list_panel($) {
    my $list_panel_config = shift;
    my @top_button, @bottom_button, @extend_search, @panel_header;

    #====组装整个面板的哈希================#
    $list_panel_config->{'top_button'}      = \@top_button;     #放在面板左上角的按钮
    $list_panel_config->{'bottom_button'}   = \@bottom_button;  #放在面板左下角的按钮
    $list_panel_config->{'extend_search'}   = \@extend_search;
    $list_panel_config->{'panel_header'}    = \@panel_header;
    $list_panel_config->{'page_size'}       = $settings{'PAGESIZE'};
    $list_panel_config->{'panel_name'}      = "logs_event_search";

    #====第一步，配置批量操作按钮(放在面板左上角的按钮)=====#

    #====第1.5步，配置页脚按钮,与批量操作按钮类似===========#
    my %functions = (
        "onclick" => "delete_all_logs(this);",
    );
    my %hash = (
        "enable"        => 1,
        "id"            => "delete_all_logs",
        "name"          => "delete_all_logs",
        "class"         => "",
        "button_icon"   => "delete.png",
        "button_text"   => "清空日志",
        "functions"     => \%functions,
    );
    push( @bottom_button, \%hash );
    
    #====第二步，配置要搜索的扩展条目=====#
    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "id"        => "time_start",
        "name"      => "time_start",
        "class"     => "time_input",
        "title"     => "开始时间",
    );
    push( @extend_search, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "id"        => "time_end",
        "name"      => "time_end",
        "class"     => "time_input",
        "title"     => "结束时间",
        "functions" => "",
    );
    push( @extend_search, \%hash );

    #====第三步，配置表头=============#
    my %functions = (
        "onclick" => "toggle_check(this)",
    );
    my %hash = (
        "enable"    => 0,           #用户控制表头是否显示
        "type"      => "checkbox",  #type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title"     => "",          #不同类型的，title需要的情况不同，一般text类型需要title
        "name"      => "checkbox",  #用户装载数据之用
        "id"        => "",          #元素的id号
        "class"     => "",          #元素的class
        "td_class"  => "",          #这一列td的class，主要用于控制列和列内元素
        "width"     => "5%",        #所有表头加起来应该等于100%,以精确控制你想要的宽度
        "functions" => \%functions, #一般只有checkbox才会有这个字段
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 0,
        "type"      => "radio",
        "title"     => "",
        "name"      => "test_radio",
        "class"     => "",
        "td_class"  => "",
        "width"     => "5%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "发生时间",
        "name"      => "time_start",
        "width"     => "18%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "入侵描述",
        "name"      => "msg",
        "width"     => "17%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "入侵类型",
        "name"      => "classification",
        "width"     => "12%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "危险级别",
        "name"      => "priority",
        "class"     => "",
        "td_class"  => "",
        "width"     => "5%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "源",
        "name"      => "sip",
        "class"     => "",
        "td_class"  => "",
        "width"     => "10%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "目标",
        "name"      => "dip",
        "class"     => "",
        "width"     => "10%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "协议类型",
        "name"      => "protocol",
        "class"     => "",
        "width"     => "5%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "处理动作",
        "name"      => "response_type",
        "class"     => "",
        "width"     => "8%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "发生次数",
        "name"      => "count",
        "class"     => "",
        "width"     => "5%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 1,
        "type"      => "text",
        "title"     => "引擎",
        "name"      => "engine_ip",
        "class"     => "",
        "width"     => "10%",
    );
    push( @panel_header, \%hash );

    my %hash = (
        "enable"    => 0,
        "type"      => "action",
        "title"     => "操作",        #一般action列都是这个标题
        "name"      => "",            #一般没有名字
        "class"     => "",
        "width"     => "10%",
    );
    push( @panel_header, \%hash );
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
        system("echo PRIORITY=all   >> $conf_file");
        system("echo ENGINE=all     >> $conf_file");
        system("echo ORDER_BY=date  >> $conf_file");
        system("echo PAGESIZE=15    >> $conf_file");
    }
}

sub get_classification_hash($) {
    my $classification_cn_ref = shift;
    my $classification_en_ref = shift;
    my @lines = &read_conf_file( $classification_file );
    foreach my $line ( @lines ) {
        my @temp = split( ",", $line );
        $classification_cn_ref->{$temp[1]} = $temp[2];
        $classification_en_ref->{$temp[3]} = $temp[2];
    }
}


# # 测试代码
# sub mytest()
# {
    # if (-e $SETTINGS) {
    #     my $dbh = connect_sql();
    #     my $conf = loadConfig($SETTINGS);

    #     #my $total_page = get_total_page_num($keyword,$time_start,$time_end,$conf,$dbh);
    #     my ($total_page,$log_count) = get_total_page_num("","","",$conf,$dbh);
    #     print "$total_page $log_count \n";
    #     print "--------------------------\ntest for search function\n";
    #     my $sth = search("","2014-04-11","2014-04-11",1,$total_page,$conf,$dbh);
    #     while ( my $list=$sth->fetchrow_hashref()) {
    #         print "$list->{'id'} $list->{'sid'}\n";
    #     }
    #     $sth = search("","","",2,$total_page,$conf,$dbh);
    #     while ( my $list=$sth->fetchrow_hashref()) {
    #         print "$list->{'id'}\n";
    #     }
    #     $sth = search("","","",3,$total_page,$conf,$dbh);
    #     while ( my $list=$sth->fetchrow_hashref()) {
    #         print "$list->{'id'}\n";
    #     }
    #     $sth = search("","","",4,$total_page,$conf,$dbh);
    #     while ( my $list=$sth->fetchrow_hashref()) {
    #         print "$list->{'id'}\n";
    #     }
    #     $sth = search("","","",5,$total_page,$conf,$dbh);
    #     while ( my $list=$sth->fetchrow_hashref()) {
    #         print "$list->{'id'}\n";
    #     }
    #     $dbh->disconnect();
    # }
# }
# mytest();
