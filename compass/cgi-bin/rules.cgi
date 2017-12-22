#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION:入侵防御规则界面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/10/20-11:04       
#===============================================================================


require '/var/efw/header.pl';
my $rules          = '/etc/snort/rules/auto';#规则集文件存在目录
my $dis_dir        = '/etc/snort/rules/rulecn';#规则集文件描述信息
my $rule_conf      = '/var/efw/snort/policies';#规则配置文件
my $rule_exception = '/var/efw/snort/exceptions';#单条规则配置文件
my %rule_detail_hash = ();
my %rule_conf_hash =();
my %exception_hash =();
my %par = ();
my $action = "";
my $subaction = "";
my $count ="";
my $page = "";
my $sensive = "";
my $is_cur_rule ="";

#判断当前操作是否要重启入侵防御服务
my $reload = 0;
my $restart = 0;
my $needreload = "/var/efw/snort/needreload";

my $first_edit = 0;
my $is_serach = 0;#判断当前是否处于搜索模式
my $last_search = "";#上一次搜索的内容
my $last_match  = "";#上一次匹配大小写
my $last_cur    = "";#上一次是否只在当前编辑状态下的规则集中搜索

#当前所选规则集的名称，告警方式，启用状态
my $ruleset_name = "";
my $ruleset_name_ch = "";
my $ruleset_action = "";
my $ruleset_active = "";
my $search_text = "";

my $cur_page = 1;#当前规则显示页数
my $per_page = 100;#规则每页显示条数
my $is_editing = 0;
my $is_click = 0;
my $ruleset_height = '';
my $sub_line = "";

#动作中出现的图片src
my $action_img = "";
my $active_img = "";
my $edit_img   = "/images/edit.png";

my $sub_action_img = "";
my $sub_active_img = "";

#分页按钮的图片src
my $first_page = "/images/first-page.gif";
my $last_page = "/images/last-page.gif";
my $next_page = "/images/next-page.gif";
my $end_page = "/images/end-page.gif";

my $action_title = "";
my $active_title = "";
my $edit_title   = "单条规则编辑";
my $sub_action_title = "";
my $sub_active_title = "";
my $sub_delete_title = "";

my %pri_set = (
	"icmp-event"              => "<span class='green'><b>低</b></span>",
	"misc-activity"           => "<span class='green'><b>低</b></span>",
	"protocol-command-decode" => "<span class='green'><b>低</b></span>",
	"network-scan"            => "<span class='green'><b>低</b></span>",
	"tcp-connetion"           => "<span class='green'><b>低</b></span>",
	"string-detect"           => "<span class='green'><b>低</b></span>",
	"not-suspicious"          => "<span class='green'><b>低</b></span>",
	"unknown"                 => "<span class='green'><b>低</b></span>",
	"policy-violation"        => "<span class='red'><b>高</b></span>",
	"attempted-user"          => "<span class='red'><b>高</b></span>",
	"inappropriate-content"   => "<span class='red'><b>高</b></span>",
	"unsuccessful-user,"      => "<span class='red'><b>高</b></span>",
	"web-application-attack"  => "<span class='red'><b>高</b></span>",
	"successful-user"         => "<span class='red'><b>高</b></span>",
	"attempted-admin"         => "<span class='red'><b>高</b></span>",
	"trojan-activity"         => "<span class='red'><b>高</b></span>",
	"successful-admin"        => "<span class='red'><b>高</b></span>",
	"shellcode-detect"        => "<span class='red'><b>高</b></span>",
	""                        => "<span class='red'><b>高</b></span>",
);

#显示规则列表
sub display_rulesset()
{
	@dir = read_config_files($rule_conf);
	printf <<EOF
	<br /><div style="width:96%;margin:0px auto;">
	<table style="width:100%;" class="ruleslist">
	<tr>
			<td class="boldbase" width="140px">%s</td>
            <td class="boldbase" width="60px">%s</td>
			<td class="boldbase" >%s</td>
            <td class="boldbase" width="120px">%s</td>
	</tr>
	</table>
EOF
,_("规则集名")
,_("规则数")
,_("描述")
,_("活动/动作")
;


	print '<div id="rule_set_div" style="margin:0px auto;overflow:scroll;"><table style="width:100%;" class="ruleslist" id="rule_set">';
	my $line = 0;
	foreach my $rule_file (@dir) {
		my @temp_ruleset =split(/,/,$rule_file);
		$temp_ruleset[0] =~ s/auto\///g;
		
		my $dealt_rule = $temp_ruleset[0];
		   $dealt_rule =~ s/emerging-//g;
		my $rule_count = count_rule($dealt_rule);
		my $bgcolor;
		
		#屏蔽规则数为0的规则
		if($rule_count>0 && $dealt_rule=~ /\.rules/)
		{
			if($rule_conf_hash{'action'.$dealt_rule} eq 'drop')
			{
				$action_img = "/images/action_drop.png";
				$action_title = "当前状态:阻断";
			}elsif($rule_conf_hash{'action'.$dealt_rule} eq 'alert')
			{
				$action_img = "/images/action_alert.png";
				$action_title = "当前状态:告警";
			}
			
			if($rule_conf_hash{'active'.$dealt_rule} eq 'on')
			{
				$active_img = "/images/on.png";
				$active_title = "启动(点击按钮禁止)";
			}elsif($rule_conf_hash{'active'.$dealt_rule} eq 'off')
			{
				$active_img = "/images/off.png";
				$active_title = "禁止(点击按钮启用)";
			}
		my $cur_line = $par{'CUR_LINE'};
		#my $bgcolor = setbgcolor($is_editing,$cur_line,$line);
		#if($bgcolor ne "selected")
		#{
		#	$bgcolor = "";
		#}
		if("emerging-".$dealt_rule eq $ruleset_name)
		{
			$bgcolor = "selected";
		}
		
		printf <<EOF
		<tr  class="$bgcolor">
		<td class="$bgcolor note" width="140px">$rule_detail_hash{$dealt_rule}</td>
		<td class="$bgcolor" width="60px">$rule_count</td>
		<td class="$bgcolor" >$rule_detail_hash{'dis'.$dealt_rule}</td>
		<td class="$bgcolor" width="103px">
		<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
		<input  type='image' name="submit" src="$action_img" title="$action_title"/>
		<input type="hidden" name="ACTION" value="$rule_conf_hash{'action'.$dealt_rule}">
		<input type="hidden" name="RULE" value="$dealt_rule">
		<input type="hidden" name="ACTIVE" value="$rule_conf_hash{'active'.$dealt_rule}">
		<input type="hidden" name="NAME" value="emerging-$dealt_rule">
		<input type="hidden" name="RULE_SET_ACTION" value="$rule_conf_hash{'action'.$dealt_rule}">
		<input type="hidden" name="RULE_SET_ACTIVE" value="$rule_conf_hash{'active'.$dealt_rule}">
		<input type="hidden" name="CUR_LINE" value="$line">
		<input type="hidden" name="RULE_SET_CH" value="$rule_detail_hash{$dealt_rule}">
		<input type="hidden" name="FIRST_EDIT" value="$first_edit">
		<input type="hidden" name="SEARCH_TEXT" value="$search_text">
		<input type="hidden" name="IS_SEARCH" value="$is_search">
		</form>
		<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
		<input  type='image' name="submit" src="$active_img" title="$active_title"/>
		<input type="hidden" name="ACTION" value="$rule_conf_hash{'active'.$dealt_rule}">
		<input type="hidden" name="RULE" value="$dealt_rule">
		<input type="hidden" name="ACTIONS" value="$rule_conf_hash{'action'.$dealt_rule}">
		<input type="hidden" name="NAME" value="emerging-$dealt_rule">
		<input type="hidden" name="RULE_SET_ACTION" value="$rule_conf_hash{'action'.$dealt_rule}">
		<input type="hidden" name="RULE_SET_ACTIVE" value="$rule_conf_hash{'active'.$dealt_rule}">
		<input type="hidden" name="CUR_LINE" value="$line">
		<input type="hidden" name="RULE_SET_CH" value="$rule_detail_hash{$dealt_rule}">
		<input type="hidden" name="FIRST_EDIT" value="$first_edit">
		<input type="hidden" name="SEARCH_TEXT" value="$search_text">
		<input type="hidden" name="IS_SEARCH" value="$is_search">
		</form>
		<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
		<input type="hidden" name="ACTION" value="edit">
		<input  type='image' name="submit" src="$edit_img" title="$edit_title"/>
		<input type="hidden" name="RULE_SET_CH" value="$rule_detail_hash{$dealt_rule}">
		<input type="hidden" name="NAME" value="emerging-$dealt_rule">
		<input type="hidden" name="RULE_SET_ACTION" value="$rule_conf_hash{'action'.$dealt_rule}">
		<input type="hidden" name="RULE_SET_ACTIVE" value="$rule_conf_hash{'active'.$dealt_rule}">
		<input type="hidden" name="CUR_LINE" value="$line">
		</form>
		</td>
		</tr>
EOF
;
	$line++;
	}
  }
  
  print '</table>';
if($line eq 0){
	print "<table style='margin:0px auto;'>";
	no_tr(4,"当前无规则集");
	print "</table>";
}
	my $check_show = "";
	if(!$first_edit)
	{
		$check_show = "class='hidden_class'";
	}
	printf <<EOF
	</div><table style='margin:0px auto;border:1px solid #999;border:0px 1px;'><tr class='table-footer'>
	<td  style="text-align:left;">
	<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;" onsubmit="return search_check();">
	规则搜索:&nbsp;关键字(关键字长度不小于2个) <input type="text" id="search_text" name="search_text" style="width:200px;" value="$last_search"/>&nbsp;&nbsp;
	 <input type="checkbox"  name ="SENSIVE"  $last_match/> 匹配大小写&nbsp;&nbsp;
			<span $check_show>&nbsp;<input type="checkbox"  name ="IS_CUR_RULE"   $last_cur />只在当前编辑的规则集中搜索&nbsp;&nbsp;</span>
			<input type="submit"  value="GO" >
			<input type="hidden" name="ACTION" value="search" >
			<input type="hidden" name="NAME" value="$ruleset_name">
			<input type="hidden" name="CUR_LINE" value="$line">
			<input type="hidden" name="FIRST_EDIT" value="$first_edit">
	</form>
	</td>
	<td>&nbsp;</td>
	</tr></table></div>
EOF
;
}

sub count_rule($)
{
  my $dir=shift;
  my $line;
  $dir = $rules."/".$dir;
  my $count=0;
  open(FD,"$dir");
  chomp($line);
  foreach my $line (<FD>) {
	   $line=~s/^\s*//;
	  if($line!~/^#/ )
	  { 
		  if($line !~/^$/)
		  {
			$count++;
		  }
	  }
  }
  close(FD);
  return $count;
}

sub read_config_files($) {
    my @lines;
	my $file = shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}


#读取规则描述信息
sub read_dis()
{
	foreach my $dis (read_config_files($dis_dir)){
		chomp($dis);
		my @lines=split(/,/,$dis);
		my $discription = "";
		for(my $i=2;$i<@lines;$i++)
		{
			if($i == @lines-1)
			{
				$discription .= $lines[$i];
			}else{
				$discription .= $lines[$i]."，";
			}
		}
		$rule_detail_hash{$lines[0]} = $lines[1];
		$rule_detail_hash{"dis".$lines[0]} = $discription;
	 }
}

sub read_rule_conf()
{
	#将当前规则配置信息读入数组conf
	my @conf = read_config_files($rule_conf);
	foreach my $conf(@conf)
	{
		my @temp = split(",",$conf);
		$temp[0] =~ s/auto\///g;
		$rule_conf_hash{'action'.$temp[0]} = $temp[1];
		$rule_conf_hash{'active'.$temp[0]} = $temp[2];
	}
}

#修改规则集
sub update_rule_conf($$$)
{
	my $temp_name   = shift;
	my $temp_action = shift;
	my $temp_active = shift;
	$rule_conf_hash{'action'.$temp_name} = $temp_action;
	$rule_conf_hash{'active'.$temp_name} = $temp_active;
}

sub save_excption()
{
	my $new_line = "";
	foreach my $key(keys %exception_hash)
	{
		if($key =~ /^action/)
		{
			$key =~ s/action//g;
			$new_line .= $key.",".$exception_hash{"action".$key}.",".$exception_hash{"active".$key}."\n";
		}
	}
	open(FILE,">$rule_exception");
	print FILE $new_line;
	close(FILE);
	`sudo fmodify $rule_exception`;
}

#保存规则集文件
sub save_rule_conf()
{
	opendir(DIR,$rules);
	my @dir=readdir(DIR);
	closedir(DIR);
	my @new_rule;
	open(FILE,">$rule_conf");
	foreach my $rule_dir(@dir)
	{
		$rule_dir =~ s/emerging-//g;
	
		if($rule_conf_hash{'action'.$rule_dir} && $rule_conf_hash{'active'.$rule_dir})
		{
			my $new_line = "auto/".$rule_dir.",".$rule_conf_hash{'action'.$rule_dir}.",".$rule_conf_hash{'active'.$rule_dir};
			print FILE "$new_line\n";
		}
	}
	close(FILE);
	`sudo fmodify $rule_conf`;
}

#修改规则集
sub update_excption($$$)
{
	my $temp_sid   = shift;
	my $temp_action = shift;
	my $temp_active = shift;
	$exception_hash{'action'.$temp_sid} = $temp_action;
	$exception_hash{'active'.$temp_sid} = $temp_active;
}

#删除规则集
sub delete_excption($)
{
	my $temp_sid   = shift;
	delete ($exception_hash{'action'.$temp_sid});
	delete ($exception_hash{'active'.$temp_sid});
}


sub save()
{
	$action = $par{'ACTION'};
	if($action eq 'apply')
	{
		system("rm $needreload");
		system("sudo /usr/local/bin/restartsnort");
		`sudo fcmd "/usr/local/bin/restartsnort"`;
		$restart = 1;
		$ruleset_name = $par{'CUR_NAME'};
		$cur_page = $par{'CUR_PAGE'};
		$count = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$first_edit = $par{'FIRST_EDIT'};
		$search_text = $par{'SEARCH_TEXT'};
		$last_search = $search_text;
		$is_cur_rule = $par{'IS_CUR_RULE'};
		$sensive = $par{'SENSIVE'};
		
		if($par{'IS_CUR_RULE'} eq "on")
		{
			$last_cur		 = "checked";
		}
		if($par{'SENSIVE'} eq "on")
		{
			$last_match     = "checked";
		}
		$sub_line        = $par{'SUB_LINE'};
		$ruleset_action= $par{'CUR_ACTION'};
		$ruleset_active = $par{'CUR_ACTIVE'};
		
		if($ruleset_name_ch)
		{
			$is_editing = 1;
		}elsif($search_text)
		{
			$is_search = 1;
		}
	}elsif($action eq 'drop')
	{
		my $rulesets_name =  $par{'RULE'};
		my $rulesets_active =  $par{'ACTIVE'};
		$ruleset_action  = "alert";
		$ruleset_active  = $par{'RULE_SET_ACTIVE'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$ruleset_name    = $par{'NAME'};
		$first_edit    = $par{'FIRST_EDIT'};
		$search_text   = $par{'SEARCH_TEXT'};
		$is_search     = $par{'IS_SEARCH'};
		&update_rule_conf($rulesets_name,'alert',$rulesets_active);
		&save_rule_conf();
		$reload = 1;
		$is_editing = 1;
	}elsif($action eq 'alert')
	{
		my $rulesets_name =  $par{'RULE'};
		my $rulesets_active =  $par{'ACTIVE'};
		$ruleset_action  = "drop";
		$ruleset_active  = $par{'RULE_SET_ACTIVE'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$ruleset_name    = $par{'NAME'};
		$first_edit    = $par{'FIRST_EDIT'};
		$search_text   = $par{'SEARCH_TEXT'};
		$is_search     = $par{'IS_SEARCH'};
		&update_rule_conf($rulesets_name,'drop',$rulesets_active);
		&save_rule_conf();
		$reload = 1;
		$is_editing = 1;
	}elsif($action eq 'on')
	{
		my $rulesets_name =  $par{'RULE'};
		my $rulesets_action =  $par{'ACTIONS'};
		$ruleset_action  = $par{'RULE_SET_ACTION'};
		$ruleset_active  = "off";
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$ruleset_name    = $par{'NAME'};
		$first_edit    = $par{'FIRST_EDIT'};
		$search_text   = $par{'SEARCH_TEXT'};
		$is_search     = $par{'IS_SEARCH'};
		&update_rule_conf($rulesets_name,$rulesets_action,'off');
		&save_rule_conf();
		$reload = 1;
		$is_editing = 1;
	}elsif($action eq 'off')
	{
		my $rulesets_name   =  $par{'RULE'};
		my $rulesets_action =  $par{'ACTIONS'};
		$ruleset_action  = $par{'RULE_SET_ACTION'};
		$ruleset_active  = "on";
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$ruleset_name    = $par{'NAME'};
		$first_edit    = $par{'FIRST_EDIT'};
		$search_text   = $par{'SEARCH_TEXT'};
		$is_search     = $par{'IS_SEARCH'};
		&update_rule_conf($rulesets_name,$rulesets_action,'on');
		&save_rule_conf();
		$reload = 1;
		$is_editing = 1;
	}elsif($action eq 'edit')
	{
		$ruleset_name    = $par{'NAME'};
		$ruleset_action  = $par{'RULE_SET_ACTION'};
		$ruleset_active  = $par{'RULE_SET_ACTIVE'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		
		$is_editing = 1;
		$first_edit = 1;
	}elsif($action eq 'search')
	{
		$is_search = 1;
		$is_editing = 1;
		$ruleset_active  = $par{'RULE_SET_ACTIVE'};
		$sensive = $par{"SENSIVE"};
		$is_cur_rule = $par{"IS_CUR_RULE"};
		if($par{'IS_CUR_RULE'} eq "on")
		{
			$ruleset_name    = $par{'NAME'};
			$ruleset_name_ch = $par{'RULE_SET_CH'};
			$first_edit      = $par{'FIRST_EDIT'};
			$last_cur		 = "checked";
		}
		if($par{'SENSIVE'} eq "on")
		{
			$last_match = "checked";
		}
		$search_text     = $par{"search_text"}; 
		$last_search     = $search_text;
	}
	
	$page = $par{'PAGE'};
	if($page eq 'NEXT')
	{
		$ruleset_name = $par{'CUR_NAME'};
		$ruleset_action  = $par{'CUR_ACTION'};
		$ruleset_active  = $par{'CUR_ACTIVE'};
		$cur_page     = $par{'CUR_PAGE'};
		$count        = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$first_edit    = $par{'FIRST_EDIT'};

		$is_editing = 1;
		if($cur_page<$count)
		{
			$cur_page++;
		}
	}elsif($page eq 'LAST')
	{
		$ruleset_name    = $par{'CUR_NAME'};
		$ruleset_action  = $par{'CUR_ACTION'};
		$ruleset_active  = $par{'CUR_ACTIVE'};
		$cur_page        = $par{'CUR_PAGE'};
		$count        = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		
		$first_edit    = $par{'FIRST_EDIT'};
		$is_editing = 1;
		if($cur_page>1)
		{
			$cur_page--;
		}
	}elsif($page eq 'FIRST')
	{
		$ruleset_name = $par{'CUR_NAME'};
		$ruleset_action  = $par{'CUR_ACTION'};
		$ruleset_active  = $par{'CUR_ACTIVE'};
		$cur_page     = $par{'CUR_PAGE'};
		$count        = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$first_edit    = $par{'FIRST_EDIT'};
		$is_editing = 1;
		if($cur_page!= 1)
		{
			$cur_page = 1;
		}
	}elsif($page eq 'END')
	{
		$ruleset_name = $par{'CUR_NAME'};
		$ruleset_action  = $par{'CUR_ACTION'};
		$ruleset_active  = $par{'CUR_ACTIVE'};
		$cur_page     = $par{'CUR_PAGE'};
		$count        = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$first_edit    = $par{'FIRST_EDIT'};
		$reload = $par{'RELOAD'};
		$restart = $par{'RESTART'};
		
		$is_editing = 1;
		if($cur_page<$count)
		{
			$cur_page = $count;
		}
	}
	
	$subaction = $par{'SUB_ACTION'};
	if($subaction eq "alert")
	{
		my $rule_sid    =  $par{'SID'};
		my $rule_active =  $par{'SUB_ACTIVE'};
		$ruleset_name   = $par{'CUR_NAME'};
		$ruleset_action = $par{'CUR_ACTION'};
		$ruleset_active = $par{'CUR_ACTIVE'};
		$cur_page       = $par{'CUR_PAGE'};
		$count          = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$sub_line        = $par{'LINE'};
		$first_edit    = $par{'FIRST_EDIT'};
		
		
		$is_editing = 1;
		$is_click   = 1;
		$reload     = 1;
		
		&update_excption($rule_sid,'drop',$rule_active);
		&save_excption();
	}elsif($subaction eq "drop")
	{
		my $rule_sid    =  $par{'SID'};
		my $rule_active =  $par{'SUB_ACTIVE'};
		$ruleset_name   = $par{'CUR_NAME'};
		$ruleset_action = $par{'CUR_ACTION'};
		$ruleset_active = $par{'CUR_ACTIVE'};
		$cur_page       = $par{'CUR_PAGE'};
		$count          = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$sub_line        = $par{'LINE'};
		$first_edit    = $par{'FIRST_EDIT'};
		
		
		$is_editing = 1;
		$is_click   = 1;
		$reload = 1;
		
		&update_excption($rule_sid,'alert',$rule_active);
		&save_excption();
	}elsif($subaction eq "on")
	{
		my $rule_sid    =  $par{'SID'};
		my $rule_action =  $par{'SUB_CUR_ACTION'};
		$ruleset_name   = $par{'CUR_NAME'};
		$ruleset_action = $par{'CUR_ACTION'};
		$ruleset_active = $par{'CUR_ACTIVE'};
		$cur_page       = $par{'CUR_PAGE'};
		$count          = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$sub_line        = $par{'LINE'};
		$reload = 1;
		$first_edit    = $par{'FIRST_EDIT'};
		
		$is_editing = 1;
		$is_click   = 1;
		$reload     = 1;
		&update_excption($rule_sid,$rule_action,'off');
		&save_excption();
	}elsif($subaction eq "off")
	{
		my $rule_sid    =  $par{'SID'};
		my $rule_action =  $par{'SUB_CUR_ACTION'};
		$ruleset_name   = $par{'CUR_NAME'};
		$ruleset_action = $par{'CUR_ACTION'};
		$ruleset_active = $par{'CUR_ACTIVE'};
		$cur_page       = $par{'CUR_PAGE'};
		$count          = $par{'COUNT'};
		$ruleset_name_ch = $par{'RULE_SET_CH'};
		$sub_line        = $par{'LINE'};
		$first_edit    = $par{'FIRST_EDIT'};
		
		
		$is_editing = 1;
		$is_click   = 1;
		$reload = 1; 
		
		&update_excption($rule_sid,$rule_action,'on');
		&save_excption();
	}
	
	my $search_action = $par{'SUB_SEAR_ACTION'};
	if($search_action eq "alert")
	{
		my $rule_sid    =  $par{'SID'};
		my $rule_active =  $par{'SUB_SEAR_ACTIVE'};
		$search_text    =  $par{'SEARCH_TEXT'};
		$last_search     = $search_text;
		$sub_line       =  $par{'LINE'};
		$is_cur_rule  = $par{'IS_CUR_RULE'};
		$sensive = $par{'SENSIVE'};
		if($par{'IS_CUR_RULE'} eq "on")
		{
			$last_cur		 = "checked";
			$ruleset_name    = $par{"NAME"};
			$first_edit      = 1;
		}
		if($par{'SENSIVE'} eq "on")
		{
			$last_match = "checked";
		}
		$is_search = 1;
		$reload     = 1;
		&update_excption($rule_sid,'drop',$rule_active);
		&save_excption();
	}elsif($search_action eq "drop")
	{
		my $rule_sid    =  $par{'SID'};
		my $rule_active =  $par{'SUB_SEAR_ACTIVE'};
		$search_text    =  $par{'SEARCH_TEXT'};
		$last_search     = $search_text;
		$sub_line       =  $par{'LINE'};
		$is_cur_rule  = $par{'IS_CUR_RULE'};
		$sensive = $par{'SENSIVE'};
		if($par{'IS_CUR_RULE'} eq "on")
		{
			$last_cur		 = "checked";
			$ruleset_name =  $par{"NAME"};
			$first_edit      = 1;
		}
		if($par{'SENSIVE'} eq "on")
		{
			$last_match = "checked";
		}
		$is_search = 1;
		$reload     = 1;
		&update_excption($rule_sid,'alert',$rule_active);
		&save_excption();
	}elsif($search_action eq "on")
	{
		my $rule_sid    =  $par{'SID'};
		my $rule_cur_action =  $par{'SUB_SEAR_CUR_ACTION'};
		$search_text    =  $par{'SEARCH_TEXT'};
		$last_search     = $search_text;
		$sub_line       =  $par{'LINE'};
		$is_search = 1;
		$reload     = 1;
		$is_cur_rule  = $par{'IS_CUR_RULE'};
		$sensive = $par{'SENSIVE'};
		if($par{'IS_CUR_RULE'} eq "on")
		{
			$last_cur		 = "checked";
			$ruleset_name = $par{"NAME"};
			$first_edit      = 1;
		}
		if($par{'SENSIVE'} eq "on")
		{
			$last_match = "checked";
		}
		&update_excption($rule_sid,$rule_cur_action,'off');
		&save_excption();
	}elsif($search_action eq "off")
	{
		my $rule_sid    =  $par{'SID'};
		my $rule_cur_action =  $par{'SUB_SEAR_CUR_ACTION'};
		$search_text    =  $par{'SEARCH_TEXT'};
		$last_search     = $search_text;
		$sub_line       =  $par{'LINE'};
		$is_cur_rule  = $par{'IS_CUR_RULE'};
		$sensive = $par{'SENSIVE'};
		if($par{'IS_CUR_RULE'} eq "on")
		{
			$last_cur		 = "checked";
			$ruleset_name = $par{"NAME"};
			$first_edit      = 1;
		}
		if($par{'SENSIVE'} eq "on")
		{
			$last_match = "checked";
		}
		$is_search = 1;
		$reload     = 1;
		&update_excption($rule_sid,$rule_cur_action,'on');
		&save_excption();
	}
}

sub display_search()
{
	
	if($is_search)
	{
		printf <<EOF
	<br /><div style="width:96%;margin:0px auto;">
	<table style="width:100%;" class="ruleslist" >
		<tr>
			<td class="boldbase" width="150px" >%s</td>
			<td class="boldbase" width="100px">%s</td>
			<td class="boldbase" >%s</td>
            <td class="boldbase" width="100px">%s</td>
			<td class="boldbase" width="100px">%s</td>
            <td class="boldbase" width="120px">%s</td>
		</tr>
	</table>
EOF
,_("所在规则集")
,"ID"
,_("规则描述")
,_("协议")
,_("危险级")
,_("活动/动作")
;
	my $pro = "";#协议
	my $rule_dis ="";#描述
	my $sid = "";#sid
	my $prio = "";#
	

	print '<div class="search_div" id="search_div" style="height:160px;margin:0px auto;overflow-y:scroll;"><table  style="width:100%;" id="search_table" class="ruleslist">';
		
	my @dir = read_config_files($rule_conf);
	my $i = 0;

		foreach my $file(@dir)
		{
		@temp_file = split(/,/,$file);
		$temp_file[0] =~ s/auto\///g;
		my $dir = $rules."/".$temp_file[0];
		my @ruleset_detail= read_config_files($dir);
		foreach my $line (@ruleset_detail) {
			chomp($line);
			my $is_match = 0;
			if ($line !~/^#/ && $line) 
			{
				if($line=~/msg:"([^:]+)".*classtype:(.*);.*sid:(\d+)/)
				{
					my @temp = split(/\s/,$line);
					$pro = $temp[1];
					$rule_dis = $1;
					$sid = $3;
					@splited = split(/;/,$2);
					$prio= $pri_set{$splited[0]};
					my $temp_sid = "";
					if(!$prio)
					{
						$prio = "<span class='orange'><b>中</b></span>";
					}
					$temp_sid = $sid;
					#搜索匹配关键字
					if($sensive ne "on")#匹配大小写
					{
						if($rule_dis =~ /($search_text)/i)
						{
							my $temp = $1;
							$rule_dis =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($sid =~ /($search_text)/i)
						{
							my $temp = $1;
							$temp_sid =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($pro =~ /($search_text)/i)
						{
							my $temp = $1;
							$pro =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($prio =~ /($search_text)/i)
						{
							my $temp = $1;
							$pro =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
					}else{#匹配不区分大小写
						if($rule_dis =~ /($search_text)/)
						{
							my $temp = $1;
							$rule_dis =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($sid =~ /($search_text)/)
						{
							my $temp = $1;
							$temp_sid =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($pro =~ /($search_text)/)
						{
							my $temp = $1;
							$pro =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($prio =~ /($search_text)/)
						{
							my $temp = $1;
							$pro =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
					}
					if($is_match)
					{
						my $bgcolor = "";
						if($sub_line eq $i)
						{
							$bgcolor = "selected";
						}
					
			
				my $sub_action = $temp_file[1];
				my $sub_active = $temp_file[2];
				my $has_exception = 0;

				#判断exception配置文件中该规则是否修改过，若有，则读取#
				if($exception_hash{'action'.$sid})
				{
					if(($sub_action eq $exception_hash{"action".$sid})&&($sub_action eq $exception_hash{"active".$sid}))
					{
						&delete_excption($sid);
						&save_excption();
					}else{
						$sub_action = $exception_hash{"action".$sid};
						$sub_active = $exception_hash{"active".$sid};
					}
				}
				if($sub_action eq "drop")
				{
					$sub_action_img = "/images/action_drop.png";
				}elsif($sub_action eq "alert")
				{
					$sub_action_img = "/images/action_alert.png";
				}
	
				if($sub_active eq "on")
				{
					$sub_active_img = "/images/on.png";
				}elsif($sub_active eq "off")
				{
					$sub_active_img = "/images/off.png";
				}

			if($is_cur_rule eq "on")
			{
				my $new_name = $ruleset_name;
				$new_name =~ s/emerging-//g;
				if($temp_file[0] eq $new_name)
				{
				printf <<EOF
			<tr class="$bgcolor">
				<td width="150px" class="$bgcolor note" >$rule_detail_hash{$temp_file[0]}</td>
				<td width="100px" class="$bgcolor" >$temp_sid</td>
				<td class="$bgcolor" >$rule_dis</td>
				<td class="$bgcolor" width="100px" style="text-align:center;" >$pro</td>
				<td class="$bgcolor" width="100px" style="text-align:center;">$prio</td>
				<td class="$bgcolor" width="103px">
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_action_img" title="$sub_action_title"/>
					<input type="hidden" name="SUB_SEAR_ACTION" value="$sub_action">
					<input type="hidden" name="SUB_SEAR_ACTIVE" value="$sub_active">
					<input  type="hidden" name="SEARCH_TEXT" value="$search_text">
					<input type="hidden" name="LINE" value="$i">
					<input type="hidden" name="SID" value="$sid">
					<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
					<input type="hidden" name="SENSIVE" value="$sensive">
					<input type="hidden" name="NAME" value="$ruleset_name">
				</form>
				
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_active_img" title="$sub_active_title"/>
					<input type="hidden" name="SUB_SEAR_ACTION" value="$sub_active">
					<input type="hidden" name="SUB_SEAR_CUR_ACTION" value="$sub_action">
					<input type="hidden" name="LINE" value="$i">
					<input  type="hidden" name="SEARCH_TEXT" value="$search_text">
					<input type="hidden" name="SID" value="$sid">
					<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
					<input type="hidden" name="SENSIVE" value="$sensive">
					<input type="hidden" name="NAME" value="$ruleset_name">
				</form></td></tr>
EOF
;
			$i++;
				}
			}else{
				printf <<EOF
			<tr class="$bgcolor">
				<td width="150px" class="$bgcolor note" >$rule_detail_hash{$temp_file[0]}</td>
				<td width="100px" class="$bgcolor" >$temp_sid</td>
				<td class="$bgcolor" >$rule_dis</td>
				<td class="$bgcolor" width="100px" style="text-align:center;" >$pro</td>
				<td class="$bgcolor" width="100px" style="text-align:center;">$prio</td>
				<td class="$bgcolor" width="103px">
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_action_img" title="$sub_action_title"/>
					<input type="hidden" name="SUB_SEAR_ACTION" value="$sub_action">
					<input type="hidden" name="SUB_SEAR_ACTIVE" value="$sub_active">
					<input  type="hidden" name="SEARCH_TEXT" value="$search_text">
					<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
					<input type="hidden" name="SENSIVE" value="$sensive">
					<input type="hidden" name="LINE" value="$i">
					<input type="hidden" name="SID" value="$sid">
				</form>
				
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_active_img" title="$sub_active_title"/>
					<input type="hidden" name="SUB_SEAR_ACTION" value="$sub_active">
					<input type="hidden" name="SUB_SEAR_CUR_ACTION" value="$sub_action">
					<input type="hidden" name="LINE" value="$i">
					<input  type="hidden" name="SEARCH_TEXT" value="$search_text">
					<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
					<input type="hidden" name="SENSIVE" value="$sensive">
					<input type="hidden" name="SID" value="$sid">
				</form></td></tr>
EOF
;
			$i++;
			}
			}
		
		}
	            
				else{
				    #classtype 不存在的规则
				    if($line=~/msg:"([^:]+)".*sid:(\d+)/)
					{
					my @temp = split(/\s/,$line);
					$pro = $temp[1];
					$rule_dis = $1;
					$sid = $2;
					my $temp_sid = "";
					$prio = "<span class='orange'><b>中</b></span>";
					$temp_sid = $sid;
					#搜索匹配关键字
					if($sensive ne "on")#匹配大小写
					{
						if($rule_dis =~ /($search_text)/i)
						{
							my $temp = $1;
							$rule_dis =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($sid =~ /($search_text)/i)
						{
							my $temp = $1;
							$temp_sid =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($pro =~ /($search_text)/i)
						{
							my $temp = $1;
							$pro =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($prio =~ /($search_text)/i)
						{
							my $temp = $1;
							$pro =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
					}else{#匹配不区分大小写
						if($rule_dis =~ /($search_text)/)
						{
							my $temp = $1;
							$rule_dis =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($sid =~ /($search_text)/)
						{
							my $temp = $1;
							$temp_sid =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($pro =~ /($search_text)/)
						{
							my $temp = $1;
							$pro =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
						if($prio =~ /($search_text)/)
						{
							my $temp = $1;
							$pro =~ s/$temp/<b class='note' style='background-color:#fdfab0;'>$temp<\/b>/g;
							$is_match = 1;
						}
					}
					if($is_match)
					{
						my $bgcolor = "";
						if($sub_line eq $i)
						{
							$bgcolor = "selected";
						}
					
			
				my $sub_action = $temp_file[1];
				my $sub_active = $temp_file[2];
				my $has_exception = 0;

				#判断exception配置文件中该规则是否修改过，若有，则读取#
				if($exception_hash{'action'.$sid})
				{
					if(($sub_action eq $exception_hash{"action".$sid})&&($sub_action eq $exception_hash{"active".$sid}))
					{
						&delete_excption($sid);
						&save_excption();
					}else{
						$sub_action = $exception_hash{"action".$sid};
						$sub_active = $exception_hash{"active".$sid};
					}
				}
				if($sub_action eq "drop")
				{
					$sub_action_img = "/images/action_drop.png";
				}elsif($sub_action eq "alert")
				{
					$sub_action_img = "/images/action_alert.png";
				}
	
				if($sub_active eq "on")
				{
					$sub_active_img = "/images/on.png";
				}elsif($sub_active eq "off")
				{
					$sub_active_img = "/images/off.png";
				}

			if($is_cur_rule eq "on")
			{
				my $new_name = $ruleset_name;
				$new_name =~ s/emerging-//g;
				if($temp_file[0] eq $new_name)
				{
				printf <<EOF
			<tr class="$bgcolor">
				<td width="150px" class="$bgcolor note" >$rule_detail_hash{$temp_file[0]}</td>
				<td width="100px" class="$bgcolor" >$temp_sid</td>
				<td class="$bgcolor" >$rule_dis</td>
				<td class="$bgcolor" width="100px" style="text-align:center;" >$pro</td>
				<td class="$bgcolor" width="100px" style="text-align:center;">$prio</td>
				<td class="$bgcolor" width="103px">
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_action_img" title="$sub_action_title"/>
					<input type="hidden" name="SUB_SEAR_ACTION" value="$sub_action">
					<input type="hidden" name="SUB_SEAR_ACTIVE" value="$sub_active">
					<input  type="hidden" name="SEARCH_TEXT" value="$search_text">
					<input type="hidden" name="LINE" value="$i">
					<input type="hidden" name="SID" value="$sid">
					<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
					<input type="hidden" name="SENSIVE" value="$sensive">
					<input type="hidden" name="NAME" value="$ruleset_name">
				</form>
				
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_active_img" title="$sub_active_title"/>
					<input type="hidden" name="SUB_SEAR_ACTION" value="$sub_active">
					<input type="hidden" name="SUB_SEAR_CUR_ACTION" value="$sub_action">
					<input type="hidden" name="LINE" value="$i">
					<input  type="hidden" name="SEARCH_TEXT" value="$search_text">
					<input type="hidden" name="SID" value="$sid">
					<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
					<input type="hidden" name="SENSIVE" value="$sensive">
					<input type="hidden" name="NAME" value="$ruleset_name">
				</form></td></tr>
EOF
;
			$i++;
				}
			}else{
				printf <<EOF
			<tr class="$bgcolor">
				<td width="150px" class="$bgcolor note" >$rule_detail_hash{$temp_file[0]}</td>
				<td width="100px" class="$bgcolor" >$temp_sid</td>
				<td class="$bgcolor" >$rule_dis</td>
				<td class="$bgcolor" width="100px" style="text-align:center;" >$pro</td>
				<td class="$bgcolor" width="100px" style="text-align:center;">$prio</td>
				<td class="$bgcolor" width="103px">
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_action_img" title="$sub_action_title"/>
					<input type="hidden" name="SUB_SEAR_ACTION" value="$sub_action">
					<input type="hidden" name="SUB_SEAR_ACTIVE" value="$sub_active">
					<input  type="hidden" name="SEARCH_TEXT" value="$search_text">
					<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
					<input type="hidden" name="SENSIVE" value="$sensive">
					<input type="hidden" name="LINE" value="$i">
					<input type="hidden" name="SID" value="$sid">
				</form>
				
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_active_img" title="$sub_active_title"/>
					<input type="hidden" name="SUB_SEAR_ACTION" value="$sub_active">
					<input type="hidden" name="SUB_SEAR_CUR_ACTION" value="$sub_action">
					<input type="hidden" name="LINE" value="$i">
					<input  type="hidden" name="SEARCH_TEXT" value="$search_text">
					<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
					<input type="hidden" name="SENSIVE" value="$sensive">
					<input type="hidden" name="SID" value="$sid">
				</form></td></tr>
EOF
;
			$i++;
			}
			}
		
		}
	            
				}
	}

	
	}
	}
	print "</table>";
	if(!$i)
	{
		print "<table class='search_result'>";
		no_tr(4,"找不到关于 <b class='note'>".$search_text."</b> 的相关内容，请调整关键字重新搜索");
		print "</table>";
	}
	print "</div><table style='margin:0px auto;border:1px solid #999;border:0px 1px;'>
	<tr class='table-footer'><td style='text-align:left;'>";
	if($i)
	{
		print "当前共搜索到关于 <b>‘".$search_text."’</b> 的规则 <b class='note'>".$i."</b>条";
	}
	print "</td></tr></table></div>";
	}
}

sub display_rules(){
	if($is_editing && $first_edit&&!$is_search)
	{
		my $edit_rule_name = $ruleset_name;
		$edit_rule_name =~ s/emerging-//g;
		my $dir = $rules."/".$edit_rule_name;
		my @ruleset_detail= read_config_files($dir);
		my @lines;
		foreach my $line (@ruleset_detail) {
			chomp($line);
			if ($line !~/^#/ && $line) {
				push(@lines,$line);
			}
		}
	printf <<EOF
	<br /><div style="width:96%;margin:0px auto;">
	<table  style="width:100%;" class="ruleslist">
	<tr>
			<td class="boldbase" width="100px" >%s</td>
			<td class="boldbase"><b class="note">[ $ruleset_name_ch ]</b> %s</td>
            <td class="boldbase" width="100px">%s</td>
			<td class="boldbase" width="100px">%s</td>
            <td class="boldbase" width="120px">%s</td>
	</tr>
	</table>
EOF
,"ID"
,_("规则描述")
,_("协议")
,_("危险级")
,_("活动/动作")
;
	my $pro = "";#协议
	my $rule_dis ="";#描述
	my $sid = "";#sid
	my $prio = "";#
	
	
	

	print '<div id="sub_rule_div" style="height:auto;margin:0px auto;overflow-y:scroll;"><table id="sub_rule" style="width:100%;" class="ruleslist">';

	if(@lines%$per_page == 0)
	{
		$count = @lines/$per_page;
	}else{
		$count = int(@lines/$per_page)+1;
	}
	
	
	for(my $i = ($cur_page-1)*$per_page;$i<$cur_page*$per_page;$i++)
	{
		if($lines[$i]=~/msg:"([^:]+)".*classtype:(.*);.*sid:(\d+)/)
		{
			my @temp = split(/\s/,$lines[$i]);
			$pro = $temp[1];
			$rule_dis = $1;
			$sid = $3;
			@splited = split(/;/,$2);
			$prio= $pri_set{$splited[0]};
			if(!$prio)
			{
				$prio = "<span class='orange'><b>中</b></span>";
			}
			
			my $sub_action = $ruleset_action;
			my $sub_active = $ruleset_active;
			my $has_exception = 0;

			#判断exception配置文件中该规则是否修改过，若有，则读取#
			if($exception_hash{'action'.$sid})
			{
				if(($sub_action eq $exception_hash{"action".$sid})&&($sub_active eq $exception_hash{"active".$sid}))
				{
					&delete_excption($sid);
					&save_excption();
				}else{
						$sub_action = $exception_hash{"action".$sid};
						$sub_active = $exception_hash{"active".$sid};
					}
			}
			if($sub_action eq "drop")
			{
				$sub_action_img = "/images/action_drop.png";
			}elsif($sub_action eq "alert")
			{
				$sub_action_img = "/images/action_alert.png";
			}
	
			if($sub_active eq "on")
			{
				$sub_active_img = "/images/on.png";
			}elsif($sub_active eq "off")
			{
				$sub_active_img = "/images/off.png";
			}
			my $bgcolor = "";
			if($sub_line eq $i)
			{
				$bgcolor = "selected";
			}
			
			#######################################################
			printf <<EOF
			<tr class="$bgcolor">
				<td width="100px" class="$bgcolor" >$sid</td>
				<td class="$bgcolor" >$rule_dis</td>
				<td class="$bgcolor" width="100px" style="text-align:center;" >$pro</td>
				<td class="$bgcolor" width="100px" style="text-align:center;">$prio</td>
				<td class="$bgcolor" width="103px">
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_action_img" title="$sub_action_title"/>
					<input type="hidden" name="SUB_ACTION" value="$sub_action">
					<input type="hidden" name="SUB_ACTIVE" value="$sub_active">
					<input type="hidden" name="CUR_NAME" value="$ruleset_name">
					<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
					<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
					<input type="hidden" name="CUR_PAGE" value="$cur_page">
					<input type="hidden" name="COUNT" value="$count">
					<input type="hidden" name="SID" value="$sid">
					<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
					<input type="hidden" name="LINE" value="$i">
					<input type="hidden" name="FIRST_EDIT" value="$first_edit">
				</form>
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_active_img" title="$sub_action_title"/>
					<input type="hidden" name="SUB_ACTION" value="$sub_active">
					<input type="hidden" name="SUB_CUR_ACTION" value="$sub_action">
					<input type="hidden" name="CUR_NAME" value="$ruleset_name">
					<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
					<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
					<input type="hidden" name="CUR_PAGE" value="$cur_page">
					<input type="hidden" name="COUNT" value="$count">
					<input type="hidden" name="SID" value="$sid">
					<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
					<input type="hidden" name="LINE" value="$i">
					<input type="hidden" name="FIRST_EDIT" value="$first_edit">
				</form></td></tr>
EOF
;

		}
	    else {
		   if($lines[$i]=~/msg:"([^:]+)".*sid:(\d+)/)
		   {
			my @temp = split(/\s/,$lines[$i]);
			$pro = $temp[1];
			$rule_dis = $1;
			$sid = $2;
			$prio = "<span class='orange'><b>中</b></span>";
			my $sub_action = $ruleset_action;
			my $sub_active = $ruleset_active;
			my $has_exception = 0;

			#判断exception配置文件中该规则是否修改过，若有，则读取#
			if($exception_hash{'action'.$sid})
			{
				if(($sub_action eq $exception_hash{"action".$sid})&&($sub_active eq $exception_hash{"active".$sid}))
				{
					&delete_excption($sid);
					&save_excption();
				}else{
						$sub_action = $exception_hash{"action".$sid};
						$sub_active = $exception_hash{"active".$sid};
					}
			}
			if($sub_action eq "drop")
			{
				$sub_action_img = "/images/action_drop.png";
			}elsif($sub_action eq "alert")
			{
				$sub_action_img = "/images/action_alert.png";
			}
	
			if($sub_active eq "on")
			{
				$sub_active_img = "/images/on.png";
			}elsif($sub_active eq "off")
			{
				$sub_active_img = "/images/off.png";
			}
			my $bgcolor = "";
			if($sub_line eq $i)
			{
				$bgcolor = "selected";
			}
			
			#######################################################
			printf <<EOF
			<tr class="$bgcolor">
				<td width="100px" class="$bgcolor" >$sid</td>
				<td class="$bgcolor" >$rule_dis</td>
				<td class="$bgcolor" width="100px" style="text-align:center;" >$pro</td>
				<td class="$bgcolor" width="100px" style="text-align:center;">$prio</td>
				<td class="$bgcolor" width="103px">
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_action_img" title="$sub_action_title"/>
					<input type="hidden" name="SUB_ACTION" value="$sub_action">
					<input type="hidden" name="SUB_ACTIVE" value="$sub_active">
					<input type="hidden" name="CUR_NAME" value="$ruleset_name">
					<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
					<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
					<input type="hidden" name="CUR_PAGE" value="$cur_page">
					<input type="hidden" name="COUNT" value="$count">
					<input type="hidden" name="SID" value="$sid">
					<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
					<input type="hidden" name="LINE" value="$i">
					<input type="hidden" name="FIRST_EDIT" value="$first_edit">
				</form>
				<form method="post" action="$ENV{'SCRIPT_NAME'}" style="float:left;margin-left: 5px;">
					<input  type='image' name="submit" src="$sub_active_img" title="$sub_action_title"/>
					<input type="hidden" name="SUB_ACTION" value="$sub_active">
					<input type="hidden" name="SUB_CUR_ACTION" value="$sub_action">
					<input type="hidden" name="CUR_NAME" value="$ruleset_name">
					<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
					<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
					<input type="hidden" name="CUR_PAGE" value="$cur_page">
					<input type="hidden" name="COUNT" value="$count">
					<input type="hidden" name="SID" value="$sid">
					<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
					<input type="hidden" name="LINE" value="$i">
					<input type="hidden" name="FIRST_EDIT" value="$first_edit">
				</form></td></tr>
EOF
;

		}
		}
	}
	print "</table></div>";
	
	my $first_disabled = "";
	my $end_disabled = "";
	if($cur_page eq 1)
	{
		$first_page = "/images/first-page-off.png";
		$last_page = "/images/last-page-off.png";
		$first_disabled = "onsubmit='return false'";
	}
	if($cur_page eq $count)
	{
		$next_page = "/images/next-page-off.png";
		$end_page = "/images/end-page-off.png";
		$end_disabled = "onsubmit='return false'";
	}
	printf <<EOF
	<table style='width:100%;margin:0px auto;border:1px solid #999;border:0px 1px;'>
	<tr class='table-footer'>
	<td>共$count页&nbsp;&nbsp;&nbsp;
	<form method="post" action="$ENV{'SCRIPT_NAME'}" class="inline" $first_disabled>
	<input type='image' src='$first_page' title='首页' style="pading:0px 5px;" />
	<input type="hidden" name="PAGE" value="FIRST">
	<input type="hidden" name="CUR_NAME" value="$ruleset_name">
	<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
	<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
	<input type="hidden" name="CUR_PAGE" value="$cur_page">
	<input type="hidden" name="COUNT" value="$count">
	<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
	<input type="hidden" name="FIRST_EDIT" value="$first_edit">
	<input type="hidden" name="RELOAD" value="$reload">
	<input type="hidden" name="RESTART" value="$restart">
	</form>
	&nbsp;&nbsp;&nbsp;
	<form method="post" action="$ENV{'SCRIPT_NAME'}" class="inline" $first_disabled >
	<input type='image'  src='$last_page' title='上一页' style="pading:0px 5px;" />
	<input type="hidden" name="PAGE" value="LAST">
	<input type="hidden" name="CUR_NAME" value="$ruleset_name">
	<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
	<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
	<input type="hidden" name="CUR_PAGE" value="$cur_page">
	<input type="hidden" name="COUNT" value="$count">
	<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
	<input type="hidden" name="FIRST_EDIT" value="$first_edit">
	<input type="hidden" name="RELOAD" value="$reload">
	<input type="hidden" name="RESTART" value="$restart">
	</form>
	&nbsp;&nbsp;&nbsp;
	<form method="post" action="$ENV{'SCRIPT_NAME'}" class="inline" $end_disabled >
	<input type='image'  src='$next_page' title='下一页' style="pading:0px 5px;" />
	<input type="hidden" name="PAGE" value="NEXT">
	<input type="hidden" name="CUR_NAME" value="$ruleset_name">
	<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
	<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
	<input type="hidden" name="CUR_PAGE" value="$cur_page">
	<input type="hidden" name="COUNT" value="$count">
	<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
	<input type="hidden" name="FIRST_EDIT" value="$first_edit">
	<input type="hidden" name="RELOAD" value="$reload">
	<input type="hidden" name="RESTART" value="$restart">
	</form>
	&nbsp;&nbsp;&nbsp;
	<form method="post" action="$ENV{'SCRIPT_NAME'}" class="inline" $end_disabled >
	<input type='image' src='$end_page' title='末页' style="pading:0px 10px;" />
	<input type="hidden" name="PAGE" value="END">
	<input type="hidden" name="CUR_NAME" value="$ruleset_name">
	<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
	<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
	<input type="hidden" name="CUR_PAGE" value="$cur_page">
	<input type="hidden" name="COUNT" value="$count">
	<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
	<input type="hidden" name="FIRST_EDIT" value="$first_edit">
	<input type="hidden" name="RELOAD" value="$reload">
	<input type="hidden" name="RESTART" value="$restart">
	</form>
	&nbsp;&nbsp;&nbsp;
	第$cur_page页</td>
	</tr></table>
EOF
;
}
}

sub read_exception()
{
	my @conf = read_config_files($rule_exception);
	foreach my $line(@conf)
	{
		my @temp = split(",",$line);
		$exception_hash{'action'.$temp[0]} = $temp[1];
		$exception_hash{'active'.$temp[0]} = $temp[2];
	}
}
sub myapplybox($) {
    my $text = shift;

    printf <<EOF
<div id="pop-apply-div">
<span><img src="/images/pop_apply.png" /> $text</span>
<span id="cancel">
<form method="post" ACTION="$ENV{'SCRIPT_NAME'}" class="inline">
	<input class="net_button" type="submit" name="save" value="%s">
	<input type="hidden" name="ACTION" value="apply">
	<input type="hidden" name="CUR_NAME" value="$ruleset_name">
	<input type="hidden" name="CUR_PAGE" value="$cur_page">
	<input type="hidden" name="COUNT" value="$count">
	<input type="hidden" name="RULE_SET_CH" value="$ruleset_name_ch">
	<input type="hidden" name="FIRST_EDIT" value="$first_edit">
	<input type="hidden" name="SEARCH_TEXT" value="$search_text">
	<input type="hidden" name="CUR_ACTION" value="$ruleset_action">
	<input type="hidden" name="CUR_ACTIVE" value="$ruleset_active">
	<input type="hidden" name="SUB_LINE" value="$sub_line">
	<input type="hidden" name="IS_CUR_RULE" value="$is_cur_rule">
	<input type="hidden" name="SENSIVE" value="$sensive">
</form>
</span>
</div>
EOF
, _('Apply')
;
}

sub showapplybox() {
    if (-e $needreload) {
		myapplybox(_("配置已经更改，需要应用才能使更改生效"));
	}
	if($restart)
	{
    service_notifications(
        ['snort'], 
        {
            'type' => $restart == 1 ? "commit" : "observe",
            'interval' => 500, 
            'startMessage' => _("入侵防御规则配置正在应用，请等待"),
            'endMessage' => _("入侵防御规则配置应用成功"),
        }
    );
	}
}

sub check_policy()
{
	if(!(-e $rule_conf))
	{
		opendir(DIR,$rules);
		my @dir=readdir(DIR);
		closedir(DIR);
		
		open(FILE,">$rule_conf");
		foreach my $line(@dir)
		{
			if($line =~ /\.rules/)
			{
				print FILE "auto/".$line.",alert,on"."\n";
			}
		}
		close(FILE);
	}
}


&showhttpheaders();
&getcgihash(\%par);
&openpage(_('规则'), 1, "<script language='javascript' src='/include/rules.js'></script>");
&check_policy();
&read_dis();
&read_rule_conf();
&read_exception();
&save();
if ($reload) {
    system("touch $needreload");
}
&showapplybox();
&display_rulesset();
&display_rules();
&display_search();
&closepage();
