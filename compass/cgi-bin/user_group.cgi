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

require '/var/efw/header.pl';
require 'list_panel_opt.pl';

#=================初始化全局变量到init_data()中去初始化========================#
my $custom_dir;         #要保存数据的目录名字
my $conf_dir;           #规则所存放的文件夹
my $conf_file;          #规则所存放的文件
my $user_group;			#用户组信息存放的文件
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my $test_hash;
my $test_hash2;
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
    $custom_dir         = '/AAA';
    $conf_dir           = "${swroot}".$custom_dir;
    $conf_file          = $conf_dir.'/user2';
	$usergroup_file     = $conf_dir.'/user_group';
    $need_reload_tag    = $conf_dir.'/add_list_need_reload';
	$setusergroup_file  = '/usr/local/bin/setusergroup.py';#后端脚本文件路径

    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
					<link rel="stylesheet" type="text/css" href="/include/yp_personal.css" />
					<link rel="stylesheet" type="text/css" href="/include/user_group.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/user_group.js"></script>';
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
    elsif ( $action eq 'apply_data' && $panel_name eq 'mesg_box' ) {
        &apply_data();
    }
    elsif ($action eq 'delete_data') {
        &delete_data();
    }
	elsif ($action eq 'add_group') {
		&add_group();
	}
	elsif ($action eq 'delete_group') {
		&delete_group();
	}
	elsif ($action eq 'edit_group') {
		&edit_group();
	}
	elsif ($action eq 'get_tree') {
		&get_tree_data;
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
	my $point = $test_hash->{'list'};
printf<<EOF
    <div id="mesg_box" class="container"></div>
    <div id="add_panel" class="container"></div>
	<div id="add_group_panel" class="container"></div>
	<div id="edit_group_panel" class="container"></div>
	<div id="panel_group_father" class="container">
		<div id="panel_user_group">
			
			<div id="user_group_title" >
				<div>用户组列表</div>
				<span class="opt-tools" style="float: right;">
						<input type="image" class="action-image" src="../images/add16x16.png" onclick="add_group_rule();" style="width: 14px;height: 14px;margin:2px;" />		
						
						<input type="image" class="action-image" src="../images/edit.png" onclick="edit_group_rule();" style="width: 14px;height: 14px;margin:2px;" />
					
						<input type="image" class="action-image" src="../images/delete.png" onclick="delete_group_rule();" style="width: 14px;height: 14px;margin:2px;" />
					
				</span>
			</div>
			<ul id="user_group">
			</ul>	
		</div>
		<div id="list_panel" >reciever</div>

	</div>
	

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
    $config{'name'}       = $temp[0];
    $config{'outtime'}    = $temp[1];
    $config{'groupid'}    = $temp[2];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;

    my @record_items = ();
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'outtime'} );
    push( @record_items, $hash_ref->{'groupid'} );
    return join ",", @record_items;
}

sub get_compare_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    #============自定义比较字段-BEGIN=========================#
    #一般来说比较的字段和保存的字段几乎都一致，但是存在保存时，
    #要更新修改时间等就不一样了，需要自己定义比较哪些字段=====#
    push( @record_items, $hash_ref->{'name'} );
    push( @record_items, $hash_ref->{'outtime'} );
    push( @record_items, $hash_ref->{'groupid'} );
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
	system "echo $par{'groupid'} > /var/efw/AAA/test";
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
    } else {
        ( $status, $mesg ) = &update_one_record( $conf_file, $item_id, $record );
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
	my $groupid = $par{'groupid_cp'};

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
			if($hash{'groupid'} eq $search){
			}else{
				next;
			}
		} else{
			next;
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
        $mesg = "删除成功"
        &create_need_reload_tag();
    }

     &send_status( $status, $reload, $mesg );
}


sub apply_data() {
    &clear_need_reload_tag();
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
	if(! -e $usergroup_file){
        system("touch $usergroup_file");
    }
}



#添加用户组
sub add_group() {
	my %hash;
	my $groupid   = $par{'groupid'};
	my $groupname = $par{'name'};
	my $description = $par{'description'};
	$groupid = `$setusergroup_file -a -i $groupid -g $groupname -z $description`;
	$groupid =~ s/\n//g;
	%hash->{'name'} = $groupname;
    %hash->{'description'} = $description;
    %hash->{'groupid'} = $groupid;
	my $result = $json->encode(\%hash);
    print $result;
	
;	
}

=pod
#将用户组数据插入json文件
sub add_group_in() {
	my ($groupid,$groupname,$description) = @_;
	my @lines = ();
	my ($a,$b,$c) = &read_config_lines($usergroup_file,\@lines);
	my $vv =$lines[0];
	my $pointer = $json->decode($vv);
	my $pointer2 = $pointer->{'list'}->[$groupid-1]->{'children'};
	my $length = @$pointer2;
	my %hash;
	
	$hash{'groupname'} = $groupname;
	$hash{'groupid'} = $groupid . "-" . ($length+1);
	$hash{'groupdescripe'} = $description;
	$hash{'children'} = undef;
	

	$pointer2->[$length] = \%hash;
	my $record = $json->encode($pointer);
	my ( $status, $mesg ) = &update_one_record( $usergroup_file,0,$record );
	
}
=cut

#删除用户组
sub delete_group() {
	
	my $groupid = $par{'groupid'};
	system "$setusergroup_file -d -i $groupid";
	
}

sub delete_model($groupid,\@array) {
	my( $id, $a ) = @_;
	foreach(@$a) {
		if($id == $_->{'groupid'}) {
			return $_;
		}
		if($_->{'children'} == undef) {
			next;
		}else{
			&delete_model($id , $_->{'children'});
		}
	}	
}

#编辑用户组
sub edit_group() {
	my %hash;
	my $groupid   = $par{'groupid'};
	my $groupname = $par{'name'};
	my $description = $par{'description'};
	system "$setusergroup_file -e -i $groupid -g $groupname -z $description";
	%hash->{'name'} = $groupname;
    %hash->{'description'} = $description;
	my $result = $json->encode(\%hash);
    print $result;
}

#获得树形数据
sub get_tree_data() {
	my @lines = ();
	my ( $status, $error_mesg)= &read_config_lines($usergroup_file,\@lines);
	my $json_data;
	foreach(@lines) {
		$json_data = $json_data . $_; 
	}
	print $json_data;
	
}
