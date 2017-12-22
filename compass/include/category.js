var expand_png = "/images/expand.png";
var collapse_png = "/images/collapse.png";
var allow_png = "/images/accept.png";
var deny_png = "/images/deny.png";
var partial_png = "/images/partial.png";

function setSubCategoryStatus(subcategory, allow, setcategory) {
    var input = subcategory.find("input");
    var icon = subcategory.children("img.status");
    
    if (allow == true) {
        input.attr("value", 0);
        icon.attr("src", allow_png);
    }
    else {
        input.attr("value", 1);
        icon.attr("src", deny_png);
    }
    
    if (setcategory != false) {
        var category = subcategory.parent().prev();
        setCategoryStatus(category);
    }
}

function setCategoryStatus(category, allow, custom) {
    var allowed = 0;
    var denied = 0;
        
    category.next().children("div.subcategory").each( function() {
        if (typeof allow != "undefined") {
            setSubCategoryStatus($(this), allow, false);
            if(allow == true)
                allowed++;
            else
                denied++;
        }
        else {
            if($(this).children("img.status").attr("src") == allow_png)
                allowed++;
            else
                denied++;
        }
    });
    
    icon = category.find("img.status");
    if (allowed == 0)
        icon.attr("src", deny_png);
    else if (denied == 0)
        icon.attr("src", allow_png);
    else
        icon.attr("src", partial_png);
    if (custom != false) {
        if(typeof customCategoryStatus == 'function') {
            customCategoryStatus(category);
        }
    }
}

function toggleCategory(category) {
    category.next().toggle();
    var icon = category.find("img.toggle");
    if(icon.attr("src") == expand_png)
       icon.attr("src", collapse_png);
    else
       icon.attr("src", expand_png);
}

$(document).ready(function() {
    $("div.category-head > img.toggle").click(function() {
        toggleCategory($(this).parent());
    });
    $("div.category-head > h3.title").click(function() {
        toggleCategory($(this).parent());
    });
    
    $("div.category-head > img.status").click( function() {
        var allow = false;
        if($(this).attr("src") == deny_png)
            allow = true;
        
        setCategoryStatus($(this).parent(), allow);
    });
    
    $("div.subcategory").click( function() {
        var allow = false;
        if ($(this).children("img.status").attr("src") == deny_png)
            allow = true;
        
        setSubCategoryStatus($(this), allow);
    });
    
    $("div.category-head").each( function() {
        setCategoryStatus($(this));
    });
});