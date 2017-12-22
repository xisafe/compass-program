#!/usr/bin/perl
#===============================================================================
# header.pl中包含很多通用函数，比如IP地址的检测，和文件的读写。
#一般都会引用，如果不需要，可以删除此行
#author 刘炬隆(liujulong) 2014.4.3
require '/var/efw/header.pl';
#===============================================================================

#=====begin全部变量定义,名字都不用改，可根据实际情况适当添加，初始化全局变量到init_data()中去初始化========================#
my $custom_dir = 'arpman';                              #要保存数据的目录名字 ！！！！要配置，不然路径初始化出问题！！！！            
my $conf_dir = '/var/efw/'.$custom_dir;                    #ARP所存放的文件夹
my $conf_file = '/var/efw/'.$custom_dir.'/config';        #ARP所存放的文件
my $dynomic_file = '/var/efw/'.$custom_dir.'/dynomic';
my $settings_ethernet ="/var/efw/ethernet/settings";
my $vpn_gre_conf = '/var/efw/vpn/greconfig';
my $needreload = '/var/efw/autoarp/needreload';    #需要重新加载的标识文件
my $restart = '/usr/local/bin/arp_table -A';                                        #应用重启的程序,根据实际情况填写
my $extraheader;                                        #存放用户自定义JS
my %par;
my %hash_interface;
my $reload = 0;
my $cmd_generate_dynomic_data = '/usr/local/bin/arp_table -s';
my $cmd_delete_dynomic_data = '/usr/local/bin/arp_table -D';    
my @static_arp;
my @dynomic_arp;
my $state = '静态';                                        #标志是否需要重新加载的标识，不要更改                                                #存放传过来的数据的哈希
my @display_add_config_data;                            #存放<input>信息的哈希
my @table_display_fields;                                #规则列表中要展示的字段的集合
my @table_display_fields_widths;                        #规则列表中要展示的各个字段的宽度的集合
my $CUR_PAGE = "ARP表管理" ;      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

#=========================end全部变量定义==================================================================================#


#==============begin主体,这里的函数一般不需要更改，可根据实际情况添加===========
&make_file();#===第一步检查要存放规则的文件夹和文件是否存在，不存在就创建=======
&init_data();
&getcgihash(\%par);
&showhttpheaders();
&openpage(_('Policy Routing'), 1, $extraheader);
&init_state();
&do_action();
&reload();
&openbigbox($errormessage, $warnmessage, $notemessage);
&display_rules(($par{'ACTION'} eq 'edit'), $par{'line'});
&check_form();
&closebigbox();
&closepage();
#===============end主体=========================================================


#============================================================#
#    配置要保存的字段和其显示的名字及样式以及初始化文件等
#============================================================#
sub init_data(){
    $extraheader =     '<script language="JavaScript" src="/include/arp_checkbox_controller.js"></script>
                    <link rel="stylesheet" type="text/css" href="/include/template_add_list.css" />';#存放用户自定义JS，这里仅仅是个示例,template_add_list.js不要删除
    
    my %hash = (
        "display" => "IP地址*",
        "input_name" => "ip_addr",
        "input_type" => "text",
        "input_class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "MAC地址*",
        "input_name" => "mac_addr",
        "input_type" => "text",
        "input_class" => "",
    );
    push(@display_add_config_data, \%hash);
    
    my %hash = (
        "display" => "接口*",
        "input_name" => "interface",
        "input_type" => "select",
        "input_class" => "",
    );
    push(@display_add_config_data, \%hash);
        
    
    @table_display_fields = ("IP地址", "MAC地址", "接口","类型");        #在规则列表中要显示的列，从@display_add_config_data字段中选取，顺序就是显示的顺序，详细用法在create_table_header()中
    @table_display_fields_widths = ("33%", "33%", "5%","11%");    #在规则列表中要显示的列的宽度，与@table_display_fields中字段一一对应，加起来最好为80%，可适当微调，详细用法在create_table_header()中
    
    
}

sub check_form(){
    #表单检测函数,要检测不同表单，可创建几个名字不同的对象，如object1，object_form等
    printf <<EOF
    <script>        
        var object = {
            'form_name':'TEMPLATE_FORM',//这里填写表单的名字
            'option'   :{
                'ip_addr':{
                    'type':'text',
                    'required':'1',
                    'check':'ip|',
                    'ass_check':function(){//这个eve对象是ChinArk_forms对象，如果需要用到其中的函数，可以填写，不一定用eve这个名字，可以用其他名字
                        
                    }
                },
                'mac_addr':{
                    'type':'text',
                    'required':'1',
                    'check':'mac|',
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
    my $str_add = $$data{'ip_addr'}.$$data{'interface'};
    foreach my $item (@display_add_config_data){
            #检查重名
            my @lines = read_conf_file($conf_file);
            my $total = @lines;
            for(my $i = 0; $i < $total; $i++){
                chomp($lines[$i]);
                my @temp = split(/,/, $lines[$i]);
                my $str_check = $temp[0].$temp[2];
                if($str_check eq $str_add){
                    return(0,"IP地址重复，添加静态ARP失败");
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

sub del_line_check($$){
    my $line = shift;
    my $type = shift;
    my @lines;
    if($type eq 'static'){
        @lines = read_conf_file($conf_file);
    }else{
        @lines = read_conf_file($dynomic_file);
    }    
    if (! @lines[$line]) {
        return ( 0, "不存在要删除的行" );
    }
    my $line_content = @lines[$line];
    #===========在此可以根据行内容判断是否可以删除=========
    my @conf = split(/,/, $line_content);    
    #====end===============================================
    return ( 1, "" );
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
            if((($item->{'input_name'}) eq 'ip_addr')&&($data->{$item->{'input_name'}})){
                $input = '<input type="'.$item->{'input_type'}.'" name="'.$item->{'input_name'}.'" value = "'.$data->{$item->{'input_name'}}.'"/>';
            }else{
                $input = '<input type="'.$item->{'input_type'}.'" name="'.$item->{'input_name'}.'" value = "'.$data->{$item->{'input_name'}}.'"/>';
            }            
        
        }elsif($item->{'input_type'} eq 'select'){
            #my @interfaces = &getinterfaces();
            my @interfaces = get_eth();
            my $green  = `cat /var/efw/ethernet/br0`;
            my $orange = `cat /var/efw/ethernet/br1`;
            my $blue   = `cat /var/efw/ethernet/br2`;
            my @br0s = split(/\n/,$green);
            my @br1s = split(/\n/,$orange);
            my @br2s = split(/\n/,$blue);
            my @ethes_new = ();
            for (my $i=0;$i<@interfaces;$i++){
                foreach(@br0s){
                    if($_ eq $interfaces[$i]){
                        delete ($interfaces[$i]);
                    }
                }
                foreach(@br1s){
                    if($_ eq $interfaces[$i]){
                        delete ($interfaces[$i]);
                    }
                }
                foreach(@br2s){
                    if($_ eq $interfaces[$i]){
                        delete ($interfaces[$i]);
                    }
                }
            }
            if(@br2s > 0){
                unshift(@interfaces,'br2');
            }
            if(@br1s > 0){
                unshift(@interfaces,'br1');
            }
            if($green){
                unshift(@interfaces,'br0');
            }
            
            my @options;
            foreach (@interfaces){
                if($_){
                    push(@options,'<option value="'.$_.'">'.$_.'</option>');
                }
            }
            if($data->{$item->{'input_name'}}){
                $input = '<select name="'.$item->{'input_name'}.'" style="width:135px;">
                <option value="'.$data->{$item->{'input_name'}}.'">'.$data->{$item->{'input_name'}}.'</option>';
            }else{
                $input = '<select name="'.$item->{'input_name'}.'" style="width:135px;">';
            }            
            foreach (@options){
                $input.=$_;
            }
            #my $ele = pop(@options);
            $input.='</select>';
        }
        #===============判断结束======================================================================================###
        my $bgcolor = "odd";
        if($i % 2){
            $bgcolor = "env";
        }
        printf <<EOF
            <tr class="$bgcolor">
                <td class="add-div-type">$item->{'display'}</td>
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
    #  传入ARP字段用','(逗号)隔开
    #  这里根据自定义字段@display_add_config_data配置返回哈希中的值
    #===================notice==============================
    for(my $i = 0; $i < $fields_length; $i++){        
         $config{@display_add_config_data[$i]->{'input_name'}} = @temp[$i];
    }
    #============自定义字段组装完毕=========================
    $config{'valid'} = 1;
    return %config;
}

sub init_state(){
    my @static_lines = read_conf_file($conf_file);
    for(my $i=0;$i<@static_lines;$i++){
        push(@static_arp,$i);
    }
    #my @dynomic_lines = read_conf_file($dynomic_file);
    my @dynomic_lines = split(/\n/,`$cmd_generate_dynomic_data`);
    for(my $i=0;$i<@dynomic_lines;$i++){
        push(@dynomic_arp,$i);
    }
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
            <td class="boldbase" width="3%"><input type="checkbox" id="CHECKALL" onclick="select_all()"/></td>
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
    my @dynomic_lines = split(/\n/,`$cmd_generate_dynomic_data`);
    my $length = @lines;
    my $dylength = @dynomic_lines;
    my $i = 0;
    my $j = 0;
    #my $current_page = 1;
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
            my $check = '<input type="checkbox" name="cbk_static" id="cbk_static'.$i.'" value="'.$i.'" onclick="add_input(this,0)"/>';
            print '<tr class="'.$bgcolor.'"><td>'.$check.'</td>';
            &create_table_body(%conf_data,"static");#打印要显示字段的值
            print '<td>';
            
            #===可根据实际情况添加一些其他操作,或则注释掉一些操作===========
            
                #启用禁用操作，一般都会用上，不用修改，如果不用，可以注释掉
                #&create_enabled_button($conf_data{'start'}, $i);
            
                #编辑操作，一般都会用上，不用修改，如果不用，可以注释掉
                &create_eidt_button( $i);

                #删除操作，一般都会用上，不用修改，如果不用，可以注释掉
                my $flag = "static";
                &create_del_button( $i,$flag);                            
            
            
            #====操作显示结束================================================
                
                    
            print '</td></tr>';
            #==============显示规则一条规则结束===============================================
            $i++;
            #if($i>($current_page*3-1)){
                #last;;
            #}
        }
    }
    $j = $i;
    if($dylength >0){
        foreach my $thisline (@dynomic_lines) {
            chomp($thisline);
            my %conf_data = &config_line($thisline);
            if (! $conf_data{'valid'}) {
                next;
            }
                        
                handle_rulelist_display_data(\%conf_data);#到此函数中去处理显示
            #==============处理结束===========================================================
            #==============显示规则一条规则===================================================
            my $bgcolor = &setbgcolor($is_editing,$line,$j);#行背景计算，不可修改
            my $k = $j-$i;
            my $check = '<input type="checkbox" name="cbk_dynomic" id="cbk_dynomic'.$k.'" value="'.$k.'" onclick="add_input(this)"/>';
            print '<tr class="'.$bgcolor.'"><td>'.$check.'</td>';
            &create_table_body(%conf_data,"dynomic");#打印要显示字段的值
            print '<td>';                            
                #删除操作，一般都会用上，不用修改，如果不用，可以注释掉
            my $flag = "dynomic";
            &create_del_button( $k,$flag);                            
            print '</td></tr>';
            #==============显示规则一条规则结束===============================================
            $j++;
            #if($j>($current_page*3-1)){
                #last;
            #}
        }
    }
    #table结束标志
    print "</table>";
    
    #====显示操作的解释=============
    &create_list_legend($length,$dylength);
    #====解释end====================
    &create_del_options();
}
        
sub create_table_header(){
    my $cols = @table_display_fields;
    for(my $i = 0; $i < $cols; $i++){
        print '<td class="boldbase" width="'.$table_display_fields_widths[$i].'">'.$table_display_fields[$i].'</td>';
    }
}

sub create_table_body(){    
    #my ($test) = @_;
    my %data = @_;
    my $flag = $_[8];
    #print $data{'ip_addr'};
    my $total_fields = @display_add_config_data;
    #将配置数据在页面上显示的中文名和其input的name生成一个哈希
    my @display_cols=qw/ ip_addr mac_addr interface type /;    
    my $cols = @table_display_fields;
    foreach(@display_cols){    
        #my $state = '动态';
        if($flag eq 'dynomic'){
            $state = '动态';            
        }else{
            $state = '静态';            
        }
        if($_ eq 'type'){
            print '<td>'.$state.'</td>';
        }else{
            print '<td>'.$data{$_}.'</td>';
        }
    }
    
}

sub create_enabled_button($$){
    my $enabled = shift;
    my $line = shift;
    my $enabled_gif = $ENABLED_PNG;
    my $enabled_alt = _('Disabled (click to enable)');
    my $enabled_action = 'enable';
    if ($enabled eq 'on') {
        $enabled_gif = $DISABLED_PNG;
        $enabled_alt = _('Enabled (click to disable)');
        $enabled_action = 'disable';
    }
    printf <<EOF
        <FORM METHOD="post" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left">
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
            <input style="margin-left:10px;" class='imagebutton' type='image' name="submit" SRC="$EDIT_PNG" ALT="%s" />
            <input TYPE="hidden" name="ACTION" value="edit">
            <input TYPE="hidden" name="line" value="$line">
        </FORM>
        </FORM>
EOF
    ,_('Edit')
    ;
}

sub create_del_button($$){
    my $line = shift;
    my $flag = shift;
    my $marginLeft;
    if($flag eq 'dynomic'){
        $marginLeft = "style='margin-left:31px;'";
    }
    printf <<EOF
        <FORM METHOD="post" onSubmit="return confirm('确定删除?')" ACTION="$ENV{'SCRIPT_NAME'}">
            <input $marginLeft class='imagebutton' type='image' name="submit" SRC="$DELETE_PNG" ALT="%s"/>
            <input TYPE="hidden" name="ACTION" value="delete">
            <input TYPE="hidden" name="line" value="$line">
            <input TYPE="hidden" name="arp_type" value="$flag">
        </FORM>
EOF
    ,_('Delete')
    ;
}

sub create_list_legend($$){
    my $length = shift;
    my $dylength = shift;
    if($length >0 || $dylength>0)
    {
        printf <<EOF
        <table class="list-legend"  cellpadding="0" cellspacing="0" style="border:0px" >
            <tr>
                <td><b>标签</b><img src="/images/edit.png" alt="编辑">编辑<img src="/images/delete.png" alt="移除">移除<!--
                        <img id="first_page_icon" src="../images/first-page-off.png" title="第一页" onclick="first_page()">
                        <img id="last_page_icon" src="../images/last-page-off.png" title="上一页" onclick="last_page()">
                        <span class="paging-text">第<input id="current-page" type="text" onkeydown="input_control(this, event)">页,共<span id="total-page">xx</span>页</span>
                        <img id="next_page_icon" src="../images/next-page.gif" title="下一页" onclick="next_page()">
                        <img id="end_page_icon" src="../images/end-page.gif" title="最后一页" onclick="end_page()">
                        <img id="refresh_icon" src="../images/refresh.png" onclick="refresh_page()">
                        <span class="paging-text">显示<span id="from-num">xx</span>-<span id="to-num">xx</span>条,共<span id="total-num">xx</span>条</span>
                    </span>-->
                </td>            
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
sub create_del_options(){
    printf <<EOF
    <div align="center" style="background-color:#EBF6FC;text-align:center;height:25px;margin-left:24px;margin-right:25px">        
        <FORM METHOD="post" id="form_checked" onSubmit="return confirm('确定删除?')" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left:350px">
            <input class="net_button" style="padding-left:10px;padding-right:10px;float:left;margin-left:20px" type="submit" value="删除选中"/>
            <input TYPE="hidden" name="ACTION" value="delete_all_checked">
        </FORM>        
        <FORM METHOD="post" onSubmit="return confirm('确定删除?')" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left:20px">
            <input class="net_button" style="padding-left:5px;padding-right:5px" type="submit" value="删除所有静态表选项" />
            <input TYPE="hidden" name="ACTION" value="delete_all_static">
        </FORM>
        <FORM METHOD="post" onSubmit="return confirm('确定删除?')" ACTION="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left:20px">
            <input class="net_button" style="padding-left:5px;padding-right:5px" type="submit" value="删除所有动态表选项" />
            <input TYPE="hidden" name="ACTION" value="delete_all_dynomic">
        </FORM>        
    </div>
EOF
    ;
}
sub display_add($$) {
    my $is_editing = shift;
    my $line = shift;    
    my %config;
    
    if (($is_editing == 1) && ($par{'sure'} ne 'y')) {
        %config = &config_line(read_conf_line($conf_file, $line));
    }
    else {
        %config = %par;
    }
    
    #===判断是编辑还是添加，以显示不同的文字，此段不能删除=====
    my $action = 'add';
    my $sure = '';
    my $show = '';
    my $addoredit = "添加静态ARP";#可根据实际情况修改名字
    $button = _("建立条目");#可根据实际情况修改名字
    my $title = _('Static ARP rule editor');
    
    if ($is_editing) {
        $action = 'edit';
        $sure = '<input TYPE="hidden" name="sure" value="y">';
        $button = _("编辑静态ARP");#可根据实际情况修改名字
        $show = "showeditor";
        $addoredit = "编辑静态ARP";#可根据实际情况修改名字
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
        $notemessage = "ARP应用成功";#此行消息可以自定义
        &write_log($CUR_PAGE,"apply",0,$rule_or_congfig);
        return;
    }   
    #==删除，基本不需要修改===========
    if ($action eq 'delete') {
        my $arp_type = $par{'arp_type'};
        my ($if_can, $errormsg);
        if($arp_type eq 'static'){
            ($if_can, $errormsg) = &del_line_check($par{'line'},$arp_type);
            if($if_can){
                &delete_line($par{'line'},$arp_type);
                $reload = 1;
            }else{
                $errormessage = $errormsg;
            }
        }else{
            &delete_line($par{'line'},$arp_type);
        }
        &reset_values();
        return;
    }
    #删除指定项
    if($action eq 'delete_all_static'){
        my $flag = 'static';
        &delete_lines($flag);
        &reset_values();
        $reload = 1;
        return;
    }
    
    if($action eq 'delete_all_dynomic'){        
        my $flag = 'dynomic';
        &delete_lines($flag);
        &reset_values();
        return;
    }
    
    if($action eq 'delete_all_checked'){        
        my $flag = 'checked';
        &delete_lines($flag);
        &reset_values();
        $reload = 1;
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
        my ($if_can, $errormsg);
        if($action eq 'add'){
            ($if_can, $errormsg) = &handle_submit_save_data(\%par);
        }else{
            ($if_can, $errormsg) = (1,"");
        }
        #==第二步保存==========================
        if($if_can){
            &save_conf_line($par{'line'},&get_conf_line(\%par));
        }else{
            $errormessage = $errormsg;
        }        
        &reset_values();
        &write_log($CUR_PAGE,"edit",0,$rule_or_congfig);
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
    my @temp_content = split(",",$line_content);
    $temp_content[1] = lc($temp_content[1]);
    my $line_content_new = join(",",@temp_content);
    my @lines = read_conf_file($conf_file);
    if($line eq ''){
        #新添加一行
        push(@lines, $line_content_new);
    }else{
        if (! @lines[$line]) {
            return;
        }
        #编辑修改
        @lines[$line] = $line_content_new;
    }
    &save_conf_file(\@lines, $conf_file);
    $reload = 1;#如果不需要重新应用可以删除此行
}

sub delete_line($$) {
    my $line = shift;
    my $type = shift;
    my $ip_dynomic;
    my @lines;
    if($type eq 'static'){
        @lines = read_conf_file($conf_file);
    }else{
        @lines = split(/\n/,`$cmd_generate_dynomic_data`);
        $ip_dynomic = (split(",",$lines[$line]))[0];
    }   
    if (! @lines[$line]) {
        return;
    }
    delete (@lines[$line]);
    if($type eq 'static'){
        &save_conf_file(\@lines, $conf_file);
    }else{
        #&save_conf_file(\@lines, $dynomic_file);
        system($cmd_delete_dynomic_data.' '.$ip_dynomic);
    }   
}

sub delete_lines($) {
    my $f=shift;
    my @del_lines;
    if($f eq 'dynomic'){
        @del_lines=@dynomic_arp;
        my $ips_delete_dynomic;
        my @lines = split(/\n/,`$cmd_generate_dynomic_data`);
        foreach (@del_lines){
            if(! @lines[$_]){
                return;
            }
            #delete (@lines[$_]);
            $ips_delete_dynomic .= ' '.(split(",",@lines[$_]))[0];
        }        
        #&save_conf_file(\@lines, $dynomic_file);
        system($cmd_delete_dynomic_data.$ips_delete_dynomic);
    }elsif($f eq 'static'){
        @del_lines=@static_arp;
        my @lines = read_conf_file($conf_file);
        foreach (@del_lines){
            if(! @lines[$_]){
                return;
            }
            delete (@lines[$_]);
        }        
        &save_conf_file(\@lines, $conf_file);
    }elsif($f eq 'checked'){
        @static_arp = split(/[|]/,$par{'arp_static'});
        my @lines_static = read_conf_file($conf_file);
        if(@static_arp){
            foreach (@static_arp){
                if(! @lines_static[$_]){
                    return;
                }
                delete (@lines_static[$_]);
            }        
            &save_conf_file(\@lines_static, $conf_file);
        }
        
        @dynomic_arp = split(/[|]/,$par{'arp_dynomic'});
        my @lines_dynomic = split(/\n/,`$cmd_generate_dynomic_data`);
        my $ips_delete_dynomic;
        if(@dynomic_arp){
            foreach (@dynomic_arp){
                if(! @lines_dynomic[$_]){
                    return;
                }
                #delete (@lines_dynomic[$_]);
                $ips_delete_dynomic .= ' '.(split(",",@lines_dynomic[$_]))[0];
            }        
            #&save_conf_file(\@lines_dynomic, $dynomic_file);
            system($cmd_delete_dynomic_data.$ips_delete_dynomic);
        }
    }        
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
    $data{'start'} = $enable;
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

sub read_conf_line(){
    my $file_name = shift;
    my $line_num = shift;
    my @lines = read_conf_file($file_name);
    return $lines[$line_num]
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
    
    if(! -e $dynomic_file){
        `touch $dynomic_file`;
    }
}
sub reload(){
    if ($reload) {
        system("touch $needreload");
    }
    if (-e $needreload) {
        applybox(_("ARP表项已更新，需点击应用以更新规则"));
    }
}

#获取所有接口
sub getinterfaces(){
    my @all_hash;
    my $temp_cmd = `ip a`;
    my @temp = split(/\n/,$temp_cmd);
    foreach my $line(@temp)
    {
        if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
        {
            $eth = $1;
            push(@all_hash,$eth);
        }
    }
    return @all_hash;
}