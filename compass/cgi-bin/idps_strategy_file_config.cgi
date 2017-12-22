#!/usr/bin/perl

#===============================================================================#
#
# DESCRIPTION: 策略集中策略项的增删改查
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2014.03.20
#===============================================================================#

use Encode;

#==== header.pl中包含很多通用函数，比如IP地址的检测，和文件的读写===============#
#一般都会引用，不要删除此行
require '/var/efw/header.pl';
#===============================================================================#

#=====begin全部变量定义,名字都不用改，可根据实际情况适当添加====================#
#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;                 #要保存数据的目录名字
my $conf_dir;                   #规则所存放的文件夹
my $conf_file;                  #规则所存放的文件
my $system_rules_dir;           #存储系统策略集文件夹
my $custom_rules_dir;           #存储用户策略集文件夹
my $intrusion_type_file;        #入侵类型所存放的文件
my $exceptions_file;            #存储策略集中例外的规则
my $rules_conf_file;            #存储策略集的文件路径和响应方式以及禁用/启用状态
my $respond_type_file;          #存储响应类型的文件，此文件为系统内置
my $export_file;                #导出时使用
my $export_filename;            #导出时使用
my $import_error_file;          #导入出错时使用
my $imported_tag;               #导入时使用
my $need_reload;                #需要重新加载的标识文件
my $restart;                    #应用重启的程序,根据实际情况填写
my $extraheader;                #存放用户自定义JS
my $REMOTE_ADDR;                #客户端地址
my %par;                        #存放传过来的数据的哈希
my %query;                      #存放通过get方法传过来的数据
my %intrusion_types_hash;       #存放系统预置的入侵类型
my %risk_level_hash;            #存放系统预置的入侵类型危险级别的哈希
my %respond_type_hash;          #存放响应方式的哈希，系统内置数据
my %rules_conf_hash;            #存放系统策略集配置的哈希
my %exceptions_hash;            #存放系统策略集配置的哈希
my @display_add_config_data;    #存放<input>信息的哈希
my @table_display_fields;       #规则列表中要展示的字段的集合
my @table_display_fields_name;  #规则列表中要展示的字段的集合
my @table_display_fields_widths;#规则列表中要展示的各个字段的宽度的集合
#=========================全部变量定义end=======================================#

&init_data();
&getcgihash(\%par);
&getqueryhash(\%query);
&do_action();

sub init_data(){
    $custom_dir             = '/ips/rules';
    $conf_dir               = "${swroot}".$custom_dir;
    # $conf_file              = $conf_dir.'/custom/';
    $system_rules_dir       = $conf_dir.'/system';
    $custom_rules_dir       = $conf_dir.'/custom';
    $intrusion_type_file    = $conf_dir.'/classification';
    $exceptions_file        = $conf_dir.'/exceptions';
    $rules_conf_file        = $conf_dir.'/policies';
    $respond_type_file      = "/etc/efw/ips/respond_type";

    $need_reload        = $conf_dir.'/strategies_conconfig_need_reload';
    $import_error_file  = $conf_dir.'/import_error_file';
    $imported_tag       = $conf_dir.'/imported_tag';
    $export_file        = '/tmp/template_add_list.csv';
    $export_filename    = 'template_add_list.csv';

    $restart            = '';

    $REMOTE_ADDR        = $ENV{'REMOTE_ADDR'};#客户端地址

    #===存放用户自定义JS,CSS：一般先用户定义相应页面的~init.js,然后引用template_add_list.js、template_add_list.css===#
    #===也可拷贝template_add_list.js、template_add_list.css再进行自定义更改,不建议这样做,这样不适合后期维护和扩展====#
    $extraheader        = '<script language="JavaScript" src="/include/idps_strategy_file_config.js"></script>
                            <script language="JavaScript" src="/include/idps_strategy_file_config_paging.js"></script>
                            <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />
                            <link rel="stylesheet" type="text/css" href="/include/idps_strategies_config.css" />';
    #================================end=============================================================================#

    &make_file();#检查要存放规则的文件夹和文件是否存在，不存在就创建，此行不要删除或更改
    # &get_intrusion_types_hash( \%intrusion_types_hash );
    &get_risk_level_hash( \%risk_level_hash );
    &get_respond_type_hash(\%respond_type_hash);
    &get_rules_conf_hash(\%rules_conf_hash);
    &get_exceptions_hash(\%exceptions_hash);

    #========配置添加模块的数据================================#
    #   添加模块的生成，主要是数据的配置，请按照例子配置数据
    #==========================================================#
    &config_add_item_data();#到这个函数中去配置
    #========配置数据end=======================================#

    &get_display_fields();#根据配置，生成需要的数据，此行不要删掉或更改
}

sub get_file_relative_path($) {
    my $file = shift;
    my $file_relative_path = "";
    my $system_file_path = $system_rules_dir."/".$file;
    my $custom_file_path = $custom_rules_dir."/".$file;
    if( -f $system_file_path ) {
        #该文件存在系统目录中
        $file_relative_path = "system/$file";
    } elsif ( -f $custom_file_path ) {
        #该文件存在用户目录中
        $file_relative_path = "custom/$file";
    }
    return $file_relative_path;
}

sub get_file_absolute_path($) {
    my $file = shift;
    my $file_absolute_path = "";
    my $system_file_path = $system_rules_dir."/".$file;
    my $custom_file_path = $custom_rules_dir."/".$file;
    if( -f $system_file_path ) {
        #该文件存在系统目录中
        $file_absolute_path = $system_file_path;
    } elsif ( -f $custom_file_path ) {
        #该文件存在用户目录中
        $file_absolute_path = $custom_file_path;
    }
    return $file_absolute_path;
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
    #===================notice==============================
    #  传入规则字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回哈希中的值
    #  也可以自定义,但要和get_config_line同步
    #===================notice==============================
    #====如果改条记录以‘#’开头，则不显示====#
    if( $line_content =~ /^\#/ ) {
        $config{'valid'} = 0;
        return %config;
    }
    if ( $line_content =~ /msg:"([^:]+)".*classtype:(.*);.*sid:(\d+)/ ) {
        $config{'summary'}          = $1;
        $config{'classtype'}        = $2;
        # $config{'classtype_en'}     = $2;
        # $config{'classtype_cn'}     = $intrusion_types_hash{$2};
        $config{'risk_level'}       = $risk_level_hash{$config{'classtype'}};
        $config{'sid'}              = $3;
        $config{'line'}             = $3;
    } else {
        $config{'valid'} = 0;
        return %config;
    }
    #=====根据策略集的配置，读取策略集的响应方式=======#
    my $file_relative_path = &get_file_relative_path( $par{'set_filename'} );
    my $rule_conf_line = $rules_conf_hash{$file_relative_path};
    if( $rule_conf_line ne '' ) {
        my %rule_conf_hash = &get_rule_config_hash( $rule_conf_line );
        $config{'respond_type'}         = $rule_conf_hash{'respond_type'};
        $config{'respond_type_text'}    = $rule_conf_hash{'respond_type_text'};
        $config{'enabled'}              = $rule_conf_hash{'enabled'};
        $config{'eliminate_type'}       = "";
        $config{'eliminate_type_text'}  = "不排除";
        $config{'eliminate_ips'}        = "";
    }

    #=====再查看系统中有没有根据单独的一条规则配置的数据===#
    my $exception_line = $exceptions_hash{$config{'sid'}};
    if( $exception_line ne '' ) {
        my %exception_hash = &get_exception_config_hash( $exception_line );
        $config{'respond_type'}         = $exception_hash{'respond_type'};
        $config{'respond_type_text'}    = $exception_hash{'respond_type_text'};
        $config{'enabled'}              = $exception_hash{'enabled'};
        $config{'eliminate_type'}       = $exception_hash{'eliminate_type'};
        $config{'eliminate_type_text'}  = $exception_hash{'eliminate_type_text'};
        $config{'eliminate_ips'}        = $exception_hash{'eliminate_ips'};
    }
    # $config{'not_editable'} = 1;
    $config{'not_deletable'} = 1;

    $config{'set_filename'} = $par{'set_filename'};
    #============自定义字段组装完毕=========================
    return %config;
}

sub get_rule_config_hash($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    $config{'valid'} = 1;#默认是合法的行，如果有不合法的，将该字段置为0
    if ($line_content eq '') {
        $config{'valid'} = 0;
        return %config;
    }
    my @temp = split(/,/, $line_content);
    #============自定义字段组装开始=========================#
    $config{'file_relative_path'} = $temp[0];
    $config{'respond_type'} = $temp[1];
    $config{'respond_type_text'} = $respond_type_hash{$temp[1]};
    $config{'enabled'} = $temp[2];
    #============自定义字段组装完毕=========================#
    return %config;
}

sub get_exception_config_hash() {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    $config{'valid'} = 1;#默认是合法的行，如果有不合法的，将该字段置为0
    if ($line_content eq '') {
        $config{'valid'} = 0;
        return %config;
    }
    my @temp = split(/,/, $line_content);
    #============自定义字段组装开始=========================#
    $config{'sid'} = $temp[0];
    $config{'respond_type'} = $temp[1];
    $config{'respond_type_text'} = $respond_type_hash{$temp[1]};
    $config{'enabled'} = $temp[2];
    $config{'eliminate_type'} = $temp[3];
    if( $config{'eliminate_type'} eq 'by_src' ) {
        $config{'eliminate_type_text'} = "基于源IP";
    } elsif ( $config{'eliminate_type'} eq 'by_dst' ) {
        $config{'eliminate_type_text'} = "基于目的IP";
    } else {
        $config{'eliminate_type_text'} = "不排除";
    }
    $config{'eliminate_ips'} = $temp[4];
    if( $temp[4] eq '' ) {
        $config{'eliminate_ips'} = "";
    }
    #============自定义字段组装完毕=========================#
    return %config;
}

sub get_exception_line_config($) {
    my $data = shift;
    $data->{'valid'} = 1;
    #===当向excption中添加新的一行时，只知道部分信息，其他信息需要补充===#
    my $file = $data->{'set_filename'};
    #根据传过来的文件名，判断其为什么类型文件
    my $file_relative_path = &get_file_relative_path( $file );

    if( $file_relative_path eq "" ) {
        $data->{'valid'} = 0;
        return;
    }

    my $rule_conf_line = $rules_conf_hash{$file_relative_path};
    my %rule_conf_hash = &get_rule_config_hash( $rule_conf_line );
    if( $data->{'respond_type'} eq '' ) {
        #传过来的数据中，响应类型为空，则默认为该策略集中的响应方式
        $data->{'respond_type'} = $rule_conf_hash{'respond_type'};
    }
    if( $data->{'enabled'} eq '' ) {
        #传过来的数据中，启用禁用为空，则默认为该策略集中的启用禁用状态
        $data->{'enabled'} = $rule_conf_hash{'enabled'};
    }
    if( $data->{'eliminate_type'} eq '' ) {
        #传过来的数据中，排除类型为空，则默认为none
        $data->{'eliminate_type'} = 'none';
    }
    if( $data->{'eliminate_type'} eq 'none' ) {
        #传过来的数据中，排除类型为none，则默认为none
        $data->{'eliminate_ips'} = "";
    }
}

sub get_exception_config_line($) {
    my $data = shift;#传入一个哈希
    my @data_arr;
    #===================notice==============================
    #  配置好的规则字段用','(逗号)隔开
    #===================notice==============================
    push( @data_arr, $data->{'sid'} );
    push( @data_arr, $data->{'respond_type'} );
    push( @data_arr, $data->{'enabled'} );
    push( @data_arr, $data->{'eliminate_type'} );
    push( @data_arr, $data->{'eliminate_ips'} );
    #============自定义字段组装完毕=========================
    return join ",", @data_arr;
}

sub get_to_save_ips($) {
    my $content = shift;
    my @content = split( "\n", $content );
    my @processed = ();
    foreach my $item ( @content ) {
        if( $item ne '' ) {
            push( @processed, $item );
        }
    }
    return join "&", @processed;
}

sub process_empty_lines($) {
    my $content = shift;
    my @content = split( "\n", $content );
    my @processed = ();
    foreach my $item ( @content ) {
        if( $item ne '' ) {
            push( @processed, $item );
        }
    }
    return join " ", @processed;
}

sub get_config_line($){
    my $data = shift;#传入一个哈希
    my @data_arr;
    #===================notice==============================
    #  配置好的规则字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回规则
    #  也可以自定义,但要和get_config_hash同步
    #===================notice==============================
    foreach my $item (@display_add_config_data){
        push(@data_arr, $data->{$item->{'name'}});
    }
    #============自定义字段组装完毕=========================
    return join ",", @data_arr;
}

sub save_line_check($$){
    my $line_content = shift;
    my $lines = shift;#
    my $can_save = 1;
    my $can_save_mesg = "";
    #===========在此可以根据行内容判断是否可以保存=========
    #===如果不能，返回0和不能保存的原因，否则返回1和空串===
    my %to_save_data = &get_config_hash( $line_content );
    foreach my $line ( @$lines ) {
        my %temp = &get_config_hash( $line );
        if($temp{'name'} eq $to_save_data{'name'}) {
            $can_save = 0;
            $can_save_mesg = "已存在相同的名称";
            last;
        }
    }
    #====end===============================================
    return ($can_save, $can_save_mesg);
}

sub update_line_check($$$){
    my $line = shift;
    my $line_content = shift;
    my $lines = shift;
    my $can_update = 1;
    my $can_update_mesg = "";
    #===========在此可以根据行内容判断是否可以更新=========
    #===如果不能，返回0和不能更新的原因，否则返回1和空串===
    my %to_update_data = &get_config_hash( $line_content );
    my $length = @$lines;
    for(my $i = 0; $i < $length; $i++) {
        my %temp = &get_config_hash( $lines->[$i] );
        if($i != $line) {
            if($temp{'name'} eq $to_update_data{'name'}) {
                $can_update = 0;
                $can_update_mesg = "已存在相同目的名称";
                last;
            }
        }
    }
    #====end===============================================
    return ($can_update, $can_update_mesg);
}

sub del_line_check($$$){
    my $line = shift;
    my $line_content = shift;
    my $lines = shift;
    my $can_delete = 1;
    my $can_delete_mesg = "";
    #===========在此可以根据行内容判断是否可以删除=========
    #===如果不能，返回0和不能删除的原因，否则返回1和空串===
    
    #====end===============================================
    return ($can_delete, $can_delete_mesg);
}

sub get_export_line($) {
    my $line_content = shift;
    #===========在此可以配置要导出的数据===================
    my $new_line = $line_content;

    #====end===============================================
    return $new_line;
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    #==如果不是导出数据，都打印普通http头部==#

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==下载配置数据==#
        &load_data();
    } elsif($action eq 'save_data'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &save_data();
    } elsif($action eq 'enable_data'){
        #==启用数据(可多条同时启用)==#
        &enable_data();
    } elsif($action eq 'disable_data'){
        #==禁用数据(可多条同时禁用)==#
        &disable_data();
    } elsif($action eq 'edit_respond_type') {
        #==编辑响应类型==#
        &edit_respond_type();
    } else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}
sub show_page() {
    &openpage("新模板", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &create_respond_type_choices();
    &display_add();
    &display_rule_list();
    &closebigbox();
    &closepage();
}

sub create_needreload_tag() {
    system("touch $need_reload");
}

sub load_data(){
    my @content_array = ();
    chomp $par{'set_filename'};
    my $file_absolute_path = &get_file_absolute_path( $par{'set_filename'} );
    my @lines = read_conf_file($file_absolute_path);
    my $record_num = @lines;
    my $total = 0;
    my $search = $par{'search'};
    chomp($search);
    #===转换成小写，进行模糊查询==#
    $search = lc($search);
    for(my $i = 0; $i < $record_num; $i++){
        chomp(@lines[$i]);
        my %conf_data = &get_config_hash(@lines[$i]);
        if (! $conf_data{'valid'}) {
            next;
        }
        if($search ne ""){
            my $searched = 0;
            my $where = -1;
            foreach my $field ( sort keys %conf_data ) {
                #===转换成小写，进行模糊查询==#
                my $new_field = lc($conf_data{$field});
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
        push(@content_array, \%conf_data);
        $total++;
    }
    my %ret_data;
    %ret_data->{'display_cols'} = \@table_display_fields_name;
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total'} = $total;
    %ret_data->{'status'} = 0;#succeed
    if (-e $need_reload) {
        %ret_data->{'reload'} = 1;#Need reload
    } else {
        %ret_data->{'reload'} = 0;
    }
    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub save_data() {
    #==第一步先对%par中的值进行处理========#
    #==到&get_config_line(\%par)进行处理=====#

    #==第二步保存==========================#
    my ($status, $reload, $mesg) = &save_conf_line($par{'sid'},$par{'set_filename'});
    &reset_values();
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 0 表示不重新应用，其他表示应用
    # => $mesg: 相关错误的消息
    #===========================================#
    &send_status($status, $reload, $mesg, $mesg);
}

sub save_conf_line($$) {
    my $sid = shift;
    my $set_filename = shift;

    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 0 表示不重新应用，其他表示应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $reload, $mesg, $succeeded_num) = (-1, 0, "",0);

    my @lines = read_conf_file( $exceptions_file );
    my $record_num = @lines;

    if( $exceptions_hash{$sid} ) {
        #===如果存在这么一条记录,进行修改====#
        for(my $i = 0; $i < $record_num; $i++){
            my %data = &get_exception_config_hash($lines[$i]);
            if( $par{'sid'} eq $data{'sid'} ) {
                $data{'eliminate_type'} = $par{'eliminate_type'};
                $data{'eliminate_ips'}  = &get_to_save_ips( $par{'eliminate_ips'} );
                if( $data{'eliminate_type'} eq 'none' ) {
                    $data{'eliminate_ips'} = "";#如果用户修改了排除类型，则应该清空IP
                }
                my $line_content = &get_exception_config_line(\%data);
                $lines[$i] = $line_content;
                $succeeded_num++;
                last;
            }
        }
    } else {
        #===不存在，进行添加===#
        &get_exception_line_config(\%par);
        $data{'eliminate_type'} = $par{'eliminate_type'};
        $par{'eliminate_ips'}   = &get_to_save_ips( $par{'eliminate_ips'} );
        if ( $par{'valid'} ) {
            #===如果配置成功====#
            my $line_content = &get_exception_config_line(\%par);
            push( @lines, $line_content );
            $succeeded_num++;
        }
    }
    if( $succeeded_num ) {
        $status = 0;
        $reload = 1;
    }
    $mesg = "成功修改$succeeded_num条规则";
    &save_conf_file(\@lines, $exceptions_file);
    return ($status, $reload, $mesg);
}

sub save_conf_file($$) {
    my $ref = shift;
    my $filename= shift;
    my @lines = @$ref;
    open (FILE, ">$filename");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
}

sub enable_data() {
    toggle_enable(1);
}

sub disable_data() {
    toggle_enable(0);
}

sub toggle_enable($) {
    my $enable = shift;
    my $opt = "";
    if ($enable) {
        $enable = 'on';
        $opt = "启用";
    } 
    else {
        $enable = 'off';
        $opt = "禁用";
    }

    my @users = &getCurUser();
    my $user = $users[0];
    my $logmsg = "";

    my ($status, $reload, $mesg, $succeeded_num, $fail_num) = (0, 0, "", 0, 0);

    my $file_absolute_path = &get_file_absolute_path( $par{'set_filename'} );
    my @conf_lines = read_conf_file( $file_absolute_path );#读取储存配置的文件

    foreach my $conf_line ( @conf_lines ) {
        my %conf_data = &get_config_hash( $conf_line );
        if( $par{ $conf_data{'sid'} } eq $conf_data{'sid'} && $conf_data{'valid'} && $conf_data{'enabled'} ne $enable ) {
            #===========判断enabled字段是否跟策略集的相同，相同就不修改===========#
            #====要修改此行中对于的sid号数据进行修改，修改在exception文件中发生===#

            #==准备记录日志===#
            if( $enable eq 'on' ) {
                $logmsg = "开启了ID号为$conf_data{'sid'}的策略";
            } else {
                $logmsg = "关闭了ID号为$conf_data{'sid'}的策略";
            }
            $logmsg = $REMOTE_ADDR."--".$logmsg;
            system("/usr/bin/logger","-p","local6.notice","-t","userLog-$user","$logmsg");

            #===准备修改记录===#
            if( $exceptions_hash{$conf_data{'sid'}} ) {
                #===如果存在这么一条记录,进行修改====#
                my %exception_conf_data = &get_exception_config_hash( $exceptions_hash{$conf_data{'sid'}} );
                $exception_conf_data{'enabled'} = $enable;
                my $line_content = &get_exception_config_line(\%exception_conf_data);
                $exceptions_hash{$conf_data{'sid'}} = $line_content;
                $succeeded_num++;
            } else {
                #===不存在，进行添加===#
                &get_exception_line_config(\%par);
                if ( $par{'valid'} ) {
                    #===如果配置成功====#
                    $par{'sid'} = $conf_data{'sid'};
                    $par{'enabled'} = $enable;
                    my $line_content = &get_exception_config_line(\%par);
                    $exceptions_hash{$conf_data{'sid'}} = $line_content;
                    $succeeded_num++;
                }
            }
        }
    }

    #====对exceptions_hash进行整理=====#
    my @lines;
    foreach my $key ( sort keys %exceptions_hash ) {
        push( @lines, $exceptions_hash{$key} );
    }

    &save_conf_file( \@lines, $exceptions_file );
    #需要重新应用
    if($succeeded_num) {
        $reload = 1;
        &create_needreload_tag();
    }
    send_status($status, $reload, "成功$opt$succeeded_num条规则", "成功$opt$succeeded_num条规则");
}

sub edit_respond_type() {
    my ($status, $reload, $mesg, $succeeded_num, $fail_num) = (0, 0, "", 0, 0);

    my $file_absolute_path = &get_file_absolute_path( $par{'set_filename'} );
    my @conf_lines = read_conf_file( $file_absolute_path );#读取储存配置的文件

    #==========当前只提交了一个sid,但是为了保留扩展批量操作，这里保留for循环所有数据===============#
    foreach my $conf_line ( @conf_lines ) {
        my %conf_data = &get_config_hash( $conf_line );
        if( $par{ $conf_data{'sid'} } eq $conf_data{'sid'} && $conf_data{'valid'} && $conf_data{'respond_type'} ne $par{'respond_type'} ) {
            #===现存数据与提交上来的数据没有差别，或者数据不合法，就不进行修改=========#
            #===当要要修改对应sid号数据时，修改在exception文件中发生===================#
            if( $exceptions_hash{$conf_data{'sid'}} ) {
                #===如果存在这么一条记录,进行修改====#
                my %exception_conf_data = &get_exception_config_hash( $exceptions_hash{$conf_data{'sid'}} );
                $exception_conf_data{'respond_type'} = $par{'respond_type'};
                my $line_content = &get_exception_config_line(\%exception_conf_data);
                $exceptions_hash{$conf_data{'sid'}} = $line_content;
                $succeeded_num++;
            } else {
                #===不存在，进行添加===#
                &get_exception_line_config(\%par);
                if ( $par{'valid'} ) {
                    #===如果配置成功====#
                    $par{'sid'} = $conf_data{'sid'};
                    my $line_content = &get_exception_config_line(\%par);
                    $exceptions_hash{$conf_data{'sid'}} = $line_content;
                    $succeeded_num++;
                }
            }
        }
    }

    #====对exceptions_hash进行整理=====#
    my @lines;
    foreach my $key ( sort keys %exceptions_hash ) {
        push( @lines, $exceptions_hash{$key} );
    }

    &save_conf_file( \@lines, $exceptions_file );
    #需要重新应用
    if( $succeeded_num ) {
        $reload = 1;
        &create_needreload_tag();
    }
    send_status($status, $reload, "成功修改$succeeded_num条规则", "成功修改$succeeded_num条规则");
}

sub send_status($$$$) {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 0 表示不重新应用，其他表示应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $reload, $mesg, $detail_mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'reload'} = $reload;
    %hash->{'mesg'} = $mesg;
    %hash->{'detail_mesg'} = $detail_mesg;
    my $json = new JSON::XS;
    my $result = $json->encode(\%hash);
    print $result;
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    # if(! -e $conf_file){
    #     system("touch $conf_file");
    # }
}

sub get_intrusion_types_hash($) {
    my $intrusion_types = shift;
    my @lines = &read_conf_file( $intrusion_type_file );
    foreach my $line ( @lines ) {
        my %intrusion_type_hash = &get_intrusion_type_hash( $line );
        $intrusion_types->{$intrusion_type_hash{'intrusion_type_en'}} = $intrusion_type_hash{'intrusion_type_cn'};
    }
    return;
}

sub get_risk_level_hash($) {
    my $risk_level_hash_ref = shift;
    my %risk_leve_text_hash = (
        '1' => "高",
        '2' => "中",
        '3' => "中",
        '4' => "低"
    );
    my @lines = &read_conf_file( $intrusion_type_file );
    foreach my $line ( @lines ) {
        my %intrusion_type_hash = &get_intrusion_type_hash( $line );
        $risk_level_hash_ref->{$intrusion_type_hash{'intrusion_type_en'}} = $risk_leve_text_hash{ $intrusion_type_hash{'intrusion_type_level'} };
    }
    return;
}

sub get_intrusion_type_hash($) {
    my $line = shift;
    chomp($line);
    my %config;
    $config{'valid'} = 1;
    if ($line eq '') {
        return ;
    }
    my @temp = split(/,/, $line);
    #===================notice================================#
    #  传入规则字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回哈希中的值
    #  也可以自定义,但要和get_config_line同步
    #===================notice================================#
    $config{'intrusion_type_en'}    = $temp[0];
    $config{'intrusion_type_cn'}    = $temp[1];
    $config{'intrusion_type_note'}  = $temp[2];
    $config{'intrusion_type_level'} = $temp[4];
    #============自定义字段组装完毕===========================#
    return %config;
}

sub get_respond_type_hash($) {
    my $respond_type_ref = shift;
    my @respond_types = &read_conf_file( $respond_type_file );
    foreach my $type ( @respond_types ) {
        my @temp = split( ",", $type );
        $respond_type_ref->{$temp[1]} = $temp[0];
    }
}

sub get_rules_conf_hash($) {
    my $rules_conf_ref = shift;
    my @rules_conf_lines = &read_conf_file( $rules_conf_file );
    foreach my $rule ( @rules_conf_lines ) {
        my @temp = split( ",", $rule );
        $rules_conf_ref->{$temp[0]} = $rule;
    }
}

sub get_exceptions_hash() {
    $exceptions_ref = shift;
    my @exceptions_lines = &read_conf_file( $exceptions_file );
    foreach my $exception ( @exceptions_lines ) {
        my @temp = split( ",", $exception );
        $exceptions_ref->{$temp[0]} = $exception;
    }
}

sub create_respond_type_choices() {
    printf <<EOF
    <div id="respond_type_choices_back" class="popup-cover"></div>
    <div id="respond_type_choices" class="popup-mesg-box">
        <table class="rule-list popup-mesg-box-table">
            <thead class="popup-mesg-box-toolbar">
                <tr class="popup-mesg-box-thead">
                    <td>
                        请选择响应方式
                        <span class="tool-right">
                            <img class="close_box_icon" src="/images/close.gif" onclick="hide_respond_type_choices();"/>
                        </span>
                    </td>
                </tr>
            </thead>
            <tbody class="popup-mesg-box-tbody">
                <tr><td>
EOF
    ;
    my @respond_types = &read_conf_file( $respond_type_file );
    foreach my $item ( @respond_types ) {
        my @temp = split( ",", $item );
        my $label = $temp[0];
        my $value = $temp[1];
        my $item_id = $temp[1];
        printf <<EOF
        <span class="respond_type_item_box">
            <input type="radio" class="respond_type_item input-radio" name="respond_type_item" id="$item_id" value="$value"/>
            <label for="$item_id" class="label-for-radio">$label</label>
        </span>
EOF
    ;
    }

    printf <<EOF
                </td></tr>
            </tbody>
            <tfoot class="popup-mesg-box-toolbar">
                <tr class="popup-mesg-box-tfoot">
                    <td><input type="button" class="net_button" value="确定" onclick="change_respond_type();"/></td>
                </tr>
            </tfoot>
        </table>
    </div>
EOF
    ;
}

sub reset_values() {
    %par = ();
}

sub display_add() {
    printf <<EOF
    <div id="eliminate_edit_box_back" class="popup-cover"></div>
    <div id="eliminate_edit_box" class="popup-mesg-box" >
        <div>
            <form id="eliminate-form" name="ELIMINATE_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" enctype="multipart/form-data" >
                <input type="hidden" class="input-text" name="sid" value=""/>
                <input type="hidden" class="input-text" name="set_filename" value=""/>
                <table>
                    <tr class="">
                        <td colspan="2">
                            <div class="edit_box_header">
                                <span class="label-text">策略项排除IP编辑</span>
                            </div>
                        </td>
                    </tr>
EOF
    ;
    &create_display_add_lines(\%config);
    printf <<EOF
                </table>
                <table>
                    <tr class="add-div-footer">
                        <td class="add-div-footer-td">
                            <input class="net_button button-left" id="submit-button" type="button" value="更新" onclick="new_save_data('/cgi-bin/idps_strategy_file_config.cgi');"/>
                        </td>
                        <td class="add-div-footer-td">
                            <input class="net_button button-right" type="button"  value="撤销" onclick="new_cancel_edit_box();"/>
                        </td>
                    </tr>
                </table>
            </form>
        </div>
    </div>
EOF
;
}

sub config_add_item_data() {
    my @type_choices = ("by_src:基于源IP", "by_dst:基于目的IP", "none:不排除:selected");
    my %hash = (
        "display" => "排除方式",
        "name" => "eliminate_type",
        "type" => "select",
        "selections" => \@type_choices,
        "value" => "",
        "is_in_list" => 0,
        "width" => "10%",
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    my %hash = (
        "display" => "地址设置",
        "name" => "eliminate_ips",
        "type" => "textarea",
        "value" => "",
        "is_in_list" => 0,
        "width" => "25%",
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
}

sub create_display_add_lines(){
    my $total_count = @display_add_config_data;
    for(my $i = 0; $i < $total_count; $i++){
        my $item = @display_add_config_data[$i];
        #======先判断input是什么类型的，再创建相应的input,根据实际情况，这里的判断语句还要增加=========================###
        my $input;
        if($item->{'type'} eq 'text') {
            $input = '<input type="'.$item->{'type'}.'" name="'.$item->{'name'}.'" class="input-text" value="'.$item->{'value'}.'"/>';
        } elsif ($item->{'type'} eq 'checkbox'){
            #==判断默认是否要勾选==#
            my $checked = "";
            if($item->{'checked'}){
                $checked = 'checked="checked"';
            }
            $input = '<input type="'.$item->{'type'}.'" name="'.$item->{'name'}.'" class="input-checkbox" '.$checked.'/>';
        } elsif ($item->{'type'} eq 'radio'){
            my $selections = $item->{'selections'};
            my $id = 0;
            foreach my $selection (@$selections){
                $id++;
                my @temp = split(":", $selection);
                my $selected = "";
                if($temp[2]){
                    $selected = "checked";
                }
                $input .= '<input type="radio" name="'.$item->{'name'}.'" id="'.$item->{'name'}.$id.'" class="input-radio" value="'.$temp[0].'" '.$selected.' onclick="'.$item->{'onclick'}.'"/>';
                $input .= '<label for="'.$item->{'name'}.$id.'"  class="label-for-radio">'.$temp[1].'</label>';
            }
        } elsif ($item->{'type'} eq 'select'){
            my $multiple = "";
            my $class = "input-select";
            if($item->{'multiple'}){
                $multiple = 'multiple="multiple"';
                $class = "input-multi-select";
            }
            $input = '<select name="'.$item->{'name'}.'" '.$multiple.' class="'.$class.'">';
            my $selections = $item->{'selections'};
            foreach my $selection (@$selections){
                my @temp = split(":", $selection);
                my $selected = "";
                if($temp[2]){
                    $selected = "selected";
                }
                $input .= '<option value="'.$temp[0].'" '.$selected.'>'.$temp[1].'</option>';
            }
            $input .= '</select>';
        } elsif($item->{'type'} eq 'textarea') {
            $input = '<textarea name="'.$item->{'name'}.'" class="input-textarea">'.$item->{'value'}.'</textarea';
        }else{
            $input = '<input type="'.$item->{'type'}.'" name="'.$item->{'name'}.'" value="'.$item->{'value'}.'"/>';
        }
        #===============判断结束======================================================================================###
        my $bgcolor = "odd";
        if($i % 2){
            $bgcolor = "env";
        }
        printf <<EOF
            <tr class="$bgcolor">
                <td class="add-div-type">$item->{'display'}</td>
                <td>
                    $input
                </td>
            </tr>
EOF
        ;
    }
}

sub display_rule_list() {
    my $colspan = @table_display_fields + 2;
    printf <<EOF
    <div id="strategy_items_list_back" class="popup-cover"></div>
        <div id="strategy_items_list" class="list">
            <table id="strategy_items_list_table" class="rule-list">
                <thead class="toolbar">
                    <tr>
                        <td id="new-rule-list-head-td" colspan="$colspan">
                            <span class="tool-right">
                                <img class="close_box_icon" src="/images/close.gif" onclick="hide_strategy_items_list();"/>
                            </span>
                            <span class="opt-tools">
EOF
    ;
    printf <<EOF
                            </span>
                            <span class="opt-tools">
                                <input id="new-search-key" class="search-key-input" placeholder="输入关键字以查询..." onkeydown="new_search(event);"/>
                                <label for="new-search-key">
                                    <img id="new-search-button" class="search-button-img" src="../images/search16x16.png" onclick="new_refresh_page();"/>
                                </label>
                            </span>
                        </td>
                    </tr>
                    <tr id="new-rule-listbh">
                        <td id="new-rule-listbh-td">
                            <input type="checkbox" id="new-rule-listbhc" onclick="new_toggle_check();" />
                        </td>
EOF
    ;
                        #==========生成规则列表的表头配置参数见本文档开头部分=====
                        &fill_table_header();
                        #==========end============================================
    printf <<EOF
                        <td class="action">
                            活动/动作
                        </td>
                    </tr>
                </thead>
                <tbody id="new-rule-listb" class="rule-listb">
EOF
    ;
                    &create_strategy_items_list_body();
    printf <<EOF
                </tbody>
                <tfoot class="toolbar">
                    <tr>
                        <td id="new-rule-list-foot-td" colspan="$colspan">
                            <span class="opt-tools">
EOF
    ;
                            #&create_export_button();
    printf <<EOF
                            </span>
                            <span class="paging-tools">
                                <img id="first_page_icon" src="../images/first-page.gif" title="第一页" onclick="new_first_page()"/>
                                <img id="last_page_icon" src="../images/last-page.gif" title="上一页" onclick="new_last_page()"/>
                                <span class="paging-text">第<input id="new-current-page" class="paging-tool-text" type="text" onkeydown="new_input_control(this, event)"/>页,共<span id="new-total-page" class="paging-tool-text">xx</span>页</span>
                                <img id="next_page_icon" src="../images/next-page.gif" title="下一页" onclick="new_next_page()"/>
                                <img id="end_page_icon" src="../images/end-page.gif" title="最后一页" onclick="new_end_page()"/>
                                <img id="refresh_icon" src="../images/refresh.png" onclick="new_refresh_page()"/>
                                <span class="paging-text">
                                    显示
                                    <span id="new-from-num" class="paging-tool-text">xx</span>
                                    -
                                    <span id="new-to-num" class="paging-tool-text">xx</span>
                                    条,共
                                    <span id="new-total-num" class="paging-tool-text">xx</span>条</span>
                            </span>
                         </td>
                    </tr>
                </tfoot>
            </table>
        </div>
EOF
    ;
}

sub create_strategy_items_list_body() {
    my $page_size = 15;
    my $main_body = "";
    for( my $i = 0; $i < $page_size; $i++ ) {
        if ( $i % 2 == 0 ){
            $main_body .= '<tr class="even-num-line">';
        } else {
            $main_body .= '<tr class="odd-num-line">';
        }
        $main_body .= '<td class="rule-listbc">';
        $main_body .= '&nbsp';
        $main_body .= '</td>';
        for ( my $j = 0; $j < 5; $j++) {
            $main_body .= '<td>&nbsp';
            $main_body .= '</td>';
        }

        $main_body .= '<td class="action">';
        $main_body .= '&nbsp';
        $main_body .= '</td>';
    }
    print "$main_body";
}

sub create_selected_operation_button() {
    my $enabled_exists = 0;
    foreach my $item (@display_add_config_data){
        if($item->{'name'} eq 'enabled'){
            #判断有没有启用禁用字段
            $enabled_exists = 1;
            last;
        }
    }
    #===========批量操作功能按钮=====================#
    #   如果存在启用禁用属性，就创建批量启用禁用功能
    #================================================#
    if($enabled_exists) {
        &create_enable_selected_button();
        &create_disable_selected_button();
    }
    &create_delete_selected_button();
}

sub create_enable_selected_button() {
    printf <<EOF
    <button id="enable-selected" class="imaged-button" onclick="enable_selected_items();">
        <img class="button-image" src="../images/on.png" /><span class="button-text" >启用选中</span>
    </button>
EOF
    ;
}

sub create_disable_selected_button() {
    printf <<EOF
    <button id="disable-selected" class="imaged-button" onclick="disable_selected_items();">
        <img class="button-image" src="../images/off.png" /><span class="button-text" >禁用选中</span>
    </button>
EOF
    ;
}

sub create_delete_selected_button() {
    printf <<EOF
    <button id="delete-selected" class="imaged-button" onclick="delete_selected_items();">
        <img class="button-image" src="../images/delete.png" /><span class="button-text" >删除选中</span>
    </button>
EOF
    ;
}

sub create_export_button() {
    printf <<EOF
    <!--<form class="export-all-form" method="post" ACTION="$ENV{'SCRIPT_NAME'}">-->
    <a class="export-all-link" href="$ENV{'SCRIPT_NAME'}?ACTION=export_data">
        <button id="export-all" class="imaged-button" name="ACTION" value="export_data">
                <img class="button-image" src="../images/download.png" /><span class="button-text" >导出全部</span>
        </button>
    </a>
    <!--</form>-->
EOF
    ;
}

sub get_display_fields(){
    #=====ID号信息======#
    push( @table_display_fields,        "ID号" );
    push( @table_display_fields_name,   "sid" );
    push( @table_display_fields_widths, "10%" );
    #=====危险级别信息======#
    push( @table_display_fields,        "危险级别" );
    push( @table_display_fields_name,   "risk_level" );
    push( @table_display_fields_widths, "20%" );
    #=====说明信息======#
    push( @table_display_fields,        "说明" );
    push( @table_display_fields_name,   "summary" );
    push( @table_display_fields_widths, "30%" );
    #=====响应方式信息======#
    push( @table_display_fields,        "排除方式" );
    push( @table_display_fields_name,   "eliminate_type_text" );
    push( @table_display_fields_widths, "10%" );
    #=====响应方式信息======#
    push( @table_display_fields,        "响应方式" );
    push( @table_display_fields_name,   "respond_type_text" );
    push( @table_display_fields_widths, "10%" );
}

sub fill_table_header(){
    my $cols = @table_display_fields;
    for(my $i = 0; $i < $cols; $i++){
        print '<td width="'.$table_display_fields_widths[$i].'">'.$table_display_fields[$i].'</td>';
    }
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