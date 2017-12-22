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

var resObject = createXMLHTTPRequestObject();
var saveObject = createXMLHTTPRequestObject();

var logTypes = new Array("squid","firewall","snort","dansguardian","openvpn","smtp","clamav","backup","dnsmasq","dhcpd","red","ipsec");

		 
		 
var lineColors = ['#eee','#fff'];
var mouseOverColor = '#ffffcc';
var isIE = !window.opera && navigator.userAgent.indexOf('MSIE') != -1;

function get_logs() {
  resObject.open("GET","/cgi-bin/logs_live-ajax.cgi");
  resObject.onreadystatechange = showLogs;
  resObject.send(null);
}

function saveLiveLogSettings() {
  if (document.getElementById('allow_save').value == 'off') { return; }
  urlstring = 'type=logs_live';
  for (var type in logTypes) {
    chk_node = document.getElementById("livelog_"+logTypes[type]);
    col_node = document.getElementById(logTypes[type]+"_color");
    urlstring = urlstring+'&LIVE_'+logTypes[type].toUpperCase()+'=';
    if (chk_node != null && chk_node.checked != false) {
      urlstring = urlstring+'on';
    } else {
      urlstring = urlstring+'off';
    }
    urlstring = urlstring+'&'+logTypes[type].toUpperCase()+'_COLOR='+col_node.value;
  }
  hl_node = document.getElementById("hl_color");
  urlstring = urlstring+'&HIGHLIGHT_COLOR='+hl_node.value+'&AUTOSCROLL=';
  if (document.getElementById('autoscroll').checked) {
    urlstring = urlstring + 'on';
  } else {
    urlstring = urlstring + 'off';
  }
  saveObject.open("POST",'/cgi-bin/save_settings-ajax.cgi');
  saveObject.setRequestHeader('Content-Type','application/x-www-form-urlencoded');
  saveObject.send(urlstring);
}

function readStatus() {
    i = 0;
    activatedTypes = new Array();
    for (var type in logTypes) {
        chk_node = document.getElementById("livelog_"+logTypes[type]);
	if (chk_node != null && chk_node.checked != false) {
	    activatedTypes[i] = logTypes[type];
	    i++;
	}
    }
    return activatedTypes;
}

function checkReverse() {
    chk_node = document.getElementById("livelog_reverse");
    return chk_node.value;
}


function appendNode(node,log_list,reverse) {
    if (document.getElementById(node.getAttribute('id')) == null) {

	id = node.getAttribute('id');
	type = node.getAttribute('type');
	if (log_type_names[type]) {
	    log_type_name = log_type_names[type];
	} else {
	    log_type_name = type;
	}
	text = node.getAttribute('text');
	date = node.getAttribute('date');
        myRenderer = new Renderer(type);
	myRenderer.setText(text);
        myRenderer.getRenderer();
        myRenderer.doRendering();

	oouter = document.createElement('div');
	oouter.className = 'log_line';
	oouter.style.display = 'none';

        if (myRenderer.onClick) {
    	    oouter.innerHTML = "<div id='"+id+"' log_type='"+type+"' log_text='"+text+"' log_date='"+date+"'name='log_entry' class='log_maindiv' style='display: none;' "+ 
	                   "onmouseover=\"setHighlightColor('"+id+"','over')\" onmouseout=\"setHighlightColor('"+id+"','out')\" onclick=\""+myRenderer.onClick+"\"></div>";
        } else {
    	    oouter.innerHTML = "<div id='"+id+"' log_type='"+type+"' log_text='"+text+"' log_date='"+date+"'name='log_entry' class='log_maindiv' style='display: none;' "+ 
	                   "onmouseover=\"setHighlightColor('"+id+"','over')\" onmouseout=\"setHighlightColor('"+id+"','out')\"></div>";
	}


	outer = oouter.firstChild;
	outer.style.display = 'none';
    log_type_name = log_type_name.replace("red","红色接口");
	log_type_name = log_type_name.replace("ipsec","IPSEC");
	log_type_name = log_type_name.replace("openvpn","SSLVPN");
	log_type_name = log_type_name.replace("dnsmasq","DNS代理");
	log_type_name = log_type_name.replace("dhcpd","DHCP服务器");
	log_type_name = log_type_name.replace("firewall","防火墙");
	log_type_name = log_type_name.replace("snort","入侵防御");
	log_type_name = log_type_name.replace("dansguardian","内容过滤");
	log_type_name = log_type_name.replace("squid","网页代理");
	// Internet Explorer doesn't like onClick events added with DOM
	inner_h = "<div id='"+id+"_h' class='header_"+type+" log_span'>"+log_type_name+"</div>";
	inner_d = "<div id='"+id+"_d' class='date_"+type+"'><span width='100%' height='100%'>"+date+"</span></div>";

	inner_t = document.createElement('div');
	inner_t.setAttribute('id',id+'_t');
	inner_t.className = 'text_'+type;
	inner_t.appendChild(myRenderer.LogEntry);
	
	outer.innerHTML = inner_h + inner_d;
	outer.appendChild(inner_t);
	// Another Internet Explorer Hack
	if (isIE) {
	    blah = document.createElement('div');
	    blah.className = 'ie_clearer';
	    outer.appendChild(blah);
	}
        if (reverse == 'off' || reverse == '') {
	    log_list.appendChild(outer);
	    if (log_list.childNodes.length > 1000) {
	       log_list.removeChild(log_list.firstChild);
	    }
		
}else {
	    log_list.insertBefore(outer,log_list.firstChild);
	    if (log_list.childNodes.length > 1000) {
	       log_list.removeChild(log_list.lastChild);
	    }
	}
    }
}

function checkType(type,activatedTypes) {
    for (j = 0; j < activatedTypes.length; j++) {
        if (type == activatedTypes[j]) {
	    return true;
	}
    }
    return false;
}

function filterNodes(activatedTypes) {
    filterNode = document.getElementById('livelog_filter');
    filterNode2 = document.getElementById('livelog_filter_2');
    highlightNode = document.getElementById('livelog_highlight');
    defaultcolour = '#ffcc00';
    colourNode = document.getElementById('hl_color');
    if (colourNode.value != '') {
	color = colourNode.value;
    } else {
	color = defaultcolour;
    }

    nodes = document.getElementsByName('log_entry');

    if (nodes.length == 0) {
	divnodes = document.getElementsByTagName('div');
	nodes = new Array();
	i = 0;
	for (j = 0; j < divnodes.length; j++) {
	    if (divnodes[j].getAttribute('name') == 'log_entry') {
		nodes[i] = divnodes[j];
		i++;
	    }
	}
    }

    if (nodes == null || nodes.length == 0) { return; }
    mstring = new RegExp(filterNode.value,'i');
    m2string = new RegExp(filterNode2.value,'i');
    hstring = new RegExp(highlightNode.value,'i');
    x = 0;

    if (filterNode.value != '') {
	document.getElementById('livelog_filter_2').disabled = false;
    } else {
	document.getElementById('livelog_filter_2').disabled = true;
    }
    lastshown = -1;
    lasthighlighted = -1;
    for (k = 0; k < nodes.length; k++) {
	if ((mstring.test(nodes[k].getAttribute('log_text')) || mstring.test(nodes[k].getAttribute('log_date')) || filterNode.value == '') && checkType(nodes[k].getAttribute('log_type'),activatedTypes)) {
	    if (x % 2 == 0) {
	      bgcolor = lineColors[0];
	    } else {
	      bgcolor = lineColors[1];
	    }
	    if ((hstring.test(nodes[k].getAttribute('log_text')) || hstring.test(nodes[k].getAttribute('log_date'))) && highlightNode.value != '') {
		lasthighlighted = k;
	    } 
	    if (filterNode.value != '') {
	      if (m2string.test(nodes[k].getAttribute('log_text')) || m2string.test(nodes[k].getAttribute('log_date')) || filterNode2.value == '') {
	        if (!isIE) {
		  nodes[k].style.display = 'table';
		} else {
		  nodes[k].style.display = 'block';
		}
		lastshown = k;
		if (lasthighlighted == k) {
		    thiscolor = color;
		} else {
		    thiscolor = bgcolor;
		}
		nodes[k].style.backgroundColor = thiscolor;
		nodes[k].setAttribute('linecolor',thiscolor);
		type_color = document.getElementById(nodes[k].getAttribute('log_type') + '_color').value;
		if (log_colors[type_color]) {
		    type_fg = log_colors[type_color];
		} else {
		    type_fg = '#000000';
		}
		nodes[k].childNodes[0].style.backgroundColor = type_color;
		nodes[k].childNodes[0].style.color = type_fg;
		nodes[k].childNodes[1].style.backgroundColor = thiscolor;
		nodes[k].childNodes[2].style.backgroundColor = thiscolor;
		x = x + 1;
	      } else {
	        nodes[k].style.display = 'none';
	      }
	    } else {
	      if (!isIE) {
	        nodes[k].style.display = 'table';
	      } else {
	        nodes[k].style.display = 'block';
	      }
	      lastshown = k;
	      if (lasthighlighted == k) {
		thiscolor = color;
	      } else {
		thiscolor = bgcolor;
	      }
	      nodes[k].setAttribute('linecolor',thiscolor);
	      nodes[k].style.backgroundColor = thiscolor;
	      type_color = document.getElementById(nodes[k].getAttribute('log_type') + '_color').value;
	      if (log_colors[type_color]) {
	        type_fg = log_colors[type_color];
	      } else {
	        type_fg = '#000000';
	      }
	      nodes[k].childNodes[0].style.backgroundColor = type_color;
    	      nodes[k].childNodes[0].style.color = type_fg;
	      nodes[k].childNodes[1].style.backgroundColor = thiscolor;
	      nodes[k].childNodes[2].style.backgroundColor = thiscolor;
	      x = x + 1;
            }
	} else {
	    nodes[k].style.display = 'none';
	}
    }
    //if (x > 0) { document.getElementById('live_logs').style.display = 'block'; };
}

function scrollDown (reverse) {
    if ((reverse != 'off' && reverse != '') || !document.getElementById('autoscroll').checked ) { return; }
    area = document.getElementById('live_logs_div');
    if (area.offsetHeight > area.scrollHeight) { 
        area.scrollTop = 0;
    } else { 
        area.scrollTop = area.scrollHeight; 
    } 
}

function doPause () {
    button = document.getElementById('pause_button');
    button_text = button.firstChild.nodeValue;
    button.firstChild.nodeValue = button.getAttribute('alttext');
    button.setAttribute('alttext',button_text);
    paused_node = document.getElementById('paused');
    if (paused_node.value == 'true') {
	paused_node.value = 'false';
    } else {
	paused_node.value = 'true';
    }
}

function resizeLogs(xyz) {
    log_div = document.getElementById('live_logs_div');
    height = log_div.style.height;
    
    pxindex = height.indexOf('px');
    height = height.substr(0,pxindex);
    if (xyz == 'grow') {
	height = eval("parseInt(height) + 100")+'px';
	window.resizeBy(0,100);
    } else {
	if (height > 200) {
	    height = eval("parseInt(height) - 100")+'px';
	    window.resizeBy(0, -100);
	}
    }
    log_div.style.height = height;
}

function showFullOptions() {
    full = document.getElementById('fulloptions');
    linko = document.getElementById('toggle_visibility_link');
    blah = document.getElementById('optionstable');
    oldtext = linko.innerHTML;
    newtext = linko.getAttribute('alttext');
    if (full.style.display == 'none') {
	full.style.display = 'block';
	blah.style.display = 'none';
    } else {
	full.style.display = 'none';
	blah.style.display = 'inline';
    }
    linko.setAttribute('alttext',oldtext);
    linko.innerHTML = newtext;
}

function showLogs() {

  if (resObject.readyState == 4) {
    if (resObject.status == 200) {
      setTimeout('get_logs()',2000);
      log_list = document.getElementById('live_logs');
      activatedTypes = readStatus();
      reverse = checkReverse();
      supernode = resObject.responseXML.firstChild;
      nodes = resObject.responseXML.getElementsByTagName('entry');
      for (i = 0; i < nodes.length; i++) {
        appendNode(nodes[i],log_list,reverse);
      }
      if (document.getElementById('paused').value != 'true') {
        filterNodes(activatedTypes);
        scrollDown(reverse);
      }
      nodes2 = document.getElementsByName('log_entry');
      if (document.getElementById('logs_loading')) {
        loading = document.getElementById('logs_loading');
	loading.parentNode.removeChild(loading);
      }
    } else {
      //setTimeout('get_logs()',2000);
      //document.getElementById('updates').innerHTML = 'No updates...';
    }
	var height = $('#live_logs').css("height");
	  //alert(height);
	  if(height == "0px")
	  {
		$("#no_msg_table").css("display","table");
	  }else{
		$("#no_msg_table").css("display","none");
	  }
  }
}

function setHighlightColor (div_id,overout) {
    div_node = document.getElementById(div_id);
    actual_color = div_node.style_backgroundColor;
    if (overout == 'over') {
	div_node.childNodes[1].style.backgroundColor = mouseOverColor;
	div_node.childNodes[2].style.backgroundColor = mouseOverColor;
    } else {
	div_node.childNodes[1].style.backgroundColor = div_node.getAttribute('linecolor');
	div_node.childNodes[2].style.backgroundColor = div_node.getAttribute('linecolor');
    }
}

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

// This is needed for the color palette

var palette, color = '';

function setColor(c){
    palette_type_node = document.getElementById('palette_type');
    colour_node = document.getElementById(palette_type_node.value + '_color');
    if (log_colors[c]) {
	foreground = log_colors[c];
    } else {
	foreground = '#000000';
    }
    
    if (palette_type_node.value != 'hl')  {
      cell = document.getElementById('td_' + palette_type_node.value);
      cell.style.backgroundColor = c;
      cell.style.color = foreground;
      showNode = document.getElementById('show_'+palette_type_node.value);
      showNode.style.backgroundColor = c;
      showNode.style.color = foreground;
    } else {
        prevNode = document.getElementById(palette_type_node.value + '_color_preview');
        prevNode.style.background = c;
    }
    colour_node.value = c;
    saveLiveLogSettings();
}

function showPalette(type) {
    colourNode = document.getElementById(type + '_color_preview');
    palette_node = document.getElementById('palette_frame_' + type);
    palette_node.style.left = getObjX(colourNode);
    palette_node.style.top = getObjY(colourNode);
    palette_node.style.visibility = 'visible';
}

function getPaletteType() {
  if (document.getElementById('palette_type').value != 'hl') {
    return 'normal';
  } else {
    return 'hl';
  }
}

function unlockPalette() {
    document.getElementById('palette_lock').value = 'off';
}

function getObj() {
  Obj = document.getElementById('palette_frame_'+document.getElementById('palette_type').value);
  return Obj;
}

function getObjX(el){
    var left = 0;
    if(el.offsetParent){
        while(1){
            left += el.offsetLeft;
            if(!el.offsetParent)break;
            el = el.offsetParent;
        }
    }else if(el.x)left += el.x;
    return left;
}

function getObjY(el){
    var top = 0;
    if(el.offsetParent){
        while(1){
            top += el.offsetTop;
            if(!el.offsetParent)break;
            el = el.offsetParent;
        }
    }else if(el.y)top += el.y;
    return top;
}
function save_settings(id){
	$.get('/cgi-bin/save_settings-ajax.cgi',{id:id},function(data){});
	
	}
