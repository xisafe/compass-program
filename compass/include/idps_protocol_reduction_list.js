// window.onload = function () {
//     init();
// }
/*此处不能用window.onload初始化，此事件已被占用，用window.onload方法解决会覆盖前一个事件*/
$(document).ready(function(){
    //init();
    $(".guanbi").click( function(){
    document.getElementById("detailDiv").style.display = "none";
    document.getElementById("bgDiv").style.display = "none";
    //deselect_edit_item_line();
    //$(".fd").hide();
    });
});

function init() {
    load_data();
    generate_list_main_body();
    //init_list_footer();
    //add_upload_listener();
    //import_data_error_check();
}


//显示加载时的状态
function show_loading_state(){
    document.getElementById("bgDiv").style.display = "";
    show_loading_mesg();
    load_search_data();
}
function show_loading_detail_state(){
    document.getElementById("bgDiv").style.display = "";
    show_loading_mesg();
    load_data_detail();
}
//设置相关按钮和图标可以点击
function enable_btn(){
    document.getElementById("btn_confirm").disabled = false;
    document.getElementById("btn_go").disabled = false;
    document.getElementById("last_page_icon").disabled = false;
    document.getElementById("next_page_icon").disabled = false;
    var imges_source = document.getElementsByName("img_source");
    if(imges_source.length>0){
        for(var i=0;i<imges_source.length;i++){
            imges_source[i].disabled = false;
        }
    }
    var imges_taget = document.getElementsByName("img_target");
    if(imges_taget.length>0){
        for(var i=0;i<imges_taget.length;i++){
            imges_taget[i].disabled = false;
        }
    }
    var imges_flow = document.getElementsByName("img_flow");
    if(imges_flow.length>0){
        for(var i=0;i<imges_flow.length;i++){
            imges_flow[i].disabled = false;
        }
    }
    var imges_detail = document.getElementsByName("img_detail");
    if(imges_detail.length>0){
        for(var i=0;i<imges_detail.length;i++){
            imges_detail[i].disabled = false;
        }
    }
}
//设置相关按钮和图标不可以点击
function disable_btn(){
    document.getElementById("btn_confirm").disabled = true;
    document.getElementById("btn_go").disabled = true;
    document.getElementById("last_page_icon").disabled = true;
    document.getElementById("next_page_icon").disabled = true;
    var imges_source = document.getElementsByName("img_source");
    if(imges_source.length>0){
        for(var i=0;i<imges_source.length;i++){
            imges_source[i].disabled = true;
        }
    }
    var imges_taget = document.getElementsByName("img_target");
    if(imges_taget.length>0){
        for(var i=0;i<imges_taget.length;i++){
            imges_taget[i].disabled = true;
        }
    }
    var imges_flow = document.getElementsByName("img_flow");
    if(imges_flow.length>0){
        for(var i=0;i<imges_flow.length;i++){
            imges_flow[i].disabled = true;
        }
    }
    var imges_detail = document.getElementsByName("img_detail");
    if(imges_detail.length>0){
        for(var i=0;i<imges_detail.length;i++){
            imges_detail[i].disabled = true;
        }
    }
}
//加载显示数据的函数
function load_search_data(){
    var sending_data = {
        ACTION: "load_data",
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        if (is_success(data_content.status)){
            hide_loading_mesg();
            paging_holder.data_content.detail_data = data_content.detail_data;
            paging_holder.data_content.total = data_content.total;
            paging_holder.data_content.display_cols = data_content.display_cols;
            //update_paging_holder();
            generate_list_main_body();
            enable_btn();
            document.getElementById("bgDiv").style.display = "none";
            return;
        }else{
            window.setTimeout("show_loading_state()",1000);
        }
     
    }

    do_request(sending_data, ondatareceived);
}

//显示详细信息的请求函数
function load_data_detail(){
    var sending_data = {
        ACTION: "load_data_detail",
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        if (is_success(data_content.status)){
            hide_loading_mesg();
            var detail_data_item = data_content.detail_data;
            var detail_show = "";
            for(var i=0;i<detail_data_item.length;i++){
                detail_show += (detail_data_item[i]+"\n");
            }
            document.getElementById("bgDiv").style.display = "";
            document.getElementById("detailDiv").style.display = "";
            document.getElementById("item_detail").innerHTML = detail_show;
            //$(".fd").show();
            enable_btn();
            //return;
        }else{
            window.setTimeout("show_loading_detail_state()",1000);
        }
     
    }

    do_request(sending_data, ondatareceived);
}

//详细信息框关闭函数
function close_detail_box(){
    document.getElementById("bgDiv").style.display = "none";
    document.getElementById("detailDiv").style.display = "none";
    enable_btn();
}
//点击确定按钮事件
function doaction_confirm(){
    var protocol = document.getElementById("protocol").value;
    var inputDate = document.getElementById("inputDate").value;
    var inputDate_arr = inputDate.split("-");
    var inputDate_new = inputDate_arr.join("");
    var sending_data = {
        ACTION: "confirm",
        protocol: protocol,
        inputDate: inputDate_new
    };

    function ondatareceived(data) {
        //document.getElementById("btn_confirm").disabled = true;
        disable_btn();
        load_search_data();
    }

    do_request(sending_data, ondatareceived);
    
}
//点击追踪源执行的事件
function track_source(e){
    var protocol = document.getElementById("protocol").value;
    var inputDate = document.getElementById("inputDate").value;
    var inputDate_arr = inputDate.split("-");
    var inputDate_new = inputDate_arr.join("");
    var detail_data = paging_holder.data_content.detail_data;
    var data_item;
    for(var i = 0; i < detail_data.length; i++) {
        if(detail_data[i].line == e.value) {
            data_item = detail_data[i];
            break;
        }
    }
    data_item = edit_config_data(data_item);
    var source = data_item.source_ip+':'+data_item.source_port;
    var sending_data = {
        ACTION: "track_source",
        protocol: protocol,
        inputDate: inputDate_new,
        source:source
    };

    function ondatareceived(data) {
        var imges_source = document.getElementsByName("img_source");
        if(imges_source.length>0){
            for(var i=0;i<imges_source.length;i++){
                imges_source[i].disabled = true;
            }
        }
        disable_btn();
        load_search_data();
    }

    do_request(sending_data, ondatareceived);
}
//点击追踪目标执行的事件
function track_target(e){
    var protocol = document.getElementById("protocol").value;
    var inputDate = document.getElementById("inputDate").value;
    var inputDate_arr = inputDate.split("-");
    var inputDate_new = inputDate_arr.join("");
    var detail_data = paging_holder.data_content.detail_data;
    var data_item;
    for(var i = 0; i < detail_data.length; i++) {
        if(detail_data[i].line == e.value) {
            data_item = detail_data[i];
            break;
        }
    }
    data_item = edit_config_data(data_item);
    var target = data_item.target_ip+':'+data_item.target_port;
    var sending_data = {
        ACTION: "track_target",
        protocol: protocol,
        inputDate: inputDate_new,
        target:target
    };

    function ondatareceived(data) {
        var imges_taget = document.getElementsByName("img_target");
        if(imges_taget.length>0){
            for(var i=0;i<imges_taget.length;i++){
                imges_taget[i].disabled = true;
            }
        }
        disable_btn();
        load_search_data();
    }

    do_request(sending_data, ondatareceived);
}
//点击追踪流执行的事件
function track_all(e){
    var protocol = document.getElementById("protocol").value;
    var inputDate = document.getElementById("inputDate").value;
    var inputDate_arr = inputDate.split("-");
    var inputDate_new = inputDate_arr.join("");
    var detail_data = paging_holder.data_content.detail_data;
    var data_item;
    for(var i = 0; i < detail_data.length; i++) {
        if(detail_data[i].line == e.value) {
            data_item = detail_data[i];
            break;
        }
    }
    data_item = edit_config_data(data_item);
    var source = data_item.source_ip+':'+data_item.source_port;
    var target = data_item.target_ip+':'+data_item.target_port;
    var sending_data = {
        ACTION: "track_all",
        protocol: protocol,
        inputDate: inputDate_new,
        source: source,
        target: target
    };

    function ondatareceived(data) {
        
        disable_btn();
        load_search_data();
    }

    do_request(sending_data, ondatareceived);
}
//点击详细信息执行的事件
function detail(e){
    var protocol = document.getElementById("protocol").value;
    var inputDate = document.getElementById("inputDate").value;
    var inputDate_arr = inputDate.split("-");
    var inputDate_new = inputDate_arr.join("");
    var detail_data = paging_holder.data_content.detail_data;
    var data_item;
    for(var i = 0; i < detail_data.length; i++) {
        if(detail_data[i].line == e.value) {
            data_item = detail_data[i];
            break;
        }
    }
    data_item = edit_config_data(data_item);
    var fileName = data_item.filename;
    var dataNum = data_item.data_num;
    var sending_data = {
        ACTION: "detail",
        protocol: protocol,
        inputDate: inputDate_new,
        fileName:fileName,
        dataNum:dataNum
    };

    function ondatareceived(data) {
        //var data_content = JSON.parse(data);
        var imges_detail = document.getElementsByName("img_detail");
        if(imges_detail.length>0){
            for(var i=0;i<imges_detail.length;i++){
                imges_detail[i].disabled = true;
            }
        }
        disable_btn();
        load_data_detail();
    }
    do_request(sending_data, ondatareceived);
}
//点击上一页执行的事件
function last_page(){
    var protocol = document.getElementById("protocol").value;
    var inputDate = document.getElementById("inputDate").value;
    var inputDate_arr = inputDate.split("-");
    var inputDate_new = inputDate_arr.join("");
    var current_page = paging_holder.current_page;
    var page_goto= -1;
    if(current_page>1){
        page_goto = current_page-1;
        paging_holder.current_page--;
    }
    
    var sending_data = {
        ACTION: "last_page",
        protocol: protocol,
        inputDate: inputDate_new,
        page_goto:page_goto
    };

    function ondatareceived(data) {
        //document.getElementById("last_page_icon").disabled = true;
        disable_btn();
        load_search_data();
    }
    if(page_goto>0){
        do_request(sending_data, ondatareceived);
    }
}
//点击下一页执行的事件
function next_page(){
    var protocol = document.getElementById("protocol").value;
    var inputDate = document.getElementById("inputDate").value;
    var inputDate_arr = inputDate.split("-");
    var inputDate_new = inputDate_arr.join("");
    var current_page = paging_holder.current_page;
    var page_goto = current_page+1;
    paging_holder.current_page = page_goto;
    
    var sending_data = {
        ACTION: "next_page",
        protocol: protocol,
        inputDate: inputDate_new,
        page_goto:page_goto
    };

    function ondatareceived(data) {
        //document.getElementById("next_page_icon").disabled = true;
        disable_btn();
        load_search_data();
    }

    do_request(sending_data, ondatareceived);
}
//点击Go按钮执行的事件
function goto_page(){
    var protocol = document.getElementById("protocol").value;
    var inputDate = document.getElementById("inputDate").value;
    var inputDate_arr = inputDate.split("-");
    var inputDate_new = inputDate_arr.join("");
    var current_page = paging_holder.current_page;
    var page_goto = document.getElementById("page_togo").value;
    paging_holder.current_page = page_goto;
    
    var sending_data = {
        ACTION: "goto_page",
        protocol: protocol,
        inputDate: inputDate_new,
        page_goto:page_goto
    };

    function ondatareceived(data) {
        //document.getElementById("btn_go").disabled = true;
        disable_btn();
        load_search_data();
    }

    do_request(sending_data, ondatareceived);
}

function add_upload_listener() {
    $('#upload-header-left').click(function(){
        if($('#add-div-content-upload').css('display')=='none')
        {
            $('#add-div-content-upload').slideDown('1000');
            $('#upload-header-left img').attr('src','/images/del.png');
        }else{
            $('#add-div-content-upload').slideUp('1000');
            $('#upload-header-left img').attr('src','/images/add.png');
        }
    });
}

function check_import() {
    if(document.getElementById("import_file").value == "") {
        show_warn_mesg("未选择文件,操作失败");
        return false;
    }
    if(confirm("导入数据会覆盖原来所有配置数据,确认导入?")) {
        return true;
    } else {
        return false;
    }
}

function import_data_error_check(url) {
    var sending_data = {
        ACTION: 'import_error_check'
    };
    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        paging_holder.import_error_mesg = data_content.detail_mesg;
        if(is_import_error(data_content.status)){
            show_error_mesg(data_content.mesg);
            change_import_error_mesg(1);//有错误状态
        } else if (is_import_success(data_content.status)){
            show_note_mesg(data_content.mesg);
        } else {
            if(data_content.detail_mesg.length){
                change_import_error_mesg(1);//有错误状态
            }
        }
    }

    do_request(sending_data, ondatareceived);
}

function change_import_error_mesg(status) {
    if(status) {
        $('#import_error_mesg').attr('src','/images/error_note.png');
    }else {
        $('#import_error_mesg').attr('src','/images/read_note.png');
    }
}

function import_error_read() {
    show_detail_error_mesg();
}

function load_data(){
	show_loading_mesg();
    //var search = document.getElementById("search-key").value;
    //var condition = document.getElementById("condition").value;
    var sending_data = {
        ACTION: "load_data",
        //search: search,
        //condition: condition
    };

    function ondatareceived(data) {
        //debugger;
        var data_content = JSON.parse(data);
        paging_holder.data_content.detail_data = data_content.detail_data;
        paging_holder.data_content.total = data_content.total;
        paging_holder.data_content.display_cols = data_content.display_cols;
        update_paging_holder();
        if(is_need_reload(data_content.reload)) {
            show_apply_mesg_box();
        }
        window.setTimeout("hide_loading_mesg()",500);//一般加载数据很快，这里做用户体验，让用户能看见加载图片
    }

    do_request(sending_data, ondatareceived);
}

function update_paging_holder() {
    var total = paging_holder.data_content.total;
    var page_size = paging_holder.page_size;
    /*Ceil computing*/
    var total_page = Math.ceil(total / page_size);
    /*To handle the condition that there is none records*/
    if (total_page == 0) {
        total_page = 1;
    }

    var current_page = paging_holder.current_page;
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

    /*Update paging_holder*/
    paging_holder.total_page = total_page;
    paging_holder.current_page = current_page;
    paging_holder.from_num = from_num;
    paging_holder.to_num = to_num;
}

function init_list_footer () {
    first_page();
}

function generate_list_main_body_bak () {
    var current_page = paging_holder.current_page;
    var total_page = paging_holder.total_page;
    var total = paging_holder.data_content.total;
    var from_num = paging_holder.from_num;
    var to_num = paging_holder.to_num;
    var page_size = paging_holder.page_size;
    var display_cols = paging_holder.data_content.display_cols;
    var detail_data = paging_holder.data_content.detail_data;
    var table_main_body = "";

    var odd_or_even = 0;

    for (var i = from_num; i < to_num; i++) {
        if ( odd_or_even % 2 == 0){
            table_main_body += '<tr class="even-num-line">';
        } else {
            table_main_body += '<tr class="odd-num-line">';
        }
        table_main_body += '<td class="rule-listbc">';
        table_main_body += i;
        table_main_body += '</td>';
        for ( var j = 0; j < display_cols.length; j++) {
            table_main_body += '<td>';
            
            table_main_body += detail_data[i][display_cols[j]];
            table_main_body += '</td>';
        }

        table_main_body += '<td class="action">';

        /*先判断数据项里面有没有启用禁用字段*/
        if(detail_data[i].enabled !== undefined){
            if(detail_data[i].enabled == "on"){
                table_main_body += '<input type="image" class="action-image" src="../images/on.png" title="禁用" value="' + detail_data[i].line + '" onclick="disable_item(this);"/>';
            } else {
                table_main_body += '<input type="image" class="action-image" src="../images/off.png" title="启用" value="' + detail_data[i].line + '" onclick="enable_item(this);"/>';
            }
        }
        table_main_body += '<input type="image" class="action-image" src="../images/edit.png" title="编辑" value="' + detail_data[i].line + '" onclick="edit_item(this);"/>';
        table_main_body += '<input type="image" class="action-image" src="../images/delete.png" title="删除" value="' + detail_data[i].line + '" onclick="delete_item(this);"/>';
        table_main_body += '</td>';
        odd_or_even++;
    }

    if(total == 0) {
        var colspan = 2 + display_cols.length;
        table_main_body += '<tr class="env table_note fordel"><td colspan="' + colspan +'"><div><img src="/images/pop_warn_min.png">无内容</div></td></tr>';
    }

    $("#rule-listb").empty();
    $("#rule-listb").append(table_main_body);
}

function update_main_body_info_bak() {
    var current_page = paging_holder.current_page;
    var total_page = paging_holder.total_page;
    var total = paging_holder.data_content.total;
    var from_num = paging_holder.from_num;
    var to_num = paging_holder.to_num;
    var page_size = paging_holder.page_size;
    var display_cols = paging_holder.data_content.display_cols;
    var detail_data = paging_holder.data_content.detail_data;
    var selected_line = paging_holder.selected_line;
    var table_main_body = "";

    var odd_or_even = 0;

    for (var i = from_num; i < to_num; i++) {
        var data_item_id = detail_data[i].line;
        if(data_item_id == selected_line){
            table_main_body += '<tr class="selected-line">';
        }else{
            if ( odd_or_even % 2 == 0){
                table_main_body += '<tr class="even-num-line">';
            } else {
                table_main_body += '<tr class="odd-num-line">';
            }
        }
        table_main_body += '<td class="rule-listbc">';
        table_main_body += i;
        table_main_body += '</td>';
        for ( var j = 0; j < display_cols.length; j++) {
            table_main_body += '<td>';
            
            table_main_body += detail_data[i][display_cols[j]];
            table_main_body += '</td>';
        }

        table_main_body += '<td class="action">';

        /*先判断数据项里面有没有启用禁用字段*/
        if(detail_data[i].enabled !== undefined){
            if(detail_data[i].enabled == "on"){
                table_main_body += '<input type="image" class="action-image" src="../images/on.png" title="禁用" value="' + detail_data[i].line + '" onclick="disable_item(this);"/>';
            } else {
                table_main_body += '<input type="image" class="action-image" src="../images/off.png" title="启用" value="' + detail_data[i].line + '" onclick="enable_item(this);"/>';
            }
        }
        table_main_body += '<input type="image" class="action-image" src="../images/edit.png" title="编辑" value="' + detail_data[i].line + '" onclick="edit_item(this);"/>';
        table_main_body += '<input type="image" class="action-image" src="../images/delete.png" title="删除" value="' + detail_data[i].line + '" onclick="delete_item(this);"/>';
        table_main_body += '</td>';
        odd_or_even++;
    }

    if(total == 0) {
        var colspan = 2 + display_cols.length;
        table_main_body += '<tr class="env table_note fordel"><td colspan="' + colspan +'"><div><img src="/images/pop_warn_min.png">无内容</div></td></tr>';
    }

    $("#rule-listb").empty();
    $("#rule-listb").append(table_main_body);
}

function generate_list_main_body() {
    /*这个函数作为备用方案*/
    var current_page = paging_holder.current_page;
    var total_page = paging_holder.total_page;
    var total = paging_holder.data_content.total;
    var from_num = paging_holder.from_num;/*Some difference*/
    var to_num = 20;
    var page_size = paging_holder.page_size;
    var display_cols = paging_holder.data_content.display_cols;
    var detail_data = paging_holder.data_content.detail_data;
    var table_main_body = "";

    var odd_or_even = 0;
    var none_sense_value = -1;
    for (var i = from_num; i < to_num; i++) {
        if ( odd_or_even % 2 == 0){
            table_main_body += '<tr class="even-num-line">';
        } else {
            table_main_body += '<tr class="odd-num-line">';
        }
        for ( var j = 0; j < display_cols.length; j++) {
            //debugger;
            if(display_cols[j] == 'source_ip'){
                table_main_body += '<td>';
                table_main_body += (detail_data[i][display_cols[j]]+":"+detail_data[i]['source_port']);
                table_main_body += '</td>';
            }else if(display_cols[j] == 'target_ip'){
                table_main_body += '<td>';
                table_main_body += (detail_data[i][display_cols[j]]+":"+detail_data[i]['target_port']);
                table_main_body += '</td>';
            }else{
                table_main_body += '<td>';
                table_main_body += detail_data[i][display_cols[j]];
                table_main_body += '</td>';
            }
            
        }

        table_main_body += '<td class="action">';
        table_main_body += '<input type="image" name="img_source" class="action-image" src="../images/source.png" title="追踪源" value="' + detail_data[i].line + '" onclick="track_source(this);"/>';
        table_main_body += '<input type="image" name="img_target" class="action-image" src="../images/target.png" title="追踪目的" value="' + detail_data[i].line + '" onclick="track_target(this);"/>';
        table_main_body += '<input type="image" name="img_flow" class="action-image" src="../images/track.png" title="追踪流" value="' + detail_data[i].line + '" onclick="track_all(this);"/>';
        table_main_body += '<input type="image" name="img_detail" class="action-image" src="../images/detail.png" title="详细信息" value="' + detail_data[i].line + '" onclick="detail(this);"/>';
        table_main_body += '</td>';
        odd_or_even++;
    }

    /*Fill the page to one page_size for stable layout*/
    if (to_num < from_num + page_size) {
        for(var i = to_num; i < from_num + page_size; i++){
            if ( odd_or_even % 2 == 0){
                table_main_body += '<tr class="even-num-line">';
            } else {
                table_main_body += '<tr class="odd-num-line">';
            }
            table_main_body += '<td class="rule-listbc">';
            table_main_body += '&nbsp';
            table_main_body += '</td>';
            for ( var j = 0; j < display_cols.length; j++) {
                table_main_body += '<td>&nbsp';
                table_main_body += '</td>';
            }

            odd_or_even++;
        }
    };

    $("#rule-listb").empty();
    $("#rule-listb").append(table_main_body);
    document.getElementById("current-page").value = current_page;
}

function update_main_body_info() {
    /*这个函数作为备用方案*/
    var current_page = paging_holder.current_page;
    var total_page = paging_holder.total_page;
    var total = paging_holder.data_content.total;
    var from_num = paging_holder.from_num;/*Some difference*/
    var to_num = paging_holder.to_num;
    var page_size = paging_holder.page_size;
    var display_cols = paging_holder.data_content.display_cols;
    var detail_data = paging_holder.data_content.detail_data;
    var selected_line = paging_holder.selected_line;
    var table_main_body = "";

    var listb_tr = $("#rule-listb tr");
    var tr_num = 0;
    var none_sense_value = -1;

    for (var i = from_num; i < to_num; i++) {
        /*在显示前配置每一条数据，配置函数config_display_data由init脚本定义*/
        detail_data[i] = config_display_data(detail_data[i]);

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
        //listb_tr.eq(tr_num).find("td").eq( 0 ).html('<p>'+i+'</p>');
        for(var j = 0; j < display_cols.length; j++) {
            if(display_cols[j] == 'source_ip'){
                listb_tr.eq(tr_num).find("td").eq( j ).html(detail_data[i][display_cols[j]]+':'+detail_data[i]['source_port']);
            }else if(display_cols[j] == 'target_ip'){
                listb_tr.eq(tr_num).find("td").eq( j ).html(detail_data[i][display_cols[j]]+':'+detail_data[i]['target_port']);
            }else{
                listb_tr.eq(tr_num).find("td").eq( j ).html(detail_data[i][display_cols[j]]);
            }
            
        }
        
        var actions = '<input type="image" class="action-image" src="../images/source.png" title="追踪源" value="' + detail_data[i].line + '" onclick="track_source(this);"/>';
        actions += '<input type="image" class="action-image" src="../images/target.png" title="追踪目的" value="' + detail_data[i].line + '" onclick="track_target(this);"/>';
        actions += '<input type="image" class="action-image" src="../images/track.png" title="追踪流" value="' + detail_data[i].line + '" onclick="track_all(this);"/>';
        actions += '<input type="image" class="action-image" src="../images/detail.png" title="详细信息" value="' + detail_data[i].line + '" onclick="detail(this);"/>';
        
        listb_tr.eq(tr_num).find("td").eq( display_cols.length ).html(actions);
        tr_num++;
    }

    /*Clean the rest of data in the page*/
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
    document.getElementById("current-page").value = current_page;
}

function update_paging_tools_info(){
    var current_page = paging_holder.current_page;
    var total_page = paging_holder.total_page;
    var total = paging_holder.data_content.total;
    var from_num = paging_holder.from_num + 1;/*Some difference*/
    var to_num = paging_holder.to_num;

    /*To handle the situation of no record*/
    if (to_num == 0){
        from_num = 0;
    }

    document.getElementById("current-page").value = current_page;
    /*document.getElementById("total-page").innerHTML = total_page;
    document.getElementById("from-num").innerHTML = from_num;
    document.getElementById("to-num").innerHTML = to_num;
    document.getElementById("total-num").innerHTML = total; */
}

/*A function to refresh the page info*/
function update_info() {
    update_paging_holder();
    update_paging_tools_info();
    update_main_body_info();
    reset_check_all_box();
}

function reset_check_all_box() {
    //document.getElementById("rule-listbhc").checked =false;
}

function toggle_check (){
    var checked_switch = document.getElementById("rule-listbhc");
    if (checked_switch.checked == true) {
        check_all();
    }else{
        uncheck_all();
    }
}

function check_all(){
    set_check_all(true);
}

function uncheck_all(){
    set_check_all(false);
}

function set_check_all(status) {
    var checkboxs = document.getElementsByClassName("rule-listbcc");
    var from_num = paging_holder.from_num;
    var to_num = paging_holder.to_num;
    for (var i = from_num; i < to_num; i++){
        checkboxs[i - from_num].checked = status;
        paging_holder.data_content.detail_data[i].checked = checkboxs[i - from_num].checked;
    }
}

function toggle_item_check(element){
    /*Record the checked items*/
    for(var i = 0; i < paging_holder.data_content.detail_data.length; i++){
        if(paging_holder.data_content.detail_data[i].line == element.value){
            paging_holder.data_content.detail_data[i].checked = element.checked;
            break;
        }
    }
}

function select_edit_item_line(element){
    paging_holder.selected_line = element.value;
    update_main_body_info();
}

function deselect_edit_item_line() {
    reset_selected_line();
    update_main_body_info();
}

function edit_item(element) {
    document.getElementById("add-title").innerHTML = paging_holder.update_title;
    document.getElementById("line-num").value = element.value;
    document.getElementById("submit-button").value = "更新";

    select_edit_item_line(element);

    /*跳到更新规则处*/
    scroll_to_add_box();

    pull_down_edit_box();

    var detail_data = paging_holder.data_content.detail_data;
    var data_item;
    for(var i = 0; i < detail_data.length; i++) {
        if(detail_data[i].line == element.value) {
            data_item = detail_data[i];
            break;
        }
    }
    data_item = edit_config_data(data_item);

    var input_texts = $('.input-text');
    for(var i = 0; i < input_texts.length; i++) {
        input_texts[i].value = data_item[input_texts[i].name];
    }
    var input_textareas = $('.input-textarea');
    for(var i = 0; i < input_textareas.length; i++) {
        input_textareas[i].innerText = data_item[input_textareas[i].name];
    }
    var input_selects = $('.input-select');
    for(var i = 0; i < input_selects.length; i++) {
        for(var j = 0; j < input_selects[i].length; j++){
            if(input_selects[i][j].value == data_item[input_selects[i].name]) {
                input_selects[i][j].selected = true;
                break;
            }
        }
    }
    var input_multi_selects = $('.input-multi-select');
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
            // value_selected = false;
        }
    }
    var input_checkboxs = $('.input-checkbox');
    for(var i = 0; i < input_checkboxs.length; i++) {
        var item_checked = false;
        if(data_item[input_checkboxs[i].name] == "on") {
            item_checked = true;
        }
        input_checkboxs[i].checked = item_checked;
    }
    /*对表单中的值重新做检查*/
    check._submit_check(object,check);
}

function clear_line_edit_mark() {
    var trs = $("#rule-listb tr");
    for(var i = 0; i < trs.length; i++) {
        if(i % 2 == 0) {
            trs[i].className = "even-num-line";
        } else {
            trs[i].className = "odd-num-line";
        }
    }
}

function enable_selected_items() {
    opt_selected_items("enable_data");
}

function disable_selected_items() {
    opt_selected_items("disable_data");
}

function delete_selected_items() {
    opt_selected_items("delete_data");
}

function opt_selected_items(opt){
    var sending_data = {
        ACTION: opt
    };
    var detail_data = paging_holder.data_content.detail_data;
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
            do_action(sending_data);
        } else if (opt == "delete_data" && confirm("确认删除所有选中项?")){
            /*Do request*/
            do_action(sending_data);
        } else if (opt == "enable_data") {
            /*Do request*/
            do_action(sending_data);
        } else {
            return;
        }
    } else {
        show_warn_mesg("未选择任何项目,操作失败");
    }
}

function enable_item(element){
    opt_item("enable_data", element.value);
}

function disable_item(element){
    if(confirm("确认禁用?")) {
        opt_item("disable_data", element.value);
    }
}

function delete_item(element){
    if(confirm("确认删除?")) {
        opt_item("delete_data", element.value);
    }
}

function opt_item(opt, line){
    var sending_data = {
        ACTION: opt
    };
    sending_data[line] = line;
    /*Do request*/
    do_action(sending_data);
}

function do_action(sending_data) {
    function ondatareceived(data){
        var data_content = JSON.parse(data);
        if(is_success(data_content.status)){
            refresh_page();
            if(is_need_reload(data_content.reload)){
                show_apply_mesg_box();
            }
            show_note_mesg(data_content.mesg);
        } else {
            show_error_mesg("操作失败,请稍后重试")
        }
    }
    
    do_request(sending_data, ondatareceived);
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: paging_holder.url,
        data: sending_data,
        async: false,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

function scroll_to_mesg_box() {
    //window.location.href = "#all-mesg-box";
}

function scroll_to_add_box() {
    //window.location.href = "#add-div";
}

function apply_config() {
    var sending_data = {
        ACTION: "apply_data"
    };

    function ondatareceived(data){
        var data_content = JSON.parse(data);
        if(is_success(data_content.status)){
            hide_apply_mesg_box();
            show_note_mesg(data_content.mesg);
        } else {
            show_error_mesg("操作失败,请稍后重试")
        }
    }

    do_request(sending_data, ondatareceived);
}

function first_page() {
    enable_next_end_page_op();
    /*Set current page number to number one*/
    paging_holder.current_page = paging_holder.first_page;
    update_info();
    disable_first_last_page_op();
    /*To handle the condition that there is only one page*/
    if(paging_holder.current_page == paging_holder.total_page) {
        disable_next_end_page_op();
    }
}

/* function last_page() {
    if(paging_holder.current_page > paging_holder.first_page) {
        if(paging_holder.current_page == paging_holder.total_page) {
            enable_next_end_page_op();
        }
        paging_holder.current_page = paging_holder.current_page - 1;
        update_info();
        if(paging_holder.current_page == paging_holder.first_page){
            disable_first_last_page_op();
        }
    }
} */

/* function next_page() {
    if(paging_holder.current_page < paging_holder.total_page) {
        if(paging_holder.current_page == paging_holder.first_page) {
            enable_first_last_page_op();
        }
        paging_holder.current_page = paging_holder.current_page + 1;
        update_info();
        if(paging_holder.current_page == paging_holder.total_page){
            disable_next_end_page_op();
        }
    }
} */

function end_page() {
    enable_first_last_page_op();
    /*Set current page number to number one*/
    paging_holder.current_page = paging_holder.total_page;
    update_info();
    disable_next_end_page_op();
    /*To handle the condition that there is only one page*/
    if(paging_holder.current_page == paging_holder.first_page) {
        disable_first_last_page_op();
    }

}

function refresh_page() {
    if(paging_holder.selected_line >= 0) {
        if(!confirm("您正在编辑数据,确认离开并刷新?")){
            return;
        } else {
            /*重置选中的行*/
            reset_selected_line();
        }
    }
    /*第一步，重置正在编辑的数据*/
    cancel_edit_box();

    /*第二步，控制翻页工具*/
    disable_first_last_page_op();
    disable_next_end_page_op();
    load_data();
    if(paging_holder.current_page == paging_holder.first_page) {
        first_page();
    } else if(paging_holder.current_page == paging_holder.total_page) {
        end_page();
    } else {
        enable_first_last_page_op();
        enable_next_end_page_op();
    }
    update_info();
}

//显示全部
function show_all(){
    document.getElementById("search-key").value = "";
    refresh_page();
}

function go_to_page(page) {
    if(page < paging_holder.first_page){
        $("#current-page").val(paging_holder.first_page);
        first_page();
    } else if(page > paging_holder.total_page){
        $("#current-page").val(paging_holder.first_page);
        end_page();
    } else {
        enable_first_last_page_op();
        enable_next_end_page_op();
        paging_holder.current_page = page;
        update_info();
    }
}

function search(event){
    var event = event || window.event; //IE、FF下获取事件对象
    var cod = event.charCode || event.keyCode; //IE、FF下获取键盘码
    if(cod == 13) {
        refresh_page();
    }
}
function input_control(element,event) {
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
        go_to_page(element.value);
    } else {
        if(cod!=8 && cod != 46 && !((cod >= 48 && cod <= 57) || (cod >= 96 && cod <= 105) || (cod >= 37 && cod <= 40))){
            notValue(event);
        }
    }
    function notValue(event){
        event.preventDefault ? event.preventDefault() : event.returnValue=false;
    }
}

function enable_first_last_page_op() {
    $("#first_page_icon").attr("src", "../images/first-page.gif");
    $("#last_page_icon").attr("src", "../images/last-page.gif");
}

function enable_next_end_page_op() {
    $("#next_page_icon").attr("src", "../images/next-page.gif");
    $("#end_page_icon").attr("src", "../images/end-page.gif");

}

function disable_first_last_page_op() {
    $("#first_page_icon").attr("src", "../images/first-page-off.png");
    $("#last_page_icon").attr("src", "../images/last-page-off.png");
}

function disable_next_end_page_op() {
    $("#next_page_icon").attr("src", "../images/next-page-off.png");
    $("#end_page_icon").attr("src", "../images/end-page-off.png");
}

function save_data(url) {

    if(check._submit_check(object,check)){
        show_warn_mesg("请填写正确的表单后再提交");
    } else {
        var sending_data = $("#template-form").serialize();
        sending_data = sending_data + "&ACTION=save_data";

        function ondatareceived(data) {
            var data_content = JSON.parse(data);
            if(is_success(data_content.status)){
                /*重置正在编辑的条目*/
                cancel_edit_box();
                /*重置选中的行*/
                reset_selected_line();
                refresh_page();
                if(is_need_reload(data_content.reload)) {
                    show_apply_mesg_box();
                }
                show_note_mesg(data_content.mesg);
            }else{
                show_error_mesg(data_content.mesg)
            }
        }

        do_request(sending_data, ondatareceived);
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

function is_import_error(status) {
    if (status == "1") {
        return true;
    } else {
        return false;
    }
}

function is_import_success(status) {
    if (status == "0") {
        return true;
    } else {
        return false;
    }
}

function cancel_edit_box() {
    //reset_edit_box();
    pull_up_edit_box();
    deselect_edit_item_line();
}

function cancel_import_box() {
    document.getElementById("template-form-upload").reset();
    $('#add-div-content-upload').slideUp('1000');
    $('#upload-header-left img').attr('src','/images/add.png');

}

function pull_down_edit_box() {
    /*下拉*/
    $('#add-div-content').slideDown('1000');
    $('#add-div-header img').attr('src','/images/del.png');
}

function pull_up_edit_box() {
    /*上拉*/
    $('#add-div-content').slideUp('1000');
    $('#add-div-header img').attr('src','/images/add.png');
}

function reset_selected_line() {
        /*重置选中的行*/
        paging_holder.selected_line = -1;
}

function reset_edit_box() {
    //document.getElementById("template-form").reset();
    /*textarea要单独处理*/
    /*var input_textareas = $('.input-textarea');
    for(var i = 0; i < input_textareas.length; i++){
        input_textareas[i].innerText = "";
    }
    document.getElementById("add-title").innerHTML = paging_holder.add_title;
    document.getElementById("line-num").value = "";
    document.getElementById("submit-button").value = "添加"; */
}

function show_apply_mesg_box() {
    $("#apply-mesg-box").show();
}

function hide_apply_mesg_box() {
    $("#apply-mesg-box").hide();
}

function show_note_mesg(mesg) {
    show_mesg("note", mesg)
}

function show_warn_mesg(mesg) {
    show_mesg("warn", mesg)
}

function show_error_mesg(mesg) {
    show_mesg("error", mesg)
}

function show_detail_error_mesg(){
    var error_mesgs = paging_holder.import_error_mesg;
    var error_body = "";
    if(error_mesgs.length){
        for(var i = 0; i < error_mesgs.length; i++) {
            if( i % 2 == 0 ) {
                error_body += '<tr class="even-num-line"> <td>' + error_mesgs[i] + '</td></tr>';
            }else {
                error_body += '<tr class="odd-num-line"> <td>' + error_mesgs[i] + '</td></tr>';
            }
        }
    } else {
        error_body = '<tr class="odd-num-line"><td><div><img src="/images/pop_warn_min.png">无内容</div></td></tr>';
    }
    $("#popup-mesg-tbody").html("");
    $("#popup-mesg-tbody").append(error_body);
    $("#popup-mesg-box-back").show();
    $("#popup-mesg-box").show();
    // change_import_error_mesg(0);
}

function hide_detail_error_mesg() {
    $("#popup-mesg-box-back").hide();
    $("#popup-mesg-box").hide();
}

function show_loading_mesg(){
    // $("#popup-mesg-box-back").show();
    $("#popup-mesg-box-loading").show();
}

function hide_loading_mesg() {
    // $("#popup-mesg-box-back").hide();
    $("#popup-mesg-box-loading").hide();
}

function show_mesg(type, mesg) {
    var mesg_show_time = 2000;
    if(type == "note"){
        $("#note-mesg").html(mesg);
        // $("#note-mesg-box").fadeIn("slow");
        $("#note-mesg-box").show();
        setTimeout('$("#note-mesg-box").fadeOut("slow")',mesg_show_time);
    } else if (type == "warn") {
        $("#warn-mesg").html(mesg);
        $("#warn-mesg-box").show();
        window.setTimeout('$("#warn-mesg-box").fadeOut("slow")',mesg_show_time);
    } else if (type == "error") {
        $("#error-mesg").html(mesg);
        $("#error-mesg-box").show();
        window.setTimeout('$("#error-mesg-box").fadeOut("slow")',mesg_show_time);
    } else {
        $("#warn-mesg").html(mesg);
       $("#warn-mesg-box").show();
        window.setTimeout('$("#warn-mesg-box").fadeOut("slow")',mesg_show_time);
    }
    /*定位到消息框去*/
    scroll_to_mesg_box();
}

function show_mesg_bak(type, mesg) {
    if(type == "note"){
        alert(mesg);
    } else if (type == "warn") {
        alert(mesg);
    } else if (type == "error") {
        alert(mesg);
    } else {
        alert(mesg);
    }
}

//显示详细信息
function show_detail(e){
    //select_edit_item_line(element);
    $(".fd").show();
    var detail_data = paging_holder.data_content.detail_data;
    var data_item;
    /* for(var i = 0; i < detail_data.length; i++) {
        if(detail_data[i].line == element.value) {
            data_item = detail_data[i];
            break;
        }
    } */
    data_item = edit_config_data(data_item);
}