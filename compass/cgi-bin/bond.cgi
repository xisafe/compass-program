#!/usr/bin/perl -w
#==============================================================================#
#
# 描述: 链路聚合规则页面
#
# 作者：辛志薇(xinzhiwei) 
# 历史：2014-11-03至2014-11-07 辛志薇创建
#       2015-02-11 王琳修改
#
#==============================================================================#
use Encode;

require '/var/efw/header.pl';
require 'list_panel_opt.pl';   #这个头文件里的函数非常重要，如read_config_lines()等

#=====初始化全局变量到init_data()中去初始化=====================================#
my $need_reload_tag;    #规则改变时需要重新应用的标识
my $extraheader;        #存放用户自定义CSS,JS
my %par;                #存放post方法传过来的数据的哈希
my %query;              #存放通过get方法传过来的数据的哈希
my $LOAD_ONE_PAGE = 0;  #是否只load一页的数据，0表示全部加载
my $json = new JSON::XS;#处理json数据的变量，一般不变
my $ethernet_dir;
my $uplinks_dir;
#=========================全部变量定义end=======================================#

&main();

sub main() {
    #获取post的值
    &getcgihash(\%par);
    #初始化变量值
    &init_data();
    #做出响应
    &do_action();
    # &get_occupied_eths();
    # &get_exist_bonds();
}

sub init_data(){
    $ethernet_dir = "${swroot}/ethernet";
    $uplinks_dir = "${swroot}/uplinks/";
    $need_reload_tag = "$ethernet_dir/need_reload_tag";
    $restart_service = "/usr/local/bin/restart_from_wizard >/dev/null &";
    %BRIDGE_AREA = (
        br0 => 'LAN',
        br1 => 'DMZ',
        br2 => 'WIFI',
    );

    #============扩展的CSS和JS文件-BEGIN========================================================#
    $extraheader = '<link rel="stylesheet" type="text/css" href="/include/add_list_base.css" />
                    <link rel="stylesheet" type="text/css" href="/include/bond.css" />
                    <script language="JavaScript" src="/include/message_manager.js"></script>
                    <script language="JavaScript" src="/include/add_panel.js"></script>
                    <script language="JavaScript" src="/include/list_panel.js"></script>
                    <script language="JavaScript" src="/include/bond.js"></script>';
    #============扩展的CSS和JS文件-BEGIN=======================================================#
}

sub do_action() {
    my $action = $par{'ACTION'};
    my $panel_name = $par{'panel_name'};

    &showhttpheaders();

    #===根据用户提交的数据进行具体反馈,默认返回页面==#
    if ( $action eq 'save_data' ) {
        &save_data();
    }
    elsif ( $action eq 'load_data' ) {
        &load_data();
    }
    elsif ( $action eq 'load_used_area' ) {
        &load_used_area();
    }
    elsif ( $action eq 'apply_data') {
        &apply_data();
    }
    elsif ($action eq 'delete_data') {
        &delete_data();
    }
    else {
        &show_page();
    }
}

sub show_page() {
    &openpage( "链路聚合", 1, $extraheader);
    &display_main_body();
    &closepage();
}

sub display_main_body() {
    printf<<EOF
    <div id="mesg_box_test" class="container"></div>
    <div id="bond_add_panel" class="container"></div>
    <div id="bond_list_panel" class="container"></div>
EOF
    ;
}

sub load_data(){   # 加载数据到页面上
    my %ret_data;
    my @exist_bonds = &get_exist_bonds();
    my @unoccupied_eths = &get_unoccupied_eths();
    my $total_num = scalar @exist_bonds;
    $ret_data{'detail_data'} = \@exist_bonds;
    $ret_data{'total_num'} = $total_num;
    $ret_data{'eths'} = \@unoccupied_eths;
    if ( -e $need_reload_tag ) {
        $ret_data{'reload'} = 1;
    }
    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub load_used_area() {
    my %ret_data, @ret_array;
    $ret_data{'used_area'} = \@ret_array;

    #===组装LAN区数据===#
    my %LAN_CONFIG = (
        dev => "br0",
        text_value => "br0",
        text => "LAN",
        class => "GREEN",
    );
    push( @ret_array, \%LAN_CONFIG );

    if ( orange_used() ) {
        #===组装DMZ区数据===#
        my %DMZ_CONFIG = (
            dev => "br1",
            text_value => "br1",
            text => "DMZ",
            class => "ORANGE",
        );
        push( @ret_array, \%DMZ_CONFIG );
    }

    my %NONE_CONFIG = (
        dev => "none",
        text_value => "none",
        text => "无",
        class => "unoccupied",
    );
    push( @ret_array, \%NONE_CONFIG );

    my $ret = $json->encode(\%ret_data);
    print $ret;
}

sub handle_before_save_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "" );

    #===只有添加没有编辑===#
    if( &get_bond_bridged_area( $par{'bond_name'} ) ne "" ){
        # 此时名字已存在，也要返回对应的消息提示！
        $mesg = "接口名已经存在";
        return ( $status, $reload, $mesg );
    }

    if ( $par{'bond_name'} !~ m/^bond[0-3]$/ ) {
        $mesg = "以bond开头, 范围: bond0-bond3";
        return ( $status, $reload, $mesg );
    }

    if( $par{'selected_member_port'} eq '') {
        $mesg = "链路聚合的成员端口不能为空";
        return ( $status, $reload, $mesg );
    }

    $status=0;
    $reload =0;
    $mesg = "检测合格";
    return( $status, $reload, $mesg ); 
}

sub save_data() {
    #===只有添加，没有编辑====#
    my ( $status, $reload, $mesg ) = &handle_before_save_data();
    if($status != 0){
        &send_status( $status, $reload, $mesg );
        return;
    }

    my ( $bond_name, $bond_area ) = ( $par{'bond_name'}, $par{'bond_area'} );
    my $bond_file = "$ethernet_dir/$bond_name";
    my @selected_member_port = split( ",", $par{'selected_member_port'} );

    #===先向brx文件中添加内容===#
    if ( $BRIDGE_AREA{ $bond_area } ) {
        #=== 向内网区域某个桥接区添加bond口 ===#
        my $bridge_file = "$ethernet_dir/$bond_area";
        my @bridged_eths = &get_bridged( $bond_area );
        my $count = scalar @bridged_eths;
        my @processed_bridged_eths;
        for my $bridged_eth ( @bridged_eths ) {
            push( @processed_bridged_eths, $bridged_eth );
        }
        #===修改brx文件内容===#
        push( @processed_bridged_eths, $bond_name );
        ( $status, $mesg ) = &write_config_lines( $bridge_file, \@processed_bridged_eths );
        if ( $status != 0 ) {
            $mesg = "添加失败";
            &send_status( $status, $reload, $mesg );
            return;
        }
        #===创建bondx文件===#
        system( "touch $bond_file" );
        $status = $?>>8;
        if ( $status != 0 ) {
            #===创建文件失败，回滚并结束===#
            &write_config_lines( $bridge_file, \@bridged_eths );
            $mesg = "添加失败";
            &send_status( $status, $reload, $mesg );
            return;
        }
        #===向bondx文件中添加内容==#
        &write_config_lines( $bond_file, \@selected_member_port );
    } else {
        #===创建bondx文件===#
        system( "touch $bond_file" );
        $status = $?>>8;
        if ( $status != 0 ) {
            $mesg = "添加失败";
            &send_status( $status, $reload, $mesg );
            return;
        } else {
            #===向bondx文件中添加内容==#
            &write_config_lines( $bond_file, \@selected_member_port );
        }
    }

    $reload = 1;
    &create_need_reload_tag();
    $mesg = "添加成功";
    &send_status( $status, $reload, $mesg );
}

sub delete_data() {
    my ( $status, $reload, $mesg ) = ( -1, 0, "未操作" );
    my $bond_name = $par{'id'};
    my $bond_file = "$ethernet_dir/$bond_name";

    my $bond_area = &get_bond_bridged_area( $bond_name );
    if ( $BRIDGE_AREA{ $bond_area } ) {
        #=== 是内网区域某个桥接区的 ===#
        my $bridge_file = "$ethernet_dir/$bond_area";
        my @bridged_eths = &get_bridged( $bond_area );
        my $exist_eths_count = scalar @bridged_eths;
        my @processed_bridged_eths;
        for my $bridged_eth ( @bridged_eths ) {
            if ( $bridged_eth eq $bond_name ) {
                next;
            }
            push( @processed_bridged_eths, $bridged_eth );
        }
        if ( $exist_eths_count > 1 ) {
            #===直接删除bond内容===#
        } else {
            #===打开bond文件内容还原到br*文件下===#
            my @bond_eths =();
            ( $status, $mesg ) = &read_config_lines( $bond_file, \@bond_eths );
            if ( $status != 0 ) {
                $mesg = "删除失败";
                &send_status( $status, $reload, $mesg );
                return;
            }
            @bond_eths = &process_null_string( \@bond_eths );
            @processed_bridged_eths = ( @processed_bridged_eths, @bond_eths );
        }

        #===修改brx文件内容===#
        ( $status, $mesg ) = &write_config_lines( $bridge_file, \@processed_bridged_eths );
        if ( $status != 0 ) {
            $mesg = "删除失败";
            &send_status( $status, $reload, $mesg );
            return;
        }
        #===删除bondx文件===#
        system( "rm $bond_file" );
        $status = $?>>8;
        if ( $status != 0 ) {
            $mesg = "删除失败";
            #==还原brx文件内容==#
            &write_config_lines( $bridge_file, @bridged_eths );
            &send_status( $status, $reload, $mesg );
            return;
        } else {
            $mesg = "删除成功";
            $reload = 1;
            &create_need_reload_tag();
        }
    } else {
        #=== 非内网去的某个bond口，直接删除 ===#
        system( "rm $bond_file" );
        $status = $?>>8;
        if ( $status != 0 ) {
            $mesg = "删除失败";
        } else {
            $mesg = "删除成功";
            $reload = 1;
            &create_need_reload_tag();
        }
    }
    
    &send_status( $status, $reload, $mesg );
}

sub process_null_string($) {
    my $array_ref = shift;
    my @processed_array = ();
    for my $item ( @$array_ref ) {
        chomp $item;
        if ( $item ne "" ) {
            push( @processed_array, $item );
        }
    }
    return @processed_array;
}

sub get_bond_bridged_area($){   # 此函数用于检查新建的接口名称是否已存在
    my $name = shift;
    my @exist_bonds = &get_exist_bonds();
    my $exist_flag = "";
    foreach my $exist_bond ( @exist_bonds ) {
        if ( $exist_bond->{'bond_name'} eq $name ) {
            $exist_flag = $exist_bond->{'bond_area'};
            last;
        }
    }
    return $exist_flag;
}

sub get_bridged($) {
    my $bridge_area = shift;
    my @eths = ();
    if ( $BRIDGE_AREA{ $bridge_area } ) {
        my $bridge_file = "$ethernet_dir/$bridge_area";
        my @read_eths;
        &read_config_lines( $bridge_file, \@read_eths );
        @eths = &process_null_string( \@read_eths );
    }
    return @eths;
}

sub get_exist_bonds() {
    my @exist_bonds = ();
    my %exist_bonds_hash;

    opendir my $bond_dir , $ethernet_dir or return @exist_bonds;
    for my $file ( readdir $bond_dir ) {
        #===第一步，读取桥接口文件内容===#
        if ( $file =~ m/^br\d+$/ ) {
            my @lines = ();
            my $bridge_file = "$ethernet_dir/$file";
            &read_config_lines( $bridge_file, \@lines );
            foreach my $line ( @lines ) {
                chomp $line;
                 #===第二步，读取聚合口文件内容===#
                if ( $line =~ /^bond\d+$/ ) {
                    my $bond_name = $line;
                    my $bond_file = "$ethernet_dir/$line";
                    my @eths = ();
                    my @processed_eths = ();
                    &read_config_lines( $bond_file, \@eths );
                    #===第三步，处理接口内容===#
                    foreach my $eth ( @eths ) {
                        chomp $eth;
                        if ( $eth =~ /^eth\d+$/ ) {
                            push( @processed_eths, $eth );
                        }
                    }
                    my $bond_area = $file;
                    my $selected_member_port = join ",", @processed_eths;
                    #===第四步，组装配置===#
                    my %bond_config = (
                        id => $bond_name,
                        bond_name =>  $bond_name,
                        bond_area => $bond_area,
                        selected_member_port => $selected_member_port,
                        uneditable => 1,
                    );
                    push( @exist_bonds, \%bond_config );
                    $exist_bonds_hash{ $bond_name } = $bond_area;
                }
            }
        }
    }
    closedir $bond_dir;

    opendir my $bond_dir , $ethernet_dir or return @exist_bonds;
    for my $file ( readdir $bond_dir ) {
        #===第二步，读取其他bond口===#
        if ( $file =~ m/^bond\d+$/ ) {
            if ( $exist_bonds_hash{ $file } ) {
                #=== 已存在其他区域 ===#
                next;
            }
            my $bond_name = $file;
            my $bond_file = "$ethernet_dir/$bond_name";
            my @eths = (), @processed_eths = ();
            &read_config_lines( $bond_file, \@eths );
            foreach my $eth ( @eths ) {
                chomp $eth;
                #===第二步，读取聚合口文件内容===#
                if ( $eth =~ /^eth\d+$/ ) {
                    push( @processed_eths, $eth );
                }
            }
            my $selected_member_port = join ",", @processed_eths;
            #===第四步，组装配置===#
            my %bond_config = (
                id => $bond_name,
                bond_name =>  $bond_name,
                bond_area => "none",
                selected_member_port => $selected_member_port,
                uneditable => 1,
            );
            push( @exist_bonds, \%bond_config );
        }
    }
    closedir $bond_dir;

    return @exist_bonds;
}

sub get_occupied_eths($) {
    my @occupied_eths = ();

    #=====第一步，读取桥接口中的物理接口====#
    opendir my $eth_dir , $ethernet_dir or return @occupied_eths;
    for my $file_name ( readdir $eth_dir ) {
        #===第1.1步，读取桥接口文件内容===#
        if ( $file_name =~ /^br\d+$/ ) {
            my @lines;
            my $bridge_file = "$ethernet_dir/$file_name";
            my $bridge_area = $file_name;
            &read_config_lines( $bridge_file, \@lines );
            foreach my $line ( @lines ) {
                chomp $line;
                 #===第1.2步，读取聚合口文件内容===#
                if ( $line =~ /^bond\d+$/ ) {
                    my $bond_name = $line;
                    my $bond_file = "$ethernet_dir/$line";
                    &read_config_lines( $bond_file, \@eths );
                    #===第1.3步，组装bond口中的物理接口===#
                    foreach my $eth ( @eths ) {
                        chomp $eth;
                        if ( $eth =~ /^eth\d+$/ ) {
                            #===第1.4步，组装配置===#
                            my %eth_config = (
                                eth_name =>  $eth,
                                eth_area => $bridge_area,
                                eth_bond => $bond_name,
                                uneditable => 1,
                            );
                            push( @occupied_eths, \%eth_config );
                        }
                    }
                } elsif ( $line =~ /^eth\d+$/ ) {
                    #===第1.4步，组装配置===#
                    my $eth = $line;
                    my %eth_config = (
                        eth_name =>  $eth,
                        eth_area => $bridge_area,
                        eth_bond => "none",
                        uneditable => 1,
                    );
                    push( @occupied_eths, \%eth_config );
                }
            }
        }
    }
    closedir $eth_dir;

    #=====第二步，读取其他bond口中的物理接口====#
    opendir my $bond_dir , $ethernet_dir or return @occupied_eths;
    for my $file ( readdir $bond_dir ) {
        if ( $file =~ m/^bond\d+$/ ) {
            if ( $exist_bonds_hash{ $file } ) {
                #=== 已存在其他区域 ===#
                next;
            }
            my $bond_name = $file;
            $bond_file = "$ethernet_dir/$bond_name";
            &read_config_lines( $bond_file, \@eths );
            foreach my $eth ( @eths ) {
                chomp $eth;
                #===第二步，读取聚合口文件内容===#
                if ( $eth =~ /^eth\d+$/ ) {
                    my %eth_config = (
                        eth_name =>  $eth,
                        eth_area => "none",
                        eth_bond => $bond_name,
                        uneditable => 1,
                    );
                    push( @occupied_eths, \%eth_config );
                }
            }
        }
    }
    closedir $bond_dir;

    #=====第三步，读取外网区的物理接口====#
    opendir my $eth_dir , $uplinks_dir or return @occupied_eths;
    for my $file_name ( readdir $eth_dir ) {
        if ( $file_name =~ m/^\./ ) {
            next;
        }
        #===第2.1步，判断setting文件是否存在===#
        my $setting_file = "$uplinks_dir/$file_name/settings";
        if ( -e $setting_file ) {
            #===第2.2步，读取数据===#
            my %settings_hash;
            &readhash($setting_file,\%settings_hash);
            if ( $settings_hash{'RED_DEV'} =~ m/^eth\d+/ ) {
                #===第2.3步，组装配置===#
                my $eth = $settings_hash{'RED_DEV'};
                my %eth_config = (
                    eth_name =>  $eth,
                    eth_area => "RED",
                    eth_bond => "none",
                    uneditable => 1,
                );
                push( @occupied_eths, \%eth_config );
            }
        }
    }
    closedir $eth_dir;

    return @occupied_eths;
}

sub get_unoccupied_eths(){
    my @unoccupied_eths = ();
    my @occupied_eths = &get_occupied_eths();
    my @all_eths = get_eth();

    # 要显示所有未使用的接口
    foreach my $eth ( @all_eths ) {
        chomp $eth;
        my $occupied_flag = 0;
        for my $occupied_eth ( @occupied_eths ) {
            if ( $occupied_eth->{'eth_name'} eq $eth ) {
                $occupied_flag = 1;
                last;
            }
        }
        if ( $occupied_flag == 0 ) {
            my %eth_config = ();
            $eth_config{'eth_name'} = $eth;
            $eth_config{'eth_color'} = "unoccupied";
            push( @unoccupied_eths, \%eth_config );
        }
    }

    return @unoccupied_eths;
}

sub apply_data() {
    # my ( $status, $reload, $mesg ) = ( -1, 1, "未开始应用" );
    system ( $restart_service );
    &clear_need_reload_tag();
    &send_status( 0, 0, "应用成功" );
}

sub send_status($$$) {
    my ($status, $reload, $mesg) = @_;
    my %hash;
    $hash{'status'} = $status;
    $hash{'reload'} = $reload;
    $hash{'mesg'} = $mesg;
    my $result = $json->encode(\%hash);
    print $result;
}

sub create_need_reload_tag() {
    system( "touch $need_reload_tag" );
}

sub clear_need_reload_tag() {
    system( "rm $need_reload_tag" );
}

