$(document).ready(function(){
	check_cert();	
	$("#AUTH").change(function(){
		check_cert();
	});
});
function check_cert(){
	var sel = $("#AUTH").val();
	if(sel == "psk"){
		$("#psk_value").css("display", 'inline-block');
		$("#filed").css("display", 'none');
	}
	else{
		$("#psk_value").css("display", 'none');
		$("#filed").css("display", 'inline-block');
	}
}