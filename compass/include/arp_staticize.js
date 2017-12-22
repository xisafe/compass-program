/**author:liujulong
date:2014/04/11
**/
//选中所有函数
function select_all(){
    var Lc=document.getElementsByTagName('input');            
    var ctr=document.getElementById('checkall');
    var ele = document.getElementById("form_checked");
    if(ctr.checked==true){
        for (var i=0;i<Lc.length;i++){        
            if (Lc[i].type=='checkbox'&&Lc[i].name=="item"&&Lc[i].checked==false){                            
                Lc[i].checked=true;    
                var input = document.createElement('input');
                input.type="hidden";
                input.name="arp_static";
                input.value=Lc[i].value;
                ele.appendChild(input);
            }
        }        
    }else{
        for (var i=0;i<Lc.length;i++){        
            if (Lc[i].type=='checkbox'&&Lc[i].name=="item"&&Lc[i].checked==true){                            
                Lc[i].checked=false;
                var inputs=document.getElementsByName("arp_static");
                for(var j=0;j<inputs.length;j++){
                    if(inputs[j].value==Lc[i].value){
                        ele.removeChild(inputs[j]);
                    }
                }
            }
        }
    }            
}
//单个复选框选中
function add_input(e){    
    var ele = document.getElementById("form_checked");    
    var input = document.createElement('input');
    var cbk;
    input.type="hidden";
    if(e.name=="item"){
        cbk = document.getElementById("item"+e.value.split(",")[0]+e.value.split(",")[1]);
        input.name="arp_static";
    }    
    input.value=e.value;
    if(cbk.checked==true){
        ele.appendChild(input);
    }else if(cbk.checked==false){
        if(e.name=="item"){
            var inputs=document.getElementsByName("arp_static");
            for(var i=0;i<inputs.length;i++){
                if(inputs[i].value==e.value){
                    ele.removeChild(inputs[i]);
                }
            }    
        }            
    }
}
//扫描提示
function trips(){
    alert("正在进行扫描");
}