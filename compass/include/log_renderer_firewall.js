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


// IPtables has lots of fields to parse...
// Most of them are hidden by default
type = 'firewall';
if (!checkRenderer(type, logFactories)) {
    logFactories[logFactories.length] = type;

    function firewallRenderer(text) {
        this.getEntry = g_Entry;
        this.getExtra = g_Extra;
        this.ms = 0;

        function g_Entry(text) {

            regexpstring = /.*\]\:\s+(\S+)\s+IN=([a-z0-9]*)\S*\s+OUT=([a-z0-9]*)\S*\s+MAC=([a-f:0-9]*)\s+SRC=([0-9\.]+)\s+DST=([0-9\.]+)\s+.*/;
            result = regexpstring.exec(text);
            if (result) {
            	chain = RegExp.$1;
            	ifin = RegExp.$2;
            	ifout = RegExp.$3;
            	mac1 = RegExp.$4;
            	src = RegExp.$5;
            	dst = RegExp.$6;
            	regexpstring = /.*DST=[0-9\.]+\s+(.*)\s+PROTO=([A-Z]+)\s+SPT=([0-9]{1,5})\s+DPT=([0-9]{1,5})\s+(.*)/;
            	regexpstring.exec(text);
            	rest1 = RegExp.$1;
		proto = RegExp.$2;
		spt = RegExp.$3;
		dpt = RegExp.$4;
		rest2 = RegExp.$5;
		chain = chain.replace("?","");
            	firediv = document.createElement('div');
            	chainspan = document.createElement('span');
            	chainspan.style.fontWeight = 'bold';
            	chainspan.style.color = logColors['proc'];
            	chainspan.appendChild(document.createTextNode(chain));
		protospan = document.createElement('span');
		protospan.style.fontWeight = 'bold';
		protospan.style.color = logColors['warning'];
		protospan.appendChild(document.createTextNode(" "+proto+" "));
            	ifinspan = document.createElement('span');
                if (ifin != '') {
              	  ifinspan.style.color = logColors['pid'];
            	  ifinspan.style.fontWeight = 'bold';
            	  ifinspan.appendChild(document.createTextNode(' ('+ifin+') '));
                } else {
                  ifinspan.appendChild(document.createTextNode(''));
                }
            	ifoutspan = document.createElement('span');
                if (ifout != '') {
            	  ifoutspan.style.color = logColors['pid'];
            	  ifoutspan.style.fontWeight = 'bold';
            	  ifoutspan.appendChild(document.createTextNode(' ('+ifout+') '));
                } else {
                  ifoutspan.appendChild(document.createTextNode(''));
                }
            	srcspan = document.createElement('span');
            	srcspan.style.fontWeight = 'bold';
            	srcspan.style.color = logColors['file'];
            	srcspan.appendChild(document.createTextNode(src+':'));
		sptspan = document.createElement('span');
		sptspan.style.fontWeight = 'bold';
		sptspan.style.color = logColors['good'];
		sptspan.appendChild(document.createTextNode(spt));
            	aspan = document.createElement('span');
            	aspan.style.fontWeight = 'bold';
            	aspan.style.color = logColors['file'];
            	aspan.appendChild(document.createTextNode(' -> '));
            	dstspan = document.createElement('span');
            	dstspan.style.fontWeight = 'bold';
            	dstspan.style.color = logColors['file'];
            	dstspan.appendChild(document.createTextNode(dst+':'));
		dptspan = document.createElement('span');
		dptspan.style.fontWeight = 'bold';
		dptspan.style.color = logColors['good'];
		dptspan.appendChild(document.createTextNode(dpt));
		now = new Date();
		this.ms = now.getTime();
            	restspan = document.createElement('span');
            	restspan.setAttribute('id','rest_'+this.ms);
            	restspan.style.color = logColors['pid'];
            	restspan.appendChild(document.createTextNode('MAC='+mac1+' '+rest1 + ' ' + rest2));
            	restspan.style.display = 'none';
		imge = document.createElement('img');
		imge.src = '/images/expand.gif';
		imge.border = '0';
		imge.alt = '+';
		imge.setAttribute('id','img_'+this.ms);
            	firediv.appendChild(chainspan);
		firediv.appendChild(protospan);
            	firediv.appendChild(ifinspan);
            	firediv.appendChild(srcspan);
		firediv.appendChild(sptspan);
		firediv.appendChild(aspan);
            	firediv.appendChild(dstspan);
		firediv.appendChild(dptspan);
            	firediv.appendChild(ifoutspan);
		firediv.appendChild(imge);
            	firediv.appendChild(restspan);
		firediv.style.display = 'inline';
            	return firediv;
            } else {
                return document.createTextNode(text);
            }
        } //end function
        
        function g_Extra(text) {
            if (this.ms > 0) {
		linko = document.createElement('a');
		linko.href='#';
		// Internet Explorer is gentle enough not to work with valid DOM...
		linko.innerHTML = "<img src='/images/expand.gif' alt='+' border='0' id='button_"+this.ms+"' onclick=\"showFullFirewallLog('"+this.ms+"');\" />";
            	return new Array(linko,"showFullFirewallLog('"+this.ms+"');");
            } else {
                return new Array(document.createTextNode(''));
            }
        }
    
    }// end class
    var firewall_positions = new Array();

}

function showFullFirewallLog(ms) {
    rest = document.getElementById('rest_'+ms);
    imge = document.getElementById('img_'+ms);
    if (!firewall_positions[ms]) {
	firewall_positions[ms] = true;
        rest.style.display = 'block';
	imge.src = '/images/collapse.gif';
	imge.alt = '-';
    } else {
	firewall_positions[ms] = null;
        rest.style.display = 'none';
	imge.src = '/images/expand.gif';
	imge.alt = '+';
    }
}

