#!/usr/bin/perl

require '/var/efw/header.pl';
use Encode;
use CGI;

use constant MAX_FILE_SIZE  => 5_242_880;
use constant MAX_DIR_SIZE   => 100 * 1_048_576;
use constant MAX_OPEN_TRIES => 100;

#记录日志的变量
my $CUR_PAGE = "ISP地址库" ;  #当前页面名称，用于记录日志
my $log_oper;                   #当前操作，用于记录日志，
                                 # 新增：add，编辑：edit，删除：del，应用：apply，启用：enable，禁用：disable，移动：move
my $rule_or_config = '1';       #当前页面是规则还是配置，用于记录日志，0为规则，1为配置

my $setting_file = "/var/efw/outboundlb/isp/settings";
my $upload_dir = "/var/efw/outboundlb/isp/files/";
my $need_reload_file = "/var/efw/outboundlb/needreload";
my $data_file = "/var/efw/outboundlb/isp/config";
my $default_config_dir = '/var/efw/outboundlb/isp/default/';
my $default_config_file = "/var/efw/outboundlb/isp/default/config";
my $smart_routing_config_file = "/var/efw/outboundlb/config";

my %par, %query;

my @errormessages=();

my $errormesg,$warnmesg,$notemesg;
my $extraheader = '<link rel="stylesheet" type="text/css" href="/include/isp_table.css" />';

my $ETHERNET_SETTINGS = "/var/efw/ethernet/settings";

$reload=0;

&getcgihash(\%par);
&getqueryhash(\%query);
&do_action();


sub create_need_reload_file() {
    if(! -e $need_reload_file){
        system( "touch $need_reload_file" );
    }
}

sub clear_need_reload_file() {
    if( -e $need_reload_file ){
        system( "rm $need_reload_file" );
    }
}
sub apply_data() {
    &clear_need_reload_file();
    system("/usr/local/bin/restartoutboundlb");
    $status = $?>>8;

    if( $status != 0 ){
        &send_status(-1, "应用失败");
    }else{
        &send_status(0, "应用成功");
    }
    
}
sub getqueryhash($){
    my $query = shift;
    my $query_string = $ENV{'QUERY_STRING'};
    if ($query_string ne '') {
        my @key_values = split("&", $query_string);
        foreach my $key_value (@key_values) {
            my ($key, $value) = split("=", $key_value);
            $query->{$key} = $value;
            $query->{$key} =~ s/\r//g;
            $query->{$key} =~ s/\n//g;
            chomp($query->{$key});
        }
    }
    return;
}
sub main(){

    &make_file();
    &openpage(_('ISP网段表配置'), 1, $extraheader);

    &openbigbox($errormesg, $warnmesg, $notemesg);

    &load_data();

    &closebigbox();
    &closepage();

}

sub make_file(){
    if(! -e $setting_file){
        system("touch $setting_file");
    }
    if(! -e $data_file){
        system("touch $data_file");
    }
    if(! -e $upload_dir){
        system("mkdir -p $upload_dir");
    }
    if(! -e $default_config_dir){
        system("mkdir -p $default_config_dir");
    }
    if(! -e $default_config_file){
        system("touch $default_config_file");
    }
}
sub read_config_file($) {
    my @lines;
    my $file=shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $query_action = $query{'ACTION'};
    my $line_id  = $par{'line_id'};
    my $if_sucess;
    my $new_name = "";
    my ($status, $mesg) = (-1, "");

    if( $action ne 'download_file' && $query_action ne 'download_file') {
        &showhttpheaders();
    }
    elsif( $query_action eq 'download_file' ) {
        if($query{'line_id'} ne ""){
            &do_download_file( $query{'line_id'} );
        }else{

        }
    }
    if( $action eq "apply" ){
        &apply_data();
        $log_oper = "apply";
    }
    elsif( $action eq "edit" && $par{'panel_action'} eq 'save_data') {
            ($status, $mesg ) = &check_values( $par{'isp_name'}, $par{'upload_file'} );
            $log_oper = "edit";
            if( $status != 0 ){
                &send_status( $status, $mesg );
            }else{
                if( $par{'upload_file'} ne "" ){   #保存编辑时数据时千万要小心如果用户没有上传新的文件时你点保存会把这个字段覆盖为空！
                    # 修改：编辑时上传了新的网段文件，但是忘了把旧网段文件删除
                    my @config_lines = &read_config_file( $data_file );
                    my $line_record = $config_lines[ $line_id ];
                    my @tmp = split(/,/, $line_record);
                    my $isp_file_name = $tmp[2];
                    my $isp_file_path = $upload_dir."$isp_file_name";
                    system("rm $isp_file_path");
                    # 修改结束
                    $new_name = &do_upload_file();

                    if( $new_name eq "" ){
                        &save_data( $par{'isp_name'}, $par{'comment'}, $par{'upload_file'}, $par{'line_id'} );
                    }else{
                        &save_data( $par{'isp_name'}, $par{'comment'}, $new_name, $par{'line_id'} );
                    }
                }
                else{   # 即$par{'upload_file'} eq "" 这时你也要做修改保存处理！
                    my @config_lines = &read_config_file( $data_file );
                    my $line_record = $config_lines[ $line_id ];
                    my @tmp = split(/,/, $line_record);
                    my $isp_name = $tmp[0];
                    my $isp_file_name = $tmp[2];
                    &save_data( $isp_name, $par{'comment'}, $isp_file_name, $par{'line_id'} );
                }
            }
    }elsif( $action eq "add" && $par{'panel_action'} eq 'save_data') {

            ($status, $mesg ) = &check_values( $par{'isp_name'}, $par{'upload_file'} );
            if( $status != 0 ){
                &send_status( $status, $mesg );
            }else{
                $new_name = &do_upload_file();
                if( $new_name eq "" ){
                    &save_data( $par{'isp_name'}, $par{'comment'}, $par{'upload_file'}, $par{'line_id'} );
                }else{
                    &save_data( $par{'isp_name'}, $par{'comment'}, $new_name, $par{'line_id'} );
                }
            }
             $log_oper = "add";
    }
    elsif( $action eq 'delete_data') {
        &delete_line( $par{'line_id'} );
        $log_oper = "del";
    }
    &main();
}

sub do_download_file($){
    my $line_id = shift;
    my $file;
    my $file_name;
    if($line_id =~ /\.txt/){
        $file_name = $line_id;
        $file = "$upload_dir".$line_id;
    }else{
        my @lines = &read_config_file( $data_file );
        my $line = $lines[$line_id];
        my @temp = split(/,/, $line);

        $file_name = $temp[2];
        $file = "$upload_dir".$file_name;
    }
    # `echo $file >/tmp/xixi`;
    if( -e "$file") {
        open(DLFILE, "<$file") or &send_status(-1, "读取下载文件内容失败！");
        my @fileholder = <DLFILE>;
        close (DLFILE);
        print "Content-Type:application/x-download\n";
        print "Content-Disposition:attachment;filename=$file_name\n\n";
        print @fileholder;
        exit;
    }else {
        &showhttpheaders();
        $errormesg = "对不起，不存在此文件";
    }

}

sub do_upload_file() {
    
    my $cgi = new CGI;
    my $file_name = $cgi->param('upload_file');
    my $upload_dir = $upload_dir;

    # my $name = $file_name;
    my $new_name;
    # my $file_path = $upload_dir . $name;
    my $file_path = $upload_dir.$file_name;

    if( ($par{'ACTION'} eq "add") && $par{'upload_file'} eq ""){
        &send_status(-1, "对不起，您没有上传文件！"); # return 0; #
        return "";
    }
    if ( &dir_size( $upload_dir ) + $ENV{CONTENT_LENGTH} > MAX_DIR_SIZE ) {
        &send_status( -1, "对不起，目录已满，文件无法上传" );  # return 0; #
        return "";
    }
    if( -s($file_name) > MAX_FILE_SIZE ){
        &send_status( -1, "对不起，你的文件大小超过了5M" );  # return 0; #
        return "";
    }

    if(-e ("$upload_dir".$file_name)){
        $new_name = &handle_filename_repeated( $file_name );
        $file_path = $upload_dir . $new_name;
    }

    open ( UPLOADFILE, ">$file_path" ) or &send_status(-1, "对不起，打开写入上传文件失败！");
    binmode UPLOADFILE;
    while ( <$file_name> )
    {
        print UPLOADFILE $_;
    }
    close UPLOADFILE;
    # return 1;
    if($new_name ne "") {  return $new_name;  }
}

sub dir_size($) {
   my $dir = shift;

   my $dir_size = 0;
   opendir DIR, $dir or die "Unable to open $dir: $!";

   while ( readdir DIR ) {

       $dir_size += -s "$dir/$_";

   }

   return $dir_size;

}

sub save_data( $$$$ ){

    my $isp_name = shift;
    my $comment = shift;
    my $isp_file_name = shift;
    my $line_id = shift;


    my @lines = &read_config_file( $data_file );
    my $line = "$isp_name,$comment,$isp_file_name";
    if($par{'ACTION'} eq "add") {
        push (@lines,$line);
    }
    else{
        $lines[ $line_id ] = $line;
    }
    &save_config_file(\@lines,$data_file);
    &send_status(0,"配置保存成功");
    &create_need_reload_file();
    return 1;
}

sub delete_line($){
    my $line_id = shift;
    my $isp_file_name;
    my @save_lines;

    my @lines = &read_config_file( $data_file );
    my $line_record = $lines[ $line_id ];
    my @tmp = split(/,/, $line_record);
    my $isp_name = $tmp[0];
    open (FILE_HOLDER, "<$smart_routing_config_file");
    while( <FILE_HOLDER> ){
        if($_ =~ /ISP:$isp_name/){
            &send_status(-1, "对不起，此ISP正在被智能路由使用，所以无法删除");
            return;
        }
    }
    close FILE_HOLDER;
    for (my $i = 0; $i < @lines ; $i++) {
        if ( "$i" ne "$line_id" ) {
            push(@save_lines,$lines[$i]);
        }elsif( "$i" eq "$line_id"){
            my @tmp = split(/,/, $lines[$i]);
            # $isp_file_name = $tmp[1];  因为加入了备注字段所以网段文件名的下标不再是1，而是2了
            $isp_file_name = $tmp[2];
        }
    }
    &save_config_file( \@save_lines, $data_file );
    my $isp_file_path = $upload_dir."$isp_file_name";

    system("rm $isp_file_path");
    if( ($?>>8) !=0 ){   &send_status(-1, "网段文件无法删除，请查看");   }
    else{   &send_status(0, "删除成功");   }
    &create_need_reload_file();
}

sub  display_add($){

    my $is_editing = shift;
    my $line_id = $par{'line_id'};
    my $action ="";
    my $title, $buttontext, $canceltext, $showeditor;
    my $isp_name, $comment, $isp_file_name;
    my $label, $readonly, $tip;

    if( $is_editing ) {
        my @lines = &read_config_file( $data_file );
        my @temp = split( /,/, $lines[$par{'line_id'}] );
        $isp_name = $temp[0];
        $comment  = $temp[1];
        $isp_file_name = $temp[2];
        $action = "edit";
        $title = _('编辑运营商网段');
        $buttontext = _("更新编辑");
        $canceltext = _("撤销");
        $label = '请替换旧的网段文件：';
        $readonly = ' readonly="readonly" ';
        $tip = '(ISP名称不可更改，您可以先删除其对应的行再重新创建)';
    }else{
       $isp_name = "";
       $comment = "";
       $isp_file_name = "";
       $action = "add";
       $title = _('添加运营商网段');
       $buttontext = _("上传文件并添加");
       $canceltext = _("撤销");
       $label = '请选择要上传的网段文件：';
       $readonly = '';
       $tip = '';
    }

    if(@errormessages > 0 || $is_editing ) {
        $showeditor = "showeditor";
    }else{
        $showeditor = "";
    }

    &openeditorbox($title, $title, $showeditor, "createrule", @errormessages);

    printf <<EOF
    </form>
    <form method='post' class="inline" name="ISP_FORM" enctype='multipart/form-data' action="$ENV{'SCRIPT_NAME'}" >
    <input type="hidden" name="ACTION" value="$action" >
    <input type="hidden" name="line_id" value="$line_id" >
    <input type="hidden" name="panel_action" value="save_data" >
     <table width="100%" cellpadding="0" cellspacing="0">
     <tr class="odd">
        <td class="add-div-type">ISP名称<font style="margin-left:3px;vertical-align:middle;">*</font></td>
        <td><input type="text" name="isp_name" value="$isp_name"  $readonly />
            <span>$tip</span>
        </td>
     </tr>
     <tr class="env">
        <td class="add-div-type">备注</td>
        <td><input type="text" name="comment" value="$comment" />
        </td>
     </tr>
     <tr class="odd">
        <td class="add-div-type">网段文件 *</td>
        <td><span>$label</span>
            <input type="file" name="upload_file" value="$isp_file_name" />
            <!--<span>请给文件重命名：</span>--><!--文件重命名一个关键问题就是你仅仅把配置信息改了但是真正上传的文件的文件名根本无法改掉，那么下次你在列表里点击下载时用新的名字去找文件就找不到也就无法下载-->
            <input type="hidden" name="file_name" />
        </td>
     </tr>
     </table>
EOF
;
        &closeeditorbox($buttontext, $canceltext, "routebutton", "createrule", $ENV{'SCRIPT_NAME'});

}

sub load_data() {
    my $is_editing;
    if($par{'ACTION'} eq "edit" && $par{'panel_action'} ne "save_data"){
        $is_editing = 1;
    }else{
        $is_editing = 0;
    }
    if(-e $need_reload_file ) {
        # applybox(_("路由规则已改变，请应用该规则以使改变生效"));
        printf <<END
        <div id="mesg_box_id" style="width:96%; margin:20px auto;">
            <div id="" class="all-mesg-box">
                <div id="" class="mesg-box apply-mesg-box" style="display:block;">
                    <div class="mesg-box-main">
                        <img src="/images/pop_apply.png">
                        <span id="" class="mesg-body">路由规则已改变，请应用该规则以使改变生效</span>
                    </div>
                    <div class="mesg-box-foot">
                        <form method="post" action="/cgi-bin/isp_table.cgi" class="inline">
                            <input id="" type="submit" class="net_button" value="应用">
                            <input type="hidden" name="ACTION" value="apply">
                        </form>
                    </div>
                </div>
            </div>
        </div>
END
;
    }
    &display_add( $is_editing );

    my $num = 0;

    my @lines = &read_config_file( $data_file );
    my @default_lines = &read_config_file( $default_config_file );
    printf <<END
    <table width="100%" cellpadding="0" cellspacing="0" border="0" class="ruleslist">
        <tr>
            <td class="boldbase" style="width:30%;">ISP名称</td>
            <td class="boldbase" style="width:20%;">备注</td>
            <td class="boldbase" style="width:30%;">网段文件</td>
            <!--<td class="boldbase" style="width:20%;">操作</td>-->
        </tr>
END
;
        foreach my $line_elem (@lines) {
            my @elem = split(/,/,$line_elem);
            if ($num % 2) {
                print "<tr class='env'>";
            }else{
                print "<tr class='odd'>";
            }
            printf <<EOF
            <td>$elem[0]</td>
            <td>$elem[1]</td>
            <td>$elem[2]</td>
            <!--
            <td class="actions" style="text-align:center">
            <center>
                <form method="get" action="$ENV{'SCRIPT_NAME'}" style="display:inline-block"><!--千万注意这个下载的form的方法要设置成get而非post！-->
                    <input type="hidden" name="ACTION" value="download_file">
                    <input type="hidden" name="line_id" value="$num">
                    <input class='imagebutton' type='image' name="submit" src="../images/download.png" alt="下载" />
                </form>
            
                <form method="post" action="$ENV{'SCRIPT_NAME'}" style="display:block;" >
                     <input class='imagebutton' type='image' name="submit" src="/images/edit.png" alt="修改" />
                     <!--<input type="hidden" name="isp_name" value="$elem[0]" />
                     <input type="hidden" name="isp_file_name" value="$elem[1]" /> -->
                     <input type="hidden" name="ACTION" value="edit">
                     <input type="hidden" name="line_id" value="$num">
                </form>
                <form method="post" action="$ENV{'SCRIPT_NAME'}" style="display:block;" >
                    <input class='imagebutton' type='image' name="submit" src="/images/delete.png" alt="删除" />
                    <input type="hidden" name="ACTION" value="delete_data">
                    <input type="hidden" name="line_id" value="$num">
                </form>
            </center>
            </td>
            -->
        </tr>
EOF
;
            $num ++;
        }
        foreach my $item(@default_lines){
            my @elem = split(/,/,$item);
            if ($num % 2) {
                print "<tr class='env'>";
            }else{
                print "<tr class='odd'>";
            }
            printf <<EOF
            <td>$elem[0]</td>
            <td>$elem[1]</td>
            <td>$elem[2]</td>
            <!--
            <td class="actions" style="text-align:center">
                <form method="get" action="$ENV{'SCRIPT_NAME'}" style="display:inline-block">
                    <input type="hidden" name="ACTION" value="download_file">
                    <input type="hidden" name="line_id" value="$elem[2]">
                    <input class='imagebutton' type='image' name="submit" src="../images/download.png" alt="下载" />
                </form>
            </td>
            -->
        </tr>
EOF
;
            $num ++;
        }

        # if ($num == 0) {
        #     no_tr(4,'无内容');
        # }

    printf <<EOF
</table>
EOF
;

}
sub trim($){
    my $str = shift;
    $str =~ s/^\s+|\s+$//g;
    return str;
}
sub check_values($$) {
    my $isp_name = shift;
    my $isp_file_name = shift;
    my $status = -1;
    my $mesg = "";
    if (!$isp_name) {
        $mesg="ISP名称不能为空!";
        return( $status, $mesg );
    }
    elsif( $isp_name =~ /\s/ ){
        $mesg = "对不起，ISP名称含有空格！";
        return( $status, $mesg );
    }
    elsif( $isp_name =~ /^[0-9]/ ){
        $mesg = "对不起，ISP名称不能以数字开头！";
        return( $status, $mesg );
    }
    else{
        my @config_lines =  &read_config_file($default_config_file);
        foreach my $line(@config_lines)
        {
            my @temp = split(",",$line);
            if( $temp[0] eq "$isp_name") {
                $mesg = "对不起，ISP名称与默认运营商名发生重复！";
                return( $status, $mesg );
            }
        }
    }
    # ISP名称长度还应该在4个字符以上，且20个字符以下
    if( $par{'ACTION'} eq "add" && (!$isp_file_name) ){
        $mesg="对不起，您没有上传文件！";
        return( $status, $mesg );
    }
    if( $par{'ACTION'} eq "add" || ( $par{'ACTION'} eq "edit" && ($isp_file_name ne "") ) ){
        if(  $isp_file_name !~ /\./  ){
            $mesg="对不起，文件名必须要有后缀";
            return( $status, $mesg );
        }
        if( $isp_file_name =~ /\.(.*)$/ ) {
           if( $1 ne "txt"){
                $mesg="对不起，文件名的后缀不正确，必须为.txt";
                return( $status, $mesg );
            }
        }
    }
    if( $par{'ACTION'} eq "add" && $par{'panel_action'} eq 'save_data') {
        my @config_lines =  &read_config_file($data_file);
        foreach my $line(@config_lines)
        {
            my @temp = split(",",$line);
            if( $temp[0] eq "$isp_name") {
                $mesg="对不起，此ISP名称$isp_name已经存在!";
                return( $status, $mesg );
            }
        }
    }
    # return ( 0,"success");
}
sub handle_filename_repeated($){
    my $repeated_name = shift;
    my $fname;
    my $digit;
    if( $repeated_name =~ /^(.*)\.txt$/ ){
        $fname = $1;
        if($fname =~ /\((\d+)\)/){
            $digit = $1;
            $fname =~ s/\(\d+//;   # 把'('和它后面的数字替换为空
            $fname =~ s/\)//;      # 把')'替换为空
        }
    }
    my $new_name = $repeated_name;
    my $i = 0;
    if($digit){  $i = $digit;  }
    while(-e ("$upload_dir".$new_name) ){
        $i += 1;
        $new_name = $fname."(".$i.")".".txt";
    }
    return $new_name;
}
sub send_status($$) {
    my $status = shift;
    my $mesg =shift ;
    if( $status == -1 ){
        $errormesg = $mesg;
    }elsif( $status == 0 ){
        $notemesg = $mesg;
    }

    &write_log($CUR_PAGE,$log_oper,$status,$rule_or_congfig);
}
