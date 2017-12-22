#!/usr/bin/perl

#===============================================================================
#
# DESCRIPTION:  一个添加模块和规则列表模块页面的模板
#               以后写类此的页面可以直接先copy，再做具体编辑
#
# AUTHOR: 刘炬隆（LiuJulong）, 849466624@qq.com
# COMPANY: capsheaf
# CREATED: 2014/05/06
#===============================================================================

#===============================================================================

use Encode;
use threads;
use POSIX qw(strftime);
#==== header.pl中包含很多通用函数，比如IP地址的检测，和文件的读写===============#
#一般都会引用，不要删除此行
require '/var/efw/header.pl';
#===============================================================================#

#=====begin全部变量定义,名字都不用改，可根据实际情况适当添加，初始化全局变量到init_data()中去初始化========================#
my $custom_dir;                 #要保存数据的目录名字
my $conf_dir;                   #规则所存放的文件夹
my $conf_file;                  #规则所存放的文件
my $detail_data_file;
my $waf;                        #执行追踪命令的文件
my $caught;
my $name_btn_caught;
my $caught_state_file;
my $state_file;              #策略所存放的文件
my $export_file;                #导出时使用
my $export_filename;            #导出时使用
my $import_error_file;          #导入出错时使用
my $imported_tag;               #导入时使用
my $need_reload;                #需要重新加载的标识文件
my $restart;                    #应用重启的程序,根据实际情况填写
my $track_state;
my $ip_port;
my $protocol_selected;
my $extraheader;                #存放用户自定义JS
my %par;                        #存放传过来的数据的哈希
my %query;                      #存放通过get方法传过来的数据
my %protocol_hash;
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
    #$custom_dir = 'protocol_reduction';                            #要保存数据的目录名字 ！！！！要配置，不然路径初始化出问题！！！！
    $conf_dir = '/tmp';                 #规则所存放的文件夹
    $conf_file = $conf_dir.'/sessionfile';      #规则所存放的文件
    $state_file = $conf_dir.'/restord_session_complited';
    $waf = '/usr/local/bin/sessionrestore';
    $caught = '/usr/local/bin/sessionrecord';
    $name_btn_caught = "开始抓包";
    $caught_state_file = $conf_dir.'/action_state';
    $need_reload = $conf_dir.'/need_reload'; #需要重新加载的标识文件
    $import_error_file = $conf_dir.'/import_error_file';
    $imported_tag = $conf_dir.'/imported_tag';
    $export_file = '/tmp/event_logs_list.csv';
    $export_filename = 'event_logs_list.csv';
    %protocol_hash = (
    "http" => "HTTP",
    "ftp" => "FTP",
    "smtp" => "SMTP",
    "pop" => "POP",
    "snmp" => "SNMP",
    "imap" => "IMAP",
    "telnet" => "TELENT"
    );
    $restart = '';                                       #应用重启的程序,根据实际情况填写
    $extraheader = '<script language="JavaScript" src="/include/idps_protocol_reduction_init2.js"></script>
                    <script language="JavaScript" src="/include/idps_protocol_reduction_list2.js"></script>
                    <script type="text/javascript" src="/include/jquery.js"></script>
                    <script type="text/javascript" src="/include/ESONCalendar.js"></script>
                    <link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />
                    <link rel="stylesheet" type="text/css" href="/include/port_custom.css" />
                    <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />';#存放用户自定义JS，这里仅仅是个示例,template_add_list.js、template_add_list.css不要删除
    #&make_file();#检查要存放规则的文件夹和文件是否存在，不存在就创建，此行不要删除或更改

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
    my @temp = split(" ", $line);
    my $fields_length =  @display_add_config_data;
    #===================notice==============================
    #  传入规则字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回哈希中的值
    #  也可以自定义,但要和get_config_line同步
    #===================notice==============================
    for(my $i = 0; $i < $fields_length-1; $i++){
         $config{@display_add_config_data[$i]->{'name'}} = shift(@temp);
    }
    my $content = join(" ",@temp);
    $config{'content'} = $content;
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

sub do_action() {
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    #==如果不是导出数据，都打印普通http头部==#
    if($action ne 'export_data' && $query_action ne 'export_data') {
        &showhttpheaders();
    }
    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==加载数据==#
        &load_data();
    } elsif($action eq 'load_data_detail'){
        #==加载详细信息==#
        &load_data_detail();
    } elsif($action eq 'confirm'){
        #==点击确定按钮所执行的事件==#
        &confirm();
    } elsif($action eq 'caught_start'){
        #==开始抓包==#
        &caught_start();
    } elsif($action eq 'caught_stop'){
        #==停止抓包==#
        &caught_stop();
    } elsif($action eq 'track_source'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &track_source();
    } elsif($action eq 'track_target'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &track_target();
    } elsif($action eq 'track_all'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &track_all();
    } elsif($action eq 'detail'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &detail();
    } elsif($action eq 'last_page'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &goto_page();
    } elsif($action eq 'next_page'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &goto_page();
    } elsif($action eq 'goto_page'){
        #==保存一条数据(可能是新增可能是编辑)==#
        &goto_page();
    } else {
        #==如果用户什么都没提交，默认返回页面==#
        &showpage();
    }
}

#清楚之前的文件
sub clear_files(){
    if(-e $conf_file){
        `rm $conf_file`;
    }
    
    if(-e $state_file){
        `rm $state_file`;
    }
}

sub caught_start(){
    my $protocol = $par{'protocol'};
    # $protocol_selected = $protocol;
    `$caught -s -p $protocol`;
    if(! -e $caught_state_file ){
        `touch $caught_state_file`;
    }
    send_status(0,0,"");
    #&showpage($protocol_selected);
}

sub caught_stop(){
    #my $protocol = $par{'protocol'};
    # $protocol_selected = $protocol;
    `$caught -k`;
    if( -e $caught_state_file ){
        `rm $caught_state_file`;
    }
    send_status(0,0,"");
    #&showpage($protocol_selected);
}
#点击确定按钮所执行的事件
sub confirm(){
    my $protocol = $par{'protocol'};
    #my $inputDate = $par{'inputDate'};
    my $inputDate = &getTime();
    $track_state = 'confirm';
    &clear_files();
    `$waf -p $protocol -y $inputDate -t none -r 1:20`;
    send_status(0,0,"");
}
#点击追踪源所执行的事件
sub track_source(){
    my $protocol = $par{'protocol'};
    #my $inputDate = $par{'inputDate'};
    my $inputDate = &getTime();
    my $source = $par{'source'};
    $track_state = 'track';
    $ip_port = $source;
    &clear_files();
    `$waf -p $protocol -y $inputDate -t sdip -n $source -r 1:20`;
    
    send_status(0,0,"");
}
#点击追踪目标所执行的事件
sub track_target(){
    my $protocol = $par{'protocol'};
    #my $inputDate = $par{'inputDate'};
    my $inputDate = &getTime();
    my $target = $par{'target'};
    $track_state = 'track';
    $ip_port = $target;
    &clear_files();
    `$waf -p $protocol -y $inputDate -t sdip -n $target -r 1:20`;
    send_status(0,0,"");
}
#点击追踪流所执行的事件
sub track_all(){
    my $protocol = $par{'protocol'};
    #my $inputDate = $par{'inputDate'};
    my $inputDate = &getTime();
    my $target = $par{'target'};
    my $source = $par{'source'};
    my $whole = $source.'#'.$target;
    $track_state = 'flow';
    $ip_port = $whole;
    &clear_files();
    `$waf -p $protocol -y $inputDate -t flow -n $whole -r 1:20`;
    send_status(0,0,"");
}
#点击详细信息所执行的事件
sub detail(){
    my $protocol = $par{'protocol'};
    #my $inputDate = $par{'inputDate'};
    my $inputDate = &getTime();
    my $fileName = $par{'fileName'};
    my $dataNum = $par{'dataNum'};
    &clear_files();
    `$waf -p $protocol -y $inputDate -i -f $fileName -s $dataNum`;
    send_status(0,0,"");
}
#点击页面切换所执行的事件
sub goto_page(){
    my $protocol = $par{'protocol'};
    #my $inputDate = $par{'inputDate'};
    my $inputDate = &getTime();
    my $page_goto = $par{'page_goto'};
    #my $current_page = $spar{'current_page'};
    my $start = 20*$page_goto-20+1;
    my $end = 20*$page_goto;
    &clear_files();
    if($track_state eq 'track'){
        `$waf -p $protocol -y $inputDate -t sdip -n $ip_port -r $start:$end`;
    }elsif($track_state eq 'flow'){
        `$waf -p $protocol -y $inputDate -t sdip -n $ip_port -r $start:$end`;
    }else{
        `$waf -p $protocol -y $inputDate -t none -r $start:$end`;
    }
    send_status(0,0,$page_goto,"");
}

#加载详细信息
sub load_data_detail(){
    my @lines = read_conf_file($conf_file);
    my %ret_data;
    %ret_data->{'detail_data'} = \@lines;
    if(-e $state_file){
        %ret_data->{'status'} = 0;#succeed
    }else{
        %ret_data->{'status'} = -1;#succeed
    }
    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub showpage() {
    &openpage("协议还原", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_add();
    #&display_upload();
    &display_rule_list();
    &closebigbox();
    &closepage();
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




sub apply_data() {
    system($restart);#重启服务
    system("rm $need_reload");
    send_status(0, 0, "规则应用成功","规则应用成功");
}

sub load_data(){
    my @content_array = ();
    my @lines = read_conf_file($conf_file);
    my $record_num = @lines;
    my $total = 0;
    if($record_num > 0){
        $total = $lines[0];
    }

    for(my $i = 1; $i < $record_num; $i++){
        my %conf_data = &get_config_hash(@lines[$i]);
        if (! $conf_data{'valid'}) {
            next;
        }
        $conf_data{'line'} = $i;
        push(@content_array, \%conf_data);
        #$total++;
    }
    my %ret_data;
    %ret_data->{'display_cols'} = \@table_display_fields_name;
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total'} = $total;
    if(-e $state_file){
        %ret_data->{'status'} = 0;#succeed
    }else{
        %ret_data->{'status'} = -1;#succeed
    }
    
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
    
    if(! -e $state_file){
        `touch $state_file`;
    }
}

sub reset_values() {
    %par = ();
}

#获取系统当前时间并格式化
sub getTime(){
    my $time = shift||time();
    my $localtime = strftime("%Y-%m-%d %H:%M:%S", localtime($time));
    my @time_out = split(' ',$localtime);
    $time_out[0] =~ s/\ |\-|\n//g;
    return $time_out[0];
}

sub display_add() {
    &openbox('100%', 'left', _('记录'));
    print "<div class='paging-div-header'>";
    printf <<END
        <div class='page-footer' style='padding:0px 0px;margin:0px auto ;width:100%'>
            <table width='100%' align='center'>
            <tr>
                <form enctype='multipart/form-data' method='post' name="SEARCH_FORM" action='$ENV{'SCRIPT_NAME'}'>
                    <td  align='left' style="padding-left:25px">选择协议 <select name="protocols" id="protocol">
END
;
    foreach my $key(keys %protocol_hash){
        print "<option value='$key'>$protocol_hash{$key}</option>";
    }
    my $date_now = &getTime();
    if( -e $caught_state_file){
        $name_btn_caught = '停止抓包';
    }else{
        $name_btn_caught = '开始抓包';
    }
    printf <<END
                </select> </td>
                <!--<td>选择日期: <input type="text" SIZE="12" id="inputDate" name='DATE' value="$date_now"/>
                <script type="text/javascript"> 
                    ESONCalendar.bind("inputDate");
                </script>
                </td>
                <td><button id="btn_caught" style="margin:0px 0px" class="imaged-button" onclick="change_action(this);"><span id="text_btn_caught" class="button-text">$name_btn_caught</span></button></td>-->
                <td  align='left'><input class='submitbutton' type='button' id="btn_caught" name='ACTION' value='$name_btn_caught' onclick="change_action(this);"/></td>
                <td  align='left'><input class='submitbutton' type='button' id="btn_confirm" name='ACTION' value='分析' onclick="doaction_confirm();"/></td>
                </form>
            </tr>
        </table>
        </div>
END
;
}

sub config_add_item_data() {
    my %hash = (
        "display" => "文件名",
        "name" => "filename",
        "type" => "text",
        "value" => "",
        "is_in_list" => 0, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "18%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "数据包编号",
        "name" => "data_num",
        "type" => "select",
        "value" => "",
        "is_in_list" => 0, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "18%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "源",
        "name" => "source_ip",
        "type" => "text",
        "value" => "",
        "is_in_list" => 1, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "16%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "源端口",
        "name" => "source_port",
        "type" => "text",
        "value" => "",
        "is_in_list" => 0, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "16%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "目标",
        "name" => "target_ip",
        "type" => "text",
        "value" => "",
        "is_in_list" => 1, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "16%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
     my %hash = (
        "display" => "目标端口",
        "name" => "target_port",
        "type" => "select",
        "value" => "",
        "is_in_list" => 0, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "20%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "发送字节数",
        "name" => "send_bits",
        "type" => "text",
        "value" => "",
        "is_in_list" => 1, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "10%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    
     my %hash = (
        "display" => "内容",
        "name" => "content",
        "type" => "text",
        "value" => "",
        "is_in_list" => 1, #配置其是否在规则列表中显示出来，0为不显示，不等于0表示显示
        "width" => "40%",#此字段只有在is_in_list字段不等于0时可用，并且所有的启用了的此字段加起来为80%最适宜，可微调
        "class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    
    
}


sub create_display_add_lines(){
    my $total_count = @display_add_config_data;
    my @names = &get_all_strategy();    
    my $inputs_name;
    foreach (@names){
        my $oneinput = '<option value="'.$_.'">'.$_.'</option>';
        $inputs_name .= $oneinput;
    }
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
            if($item->{name} eq 'strategy_name'){
                $input .=$inputs_name;
            }elsif($item->{name} eq 'type'){
                $input .= '<option value="query_param_name">查询参数名称</option>';
            }elsif($item->{name} eq 'match_type'){
                $input .= '<option value="regex">正则匹配</option>';
            }
            $input .= '</select>';
        } elsif($item->{'type'} eq 'textarea') {
            $input = '<textarea name="'.$item->{'name'}.'" class="input-textarea">'.$item->{'value'}.'</textarea>';
        }elsif($item->{'type'} eq 'radio'){
            $input = '<input type="'.$item->{'type'}.'" name="'.$item->{'name'}.'" value="on"/>开启
            <input style="margin-left:44px" type="'.$item->{'type'}.'" name="'.$item->{'name'}.'" value="off"/>关闭';
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
                <td class="add-div-type" colspan="2">$item->{'display'}</td>
                <td>
                    $input
                </td>
            </tr>
EOF
        ;
        
    }
}


sub display_rule_list() {
    &create_mesg_boxs();
    my $colspan = @table_display_fields + 2;
    printf <<EOF
    <div id= "bgDiv" style= "position:absolute;display:none;top:0; background-color:#777; filter:progid:DXImagesTransform.Microsoft.Alpha(style=3,opacity=25,finishOpacity=75); opacity:0.6; left:0; width:100%; height:900px; z-index:10000;"> </div> 
    <div id= "detailDiv" style= "width:100%;margin-left:300px; height:auto; position:absolute;display:none; top:150px; left:0px; filter:progid:DXImagesTransform.Microsoft.Alpha(style=3,opacity=25,finishOpacity=75); opacity:1.0; left:0; width:50%; z-index:10000;"> 
    <div class="fd_box">
    <div class="tm_box" style="width:600px"></div>
    <div class="denglu_box" style="width:580px">
    <h1 style="width:570px">详细信息</h1>
    <span><textarea id="item_detail" style="width:100%;height:170px" type="textarea"></textarea></span>
    <div><input class='net_button' style="margin-top:9px;margin-left:250px" type='button' style='color: black; background-image: url(\"/images/button.jpg\");' value='确定' onclick='close_detail_box();'  name='ok' />
    </div>
    </div>
    <div class="guanbi" style="right:-270px">
        <label>
            <img id="search-button" class="search-button-img" src="../images/close.png" />
        </label>
    </div>
    </div>
    </div> 
    
    <!--<div class="fd" id="detailDiv" style="left:-150px">
    <div class="fd_box">
    <div class="tm_box" style="width:600px"></div>
    <div class="denglu_box" style="width:580px">
    <h1 style="width:570px">详细信息</h1>
    <span><textarea id="item_detail" style="width:100%;height:170px" type="textarea"></textarea></span>
    <div><input class='net_button' style="margin-top:9px;margin-left:250px" type='button' style='color: black; background-image: url(\"/images/button.jpg\");' value='确定' onclick='\$(".fd").hide();'  name='ok' />
    </div>
    </div>
    <div class="guanbi" style="right:-270px">
        <label>
            <img id="search-button" class="search-button-img" src="../images/close.png" />
        </label>
    </div>
    </div>
    </div>-->
    
    <div class="list">
            <table class="rule-list">
                <thead class="toolbar" style="height:40px">
                    
                    <tr id="rule-listbh">
EOF
    ;
                        #==========生成规则列表的表头配置参数见本文档开头部分=====
                        &fill_table_header();
                        #==========end============================================
    printf <<EOF
                    <td width="15%">操作</td>    
                    </tr>
                </thead>
                <tbody id="rule-listb" class="rule-listb">
                </tbody>
                <tfoot class="toolbar">
                    <tr>
                        <td id="rule-list-foot-td" colspan="$colspan">
                            <span class="paging-tools">
                                <img id="last_page_icon" src="../images/last-page.gif" title="上一页" onclick="last_page()"/>
                                <span class="paging-text">第<input id="current-page" class="paging-tool-text" type="text" disabled />页,共<span id="total-page" class="paging-tool-text">1</span>页</span>
                                <img id="next_page_icon" src="../images/next-page.gif" title="下一页" onclick="next_page()"/>
                                <span>
                                    <input type="text" id="page_togo" name="page_togo" />
                                    <input type="button" id="btn_go" name="btn_go" value="Go" onclick="goto_page();"/>
                                </span>
                            </span>
                         </td>
                    </tr>
                </tfoot>
            </table>
        </div>
EOF
    ;
    #&turn_page();
}

sub turn_page(){
    #####翻页的代码以及跳转页面的代码
    printf <<END

    <div class='page-footer' style='padding:0px 5px;margin:0px auto ;width:95%;border-top:1px solid #999;'>
    <table width='100%' align='center' style="border:0px">
    <tr>
        <td width='40%' align='right'>
        <td  align='right'>
        <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type="hidden" name="DATE" value="$prevday">
        $hidden_class
        <input class='submitbutton' type="submit" style="background:none;border:0;cursor:pointer" name="ACTION" value='上一天' />
        </form>
        </td>
        <td width='2%' align='right'>
END
,
;
    if ($next != -1) {
printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="1">
    <input type="hidden" name="DATE" value="$date">
    <input type='hidden' name='status' value='$status'>
    $hidden_class
    <input class='submitbutton' type="image" title='%s' name="ACTION" src="/images/first-page.png">
    </form>
END
,
_('First page')
;
    } else {

    print "<input class='submitbutton' type='image' name='ACTION' title='"._('First page')."' src='/images/first-page-off.png'>";
    }
    print "</td><td width='2%'>\n";
    if ($next != -1) {
printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$next">
    <input type="hidden" name="DATE" value="$date">
    <input type='hidden' name='status' value='$status'>
    $hidden_class
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/last-page.png">
    </form>
END
,
_('Last page')
;
    }
    else {

    print "<input class='submitbutton' type='image' name='ACTION' title='"._('Last page')."' src='/images/last-page-off.png'>";
    }
    printf <<END
        <td  align='center'>%s</td>
END
,
_('Current %s page',1),
;

    print "<td width='2%' align='right'>";
    if ($prev != -1) {
printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$prev">
    <input type="hidden" name="DATE" value="$date">
    <input type='hidden' name='status' value='$status'>
    $hidden_class
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/next-page.png">
    </form>
END
,
_('Next page')
;
    } 
    else {
        print "<input class='submitbutton' type='image' name='ACTION' title='"._('Next page')."' src='/images/next-page-off.png'>";
    }
    print "</td><td width='2%'>\n";
     if ($prev != -1) {
printf <<END
    <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$totaloffset">
    <input type="hidden" name="DATE" value="$date">
    <input type='hidden' name='status' value='$status'>
    $hidden_class
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/end-page.png">
    </form>
END
,
_('End page')
;
    } 
    else {
        print "<input class='submitbutton' type='image' name='ACTION' title='"._('End page')."' src='/images/end-page-off.png'>";
    }
    printf <<END
        </td>
        <td width='2%'>
        <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type="hidden" name="DATE" value="$nextday">
        $hidden_class
        <input class='submitbutton' type="submit" style="background:none;border:0;cursor:pointer" name="ACTION" value='%s' />
        </form>
        </td>
        <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
        <td  align='right' >%s: <input type="text" SIZE="8" name='OFFSET' VALUE="$offset"></td>
        <td  align='center'><input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
        <input type="hidden" name="DATE" value="$date">
        <input type='hidden' name='status' value='$status'>
        <input type="hidden" name="totaled" value="$totaloffset">
        $hidden_class
        </form>
    </tr>
    </table>
    </div>
END
,
_('Next day'),
_('Jump to Page'),
_('Go')
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
            <img src="/images/dialog-warning.png"/>
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
    #&create_delete_selected_button();
    &create_show_all_button();
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

sub create_show_all_button() {
    printf <<EOF
    <button id="show-all" class="imaged-button" onclick="show_all()">
        <span class="button-text" >显示全部</span>
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
