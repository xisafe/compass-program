if(typeof console == 'undefined') {
    var console = { 'log': function() {}}
}

function resetForm() {
   $(".form").each(function() {
       if ($(this).is("input") && $(this).attr("type") == "checkbox") {
           if ($(this).attr("name") == "ENABLED")
               $(this).attr("checked", "checked");
           else
               $(this).get(0).checked = false;
       }
       else if ($(this).is("textarea"))
           $(this).attr("value", "");
       else if ($(this).is("select"))
           $(this).get(0).selectedIndex = 0;
       else
           $(this).attr("value", "");
   });
   if (typeof customResetForm != "undefined")
        customResetForm();
}

function loadForm(id) {
    $(".form").each(function() {
        var name = $(this).attr("name");
        var value = $("input." + id + "[name=" + name + "]").attr("value");
        var field = $(this);
        if (typeof value == "undefined")
            value = "";
        if (field.is("input") && field.attr("type") == "checkbox") {
            if (value == "off" || value == "" || typeof value == "undefined")
                field.get(0).checked = false;
            else
                field.attr("checked", "checked");
        }
        else if (field.is("textarea")) {
            while(value.indexOf(',') != -1)
               value = value.replace(',', '\n');
            field.attr("value", value);
        }
        else if (field.is("select"))
            field.selectOptions(value);
        else
            field.attr("value", value);
    });
    if (typeof customLoadForm != "undefined")
         customLoadForm();
}

function showForm(name) {
    if (typeof name == "undefined") {
        $("div.editorbox").removeClass("hidden");
        $("div.editoradd").addClass("hidden");
        $("div.editorerror").addClass("hidden");
    }
    else {
        $("div.editorbox[@name=" + name + "]").removeClass("hidden");
        $("div.editoradd[@name=" + name + "]").addClass("hidden");
        $("div.editorerror[@name=" + name + "]").addClass("hidden");
    }
    if (typeof customShowForm != "undefined")
         customShowForm();
}

function hideForm(name) {
    $("div.editorbox[@name=" + name + "]").addClass("hidden");
    $("div.editoradd[@name=" + name + "]").removeClass("hidden");
    $("div.editorerror[@name=" + name + "]").removeClass("hidden");
}

function cancelForm() {
    var id = $("input.form[name=ID]").attr("value");
    var color = $("input." + id + "[name=rowcolor]").attr("value");
    $("#row_" + id).attr("class", color);
}

$(document).ready(function() {
    $("a.editoradd").click( function() {
        resetForm();
        showForm($(this).attr("name"));
    });
    $("a.editorcancel").click( function() {
        hideForm($(this).attr("name"));
        cancelForm();
    });
});
