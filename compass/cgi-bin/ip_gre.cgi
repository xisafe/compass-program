#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 	一个添加模块和规则列表模块页面的模板
#				以后写类此的页面可以直接先copy，再做具体编辑
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2013/12/04-13:00
#===============================================================================

#===============================================================================
# header.pl中包含很多通用函数，比如IP地址的检测，和文件的读写。
#一般都会引用，如果不需要，可以删除此行
require '/var/efw/header.pl';
#===============================================================================

#=====begin全部变量定义,名字都不用改，可根据实际情况适当添加，初始化全局变量到init_data()中去初始化========================#
my $custom_dir = 'gre'; 								#要保存数据的目录名字 ！！！！要配置，不然路径初始化出问题！！！！			
my $conf_dir = '/var/efw/'.$custom_dir;					#规则所存放的文件夹
my $conf_file = '/var/efw/'.$custom_dir.'/config';		#规则所存放的文件
my $vpn_gre_conf = '/var/efw/vpn/greconfig';
my $needreload = '/var/efw/'.$custom_dir.'/needreload';	#需要重新加载的标识文件
my $restart = '';										#应用重启的程序,根据实际情况填写
my $extraheader;										#存放用户自定义JS
my %par;												#存放传过来的数据的哈希
my $reload = 0;											#标志是否需要重新加载的标识，不要更改
my @display_add_config_data;							#存放<input>信息的哈希
my @table_display_fields;								#规则列表中要展示的字段的集合
my @table_display_fields_widths;						#规则列表中要展示的各个字段的宽度的集合
my $CUR_PAGE = "GRE配置" ;      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

#=========================end全部变量定义==================================================================================#


#==============begin主体,这里的函数一般不需要更改，可根据实际情况添加===========
&make_file();#===第一步检查要存放规则的文件夹和文件是否存在，不存在就创建=======
&init_data();
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('Policy Routing'), 1, $extraheader);
&do_action();
&reload();
&openbigbox($errormessage, $warnmessage, $notemessage);
&display_rules(($par{'ACTION'} eq 'edit'), $par{'line'});
&check_form();
&closebigbox();
&closepage();
#===============end主体=========================================================


#============================================================#
#	配置要保存的字段和其显示的名字及样式以及初始化文件等
#============================================================#
sub init_data(){
	$extraheader = 	'<script language="JavaScript" src="/include/template_add_list.js"></script>';#存放用户自定义JS，这里仅仅是个示例,template_add_list.js不要删除
	$restart = '';
	
	my %hash = (
		"display" => "名称",
		"input_name" => "name",
		"input_type" => "text",
		"input_class" => "",
	);
	push(@display_add_config_data, \%hash);
	
	my %hash = (
		"display" => "本地地址",
		"input_name" => "local_addr",
		"input_type" => "text",
		"input_class" => "",
	);
	push(@display_add_config_data, \%hash);
	
	my %hash = (
		"display" => "远程地址",
		"input_name" => "remote_addr",
		"input_type" => "text",
		"input_class" => "",
	);
	push(@display_add_config_data, \%hash);
	
	@table_display_fields = ("名称", "本地地址", "远程地址");		#在规则列表中要显示的列，从@display_add_config_data字段中选取，顺序就是显示的顺序，详细用法在create_table_header()中
	@table_display_fields_widths = ("20%", "30%", "30%");	#在规则列表中要显示的列的宽度，与@table_display_fields中字段一一对应，加起来最好为80%，可适当微调，详细用法在create_table_header()中
}

sub check_form(){
	#表单检测函数,要检测不同表单，可创建几个名字不同的对象，如object1，object_form等
    printf <<EOF
	<script>
		var object = {
			'form_name':'TEMPLATE_FORM',//这里填写表单的名字
			'option'   :{
				'name':{
					'type':'text',
					'required':'1',
					'check':'name|',
					'ass_check':function(eve){//这个eve对象是ChinArk_forms对象，如果需要用到其中的函数，可以填写，不一定用eve这个名字，可以用其他名字
						var msg = "";
						//此处添加你自己的代码,如果要返回错误消息，就填在msg中，如果没有错误，将msg置空就OK了
						var name = eve._getCURElementsByName("name","input","TEMPLATE_FORM")[0].value;
						var line = eve._getCURElementsByName("line","input","TEMPLATE_FORM")[0].value;
						var pattern = /^gre(\\d)+\$/;
						if(!pattern.test(name)){
							msg = "名称以gre开头，1-1024数字结尾";
						}else{
							var pattern_d = /(\\d)+/g;
							var result = name.match(pattern_d);
							if(result < 1 || result > 1024){
								msg = "名称以gre开头，1-1024数字结尾";
							}
						}
						if(!eve.gres){
							\$.ajax({
								  type : "get",
								  url : '/cgi-bin/chinark_back_get.cgi',
								  async : false,
								  data : 'path=/var/efw/gre/config',
								  success : function(data){ 
									eve.gres = data;                                                                     
								  }
							});
						}
						var exist = eve.gres.split('\\n');
						for (var i = 0; i < exist.length; i++) {
							var tmp = exist[i].split(',');
							if(name == "gre" + tmp[0] ){
								if(line == ""){
									msg = '名称'+name+'已存在';
									break;
								}else if(i != line){
									msg = '名称'+name+'已存在';
									break;
								}
							}
						}
						
						return msg;
					}
				},
				'local_addr':{
					'type':'text',
					'required':'1',
					'check':'ip|',
					'ass_check':function(){
				   
					}
				},
				'remote_addr':{
					'type':'text',
					'required':'1',
					'check':'ip|',
					'ass_check':function(){
						
					}
				}
            }
        }
		var check = new ChinArk_forms();
		check._main(object);
		//打开此函数可以生成上面的表单检测的对象
		//check._get_form_obj_table("TEMPLATE_FORM");
	</script>
EOF
	;
}

sub handle_submit_save_data($){
	#======在此函数中对提交上来的%par中的变量进行处理=====
	my ($data) = @_;
	foreach my $item (@display_add_config_data){
		if($item->{'input_name'} eq 'name'){
			$data->{$item->{'input_name'}} =~ s/gre//g;
			#检查重名
			my @lines = read_conf_file($conf_file);
			my $total = @lines;
			for(my $i = 0; $i < $total; $i++){
				chomp($lines[$i]);
				my @temp = split(/,/, $lines[$i]);
				if($data->{$item->{'input_name'}} == $temp[0]){
					#有二种情况要判断，一是$data->{'line'}是否为空，二是$data->{'line'}是否等于现在的$i
					if($data->{'line'} eq ''){
						return(0, "gre".$temp[0]."已存在");
					}else{
						if($data->{'line'} != $i){
							return(0, "gre".$temp[0]."已存在");
						}else{
							#如果等于现在的$i,要先判断此接口是否在使用，如果是，则不能编辑
							my $gre_name = $temp[0];
							my ($used, $use_con) = &is_gre_used($gre_name);
							if($used){
								return ( 0, "gre".$gre_name."正在被VPN中".$use_con."使用，不能编辑");
							}
						}
					}
				}
			}
		}
	}
	return(1, "");
}

sub handle_rulelist_display_data($){
	#======在此函数中对要显示的数据进行处理===============
	#!!在config_line中对取出来的数据做了处理同样影响显示!!
	my ($data) = @_;
	#进行处理
	foreach my $item (@display_add_config_data){
		if($item->{'input_name'} eq 'name'){
			#$data->{$item->{'input_name'}} = "gre".$data->{$item->{'input_name'}};已在config_line中更改
		}
	}
	#处理结束
	return;
}

sub del_line_check($){
	my $line = shift;
    my @lines = read_conf_file($conf_file);
    if (! @lines[$line]) {
        return ( 0, "不存在要删除的行" );
    }
    my $line_content = @lines[$line];
	#===========在此可以根据行内容判断是否可以删除=========
	my @conf = split(/,/, $line_content);
	my $gre_name = $conf[0];
	#$gre_name =~ s/gre//g;#只留下数字
	my ($used, $use_con) = &is_gre_used($gre_name);
	if($used){
		return ( 0, "gre".$gre_name."正在被VPN中".$use_con."使用，不能删除");
	}
	#====end===============================================
	return ( 1, "" );
}

sub is_gre_used($){
	my $gre_name = shift;
	my @vpn_gre_lines = read_conf_file($vpn_gre_conf);#读取当前正在使用的gre接口
	my $used = 0;#标识当前gre接口是否被使用
	my $use_con = '';
	foreach my $vpn_gre_conf (@vpn_gre_lines){
		chomp($vpn_gre_conf);
		my @temp = split(/,/, $vpn_gre_conf);
		if($temp[1] == $gre_name){
			$used = 1;
			$use_con = $temp[2];
			last;
		}
	}
	return ($used, $use_con);
}

sub create_display_add_lines($){
	my ($data) = @_;
	my $total_count = @display_add_config_data;
	#my $total_count = 2;
	for(my $i = 0; $i < $total_count; $i++){
		my $item = @display_add_config_data[$i];
		#======先判断input是什么类型的，再创建相应的input,根据实际情况，这里的判断语句还要增加=========================###
		my $input;
		if($item->{'input_type'} eq 'text'){
			$input = '<input type="'.$item->{'input_type'}.'" name="'.$item->{'input_name'}.'" value = "'.$data->{$item->{'input_name'}}.'"/>';
		}elsif($item->{'input_type'} eq 'checkbox'){
			my $enabled_checked = "checked";
			if($data->{$item->{'input_name'}} ne 'on'){
				$enabled_checked = "";
			}
			$input = '<input type="'.$item->{'input_type'}.'" name="'.$item->{'input_name'}.'"'.$enabled_checked.'/>';
		}else{
			$input = '<input type="'.$item->{'input_type'}.'" name="'.$item->{'input_name'}.'"/>';
		}
		#===============判断结束======================================================================================###
		my $bgcolor = "odd";
		if($i % 2){
			$bgcolor = "env";
		}
		printf <<EOF
			<tr class="$bgcolor">
				<td class="add-div-type">$item->{'display'}*</td>
				<td>
					$input
				</td>
			</tr>
EOF
		;
	}
}

sub config_line($) {
    my $line = shift;
	chomp($line);
    my %config;
    $config{'valid'} = 0;
    if ($line eq '') {
        return ;
    }
    my @temp = split(/,/, $line);
	my $fields_length =  @display_add_config_data;
	#===================notice==============================
	#  传入规则字段用','(逗号)隔开
	#  这里根据自定义字段@display_add_config_data配置返回哈希中的值
	#===================notice==============================
	for(my $i = 0; $i < $fields_length; $i++){
		if($i == 0){
			$config{@display_add_config_data[$i]->{'input_name'}} = "gre".@temp[$i];
			next;
		}
		 $config{@display_add_config_data[$i]->{'input_name'}} = @temp[$i];
	}
	#============自定义字段组装完毕=========================
    $config{'valid'} = 1;
    return %config;
}

sub display_rules($$) {
    my $is_editing = shift;
    my $line = shift;
    
	#添加和编辑模块
    &display_add($is_editing, $line);
	
    printf <<EOF
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr>
			<!-- 此行是表头，要创建几列看具体创建的内容-->
            <td class="boldbase" width="5%">序号</td><!--此行不建议更改-->
EOF
;
			#==========生成规则列表的表头配置参数见本文档开头部分=====
            &create_table_header();
			#==========end============================================
	printf <<EOF
            <td class="boldbase" width="15%">活动/动作</td><!--此行不建议更改，宽度可以适当调整-->
        </tr>
EOF
    ;

	#读取规则文件，这里的规则文件的规则是一行一个规则，规则中的每一项用','(逗号)隔开
    my @lines = read_conf_file($conf_file);
	my $length = @lines;
    my $i = 0;
	if($length >0)
	{
		foreach my $thisline (@lines) {
			chomp($thisline);
			my %conf_data = &config_line($thisline);
			if (! $conf_data{'valid'}) {
				next;
			}
			
			#==============读取规则中的每个字段，做相应的显示处理=============================
				#此处根据用户自定义处理
				handle_rulelist_display_data(\%conf_data);#到此函数中去处理显示
			#==============处理结束===========================================================
							
			
			#==============显示规则一条规则===================================================
			my $bgcolor = &setbgcolor($is_editing,$line,$i);#行背景计算，不可修改
			my $num = $i + 1;#行号
			print '<tr class="'.$bgcolor.'"><td>'.$num.'</td>';
			&create_table_body(\%conf_data);#打印要显示字段的值			
			print '<td>';
			
			#===可根据实际情况添加一些其他操作,或则注释掉一些操作===========

			#启用禁用操作，一般都会用上，不用修改，如果不用，可以注释掉
			#&create_enabled_button($conf_data{'enabled'}, $i);
			
			#编辑操作，一般都会用上，不用修改，如果不用，可以注释掉
			&create_eidt_button( $i);

			#删除操作，一般都会用上，不用修改，如果不用，可以注释掉
			&create_del_button( $i);
			
			#====操作显示结束================================================
				
					
			print '</td></tr>';
			#==============显示规则一条规则结束===============================================
			$i++;
		}
    }else{
		#===无内容的时候显示,这里的数字为自己创建table的列数=====
		no_tr(6,_('Current no content'));
	}
	#table结束标志
	print "</table>";
	
	#====显示操作的解释=============
	&create_list_legend($length);
	#====解释end====================
}

sub create_table_header(){
	my $cols = @table_display_fields;
	for(my $i = 0; $i < $cols; $i++){
		print '<td class="boldbase" width="'.$table_display_fields_widths[$i].'">'.$table_display_fields[$i].'</td>';
	}
}

sub create_table_body(){
	my ($data) = @_;
	my $total_fields = @display_add_config_data;
	#将配置数据在页面上显示的中文名和其input的name生成一个哈希
	my %display_config_data_hash;
	for(my $i = 0; $i < $total_fields; $i++){
		my $item = @display_add_config_data[$i];
		%display_config_data_hash->{$item->{'display'}} = $item->{'input_name'};
	}
	my $cols = @table_display_fields;
	for(my $i = 0; $i < $cols; $i++){
		#取出想显示字段的值打印
		my $display_data = $data->{$display_config_data_hash{$table_display_fields[$i]}};
		print '<td>'.$display_data.'</td>';
	}
}

sub create_enabled_button($$){
	my $enabled = shift;
	my $line = shift;
	my $enabled_gif = $DISABLED_PNG;
	my $enabled_alt = _('Disabled (click to enable)');
	my $enabled_action = 'enable';
	if ($enabled eq 'on') {
		$enabled_gif = $ENABLED_PNG;
		$enabled_alt = _('Enabled (click to disable)');
		$enabled_action = 'disable';
	}
	printf <<EOF
		<FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left;display:inline-block">
			<input class='imagebutton' type='image' name="submit" SRC="$enabled_gif" ALT="$enabled_alt" />
			<input TYPE="hidden" name="ACTION" value="$enabled_action">
			<input TYPE="hidden" name="line" value="$line">
		</FORM>
EOF
	;	
}

sub create_eidt_button($){
	my $line = shift;
	printf <<EOF
		<FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}">
			<input class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s" />
			<input TYPE="hidden" name="ACTION" value="edit">
			<input TYPE="hidden" name="line" value="$line">
		</FORM>
		</FORM>
EOF
	,_('Edit')
	;
}

sub create_del_button($){
	my $line = shift;
	printf <<EOF
		<FORM METHOD="post" onSubmit="return confirm('确定删除?')" ACTION="$ENV{'SCRIPT_NAME'}">
			<input class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s"/>
			<input TYPE="hidden" name="ACTION" value="delete">
			<input TYPE="hidden" name="line" value="$line">
		</FORM>
EOF
	,_('Delete')
	;
}

sub create_list_legend($){
	my $length = shift;
	if($length >0)
	{
		printf <<EOF
		<table class="list-legend"  cellpadding="0" cellspacing="0" >
			<tr>
				<td ><B>%s</B><IMG SRC="$ENABLED_PNG" ALT="%s" />%s<IMG SRC='$DISABLED_PNG' ALT="%s" />%s<IMG SRC="$EDIT_PNG" alt="%s" />%s<IMG SRC="$DELETE_PNG" ALT="%s" />%s</td>
			</tr>
		</table>
EOF
		,
		_('Legend'),
		_('Enabled (click to disable)'),
		_('Enabled (click to disable)'),
		_('Disabled (click to enable)'),
		_('Disabled (click to enable)'),
		_('Edit'),
		_('Edit'),
		_('Remove'),
		_('Remove')
		;   
	}
}

sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;
    my %config;
        
    if (($is_editing) && ($par{'sure'} ne 'y')) {
        %config = &config_line(read_conf_line($conf_file, $line));
    }
    else {
        %config = %par;
    }
	
	#===判断是编辑还是添加，以显示不同的文字，此段不能删除=====
    my $action = 'add';
    my $sure = '';
	my $addoredit = "添加规则";#可根据实际情况修改名字
    $button = _("Create Rule");#可根据实际情况修改名字
    my $title = _('Policy routing rule editor');
    
    if ($is_editing) {
        $action = 'edit';
        $sure = '<input TYPE="hidden" name="sure" value="y">';
        $button = _("编辑规则");#可根据实际情况修改名字
        $show = "showeditor";
		$addoredit = "编辑规则";#可根据实际情况修改名字
    } elsif(@errormessages > 0) {
        $show = "showeditor";
    }else{
		$show = "";
	}
	#===判断结束==============================================
	
    openeditorbox($addoredit, $title, $show, "createrule", @errormessages);
    printf <<EOF
		</form><!--上一个form中name没有定义，无法进行特殊的表单检测，此处是为了关闭上一个form,请勿删除，否则表单检测会出问题-->
		<form name="TEMPLATE_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
		<!--此处form的name可以更改，以适应自己check_form函数中的表单检测-->
			<table width="100%" cellpadding="0" cellspacing="0">
EOF
	;
				#======begin 在此之间加入自己的行=====
				&create_display_add_lines(\%config);
				#======end 行添加完毕================
	printf <<EOF
			</table>
		<input type="hidden" name="ACTION" value="$action">
		<input type="hidden" name="line" value="$line">
		<input type="hidden" name="sure" value="y">
EOF
		;
    &closeeditorbox($button, _("Cancel"), "routebutton", "createrule", "$ENV{SCRIPT_NAME}");
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $sure = $par{'sure'};
	
    if ($action eq 'apply') {			
		`$restart`;#重启服务
		`rm $needreload`;
        $notemessage = "规则应用成功";#此行消息可以自定义
		&write_log($CUR_PAGE,'apply',0,$rule_or_congfig);
        return;
    }
	#==删除，基本不需要修改===========
    if ($action eq 'delete') {
		my ($if_can, $errormsg) = &del_line_check($par{'line'});
		if($if_can){
			&delete_line($par{'line'});
		}else{
			$errormessage = $errormsg;
		}
		&reset_values();
		return;
    }

    if ($action eq 'enable') {
        if (&toggle_enable($par{'line'}, 1)) {
            &reset_values();
            return;
        }
    }
    if ($action eq 'disable') {
        if (&toggle_enable($par{'line'}, 0)) {
            &reset_values();
            return;
        }
    }

    if (($action eq 'add') ||(($action eq 'edit')&&($sure eq 'y'))) {
		#==第一步先对%par中的值进行处理====
		my ($if_can, $errormsg) = &handle_submit_save_data(\%par);
		#==第二步保存==========================
		if($if_can){
			&save_conf_line($par{'line'},&get_conf_line(\%par));
		}else{
			$errormessage = $errormsg;
		}		
        &reset_values();
        &write_log($CUR_PAGE,'edit',0,$rule_or_congfig);
        return;
	}
}

sub save_conf_file($$) {
    my $ref = shift;
	my $filename= shift;
    my @lines = @$ref;
    open (FILE, ">$filename");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
}

sub save_conf_line($$) {
    my $line = shift;
    my $line_content = shift;
    my @lines = read_conf_file($conf_file);
	if($line eq ''){
		#新添加一行
		push(@lines, $line_content);
	}else{
		if (! @lines[$line]) {
			return;
		}
		#编辑修改
		@lines[$line] = $line_content;
	}
    &save_conf_file(\@lines, $conf_file);
	$reload = 1;#如果不需要重新应用可以删除此行
}

sub delete_line($) {
    my $line = shift;
    my @lines = read_conf_file($conf_file);
    if (! @lines[$line]) {
        return;
    }
    delete (@lines[$line]);
    &save_conf_file(\@lines, $conf_file);
}


sub toggle_enable($$) {
    my $line = shift;
    my $enable = shift;
    if ($enable) {
        $enable = 'on';
    } 
    else {
        $enable = '';
    }

    my %data = &config_line(read_conf_line($conf_file, $line));
    $data{'enabled'} = $enable;
	my $line_content = &get_conf_line(\%data);

    save_conf_line($line,$line_content);
}

sub get_conf_line($){
	my ($data, $params) = @_;
	my @data_arr;
	foreach my $item (@display_add_config_data){
		push(@data_arr, $data->{$item->{'input_name'}})
	}
	return join ",", @data_arr;
}

sub reset_values() {
    %par = ();
}

sub make_file(){
	if(! -e $conf_dir){
		`mkdir -p $conf_dir`;
	}
	
	if(! -e $conf_file){
		`touch $conf_file`;
	}
}

sub reload(){
	if ($reload) {
		system("touch $needreload");
	}
	if (-e $needreload) {
		applybox(_("规则已改变，需应用该规则以使改变生效"));
	}
}