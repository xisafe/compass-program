//author:zhouyuan
//Date:2011-07-09
//function:用于backupschedule.cgi页面的js控制

$(document).ready(function(){
	document.getElementById("mail_backup").onclick = function()
	{
		
		//$('#tables').find("td").css('border','qpx solid #999');
		if(document.getElementById("mail_backup").checked)
		{
			document.getElementById("mail_item0").style.display=document.all?"block":"block";
			document.getElementById("mail_item4").style.display=document.all?"block":"table-cell";
		}else{
			document.getElementById("mail_item0").style.display="none";
			document.getElementById("mail_item4").style.display="none";
		}
	}
		
});
