$(document).ready(function(){
    register_listeners();
});

function register_listeners() {
    $( "#edit_passwd_button" ).click( show_edit_passwd );
}

function show_edit_passwd() {

    var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
    mainframe.document.getElementById("eidt_passwd_bg").setAttribute('class','open-dialog__overlay')
    mainframe.document.getElementById("eidt_passwd_bg").style.display = 'block';
    mainframe.document.getElementById("eidt_passwd_body").style.display = "block";
    mainframe.document.getElementById("eidt_passwd_bbb").setAttribute('class','open--eidt_passwd_bbb');
    mainframe.document.getElementById("eidt_passwd_bbb").style.display = 'block';
    var edit_passwd_height = mainframe.document.getElementById("eidt_passwd_body").offsetHeight;
    mainframe.document.getElementById("eidt_passwd_bbb").style.height = edit_passwd_height + 'px';

    var bottomframe = window.parent.parent.document.getElementById("bottomFrame").contentWindow;
    bottomframe.document.getElementById("div_lock_footer").style.display = "block";
    var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;
    topframe.document.getElementById("div_lock_top").style.display = "block";

    var cover_height = parseInt(mainframe.document.getElementById("eidt_passwd_bg").offsetHeight);
    var cover_width = parseInt(mainframe.document.getElementById("eidt_passwd_bg").offsetWidth);

    var border_height = parseInt(mainframe.document.getElementById("eidt_passwd_bbb").offsetHeight);
    var border_width = parseInt(mainframe.document.getElementById("eidt_passwd_bbb").offsetWidth);

    var temp_top = (cover_height - border_height)/2 - 78;
    var temp_left = (cover_width - border_width)/2;

    mainframe.document.getElementById("eidt_passwd_bbb").style.top = temp_top + 'px';
    mainframe.document.getElementById("eidt_passwd_bbb").style.marginTop = 0 + 'px';
    mainframe.document.getElementById("eidt_passwd_bbb").style.left = temp_left + 'px';
    mainframe.document.getElementById("eidt_passwd_bbb").style.marginLeft = 0 + 'px';
}