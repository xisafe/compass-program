// JavaScript Document
$(document).ready(function(){
	$("#w_type").click(function(){
		var value=$("#w_type").val();
		if(value && value != "INTERFACE"){
			$("#mail").css("display", "inline");
		}
		else{$("#mail").css("display", "none");}
	});	
	$("#all_att").click(function(){
		var choose=$("#all_att").attr("checked");
		if(choose){
			$(".for_select").attr( "selected","selected" );
		}
		else{
			$(".for_select").attr( "selected","" );
		}
	});	
	$("#all_level").click(function(){
		var choose=$("#all_level").attr("checked");
		if(choose){
			$(".for_level").attr( "selected","selected" );
		}
		else{
			$(".for_level").attr( "selected","" );
		}
	});
});