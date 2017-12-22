var strategy_list = {
    system_list: [],
    custom_list: [],
    loaded: false
}

function distribute_strategy() {
    if ( count_selected_strategy() <= 0 ) {
        show_warn_mesg("未选择策略,操作无效");
        return;
    }

    var detail_data = paging_holder.data_content.detail_data;
    var items_length = detail_data.length;
    var consoles = new Array();
    for(var i = 0; i < items_length; i++) {
        if(detail_data[i].checked) {
            consoles.push( detail_data[i].line );
        }
    }

    var system_list = new Array();
    for( var i = 0; i < strategy_list.system_list.length; i++ ) {
        if ( strategy_list.system_list[i].checked ) {
            system_list.push( strategy_list.system_list[i].strategy_value );
        }
    }

    var custom_list = new Array();
    for( var i = 0; i < strategy_list.custom_list.length; i++ ) {
        if ( strategy_list.custom_list[i].checked ) {
            custom_list.push( strategy_list.custom_list[i].strategy_value );
        }
    }

    var sending_data = {
        ACTION: 'distribute_data',
        consoles: consoles,
        system_list: system_list,
        custom_list: custom_list
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        if( is_success(data_content.status) ) {
            hide_strategy_list();
            reset_strategy_list();
            show_note_mesg( data_content.mesg );
        } else {
            hide_strategy_list();
            show_warn_mesg( data_content.mesg );
        }
        refresh_page();
    }
    do_request(sending_data, ondatareceived);
}

function reset_strategy_list() {
    strategy_list.loaded = false;
    $("#system_strategy_set").attr("checked", false);
    $("#custom_strategy_set").attr("checked", false);
}

function distribute_selected_items() {
    if ( count_selected_console() <= 0 ) {
        show_warn_mesg("未选择任何引擎,操作无效");
        return;
    }
    if ( !strategy_list.loaded ) {
        load_strategy_list();
    }
    show_strategy_list();
}

function load_strategy_list() {
    var sending_data = {
        ACTION: 'load_strategy_list'
    };
    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        strategy_list.system_list = data_content.system_list;
        strategy_list.custom_list = data_content.custom_list;
        strategy_list.loaded = true;
        generate_strategy_list();
        hide_loading_mesg();
    }
    show_loading_mesg();
    do_request(sending_data, ondatareceived);
}

function generate_strategy_list() {
    var system_list = strategy_list.system_list;
    var custom_list = strategy_list.custom_list;
    var ret_system_list = "";
    var ret_custom_list = "";
    for( var i = 0; i < system_list.length; i++ ) {
        ret_system_list += '<span class="strategy_item"><input type="checkbox" name="' + system_list[i].strategy_name + '" id="' + system_list[i].strategy_id + '" value="' + system_list[i].strategy_value + '" onclick="toggle_system_strategy(this);"/>';
        ret_system_list += '<label for="' + system_list[i].strategy_id + '">' + system_list[i].strategy_label + '</label></span>';
    }
    $("#system_strategy_set_hook").html(ret_system_list);

    for( var i = 0; i < custom_list.length; i++ ) {
        ret_custom_list += '<span class="strategy_item"><input type="checkbox" name="' + custom_list[i].strategy_name + '" id="' + custom_list[i].strategy_id + '" value="' + custom_list[i].strategy_value + '" onclick="toggle_custom_strategy(this);"/>';
        ret_custom_list += '<label for="' + custom_list[i].strategy_id + '">' + custom_list[i].strategy_label + '</label></span>';
    }
    $("#custom_strategy_set_hook").html(ret_custom_list);
}

function toggle_all_system_strategy( element ) {
    $("input[name='system_strategy']").attr("checked", element.checked);
    for( var i = 0; i < strategy_list.system_list.length; i++ ) {
        strategy_list.system_list[i].checked = element.checked;
    }
}

function toggle_all_custom_strategy( element ) {
    $("input[name='custom_strategy']").attr("checked", element.checked);
    for( var i = 0; i < strategy_list.custom_list.length; i++ ) {
        strategy_list.custom_list[i].checked = element.checked;
    }
}

function toggle_system_strategy( element ) {
    for( var i = 0; i < strategy_list.system_list.length; i++ ) {
        if ( strategy_list.system_list[i].strategy_id == element.id ) {
            strategy_list.system_list[i].checked = element.checked;
        }
    }
}

function toggle_custom_strategy( element ) {
    for( var i = 0; i < strategy_list.custom_list.length; i++ ) {
        if ( strategy_list.custom_list[i].strategy_id == element.id ) {
            strategy_list.custom_list[i].checked = element.checked;
            break;
        }
    }
}

function power_on_selected_items() {
    opt_selected_items("power_on");
}

function power_down_selected_items() {
     if(confirm("确认关闭选中项?")) {
        opt_selected_items("power_down");
    }
}

function power_on_item(element){
    opt_item("power_on", element.value);
}

function power_down_item(element){
    if(confirm("确认关闭?")) {
        opt_item("power_down", element.value);
    }
}

function show_strategy_list() {

    $("#popup-mesg-box-back").show();
    $("#popup-strategy").show();
}

function hide_strategy_list() {
    $("#popup-mesg-box-back").hide();
    $("#popup-strategy").hide();
}

function count_selected_console() {
    var detail_data = paging_holder.data_content.detail_data;
    var items_length = detail_data.length;
    var selected_num = 0;
    for(var i = 0; i < items_length; i++) {
        if(detail_data[i].checked) {
            selected_num++;
        }
    }
    return selected_num;
}

function count_selected_strategy() {
    var system_list = strategy_list.system_list;
    var custom_list = strategy_list.custom_list;
    var selected_num = 0;
    for(var i = 0; i < system_list.length; i++) {
        if(system_list[i].checked) {
            selected_num++;
        }
    }
    for(var i = 0; i < custom_list.length; i++) {
        if(custom_list[i].checked) {
            selected_num++;
        }
    }
    return selected_num;
}