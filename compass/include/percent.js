/*功能：比例图模块编写         
  作者：周圆                    
  时间：2011-06-20               
  说明：此函数将产生一个或多个比例图,用表格的形式呈现
         ——————————————————————————————————————————————————————————————————————————————————————
		| 这格显示比例图value |   这格显示比例图    |  这格显示比例percent |   这格显示key   |
		 ——————————————————————————————————————————————————————————————————————————————————————
		|    CPU1:            |   比例图1           |       3%             |   1.23M           |
		 ——————————————————————————————————————————————————————————————————————————————————————
		|    内存:            |   比例图2           |       98%            |   1.23G           |
		 ——————————————————————————————————————————————————————————————————————————————————————
  传入参数：cgi_name: Ajax方法中的cgi页面名称
            cgi_var:传给cgi页面的变量,若有多个，则变量以split_mark隔开。
                    例如：假如split_mark为逗号",",则other_var=var1+","+var2+","....;
			table_width:表示表格宽度(例如table_width=100;则表示表格宽度为100px);
			append_To_id:表示存放此比例图的div的ID号;
			data:异步运行的cgi页面执行返回的参数。
				 其格式为"key=value=percent"。
				 其中key为比例图名称，value为值，percent为所占比例
				 若有多个比例图，则会传多组值，若此时split_mark为逗号",",其格式为
				 "key1,key2,key3=value1,value2,value3=percent1,percent2,percent3",
				 其中key1与value1,percent1相对应，key2与value2,percent2相对应等等....
				 其中key为字符串格式，value为字符串格式，percent为整形或浮点型(如70,23等)
  最终解释权归我所有,如有不明白,请当面问我,谢谢合作。
*/

var percent_draw_width = 100;//比例图默认宽度
var percent_draw_height = 20;//比例图默认高度
var percent_color = ['#43ac38','#f7ba4e','#d14507'];//分别对应着低中高时的比例图的颜色
var percent_bg = "style='background-color:#dee0de;border:1px solid #515350;width:"+percent_draw_width+"px;height:"+percent_draw_height+"px'";

function percent(cgi_name,cgi_var,split_mark,table_width,append_To_id)
{
	var table_style = "style='width:"+table_width+"px'";
	var str = "<table cellpadding='0' cellspacing='0' "+table_style+">";
	$.get('/cgi-bin/'+cgi_name, {trans_var:other_var}, function(data){
		var cur_data = data.split("=");
		var key_array = cur_data[0].split(split_mark);//用于存放key1,key2...
		var value_array = cur_data[1].split(split_mark);//用于存放value1，value2...
		var percent_array = cur_data[2].split(split_mark);//用于存放percent1，percent2...
		var percent_color_style = "";
		for(var i=0,var j=cur_data.length;i<j;i++){
			if(parseInt(percent_array[i])>80)
			{
				percent_color_style = percent_color[2];
			}else if(parseInt(percent_array[i])<20)
			{
				percent_color_style = percent_color[0];
			}else{
				percent_color_style = percent_color[1];
			}
			var percent_style = "style='width:"+percent_array[i]*percent_draw_width+"px;height:"+percent_draw_height+";background-color:"+percent_color_style+";display:block;float:left;margin:0px;padding:0px;'";
			str +="<tr><td style='font-weight:bold;'>"+key_array[i]+"</td><td "+percent_bg+"><span "+percent_style+"></span></td>"+percent_array[i]+"%"+"<td>"+value_array[i]+"</td></tr>";
		}
		str += "</table>";
		$(str).appendTo(append_To_id);
	});
}


