//author:zhouyuan
//Date:2011-07-09
//function:�����ұ߿��ҳ���js����

document.onreadystatechange=function(){
	if (document.readyState == 'complete') {
		$('.right-waiting').fadeOut();
	}
}
$(document).ready(function(){

//���ڼ���IE6����Ϊ��ʱ����ʾ�߿��bug
		$(".ruleslist td").append(" ");
		$(".odd td").append(" ");
		$(".env td").append(" ");
		$(".odd_thin td").append(" ");
		$(".env_thin td").append(" ");
		
//���ڿ����ұ߿��ҳ���ڲ�ͬ�ֱ��ʣ���ͬ��С������������еĸ߶�
		var height_style = (document.documentElement.clientHeight||window.innerHeight)-33;
		$('.right-content').css("height",height_style+"px");
		$('#module-content23').css("height",height_style+"px");
		$('#menu-content').css("height",height_style+"px");
//--end--//		
		
//�������ӿ��������ʾ��openeditorbox��
		$('#add-div-header').click(function(){
            if($('#add-div-content').css('display')=='none')
			{
				$('#add-div-content').slideDown('1000');
				$('#add-div-header img').attr("src","/images/del.png");
			}else{
				$('#add-div-content').slideUp('1000');
				$('#add-div-header img').attr("src","/images/add.png")
			}
        });
		
		$('.cancel_button').click(function(){
			    $('#add-div-content').slideUp('1000');
				$('#add-div-header img').attr("src","/images/add.png")
		});
		
		$('.show_hidden_header img').click(function(){
			if($('.show_hidden_content').css('display')=='none')
			{
				$('.show_hidden_content').slideDown('1000');
				$('.show_hidden_header img').attr("src","/images/hidden.png");
			}else{
				$('.show_hidden_content').slideUp('1000');
				$('.show_hidden_header img').attr("src","/images/show.png")
			}
		});

//--end--//	

//���ڴ�����Ϣ��ʾ���js���ƣ�openbigbox��
		
		$('#pop-note-div input').click(function(){
			$('#pop-note-div').fadeOut("slow");
			$('#pop-div').css("display","none");
		});
		
		$('#pop-error-div input').click(function(){
			$('#pop-error-div').fadeOut("slow");
			$('#pop-div').css("display","none");
		});
		
		$('#pop-apply-div input').click(function(){
			$('#pop-apply-div').fadeOut("slow");
			$('#pop-div').css("display","none");
		});

//--end--//			
		
		
		
		
		
		$(".add-div-text").click(function() {
		$(".add-div-text div").css("display","none");
		$(this).find("div").slideDown("fast");
		});
		
		$('.net_config_radio').click(function(){
			//alert("haha");
			$('.net_config_radio').css("background-color","#FFF");
			$('.net_config_radio').css("font-weight","normal");
			$('.net_config_radio').css("border","0px");
			$('.net_config_radio input').attr("checked",false);
			$(this).css("background-color","#f5d66c");
			$(this).css("border","1px solid #f98952");
			$(this).css("font-weight","bold");
			$(this).find("input").attr("checked",true);
		});
	
});


$(window).resize(function(){
	var height_style = (document.documentElement.clientHeight||window.innerHeight)-38;
	$('.right-content').css("height",height_style+"px");
	$('#module-content23').css("height",height_style+"px");
	$('#menu-content').css("height",height_style+"px");
});

//author:zhouyuan
//date:2011-10-19
//function:�ǵĿ����ҳ�治�ܵ�����ʾ
window.onload=function(){
	var f;
	f=parent.location.pathname;
	if(f!= '/cgi-bin/center.cgi'){
		window.parent.parent.location.pathname = '/cgi-bin/main.cgi';
	}
}