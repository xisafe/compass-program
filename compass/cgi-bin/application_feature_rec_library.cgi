#!/usr/bin/perl
#==============================================================================#
#
# 描述: 添加规则列表规则页面
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.09.23 WangLin创建
#
#==============================================================================#
use Encode;
use Data::Dumper;
require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=================初始化全局变量到init_data()中去初始化========================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my $IDCON = "-";

my $CUR_PAGE = "应用特征识别库" ;      #当前页面名称，用于记录日志
my $log_oper;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '0';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post请求传过来的变量
    &getcgihash(\%par);
    #获取get请求传过来的变量
    &get_query_hash(\%query);
    #初始化变量值
    &init_data();
    &make_file();
    #做出响应
    &do_action();
}


sub init_data(){
    $custom_dir         = '/add_list';
    $conf_dir           = "${swroot}".$custom_dir;
    $conf_file          = $conf_dir.'/config';
    $need_reload_tag    = $conf_dir.'/add_list_need_reload';
	
	$classfication_file = '/var/efw/objects/application/app_group';#应用组数据存放文件路径
	$application_file   = '/var/efw/objects/application/app_system';#应用数据存放文件路径
	$rule_file          = '/var/efw/objects/application/app_rule';#应用规则数据存放文件路径
	$rulePort_file      = '/var/efw/objects/application/app_rule_port';#应用规则数据存放文件路径

    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/application_feature_rec_library.css" />
                    <script language="javascript" type="text/javascript" src="/include/jquery.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="javascript" type="text/javascript" src="/include/left-menu.js"></script>
                    <script language="JavaScript" src="/include/application_feature_rec_library.js"></script>';
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-END==============================#
}

sub do_action() {
    #==一般ACTION只会通过一种方式传过来，开发者需要自己判断从哪种方式传过来==#
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $panel_name = $par{'panel_name'};

    if($action ne 'export_data' && $query_action ne 'export_data' && $query_action ne 'export_selected') {
        &showhttpheaders();
    }

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ( $action eq 'save_data' && $panel_name eq 'add_panel'  ) {
        &save_data();
    }
    elsif ( $action eq 'load_data' && $panel_name eq 'list_panel' ) {
        &load_data();
    }
	elsif ( $action eq 'load_classfication' ) {
		&load_classfication();
	}
	elsif( $action eq 'load_application' ) {
		&load_application();
	}
	elsif( $action eq 'load_rule' ) {
		&load_rule();
	} 
    elsif ( $action eq 'apply_data' && $panel_name eq 'mesg_box' ) {
        &apply_data();
    }
    elsif ($action eq 'delete_data') {
        &delete_data();
    }
    elsif ($action eq 'enable_data') {
        &toggle_enable( "1" );
    }
    elsif ($action eq 'disable_data') {
        &toggle_enable( "0" );
    }
	elsif ($action eq 'edit_rule') {
		&edit_rule();
	} 
    else {
        &show_page();
    }
}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &display_main_body();
    &closepage();
}

sub display_main_body() {
    printf<<EOF
	<div id="mesg_box" class="container"></div>
    <div id="content_panel" class="container content_panel">
        <div id="cont_title">应用总数：<b></b>;  规则总数：<b></b></div>
		<div id="for_content">
			<div id="left">
				<div id="cont_menu" class="cont_menu">
					<div id="cont_menu_title">应用分类</div>
					<ul id="cont_menu_ul"></ul>
				</div>
			</div>
			<div id="right">
				<input type="text" value="隐藏域" class="hidden_class">
				<div id="cur_app">具体应用</div>
				<div id="table_list" class="table_list"></div>
			</div>
		</div>
        
        
    </div>
	<div id="edit_panel" class="container"></div>
EOF
    ;    

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
    $config{'appid'}          = $temp[0];
    $config{'rName'}          = $temp[1];
    $config{'name'}           = $temp[2];
    $config{'description'}    = $temp[3];
	$config{'appgroupid'}     = $temp[4];
	$config{'enable'}         = $temp[5];

    #============自定义字段组装-END===========================#
    return %config;
}

#apprule组装 
sub get_rule_config_hash($) {
	my $line_content = shift;
    chomp($line_content);
    my %config;
    $config{'valid'} = 1;#默认是合法的行，如果有不合法的，将该字段置为0
    if ($line_content eq '') {
        $config{'valid'} = 0;
        return %config;
    }
    #============自定义apprule组装-BEGIN=========================#
    my @data_line = split(/,/, $line_content);
	$config{'appruleid'}    = $data_line[0];
	$config{'name'}         = $data_line[1];
	$config{'description'}  = $data_line[2];	
	$config{'appid'}        = $data_line[3];
	$config{'appruleEnable'}= $data_line[4];  
    #============自定义apprule组装-END===========================#
    return %config;
}
sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, $hash_ref->{'appid'} );
    push( @record_items, $hash_ref->{'rName'});
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'description'} );
	push( @record_items, $hash_ref->{'appgroupid'} );
	push( @record_items, $hash_ref->{'enable'} );
    return join ",", @record_items;
}

sub get_compare_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    #============自定义比较字段-BEGIN=========================#
    #一般来说比较的字段和保存的字段几乎都一致，但是存在保存时，
    #要更新修改时间等就不一样了，需要自己定义比较哪些字段=====#
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'note'} );
    push( @record_items, $hash_ref->{'enable'} );
    #============自定义比较字段-END===========================#
    return join ",", @record_items;
}

sub save_data_handler() {
    my ( $status, $mesg ) = ( -1, "未开始检测各项的合法性" );

    #===第一步，检查名称是否重名===#
    my $name_exist_line_num = "";
    ( $status, $mesg, $name_exist_line_num ) = &where_is_field( $conf_file, ",", 0, $par{'name'} );
    if ( $name_exist_line_num ne "" ) {
        #===如果检测到已存在，则允许是编辑的情况，并且只能是原来的行===#
        if ( $par{'id'} ne "" && $par{'id'} eq $name_exist_line_num ) {
            #===允许通过===#
        } else {
            $status = -1;
            $mesg = "名称已存在";
            return ( $status, $mesg );
        }
    }

    #===第二步，处理说明信息===#
    $par{'note'} = &prepare_note( $par{'note'} );

    #===第三步，处理启用禁用===#
    if ( $par{'enable'} ne "on" ) {
        $par{'enable'} = "off";
    }

    #===如果当前是编辑状态，检测传上来的字段与现有字段是否一致，一致就不在进行更改===#
    if ( $par{'id'} ne "" ) {
        my $exist_record = &get_one_record( $conf_file, $par{'id'} );
        my %exist_record_hash = &get_config_hash( $exist_record );
        my $compare_record_old = &get_compare_record( \%exist_record_hash );
        my $compare_record_new = &get_compare_record( \%par );
        if ( $compare_record_old eq $compare_record_new ) {
            $status = -1;
            $mesg = "配置未改变";
        } else {
            $status = 0;
            $mesg = "检测合格";
        }
    } else {
        $status = 0;
        $mesg = "检测合格";
    }

    return ( $status, $mesg );
}

sub save_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未保存" );
    #===检测字段合法性===#
    ( $status, $mesg ) = save_data_handler();
    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $record = &get_config_record( \%par );
    my $item_id = $par{'id'};

    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $conf_file, $record );
        $log_oper = "add";
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
        $log_oper = "edit";
    }

    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    } else {
        $mesg = "保存失败";
    }

    &send_status( $status, $reload, $mesg );
}

sub load_data(){
    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 1;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub get_detail_data($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;
    my $search = &prepare_search( $par{'search'} );

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records( $conf_file, $page_size, $current_page, \@lines );
    }

    $total_num = 0; #重新初始化总数
    for( my $i = 0; $i < @lines; $i++ ) {
        my $id = $from_num + $i;
        if( !$LOAD_ONE_PAGE ) {
            $id = $i;
        }
        my %hash = &get_config_hash( $lines[$i] );

        if ( !$hash{'valid'} ) {
            next;
        }

        #===实现查询===#
        if ( $search ne "" ) {
            my $name = lc $hash{'name'};
            my $note = lc $hash{'note'};
            if ( !($name =~ m/$search/) && !($note =~ m/$search/) ) {
                #===对名字，说明进行搜索===#
                next;
            }
        }

        $hash{'id'} = $id; #自定义id，id可以是任何字符，只要能唯一区别每一条数据
        push( @$content_array_ref, \%hash );
        $total_num++;
    }

    return ( $status, $mesg, $total_num );
}

sub delete_data() {
    my $reload = 0;
    my ( $status, $mesg ) = &delete_several_records( $conf_file, $par{'id'} );

    if( $status == 0 ) {
        $reload = 1;
        $mesg = "删除成功";
        &create_need_reload_tag();
    }
    $log_oper = "del";
    &send_status( $status, $reload, $mesg );
}

sub toggle_enable($) {
    my $enable = shift;
    my $operation = "启用";
    $log_oper = 'enable';
    if ( $enable ne "1" ) {
        $operation = "禁用";
        $log_oper = 'disable';
    }
    my @lines = ();
    my @rule_lines;
    my $reload = 0;
    my %app_idHash;
    my ( $status, $mesg ) = &read_config_lines( $application_file, \@lines );
    ($status,$mesg) = &read_config_lines($rule_file,\@rule_lines);
    if( $status != 0 ) {
        $mesg = "$operation失败";
        &send_status( $status, $reload, $mesg );
        return;
    }

    my %item_id_hash;
    my @item_ids = split( "&", $par{'id'} );
    foreach my $id ( @item_ids ) {
        $item_id_hash{$id} = $id;
    }

    my $len = scalar( @lines );

    for ( my $i = 0; $i < $len; $i++ ) {
        
		if( $item_id_hash{$i} eq "$i" ) {
            my %config = &get_config_hash( $lines[$i] );
            $config{'enable'} = $enable;
            %app_idHash->{$config{'appid'}} = $enable;
            $lines[$i] = &get_config_record(\%config);
        }
    }

    for(my $j = 0; $j < @rule_lines; $j++){
      my @temp = split(",",$rule_lines[$j]);
      my %ruleLineHash = &getRuleHash( \@temp);
      my $id_ = %ruleLineHash->{'appruleid'};
        
      if(exists %app_idHash->{$id_}){
        @temp[4] = %app_idHash->{$id_};
       
        $rule_lines[$j] = join(",",@temp);
       
        # print Dumper(\@temp);
        # return;
      }
    }

 
    my ( $status, $mesg ) = &write_config_lines( $application_file, \@lines );
       ( $status, $mesg ) = &write_config_lines( $rule_file, \@rule_lines ); 
  
    if( $status != 0 ) {
        $mesg = "$operation失败";
    } else {
        $mesg = "$operation成功";
        $reload = 1;
        &create_need_reload_tag();
    }

    &send_status( $status, $reload, $mesg );
    return;
}

sub apply_data() {
    &clear_need_reload_tag();
    $log_oper = "apply";
    &send_status( 0, 0, "应用成功" );
}

sub send_status($$$) {
    #==========状态解释=========================#
    # => $status: 0 表示成功，其他表示不成功
    # => $reload: 1 表示重新应用，其他表示不应用
    # => $mesg: 相关错误的消息
    #===========================================#
    my ($status, $reload, $mesg) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'reload'} = $reload;
    %hash->{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_config);
}

sub prepare_search($) {
    my $search = shift;

    $search =~ s/\^/\\\^/g;
    $search =~ s/\$/\\\$/g;
    $search =~ s/\./\\\./g;
    $search =~ s/\|/\\\|/g;
    $search =~ s/\(/\\\(/g;
    $search =~ s/\)/\\\)/g;
    $search =~ s/\[/\\\[/g;
    $search =~ s/\]/\\\]/g;
    $search = lc $search;

    return $search;
}

sub prepare_note($) {
    my $note = shift;
    $note =~ s/\n/ /g;
    $note =~ s/,/，/g;
    return $note;
}

sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}

#读取应用分类列表的数据
sub load_classfication() {
    my %ret_data;
    my @content_array;
    my @lines = ();
	my @lines_app = ();
	my (@nu1 , @nu2);
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $classfication_file, \@lines );
	my ($status2,$error_mesg) = &read_config_lines( $application_file, \@lines_app );
    my $record_num = @lines;
	my $total_number = @lines_app;
	my $total_number_rule = &getRuleNumber();
    $total_num = $record_num;
    
    for ( my $i = 0; $i < $record_num; $i++ ) {
        my %config;
        my @data_line = split(",",$lines[$i]);
		my $number = 0;
		%config->{'appgroupId'} = $data_line[0];
        %config->{'name'} = $data_line[1];
		foreach(@lines_app) {
			my @line = split(",",$_);
			if ( $line[4] == $data_line[0]) {
				$number ++;
			}
		}
		%config->{'number'} = $number;
        push( @content_array, \%config );
    }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
	%ret_data->{'total_number'} = $total_number;
	%ret_data->{'total_number_rule'} = $total_number_rule;
    %ret_data->{'error_mesg'} = $error_mesg;
    

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
#获取规则总数
sub getRuleNumber() {
    my (@nu1, @nu2);
	&read_config_lines( $rule_file, \@nu1);
	&read_config_lines( $rulePort_file, \@nu2);
    my %nu1 = getRuleHashGrep('', \@nu1);
    my %nu2 = getRuleHashGrep('', \@nu2);
    my @num = (keys %nu1, keys %nu2);
    return @num;
}
#读取应用数据
sub load_application() {
	my %ret_data;
    my @content_array;
    my @lines = ();
	my $groupid = $par{'appgroupid'};
	my $search = "";
	$search = &prepare_search( $par{'search'} );
	my $selectVal = 1;
	if( $par{'selectVal'} eq 'on' ) {
		$selectVal = 1;
	}elsif( $par{'selectVal'} eq 'off' ) {
		$selectVal = 0;
	}else{
		$selectVal = 2;
	}
    my ( $status, $error_mesg, $total_num );
	( $status, $error_mesg ) = &read_config_lines( $application_file, \@lines );
	my $record_num = @lines;
    $total_num = 0;
	for ( my $i = 0; $i < $record_num; $i++ ) {
		my %config;
		my @data_line = split(",",$lines[$i]);
        #===实现查询===#
        if ( $search ne "" ) {
            my $name = lc $data_line[2];
            if ( !($name =~ m/$search/) ) {
                #===对名字，说明进行搜索===#
                next;
            }
        }
		if( $data_line[4] != $groupid ) {
			next;
		}
		if( $selectVal != 2 ){
			if ( $data_line[5] != $selectVal ) {
				next;
			}
		}
		%config->{'id'} = $total_num;
		%config->{'appid'} = $data_line[0];
		%config->{'name'} = $data_line[2];
		%config->{'description'} = $data_line[3];
		%config->{'rowNumber'} = $i;
				
		$total_num ++;
		push( @content_array, \%config );
	}
    &get_appStatus(\@content_array);
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
	%ret_data->{'reload'} = 0; 
    %ret_data->{'error_mesg'} = $error_mesg;
	%ret_data->{'search'} = $search;
	my $ret = $json->encode(\%ret_data);
    print $ret; 
}

#读取规则数据
sub load_rule() {
	my %ret_data;
    my @content_array;
	my %lines;
	my %linesPort;
    my @lines = ();
	my @linesPort = ();
	my $appid = $par{'appid'};
    my $count = 0;
    my ( $status, $error_mesg, $total_num );
	( $status, $error_mesg ) = &read_config_lines( $rule_file, \@lines );
	my ($status2, $error_mesg2 ) = &read_config_lines( $rulePort_file,\@linesPort );
	#system("echo '###################' >> /tmp/applicationTest");
    #===处理rule_file中的数据===#
	for ( my $i = 0; $i < @lines; $i++ ) {
		my @data_line = split(",",$lines[$i]);
		my %line = &getRuleHash(\@data_line);		
		if($appid eq $line{'appid'}) {
			my $name = $line{'name'};
            #system("echo '$name' >> /tmp/applicationTest");
			if($lines{$name}) {
				$lines{$name}->{'appruleid'} .= $IDCON . $line{'appruleid'};
			}else {
                #===标注规则类型===#
				$line{'type'} = 0;
                
                #===标注ID===#
                $line{'id'} = $count;
                $count++;

				$lines{$name} = \%line;
			}
		}
	}
	
	#===处理rulePort_file中的数据===#
	for ( my $i = 0; $i < @linesPort; $i++ ) {		
		my @data_line = split(",",$linesPort[$i]);
		my %line = &getRuleHash(\@data_line);		
		if($appid eq $line{'appid'}) {
			my $name = $line{'name'};
            #system("echo '$name' >> /tmp/applicationTest");
			if($linesPort{$name}) {
				$linesPort{$name}->{'appruleid'} .= $IDCON . $line{'appruleid'};
			}else {			
                #===标注规则类型===#
				$line{'type'} = 1;

                #===标注ID===#
                $line{'id'} = $count;
                $count++;
				
                $linesPort{$name} = \%line;
			}
		}
	}
	push(@content_array, values %lines);
	push(@content_array, values %linesPort);
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = @content_array;
    %ret_data->{'status'} = $status;
	%ret_data->{'reload'} = 0; 
    %ret_data->{'error_mesg'} = $error_mesg2;
	my $ret = $json->encode(\%ret_data);
    print $ret;
}
sub getRuleHash() {
	my $arr = shift;
	my %lineHash;
	$lineHash{'appruleid'}   = $arr->[0];
	$lineHash{'name'}        = $arr->[1];
	$lineHash{'description'} = $arr->[2];
	$lineHash{'appid'}       = $arr->[3];
	$lineHash{'enable'}      = $arr->[4];
	return %lineHash;
}
#编辑规则enable字段
sub edit_rule() {
	
	my %ret_data;
	my @lines;
	my @linesPort;
	my $str = $par{'jsonData'};
	$str =~ s/\&quot;/\"/g;
	my $data = $json->decode($str);
	my $detail_data = $data->{'detaildata'};
	my @detail_data = @$detail_data;
	my %ruleId;
	my %rulePortId;
	my ( $status, $error_mesg );
	( $status, $mesg ) = &read_config_lines( $rule_file, \@lines );
	( $status, $mesg ) = &read_config_lines( $rulePort_file, \@linesPort );
    #system("echo '############################' >> /tmp/applicationTest");
	foreach(@detail_data) {
		my $enable = $_->{'enable'};
		my @ids = split($IDCON, $_->{'appruleid'});
		if( $_->{'type'} == 0 ) {
			foreach(@ids) {
				$ruleId{$_} = $enable;
                #system("echo '$_-$enable' >> /tmp/applicationTest");
			}
		}
		if( $_->{'type'} == 1 ) {
			foreach(@ids) {
				$rulePortId{$_} = $enable;
                #system("echo '$_-$enable' >> /tmp/applicationTest");
			}
		}
	}
	
	#===修改rule_file文件内容===#		
	for( my $i=0; $i<@lines; $i++ ) {
		
		my @line_data = split(",",$lines[$i]);
        my %line_data = &getRuleHash(\@line_data);
        my $appruleid = $line_data{'appruleid'};
		my $enable = $ruleId{$appruleid};
		if($enable eq "0" || $enable eq "1") {
			$line_data[4] = $enable;
            #system("echo '$appruleid-$enable' >> /tmp/applicationTest");
			my $record = join (",", @line_data);
			( $status, $mesg ) = &update_one_record( $rule_file, $i, $record );
		}
	}
	
	
	#===修改rulePort_file文件内容===#		
	for( my $i=0; $i<@linesPort; $i++ ) {
		
		my @line_data = split(",",$linesPort[$i]);
        my %line_data = &getRuleHash(\@line_data);
        my $appruleid = $line_data{'appruleid'};
		my $enable = $rulePortId{$appruleid};
		if( $enable eq "0" || $enable eq "1") {
			$line_data[4] = $enable;
            #system("echo '$appruleid-$enable' >> /tmp/applicationTest");
			my $record = join (",", @line_data);
			( $status, $mesg ) = &update_one_record( $rulePort_file, $i, $record );
		}
	}
	

	%ret_data->{'error_mesg'} = $mesg;
	%ret_data->{'data'} = $data;
	%ret_data->{'rule'} = \@rule;
	%ret_data->{'rulePort'} = \@rulePort;
	%ret_data->{'detail'} = \@detail_data;
	%ret_data->{'lines'} = \@lines;
	%ret_data->{'linesPort'} = \@linesPort;
	
	my $ret = $json->encode(\%ret_data);
	print $ret;
}


#获得规则应用状态
sub get_appStatus($) {
	my $apps = shift;
    my @apps = @$apps;
	my @lines;
	my @linesPort;
	my $enablenumber = 0;
	my $totalnumber = 0;
	my ( $status, $error_mesg );
	( $status, $mesg ) = &read_config_lines( $rule_file, \@lines );
	( $status, $mesg ) = &read_config_lines( $rulePort_file, \@linesPort );
    my @linesAll = (@lines, @linesPort);
    my @appidSearchs = ();
    foreach( @apps ) {
        push ( @appidSearchs, $_->{'appid'} );
    }
	my %lines = &getRuleHashGreps(\@appidSearchs, \@linesAll);
    foreach(@apps) {
        
        my $str = "暂无规则";
        my $tn  = 0;
        my $en  = 0;
        my $a = $lines{$_->{appid}};
        my @values = values %$a; 
        my $tn  = @values;
        foreach(@values) {
            if($_ eq "1") {
                $en++;
            }
        }
        unless( $tn == 0 ) {
            $str = $en . "/" . $tn;
        }
        $_->{'appStatus'} = $str;
    }
}

#获得规则去重后的rules
sub getRuleHashGrep() {
    my $appidSearch = shift;
    my $lines = shift;
    my @lines = @$lines;
    my %lines;
    #system("echo '#############################$appidSearch' >> /tmp/applicationTest");
    foreach( @lines ) {
        my @line = split(",", $_);
        my %line = &getRuleHash(\@line);
        my $appid = $line{'appid'};
        my $name = $line{'name'};
        my $enable = $line{'enable'};
        if($appid eq $appidSearch || $appidSearch eq '') {
            #system("echo '$appid-$name-$enable' >>/tmp/applicationTest");
            unless($lines{$name}) {
                $lines{$name} = $enable;
            }
        }
    }
    return %lines;
}
#批量获得规则去重后的rules
sub getRuleHashGreps() {
    my $appidSearchs = shift;    
    my $lines = shift;
    my @appidSearchs = @$appidSearchs;
    my %appidSearchs;
    my @lines = @$lines;
    my %lines;
    foreach(@appidSearchs) {
        my %hash;
        $appidSearchs{$_} = \%hash;
    }
    #system("echo '#############################$appidSearch' >> /tmp/applicationTest");
    foreach( @lines ) {
        my @line = split(",", $_);
        my %line = &getRuleHash(\@line);
        my $appid = $line{'appid'};
        my $name = $line{'name'};
        my $enable = $line{'enable'};
        if( $appidSearchs{$appid} ) {
            #system("echo '$appid-$name-$enable' >>/tmp/applicationTest");
            $appidSearchs{$appid}->{$name} = $enable;
        }
    }
    my @keys = keys %appidSearchs; 

    return %appidSearchs;
}
