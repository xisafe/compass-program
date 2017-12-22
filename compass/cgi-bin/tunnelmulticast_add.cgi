#!/usr/bin/perl
#DATE:2013-7-15
#author:殷其雷

require '/var/efw/header.pl';

my $config_dir = '/var/efw/tunnelmulticast/';
my $config = '/var/efw/tunnelmulticast/config';
my $greconfig = '/var/efw/vpn/greconfig';
my $needreload = '/var/efw/tunnelmulticast/needreload';
my $restarttunnelmulticast = 'sudo /usr/local/bin/restarttunnelmulticast';
my @gres;
my @currents;
my $errormessage='';
my $warnmessage='';
my $notemessage='';
&showhttpheaders();
&getcgihash(\%par);
&make_file();
&read_conf();
&save();
&read_conf();
my $extraheader = "";
&openpage(_('组播条目设置'), 1, $extraheader);
&openbigbox($errormessage, $warnmessage, $notemessage);
if (-e $needreload) {
    $warnmessage = "隧道组播条目设置已改变，请点击应用按钮以重启组播路由服务！";
	applybox($warnmessage);
}
&display_add();
&display_html();
&closebigbox();
&closepage();
&check_form();

sub save(){
    if($par{'ACTION'} eq  'apply')
	{
	    `$restarttunnelmulticast`;
		`rm $needreload`;
	}
    if($par{'ACTION'} eq  'add_save')
	{
	    my $tmp = $par{'tunnel_name'};
		my @splited = split(/\+/,$tmp);
		my $tunnel_name = $splited[1];
		my $tunnel_seq = $splited[0];
		my $tunnel_weight = $par{'tunnel_weight'};
		my $tunnel_ip = $par{'tunnel_ip'};
		my $tunnel_listen = $par{'tunnel_listen'};
		my $tunnel_enable = $par{'tunnel_enable'};
		
		my $line = $tunnel_enable.','.$tunnel_name.','.$tunnel_seq.','.$tunnel_weight.','.$tunnel_ip.','.$tunnel_listen;
		push(@currents,$line);
		save_config_file(\@currents,$config);
		$notemessage = '新条目添加成功！';
		`touch $needreload`;
	}
	
	if($par{'ACTION'} eq 'edit_save')
	{
		my $tunnel_name = $par{'old_name'};
		my $tunnel_seq = $par{'old_seq'};
		my $tunnel_weight = $par{'tunnel_weight'};
		my $tunnel_ip = $par{'tunnel_ip'};
		my $tunnel_listen = $par{'tunnel_listen'};
		my $tunnel_enable = $par{'tunnel_enable'};
		my @new_currents;
        foreach my $one (@currents)
		{
		   my @split = split(/,/,$one);
		   if($split[1] ne $tunnel_name )
		   {
		      push(@new_currents,$one);
		   } else {
		      my $line = $tunnel_enable.','.$tunnel_name.','.$tunnel_seq.','.$tunnel_weight.','.$tunnel_ip.','.$tunnel_listen;
			  push(@new_currents,$line);
		   }
		}
	    save_config_file(\@new_currents,$config);
		$notemessage = '条目编辑成功！';
		`touch $needreload`;
	}
	
	if($par{'ACTION'} eq 'enable or disable')
	{
	    my $name = $par{'name'};
		my $status = $par{'status'};
		my @new_currents;
		foreach my $one (@currents)
		{
		   my @split = split(/,/,$one);
		   {
		      if($split[1] ne $name)
			  {
			     push(@new_currents,$one);
			  } else {
			     my $new_one;
			     if($status eq 'on')
				 {
				    $new_one = 'off';
					my $count = 0;
					foreach my $one_split(@split)
					{
					   if($count ne 0)
					   {
					      $new_one .= ',';
					      $new_one .= $one_split;
					   }
					   $count++;
					}
					$notemessage = '条目禁用成功！';
				 } else {
				    $new_one = 'on';
					my $count = 0;
					foreach my $one_split(@split)
					{
					   if($count ne 0)
					   {
					      $new_one .= ',';
					      $new_one .= $one_split;
					   }
					   $count++;
					}
					$notemessage = '条目启用成功！';
				 }
				 push(@new_currents,$new_one);
			  }
		   }
		}
		save_config_file(\@new_currents,$config);
		`touch $needreload`;
	}
	
	if($par{'ACTION'} eq 'remove')
	{
	    my $name = $par{'name'};
		my @new_currents;
		foreach my $one (@currents)
		{
		   my @split = split(/,/,$one);
		   {
		      if($split[1] ne $name)
			  {
			     push(@new_currents,$one);
			  }
		   }
		}
		save_config_file(\@new_currents,$config);
		$notemessage = '条目删除成功！';
		`touch $needreload`;
	}
}

sub read_conf(){
    my @tmp_currents;
    open(FILE,$config);
	foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@tmp_currents, $line);
    }
	close (FILE);
	@currents = @tmp_currents;
}

sub make_file(){
    if(!-e $config_dir)
	{
	    `mkdir $config_dir`;
	}
	if(!-e $config)
    {
	    `touch $config`;
	}
}

sub check_form(){
  printf <<EOF
  <script>
  var object = {
       'form_name':'USER_FORM',
       'option'   :{
                    'tunnel_weight':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'!/^\$/',
							   'ass_check':function(eve){
							                               var msg = '';
							                               var str = eve._getCURElementsByName("tunnel_weight","input","USER_FORM")[0].value;
                                                           var reg = /^([0-9])+\$/;
														   if(reg.test(str))
														   {
														      if(str==0)
															  {
															     msg = "权重值应取大于0的正整数！";
															  }
														   } else {
														      msg = "权重值应取大于0的正整数！";
														   }
														   return msg;
							                            }
                             },
                    'tunnel_ip':{
                               'type':'text',
                               'required':'1',
                               'check':'other|',
                               'other_reg':'!/^\$/',
							   'ass_check':function(eve){
							                               var msg = '';
							                               var str = eve._getCURElementsByName("tunnel_ip","input","USER_FORM")[0].value;
														   var reg1 = /^([0-9])+\$/;
														   var reg2 = /^([1-9]|[1-9]\\d|1\\d{2}|2[0-1]\\d|22[0-3])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3}\$/;
														   var splited = new Array();
														   splited = str.split('/');
														   if(splited.length != 2)
														   {
														      msg = "接口地址应该为IP地址/子网掩码格式！";
														   } else {
														      if(reg2.test(splited[0]))
															  {
															     if(reg1.test(splited[1]))
																 {
																    if(splited[1]<0||splited[1]>32)
																	{
																	  msg = "接口地址应该为IP地址/子网掩码格式！";
																	}
																 } else {
																    msg = "接口地址应该为IP地址/子网掩码格式！";
																 }
															  } else {
															     msg = "接口地址应该为IP地址/子网掩码格式！";
															  }
														   }
														   return msg;
														   
							                            }
                             },
                    'tunnel_name':{
                               'type':'select-one',
                               'required':'1',
                             },
                 }
         }
  var check = new  ChinArk_forms();
  check._main(object);
  //check._get_form_obj_table("USER_FORM");
  </script>
EOF
;
}

sub display_add(){
    my $weight;
	my $ip;
	my $listen = "checked";
	my $enable = "checked";
    if($par{'ACTION'} eq 'edit')
	{
	   openeditorbox(_('编辑组播服务条目'), "","showeditor", "createrule", @errormessages);
	   foreach my $one (@currents)
	   {
	      my @split = split(/,/,$one);
		  if($split[1] eq $par{'name'})
		  {
		     $weight = $split[3];
			 $ip = $split[4];
			 if($split[5] eq 'on')
			 {
			    $listen = 'checked';
			 } else {
			    $listen = '';
			 }
			 
			 if($split[0] eq 'on')
			 {
			    $enable = 'checked';
			 } else {
			    $enable = '';
			 }
		  }
	   }
	} else {
       openeditorbox(_('添加组播服务条目'), "","", "createrule", @errormessages);
	}
	printf <<EOF
	</form>
	<form name="USER_FORM" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
	<table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
	  <tbody>
	   <tr class="odd" >
	     <td class="add-div-type" >隧道连接名</td>
		 <td>
EOF
;
    if($par{'ACTION'} eq 'edit')
	{
	  printf <<EOF
	        <input type="text" disabled="true" name='old_name 'value="$par{'name'}" />
            <input type="hidden" name='old_seq' value="$par{'seq'}" /> 			
EOF
;
	} else {
	  printf <<EOF
		    <select name='tunnel_name' onchange="show_second_detail()">
			            <option value=''>不选择</option>
EOF
;
    &print_names();
    printf <<EOF
					  </select>
EOF
;
    }
    printf <<EOF	
		 </td>
	   </tr>
	   <tr class="env">
	     <td class="add-div-type" style="width:20%;">权重*</td>
		 <td>
		    <input type="text" name='tunnel_weight' value='$weight' />
		 </td>
	   </tr>
	   <tr class="odd">
	     <td class="add-div-type" >隧道接口地址*</td>
		 <td>
		    <input type="text" name='tunnel_ip' value='$ip' />
		 </td>
	   </tr>
	   <tr class="env">
	     <td class="add-div-type" >自动侦听</td>
		 <td>
		    <input type="checkbox" name='tunnel_listen' $listen />
		 </td>
	   </tr>
	   <tr class="odd">
	     <td class="add-div-type" >是否启用</td>
		 <td>
		    <input type="checkbox" name='tunnel_enable' $enable />
		 </td>
	   </tr>
	  </tbody>
	 </table>
EOF
;
     if($par{'ACTION'} eq 'edit')
	 {
		my $old_name = $par{'name'};
		printf <<EOF
		<input type="hidden" id="ACTION" name="ACTION" value="edit_save" />
		<input type="hidden" id="old_name" name="old_name" value="$old_name" />
EOF
;
	 } else {
	    print '<input type="hidden" id="ACTION" name="ACTION" value="add_save" />';
	 }
EOF
;
	 closeeditorbox("保存", "撤销", "routebutton", "createrule", $ENV{'SCRIPT_NAME'});
}

sub display_html(){
    printf <<EOF
	<table class="ruleslist" cellpadding="0" cellspacing="0" width="100%">
	<tr>
	  <td class="boldbase">隧道连接名
	  </td>
	  <td class="boldbase">权重
	  </td>
	  <td class="boldbase">接口地址
	  </td>
	  <td class="boldbase">自动侦听
	  </td>
	  <td class="boldbase">活动/动作
	  </td>
	</tr>
EOF
;
    my $count;
    foreach my $one (@currents)
	{
	   $count++;
	   my $listen;
	   my $src;
	   my $title;
	   my $alt;
	   my @splited = split(/,/,$one);
	   if($splited[5] eq 'on')
	   {
	      $listen = '是';
	   } else {
	      $listen = '否';
	   }
	   
	   if($splited[0] eq 'on')
	   {
		  $src = '/images/on.png';
		  $title = '点击使此条目禁用';
		  $alt = '点击使此条目禁用';
	   } else {
		  $src = '/images/off.png';
		  $title = '点击使此条目启用';
		  $alt = '点击使此条目启用';
	   }
	   printf <<EOF
	   <tr>
	   <td>$splited[1]
	   </td>
	   <td>$splited[3]
	   </td>
	   <td>$splited[4]
	   </td>
	   <td>$listen
	   </td>
	   <td>
	      <form method="post" action='$ENV{'SCRIPT_NAME'}'>
		    <input type='hidden' name='name' value='$splited[1]' />
			<input type='hidden' name='status' value='$splited[0]' />
			<input type='hidden' name='ACTION' value='enable or disable' />
			<input class="imagebutton" type="image" src="$src" alt="$alt" title="$title" />
		  </form>
		  <form method="post" action='$ENV{'SCRIPT_NAME'}'>
		    <input type='hidden' name='name' value='$splited[1]' />
			<input type='hidden' name='seq' value='$splited[2]' />
		    <input type='hidden' name='ACTION' value='edit' />
			<input class="imagebutton" type="image" src='/images/edit.png' alt='编辑' title='编辑' />
		  </form>
		  <form method="post" action='$ENV{'SCRIPT_NAME'}'>
		    <input type='hidden' name='name' value='$splited[1]' />
		    <input type='hidden' name='ACTION' value='remove' />
			<input class="imagebutton" type="image" src='/images/delete.png' alt='移除' title='移除' />
		  </form>
	   </td>
	   </tr>
EOF
;
	}
	if($count)
	{
	  printf <<EOF
	  </table>
	  <table cellpadding="0" cellspacing="0" class="list-legend">
  <tbody><tr>
    <td class="boldbase">
      <b>标签</b>
    <img src="/images/on.png" alt="启用（点击按钮使禁止）">
    启用（点击按钮使禁止）
    <img src="/images/off.png" alt="禁止（点击按钮启用）">
    禁止（点击按钮启用）
    <img src="/images/edit.png" alt="编辑">
    编辑
    <img src="/images/delete.png" alt="移除">
    移除</td>
  </tr>
</tbody></table>
EOF
;
	} else {
	   no_tr(5,_('Current no content'));
	}
}

sub print_names(){
    open(FILE,$greconfig);
	@gres = <FILE>;
	close(FILE);
	foreach my $one (@gres)
	{
	   if($one=~/^on/)
	   {
	      my @splited = split(/,/,$one);
		  my $exist;
		  foreach my $one (@currents)
		  {
		     my @one_split = split(/,/,$one);
			 if($one_split[1] eq $splited[2])
			 {
			    $exist=1;
			 }
		  }
		  if(!$exist)
		  {
		     print "<option value='$splited[1]+$splited[2]'>$splited[2]</option>";
	      }
	   }
	}
}
