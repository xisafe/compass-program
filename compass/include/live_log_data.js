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

var log_colors = new Array();

log_colors["#CCFFFF"] = '#000000';
log_colors["#99FFFF"] = '#000000';
log_colors["#009999"] = '#FFFFFF';
log_colors["#006666"] = '#FFFFFF';

log_colors["#CCFFCC"] = '#000000';
log_colors["#99FF99"] = '#000000';
log_colors["#00CC00"] = '#FFFFFF';
log_colors["#009900"] = '#FFFFFF';

log_colors["#FFFFCC"] = '#000000';
log_colors["#FFCC99"] = '#000000';
log_colors["#FF9900"] = '#FFFFFF';
log_colors["#CC6600"] = '#FFFFFF';

log_colors["#FFCCCC"] = '#000000';
log_colors["#FF9999"] = '#000000';
log_colors["#FF3300"] = '#FFFFFF';
log_colors["#CC3300"] = '#FFFFFF';


var logFactories = Array();                                                                                                                                                                                                                                                         
var logColors = Array();                                                                                                                                                                                                                                                            
logColors['error'] = 'red';                                                                                                                                                                                                logColors['sid'] = '#FF6600';    
logColors['class'] = '#6699FF';                                                     
logColors['warning'] = 'orange';

logColors['middle'] = 'yellow';
                                 
				                                                                                                                                                                                                                   
logColors['proc'] = '#555555';                                                                                                                                                                                                                                                      
logColors['pid'] = '#555555';                                                                                                                                                                                                                                                       
logColors['file'] = 'darkblue';                                                                                                                                                                                                                                                     
logColors['good'] = 'green';                                                                                                                                                                                                                                                        
logColors['msg'] = 'black';                                                                                                                                                                                                                                                         


// check if Renderer exists                                                                                                                                                                                                                                                         
function checkRenderer(type) {                                                                                                                                                                                                                                                      
    for (i=0; i<logFactories.length; i++) {                                                                                                                                                                                                                                         
        if (logFactories[i] == type) {                                                                                                                                                                                                                                              
	    return true;                                                                                                                                                                                                                                                            
	}                                                                                                                                                                                                                                                                           
    }                                                                                                                                                                                                                                                                               
    return false;                                                                                                                                                                                                                                                                   
}                                                                                                                                                                                                                                                                                   
		  