/*
 * 描述: 用于创建展示信息的面板
 * 参数：panel_config -- 信息面板所需的所有配置，具体使用见info_panel_extend.js文件
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2015.10.15 WangLin创建
 */

function InfoDisplayPanel(panel_config) {
    /* 第一步，初始化本panel_config */
    this.init_panel_config( panel_config );
    this.init_panel_control_variable();
}

InfoDisplayPanel.prototype.render = function() {
    var infoDisplayPanel = this;

    /* 第一步，创建面板 */
    infoDisplayPanel.display_info_panel();
    /* 第二步，增加监听 */
    infoDisplayPanel.add_listener_to_panel_buttons();
}

InfoDisplayPanel.prototype.init_panel_config = function( panel_config ) {
    var infoDisplayPanel = this;
    infoDisplayPanel.panel_config = panel_config;

    panel_config.panel_name = panel_config.panel_name !== undefined ? panel_config.panel_name : "my_info_panel";
    /* 默认是“true”，表示标题前面的图标是否显 */
    panel_config.is_panel_title_icon = panel_config.is_panel_title_icon !== undefined ? panel_config.is_panel_title_icon : true;
    panel_config.panel_title_icon = panel_config.panel_title_icon !== undefined ? panel_config.panel_title_icon : "info.png";
    panel_config.panel_title = panel_config.panel_title !== undefined ? panel_config.panel_title : "信息";
    panel_config.is_panel_closable = panel_config.is_panel_closable !== undefined ? panel_config.is_panel_closable : false;
    panel_config.is_modal = panel_config.is_modal !== undefined ? panel_config.is_modal : false;
    panel_config.columns = panel_config.columns !== undefined ? ( parseInt(panel_config.columns) > 0 ? parseInt(panel_config.columns) : 2 ) : 2;
    panel_config.label_width = panel_config.label_width !== undefined ? ( parseFloat(panel_config.label_width) > 0 ? parseFloat(panel_config.label_width) : 3 ) : 3;
    panel_config.value_width = panel_config.value_width !== undefined ? ( parseFloat(panel_config.value_width) > 0 ? parseFloat(panel_config.value_width) : 7 ) : 7;
;
}

InfoDisplayPanel.prototype.init_panel_control_variable = function() {
    var infoDisplayPanel  = this;
    var panel_name      = infoDisplayPanel.panel_config.panel_name;

    var panel_id            = "info_panel_id_for_" + panel_name;
    var panel_header_id     = "info_panel_header_id_for_" + panel_name;
    var panel_title_id      = "info_panel_title_for_" + panel_name;
    var panel_title_img_id  = "info_panel_title_img_for_" + panel_name;
    var panel_title_text_id = "info_panel_title_text_for_" + panel_name;
    var panel_close_id      = "info_panel_close_for_" + panel_name;
    var panel_body_id       = "info_panel_body_id_for_" + panel_name;
    var data_item_class     = "info_panel_info_label_class_for" + panel_name;

    var panel_control = {
        panel_id: panel_id,
        panel_header_id: panel_header_id,
        panel_title_id: panel_title_id,
        panel_title_img_id: panel_title_img_id,
        panel_title_text_id: panel_title_text_id,
        panel_close_id: panel_close_id,
        panel_body_id: panel_body_id,
        data_item_class: data_item_class
    }

    infoDisplayPanel.panel_control = panel_control;
}

InfoDisplayPanel.prototype.display_info_panel = function() {
    var infoDisplayPanel = this;
    var panel_config = infoDisplayPanel.panel_config;
    var panel_control = infoDisplayPanel.panel_control;
    var info_panel = "";

    info_panel += '<div id="' + panel_control.panel_id + '" class="add-panel">';
    info_panel += infoDisplayPanel.create_panel_header();
    info_panel += infoDisplayPanel.create_panel_body();

    info_panel += '</div>';

    if ( panel_config.is_modal ) {
        info_panel = infoDisplayPanel.get_modaled_panel( info_panel );
    }
    var check_in_selector = "#" + panel_config.check_in_id;
    $( check_in_selector ).empty();
    $( check_in_selector ).html( info_panel );

    if ( panel_config.is_modal ) {
        /* 上下居中渲染 */
        var popup_body_selector = "#" + panel_config.check_in_id + " .popup-mesg-box-body";
        var popup_body = $( popup_body_selector );
        var body_height = $( popup_body ).height();
        var margin_top = - body_height / 2;
        $( popup_body_selector ).css( "margin-top", margin_top );
    }
}

InfoDisplayPanel.prototype.create_panel_header = function() {
    var infoDisplayPanel = this;
    var panel_control = infoDisplayPanel.panel_control;
    var panel_config = infoDisplayPanel.panel_config;
    var panel_title = panel_config.panel_title;
    var panel_title_icon = '/images/' + panel_config.panel_title_icon;

    var panel_header = "";
    panel_header +=  '<div id="' + panel_control.panel_header_id + '" class="add-panel-header">' +
                        '<div id="' + panel_control.panel_title_id + '" class="add-panel-title">';
    if( panel_config.is_panel_title_icon ) {
        panel_header +=      '<img id="' + panel_control.panel_title_img_id + '" src="' + panel_title_icon + '"/>';
    }
        panel_header +=      '<span id="' + panel_control.panel_title_text_id + '" class="add-panel-title-text">' + panel_title + '</span>' +
                        '</div>';
    if( panel_config.is_panel_closable ) {
        panel_header +=  '<span id="' + panel_control.panel_close_id + '" class="add-panel-close-button"></span>'
    }
    panel_header +=  '</div>';

    return panel_header;
}

InfoDisplayPanel.prototype.create_panel_body = function() {
    var infoDisplayPanel = this;
    var panel_control = infoDisplayPanel.panel_control;
    var panel_config = infoDisplayPanel.panel_config;
    var items_list = panel_config.items_list;
    var columns = panel_config.columns;

    var panel_body = "";
    panel_body +=   '<div id="' + panel_control.panel_body_id + '" class="add-panel-content">' ;

    var container_class = 'container-main-body';
    if ( panel_config.modal_config !== undefined ) {
            var modal_config = panel_config.modal_config;
            if ( modal_config.modal_box_size !== undefined ) {
                container_class += ' ' + "container-main-body-" + modal_config.modal_box_size;
            }
    }
    panel_body +=           '<div class="' + container_class + '">' +
                                '<table>' +
                                    '<tbody>';
    var initItemsLength = items_list.length;
    if ( items_list.length % columns != 0 ) {
        for ( var i = 0; i < (columns - initItemsLength % columns); i++ ) {
            var item = {
                label: "",
                value: "",
            }
            items_list.push( item );
        }
    }
    for ( var i = 0; i < items_list.length; i++ ) {
        var items_list_item = items_list[i];

        if ( i % columns == 0 ) {
            var bgcolor = "add-panel-even-line";
            if( i % ( 2 * columns ) == 0 ) {
                bgcolor = "add-panel-odd-line"
            }
            panel_body += '<tr class="' + bgcolor + '">';
        }
         panel_body += infoDisplayPanel.create_panel_line_cell(items_list_item);
        if ( i % columns == (columns -1) ) {
            panel_body += '</tr>'
        }
    }

    panel_body +=                   '</tbody>' +
                                '</table>' +
                            '</div>';
    panel_body +=           infoDisplayPanel.create_panel_footer();
    panel_body +=   '</div>';

    return panel_body;
}

InfoDisplayPanel.prototype.create_panel_line_cell = function( item ) {
    var infoDisplayPanel = this;
    var panel_config = infoDisplayPanel.panel_config;
    var panel_control = infoDisplayPanel.panel_control;
    var columns = panel_config.columns;

    var title_width_scale = panel_config.label_width / ( panel_config.label_width + panel_config.value_width );
    var section_width_scale = panel_config.value_width / ( panel_config.label_width + panel_config.value_width );
    var title_width = ( 100 / columns * title_width_scale );
    var section_width = ( 100 / columns * section_width_scale );

    var panel_line_cell = "";
    panel_line_cell +=  '<td class="add-panel-subtitle" style="width: ' + title_width + '%">' + item.label + '</td>' +
                        '<td class="add-panel-section" style="width: ' + section_width + '%">';
    panel_line_cell +=  '<label class="'+ panel_control.data_item_class +'" ';
    if ( item.id !== undefined ) {
        panel_line_cell += 'id="' + item.id + '" ';
    }
    if ( item.name !== undefined ) {
        panel_line_cell += 'name="' + item.name + '" ';
    }
    if ( item.cls !== undefined ) {
        panel_line_cell += 'class="' + item.cls + '" ';
    }
    panel_line_cell += '>';

    if ( item.value !== undefined ) {
        panel_line_cell += item.value;
    }
    panel_line_cell +=  '</label>';

    panel_line_cell +=  '</td>';

    return panel_line_cell;
}

InfoDisplayPanel.prototype.create_panel_footer = function() {
    var panel_footer = "";

    panel_footer += '<div class="add-panel-footer">';
    panel_footer += '</div>';

    return panel_footer;
}

InfoDisplayPanel.prototype.get_modaled_panel = function( info_panel ) {
    var infoDisplayPanel = this;
    var panel_config = infoDisplayPanel.panel_config;

    if( panel_config.is_modal ) {
        var modal_cover = '<div ';
        var modal_body = '<div ';
        var modal_cover_class = 'popup-mesg-box-cover';
        var modal_body_class = 'popup-mesg-box-body';
        var modal_cover_style = '';
        var modal_body_style = '';

        if ( panel_config.modal_config !== undefined ) {
            var modal_config = panel_config.modal_config;
            if ( modal_config.modal_box_size !== undefined ) {
                modal_body_class += ' ' + "mesg-box-" + modal_config.modal_box_size;
            }
            if ( modal_config.modal_level !== undefined ) {
                var level = modal_config.modal_level * 10;
                modal_cover_style = 'z-index: ' + (level -1) + '; ';
                modal_body_style = 'z-index: ' + level + '; ';
            }
            if ( modal_config.modal_box_position !== undefined ) {
                modal_body_style += 'position: ' + modal_config.modal_box_position + '; ';
            }
        }

        modal_cover += 'class="' + modal_cover_class + '" ';
        modal_cover += 'style="' + modal_cover_style + '" ';
        modal_cover += '></div>';
        modal_body += 'class="' + modal_body_class + '" ';
        modal_body += 'style="' + modal_body_style + '" ';;
        modal_body += '>' + info_panel + '</div>';
        info_panel = modal_cover + modal_body;
    }

    return info_panel;
}

InfoDisplayPanel.prototype.add_listener_to_panel_buttons = function() {
    var infoDisplayPanel = this;
    var panel_control = infoDisplayPanel.panel_control;

    var panel_close_selector = "#" + panel_control.panel_close_id;

    /* 关闭按钮 */
    if( $( panel_close_selector ).length > 0 ) {
        $( panel_close_selector ).click(function() {
            infoDisplayPanel.hide();
        });
    }
}

InfoDisplayPanel.prototype.update_data = function(dataItem) {
    var infoDisplayPanel = this;
    var panel_control = infoDisplayPanel.panel_control;

    var data_item_selector = "." + panel_control.data_item_class;
    var data_items = $( data_item_selector );
    data_items.each(function() {
        var data_item = this;
        if ( $(data_item).attr("name") ) {
            if ( dataItem[$(data_item).attr("name")] !== undefined ) {
                $(data_item).text( dataItem[$(data_item).attr("name")] );
            }
        }
    });
}

InfoDisplayPanel.prototype.show = function() {
    var infoDisplayPanel = this;
    var panel_config = infoDisplayPanel.panel_config;
    
    var check_in_selector = "#" + panel_config.check_in_id;
    $( check_in_selector ).show();
     if ( panel_config.is_modal ) {
        /* 上下居中渲染 */
        var popup_body_selector = "#" + panel_config.check_in_id + " .popup-mesg-box-body";
        var popup_body = $( popup_body_selector );
        var body_height = $( popup_body ).height();
        var margin_top = - body_height / 2;
        $( popup_body_selector ).css( "margin-top", margin_top );
    }
}

InfoDisplayPanel.prototype.hide = function() {
    var infoDisplayPanel = this;
    var panel_config = infoDisplayPanel.panel_config;
    
    var check_in_selector = "#" + panel_config.check_in_id;
    $( check_in_selector ).hide();
}