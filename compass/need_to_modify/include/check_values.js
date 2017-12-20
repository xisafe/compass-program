// JavaScript Document

//检测IP合法性的函数start
function validip(str){   
    var ip =   /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}$/;   
    return ip.test(str);   
}
//检测IP合法性的函数end


//检测网段合法性的函数start
function formatIP(ip){
	return (ip+256).toString(2).substring(1); //格式化输出(补零)
}
function validsegment(str){  
	var test = new Array(); 
	test = str.split("/");
	var leng = test.length;
	var ip = test[0];
	var mask = test[1];
	if (mask < 1 || mask >32 || leng < 2){
		return false;
	}   
	else if(!validip(ip)){
		return false;
	}
	else{
		var total_str = "";
		var temp = new Array(); 
		temp = ip.split(".");
		for (i = 0;i < 4;i ++){
			temp[i] = parseInt(temp[i]);
			temp[i] = formatIP(temp[i]);
			total_str += temp[i];
		}
		var segment = total_str.substring(mask);
		var all_zero = /^0+$/;
		return all_zero.test(segment);
	}
}
//检测网段合法性的函数end

//检测IP范围合法性的函数start
function rangeip(str){   
	var temp = str.split("-");
	var startip = temp[0];
	var endip = temp[1];
	var start = startip.split(".");
	var end = endip.split(".");
	var flag = compareIP(startip,endip);
    if(validip(startip) && flag == -1){
		return validip(endip);
	}
	else{
		return false;
	}
}
function compareIP(ipBegin, ipEnd) {  
    var temp1;  
    var temp2;    
    temp1 = ipBegin.split(".");  
    temp2 = ipEnd.split(".");     
    for (var i = 0; i < 4; i++)  
    {  
        if (temp1[i]>temp2[i])  
        {  
            return 1;  
        }  
        else if (temp1[i]<temp2[i])  
        {  
            return -1;  
        }  
    }  
    return 0;     
}
//检测IP范围合法性的函数end
//检测数字的函数
function validnumber(str)  {         
     var reg = /^\d+$/;
	 var reg0 = /^0/;
	 if (reg0.test(str) && str != 0){
	 	return false;		 
	 }
     return reg.test(str);
}

//检测限制范围的数字的函数
function rangenumber(num,minnum,maxnum){
	if(validnumber(num)){
		if(num < minnum || num > maxnum){
			return false;
		}
		return true;
	}
	return false;
}
//检测端口号的函数start
function validport(str) { 
	return (validnumber(str) && str < 65536 && str > 0); 
}
//检测端口号的函数end

//检测端口号范围的函数start
function rangeport(str) { 
	str = str.replace("-",":");
	var reg = /^\d+:\d+$/;
	if(!reg.test(str)){
		return false;
	}
	var temp = str.split(":");
	temp[0] = parseInt(temp[0]);
	temp[1] = parseInt(temp[1]);
	if(!validport(temp[0]) || !validport(temp[1])){
		return false;
	}
	return (temp[1] > temp[0]);
}

//检测mac地址合法性的函数
function validmac(str) {
	str = str.replace(/-/g,":");
    var reg = /^([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2}):([\dA-Fa-f]{2})$/;
	return (reg.test(str));
}

//检测邮件地址的函数
function validemail(str) { 
	var myReg = /^[-_A-Za-z0-9]+@([_A-Za-z0-9]+\.)+[A-Za-z0-9]{2,3}$/; 
    return myReg.test(str); 
} 

//检测数字字母汉字
function ChinaorNumorLet(str) {//判断是否是汉字、字母、数字组成 
	var reg = /^[0-9a-zA-Z\u4e00-\u9fa5]+$/; 
	return reg.test(str);
}

//检测域名的函数
function validdomainname(str){
	var reg = /^[A-Za-z0-9+\.]+([_A-Za-z0-9]+\.)+[A-Za-z0-9]{2,6}$/; 
	var regnum = /^(\d+\.)+\d+$/;
	if(regnum.test(str)){
		return validip(str);
	}
	return reg.test(str);
}


//检测用户名的函数
function validname(str){
	var reg = /^[0-9a-zA-Z\u4e00-\u9fa5][_0-9a-zA-Z\u4e00-\u9fa5]+$/;
	if((str.length > 4) && (str.length < 17)){
		return reg.test(str);
	}
	return false;
}

//检测密码的函数
function validpassword(str){
	if((str.length < 6) || (str.length > 16)){
		return false;
	}
	return true;
}

//检测注释信息的函数
function validnote(str){
	if(str.length > 200){
		return false;
	}
	return true;
}
//检测URL合法性函数
function validurl(str){
	var strRegex = "^((https|http|ftp|rtsp|mms)?://)"
	+ "?(([0-9a-z_!~*'().&=+$%-]+: )?[0-9a-z_!~*'().&=+$%-]+@)?" //ftp的user@
	+ "(([0-9]{1,3}.){3}[0-9]{1,3}" // IP形式的URL- 199.194.52.184
	+ "|" // 允许IP和DOMAIN（域名）
	+ "([0-9a-z_!~*'()-]+.)*" // 域名- www.
	+ "([0-9a-z][0-9a-z-]{0,61})?[0-9a-z]." // 二级域名
	+ "[a-z]{2,6})" // first level domain- .com or .museum
	+ "(:([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]{1}|6553[0-5]))?" // 端口- :80
	+ "((/?)|" // a slash isn't required if there is no file name
	+ "(/[0-9a-z_!~*'().;?:@&=+$,%#-]+)+/?)$";
	var re=new RegExp(strRegex);
	var flag = false;
	if(re.test(str)){
		var re2 = /(\d+\.\d+\.\d+\.\d+)/;//判断URL中的IP地址是否合法
		var re3 = /\./;
		if (re2.test(str)){
			re2.exec(str);
			var s1 = RegExp.$1;
			flag = validip(s1);
		}
		else if(!re3.test(str)){
			flag = false;
		}
		else{
			flag = true;
		}
	};
	return flag;	
}
//检测是否和绿色IP同网段输入为检测的IP地址，绿色地址IP
function same_green(ip,green){
	if(!validip(ip)){
		return false;
	}
	var ip_mask = green.split("/");
	var mask = ip_mask[1];
	var temp_ip = ip.split(".");
	var ip_str = "",green_str = "";
	for (i = 0;i < 4;i ++){
		temp_ip[i] = parseInt(temp_ip[i]);
		temp_ip[i] = formatIP(temp_ip[i]);
		ip_str += temp_ip[i];
	}
	var temp_green = ip_mask[0].split(".");
	for (i = 0;i < 4;i ++){
		temp_green[i] = parseInt(temp_green[i]);
		temp_green[i] = formatIP(temp_green[i]);
		green_str += temp_green[i];
	}
	var ip_segment = ip_str.substring(0,mask);
	var green_segment = green_str.substring(0,mask);
	return ip_segment == green_segment;
}

//检测是否和橙色IP同网段输入为检测的IP地址，橙色地址IP
function same_orange(ip,orange){
	if(!validip(ip)){
		return false;
	}
	var ip_mask = orange.split("/");
	var mask = ip_mask[1];
	var temp_ip = ip.split(".");
	var ip_str = "",orange_str = "";
	for (i = 0;i < 4;i ++){
		temp_ip[i] = parseInt(temp_ip[i]);
		temp_ip[i] = formatIP(temp_ip[i]);
		ip_str += temp_ip[i];
	}
	var temp_orange = ip_mask[0].split(".");
	for (i = 0;i < 4;i ++){
		temp_orange[i] = parseInt(temp_orange[i]);
		temp_orange[i] = formatIP(temp_orange[i]);
		orange_str += temp_orange[i];
	}
	var ip_segment = ip_str.substring(0,mask);
	var orange_segment = orange_str.substring(0,mask);
	return ip_segment == orange_segment;
}