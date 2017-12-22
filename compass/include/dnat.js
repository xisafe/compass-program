var display = "";
var explorer = CheckBrowser();
var IE7_use = -1;

if(explorer == "firefox")
{
	display = "table-row";
}else{
	display = "block";
}

$('document').ready(function() {
    $("#simple").click(show_simple);
    $("#advanced").click(show_advanced);
    $(".policy").change(policy_change);
    $("#target_type").change(target_type_change);
	toggle_filter_policy($(".policy").val());
	//判断浏览器版本设定rowspan初始值
	var version = navigator.appVersion;
	IE7_use = version.indexOf(" MSIE 7.0");
	if(IE7_use!=-1){
	  $("#translate_to_td").attr("rowspan","16");
	}
	else{
	  $("#translate_to_td").attr("rowspan","8");
	}	
	toggleTypes("target");
});

function toggleTypes(direction) {
	var selected = $('#'+direction+'_type').val();
	//选择转换类型时隐藏不需要的表格
	if(direction == "target"){
		$('tr:.all_tr').css("display","none");
		$('tr:.target_tr_'+selected).css("display", display);		
		var objS = document.getElementById("target_type");
		var value = objS.options[objS.selectedIndex].value;
		var rowspan = 9;
		//判断协议是否为UDP和TCP，只要不隐藏转换端口的表格2012-1-7 by 张征
		var services = document.getElementsByName("protocol")[0].value;
		if(services == "esp" || services == "gre" || services == "any" || services == "icmp"){
			$('tr:.all_port_tr').css("display", "none");
			$('tr:.all_port_tr input').val("");
			$('tr:.all_port_tr div').css("display", "none");
			rowspan --;
		}
		//END
		//非IE7浏览器时选项不同时改变rowspan值
		if(value == "map"){
			rowspan = 7;
		}
		if(IE7_use==-1){
			$("#translate_to_td").attr("rowspan",rowspan);
		}
		else{
			$("#translate_to_td").attr("rowspan",16);
		}
	}
	//选择目标时隐藏不需要的内容
	if(direction == "dst"){
		$('div:.all_dst').css("display","none");
		$('#dst_'+selected+'_v').css("display", display);
		$('#dst_'+selected+'_t').css("display", display);
	}
	//选择源时隐藏不需要的内容
	if(direction == "src"){
		$('div:.all_src').css("display","none");
		$('#src_'+selected+'_v').css("display", display);
		$('#src_'+selected+'_t').css("display", display);
	}
}
function show_simple() {
    $(".simple").show();
    $(".advanced").hide();
    $("#target_type").val("ip");
    toggleTypes('target');
    $("#src_type").val("any");
    toggleTypes('src');
    $("#filter_policy").val("ALLOW");
}

function show_advanced() {
    $(".simple").hide();
    $(".advanced").show();
}

function toggle_filter_policy(value) {
    if (value == "RETURN") {
        $(".filter_policy").hide();
    }
    else {
        $(".filter_policy").css("display","inline-block" );
    }
}

function policy_change() {
    toggle_filter_policy($(this).val());
}

function target_type_change() {
    target_type = $(".policy").val();
    toggle_filter_policy(target_type);
}