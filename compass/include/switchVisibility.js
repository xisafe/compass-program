function switchVisibility(id, sw) {
    el = document.getElementById(id);
	rownum =document.getElementById("rownum");
    if (sw == 'on') 
	{
		if(id == 'cert')
		{
			el.style.display = 'block';
			rownum.setAttribute("rowspan",6);
		}else{
				var explorer = CheckBrowser();
				rownum.setAttribute("rowspan",5);
				if(explorer != "firefox")
				{
					el.style.display = 'block'
				}else{
					el.style.display = 'table-row'
				}
			}
    } else {
        el.style.display = 'none';		
		rownum.setAttribute("rowspan",6);
    }
}
function check_enabled(){
    var obj1 = document.getElementById("PUSH_GLOBAL_DNS");
    if(obj1.checked){
        document.getElementById("MAIN_DNS").style.display = "block";
        document.getElementById("SECOND_DNS").style.display = "block";
    }
    else{
        document.getElementById("MAIN_DNS").style.display = "none";
        document.getElementById("SECOND_DNS").style.display = "none";
    }
}
function check_time(obj){
    var val = obj.value;
    if(val == "manual"){
        $(".manual").css("display","table-row");
        $(".auto").css("display","none");
        $("#action_type").val("importcrl");
    }
    else{
        $(".auto").css("display","table-row");
        $(".manual").css("display","none");
        $("#action_type").val("save");
    }
}