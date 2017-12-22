function check_running() {
    var sending_data = {
        ACTION: 'check_running'
    }

    function ondatareceived( response ) {
        if ( response.running ) {
            // 隐藏应用框
            $( ".apply-mesg-box" ).hide();
            $( "#pop-apply-div" ).hide();
            if ( typeof RestartService == 'function' ) {
                RestartService( "正在应用更改..." );
            }
            window.setTimeout( check_running, 1000 );
        } else {
            if ( response.reload ) {
                $( ".apply-mesg-box" ).show();
                $( "#pop-apply-div" ).show();
            } else {
                $( ".apply-mesg-box" ).hide();
                $( "#pop-apply-div" ).hide();
            }
            if ( typeof endmsg == 'function' ) {
                endmsg( "应用成功" );
            }
        }
    }

    check_running_request_for_json( sending_data, ondatareceived );
}

check_running_request_for_json = function( sending_data, ondatareceived ) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/ips_check_running.cgi",
        data: sending_data,
        dataType: 'json',
        async: true,
        success: ondatareceived
    });
}