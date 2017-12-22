#!/usr/bin/perl

#===============================================================================#
#
# DESCRIPTION: 入侵防护->引擎配置->引擎配置
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2014.05.28
#===============================================================================#

require '/var/efw/header.pl';


my %settings;
my $restart     = "/usr/local/bin/restarttopology";

my $extraheader = '<link rel="stylesheet" type="text/css" href="/include/idps_topological_graph.css"/>';

&show_page();



sub show_page() {
    &showhttpheaders();
    system( $restart );#重新生成图片
    &openpage("拓扑图", 1, $extraheader);
    &openbigbox($errormessage, $warnmessage, $notemessage);
    &display_topology();
    &closepage();
}

sub display_topology() {
    printf <<EOF
    <div class="containter-div">
        <div class="containter-div-header-title">系统拓扑图</div>
        <div class="containter-div-content">
            <object data="../images/ips_topology.svg" type="image/svg+xml"></object>
        </div>
    </div>
EOF
    ;
}