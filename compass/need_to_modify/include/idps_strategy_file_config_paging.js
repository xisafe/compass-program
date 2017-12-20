function new_init() {
    new_load_data();
    new_init_list_footer();
    new_check._main(ips_object);
}

function new_load_data(){
    show_loading_mesg();
    var search = document.getElementById("new-search-key").value;
    var set_filename = document.getElementById("load_set_filename").value;
    var sending_data = {
        ACTION: "load_data",
        search: search,
        set_filename: set_filename
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        strategy_file_paging_holder.data_content.detail_data = data_content.detail_data;
        strategy_file_paging_holder.data_content.total = data_content.total;
        strategy_file_paging_holder.data_content.display_cols = data_content.display_cols;
        update_strategy_file_paging_holder();
        if(is_need_reload(data_content.reload)) {
            show_apply_mesg_box();
        }
        window.setTimeout("hide_loading_mesg()",500);//一般加载数据很快，这里做用户体验，让用户能看见加载图片
    }

    new_do_request(sending_data, ondatareceived);
}

function update_strategy_file_paging_holder() {
    var total = strategy_file_paging_holder.data_content.total;
    var page_size = strategy_file_paging_holder.page_size;
    /*Ceil computing*/
    var total_page = Math.ceil(total / page_size);
    /*To handle the condition that there is none records*/
    if (total_page == 0) {
        total_page = 1;
    }

    var current_page = strategy_file_paging_holder.current_page;
    if (current_page <= 0){
        current_page = 1;
    }else if (current_page > total_page) {
        current_page = total_page;
    }

    var from_num = (current_page - 1) > 0 ? (current_page - 1) * page_size : 0;
    if (from_num > total) {
        from_num = total;
    }

    var to_num = current_page * page_size;
    if (to_num > total) {
        to_num = total;
    }

    /*Update strategy_file_paging_holder*/
    strategy_file_paging_holder.total_page = total_page;
    strategy_file_paging_holder.current_page = current_page;
    strategy_file_paging_holder.from_num = from_num;
    strategy_file_paging_holder.to_num = to_num;
}

function new_init_list_footer () {
    new_first_page();
}

function new_update_main_body_info() {
    /*这个函数作为备用方案*/
    var current_page = strategy_file_paging_holder.current_page;
    var total_page = strategy_file_paging_holder.total_page;
    var total = strategy_file_paging_holder.data_content.total;
    var from_num = strategy_file_paging_holder.from_num;/*Some difference*/
    var to_num = strategy_file_paging_holder.to_num;
    var page_size = strategy_file_paging_holder.page_size;
    var display_cols = strategy_file_paging_holder.data_content.display_cols;
    var detail_data = strategy_file_paging_holder.data_content.detail_data;
    var selected_line = strategy_file_paging_holder.selected_line;
    var table_main_body = "";

    var listb_tr = $("#new-rule-listb tr");
    var tr_num = 0;
    var none_sense_value = -1;

    for (var i = from_num; i < to_num; i++) {
        /*在显示前配置每一条数据，配置函数new_config_display_data由init脚本定义*/
        detail_data[i] = new_config_display_data(detail_data[i]);

        var data_item_id = detail_data[i].line;
        if(data_item_id == selected_line){
            listb_tr[tr_num].className = "selected-line";
        }else{
            if ( tr_num % 2 == 0){
                listb_tr[tr_num].className = "even-num-line";
            } else {
                listb_tr[tr_num].className = "odd-num-line";
            }
        }
        var checked = "";
        if(detail_data[i].checked) {
            /*如果以前勾选过，现在也要显示为勾选状态*/
            checked = 'checked="checked"'
        }
        listb_tr.eq(tr_num).find("td").eq( 0 ).html('<input type="checkbox" class="new-rule-listbcc" value="' + data_item_id + '" onclick="new_toggle_item_check(this);" ' + checked + '/>');
        for(var j = 0; j < display_cols.length; j++) {
            listb_tr.eq(tr_num).find("td").eq( j + 1 ).html(detail_data[i][display_cols[j]]);
        }
        var actions = "";
        /*先判断数据项里面有没有启用禁用字段*/
        if(detail_data[i].enabled !== undefined){
            if(detail_data[i].enabled == "on"){
                actions += '<input type="image" class="action-image" src="../images/on.png" title="禁用" value="' + data_item_id + '" onclick="new_disable_item(this);"/>';
            } else {
                actions += '<input type="image" class="action-image" src="../images/off.png" title="启用" value="' + data_item_id + '" onclick="new_enable_item(this);"/>';
            }
        }
        try {
            if ( typeof( eval( new_create_other_opt_image_button ) ) == "function") {
                /*创建一些其他暂时未考虑到的按钮*/
                actions += new_create_other_opt_image_button(data_item_id, detail_data[i]);
            }
        } catch(e) {
            /*do nothing*/
        }
        if(detail_data[i].not_editable === undefined) {
            actions += '<input type="image" class="action-image" src="../images/edit.png" title="编辑" value="' + data_item_id + '" onclick="new_edit_item(this);"/>';
        }
        if(detail_data[i].not_deletable === undefined) {
            actions += '<input type="image" class="action-image" src="../images/delete.png" title="删除" value="' + data_item_id + '" onclick="new_delete_item(this);"/>';
        }
        listb_tr.eq(tr_num).find("td").eq( display_cols.length + 1 ).html(actions);
        tr_num++;
    }

    /*Clean the reset of data in the page*/
    if(to_num < from_num + page_size) {
        for (var i = to_num; i < from_num + page_size; i++) {
            if ( tr_num % 2 == 0){
                listb_tr[tr_num].className = "even-num-line";
            } else {
                listb_tr[tr_num].className = "odd-num-line";
            }
            for(var j = 0; j < display_cols.length + 2; j++) {
                listb_tr.eq(tr_num).find("td").eq( j ).html("&nbsp");
            }
            tr_num++;
        }
    }
}

function new_update_paging_tools_info(){
    var current_page = strategy_file_paging_holder.current_page;
    var total_page = strategy_file_paging_holder.total_page;
    var total = strategy_file_paging_holder.data_content.total;
    var from_num = strategy_file_paging_holder.from_num + 1;/*Some difference*/
    var to_num = strategy_file_paging_holder.to_num;

    /*To handle the situation of no record*/
    if (to_num == 0){
        from_num = 0;
    }

    document.getElementById("new-current-page").value = current_page;
    document.getElementById("new-total-page").innerHTML = total_page;
    document.getElementById("new-from-num").innerHTML = from_num;
    document.getElementById("new-to-num").innerHTML = to_num;
    document.getElementById("new-total-num").innerHTML = total;
}

/*A function to refresh the page info*/
function new_update_info() {
    update_strategy_file_paging_holder();
    new_update_paging_tools_info();
    new_update_main_body_info();
    new_reset_check_all_box();
}

function new_reset_check_all_box() {
    document.getElementById("new-rule-listbhc").checked =false;
}

function new_toggle_check (){
    var checked_switch = document.getElementById("new-rule-listbhc");
    if (checked_switch.checked == true) {
        new_check_all();
    }else{
        new_uncheck_all();
    }
}

function new_check_all(){
    new_set_check_all(true);
}

function new_uncheck_all(){
    new_set_check_all(false);
}

function new_set_check_all(status) {
    var checkboxs = document.getElementsByClassName("new-rule-listbcc");
    var from_num = strategy_file_paging_holder.from_num;
    var to_num = strategy_file_paging_holder.to_num;
    for (var i = from_num; i < to_num; i++){
        checkboxs[i - from_num].checked = status;
        strategy_file_paging_holder.data_content.detail_data[i].checked = checkboxs[i - from_num].checked;
    }
}

function new_toggle_item_check(element){
    /*Record the checked items*/
    for(var i = 0; i < strategy_file_paging_holder.data_content.detail_data.length; i++){
        if(strategy_file_paging_holder.data_content.detail_data[i].line == element.value){
            strategy_file_paging_holder.data_content.detail_data[i].checked = element.checked;
            break;
        }
    }
}

function new_select_edit_item_line(element){
    strategy_file_paging_holder.selected_line = element.value;
    new_update_main_body_info();
}

function new_deselect_edit_item_line() {
    new_reset_selected_line();
    new_update_main_body_info();
}

function new_edit_item(element) {
    new_select_edit_item_line(element);

    var detail_data = strategy_file_paging_holder.data_content.detail_data;
    var data_item;
    for(var i = 0; i < detail_data.length; i++) {
        if(detail_data[i].line == element.value) {
            data_item = detail_data[i];
            break;
        }
    }
    data_item = new_edit_config_data(data_item);

    var input_texts = $(".input-text");
    for(var i = 0; i < input_texts.length; i++) {
        input_texts[i].value = data_item[input_texts[i].name];
    }
    var input_textareas = $(".input-textarea");
    for(var i = 0; i < input_textareas.length; i++) {
        input_textareas[i].value = data_item[input_textareas[i].name];
    }
    var input_selects = $(".input-select");
    for(var i = 0; i < input_selects.length; i++) {
        for(var j = 0; j < input_selects[i].length; j++){
            if(input_selects[i][j].value == data_item[input_selects[i].name]) {
                input_selects[i][j].selected = true;
                break;
            }
        }
    }
    var input_multi_selects = $(".input-multi-select");
    for(var i = 0; i < input_multi_selects.length; i++) {
        var values = data_item[input_multi_selects[i].name].split("|");
        for(var j = 0; j < input_multi_selects[i].childNodes.length; j++) {
            var value_selected = false;
            for(var k = 0; k < values.length; k++) {
                /*如果当前的option中的值在配置项中能找到，标记为选择状态*/
                if(input_multi_selects[i].childNodes[j].value == values[k]) {
                    value_selected = true;
                    break;
                }
            }
            input_multi_selects[i].childNodes[j].selected = value_selected;
        }
    }
    var input_checkboxs = $(".input-checkbox");
    for(var i = 0; i < input_checkboxs.length; i++) {
        var item_checked = false;
        if(data_item[input_checkboxs[i].name] == "on") {
            item_checked = true;
        }
        input_checkboxs[i].checked = item_checked;
    }

    /*做一些其他暂时未考虑到的事情*/
    try {
        if ( typeof( eval( new_do_other_when_edit_item ) ) == "function") {
            new_do_other_when_edit_item( data_item );
        }
    } catch(e) {
        /*do nothing*/ 
    }

    /*对表单中的值重新做检查*/
    new_check._submit_check(ips_object,check);
}

function new_clear_line_edit_mark() {
    var trs = $("#new-rule-listb tr");
    for(var i = 0; i < trs.length; i++) {
        if(i % 2 == 0) {
            trs[i].className = "even-num-line";
        } else {
            trs[i].className = "odd-num-line";
        }
    }
}

function new_enable_selected_items() {
    new_opt_selected_items("enable_data");
}

function new_disable_selected_items() {
    new_opt_selected_items("disable_data");
}

function new_delete_selected_items() {
    new_opt_selected_items("delete_data");
}

function new_opt_selected_items(opt){
    var set_filename = document.getElementById("load_set_filename").value;
    var sending_data = {
        ACTION: opt,
        set_filename: set_filename
    };
    var detail_data = strategy_file_paging_holder.data_content.detail_data;
    var items_length = detail_data.length;
    var selected_num = 0;
    for(var i = 0; i < items_length; i++) {
        if(detail_data[i].checked) {
            sending_data[detail_data[i].line] = detail_data[i].line;
            selected_num++;
        }
    }
    if(selected_num > 0) {
        if(opt == "disable_data" && confirm("确认禁用所有选中项?")){
            /*Do request*/
            new_do_action(sending_data);
        } else if (opt == "delete_data" && confirm("确认删除所有选中项?")){
            /*Do request*/
            new_do_action(sending_data);
        } else if (opt == "enable_data") {
            /*Do request*/
            new_do_action(sending_data);
        } else {
            new_do_action(sending_data);
        }
    } else {
        show_warn_mesg("未选择任何项目,操作失败");
    }
}

function new_enable_item(element){
    new_opt_item("enable_data", element.value);
}

function new_disable_item(element){
    if(confirm("确认禁用?")) {
        new_opt_item("disable_data", element.value);
    }
}

function new_delete_item(element){
    if(confirm("确认删除?")) {
        new_opt_item("delete_data", element.value);
    }
}

function new_opt_item(opt, line){
    var set_filename = document.getElementById("load_set_filename").value;
    var sending_data = {
        ACTION: opt,
        set_filename: set_filename
    };
    sending_data[line] = line;
    /*Do request*/
    new_do_action(sending_data);
}

function new_do_action(sending_data) {
    function ondatareceived(data){
        var data_content = JSON.parse(data);
        if(is_success(data_content.status)){
            new_refresh_page();
            if(is_need_reload(data_content.reload)){
                show_apply_mesg_box();
            }
            show_note_mesg(data_content.mesg);
        } else {
            show_error_mesg("操作失败,请稍后重试")
        }
    }
    
    new_do_request(sending_data, ondatareceived);
}

function new_do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: strategy_file_paging_holder.url,
        data: sending_data,
        async: false,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

function new_first_page() {
    new_enable_next_end_page_op();
    /*Set current page number to number one*/
    strategy_file_paging_holder.current_page = strategy_file_paging_holder.first_page;
    new_update_info();
    new_disable_first_last_page_op();
    /*To handle the condition that there is only one page*/
    if(strategy_file_paging_holder.current_page == strategy_file_paging_holder.total_page) {
        new_disable_next_end_page_op();
    }
}

function new_last_page() {
    if(strategy_file_paging_holder.current_page > strategy_file_paging_holder.first_page) {
        if(strategy_file_paging_holder.current_page == strategy_file_paging_holder.total_page) {
            new_enable_next_end_page_op();
        }
        strategy_file_paging_holder.current_page = strategy_file_paging_holder.current_page - 1;
        new_update_info();
        if(strategy_file_paging_holder.current_page == strategy_file_paging_holder.first_page){
            new_disable_first_last_page_op();
        }
    }
}

function new_next_page() {
    if(strategy_file_paging_holder.current_page < strategy_file_paging_holder.total_page) {
        if(strategy_file_paging_holder.current_page == strategy_file_paging_holder.first_page) {
            new_enable_first_last_page_op();
        }
        strategy_file_paging_holder.current_page = strategy_file_paging_holder.current_page + 1;
        new_update_info();
        if(strategy_file_paging_holder.current_page == strategy_file_paging_holder.total_page){
            new_disable_next_end_page_op();
        }
    }
}

function new_end_page() {
    new_enable_first_last_page_op();
    /*Set current page number to number one*/
    strategy_file_paging_holder.current_page = strategy_file_paging_holder.total_page;
    new_update_info();
    new_disable_next_end_page_op();
    /*To handle the condition that there is only one page*/
    if(strategy_file_paging_holder.current_page == strategy_file_paging_holder.first_page) {
        new_disable_first_last_page_op();
    }

}

function new_refresh_page() {
    if(strategy_file_paging_holder.selected_line >= 0) {
        if(!confirm("您正在编辑数据,确认离开并刷新?")){
            return;
        } else {
            /*重置选中的行*/
            new_reset_selected_line();
        }
    }
    /*第一步，重置正在编辑的数据*/
    new_cancel_edit_box();

    /*第二步，控制翻页工具*/
    new_disable_first_last_page_op();
    new_disable_next_end_page_op();
    new_load_data();
    if(strategy_file_paging_holder.current_page == strategy_file_paging_holder.first_page) {
        new_first_page();
    } else if(strategy_file_paging_holder.current_page == strategy_file_paging_holder.total_page) {
        new_end_page();
    } else {
        new_enable_first_last_page_op();
        new_enable_next_end_page_op();
    }
    new_update_info();
}

function new_go_to_page(page) {
    if(page < strategy_file_paging_holder.first_page){
        $("#new-current-page").val(strategy_file_paging_holder.first_page);
        new_first_page();
    } else if(page > strategy_file_paging_holder.total_page){
        $("#new-current-page").val(strategy_file_paging_holder.first_page);
        new_end_page();
    } else {
        new_enable_first_last_page_op();
        new_enable_next_end_page_op();
        strategy_file_paging_holder.current_page = page;
        new_update_info();
    }
}

function new_search(event){
    var event = event || window.event; //IE、FF下获取事件对象
    var cod = event.charCode || event.keyCode; //IE、FF下获取键盘码
    if(cod == 13) {
        new_refresh_page();
    }
}
function new_input_control(element,event) {
    /*8：退格键、46：delete、37-40： 方向键
    **48-57：小键盘区的数字、96-105：主键盘区的数字
    **110、190：小键盘区和主键盘区的小数
    **189、109：小键盘区和主键盘区的负号
    **enter:13
    **/
    var event = event || window.event; //IE、FF下获取事件对象
    var cod = event.charCode||event.keyCode; //IE、FF下获取键盘码
    if (cod == 13){
        /*解决firefox连续弹框问题*/
        //document.getElementById('current-page').blur();
        new_go_to_page(element.value);
    } else {
        if(cod!=8 && cod != 46 && !((cod >= 48 && cod <= 57) || (cod >= 96 && cod <= 105) || (cod >= 37 && cod <= 40))){
            notValue(event);
        }
    }
    function notValue(event){
        event.preventDefault ? event.preventDefault() : event.returnValue=false;
    }
}

function new_enable_first_last_page_op() {
    $("#new_first_page_icon").attr("src", "../images/first-page.gif");
    $("#new_last_page_icon").attr("src", "../images/last-page.gif");
}

function new_enable_next_end_page_op() {
    $("#new_next_page_icon").attr("src", "../images/next-page.gif");
    $("#new_end_page_icon").attr("src", "../images/end-page.gif");

}

function new_disable_first_last_page_op() {
    $("#new_first_page_icon").attr("src", "../images/first-page-off.png");
    $("#new_last_page_icon").attr("src", "../images/last-page-off.png");
}

function new_disable_next_end_page_op() {
    $("#new_next_page_icon").attr("src", "../images/next-page-off.png");
    $("#new_end_page_icon").attr("src", "../images/end-page-off.png");
}

function new_save_data(url) {

    if(check._submit_check(ips_object,check)){
        show_warn_mesg("请填写正确的表单后再提交");
    } else {
        var sending_data = $("#eliminate-form").serialize();
        sending_data = sending_data + "&ACTION=save_data";

        function ondatareceived(data) {
            var data_content = JSON.parse(data);
            if(is_success(data_content.status)){
                /*重置正在编辑的条目*/
                new_cancel_edit_box();
                /*重置选中的行*/
                new_reset_selected_line();
                new_refresh_page();
                if(is_need_reload(data_content.reload)) {
                    show_apply_mesg_box();
                }
                show_note_mesg(data_content.mesg);
            }else{
                show_error_mesg(data_content.mesg)
            }
        }

        new_do_request(sending_data, ondatareceived);
    }
}

function is_success(status) {
    if (status == "0") {
        return true;
    } else {
        return false;
    }
}

function is_need_reload(status) {
    if (status == "1") {
        return true;
    } else {
        return false;
    }
}

function new_cancel_edit_box() {
    new_reset_edit_box();
    new_deselect_edit_item_line();
}

function new_reset_selected_line() {
        /*重置选中的行*/
        strategy_file_paging_holder.selected_line = -1;
}

function new_reset_edit_box() {
    document.getElementById("eliminate-form").reset();
    /*textarea要单独处理*/
    var input_textareas = $(".input-textarea");
    for(var i = 0; i < input_textareas.length; i++){
        input_textareas[i].value = "";
    }

    /*做一些其他暂时未考虑到的事情*/
    try {
        if ( typeof( eval( new_do_other_when_reset_edit_box ) ) == "function") {
            new_do_other_when_reset_edit_box();
        }
    } catch(e) {
        /*do nothing*/
    }
}