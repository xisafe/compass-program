#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: graphs.cgi,v 1.9.2.1 2004/05/15 22:04:15 gespinasse Exp $
#

require '/var/efw/header.pl';

my %cgiparams;
my %pppsettings;
my %netsettings;
my (@cgigraphs, @graphs);

&showhttpheaders();

my $graphdir = "/home/httpd/html/graphs";
&readhash("${swroot}/ethernet/settings", \%netsettings);

$ENV{'QUERY_STRING'} =~ s/&//g;
my @cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});

my %graphtitles = (
    'GREEN' => _('Green graph'),
    'BLUE' => _('Blue graph'),
    'ORANGE' => _('Orange graph'),
    'RED' => _('Red graph'),
    'cpu' => _('CPU graph'),
    'memory' => _('Memory graph'),
    'swap' => _('Swap graph'),
    'disk' => _('Disk graph')
); 


if ($cgigraphs[1] =~ /(network|GREEN|BLUE|ORANGE|RED)/) {
	&openpage(_('Network traffic graphs'), 1, '');
} else {
	&openpage(_('System graphs'), 1, '');
}
&openbigbox($errormessage, $warnmessage, $notemessage);


	
if ($cgigraphs[1] =~ /(GREEN|BLUE|ORANGE|RED|cpu|memory|swap|disk)/) {

	$graph = $cgigraphs[1];
	print "<div align='center'><table width='80%'><tr><td align='center'>";
	if ($cgigraphs[1] =~ /(GREEN|BLUE|ORANGE|RED)/) {
		print "<a href='/cgi-bin/flow.cgi?graph=network'>";
	} else {
		print "<a href='/cgi-bin/graphs.cgi'>";
	}
	print "["._('BACK')."]" ."</a></td></tr></table></div>\n";
	;
	if (-e "$graphdir/${graph}-day.png") {
		$ftime = localtime((stat("$graphdir/${graph}-day.png"))[9]);
		my $deal_date = deal_date($ftime);
		if ($cgigraphs[1] =~ /RED_(.*)/) {
			my $name = $1;
			if ($name eq "main") {
				$name = "主上行线路流量图";
			}
			else{
				$name = "上行线路$name流量图";
			}
			$graphtitles{$cgigraphs[1]} = $name;
		}
		&openbox('100%', 'center', $graphtitles{$cgigraphs[1]}."-". _('The statistics were last updated at: %s',$deal_date));
		printf <<EOF
		<center>
		<img class="graph_img"  src='/graphs/${graph}-day.png' border='0' /><hr />
		<img class="graph_img"  src='/graphs/${graph}-week.png' border='0' /><hr />
		<img class="graph_img"  src='/graphs/${graph}-month.png' border='0' /><hr />
		<img class="graph_img"  src='/graphs/${graph}-year.png' border='0' />
EOF
;
	} else {
	&openbox('100%', 'center', $graphtitles{$cgigraphs[1]});
		my $str = no_graph(_('No information available.'));
		print $str;
	}
	&closebox();
	print "<div align='center'><table width='80%'><tr><td align='center'>";
	if ($cgigraphs[1] =~ /(GREEN|BLUE|ORANGE|RED)/) {
		print "<a href='/cgi-bin/flow.cgi?graph=network'>";
	} else {
		print "<a href='/cgi-bin/graphs.cgi'>";
	}
	print _('BACK') ."</a></td></tr></table></div>\n";
	;
} elsif ($cgigraphs[1] =~ /network/) {
	push (@graphs, ('GREEN'));
	if (blue_used()) {
		push (@graphs, ('BLUE')); }
	if (orange_used()) {
		push (@graphs, ('ORANGE')); }

	$uplinks = get_uplinks();
	foreach my $ul (@$uplinks) {
	    push (@graphs, ("RED_".$ul));
	}

	foreach $graphname (@graphs) {
		if ($graphname =~ /RED_(.*)/) {
			my $uplink = $1;
			my $uplink_dis = $1;
			if ($uplink_dis eq "main") {
				$uplink_dis = "主上行线路流量图";
			}
			else{
				$uplink_dis = $uplink_dis."流量图";
			}
			if (-e "$graphdir/${graphname}-day.png") {
			$ftime = localtime((stat("$graphdir/${graphname}-day.png"))[9]);
			my $deal_date = deal_date($ftime);
			&openbox('100%', 'center', $uplink_dis."-"._('The statistics were last updated at: %s', $deal_date));
			printf <<EOF
<a href='/cgi-bin/flow.cgi?graph=$graphname'>
  <img class="graph_img" src='/graphs/${graphname}-day.png' border='0' />
</a>
EOF
;
			}else{
			&openbox('100%', 'center', $uplink_dis);
			my $str = no_graph(_('No information available.'));
		print $str;
			}
		} else {
			if (-e "$graphdir/${graphname}-day.png") {
			$ftime = localtime((stat("$graphdir/${graphname}-day.png"))[9]);
			my $deal_date = deal_date($ftime);
			&openbox('100%', 'center',$graphtitles{$graphname}."-"._('The statistics were last updated at: %s', $deal_date));
			printf <<EOF
<a href='/cgi-bin/flow.cgi?graph=$graphname'>
  <img class="graph_img" src='/graphs/${graphname}-day.png' border='0' />
</a>
EOF
;
			}else{
			&openbox('100%', 'center', $graphtitles{$graphname});
			my $str = no_graph(_('No information available.'));
		print $str;
			}
		}
		
		&closebox();
	}
} else {
	if (-e "$graphdir/cpu-day.png") {
	$ftime = localtime((stat("$graphdir/cpu-day.png"))[9]);
	my $deal_date = deal_date($ftime);
	&openbox('100%', 'center', _('CPU graph')."-"._('The statistics were last updated at: %s', $deal_date));
		
		printf <<EOF
<a href='/cgi-bin/graphs.cgi?graph=cpu'>
  <img class="graph_img" src='/graphs/cpu-day.png' border='0' />
</a>
EOF
;
	} else {
	&openbox('100%', 'center', _('CPU graph'));
	        my $str = no_graph(_('No information available.'));
		print $str;
	}
	&closebox();

	
	if (-e "$graphdir/memory-day.png") {
		$ftime = localtime((stat("$graphdir/memory-day.png"))[9]);
		my $deal_date = deal_date($ftime);
		&openbox('100%', 'center', _('Memory graph')."-"._('The statistics were last updated at: %s', $deal_date));
		printf <<EOF
<a href='/cgi-bin/graphs.cgi?graph=memory'>
  <img class="graph_img" src='/graphs/memory-day.png' border='0' />
</a>
EOF
;
	} else {
		&openbox('100%', 'center', _('Memory graph'));
	        my $str = no_graph(_('No information available.'));
		print $str;
	}
	&closebox();

	
	

	
	if (-e "$graphdir/disk-day.png") {
		
		my $ftime = localtime((stat("$graphdir/disk-day.png"))[9]);
		my $deal_date = deal_date($ftime);
		&openbox('100%', 'center', _('Disk graph')."-"._('The statistics were last updated at: %s', $deal_date));
		printf <<EOF
<a href='/cgi-bin/graphs.cgi?graph=disk'>
  <img class="graph_img" src='/graphs/disk-day.png' border='0' />
</a>
EOF
;
	} else {
	&openbox('100%', 'center', _('Disk graph'));
	        my $str = no_graph(_('No information available.'));
		print $str;
	}
	&closebox();
}

&closebigbox();
&closepage();
