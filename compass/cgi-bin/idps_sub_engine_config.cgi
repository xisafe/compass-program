#!/usr/bin/perl

#===============================================================================
#
# DESCRIPTION:  一个添加模块和规则列表模块页面的模板
#               以后写类此的页面可以直接先copy，再做具体编辑
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2014/03/20-09:00
#===============================================================================

#===============================================================================

use Encode;

#==== header.pl中包含很多通用函数，比如IP地址的检测，和文件的读写===============#
#一般都会引用，不要删除此行
require '/var/efw/header.pl';
#===============================================================================#

#=====begin全部变量定义,名字都不用改，可根据实际情况适当添加，初始化全局变量到init_data()中去初始化========================#
my $custom_dir;                 #要保存数据的目录名字
my $conf_dir;                   #规则所存放的文件夹
my $conf_file;                  #规则所存放的文件
my $system_rules_dir;           #存储系统策略集文件夹
my $custom_rules_dir;           #存储用户策略集文件夹
my $strategy_sets_conf;         #存储策略集配置的文件
my $export_file;                #导出时使用
my $export_filename;            #导出时使用
my $import_error_file;          #导入出错时使用
my $imported_tag;               #导入时使用
my $need_reload;                #需要重新加载的标识文件
my $restart;                    #应用重启的程序,根据实际情况填写
my $distribute_strategy_cmd;    #下发策略集
my $extraheader;                #存放用户自定义JS
my %par;                        #存放传过来的数据的哈希
my %query;                      #存放通过get方法传过来的数据
my @display_add_config_data;    #存放<input>信息的哈希
my @table_display_fields;       #规则列表中要展示的字段的集合
my @table_display_fields_name;  #规则列表中要展示的字段的集合
my @table_display_fields_widths;#规则列表中要展示的各个字段的宽度的集合
#=========================end全部变量定义==================================================================================#

&init_data();
&getcgihash(\%par);
&getqueryhash(\%query);
&do_action();

sub init_data(){
    $custom_dir         = 'ipsconsole/child';           #要保存数据的目录名字 ！！！！要配置，不然路径初始化出问题！！！！
    $conf_dir           = '/var/efw/'.$custom_dir;      #规则所存放的文件夹
    $conf_file          = $conf_dir.'/engine.config';   #规则所存放的文件
    $system_rules_dir   = '/var/efw/ipsconsole/rules/system';
    $custom_rules_dir   = '/var/efw/ipsconsole/rules/custom';
    $strategy_sets_conf = '/var/efw/ipsconsole/rules/rulespolicy';
    $need_reload        = $conf_dir.'/sub_engine_need_reload';     #需要重新加载的标识文件
    $import_error_file  = $conf_dir.'/sub_engine_import_error_file';
    $imported_tag       = $conf_dir.'/sub_engine_imported_tag';
    $export_file        = '/tmp/sub_engine_config.csv';
    $export_filename    = 'sub_engine_config.csv';

    $restart                    = '';
    $distribute_strategy_cmd    = '/usr/local/bin/distributepolicy -e';

    #=====存放用户自定义JS、CSS,template_add_list.js、template_add_list.css不要删除=======#
    $extraheader        = '<script language="JavaScript" src="/include/idps_sub_engine_config_init.js"></script>
                            <script language="JavaScript" src="/include/template_add_list.js"></script>
                            <script language="JavaScript" src="/include/idps_sub_engine_config.js"></script>
                            <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />
                            <link rel="stylesheet" type="text/css" href="/include/idps_strategy_list_style.css" />';

    &make_file();#检查要存放规则的文件夹和文件是否存在，不存在就创建，此行不要删除或更改

    #========配置添加模块的数据================================#
    #   添加模块的生成，主要是数据的配置，请按照例子配置数据
    #==========================================================#
    &config_add_item_data();#到这个函数中去配置
    #========配置数据end=======================================#

    &get_display_fields();#根据配置，生成需要的数据，此行不要删掉或更改
}

sub get_config_hash($) {
    my $line = shift;
    chomp($line);
    my %config;
    $config{'valid'} = 0;
    if ($line eq '') {
        return ;
    }
    my @temp = split(/,/, $line);
    my $fields_length =  @display_add_config_data;
    #===================notice==============================
    #  传入规则字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回哈希中的值
    #  也可以自定义,但要和get_config_line同步
    #===================notice==============================
    $config{'engine_name'} = $temp[0];
    $config{'engine_addr'} = $temp[1];
    $config{'engine_status'} = $temp[2];
    $config{'engine_connected'} = $temp[3];
    $config{'strategy'} = $temp[4];
    $config{'strategy_text'} = &get_strategy_text( $config{'strategy'} );
    #============自定义字段组装完毕=========================
    $config{'valid'} = 1;
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
    push(@data_arr, $data->{'engine_name'});
    push(@data_arr, $data->{'engine_addr'});
    push(@data_arr, $data->{'engine_status'});
    push(@data_arr, $data->{'engine_connected'});
    push(@data_arr, $data->{'strategy'});
    #============自定义字段组装完毕=========================
    return join ",", @data_arr;
}

sub get_be_searched_content($) {
    my $line_content = shift;#传入一行数据的配置
    my %data = &get_config_hash($line_content);
    #===================notice==============================
    #  页面展示的内容可能跟后台不一致，
    #  在搜索之前，将后台内容转换为前台展示内容
    #===================notice==============================
    if($data{'engine_status'} eq 'UP') {
        $data{'engine_status'} = "开启";
    } elsif ($data{'engine_status'} eq 'DOWN') {
        $data{'engine_status'} = "关闭";
    } else {
        $data{'engine_status'} = "未知";
    }
    if($data{'engine_connected'} eq 'CONNECTED') {
        $data{'engine_connected'} = "已连接";
    } elsif ($data{'engine_connected'} eq 'DISCONNECT') {
        $data{'engine_connected'} = "未连接";
    }
    #============转换完毕===================================
    return %data;
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
        if($temp{'engine_name'} eq $to_save_data{'engine_name'}) {
            $can_save = 0;
            $can_save_mesg = "已存在相同的引擎名称";
            last;
        }
    }
    #====end==============================================
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
            if($temp{'engine_name'} eq $to_update_data{'engine_name'}) {
                $can_update = 0;
                $can_update_mesg = "已存在相同目的引擎名称";
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

sub toggle_powered_check($$$) {
    my $line = shift;
    my $line_content = shift;
    my $lines = shift;
    my $can_toggle_powered = 1;
    my $can_toggle_powered_mesg = "";
    #===在此可以根据行内容判断是否可以开启或者关闭子引擎===
    #===如果不能，返回0和不能下发的原因，否则返回1和空串=== 
    my %temp = &get_config_hash($line_content);
    if( $temp{'engine_connected'} eq 'DISCONNECT' ) {
        $can_toggle_powered = 0;
        $can_toggle_powered_mesg = "$temp{'engine_name'}未连接,操作下发失败";
    }
    #====end===============================================
    return ($can_toggle_powered, $can_toggle_powered_mesg);
}

sub distribute_line_check($$$){
    my $line = shift;
    my $line_content = shift;
    my $lines = shift;
    my $can_distribute = 1;
    my $can_distribute_mesg = "";
    #===========在此可以根据行内容判断是否可以下发策略=====
    #===如果不能，返回0和不能下发的原因，否则返回1和空串===
    # my %temp = &get_config_hash($line_content);
    # if( $temp{'engine_connected'} eq 'DISCONNECT' ) {
    #     $can_distribute = 0;
    #     $can_distribute_mesg = "$temp{'engine_name'}未连接,策略下发失败";
    # }
    #====end===============================================
    return ($can_distribute, $can_distribute_mesg);
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
        &enable_data();#此文档不需要 2014.04.24
    } elsif($action eq 'disable_data'){
        #==禁用数据(可多条同时禁用)==#
        &disable_data();#此文档不需要 2014.04.24
    } elsif($action eq 'power_down'){
        #==关闭引擎(可多条同时操作)==#
        &power_down();
    } elsif($action eq 'power_on'){
        #==开启引擎(可多条同时操作)==#
        &power_on();
    } elsif($action eq 'delete_data'){
        #==删除数据(可多条同时删除)==#
        &delete_data();
    } elsif($action eq 'distribute_data'){
        #==下发策略数据(可多条同时下发)==#
        &distribute_data();
    } elsif($action eq 'load_strategy_list'){
        #==加载策略数据(可多条同时下发)==#
        &load_strategy_list();
    } elsif($action eq 'export_data'){
        #==导出数据,可以导出特定几列的数据==#
        &export_data();#此文档不需要 2014.04.24
    } elsif($action eq 'import_data'){
        #==导入数据,可以导入特定几列的数据==#
        &import_data();#此文档不需要 2014.04.24
        &showpage();
    } elsif($action eq 'import_error_check') {
        #==检查导入的错误信息(多条)，并返回给用户==#
        &import_error_check();
    } else {
        if($query_action eq 'export_data') {
            #==导出数据,可以导出特定几列的数据==#
            &export_data();
        }
        #==如果用户什么都没提交，默认返回页面==#
        &showpage();
    }
}
sub showpage() {
    &openpage("新模板", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_add();
    # &display_upload();
    &display_rule_list();
    &closebigbox();
    &display_strategy();
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
    # system("touch $need_reload");#此处的进程是守护进程，不需要重启或者重新应用
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
        # $reload = 1;
        $mesg = "规则应用异常";
    }
    send_status( $status, $reload, $mesg, $detail_mesg );
}

sub load_data(){
    my @content_array = ();
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
            #====查询之前做一次映射，以符合前台看到的查询====#
            my %to_be_searched_content = &get_be_searched_content($lines[$i]);
            foreach my $field (keys %to_be_searched_content) {
                #===转换成小写，进行模糊查询==#
                my $new_field = lc($to_be_searched_content{$field});
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

sub load_strategy_list() {
    my @system_list;
    my @custom_list;
    &get_system_strategy_list(\@system_list);
    &get_custom_strategy_list(\@custom_list);

    my %ret_data;
    %ret_data->{'system_list'} = \@system_list;
    %ret_data->{'custom_list'} = \@custom_list;
    %ret_data->{'status'} = 0;#succeed
    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub get_strategy_text($) {
    my $filenames = shift;
    #====原始内容是‘|’隔开的策略文件名,且没有文件名.rules后缀===#
    my %strategy_config;
    my @lines = &read_conf_file($strategy_sets_conf);
    foreach my $line ( @lines ) {
        my %temp = &get_strategy_config_hash( $line );
        $strategy_config{$temp{'strategy_set'}} = $temp{'strategy_set_name'};
    }

    my @strategy_set_filenames = split( /\|/, $filenames );
    my @strategy_set_names;
    foreach my $filename ( @strategy_set_filenames ) {
        push( @strategy_set_names, $strategy_config{$filename} );
    }

    return join "，", @strategy_set_names;
}

sub get_strategy_config_hash($) {
    my $line = shift;
    chomp($line);
    my %config;
    my @temp = split(/,/, $line);
    #===================notice================================#
    #  传入规则字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回哈希中的值
    #  也可以自定义,但要和get_config_line同步
    #===================notice================================#
    $config{'strategy_set_filename'} = $temp[0];
    $config{'strategy_set'} = $temp[0];
    $config{'strategy_set'} =~ s/.rules$//g;
    my $system_rule_absolute_path = $system_rules_dir."/".$config{'strategy_set_filename'};
    my $custom_rule_absolute_path = $custom_rules_dir."/".$config{'strategy_set_filename'};
    if ( -f $system_rule_absolute_path ) {
        $config{'type'} = "系统";
    } elsif ( -f $custom_rule_absolute_path ) {
        $config{'type'} = "用户";
    } else {
        $config{'type'} = "未知";
    }
    $config{'strategy_set_name'} = $temp[1];
    $config{'strategy_set_note'} = $temp[2];
    #============自定义字段组装完毕===========================#
    return %config;
}

sub get_system_strategy_list() {
    my $system_list = shift;
    #=====整理系统策略集=====================#
    my @strategies = &read_conf_file($strategy_sets_conf);
    foreach my $item ( @strategies ) {
        my %data = &get_strategy_config_hash( $item );
        if ( $data{'type'} eq '系统' ) {
            my %strategy = (
                'strategy_name' => 'system_strategy',
                'strategy_id' => $data{'strategy_set'},
                'strategy_value' => $data{'strategy_set'},
                'strategy_label' => $data{'strategy_set_name'}
            );
            push( @$system_list, \%strategy );
        }
    }
    #===========整理完毕=====================#
    return @system_list;
}

sub get_custom_strategy_list() {
    my $custom_list = shift;
    #=====整理用户自定义策略集===============#
    my @strategies = &read_conf_file($strategy_sets_conf);
    foreach my $item ( @strategies ) {
        my %data = &get_strategy_config_hash( $item );
        if ( $data{'type'} eq '用户' ) {
            my %strategy = (
                'strategy_name' => 'custom_strategy',
                'strategy_id' => $data{'strategy_set'},
                'strategy_value' => $data{'strategy_set'},
                'strategy_label' => $data{'strategy_set_name'}
            );
            push( @$custom_list, \%strategy );
        }
    }
    #=====整理完毕===========================#
    return @custom_list;
}

sub save_data() {
    #==第一步先对%par中的值进行处理========#
    #==到&get_config_line(\%par)进行处理=====#
    if($par{'line'} eq '') {
        #===对%par中添加几个未提交上的字段,便于添加=====#
        $par{'engine_status'} = "DOWN";
        $par{'engine_connected'} = "DISCONNECT";
        $par{'strategy'} = "";
        #======end by wl 2014.04.24=====================#
    } else {
        #===对%par中添加几个未提交上的字段,便于更新=====#
        my $line_content = &read_conf_line($conf_file, $par{'line'});
        my @temp = split(",", $line_content);
        $par{'engine_status'} = $temp[2];
        $par{'engine_connected'} = $temp[3];
        $par{'strategy'} = $temp[4];
        #======end by wl 2014.04.24=====================#
    }

    #==第二步保存==========================#
    my ($status, $reload, $mesg) = &save_conf_line($par{'line'},&get_config_line(\%par));
    &reset_values();
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 0 表示不重新应用，其他表示应用
    # => $mesg: 相关错误的消息
    #===========================================#
    &send_status($status, $reload, $mesg, $mesg);
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
            # $reload = 1;
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
            # $reload = 1;
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
        if($i == 0) {
            #针对第0项，要特殊处理
            if($par{'0'} eq '0'){
                my %data = &get_config_hash(@lines[0]);
                $data{'enabled'} = $enable;
                my $line_content = &get_config_line(\%data);
                @lines[0] = $line_content;
                $succeeded_num++;
            }
        }else {
            if($par{$i}){
                my %data = &get_config_hash(@lines[$i]);
                $data{'enabled'} = $enable;
                my $line_content = &get_config_line(\%data);
                @lines[$i] = $line_content;
                $succeeded_num++;
            }
        }
    }
    &save_conf_file(\@lines, $conf_file);
    #不需要重新应用
    # if($succeeded_num) {
    #     $reload = 1;
    #     &create_needreload_tag();
    # }
    send_status($status, $reload, "成功$opt$succeeded_num条规则", "成功$opt$succeeded_num条规则");
}


sub power_on() {
    &toggle_powered(1);
}

sub power_down() {
    &toggle_powered(0);
}

sub toggle_powered() {
    my $power = shift;
    my $opt = "";
    if ($power) {
        $power = 'UP';
        $opt = "开启";
    } 
    else {
        $power = 'DOWN';
        $opt = "关闭";
    }
    my ($status, $reload, $mesg, $succeeded_num, $fail_num) = (0, 0, "", 0, 0);
    my @fail_mesg = ();
    my @lines = read_conf_file($conf_file);
    my @new_lines;
    my $record_num = @lines;

    for(my $i = 0; $i < $record_num; $i++){
        my %data = &get_config_hash( $lines[$i] );
        if ( $par{$i} eq "$i" ) {
            #检查能否开关
            my ($if_can, $errormsg) = &toggle_powered_check($i, $lines[$i], \@lines);
            if($if_can){
                $succeeded_num++;
                #======这里应该是调用脚本，暂时修改数据==#
                $data{'engine_status'} = $power;
            }else{
                $fail_num++;
                push(@fail_mesg, $errormsg);
            }
        }
        my $new_line = &get_config_line( \%data );
        push( @new_lines, $new_line );
    }
    &save_conf_file(\@new_lines, $conf_file);
    #不需要重新应用
    # if($succeeded_num) {
    #     $reload = 1;
    #     &create_needreload_tag();
    # }
    send_status($status, $reload, "成功$opt$succeeded_num个引擎,失败$fail_num个", \@fail_mesg);
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
        if($i == 0) {
            #针对第0项，要特殊处理
            if($par{'0'} ne '0'){
                push(@new_lines, @lines[0]);
            } else {
                #检查能否被删除
                my ($if_can, $errormsg) = &del_line_check(0, @lines[0], \@lines);
                if($if_can){
                    $succeeded_num++;
                }else{
                    push(@new_lines, @lines[0]);#不能删除
                    $fail_num++;
                    push(@fail_mesg, $errormsg);
                }
            }
        }else {
            if(!$par{$i}){
                push(@new_lines, @lines[$i]);
            } else {
                #检查能否被删除
                 my ($if_can, $errormsg) = &del_line_check($i, @lines[$i], \@lines);
                if($if_can){
                    $succeeded_num++;
                }else{
                    push(@new_lines, @lines[$i]);#不能删除
                    $fail_num++;
                    push(@fail_mesg, $errormsg);
                }
            }
        }
    }
    &save_conf_file(\@new_lines, $conf_file);
    #不需要重新应用
    # if($succeeded_num) {
    #     $reload = 1;
    #     &create_needreload_tag();
    # }
    send_status($status, $reload, "成功删除$succeeded_num条规则,失败$fail_num条规则", \@fail_mesg);
}

sub distribute_data() {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 0 表示不重新应用，其他表示应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $reload, $mesg, $succeeded_num, $fail_num) = (0, 0, "", 0, 0);
    my @fail_mesg = ();

    my @lines = read_conf_file($conf_file);
    my @new_lines;
    my @engine_names;
    my $record_num = @lines;
    my %engines;
    my %system_list;
    my %custom_list;
    my $strategies = &get_strategies_text();
    &get_content_hash( \%engines, $par{'engines'} );
    # &get_content_hash( \%system_list, $par{'system_list'} );
    # &get_content_hash( \%custom_list, $par{'custom_list'} );

    for(my $i = 0; $i < $record_num; $i++){
        my %data = &get_config_hash( $lines[$i] );
        if ( $engines{$i} eq "$i" ) {
            #检查能否下发策略
            my ($if_can, $errormsg) = &distribute_line_check($i, $lines[$i], \@lines);
            if($if_can){
                $succeeded_num++;
                $data{'strategy'} = $strategies;
                push(@engine_names, $data{'engine_name'});
            }else{
                $fail_num++;
                push(@fail_mesg, $errormsg);
            }
        }
        my $new_line = &get_config_line(\%data);
        push( @new_lines, $new_line );
    }
    #=======保存策略到配置文件=============#
    &save_config_file( \@new_lines, $conf_file );
    #=======保存end========================#

    #=======根据引擎名字下发策略===========#
    my $engines = join " ", @engine_names;
    my $distribute_data_opt = $distribute_strategy_cmd." ".$engines;
    my $result = system($distribute_data_opt);
    if ( $result == 0 ) {
        $status = 0;
    } else {
        $status = -1;
    }
    #======================================#
    if ( $fail_num == 0) {
        #==没有错误的信息===#
        $mesg = "$succeeded_num个引擎成功下发策略";
    } else {
        $mesg = "$fail_num个引擎因未连接而下发失败,$succeeded_num个引擎下发策略成功";
    }
    send_status($status, $reload, $mesg, \@fail_mesg);
}

sub get_strategies_text() {
    if( $par{'system_list'} ne '' && $par{'custom_list'} ne '') {
        return $par{'system_list'}."|".$par{'custom_list'};
    } elsif ( $par{'system_list'} ne '' && $par{'custom_list'} eq '' ) {
        return $par{'system_list'};
    } elsif ( $par{'system_list'} eq '' && $par{'custom_list'} ne '' ) {
        return $par{'custom_list'};
    } else {
        return "";
    }
}
sub get_content_hash($$) {
    my $data = shift;
    my $content = shift;
    my @temp = split( /\|/, $content );
    foreach my $item ( @temp ) {
        $data->{$item} = $item;
    }
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
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $conf_file){
        `touch $conf_file`;
    }
}

sub reset_values() {
    %par = ();
}

sub display_add() {
    &create_mesg_boxs();
    printf <<EOF
    <div id="add-div" >
        <div id="add-div-header">
            <span class="add-header-title">
                <img class="label-image" src="/images/add.png"/>
                <span id="add-title" class="label-text">添加引擎</span>
            </span>
        </div>
        <div id="add-div-content">
            <form id="template-form" name="TEMPLATE_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" enctype="multipart/form-data" >
                <input type="hidden" id="line-num" name="line" value=""/>
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
        "display" => "引擎名称",
        "name" => "engine_name",
        "type" => "text",
        "value" => "",
        "is_in_list" => 1, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "12%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "引擎IP地址",
        "name" => "engine_addr",
        "type" => "text",
        "value" => "",
        "is_in_list" => 1, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "12%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
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
                                <!--<form class="export-all-form" method="post" ACTION="$ENV{'SCRIPT_NAME'}">-->
                                <!--<a class="export-all-link" href="$ENV{'SCRIPT_NAME'}?ACTION=export_data">
                                    <button id="export-all" class="imaged-button" name="ACTION" value="export_data">
                                            <img class="button-image" src="../images/download.png" /><span class="button-text" >导出全部</span>
                                    </button>
                                </a>-->
                                <!--</form>-->
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

sub display_strategy() {
    printf <<EOF
    <div id="popup-strategy" class="popup-mesg-box">
        <div class="popup-strategy-head">
            <input type="image" id="hide_strategy_list" src="/images/close.gif" onclick="hide_strategy_list();"/>
        </div>
        <table class="strategy-list">
            <thead>
                <tr class="table-header">
                    <td class="boldbase" colspan="2">
                        请选择要下发的策略
                    </td>
                </tr>
            </thead>
            <tbody>
                <tr class="odd">
                    <td width="20%" class="add-div-type">
                        <label for="system_strategy_set">系统策略集</label>
                        <input type="checkbox" id="system_strategy_set" name="system_strategy_set" onclick="toggle_all_system_strategy(this);"/>
                    </td>
                    <td id="system_strategy_set_hook">
                    </td>
                </tr>
                <tr class="odd">
                    <td width="15%" class="add-div-type">
                        <label for="custom_strategy_set">用户策略集</label>
                        <input type="checkbox" id="custom_strategy_set" name="custom_strategy_set" onclick="toggle_all_custom_strategy(this);"/>
                    </td>
                    <td id="custom_strategy_set_hook">
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr class="table-footer">
                    <td colspan="2">
                        <input class="net_button" type="button" name="distribute_strategy" value="下发" onclick="distribute_strategy();"/>
                    </td>
                </tr>
            </tfoot>
        </table>
    </div>
EOF
    ;
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
    &create_distribute_selected_button(); #针对此文档新增 by wl 2014.04.24
    # &create_power_on_selected_button(); #针对此文档新增 by wl 2014.04.24
    # &create_power_down_selected_button(); #针对此文档新增 by wl 2014.04.24
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

sub create_power_on_selected_button() {
    printf <<EOF
    <button id="power-on-selected" class="imaged-button" onclick="power_on_selected_items();">
        <img class="button-image" src="../images/powered-on.png" /><span class="button-text" >开启选中</span>
    </button>
EOF
    ;
}

sub create_power_down_selected_button() {
    printf <<EOF
    <button id="power-down-selected" class="imaged-button" onclick="power_down_selected_items();">
        <img class="button-image" src="../images/powered-down.png" /><span class="button-text" >关闭选中</span>
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

sub create_distribute_selected_button() {
    printf <<EOF
    <button id="distribute-selected" class="imaged-button" onclick="distribute_selected_items();">
        <img class="button-image" src="../images/distribute.png" /><span class="button-text" >下发策略</span>
    </button>
EOF
    ;
}

sub get_display_fields(){
    my $fields_length = @display_add_config_data;
    for(my $i = 0; $i < $fields_length; $i++){
         if(@display_add_config_data[$i]->{'is_in_list'}){
            push(@table_display_fields,@display_add_config_data[$i]->{'display'});
            push(@table_display_fields_name,@display_add_config_data[$i]->{'name'});
            push(@table_display_fields_widths,@display_add_config_data[$i]->{'width'});
         }
    }
    #=====增加两个字段(引擎状态、连接状态)====#
    push(@table_display_fields,"引擎状态");
    push(@table_display_fields_name, "engine_status_render");
    push(@table_display_fields_widths,"8%");
    push(@table_display_fields,"连接状态");
    push(@table_display_fields_name, "engine_connected_render");
    push(@table_display_fields_widths,"8%");
    push(@table_display_fields,"策略");
    push(@table_display_fields_name, "strategy_text");
    push(@table_display_fields_widths,"40%");
    #==========end by wl 2014.04.24===========#
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