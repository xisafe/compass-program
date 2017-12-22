// JavaScript Document
$(document).ready(function(){
	$("#protocal").change(function(){
		var prot = $("#protocal").val();
		if (prot == "ICMP"){
			$("#srcport").css("display", "none");
			$("#dstport").css("display", "none");
		}
		else{
			$("#srcport").css("display", "table-row");
			$("#dstport").css("display", "table-row");
		}
	});
});