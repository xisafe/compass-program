#!/usr/bin/perl
#
#author:zhouyuan
#
#date:2011-08-02

require '/var/efw/header.pl';
my %par;
my $host_str = "";

#存放host号
my $uuid_conf = "/etc/uuid";

#sub read_host()
#{
#	open (FILE, "<$uuid_conf");
#	 foreach my $line (<FILE>) {
#        chomp($line);
#        $line =~ s/[\r\n]//g;
#		$host_str = $line;
#	}
#    close (FILE);
#}
$host_str = `sudo cat /etc/uuid`;
sub show_image()
{

	
	&openbox('100%','left',_('Hour graphs'));
	my $temp_hour = 'Hour graphs';
printf <<EOF
<img  class="graph_img"  src="/cgi-bin/collection.cgi?action=show_graph;plugin=conntrack;type=conntrack;timespan=hour;host=$host_str;ini_title=$temp_hour;" onerror=\"imgErr(this);\"   />	
EOF
,_('Hour graphs')
;
		&closebox();
	&openbox('100%','left',_('Day graphs'));
	my $temp_day = 'Day graphs';
	printf <<EOF
<img  class="graph_img"  src="/cgi-bin/collection.cgi?action=show_graph;plugin=conntrack;type=conntrack;timespan=day;host=$host_str;ini_title=$temp_day;" onerror=\"imgErr(this);\"   />	
EOF
,_('Day graphs')
;

	
	&closebox();
	
	
	
	&openbox('100%','left',_('Week graphs'));
	my $temp_week = 'Week graphs';
	printf <<EOF
<img   class="graph_img"  src="/cgi-bin/collection.cgi?action=show_graph;plugin=conntrack;type=conntrack;timespan=week;host=$host_str;ini_title=$temp_week;" onerror=\"imgErr(this);\"   />	
EOF
,_('Week graphs')
;
	&closebox();
	
		&openbox('100%','left',_('Month graphs'));
		my $temp_month = 'Month graphs';
	printf <<EOF
<img  class="graph_img" src="/cgi-bin/collection.cgi?action=show_graph;plugin=conntrack;type=conntrack;timespan=month;host=$host_str;ini_title=$temp_month;" onerror=\"imgErr(this);\"   />
EOF
,_('Month graphs')
;
	&closebox();
	
	
}

&getcgihash(\%par);
&showhttpheaders();
&openpage(_('history connects'), 1, '<script language="javascript" src="/include/connections_history.js"></script>');
my $error_img = "无可用信息";
my $no_tr = no_graph($error_img);
printf <<EOF
	<script type="text/javascript"> 
var imgErr = function(imgObj){ 
imgObj.parentNode.innerHTML = '$no_tr';
} 
</script> 
EOF
;
&show_image();
&closepage();
