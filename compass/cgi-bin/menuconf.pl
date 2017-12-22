#!/usr/bin/perl
sub read_menu_settings(){
	my $file = "/var/efw/menu/settings";
	open (FILE,"$file");
	my $line_num = 1;
	my %mainmenu;
	foreach my $menu (<FILE>){
		chomp($menu);
		if($menu && $menu !~ /^#/){
			#===这里需要优化一下，在10以前的数字需要在前面加0，不然以后排序会出错，10以后20以前的项目会排在2之前，===#
			#===一般一级菜单不超过100，所以不用考虑100以后的数字，如果出现这种情况，还要另作考虑 by wl 2014.2.20=====#
			#===优化开始 by wl 2014.2.20================#
			my $num = $line_num;
			if($line_num < 10){
				$num = "0".$num;
			}
			#$mainmenu{$menu} = $line_num;#原始代码
			$mainmenu{$menu} = $num;
			#============end============================#
			$line_num ++;
		}
	}
	close(FILE);
	return %mainmenu;
}

1
;