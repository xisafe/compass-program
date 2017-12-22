#!/usr/bin/perl
#author: LiuJulong
#createDate: 2015/04/08
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_dir_default;   #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $file_settings_default;
my $conf_file_havp;     #反病毒设置所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %settings_default;
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $cmd;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $status_havp;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir            = '/dansguardian/profiles';                  #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir              = "/var/efw".$custom_dir;                    #规则所存放的文件夹
    $conf_dir_default      = "/var/efw/dansguardian/default";           #默认规则所存放的文件夹
    $file_settings_default = $conf_dir_default.'/settings';
    $conf_file             = $conf_dir.'/notice';        
    $conf_file_havp        = '/var/efw/havp/whitelist';                 #反病毒设置所存放的文件
    $conf_file_url         = '/var/efw/proxy/urlconfig';                #urllist所存放的文件
    $need_reload_tag       = $conf_dir.'/add_list_need_reload_notice';  #启用信息所存放的文件
    $cmd                   = "sudo /usr/local/bin/judge_virus_enable.py -m clamav";
    $status_havp           = "off";
    
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/filter_template_init.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#

    #&make_file();#检查要存放规则的文件夹和文件是否存在
    
    #判断启用杀毒与否
    system("$cmd");
    if(($? >> 8) == 0){
        $status_havp = "on";
    }
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
    elsif ($action eq 'load_data' && $panel_name eq 'urllist_panel') {
        #==下载数据==#
        &load_data_url();
    } 
    elsif ($action eq 'save_data' && $panel_name eq 'add_panel') {
        #==保存数据==#
        &save_data();
    }
    elsif ($action eq 'judge_havp') {
        #==判断启用杀毒==#
        &judge_havp();
    }
    elsif ($action eq 'save_url') {
        #==保存反病毒设置==#
        &save_data_url();
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
    printf<<EOF
    <div id="mesg_box_template" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
    &display_havp_div();
    printf<<EOF
    <div id="panel_template_add" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_template_keywords" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_template_urllist" style="width: 96%;margin: 20px auto;"></div>
    <div id="panel_template_list" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}


sub save_data() {
    my $reload = 0;
    my @record = &get_config_record( \%par );
    my $item_id = $par{'id'};
    my @array_dir = split(/\n/,`ls $conf_dir -F | grep '/'`);
    my $length_dirs = @array_dir;
    my $length_orignal = $length_dirs;
    if(!$length_dirs){
        $length_dirs = 2;
    }else{
        if($length_dirs eq 1){
            $length_dirs = 2;
            $length_dirs += 1;
        }else{
            $length_dirs += 2;
        }
        
        for(my $i=0;$i < $length_orignal;$i++){
            my $num = ($i+2);
            my $name_content = "content$num/";
            if($array_dir[$i] ne $name_content){
                $length_dirs = $num;
                last;
            }
        }
    }

    my ( $status, $mesg ) = ( -1, "未保存" );
    # foreach (@lines){
        # if($par{'title'} eq (split(",",$_))[0]){
            # ( $status, $mesg ) = ( -2, $par{'title'}."已占用" );
        # }
    # }
    
    my @template_names_pre = &get_all_template_names();
    my $len_template = @template_names_pre;
    if($len_template > 7){
        ( $status, $mesg ) = ( -2, "最多只能添加8个模板" );
    }
    my @template_names;
    if($item_id ne ''){
        @template_names = map($par{'NAME'} ne $_,@template_names_pre);
    }else{
        @template_names = @template_names_pre;
    }
    foreach(@template_names){
        if($par{'NAME'} eq $_){
            ( $status, $mesg ) = ( -2, $par{'NAME'}."已占用" );
        }
    }
    
    if( $item_id eq '' ) {
        $item_id = 'content'.$length_dirs;
        if($status != -2){
            ( $status, $mesg ) = &append_one_record_filter( $item_id, \@record );
        }
    } else {
        if($status != -2){
            ( $status, $mesg ) = &update_one_record_filter( $item_id, \@record );
        }
    }

    if( $status == 0 ) {
        #$reload = 1;
        #&create_need_reload_tag();
        #$mesg = "保存成功";
    }

    &send_status( $status, $reload, $mesg );
}
sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    @lines = split(/\n/,`ls $conf_dir -F | grep '/'`);
    
    my $record_num = @lines;
    my $search = $par{'search'};
    if($search){
        chomp($search);
        #===转换成小写，进行模糊查询==#
        $search = lc($search);
        for(my $i = 0; $i < $record_num; $i++){
            if($search ne ""){
                my $searched = 0;
                my $where = -1;
                my @lines_setting = ();
                &read_config_lines($conf_dir.'/'.$lines[$i].'settings',\@lines_setting);
                my @data = ();
                foreach(@lines_setting){
                    push(@data,(split("=",$_))[1]);
                }
                my @lines_ban = ();
                &read_config_lines($conf_dir.'/'.$lines[$i].'bannedphraselist',\@lines_ban);
                my $str_ban = join(",",@lines_ban);
                push (@data,$str_ban);
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
            my %conf_data = &get_config_hash($conf_dir.'/'.$lines[$i].'settings');
            my @key_words = ();
            &read_config_lines($conf_dir.'/'.$lines[$i].'bannedphraselist',\@key_words);
            my $str_key_words = join(",",@key_words);
            $str_key_words =~ s/\<//g;
            $str_key_words =~ s/\>//g;
            $conf_data{'KEY_WORDS'} = $str_key_words;
            
            if (! $conf_data{'valid'}) {
                next;
            }
            $conf_data{'id'} = @lines[$i];
            push(@content_array, \%conf_data);
            $total_num++;
        }
    }else{
        ( $status, $error_mesg, $total_num ) = &get_content( \@content_array );
    }
    
    #配置url库key-value
    

    %ret_data->{'detail_data'} = \@content_array;
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
    my ( $status, $mesg ) = &delete_several_records_filter($par{'id'});
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

    my @dirs = split(/\n/,`ls $conf_dir -F | grep '/'`);
    
    my ( $status, $error_mesg ) = (0,"");

    my $total_num = @dirs+1;
    if($total_num > 0){
        #加载默认过滤模板
        my $settings_file_default = $conf_dir_default."/settings";
        my $ban_file_default = $conf_dir_default."/bannedphraselist";
        my %config_settings_default = &get_config_hash($settings_file_default);
        $config_settings_default{'id'} = "content1";
        $config_settings_default{'undeletable'} = "true";
        if(-f $ban_file_default){
            my @key_words_defalut = ();
            &read_config_lines($ban_file_default,\@key_words_defalut);
            my $str_key_words_default = join(",",@key_words_defalut);
            $str_key_words_default =~ s/\<//g;
            $str_key_words_default =~ s/\>//g;
            $config_settings_default{'KEY_WORDS'} = $str_key_words_default;
        }
        push( @$content_array_ref, \%config_settings_default );
        
        foreach(@dirs){
            $_ =~ s/\///g;
            my $item_id = $_;
            my $settings_file = $conf_dir.'/'.$_."/settings";
            my $ban_file = $conf_dir.'/'.$_."/bannedphraselist";
            if(-f $settings_file){
                my %config_settings = &get_config_hash($settings_file);
                $config_settings{'id'} = $item_id;
                if(-f $ban_file){
                    my @key_words = ();
                    &read_config_lines($ban_file,\@key_words);
                    my $str_key_words = join(",",@key_words);
                    $str_key_words =~ s/\<//g;
                    $str_key_words =~ s/\>//g;
                    $config_settings{'KEY_WORDS'} = $str_key_words;
                    # my $len = @key_words;
                    # $config_settings{'KEY_WORDS'} = $settings_file;
                }
                push( @$content_array_ref, \%config_settings );
            }
        }
    }
    
    if( $total_num < $to_num ) {
        $to_num = $total_num;
    }

    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        #==全部加载===#
        $from_num = 0;
        $to_num = $total_num;
    }
    
    return ( $status, $error_mesg, $total_num );
}

sub get_config_hash($) {
    my $file_settings = shift;
    my %config;
    $config{'valid'} = 1;#默认是合法的行，如果有不合法的，将该字段置为0
    if (!-f $file_settings) {
        $config{'valid'} = 0;
        return %config;
    }
    #============自定义字段组装-BEGIN=========================#
    readhash($file_settings, \%config);
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_hash_url($) {
    my $line_content = shift;
    chomp($line_content);
    my %config;
    $config{'valid'} = 1;#默认是合法的行，如果有不合法的，将该字段置为0
    if ($line_content eq '') {
        $config{'valid'} = 0;
        return %config;
    }
    #============自定义字段组装-BEGIN=========================#
    my @temp = split(",", $line_content);
    $config{'type'}   = $temp[0];
    $config{'name'}   = $temp[1];
    $config{'description'}   = $temp[2];
    #$config{'path'}   = $temp[3];
    my @arr_path = split(/\//,$temp[3]);
    my $len_path = @arr_path;
    $config{'id'}   = $arr_path[5];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, 'NAME='.$hash_ref->{'NAME'} );
    #push( @record_items, 'HAVP='.$hash_ref->{'HAVP'} );
    push( @record_items, 'HAVP='.$status_havp );
    push( @record_items, 'URLLIST='.$hash_ref->{'URLLIST'} );
    push( @record_items, 'BLACK_WHITE='.$hash_ref->{'BLACK_WHITE'} );
    my $key_words = $hash_ref->{'KEY_WORDS'};
    $key_words =~ s/，/,/g;
    push( @record_items, $key_words );
    return @record_items;
}

sub toggle_enable($$) {
    my $item_id = shift;
    my $enable = shift;

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
#新增一个过滤模板
sub append_one_record_filter($$){
    my $folder = shift;
    $folder = "/".$folder;
    my $ref_record = shift;
    my @records = @$ref_record;
    my $setting_file_record = $conf_dir.$folder.'/settings';
    my $ban_file_record = $conf_dir.$folder.'/bannedphraselist';
    system("mkdir -p $conf_dir$folder");
    system("touch $setting_file_record");
    system("touch $ban_file_record");
    
    my $len_records = @records;
    for(my $i=0;$i<($len_records -1);$i++){
        system("echo '$records[$i]' >> $setting_file_record");
    }
    system("echo PICS_ENABLE=off >> $setting_file_record");
    system("echo PORT= >> $setting_file_record");
    system("echo NAUGHTYNESSLIMIT=160 >> $setting_file_record");
    
    my @array_key_words = split(/,/,$records[4]);
    foreach(@array_key_words){
        #my $line_one = "\<".$_."\>";
        system("echo '<'$_'>' >> $ban_file_record");
    }
    #system("echo $array_key_words[0] >> $ban_file_record");
    return (0,"添加成功");
}
#修改一个过滤模板
sub update_one_record_filter($$){
    my $folder = shift;
    $folder = "/".$folder;
    my $ref_record = shift;
    my @records = @$ref_record;
    my $setting_file_record = $conf_dir.$folder.'/settings';
    my $ban_file_record = $conf_dir.$folder.'/bannedphraselist';
    
    if($folder eq '/content1'){
        $setting_file_record = $conf_dir_default.'/settings';
        $ban_file_record = $conf_dir_default.'/bannedphraselist';
    }
    
    system("cat '' > $setting_file_record");
    for(my $i=0;$i<(@records -1);$i++){
        system("echo '$records[$i]' >> $setting_file_record");
    }
    system("echo PICS_ENABLE=off >> $setting_file_record");
    system("echo PORT= >> $setting_file_record");
    system("echo NAUGHTYNESSLIMIT=160 >> $setting_file_record");
    
    my @array_key_words = split(",",$records[4]);
    system("cat '' > $ban_file_record");
    foreach(@array_key_words){
        #my $line_one = "<".$_.">";
        system("echo '<'$_'>' >> $ban_file_record");
    }
    return (0,"修改成功");
}
#删除过滤模板
sub delete_several_records_filter($){
    my @ids = split("\&",shift);
    foreach(@ids){
        system("rm -rf $conf_dir'/'$_");
    }
    return (0,"删除成功");
}
#加载url数据
sub load_data_url(){
    my %ret_data;
    
    my @content_array;
    my @lines = ();
    my @lines_custom = ();
    #my @key_values_url = ();
    my %key_values_url;
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $conf_file_url.'/system', \@lines );
    ( $status, $error_mesg) = &read_config_lines( $conf_file_url.'/custom', \@lines_custom );
    
    my $total_num = @lines+@lines_custom;
    for ( my $i = 0; $i < @lines; $i++ ) {
        my %config = &get_config_hash_url( $lines[$i] );
        if( $config{'valid'} ) {
            #$config{'id'} = $i;
            push( @content_array, \%config );
            # my %hash_url;
            # $hash_url{$config{'id'}} = $config{'name'};
            # push(@key_values_url,\%hash_url);
            $key_values_url{$config{'id'}} = $config{'name'};
        }else{
            $total_num --;
        }
    }
    for ( my $i = 0; $i < @lines_custom; $i++ ) {
        my %config = &get_config_hash_url( $lines_custom[$i] );
        if( $config{'valid'} ) {
            #$config{'id'} = $i;
            push( @content_array, \%config );
            # my %hash_url;
            # $hash_url{$config{'id'}} = $config{'name'};
            # push(@key_values_url,\%hash_url);
            $key_values_url{$config{'id'}} = $config{'name'};
        }else{
            $total_num --;
        }
    }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'key_values_url'} = \%key_values_url;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    # %ret_data->{'page_size'} = $PAGE_SIZE;

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
#显示反病毒设置面板
sub display_havp_div(){
    my @lines_urls_white = ();
    &read_config_lines($conf_file_havp,\@lines_urls_white);
    my $str_urls_white = join("\n",@lines_urls_white);
    &readhash($file_settings_default,\%settings_default);
    my $is_checked_havp = "";
    if($settings_default{'HAVP'} eq 'on' && $status_havp eq 'on'){
        $is_checked_havp = "checked";
    }
    openbox('100%', 'left', _('反病毒设置'));
printf <<EOF
    <form name="HAVP_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="odd">
    <td class="add-div-type">启用病毒扫描</td>
    <td>
      <input type="checkbox" id="HAVP" name="HAVP" $is_checked_havp value="on"/>
      <span id="label_havp">启用</span>
      <span id="label_tip" style="color:red;"></span>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type" style="width:250px">不扫描以下URL</td>
    <td>
      <textarea style="width:250px;height:100px;" name="whitelist_url">$str_urls_white</textarea>
    </td>
    </tr>
    <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save_url"></input>
      <input type="submit" class="net_button" value="保存" align="middle"/>
      <!--<input type="reset" class="net_button" value="重置" align="middle"/>-->
    </td>
    </tr>
    </table>
    </form>
EOF
;
&closebox();
}
sub save_data_url(){
    &readhash($file_settings_default,\%settings_default);
    if($par{'HAVP'}){
        $settings_default{'HAVP'} = $par{'HAVP'};
    }else{
        $settings_default{'HAVP'} = "off";
    }
    &writehash($file_settings_default,\%settings_default);
    &update_all_havp();
    
    my $urls = $par{'whitelist_url'};
    #$urls =~ s/\r//g;
    `echo "$urls" > $conf_file_havp`;
    &show_page();
}
#判断启用杀毒
sub judge_havp(){
    system("$cmd");
    my %ret;
    %ret -> {'status'} = $?>>8;
    if($ret{'status'} == 0){
        $status_havp = "on";
    }else{
        $status_havp = "off";
    }
    my $result = $json->encode(\%ret);
    print $result;
}
#获取所有过滤模板的名称
sub get_all_template_names(){
    my @dirs = split(/\n/,`ls $conf_dir -F | grep '/'`);
    my @names = ();
    foreach(@dirs){
        $_ =~ s/\///g;
        my $settings_file = $conf_dir.'/'.$_."/settings";
        if(-f $settings_file){
            my %config_settings;
            &readhash($settings_file,\%config_settings);
            push( @names, $config_settings{'NAME'} );
        }
    }
    return @names;
}
#修改所有规则的启用病毒扫描字段
sub update_all_havp(){
    my @dirs = split(/\n/,`ls $conf_dir -F | grep '/'`);
    foreach(@dirs){
        $_ =~ s/\///g;
        my $settings_file = $conf_dir.'/'.$_."/settings";
        if(-f $settings_file){
            my %config_settings;
            &readhash($settings_file,\%config_settings);
            $config_settings{'HAVP'} = $status_havp;
            &writehash($settings_file,\%config_settings);
        }
    }
}