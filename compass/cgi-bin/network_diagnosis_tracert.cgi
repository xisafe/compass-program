#!/usr/bin/perl

#===============================================================================
# DESCRIPTION: 网络诊断，包括ping和traceroute程序
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2014/03/27-09:00
#===============================================================================

require '/var/efw/header.pl';

my $setting_dir = "/var/efw/network_diagnose";
my $setting_file = "/var/efw/network_diagnose/tracert_settings";
my $result_file = "/tmp/network_diagnose/tracert";
my $start_cmd = 'sudo /usr/local/bin/network_diagnose.py -t &>/dev/null &';
my $stop_cmd = 'sudo /usr/local/bin/network_diagnose.py -k &>/dev/null &';
my $extraheader ='<script language="JavaScript" src="/include/network_diagnosis_tracert.js"></script>';
my %par;
my %save;
my $errormessage='';
my $warnmessage='';
my $notemessage='';

&init();
showhttpheaders();
&do_action();


sub init() {
    &make_file();
    &load_config();
    getcgihash(\%par);
}

sub make_file() {
    if(!-e $setting_dir){
        system("mkdir $setting_dir"); 
    }

    if(!-e $setting_file){
        system("touch $setting_file"); 
    }
}

sub load_config() {
    ###读取配置文件显示
    if(-e $setting_file) {
        #readhash($setting_file,\%settings);
    }
}

sub do_action() {
    chomp($par{'ACTION'});
    if ($par{'ACTION'} eq "start"){
        &save_settings();
        &start();
    } elsif ($par{'ACTION'} eq "stop") {
        &stop();
    } elsif ($par{'ACTION'} eq "read_result") {
        &read_result();
    } else {
        openpage("网络诊断", 1, $extraheader);
        openbigbox($errormessage, $warnmessage, $notemessage);
        &display_config();
        &display_result();
        closebigbox();
        &check_form();
        closepage();
    }
}

sub save_settings() {
    my %settings;
    $settings{'IP'} = $par{'target'};
    &writehash($setting_file, \%settings);
}

sub start() {
    my ( $status, $mesg, $data ) = ( -1, "tracert", "");
    system($start_cmd);
    $status = $?>>8;
    if( $status == 0 ) {
        $mesg = "tracertOK";
    } else {
        $status = -1;
        $mesg = "tracertFailed"
    }
    &send_result( $status, $mesg, $data );
}

sub stop() {
    system($stop_cmd);
    &send_result(0, "stoped", "");
}

sub read_result() {
    my ($status, $mesg) = (-1, "no result");
    my @ret_lines = ();
    if( -e $result_file) {
        my @lines = read_conf_file($result_file);
        my $total_count = scalar @lines;
        #===判断是否已经写完===#
        if( $lines[$total_count - 1] =~ /end/ ) {
            #===写操作已结束===#
            $mesg = "end";
            pop @lines; #去除最后一行
        } else {
            #===写操作没有结束===#
            $mesg = "continue";
        }
        $status = 0;
        @ret_lines = @lines;
        send_result($status, $mesg, \@ret_lines);

    } else {
        send_result($status, $mesg, \@ret_lines);
    }
}

sub send_result($$$) {
    my ($status, $mesg, $data) = @_;
    my %hash;
    %hash->{'status'} = $status;
    %hash->{'mesg'} = $mesg;
    %hash->{'data'} = $data;
    my $json = new JSON::XS;
    my $result = $json->encode(\%hash);
    print $result;
}

sub display_config() {
    my %settings;
    if ( -f $setting_file ) {
        &readhash($setting_file,\%settings);
    }
    &openbox('100%', 'left', "网络诊断");
    printf <<EOF
    <form enctype='multipart/form-data' id="NETWORK_DIAGNOSIS_FORM" name="NETWORK_DIAGNOSIS_FORM" method='post' action="$ENV{'SCRIPT_NAME'}" onsubmit="start();return false;">
        <table border='0' cellspacing="0" cellpadding="4">
            <tr class="odd">
                <td class="add-div-table">IP地址或域名 *</td>
                <td >
                    <input name="target"/>
                </td>
            </tr>

            <tr  class="table-footer">
                <td colspan="2">
                    <input class="net_button" type="submit" id="begin" name="begin" value="开始"/>
                    <input class="net_button" type="button" id="stop" name="stop" value="停止" onclick="stop_fetch_data(); return false;" disabled/>
                </td>
            </tr>

        </table>
    </form>
EOF
    ;

    &closebox();
}

sub display_result() {
    &openbox('100%', 'left', "诊断结果");
    printf <<EOF
    <table width="96%" border='0' cellspacing="0" cellpadding="4" style="padding:0px;">
        <tr class="odd" style="padding:0px;">
            <td width="96%" style="padding:0px;">
                <textarea style="width: 98%; height: 350px; margin: 5px 0px; padding: 5px; resize: none" id="diagnosis_result" name="diagnosis_result" readonly="readonly"></textarea>
            </td>
        </tr>
    </table>
EOF
    ;
    &closebox();
}

sub check_form()
{
    printf <<EOF
    <script>
    var object = {
        'form_name':'NETWORK_DIAGNOSIS_FORM',
        'option':{
            'target':{
               'type':'text',
               'required':'1',
               'check':'ip|domain|',
            }
        }
    }
    var check = new ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("NETWORK_DIAGNOSIS_FORM");
    </script>
EOF
    ;
}

