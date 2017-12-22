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


// System logs start with the service name, sometimes followed by the process-id in square
// brackets and always by a ":" and the following message
type = 'system';
if (!checkRenderer(type, logFactories)) {
    logFactories[logFactories.length] = type;

    function systemRenderer(text) {
    this.getEntry = g_Entry;
    this.getExtra = function (text) { return new Array(document.createTextNode('')) };

    function g_Entry(text) {
    regexpstring = /(.*)\: (.*)/;
    result = regexpstring.exec(text);
    if (result) {
	proc = RegExp.$1;
	msg = RegExp.$2;

	systr = document.createElement('div');
	
	regexpstring = /([A-Za-z\(\)_\-]+)\[([0-9]{1,5})\]/;
	result = regexpstring.exec(text);
	if (result) {
	    proc = RegExp.$1;
	    pid = RegExp.$2;
	    pidtd = document.createElement('span');
	    pidtd.style.fontWeight = 'bold';
	    pidtd.style.color = logColors['pid'];
	    pidtd.appendChild(document.createTextNode('('+pid+') '));
	    systr.appendChild(pidtd);
	}
	proctd = document.createElement('span');
	proctd.style.fontWeight = 'bold';
	proctd.style.color = logColors['proc'];
	proctd.appendChild(document.createTextNode(proc+' '));
	if (systr.childNodes.length > 0) {
	  systr.insertBefore(proctd,systr.firstChild);
	} else {
	  systr.appendChild(proctd);
	}
	msgtd = document.createElement('span');
	msgtd.style.color = logColors['msg'];
	msgtd.appendChild(document.createTextNode(msg));
	systr.appendChild(msgtd);
	systr.style.display='inline';
	return systr;
    } else {
	return document.createTextNode(text);
    }
    } // end function
    }
}

