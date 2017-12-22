#!/usr/bin/perl
#==============================================================================#
#
# 描述: 文件类型过滤页面 
# 时间：2014-12-24
# 作者: 辛志薇
# 
require '/var/efw/header.pl';
require 'list_panel_opt.pl';
my $upload_filter_path;
my $extraheader;        #存放用户自定义JS
my $download_filter_path;
my %par;
my $errormessage,$warnmessage,$notemessage;
my $json = new JSON::XS;   # 切记要new出一个实例对象来！

&main();



sub main(){

    &getcgihash(\%par);
    &init_data();
    &make_file();
    &showhttpheaders();
    &do_action();
    &show_page();  #这个写在哪里对呢,原来写在do_action()里的最后一行的位置

}

sub init_data(){
    $upload_filter_path = '/var/efw/frox/upload_blacklist';
    $download_filter_path   = '/var/efw/frox/download_blacklist';
    $errormessage = "";     $warnmessage = "";    $notemessage = "";
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/filter.css" />';
}


sub make_file(){
    if(! -e $upload_filter_path){
        system("touch  $upload_filter_path");
    }
    if(! -e $download_filter_path){
        system("touch $download_filter_path");
    }
}
sub do_action(){
    my $action = $par{'ACTION'};
    
    if( $action eq "save_data"){
        &handle_save_data();
    }
}

sub handle_save_data(){
    my $record ="";
    my ( $status, $mesg ) = (-1,"");
    system("echo  >$upload_filter_path");        #先要清空文件内容，否则append_one_record函数就会在原来的基础上累加
    system("echo  >$download_filter_path");      #先要清空文件内容

    my @items;
    my @filter_arr = split(/\|/,$par{'UPLOAD_FILTER'} );   #结果测试，分隔符确实是竖线，而不是&,而且写split("|", $par{'UPLOAD_FILTER'})是不行的，结果就是e,x,e,|,p,d,f各占一行
    foreach my $filter( @filter_arr ){
        $record = ".".$filter;
        ( $status, $mesg ) = &append_one_record( $upload_filter_path, $record );  #要改成写入两个配置文件
        if($status != 0) {    $errormessage = "保存失败";    return;        }
    }
        # $record = $par{'upload_customize'};
        # $record =~ s/\r//g;
        my @tmp = split(/\n/, $par{'upload_customize'});
        foreach( @tmp ){
            $_ =~ s/\r//g;
            if( $_ eq '' ){  next;  }    # 过滤掉前台填写的'空'值，否则后台就会保存为多个'.'这样的行,反过来又会显示在页面上
            else {
                $_ = ".".$_;
                push(@items, $_);
            }
        }
        $record = join( "\n", @items );
        ( $status, $mesg ) = &append_one_record( $upload_filter_path, $record ); # 其实你这里实现的是一次添加了多行！因为$record把所有的行用换行符连接起来
        if($status != 0) {    $errormessage = "保存失败";    return;        }

    my @filter_arr = split(/\|/,$par{'DOWNLOAD_FILTER'} );
    foreach my $filter( @filter_arr ){
        $record = ".".$filter;
        ( $status, $mesg ) = &append_one_record( $download_filter_path, $record );  #要改成写入两个配置文件
        if($status != 0) {    $errormessage = "保存失败";    return;        }
    }
        # $record = $par{'download_customize'};
        # $record =~ s/\r//g;
        my @tmp = split(/\n/, $par{'download_customize'});
        @items = ();   # 清空
        foreach( @tmp ){
            $_ =~ s/\r//g;
            if( $_ eq '' ){  next;  }    # 过滤掉前台填写的'空'值，否则后台就会保存为多个'.'这样的行,反过来又会显示在页面上
            else {
                $_ = ".".$_;
                push(@items, $_);
            }
        }
        $record = join( "\n", @items );
        ( $status, $mesg ) = &append_one_record( $download_filter_path, $record ); # 其实你这里实现的是一次添加了多行！同上
        if($status != 0) {
            $errormessage = "保存失败";    return;
        }else{
            $notemessage = "保存成功";
        }

}

sub show_page() {
    &openpage(_('文件类型过滤'), 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &closebigbox();
    &openbox('100%', 'left', '文件类型过滤');

    &display_main_body();

    &closebox();
    &check_form();
    &closepage();
}

sub display_main_body() {
    my $upload_exe_checked,$upload_pdf_checked, $upload_ppt_checked,$upload_doc_checked,$upload_docx_checked,
    $upload_dat_checked, $upload_tar_checked, $upload_zip_checked, $upload_html_checked, $upload_rar_checked;
    my $upload_textarea;

    my $download_exe_checked, $download_pdf_checked, $download_ppt_checked, $download_doc_checked, $download_docx_checked,
    $download_dat_checked, $download_tar_checked, $download_zip_checked, $download_html_checked, $download_rar_checked;
    my $download_textarea;

    my @lines_arr = ();  my $customize = "";
    &read_config_lines( $upload_filter_path, \@lines_arr );
    foreach my $item( @lines_arr ){
        if($item eq ".exe"){
            $upload_exe_checked = ' checked="checked" ';
        }elsif($item eq ".pdf"){
            $upload_pdf_checked = ' checked="checked" ';
        }elsif($item eq ".ppt"){
            $upload_ppt_checked = ' checked="checked" ';
        }elsif($item eq ".doc"){
            $upload_doc_checked = ' checked="checked" ';
        }elsif($item eq ".docx"){
            $upload_docx_checked = ' checked="checked" ';
        }elsif($item eq ".dat"){
            $upload_dat_checked = ' checked="checked" ';
        }elsif($item eq ".tar"){
            $upload_tar_checked = ' checked="checked" ';
        }elsif($item eq ".zip"){
            $upload_zip_checked = ' checked="checked" ';
        }elsif($item eq ".html"){
            $upload_html_checked = ' checked="checked" ';
        }elsif($item eq ".rar"){
            $upload_rar_checked = ' checked="checked" ';
        }else{
            # $customize += $item."\n";  # perl不支持'+='运算符！导致计算后 $customize 的值就是0
            # $customize = $customize.$item.'\n';  用单引号是非常错误的！
            # $customize = $customize.$item."\n";
            $item =~ /\.(.*)/;
            $customize = $customize.$1."\n";
        }
    }
    $upload_textarea = $customize;

    @lines_arr = ();  $customize = "";  #清空$customize里的内容！
    &read_config_lines( $download_filter_path, \@lines_arr );
    foreach my $item( @lines_arr ){
        if($item eq ".exe"){
            $download_exe_checked = ' checked="checked" ';
        }elsif($item eq ".pdf"){
            $download_pdf_checked = ' checked="checked" ';
        }elsif($item eq ".ppt"){
            $download_ppt_checked = ' checked="checked" ';
        }elsif($item eq ".doc"){
            $download_doc_checked = ' checked="checked" ';
        }elsif($item eq ".docx"){
            $download_docx_checked = ' checked="checked" ';
        }elsif($item eq ".dat"){
            $download_dat_checked = ' checked="checked" ';
        }elsif($item eq ".tar"){
            $download_tar_checked = ' checked="checked" ';
        }elsif($item eq ".zip"){
            $download_zip_checked = ' checked="checked" ';
        }elsif($item eq ".html"){
            $download_html_checked = ' checked="checked" ';
        }elsif($item eq ".rar"){
            $download_rar_checked = ' checked="checked" ';
        }else{
            # $customize = $customize.$item.'\n';
            # $customize = $customize.$item."\n";
            $item =~ /\.(.*)/;
            $customize = $customize.$1."\n";
        }
    }
    $download_textarea = $customize;

    printf<<EOF
    <form name="UPLOAD_FILTER_FORM" enctype="multipart/form-data" method="post" action="$ENV{SCRIPT_NAME}">
      <table width="600px;" border='0px;' cellspacing="0" cellpadding="4">
        <tr class="odd">
            <td width="380px;">
                <div><span style="color:blue;font-size:14px;">文件上传过滤：</span><div>
                    <div>
                    <input type="checkbox" name="UPLOAD_FILTER" value="exe" $upload_exe_checked > <span>exe</span></input>
                    <input type="checkbox" name="UPLOAD_FILTER" value="pdf" $upload_pdf_checked > <span>pdf</span></input>
                    <input type="checkbox" name="UPLOAD_FILTER" value="ppt" $upload_ppt_checked > <span>ppt</span></input>
                    <input type="checkbox" name="UPLOAD_FILTER" value="doc" $upload_doc_checked > <span>doc</span></input>
                    <input type="checkbox" name="UPLOAD_FILTER" value="docx" $upload_docx_checked > <span>docx</span></input>
                    </div>
                    <div>
                    <input type="checkbox" name="UPLOAD_FILTER" value="dat" $upload_dat_checked > <span>dat</span></input>
                    <input type="checkbox" name="UPLOAD_FILTER" value="tar" $upload_tar_checked> <span>tar</span></input>
                    <input type="checkbox" name="UPLOAD_FILTER" value="zip" $upload_zip_checked> <span>zip</span></input>
                    <input type="checkbox" name="UPLOAD_FILTER" value="html" $upload_html_checked> <span>html</span></input>
                    <input type="checkbox" name="UPLOAD_FILTER" value="rar" $upload_rar_checked> <span>rar</span></input>
                    </div>
                    <div class="customize_tip" style="dispaly:block;">用户自定义（每行一个）：</div>
                    <div> </div>
                    <div>
                    <textarea  name="upload_customize" style="width:320px;height:120px;dispaly:block;">$upload_textarea</textarea>
                    </div>
                
            </td>
            <td width="380px;">
                <div><span style="color:blue;font-size:14px;">文件下载过滤：</span><div>
                    <div>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="exe" $download_exe_checked > <span>exe</span></input>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="pdf" $download_pdf_checked > <span>pdf</span></input>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="ppt" $download_ppt_checked > <span>ppt</span></input>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="doc" $download_doc_checked > <span>doc</span></input>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="docx" $download_docx_checked > <span>docx</span></input>
                    </div>
                    <div>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="dat" $download_dat_checked > <span>dat</span></input>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="tar" $download_tar_checked > <span>tar</span></input>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="zip" $download_zip_checked > <span>zip</span></input>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="html" $download_html_checked > <span>html</span></input>
                    <input type="checkbox" name="DOWNLOAD_FILTER" value="rar" $download_rar_checked > <span>rar</span></input>
                    </div>
                    <div class="customize_tip" style="dispaly:block;">用户自定义（每行一个）：</div>
                    <div> </div>
                    <div>
                    <textarea  name="download_customize"  style="width:320px;height:120px;dispaly:block;">$download_textarea</textarea>
                    </div>
            </td>
        </tr>

        <tr class="table-footer">
            <td colspan="2">
                <input  type='submit' name='submit' class="net_button" value='保存' />
                <input  type="hidden" name="ACTION" value="save_data" />
            </td>
        </tr>
    </table>
</form>

    
EOF
    ;
}

sub check_form(){

}