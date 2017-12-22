#!/usr/bin/perl
#author: pj
#createDate: 2016/12/19
#description: 弱口令管理
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=====初始化全局变量到init_data()中去初始化=====================================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $user_confile;       #规则所存放的文件
my $adminconf_file;
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $page_title;         #页面标题
my $extraheader;        #存放用户自定义JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my %settings;           #存放该页面配置的哈希
my %list_panel_config;  #存放列表面板的配置信息，每个页面需要自己配置
my $PAGE_SIZE = 15;             #常量
my $PANEL_NAME = "list_panel";  #常量
$cmd_getlogriskvalue;
$cmd_getassettree;
$cmd_getposition;
$cmd_getattacksid;
my $LOAD_ONE_PAGE = 0;
my $json = new JSON::XS;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    &init_data();
    &do_action();
}

sub init_data(){
    $custom_dir          = '/riskControl/console';               #要保存数据的目录名字,要配置,不然路径初始化会出问题
    $conf_dir            = "/var/efw".$custom_dir;               #规则所存放的文件夹
    $user_confile        = $conf_dir.'/userlistconf';            #发件人信息所存放的文件
    $adminconf_file      = $conf_dir."/adminconf";
    $need_reload_tag     = '';                                   #启用信息所存放的文件
    $cmd_getComparisionValue = "sudo /usr/local/bin/riskControl/Comparision.py";
    $cmd_getassettree    = "/usr/local/bin/riskControl/getassettree.py";
    #============页面要能翻页必须引用的CSS和JS-BEGIN============================================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的extend脚本=============================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/dist/themes/default/style.css" />
                    <link rel="stylesheet" href="/include/bootstrap/css/bootstrap.css">
                    <script language="JavaScript" src="/include/jquery-1.12.1.min.js"></script>          
                    <script language="javascript" src="/include/bootstrap/js/bootstrap.min.js"></script>
                    <!--<script language="JavaScript" src="/include/dist/jstree.min.js"></script>-->
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/info_panel.js"></script>
                    <script language="JavaScript" src="/include/info_panel_extend.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/weak_pwd_management.js"></script>';
    #============页面要能翻页必须引用的CSS和JS-END==============================================#

    #====获取通过post或者get方法传过来的值-BEGIN=======#
    &getcgihash(\%par);
    #====获取通过post或者get方法传过来的值-END=========#
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $pan = $par{'panel_name'};

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ($action eq 'load_zoneData') {
        #==获取配置数据==#
        &load_zoneData();
    }elsif($action eq 'startScan'){
        &startScan();
    }
    elsif($action eq 'showScanInfo'){
        &showScanInfo();
    }
    elsif($action eq 'viewReport'){
        &viewReport();
    } 
    elsif($action eq 'deleteTaskList'){
        &deleteTaskList();
    }
    elsif($action eq 'init_list_panel'){
       &init_list_panel(); 
    }
    elsif ( $action eq 'saveTask') {
       &saveTask();
    }
	elsif ( $action eq 'load_data' && $pan eq 'strategy_panel') {
		&loadStrategy()
	}
	elsif ( $action eq 'on_strategy') {
		&onStrategy()
	}
	elsif ( $action eq 'off_strategy') {
		&offStrategy();
	}
	elsif ( $action eq 'delete_strategy') {
		&deleteStrategy();
	}
	elsif( $action eq 'apply_strategy') {
		&applyStrategy();
	}
    else {
        #==如果用户什么都没提交，默认返回页面==#
        &show_page();
    }
}

sub show_page() {
    &openpage($page_title, 1, $extraheader);
    &display_main_body();
    &closepage();
}

sub display_main_body() {
    printf<<EOF
    <div id="mesg_panel"></div>
    
        <div id="add_panel" class="weakPwd-addPanel"></div>
        <!--<div id="tree_panel"></div>-->
        <div id="servicePanel" class="weakPwd-servicePanel"></div>
        <div id="edit_service_panel"></div>
        <div id="highSetting" class="weakPwd-highSetting"></div>
        <div id="scanResult"></div>
        
        <div style="width:100px;heght:100px">
            <div id="showReport"></div>
            <div id="protocolPanel"></div>
        </div>
        <div id="display_panel"></div>
        
    
            
    <div id="list_panel" class="weak_pwd-listPanel"></div>
    <div id="strategy_panel"></div>    
EOF
    ;
}

 sub load_zoneData {
   my $cmd = "/usr/local/bin/riskControl/getWeakScanConfigInfo.py";
   my $json = `sudo $cmd`;
   print $json;
 }
 sub init_list_panel {
      my $cmd = "/usr/local/bin/riskControl/setWeakScanConfigInfo.py -S";
      my $json = `sudo $cmd`;
    print $json;
 }
 sub showScanInfo{
    my $taskName = '"'.$par{'taskName'}.'"';
    my $cmd = "/usr/local/bin/riskControl/viewTaskInfo.py -t $taskName";
    my $json = `sudo $cmd`;
    print $json;
 }
 sub viewReport(){
    my $taskName = '"'.$par{'taskName'}.'"';
    my $cmd = "/usr/local/bin/riskControl/getWeakScanReport.py -t $taskName";
    my $json = `sudo $cmd`;
    print $json;
 }
 sub startScan {
    my $taskName = '"'.$par{'taskName'}.'"';
    my $operate  = ($par{'operate'} eq 'yes') ? ' -p' : ' -s' ;
    my $cmd = "/usr/local/bin/riskControl/weakWordScanCtl.py -t $taskName $operate";
    my $json = `sudo $cmd`;
    print $json;
 }
 sub deleteTaskList(){
    my $taskName = '"'.$par{'taskName'}.'"';
    my $cmd = "/usr/local/bin/riskControl/deleteWeakScanTask.py -t $taskName";
    my $json = `sudo $cmd`;
    print $json;
 }
 sub saveTask {
    my $title ='-t "'.$par{'title'}.'"';
    my $assetId = '-i "'. $par{'assetId'}.'"';
    my $service = '-s "'. $par{'service'}.'"';
    my $method = '-m "'.$par{'method'}.'"';
    my $userNameList = ($par{'userNameList'} eq "") ? '' : '-u "'.$par{'userNameList'}.'"';

    my $pwdList = ($par{'pwdList'} eq "") ? '' : '-p "'. $par{'pwdList'}.'"';
    my $urlList = ($par{'urlList'} eq "") ? '' : '-g "'.$par{'urlList'}.'"';
    my $emailList_stmp = ($par{'emailList_stmp'} eq "") ? '' : '-c "'.$par{'emailList_stmp'}.'"';
    my $emailList_pop3 = ($par{'emailList_pop3'} eq "") ? '' : '-o "'.$par{'emailList_pop3'}.'"';
    my $emailList_imap = ($par{'emailList_imap'} eq "") ? '' : '-a "'.$par{'emailList_imap'}.'"';
    # if($title =~ /[a-z][0-9]+/ && $assetId =~ /[a-z0-9-&]+/ && $service =~ /[a-z0-9/]+/ && $method =~ /[0-3]/)

    my $cmd = "/usr/local/bin/riskControl/setWeakScanConfigInfo.py $title $assetId $service $method $userNameList $pwdList $urlList $emailList_stmp $emailList_pop3 $emailList_imap";

    my $json = `sudo $cmd`;
    print $json;
    
 }
 #下载策略列表数据 
 sub loadStrategy() {
 	my $jsonData = `/usr/local/bin/riskControl/viewProtecStrategy.py -v`;
 	my %data;
 	my @data;
 	if($jsonData) {
 		$jsonData = $json->decode($jsonData);
 		$jsonData = $jsonData->{'detail'};
 	}else {
 		return;
 	}

 	@data = @$jsonData;
 	for(my $i = 0; $i < @data; $i++ ) {
 		$data[$i]->{'id'} = $i;
 	}
 	$data{'detail_data'} = \@data;
 	$data{'error_mesg'} = "读取数据成功";
 	$data{'reload'} = 0;
 	$data{'status'} = 0;
 	$data{'total_num'} = @data;
 	print $json->encode(\%data);
 }
 #启用策略 
 sub onStrategy() {
 	my $ids = $par{'ids'};
 	system("/usr/local/bin/riskControl/viewProtecStrategy.py -e '$ids'");
 	print '{"mesg": "启用成功"}';
 }
 #禁用策略 
 sub offStrategy() {
 	my $ids = $par{'ids'};
 	system("/usr/local/bin/riskControl/viewProtecStrategy.py -f '$ids'");
 	print '{"mesg": "禁用成功"}';
 }
 #删除策略 
 sub deleteStrategy() {
 	my $ids = $par{'ids'};
 	system("/usr/local/bin/riskControl/viewProtecStrategy.py -r '$ids' > /tmp/yp.test 2>&1");
 	print '{"mesg": "删除成功"}';
 }
 #应用策略
 sub applyStrategy() {
 	my $name = $par{'name'};
 	#system("/usr/local/bin/riskControl/protectRisk.py -t '$name'");
 	my $cmd = "/usr/local/bin/riskControl/protectRisk.py -t '$name'";
	my $stat = `$cmd `;
     #$stat =~ s/\n//g;
	if ($stat =~ 'ok') {
 	print '{"mesg": "应用策略成功"}';
	}
 	else{
	print '{"mesg": "应用策略失败"}';	
	}
	

 }
