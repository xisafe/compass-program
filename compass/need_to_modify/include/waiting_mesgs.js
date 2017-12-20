function show_waiting_mesg(mesg){
    if($("#waiting-mesg-box").length > 0) {
        $("#popup-waiting-mesg-text").html(mesg);
        $("#waiting-mesg-box").show();
    } else {
        $('body').append(create_waiting_mesg_box(mesg));
    }
}

function hide_waiting_mesg() {
    $("#waiting-mesg-box").hide();
}

function create_waiting_mesg_box(mesg) {
    var mesg_box = "";
    mesg_box += '<div id="waiting-mesg-box">';
    mesg_box += '<div class="popup-waiting-cover"></div>';
    mesg_box += '<div class="popup-waiting-mesg-box">';
    mesg_box += '<img src="/images/waiting.gif"/>';
    mesg_box += '<span id="popup-waiting-mesg-text" class="popup-waiting-mesg-text">' + mesg + '</span>';
    mesg_box += '</div>';
    mesg_box += '</div>';
    return mesg_box;
}