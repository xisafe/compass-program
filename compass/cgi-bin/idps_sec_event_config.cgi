#!/usr/bin/perl

#===============================================================================#
#
# DESCRIPTION: 入侵防护->策略配置->二次事件配置页面
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2014.05.26
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
my $respond_type_file;          #存储响应类型的文件，此文件为系统内置
my $export_file;                #导出时使用
my $export_filename;            #导出时使用
my $import_error_file;          #导入出错时使用
my $imported_tag;               #导入时使用
my $need_reload;                #需要重新加载的标识文件
my $restart;                    #应用重启的程序,根据实际情况填写
my $get_icmp_sid_cmd;           #获取保护icmp协议的sid号
my $extraheader;                #存放用户自定义JS
my %par;                        #存放传过来的数据的哈希
my %query;                      #存放通过get方法传过来的数据
my %respond_type_hash;          #存放响应方式的哈希，系统内置数据
my %risk_level_hash;            #存放危险级别的哈希，系统内置数据
my %icmp_protocol_hash;         #存放有icmp协议的sid号的哈希
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
    $custom_dir         = '/ips/sec_event';
    $conf_dir           = "${swroot}".$custom_dir;
    $conf_file          = $conf_dir.'/config';
    $respond_type_file  = "/etc/efw/ips/respond_type";

    $need_reload        = $conf_dir.'/sec_event_need_reload';
    $import_error_file  = $conf_dir.'/sec_event_import_error_file';
    $imported_tag       = $conf_dir.'/sec_event_imported_tag';
    $export_file        = '/tmp/sec_event.csv';
    $export_filename    = 'sec_event.csv';

    $restart            = '/usr/local/bin/restartsecondevent';
    $get_icmp_sid_cmd   = './idps_rules_helper.py -f "/var/efw/ips/rules/system_##_/var/efw/ips/rules/custom"';

    #===存放用户自定义JS,CSS：一般先用户定义相应页面的~init.js,然后引用template_add_list.js、template_add_list.css===#
    #===也可拷贝template_add_list.js、template_add_list.css再进行自定义更改,不建议这样做,这样不适合后期维护和扩展====#
    $extraheader        = '<link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />
                            <link rel="stylesheet" type="text/css" href="/include/idps_sec_event_config.css" />
                            <link rel="stylesheet" type="text/css" href="/include/idps_strategies_config.css" />
                            <script language="JavaScript" src="/include/idps_sec_event_config.js"></script>
                            <script language="JavaScript" src="/include/template_add_list.js"></script>
                            <script language="JavaScript" src="/include/idps_strategy_choices.js"></script>
                            <script language="JavaScript" src="/include/idps_strategy_choices_paging.js"></script>';
    #================================end=============================================================================#

    &make_file();#检查要存放规则的文件夹和文件是否存在，不存在就创建，此行不要删除或更改

    &get_respond_type_hash( \%respond_type_hash );
    &get_risk_level_hash( \%risk_level_hash );
    &get_icmp_protocol_hash( \%icmp_protocol_hash );

    #========配置添加模块的数据================================#
    #   添加模块的生成，主要是数据的配置，请按照例子配置数据
    #==========================================================#
    &config_add_item_data();#到这个函数中去配置
    #========配置数据end=======================================#

    &get_display_fields();#根据配置，生成需要的数据，此行不要删掉或更改
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
    my @temp = split(/,/, $line_content);
    my $fields_length =  @display_add_config_data;
    #===================notice==============================
    #  传入规则字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回哈希中的值
    #  也可以自定义,但要和get_config_line同步
    #===================notice==============================
    $config{'name'}             = $temp[0];
    $config{'event_name'}             = $temp[0];
    $config{'summary'}          = $temp[1];
    $config{'level'}            = $temp[2];
    $config{'sid'}              = $temp[3];
    $config{'src_ip'}           = $temp[4];
    $config{'src_ip_value'}     = $temp[5];
    $config{'dst_ip'}           = $temp[6];
    $config{'dst_ip_value'}     = $temp[7];
    $config{'src_port'}         = $temp[8];
    $config{'src_port_value'}   = $temp[9];
    $config{'dst_port'}         = $temp[10];
    $config{'dst_port_value'}   = $temp[11];
    $config{'min_count'}        = $temp[12];
    $config{'interval'}         = $temp[13];
    $config{'respond_type'}     = $temp[14];
    $config{'enabled'}          = $temp[15];

    $config{'level_text'}           = $risk_level_hash{$config{'level'}};
    $config{'respond_type_text'}    = $respond_type_hash{$config{'respond_type'}};
    if( $icmp_protocol_hash{$config{'sid'}} ){
        $config{'protocol'} = "icmp";
    } else {
        $config{'protocol'} = "other";
    }
    #============自定义字段组装完毕=========================
    return %config;
}

sub get_config_line($){
    my $data = shift;#传入一个哈希
    my @data_arr;
    #===================notice==============================
    #  配置好的规则字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回规则
    #  也可以自定义,但要和get_config_hash同步
    #===================notice==============================
    push( @data_arr, $data->{'name'} );
    push( @data_arr, $data->{'summary'} );
    push( @data_arr, $data->{'level'} );
    push( @data_arr, $data->{'sid'} );
    push( @data_arr, $data->{'src_ip'} );
    push( @data_arr, $data->{'src_ip_value'} );
    push( @data_arr, $data->{'dst_ip'} );
    push( @data_arr, $data->{'dst_ip_value'} );
    push( @data_arr, $data->{'src_port'} );
    push( @data_arr, $data->{'src_port_value'} );
    push( @data_arr, $data->{'dst_port'} );
    push( @data_arr, $data->{'dst_port_value'} );
    push( @data_arr, $data->{'min_count'} );
    push( @data_arr, $data->{'interval'} );
    push( @data_arr, $data->{'respond_type'} );
    push( @data_arr, $data->{'enabled'} );
    #============自定义字段组装完毕=========================
    return join ",", @data_arr;
}

sub handle_submited_data() {
    #===提交上来的值，尤其是textarea里面的内容===============#
    #===要进行空行和换行的处理，可以自行进行相应的处理=======#
    $par{'summary'} = &process_empty_lines( $par{'summary'} );
    if( $par{'line'} ne '' ) {
        $par{'name'} = $par{'event_name'};
    }

    if( $par{'protocol'} eq 'icmp' ) {
        $par{'src_port'}        = 'none';
        $par{'src_port_value'}  = '';
        $par{'dst_port'}        = 'none';
        $par{'dst_port_value'}  = '';
    }

    if( $par{'src_port'} eq 'none' ) {
        $par{'src_port_value'}  = '';
    }

    if($par{'dst_port'} eq 'none' ) {
        $par{'dst_port_value'}  = '';
    }
    #===处理完毕=============================================#
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

sub get_import_line($) {
    my $line_content = shift;
    #===========在此可以配置要导入的数据===================
    my $new_line = $line_content;

    #====end===============================================
    return $new_line;
}

sub import_data_check($) {
    my $res = shift;
    my @lines = @$res;
    my $total_count = @lines;
    my @new_lines;
    my $if_can = 0;
    my @errormsg;
    my $error_length = @errormsg;
    my %exit_lines;

    #===第一步检查每个字段的正确性===#
    for( my $i = 0; $i < $total_count; $i ++ ) {
        my $present_line = $i + 1;
        my @temp = split(",", $line[$i]);
    }

    #===第二步检查重复===============#
    if(@errormsg) {
        $if_can = 0;
        return ($if_can, \@errormsg, \@new_lines);
    } else {
        for ( my $i = 0; $i < $total_count; $i ++ ) {
            my $feature = @lines[$i];#这里可以定义不能重复的特征
            if(%exit_lines->{$feature}) {
                my $repeat_line = %exit_lines->{$feature};
                my $present_line = $i + 1;
                push(@errormsg, "第".$present_line."行与第".$repeat_line."行重复");
            } else {
                %exit_lines->{$feature} = $i + 1;
            }
        }
    }

    #===第三步根据错误情况决定是否组装数据===#
    if(!@errormsg) {
        #=====组装行====#
        @new_lines = &get_import_lines(\@lines);
        $if_can = 1;
    } else {
        $if_can = 0;
    }

    return ($if_can, \@errormsg, \@new_lines);
}

sub get_import_lines($) {
    my $src_lines = shift;
    my @new_lines = ();
    foreach my $line (@$src_lines) {
        push(@new_lines, &get_import_line($line));
    }
    return @new_lines;
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    #==如果不是导出数据，都打印普通http头部==#
    if($action ne 'export_data' && $query_action ne 'export_data') {
        &showhttpheaders();
    }
    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==下载配置数据==#
        &load_data();
    } elsif($action eq 'apply_data'){
        #==应用更改==#
        &apply_data();
    } elsif($action eq 'save_data'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &save_data();
    } elsif($action eq 'enable_data'){
        #==启用数据(可多条同时启用)==#
        &enable_data();
    } elsif($action eq 'disable_data'){
        #==禁用数据(可多条同时禁用)==#
        &disable_data();
    } elsif($action eq 'delete_data'){
        #==删除数据(可多条同时删除)==#
        &delete_data();
    } elsif($action eq 'export_data'){
        #==导出数据,可以导出特定几列的数据==#
        &export_data();
    } elsif($action eq 'import_data'){
        #==导入数据,可以导入特定几列的数据==#
        &import_data();
        &show_page();
    } elsif($action eq 'import_error_check') {
        #==检查导入的错误信息(多条)，并返回给用户==#
        &import_error_check();
    } elsif($action eq 'edit_respond_type') {
        #==编辑响应类型==#
        &edit_respond_type();
    }  else {
        if($query_action eq 'export_data') {
            #==导出数据,可以导出特定几列的数据==#
            &export_data();
        }
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}
sub show_page() {
    &openpage("二次事件配置", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_add();
    # &display_upload();
    &display_rule_list();
    &display_strategy_choices_list();
    &closebigbox();
    &closepage();
}

sub import_error_check() {
    #====检查导入错误存在4种状态====================#
    # 1.上次用户操作导入了数据，并且成功
    # 2.上次用户操作导入了数据，并且失败
    # 3.上次用户操作没有导入数据，
    #   系统没有最近一次导入的错误信息
    # 4.上次用户操作没有导入数据，
    #   系统有最近一次导入的错误信息，要返回给用户
    #====检查导入错误存在4种状态====================#
    my @errormessage = read_conf_file($import_error_file);
    if(-e $imported_tag){
        #说明上次用户操作导入了数据
        if (@errormessage) {
            &send_status(1, 0, "导入失败", \@errormessage);
        } else {
            &send_status(0, 1, "导入成功", "");
        }
        &clear_imported_tag();#清除标记，表示已通知用户上次导入情况
    } else {
        if (@errormessage) {
            &send_status(-1, 0, "无数据导入", \@errormessage);
        } else {
            &send_status(-1, 0, "无数据导入", \@errormessage);
        }
    }
}

sub create_imported_tag() {
    system("touch $imported_tag");
}

sub clear_imported_tag() {
    system("rm $imported_tag");
}

sub create_needreload_tag() {
    system("touch $need_reload");
}

sub import_data(){
    my $cgi = new CGI; 
    my $upload_filehandle = $cgi->param('import_file');
    my @lines = ();
    while ( <$upload_filehandle> )
    {
        chomp $_;
        push(@lines, encode("utf8", decode("gb2312", $_)));
    }
    #===第一步去掉多余字符===#
    for my $line (@lines) {
        #==用户的工作环境不定==========================#
        #==导入的数据可能在原来导出数据后更改过========#
        #==如果在window下更改过，数据的回车换行要去掉==#
        #==不然影响unix系统后台程序====================#
        $line =~ s/\r//g;
        $line =~ s/\n//g;
        chomp($line);
    }
    #===第二步，检查能否导入，如果能，将返回配置好的数据===#
    my ($if_can, $errormsg, $save_lines) = &import_data_check(\@lines);
    if($if_can) {
        &save_config_file($save_lines, $conf_file);
        &create_needreload_tag();
    }
    &create_imported_tag();#做一个标记，表示上一次用户操作导入过数据
    &save_config_file($errormsg, $import_error_file);#每次导入都将错误消息(无论是否为空)写入，覆盖原来的错误消息
}

sub export_data() {
    my $file = &generate_download_file();
    if( -e "$file"){
        open(DLFILE, "<$file") || Error('open', "$file");  
        @fileholder = <DLFILE>;  
        close (DLFILE) || Error ('close', "$file"); 
        print "Content-Type:application/x-download\n";  
        print "Content-Disposition:attachment;filename=$export_filename\n\n";
        print @fileholder;
        exit;
    }
    else{
        print "Content-type:text/html\n\n";
        printf <<EOF
            <html>
                <head>
                    <title>The file doesn't exist.</title>
                </head>
                <body>
                    <center>
                        <h1>The file does not exist.</h1>
                    </center>
                </body>
            </html>    
EOF
        ;
        exit;
    }
}

sub generate_download_file() {
    my $download_file = $export_file;
    my @lines = read_conf_file($conf_file);
    my @new_lines;
    foreach my $line (@lines) {
        #===在get_export_line面去配置导出的数据==#
        my $new_line = &get_export_line($line);
        push(@new_lines, encode("gb2312",decode('utf8', $new_line)));
    }
    save_config_file(\@new_lines, $download_file);
    return $download_file;
}

sub apply_data() {
    my ( $status, $reload, $mesg, $detail_mesg ) = ( -1, 0, "","" );
    $status = system($restart);#重启服务
    if( $status == 0 ) {
        $mesg = "规则应用成功";
        system("rm $need_reload");
    } else {
        $status = -1;
        $reload = 1;
        $mesg = "规则应用异常";
    }
    send_status( $status, $reload, $mesg, $detail_mesg );
}

sub load_data(){
    my @content_array = ();
    my $load_data_cmd;
    my @lines = read_conf_file($conf_file);
    my $record_num = @lines;
    my $total = 0;
    my $search = $par{'search'};
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
        $conf_data{'line'} = $i;
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
    &handle_submited_data();

    #==第二步到&get_config_line(\%par)进行处理=====#

    #==第三步保存==========================#
    my ($status, $reload, $mesg) = &save_conf_line($par{'line'},&get_config_line(\%par));
    &reset_values();
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 0 表示不重新应用，其他表示应用
    # => $mesg: 相关错误的消息
    #===========================================#
    &send_status($status, $reload, $mesg, $mesg);
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

sub save_conf_line($$) {
    my $line = shift;
    my $line_content = shift;

    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 0 表示不重新应用，其他表示应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $reload, $mesg) = (-1, 0, "");
    my @lines = read_conf_file($conf_file);
    if($line eq ''){
        #新添加一行
        #先检查能否添加
        my ($if_can, $errormsg) = &save_line_check($line_content, \@lines);
        if($if_can){
            push(@lines, $line_content);
            $status = 0;
            &create_needreload_tag();
            $reload = 1;
            $mesg = "添加成功";
        }else{
            $status = -1;
            $reload = 0;
            $mesg = $errormsg;
        }
    }else{
        if (! @lines[$line]) {
            $status = -1;
            $reload = 0;
            $mesg = "不存在要编辑的数据,请稍后重试";
            return ($status, $reload, $mesg);
        }
        #更新修改
        #先检查能否修改
        my ($if_can, $errormsg) = &update_line_check($line, $line_content, \@lines);
        if($if_can){
            @lines[$line] = $line_content;
            $status = 0;
            &create_needreload_tag();
            $reload = 1;
            $mesg = "更新成功";
        }else{
            $status = -1;
            $reload = 0;
            $mesg = $errormsg;
        }
    }
    &save_conf_file(\@lines, $conf_file);
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

    my ($status, $reload, $mesg, $succeeded_num, $fail_num) = (0, 0, "", 0, 0);

    my @lines = read_conf_file($conf_file);
    my $record_num = @lines;

    for(my $i = 0; $i < $record_num; $i++){
        if( $par{$i} eq "$i" ) {
            my %data = &get_config_hash(@lines[$i]);
            $data{'enabled'} = $enable;
            my $line_content = &get_config_line(\%data);
            @lines[$i] = $line_content;
            $succeeded_num++;
        }
    }
    &save_conf_file(\@lines, $conf_file);
    #需要重新应用
    if($succeeded_num) {
        $reload = 1;
        &create_needreload_tag();
    }
    send_status($status, $reload, "成功$opt$succeeded_num条规则", "成功$opt$succeeded_num条规则");
}

sub delete_data() {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 0 表示不重新应用，其他表示应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $reload, $mesg, $succeeded_num, $fail_num) = (0, 0, "", 0, 0);
    my @fail_mesg = ();

    my @lines = read_conf_file($conf_file);
    my @new_lines;
    my $record_num = @lines;

    for(my $i = 0; $i < $record_num; $i++){
        if ( $par{$i} eq "$i" ) {
            #===要删除该行==================#
            #===先检查检查能否被删除===#
            my ($if_can, $errormsg) = &del_line_check( $i, $lines[$i], \@lines);
            if($if_can){
                $succeeded_num++;
            }else{
                push( @new_lines, $lines[$i] );#不能删除
                push( @fail_mesg, $errormsg );
                $fail_num++;
            }
        } else {
            #===不删除该行==================#
            push(@new_lines, $lines[$i]);
        }
    }
    &save_conf_file(\@new_lines, $conf_file);
    #需要重新应用
    if($succeeded_num) {
        $reload = 1;
        &create_needreload_tag();
    }
    if( $fail_num ) {
        $mesg = "成功删除$succeeded_num条规则,失败$fail_num条规则";
        # $mesg = "成功删除$succeeded_num条规则";
    } else {
        $mesg = "成功删除$succeeded_num条规则";
    }
    send_status($status, $reload, $mesg, \@fail_mesg);
}

sub edit_respond_type() {
    my ($status, $reload, $mesg, $succeeded_num, $fail_num) = (0, 0, "", 0, 0);

    my @lines = read_conf_file($conf_file);
    my $record_num = @lines;

    for(my $i = 0; $i < $record_num; $i++){
        if( $par{$i} eq "$i" ) {
            my %data = &get_config_hash(@lines[$i]);
            $data{'respond_type'} = $par{'respond_type'};
            my $line_content = &get_config_line(\%data);
            @lines[$i] = $line_content;
            $succeeded_num++;
        }
    }
    my @conf_lines;
    foreach my $key ( sort keys %rules_conf_hash ) {
        push( @conf_lines, $rules_conf_hash{$key} );
    }
    &save_conf_file( \@lines, $conf_file );
    #需要重新应用
    if($succeeded_num) {
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
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}

sub get_respond_type_hash($) {
    my $respond_type_ref = shift;
    my @respond_types = &read_conf_file( $respond_type_file );
    foreach my $type ( @respond_types ) {
        my @temp = split( ",", $type );
        $respond_type_ref->{$temp[1]} = $temp[0];
    }
}

sub get_risk_level_hash($) {
    my $risk_level_hash_ref = shift;
    $risk_level_hash_ref->{'1'} = "高";
    $risk_level_hash_ref->{'2'} = "中";
    $risk_level_hash_ref->{'3'} = "中";
    $risk_level_hash_ref->{'4'} = "低";
    return;
}

sub get_icmp_protocol_hash($) {
    my $icmp_protocol_hash_ref = shift;
    my $sids_str = `$get_icmp_sid_cmd`;#返回的多个sid以#隔开
    chomp $sids_str;
    my @sids = split( /\#/, $sids_str );
    foreach my $sid ( @sids ) {
        $icmp_protocol_hash_ref->{$sid} = 1;
    }
    return;
}

sub get_respond_type_array($) {
    my $respond_type_ref = shift;
    my @respond_types = &read_conf_file( $respond_type_file );
    foreach my $type ( @respond_types ) {
        my @temp = split( ",", $type );
        if( $temp[2] eq 'on' ) {
            if( $temp[1] eq 'alert' ) {
                push( @$respond_type_ref, "$temp[1]:$temp[0]:checked" );
            } else {
                push( @$respond_type_ref, "$temp[1]:$temp[0]" );
            }
        }
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
        if( $temp[2] ne 'on' ) {
            next;
        }
        my $label = $temp[0];
        my $value = $temp[1];
        my $item_id = $temp[1];
        printf <<EOF
        <span class="respond_type_item_box">
            <input type="radio" class="respond_type_item input-radio" name="respond_type_item" id="$item_id" value="$value" onclick="select_respond_type();"/>
            <label for="$item_id" id="label_for_$item_id" class="label-for-radio">$label</label>
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
    &create_mesg_boxs();
    &create_respond_type_choices();
    printf <<EOF
    <div id="add-div" >
        <div id="add-div-header">
            <span class="add-header-title">
                <img class="label-image" src="/images/add.png"/>
                <span id="add-title" class="label-text">添加二次事件</span>
            </span>
        </div>
        <div id="add-div-content">
            <form id="template-form" name="TEMPLATE_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" enctype="multipart/form-data" >
                <input type="hidden" id="line-num" name="line" value=""/>
                <input type="hidden" class="input-text" name="protocol" value=""/>
                <input type="hidden" class="input-text" name="event_name" value=""/>
                <table>
EOF
    ;
    &create_display_add_lines(\%config);
    printf <<EOF
                </table>
                <table>
                    <tr class="add-div-footer">
                        <td class="add-div-footer-td">
                            <input class="net_button button-left" id="submit-button" type="button" value="添加" onclick="save_data('$ENV{SCRIPT_NAME}');"/>
                        </td>
                        <td class="add-div-footer-td">
                            <input class="net_button button-right" type="button"  value="撤销" onclick="cancel_edit_box();"/>
                            <span class="tips-text">* 表示必填项</span>
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
    my %hash = (
        "display"    => "名称 *",
        "name"       => "name",
        "type"       => "text",
        "value"      => "",
        "is_in_list" => 1,
        "width"      => "15%",
        "class"      => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "说明",
        "name" => "summary",
        "type" => "textarea",
        "value" => "",
        "is_in_list" => 1,#配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "35%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);

    my @level_choices = ("1:高", "2:中", "4:低:checked");
    my %hash = (
        "display" => "危险级别",
        "name" => "level",
        "type" => "radio",
        "selections" => \@level_choices,
        "value" => "",
        "is_in_list" => 1,#配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "15%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "risk_level",
    );
    push(@display_add_config_data, \%hash);

    my %sid_extend = (
        "name" => "sid_button",
        "type" => "button",
        "value" => "选择策略项",
        "onclick" => "choose_strategy_item_id();",
        "class" => "net_button"
    );
    my %hash = (
        "display"       => "匹配的策略项 *",
        "name"          => "sid",
        "type"          => "text",
        "value"         => "",
        "is_in_list"    => 0,
        "width"         => "15%",
        "onfocus"       => "choose_strategy_item_id();",
        "class"         => "",
        "extend"        => \%sid_extend
    );
    push(@display_add_config_data, \%hash);

    my @src_ip_choices = ("none:不考虑此项:selected", "specify:指定IP");
    my %src_ip_extend = (
        "name" => "src_ip_value",
        "type" => "text",
        "value" => "",
    );
    my %hash = (
        "display" => "源IP",
        "name" => "src_ip",
        "type" => "select",
        "selections" => \@src_ip_choices,
        "value" => "",
        "is_in_list" => 0,
        "width" => "5%",
        "class" => "specify_ip",
        "tr_class" => "specify_ip_tr",
        "extend" => \%src_ip_extend,
        "toggle" => "change_type(this)"
    );
    push(@display_add_config_data, \%hash);

    my @dst_ip_choices = ("none:不考虑此项:selected", "specify:指定IP");
    my %dst_ip_extend = (
        "name" => "dst_ip_value",
        "type" => "text",
        "value" => "",
    );
    my %hash = (
        "display" => "目的IP",
        "name" => "dst_ip",
        "type" => "select",
        "selections" => \@dst_ip_choices,
        "value" => "",
        "is_in_list" => 0,
        "width" => "5%",
        "class" => "specify_ip",
        "tr_class" => "specify_ip_tr",
        "extend" => \%dst_ip_extend,
        "toggle" => "change_type(this)"
    );
    push(@display_add_config_data, \%hash);

    my @src_port_choices = ("none:不考虑此项:selected", "specify:指定端口");
    my %src_port_extend = (
        "name" => "src_port_value",
        "type" => "text",
        "value" => "",
    );
    my %hash = (
        "display" => "源端口",
        "name" => "src_port",
        "type" => "select",
        "selections" => \@src_port_choices,
        "value" => "",
        "is_in_list" => 0,
        "width" => "5%",
        "class" => "specify_port",
        "tr_class" => "specify_port_tr",
        "extend" => \%src_port_extend,
        "toggle" => "change_type(this)"
    );
    push(@display_add_config_data, \%hash);

    my @dst_port_choices = ("none:不考虑此项:selected", "specify:指定端口");
    my %dst_port_extend = (
        "name" => "dst_port_value",
        "type" => "text",
        "value" => "",
    );
    my %hash = (
        "display" => "目的端口",
        "name" => "dst_port",
        "type" => "select",
        "selections" => \@dst_port_choices,
        "value" => "",
        "is_in_list" => 0,
        "width" => "5%",
        "class" => "specify_port",
        "tr_class" => "specify_port_tr",
        "extend" => \%dst_port_extend,
        "toggle" => "change_type(this)"
    );
    push(@display_add_config_data, \%hash);

    my %hash = (
        "display"    => "最小累积次数 *",
        "name"       => "min_count",
        "type"       => "text",
        "value"      => "",
        "is_in_list" => 0,
        "width"      => "10%",
        "class"      => "",
    );
    push(@display_add_config_data, \%hash);

    my %hash = (
        "display"    => "时间间隔 *",
        "name"       => "interval",
        "type"       => "text",
        "value"      => "",
        "is_in_list" => 0,
        "width"      => "10%",
        "class"      => "",
    );
    push(@display_add_config_data, \%hash);

    my @respond_type_choices;
    &get_respond_type_array( \@respond_type_choices );
    my %hash = (
        "display" => "响应方式",
        "name" => "respond_type",
        "type" => "radio",
        "selections" => \@respond_type_choices,
        "onclick" => "",
        "is_in_list" => 1,
        "width" => "15%",
        "class" => "respond_type_choice_item",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "启用",#此字段可以改为同义的其他词
        "name" => "enabled",#如果需要启用禁用功能，此字段的名字不能更改，否则启用禁用按钮不能使用
        "type" => "checkbox",
        "checked" => 1,#不为0时表示默认选中
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
            # if( $item->{'name'} eq 'sid ') {
            #     $input = '<input type="'.$item->{'type'}.'" name="'.$item->{'name'}.'" class="input-text" value="'.$item->{'value'}.'" onfocus="'.$item->{'onfocus'}.'"/>';
            # } else {
            #     $input = '<input type="'.$item->{'type'}.'" name="'.$item->{'name'}.'" class="input-text" value="'.$item->{'value'}.'"/>';
            # }
            $input = '<input type="'.$item->{'type'}.'" name="'.$item->{'name'}.'" class="input-text" value="'.$item->{'value'}.'" onfocus="'.$item->{'onfocus'}.'"/>';
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
                $input .= '<input type="radio" name="'.$item->{'name'}.'" id="'.$temp[0].'" class="input-radio '.$item->{'class'}.'" value="'.$temp[0].'" '.$selected.' onclick="'.$item->{'onclick'}.'"/>';
                $input .= '<label for="'.$temp[0].'"  class="label-for-radio">'.$temp[1].'</label>';
            }
        } elsif ($item->{'type'} eq 'select'){
            my $multiple = "";
            my $class = "input-select";
            if( $item->{'extend'} ) {
                $class .= " ref_extend";
            }
            if($item->{'multiple'}){
                $multiple = 'multiple="multiple"';
                $class = "input-multi-select";
            }
            $input = '<select name="'.$item->{'name'}.'" '.$multiple.' class="'.$class.'" onkeyup="'.$item->{'toggle'}.'" onchange="'.$item->{'toggle'}.'">';
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

            if( $item->{'extend'} ) {
                #===此页面专用，用户创建单选框后面的input text框===#
                my $extend = $item->{'extend'};
                $input .= '<span class="extend_text hidden"><input type="'.$extend->{'type'}.'" name="'.$extend->{'name'}.'" class="input-text '.$item->{'class'}.'" value="'.$extend->{'value'}.'"/></span>';
            }
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
            <tr class="$bgcolor $item->{'tr_class'}">
                <td class="add-div-type">$item->{'display'}</td>
                <td>
                    $input
                </td>
            </tr>
EOF
        ;
    }
}

sub display_upload(){
    printf <<EOF
    <div id="add-div-upload" class="add-panel">
        <div id="add-div-header-upload" class="add-header">
            <span id="upload-header-left" class="add-header-title">
                <img class="label-image" src="/images/add.png"/>
                <span class="label-text">导入规则</span>
            </span>
            <span id="upload-header-right" class="tips-text">
                <img id="import_error_mesg" src="/images/read_note.png" title="点击查看导入的错误信息" onclick="import_error_read();"/>
            </span>
        </div>
        <div id="add-div-content-upload" class="add-content">
            <form id="template-form-upload" name="TEMPLATE_FORM_UPLOAD" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}' onsubmit="return check_import();">
                <table>
                    <tbody>
                        <tr class="odd">
                            <td class="add-div-type">选择文件*</td>
                            <td>
                                <input type="file" id="import_file" name="import_file"/>
                                <input type="hidden" name="ACTION" value="import_data"/>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <table>
                    <tr class="add-div-footer">
                        <td class="add-div-footer-td">
                            <input class="net_button button-left" id="submit-button" type="submit" value="导入"/>
                        </td>
                        <td class="add-div-footer-td">
                            <input class="net_button button-right" type="button"  value="撤销" onclick="cancel_import_box();"/>
                            <span class="tips-text">* 表示必填项</span>
                        </td>
                    </tr>
                </table>
            </form> 
        </div>
    </div>
EOF
    ;
}

sub display_rule_list() {
    my $colspan = @table_display_fields + 2;
    printf <<EOF
    <div class="list">
            <table class="rule-list">
                <thead class="toolbar">
                    <tr>
                        <td id="rule-list-head-td" colspan="$colspan">
                            <span class="opt-tools">
EOF
    ;
                       &create_selected_operation_button();
    printf <<EOF
                            </span>
                            <span class="search">
                                <input id="search-key" class="search-key-input" placeholder="输入关键字以查询..." onkeydown="search(event);"/>
                                <label for="search-key">
                                    <img id="search-button" class="search-button-img" src="../images/search16x16.png" onclick="refresh_page();"/>
                                </label>
                            </span>
                        </td>
                    </tr>
                    <tr id="rule-listbh">
                        <td id="rule-listbh-td">
                            <input type="checkbox" id="rule-listbhc" onclick="toggle_check();" />
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
                <tbody id="rule-listb" class="rule-listb">
                </tbody>
                <tfoot class="toolbar">
                    <tr>
                        <td id="rule-list-foot-td" colspan="$colspan">
                            <span class="opt-tools">
EOF
    ;
                            #&create_export_button();
    printf <<EOF
                            </span>
                            <span class="paging-tools">
                                <img id="first_page_icon" src="../images/first-page.gif" title="第一页" onclick="first_page()"/>
                                <img id="last_page_icon" src="../images/last-page.gif" title="上一页" onclick="last_page()"/>
                                <span class="paging-text">第<input id="current-page" class="paging-tool-text" type="text" onkeydown="input_control(this, event)"/>页,共<span id="total-page" class="paging-tool-text">xx</span>页</span>
                                <img id="next_page_icon" src="../images/next-page.gif" title="下一页" onclick="next_page()"/>
                                <img id="end_page_icon" src="../images/end-page.gif" title="最后一页" onclick="end_page()"/>
                                <img id="refresh_icon" src="../images/refresh.png" onclick="refresh_page()"/>
                                <span class="paging-text">
                                    显示
                                    <span id="from-num" class="paging-tool-text">xx</span>
                                    -
                                    <span id="to-num" class="paging-tool-text">xx</span>
                                    条,共
                                    <span id="total-num" class="paging-tool-text">xx</span>条</span>
                            </span>
                         </td>
                    </tr>
                </tfoot>
            </table>
        </div>
EOF
    ;
}

sub display_strategy_choices_list() {
    my $colspan = 3;
    printf <<EOF
        <div id="strategy_choices_list_back" class="popup-cover"></div>
        <div id="strategy_choices_list" class="list">
            <table id="strategy_choices_list_table" class="rule-list">
                <thead class="toolbar">
                    <tr class="close">
                        <td colspan="$colspan">
                            <span class="tool-right">
                                <img class="close_box_icon" src="/images/close.gif" onclick="hide_strategy_choices_list();"/>
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <td id="new-rule-list-head-td" colspan="$colspan">
                            <span class="opt-tools">
                            </span>
                            <span class="tool-right">
                                <input id="new-search-key" class="search-key-input" placeholder="输入关键字以查询..." onkeydown="new_search(event);"/>
                                <input id="load_set_filename" type="hidden" name="load_set_filename"/>
                                <label for="new-search-key">
                                    <img id="new-search-button" class="search-button-img" src="../images/search16x16.png" onclick="new_refresh_page();"/>
                                </label>
                            </span>
                        </td>
                    </tr>
                    <tr id="new-rule-listbh">
                        <td id="new-rule-listbh-td">
                            &nbsp;
                        </td>
                        <td width="30%">
                            ID号
                        </td>
                        <td class="action" width="70%">
                            说明
                        </td>
                    </tr>
                </thead>
                <tbody id="new-rule-listb" class="rule-listb">
EOF
    ;
                    &create_strategy_choices_list_body();
    printf <<EOF
                </tbody>
                <tfoot class="toolbar">
                    <tr>
                        <td id="new-rule-list-foot-td" colspan="$colspan">
                            <span class="opt-tools">
                            </span>
                            <span class="paging-tools">
                                <img id="new_first_page_icon" src="../images/first-page.gif" title="第一页" onclick="new_first_page()"/>
                                <img id="new_last_page_icon" src="../images/last-page.gif" title="上一页" onclick="new_last_page()"/>
                                <span class="paging-text">第<input id="new-current-page" class="paging-tool-text" type="text" onkeydown="new_input_control(this, event)"/>页,共<span id="new-total-page" class="paging-tool-text">xx</span>页</span>
                                <img id="new_next_page_icon" src="../images/next-page.gif" title="下一页" onclick="new_next_page()"/>
                                <img id="new_end_page_icon" src="../images/end-page.gif" title="最后一页" onclick="new_end_page()"/>
                                <img id="new_refresh_icon" src="../images/refresh.png" onclick="new_refresh_page()"/>
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
                    <tr class="strategy_choices_list_foot_tr">
                        <td class="strategy_choices_list_foot_td"colspan="$colspan">
                            <input type="button" class="net_button" value="确定" onclick="choosed_strategy_item_id();"
                        </td>
                    </tr>
                </tfoot>
            </table>
        </div>
EOF
    ;
}

sub create_strategy_choices_list_body() {
    my $page_size = 10;
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
        for ( my $j = 0; $j < 2; $j++) {
            $main_body .= '<td>&nbsp';
            $main_body .= '</td>';
        }
    }
    print "$main_body";
}

sub create_mesg_boxs() {
    printf <<EOF
    <div id="all-mesg-box">
        <div id="apply-mesg-box" class="mesg-box">
            <div class="mesg-box-main">
                <img src="/images/pop_apply.png"/>
                <span id="apply-mesg" class="mesg-body">规则已改变,需应用该规则以使改变生效</span>
            </div>
            <div class="mesg-box-foot">
                <button id="apply-config" onclick="apply_config();">应用</button>
            </div>
        </div>
        <div id="note-mesg-box" class="mesg-box tips-mesg-box">
            <img src="/images/Emoticon.png"/>
            <span id="note-mesg" class="mesg-body">操作成功</span>
        </div>
        <div id="warn-mesg-box" class="mesg-box tips-mesg-box">
            <img src="/images/pop_warn.png"/>
            <span id="warn-mesg" class="mesg-body">操作有误</span>
        </div>
        <div id="error-mesg-box" class="mesg-box tips-mesg-box">
            <img src="/images/pop_error.png"/>
            <span id="error-mesg" class="mesg-body">操作失败</span>
        </div>
        <div id="popup-mesg-box-back" class="popup-cover"></div>
        <div id="popup-mesg-box" class="popup-mesg-box">
            <div class="popup-mesg-box-head-tool">
                <span class="tool-right">
                    <img id="close-popup-mesg-box" src="/images/close_mesg_box.png" onclick="hide_detail_error_mesg();"/>
                </span>
            </div>
            <table class="rule-list popup-mesg-box-table">
                <thead class="popup-mesg-box-toolbar">
                    <tr class="popup-mesg-box-thead">
                        <td>导入错误信息如下</td>
                    </tr>
                </thead>
                <tbody id="popup-mesg-tbody" class="popup-mesg-box-tbody">
                </tbody>
                <tfoot class="popup-mesg-box-toolbar">
                    <tr class="popup-mesg-box-tfoot">
                        <td><input type="button" class="net_button" value="确定" onclick="hide_detail_error_mesg();"/></td>
                    </tr>
                </tfoot>
            </table>
        </div>
        <div id="popup-mesg-box-loading" class="popup-mesg-box">
            <img src="/images/ajax_loading.gif"/>
        </div>
    </div>
EOF
    ;
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
    my $fields_length = @display_add_config_data;
    for(my $i = 0; $i < $fields_length; $i++){
         if(@display_add_config_data[$i]->{'is_in_list'}){
            my $display = @display_add_config_data[$i]->{'display'};
            $display =~ s/\*//g;
            push( @table_display_fields, $display );
            if( @display_add_config_data[$i]->{'name'} eq 'respond_type' ) {
                push( @table_display_fields_name, "respond_type_text" );
            } elsif( @display_add_config_data[$i]->{'name'} eq 'level' ) {
                push( @table_display_fields_name, "level_text" );
            } else {
                push( @table_display_fields_name,   @display_add_config_data[$i]->{'name'} );
            }
            push( @table_display_fields_widths, @display_add_config_data[$i]->{'width'} );
         }
    }
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