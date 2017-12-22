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

// Our default renderer
function defaultRenderer(text) {
    this.getEntry = g_Entry;
    this.getExtra = g_Extra;
    
    function g_Entry(text) {
        return document.createTextNode(text);
    }
    
    function g_Extra(text) {
	return new Array(document.createTextNode(''));
    }
    
}

// Our Renderer class
function Renderer(type) {

    this.Renderer = null;
    this.Extra = null;
    this.Type = type;
    this.LogEntry = document.createTextNode('');
    this.LogExtra = document.createTextNode('');
    this.getRenderer = getRenderer;
    this.doRendering = doRendering;
    this.setText = s_Text;
    this.onClick = null;

    function s_Text(text) {
	this.Text = text;
    }

    function getRenderer() {
	if (checkRenderer(this.Type)) {
	    eval("this.Renderer = new "+this.Type+"Renderer('"+this.Text+"');");
	} else {
	    this.Renderer = new defaultRenderer(this.Text);
	}
    }
    
    function doRendering() {
	this.LogEntry = this.Renderer.getEntry(this.Text);
	LogExtra = this.Renderer.getExtra(this.Text);
	this.LogExtra = LogExtra[0];
	if (LogExtra.length == 2) {
	    this.onClick = LogExtra[1];
	}
    }
    
}
