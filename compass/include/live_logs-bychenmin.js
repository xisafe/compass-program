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

var logTypes = new Array("squid","firewall","snort","dansguardian","openvpn","system","smtp","clamav","httpd");
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
	//###chenmin 
	if( type == 'snort'){
	if (log_type_names[type]) {
	    log_type_name = log_type_names[type];
	} else {
	    log_type_name = type;
	}
	text = node.getAttribute('text');
	date = node.getAttribute('date');

	//###chenmin {
	var sid;
	var action;
	var description;
	var priority;
	var protocol;
	var srcip;
	var srcport;
	var destip;
	var destport;
	var srcMAC='00:19:21:4A:7E:AB';
	var destMAC='08:00:27:00:58:44';
	
	var priArray=['超高','高','中','低'];
	var priColor=['orangered','red','orange','green'];
	var Zhcn={'alert':'报警','warning':'全局预警','drop':'阻断','mail':'发送邮件','firewall':'联动防火墙','switcher':'联动交换机','soc':'联动安全管理中心'};
	var color;
	
	regexpstring1 = /\[([0-9]+)\:([0-9]+)\:[0-9]+\]/;// for sid
	regexpstring2 = /\] ([a-zA-Z]+) ([\d\D]+) \{/;// for action,description
	regexpstring3 = /(\[Priority\: (\d)\]\:)? \{([a-zA-Z]+)\}/;// for priority,protocol
	//regexpstring4 = /([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\:([0-9]{1,6}) \-\> ([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\:([0-9]{1,6})/;// for src,dest
	//regexpstring5 = /([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3}) \-\> ([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})/;
	
	//for ip port mac
	regexpstring6 = /(\[([0-9A-Fa-f]{2}\:){5}[0-9A-Fa-f]{2}\] )?(([0-9]{1,3}\.){3}[0-9]{1,3}(\:[0-9]{1,6})?) \-\> (\[([0-9A-Fa-f]{2}\:){5}[0-9A-Fa-f]{2}\] )?(([0-9]{1,3}\.){3}[0-9]{1,3}(\:[0-9]{1,6})?)/;
	
	result1 = regexpstring1.exec(text);
	if(result1)
	{	
	    if(RegExp.$1 == 1){
			sid = RegExp.$2;
		}
		else{
			sid = RegExp.$1+":"+RegExp.$2;
		}
	}
	
	result2 = regexpstring2.exec(text);
	if(result2)
	{
	    action = RegExp.$1;
		action = action.toLowerCase();
		action = Zhcn[action];
		description = RegExp.$2;
		description = description.replace(/\[Classification: ([\d\D]+)\]/g,'');
		description = description.replace(/\[Priority: \d+\]\:/g,'');
		description = description.replace(/:/g,'');
	}
	
	result3 = regexpstring3.exec(text);
	if(result3)
	{
		index = Number(RegExp.$2);
		//if(index == ''){
		//	index = 2;
		//}
	    priority = priArray[index];
		color = priColor[index];
		protocol = RegExp.$3;
	}
	/*
	result4 = regexpstring4.exec(text);
	if(result4)
	{
	    srcip = RegExp.$1 + "." + RegExp.$2 + "." + RegExp.$3 + "." + RegExp.$4;
	    srcport = ":"+RegExp.$5;
	    destip = RegExp.$6 + "." +RegExp.$7 + "." + RegExp.$8 + "." + RegExp.$9;
		
		//RegExp.lastParen表示RegExp.$10, 是否因为javascript只能支持$1~$9 ？
	    destport = ":"+RegExp.lastParen;
		
	}
	else{
		result5 = regexpstring5.exec(text);
		if(result5)
		{
			srcip = RegExp.$1 + "." + RegExp.$2 + "." + RegExp.$3 + "." + RegExp.$4;
			destip = RegExp.$5 + "." +RegExp.$6 + "." + RegExp.$7 + "." + RegExp.$8;
			srcport = "";
			destport = "";
		}
	}
	*/
	result6 = regexpstring6.exec(text);
	if(result6)
	{
		srcMAC = RegExp.$1;
		destMAC = RegExp.$6;
		srcip = RegExp.$3;
		destip = RegExp.$8;
		srcMAC = srcMAC.replace(/\[|\]/g,'');
		destMAC = destMAC.replace(/\[|\]/g,'');
	}
	
	//创建10个<td>
	datenode = document.createElement('td');
	sidnode = document.createElement('td');
	actionnode = document.createElement('td');
	descriptionnode = document.createElement('td');
	prioritynode = document.createElement('td');
	protocolnode = document.createElement('td');
	srcnode = document.createElement('td');
	destnode = document.createElement('td');
	srcMACnode = document.createElement('td');
	destMACnode = document.createElement('td');
	
	//为每个<td>填入文本内容
	datenode.appendChild(document.createTextNode(date));
	sidnode.appendChild(document.createTextNode(sid));
	actionnode.appendChild(document.createTextNode(action));
	descriptionnode.appendChild(document.createTextNode(description));
	prioritynode.appendChild(document.createTextNode(priority));
	protocolnode.appendChild(document.createTextNode(protocol));
	//srcnode.appendChild(document.createTextNode(srcip+srcport));//change
	//destnode.appendChild(document.createTextNode(destip+destport));//change
	srcnode.appendChild(document.createTextNode(srcip));
	destnode.appendChild(document.createTextNode(destip));
	srcMACnode.appendChild(document.createTextNode(srcMAC));
	destMACnode.appendChild(document.createTextNode(destMAC));
	
	if (log_list.childNodes.length > 1000) {
	       log_list.removeChild(log_list.firstChild);
	}
	//向<table>中插入<tr>
	outer = log_list.insertRow(log_list.rows.length);
	
	/*设置<tr>属性：name,id,width,display 
	新建属性：log_type,log_date,log_text
	设置事件函数：onmouseover,onmouseout
	*/
	outer.setAttribute('name','log_entry');
	outer.setAttribute('id',id);
	outer.setAttribute('log_type',type);
	outer.setAttribute('log_date',date);
	outer.setAttribute('log_text',text);
	outer.setAttribute('style','display:none;');
	outer.setAttribute('onmouseover',"setHighlightColor('"+id+"','over')");
	outer.setAttribute('onmouseout',"setHighlightColor('"+id+"','out')");
	outer.setAttribute('width','100%');
	
	//把每个<td>依次加入到<tr>中
	outer.appendChild(datenode);
	outer.appendChild(sidnode);
	outer.appendChild(actionnode);
	outer.appendChild(prioritynode);
	outer.appendChild(protocolnode);
	outer.appendChild(srcnode);
	outer.appendChild(destnode);
	outer.appendChild(srcMACnode);
	outer.appendChild(destMACnode);
	outer.appendChild(descriptionnode);
	
	//设置<td>宽度,颜色
	outer.childNodes[0].setAttribute('width','12%');
	outer.childNodes[1].setAttribute('width','6%');
	outer.childNodes[2].setAttribute('width','8%');
	outer.childNodes[3].setAttribute('width','6%');
	outer.childNodes[4].setAttribute('width','5%');
	outer.childNodes[5].setAttribute('width','12%');
	outer.childNodes[6].setAttribute('width','12%');
	outer.childNodes[7].setAttribute('width','11%');
	outer.childNodes[8].setAttribute('width','11%');
	outer.childNodes[3].setAttribute('style',"color:"+color);
	//###chenmin }
	}//end if (type==snort)
    }//end if null
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
	//###chenmin{
	divnodes = document.getElementsByTagName('tr');
	//###chenmin}
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
		  nodes[k].style.display = 'table-row';
		} else {
		  nodes[k].style.display = 'table-row';
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
		//###chenmin {
		nodes[k].style.backgroundColor = thiscolor;
		nodes[k].style.color = type_fg;
		//nodes[k].childNodes[0].style.backgroundColor = type_color;
		//nodes[k].childNodes[0].style.color = type_fg;
		//nodes[k].childNodes[1].style.backgroundColor = thiscolor;
		//###chenmin }
		varlogtype = nodes[k].getAttribute('log_type');
		if(ips_threads == 0)
		{
			//###chenmin {
			//nodes[k].childNodes[2].style.backgroundColor = thiscolor;
			//###chenmin }
		}
		x = x + 1;
	      } else {
	        nodes[k].style.display = 'none';
	      }
	    } else {
		//###chenmin {
	      //if (!isIE) {
	      //  nodes[k].style.display = 'table';
	      //} else {
	      //  nodes[k].style.display = 'block';
	      //}
		//###chenmin }
		  nodes[k].style.display = 'table-row';
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
		  //###chenmin {
		  nodes[k].style.backgroundColor = thiscolor;
		  nodes[k].style.color = type_fg;
	      //nodes[k].childNodes[0].style.backgroundColor = type_color;
    	  //    nodes[k].childNodes[0].style.color = type_fg;
	      //nodes[k].childNodes[1].style.backgroundColor = thiscolor;
		  //###chenmin }
		  if(ips_threads == 0)
		  {
			//###chenmin {
	          //nodes[k].childNodes[2].style.backgroundColor = thiscolor;
			//###chenmin }
			  nodes[k].style.backgroundColor = thiscolor;
		  }
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
      log_list = document.getElementById('live_logs_table');
      activatedTypes = readStatus();
      reverse = checkReverse();
      supernode = resObject.responseXML.firstChild;
      nodes = resObject.responseXML.getElementsByTagName('entry');
      for (i = 0; i < nodes.length; i++) {
		if(nodes[i]){
        appendNode(nodes[i],log_list,reverse);
		}
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
  }
}

function setHighlightColor (div_id,overout) {
    div_node = document.getElementById(div_id);
    actual_color = div_node.style_backgroundColor;
    if (overout == 'over') {
	div_node.style.backgroundColor = mouseOverColor;
		//if(ips_threads == 0)
		//{
		//	div_node.childNodes[2].style.backgroundColor = mouseOverColor;
		//}
    } else {
	div_node.style.backgroundColor = div_node.getAttribute('linecolor');
	/*
		if(ips_threads == 0)
		{
			div_node.childNodes[2].style.backgroundColor = div_node.getAttribute('linecolor');
		}
	*/
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

