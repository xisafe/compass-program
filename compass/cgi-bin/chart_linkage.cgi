#!/usr/bin/perl
# AUTHOR: 刘炬隆(Liu Julong)
# COMPANY: capsheaf
# CREATED: 2014/08/25
require '/var/efw/header.pl';

my $errormessage = "";
my $warnmessage  = "";
my $notemessage  = "";
my $confdir = '/var/lib/sessionmanager/sessiondbm/';
my $cmd = 'sudo /usr/local/bin/session_statistic.py';
my $JFile_hour = $confdir.'hourly.log';
my $JFile_day = $confdir.'day.log';
my $JFile_week = $confdir.'week.log';
my $JFile_month = $confdir.'month.log';
my $JFile_history = $confdir.'contrast.log';
my $extraheader  = '<script language="javascript" type="text/javascript" src="/include/echarts-plain.js"></script>';
   $extraheader .= '<script language="javascript" type="text/javascript" src="/include/chart_linkage_controller.js"></script>';
   $extraheader .= '<script language="javascript" type="text/javascript" src="/include/dot_preproccess.js"></script>';
sub display()
{
    &openbox('100%', 'left', _("会话连接统计曲线"));
    printf <<EOF
        <div style="margin-left:65px;margin-top:10px">
            <span style="font-size:12px;font-weight:bold">选择统计方式</span>
            <select id="style_count" onchange="changeChart(this);" onkeyup="changeChart(this);"><option value="hour" onclick="changeChart(this);">最近一小时</option><option value="day" onclick="changeChart(this);">最近一天</option>
            <option value="week" onclick="changeChart(this);">最近一周</option><option value="month" onclick="changeChart(this);">最近一月</option>
            </select>
        </div>
        <div id="chart_recent" style="height:300px;border:0px solid #ccc;padding:10px;"></div>
EOF
;
    &closebox();
    &openbox('100%', 'left', _("历史会话对比"));
    printf <<EOF
        <div id="chart_history" style="height:300px;border:0px solid #ccc;padding:10px;"></div>
EOF
;
    &closebox();
}

#加载数据
sub load_data(){
    system($cmd.' -o');
    system($cmd.' -a');
    system($cmd.' -w');
    system($cmd.' -m');
    system($cmd.' -t');
    my $sessioninfo_hour = '';
    $sessioninfo_hour = &readJfile($JFile_hour);
    $sessioninfo_hour = '{sessioninfo_hour:'.$sessioninfo_hour.',';
    
    my $sessioninfo_day = '';
    $sessioninfo_day = &readJfile($JFile_day);
    $sessioninfo_day = 'sessioninfo_day:'.$sessioninfo_day.',';
    
    my $sessioninfo_week = '';
    $sessioninfo_week = &readJfile($JFile_week);
    $sessioninfo_week = 'sessioninfo_week:'.$sessioninfo_week.',';
    
    my $sessioninfo_month = '';
    $sessioninfo_month = &readJfile($JFile_month);
    $sessioninfo_month = 'sessioninfo_month:'.$sessioninfo_month.',';
    
    my $sessioninfo_history = '';
    $sessioninfo_history = &readJfile($JFile_history);
    $sessioninfo_history = 'sessioninfo_history:'.$sessioninfo_history.'}';
    
    print $sessioninfo_hour.$sessioninfo_day.$sessioninfo_week.$sessioninfo_month.$sessioninfo_history; 
}

sub load_data_hour(){
    system($cmd.' -o');
    my $sessioninfo_hour = '';
    $sessioninfo_hour = &readJfile($JFile_hour);
    $sessioninfo_hour = '{sessioninfo_hour:'.$sessioninfo_hour.'}';
    print $sessioninfo_hour;
}


sub readJfile($){
    my $fileName = shift;
    my $temp = '';
    open JFILE,$fileName;
    while (<JFILE>){
        $temp.=$_;
    }
    $temp =~ s/\r\n//g;
    close JFILE;
    return $temp;
}
sub do_action(){
    my $action = $par{'ACTION'};
    if($action eq 'load_data'){
        &load_data();
    }elsif($action eq 'load_data_hour'){
        &load_data_hour();
    }else{
        &openpage(_('连接曲线'), 1, $extraheader);
        &openbigbox($errormessage, $warnmessage, $notemessage);
        &display();
        &closepage();
    }
}


&getcgihash(\%par);
&showhttpheaders();
&do_action();