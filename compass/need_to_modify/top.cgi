#!/usr/bin/perl
use Encode;
require '/var/efw/header.pl';
require 'list_panel_opt.pl';
my $action = "";
my %par;
my $help_file = "/var/efw/help/setting";
my %help_hash;
my $help_src = "/images/help_icon_on.png";
my $url = "https://".$ENV{'SERVER_ADDR'}.":10443";

my $file_warn = "/var/efw/ips/warnevent/warn";
my $file_gwarn = "/var/efw/warn/console_warn/should_warn";
my $file_gwarn_info = "/var/efw/warn/console_warn/warn_content";
#2014.11.26 新加关机重启
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;
my $system_title;
&validateUser();
&read_config_system();
&readhash($help_file, \%help_hash);
$action = $help_hash{"HELP_ENABLED"};
if($action eq "on"){
    $hidden_action = "off";
    $help_src = "/images/help_icon_on.png";
}else{
    $hidden_action = "on";
    $help_src = "/images/help_icon_off.png";
}
sub showhttpheaders_top
{
    calcURI();
    genFlavourMenus();
    checkForHASlave();
    print "Pragma: no-cache\n";
    print "Cache-control: no-cache\n";
    print "Connection: close\n";
    print "Content-type: text/html\n\n";
}
sub delCache1()
{
        my $time = ` cat /var/efw/userinfo/user_config |grep TIMEOUT`;
        $time =~ /TIMEOUT=(\d+)/;
        $time = 1 ;
        $timeout = gmtime(time()+$time)." GMT";
        my $cookiepath = "/";
        print "Set-Cookie: ee11cbb19052e40b07aac0ca060c23ee=/; expires=$timeout; path=$cookiepath\r\n";
}
sub save()
{
    if($par{'ACTION'} eq "on"){
        $help_hash{"HELP_ENABLED"} = "on";
        &writehash($help_file,\%help_hash);
        print "<script type='text/javascript' charset='utf-8'>window.location.href=window.location.href;</script>";
    }
    elsif($par{'ACTION'} eq "off"){
        $help_hash{"HELP_ENABLED"} = "off";
        &writehash($help_file,\%help_hash);
        print "<script type='text/javascript' charset='utf-8'>window.location.href=window.location.href;</script>";
    }
    ####退出登录时记录用户审计信息 by 张征 2012-1-6
    if($par{'ACTION'} eq "logout"){
        #my $url = "../html/index.cgi";
        print "<script>var des='https://' + window.parent.location.host + '/index.cgi';window.parent.location.replace(des); </script>";
        #print "<script type='text/javascript' charset='utf-8'>exit_sys('$ENV{'SERVER_ADDR'}')</script>";
    }
    ####退出登录时记录用户审计信息 by 张征 2012-1-6 END
}


sub read_config(){
    if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    $system_title = $system_settings{'SYSTEM_TITLE'};
}

#将框架分html写入
sub top_html(){
&read_config();
my @user = getCurUser();
printf <<EOF
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>$system_title</title>
<style>
.tip{width:500px;border:1px solid #ddd;padding:8px;background:#f1f1f1;color:#666;}
</style>
<link rel="shortcut icon" href="/images/shortcut.ico" />
<!--<link rel="stylesheet" type="text/css" href="/include/main.css" />-->
<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
<link rel="stylesheet" type="text/css" href="/include/main.css" />
<script language="javascript" type="text/javascript" src="/include/jquery.js"></script>



<script src="/include/jquery.easing.1.3.js" type="text/javascript"></script>
<script src="/include/jquery.kwicks-1.5.1.pack.js" type="text/javascript"></script>
<script language="javascript" type="text/javascript" src="/include/main.js"></script>
<script type="text/javascript" src="/include/for_iE6_png.js"></script>
<script language="JavaScript" type="text/javascript" src="/include/alarm_controller.js"></script>
<script language="JavaScript" type="text/javascript" src="/include/show_edit_passwd.js"></script>


<script language="javascript" type="text/javascript">
var tip={\$:function(ele){
  if(typeof(ele)=="object")
    return ele;
  else if(typeof(ele)=="string"||typeof(ele)=="number")
    return document.getElementById(ele.toString());
    return null;
  },
  mousePos:function(e){
    var x,y;
    var e = e||window.event;
    return{x:e.clientX+document.body.scrollLeft+document.documentElement.scrollLeft,
y:e.clientY+document.body.scrollTop+document.documentElement.scrollTop};
  },
  start:function(obj){
    var self = this;
    var t = self.\$("mjs:tip");
    obj.onmousemove=function(e){
      var mouse = self.mousePos(e);  
      t.style.left = mouse.x + 10 + 'px';
      t.style.top = mouse.y + 10 + 'px';
      t.innerHTML = obj.getAttribute("tips");
      t.style.display = '';
    };
    obj.onmouseout=function(){
      t.style.display = 'none';
    };
  }
  }
    \$(function () {
    //    var begin = window.setInterval("begin()","3000");
    });
    function begin(){
        \$.get('/cgi-bin/get_snort_alert.cgi',function(data){
            var now =data;
            if(data == "no message"){
                \$("#add_div").remove();
                \$("#mjs:tip").remove();
            }
            else{
                \$("#add_div").remove();
                \$("#mjs:tip").remove();
                var str = "<div id='add_div' style='text-align:right;float:left;'><img style='height:45px' src='/images/warning.gif' onmouseover='tip.start(this)' tips='"+now+"' /></div>";
                \$(".logo").after(str);
            }
        });
    }
    function do_confirm_restart(){
        var r = confirm("确定重启？");
        if(r == true){
            \$("#val_r").val("YES");
        }else{
            \$("#val_r").val("NO");
        }
    }
    function do_confirm_shutdown(){
        var r = confirm("确定关机？");
        if(r == true){
            \$("#val_s").val("YES");
        }else{
            \$("#val_s").val("NO");
        }
    }
</script>
</head>
<body>
<div class="header">
    <!--将图标和文字分开管理 By WL-->
    <a class="logo" onclick="refresh_page()" href='/index.cgi'>
        <span id="CH_logo_title">$system_settings{'SYSTEM_TITLE'}</span>
    </a>

<div class="header-right">
<div id="alarm_controller">
    <span  alt="报警事件"  onclick="show_alarm_panel()"></span>
    <audio src="#" autoplay=true loop=true hidden=ture></audio>
</div>

<div class="help-div">

<ul class="kwicks">

<!--三峡版本暂时不加入此功能
    <li><img src="/images/message.gif" />  %s</li>
-->
    <!--加入重启和关机按钮 -->
    <li>
        <form METHOD="post" action="$ENV{'SCRIPT_NAME'}"  onclick="do_confirm_restart();" class="top_page_img_title" title="重启">
            <span>
                <i class="top-reboot_sys"></i>
                <span >重启</span>
                <input type="hidden" name="ACTION" value="restart">
                <input id="val_r" type="hidden" name="CONFIRM">
            </span>
        </form>
    </li>
    <li>
        <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" onclick="do_confirm_shutdown();" title="关机">
            <span class="top_page_img_title" >
                <i class="top-shutdown"></i>
                <span>关机</span>
                <input type="hidden" name="ACTION" value="shutdown">
                <input id="val_s" type="hidden" name="CONFIRM">
            </span>
        </form>
    </li>
    <li title="%s">        
        <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" id="help_form" onclick="document.getElementById('help_form').submit();fresh_current_page('$url');return false;" title="帮助">
            <span class="top_page_img_title" >
                <i class="top-help"></i>
                <span type="submit">%s</span>
                <input type="hidden" name="ACTION" value="$hidden_action">
            </span>
        </form>
    </li>
<!--三峡版本暂时不加入此功能
    <li><img src="/images/lock.gif"  />  %s</li>
-->
     <li>
        <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" onsubmit=" return false;" id="edit_passwd_button" title="修改密码">


            <span  class="top_page_img_title" >
                <i class="top-change_pwd"></i>
                <span>修改密码</span>

            </span>
        </form>
    </li>
    <li title="退出系统">
        <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" id="logout_form" onclick="document.getElementById('logout_form').submit();" title="退出系统">
            <span class="top_page_img_title"  >
                <i class="top-user"></i>
                <span id="now_user" title="$user[0]">$user[0]</span>
                <input type="hidden" name="ACTION" value="logout">
            </span>
        </form>
    </li>












</ul>
</div>
</div>
</div>

<div id='mjs:tip' class='tip' style='position:absolute;left:0px;top:0px;display:none;z-index:100'></div>
<div id= "div_lock_top" class="popup-mesg-box-cover" style="z-index:1000; display:none;"> </div> 
</body>
</html>
EOF
, _('Contact us')
, $action eq "on"?_("当前帮助提示框显示，点击关闭不显示"):_("当前帮助提示框不显示，点击开启显示")
, $action eq "on"?_("帮助已开启"):_("帮助已关闭")
, _('lock')
;
}
&getcgihash(\%par);

&do_action();

sub do_action(){
    
    my $action = $par{'ACTION'};
    if($action eq 'check_warnfile'){
        &showhttpheaders();
        &check_warnfile();
    }elsif($action eq 'confirm'){
        &showhttpheaders();
        &do_confirm();
    }elsif($action eq 'load_data_detail'){
        &showhttpheaders();
        &load_data_detail();
    }else{
        ####退出登录时清空用户登录的cookie信息 by 张征 2012-1-6
        if($action eq "logout"){

            my $log_message = "用户正常退出登录";
            &user_log_login($log_message);
            &delCache1($user[0]);
        }elsif($action eq 'restart'){
            if($par{'CONFIRM'} eq 'YES'){
                &restart();
                &delCache1($user[0]);
            }
        }elsif($action eq 'shutdown'){
            if($par{'CONFIRM'} eq 'YES'){
                &shutdown();
                &delCache1($user[0]);
            }
        }
        ####退出登录时清空用户登录的cookie信息 by 张征 2012-1-6 END
        showhttpheaders_top();
        top_html();
        save();
    }
    

}

#检查预警文件是否存在函数
sub check_warnfile(){


    if( -e $file_gwarn){
        print "exercise";
    }#else{
        # if(-e $file_warn){
            # print "exercise";
        # }else{
            # print "unexercise";
        # }
    # }












}
#取消预警提示信息的函数
sub do_confirm(){
    if(-e $file_gwarn){








        `rm $file_gwarn`;
    }#elsif(-e $file_warn){
        # `rm $file_warn`;
    # }


}
#加载预警详细信息
sub load_data_detail(){
    my @lines;
    my @data_detail;
    my @data_field;
    my $detail_info;
    if(-e $file_gwarn_info){
        @lines = read_conf_file($file_gwarn_info);
        $detail_info = join("\n",@lines);










        # my $line = @lines[0];
        # @data_detail = split(/,/,$line);
        # @data_field = ("report_time","danger_level","protocol","sip","sport","dip","dport","chinese_name","msg","eip");
    } #elsif(-e $file_warn){
        # @lines = read_conf_file($file_warn);
        # my $line = @lines[0];
        # @data_detail = split(/,/,$line);
        # @data_field = ("report_time","danger_level","protocol","sip","sport","dip","dport","chinese_name","msg");
    # }


    
    my %ret_data;
    # my $length = @data_field;
    # for(my $i=0;$i<$length;$i++){
        # %ret_data ->{$data_field[$i]} = $data_detail[$i];
    # }
    %ret_data ->{'detail_info'} = $detail_info;


    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
#关机
sub shutdown(){
    my $log_message = "关闭".$system_title;
    &user_log($log_message);
    &log($system_title."关闭");
    system '/usr/local/bin/ipcopdeath';
}
#重启
sub restart(){
    my $log_message = "重启".$system_title;
    &user_log($log_message);
    system '/usr/local/bin/ipcoprebirth';
}
sub read_config_system(){
    if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    $system_title = $system_settings{'SYSTEM_TITLE'};
}
