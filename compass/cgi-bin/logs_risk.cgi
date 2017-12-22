#!/usr/bin/perl
#file:风险历史日志
#author:周圆

require '/var/efw/header.pl';
require 'logs_common.pl';
use POSIX();

my %cgiparams;
my %logsettings;
my $attfile = "/var/efw/risk/attacktype_order";
my $logfile="/var/log/risk/evaluation/";
my $config = "/var/efw/risk/logic/config";#逻辑配置文件
my $hash;
my $start;
my $prev;
my $next ;
my $prevday;
my $nextday ;
my $offset = 1;
my $date;
my $today;
my $years;
my $filetotal;
my $url =  $ENV{'SCRIPT_NAME'};
my $files_cur = "";

my @files = sort(glob("${logfile}*.tar"));
my $name = "maillog";
my @branch;
my @branch_host;
my @log;
my $filestr ="";
my $lines = 0;

my $test = "";

my $time = getDate(time);
my $branch_line = '0';#默认部门为0
my $host_line='all';#默认部门主机位全部
my $attack_id = '35';
my $branch_name = "根节点";
my $host_name   = "所有主机";
my $attack_name = "总攻击";

my $totaloffset = 0;
my $offset = 1;
my $viewsize = 100;

my @attack_log;
&getcgihash(\%cgiparams);


sub getDate($) {
    my $now = shift;
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
	localtime($now);
    $year += 1900;
    $mon++;
    return sprintf("%04d-%02d-%02d", $year, $mon, $mday);
}

sub dateToFilestring($) {
    my $date = shift;
    $date =~ s/\-//g;
    return $date;
}

sub dateToArray($) {
    my $date = shift;
    $date =~ s/\-//g;
    my @datearr = ($date =~ /^(\d{4})(\d{2})(\d{2})$/);
    return \@datearr;
}

sub read_file($)
{
	my $file =shift;
	my $string = "";
	open(MYFILE,"$file");
	foreach my $line (<MYFILE>) 
	{
		$string .= $line;
	}
	close (MYFILE);
	return $string;
}

sub save(){
	if(-e $config)
	{
		my $string = read_file($config);
		$string =~ s/\s//g;
		$string =~ s/\n//g;
		$string =~ s/\r//g;
		$hash = JSON::XS->new->decode($string);
		%hash = %$hash;
	}
	print uri_unescape($ENV{'QUERY_STRING'});
	if(uri_unescape($ENV{'QUERY_STRING'}) =~ /^time=(.*)&&attack=(.*)&&branch=(.*)&&host=(.*)&&attack_name=(.*)&&branch_name=(.*)&&host_name=(.*)$/)
	{
		$time = $1;
		$attack_id = $2;
		$branch_line = $3;
		$host_line = $4;
		$attack_name = $5;
		$branch_name = $6;
		$host_name =$7;
	}
	
	
	if ($cgiparams{'ACTION'} eq "delete") 
	{
		system("/usr/bin/sudo /home/httpd/cgi-bin/del_event.pl $filestr");
		@log=();
		$offset = 0;
		$totaloffset = 0;
	}
	
	if($cgiparams{'ACTION'} eq "DATE") 
	{
		$time = $cgiparams{'TIME'};
		if(!-e $logfile.$time."gz")
		{
			$errormessage = "不存在当前日期的日志";
		}
	}
	
	my $firstdatearr = dateToArray($firstdatestring);
	my $lastdatearr = dateToArray($today);

	if($cgiparams{'OFFSET'})
	{
		$attack_name = $cgiparams{'ATTACK'};
		$branch_name = $cgiparams{'BRANCH_NAME'};
		$host_name = $cgiparams{'HOST_NAME'};
	}
	if ($cgiparams{'OFFSET'} =~ /^\d+$/) {
		$offset = $cgiparams{'OFFSET'};
	}elsif($cgiparams{'OFFSET'}){
		$errormessage = "跳转页面必须输入整数,请重新输入,现在跳转到首页.";
	}
	
	$today = getDate(time);
	$date = $today;
	
	if ($cgiparams{'DATE'} =~ /[\d\/]+/) {
		$date = $cgiparams{'DATE'};
	}
}


sub stringToDate($) {
    my $date = shift;
    my $arr = dateToArray($date);
    return $lala = mktime(0, 0, 0, @$arr[2], @$arr[1] - 1, @$arr[0] - 1900);
}

sub config()
{
	my @t = split(/-/,$date);
	$years=$t[0];

	if (length($t[1]) == 1) {
		$t[1] = "0".$t[1];
		$date = "$t[0]-$t[1]-$t[2]";
	}

	if (length($t[2]) == 1) {
		$t[2] = "0".$t[2];
		$date = "$t[0]-$t[1]-$t[2]";
	}

	$filetotal=scalar(@files);
	if ($fileoffset > $filetotal) {
		$fileoffset = 0;
	}

	my ($firstdatestring) = ($files[0] =~ /\-(\d+).gz$/);
	if ($firstdatestring eq '') {
		$firstdatestring = dateToFilestring($today);
	}
	if ((dateToFilestring($date) < $firstdatestring) || (dateToFilestring($date) > dateToFilestring($today))) {
		$errormessage = _('Please select date between "%s" and "%s" ,now goto logs file for today!',$firstdatestring,dateToFilestring($today));
		$date = $today;
	}
 
	$filestr = $logfile;
	if ($date ne $today) {
		$filestr=$logfile.dateToFilestring($date).".tar";
	}else{
		if($host_line eq "all")
		{
			$filestr = $logfile."netorder/".$branch_line.".log";
		}else{
			$filestr = $logfile."hostorder/".$host_line.".log";
		}
	}
	
	if($attack_id eq 'all')
	{
		$attack_id = 35;
	}
	
	if($filestr =~ /tar/)
	{
		`tar -xvf $filestr`;
		if($host_line eq "all")
		{
			$files_cur = $logfile."netorder".$date."/".$branch_line.".log";
		}else{
			$filestr  = $logfile."netorder".$date."/".$host_line.".log";
		}
	}else{
		$files_cur = $filestr;
	}
	my $string = read_file($files_cur);
	my @temp = split("=",$string);
	foreach my $temp_line(@temp)
	{
		my @temp_slice = split("\n",$temp_line);
		my $temp_length = @temp_slice;
		for(my $i = 1;$i<$temp_length;$i++)
		{
			if($temp_slice[$i])
			{
				my @line_detail = split(",",$temp_slice[$i]);
				my $time_str = "";
				if($line_detail[$attack_id+1])
				{
					push(@log,$temp_slice[$i-1].",".$branch_name.",".$host_name.",".$attack_name.",".$line_detail[$attack_id+1]);
					push(@attack_log,$line_detail[$attack_id+1]);
				}else{
					$time_str = $temp_slice[$i];
				}
			}
		}
	}
	
	$totaloffset =@log%$viewsize?int(@log/$viewsize+1):@log/$viewsize;
	if ($offset > $totaloffset) {
		$offset = $totaloffset;
	}
	if ($offset == $totaloffset) {
		$prev = -1;
	}
	if ($offset == 1) {
		$next = -1;
	}
	if ($offset < 1) {
		$offset = 1;
	}
	
	$start = $viewsize * ($offset-1);
	if ($start < 0) {$start = 0;}
	$prev = $offset+1;
	$next = $offset-1;
}

 
sub show_content()
{

printf <<END
<table  style="width:100%;margin:15px 0 0 0;border-top:1px solid #999;">
<tr class="table-footer">
    <td width='20%' align='center' style="border-right:1px solid #999"><b>时间</b></td>
	<td width='20%' align='center' style="border-right:1px solid #999"><b>部门</b></td>
	<td width='20%' align='center' style="border-right:1px solid #999"><b>主机</b></td>
	<td width='20%' align='center' style="border-right:1px solid #999"><b>攻击类型</b></td>
    <td align='20%' ><b>风险值</b></td>
</tr>
</table>
<div style="max-height:250px;overflow:auto;">
<table width="100%">
END
;

my @slice = splice(@log, $start, $viewsize);

if ($logsettings{'LOGVIEW_REVERSE'} eq 'on') { @slice = reverse @slice; }

my $i = 0;
foreach my $line (@slice) {
    my @tmp = split(",",$line);
    if ($i % 2) {
		print "<tr class='env_thin'>\n";
    } else {
		print "<tr class='odd_thin'>\n";
    }
	my $times = deal_date($tmp[0]);
    printf <<END
	<td width='20%' >$times</td>
	<td width='20%' >$tmp[1]</td>
	<td width='20%' >$tmp[2]</td>
	<td width='20%' >$tmp[3]</td>
	<td width='20%' >$tmp[4]</td>
</tr>
END
;
    $i++;
}
if ($i==0) {
	no_tr(5,_('Current no content'));
}
print "</table></div>";

}

sub show_footer()
{

printf <<EOF
	<table style="width:100%;margin:0 auto;">
	<tr class="table-footer"><td>
	<form onsubmit="return confirm('确定要删除当天的日志？')" enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<input class='net_button' type='submit' style='color: black; background-image: url(\"/images/button.jpg\");' value='删除日志' name='routebutton'>
		<input type="hidden" name="ACTION" value="delete">
		<input type="hidden" name="DATE" value="$date">
	</form>
	</td>	
	<td width='2%' align='right'>
EOF
,_('Last day')
;
	if ($next != -1) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="OFFSET" value="1">
    <input type="hidden" name="BRANCH_NAME" value="$branch_name">
	<input type="hidden" name="ATTACK" value="$attack_id">
	<input type="hidden" name="HOST_NAME" value="$host_name">
    <input class='submitbutton' type="image" title='%s' name="ACTION" src="/images/first-page.png">
	</form>
END
,
_('First page')
;
    } else {

	print "<input class='submitbutton' type='image' name='ACTION' title='"._('First page')."' src='/images/first-page-off.png'>";
    }
    print "</td><td width='2%'>\n";
	if ($next != -1) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$next">
     <input type="hidden" name="BRANCH_NAME" value="$branch_name">
	<input type="hidden" name="ATTACK" value="$attack_id">
	<input type="hidden" name="HOST_NAME" value="$host_name">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/last-page.png">
	</form>
END
,
_('Last page')
;
    }
	else {

	print "<input class='submitbutton' type='image' name='ACTION' title='"._('Last page')."' src='/images/last-page-off.png'>";
    }
	printf <<END
		<td  align='center'>%s</td>
		<td  align='center'>%s</td>
END
,
_('Total %s pages',$totaloffset),
_('Current %s page',$offset),
;

    print "<td width='2%' align='right'>";
    if ($prev != -1) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
    <input type="hidden" name="OFFSET" value="$prev">
    <input type="hidden" name="BRANCH_NAME" value="$branch_name">
	<input type="hidden" name="ATTACK" value="$attack_id">
	<input type="hidden" name="HOST_NAME" value="$host_name">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/next-page.png">
	</form>
END
,
_('Next page')
;
    } else {
	print "<input class='submitbutton' type='image' name='ACTION' title='"._('Next page')."' src='/images/next-page-off.png'>";
    }
	print "</td><td width='2%'>\n";
	 if ($prev != -1) {
printf <<END
	<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
	<input type="hidden" name="OFFSET" value="$totaloffset">
    <input type="hidden" name="BRANCH_NAME" value="$branch_name">
	<input type="hidden" name="ATTACK" value="$attack_id">
	<input type="hidden" name="HOST_NAME" value="$host_name">
    <input class='submitbutton' type="image" name="ACTION" title='%s' src="/images/end-page.png">
    </form>
END
,
_('End page')
;
    } else {
	print "<input class='submitbutton' type='image' name='ACTION' title='"._('End page')."' src='/images/end-page-off.png'>";
    }
    printf <<END
		</td>
		<form enctype='multipart/form-data' method='post' action='$ENV{'SCRIPT_NAME'}'>
		<td  align='right' >%s: <input type="text" SIZE="2" name='OFFSET' VALUE="$offset">
        <input class='submitbutton' type='submit' name='ACTION' value='%s' /></td>
		<input type="hidden" name="BRANCH_NAME" value="$branch_name">
		<input type="hidden" name="ATTACK" value="$attack_id">
		<input type="hidden" name="HOST_NAME" value="$host_name">
		</form>
	
</tr>
</table>
END
,
_('Jump to Page'),
_('Go')
;
}

sub read_config_file($) {
    my @lines;
	my $file=shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

sub show_search()
{
	my @attlines = read_config_file($attfile);
    printf <<EOF
	<table width='100%' align='center'>
				<tr class='table-footer' >	
					<td width='220px'><span class="note" style='float:left;'>日期 &nbsp;</span>
						<form  method='post' action='$ENV{'SCRIPT_NAME'}' style='float:left;'>
						<input type="text" SIZE="12" id="inputDate" name='TIME' VALUE="$time" />
						<input type="submit" value="确定" />
						<input type="hidden" name="ACTION" value="DATE" />
						</form>
					</td>
					<td width='380px'>  <span class="note"  >攻击类型 </span>
						<select name="ATTACK_TYPE" id="attack" onchange='refresh("$url")' >
						
EOF
;
		if($attack_id eq 'all')
		{
			print '<option value="all" selected>--总攻击--</option>';
		}else{
			print '<option value="all" >--总攻击--</option>';
		}
		
		foreach my $line (@attlines) 
		{
			if ($line) {
				my @tmp = split(/,/,$line);
				if($attack_id eq $tmp[0])
				{
					$attack_name = $tmp[1]."--".$tmp[2];
					print "<option value='$tmp[0]' selected>$tmp[1]--$tmp[2]</option>";
				}else{
					print "<option value='$tmp[0]' >$tmp[1]--$tmp[2]</option>";
				}
			}
		}
printf <<EOF
						</select>
					</td>
					<td width='220px'>
						<span class="note">部门 </span> <select name="BRANCH" id="branch"  onchange='refresh("$url")' >
EOF
;
			get_branch($hash);
printf <<EOF
				</select> </td>
				<td>
				<span class="note">主机 </span>
				<select name="HOST" id='host'  onchange='refresh("$url")' >
EOF
;
			if($host_line eq "all")
			{
				print "<option value='all' selected >所有主机</option>";
			}else{
				print "<option value='all' >所有主机</option>";
			}
			get_branch_host($hash,$branch_line);
printf <<EOF
				</select>
				</td>
				</tr>
		</table>
		<script type="text/javascript"> 
			function refresh(href)
			{
				var time = document.getElementById("inputDate").value;
				var attack = document.getElementById("attack").value;
				var attack_name= document.getElementById("attack").options[document.getElementById("attack").selectedIndex].text;
				
				var branch = document.getElementById("branch").value;
				var branch_name = document.getElementById("branch").options[document.getElementById("branch").selectedIndex].text;
				
				var host = document.getElementById("host").value;
				var host_name = document.getElementById("host").options[document.getElementById("host").selectedIndex].text;
				
				location.href = href+"?time="+time+"&&attack="+attack+"&&branch="+branch+"&&host="+host+"&&attack_name="+attack_name+"&&branch_name="+branch_name+"&&host_name="+host_name;
			}		
			ESONCalendar.bind("inputDate");
		</script>
EOF
;
}

#获取部门
sub get_branch($)
{
	my $hash = shift;
	my %hash = %$hash;
	foreach my $net(sort keys %hash)
	{
		if($net ne "global")
		{
		if($branch_line eq $net)
		{
			print "<option value='$net' selected>";
			$branch_name =  $hash{$net}{"host_name"}?$hash{$net}{"host_name"}:$hash{$net}{"type"};
		}else{
			print "<option value='$net'>";
		}
		print $hash{$net}{"host_name"}?$hash{$net}{"host_name"}:$hash{$net}{"type"};
		print "</option>";
		get_branch($hash{$net}{"net"});
		}
	}
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


sub show_graph()
{
	my $host_top = count_host_branch('/var/log/risk/evaluation/hostorder/');
	$host_top = sorts($host_top,5);
	#$host_top = get_ip_branch($host_top,$hash);
	my $host_top_str = _hashToJSON($host_top);
	
	my $net_top = count_host_branch('/var/log/risk/evaluation/netorder/');
	$net_top = sorts($net_top,5);
	$net_top = get_branch_name($net_top,$hash);
	my $net_top_str = _hashToJSON($net_top);
	
	my $risk_top = count_risk('/var/log/risk/evaluation/netorder/');
	$risk_top = sorts($risk_top,5);
	my $risk_top_str = _hashToJSON($risk_top);
	
	my $risk_flow_str = join(",", @attack_log);
	printf <<EOF
	<div  class="hidden_class" id="host_top">$host_top_str</div>
	<div class="hidden_class" id="net_top"> $net_top_str </div>
	<div class="hidden_class" id="risk_top"> $risk_top_str </div>
	<div class="hidden_class"  id="risk_flow">$risk_flow_str</div>
	<table width="100%" height="200px">
	<tr>
	<td style="border-bottom:1px dotted #999;"><p class="note" style="text-align:center;height:20px;line-height:20px;" >$time 主机风险值Top5</p>
		<div id="host_top_pie" style="width:120px;height:120px;float:left;margin:10px 5px 10px 20px;"></div>
		<div id="host_top_pie_legend" style="width:80px;height:100px;float:left;margin-top:10px;"></div>
	</td>
	<td style="border-bottom:1px dotted #999;"><p class="note" style="text-align:center;height:20px;line-height:20px;" >$time 部门风险值Top5</p>
		<div id="net_top_pie" style="width:120px;height:120px;float:left;margin:10px 5px;"></div>
		<div id="net_top_pie_legend" style="width:80px;height:100px;float:left;margin-top:10px;"></div>
	</td>
	<td style="border-bottom:1px dotted #999;" ><p class="note" style="text-align:center;height:20px;line-height:20px;" >$time 攻击类型风险值Top5</p>
		<div id="risk_top_pie" style="width:120px;height:120px;float:left;margin:10px 5px;"></div>
		<div id="risk_top_pie_legend" style="width:250px;height:120px;float:left;margin-top:10px;"></div>
	</td>
	</tr>
	
	<tr>
	<td colspan="3"><p class="note" style="text-align:center;height:20px;line-height:20px;" >$time 【$attack_name】风险值曲线图</p>
		<div id="risk_flow_con" style="width:98%;height:120px;margin:5px auto;" ></div>
	</td>
	</tr>
	</table>

EOF
;
}


sub get_branch_name($$)
{
	my $riskref = shift;
	my %risk = %$riskref;
	my $hashref = shift;
    my %hash = %$hashref;
	my %new_risk = ();
	foreach my $id(sort keys %risk)
	{
		$id =~ /^(.*)\.log$/;
		if(get_net_name($1,\%hash))
		{
			$new_risk{get_net_name($1,\%hash)} = $risk{$id};
		}else{
			$new_risk{$id} = $risk{$id};
		}
	}
	return \%new_risk;
}


sub get_net_name($$)
{
	my $id = shift;
	my $hashref = shift;
	my %node_root = %$hashref;
	my $name = "";
	foreach my $net(sort keys %node_root)
	{
		if(compare($net,$id) == 2 ||compare($net,$id) == 4)#父级节点
		{
			$name = get_net_name($id,$node_root{$net}{'net'});
			last;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)<0)#兄弟节点
		{
			next;
		}elsif(compare($net,$id) == 5 && brother_distance($net,$id)>0)#兄弟节点
		{
			last;
		}elsif(compare($net,$id) == 0)#同一节点
		{
			return  $node_root{$net}{"host_name"};
			last;
		}
	}
}

#统计部门主机top5
sub count_host_branch($)
{
	my $file_name = shift;
	opendir (FILE, $file_name);
	my @file = readdir(FILE);
	my %risk_count = ();
	foreach my $files(@file)
	{
		if($files !~ /^\./)
		{
			my $str = read_file($file_name.$files);
			my @tmp = split("=",$str);
			my $risk_count = 0;
			foreach my $tmp(@tmp)
			{
				my @file_line = split("\n",$tmp);
				foreach my $file_line(@file_line)
				{
					if($file_line =~ /,(.*)$/)
					{
						my @line_temp = split(",",$file_line);
						my $length = @line_temp;
						$risk_count+= $line_temp[$length-1]+0;
					}
				}
			}
			$risk_count{$files} = $risk_count;
		}
	}
	closedir (FILE);
	return \%risk_count;
}

#通过主机ip获取其父级部门名称
sub get_ip_branch($$)
{
	my $riskref = shift;
	my %risk = %$riskref;
	my $hashref = shift;
    my %hash = %$hashref;
	
	foreach  my $ip(sort keys %risk)
	{
		#$test .= $ip."<br />";
		$risk = get_ip_branch_sub(\%risk,\%hash,$ip);
		%new_risk = %$risk;
	}
	return \%new_risk;
}

sub get_ip_branch_sub($$$)
{
	my $riskref = shift;
	my %risk = %$riskref;
	my $hashref = shift;
    my %hash = %$hashref;
	my $ip = shift;
	my %new_risk = ();
	
	foreach my $net(sort keys %hash)
	{
		my $host = $hash{$net}{'host'};
		my %host = %$host;
		my $is_match = 0;
		foreach my $hosts(sort keys %host)
		{
			if($host{$hosts}{'ip'} eq $ip)
			{
				my $title = $hash{$net}{'host_name'}?$hash{$net}{'host_name'}:$hash{$net}{'type'}.":".$host{$hosts}{'host_name'}." ".$ip;
				$new_risk{$title} = $risk{$ip};
				$is_match = 1;
				last;
			}
		}
		if($is_match){last;}
		$riskref = get_ip_branch_sub(\%risk,$hash{$net}{'net'});
		%new_risk = %$riskref;
	}
	return \%new_risk;
}

#统计风险top5
sub count_risk($)
{
	my $file_name = shift;
	opendir (FILE, $file_name);
	my @file = readdir(FILE);
	my %risk_count = ();
	foreach my $files(@file)
	{
		if($files !~ /^\./)
		{
			my $str = read_file($file_name.$files);
			my @tmp = split("=",$str);
			my $risk_count = 0;
			foreach my $tmp(@tmp)
			{
				my @file_line = split("\n",$tmp);
				foreach my $file_line(@file_line)
				{
					if($file_line =~ /,(.*)$/)
					{
						my @line_temp = split(",",$file_line);
						my $length = @line_temp;
						for(my $i = 0;$i<$length;$i++)
						{
							$risk_count{$i} += $line_temp[$i+1]+0;
						}
					}
				}
			}
		}
	}
	closedir (FILE);
	return \%risk_count;
}


sub sorts($$)
{
	my $hash = shift;
	my %hash = %$hash;
	my $length = shift;
	
	my $temp = 0;
	my @key = keys(%hash);
	my @value= values(%hash);
	my %new =();
	
	for(my $i =0;$i<$length;$i++)
	{
		for(my $j = $i+1;$j<@value-$i;$j++)
		{
			if($value[$i]<$value[$j])
			{
				$temp = $value[$i];
				$value[$i] = $value[$j];
				$value[$j] = $temp;
			
				$temp = $key[$i];
				$key[$i] = $key[$j];
				$key[$j] = $temp;
			}
		}
	}
	for(my $z = 0;$z<$length;$z++)
	{
		$new{$key[$z]} = $value[$z];
	}
	return \%new;
}

#获取$id部门下的主机
sub get_branch_host($$)
{
	my $hash = shift;
	my %node_root = %$hash;
	my $father_id = shift;
	foreach my $net(sort keys %node_root)
	{
		$test .= $net." ".$father_id." ".compare($net,$father_id)."<br />";
		if(compare($net,$father_id) == 2 || compare($net,$father_id) == 4)
		{
		     get_branch_host($node_root{$net}{'net'},$father_id);
			last;
		}elsif(compare($net,$father_id) == 5 && brother_distance($net,$father_id)<0)#兄弟节点
		{
			next;
		}elsif(compare($net,$father_id) == 5 && brother_distance($net,$father_id)>0)#兄弟节点
		{
			last;
		}elsif(compare($net,$father_id) == 0)#同一节点
		{
			my $hosts = $node_root{$net}{"host"};
			my %hosts = %$hosts;
			foreach my $host(sort keys %hosts)
			{
				my $name = $hosts{$host}{"host_name"}?$hosts{$host}{"host_name"}." ".$hosts{$host}{"ip"}:$hosts{$host}{"ip"};
				if($host_line eq $hosts{$host}{"ip"})
				{
					print "<option value='".$hosts{$host}{"ip"}."' selected >".$name."</option>";
				}else{
					print "<option value='".$hosts{$host}{"ip"}."' >".$name."</option>";
				}
			}
		}
	}
}


sub note_box()
{
	&openbox('100%','left',_('风险历史日志'));
	print "<table width=\"100%\">";
	&no_tr(1,"当前尚无日志数据，请查看风险监控功能是否开启！");
	print "</table>";
	&closebox();
}
	
&showhttpheaders();
$extraheaders = <<EOF
<script type="text/javascript" src="/include/ESONCalendar.js"></script>
<link rel="stylesheet" href="/include/datepicker/css/datepicker.css" type="text/css" />
<script language="javascript" type="text/javascript" src="/include/excanvas.js"></script>
<script language="javascript" type="text/javascript" src="/include/jquery.flot.js"></script>
<link rel="stylesheet" href="/include/flotpie.css" type="text/css" />
<script type="text/javascript" src="/include/jquery.flot.pie.js"></script>
<script language="javascript" type="text/javascript" src="/include/log_risk.js"></script>
EOF
;
&openpage(_('SMTP log'), 1, $extraheaders);
if(-e $config)
{
&save();
&config();
if(!-e $files_cur)
{
	$errormessage = "不存在当前日期日志";
}
&openbigbox($errormessage, $warnmessage, $notemessage);
&openbox('100%', 'left', _('风险监控历史日志'));
&show_search();
if(-e $files_cur)
{
&show_graph();
}
&show_content();
&show_footer();
&closebox();
}else{
	note_box()
}
&closepage();


