// JavaScript Document
function change_value(){
	var value = $("#uplinks").val();
	$.get('/cgi-bin/bandwidth-ajax.cgi',{value:value},function(data){
		var tmpdata=new Array();
		tmpdata=data.split(",");
		$("#upload").val(tmpdata[0]);
		$("#download").val(tmpdata[1]);
	});
}