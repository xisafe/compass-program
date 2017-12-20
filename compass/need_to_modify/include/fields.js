$(document).ready(function() {
    function toggle_on_change(field) {
        var id = field.attr("id");
        var value = field.selectedValues()[0];
        
        if (id == "")
            return;
        
        $("." + id).addClass("hidden");
        
        $("." + value).each(function() {
            if ($(this).hasClass(id) && $(this).hasClass("hidden"))
                $(this).removeClass("hidden");
        });
    }
    
    $(".toggle_on_change").change(function() {
        toggle_on_change($(this));
    });
    
    function toggle_on_click(field) {
        var id = field.attr("id");
        var show = false;
        if (field.is(":checked"))
            show = true;
        
        $("." + id).each(function() {
            if (show) {
                $(this).removeClass("hidden");
            }
            else {
                $(this).addClass("hidden");
            }
        });
    }
        
    $(".toggle_on_click").click(function() {
        var field = $(this);
        var id = field.attr("id");
        
        console.log(field.is(":checked"));
        
        toggle_on_click(field);
        
        if (field.is(":checked")) {
            $(".toggle_on_click").each(function() {
                if (id != $(this).attr("id")) {
                    toggle_on_click($(this));
                }
            });
            $(".toggle_on_change").each(function() {
                 toggle_on_change($(this));
            });
        }
    });
	
	
});

window.onload=function(){
	$(".up_img:first").css("visibility","hidden");
	$(".down_img:last").css("visibility","hidden");
}

