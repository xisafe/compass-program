//author:zhouyuan
//Date:2011-06-01
//function:����top.cgiҳ���js����
//modify:2011-07-20

$(document).ready(function(){

	$("#now_user").attr("title",$("#now_user").text());
	
//����top.cgi�����ul�Ļ���Ч��
		//$(".help-menu li").mouseover(function(){
		//	$(this).css("font-size","16px");
		//});
		
		//������ÿһ��li�������

		// $('.kwicks').kwicks({
		// 	max:180
		// });
	
		// $('.kwicks li').mouseover(function(){
		// 	//alert("haha");
		// 	$(this).css("font-size","14px");
		// 	$(this).css("font-weight","bold");
		// 	$(this).css("color","#c0521c");
		// 	$(this).css("border-left","1px solid #999");
		// 	$(this).css("border-right","1px solid #999");
		// 	$(this).find('.help_button').css("font-size","14px");
		// 	$(this).find('.help_button').css("font-weight","bold");
		// 	$(this).find('.help_button').css("color","#c0521c");
		// });
		
		// $('.kwicks li').mouseout(function(){
		// 	$(this).css("font-size","12px");
		// 	$(this).css("font-weight","normal");
		// 	$(this).css("color","#000");
		// 	$(this).css("border","0");
		// 	$(this).find('.help_button').css("font-size","12px");
		// 	$(this).find('.help_button').css("font-weight","normal");
		// 	$(this).find('.help_button').css("color","#000");
		// });
		
//����
});
	


//����˳���ťʱ���õĺ���
function exit_sys(url)
{
	var new_url = "https://"+url+":10443/";
	window.parent.location.replace(new_url);//��ת��½����
}

function fresh_current_page(url)
{
	var html_name = self.parent.frames["mainFrame"].frames["right"].document.getElementById("help_hidden").value;
	if(html_name != "/cgi-bin/template.cgi")
	{
		self.parent.frames["mainFrame"].document.getElementById("rightFrame").src=url+html_name;
	}else{
			self.parent.frames["mainFrame"].document.getElementById("rightFrame").src=url+"/cgi-bin/main_start.cgi";
	}
}