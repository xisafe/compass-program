#!/usr/bin/perl
use POSIX();
use CGI ':standard';
use Encode;
use CGI::Carp qw (fatalsToBrowser);
use GD;
use GD::Graph::bars;
use GD::Graph::Data;
use GD::Graph::Error;
use strict;
use warnings;
use Spreadsheet::WriteExcel;

#####使用GD画图
my $data=shift(@ARGV);
my @tmp = split(/-/,$data);
my @attack_number;
my $y_max;

push(@attack_number,"IP");
for(my $i = 0;$i < @tmp; $i++){
  if ($tmp[$i] =~ /(.*),(\d+)/) {
    push(@attack_number,$2);
  }  
}

my $max_value_len = rindex $attack_number[1]."\$","\$";####获取最大数字的位数
my $first = $1 if $attack_number[1] =~ /(.)/;          ####获取最大数字的首位

####四舍五入设定Y轴最大值
if ($first < 3) {
    $y_max = 3 * 10**($max_value_len - 1);
}
elsif ($first < 5) {
    $y_max = 5 * 10**($max_value_len - 1);
}
elsif ($first < 8) {
    $y_max = 8 * 10**($max_value_len - 1);
}
else{
     $y_max = 10**$max_value_len;
}
my $len = @attack_number;
my @datas;
foreach my $elem(@attack_number){
    if ($elem < $y_max/400) {
        $elem = POSIX::ceil($y_max/400);
    }
   push(@datas,[$elem]);
}
my $bar_width =  POSIX::ceil(150 / $len);
if ($bar_width > 30) {
    $bar_width = 30;
}
my $graph = GD::Graph::bars->new(400, 300);
$graph->set(
  dclrs             => [qw(#FFFF00 #66CC99 #7DFF00 #3399FF #ECA238 #D94066 #FFCC00 #8C991A #999966 #9933CC #CC9900 #59E699 #D95933 #9926FF #FF99CC #33DF99)],
  x_label           => 'IP',
  #y_label           => 'num',
  #title             => 'Some simple graph',
  y_max_value       => $y_max,
  y_tick_number     => 10,
  bar_spacing       => 5,
  x_plot_values     => 0,
  bar_width         => $bar_width,
  x_ticks           => 0,
  #y_label_skip      => 1
) or die $graph->error;
my $gd = $graph->plot(\@datas) or die $graph->error;
open(IMG, ">/home/httpd/html/images/bars.png") or die $!;
binmode IMG;
print IMG $gd->png;


###画图结束，开始生成报表文件，方便下载
my $file = '/tmp/export.xls';
my $data_file = '/tmp/datafile';
my $sheetName = '防火墙日志报表';
my @datas = read_config_file($data_file);
my $book = new Spreadsheet::WriteExcel( $file );
my $sheet = $book->add_worksheet( decode('utf8',$sheetName));
my $new_format = $book->add_format(align => 'center',size => 24,color => '17');
my $left = $book->add_format(align => 'left'); 
my $left_color = $book->add_format(align => 'left',color => '54'); 
####设置表头样式
my $title = $datas[0];
my @tmp = split(/,/,$title);
$title = $tmp[0];
system("cp /home/httpd/html/images/bars.png /tmp/bars.png");
$sheet->set_column('A:A',20);
$sheet->set_column('B:B',10);
$sheet->set_column('C:C',10);
$sheet->set_column('D:D',10);
#$sheet->write("F1", decode('utf8',$title));
###合并第一行的单元格
$sheet->merge_range("A1:M1",decode('utf8',$title),$new_format);
$sheet->insert_image('G6',"/tmp/bars.png");
$sheet->write("A4", decode('utf8',$tmp[1]),$left_color);
$sheet->write("B4", decode('utf8',"总次数"),$left_color);
$sheet->write("C4", decode('utf8',"允许次数"),$left_color);
$sheet->write("D4", decode('utf8',"阻断次数"),$left_color);
my $start_row = 5;

#删除数组第一行元素，第一行元素为标题.by zhouji
splice(@datas, 0, 1);

foreach my $line(@datas){
    if ($line =~ /^\d+/) {
        my @elem = split(/,/,$line);
        for (my $i = 0; $i < @elem; $i++) {
            $sheet->write($start_row, $i, $elem[$i] ,$left);
        }
        $sheet->set_row($start_row,18);
        $start_row ++;
    }
}
$book->close();

sub read_config_file($) {
    my @lines;
    my $file=shift;
    open (FILE, "$file");
    foreach my $line (<FILE>) {
        chomp($line);
        $line =~ s/[\r\n]//g;
        push(@lines, $line);
    }
    close (FILE);
    return @lines;
}