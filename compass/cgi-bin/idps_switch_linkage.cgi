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
my $conf_switch_file = $conf_dir.'/respond_switch';
my $switch_type_file = $conf_dir.'/switch_type.json';
my $reload = 0;    
my %par;
my $extraheader;
my $errormessage = "";
my $notemessage ="";

sub display(){         
    
openbox('100%', 'left', _('交换机联动'));
printf <<EOF
    <form name="SWITCH_LINKAGE_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="env">
    <td class="add-div-type">%s </td>
    <td><select style="width:120px" id="switches_type" name='switches_type'></select></td>
    </tr>
    <tr class="odd">
    <td class="add-div-type">%s</td>
    <td><select style="width:120px" id="linkage_way_switch" name='linkage_way_switch'></select></td>
    </tr>
    <tr class="env">
    <td  class="add-div-type">%s</td>
    <td><input type="text" name='ip_addr_switch' id="ip_addr_switch"/></td>
    </tr> 
    <tr class="odd">
    <td  class="add-div-type">%s</td>
    <td><input type="text" name='port_switch' id="port_switch"/></td>
    </tr>
    <tr class="env">
    <td  class="add-div-type">%s</td>
    <td><input type="checkbox" name='start_switch' value="on" id="start_switch" onclick="change_account_input()"/>启用
    <div style="margin-top:10px">账户*&nbsp;&nbsp;<input type="text" name="account_switch" id="account_switch"/></div>
    <div style="margin-top:10px">密码*&nbsp;&nbsp;<input type="password" name="pwd_switch" id="pwd_switch"/></div>
    </td>
    </tr>
EOF
, _('交换机类型')
, _('联动方式')
, _('IP*')
, _('端口*')
, _('身份验证')
;    
printf <<EOF    
  <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save_switch"></input>
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
    if($action eq 'save_switch') {
        my @data_email;
        my @conf_template_fileds = ("switches_type","linkage_way_switch","ip_addr_switch","port_switch","start_switch","account_switch","pwd_switch");
        my @conf_keys = ("TYPE","MODE","IPADDR","PORT","VERIFCATION","USER","PASS");
        my $length = @conf_keys;
        for(my $i=0;$i<$length;$i++){
            if($conf_template_fileds[$i] eq 'start_switch'){
                my $temp = $par{$conf_template_fileds[$i]};
                if(defined($temp)){
                    $par{$conf_template_fileds[$i]} = 'on';
                }else{
                    $par{$conf_template_fileds[$i]} = 'off';
                }
            }
            
            my $item = $conf_keys[$i].'='.$par{$conf_template_fileds[$i]};
            push (@data_email,$item)
        }
        &save_data_to_file(\@data_email,$conf_switch_file);
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
        &openpage(_('交换机联动'),1,$extraheader); 
        &openbigbox($errormessage,$warnmessage,$notemessage);
        &display();
        &closebigbox();
        &closepage();
    }
}

sub load_type(){
    
    my $result;
    open JFILE,$switch_type_file;
    while (<JFILE>){
        $result.=$_;
    }
    $result =~ s/\r\n//g;
    print $result;
}

sub load_data(){
    my @content_array = ();
    my @lines = read_conf_file($conf_switch_file);
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
    $extraheader = '<script type="text/javascript" charset="gb2312" src="/include/idps_switch_linkage_controller.js"></script>';
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $conf_switch_file){
        `touch $conf_switch_file`;
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