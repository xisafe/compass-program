#!/usr/bin/perl

#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
#        |         Endian GmbH/Srl                                                     |
#        |         Bergweg 41 Via Monte                                                |
#        |         39057 Eppan/Appiano                                                 |
#        |         ITALIEN/ITALIA                                                      |
#        |         info@endian.it                                                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        | http://www.fsf.org/                                                         |
#        +-----------------------------------------------------------------------------+
#

require '/var/efw/header.pl';
&showhttpheaders();
&getcgihash( \%par );

sub print_html()
{
	openpage(_('Mail queue'), 1, '');
	#openbox('100%','left', _('Mail queue'));

	open(QUEUE, '/usr/sbin/postqueue -p |');
        @lines = <QUEUE>;
        close(QUEUE);

	print '<br />';
	print ' <table class="ruleslist" cellpadding="0" cellspacing="0" width="100%"><tr>';
	print '<td  class="boldbase" width="10%">'._('Queue ID').'</td>';
	print '<td  class="boldbase" width="10%">'._('Size').'</td>';
	print '<td  class="boldbase" width="15%">'._('Arrival Time').'</td>';
	print '<td  class="boldbase" width="35%">'._('Sender').'</td>';
	print '<td  class="boldbase" width="30%">'._('Recipient').'</td></tr>';
	my $length = @lines;
	

		print '</table><div style="width:96%;margin:0px auto;max-height:400px;overflow-y:auto;border-left:1px solid #999;"><table cellpadding="0" cellspacing="0">';
		my @temp_array;
		my $j = 0;
		for(my $i =1;$i<$length;$i++)
		{
			if($lines[$i] =~ /^([A-Za-z0-9]+) +([0-9]+) +([A-Za-z]+ +[A-Za-z]+ +[0-9]+ +[0-9]+\:[0-9]+\:[0-9]+) +(.*)$/)
			{
				push(@temp_array,$i);	
			}
		}
		
		push(@temp_array,$length);
		@temp_array = reverse(@temp_array);
		
		my $note_length = @temp_array;
		my $fifty_note = "";#当邮件超过50条时显示的信息
		my $bytes_count ="";
	if(!@lines)
	{
		no_tr(5, _('The SMTP proxy is currently disabled.')._('Therefore no information is available.'));
	}elsif($note_length >1)
	{
		if($note_length >50)
		{
			$fifty_note = _('display the last 50');
		}
		
		for(my $i=$length;$i>=0;$i--)
		{
			if($j<50)
			{
			if($lines[$i] =~ /^([A-Za-z0-9]+) +([0-9]+) +([A-Za-z]+ +[A-Za-z]+ +[0-9]+ +[0-9]+\:[0-9]+\:[0-9]+) +(.*)$/)
			{
				my $recover_str= "";
				my $send_str = "";
				for(my $k =$i+2;$k<$temp_array[$j];$k++)
				{
					if($lines[$k]  !~ /\-\-.*/)
					{
						$recover_str .= "<li><b>".$lines[$k]."</b></li>";
					}else{
						
						$bytes_count = $lines[$k];
						$bytes_count =~ s/\-\-//g;
						
					}
				}
				
				$send_str .= "<li><span class='error'>"._('error').":</span>".$lines[$i+1]."</li>";
				
				print "<tr class='odd_thin'><td width='10%'>".$1."</td><td width='10%'>".$2."</td><td width='15%' >".$3."</td><td width='35%'><ul><li><b>".$4."</b></li>".$send_str."</ul></td><td width='30%'><ul>".$recover_str."</td></tr>";
				$j++;
				
			}
			}
		}
		print "</table>";
	}else {
		no_tr(5, _('Current no content'));
		print "</table>";
	}
	printf <<EOF
	
		<table  cellpadding="0" cellspacing="0" >
		<tr class="table-footer">
		<td><span style="display:block;float:left;">$bytes_count  $fifty_note</span> <form method='post'  action='$ENV{'SCRIPT_NAME'}'>
		<input type='hidden' name='ACTION' value="flush" />
		<input class='submitbutton net_button' type='submit' name='submit' value="%s" />
		</form>
		</td>
		</table></div>
EOF
,_('Flush mail queue')
;
	#closebox();
	closepage();
}

if ( $par{ACTION} eq 'flush' ) {
    my $clear =`sudo postsuper -d ALL`;
}
print_html;



