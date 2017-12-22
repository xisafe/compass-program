var path_config = '/var/efw/risk/config';
var path_risk =   '/var/efw/risk/risk_log';

var img_width = 1600;
var img_height = 3000;

//初始化位置
var ini_x = 20;
var ini_y = 20;
var line_id = 0;
var mode_id = 0;
var child_x = 0;
var child_y = 0;

var first_host = 0;//配置文件中第一级主机数目
var first_net  = 0;//配置文件中第一级网络数目，为了初始化图片宽度
var last_net   = 0;//配置文件中第一级网络之后主机数目，为了初始化图片高度
var net_temp = 0;

var net_level = 2;//网络层级
var data = "";

var xmlText = '<?xml version="1.0"?>';
xmlText += '<modes>';		
var global = com.xjwgraph.Global;

//服务类型字段申明
function type_img_hash(type)
{
	if(type == 'host')
	{
		return '../images/computer0.gif';
	}else if(type == 'switch')
	{
		return '../images/switch0.gif';
	}else if(type == 'router')
	{
		return '../images/router0.gif';
	}else if(type == 'server')
	{
		return '../images/server0.gif';
	}else if(type == 'router_if' || type == 'switcher_if')
	{
		return '../images/if.png';
	}
}


//修改节点类型后修改json object
function set_config(net,node_no,key,value)
{
	for(var y in net)
	{
		if(y == node_no)
		{
			net[y][key] = value;
		}
		var sub_host = net[y].host;

		if(sub_host && sub_host[node_no])
		{
			sub_host[node_no][key] = value;
		}
		var sub_net = net[y].net;
		if(sub_net && sub_net[node_no])
		{
			sub_net[node_no][key] = value;
		}else{
			set_config(sub_net,node_no,key,value);
		}
	}
}

		
//计算配置文件中拓扑图复杂程度
function count_config(data)
{
	for(var x in data)
	{
		var host = data[x].host;
		if(typeof host == "object")
		{
			for(var y in host)
			{
				first_host++;
			}
		}
	}
}

function count_config_net(data)
{
	for(var x in data)
	{
		var net = data[x].net;
		if(typeof host == "object")
		{
			first_net++;
			count_config_net(net);		
		}
	}
}

function count_net(net)
{
	var host = net.host;
	if(typeof host == "object")
	{
		for(var x in host)
		{
			net_temp++;
		}
	}
	var sub_net = net.net;
	if(typeof sub_net == "object")
	{
		net_level++;
		for(var z in sub_net)
		{
			net_temp++;
			count_net(sub_net[z]);
		}
	}
	return net_temp;
}


		
function type_width_hash(type)
{
	if(type == 'host')
	{
		return '30';
	}else if(type == 'switch')
	{
		return '45';
	}else if(type == 'router')
	{
		return '40';
	}else if(type == 'server')
	{
		return '30';
	}else if(type == 'router_if' ||type == 'switcher_if')
	{
		return '40';
	}
}

function type_height_hash(type)
{
	if(type == 'host')
	{
		return '30';
	}else if(type == 'switch')
	{
		return '40';
	}else if(type == 'router')
	{
		return '28';
	}else if(type == 'server')
	{
		return '50';
	}else if(type == 'router_if' ||type == 'switcher_if')
	{
		return '26';
	}
}

function get_child(host,net,x,f_x,f_y,level)
{
	if(typeof host=="object"|| typeof net == "object")
	{
		ini_y += 60;
		level++;
	}
	get_host(host,x,f_x,f_y,level);
	get_net(net,x,f_x,f_y,level);
}


function get_host(host,x,f_x,f_y,level)
{
	var key = 0;//判断当前主机是第几个主机
	if(level){ini_y -= 30;}
	if(typeof host == "object")
	{
		for(var y in host)
		{
			if(!level)
			{
				child_x = ini_x+18;
				child_y = (key%6)*60+ini_y;
			}else{
				child_x = ini_x+10;
				child_y = ini_y+35;
			}
			
			var type = host[y].type;
			var title = host[y].ip?host[y].ip:host[y].type;
		
			xmlText += '<mode class="module"   id="'+y+'"   title="'+title+'"  mac="'+host[y].mac+'"  host_name="'+host[y].host_name+'"   service_type="'+host[y].service_type+'"  remark="'+host[y].remark+'"  alise="'+host[y].alise+'"  backImgSrc="'+type_img_hash(type)+'"    top="'+child_y+'"  left="'+ini_x+'"  width="'+type_width_hash(type)+'" height="'+type_height_hash(type)+'"/>';	
			if(!level)//第一级横排展示
			{
				var temp_y = f_y+20;
				var temp_x = f_x+20;
				xmlText += '<line d="M '+temp_x+' '+f_y+','+temp_x+' '+temp_y+' L '+child_x+' '+temp_y+', '+child_x+' '+child_y+' z"   brokenType="1"  id="line'+line_id+'"   wBaseMode="module'+y+'"  wIndex="2"  xBaseMode="module'+x+'"  xIndex="4" style=" CURSOR: pointer; POSITION: absolute; fill: none; stroke: black; stroke-width: 1.7999999999999998;fill: none; stroke: black; stroke-width: 1.7999999999999998"/>';
				ini_x += 40;
			}else{    //一级之后数列展示
				var end_point_y = child_y+15;
				xmlText += '<line d="M '+f_x+' '+f_y+' L '+f_x+' '+end_point_y+', '+child_x+' '+end_point_y+' z"   brokenType="1"  id="line'+line_id+'"   wBaseMode="module'+y+'"  wIndex="4"  xBaseMode="module'+x+'"  xIndex="7" style=" CURSOR: pointer; POSITION: absolute; fill: none; stroke: black; stroke-width: 1.7999999999999998;fill: none; stroke: black; stroke-width: 1.7999999999999998"/>';
				ini_y += 55;
			}
			line_id++;
			key++;
		}
	}
}



function get_net(net,x,f_x,f_y,level)
{
	var key = 0;//判断当前子网络是否为第一个子网络
	ini_y += 40;
	var net_ini_x = ini_x;
	var net_ini_y = ini_y;
	if(typeof net == "object"){
	for(var y in net)
	{
		if(!level)
		{
			ini_y = f_y+2;
			ini_x += 70;//保持子网和子网之间的间距
			child_x = ini_x+20;
			child_y = ini_y+10;
		}else{
				ini_x   = net_ini_x;
				child_x = net_ini_x+20;
				child_y = ini_y+10;
			}
			
			var type = net[y].type;

			var title = net[y].ip?net[y].ip:net[y].type;
			
			xmlText += '<mode class="module"   id="'+y+'"   title="'+title+'"  mac="'+net[y].mac+'"  host_name="'+net[y].host_name+'" service_type="'+net[y].service_type+'"  remark="'+net[y].remark+'"  alise="'+net[y].alise+'" backImgSrc="'+type_img_hash(type)+'"    top="'+ini_y+'"  left="'+ini_x+'"  width="'+type_width_hash(type)+'" height="'+type_height_hash(type)+'"/>';	
			if(!level)
			{
				var temp_y = f_y+20;
				var temp_x = f_x+20;
				xmlText += '<line d="M '+temp_x+' '+f_y+','+temp_x+' '+temp_y+' L '+child_x+' '+temp_y+', '+child_x+' '+child_y+' z"   brokenType="1"  id="line'+line_id+'"   wBaseMode="module'+y+'"  wIndex="2"  xBaseMode="module'+x+'"  xIndex="4" style=" CURSOR: pointer; POSITION: absolute; fill: none; stroke: black; stroke-width: 1.7999999999999998;fill: none; stroke: black; stroke-width: 1.7999999999999998"/>';
				ini_x += 60;
			}else{
				xmlText += '<line d="M '+f_x+' '+f_y+' L '+f_x+' '+child_y+', '+child_x+' '+child_y+' z"  brokenType="1"  id="line'+line_id+'"   wBaseMode="module'+y+'"  wIndex="4"  xBaseMode="module'+x+'"  xIndex="7" style=" CURSOR: pointer; POSITION: absolute; fill: none; stroke: black; stroke-width: 1.7999999999999998;fill: none; stroke: black; stroke-width: 1.7999999999999998"/>';
				ini_x += 60;
			}
			line_id++;
			get_child(net[y].host,net[y].net,y,child_x,child_y,level);
			key++;
		}
	}
}


function net_map(data)
{
	for(var x in data)
	{
		father_x = ini_x+500;
		father_y = ini_y;
		var type = data[x].type;
		xmlText += '<mode class="module"   id="'+x+'"   title="'+data[x].ip+'"  mac="'+data[x].mac+'"  host_name="'+data[x].host_name+'"    service_type="'+data[x].service_type+'"  remark="'+data[x].remark+'"  alise="'+data[x].alise+'" backImgSrc="'+type_img_hash(type)+'"    top="'+father_y+'"      left="'+father_x+'"  width="'+type_width_hash(type)+'" height="'+type_height_hash(type)+'"/>';				
		father_y += 30;		
		get_child(data[x].host,data[x].net,x,father_x,father_y,-1);
	}
}

/* object to string */  
function obj2str(o){  
        var r = [], i, j = 0, len;  
        if(o == null) {  
            return o;  
        }  
        if(typeof o == 'string'){  
            return '"'+o+'"';  
        }  
        if(typeof o == 'object'){  
            if(!o.sort){  
                r[j++]='{';  
                for(i in o){  
                    r[j++]= '"';  
                    r[j++]= i;  
                    r[j++]= '":';  
                    r[j++]= obj2str(o[i]);  
                    r[j++]= ',';  
                }  
                //可能的空对象  
                //r[r[j-1] == '{' ? j:j-1]='}';  
                r[j-1] = '}';  
            }else{  
                r[j++]='[';  
                for(i =0, len = o.length;i < len; ++i){  
                    r[j++] = obj2str(o[i]);  
                    r[j++] = ',';  
                }  
                //可能的空数组  
                r[len==0 ? j:j-1]=']';  
            }  
            return r.join('');  
        }  
        return o.toString();  
 } 
	
function draw()
{
	jQuery.getJSON('/cgi-bin/get_json.cgi',{path:path_config,type:'json'}, function(datas){
			data = datas;
			count_config(data);
			count_config_net(data);
					
			for(var x in data)
			{
				var net = data[x].net;
				var temp = 0;
				if(typeof net == "object")	{
				for(var y in net)
				{
					var temp = 0;
					net_temp = 0;

					temp = count_net(net[y]);
					if(temp > last_net)
					{
						last_net = temp;
					}
				}
				}		
			}
					
			img_width = first_host*80+first_net*80;
			img_height = (last_net+2)*62;
					
			graphUtils = com.xjwgraph.Utils.create({
						contextBody : 'contextBody',
						width : img_width,
						height : img_height,
			});
				
			var modes = jQuery("[divType='mode']");
			var modeLength = modes.length;
				
			for (var i = 0; i < modeLength; i++) {
				graphUtils.nodeDrag(modes[i]);
			}
			net_map(data);
			xmlText += '</modes>';
			graphUtils.loadTextXml(xmlText);
		});
}
			
