#!/usr/bin/perl
#==============================================================================#
#
# 描述: 检查ips是否正在重启中
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2015.05.15 WangLin创建
#
#==============================================================================#
use Encode;
require '/var/efw/header.pl';

my $running_flag        = "${swroot}/idps/engine/apping_flage";
my $need_reload_tag    = "${swroot}/idps/need_reload_tag";

#获取post请求传过来的变量
&getcgihash(\%par);

my $action = $par{'ACTION'};
&showhttpheaders();

#===根据用户提交的数据进行具体反馈,默认返回页面==#
if ( $action eq 'check_running' ) {
    my ($status, $reload, $mesg) = @_;
    my %hash;
    if ( -f $running_flag ) {
        %hash->{'running'} = 1;
    }
    if ( -f $need_reload_tag ) {
        %hash->{'reload'} = 1;
    }
    my $json = new JSON::XS;
    my $result = $json->encode(\%hash);
    print $result;
}