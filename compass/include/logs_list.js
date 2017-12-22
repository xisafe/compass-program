/*                                                                                                                                                                                                                               
#                                                                                                                                                                                                                                
#        +-----------------------------------------------------------------------------+                                                                                                                                         
#        | Endian Firewall                                                             |                                                                                                                                         
#        +-----------------------------------------------------------------------------+                                                                                                                                         
#        | Copyright (c) 2006 Endian                                                   |                                                                                                                                         
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
*/                                                                                                                                                                                                                               


function selectAllLogs() {                                                                                                                                                                                                       
    mynode = document.getElementById('select_all');                                                                                                                                                                              
    nodes = document.getElementsByTagName('input');                                                                                                                                                                              
    if (mynode.checked) {                                                                                                                                                                                                        
        for (i=0;i<nodes.length;i++) {                                                                                                                                                                                           
            nodes[i].checked = 'checked';                                                                                                                                                                                        
        }                                                                                                                                                                                                                        
    } else {                                                                                                                                                                                                                     
        for (i=0;i<nodes.length;i++) {                                                                                                                                                                                           
            nodes[i].checked = null;                                                                                                                                                                                             
        }                                                                                                                                                                                                                        
    }                                                                                                                                                                                                                            
}

function showSelectedLogs() {
    linkstring = '/cgi-bin/logs_live.cgi?show=single';
    count = 0;
    nodes = document.getElementsByTagName('input');
    for (i=0;i<nodes.length;i++) {
	if (nodes[i].getAttribute('id') != 'select_all' && nodes[i].checked) {
	    if (count == 0) {
		linkstring = linkstring + '&showfields='+nodes[i].getAttribute('id');
	    } else {
		linkstring = linkstring + ','+nodes[i].getAttribute('id');
	    }
	    count++;
	}
    }
    
    if (count > 4) {
      wheight = 700 + (count - 4) * 10;
    } else {
      wheight = 700;
    }
        
    if (count > 0) {
	window.open(linkstring,'_blank','height='+wheight+',width=1000,location=no,menubar=no,scrollbars=yes');
    }
}