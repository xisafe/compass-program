#!/usr/bin/perl
#author: LiuJulong
#createDate: 2015/04/07
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_dir_ftype;     #文件类型所存放的文件夹
my $conf_file;          #规则所存放的文件
my $conf_file_user;     #NCSA用户所存放的文件
my $conf_file_group;    #NCSA组所存放的文件
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
my $cmd_judgehavp;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my @zones = ();
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir         = '/proxy';                                #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir           = "/var/efw".$custom_dir;                  #规则所存放的文件夹
    $conf_dir_ftype     = "/var/efw".$custom_dir."/MIME";                  #文件类型所存放的文件夹
    $conf_file          = $conf_dir.'/policyrules';                #发件人信息所存放的文件
    $conf_file_user     = $conf_dir.'/ncsausers';                  #发件人信息所存放的文件
    $conf_file_group    = $conf_dir.'/ncsagroups';                 #发件人信息所存放的文件
    $need_reload_tag    = $conf_dir.'/add_list_need_reload_policy';#启用信息所存放的文件
    $cmd                = "/usr/local/bin/restartsquid -f";
    $cmd_judgehavp      = "sudo /usr/local/bin/judge_virus_enable.py -m clamav";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/access_policy_init.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#
    &get_useable_zones();

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
    if ($action eq 'load_data' && $panel_name eq 'list_panel') {
        #==下载数据==#
        &load_data();
    } 
    elsif ($action eq 'load_data' && $panel_name eq 'list_panel_ftype') {
        #==下载数据==#
        &load_data_ftype();
    }elsif ($action eq 'save_data' && $panel_name eq 'add_panel') {
        #==保存数据==#
        &save_data();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
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
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_list_div();
    &closepage();
}

sub display_list_div() {
    my $html_ftypes = "";
    my @all_types = &get_all_ftype();
    $html_ftypes .= "<ul style='list-style-type:none;margin-left:20px;'>";
    foreach my $item(@all_types){
        my $text_parent = ${$item}{'parent'};
        if(${$item}{'parent'} eq 'audio'){
            $text_parent = "+音频";
        }elsif(${$item}{'parent'} eq 'compression'){
            $text_parent = "+压缩文档";
        }elsif(${$item}{'parent'} eq 'html'){
            $text_parent = "+网页文档";
        }elsif(${$item}{'parent'} eq 'other'){
            $text_parent = "+其他";
        }elsif(${$item}{'parent'} eq 'picture'){
            $text_parent = "+图片";
        }elsif(${$item}{'parent'} eq 'text'){
            $text_parent = "+文本文档";
        }elsif(${$item}{'parent'} eq 'video'){
            $text_parent = "+视频";
        }
        $html_ftypes .= "<li style='margin-top:5px'><input type='checkbox' value=".${$item}{'parent'}." onclick='select_ftype_all(this);'><span style='margin-left:3px;cursor:pointer;' title=".${$item}{'parent'}." onclick='toogle(this);'>".$text_parent."</span>";
        $html_ftypes .= "<ul style='list-style-type:none;margin-left:30px;display:none;' id=".${$item}{'parent'}.">";
        my $href_lines = ${$item}{'lines'};
        foreach my $line(@$href_lines){
            my $ftype = (split(" ",$line))[0];
            my $value_ftype = (split(" ",$line))[1];
            my $id = $ftype;
            $id =~ s/\.//g;
            $html_ftypes .= "<li><input type='checkbox' id=".$id." class='ctr_ftype ".${$item}{'parent'}."' value=".$value_ftype."><span style='margin-left:3px;'>".$ftype."</span></li>";
        }
        $html_ftypes .= "</ul>";
        $html_ftypes .= "</li>";
    }
    $html_ftypes .= "</ul>";
    printf<<EOF
    <div id="mesg_box_policy" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_policy_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_policy_list" style="width: 96%;margin: 20px auto;"></div>
    <div id="cover_filetype_list" class="popup-mesg-box-cover" style="z-index: 199;display:none;"></div>
    
    <div id="panel_filetype_list" class="popup-mesg-box-body mesg-box-s" style="z-index: 200; margin-top: -258.5px;display:none;">
      <div id="add_panel_header_id_for_add_panel" class="add-panel-header">
        <div id="add_panel_title_for_add_panel" class="add-panel-title">
          <span id="add_panel_title_text_for_add_panel" class="add-panel-title-text">选择文件类型</span>
        </div>
        <span id="add_panel_close_for_add_panel" class="add-panel-close-button" onclick="close_panel_ftype();"></span>
      </div>
      
      <div class="container-main-body" style="height:300px;">
        $html_ftypes
      </div>
      
      <div class="add-panel-footer">
        <input id="add_panel_add_button_id_for_add_panel" class="add-panel-form-button" value="确定" type="button" onclick="save_ftype();"/>
        <input id="add_panel_cancel_button_id_for_add_panel" class="add-panel-form-button" value="撤销" type="button" onclick="close_panel_ftype();"/>
      </div>
    </div>
EOF
    ;
}


sub save_data() {
    my $reload = 0;
    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};
    
    my @lines;
    &read_config_lines($conf_file,\@lines);
    my $len = @lines;
    
    if($item_id ne ''){
        delete $lines[$item_id]
    }

    my ( $status, $mesg ) = ( -1, "未保存" );
    foreach (@lines){
        if($par{'policy_name'} eq (split(",",$_))[0]){
            ( $status, $mesg ) = ( -2, $par{'policy_name'}."已占用" );
        }
    }
    if( $item_id eq '' ) {
        if($status != -2){
            if($par{'position'} eq 'last' || $len < 1){
                ( $status, $mesg ) = &append_one_record( $conf_file, $record );
            }else{
                ( $status, $mesg ) = &insert_one_record( $conf_file, $par{'position'}, $record );
            }
        }
    } else {
        if($status != -2){
            if($par{'position'} eq 'last' || $par{'position'} eq ($len-1)){
                ( $status, $mesg ) = &delete_one_record( $conf_file, $item_id );
                ( $status, $mesg ) = &append_one_record( $conf_file, $record );
            }else{
                ( $status, $mesg ) = &delete_one_record( $conf_file, $item_id );
                ( $status, $mesg ) = &insert_one_record( $conf_file, $par{'position'}, $record );
            }
        }
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
}
sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file, \@lines );
    
    my $record_num = @lines;
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
            $conf_data{'position'} = $i;
            push(@content_array, \%conf_data);
            $total_num++;
        }
    }else{
        ( $status, $error_mesg, $total_num ) = &get_content( \@content_array );
    }
    
    #装载用户和组的数据
    my @lines_users = ();
    my @lines_groups = ();
    my @users = ();
    my @groups = ();
    &read_config_lines($conf_file_user,\@lines_users);
    &read_config_lines($conf_file_group,\@lines_groups);
    foreach my $line_user(@lines_users){
        my $user = (split(":",$line_user))[0];
        push(@users,$user);
    }
    foreach my $line_group(@lines_groups){
        my $group = (split(",",$line_group))[0];
        push(@groups,$group);
    }
    
    #获取文件类型集合
    #my @file_types = &get_all_ftype("all");
    
    #获取过滤模板
    my @names_template = ();
    my @filter_templates = split(/\n/,`ls "/var/efw/dansguardian/profiles" -F | grep '/'`);
    foreach(@filter_templates){
        $_ =~ s/\///g;
        my $temp_file = "/var/efw/dansguardian/profiles/".$_."/settings";
        my $value_content = $_;
        my %settings_temp;
        &readhash($temp_file,\%settings_temp);
        my %hash_content;
        $hash_content{'NAME'} = $settings_temp{'NAME'};
        $hash_content{'VALUE'} = $value_content;
        push(@names_template,\%hash_content);
    }
    
    #获取病毒扫描是否激活
    my $is_active_havp = "no";
    system("$cmd_judgehavp");
    if(($? >> 8) == 0){
        $is_active_havp = "yes";
    }

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'useable_zones'} = \@zones;
    %ret_data->{'filter_templates'} = \@names_template;
    %ret_data->{'users'} = \@users;
    %ret_data->{'groups'} = \@groups;
    #%ret_data->{'file_types'} = \@file_types;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'is_active_havp'} = $is_active_havp;
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
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'});
    my $reload = 0;
    if($status eq 0){
        $mesg = "删除成功";
        $reload = 1;
        &create_need_reload_tag();
    }

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;
    %ret_data->{'reload'} = $reload;

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
            $config{'position'} = $i;
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
    $config{'policy_name'}   = $temp[0];
    $config{'enable'}   = $temp[1];
    $config{'access_policy'}   = $temp[2];
    $config{'auth_type'}   = $temp[3];
    $config{'group'}   = $temp[4];
    $config{'user'}   = $temp[5];
    $config{'enable_time_limit'}   = $temp[6];
    my @data_live_days = split(//,$temp[7]);
    $config{'live_days'}   = join("\|",@data_live_days);
    $config{'start_hour'}   = $temp[8];
    $config{'start_min'}   = $temp[9];
    $config{'end_hour'}   = $temp[10];
    $config{'end_min'}   = $temp[11];
    $config{'filter_template'}   = $temp[12];
    $config{'type_r'}   = $temp[13];
    if($config{'type_r'} eq 'ip'){
        $config{'ip_r'}   = $temp[14];
    }elsif($config{'type_r'} eq 'zone'){
        $config{'source_zone'}   = $temp[14];
    }elsif($config{'type_r'} eq 'mac'){
        $config{'mac_r'}   = $temp[14];
    }
    $config{'source'}   = $temp[14];
    $config{'type_d'}   = $temp[15];
    if($config{'type_d'} eq 'ip'){
        $config{'ip_d'}   = $temp[16];
    }elsif($config{'type_d'} eq 'zone'){
        $config{'dest_zone'}   = $temp[16];
    }elsif($config{'type_d'} eq 'domain'){
        $config{'domain_d'}   = $temp[16];
    }
    $config{'dest'}   = $temp[16];
    $config{'file_type'}   = $temp[17];
    $config{'browser'}   = $temp[18];
    
    
    
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'policy_name'} );
    push( @record_items, $hash_ref->{'enable'} );
    push( @record_items, $hash_ref->{'access_policy'} );
    # push( @record_items, $hash_ref->{'auth_type'} );
    push( @record_items, "none" );
    # push( @record_items, $hash_ref->{'group'} );
    # push( @record_items, $hash_ref->{'user'} );
    push( @record_items, "" );
    push( @record_items, "" );
    push( @record_items, $hash_ref->{'enable_time_limit'} );
    my $live_days = $hash_ref->{'live_days_save'};
    $live_days =~ s/\|//g;
    push( @record_items, $live_days );
    my ($start_hour,$start_hour,$end_hour,$end_min) = ("","","","");
    if($hash_ref->{'enable_time_limit'} eq 'on'){
        $start_hour = $hash_ref->{'start_hour'};
        $start_min = $hash_ref->{'start_min'};
        $end_hour = $hash_ref->{'end_hour'};
        $end_min = $hash_ref->{'end_min'};
    }
    push( @record_items, $start_hour );
    push( @record_items, $start_min );
    push( @record_items, $end_hour );
    push( @record_items, $end_min );
    push( @record_items, $hash_ref->{'filter_template'} );
    push( @record_items, $hash_ref->{'type_r'} );
    my $source = "";
    if($hash_ref->{'type_r'} eq "zone"){
        $source = $hash_ref->{'source_zone'};
    }elsif($hash_ref->{'type_r'} eq "ip"){
        $source = $hash_ref->{'ip_r'};
    }elsif($hash_ref->{'type_r'} eq "mac"){
        $source = $hash_ref->{'mac_r'};
    }
    push( @record_items, $source );
    
    push( @record_items, $hash_ref->{'type_d'} );
    my $dest = "";
    if($hash_ref->{'type_d'} eq "zone"){
        $dest = $hash_ref->{'dest_zone'};
    }elsif($hash_ref->{'type_d'} eq "ip"){
        $dest = $hash_ref->{'ip_d'};
    }elsif($hash_ref->{'type_d'} eq "domain"){
        $dest = $hash_ref->{'domain_d'};
    }
    push( @record_items, $dest );
    push( @record_items, $hash_ref->{'file_type'} );
    #push( @record_items, $hash_ref->{'browser'} );
    push( @record_items, "" );
    
    return join (",", @record_items);
}

sub toggle_enable($$) {
    my $item_id = shift;
    my $enable = shift;
    my $reload = 0;

    my ( $status, $mesg, $line_content ) = &get_one_record( $conf_file, $item_id );
    if( $status != 0 ) {
        $mesg = "操作失败";
        &send_status( $status, 0, $mesg );
        return;
    }

    my %config = &get_config_hash( $line_content );
    $config{'enable'} = $enable;
    $line_content = &get_config_record(\%config);

    my ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $line_content );
    if( $status != 0 ) {
        $mesg = "操作失败";
    }else{
        $mesg = "操作成功";
        $reload = 1;
        &create_need_reload_tag();
    }

    &send_status( $status, $reload, $mesg );
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
    &send_status( 0, 0, $msg );
}
sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}
#获取可用区域
sub get_useable_zones(){
    my $valid_zones_ref = validzones();
    my @valid_zones = @$valid_zones_ref;
    my $zone_display;
    foreach $zone (@valid_zones) {
        my %hash_zone;
        if (uc($zone) eq "RED") {
            next;
        }
        if (uc($zone) eq "GREEN") {
            $zone_display = "LAN";
        }
        if (uc($zone) eq "ORANGE") {
            $zone_display = "DMZ";
        }
        if (uc($zone) eq "BLUE") {
            $zone_display = "WAN";
        }
        $hash_zone{'value'} = $zone;
        $hash_zone{'display'} = $zone_display;
        push(@zones, \%hash_zone);
    }
    return @zones;
}
#获取文件类型集合
sub get_all_ftype(){
    my @types = ();
    
    @types = split(/\n/,`ls $conf_dir_ftype -F | grep '.'`);
    
    my @all_types = ();
    foreach my $type (@types){
        my @lines_ptype = ();
        &read_config_lines($conf_dir_ftype.'/'.$type,\@lines_ptype);
        my %hash_item;
        $hash_item{'parent'} = $type;
        $hash_item{'lines'} = \@lines_ptype;
        push(@all_types,\%hash_item);
    }
    return @all_types;
}
sub load_data_ftype(){
    my %ret_data;
    my @content_array;
    my @types = split(/\n/,`ls $conf_dir_ftype -F | grep '.'`);
    my $parent_type = $par{'parent_type'};
    my ( $status, $error_mesg, $total_num ) = ("","","");
    @content_array = &get_all_ftype($parent_type);
    $total_num = @content_array;
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'ftypes'} = \@types;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    # %ret_data->{'page_size'} = $PAGE_SIZE;
    

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}