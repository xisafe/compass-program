#!/usr/bin/perl
#殷其雷 2013-5-7
require '/var/efw/header.pl';

my $description_folder = "/var/efw/openvpn/resources/description/";
my $description_change_file = "/var/efw/openvpn/resources/changefile";
my $max_des_file_num = 99;

#根据资源名称读取对应描述信息文件中内容并将其转化为一条长字符串以||分割。旧
sub read_description($){
    my $get = shift;
	my @getlines = split(/\n/,$get);
	my $description_name = $getlines[0];
	chomp($description_name);
	my $description_file = $description_folder;
	$description_file .= $description_name;
	my @description;
	my $return_description="";
	my $fail = 0;
	if(!(-e $description_file))
	{
	   return "描述信息不存在！";
	} else {
	   open(FILE,$description_file) or $fail = 1;
	   @description = <FILE>;
	   close(FILE);
	   my $length = scalar(@description);
	   if($length == 0)
	   {
	      return "描述信息为空！";
	   } else {
	      my $count = 1;
	      foreach my $line (@description)
	      {
	         $return_description .= $line;
			 if($count < $length)
			 {
			   $return_description .= "&";
			 }
			 $count++;
	      }
		  return $return_description;
		  
	   }
	}
	if($fail)
	{
	   return "描述信息文件打开失败！";
	}
}

#根据资源名称读取对应描述信息文件中内容并将其转化为一条长字符串不分割。旧
sub read_description_notsplit($){
    my $description_name = shift;
	my $description_file = $description_folder;
	$description_file .= $description_name;
	my @description;
	my $return_description="";
	my $fail = 0;
	if(!(-e $description_file))
	{
	   return "描述信息不存在！";
	} else {
	   open(FILE,$description_file) or $fail = 1;
	   @description = <FILE>;
	   close(FILE);
	   my $length = scalar(@description);
	   if($length == 0)
	   {
	      return "描述信息为空！";
	   } else {
	      foreach my $line (@description)
	      {
	         $return_description .= $line;
	      }
		  return $return_description;
		  
	   }
	}
	if($fail)
	{
	   return "描述信息文件打开失败！";
	}
}

#根据资源名读取对应描述文件，失败则返回-1。
sub readdesfile($){
    my $file_name = shift;
	my $num = &search_des_num($file_name);
	if($num eq -1)
	{
	   return $num;
	} else {
	   return &get_des($num);
	}
}

#根据资源名创建一个文件存放描述信息,返回0为同名资源已经存在，资源以一行形式存储，0为存在同名资源,-1为达到最大数量不能添加,1为添加成功。
sub mkdesfile($$){
    my $filename = shift;
	my $des = shift;
	my $check_exist = &check_file_exist($filename);
	if($check_exist eq 1)
	{
	   return 0;
	}
    my $free_num = &get_free_des_num();
	if($free_num eq -1)
	{
	   return -1;
	} else {
	   &mk_change_line($filename,$free_num);
	   &mk_des_file($free_num,$des);
	   return 1;
	}
}

#根据资源名删除一个文件描述信息
sub rmdesfile($){
    my $file_name = shift;
	my $num = &search_des_num($file_name);
	if($num eq -1)
	{
	   return;
	} else {
	   &rm_change_file($file_name);
	   &rm_des_file($num);
	   return;
	}
}

#根据资源名修改一个文件描述信息，-1为失败，1为成功。
sub modifydesfile($$){
    my $filename = shift;
	my $des = shift;
	my $num = &search_des_num($file_name);
	if($Num eq -1)
	{
	   return $num;
	} else {
	   &rm_des_file($num);
	   my $total_name = $description_folder;
	   $total_name .= "des";
 	   $total_name .= $num;
	   chomp($total_name);
	   `touch $total_name`;
	   `echo >>$total_name $des`;
	}
}

#根据转换文件获取一个最小的未使用的文件编号,返回-1为达到最大数量不能添加。
sub get_free_des_num(){
    my @lines;
    open(FILE,$description_change_file);
	@lines = <FILE>;
	close(FILE);
	
	my $count=0;
	my $notfind = 1;
    my $match = 0;
	my $match_num = -1;
	while($notfind&&($count <= $max_des_file_num))
	{
	   foreach my $line (@lines)
       {
		  my @line_splited = split(/,/,$line);
	      chomp($line_splited[1]);
		  if($count eq $line_splited[1])
		  {
			 $match = 1;
		  }
	   }
	   if($match)
	   {
		  $match = 0;
		  $count++;
	   } else {
		  $notfind = 0;
		  $match_num = $count;
	   }
   }
   return $match_num;
}

#根据资源名获取描述文件编号，未查到返回-1
sub search_des_num($){
    my $file_name = shift;
	my @lines;
    open(FILE,$description_change_file) or return -1;
	@lines = <FILE>;
	close(FILE);
	
	if(scalar(@lines)==0)
	{
	   return -1;
	} else {
	   foreach my $line(@lines)
	   {
	      my @line_splited = split(/,/,$line);
		  if($line_splited[0] eq $file_name)
		  {
		      return $line_splited[1];
		  }
	   }
	   return -1;
	}
}

#根据一个编号及描述信息创建一个新的描述文件。
sub mk_des_file($$){
    my $file_num = shift;
	my $des_line = shift;
    my $des_file = $description_folder;
	$des_file .= "des$file_num";
	if(!(-e $description_folder))
	{
	   `mkdir $description_folder`;
	}
	`echo >>$des_file $des_line`;
}

#根据一个编号及文件名创建一行新的转换文件。
sub mk_change_line($$){
    my $file_name = shift;
	my $num = shift;
	my $change_line = $file_name;
	$change_line .= ",";
	$change_line .= $num;
	`echo >>$description_change_file $change_line`;
}

#根据一个文件名查看是否有同名文件存在，存在返回1，不存在返回0;
sub check_file_exist($){
    my $file_name = shift;
	my @lines;
    open(FILE,$description_change_file);
	@lines = <FILE>;
	close(FILE);
	my $match = 0;
	foreach my $line (@lines)
	{
	   my @line_splited = split(/,/,$line);
	   if($line_splited[0] eq $file_name)
	   {
	      $match = 1;
	   }
	}
	return $match;
}

#根据编号获取文件中的描述内容，以一行字符串返回，行之间不分割，错误则返回相应错误信息。
sub get_des($){
    my $filenum = shift;
	my $total_name = $description_folder;
	$total_name .= "des";
	$total_name .= $filenum;
	chomp($total_name);
	if(!(-e "$total_name"))
	{
	   return "描述文件不存在！";
	} else {
	   open(FILE,$total_name) or return "描述文件打开失败！";
	   my $return_line = <FILE>;
	   close(FILE);
	   if($return_line eq "")
	   {
	      return "描述文件为空！";
	   } else {
	      return $return_line;
	   }	   
   }
}

#根据一个文件名删除装换文件中对应行。
sub rm_change_file($){
    my $file_name = shift;
	my @lines;
	my @new_lines;
	my $count=0;
	my $new_count=0;
	open(FILE,$description_change_file);
	@lines = <FILE>;
	close(FILE);
	foreach my $line (@lines)
	{
	   my @split = split(/,/,$line);
	   if($split[0] ne $file_name)
	   {
	      $new_lines[$new_count++] = $lines[$count];
	   }
	   $count++;
	}
	`rm $description_change_file`;
	`touch $description_change_file`;
	foreach my $new_line (@new_lines)
	{
	   `echo >>$description_change_file $new_line`;
	}
}

#根据一个编号删除对应的描述文件。
sub rm_des_file($){
    my $num = shift;
	my $total_name = $description_folder;
	$total_name .= "des";
    $total_name.= $num;
	chomp($total_name);
	`rm $total_name`;
}

1;