#!/usr/bin/perl
#
# (c) 2002 Robert Wood <rob@empathymp3.co.uk>
#
# $Id: proxygraphs.cgi,v 1.2 2003/12/11 11:06:40 riddles Exp $
#

require '/var/efw/header.pl';

my %cgiparams;
my %pppsettings;
my %netsettings;
my @graphs;

&showhttpheaders();

my $dir = "/home/httpd/html/sgraph";
$cgiparams{'ACTION'} = '';
&getcgihash(\%cgiparams);
my $sgraphdir = "/home/httpd/html/sgraph";

&openpage(_('Proxy access graphs'), 1, '');

&openbigbox($errormessage, $warnmessage, $notemessage);

&openbox('100%', 'left', _('Proxy access graphs'));

if (open(IPACHTML, "$sgraphdir/index.html"))
{
$skip = 1;
	while (<IPACHTML>)
	{
		$skip = 1 if /^<HR>$/;
		if ($skip)
		{
			$skip = 0 if /<H1>/;
			next;
		}
		s/<IMG SRC=([^"'>]+)>/<img src='\/sgraph\/$1' alt='Graph' \/>/;
		s/<HR>/<hr \/>/g;
		s/<BR>/<br \/>/g;
		s/<([^>]*)>/\L<$1>\E/g;
		s/(size|align|border|color)=([^'"> ]+)/$1='$2'/g;
		print;
	}
	close(IPACHTML);
}else {
	my $str = no_graph(_('No information available.'));
	print $str;
}

&closebox();

&closebigbox();

&closepage();
