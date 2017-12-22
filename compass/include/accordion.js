var expand_png = "/images/expand.png";
var collapse_png = "/images/collapse.png";

$(document).ready(function() {
    $("div.accordion-toggle").click(function() {
        $(this).parent().next().toggle();
        var icon = $(this).find("img.toggle");
        if(icon.attr("src") == expand_png)
           icon.attr("src", collapse_png);
        else
           icon.attr("src", expand_png);
    });
});