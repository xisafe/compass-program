#!/usr/bin/perl
#file:资产识别页面
#author:周圆

my  %par;
require '/var/efw/header.pl';
my $config = "/var/efw/risk/logic/config";#逻辑配置文件
my $p_config = "/var/efw/risk/config";#逻辑配置文件
my %hash = ();
my $line = "0";
my $level = 0;
my $test = "";
my @up_ary;
my $action = "";
my $name;
my $father;
my $title = "";
my $merge_id = "0";
my $url =  $ENV{'SCRIPT_NAME'};

my %node_type=(
					"host"=>"一般主机",
					"SERVER"=>"一般服务器",
					"WEB"=>"WEB服务器",
					"DATABASE"=>"数据库服务器",
					"BACKUP"=>"备份机"
				);
my %move_type=(
					"host"=>"主机",
					"net"=>"部门"
				);

sub read_file($)
{
	my $file =shift;
	my $string = "";
	open(MYFILE,"$file");
	foreach my $line (<MYFILE>) 
	{
		chomp($line);
		$line =~ s/\s//g;
		$string .= $line;
	}
	close (MYFILE);
	return $string;
}


sub write_config($$)
{
	my $dir = shift;
	my $str = shift;
	open(FILE,">".$dir);
	print FILE $str;
	close FILE;
}

sub save()
{
	if(-e $config)
	{
		my $string = read_file($config);
		$hash = JSON::XS->new->decode($string);
		#$hash = get_logic_config($hash);
		#$hash = update_index($hash);
		#write_config($config,_hashToJSON($hash));
		%hash = %$hash;
	}
	if($ENV{'QUERY_STRING'} =~ /^line=(.*)$/)
	{
		$line = $1;
	}
	if($par{'line'})
	{	
		$line = $par{'line'};
	}
	$action = $par{'ACTION'};
	
	if($ENV{'QUERY_STRING'} =~ /^action=(.*)&&line=(.*)$/)
	{
		$action = $1;
		$merge_id = $2;
	}
	
	if($action eq "add_save")
	{
		my $name = $par{'NAME'};
		my $father = $par{'FATHER'};
		$hash = add_node($hash,$father,$name);
		write_config($config,_hashToJSON($hash));
	}elsif($action eq "edit_save")
	{
		my $name = $par{'NAME'};
		my $node = $par{'NODE'};
		my $type = $par{'TYPE'};
		my $service = $par{'SERVICE'};
		my @value=("service_type",$service,"host_name",$name);
		$hash = $type eq "host" ? edit_host_node($node,$hash,@value):edit_net_node($node,$hash,@value);
		$hash = update_index($hash);
		write_config($config,_hashToJSON($hash));
	}elsif($action eq "merge_save")
	{
		my $merge_option = $par{'MERGE_OPTION'};
		my $merge_name   = $par{'MERGE_NAME'};
		$hash = merge_node($merge_option,$merge_name,$hash);
		$hash = update_index($hash);
		write_config($config,_hashToJSON($hash));
	}elsif($action eq "unmerge_save")
	{
		my $unmerge_father = $par{'UNMERGE_FATHER'};
		my $unmerge_child = $par{'UNMERGE_CHILD'};
		$hash = unmerge_node($unmerge_father,$unmerge_child,$hash);
		$hash = update_index($hash);
		write_config($config,_hashToJSON($hash));
	}elsif($action eq "move_save")
	{
		my $father = $par{'MOVE_FATHER'};
		my $child = $par{'MOVE_CHILD'};
		my @child = split("\\|",$child);
		$hash = move_node($hash,$father,@child);
		#$test = _hashToJSON($hash);
		$hash = update_index($hash);
		write_config($config,_hashToJSON($hash));
	}elsif($action eq "delete")
	{
		my $id = $par{'LINE'};
		$hash = delete_node("net",$id,$hash);
		$hash = add_disso($hash,$id);#将$id下节点添加到游离主机组去
		$hash = update_index($hash);
		write_config($config,_hashToJSON($hash));
	}elsif($action eq "recycle")
	{
		my $string = read_file($p_config);
		my $p_hash = JSON::XS->new->decode($string);
		$p_hash = get_logic_config($p_hash);
		$p_hash = update_index($p_hash);
		write_config($config,_hashToJSON($p_hash));
	}elsif($action eq "add")
	{
		$title = "添加新部门";
	}elsif($action eq "edit")
	{
		$title = "编辑节点";
	}elsif($action eq "merge")
	{
		$title = "合并部门";
	}elsif($action eq "unmerge")
	{
		$title = "分解部门";
	}elsif($action eq "move")
	{
		$title = "移动节点";
	}
}

sub add_disso($$)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	my $id = shift;
	
	my $string = read_file($config);
	my $temp_hash = JSON::XS->new->decode($string);
	my $temp_hash2 = JSON::XS->new->decode($string);
	%temp_hash = %$temp_hash;
	%temp_hash2 = %$temp_hash2;	
	
	my $temp_disso = get_net_node($id,\%temp_hash2);
	my %temp_disso = %$temp_disso;
	my $nets = $temp_disso{"net"};
	my %net = %$nets;
	my $hosts = $temp_disso{"host"};
	my %host = %$hosts;
	
	my $is_disso = 0;#判断是否已存在游离节点
	my $disso_id ;
	my $temp_net = $temp_hash{"0"}{"net"};
	my %temp_net = %$temp_net;

	foreach my $tempnet(sort keys %temp_net)
	{
		if($temp_net{$tempnet}{"type"} eq "disso")
		{
			$is_disso = 1;
			$disso_id = $tempnet;
		}
	}
			
	my %disso_node = ();
	if($is_disso)#若已存在游离节点，则把刚刚删除的部门下的节点放入
	{
		$temp_net = delete_node("net",$id,$temp_net);
		my $disso_node = get_net_node($disso_id,$temp_net);
		%disso_node = %$disso_node;
				
		foreach $curnet(sort keys %net)
		{
			$disso_node{"net"}{$curnet} = $net{$curnet};
		}
		foreach $curhost(sort keys %host)
		{
			$disso_node{"host"}{$curhost} = $host{$curhost};
		}
	}else{
			%disso_node = (
							"type" => "disso",
							"ip"   => "",
							"mac"  => "",
							"host_name" => "游离部门与主机",
							"net"  => \%net,
							"host"  => \%host
						);
	}
	$disso_id = $disso_id ne "" ? $disso_id:"0-disso";
	
	$node_root{"0"}{"net"}{$disso_id} = \%disso_node;
	return \%node_root;
}



sub move_node($$@)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	my $father_id = shift;
	my @child = @_;
	my $cur_father = get_father_node($child[0]);
	foreach my $temp_f(@child)
	{
		delete_node("net",$temp_f,$hashref);
		delete_node("host",$temp_f,$hashref);
	}
	
	foreach my $net(sort keys %node_root)
	{
		#$test.= $net." ".$father_id." ".compare($net,$father_id)." ".brother_distance($net,$father_id)." ".$node_root{$net}{"type"}."<br />";
		if(compare($net,$father_id) == 2 || compare($net,$father_id) == 4)#父亲节点和爷爷节点
		{
			$node_root{$net}{"net"}  = move_node($node_root{$net}{"net"},$father_id,@child);
		}elsif(compare($net,$father_id) == 5 && brother_distance($net,$father_id)<0)
		{
			next;
		}elsif(compare($net,$father_id) == 5 && brother_distance($net,$father_id)>0)
		{
			last;
		}elsif(compare($net,$father_id) == 0)
		{
			my $string = read_file($config);
			my $temp_hash = JSON::XS->new->decode($string);
			%temp_hash = %$temp_hash;
			my $child = get_net_node($cur_father,\%temp_hash);
			my %child_node = %$child;
			
			foreach my $childs(@child)
			{
				if($child_node{"host"}{$childs})
				{
					$node_root{$net}{"host"}{$childs} = $child_node{"host"}{$childs};
				}elsif($child_node{"net"}{$childs}){
					$node_root{$net}{"net"}{$childs} = $child_node{"net"}{$childs};
				}
			}
		}
	}
	return \%node_root;
}


sub unmerge_node($$$)
{
	my $father_id = shift;
	my $child = shift;
	my $hashref = shift;
    my %node_root = %$hashref;
	my %child_hash=();

	my @child_temp = split("\\|",$child);
	foreach my $childs(@child_temp)
	{
		my @temp = split("=",$childs);
		my @temp_ary = [];
		if($child_hash{$temp[0]})
		{
			my $temps = $child_hash{$temp[0]};
			@temp_ary = @$temps;
		}	
		push(@temp_ary,$temp[1]);
		delete($child_hash{$temp[0]});
		$child_hash{$temp[0]} = \@temp_ary;
	}
	
	foreach my $net(sort keys %node_root)
	{	
		#$test.= $net." ".$father_id." ".compare($net,$father_id)." ".brother_distance($net,$father_id)." ".$node_root{$net}{"type"}."<br />";
		if(compare($net,$father_id) == 2 || compare($net,$father_id) == 4)#父亲节点和爷爷节点
		{
			$node_root{$net}{"net"}  = unmerge_node($father_id,$child,$node_root{$net}{"net"});
		}elsif(compare($net,$father_id) == 5 && brother_distance($net,$father_id)<0)
		{
			next;
		}elsif(compare($net,$father_id) == 5 && brother_distance($net,$father_id)>0)
		{
			last;
		}elsif(compare($net,$father_id) == 0)
		{
			foreach my $sub_child(sort keys %child_hash)
			{
				my $group = $child_hash{$sub_child};
				my @group = @$group;
				my %host = ();
				my %net = ();
				foreach my $group_id(@group)
				{
					if($node_root{$net}{"net"}{$group_id})
					{
						$net{$group_id} = $node_root{$net}{"net"}{$group_id};
						delete($node_root{$net}{"net"}{$group_id});
					}elsif($node_root{$net}{"host"}{$group_id})
					{
						$host{$group_id} = $node_root{$net}{"host"}{$group_id};
						delete($node_root{$net}{"host"}{$group_id});
					}
				}
				my %temp = (
							"type" => "merge",
							"ip"   => "",
							"mac"  => "",
							"host_name" => "分解部门".$sub_child,
							"host" => \%host,
							"net"  => \%net
						);
				$node_root{$net}{"net"}{$group[0]} = \%temp;
			}
		}
	}
	return \%node_root;
}


sub merge_node($$$)
{
	my $merge = shift;
	my $name = shift;
	my $hashref = shift;
    my %node_root = %$hashref;
	my @merge_node = split("\\|",$merge);
	my $father_id = get_father_node($merge_node[0]);
	my $length = @merge_node;
	foreach my $net(sort keys %node_root)
	{	
		#$test.= $net." ".$father_id." ".compare($net,$father_id)." ".brother_distance($net,$father_id)." ".$node_root{$net}{"type"}."<br />";
		if(compare($net,$father_id) == 2 || compare($net,$father_id) == 4)#父亲节点和爷爷节点
		{
			$node_root{$net}{"net"}  = merge_node($merge,$name,$node_root{$net}{"net"});
		}elsif(compare($net,$father_id) == 5 && brother_distance($net,$father_id)<0)
		{
			next;
		}elsif(compare($net,$father_id) == 5 && brother_distance($net,$father_id)>0)
		{
			last;
		}elsif(compare($net,$father_id) == 0)
		{
			my $index = 0;
			my $sub_host = $node_root{$net}{"host"};
			my %sub_host = %$sub_host;
			my $sub_net = $node_root{$net}{"net"};
			my %sub_net = %$sub_net;
			foreach my $temps(keys %sub_host){$index++;}
			foreach my $temps(keys %sub_net){$index++;}

			my %net = ();
			my %host = ();
			my $new_ip = "";
			foreach my $nets(@merge_node)
			{
				$net{$nets} = $node_root{$net}{"net"}{$nets};
				if($node_root{$net}{"net"}{$nets}{"type"} eq "router" || $node_root{$net}{"net"}{$nets}{"type"} eq "switcher")
				{
					$new_ip .= $node_root{$net}{"net"}{$nets}{"type"}."=".$node_root{$net}{"net"}{$nets}{"ip"}."|";
				}
				delete($node_root{$net}{"net"}{$nets});
			}
			my %temp = (
							"type" => "merge",
							"ip"   => $new_ip,
							"mac"  => "",
							"host_name" => $name,
							"net"  => \%net
						);
			if($index>$length)#表示还有其他的未合并的兄弟节点
			{
				$node_root{$net}{"net"}{$merge_node[0]} = \%temp;
			}else{	#直接合并到父级部门
				$node_root{$net} = \%temp;
			}
			last;
		}
	}
	return \%node_root;
}


sub add_node($$$)
{
	my $hashref = shift;
    my %node_root = %$hashref;
	my $id = shift;
	my $hostname = shift;
	foreach my $net(sort keys %node_root)
	{
		if(compare($net,$id) == 2 || compare($net,$id) == 4)#父级节点
		{
			$node_root{$net}{"net"} = add_node($node_root{$net}{"net"},$id,$hostname);
			last;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)<0)#兄弟节点
		{
			next;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id) >0)#兄弟节点
		{
			last;
		}elsif(compare($net,$id) == 0)#同一节点
		{
			my $index = 0;
			my $temp_net = $node_root{$net}{"net"};
			my %temp_nets = %$temp_net;
			foreach my $temps(keys %temp_nets){$index++;}
			
			my $temp_host = $node_root{$net}{"host"};
			my %temp_hosts = %$temp_host;
			foreach my $temps(keys %temp_hosts){$index++;}			
			
			my %hosts = ();
			my %nets = ();
			my %temp = (
							"type" => "virtual",
							"ip"   => "",
							"host_name" => $hostname
						);
			#$test.=_hashToJSON(\%temp);
			$node_root{$net}{"net"}{$net."_".$index} = \%temp;
			last;#结束遍历
		}
	}
	return \%node_root;
}


sub show_tree($)
{
	my $hash = shift;
	my %hash = %$hash;
	printf <<EOF
	<div class="tree" style="width:21%;min-width:200px;float:left;min-height:400px;margin:15px 0 0 10px;border:1px solid #aaa;overflow-y:auto;">
	<p class="table-footer" style='font-weight:bold;text-align:center;'>逻辑资产树 </p>

EOF
;
	get_net(\%hash,0);
printf <<EOF
	</div>
EOF
;
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
		
		my $disso_net;#记录游离部门编号
		foreach my $nets(sort keys %sub_net)
		{
			if($sub_net{$nets}{"type"} ne "disso")
			{
				$node_root{$net}{"net"}{$net."_".$i} = $sub_net{$nets};
				$i++;
			}else{
				$disso_net = $nets;
			}
		}
		if($disso_net)
		{
			$node_root{$net}{"net"}{$net."_".$i} = $sub_net{$disso_net};
		}
		
		if($node_root{$net}{"net"} ne "")
		{
			$node_root{$net}{"net"} = update_index($node_root{$net}{"net"});
		}
	}
	return \%node_root;
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
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/adds.png" ALT="添加部门"   title="添加部门" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="add">
				</form>
				
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;" >
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/merge.png" ALT="合并部门"   title="合并部门" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="merge">
				</form>
				
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;" >
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/unmerge.png" ALT="分解部门"   title="分解部门" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="unmerge">
				</form>
				
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;" >
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/move.png" ALT="移动部门或主机"   title="移动部门或主机" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="move">
				</form>
				
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;" onsubmit="if(!confirm('确定将逻辑资产还原为最初状态？')){return false;}">
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/recycle.png"  ALT="还原逻辑视图"   title="还原逻辑视图" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="recycle">
				</form>
				
				
				<input style="float:left;" class="imagebutton" type='image' onclick='graphUtils.printView()' SRC="/images/scan_mini.png" ALT="预览逻辑资产图"   title="预览逻辑资产图" />
			</td>
		</tr>
	</table>
	<div  style="width:76%;margin:0 auto;overflow-y:auto;border:1px solid #999;border:0 1px;">
	<div id="pathBody">
	<div  class="right_risk" title="逻辑拓扑图"  id="contextBody"  style="width:100%;margin:0 auto;overflow:auto;position:relative;"></div>
	</div>
	
	</div>
		<table style="width:76%;" class="ruleslist" cellpadding="0" cellspacing="0" >
		<tr>
            <td class="boldbase" width="35%">名称</td>
            <td class="boldbase" width="20%">IP/掩码</td>
			<td class="boldbase" width="20%">服务类型</td>
			<td class="boldbase" width="25%">动作</td>
		</tr>
	</table>
	<div class="right_risk" style="width:76%;margin:0 auto;overflow-y:auto;border:1px solid #999;border:0 1px;">
	<table width="100%">
EOF
;
	$hash = get_net_node($line,$hash);
	get_json_table($hash,'1',$line);
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

sub get_net_node($$)
{
	my $id = shift;
	my $hashref = shift;
	my %node_root = %$hashref;
	my $node = ();
	$test.= $id;
	foreach my $net(sort keys %node_root)
	{
		$test.= $net." ".$id." ".compare($net,$id)." ".brother_distance($net,$id)." ".$node_root{$net}{"type"}."<br />";
		if(compare($net,$id) == 2 ||compare($net,$id) == 4)#父级节点
		{
			$node_root{$net}{"net"} = get_net_node($id,$node_root{$net}{'net'});
			last;
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


sub get_host_node($$)
{
	my $id = shift;
	my $hashref = shift;
	my %node_root = %$hashref;
	my $node = ();	
	foreach my $net(sort keys %node_root)
	{
		if(compare($net,$id) == 2 ||compare($net,$id) == 4)#父级节点
		{
			if(compare($net,$id) == 2)
			{
				$node_root{$net}{"host"} = get_host_node($id,$node_root{$net}{'host'});
			}else{
				$node_root{$net}{"net"} = get_host_node($id,$node_root{$net}{'net'});
			}
			last;
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


sub edit_net_node($$@)
{
	my $id = shift;
	my $hashref = shift;
	my %node_root = %$hashref;
	my @value= @_;

	foreach my $net(sort keys %node_root)
	{
		if(compare($net,$id) == 2 ||compare($net,$id) == 4)#父级节点
		{
			$node_root{$net}{"net"} = edit_net_node($id,$node_root{$net}{'net'},@value);
			last;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)<0)#兄弟节点
		{
				next;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)>0)#兄弟节点
		{
				last;
		}elsif(compare($net,$id) == 0)#同一节点
		{
			my $length = @value;
			for(my $i = 0;$i<$length;$i=2*($i+1))
			{
				$node_root{$net}{$value[$i]} = $value[$i+1];
			}
		}
	}
	return \%node_root;
}

sub edit_host_node($$@)
{
	my $id = shift;
	my $hashref = shift;
	my %node_root = %$hashref;
	my @value= @_;
	
	foreach my $net(sort keys %node_root)
	{
			if(compare($net,$id) == 2 )#父级节点
			{
				$node_root{$net}{"host"} = edit_host_node($id,$node_root{$net}{'host'},@value);
				last;
			}elsif(compare($net,$id) == 4)
			{
				$node_root{$net}{"net"} = edit_host_node($id,$node_root{$net}{'net'},@value);
				last;
			}elsif(compare($net,$id) == 5 && brother_distance($net,$id)<0)#兄弟节点
			{
				next;
			}elsif(compare($net,$id) == 5 && brother_distance($net,$id)>0)#兄弟节点
			{
				last;
			}elsif(compare($net,$id) == 0)#同一节点
			{
				my $length = @value;
				for(my $i = 0;$i<$length;$i=2*($i+1))
				{
					$node_root{$net}{$value[$i]} = $value[$i+1];
				}
			}
	}
	return \%node_root;
}


sub delete_node($$$)
{
	my $type = shift;
	my $id = shift;
	my $hashref = shift;
    my %node_root = %$hashref;

	foreach my $net(sort keys %node_root)
	{
		if(compare($net,$id) == 2)
		{
			if($type eq "host")
			{
				$node_root{$net}{"host"} = delete_node($type,$id,$node_root{$net}{'host'});
			}else{
				$node_root{$net}{"net"} = delete_node($type,$id,$node_root{$net}{'net'});
			}
			last;
		}elsif(compare($net,$id) == 4)
		{
			$node_root{$net}{"net"} = delete_node($type,$id,$node_root{$net}{'net'});
			last;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)<0)#兄弟节点
		{
			next;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)>0)#兄弟节点
		{
			last;
		}elsif(compare($net,$id) == 0)#同一节点
		{
			delete($node_root{$net});
		}
	}
	return \%node_root;
}

sub get_father_node($)
{
	my $node = shift;
	if($node =~ /^(.*)(_\d+){1}$/)
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

printf <<EOF
	<tr class="env_thin" id="$level" >
		   <td width="35%" $indent_str><img src="/images/level.png"  />$level <a href=\"$ENV{'SCRIPT_NAME'}?line=$level\" >
EOF
;
		print $hash{'host_name'}?$hash{'host_name'}:$hash{'type'};
printf <<EOF
		</a></td>
		   <td width="20%">$hash{'ip'}</td>
		   <td width="20%">$node_type{$hash{'service_type'}}</td>
		   <td width="25%">
EOF
;
if($hash{'type'} !~ /disso/)
{
printf <<EOF
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left" onsubmit="if(!confirm('是否删除此节点？')){return false;}">
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/delete.png" ALT="删除当前节点"   title="删除当前节点" />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="delete">
					<input type="hidden" name="LINE"   value="$level" />
				</form>
				
				<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/edit.png"  ALT="编辑节点"    title="编辑节点"  />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="edit">
					<input type="hidden" name="LINE"   value="$level" />
					<input type="hidden" name="TYPE"   value="net" />
					<input type="hidden" name="line"   value="$line" />
					<input type="hidden" name="host_name"   value="$hash{'host_name'}" />
				</form>
EOF
;
}
printf <<EOF
		   </td>
	</tr>
EOF
;

	if($time ne '2')
	{	
		my $net_child  = $hash{'net'};
		my $host_child = $hash{'host'};
		my %net_child = %$net_child;
		foreach my $nets(sort keys %net_child)
		{
			get_json_table($net_child{$nets},'2',$nets);
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
	print $hash{$host}{'host_name'}?$hash{$host}{'host_name'}:$hash{$host}{'type'};
printf <<EOF
			</td>
		   <td>$hash{$host}{'ip'}</td>
		    <td width="20%">$node_type{$hash{$host}{'service_type'}}</td>
		   <td>
		   <form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left">
					<input class="imagebutton" type='image' NAME="submit" SRC="/images/edit.png"  ALT="编辑节点"    title="编辑节点"  />
					<INPUT TYPE="hidden" NAME="ACTION" VALUE="edit">
					<input type="hidden" name="LINE"   value="$host" />
					<input type="hidden" name="TYPE"   value="host" />
					<input type="hidden" name="line"   value="$line" />
					<input type="hidden" name="host_name"   value="$hash{$host}{'host_name'}" />
				</form>
		   </td>
	</tr>
EOF
;
	}
}




sub _hashToJSON {
    my $hashref = shift;
    my %hash = %$hashref;
    my $json = '{';
    my @key_value_pairs = ();
    foreach $key (keys %hash) 
	{
		if($key eq "risk_drop_threshold" || $key eq "risk_pass_threshold" || $key eq "weight")
		{
			my $values = $hash{$key};
			my @value = @$values;
			$value = "[";
			$value .= join(",",@value);
			$value .= "]";
			push(@key_value_pairs, sprintf("\"%s\": %s ",$key,$value));
		}elsif(($value = _hashToJSON($hash{$key})) ne '{}')
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

#将物理拓扑图配置文件转换为逻辑拓扑图配置文件
sub get_logic_config($)
{
	my $hash = shift;
	my %hash = %$hash;
	foreach my $net(sort keys %hash)
	{
		#$test .= $net."<br />";
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

sub get_net($$)
{
	my $hash = shift;
	my %hash = %$hash;
	my $level = shift;
	my $disso = "";
	if($level<4)
	{
		print "<ul class='UL' style='display:block;'>";
	}else{
		print "<ul class='UL' style='display:none;'>";
	}
	foreach my $net(sort keys %hash)
	{
		if($net ne "global")
		{
		my @level = split("_",$net);
		my $level_length = @level;
		my $text_indent = 15*($level_length-1)."px";
		if($hash{$net}{"type"} !~ /disso/)
		{
			print "<li id='$net' style='cursor:pointer;display:block;'>";
		
		if($net eq $line)
		{
				print "<span class='odd' style='background:#fee6cf;display:block;height:30px;line-height:30px;border-bottom:1px solid #999;text-indent:$text_indent;'>";
		}else{
				print "<span  class='odd' style='display:block;height:30px;line-height:30px;border-bottom:1px solid #999;text-indent:$text_indent;'>";
		}
		print '<img src="/images/toggle.png" style="cursor:pointer;margin-top:5px;margin-bottom:-5px;" onclick="show_hidden_child(event)" />';
		print "<a href=\"$ENV{'SCRIPT_NAME'}?line=$net\" style='height:30px;line-height:30px;font-size:11px;font-weight:bold;'>";
		print $hash{$net}{"host_name"}?$hash{$net}{"host_name"}:$hash{$net}{"type"};
		print "</a>";
			
		$net_child = get_net_count($hash{$net}{"net"},0);
		$host_child = get_host_count($hash{$net},0);
			
		print "&nbsp;&nbsp;部门:".$net_child."&nbsp;&nbsp;主机:".$host_child;
		print "</span>";
		get_net($hash{$net}{"net"},$level);
		print "</li>";
		}else{
			$disso = $net;
		}
		}
	}
	if($disso)
	{
		my @level = split("_",$disso);
		my $level_length = @level;
		my $text_indent = 15*($level_length-1)."px";
		print "<li id='$disso' style='cursor:pointer;display:block;border:2px dotted #ec8806;margin-top:30px;'>";
		if($disso eq $line)
		{
				print "<span class='odd' style='background:#fee6cf;display:block;height:30px;line-height:30px;border-bottom:1px solid #999;text-indent:$text_indent;'>";
		}else{
				print "<span  class='odd' style='display:block;height:30px;line-height:30px;border-bottom:1px solid #999;text-indent:$text_indent;'>";
		}
		print '<img src="/images/toggle.png" style="cursor:pointer;margin-top:5px;margin-bottom:-5px;" onclick="show_hidden_child(event)" />';
		print "<a href=\"$ENV{'SCRIPT_NAME'}?line=$disso\" style='height:30px;line-height:30px;font-size:11px;font-weight:bold;'>";
		print $hash{$disso}{"host_name"}?$hash{$disso}{"host_name"}:$hash{$disso}{"type"};
		print "</a>";
			
		$net_child = get_net_count($hash{$disso}{"net"},0);
		$host_child = get_host_count($hash{$disso},0);
			
		print "&nbsp;&nbsp;部门:".$net_child."&nbsp;&nbsp;主机:".$host_child;
		print "</span>";
		get_net($hash{$disso}{"net"},$level);
		print "</li>";
	}
	print "</ul>";
}

sub get_net_count($$)
{
	my $hash = shift;
	my %hash = %$hash;
	my $count = shift;
	foreach my $net(sort keys %hash)
	{
		$count++;
		my $nets = $hash{$net}{"net"};
		my %net = %$nets;
		foreach my $temp(keys %net)
		{
			$count++;
			$count = get_net_count($net{$temp}{"net"},$count);
		}
	}
	return $count;
}

sub get_host_count($$)
{
	my $hash = shift;
	my %hash = %$hash;
	my $count = shift;
	
	my $hosts = $hash{"host"};
	my %host = %$hosts;
	foreach my $host(sort keys %host)
	{
		$count++;
	}
	my $nets = $hash{"net"};
	my %net = %$nets;
	foreach my $net(sort keys %net)
	{
		$count = get_host_count($hash{"net"}{$net},$count);
	}
	return $count;
}


sub get_merge($)
{
	my $hash = shift;
	my %hash = %$hash;
	foreach my $net(sort keys %hash)
	{
		my @level = split("_",$net);
		my $level_length = @level;
		my $text_indent = 10*$level_length."px";
			
		print "<li id='$net' style='cursor:pointer;text-indent:$text_indent;margin:3px;padding:3px;'>";
		print '<input type="checkbox" name="MERGE_OPTION" class="merge_option" value="'.$net.'"> ';
		print $hash{$net}{"host_name"}?$hash{$net}{"host_name"}:$hash{$net}{"type"};
		get_merge($hash{$net}{"net"});
		print "</li>";
	}
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

sub show_action($)
{
	my $hash = shift;
	my %hash = %$hash;
	my $hidden = "hidden_class";
	if($action eq "add" || $action eq "edit" || $action eq "merge" ||$action eq "unmerge" ||$action eq "move")
	{
		$hidden = "";
	}
	printf <<EOF
	<div id="add_div" class="containter-div $hidden" style="width:80%;position:absolute;left:10%;top:150px;z-index:999;border:10px solid #ddd;">
	<span class="containter-div-header">
		<span style="display:block;float:left;margin-top:3px;"><img src='/images/applications-blue.png'  />$title</span>
		<img src="/images/delete.png" onclick="hide()" style="display:block;float:right;margin:5px 10px 0 0 ;cursor:pointer;"/>
	</span>
	<div class="containter-div-content">
		<form METHOD="post" id="add" action="$ENV{'SCRIPT_NAME'}" onsubmit = "if(!check_form('$action'))return false;">
		<table>
EOF
;
	if($action eq "add")
	{
		&add_inner(\%hash);
	}elsif($action eq "edit")
	{
		&edit_inner(\%hash);
	}elsif($action eq "merge")
	{
		&merge_inner(\%hash);
	}elsif($action eq "unmerge")
	{
		&unmerge_inner(\%hash);
	}elsif($action eq "move")
	{
		&move_inner(\%hash);
	}
printf <<EOF
		</table>
		</form>
	</div>
	</div>
	<div class="$hidden" id="pop-divs"></div>
EOF
;
}

sub move_inner($)
{
	my $hash = shift;
	my %hash = %$hash;
	get_root($hash);#定义上级节点
printf <<EOF
	<tr class="env"><td class="add-div-type">选择移动节点所在部门 *</td>
	<td colspan="2">
	<select name="FATHER" id="move" style="width:150px;float:left;margin-right:20px;" onchange='refresh("$url","move","move")'>
EOF
;
	foreach my $node(@up_ary)
	{
		if($node =~ /^(.*)=(.*)$/)
		{
			if($1 eq $merge_id)
			{
				print "<option selected value='$1' >$2</option>";
			}else{
				print "<option value='$1' >$2</option>";
			}
		}
	}
printf <<EOF
				</select>
				<select  name="MOVE_CHILD" id="move_host" multiple  style="width:200px;height:150px;float:left;" >
EOF
;
	my $host;
	my $net;
	my $count = 0;

	$hash = get_net_node($merge_id,\%hash);
	%hash = %$hash;
	$net = $hash{"net"};
	$host = $hash{"host"};

	my %net = %$net;
	my %host = %$host;
	foreach my $sub_net(sort keys %net)
	{
		my $temp = $net{$sub_net}{"host_name"}?$net{$sub_net}{"host_name"}:$net{$sub_net}{"type"};
		print "<option value='".$sub_net."' class='net'>".$temp."</option>";
		$count++;
	}
	foreach my $sub_host(sort keys %host)
	{
		my $temp = $host{$sub_host}{"host_name"}?$host{$sub_host}{"host_name"}:$host{$sub_host}{"ip"};
		print "<option value='".$sub_host."'   class='host' >".$temp."</option>";
		$count++;
	}
printf <<EOF	
	</select>

				</td>
			</tr>
EOF
;
printf <<EOF	
			<tr class="env">
				<td class="add-div-type">选择移动的目标部门 *</td>
				<td>
				<select name="MOVE_FATHER">
EOF
;
	foreach my $node(@up_ary)
	{
		if($node =~ /^(.*)=(.*)$/)
		{
			if($merge_id eq $1)
			{
				print "<option selected value='$1' >$2</option>";
			}elsif(compare($par{'LINE'},$1) != 2 && compare($net,$father_id)!= 4){
				print "<option value='$1' >$2</option>";
			}
		}
	}
printf <<EOF
				</select></td>
			</tr>
				</td>
			</tr>
			<tr class="table-footer">
				<td colspan="3">
					<input class="net_button" type="submit" value="移动" />
					<input class="net_button" type="button" value="取消" onclick="hide()"/>
				    <input type="hidden" name="ACTION" value="move_save"  />
				</td>
			</tr>
EOF
;
}

sub unmerge_inner($)
{
	my $hash = shift;
	my %hash = %$hash;
	get_root($hash);#定义上级节点
	
	printf <<EOF
	<tr class="odd">
				<td class="add-div-type">请选择要分解的部门*</td>
				<td><select name="UNMERGE_FATHER" id="unmerge" onchange='refresh("$url","unmerge","unmerge")'>
EOF
;
	foreach my $node(@up_ary)
	{
		if($node =~ /^(.*)=(.*)$/)
		{
			if($1 eq $merge_id)
			{
				print "<option selected value='$1' >$2</option>";
			}else{
				print "<option value='$1' >$2</option>";
			}
		}
	}
printf <<EOF
				</select></td>
			</tr>
EOF
;

printf <<EOF
	<tr class="env">
		<td class="add-div-type">选择分解组 *</td>
		<td>
		<select multiple name="UNMERGE_CHILD"  id="unmerge_id" style="width:200px;height:150px;float:left;">
EOF
;
	my $host;
	my $net;
	my $count = 0;

	$hash = get_net_node($merge_id,\%hash);
	%hash = %$hash;
	$net = $hash{"net"};
	$host = $hash{"host"};

	my %net = %$net;
	my %host = %$host;
	foreach my $sub_net(sort keys %net)
	{
		my $temp = $net{$sub_net}{"host_name"}?$net{$sub_net}{"host_name"}:$net{$sub_net}{"type"};
		print "<option value='".$sub_net."' class='net'>".$temp."</option>";
		$count++;
	}
	foreach my $sub_host(sort keys %host)
	{
		my $temp = $host{$sub_host}{"host_name"}?$host{$sub_host}{"host_name"}:$host{$sub_host}{"ip"};
		print "<option value='".$sub_host."'   class='host' >".$temp."</option>";
		$count++;
	}
printf <<EOF	
	</select>
		<img src="/images/right.png" style="display:block;cursor:pointer;float:left;margin:10px;" onclick="add_group(event)" />
		<div id="unmerge_result" style="width:120px;height:150px;display:block;border:1px solid #999;float:left;overflow:auto;">
		</div>
		<a href="$url?action=unmerge&&line=$merge_id"  style="display:block;cursor:pointer;float:left;margin:10px 5px;" >【重新分解】</a>
		<span class="note" style='display:block;clear:both;'>点击箭头生成分组</span>
EOF
;
	if($count<=3)
	{
		print "<b style='color:red;'>当前部门的下属部门数目已经很少，不能再进行分解操作！</b>";
	}
printf <<EOF
	</td>
	</tr>
	<tr class="table-footer">
			<td colspan="3">
					<input class="net_button" type="submit" value="分解" id="submit"/>
					<input class="net_button" type="button" value="取消" onclick="hide()"/>
				    <input type="hidden" name="ACTION" value="unmerge_save"  />
			</td>
	</tr>
EOF
;
}

sub merge_inner($)
{
	my $hash = shift;
	my %hash = %$hash;
	printf <<EOF
	<tr class="odd">
				<td class="add-div-type">请选择待合并中的一个*</td>
				<td ><div id="merge_node"  style='width:60%;height:160px;overflow:auto;border:1px solid #999;' ><span class="note">注意：只能合并兄弟节点部门</span><ul>
EOF
;
			get_merge($hash);
printf <<EOF
				</ul></div></td>
			</tr>
EOF
;
printf <<EOF
	<tr class="env">
		<td class="add-div-type">合并后的部门名称 *</td>
		<td><input type="text" name="MERGE_NAME" id="merge_name" /></td>
	</tr>
	<tr class="table-footer">
			<td colspan="3">
					<input class="net_button" type="submit" value="合并" id="submit"/>
					<input class="net_button" type="button" value="取消" onclick="hide()"/>
				    <input type="hidden" name="ACTION" value="merge_save"  />
			</td>
	</tr>
EOF
;
}

sub edit_inner($)
{
	my $hash = shift;
	my %hash = %$hash;
	my $id = $par{'LINE'};
	my $temp;
	my $hostname = $par{'host_name'};
	
	printf <<EOF
	<tr class="odd">
				<td class="add-div-type">节点名称 *</td>
				<td>
					<input type="text" name="NAME" value="$hostname"/>
				</td>
	</tr>
EOF
;

if($par{'TYPE'} eq "host")
{
printf <<EOF
	<tr class="odd">
				<td class="add-div-type">节点类型 *</td>
				<td>
					<select name="SERVICE">
EOF
;
		foreach my $types(keys %node_type)
		{
			print "<option value='$types'>".$node_type{$types}."</option>";
		}
printf <<EOF
					</select>
				</td>
	</tr>
EOF
;
}

printf <<EOF
	<tr class="table-footer">
				<td colspan="3">
					<input class="net_button" type="submit" value="保存" id="submit" />
					<input class="net_button" type="button" value="取消" onclick="hide()"/>
				    <input type="hidden" name="ACTION" value="edit_save"  />
					<input type="hidden" name="NODE" value="$id"  />
					<input type = "hidden" name="line"  value = "$line" />
					<input type="hidden" name="TYPE" value="$par{'TYPE'}"  />
				</td>
	</tr>
EOF
;
}

sub add_inner($)
{
	my $hash = shift;
	my %hash = %$hash;
	get_root($hash);#定义上级节点
	printf <<EOF
			<tr class="odd">
				<td class="add-div-type">部门名称 *</td><td><input type="text" name="NAME" /></td></tr>
			<tr class="env"><td class="add-div-type">上级部门节点 *</td><td><select name="FATHER">
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
			</tr>
EOF
;
printf <<EOF				
			<tr class="table-footer">
				<td colspan="3">
					<input class="net_button" type="submit" value="添加" />
					<input class="net_button" type="button" value="取消" onclick="hide()"/>
				    <input type="hidden" name="ACTION" value="add_save"  />
				</td>
			</tr>
EOF
;
}

sub close_page()
{
	printf <<EOF
	<script src="/include/jquery.easyui.min.js" type="text/javascript"></script>
	<script src="/include/p_strawberry.min.js" type="text/javascript" language="javascript"></script>
	<script src="/include/draw_asset.js" type="text/javascript" language="javascript"></script>
	<script type="text/javascript" src="/include/asset.js"></script>
	</div></div></body></html>
EOF
;
}

sub note_box()
{
	&openbox('100%','left',_('逻辑资产'));
	print "<table width=\"100%\">";
	&no_tr(1,"当前还没有生成逻辑资产相关信息，请在物理资产页面中生成！");
	print "</table>";
	&closebox();
}

my $extraheader = '<link rel="stylesheet" type="text/css" href="/include/style.css">
	<link rel="stylesheet" type="text/css" href="/include/main.css">
	<link rel="stylesheet" type="text/css" href="/include/menu.css">
	<link rel="stylesheet" type="text/css" href="/include/content.css">
	<link href="/include/flowPath.css" type="text/css" rel="stylesheet" />
	<STYLE>v\:*{behavior:url(#default#VML);}</STYLE>';
&getcgihash(\%par);
&save();
&showhttpheaders();
&openpage(_('资产识别'), 1, $extraheader);
if(-e $config)
{
	&show_tree(\%hash);
	&show_content(\%hash);
	&show_action(\%hash);
}else{
	&note_box();
}

&close_page();