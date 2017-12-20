#!/usr/bin/perl
require '/var/efw/header.pl';
my $uptime = "";
#将框架分html写入

my $run_days;
my $run_hour;
my $run_minute;
my $host_name;
my $host_dir = "hostname";
my $hirel_dir = "/var/efw/hirel/settings";
my $hirel;
my $hirel_enabled = 0;
my %hirel_setting ;
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;
my $system_title;

#读取系统信息

&read_config();

sub read_config(){
    if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    $system_title = $system_settings{'SYSTEM_TITLE'};
}

sub read_host()
{
    $host_name = `$host_dir`;
    my @temp = split(/\./,$host_name);
    $host_name = $temp[0];
}

sub read_hirel()
{
    &readhash($hirel_dir,\%hirel_setting);
    $hirel = $hirel_setting{"STATE"};
    if($hirel_setting{"STATE"} eq "MASTER")
    {

        $hirel = "主机";
        

    }elsif($hirel_setting{"STATE"} eq "BACKUP")
    {

        $hirel = "备机";
    }

    if($hirel_setting{"HI_ENABLED"} eq "1")
    {

        $hirel_enabled = 1;
    }else{
        $hirel_enabled = 0;
    }

}

sub sys_run_time($)
{
    my $sys_time = shift;
    my @time = split("\\s",$sys_time);
    my $run_time = $time[0];
    $run_days=int($run_time / 86400);
    $run_hour=int(($run_time % 86400)/3600);
    $run_minute=int(($run_time % 3600)/60);
}


sub footer_html()
{
    $uptime = `cat /proc/uptime`;
    sys_run_time($uptime);
    printf <<EOF
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>
            $system_title
        </title>
        <link rel="shortcut icon" href="/images/shortcut.ico" />
        <!--<link rel="stylesheet" type="text/css" href="/include/main.css" />-->
        <link rel="stylesheet" type="text/css" href="/include/main.css" />

        <script language="javascript" type="text/javascript" src="/include/jquery.js">
        </script>
		<script language="JavaScript" type="text/javascript" src="/include/jquery.md5.js"></script>
        <script language="javascript" type="text/javascript" src="/include/run_time.js">
        </script>
        <script type="text/javascript" src="/include/for_iE6_png.js">
        </script>
    </head>
    
    <body>
        <div class="main-footer" >
            <table>
                <tr>

                    <td class="host-name">
                        <span >
                            <img src="/images/shortcut.ico" />
                            <b class="note_title">
                                [主机名]
                            </b>
                            <span id="hostname" class="footer_msg">
                                $host_name
                            </span>
                        </span>
                        <span class="hirel" >
                            &nbsp;
EOF
    ;

    if($hirel_enabled)
    {

        printf <<EOF
                            <b class="note_title">
                                [双机热备]
                            </b>
                            <span  class="footer_msg">
                                $hirel
                            </span>

EOF
        ;
    }



    printf <<EOF
                        </span>
                    </td>


                    <td class="copy-right">
                        <span >
                            Copyright @ 2017 %s, All rights Reserved
                        </span>
                    </td>

                    <td class="time">
                        <span >
                            <b class="note_title">
                                [%s]
                            </b>
                            <span id="sys_run_time" class="footer_msg">
                                <span id="day">
                                    $run_days
                                </span>
                                %s
                                <span id="hour">
                                    $run_hour
                                </span>
                                %s
                                <span id="min">
                                    $run_minute
                                </span>
                                %s




EOF
    ,$system_settings{'COMPANY_WEBSITE'}
    , _('运行时间')
    , _('days')
    , _('hours')
    , _('minutes')
    ;

    my $cur_time = `date "+%Y-%m-%d %H:%M"`;
    printf <<EOF
                            </span>
                            &nbsp;&nbsp;

                            <span >
                                <b class="note_title">
                                    [当前时间]
                                </b>
                                <span id="run_time" class="footer_msg">
                                    $cur_time
                                </span>
                            </span>
                        </span>
                    </td>
                </tr>
            </table>


        </div>
        <div id= "div_lock_footer" class="popup-mesg-box-cover" > </div>
    </body>

</html>
EOF
    ;

}

showhttpheaders();
read_host();
#read_hirel();
footer_html();