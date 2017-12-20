// JavaScript Document
function detail(name){
   	  var obj4 = document.getElementById("title_name");
   	  var obj = document.getElementById("detail_display_p");
   	  obj.value = "描述信息获取中，请稍候......";
   	  obj4.innerHTML = name;
      var server_address_whole = window.location.href;
   	  var locations = [];
   	  locations = server_address_whole.split("//");
   	  var ipaddress = [];
   	  ipaddress = locations[1].split("/");
   	  var destination = locations[0] + "//" + ipaddress[0] + ":10443/cgi-bin/description_html.cgi";
   	  $.get("description_html.cgi", {resource_name:name}, function(data){
        obj.value = data;
      });
	  display_protocol();
    }
	
	function change(){
	  var obj = document.getElementById("modify_type");
	  var obj2 = document.getElementById("hreftr");
	  if(obj.value=="web")
	  {
	     obj2.style.display = "table-row";
	  } else {
	     obj2.style.display = "none";
	  }
	}
	
	function change2(){
	  var obj = document.getElementById("new_type");
	  var obj2 = document.getElementById("hreftr");
	  if(obj.value=="web")
	  {
	     obj2.style.display = "table-row";
	  } else {
	     obj2.style.display = "none";
	  }
	}
	
	function clearall(){
	  var obj1 = document.getElementById("new_name");
	  var obj2 = document.getElementById("new_href");
	  var obj3 = document.getElementById("new_description");
	  var obj4 = document.getElementById("modify_name");
	  var obj5 = document.getElementById("modify_href");
	  var obj6 = document.getElementById("modify_description");
	  if(obj1)
	  {
	     obj1.value = "";
	  }
	  if(obj2)
	  {
	     obj2.value = "";
	  }
	  if(obj3)
	  {
	     obj3.value = "";
	  }
	  if(obj4)
	  {
	     obj4.value = "";
	  }
	  if(obj5)
	  {
	     obj5.value = "";
	  }
	  if(obj6)
	  {
	     obj6.value = "";
	  }
	}
	function check_all(){
	  var obj1 = document.getElementById("new_name");
	  var obj2 = document.getElementById("new_href");
	  var obj3 = document.getElementById("new_description");
	  var obj4 = document.getElementById("modify_name");
	  var obj5 = document.getElementById("modify_href");
	  var obj6 = document.getElementById("modify_description");
	  var obj7 = document.getElementById("new_type");
	  var obj8 = document.getElementById("modify_type");
	  var wrong =0;
	  if(obj1)
	  {
	     if(obj1.value==""&&wrong==0)
		 { 
		    alert("资源名称不能为空！");
		    wrong = 1;
		 }
		 if(obj1.value.length>50&&wrong==0)
		 {
		    alert("资源名称最大长度不能超过50个字符！");
			wrong = 1;
		 }
	  }
	  if(obj4)
	  {
	     if(obj4.value==""&&wrong==0)
		 { 
		    alert("资源名称不能为空！");
		     wrong = 1;
		 }
		 if(obj4.value.length>50&&wrong==0)
		 {
		    alert("资源名称最大长度不能超过50个字符！");
			 wrong = 1;
		 }
	  }
	  if(obj2)
	  {
	     if(obj7.value=="web"&&obj2.value==""&&wrong==0)
		 {
		    alert("访问方式为WEB访问时，地址栏不能为空！");
			 wrong = 1;
		 }
		 if(obj7.value=="web"&&obj2.value.length>100&&wrong==0)
		 {
		    alert("资源地址长度不能超过100个字符！");
			 wrong = 1;
		 }
	  }
	  if(obj5)
	  {
	     if(obj8.value=="web"&&obj5.value==""&&wrong==0)
		 {
		    alert("访问方式为WEB访问时，地址栏不能为空！");
			 wrong = 1;
		 }
		 if(obj8.value=="web"&&obj5.value.length>100&&wrong==0)
		 {
		    alert("资源地址长度不能超过100个字符！");
			 wrong = 1;
		 }
	  }
	  if(obj3)
	  {
	     if(obj3.value==""&&wrong==0)
		 {
		    alert("描述信息不能为空！");
			 wrong = 1;
		 }
	  }
	  if(obj6)
	  {
	     if(obj6.value==""&&wrong==0)
		 {
		    alert("描述信息不能为空！");
			 wrong = 1;
		 }
	  }
	  if(wrong)
	  {
	     return false;
	  } else {
	     return true;
	  }
	}
	
function setdes(count){
	   var line_name_obj = "rename" + count.toString();
	   var line_name = document.getElementById(line_name_obj).value;
	   var a = "des" + count.toString();
	   var obj = document.getElementById(a);
	   $.get("description_html.cgi", {resource_name:line_name}, function(data){
			if(data=="")
			{
				obj.innerHTML = "描述信息不存在！";
			} else {
				var line = data.substr(0,20);
				if(line=="描述信息不存在！")
				{
				} else {
				   if(data.length>20)
				   {
				      line = line + " ... ...";
				   }
				}
                obj.innerHTML = line;
			}
        });
}

var count = 1;
	var a = "des" + count.toString();
    while(document.getElementById(a))
    {
		setdes(count);
		count++;
		a = "des" + count.toString();
    }