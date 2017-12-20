/*
 * 描述: 证书验证
 *
 * 作者: leo，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2016.12.8 yupeng创建
 */

$(document).ready(function() {
	
	!function() {
		document.getElementById("upload_file").onchange = function() {
			var str = document.getElementById("upload_file").value;
			if(str == "") {
				document.getElementById("upload_file_tip").innerText = "未选择授权文件";
				document.getElementById("upload_file_tip").title = "未选择授权文件";
			}else {
				var arr = str.split("\\");
				document.getElementById("upload_file_tip").innerText = arr[arr.length-1];
				document.getElementById("upload_file_tip").title = arr[arr.length-1];
			}
		}
	}();
});