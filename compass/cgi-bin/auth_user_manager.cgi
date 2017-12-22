#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/12/03
use Encode;
use Digest::MD5;
use Data::Dumper;
use Spreadsheet::WriteExcel;
use MIME::Base64;
require '/var/efw/header.pl';
require 'list_panel_opt.pl';
require 'file_relevant_time.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $conf_file_settings; #默认配置所存放的文件
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
my $cmd_logout;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $templet = "/var/efw/AAA/users_template.xls";
#记录日志的变量
my $CUR_PAGE = "认证用户管理";   #当前页面
my $log_oper;    #当前操作，用于记录日志,新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '0';  #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

my $errormessage    = '';
my $warnmessage     = '';
my $notemessage     = '';
#=========================全部变量定义end=======================================#
&getcgihash(\%par);
if ($par{'ACTION'} eq 'download' || $par{'ACTION'} eq 'export') {
    &upload_download($par{'ACTION'});
}
&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/AAA';                               #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;               #规则所存放的文件夹
    $conf_file          = $conf_dir.'/user';                    #发件人信息所存放的文件
    $usergroup_file     = $conf_dir.'/user_group';
    $conf_file_settings = $conf_dir.'/config';                  #发件人信息所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_user';#启用信息所存放的文件
    $cmd                = "/usr/local/bin/rstAAA";
    $cmd_logout         = "/usr/local/bin/aaaLogout";
    $errormessage       = '';
    $notemessage        = '';
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    
                    <link rel="stylesheet" type="text/css" href="/include/yp_personal.css" />
                    <link rel="stylesheet" type="text/css" href="/include/jsTree.css" />
                    <link rel="stylesheet" type="text/css" href="/include/auth_user_manager.css" />
                    <script language="JavaScript" src="/include/jquery-3.1.0.min.js"></script>
                    <script language="JavaScript" src="/include/jstree.js"></script>
                    
                    <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css"/>
                    <link rel="stylesheet" type="text/css" href="/include/waiting_mesgs.css"/>
                    <script type="text/javascript" src="/include/popup_mesgs.js"></script>
                    <script type="text/javascript" src="/include/waiting_mesgs.js"></script>

                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/auth_user_manager_init.js"></script>';
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

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_data') {
        #==下载数据==#
        &load_data();
    } 
    elsif ($action eq 'save_data' && $panel_name eq 'add_panel') {
        #==保存数据==#
        &save_data();
    }
    elsif ( $action eq 'enable_forbidded_item') {
        &enable_forbidded_item();
    }
    elsif ($action eq 'get_tree') {
        &get_tree_data();#得到树结构
    }
    elsif ($action eq 'delete_group_item') {
        &delete_group_item();#删除树中要删除的组
    }
    elsif ($action eq 'update_tree') {
        &update_tree();#更新树
    }
    elsif ($action eq 'move_to') {
        &move_to();#移动用户所在组
    }
    elsif ($action eq 'show_user_num') {
        &show_user_num();#更新用户数目
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ( $action eq 'import') {
        &import_user();
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
    }elsif ($action eq 'up_down_tree') {
        #==禁用规则==#
        &up_down_tree();
    }
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub import_user() {
    my $cgi = new CGI; 
    my $file = $cgi->param('file_lib');
    my $default_group_id = $cgi->param('default_group_id');
    my $continue_or_skip = $cgi->param('continue_or_skip');
    my $update_user_dir = "/tmp/";
    my $update_user_file = 'import_user.xls' ;
    &uploads($update_user_file,$update_user_dir);
    my $filename = $update_user_dir.$update_user_file;
    my $user_data = `sudo /usr/local/bin/excelImportExport.py -a import -f $filename`;
    my $temp_hash = $json->decode($user_data);
    my $temp_users = $temp_hash->{'detail'};
    my @users = @$temp_users ;
    my @lines;
    ( $status, $mesg ) = &read_config_lines($conf_file,\@lines);
    for (my $m = 0; $m < @users; $m++){
        
        if ($users[$m]->{'username'} =~ /\"|\<|\>/ || length($users[$m]->{'username'}) >10 || length($users[$m]->{'username'}) <3) {
            
            $errormessage .= '第'.($m+2).'行用户名 ';
            next ;
        }
        if (length($users[$m]->{'passwd'}) <6) {
            $errormessage .= '第'.($m+2).'行密码 ';
            next ;
        }
        if ($users[$m]->{'lifetime'} ne '' ) {
            if ($users[$m]->{'lifetime'} >60 || $users[$m]->{'lifetime'} <30) {
                $errormessage .= '第'.($m+2).'行老化时间 ';
                next ;
            }
        }
        my @ip_mac_check = split(/\r?\n/,$users[$m]->{'bindmess'});
        my $detail_flag = 0 ;
        for (my $n = 0; $n < @ip_mac_check; $n++) {
            if ($ip_mac_check[$n] =~ /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}$/ ||
                $ip_mac_check[$n] =~ /^([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2})$/ ||
                $ip_mac_check[$n] =~ /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}\/([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2})$/) {
                    
            }else{
                $errormessage .= '第'.($m+2).'行绑定信息 ';
                    $detail_flag = 1 ;
                    
                    last ;
            }
        }
        if ($detail_flag eq 1) {
            next ;
        }

        my %par_user ;
        $par_user{'uname'} = $users[$m]->{'username'};
        $par_user{'pwd'} = $users[$m]->{'passwd'};
        $par_user{'outtime'} = $users[$m]->{'lifetime'};
        $users[$m]->{'bindmess'} =~ s/\r?\n/\&/g;
        if ($users[$m]->{'bindmess'} =~ /\./ && $users[$m]->{'bindmess'} !~ /\:/) {
            $par_user{'bind_info'} = 'ip';
            $par_user{'binding_info_ip'} = $users[$m]->{'bindmess'};
        }elsif($users[$m]->{'bindmess'} =~ /\:/ && $users[$m]->{'bindmess'} !~ /\./){
            $par_user{'bind_info'} = 'mac';
            $par_user{'binding_info_mac'} = $users[$m]->{'bindmess'};
        }elsif($users[$m]->{'bindmess'} =~ /\:/ && $users[$m]->{'bindmess'} =~ /\./){
            $par_user{'bind_info'} = 'ipmac';
            $par_user{'binding_info_ipmac'} = $users[$m]->{'bindmess'};
        }else{
            $par_user{'bind_info'} = 'no_bind';
        }

        if ($default_group_id eq '') {
            $par_user{'group_addr'} = 'j1_18';
        }else{
            $par_user{'group_addr'} = $default_group_id ;
        }

        my $record = &get_config_record( \%par_user , 1); # dont_encode
        my $flag = 0;
        my $item_id ;
        for (my $i = 0; $i < @lines; $i++) {
            if($par_user{'uname'} eq (split(",",$lines[$i]))[0]){
                $flag = 1 ;
                $item_id = $i ;
            }
        }
        &debug2file("$m,$flag");
        if ($flag eq 0) {
            &debug2file("$m,$flag,$continue_or_skip");
            ( $status, $mesg ) = &append_one_record( $conf_file, $record );
        }else{
            if ($continue_or_skip ne 'skip_import') {
                &debug2file("$m,$item_id,$flag,$continue_or_skip");
                ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
            }
        }
    } 
    if ($errormessage ne '') {
        $errormessage = 'excel中 '.$errormessage.'数据格式有误，自动跳过该数据'; 
    }  
}
sub uploads($$){
    my $cgi = new CGI;
    my $uploadname = shift;
    my $upload_dir = shift;
    my $file_length = 0;
    my $upload_filehandle = $cgi->param('file_lib');
    my $upload_filename = $upload_filehandle;
    my @splited_filenames = split(/\./, $upload_filename);
    foreach my $splited_filename (@splited_filenames)
    {
        $file_length++;
    }
    if($file_length == 0)
    {
        $errormessage = '请选择一个xls文件再上传！';
    } else {
        $file_length--;
        if ($splited_filenames[$file_length] eq 'xls')
        {
            my $filename = $upload_dir.$uploadname;
            if(! -e $filename){
                system("touch $filename");
            }
            open ( UPLOADFILE, ">$filename" ) or die "$!";
            binmode UPLOADFILE;
            while ( <$upload_filehandle> )
            {
                print UPLOADFILE;
            }
            close UPLOADFILE;

        } else {
            $errormessage = '只支持处理xls文件！';
        }
    }
}
sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_list_div();
    &closepage();
}

sub display_list_div() {
    printf<<EOF
    <div id="mesg_box_user" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_user_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="import_panel" style="width: 96%;margin: 20px auto;"></div>
    <div id="user_group_panel" class="container"></div>

    <div id="panel_group_father" class="container" >
        <div id="panel_user_group" style="width:18%;float:left;">
            
            <div id="user_group_title" >
                <div>用户组列表</div>
                <span class="opt-tools" style="float: right;">
                    <input type="text" id="cat_tree_search" placeholder="查询"">
                </span>
            </div>
                <div id="cat_tree"></div>
            </ul>   
        </div>
        <div id="panel_user_list" style="width:81%;float:left;"></div>

    </div>

EOF
    ;
}
sub upload_download($) {
    my $action_type = shift ;
    my $file = $templet;
    my $file_print = '导入用户模板';
    if ($action_type eq 'export') {
        $file = "/tmp/auth_users.xls";
        if (!-e $file) {
            system("touch $file");
        }
        `sudo /usr/local/bin/excelImportExport.py -a export -f /var/efw/AAA/user`;
        $file_print = '导出用户列表';
    }
        if( -e "$file"){
            open(DLFILE, "<$file") || Error('open', "$file");  
            @fileholder = <DLFILE>;  
            close (DLFILE) || Error ('close', "$file"); 
            print "Content-Type:application/x-download\n";  
            print "Content-Disposition:attachment;filename=".$file_print.".xls\n\n";
            print @fileholder;
            exit;
        }
        else{
            print "Content-type:text/html\n\n";
            print qq{<html><head><title>The file doesn't exist.</title></head><body><br/><br/>
                <br/><center><h1>The file does not exist.</h1></center></body></html>};
            exit;
        }
}
sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};
    
    my @lines;
    ( $status, $mesg ) = &read_config_lines($conf_file,\@lines);
    if ($status ne '0') {
        system("touch $conf_file");
    }
    if($item_id ne ''){
        delete $lines[$item_id];
    }

    my ( $status, $mesg ) = ( -1, "未保存" );

    foreach (@lines){
        if ($par{'description'} ne '') {
            
                if($par{'description'} eq (split(",",$_))[8]){
                    ( $status, $mesg ) = ( -2, "名称 ".$par{'description'}." 已占用" );
                    last;

            }

        }
    }
    foreach (@lines){
        if ($par{'uname'} ne '') {
            
                if($par{'uname'} eq (split(",",$_))[0]){
                    ( $status, $mesg ) = ( -2, "用户名“".$par{'uname'}."”已占用" );
                    last;

            }

        }
    }
    if( $item_id eq '' ) {
        if($status != -2){
            ( $status, $mesg ) = &append_one_record( $conf_file, $record );
            $log_oper = "add";
        }
    } else {
        # my @item_old = split(",",$lines[$item_id]);
        # my @item_new = split(",",$record);
        # if($item_old[1] ne $item_new[1]){
            
        # }
        if($status != -2){
            ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
            $log_oper = "edit";
        }
    }

    if( $status == 0 ) {
        $reload = 0;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
}
sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines_ref = ();
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );
    
    my $record_num = @lines;
    my $search = $par{'search'};
    my $user_data_addr = $par{'user_data_addr'};
    my $group_addr = $par{'group_addr'};
    if ($group_addr) {
        $user_data_addr = $group_addr;
    }
    

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
            push(@content_array, \%conf_data);
            $total_num++;
        }
    }else{
        ( $status, $error_mesg, $total_num ) = &get_content( \@content_array );
    }

    if($user_data_addr){

        for(my $i = 0; $i < @content_array; $i++){
 
            if ($user_data_addr eq @content_array[$i]->{'user_group'}) {
                push(@lines_ref,@content_array[$i]);
            }

        }
        %ret_data->{'detail_data'} = \@lines_ref;
        $total_num = scalar(@lines_ref);
    }else{
        %ret_data->{'detail_data'} = \@content_array;

    }


   
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    # %ret_data->{'page_size'} = $PAGE_SIZE;
    
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}


sub delete_data() {
    my @lines = ();
    &read_config_lines($conf_file,\@lines);
    my $ip = (split(",",$lines[$par{'id'}]))[2];
    `$cmd_logout $ip`;
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});
    
    if($status eq '0'){
        $mesg = "删除成功";
        `sudo /usr/local/bin/ipslog_parserd.py`;
    }

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;
    $log_oper = "del";

    send_status($status,0,$mesg);
    # my $ret = $json->encode(\%ret_data);
    # print $ret;
}

sub move_to() {
    my $move_data = $par{'move_data'};
    my @move_data_arr = split(/,/,$move_data);
    my $move_to_num = $par{'move_to_num'};

    my @lines = ();
    &read_config_lines( $conf_file, \@lines );

    my $len = scalar( @lines );

    my @new_lines = ();
    for ( my $i = 0; $i < $len; $i++ ) {
      
        for (my $j = 0; $j < @move_data_arr; $j++) {
            chomp(@lines[$i]);
            my @temp = split(/,/, $lines[$i]);
            if ($temp[10] eq $move_data_arr[$j]) {
                $temp[11] = $move_to_num;
                $lines[$i] = join(",",@temp);
            }
        }
        push(@new_lines,$lines[$i]);
    }

    my ( $status, $mesg ) = &write_config_lines( $conf_file, \@new_lines );

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub delete_group_item() {
    my $user_group_data = $par{'user_group_data'};
    my @user_group_data_arr = split(/,/,$user_group_data);

    my @lines = ();
    &read_config_lines( $conf_file, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $len = scalar( @lines );
    #===删除数据===#
    my @new_lines = ();
    for ( my $i = 0; $i < $len; $i++ ) {

        chomp(@lines[$i]);
        my @temp = split(/,/, $lines[$i]);

        for (my $j = 0; $j < @user_group_data_arr; $j++) {

            if( $temp[11] eq $user_group_data_arr[$j] ) {
                #删除用户
                @lines = grep(/[^$lines[$i]]/,@lines);
                #删除用户后，@lines中length与index都发生变化
                $i--;
                $len--;
                &debug( "\t删除第<$i>行数据$lines[$i]..." );

            } else {

                &debug( "\t保留第<$i>行数据$lines[$i]..." );

            }
        }
        
    }
   
    my ( $status, $mesg ) = &write_config_lines( $conf_file, \@lines );

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret;
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
    for ( my $i = $from_num; $i < $total_num; $i++ ) {
        my %config = &get_config_hash( $lines[$i] );
        if( $config{'valid'} ) {
            $config{'id'} = $i;
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
    my @temp = split(/,/, $line_content);
    
    $config{'uname'}   = $temp[0];
    $config{'pwd'}   = $temp[1];
    $config{'pwd_again'}   = $temp[1];
    $config{'outtime'}   = $temp[5];
    my $userstate = "offline";
    if($temp[4] > 0 && $temp[6] == 0){        
        $userstate = "online";
        
    }elsif($temp[4] == 0 && $temp[6] > 0){
        $userstate = "forbidden";
       

    }else{
        $userstate = "offline";
        
    }
    $config{'userstate'}   = $userstate;
	#============列表的ip组装-BENGIN================#
    
    my $bind_detail = $temp[7];
    $bind_detail =~ s/&/ | /g;
	# my %temproray = &output_ip_handle($temp[7]);
	$config{'bind_detail'} = $bind_detail;
	# $config{'ip_name'} = $temproray{'ip_name'};
	# $config{'ip_mask'} = $temproray{'ip_mask'};
	# $config{'ip_range'} = $temproray{'ip_range'};

    #============列表的ip组装-END===================#
    $config{'description'}   = $temp[8];
    #============自定义字段组装-END===========================#
    #
    my $strategy = $temp[9];
    if ($strategy eq '1') {
        $config{'strategy'} = '有';
    }else{
        $config{'strategy'} = '无';
    }    
    
    $config{'user_id'} = $temp[10];

    $config{'user_group'} = $temp[11];

    return %config;
}

sub get_config_record($$) {
    my $hash_ref = shift;
    # my $ctx = Digest::MD5->new;
    my $dont_encode_pwd = shift;
    my @record_items = ();
    my $uname = $hash_ref->{'uname'};
    push( @record_items, $uname );

    my $pwd = $hash_ref->{'pwd'};
    if ($pwd eq '') {
        my @lines;
        &read_config_lines( $conf_file, \@lines);
        foreach my $line (@lines){
            my @temp = split(',',$line);
            if($hash_ref->{'uname'} eq $temp[0]) {
                $pwd = $temp[1];
            }
        }
        push( @record_items, $pwd );
    } else {
	# TODO: use base64 instead of md5
	# 如果表明了不要在b64
	if (!$dont_encode_pwd){
		$pwd = encode_base64($pwd);
		$pwd =~ s/\n//g;
	        # $ctx->add($hash_ref->{'pwd'});
        	#my $pwd = $ctx->hexdigest;
	}
        push( @record_items, $pwd );
    }
    
    push( @record_items, "0" );
    push( @record_items, '0' );
    push( @record_items, '0' );

    &readhash( $conf_file_settings, \%settings );
    my $outtime = $hash_ref->{'outtime'};
    # if ( $uname eq '' && $outtime eq '') {
        # $outtime = '';
    # }else{
       if($outtime eq ''){
            $outtime = $settings{'Timeout'};
        }
    # }
    
    push( @record_items, $outtime );
    push( @record_items, '0' );


	#============放入配置文件的绑定信息组装-BENGIN================#
	
    my $bind_info = $hash_ref->{'bind_info'};

    my $bind_detail;

    if ($bind_info eq 'ip') {
        $bind_detail = $hash_ref->{'binding_info_ip'};
        $bind_detail = "IP="."$bind_detail";
    } elsif ($bind_info eq 'mac') {
        $bind_detail = $hash_ref->{'binding_info_mac'};
        $bind_detail = "MAC="."$bind_detail";
    } elsif ($bind_info eq 'ipmac') {
        $bind_detail = $hash_ref->{'binding_info_ipmac'};
        $bind_detail = "IP/MAC="."$bind_detail";
    }else{
        $bind_detail = '';
    }

    $bind_detail =~ s/\r\n/&/g;
    
    push( @record_items, $bind_detail );
  

	#============放入配置文件的ip_name组装-END====================#
    my $description = $hash_ref->{'description'};
    $description =~ s/,/，/g;
    push( @record_items, $description );

    my $strategy = $hash_ref->{'strategy'};
    push(@record_items, $strategy);


    my $id = &get_serviceId();
    push(@record_items, $id);  

    my $group_addr = $hash_ref->{'group_addr'};
    push(@record_items, $group_addr);

    return join (",", @record_items);
}

sub toggle_enable($$) {
    my $item_id = shift;
    my $enable = shift;
    my $operation = "启用";
    $log_oper = 'enable';
    if ( $enable ne "on" ) {
        $operation = "禁用";
        $log_oper = 'disable';
    }

    my ( $status, $mesg, $line_content ) = &get_one_record( $conf_file, $item_id );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, $mesg );
        return;
    }

    my %config = &get_config_hash( $line_content );
    $config{'enable'} = $enable;
    $line_content = &get_config_record(\%config);

    my ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $line_content );
    if( $status != 0 ) {
        $mesg = "操作失败";
    }

    &send_status( $status, $mesg );
    return;
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
    $log_oper = 'apply';
    &send_status( 0, 0, $msg );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
#启用被禁用的用户
sub enable_forbidded_item(){
    my $item_id = $par{'id'};
    my $userstate = $par{'userstate'};
    my @lines = ();
    &read_config_lines($conf_file,\@lines);
    my @data_line = split(",",$lines[$item_id]);
    $data_line[6] = "0";
    &update_one_record( $conf_file, $item_id, join(",",@data_line) );
    &send_status( 0, 0, "success" );
}
sub output_ip_handle() {
	my $tem = shift;
	my @tem = split(/&/,$tem);
	$tem =~ s/&/<br \/>&nbsp/g;
	my %tem;
	$tem{'ip_detail'} = $tem;
	my $count = 1;
	foreach(@tem) {
		
		if (/\//) {
		$tem{'ip_mask'} = $_;
		} else {
			if(/-/) {
				$tem{'ip_range'} = $_;
			} else {
				$tem{"ip_name"} = $_;
				$count++;
			}
		}
		
		
	}
	return %tem;	


}

sub get_serviceId() {
    my @lines;
    my @max_id;
    my ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);
    foreach(@lines){
        my @lines_ref = split(/,/,$_);
        push(@max_id,$lines_ref[10]);
    }
    
    @max_id=sort {$a<=>$b}@max_id;
    return $max_id[$#max_id] ? $max_id[$#max_id]+1 :1 ;

}

sub up_down_tree() {
    my @lines_ref;
    my ( $status, $mesg ) = &read_config_lines($usergroup_file,\@lines_ref);
    if ($status ne 0) {
        &send_status($status,$mesg);
        return;
    }
    my $json_data;
    foreach(@lines_ref) {
        $json_data = $json_data . $_; 
    }  
    # print $json_data;
    $json_data = $json->decode($json_data);
    # print Dumper($json_data);
    my $temp; 
    my $temp1;
    my $json_children = $json_data->{'children'};
    # my @json_children_arr =$json_children;
    # print @json_children[0];

    my $len = scalar(@$json_children);
    # print $len.'-';
    for (my $i = 0; $i < $len; $i++) {
        # print $i.'---';
        # print @$json_children[$i]->{'id'};
        # print $par{'node'}.'---';
        if (@$json_children[$i]->{'id'} eq $par{'node'}) {

            $temp = $i;
        }
    }
    # print @$json_children[0]->{'id'}; 
    # print $par{'node'};
    # print $temp;
    # print $par{'derection'};

    if ($par{'derection'} eq 'up') {
        $temp1 = @$json_children[$temp-1];
        @$json_children[$temp-1] = @$json_children[$temp];
        @$json_children[$temp] = $temp1;
        
    }else{
        $temp1 = @$json_children[$temp+1];  
        @$json_children[$temp+1] = @$json_children[$temp]; 
        @$json_children[$temp] = $temp1;
             
    }
    $json_data->{'children'} = $json_children;
    my $json_ret = $json->encode(\%$json_data);
    # print $json_data;
    my @lines;
    $lines[0] = $json_ret;
    # print Dumper($lines[0]);
    # print Dumper($lines[0]);
    ( $status, $mesg ) = &write_config_lines($usergroup_file,\@lines);#将树结构写进配置文件
    &send_status( $status, $mesg );
    return;
}
#获得树形数据
sub get_tree_data() {
    my @lines = ();
    my ( $status, $error_mesg)= &read_config_lines($usergroup_file,\@lines);
    # print $status;
    if ($status ne 0) {
        system("touch $usergroup_file");
        print $status;
        return;
    }
    # print @lines;
    my $json_data;
    # if (@lines eq '') {
    #     print '-1';
    #     return;
    # }else{
        foreach(@lines) {
            $json_data = $json_data . $_; 
        }    
    # }
    if ($json_data eq '') {
        print '-1';
        return;
    }
    print $json_data;
    
}

sub update_tree() {
   
    my $tree_json = $par{'tree_json'};
    my @lines;
    $lines[0] = $tree_json;
    my ( $status, $mesg ) = &write_config_lines($usergroup_file,\@lines);#将树结构写进配置文件
    my %hash ;
    if( $status != 0 ) {
        %hash->{'status'} = 'fail';
    } else {
        %hash->{'status'} = 'success';
    }
    my $result = $json->encode(\%hash);
    print $result;
}

sub show_user_num() {
    my $all_id = $par{'all_id'};

    my @all_id_arr = split(/,/,$all_id);#字符串转换成数组


    my @lines = ();
    &read_config_lines($conf_file,\@lines);

    my %page_num_hash;
    $page_num_hash{$_} = "0" foreach @all_id_arr;#将数组中内容赋给hash的key
    for (my $i = 0; $i < @lines; $i++) {

        chomp(@lines[$i]);#去掉换行符
        my @temp = split(/,/, $lines[$i]);
        foreach my $key ( keys %page_num_hash ) {#遍历hash

            if ($key eq $temp[11]) {

                $page_num_hash{$key} ++;
            }
        }    
    }
    my $result = $json->encode(\%page_num_hash);#hash转换成json
    print $result;
}

