function Check()
{
	var obj = document.getElementById('select_mail');
	var tmpValue = obj.options[obj.selectedIndex].value;
	if(tmpValue == '1')
	{
		document.getElementById('mail_address').style.display = "";
		document.getElementById('lt').value = '1';			
	}
	if(tmpValue == '0')
	{
		document.getElementById('mail_address').style.display = "none";
		document.getElementById('lt').value = '0';
	}
	if(tmpValue == '2')
	{
		document.getElementById('mail_address').style.display = "none";
		document.getElementById('lt').value = '2';
	}
}