#!/usr/bin/perl
require '/var/efw/header.pl';
require 'list_panel_opt.pl';
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;
my $system_title;
my %par;
my $json = new JSON::XS;
my $file_gwarn_info = "/var/efw/warn/console_warn/warn_content";
my $file_auto_confirm = "/var/efw/warn/console_warn/autoconfirme_config";
my $cmd = "sudo /usr/local/bin/processwarnevent.py ";

my $psdLength = &readPsdLength();
my $passwd_height;


sub read_config(){
    if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    $system_title = $system_settings{'SYSTEM_TITLE'};
}

#将框架分html写入
sub center_html()
{
&read_config();
printf <<EOF
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf8" />
<title>$system_title</title>
<link rel="stylesheet" type="text/css" href="/include/port_custom.css" />
<link rel="stylesheet" type="text/css" href="/include/main.css" />
<link rel="stylesheet" type="text/css" href="/include/content.css" />
<link rel="stylesheet" type="text/css" href="/include/style.css" />
<link rel="stylesheet" type="text/css" href="/include/center-dialog.css" />
<script language="javascript" type="text/javascript" src="/include/jquery.js"></script>
<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
<script language="JavaScript" src="/include/ChinArk_form.js"></script>
<script language="JavaScript" src="/include/list_panel.js"></script>
<script language="JavaScript" src="/include/add_panel.js"></script>
<script language="JavaScript" src="/include/message_manager.js"></script>
<script language="JavaScript" src="/include/async_modify.js"></script>
<script language="JavaScript" type="text/javascript" src="/include/jquery.md5.js"></script>
<script type='text/javascript' src='/include/jsencrypt.min.js'></script>

<script language="JavaScript" type="text/javascript" src="/include/alarm_controller_init.js"></script>

<script>
\$(document).ready(function(){
    var right_frame_width =(document.body.clientWidth||window.innerWidth)-181;
    document.getElementById("rightFrame").style.width=right_frame_width+"px";

});
\$(window).resize(function(){
  var right_frame_width =(document.body.clientWidth||window.innerWidth)-181;
  document.getElementById("rightFrame").style.width=right_frame_width+"px";
});
</script>


</head>

<body>
<iframe src="left.cgi"  name="left" frameborder=0 id="leftFrame" >
浏览器不支持嵌入式框架，或被配置为不显示嵌入式框</iframe>
<iframe src="d_status.cgi"  name="right" scrolling="NO" frameborder=0 id="rightFrame" >
浏览器不支持嵌入式框架，或被配置为不显示嵌入式框</iframe>
    
    <!--
    <div id= "bgDiv" style= "position:absolute;display:none;top:0; background-color:#777; filter:progid:DXImagesTransform.Microsoft.Alpha(style=3,opacity=25,finishOpacity=75); opacity:0.6; left:0; width:100%; height:768px; z-index:10000;"> </div> 
    <div id= "bgDiv2" style= "width:100%;margin-left:300px; height:auto; position:absolute;display:none; top:150px; left:0px; filter:progid:DXImagesTransform.Microsoft.Alpha(style=3,opacity=25,finishOpacity=75); opacity:1.0; left:0; width:50%; z-index:10000;"> 
        <div class="fd_box" style="width:600px">
        <div class="tm_box" style="width:580px;height:288px"></div>
        <div class="denglu_box" style="width:560px;height:266px;background-color:#ffffff">
        <h1 style="width:550px;color:red;font-size:24px">预警详细信息</h1>
        
        <div>
        <div style="float:left;width:550px;height:220px;">
        <div id="info" style="text-align:center;" class="div_dis">事件基本信息</div>
        <div id="detail_indo" style="width:260px;word-wrap:break-word;"></div>
        </div>
        
        <div id="des" style="float:left;width:260px;margin-left:10px">
        <div class="div_dis" style="text-align:center;">事件说明</div>
        <div class="div_dis"><div style="float:left">入侵类型：</div><div style="float:left" id="inv_type" ></div></div><br/>
        <div class="div_dis"><div style="float:left">入侵描述：</div><div style="float:left;width:250px" id="description"></div></div>
        </div>
        </div>
        
        <div style="width:50px;margin-top:210px;margin-left:245px"><input type='button' style='color: black; background-image: url(\"/images/button.jpg\");' value='确定' onclick="doaction_confirm()"  name='ok' /></div>
        </div>
        
        <div style="top:15px" onclick="closedetail();" class="guanbi">
        <label>
            <img id="search-button" class="search-button-img" src="../images/close.png" />
        </label>
        </div>
    </div>
    </div>
    -->
    <div id="mesg_box_alarm" style="width: 96%;margin: 0px auto;"></div>
    <div id="panel_list" style="width: 96%;margin: 0px auto;"></div>
    <div id="panel_detail" style="width: 96%;margin: 0px auto;"></div>
    <div id= "eidt_passwd_bg" class="dialog__overlay" style="display:block;"> </div>
    <div id= "eidt_passwd_aaa" style="width:100%;height:100%;">
        <div id= "eidt_passwd_bbb" style="dispaly:none;">
            <div id="eidt_passwd_body" class="popup-mesg-box-body mesg-box-s" style="margin:0px auto;line-height: 30px;text-align: center;display:none; width:500px;">
                <div class=modifypsd-header style="background-color: #d5e2f2;height: 34px;border-bottom: 1px solid;border-color: #ccc;"><span>修改密码</span></div>
                <div id="have_to_mesg" style="color:red;background-color: #e6eff8;"></div>
                <form name="EDIT_PASSWD_FORM" action="/cgi-bin/lock_screen_check.cgi"  enctype='multipart/form-data' method='post' onsubmit="do_edit_passwd(); return false;">
                <table>
                    <tr class="modifypsd-original env1">
                        <td class="modifypsd-left"><span style="margin-left:12px;">原始密码*</span></td>                
                        <td class="modifypsd-right"><input type="password" style="width:253px;margin-left:12px;padding:4px;margin-bottom:5px;margin-top: 5px;" placeholder="原始密码" id="primary_passwd" name="primary_passwd"/></td>    
                    </tr>
            
                    <tr class="modifypsd-new odd1">
                        <td class="modifypsd-left"><span style="margin-left:12px;">新</span><span style="margin-left:6px;">密</span><span style="margin-left:6px;">码*</span></td>             
                        <td class="modifypsd-right"><input type="password" style="width:253px;margin-left:12px;padding:4px;margin-bottom:5px;" placeholder="新密码" id="new_passwd" name="new_passwd"/></td>
                    </tr>
            
                    <tr class="modifypsd-newagain env1">
                        <td class="modifypsd-left"><span style="margin-left:12px;">确认密码*</span></td>            
                        <td class="modifypsd-right"><input type="password" style="width:253px;margin-left:12px;padding:4px;margin-bottom:5px;" placeholder="确认密码" id="confirm_passwd" name="confirm_passwd"/></td>
                    </tr>
                </table>    
                    <div style="color: red;"> </div>
            
                    <div class="add-panel-footer" style="height: 34px;line-height: 34px;">
                        <input type="submit" class="add-panel-form-button" value="确认"/>
                        <input type="text" value="$psdLength" hidden="hidden" disabled="disabled" id="psdLength"/>
                        <input type="reset" id="reset_edit_button" class="add-panel-form-button" value="撤销"/>
                    </div>
                    <script>
                        \$('#reset_edit_button').on('click',function(){
                            \$("#eidt_passwd_bbb").attr('class','close--eidt_passwd_bbb');
                            setTimeout(function() {
                                \$("#eidt_passwd_bbb").css('display','none');
                                \$("#eidt_passwd_bg").css('display','none');
                            },250);
                        });
                        \$('#eidt_passwd_bg').on('click',function(){
                            \$("#eidt_passwd_bbb").attr('class','close--eidt_passwd_bbb');
                            setTimeout(function() {
                                \$("#eidt_passwd_bbb").css('display','none');
                                \$("#eidt_passwd_bg").css('display','none');
                            },250);
                            var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;
                            topframe.document.getElementById("div_lock_top").style.display = "none";
                            \$(this).attr('class','dialog__overlay');
                            setTimeout(function() {
                                \$(this).css('display','none');
                                },0);
                            });
                    </script>
                </form>
            </div>
        </div>
    </div> 
    <script language="JavaScript" type="text/javascript" src="/include/lock_screen_controller.js"></script>

</body>
</html>
EOF
;
}
&getcgihash(\%par);
showhttpheaders();
&do_action();
#center_html();

sub do_action(){
    my $action = $par{'ACTION'};
    if($action eq 'load_data'){
        &load_data();
    }elsif($action eq 'do_confirm_detail'){
        &do_confirm_detail();
    }elsif($action eq 'do_confirm_selected'){
        &do_confirm_selected();
    }elsif($action eq 'getPasswordLength'){
        print $psdLength;
        return;
    }
    else{
        center_html();
    }
}
#配置报警事件
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
    $config{'id'}   = $temp[0];
    $config{'theme'}   = $temp[1];
    $config{'type'}   = $temp[2];
    $config{'time'}   = $temp[3];
    $config{'content'}   = $temp[4];
    #============自定义字段组装-END===========================#
    return %config;
}
#加载预警列表信息
sub load_data(){
    my %ret_data;
    my @content_array;
    my @lines = ();
    my ( $status, $error_mesg, $total_num );
    ( $status, $error_mesg, $total_num ) = &get_content( \@content_array );

    
    #读取自动确认配置信息
    my @lines_auto = ();
    &read_config_lines($file_auto_confirm,\@lines_auto);
    my @detail_data_auto = ();
    for(my $i = 0; $i< @lines_auto; $i++){
        my @data_item = split(",",$lines_auto[$i]);
        my %conf_data_auto;
        %conf_data_auto ->{'alarm_theme'} = $data_item[0];
        %conf_data_auto ->{'num_event'} = $data_item[1];
        %conf_data_auto ->{'id'} = $i;
        push(@detail_data_auto, \%conf_data_auto);
    }

    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'detail_data_auto'} = \@detail_data_auto;
    %ret_data->{'total_num'} = $total_num;
    %ret_data->{'status'} = $status;
    %ret_data->{'reload'} = 0;
    %ret_data->{'error_mesg'} = $error_mesg;
    # %ret_data->{'page_size'} = $PAGE_SIZE;

    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
sub get_content($) {
    my $content_array_ref = shift;
    my $current_page = int( $par{'current_page'} );
    my $page_size = int( $par{'page_size'} );
    my $alarm_type = $par{'alarm_type'};
    
    if(!$current_page){
        $current_page = 1;
    }
    if(!$alarm_type){
        $alarm_type = "all";
    }

    my $from_num = ( $current_page - 1 ) * $page_size;
    my $to_num = $current_page * $page_size;

    my @lines = ();
    my ( $status, $error_mesg ) = (0,"");
    # my ( $status, $error_mesg ) = &read_config_lines( $file_gwarn_info, \@lines );
    my $str_lines = `$cmd -t $alarm_type -p $current_page`;
    @lines = split("\n",$str_lines);

    my $total_num = $lines[0];
    if( $total_num < $to_num ) {
        $to_num = $total_num;
    }

    #==判断是否只加载一页====#
    if( !$LOAD_ONE_PAGE ) {
        #==全部加载===#
        $from_num = 0;
        $to_num = $total_num;
    }
    for ( my $i = 1; $i < @lines; $i++ ) {
        my %config = &get_config_hash( $lines[$i] );
        if( $config{'valid'} ) {
            #$config{'item_id'}   = 20 - $i;
            $config{'item_id'}   = $i - 1;
            #unshift( @$content_array_ref, \%config );
            push( @$content_array_ref, \%config );
        }else{
            $total_num --;
        }
    }
    return ( $status, $error_mesg, $total_num );
}
sub do_confirm_detail(){
    my $is_checked = $par{'is_checked'};
    my $id_alarm = $par{'id_alarm'};
    my $id_auto = $par{'id_auto'};
    my $item_auto = $par{'item_auto'};
    if($is_checked eq 'yes'){
        if($id_auto eq 'new_id'){
            &append_one_record( $file_auto_confirm, $item_auto );
        }else{
            &update_one_record( $file_auto_confirm, $id_auto, $item_auto );
        }
    }else{
        if($id_auto ne 'new_id'){
            &delete_several_records( $file_auto_confirm, $id_auto);
        }
    }
    #&delete_several_records( $file_gwarn_info, $id_alarm);
    system("$cmd -r $id_alarm");
    print $is_checked.$id_alarm;
}
sub do_confirm_selected(){
    if($par{'id'} eq 'ids_all'){
        # my @empty = ();
        # &write_config_lines( $file_gwarn_info, \@empty );
        system("$cmd -f");
    }else{
        #&delete_several_records( $file_gwarn_info, $par{'id'});
        system("$cmd -r $par{'id'}");
    }
}