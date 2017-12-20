function selectService(protoField, serviceField, portField) {
    var values;
    var service = document.getElementsByName(serviceField)[0];
    var port = document.getElementsByName(portField)[0];
    var proto = document.getElementsByName(protoField)[0];
	var protocol = document.getElementsByName("protocol")[0];
	//alert(protocol.value);
    values = service.value.split('/');
	if(values[1]) {
		values[1] = values[1].replace(/\n/g, "");
	}
    proto.value = values[1];
	
	
	//alert(values);
    if (values[0] == "any" || values[1] == "any") {
		$("#port_ul").css("display","none");
		$("#port_ul2").css("display","block");
        port.disabled = true;
        port.value = "";
    } else {
		$("#port_ul").css("display","block");
		$("#port_ul2").css("display","none");
        port.disabled = false;
        port.value = values[0];
    }
	if(protocol.value == "any" &&  values == "")
	{
		//alert("haha");
		$("#port_ul").css("display","none");
		$("#port_ul2").css("display","block");
        port.disabled = true;
        port.value = "";
	}
}

function updateService(protoField, serviceField, portField) {
    var found = 0;
    var service = document.getElementsByName(serviceField)[0];
    var port = document.getElementsByName(portField)[0];
    var proto = document.getElementsByName(protoField)[0];
	var proto_value = proto.value;
	
	if(proto_value != "any")
	{
		$("#port_ul").css("display","block");
		$("#port_ul2").css("display","none");
		if(proto_value == "icmp" || proto_value == "esp" || proto_value == "gre")
		{
			port.readOnly = true;
			port.disabled = true;
       		port.value = "";
			//为dnat页面隐藏转换后的端口表格
			//toggleTypes("target");
		}else{
			port.readOnly = false;
			port.disabled = false;
			//为dnat页面隐藏转换后的端口表格
			//toggleTypes("target");
		}
	}
	else{
		$("#port_ul").css("display","none");
		$("#port_ul2").css("display","block");
		port.value = "";
		//toggleTypes("target");
	}
    for (var i = 0; i < service.options.length; i++) {
        curvalue = service.options[i].value;
        values = curvalue.split('/');

        if (port.value == values[0] && proto.value == values[1]) {
            found = 1;
            service.value = curvalue;
            break;
        }
    }

    if (!found) {
        service.value = service.options[1].value;
    }

    if (proto.value == "any") {
        port.disabled = true;
        port.value = "";
    } else {
        port.disabled = false;
    }
}
