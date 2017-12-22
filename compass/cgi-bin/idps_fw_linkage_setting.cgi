#!/usr/bin/perl
#
#author:liujulong
#
#date:2014/05/21
#
#description:响应方式配置页面
require '/var/efw/header.pl';
my $custom_dir = 'ips/respond_type';                             #要保存数据的目录名字 ！！！！要配置，不然路径初始化出问题！！！！            
my $conf_dir = '/var/efw/'.$custom_dir;
my $conf_fw_file = $conf_dir.'/respond_fw';
my $fw_type_file = $conf_dir.'/fw_type.json';

my $reload = 0;    
my %par;
my $extraheader;
my $errormessage = "";
my $notemessage ="";

sub display(){         
     
    openbox('100%', 'left', _('防火墙联动设置'));
printf <<EOF
    <form name="TEMPLATE_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="env">
    <td class="add-div-type">%s </td>
    <td><select style="width:120px" id = "firewall_type" name='firewall_type'></select>
    </td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">%s</td>
    <td><select style="width:120px" id = "linkage_way" name='linkage_way'></select>
    </td>
    </tr>
    <tr class="env">
    <td  class="add-div-type">%s</td>
    <td><input type="text" name='ip_addr' id="ip_addr"/></td>
    </tr> 
    <tr class="odd">
    <td  class="add-div-type">%s</td>
    <td><input type="radio" onclick="change_form()" name='snmp_protocol' checked="checked" value="V1"/>V1<input type="radio" onclick="change_form()" style="margin-left:15px" name='snmp_protocol' value="2C"/>2C
    <input type="radio" style="margin-left:15px" name='snmp_protocol' value="V3" onclick="change_form_another()" />V3
    </td>
    <tr class="env">
    <td  class="add-div-type">%s</td>
    <td><input type="text" name='snmp_group_character' id="group"/></td>
    </tr>
    </tr>
    <tr class="odd" id="tr_uname">
    <td  class="add-div-type">%s</td>
    <td><input type="text" name='user_name' id="uname"/></td>
    </tr>
    <tr class="env" id="tr_level">
    <td  class="add-div-type">%s</td>
    <td><input type="radio" name='auth_level' checked="checked" value="authPriv" onclick="change_form_auth_encry()"/>认证加密<input type="radio" style="margin-left:10px" name='auth_level' value="authNoPriv" onclick="change_form_auth_unencry()"/>认证不加密
    <input type="radio" style="margin-left:10px" name='auth_level' value="noAuthNoPriv" onclick="change_form_nolevel()"/>不认证
    </td>
    </tr>
    <tr class="odd" id="tr_pwd">
    <td  class="add-div-type">%s</td>
    <td><input type="password" name='password' id="pwd"/></td>
    </tr>
    <tr class="env" id="tr_auth">
    <td  class="add-div-type">%s</td>
    <td><select name='auth_method' id="auth_method" style="width:120px">
        <option value="MD5">MD5</option>
        <option value="SHA">SHA</option>
    </select></td>
    </tr>
    <tr class="odd" id="tr_encry_key">
    <td  class="add-div-type">%s</td>
    <td><input type="password" name='encry_key' id="key"/></td>
    </tr>
    <tr class="env" id="tr_encry_method">
    <td  class="add-div-type">%s</td>
    <td><select name='encry_method' id="encry_method" style="width:120px">
        <option value="DES">DES</option>
        <option value="AES">AES</option>
    </select></td>
    </tr>
EOF
, _('防火墙类型')
, _('联动方式')
, _('IP*')
, _('SNMP协议')
, _('SNMP团体字符*')
, _('用户名*')
, _('认证等级')
, _('密码*')
, _('认证算法')
, _('加密密钥*')
, _('加密算法')
;    
printf <<EOF    
  <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save_fw"></input>
        <input type="submit" class="net_button" value="保存" align="middle"/>
    </td>
  </tr>
  </table>
  </form>
EOF
;
&closebox();


}



sub do_action(){
    my $action = $par{'ACTION'};
    if($par{'ACTION'} eq "save_fw" )
    {          
        
        my @data;
        my @conf_template_fileds;
        my @conf_keys;
        if($par{'snmp_protocol'}ne 'V3'){
            @conf_template_fileds = ("firewall_type","linkage_way","ip_addr","snmp_protocol","snmp_group_character");
            @conf_keys = ("TYPE","MODE","IPADDR","PROT","SNMP_COMMUNITY_STRING");
        }else{
            @conf_template_fileds = ("firewall_type","linkage_way","ip_addr","snmp_protocol","snmp_group_character","user_name","auth_level","password","auth_method","encry_key","encry_method");
            @conf_keys = ("TYPE","MODE","IPADDR","PROT","SNMP_COMMUNITY_STRING","USER","LEVEL","PASS","AUTHEN","PASS_ENCRY","ENCRYT");
        }        
        my $length = @conf_keys;
        for(my $i=0;$i<$length;$i++){
            my $item = $conf_keys[$i].'='.$par{$conf_template_fileds[$i]};
            push (@data,$item)
        }
        &save_data_to_file(\@data,$conf_fw_file);
    }elsif($action eq 'load_data') {
        &showhttpheaders(); 
        &load_data();
    }elsif($action eq 'load_type') {
        &showhttpheaders(); 
        &load_type();
    }
    if( $action ne 'load_data' && $action ne 'load_type') {
        $reload = 1;
        &showhttpheaders(); 
        &openpage(_('策略模板'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}

sub load_type(){
    
    my $result;
    open JFILE,$fw_type_file;
    while (<JFILE>){
        $result.=$_;
    }
    $result =~ s/\r\n//g;
    print $result;
    
}

sub load_data(){
    my @content_array = ();
    my @lines = read_conf_file($conf_fw_file);
    
    foreach(@lines){
        my @item = split(/=/,$_);
        my %conf_data;
        %conf_data->{$item[0]} = $item[1];
        push(@content_array,\%conf_data);
    }
    my %ret_data;
    %ret_data->{'detail_data'} = \@content_array;
    %ret_data->{'status'} = 0;#succeed
    if (-e $need_reload) {
        %ret_data->{'reload'} = 1;#Need reload
    } else {
        %ret_data->{'reload'} = 0;
    }
    my $json = new JSON::XS;
    my $ret = $json->encode(\%ret_data);
    print $ret; 
}
#初始化数据
sub init_data(){
    $extraheader = '<script type="text/javascript" charset="gb2312" src="/include/idps_fw_linkage_controller.js"></script>';
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $conf_fw_file){
        `touch $conf_fw_file`;
    }
    
    
}

#将记录写入文件
sub save_data_to_file(){
    my $ref_conf_data = shift;
    my @conf_data = @$ref_conf_data;   
    my $filename= shift;
    
    open (FILE, ">$filename");
    foreach my $line (@conf_data) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
}

&make_file();
&init_data();
&getcgihash(\%par);
&do_action();