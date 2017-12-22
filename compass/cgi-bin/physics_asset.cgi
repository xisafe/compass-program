#!/usr/bin/perl
#file:物理资产识别页面
#author:周圆

my  %par;
require '/var/efw/header.pl';
my $show = "";
my $action = "";
my $line = "";
my $hash = ();
my $date = "";
my $errormessage =  "";
my $warnmessage  =  "";
my $notemessage  =  "";
my @errormessages = ();
my $line_node = "0";
my @up_ary = ();
my $url =  $ENV{'SCRIPT_NAME'};
my $test;
my $add_id = '0';
my $ini_name = "ChinArk 东方舟网络威胁综合管理系统";
my %node_type  = (
	"router"   => "路由器",
	"switcher" => "交换机",
	"host"     =>"主机"
);


my $config = '/var/efw/risk/config';            	   #后台扫描后生成的数据
my $config_temp = '/var/efw/risk/physic/web.config';    #前台传给后台的数据
my $logic_config = '/var/efw/risk/logic/config';

#逻辑视图和物理视图连接文件
my $temp_add_router = '/var/efw/risk/map/addrouter';
my $temp_add_host = '/var/efw/risk/map/addhost';
my $temp_del_host = '/var/efw/risk/map/delhost';
my $temp_my = '/var/efw/risk/map/my_addrouter';

my $state= '/var/efw/risk/physic/state'; 
my $scan = '/usr/bin/networkTopoFound/programe/topoFound.sh';#后台运行脚本

my %green_eth;
my %orange_eth;

sub write_config($$)
{
	my $dir = shift;
	my $str = shift;
	open(FILE,">".$dir);
	print FILE $str;
	close FILE;
}

sub read_file($)
{
	my $file =shift;
	my $string = "";
	open(MYFILE,"$file");
	foreach my $line (<MYFILE>) 
	{
		chomp($line);
		$line =~ s/\s//g;
		$line =~ s/\r//g;
		$line =~ s/\n//g;
		$string .= $line;
	}
	close (MYFILE);
	return $string;
}

sub read_file_ary($) {
	my $file =shift;
    my @lines;
    open (FILE, $file);
    foreach my $line (<FILE>) {
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}


sub _hashToJSON {
    my $hashref = shift;
    my %hash = %$hashref;
    my $json = '{';
    my @key_value_pairs = ();
    foreach $key (keys %hash) {
		if(($value = _hashToJSON($hash{$key})) ne '{}')
		{
			push(@key_value_pairs, sprintf("\"%s\": %s ",$key,$value));
		}else{
			$value = $hash{$key};
			push(@key_value_pairs, sprintf("\"%s\": \"%s\"", $key,$value));
		}
    }
    $json .= join(',', @key_value_pairs);
    $json .= '}';
    return $json;
}

sub save()
{
	if($ENV{'QUERY_STRING'} =~ /^line_node=(.*)$/)
	{
		$line_node = $1;
	}
	
	if($ENV{'QUERY_STRING'} =~ /^action=(.*)&&line=(.*)$/)
	{
		$action = $1;
		$add_id = $2;
	}
	
	if($par{'ACTION'})
	{
		$action = $par{'ACTION'};
	}
	
	if($par{'LINE'})
	{
		$line   = $par{'LINE'};
	}
	
		my $type = $par{'TYPE'};
		my $ip = $par{'IP'};
		my $ip_mask = $par{'IP_MASK'};
		$ip_mask =~ s/\r//g;
		$ip_mask =~ s/\n/&&/g;
		my $child_node =  $par{'SWICHER_VALUE'};
		my $hostname = $par{'HOST_NAME'};
		my $father_node = $par{'FATHER_NODE'};


	if($action eq 'add_save' || $action eq 'delete')
	{
		write_if($action,$type,$ip_mask,$ip,$hostname,$child_node,$father_node);#前后台交互接口
	}elsif($action eq 'LOGIC')
	{
		my $string = read_file($config);
		my $logic_hash = JSON::XS->new->decode($string);
		$logic_hash = get_logic_config($logic_hash);
		$logic_hash = update_index($logic_hash);
		$logic_hash = deal_logic_config($logic_hash);
		$logic_hash = add_logic_gloabl($logic_hash);
		my $str = _hashToJSON($logic_hash);
		$str = splace_ary($str);
		write_config($logic_config,$str);
	}elsif($action eq 'UPDATE')
	{
		my $string = read_file($logic_config);
		my $logic_hash = JSON::XS->new->decode($string);
		$logic_hash = update_logic($logic_hash);
		$logic_hash = update_index($logic_hash);
		write_config($logic_config,_hashToJSON($logic_hash));
		`sudo rm /var/efw/risk/map/*`;
	}
	
	if(-e $config)
	{
		my $string = read_file($config);
		$hash = JSON::XS->new->decode($string);
	}
}

sub get_logic_config($)
{
	my $hash = shift;
	my %hash = %$hash;
	foreach my $net(sort keys %hash)
	{
		if($hash{$net}{"type"} eq "switcher" || $hash{$net}{"type"} eq "router")
		{
			my $interface = $hash{$net}{"net"};
			my %interface = %$interface;
			my %new_host = ();
			my %new_net = ();
			
			foreach my $inter(sort keys %interface)
			{
				my $sub_net = $interface{$inter}{"net"};
				my %sub_net = %$sub_net;
				foreach my $sub_nets(sort keys %sub_net)
				{
					$new_net{$sub_nets} = $sub_net{$sub_nets};
				}
				
				my $sub_host = $interface{$inter}{"host"};
				my %sub_host = %$sub_host;
				foreach my $sub_hosts(sort keys %sub_host)
				{
					$new_host{$sub_hosts} = $sub_host{$sub_hosts};
				}
			}

			$hash{$net}{"net"} = \%new_net;
			$hash{$net}{"host"} = \%new_host;
		}
		$hash{$net}{"net"} = get_logic_config($hash{$net}{"net"});
	}
	return \%hash;
}

sub add_logic_gloabl($)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	my $drop = "[0.3, 0.2 ,0.2 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.6 ,0.6 ,0.6 ,0.6 ,0.6 ,0.4 ,0.6 ,0.2 ,0.4 ,0.4 ,0.4 ,0.1 ,0.6 ,0.4 ,0.2 ,0.4 ,0.4 ,0.2 ,0.4 ,0.6 ,0.2 ,0.4 ,0.2 ,0.6 ,0.6 ,0.4]";
	my $pass = "[0.15, 0.1 ,0.1 ,0.2 ,0.2 ,0.2 ,0.2 ,0.2 ,0.2 ,0.3 ,0.3 ,0.3 ,0.3 ,0.3 ,0.2 ,0.3 ,0.1 ,0.2 ,0.2 ,0.2 ,0.05 ,0.3 ,0.2 ,0.1 ,0.2 ,0.2 ,0.1 ,0.2 ,0.3 ,0.1 ,0.2 ,0.1 ,0.3 ,0.3 ,0.2]";
	my %global = (
					"yita_1"=> 0.2,
					"yita_2"=> 0.9998,		
					"decline_step"=> 100,		
					"refresh_time"=> 1,		
					"risk_drop_threshold"=>$drop,
					"risk_pass_threshold"=>$pass
					
	);
	$node_root{"global"} = \%global;
	return \%node_root;
}

#给配置文件添加阈值
sub deal_logic_config($)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	my $weight = "[0.3, 0.3, 0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4 ,0.4]";
	foreach my $net(sort keys %node_root)
	{
		my $host = $node_root{$net}{"host"};
		my %hosts = %$host;
		foreach my $hosts(sort keys %hosts)
		{
			$node_root{$net}{"host"}{$hosts}{"weight"} = $weight;
		}
		$node_root{$net}{"net"} = deal_logic_config($node_root{$net}{"net"});
	}
	return \%node_root;
}

sub splace_ary($)
{
	my $str = shift;
	$str =~ s/\s//g;
	$str =~ s/:"\[/:\[/g;
	$str =~ s/\]"/\]/g;
	$str =~ s/"HASH\([0-9a-zA-Z]+\)"/\{\}/g;
	$str =~ s/,"net":\{\}//g;
	return $str;
}


sub update_logic($)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	
	my $net = $node_root{"0"}{"net"};
	my %net = %$net;
	my $key;
	my %disso = ();
	
	foreach my $sub_net(sort keys %net)
	{
		if($net{$sub_net}{"type"} eq "disso")
		{
			$key = $sub_net;
			last;
		}
	}
		
	if(-e $temp_add_router)
	{
		my $string = read_file($temp_add_router);
		my $router_temp = JSON::XS->new->decode($string);
		$router_temp = get_logic_config($router_temp);
		my %update_router = %$router_temp;
		
		foreach my $update (sort keys %update_router)
		{
			if($key)
			{
				$node_root{"0"}{"net"}{$key}{"net"}{$update} = $update_router{$update};
			}else{
				$node_root{"0"}{"net"}{"disso"}{"net"}{$update} = $update_router{$update};
			}
		}
		`sudo rm $temp_add_router`;
	}
	if(-e $temp_add_host)
	{
		my @temp_ip = read_file_ary($temp_add_host);
		foreach my $ip(@temp_ip)
		{
			my %ip_temp = (
							"type"=>"host",
							"ip"=>$ip,
							"host_name"=>""
			);
			if($key)
			{
				$node_root{"0"}{"net"}{$key}{"host"}{"disso".$ip} = \%ip_temp;
			}else{
				$node_root{"0"}{"net"}{"disso"}{"net"}{"disso".$ip} = \%ip_temp;
			}
		}
		`sudo rm $temp_add_host`;
	}
	if(-e $temp_del_host)
	{
		my @temp_ip = read_file_ary($temp_del_host);
		foreach my $del_ip(@temp_ip)
		{
			del_ip_node(\%node_root,$del_ip);
		}
		`sudo rm $temp_del_host`;
	}
	`sudo rm $temp_my`;
	return \%node_root;
}

sub del_ip_node($$)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	my $ip =shift;

	foreach my $net(sort keys %node_root)
	{
		my $host = $node_root{$net}{"host"};
		my %host = %$host;
		foreach my $hosts(sort keys %host)
		{
			if($host{$hosts}{"ip"} eq $ip)
			{
				delete($host{$hosts});
			}
		}
		$node_root{$net}{"net"} = del_ip_node($node_root{$net}{"net"},$ip);
	}
	return \%node_root;
}

sub begin(){
	printf <<EOF
	<div id="key"></div>
	<script>
	  RestartService("正在扫描当前网络，需要一定时间，请等待.....");
	</script>
EOF
;
}

sub ends(){
	printf <<EOF
	<script>
	  endmsg("网络已经扫描成功");
	</script>
EOF
;
}


#前台传给后台的交互数据
sub write_if($$$$$$$)
{
	my $action = shift;#动作
	my $type = shift;
	my $ip_mask = shift;
	my $ip = shift;
	my $hostname = shift;
	my $child_node = shift;
	my $father_node = shift;
	
	my $str = "";
	if($action eq "add_save")
	{
		if($type eq "router" || $type eq "")
		{
			my @if = split("\\|",$ip_mask);
			my $if_length = @if;
			
			$str .= "addRouter\n";
			$str .= $if_length."\n";
			foreach my $if(@if)
			{
				my @ip = split("&&",$if);
				@ip = array_repeat(\@ip);
				$str .= "interface_start\n";
				foreach my $lines(@ip)
				{
					$str .= $lines."\n";
				}
				$str .= "interface_end\n";
			}
		}elsif($type eq "switcher")
		{
			my @if = split("=",$child_node);
			my $if_length = @if;
			$str .= "addSwitch\n";
			$str .= $father_node."\n";
			$str .= $if_length."\n";
			foreach my $if(@if)
			{
				my @ip = split("\\|",$if);
				$str .= "interface_start\n";
				foreach my $lines(@ip)
				{
					$str .= $lines."\n";
				}
				$str .= "interface_end\n";
			}
		}elsif($type eq "host")
		{
			$str .= "addHost\n";
			$str .= $father_node."\n";
			$str .= $ip."\n";
			$str .= "no\n";
			$str .= "no\n";
			$str .= $hostname."\n";
			$str .= "no\n";
			$str .= "no\n";
		}
	}
	
	if($action eq "delete")
	{
		if($type eq "router")
		{
			$str .= "delRouter\n";
			$str .= $father_node."\n";
		}elsif($type eq "switcher")
		{
			$str .= "delSwitch\n";
			$str .= $father_node."\n";
		}elsif($type eq "host")
		{
			$str .= "delHost\n";
			$str .= $father_node."\n";
		}
	}
	write_config($config_temp,$str);
}


sub get_net_node($$)
{
	my $id = shift;
	my $hashref = shift;
	my %node_root = %$hashref;
	my $node = ();
	
	foreach my $net(sort keys %node_root)
	{
		if(compare($net,$id) == 2 ||compare($net,$id) == 4)#父级节点
		{
			$node_root{$net}{"net"} = get_net_node($id,$node_root{$net}{'net'});
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)<0)#兄弟节点
		{
			next;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)>0)#兄弟节点
		{
			last;
		}elsif(compare($net,$id) == 0)#同一节点
		{
			$node = $node_root{$net};
			%node = %$node;
			last;
		}
	}
	return \%node;
}

sub add_node($$$$$$)
{
	my $hashref = shift;
	my %node_root = %$hashref;
	
	my $type = shift;
	my $ip_mask   = shift;
	
	my $ip  = shift;
	my $child_node = shift;
	my $hostname = shift;
	
	if($type eq "router")
	{
		$ip = $ip_mask;
	}
	if($type eq "host" || $type eq "router")
	{
		$hashref = add_host_router($hashref,$type,$ip,$hostname);
	}elsif($type eq "switcher")
	{
		$hashref = add_switcher($hashref,'',$type,$hostname,$child_node);
		$hashref = update_index($hashref);
	}
	my $str = _hashToJSON($hashref);
	return $str;
}


#添加主机、路由器类型节点
sub add_host_router($$$$)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	
	my $type = shift;
	my $ip = shift;
	my $hostname = shift;
	
	foreach my $net(sort keys %node_root)
	{
		if(compare($net,$line) == 2 || compare($net,$line) == 4)#父级节点
		{
			$node_root{$net}{"net"} = add_host_router($node_root{$net}{"net"},$type,$ip,$hostname);
		}elsif(compare($net,$line) == 5 && brother_distance($net,$line)<0)#兄弟节点
		{
			next;
		}elsif(compare($net,$line) == 0)#同一节点
		{
				my $index = 0;
				my $temp_net = $node_root{$net}{"net"};
				my %temp_nets = %$temp_net;
				my $temp_host = $node_root{$net}{"host"};
				my %temp_hosts = %$temp_host;
				foreach my $temps(keys %temp_hosts){$index++;}
				foreach my $temps(keys %temp_nets){$index++;}
				
				if($type eq "host")
				{
					my %temp = (
								"type" => $type,
								"ip"   => $ip,
								"mac"  => "",
								"host_name" => $hostname
							);
					$node_root{$net}{"host"}{$net."_".$index} = \%temp;	
				}else{
					my %interface = ();
					my @ip = split("\\|",$ip);
					@ip = array_repeat(\@ip);
					my $i = 0;
					foreach my $if(@ip)
					{
						$if=~ s/&&/|/;
						my %if_temp = (
											"type" => "router_if",
											"ip"   => $if
										);
						$interface{$net."_".$index."_".$i} = \%if_temp;
						$i++;
					}
					
					my %temp = (
								"type" => $type,
								"ip"   => "",
								"net"  => \%interface,
								"host_name" => $hostname
							);
					$node_root{$net}{"net"}{$net."_".$index} = \%temp;
				}
				last;#结束遍历
		}
	}
	return \%node_root;
}

#更新节点标号
sub update_index($)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	
	foreach my $net(sort keys %node_root)
	{
		my $sub_host = $node_root{$net}{"host"};
		my %sub_host = %$sub_host;
		
		my $i = 0;
		delete($node_root{$net}{"host"});
		foreach my $host(sort keys %sub_host)
		{
			$node_root{$net}{"host"}{$net."_".$i} = $sub_host{$host};
			$i++;
		}
		
		my $sub_net  = $node_root{$net}{"net"};
		my %sub_net = %$sub_net;
		delete($node_root{$net}{"net"});
		foreach my $nets(sort keys %sub_net)
		{
			$node_root{$net}{"net"}{$net."_".$i} = $sub_net{$nets};
			$i++;
		}
		if($node_root{$net}{"net"} ne "")
		{
			$node_root{$net}{"net"} = update_index($node_root{$net}{"net"});
		}
		if(!exists ($node_root{$net}{"host"}))
		{
			my %temp = ();
			$node_root{$net}{"host"} = \%temp;
		}
	}
	return \%node_root;
}

#将数组消重
sub array_repeat()
{
	my $array_ref = shift;
	my @array = @$array_ref;
	my @new_array;
	my %temp = ();
	foreach my $line(@array)
	{
		$temp{$line} = $line;
	}
	foreach my $line(keys %temp)
	{
		push(@new_array,$line);
	}
	return @new_array;
}

#添加交换机类型节点
sub add_switcher($$$$$)
{
	my $hashref_net = shift;
	my $hashref_host = shift;
	
    my %node_root_net = %$hashref_net;
    my %node_root_host = %$hashref_host;
	
	my $type = shift;
	my $alise = shift;
	
	my $child_node = shift;
	$child_node =~ s/\|/,/g;
	my @child = split(",",$child_node);
	my @host;
	my @net;
	my $str = "";

	#将当前选中的switcher的子节点分别检索放入数组中存储
	foreach my $child(@child)
	{
		if($child=~/^(.*)=host$/)
		{
			push(@host,$1);
		}elsif($child=~/^(.*)=/){
			push(@net,$1);
		}
	}
	my $child_id;
	my $child_type;
	if(($#host ne -1) && ($#net ne -1))
	{
		$child_id    = brother_distance($host[0],$net[0])<0?$host[0]:$net[0];#找出switcher子节点的最小id号
		$child_type  = brother_distance($host[0],$net[0])<0?"host":"net";#找出switcher子节点的最小id号
	}elsif($#host ne -1){
		$child_id   = $host[0];
		$child_type = "host";
	}elsif($#net ne -1){
		$child_id   = $net[0];
		$child_type = "net";
	}
	
	foreach my $net(sort keys %node_root_net)
	{	
		if(compare($net,$child_id) == 2 || compare($net,$child_id) == 4)#父亲节点和爷爷节点
		{
			if(compare($net,$child_id) == 2 && $child_type eq "host")
			{
				my %host = ();
				my %net = ();
				foreach my $host(@host)
				{
					$host{$host} = $node_root_net{$net}{"host"}{$host};
					delete($node_root_net{$net}{"host"}{$host});
				}
			
				foreach my $nets(@net)
				{
					$net{$nets} = $node_root_net{$net}{"net"}{$nets};
					delete($node_root_net{$net}{"net"}{$nets});
				}
			
				my %temp = (
								"type" => "switcher",
								"ip"   => "",
								"mac"  => "",
								"host_name" => $alise,
								"host" => \%host,
								"net"  => \%net
						);
				$node_root_net{$net}{"net"}{$child_id} = \%temp;
				last;
			}else{
				$node_root_net{$net}{"net"}  = add_switcher($node_root_net{$net}{"net"},$node_root_net{$net}{"host"},$type,$alise,$child_node);
			}
		}elsif(compare($net,$child_id) == 5 && brother_distance($net,$child_id)<0)#兄弟节点
		{
			next;
		}elsif(compare($net,$child_id) == 5 && brother_distance($net,$child_id)>0)#兄弟节点
		{
			last;
		}elsif(compare($net,$child_id) == 0)#同一节点
		{
			my %host = ();
			my %net = ();
			foreach my $host(@host)
			{
				$host{$host} = $node_root_host{$host};
				delete($node_root_host{$host});
			}
			
			foreach my $nets(@net)
			{
				$net{$nets} = $node_root_net{$nets};
				delete($node_root_net{$nets});
			}
			
			my %temp = (
								"type" => "switcher",
								"ip"   => "",
								"mac"  => "",
								"host_name" => $alise,
								"host" => \%host,
								"net"  => \%net
						);
			$node_root_net{$net} = \%temp;
			last;
		}
	}
	return \%node_root_net;
}


sub get_father_node($)
{
	my $node = shift;
	if($node =~ /^(.*)(_\d){1}$/)
	{
		return $1;
	}
}

#判断两个节点的关系
sub compare($$)
{
	my $one = shift;
	my $two = shift;
	my $result;
	if($one eq $two)
	{
		$result =  0;#1是2的同一节点
	}elsif($one =~ /^$two(_\d+){1}$/)
	{
		$result =  1;#1是2的孩子节点
	}elsif($two =~ /^$one(_\d+){1}$/)
	{
		$result =  2;#1是2的父亲节点
	}elsif($one =~ /^$two(_\d+){2,}$/)
	{
		$result =  3;#2是1的爷爷节点
	}elsif($two =~ /^$one(_\d+){2,}$/)
	{
		$result =  4;#2是1的孙子重孙节点
	}elsif($one =~ /^(.*)(_\d+){1}$/ && $two =~ /^$1(_\d+){1}$/)
	{
		$result =  5;#1是2的兄弟节点
	}else{
		$result =  6;#1是2的八竿子打不着的关系，路人
	}
	return $result;
}

#获取下一个兄弟节点ID
sub next_node($)
{
	my $id = shift;
	if($one =~ /^(.*)_(\d+)$/)
	{
		return $1."_".$2+1;
	}
}

#两个兄弟节点的间距
sub brother_distance($$)
{
	my $one = shift;
	my $two = shift;
	if(compare($one,$two) == 5)
	{
		my @one = reverse(split("_",$one));
		my @two = reverse(split("_",$two));
		return $one[0]-$two[0];
	}else{
		return;
	}
}

sub delete_node($)
{
	my $hashref = shift;
    my %node_root = %$hashref;

	foreach my $net(sort keys %node_root)
	{
		if($line eq '0')
		{
			$str = "";
		}
		if($line =~ /^(.*)_\d+$/ && $1 eq $net)
		{
			if($node_root{$net}{"net"}){delete ($node_root{$net}{"net"}{$line})};
			if($node_root{$net}{"host"}){delete ($node_root{$net}{"host"}{$line})};
		}else{
			delete_node($node_root{$net}{"net"});
			delete_node($node_root{$net}{"host"});
		}
	}
	my $str = _hashToJSON(\%node_root);
	return $str;
}

#### 将十进制表示的 IP/子网掩码转换成二进制形式
sub ipmask_dec2bin {
    my $prefix = "";
    my $result;
    map { 
		$result .= &dectobin($_); 
    } 
	split (/\./,shift);
	my @temp = split("",$result);
	my $count = 0;
	foreach my $char(@temp)
	{
		if($char eq "1")
		{
			$count++;
		}
	}
	return $count;
}

sub dectobin {
    substr(unpack("B32",pack("N",shift)) , -8);
}

#获取所有网络接口
sub get_eths()
{
	my $cmd = `ifconfig br0`;
	if($cmd =~ /.*inet +addr:(\d+\.\d+\.\d+\.\d+).*Mask:(\d+\.\d+\.\d+\.\d+)[\w\W]+/)
	{
				my $ip   = $1;
				my $mask = $2;
				
				$mask = &ipmask_dec2bin($mask);
				$ip = $ip."/".$mask;
				my %temp = ("ip"=>$ip);
				$green_eth{'br0'} = \%temp;
	}

	my $cmd = `ifconfig br1`;
	if($cmd =~ /.*inet +addr:(\d+\.\d+\.\d+\.\d+).*Mask:(\d+\.\d+\.\d+\.\d+)[\w\W]+/)
	{
				my $ip   = $1;
				my $mask = $2;
				$mask = &ipmask_dec2bin($mask);
				$ip = $ip."/".$mask;
				my %temp = ("ip"=>$ip);
				$orange_eth{'br1'} = \%temp;
	}
}



sub show_add($)
{
	my $hash = shift;
	my %hash = %$hash;
	my $first = 0;#标记是否为第一次配置
	if(!-e $config)
	{
		 $first = 1;
	}
	my $hidden = "hidden_class";
	if($action  eq 'add_first' || $action eq 'add_node' || $action eq 'add_host' ||  $action eq 'add_router' || $action eq 'add_switcher')
	{
		$hidden = "";
	}
	printf <<EOF
		<div id="add_div" class="containter-div $hidden" style="width:80%;position:absolute;left:10%;top:150px;z-index:999;border:10px solid #ddd;">
	<span class="containter-div-header">
		<span style="display:block;float:left;margin-top:3px;"><img src='/images/applications-blue.png'  />添加一个网络节点</span>
		<img src="/images/delete.png" onclick="hide()" style="display:block;float:right;margin:5px 10px 0 0 ;cursor:pointer;"/>
	</span>
	<div class="containter-div-content">
		<form METHOD="post" id="add" action="$ENV{'SCRIPT_NAME'}" onsubmit = "if(!check_form())return false;">
		<table>
EOF
;
	if($action  eq 'add_first')#第一次添加根节点式
	{
		printf <<EOF
		<tr class="env">
			<td class="add-div-type">根节点名称</td>
			<td>$ini_name</td>
		</tr>
		<tr class="odd">
			<td class="add-div-type">选择要监控的接口</td>
			<td><ul width="100%" id="br_con" >
EOF
;
		&get_eths();
		foreach my $green(keys %green_eth)
		{
			printf <<EOF
			<li style="width:100%;height:25px;line-height:25px;"><input type="checkbox" id="br0" value="$green_eth{$green}{'ip'}" name="IP_MASK" checked="checked" />   <span class="green" style="font-weight:bold;">%s接口$green:</span>    $green_eth{$green}{"ip"}</li>
EOF
,_('GREEN')
;
		}
		foreach my $orange(keys %orange_eth)
		{
			printf <<EOF
			<li style="width:100%;height:25px;line-height:25px;"><input type="checkbox" id="br1" value="$orange_eth{$orange}{'ip'}" name="IP_MASK"  checked="checked" />   <span class="orange" style="font-weight:bold;">%s接口$orange:</span>   $orange_eth{$orange}{"ip"}</li>
EOF
,_('ORANGE')
;
		}
printf <<EOF
			</td>
		</tr>
EOF
;
	}elsif( $action eq 'add_node' || $action eq 'add_host' ||  $action eq 'add_router' || $action eq 'add_switcher')
	{
		get_root($hash);#定义上级节点
	printf <<EOF
			<tr class="odd_thin">
				<td class="add-div-type">添加节点类型 *</td>
				<td colspan="2"><select id="node_type" name="TYPE" style="width:100px">
EOF
;
	foreach my $type(sort keys %node_type)
	{
		if($action eq "add_first")
		{
			if($type eq "router")
			{
				print "<option value='$type' selected='selected' >$node_type{$type}</option>";
			}
		}elsif($action eq "add_node")
		{
			if($type eq "router")
			{
				print "<option value='$type' selected='selected' >$node_type{$type}</option>";
			}else{
				print "<option value='$type' >$node_type{$type}</option>";
			}
		}elsif($action =~ /add_/)
		{
			if("add_".$type eq $action)
			{
				print "<option value='$type' selected='selected' >$node_type{$type}</option>";
			}else{
				print "<option value='$type' >$node_type{$type}</option>";
			}
		}
	}
printf <<EOF
				</select></td>
			</tr>
EOF
;
if($action eq "add_host" || $action eq "add_switcher")
{
	print '<tr  class="env_thin " id="UP_NODE" name="UP_NODE">';
}else{
	print '<tr  class="env_thin hidden_class" id="UP_NODE" name="UP_NODE">';
}
printf <<EOF
			
				<td class="add-div-type">选择上级节点 *</td>
				<td><select id="FATHER" name="FATHER" onchange='refresh("$url","FATHER","node_type")' >
EOF
;
	foreach my $node(@up_ary)
	{
		if($node =~ /^(.*)=(.*)$/)
		{
			print "<option value='$1' >$2</option>";
		}
	}
printf <<EOF
				</select></td>

EOF
;
	my @up_if = get_if($hash,$add_id);
printf <<EOF				
				<td >选择上级接口 * <select name="FATHER_NODE">
EOF
;
	my $temp_count = 0;
	foreach my $if(@up_if)
	{
		$temp_count++;
		if($if =~ /^(.*)=(.*)$/)
		{
			print "<option value='$1' >接口$temp_count:$2</option>";
		}
	}
	printf <<EOF
			</select></td>
			</tr>
EOF
;
if($action eq "add_host")
{
	print '<tr id="IP" class="env_thin">';
}else{
	print '<tr id="IP" class="env_thin hidden_class">';
}
printf <<EOF
				<td class="add-div-type">添加节点IP *</td>
				<td colspan="2"><input type="text" id="host_ip" name="IP" style="width:100px" /></td>
			</tr>
EOF
;
if($action eq "add_router" || $action eq "add_node")
{
	print '<tr id="IP_MASK" class="env_thin ">';
}else{
	print '<tr id="IP_MASK" class="env_thin hidden_class">';
}
printf <<EOF
				<td class="add-div-type">节点接口 *
				</td>
				<td>接口IP </td>
				<td><a id="IF_FIRST" href="#" onclick="add_if(event)" style="display:block;float:right;">【添加接口】</a>
					<ul id="INTERFACE" style="height:140px;overflow:auto;">
						<li style="height:45px;border-bottom:1px dotted #999" >接口 IP/mask： <textarea style="width:200px;height:40px" name="IP_MASK"></textarea></li>
						<li style="height:45px;border-bottom:1px dotted #999" >接口 IP/mask： <textarea style="width:200px;height:40px" name="IP_MASK"></textarea></li>
					</ul>
				</td>
			</tr>
EOF
;
if($action eq "add_switcher")
{
	print '<tr id="S_SUB" class="odd_thin">';
}else{
	print '<tr id="S_SUB" class="odd_thin  hidden_class">';
}
printf <<EOF
				<td class="add-div-type"  >选择此交换机下的节点 *</td>
				<td style='width:120px;'>选择各个接口下节点</td>
				<td >
				<select id="switcher_child" name="CHILD" multiple style="width:40%; height:120px;display:block;float:left;">
EOF
;		
				my $sub_node_list = get_net_node($line,$hash);
				my %sub = %$sub_node_list;
				my $sub_host_ref = $sub{'host'};
				my $sub_net_ref = $sub{'net'};
				my %sub_host = %$sub_host_ref;
				my %sub_net = %$sub_net_ref;
				my $key =0;
				foreach my $sub_node(sort keys %sub_host)
				{
					my $node_type = $sub_host{$sub_node}{'type'};
					if($node_type !~ /_if$/)
					{
						print "<option value='$sub_node=$node_type'>".$node_type{$node_type}." ".$sub_host{$sub_node}{'host_name'}."</option>";
						$key =1;
					}
				}
				foreach my $sub_node(sort keys %sub_net)
				{
					my $node_type = $sub_net{$sub_node}{'type'};
					if($node_type !~ /_if$/)
					{
						print "<option value='$sub_node=$node_type'>".$node_type{$node_type}." ".$sub_net{$sub_node}{'host_name'}."</option>";
						$key =1;
					}
				}
				if(!$key)
				{
					$note = "<span class='note'>其父级节点没有子节点，不能添加交换机！</span>";
				}else{
					$note = "点击上面箭头选择";
				}
printf <<EOF
				</select> 
				<img src="/images/right.png" style='cursor:pointer;width:20px;height:15px;display:block;float:left;margin:10px' onclick='get_s_node()' />
				<ul id="switcher_if" style='display:block;float:left;height:120px;border:1px dotted #999;width:50%;'>
				</ul>
				<div style="clear:both;">$note</div>
				</td>
			</tr>
			<tr class="env_thin">
				<td class="add-div-type" >添加节点别名 *</td>
				<td colspan="2"> 
					<input type="text" id="HOST_NAME" name="HOST_NAME" style="width:100px" /> 
				</td>
			</tr>
EOF
;
}

printf <<EOF	
			
			
			<tr class="table-footer">
				<td colspan="3">
					<input class="net_button" type="submit" value="添加" />
					<input class="net_button" type="button" value="取消" onclick="hide()"/>
				    <input type="hidden" name="ACTION" value="add_save"      />
					<input type="hidden" name="IS_FIRST" value="$action" />
					<input type="hidden" name="LINE" value="$line" />
				</td>
			</tr>
		</table>
		</form>
	</div>
	</div>
	<div class="$hidden" id="pop-divs"></div>
EOF
;
}

sub get_root($)
{
	my $hash = shift;
	my %hash = %$hash;
	
	foreach my $net(sort keys %hash)
	{
		if($hash{$net}{"type"} !~ /_if/)
		{
			my $value = $hash{$net}{"host_name"}?$hash{$net}{"host_name"}:$hash{$net}{"type"};
			push(@up_ary,$net."=".$value);
		}
		get_root($hash{$net}{"net"});
	}
}


sub get_if($$)
{
	my $hash = shift;
	my %hash = %$hash;
	my $id = shift;
	my @up_if=();
	
	$hash = get_net_node($id,$hash);
	my %if_hash = %$hash;
	
	my $if = $if_hash{"net"};
	my %if = %$if;
	foreach my $ifs(sort keys %if)
	{
		my $value = $if{$ifs}{"ip"};
		push(@up_if,$ifs."=".$value)
	}
	return @up_if;
}

sub show_content($)
{
	my $hash = shift;
	my %hash = %$hash;
	printf <<EOF
	<table style="width:76%;margin-top:15px;" class="ruleslist" cellpadding="0" cellspacing="0" >
		<tr class="table-footer">
			<td colspan = "4">
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left:15px;" >
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/adds.png" ALT="添加网络节点"   title="添加网络节点" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="add_node">
				</form>
EOF
;
if(!-e $logic_config)
{
printf <<EOF
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left:15px;" >
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/logic.png" ALT="生成逻辑资产"   title="生成逻辑资产" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="LOGIC">
				</form>
EOF
;
}
if(-e $logic_config && -e $temp_add_router)
{
printf <<EOF
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left:15px;" onsubmit="confirm('物理资产已有改变，是否将此改变更新到逻辑资产？')">
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/logic_update.png"  ALT="更新逻辑资产"   title="更新逻辑资产" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="UPDATE">
				</form>
EOF
;
}
printf <<EOF			
				<input style="float:left;margin-left:15px;" class="imagebutton" type='image' onclick='graphUtils.printView()' SRC="/images/scan_mini.png" ALT="预览逻辑资产图"   title="预览逻辑资产图" />
			</td>
		</tr>
	</table>
	<div  style="width:76%;margin:0 auto;overflow-y:auto;border:1px solid #999;border:0 1px;">
	<div id="pathBody">
	<div  class="right_risk" title="物理拓扑图"  id="contextBody"  style="width:100%;margin:0 auto;overflow:auto;position:relative;"></div>
	</div>
	
	
	</div>
		<table style="width:76%;" class="ruleslist" cellpadding="0" cellspacing="0" >
		<tr>
            <td class="boldbase" width="35%">类型</td>
            <td class="boldbase" width="20%">IP/掩码</td>
			<td class="boldbase" width="20%">MAC</td>
			<td class="boldbase" width="25%">动作</td>
		</tr>
	</table>
	<div class="right_risk" style="width:76%;margin:0 auto;overflow-y:auto;border:1px solid #999;border:0 1px;">
	<table width="100%">
EOF
;
	$hash = get_net_node($line_node,$hash);
	get_json_table($hash,'1',$line_node);
printf <<EOF
	</table>
	</div>
	<table  style="width:76%;" class="ruleslist" cellpadding="0" cellspacing="0">
		<tr class="table-footer">
			<td></td>
		</tr>
	</table>
EOF
;
}

#将网络节点json文件映射为table表示出来
sub get_json_table($$$)
{
	my $hash = shift;
	my %hash = %$hash;
	my $time = shift;
	my $level = shift;
	
	my @ini = split("_",$line);
	my $ini_length = @ini;
	my @level = split("_",$level);
	my $level_length = @level;
	my $text_indent = ($level_length-$ini_length)*15;
	my $indent_str = "style='text-indent:".$text_indent."px;'";

if($hash{'type'} !~ /_if/)
{
	my @if;
	my $net_child  = $hash{'net'};
	my %net_child = %$net_child;
	foreach my $if(%net_child)
	{
		if($net_child{$if}{"type"} =~ /_if$/)
		{
			push(@if,$net_child{$if}{"ip"});
		}
	}
	
printf <<EOF
	<tr class="env_thin" id="$level" >
		   <td width="35%" $indent_str><img src="/images/level.png"  /><a href=\"$ENV{'SCRIPT_NAME'}?line=$level\" >
EOF
;
		print $hash{'type'};
printf <<EOF
		</a></td>
		    <td width="25%"><ul>
EOF
;
	my $count = 1;
foreach my $if(@if)
{
	print "<li><span class='note'>接口$count ip</span> $if";

	$count++;
}
			printf <<EOF
		    </ul></td>
		   <td width="20%">$hash{'mac'}</td>
		   <td width="25%">
EOF
;

printf <<EOF
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left" onsubmit="confirm('是否删除此节点？')">
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/delete.png" ALT="删除当前节点"   title="删除当前节点" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
					<input type="hidden" name="FATHER_NODE"   value="$level" />
					<input type="hidden" name="TYPE"   value="$hash{'type'}" />
				</form>
		   </td>
	</tr>
EOF
;
}
	if($time ne '2')
	{	
		my $net_child  = $hash{'net'};
		my $host_child = $hash{'host'};
		my %net_child = %$net_child;
		foreach my $nets(sort keys %net_child)
		{
			if($net_child{$nets} =~ /_if/)
			{
				get_json_table($net_child{$nets},'2',$nets);
			}else{
				get_json_table($net_child{$nets},'1',$nets);
			}
		}
		get_host_child($host_child,$level);
	}
}

sub get_host_child($$)
{
	my $hash = shift;
	my %hash = %$hash;
	my $level = shift;
	
	my @ini = split("_",$line);
	my $ini_length = @ini;
	my @level = split("_",$level);
	my $level_length = @level;
	my $text_indent = ($level_length+1-$ini_length)*15;
	my $indent_str = "style='text-indent:".$text_indent."px;'";
	
	foreach my $host(sort keys %hash)
	{
		my $father_id = get_father_node($host);
printf <<EOF
	<tr class="odd_thin $father_id">
		   <td $indent_str><img src="/images/level.png"  />$host
EOF
;
	print $hash{$host}{'type'};
printf <<EOF
			</td>
		   <td>$hash{$host}{'ip'}</td>
		   <td width="20%">$hash{$host}{'mac'}</td>
		   <td>
		   <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left" onsubmit="confirm('是否删除此节点？')">
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/delete.png"  ALT="删除节点"    title="删除节点"  />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
					<input type="hidden" name="FATHER_NODE"   value="$host" />
					<input type="hidden" name="TYPE"   value="host" />
				</form>
		   </td>
	</tr>
EOF
;
	}
}


sub get_net($$)
{
	my $hash = shift;
	my %hash = %$hash;
	my $level = shift;
	if($level<4)
	{
		print "<ul class='UL' style='display:block;'>";
	}else{
		print "<ul class='UL' style='display:none;'>";
	}
	foreach my $net(sort keys %hash)
	{
		if($hash{$net}{"type"} !~ /_if/)
		{
			my @level = split("_",$net);
			my $level_length = @level;
			my $text_indent = 15*($level_length-1)."px";

			print "<li id='$net' style='cursor:pointer;display:block;'>";
		
			if($net eq $line_node)
			{
				print "<span class='odd' style='background:#fee6cf;display:block;height:30px;line-height:30px;border-bottom:1px solid #999;text-indent:$text_indent;'>";
			}else{
				print "<span  class='odd' style='display:block;height:30px;line-height:30px;border-bottom:1px solid #999;text-indent:$text_indent;'>";
			}
		
			print '<img src="/images/toggle.png" style="cursor:pointer;margin-top:5px;margin-bottom:-5px;" onclick="show_hidden_child(event)" />';
			print "<a href=\"$ENV{'SCRIPT_NAME'}?line_node=$net\" style='height:30px;line-height:30px;font-size:11px;font-weight:bold;'>";
			print  $hash{$net}{"host_name"}?$hash{$net}{"host_name"}:$hash{$net}{"type"};
			$net_child = print "</a>";
			print "</span>";
			get_net($hash{$net}{"net"},$level);
			print "</li>";
		}else{
			get_net($hash{$net}{"net"},$level);
		}
	}
	print "</ul>";
}

sub show_tree($)
{
	my $hash = shift;
	my %hash = %$hash;
	printf <<EOF
	<div class="tree" style="width:21%;min-width:200px;float:left;min-height:150px;margin:15px 0 0 10px;border:1px solid #aaa;overflow-y:auto;">
	<p class="table-footer" style='font-weight:bold;text-align:center;'>物理资产树 </p>

EOF
;
	get_net(\%hash,0);
printf <<EOF
	</div>
EOF
;
}


sub check_running()
{
	if( -e $state)
	{
		my $string = read_file($state);

		if($string =~ /running/)
		{
			begin();
		}elsif($string =~ /^end(.*)$/)
		{
			$errormessage = $1;
		}
	}
}


sub close_page()
{
	printf <<EOF
	<script src="/include/jquery.easyui.min.js" type="text/javascript"></script>
	<script src="/include/p_strawberry.min.js" type="text/javascript" language="javascript"></script>
	<script src="/include/draw.js" type="text/javascript" language="javascript"></script>
	<script type="text/javascript" src="/include/physics.js"></script>	
	
	</div></div></body></html>
EOF
;
}

sub note_box()
{
	&openbox('100%','left',_('物理资产'));
printf  <<EOF
	<table width="100%">
	<tr class="env table_note fordel" ><td style="text-align:center;" ><img src="/images/pop_warn_min.png" /> 当前尚未扫描物理资产,或者扫描失败,请添加根节点扫描网络！
	<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="display:inline-block;">
		<input  type='submit'  class="net_button" value="添加根节点"  ALT="添加根节点"   />
		<INPUT TYPE="hidden" NAME="ACTION" VALUE="add_first">
	</form>
	</td></tr>
	</table>
EOF
;
	&closebox();
}

&getcgihash(\%par);
&showhttpheaders();
my $extraheader = '<link rel="stylesheet" type="text/css" href="/include/style.css">
	<link rel="stylesheet" type="text/css" href="/include/main.css">
	<link rel="stylesheet" type="text/css" href="/include/menu.css">
	<link rel="stylesheet" type="text/css" href="/include/content.css">
	<link href="/include/flowPath.css" type="text/css" rel="stylesheet" />
	<script type="text/javascript" src="/include/waiting.js"></script>	
	<STYLE>v\:*{behavior:url(#default#VML);}</STYLE>';
	
&openpage(_('物理逻辑'), 1, $extraheader);
&save();
&check_running();
&openbigbox($errormessage,$warnmessage,$notemessage);
if(-e $config && _hashToJSON($hash) ne '{}')
{
	&show_tree($hash);
	&show_content($hash);
}else{
	note_box();
}
if($action eq "add_save" || $action eq "delete")
{
		begin();
		#调用后台命令
		`sudo $scan`;
		#调用后台命令结束
		ends();
}
&show_add($hash);
&close_page();