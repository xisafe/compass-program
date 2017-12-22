#!/usr/bin/perl
#author: LiuJulong
#createDate: 2014/12/03
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#

my $page_title;            #页面标题
my $extraheader;           #存放用户自定义JS
my %par;                   #存放post方法传过来的数据的哈希
my %query;                 #存放通过get方法传过来的数据的哈希
my %settings;              #存放该页面配置的哈希
my %list_panel_config;     #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
my $read_conf_dir; 
my $url_classify_file; 
my $apply_classify_file;
my $conf_dir;
my $disable_file;
my $CUR_PAGE = "统计配置" ;      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

#=========================全部变量定义end=======================================#
# &save_data();
&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $conf_dir              = "/var/efw/flowmeter/";
    $read_conf_dir         ="/var/efw/flowmeter/all_ip.txt";                    #读取数据的目录文件夹     
    $disable_file          = $conf_dir."disable";  
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/jquery-ui.min.css" />
                    <script language="JavaScript" src="/include/jquery-1.12.1.min.js"></script>
                    <script language="JavaScript" src="/include/jquery-ui.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/statistics_conf.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    &getqueryhash(\%query);
    #====获取通过post或者get方法传过来的值-END=========#

    # &make_file();#检查要存放规则的文件夹和文件是否存在
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $panel_name = $par{'panel_name'};
    if( !$action ) {
        $action = $query{'ACTION'};
    }

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'read_data' ) {
        #==下载数据==#
        &read_data();
    }
    elsif($action eq 'save_data'){
        &save_data();
        &write_log($CUR_PAGE,"edit",0,$rule_or_config);
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
    <div id="panel_flow_list" style="width: 96%;margin: 20px auto;"></div>
    <div id="mesg_box_tmp" style="width: 96%;margin: 20px auto;"></div>
EOF
    ;
}

sub read_data(){
    my %ret_data; 
    my @data_content;

    my ( $status, $error_mesg)= &read_config_lines($read_conf_dir,\@data_content);
    # my $device = `sudo ethconfig -j`;
    # my $device_arr = $json->decode($device);
    # my @device_name;
    
    # foreach my $item(@$device_arr){
    #     my %temp;
    #     %temp->{'iface'} = $item->{'iface'};
    #     %temp->{'mac'} = $item->{'mac'};
    #     push(@device_name,\%temp);
    # }
    # my $state = `sudo /usr/local/bin/flowmeter_dae.py  -o status`;
    
    %ret_data->{'data_content'}= \@data_content;
    if(!-e $disable_file){
        %ret_data->{'enable'}= 1;
    }else{
        %ret_data->{'enable'}= 0;

    }
    # %ret_data->{'label'}= $state;

    # %ret_data->{'device'} = \@device_name;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $error_mesg;
    my $ret = $json->encode(\%ret_data);
    print $ret; 

}
sub save_data(){
    my %ret_data; 
    my $record = $par{'data'};
    my $enable = $par{'enable'};
    # my $device = $par{'device'};

    my ( $status, $mesg ) = (-1,"未写入数据");
    my @arr = split('&',$record);
    my $pass = 0;
    for(my $i = 0; $i < @arr; $i++){
        my $check = (&validip($arr[$i]) || &validip_addr_segment($arr[$i]));
        if( $check > 0 ){
            $pass =1;
        }
        else{ 
			$pass = 0;
			last;
		}
    }
   
     #ip is ok
    if ($pass == 1){
        if($enable == 1){
            unlink $disable_file; 
        }else{
            if(! -e $disable_file){
                system("touch $disable_file");
            }
        }

        open( FILE, "+>$read_conf_dir" ) or return &send_status( $status,0, "写入数据时，打开文件失败" );
        foreach my $record ( @arr ) {
            if ($record ne "") {#去掉空行
				$mesg = "$mesg,writing line: $record";
                print FILE "$record\n";
            }
        }
        close FILE;
        ($status , $mesg) = (1, '保存成功');
        `sudo /usr/local/bin/restartflowmeter.py`;
    }
   
    &send_status($status,0,$mesg);
    
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
}
