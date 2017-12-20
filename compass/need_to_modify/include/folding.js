var expand_png = "/images/expand.gif";
var collapse_png = "/images/collapse.gif";
var allow_png = "/images/accept.png";
var deny_png = "/images/deny.png";
var partial_png = "/images/partial.png";

function setSubCategoryStatus(name, allow) {
    if (allow == false)
        $("input[name=" + name + "]").attr("value", "deny");
    else
        $("input[name=" + name + "]").attr("value", "");
    $("img[name=" + name + "]").each( function() {
        if (allow == false)
            $(this).attr("src", deny_png);
        else
           $(this).attr("src", allow_png);
        var klass = $(this).attr("class");
        setCategoryStatus(klass);
    });
}

function setCategoryStatus(name, allow) {
    var allowed = 0;
    var denied = 0;
    
    $("img." + name).each( function() {
        if (typeof allow != "undefined") {
            var name = $(this).attr("name");
            setSubCategoryStatus(name, allow);
            if(allow == true)
                allowed++;
            else
                denied++;
        }
        else {
            if($(this).attr("src") == allow_png)
                allowed++;
            else
                denied++;
        }
    });

    if (allowed == 0)
        $("img[name=" + name + "]").attr("src", deny_png);
    else if (denied == 0)
        $("img[name=" + name + "]").attr("src", allow_png);
    else
        $("img[name=" + name + "]").attr("src", partial_png);
}

$(document).ready(function() {
    $("div.foldingtitle").click( function() {
        var name = $(this).attr("name");
        if($("img[name=fold_" + name + "]").attr("src") == expand_png) {
            $("#" + name).removeClass("hidden");
            $("img[name=fold_" + name + "]").attr("src", collapse_png);
        }
        else {
            $("#" + name).addClass("hidden");
            $("img[name=fold_" + name + "]").attr("src", expand_png);
        }
    });
    
    $("div.categorytitle").click( function() {
        var name = $(this).attr("name");
        if($("img[name=fold_" + name + "]").attr("src") == expand_png) {
            $("#" + name).removeClass("hidden");
            $("img[name=fold_" + name + "]").attr("src", collapse_png);
        }
        else {
            $("#" + name).addClass("hidden");
            $("img[name=fold_" + name + "]").attr("src", expand_png);
        }
    });
    
    $("div.subcategory").click( function() {
        var name = $(this).attr("name");
        var allow = true;
        if ($("img[name=" + name + "]").attr("src") == allow_png) {
            allow = false;
        }
        setSubCategoryStatus(name, allow);
    });
    
    $("div.categorystatus").click( function() {
        var name = $(this).attr("name");
        var allow = false;

        if($("img[name=" + name + "]").attr("src") == deny_png) {
            $("img[name=" + name + "]").attr("src", allow_png);
            allow = true;
        }
        else {
            $("img[name=" + name + "]").attr("src", deny_png);
            allow = false;
        }
        
        setCategoryStatus(name, allow);
    });
});