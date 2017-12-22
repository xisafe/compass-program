//author:zhouyuan
//Date:2012-03-09
//function:用于hirel.cgi页面的js控制
var switcher_interface = new Array();
var interface_num = 0;
var switcher_value = "";
var state= '/var/efw/risk/physic/state'; 
window.onload = function()
{
	if(document.getElementById("node_type"))
	{
		document.getElementById("node_type").onchange = function()
		{
			if(this.value == 'host')
			{
				document.getElementById("IP").style.display = document.all ? "block":"table-row";
				document.getElementById("UP_NODE").style.display = document.all ? "block":"table-row";
				document.getElementById("IP_MASK").style.display = "none";
				document.getElementById("S_SUB").style.display = "none";
			}else if(this.value == 'router'){
				document.getElementById("IP_MASK").style.display  = document.all ? "block":"table-row";
				document.getElementById("IP").style.display = "none";
				document.getElementById("S_SUB").style.display = "none";
				document.getElementById("UP_NODE").style.display = "none";
			}else if(this.value == 'switcher'){
				document.getElementById("UP_NODE").style.display = document.all ? "block":"table-row";
				document.getElementById("S_SUB").style.display  = document.all ? "block":"table-row";
				document.getElementById("IP").style.display = "none";
				document.getElementById("IP_MASK").style.display = "none";
			}
		}
	}
	count_content_height();
	draw();
	window.setInterval(check_state,3000);
}

function refresh(href,id,type)
{
	var values = document.getElementById(id).value;
	var type = document.getElementById(type).value;
	location.href = href+"?action=add_"+type+"&&line="+values;
}

function count_content_height()
{
	 var content_height =(document.documentElement.clientHeight||window.innerHeight)-70;
	 var content_width  =(document.documentElement.clientWidth||window.innerWidth)*0.9-170;
	 $(".tree").css("height",content_height+"px");
	 $(".right_risk").css("height", (content_height-95)/2+"px");
}

function check_state()
{
	jQuery.getJSON('/cgi-bin/get_json.cgi',{path:state,type:"text"}, function(datas){
		alert(datas);
		var r=/^running/;
		if(!r.test(datas))
		{
			location.href = location.href;
		}
	});
}

function hide()
{
	document.getElementById("pop-divs").style.display ="none";
	document.getElementById("add_div").style.display ="none";
}

function add_if(evt)
{
	var ul = document.getElementById("INTERFACE").childNodes;
	var index = 1;
	for(var i = 0;i<ul.length;i++)
	{
		if(ul[i].nodeName == "LI")
		{
			index++;
		}
	}
	var li = document.createElement("LI");
	var txt = document.createTextNode("接口 IP/mask： ");
	var textarea = document.createElement("textarea");
		textarea.style.width = 200;
		textarea.style.height = 40;
		textarea.name = "IP_MASK";
	var span = document.createElement("span");
	span.innerHTML = "<a href='#' onclick='rm_if(event)' >【删除接口】</a>";
	
	li.appendChild(txt);
	li.appendChild(textarea);
	li.appendChild(span);
	
	document.getElementById("INTERFACE").appendChild(li);
}

function rm_if(evt)
{
	evt = evt|| window.event;
	var selected = evt.target||evt.srcElement;
	document.getElementById("INTERFACE").removeChild(selected.parentNode.parentNode);
}

function rm_s_if(evt)
{
	if(confirm("确定要将此接口下的此节点移除？"))
	{
		evt = evt|| window.event;
		var selected = evt.target||evt.srcElement;
		var value = selected.parentNode.value;
		var text = selected.innerHTML;
		var parents = selected.parentNode.parentNode;
		selected.parentNode.parentNode.removeChild(selected.parentNode);//移除当前li
	
		var length = 0;
		for(var i = 0;i<parents.childNodes.length;i++)
		{
			if(parents.childNodes[i].tagName == "LI")
			{
				length++;
			}
		}
		if(!length)
		{
			parents.parentNode.removeChild(parents);
		}
		var option = document.createElement("option");
		option.value = value;
		option.text = text;
		document.getElementById("switcher_child").appendChild(option);
	}
}

function check_form()
{
	remove_error_node();
	if(document.getElementById("node_type"))
	{
	var type = document.getElementById("node_type").value;
	if(type == "host")
	{
		var ip = document.getElementById("host_ip").value;
		if(!ip)
		{
			get_error_node("主机IP为空！",document.getElementById("host_ip").parentNode);
		}else if(!valid_ip(ip))
		{
			get_error_node("主机IP格式不正确！",document.getElementById("host_ip").parentNode);
		}
		
	}else if(type == "router")
	{
		var ul = document.getElementById("INTERFACE").childNodes;
		for(var i = 0;i<ul.length;i++)
		{
			if(ul[i].nodeName == "LI")
			{
				var li = ul[i].childNodes;
				for(var j = 0;j<li.length;j++)
				{
					if(li[j].nodeName == "TEXTAREA")
					{
						var value = li[j].value;
						var ip_ary = value.split("\n");
						var key = 0;
						for(var z = 0;z<ip_ary.length;z++)
						{
							if(!valid_mask(ip_ary[z]))key = 1;
						}
						if(key)
						{
							get_error_node("此接口IP填写有误！",ul[i]);
						}
					}
				}
			}
		}
	}else{
		var s_child = document.getElementById("switcher_if").childNodes;
		var length = 0;
		for(var i = 0;i<s_child.length;i++)
		{
			if(s_child[i].tagName == "LI")
			{
				length++;
			}
		}
		if(!length)
		{
			get_error_node("请选择此交换机下的节点！",document.getElementById("switcher_child").parentNode);
		}else{
			var input = document.createElement("input");
			input.type="hidden"
			input.name="SWICHER_VALUE";
			
			for(var i =0;i<switcher_interface.length;i++)
			{
				var my_class = switcher_interface[i];
				if($("."+my_class).size())
				{
					for(var j =0;j<$("."+my_class).size();j++)
					{
						switcher_value += $("."+my_class).eq(j).attr("value")+"|";
					}
				}
				switcher_value += "=";
			}
			input.value=switcher_value;
			document.getElementById("add").appendChild(input);
		}
	}
	
	var hostname = document.getElementById("HOST_NAME").value;
	var r = /[\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\?]+/g;
	if(!hostname)
	{
		get_error_node("请输入节点别名！",document.getElementById("HOST_NAME").parentNode);
	}else if(r.test(hostname))
	{
		get_error_node("节点名称含有非法字符！",document.getElementById("HOST_NAME").parentNode);
	}
	}else{
		var br0 = document.getElementById("br0").checked;
		var br1 = document.getElementById("br1").checked;
		if(!(br0 || br1))
		{
			get_error_node("至少应选择一个区域！",document.getElementById("br_con").parentNode);
		}
	}
	var error = document.getElementsByTagName("b");
	if(error.length>0)
	{
		return 0;
	}else{
		return 1;
	}
}

function remove_error_node()
{
	var error = document.getElementsByTagName("b");
	while(error.length)
	{
		for(var h = 0;h<error.length;h++)
		{
			error[h].parentNode.removeChild(error[h]);
		}
		remove_error_node();
	}
}

function get_error_node(err,container)
{
	var error_node = document.createElement("b");
	var txt = document.createTextNode(err);
	error_node.appendChild(txt);
	error_node.style.color = "red";
	container.appendChild(error_node);
}

function valid_ip(ip)
{
	var r = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/g;
	if(ip.match(r))
	{
		if((RegExp.$1<=255 && RegExp.$1>=0) && 
		(RegExp.$2<=255 && RegExp.$2>=0) && 
		(RegExp.$3<=255 && RegExp.$3>=0) &&  
		(RegExp.$4<=255 && RegExp.$4>=0) )
		{
			return 1;
		}else{
			return 0;
		}
	}
	return 0;
}

function valid_mask(ip_mask)
{
	var r = /^([\.0-9]+)\/(\d+)$/g;
	if(ip_mask.match(r))
	{
		var mask = RegExp.$2;
		if(valid_ip(RegExp.$1)&& mask<=32 && mask>= 0)
		{
			return 1;
		}else{
			return 0;
		}
	}
	return 0;
}


function get_s_node()
{
	remove_error_node();
	 var select_obj = document.getElementById("switcher_child");
	 var select_value = new Array();
	 var select_text = new Array();
	 var is_selected = 0;
	 
	 for(var i =0;i<select_obj.options.length;i++)
	 {
		if(select_obj.options[i].selected)
		{
			select_value.push(select_obj.options[i].value);
			select_text.push(select_obj.options[i].text);
			select_obj.removeChild(select_obj.options[i]);
			i--;
			is_selected = 1;
		}
	 }
	 if(is_selected)
	 {
		var switcher = document.getElementById("switcher_if");
		var li = document.createElement("LI");
		li.innerHTML += "<span class='note'>接口下节点为: </span><ul style='display:inline' id=''>";
		var temp = new Array();
		for(var j = 0;j<select_value.length;j++)
		{
			var values = select_value[j].split("=");
			li.innerHTML += "<li  style='display:inline' value='"+select_value[j]+"'>【<a href='#' onclick='rm_s_if(event)' class='if"+interface_num+"' value='"+values[0]+"'>"+select_text[j]+"</a>】</li>";
		}
		switcher_interface.push("if"+interface_num);
		interface_num++;
		switcher.appendChild(li);
	}else{
		var switcher = document.getElementById("switcher_if");
		get_error_node("没有选择任何节点！",switcher.parentNode);
	}
}

function show_hidden_child(evt)
{
	evt = evt|| window.event;
	var selected = evt.target||evt.srcElement;
	var father= selected.parentNode.parentNode.id;
	var r = /toggle.png$/;
	if(r.test(selected.src))
	{
		selected.src = "/images/toggle-expand.png";
	}else{
		selected.src = "/images/toggle.png";
	}
	$("#"+father+" > .UL").toggle();
}