#!/usr/bin/perl
#
#author:刘炬隆（liujulong）
#
#date:2014/05/30
#
#description:事件合并页面
require '/var/efw/header.pl';
my $custom_dir = 'ipslog';
my $conf_dir = '/var/efw/'.$custom_dir;
my $default_dir = $conf_dir.'/default';
my $conf_file = $conf_dir.'/settings';
my $conf_default_file = $default_dir.'/settings';
my $setmerge = '/usr/local/bin/log2sql';
my $reload = 0;
my %par;
my %settings;
my @mergeway;
my %mergeway_value;
my $extraheader;
my $errormessage = "";
my $notemessage ="";

sub display(){
    #&readhash( $conf_default_file, \%settings );
    if( -f $conf_file ) {
        &readhash( $conf_file, \%settings );
    }
openbox('100%', 'left', _('事件合并'));
printf <<EOF
    <form name="EVENT_MERGE_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='1' >
    <tr class="env">
    <td  class="add-div-type">%s</td>
    <td><select style="width:120px" id="mergeway" name='mergeway' value='$settings{'MERGEWAY'}'>
EOF
, _('合并方式：')
;
    foreach my $theway (@mergeway) {
        my $selected = "";
        if($settings{'MERGEWAY'} eq $mergeway_value{$theway}){
            $selected = "selected";
            print "<option selected='$selected' value='$mergeway_value{$theway}'>$theway</option>";
        }else{
            print "<option value='$mergeway_value{$theway}'>$theway</option>";
        }
        
    }
printf <<EOF
    </select>
    </td>
    </tr> 
    <tr class="odd">
    <td  class="add-div-type">%s</td>
    <td><input type="text" id="mergecyle" name='mergecyle' value="$settings{'MERGECYCLE'}"/> （整数：0-120）</td>
    </tr>
    <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save"></input>
        <input type="submit" class="net_button" value="保存" align="middle"/>
    </td>
    </tr>
    </table>
    </form>
EOF
, _('合并周期：')
;
&closebox();

}



sub do_action(){
    my $action = $par{'ACTION'};
    if($action eq 'save') {
        my @data_email;
        my @conf_template_fileds = ("mergeway","mergecyle");
        my @conf_keys = ("MERGEWAY","MERGECYCLE");
        my $length = @conf_keys;
        for(my $i=0;$i<$length;$i++){
            my $item = $conf_keys[$i].'='.$par{$conf_template_fileds[$i]};
            push (@data_email,$item)
        }
        if(! -e $conf_file){
        `touch $conf_file`;
        }
        &save_data_to_file(\@data_email,$conf_file);
        `$setmerge`;
    }

    &showhttpheaders(); 
    &openpage(_('事件合并'),1,$extraheader); 
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
    $extraheader = '<script language="JavaScript" charset="gb2312" src="/include/logs_event_merge_controller.js"></script>';
    @mergeway = ("源地址","目标地址");
    %mergeway_value = ("源地址"=>"SIP","目标地址"=>"DIP");
}
#创建目录和文件
sub make_file(){
    if(! -e $conf_dir){
        `mkdir -p $conf_dir`;
    }
    
    if(! -e $default_dir){
        `mkdir -p $default_dir`;
    }
    
    
    if(! -e $conf_file){
        `touch $conf_file`;
        
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