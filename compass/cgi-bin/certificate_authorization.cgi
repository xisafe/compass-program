#!/usr/bin/perl
#==============================================================================#
#
# 描述: ipmac绑定配置页面
#
# 作者: 辛志薇
# 公司: capsheaf
# 历史:
#   2015-1-5 创建
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $base_dir;
# my $sb_learn_dir;  # 两个目录三个文件
my $ca_config_file;        # CA证书配置文件路径
my $ca_create_cmd;         #生成CA证书的脚本
my $ca_manage_file;        #管理CA证书的配置文件路径

my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希

my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变

my $errormessage,$warnmessage,$notemessage;
#=========================全部变量定义end=======================================#

&main();

sub main() {

    &getcgihash(\%par);

    &get_query_hash(\%query);
    
    &init_data();
    
    &make_file();
    
    &do_action();

}
sub init_data(){

	$errormessage     = '';
    $notemessage     = '';
    $base_dir = '/var/efw/vpn/award';
    $ca_config_file = $base_dir.'/ca_config';
    $ca_manage_file = $base_dir.'/certs/config';
    $ca_create_cmd = "sudo /usr/local/bin/generate_ca_cert.py";
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <script language="JavaScript" src="/include/jquery-3.1.0.min.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/certificate_authorization.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#
}

sub make_file(){
	# system ("echo 'aaa'>/var/efw/chensisi.debug");
    if(! -e $base_dir){
        system("mkdir -p $base_dir");
    }
    if(! -e $ca_config_file){
        system("touch $ca_config_file");
    }
}

sub do_action() {
    my $action      = $par{'ACTION'};    # 千万注意par哈希里面装的是post提交过来的数据
    my $panel_name  = $par{'panel_name'};  # 同上

    my $location      = $par{'id'};

    my $query_action = $query{'ACTION'};  # 千万注意query哈希里面装的是get提交过来的数据
    # my $query_panel_name = $query{'panel_name'};  # 同上

    my $status;
    if( $action ne 'ca_download' && $query_action ne 'ca_download' && $query_action ne 'ca_download') {
        &showhttpheaders();
    }
    if ( $action eq 'save_data' ) {
        &save_data_branch();
    }    
    elsif ( $action eq 'check_ca' ) {
        
        &check_ca_file();
    }      
    elsif ( $action eq 'check_ca_one' ) {
        my $id_download = $par{'id'};
        &check_ca_file_one($id_download);
    }    
    elsif ( $action eq 'reset_ca' ) {
        &reset_ca_file();
    }
    elsif( $action eq 'import_data' ){
        &upload_file();
        &show_page();
    }    
    elsif ( $action eq 'load_data' ) {
        &load_data_branch();
    }    
    else {
        if ($action eq 'ca_download') {
            my $id_download = $par{'import_item'};
            $errormessage = &download($id_download );
            &showhttpheaders();
            &show_page();
        }
        else {
            &show_page();
        }
    }

}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &closebigbox();
    &display_main_body();
    &closepage();
}
sub display_main_body() {  #第一个首先写一个开启整个绑定功能的div
    &show_body();
}

sub show_body(){
    printf<<EOF
    <div id="message_box_config" style="width:96%; margin:20px auto;"></div>
    <div id="toggle_CA_panel_config" style="width:96%; margin:20px auto;"></div>
    <div id="create_CA_add_panel_config" style="width:96%; margin:20px auto;"></div>

    <div id="ipmac_add_panel_config"      style="width:96%; margin:20px auto;"></div>
    <div id="CA_import_panel_config" style="width:96%; margin:20px auto;"></div>
    <div id="CA_list_panel_config"      style="width:96%; margin:20px auto;"></div>
EOF
    ;
}
sub ip_mac_start(){
    my %read_hash = ();
    if(-e $snmp_settings_file_path){
        &readhash( $snmp_settings_file_path, \%read_hash );
    }
    my ( $status, $mesg ) = (-1, "开启失败");
    my %save_hash = %read_hash;
    if( $read_hash{'BIND'} eq 'disable'){  # 只有在后台状态为‘关闭’时才允许执行开启脚本！
        # 而你如果不判断的话很可能用户已经开启了一次后再点击若干次开启，这样就会导致多个开启脚本同时在执行！！这是很危险的！
        $save_hash{'BIND'} = 'enable';
        &writehash( $snmp_settings_file_path, \%save_hash );
        &restartipmac();  # 调用脚本重启
        if( $? == 0 ){
            $status = 0;  $mesg = "开启成功";
        }else {
            $mesg .= " 错误码:". $?>>8;  # 记住在$?的值为非0时必须要右移8位才是错误返回值，
            # 为0的时候可以不写右移8位，因为0右移了8位值还是0
        }
    }
    &send_status( $status, $mesg );
}

sub save_data_branch(){
	my $record = &get_config_record( \%par );

	my @lines = $record;
	&write_config_lines($ca_config_file,\@lines);

	`$ca_create_cmd`;
	my $status = 0;
	my $mesg = '操作成功';
	send_status( $status, $mesg);
}

sub load_data_branch(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $ca_manage_file, \@lines );
    
    my $record_num = @lines;
    for(my $i = 0; $i < $record_num; $i++){
            chomp(@lines[$i]);
            my %conf_data = &get_config_hash(@lines[$i]);
            if (! $conf_data{'valid'}) {
                next;
            }


            $conf_data{'id'} = $i;
            push(@content_array, \%conf_data);
            $total_num++;
    }
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
    my @temp = split(/;/, $line_content);
    $config{'CA_ID'}           = $temp[0];
    $config{'CA_Name'}         = $temp[1];
    $config{'CA_Type'}         = $temp[3];
    $config{'CA_Form'}         = $temp[2];
    $config{'CA_Item'}         = $temp[4];
	$config{'state_Date'}      = $temp[5];
	$config{'end_Date'}        = $temp[6];

    #============自定义字段组装-END===========================#
    return %config;
}

sub upload_file(){
	my $cgi = new CGI; 
    my $filename = $cgi->param('file_lib');
    # system("echo $tmp_fp >/var/efw/chensisi.debug");

    my $file_path = `mktemp -p /tmp`;

    # system("echo $file_path >/var/efw/chensisi.debug");
    open ( UPLOADFILE, ">$file_path" ) or $errormessage = "对不起，打开写入上传文件失败！";
    binmode UPLOADFILE;
    while ( <$filename> )
    {
        print UPLOADFILE $_;
    }
    close UPLOADFILE;
    # system("echo $file_path>/var/efw/chensisi.debug");
    my $temp_cmd = "sudo /usr/local/bin/generate_host_cert.py -r $file_path";
    # system("echo $temp_cmd>>/var/efw/chensisi.debug");
    # print $temp_cmd;
    my $status = `$temp_cmd`;
    if ($status eq '0') {
    	$notemessage = "导入成功";
    }
    else {
    	$errormessage = "导入失败";
    }
    return ($errormessage,$notemessage);
}

sub check_ca_file() {
    my %ret_data;
    my $ca_file = `sudo /usr/bin/gmssl x509 -text -in /var/efw/vpn/award/cacerts/*.pem |head -n 9`;
    # print $ca_file;
    # return;
    # my $temp_hash = $json->decode($ca_file);
 #    print $ca_file;
 #    print $temp_hash;
    $ret_data{'detail_data'} = $ca_file;

    my $result = $json->encode(\%ret_data);

    print $result;
}
sub check_ca_file_one($) {

    my $id_download = shift;
    my $temp="sudo /usr/local/bin/get_host_cert_info.py -i $id_download";
    my $file = `$temp`;
	my %ret_data;
	my $ca_file = `sudo /usr/bin/gmssl x509 -text -in /var/efw/vpn/award/cacerts/*.pem |head -n 9`;

	$ret_data{'detail_data'} = $file;

	my $result = $json->encode(\%ret_data);

	print $result;
}

sub reset_ca_file() {

	`rm -rf /var/efw/vpn/award/cacerts/*.pem`;
	my $status = 0;
	my $mesg = '删除成功';
	send_status($status,$mesg);
	
}

sub get_detail_data($$) {
    my $type = shift;
    my $content_array_ref = shift;

    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;
    my $search = $par{'search'};
    
    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        # 读交换机配置文件
        if( $type eq "switchboard" ){
            ( $status, $mesg, $total_num ) = &read_config_lines( $sb_config_file_path, \@lines);
            for( my $i = 0; $i < @lines; $i++ ) {
                my $id = $from_num + $i;
                if( !$LOAD_ONE_PAGE ) {
                    $id = $i;
                }
                my %hash = ();
                %hash = &get_sb_config_hash( $lines[$i] );
                $hash{'id'} = $id;
                push( @$content_array_ref, \%hash );
            }
        }
        # 读ipmac_table配置文件
        elsif( $type eq "ipmac" ){
            ( $status, $mesg, $total_num ) = &read_config_lines( $ipmac_table_file_path, \@lines);
            for( my $i = 0; $i < @lines; $i++ ) {
                my $id = $from_num + $i;
                if( !$LOAD_ONE_PAGE ) {
                    $id = $i;
                }
                my %hash = ();
                %hash = &get_ipmac_config_hash( $lines[$i] );
                $hash{'id'} = "ipmac_table_file".":".$id;

                if ( $search ne "" ) {
                    if ( !( $hash{'IP_ADDR'} =~ m/$search/ ) ) {
                            $total_num--;
                            next;
                    }else{
                        push( @$content_array_ref, \%hash );
                    }
                }else {
                    push( @$content_array_ref, \%hash );
                }

                # push( @$content_array_ref, \%hash );
            }
            # 读取存放交换机ip-mac条目的配置文件里的所有行
            @lines = ();
            &read_config_lines( $ipmac_bind_file_path, \@lines);
            $total_num += @lines;
            for( my $i = 0; $i < @lines; $i++ ) {
                my $id = $from_num + $i;
                if( !$LOAD_ONE_PAGE ) {
                    $id = $i;
                }
                my %hash = ();
                %hash = &get_ipmac_config_hash( $lines[$i] );
                $hash{'id'} = "ipmac_bind_file".":".$id;

                if ( $search ne "" ) {
                    if ( !( $hash{'IP_ADDR'} =~ m/$search/ ) ) {
                            $total_num--;
                            next;
                    }else{
                        push( @$content_array_ref, \%hash );
                    }
                }else {
                    push( @$content_array_ref, \%hash );
                }
                # push( @$content_array_ref, \%hash );
            }
        }
    } else {
        # 只加载一页的时候哦
    }
    return ( $status, $mesg, $total_num );
}

sub send_status($$) {
    my ( $status, $mesg ) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}

sub  get_config_record($) {
	my $hash_ref = shift;
    my @record_items = ();

    my $name = "CN=$hash_ref->{'name'}";
    my $country = "C=$hash_ref->{'country'}";
    my $province = "ST=$hash_ref->{'province'}";
    my $city = "L=$hash_ref->{'city'}";
    my $organization = "O=$hash_ref->{'organization'}";
    my $department = "OU=$hash_ref->{'department'}";
    my $email = "EA=$hash_ref->{'email'}";

    push( @record_items, $name);
    push( @record_items, $country);
    push( @record_items, $province);
    push( @record_items, $city);
    push( @record_items, $organization);
    push( @record_items, $department);
    push( @record_items, $email);

    return join ("\n", @record_items);
}

sub download(){
    my $id_download = shift;
    my $temp="sudo /usr/local/bin/download_host_cert.py -i $id_download";
    # print $temp;
    # system("echo $id_download>>/var/efw/chensisi.debug");
    # system("echo $temp>>/var/efw/chensisi.debug");
    my $file = `$temp`;
    my $data = $file;
    $data =~ /\/var\/efw\/vpn\/award\/certs\/(.*)\/(.*)/;
    my $down_name = $2;
    my @fileholder = ();
    my $errormessage = '文件不存在';
    if( -e "$file"){            
        if($file =~ /\.gz/){
            my $str = `zcat '$file'`;
            @fileholder = split("\n", $str);
            foreach(@fileholder) {
                $_ .= "\n";
            }
        }else{
            open(DLFILE, "<$file") || Error('open', "$file");
            @fileholder = <DLFILE>;
            close (DLFILE) || Error ('close', "$file");

        }
        print "Content-Type:application/x-download\n";  
        print "Content-Disposition:attachment;filename='$down_name'\n\n";
        print @fileholder;
        exit;
        
    }
    else{
        return $errormessage;
    }
}