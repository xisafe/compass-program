#!/usr/bin/perl
#===============================================================
#
# DESCRIPTION: 网络状态页面
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# HISTORY:
#   2014.08.28 Created by WangLin
#===============================================================

require '/var/efw/header.pl';

my %par;
my $netstatus_json = 'sudo /usr/local/bin/netstatus_json.py';
my $extraheader = '<script language="JavaScript" src="/include/network_status.js"></script>';

&getcgihash(\%par);
&do_action();

sub do_action() {
    my $action = $par{'ACTION'};

    if ($action eq 'load_data') {
        &load_data();
    } else {
        &display_page();
    }
}

sub load_data() {
    my $return_data = `$netstatus_json`;

    &showhttpheaders();
    print $return_data;
}

sub display_page() {
    &showhttpheaders()
    &openpage( _('Network status'), 1, $extraheader );
    &display_status_table();
    &closepage();
}

sub display_status_table() {
    printf <<EOF
    <table class="table-style" style="margin-top: 20px;">
        <tr class="table-header">
            <td style="width:8%;">区域</td>
            <td style="width:15%;">IP/掩码</td>
            <td style="width:10%;" colspan="2">接口</td>
            <td style="width:13%;">MAC地址</td>
            <td style="width:15%;">接口速率</td>
            <td style="width:9%;">网口状态</td>
            <td style="width:15%;">当前流入速率</td>
            <td style="width:15%;">当前流出速率</td>
        <tr>
        <tbody id="network_status_body">
            <tr class="odd">
                <td colspan="9">正在加载...</td>
            </tr>
        </tbody>
        <tr class="table-footer"><td colspan="9">&nbsp;</td></tr>
    </table>
EOF
    ;
}