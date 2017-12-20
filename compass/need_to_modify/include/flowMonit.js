//author:zhouyuan
//Date:2012-03-16
//function:用于flowmonit.cgi页面的js控制

var zone_hash = {
	"br0" : "绿色区域",
	"br1" : "橙色区域",
	"br2" : "蓝色区域",
};

$(document).ready(function(){	

	//当选择了监控接口和区域时，动态更新ipfix的接口选项
	$("#choice_eth").change(function(){
		$("#eth_note").remove();
		$(".eth_id").remove();
		var obj = document.getElementById("choice_eth");
		
		for(var i = 0;i<obj.length;i++)
		{
			if(obj[i].selected)
			{
				var choice_eth = obj[i].value;
				var str = "<option class='eth_id'  value='"+choice_eth+"'>"+choice_eth+"</option>";
				$(str).appendTo("#ipfix_eth");
				document.getElementById("hidden_value1").value = choice_eth+"|";
			}
		}
	});
	
	$("#choice_zone").change(function(){
		$("#eth_note").remove();
		$(".zone_id").remove();
		var obj = document.getElementById("choice_zone");
		for(var i = 0;i<obj.length;i++)
		{
			if(obj[i].selected)
			{
				var choice_eth = obj[i].value;
				var str = "<option class='zone_id'  value='"+choice_eth+"'>"+zone_hash[choice_eth]+"</option>";
				$(str).appendTo("#ipfix_eth");
				document.getElementById("hidden_value2").value = choice_eth+"|";
			}
		}
	});
});