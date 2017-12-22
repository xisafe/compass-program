/*
 * 描述: 用户显示各种消息
 * 参数：panel_config -- 添加面板所需的所有配置，具体使用见message_manager_extend.js文件
 *
 * 作者: WangLin，245105947@qq.com
 * 历史：
 *       2012.09.25 WangLin创建
 */

function MessageManager( panel_config ) {
    var message_manager = this;
    message_manager.init_panel_config( panel_config );
    message_manager.init_variable_manager();
    // message_manager.render(); //留给用户去渲染
}

MessageManager.prototype.render = function() {
    var message_manager = this;
    message_manager.display_message_box();
    message_manager.add_listeners();
}

MessageManager.prototype.init_panel_config = function( panel_config ) {
    var message_manager = this;
    message_manager.panel_config = panel_config;
    message_manager.panel_config.panel_name = panel_config.panel_name !== undefined ? panel_config.panel_name : "my_message_box";
    message_manager.panel_config.rule_title = panel_config.rule_title !== undefined ? panel_config.rule_title : "";
    message_manager.panel_config.mesg_show_time = 3000;
}

MessageManager.prototype.init_variable_manager= function() {
    var message_manager             = this;
    var panel_config                = message_manager.panel_config;
    var panel_name                  = panel_config.panel_name;
    var message_box_id              = "all_mesg_box_for_" + panel_name;
    var apply_message_box_id        = "apply_mesg_box_for_" + panel_name;
    var note_message_box_id         = "note_mesg_box_for_" + panel_name;
    var warn_message_box_id         = "warn_mesg_box_for_" + panel_name;
    var error_message_box_id        = "error_mesg_box_for_" + panel_name;
    var popup_message_box_id        = "popup_mesg_box_for_" + panel_name;
    var details_message_box_id      = "details_message_box_for_" + panel_name;
    var apply_message_box_text_id   = "apply_mesg_box_text_for_" + panel_name;
    var note_message_box_text_id    = "note_mesg_box_text_for_" + panel_name;
    var warn_message_box_text_id    = "warn_mesg_box_text_for_" + panel_name;
    var error_message_box_text_id   = "error_mesg_box_text_for_" + panel_name;
    var popup_message_box_text_id   = "popup_mesg_box_text_for_" + panel_name;
    var details_message_box_title_id= "details_message_box_title_for_" + panel_name;
    var details_message_box_text_id = "details_message_box_text_for_" + panel_name;
    var apply_message_box_button_id = "apply_mesg_box_button_for_" + panel_name;
    var popup_message_box_button_id = "popup_mesg_box_button_for_" + panel_name;
    var details_message_box_button_id = "details_message_box_button_for_" + panel_name;


    var variable_manager= {
        message_box_id: message_box_id,
        apply_message_box_id: apply_message_box_id,
        note_message_box_id: note_message_box_id,
        warn_message_box_id: warn_message_box_id,
        error_message_box_id: error_message_box_id,
        popup_message_box_id: popup_message_box_id,
        details_message_box_id: details_message_box_id,
        apply_message_box_text_id: apply_message_box_text_id,
        note_message_box_text_id: note_message_box_text_id,
        warn_message_box_text_id: warn_message_box_text_id,
        error_message_box_text_id: error_message_box_text_id,
        popup_message_box_text_id: popup_message_box_text_id,
        details_message_box_text_id: details_message_box_text_id,
        details_message_box_title_id :details_message_box_title_id,
        apply_message_box_button_id: apply_message_box_button_id,
        popup_message_box_button_id: popup_message_box_button_id,
        details_message_box_button_id: details_message_box_button_id
    }

    message_manager.variable_manager = variable_manager;
}

MessageManager.prototype.add_listeners = function() {
    var message_manager = this;
    message_manager.add_listener_to_popup_button();
    message_manager.add_listener_to_apply_button();
    message_manager.add_listener_to_details_button();
}

MessageManager.prototype.add_listener_to_details_button = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;
    var details_button_selector = "#" + variable_manager.details_message_box_button_id;
    if ( $(details_button_selector).length > 0 ) {
        $( details_button_selector).click(function(){
            message_manager.hide_details_mesg();
        });
    }
}
MessageManager.prototype.add_listener_to_popup_button = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;

    var popup_button_selector = "#" + variable_manager.popup_message_box_button_id;

    if ( $( popup_button_selector ).length > 0 ) {
        $( popup_button_selector).click(function(){
            message_manager.hide_popup_mesg();
        });
    }
}

MessageManager.prototype.add_listener_to_apply_button = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;

    var apply_button_selector = "#" + variable_manager.apply_message_box_button_id;

    if ( $( apply_button_selector ).length > 0 ) {
        $( apply_button_selector).click(function(){
            message_manager.apply_data();
        });
    }
}

MessageManager.prototype.display_message_box = function() {
    var message_manager = this;

    var message_box = "";
    message_box += '<div id="all-mesg-box" class="all-mesg-box">';
    message_box += message_manager.create_apply_message_box();
    message_box += message_manager.create_note_message_box();
    message_box += message_manager.create_warn_message_box();
    message_box += message_manager.create_error_message_box();
    message_box += message_manager.create_popup_message_box();
    message_box += message_manager.create_details_message_box();
    message_box += '</div>';

    var check_in_selector = "#" + message_manager.panel_config.check_in_id;
    $( check_in_selector ).empty();
    $( check_in_selector ).html( message_box );
}

MessageManager.prototype.create_apply_message_box = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;
    var apply_message_box = "";
    apply_message_box += '<div id="' + variable_manager.apply_message_box_id + '" class="mesg-box apply-mesg-box">' +
                            '<div class="mesg-box-main">' +
                                '<img src="/images/pop_apply.png">' +
                                '<span id="' + variable_manager.apply_message_box_text_id + '" class="mesg-body">规则已改变,需应用该规则以使改变生效</span>' +
                            '</div>' +
                            '<div class="mesg-box-foot">' +
                                '<input  id="' + variable_manager.apply_message_box_button_id + '" type="button" class="net_button" value="应用"/>' +
                            '</div>' +
                        '</div>';

    return apply_message_box;
}

MessageManager.prototype.create_note_message_box = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;

    var note_message_box = "";
    note_message_box += '<div id="' + variable_manager.note_message_box_id + '" class="mesg-box tips-mesg-box note-mesg-box">' +
                            '<img src="/images/Emoticon.png">' +
                            '<span id="' + variable_manager.note_message_box_text_id + '" class="mesg-body">操作成功</span>' +
                        '</div>';

    return note_message_box;
}

MessageManager.prototype.create_warn_message_box = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;

    var warn_message_box = "";
    warn_message_box += '<div id="' + variable_manager.warn_message_box_id + '" class="mesg-box tips-mesg-box warn-mesg-box">' +
                            '<img src="/images/pop_warn.png">' +
                            '<span id="' + variable_manager.warn_message_box_text_id + '" class="mesg-body">操作有误</span>' +
                        '</div>';

    return warn_message_box;
}

MessageManager.prototype.create_error_message_box = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;

    var error_message_box = "";
    error_message_box += '<div id="' + variable_manager.error_message_box_id + '" class="mesg-box tips-mesg-box error-mesg-box">' +
                            '<img src="/images/pop_error.png">' +
                            '<span id="' + variable_manager.error_message_box_text_id + '" class="mesg-body">操作失败</span>' +
                        '</div>';

    return error_message_box;
}

MessageManager.prototype.create_popup_message_box = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;
    var mesg_box = "";
    mesg_box += '<div id="' + variable_manager.popup_message_box_id + '" class="hidden">';
    mesg_box +=     '<div class="popup-mesg-box-cover popup-short-mesg-box-cover"></div>';
    mesg_box +=     '<div class="popup-short-mesg-box-body">';
    mesg_box +=         '<div class="popup-short-mesg-text-area">' +
                            '<div id="' + variable_manager.popup_message_box_text_id + '" class="popup-short-mesg-text"></div>' +
                        '</div>';
    mesg_box +=         '<div class="popup-short-mesg-buttons">';
    mesg_box +=             '<button id="' + variable_manager.popup_message_box_button_id + '" class="popup-short-mesg-button">' +
                                '<span class="popup-short-mesg-button-text">确定</span>' +
                            '</button>';
    mesg_box +=         '</div>';
    mesg_box +=     '</div>';
    mesg_box += '</div>';
    return mesg_box;
}
MessageManager.prototype.create_details_message_box = function() {
    var message_manager = this;
    var variable_manager = message_manager.variable_manager;
    var self_class = (message_manager.panel_config.self_class !== undefined) ? message_manager.panel_config.self_class : "";

    var panel_config  = message_manager.panel_config;
    var mesg_box = "";
    mesg_box += '<div id="' + variable_manager.details_message_box_id + '"class="hidden">';
    mesg_box += '<div class="popup-mesg-box-cover popup-short-mesg-box-cover popup-short-mesg-box-cover"></div>';
    mesg_box +=     '<div class="details-mesg-box-body '+ self_class +'">';
    mesg_box +=         '<div class= "details-mesg-box-title-area">'+
                            '<div id="'+variable_manager.details_message_box_title_id + '" class="details-mesg-box-title"></div>' +
                        '</div>';
    mesg_box +=         '<div class="popup-short-mesg-text-area">' +
                            '<div id="' + variable_manager.details_message_box_text_id + '" class="popup-short-mesg-text"></div>' +
                        '</div>';
    mesg_box +=         '<div class="popup-short-mesg-buttons">';
    mesg_box +=             '<button id="' + variable_manager.details_message_box_button_id + '" class="popup-short-mesg-button">' +
                                '<span class="popup-short-mesg-button-text">确定</span>' +
                            '</button>';
    mesg_box +=         '</div>';
    mesg_box +=     '</div>';
    mesg_box += '</div>';
    return mesg_box;
}
MessageManager.prototype.show_details_message = function( mesg,isHtml ) {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var details_name = panel_config.rule_title;
    var variable_manager = message_manager.variable_manager;
    var details_message_box_selector = "#" + variable_manager.details_message_box_id;
    var details_message_box_text_selector = "#" + variable_manager.details_message_box_text_id;
    var details_message_box_title_selector = "#" + variable_manager.details_message_box_title_id;
    $( details_message_box_title_selector).text(details_name);
    if( isHtml !== undefined){
        $( details_message_box_text_selector ).html(mesg);
    }else{
        $( details_message_box_text_selector ).text(mesg);
    }
    $( details_message_box_selector ).show(); 
}
MessageManager.prototype.hide_details_mesg = function () {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;
    var details_message_box_selector = "#" + variable_manager.details_message_box_id;
    var details_message_box_text_selector = "#" + variable_manager.details_message_box_text_id;
    $( details_message_box_text_selector ).text( "" );
    $( details_message_box_selector ).hide();
}
MessageManager.prototype.show_apply_mesg = function( mesg ) {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;

    var apply_message_box_selector = "#" + variable_manager.apply_message_box_id;
    var apply_message_box_text_selector = "#" + variable_manager.apply_message_box_text_id;

    $( apply_message_box_text_selector ).text( mesg );
    $( apply_message_box_selector ).show();
}

MessageManager.prototype.hide_apply_mesg = function() {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;

    var apply_message_box_selector = "#" + variable_manager.apply_message_box_id;
    var apply_message_box_text_selector = "#" + variable_manager.apply_message_box_text_id;

    $( apply_message_box_text_selector ).text( "" );
    $( apply_message_box_selector ).hide();
}

MessageManager.prototype.show_note_mesg = function( mesg ) {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;

    var note_message_box_selector = "#" + variable_manager.note_message_box_id;
    var note_message_box_text_selector = "#" + variable_manager.note_message_box_text_id;

    $( note_message_box_text_selector ).text( mesg );
    $( note_message_box_selector ).show();

    var fadeOut = "$('" + note_message_box_selector + "').fadeOut( 'slow' )";
    window.setTimeout( fadeOut, panel_config.mesg_show_time );
}

MessageManager.prototype.show_warn_mesg = function( mesg ) {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;

    var warn_message_box_selector = "#" + variable_manager.warn_message_box_id;
    var warn_message_box_text_selector = "#" + variable_manager.warn_message_box_text_id;

    $( warn_message_box_text_selector ).text( mesg );
    $( warn_message_box_selector ).show();

    var fadeOut = "$('" + warn_message_box_selector + "').fadeOut( 'slow' )";
    window.setTimeout( fadeOut, panel_config.mesg_show_time );
}

MessageManager.prototype.show_error_mesg = function( mesg ) {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;

    var error_message_box_selector = "#" + variable_manager.error_message_box_id;
    var error_message_box_text_selector = "#" + variable_manager.error_message_box_text_id;

    $( error_message_box_text_selector ).text( mesg );
    $( error_message_box_selector ).show();

    var fadeOut = "$('" + error_message_box_selector + "').fadeOut( 'slow' )";
    window.setTimeout( fadeOut, panel_config.mesg_show_time );
}

MessageManager.prototype.show_popup_mesg = function( mesg ,isHtml) { /*ishtml是否用innerHtml方式*/
    var message_manager = this;
    message_manager.show_popup_note_mesg( mesg ,isHtml);
}

MessageManager.prototype.show_popup_note_mesg = function( mesg ,isHtml) {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;

    var popup_message_box_selector = "#" + variable_manager.popup_message_box_id;
    var popup_message_box_text_selector = "#" + variable_manager.popup_message_box_text_id;
    if( isHtml !== undefined){
        $( popup_message_box_text_selector ).html( mesg );
    }else{
        $( popup_message_box_text_selector ).text( mesg );
    }
    $( popup_message_box_text_selector ).removeClass("popup-short-mesg-alert-mesg");
    $( popup_message_box_text_selector ).addClass("popup-short-mesg-note-mesg");
    $( popup_message_box_selector ).show();
}


MessageManager.prototype.show_popup_error_mesg = function( mesg ) {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;

    var popup_message_box_selector = "#" + variable_manager.popup_message_box_id;
    var popup_message_box_text_selector = "#" + variable_manager.popup_message_box_text_id;

    $( popup_message_box_text_selector ).text( mesg );
    $( popup_message_box_text_selector ).removeClass("popup-short-mesg-note-mesg");
    $( popup_message_box_text_selector ).addClass("popup-short-mesg-alert-mesg");
    $( popup_message_box_selector ).show();
}

MessageManager.prototype.hide_popup_mesg = function() {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var variable_manager = message_manager.variable_manager;

    var popup_message_box_selector = "#" + variable_manager.popup_message_box_id;
    var popup_message_box_text_selector = "#" + variable_manager.popup_message_box_text_id;

    $( popup_message_box_text_selector ).text( "" );
    $( popup_message_box_selector ).hide();
}

MessageManager.prototype.apply_data = function() {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var panel_name = panel_config.panel_name;

    var sending_data = {
        ACTION: 'apply_data',
        panel_name: panel_name
    }

    function ondatareceived( data ) {
        if( message_manager.is_operation_succeed( data ) ) {
            message_manager.show_note_mesg( "应用成功" );
            message_manager.hide_apply_mesg();
        } else {
            message_manager.show_error_mesg( "应用失败" );
        }
    }

    message_manager.request_for_json( sending_data, ondatareceived );
}

MessageManager.prototype.request_for_json = function( sending_data, ondatareceived ) {
    var message_manager = this;
    var panel_config = message_manager.panel_config;
    var url = panel_config.url;
    $.ajax({
        type: 'POST',
        url: url,
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            message_manager.show_error_mesg("返回数据格式有误,请检查");
        },
        success: ondatareceived
    });
}

MessageManager.prototype.is_operation_succeed = function( data ) {
    if( data.status == 0 ) {
        return true;
    } else {
        return false
    }
}