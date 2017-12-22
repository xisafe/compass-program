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
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my $ipGroup_select;
my $dest_ip_text_select;
my $dest_any_select;
my $dest_ip_value=' ';

my $CUR_PAGE = "僵尸网络" ;      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '1';
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
    $custom_dir         = '/botnet';
    $conf_dir           = "${swroot}".$custom_dir;
    $conf_file          = $conf_dir.'/config';
    $botnetrules_file   = $conf_dir.'/botnetrules';
    $need_reload_tag    = $conf_dir.'/add_list_need_reload';	

    $read_conf_dir      ="/var/efw/objects";                        #读取数据的目录文件夹     
    $ip_groups_file     =$read_conf_dir.'/ip_object/ip_group';      #读取ip组文件
	$sourceip_file      = '/var/efw/objects/ip_object/ip_group';
    $setbotnet          ="/usr/local/bin/botnet.py";          #应用按钮调用py文件路径
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/set_botnet.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/add_panel_include_config.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/set_botnet.js"></script>';
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
    if ( $action eq 'save_data'  ) {
        &save_data();
        &show_page();
    }
    elsif( $action eq 'load_data' && $panel_name eq 'lib_panel') {
        &load_data_lib();
    }	
    elsif( $action eq 'load_data' && $panel_name eq 'DestIPGroup_panel') {
		&load_settingdata($sourceip_file);
	}
    elsif( $action eq 'apply_data' ) {
    	&apply_data();
    }
    else {
        &show_page();
    }

    if ($action eq 'save_data' || $action eq 'apply_data') {
        if ($action eq 'apply_data') {
            $log_oper = 'apply';
        }else{                                      
            $log_oper = 'edit';
        }
        &write_log($CUR_PAGE,$log_oper,0,$rule_or_congfig);
    }
}

sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);
    &display_main_body();
    &closepage();
}

sub load_settingdata() {
    my $file = shift;
    
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $file, \@lines );    
    my $record_num = @lines;
    $total_num = $record_num;
    
    for ( my $i = 0; $i < $record_num; $i++ ) {
        my %config;
        my @data_line = split(",",$lines[$i]);
        %config->{'name'} = $data_line[1];
        %config->{'id'} = $i;
        %config->{'valid'} = 1;
        push( @content_array, \%config );
    }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    

    my $ret = $json->encode(\%ret_data); 
    print $ret; 
}

sub display_main_body() {
    my %data = &loadFormData(); 
    my $reload; 
    if ( -e $need_reload_tag ) {
        $reload = 1;
    } else {
        $reload = 0;
    }
    printf<<EOF
    <script>
        \$(document).ready(function(){
            var se = document.getElementById('dest_ipgroup').selectedIndex;
            var val = document.getElementById('dest_ipgroup').options[se].value
            if (val == 'dest_any') {
                document.getElementById("DestIPGroup").style.display = 'none';
                document.getElementById("ipGroup").style.display = 'none';
                document.getElementById("dest_ip_text").style.display = 'none';
            }
            if (val == 'dest_ip') {
                document.getElementById("DestIPGroup").style.display = 'inline-block';
                document.getElementById("ipGroup").style.display = 'inline-block';
                document.getElementById("dest_ip_text").style.display = 'none'; 
            }
            if (val == 'dest_group') {
                document.getElementById("DestIPGroup").style.display = 'none';
                document.getElementById("ipGroup").style.display = 'none';
                document.getElementById("dest_ip_text").style.display = 'inline-block';
            }

        });
    </script>

    <div id="mesg_box" class="container"></div>
	<input type="hidden" id="apply-control" value="$reload">
    <div id="panel_rule_lib" class="container"></div>
	<div id="DestIPGroup_panel" class="container"></div>
EOF
    ;
    &openbox('96%', 'left', '僵尸网络配置'.$page_config{'page_title'} );
    &displayWebBody(\%data);
    &closebox();

}
sub displayWebBody() {
    my $data = shift;
	my %data = %$data;
	my $form = $data{'formdata'};
    my %formdata = %$form;
    # print $formdata{'dest_ipgroup'};
    if ($formdata{'dest_ipgroup'} eq 'dest_ip') {
        $ipGroup_select = 'selected';
        $dest_ip_value = $formdata{'DestIPGroup'};
        $dest_ip_text_select = '';
        $dest_any_select ='';
    }
    if ($formdata{'dest_ipgroup'} eq 'dest_group') {
        $ipGroup_select = '';
        $dest_ip_text_select = 'selected';
        $dest_any_select ='';
    }
    if ($formdata{'dest_ipgroup'} eq 'dest_any'){
        $ipGroup_select = '';
        $dest_ip_text_select = '';
        $dest_any_select ='selected';
    }
	my $ip = $data{'ipgroups'};
	my @ipgroups = @$ip;


	

    printf<<EOF
    <form name = "setbotnet-form" action='$ENV{SCRIPT_NAME}' method="post">
        <table width="100%" cellpadding="0" cellspacing="0">
                
                <tr class ='odd'>
                    <td class='add-div-type'>目标IP组*</td>
                    <td>
                        <select id="dest_ipgroup" name="dest_ipgroup" class="add-panel-form-select" style="width:174px;vertical-align: text-top;margin-right: 10px;">
                        <option id="dest_any" value="dest_any $dest_any_select">任意</option>
                        <option id="dest_ip" value="dest_ip" $ipGroup_select>IP组</option>
                        <option id="dest_group" value="dest_group" $dest_ip_text_select>网络/IP</option></select>
                        <div id='ipselect' style="display:inline-block;">
                            <input type="text" id="DestIPGroup" name="DestIPGroup" value=$dest_ip_value class="add-panel-form-text" readonly="readonly" style="width: 117px;display:none;float: left;margin-right: 10px;">
                        </div>
                        <div id='netselect' style="display:inline-block;">
                            <input type="button" id="ipGroup" name="ipGroup" class="add-panel-form-button" value="配置" style="width: 40px; height: 20px; border-radius: 4px;display: none;" onclick="DestIPGroup_panel.show()">
                        </div>
                        <div style="display:inline-block;">
                            <textarea id="dest_ip_text" name="dest_ip_text" class="add-panel-form-textarea" placeholder="请填写IP(每行一个)" style="width: 119px; vertical-align: middle;display:none;">$formdata{'dest_ip_text'}</textarea>
                        </div>
                <script>
                    var se = document.getElementById('dest_ipgroup').selectedIndex;
                        document.getElementById('dest_ipgroup').options[se].value
                    \$("#dest_ipgroup").change(function(){
                        var index = document.getElementById("dest_ipgroup").selectedIndex;
                        if (index == 0) {
                            document.getElementById("DestIPGroup").style.display = 'none';
                            document.getElementById("ipGroup").style.display = 'none';
                            document.getElementById("dest_ip_text").style.display = 'none';
                            document.getElementById("DestIPGroup").value = '';  
                            document.getElementById("dest_ip_text").value = '';
                        }
                        if (index == 1) {
                            document.getElementById("DestIPGroup").style.display = 'block';
                            document.getElementById("ipGroup").style.display = 'block';
                            document.getElementById("dest_ip_text").style.display = 'none';
                            document.getElementById("DestIPGroup").value = '';  
                            document.getElementById("dest_ip_text").value = '';  
                        }
                        if (index == 2) {
                            document.getElementById("DestIPGroup").style.display = 'none';
                            document.getElementById("ipGroup").style.display = 'none';
                            document.getElementById("dest_ip_text").style.display = 'block';
                            document.getElementById("DestIPGroup").value = '';  
                            document.getElementById("dest_ip_text").value = '';
                        }
                    })
                </script>


EOF
	;
	# forSelect();
	printf<<EOF    
						</select>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>防护规则*</td>
                    <td style="position: relative;">
                        <textarea name="webRule" class="setbotnet-textarea" id="setbotnet-webrule" readonly="readonly">$formdata{'webRule'}</textarea>
                        <input type="button" class="net_button setbotnet-note" id="setbotnet-webrule-btn" value="配置" onclick="show_config_panel_area(lib_panel,'setbotnet-webrule');">
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>启用</td>
                    <td>
EOF
	;
	forCheckbox();
	print<<EOF                       
                    </td>
                </tr>
                <tr class="table-footer"> 
                    <td colspan="2">
                        <input type="submit" class="net_button" id="webdefend-save" value="保存"/>
                        <input type="hidden" name="ACTION" value="save_data">
                    </td>
                </tr>
            </table>
        </form>
EOF
    ;
    sub forCheckbox {
    	my $enable = $formdata{'enable'};
    	if($enable eq 'on') {
			print '<input type="checkbox" name="enable" value="on" checked>';
		}else {
			print '<input type="checkbox" name="enable" value="on">'
		}
    }
	sub forSelect {
		my $ipgroup = $formdata{'ipGroup'};
		print "<option disabled value=''>请选择目标IP组</option>";
		foreach(@ipgroups) {
			if($ipgroup eq $_) {
				print "<option value='$_' selected='selected'>$_</option>";
			}else {
				print "<option value='$_'>$_</option>";
			}
		}
	}
}
sub loadFormData() {
    my @lines;
	my %formdata;
	my @lines_ipgroups;
	my @lines_ipgroups_names;
    my %data;
	&read_config_lines( $conf_file, \@lines);
	&read_config_lines($ip_groups_file ,\@lines_ipgroups);

    %formdata = &get_config_hash($lines[0]);
    $formdata{'DestIPGroup'} = &datas_hander($formdata{'DestIPGroup'},'load');
    $formdata{'dest_ip_text'} = view_assembling($formdata{'dest_ip_text'});
    $formdata{'ipPort'} = view_assembling($formdata{'ipPort'});
	$formdata{'webRule'} = view_assembling($formdata{'webRule'});
	
	foreach(@lines_ipgroups){	
        push( @lines_ipgroups_names,(split(",",$_))[1]);
    }
	
	$data{'formdata'} = \%formdata;
	$data{'ipgroups'} = \@lines_ipgroups_names;
    return %data;

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
	$config{'name'}          = $temp[0];
	$config{'description'}   = $temp[1];
    $config{'DestIPGroup'}   = $temp[2];
	$config{'dest_ip_text'}  = $temp[3];
	$config{'webRule'}       = $temp[4];
    $config{'enable'}        = $temp[5];
    $config{'dest_ipgroup'}  = $temp[6];

    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    # push( @record_items, $hash_ref->{'name'} );
    # push( @record_items, $hash_ref->{'description'} );
    push( @record_items,  'BOTNET');
    push( @record_items, 'BOTNET' );
    my $DestIPGroup = &datas_hander($hash_ref->{'DestIPGroup'},'save');
    push( @record_items, $DestIPGroup );
    my $dest_ip_text = &save_assembling($hash_ref->{'dest_ip_text'});
	push( @record_items, $dest_ip_text );
    push( @record_items, $hash_ref->{'webRule'} );
    push( @record_items, $hash_ref->{'enable'} );
    push( @record_items, $hash_ref->{'dest_ipgroup'} );
    return join ",", @record_items;
}

sub get_compare_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    #============自定义比较字段-BEGIN=========================#
    #一般来说比较的字段和保存的字段几乎都一致，但是存在保存时，
    #要更新修改时间等就不一样了，需要自己定义比较哪些字段=====#
    push( @record_items, $hash_ref->{'name'} );
	push( @record_items, $hash_ref->{'description'} );
	push( @record_items, $hash_ref->{'ipGroup'} );
	push( @record_items, $hash_ref->{'ipPort'} );
    push( @record_items, $hash_ref->{'webRule'} );
    push( @record_items, $hash_ref->{'enable'} );
    #============自定义比较字段-END===========================#
    return join ",", @record_items;
}

sub save_data_handler() {
    my ( $status, $mesg ) = ( -1, "未开始检测各项的合法性" );

    #===第二步，处理说明信息===#

    $par{'description'}  = &prepare_note( $par{'description'} );
	
    #===第三步，处理启用禁用===#
    if ( $par{'enable'} ne "on" ) {
        $par{'enable'} = "off";
    }
	#===将端口，web防护规则拼装===#
	$par{'ipPort'} = &save_assembling( $par{'ipPort'} );
	$par{'webRule'} = &save_assembling( $par{'webRule'} );

	if($par{'name'} !~ /[!@#$%^&*]/ && $par{'description'} !~ /!@#$%^&*/) {
		( $status, $mesg ) = ( 0, "检测合格");
	}
    return ( $status, $mesg );
}

sub save_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未保存" );
    #===检测字段合法性===#
    ( $status, $mesg ) = save_data_handler();
    if ( $status != 0 ) {
        #&send_status( $status, $reload, $mesg );
        return;
    }

    my $record = &get_config_record( \%par );
	my @lines = ();
	$lines[0] = $record;
	( $status, $mesg ) = &write_config_lines( $conf_file, \@lines );    
    if( $status == 0 ) {
        $reload = 1;
        &create_need_reload_tag();
        $mesg = "保存成功";
    } else {
        $mesg = "保存失败";
    }

    # &send_status( $status, $reload, $mesg );
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
		$hash{'webAction_view'} = &webAction_handler($hash{'webAction'});#将webACtion转化为中文
		$hash{'idView'} = $id+1;#为界面显示的列表序号赋值
		$hash{'ipPort'} = &view_assembling( $hash{'ipPort'} );#对端口号进行处理
		$hash{'webRule'} = &view_assembling( $hash{'webRule'} );#对web防护规则进行处理
		
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

sub toggle_enable($) {
    my $enable = shift;
    my $operation = "启用";
    if ( $enable ne "on" ) {
        $operation = "禁用";
    }
    my @lines = ();
    my $reload = 0;

    my ( $status, $mesg ) = &read_config_lines( $conf_file, \@lines );
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
            $lines[$i] = &get_config_record(\%config);
        }
    }

    my ( $status, $mesg ) = &write_config_lines( $conf_file, \@lines );
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
    my $result;
    $result = `sudo $setbotnet`;
    chomp($result);
    my $msg;
    if($result == 0){
        $msg = "应用成功";
    }else{
        $msg = "应用失败";
    }
    &clear_need_reload_tag();
	#system "sudo $setbotnet";
    &send_status( 0, 0, $msg );
}

sub datas_hander() {
    my ($data,$act) = @_;
    if( $act eq 'save' ) {
        $data =~ s/，/&/g;
    }
    if($act eq 'load') {
        $data =~ s/&/，/g;
    }
    return $data;
    
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
    system( "rm  $need_reload_tag" );
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}

#处理输出的动作
sub webAction_handler() {
	if($_[0] == 0) {
		return '允许';
	}else {
		return '拒绝';
	}
}

#读取ip组文件
sub read_data(){
    my %ret_data; 
    my @lines_ipgroups;
	my @lines_ipgroups_names;
    my ( $status, $error_mesg)= &read_config_lines($ip_groups_file ,\@lines_ipgroups);

    foreach(@lines_ipgroups){
        push( @lines_ipgroups_names,(split(",",$_))[1]);
    }

    %ret_data->{'ipgroups_data'}    = \@lines_ipgroups_names;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $error_mesg;
    my $ret = $json->encode(\%ret_data);
    print $ret; 

}

#加载botnet防护规则库

sub get_data_lib(){
	system '/usr/local/bin/getbotnetrules.py > /var/efw/botnet/botnetrules 2>&1';
}


sub load_data_lib(){
	&get_data_lib();
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $botnetrules_file, \@lines );
	@lines = split("&",$lines[0]);
	system $str;
    
    my $record_num = @lines;
    $total_num = $record_num;
    
    for ( my $i = 0; $i < $record_num; $i++ ) {
        my %config;
        my @data_line = split("#",$lines[$i]);
        %config->{'name'} = $data_line[0];
        %config->{'description'} = $data_line[1];
        %config->{'id'} = $i;
        %config->{'valid'} = 1;
        push( @content_array, \%config );
    }
    
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'error_mesg'} = $error_mesg;
    %ret_data->{'page_size'} = $total_num;
    

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub save_assembling(){
	$_ = shift;
	$_ =~ s/\n/&/g;
	$_ =~ s/\r//g;
	return $_;
	
}

sub view_assembling(){
	$_ = shift;
	$_ =~ s/&/\r\n/g;
	return $_;
}


