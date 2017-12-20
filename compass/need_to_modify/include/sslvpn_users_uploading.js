$(document).ready(function(){
	lastRefreshMsg();
});

function getMsg(){
	var hasMsgFlag = true;
	$.ajax({
		type: "get",
		url : '/cgi-bin/sslvpn_users_waitingmsg.cgi',
		async : false,
		success : function(data){
			if(data == -1){
				hasMsgFlag = false;
			}else{
				var msg_div = document.getElementById('wait_upload_msg');
				msg_div.innerHTML = data;
			}
		},
		error : function(data){
			hasMsgFlag = false;
		}
	});
	return hasMsgFlag;
}

function lastRefreshMsg(){
	var continueRefresh = getMsg();
	if(continueRefresh){
		setTimeout("lastRefreshMsg()",3000);
	}else{
		//window.location.reload();
		window.location = '/cgi-bin/sslvpn_users_management.cgi';
	}
}