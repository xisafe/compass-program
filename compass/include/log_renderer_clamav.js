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

// Clamav tells us about updates, PID files, .cvd files errors and warnings...
type = 'clamav';
if (!checkRenderer(type, logFactories)) {
    logFactories[logFactories.length] = type;

  function clamavRenderer(text) {
    this.getEntry = g_Entry;
    this.getExtra = g_Extra;

    function g_Extra(text) {
        return new Array(document.createTextNode(''));
    }

    function g_Entry(text) {
        regexpstring = /([a-zA-Z]+)\[([0-9]{1,5})\]\:(.*)/;
	result = regexpstring.exec(text);
        if (result) {
	    proc = RegExp.$1+' ';
	    pid = RegExp.$2;
    	    rest = RegExp.$3+' ';
	    clamtr = document.createElement('div');
	    proctd = document.createElement('span');
	    proctd.style.fontWeight = 'bold';
	    proctd.style.color = logColors['proc'];
	    proctd.appendChild(document.createTextNode(proc));
	    pidtd = document.createElement('span');
	    pidtd.style.fontWeight = 'bold';
	    pidtd.style.color = logColors['pid'];
	    pidtd.appendChild(document.createTextNode('('+pid+') '));
	    clamtr.appendChild(proctd);
	    clamtr.appendChild(pidtd);

	    regexpstring = /(daily\.cvd|main\.cvd|daily\.inc|main\.inc) (is up to date|updated)(.*)/;
	    result = regexpstring.exec(rest);
	    if (result) {
		file = RegExp.$1+' ';
		update = RegExp.$2+' ';
		rest = RegExp.$3+' ';
		filetd = document.createElement('span');
		filetd.style.color = logColors['file'];
		filetd.appendChild(document.createTextNode(file));
		updatetd = document.createElement('span');
		updatetd.style.color = logColors['good'];
		updatetd.appendChild(document.createTextNode(update));
		resttd = document.createElement('span');
		resttd.appendChild(document.createTextNode(rest));
		clamtr.appendChild(filetd);
		clamtr.appendChild(updatetd);
	    } else {
		regexpstring = /(ERROR|WARNING):(.*)/;
		result = regexpstring.exec(rest);
		if (result) {
		    msgtype = RegExp.$1+' ';
		    msg = RegExp.$2+' ';
		    if (msgtype == 'ERROR ') {
			color = logColors['error'];
		    } else {
			color = logColors['warning'];
		    }
		    errtd = document.createElement('span');
		    errtd.style.fontWeight = 'bold';
		    errtd.style.color = color;
		    errtd.appendChild(document.createTextNode(msgtype));
		    msgtd = document.createElement('span');
		    msgtd.style.color = color;
		    msgtd.appendChild(document.createTextNode(msg));
		    clamtr.appendChild(errtd);
		    clamtr.appendChild(msgtd);
		} else {
    		    resttd = document.createElement('span');
		    resttd.style.color = logColors['msg'];
		    resttd.appendChild(document.createTextNode(rest));
		    clamtr.appendChild(resttd);
		}
	    }
	    clamtr.style.display='inline';
	    return clamtr;
	} else {
	    return document.createTextNode(text);
	}
    }
  }
}

