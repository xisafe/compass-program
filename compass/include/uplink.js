if(typeof console == 'undefined') {
    var console = { 'log': function() {}}
}

var uplink_colors = {'offline' : '#993333',
                     'online' : '#339933',
                     'pending' : '#FF9933',
                     'unmanaged' : '#666666'}
/* mapping status to color */
var status_color = {'DEAD' : uplink_colors['pending'],
                    'INACTIVE' : uplink_colors['offline'],
                    'ACTIVE' : uplink_colors['online'],
                    'CONNECTING' : uplink_colors['pending'],
                    'DISCONNECTING' : uplink_colors['pending'],
                    'FAILURE' : uplink_colors['pending']    
}
/* defines whether a current status request is running or not, if
 * so, no further status request is fired
 */
var RUNNING_STATUS_REQUEST = false;
var UPLINKS_SCRIPT = '/cgi-bin/uplinks-status.cgi'

function statusToColor(status) {
    if(status) return uplink_colors['online'];
    return uplink_colors['offline']
}

function installUplinksActions() {
    $('.uplink-switch').each(function(i, o) {
        $(o).click(function() {
            /* OUTDATED: If the uplink is in connecting state, a click should be prevented.
             * A click is allowed, since the user should be able to stop the connection
             * at any point 
             */
            $(o).attr('src', '/images/indicator.gif');
            var row = $(o).parent().parent();
            var status_col = $('.uplink-color', row);
            var action_col = $('.uplink-action', row);
            var status = $('.uplink-status', action_col);
            var uplink = $('.uplink', action_col);
            var matched_uplinks = $('.uplink-name-' + uplink.val());
            var status_col = $('.uplink-color', matched_uplinks);
            var backup_col = $('.link-type', matched_uplinks);
            /* setting status color and description */
            status_col.css('background-color', uplink_colors['pending']);
            backup_col.css('background-color', uplink_colors['pending']);
            var action = status.val() == "Disconnect" ? "stop" : "start";
            changeStatusText(status_col, "pending", action);
            
            RUNNING_STATUS_REQUEST = true;
            /* If the uplink is being activated or deactivated, changing the managed
             * status causes the manage status to be dismissed, since the activating
             * process may return at a latter point, which revokes the previous change
             * of the manage status.
             * Hence the manage button is hidden if the de/activating button is running.
             */
            $('.uplink-switch-managed', matched_uplinks).hide();
            $.post(UPLINKS_SCRIPT, 
                   {'action' : action, 'uplink' : uplink.val()},
                   function(response) {
                       var obj = responseToObject(response);
                       /* Changing the image */
                       changeImage($(o), obj, function () {
                           return isAlive(obj);
                       });
                       
                       color = status_color[obj.status];
                       status_col.css('background-color', color);
                       backup_col.css('background-color', color);
                       
                       var action = isAlive(obj) ? "on" : "off";
                       if(action == "off" && obj.managed == "off") action="stopped";
                       action = obj.status == 'FAILURE' ? 'failure' : (obj.status == 'DEAD' ? 'dead' : (obj.status == 'INACTIVE' && isBackupLink(obj, row) ? 'hold' : action))
                       changeStatusText(status_col, action, null, obj);
                       setAction(status, isAlive(obj) ? "on" : "off");
                       updateUptime(matched_uplinks, obj)
                       setUplinkData(matched_uplinks, obj);
                       RUNNING_STATUS_REQUEST = false;
                       $('.uplink-switch-managed', matched_uplinks).show();
                       $('#abort-message').fadeOut(500);
                   });
                   /* Displaying the notification that the connection can be stopped by clicking
                    * on the spinner image
                    */
                  $('#abort-message').fadeIn(500);
            });

    })
    $('.uplink-switch-managed').each(function(i, o) {
        $(o).click(function() {
            
            var row = $(o).parent().parent();
            var status_col = $('.uplink-color', row);
            var action_col = $('.uplink-action', row);
            var managed = $('.uplink-managed', action_col);
            var uplink = $('.uplink', action_col);
            var matched_uplinks = $('.uplink-name-' + uplink.val());
            var managed_icon = $('.uplink-switch-managed', matched_uplinks);
            var managed_text = $('.uplink-managed', matched_uplinks);
            var switch_image = $('.uplink-switch', matched_uplinks);
            
            var action = managed.val() == "off" ? "unmanage" : "manage"
            /* Starting the spinner */
            managed_icon.attr('src', '/images/indicator.gif');
            $.post(UPLINKS_SCRIPT,
                   {'action' : action, uplink : uplink.val()},
                   function(response) {
                       var obj = responseToObject(response);
                       /* Switching image */
                       changeImage(managed_icon, obj, function() {
                           return isManaged(obj);
                       });
                       /* Switching status */
                       managed_text.val(obj.managed == "on" ? "off" : "on");
                       if(obj.managed == "on") switch_image.hide();
                       else
                            switch_image.show();
                   });
            
        })
    });
}

function isManaged(uplink) {
    return (uplink.managed == "on");
}

function isAlive(uplink) {
    return (uplink.status == "ACTIVE" || uplink.status == "DEAD"); 
}

function isBackupLink(obj, row) {
    return obj.managed == 'on' && row.hasClass("backup-link")
}

function setAction(status, action) {
    if(action == "on") status.val('Disconnect');
    else status.val('Connect');
}

function changeImage(container, response, status_func) {
    var tmp_stat = status_func();
    if(tmp_stat) {
        container.attr('src', "/images/on.png");
    }
    else {
        container.attr('src', "/images/off.png");
    }
}

function changeStatusText(status, stat, c_stat, obj) {
    var c_stat = typeof c_stat == "undefined" ? null : c_stat;
    var obj = typeof obj == "undefined" ? null : obj;
    /* hiding the descriptions */
    $('.uplink-status-text', status).hide();
    
    if(stat == "pending") {
        if(c_stat == "start") 
            $('.uplink-status-connect', status).show()
        else
            $('.uplink-status-disconnect', status).show()
    }
    else if(stat == "on") {
        $('.uplink-status-on', status).show()
    }
    else if(stat == "off") {
        $('.uplink-status-off', status).show();
    }
    else if(stat == "stopped") {
        $('.uplink-status-stopped', status).show();
    }
    else if(stat == "failure") {
        $('.status-text', $('.uplink-status-off', status)).html($('#failure').html());
        if(obj.data.last_retry != '') {
            $('.uplink-last-retry', $('.uplink-status-off', status)).html(obj.data.last_retry);
            $('.uplink-last-retry', $('.uplink-status-off', status)).show();
        }
        $('.uplink-status-off', status).show();
    }
    else if(stat == "dead") {
        $('.status-text', $('.uplink-status-off', status)).html($('#dead').html());
        $('.uplink-status-off', status).show();
    }
    else if(stat == "hold") {
        $('.status-text', $('.uplink-status-off', status)).html($('#onhold').html());
        $('.uplink-status-off', status).show();
    }
}

function updateUptime(uplink_row, uplink) {
    if(isAlive(uplink)) {
        $('.uplink-uptime', uplink_row).html(" - " + uplink.uptime).show();
    }
        
}

function inA(status, status_list) {
    var i = 0;
    for(i = 0; i < status_list.length; i++) {
        if(status_list[i] == status) return true;
    }
    return false;
}

var uplinks = null;
function statusCheck() {
    /* Retrieving uplinks statuses */
    $.post('/cgi-bin/uplinks-status.cgi', {'action' : 'list'}, function(response) {
        if(RUNNING_STATUS_REQUEST) {
            setTimeout("statusCheck()", 10000);
            return false;
        }
        uplinks = responseToObject(response);
        $('.uplink-item').each(function(i, o) {
            var name = $('.uplink', $(o)).val();
            var uplink = uplinkByName(name);
            if(uplink) {
                color = status_color[uplink.status];
                $('.uplink-color', $(o)).css('background-color', color);
                $('.link-type', $(o)).css('background-color', color);
                
                var stat = isAlive(uplink) ? "on" : "off"
                var image = $('.uplink-switch', $(o));
                if(uplink.managed == "off") {
                    image.show();
                }
                else {
                    image.hide();
                }
                
                changeImage(image, uplink, function() {
                    return isAlive(uplink);
                });
                
                if(inA(uplink.status, ["CONNECTING", "DISCONNECTING"])) {
                    changeStatusText($('.uplink-color', $(o)), "pending", (uplink.status == "CONNECTING" ? "start" : "stop"))
                    image.attr('src', '/images/indicator.gif');
                }
                else {
                    var row = $(o);
                    stat = uplink.status == 'FAILURE' ? 'failure' : (uplink.status == 'DEAD' ? 'dead' : (uplink.status == 'INACTIVE' && isBackupLink(uplink, row) ? 'hold' : stat))
                    changeStatusText($('.uplink-color', $(o)), stat, null, uplink);
                }
                setAction($('.uplink-status', $(o)), isAlive(uplink) ? "on" : "off");
                updateUptime($(o), uplink);
                setUplinkData($(o), uplink);
            }
        });
        setTimeout("statusCheck()", 5000);
    });
}

function get(data, optional) {
    if(typeof data == 'undefined' || data == null) return optional;
    return data;
}

function setUplinkData(obj, uplink) {
    $('.type', $(obj)).html(get(uplink.data.type, $('#NA').text()));
    $('.interface', $(obj)).html(get(uplink.data.interface, $('#NA').text()));
    $('.ip', $(obj)).html(get(uplink.data.ip, $('#NA').text()));
    $('.gateway', $(obj)).html(get(uplink.data.gateway, $('#NA').text()));
}

function uplinkByName(name) {
    var chain = uplinks
    for(i = 0; i < chain.length; i++) {
        if(chain[i].name == name) return chain[i];
    }
    return null;
}

function initStatusCheck() {
    try {
        statusCheck();
    }
    catch(e) {
        //console.log(e);
    }

}

function responseToObject(response) {
    try {
        var obj = eval("(" + response + ")")
    }
    catch(e) {
    }
    return obj;
}

function initUp() {
    $('#abort-message').hide();
    installUplinksActions();
    initStatusCheck();
}
$(document).ready(function() {
    initUp();
})