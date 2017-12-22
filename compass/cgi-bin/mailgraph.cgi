#!/usr/bin/perl
#===============================================================================
#
# DESCRIPTION: SMTP邮件统计图页面
#
# AUTHOR: 周圆 (zhouyuan), 834613209@qq.com
# COMPANY: great.chinark
# CREATED: 2011/09/02-11:04
#===============================================================================

use RRDs;
use POSIX qw(uname);
require '/var/efw/header.pl';


my $VERSION = "1.12";

my $host = (POSIX::uname())[1];
my $scriptname = 'mailgraph.cgi';
my $xpoints = 540;
my $points_per_sample = 3;
my $ypoints = 160;
my $ypoints_err = 96;
my $rrd = '/var/log/rrd/mailgraph.rrd'; # path to where the RRD database is
my $rrd_virus = '/var/log/rrd/mailgraph_virus.rrd'; # path to where the Virus RRD database is
my $tmp_dir = '/tmp/mailgraph'; # temporary directory where to store the images

my @graphs = (
	{ title => _('Day graphs'),   seconds => 3600*24,        },
	{ title => _('Week graphs'),  seconds => 3600*24*7,      },
	{ title => _('Month graphs'), seconds => 3600*24*31,     },
	{ title => _('Year graphs'),  seconds => 3600*24*365, },
);

my %color = (
	sent     => '000099', # rrggbb in hex
	received => '009900',
	rejected => 'AA0000', 
	bounced  => '000000',
	virus    => 'DDBB00',
	spam     => '999999',
);

sub rrd_graph(@)
{
	my ($range, $file, $ypoints, @rrdargs) = @_;
	my $step = $range*$points_per_sample/$xpoints;
	# choose carefully the end otherwise rrd will maybe pick the wrong RRA:
	my $end  = time; $end -= $end % $step;
	my $date = localtime(time);
	$date =~ s|:|\\:|g unless $RRDs::VERSION < 1.199908;

	my ($graphret,$xs,$ys) = RRDs::graph($file,
		'--imgformat', 'PNG',
		'--width', $xpoints,
		'--height', $ypoints,
		'--start', "-$range",
		'--end', $end,
		'--vertical-label', 'msgs/min',
		'--lower-limit', 0,
		'--units-exponent', 0, # don't show milli-messages/s
		'--lazy',
		"-w 695", "-h 140",
		"--color", "SHADEA#a7e1f7",
		"--color", "SHADEB#4fb0c1",
		"--color", "BACK#f5fbfc",

		$RRDs::VERSION < 1.2002 ? () : (
			'--slope-mode'
		),

		@rrdargs,

		'COMMENT:['.$date.']\r',
	);

	my $ERR=RRDs::error;
	die "ERROR: $ERR\n" if $ERR;
}

sub graph($$)
{
	my ($range, $file) = @_;
	my $step = $range*$points_per_sample/$xpoints;
	rrd_graph($range, $file, $ypoints,
		"DEF:sent=$rrd:sent:AVERAGE",
		"DEF:msent=$rrd:sent:MAX",
		"CDEF:rsent=sent,60,*",
		"CDEF:rmsent=msent,60,*",
		"CDEF:dsent=sent,UN,0,sent,IF,$step,*",
		"CDEF:ssent=PREV,UN,dsent,PREV,IF,dsent,+",
		"AREA:rsent#$color{sent}:"._('Sent')."    ",
		'GPRINT:ssent:MAX:total\: %8.0lf msgs',
		'GPRINT:rsent:AVERAGE:avg\: %5.2lf msgs/min',
		'GPRINT:rmsent:MAX:max\: %4.0lf msgs/min\l',

		"DEF:recv=$rrd:recv:AVERAGE",
		"DEF:mrecv=$rrd:recv:MAX",
		"CDEF:rrecv=recv,60,*",
		"CDEF:rmrecv=mrecv,60,*",
		"CDEF:drecv=recv,UN,0,recv,IF,$step,*",
		"CDEF:srecv=PREV,UN,drecv,PREV,IF,drecv,+",
		"LINE2:rrecv#$color{received}:"._('Received'),
		'GPRINT:srecv:MAX:total\: %8.0lf msgs',
		'GPRINT:rrecv:AVERAGE:avg\: %5.2lf msgs/min',
		'GPRINT:rmrecv:MAX:max\: %4.0lf msgs/min\l',
	);
}

sub graph_err($$)
{
	my ($range, $file) = @_;
	my $step = $range*$points_per_sample/$xpoints;
	rrd_graph($range, $file, $ypoints_err,
		"DEF:rejected=$rrd:rejected:AVERAGE",
		"DEF:mrejected=$rrd:rejected:MAX",
		"CDEF:rrejected=rejected,60,*",
		"CDEF:drejected=rejected,UN,0,rejected,IF,$step,*",
		"CDEF:srejected=PREV,UN,drejected,PREV,IF,drejected,+",
		"CDEF:rmrejected=mrejected,60,*",
		"LINE2:rrejected#$color{rejected}:"._('Rejected'),
		'GPRINT:srejected:MAX:total\: %8.0lf msgs',
		'GPRINT:rrejected:AVERAGE:avg\: %5.2lf msgs/min',
		'GPRINT:rmrejected:MAX:max\: %4.0lf msgs/min\l',

		"DEF:bounced=$rrd:bounced:AVERAGE",
		"DEF:mbounced=$rrd:bounced:MAX",
		"CDEF:rbounced=bounced,60,*",
		"CDEF:dbounced=bounced,UN,0,bounced,IF,$step,*",
		"CDEF:sbounced=PREV,UN,dbounced,PREV,IF,dbounced,+",
		"CDEF:rmbounced=mbounced,60,*",
		"AREA:rbounced#$color{bounced}:"._('Bounced')." ",
		'GPRINT:sbounced:MAX:total\: %8.0lf msgs',
		'GPRINT:rbounced:AVERAGE:avg\: %5.2lf msgs/min',
		'GPRINT:rmbounced:MAX:max\: %4.0lf msgs/min\l',

		"DEF:virus=$rrd_virus:virus:AVERAGE",
		"DEF:mvirus=$rrd_virus:virus:MAX",
		"CDEF:rvirus=virus,60,*",
		"CDEF:dvirus=virus,UN,0,virus,IF,$step,*",
		"CDEF:svirus=PREV,UN,dvirus,PREV,IF,dvirus,+",
		"CDEF:rmvirus=mvirus,60,*",
		"STACK:rvirus#$color{virus}:"._('Viruses')." ",
		'GPRINT:svirus:MAX:total\: %8.0lf msgs',
		'GPRINT:rvirus:AVERAGE:avg\: %5.2lf msgs/min',
		'GPRINT:rmvirus:MAX:max\: %4.0lf msgs/min\l',

		"DEF:spam=$rrd_virus:spam:AVERAGE",
		"DEF:mspam=$rrd_virus:spam:MAX",
		"CDEF:rspam=spam,60,*",
		"CDEF:dspam=spam,UN,0,spam,IF,$step,*",
		"CDEF:sspam=PREV,UN,dspam,PREV,IF,dspam,+",
		"CDEF:rmspam=mspam,60,*",
		"STACK:rspam#$color{spam}:"._('Spam')."    ",
		'GPRINT:sspam:MAX:total\: %8.0lf msgs',
		'GPRINT:rspam:AVERAGE:avg\: %5.2lf msgs/min',
		'GPRINT:rmspam:MAX:max\: %4.0lf msgs/min\l',
	);
}

sub print_html()
{
	showhttpheaders();
	openpage(_('Mail statistics for: %s', $host), 1, '');
	my $error_img = no_graph(_('No information available.'));
	printf <<EOF
	<script type="text/javascript"> 
var imgErr = function(imgObj){ 
imgObj.parentNode.innerHTML = '$error_img'; 
} 
</script> 
EOF
;
        &openbigbox($errormessage, $warnmessage, $notemessage);
	for my $n (0..$#graphs) {
		openbox('100%', 'left', $graphs[$n]{title});
				printf "<div  style=\"text-align:center;\">";
                printf "<span><IMG BORDER=\"0\" SRC=\"$scriptname?${n}-n\"  onerror=\"imgErr(this);\"  /></span>\n";
                printf "<span><IMG BORDER=\"0\" SRC=\"$scriptname?${n}-e\"  onerror=\"imgErr(this);\"  /></span>";
				printf "</div>";
		closebox();
	}
	closebigbox();
	closepage();
}

sub send_image($)
{
	my ($file)= @_;

	-r $file or do {
		print "Content-type: text/plain\n\nERROR: can't find $file\n";
		exit 1;
	};

	print "Content-type: image/png\n";
	print "Content-length: ".((stat($file))[7])."\n";
	print "\n";
	open(IMG, $file) or die;
	my $data;
	print $data while read(IMG, $data, 16384)>0;
}

sub main()
{
	my $uri = $ENV{REQUEST_URI} || '';
	$uri =~ s/\/[^\/]+$//;
	$uri =~ s/\//,/g;
	$uri =~ s/(\~|\%7E)/tilde,/g;
	mkdir $tmp_dir, 0777 unless -d $tmp_dir;
	mkdir "$tmp_dir/$uri", 0777 unless -d "$tmp_dir/$uri";

	my $img = $ENV{QUERY_STRING};
	if(defined $img and $img =~ /\S/) {
		if($img =~ /^(\d+)-n$/) {
			my $file = "$tmp_dir/$uri/mailgraph_$1.png";
			graph($graphs[$1]{seconds}, $file);
			send_image($file);
		}
		elsif($img =~ /^(\d+)-e$/) {
			my $file = "$tmp_dir/$uri/mailgraph_$1_err.png";
			graph_err($graphs[$1]{seconds}, $file);
			send_image($file);
		}
		else {
			die "ERROR: invalid argument\n";
		}
	}
	else {
		print_html;
	}
}

main;
