var float_host_data = new Array();
var float_host_all_data = new Array();
var float_net_data = new Array();
var float_net_all_data = new Array();

var legends = new Array();
var num_host = 100;
var num_net = 100;
var num_host_all = 100;
var num_net_all = 100;


var host_key;
var data = "";
var risk_logic;
var net_array = new Array();
var path_config = '/var/efw/risk/logic/config';//逻辑资产配置文件

//定义风险数组
var risk_array = {
					"risk0" : "OTHER,其他攻击",
					"risk1" : "NSPS,非可疑流量攻击",
					"risk2" : "UKN,未知流量攻击",
					"risk3" : "BUKN,潜在的Bad-Traffic",
					"risk4" : "AttemptedRecon,尝试侦查和获取泄露的信息",
					"risk5" : "SReconLimited,侦查和获取泄露的信息",
					"risk6" : "SReconLargescale,侦查和大规模获取泄露的信息",
					"risk7" : "ADOS,尝试Dos攻击",
					"risk8" : "SDOS,成功的Dos攻击",
					"risk9" : "AttemptedUser,尝试获取用户权限",
					"risk10" : "UnsuccessfulUser,不成功的用户权限获取",
					"risk11" : "SuccessfulUser,成功的用户权限获取",
					"risk12" : "AttemptedAdmin,尝试获取管理员权限",
					"risk13" : "SuccessfulAdmin,成功的获取管理员权限",
					"risk14" : "RpcPortMapDecode,rpc端口映射解码",
					"risk15" : "ShellCodeDetect,可执行脚本检测",
					"risk16" : "StringDetect,可疑的字符串检测",
					"risk17" : "FilenameDetect,可疑的文件名检测",
					"risk18" : "SPSLogin,可疑的登录检测",
					"risk19" : "SysCallDetect,系统调用检测",
					"risk20" : "TcpConnection,Tcp连接检测",
					"risk21" : "TrojanDetect,木马检测",
					"risk22" : "UCPC,不寻常的用户端口连接检测",
					"risk23" : "NetworkScan,网络扫描",
					"risk24" : "DOS,拒绝服务攻击",
					"risk25" : "NSP,非标准协议攻击",
					"risk26" : "PCD,通用协议命令解码攻击",
					"risk27" : "APVWA,入侵潜在的易受攻击的Web应用",
					"risk28" : "WAA,Web应用攻击",
					"risk29" : "MiscActivity,未明确分类的活动",
					"risk30" : "MiscAttack,未明确分类的攻击",
					"risk31" : "IcmpEvent,Icmp事件",
					"risk32" : "KickAssPorn",
					"risk33" : "PolicyViolation,侵犯潜在的企业隐私",
					"risk34" : "3DefaultLoginAttempt,尝试用默认的用户名和密码登录"
				};

var risk_obj = {
				get_net:function(str)
				{
					var temp = str.split("=\n");
					var risk_ary = new Array();
					for(x in temp)
					{
						var net_temp = temp[x].split("\n");
				
						var net = net_temp[0].split(",");
						if(net[0])
						{
							risk_ary.push(net[0]); 
						}
					}
					return risk_ary;
				},
				get_host:function(str,net_no)
				{
					var temp = str.split("=\n");
					var host_ary = new Array();
					for(x in temp)
					{
						var net_temp = temp[x].split("\n");
						var net_ary = net_temp[0].split(",");
						if(net_ary[0] == net_no)
						{
							for(var j = 1;j<net_temp.length;j++)
							{
								var net = net_temp[j].split(",");
								if(net[0])
								{
									host_ary.push(net[0]); 
								}
							}
						}
					}
					return host_ary;
				},
				get_all_host_risk:function(str)
				{
					var temp = str.split("=\n");
					var host_obj = new Object();
					var net_array = new Array;
					var host_array = new Array;
					var risk_array = new Array;
					var risk_no_array = new Array;
					
					for(x in temp)
					{
						var net_temp = temp[x].split("\n");
						var net_ary = net_temp[0].split(",");
						for(var j = 1;j<net_temp.length;j++)
						{
							var net = net_temp[j].split(",");
							
							for(var z= 3;z<net.length-1;z++)
							{
								var index = z-3;
								net_array.push(net_ary[0]);//标识节点ID
								host_array.push(net[0]);//标识父级ID
								risk_array.push(net[z]);//标识风险值
								risk_no_array.push(index);//表示第几类风险
							}
						}
					}
					host_obj.net = net_array;
					host_obj.host = host_array;
					host_obj.risk = risk_array;
					host_obj.risk_no = risk_no_array;
					return host_obj;
				},
				get_risk:function(str,net_no,host_no,risk_no)
				{
					var risk = "";
					if(str && net_no && host_no && risk_no)//获取主机分类风险
					{
						var temp = str.split("=\n");
						for(x in temp)
						{
							var net_temp = temp[x].split("\n");
							var net_ary = net_temp[0].split(",");
							if(net_ary[0] == net_no)
							{
								for(var j = 1;j<net_temp.length;j++)
								{
									var net = net_temp[j].split(",");
									if(net[0]== host_no)
									{
										risk = net[parseInt(risk_no)+3];
									}
								}
							}
						}
					}else if(str && net_no && host_no && !risk_no)//获取主机整体风险
					{
						var temp = str.split("=\n");
						
						for(x in temp)
						{
							var net_temp = temp[x].split("\n");
							var net_ary = net_temp[0].split(",");
							if(net_ary[0] == net_no)
							{
								for(var j = 1;j<net_temp.length;j++)
								{
									var net = net_temp[j].split(",");
									if(net[0]== host_no)
									{
										risk = net[38];
									}
								}
							}
						}
					}else if(str && net_no && !host_no && risk_no)//获取网络分类风险
					{
						var temp = str.split("=\n");
						for(x in temp)
						{
							var net_temp = temp[x].split("\n");
							var net_ary = net_temp[0].split(",");
							if(net_ary[0] == net_no)
							{
								risk = net_ary[parseInt(risk_no)+3];
							}
						}
					}else if(str && net_no && !host_no && !risk_no)//获取网络整体风险
					{
						var temp = str.split("=\n");
						for(x in temp)
						{
							var net_temp = temp[x].split("\n");
							var net_ary = net_temp[0].split(",");
							if(net_ary[0] == net_no)
							{
								risk = net_ary[35];
							}
						}
					}
					return risk;
				}
			}


function host_data(data,net,host,risk,num_host)
{
	var temp_risk = risk_obj.get_risk(data,net,host,risk);
	float_host_data.push([num_host,temp_risk]);
	float_host_data = float_host_data.slice(1,101);
	draw_flot(float_host_data,"host_channels",risk_array["risk"+risk],"host_type");
	
}


//绘制主机整体风险
function host_all_data(data,net,host,risk,num_host_all)
{
	var temp_risk = risk_obj.get_risk(data,net,host,null);
	float_host_all_data.push([num_host_all,temp_risk]);
	float_host_all_data = float_host_all_data.slice(1,101);
	draw_flot(float_host_all_data,"host_all_channels","risk_all","host_all");
}

//绘制网络分类风险
function net_data(data,net,host,risk,num_net)
{
	var temp_risk = risk_obj.get_risk(data,net,null,risk);
	float_net_data.push([num_net,temp_risk]);
	float_net_data = float_net_data.slice(1,101);
	draw_flot(float_net_data,"net_channels",risk_array["risk"+risk],"net_type");
}

//绘制网络整体风险
function net_all_data(data,net,host,risk,num_net_all)
{
	var temp_risk = risk_obj.get_risk(data,net,null,null);
	float_net_all_data.push([num_net_all,temp_risk]);
	float_net_all_data = float_net_all_data.slice(1,101);
	draw_flot(float_net_all_data,"net_all_channels","risk_all","net_all");
}

/*绘制分类风险top10直方图
function host_type_bar(data,net_ary)
{
	var host_obj = get_all_host_risk(data);
	var net = host_obj.net;
	var host = host_obj.host;
	var risk = host_obj.risk;
	var risk_no = host_obj.risk_no;
	
}*/


function get_risk_data()
{
		if($("#on_off").attr("src")== "/images/switch-on.png")
		{	 
		$.get('/cgi-bin/risk_back.cgi',{}, function(datas){
			$.getJSON('/cgi-bin/get_json.cgi',{path:path_config,type:'json'}, function(risk_config){
			risk_logic =  risk_config;
			data = datas;
			net_array  = risk_obj.get_net(data);
			host_array = risk_obj.get_host(data,net_array[0]);
			
			
			get_net_select_item(data,"NET_NO",risk_config);
			
			get_host_select_item(data,"HOST_IP",net_array[0],risk_config);
			
			get_risk_select_item("HOST_RISK");
			
			get_net_select_item(data,"NET_NO_ALL",risk_config,risk_config);
			get_host_select_item(data,"HOST_IP_ALL",net_array[0],risk_config);
			
			get_net_select_item(data,"NETS_NO",risk_config,risk_config);
			get_risk_select_item("NETS_RISK");
			
			get_net_select_item(data,"NETS_NO_ALL",risk_config);
			
			//绘制主机分类风险
			host_data(data,net_array[0],host_array[0],1,num_host);
			host_all_data(data,net_array[0],host_array[0],null,num_host_all);
			net_data(data,net_array[0],host_array[0],1,num_net);
			net_all_data(data,net_array[0],null,null,num_net_all);

			num_host++;
			num_host_all++;
			num_net++;
			num_net_all++;
		});
	});
	}
}


function host_change(host,type)
{
	var NET_NO  = document.getElementById("NET_NO").value;
	if(host && type=='host')
	{
		get_host_select_item(data,"HOST_IP",NET_NO,risk_logic);
	}
	var HOST_IP = document.getElementById("HOST_IP").value;
	var HOST_RISK = document.getElementById("HOST_RISK").value;
	host_data(data,NET_NO,HOST_IP,HOST_RISK,num_host);
	num_host++;

	var NET_ALL_NO  = document.getElementById("NET_NO_ALL").value;
	if(host && type=='host_all')
	{
		get_host_select_item(data,"HOST_IP_ALL",NET_ALL_NO,risk_logic);
	}
	var HOST_ALL_IP = document.getElementById("HOST_IP_ALL").value;
	host_all_data(data,NET_ALL_NO,HOST_ALL_IP,null,num_host_all);
	num_host_all++;
	
	var NETS_NO  = document.getElementById("NETS_NO").value;
	var NETS_RISK = document.getElementById("NETS_RISK").value;
	net_data(data,NETS_NO,null,NETS_RISK,num_net);
	num_net++;
	
	var NETS_NO_ALL  = document.getElementById("NETS_NO_ALL").value;
	net_all_data(data,NETS_NO_ALL,null,null,num_net_all);
	num_net_all++;
}



$(document).ready(function(){
			ini_host();
			var content_height =(document.documentElement.clientHeight||window.innerHeight)-130;
			$("#monitor_content").css("height",content_height+"px");
			if($("#IF_EXITS_LOG"))
			{
				get_risk_data();
				var host_key = setInterval("get_risk_data()",2000);
			}
			$("#NET_NO").change(function(){

				float_host_data = float_host_data.slice(1,101);
				for(var j = 0;j<100;j++)
				{
					float_host_data[j] = [j,0];
				}
				num_host = 100;

				clearInterval(host_key);
				host_key = setInterval("host_change(1,'host')",2000);
			});
		
			$("#HOST_IP").change(function(){
				float_host_data = float_host_data.slice(1,101);
				for(var j = 0;j<100;j++)
				{
					float_host_data[j] = [j,0];
				}
				num_host = 100;

				clearInterval(host_key);
				host_key = setInterval("host_change(1,'')",2000);
			});
		
			$("#HOST_RISK").change(function(){
				float_host_data = float_host_data.slice(1,101);
				for(var j = 0;j<100;j++)
				{
					float_host_data[j] = [j,0];
				}
				num_host = 100;
	
				clearInterval(host_key);
				host_key = setInterval("host_change(0,'')",2000);
			});
		
			$("#NET_NO_ALL").change(function(){
				float_host_all_data = float_host_all_data.slice(1,101);
				for(var j = 0;j<100;j++)
				{
					float_host_all_data[j] = [j,0];
				}
				num_host_all = 100;

				clearInterval(host_key);
				host_key = setInterval("host_change(1,'host_all')",2000);
			});
		
			$("#HOST_IP_ALL").change(function(){
				float_host_all_data = float_host_all_data.slice(1,101);
				for(var j = 0;j<100;j++)
				{
					float_host_all_data[j] = [j,0];
				}
				num_host_all = 100;

				clearInterval(host_key);
				host_key = setInterval("host_change(0,'host_all')",2000);
			});
		
			$("#NETS_NO").change(function(){
				float_net_data = float_net_data.slice(1,101);
				for(var j = 0;j<100;j++)
				{
					float_net_data[j] = [j,0];
				}
				num_net = 100;

				clearInterval(host_key);
				host_key = setInterval("host_change(0,'host')",2000);
			});
		
		
			$("#NETS_RISK").change(function(){
				float_net_data = float_net_data.slice(1,101);
				for(var j = 0;j<100;j++)
				{
					float_net_data[j] = [j,0];
				}
				num_net = 100;

				clearInterval(host_key);
				host_key = setInterval("host_change(0,'host')",2000);
			});
		
			$("#NETS_NO_ALL").change(function(){
				float_net_all_data = float_net_all_data.slice(1,101);
				for(var j = 0;j<100;j++)
				{
					float_net_all_data[j] = [j,0];
				}
				num_net_all = 100;

				clearInterval(host_key);
				host_key = setInterval("host_change(0,'host_all')",2000);
			});

			var length = $(".menu").size();
			for(var i = 0;i<length;i++)
			{
				$(".menu").eq(i).attr("index",i);
				$(".menu").eq(i).click(function()
				{
					$(".menu").removeClass("active");
					$(this).addClass("active");
					$(".comment_info").css("display","none");
					$(".comment_info").eq($(this).attr("index")).css("display","block");
				});
			}
});


function ini_host()
{
	float_host_data = new Array();
	float_host_all_data = new Array();
	float_net_data = new Array();
	float_net_all_data = new Array();
	
	for(var j = 0;j<100;j++)
	{
		float_host_data.push([j,0]);
		float_host_all_data.push([j,0]);
		float_net_data.push([j,0]);
		float_net_all_data.push([j,0]);
	}
}

function get_net_select_item(str,id,risk)
{
	var strs = "";
	var temp = risk_obj.get_net(str);
	for(var i=0;i<temp.length;i++)
	{
		if(temp[i])
		{
			var name = get_net_name(temp[i],risk);
			strs += "<option value='"+temp[i]+"'>"+name+"</option>";
		}
	}
	$("#"+id).html(strs);
}


function get_net_name(id,risk)
{
	var host_name = "";
	if(typeof risk == "object")
	{
		for(var x in risk)
		{
			if(compare(x,id) == 4 || compare(x,id) == 2)
			{
				host_name = get_net_name(id,risk[x].net);
				break;
			}else if(compare(x,id) == 3)
			{
				continue;
			}else if(compare(x,id) == 0)
			{
				host_name =  risk[x].host_name?risk[x].host_name:risk[x].type+" "+risk[x].ip;
				break;
			}
		}
	}
	return host_name;
}


function get_father_id(id)
{
	var r = /^(.*)_\d+$/g;
	if(r.test(id))
	{
		return RegExp.$1;
	}
}

function get_host_name(id,risk)
{
	var father = get_father_id(id);
	var host_name = "";
	if(typeof risk == "object")
	{
		for(var x in risk)
		{
			if(compare(x,father) == 4 || compare(x,father) == 2)
			{
				host_name = get_host_name(id,risk[x].net);
				break;
			}else if(compare(x,father) == 3)
			{
				continue;
			}else if(compare(x,father) == 0)
			{
				if(risk[x].host && risk[x].host[id])
				{
					host_name =  risk[x].host[id].host_name?risk[x].host[id].ip+"("+ risk[x].host[id].host_name+")": risk[x].host[id].ip;
				}
				break;
			}
		}
	}
	return host_name;
}

function compare(id1,id2)
{
	var r = "";
	var temp1 = "";
	var temp2 = "";
	if(id1 == id2){return 0;}
	else if((r = eval("/^"+id1+"(_\\d+)+$/g")) && r.test(id2)){return 4;}
	else if((r = eval("/^"+id1+"_\\d+$/")) && r.test(id2)){return 2;}
	else if((r = /^(.*)_\\d+$/) && r.test(id1) && (temp1 = RegExp.$1) && r.test(id2) && (temp2 = RegExp.$1) && temp1 == temp2){return 3;}
	else{return 5;}
}

function get_host_select_item(str,id,net_no,risk)
{
	var temp = risk_obj.get_host(str,net_no);
	var length = temp.length;
	var strs = "";
	if(length)
	{
		if(id=="HOST_IP")
		{
			$("#host_channels").css("display","block");
			$("#host_legend").css("display","block");
			$("#host_error").css("display","none");
		}else if(id=="HOST_IP_ALL"){
			$("#host_all_channels").css("display","block");
			$("#host_all_legend").css("display","block");
			$("#host_all_error").css("display","none");
		}
		for(var i = 0;i<length;i++)
		{
			var name = get_host_name(temp[i],risk);
			strs += "<option value='"+temp[i]+"'>"+name+"</option>";
		}
	}else{
		if(id=="HOST_IP")
		{
			$("#host_channels").css("display","none");
			$("#host_legend").css("display","none");
			$("#host_error").css("display","block");
		}else if(id=="HOST_IP_ALL"){
			$("#host_all_channels").css("display","none");
			$("#host_all_legend").css("display","none");
			$("#host_all_error").css("display","block");
		}
	}
	$("#"+id).html(strs);
}

function get_risk_select_item(id)
{
	var strs = "";
	for(var i = 1;i<35;i++)
	{
		strs += "<option value='"+i+"'>"+risk_array["risk"+i]+"</option>";
	}
	$("#"+id).html(strs);
}



function draw_flot(draw_data,id,label,legend)
{	
	var finaldis = new Array();
	finaldis[0] = {
					'label':label,
				    'data':draw_data,
					'color':5
		    	};

	var options = {
						'series': { shadowSize: 0 ,lines:{lineWidth: 1}}, // drawing is faster without shadows
						 yaxis: {
									max:1,
									min:0
							},
						'xaxis': { show: false},
						'legend':{
									noColumns: 1,
									container:$("."+legend)
								}
				};
		
	$.plot($("#"+id),finaldis,options);	
}

