#!/usr/bin/perl

use Encode;
use Digest::MD5;
require '/var/efw/header.pl';

my $passwd_modify_time_file = "/var/efw/userinfo/passwd_modify_time";
my $user_config_file = '/var/efw/userinfo/user_config'; 
my %user_passwd_md_time;
my %par;

&showhttpheaders('json');
&make_file();
&getcgihash(\%par);
&get_passwd_modify_time();
&do_action();

sub do_action() {
    my $action = $par{'ACTION'};

    if ( $action eq "change_passwd" ) {
        &change_passwd();
    } elsif ( $action eq "lock_check" ) {
        &lock_check();
    }
}

sub lock_check() {
    my @users = &getCurUser();

    if ( @users < 1 ) {
        &send_status( 0, "用户未登录" );
        return;
    }

    my $cur_user = $users[0];

    if ( !exists $user_passwd_md_time{$cur_user} ) {
        &send_status( -1, "目前您尚未修改过初始密码，请修改密码" );
        return;
    }
    # 检查密码是否使用过久
    my %user_config_hash;
    readhash( $user_config_file, \%user_config_hash );
    my $PASSWD_TIMEOUT = 7; # 默认设置为7
    if ( exists $user_config_hash{'PASSWD_TIMEOUT'} ) {
        $PASSWD_TIMEOUT = $user_config_hash{'PASSWD_TIMEOUT'};
    }
    my $modified_time = time - $user_passwd_md_time{$cur_user};
    my $subtraction = $modified_time - ($PASSWD_TIMEOUT * 24 * 60 * 60);
    if ( $subtraction > 0 ) {
        # 超时了
        &send_status( -1, "您太长时间没有修改过密码，修改后才能使用" );
        return;
    } else {
        &send_status( 0, "" );
        return;
    }
}

sub change_passwd() {
    my @users = &getCurUser();

    if ( @users < 1 ) {
        &send_status( -1, "用户未登录" );
        return;
    }

    my $cur_user = $users[0];

    # my $md5 = Digest::MD5->new;
    # $md5->add($par{'primary_passwd'});
    # my $primary_passwd = $md5->hexdigest;
    my $primary_passwd = &decryptFn($par{'primary_passwd'});
    my @user_info = read_users_file();
    my $modified_flag = 0;
    for( my $i = 0; $i < @user_info; $i++ )
    {
        my $user = $user_info[$i];
        my @user_temp = split(",",$user);
        if($cur_user eq $user_temp[0])
        {
            if ( $primary_passwd eq $user_temp[1] ) {
                # 开始修改密码
                $modified_flag = 1;
                # my $new_md5 = Digest::MD5->new;
                # $new_md5->add($par{'new_passwd'});
                # my $new_passwd = $new_md5->hexdigest;
                
                my $new_passwd = &decryptFn($par{'new_passwd'});
                if ( $new_passwd eq $primary_passwd ) {
                    &send_status( -1, "新密码不能和原始密码相同" );
                    return;
                }
                $user_temp[1] = $new_passwd;
                $user_info[$i] = join( ",", @user_temp );
                write_users_file(\@user_info);
                $user_passwd_md_time{$cur_user} = time;
                &save_passwd_modify_time();
                &send_status( 0, "修改成功" );
                return;
            } else {
                &send_status( -1, "原始密码不正确" );
                return;
            }
        }
    }

    &send_status( -1, "未找到相应用户" );
}

sub get_passwd_modify_time() {
    readhash( $passwd_modify_time_file, \%user_passwd_md_time );
}

sub save_passwd_modify_time() {
    writehash( $passwd_modify_time_file, \%user_passwd_md_time );
}

sub send_status($$) {
    my $status = shift;
    my $mesg = shift;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'mesg'} = $mesg;
    my $json = new JSON::XS;
    my $result = $json->encode(\%hash);
    print $result;
}

sub make_file() {
    if ( !-f $passwd_modify_time_file ) {
        system( "touch $passwd_modify_time_file" );
    }
}