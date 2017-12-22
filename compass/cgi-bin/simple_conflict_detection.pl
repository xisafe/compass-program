#!/usr/bin/perl

#===============================================================================
#
# DESCRIPTION: 冲突提示简易版，只判断冲突和重复
#
# AUTHOR:  肖骞宇 (Squall), wsxqyws@gmail.com
# CREATED: 2013-4-17
#===============================================================================

my $conflict_value = "/etc/conflict_detection/conflict_value";
my $global_script_name = "";

#流出防火墙
my %outgoing = (
    "path" => "/var/efw/outgoing/config",
    "relation_sub"  => "outgoing_relation",
    "config_line_sub" => "outgoing_config_line"
);
#流入防火墙
my %incoming = (
    "path" => "/var/efw/incoming/config",
    "relation_sub"  => "incoming_relation",
    "config_line_sub" => "incoming_config_line"
);
#区域防火墙
my %zonefw = (
    "path" => "/var/efw/zonefw/config",
    "relation_sub"  => "zonefw_relation",
    "config_line_sub" => "zonefw_config_line"
);
#系统访问
my %xtaccess = (
    "path" => "/var/efw/xtaccess/config",
    "relation_sub"  => "xtaccess_relation",
    "config_line_sub" => "xtaccess_config_line"
);
#vpn防火墙
my %vpnfw = (
    "path" => "/var/efw/vpnfw/config",
    "relation_sub"  => "vpnfw_relation",
    "config_line_sub" => "vpnfw_config_line"
);
#DNAT
my %dnat = (
    "path" => "/var/efw/dnat/config",
    "relation_sub"  => "dnat_relation",
    "config_line_sub" => "dnat_config_line"
);
#SNAT
my %snat = (
    "path" => "/var/efw/snat/config",
    "relation_sub"  => "snat_relation",
    "config_line_sub" => "snat_config_line"
);
my %module_hash = (
    "/cgi-bin/outgoingfw.cgi" => \%outgoing,
    "/cgi-bin/incoming.cgi"   => \%incoming,
    "/cgi-bin/zonefw.cgi"     => \%zonefw,
    "/cgi-bin/xtaccess.cgi"   => \%xtaccess,
    "/cgi-bin/vpnfw.cgi"      => \%vpnfw,
    "/cgi-bin/dnat.cgi"       => \%dnat,
    "/cgi-bin/snat.cgi"       => \%snat
);

#
# DESCRIPTION: 流出防火墙关系
# @param:      规则A引用
#              规则B引用
# @return:     集合间关系string
#
sub outgoing_relation($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    my @compare_fields = qw "protocol source destination port mac src_dev dst_dev src_port start_day end_day start_hour_min end_hour_min week";
    my $tmp_relation = "";
    
    #记录关系出现的次数
    my %count = (
        "=" => 0,
        ""  => 0,
        "total" => 0
    );
    
    foreach my $field (@compare_fields) {
        $tmp_relation = relation_by_name(\%rule_A,\%rule_B,$field);
        $count{$tmp_relation}++;
        $count{"total"}++;
    }
    
    
    if ($count{"total"} eq $count{"="}) {
        return "=";
    } else {
        return "";
    }
}

#读取一行，返回一个config hash
#
# DESCRIPTION: 流出防火墙使用，通过line得到规则hash
# @param:      一条规则string
# @return:     规则hash
#
sub outgoing_config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    if (! is_valid($line)) {
        return;
    }
    my @temp = split(/,/, $line);
    $config{'enabled'} = $temp[0];
    $config{'protocol'} = $temp[1];
    $config{'source'} = $temp[2];
    $config{'destination'} = $temp[3];
    $config{'port'} = $temp[4];
    $config{'target'} = $temp[5];
    $config{'mac'} = $temp[6];
    $config{'remark'} = $temp[7];
    $config{'log'} = $temp[8];
    $config{'src_dev'} = $temp[9];
    $config{'dst_dev'} = $temp[10];
    $config{'src_port'} = $temp[11];
    $config{'start_day'}= $temp[12];
    $config{'end_day'}= $temp[13];
    $config{'start_hour_min'}= $temp[14];
    $config{'end_hour_min'}= $temp[15];
    $config{'week'}= $temp[16];
    $config{'valid'} = 1;

    return %config;
}
#
# DESCRIPTION: 流入防火墙关系
# @param:      规则A引用
#              规则B引用
# @return:     集合间关系string
#
sub incoming_relation($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    foo("incoming_relaiton\n");
    
    my @compare_fields = qw "protocol src_dev source dst_dev destination port start_day end_day start_hour_min end_hour_min week";
                            
    my $tmp_relation = "";
    
    #记录关系出现的次数
    my %count = (
        "=" => 0,
        ""  => 0,
        "total" => 0
    );
    
    foreach my $field (@compare_fields) {
        $tmp_relation = relation_by_name(\%rule_A,\%rule_B,$field);
        $count{$tmp_relation}++;
        $count{"total"}++;
    }
    
    
    if ($count{"total"} eq $count{"="}) {
        return "=";
    } else {
        return "";
    }
}

#
# DESCRIPTION: 流入防火墙使用，通过line得到规则hash
# @param:      一条规则string
# @return:     规则hash
#
sub incoming_config_line($) {
    my $line = shift;
    my %config;
    foo("incoming_config_line\n");
    $config{'valid'} = 0;
    if (! is_valid($line)) {
        return;
    }
    my @temp = split(/,/, $line);
    $config{'enabled'} = $temp[0];
    $config{'protocol'} = $temp[1];
    $config{'src_dev'} = $temp[2];
    $config{'source'} = $temp[3];
    $config{'dst_dev'} = $temp[4];
    $config{'destination'} = $temp[5];
    $config{'port'} = $temp[6];
    $config{'start_day'}= $temp[10];
    $config{'end_day'}= $temp[11];
    $config{'start_hour_min'}= $temp[12];
    $config{'end_hour_min'}= $temp[13];
    $config{'week'}= $temp[14];
    $config{'target'} = $temp[7];
    $config{'remark'} = $temp[8];
    $config{'log'} = $temp[9];
    $config{'valid'} = 1;

    return %config;
}
#
# DESCRIPTION: 区域防火墙关系
# @param:      规则A引用
#              规则B引用
# @return:     集合间关系string
#
sub zonefw_relation($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    foo("zonefw_relaiton\n");
    
    my @compare_fields = qw "protocol source destination port mac start_day end_day start_hour_min end_hour_min week src_dev dst_dev";
                            
    my $tmp_relation = "";
    
    #记录关系出现的次数
    my %count = (
        "=" => 0,
        ""  => 0,
        "total" => 0
    );
    
    foreach my $field (@compare_fields) {
        $tmp_relation = relation_by_name(\%rule_A,\%rule_B,$field);
        $count{$tmp_relation}++;
        $count{"total"}++;
    }
    
    
    if ($count{"total"} eq $count{"="}) {
        return "=";
    } else {
        return "";
    }
}

#
# DESCRIPTION: 区域防火墙使用，通过line得到规则hash
# @param:      一条规则string
# @return:     规则hash
#
sub zonefw_config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    if ($line !~ /(?:(?:[^,]*),){10}/) {
        return;
    }
    
    my @temp = split(/,/, $line);
    $config{'enabled'} = $temp[0];
    $config{'protocol'} = $temp[1];
    $config{'source'} = $temp[2];
    $config{'destination'} = $temp[3];
    $config{'port'} = $temp[4];
    $config{'target'} = $temp[5];
    $config{'mac'} = $temp[6];
    $config{'start_day'}= $temp[11];
    $config{'end_day'}= $temp[12];
    $config{'start_hour_min'}= $temp[13];
    $config{'end_hour_min'}= $temp[14];
    $config{'week'}= $temp[15];
    $config{'remark'} = $temp[7];
    $config{'log'} = $temp[8];
    $config{'src_dev'} = $temp[9];
    $config{'dst_dev'} = $temp[10];
    $config{'valid'} = 1;

    return %config;
}

#
# DESCRIPTION: 系统访问关系
# @param:      规则A引用
#              规则B引用
# @return:     集合间关系string
#
sub xtaccess_relation($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    foo("xtaccess_relaiton\n");
    
    my @compare_fields = qw "protocol source port destination dst_dev mac start_day end_day start_hour_min end_hour_min week";
                            
    my $tmp_relation = "";
    
    #记录关系出现的次数
    my %count = (
        "=" => 0,
        ""  => 0,
        "total" => 0
    );
    
    foreach my $field (@compare_fields) {
        $tmp_relation = relation_by_name(\%rule_A,\%rule_B,$field);
        $count{$tmp_relation}++;
        $count{"total"}++;
    }
    
    
    if ($count{"total"} eq $count{"="}) {
        return "=";
    } else {
        return "";
    }
}

#
# DESCRIPTION: 系统访问使用，通过line得到规则hash
# @param:      一条规则string
# @return:     规则hash
#
sub xtaccess_config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    if ($line !~ /(?:(?:[^,]*),){4}/) {
        return;
    }
    
    my @temp = split(/,/, $line);
    $config{'protocol'} = $temp[0];
    $config{'source'} = $temp[1];
    $config{'port'} = $temp[2];
    $config{'enabled'} = $temp[3];
    $config{'destination'} = $temp[4];
    $config{'dst_dev'} = $temp[5];
    $config{'log'} = $temp[6];
    $config{'logprefix'} = $temp[7];
    $config{'target'} = $temp[8];
    $config{'mac'} = $temp[9];
    $config{'remark'} = $temp[10];
    $config{'start_day'}= $temp[11];
    $config{'end_day'}= $temp[12];
    $config{'start_hour_min'}= $temp[13];
    $config{'end_hour_min'}= $temp[14];
    $config{'week'}= $temp[15];
    $config{'valid'} = 1;

    return %config;
}

#
# DESCRIPTION: vpn防火墙关系
# @param:      规则A引用
#              规则B引用
# @return:     集合间关系string
#
sub vpnfw_relation($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    foo("xtaccess_relaiton\n");
    
    my @compare_fields = qw "protocol source destination port mac start_day end_day start_hour_min end_hour_min week src_dev dst_dev";
                            
    my $tmp_relation = "";
    
    #记录关系出现的次数
    my %count = (
        "=" => 0,
        ""  => 0,
        "total" => 0
    );
    
    foreach my $field (@compare_fields) {
        $tmp_relation = relation_by_name(\%rule_A,\%rule_B,$field);
        $count{$tmp_relation}++;
        $count{"total"}++;
    }
    
    
    if ($count{"total"} eq $count{"="}) {
        return "=";
    } else {
        return "";
    }
}

#
# DESCRIPTION: 系统访问使用，通过line得到规则hash
# @param:      一条规则string
# @return:     规则hash
#
sub vpnfw_config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    if ($line !~ /(?:(?:[^,]*),){10}/) {
        return;
    }
    
    my @temp = split(/,/, $line);
    $config{'enabled'} = $temp[0];
    $config{'protocol'} = $temp[1];
    $config{'source'} = $temp[2];
    $config{'destination'} = $temp[3];
    $config{'port'} = $temp[4];
    $config{'target'} = $temp[5];
    $config{'mac'} = $temp[6];
    $config{'start_day'}= $temp[11];
    $config{'end_day'}= $temp[12];
    $config{'start_hour_min'}= $temp[13];
    $config{'end_hour_min'}= $temp[14];
    $config{'week'}= $temp[15];
    $config{'remark'} = $temp[7];
    $config{'log'} = $temp[8];
    $config{'src_dev'} = $temp[9];
    $config{'dst_dev'} = $temp[10];
    $config{'valid'} = 1;

    return %config;
}

#
# DESCRIPTION: DNAT关系
# @param:      规则A引用
#              规则B引用
# @return:     集合间关系string
#
sub dnat_relation($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    foo("dnat_relaiton\n");
    
    my @compare_fields = qw "protocol src_dev source dst_dev destination port";

    my $tmp_relation = "";
    
    #记录关系出现的次数
    my %count = (
        "=" => 0,
        ""  => 0,
        "total" => 0
    );
    
    foreach my $field (@compare_fields) {
        $tmp_relation = relation_by_name(\%rule_A,\%rule_B,$field);
        $count{$tmp_relation}++;
        $count{"total"}++;
    }
    
    
    if ($count{"total"} eq $count{"="}) {
        return "=";
    } else {
        return "";
    }
}

#
# DESCRIPTION: dnat使用，通过line得到规则hash
# @param:      一条规则string
# @return:     规则hash
#
sub dnat_config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
    if (not ($line =~ /(?:(?:[^,]*),){10}/ || $line =~ /(?:(?:[^,]*),){7}/)) {
        return;
    }
    
    my @temp = split(/,/, $line);
    $config{'enabled'} = $temp[0];
    $config{'protocol'} = $temp[1];
    $config{'src_dev'} = $temp[2];
    $config{'source'} = $temp[3];
    $config{'dst_dev'} = $temp[4];
    $config{'destination'} = $temp[5];
    $config{'port'} = $temp[6];
    $config{'target_ip'} = $temp[7];
    $config{'target_port'} = $temp[8];
    $config{'nat_target'} = $temp[9];
    $config{'remark'} = $temp[10];
    $config{'log'} = $temp[11];
    $config{'filter_target'} = $temp[12];
    $config{'valid'} = 1;

    return %config;
}

#
# DESCRIPTION: SNAT关系
# @param:      规则A引用
#              规则B引用
# @return:     集合间关系string
#
sub snat_relation($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    foo("snat_relaiton\n");

    my @compare_fields = qw "proto src_ip dst_ip dst_port dst_dev";

    my $tmp_relation = "";
    
    #记录关系出现的次数
    my %count = (
        "=" => 0,
        ""  => 0,
        "total" => 0
    );
    
    foreach my $field (@compare_fields) {
        $tmp_relation = relation_by_name(\%rule_A,\%rule_B,$field);
        $count{$tmp_relation}++;
        $count{"total"}++;
    }
    
    
    if ($count{"total"} eq $count{"="}) {
        return "=";
    } else {
        return "";
    }
}

#
# DESCRIPTION: snat使用，通过line得到规则hash
# @param:      一条规则string
# @return:     规则hash
#
sub snat_config_line($) {
    my $line = shift;
    my %config;
    $config{'valid'} = 0;
#    if (not ($line =~ /(?:(?:[^,]*),){10}/ || $line =~ /(?:(?:[^,]*),){7}/)) {
#        return;
#    }
    
    my @temp = split(/,/, $line);
    $config{'enabled'} = $temp[0];
    $config{'proto'} = $temp[1];
    $config{'src_ip'} = $temp[2];
    $config{'dst_ip'} = $temp[3];
    $config{'dst_port'} = $temp[4];
    $config{'dst_dev'} = $temp[5];
    $config{'target'} = $temp[6];
    $config{'remark'} = $temp[7];
    $config{'log'} = $temp[8];
    $config{'snat_to'} = $temp[9];
    $config{'valid'} = 1;

    return %config;
}

#
# DESCRIPTION: 通过具体字段name比较是否相等
# @param:      规则A引用
#              规则B引用
#              字段name
# @return:     "=" or ""
#
sub relation_by_name($$$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    my $field_name = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    my $ret_str = "";
    
    if (not $rule_A{"$field_name"}) {
        $rule_A{"$field_name"} = "";
    }
    if (not $rule_B{"$field_name"}) {
        $rule_B{"$field_name"} = "";
    }
    
    $ret_str = "=" if $rule_A{"$field_name"} eq $rule_B{"$field_name"};
    
    return $ret_str;
}

#
# DESCRIPTION: 新增函数；当用户试图建立与已有访问控制规则相矛盾的规则时弹出提示窗口。
# @param:      冲突list的引用
#              当前规则编号
# @return:     
#
sub generate_conflict_warning_msg($$) {
    my $conflict_list_ref = shift;
    my $current_seq = shift;
    my @conflict_list = @$conflict_list_ref;

    my $msg = "";
    my $conflict_num_string = "";
    
    foreach my $conflict_ref (@conflict_list) {
        my %conflict_item = %$conflict_ref;
        $conflict_num_string .= "$conflict_item{'rule_seq'},";
    }
    $conflict_num_string =~ s/,$//;
    $msg = "检测到当前规则$current_seq与规则".$conflict_num_string."冲突";
    my $ret = "<script>warning_box(\"$msg\")</script>";
    return $ret;
}


#
# DESCRIPTION: 对触发冲突检测的规则进行冲突检测，返回冲突列表
# @param:      一条规则hash;
#              一个触发类型
#              一个script_name
#              注意：规则hash中需要添加seq字段，该字段为触发操作前的位置
# @return:     一个冲突列表，每一项记录应包含序号，冲突类型号
#
sub conflict_detection($$$) {
    my $rule_A_ref = shift;
    my $trigger_type = shift;
    $global_script_name = shift;
    foo("global_script_name:$global_script_name\n");
    
    my @conflict_list = ();                                      #冲突列表
    
    my %rule_A = %$rule_A_ref;
    
    my @rule_hash = get_rule_hash(\%rule_A,$trigger_type);       #获取待比较的规则hash list
    foo("rule_hash length = $#rule_hash\n");
    foreach my $tmp_ref (@rule_hash) {
        my %tmp_rule = %$tmp_ref;
        
        my %conflict_hash = ();
        %conflict_hash = compare_rule(\%rule_A,\%tmp_rule);      #进行规则比较
        if (%conflict_hash) {
            push(@conflict_list,\%conflict_hash);
        }
    }
    
    return @conflict_list;
}

#
# DESCRIPTION: 两条规则进行比较，若发现冲突，则返回一条冲突记录
# @param:      规则A的引用
#              规则B的引用
# @return:     若无冲突，返回为空，否则返回一条冲突记录hash，格式为
#              rule_seq
#              conflict_type(在conflict_value中有定义)
#
sub compare_rule($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    my %conflict_hash = ();
    
    my $relation = relation_between(\%rule_A,\%rule_B); #判断两个规则间的集合关系
    foo(">>>$rule_A{'seq'}-$rule_B{'seq'}-relation:$relation\n");
    
    #部分模块，如dnat时没有target字段
    if (not $rule_A{'target'}) {
        $rule_A{'target'} = "";
    }
    if (not $rule_B{'target'}) {
        $rule_B{'target'} = "";
    }
    #当策略相同时
    if ($rule_A{'target'} eq $rule_B{'target'}) {
        #AB重复
        if ($relation eq "=") {
            $conflict_hash{'rule_seq'} = $rule_B{'seq'};
            $conflict_hash{'conflict_type'} = 3;
        }
    }
    #当策略不同时
    else {
        #冲突
        if ($relation eq "=") {
            $conflict_hash{'rule_seq'} = $rule_B{'seq'};
            $conflict_hash{'conflict_type'} = 6;
        }
    }
    
    return %conflict_hash;
}

#
# DESCRIPTION: 判断两个规则间的集合关系
# @param:      规则A的引用
#              规则B的引用
# @return:     一个字符串，代表着规则间的集合关系
#              "=" 表示AB集合相同
#              ""  表示其他
#
sub relation_between($$) {
    my $rule_A_ref = shift;
    my $rule_B_ref = shift;
    
    my %rule_A = %$rule_A_ref;
    my %rule_B = %$rule_B_ref;
    
    foo(">>global:$global_script_name\n");
    #获取关系判断使用子例程名
    my $relation_sub = $module_hash{$global_script_name}->{"relation_sub"};
    #通过子例程名调用子例程
    my $relation_str = $relation_sub->(\%rule_A,\%rule_B);

    
    return $relation_str;
}

#
# DESCRIPTION: 获取待比较规则集
# @param:      待比较的rule hash
#              触发类型
# @return:     一个待比较的规则hash list
#
sub get_rule_hash($$) {
    my $rule_A_ref = shift;
    my $trigger_type = shift;

    my %rule_A = %$rule_A_ref;
    my $rule_pos = -1;
    
    my $config_path = $module_hash{$global_script_name}->{"path"};

    my @rule_list = ();
    my @lines = read_config_file($config_path);
    my $i = 0;
    
    if ($trigger_type eq 'up') {               #触发冲突操作为上移，只需要和该规则的前一条规则进行判断
        $rule_pos = $rule_A{'seq'}-1;
    } elsif ($trigger_type eq 'down') {        #触发冲突操作为下移，只需要和该规则的后一条规则进行判断
        $rule_pos = $rule_A{'seq'}+1;
    }
    
    foreach my $line (@lines) {
        my %config = config_line($line);
        $i++;

        $config{"seq"} = $i;
        if ($rule_pos eq -1) {
            if ($config{'enabled'} eq 'on') {
                push(@rule_list,\%config);
            }
        } else {
            if ($rule_pos eq $i && $config{'enabled'} eq 'on') {
                push(@rule_list,\%config);
            }
        }
    }
    
    my @ret_list = ();
    foreach my $rule_ref (@rule_list) {
        my %rule = %$rule_ref;
        if ($trigger_type eq 'add') {
            #将在新规则之后的seq全部加1
            if ($rule{'seq'} >= $rule_A{'seq'}) {
                $rule{'seq'}++;
            }
        } elsif ($trigger_type eq 'enable') {
            #不与自己进行比较
            if ($rule{'seq'} eq $rule_A{'seq'}) {
                next
            }
        } elsif ($trigger_type =~ /^edit_/) {
            my $old_seq = $trigger_type;
            $old_seq =~ s/edit_//;
            #不与自己之前位置进行比较
            if ($rule{'seq'} eq $old_seq) {
                next;
            }
        }
        push(@ret_list,\%rule);
    }
    
    my @ret_list2 = ();
    #修正edit模式下bug,为edit后的规则重新排序
    if ($trigger_type =~ /^edit_/) {
        my $old_seq = $trigger_type;
        $old_seq =~ s/edit_//;
        
        foreach my $rule_ref (@ret_list) {
            my %rule = %$rule_ref;
            
            if ($old_seq > $rule_A{'seq'}) {
                if( $rule{'seq'} >= $rule_A{'seq'} and $rule{'seq'} < $old_seq ) {
                    $rule{'seq'}++;
                }
            } elsif ($old_seq <= $rule_A{'seq'}) {
                if( $rule{'seq'} > $old_seq and $rule{'seq'} <= $rule_A{'seq'}) {
                    $rule{'seq'}--;
                }
            }
            
            push(@ret_list2,\%rule);
        }
        
        return @ret_list2;
    }
    
    return @ret_list;
}

sub read_config_file($) {
    my $filename = shift;
    my @lines;
    open (FILE, "$filename");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        if (!is_valid($line)) {
            next;
        }
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}

#判断line是否符合基本标准
sub is_valid($) {
    my $line = shift;
    if ($line =~ /(?:(?:[^,]*),)+/) {
        return 1;
    }
    return 0;
}

#
# DESCRIPTION: 调试用函数
# @param:      
# @return:     
#
sub foo($) {
    my $str = shift;
#    open FILE , ">>/root/mylog";
#    print FILE ("$str\n");
#    close FILE;
}

1;
