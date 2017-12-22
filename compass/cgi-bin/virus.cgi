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

my $CUR_PAGE = "病毒查杀" ;      #当前页面名称，用于记录日志
my $log_oper ;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_congfig = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置
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
    $custom_dir         = '/virus';
    $conf_dir           = "${swroot}".$custom_dir;
    $conf_file          = $conf_dir.'/conf';
    $virusrules_file   = $conf_dir.'/virusrules';
    $need_reload_tag    = $conf_dir.'/add_list_need_reload';    

    $read_conf_dir      ="/var/efw/objects";                        #读取数据的目录文件夹     
    $file_type_file     =$read_conf_dir.'/file_type/fileconfig';        #读取文件类型文件
    $cmd_file_type      = "sudo /usr/local/bin/getfiletypejson.py";
    $cmd_set_virus      = "/usr/local/bin/setvirus.py";
    $cmd_set_virusIsactive = "/usr/local/bin/virusIsactive";
    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/jsTree.css" />
                    <link rel="stylesheet" type="text/css" href="/include/virus.css" />
                    <script language="JavaScript" src="/include/jquery-3.1.0.min.js"></script>
                    <script language="JavaScript" src="/include/jstree.min.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/virus.js"></script>
                    <script language="JavaScript" src="/include/add_panel_include_config.js"></script>';
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
    elsif( $action eq 'read_data') {
        &read_data();
    }

    elsif( $action eq 'apply_data' ) {
        &apply_data();
    }
    else {
        &show_page();
    }

    if ($action eq 'apply_data' || $action eq 'save_data') {
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
    $result =`sudo $cmd_set_virusIsactive`;
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
EOF
    ;
    &openbox('96%', 'left', '病毒查杀配置');
    &displayWebBody(\%data);
    &closebox();

}
sub displayWebBody() {
      my $formdata = shift;
    # print Dumper(\%$formdata);
        # return;
      my $http_str="";
      my $smtp_str="";
      my $pop_str="";
      my $ftp_str="";

      my $pro = %$formdata->{'proto'};
      my @protocol = split(/\&/,$pro);
      # system("echo '$pro'>>/tmp/test.log");
      foreach my $proto (@protocol)
      {
        if($proto eq "http")
            {  
                $http_str="checked";
            }
         if($proto eq "smtp")
         {
            $smtp_str="checked";
         }
         if($proto eq "pop")
         {
            $pop_str="checked";
         }  
         if($proto eq "ftp")
         {
            $ftp_str="checked";
         }  
      }
      my $actionlog="";
      my $actiondrop="";
      my $action = %$formdata->{'clamav_action'};
      my @act = split(/\&/,$action);
      
        foreach my $action_ (@act)
      {
        if($action_ eq "alert")
            {  
            $actionlog="checked";
            }
         if($action_ eq "drop")
         {
            $actiondrop="checked";
         }
         
      }
    my $tree = %$formdata->{'filetypes'};
    # handle value in config
    my $enable = %$formdata->{'enable_clamav'};
    my $able="";
    if($enable eq "1")
    {
        $able="checked";
    }
    else{
        $able="unchecked";
        $enable = 0;
    }
    
    #handle mod status
    my $enableordis="";
    my $title="";
    my $dest=ModIsOK();
    system("echo '$dest'>>/tmp/mmtest.log");
    if($dest eq "0"){
    	$able = '';     
        $enableordis="disabled";
        $title="病毒查杀功能模块未激活，暂无法启用";
        
      }else{
    	$enableordis="";
        $title="";
    }


     printf<<EOF
    <form name = "virus-form" action='$ENV{SCRIPT_NAME}' method="post">
        <table width="100%" cellpadding="0" cellspacing="0">
                <tr class ='odd'>
                    <td class='add-div-type'>启用</td>
                    <td>
  
               <input type="checkbox" name="enable_clamav" value="$enable" $enableordis $able>
               <span><font color="red">&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp $title</font></span>
                    </td>
                </tr>
              <!--   <tr class ='odd'>
                    <td class='add-div-type'>描述</td>
                    <td><span><input type="text" style='width:196px' id="description" name="description" value=$formdata->{'description'}> </span>    
                    </td>
                </tr>  -->              
                <tr class ='odd'>
                    <td class='add-div-type'>扫描文件大小 *</td>
                    <td>
                        <div>
                         最小： 
                         <span><input type="text" id="depth_min" name="depth_min" value=$formdata->{'depth_min'}>&nbsp&nbspKB </span>
                         </div>
             
                   
                    <div>
                         最大：
                         <span><input type="text" id="depth_max" name="depth_max" value=$formdata->{'depth_max'}>&nbsp&nbspKB </span>  
                    </div>                  
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>扫描协议 *</td>
                    <td>
                        <input type="checkbox" id="proto" name="proto" value="http" $http_str>HTTP&nbsp&nbsp&nbsp
                        <input type="checkbox" id="proto" name="proto" value="smtp" $smtp_str> SMTP&nbsp&nbsp&nbsp
                        <input type="checkbox" id="proto" name="proto" value="pop" $pop_str>POP&nbsp&nbsp&nbsp
                        <input type="checkbox" id="proto" name="proto" value="ftp" $ftp_str> FTP  
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>文件类型杀毒 *</td>
                    <td>
                        <input type="text" name="filetypes" value="$tree" readonly="readonly" title="$tree" id="setvirus-filetype" style="width:195px">&nbsp&nbsp&nbsp
                        <input type="button" name="killvirusbtn" value="配置" onclick="show_lib_panel();" style="">
                    </td>
                </tr>
                <tr class ='odd'>
                    <td class='add-div-type'>检测攻击后操作</td>
                    <td>
                        <input type="checkbox" name="clamav_action" value="alert" $actionlog>记录日志
                        <input type="checkbox" name="clamav_action" value="drop" $actiondrop>阻断
                    </td>
                </tr>
                <tr class="table-footer"> 
                    <td colspan="2">
                        <input type="submit" class="net_button" id="webdefend-save" value="完成"/>
                        <input type="hidden" name="ACTION" value="save_data">
                    </td>
                </tr>

        </table>
        </form>
EOF
    ; 
 
}



sub loadFormData() {
    my @lines;
    my %formdata;
   
    my %data;
    &read_config_lines( $conf_file, \@lines);
    #&read_config_lines($ip_groups_file ,\@lines_ipgroups);

    %formdata = &get_config_hash($lines[0]);

    # $formdata{'clamav_action'} = view_assembling($formdata{'clamav_action'});
    
    
    # $data{'formdata'} = \%formdata;
    return %formdata;

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
    $config{'enable_clamav'} = $temp[0];
    $config{'depth_min'}     = $temp[1];
    $config{'depth_max'}     = $temp[2];
    $config{'clamav_action'} = $temp[3];
    $config{'proto'}         = $temp[4];
    $config{'filetypes'}     = &datas_hander( $temp[5],'load');
    $config{'description'}   = $temp[6];
    #============自定义字段组装-END===========================#
    return %config;
}

sub get_config_record($) {
    my $hash_ref = shift;
    my @record_items = ();
 
    my $dest=ModIsOK();

    my $enable_status = $hash_ref->{'enable_clamav'};
    # system("echo $enable_status >> /tmp/pt.log");
    if($enable_status eq '' ){   
            $enable_status = "0";
        }
    else{
            if ($dest eq "0"){
                $enable_status = "0";
            }
            else{
                $enable_status = "1";
            }
        }
    push( @record_items, $enable_status);
    
    push( @record_items, $hash_ref->{'depth_min'} );
    push( @record_items, $hash_ref->{'depth_max'} );
    #push( @record_items, $hash_ref->{'clamav_action'} );

     my $action = $hash_ref->{'clamav_action'};
     if($action eq ""){
        $action=none;
     }
     $action =~ s/\|/&/g;
     push( @record_items, $action);

    # my $action = $hash_ref->{'clamav_action'};
    # $action = ~ s/|/&/g;
    # push( @record_items, $action);
    #push( @record_items, $hash_ref->{'proto'} );
    
    # my @pro = split("\|",$hash_ref->{'proto'});
    # my $mypro = join ("\&",@pro);
    # push( @record_items, $mypro);
         
    my $pro = $hash_ref->{'proto'};
    #system("echo '$hash_ref->{'proto'}' >> /tmp/test.log");
    $pro =~ s/\|/&/g;
    push( @record_items, $pro);
    #    my @proto = split("\|",$pro);
    #   my $mypro = join ("&",@proto);
    

    push( @record_items, &datas_hander($hash_ref->{'filetypes'},'save') );
    push( @record_items, $hash_ref->{'description'} );
    
    return join ",", @record_items;
}

sub get_compare_record($) {
    my $hash_ref = shift;
    my @record_items = ();
    #============自定义比较字段-BEGIN=========================#
    #一般来说比较的字段和保存的字段几乎都一致，但是存在保存时，
    #要更新修改时间等就不一样了，需要自己定义比较哪些字段=====#
    push( @record_items, $hash_ref->{'enable_clamav'} );
    push( @record_items, $hash_ref->{'depth_min'} );
    push( @record_items, $hash_ref->{'depth_max'} );
    push( @record_items, $hash_ref->{'clamav_action'} );
    push( @record_items, $hash_ref->{'proto'} );
    push( @record_items, $hash_ref->{'filetypes'} );
    push( @record_items, $hash_ref->{'description'} );
    #============自定义比较字段-END===========================#
    return join ",", @record_items;
}

sub save_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未保存" );
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
        #if ( $search ne "" ) {
         #   my $name = lc $hash{'name'};
          #  my $note = lc $hash{'note'};
           # if ( !($name =~ m/$search/) && !($note =~ m/$search/) ) {
                #===对名字，说明进行搜索===#
            #    next;
            #}
        #}

        $hash{'id'} = $id; #自定义id，id可以是任何字符，只要能唯一区别每一条数据
        #$hash{'webAction_view'} = &webAction_handler($hash{'webAction'});#将webACtion转化为中文
       # $hash{'idView'} = $id+1;#为界面显示的列表序号赋值
        $hash{'filetypes'} = &view_assembling( $hash{'filetypes'} );#对端口号进行处理
        #$hash{'webRule'} = &view_assembling( $hash{'webRule'} );#对web防护规则进行处理
        
        push( @$content_array_ref, \%hash );
        $total_num++;
    }  
    

    return ( $status, $mesg, $total_num );
}

sub apply_data() {
    &clear_need_reload_tag();
    system "sudo $setvirus";
    system( "sudo $cmd_set_virus" );
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
   # return $result;
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

#读取文件类型
sub read_data(){
    my $file_json_str = `$cmd_file_type`;
    # print $file_json_str;
    # return;
    my %ret_data; 
    my @lines_file_type;
    my @lines_file_type_names;

    my ( $status, $error_mesg)= &read_config_lines($file_type_file,\@lines_file_type);
    foreach(@lines_file_type){
         my %filedata->{'id'} = (split(",",$_))[0];
         %filedata->{'text'} = (split(",",$_))[1];
         %filedata->{'type'} = 'file';
         push( @lines_file_type_names,\%filedata);
     }


    my $file_json_str = `$cmd_file_type`;
    my $file_json = $json->latin1->decode( $file_json_str );
    #my $file_json = $file_json_str;
    %ret_data->{'file_type_data'} = $file_json;
    %ret_data->{'status'} = $status;
    %ret_data->{'mesg'} = $error_mesg;

    my $ret = $json->encode(\%ret_data);
    print $ret; 

}

#将同一字段中的多个值进行处理
sub datas_hander() {
    my ($data,$act) = @_;
    if( $act eq 'save' ) {
        $data =~ s/\，/\&/g;
        $data =~ s/\,\ /\&/g;
    }
    if($act eq 'load') {
        $data =~ s/&/\,\ /g;
    }
    return $data;
    
}

