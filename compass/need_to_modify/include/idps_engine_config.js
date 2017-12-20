function update_mode( element ) {
    var transparent = document.getElementById("choose_pair_panel_for_INTERFACE_PAIR");
    var bypass      = document.getElementById("choose_panel_for_INTERFACE");
    var gateway     = document.getElementById("choose_gateway_div");
    if( element.value == 'TRANSPARENT' ) {
        transparent.style.display = "block";
        bypass.style.display = "none";
        gateway.style.display = "none";
    } else if( element.value == "BYPASS" ) {
        transparent.style.display = "none";
        bypass.style.display = "block";
        gateway.style.display = "none";
    } else if( element.value == "GATEWAY" ) {
        transparent.style.display = "none";
        bypass.style.display = "none";
        gateway.style.display = "block";
    }
}