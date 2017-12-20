var display = "";
//var explorer = CheckBrowser();
var version = navigator.appVersion;
var IE7_use = version.indexOf(" MSIE 7.0");
if(window.XMLHttpRequest)
{
	display = "table-row";
}else{
	display = "block";
}
$('document').ready(function() {
	$('#LOGMAIL').click(function(){
		check_on();
		});
	check_on();
});
function display_remote(){
	if(document.getElementById("ENABLE_REMOTELOG").checked){
		document.getElementById("REMOTELOG_ADDR").style.display = "table-cell";
		document.getElementById("colspaned").setAttribute("colspan",1)
	}else{
		document.getElementById("REMOTELOG_ADDR").style.display = "none";
		document.getElementById("colspaned").setAttribute("colspan",2)
	}
}
function check_on(){
	if($("#LOGMAIL").attr("checked")){
		$(".mail_alert").css("display","table-row");
		$("#log_manage").attr("rowspan",3);
	}
	else{
		$(".mail_alert").css("display","none");
		if(IE7_use == -1){	
			$("#log_manage").attr("rowspan",3);
		}
	}
}
