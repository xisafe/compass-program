#!/usr/bin/perl -w
#  2015.5.12 modified by Julong Liu
use CGI();
use URI::Escape;

require "/var/efw/header.pl";
print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

my $STATUS_DIR="${swroot}/HA/status/";
my $status = "";
my $exsit_flag = 0;

my @sync_status = ("SYNC", "NOSYNC");
my @run_status = ("FAULT", "SLAVE", "MASTER", "QUIET");
my @run_status1 = ("FAULT1", "SLAVE1", "MASTER1", "QUIET1");
my @run_status2 = ("FAULT2", "SLAVE2", "MASTER2", "QUIET2");
my @link_status = ("CONNECTED", "DISCONNECTED");
&validateUser();
system("/usr/bin/sudo /usr/local/bin/checksync");
system("/usr/bin/sudo /usr/local/bin/checksshstatus");

foreach my $link_name(@link_status) {
    my $file_path = $STATUS_DIR.$link_name;
    if(-e $file_path)
    {
        $exsit_flag = 1;               
        if ($link_name eq "CONNECTED") {
            $status= "===1";
        }
        else{
            $status= "===0";
        }
    }
}
if ( $exsit_flag == 0 ) {
    $status = "===0";
}

$status .= ",";
$exsit_flag = 0;
my $i = 0;
foreach my $run_name(@run_status) {
  my $file_path = $STATUS_DIR.$run_name;
  if(-e $file_path)
  {
      $exsit_flag = 1;
      $status .= $i;
  }
  $i++;
}
if ( $exsit_flag == 0 ) {
    $status .= "0";
}

#added by Julong Liu
$status .= ",";
$exsit_flag = 0;
my $j = 0;
foreach my $run_name1(@run_status1) {
  my $file_path = $STATUS_DIR.$run_name1;
  if(-e $file_path)
  {
      $exsit_flag = 1;
      $status .= $j;
  }
  $j++;
}
if ( $exsit_flag == 0 ) {
    $status .= "0";
}

#added by Julong Liu
$status .= ",";
$exsit_flag = 0;
my $k = 0;
foreach my $run_name2(@run_status2) {
  my $file_path = $STATUS_DIR.$run_name2;
  if(-e $file_path)
  {
      $exsit_flag = 1;
      $status .= $k;
  }
  $k++;
}
if ( $exsit_flag == 0 ) {
    $status .= "0";
}

$status .= ",";
$exsit_flag = 0;
foreach my $sync_name(@sync_status) {

    my $file_path = $STATUS_DIR.$sync_name;
    if(-e $file_path)
    {
        $exsit_flag = 1;               
        if ($sync_name eq "SYNC") {
            $status .= "1";
    }
    else{
        $status .= "0";
        }
    }
}
if ( $exsit_flag == 0 ) {
     $status .= "0";
}

print $status;
