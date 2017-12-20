$(document).ready(function(){
	/*用于鼠标移向待解释的表单元素时，显示帮助层,鼠标移除，帮助层消失*/
		$(".need_help").hover(function() {
			$(this).find(".help_div").stop()
			.animate({left: "150", opacity:1}, "fast")
			.css("display","block")
		}, function() {
			$(this).find(".help_div").stop()
			.animate({left: "130", opacity:0}, "10")
			.css("display","none")
		});
});