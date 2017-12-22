#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: 防火墙部分检查规则修改具体的项目
#
# AUTHOR: 张征 (Elvis), 359552507@qq.com
# COMPANY: nesec_firewall
# CREATED: 2013/04/28-9:04
#===============================================================================

require '/var/efw/header.pl';

sub check_change($$$){
	my $old_value = shift;
	my $new_value = shift;
	my $line_message = shift;
	my $message="";
	my @old = split(/,/,$old_value);
	my @new = split(/,/,$new_value);
	my @messages = split(/,/,$line_message);
	for (my $num = 0; $num < @old; $num++) {
		if ($old[$num] ne $new[$num]) {
			if (!$old[$num]) {
				$old[$num] = "任意";
			}
			if (!$new[$num]) {
				$new[$num] = "任意";
			}
			$message .= "$messages[$num]由$old[$num]变为$new[$num];";
		}
	}
	if(!$message){
		$message = "未修改参数";
	}
	return $message;
}
sub build_rule($$){
	my $line_value = shift;
	my $line_message = shift;
	my $message="";
	my @values = split(/,/,$line_value);
	my @messages = split(/,/,$line_message);
	for (my $num = 0; $num < @values; $num++) {		
		if (!$values[$num]) {
			$values[$num] = "任意";
		}
		$message .= "$messages[$num]是$values[$num];";
	}
	if(!$message){
		$message = "未修改参数";
	}
	return $message;
}

1;