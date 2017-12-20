// JavaScript Document
// snort has lots of fields to parse...
// Most of them are hidden by default
type = 'snort';
if (!checkRenderer(type, logFactories)) {
    logFactories[logFactories.length] = type;

    function snortRenderer(text) {
        this.getEntry = g_Entry;
        this.getExtra = g_Extra;
        this.ms = 0;

        function g_Entry(text) {
			var sid,head,description,priority,protocol,classification,srcip,srcport,dstip,dstport;
			classification = "Preprocess";
            regexpstring = /snort\[(\d+)\]/;// for sid
			result0 = regexpstring.exec(text);
			head = RegExp.$1;  //content between '[' and ']' after snort;
            regexpstring1 = /\[([0-9]+\:[0-9]+\:[0-9]+)\]/;// for sid
            result = regexpstring1.exec(text);
            if (result) {
            	sid = RegExp.$1;
            	regexpstring2 = /\[([0-9]+\:[0-9]+\:[0-9]+)\] (.*) \[Priority.*/;// for description
            	var res2 = regexpstring2.exec(text);
            	description = RegExp.$2;
				regexpstring6 =/\[([0-9]+\:[0-9]+\:[0-9]+)\] (.*) \[Classification:(.*)\] \[Priority.*/  //for classification	
				var res6 = regexpstring6.exec(text);
				if(res6){
					description = RegExp.$2;
					classification = RegExp.$3;
					}
				regexpstring3 = /\[Priority\: (\d)\] \{(.*)\}/;// for priority,protocol
				var res3 = regexpstring3.exec(text);
				priority = RegExp.$1;
				protocol = RegExp.$2;
				if (protocol == "PROTO:255"){protocol = RESERVE	;}
				var priArray=['超高','高','中','低'];
				priority = priArray[priority];
				regexpstring4 =/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\:([0-9]{1,6}) \-\> ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\:(.*)/  //for ip and port if port exist
				var res4 = regexpstring4.exec(text);
				if(res4){
					srcip = RegExp.$1;
					srcport = RegExp.$2;
					dstip = RegExp.$3;
					dstport = RegExp.$4;
					}
				regexpstring5 =/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}) \-\> ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/  //for ip if port not exist
				var res5 = regexpstring5.exec(text);
				if(res5){
					srcip = RegExp.$1;
					dstip = RegExp.$2;
					}
            	firediv = document.createElement('div');
            	headspan = document.createElement('span');
            	headspan.style.fontWeight = 'bold';
            	headspan.style.color = logColors['proc'];
            	headspan.appendChild(document.createTextNode("snort[" +head+"]: " ));
				sidspan = document.createElement('span');
				sidspan.style.color = logColors['sid'];
				sidspan.appendChild(document.createTextNode("["+sid+"]"));
            	descriptionspan = document.createElement('span');
				descriptionspan.style.color = logColors['pid'];
				descriptionspan.appendChild(document.createTextNode(" "+description+" "));
				classificationspan = document.createElement('span');
				classificationspan.style.color = logColors['class'];
				classificationspan.appendChild(document.createTextNode(" [类别："+classification +"] "));
				priorityspan = document.createElement('span');
				priorityspan.style.fontWeight = 'bold';
				if(priority == "超高"){priorityspan.style.color = logColors['error'];}
				if(priority == "高"){priorityspan.style.color = logColors['error'];}
				if(priority == "中"){priorityspan.style.color = logColors['middle'];}
				if(priority == "低"){priorityspan.style.color = logColors['good'];}
				priorityspan.appendChild(document.createTextNode(" 危险级："+priority+" "));
				protocolspan = document.createElement('span');
				protocolspan.style.color = logColors['warning'];
				protocolspan.appendChild(document.createTextNode(" "+protocol+" "));
				srcipspan = document.createElement('span');
				srcipspan.style.color = logColors['file'];
				srcipspan.style.fontWeight = 'bold';
				srcipspan.appendChild(document.createTextNode(" "+srcip));
				srcportspan = document.createElement('span');
				srcportspan.style.color = logColors['good'];
				srcportspan.style.fontWeight = 'bold';
				srcportspan.appendChild(document.createTextNode(":"+srcport));
				dstipspan = document.createElement('span');
				dstipspan.style.color = logColors['file'];
				dstipspan.style.fontWeight = 'bold';
				dstipspan.appendChild(document.createTextNode(dstip));
				dstportspan = document.createElement('span');
				dstportspan.style.color = logColors['good'];
				dstportspan.style.fontWeight = 'bold';
				dstportspan.appendChild(document.createTextNode(":"+dstport));
				forwardspan = document.createElement('span');
				forwardspan.style.color = logColors['pid'];
				forwardspan.appendChild(document.createTextNode(" -> "));
				firediv.appendChild(sidspan);
            	firediv.appendChild(descriptionspan);
				firediv.appendChild(classificationspan);
            	firediv.appendChild(priorityspan);
				firediv.appendChild(protocolspan);
				firediv.appendChild(srcipspan);
				if(srcport){firediv.appendChild(srcportspan);}
				firediv.appendChild(forwardspan);
            	firediv.appendChild(dstipspan);
				if(dstport){firediv.appendChild(dstportspan);}
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

