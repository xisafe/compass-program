var path_config = '/var/efw/risk/logic/config';
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
var risk_info = "";//记录日志信息

var first_host = 0;//配置文件中第一级主机数目
var first_net  = 0;//配置文件中第一级网络数目，为了初始化图片宽度
var last_net   = 0;//配置文件中第一级网络之后主机数目，为了初始化图片高度
var net_temp = 0;

var net_level = 2;//网络层级
var data = "";

var xmlText = '<?xml version="1.0"?>';
xmlText += '<modes>';		
var global = com.xjwgraph.Global;

var risk_obj = {
				get_risk:function(str,net_no,host_no,risk_no)
				{
					var risk = "";
					if(str && net_no && host_no && !risk_no)//获取主机整体风险
					{
						var temp = str.split("=\n");
						for(x in temp)
						{
							if(typeof temp[x] == 'string')
							{
								var net_temp = temp[x].split("\n");
								var net_ary = net_temp[0].split(",");
								if(net_ary[0] == net_no)
								{
									
									for(var j = 1;j<net_temp.length;j++)
									{
										var net = net_temp[j].split(",");
										if(net[1]== host_no)
										{
											risk = net[37];
										}
									}
								}
							}
						}
					}else if(str && net_no && !host_no && !risk_no)//获取网络整体风险
					{
						var temp = str.split("=\n");
						for(x in temp)
						{
							if(typeof temp[x] == 'string')
							{
								var net_temp = temp[x].split("\n");
								var net_ary = net_temp[0].split(",");
								if(net_ary[0] == net_no)
								{
									risk = net_ary[35];
								}
							}
						}
				}
			return risk;
		}
}
			
function risk_level(risk)
{
	if(risk== 0)
	{
		return "";
	}if(risk<=0.25)
	{
		return 1;
	}else if(risk<=0.5)
	{
		return 2;
	}else if(risk<=0.75)
	{
		return 3;
	}else if(risk<=1)
	{
		return 4;
	}
	return risk;
}

		
//服务类型字段申明
function type_img_hash(type,risk,service)
{
	risk = risk_level(risk);
	if(type != 'host')
	{
		return '../images/branch'+risk+'.png';
	}else{
		if(service == "SERVER")
		{
			return '../images/server'+risk+'.png';
		}else if(service == "WEB")
		{
			return '../images/server_web'+risk+'.png';
		}else if(service == "DATABASE")
		{
			return '../images/server_database'+risk+'.png';
		}else if(service == "BACKUP")
		{
			return '../images/server_backup'+risk+'.png';
		}else{
			return '../images/computer'+risk+'.png';
		}
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
		for(var y in host)
		{
			first_host++;
		}
	}
}

function count_config_net(data)
{
	for(var x in data)
	{
		var net = data[x].net;
		if(net)
		{
			first_net++;
			count_config_net(net);		
		}
	}
}

function count_net(net)
{
	var host = net.host;
	for(var x in host)
	{
		net_temp++;
	}
	var sub_net = net.net;
	if(sub_net)
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


		
function type_width_hash(type,service)
{
	if(type != 'host')
	{
		return '50';
	}else{
		if(service == "SERVER")
		{
			return '32';
		}else if(service == "WEB")
		{
			return '34';
		}else if(service == "DATABASE")
		{
			return '34';
		}else if(service == "BACKUP")
		{
			return '34';
		}else{
			return '32';
		}
	}
}

function type_height_hash(type,service)
{
	if(type != 'host')
	{
		return '50';
	}else{
		if(service == "SERVER")
		{
			return '56';
		}else if(service == "WEB")
		{
			return '56';
		}else if(service == "DATABASE")
		{
			return '56';
		}else if(service == "BACKUP")
		{
			return '56';
		}else{
			return '32';
		}
	}
}

function get_child(host,net,x,f_x,f_y,level,risk_info)
{
	if(host || net)
	{
		ini_y += 60;
		level++;
	}
	get_host(host,x,f_x,f_y,level,risk_info);
	get_net(net,x,f_x,f_y,level,risk_info);
}


function get_host(host,x,f_x,f_y,level,risk_info)
{
	var key = 0;//判断当前主机是第几个主机
	if(level){ini_y -= 30;}
	if(typeof host == "object")
	{
		var last = "";
		for(var y in host)
		{
			if(!level)
			{
				child_x = ini_x+18;
				child_y = (key%6)*60+ini_y;
			}else{
				child_x = ini_x+10;
				if(!host[last])
				{
					child_y = ini_y+40;
				}else if(host[last].service_type == "" || host[last].service_type == "host")
				{
					child_y = ini_y+40;
				}else{
					child_y = ini_y+55;
				}
			}
			
			var type = host[y].type;
			var service = host[y].service_type;		
			var title = host[y].host_name?host[y].host_name:host[y].ip;
			var risk = risk_obj.get_risk(risk_info,x,host[y].ip,null);	
			var title = host[y].host_name?host[y].host_name:host[y].ip;
			xmlText += '<mode class="module"   id="'+y+'"   title="'+title+'"  mac="'+host[y].mac+'"  host_name="'+host[y].host_name+'"   service_type="'+host[y].service_type+'"  remark="'+host[y].ip+'"  alise="'+host[y].alise+'"  backImgSrc="'+type_img_hash(type,risk,service)+'"    top="'+child_y+'"  left="'+ini_x+'"  width="'+type_width_hash(type,service)+'" height="'+type_height_hash(type,service)+'"/>';	
			if(!level)//第一级横排展示
			{
				var temp_y = f_y+20;
				var temp_x = f_x+20;
				xmlText += '<line d="M '+temp_x+' '+f_y+','+temp_x+' '+temp_y+' L '+child_x+' '+temp_y+', '+child_x+' '+child_y+' z"    brokenType="1"  id="line'+line_id+'"   wBaseMode="module'+y+'"  wIndex="2"  xBaseMode="module'+x+'"  xIndex="4" style=" CURSOR: pointer; POSITION: absolute; fill: none; stroke: black; stroke-width: 1.7999999999999998;fill: none; stroke: black; stroke-width: 1.7999999999999998"/>';
				ini_x += 45;
			}else{    //一级之后数列展示
				var end_point_y = child_y+15;
				xmlText += '<line d="M '+f_x+' '+f_y+' L '+f_x+' '+end_point_y+', '+child_x+' '+end_point_y+' z"  brokenType="1"  id="line'+line_id+'"   wBaseMode="module'+y+'"  wIndex="4"  xBaseMode="module'+x+'"  xIndex="7" style=" CURSOR: pointer; POSITION: absolute; fill: none; stroke: black; stroke-width: 1.7999999999999998;fill: none; stroke: black; stroke-width: 1.7999999999999998"/>';
				ini_y += 60;
			}
			line_id++;
			key++;
			last = y;
		}
	}
}

function get_net(net,x,f_x,f_y,level,risk_info)
{
	var key = 0;//判断当前子网络是否为第一个子网络
	var net_ini_x = ini_x;
	var net_ini_y = ini_y;
	if(typeof net == "object"){
	for(var y in net)
	{
		if(!level)
		{
			ini_y = (level+1)*60+30;
			ini_x += 50;//保持子网和子网之间的间距
			child_x = ini_x+20;
			child_y = ini_y;
		}else{
				ini_x   = net_ini_x;
				if(key){ini_y += 95;}else{ini_y += 40;}
				child_x = net_ini_x+20;
				child_y = ini_y+10;
			}
			
			var type = net[y].type;
			var service = net[y].service;
			var title = net[y].host_name?net[y].host_name:net[y].ip;
			var risk = risk_obj.get_risk(risk_info,y,null,null);	
			var title = net[y].host_name?net[y].host_name:net[y].ip;
			xmlText += '<mode class="module"   id="'+y+'"   title="'+title+'"  mac="'+net[y].mac+'"  host_name="'+net[y].host_name+'" service_type="'+net[y].service_type+'"  remark="'+net[y].ip+'"  alise="'+net[y].alise+'" backImgSrc="'+type_img_hash(type,risk,service)+'"    top="'+ini_y+'"  left="'+ini_x+'"  width="'+type_width_hash(type,service)+'" height="'+type_height_hash(type,service)+'"/>';	
			
			if(!level)
			{
				var temp_y = f_y+20;
				var temp_x = f_x+20;
				xmlText += '<line d="M '+temp_x+' '+f_y+','+temp_x+' '+temp_y+' L '+child_x+' '+temp_y+', '+child_x+' '+child_y+' z"  brokenType="1"  id="line'+line_id+'"   wBaseMode="module'+y+'"  wIndex="2"  xBaseMode="module'+x+'"  xIndex="4" style=" CURSOR: pointer; POSITION: absolute; fill: none; stroke: black; stroke-width: 1.7999999999999998;fill: none; stroke: black; stroke-width: 1.7999999999999998"/>';
				ini_x += 60;
			}else{
				xmlText += '<line d="M '+f_x+' '+f_y+' L '+f_x+' '+child_y+', '+child_x+' '+child_y+' z"  brokenType="1"  id="line'+line_id+'"   wBaseMode="module'+y+'"  wIndex="4"  xBaseMode="module'+x+'"  xIndex="7" style=" CURSOR: pointer; POSITION: absolute; fill: none; stroke: black; stroke-width: 1.7999999999999998;fill: none; stroke: black; stroke-width: 1.7999999999999998"/>';
				ini_x += 60;
			}
			line_id++;
			get_child(net[y].host,net[y].net,y,child_x,child_y,level,risk_info);
			key++;
		}
	}
}


function net_map(data,risk_info)
{
	for(var x in data)
	{
		if(x == "0")
		{
		father_x = ini_x+500;
		father_y = ini_y;
		var type = data[x].type;
		var risk = risk_obj.get_risk(risk_info,x,null,null);
		var service = data[x].service_type;
		var title = data[x].host_name?data[x].host_name:data[x].ip;
		xmlText += '<mode class="module"   id="'+x+'"   title="'+title+'"  mac="'+data[x].mac+'"  host_name="'+data[x].host_name+'"    service_type="'+data[x].service_type+'"  remark="'+data[x].remark+'"  alise="'+data[x].alise+'" backImgSrc="'+type_img_hash(type,risk,service)+'"    top="'+father_y+'"      left="'+father_x+'"  width="'+type_width_hash(type,service)+'" height="'+type_height_hash(type,service)+'"/>';				
		father_y += 30;		
		get_child(data[x].host,data[x].net,x,father_x,father_y,-1,risk_info);
		}
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
					
			img_width = first_host*75+first_net*80;
			img_height = (last_net+2)*70+40;
					
			graphUtils = com.xjwgraph.Utils.create({
						contextBody : 'contextBody',
						width : img_width,
						height : img_height,
						smallMap : 'smallMap',
						mainControl : 'mainControl',
						prop : 'prop'
			});
				
					var modes = jQuery("[divType='mode']");
					var modeLength = modes.length;
				
					for (var i = 0; i < modeLength; i++) {
						graphUtils.nodeDrag(modes[i]);
					}
					
					//获取风险文件
					jQuery.get('/cgi-bin/get_json.cgi',{path:path_risk,type:'text'}, function(risk_info){
						risk_info = risk_info;
						net_map(data,risk_info);
						xmlText += '</modes>';
						graphUtils.loadTextXml(xmlText);
					});

		});
}

//实时更新风险值
function update()
{
	jQuery.get('/cgi-bin/get_json.cgi',{path:path_risk,type:'text'}, function(risk_info){
		risk_info = risk_info;
		risk_update(data)
	});
}

function risk_update(data)
{
	for(var x in data)
	{
		var risk = risk_obj.get_risk(risk_info,x,null,null);
		var type = data[x].type;
		var img = type_img_hash(type,risk)
		$("#module"+x).css("background",img);
			
		var host = data[x].host;
		for(var z in host)
		{
			var host_risk = risk_obj.get_risk(risk_info,x,host[z].ip,null);
			var host_type = host[z].type;
			var img = type_img_hash(host_type,host_risk)
			$("#module"+z).css("background",img);
		}
			
		var net = data[x].net;
		risk_update(net);
	}
}


jQuery(document).ready(function () {
	draw();
	setInterval("update()",5000);
});
			
