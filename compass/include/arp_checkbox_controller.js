var paging_holder = {
    url: "/cgi-bin/arp_table_manager.cgi",
    add_title: "添加规则",
    update_title: "更新规则",
    page_size: 15,
    total_page: 0,
    first_page: 1,
    current_page: 1,
    from_num: 0,
    to_num: 0,
    search: "",
    data_content:{
        total: 0,
        detail_data: [],
        display_cols: ["col1", "col2", "col3"]
    }
};
function select_all(){
	var Lc=document.getElementsByTagName('input');			
	var ctr=document.getElementById('CHECKALL');
	var ele = document.getElementById("form_checked");
	if(ctr.checked==true){
		for (var i=0;i<Lc.length;i++){		
			if (Lc[i].type=='checkbox'&&Lc[i].name=="cbk_static"&&Lc[i].checked==false){							
				Lc[i].checked=true;	
				//var cbk = document.getElementById("cbk"+Lc[i].value);
				var input = document.createElement('input');
				input.type="hidden";
				input.name="arp_static";
				input.value=Lc[i].value;
				ele.appendChild(input);
			}else if (Lc[i].type=='checkbox'&&Lc[i].name=="cbk_dynomic"&&Lc[i].checked==false){							
				Lc[i].checked=true;	
				//var cbk = document.getElementById("cbk"+Lc[i].value);
				var input = document.createElement('input');
				input.type="hidden";
				input.name="arp_dynomic";
				input.value=Lc[i].value;
				ele.appendChild(input);
			}
		}		
	}else{
		for (var i=0;i<Lc.length;i++){		
			if (Lc[i].type=='checkbox'&&Lc[i].name=="cbk_static"&&Lc[i].checked==true){							
				Lc[i].checked=false;
				var inputs=document.getElementsByName("arp_static");
				for(var j=0;j<inputs.length;j++){
					if(inputs[j].value==Lc[i].value){
						ele.removeChild(inputs[j]);
					}
				}
			}else if(Lc[i].type=='checkbox'&&Lc[i].name=="cbk_dynomic"&&Lc[i].checked==true){
				Lc[i].checked=false;
				var inputs=document.getElementsByName("arp_dynomic");
				for(var j=0;j<inputs.length;j++){
					if(inputs[j].value==Lc[i].value){
						ele.removeChild(inputs[j]);
					}
				}
			}
		}
	}			
}

function add_input(e,s){	
	var ele = document.getElementById("form_checked");	
	var input = document.createElement('input');
	input.type="hidden";
	if(e.name=="cbk_static"){
		var cbk = document.getElementById("cbk_static"+e.value);
		input.name="arp_static";
	}else if(e.name=="cbk_dynomic"){
		var cbk = document.getElementById("cbk_dynomic"+e.value);
		input.name="arp_dynomic";
	}	
	input.value=e.value;
	if(cbk.checked==true){
		ele.appendChild(input);
	}else if(cbk.checked==false){
		if(e.name=="cbk_static"){
			var inputs=document.getElementsByName("arp_static");
			for(var i=0;i<inputs.length;i++){
				if(inputs[i].value==e.value){
					ele.removeChild(inputs[i]);
				}
			}	
		}else if(e.name=="cbk_dynomic"){
			var inputs=document.getElementsByName("arp_dynomic");
			for(var i=0;i<inputs.length;i++){
				if(inputs[i].value==e.value){
					ele.removeChild(inputs[i]);
				}
			}
		}
			
	}
}
