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
my $read_conf_header_dir;
my $http_rule_conf_file;
my $hidden_header_file;					 					   
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变

my $CUR_PAGE = "WEB应用防护" ;      #当前页面名称，用于记录日志
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
    $custom_dir                 = '/webdefend';
    $conf_dir                   = "${swroot}".$custom_dir;
    $conf_file                  = $conf_dir.'/config';

    $csrf_host_conf_file        = $conf_dir.'/config_csrf_host';
    $csrf_rule_conf_file        = $conf_dir.'/config_csrf_rule';

    $mgxx_rule_conf_file        = $conf_dir.'/config_info_sen';
    $mgxx_conf_file             = '/var/efw/security_objects/dataleak/config';
    
    $brute_rule_con_file        = $conf_dir.'/config_brute_rule';
	$http_rule_conf_file        = $conf_dir.'/config_app_hidden_http_rule';

    $need_reload_tag            = $conf_dir.'/add_list_need_reload';
	$replace_page_file          = $conf_dir.'/replace_err_page_flag'; 
	
    $read_conf_header_dir ="/var/efw/webdefend";                        #读取数据的目录文件夹     
    $hidden_header_file   =$read_conf_header_dir.'/config_app_hidden_headers';																			  
    $read_conf_dir      ="/var/efw/objects";                        #读取数据的目录文件夹     
    $ip_groups_file     =$read_conf_dir.'/ip_object/ip_group';      #读取ip组文件
	$webrules_file      = $conf_dir.'/webrules';
	$setweb             ="/usr/local/bin/setwebdefend.py";          #应用按钮调用py文件路径
    $cmd_set_webdefendIsactive = "/usr/local/bin/webdefendIsactive";
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/webdefend.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/webdefend.js"></script>';
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
    if ( $action eq 'save_data'  && $panel_name eq 'main_panel') {
        &save_data();
        &show_page();
    }
    elsif ( $action eq 'save_data'  && $panel_name ne 'main_panel') {
        &save_data_other();
    }
	elsif( $action eq 'save_complete') {
        &save_complete();
	}
	elsif( $action eq 'load_data' && $panel_name eq 'lib_panel') {
		&load_data_lib();
	}
    elsif( $action eq 'load_data' && $panel_name ne 'lib_panel') {
        &load_data_other();
    }
    elsif ($action eq 'delete_data') {
        &delete_data();
    }elsif ($action eq 'load_domain') {
        &load_domain();
    }
    elsif ($action eq 'sava_domain_brute') {
        &sava_domain_brute();
    }elsif ($action eq 'change_connect_type') {
        &change_connect_type();
    }
    elsif( $action eq 'apply_data' && $panel_name eq 'mesg_box') {
    	&apply_data();
    }
    elsif ($action eq 'enable_data') {
        &toggle_enable( "on" );
    }
    elsif ($action eq 'disable_data') {
        &toggle_enable( "off" );
    }
    elsif ( $action eq 'load_brute_data') {
        &load_brute_data();
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
sub ModIsOK()
{  
    my $result;
    $result =`sudo $cmd_set_webdefendIsactive`;
    chomp($result);
    if ($result eq '1'){
        return 1;
    }else{
        return 0;
    }
}
sub show_page() {
    &openpage($page_config{'page_title'}, 1, $extraheader);

    &display_main_body();
    &closepage();
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
    <div id="mesg_box" class="container"></div>
	<input type="hidden" id="apply-control" value="$reload">
	<div id="panel_rule_lib" class="container"></div>

    <div id="csrf_list_panel" class="container"></div>
    <div id="csrf_add_panel" class="container"></div>
    
    <div id="mgxx_list_panel" class="container"></div>
    <div id="mgxx_add_panel" class="container"></div>

    <div id="panel_brute" class="container"></div>
	<div id="panel_site_hide" class="container"></div>

EOF
    ;
    &openbox('96%', 'left', 'WEB防护配置');
    &displayWebBody(\%data);
    &closebox();

}
sub displayWebBody($) {
	my $data = shift;
    my %data = %$data;
	my $form = $data{'formdata'};
    my %formdata = %$form;
	my $ip = $data{'ipgroups'};
	my @ipgroups = @$ip;

    my $enable = $formdata{'enable'};
    my $able="";
    if($enable eq "on")
    {
        $able="checked";
    }
    else{
        $able="unchecked";
        $enable = "on";
    }

	my $enableordis="";
    my $title="";
    my $dest=ModIsOK();
    system("echo '$dest'>>/tmp/mmtest.log");
    if($dest eq "0"){
        $able = '';     
        $enableordis="disabled";
        $title="WEB防护功能模块未激活，暂无法启用";
        
      }else{
        $enableordis="";
        $title="";
    }

    printf<<EOF
    <form name = "webdefend-form" action='$ENV{SCRIPT_NAME}' method="post">
        <table width="100%" cellpadding="0" cellspacing="0">
        <!--    <tr class ='odd'>
                    <td class='add-div-type'>名称*</td>
                    <td>
                        <input type="text" name="name" value="$formdata{'name'}"> 
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>描述</td>
                    <td>
                        <textarea name="description" class="webdefend-textarea">$formdata{'description'}</textarea>
                    </td>
                </tr>     -->
                <tr class ='odd'>
                    <td class='add-div-type'>目标IP组*</td>
                    <td>
                        <select name="ipGroup" style="width:173px">
EOF
	;
	forSelect();
	printf<<EOF    
						</select>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>端口*</td>
                    <td style="position: relative;">
                        <textarea name="ipPort" id="webdefend-ipport" class="webdefend-textarea" >$formdata{'ipPort'}</textarea>
                        <span class="webdefend-note">(每行一个, 可输入多个)</span>
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>WEB防护规则</td>
                    <td style="position: relative;">
                        <textarea name="webRule" class="webdefend-textarea" id="webdefend-webrule" readonly="readonly">$formdata{'webRule'}</textarea>
                        <input type="button" class="net_button webdefend-note" id="webdefend-webrule-btn" value="配置" data="lib" onclick="panel_show(this);">
                    </td>
                </tr>
                 <tr class ='odd'>
                    <td class='add-div-type'>应用隐藏</td>
                    <td>
EOF
	;
	forHiddenCheckbox();
	print<<EOF   
	             <span style="display:inline-block;width:109px;">HTTP</span>
                 <input type="button" class="net_button" id="webdefend-hidden-btn" value="配置" data="hideSite" onclick="panel_show(this);">
	                </td>   
                </tr>					 
                <tr class ='odd'>
                    <td class='add-div-type'>口令防护</td>
                    <td>
EOF
    ;
    forBruteCheckbox();
    print<<EOF
                 <span style="display:inline-block;width:109px;">口令暴力破解防护</span><input type="button" class="net_button" id="webdefend-brute-btn" value="配置" data="brute" onclick="panel_show(this);" style="margin-left: 19px;">
                    </td> 
                </tr>
                
                <tr class ='odd'>
                    <td class='add-div-type'>网站攻击防护</td>
                    <td style="position: relative;">
EOF
    ;
    forCSRFcheckbox();
    print<<EOF
                        <span style="display:inline-block;width:109px;">CSRF防护</span>
                        <input type="button" class="net_button " id="" value="配置" data="csdf" onclick="panel_show(this);">
                    </td>
                </tr>

                <tr class ='odd'>
                    <td class='add-div-type'>数据泄密防护</td>
                    <td style="position: relative;">
EOF
    ;
    forMGXXcheckbox();
    print<<EOF
                        <span style="display:inline-block;width:109px;">敏感信息防护</span>
                        <input type="button" class="net_button " id="" value="配置" data="mgxx" onclick="panel_show(this);">
                    </td>
                </tr>

                <tr class ='odd'>
                    <td class='add-div-type'>启用</td>
                    <td>
                    <input type="checkbox" name="enable" value="$enable" $enableordis $able>
               <span><font color="red">&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp $title</font></span>
EOF
	;
	# forCheckbox();
	print<<EOF                       
                    </td>
                </tr>

                <tr class="table-footer"> 
                    <td colspan="2">

                        <input type="submit" class="net_button" id="webdefend-save" value="保存"/>
                        <input type="hidden" name="ACTION" value="save_data">
                        <input type="hidden" name="panel_name" value="main_panel">
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
    sub forCSRFcheckbox {
        my $csrfEnable = $formdata{'csrfEnable'};
        if($csrfEnable eq 'on'){
            print '<input type="checkbox" name="csrfEnable" value="on" checked>';
        }else{
            print '<input type="checkbox" name="csrfEnable" value="on">';
        }
    }
    sub forMGXXcheckbox {
        my $csrfEnable = $formdata{'mgxxEnable'};
        if($csrfEnable eq 'on'){
            print '<input type="checkbox" name="mgxxEnable" value="on" checked>';
        }else{
            print '<input type="checkbox" name="mgxxEnable" value="on">';
        }
    }
	sub forHiddenCheckbox(){
        my $hiddenEnable = $formdata{'hiddenEnable'};
        if($hiddenEnable eq 'on'){
            print '<input type="checkbox" name="hiddenEnable" value="on" checked>';
        }else{
            print '<input type="checkbox" name="hiddenEnable" value="on">';
        }
    }
    sub forBruteCheckbox(){
    my $bruteEnable = $formdata{'bruteEnable'};
    if($bruteEnable eq 'on'){
        print '<input type="checkbox" name="bruteEnable" value="on" checked>';
    }else{
        print '<input type="checkbox" name="bruteEnable" value="on">';
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
	$formdata{'ipPort'} = view_assembling($formdata{'ipPort'});
	$formdata{'webRule'} = view_assembling($formdata{'webRule'});
	
	foreach(@lines_ipgroups){	
        push( @lines_ipgroups_names,(split(",",$_))[1]);
    }
	
	$data{'formdata'} = \%formdata;
	$data{'ipgroups'} = \@lines_ipgroups_names;
    return %data;

}
sub load_domain() {
    my @lines;
    my ( $status, $mesg, $total_num ) = &read_config_lines( $csrf_host_conf_file, \@lines); 
    my %hash;
    my @lines_temp = split(/,/,$lines[0]);
    %hash->{'domain'} = $lines_temp[1];

    my $result = $json->encode(\%hash);
    print $result;

}
sub sava_domain_brute() {
    my $panel_name = $par{'panel_name'};
    my $config_file;
    my $info;
    if ($panel_name eq 'csrf_list_panel') {
        $config_file = $csrf_host_conf_file;
        $info = '1,'.$par{'domain'};
    }else{
        $config_file = $brute_rule_con_file;
        $info = &get_config_record_other( \%par );
    }
    # my $domain = $par{'domain'};
    my @lines;
    $lines[0] = $info;
    my ( $status, $mesg ) = &write_config_lines($config_file,\@lines);
    my $reload = 0;
    &send_status( $status, $reload, $mesg );
    return;
}

sub change_connect_type() {
    my $mgxx_select = $par{'mgxx_select'};

    my @lines = ();
    &read_config_lines( $mgxx_rule_conf_file, \@lines );

    my $len = scalar( @lines );

    my @new_lines = ();
    for ( my $i = 0; $i < $len; $i++ ) {
      
        chomp(@lines[$i]);
        my @temp = split(/,/, $lines[$i]);
        if ($temp[4] ne $mgxx_select) {
            $temp[4] = $mgxx_select;
            $lines[$i] = join(",",@temp);
        }

        push(@new_lines,$lines[$i]);
    }

    my ( $status, $mesg ) = &write_config_lines( $mgxx_rule_conf_file, \@new_lines );

    my %ret_data;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $mesg;

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
    my @temp = split(/,/, $line_content);

    my $config_file = &judgePanel();

    if ($config_file eq $csrf_rule_conf_file ) {
        $config{'need_target'}       = $temp[1];
        $config{'allow_rerfer'} = $temp[2];
        $config{'enable'}    = $temp[4];
    } elsif ($config_file eq $mgxx_rule_conf_file) {
        $config{'mgxx_comb_stra'}       = $temp[0];
        $config{'mgxx_info'}       = $temp[1];
        $config{'description'} = $temp[2];
        $config{'min_num'}    = $temp[3];
        $config{'connect_type'} = $temp[4];
    } elsif ($config_file eq $conf_file) {
        $config{'name'}              = $temp[0];
        $config{'description'}       = $temp[1];
        $config{'ipGroup'}           = $temp[2];
        $config{'ipPort'}            = $temp[3];
        $config{'webRule'}           = $temp[4];
        $config{'enable'}            = $temp[5];
        $config{'hiddenEnable'}      = $temp[7];       
        $config{'bruteEnable'}       = $temp[8];               
        $config{'csrfEnable'}        = $temp[6];              
        $config{'mgxxEnable'}        = $temp[9];
       
    } elsif($config_file eq $mgxx_conf_file) {
        $config{'storage_id'}       = $temp[0];
        $config{'mgxx_name'} = $temp[1];
        
        if ($temp[3] eq '0') {
            $config{'type'} = '内置';
            $config{'mgxx_reg'}    = '---';
        }else{
            $config{'type'}    = $temp[2];
            my @temp_temp;
            &read_config_lines( $temp[4], \@temp_temp);
            $config{'mgxx_reg'}    = join("<br/>",@temp_temp);
        }
        
    }

    #============自定义字段组装-END===========================#
    return %config;
}
sub judgePanel() {
    my $panel_name = $par{'panel_name'};
    my $config_file;
    if ($panel_name eq 'csrf_list_panel' || $panel_name eq 'csrf_add_panel') {
        $config_file = $csrf_rule_conf_file;
    }elsif($panel_name eq 'mgxx_list_panel'){
        $config_file = $mgxx_rule_conf_file;
    }elsif($panel_name eq 'mgxx_add_panel'){
        $config_file = $mgxx_conf_file;
    }elsif($panel_name eq 'brute_panel'){
        $config_file = $brute_rule_con_file;
    }elsif($panel_name eq '' || $panel_name eq 'main_panel'){
        $config_file = $conf_file;
    }
    return $config_file;
}  

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    push( @record_items, 'WEB_defend' );
	push( @record_items, 'WEB_defend' );
    push( @record_items, $hash_ref->{'ipGroup'} );
    push( @record_items, $hash_ref->{'ipPort'} );
    push( @record_items, $hash_ref->{'webRule'} );
    push( @record_items, $hash_ref->{'enable'} );
    if ($hash_ref->{'csrfEnable'} eq '') {
        $hash_ref->{'csrfEnable'} = 'off';
    }
    push( @record_items, $hash_ref->{'csrfEnable'} );    
    if ($hash_ref->{'hiddenEnable'} eq '') {
        $hash_ref->{'hiddenEnable'} = 'off';
    }
    push( @record_items, $hash_ref->{'hiddenEnable'} );
    if ($hash_ref->{'bruteEnable'} eq '') {
        $hash_ref->{'bruteEnable'} = 'off';
    }
    push( @record_items, $hash_ref->{'bruteEnable'} );    
    if ($hash_ref->{'mgxxEnable'} eq '') {
        $hash_ref->{'mgxxEnable'} = 'off';
    }
    push( @record_items, $hash_ref->{'mgxxEnable'} );


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

sub get_compare_record_CSRF($) {
    my $hash_ref = shift;
    my @record_items = ();
    #============自定义比较字段-BEGIN=========================#
    #一般来说比较的字段和保存的字段几乎都一致，但是存在保存时，
    #要更新修改时间等就不一样了，需要自己定义比较哪些字段=====#
    push( @record_items, $hash_ref->{'need_target'} );
    push( @record_items, $hash_ref->{'allow_rerfer'} );
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
    &debug2file($par{'ipPort'});
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
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $record = &get_config_record( \%par );
	my @lines = ();
	$lines[0] = $record;
	( $status, $mesg ) = &write_config_lines( $conf_file, \@lines );    
    if( $status == 0 ) {
        $reload = 0;
        &create_need_reload_tag();
        $mesg = "保存成功";
    } else {
        $mesg = "保存失败";
    }

}
sub get_config_http_hidden_record($){
    my $hash = shift;
    my @record_items = ();
    my $record = $hash->{'content'}; #a:b&c:d
    my @hash_record = split (/&/,$record);#a:b c:d
    #my @hash_record_string = join ",", @hash_record;

    my @hash_ref;
    my @content = ();
    for($i=0;$i<@hash_record;$i++){
        @hash_ref = split (/:/,$hash_record[$i]); #abcd
        my $temp = "$hash_ref[0],$hash_ref[1],on";#a,b,onc,d,on
        
        push(@content, $temp);		 
    }    
    return join "&", @content;							  
}
sub save_complete(){
    
    my ( $status, $reload, $mesg ) = ( -1, 0, "未保存" );
    my $record = &get_config_http_hidden_record( \%par );
    my @lines = ();
    @lines = split("&",$record);
		  
    ( $status, $mesg ) = &write_config_lines( $http_rule_conf_file, \@lines);   
# print $par{'replace_page'};
    if ($par{'replace_page'} eq 'true') {
        # print $replace_page_file;
        system("touch $replace_page_file");

    }else{
         
        system("rm $replace_page_file");        
    }

    if( $status == 0 ) {
        $reload = 0;
        &create_need_reload_tag();
        $mesg = "保存成功";
    } else {
        $mesg = "保存失败";
    }

    &send_status($status,$reload,$mesg);
} 

sub save_data_handler_other() {
    my $config_file = &judgePanel();
    my ( $status, $mesg ) = ( -1, "未开始检测各项的合法性" );

    #===第一步，检查名称是否重名===#
    my $name_exist_line_num = "";
    
    ( $status, $mesg, $name_exist_line_num ) = &where_is_field( $config_file , ",", 0, $par{'mgxx_name'} );


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
    # if ( $par{'id'} ne "" ) {
    #     my $exist_record = &get_one_record( $config_file, $par{'id'} );
    #     my %exist_record_hash = &get_config_hash( $exist_record );
    #     my $compare_record_old = &get_compare_record_CSRF( \%exist_record_hash );
    #     my $compare_record_new = &get_compare_record_CSRF( \%par );
    #     if ( $compare_record_old eq $compare_record_new ) {
    #         $status = -1;
    #         $mesg = "配置未改变";
    #     } else {
    #         $status = 0;
    #         $mesg = "检测合格";
    #     }
    # } else {
        $status = 0;
        $mesg = "检测合格";
    # }

    return ( $status, $mesg );
}

sub save_data_other() {
    my $config_file = &judgePanel();

    my ( $status, $reload, $mesg ) = ( -1, 0, "未保存" );
    #===检测字段合法性===#
    ( $status, $mesg ) = save_data_handler_other();
    if ( $status != 0 ) {
        &send_status( $status, $reload, $mesg );
        return;
    }

    my $record = &get_config_record_other( \%par );
    # print $record;
    # print $config_file;
    my $item_id = $par{'id'};

    if( $item_id eq '' ) {
        ( $status, $mesg ) = &append_one_record( $config_file , $record );
    } else {
        ( $status, $mesg ) = &update_one_record( $config_file , $item_id, $record );
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
sub get_serviceId($) {
    my @lines;
    my @max_id;
    my ( $status, $mesg, $total_num ) = &read_config_lines( $conf_file, \@lines);
    foreach(@lines){
        my @lines_ref = split(/,/,$_);
        push(@max_id,$lines_ref[0]);
    }
    
    @max_id=sort {$a<=>$b}@max_id;
    return $max_id[$#max_id] ? $max_id[$#max_id]+1 :1 ;
}
sub get_config_record_other($) {
    my $config_file = &judgePanel();

    my $hash_ref = shift;
    my @record_items = ();
    if ($config_file eq $csrf_rule_conf_file) {
        my $id = &get_serviceId( $csrf_rule_conf_file );
        push(@record_items, $id); 
        push( @record_items, $hash_ref->{'need_target'} );
        push( @record_items, $hash_ref->{'allow_rerfer'} );
        push( @record_items, 1 );
        push( @record_items, $hash_ref->{'enable'} );
    }elsif($config_file eq $mgxx_rule_conf_file){
        my $mgxx_name = $hash_ref->{'mgxx_name'};
        $mgxx_name =~ s/,/，/g;
        push( @record_items, $mgxx_name );
        push( @record_items, $hash_ref->{'mgxx_checked'} );
        push( @record_items, $hash_ref->{'mgxx_description'} );
        push( @record_items, $hash_ref->{'mgxx_num'} );
        push( @record_items, $hash_ref->{'mgxx_select'} );
    }elsif($config_file eq $brute_rule_con_file){
        push( @record_items, $hash_ref->{'loginpage'} );
        push( @record_items, $hash_ref->{'brute_number'} );
        push( @record_items, $hash_ref->{'rate'} );
    }

    return join ",", @record_items;
}
sub load_data_other(){

    my %ret_data;

    my @content_array = ();
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'total_num'} = $total_num;
    if ( -e $need_reload_tag ) {
        %ret_data->{'reload'} = 0;
    } else {
        %ret_data->{'reload'} = 0;
    }

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}

sub get_detail_data($) {

    my $config_file = &judgePanel();

    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $from_num = ( $current_page - 1 ) * $page_size;
    my $search = &prepare_search( $par{'search'} );

    my @lines = ();
    my ( $status, $mesg, $total_num ) = ( -1, "未读取", 0 );
    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        ( $status, $mesg, $total_num ) = &read_config_lines( $config_file, \@lines);
    } else {
        ( $status, $mesg, $total_num ) = &get_one_page_records( $config_file, $page_size, $current_page, \@lines );
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

        $hash{'index'} = $id+1; #自定义id，id可以是任何字符，只要能唯一区别每一条数据
		$hash{'id'} = $id; #自定义id，id可以是任何字符，只要能唯一区别每一条数据
        push( @$content_array_ref, \%hash );
        $total_num++;
    }  
	

    return ( $status, $mesg, $total_num );
}

sub delete_data() {
    
    my $config_file = &judgePanel();

    my $reload = 0;
    my ( $status, $mesg ) = &delete_several_records($config_file , $par{'id'} );

    if( $status == 0 ) {
        $reload = 0;
        $mesg = "删除成功"
        &create_need_reload_tag();
    }

    &send_status( $status, $reload, $mesg );
}




sub toggle_enable($) {

    my $config_file = &judgePanel();

    my $enable = shift;
    my $operation = "启用";
    if ( $enable ne "on" ) {
        $operation = "禁用";
    }
    my @lines = ();
    my $reload = 0;

    my ( $status, $mesg ) = &read_config_lines( $config_file, \@lines );
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
            $lines[$i] = &get_config_record_other(\%config);
        }
    }

    my ( $status, $mesg ) = &write_config_lines( $config_file, \@lines );
    if( $status != 0 ) {
        $mesg = "$operation失败";
    } else {
        $mesg = "$operation成功";
        $reload = 0;
        &create_need_reload_tag();
    }

    &send_status( $status, $reload, $mesg );
    return;
}

sub apply_data() {
    &clear_need_reload_tag();
	`sudo $setweb`;
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
    system( "rm  $need_reload_tag" );
}

sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }    
    if(! -e $csrf_host_conf_file){
        system("touch $csrf_host_conf_file");
    }    
    if(! -e $csrf_rule_conf_file){
        system("touch $csrf_rule_conf_file");
    }    
    if(! -e $mgxx_rule_conf_file){
        system("touch $mgxx_rule_conf_file");
    }    
    if(! -e $brute_rule_con_file){
        system("touch $brute_rule_con_file");
    }    
    if(! -e $http_rule_conf_file){
        system("touch $http_rule_conf_file");
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

#加载web防护规则库

sub get_data_lib(){
	system '/usr/local/bin/getwebrules.py > /var/efw/webdefend/webrules 2>&1';
}


sub load_data_lib(){
	&get_data_lib();
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg) = &read_config_lines( $webrules_file, \@lines );
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
    $_ =~ s/&*$//;
	return $_;
	
}

sub view_assembling(){
	$_ = shift;
	$_ =~ s/&/\r\n/g;
	return $_;
}

sub load_brute_data {
    my %hash;
    my @lines;
    my @content_array = ();
    my ( $status, $mesg, $total_num ) = &read_config_lines($brute_rule_con_file, \@lines);
    my ( $status, $error_mesg, $total_num ) = &get_detail_data( \@content_array );
    my @headers = &get_headers();   
    my @http_rule = &get_http_rule();

       %hash = &get_brute_config_hash($lines[0]);
       %hash->{'detail_data'} = \@content_array;
       %hash->{'headers'} = \@headers;
       %hash->{'http_content'} = \@http_rule;

    if ( -e $replace_page_file ) {
        %hash->{'replace_page'} = 1;
    } else {
        %hash->{'replace_page'} = 0;
    }

    if ( -e $need_reload_tag ) {
        %hash->{'reload'} = 1;
    } else {
        %hash->{'reload'} = 0;
    }

    my $ret = $json->encode(\%hash);
    print $ret;
}

sub get_brute_config_hash($) {
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
    my $web = $temp[0];
    my @login = split('&',$web);
    my $test;
    foreach $login(@login) {
        $config{'loginpage'}.= $login.'&';
    }
    $config{'brute_number'} = $temp[1];
    $config{'rate'} = $temp[2];

    return %config;
}

sub get_headers(){
    my @lines = ();
    &read_config_lines($hidden_header_file,\@lines);
    return @lines;
}
sub get_http_rule(){
    my @lines = ();
    &read_config_lines($http_rule_conf_file,\@lines);
    return @lines;
}

