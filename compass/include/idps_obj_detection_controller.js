/**author:刘炬隆（liujulong）
date:2014/05/23
**/

//输入框验证函数
function isip(obj){
    var sIPAddress = obj.value;
    var exp=/^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;    
    var reg = sIPAddress.match(exp);
    var ErrMsg="你输入的是一个非法的IP地址段,IP段为：xxx.xxx.xxx.xxx（xxx为0-255)！";   
    //var Msg="你输入的是一个合法的IP地址段！";   
    if(reg==null)
    {
        //alert(ErrMsg);
        if(obj.id == "addr_val"){
            document.getElementById("msg").innerHTML=ErrMsg;
        }else if(obj.id == "ip_f" || obj.id == "ip_t"){
            document.getElementById("msg_iprangge").innerHTML=ErrMsg;
        }else if(obj.id == "subnet_val" ){
            document.getElementById("msg_net").innerHTML=ErrMsg;
        }
        document.getElementById("submit-button").disabled=true;
    }
    else
    {
        if(obj.id == "addr_val"){
            document.getElementById("msg").innerHTML='<div id="TEMPLATE_FORMdescriptionCHINARK_NOTE_TIP" style="font-size: 11px; display: inline-block;"><img src="/images/note_note.png"></img></div>';
            document.getElementById("submit-button").disabled=false;
        }else if(obj.id == "ip_f" || obj.id == "ip_t"){
            if(obj.id == "ip_t"){
                var ip_from = document.getElementById("ip_f").value;
                var ip_from_array = ip_from.split(".");
                var ip_form_value= 0;
                ip_form_value += ip_from_array[0]*256^3;
                ip_form_value += ip_from_array[1]*256^2;
                ip_form_value += ip_from_array[2]*256^1;
                ip_form_value += ip_from_array[3]*256^0;
                var ip_to = document.getElementById("ip_t").value;
                var ip_to_array = ip_to.split(".");
                var ip_to_value= 0;
                ip_to_value += ip_to_array[0]*256^3;
                ip_to_value += ip_to_array[1]*256^2;
                ip_to_value += ip_to_array[2]*256^1;
                ip_to_value += ip_to_array[3]*256^0;
                if(ip_to_value < ip_form_value){
                    ErrMsg="IP地址范围错误，后者应该大于前者，如192.168.4.1 - 192.168.4.11";
                    document.getElementById("msg_iprangge").innerHTML=ErrMsg;
                    document.getElementById("submit-button").disabled=true;
                }else{
                    document.getElementById("msg_iprangge").innerHTML='<div id="TEMPLATE_FORMdescriptionCHINARK_NOTE_TIP" style="font-size: 11px; display: inline-block;"><img src="/images/note_note.png"></img></div>';
                    document.getElementById("submit-button").disabled=false;
                }
            }else{
                document.getElementById("msg_iprangge").innerHTML='<div id="TEMPLATE_FORMdescriptionCHINARK_NOTE_TIP" style="font-size: 11px; display: inline-block;"><img src="/images/note_note.png"></img></div>';
            }
        }else if(obj.id == "subnet_val" ){
            document.getElementById("msg_net").innerHTML='<div id="TEMPLATE_FORMdescriptionCHINARK_NOTE_TIP" style="font-size: 11px; display: inline-block;"><img src="/images/note_note.png"></img></div>';
            document.getElementById("submit-button").disabled=false;
        }
    }
}

//IP子网验证函数
function isip_net(obj){
    var ip_net = obj.value;
    ip_net = str_trim(ip_net);
    
    var test = new Array();
    test = ip_net.split("/");
    var length = test.length;
    var ip = test[0];
    var mask = test[1];
    //var exp=/^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\/(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;    
    var exp = /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}$/;
    var zero = /^0+/;
    var ErrMsg="你输入的是一个非法的子网地址段,示例:224.1.1.1/24！";
    if(mask<1 || mask>32 || length<2 || zero.test(mask) || !exp.test(ip)){
        document.getElementById("msg_net").innerHTML=ErrMsg;
        document.getElementById("submit-button").disabled=true;
    }else{
        var total_str = "";
        var temp = new Array();
        temp = ip.split(".");
        for(var i=0;i<4;i++){
            temp[i] = parseInt(temp[i]);
            temp[i] = formatip(temp[i]);
            total_str += temp[i];
        }
        var segment = total_str.substring(mask);
        var all_zero = /^0+$/;
        if(all_zero.test(segment)){
            document.getElementById("msg_net").innerHTML='<div id="TEMPLATE_FORMdescriptionCHINARK_NOTE_TIP" style="font-size: 11px; display: inline-block;"><img src="/images/note_note.png"></img></div>';
            document.getElementById("submit-button").disabled=false;
        }
        
    }
    
    /* var reg = ip_net.match(exp);
       
    //var Msg="你输入的是一个合法的IP地址段！";   
    if(reg==null)
    {
        
        document.getElementById("msg_net").innerHTML=ErrMsg;
        document.getElementById("submit-button").disabled=true;
    }
    else
    {
        
        document.getElementById("msg_net").innerHTML='<div id="TEMPLATE_FORMdescriptionCHINARK_NOTE_TIP" style="font-size: 11px; display: inline-block;"><img src="/images/note_note.png"></img></div>';
        document.getElementById("submit-button").disabled=false;
    } */
}

function formatip(ip){
    return (ip+256).toString(2).substring(1);
}

function get_str_byte(str){
    var bytes = 0;
    for(var i=0;i<str.length;i++){
        if(str.charCodeAt(i)>255){
            bytes+=2;
        }else{
            bytes+=1;
        }
    }
    return bytes;
}

function str_trim(str){
    return str.replace(/^\s+|\s+$g/,"");
}

//类型切换函数
function change_type(e){
    var type = e.value;
    var td = document.getElementById("name_addr_value");
    var input = document.getElementById("td_addr_value");
    if(type == "addr"){
        td.innerHTML = "IP地址";
        input.innerHTML = '<input style="margin-left:4px;float:left" name="addr_value" id = "addr_val" oninput="isip(this)" onpropertychange="isip(this)" class="input-text" type="text"><div style="float:left;color:red" id="msg"></div>';
        
    }else if(type == "subnet"){
        td.innerHTML = "IP子网";
        input.innerHTML = '<input style="margin-left:4px;float:left" name ="subnet_value" id = "subnet_val" class="input-text" type="text" oninput="isip_net(this)" onpropertychange="isip_net(this)"><div style="float:left;color:red" id="msg_net"></div>';
        
    }else if(type == "iprange"){
        td.innerHTML = "IP范围";
        input.innerHTML = '<div style="float:left"><input style="width:93px" oninput="isip(this)" onpropertychange="isip(this)" name = "ip_from" id = "ip_f" type="text"> - <input style="width:93px" oninput="isip(this)" onpropertychange="isip(this)" name="ip_to" id = "ip_t" type="text"></div> <div style="float:left;color:red" id="msg_iprangge"></div>';
        
    }
}