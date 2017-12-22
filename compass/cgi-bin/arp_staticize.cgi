#!/usr/bin/perl
#
#author:liujulong
#
#date:2014/04/10
#
#description:ARP扫描页面
require '/var/efw/header.pl';
require './endianinc.pl';
my $custom_dir = 'arpsolidify';                             #要保存数据的目录名字 ！！！！要配置，不然路径初始化出问题！！！！            
my $save_dir = '/var/efw/'.$custom_dir;                        #ARP扫描所存放的文件夹
my $save_file = '/var/efw/'.$custom_dir.'/scandfile';
my $conf_file = '/var/efw/arpman/config';
my $settings_ethernet ="/var/efw/ethernet/settings";
my $needreload = '/var/efw/autoarp/needreload';
my $reload = 0;
my $restart = '/usr/local/bin/arp_table -A';
my $cmd_scan = '/usr/local/bin/arpscan';    
my %par;
my %hash_interface;
my $extraheader;
my $errormessage = "";
my $notemessage ="";
my $is_show_list_box = 0;

sub is_valid($) 
{
    my $line = shift;
    if($line =~ /(?:(?:[^,]*),){9}/) 
    {
        return 1;
    }
    return 0;
}
sub read_config_file($) {
    my $filename = shift;
    my @lines;
    open(FILE, "<$filename");
    foreach my $line (<FILE>){
        chomp($line);
        $line =~ s/[\r\n]//g;
        if(is_valid($line)){
            next;
        }
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub get_eth2()
{
    my @all_hash;
    my $green  = `cat /var/efw/ethernet/br0`;
    my $orange = `cat /var/efw/ethernet/br1`;
    my $blue   = `cat /var/efw/ethernet/br2`;
    if($green ne "")
    {
      my $a="br0";
      push(@all_hash,$a);    
    }
    
    if($orange ne " ")
    {
            push(@all_hash,'br1');
    }
    my $temp_cmd = `ip a`;
    my @temp = split(/\n/,$temp_cmd);
    foreach my $line(@temp)
    {
        if(($line =~ /^[0-9]+\: +([a-zA-Z0-9]+)\:/))
        {
            $eth = $1;
            if($eth =~ /^eth/ || $eth =~ /^tap/)
            {
                push(@all_hash,$eth);
                
            }
        }
    }

    return @all_hash;
    
}

sub display(){         
    my $select_block='';
    #my @eth  =  get_eth2();
    
    my @interfaces = get_eth();
    my $green  = `cat /var/efw/ethernet/br0`;
    my $orange = `cat /var/efw/ethernet/br1`;
    my $blue   = `cat /var/efw/ethernet/br2`;
    my @br0s = split(/\n/,$green);
    my @br1s = split(/\n/,$orange);
    my @br2s = split(/\n/,$blue);
    my @ethes_new = ();
    for (my $i=0;$i<@interfaces;$i++){
        foreach(@br0s){
            if($_ eq $interfaces[$i]){
                delete ($interfaces[$i]);
            }
        }
        foreach(@br1s){
            if($_ eq $interfaces[$i]){
                delete ($interfaces[$i]);
            }
        }
        foreach(@br2s){
            if($_ eq $interfaces[$i]){
                delete ($interfaces[$i]);
            }
        }
    }
    if(@br2s > 0){
        unshift(@interfaces,'br2');
    }
    if(@br1s > 0){
        unshift(@interfaces,'br1');
    }
    if($green){
        unshift(@interfaces,'br0');
    }
    
    foreach my $interface (@interfaces)
    {   
        if($interface){
			$select_block.="<option value='$interface' >$interface</option>";
		}
        
    }
 
    openbox('100%', 'left', _('ARP扫描'));
printf <<EOF
    <form name="TEMPLATE_FORM"  action="$ENV{'SCRIPT_NAME'}"  method="post">
    <table cellpadding="0" cellspacing="0" width="100%" border='0' >
    <tr class="odd" id="interface">
    <td class="add-div-type">%s </td>
    <td><select name='SECTION' style="width:156px">
EOF
, _('接口*')
;
print $select_block;    
printf <<EOF    
    </select>
    </td>
    </tr>
    <tr class="env">
    <td class="add-div-type">%s</td>
    <td><input type='text' name='ip_start' /></td>
    </tr>
    <tr class="odd" id="local_ip">
    <td  class="add-div-type">%s</td>
    <td><input type='text' name='ip_end'  /></td>
    </tr>  
EOF
, _('起始IP*')
, _('结束IP*')
;    
printf <<EOF    
  <tr class="table-footer">
    <td colspan="2">
      <input type="hidden" class="action" name="ACTION" value="save"></input>
        <input type="submit" class="net_button" value="开始" align="middle"/>
    </td>
  </tr>
  </table>
  </form>
EOF
;
&closebox();
if($is_show_list_box){
    &createArpStaticBox();
}
}

sub createArpStaticBox(){
    my @table_display_fields = ("IP地址", "MAC地址"); 
    printf <<EOF
        <div style="margin-top:30px;margin-left:24px;margin-right:25px"> <table border="1" bordercolor="#999999">
                <tr class="table-footer"><td style="text-align:center;font-weight:bold;width:10%">
                <input style="margin-right:20px;" type="checkbox" id="checkall" onclick="select_all()"/></td><td style="text-align:center;font-weight:bold">IP地址</td><td style="text-align:center;font-weight:bold">MAC地址
                </td></tr>        
EOF
;    
    my @datas;
    # my @scan_data = read_conf_file($save_file);
    begin();
    my @scan_data = split(/\n/, `$cmd_scan $par{'ip_start'} $par{'ip_end'} $par{'SECTION'}`);
    ends();
    foreach (@scan_data){
        my @data_line = split(/,/,$_);
        my %line_display = (
            ip => shift(@data_line),
            mac => shift(@data_line),
            interface => shift(@data_line),
            #interface => $par{'SECTION'},
        );
        push (@datas,\%line_display);
    }
    
    foreach (@datas){
        my $ip = ${$_}{'ip'};
        my $mac = ${$_}{'mac'};
        my $interface = ${$_}{'interface'};
        print '<tr style="height:30px;"><td style="text-align:right"><input name="item" style="margin-right:20px;" id="item'.$ip.$mac.'" type="checkbox" value="'.$ip.",".$mac.",".$interface.'" onclick="add_input(this)"/></td><td style="padding-left:9px">'.$ip.'</td><td style="padding-left:9px">'.$mac.'</td></tr>';
    }    
    printf <<EOF            
                <tr class="table-footer"><td colspan="3" align="center">
                <form method="post" id="form_checked" style="float:left;margin-left:500px" ACTION="$ENV{'SCRIPT_NAME'}"><input type="submit" class="net_button" value="固化选中"/><input TYPE="hidden" name="ACTION" value="staticize" /></form>
                <form method="post" style="float:left" ACTION="$ENV{'SCRIPT_NAME'}"><input type="submit" class="net_button" value="撤销"/><input TYPE="hidden" name="ACTION" value="cancel">
                </td></form></tr>
          </table>
          </div>
EOF
;          
}

sub do_action(){
    my $action = $par{'ACTION'};
    if($par{'ACTION'} eq "save" )
    {          
        if (!validip($par{'ip_start'}))
        {
           $errormessage="无效的起始IP地址，请输入正确的IP地址";
        }
        if (!validip($par{'ip_end'}))
        {
           $errormessage="无效的结束IP地址，请输入正确的IP地址";
        }
        $is_show_list_box = 1;
    }
    if ($action eq 'apply') {
        `$restart`;#重启服务
        `rm $needreload`;
        $notemessage = "ARP应用成功";#此行消息可以自定义
        return;
    }
    if($action eq 'staticize'){
        $par{'arp_static'} = lc($par{'arp_static'});
        my @arp_data = split(/[|]/,$par{'arp_static'});
        &save_data_to_file(@arp_data);
        $reload = 1;
        #my $success_data = $par{'arp_static'};
        # print "固化信息：@arp_data";
        # print "固化成功";
    }
}

sub check_form(){
    printf <<EOF
    <script>
    var object = {
    'form_name':'TEMPLATE_FORM',//这里填写表单的名字
    'option'   :{
        'ip_start':{
            'type':'text',
            'required':'1',
            'check':'ip|',
            'ass_check':function(){//这个eve对象是ChinArk_forms对象，如果需要用到其中的函数，可以填写，不一定用eve这个名字，可以用其他名字
                        
            }
        },
        'ip_end':{
            'type':'text',
            'required':'1',
            'check':'ip|',
            'ass_check':function(){
                   
            }
        }
    }
}    
    var check = new ChinArk_forms();
    check._main(object);
    </script>
EOF
;
}
#初始化数据
sub init_data(){
    $extraheader = '<script type="text/javascript" charset="gb2312" src="/include/arp_staticize.js"></script>';
    $extraheader .= '<script type="text/javascript" src="/include/waiting.js"></script>';
}
#创建目录和文件
sub make_file(){
    if(! -e $save_dir){
        `mkdir -p $save_dir`;
    }
    
    if(! -e $save_file){
        `touch $save_file`;
    }
}

#将扫描记录写入文件
sub save_data_to_file(){
    my @add_lines = @_;
    my $filename= $conf_file;
    my @lines = read_conf_file($conf_file);
    push (@lines,@add_lines);
    my %hash;
    @lines = grep{++$hash{$_}<2}@lines;
    open (FILE, ">$filename");
    foreach my $line (@lines) {
        if ($line ne "") {
            print FILE "$line\n";
        }
    }
    close(FILE);
}

sub reload(){
    if ($reload) {
        system("touch $needreload");
    }
    if (-e $needreload) {
        applybox(_("ARP表项已更新，需点击应用以更新规则"));
    }
}

sub begin(){
    printf <<EOF
    <script>
      RestartService("正在执行ARP扫描，需要一定时间，请等待.....");
    </script>
EOF
;
}
sub ends(){
    printf <<EOF
    <script>
      endmsg("ARP扫描完成！");
    </script>
EOF
;
}

&make_file();
&init_data();
&getcgihash(\%par);
&showhttpheaders(); 
&openpage(_('扫描页面'),1,$extraheader);
&do_action(); 
&reload();
&openbigbox($errormessage,$warnmessage,$notemessage);
&display(); 
&check_form();
&closebigbox();
&closepage();
