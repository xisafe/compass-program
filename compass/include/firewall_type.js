function toggleTypes(direction) {
  

    var selected = document.getElementsByName(direction+'_type')[0];
    for (var i = 0; i < selected.options.length; i++) {
        var title = document.getElementById(direction+'_'+selected.options[i].value+'_t');
        if (title != null) {
            title.style.display = 'none';
        }
        var value = document.getElementById(direction+'_'+selected.options[i].value+'_v');
        if (value != null) {
            value.style.display = 'none';
        }
        
        var opt = document.getElementById(direction+'_'+selected.options[i].value+'_opt');
        if(opt != null){
            opt.style.display = 'none';
        }
       
    }

    var enabletitle = document.getElementById(direction+'_'+selected.value+'_t')
    if (enabletitle != null) {
        enabletitle.style.display = 'block';
    }
    var enablevalue = document.getElementById(direction+'_'+selected.value+'_v')
    if (enablevalue != null) {
        enablevalue.style.display = 'block';
    }
    var enablevalue = document.getElementById(direction+'_'+selected.value+'_opt')
    if (enablevalue != null) {
        enablevalue.style.display = 'block';
    }
}
function hideServicePort(direction) {
    var selected = document.getElementsByName(direction+'_type')[0];
	var servicePort = document.getElementById('service_port_tr');
	if(selected.value == "res"){
		servicePort.style.display = "none";
	}else{
		servicePort.style.display = "table-row";
	}
}
function toggleMetric(element) {
	if ( element.value == "gw" ) {
		// 如果选择了静态网关
		$( "#via_type_td" ).attr( "rowspan", 2 );
		$( "#metric_tr" ).show();
	} else {
		// 如果选择了静态网关
		$( "#via_type_td" ).attr( "rowspan", 1 );
		$( "#metric_tr" ).hide();
	}
}