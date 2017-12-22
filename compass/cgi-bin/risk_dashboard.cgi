#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 风险概览页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================


require '/var/efw/header.pl';
my $config = "/var/efw/risk/logic/config";#逻辑配置文件
my $p_config = "/var/efw/risk/config";#逻辑配置文件

my %par = ();
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
	my $action = $par{'ACTION'};
	if($action eq "recycle")
	{
		my $string = read_file($p_config);
		my $p_hash = JSON::XS->new->decode($string);
		$p_hash = get_logic_config($p_hash);
		$p_hash = update_index($p_hash);
		write_config($config,_hashToJSON($p_hash));
	}
}

sub note_box()
{
	&openbox('100%','left',_('风险监控'));
	print "<table width=\"100%\">";
	&no_tr(1,"当前尚未生成逻辑资产，所以没有风险监控图！");
	print "</table>";
	&closebox();
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


sub _hashToJSON {
    my $hashref = shift;
    my %hash = %$hashref;
    my $json = '{';
    my @key_value_pairs = ();
    foreach $key (keys %hash) 
	{
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

#将物理拓扑图配置文件转换为逻辑拓扑图配置文件
sub get_logic_config($)
{
	my $hash = shift;
	my %hash = %$hash;
	foreach my $net(sort keys %hash)
	{
		$test .= $net."<br />";
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


sub open_page()
{
	printf <<EOF
<html xmlns:v>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>xjwGraphDemo</title>
	
	<link rel="stylesheet" type="text/css" href="/include/easyui.css">
	<link href="/include/flowPath.css" type="text/css" rel="stylesheet" />

	<STYLE>v\:*{behavior:url(#default#VML);}</STYLE>

</head>

<body class="easyui-layout bodySelectNone" id="body" onselectstart="return false">
	<div region="center"   title="风险监控区"  id="contextBody" class="mapContext" >
	</div>
	<div id="title" region="south" split="true" border="false"   title="工具栏" class="titleTool">
		
		<div region="east"  split="true"  title="辅助区"  class="auxiliaryArea" >
		<!-- 小地图 -->	
		<div id="smallMap"></div> 
		
		<div id="mainControl">
				<span id="ini_id" style="display:none;"></span>
				<table class="risk_table" style="float:left;">
				<tr>
					<td width="60px">IP地址 </td><td width="140px"> <span id="inputTitle" ></span>
				</tr>
				
				<tr><td>MAC地址 </td><td> <span id="inputMac" style="width:120px;" /></span>
				</tr>
				
				<tr><td>节点名称</td><td> <span  id="inputHost_name" style="width:200px;"  /></span>
				</tr>
				</table>
				
				<ul class='risk_button' style="float:left;">
				<li>
						<img alt="预览"	  title="预览拓扑图" src="/images/zoom.png"           onclick="graphUtils.printView()" class="buttonStyle"/>
						<form METHOD="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;" onsubmit="if(!confirm('确定将逻辑资产还原为最初状态？')){return false;}">
							<input class="imagebutton" type='image' NAME="submit" SRC="/images/recycle.png"  ALT="还原逻辑视图"   title="还原逻辑视图" />
							<INPUT TYPE="hidden" NAME="ACTION" VALUE="recycle">
						</form>
				</li>
				</ul>
		</div>
	</div>
	</div>
	</body>
	
	<script src="/include/jquery-1.6.min.js" type="text/javascript"></script>
	<script src="/include/jquery.easyui.min.js" type="text/javascript"></script>
	<script src="/include/strawberry.min.js" type="text/javascript" language="javascript"></script>
	<script src="/include/risk.js" type="text/javascript" language="javascript"></script>
	
</html>
EOF
;
}
&getcgihash(\%par);
&showhttpheaders();
if(-e $config)
{
	&open_page();
}else{
	&openpage(_('风险监控'), 1, $extraheader);
	&note_box();
	&closepage();
}
