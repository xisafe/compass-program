//author:zhouyuan
//Date:2011-07-09
//function:����gui.cgiҳ���js����

window.onload=function refresh_other_frame()
{
    parent.window.document.getElementById("leftFrame").src="left.cgi";
	parent.parent.window.document.getElementById("topFrame").src="top.cgi";
	parent.parent.window.document.getElementById("bottomFrame").src="footer.cgi";
}

	