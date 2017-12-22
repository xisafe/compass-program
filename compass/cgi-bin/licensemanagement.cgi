#!/usr/bin/perl
#==============================================================================#
#
# 描述: 添加规则列表规则页面
#
# 作者: 刘婷 (LiuTing), 914855723@qq.com
# 公司: capsheaf
# 历史:
#   2015.4.15 LiuTing创建
#   2015.5.9 modified by Julong Liu
#
#==============================================================================#
use Encode;
use Data::Dumper;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';


#=================初始化全局变量到init_data()中去初始化========================#
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变

my $MSG;                #存放系统提示信息
my $STATUS_FLAG;


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

    $errormessage       = '';
    $notemessage        = '';
    $cmd                         = "/usr/local/bin/getSerialMessage.py";

    #============要使用添加面板和翻页列表面板必须引用的CSS和JS-BEGIN============================#
    #============扩展的CSS和JS放在源CSS和JS后面就像这里的add_list_demo.js脚本===================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/licensemanagement.css" />
                    <link rel="stylesheet" type="text/css" href="/include/sm_update_manager.css" />

                    <link rel="stylesheet" type="text/css" href="/include/popup_mesgs.css"/>
                    <link rel="stylesheet" type="text/css" href="/include/waiting_mesgs.css"/>
                    <script type="text/javascript" src="/include/popup_mesgs.js"></script>
                    <script type="text/javascript" src="/include/waiting_mesgs.js"></script>

                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/licensemanagement.js"></script>
                    <script type="text/javascript">
                        function jump(des){
                        window.open(des);
                        }
                    </script>';
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
    if ( $action eq 'upgrade' ) {
        &update_file();
        &show_page();
    }else{
        &show_page();
    }
}

sub show_page() {
    &openpage($page_config{'LICENSE管理'}, 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_main_body();
    &show_device_info();
    &show_message();
    &closepage();
}

sub display_main_body() {
    printf<<EOF

    <div id="mesg_box" class="container"></div>
    <div id="add_panel" class="container"></div>
    <input type="hidden" id="log-mesg-error" value="$errormesg">
    <input type="hidden" id="log-mesg-note" value="$notemessage">  
    
EOF
    ;
}

sub update_file() {

    my $cgi = new CGI; 
    my $file = $cgi->param('file_lib');
    my $tmp_fp = `mktemp`;
    chomp($tmp_fp);
    # print $tmp_fp;
    my $lib_type = $cgi->param('lib_type');
    my $tmp_dat = '/tmp/'.$lib_type.'License.dat';

    
    if(!open(UPLOAD, ">$tmp_fp")) { $errormessage="打开文件失败"; return false; } 
    binmode UPLOAD;
    my $count = 0;
    while(<$file>) { $count = 1; print UPLOAD; }
    close UPLOAD;
    if(!$count) {
        $errormessage = "文件内容为空";
        return 0;
    }

    my $temp_cmd ="sudo /usr/local/bin/import_license.py -t $lib_type -f $tmp_fp";
    # if ($lib_type eq 'firewall') {
    #     $temp_cmd = "sudo /usr/local/bin/import_license.py -t firewall -f $tmp_fp ";
    # }elsif($lib_type eq 'mod'){
    #     $temp_cmd = "sudo /usr/local/bin/import_license.py -t mod -f $tmp_fp ";
    # }else{
    #     $temp_cmd = "sudo /usr/local/bin/import_license.py -t $lib_type -f $tmp_fp";
    # }

    my $res = `$temp_cmd`;
    
    if($res eq "0"){
        $notemessage ="导入成功!";
    }else{
        $errormessage ="导入失败!";
    }
        
    # system("rm -f $tmp_fp");



}

sub show_device_id(){

    
    my $res = `$cmd`;
    my $temp_hash = $json->decode($res);
    my $content_arr = $temp_hash->{'detail'};

    my $firewall = @$content_arr[0];
    my $mod = @$content_arr[1];
    my $lib = @$content_arr[2]->{'lib'};

        printf <<EOF  
        <div class="main">
            <div class="innarsat-serial">
                <form>
                  <fieldset >
                    <legend>设备序列号</legend>
                    <ul class="update-info">
                        <li>系统版本：</li>
                        <li class="facility">$firewall->{'system_version'}</li>
                    </ul>
                    <ul class="update-info">
                        <li>设备ID：</li>
                        <li class="facility">$firewall->{'devid'}</li>
                    </ul>
                    <ul class="update-info">
                        <li>序列号：</li>
                        <li class="active_status">$firewall->{'active'}</li>
                        <li><a class="modify modify_num" libtype="$firewall->{'type'}">修改</a></li>
                        <li class="deadtime">$firewall->{'deadtime'}</li>
                    </ul>
                  </fieldset>
                </form>
            </div>
            <div class="function-module">
                <form>
                  <fieldset >
                    <legend>功能模块序列号</legend>
                    <ul class="update-info">
                        <li>序列号：</li>
                        <li class="active_status">$mod->{'active'}</li>
                        <li><a class="modify modify_num" libtype="$mod->{'type'}">修改</a></li>
                        <li></li>
                    </ul>
                    <ul class="update-info">
                        <li>IPS：</li>
                        <li class="active_status">$mod->{'ips'}</li>
                        <li></li>
                    </ul>
                    <ul class="update-info">
                        <li>应用控制：</li>
                        <li class="active_status">$mod->{'appctrl'}</li>
                        <li></li>
                    </ul>
                    <ul class="update-info">
                        <li>病毒查杀：</li>
                        <li class="active_status">$mod->{'virus'}</li>
                        <li></li>
                    </ul>
                    <ul class="update-info">
                        <li>WEB应用防护：</li>
                        <li class="active_status">$mod->{'webdefend'}</li>
                        <li></li>
                    </ul>
                  </fieldset>
                </form>
            </div>
            <div class="update-serial">
                <form>
                  <fieldset >
                    <legend>升级序列号</legend>
                    <ul class="update-info">
                        <li>应用识别库：</li>
                        <li class="active_status">@$lib[0]->{'active'}</li>
                        <li><a class="modify modify_lib" libtype="@$lib[0]->{'type'}">修改</a></li>
                        <li class="deadtime">@$lib[0]->{'deadtime'}</li>
                    </ul>
                    <ul class="update-info">
                        <li>文件类型库：</li>
                        <li class="active_status">@$lib[1]->{'active'}</li>
                        <li><a class="modify modify_lib" libtype="@$lib[1]->{'type'}">修改</a></li>
                        <li class="deadtime">@$lib[1]->{'deadtime'}</li>
                    </ul>
                    <ul class="update-info">
                        <li>URL库：</li>
                        <li class="active_status">@$lib[2]->{'active'}</li>
                        <li><a class="modify modify_lib" libtype="@$lib[2]->{'type'}">修改</a></li>
                        <li class="deadtime">@$lib[2]->{'deadtime'}</li>
                    </ul>
                    <ul class="update-info">
                        <li>僵尸网络特征库：</li>
                        <li class="active_status">@$lib[3]->{'active'}</li>
                        <li><a class="modify modify_lib" libtype="@$lib[3]->{'type'}">修改</a></li>
                        <li class="deadtime">@$lib[3]->{'deadtime'}</li>
                    </ul>
                    <ul class="update-info">
                        <li>病毒库：</li>
                        <li class="active_status">@$lib[4]->{'active'}</li>
                        <li><a class="modify modify_lib" libtype="@$lib[4]->{'type'}">修改</a></li>
                        <li class="deadtime">@$lib[4]->{'deadtime'}</li>
                    </ul>
                    <ul class="update-info">
                        <li>WEB应用防护特征库：</li>
                        <li class="active_status">@$lib[5]->{'active'}</li>
                        <li><a class="modify modify_lib" libtype="@$lib[5]->{'type'}">修改</a></li>
                        <li class="deadtime">@$lib[5]->{'deadtime'}</li>
                    </ul>
                  </fieldset>
                </form>
            </div>
        </div>
        <div class="add-div-footer"></div>
EOF
    ;
}

sub openmybox
{
    $width = $_[0];
    $align = $_[1];
    $caption = $_[2];
    $id = $_[3];
    
    if($id ne '') {
        $id = "id=\"$id\"";
    }
    else {
        $id="";
    }
    printf <<EOF
    <div class="containter-div">
EOF
    ;
    if ($caption) {
        printf <<EOF
        <span class="containter-div-header"><span style="display:block;float:left;margin-top:3px;">
        <img src='/images/applications-blue.png' />$caption</span>
        <span style="display:block;float:right;height:25px;line-height:25px;margin-right:10px;font-size:12px;font-weight:normal;color:#666;"></span></span>
EOF
;
    }
    else {
        printf <<EOF
        <span class="containter-div-header"><img src='/images/applications-blue.png' />&nbsp;</span>
EOF
;
    }
    
        printf <<EOF
        <div class="containter-div-content">
EOF
    ;

}

sub show_device_info(){
    &openmybox('100%', 'left', _('序列号'));
    &show_device_id();
    &closebox();
}



sub show_message(){
        printf<<EOF
        <script>
        \$( document ).ready(function(){
                message_box.render();
EOF
;
    if($STATUS_FLAG == 0 ){
        if($MSG ne ''){
        printf<<EOF
        message_box.show_popup_mesg("$MSG");
EOF
;
        } 
    }
    if($STATUS_FLAG != 0 ){
        if($MSG ne ''){
        printf<<EOF
        message_box.show_popup_error_mesg("$MSG");
EOF
;
        }
    } 
        printf<<EOF
        });
        var message_box_config = {
            url: "/cgi-bin/message_manager.cgi",
            check_in_id: "mesg_box",
            panel_name: "mesg_box"
        }

        var message_box = new MessageManager( message_box_config );
        </script>
EOF
;
}


sub make_file(){
    if(! -e $conf_dir){
        system("mkdir -p $conf_dir");
    }
    
    if(! -e $conf_file){
        system("touch $conf_file");
    }
}
