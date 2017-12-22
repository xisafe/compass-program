#!/usr/bin/perl
#
#author:刘炬隆（liujulong）
#
#date:2014/05/30
#
#description:管理口设置页面
require '/var/efw/header.pl';
my $custom_dir = 'managerinterface';
my $conf_dir = '/var/efw/'.$custom_dir;
my $default_dir = $conf_dir.'/default';
my $conf_file = $conf_dir.'/settings';
my $conf_default_file = $default_dir.'/settings';
my $setmanager = '/usr/local/bin/setmanagerinterface';
my $reload = 0;
my @mask;
my %masknumber;
my %par;
my %settings;
my $extraheader;
my $errormessage = "";
my $notemessage ="";

sub display(){
    &readhash( $conf_default_file, \%settings );
    if( -f $conf_file ) {
        &readhash( $conf_file, \%settings );
    }
openbox('100%', 'left', _('管理口设置'));
printf <<EOF
    <form name="MANAGENMENT_MOUTH_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='1' >
    <tr class="env">
    <td class="add-div-type">%s </td>
    <td><input type="text" name='management_interface' value="eth0" readonly background-color="#dddddd" /></td>
    </tr>
    <tr class="odd">
    <td  class="add-div-type">%s</td>
    <td><input type="text" id="management_ip" name='management_ip' value="$settings{'IPADDR'}"/></td>
    </tr>
    <tr class="env">
    <td  class="add-div-type">%s</td>
    <td><select style="width:120px" id="netmask" name='netmask' value="$settings{'NETMASK'}">
EOF
, _('管理接口')
, _('管理IP')
, _('子网掩码')
;
    foreach my $themask (@mask) {
        my $selected = "";
        if($settings{'NETMASK'} eq $masknumber{$themask}){
            $selected = "selected";
            print "<option selected='$selected' value='$masknumber{$themask}'>$themask</option>";
        }else{
            print "<option value='$masknumber{$themask}'>$themask</option>";
        }
        
    }

printf <<EOF
    </select>
    </td>
    </tr> 
    <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save"></input>
        <input type="submit" class="net_button" value="保存" align="middle"/>
        <!--<input type="reset" class="net_button" value="重置" align="middle"/>-->
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
    if($action eq 'save') {
        my @data_email;
        my @conf_template_fileds = ("management_interface","management_ip","netmask");
        my @conf_keys = ("INTERFACE","IPADDR","NETMASK");
        my $length = @conf_keys;
        for(my $i=0;$i<$length;$i++){
            my $item = $conf_keys[$i].'='.$par{$conf_template_fileds[$i]};
            push (@data_email,$item)
        }
        if(! -e $conf_file){
        `touch $conf_file`;
        }
        &save_data_to_file(\@data_email,$conf_file);
        `$setmanager`;
    }

    &showhttpheaders(); 
    &openpage(_('管理口设置'),1,$extraheader); 
    &openbigbox($errormessage,$warnmessage,$notemessage);
    &display();
    &closebigbox();
    &closepage();
}

sub load_data(){
    my @content_array = ();
    my @lines;
    if(-e $conf_file){
        @lines = read_conf_file($conf_file);
    }else{
        @lines = read_conf_file($conf_default_file);
    }
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
    $extraheader = '<script language="JavaScript" src="/include/manager_interface_controller.js"></script>';
    @mask = (
       "128.0.0.0","192.0.0.0","224.0.0.0","240.0.0.0","248.0.0.0","252.0.0.0",
       "254.0.0.0","255.0.0.0","255.128.0.0","255.192.0.0","255.224.0.0","255.240.0.0",
       "255.248.0.0","255.252.0.0","255.254.0.0","255.255.0.0","255.255.128.0","255.255.192.0",
       "255.255.224.0","255.255.240.0","255.255.248.0","255.255.252.0","255.255.254.0","255.255.255.0",
       "255.255.255.128","255.255.255.192","255.255.255.224","255.255.255.240","255.255.255.248","255.255.255.252",
       "255.255.255.254","255.255.255.255"
);
    %masknumber = (
            "128.0.0.0" => "1",
            "192.0.0.0" => "2",
            "224.0.0.0" => "3",
            "240.0.0.0" => "4",
            "248.0.0.0" => "5",
            "252.0.0.0" => "6",
            "254.0.0.0" => "7",
            "255.0.0.0" => "8",
            "255.128.0.0" => "9",
            "255.192.0.0" => "10",
            "255.224.0.0" => "11",
            "255.240.0.0" => "12",
            "255.248.0.0" => "13",
            "255.252.0.0" => "14",
            "255.254.0.0" => "15",
            "255.255.0.0" => "16",
            "255.255.128.0" => "17",
            "255.255.192.0" => "18",
            "255.255.224.0" => "19",
            "255.255.240.0" => "20",
            "255.255.248.0" => "21",
            "255.255.252.0" => "22",
            "255.255.254.0" => "23",
            "255.255.255.0" => "24",
            "255.255.255.128" => "25",
            "255.255.255.192" => "26",
            "255.255.255.224" => "27",
            "255.255.255.240" => "28",
            "255.255.255.248" => "29",
            "255.255.255.252" => "30",
            "255.255.255.254" => "31",
            "255.255.255.255" => "32",
);
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $default_dir){
        `mkdir -p $default_dir`;
    }
    
    
    if(! -e $conf_default_file){
        `touch $conf_default_file`;
        system("echo INTERFACE=eth0 >> $conf_default_file");
        system("echo IPADDR=192.168.1.254 >> $conf_default_file");
        system("echo NETMASK=1 >> $conf_default_file");
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