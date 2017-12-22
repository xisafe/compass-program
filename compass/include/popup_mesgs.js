function show_popup_mesg(mesg){
    if($("#popup-short-mesg-box").length > 0) {
        $("#popup-short-mesg-text").html(mesg);
        $("#popup-short-mesg-text").removeClass("alert-mesg");
        $("#popup-short-mesg-text").addClass("note-mesg");
        $("#popup-short-mesg-box").show();
    } else {
        $('body').append(create_popup_mesg_box(mesg));
        $("#popup-short-mesg-text").addClass("note-mesg");
    }
}

function show_popup_long_mesg(mesgs) {
    var mesg = "";
    for( var i = 0; i < mesgs.length; i++ ) {
        mesg += '<p>' + mesgs[i] + '</p>';
    }
    show_popup_mesg(mesg);
}

function show_popup_alert_mesg(mesg) {
    if($("#popup-short-mesg-box").length > 0) {
        $("#popup-short-mesg-text").html(mesg);
        $("#popup-short-mesg-text").removeClass("note-mesg");
        $("#popup-short-mesg-text").addClass("alert-mesg");
        $("#popup-short-mesg-box").show();
    } else {
        $('body').append(create_popup_mesg_box(mesg));
        $("#popup-short-mesg-text").addClass("alert-mesg");
    }
}

function show_popup_long_alert_mesg(mesgs) {
    var mesg = "";
    for( var i = 0; i < mesgs.length; i++ ) {
        mesg += '<p>' + mesgs[i] + '</p>';
    }
    show_popup_alert_mesg(mesg);
}

function hide_popup_mesg() {
    $("#popup-short-mesg-box").hide();
}

function create_popup_mesg_box(mesg) {
    var mesg_box = "";
    mesg_box += '<div id="popup-short-mesg-box">';
    mesg_box += '<div class="popup-short-mesg-box-cover"></div>';
    mesg_box += '<div class="popup-short-mesg-box-body">';
    mesg_box += '<div class="popup-short-mesg-text-area">' + '<div id="popup-short-mesg-text" class="popup-short-mesg-text">' +mesg + '</div></div>';
    mesg_box += '<div class="popup-short-mesg-buttons">';
    mesg_box += '<button class="popup-short-mesg-button" onclick="hide_popup_mesg();"><span class="button-text">确定</span></button>';
    // if(type != "alert") {
    //     mesg_box += '<button class="popup-short-mesg-button"><span class="button-text">取消</span></button>';
    // }
    mesg_box += '</div>';
    mesg_box += '</div>';
    mesg_box += '</div>';
    return mesg_box;
}