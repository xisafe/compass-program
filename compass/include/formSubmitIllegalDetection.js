//Date:2016-12-5
//功能：form表单提交非法检测检查
//作者:	leo
//传入: 无
 $(document).ready(function() {
	!function() {
		f$ = $("form");
		f$.each(function(index,element) {
			$(element).on("submit", function() {
				var arr = new Array();
				var reg = /[<>]/;
				arr = $(this).serializeArray();
				for(var i = 0; i < arr.length; i++) {
					if(reg.test(arr[i].value)) {
						alert("请不要输入恶意信息!");
						return false;
					}
				}
			});
		});
	}();
 });