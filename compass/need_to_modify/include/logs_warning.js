// JavaScript Document
$(function () {
	var all_data = $("#data00").val();	
	var each_data = new Array();
	//将各种数据分开
	var total_num = 0;
	var attack_num = 0;	
	var dev_num = 0;	
	each_data = all_data.split("|||");	
	//分隔时间数据
	var time_data = new Array();
	time_data = each_data[1].split("&&");
	for (var i=0;i<6;i++){
		time_data[i] = parseInt(time_data[i]) ;
		total_num += time_data[i];
	}
	var data2 = [
		{ label: "0-4 时",  data: time_data[0]},
		{ label: "4-8 时",  data: time_data[1]},
		{ label: "8-12 时",  data: time_data[2]},
		{ label: "12-16 时",  data: time_data[3]},
		{ label: "16-20 时",  data: time_data[4]},
		{ label: "20-24 时",  data: time_data[5]},
	];
	//分隔告警类型数据
	var attack_data = new Array();
	attack_data = each_data[0].split("__");
	var len = attack_data.length;
	var data1 = new Array();
	for (var i=0;i<len;i++){
		if(i > 4){break;}
		var temp = new Array();
		temp = attack_data[i].split("=");
		temp[1] = parseInt(temp[1]);
		attack_num += temp[1];
		data1[i] = {label:temp[0],data:temp[1]};
	}
	if(len > 5){
		var other = total_num - attack_num;
		data1[5] = {label:"其他",data:other};
	}
	//分隔设备类型数据
	var dev_data = new Array();
	dev_data = each_data[2].split("__");
	var len3 = dev_data.length;
	var data3 = new Array();
	for (var i=0;i<len3;i++){
		if(i > 4){break;}
		var temp = new Array();
		temp = dev_data[i].split("=");
		temp[1] = parseInt(temp[1]);
		dev_num += temp[1];
		data3[i] = {label:temp[0],data:temp[1]};
	}
	if(len3 > 5){	
		var other = total_num - dev_num;
		data3[5] = {label:"其他",data:other};
	}
	//分隔入侵告警数据	
	var snort_data = new Array();
	snort_data = each_data[3].split("&&");
	for (var i=0;i<3;i++){
		snort_data[i] = parseInt(snort_data[i]) ;
	}
	var data4 = [
		{ label: "已告警且通过",  data: snort_data[0]},
		{ label: "已告警且丢弃",  data: snort_data[1]},
		{ label: "直接通过",  data: snort_data[2]},
	];
	
$.plot($("#graph1"), data1, 
	{
		series: {
			pie: { 
				show: true,
				radius: 1,
				label: {
					show: true,
					radius: 2/3,
					formatter: function(label, series){
						return '<div style="font-size:8pt;text-align:center;padding:2px;color:#00F;">'+Math.round(series.percent)+'%</div>';
					},
				}
			}
		},
		grid: {
			hoverable: true,
			clickable: false,
			
		},
		legend: {
			show: false
		}
	});
	$.plot($("#graph2"), data2, 
	{
		series: {
			pie: { 
				show: true,
				radius: 1,
				label: {
					show: true,
					radius: 2/3,
					formatter: function(label, series){
						return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'+Math.round(series.percent)+'%)</div>';
					},
				}
			}
		},
		grid: {
			hoverable: true,
			clickable: false,
			
		},
		legend: {
			show: false
		}
	});
	$.plot($("#graph3"), data3, 
	{
		series: {
			pie: { 
				show: true,
				radius: 1,
				label: {
					show: true,
					radius: 2/3,
					formatter: function(label, series){
						return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'+Math.round(series.percent)+'%</div>';
					},
				}
			}
		},
		grid: {
			hoverable: true,
			clickable: false,
			
		},
		legend: {
			show: false
		}
	});
	$.plot($("#graph4"), data4, 
	{
		series: {
			pie: { 
				show: true,
				radius: 1,
				label: {
					show: true,
					radius: 2/3,
					formatter: function(label, series){
						return '<div style="font-size:8pt;text-align:center;padding:2px;color:black;">'+Math.round(series.percent)+'%</div>';
					},
				}
			}
		},
		grid: {
			hoverable: true,
			clickable: false,
			
		},
		legend: {
			show: false
		}
	});
	$(".base").css("float","left");
	$("#graph1").bind("plothover", pieHover1);
	$("#graph2").bind("plothover", pieHover2);
	$("#graph3").bind("plothover", pieHover3);
	$("#graph4").bind("plothover", pieHover4);
	//$("#graph1").bind("plotclick", pieClick);

});
function pieHover1(event, pos, obj) 
{
	if (!obj)
                return;
	percent = parseFloat(obj.series.percent).toFixed(2);
	//alert(''+obj.series.label+': '+percent+'%');
	$("#graph1hover").html('<span style="float:left;font-weight: bold; color: '+obj.series.color+'">'+obj.series.label+'</span><br /><span style="float:left;font-weight: bold; color: '+obj.series.color+'">('+percent+'%)</span>');
}
function pieHover2(event, pos, obj) 
{
	if (!obj)
                return;
	percent = parseFloat(obj.series.percent).toFixed(2);
	//alert(''+obj.series.label+': '+percent+'%');
	$("#graph2hover").html('<span style="float:left;font-weight: bold; color: '+obj.series.color+'">'+obj.series.label+'</span><br /><span style="float:left;font-weight: bold; color: '+obj.series.color+'">('+percent+'%)</span>');
}
function pieHover3(event, pos, obj) 
{
	if (!obj)
                return;
	percent = parseFloat(obj.series.percent).toFixed(2);
	//alert(''+obj.series.label+': '+percent+'%');
	$("#graph3hover").html('<span style="float:left;font-weight: bold; color: '+obj.series.color+'">'+obj.series.label+'</span><br /><span style="float:left;font-weight: bold; color: '+obj.series.color+'">('+percent+'%)</span>');
}
function pieHover4(event, pos, obj) 
{
	if (!obj)
                return;
	percent = parseFloat(obj.series.percent).toFixed(2);
	//alert(''+obj.series.label+': '+percent+'%');
	$("#graph4hover").html('<span style="float:left;font-weight: bold; color: '+obj.series.color+'">'+obj.series.label+'</span><br /><span style="float:left;font-weight: bold; color: '+obj.series.color+'">('+percent+'%)</span>');
}
function pieClick(event, pos, obj) 
{
	if (!obj)
                return;
	percent = parseFloat(obj.series.percent).toFixed(2);
	alert(''+obj.series.label+': '+percent+'%');
}