var allow_png = "/images/accept.png";
var deny_png = "/images/deny.png";
var partial_png = "/images/partial.png";

function customCategoryStatus(category) {
    icon = category.parent().parent().parent().parent().parent().find("img.statusall");
    setCategoryTypeStatus(icon)
}

function setCategoryTypeStatus(icon, allow) {
    var name = icon.attr("name");
    var allowed = 0;
    var denied = 0;
    var partial = 0;
    
    $("div." + name).find("div.category-head").each(function() {
        if (typeof allow != "undefined") {
            setCategoryStatus($(this), allow, false);
            if(allow == true)
                allowed++;
            else
                denied++;
        }
        else {
            png = $(this).children("img.status").attr("src")
            if (png == allow_png)
                allowed++;
            else if (png == deny_png)
                denied++;
            else
                partial++;
        }
    });
    
    if (partial > 0) 
        icon.attr("src", partial_png);
    else if (allowed == 0)
        icon.attr("src", deny_png);
    else if (denied == 0)
        icon.attr("src", allow_png);
    else
        icon.attr("src", partial_png);
}

$(document).ready(function() {
    $("img.statusall").click(function() {
        var allow = false;
        if($(this).attr("src") == deny_png) {
            allow = true;
        }
        else {
            allow = false;
        }
        setCategoryTypeStatus($(this), allow)
    });
    $("img.statusall").each( function() {
        setCategoryTypeStatus($(this));
    });
});