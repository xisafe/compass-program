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
my $setting_file = "/var/efw/network_diagnose/ping_settings";
my $ping_result_file = "/tmp/network_diagnose/ping";
my $every_return_count = 1;#每次返回多少行数据
my $ping_start_cmd = '/usr/bin/sudo /usr/local/bin/network_diagnose.py -p >/dev/null &';
my $ping_stop_cmd = '/usr/bin/sudo /usr/local/bin/network_diagnose.py -k &>/dev/null &';
my $extraheader ='<script language="JavaScript" src="/include/network_diagnosis_ping.js"></script>';
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
    &getcgihash(\%par);
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
    if ($par{'ACTION'} eq "ping_start"){
        &save_ping_config();
        &ping_start();
    } elsif ($par{'ACTION'} eq "ping_stop") {
        &ping_stop();
    } elsif ($par{'ACTION'} eq "read_ping") {
        &read_ping();
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

sub save_ping_config() {
    my %settings;
    $settings{'IP'} = $par{'target'};
    $settings{'COUNT'} = $par{'ping_num'};
    $settings{'SIZE'} = $par{'ping_size'};

    &writehash($setting_file, \%settings);
}

sub ping_start() {
    my ( $status, $mesg, $data ) = ( -1, "ping", "");
    system($ping_start_cmd);
    # print "111111111111";
    # `$ping_start_cmd`;
    # print "$?";
    
    $status = $?>>8;
    $status = 0;
    if( $status == 0 ) {
        $mesg = "pingOK";
    } else {
        $status = -1;
        $mesg = "pingFailed"
    }
    &send_result( $status, $mesg, $data );
}

sub ping_stop() {
    system($ping_stop_cmd);
    &send_result(0, "stoped", "");
}

sub read_ping() {
    my ($status, $mesg) = (-1, "no result");
    my @ret_lines = ();
    if( -e $ping_result_file) {
        my @lines = read_conf_file($ping_result_file);
        my $total_count = @lines;
        #===判断是否已经写完===#
        if( $lines[$total_count - 1] =~ /end/ ) {
            #===写操作已结束===#
            $mesg = "end"; #去除最后一行
            pop @lines;
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
    <form enctype='multipart/form-data' id="NETWORK_DIAGNOSIS_FORM" name="NETWORK_DIAGNOSIS_FORM" method='post' action="$ENV{'SCRIPT_NAME'}"  onsubmit="start();return false;">
        <table border='0' cellspacing="0" cellpadding="4">
            <tr class="odd">
                <td class="add-div-table">IP地址或域名 *</td>
                <td >
                    <input name="target"/>
                </td>
            </tr>
            <tr class="odd ping_config_tr">
                <td class="add-div-table">ping包数目 *</td>
                <td >
                    <input name="ping_num" value="$settings{'COUNT'}"/>(1-50)
                </td>
            </tr>
            <tr class="odd ping_config_tr">
                <td class="add-div-table">ping包大小 *</td>
                <td >
                    <input name="ping_size" value="$settings{'SIZE'}"/>(4-1472字节)
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
                <textarea style="width: 98%; height: 310px; margin: 5px 0px; padding: 5px; resize: none;font-size: 11px;" id="diagnosis_result" name="diagnosis_result" readonly="readonly"></textarea>
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
                },
                'ping_num':{
                   'type':'text',
                   'required':'1',
                   'check':'num|',
                   'ass_check':function(eve){
                        var ping_num = eve._getCURElementsByName("ping_num","input","NETWORK_DIAGNOSIS_FORM")[0].value;
                        if(ping_num > 50) {
                            return "包数目为1-50";
                        }
                    }
                },
                'ping_size':{
                   'type':'text',
                   'required':'1',
                   'check':'num|',
                   'ass_check':function(eve){
                        var ping_size = eve._getCURElementsByName("ping_size","input","NETWORK_DIAGNOSIS_FORM")[0].value;
                        if(ping_size > 1472 || ping_size < 4) {
                            return "包大小为4-1472字节";
                        }
                    }
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

