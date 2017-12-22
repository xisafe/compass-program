#!/usr/bin/perl

use Spreadsheet::WriteExcel;
use Encode;

require '/var/efw/header.pl';

my $templet = "/var/efw/openvpn/sslvpnusertemp.xls";
my $uploadsetting = "/var/efw/openvpn/uploadsetting";
my $openvpnusers   = '/usr/bin/openvpn-sudo-user';
my $sslvpnuseruploading = "/tmp/sslvpnuseruploading";
my $errorreadflag = "/var/efw/openvpn/errorreadflag";
my $errorreadnote = "/var/efw/openvpn/errorreadnote";
my $uploaderrormessage = "/var/efw/openvpn/";
my $name        = _('OpenVPN server');
my $extraheader     = "<link rel='stylesheet' type='text/css' href='/extjs/resources/css/ext-all.css'>
                    <link rel='stylesheet' type='text/css' href='/include/sslvpn_users.css'>
                    <script type='text/javascript' src='/extjs/ext-debug.js'></script>
                    <script type='text/javascript' src='/include/ajaxfileupload.js'></script>
                    <script language='javascript' type='text/javascript' src='/include/sslvpn_users_management.js'></script>
                    <script language='javascript' type='text/javascript' src='/include/sslvpn_users_opfunc.js'></script>
                    <script language='javascript' type='text/javascript' src='/include/sslvpn_users_func.js'></script>
                    <script language='javascript' type='text/javascript' src='/include/sslvpn_users_submit.js'></script>";
my %par;
my $cgi = new CGI; 
&validateUser();
getcgihash(\%par);
&upload_download();
showhttpheaders();

if( -e $sslvpnuseruploading){
    my $waithingheader = "<link rel='stylesheet' type='text/css' href='/include/sslvpn_users_waiting.css'>
                        <script language='javascript' type='text/javascript' src='/include/sslvpn_users_uploading.js'></script>";
    openpage($name, 1, $waithingheader);
    &show_upload_waiting();
    closepage();
    exit;
}else{
    openpage($name, 1, $extraheader);
    openbigbox($errormessage,"", $notemessage);
    &display_add_orgz();
    &display_add_ugrp();
    &display_add_user();
    &display_upload_user();
    &list_users();
    closebigbox();
    closepage();
}

sub show_upload_waiting(){
    printf <<EOF
        <div id="waiting-top">
            <div id="waiting">
                <div id="wait_upload_msg">
                    用户数据正在上传,请稍后刷新页面...
                </div>
            </div>
        </div>
EOF
;
}

sub upload_download(){
    my $action = $par{'ACTION'};
    #下载用户
    if ($action eq 'download') {
        my $file = $templet;
        if( -e "$file"){
            open(DLFILE, "<$file") || Error('open', "$file");  
            @fileholder = <DLFILE>;  
            close (DLFILE) || Error ('close', "$file"); 
            print "Content-Type:application/x-download\n";  
            print "Content-Disposition:attachment;filename=sslvpnusertemp.xls\n\n";
            print @fileholder;
            exit;
        }
        else{
            print "Content-type:text/html\n\n";
            print qq{<html><head><title>The file doesn't exist.</title></head><body><br/><br/>
                <br/><center><h1>The file does not exist.</h1></center></body></html>};
            exit;
        }
    }elsif ($action eq '下载全部用户') {
        #$notemessage = "下载用户";
        #return;
        my $file = download_all();
        if( -e "$file"){
            open(DLFILE, "<$file") || Error('open', "$file");  
            @fileholder = <DLFILE>;  
            close (DLFILE) || Error ('close', "$file"); 
            print "Content-Type:application/x-download\n";  
            print "Content-Disposition:attachment;filename=sslvpnallusers.xls\n\n";
            print @fileholder;
            exit;
        }
        else{
            print "Content-type:text/html\n\n";
            print qq{<html><head><title>The file doesn't exist.</title></head><body><br/><br/>
                <br/><center><h1>The file does not exist.</h1></center></body></html>};
            exit;
        }
       #应用成功后清空动作
       %par = ();
    }elsif ($action eq 'upload') {
        $uploadname='temp.xls';
        $dir = "/tmp/";
        uploads($uploadname,$dir);
        #应用成功后清空动作
        %par = ();
    }
}


sub download_all {
    my $download_file = '/tmp/all_users.xls';
    my @users = split(/\n/, `$openvpnusers longlist`);
    my @whitelists = split(/\n/, `sudo ResMng -orgq -u -c 所有用户`);
    my $row_num = 1;
    my $sheetName = 'My sheet';
    my $book = new Spreadsheet::WriteExcel( $download_file );
    my $sheet = $book->add_worksheet( $sheetName );
    
    #设置格式
    $sheet->set_column('A:A',8);
    $sheet->set_column('B:B',8);
    $sheet->set_column('C:C',10);
    $sheet->set_column('D:D',20);
    $sheet->set_column('E:E',20);
    $sheet->set_column('F:F',6);
    $sheet->set_column('G:G',12);
    $sheet->set_column('H:H',18);
    $sheet->set_column('I:I',12);
    $sheet->set_column('J:J',12);
    $sheet->set_column('K:K',6);
    $sheet->set_column('L:L',18);
    $sheet->set_column('M:M',6);
    
    my $vhcenter_format = $book -> add_format();
    $vhcenter_format->set_align('center');
    $vhcenter_format->set_align('vcenter');
    
    my $vcenter_format = $book -> add_format();
    $vcenter_format->set_align('vcenter');
    
    #输出表头
    $sheet->write(0, 0,  decode('utf8','用户名'),$vhcenter_format);
    $sheet->write(0, 1,  decode('utf8','密码'),$vhcenter_format);
    $sheet->write(0, 2,  decode('utf8','用户证书序列号'),$vhcenter_format);
    $sheet->write(0, 3,  decode('utf8','备注'),$vhcenter_format);
    $sheet->write(0, 4,  decode('utf8','所属用户组'),$vhcenter_format);
    $sheet->write(0, 5,  decode('utf8','是否加入白名单'),$vhcenter_format);
    $sheet->write(0, 6,  decode('utf8','静态地址'),$vhcenter_format);
    $sheet->write(0, 7,  decode('utf8','本地子网'),$vhcenter_format);
    $sheet->write(0, 8,  decode('utf8','DNS服务器'),$vhcenter_format);
    $sheet->write(0, 9,  decode('utf8','加入域'),$vhcenter_format);
    $sheet->write(0, 10, decode('utf8','是否使用默认网关'),$vhcenter_format);
    $sheet->write(0, 11, decode('utf8','远程网络'),$vhcenter_format);
    $sheet->write(0, 12, decode('utf8','是否启用'),$vhcenter_format);
    
    
    #输出内容
    foreach my $user (@users) {
        my @user_split = split(/:/, $user); 
        my $username = $user_split[0];
        foreach my $whitelist (@whitelists) {
            my @whitelist_split = split(/,/, $whitelist); 
            my $w_username = $whitelist_split[0];
            
            next if ($w_username ne $username);
            
            $username = $user_split[0];
            my $password = '******';
            
            my $user_cert_value = $whitelist_split[2]; #加冒号
            $user_cert_value = &add_maohao($user_cert_value);
            
            my $comments = $whitelist_split[5];
            
            my $group_info = $whitelist_split[7];
            $group_info =~ s/:/\n/g;
            
            my $whitelist = '否';
            $whitelist = '是' if ($whitelist_split[4] eq 'on');
            
            my $static_ip = $user_split[8];
            
            my $explicitroutes = '';
            $explicitroutes = $user_split[7] if ($user_split[8] ne '');
            $explicitroutes =~ s/,/\n/g;
            
            my $custom_dns = '';
            $custom_dns = $user_split[9] if ($user_split[9] ne '');
            $custom_dns =~ s/,/\n/g;
            
            my $custom_domain = '';
            $custom_domain = $user_split[10] if ($user_split[10] ne '');
            
            my $setred = '否';
            $setred = '是' if ($whitelist_split[2] ne 'unsetred');
            
            my $remotenets = '';
            $remotenets = $user_split[5] if ($user_split[5] ne '');
            $remotenets =~ s/,/\n/g;
            
            my $user_enabled = '否';
            $user_enabled = '是' if ($whitelist_split[1] ne 'disabled');
            
            $sheet->write_string($row_num, 0, decode('utf8',$username), $vcenter_format);
            $sheet->write_string($row_num, 1, $password, $vcenter_format);
            $sheet->write_string($row_num, 2, $user_cert_value, $vcenter_format);
            $sheet->write_string($row_num, 3, decode('utf8',$comments), $vcenter_format);
            $sheet->write_string($row_num, 4, decode('utf8',$group_info), $vcenter_format);
            $sheet->write_string($row_num, 5, decode('utf8',$whitelist), $vhcenter_format);
            $sheet->write_string($row_num, 6, $static_ip, $vcenter_format);
            $sheet->write_string($row_num, 7, $explicitroutes, $vcenter_format);
            $sheet->write_string($row_num, 8, $custom_dns, $vcenter_format);
            $sheet->write_string($row_num, 9, $custom_domain, $vcenter_format);
            $sheet->write_string($row_num, 10, decode('utf8',$setred) ,$vhcenter_format);
            $sheet->write_string($row_num, 11, $remotenets,$vcenter_format);
            $sheet->write_string($row_num, 12, decode('utf8',$user_enabled), $vhcenter_format);
            $row_num++;
            last;
        }
    }
    $book->close();
    return $download_file;
}

sub add_maohao($){
    my $line = shift;
    my $return_line;
    if(length($line)<=2)
    {
       return $line;
    } else {
       $return_line = substr($line,0,2);
       $line = substr($line,2,length($line)-2);
       do{
          $return_line .= ":";
          $return_line .= substr($line,0,2);
          $line = substr($line,2,length($line)-2);
       } while (length($line)>=2)
    }
    return $return_line;
}

sub uploads($$){
    my $uploadname = shift;
    my $upload_dir = shift;
    my $file_length = 0;
    my $upload_filehandle = $cgi->param('upload_name');
    my $upload_filename = $upload_filehandle;
    my @splited_filenames = split(/\./, $upload_filename);
    foreach my $splited_filename (@splited_filenames)
    {
        $file_length++;
    }
    if($file_length == 0)
    {
        $errormessage = '请选择一个xls文件再上传！';
    } else {
        $file_length--;
        if ($splited_filenames[$file_length] eq 'xls')
        {
            my $filename = $upload_dir.$uploadname;
            open ( UPLOADFILE, ">$filename" ) or die "$!";
            binmode UPLOADFILE;
            while ( <$upload_filehandle> )
            {
                print UPLOADFILE;
            }
            close UPLOADFILE;
            #调用上传之前要保存配置信息
            if(!-e $uploadsetting){
                `touch $uploadsetting`;
            }
            my %uploadsetting;
            $uploadsetting{'DEFAULTGROUP'} = $par{'upload_group_info'};
            $uploadsetting{'COVERUSER'} = '';
            if($par{'conflict_policy'} eq 'cover'){
                $uploadsetting{'COVERUSER'} = 'on';
            }
            &writehash("$uploadsetting", \%uploadsetting);
            
            #开始添加用户
            `touch $sslvpnuseruploading`;
            system('/usr/local/bin/openvpn_users_upload &');
        } else {
            $errormessage = '只支持处理xls文件！';
        }
    }
}

sub display_add_orgz(){
    #添加组织结构
    printf <<EOF
<div id="add-div-orgz" >
    <div id="add-div-header-orgz">
        <span style="display:block;float:left;margin:0px auto auto 10px;"><img src="/images/add.png" /><span>添加组织结构</span></span>
    </div>
    <div id="add-div-content-orgz"  style="display:none">
        <form name="USER_FORM_ORGZ" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
            <!--此table是为了消除Firefox中内容漂移问题-->
            <table></table>
            <table width="100%" cellpadding="0" cellspacing="0" >
                <tbody>
                    <tr class="env">
                        <td class="add-div-type">组织名称*</td>
                        <td>
                            <input type="text" MaxLength="50" id="orgz_name" name="orgz_name" value=""/>
                        </td>
                    </tr>
                    <tr class="odd" >
                        <td class="add-div-type">描述</td>
                        <td >
                            <textarea id="orgz_description" style="height:150px;width:400px;" name="orgz_description" ></textarea>
                        </td>
                    </tr>
                    <tr class="env">
                        <td class="add-div-type">所属上级*</td>
                        <td >
                            <input id="orgz_belong_to" name="orgz_belong_to" style="width:400px;" readonly onClick="createTreeWindow('orgz_belong_to')" ></input>
                        </td>
                    </tr>
                    <tr class="odd hidden">
                        <td class="add-div-type">是否启用</td>
                        <td>
                            <input type="checkbox" id="orgz_enable" name="orgz_enable" style="vertical-align:middle;padding:0px;margin:0px;" checked>
                            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">启用</label>
                        </td>
                    </tr>       
                </tbody>
            </table>
            <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
                <tr class="add-div-footer">
                    <td width="50%">
                        <input class='net_button' type='button' id="openvpn_users_submit_orgz" value='添加' style="display:block;float:right;color:black" />
                    </td>
                    <td width="50%">
                        <input class='net_button' type='button'  value='撤销' style="display:block;float:left;color:black" onclick="cancelAddOrEditOrgz();"/>
                        <span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
                        <input type="hidden" class="form" name="color" value=""  />
                    </td>
                </tr>
            </table>
        </form> 
    </div>
</div>
EOF
;
}

sub display_add_ugrp(){
    #添加用户组
    printf <<EOF
<div id="add-div-ugrp" >
    <div id="add-div-header-ugrp">
        <span style="display:block;float:left;margin:0px auto auto 10px;"><img src="/images/add.png" /><span>添加用户组</span></span>
    </div>
    <div id="add-div-content-ugrp"  style="display:none">
        <form name="USER_FORM_UGRP" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
            <!--此table是为了消除Firefox中内容漂移问题-->
            <table></table>
            <table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
                <tbody>
                    <tr class="env">
                        <td class="add-div-type">用户组名称*</td>
                        <td>
                            <input type="text" MaxLength="50" id="ugrp_name" name="ugrp_name" value=""/>
                        </td>
                    </tr>
                    <tr class="odd" >
                        <td class="add-div-type">描述</td>
                        <td >
                            <textarea id="ugrp_description" name="ugrp_description" style="height:150px;width:400px;" ></textarea>
                        </td>
                    </tr>
                    <tr class="env">
                        <td class="add-div-type">关联资源</td>
                        <td >
                            <input id="related_resource" name="related_resource"  style="width:400px;" readonly onclick="createResTreeWindow('related_resource');"></input>
                        </td>
                    </tr>
                    <tr class="odd">
                        <td class="add-div-type">所属组织*</td>
                        <td >
                            <input id="ugrp_belong_to" name="ugrp_belong_to" style="width:400px;" readonly onClick="createTreeWindow('ugrp_belong_to')" ></input>
                        </td>
                    </tr>
                    <tr class="env  hidden">
                        <td class="add-div-type">是否启用</td>
                        <td>
                            <input type="checkbox" id="ugrp_enable" name="ugrp_enable" style="vertical-align:middle;padding:0px;margin:0px;" checked>
                            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">启用</label>
                        </td>
                    </tr>       
                </tbody>
            </table>
            <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
                <tr class="add-div-footer">
                    <td width="50%">
                        <input class='net_button' type='button' id="openvpn_users_submit_ugrp" value='添加' style="display:block;float:right;color:black"/>
                    </td>
                    <td width="50%">
                        <input class='net_button' type='button'  value='撤销' style="display:block;float:left;color:black" onclick="cancelAddOrEditUgrp();"/>
                        <span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
                        <input type="hidden" class="form" name="color" value=""  />
                    </td>
                </tr>
            </table>
        </form>     
    </div>
</div>
EOF
;
}

sub display_add_user(){
    
    ####help_msg
    my $help_hash1 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","通过vpn引导客户流量","-10","30","down");
    my $help_hash2 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","networt_behind_client","-10","30","down");
    my $help_hash3 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","push_only_these_net","-10","30","down");
    my $help_hash4 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","推送域名服务器","-10","30","down");
    my $help_hash5 = read_json("/home/httpd/help/openvpn_users_help.json","openvpn_users.cgi","推送域","-10","30","down");
    
    ##添加或者编辑用户控件
    printf <<EOF
<div id="add-div" >
    <div id="add-div-header">
        <span style="display:block;float:left;margin:0px auto auto 5px;"><img src="/images/add.png" /><span>添加用户</span></span>
    </div>
    <div id="add-div-content"  style="display:none">
        <form enctype="multipart/form-data" name="USER_FORM_NEW" method="post" ACTION="$ENV{'SCRIPT_NAME'}">
            <!--此table是为了消除Firefox中内容漂移问题-->
            <table></table>
            <table border='0' cellspacing="0" cellpadding="4" width="100%">
                <tr class="env">
                    <td class="add-div-table" rowspan="7"><b>账户信息</b></td>
                    <td>用户名*</td><td><input type="text" id="username" name="username" value="" /></td>
                    <tr class="odd">
                        <td >密码*</td>
                        <td><input type='password' id="password"  name='password'  value='' /></td>
                    </tr>
                    <tr class="env">
                        <td>确认密码*</td>
                        <td><input type='password' id="password2" name='password2' value='' /></td>
                    </tr>
                    <tr class="odd">
                        <td>用户证书*</td>
                        <td>
                            <select  id="user_cert"  name="user_cert" onchange="change_cert_type()" style="width:136px">
                                <option value="upload" >上传</option>
                                <option value="input" >输入证书序列号</option>
                                <option value="none" selected>暂不设置</option>
                            </select>
                            <span id="user_cert_file" class="hidden">
                                <input type="file" name="cert_file" id="cert_file" onchange="cert_upload();"/>
                                <input type="text" style="display:none;width:200px;" name="cert_file_value" id="cert_file_value" value="" readonly />
                                <input type="button" style="display:none;" name="cert_file_reset" id="cert_file_reset" value="重新上传" onclick="reset_upload();"/>
                            </span>
                            <span id="user_cert_input" class="hidden"><input type="text" name="cert_sn" id="cert_sn" value="" style="width:200px;"/></span>
                            <span id="user_cert_hidden"><input type="hidden" name="ori_cert_type" id="ori_cert_type" value=""/></span>
                       </td>
                    </tr>
                    <tr class="env">
                        <td>备注 </td>
                        <td><input id="comments" name="comments" type="text" value="" maxlength="20" style="width:136px;"/></td>
                    </tr>
                    <tr class="odd">
                        <td>所属组结构</td>
                        <td>
                            <div id="group_infos"></div>
                            <div class="multi_line"><img id="add_group_info" src="/images/add16x16.png" onClick="createInput('group_infos','group_info')"/></div>
                        </td>
                    </tr>
                    <tr class="env">
                       <td>是否加入白名单</td>
                       <td><input type="checkbox" id="whitelist" name="whitelist" checked/>加入白名单</td>
                    </tr>
                    <tr class="odd">
                        <td class="add-div-table" rowspan="7">接入时用户计算机设置</td>
                        <td width="300px">地址分配</td>
                        <td>
                            <div class="multi_line">
                                <input type="radio" name="addresschoose" value="autoset" style="vertical-align:middle;" onchange="address_choose();" checked/>
                                <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">自动分配</label>
                            </div>         
                            <p class="multi_line">
                                <input type="radio" name="addresschoose" value="byhand" style="float:left;margin-left:5px;vertical-align:middle;" onchange="address_choose();"/>
                                <label style="float:left;vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">&nbsp;手动设置</label>
                                <label style="float:left;vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;display:none;" id="ipaddress_text">IP地址：*</label>
                                <label style="float:left;vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;" id="ipaddress_label">
                                    <input type="text" name="static_ip" id="ipaddress" value="" style="float:left;vertical-align:middle;width:100px;display:none;"/>
                                </label>
                        </td>
                    </tr>
                </tr>
                <tr  class="env">
                    <td class="need_help" width="300px">本地子网 </td>
                    <td class="need_help"><textarea id="explicitroutes" cols="17" rows="2" name='explicitroutes' style="width:153px"></textarea>$help_hash3</td>
                </tr>
                <tr  class="odd" >
                    <td class="need_help">接入时用户计算机使用右边的DNS服务器地址 </td>
                    <td class="need_help">
                        <div class="multi_line">
                            <input type="checkbox" id="push_custom_dns" name="push_custom_dns" style="vertical-align:middle;padding:0px;margin:0px;" onchange="start_dns();" />
                            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">启用</label>
                        </div>
                        <p id="first_dns_display" style="display:none;">
                            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">首选DNS服务器：*</label>
                            <input type="text" id="firstdns" name="main_dns" value="" style="vertical-align:middle;padding:0px;margin:0px;" />
                        </p>
                        <p id="second_dns_display" style="display:none;margin-top:1px;margin-bottom:2px;">
                            <label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">备选DNS服务器：*</label>
                            <input type="text" id="seconddns" name="second_dns" value="" style="vertical-align:middle;padding:0px;margin:0px;" />
                        </p>$help_hash4
                    </td>
                </tr>
                <tr  class="env" >
                    <td class="need_help">接入时将用户计算机加入此域 </td>
                    <td valign="top" class="need_help">
                        <input type='checkbox' id="push_custom_domain" name='push_custom_domain' value='on' ></input>
                        <input type="text" id="custom_domain" name='custom_domain' value="" />$help_hash5
                    </td>
                </tr>
                <tr class="odd">
                    <td class="need_help">接入时用户计算机使用此服务器作为默认网关 </td>
                    <td class="need_help"><input type="checkbox" id="setred" name="setred" value="set" checked>启用 $help_hash1</td>
                </tr>
                <tr  class="env">
                    <td class="need_help">远程网络 </td>
                    <td class="need_help"><textarea id="remotenets" cols="17" rows="2" name='remotenets' style="width:153px"></textarea>$help_hash2</td>
                </tr>
                <tr class="odd">
                    <td class="need_help">此账户是否启用 </td>
                    <td class="need_help"><input type="checkbox" id="user_enabled"　name="user_enabled" value="set" checked>启用 $help_hash1</td>
                </tr>
            </table>
            <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
                <tr class="add-div-footer">
                    <td width="50%">
                        <input class='net_button' type='button' value='添加' style="display:block;float:right;color:black" id="openvpn_users_submit" />
                    </td>
                    <td width="50%">
                        <input class='net_button' type='button'  value='撤销' style="display:block;float:left;color:black" onclick="cancelAddOrEdit();"/>
                        <span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
                        <input type="hidden" class="form" name="color" value=""  />
                    </td>
                </tr>
            </table>
        </form>     
    </div>
</div>
EOF
;
}

sub display_upload_user(){
    #先检查用户是否已查看了错误信息
    my $error_read_img = 'read_note.png';
    if(-e $errorreadflag){
        $error_read_img = 'error_note.png';
    }
    my $title_msg = "查看导入用户的错误信息";
    if(-e $errorreadnote){
        open(ERRORNOTE, "<$errorreadnote");
        my @notemsg = <ERRORNOTE>;
        close(ERRORNOTE);
        $title_msg = $notemsg[0];
        chomp($title_msg);
    }

    printf <<EOF
<div id="add-div-upload" >
    <div id="add-div-header-upload">
        <span id="add-div-header-leftspan-upload" style="display:block;float:left;margin:0px auto auto 10px;"><img src="/images/add.png" /><span>导入用户</span></span>
        <span id="add-div-header-rightspan-upload" style="display:block;float:right;margin:0px 10px auto auto;">
            <form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
                * 请严格按照模板创建新用户数据，只支持处理xls表格。
                <input type="submit" value="下载模板" style="width:80px"><input type="hidden" name='ACTION' value="download" />
                &nbsp;&nbsp;<a href="error_upload_users.cgi" target="_blank"><img src="/images/$error_read_img" title="$title_msg" onclick="error_read();"/></a>
            </form>
        </span>
    </div>
    <div id="add-div-content-upload"  style="display:none">
        <form name="USER_FORM_UPLOAD" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
            <!--此table是为了消除Firefox中内容漂移问题-->
            <table></table>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tbody>
                    <tr class="env">
                        <td class="add-div-type">选择文件*</td>
                        <td>
                            <input type="file" id="upload_name" name="upload_name"/>
                        </td>
                    </tr>
                    <tr class="odd" >
                        <td class="add-div-type">默认分组</td>
                        <td >
                            <input type="text" id="upload_group_info" name="upload_group_info"  style="width:400px;"  readonly onClick="createTreeWindow('upload_group_info')"/>
                        </td>
                    </tr>
                    <tr class="env">
                        <td class="add-div-type">对本地存在的用户</td>
                        <td >
                            <div class="multi_line">
                                <input type="radio" name="conflict_policy" value="cover" style="vertical-align:middle;" onchange="" checked/>&nbsp;继续导入，覆盖已存在的用户
                            </div> 
                            <div class="multi_line">
                                <input type="radio" name="conflict_policy" value="skip" style="vertical-align:middle;" onchange=""/>&nbsp;跳过，不导入该用户
                            </div> 
                        </td>
                    </tr>       
                </tbody>
            </table>
            <table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
                <tr class="add-div-footer">
                    <td width="50%">
                        <input class='net_button' type='submit' id="openvpn_users_submit_upload" value='上传' style="display:block;float:right;color:black" />
                        <input type='hidden' name="ACTION" value='upload' style="display:block;float:right;color:black" />
                    </td>
                    <td width="50%">
                        <input class='net_button' type='button'  value='撤销' style="display:block;float:left;color:black" onclick="cancelAddOrEditUpload();"/>
                        <span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
                        <input type="hidden" class="form" name="color" value=""  />
                    </td>
                </tr>
            </table>
        </form> 
    </div>
</div>
EOF
;
}

##用户列表将挂载在这里
sub list_users() {
printf <<EOF
    <div id='openvpn_users_list'></div>
EOF
;
}
