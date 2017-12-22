//author:zhouyuan
//Date:2012-08-03
//function:用于风险日志页面的js控制

var attack_pie = new Array();  //攻击类型top5
var host_pie = new Array();    //主机风险top5
var net_pie = new Array();     //部门风险top5
var risk_pie = new Array();    //风险top5
var attack_flow = new Array(); //攻击类型曲线图

//定义风险数组
var risk_array = {
					"0" : "OTHER,其他攻击",
					"1" : "NSPS,非可疑流量攻击",
					"2" : "UKN,未知流量攻击",
					"3" : "BUKN,潜在的Bad-Traffic",
					"4" : "AttemptedRecon,尝试侦查和获取泄露的信息",
					"5" : "SReconLimited,侦查和获取泄露的信息",
					"6" : "SReconLargescale,侦查和大规模获取泄露的信息",
					"7" : "ADOS,尝试Dos攻击",
					"8" : "SDOS,成功的Dos攻击",
					"9" : "AttemptedUser,尝试获取用户权限",
					"10" : "UnsuccessfulUser,不成功的用户权限获取",
					"11" : "SuccessfulUser,成功的用户权限获取",
					"12" : "AttemptedAdmin,尝试获取管理员权限",
					"13" : "SuccessfulAdmin,成功的获取管理员权限",
					"14" : "RpcPortMapDecode,rpc端口映射解码",
					"15" : "ShellCodeDetect,可执行脚本检测",
					"16" : "StringDetect,可疑的字符串检测",
					"17" : "FilenameDetect,可疑的文件名检测",
					"18" : "SPSLogin,可疑的登录检测",
					"19" : "SysCallDetect,系统调用检测",
					"20" : "TcpConnection,Tcp连接检测",
					"21" : "TrojanDetect,木马检测",
					"22" : "UCPC,不寻常的用户端口连接检测",
					"23" : "NetworkScan,网络扫描",
					"24" : "DOS,拒绝服务攻击",
					"25" : "NSP,非标准协议攻击",
					"26" : "PCD,通用协议命令解码攻击",
					"27" : "APVWA,入侵潜在的易受攻击的Web应用",
					"28" : "WAA,Web应用攻击",
					"29" : "MiscActivity,未明确分类的活动",
					"30" : "MiscAttack,未明确分类的攻击",
					"31" : "IcmpEvent,Icmp事件",
					"32" : "KickAssPorn",
					"33" : "PolicyViolation,侵犯潜在的企业隐私",
					"34" : "3DefaultLoginAttempt,尝试用默认的用户名和密码登录"
};
				
$(document).ready(function(){
	var host_top = eval("("+document.getElementById("host_top").innerHTML+")");
	var net_top = eval("("+document.getElementById("net_top").innerHTML+")");
	var risk_top = eval("("+document.getElementById("risk_top").innerHTML+")");
	var risk_flow =document.getElementById("risk_flow").innerHTML;

	var risk_flow_con = new Array();
	var host_all = 0;
	var net_all = 0;
	var risk_all = 0;

	for(var x in host_top)
	{
		host_all += host_top[x]*1;
		
	}
	
	for(var x in host_top)
	{
		var title = x.replace(/_/g,".");
		var temp_hash ={
							"label":title,
							"data":parseInt((host_top[x]/host_all)*1000000)/10000
						};
		host_pie.push(temp_hash);
	}


	for(var x in net_top)
	{
		net_all += net_top[x]*1;
	}
	for(var x in net_top)
	{
		var data = 0;
		if(net_all)
		{
			data = parseInt((net_top[x]/net_all)*1000000)/10000;
		}else{
			data=20;
		}
		var temp_hash ={
							"label":x,
							"data":data
						};
		net_pie.push(temp_hash);
	}
	
	

	for(var x in risk_top)
	{
		risk_all += risk_top[x]*1;
	}
	for(var x in risk_top)
	{
		var data = 0;
		if(risk_all)
		{
			data = parseInt((risk_top[x]/risk_all)*1000000)/10000;
		}else{
			data=20;
		}
		var temp_hash ={
							"label":risk_array[x],
							"data":data
						};
		risk_pie.push(temp_hash);
	}
	
	
	var risk_flow_ary =  risk_flow.split(/,/);
	for(var j = 0;j<risk_flow_ary.length;j++)
	{
		risk_flow_con.push([j,risk_flow_ary[j]]);
	}
	
	if(host_pie.length>1 || (host_pie.length==1 && host_pie[0])){draw_pie("host_top_pie",host_pie);}
	if(net_pie.length>1 || (net_pie.length==1 && net_pie[0])){draw_pie("net_top_pie",net_pie);}
	if(risk_pie.length>1 || (risk_pie.length==1 && risk_pie[0])){draw_pie("risk_top_pie",risk_pie);}
	if(risk_pie.length>1 || (risk_pie.length==1 && risk_pie[0])){draw_flot("risk_flow_con",risk_flow_con);}
	
});



function draw_flot(id,data)
{	
	var finaldis = new Array();
	finaldis[0] = {
				    'data':data,
					'color':5
		    	};

	var options = {
						'series': { shadowSize: 0 ,lines:{lineWidth: 1}}, // drawing is faster without shadows
						 yaxis: {
									max:1,
									min:0
							},
						'xaxis': { show: false},
				};
		
	$.plot($("#"+id),finaldis,options);	
}

function draw_pie(id,data)
{
	$.plot($("#"+id), data,
	{
        series: {
            pie: {
                show: true
            }
        },
		'legend':{
					noColumns: 1,
					container:$("#"+id+"_legend")
				}
	});
}